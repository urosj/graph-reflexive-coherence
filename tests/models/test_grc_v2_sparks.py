"""Spark backend and event detection tests for Phase 4 Iteration 5."""

from __future__ import annotations

import unittest

from pygrc.core import InvalidParamsError
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


class GRCV2SparkDetectionTest(unittest.TestCase):
    """Validate the Iteration 5 spark backend and event surface."""

    def test_invalid_spark_backend_is_rejected(self) -> None:
        config = _valid_grcv2_config()
        evolution = dict(config["evolution"])
        evolution["spark_backend"] = "eigenvalue"
        config["evolution"] = evolution

        with self.assertRaises(InvalidParamsError):
            GRCV2.from_config(config)

    def test_step_emits_deterministic_cheeger_spark_events(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["lambda_birth"] = 1e9
        config["state"] = {
            "topology": {
                "nodes": [
                    {"node_id": 0, "payload": {}},
                    {"node_id": 1, "payload": {}},
                    {"node_id": 2, "payload": {}},
                    {"node_id": 3, "payload": {}},
                ],
                "edges": [
                    {"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}},
                    {"edge_id": 1, "node_a": 2, "node_b": 3, "payload": {}},
                ],
                "incidence": {"0": [0], "1": [0], "2": [1], "3": [1]},
            },
            "nodes": {"0": 2.0, "1": 1.0, "2": 2.0, "3": 1.0},
            "edges": {"0": 1.0, "1": 1.0},
        }
        model = GRCV2.from_config(config)

        result = model.step()

        spark_events = [event for event in result.events if event.kind == "spark"]
        split_init_events = [event for event in result.events if event.kind == "split_init"]
        self.assertEqual(2, len(spark_events))
        self.assertEqual(2, len(split_init_events))
        self.assertEqual(
            ["spark", "spark"],
            [event.kind for event in spark_events],
        )
        self.assertEqual([1, 3], [event.payload["sink_node_id"] for event in spark_events])
        self.assertEqual(
            [0, 1],
            [event.payload["candidate_rank"] for event in spark_events],
        )
        self.assertTrue(
            all(event.payload["backend"] == "cheeger_proxy" for event in spark_events)
        )
        self.assertTrue(
            all(event.payload["topology_event_kind"] == "soft_split" for event in spark_events)
        )
        self.assertEqual(2, result.observables["spark_count"])
        self.assertEqual(
            [1, 3],
            [
                record["payload"]["sink_node_id"]
                for record in model.get_state().cached_quantities["pending_topology_events"]
            ],
        )

    def test_equivalent_builds_emit_identical_spark_payloads(self) -> None:
        config_a = _valid_grcv2_config()
        config_b = _valid_grcv2_config()
        shared_state = {
            "topology": {
                "nodes": [
                    {"node_id": 0, "payload": {}},
                    {"node_id": 1, "payload": {}},
                    {"node_id": 2, "payload": {}},
                    {"node_id": 3, "payload": {}},
                ],
                "edges": [
                    {"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}},
                    {"edge_id": 1, "node_a": 2, "node_b": 3, "payload": {}},
                ],
                "incidence": {"0": [0], "1": [0], "2": [1], "3": [1]},
            },
            "nodes": {"0": 2.0, "1": 1.0, "2": 2.0, "3": 1.0},
            "edges": {"0": 1.0, "1": 1.0},
        }
        config_a["state"] = shared_state
        config_b["state"] = shared_state
        model_a = GRCV2.from_config(config_a)
        model_b = GRCV2.from_config(config_b)

        result_a = model_a.step()
        result_b = model_b.step()

        self.assertEqual(
            [(event.kind, event.payload) for event in result_a.events],
            [(event.kind, event.payload) for event in result_b.events],
        )
