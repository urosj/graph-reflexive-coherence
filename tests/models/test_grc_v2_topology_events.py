"""Topology mutation tests for Phase 4 Iteration 6."""

from __future__ import annotations

import unittest

from pygrc.core import GRCEvent, InvalidStateTransitionError
from pygrc.models import GRCV2


def _valid_grcv2_config() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "alpha": 1.0,
            "beta": 1.0,
            "gamma": 1.0,
            "delta": 1.0,
            "eta": 1.0,
            "kappa_c": 1.0,
            "lambda_c": 1.0,
            "xi_c": 1.0,
            "zeta_c": 1.0,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0},
            "eps_spark": 0.01,
            "tau_split": 2.0,
            "lambda_birth": 0.25,
            "alpha_seed": 0.5,
            "eps_prune": 0.001,
            "rng_seed": 0,
            "spark_backend": "cheeger_proxy",
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


class GRCV2TopologyEventsTest(unittest.TestCase):
    """Validate split, birth, and prune behavior."""

    def test_soft_split_initialization_is_deterministic(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 2.0, "1": 1.0},
            "edges": {"0": 1.0},
        }
        model = GRCV2.from_config(config)
        spark_event = GRCEvent(
            kind="spark",
            step_index=0,
            source_family="GRCV2",
            payload={
                "backend": "cheeger_proxy",
                "sink_node_id": 1,
                "basin_members": [0, 1],
                "candidate_rank": 0,
            },
        )

        model._apply_topology_changes([spark_event])

        state = model.get_state()
        self.assertEqual((0, 1, 2, 3), tuple(state.topology.iter_live_node_ids()))
        self.assertEqual(0.0, state.nodes[1])
        self.assertEqual(0.5, state.nodes[2])
        self.assertEqual(0.5, state.nodes[3])
        self.assertEqual(5, len(tuple(state.topology.iter_live_edge_ids())))
        self.assertEqual(1, len(state.split_registry))
        registry = next(iter(state.split_registry.values()))
        self.assertEqual([2, 3], registry["child_node_ids"])
        self.assertFalse(registry["complete"])

    def test_split_progression_removes_parent_only_after_completion(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 2.0, "1": 1.0},
            "edges": {"0": 1.0},
        }
        model = GRCV2.from_config(config)
        spark_event = GRCEvent(
            kind="spark",
            step_index=0,
            source_family="GRCV2",
            payload={
                "backend": "cheeger_proxy",
                "sink_node_id": 1,
                "basin_members": [0, 1],
                "candidate_rank": 0,
            },
        )
        model._apply_topology_changes([spark_event])

        model._progress_split_registry()
        self.assertTrue(model.get_state().topology.has_node(1))

        model._progress_split_registry()
        self.assertFalse(model.get_state().topology.has_node(1))
        registry = next(iter(model.get_state().split_registry.values()))
        self.assertTrue(registry["complete"])
        self.assertTrue(registry["parent_removed"])

    def test_front_birth_adds_node_edge_and_transfers_mass(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["lambda_birth"] = 1e9
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 1.0, "1": 1.0},
            "edges": {"0": 1.0},
            "flux": {"0:0": 2.0, "0:1": -2.0},
        }
        model = GRCV2.from_config(config)

        model._apply_front_birth()

        state = model.get_state()
        self.assertEqual((0, 1, 2), tuple(state.topology.iter_live_node_ids()))
        self.assertEqual((0, 1), tuple(state.topology.iter_live_edge_ids()))
        self.assertAlmostEqual(0.9, state.nodes[0])
        self.assertAlmostEqual(0.1, state.nodes[2])
        self.assertEqual("bernoulli_probability", state.cached_quantities["birth_rule_mode"])

    def test_prune_removes_isolated_low_mass_nodes_and_redistributes_mass(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [
                    {"node_id": 0, "payload": {}},
                    {"node_id": 1, "payload": {}},
                    {"node_id": 2, "payload": {}},
                ],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0], "2": []},
            },
            "nodes": {"0": 1.0, "1": 1.0, "2": 0.0001},
            "edges": {"0": 1.0},
        }
        model = GRCV2.from_config(config)

        model._apply_boundary_behavior()

        state = model.get_state()
        self.assertEqual((0, 1), tuple(state.topology.iter_live_node_ids()))
        self.assertAlmostEqual(1.00005, state.nodes[0])
        self.assertAlmostEqual(1.00005, state.nodes[1])

    def test_barrier_and_ghost_modes_fail_explicitly_when_unimplemented(self) -> None:
        config = _valid_grcv2_config()
        modes = dict(config["constitutive_semantic_modes"])
        modes["boundary_mode"] = "barrier"
        config["constitutive_semantic_modes"] = modes
        model = GRCV2.from_config(config)

        with self.assertRaises(InvalidStateTransitionError):
            model._apply_boundary_behavior()
