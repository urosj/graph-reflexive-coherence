#!/usr/bin/env python3
"""Build N22 Iteration 6-B carrier transfer stress-boundary probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n22_carrier_transfer_stress_boundary_probe.json"
REPORT = EXPERIMENT / "reports" / "n22_carrier_transfer_stress_boundary_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_carrier_transfer_stress_boundary_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_carrier_transfer_stress_boundary_probe.py"
)

I5C_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_alternative_nonconsumptive_carrier_probe.json"
)
I6A_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_carrier_transfer_reentry_probe.json"
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

RUN_ID = "n22_i6b_carrier_transfer_stress_boundary"
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

MIN_TRANSFER_CARRIER_RATIO = 0.90
MIN_TRANSFER_TARGET_OVER_PEER_MARGIN = 0.05
MAX_CARRIER_LOSS_AFTER_STRESS = 0.02
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
MAX_BUDGET_ERROR = 1e-9

STRESS_CONTEXTS = [
    {
        "context_id": "long_idle_delay_target_reentry",
        "stress_role": "longer_delay_before_target_reentry",
        "steps": [
            {"route": "target", "amount": 0.02, "event_time": 12.0, "scheduler_index": 120},
        ],
    },
    {
        "context_id": "strong_peer_corridor_then_target_reentry",
        "stress_role": "stronger_peer_corridor_flux_before_target_reentry",
        "steps": [
            {"route": "peer", "amount": 0.04, "event_time": 4.0, "scheduler_index": 40},
            {"route": "target", "amount": 0.02, "event_time": 8.0, "scheduler_index": 80},
        ],
    },
    {
        "context_id": "repeated_target_reentry_pair",
        "stress_role": "two_target_reentry_events_before_readback",
        "steps": [
            {"route": "target", "amount": 0.02, "event_time": 6.0, "scheduler_index": 60},
            {"route": "target", "amount": 0.02, "event_time": 8.0, "scheduler_index": 80},
        ],
    },
    {
        "context_id": "mixed_peer_target_corridor_sequence",
        "stress_role": "alternating_peer_and_target_corridor_flux",
        "steps": [
            {"route": "peer", "amount": 0.02, "event_time": 4.0, "scheduler_index": 40},
            {"route": "target", "amount": 0.02, "event_time": 5.0, "scheduler_index": 50},
            {"route": "peer", "amount": 0.02, "event_time": 7.0, "scheduler_index": 70},
            {"route": "target", "amount": 0.02, "event_time": 8.0, "scheduler_index": 80},
        ],
    },
]

CONTROL_CONTEXTS = [
    "peer_label_swap_under_stress_control",
    "active_carrier_update_carryover_control",
    "native_conductance_memory_relabel_control",
    "stress_success_as_final_su5_relabel_control",
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
        "threshold_record_id": "n22_i6b_carrier_transfer_stress_boundary_thresholds",
        "declared_before_use": True,
        "consumes_i5c_and_i6a_only": True,
        "stress_contexts": [
            {
                "context_id": context["context_id"],
                "stress_role": context["stress_role"],
                "steps": context["steps"],
            }
            for context in STRESS_CONTEXTS
        ],
        "control_contexts": CONTROL_CONTEXTS,
        "min_transfer_carrier_ratio": MIN_TRANSFER_CARRIER_RATIO,
        "min_transfer_target_over_peer_margin": MIN_TRANSFER_TARGET_OVER_PEER_MARGIN,
        "max_carrier_loss_after_stress": MAX_CARRIER_LOSS_AFTER_STRESS,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "max_budget_error": MAX_BUDGET_ERROR,
        "carrier_retune_allowed": False,
        "producer_carrier_update_after_load_allowed": False,
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
    route: str,
    amount: float,
    event_time: float,
    scheduler_index: int,
) -> None:
    route_spec = TARGET_REENTRY if route == "target" else PEER_CORRIDOR
    model.schedule_packet_departure(
        source_node_id=route_spec["source_node_id"],
        target_node_id=route_spec["target_node_id"],
        edge_id=route_spec["edge_id"],
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
        trigger_kind="n22_i6b_transfer_stress_carrier_readback",
        trigger_source="iteration_6b_explicit_carrier_readback",
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
    context: dict[str, Any],
    snapshot_key: str,
    baseline_snapshot_key: str,
    source_delta: float,
    peer_model_snapshot_key: str | None,
    control: bool = False,
) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    context_id = str(context["context_id"])
    run_role = f"{source_row['carrier_family']}_{context_id}"
    model = load_model(source_row["snapshots"][snapshot_key])
    baseline = load_model(source_row["snapshots"][baseline_snapshot_key])
    loaded_signature = state_signature(model, "loaded_post_carrier_state")
    loaded_snapshot = save_snapshot(model, run_role, "loaded")
    events: list[dict[str, Any]] = []
    for index, step in enumerate(context["steps"]):
        phase = f"{context_id}_step_{index}_{step['route']}"
        schedule_packet(model, **step)
        events.extend(drain_queue(model, run_role, phase))
    after_stress = state_signature(model, "after_transfer_stress")
    after_stress_snapshot = save_snapshot(model, run_role, "after_stress")
    readback_record = readback(model, run_role, "post_stress_readback")
    after_readback = state_signature(model, "after_stress_readback")
    after_readback_snapshot = save_snapshot(model, run_role, "after_readback")
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, events)

    baseline_signature = state_signature(baseline, "baseline_pre_carrier")
    carrier_delta_after_stress = (
        after_readback["target_edge_state"]["base_conductance"]
        - baseline_signature["target_edge_state"]["base_conductance"]
    )
    ratio = carrier_delta_after_stress / source_delta if source_delta else 0.0
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
    margin = carrier_delta_after_stress - peer_delta
    gate = {
        "context_id": context_id,
        "stress_role": context.get("stress_role", "control"),
        "source_i5c_carrier_delta": source_delta,
        "carrier_delta_after_stress_readback": carrier_delta_after_stress,
        "carrier_transfer_ratio": ratio,
        "carrier_loss_after_stress_readback": carrier_loss,
        "peer_same_budget_target_edge_delta": peer_delta,
        "target_over_peer_margin": margin,
        "carrier_preserved_after_stress": (
            ratio >= MIN_TRANSFER_CARRIER_RATIO
            and carrier_loss <= MAX_CARRIER_LOSS_AFTER_STRESS
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
        gate["carrier_preserved_after_stress"]
        and gate["same_budget_peer_separated"]
        and gate["support_floor_result"] == "preserved"
        and gate["coherence_floor_result"] == "preserved"
        and gate["budget_result"] == "preserved"
        and gate["new_carrier_update_after_loaded_snapshot"] is False
        and not control
    )
    artifact = {
        "artifact_id": f"n22_i6b_{run_role}_run",
        "source_i5c_row_id": source_row["row_id"],
        "carrier_family": source_row["carrier_family"],
        "context_id": context_id,
        "loaded_signature": loaded_signature,
        "after_stress_signature": after_stress,
        "after_readback_signature": after_readback,
        "readback_record": readback_record,
        "event_count": len(events),
        "event_counts_by_kind": dict(Counter(row["kind"] for row in events)),
        "gate": gate,
        "passed": passed,
        "control_context": control,
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
            "after_stress_snapshot_path": after_stress_snapshot,
            "after_readback_snapshot_path": after_readback_snapshot,
            "event_log_path": rel(event_log_path),
            "gate": gate,
            "passed": passed,
            "readback_record": readback_record,
        },
        [
            (rel(artifact_path), f"{run_role}_run"),
            (loaded_snapshot, f"{run_role}_loaded_snapshot"),
            (after_stress_snapshot, f"{run_role}_after_stress_snapshot"),
            (after_readback_snapshot, f"{run_role}_after_readback_snapshot"),
            (rel(event_log_path), f"{run_role}_event_log"),
        ],
    )


def stress_boundary(context_records: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = [record["gate"]["carrier_transfer_ratio"] for record in context_records]
    margins = [record["gate"]["target_over_peer_margin"] for record in context_records]
    losses = [record["gate"]["carrier_loss_after_stress_readback"] for record in context_records]
    return {
        "stress_context_count": len(context_records),
        "min_carrier_transfer_ratio": min(ratios),
        "max_carrier_loss_after_stress": max(losses),
        "min_target_over_peer_margin": min(margins),
        "all_stress_contexts_passed": all(record["passed"] for record in context_records),
        "stress_envelope_scope": "local_i5c_carrier_contexts_only",
    }


def build_stress_row(source_row: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    source_delta = source_row["carrier_gate"]["target_carrier_delta"]
    context_records: list[dict[str, Any]] = []
    manifest_entries: list[tuple[str, str]] = []
    for context in STRESS_CONTEXTS:
        record, paths = run_context(
            source_row=source_row,
            context=context,
            snapshot_key="target_post",
            baseline_snapshot_key="target_pre",
            source_delta=source_delta,
            peer_model_snapshot_key="peer_post",
        )
        context_records.append(record)
        manifest_entries.extend(paths)

    peer_control, peer_control_paths = run_context(
        source_row=source_row,
        context={
            "context_id": "peer_label_swap_under_stress_control",
            "stress_role": "peer_only_stress_must_not_count_as_target_transfer",
            "steps": [
                {"route": "peer", "amount": 0.04, "event_time": 4.0, "scheduler_index": 40},
                {"route": "peer", "amount": 0.02, "event_time": 8.0, "scheduler_index": 80},
            ],
        },
        snapshot_key="peer_post",
        baseline_snapshot_key="peer_pre",
        source_delta=source_delta,
        peer_model_snapshot_key="peer_post",
        control=True,
    )
    manifest_entries.extend(peer_control_paths)
    boundary = stress_boundary(context_records)
    positive_contexts_passed = boundary["all_stress_contexts_passed"]
    controls = [
        {
            "control_id": "peer_label_swap_under_stress_control",
            "status": "failed_closed" if not peer_control["passed"] else "failed_open",
            "claim_allowed": False,
            "primary_blocker": "peer_stress_has_no_target_carrier_delta",
            "reason": "Peer-only stress cannot satisfy target carrier transfer/re-entry.",
            "control_record": peer_control,
        },
        {
            "control_id": "active_carrier_update_carryover_control",
            "status": "failed_closed",
            "claim_allowed": False,
            "primary_blocker": "producer_carrier_update_after_loaded_snapshot_blocked",
            "reason": "I6-B applies stress packets only; no new carrier update is allowed after loading I5-C snapshots.",
        },
        {
            "control_id": "native_conductance_memory_relabel_control",
            "status": "failed_closed",
            "claim_allowed": False,
            "primary_blocker": "native_route_conductance_memory_policy_missing",
            "reason": "The stress-stable carrier remains producer-mediated naturalization debt.",
        },
        {
            "control_id": "stress_success_as_final_su5_relabel_control",
            "status": "failed_closed",
            "claim_allowed": False,
            "primary_blocker": "i7_replay_and_control_matrix_not_run",
            "reason": "Stress-context survival is provisional until I7 control classification.",
        },
    ]
    row = {
        "row_id": f"n22_i6b_row_{source_row['carrier_family']}",
        "source_i5c_row_id": source_row["row_id"],
        "source_i6a_role": "stress_extension_of_i6a_carrier_transfer_candidate",
        "carrier_family": source_row["carrier_family"],
        "row_decision": "partial" if positive_contexts_passed else "blocked",
        "decision_scope": (
            "producer_mediated_carrier_transfer_stress_boundary_candidate_pending_I7_controls"
            if positive_contexts_passed
            else "blocked_before_carrier_transfer_stress_boundary"
        ),
        "provisional_su_ladder_rung": (
            "SU5_producer_mediated_carrier_transfer_stress_boundary_candidate_pending_I7"
            if positive_contexts_passed
            else "demoted_before_SU5"
        ),
        "supporting_su5_stress_candidate": positive_contexts_passed,
        "stress_boundary": boundary,
        "su5_supported": False,
        "su6_supported": False,
        "native_route_conductance_memory_supported": False,
        "stress_context_records": context_records,
        "controls": controls,
        "variable_classification": source_row["variable_classification"],
        "claim_ceiling": (
            "provisional producer-mediated carrier transfer stress-boundary "
            "candidate pending I7; not native conductance memory, semantic "
            "learning, agency, native support, SU6, final N22, or N21 ND6 bridge"
        ),
        "susceptibility_update_claim_allowed": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    row["row_digest"] = digest_value({key: value for key, value in row.items() if key != "row_digest"})
    return row, manifest_entries


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    i5c = load_json(I5C_OUTPUT_PATH)
    i6a = load_json(I6A_OUTPUT_PATH)
    threshold_path = ARTIFACT_DIR / "n22_i6b_thresholds_declared_before_use.json"
    write_json(threshold_path, threshold_record())
    runtime_config = {
        "config_id": "n22_i6b_carrier_transfer_stress_boundary_runtime_config",
        "model_family": "LGRC9V3",
        "source_iteration": "I5-C plus I6-A",
        "fixture_source": "I5-C source-current snapshots",
        "spark_lane": LANE_B,
        "stress_contexts": STRESS_CONTEXTS,
        "control_contexts": CONTROL_CONTEXTS,
        "thresholds": threshold_record(),
        "carrier_retune_allowed": False,
        "producer_carrier_update_after_load_allowed": False,
    }
    runtime_config_path = ARTIFACT_DIR / "n22_i6b_runtime_config.json"
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
        row, entries = build_stress_row(source_row)
        rows.append(row)
        manifest_entries.extend(entries)
    artifact_manifest = file_manifest(manifest_entries)
    stress_candidate_rows = [row for row in rows if row["supporting_su5_stress_candidate"]]
    all_controls = [control for row in rows for control in row["controls"]]
    all_boundaries = [row["stress_boundary"] for row in rows]
    summary = {
        "source_i5c_su4_candidate_count": len(source_rows),
        "source_i6a_su5_candidate_count": len(
            [
                row
                for row in i6a.get("transfer_rows", [])
                if row.get("supporting_su5_candidate") is True
            ]
        ),
        "provisional_su5_stress_candidate_count": len(stress_candidate_rows),
        "stress_context_count_per_row": len(STRESS_CONTEXTS),
        "stress_context_pass_count": sum(
            1 for row in rows for record in row["stress_context_records"] if record["passed"]
        ),
        "min_carrier_transfer_ratio_observed": min(
            boundary["min_carrier_transfer_ratio"] for boundary in all_boundaries
        ),
        "min_target_over_peer_margin_observed": min(
            boundary["min_target_over_peer_margin"] for boundary in all_boundaries
        ),
        "max_carrier_loss_after_stress_observed": max(
            boundary["max_carrier_loss_after_stress"] for boundary in all_boundaries
        ),
        "i6a_replaced": False,
        "existing_i6_superseded": False,
        "packet_readout_branch_status": "unchanged_consumptive_SU3_transfer_readout_expression_only",
        "i5c_i6a_branch_status": "provisional_producer_mediated_SU5_stress_boundary_candidate_pending_I7",
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
        check(
            "i6a_passed",
            i6a.get("acceptance_state")
            == "accepted_producer_mediated_carrier_transfer_candidates_pending_i7_no_final_su5",
            i6a.get("iteration6a_summary", {}),
        ),
        check("thresholds_declared_before_use", threshold_record()["declared_before_use"], threshold_record()),
        check("source_i5c_su4_candidate_count", len(source_rows) == 3, [row["row_id"] for row in source_rows]),
        check(
            "source_i6a_su5_candidate_count",
            summary["source_i6a_su5_candidate_count"] == 3,
            summary["source_i6a_su5_candidate_count"],
        ),
        check("artifact_manifest_non_empty", len(artifact_manifest) >= 75, len(artifact_manifest)),
        check(
            "artifact_hashes_match",
            all(item["sha256"] == sha256_file(item["path"]) for item in artifact_manifest),
            len(artifact_manifest),
        ),
        check(
            "all_stress_contexts_passed",
            all(record["passed"] for row in rows for record in row["stress_context_records"]),
            [
                {
                    "row_id": row["row_id"],
                    "contexts": [
                        {"context_id": record["context_id"], "passed": record["passed"]}
                        for record in row["stress_context_records"]
                    ],
                }
                for row in rows
            ],
        ),
        check(
            "all_rows_provisional_su5_stress_candidates",
            len(stress_candidate_rows) == 3 and all(not row["su5_supported"] for row in rows),
            [row["provisional_su_ladder_rung"] for row in rows],
        ),
        check(
            "carrier_update_disabled_after_load",
            all(
                not record["gate"]["new_carrier_update_after_loaded_snapshot"]
                for row in rows
                for record in row["stress_context_records"]
            ),
            "no new carrier update after I5-C snapshots",
        ),
        check(
            "peer_label_swap_controls_fail_closed",
            all(
                any(
                    control["control_id"] == "peer_label_swap_under_stress_control"
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
        check(
            "final_claims_blocked",
            not summary["su5_supported"]
            and not summary["su6_supported"]
            and not summary["final_n22_supported"]
            and summary["n21_nd6_bridge_status"] == "not_supported",
            summary,
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i6b_carrier_transfer_stress_boundary_probe",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "6-B",
        "purpose": "bounded stress-boundary probe over I5-C/I6-A producer-mediated carrier transfer candidates",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_producer_mediated_carrier_transfer_stress_boundary_pending_i7_no_final_su5"
            if not failed_checks
            else "failed_carrier_transfer_stress_boundary_probe"
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I5C_OUTPUT_PATH, "i5c_alternative_non_consumptive_carrier_probe"),
            source_record(I6A_OUTPUT_PATH, "i6a_carrier_transfer_reentry_probe"),
        ],
        "carrier_stress_policy": {
            "consumes_i5c_and_i6a_only": True,
            "i6a_replaced": False,
            "existing_i6_replaced": False,
            "packet_readout_branch_reopened": False,
            "carrier_retune_allowed": False,
            "producer_carrier_update_after_load_allowed": False,
            "positive_rows_are_producer_mediated": True,
            "native_route_conductance_memory_policy_available": False,
            "su6_or_final_n22_allowed": False,
        },
        "stress_rows": rows,
        "artifact_manifest": artifact_manifest,
        "iteration6b_summary": summary,
        "geometric_interpretation": {
            "short_read": (
                "I6-B stress-tests the I5-C/I6-A edge/conductance carriers under "
                "longer delay, stronger peer-corridor flux, repeated target re-entry, "
                "and mixed peer/target corridor stress. The carrier remains present "
                "without any new producer carrier update after loading I5-C snapshots."
            ),
            "claim_boundary": (
                "This is bounded producer-mediated SU5 stress-boundary evidence "
                "pending I7 controls. It does not replace I6-A, does not rescue the "
                "packet-readout branch, does not support native conductance memory, "
                "and does not support final SU5, SU6, final N22, the N21 ND6 bridge, "
                "semantic learning, choice, agency, native support, sentience, or Phase 8."
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
        "# N22 Iteration 6-B - Carrier Transfer Stress-Boundary Probe",
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
        "## Stress Rows",
        "",
        "| Row | Decision | Rung | Stress Contexts Passed | Min Ratio | Min Margin | SU5 Final |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in output["stress_rows"]:
        contexts_passed = sum(1 for record in row["stress_context_records"] if record["passed"])
        boundary = row["stress_boundary"]
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i6b_row_')}` | "
            f"`{row['row_decision']}` | "
            f"`{row['provisional_su_ladder_rung']}` | "
            f"{contexts_passed}/{len(row['stress_context_records'])} | "
            f"{boundary['min_carrier_transfer_ratio']:.6f} | "
            f"{boundary['min_target_over_peer_margin']:.6f} | "
            f"`{str(row['su5_supported']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Stress Context Details",
            "",
            "| Row | Context | Ratio | Margin | New Carrier Update | Passed |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in output["stress_rows"]:
        label = row["row_id"].removeprefix("n22_i6b_row_")
        for record in row["stress_context_records"]:
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
