#!/usr/bin/env python3
"""Deeper Phase 3 smoke tests for substrates, persistence, and determinism."""

from __future__ import annotations

import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pygrc.core import (
    GRCEvent,
    GRCParams,
    build_snapshot_metadata,
    build_standard_snapshot,
    digest_snapshot,
    export_port_topology,
    export_weighted_topology,
    load_snapshot,
    restore_port_graph,
    restore_weighted_graph,
    save_snapshot,
    snapshot_to_json,
)
from pygrc.core.storage import PortGraphBackend, WeightedGraphBackend
from pygrc.models import GRC9V3, GRC9V3State


PASS = 0
FAIL = 0


def check(name: str, condition: bool, details: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  OK   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")
        if details:
            print(f"       {details}")


def section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def weighted_snapshot(graph: WeightedGraphBackend) -> dict:
    params = GRCParams.from_mapping(
        {
            "dt": 0.1,
            "evolution": {"alpha": 2.0},
            "constitutive_semantic_modes": {"frame_mode": "host_embedding"},
        }
    )
    return build_standard_snapshot(
        metadata=build_snapshot_metadata(
            model_family="GRCV2",
            step_index=4,
            params=dict(params.raw_config),
            resolved_params=dict(params.resolved_config),
            params_hash=params.params_hash,
            capabilities={
                "single_weight_edges",
                "multi_metric_edges",
                "identity_basins",
                "proxy_sparks",
                "soft_split",
                "front_birth",
                "budget_preservation",
            },
            next_node_id=graph.next_node_id,
            next_edge_id=graph.next_edge_id,
        ),
        topology=export_weighted_topology(graph),
    )


def port_snapshot(graph: PortGraphBackend) -> dict:
    params = GRCParams.from_mapping(
        {
            "dt": 0.1,
            "constitutive_semantic_modes": {"frame_mode": "intrinsic_frame"},
        }
    )
    return build_standard_snapshot(
        metadata=build_snapshot_metadata(
            model_family="GRC9",
            step_index=6,
            params=dict(params.raw_config),
            resolved_params=dict(params.resolved_config),
            params_hash=params.params_hash,
            capabilities={
                "port_graph",
                "mechanical_refinement",
                "column_coarse_graining",
                "single_weight_edges",
                "multi_metric_edges",
                "intrinsic_frame",
            },
            next_node_id=graph.next_node_id,
            next_edge_id=graph.next_edge_id,
        ),
        topology=export_port_topology(graph),
    )


def build_weighted_reference() -> WeightedGraphBackend:
    graph = WeightedGraphBackend()
    node_0 = graph.add_node({"label": "A"})
    node_1 = graph.add_node({"label": "B"})
    node_2 = graph.add_node({"label": "C"})
    edge_0 = graph.add_edge(node_0, node_1, {"base_conductance": 0.5})
    graph.add_edge(node_1, node_2, {"base_conductance": 0.25})
    graph.remove_edge(edge_0)
    graph.remove_node(node_0)
    node_3 = graph.add_node({"label": "D"})
    graph.add_edge(node_1, node_3, {"base_conductance": 0.75})
    return graph


def build_port_reference() -> PortGraphBackend:
    graph = PortGraphBackend()
    node_0 = graph.add_node({"label": "P0"})
    node_1 = graph.add_node({"label": "P1"})
    node_2 = graph.add_node({"label": "P2"})
    edge_0 = graph.connect_ports(node_0, 0, node_1, 8, {"bond": 1.0})
    edge_1 = graph.connect_ports(node_0, 1, node_2, 7, {"bond": 0.5})
    graph.rewire_edge(edge_1, node_1, 0, node_2, 6)
    graph.remove_edge(edge_0)
    graph.connect_ports(node_0, 4, node_2, 5, {"bond": 0.75})
    return graph


def run_weighted_deep_smoke() -> None:
    section("1. Weighted Backend Deep Smoke")
    graph = build_weighted_reference()
    snapshot = weighted_snapshot(graph)
    json_1 = snapshot_to_json(snapshot)
    json_2 = snapshot_to_json(snapshot)

    check(
        "W-live-node-ids",
        tuple(graph.iter_live_node_ids()) == (1, 2, 3),
        f"got {tuple(graph.iter_live_node_ids())}",
    )
    check(
        "W-live-edge-ids",
        tuple(graph.iter_live_edge_ids()) == (1, 2),
        f"got {tuple(graph.iter_live_edge_ids())}",
    )
    check("W-next-node-id", graph.next_node_id == 4, f"got {graph.next_node_id}")
    check("W-next-edge-id", graph.next_edge_id == 3, f"got {graph.next_edge_id}")
    check("W-json-repeatable", json_1 == json_2)

    rebuilt = build_weighted_reference()
    rebuilt_snapshot = weighted_snapshot(rebuilt)
    check(
        "W-equivalent-build-json",
        snapshot_to_json(rebuilt_snapshot) == json_1,
    )
    check(
        "W-equivalent-build-digest",
        digest_snapshot(rebuilt_snapshot) == digest_snapshot(snapshot),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "weighted.json"
        save_snapshot(path, snapshot)
        loaded = load_snapshot(path)

    restored = restore_weighted_graph(loaded["topology"], loaded["metadata"])
    restored_topology = export_weighted_topology(restored)
    check("W-file-roundtrip-snapshot", loaded == snapshot)
    check(
        "W-restore-live-node-ids",
        tuple(restored.iter_live_node_ids()) == (1, 2, 3),
        f"got {tuple(restored.iter_live_node_ids())}",
    )
    check(
        "W-restore-live-edge-ids",
        tuple(restored.iter_live_edge_ids()) == (1, 2),
        f"got {tuple(restored.iter_live_edge_ids())}",
    )
    check("W-restore-next-node-id", restored.next_node_id == 4)
    check("W-restore-next-edge-id", restored.next_edge_id == 3)
    check("W-restore-topology-equal", restored_topology == snapshot["topology"])
    check(
        "W-params-preserved",
        loaded["metadata"]["params_hash"] == snapshot["metadata"]["params_hash"],
    )


def run_port_deep_smoke() -> None:
    section("2. Port Backend Deep Smoke")
    graph = build_port_reference()
    snapshot = port_snapshot(graph)
    json_1 = snapshot_to_json(snapshot)

    occupied_node_0 = {slot for slot in range(9) if graph.port_is_occupied(0, slot)}
    occupied_node_1 = {slot for slot in range(9) if graph.port_is_occupied(1, slot)}
    occupied_node_2 = {slot for slot in range(9) if graph.port_is_occupied(2, slot)}

    check("P-live-node-ids", tuple(graph.iter_live_node_ids()) == (0, 1, 2))
    check(
        "P-live-edge-ids",
        tuple(graph.iter_live_edge_ids()) == (1, 2),
        f"got {tuple(graph.iter_live_edge_ids())}",
    )
    check("P-next-node-id", graph.next_node_id == 3)
    check("P-next-edge-id", graph.next_edge_id == 3)
    check("P-node0-occupancy", occupied_node_0 == {4}, f"got {occupied_node_0}")
    check("P-node1-occupancy", occupied_node_1 == {0}, f"got {occupied_node_1}")
    check("P-node2-occupancy", occupied_node_2 == {5, 6}, f"got {occupied_node_2}")
    check(
        "P-edge1-rewired",
        graph.edge_ports(1) == ((1, 0), (2, 6)),
        f"got {graph.edge_ports(1)}",
    )

    rebuilt = build_port_reference()
    rebuilt_snapshot = port_snapshot(rebuilt)
    check(
        "P-equivalent-build-json",
        snapshot_to_json(rebuilt_snapshot) == json_1,
    )
    check(
        "P-equivalent-build-digest",
        digest_snapshot(rebuilt_snapshot) == digest_snapshot(snapshot),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "port.json"
        save_snapshot(path, snapshot)
        loaded = load_snapshot(path)

    restored = restore_port_graph(loaded["topology"], loaded["metadata"])
    restored_topology = export_port_topology(restored)
    check("P-file-roundtrip-snapshot", loaded == snapshot)
    check(
        "P-restore-live-edge-ids",
        tuple(restored.iter_live_edge_ids()) == (1, 2),
        f"got {tuple(restored.iter_live_edge_ids())}",
    )
    check("P-restore-next-node-id", restored.next_node_id == 3)
    check("P-restore-next-edge-id", restored.next_edge_id == 3)
    check("P-restore-topology-equal", restored_topology == snapshot["topology"])
    check("P-restore-slot-node1-0", restored.port_edge_id(1, 0) == 1)
    check("P-restore-slot-node2-6", restored.port_edge_id(2, 6) == 1)
    check("P-restore-slot-node0-4", restored.port_edge_id(0, 4) == 2)
    check("P-restore-slot-node2-5", restored.port_edge_id(2, 5) == 2)


def run_stub_persistence_smoke() -> None:
    section("3. Stub Persistence Deep Smoke")
    rng = random.Random(17)
    rng_state = rng.getstate()
    model = GRC9V3.from_config({"dt": 0.25})
    model.set_state(
        GRC9V3State(
            step_index=9,
            time=2.5,
            budget_target=3.0,
            remainder=1e-12,
            observables={"budget_current": 3.0},
            cached_quantities={"laplacian": {"1": -0.5}},
            event_log=[
                GRCEvent(
                    kind="spark",
                    step_index=9,
                    payload={"det_h": 0.0},
                    source_family="GRC9V3",
                )
            ],
            rng_state=rng_state,
            params_identity=model.get_params().params_hash,
        )
    )

    snapshot = model.snapshot()
    snapshot_keys = set(snapshot)
    check(
        "S-shared-snapshot-core-groups",
        {"metadata", "topology", "dynamics", "observables", "events"}.issubset(snapshot_keys),
        f"got {list(snapshot.keys())}",
    )
    check(
        "S-grc9v3-extension-groups",
        {"basin_attributes", "edge_labels", "caches"}.issubset(snapshot_keys),
        f"got {list(snapshot.keys())}",
    )
    check("S-metadata-rng-tagged", snapshot["metadata"]["rng_state"]["engine"] == "python_random")
    check(
        "S-state-rng-tagged",
        snapshot["dynamics"]["state"]["rng_state"]["engine"] == "python_random",
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "stub.json"
        model.save(str(path))
        loaded = load_snapshot(path)
        restored = GRC9V3.load(str(path))

    restored_state = restored.get_state()
    replay = random.Random()
    replay.setstate(restored_state.rng_state)

    check("S-family-restored", restored.MODEL_FAMILY == "GRC9V3")
    check("S-step-index-restored", restored_state.step_index == 9)
    check("S-time-restored", restored_state.time == 2.5)
    check("S-remainder-restored", restored_state.remainder == 1e-12)
    check(
        "S-params-identity-restored",
        restored_state.params_identity == model.get_params().params_hash,
    )
    check("S-event-log-restored", len(restored_state.event_log) == 1)
    # Compare RNG progression directly from the restored state.
    baseline = random.Random()
    baseline.setstate(rng_state)
    check("S-rng-next-value", replay.random() == baseline.random())
    check(
        "S-params-hash-preserved",
        loaded["metadata"]["params_hash"] == model.get_params().params_hash,
    )


def main() -> int:
    run_weighted_deep_smoke()
    run_port_deep_smoke()
    run_stub_persistence_smoke()

    print("\n" + "=" * 48)
    print(f"Deep smoke results: {PASS} passed, {FAIL} failed")
    if FAIL:
        print("Deep smoke failed.")
        return 1
    print("All deep smoke tests passed. OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
