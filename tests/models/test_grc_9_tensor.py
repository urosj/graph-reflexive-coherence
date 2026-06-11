"""Row-tensor and metric-surface tests for the Phase 6 GRC9 shell."""

from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from pygrc.core import load_snapshot
from pygrc.models import GRC9


def _tensor_config() -> dict[str, object]:
    return {
        "dt": 0.1,
        "evolution": {
            "lambda_c": 2.0,
            "xi_c": 0.5,
            "zeta_c": 0.25,
            "alpha": 1.0,
            "beta": 1.0,
            "gamma": 1.0,
            "delta": 1.0,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-6,
        },
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def _row_tensor_state() -> dict[str, object]:
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
        "node_coherence": {"0": 1.0, "1": 3.0, "2": 2.0, "3": 5.0},
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
                "conductance": 0.5,
                "flux_uv": 0.4,
            },
        },
        "budget_target": 11.0,
    }


def _curvature_state() -> dict[str, object]:
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
        "node_coherence": {"0": 1.0, "1": 2.0, "2": 0.5},
        "port_edges": {
            "0": {
                "node_u": 0,
                "port_u": 1,
                "node_v": 1,
                "port_v": 1,
                "conductance": 2.0,
                "flux_uv": 0.3,
            },
            "1": {
                "node_u": 1,
                "port_u": 4,
                "node_v": 2,
                "port_v": 1,
                "conductance": 0.5,
                "flux_uv": -0.2,
            },
        },
    }


class GRC9TensorMetricTest(unittest.TestCase):
    """Validate the Iteration 3 row-tensor and metric surface."""

    def test_geometry_accumulates_row_mismatch_deterministically(self) -> None:
        config = _tensor_config()
        config["state"] = _row_tensor_state()
        model = GRC9.from_config(config)

        model._compute_geometry()

        row_neighborhoods = model.get_state().cached_quantities["row_neighborhoods"]
        row_mismatch_terms = model.get_state().cached_quantities["row_mismatch_terms"]
        row_tensor_diagonal = model.get_state().cached_quantities["row_tensor_diagonal"]

        self.assertEqual((0, 1), row_neighborhoods[0][1])
        self.assertEqual((2,), row_neighborhoods[0][2])
        self.assertEqual((), row_neighborhoods[0][3])
        self.assertAlmostEqual(4.5, row_mismatch_terms[0][1])
        self.assertAlmostEqual(4.0, row_mismatch_terms[0][2])
        self.assertAlmostEqual(0.0, row_mismatch_terms[0][3])
        self.assertEqual(
            [6.5625, 6.0625, 2.0625],
            [round(value, 4) for value in row_tensor_diagonal[0]],
        )

    def test_metric_update_uses_only_edge_local_inputs_when_curvature_is_none(self) -> None:
        base_config = _tensor_config()
        base_state = _curvature_state()
        base_config["state"] = base_state

        variant_config = _tensor_config()
        variant_state = _curvature_state()
        variant_state["port_edges"] = {
            **variant_state["port_edges"],
            "1": {
                "node_u": 1,
                "port_u": 4,
                "node_v": 2,
                "port_v": 1,
                "conductance": 99.0,
                "flux_uv": -0.2,
            },
        }
        variant_config["state"] = variant_state

        base_model = GRC9.from_config(base_config)
        variant_model = GRC9.from_config(variant_config)

        base_model._compute_metric()
        variant_model._compute_metric()

        expected = math.exp(
            -1.0 * (1.0 + 2.0) / 2.0
            -1.0 * ((1.0 - 2.0) ** 2) / 2.0
            -1.0 * ((0.3**2) / 2.0)
        )
        self.assertAlmostEqual(expected, base_model.get_state().port_edges[0].conductance)
        self.assertAlmostEqual(
            base_model.get_state().port_edges[0].conductance,
            variant_model.get_state().port_edges[0].conductance,
        )

    def test_metric_integrates_curvature_backend_selection(self) -> None:
        none_config = _tensor_config()
        none_config["state"] = _curvature_state()

        forman_config = _tensor_config()
        forman_config["state"] = _curvature_state()
        forman_config["constitutive_semantic_modes"] = {
            **dict(forman_config["constitutive_semantic_modes"]),
            "curvature_backend": "forman",
        }

        ollivier_config = _tensor_config()
        ollivier_config["state"] = _curvature_state()
        ollivier_config["constitutive_semantic_modes"] = {
            **dict(ollivier_config["constitutive_semantic_modes"]),
            "curvature_backend": "ollivier",
        }

        none_model = GRC9.from_config(none_config)
        forman_model = GRC9.from_config(forman_config)
        ollivier_model = GRC9.from_config(ollivier_config)

        none_model._compute_metric()
        forman_model._compute_metric()
        ollivier_model._compute_metric()

        self.assertEqual(0.0, none_model.get_state().cached_quantities["edge_curvature"][0])
        self.assertNotEqual(0.0, forman_model.get_state().cached_quantities["edge_curvature"][0])
        self.assertNotEqual(0.0, ollivier_model.get_state().cached_quantities["edge_curvature"][0])
        self.assertNotEqual(
            none_model.get_state().port_edges[0].conductance,
            forman_model.get_state().port_edges[0].conductance,
        )
        self.assertNotEqual(
            none_model.get_state().port_edges[0].conductance,
            ollivier_model.get_state().port_edges[0].conductance,
        )

    def test_edge_labels_are_explicit_and_separately_serialized(self) -> None:
        config = _tensor_config()
        config["state"] = _curvature_state()
        model = GRC9.from_config(config)

        model._compute_geometry()
        model._compute_metric()
        model._compute_edge_labels()

        state = model.get_state()
        edge_id = 0
        self.assertEqual("induced_intrinsic", state.edge_label_computation_mode["geometric_length"])
        self.assertEqual("absolute_flux", state.edge_label_computation_mode["flux_coupling"])
        self.assertEqual("transport_ratio", state.edge_label_computation_mode["temporal_delay"])
        self.assertAlmostEqual(abs(state.port_edges[edge_id].flux_uv), state.flux_coupling[edge_id])
        expected_delay = state.geometric_length[edge_id] / (
            1.0 + state.flux_coupling[edge_id] + 1e-6
        )
        self.assertAlmostEqual(expected_delay, state.temporal_delay[edge_id])

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grc9_labels.json"
            model.save(str(path))
            snapshot = load_snapshot(path)

        self.assertIn("edge_labels", snapshot)
        self.assertEqual(
            "induced_intrinsic",
            snapshot["edge_labels"]["edge_label_computation_mode"]["geometric_length"],
        )
        self.assertEqual(
            "transport_ratio",
            snapshot["edge_labels"]["edge_label_computation_mode"]["temporal_delay"],
        )
        self.assertEqual(
            "absolute_flux",
            snapshot["edge_labels"]["edge_label_computation_mode"]["flux_coupling"],
        )
        self.assertEqual(
            "all",
            snapshot["edge_labels"]["edge_label_params"]["selection"],
        )
