"""Runtime persistence tests for Phase 4 Iteration 8."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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


class GRCV2RuntimePersistenceTest(unittest.TestCase):
    """Validate executable runtime persistence and reset behavior."""

    def test_snapshot_includes_v2_runtime_groups_and_event_records(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["h_thr"] = 0.0
        config["evolution"]["lambda_birth"] = 1e9
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
        model.step()

        snapshot = model.snapshot()

        self.assertEqual(
            [
                "metadata",
                "topology",
                "dynamics",
                "observables",
                "events",
                "reset_baseline",
            ],
            list(snapshot.keys()),
        )
        self.assertEqual("available", snapshot["reset_baseline"]["status"])
        self.assertEqual("GRCV2", snapshot["metadata"]["model_family"])
        self.assertEqual(model.get_params().params_hash, snapshot["metadata"]["params_hash"])
        self.assertEqual(model.get_state().step_index, snapshot["metadata"]["step_index"])
        self.assertEqual(model.get_state().event_log[0].kind, snapshot["events"][0]["kind"])
        self.assertIn("state", snapshot["dynamics"])

    def test_save_load_preserves_ability_to_continue_deterministically(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["h_thr"] = 0.0
        config["evolution"]["lambda_birth"] = 1e9
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
        model.step()

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv2-runtime.json"
            model.save(str(path))
            restored = GRCV2.load(str(path))

        continued_original = model.step()
        continued_restored = restored.step()

        self.assertEqual(model.get_params().params_hash, restored.get_params().params_hash)
        self.assertEqual(model.get_state().step_index, restored.get_state().step_index)
        self.assertEqual(model.get_state().time, restored.get_state().time)
        self.assertEqual(
            tuple(model.get_state().topology.iter_live_node_ids()),
            tuple(restored.get_state().topology.iter_live_node_ids()),
        )
        self.assertEqual(
            tuple(model.get_state().topology.iter_live_edge_ids()),
            tuple(restored.get_state().topology.iter_live_edge_ids()),
        )
        self.assertEqual(model.get_state().nodes, restored.get_state().nodes)
        self.assertEqual(model.get_state().edges, restored.get_state().edges)
        self.assertEqual(
            [(event.kind, event.payload) for event in continued_original.events],
            [(event.kind, event.payload) for event in continued_restored.events],
        )
        self.assertEqual(continued_original.observables, continued_restored.observables)

    def test_reset_restores_executable_construction_baseline(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["h_thr"] = 0.0
        config["evolution"]["lambda_birth"] = 1e9
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 2.0, "1": 1.0},
            "edges": {"0": 1.0},
            "step_index": 0,
            "time": 0.0,
        }
        model = GRCV2.from_config(config)
        initial_snapshot = model.snapshot()
        model.step()
        model.step()

        model.reset()

        self.assertEqual(initial_snapshot, model.snapshot())
