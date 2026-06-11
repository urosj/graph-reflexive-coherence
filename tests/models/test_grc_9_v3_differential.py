"""Differential-layer tests for the Phase 7 GRC9V3 shell."""

from __future__ import annotations

import unittest

from pygrc.models import GRC9V3, PortEdge


def _differential_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {}},
                {"node_id": 1, "payload": {}},
                {"node_id": 2, "payload": {}},
                {"node_id": 3, "payload": {}},
            ],
            "edges": [
                {
                    "edge_id": 0,
                    "endpoint_a": {"node_id": 0, "slot": 0},
                    "endpoint_b": {"node_id": 1, "slot": 0},
                    "payload": {},
                },
                {
                    "edge_id": 1,
                    "endpoint_a": {"node_id": 0, "slot": 2},
                    "endpoint_b": {"node_id": 2, "slot": 0},
                    "payload": {},
                },
                {
                    "edge_id": 2,
                    "endpoint_a": {"node_id": 0, "slot": 3},
                    "endpoint_b": {"node_id": 3, "slot": 0},
                    "payload": {},
                },
            ],
            "incidence": {"0": [0, 1, 2], "1": [0], "2": [1], "3": [2]},
            "port_structure": {},
        },
        "nodes": {
            "0": {
                "coherence": 1.0,
                "basin_mass": 1.0,
                "basin_id": "root",
                "parent_id": None,
                "depth": 0,
            },
            "1": {"coherence": 3.0, "basin_mass": 3.0, "basin_id": 1},
            "2": {"coherence": 2.0, "basin_mass": 2.0, "basin_id": 2},
            "3": {"coherence": 0.0, "basin_mass": 0.0, "basin_id": 3},
        },
        "port_edges": {
            "0": {
                "node_u": 0,
                "port_u": 1,
                "node_v": 1,
                "port_v": 1,
                "conductance": 2.0,
                "flux_uv": 0.2,
            },
            "1": {
                "node_u": 0,
                "port_u": 3,
                "node_v": 2,
                "port_v": 1,
                "conductance": 1.0,
                "flux_uv": -0.1,
            },
            "2": {
                "node_u": 0,
                "port_u": 4,
                "node_v": 3,
                "port_v": 1,
                "conductance": 4.0,
                "flux_uv": 0.4,
            },
        },
    }


def _differential_params(**modes: object) -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "lambda_c": 2.0,
            "xi_c": 0.5,
            "zeta_c": 0.25,
            "eps_gradient": 0.001,
            "eps_hessian": 0.001,
        },
        "constitutive_semantic_modes": dict(modes),
    }


class GRC9V3DifferentialLayerTest(unittest.TestCase):
    """Validate Phase 7 Iteration 2 row-basis differential behavior."""

    def test_row_basis_gradient_and_default_hessian_follow_g2_g3(self) -> None:
        model = GRC9V3.from_state(
            state=_differential_state(),
            params=_differential_params(),
        )

        model.rebuild_differential_state()
        state = model.get_state()

        self.assertAlmostEqual(5.0 / 3.0, state.nodes[0].gradient_row_basis[0])
        self.assertAlmostEqual(-1.0, state.nodes[0].gradient_row_basis[1])
        self.assertAlmostEqual(0.0, state.nodes[0].gradient_row_basis[2])
        self.assertEqual(
            state.nodes[0].gradient_row_basis,
            state.nodes[0].signed_hessian_row_basis,
        )
        self.assertEqual("row_basis_diagonal", state.cached_quantities["hessian_backend"])
        self.assertEqual(1, state.cached_quantities["hessian_sign"])

    def test_weighted_least_squares_backend_records_comparison_geometry(self) -> None:
        model = GRC9V3.from_state(
            state=_differential_state(),
            params=_differential_params(hessian_backend="weighted_least_squares"),
        )

        model.rebuild_differential_state()
        state = model.get_state()

        unsigned_row_hessian = state.cached_quantities["row_basis_hessian_unsigned"]["0"]
        comparison_hessian = state.cached_quantities["weighted_least_squares_hessian"]["0"]

        self.assertEqual("weighted_least_squares", state.cached_quantities["hessian_backend"])
        self.assertNotEqual(unsigned_row_hessian, state.nodes[0].signed_hessian_row_basis)
        self.assertAlmostEqual(0.0, comparison_hessian[0][0])
        self.assertAlmostEqual(0.0, state.nodes[0].signed_hessian_row_basis[0])

    def test_cached_hessian_sign_is_reused_as_run_fixed_convention(self) -> None:
        state = _differential_state()
        state["cached_quantities"] = {"hessian_sign": -1}
        model = GRC9V3.from_state(state=state, params=_differential_params())

        model.rebuild_differential_state()

        self.assertEqual(-1, model.get_state().cached_quantities["hessian_sign"])
        self.assertAlmostEqual(
            -5.0 / 3.0,
            model.get_state().nodes[0].signed_hessian_row_basis[0],
        )

    def test_differential_rebuild_carries_signed_hessian_history(self) -> None:
        state = _differential_state()
        state["cached_quantities"] = {
            "current_min_signed_hessian_by_node": {"0": 0.25, "99": -1.0}
        }
        model = GRC9V3.from_state(state=state, params=_differential_params())

        model.rebuild_differential_state()
        caches = model.get_state().cached_quantities

        self.assertEqual({"0": 0.25}, caches["previous_min_signed_hessian_by_node"])
        self.assertEqual(["99"], caches["signed_hessian_history_pruned_node_ids"])
        self.assertIn("0", caches["current_min_signed_hessian_by_node"])

    def test_net_flux_summary_refreshes_when_edge_flux_changes(self) -> None:
        model = GRC9V3.from_state(
            state=_differential_state(),
            params=_differential_params(),
        )

        model.rebuild_differential_state()
        first_summary = list(model.get_state().nodes[0].net_flux_summary)

        state = model.get_state()
        state.port_edges[0] = PortEdge(
            node_u=0,
            port_u=1,
            node_v=1,
            port_v=1,
            conductance=2.0,
            flux_uv=1.0,
        )
        model.set_state(state)
        model.rebuild_differential_state()
        second_summary = list(model.get_state().nodes[0].net_flux_summary)

        self.assertEqual([0.1, 0.4, 0.0], first_summary)
        self.assertEqual([0.9, 0.4, 0.0], second_summary)

    def test_hybrid_node_tensor_uses_eq1_diagonal_mismatch_and_isotropic_flux(self) -> None:
        model = GRC9V3.from_state(
            state=_differential_state(),
            params=_differential_params(),
        )

        model.rebuild_differential_state()
        state = model.get_state()
        tensor = state.cached_quantities["hybrid_node_tensors"]["0"]

        self.assertEqual([9.0, 4.0, 0.0], state.cached_quantities["row_mismatch_sums"]["0"])
        self.assertAlmostEqual(6.5625, tensor[0][0])
        self.assertAlmostEqual(4.0625, tensor[1][1])
        self.assertAlmostEqual(2.0625, tensor[2][2])
        self.assertAlmostEqual(0.0, tensor[0][1])
        self.assertAlmostEqual(0.0, tensor[0][2])
        self.assertAlmostEqual(0.0, tensor[1][2])


if __name__ == "__main__":
    unittest.main()
