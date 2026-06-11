"""Hybrid spark tests for the Phase 7 GRC9V3 shell."""

from __future__ import annotations

from collections import deque
from pathlib import Path
import tempfile
import unittest

from pygrc.models import GRC9V3
from pygrc.models.grc_9_v3_sparks import (
    apply_mechanical_expansion,
    evaluate_child_basin_stabilization,
    register_completed_hybrid_spark,
)


def _saturated_candidate_state() -> dict[str, object]:
    nodes = [{"node_id": 0, "payload": {"role": "candidate"}}]
    edges = []
    incidence: dict[str, list[int]] = {"0": []}
    node_states: dict[str, dict[str, object]] = {
        "0": {
            "coherence": 9.0,
            "gradient_row_basis": [0.0, 0.0, 0.0],
            "signed_hessian_row_basis": [-0.1, 0.2, 0.3],
            "basin_mass": 9.0,
            "basin_id": "root",
            "depth": 0,
        }
    }
    port_edges: dict[str, dict[str, object]] = {}
    for port_index in range(9):
        leaf_node_id = port_index + 1
        edge_id = port_index
        nodes.append({"node_id": leaf_node_id, "payload": {"role": "boundary"}})
        incidence[str(leaf_node_id)] = [edge_id]
        incidence["0"].append(edge_id)
        edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": 0, "slot": port_index},
                "endpoint_b": {"node_id": leaf_node_id, "slot": 0},
                "payload": {"kind": "boundary"},
            }
        )
        node_states[str(leaf_node_id)] = {
            "coherence": 1.0,
            "gradient_row_basis": [1.0, 0.0, 0.0],
            "signed_hessian_row_basis": [1.0, 1.0, 1.0],
            "basin_mass": 1.0,
            "basin_id": leaf_node_id,
        }
        port_edges[str(edge_id)] = {
            "node_u": 0,
            "port_u": port_index + 1,
            "node_v": leaf_node_id,
            "port_v": 1,
            "conductance": 1.0,
            "flux_uv": 0.0,
        }

    return {
        "topology": {
            "nodes": nodes,
            "edges": edges,
            "incidence": incidence,
            "port_structure": {},
        },
        "nodes": node_states,
        "port_edges": port_edges,
        "sink_set": [0],
        "basins": {"0": list(range(10))},
    }


def _spark_params(
    *,
    evolution_overrides: dict[str, object] | None = None,
    **modes: object,
) -> dict[str, object]:
    evolution = {
        "eps_gradient": 0.01,
        "eps_hessian": 0.01,
        "eps_spark": 0.0,
        "D_eff_target": 30,
        "w_bond": 1.0,
        "alpha": 1e-12,
        "beta": 1e-12,
        "gamma": 1e-12,
        "kappa_c": 1e-12,
        "site_potential_params": {"mu": 0.0, "scale": 0.0},
    }
    if evolution_overrides is not None:
        evolution.update(evolution_overrides)
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": dict(modes),
    }


def _is_connected(model: GRC9V3) -> bool:
    state = model.get_state()
    live_nodes = set(state.topology.iter_live_node_ids())
    if not live_nodes:
        return True
    start = min(live_nodes)
    seen = {start}
    queue: deque[int] = deque([start])
    while queue:
        node_id = queue.popleft()
        for edge_id in state.topology.incident_edge_ids(node_id):
            edge = state.port_edges[edge_id]
            other = edge.node_v if edge.node_u == node_id else edge.node_u
            if other not in seen:
                seen.add(other)
                queue.append(other)
    return seen == live_nodes


class GRC9V3HybridSparkTest(unittest.TestCase):
    """Validate Phase 7 Iteration 4 hybrid spark behavior."""

    def test_candidate_detection_does_not_complete_or_expand_by_itself(self) -> None:
        model = GRC9V3.from_state(
            state=_saturated_candidate_state(),
            params=_spark_params(),
        )

        candidates = model.detect_hybrid_spark_candidates()

        modes = dict(model.get_params().constitutive_semantic_modes)
        self.assertEqual("current_hybrid_signed_hessian", modes["spark_lane"])
        self.assertEqual(1, len(candidates))
        self.assertEqual("hybrid_spark_candidate", candidates[0].kind)
        self.assertEqual(9, candidates[0].payload["active_degree"])
        self.assertTrue(candidates[0].payload["saturation_gate"])
        self.assertTrue(candidates[0].payload["basin_interior_gate"])
        self.assertTrue(candidates[0].payload["signed_hessian_degeneracy_gate"])
        self.assertNotIn("spark_lane", candidates[0].payload)
        self.assertNotIn("lane_b_candidate_hit", candidates[0].payload)
        self.assertNotIn("column_h", candidates[0].payload)
        self.assertNotIn("current_column_h_by_node", model.get_state().cached_quantities)
        self.assertEqual([], model.get_state().event_log)
        self.assertTrue(model.get_state().topology.has_node(0))

    def test_lane_a_ignores_column_h_like_threshold_by_default(self) -> None:
        state_payload = _saturated_candidate_state()
        state_payload["nodes"]["0"]["signed_hessian_row_basis"] = [0.2, 0.3, 0.4]
        model = GRC9V3.from_state(
            state=state_payload,
            params=_spark_params(evolution_overrides={"eps_column_h": 100.0}),
        )

        candidates = model.detect_hybrid_spark_candidates()

        self.assertEqual([], candidates)
        self.assertNotIn("current_column_h_by_node", model.get_state().cached_quantities)

    def test_mechanical_expansion_with_module_sink_gain_completes_spark(self) -> None:
        state_payload = _saturated_candidate_state()
        state_payload["coarse_cache"] = {"stale": {"field": "coherence"}}
        model = GRC9V3.from_state(
            state=state_payload,
            params=_spark_params(),
        )

        emitted_events = model.apply_hybrid_sparks()
        event_kinds = [event.kind for event in emitted_events]
        state = model.get_state()

        self.assertEqual(
            [
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
            ],
            event_kinds,
        )
        self.assertNotIn("spark_lane", emitted_events[0].payload)
        self.assertNotIn("lane_b_candidate_hit", emitted_events[0].payload)
        self.assertNotIn("column_h", emitted_events[0].payload)
        self.assertFalse(state.topology.has_node(0))
        self.assertEqual(1, len(state.expansion_registry))
        self.assertIn("hybrid_spark_completed", [event.kind for event in state.event_log])
        self.assertTrue(
            state.cached_quantities["last_child_basin_stabilization"][
                "stabilization_pass"
            ]
        )
        self.assertGreaterEqual(
            state.cached_quantities["last_child_basin_stabilization"][
                "stable_child_basin_count"
            ],
            1,
        )
        self.assertAlmostEqual(18.0, emitted_events[1].payload["budget_before"])
        self.assertAlmostEqual(18.0, emitted_events[1].payload["budget_after"])
        self.assertAlmostEqual(0.0, emitted_events[1].payload["budget_error"])
        self.assertEqual(
            "expansion_transfer_unit_measure",
            emitted_events[1].payload["budget_preservation_path"],
        )
        self.assertEqual({}, state.coarse_cache)
        self.assertEqual(
            "hybrid_expansion_topology_change",
            state.cached_quantities["coarse_cache_invalidation_reason"],
        )
        self.assertTrue(_is_connected(model))

    def test_mechanical_expansion_can_assign_nonzero_core_coherence(self) -> None:
        model = GRC9V3.from_state(
            state=_saturated_candidate_state(),
            params=_spark_params(
                evolution_overrides={"expansion_core_coherence_fraction": 0.25},
            ),
        )

        emitted_events = model.apply_hybrid_sparks()
        expansion_event = emitted_events[1]
        core_node_id = int(expansion_event.payload["module_node_ids"][0])

        self.assertAlmostEqual(0.25, expansion_event.payload["core_coherence_fraction"])
        self.assertAlmostEqual(2.25, model.get_state().nodes[core_node_id].coherence)
        self.assertAlmostEqual(18.0, expansion_event.payload["budget_before"])
        self.assertAlmostEqual(18.0, expansion_event.payload["budget_after"])

    def test_mechanical_expansion_registry_survives_snapshot_round_trip(self) -> None:
        model = GRC9V3.from_state(
            state=_saturated_candidate_state(),
            params=_spark_params(),
        )
        model.apply_hybrid_sparks()

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grc9v3_spark.json"
            model.save(str(path))
            restored = GRC9V3.load(str(path))

        restored_registry = restored.get_state().expansion_registry
        self.assertEqual(1, len(restored_registry))
        record = next(iter(restored_registry.values()))
        self.assertEqual(0, record.parent_sink_id)
        self.assertEqual((1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0), record.distribution_weights)
        self.assertTrue(all(restored.get_state().topology.has_node(node_id) for node_id in record.module_node_ids))

    def test_stabilized_child_basin_registers_completed_spark_and_hierarchy(self) -> None:
        model = GRC9V3.from_state(
            state=_saturated_candidate_state(),
            params=_spark_params(),
        )
        candidate_event = model.detect_hybrid_spark_candidates()[0]
        state = model.get_state()
        expansion_event = apply_mechanical_expansion(
            state,
            candidate_event,
            evolution=model.get_params().evolution,
            modes=model.get_params().constitutive_semantic_modes,
            source_family=model.MODEL_FAMILY,
        )
        stabilized_child = int(expansion_event.payload["module_node_ids"][1])
        state.cached_quantities["geometric_identity"] = {
            "seed_nodes": [stabilized_child],
        }

        evidence = evaluate_child_basin_stabilization(state, expansion_event)
        completed_event = register_completed_hybrid_spark(
            state,
            candidate_event,
            expansion_event,
            evidence,
            source_family=model.MODEL_FAMILY,
        )

        self.assertIsNotNone(completed_event)
        assert completed_event is not None
        self.assertEqual("hybrid_spark_completed", completed_event.kind)
        self.assertEqual([stabilized_child], completed_event.payload["stabilized_child_node_ids"])
        self.assertEqual({"root": [str(stabilized_child)]}, state.hierarchy)
        self.assertEqual("root", state.nodes[stabilized_child].parent_id)
        self.assertEqual(1, state.nodes[stabilized_child].depth)

    def test_signed_crossing_criterion_is_capability_gated(self) -> None:
        unavailable_model = GRC9V3.from_state(
            state=_saturated_candidate_state(),
            params=_spark_params(spark_signed_crossing=True),
        )

        self.assertEqual([], unavailable_model.detect_hybrid_spark_candidates())
        self.assertEqual(
            "history_unavailable",
            unavailable_model.get_state().cached_quantities[
                "hybrid_spark_signed_crossing_status"
            ],
        )

        state = _saturated_candidate_state()
        state["cached_quantities"] = {"previous_min_signed_hessian_by_node": {"0": 0.2}}
        crossing_model = GRC9V3.from_state(
            state=state,
            params=_spark_params(spark_signed_crossing=True),
        )

        candidates = crossing_model.detect_hybrid_spark_candidates()
        self.assertEqual(1, len(candidates))
        self.assertTrue(candidates[0].payload["signed_crossing_gate"])


if __name__ == "__main__":
    unittest.main()
