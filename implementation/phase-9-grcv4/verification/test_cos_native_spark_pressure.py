"""Bounded independent pressure; synthetic windows are not a closure campaign."""

import json
import math
import subprocess
import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb_mat, ctx
from flint import fmpq as Q
from flint import fmpq_mat as M

ROOT = Path(__file__).resolve().parents[3]
for directory in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(directory))

from cos_native_spark_oracle import (
    Equations,
    contains,
    infinity,
    matrix,
    nullspace,
    vector,
)
from cos_native_spark_oracle import classify as independent_classify
from p991a2_native_spark_numerics import subjects

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion import classify
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_completion_codec import CompletionPolicy
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_cos import SparkCOSKernel
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_9_v4_spark_completion as fixtures
from tests.models.test_grc_9_v4_spark_completion import configuration, request


def delivery(name):
    return GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", name, 32, FrozenJSONMap({})
    )


def observed_step(model, mutation=None):
    """Read-only stage capture in normal use; explicit mutations in fault tests."""
    reads, steps = [], []
    read, step = SparkCOSKernel._read, SparkCOSKernel.step

    def capture(k, C, H, operators):
        J, f = read(k, C, H, operators)
        if mutation is not None:
            J, f = mutation(len(reads), J, f)
        reads.append((M(C), M(H), M(J), M(f)))
        return J, f

    def retain(k, *args, **kwargs):
        result = step(k, *args, **kwargs)
        steps.append(result)
        return result

    with (
        patch.object(SparkCOSKernel, "_read", capture),
        patch.object(SparkCOSKernel, "step", retain),
    ):
        result = model.step()
    if not result.committed:
        raise AssertionError(result.reason)
    return reads, steps[0]


def toy(values, edges):
    """Literal scientific port inputs, independent of the native classifier."""
    graph = GRCV4Graph.from_payload(
        {
            "schema_version": "grc9v4-port-graph-v1",
            "live_node_ids": sorted(values),
            "edges": [
                {
                    "edge_id": f"e{i}",
                    "kind": "boundary",
                    "tail": {"node_id": a, "port": p},
                    "head": {"node_id": b, "port": q},
                }
                for i, (a, p, b, q) in enumerate(edges)
            ],
        }
    )
    return ExactResources(
        graph,
        tuple(str(values[n]) for n in graph.live_node_ids),
        str(sum(map(Q, values.values()))),
    )


class COSNativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.measurements = {}
        fixtures.NativeSparkCompletionTests.setUpClass()
        cls.fixture = fixtures.NativeSparkCompletionTests()
        cls.event = cls.fixture.event_model
        cls.cert = cls.fixture.certificates[0]

    def assert_classification(self, state, policy=None):
        policy = policy or CompletionPolicy()
        expected = independent_classify(
            state.graph.to_payload(), state.C, policy.to_payload()
        )
        actual = classify(state, policy)
        self.assertEqual(
            (actual.basins, actual.terminals, [r.to_dict() for r in actual.rows]),
            expected,
        )
        return expected

    def test_public_equation_stages_outward_error_and_fresh_restart(self):
        model = self.event.duplicate()
        U = matrix(self.cert.operands["U"])
        bounds = []
        for beat in range(2):
            before = model.configuration.current  # Immutable before producer.
            equations = Equations(before.graph.to_payload())
            with _ARB_CONTEXT_LOCK, ctx.workprec(512):
                expected = Equations(before.graph.to_payload(), outward=True).step(
                    before.C
                )
                reads, step = observed_step(model)
                self.assertEqual(
                    len(reads), 4, "one predictor/corrector plus two poststate reads"
                )
                C, Hp, Jc, fc = reads[1]
                self.assertEqual(reads[0][0], vector(before.C))
                self.assertEqual(C, reads[0][0], "corrector must use incoming C")
                self.assertEqual(reads[0][1], equations.I, "fresh reference predictor")
                for label, actual in (
                    ("predictor_current", reads[0][2]),
                    ("predictor_flat", reads[0][3]),
                    ("H", Hp),
                    ("corrector_current", Jc),
                    ("corrector_flat", fc),
                ):
                    self.assertTrue(contains(expected[label], actual), label)
                self.assertNotEqual(
                    Hp * equations.L, equations.L * Hp, "noncommuting fixture"
                )
                self.assertNotEqual(reads[0][2], Jc, "geometry effect reaches current")
                self.assertTrue(any(Q(c) not in (1, 2, 3) for c in before.C))
                after = vector(model.configuration.current.C)
                for index, H in ((2, Hp), (3, equations.I)):
                    self.assertEqual(reads[index][:2], (after, H))
                    self.assertEqual(reads[index][2:], equations.read(after, H))
                self.assertNotEqual(
                    reads[2][2], reads[3][2], "consumed geometry differs from restart"
                )
                self.assertNotEqual(Jc, reads[3][2])
                defect = Hp - equations.geometry(fc)
                self.assertTrue(contains(expected["split"], defect))
                self.assertEqual(
                    Q(step.split_frobenius_squared),
                    sum(x * x for x in defect.entries()),
                )
                self.assertEqual(
                    after, vector(before.C) - 32 * equations.B * vector(step.flux)
                )
                error = arb_mat(U) * (arb_mat(after) - expected["after"])
                upper = max(abs(x).upper().fmpq() for x in error.entries())
                uniform = 32 * infinity(U * equations.B) / Q(2**129)
                self.assertLessEqual(
                    upper, uniform, "outward full-map error in accepted U norm"
                )
                self.assertEqual(uniform, Q(self.cert.proof["full_step_error"]))
                bounds.append(
                    {
                        "beat": beat + 1,
                        "input": list(before.C),
                        "output": list(step.after.C),
                        "error_upper": str(upper),
                        "uniform_bound": str(uniform),
                    }
                )
                self.assertEqual(sum(map(Q, step.after.C)), 21)
                self.assertEqual(sum(map(Q, model.configuration.reset.C)), 21)
        self.measurements["two_target_steps"] = bounds

    def test_cycle_current_mutation_preserves_state_but_fails_current_oracle(self):
        before = self.event.configuration.current
        oracle = Equations(before.graph.to_payload())
        cycles = nullspace(oracle.B)
        self.assertEqual(len(cycles), 2)
        z = cycles[0]
        self.assertEqual(oracle.B * z, M(15, 1))
        # Even integer flux lattice shift: nearest/even rounding commutes too.
        delta = Q(1, 2**120)
        self.assertTrue(all((delta * x * 2**128).denominator == 1 for x in z.entries()))
        good, bad = self.event.duplicate(), self.event.duplicate()
        good_reads, good_step = observed_step(good)
        bad_reads, bad_step = observed_step(
            bad, lambda i, J, f: (J + delta * z, f) if i == 1 else (J, f)
        )
        self.assertEqual(
            good_step.after, bad_step.after, "resource-only test misses cycle current"
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(512):
            expected = Equations(before.graph.to_payload(), outward=True).step(before.C)
            self.assertTrue(contains(expected["corrector_current"], good_reads[1][2]))
            self.assertFalse(
                contains(expected["corrector_current"], bad_reads[1][2]),
                "corrector.current detects cycle mutation",
            )

    def test_flat_sign_mutation_preserves_geometry_but_fails_flat_oracle(self):
        before = self.event.configuration.current
        good_reads, good = observed_step(self.event.duplicate())
        bad_reads, bad = observed_step(
            self.event.duplicate(), lambda i, J, f: (J, -f) if i == 0 else (J, f)
        )
        self.assertEqual(good.selected_geometry, bad.selected_geometry)
        self.assertEqual(good.after, bad.after)
        self.assertNotEqual(good_reads[0][3], bad_reads[0][3])
        with _ARB_CONTEXT_LOCK, ctx.workprec(512):
            expected = Equations(before.graph.to_payload(), outward=True).step(before.C)
            self.assertFalse(
                contains(expected["predictor_flat"], bad_reads[0][3]),
                "predictor.flat detects sign mutation",
            )

    def test_predictor_current_mutation_and_wrong_fixed_geometry_equations(self):
        before = self.event.configuration.current
        Equations(before.graph.to_payload())
        remembered = []

        def predictor_write(i, J, f):
            if i == 0:
                remembered.append(J)
            return (remembered[0], f) if i == 1 else (J, f)

        reads, changed = observed_step(self.event.duplicate(), predictor_write)
        with _ARB_CONTEXT_LOCK, ctx.workprec(512):
            expected = Equations(before.graph.to_payload(), outward=True).step(before.C)
            self.assertFalse(contains(expected["corrector_current"], reads[1][2]))
            error = arb_mat(matrix(self.cert.operands["U"])) * (
                arb_mat(vector(changed.after.C)) - expected["after"]
            )
            self.assertGreater(
                max(abs(x).lower().fmpq() for x in error.entries()),
                Q(self.cert.proof["full_step_error"]),
            )
            # Synthetic fixed-H equation pressure: not a runtime CI trajectory.
            C, H = expected["C"], expected["H"]
            eq = Equations(before.graph.to_payload(), outward=True)
            site = arb_mat(
                [[(C[i, 0] - 2) ** 3 - (C[i, 0] - 2)] for i in range(C.nrows())]
            )
            frozen_j0 = (
                -eq.B.transpose() * (eq.B * eq.B.transpose() * C / 64 - site) / 1024
            )
            frozen_J = frozen_j0 + (3 * eq.I / 4 + H * eq.L).inv() * frozen_j0 / 4
            swapped_j0 = (
                -eq.B.transpose() * (eq.B * H * eq.B.transpose() * C / 64 - site) / 1024
            )
            swapped_J = swapped_j0 + (3 * eq.I / 4 + eq.L * H).inv() * swapped_j0 / 4
            extra_J, _ = eq.read(C, eq.geometry(expected["corrector_flat"]))
            for label, bad in (
                ("frozen potential", frozen_J),
                ("reversed H L", swapped_J),
                ("extra corrector", extra_J),
            ):
                self.assertTrue(
                    any(
                        not (a - b).contains(0)
                        for a, b in zip(
                            bad.entries(), expected["corrector_current"].entries()
                        )
                    ),
                    label,
                )

    def test_literal_both_chiral_events_and_actual_role_transfer(self):
        _, _, _, domain = subjects()
        pre = configuration()
        model = GRC9V4(pre)
        self.assertEqual(sum(map(Q, pre.current.C)), 21)
        self.assertEqual(sum(map(Q, pre.reset.C)), 21)
        self.assertTrue(model.step().committed)
        source = model.configuration
        self.assertEqual(source.reset, pre.reset)
        self.assertNotEqual(source.current, pre.current)
        basins, _, rows = self.assert_classification(source.current)
        self.assertIn("v", dict(basins)["p"])
        ports = [
            e[end]["port"]
            for e in source.reference.graph.to_payload()["edges"]
            for end in ("head", "tail")
            if e[end]["node_id"] == "v"
        ]
        self.assertEqual(sorted(ports), list(range(1, 10)))
        trigger = next(r for r in rows if r["node_id"] == "v")
        self.assertLess(Q(trigger["gradient_squared"]), 16)
        self.assertLess(Q(trigger["minimum_signed_gradient"]), Q(1, 8))
        for chirality in (-1, 1):
            literal = deepcopy(domain["graphs"][str(chirality)])  # Before producer.
            target = model.duplicate()
            result = target.expand(request(target, chirality))
            self.assertTrue(result.committed, result.reason)
            cp, config = target._operation._published.completion, target.configuration
            namespace = cp.event[
                "event_id"
            ]  # Opaque namespace only, never expected topology.
            expected = json.loads(
                json.dumps(literal).replace("sc2-positive-module", namespace)
            )
            expected["live_node_ids"].sort()
            expected["edges"].sort(key=lambda e: e["edge_id"])
            self.assertEqual(config.reference.graph.to_payload(), expected)
            self.assertEqual(len(expected["live_node_ids"]), 15)
            self.assertEqual(len(expected["edges"]), 16)
            module = [
                namespace + "/core",
                *[namespace + "/satellite/" + str(i) for i in (1, 2, 3)],
            ]
            self.assertEqual(list(cp.event["module"]), module)
            for role in ("current", "reset"):
                incoming = getattr(source, role)
                values = dict(
                    zip(incoming.graph.live_node_ids, map(Q, incoming.C), strict=True)
                )
                cv = values.pop("v")
                values.update(
                    zip(module, (Q(0), cv / 64, cv * 31 / 32, cv / 64), strict=True)
                )
                actual = getattr(config, role)
                self.assertEqual(
                    dict(
                        zip(actual.graph.live_node_ids, map(Q, actual.C), strict=True)
                    ),
                    values,
                )
                self.assertEqual(sum(map(Q, actual.C)), 21)
            self.assertEqual(
                [a for a, _ in self.assert_classification(config.current)[0]], ["p"]
            )
            self.assertEqual(result.local_gain, 0)
            self.assertEqual(target.compute_observables()["completion"]["children"], [])
            weights = config.reference.profile.baseline.params_resolved.candidate.W_C_tr
            self.assertEqual(
                dict(weights), {e["edge_id"]: 1 for e in expected["edges"]}
            )
        self.measurements["literal_chiralities"] = [-1, 1]

    def test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds(
        self,
    ):
        star = [("a", 1, "u", 1), ("a", 4, "v", 1), ("a", 7, "w", 1)]
        unique = toy({"a": 3, "u": 1, "v": 1, "w": 1}, star)
        self.assertEqual(
            self.assert_classification(unique)[0], (("a", ("a", "u", "v", "w")),)
        )
        mixed = toy({"a": 3, "b": 4, "u": 1, "v": 1, "w": 1}, star + [("u", 2, "b", 1)])
        domains, terminals, _ = self.assert_classification(mixed)
        self.assertEqual(dict(terminals)["u"], ("a", "b"))
        self.assertNotIn("u", dict(domains)["a"])
        singleton = toy(
            {"a": 3, "b": 4, "u": 1, "v": 1, "w": 1},
            star + [("u", 2, "b", 1), ("v", 2, "b", 4), ("w", 2, "b", 7)],
        )
        self.assertEqual(self.assert_classification(singleton)[0], ())
        diamond = toy(
            {"a": 4, "l": 2, "r": 2, "u": 1},
            [("u", 1, "l", 1), ("u", 4, "r", 1), ("l", 2, "a", 1), ("r", 2, "a", 4)],
        )
        self.assertEqual(dict(self.assert_classification(diamond)[1])["u"], ("a",))
        tied = toy({"a": 2, "b": 2}, [("a", 1, "b", 1)])
        self.assertEqual(
            self.assert_classification(tied)[1], (("a", ("a",)), ("b", ("b",)))
        )
        self.assertFalse(any(r["seed"] for r in self.assert_classification(tied)[2]))
        equality = toy({"a": 3, "u": 2, "v": 1, "w": 1}, star)
        for changes in (
            {"epsilon_gradient": "3"},
            {"epsilon_Hessian": "1"},
            {"contrast": "1"},
            {"minimum_resource": "3"},
        ):
            _, _, rows = self.assert_classification(
                equality, replace(CompletionPolicy(), **changes)
            )
            self.assertFalse(
                next(r for r in rows if r["node_id"] == "a")["anchor"], changes
            )
        center = self.fixture.center
        domains = dict(self.assert_classification(center)[0])
        satellite = self.event._operation._published.completion.event["module"][2]
        self.assertEqual(set(domains["p"]), {"p", "private"})
        self.assertEqual(set(domains[satellite]), {satellite, "n2", "n8"})

    def test_charge_chart_faces_and_charge_normal_projection_trap(self):
        S, U, c = (
            matrix(self.cert.operands["S"]),
            matrix(self.cert.operands["U"]),
            vector(self.cert.operands["center"]),
        )
        self.assertEqual(
            U * S, M([[int(i == j) for j in range(14)] for i in range(14)])
        )
        self.assertEqual(S.rank(), 14)
        self.assertEqual(M([[1] * 15]) * S, M(1, 14))
        self.assertEqual(sum(c.entries()), 21)
        state = self.fixture.center
        for axis in range(14):
            for sign in (-1, 1):
                for radius, member in (
                    (Q(999, 1000), True),
                    (Q(1), True),
                    (Q(1001, 1000), False),
                ):
                    v = M(14, 1)
                    v[axis, 0] = sign * radius
                    point = c + S * v
                    tested = ExactResources(
                        state.graph, tuple(map(str, point.entries())), "21"
                    )
                    self.assertEqual(
                        self.cert.membership(tested), (member, str(radius))
                    )
        (w,) = nullspace(U)
        self.assertNotEqual(sum(w.entries()), 0)
        delta = Q(1, 2**30) / max(abs(x) for x in w.entries())
        bad = c + delta * w
        self.assertEqual(
            U * (bad - c), M(14, 1), "projection-only membership misses wrong charge"
        )
        wrong_charge = str(sum(bad.entries()))
        with self.assertRaises(ValueError):
            self.cert.membership(
                ExactResources(
                    state.graph, tuple(map(str, bad.entries())), wrong_charge
                )
            )
        with self.assertRaises(ValueError):
            ExactResources(state.graph, tuple(map(str, bad.entries())), "21")

    def test_rehashed_certificate_semantic_corruption(self):
        original = self.cert.to_payload()

        def swap_columns(v):
            for row in v["operands"]["S"]:
                row[0], row[1] = row[1], row[0]

        mutations = {
            "column order": swap_columns,
            "duration": lambda v: v["operands"]["binding"].update(duration="64"),
            "charge": lambda v: v["operands"]["binding"].update(charge="22"),
            "reference": lambda v: v["operands"]["binding"]["reference"].update(
                H_ref="other"
            ),
            "numerical claim": lambda v: v["proof"].update(full_step_error="0"),
            "drop coordinate": lambda v: v["operands"]["U"].pop(),
            "port": lambda v: v["operands"]["binding"]["graph"]["edges"][0][
                "tail"
            ].update(port=9),
        }
        for label, change in mutations.items():
            bad = deepcopy(original)
            change(bad)
            # There is no caller-supplied digest: admission recomputes it AND proof.
            with (
                self.subTest(label=label),
                self.assertRaises((ValueError, ArithmeticError, RuntimeError)),
            ):
                CompletionCertificate.from_payload(bad)

    def test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries(self):
        model = self.fixture.synthetic_window_fixture()
        req = delivery("pressure-distinct-physical-beat")
        self.assertTrue(model.step_v4_input(req).committed)
        for tested in (model, model.duplicate(), GRC9V4.from_state(model.snapshot())):
            root, snap = tested._operation._spark_scope.published, tested.snapshot()
            result = tested.step_v4_input(req)
            self.assertFalse(result.committed)
            self.assertIn("already committed", result.reason)
            self.assertIs(tested._operation._spark_scope.published, root)
            self.assertEqual(tested.snapshot(), snap)
        retry = delivery("pressure-retry")
        with patch.object(
            owner, "progress", side_effect=ValueError("injected window fault")
        ):
            self.assertFalse(model.step_v4_input(retry).committed)
        self.assertTrue(model.step_v4_input(retry).committed)
        self.assertEqual(
            model.compute_observables()["completion"]["window_observations"], 2
        )
        self.assertEqual(
            model.step_v4_input(delivery("third-physical-beat")).local_gain, 1
        )
        self.assertTrue(
            model.install_completion_certificates(*self.fixture.certificates).committed
        )
        self.assertEqual(
            model.step_v4_input(delivery("after-certificate-replacement")).local_gain, 0
        )

    def test_atomic_failures_at_preparation_window_and_publication(self):
        for phase in ("after_numerics", "after_window", "before_publish"):
            model = self.fixture.synthetic_window_fixture()
            self.assertTrue(model.step().committed)
            self.assertTrue(model.step().committed)
            root, snap = model._operation._spark_scope.published, model.snapshot()
            req = delivery("retry-" + phase)
            real = owner.progress

            def fail(*args, phase=phase, real=real):
                if phase == "after_window":
                    real(*args)
                raise ValueError("injected " + phase)

            target, method = (
                (type(model._operation), "_publish")
                if phase == "before_publish"
                else (owner, "progress")
            )
            with patch.object(target, method, side_effect=fail):
                self.assertFalse(model.step_v4_input(req).committed)
            self.assertIs(model._operation._spark_scope.published, root, phase)
            self.assertEqual(model.snapshot(), snap, phase)
            self.assertEqual(model.step_v4_input(req).local_gain, 1, phase)

    def test_reset_only_event_and_certificate_failures_are_atomic(self):
        source = self.fixture.source_model.duplicate()
        root, snap = source._operation._spark_scope.published, source.snapshot()
        readmission, calls = SparkCOSKernel.readmission, []

        def fail_reset(k, state):
            calls.append(state)
            if len(calls) == 2:
                raise ValueError("injected reset-only admission fault")
            return readmission(k, state)

        req = request(source)
        with patch.object(SparkCOSKernel, "readmission", fail_reset):
            self.assertFalse(source.expand(req).committed)
        self.assertEqual(len(calls), 2)
        self.assertIs(source._operation._spark_scope.published, root)
        self.assertEqual(source.snapshot(), snap)
        self.assertTrue(source.expand(req).committed)
        model = self.event.duplicate()
        root, snap = model._operation._spark_scope.published, model.snapshot()
        require = CompletionCertificate.require_binding

        def fail_certificate(cert, kernel, policy, role, charge):
            if role == "reset":
                raise ValueError("injected reset certificate fault")
            return require(cert, kernel, policy, role, charge)

        with patch.object(CompletionCertificate, "require_binding", fail_certificate):
            self.assertFalse(
                model.install_completion_certificates(
                    *self.fixture.certificates
                ).committed
            )
        self.assertIs(model._operation._spark_scope.published, root)
        self.assertEqual(model.snapshot(), snap)
        self.assertTrue(
            model.install_completion_certificates(*self.fixture.certificates).committed
        )

    def test_checkpoints_at_each_window_boundary_and_observer_noninterference(self):
        first, second = (
            self.fixture.synthetic_window_fixture(),
            self.fixture.synthetic_window_fixture(),
        )
        for count in range(4):
            snapshot = first.snapshot()
            restored = GRC9V4.from_state(snapshot)
            self.assertEqual(restored.configuration, first.configuration)
            self.assertEqual(
                restored._operation._published.completion,
                first._operation._published.completion,
            )
            for _ in range(4):
                first.compute_observables()
            self.assertEqual(first.snapshot(), snapshot)
            self.assertEqual(first.configuration, second.configuration)
            if count < 3:
                a, b = (
                    first.step_v4_input(delivery(str(count))),
                    second.step_v4_input(delivery(str(count))),
                )
                self.assertTrue(a.committed and b.committed)
                self.assertEqual((a.local_gain, b.local_gain), (int(count == 2),) * 2)
        self.assertEqual(restored.step().local_gain, 0)

    def test_inside_domain_without_event_cannot_earn_gain(self):
        config = replace(
            self.event.configuration,
            current=self.fixture.center,
            reset=self.fixture.center,
        )
        model = GRC9V4(config)
        self.assertTrue(
            model.install_completion_certificates(*self.fixture.certificates).committed
        )
        for _ in range(3):
            self.assertEqual(model.step().local_gain, 0)
        self.assertEqual(
            model.compute_observables()["completion"]["window_observations"], 0
        )

    def test_generic_spectral_split_boundary_and_frobenius_conservatism(self):
        from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
        from pygrc.models.grc_v4_realizations import OSSplitResidual
        from tests.models.test_grc_v4_realizations import current_fixture, os_fixture

        ref = os_fixture(realization={"tolerance": 0.5}).geometry.reference

        def scalar(h):
            return GRCV4Geometry(ref, OneFormHodge(ref.graph, ((h,),)))

        self.assertTrue(OSSplitResidual(scalar(3), scalar(2)).admitted)
        self.assertFalse(
            OSSplitResidual(scalar(math.nextafter(3, math.inf)), scalar(2)).admitted
        )
        ref = current_fixture(
            weights={"a": 1, "z": 1}, changes={"realization": {"tolerance": 0.5}}
        ).geometry.reference

        def diagonal(h):
            return GRCV4Geometry(ref, OneFormHodge(ref.graph, ((h, 0), (0, h))))

        self.assertTrue(OSSplitResidual(diagonal(1.5), diagonal(1)).admitted)
        self.assertGreater(
            2 * Q(1, 2) ** 2,
            Q(1, 2) ** 2,
            "Frobenius fails although spectral equals tolerance",
        )

    def test_native_execution_without_research_imports_or_trajectory_reads(self):
        code = r"""
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(root/'src'))
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        name = str(args[0])
        if '/investigations/' in name or '/tests/' in name:
            raise RuntimeError('forbidden native dependency: '+name)
sys.addaudithook(audit)
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
data = json.load(sys.stdin)
model = GRC9V4(GRC9V4SparkConfiguration.from_payload(data['configuration']))
assert model.step().committed
assert model.expand(GRC9V4ExpansionRequestInput.from_payload(data['request'])).committed
assert model.step().committed
assert not any('spark_completion_' in n or n.startswith('tests.') for n in sys.modules)
print('native_only_pass')
"""
        data = {
            "configuration": configuration().to_payload(),
            "request": request(self.fixture.source_model).to_payload(),
        }
        result = subprocess.run(
            [sys.executable, "-I", "-c", code, str(ROOT)],
            input=json.dumps(data),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("native_only_pass", result.stdout)


if __name__ == "__main__":
    unittest.main()
