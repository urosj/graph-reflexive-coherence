"""Conductance and edge-label tests for the Phase 4 GRCV2 baseline."""

from __future__ import annotations

import math
import unittest

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
            "temporal_v0": 1.0,
            "temporal_rho": 2.0,
            "eps_tau": 1e-12,
        },
        "constitutive_semantic_modes": {
            "curvature_backend": "none",
            "frame_mode": "combinatorial",
            "boundary_mode": "prune",
            "split_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def _weighted_state(*, edge_payload: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "topology": {
            "nodes": [{"node_id": 0, "payload": {}}, {"node_id": 1, "payload": {}}],
            "edges": [
                {
                    "edge_id": 0,
                    "node_a": 0,
                    "node_b": 1,
                    "payload": dict(edge_payload or {}),
                }
            ],
            "incidence": {"0": [0], "1": [0]},
        },
        "nodes": {"0": 2.0, "1": 1.0},
        "flux": {"0:0": 0.5, "0:1": -0.5},
    }


class GRCV2MetricLabelsTest(unittest.TestCase):
    """Validate deterministic conductance and edge-label behavior."""

    def test_geometry_computes_paper_style_tensor_terms(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = _weighted_state()
        model = GRCV2.from_config(config)

        model.step()

        state = model.get_state()
        node_tensor_0 = state.cached_quantities["node_tensors"][0]
        node_tensor_1 = state.cached_quantities["node_tensors"][1]
        self.assertEqual((1,), node_tensor_0["basis_neighbors"])
        self.assertEqual((0,), node_tensor_0["basis_edges"])
        self.assertTrue(math.isclose(2.0, node_tensor_0["density_term"], rel_tol=1e-12, abs_tol=1e-12))
        self.assertEqual((1.0,), node_tensor_0["gradient_diagonal"])
        self.assertTrue(math.isclose(0.25, node_tensor_0["flux_feedback_term"], rel_tol=1e-12, abs_tol=1e-12))
        self.assertEqual((3.25,), node_tensor_0["tensor_diagonal"])
        self.assertEqual((2.25,), node_tensor_1["tensor_diagonal"])

    def test_quadratic_site_potential_contributes_to_runtime_potential(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = _weighted_state()
        model = GRCV2.from_config(config)

        model.step()

        state = model.get_state()
        conductance = state.edges[0]
        expected_0 = conductance * (2.0 - 1.0) - (2.0 * 2.0)
        expected_1 = conductance * (1.0 - 2.0) - (2.0 * 1.0)
        self.assertTrue(math.isclose(expected_0, state.potential[0], rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(expected_1, state.potential[1], rel_tol=1e-12, abs_tol=1e-12))

    def test_flux_uses_negative_eta_weighted_potential_gradient(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = _weighted_state()
        model = GRCV2.from_config(config)

        model.step()

        state = model.get_state()
        expected_flux = -1.0 * state.edges[0] * (state.potential[0] - state.potential[1])
        self.assertTrue(math.isclose(expected_flux, state.flux[(0, 0)], rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(-expected_flux, state.flux[(0, 1)], rel_tol=1e-12, abs_tol=1e-12))

    def test_step_computes_paper_style_exponential_conductance_and_label_metadata(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = _weighted_state()
        model = GRCV2.from_config(config)

        model.step()

        state = model.get_state()
        expected_conductance = math.exp(
            -1.0 * (2.0 + 1.0) / 2.0
            - 1.0 * ((2.0 - 1.0) ** 2) / 2.0
            - 1.0 * (0.5**2) / 2.0
            - 1.0 * 0.0
        )
        self.assertTrue(
            math.isclose(
                expected_conductance,
                state.edges[0],
                rel_tol=1e-12,
                abs_tol=1e-12,
            )
        )
        self.assertIn("geometric_length", state.cached_quantities["edge_label_computation_mode"])
        self.assertIn("temporal_delay", state.cached_quantities["edge_label_computation_mode"])
        self.assertIn("flux_coupling", state.cached_quantities["edge_label_computation_mode"])
        self.assertEqual("all", state.cached_quantities["edge_label_params"]["selection"])
        self.assertEqual({0: 0.0}, state.cached_quantities["edge_curvature"])

    def test_forman_curvature_backend_computes_real_edge_curvature(self) -> None:
        config = _valid_grcv2_config()
        config["constitutive_semantic_modes"]["curvature_backend"] = "forman"
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

        model.step()

        state = model.get_state()
        self.assertTrue(math.isclose(1.0, state.cached_quantities["edge_curvature"][0], rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(1.0, state.cached_quantities["edge_curvature"][1], rel_tol=1e-12, abs_tol=1e-12))

    def test_ollivier_curvature_backend_computes_real_edge_curvature(self) -> None:
        config = _valid_grcv2_config()
        config["constitutive_semantic_modes"]["curvature_backend"] = "ollivier"
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

        model.step()

        state = model.get_state()
        self.assertTrue(math.isclose(0.0, state.cached_quantities["edge_curvature"][0], rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(0.0, state.cached_quantities["edge_curvature"][1], rel_tol=1e-12, abs_tol=1e-12))

    def test_edge_label_selection_subset_omits_unselected_labels(self) -> None:
        config = _valid_grcv2_config()
        modes = dict(config["constitutive_semantic_modes"])
        modes["edge_label_selection"] = ["flux_coupling"]
        config["constitutive_semantic_modes"] = modes
        config["state"] = _weighted_state()
        model = GRCV2.from_config(config)

        model.step()

        state = model.get_state()
        self.assertEqual({}, state.geometric_length)
        self.assertEqual({}, state.temporal_delay)
        self.assertEqual({0: 0.5}, state.flux_coupling)
        self.assertEqual(
            {"flux_coupling": "absolute_flux"},
            state.cached_quantities["edge_label_computation_mode"],
        )
        self.assertEqual(
            ("flux_coupling",),
            state.cached_quantities["edge_label_params"]["selection"],
        )

    def test_host_embedding_uses_ambient_edge_length(self) -> None:
        config = _valid_grcv2_config()
        modes = dict(config["constitutive_semantic_modes"])
        modes["frame_mode"] = "host_embedding"
        modes["host_geometry_fields"] = ["positions"]
        config["constitutive_semantic_modes"] = modes
        config["state"] = _weighted_state(edge_payload={"ambient_length": 3.5})
        model = GRCV2.from_config(config)

        model.step()

        state = model.get_state()
        self.assertEqual(3.5, state.geometric_length[0])
        self.assertEqual(
            "ambient_metric",
            state.cached_quantities["edge_label_computation_mode"]["geometric_length"],
        )

    def test_temporal_delay_uses_transport_ratio_formula(self) -> None:
        config = _valid_grcv2_config()
        config["state"] = _weighted_state()
        model = GRCV2.from_config(config)

        model.step()

        state = model.get_state()
        expected = state.geometric_length[0] / (1.0 + 2.0 * state.flux_coupling[0] + 1e-12)
        self.assertTrue(math.isclose(expected, state.temporal_delay[0], rel_tol=1e-12, abs_tol=1e-12))

    def test_metric_and_labels_are_repeatable_for_equivalent_builds(self) -> None:
        config_a = _valid_grcv2_config()
        config_a["state"] = _weighted_state()
        config_b = _valid_grcv2_config()
        config_b["state"] = _weighted_state()
        model_a = GRCV2.from_config(config_a)
        model_b = GRCV2.from_config(config_b)

        result_a = model_a.step()
        result_b = model_b.step()

        self.assertEqual(model_a.get_state().edges, model_b.get_state().edges)
        self.assertEqual(model_a.get_state().geometric_length, model_b.get_state().geometric_length)
        self.assertEqual(model_a.get_state().temporal_delay, model_b.get_state().temporal_delay)
        self.assertEqual(model_a.get_state().flux_coupling, model_b.get_state().flux_coupling)
        self.assertEqual(result_a.observables, result_b.observables)
