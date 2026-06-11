"""Direct tests for the Phase 5 Iteration 4 GRCV3 transport baseline."""

from __future__ import annotations

from pathlib import Path
import math
import tempfile
import unittest

from pygrc.models import GRCV3
from pygrc.core import load_snapshot, WeightedGraphBackend


def _node_attributes(coherence: float) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": f"basin-{coherence}",
        "parent_id": None,
        "depth": 0,
    }


class GRCV3MetricLabelsTest(unittest.TestCase):
    """Validate metric, labels, potential, and flux for the Iteration 4 baseline."""

    def test_rebuild_transport_state_materializes_host_embedding_labels(self) -> None:
        graph = WeightedGraphBackend()
        node_left = graph.add_node({"chart_center_hint": [0.0, 0.0]})
        node_right = graph.add_node({"chart_center_hint": [1.0, 0.0]})
        edge_id = graph.add_edge(
            node_left,
            node_right,
            {"ambient_length": 3.5},
        )

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(node_left): _node_attributes(1.0),
                    str(node_right): _node_attributes(0.5),
                },
                "base_conductance": {str(edge_id): 1.0},
            },
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "frame_mode": "host_embedding",
                    "host_geometry_fields": ["chart_center_hint"],
                    "edge_label_selection": "all",
                },
            },
        )
        model.get_state().topology = graph

        model.rebuild_transport_state()

        state = model.get_state()
        self.assertIn("node_tensors", state.cached_quantities)
        self.assertIn(node_left, state.cached_quantities["node_tensors"])
        self.assertGreater(state.base_conductance[edge_id], 0.0)
        self.assertEqual(3.5, state.geometric_length[edge_id])
        self.assertEqual(
            "ambient_metric",
            state.edge_label_computation_mode["geometric_length"],
        )
        self.assertEqual(
            ["chart_center_hint"],
            state.edge_label_params["geometric_length"]["host_geometry_fields"],
        )
        self.assertIn(node_left, state.potential)
        self.assertIn(node_right, state.potential)
        self.assertAlmostEqual(
            state.flux[(edge_id, node_left)],
            -state.flux[(edge_id, node_right)],
            places=12,
        )
        self.assertAlmostEqual(
            abs(state.flux[(edge_id, min(node_left, node_right))]),
            state.flux_coupling[edge_id],
            places=12,
        )
        expected_delay = state.geometric_length[edge_id] / (
            1.0 + state.flux_coupling[edge_id] + 1e-9
        )
        self.assertTrue(
            math.isclose(
                expected_delay,
                state.temporal_delay[edge_id],
                rel_tol=1e-12,
                abs_tol=1e-12,
            )
        )

    def test_missing_host_coordinates_fall_back_to_intrinsic_surrogate(self) -> None:
        graph = WeightedGraphBackend()
        node_left = graph.add_node({})
        node_right = graph.add_node({})
        edge_id = graph.add_edge(node_left, node_right, {})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(node_left): _node_attributes(1.0),
                    str(node_right): _node_attributes(0.25),
                },
                "base_conductance": {str(edge_id): 1.0},
            },
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "frame_mode": "host_embedding",
                    "host_geometry_fields": ["chart_center_hint"],
                },
            },
        )
        model.get_state().topology = graph

        model.rebuild_transport_state()

        state = model.get_state()
        self.assertEqual(
            "intrinsic_surrogate",
            state.edge_label_computation_mode["geometric_length"],
        )
        self.assertEqual(
            "inverse_base_conductance",
            state.edge_label_params["geometric_length"]["source"],
        )
        self.assertGreater(state.geometric_length[edge_id], 0.0)

    def test_snapshot_roundtrip_preserves_materialized_transport_state(self) -> None:
        graph = WeightedGraphBackend()
        node_left = graph.add_node({"chart_center_hint": [0.0, 0.0]})
        node_right = graph.add_node({"chart_center_hint": [2.0, 0.0]})
        edge_id = graph.add_edge(node_left, node_right, {})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(node_left): _node_attributes(0.75),
                    str(node_right): _node_attributes(0.25),
                },
                "base_conductance": {str(edge_id): 1.0},
            },
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "frame_mode": "host_embedding",
                    "host_geometry_fields": ["chart_center_hint"],
                },
            },
        )
        model.get_state().topology = graph
        model.rebuild_transport_state()

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3-transport.json"
            model.save(str(path))
            snapshot = load_snapshot(path)
            restored = GRCV3.load(str(path))

        restored_state = restored.get_state()
        self.assertEqual(
            model.get_state().base_conductance,
            restored_state.base_conductance,
        )
        self.assertEqual(
            model.get_state().geometric_length,
            restored_state.geometric_length,
        )
        self.assertEqual(
            model.get_state().temporal_delay,
            restored_state.temporal_delay,
        )
        self.assertEqual(
            model.get_state().flux_coupling,
            restored_state.flux_coupling,
        )
        self.assertEqual(
            model.get_state().edge_label_computation_mode,
            restored_state.edge_label_computation_mode,
        )
        self.assertEqual(
            model.get_state().edge_label_params,
            restored_state.edge_label_params,
        )
        self.assertEqual(
            model.get_state().flux,
            restored_state.flux,
        )
        self.assertIn("edge_labels", snapshot)
        self.assertIn("base_conductance", snapshot["edge_labels"])
        self.assertIn("temporal_delay", snapshot["edge_labels"])
