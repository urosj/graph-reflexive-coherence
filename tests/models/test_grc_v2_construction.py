"""Construction and state-surface tests for the Phase 4 GRCV2 baseline."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pygrc.core import (
    HOST_EMBEDDING_FRAME,
    INTRINSIC_FRAME,
    InvalidParamsError,
    InvalidStateTransitionError,
    WeightedGraphBackend,
)
from pygrc.models import GRCV2
from pygrc.models.grc_v2_state import GRCV2State


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
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


class GRCV2ConstructionTest(unittest.TestCase):
    """Validate the Iteration 1 GRCV2 construction/state surface."""

    def test_from_config_constructs_grcv2_state(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())

        state = model.get_state()
        self.assertIsInstance(state, GRCV2State)
        self.assertIsInstance(state.topology, WeightedGraphBackend)
        self.assertEqual({}, state.nodes)
        self.assertEqual(model.get_params().params_hash, state.params_identity)

    def test_list_capabilities_advertises_intrinsic_or_host_frame_exactly_once(self) -> None:
        intrinsic_model = GRCV2.from_config(_valid_grcv2_config())
        host_config = _valid_grcv2_config()
        host_modes = dict(host_config["constitutive_semantic_modes"])
        host_modes["frame_mode"] = "host_embedding"
        host_modes["host_geometry_fields"] = ["positions"]
        host_config["constitutive_semantic_modes"] = host_modes
        host_model = GRCV2.from_config(host_config)

        intrinsic_claims = intrinsic_model.list_capabilities()
        host_claims = host_model.list_capabilities()

        self.assertIn(INTRINSIC_FRAME, intrinsic_claims)
        self.assertNotIn(HOST_EMBEDDING_FRAME, intrinsic_claims)
        self.assertIn(HOST_EMBEDDING_FRAME, host_claims)
        self.assertNotIn(INTRINSIC_FRAME, host_claims)

    def test_invalid_mode_values_are_rejected_early(self) -> None:
        bad_config = _valid_grcv2_config()
        bad_modes = dict(bad_config["constitutive_semantic_modes"])
        bad_modes["boundary_mode"] = "teleport"
        bad_config["constitutive_semantic_modes"] = bad_modes

        with self.assertRaises(InvalidParamsError):
            GRCV2.from_config(bad_config)

    def test_host_embedding_requires_host_geometry_fields(self) -> None:
        bad_config = _valid_grcv2_config()
        bad_modes = dict(bad_config["constitutive_semantic_modes"])
        bad_modes["frame_mode"] = "host_embedding"
        bad_config["constitutive_semantic_modes"] = bad_modes

        with self.assertRaises(InvalidParamsError):
            GRCV2.from_config(bad_config)

    def test_set_state_validates_topology_membership(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())

        invalid_state = GRCV2State(
            topology=WeightedGraphBackend(),
            nodes={99: 1.0},
        )

        with self.assertRaises(InvalidStateTransitionError):
            model.set_state(invalid_state)

    def test_from_state_restores_weighted_topology_and_fields(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node({"label": "A"})
        node_1 = graph.add_node({"label": "B"})
        edge_0 = graph.add_edge(node_0, node_1, {"weight": 0.5})
        params = _valid_grcv2_config()
        state = {
            "topology": {
                "nodes": [
                    {"node_id": node_0, "payload": {"label": "A"}},
                    {"node_id": node_1, "payload": {"label": "B"}},
                ],
                "edges": [
                    {
                        "edge_id": edge_0,
                        "node_a": node_0,
                        "node_b": node_1,
                        "payload": {"weight": 0.5},
                    }
                ],
                "incidence": {"0": [0], "1": [0]},
            },
            "next_node_id": graph.next_node_id,
            "next_edge_id": graph.next_edge_id,
            "nodes": {"0": 1.0, "1": 0.5},
            "edges": {"0": 0.25},
            "geometric_length": {"0": 1.0},
            "temporal_delay": {"0": 0.5},
            "flux_coupling": {"0": 0.25},
            "flux": {"0:0": 0.25, "0:1": -0.25},
            "potential": {"0": 1.0, "1": 0.2},
            "sink_set": [1],
            "basins": {"1": [0, 1]},
            "split_registry": {
                "spark-0": {
                    "parent_node_id": 1,
                    "child_node_ids": [],
                    "split_ratio": 0.5,
                    "progress": 0.0,
                    "complete": False,
                }
            },
        }

        model = GRCV2.from_state(state, params)

        restored = model.get_state()
        self.assertEqual((0, 1), tuple(restored.topology.iter_live_node_ids()))
        self.assertEqual((0,), tuple(restored.topology.iter_live_edge_ids()))
        self.assertEqual({0: 1.0, 1: 0.5}, restored.nodes)
        self.assertEqual({(0, 0): 0.25, (0, 1): -0.25}, restored.flux)
        self.assertEqual({1}, restored.sink_set)
        self.assertEqual({1: {0, 1}}, restored.basins)

    def test_reset_restores_initial_state(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {"step_index": 2, "time": 1.0}
        model = GRCV2.from_config(config)
        state = model.get_state()
        state.step_index = 8
        state.time = 4.0
        model.set_state(state)

        model.reset()

        self.assertEqual(2, model.get_state().step_index)
        self.assertEqual(1.0, model.get_state().time)

    def test_snapshot_save_load_preserve_grcv2_state_surface(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node({"label": "A"})
        node_1 = graph.add_node({"label": "B"})
        graph.add_edge(node_0, node_1, {"weight": 0.5})
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [
                    {"node_id": node_0, "payload": {"label": "A"}},
                    {"node_id": node_1, "payload": {"label": "B"}},
                ],
                "edges": [
                    {
                        "edge_id": 0,
                        "node_a": node_0,
                        "node_b": node_1,
                        "payload": {"weight": 0.5},
                    }
                ],
                "incidence": {"0": [0], "1": [0]},
            },
            "next_node_id": graph.next_node_id,
            "next_edge_id": graph.next_edge_id,
            "nodes": {"0": 1.0, "1": 0.5},
            "edges": {"0": 0.25},
        }
        model = GRCV2.from_config(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv2.json"
            model.save(str(path))
            restored = GRCV2.load(str(path))

        self.assertEqual(model.get_params().params_hash, restored.get_params().params_hash)
        self.assertEqual({0: 1.0, 1: 0.5}, restored.get_state().nodes)
        self.assertEqual((0,), tuple(restored.get_state().topology.iter_live_edge_ids()))
