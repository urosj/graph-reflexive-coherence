"""Bounded W-causal-loop pressure; no source-to-completion campaign."""

import builtins
import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import test_cos_native_spark_pressure as common
from aos_native_spark_audit import (
    audit_event,
    audit_step,
    digest,
    fixed_read,
    separation,
)
from aos_native_spark_oracle import Reference, contains, verify_step
from aos_native_spark_oracle import classify as independent_classify
from cos_native_spark_oracle import matrix, vector
from cpc_native_spark_pressure_oracle import decode, intervals
from p991a6_aos_preflight import transition
from p991a6_aos_subjects import profile, request

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_aos as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import (
    _ARB_CONTEXT_LOCK,
    CertificationInconclusive,
    weighted_split,
)
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_aos_math import AOSMath
from pygrc.models.grc_v4_spark_conductance import ExactConductanceState
from pygrc.models.grc_v4_spark_state import ExactResources, round_flux
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_aos as fixtures


def sentinel(state, sign=1):
    return replace(
        state, W_A=tuple(str(1 + sign * Q(i + 1, 2**14)) for i in range(len(state.W_A)))
    )


def observed(model):
    initial = model.configuration
    publication = model._operation._spark_scope.published
    records, steps = [], []
    read, writer, step = (
        AOSMath.read,
        native.SparkAOSKernel._writer,
        native.SparkAOSKernel.step,
    )

    def frozen():
        if (
            model.configuration != initial
            or model._operation._spark_scope.published is not publication
        ):
            raise AssertionError("provisional calculation published progress")

    def capture_read(math, C, W, H, *args):
        frozen()
        inputs = {"C": intervals(C), "W": intervals(W), "H": intervals(H)}
        result = read(math, C, W, H, *args)
        records.append(
            dict(
                stage="fixed_read",
                **inputs,
                result={k: intervals(v) for k, v in result.items()},
            )
        )
        return result

    def capture_writer(k, state, after, consumed):
        frozen()
        result = writer(k, state, after, consumed)
        records.append(
            {
                "stage": "writer",
                "before": state.to_payload(),
                "final_C": after.to_payload(),
                "writer": result[1].to_dict(),
            }
        )
        return result

    def capture_step(k, *args, **kwargs):
        value = step(k, *args, **kwargs)
        steps.append(value)
        return value

    with (
        patch.object(AOSMath, "read", capture_read),
        patch.object(native.SparkAOSKernel, "_writer", capture_writer),
        patch.object(native.SparkAOSKernel, "step", capture_step),
    ):
        result = model.step()
    if not result.committed:
        raise AssertionError(result.reason)
    if len(steps) != 1:
        raise AssertionError("one physical step")
    return steps[0], records


class AOSNativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeAOSTests.setUpClass()
        cls.fixture = fixtures.NativeAOSTests()
        cls.config = cls.fixture.config
        cls.event = cls.fixture.event_model
        cls.certs = cls.fixture.certificates
        cls.good = owner.kernel(cls.config).step(sentinel(cls.config.current))
        cls.measurements = {"mutations": []}
        cls.evidence = {"actual_steps": [], "events": []}

    def setUp(self):
        self.enterContext(exact_backend(ExactBackend.FLINT))

    def test_exact_weighted_rows_ports_empty_parallel_and_log_derivative(self):
        state = common.toy(
            {"a": "0", "b": "1/2", "c": "3/2"},
            [("a", 1, "b", 4), ("a", 2, "c", 7), ("a", 4, "b", 5), ("a", 7, "c", 8)],
        )
        state = ExactConductanceState(
            state.graph, state.C, state.charge, ("999/1000", "1001/1000", "1", "1")
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            math = AOSMath(state.graph)
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            dC = arb_mat(3, 4)
            dW = arb_mat(
                [[W[i, 0] if i == j else 0 for j in range(4)] for i in range(4)]
            )
            rows, der = math.rows(C, W, dC, dW)
            self.assertTrue(rows[0][0].contains(Q(2001, 2000)))
            self.assertFalse(rows[0][0].contains(Q(1999, 2000)))
            self.assertFalse(rows[0][0].contains(1))
            self.assertTrue(
                rows[0][1].contains(Q(1, 2)) and rows[0][2].contains(Q(3, 2))
            )
            self.assertEqual(rows[1][0], 0)
            self.assertTrue(rows[1][1].contains(-Q(1, 2)))
            self.assertEqual(rows[2][1], 0)
            self.assertTrue(rows[2][2].contains(-Q(3, 2)))
            for k, delta in enumerate((Q(1, 2), Q(3, 2))):
                expected = Q(state.W_A[k]) / 2 * (delta - Q(2001, 2000))
                self.assertTrue(der[0][0][k].contains(expected))
            diagnostics = state.spatial_diagnostics(
                sign=1,
                gradient="4",
                hessian="1/8",
                contrast="1/16",
                core_resource="1/16",
            )
            self.assertEqual(diagnostics[0]["gradient"][0], "2001/2000")
            swapped = replace(state, W_A=("1001/1000", "999/1000", "1", "1"))
            self.assertEqual(
                swapped.spatial_diagnostics(
                    sign=1,
                    gradient="4",
                    hessian="1/8",
                    contrast="1/16",
                    core_resource="1/16",
                )[0]["gradient"][0],
                "1999/2000",
            )
            with self.assertRaisesRegex(RuntimeError, "positive fixed-row denominator"):
                math.rows(C, arb_mat(vector(("1", "-1", "1", "1"))))
        self.measurements["weighted_row"] = {
            "correct": "2001/2000",
            "swapped": "1999/2000",
            "unweighted": "1",
            "parallel_edges": True,
            "all_port_rows": True,
        }

    def test_uniform_C_writes_W_without_current_or_resource_motion(self):
        state = replace(sentinel(self.config.current), C=("2",) * 12, charge="24")
        k = owner.kernel(self.config)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            initial = arb_mat([[arb(Q(w)).log()] for w in state.W_A])
            target = -arb(Q(1, 16384))
            a = (-arb(1)).exp()
            for i in range(1, 4):
                step = k.step(state)
                verify_step(step)
                self.assertEqual(step.after.C, state.C)
                self.assertEqual(step.flux, ("0",) * 13)
                self.assertNotEqual(step.after.W_A, state.W_A)
                for j, w in enumerate(step.after.W_A):
                    ideal = a**i * initial[j, 0] + (1 - a**i) * target
                    self.assertLess(
                        abs(arb(Q(w)).log() - ideal).upper().fmpq(), Q(1, 2**188)
                    )
                state = step.after
        self.measurements["zero_flow_writer"] = {
            "charge": "24",
            "steps": 3,
            "resources_unchanged": True,
            "history_changes": True,
        }

    def test_matched_total_current_formation_and_geometric_relaxation(self):
        state = self.good.before
        k = owner.kernel(self.config)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload())
            C = arb_mat(vector(self.good.after.C))
            W = arb_mat(vector(state.W_A))
            J = r.selected(arb_mat(vector(state.C)), W)["corrector"]["current"]
            formed = r.log_drive(C, W, J)
            zero = r.log_drive(C, W, arb_mat(13, 1))
            a = (-arb(1)).exp()
            delta = (1 - a) * (formed - zero)
            for i in range(13):
                self.assertTrue(
                    (delta[i, 0] + (1 - a) * J[i, 0] ** 2 / 65536).contains(0)
                )
            lower = separation(formed, zero)
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            read = k._admitted_read(state)
            resources = ExactResources(
                self.good.after.graph, self.good.after.C, self.good.after.charge
            )
            actual, writer = k._writer(state, resources, read)
            null = dict(read, corrector=dict(read["corrector"], current=arb_mat(13, 1)))
            neutral, _ = k._writer(state, resources, null)
            self.assertNotEqual(actual, neutral)
            W = arb_mat(vector(state.W_A))
            G = arb_mat([[x.exp()] for x in decode(writer["exponent"]).entries()])
            a = (-arb(1)).exp()
            wrong = a * W + (1 - a) * G
            separation(decode(writer["ideal"]), wrong)
        self.measurements["formation"] = {
            "matched_final_C_and_old_W": True,
            "log_drive_separation_lower": lower,
            "sign_flip_not_used": True,
            "arithmetic_writer_distinguished": True,
        }

    def test_fixed_H_W_roles_and_noncommuting_flat(self):
        state = self.good.before
        math = AOSMath(state.graph)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            r = Reference(state.graph.to_payload())
            H = arb_mat(r.I)
            H[0, 1] = H[1, 0] = Q(1, 10)
            expected = r.read(C, W, H)
            wrong = arb_mat(
                [
                    [expected["q"][i, 0] * x / 2]
                    for i, x in enumerate((H.inv() * expected["current"]).entries())
                ]
            )
            noncommuting = separation(expected["causal_flat"], wrong)
            unweighted = r.read(C, arb_mat([[1]] * 13), H)
            for key in ("potential", "baseline", "drive", "q", "current"):
                separation(expected[key], unweighted[key])
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            actual = math.read(arb_mat(vector(state.C)), arb_mat(vector(state.W_A)), H)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            payload = {k: intervals(v) for k, v in actual.items()}
            fixed_read(state.graph.to_payload(), state.C, state.W_A, H, payload)
            for key in expected:
                bad = deepcopy(payload)
                bad[key] = intervals(unweighted[key] if key != "causal_flat" else wrong)
                with self.assertRaisesRegex(AssertionError, "fixed-H " + key):
                    fixed_read(state.graph.to_payload(), state.C, state.W_A, H, bad)
        self.measurements["fixed_H"] = {
            "offdiagonal_H": True,
            "W_in_all_five_roles": True,
            "flat_order_separation_lower": noncommuting,
        }

    def test_frozen_public_OS_stages_and_complete_map(self):
        source = GRC9V4(self.config)
        before = source.configuration
        step, stages = observed(source)
        self.evidence["source_step"] = {
            "subject": before.to_payload(),
            "step": transition(step),
            "role": "current",
            "audit": audit_step(before, before.current, step),
        }
        self.assertTrue(source.expand(request(source)).committed)
        for role in ("current", "reset"):
            m = source.duplicate()
            if role == "reset":
                self.assertTrue(m.reset().committed)
            for _ in range(2):
                config = m.configuration
                before = config.current
                step, stages = observed(m)
                writers = [
                    i for i, stage in enumerate(stages) if stage["stage"] == "writer"
                ]
                self.assertEqual(len(writers), 1)
                incoming = stages[: writers[0]]
                returned = stages[writers[0] + 1 :]
                with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                    r = Reference(before.graph.to_payload())
                    C, W = arb_mat(vector(before.C)), arb_mat(vector(before.W_A))
                    expected = r.selected(C, W)
                    self.assertTrue(
                        incoming
                        and all(
                            contains(row["C"], C) and contains(row["W"], W)
                            for row in incoming
                        )
                    )
                    self.assertTrue(any(contains(row["H"], r.I) for row in incoming))
                    self.assertTrue(
                        any(contains(row["H"], expected["H"]) for row in incoming)
                    )
                    separation(
                        expected["predictor"]["current"],
                        expected["corrector"]["current"],
                    )
                    C1, W1 = (
                        arb_mat(vector(step.after.C)),
                        arb_mat(vector(step.after.W_A)),
                    )
                    self.assertTrue(
                        any(
                            contains(row["C"], C1)
                            and contains(row["W"], W1)
                            and contains(row["H"], r.I)
                            for row in returned
                        )
                    )
                # Extra read-only validation is permitted; selected-stage authority
                # and actual inputs, not an internal call count, decide correctness.
                audit = audit_step(
                    config,
                    before,
                    step,
                    self.certs[0 if role == "current" else 1],
                    role,
                )
                self.evidence["actual_steps"].append(
                    {
                        "subject": config.to_payload(),
                        "step": transition(step),
                        "role": role,
                        "certificate": self.certs[
                            0 if role == "current" else 1
                        ].to_payload(),
                        "audit": audit,
                    }
                )
        self.measurements["OS_staging"] = {
            "actual_target_steps": 4,
            "same_incoming_C_W": True,
            "resolved_geometry_current_effect": True,
            "reference_restarts": True,
        }

    def test_writer_stage_alternatives_are_resolved_and_rejected(self):
        step = self.good
        state = step.before
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload())
            C, W, C1, W1 = (
                arb_mat(vector(x))
                for x in (state.C, state.W_A, step.after.C, step.after.W_A)
            )
            s = r.selected(C, W)
            J = s["corrector"]["current"]
            correct = r.log_drive(C1, W, J)
            variants = {
                "stale_C": r.log_drive(C, W, J),
                "baseline_J": r.log_drive(C1, W, s["corrector"]["baseline"]),
                "predictor_J": r.log_drive(C1, W, s["predictor"]["current"]),
                "new_W": r.log_drive(C1, W1, J),
                "future_J": r.log_drive(
                    C1, W, r.selected(C1, W1)["corrector"]["current"]
                ),
                "pre_read_G": r.log_drive(C, W, s["corrector"]["baseline"]),
            }
            reports = {}
            for name, bad in variants.items():
                reports[name] = separation(correct, bad)
                writer = step.writer.to_dict()
                writer["exponent"] = intervals(bad)
                with self.assertRaisesRegex(
                    AssertionError, "final-C incoming-W writer"
                ):
                    verify_step(replace(step, writer=FrozenJSONMap(writer)))
                self.measurements["mutations"].append(name)
        self.measurements["writer_stage_separation_lower"] = reports

    def test_corrector_current_and_pre_read_reference_mutations(self):
        step = self.good
        payload = step.consumed_read.to_dict()
        for key in ("baseline", "drive", "q", "current"):
            bad = deepcopy(payload)
            bad["corrector"][key] = bad["predictor"][key]
            with self.assertRaisesRegex(AssertionError, "corrector " + key):
                verify_step(replace(step, consumed_read=FrozenJSONMap(bad)))
            self.measurements["mutations"].append("predictor_" + key)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(step.before.graph.to_payload())
            C, W = arb_mat(vector(step.before.C)), arb_mat(vector(step.before.W_A))
            s = r.selected(C, W)
            G = arb_mat(
                [
                    [x.exp()]
                    for x in r.log_drive(C, W, s["corrector"]["current"]).entries()
                ]
            )
            separation(G, s["corrector"]["drive"])
            bad = deepcopy(payload)
            bad["corrector"]["drive"] = intervals(G)
            with self.assertRaisesRegex(AssertionError, "corrector drive"):
                verify_step(replace(step, consumed_read=FrozenJSONMap(bad)))
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            pred = r.selected(C, W)["predictor"]["current"]
            wrong = replace(
                step,
                flux=tuple(str(round_flux(x.mid().fmpq())) for x in pred.entries()),
            )
        self.assertNotEqual(wrong.flux, step.flux)
        with self.assertRaisesRegex(AssertionError, "nearest-even flux"):
            verify_step(wrong)
        self.measurements["mutations"] += ["G_from_total_J", "predictor_continuity"]

    def test_equal_C_same_sum_W_and_next_read_consumes_written_history(self):
        state = self.good.before
        other = replace(state, W_A=tuple(reversed(state.W_A)))
        k = owner.kernel(self.config)
        self.assertEqual(sum(map(Q, state.W_A)), sum(map(Q, other.W_A)))
        a, b = k.step(state), k.step(other)
        verify_step(a)
        verify_step(b)
        self.assertNotEqual(a.after, b.after)
        self.assertNotEqual(
            a.consumed_read["subject_digest"], b.consumed_read["subject_digest"]
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload())
            C = arb_mat(vector(a.after.C))
            fresh = r.selected(C, arb_mat(vector(a.after.W_A)))["corrector"]["current"]
            old = r.selected(C, arb_mat(vector(state.W_A)))["corrector"]["current"]
            delta = separation(fresh, old)
        next_step = k.step(a.after)
        verify_step(next_step)
        self.assertEqual(next_step.before, a.after)
        self.measurements["next_history"] = {
            "same_sum_edge_patterns_distinguished": True,
            "next_current_separation_lower": delta,
        }

    def test_nonuniform_event_lineage_both_roles_and_chiralities(self):
        for chi in (-1, 1):
            config = replace(
                self.config,
                current=sentinel(self.config.current),
                reset=sentinel(self.config.reset, -1),
            )
            m = GRC9V4(config)
            self.assertTrue(m.step().committed)
            source = m.configuration
            self.assertNotEqual(source.current.W_A, config.current.W_A)
            self.assertEqual(source.reset, config.reset)
            self.assertTrue(m.expand(request(m, chi)).committed)
            event = m._operation._published.completion.event.to_dict()
            report = audit_event(source, m.configuration, event)
            self.evidence["events"].append(
                {
                    "source": source.to_payload(),
                    "target": m.configuration.to_payload(),
                    "event": event,
                    "audit": report,
                }
            )
        self.measurements["lineage"] = {
            "chiralities": 2,
            "nonuniform_old_edges": 13,
            "new_unit_edges": 3,
            "C_shares_reused": False,
            "persistent_Z": False,
        }

    def test_rehashed_event_allocation_and_history_mutations_reject(self):
        m = GRC9V4(self.config)
        self.assertTrue(m.step().committed)
        source = m.configuration
        self.assertTrue(m.expand(request(m)).committed)
        target = m.configuration
        event = m._operation._published.completion.event.to_dict()
        bad = deepcopy(event)
        bad["conductance_history"]["source_archive"]["current"]["W_A"][0] = "1"
        content = {
            "schema_version": "grcv4-exact-conductance-history-v1",
            "subject": "candidate",
            "content": bad["conductance_history"]["source_archive"],
        }
        bad["conductance_history"]["history_policy"]["candidate"][
            "source_history_digest"
        ] = "grcv4-history-content-sha256:" + digest(content)
        with self.assertRaisesRegex(AssertionError, "actual both-role source archive"):
            audit_event(source, target, bad)
        with self.assertRaisesRegex(AssertionError, "exact old-edge lineage current"):
            audit_event(
                source,
                replace(target, current=replace(target.current, W_A=("1",) * 16)),
                event,
            )
        values = dict(zip(target.current.graph.live_node_ids, map(Q, target.current.C)))
        charge = Q(source.current.C[source.current.graph.node_index("v")])
        for node, share in zip(
            event["module"], map(Q, ("0", "1/64", "31/32", "1/64")), strict=True
        ):
            values[node] = share * charge
        badstate = replace(
            target.current,
            C=tuple(str(values[n]) for n in target.current.graph.live_node_ids),
        )
        with self.assertRaisesRegex(AssertionError, "A allocation"):
            audit_event(source, replace(target, current=badstate), event)
        self.measurements["mutations"] += [
            "rehash_false_archive",
            "reset_old_W_to_one",
            "C_family_allocation",
        ]

    def test_log_writer_held_target_composition_and_no_arithmetic_average(self):
        k = owner.kernel(self.config)
        state = replace(self.good.before, W_A=("201/200",) * 13)
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            target = arb(Q(995, 1000))
            logs = arb_mat([[target.log()]] * 13)
            a = (-arb(1)).exp()
            original = state
            for i in range(2):
                read = k._admitted_read(state)
                resources = ExactResources(state.graph, state.C, state.charge)
                with patch.object(AOSMath, "exponent", return_value=(logs, None)):
                    weights, _writer = k._writer(state, resources, read)
                state = replace(state, W_A=weights)
                expected = (
                    a ** (i + 1) * arb(Q(original.W_A[0])).log()
                    + (1 - a ** (i + 1)) * target.log()
                ).exp()
                self.assertLess(
                    abs(arb(Q(weights[0])) - expected).upper().fmpq(), Q(1, 2**189)
                )
                self.assertTrue(Q(995, 1000) < Q(weights[0]) < Q(original.W_A[0]))
            wrong = a * arb(Q(original.W_A[0])) + (1 - a) * target
            one = (a * arb(Q(original.W_A[0])).log() + (1 - a) * target.log()).exp()
            self.assertGreater(abs(wrong - one).lower().fmpq(), 0)
        for tau in (0, 16, 64):
            with self.assertRaises((ValueError, RuntimeError)):
                native.SparkAOSKernel(
                    self.config.reference.graph,
                    profile(self.config.reference.graph, candidate={"tau_A": tau}),
                )
        self.measurements["writer_primitive"] = {
            "held_target": "199/200",
            "initial_W": "201/200",
            "two_fixed_duration_writes": True,
            "whole_step_semigroup_claimed": False,
            "other_durations_native": False,
        }

    def test_neutral_signed_and_extreme_contrast_primitives(self):
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            math = AOSMath(self.good.before.graph)
            C = arb_mat(vector(self.good.before.C))
            for w, g in (
                (Q(1), Q(1)),
                (Q(1001, 1000), Q(999, 1000)),
                (Q(999, 1000), Q(1001, 1000)),
                (Q(2) ** 64, Q(1)),
                (Q(1), Q(2) ** 64),
            ):
                W = arb_mat([[w]] * 13)
                G = arb_mat([[arb(g).log()]] * 13)
                with patch.object(math, "exponent", return_value=(G, None)):
                    read = math.read(C, W, math.I)
                for i in range(13):
                    expected = 4 * (w + g) * read["baseline"][i, 0] / (3 * w + 5 * g)
                    self.assertTrue((read["current"][i, 0] - expected).contains(0))
                    self.assertTrue(-1 < read["q"][i, 0] < 1)
                    if read["baseline"][i, 0] != 0:
                        self.assertTrue(
                            read["baseline"][i, 0] * read["current"][i, 0] > 0
                        )
                if w == g:
                    self.assertTrue(
                        all(x.is_zero() for x in read["causal_flat"].entries())
                    )
                    self.assertEqual(math.geometry(read["causal_flat"]), math.I)
        self.measurements["contrast_primitives"] = {
            "neutral_positive_negative": True,
            "resolved_exponent_range_bits": 64,
            "complete_profile_admission_claimed": False,
        }

    def test_spectral_split_equality_outside_and_Frobenius_distinction(self):
        from pygrc.models import grc_v4_numerics as numerics

        with exact_backend(ExactBackend.FLINT):
            t = Q(*(1e-11).as_integer_ratio())
            I = ((Q(1), Q(0)), (Q(0), Q(1)))
            for coefficient, accepted in (
                (Q(1), True),
                (Q(1) + Q(1, 2**40), False),
                (Q(3, 4), True),
            ):
                R = ((coefficient * t, Q(0)), (Q(0), -coefficient * t))
                exact = all(
                    numerics.inertia(
                        tuple(
                            tuple(t * I[i][j] + sign * R[i][j] for j in range(2))
                            for i in range(2)
                        )
                    )[0]
                    == 0
                    for sign in (-1, 1)
                )
                self.assertEqual(exact, accepted)
                if accepted:
                    self.assertLessEqual(
                        Q(weighted_split(R, I, t)["weighted_row_bound"]), t
                    )
                else:
                    with self.assertRaises(CertificationInconclusive):
                        weighted_split(R, I, t)
                if coefficient == Q(3, 4):
                    self.assertGreater(sum(x * x for row in R for x in row), t * t)
        self.measurements["split"] = {
            "tolerance_exact": str(t),
            "normalized_spectral_equality": True,
            "just_outside_rejected": True,
            "spectral_pass_Frobenius_fail": True,
            "native_bound": "strict_Frobenius_sufficient_only; inconclusive is not a spectral rejection proof",
        }

    def test_smooth_floor_and_invalid_history_domains_fail_closed(self):
        k = owner.kernel(self.config)
        state = self.good.before
        for bad in ("0", "-1", "nan", "inf", 0.0, float("nan"), float("inf")):
            with (
                self.subTest(value=str(bad)),
                self.assertRaises((ValueError, TypeError)),
            ):
                replace(state, W_A=(bad,) * 13)
        for value in ("99/100", "101/100", "1/2", "2"):
            with self.assertRaisesRegex(RuntimeError, "conductance box"):
                k.readmission(replace(state, W_A=(value,) * 13))
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            math = AOSMath(state.graph)
            W = arb_mat([[1]] * 13)
            J = arb_mat(13, 1)
            self.assertTrue(
                all(
                    x > math.floor_log
                    for x in math.exponent(arb_mat([[2]] * 12), W, J)[0].entries()
                )
            )
            for c in (arb(32768), arb(32768) * arb(2).log(), arb(23000, 1000)):
                with self.assertRaisesRegex(
                    RuntimeError, "floor not strictly inactive"
                ):
                    math.exponent(arb_mat([[c]] * 12), W, J)
            with self.assertRaises((ZeroDivisionError, ValueError)):
                math.read(arb_mat(vector(state.C)), W, arb_mat(13, 13))
        self.measurements["domain_scope"] = {
            "invalid_W_rejected_before_log": True,
            "floor_active_and_crossing_reject": True,
            "generic_max_extension_claimed": False,
            "narrow_W_domain_not_widened": True,
        }

    def test_weighted_classifier_thresholds_and_committed_history(self):
        raw = common.toy(
            {"a": "1", "b": "3/2", "c": "5/2", "d": "2", "e": "2"},
            [("a", 1, "b", 1), ("a", 2, "c", 1), ("a", 4, "d", 1), ("a", 7, "e", 1)],
        )
        s = ExactConductanceState(
            raw.graph, raw.C, raw.charge, ("999/1000", "1001/1000", "1", "1")
        )
        policy = replace(
            self.config.policy,
            landscape_sign=1,
            epsilon_gradient="4",
            epsilon_Hessian="1",
            contrast="1/4",
            minimum_resource="1/2",
        )
        # Make both other rows strictly greater than the same threshold.
        s = replace(s, C=("1", "3/2", "5/2", "5/2", "5/2"), charge="10")
        other = replace(s, W_A=("1001/1000", "999/1000", "1", "1"))
        rows = []
        for state in (s, other):
            actual = classify(state, policy)
            expected = independent_classify(
                state.graph.to_payload(), state.C, state.W_A, policy.to_payload()
            )
            self.assertEqual(
                (actual.basins, actual.terminals, [r.to_dict() for r in actual.rows]),
                expected,
            )
            rows.append(actual)
        self.assertEqual(rows[0].terminals, rows[1].terminals)
        self.assertNotEqual(rows[0].rows[0]["anchor"], rows[1].rows[0]["anchor"])
        m = self.fixture.synthetic_window_fixture()
        seen = []
        original = owner.classify

        def capture(state, policy):
            seen.append(state)
            return original(state, policy)

        with patch.object(owner, "classify", capture):
            self.assertTrue(m.step().committed)
        self.assertTrue(any(x == m.configuration.current for x in seen))
        self.assertNotEqual(
            self.event.configuration.current.W_A, m.configuration.current.W_A
        )
        self.measurements["classifier"] = {
            "same_C_routing_different_weighted_qualification": True,
            "committed_W_consumed": True,
        }

    def test_mixed_C_logW_derivatives_away_from_equilibrium(self):
        state = sentinel(self.event.configuration.current)
        n, m = len(state.C), len(state.W_A)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            C = arb_mat(vector(state.C))
            L = arb_mat([[arb(Q(x)).log()] for x in state.W_A])
            x = arb_mat(C.tolist() + L.tolist())
            math = AOSMath(state.graph)
            r = Reference(state.graph.to_payload())
            eps = Q(1, 2**24)
            for phase in range(4):
                dc = [Q((i + phase) % 3 - 1) for i in range(n - 1)]
                dc.append(-sum(dc))
                direction = arb_mat(
                    vector(dc + [Q((i + phase) % 5 - 2, 16) for i in range(m)])
                )
                box = arb_mat(
                    [
                        [x[i, 0] + arb(0, abs(direction[i, 0]).upper().fmpq() * eps)]
                        for i in range(n + m)
                    ]
                )
                J = math.jacobian(arb_mat(box.tolist()[:n]), arb_mat(box.tolist()[n:]))
                p = x + eps * direction
                q = x - eps * direction
                finite = (
                    r.map(arb_mat(p.tolist()[:n]), arb_mat(p.tolist()[n:]))
                    - r.map(arb_mat(q.tolist()[:n]), arb_mat(q.tolist()[n:]))
                ) / (2 * eps)
                self.assertTrue(
                    all(
                        a.contains(b)
                        for a, b in zip(
                            (J * direction).entries(), finite.entries(), strict=True
                        )
                    )
                )
                self.assertGreater(
                    max(
                        abs(J[i, j]).lower().fmpq()
                        for i in range(n)
                        for j in range(n, n + m)
                    ),
                    0,
                )
                self.assertGreater(
                    max(
                        abs(J[i, j]).lower().fmpq()
                        for i in range(n, n + m)
                        for j in range(n)
                    ),
                    0,
                )
        self.measurements["mixed_derivatives"] = {
            "directions": 4,
            "nonstationary": True,
            "both_cross_blocks_nonzero": True,
            "prior_all_30_directions_retained": True,
        }

    def test_full_chart_near_faces_all_W_coordinates_and_relabelled_proofs(self):
        cert = self.certs[0]
        S, U = matrix(cert.operands["S"]), matrix(cert.operands["U"])
        n = 15
        self.assertEqual(
            U * S, M([[int(i == j) for j in range(30)] for i in range(30)])
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(256):
            center = list(map(Q, cert.operands["center"])) + list(
                map(Q, cert.operands["logW_center"])
            )
            for axis in range(30):
                for scale, inside in ((Q(999, 1000), True), (Q(1001, 1000), False)):
                    x = [center[i] + scale * S[i, axis] for i in range(31)]
                    W = tuple(
                        str(round_flux(arb(z).exp().mid().fmpq() * 2**64) / 2**64)
                        for z in x[n:]
                    )
                    state = ExactConductanceState(
                        self.fixture.center.graph, tuple(map(str, x[:n])), "21", W
                    )
                    self.assertEqual(
                        cert.membership(state)[0], inside, (axis, str(scale))
                    )
        wrong = replace(
            self.fixture.center,
            C=tuple(
                str(Q(x) + (1 if i == 0 else 0))
                for i, x in enumerate(self.fixture.center.C)
            ),
            charge="22",
        )
        with self.assertRaisesRegex(ValueError, "exact charge"):
            cert.membership(wrong)
        data = cert.operands.to_dict()
        data["S"].pop()
        with self.assertRaisesRegex(ValueError, "all independent C/logW"):
            CompletionCertificate(FrozenJSONMap(data))
        from tests.models.test_grc_9_v4_spark_completion import (
            NativeSparkCompletionTests,
        )

        NativeSparkCompletionTests.setUpClass()
        with self.assertRaises((ValueError, TypeError)):
            NativeSparkCompletionTests.certificates[0].membership(self.fixture.center)
        self.measurements["chart"] = {
            "all_30_near_faces": True,
            "charge_separate": True,
            "omitted_W_rejects": True,
            "C_family_certificate_rejects": True,
        }

    def test_signed_edge_reindexing_permutes_W_without_sign(self):
        state = sentinel(self.event.configuration.current)
        payload = state.graph.to_payload()
        m = len(state.W_A)
        perm = list(reversed(range(m)))
        sign = [-1 if i % 3 == 0 else 1 for i in range(m)]
        payload["edges"] = [deepcopy(payload["edges"][i]) for i in perm]
        for i, e in enumerate(payload["edges"]):
            if sign[i] < 0:
                e["tail"], e["head"] = e["head"], e["tail"]
        graph = GRCV4Graph.from_payload(payload)
        moved = replace(state, graph=graph, W_A=tuple(state.W_A[i] for i in perm))
        a = owner.kernel(self.event.configuration).step(state)
        b = native.SparkAOSKernel(graph, profile(graph)).step(moved)
        verify_step(a)
        verify_step(b)
        self.assertEqual(a.after.C, b.after.C)
        self.assertEqual(b.after.W_A, tuple(a.after.W_A[i] for i in perm))
        P = arb_mat(
            [[sign[i] if j == perm[i] else 0 for j in range(m)] for i in range(m)]
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload()).selected(
                arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            )
            for key in ("current", "causal_flat"):
                self.assertTrue(
                    contains(b.consumed_read["corrector"][key], P * r["corrector"][key])
                )
            self.assertTrue(contains(b.consumed_read["H"], P * r["H"] * P.transpose()))
        with self.assertRaisesRegex(ValueError, "state graph"):
            self.certs[0].membership(moved)
        self.measurements["covariance"] = {
            "permutation": perm,
            "signs": sign,
            "scalar_W_only_permuted": True,
            "exact_represented_result": True,
        }

    def test_all_transaction_faults_preserve_complete_C_W_publication(self):
        for phase in (
            "corrector",
            "resource_gate",
            "writer_target",
            "log_writer",
            "poststate",
            "prepared_window",
        ):
            m = self.fixture.synthetic_window_fixture()
            self.assertTrue(m.step().committed)
            snapshot = m.snapshot()
            publication = m._operation._spark_scope.published
            if phase == "corrector":
                original = AOSMath.read
                counter = []

                def fail(*args, original=original, counter=counter):
                    result = original(*args)
                    counter.append(1)
                    if len(counter) == 2:
                        raise RuntimeError("injected corrector")
                    return result

                context = patch.object(AOSMath, "read", fail)
            elif phase == "resource_gate":
                original = ExactResources.advance

                def fail(*args, original=original):
                    original(*args)
                    raise RuntimeError("injected resource gate")

                context = patch.object(ExactResources, "advance", fail)
            elif phase == "writer_target":
                original = AOSMath.exponent
                counter = []

                def fail(*args, original=original, counter=counter):
                    result = original(*args)
                    counter.append(1)
                    if len(counter) == 3:
                        raise RuntimeError("injected writer target")
                    return result

                context = patch.object(AOSMath, "exponent", fail)
            elif phase == "log_writer":
                original = native._midpoints

                def fail(values, bits, label, original=original):
                    result = original(values, bits, label)
                    if bits == native.WRITER_BITS:
                        raise RuntimeError("injected log writer")
                    return result

                context = patch.object(native, "_midpoints", fail)
            elif phase == "poststate":
                original = native.SparkAOSKernel._admitted_read
                counter = []

                def fail(*args, original=original, counter=counter):
                    result = original(*args)
                    counter.append(1)
                    if len(counter) == 2:
                        raise RuntimeError("injected poststate")
                    return result

                context = patch.object(native.SparkAOSKernel, "_admitted_read", fail)
            else:
                original = owner.progress

                def fail(*args, original=original):
                    original(*args)
                    raise RuntimeError("injected window")

                context = patch.object(owner, "progress", fail)
            with context:
                result = m.step()
            self.assertFalse(result.committed, phase)
            self.assertIn("injected", result.reason)
            self.assertEqual(m.snapshot(), snapshot, phase)
            self.assertIs(m._operation._spark_scope.published, publication)
            self.assertTrue(m.step().committed)
        self.measurements["rollback"] = {
            "ordinary_phases": 6,
            "whole_scope_compared": True,
            "retries": 6,
        }

    def test_reset_only_event_failure_is_atomic_and_preserves_old_histories(self):
        m = GRC9V4(self.config)
        self.assertTrue(m.step().committed)
        snapshot = m.snapshot()
        root = m._operation._spark_scope.published
        original = native.SparkAOSKernel.readmission

        # Identify reset by its preserved below-one edge, independently of target ordering.
        def fail(k, state):
            if len(state.C) == 15 and any(Q(w) == Q(8191, 8192) for w in state.W_A):
                raise RuntimeError("injected target reset admission")
            return original(k, state)

        with patch.object(native.SparkAOSKernel, "readmission", fail):
            result = m.expand(request(m))
        self.assertFalse(result.committed)
        self.assertIn("injected target reset", result.reason)
        self.assertEqual(m.snapshot(), snapshot)
        self.assertIs(m._operation._spark_scope.published, root)
        self.assertTrue(m.expand(request(m)).committed)

    def test_observers_aliasing_equal_C_roles_and_unsupported_durations(self):
        state = sentinel(self.good.after)
        config = replace(self.config, current=state, reset=sentinel(state, -1))
        a, b = GRC9V4(config), GRC9V4(config)
        self.assertEqual(config.current.C, config.reset.C)
        self.assertNotEqual(config.current.W_A, config.reset.W_A)
        for _ in range(2):
            before = a.snapshot()
            with patch.object(
                native.SparkAOSKernel,
                "_writer",
                side_effect=AssertionError("observation wrote history"),
            ):
                a.compute_observables()
                snapshot = a.snapshot()
                restored = GRC9V4.from_state(snapshot)
            changed = deepcopy(state.to_payload())
            changed["W_A"][0] = "1"

            def poison(value):
                if isinstance(value, dict):
                    for key, child in value.items():
                        if key == "W_A":
                            child[0] = "0"
                        else:
                            poison(child)
                elif isinstance(value, list):
                    for child in value:
                        poison(child)

            poison(snapshot)
            self.assertEqual(a.snapshot(), before)
            self.assertEqual(restored.configuration, a.configuration)
            self.assertTrue(a.step().committed and b.step().committed)
            self.assertEqual(a.configuration, b.configuration)
        from pygrc.models.grc_v4 import GRCV4StepRequestInput

        for duration in (0, -1, 1, 64):
            before = a.snapshot()
            result = a.step_v4_input(
                GRCV4StepRequestInput(
                    "grcv4-step-request-input-v1",
                    "unsupported",
                    duration,
                    FrozenJSONMap({}),
                )
            )
            self.assertFalse(result.committed)
            self.assertEqual(a.snapshot(), before)
        self.assertTrue(a.reset().committed)
        self.assertEqual(a.configuration.current.W_A, config.reset.W_A)

    def test_window_replay_replacement_and_once_only_accounting(self):
        m = self.fixture.synthetic_window_fixture()
        fork = m.duplicate()
        for _ in range(2):
            self.assertTrue(m.step().committed)
        pending = m.snapshot()
        restored = GRC9V4.from_state(pending)
        self.assertEqual(m.step().local_gain, 1)
        self.assertEqual(restored.step().local_gain, 0)
        for _ in range(3):
            self.assertEqual(fork.step().local_gain, 0)
        self.assertTrue(m.install_completion_certificates(*self.certs).committed)
        self.assertEqual(m.step().local_gain, 0)
        self.measurements["synthetic_window"] = {
            "source_to_entry_claimed": False,
            "shared_once_only_credit": True,
            "replay_and_replacement_no_gain": True,
        }

    def test_native_execution_without_research_files_or_imports(self):
        k = owner.kernel(self.config)
        state = self.good.before
        original = builtins.__import__
        read = Path.read_bytes

        def guarded(name, *args, **kw):
            if name.startswith(("research.", "spark_completion_")):
                raise AssertionError("research evaluator")
            return original(name, *args, **kw)

        def guarded_file(path, *args, **kw):
            if "/evidence/" in str(path) or "/tranche-9/" in str(path):
                raise AssertionError("trajectory input")
            return read(path, *args, **kw)

        with (
            patch.object(builtins, "__import__", guarded),
            patch.object(Path, "read_bytes", guarded_file),
        ):
            step = k.step(state)
        verify_step(step)

    def test_each_W_role_is_individually_discriminated(self):
        state = self.good.before
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload())
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            H = arb_mat(r.I)
            H[0, 1] = H[1, 0] = Q(1, 10)
            expected = r.read(C, W, H)
            delta = r.B.transpose() * C
            stiffness = (
                r.B * arb_mat([[(1 - W[i, 0]) * delta[i, 0]] for i in range(13)]) / 64
            )
            wrong_phi = expected["potential"] + stiffness
            wrong_mobility = -(r.B.transpose() * expected["potential"]) / 1024
            wrong_rows = arb_mat(
                [
                    [x.exp()]
                    for x in r.log_drive(
                        C, arb_mat([[1]] * 13), expected["baseline"]
                    ).entries()
                ]
            )
            wrong_contrast = arb_mat(13, 1)
            cases = {
                "stiffness": ("potential", wrong_phi),
                "mobility": ("baseline", wrong_mobility),
                "weighted_rows": ("drive", wrong_rows),
                "contrast": ("q", wrong_contrast),
            }
            payload = {k: intervals(v) for k, v in expected.items()}
            for name, (key, bad) in cases.items():
                separation(expected[key], bad)
                altered = deepcopy(payload)
                altered[key] = intervals(bad)
                with self.assertRaisesRegex(AssertionError, "fixed-H " + key):
                    fixed_read(state.graph.to_payload(), state.C, state.W_A, H, altered)
                self.measurements["mutations"].append("wrong_W_" + name)
        self.measurements["W_roles"] = {
            "stiffness": True,
            "mobility": True,
            "weighted_rows": True,
            "contrast": True,
            "retained_log_input": "geometric_writer_and_skip_or_overwrite_mutations",
        }

    def test_OS_geometry_ownership_provisional_W_and_writer_retention_mutations(self):
        step = self.good
        k = owner.kernel(self.config)
        bad = step.consumed_read.to_dict()
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(step.before.graph.to_payload())
            C, W = arb_mat(vector(step.before.C)), arb_mat(vector(step.before.W_A))
            value = r.selected(C, W)
            regenerated = r.geometry(value["corrector"]["causal_flat"])
            separation(regenerated, value["H"])
            bad["H"] = intervals(regenerated)
            with self.assertRaisesRegex(AssertionError, "literal star geometry"):
                verify_step(replace(step, consumed_read=FrozenJSONMap(bad)))
            second = r.read(C, W, regenerated)
            separation(second["current"], value["corrector"]["current"])
            bad["corrector"] = {key: intervals(v) for key, v in second.items()}
            with self.assertRaisesRegex(AssertionError, "literal star geometry"):
                verify_step(replace(step, consumed_read=FrozenJSONMap(bad)))
            driver = r.log_drive(
                arb_mat(vector(step.after.C)), W, value["corrector"]["current"]
            )
            overwritten = tuple(
                str(round_flux(x.exp().mid().fmpq() * 2**64) / 2**64)
                for x in driver.entries()
            )
        provisional = replace(step.before, W_A=step.after.W_A)
        bad = k.readmission(provisional).to_dict()
        bad["subject_digest"] = step.consumed_read["subject_digest"]
        with self.assertRaisesRegex(
            AssertionError, "literal star geometry|predictor potential"
        ):
            verify_step(replace(step, consumed_read=FrozenJSONMap(bad)))
        for name, weights in (
            ("skip_writer", step.before.W_A),
            ("overwrite_with_drive", overwritten),
        ):
            after = replace(step.after, W_A=weights)
            self.assertNotEqual(after.W_A, step.after.W_A)
            badstep = replace(step, after=after, restart_read=k.readmission(after))
            with self.assertRaisesRegex(AssertionError, "nearest-even conductance"):
                verify_step(badstep)
            self.measurements["mutations"].append(name)
        self.measurements["mutations"] += [
            "regenerated_geometry_replaces_consumed",
            "second_OS_pass",
            "provisional_W_before_corrector",
        ]


if __name__ == "__main__":
    unittest.main()
