"""Bounded full-history PC pressure; synthetic windows never claim an endpoint."""

import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import test_cos_native_spark_pressure as common
from cpc_native_spark_oracle import CPCReference
from cpc_native_spark_pressure_oracle import (
    Equations,
    audit_event,
    audit_step,
    contains_ball,
    intervals,
    matrix,
    norm2,
    pack,
    vector,
)
from p991a6_cpc_preflight import transition
from p991a6_cpc_subjects import profile, request

from pygrc.models import grc_9_v4_spark_carrier_event as event_owner
from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_cpc as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import (
    _ARB_CONTEXT_LOCK,
    CertificationInconclusive,
)
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_carrier import (
    ExactCarrierState,
    carrier_pairs,
    exact_state,
)
from pygrc.models.grc_v4_spark_state import ExactResources, flint_operation
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_cpc as fixtures


def with_Z(state, Z):
    return replace(state, Z_4=tuple(tuple(row) for row in pack(Z)))


def mixed(state, scale=None):
    scale = Q(1, 2**16) if scale is None else scale
    eq = Equations(state.graph.to_payload())
    Z = M(eq.I.nrows(), eq.I.ncols())
    for k, (i, j) in enumerate(eq.pairs):
        Z[i, j] = Z[j, i] = (-1 if k % 3 else 1) * scale
    return with_Z(state, Z)


def observed(model):
    initial = model.configuration
    frozen = exact_state(deepcopy(initial.current.to_payload()))
    root = model._operation._spark_scope.published
    stages = []
    steps = []
    read, write, advance, step = (
        native.SparkCPCKernel._admitted_read,
        native.SparkCPCKernel._writer,
        ExactCarrierState.advance_carrier,
        native.SparkCPCKernel.step,
    )

    def check():
        if (
            model.configuration != initial
            or model._operation._spark_scope.published is not root
        ):
            raise AssertionError("partial physical publication")

    def read_spy(k, state):
        check()
        result = read(k, state)
        stages.append(
            {
                "stage": "read",
                "input": state.to_payload(),
                "read": k.read_payload(result).to_dict(),
            }
        )
        return result

    def writer_spy(k, state, value):
        check()
        saved = k.read_payload(value).to_dict()
        result = write(k, state, value)
        stages.append(
            {
                "stage": "writer",
                "input": state.to_payload(),
                "held": saved,
                "writer": result[1].to_dict(),
            }
        )
        return result

    def advance_spy(state, *args):
        check()
        result = advance(state, *args)
        stages.append(
            {
                "stage": "write",
                "input": state.to_payload(),
                "output": result.to_payload(),
            }
        )
        return result

    def step_spy(k, *args):
        result = step(k, *args)
        steps.append(result)
        return result

    with (
        patch.object(native.SparkCPCKernel, "_admitted_read", read_spy),
        patch.object(native.SparkCPCKernel, "_writer", writer_spy),
        patch.object(ExactCarrierState, "advance_carrier", advance_spy),
        patch.object(native.SparkCPCKernel, "step", step_spy),
    ):
        result = model.step()
    if not result.committed:
        raise AssertionError(result.reason)
    if len(steps) != 1 or [r["stage"] for r in stages] != [
        "read",
        "writer",
        "write",
        "read",
        "read",
    ]:
        raise AssertionError("one writer/write and three staged reads")
    if steps[0].before != frozen:
        raise AssertionError("mutated incoming copy")
    return steps[0], stages


class CPCNativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.NativeCPCTests.setUpClass()
        cls.fixture = fixtures.NativeCPCTests()
        cls.event = cls.fixture.event_model
        cls.config = cls.event.configuration
        cls.cert = cls.fixture.certificates[0]
        cls.good = owner.kernel(cls.config).step(cls.config.current)
        cls.measurements = {}
        cls.evidence = {}

    assert_classification = common.COSNativePressureTests.assert_classification
    test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries = common.COSNativePressureTests.test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries
    test_atomic_failures_at_preparation_window_and_publication = common.COSNativePressureTests.test_atomic_failures_at_preparation_window_and_publication
    test_checkpoints_at_each_window_boundary_and_observer_noninterference = common.COSNativePressureTests.test_checkpoints_at_each_window_boundary_and_observer_noninterference
    test_inside_domain_without_event_cannot_earn_gain = (
        common.COSNativePressureTests.test_inside_domain_without_event_cannot_earn_gain
    )
    test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds = common.COSNativePressureTests.test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds

    def test_actual_source_beat_preserves_distinct_reset_history(self):
        config = self.fixture.config
        m = len(config.current.Z_4)
        for role, q in (("current", Q(1, 2**16)), ("reset", -Q(1, 2**17))):
            expected = M([[q if i == j else 0 for j in range(m)] for i in range(m)])
            self.assertEqual(matrix(getattr(config, role).Z_4), expected)
        model = GRC9V4(config)
        step, stages = observed(model)
        self.assertEqual(model.configuration.reset, config.reset)
        self.assertEqual(
            model.configuration.current, self.fixture.source_model.configuration.current
        )
        audit = audit_step(config, config.current, step)
        self.evidence["source_step"] = {
            "subject": config.to_payload(),
            "step": transition(step),
            "stages": stages,
            "role": "current",
            "audit": audit,
        }
        self.measurements["actual_source_steps"] = 1

    def test_native_step_without_research_import_or_trajectory_read(self):
        import json
        import os
        import subprocess

        code = r"""
import builtins,json,sys
original=builtins.__import__
def admitted(name,*args,**kwargs):
    if any(x in name for x in ('spark_completion_', 'oracle', 'research')) or any(x.startswith('test_') for x in name.split('.')):
        raise AssertionError('forbidden verification dependency: '+name)
    return original(name,*args,**kwargs)
builtins.__import__=admitted
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
model=GRC9V4(GRC9V4SparkConfiguration.from_payload(json.loads(sys.stdin.read())))
assert model.step().committed
assert any(x!='0' for row in model.configuration.current.Z_4 for x in row)
print('native C/Z advance without verifier imports')
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            input=json.dumps(self.config.to_payload()),
            text=True,
            capture_output=True,
            cwd=ROOT,
            env=dict(os.environ, PYTHONPATH=str(ROOT / "src")),
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_actual_stages_frozen_inputs_and_complete_joint_error(self):
        records = []
        for index, role in enumerate(("current", "reset")):
            model = self.event.duplicate()
            self.assertTrue(
                model.install_completion_certificates(
                    *self.fixture.certificates
                ).committed
            )
            if role == "reset":
                self.assertTrue(model.reset().committed)
            for beat in range(2):
                config = model.configuration
                step, stages = observed(model)
                self.assertEqual(stages[0]["input"], config.current.to_payload())
                self.assertEqual(stages[1]["held"], stages[0]["read"])
                self.assertEqual(stages[3]["input"], step.after.to_payload())
                self.assertEqual(stages[4]["input"]["C"], list(step.after.C))
                self.assertEqual(
                    stages[4]["input"]["Z_4"], [list(r) for r in step.before.Z_4]
                )
                self.assertEqual(model.configuration.reset, config.reset)
                self.assertEqual(Q(model.configuration.time) - Q(config.time), 32)
                audit = audit_step(
                    config, config.current, step, self.fixture.certificates[index], role
                )
                records.append(
                    {
                        "subject": config.to_payload(),
                        "step": transition(step),
                        "stages": stages,
                        "role": role,
                        "beat": beat + 1,
                        "certificate": self.fixture.certificates[index].to_payload(),
                        "audit": audit,
                    }
                )
        self.evidence["actual_steps"] = records
        self.measurements["actual_target_steps"] = len(records)

    def test_uniform_signed_history_releases_without_resource_motion(self):
        state = self.fixture.config.current
        state = replace(state, C=("1",) * len(state.C), charge=str(len(state.C)))
        state = mixed(state)
        k = owner.kernel(self.fixture.config)
        start = matrix(state.Z_4)
        rows = []
        for n in range(1, 5):
            before = state
            step = k.step(state)
            state = step.after
            self.assertEqual(state.C, before.C)
            self.assertNotEqual(state.Z_4, before.Z_4)
            self.assertTrue(any(Q(x) for row in state.Z_4 for x in row))
            with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                eq = Equations(state.graph.to_payload())
                read = eq.read(vector(before.C), matrix(before.Z_4))
                self.assertEqual(read["J"], M(eq.I.nrows(), 1))
                self.assertEqual(read["S"], M(eq.I.nrows(), eq.I.ncols()))
                audit = audit_step(
                    replace(self.fixture.config, current=before, reset=before),
                    before,
                    step,
                )
                error = arb_mat(matrix(state.Z_4)) - (-arb(n)).exp() * arb_mat(start)
                # Accumulated coordinate rounding, with every attenuation <=1.
                self.assertLessEqual(
                    max(abs(x).upper().fmpq() for x in error.entries()),
                    n * (Q(1, 2**193) + Q(1, 2**224)),
                )
            rows.append(audit)
        self.measurements["uniform_release"] = {
            "charge": state.charge,
            "steps": 4,
            "nonzero_history": True,
            "audits": rows,
        }

    def test_zero_formation_next_consumption_and_signed_source(self):
        k = owner.kernel(self.config)
        first = self.good
        second = k.step(first.after)
        self.assertTrue(any(Q(x) for row in first.after.Z_4 for x in row))
        neutral = ExactCarrierState.zero(
            ExactResources(first.after.graph, first.after.C, first.after.charge)
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(first.before.graph.to_payload())
            formed = eq.audit_read(first.before, first.consumed_read)
            actual = eq.audit_read(first.after, second.consumed_read)
            control = eq.read(vector(neutral.C), matrix(neutral.Z_4))
            difference = max(abs(x) for x in (actual["J"] - control["J"]).entries())
            self.assertGreater(difference, Q(1, 2**192))
            negative = [(i, j) for i, j in eq.pairs if formed["S"][i, j] < 0]
            self.assertTrue(negative, "fixture must resolve a negative source entry")
        self.assertNotEqual(
            second.consumed_read["subject_digest"],
            k.step(neutral).consumed_read["subject_digest"],
        )
        self.measurements["formation_consumer"] = {
            "next_current_difference": str(difference),
            "negative_source_entries": len(negative),
        }

    def test_equal_C_equal_norm_trace_different_patterns_and_roles(self):
        k = owner.kernel(self.config)
        base = self.good.after
        eq = Equations(base.graph.to_payload())
        pairs = [p for p in eq.pairs if p[0] != p[1]]
        states = []
        for p in pairs[:2]:
            Z = M(eq.I.nrows(), eq.I.ncols())
            i, j = p
            Z[i, j] = Z[j, i] = Q(1, 2**16)
            states.append(with_Z(base, Z))
        a, b = states
        self.assertEqual(norm2(matrix(a.Z_4)), norm2(matrix(b.Z_4)))
        self.assertEqual(sum(matrix(a.Z_4)[i, i] for i in range(eq.I.nrows())), 0)
        sa, sb = k.step(a), k.step(b)
        self.assertNotEqual(sa.consumed_read, sb.consumed_read)
        self.assertEqual(
            classify(a, self.config.policy), classify(b, self.config.policy)
        )
        self.assertNotEqual(a.to_canonical_bytes(), b.to_canonical_bytes())
        for s in (sa, sb):
            audit_step(
                replace(self.config, current=s.before, reset=s.before), s.before, s
            )
        wrong = replace(sa, consumed_read=sb.consumed_read)
        self.detect(
            "swap_equal_C_carriers",
            "whole C/Z read identity",
            lambda: audit_step(replace(self.config, current=a, reset=b), a, wrong),
        )
        model = GRC9V4(replace(self.config, current=a, reset=b))
        snapshot = model.snapshot()
        self.assertTrue(model.reset().committed)
        self.assertEqual(model.configuration.current, b)
        restored = GRC9V4.from_state(snapshot)
        self.assertEqual(restored.configuration.current, a)
        self.assertEqual(restored.configuration.reset, b)
        self.measurements["equal_C_roles"] = {
            "equal_C": True,
            "different_Z": True,
            "equal_norm": True,
            "equal_trace": True,
            "distinct_reads": True,
        }

    def detect(self, label, assertion, operation):
        with self.assertRaisesRegex(AssertionError, assertion):
            operation()
        self.measurements.setdefault("mutations", []).append(
            {"mutation": label, "assertion": assertion}
        )

    def test_read_mutations_have_specific_constitutive_discriminators(self):
        base = mixed(self.good.after)
        config = replace(self.config, current=base)
        step = owner.kernel(config).step(base)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(base.graph.to_payload())
            C = vector(base.C)
            Z = matrix(base.Z_4)
            exact = eq.read(C, Z)
            from cos_native_spark_oracle import nullspace

            cycle = nullspace(eq.B)[0]
            self.assertEqual(eq.B * cycle, M(C.nrows(), 1))
            negatives = -exact["flat"]
            self.assertEqual(
                M(
                    [
                        [
                            eq.O[i, j] * negatives[i, 0] * negatives[j, 0] / 4
                            for j in range(eq.I.nrows())
                        ]
                        for i in range(eq.I.nrows())
                    ]
                ),
                exact["S"],
            )
            variants = [
                ("ignore_old_Z", "H", eq.I),
                ("same_step_source_in_H", "H", exact["H"] + exact["S"] / 2),
                ("cycle_current", "J", exact["J"] + cycle / Q(2**20)),
                ("negate_flat", "flat", -exact["flat"]),
                (
                    "clip_negative_source",
                    "S",
                    M([[max(0, x) for x in row] for row in pack_numbers(exact["S"])]),
                ),
            ]
            for label, key, value in variants:
                p = step.consumed_read.to_dict()
                p[key] = intervals(arb_mat(value))
                bad = replace(step, consumed_read=FrozenJSONMap(p))
                self.detect(
                    label,
                    "exact old-carrier read: " + key,
                    lambda bad=bad: audit_step(config, base, bad),
                )
            p = step.consumed_read.to_dict()
            p["current_midpoint"][0] = str(Q(p["current_midpoint"][0]) + Q(1, 2**160))
            self.detect(
                "unbounded_current_midpoint",
                "whole current midpoint budget",
                lambda: audit_step(
                    config, base, replace(step, consumed_read=FrozenJSONMap(p))
                ),
            )

            p = step.consumed_read.to_dict()
            p["conditioning_upper"] = "1"
            self.detect(
                "understated_conditioning",
                "independent conditioning bound",
                lambda: audit_step(
                    config, base, replace(step, consumed_read=FrozenJSONMap(p))
                ),
            )
            self.detect(
                "omit_carrier_error",
                "carrier numerical budget",
                lambda: audit_step(
                    config, base, replace(step, carrier_component_error="0")
                ),
            )

    def test_held_source_and_writer_mutations(self):
        base = mixed(self.good.after)
        config = replace(self.config, current=base)
        step = owner.kernel(config).step(base)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(base.graph.to_payload())
            old = eq.read(vector(base.C), matrix(base.Z_4))
            for label, C, Z in [
                ("post_C_old_Z", step.after.C, base.Z_4),
                ("post_C_new_Z", step.after.C, step.after.Z_4),
            ]:
                other = eq.read(vector(C), matrix(Z))["S"]
                self.assertNotEqual(old["S"], other)
                w = step.writer.to_dict()
                w["source"] = intervals(arb_mat(other))
                self.detect(
                    label,
                    "same incoming held source",
                    lambda w=w: audit_step(
                        config, base, replace(step, writer=FrozenJSONMap(w))
                    ),
                )
            Z = matrix(base.Z_4)
            S = old["S"]
            a = (-arb(1)).exp()
            ideal = a * arb_mat(Z) + (1 - a) * arb_mat(S)
            for label, wrong in [
                ("freeze", arb_mat(Z)),
                ("clear", arb_mat(M(Z.nrows(), Z.ncols()))),
                ("additive", arb_mat(Z + S)),
                ("double_write", a * ideal + (1 - a) * arb_mat(S)),
                (
                    "tau_C_instead_of_PC",
                    (-arb(32)).exp() * arb_mat(Z) + (1 - (-arb(32)).exp()) * arb_mat(S),
                ),
                (
                    "clip_signed_history",
                    a
                    * arb_mat(M([[max(0, x) for x in row] for row in pack_numbers(Z)]))
                    + (1 - a) * arb_mat(S),
                ),
            ]:
                w = step.writer.to_dict()
                w["ideal"] = intervals(wrong)
                self.detect(
                    label,
                    "complete exponential writer",
                    lambda w=w: audit_step(
                        config, base, replace(step, writer=FrozenJSONMap(w))
                    ),
                )
            w = step.writer.to_dict()
            w["decay"] = ["0", "0"]
            self.detect(
                "wrong_decay",
                "tau_PC exponential coefficient",
                lambda: audit_step(
                    config, base, replace(step, writer=FrozenJSONMap(w))
                ),
            )

    @flint_operation
    def test_writer_primitive_held_source_semigroup_and_cancellation(self):
        state = mixed(self.good.after)
        k = owner.kernel(self.config)
        Z = matrix(state.Z_4)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            a = (-arb(1)).exp()
            cases = [
                ("zero_source", arb_mat(M(Z.nrows(), Z.ncols()))),
                ("stationary_held", arb_mat(Z)),
                ("mixed", arb_mat(-Z / 2)),
                ("cancelling", -a / (1 - a) * arb_mat(Z)),
            ]
            bounds = []
            for name, S in cases:
                with ctx.workprec(256):
                    result, writer = k._writer(
                        state,
                        {
                            "subject_digest": sha256(
                                state.to_canonical_bytes()
                            ).hexdigest(),
                            "S": S,
                        },
                    )
                expected = a * arb_mat(Z) + (1 - a) * S
                actual = arb_mat(matrix(result))
                self.assertLessEqual(
                    max(abs(x).upper().fmpq() for x in (actual - expected).entries()),
                    Q(1, 2**193) + Q(1, 2**224),
                )
                self.assertTrue(contains_ball(writer["ideal"], expected))
                bounds.append(name)
            # Same held source in two fixed-duration primitive calls; not two full beats.
            S = arb_mat(-Z / 2)
            current = state
            for _ in range(2):
                with ctx.workprec(256):
                    result, _ = k._writer(
                        current,
                        {
                            "subject_digest": sha256(
                                current.to_canonical_bytes()
                            ).hexdigest(),
                            "S": S,
                        },
                    )
                current = replace(current, Z_4=result)
            expected = (-arb(2)).exp() * arb_mat(Z) + (1 - (-arb(2)).exp()) * S
            self.assertLessEqual(
                max(
                    abs(x).upper().fmpq()
                    for x in (arb_mat(matrix(current.Z_4)) - expected).entries()
                ),
                2 * (Q(1, 2**193) + Q(1, 2**224)),
            )
        for duration in ("0", "-1", "1/1000000000", "64"):
            with self.assertRaises(ValueError):
                k.step(state, duration)
        for tau in (1, 0, -1, 64):
            with self.assertRaises((ValueError, RuntimeError)):
                native.SparkCPCKernel(
                    state.graph, profile(state.graph, realization={"tau_PC": tau})
                )
        self.measurements["writer_primitive"] = {
            "cases": bounds,
            "held_source_two_beat_semigroup": True,
            "variable_duration_support": False,
        }

    def test_every_source_target_signed_direction_and_simultaneous_history(self):
        result = {}
        for label, config, count in [
            ("source", self.fixture.config, 58),
            ("target", self.config, 46),
        ]:
            state = config.current
            k = owner.kernel(config)
            eq = Equations(state.graph.to_payload())
            self.assertEqual(len(eq.pairs), count)
            self.assertEqual(tuple(carrier_pairs(state.graph)), eq.pairs)
            for i, j in eq.pairs:
                for sign in (-1, 1):
                    Z = M(eq.I.nrows(), eq.I.ncols())
                    Z[i, j] = Z[j, i] = sign * Q(1, 2**16)
                    s = with_Z(state, Z)
                    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                        eq.audit_read(s, k.readmission(s))
            s = mixed(state)
            audit_step(replace(config, current=s), s, k.step(s))
            result[label] = {
                "edges": eq.I.nrows(),
                "off_diagonal": count - eq.I.nrows(),
                "coordinates": count,
                "signed_probes": 2 * count,
                "simultaneous_signed": True,
            }
        self.measurements["carrier_spaces"] = result

    def test_exact_norm_boundaries_and_packed_offdiagonal_discriminator(self):
        state = self.good.after
        eq = Equations(state.graph.to_payload())
        k = owner.kernel(self.config)
        R = Q(1, 64)
        for q in (R * (1 - Q(1, 2**32)), R, -R):
            Z = M(eq.I.nrows(), eq.I.ncols())
            Z[0, 0] = q
            s = with_Z(state, Z)
            k.readmission(s)
        Z[0, 0] = R * (1 + Q(1, 2**32))
        with self.assertRaisesRegex(ValueError, "Frobenius"):
            with_Z(state, Z)
        i, j = next(p for p in eq.pairs if p[0] != p[1])
        Z = M(eq.I.nrows(), eq.I.ncols())
        Z[i, j] = Z[j, i] = 3 * R / 4
        self.assertLess((3 * R / 4) ** 2, R**2)
        self.assertGreater(norm2(Z), R**2)
        with self.assertRaisesRegex(ValueError, "Frobenius"):
            with_Z(state, Z)
        self.measurements["packed_norm"] = {
            "upper_triangle_only_squared": str((3 * R / 4) ** 2),
            "full_squared": str(norm2(Z)),
            "radius_squared": str(R * R),
            "rejected": True,
        }

    def test_invalid_carrier_payloads_and_wrong_graph_binding(self):
        good = mixed(self.good.after)
        eq = Equations(good.graph.to_payload())
        payload = good.to_payload()
        i, j = next(
            (i, j)
            for i in range(eq.I.nrows())
            for j in range(i + 1, eq.I.nrows())
            if not eq.O[i, j]
        )
        changes = [
            lambda x: x.pop("Z_4"),
            lambda x: x["Z_4"].pop(),
            lambda x: x["Z_4"][0].pop(),
            lambda x: x["Z_4"][0].__setitem__(1, "1/64"),
            lambda x: x["Z_4"][i].__setitem__(j, "1/1024"),
            lambda x: x["Z_4"][0].__setitem__(0, "nan"),
            lambda x: x["Z_4"][0].__setitem__(0, "inf"),
            lambda x: x.update(Z_4=[{"i": 0, "j": 0, "value": "0"}] * eq.I.nrows()),
        ]
        for change in changes:
            bad = deepcopy(payload)
            change(bad)
            with self.assertRaises((ValueError, TypeError, KeyError)):
                exact_state(bad)
        graph = good.graph.to_payload()
        graph["edges"][0]["tail"], graph["edges"][0]["head"] = (
            graph["edges"][0]["head"],
            graph["edges"][0]["tail"],
        )
        other = GRCV4Graph.from_payload(graph)
        with self.assertRaisesRegex(ValueError, "subject"):
            owner.kernel(self.config).step(replace(good, graph=other))
        with self.assertRaises(ValueError):
            self.cert.membership(ExactResources(good.graph, good.C, good.charge))

    def test_joint_trap_boundary_all_coordinates_and_relabelled_proofs(self):
        center = self.fixture.center
        eq = Equations(center.graph.to_payload())
        r = Q(self.cert.operands["carrier_radius"])
        for i, j in eq.pairs:
            for sign in (-1, 1):
                Z = M(eq.I.nrows(), eq.I.ncols())
                Z[i, j] = Z[j, i] = sign * r * (1 if i == j else Q(1, 2))
                state = with_Z(center, Z)
                expected = norm2(Z) / r**2
                self.assertEqual(self.cert.membership(state), (True, str(expected)))
        Z = M(eq.I.nrows(), eq.I.ncols())
        Z[0, 0] = r
        self.assertEqual(self.cert.membership(with_Z(center, Z)), (True, "1"))
        Z[0, 0] = r * (1 + Q(1, 2**32))
        outside = with_Z(center, Z)
        owner.kernel(self.config).readmission(outside)
        self.assertFalse(self.cert.membership(outside)[0])
        i, j = next(p for p in eq.pairs if p[0] != p[1])
        Z = M(eq.I.nrows(), eq.I.ncols())
        Z[i, j] = Z[j, i] = 3 * r / 4
        self.assertFalse(self.cert.membership(with_Z(center, Z))[0])
        simultaneous = mixed(center, r / 16)
        self.assertEqual(
            self.cert.membership(simultaneous),
            (True, str(norm2(matrix(simultaneous.Z_4)) / r**2)),
        )
        for mutation in (
            lambda x: x["operands"]["carrier_pairs"].pop(),
            lambda x: x["operands"].pop("carrier_center"),
            lambda x: x["operands"]["binding"].update(state_channels=["C"]),
            lambda x: x["operands"].update(
                schema_version="grc9v4-native-trap-operands-v1"
            ),
            lambda x: x["operands"]["binding"]["profile"]["identity_payload"].update(
                profile_family_id="C_CI_PC"
            ),
        ):
            data = deepcopy(self.cert.to_payload())
            mutation(data)
            with self.assertRaises((ValueError, TypeError, KeyError, RuntimeError)):
                CompletionCertificate.from_payload(data)
        from tests.models import test_grc_v4_spark_cci as ci

        ci.NativeCCITests.setUpClass()
        wrong = ci.NativeCCITests.certificates[0].to_payload()
        wrong["operands"]["binding"] = self.cert.operands["binding"].to_dict()
        with self.assertRaises((ValueError, RuntimeError)):
            CompletionCertificate.from_payload(wrong)
        self.measurements["joint_membership"] = {
            "directions": 46,
            "both_signs": True,
            "ordinary_admitted_outside_trap": True,
            "off_diagonal_factor_two": True,
        }

    def test_full_60_direction_finite_segments_and_cross_couplings(self):
        state = mixed(self.good.after, Q(1, 2**24))
        k = owner.kernel(self.config)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            ref = CPCReference(state.graph.to_payload())
            C = arb_mat(vector(state.C))
            Z = arb_mat(matrix(state.Z_4))
            S = arb_mat(matrix(self.cert.operands["S"]))
            eps = Q(1, 2**30)
            results = []
            for axis in range(60):
                dC = arb_mat(C.nrows(), 1)
                dZ = arb_mat(Z.nrows(), Z.ncols())
                if axis < 14:
                    for i in range(C.nrows()):
                        dC[i, 0] = S[i, axis]
                else:
                    i, j = ref.pairs[axis - 14]
                    dZ[i, j] = dZ[j, i] = arb(1) if i == j else 1 / arb(2).sqrt()

                def box(A, d):
                    return arb_mat(
                        [
                            [
                                arb(
                                    A[i, j].mid().fmpq(),
                                    (abs(d[i, j]) * eps).upper().fmpq(),
                                )
                                for j in range(A.ncols())
                            ]
                            for i in range(A.nrows())
                        ]
                    )

                with ctx.workprec(256):
                    p = k.partials(box(C, dC), box(Z, dZ))
                a = ref.pc_step(C - eps * dC, Z - eps * dZ)
                b = ref.pc_step(C + eps * dC, Z + eps * dZ)
                csec = (b["after"] - a["after"]) / (2 * eps)
                zsec = (b["carrier_after"] - a["carrier_after"]) / (2 * eps)
                basis = arb_mat([[0] for _ in ref.pairs])
                if axis >= 14:
                    basis[axis - 14, 0] = 1
                dc = p["CC"] * dC + p["CZ"] * basis
                dz = (1 - ref.decay) * (
                    p["SC"] * dC + p["SZ"] * basis
                ) + ref.decay * basis
                packed = arb_mat(
                    [
                        [(1 if i == j else arb(2).sqrt()) * zsec[i, j]]
                        for i, j in ref.pairs
                    ]
                )
                self.assertTrue(
                    all(
                        x.contains(y)
                        for x, y in zip(dc.entries(), csec.entries(), strict=True)
                    ),
                    ("C", axis),
                )
                self.assertTrue(
                    all(
                        x.contains(y)
                        for x, y in zip(dz.entries(), packed.entries(), strict=True)
                    ),
                    ("Z", axis),
                )
                results.append(
                    {
                        "axis": axis,
                        "kind": "charge" if axis < 14 else "carrier",
                        "contains_secant": True,
                    }
                )
            for name in ("CZ", "SC", "SZ"):
                self.assertTrue(any(not x.contains(0) for x in p[name].entries()), name)
        self.measurements["finite_segments"] = results

    def test_signed_edge_permutation_covariance_and_untransported_binding(self):
        state = mixed(self.good.after)
        graph = state.graph.to_payload()
        m = len(graph["edges"])
        perm = list(reversed(range(m)))
        sign = [-1 if i % 3 == 0 else 1 for i in range(m)]
        graph["edges"] = [deepcopy(graph["edges"][i]) for i in perm]
        for i, e in enumerate(graph["edges"]):
            if sign[i] < 0:
                e["tail"], e["head"] = e["head"], e["tail"]
        target = GRCV4Graph.from_payload(graph)
        Qm = M([[sign[i] if j == perm[i] else 0 for j in range(m)] for i in range(m)])
        transformed = ExactCarrierState(
            target,
            state.C,
            state.charge,
            tuple(tuple(r) for r in pack(Qm * matrix(state.Z_4) * Qm.transpose())),
        )
        first = owner.kernel(self.config).step(state)
        second = native.SparkCPCKernel(target, profile(target)).step(transformed)
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(state.graph.to_payload())
            other = Equations(target.to_payload())
            self.assertEqual(other.B, eq.B * Qm.transpose())
            a = eq.audit_read(state, first.consumed_read)
            b = other.audit_read(transformed, second.consumed_read)
            for key in ("J", "flat"):
                self.assertEqual(b[key], Qm * a[key])
            for key in ("H", "S"):
                self.assertEqual(b[key], Qm * a[key] * Qm.transpose())
        self.assertEqual(first.after.C, second.after.C)
        self.assertEqual(
            matrix(second.after.Z_4), Qm * matrix(first.after.Z_4) * Qm.transpose()
        )
        with self.assertRaises(ValueError):
            owner.kernel(self.config).step(transformed)
        self.measurements["covariance"] = {
            "permutation": perm,
            "signs": sign,
            "off_diagonal_history": True,
            "exact_represented_transport": True,
        }

    def test_event_whole_actual_archive_changed_support_and_regeneration(self):
        records = []
        for chirality in (-1, 1):
            source = self.fixture.source_model.duplicate()
            before = source.configuration
            self.assertNotEqual(before.current.Z_4, self.fixture.config.current.Z_4)
            self.assertEqual(before.reset, self.fixture.config.reset)
            self.assertTrue(source.expand(request(source, chirality)).committed)
            event = source._operation._published.completion.event.to_dict()
            audit = audit_event(before, source.configuration, event)
            sg = before.reference.graph
            tg = source.configuration.reference.graph
            old = Equations(sg.to_payload())
            new = Equations(tg.to_payload())
            ids = sg.live_edge_ids
            newids = tg.live_edge_ids
            lost = [
                (i, j)
                for i, j in old.pairs
                if i != j
                and ids[i] in newids
                and ids[j] in newids
                and not new.O[newids.index(ids[i]), newids.index(ids[j])]
            ]
            self.assertTrue(lost)
            active = [(i, j) for i, j in lost if Q(before.current.Z_4[i][j])]
            self.assertTrue(
                active, "actual source history must occupy a lost support pair"
            )
            pair = tuple(
                next(
                    i
                    for i, e in enumerate(sg.oriented_edges)
                    if {e.tail_node_id, e.head_node_id} == {"v", n}
                )
                for n in ("n1", "n2")
            )
            self.assertIn(tuple(sorted(pair)), lost)
            self.assertNotEqual(Q(before.current.Z_4[pair[0]][pair[1]]), 0)
            self.assertEqual(
                new.O[newids.index(ids[pair[0]]), newids.index(ids[pair[1]])], 0
            )
            records.append(
                {
                    "source": before.to_payload(),
                    "target": source.configuration.to_payload(),
                    "event": event,
                    "audit": audit,
                    "lost_pairs": [list(x) for x in lost],
                }
            )
            formed = owner.kernel(source.configuration).step(
                source.configuration.current
            )
            self.assertTrue(any(Q(x) for row in formed.after.Z_4 for x in row))
            audit_step(source.configuration, formed.before, formed)
        self.evidence["events"] = records
        self.measurements["event_history"] = {
            "chiralities": 2,
            "source_coordinates": 58,
            "target_coordinates": 46,
            "changed_support_pairs": len(records[0]["lost_pairs"]),
            "whole_target_reset": True,
        }

    def test_archive_and_whole_target_mutations(self):
        before = self.fixture.source_model.configuration
        after = self.event.configuration
        event = self.event._operation._published.completion.event.to_dict()
        for label, role, payload in [
            ("prebeat_current", "current", self.fixture.config.current.to_payload()),
            ("role_swap", "current", before.reset.to_payload()),
            (
                "diagonal_only",
                "current",
                replace(
                    before.current,
                    Z_4=tuple(
                        tuple(x if i == j else "0" for j, x in enumerate(row))
                        for i, row in enumerate(before.current.Z_4)
                    ),
                ).to_payload(),
            ),
        ]:
            changed = deepcopy(event)
            changed["carrier_history"]["source_archive"][role] = payload
            self.detect(
                label,
                "whole actual source archive",
                lambda changed=changed: audit_event(before, after, changed),
            )
        changed = replace(after, current=mixed(after.current))
        self.detect(
            "copy_old_history_or_zero_only_new_rows",
            "whole target carrier zero",
            lambda: audit_event(before, changed, event),
        )

    def test_all_PC_transaction_faults_preserve_whole_publication(self):
        cases = [("_admitted_read", 1), ("_writer", 1), ("_admitted_read", 2)]
        for method, index in cases:
            model = self.fixture.synthetic_window_fixture()
            model.step()
            model.step()
            snapshot = model.snapshot()
            root = model._operation._spark_scope.published
            original = getattr(native.SparkCPCKernel, method)
            calls = []

            def fail(k, *args, original=original, calls=calls, index=index):
                calls.append(True)
                value = original(k, *args)
                if len(calls) == index:
                    raise CertificationInconclusive("injected PC stage")
                return value

            with patch.object(native.SparkCPCKernel, method, fail):
                self.assertFalse(model.step().committed)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertIs(model._operation._spark_scope.published, root)
            self.assertEqual(model.step().local_gain, 1)
        for method in ("archive", "capture"):
            model = self.fixture.source_model.duplicate()
            req = request(model)
            snapshot = model.snapshot()
            root = model._operation._spark_scope.published
            with patch.object(
                event_owner, method, side_effect=ValueError("archive preparation")
            ):
                self.assertFalse(model.expand(req).committed)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertIs(model._operation._spark_scope.published, root)
            self.assertTrue(model.expand(req).committed)
        self.measurements["PC_faults"] = {
            "read": True,
            "writer": True,
            "poststate": True,
            "archive": True,
            "complete_snapshot_and_root": True,
            "retry_once": True,
        }

    def test_reset_only_and_target_admission_faults(self):
        for index in (2, 4):
            model = self.fixture.source_model.duplicate()
            snapshot = model.snapshot()
            root = model._operation._spark_scope.published
            req = request(model)
            original = native.SparkCPCKernel.readmission
            calls = []

            def fail(k, state, calls=calls, index=index, original=original):
                calls.append(state)
                if len(calls) == index:
                    raise CertificationInconclusive("injected reset-only read")
                return original(k, state)

            with patch.object(native.SparkCPCKernel, "readmission", fail):
                self.assertFalse(model.expand(req).committed)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertIs(model._operation._spark_scope.published, root)
            self.assertTrue(model.expand(req).committed)
        for operation in ("reset", "rebase_reset_baseline"):
            current = mixed(self.good.after)
            reset = with_Z(current, -matrix(current.Z_4))
            model = GRC9V4(replace(self.config, current=current, reset=reset))
            snapshot = model.snapshot()
            calls = []

            def fail(k, state, calls=calls):
                calls.append(state)
                if len(calls) == 2:
                    raise CertificationInconclusive("reset role")
                return original(k, state)

            with patch.object(native.SparkCPCKernel, "readmission", fail):
                self.assertFalse(getattr(model, operation)().committed)
            self.assertEqual(model.snapshot(), snapshot)
            self.assertTrue(getattr(model, operation)().committed)

    def test_observer_snapshot_aliasing_zero_duration_and_migration(self):
        state = mixed(self.good.after)
        config = replace(
            self.config, current=state, reset=with_Z(state, -matrix(state.Z_4))
        )
        a, b = GRC9V4(config), GRC9V4(config)
        for i in range(2):
            before = a.snapshot()
            Z = deepcopy(state.to_payload())
            for _ in range(3):
                with patch.object(
                    native.SparkCPCKernel,
                    "_writer",
                    side_effect=AssertionError("observation aged history"),
                ):
                    a.compute_observables()
                    snap = a.snapshot()
                GRC9V4.from_state(snap)
            self.assertEqual(a.snapshot(), before)
            Z["Z_4"][0][0] = "0"
            self.assertEqual(a.configuration.current, b.configuration.current)
            self.assertTrue(a.step().committed and b.step().committed)
            self.assertEqual(a.configuration, b.configuration)
        from pygrc.models.grc_v4 import GRCV4StepRequestInput

        for duration in (0, -1, 1):
            snap = a.snapshot()
            result = a.step_v4_input(
                GRCV4StepRequestInput(
                    "grcv4-step-request-input-v1",
                    "wrong-duration",
                    duration,
                    FrozenJSONMap({}),
                )
            )
            self.assertFalse(result.committed)
            self.assertEqual(a.snapshot(), snap)
        migrated = GRC9V4(config)
        self.assertTrue(migrated.migrate_spark_configuration(config).committed)
        self.assertEqual(migrated.configuration.current.Z_4, state.Z_4)
        self.assertEqual(migrated.configuration.reset.Z_4, config.reset.Z_4)

    def test_nonfinite_or_unresolved_reads_and_writers_fail_closed(self):
        for key in ("J", "S"):
            model = self.event.duplicate()
            snap = model.snapshot()
            root = model._operation._spark_scope.published
            original = native.SparkCPCKernel.read_ball

            def broken(k, *args, key=key, original=original):
                result = original(k, *args)
                result[key][0, 0] = arb("nan")
                return result

            with patch.object(native.SparkCPCKernel, "read_ball", broken):
                self.assertFalse(model.step().committed)
            self.assertEqual(model.snapshot(), snap)
            self.assertIs(model._operation._spark_scope.published, root)
        model = self.event.duplicate()
        snap = model.snapshot()
        with patch.object(native, "CURRENT_BITS", 1024):
            self.assertFalse(model.step().committed)
        self.assertEqual(model.snapshot(), snap)
        with patch.object(native, "WRITER_BITS", 1024):
            self.assertFalse(model.step().committed)
        self.assertEqual(model.snapshot(), snap)


def pack_numbers(A):
    return [[A[i, j] for j in range(A.ncols())] for i in range(A.nrows())]


if __name__ == "__main__":
    unittest.main()
