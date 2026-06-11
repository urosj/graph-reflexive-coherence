"""Direct tests for the Phase 5 Iteration 5 GRCV3 identity baseline."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.core import WeightedGraphBackend, load_snapshot
from pygrc.models import GRCV3


def _basin_attributes(
    *,
    coherence: float,
    gradient: list[float],
    hessian: list[list[float]],
    basin_id: str | int,
    parent_id: str | int | None = None,
    depth: int = 0,
) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": gradient,
        "hessian": hessian,
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": parent_id,
        "depth": depth,
    }


class GRCV3HierarchyTest(unittest.TestCase):
    """Validate flux/geometric identity layers and deterministic hierarchy state."""

    def test_rebuild_identity_state_exposes_flux_and_geometric_layers(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({})
        center = graph.add_node({})
        right = graph.add_node({})
        edge_left = graph.add_edge(left, center, {})
        edge_right = graph.add_edge(center, right, {})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(left): _basin_attributes(
                        coherence=0.25,
                        gradient=[0.1, 0.0],
                        hessian=[[0.2, 0.0], [0.0, 0.2]],
                        basin_id=left,
                    ),
                    str(center): _basin_attributes(
                        coherence=1.0,
                        gradient=[0.0, 0.0],
                        hessian=[[2.0, 0.0], [0.0, 1.0]],
                        basin_id=center,
                    ),
                    str(right): _basin_attributes(
                        coherence=0.5,
                        gradient=[0.15, 0.0],
                        hessian=[[0.3, 0.0], [0.0, 0.25]],
                        basin_id=right,
                    ),
                },
                "flux": {
                    f"{edge_left}:{left}": 1.0,
                    f"{edge_left}:{center}": -1.0,
                    f"{edge_right}:{center}": -2.0,
                    f"{edge_right}:{right}": 2.0,
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph

        model.rebuild_identity_state()

        state = model.get_state()
        self.assertEqual({center}, state.sink_set)
        self.assertEqual({center: {left, center, right}}, state.basins)

        flux_identity = state.cached_quantities["flux_identity"]
        geometric_identity = state.cached_quantities["geometric_identity"]
        self.assertEqual([center], flux_identity["sink_nodes"])
        self.assertEqual([center], geometric_identity["seed_nodes"])
        self.assertEqual([center], geometric_identity["validated_basin_ids"])
        self.assertEqual(
            {str(left): center, str(center): center, str(right): center},
            geometric_identity["basin_id_by_node"],
        )

        self.assertEqual(center, state.nodes[left].basin_id)
        self.assertEqual(center, state.nodes[center].basin_id)
        self.assertEqual(center, state.nodes[right].basin_id)
        self.assertEqual({center: []}, state.hierarchy)

    def test_hierarchy_update_preserves_parent_and_depth_deterministically(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({})
        center = graph.add_node({})
        edge_id = graph.add_edge(left, center, {})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(left): _basin_attributes(
                        coherence=0.4,
                        gradient=[0.0, 0.0],
                        hessian=[[1.5, 0.0], [0.0, 1.0]],
                        basin_id="legacy-left",
                        parent_id="root",
                        depth=1,
                    ),
                    str(center): _basin_attributes(
                        coherence=0.8,
                        gradient=[0.0, 0.0],
                        hessian=[[2.0, 0.0], [0.0, 1.5]],
                        basin_id="legacy-center",
                        parent_id="root",
                        depth=1,
                    ),
                },
                "flux": {
                    f"{edge_id}:{left}": 1.0,
                    f"{edge_id}:{center}": -1.0,
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph

        model.rebuild_identity_state()

        state = model.get_state()
        self.assertEqual("root", state.nodes[left].parent_id)
        self.assertEqual("root", state.nodes[center].parent_id)
        self.assertEqual(1, state.nodes[left].depth)
        self.assertEqual(1, state.nodes[center].depth)
        self.assertEqual({"root": [center], center: []}, state.hierarchy)
        self.assertEqual(["root"], state.cached_quantities["hierarchy_roots"])

    def test_snapshot_roundtrip_preserves_hierarchy_and_identity_fields(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({})
        center = graph.add_node({})
        edge_id = graph.add_edge(left, center, {})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(left): _basin_attributes(
                        coherence=0.4,
                        gradient=[0.0, 0.0],
                        hessian=[[1.5, 0.0], [0.0, 1.0]],
                        basin_id="legacy-left",
                        parent_id="root",
                        depth=1,
                    ),
                    str(center): _basin_attributes(
                        coherence=0.8,
                        gradient=[0.0, 0.0],
                        hessian=[[2.0, 0.0], [0.0, 1.5]],
                        basin_id="legacy-center",
                        parent_id="root",
                        depth=1,
                    ),
                },
                "flux": {
                    f"{edge_id}:{left}": 1.0,
                    f"{edge_id}:{center}": -1.0,
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph
        model.rebuild_identity_state()

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3-hierarchy.json"
            model.save(str(path))
            snapshot = load_snapshot(path)
            restored = GRCV3.load(str(path))

        restored_state = restored.get_state()
        self.assertEqual(model.get_state().hierarchy, restored_state.hierarchy)
        self.assertEqual(model.get_state().sink_set, restored_state.sink_set)
        self.assertEqual(model.get_state().basins, restored_state.basins)
        self.assertEqual(
            model.get_state().nodes[left].parent_id,
            restored_state.nodes[left].parent_id,
        )
        self.assertEqual(
            model.get_state().nodes[left].depth,
            restored_state.nodes[left].depth,
        )
        self.assertEqual(
            model.get_state().nodes[left].basin_id,
            restored_state.nodes[left].basin_id,
        )
        self.assertIn("hierarchy", snapshot["basin_attributes"])
