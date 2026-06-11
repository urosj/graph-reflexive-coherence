"""Transport and identity tests for the Phase 7 GRC9V3 shell."""

from __future__ import annotations

import unittest

from pygrc.models import GRC9V3, PortEdge


def _two_node_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {}},
                {"node_id": 1, "payload": {}},
            ],
            "edges": [
                {
                    "edge_id": 0,
                    "endpoint_a": {"node_id": 0, "slot": 0},
                    "endpoint_b": {"node_id": 1, "slot": 0},
                    "payload": {},
                }
            ],
            "incidence": {"0": [0], "1": [0]},
            "port_structure": {},
        },
        "nodes": {
            "0": {"coherence": 1.0, "basin_mass": 1.0, "basin_id": 0},
            "1": {"coherence": 3.0, "basin_mass": 3.0, "basin_id": 1},
        },
        "port_edges": {
            "0": {
                "node_u": 0,
                "port_u": 1,
                "node_v": 1,
                "port_v": 1,
                "conductance": 0.5,
                "flux_uv": 0.0,
            }
        },
    }


def _three_node_identity_state() -> dict[str, object]:
    return {
        "topology": {
            "nodes": [
                {"node_id": 0, "payload": {}},
                {"node_id": 1, "payload": {}},
                {"node_id": 2, "payload": {}},
            ],
            "edges": [
                {
                    "edge_id": 0,
                    "endpoint_a": {"node_id": 0, "slot": 0},
                    "endpoint_b": {"node_id": 1, "slot": 0},
                    "payload": {},
                }
            ],
            "incidence": {"0": [0], "1": [0], "2": []},
            "port_structure": {},
        },
        "nodes": {
            "0": {
                "coherence": 1.0,
                "gradient_row_basis": [1.0, 0.0, 0.0],
                "signed_hessian_row_basis": [0.5, 0.5, 0.5],
            },
            "1": {
                "coherence": 3.0,
                "gradient_row_basis": [0.0, 0.0, 0.0],
                "signed_hessian_row_basis": [0.5, 0.5, 0.5],
            },
            "2": {
                "coherence": 2.0,
                "gradient_row_basis": [0.0, 0.0, 0.0],
                "signed_hessian_row_basis": [0.0, 0.0, 0.0],
            },
        },
        "port_edges": {
            "0": {
                "node_u": 0,
                "port_u": 1,
                "node_v": 1,
                "port_v": 1,
                "conductance": 1.0,
                "flux_uv": 1.0,
            }
        },
    }


def _transport_params(**modes: object) -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "eta": 1.0,
            "kappa_c": 1.0,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 0.0},
            "eps_gradient": 0.5,
            "eps_hessian": 0.1,
        },
        "constitutive_semantic_modes": dict(modes),
    }


class GRC9V3TransportIdentityTest(unittest.TestCase):
    """Validate Phase 7 Iteration 3 transport and identity behavior."""

    def test_transport_pass_computes_conductance_potential_flux_and_labels(self) -> None:
        model = GRC9V3.from_state(
            state=_two_node_state(),
            params=_transport_params(),
        )

        model.rebuild_differential_state()
        model.rebuild_transport_state()
        state = model.get_state()

        self.assertAlmostEqual(1.0, state.base_conductance[0])
        self.assertAlmostEqual(-2.0, state.potential[0])
        self.assertAlmostEqual(2.0, state.potential[1])
        self.assertAlmostEqual(4.0, state.port_edges[0].flux_uv)
        self.assertAlmostEqual(1.0, state.geometric_length[0])
        self.assertAlmostEqual(4.0, state.flux_coupling[0])
        self.assertAlmostEqual(0.2, state.temporal_delay[0])
        self.assertEqual(
            "inverse_base_conductance",
            state.edge_label_computation_mode["geometric_length"],
        )
        self.assertEqual("absolute_flux", state.edge_label_computation_mode["flux_coupling"])
        self.assertEqual("transport_ratio", state.edge_label_computation_mode["temporal_delay"])

    def test_edge_label_selection_can_omit_post_flux_labels(self) -> None:
        model = GRC9V3.from_state(
            state=_two_node_state(),
            params=_transport_params(edge_label_selection=["geometric_length"]),
        )

        model.rebuild_differential_state()
        model.rebuild_transport_state()
        state = model.get_state()

        self.assertEqual({0}, set(state.geometric_length))
        self.assertEqual({}, state.flux_coupling)
        self.assertEqual({}, state.temporal_delay)
        self.assertEqual(("geometric_length",), state.edge_label_params["selection"])

    def test_identity_pass_extracts_flux_basins_and_eq_g7_seed(self) -> None:
        model = GRC9V3.from_state(
            state=_three_node_identity_state(),
            params=_transport_params(),
        )

        model.rebuild_identity_state()
        state = model.get_state()
        geometric_identity = state.cached_quantities["geometric_identity"]

        self.assertEqual({1}, state.sink_set)
        self.assertEqual({1: {0, 1}}, state.basins)
        self.assertEqual({"0": 1, "1": 1, "2": 2}, state.cached_quantities["successor_map"])
        self.assertEqual([1], geometric_identity["seed_nodes"])
        self.assertEqual(["1"], [str(value) for value in geometric_identity["validated_basin_ids"]])
        self.assertEqual([1], geometric_identity["basin_seed_nodes"]["1"])
        self.assertGreater(geometric_identity["gradient_norm_by_node"]["0"], 0.5)
        self.assertEqual(0.0, geometric_identity["min_signed_hessian_by_node"]["2"])
        self.assertEqual(
            "unit_measure_basin_membership",
            geometric_identity["basin_mass_source"],
        )
        self.assertAlmostEqual(4.0, geometric_identity["basin_mass_by_basin_id"]["1"])
        self.assertAlmostEqual(4.0, geometric_identity["basin_mass_by_node"]["0"])
        self.assertAlmostEqual(4.0, geometric_identity["basin_mass_by_node"]["1"])
        self.assertAlmostEqual(4.0, state.nodes[1].basin_mass)
        self.assertAlmostEqual(1.0, state.nodes[0].basin_mass)
        self.assertAlmostEqual(2.0, state.nodes[2].basin_mass)

    def test_identity_basin_mass_recomputes_after_membership_changes(self) -> None:
        params = _transport_params()
        params["evolution"]["eps_hessian"] = 0.6
        model = GRC9V3.from_state(
            state=_three_node_identity_state(),
            params=params,
        )

        model.rebuild_identity_state()
        state = model.get_state()
        self.assertAlmostEqual(4.0, state.nodes[1].basin_mass)

        state.port_edges[0] = PortEdge(
            node_u=0,
            port_u=1,
            node_v=1,
            port_v=1,
            conductance=1.0,
            flux_uv=-1.0,
        )
        model.rebuild_identity_state()
        state = model.get_state()
        geometric_identity = state.cached_quantities["geometric_identity"]

        self.assertEqual({0}, state.sink_set)
        self.assertEqual({0: {0, 1}}, state.basins)
        self.assertAlmostEqual(4.0, state.nodes[0].basin_mass)
        self.assertAlmostEqual(3.0, state.nodes[1].basin_mass)
        self.assertAlmostEqual(4.0, geometric_identity["basin_mass_by_basin_id"]["0"])


if __name__ == "__main__":
    unittest.main()
