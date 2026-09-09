"""Independent equations and adversarial staging for bounded A_OS/C_OS steps."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import math
from typing import Any, cast
import unittest
from unittest.mock import patch

import numpy as np

from pygrc.models.grc_v4_candidate_c import CandidateCCurrent, CandidateCStageError
from pygrc.models.grc_v4_candidate_a import (
    CandidateACurrent,
    CandidateAStageError,
    CandidateAWriter,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_codec import V4SchemaError
from pygrc.models.grc_v4_geometry import (
    GRCV4Geometry,
    GRCV4Graph,
    GeometryStageInputs,
    OneFormHodge,
    OrientedEdge,
)
from pygrc.models.grc_v4_realizations import (
    CandidateCOSPass,
    CandidateAOSPass,
    OSSplitResidual,
    OSStageError,
)
from pygrc.models.grc_v4_profile import CandidateCParams
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep, ResourceBoundaryError
from pygrc.models.grc_v4_step import ProvisionalCandidateAOSStep
from tests.models.test_grc_v4_candidate_c import current_fixture, dense_current_oracle
from tests.models.test_grc_v4_candidate_a import (
    current_fixture as a_current_fixture,
    scalar_oracle as a_conductance_oracle,
    log_writer_oracle as a_writer_oracle,
)


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

        for fault in (
            CandidateCStageError("domain_failure", "injected final admission failure"),
            ValueError("injected final admission failure"),
        ):

            def fail_final(stage: GeometryStageInputs) -> CandidateCCurrent:
                if stage.stage == "post_continuity":
                    raise fault
                return original(stage)

            with (
                self.subTest(kind=type(fault)),
                patch.object(owner, "CandidateCCurrent", side_effect=fail_final),
            ):
                if isinstance(fault, CandidateCStageError):
                    with self.assertRaisesRegex(
                        ResourceBoundaryError, "injected final"
                    ) as failure:
                        ProvisionalCandidateCOSStep(inputs)
                    self.assertEqual(failure.exception.stage, "final_reconstruction")
                    self.assertEqual(failure.exception.code, "domain_failure")
                    self.assertIs(failure.exception.__cause__, fault)
                else:
                    with self.assertRaises(ValueError) as programmer:
                        ProvisionalCandidateCOSStep(inputs)
                    self.assertIs(programmer.exception, fault)
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


def a_os_fixture(**options):
    changes = {"geometry": {"kappa_H": 0.125}, "realization": {"tolerance": 10.0}}
    for group, values in options.pop("changes", {}).items():
        changes.setdefault(group, {}).update(values)
    return a_current_fixture(
        dt=options.pop("dt", 0.001),
        kappa_Ah=options.pop("kappa_Ah", 0.25),
        changes=changes,
        **options,
    )


def a_scalar_pass(inputs):
    """Independent one-edge rational law with constant unit G_W.

    This is the real-arithmetic equation oracle, not the runtime's staged
    binary64 recipe; comparisons allow local rounding error on modest inputs.
    """
    p = inputs.geometry.reference.profile.params_resolved
    a = p.candidate
    w, eta, kc, kh, chi, zeta, gain = map(
        Fraction,
        (
            inputs.current.W_A[0],
            a.eta,
            a.kappa_c,
            a.kappa_Ah,
            a.chi_A,
            a.zeta_A,
            p.geometry.kappa_H,
        ),
    )
    difference = Fraction(inputs.current.C[0]) - Fraction(inputs.current.C[1])
    q = (w - 1) / (w + 1)
    d = 1 - zeta * chi * q

    def point(h):
        phi = (kc * w + kh * (h - 1)) * difference
        baseline = -eta * w * 2 * phi
        current = baseline / d
        return baseline, current, chi * q * current / h

    pred = point(Fraction(1))
    h = 1 + gain * zeta * pred[2] ** 2
    corr = point(h)
    regen = 1 + gain * zeta * corr[2] ** 2
    return {
        "predictor": pred,
        "corrector": corr,
        "h": h,
        "regenerated": regen,
        "residual": h - regen,
    }


def a_dense_pass(inputs, backend):
    """Independent matrix/Decimal equations and explicit normalized stars.

    No runtime A current, realization, resource, writer or geometry helper is
    used. Decimal WLS/G_W and multiplicative interpolation oracles are shared
    with the independent A initialization tests, not production evaluators.
    """
    ref = inputs.geometry.reference
    a = ref.profile.params_resolved.candidate
    graph, C, W = ref.graph, np.array(inputs.current.C), np.array(inputs.current.W_A)
    B = np.zeros((len(C), len(W)))
    stars = [[] for _ in C]
    for e, edge in enumerate(graph.oriented_edges):
        u, v = graph.node_index(edge.tail_node_id), graph.node_index(edge.head_node_id)
        B[u, e] += 1
        B[v, e] -= 1
        for node in {u, v}:
            stars[node].append(e)
    multiplicity = [sum(e in star for star in stars) for e in range(len(W))]
    href = np.array(ref.pairings.one_form.matrix)

    def point(h):
        phi = (
            a.kappa_c * B @ np.diag(W) @ B.T @ C + a.kappa_Ah * B @ (h - href) @ B.T @ C
        )
        baseline = -a.eta * W * (B.T @ phi)
        _, hat = a_conductance_oracle(ref, backend, tuple(C), tuple(baseline))
        q = (W - hat) / (W + hat)
        current = baseline / (1 - a.zeta_A * a.chi_A * q)
        flat = np.linalg.solve(h, a.chi_A * q * current)
        source = np.zeros_like(h)
        for star in stars:
            for i in star:
                for j in star:
                    source[i, j] += (
                        flat[i] * flat[j] / math.sqrt(multiplicity[i] * multiplicity[j])
                    )
        return dict(
            baseline=baseline, current=current, hat=hat, source=a.zeta_A * source
        )

    pred = point(href)
    h = href + ref.profile.params_resolved.geometry.kappa_H * pred["source"]
    corr = point(h)
    residual = h - href - ref.profile.params_resolved.geometry.kappa_H * corr["source"]
    final_C = C - inputs.dt * B @ corr["current"]
    _, target = a_conductance_oracle(
        ref, backend, tuple(final_C), tuple(corr["current"])
    )
    written = a_writer_oracle(tuple(W), target, inputs.dt, a.tau_A)
    return dict(
        predictor=pred,
        corrector=corr,
        h=h,
        residual=residual,
        C=final_C,
        W=written,
        target=target,
    )


class CandidateAOSIntegrationTests(unittest.TestCase):
    def test_scalar_pass_and_complete_numerical_step_against_equations(self):
        before, backend = a_os_fixture()
        expected = a_scalar_pass(before)
        self.assertEqual(expected["predictor"][1], Fraction(-16, 7))
        self.assertEqual(expected["h"], Fraction(149, 147))
        self.assertEqual(expected["corrector"][1], Fraction(-2360, 1029))
        step = ProvisionalCandidateAOSStep(before, backend)
        passed = step.os_pass
        for actual, value in (
            (passed.predictor.current.values[0], expected["predictor"][1]),
            (passed.corrector.current.values[0], expected["corrector"][1]),
            (
                passed.corrector.inputs.geometry.one_form_hodge.matrix[0][0],
                expected["h"],
            ),
            (passed.residual.values[0][0], expected["residual"]),
        ):
            self.assertAlmostEqual(actual, float(value), delta=2e-14)
        self.assertNotEqual(passed.residual.values, ((0.0,),))
        j = passed.corrector.current.values[0]
        self.assertEqual(
            step.next_inputs.current.C,
            (
                float(Fraction(3) - Fraction(before.dt) * Fraction(j)),
                float(Fraction(1) + Fraction(before.dt) * Fraction(j)),
            ),
        )
        self.assertEqual(
            step.next_inputs.current.W_A,
            a_writer_oracle((2.0,), (1.0,), before.dt, 1.0),
        )
        self.assertEqual(
            (step.next_inputs.step_index, step.next_inputs.time), (1, before.dt)
        )
        self.assertEqual(step.next_inputs.reset, before.reset)
        self.assertEqual(step.next_inputs.geometry, before.geometry)

    def test_one_pass_one_continuity_one_writer_and_no_new_weight_feedback(self):
        before, backend = a_os_fixture(gamma=0.125)
        with (
            patch(
                "pygrc.models.grc_v4_realizations.CandidateACurrent",
                wraps=CandidateACurrent,
            ) as currents,
            patch(
                "pygrc.models.grc_v4_realizations._selector_path_segments",
                side_effect=AssertionError("A has no C selector"),
            ),
            patch(
                "pygrc.models.grc_v4_step.CandidateAWriter", wraps=CandidateAWriter
            ) as writers,
        ):
            step = ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(
            [c.args[0].stage for c in currents.call_args_list],
            ["os_predictor", "os_corrector"],
        )
        self.assertEqual(writers.call_count, 1)
        self.assertEqual(step.resource.continuity_evaluations, 1)
        self.assertEqual(
            step.resource.selection.current, step.os_pass.corrector.current
        )
        for point in (step.os_pass.predictor, step.os_pass.corrector):
            self.assertEqual(point.inputs.current, before.current)
        self.assertNotEqual(step.writer.W_drv_A, step.os_pass.corrector.W_hat_A)
        self.assertNotEqual(step.next_inputs.current.W_A, before.current.W_A)
        self.assertEqual(step.final.inputs.current, step.next_inputs.current)
        self.assertEqual(step.restart.inputs.current, step.next_inputs.current)
        self.assertEqual(
            step.final.inputs.geometry, step.os_pass.corrector.inputs.geometry
        )
        self.assertEqual(step.restart.inputs.geometry, before.geometry)
        self.assertNotEqual(step.final.current, step.os_pass.corrector.current)

    def test_multigraph_all_channels_against_independent_dense_oracle(self):
        graph = GRCV4Graph(
            ("u", "v", "w", "i"),
            (
                OrientedEdge("a", "u", "v"),
                OrientedEdge("b", "v", "u"),
                OrientedEdge("c", "v", "w"),
                OrientedEdge("loop", "u", "u"),
            ),
        )
        before, backend = a_os_fixture(
            graph=graph,
            C=(3.0, 1.0, 2.0, 7.0),
            W=(2.0, 0.5, 1.0, 3.0),
            alpha=0.125,
            beta=0.25,
            gamma=0.0625,
        )
        expected = a_dense_pass(before, backend)
        step = ProvisionalCandidateAOSStep(before, backend)
        for value, oracle in (
            (step.os_pass.predictor.current.values, expected["predictor"]["current"]),
            (step.os_pass.corrector.current.values, expected["corrector"]["current"]),
            (
                step.os_pass.corrector.inputs.geometry.one_form_hodge.matrix,
                expected["h"],
            ),
            (step.os_pass.residual.values, expected["residual"]),
            (step.next_inputs.current.C, expected["C"]),
            (step.next_inputs.current.W_A, expected["W"]),
            (step.writer.W_drv_A, expected["target"]),
        ):
            np.testing.assert_allclose(value, oracle, rtol=2e-13, atol=2e-14)
        self.assertEqual(step.os_pass.corrector.current.values[-1], 0.0)
        self.assertEqual(step.next_inputs.current.C[-1], 7.0)
        self.assertNotEqual(step.writer.descriptors, step.os_pass.corrector.descriptors)

    def test_chi_zeta_geometry_controls_preserve_direct_retained_path(self):
        for changes in (
            {"chi_A": 0.0},
            {"zeta_A": 0.0},
            {"changes": {"geometry": {"kappa_H": 0.0}}},
        ):
            with self.subTest(changes=changes):
                before, backend = a_os_fixture(**changes)
                step = ProvisionalCandidateAOSStep(before, backend)
                self.assertEqual(
                    step.os_pass.corrector.inputs.geometry, before.geometry
                )
                self.assertEqual(step.os_pass.residual.values, ((0.0,),))
                self.assertNotEqual(step.os_pass.corrector.current.values, (0.0,))
                self.assertNotEqual(step.next_inputs.current.W_A, before.current.W_A)

    def test_split_tolerance_equality_adjacent_failure_and_duration_independence(self):
        before, backend = a_os_fixture()
        passed = CandidateAOSPass(before, backend)
        bound = abs(float(Fraction(passed.residual.exact_values[0][0])))
        self.assertGreater(bound, 0)
        equal, eb = a_os_fixture(changes={"realization": {"tolerance": bound}})
        self.assertTrue(CandidateAOSPass(equal, eb).residual.admitted)
        lower, lb = a_os_fixture(
            changes={"realization": {"tolerance": math.nextafter(bound, 0.0)}}
        )
        with self.assertRaises(OSStageError) as caught:
            CandidateAOSPass(lower, lb)
        self.assertEqual(caught.exception.substage, "split_residual")
        for dt in (math.nextafter(0.0, 1.0), 2.0):
            other = CandidateAOSPass(replace(before, dt=dt), backend)
            self.assertEqual(other.corrector.current, passed.corrector.current)
            self.assertEqual(other.residual, passed.residual)

    def test_predictor_and_reachable_corrector_singularities_keep_stage(self):
        before, backend = a_os_fixture(chi_A=1.0, zeta_A=3.0)
        with self.assertRaises(OSStageError) as caught:
            CandidateAOSPass(before, backend)
        self.assertEqual(caught.exception.substage, "os_predictor")
        self.assertIsInstance(caught.exception.__cause__, CandidateAStageError)
        self.assertEqual(caught.exception.__cause__.disposition, "singular")
        seed, sb = a_os_fixture(
            C=(2.0, 1.0), gamma=2.0, chi_A=1.0, zeta_A=3.0, kappa_Ah=0.0
        )
        passed = CandidateAOSPass(seed, sb)
        dh = passed.corrector.inputs.geometry.one_form_hodge.matrix[0][0] - 1
        # Cancel the corrected baseline to round G_W to 1; q=1/3 is singular
        # although the predictor's nonzero baseline made its G_W less than 1.
        before, backend = a_os_fixture(
            C=(2.0, 1.0), gamma=2.0, chi_A=1.0, zeta_A=3.0, kappa_Ah=-1 / dh
        )
        with self.assertRaises(OSStageError) as caught:
            CandidateAOSPass(before, backend)
        self.assertEqual(caught.exception.substage, "os_corrector")
        self.assertEqual(caught.exception.__cause__.disposition, "singular")

    def test_geometry_and_resource_failures_prevent_writer(self):
        before, backend = a_os_fixture(changes={"geometry": {"kappa_H": -1000.0}})
        with self.assertRaises(OSStageError) as caught:
            CandidateAOSPass(before, backend)
        self.assertEqual(caught.exception.substage, "geometry_update")
        before, backend = a_os_fixture(C=(0.0, 1.0), dt=10.0)
        original = canonical_json_bytes(before.to_payload())
        with patch(
            "pygrc.models.grc_v4_step.CandidateAWriter", wraps=CandidateAWriter
        ) as writer:
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateAOSStep(before, backend)
            writer.assert_not_called()
        self.assertEqual(caught.exception.stage, "charge_admission")
        self.assertEqual(canonical_json_bytes(before.to_payload()), original)

    def test_positive_writer_singularity_rejects_after_successful_current(self):
        before, backend = a_os_fixture(
            C=(0.0, 0.0), W=(4.0,), kappa_c=0.0, chi_A=1.0, zeta_A=3.0, dt=math.log(2.0)
        )
        original = canonical_json_bytes(before.to_payload())
        written = []

        def observe(*args):
            value = CandidateAWriter(*args)
            written.append(value)
            return value

        with patch("pygrc.models.grc_v4_step.CandidateAWriter", side_effect=observe):
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(caught.exception.stage, "final_reconstruction")
        self.assertEqual(caught.exception.code, "domain_failure")
        self.assertEqual(caught.exception.__cause__.disposition, "singular")
        self.assertEqual(written[0].point.current.values, (0.0,))
        self.assertEqual(written[0].authority.state.W_A, (2.0,))
        self.assertEqual(canonical_json_bytes(before.to_payload()), original)

    def test_reference_restart_can_fail_after_consumed_geometry_admission(self):
        args = dict(
            C=(2.0, 1.0),
            W=(0.25,),
            eta=8.0,
            kappa_c=0.5,
            kappa_Ah=-0.125,
            chi_A=1.0,
            zeta_A=3.0,
            gamma=math.log(2.0),
            dt=math.log(2.0),
        )
        seed, backend = a_os_fixture(**args)
        pred = CandidateACurrent(seed, backend)
        gain = 1 / pred.structural_source().increment[0][0]
        before, backend = a_os_fixture(**args, changes={"geometry": {"kappa_H": gain}})
        passed = CandidateAOSPass(before, backend)
        self.assertEqual(
            passed.corrector.inputs.geometry.one_form_hodge.matrix, ((2.0,),)
        )
        self.assertEqual(passed.corrector.current.values, (0.0,))
        calls = []

        def observe(inputs, differential):
            value = CandidateACurrent(inputs, differential)
            calls.append(value)
            return value

        with patch("pygrc.models.grc_v4_step.CandidateACurrent", side_effect=observe):
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(caught.exception.stage, "final_reconstruction")
        self.assertEqual(caught.exception.__cause__.disposition, "singular")
        final = calls[-1]
        self.assertEqual(final.inputs.current.W_A, (0.5,))
        self.assertEqual(final.inputs.geometry.one_form_hodge.matrix, ((2.0,),))
        self.assertEqual(final.baseline.values, (-1.0,))
        # At reference H1=1 the new W gives J0=-2, rounded G_W=1/4,
        # hence q=(1/2-1/4)/(1/2+1/4)=1/3 and d=0.
        self.assertNotEqual(final.denominator_exact, (Fraction(0),))

    def test_zero_duration_admits_current_and_reset_without_advancement(self):
        before, backend = a_os_fixture(dt=0.0)
        with (
            patch(
                "pygrc.models.grc_v4_step.CandidateAOSPass",
                side_effect=AssertionError("zero has no pass"),
            ),
            patch(
                "pygrc.models.grc_v4_step.CandidateAWriter",
                side_effect=AssertionError("zero has no writer"),
            ),
        ):
            step = ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(step.next_inputs, before)
        self.assertEqual(step.resource.continuity_evaluations, 0)
        self.assertIsNone(step.writer)
        self.assertIsNone(step.os_pass)
        singular, sb = a_os_fixture(
            C=(0.0, 0.0), W=(4.0,), chi_A=1.0, zeta_A=3.0, dt=0.0
        )
        for name in ("current", "reset"):
            with self.subTest(name=name):
                failed = replace(
                    singular,
                    **{name: GRCV4AuthoritativeState((0.0, 0.0), (2.0,), None)},
                )
                with self.assertRaises(ResourceBoundaryError) as caught:
                    ProvisionalCandidateAOSStep(failed, sb)
                self.assertEqual(caught.exception.stage, "pre_read_reconstruction")
                self.assertEqual(caught.exception.__cause__.disposition, "singular")

    def test_subnormal_duration_clock_limits_and_charge_admission(self):
        before, backend = a_os_fixture(dt=math.nextafter(0.0, 1.0))
        before = replace(before, time=1.0)
        step = ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(step.next_inputs.time, 1.0)
        self.assertEqual(step.next_inputs.step_index, 1)
        self.assertEqual(step.resource.continuity_evaluations, 1)
        self.assertIsNotNone(step.writer)
        for changes in (
            dict(step_index=2**53 - 1),
            dict(time=1e308, dt=1e308),
            dict(Q_target=99.0),
        ):
            with (
                self.subTest(changes=changes),
                self.assertRaises(ResourceBoundaryError) as caught,
            ):
                ProvisionalCandidateAOSStep(replace(before, **changes), backend)
            self.assertEqual(caught.exception.stage, "admission")
        with self.assertRaises(ValueError):
            replace(before, dt=-1.0)

    def test_empty_reference_rejection_and_loop_only_positive_writes(self):
        # The frozen reference-Hodge identity requires a nonempty weight map.
        # Do not invent a dummy edge or silently advertise an empty reference.
        with self.assertRaises(V4SchemaError):
            a_os_fixture(graph=GRCV4Graph(("i",), ()), C=(2.0,), W=())
        for graph, C, W in (
            (
                GRCV4Graph(("u", "i"), (OrientedEdge("loop", "u", "u"),)),
                (2.0, 3.0),
                (2.0,),
            ),
        ):
            with self.subTest(graph=graph):
                before, backend = a_os_fixture(graph=graph, C=C, W=W)
                step = ProvisionalCandidateAOSStep(before, backend)
                self.assertEqual(step.next_inputs.current.C, C)
                self.assertEqual(step.os_pass.corrector.current.values, (0.0,) * len(W))
                self.assertEqual(
                    step.next_inputs.current.W_A,
                    a_writer_oracle(W, (1.0,) * len(W), before.dt, 1.0),
                )

    def test_roundtrip_recomputes_and_rejects_forged_outputs_and_stage_inputs(self):
        before, backend = a_os_fixture()
        for cls in (CandidateAOSPass, ProvisionalCandidateAOSStep):
            original = cls(before, backend)
            self.assertEqual(cls.from_payload(original.to_payload()), original)
            for key in ("next_inputs", "current", "residual", "committed"):
                payload = original.to_payload()
                payload[key] = True
                with self.assertRaises(ValueError):
                    cls.from_payload(payload)
            with self.assertRaises(ValueError):
                cls(replace(before, stage="os_corrector"), backend)
            foreign = replace(
                before,
                geometry=GRCV4Geometry(
                    before.geometry.reference,
                    OneFormHodge(before.geometry.reference.graph, ((2.0,),)),
                ),
            )
            with self.assertRaises(ValueError):
                cls(foreign, backend)

    def test_writer_failure_and_reset_only_failure_preserve_whole_inputs(self):
        before, backend = a_os_fixture(
            C=(500.0, 500.0),
            W=(1e-308,),
            eta=1e308,
            kappa_c=0.0,
            alpha=-1.0,
            chi_A=0.0,
            zeta_A=0.0,
            dt=1000.0,
        )
        original = canonical_json_bytes(before.to_payload())
        with self.assertRaises(ResourceBoundaryError) as caught:
            ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(
            (caught.exception.stage, caught.exception.code),
            ("history_write", "nonfinite_value"),
        )
        self.assertEqual(canonical_json_bytes(before.to_payload()), original)
        before, backend = a_os_fixture(C=(0.0, 0.0), W=(4.0,), chi_A=1.0, zeta_A=3.0)
        before = replace(
            before, reset=GRCV4AuthoritativeState((0.0, 0.0), (2.0,), None)
        )
        original = canonical_json_bytes(before.to_payload())
        with patch(
            "pygrc.models.grc_v4_step.CandidateAOSPass",
            side_effect=AssertionError("reset fails before pass"),
        ):
            with self.assertRaises(ResourceBoundaryError) as caught:
                ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(caught.exception.stage, "pre_read_reconstruction")
        self.assertEqual(canonical_json_bytes(before.to_payload()), original)
        for dt in (0.0, 0.001):
            bad, bb = a_os_fixture(
                dt=dt, changes={"lifecycle": {"history_policy_id": "unknown_writer"}}
            )
            with self.assertRaises(ValueError):
                ProvisionalCandidateAOSStep(bad, bb)

    def test_complete_step_covariance_and_repeated_beat_use_new_authority(self):
        nodes = ("u", "v", "w")
        edges = (
            OrientedEdge("a", "u", "v"),
            OrientedEdge("b", "v", "w"),
            OrientedEdge("loop", "u", "u"),
        )
        values, weights, positions = (
            {"u": 3.0, "v": 1.0, "w": 2.0},
            {"a": 2.0, "b": 0.5, "loop": 3.0},
            {"u": (0.0,), "v": (1.0,), "w": (2.0,)},
        )
        options = dict(alpha=0.125, beta=0.25, gamma=0.0625)
        before, backend = a_os_fixture(
            graph=GRCV4Graph(nodes, edges),
            C=tuple(values[n] for n in nodes),
            W=tuple(weights[e.edge_id] for e in edges),
            **options,
        )
        original = ProvisionalCandidateAOSStep(before, backend)
        changed_nodes = ("w", "u", "v")
        changed_edges = (edges[2], OrientedEdge("a", "v", "u"), edges[1])
        changed, cb = a_os_fixture(
            graph=GRCV4Graph(changed_nodes, changed_edges),
            C=tuple(values[n] for n in changed_nodes),
            W=tuple(weights[e.edge_id] for e in changed_edges),
            positions=tuple(positions[n] for n in changed_nodes),
            **options,
        )
        mapped = ProvisionalCandidateAOSStep(changed, cb)
        for node, c in zip(changed_nodes, mapped.next_inputs.current.C, strict=True):
            self.assertAlmostEqual(
                c, original.next_inputs.current.C[nodes.index(node)], delta=2e-14
            )
        for edge, w, j in zip(
            changed_edges,
            mapped.next_inputs.current.W_A,
            mapped.os_pass.corrector.current.values,
            strict=True,
        ):
            old_i = next(i for i, e in enumerate(edges) if e.edge_id == edge.edge_id)
            self.assertAlmostEqual(
                w, original.next_inputs.current.W_A[old_i], delta=2e-14
            )
            self.assertAlmostEqual(
                j,
                (-1 if edge.edge_id == "a" else 1)
                * original.os_pass.corrector.current.values[old_i],
                delta=2e-14,
            )
        second = ProvisionalCandidateAOSStep(original.next_inputs, backend)
        expected = a_dense_pass(original.next_inputs, backend)
        np.testing.assert_allclose(
            second.next_inputs.current.C, expected["C"], rtol=2e-13, atol=2e-14
        )
        np.testing.assert_allclose(
            second.next_inputs.current.W_A, expected["W"], rtol=2e-13, atol=2e-14
        )
        self.assertEqual(
            second.os_pass.predictor.inputs.current, original.next_inputs.current
        )
        self.assertEqual(second.next_inputs.reset, before.reset)
        self.assertEqual(second.next_inputs.step_index, 2)
        self.assertNotEqual(
            second.os_pass.predictor.current, original.os_pass.predictor.current
        )


def a_extreme_split_fixture(tolerance: float = 64.0):
    s = math.ldexp(1.0, 1023)
    graph = GRCV4Graph(
        ("u", "v"),
        (OrientedEdge("a", "u", "v"), OrientedEdge("b", "u", "v")),
    )
    # Multiplication order matters when preparing this fixture: 3*s overflows,
    # whereas 3*(s/8) is the intended finite reference value.
    return a_os_fixture(
        graph=graph,
        weights={"a": s / 8, "b": 3 * (s / 8)},
        C=(1.0, 2.0),
        W=(2.0, 3.0),
        eta=1.0,
        kappa_c=s / 64,
        kappa_Ah=1 / 256,
        alpha=0.0,
        beta=0.0,
        gamma=0.0,
        chi_A=1.0,
        zeta_A=1.0,
        dt=math.ldexp(1.0, -1030),
        changes={
            "geometry": {"kappa_H": s},
            "realization": {"tolerance": tolerance},
            "solver": {"conditioning_limit": 1e12},
            "charge": {"absolute_tolerance": 0.0, "relative_tolerance": 0.0},
        },
    )


def a_split_source_geometry(point):
    from pygrc.models.grc_v4_geometry import H_profile

    ref = point.inputs.geometry.reference
    return H_profile(
        point.structural_source(),
        reference=ref,
        context=ref.context,
        profile=ref.profile,
    )


def split_exact_difference(geometry, regenerated):
    return tuple(
        tuple(Fraction(a) - Fraction(b) for a, b in zip(left, right, strict=True))
        for left, right in zip(
            geometry.one_form_hodge.matrix,
            regenerated.one_form_hodge.matrix,
            strict=True,
        )
    )


def split_positive_two_by_two(matrix) -> bool:
    """Independent exact Sylvester test, not the production inertia helper."""
    return (
        matrix[0][1] == matrix[1][0]
        and matrix[0][0] > 0
        and matrix[0][0] * matrix[1][1] > matrix[0][1] ** 2
    )


class CandidateAOSAuditTests(unittest.TestCase):
    def test_finite_whitened_split_does_not_require_finite_raw_display_entries(self):
        before, backend = a_extreme_split_fixture()
        pred = CandidateACurrent(replace(before, stage="os_predictor"), backend)
        geometry = a_split_source_geometry(pred)
        corr = CandidateACurrent(
            replace(before, geometry=geometry, stage="os_corrector"),
            backend,
        )
        regenerated = a_split_source_geometry(corr)
        residual = split_exact_difference(geometry, regenerated)
        self.assertGreater(
            abs(residual[0][1]), Fraction(float.fromhex("0x1.fffffffffffffp+1023"))
        )
        href = before.geometry.one_form_hodge.matrix
        for sign in (-1, 1):
            bound_matrix = tuple(
                tuple(64 * Fraction(h) + sign * r for h, r in zip(hr, rr, strict=True))
                for hr, rr in zip(href, residual, strict=True)
            )
            self.assertTrue(split_positive_two_by_two(bound_matrix))
        # This is the behavior requiring correction on the reviewed source.
        passed = CandidateAOSPass(before, backend)
        self.assertTrue(passed.residual.admitted)
        self.assertIsNone(passed.residual.values)
        self.assertEqual(CandidateAOSPass.from_payload(passed.to_payload()), passed)
        self.assertEqual(
            tuple(
                tuple(Fraction(x) for x in row) for row in passed.residual.exact_values
            ),
            residual,
        )
        step = ProvisionalCandidateAOSStep(before, backend)
        self.assertEqual(step.next_inputs.current.C, (64591 / 65536, 132017 / 65536))
        self.assertEqual(step.next_inputs.current.W_A, (2.0, 3.0))
        self.assertEqual(step.next_inputs.reset, before.reset)
        self.assertEqual(step.resource.continuity_evaluations, 1)
        self.assertTrue(all(math.isfinite(v) for v in step.final.current.values))
        self.assertTrue(all(math.isfinite(v) for v in step.restart.current.values))

    def test_exceeded_exact_split_keeps_its_real_failure_reason(self):
        before, backend = a_extreme_split_fixture(tolerance=0.0)
        with self.assertRaises(OSStageError) as raised:
            CandidateAOSPass(before, backend)
        self.assertEqual(raised.exception.substage, "split_residual")
        self.assertEqual(raised.exception.__cause__.disposition, "domain_failure")

    def test_shared_numerical_failure_is_classified_at_the_A_OS_boundary(self):
        # Applicable while A reuses C-typed numerical utilities. If the shared
        # utility adopts a candidate-neutral error type, update this type only.
        before, backend = a_os_fixture()
        fault = CandidateCStageError("nonfinite", "explicit shared-helper fault")
        with patch(
            "pygrc.models.grc_v4_realizations.OSSplitResidual",
            side_effect=fault,
        ):
            with self.assertRaises(OSStageError) as raised:
                CandidateAOSPass(before, backend)
        self.assertEqual(raised.exception.substage, "split_residual")
        cause = raised.exception.__cause__
        self.assertEqual(cause.disposition, "nonfinite")
        # Either retain the numerical cause directly or translate it to the
        # A stage exception and retain the original cause below that adapter.
        self.assertTrue(cause is fault or cause.__cause__ is fault)

    def test_programmer_errors_are_not_scientific_split_failures(self):
        before, backend = a_os_fixture()
        fault = ValueError("explicit programmer fault, not numerical admission")
        with patch(
            "pygrc.models.grc_v4_realizations.OSSplitResidual",
            side_effect=fault,
        ):
            with self.assertRaises(ValueError) as raised:
                CandidateAOSPass(before, backend)
        self.assertIs(raised.exception, fault)


class OSSplitResidualAuditTests(unittest.TestCase):
    def test_both_candidates_signed_display_limits_and_exact_norm_boundary(self):
        # Independent eigenvalues for R=[[0,r],[r,0]], Href=s*I:
        # the whitened norm is exactly abs(r)/s. Pressure the rounding limit
        # separately from tolerance equality and its adjacent lower neighbor.
        s = math.ldexp(1.0, 1023)
        graph = GRCV4Graph(
            ("u", "v"), (OrientedEdge("a", "u", "v"), OrientedEdge("b", "u", "v"))
        )
        for family in ("A", "C"):
            for coefficient in (
                0.5,
                math.nextafter(1.0, 0),
                1.0,
                math.nextafter(1.0, 2),
                1.25,
            ):
                off = s * coefficient
                bound = 2 * coefficient
                for tolerance in (bound, math.nextafter(bound, 0)):
                    options = dict(
                        graph=graph,
                        weights={"a": s, "b": s},
                        changes={"realization": {"tolerance": tolerance}},
                    )
                    before = (
                        a_os_fixture(W=(2.0, 3.0), **options)[0]
                        if family == "A"
                        else current_fixture(**options)
                    )
                    ref = before.geometry.reference
                    for sign in (-1, 1):
                        with self.subTest(
                            family=family,
                            coefficient=coefficient,
                            tolerance=tolerance,
                            sign=sign,
                        ):
                            left = GRCV4Geometry(
                                ref,
                                OneFormHodge(
                                    graph,
                                    ((1.75 * s, sign * off), (sign * off, 1.75 * s)),
                                ),
                            )
                            right = GRCV4Geometry(
                                ref,
                                OneFormHodge(
                                    graph,
                                    ((1.75 * s, -sign * off), (-sign * off, 1.75 * s)),
                                ),
                            )
                            value = OSSplitResidual(left, right)
                            expected = (
                                (Fraction(), 2 * sign * Fraction(off)),
                                (2 * sign * Fraction(off), Fraction()),
                            )
                            self.assertEqual(value.admitted, tolerance == bound)
                            self.assertEqual(
                                tuple(
                                    tuple(Fraction(x) for x in row)
                                    for row in value.exact_values
                                ),
                                expected,
                            )
                            if coefficient >= 1:
                                self.assertIsNone(value.values)
                            else:
                                self.assertEqual(
                                    value.values,
                                    tuple(
                                        tuple(float(x) for x in row) for row in expected
                                    ),
                                )

    def test_shared_numeric_dispositions_and_programmer_faults_keep_provenance(self):
        import pygrc.models.grc_v4_realizations as module

        before, backend = a_os_fixture()
        for disposition in (
            "nonfinite",
            "domain_failure",
            "singular",
            "conditioning_failure",
            "no_admitted_root",
            "multiple_admitted_roots",
        ):
            # Inject into the remaining shared exact inertia helper, not only
            # the residual constructor. All typed dispositions retain identity.
            fault = CandidateCStageError(disposition, "shared inertia fault")
            with (
                self.subTest(disposition=disposition),
                patch.object(module, "_c_inertia", side_effect=fault),
            ):
                with self.assertRaises(OSStageError) as raised:
                    CandidateAOSPass(before, backend)
                self.assertEqual(raised.exception.substage, "split_residual")
                self.assertIs(raised.exception.__cause__, fault)
                self.assertEqual(raised.exception.__cause__.disposition, disposition)
        for fault in (
            ValueError("programmer value fault"),
            TypeError("programmer type fault"),
        ):
            with patch.object(module, "_c_inertia", side_effect=fault):
                with self.assertRaises(type(fault)) as raised:
                    CandidateAOSPass(before, backend)
                self.assertIs(raised.exception, fault)

    def test_c_publication_allows_missing_display_and_preserves_exact_defect(self):
        from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation
        from tests.models.test_grc_v4_lifecycle import request
        import pygrc.models.grc_v4_realizations as module

        # A consumer fault-injection control, not a native C overflow witness.
        # Hide only the optional display on the real computed C residual.
        values = []

        def without_display(*args):
            result = OSSplitResidual(*args)
            values.append(result)
            object.__setattr__(result, "values", None)
            return result

        before = os_fixture()
        expected = CandidateCOSOperation(before)
        ordinary = expected.step_v4(request(before.dt))
        owner = CandidateCOSOperation(before)
        with patch.object(module, "OSSplitResidual", side_effect=without_display):
            result = owner.step_v4(request(before.dt))
        self.assertTrue(result.committed)
        self.assertEqual(owner.snapshot(), expected.snapshot())
        self.assertEqual(result.emitted_receipts, ordinary.emitted_receipts)
        os = result.observables.to_dict()["os"]
        self.assertIsNone(os["split_residual"])
        self.assertEqual(len(values), 1)
        self.assertEqual(
            os["exact_split_residual"], [list(row) for row in values[0].exact_values]
        )
        self.assertEqual(
            os["exact_split_residual"],
            ordinary.observables.to_dict()["os"]["exact_split_residual"],
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3 and sys.argv[1] == "--capture-p944":
        raise SystemExit(capture_p944(sys.argv[2]))
    unittest.main()
