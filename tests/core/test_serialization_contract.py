"""Contract tests for the interface-level snapshot contract."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from pygrc.core import (
    RESET_BASELINE_SCHEMA,
    RESET_BASELINE_VERSION,
    SNAPSHOT_SCHEMA,
    SNAPSHOT_GROUP_ORDER,
    SNAPSHOT_VERSION,
    PortGraphBackend,
    SnapshotCompatibilityError,
    WeightedGraphBackend,
    build_dynamics_group,
    build_event_records,
    build_reset_baseline_group,
    build_snapshot_metadata,
    build_standard_snapshot,
    build_topology_snapshot,
    canonical_json_dumps,
    canonicalize_json_value,
    export_port_topology,
    export_weighted_topology,
    load_snapshot,
    require_snapshot_family,
    restore_port_graph,
    restore_weighted_graph,
    save_snapshot,
    snapshot_from_json,
    snapshot_to_json,
    validate_snapshot_contract,
    validate_reset_baseline_group,
)


class SnapshotContractTest(unittest.TestCase):
    """Validate the Phase 1 snapshot contract surface."""

    def test_build_snapshot_metadata_produces_required_fields(self) -> None:
        metadata = build_snapshot_metadata(
            model_family="GRCV2",
            step_index=5,
            params={"dt": 0.1},
            resolved_params={"dt": 0.1},
            params_hash="abc",
            capabilities={"single_weight_edges"},
        )

        self.assertEqual(SNAPSHOT_SCHEMA, metadata["snapshot_schema"])
        self.assertEqual(SNAPSHOT_VERSION, metadata["snapshot_version"])
        self.assertEqual("GRCV2", metadata["model_family"])
        self.assertEqual(5, metadata["step_index"])
        self.assertEqual(["single_weight_edges"], metadata["capabilities"])

    def test_validate_snapshot_contract_accepts_minimal_shared_shape(self) -> None:
        snapshot = {
            "metadata": build_snapshot_metadata(
                model_family="GRCV3",
                step_index=1,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"basin_attributes"},
            ),
            "topology": {"nodes": [], "edges": []},
            "observables": {"budget_current": 1.0},
            "events": [],
        }

        validate_snapshot_contract(snapshot)

    def test_validate_snapshot_contract_rejects_missing_metadata(self) -> None:
        with self.assertRaises(SnapshotCompatibilityError):
            validate_snapshot_contract({"topology": {}})

    def test_validate_snapshot_contract_rejects_wrong_schema(self) -> None:
        snapshot = {
            "metadata": {
                "snapshot_schema": "wrong.schema",
                "snapshot_version": SNAPSHOT_VERSION,
                "model_family": "GRCV2",
                "step_index": 0,
                "params": {},
                "resolved_params": {},
                "params_hash": "hash",
                "capabilities": [],
            },
            "topology": {},
        }

        with self.assertRaises(SnapshotCompatibilityError):
            validate_snapshot_contract(snapshot)

    def test_require_snapshot_family_rejects_family_mismatch(self) -> None:
        snapshot = {
            "metadata": build_snapshot_metadata(
                model_family="GRC9",
                step_index=0,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"port_graph"},
            ),
            "topology": {},
        }

        with self.assertRaises(SnapshotCompatibilityError):
            require_snapshot_family(snapshot, expected_family="GRCV3")

    def test_core_exports_include_canonical_serialization_helpers(self) -> None:
        self.assertEqual('{"a":1,"b":2}', canonical_json_dumps({"b": 2, "a": 1}))
        self.assertEqual(["a", "b"], canonicalize_json_value({"a", "b"}))

    def test_build_topology_snapshot_keeps_lists_and_omits_unsupported_groups(self) -> None:
        topology = build_topology_snapshot(
            nodes=[{"node_id": 0}],
            edges=[{"edge_id": 1}],
        )

        self.assertEqual({"nodes": [{"node_id": 0}], "edges": [{"edge_id": 1}]}, topology)

    def test_build_dynamics_group_canonicalizes_payload_sections(self) -> None:
        dynamics = build_dynamics_group(
            state={"time": 1.0, "step_index": 2},
            budget={"current": 1.0},
        )

        self.assertEqual(
            {"state": {"step_index": 2, "time": 1.0}, "budget": {"current": 1.0}},
            dynamics,
        )

    def test_build_standard_snapshot_preserves_canonical_group_order(self) -> None:
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=2,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"single_weight_edges"},
            ),
            topology=build_topology_snapshot(nodes=[{"node_id": 0}], edges=[]),
            dynamics=build_dynamics_group(state={"step_index": 2}),
            observables={"budget_current": 1.0},
            events=[{"kind": "tick", "step_index": 2, "payload": {}}],
        )

        self.assertEqual(
            ["metadata", "topology", "dynamics", "observables", "events"],
            list(snapshot.keys()),
        )
        self.assertEqual(
            [group for group in SNAPSHOT_GROUP_ORDER if group in snapshot],
            list(snapshot.keys()),
        )

    def test_build_standard_snapshot_rejects_mutation_history_in_standard_mode(self) -> None:
        with self.assertRaises(ValueError):
            build_standard_snapshot(
                metadata=build_snapshot_metadata(
                    model_family="GRCV2",
                    step_index=0,
                    params={"dt": 0.1},
                    resolved_params={"dt": 0.1},
                    params_hash="hash",
                    capabilities={"single_weight_edges"},
                ),
                topology=build_topology_snapshot(),
                mutation_history=[{"kind": "remove_edge"}],
            )

    def test_reset_baseline_group_is_versioned_and_non_recursive(self) -> None:
        baseline = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=0,
                params={},
                resolved_params={},
                params_hash="hash",
                capabilities={"single_weight_edges"},
            ),
            topology=build_topology_snapshot(nodes=[], edges=[]),
        )
        group = build_reset_baseline_group(
            model_family="GRCV2",
            baseline_snapshot=baseline,
        )

        self.assertEqual(RESET_BASELINE_SCHEMA, group["reset_baseline_schema"])
        self.assertEqual(RESET_BASELINE_VERSION, group["reset_baseline_version"])
        self.assertEqual("available", group["status"])
        validate_reset_baseline_group(group, expected_family="GRCV2")

        with self.assertRaises(ValueError):
            build_reset_baseline_group(
                model_family="GRCV2",
                baseline_snapshot={**baseline, "reset_baseline": group},
            )

    def test_unavailable_reset_baseline_requires_explicit_reason(self) -> None:
        group = build_reset_baseline_group(
            model_family="GRC9V3",
            baseline_snapshot=None,
            unavailable_reason="legacy_snapshot_missing_reset_baseline",
        )

        self.assertEqual("unavailable", group["status"])
        validate_reset_baseline_group(group, expected_family="GRC9V3")
        with self.assertRaises(ValueError):
            build_reset_baseline_group(
                model_family="GRC9V3",
                baseline_snapshot=None,
            )

    def test_build_event_records_returns_canonical_event_list(self) -> None:
        events = build_event_records(
            [{"payload": {"b": 2, "a": 1}, "kind": "tick", "step_index": 1}]
        )

        self.assertEqual(
            [{"kind": "tick", "payload": {"a": 1, "b": 2}, "step_index": 1}],
            events,
        )

    def test_export_weighted_topology_is_deterministic_and_live_only(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node({"coherence": 1.0})
        node_1 = graph.add_node({"coherence": 0.5})
        edge_0 = graph.add_edge(node_0, node_1, {"base_conductance": 0.25})
        node_2 = graph.add_node({"coherence": 0.1})
        edge_1 = graph.add_edge(node_1, node_2, {"base_conductance": 0.1})
        graph.remove_edge(edge_1)
        graph.remove_node(node_2)

        topology = export_weighted_topology(graph)

        self.assertEqual(
            [{"node_id": 0, "payload": {"coherence": 1.0}}, {"node_id": 1, "payload": {"coherence": 0.5}}],
            topology["nodes"],
        )
        self.assertEqual(
            [
                {
                    "edge_id": edge_0,
                    "node_a": 0,
                    "node_b": 1,
                    "payload": {"base_conductance": 0.25},
                }
            ],
            topology["edges"],
        )
        self.assertEqual({"0": [0], "1": [0]}, topology["incidence"])

    def test_export_weighted_topology_sorts_multi_edge_incidence(self) -> None:
        graph = WeightedGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.add_edge(node_0, node_2)
        edge_1 = graph.add_edge(node_0, node_1)
        edge_2 = graph.add_edge(node_0, node_1)

        topology = export_weighted_topology(graph)

        self.assertEqual([edge_0, edge_1, edge_2], topology["incidence"]["0"])

    def test_export_port_topology_is_deterministic_and_exposes_port_structure(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node({"mass": 1.0})
        node_1 = graph.add_node({"mass": 2.0})
        edge_0 = graph.connect_ports(node_0, 0, node_1, 8, {"bond": 0.5})

        topology = export_port_topology(graph)

        self.assertEqual(
            [{"node_id": 0, "payload": {"mass": 1.0}}, {"node_id": 1, "payload": {"mass": 2.0}}],
            topology["nodes"],
        )
        self.assertEqual(
            [
                {
                    "edge_id": edge_0,
                    "endpoint_a": {"node_id": 0, "slot": 0},
                    "endpoint_b": {"node_id": 1, "slot": 8},
                    "payload": {"bond": 0.5},
                }
            ],
            topology["edges"],
        )
        self.assertEqual({"0": [0], "1": [0]}, topology["incidence"])
        self.assertEqual(
            {"slot": 0, "row": 0, "column": 0, "occupied": True, "edge_id": 0},
            topology["port_structure"]["0"]["ports"][0],
        )
        self.assertEqual(
            {"slot": 8, "row": 2, "column": 2, "occupied": True, "edge_id": 0},
            topology["port_structure"]["1"]["ports"][8],
        )

    def test_export_port_topology_sorts_multi_edge_incidence(self) -> None:
        graph = PortGraphBackend()
        node_0 = graph.add_node()
        node_1 = graph.add_node()
        node_2 = graph.add_node()
        edge_0 = graph.connect_ports(node_0, 0, node_1, 1)
        edge_1 = graph.connect_ports(node_0, 2, node_2, 3)

        topology = export_port_topology(graph)

        self.assertEqual([edge_0, edge_1], topology["incidence"]["0"])

    def test_exported_topology_remains_compatible_with_snapshot_contract(self) -> None:
        weighted = WeightedGraphBackend()
        left = weighted.add_node()
        right = weighted.add_node()
        weighted.add_edge(left, right)

        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=0,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"single_weight_edges"},
            ),
            topology=export_weighted_topology(weighted),
        )

        validate_snapshot_contract(snapshot)

    def test_snapshot_to_json_and_from_json_roundtrip(self) -> None:
        weighted = WeightedGraphBackend()
        left = weighted.add_node({"coherence": 1.0})
        right = weighted.add_node({"coherence": 0.5})
        weighted.add_edge(left, right, {"base_conductance": 0.25})
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=0,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"single_weight_edges"},
                next_node_id=weighted.next_node_id,
                next_edge_id=weighted.next_edge_id,
            ),
            topology=export_weighted_topology(weighted),
        )

        restored = snapshot_from_json(snapshot_to_json(snapshot))

        self.assertEqual(snapshot, restored)

    def test_snapshot_from_json_rejects_malformed_or_invalid_payload(self) -> None:
        with self.assertRaises(SnapshotCompatibilityError):
            snapshot_from_json("{not-json}")

        with self.assertRaises(SnapshotCompatibilityError):
            snapshot_from_json(json.dumps(["not", "a", "mapping"]))

        with self.assertRaises(SnapshotCompatibilityError):
            snapshot_from_json(json.dumps({"metadata": {}, "topology": {}}))

    def test_save_snapshot_writes_atomically_and_load_snapshot_is_strict(self) -> None:
        weighted = WeightedGraphBackend()
        left = weighted.add_node()
        right = weighted.add_node()
        weighted.add_edge(left, right)
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=0,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"single_weight_edges"},
                next_node_id=weighted.next_node_id,
                next_edge_id=weighted.next_edge_id,
            ),
            topology=export_weighted_topology(weighted),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "snapshot.json"
            path.write_text("stale-data", encoding="utf-8")
            save_snapshot(path, snapshot)
            loaded = load_snapshot(path)

        self.assertEqual(snapshot, loaded)

    def test_restore_weighted_graph_preserves_ids_counters_and_structure(self) -> None:
        weighted = WeightedGraphBackend()
        left = weighted.add_node({"coherence": 1.0})
        right = weighted.add_node({"coherence": 0.5})
        edge = weighted.add_edge(left, right, {"base_conductance": 0.25})
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRCV2",
                step_index=0,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"single_weight_edges"},
                next_node_id=weighted.next_node_id,
                next_edge_id=weighted.next_edge_id,
            ),
            topology=export_weighted_topology(weighted),
        )

        restored = restore_weighted_graph(snapshot["topology"], snapshot["metadata"])

        self.assertEqual((0, 1), tuple(restored.iter_live_node_ids()))
        self.assertEqual((edge,), tuple(restored.iter_live_edge_ids()))
        self.assertEqual(weighted.next_node_id, restored.next_node_id)
        self.assertEqual(weighted.next_edge_id, restored.next_edge_id)
        self.assertEqual((1,), tuple(restored.neighbors(left)))

    def test_restore_port_graph_preserves_ids_counters_and_structure(self) -> None:
        port_graph = PortGraphBackend()
        left = port_graph.add_node({"mass": 1.0})
        right = port_graph.add_node({"mass": 2.0})
        edge = port_graph.connect_ports(left, 0, right, 8, {"bond": 0.5})
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRC9",
                step_index=0,
                params={"dt": 0.1},
                resolved_params={"dt": 0.1},
                params_hash="hash",
                capabilities={"port_graph"},
                next_node_id=port_graph.next_node_id,
                next_edge_id=port_graph.next_edge_id,
            ),
            topology=export_port_topology(port_graph),
        )

        restored = restore_port_graph(snapshot["topology"], snapshot["metadata"])

        self.assertEqual((0, 1), tuple(restored.iter_live_node_ids()))
        self.assertEqual((edge,), tuple(restored.iter_live_edge_ids()))
        self.assertEqual(port_graph.next_node_id, restored.next_node_id)
        self.assertEqual(port_graph.next_edge_id, restored.next_edge_id)
        self.assertEqual(edge, restored.port_edge_id(left, 0))
        self.assertEqual(edge, restored.port_edge_id(right, 8))

    def test_save_load_roundtrip_on_port_snapshot_preserves_metadata_and_topology(self) -> None:
        port_graph = PortGraphBackend()
        left = port_graph.add_node({"mass": 1.0})
        right = port_graph.add_node({"mass": 2.0})
        edge = port_graph.connect_ports(left, 0, right, 8, {"bond": 0.5})
        snapshot = build_standard_snapshot(
            metadata=build_snapshot_metadata(
                model_family="GRC9",
                step_index=4,
                params={"dt": 0.1, "frame_mode": "intrinsic_frame"},
                resolved_params={
                    "dt": 0.1,
                    "frame_mode": "intrinsic_frame",
                    "numerical_backend": {},
                },
                params_hash="port-hash",
                capabilities={"port_graph"},
                next_node_id=port_graph.next_node_id,
                next_edge_id=port_graph.next_edge_id,
            ),
            topology=export_port_topology(port_graph),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "port-snapshot.json"
            save_snapshot(path, snapshot)
            loaded = load_snapshot(path)

        self.assertEqual(snapshot, loaded)
        restored = restore_port_graph(loaded["topology"], loaded["metadata"])
        self.assertEqual((0, 1), tuple(restored.iter_live_node_ids()))
        self.assertEqual((edge,), tuple(restored.iter_live_edge_ids()))
        self.assertEqual("port-hash", loaded["metadata"]["params_hash"])
        self.assertEqual(port_graph.next_node_id, restored.next_node_id)
        self.assertEqual(port_graph.next_edge_id, restored.next_edge_id)
