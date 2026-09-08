"""Independent equations and adversarial staging for the bounded C_OS step."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import math
from typing import Any, cast
import unittest
from unittest.mock import patch

import numpy as np

from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_geometry import (
    GRCV4Geometry,
    GRCV4Graph,
    GeometryStageInputs,
    OneFormHodge,
    OrientedEdge,
)
from pygrc.models.grc_v4_realizations import (
    CandidateCOSPass,
    OSSplitResidual,
    OSStageError,
)
from pygrc.models.grc_v4_profile import CandidateCParams
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep, ResourceBoundaryError
from tests.models.test_grc_v4_candidate_c import current_fixture, dense_current_oracle


def os_fixture(**changes: Any) -> GeometryStageInputs:
    updates: dict[str, dict[str, Any]] = {
        "candidate": {
            "kappa_M_C": 0,
            "tau_C": 0.25,
            "eta_C": 0.5,
            "chi_C": 0.5,
            "zeta_C": 0.5,
        },
        "geometry": {"kappa_H": 0.125},
        "realization": {"tolerance": 1},
        "charge": {"absolute_tolerance": 1e-12},
    }
    for group, values in changes.items():
        updates.setdefault(group, {}).update(values)
    return cast(
        GeometryStageInputs,
        replace(
            current_fixture(
                graph=GRCV4Graph(("u", "v"), (OrientedEdge("e", "u", "v"),)),
                weights={"e": 2},
                resource=(3, 1),
                changes=updates,
            ),
            dt=2**-10,
        ),
    )


def scalar_pass(inputs: GeometryStageInputs) -> dict[str, Fraction]:
    """Closed one-edge rational equations for kappa_M=0, without runtime calls."""
    p = inputs.geometry.reference.profile.params_resolved
    c = p.candidate
    assert isinstance(c, CandidateCParams)
    h0 = Fraction(2)
    tau, eta, chi, zeta = map(Fraction, (c.tau_C, c.eta_C, c.chi_C, c.zeta_C))
    gain = Fraction(p.geometry.kappa_H)
    difference = Fraction(inputs.current.C[1]) - Fraction(inputs.current.C[0])

    def point(h: Fraction) -> tuple[Fraction, Fraction]:
        response = 1 / (1 + 2 * tau * h)
        current = 2 * eta * 2 * h * difference / (1 - zeta * chi * response)
        return current, chi * response * current / h

    j0, flat0 = point(h0)
    h1 = h0 + gain * zeta * flat0**2
    j1, flat1 = point(h1)
    regenerated = h0 + gain * zeta * flat1**2
    return dict(
        predictor=j0,
        corrector=j1,
        geometry=h1,
        regenerated=regenerated,
        residual=h1 - regenerated,
        flat=flat0,
    )


def dense_pass(inputs: GeometryStageInputs) -> dict[str, Any]:
    """Literal star restrictions plus independent fixed-geometry equations."""
    ref = inputs.geometry.reference
    params = ref.profile.params_resolved
    candidate = params.candidate
    assert isinstance(candidate, CandidateCParams)
    graph = ref.graph
    stars = [
        [
            i
            for i, e in enumerate(graph.oriented_edges)
            if v in (e.tail_node_id, e.head_node_id)
        ]
        for v in graph.live_node_ids
    ]
    multiplicities = [
        sum(i in star for star in stars) for i in range(len(graph.oriented_edges))
    ]

    def source(point: dict[str, Any], h: Any) -> Any:
        flat = np.linalg.solve(h, point["read"])
        result = np.zeros_like(h)
        for star in stars:
            for i in star:
                for j in star:
                    result[i, j] += (
                        flat[i]
                        * flat[j]
                        / math.sqrt(multiplicities[i] * multiplicities[j])
                    )
        return candidate.zeta_C * result

    h0 = np.array(ref.pairings.one_form.matrix)
    pred = dense_current_oracle(inputs)
    h1 = h0 + params.geometry.kappa_H * source(pred, h0)
    corrected = replace(
        inputs, geometry=GRCV4Geometry(ref, OneFormHodge(graph, tuple(map(tuple, h1))))
    )
    corr = dense_current_oracle(corrected)
    regenerated = h0 + params.geometry.kappa_H * source(corr, h1)
    cnext = (
        np.array(inputs.current.C)
        - inputs.dt * np.array(graph.incidence) @ corr["current"]
    )
    return dict(
        predictor=pred,
        corrector=corr,
        geometry=h1,
        residual=h1 - regenerated,
        resource=cnext,
    )


class CandidateCOSPassTests(unittest.TestCase):
    def test_rational_complete_scalar_pass_and_nonzero_split(self) -> None:
        inputs = os_fixture()
        expected, actual = scalar_pass(inputs), CandidateCOSPass(inputs)
        self.assertEqual(expected["predictor"], Fraction(-64, 7))
        self.assertGreater(abs(expected["residual"]), 0)
        for value, name in (
            (actual.predictor.current.values[0], "predictor"),
            (actual.corrector.current.values[0], "corrector"),
            (actual.corrector.inputs.geometry.one_form_hodge.matrix[0][0], "geometry"),
            (actual.residual.values[0][0], "residual"),
        ):
            self.assertAlmostEqual(value, float(expected[name]), delta=2e-14)
        self.assertTrue(actual.residual.admitted)
        self.assertNotEqual(actual.predictor.current, actual.corrector.current)

    def test_once_gated_flat_star_source_and_separate_controls(self) -> None:
        for candidate in (
            {},
            {"chi_C": 0},
            {"zeta_C": 0},
            {"kappa_M_C": 0},
            {"tau_C": 0},
        ):
            with self.subTest(candidate=candidate):
                inputs = os_fixture(candidate=candidate)
                expected, actual = scalar_pass(inputs), CandidateCOSPass(inputs)
                h = actual.corrector.inputs.geometry.one_form_hodge.matrix[0][0]
                self.assertAlmostEqual(h, float(expected["geometry"]), delta=1e-13)
                self.assertAlmostEqual(
                    actual.corrector.current.values[0],
                    float(expected["corrector"]),
                    delta=1e-13,
                )
                if candidate.get("chi_C") == 0 or candidate.get("zeta_C") == 0:
                    self.assertEqual(h, 2)
                    self.assertEqual(actual.residual.values, ((0,),))
        active = CandidateCOSPass(os_fixture())
        # Raw physical current and ungated read would each give a different K4.
        flat = active.predictor.read.causal_flat.values[0]
        self.assertNotEqual(flat, active.predictor.read.flux.values[0])
        self.assertNotEqual(flat, active.predictor.read.ungated_flat.values[0])

    def test_dense_multigraph_chain_and_signed_coordinate_covariance(self) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            (
                OrientedEdge("ab", "a", "b"),
                OrientedEdge("ac", "a", "c"),
                OrientedEdge("parallel", "a", "b"),
                OrientedEdge("loop", "c", "c"),
            ),
        )
        weights: dict[str, float] = {"ab": 2, "ac": 3, "parallel": 4, "loop": 5}
        inputs = replace(
            current_fixture(
                graph=graph,
                weights=weights,
                resource=(1, 2, 4, 7),
                changes={
                    "candidate": {"Lambda_C": 1, "kappa_M_C": 0.4},
                    "geometry": {"kappa_H": 0.0001},
                    "realization": {"tolerance": 1},
                    "charge": {"absolute_tolerance": 1e-11},
                },
            ),
            dt=1e-6,
        )
        expected, result = dense_pass(inputs), ProvisionalCandidateCOSStep(inputs)
        assert result.os_pass is not None
        np.testing.assert_allclose(
            result.os_pass.corrector.current.values,
            expected["corrector"]["current"],
            rtol=2e-12,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            result.os_pass.residual.values, expected["residual"], rtol=2e-10, atol=1e-12
        )
        np.testing.assert_allclose(
            result.resource.provisional_state.C,
            expected["resource"],
            rtol=2e-14,
            atol=0,
        )
        self.assertEqual(result.resource.provisional_state.C[3], 7)
        order, vertices, signs = (3, 1, 0, 2), (2, 0, 3, 1), (-1, 1, -1, 1)
        edges = tuple(graph.oriented_edges[i] for i in order)
        transformed_graph = GRCV4Graph(
            tuple(graph.live_node_ids[i] for i in vertices),
            tuple(
                OrientedEdge(
                    e.edge_id,
                    e.tail_node_id if sign == 1 else e.head_node_id,
                    e.head_node_id if sign == 1 else e.tail_node_id,
                )
                for e, sign in zip(edges, signs, strict=True)
            ),
        )
        other = replace(
            current_fixture(
                graph=transformed_graph,
                weights=weights,
                resource=tuple(inputs.current.C[i] for i in vertices),
                changes={
                    "candidate": {"Lambda_C": 1, "kappa_M_C": 0.4},
                    "geometry": {"kappa_H": 0.0001},
                    "realization": {"tolerance": 1},
                    "charge": {"absolute_tolerance": 1e-11},
                },
            ),
            dt=inputs.dt,
        )
        moved = ProvisionalCandidateCOSStep(other)
        assert moved.os_pass is not None
        expected_j = [
            result.os_pass.corrector.current.values[i] * s
            for i, s in zip(order, signs, strict=True)
        ]
        np.testing.assert_allclose(
            moved.os_pass.corrector.current.values, expected_j, rtol=2e-12, atol=1e-12
        )
        np.testing.assert_allclose(
            moved.resource.provisional_state.C,
            np.array(result.resource.provisional_state.C)[list(vertices)],
            rtol=2e-14,
            atol=0,
        )

    def test_exact_norm_boundary_uses_reference_metric_and_offdiagonals(self) -> None:
        inputs = os_fixture(realization={"tolerance": 0.5})
        ref = inputs.geometry.reference

        def geometry(h: float) -> GRCV4Geometry:
            return GRCV4Geometry(ref, OneFormHodge(ref.graph, ((h,),)))

        self.assertTrue(OSSplitResidual(geometry(3), geometry(2)).admitted)
        self.assertFalse(
            OSSplitResidual(geometry(math.nextafter(3, math.inf)), geometry(2)).admitted
        )
        self.assertTrue(
            OSSplitResidual(geometry(math.nextafter(3, 0)), geometry(2)).admitted
        )
        # Unit graph edge l2 norm of [[0,.6],[.6,0]] is .6: diagonal-only is wrong.
        pair = current_fixture(
            weights={"a": 1, "z": 1}, changes={"realization": {"tolerance": 0.5}}
        ).geometry.reference
        original = GRCV4Geometry(pair, OneFormHodge(pair.graph, ((1, 0), (0, 1))))
        perturbed = GRCV4Geometry(pair, OneFormHodge(pair.graph, ((1, 0.6), (0.6, 1))))
        self.assertFalse(OSSplitResidual(original, perturbed).admitted)

    def test_seeded_rank_two_signed_coupling_passes_match_independent_equations(
        self,
    ) -> None:
        graph = GRCV4Graph(
            ("a", "b", "c"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("bc", "b", "c")),
        )
        rng = np.random.default_rng(944)
        for case in range(8):
            weights = {"ab": float(rng.uniform(0.5, 2)), "bc": float(rng.uniform(2, 4))}
            b = np.array(graph.incidence)
            spectrum = np.linalg.eigvalsh(b @ np.diag(list(weights.values())) @ b.T)
            inputs = replace(
                current_fixture(
                    graph=graph,
                    weights=weights,
                    resource=tuple(map(float, rng.uniform(1, 4, 3))),
                    changes={
                        "candidate": {
                            "Lambda_C": float((spectrum[1] + spectrum[2]) / 2),
                            "kappa_M_C": (-1) ** case * 0.7,
                            "zeta_C": 0.3,
                            "chi_C": 0.4,
                        },
                        "geometry": {"kappa_H": (-1) ** (case // 2) * 1e-5},
                        "realization": {"tolerance": 1},
                        "charge": {"absolute_tolerance": 1e-11},
                    },
                ),
                dt=1e-6,
            )
            with self.subTest(case=case):
                expected, actual = (
                    dense_pass(inputs),
                    ProvisionalCandidateCOSStep(inputs),
                )
                assert actual.os_pass is not None
                self.assertEqual(actual.os_pass.corrector.algebra.selector.rank, 2)
                np.testing.assert_allclose(
                    actual.os_pass.corrector.current.values,
                    expected["corrector"]["current"],
                    rtol=3e-12,
                    atol=2e-12,
                )
                np.testing.assert_allclose(
                    actual.resource.provisional_state.C,
                    expected["resource"],
                    rtol=2e-14,
                    atol=0,
                )

    def test_norm_admission_does_not_underflow_or_overflow(self) -> None:
        for h, t, difference in ((1e-300, 1e-30, 1e-310), (1e300, 1e-30, 1e290)):
            inputs = current_fixture(
                graph=os_fixture().geometry.reference.graph,
                weights={"e": h},
                changes={"realization": {"tolerance": t}},
            )
            ref = inputs.geometry.reference
            a = GRCV4Geometry(ref, OneFormHodge(ref.graph, ((h + difference,),)))
            self.assertFalse(OSSplitResidual(a, ref.geometry()).admitted)
        ref = os_fixture(realization={"tolerance": 0}).geometry.reference
        adjacent = GRCV4Geometry(
            ref, OneFormHodge(ref.graph, ((math.nextafter(2, math.inf),),))
        )
        self.assertFalse(OSSplitResidual(adjacent, ref.geometry()).admitted)

    def test_positive_bounded_residual_is_accepted_but_zero_tolerance_rejects(
        self,
    ) -> None:
        result = CandidateCOSPass(os_fixture())
        self.assertGreater(abs(result.residual.values[0][0]), 0)
        with self.assertRaisesRegex(
            OSStageError, "split_residual.*no second iteration"
        ):
            CandidateCOSPass(os_fixture(realization={"tolerance": 0}))

    def test_stage_count_rebuilds_corrector_without_consuming_residual_geometry(
        self,
    ) -> None:
        import pygrc.models.grc_v4_realizations as owner

        seen = []
        original = CandidateCCurrent

        def observe(inputs: GeometryStageInputs) -> CandidateCCurrent:
            seen.append(inputs)
            return original(inputs)

        with (
            patch.object(owner, "CandidateCCurrent", side_effect=observe),
            patch.object(owner, "H_profile", wraps=getattr(owner, "H_profile")) as h,
        ):
            result = CandidateCOSPass(os_fixture())
        self.assertEqual([x.stage for x in seen], ["os_predictor", "os_corrector"])
        self.assertEqual(
            h.call_count, 2
        )  # one update and one residual operand, no third solve
        self.assertEqual(seen[0].current, seen[1].current)
        self.assertNotEqual(seen[0].geometry, seen[1].geometry)
        self.assertEqual(result.corrector.inputs.geometry, result.residual.geometry)
        self.assertNotEqual(
            result.corrector.inputs.geometry, result.residual.regenerated
        )

    def test_rank_change_cutoff_tie_and_current_singularity_reject(self) -> None:
        for changes, message in (
            ({"candidate": {"Lambda_C": 4}}, "cutoff"),
            ({"candidate": {"Lambda_C": 4.1}}, "stratum"),
            (
                {
                    "candidate": {"zeta_C": 3, "chi_C": 1},
                    "geometry": {"kappa_H": 1 / 24},
                },
                "singular",
            ),
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaisesRegex(ValueError, message),
            ):
                CandidateCOSPass(os_fixture(**changes))

    def test_geometry_domain_loss_is_not_repaired(self) -> None:
        with self.assertRaisesRegex(OSStageError, "geometry_update"):
            CandidateCOSPass(os_fixture(geometry={"kappa_H": -4}))

    def test_duration_does_not_scale_or_iterate_the_structural_pass(self) -> None:
        before = os_fixture()
        results = [
            CandidateCOSPass(replace(before, dt=t))
            for t in (math.ulp(0.0), 0.01, 1e300)
        ]
        for result in results[1:]:
            self.assertEqual(result.corrector.current, results[0].corrector.current)
            self.assertEqual(result.residual, results[0].residual)
        for t in (0, -1):
            with self.assertRaises(ValueError):
                CandidateCOSPass(replace(before, dt=t))

    def test_equal_endpoint_ranks_do_not_hide_an_interior_selector_crossing(
        self,
    ) -> None:
        from pygrc.models.grc_v4_realizations import _selector_path_segments

        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("cd", "c", "d")),
        )
        before = current_fixture(
            graph=graph,
            weights={"ab": 0.5, "cd": 2},
            resource=(1, 1, 1, 1),
            changes={"candidate": {"Lambda_C": 3}},
        )
        after = replace(
            before,
            geometry=GRCV4Geometry(
                before.geometry.reference, OneFormHodge(graph, ((2, 0), (0, 0.5)))
            ),
        )
        a, b = CandidateCCurrent(before), CandidateCCurrent(after)
        self.assertEqual(a.algebra.selector.rank, b.algebra.selector.rank)
        # Nonzero eigenvalues go from (1,4) to (4,1), through (2.5,2.5).
        with self.assertRaisesRegex(ValueError, "crosses selector"):
            _selector_path_segments(a, b)
        safe = replace(
            before,
            geometry=GRCV4Geometry(
                before.geometry.reference, OneFormHodge(graph, ((0.6, 0), (0, 1.9)))
            ),
        )
        self.assertGreater(_selector_path_segments(a, CandidateCCurrent(safe)), 0)

    def test_pass_and_step_reject_interior_crossing_before_residual_or_resource(
        self,
    ) -> None:
        import pygrc.models.grc_v4_realizations as owner
        import pygrc.models.grc_v4_step as step_owner

        graph = GRCV4Graph(
            ("a", "b", "c", "d"),
            (OrientedEdge("ab", "a", "b"), OrientedEdge("cd", "c", "d")),
        )
        # Injected source-geometry controls, not naturally generated K4 claims.
        # The two crossing directions exchange eigenvalues (1,4) and (4,1);
        # the midpoint has (2.5,2.5). Safe mixed directions stay below/above 3.
        for reverse in (False, True):
            weights = (2, 0.5) if reverse else (0.5, 2)
            before = current_fixture(
                graph=graph,
                weights=dict(zip(("ab", "cd"), weights)),
                resource=(1, 1, 1, 1),
                changes={
                    "candidate": {"Lambda_C": 3},
                    "geometry": {"kappa_H": 1},
                    "realization": {"tolerance": 1e9},
                },
            )
            original = canonical_json_bytes(before.to_payload())
            for crosses in (True, False):
                diagonal = (2, 0.5) if crosses else (0.6, 1.9)
                if reverse:
                    diagonal = diagonal[::-1]
                after = GRCV4Geometry(
                    before.geometry.reference,
                    OneFormHodge(graph, ((diagonal[0], 0), (0, diagonal[1]))),
                )
                a = CandidateCCurrent(before)
                b = CandidateCCurrent(replace(before, geometry=after))
                self.assertEqual(a.algebra.selector.rank, b.algebra.selector.rank)
                for entry in (CandidateCOSPass, ProvisionalCandidateCOSStep):
                    with (
                        self.subTest(reverse=reverse, crosses=crosses, entry=entry),
                        patch.object(
                            owner, "_source_geometry", return_value=after
                        ) as source,
                        patch.object(
                            owner, "OSSplitResidual", wraps=OSSplitResidual
                        ) as residual,
                        patch.object(
                            step_owner,
                            "ProvisionalResourceStep",
                            wraps=step_owner.ProvisionalResourceStep,
                        ) as resource,
                        patch.object(
                            step_owner,
                            "provisional_continuity",
                            wraps=getattr(step_owner, "provisional_continuity"),
                        ) as writer,
                    ):
                        if crosses:
                            with self.assertRaisesRegex(
                                OSStageError, "crosses selector cutoff"
                            ) as failure:
                                entry(before)
                            self.assertEqual(failure.exception.substage, "os_corrector")
                            self.assertEqual(source.call_count, 1)
                            residual.assert_not_called()
                            resource.assert_not_called()
                            writer.assert_not_called()
                        else:
                            # Passing control prevents blanket mixed-path rejection.
                            entry(before)
                            self.assertEqual(source.call_count, 2)
                            residual.assert_called_once()
                            count = int(entry is ProvisionalCandidateCOSStep)
                            self.assertEqual(resource.call_count, count)
                            self.assertEqual(writer.call_count, count)
                        self.assertEqual(
                            canonical_json_bytes(before.to_payload()), original
                        )

    def test_loop_only_and_zero_current_have_no_spurious_structural_source(
        self,
    ) -> None:
        graph = GRCV4Graph(("v",), (OrientedEdge("loop", "v", "v"),))
        before = current_fixture(
            graph=graph,
            weights={"loop": 2},
            resource=(3,),
            changes={"realization": {"tolerance": 0}},
        )
        result = ProvisionalCandidateCOSStep(before)
        assert result.os_pass is not None
        self.assertEqual(result.os_pass.corrector.current.values, (0,))
        self.assertEqual(result.os_pass.residual.values, ((0,),))
        self.assertEqual(result.resource.provisional_state.C, (3,))

    def test_foreign_stage_geometry_profile_and_norm_fail_closed(self) -> None:
        before = os_fixture()
        for bad in (
            replace(before, stage="os_corrector"),
            replace(
                before,
                geometry=GRCV4Geometry(
                    before.geometry.reference,
                    OneFormHodge(before.geometry.reference.graph, ((3,),)),
                ),
            ),
            current_fixture(realization="CI"),
            os_fixture(realization={"split_residual_norm_id": "unknown"}),
        ):
            with self.subTest(stage=bad.stage), self.assertRaises(ValueError):
                CandidateCOSPass(bad)
        with self.assertRaises(TypeError):
            CandidateCOSPass(before.to_payload())  # type: ignore[arg-type]


class CandidateCOSStepTests(unittest.TestCase):
    def test_one_corrector_resource_write_and_fresh_final_chain(self) -> None:
        import pygrc.models.grc_v4_step as owner

        inputs = os_fixture(candidate={"kappa_M_C": 0.5})
        before = canonical_json_bytes(inputs.to_payload())
        with patch.object(
            owner,
            "provisional_continuity",
            wraps=getattr(owner, "provisional_continuity"),
        ) as writer:
            result = ProvisionalCandidateCOSStep(inputs)
        assert result.os_pass is not None and result.final is not None
        self.assertEqual(writer.call_count, 1)
        self.assertEqual(writer.call_args.args[1], result.os_pass.corrector.current)
        self.assertEqual(result.resource.continuity_evaluations, 1)
        final = result.final
        self.assertEqual(final.inputs.current, result.resource.provisional_state)
        self.assertEqual(final.inputs.stage, "post_continuity")
        self.assertEqual(
            final.inputs.geometry, result.os_pass.corrector.inputs.geometry
        )
        self.assertNotEqual(
            final.algebra.baseline, result.os_pass.corrector.algebra.baseline
        )
        self.assertIsNot(
            final.algebra.selector, result.os_pass.corrector.algebra.selector
        )
        expected = dense_current_oracle(final.inputs)
        np.testing.assert_allclose(
            final.algebra.baseline.values, expected["j0"], rtol=2e-13, atol=1e-13
        )
        self.assertEqual(canonical_json_bytes(inputs.to_payload()), before)
        self.assertIsNone(result.resource.provisional_state.W_A)
        self.assertIsNone(result.resource.provisional_state.Z_4)
        self.assertEqual(
            result.next_inputs.geometry, inputs.geometry.reference.geometry()
        )

    def test_next_beat_restarts_at_reference_and_preserves_reset(self) -> None:
        first = ProvisionalCandidateCOSStep(os_fixture())
        second = ProvisionalCandidateCOSStep(first.next_inputs)
        assert first.os_pass is not None and second.os_pass is not None
        self.assertNotEqual(
            first.os_pass.corrector.inputs.geometry,
            second.os_pass.predictor.inputs.geometry,
        )
        self.assertEqual(
            second.os_pass.predictor.inputs.current, first.resource.provisional_state
        )
        self.assertEqual(second.next_inputs.reset, first.inputs.reset)
        self.assertEqual(second.next_inputs.step_index, 2)
        self.assertEqual(second.next_inputs.time, 2 * first.inputs.dt)
        self.assertEqual(second.next_inputs.receipt_ids, first.inputs.receipt_ids)
        with self.assertRaises(FrozenInstanceError):
            first.next_inputs.time = 7  # type: ignore[misc]

    def test_zero_duration_admits_current_and_reset_without_pass_or_writer(
        self,
    ) -> None:
        import pygrc.models.grc_v4_step as owner

        inputs = replace(os_fixture(), dt=0)
        with (
            patch.object(
                owner,
                "CandidateCOSPass",
                side_effect=AssertionError("unexpected OS pass"),
            ),
            patch.object(
                owner,
                "provisional_continuity",
                side_effect=AssertionError("unexpected writer"),
            ),
        ):
            result = ProvisionalCandidateCOSStep(inputs)
        self.assertIsNone(result.os_pass)
        self.assertIsNone(result.final)
        self.assertEqual(result.next_inputs, inputs)
        self.assertEqual(result.resource.continuity_evaluations, 0)
        for bad in (
            replace(inputs, Q_target=999),
            replace(os_fixture(candidate={"tau_C": 0, "chi_C": 1, "zeta_C": 1}), dt=0),
            replace(inputs, reset=GRCV4AuthoritativeState((4, 1), None, None)),
        ):
            with self.assertRaises(ValueError):
                ProvisionalCandidateCOSStep(bad)

    def test_subnormal_positive_duration_runs_full_pass_even_without_clock_motion(
        self,
    ) -> None:
        inputs = replace(os_fixture(), dt=math.ulp(0.0), time=1)
        result = ProvisionalCandidateCOSStep(inputs)
        self.assertIsNotNone(result.os_pass)
        self.assertIsNotNone(result.final)
        self.assertEqual(result.resource.continuity_evaluations, 1)
        self.assertEqual(result.next_inputs.step_index, 1)
        self.assertEqual(result.next_inputs.time, 1)

    def test_resource_domain_charge_and_clock_failures_preserve_all_inputs(
        self,
    ) -> None:
        for inputs in (
            replace(os_fixture(), dt=1),
            replace(os_fixture(), Q_target=0),
            replace(os_fixture(), time=1.7e308, dt=1.7e308),
            replace(os_fixture(), dt=1.7e308),
        ):
            before = canonical_json_bytes(inputs.to_payload())
            with self.subTest(dt=inputs.dt), self.assertRaises(ValueError):
                ProvisionalCandidateCOSStep(inputs)
            self.assertEqual(canonical_json_bytes(inputs.to_payload()), before)

    def test_final_reconstruction_failure_returns_no_partial_success(self) -> None:
        import pygrc.models.grc_v4_step as owner

        inputs = os_fixture()
        before = canonical_json_bytes(inputs.to_payload())
        original = CandidateCCurrent

        def fail_final(stage: GeometryStageInputs) -> CandidateCCurrent:
            if stage.stage == "post_continuity":
                raise ValueError("injected final admission failure")
            return original(stage)

        with (
            patch.object(owner, "CandidateCCurrent", side_effect=fail_final),
            self.assertRaisesRegex(ResourceBoundaryError, "injected final") as failure,
        ):
            ProvisionalCandidateCOSStep(inputs)
        self.assertEqual(failure.exception.stage, "final_reconstruction")
        self.assertEqual(canonical_json_bytes(inputs.to_payload()), before)

    def test_extreme_finite_duration_with_zero_current_still_writes_once(self) -> None:
        before = replace(
            os_fixture(),
            current=GRCV4AuthoritativeState((2, 2), None, None),
            dt=1.7e308,
        )
        result = ProvisionalCandidateCOSStep(before)
        self.assertEqual(result.resource.continuity_evaluations, 1)
        self.assertEqual(result.resource.provisional_state.C, (2, 2))
        self.assertEqual(result.next_inputs.time, 1.7e308)
        self.assertEqual(result.next_inputs.step_index, 1)


_P944_METHODS = (
    "CandidateCOSPassTests.test_rational_complete_scalar_pass_and_nonzero_split",
    "CandidateCOSPassTests.test_once_gated_flat_star_source_and_separate_controls",
    "CandidateCOSPassTests.test_dense_multigraph_chain_and_signed_coordinate_covariance",
    "CandidateCOSPassTests.test_exact_norm_boundary_uses_reference_metric_and_offdiagonals",
    "CandidateCOSPassTests.test_seeded_rank_two_signed_coupling_passes_match_independent_equations",
    "CandidateCOSPassTests.test_norm_admission_does_not_underflow_or_overflow",
    "CandidateCOSPassTests.test_positive_bounded_residual_is_accepted_but_zero_tolerance_rejects",
    "CandidateCOSPassTests.test_stage_count_rebuilds_corrector_without_consuming_residual_geometry",
    "CandidateCOSPassTests.test_rank_change_cutoff_tie_and_current_singularity_reject",
    "CandidateCOSPassTests.test_geometry_domain_loss_is_not_repaired",
    "CandidateCOSPassTests.test_duration_does_not_scale_or_iterate_the_structural_pass",
    "CandidateCOSPassTests.test_equal_endpoint_ranks_do_not_hide_an_interior_selector_crossing",
    "CandidateCOSPassTests.test_pass_and_step_reject_interior_crossing_before_residual_or_resource",
    "CandidateCOSPassTests.test_loop_only_and_zero_current_have_no_spurious_structural_source",
    "CandidateCOSPassTests.test_foreign_stage_geometry_profile_and_norm_fail_closed",
    "CandidateCOSStepTests.test_one_corrector_resource_write_and_fresh_final_chain",
    "CandidateCOSStepTests.test_next_beat_restarts_at_reference_and_preserves_reset",
    "CandidateCOSStepTests.test_zero_duration_admits_current_and_reset_without_pass_or_writer",
    "CandidateCOSStepTests.test_subnormal_positive_duration_runs_full_pass_even_without_clock_motion",
    "CandidateCOSStepTests.test_resource_domain_charge_and_clock_failures_preserve_all_inputs",
    "CandidateCOSStepTests.test_final_reconstruction_failure_returns_no_partial_success",
    "CandidateCOSStepTests.test_extreme_finite_duration_with_zero_current_still_writes_once",
)
_RESOURCE_METHODS = (
    "ResourceBoundaryTests.test_zero_rounded_residual_can_hide_exact_stored_sum_growth",
    "ResourceBoundaryTests.test_distinct_live_reset_resources_and_histories_across_ten_declarations",
    "ResourceBoundaryTests.test_cycle_circulation_with_same_resource_cannot_borrow_selection",
    "ResourceBoundaryTests.test_exact_zero_divergence_can_overflow_before_cancellation",
    "ResourceBoundaryTests.test_ten_declarations_write_once_preserve_nonresource_authority",
    "ResourceBoundaryTests.test_every_failed_solver_disposition_blocks_fallback_before_continuity",
    "ResourceBoundaryTests.test_predictor_and_postcontinuity_cannot_supply_selected_current",
    "ResourceBoundaryTests.test_full_prestate_clock_reset_ledger_and_request_are_bound",
    "ResourceBoundaryTests.test_corrected_hodge_is_allowed_with_same_reference_and_authority",
    "ResourceBoundaryTests.test_joint_selection_must_equal_exact_bound_trial",
    "ResourceBoundaryTests.test_prestate_and_reset_charge_gate_precedes_current_consumption",
    "ResourceBoundaryTests.test_postcontinuity_negative_and_overflow_reject_before_exposure",
    "ResourceBoundaryTests.test_conservative_real_transfer_can_fail_the_binary64_charge_gate",
    "ResourceBoundaryTests.test_zero_duration_is_locally_admitted_identity_without_selection",
    "ResourceBoundaryTests.test_consumer_requires_independent_exact_inputs_even_if_output_matches",
    "ResourceBoundaryTests.test_selection_reconstruction_revalidates_roles_shape_and_forged_types",
    "ResourceBoundaryTests.test_charge_values_fit_frozen_receipt_without_inventing_commit",
    "ResourceReconstructionTests.test_resource_reconstruction_outside_checkout_with_three_hash_seeds",
)


def capture_p944(output: str) -> int:
    """One source-bound focused run; replay source comes from Git history."""
    from datetime import datetime, timezone
    import hashlib
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import platform
    import subprocess
    from tests.models.test_grc_v4_candidate_c import _p941_execute

    root = Path(__file__).resolve().parents[2]
    generated = (
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated"
    )
    destination = (root / output).resolve()
    if (
        not destination.is_relative_to(generated.resolve())
        or destination == generated.resolve()
        or destination.exists()
    ):
        raise ValueError(
            "capture requires a fresh repository-local generated destination"
        )
    base = "4a3a7ee10e60cc2ddb274f868d8d1177b07b431f"
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"], cwd=root, check=True
    )
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "uv.lock",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    ]
    overrides = {
        "src/pygrc/models/grc_v4_realizations.py",
        "src/pygrc/models/grc_v4_step.py",
        "tests/models/test_grc_v4_realizations.py",
    }

    def snapshot() -> dict[str, str]:
        names = subprocess.check_output(
            [
                "git",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                *scopes,
            ],
            cwd=root,
            text=True,
        ).splitlines()
        return {
            n: hashlib.sha256((root / n).read_bytes()).hexdigest()
            for n in sorted(set(names))
        }

    before = snapshot()
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", base, "--", *scopes], cwd=root, text=True
        ).splitlines()
    )
    base_names = set(
        subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", base, "--", *scopes],
            cwd=root,
            text=True,
        ).splitlines()
    )
    if (changed | (set(before) - base_names)) - overrides or base_names - set(before):
        raise ValueError("source differs outside the P9-4.4 reconstruction envelope")
    prior_path = "implementation/phase-9-grcv4/evidence/P9-4.3/audit-followup/run.json"
    prior = json.loads(
        subprocess.check_output(["git", "show", base + ":" + prior_path], cwd=root)
    )
    required = (
        set(prior["required_ids"])
        | {"tests.models.test_grc_v4_realizations." + n for n in _P944_METHODS}
        | {"tests.models.test_grc_v4_step." + n for n in _RESOURCE_METHODS}
    )
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    started = datetime.now(timezone.utc).isoformat()
    record = {
        "schema": "phase9_leaf_focused_run_v1",
        "iteration_id": "P9-4.4",
        "source": {
            "base_commit": base,
            "scopes": scopes,
            "overrides_sha256": {n: before[n] for n in sorted(overrides)},
            "manifest_sha256": hashlib.sha256(canonical_json_bytes(before)).hexdigest(),
            "file_count": len(before),
            "reconstruction": "Overlay only the listed hash-matching source files from the commit containing this run onto base_commit; verify the scoped manifest. Before commit, use the reviewed working tree.",
        },
        "required_ids": sorted(required),
        "started_utc": started,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            key: os.environ.get(key)
            for key in ("PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        },
        "replay_command": [
            ".venv/bin/python",
            "-m",
            "tests.models.test_grc_v4_realizations",
            "--capture-p944",
            str(destination.relative_to(root)),
        ],
        "claim_ceiling": "Provisional C_OS pass, split admission, one resource write and final-C reconstruction. No lifecycle commit, authenticated receipts, profile conformance or cross-platform bitwise claim.",
        "numerical_policy": "Inherited C stage/star/geometry binary64 policy; exact reference-relative split tolerance via symmetric inertia; fixed-rank affine selector path certification with a 256-bisection fail-closed ceiling. Positive subnormal durations are never classified as zero.",
    }
    record.update(_p941_execute(root, before, required, suite, snapshot))
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["live_source_check_limits"] = (
        "Same before/after live-code and disk attribution checks as accepted P9-4.3 capture; not hostile-interpreter attestation. Existing dependency environment, no fresh dependency installation."
    )
    if record.get("loaded_sources_before") == record.get("loaded_sources_after"):
        record["loaded_sources"] = record.pop("loaded_sources_before")
        record.pop("loaded_sources_after")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(json.dumps(record, indent=2) + "\n")
    print("P9-4.4", record["status"], json.dumps(record.get("results", {})), flush=True)
    if record["status"] != "passed":
        print(record.get("capture_error", record.get("failure_output", "")), flush=True)
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p944":
        raise SystemExit(capture_p944(sys.argv[2]))
    unittest.main()
