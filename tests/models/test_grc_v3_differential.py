"""Direct tests for the Iteration 3 GRCV3 differential-summary baseline."""

from __future__ import annotations

import math
import unittest

from pygrc.core import WeightedGraphBackend
from pygrc.models import BasinAttributes, GRCV3
from pygrc.models.grc_v3_differential import (
    calibrate_hessian_sign,
    induced_local_frame_displacements,
    symmetric_eigenvalues,
    weighted_least_squares_gradient,
    weighted_least_squares_hessian,
)


class GRCV3DifferentialBackendTest(unittest.TestCase):
    """Validate the Phase 5 Iteration 3 reference differential backend."""

    def test_weighted_least_squares_gradient_matches_linear_profile(self) -> None:
        gradient = weighted_least_squares_gradient(
            center_value=0.0,
            displacements={0: [-1.0], 1: [1.0]},
            neighbor_values={0: -1.0, 1: 1.0},
            weights={0: 1.0, 1: 1.0},
            regularization=1e-9,
        )

        self.assertEqual(1, len(gradient))
        self.assertAlmostEqual(1.0, gradient[0], places=6)

    def test_weighted_least_squares_hessian_matches_quadratic_profile(self) -> None:
        hessian = weighted_least_squares_hessian(
            center_value=0.0,
            gradient=[0.0],
            displacements={0: [-1.0], 1: [1.0]},
            neighbor_values={0: 0.5, 1: 0.5},
            weights={0: 1.0, 1: 1.0},
            regularization=0.0,
        )

        self.assertEqual([[1.0]], [[round(value, 6) for value in row] for row in hessian])

    def test_induced_local_frame_displacements_are_deterministic_on_chain(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({"coherence": 0.0})
        center = graph.add_node({"coherence": 1.0})
        right = graph.add_node({"coherence": 2.0})
        edge_left = graph.add_edge(left, center, {"base_conductance": 1.0})
        edge_right = graph.add_edge(center, right, {"base_conductance": 1.0})

        displacements = induced_local_frame_displacements(
            graph,
            node_id=center,
            base_conductance={edge_left: 1.0, edge_right: 1.0},
            dimension=1,
        )

        self.assertEqual((left, right), tuple(sorted(displacements)))
        self.assertAlmostEqual(
            abs(displacements[left][0]),
            abs(displacements[right][0]),
            places=6,
        )
        self.assertLess(displacements[left][0] * displacements[right][0], 0.0)

    def test_calibrate_hessian_sign_prefers_positive_definite_basin_convention(self) -> None:
        sign = calibrate_hessian_sign(
            candidate_seed_ids=[0],
            basin_attributes={
                0: BasinAttributes(
                    coherence=1.0,
                    gradient=[0.0],
                    hessian=[[-2.0]],
                    net_flux=[0.0],
                    basin_mass=1.0,
                    basin_id="seed",
                    parent_id=None,
                    depth=0,
                )
            },
            gradient_threshold=1e-3,
            hessian_threshold=1e-3,
        )

        self.assertEqual(-1, sign)

    def test_symmetric_eigenvalues_returns_sorted_real_spectrum(self) -> None:
        eigenvalues = symmetric_eigenvalues([[2.0, 0.0], [0.0, 1.0]])
        self.assertEqual([1.0, 2.0], [round(value, 6) for value in eigenvalues])

    def test_rebuild_basin_attributes_materializes_gradient_hessian_and_sign(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({"coherence": -1.0})
        center = graph.add_node({"coherence": 0.0})
        right = graph.add_node({"coherence": 1.0})
        edge_left = graph.add_edge(left, center, {"base_conductance": 1.0})
        edge_right = graph.add_edge(center, right, {"base_conductance": 1.0})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(left): {"coherence": -1.0, "basin_id": left},
                    str(center): {"coherence": 0.0, "basin_id": center},
                    str(right): {"coherence": 1.0, "basin_id": right},
                },
                "base_conductance": {
                    str(edge_left): 1.0,
                    str(edge_right): 1.0,
                },
                "sink_set": [center],
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph

        model.rebuild_basin_attributes()

        state = model.get_state()
        self.assertIn(center, state.nodes)
        self.assertEqual(2, len(state.nodes[center].gradient))
        self.assertEqual(2, len(state.nodes[center].hessian))
        self.assertEqual(2, len(state.nodes[center].net_flux))
        self.assertEqual(
            "weighted_least_squares",
            state.cached_quantities["differential_backend"],
        )
        self.assertEqual(
            "induced_local_frame",
            state.cached_quantities["geometry_backend"],
        )
        self.assertIn("hessian_sign", state.cached_quantities)
        self.assertTrue(math.isfinite(state.nodes[center].gradient[0]))

    def test_rebuild_basin_attributes_preserves_existing_hessian_sign(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({"coherence": -1.0})
        center = graph.add_node({"coherence": 0.0})
        right = graph.add_node({"coherence": 1.0})
        edge_left = graph.add_edge(left, center, {"base_conductance": 1.0})
        edge_right = graph.add_edge(center, right, {"base_conductance": 1.0})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(left): {"coherence": -1.0, "basin_id": left},
                    str(center): {"coherence": 0.0, "basin_id": center},
                    str(right): {"coherence": 1.0, "basin_id": right},
                },
                "base_conductance": {
                    str(edge_left): 1.0,
                    str(edge_right): 1.0,
                },
                "sink_set": [center],
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph

        model.rebuild_basin_attributes()
        calibrated = int(model.get_state().cached_quantities["hessian_sign"])
        frozen = -calibrated
        model.get_state().cached_quantities["hessian_sign"] = frozen

        model.rebuild_basin_attributes()

        self.assertEqual(frozen, model.get_state().cached_quantities["hessian_sign"])
