"""Step-skeleton tests for the Phase 4 GRCV2 baseline."""

from __future__ import annotations

import unittest

from pygrc.core import GRCEvent, StepResult, WeightedGraphBackend
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
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


class GRCV2StepSkeletonTest(unittest.TestCase):
    """Validate the executable step skeleton introduced in Phase 4 Iteration 2."""

    def test_step_executes_and_returns_real_step_result(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        graph.add_edge(node_0, node_1)
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "next_node_id": graph.next_node_id,
            "next_edge_id": graph.next_edge_id,
            "nodes": {"0": 1.0, "1": 0.5},
        }
        model = GRCV2.from_config(config)

        result = model.step()

        self.assertIsInstance(result, StepResult)
        self.assertEqual(1, result.step_index)
        self.assertEqual(0.1, result.time)
        self.assertEqual([], result.events)
        self.assertEqual(
            (
                "compute_geometry",
                "compute_metric",
                "compute_edge_labels",
                "build_laplacian",
                "compute_potential",
                "compute_flux",
                "detect_identities",
                "detect_events",
                "apply_topology_changes",
                "apply_front_birth",
                "apply_boundary_behavior",
                "apply_continuity",
                "enforce_budget",
                "compute_observables",
            ),
            result.bookkeeping["step_order"],
        )

    def test_step_populates_cached_trace_and_updates_state_time(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())

        result = model.step()

        self.assertEqual(result.bookkeeping["step_order"], model.get_state().cached_quantities["last_step_trace"])
        self.assertEqual(1, model.get_state().step_index)
        self.assertEqual(0.1, model.get_state().time)

    def test_run_uses_executable_step_surface(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())

        results = model.run(2)

        self.assertEqual(2, len(results))
        self.assertEqual([1, 2], [result.step_index for result in results])

    def test_step_skeleton_preserves_flux_antisymmetry(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
                "edges": [{"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}}],
                "incidence": {"0": [0], "1": [0]},
            },
            "nodes": {"0": 2.0, "1": 1.0},
            "edges": {"0": 0.5},
        }
        model = GRCV2.from_config(config)

        model.step()

        self.assertEqual(
            model.get_state().flux[(0, 0)],
            -model.get_state().flux[(0, 1)],
        )

    def test_step_detects_sinks_from_current_flux(self) -> None:
        config = _valid_grcv2_config()
        config["evolution"]["lambda_birth"] = 0.0
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

        result = model.step()

        self.assertEqual({1}, model.get_state().sink_set)
        self.assertEqual(1, result.observables["sink_count"])
        self.assertEqual({1: {0, 1}}, model.get_state().basins)
        self.assertEqual({0: 1, 1: None}, model.get_state().cached_quantities["successor_map"])

    def test_step_keeps_event_surface_structured(self) -> None:
        model = GRCV2.from_config(_valid_grcv2_config())

        result = model.step()

        self.assertTrue(all(isinstance(event, GRCEvent) for event in result.events))

    def test_step_extracts_basins_by_successor_composition(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [
                    {"node_id": 0, "payload": {}},
                    {"node_id": 1, "payload": {}},
                    {"node_id": 2, "payload": {}},
                ],
                "edges": [
                    {"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}},
                    {"edge_id": 1, "node_a": 1, "node_b": 2, "payload": {}},
                ],
                "incidence": {"0": [0], "1": [0, 1], "2": [1]},
            },
            "nodes": {"0": 3.0, "1": 2.0, "2": 1.0},
            "edges": {"0": 1.0, "1": 1.0},
        }
        model = GRCV2.from_config(config)

        model.step()

        self.assertEqual({2}, model.get_state().sink_set)
        self.assertEqual({2: {0, 1, 2}}, model.get_state().basins)

    def test_sink_requires_non_negative_incoming_flux_from_every_neighbor(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = {
            "topology": {
                "nodes": [
                    {"node_id": 0, "payload": {}},
                    {"node_id": 1, "payload": {}},
                    {"node_id": 2, "payload": {}},
                ],
                "edges": [
                    {"edge_id": 0, "node_a": 0, "node_b": 1, "payload": {}},
                    {"edge_id": 1, "node_a": 1, "node_b": 2, "payload": {}},
                ],
                "incidence": {"0": [0], "1": [0, 1], "2": [1]},
            },
            "nodes": {"0": 1.0, "1": 1.0, "2": 1.0},
            "edges": {"0": 1.0, "1": 1.0},
        }
        model = GRCV2.from_config(config)
        state = model.get_state()
        state.flux = {
            (0, 0): 2.0,
            (0, 1): -2.0,
            (1, 1): 0.5,
            (1, 2): -0.5,
        }

        model._detect_identities()

        self.assertNotIn(1, model.get_state().sink_set)
