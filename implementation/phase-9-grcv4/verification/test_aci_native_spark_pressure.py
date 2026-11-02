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
from aci_native_spark_audit import (
    audit_event,
    audit_step,
    audit_trace,
    digest,
    fixed_read,
    separation,
)
from aci_native_spark_oracle import Reference, contains, verify_step
from aci_native_spark_oracle import classify as independent_classify
from cos_native_spark_oracle import matrix, vector
from cpc_native_spark_pressure_oracle import decode, intervals
from p991a6_aci_preflight import transition
from p991a6_aci_subjects import profile, request

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_aci as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import (
    _ARB_CONTEXT_LOCK,
)
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_aci_math import ACIMath
from pygrc.models.grc_v4_spark_conductance import ExactConductanceState
from pygrc.models.grc_v4_spark_state import ExactResources, round_flux
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_aci as fixtures


def sentinel(state, sign=1):
    return replace(
        state, W_A=tuple(str(1 + sign * Q(i + 1, 2**14)) for i in range(len(state.W_A)))
    )


def observed(model):
    """Observe every root/read/drive operand before any atomic publication."""
    initial = model.configuration
    publication = model._operation._spark_scope.published
    records, steps, writes = [], [], []
    active = ["other"]
    root_inputs = []
    read, writer, step, root, exponent, advance = (
        ACIMath.read,
        native.SparkACIKernel._writer,
        native.SparkACIKernel.step,
        ACIMath.root,
        ACIMath.exponent,
        ExactConductanceState.advance_conductance,
    )

    def frozen():
        if (
            model.configuration != initial
            or model._operation._spark_scope.published is not publication
        ):
            raise AssertionError("provisional calculation published progress")

    def capture_root(math, C, L, *args):
        frozen()
        active.append("root")
        root_inputs.append(C)
        records.append({"stage": "root_start", "C": intervals(C), "L": intervals(L)})
        try:
            result = root(math, C, L, *args)
            records.append({"stage": "root_end", "iterations": result["iterations"]})
            return result
        finally:
            active.pop()
            root_inputs.pop()

    def capture_read(math, C, W, H, *args):
        frozen()
        result = read(math, C, W, H, *args)
        records.append(
            {
                "stage": "fixed_read",
                "phase": active[-1],
                "subject_mode": "actual_input"
                if root_inputs and C is root_inputs[-1]
                else "proposal_midpoint",
                "C": intervals(C),
                "W": intervals(W),
                "H": intervals(H),
                "result": {k: intervals(v) for k, v in result.items()},
            }
        )
        return result

    def capture_exponent(math, C, W, J, *args):
        frozen()
        result = exponent(math, C, W, J, *args)
        records.append(
            {
                "stage": "drive",
                "phase": active[-1],
                "C": intervals(C),
                "W": intervals(W),
                "J": intervals(J),
                "value": intervals(result[0]),
            }
        )
        return result

    def capture_writer(k, state, after, consumed):
        frozen()
        active.append("writer")
        try:
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
        finally:
            active.pop()

    def capture_advance(state, *args):
        frozen()
        writes.append(state)
        return advance(state, *args)

    def capture_step(k, *args, **kwargs):
        value = step(k, *args, **kwargs)
        steps.append(value)
        return value

    with (
        patch.object(ACIMath, "root", capture_root),
        patch.object(ACIMath, "read", capture_read),
        patch.object(ACIMath, "exponent", capture_exponent),
        patch.object(native.SparkACIKernel, "_writer", capture_writer),
        patch.object(native.SparkACIKernel, "step", capture_step),
        patch.object(ExactConductanceState, "advance_conductance", capture_advance),
    ):
        result = model.step()
    if not result.committed:
        raise AssertionError(result.reason)
    if len(steps) != 1 or len(writes) != 1:
        raise AssertionError("one physical C/W write per step")
    return steps[0], records


class ACINativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeACITests.setUpClass()
        cls.fixture = fixtures.NativeACITests()
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
            {"a": "0", "b": "1", "c": "3"},
            [("a", 1, "b", 4), ("a", 2, "c", 7), ("a", 4, "b", 5), ("a", 7, "c", 8)],
        )
        state = ExactConductanceState(
            state.graph, state.C, state.charge, ("4095/4096", "4097/4096", "1", "1")
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            math = ACIMath(state.graph)
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            dC = arb_mat(3, 4)
            dW = arb_mat(
                [[W[i, 0] if i == j else 0 for j in range(4)] for i in range(4)]
            )
            rows, der = math.rows(C, W, dC, dW)
            self.assertTrue(rows[0][0].contains(Q(8193, 4096)))
            self.assertFalse(rows[0][0].contains(Q(8191, 4096)))
            self.assertFalse(rows[0][0].contains(2))
            self.assertTrue(rows[0][1].contains(Q(1)) and rows[0][2].contains(Q(3)))
            self.assertEqual(rows[1][0], 0)
            self.assertTrue(rows[1][1].contains(-Q(1)))
            self.assertEqual(rows[2][1], 0)
            self.assertTrue(rows[2][2].contains(-Q(3)))
            for k, delta in enumerate((Q(1), Q(3))):
                expected = Q(state.W_A[k]) / 2 * (delta - Q(8193, 4096))
                self.assertTrue(der[0][0][k].contains(expected))
            diagnostics = state.spatial_diagnostics(
                sign=1,
                gradient="4",
                hessian="1/8",
                contrast="1/16",
                core_resource="1/16",
            )
            self.assertEqual(diagnostics[0]["gradient"][0], "8193/4096")
            swapped = replace(state, W_A=("4097/4096", "4095/4096", "1", "1"))
            self.assertEqual(
                swapped.spatial_diagnostics(
                    sign=1,
                    gradient="4",
                    hessian="1/8",
                    contrast="1/16",
                    core_resource="1/16",
                )[0]["gradient"][0],
                "8191/4096",
            )
            with self.assertRaisesRegex(RuntimeError, "positive fixed-row denominator"):
                math.rows(C, arb_mat(vector(("1", "-1", "1", "1"))))
        self.measurements["weighted_row"] = {
            "correct": "8193/4096",
            "swapped": "8191/4096",
            "unweighted": "2",
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
            J = r.selected(arb_mat(vector(state.C)), W)["selected"]["current"]
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
            null = dict(read, selected=dict(read["selected"], current=arb_mat(13, 1)))
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
        math = ACIMath(state.graph)
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
            J = s["selected"]["current"]
            correct = r.log_drive(C1, W, J)
            variants = {
                "stale_C": r.log_drive(C, W, J),
                "baseline_J": r.log_drive(C1, W, s["selected"]["baseline"]),
                "predictor_J": r.log_drive(C1, W, r.read(C, W, r.I)["current"]),
                "new_W": r.log_drive(C1, W1, J),
                "future_J": r.log_drive(
                    C1, W, r.selected(C1, W1)["selected"]["current"]
                ),
                "pre_read_G": r.log_drive(C, W, s["selected"]["baseline"]),
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
            fresh = r.selected(C, arb_mat(vector(a.after.W_A)))["selected"]["current"]
            old = r.selected(C, arb_mat(vector(state.W_A)))["selected"]["current"]
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
                with patch.object(ACIMath, "exponent", return_value=(logs, None)):
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
                native.SparkACIKernel(
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
            math = ACIMath(self.good.before.graph)
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
            math = ACIMath(state.graph)
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
        b = native.SparkACIKernel(graph, profile(graph)).step(moved)
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
                    contains(b.consumed_read["selected"][key], P * r["selected"][key])
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

    def test_reset_only_event_failure_is_atomic_and_preserves_old_histories(self):
        m = GRC9V4(self.config)
        self.assertTrue(m.step().committed)
        snapshot = m.snapshot()
        root = m._operation._spark_scope.published
        original = native.SparkACIKernel.readmission

        # Identify reset by its preserved below-one edge, independently of target ordering.
        def fail(k, state):
            if len(state.C) == 15 and any(Q(w) == Q(8191, 8192) for w in state.W_A):
                raise RuntimeError("injected target reset admission")
            return original(k, state)

        with patch.object(native.SparkACIKernel, "readmission", fail):
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
                native.SparkACIKernel,
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

    def test_frozen_public_CI_trials_drives_and_one_physical_writer(self):
        source = GRC9V4(self.config)
        before = source.configuration
        step, trace = observed(source)
        self.evidence["source_step"] = {
            "subject": before.to_payload(),
            "step": transition(step),
            "role": "current",
            "audit": audit_step(before, before.current, step),
        }
        self.assertTrue(source.expand(request(source)).committed)
        counts = []
        for role in ("current", "reset"):
            model = source.duplicate()
            if role == "reset":
                self.assertTrue(model.reset().committed)
            for beat in range(2):
                config = model.configuration
                before = config.current
                step, trace = observed(model)
                positions = [
                    i for i, row in enumerate(trace) if row["stage"] == "writer"
                ]
                self.assertEqual(len(positions), 1)
                self.assertEqual(sum(row["stage"] == "root_start" for row in trace), 2)
                with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                    r = Reference(before.graph.to_payload())
                    for subject, rows in (
                        (before, trace[: positions[0]]),
                        (step.after, trace[positions[0] + 1 :]),
                    ):
                        C, W = arb_mat(vector(subject.C)), arb_mat(vector(subject.W_A))
                        reads = [
                            row
                            for row in rows
                            if row["stage"] == "fixed_read" and row["phase"] == "root"
                        ]
                        self.assertTrue(reads)
                        self.assertEqual(
                            [row["subject_mode"] for row in reads[-2:]],
                            ["actual_input", "actual_input"],
                        )
                        for row in reads:
                            if row["subject_mode"] == "actual_input":
                                self.assertTrue(
                                    contains(row["C"], C) and contains(row["W"], W)
                                )
                                cc, ww = subject.C, subject.W_A
                            else:
                                self.assertEqual(row["C"], reads[0]["C"])
                                self.assertEqual(row["W"], reads[0]["W"])
                                cc = tuple(
                                    str(v.fmpq()) for v in decode(row["C"]).entries()
                                )
                                ww = tuple(
                                    str(v.fmpq()) for v in decode(row["W"]).entries()
                                )
                            H = decode(row["H"])
                            point = arb_mat(
                                [
                                    [H[i, j].mid() for j in range(r.m)]
                                    for i in range(r.m)
                                ]
                            )
                            fixed_read(
                                subject.graph.to_payload(), cc, ww, point, row["result"]
                            )
                        drives = [
                            row
                            for row in rows
                            if row["stage"] == "drive" and row["phase"] == "root"
                        ]
                        self.assertEqual(len(drives), len(reads))
                        for drive, read in zip(drives, reads, strict=True):
                            self.assertEqual(drive["C"], read["C"])
                            self.assertEqual(drive["W"], read["W"])
                            self.assertEqual(drive["J"], read["result"]["baseline"])
                        counts.append(len(reads))
                    writer_drives = [
                        row
                        for row in trace
                        if row["stage"] == "drive" and row["phase"] == "writer"
                    ]
                    self.assertEqual(len(writer_drives), 1)
                    wd = writer_drives[0]
                    self.assertTrue(contains(wd["C"], arb_mat(vector(step.after.C))))
                    self.assertTrue(contains(wd["W"], arb_mat(vector(before.W_A))))
                    self.assertEqual(wd["J"], step.writer.to_dict()["selected_current"])
                    value = r.selected(
                        arb_mat(vector(before.C)), arb_mat(vector(before.W_A))
                    )
                    H0 = r.I
                    initial = r.read(
                        arb_mat(vector(before.C)), arb_mat(vector(before.W_A)), H0
                    )
                    separation(initial["current"], value["selected"]["current"])
                    separation(initial["drive"], value["selected"]["drive"])
                cert = self.certs[int(role == "reset")]
                self.evidence["actual_steps"].append(
                    {
                        "subject": config.to_payload(),
                        "step": transition(step),
                        "role": role,
                        "certificate": cert.to_payload(),
                        "audit": audit_step(config, before, step, cert, role),
                    }
                )
                # One full operand trace is sufficient; remaining stages are checked live.
                if role == "current" and beat == 0:
                    self.evidence["operand_trace"] = trace
                    self.evidence["operand_trace_audit"] = audit_trace(step, trace)
        self.measurements["CI_staging"] = {
            "actual_target_steps": 4,
            "root_trial_read_counts": counts,
            "incoming_C_W_frozen": True,
            "baseline_read_drive": True,
            "final_C_incoming_W_selected_J_writer": True,
            "one_physical_writer": True,
        }

    def test_fresh_read_reference_root_and_provisional_history_mutations(self):
        step = self.good
        state = step.before
        k = owner.kernel(self.config)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload())
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            value = r.selected(C, W)
            selected = value["selected"]
            initial = r.read(C, W, r.I)
            total_drive = arb_mat(
                [[x.exp()] for x in r.log_drive(C, W, selected["current"]).entries()]
            )
            for name, key, wrong in (
                ("freeze_trial_read_drive", "drive", initial["drive"]),
                ("total_J_in_read_drive", "drive", total_drive),
                ("initial_geometry_current", "current", initial["current"]),
                ("initial_geometry_baseline", "baseline", initial["baseline"]),
            ):
                separation(selected[key], wrong)
                bad = step.consumed_read.to_dict()
                bad["selected"][key] = intervals(wrong)
                with self.assertRaisesRegex(AssertionError, "selected " + key):
                    verify_step(replace(step, consumed_read=FrozenJSONMap(bad)))
                self.measurements["mutations"].append(name)
            driver = r.log_drive(arb_mat(vector(step.after.C)), W, selected["current"])
            overwritten = tuple(
                str(round_flux(x.exp().mid().fmpq() * 2**64) / 2**64)
                for x in driver.entries()
            )
        provisional = replace(state, W_A=step.after.W_A)
        bad = k.readmission(provisional).to_dict()
        bad["subject_digest"] = step.consumed_read["subject_digest"]
        with self.assertRaises(AssertionError):
            verify_step(replace(step, consumed_read=FrozenJSONMap(bad)))
        self.measurements["mutations"].append("provisional_W_inside_root")
        for name, weights in (
            ("skip_writer", state.W_A),
            ("overwrite_with_drive", overwritten),
        ):
            after = replace(step.after, W_A=weights)
            self.assertNotEqual(after.W_A, step.after.W_A)
            badstep = replace(step, after=after, restart_read=k.readmission(after))
            with self.assertRaisesRegex(AssertionError, "nearest-even conductance"):
                verify_step(badstep)
            self.measurements["mutations"].append(name)

    def test_more_root_iterations_never_write_more_physical_history(self):
        from pygrc.models import grc_v4_spark_aci_math as root_math

        outcomes = []
        counts = []
        for bits in (224, 240):
            m = GRC9V4(self.config)
            with patch.object(root_math, "PROPOSAL_BITS", bits):
                step, trace = observed(m)
            verify_step(step)
            outcomes.append(step.after)
            counts.append([r["iterations"] for r in trace if r["stage"] == "root_end"])
            self.assertEqual(sum(r["stage"] == "writer" for r in trace), 1)
        self.assertEqual(outcomes[0], outcomes[1])
        self.assertNotEqual(counts[0], counts[1])
        self.measurements["iteration_control"] = {
            "experimental_thresholds": [224, 240],
            "iterations": counts,
            "physical_writes_per_step": 1,
            "identical_states": True,
            "native_policy_changed": False,
        }

    def test_full_implicit_derivative_sweep_and_specific_omission_mutations(self):
        from aci_native_spark_audit import derivative_mutation

        graph = self.event.configuration.current.graph
        n, e = len(graph.live_node_ids), len(graph.live_edge_ids)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            C = arb_mat([[Q(5, 4) + Q((i * 7) % 11, 32)] for i in range(n)])
            W = arb_mat([[1 + Q((i * 5) % 13 - 6, 2048)] for i in range(e)])
            L = arb_mat([[w.log()] for w in W.entries()])
            x = arb_mat(C.tolist() + L.tolist())
            math = ACIMath(graph)
            r = Reference(graph.to_payload())
            directions = []
            for k in range(n - 1):
                directions.append(
                    arb_mat(
                        [[int(i == k) - int(i == n - 1)] for i in range(n)] + [[0]] * e
                    )
                )
            for k in range(e):
                directions.append(
                    arb_mat([[0]] * n + [[int(i == k)] for i in range(e)])
                )
            for phase in range(4):
                dc = [Q((i + phase) % 3 - 1) for i in range(n - 1)]
                dc.append(-sum(dc))
                directions.append(
                    arb_mat(vector(dc + [Q((i + phase) % 5 - 2, 16) for i in range(e)]))
                )
            reports = []
            detection = {}
            variants = (
                "omit_Ff",
                "freeze_root",
                "freeze_read_drive",
                "omit_row_denominator",
                "drop_C_from_logW",
                "drop_logW_from_C",
            )
            for bits in (112, 128, 144):
                eps = Q(1, 2**bits)
                for axis, d in enumerate(directions):
                    box = arb_mat(
                        [
                            [x[i, 0] + arb(0, abs(d[i, 0]).upper().fmpq() * eps)]
                            for i in range(n + e)
                        ]
                    )
                    cb, lb = arb_mat(box.tolist()[:n]), arb_mat(box.tolist()[n:])
                    J = math.jacobian(cb, lb)
                    p = x + eps * d
                    m = x - eps * d
                    finite = (
                        r.map(arb_mat(p.tolist()[:n]), arb_mat(p.tolist()[n:]))
                        - r.map(arb_mat(m.tolist()[:n]), arb_mat(m.tolist()[n:]))
                    ) / (2 * eps)
                    self.assertTrue(
                        all(
                            a.contains(b) or (a.is_zero() and b.contains(0))
                            for a, b in zip(
                                (J * d).entries(), finite.entries(), strict=True
                            )
                        ),
                        (bits, axis),
                    )
                    self.assertTrue(
                        all(v.rad() < arb(2) ** -400 for v in finite.entries())
                    )
                    for variant in variants:
                        if variant not in detection:
                            bad = derivative_mutation(math, cb, lb, variant) * d
                            difference = max(
                                abs(a - b).lower().fmpq()
                                for a, b in zip(
                                    bad.entries(), finite.entries(), strict=True
                                )
                            )
                            if difference > 0:
                                detection[variant] = {
                                    "axis": axis,
                                    "bits": bits,
                                    "separation_lower": str(difference),
                                }
                    reports.append(
                        {
                            "axis": axis,
                            "bits": bits,
                            "independent_secant_consistent": True,
                        }
                    )
            self.assertEqual(set(detection), set(variants))
        self.measurements["implicit_derivatives"] = {
            "physical_axes": 30,
            "mixed_directions": 4,
            "step_size_bits": [112, 128, 144],
            "segments": reports,
            "detected": detection,
            "all_four_blocks": True,
        }
        self.measurements["mutations"] += list(variants)

    def test_root_domain_proposals_cache_clearing_and_false_authority(self):
        from aci_native_spark_audit import admit_proposal
        from aci_native_spark_oracle import audit_read
        from aos_native_spark_oracle import upper

        from pygrc.models.grc_9_v4_completion_certificate import _verify
        from pygrc.models.grc_v4_spark_aci_math import root_domain
        from pygrc.models.grc_v4_spark_conductance import _fixed_rows
        from pygrc.models.grc_v4_spark_cos import _reference_facts

        state = self.good.before
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            r = Reference(state.graph.to_payload())
            selected = r.selected(C, W)
            start = r.read(C, W, r.I)["causal_flat"]
            starts = (
                arb_mat(r.m, 1),
                arb_mat([[v.mid()] for v in start.entries()]),
                arb_mat([[Q((-1) ** i, 4096)] for i in range(r.m)]),
            )
            for proposal in starts:
                for _ in range(60):
                    candidate = r.read(C, W, r.geometry(proposal))["causal_flat"]
                    if upper(candidate - proposal) < Q(1, 2**640):
                        break
                    proposal = arb_mat([[v.mid()] for v in candidate.entries()])
                else:
                    self.fail("independent proposal failed to converge")
                _residual, error = admit_proposal(r, C, W, proposal)
                for i in range(r.m):
                    self.assertTrue(
                        arb(proposal[i, 0].fmpq(), error).overlaps(
                            selected["flat"][i, 0]
                        )
                    )
            with self.assertRaisesRegex(AssertionError, "outside declared root ball"):
                admit_proposal(r, C, W, arb_mat([[Q(1, 16)]] * r.m))
            # An OS proposal is mathematically admissible if its actual residual
            # gives a ball inside the domain; no minimum iteration count decides this.
            os_proposal = arb_mat([[v.mid()] for v in start.entries()])
            os_residual, os_error = admit_proposal(r, C, W, os_proposal)
            self.assertLess(upper(os_proposal) + os_error, Q(1, 32))
            for key, value in (
                ("root_error", ["0", "0"]),
                ("proposal_residual", ["0", "0"]),
                (
                    "domain",
                    self.good.restart_read["domain"].to_dict() | {"contraction": "0"},
                ),
                ("conditioning_upper", "1"),
            ):
                bad = self.good.consumed_read.to_dict()
                bad[key] = value
                with self.assertRaises(AssertionError):
                    audit_read(r, state, bad)
                self.measurements["mutations"].append("false_root_" + key)
        k = owner.kernel(self.config)
        first = k.step(state)
        for cache in (root_domain, _reference_facts, _fixed_rows, _verify):
            cache.cache_clear()
        second = owner.kernel(self.config).step(state)
        self.assertEqual(first, second)
        cert = self.certs[0].to_payload()
        cert["proof"]["q"] = self.good.consumed_read["domain"]["contraction"]
        with self.assertRaisesRegex(ValueError, "recomputed mathematics"):
            CompletionCertificate.from_payload(cert)
        self.measurements["root_authority"] = {
            "independent_start_proposals": 3,
            "same_enclosed_root": True,
            "OS_proposal_error": str(os_error),
            "OS_proposal_residual": str(os_residual),
            "native_policy_zero_start_unchanged": True,
            "caches_not_authoritative": True,
            "inner_root_rate_not_physical_contraction": True,
        }

    def test_nonfinite_exhaustion_conditioning_and_root_admission_rollback(self):
        from pygrc.models import grc_v4_spark_aci_math as math_module

        contexts = []
        original = ACIMath.read

        def nonfinite(math, *args):
            value = original(math, *args)
            value["causal_flat"] = arb_mat([[arb("nan")]] * math.m)
            return value

        contexts.append(patch.object(math_module, "PROPOSAL_BITS", 1024))
        contexts.append(patch.object(ACIMath, "read", nonfinite))
        for context in contexts:
            m = self.event.duplicate()
            snapshot = m.snapshot()
            publication = m._operation._spark_scope.published
            with context:
                result = m.step()
            self.assertFalse(result.committed)
            self.assertEqual(m.snapshot(), snapshot)
            self.assertIs(m._operation._spark_scope.published, publication)
            self.assertTrue(m.step().committed)
        graph = self.config.reference.graph
        short = native.SparkACIKernel(
            graph,
            profile(
                graph, realization={"iteration_limit": 1}, solver={"iteration_limit": 1}
            ),
        )
        with self.assertRaisesRegex(RuntimeError, "iteration limit"):
            short.readmission(self.good.before)
        poor = native.SparkACIKernel(
            graph, profile(graph, solver={"conditioning_limit": 2})
        )
        with self.assertRaisesRegex(RuntimeError, "conditioning"):
            poor.readmission(self.good.before)
        self.measurements["root_failures"] = {
            "nonfinite": True,
            "exhaustion": True,
            "conditioning": True,
            "no_fallback": True,
        }

    def test_wrong_production_residuals_do_not_validate_themselves(self):
        from aci_native_spark_oracle import audit_read

        state = self.good.before
        k = owner.kernel(self.config)
        original = ACIMath.read
        for variant in ("frozen_read_reference", "total_current_read_reference"):
            frozen = []

            def mutated(math, C, W, H, rows=None, variant=variant, frozen=frozen):
                result = original(math, C, W, H, rows)
                if variant == "frozen_read_reference":
                    if not frozen:
                        frozen.append(result["drive"])
                    G = frozen[0]
                else:
                    ex, _ = math.exponent(C, W, result["current"], rows)
                    G = math.exp(ex)
                q = arb_mat(
                    [[(W[i, 0] - G[i, 0]) / (W[i, 0] + G[i, 0])] for i in range(math.m)]
                )
                J = arb_mat(
                    [
                        [result["baseline"][i, 0] / (1 - q[i, 0] / 4)]
                        for i in range(math.m)
                    ]
                )
                flat = H.solve(
                    arb_mat([[q[i, 0] * J[i, 0] / 2] for i in range(math.m)])
                )
                return dict(result, drive=G, q=q, current=J, causal_flat=flat)

            with patch.object(ACIMath, "read", mutated):
                payload = k.readmission(state)
            # Native residuals are self-consistent for the injected wrong law.
            # The independently reconstructed simultaneous equations must fail.
            with (
                _ARB_CONTEXT_LOCK,
                ctx.workprec(768),
                self.assertRaises(AssertionError),
            ):
                audit_read(Reference(state.graph.to_payload()), state, payload)
            self.measurements["mutations"].append("production_" + variant)

    def test_certificate_exact_subject_bindings_and_center_defect(self):
        cert = self.certs[0]
        base = cert.operands.to_dict()
        cases = {
            "graph_incidence": lambda v: v["binding"]["graph"]["edges"][0].update(
                tail=v["binding"]["graph"]["edges"][1]["tail"]
            ),
            "row_assignment": lambda v: v["binding"]["graph"]["edges"][0][
                "tail"
            ].update(port=3),
            "duration": lambda v: v["binding"].update(duration="16"),
            "site_law": lambda v: v["binding"]["profile"]["params_resolved"][
                "candidate"
            ]["site_binding"].update(mu="2"),
            "reference": lambda v: v["binding"]["reference"].update(H_ref="zero"),
            "charge": lambda v: v["binding"].update(charge="22"),
            "basis": lambda v: v["S"][0].__setitem__(0, "0"),
            "center": lambda v: v["center"].__setitem__(
                0, str(Q(v["center"][0]) + Q(1, 4096))
            ),
            "logW_center": lambda v: v["logW_center"].__setitem__(0, "0"),
            "profile": lambda v: v["binding"]["profile"].update(
                complete_profile_id="wrong"
            ),
            "context": lambda v: v["binding"]["context"].update(evaluator="wrong"),
        }
        for name, edit in cases.items():
            bad = deepcopy(base)
            edit(bad)
            with (
                self.subTest(name=name),
                self.assertRaises((ValueError, TypeError, RuntimeError)),
            ):
                CompletionCertificate(FrozenJSONMap(bad))
            self.measurements["mutations"].append("certificate_" + name)
        self.assertGreater(Q(cert.proof["center_defect"]), 0)
        self.assertLess(Q(cert.proof["q"]) + Q(cert.proof["center_defect"]), 1)
        self.assertLess(Q(cert.proof["full_step_error"]), Q(cert.proof["image_margin"]))
        self.measurements["certificate_subject"] = {
            "negative_bindings": sorted(cases),
            "nonzero_center_defect": True,
            "full_norm_numeric_margin": True,
            "resource_only_rejected": True,
        }

    def test_all_provisional_transaction_stages_roll_back_and_retry_once(self):
        rows = []
        for phase in (
            "accepted_root",
            "continuity",
            "refreshed_writer_rows",
            "constructed_writer",
            "returned_root",
            "completion_preparation",
        ):
            model = self.fixture.synthetic_window_fixture()
            self.assertTrue(model.step().committed)
            self.assertTrue(model.step().committed)
            snapshot = model.snapshot()
            publication = model._operation._spark_scope.published
            calls = []
            active = []
            read = native.SparkACIKernel._admitted_read
            writer = native.SparkACIKernel._writer
            row = ACIMath.rows
            advance = ExactResources.advance
            progress = owner.progress

            def read_fault(k, state, read=read, calls=calls, phase=phase):
                result = read(k, state)
                calls.append(True)
                if (phase == "accepted_root" and len(calls) == 1) or (
                    phase == "returned_root" and len(calls) == 2
                ):
                    raise RuntimeError("injected " + phase)
                return result

            def writer_fault(*args, writer=writer, active=active, phase=phase):
                active.append(True)
                try:
                    result = writer(*args)
                    if phase == "constructed_writer":
                        raise RuntimeError("injected " + phase)
                    return result
                finally:
                    active.pop()

            def rows_fault(*args, row=row, active=active, phase=phase, **kw):
                result = row(*args, **kw)
                if phase == "refreshed_writer_rows" and active:
                    raise RuntimeError("injected " + phase)
                return result

            def advance_fault(*args, advance=advance, phase=phase, **kw):
                result = advance(*args, **kw)
                if phase == "continuity":
                    raise RuntimeError("injected " + phase)
                return result

            def progress_fault(*args, progress=progress, phase=phase, **kw):
                result = progress(*args, **kw)
                if phase == "completion_preparation":
                    raise RuntimeError("injected " + phase)
                return result

            with (
                patch.object(native.SparkACIKernel, "_admitted_read", read_fault),
                patch.object(native.SparkACIKernel, "_writer", writer_fault),
                patch.object(ACIMath, "rows", rows_fault),
                patch.object(ExactResources, "advance", advance_fault),
                patch.object(owner, "progress", progress_fault),
            ):
                result = model.step()
            self.assertFalse(result.committed, phase)
            self.assertIn("injected", result.reason)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertIs(model._operation._spark_scope.published, publication)
            retry = model.step()
            self.assertTrue(retry.committed)
            self.assertEqual(retry.local_gain, 1)
            self.assertEqual(model.step().local_gain, 0)
            rows.append({"phase": phase, "complete_rollback": True, "retry_gain": 1})
        self.measurements["rollback"] = rows

    def test_cold_checkpoint_without_solver_caches_continues_identically(self):
        from pygrc.models.grc_9_v4_completion_certificate import _verify
        from pygrc.models.grc_v4_spark_aci_math import root_domain
        from pygrc.models.grc_v4_spark_conductance import _fixed_rows
        from pygrc.models.grc_v4_spark_cos import _reference_facts

        model = self.event.duplicate()
        self.assertTrue(model.step().committed)
        snapshot = model.snapshot()
        for cache in (root_domain, _reference_facts, _fixed_rows, _verify):
            cache.cache_clear()
        with patch.object(owner, "_SCOPES", {}):
            cold = GRC9V4.from_state(snapshot)
            self.assertEqual(cold.snapshot(), snapshot)
        for _ in range(2):
            a = model.step()
            b = cold.step()
            self.assertTrue(a.committed and b.committed)
            self.assertEqual(a.local_gain, b.local_gain)
            self.assertEqual(model.configuration, cold.configuration)
            self.assertEqual(
                model.snapshot()["owner"]["publication"],
                cold.snapshot()["owner"]["publication"],
            )
        self.measurements["cold_continuation"] = {
            "cacheless_full_replay": True,
            "identical_followup_steps": 2,
        }

    def test_reordered_renamed_signed_source_event_and_lineage_rejections(self):
        from pygrc.models.grc_9_v4_spark_conductance_event import target as transport
        from pygrc.models.grc_9_v4_spark_contracts import SparkReference

        old = replace(
            self.config,
            current=sentinel(self.config.current),
            reset=sentinel(self.config.reset, -1),
        )
        payload = old.reference.graph.to_payload()
        source_nodes = list(payload["live_node_ids"])
        payload["live_node_ids"] = list(reversed(source_nodes))
        original_edges = deepcopy(payload["edges"])
        order = list(reversed(range(len(original_edges))))
        payload["edges"] = [deepcopy(original_edges[i]) for i in order]
        for i, edge in enumerate(payload["edges"]):
            edge["edge_id"] = "renamed/" + edge["edge_id"]
            if i % 2 == 0:
                edge["tail"], edge["head"] = edge["head"], edge["tail"]
        graph = GRCV4Graph.from_payload(payload)

        def mapped(state):
            values = dict(zip(source_nodes, state.C, strict=True))
            return replace(
                state,
                graph=graph,
                C=tuple(values[x] for x in graph.live_node_ids),
                W_A=tuple(state.W_A[i] for i in order),
            )

        config = replace(
            old,
            reference=SparkReference(graph, profile(graph)),
            current=mapped(old.current),
            reset=mapped(old.reset),
        )
        a, b = GRC9V4(old), GRC9V4(config)
        self.assertTrue(a.step().committed and b.step().committed)
        self.assertEqual(
            dict(
                zip(
                    a.configuration.current.graph.live_node_ids,
                    a.configuration.current.C,
                )
            ),
            dict(
                zip(
                    b.configuration.current.graph.live_node_ids,
                    b.configuration.current.C,
                )
            ),
        )
        self.assertEqual(
            b.configuration.current.W_A,
            tuple(a.configuration.current.W_A[i] for i in order),
        )
        source = b.configuration
        self.assertTrue(b.expand(request(b, -1)).committed)
        target = b.configuration
        event = b._operation._published.completion.event.to_dict()
        audit_event(source, target, event)
        self.assertEqual(
            target.current.C[target.current.graph.node_index(event["module"][0])], "0"
        )
        bad = deepcopy(event)
        bad["conductance_history"]["target_edge_ids"][1] = bad["conductance_history"][
            "target_edge_ids"
        ][0]
        with self.assertRaisesRegex(AssertionError, "edge roster"):
            audit_event(source, target, bad)
        missing = target.reference.graph.to_payload()
        old_id = source.reference.graph.live_edge_ids[0]
        next(row for row in missing["edges"] if row["edge_id"] == old_id)["edge_id"] = (
            "missing-old-edge"
        )
        with self.assertRaisesRegex(ValueError, "complete old-edge lineage"):
            transport(source.current, GRCV4Graph.from_payload(missing), ())
        duplicate = deepcopy(payload)
        duplicate["edges"][1]["edge_id"] = duplicate["edges"][0]["edge_id"]
        with self.assertRaises((ValueError, TypeError)):
            GRCV4Graph.from_payload(duplicate)
        self.measurements["event_covariance"] = {
            "node_storage_permutation": True,
            "edge_renaming_permutation_reversal": True,
            "exact_first_step_covariance": True,
            "fresh_target_root": True,
            "missing_and_duplicate_lineage_rejected": True,
        }
        self.measurements["mutations"] += ["missing_old_edge", "duplicate_lineage"]

    def test_all_strict_classifier_thresholds_ties_and_unqualified_terminals(self):
        from pygrc.models.grc_9_v4_completion_codec import CompletionPolicy

        def checked(raw, policy):
            state = ExactConductanceState(
                raw.graph,
                raw.C,
                raw.charge,
                tuple(
                    str(1 + Q(i + 1, 4096)) for i in range(len(raw.graph.live_edge_ids))
                ),
            )
            actual = classify(state, policy)
            expected = independent_classify(
                state.graph.to_payload(), state.C, state.W_A, policy.to_payload()
            )
            self.assertEqual(
                (
                    actual.basins,
                    actual.terminals,
                    [row.to_dict() for row in actual.rows],
                ),
                expected,
            )
            return actual

        star = [("a", 1, "u", 1), ("a", 4, "v", 1), ("a", 7, "w", 1)]
        equal = common.toy({"a": 3, "u": 2, "v": 1, "w": 1}, star)
        delta = Q(1, 2**40)
        for field, bound, above in (
            ("epsilon_gradient", Q(3), True),
            ("epsilon_Hessian", Q(1), False),
            ("contrast", Q(1), False),
            ("minimum_resource", Q(3), False),
        ):
            for sign in (-1, 0, 1):
                policy = replace(
                    CompletionPolicy(), **{field: str(bound + sign * delta)}
                )
                result = checked(equal, policy)
                self.assertEqual(
                    next(row for row in result.rows if row["node_id"] == "a")["anchor"],
                    (sign == 1 if above else sign == -1),
                    (field, sign),
                )
        empty = common.toy({"a": 3, "u": 1, "v": 1}, star[:2])
        self.assertFalse(
            next(
                row
                for row in checked(empty, CompletionPolicy()).rows
                if row["node_id"] == "a"
            )["seed"]
        )
        mixed = common.toy(
            {"a": 3, "b": 4, "u": 1, "v": 1, "w": 1}, star + [("u", 2, "b", 1)]
        )
        result = checked(mixed, CompletionPolicy())
        self.assertEqual(dict(result.terminals)["u"], ("a", "b"))
        self.assertNotIn("u", dict(result.basins)["a"])
        self.assertFalse(
            next(row for row in result.rows if row["node_id"] == "b")["anchor"]
        )
        for sign in (-1, 0, 1):
            tied = common.toy(
                {"a": "2", "b": str(2 + sign * delta)}, [("a", 1, "b", 1)]
            )
            terminals = dict(checked(tied, CompletionPolicy()).terminals)
            self.assertEqual(terminals["a"], ("a",) if sign <= 0 else ("b",))
            self.assertEqual(terminals["b"], ("b",) if sign >= 0 else ("a",))
        self.measurements["strict_predicates"] = {
            "thresholds": 4,
            "each_equality_and_both_sides": True,
            "tie_and_both_sides": True,
            "empty_row_in_minimum": True,
            "all_reachable_unqualified_terminals": True,
        }

    def test_tiny_geometry_is_resolved_against_native_budget(self):
        from aos_native_spark_oracle import upper

        state = self.good.before
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            r = Reference(state.graph.to_payload())
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            value = r.selected(C, W)
            base = r.read(C, W, r.I)
            effect = Q(separation(value["selected"]["current"], base["current"]))
            geometry = Q(separation(value["H"], r.I))
            self.assertGreater(effect, 2 * Q(1, 2**192))
            self.assertGreater(geometry, Q(1, 2**224))
            no_feedback = base["baseline"]
            unit_history = r.read(C, arb_mat([[1]] * r.m), r.I)["baseline"]
            separation(no_feedback, unit_history)
            self.assertLess(upper(value["flat"]), Q(1, 32))
        self.measurements["resolved_geometry"] = {
            "current_effect_lower": str(effect),
            "current_midpoint_budget": str(Q(1, 2**192)),
            "geometry_effect_lower": str(geometry),
            "readback_off_not_history_off": True,
        }
