"""Bounded CI pressure: coupled roots, physical map, freshness and atomic owner."""

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from flint import arb, arb_mat, ctx
from flint import fmpq as Q

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
import test_cos_native_spark_pressure as common
from cci_native_spark_oracle import CCIReference, verify_step
from cci_native_spark_pressure_oracle import (
    audit_root,
    audit_step,
    decode,
    domain,
    upper,
)
from cos_native_spark_oracle import Equations, matrix, nullspace, vector
from p991a6_cci_preflight import seal, transition
from p991a6_cci_subjects import configuration, profile

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models import grc_v4_spark_cci as native
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4_certification import (
    _ARB_CONTEXT_LOCK,
    CertificationInconclusive,
)
from pygrc.models.grc_v4_geometry import GRCV4Graph
from pygrc.models.grc_v4_spark_cos import SparkCOSKernel
from pygrc.models.grc_v4_spark_state import ExactResources
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models import test_grc_v4_spark_cci as ci_fixtures
from tests.models.test_grc_9_v4_spark_completion import certificate_pair, request


def observed(model):
    """Read-only spies: no oracle supplies a next state or a root proposal."""
    initial = model.configuration
    published = model._operation._spark_scope.published
    roots = []
    active = []
    steps = []
    writes = []
    root, read, step, advance = (
        native.SparkCCIKernel._root,
        native.SparkCCIKernel._read_ball,
        native.SparkCCIKernel.step,
        ExactResources.advance,
    )

    def root_spy(k, C):
        row = {
            "input": [
                [str(x.lower().fmpq()), str(x.upper().fmpq())] for x in C.entries()
            ],
            "trials": [],
        }
        roots.append(row)
        active.append(row)
        try:
            return root(k, C)
        finally:
            active.pop()

    def read_spy(k, C, H):
        if (
            model.configuration != initial
            or model._operation._spark_scope.published is not published
        ):
            raise AssertionError("algebraic solve published physical progress")
        if active:
            active[-1]["trials"].append([str(x.mid().fmpq()) for x in C.entries()])
        return read(k, C, H)

    def write_spy(state, *args, **kwargs):
        writes.append(state)
        return advance(state, *args, **kwargs)

    def step_spy(k, *args, **kwargs):
        result = step(k, *args, **kwargs)
        steps.append(result)
        return result

    with (
        patch.object(native.SparkCCIKernel, "_root", root_spy),
        patch.object(native.SparkCCIKernel, "_read_ball", read_spy),
        patch.object(native.SparkCCIKernel, "step", step_spy),
        patch.object(ExactResources, "advance", write_spy),
    ):
        result = model.step()
    if not result.committed:
        raise AssertionError(result.reason)
    if len(steps) != 1 or len(writes) != 1 or len(roots) != 2:
        raise AssertionError("root/physical-write counts")
    return steps[0], roots


def shift(pair, delta):
    return [str(Q(x) + delta) for x in pair]


class CCINativePressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.measurements = {}
        cls.evidence = {}
        ci_fixtures.NativeCCITests.setUpClass()
        cls.fixture = ci_fixtures.NativeCCITests()
        cls.event = cls.fixture.event_model
        cls.cert = cls.fixture.certificates[0]
        cls.config = cls.event.configuration
        k = owner.kernel(cls.config)
        cls.good = k.step(cls.config.current)
        cls.reset_step = k.step(cls.config.reset)

    assert_classification = common.COSNativePressureTests.assert_classification
    test_charge_chart_faces_and_charge_normal_projection_trap = common.COSNativePressureTests.test_charge_chart_faces_and_charge_normal_projection_trap
    test_rehashed_certificate_semantic_corruption = (
        common.COSNativePressureTests.test_rehashed_certificate_semantic_corruption
    )
    test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries = common.COSNativePressureTests.test_duplicate_delivery_is_noop_in_ancestry_and_failed_request_retries
    test_atomic_failures_at_preparation_window_and_publication = common.COSNativePressureTests.test_atomic_failures_at_preparation_window_and_publication
    test_checkpoints_at_each_window_boundary_and_observer_noninterference = common.COSNativePressureTests.test_checkpoints_at_each_window_boundary_and_observer_noninterference
    test_inside_domain_without_event_cannot_earn_gain = (
        common.COSNativePressureTests.test_inside_domain_without_event_cannot_earn_gain
    )
    test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds = common.COSNativePressureTests.test_independent_classifier_diamonds_unqualified_ties_singletons_thresholds

    def test_actual_frozen_input_two_roots_one_write_and_error_decomposition(self):
        records = []
        for role in ("current", "reset"):
            model = self.event.duplicate()
            if role == "reset":
                self.assertTrue(model.reset().committed)
            cert = self.fixture.certificates[int(role == "reset")]
            for beat in range(2):
                config = model.configuration
                before = config.current
                step, roots = observed(model)
                report = audit_step(config, before, step, cert, role=role)
                verify_step(step)
                self.assertEqual(model.configuration.step_index, config.step_index + 1)
                self.assertEqual(Q(model.configuration.time) - Q(config.time), 32)
                self.assertEqual(model.configuration.reset, config.reset)
                for row, state in zip(roots, (before, step.after), strict=True):
                    self.assertTrue(
                        all(
                            Q(lo) <= Q(x) <= Q(hi)
                            for (lo, hi), x in zip(row["input"], state.C, strict=True)
                        )
                    )
                    midpoint = [str((Q(lo) + Q(hi)) / 2) for lo, hi in row["input"]]
                    self.assertTrue(all(t == midpoint for t in row["trials"]))
                self.assertNotEqual(roots[0]["input"], roots[1]["input"])
                self.assertEqual(
                    model.compute_observables()["completion"]["children"], []
                )
                records.append(
                    {
                        "role": role,
                        "beat": beat + 1,
                        "subject": config.to_payload(),
                        "occurrence": model._operation._published.completion.event.to_dict()
                        if model._operation._published.completion.event
                        else None,
                        "step": transition(step),
                        "certificate": cert.to_payload(),
                        "trial_inputs": roots,
                        "audit": report,
                    }
                )
        self.evidence["actual_steps"] = records
        self.measurements["actual_target_steps"] = 4

    def test_rehashed_root_mutations_have_specific_mathematical_discriminators(self):
        good = self.good
        delta = Q(1, 2**40)
        variants = {}

        def root_variant(label, fn):
            payload = good.root.to_dict()
            fn(payload)
            variants[label] = replace(good, root=FrozenJSONMap(payload))

        root_variant(
            "unchanged_J_final_H_diagonal",
            lambda p: p["geometry"][-1].__setitem__(
                -1, shift(p["geometry"][-1][-1], delta)
            ),
        )
        root_variant(
            "unchanged_J_final_H_offdiagonal",
            lambda p: p["geometry"][-1].__setitem__(
                -2, shift(p["geometry"][-1][-2], delta)
            ),
        )
        root_variant(
            "sign_flipped_flat_same_H",
            lambda p: p.update(
                flat=[[[str(-Q(x[1])), str(-Q(x[0]))]] for (x,) in p["flat"]]
            ),
        )
        root_variant(
            "different_proposal_after_small_residual",
            lambda p: p["proposal"][0].__setitem__(
                0, shift(p["proposal"][0][0], delta)
            ),
        )
        root_variant(
            "fabricated_zero_residual", lambda p: p.update(proposal_residual=["0", "0"])
        )
        root_variant(
            "understated_root_error", lambda p: p.update(root_error=["0", "0"])
        )
        root_variant(
            "dropped_final_geometry_coordinate", lambda p: p["geometry"][-1].pop()
        )
        root_variant(
            "wrong_source_domain_on_target",
            lambda p: p.update(
                domain=owner.kernel(self.fixture.config).root_domain.to_dict()
            ),
        )
        root_variant(
            "mixed_reset_flat",
            lambda p: p.update(flat=self.reset_step.root.to_dict()["flat"]),
        )
        root_variant(
            "stale_poststate_root", lambda p: p.update(good.restart_root.to_dict())
        )
        root_variant(
            "overlap_without_containment",
            lambda p: p["current"][0].__setitem__(
                0,
                [
                    p["current"][0][0][0],
                    str(
                        Q(p["current"][0][0][0])
                        + (Q(p["current"][0][0][1]) - Q(p["current"][0][0][0])) / 8
                    ),
                ],
            ),
        )
        B = Equations(good.before.graph.to_payload()).B
        z = nullspace(B)[0]
        cycle_delta = Q(1, 2**120)
        p = good.root.to_dict()
        for i in range(z.nrows()):
            p["current"][i][0] = shift(p["current"][i][0], cycle_delta * z[i, 0])
        flux = tuple(str(Q(x) + cycle_delta * z[i, 0]) for i, x in enumerate(good.flux))
        variants["cycle_current_same_continuity"] = replace(
            good, root=FrozenJSONMap(p), flux=flux
        )
        self.assertEqual(B * vector(flux), B * vector(good.flux))
        rows = []
        for label, changed in variants.items():
            wire = seal(transition(changed))
            self.assertEqual(wire, seal(wire))
            with self.subTest(label=label), self.assertRaises(AssertionError) as error:
                audit_step(self.config, self.config.current, changed, self.cert)
            rows.append(
                {
                    "mutation": label,
                    "discriminator": str(error.exception),
                    "rehash": wire["record_digest"],
                }
            )
        self.measurements["root_mutations"] = rows
        self.evidence["root_mutation_reference"] = transition(good)

    def test_fixed_H_or_regenerated_H_alone_is_not_joint_root_authority(self):
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            eq = Equations(self.config.reference.graph.to_payload(), outward=True)
            C = arb_mat(vector(self.config.current.C))
            for f in (
                arb_mat(eq.I.nrows(), 1),
                arb_mat([[Q(1, 128)] for _ in range(eq.I.nrows())]),
            ):
                H = eq.geometry(f)
                J, F = eq.read(C, H)
                self.assertGreater(upper(F - f), Q(1, 2**192))
                self.assertTrue(
                    all(x.contains(0) for x in (H - eq.geometry(f)).entries())
                )
                # An excellent linear solve and regenerated H do not close CI.
                self.assertTrue(
                    any(
                        not (
                            J[i, 0]
                            - decode(self.good.root["current"], eq.I.nrows(), 1)[i, 0]
                        ).contains(0)
                        for i in range(eq.I.nrows())
                    )
                )
            root = CCIReference(self.config.reference.graph.to_payload()).root(C)
            H = root["geometry"]
            f = root["flat"]
            self.assertGreater(upper(H * eq.L - eq.L * H), Q(1, 2**192))
            j, flat = eq.read(C, H)
            site = arb_mat([[(x - 2) ** 3 - (x - 2)] for x in C.entries()])
            j0 = (
                -eq.B.transpose() * (eq.B * H * eq.B.transpose() * C / 64 - site) / 1024
            )
            wrong = j0 + (3 * eq.I / 4 + eq.L * H).solve(j0) / 4
            frozen = (
                -eq.B.transpose() * (eq.B * eq.B.transpose() * C / 64 - site) / 1024
            )
            frozen = frozen + (3 * eq.I / 4 + H * eq.L).solve(frozen) / 4
            self.assertTrue(any(not x.contains(0) for x in (wrong - j).entries()))
            self.assertTrue(any(not x.contains(0) for x in (frozen - j).entries()))
            self.assertTrue(any(not x.contains(0) for x in (H * flat - flat).entries()))

    def test_residual_upper_endpoint_and_graph_specific_root_bounds(self):
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            for state, payload in [
                (self.good.before, self.good.root),
                (self.reset_step.before, self.reset_step.root),
            ]:
                changed = payload.to_dict()
                changed["proposal_residual"][0] = str(
                    -Q(changed["proposal_residual"][1])
                )
                audit_root(state, changed)  # A negative lower endpoint is harmless.
            source = owner.kernel(self.fixture.config).step(self.fixture.config.current)
            audit_step(self.fixture.config, source.before, source)
            ds, dt = (
                domain(source.before.graph.to_payload()),
                domain(self.good.before.graph.to_payload()),
            )
            self.assertNotEqual(ds["contraction"], dt["contraction"])
            changed = source.root.to_dict()
            changed["domain"] = self.good.root["domain"].to_dict()
            with self.assertRaisesRegex(AssertionError, "graph-specific"):
                audit_root(source.before, changed)
            self.measurements["root_domains"] = {
                "source": ds,
                "target": dt,
                "homotopy_to_reference": "uniform bounds dominate t in [0,1]",
            }

    def test_OS_source_poststate_and_split_admission_do_not_substitute_CI(self):
        config = self.fixture.config
        k = owner.kernel(config)
        ci = k.step(config.current)
        from p991a2_native_spark_numerics import profile as cos_profile

        os = SparkCOSKernel(
            config.reference.graph, cos_profile(config.reference.graph)
        ).step(config.current)
        wrong = replace(ci, after=os.after, flux=os.flux)
        with self.assertRaises(AssertionError):
            audit_step(config, config.current, wrong)
        self.assertNotEqual(ci.after, os.after)
        self.assertEqual(ci.after, self.fixture.source_model.configuration.current)
        self.evidence["source_discriminator"] = {
            "subject": config.to_payload(),
            "step": transition(ci),
            "role": "current",
            "audit": audit_step(config, config.current, ci),
            "OS_output": os.after.to_payload(),
            "actual_public_CI_source_output": self.fixture.source_model.configuration.current.to_payload(),
        }
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            e = Equations(config.reference.graph.to_payload(), outward=True)
            read = e.step(config.current.C)
            closure = (
                e.read(read["C"], e.geometry(read["corrector_flat"]))[1]
                - read["corrector_flat"]
            )
            self.assertGreater(upper(closure), Q(1, 2**192))
        self.measurements["CI_OS_discriminator"] = {
            "source_states_differ": True,
            "OS_split_is_not_CI_certificate": True,
        }

    def test_full_implicit_derivative_all_14_finite_segments(self):
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            m = CCIReference(self.config.reference.graph.to_payload())
            S = arb_mat(matrix(self.cert.operands["S"]))
            C = arb_mat(vector(self.config.current.C))
            n = C.nrows()
            epsilon = Q(1, 2**36)
            # The exact event core is zero: use the first actual native target state.
            C = arb_mat(vector(self.good.after.C))
            reports = []
            for axis in range(14):
                d = arb_mat([[S[i, axis]] for i in range(n)])
                segment = arb_mat(
                    [
                        [
                            arb(
                                C[i, 0].mid().fmpq(),
                                (abs(d[i, 0]) * epsilon).upper().fmpq(),
                            )
                        ]
                        for i in range(n)
                    ]
                )
                with ctx.workprec(256):
                    _, J, _, _ = owner.kernel(self.config).analytic(segment)
                a = m.ci_step(C - epsilon * d)["after"]
                b = m.ci_step(C + epsilon * d)["after"]
                quotient = (b - a) / (2 * epsilon)
                integral = J * d
                self.assertTrue(
                    all(
                        x.contains(y)
                        for x, y in zip(
                            integral.entries(), quotient.entries(), strict=True
                        )
                    ),
                    axis,
                )
                reports.append(
                    {
                        "axis": axis,
                        "segment_half_length": str(epsilon),
                        "contains_independent_secant": True,
                    }
                )
            root = m.root(C)
            J, _ = m.full_jacobian(C)
            _, _, _, _, JC = m.partials(C, root["flat"])
            frozen = (
                arb_mat([[int(i == j) for j in range(n)] for i in range(n)])
                - 32 * m.B * JC
            )
            self.assertTrue(any(not x.contains(0) for x in (J - frozen).entries()))
            self.measurements["finite_segments"] = reports

    def test_root_contraction_cannot_replace_physical_certificate(self):
        wrong = deepcopy(self.cert.to_payload())
        wrong["proof"]["q"] = self.good.root["domain"]["contraction"]
        with self.assertRaisesRegex(ValueError, "recomputed mathematics"):
            CompletionCertificate.from_payload(wrong)
        self.assertNotEqual(
            self.cert.proof["q"], self.good.root["domain"]["contraction"]
        )

    def test_stagnation_nonfinite_and_iteration_limit_fail_without_progress(self):
        model = self.event.duplicate()
        before = model.snapshot()
        root = model._operation._spark_scope.published
        with patch.object(native, "PROPOSAL_BITS", 1024):
            self.assertFalse(model.step().committed)
        self.assertEqual(model.snapshot(), before)
        self.assertIs(model._operation._spark_scope.published, root)
        original = native.SparkCCIKernel._read_ball

        def nonfinite(k, C, H):
            value = original(k, C, H)
            value["F"] = arb_mat([[arb("nan")] for _ in range(H.nrows())])
            return value

        with patch.object(native.SparkCCIKernel, "_read_ball", nonfinite):
            self.assertFalse(model.step().committed)
        self.assertEqual(model.snapshot(), before)
        self.assertTrue(model.step().committed)
        # A counterfeit tiny update is not accepted as a residual certificate.
        p = self.good.root.to_dict()
        p["proposal"] = [[["0", "0"]] for _ in p["proposal"]]
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            e = Equations(self.good.before.graph.to_payload(), outward=True)
            _, F = e.read(arb_mat(vector(self.good.before.C)), e.I)
            residual = upper(F)
            movement = residual / Q(2**220)
            self.assertLess(movement, Q(1, 2**192))
            self.assertGreater(residual, Q(1, 2**192))
        p["proposal_residual"] = ["0", str(movement)]
        with (
            _ARB_CONTEXT_LOCK,
            ctx.workprec(768),
            self.assertRaisesRegex(AssertionError, "proposal residual"),
        ):
            audit_root(self.good.before, p)

    def test_CI_specific_faults_roll_back_and_retry_final_window(self):
        rows = []
        for phase, method, index in [
            ("proposal", "_root", 1),
            ("final_residual", "_admitted_root", 1),
            ("poststate_root", "_admitted_root", 2),
        ]:
            model = self.fixture.synthetic_window_fixture()
            model.step()
            model.step()
            before = model.snapshot()
            publication = model._operation._spark_scope.published
            original = getattr(native.SparkCCIKernel, method)
            calls = []

            def fail(
                k, *args, original=original, index=index, phase=phase, calls=calls
            ):
                calls.append(args[0])
                value = original(k, *args)
                if len(calls) == index:
                    raise CertificationInconclusive("injected " + phase)
                return value

            with patch.object(native.SparkCCIKernel, method, fail):
                self.assertFalse(model.step().committed, phase)
            self.assertEqual(model.snapshot(), before)
            self.assertIs(model._operation._spark_scope.published, publication)
            self.assertEqual(model.step().local_gain, 1)
            rows.append({"phase": phase, "rollback": True, "retry_gain": 1})
        self.measurements["CI_transaction_faults"] = rows

    def test_target_and_reset_only_reconstruction_are_atomic(self):
        for phase, index in [("target_current", 1), ("target_reset", 2)]:
            model = self.fixture.source_model.duplicate()
            before = model.snapshot()
            publication = model._operation._spark_scope.published
            original = native.SparkCCIKernel.readmission
            calls = []

            def fail(k, state, index=index, calls=calls, original=original):
                calls.append(state)
                value = original(k, state)
                if len(calls) == index:
                    raise CertificationInconclusive("injected target readmission")
                return value

            req = request(model)
            with patch.object(native.SparkCCIKernel, "readmission", fail):
                self.assertFalse(model.expand(req).committed)
            self.assertEqual(model.snapshot(), before)
            self.assertIs(model._operation._spark_scope.published, publication)
            self.assertTrue(model.expand(req).committed)
        for operation in ("reset", "rebase_reset_baseline"):
            model = self.event.duplicate()
            before = model.snapshot()
            original = native.SparkCCIKernel.readmission
            calls = []

            def fail_second(k, state, calls=calls, original=original):
                calls.append(state)
                if len(calls) == 2:
                    raise CertificationInconclusive("reset-role failure")
                return original(k, state)

            with patch.object(native.SparkCCIKernel, "readmission", fail_second):
                self.assertFalse(getattr(model, operation)().committed)
            self.assertEqual(model.snapshot(), before)
            self.assertTrue(getattr(model, operation)().committed)

    def test_graph_same_sizes_profile_migration_and_no_proposal_history(self):
        graph = self.config.reference.graph
        payload = graph.to_payload()
        edge = payload["edges"][0]
        edge["tail"], edge["head"] = edge["head"], edge["tail"]
        changed = GRCV4Graph.from_payload(payload)
        before = native.SparkCCIKernel.root_cache_info()
        k = native.SparkCCIKernel(changed, profile(changed))
        after = k.root_cache_info()
        self.assertGreater(after["misses"], before["misses"])
        self.assertNotEqual(changed.graph_digest, graph.graph_digest)
        state = ExactResources(changed, self.config.current.C, "21")
        step = k.step(state)
        verify_step(step)
        self.assertEqual(step.after.C, self.good.after.C)
        with self.assertRaises(ValueError):
            self.cert.require_binding(k, self.config.policy, "current", "21")
        with self.assertRaises(TypeError):
            k.root_domain["contraction"] = "0"
        # A degree-preserving endpoint swap changes adjacency as well as the
        # stable-edge binding; dimensions alone cannot key the cached operators.
        payload = graph.to_payload()
        a, b = payload["edges"][0], payload["edges"][4]
        a["head"], b["head"] = b["head"], a["head"]
        other = GRCV4Graph.from_payload(payload)
        left, right = Equations(graph.to_payload()), Equations(payload)
        self.assertNotEqual(left.B * left.B.transpose(), right.B * right.B.transpose())
        before = native.SparkCCIKernel.root_cache_info()
        other_kernel = native.SparkCCIKernel(other, profile(other))
        self.assertGreater(other_kernel.root_cache_info()["misses"], before["misses"])
        other_state = ExactResources(other, self.config.current.C, "21")
        verify_step(other_kernel.step(other_state))
        self.measurements["same_size_graph_cache_controls"] = {
            "source": graph.to_payload(),
            "orientation": changed.to_payload(),
            "changed_adjacency": other.to_payload(),
            "fresh_misses": True,
        }
        self.assertNotIn("root", self.config.to_payload())
        old = self.event.duplicate()
        snapshot = old.snapshot()
        changed_profile = profile(graph, solver={"conditioning_limit": 1})
        target = replace(
            old.configuration,
            reference=replace(old.configuration.reference, profile=changed_profile),
        )
        self.assertFalse(old.migrate_spark_configuration(target).committed)
        self.assertEqual(old.snapshot(), snapshot)
        self.assertTrue(old.step().committed)

    def test_cold_load_root_failure_registers_no_partial_owner(self):
        model = self.event.duplicate()
        snapshot = model.snapshot()
        origin = snapshot["owner"]["origin"]
        with owner._SCOPES_LOCK:
            scope = owner._SCOPES.pop(origin)
        try:
            with (
                patch.object(
                    native.SparkCCIKernel,
                    "_root",
                    side_effect=CertificationInconclusive("cold replay root fault"),
                ),
                self.assertRaises((ValueError, RuntimeError)),
            ):
                GRC9V4.from_state(snapshot)
            self.assertNotIn(origin, owner._SCOPES)
            loaded = GRC9V4.from_state(snapshot)
            self.assertEqual(loaded.snapshot(), snapshot)
            self.assertTrue(loaded.step().committed)
        finally:
            with owner._SCOPES_LOCK:
                owner._SCOPES[origin] = scope

    def test_uniform_root_is_not_a_child_or_event(self):
        state = ExactResources(self.config.reference.graph, tuple(["7/5"] * 15), "21")
        config = replace(self.config, current=state, reset=state)
        model = GRC9V4(config)
        step, roots = observed(model)
        self.assertEqual(step.after, state)
        self.assertTrue(all(Q(x) == 0 for x in step.flux))
        self.assertEqual(len(roots), 2)
        audit_step(config, state, step)
        self.assertEqual(model.compute_observables()["completion"]["children"], [])

    def test_native_execution_has_no_research_or_saved_trajectory_dependency(self):
        code = r"""
import json,pathlib,sys
root=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(root/'src'))
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)) and any(p in str(args[0]) for p in ('/investigations/','/tests/')):
        raise RuntimeError('native research dependency')
sys.addaudithook(audit)
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
x=json.load(sys.stdin);m=GRC9V4(GRC9V4SparkConfiguration.from_payload(x['configuration']))
assert m.step().committed
assert m.expand(GRC9V4ExpansionRequestInput.from_payload(x['request'])).committed
assert m.step().committed
assert m.support_status()['execution_families']==['C_CI']
print('native_CI_only_pass')
"""
        result = subprocess.run(
            [sys.executable, "-I", "-c", code, str(ROOT)],
            input=json.dumps(
                {
                    "configuration": configuration().to_payload(),
                    "request": request(self.fixture.source_model).to_payload(),
                }
            ),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("native_CI_only_pass", result.stdout)

    def test_literal_both_chiral_events_and_role_transfer(self):
        # Reuse the exact topology/transfer assertions with the CI constructor.
        # The scoped patch selects fixture construction only, never map expectations.
        import test_cos_native_spark_pressure as common

        with patch.object(common, "configuration", configuration):
            common.COSNativePressureTests.test_literal_both_chiral_events_and_actual_role_transfer(
                self
            )
        for chi in (-1, 1):
            model = self.fixture.source_model.duplicate()
            self.assertTrue(model.expand(request(model, chi)).committed)
            pair, center = certificate_pair(model)
            for role, state in [
                ("current", model.configuration.current),
                ("reset", model.configuration.reset),
            ]:
                step = owner.kernel(model.configuration).step(state)
                audit_step(
                    model.configuration,
                    state,
                    step,
                    pair[int(role == "reset")],
                    role=role,
                )
            roster = dict(self.assert_classification(center)[0])
            sat = model._operation._published.completion.event["module"][2]
            self.assertEqual(set(roster["p"]), {"p", "private"})
            self.assertEqual(set(roster[sat]), {sat, "n2", "n8"})


if __name__ == "__main__":
    unittest.main()
