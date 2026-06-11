"""Direct tests for the Phase 5 Iteration 6 GRCV3 spark baseline."""

from __future__ import annotations

import unittest

from pygrc.core import WeightedGraphBackend
from pygrc.models import GRCV3


def _attributes(
    *,
    coherence: float,
    hessian: list[list[float]],
    basin_id: str | int,
    parent_id: str | int | None = None,
    depth: int = 0,
) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": hessian,
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": parent_id,
        "depth": depth,
    }


class GRCV3SparkTest(unittest.TestCase):
    """Validate signed-Hessian spark detection and soft split integration."""

    def test_candidate_degeneracy_does_not_force_completed_spark(self) -> None:
        graph = WeightedGraphBackend()
        left = graph.add_node({})
        node_id = graph.add_node({})
        right = graph.add_node({})
        edge_left = graph.add_edge(left, node_id, {})
        edge_right = graph.add_edge(node_id, right, {})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(left): _attributes(
                        coherence=0.0,
                        hessian=[[2.0, 0.0], [0.0, 2.0]],
                        basin_id=left,
                    ),
                    str(node_id): _attributes(
                        coherence=0.0,
                        hessian=[[0.0001, 0.0], [0.0, 2.0]],
                        basin_id=node_id,
                    ),
                    str(right): _attributes(
                        coherence=0.0,
                        hessian=[[2.0, 0.0], [0.0, 2.0]],
                        basin_id=right,
                    ),
                },
                "base_conductance": {
                    str(edge_left): 1.0,
                    str(edge_right): 1.0,
                },
                "hessian_sign": 1,
            },
            params={
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    "backend_selections": {
                        "spark": {
                            "name": "signed_hessian_plus_attractor_delta",
                            "params": {"min_child_basins": 3},
                        }
                    }
                },
            },
        )
        model.get_state().topology = graph
        model.rebuild_identity_state()

        candidates = model.detect_spark_candidates()
        applied = model.apply_spark_candidates(candidates)

        self.assertEqual(1, len(candidates))
        self.assertEqual("spark_candidate", candidates[0].kind)
        self.assertTrue(any(event.kind == "split_init" for event in applied))
        self.assertTrue(any(event.kind == "spark_pending" for event in applied))
        self.assertFalse(any(event.kind == "spark" for event in applied))

    def test_completed_spark_creates_child_basins_with_ancestry(self) -> None:
        graph = WeightedGraphBackend()
        parent = graph.add_node({})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(parent): _attributes(
                        coherence=1.2,
                        hessian=[[0.0001, 0.0], [0.0, 2.0]],
                        basin_id=parent,
                    )
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1},
        )
        model.get_state().topology = graph
        model.rebuild_identity_state()

        events = model.rebuild_spark_state()
        state = model.get_state()

        self.assertTrue(any(event.kind == "spark_candidate" for event in events))
        self.assertTrue(any(event.kind == "split_init" for event in events))
        self.assertTrue(any(event.kind == "spark" for event in events))

        split_registry = state.cached_quantities["split_registry"]
        self.assertEqual(1, len(split_registry))
        entry = next(iter(split_registry.values()))
        child_node_ids = tuple(entry["child_node_ids"])
        self.assertEqual(2, len(child_node_ids))
        for child_node_id in child_node_ids:
            self.assertIn(child_node_id, state.nodes)
            self.assertEqual(parent, state.nodes[child_node_id].parent_id)
            self.assertEqual(1, state.nodes[child_node_id].depth)
            self.assertEqual(child_node_id, state.nodes[child_node_id].basin_id)

    def test_split_progression_is_deterministic_and_removes_parent_on_completion(self) -> None:
        graph = WeightedGraphBackend()
        parent = graph.add_node({})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(parent): _attributes(
                        coherence=1.0,
                        hessian=[[0.0001, 0.0], [0.0, 2.0]],
                        basin_id=parent,
                    )
                },
                "hessian_sign": 1,
            },
            params={"dt": 0.1, "evolution": {"tau_split": 2.0}},
        )
        model.get_state().topology = graph
        model.rebuild_identity_state()
        model.rebuild_spark_state()

        first_progress = model.advance_split_state()
        second_progress = model.advance_split_state()
        state = model.get_state()
        registry = state.cached_quantities["split_registry"]
        entry = next(iter(registry.values()))

        self.assertEqual(["split_progress"], [event.kind for event in first_progress])
        self.assertEqual(
            ["split_progress", "split_complete"],
            [event.kind for event in second_progress],
        )
        self.assertTrue(bool(entry["complete"]))
        self.assertFalse(state.topology.has_node(parent))

    def test_split_progression_preserves_external_conductance_budget(self) -> None:
        graph = WeightedGraphBackend()
        neighbor = graph.add_node({})
        parent = graph.add_node({})
        external_edge = graph.add_edge(parent, neighbor, {})

        model = GRCV3.from_state(
            state={
                "nodes": {
                    str(neighbor): _attributes(
                        coherence=0.2,
                        hessian=[[2.0, 0.0], [0.0, 2.0]],
                        basin_id=neighbor,
                    ),
                    str(parent): _attributes(
                        coherence=1.0,
                        hessian=[[0.0001, 0.0], [0.0, 2.0]],
                        basin_id=parent,
                    ),
                },
                "base_conductance": {str(external_edge): 2.0},
                "hessian_sign": 1,
            },
            params={"dt": 0.1, "evolution": {"tau_split": 2.0}},
        )
        model.get_state().topology = graph
        model.rebuild_identity_state()
        model.rebuild_spark_state()

        model.advance_split_state()
        state = model.get_state()
        split_registry = state.cached_quantities["split_registry"]
        entry = next(iter(split_registry.values()))
        child_node_ids = tuple(entry["child_node_ids"])
        external_weights = []
        for edge_id in state.topology.iter_live_edge_ids():
            node_a, node_b = state.topology.edge_endpoints(edge_id)
            if neighbor not in {node_a, node_b}:
                continue
            if parent in {node_a, node_b} or any(child_id in {node_a, node_b} for child_id in child_node_ids):
                external_weights.append(state.base_conductance[edge_id])

        self.assertAlmostEqual(2.0, sum(external_weights), places=4)
