#!/usr/bin/env python3
"""Build N22 Iteration 6-A carrier transfer / re-entry probe."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
)
OUTPUT = EXPERIMENT / "outputs" / "n22_carrier_transfer_reentry_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_carrier_transfer_reentry_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_carrier_transfer_reentry_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_carrier_transfer_reentry_probe.py"
)

I5C_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_alternative_nonconsumptive_carrier_probe.json"
)

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B  # noqa: E402
from pygrc.core import canonicalize_json_value  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402


GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "semantic_learning",
    "free_will",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "fully_native_integration",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]

RUN_ID = "n22_i6a_carrier_transfer_reentry"
TARGET_EDGE_ID = 0
PEER_EDGE_ID = 1
TARGET_REENTRY = {
    "source_node_id": 1,
    "target_node_id": 0,
    "edge_id": 0,
}
PEER_CORRIDOR = {
    "source_node_id": 2,
    "target_node_id": 0,
    "edge_id": 1,
}
TARGET_REENTRY_PACKET_AMOUNT = 0.02
PEER_CORRIDOR_PACKET_AMOUNT = 0.01
MIN_TRANSFER_CARRIER_RATIO = 0.90
MIN_TRANSFER_TARGET_OVER_PEER_MARGIN = 0.05
MAX_CARRIER_LOSS_AFTER_TRANSFER = 0.02
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
MAX_BUDGET_ERROR = 1e-9
POSITIVE_CONTEXTS = [
    "delayed_target_reentry_then_readback",
    "peer_corridor_flux_then_target_reentry_readback",
]
CONTROL_CONTEXTS = [
    "peer_label_swap_reentry_control",
    "active_carrier_update_carryover_control",
    "native_conductance_memory_relabel_control",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def source_record(path: str, role: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
    }


def threshold_record() -> dict[str, Any]:
    return {
        "threshold_record_id": "n22_i6a_carrier_transfer_reentry_thresholds",
        "declared_before_use": True,
        "consumes_i5c_only": True,
        "positive_contexts": POSITIVE_CONTEXTS,
        "control_contexts": CONTROL_CONTEXTS,
        "min_transfer_carrier_ratio": MIN_TRANSFER_CARRIER_RATIO,
        "min_transfer_target_over_peer_margin": MIN_TRANSFER_TARGET_OVER_PEER_MARGIN,
        "max_carrier_loss_after_transfer": MAX_CARRIER_LOSS_AFTER_TRANSFER,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "target_reentry_packet_amount": TARGET_REENTRY_PACKET_AMOUNT,
        "peer_corridor_packet_amount": PEER_CORRIDOR_PACKET_AMOUNT,
        "su6_or_final_n22_allowed": False,
    }


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def edge_state(model: LGRC9V3, edge_id: int) -> dict[str, Any]:
    state = model.get_state()
    edge = state.base_state.port_edges[edge_id]
    return {
        "edge_id": edge_id,
        "node_u": edge.node_u,
        "port_u": edge.port_u,
        "node_v": edge.node_v,
        "port_v": edge.port_v,
        "conductance": float(edge.conductance),
        "flux_uv": float(edge.flux_uv),
        "base_conductance": float(state.base_state.base_conductance.get(edge_id, 0.0)),
    }


def carrier_update_count(model: LGRC9V3) -> int:
    updates = model.get_state().cached_quantities.get("n22_i5c_carrier_updates", [])
    return len(updates) if isinstance(updates, list) else 0


def state_signature(model: LGRC9V3, phase: str) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    target = state.base_state.nodes[1]
    peer = state.base_state.nodes[2]
    ledger = state.packet_ledger
    assert ledger is not None
    signature = {
        "phase": phase,
        "center_coherence": float(center.coherence),
        "center_basin_mass": float(center.basin_mass),
        "target_route_node_coherence": float(target.coherence),
        "target_route_basin_mass": float(target.basin_mass),
        "peer_route_node_coherence": float(peer.coherence),
        "peer_route_basin_mass": float(peer.basin_mass),
        "target_edge_state": edge_state(model, TARGET_EDGE_ID),
        "peer_edge_state": edge_state(model, PEER_EDGE_ID),
        "carrier_update_count": carrier_update_count(model),
        "active_degree": len(state.base_state.topology.incident_edge_ids(0)),
        "packet_count": len(ledger.packet_records),
        "packet_event_count": len(ledger.packet_event_records),
        "event_queue_count": len(ledger.event_queue_records),
        "budget_error": float(ledger.budget_error),
        "in_flight_packet_total": float(ledger.in_flight_packet_total),
        "observables": canonicalize_json_value(dict(model.compute_observables())),
    }
    signature["state_signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def save_snapshot(model: LGRC9V3, run_role: str, phase: str) -> str:
    path = ARTIFACT_DIR / f"{run_role}_{phase}_snapshot.json"
    model.save(str(path))
    return rel(path)


def schedule_packet(
    model: LGRC9V3,
    *,
    source_node_id: int,
    target_node_id: int,
    edge_id: int,
    amount: float,
    event_time: float,
    scheduler_index: int,
) -> None:
    model.schedule_packet_departure(
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        edge_id=edge_id,
        amount=amount,
        departure_event_time_key=event_time,
        scheduler_event_index=scheduler_index,
    )


def event_to_record(event: Any, run_role: str, phase: str) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "phase": phase,
            "kind": event.kind,
            "step_index": event.step_index,
            "source_family": event.source_family,
            "payload": dict(event.payload),
        }
    )


def drain_queue(model: LGRC9V3, run_role: str, phase: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        rows.extend(event_to_record(event, run_role, phase) for event in result.events)
    return rows


def compact_spark_event(event: Any, run_role: str, phase: str) -> dict[str, Any]:
    payload = dict(event.payload)
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "phase": phase,
            "kind": event.kind,
            "event_id": payload.get("candidate_event_id"),
            "spark_lane": payload.get("spark_lane"),
            "column_h": payload.get("column_h"),
            "min_abs_column_h": payload.get("min_abs_column_h"),
            "min_abs_column_h_column": payload.get("min_abs_column_h_column"),
            "column_h_branch_hit": payload.get("column_h_branch_hit"),
            "column_h_threshold_hit": payload.get("column_h_threshold_hit"),
            "gate_reasons": payload.get("gate_reasons"),
        }
    )


def readback(model: LGRC9V3, run_role: str, phase: str) -> dict[str, Any]:
    before = state_signature(model, f"{phase}_before_readback")
    events = model.evaluate_causal_spark_diagnostics(
        trigger_kind="n22_i6a_transfer_carrier_readback",
        trigger_source="iteration_6a_explicit_carrier_readback",
        trigger_node_id=0,
    )
    compact = [compact_spark_event(event, run_role, phase) for event in events]
    after = state_signature(model, f"{phase}_after_readback")
    record = {
        "phase": phase,
        "candidate_count": len(compact),
        "compact_candidate_events": compact,
        "before_state_signature_digest": before["state_signature_digest"],
        "after_state_signature_digest": after["state_signature_digest"],
        "carrier_update_count_before": before["carrier_update_count"],
        "carrier_update_count_after": after["carrier_update_count"],
        "new_carrier_update_during_readback": (
            after["carrier_update_count"] != before["carrier_update_count"]
        ),
        "target_edge_base_conductance_before": before["target_edge_state"][
            "base_conductance"
        ],
        "target_edge_base_conductance_after": after["target_edge_state"][
            "base_conductance"
        ],
        "column_h": compact[0].get("column_h") if compact else None,
        "min_abs_column_h": compact[0].get("min_abs_column_h") if compact else None,
        "column_h_branch_hit": compact[0].get("column_h_branch_hit") if compact else False,
    }
    record["readback_digest"] = digest_value(record)
    return canonicalize_json_value(record)


def load_model(path: str) -> LGRC9V3:
    return LGRC9V3.load(str(ROOT / path))


def run_context(
    *,
    source_row: dict[str, Any],
    context_id: str,
    snapshot_key: str,
    baseline_snapshot_key: str,
    source_delta: float,
    peer_model_snapshot_key: str | None = None,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    run_role = f"{source_row['carrier_family']}_{context_id}"
    model = load_model(source_row["snapshots"][snapshot_key])
    baseline = load_model(source_row["snapshots"][baseline_snapshot_key])
    loaded_signature = state_signature(model, "loaded_post_carrier_state")
    loaded_snapshot = save_snapshot(model, run_role, "loaded")
    events: list[dict[str, Any]] = []
    if context_id == "delayed_target_reentry_then_readback":
        # Delay is represented by using a later event key without inserting a
        # carrier mutation. The only runtime event is the declared re-entry.
        schedule_packet(
            model,
            **TARGET_REENTRY,
            amount=TARGET_REENTRY_PACKET_AMOUNT,
            event_time=6.0,
            scheduler_index=60,
        )
        events.extend(drain_queue(model, run_role, "delayed_target_reentry"))
    elif context_id == "peer_corridor_flux_then_target_reentry_readback":
        schedule_packet(
            model,
            **PEER_CORRIDOR,
            amount=PEER_CORRIDOR_PACKET_AMOUNT,
            event_time=4.0,
            scheduler_index=40,
        )
        events.extend(drain_queue(model, run_role, "peer_corridor_flux"))
        schedule_packet(
            model,
            **TARGET_REENTRY,
            amount=TARGET_REENTRY_PACKET_AMOUNT,
            event_time=6.0,
            scheduler_index=60,
        )
        events.extend(drain_queue(model, run_role, "target_reentry_after_corridor"))
    elif context_id == "peer_label_swap_reentry_control":
        schedule_packet(
            model,
            **PEER_CORRIDOR,
            amount=TARGET_REENTRY_PACKET_AMOUNT,
            event_time=6.0,
            scheduler_index=60,
        )
        events.extend(drain_queue(model, run_role, "peer_label_swap_reentry"))
    else:
        raise ValueError(f"unsupported context {context_id}")
    after_transfer = state_signature(model, "after_transfer_reentry")
    after_transfer_snapshot = save_snapshot(model, run_role, "after_transfer")
    readback_record = readback(model, run_role, "post_transfer_readback")
    after_readback = state_signature(model, "after_transfer_readback")
    after_readback_snapshot = save_snapshot(model, run_role, "after_readback")
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, events)
    carrier_delta_after_transfer = (
        after_readback["target_edge_state"]["base_conductance"]
        - state_signature(baseline, "baseline_pre_carrier")["target_edge_state"][
            "base_conductance"
        ]
    )
    ratio = carrier_delta_after_transfer / source_delta if source_delta else 0.0
    carrier_loss = 1.0 - ratio
    peer_delta = 0.0
    if peer_model_snapshot_key is not None:
        peer_model = load_model(source_row["snapshots"][peer_model_snapshot_key])
        peer_baseline = load_model(source_row["snapshots"]["peer_pre"])
        peer_delta = (
            state_signature(peer_model, "peer_post")["target_edge_state"][
                "base_conductance"
            ]
            - state_signature(peer_baseline, "peer_pre")["target_edge_state"][
                "base_conductance"
            ]
        )
    margin = carrier_delta_after_transfer - peer_delta
    gate = {
        "context_id": context_id,
        "source_i5c_carrier_delta": source_delta,
        "carrier_delta_after_transfer_readback": carrier_delta_after_transfer,
        "carrier_transfer_ratio": ratio,
        "carrier_loss_after_transfer_readback": carrier_loss,
        "peer_same_budget_target_edge_delta": peer_delta,
        "target_over_peer_margin": margin,
        "carrier_preserved_after_transfer": (
            ratio >= MIN_TRANSFER_CARRIER_RATIO
            and carrier_loss <= MAX_CARRIER_LOSS_AFTER_TRANSFER
        ),
        "same_budget_peer_separated": margin >= MIN_TRANSFER_TARGET_OVER_PEER_MARGIN,
        "support_floor_result": (
            "preserved"
            if after_readback["center_basin_mass"] >= SUPPORT_FLOOR
            else "crossed_floor"
        ),
        "coherence_floor_result": (
            "preserved"
            if after_readback["center_coherence"] >= COHERENCE_FLOOR
            else "crossed_floor"
        ),
        "budget_result": (
            "preserved"
            if abs(after_readback["budget_error"]) <= MAX_BUDGET_ERROR
            and after_readback["in_flight_packet_total"] == 0.0
            else "exceeded_bound"
        ),
        "new_carrier_update_after_loaded_snapshot": (
            after_readback["carrier_update_count"]
            != loaded_signature["carrier_update_count"]
        ),
    }
    passed = (
        gate["carrier_preserved_after_transfer"]
        and gate["same_budget_peer_separated"]
        and gate["support_floor_result"] == "preserved"
        and gate["coherence_floor_result"] == "preserved"
        and gate["budget_result"] == "preserved"
        and gate["new_carrier_update_after_loaded_snapshot"] is False
    )
    artifact = {
        "artifact_id": f"n22_i6a_{run_role}_run",
        "source_i5c_row_id": source_row["row_id"],
        "carrier_family": source_row["carrier_family"],
        "context_id": context_id,
        "loaded_signature": loaded_signature,
        "after_transfer_signature": after_transfer,
        "after_readback_signature": after_readback,
        "readback_record": readback_record,
        "event_count": len(events),
        "event_counts_by_kind": dict(Counter(row["kind"] for row in events)),
        "gate": gate,
        "passed": passed,
        "producer_carrier_updates_disabled_after_load": (
            gate["new_carrier_update_after_loaded_snapshot"] is False
        ),
        "derived_report_only": False,
    }
    artifact["run_artifact_digest"] = digest_value(artifact)
    artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(artifact_path, artifact)
    return (
        {
            "context_id": context_id,
            "run_artifact_path": rel(artifact_path),
            "loaded_snapshot_path": loaded_snapshot,
            "after_transfer_snapshot_path": after_transfer_snapshot,
            "after_readback_snapshot_path": after_readback_snapshot,
            "event_log_path": rel(event_log_path),
            "gate": gate,
            "passed": passed,
            "readback_record": readback_record,
        },
        [
            (rel(artifact_path), f"{run_role}_run"),
            (loaded_snapshot, f"{run_role}_loaded_snapshot"),
            (after_transfer_snapshot, f"{run_role}_after_transfer_snapshot"),
            (after_readback_snapshot, f"{run_role}_after_readback_snapshot"),
            (rel(event_log_path), f"{run_role}_event_log"),
        ],
    )


def build_transfer_row(source_row: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    source_delta = source_row["carrier_gate"]["target_carrier_delta"]
    context_records: list[dict[str, Any]] = []
    manifest_entries: list[tuple[str, str]] = []
    for context_id in POSITIVE_CONTEXTS:
        record, paths = run_context(
            source_row=source_row,
            context_id=context_id,
            snapshot_key="target_post",
            baseline_snapshot_key="target_pre",
            source_delta=source_delta,
            peer_model_snapshot_key="peer_post",
        )
        context_records.append(record)
        manifest_entries.extend(paths)
    control_record, control_paths = run_context(
        source_row=source_row,
        context_id="peer_label_swap_reentry_control",
        snapshot_key="peer_post",
        baseline_snapshot_key="peer_pre",
        source_delta=source_delta,
        peer_model_snapshot_key="peer_post",
    )
    manifest_entries.extend(control_paths)
    active_update_carryover_control = {
        "control_id": "active_carrier_update_carryover_control",
        "status": "failed_closed",
        "claim_allowed": False,
        "primary_blocker": "producer_carrier_update_after_loaded_snapshot_blocked",
        "reason": "I6-A records no new carrier update after loading I5-C snapshots.",
    }
    native_relabel_control = {
        "control_id": "native_conductance_memory_relabel_control",
        "status": "failed_closed",
        "claim_allowed": False,
        "primary_blocker": "native_route_conductance_memory_policy_missing",
        "reason": "I5-C/I6-A carrier deltas remain producer-mediated naturalization debt.",
    }
    positive_contexts_passed = all(record["passed"] for record in context_records)
    peer_label_swap_failed_closed = not control_record["passed"]
    row = {
        "row_id": f"n22_i6a_row_{source_row['carrier_family']}",
        "source_i5c_row_id": source_row["row_id"],
        "carrier_family": source_row["carrier_family"],
        "row_decision": "partial" if positive_contexts_passed else "blocked",
        "decision_scope": (
            "producer_mediated_carrier_transfer_candidate_pending_I7_controls"
            if positive_contexts_passed
            else "blocked_before_carrier_transfer_support"
        ),
        "provisional_su_ladder_rung": (
            "SU5_producer_mediated_carrier_transfer_candidate_pending_I7"
            if positive_contexts_passed
            else "demoted_before_SU5"
        ),
        "supporting_su5_candidate": positive_contexts_passed,
        "su5_supported": False,
        "su6_supported": False,
        "native_route_conductance_memory_supported": False,
        "context_records": context_records,
        "controls": [
            {
                "control_id": "peer_label_swap_reentry_control",
                "status": "failed_closed" if peer_label_swap_failed_closed else "failed_open",
                "claim_allowed": False,
                "primary_blocker": "peer_target_edge_delta_missing",
                "reason": "Peer snapshot lacks the target carrier delta and cannot satisfy I6-A transfer.",
                "control_record": control_record,
            },
            active_update_carryover_control,
            native_relabel_control,
        ],
        "variable_classification": source_row["variable_classification"],
        "claim_ceiling": (
            "provisional producer-mediated carrier transfer candidate pending I7; "
            "not native conductance memory, semantic learning, agency, native support, "
            "SU6, final N22, or N21 ND6 bridge"
        ),
        "susceptibility_update_claim_allowed": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    row["row_digest"] = digest_value({key: value for key, value in row.items() if key != "row_digest"})
    return row, manifest_entries


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i5c = load_json(I5C_OUTPUT_PATH)
    threshold_path = ARTIFACT_DIR / "n22_i6a_thresholds_declared_before_use.json"
    write_json(threshold_path, threshold_record())
    runtime_config = {
        "config_id": "n22_i6a_carrier_transfer_runtime_config",
        "model_family": "LGRC9V3",
        "source_iteration": "I5-C",
        "fixture_source": "I5-C source-current snapshots",
        "spark_lane": LANE_B,
        "positive_contexts": POSITIVE_CONTEXTS,
        "control_contexts": CONTROL_CONTEXTS,
        "thresholds": threshold_record(),
        "producer_carrier_update_after_load_allowed": False,
    }
    runtime_config_path = ARTIFACT_DIR / "n22_i6a_runtime_config.json"
    write_json(runtime_config_path, runtime_config)
    source_rows = [
        row
        for row in i5c["carrier_rows"]
        if row["supporting_su4_candidate"] and row["carrier_family"] != "reduced_packet_readout_boundary"
    ]
    rows: list[dict[str, Any]] = []
    manifest_entries: list[tuple[str, str]] = [
        (rel(threshold_path), "threshold_record"),
        (rel(runtime_config_path), "runtime_config"),
    ]
    for source_row in source_rows:
        row, entries = build_transfer_row(source_row)
        rows.append(row)
        manifest_entries.extend(entries)
    artifact_manifest = file_manifest(manifest_entries)
    candidate_rows = [row for row in rows if row["supporting_su5_candidate"]]
    all_controls = [control for row in rows for control in row["controls"]]
    summary = {
        "source_i5c_su4_candidate_count": len(source_rows),
        "provisional_su5_carrier_candidate_count": len(candidate_rows),
        "positive_context_count_per_row": len(POSITIVE_CONTEXTS),
        "existing_i6_superseded": False,
        "packet_readout_branch_status": "unchanged_consumptive_SU3_transfer_readout_expression_only",
        "i5c_branch_status": "provisional_producer_mediated_SU5_candidate_pending_I7",
        "su5_supported": False,
        "su6_supported": False,
        "final_n22_supported": False,
        "native_route_conductance_memory_supported": False,
        "n21_nd6_bridge_status": "not_supported",
        "ready_for_iteration_7_control_matrix": True,
    }
    checks = [
        check(
            "i5c_passed",
            i5c.get("acceptance_state")
            == "accepted_producer_mediated_non_consumptive_carrier_candidate_native_gap_preserved",
            i5c.get("iteration5c_summary", {}),
        ),
        check("thresholds_declared_before_use", threshold_record()["declared_before_use"], threshold_record()),
        check("source_i5c_su4_candidate_count", len(source_rows) == 3, [row["row_id"] for row in source_rows]),
        check("artifact_manifest_non_empty", len(artifact_manifest) >= 40, len(artifact_manifest)),
        check(
            "artifact_hashes_match",
            all(item["sha256"] == sha256_file(item["path"]) for item in artifact_manifest),
            len(artifact_manifest),
        ),
        check(
            "all_positive_contexts_passed",
            all(record["passed"] for row in rows for record in row["context_records"]),
            [
                {
                    "row_id": row["row_id"],
                    "contexts": [
                        {"context_id": record["context_id"], "passed": record["passed"]}
                        for record in row["context_records"]
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "all_rows_provisional_su5_candidates",
            len(candidate_rows) == 3 and all(not row["su5_supported"] for row in rows),
            [row["provisional_su_ladder_rung"] for row in rows],
        ),
        check(
            "carrier_update_disabled_after_load",
            all(
                not record["gate"]["new_carrier_update_after_loaded_snapshot"]
                for row in rows
                for record in row["context_records"]
            ),
            "no new carrier update after I5-C snapshots",
        ),
        check(
            "peer_label_swap_controls_fail_closed",
            all(
                any(
                    control["control_id"] == "peer_label_swap_reentry_control"
                    and control["status"] == "failed_closed"
                    for control in row["controls"]
                )
                for row in rows
            ),
            [row["row_id"] for row in rows],
        ),
        check(
            "native_conductance_memory_still_blocked",
            all(not row["native_route_conductance_memory_supported"] for row in rows),
            "native policy gap preserved",
        ),
        check(
            "controls_fail_closed",
            all(control["status"] == "failed_closed" and control["claim_allowed"] is False for control in all_controls),
            [control["control_id"] for control in all_controls],
        ),
        check(
            "unsafe_flags_all_false",
            all(all(value is False for value in row["unsafe_claim_flags"].values()) for row in rows),
            "all rows",
        ),
        check(
            "artifact_paths_repository_relative",
            all(not item["path"].startswith("/") for item in artifact_manifest),
            "relative paths only",
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i6a_carrier_transfer_reentry_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "6-A",
        "purpose": "transfer and later re-entry over I5-C producer-mediated non-consumptive carrier rows",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_producer_mediated_carrier_transfer_candidates_pending_i7_no_final_su5"
            if not failed_checks
            else "failed_carrier_transfer_reentry_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I5C_OUTPUT_PATH, "i5c_alternative_non_consumptive_carrier_probe"),
        ],
        "carrier_transfer_policy": {
            "consumes_i5c_only": True,
            "existing_i6_replaced": False,
            "packet_readout_branch_reopened": False,
            "producer_carrier_update_after_load_allowed": False,
            "positive_rows_are_producer_mediated": True,
            "native_route_conductance_memory_policy_available": False,
            "su6_or_final_n22_allowed": False,
        },
        "transfer_rows": rows,
        "artifact_manifest": artifact_manifest,
        "iteration6a_summary": summary,
        "geometric_interpretation": {
            "short_read": (
                "I6-A shows that the I5-C edge/conductance carriers remain present "
                "through delayed target re-entry and peer-corridor flux followed by "
                "target re-entry. No new carrier update is applied after loading the "
                "I5-C snapshots."
            ),
            "claim_boundary": (
                "This is a provisional producer-mediated SU5 carrier-transfer "
                "candidate pending I7 controls. It does not supersede the existing "
                "I6 packet-readout result, does not support native conductance memory, "
                "and does not support SU6, final N22, the N21 ND6 bridge, semantic "
                "learning, choice, agency, native support, sentience, or Phase 8."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return canonicalize_json_value(output)


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N22 Iteration 6-A - Carrier Transfer / Re-entry Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["claim_boundary"],
        "",
        "## Transfer Rows",
        "",
        "| Row | Decision | Rung | Contexts Passed | SU5 Final |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in output["transfer_rows"]:
        contexts_passed = sum(1 for record in row["context_records"] if record["passed"])
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i6a_row_')}` | "
            f"`{row['row_decision']}` | "
            f"`{row['provisional_su_ladder_rung']}` | "
            f"{contexts_passed}/{len(row['context_records'])} | "
            f"`{str(row['su5_supported']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Context Details",
            "",
            "| Row | Context | Ratio | Margin | New Carrier Update | Passed |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in output["transfer_rows"]:
        label = row["row_id"].removeprefix("n22_i6a_row_")
        for record in row["context_records"]:
            gate = record["gate"]
            lines.append(
                "| "
                f"`{label}` | "
                f"`{record['context_id']}` | "
                f"{gate['carrier_transfer_ratio']:.6f} | "
                f"{gate['target_over_peer_margin']:.6f} | "
                f"`{str(gate['new_carrier_update_after_loaded_snapshot']).lower()}` | "
                f"`{str(record['passed']).lower()}` |"
            )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in output["checks"]:
        detail = item["detail"]
        if isinstance(detail, (dict, list)):
            detail_text = json.dumps(detail, sort_keys=True)
        else:
            detail_text = str(detail)
        if len(detail_text) > 140:
            detail_text = detail_text[:137] + "..."
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail_text} |"
        )
    lines.append("")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    output = load_json(rel(OUTPUT))
    write_report(output)


if __name__ == "__main__":
    main()
