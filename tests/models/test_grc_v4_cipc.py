"""CI+PC literal composition, separate candidate chains and history pressure."""

from dataclasses import replace
from fractions import Fraction
import math
import unittest
from unittest.mock import patch

import numpy as np

from pygrc.models.grc_v4_ci import (
    CandidateCIRoot,
    ProvisionalCandidateCIStep,
    CIContractionCertificate,
    CITrial,
    CIStageError,
    CIBoundedDomain,
    JOINT_NORM,
    SOLVER_ID,
)
from pygrc.models.grc_v4_pc import (
    CandidatePCRead,
    PCEnvelopeCertificate,
    PCStageError,
    scalar_zoh,
    carrier_geometry,
)
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    OrientedEdge,
    PhysicalFlux,
)
from pygrc.models.grc_v4_profile import resolve_profile, list_supported_profiles
from pygrc.models.grc_v4_step import (
    ResourceBoundaryError,
    CurrentSelection,
    ProvisionalResourceStep,
)
from tests.models.test_grc_v4_profile import reidentify
from tests.models.test_grc_v4_pc import (
    fixture as pc_fixture,
    configure as pc_configure,
    zoh_oracle,
)
from tests.models.test_grc_v4_ci import independent_point
from tests.models.test_grc_v4_candidate_a import scalar_oracle, log_writer_oracle


def configure(before, *, domain_radius=0.125, tolerance=1e-11, limit=60, changes=None):
    ref = before.geometry.reference
    params, identity = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    params["realization"].update(
        schema_version="grcv4-cipc-params-v1",
        contraction_domain_id=CIBoundedDomain(domain_radius).identity,
        root_selector_id="unique_admitted_root_v1",
        iteration_limit=limit,
        residual_norm_id=JOINT_NORM,
        tolerance=tolerance,
        rho_inst=1,
    )
    params["solver"].update(solver_kind="fixed_point", iteration_limit=limit)
    identity.update(
        realization="CI+PC",
        profile_family_id=identity["candidate"] + "_CI_PC",
        solver_id=SOLVER_ID,
        composition_gain=2,
    )
    for group, values in (changes or {}).items():
        (identity if group == "identity" else params[group]).update(values)
    reidentify(params, identity)
    ref = replace(ref, profile=resolve_profile(params, identity))
    return replace(before, geometry=ref.geometry())


def fixture(
    candidate="C",
    *,
    domain_radius=0.125,
    tolerance=1e-11,
    limit=60,
    composite_changes=None,
    **kwargs,
):
    before, backend = pc_fixture(candidate, **kwargs)
    return configure(
        before,
        domain_radius=domain_radius,
        tolerance=tolerance,
        limit=limit,
        changes=composite_changes,
    ), backend


def independent_root(before, backend):
    """Literal root iteration using existing independent candidate equations."""
    ref = before.geometry.reference
    href = np.array(ref.pairings.one_form.matrix)
    z = np.array(before.current.Z_4).reshape(href.shape)
    gain = ref.profile.params_resolved.geometry.kappa_H
    h = href.copy()
    for _ in range(400):
        current, source = independent_point(before, backend, h)
        generated = href + gain * (z + source)
        if np.linalg.norm(generated - h) < 5e-15:
            return h, current, source
        h = generated
    raise AssertionError("independent composite root did not converge")


class CandidateCCIPCTests(unittest.TestCase):
    def test_nonzero_geometry_gain_has_literal_gain_two_equilibrium(self):
        before, _ = fixture(
            gain=0.001, domain_radius=0.25, changes={"candidate": {"tau_C": 0.0}}
        )
        p = before.geometry.reference.profile.params_resolved.candidate
        flat = (
            -2
            * p.eta_C
            * p.W_C_tr["e"]
            * p.kappa_Phi_C
            * (before.current.C[0] - before.current.C[1])
            * p.chi_C
            / (1 - p.zeta_C * p.chi_C)
        )
        source = p.zeta_C * flat**2
        settled = replace(before, current=replace(before.current, Z_4=(source,)))
        root = CandidateCIRoot(settled)
        self.assertAlmostEqual(
            root.selected.structural_source.increment[0][0], source, places=14
        )
        expected = (
            before.geometry.reference.pairings.one_form.matrix[0][0]
            + 0.001 * 2 * source
        )
        self.assertAlmostEqual(
            root.selected.inputs.geometry.one_form_hodge.matrix[0][0],
            expected,
            places=12,
        )
        self.assertGreater(abs(expected - (2 + 0.001 * source)), 1e-5)

    def test_nonzero_old_history_joint_root_against_literal_oracle(self):
        before, backend = fixture(z=(2.0,))
        root = CandidateCIRoot(before, backend)
        h, current, source = independent_root(before, backend)
        np.testing.assert_allclose(
            root.selected.inputs.geometry.one_form_hodge.matrix, h, rtol=0, atol=1e-11
        )
        np.testing.assert_allclose(root.current.values, current, rtol=1e-10, atol=1e-11)
        np.testing.assert_allclose(
            root.selected.structural_source.increment, source, rtol=1e-10, atol=1e-12
        )
        self.assertEqual(root.selected.inputs.stage, "cipc_trial")
        self.assertEqual(root.selected.inputs.current.Z_4, (2.0,))
        self.assertLessEqual(root.selected.residual_squared, Fraction(1e-11) ** 2)

    def test_dense_noncommuting_retained_geometry_and_trial_refresh(self):
        graph = GRCV4Graph(
            ("a", "b", "c"), (OrientedEdge("x", "a", "b"), OrientedEdge("y", "b", "c"))
        )
        before, backend = fixture(
            graph=graph,
            C=(2.0, 1.0, 0.5),
            z=(1.0, 0.25, 0.25, 2.0),
            changes={"candidate": {"kappa_M_C": 0.1, "zeta_C": 0.05, "Lambda_C": 0.5}},
        )
        root = CandidateCIRoot(before, backend)
        h, current, source = independent_root(before, backend)
        np.testing.assert_allclose(root.current.values, current, rtol=2e-10, atol=1e-10)
        np.testing.assert_allclose(
            root.selected.structural_source.increment, source, rtol=2e-9, atol=1e-10
        )
        self.assertGreater(abs(h[0, 1]), 0)
        self.assertGreater(root.evaluations, 1)
        first = CITrial(
            replace(root.selected.inputs, geometry=before.geometry, evaluation_index=0),
            None,
        )
        self.assertNotEqual(
            first.point.algebra.baseline, root.selected.point.algebra.baseline
        )
        self.assertNotEqual(
            first.point.algebra.selector, root.selected.point.algebra.selector
        )

    def test_both_geometry_paths_change_the_consumed_root(self):
        before, _ = fixture(z=(4.0,))
        root = CandidateCIRoot(before)
        zero = replace(before, current=replace(before.current, Z_4=(0.0,)))
        self.assertNotEqual(root.current, CandidateCIRoot(zero).current)
        pc = pc_configure(
            before,
            z=before.current.Z_4,
            changes={"identity": {"composition_gain": None}},
        )
        pc_read = CandidatePCRead(pc)
        self.assertNotEqual(root.current.values, pc_read.point.current.values)
        self.assertNotEqual(
            before.geometry.reference.profile.complete_profile_id,
            pc.geometry.reference.profile.complete_profile_id,
        )

    def test_source_held_through_continuity_and_exactly_one_carrier_write(self):
        before, _ = fixture(z=(2.0,), tau=0.1)
        with patch("pygrc.models.grc_v4_pc.scalar_zoh", wraps=scalar_zoh) as writer:
            step = ProvisionalCandidateCIStep(before)
        source = tuple(
            x for row in step.root.selected.structural_source.increment for x in row
        )
        self.assertEqual(writer.call_count, 1)
        self.assertEqual(
            writer.call_args.args, (before.current.Z_4, source, before.dt, 0.1)
        )
        self.assertEqual(
            step.next_inputs.current.Z_4,
            zoh_oracle(before.current.Z_4, source, before.dt, 0.1),
        )
        self.assertEqual(step.resource.continuity_evaluations, 1)
        self.assertEqual(step.carrier_writes, 1)
        self.assertIsNone(step.writer)
        self.assertNotEqual(
            step.restart.selected.structural_source.increment,
            step.root.selected.structural_source.increment,
        )
        np.testing.assert_allclose(
            step.next_inputs.current.C,
            np.array(before.current.C)
            - before.dt
            * np.array(before.geometry.reference.graph.incidence)
            @ np.array(step.root.current.values),
            atol=1e-14,
        )

    def test_selector_boundary_fails_before_any_current(self):
        before, _ = fixture(changes={"candidate": {"Lambda_C": 4.0}})
        with patch(
            "pygrc.models.grc_v4_ci._point",
            side_effect=AssertionError("current attempted"),
        ):
            with self.assertRaises(PCStageError) as caught:
                CandidateCIRoot(before)
        self.assertEqual(caught.exception.disposition, "domain_failure")


class CandidateACIPCTests(unittest.TestCase):
    def test_old_history_root_recomputes_A_potential_and_conductance(self):
        before, backend = fixture("A", z=(3.0,))
        root = CandidateCIRoot(before, backend)
        h, current, source = independent_root(before, backend)
        np.testing.assert_allclose(root.current.values, current, rtol=1e-10, atol=1e-11)
        np.testing.assert_allclose(
            root.selected.structural_source.increment, source, rtol=1e-10, atol=1e-12
        )
        initial = CITrial(
            replace(root.selected.inputs, geometry=before.geometry, evaluation_index=0),
            backend,
        )
        self.assertNotEqual(initial.point.baseline, root.selected.point.baseline)
        self.assertNotEqual(initial.point.W_hat_A, root.selected.point.W_hat_A)

    def test_W_writer_preserves_old_Z_before_one_same_root_Z_write(self):
        before, backend = fixture("A", z=(3.0,))
        step = ProvisionalCandidateCIStep(before, backend)
        self.assertEqual(step.writer.authority.state.Z_4, before.current.Z_4)
        self.assertEqual(step.carrier_writes, 1)
        source = tuple(
            x for row in step.root.selected.structural_source.increment for x in row
        )
        self.assertEqual(
            step.next_inputs.current.Z_4,
            zoh_oracle(before.current.Z_4, source, before.dt, 0.5),
        )
        _, target = scalar_oracle(
            before.geometry.reference,
            backend,
            step.resource.provisional_state.C,
            step.root.current.values,
        )
        expected = log_writer_oracle(
            before.current.W_A,
            target,
            before.dt,
            before.geometry.reference.profile.params_resolved.candidate.tau_A,
        )
        np.testing.assert_allclose(step.next_inputs.current.W_A, expected, rtol=1e-14)
        self.assertEqual(step.resource.continuity_evaluations, 1)
        self.assertNotEqual(
            step.restart.selected.structural_source.increment,
            step.root.selected.structural_source.increment,
        )

    def test_loop_parallel_and_isolated_coordinates(self):
        graph = GRCV4Graph(
            ("a", "b", "iso"),
            (
                OrientedEdge("e0", "a", "b"),
                OrientedEdge("e1", "a", "b"),
                OrientedEdge("loop", "a", "a"),
            ),
        )
        before, backend = fixture(
            "A",
            graph=graph,
            C=(2.0, 1.0, 0.5),
            W=(1.2, 1.4, 1.6),
            z=(1.0, 0.2, 0.0, 0.2, 1.0, 0.1, 0.0, 0.1, 1.0),
            changes={"candidate": {"zeta_A": 0.05}},
        )
        root = CandidateCIRoot(before, backend)
        _, current, source = independent_root(before, backend)
        np.testing.assert_allclose(root.current.values, current, rtol=1e-10, atol=1e-11)
        np.testing.assert_allclose(
            root.selected.structural_source.increment, source, rtol=1e-9, atol=1e-12
        )
        self.assertEqual(root.current.values[-1], 0)

    def test_reset_W_admission_and_writer_policy_at_zero_duration(self):
        before, backend = fixture("A", z=(2.0,))
        for dt in (0.0, before.dt):
            bad = replace(before, dt=dt, reset=replace(before.reset, W_A=(3.0,)))
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateCIStep(bad, backend)
            self.assertEqual(caught.exception.stage, "pre_read_reconstruction")


class CIPCSharedTests(unittest.TestCase):
    def test_signed_orientation_covariance_with_dense_history(self):
        graph = GRCV4Graph(
            ("a", "b", "c"), (OrientedEdge("x", "a", "b"), OrientedEdge("y", "b", "c"))
        )
        reversed_graph = GRCV4Graph(
            graph.live_node_ids,
            (OrientedEdge("x", "b", "a"), OrientedEdge("y", "b", "c")),
        )
        sign = np.diag([-1.0, 1.0])
        z = np.array([[1.0, 0.25], [0.25, 2.0]])
        for candidate in ("A", "C"):
            args = dict(
                C=(2.0, 1.0, 0.5),
                W=(1.5, 1.75),
                changes={"candidate": {"zeta_" + candidate: 0.05}},
            )
            before, backend = fixture(candidate, graph=graph, z=tuple(z.flat), **args)
            reversed_before, reversed_backend = fixture(
                candidate, graph=reversed_graph, z=tuple((sign @ z @ sign).flat), **args
            )
            root = CandidateCIRoot(before, backend)
            other = CandidateCIRoot(reversed_before, reversed_backend)
            np.testing.assert_allclose(
                other.current.values,
                sign @ np.array(root.current.values),
                rtol=1e-11,
                atol=1e-12,
            )
            np.testing.assert_allclose(
                other.selected.structural_source.increment,
                sign @ np.array(root.selected.structural_source.increment) @ sign,
                rtol=1e-11,
                atol=1e-12,
            )
            np.testing.assert_allclose(
                other.selected.inputs.geometry.one_form_hodge.matrix,
                sign
                @ np.array(root.selected.inputs.geometry.one_form_hodge.matrix)
                @ sign,
                rtol=1e-11,
                atol=1e-12,
            )

    def test_negative_gains_and_gate_ablation_keep_old_history(self):
        for candidate in ("A", "C"):
            for gate, value in (
                ("zeta_" + candidate, -0.05),
                ("chi_" + candidate, 0.0),
            ):
                before, backend = fixture(
                    candidate,
                    gain=-1e-5,
                    z=(-2.0,),
                    changes={"candidate": {gate: value}},
                )
                root = CandidateCIRoot(before, backend)
                h, current, source = independent_root(before, backend)
                np.testing.assert_allclose(
                    root.current.values, current, rtol=1e-10, atol=1e-11
                )
                np.testing.assert_allclose(
                    root.selected.structural_source.increment,
                    source,
                    rtol=1e-10,
                    atol=1e-12,
                )
                if gate.startswith("chi"):
                    self.assertEqual(
                        root.selected.structural_source.increment, ((0.0,),)
                    )
                    self.assertNotEqual(
                        tuple(map(tuple, h)), before.geometry.one_form_hodge.matrix
                    )
                else:
                    self.assertLess(source[0, 0], 0)

    def test_source_envelope_is_not_inferred_from_zero_submitted_state(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, C=(0.0, 0.0), radius=1e-20)
            with self.assertRaisesRegex(PCStageError, "source envelope"):
                CandidateCIRoot(before, backend)

    def test_B2R_exact_boundary_and_adjacent_domain_rejection(self):
        for candidate in ("A", "C"):
            args = dict(
                radius=32.0,
                gain=2**-10,
                changes={"candidate": {"zeta_" + candidate: 0.01}},
            )
            before, backend = fixture(candidate, domain_radius=0.0625, **args)
            bound = CIContractionCertificate(before, backend)
            self.assertEqual(
                Fraction(bound.bounds["composite_geometry_radius"]), Fraction(0.0625)
            )
            bad, _ = fixture(candidate, domain_radius=math.nextafter(0.0625, 0), **args)
            with self.assertRaisesRegex(PCStageError, "B_2R"):
                CandidateCIRoot(bad, backend)

    def test_reset_resource_and_carrier_are_independent_of_live_state(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(1.0,), reset_z=(-2.0,))
            for dt in (0.0, before.dt):
                for reset in (
                    replace(before.reset, C=(5.0, 0.0)),
                    replace(before.reset, Z_4=(65.0,)),
                ):
                    altered = replace(before, dt=dt, reset=reset)
                    with self.assertRaises(ResourceBoundaryError):
                        ProvisionalCandidateCIStep(altered, backend)
            self.assertEqual(before.current.Z_4, (1.0,))

    def test_clock_charge_and_resource_failures_preserve_inputs(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(1.0,))
            for altered in (
                replace(before, step_index=2**53 - 1),
                replace(before, Q_target=1.0),
                replace(
                    before,
                    time=float.fromhex("0x1.fffffffffffffp+1023"),
                    dt=float.fromhex("0x1.fffffffffffffp+1023"),
                ),
            ):
                with self.assertRaises(ResourceBoundaryError):
                    ProvisionalCandidateCIStep(altered, backend)
            with self.assertRaises(ResourceBoundaryError):
                ProvisionalCandidateCIStep(replace(before, dt=1000.0), backend)
            self.assertEqual(before.current.Z_4, (1.0,))

    def test_failed_carrier_writer_cannot_publish_a_resource_or_W_poststate(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(2.0,))
            payload = before.to_payload()
            with patch(
                "pygrc.models.grc_v4_pc.scalar_zoh",
                side_effect=PCStageError("domain_failure", "forced writer failure"),
            ):
                with self.assertRaises(ResourceBoundaryError) as caught:
                    ProvisionalCandidateCIStep(before, backend)
            self.assertEqual(caught.exception.stage, "history_write")
            self.assertEqual(before.to_payload(), payload)

    def test_selected_current_cannot_be_swapped_for_a_different_trial(self):
        before, backend = fixture("A", z=(2.0,))
        root = CandidateCIRoot(before, backend)
        wrong = PhysicalFlux(
            before.geometry.reference.graph, (root.current.values[0] + 1.0,)
        )
        with self.assertRaises(ResourceBoundaryError):
            ProvisionalResourceStep(
                before, CurrentSelection(root.selected.inputs, "valid_root", wrong)
            )

    def test_computed_negative_zero_in_shared_source_is_canonical(self):
        from pygrc.models.grc_v4_ci import _source

        for candidate in ("A", "C"):
            before, backend = fixture(
                candidate,
                gain=0.0,
                changes={"candidate": {"zeta_" + candidate: -math.ulp(0.0)}},
            )
            root = CandidateCIRoot(before, backend)
            tiny = PhysicalFlux(before.geometry.reference.graph, (1e-100,))
            source = _source(root.selected.point, tiny)
            self.assertEqual(source.increment, ((0.0,),))
            self.assertEqual(math.copysign(1, source.increment[0][0]), 1)

    def test_B2R_domain_requirement_cannot_be_replaced_by_old_PC_ball(self):
        for candidate in ("A", "C"):
            before, backend = fixture(
                candidate, radius=64.0, gain=1e-5, domain_radius=0.0008
            )
            self.assertLess(64e-5, 0.0008)
            with self.assertRaisesRegex(PCStageError, "B_2R"):
                CandidateCIRoot(before, backend)

    def test_uniform_source_slack_and_contraction_are_derived(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(1.0,))
            certificate = CIContractionCertificate(before, backend)
            self.assertGreater(Fraction(certificate.bounds["uniform_source_slack"]), 0)
            self.assertLess(Fraction(certificate.bounds["contraction_upper"]), 1)
            self.assertEqual(certificate.bounds["rho_inst"], 1)
            self.assertEqual(
                Fraction(certificate.bounds["composite_geometry_radius"]),
                2 * Fraction(1e-5) * 64,
            )
            for c in ((0.0, 0.0), (4.0, 0.0), (0.0, 4.0)):
                altered = replace(before, current=replace(before.current, C=c))
                envelope = PCEnvelopeCertificate(altered, backend)
                self.assertEqual(
                    envelope.bounds, certificate.bounds["composite_envelope"]
                )

    def test_zero_Z_root_is_CI_but_enabled_writer_changes_future_state(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate)
            root = CandidateCIRoot(before, backend)
            no_carrier = replace(before.current, Z_4=None)
            no_reset = replace(before.reset, Z_4=None)
            # Change profile and state together; the carrier is identity-bearing.
            base = before.geometry.reference
            p, i = (
                base.profile.params_resolved.to_payload(),
                base.profile.identity_payload.to_payload(),
            )
            p["realization"] = {
                k: v
                for k, v in p["realization"].items()
                if k
                in {
                    "schema_version",
                    "contraction_domain_id",
                    "root_selector_id",
                    "iteration_limit",
                    "residual_norm_id",
                    "tolerance",
                }
            }
            p["realization"]["schema_version"] = "grcv4-ci-params-v1"
            i.update(
                realization="CI",
                profile_family_id=candidate + "_CI",
                composition_gain=None,
            )
            reidentify(p, i)
            ci_ref = replace(base, profile=resolve_profile(p, i))
            ci = replace(
                before, geometry=ci_ref.geometry(), current=no_carrier, reset=no_reset
            )
            ci_root = CandidateCIRoot(ci, backend)
            self.assertEqual(root.current.values, ci_root.current.values)
            self.assertEqual(
                root.selected.structural_source.increment,
                ci_root.selected.structural_source.increment,
            )
            self.assertEqual(
                root.selected.inputs.geometry.one_form_hodge.matrix,
                ci_root.selected.inputs.geometry.one_form_hodge.matrix,
            )
            self.assertTrue(
                any(ProvisionalCandidateCIStep(before, backend).next_inputs.current.Z_4)
            )

    def test_constant_source_carrier_limit_has_gain_two_not_normalized_gain(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, gain=0.0)
            root = CandidateCIRoot(before, backend)
            source = tuple(
                x for row in root.selected.structural_source.increment for x in row
            )
            self.assertTrue(any(source))
            z = (0.0,)
            for _ in range(8):
                z = scalar_zoh(z, source, 1.0, 0.5)
            expected = zoh_oracle((0.0,), source, 8.0, 0.5)
            np.testing.assert_allclose(z, expected, rtol=3e-16)
            settled = replace(before, current=replace(before.current, Z_4=source))
            result = CandidateCIRoot(settled, backend)
            self.assertEqual(
                result.selected.structural_source.increment,
                root.selected.structural_source.increment,
            )
            from pygrc.models.grc_v4_ci import _effective_source

            effective = _effective_source(settled, result.selected.structural_source)
            self.assertEqual(effective.increment, ((2 * source[0],),))
            self.assertAlmostEqual(
                (z[0] + source[0]) / (2 * source[0]), 1 - math.exp(-16) / 2, delta=3e-16
            )

    def test_zero_duration_admits_independent_histories_without_writes(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(2.0,), reset_z=(-1.0,))
            before = replace(before, dt=0.0)
            with patch(
                "pygrc.models.grc_v4_pc.scalar_zoh",
                side_effect=AssertionError("writer at dt0"),
            ):
                step = ProvisionalCandidateCIStep(before, backend)
            self.assertEqual(step.next_inputs, before)
            self.assertEqual(step.carrier_writes, 0)
            self.assertEqual(step.resource.continuity_evaluations, 0)
            self.assertNotEqual(
                step.root.selected.inputs.geometry,
                step.reset_root.selected.inputs.geometry,
            )

    def test_disabled_source_releases_history_without_dropping_old_geometry(self):
        for candidate in ("A", "C"):
            before, backend = fixture(
                candidate, z=(2.0,), changes={"candidate": {"zeta_" + candidate: 0.0}}
            )
            step = ProvisionalCandidateCIStep(before, backend)
            self.assertEqual(step.root.selected.structural_source.increment, ((0.0,),))
            self.assertEqual(
                step.root.selected.generated.one_form_hodge.matrix,
                carrier_geometry(before, before.current).one_form_hodge.matrix,
            )
            self.assertEqual(
                step.next_inputs.current.Z_4, zoh_oracle((2.0,), (0.0,), before.dt, 0.5)
            )
            self.assertGreater(step.next_inputs.current.Z_4[0], 0)

    def test_iteration_exhaustion_never_returns_a_PC_fallback(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(2.0,), limit=1, tolerance=1e-18)
            with self.assertRaises(CIStageError) as caught:
                CandidateCIRoot(before, backend)
            self.assertEqual(caught.exception.disposition, "no_admitted_root")

    def test_source_and_B2R_pass_do_not_replace_composite_contraction(self):
        before, backend = fixture(
            changes={"candidate": {"Lambda_C": 4.25001, "kappa_M_C": 0.1}}
        )
        envelope = PCEnvelopeCertificate(before, backend)
        self.assertLess(Fraction(envelope.bounds["source_norm_upper"]), 64)
        with self.assertRaisesRegex(CIStageError, "contraction bound"):
            CandidateCIRoot(before, backend)

    def test_W_chart_corners_and_uniform_source_derivative_bounds(self):
        before, backend = fixture("A", z=(1.0,))
        for weights in ((0.1,), (2.0,)):
            inputs = replace(before, current=replace(before.current, W_A=weights))
            envelope = PCEnvelopeCertificate(inputs, backend)
            root = CandidateCIRoot(inputs, backend)
            _, current, source = independent_root(inputs, backend)
            np.testing.assert_allclose(
                root.current.values, current, rtol=1e-10, atol=1e-11
            )
            self.assertLessEqual(
                np.linalg.norm(source),
                float(Fraction(envelope.bounds["source_norm_upper"])),
            )
            self.assertEqual(
                envelope.bounds, PCEnvelopeCertificate(before, backend).bounds
            )

    def test_unrepresentable_analytic_root_rejects_even_with_floating_stagnation(self):
        before, backend = fixture("A", z=(3.0,), tolerance=1e-300, limit=8)
        with self.assertRaises(CIStageError) as caught:
            CandidateCIRoot(before, backend)
        self.assertEqual(caught.exception.disposition, "no_admitted_root")

    def test_reconstruction_binds_composition_tau_reset_and_recipe(self):
        before, backend = fixture("A", z=(2.0,), reset_z=(-1.0,))
        root = CandidateCIRoot(before, backend)
        self.assertEqual(
            CandidateCIRoot.from_payload(root.to_payload()).to_payload(),
            root.to_payload(),
        )
        step = ProvisionalCandidateCIStep(before, backend)
        restored = ProvisionalCandidateCIStep.from_payload(step.to_payload())
        self.assertEqual(restored.next_inputs, step.next_inputs)
        wrong = root.to_payload()
        wrong["numerics"] = "ci_analytic_residual_enclosure_binary64_v2"
        with self.assertRaises(CIStageError):
            CandidateCIRoot.from_payload(wrong)
        with self.assertRaises(ValueError):
            configure(before, changes={"realization": {"rho_inst": 0}})
        with self.assertRaises(PCStageError):
            CandidatePCRead(before, backend)

    def test_bad_composite_residual_cannot_omit_old_history(self):
        before, backend = fixture("A", z=(4.0,))
        root = CandidateCIRoot(before, backend)
        zero = replace(before, current=replace(before.current, Z_4=(0.0,)))
        ci_like = CandidateCIRoot(zero, backend)
        wrong = CITrial(
            replace(
                root.selected.inputs,
                geometry=ci_like.selected.inputs.geometry,
                trial_current=ci_like.current,
            ),
            backend,
        )
        self.assertGreater(wrong.residual_squared, Fraction(1e-11) ** 2)
        self.assertLess(abs(float(wrong.geometry_residual[0][0]) + 4e-5), 1e-10)

    def test_public_capabilities_are_unchanged(self):
        self.assertEqual(len(list_supported_profiles()), 3)


# Independent audit proposals, executed natively and retained once for P9-6.3c.
import pygrc.models.grc_v4_ci as ci  # noqa: E402
from pygrc.models.grc_v4_candidate_a import CandidateACurrent  # noqa: E402
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge  # noqa: E402


class CIPCAdditionalAuditPressure(unittest.TestCase):
    def test_exact_old_source_cancellation_does_not_erase_writer_source(self):
        for candidate in ("A", "C"):
            params = (
                dict(
                    eta=5 / 16,
                    kappa_c=0.5,
                    alpha=0.0,
                    beta=0.0,
                    gamma=0.0,
                    kappa_Ah=0.0,
                    chi_A=0.25,
                    zeta_A=2.0,
                )
                if candidate == "A"
                else dict(
                    eta_C=15 / 32,
                    kappa_Phi_C=1.0,
                    kappa_M_C=0.0,
                    tau_C=0.0,
                    chi_C=0.25,
                    zeta_C=0.25,
                )
            )
            source = 0.125 if candidate == "A" else 0.25
            before, backend = fixture(
                candidate,
                z=(-source,),
                reset_z=(-source,),
                gain=2**-10,
                domain_radius=0.125,
                changes={"candidate": params},
            )
            step = ci.ProvisionalCandidateCIStep(before, backend)
            self.assertEqual(step.root.evaluations, 1)
            self.assertEqual(
                step.root.selected.structural_source.increment, ((source,),)
            )
            self.assertEqual(step.root.selected.inputs.geometry, before.geometry)
            self.assertEqual(step.root.selected.generated, before.geometry)
            self.assertEqual(step.root.selected.residual_squared, 0)
            expected = zoh_oracle((-source,), (source,), before.dt, 0.5)
            self.assertEqual(step.next_inputs.current.Z_4, expected)
            self.assertNotEqual(expected, (-source,))
            self.assertEqual(step.carrier_writes, 1)
            self.assertEqual(step.resource.continuity_evaluations, 1)

    def test_carrier_only_rounding_stagnation_is_not_analytic_zero(self):
        H, old = 2.0**100, 3 * 2.0**46
        graph = GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "v"),))
        from tests.models.test_grc_v4_candidate_c import current_fixture as c_fixture
        from tests.models.test_grc_v4_candidate_a import current_fixture as a_fixture

        for candidate in ("A", "C"):
            if candidate == "C":
                raw = c_fixture(
                    graph=graph,
                    resource=(0.0, 0.0),
                    weights={"e": H},
                    changes={
                        "candidate": dict(
                            chi_C=0.0, zeta_C=0.0, tau_C=0.0, kappa_M_C=0.0, Lambda_C=H
                        )
                    },
                )
                backend = None
            else:
                raw, backend = a_fixture(
                    graph=graph,
                    C=(0.0, 0.0),
                    W=(1.0,),
                    weights={"e": H},
                    alpha=0.0,
                    beta=0.0,
                    gamma=0.0,
                    chi_A=0.0,
                    zeta_A=0.0,
                )
            pc = pc_configure(
                raw,
                radius=2.0**59,
                resource_radius=1.0,
                gain=1.0,
                z=(old,),
                reset_z=(old,),
            )
            before = configure(pc, domain_radius=2.0**60, limit=3, tolerance=1e-11)
            certificate = ci.CIContractionCertificate(before, backend)
            self.assertEqual(Fraction(certificate.bounds["contraction_upper"]), 0)
            geometry = GRCV4Geometry(
                before.geometry.reference, OneFormHodge(graph, ((H + 2.0**48,),))
            )
            trial = ci.CITrial(
                replace(
                    before,
                    geometry=geometry,
                    stage="cipc_trial",
                    trial_current=PhysicalFlux(graph, (0.0,)),
                ),
                backend,
            )
            self.assertEqual(trial.generated, geometry)
            residual = trial.analytic_geometry_residual[0][0]
            self.assertEqual(
                (residual.lo, residual.hi), (Fraction(2**46), Fraction(2**46))
            )
            with self.assertRaises(ci.CIStageError) as caught:
                ci.CandidateCIRoot(before, backend)
            self.assertEqual(caught.exception.disposition, "no_admitted_root")
            exact = replace(before, current=replace(before.current, Z_4=(2.0**48,)))
            self.assertEqual(
                ci.CandidateCIRoot(exact, backend).selected.residual_squared, 0
            )

    def test_reset_and_consumed_root_exhaustion_have_distinct_stages(self):
        for candidate in ("A", "C"):
            before, backend = fixture(
                candidate,
                C=(0.0, 0.0),
                W=(1.0,),
                z=(2.0,),
                reset_z=(0.0,),
                limit=1,
                tolerance=0.0,
                changes={"candidate": {"zeta_" + candidate: 0.0}},
            )
            for inputs, expected in [
                (before, "candidate_solve"),
                (
                    replace(before, current=before.reset, reset=before.current),
                    "pre_read_reconstruction",
                ),
            ]:
                with self.assertRaises(ResourceBoundaryError) as caught:
                    ci.ProvisionalCandidateCIStep(inputs, backend)
                self.assertEqual(
                    (caught.exception.stage, caught.exception.code),
                    (expected, "no_admitted_root"),
                )

    def test_final_CI_chart_can_fail_after_PC_chart_and_fixed_current_pass(self):
        before, backend = fixture(
            "A", z=(2.0,), changes={"candidate": {"W_floor": 0.8}}
        )
        before = replace(before, dt=1 / 16)
        actual_root = ci.CandidateCIRoot
        captured = []

        def observed(inputs, backend=None):
            captured.append(inputs)
            return actual_root(inputs, backend)

        with patch.object(ci, "CandidateCIRoot", side_effect=observed):
            with self.assertRaises(ResourceBoundaryError) as caught:
                ci.ProvisionalCandidateCIStep(before, backend)
        self.assertEqual(
            (caught.exception.stage, caught.exception.code),
            ("final_reconstruction", "domain_failure"),
        )
        self.assertIn("floor chart", str(caught.exception))
        self.assertEqual(len(captured), 3)
        final = captured[-1]
        PCEnvelopeCertificate(final, backend)
        CandidateACurrent(final, backend)
        ci.ProvisionalCandidateCIStep(replace(before, dt=1 / 32), backend)


class CIPCReconciliationTests(unittest.TestCase):
    def test_negative_source_cancellation_and_one_ulp_history_neighbours(self):
        for candidate in ("A", "C"):
            for sign in (-1, 1):
                params = (
                    dict(
                        eta=(5 if sign == 1 else 7) / 16,
                        kappa_c=0.5,
                        alpha=0.0,
                        beta=0.0,
                        gamma=0.0,
                        kappa_Ah=0.0,
                        chi_A=0.25,
                        zeta_A=sign * 2.0,
                    )
                    if candidate == "A"
                    else dict(
                        eta_C=(15 if sign == 1 else 17) / 32,
                        kappa_Phi_C=1.0,
                        kappa_M_C=0.0,
                        tau_C=0.0,
                        chi_C=0.25,
                        zeta_C=sign * 0.25,
                    )
                )
                source = sign * (0.125 if candidate == "A" else 0.25)
                for gain in (2**-10, -(2**-10)):
                    before, backend = fixture(
                        candidate,
                        z=(-source,),
                        reset_z=(-source,),
                        gain=gain,
                        # sqrt(3**2+1**2) < 3.25. At M=4 the negative-zeta
                        # A counterpart reaches the conservative source bound R;
                        # cancellation at one state cannot supply strict slack.
                        resource_radius=3.25,
                        changes={"candidate": params},
                    )
                    root = CandidateCIRoot(before, backend)
                    self.assertEqual(root.selected.residual_squared, 0)
                    self.assertEqual(
                        root.selected.structural_source.increment, ((source,),)
                    )
                    for neighbour in (
                        math.nextafter(-source, -math.inf),
                        math.nextafter(-source, math.inf),
                    ):
                        inputs = replace(
                            root.selected.inputs,
                            current=replace(before.current, Z_4=(neighbour,)),
                        )
                        trial = CITrial(inputs, backend)
                        expected = -Fraction(gain) * (
                            Fraction(neighbour) + Fraction(source)
                        )
                        residual = trial.analytic_geometry_residual[0][0]
                        self.assertEqual(
                            (residual.lo, residual.hi), (expected, expected)
                        )
                        self.assertNotEqual(residual.lo, 0)
                        self.assertEqual(trial.generated, before.geometry)
                        self.assertEqual(
                            trial.structural_source.increment, ((source,),)
                        )

    def test_same_forcing_different_histories_do_not_have_the_same_source(self):
        for candidate in ("A", "C"):
            left, backend = fixture(candidate, z=(1.0,))
            right = replace(left, current=replace(left.current, Z_4=(3.0,)))
            first = ProvisionalCandidateCIStep(left, backend)
            second = ProvisionalCandidateCIStep(right, backend)
            s1 = first.root.selected.structural_source.increment[0][0]
            s2 = second.root.selected.structural_source.increment[0][0]
            self.assertNotEqual(s1, s2)
            delta = second.next_inputs.current.Z_4[0] - first.next_inputs.current.Z_4[0]
            a = math.exp(-left.dt / 0.5)
            expected = a * 2 + (1 - a) * (s2 - s1)
            self.assertAlmostEqual(delta, expected, delta=2e-15)
            self.assertGreater(abs(delta - a * 2), 1e-12)
            self.assertEqual(
                first.next_inputs.current.Z_4, zoh_oracle((1.0,), (s1,), left.dt, 0.5)
            )
            self.assertEqual(
                second.next_inputs.current.Z_4, zoh_oracle((3.0,), (s2,), right.dt, 0.5)
            )

    def test_programmer_errors_are_not_scientific_dispositions(self):
        for candidate in ("A", "C"):
            before, backend = fixture(candidate, z=(1.0,))
            for dt in (0.0, before.dt):
                with patch.object(
                    ci, "CandidateCIRoot", side_effect=RuntimeError("root bug")
                ):
                    with self.assertRaisesRegex(RuntimeError, "root bug"):
                        ProvisionalCandidateCIStep(replace(before, dt=dt), backend)
            with patch(
                "pygrc.models.grc_v4_pc.scalar_zoh",
                side_effect=RuntimeError("writer bug"),
            ):
                with self.assertRaisesRegex(RuntimeError, "writer bug"):
                    ProvisionalCandidateCIStep(before, backend)

    def test_uniform_source_h_derivative_bound_with_native_dense_candidate_chain(self):
        graph = GRCV4Graph(
            ("a", "b", "c"), (OrientedEdge("x", "a", "b"), OrientedEdge("y", "b", "c"))
        )
        directions = (
            np.array([[1.0, 0.0], [0.0, 0.0]]),
            np.array([[0.0, 1.0], [1.0, 0.0]]) / math.sqrt(2),
        )
        for candidate in ("A", "C"):
            changes = {"zeta_" + candidate: 0.05}
            if candidate == "C":
                changes.update(kappa_M_C=0.1, Lambda_C=0.5)
            before, backend = fixture(
                candidate,
                graph=graph,
                C=(2.0, 1.0, 0.5),
                W=(1.5, 1.75),
                z=(1.0, 0.25, 0.25, 2.0),
                changes={"candidate": changes},
            )
            envelope = PCEnvelopeCertificate(before, backend)
            v = float(Fraction(envelope.bounds["flat_norm_upper"]))
            lip = float(Fraction(envelope.bounds["flat_geometry_lipschitz_upper"]))
            bound = 2 * 0.05 * v * lip
            centre = np.array(
                before.geometry.reference.pairings.one_form.matrix
            ) + np.array([[0.01, 0.02], [0.02, -0.01]])
            for direction in directions:
                for epsilon in (2**-14, 2**-16):
                    sources = []
                    for sign in (-1, 1):
                        h = centre + sign * epsilon * direction
                        # Existing independent literal candidate equations, with
                        # native typed geometry/transport/state admission.
                        j, s = independent_point(before, backend, h)
                        self.assertLessEqual(
                            np.linalg.norm(j),
                            float(Fraction(envelope.bounds["current_norm_upper"])),
                        )
                        self.assertLessEqual(
                            np.linalg.norm(s),
                            float(Fraction(envelope.bounds["source_norm_upper"])),
                        )
                        sources.append(s)
                    slope = np.linalg.norm(sources[1] - sources[0]) / (2 * epsilon)
                    self.assertGreater(slope, 0)
                    self.assertLessEqual(slope, bound)
