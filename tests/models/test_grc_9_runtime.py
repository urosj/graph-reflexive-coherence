"""Runtime surface tests for the pre-topology GRC9 reflexive loop."""

from __future__ import annotations

import unittest

from pygrc.models import GRC9


def _runtime_config() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "kappa_c": 1.5,
            "eta": 0.5,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": 1.0},
        },
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


class GRC9RuntimeSurfaceTest(unittest.TestCase):
    """Validate Iteration 4 potential/flux/identity behavior."""

    def test_compute_potential_and_flux_preserve_oriented_antisymmetry(self) -> None:
        model = GRC9.from_state(
            state={
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
                "node_coherence": {"0": 1.0, "1": 3.0},
                "port_edges": {
                    "0": {
                        "node_u": 0,
                        "port_u": 1,
                        "node_v": 1,
                        "port_v": 1,
                        "conductance": 2.0,
                        "flux_uv": 0.0,
                    }
                },
            },
            params=_runtime_config(),
        )

        model._compute_potential()
        model._compute_flux()

        state = model.get_state()
        self.assertAlmostEqual(-8.0, state.potential[0])
        self.assertAlmostEqual(0.0, state.potential[1])
        self.assertAlmostEqual(8.0, state.port_edges[0].flux_uv)
        oriented_flux = state.cached_quantities["oriented_flux"][0]
        self.assertAlmostEqual(8.0, oriented_flux[0])
        self.assertAlmostEqual(-8.0, oriented_flux[1])
        self.assertAlmostEqual(0.0, oriented_flux[0] + oriented_flux[1])

    def test_topology_hydration_enforces_canonical_port_edge_orientation(self) -> None:
        model = GRC9.from_state(
            state={
                "topology": {
                    "nodes": [
                        {"node_id": 0, "payload": {}},
                        {"node_id": 1, "payload": {}},
                    ],
                    "edges": [
                        {
                            "edge_id": 0,
                            "endpoint_a": {"node_id": 1, "slot": 4},
                            "endpoint_b": {"node_id": 0, "slot": 0},
                            "payload": {},
                        }
                    ],
                    "incidence": {"0": [0], "1": [0]},
                    "port_structure": {},
                },
                "node_coherence": {"0": 1.0, "1": 1.0},
            },
            params=_runtime_config(),
        )

        port_edge = model.get_state().port_edges[0]
        self.assertEqual(0, port_edge.node_u)
        self.assertEqual(1, port_edge.port_u)
        self.assertEqual(1, port_edge.node_v)
        self.assertEqual(5, port_edge.port_v)

    def test_successor_map_tie_break_uses_ascending_neighbor_id_and_zero_outflow_self(self) -> None:
        tie_model = GRC9.from_state(
            state={
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
                        },
                        {
                            "edge_id": 1,
                            "endpoint_a": {"node_id": 0, "slot": 1},
                            "endpoint_b": {"node_id": 2, "slot": 0},
                            "payload": {},
                        },
                    ],
                    "incidence": {"0": [0, 1], "1": [0], "2": [1]},
                    "port_structure": {},
                },
                "node_coherence": {"0": 1.0, "1": 1.0, "2": 1.0},
                "potential": {"0": 0.0, "1": 1.0, "2": 1.0},
                "port_edges": {
                    "0": {
                        "node_u": 0,
                        "port_u": 1,
                        "node_v": 1,
                        "port_v": 1,
                        "conductance": 1.0,
                        "flux_uv": 0.0,
                    },
                    "1": {
                        "node_u": 0,
                        "port_u": 2,
                        "node_v": 2,
                        "port_v": 1,
                        "conductance": 1.0,
                        "flux_uv": 0.0,
                    },
                },
            },
            params=_runtime_config(),
        )
        tie_model._compute_flux()
        tie_model._detect_identities()

        successor_map = tie_model.get_state().cached_quantities["successor_map"]
        self.assertEqual(1, successor_map[0])
        self.assertEqual({1, 2}, tie_model.get_state().sink_set)

        zero_model = GRC9.from_state(
            state={
                "topology": {
                    "nodes": [{"node_id": 0, "payload": {}}],
                    "edges": [],
                    "incidence": {"0": []},
                    "port_structure": {},
                },
                "node_coherence": {"0": 1.0},
            },
            params=_runtime_config(),
        )
        zero_model._detect_identities()

        zero_successor_map = zero_model.get_state().cached_quantities["successor_map"]
        self.assertEqual(0, zero_successor_map[0])
        self.assertEqual(set(), zero_model.get_state().sink_set)
        self.assertEqual({}, zero_model.get_state().basins)

    def test_basin_extraction_is_deterministic_on_fixed_inputs(self) -> None:
        model = GRC9.from_state(
            state={
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
                        },
                        {
                            "edge_id": 1,
                            "endpoint_a": {"node_id": 1, "slot": 3},
                            "endpoint_b": {"node_id": 2, "slot": 0},
                            "payload": {},
                        },
                    ],
                    "incidence": {"0": [0], "1": [0, 1], "2": [1]},
                    "port_structure": {},
                },
                "node_coherence": {"0": 1.0, "1": 1.0, "2": 1.0},
                "potential": {"0": 0.0, "1": 1.0, "2": 2.0},
                "port_edges": {
                    "0": {
                        "node_u": 0,
                        "port_u": 1,
                        "node_v": 1,
                        "port_v": 1,
                        "conductance": 1.0,
                        "flux_uv": 0.0,
                    },
                    "1": {
                        "node_u": 1,
                        "port_u": 4,
                        "node_v": 2,
                        "port_v": 1,
                        "conductance": 1.0,
                        "flux_uv": 0.0,
                    },
                },
            },
            params=_runtime_config(),
        )

        model._compute_flux()
        model._detect_identities()

        state = model.get_state()
        self.assertEqual({2}, state.sink_set)
        self.assertEqual({2: {0, 1, 2}}, state.basins)
        self.assertEqual({0: 1, 1: 2, 2: 2}, state.cached_quantities["successor_map"])
