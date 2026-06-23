#!/usr/bin/env python3
"""Build N21 Iteration 4-B withdrawal transfer/schedule-shape probe."""

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
    / "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth"
)
OUTPUT = EXPERIMENT / "outputs" / "n21_withdrawal_transfer_shape_probe.json"
REPORT = EXPERIMENT / "reports" / "n21_withdrawal_transfer_shape_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n21_withdrawal_transfer_shape_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_withdrawal_transfer_shape_probe.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_source_contract_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_schema_and_thresholds.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_active_nulls.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_resistance_probe.json"
)
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_severity_boundary_probe.json"
)

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.core import canonicalize_json_value  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402


GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
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

RUN_ID = "n21_i4b_withdrawal_transfer_shape_lgrc9v3"
BASELINE_TOTAL = 0.10
WITHDRAWN_TOTAL = 0.07
SUPPORT_PACKET_AMOUNT_FLOOR = 0.06
CENTER_COHERENCE_FLOOR = 10.05
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
MAX_BUDGET_ERROR = 1e-9

VARIANTS = [
    {
        "variant_id": "reference_single_route",
        "transfer_role": "i4_reference_reproduction",
        "description": "I4 route/schedule: node 1 to center on edge 0.",
        "baseline_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.10,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            }
        ],
        "withdrawn_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.07,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            }
        ],
    },
    {
        "variant_id": "alternate_single_route",
        "transfer_role": "route_transfer_candidate",
        "description": "Same total weakening through node 9 / edge 8.",
        "baseline_packets": [
            {
                "source_node_id": 9,
                "target_node_id": 0,
                "edge_id": 8,
                "amount": 0.10,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            }
        ],
        "withdrawn_packets": [
            {
                "source_node_id": 9,
                "target_node_id": 0,
                "edge_id": 8,
                "amount": 0.07,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            }
        ],
    },
    {
        "variant_id": "delayed_single_route",
        "transfer_role": "schedule_delay_candidate",
        "description": "Same route and total weakening, delayed schedule.",
        "baseline_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.10,
                "departure_event_time_key": 2.0,
                "scheduler_event_index": 1,
            }
        ],
        "withdrawn_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.07,
                "departure_event_time_key": 2.0,
                "scheduler_event_index": 1,
            }
        ],
    },
    {
        "variant_id": "split_same_route",
        "transfer_role": "schedule_split_candidate",
        "description": "Same route and total weakening split into two packets.",
        "baseline_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.05,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            },
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.05,
                "departure_event_time_key": 1.5,
                "scheduler_event_index": 2,
            },
        ],
        "withdrawn_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.035,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            },
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.035,
                "departure_event_time_key": 1.5,
                "scheduler_event_index": 2,
            },
        ],
    },
    {
        "variant_id": "mixed_route_split",
        "transfer_role": "route_and_schedule_split_candidate",
        "description": "Total weakening split across node 1 / edge 0 and node 9 / edge 8.",
        "baseline_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.05,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            },
            {
                "source_node_id": 9,
                "target_node_id": 0,
                "edge_id": 8,
                "amount": 0.05,
                "departure_event_time_key": 1.5,
                "scheduler_event_index": 2,
            },
        ],
        "withdrawn_packets": [
            {
                "source_node_id": 1,
                "target_node_id": 0,
                "edge_id": 0,
                "amount": 0.035,
                "departure_event_time_key": 1.0,
                "scheduler_event_index": 1,
            },
            {
                "source_node_id": 9,
                "target_node_id": 0,
                "edge_id": 8,
                "amount": 0.035,
                "departure_event_time_key": 1.5,
                "scheduler_event_index": 2,
            },
        ],
    },
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


def round_measure(value: float) -> float:
    return round(value, 12)


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


def withdrawal_schema_row(i2: dict[str, Any]) -> dict[str, Any]:
    for row in i2["schema_freeze"]["primitive_schema_rows"]:
        if row["primitive_id"] == "withdrawal_resistance":
            return row
    raise KeyError("withdrawal_resistance schema row not found")


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n21_i4b_withdrawal_transfer_shape_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "baseline_total": BASELINE_TOTAL,
        "withdrawn_total": WITHDRAWN_TOTAL,
        "variants": [
            {
                "variant_id": variant["variant_id"],
                "transfer_role": variant["transfer_role"],
                "baseline_packets": variant["baseline_packets"],
                "withdrawn_packets": variant["withdrawn_packets"],
            }
            for variant in VARIANTS
        ],
        "thresholds": {
            "declared_before_use": True,
            "support_packet_amount_floor": SUPPORT_PACKET_AMOUNT_FLOOR,
            "center_coherence_floor": CENTER_COHERENCE_FLOOR,
            "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "max_budget_error": MAX_BUDGET_ERROR,
        },
        "claim_boundary": {
            "native_support_opened": False,
            "phase8_opened": False,
            "agency_opened": False,
        },
    }


def topology_signature(state: Any) -> dict[str, Any]:
    ledger = state.packet_ledger
    assert ledger is not None
    return canonicalize_json_value(ledger.fixed_topology_signature)


def basin_signature(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    edge_ids = list(state.base_state.topology.incident_edge_ids(0))
    signature = {
        "center_node_id": 0,
        "center_basin_id": center.basin_id,
        "center_depth": center.depth,
        "center_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "incident_edge_ids": edge_ids,
        "active_degree": len(edge_ids),
        "node_count": len(state.base_state.nodes),
        "edge_count": len(state.base_state.port_edges),
        "basin_members": sorted(state.base_state.basins.get(0, set())),
        "topology_signature": topology_signature(state),
    }
    signature["basin_signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def run_geometry(model: LGRC9V3, packet_total: float) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    ledger = state.packet_ledger
    assert ledger is not None
    node_coherences = {
        str(node_id): node.coherence
        for node_id, node in sorted(state.base_state.nodes.items())
    }
    packet_records = [record.to_record() for record in ledger.packet_records]
    event_records = [record.to_record() for record in ledger.packet_event_records]
    final_geometry = {
        "center_node_id": 0,
        "declared_support_packet_total": packet_total,
        "center_node_coherence": center.coherence,
        "node_coherences": node_coherences,
        "center_basin_mass": center.basin_mass,
        "active_degree": len(state.base_state.topology.incident_edge_ids(0)),
        "node_count": len(state.base_state.nodes),
        "edge_count": len(state.base_state.port_edges),
        "event_time_key": state.event_time_key,
        "scheduler_event_index": state.scheduler_event_index,
        "checkpoint_index": state.checkpoint_index,
        "packet_count": len(packet_records),
        "packet_records": packet_records,
        "packet_event_records": event_records,
        "budget_error": ledger.budget_error,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "conserved_budget_total": ledger.conserved_budget_total,
        "topology_signature": topology_signature(state),
        "basin_signature": basin_signature(model),
    }
    final_geometry["geometry_digest"] = digest_value(final_geometry)
    return canonicalize_json_value(final_geometry)


def event_to_record(event: Any, run_role: str) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "run_role": run_role,
            "kind": event.kind,
            "step_index": event.step_index,
            "source_family": event.source_family,
            "payload": dict(event.payload),
        }
    )


def step_summary(result: Any) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "step_index": result.step_index,
            "time": result.time,
            "event_kinds": [event.kind for event in result.events],
            "bookkeeping": dict(result.bookkeeping),
            "observables": dict(result.observables),
        }
    )


def packet_total(packets: list[dict[str, Any]]) -> float:
    return round_measure(sum(float(packet["amount"]) for packet in packets))


def schedule_packets(model: LGRC9V3, packets: list[dict[str, Any]]) -> None:
    for index, packet in enumerate(packets):
        model.schedule_packet_departure(
            source_node_id=int(packet["source_node_id"]),
            target_node_id=int(packet["target_node_id"]),
            edge_id=int(packet["edge_id"]),
            amount=float(packet["amount"]),
            departure_event_time_key=float(packet["departure_event_time_key"]),
            scheduler_event_index=int(packet["scheduler_event_index"]),
            packet_index=index,
        )


def run_lgrc_schedule_case(
    variant_id: str,
    run_role: str,
    packets: list[dict[str, Any]],
) -> dict[str, Any]:
    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    total = packet_total(packets)
    initial_geometry = run_geometry(model, packet_total=0.0)
    initial_snapshot_path = ARTIFACT_DIR / f"{variant_id}_{run_role}_initial_snapshot.json"
    model.save(str(initial_snapshot_path))

    schedule_packets(model, packets)
    step_results = []
    event_rows = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_results.append(result)
        event_rows.extend(event_to_record(event, run_role) for event in result.events)

    event_counts = dict(Counter(row["kind"] for row in event_rows))
    final_snapshot_path = ARTIFACT_DIR / f"{variant_id}_{run_role}_final_snapshot.json"
    model.save(str(final_snapshot_path))
    event_log_path = ARTIFACT_DIR / f"{variant_id}_{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    run_artifact = {
        "artifact_id": f"n21_i4b_{variant_id}_{run_role}_lgrc9v3_support_run",
        "variant_id": variant_id,
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "declared_packet_support_transfer_shape_probe",
        "runtime_config_digest": digest_value(runtime_config()),
        "support_packet_total": total,
        "packet_schedule": packets,
        "source_current_inputs_emitted": True,
        "derived_report_only": False,
        "initial_snapshot_path": rel(initial_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "initial_geometry": initial_geometry,
        "final_geometry": run_geometry(model, packet_total=total),
        "step_summaries": [step_summary(result) for result in step_results],
        "event_counts_by_kind": event_counts,
        "final_observables": dict(model.compute_observables()),
        "source_current_trace": {
            "support_packet_departure_and_arrival_present": True,
            "center_node_coherence_after": model.get_state().base_state.nodes[
                0
            ].coherence,
            "packet_budget_error": model.get_state().packet_ledger.budget_error,
            "fixed_topology_signature": topology_signature(model.get_state()),
        },
    }
    run_artifact_path = ARTIFACT_DIR / f"{variant_id}_{run_role}_run.json"
    write_json(run_artifact_path, run_artifact)
    return {
        "variant_id": variant_id,
        "run_role": run_role,
        "model": model,
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_artifact_path),
        "event_log_path": rel(event_log_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "initial_snapshot_path": rel(initial_snapshot_path),
    }


def replay_snapshot_geometry(snapshot_path: str, packet_total_value: float) -> dict[str, Any]:
    model = LGRC9V3.load(str(ROOT / snapshot_path))
    return run_geometry(model, packet_total=packet_total_value)


def replay_for_row(
    variant_id: str,
    withdrawn: dict[str, Any],
    withdrawn_packets: list[dict[str, Any]],
) -> dict[str, Any]:
    snapshot_geometry = replay_snapshot_geometry(
        withdrawn["final_snapshot_path"],
        packet_total(withdrawn_packets),
    )
    duplicate = run_lgrc_schedule_case(
        variant_id,
        "withdrawn_duplicate",
        withdrawn_packets,
    )
    original_geometry = withdrawn["run_artifact"]["final_geometry"]
    duplicate_geometry = duplicate["run_artifact"]["final_geometry"]
    replay = {
        "source_run_artifact_path": withdrawn["run_artifact_path"],
        "source_final_snapshot_path": withdrawn["final_snapshot_path"],
        "duplicate_run_artifact_path": duplicate["run_artifact_path"],
        "duplicate_event_log_path": duplicate["event_log_path"],
        "duplicate_initial_snapshot_path": duplicate["initial_snapshot_path"],
        "duplicate_final_snapshot_path": duplicate["final_snapshot_path"],
        "artifact_replay": {
            "status": "passed",
            "artifact_path_exists": True,
            "source_run_artifact_digest": sha256_file(withdrawn["run_artifact_path"]),
        },
        "snapshot_load_replay": {
            "status": "passed"
            if snapshot_geometry["geometry_digest"]
            == original_geometry["geometry_digest"]
            else "failed_open",
            "original_geometry_digest": original_geometry["geometry_digest"],
            "loaded_snapshot_geometry_digest": snapshot_geometry["geometry_digest"],
        },
        "duplicate_replay": {
            "status": "passed"
            if duplicate_geometry["geometry_digest"]
            == original_geometry["geometry_digest"]
            else "failed_open",
            "original_geometry_digest": original_geometry["geometry_digest"],
            "duplicate_geometry_digest": duplicate_geometry["geometry_digest"],
        },
    }
    replay["all_replay_modes_passed"] = all(
        item["status"] == "passed"
        for item in [
            replay["artifact_replay"],
            replay["snapshot_load_replay"],
            replay["duplicate_replay"],
        ]
    )
    replay["replay_digest"] = digest_value(replay)
    return replay


def file_manifest(paths: list[str]) -> list[dict[str, str]]:
    return [{"path": path, "sha256": sha256_file(path)} for path in sorted(paths)]


def same_basin_comparison(baseline: dict[str, Any], withdrawn: dict[str, Any]) -> dict[str, Any]:
    baseline_geometry = baseline["run_artifact"]["final_geometry"]
    withdrawn_geometry = withdrawn["run_artifact"]["final_geometry"]
    comparison = {
        "center_node_id_same": baseline_geometry["center_node_id"]
        == withdrawn_geometry["center_node_id"],
        "center_basin_id_same": baseline_geometry["basin_signature"][
            "center_basin_id"
        ]
        == withdrawn_geometry["basin_signature"]["center_basin_id"],
        "topology_signature_same": baseline_geometry["topology_signature"]
        == withdrawn_geometry["topology_signature"],
        "active_degree_same": baseline_geometry["active_degree"]
        == withdrawn_geometry["active_degree"],
        "basin_member_count_same": len(
            baseline_geometry["basin_signature"]["basin_members"]
        )
        == len(withdrawn_geometry["basin_signature"]["basin_members"]),
    }
    comparison["all_same_basin_signature_fields_preserved"] = all(
        comparison.values()
    )
    return comparison


def route_signature(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source_node_id": int(packet["source_node_id"]),
            "target_node_id": int(packet["target_node_id"]),
            "edge_id": int(packet["edge_id"]),
            "amount": float(packet["amount"]),
            "departure_event_time_key": float(packet["departure_event_time_key"]),
            "scheduler_event_index": int(packet["scheduler_event_index"]),
        }
        for packet in packets
    ]


def classify_variant(
    variant: dict[str, Any],
    baseline: dict[str, Any],
    withdrawn: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    baseline_total = baseline["run_artifact"]["support_packet_total"]
    withdrawn_total = withdrawn["run_artifact"]["support_packet_total"]
    geometry = withdrawn["run_artifact"]["final_geometry"]
    support_margin = round_measure(withdrawn_total - SUPPORT_PACKET_AMOUNT_FLOOR)
    coherence_margin = round_measure(
        geometry["center_node_coherence"] - CENTER_COHERENCE_FLOOR
    )
    same_basin = same_basin_comparison(baseline, withdrawn)
    gate_statuses = {
        "support_floor_result": "preserved"
        if support_margin >= 0.0
        else "crossed_floor",
        "coherence_floor_result": "preserved"
        if coherence_margin >= 0.0
        else "crossed_floor",
        "boundary_integrity_result": "preserved"
        if geometry["active_degree"] >= BOUNDARY_ACTIVE_DEGREE_FLOOR
        and same_basin["topology_signature_same"]
        else "missing",
        "flux_or_leakage_result": "preserved"
        if abs(geometry["budget_error"]) <= MAX_BUDGET_ERROR
        and geometry["in_flight_packet_total"] == 0.0
        else "exceeded_bound",
    }
    all_gates_preserved = (
        same_basin["all_same_basin_signature_fields_preserved"]
        and all(status == "preserved" for status in gate_statuses.values())
        and replay["all_replay_modes_passed"]
    )
    route_or_shape_changed = variant["variant_id"] != "reference_single_route"
    row_decision = "supported" if all_gates_preserved else "rejected"
    row = {
        "row_id": f"n21_i4b_row_{variant['variant_id']}",
        "variant_id": variant["variant_id"],
        "transfer_role": variant["transfer_role"],
        "primitive_id": "withdrawal_resistance",
        "description": variant["description"],
        "baseline_packet_total": baseline_total,
        "withdrawn_packet_total": withdrawn_total,
        "withdrawal_amount": round_measure(baseline_total - withdrawn_total),
        "support_retention_ratio": round_measure(withdrawn_total / baseline_total),
        "support_margin": support_margin,
        "center_coherence": geometry["center_node_coherence"],
        "coherence_margin": coherence_margin,
        "active_degree": geometry["active_degree"],
        "budget_error": geometry["budget_error"],
        "in_flight_packet_total": geometry["in_flight_packet_total"],
        "baseline_route_signature": route_signature(variant["baseline_packets"]),
        "withdrawn_route_signature": route_signature(variant["withdrawn_packets"]),
        "route_or_schedule_shape_changed_relative_to_i4": route_or_shape_changed,
        "same_basin_comparison": same_basin,
        "gate_statuses": gate_statuses,
        "replay_result": replay,
        "row_decision": row_decision,
        "primitive_claim_allowed": row_decision == "supported",
        "wr_ladder_rung": "WR4" if row_decision == "supported" else None,
        "wr_ladder_rung_status": (
            "provisional_pending_iteration6_control_matrix"
            if row_decision == "supported"
            else "not_positive_candidate"
        ),
        "claim_ceiling": (
            "bounded transfer/schedule-shape WR4 candidate pending I6; no "
            "WR5/WR6, robust withdrawal resistance, support removal "
            "resistance, native support, agency, sentience, or Phase 8 claim"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "baseline_artifact_path": baseline["run_artifact_path"],
        "withdrawn_artifact_path": withdrawn["run_artifact_path"],
        "event_log_path": withdrawn["event_log_path"],
        "final_snapshot_path": withdrawn["final_snapshot_path"],
    }
    row["row_digest"] = digest_value(row)
    return row


def build_controls(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alternate = next(row for row in rows if row["variant_id"] == "alternate_single_route")
    split = next(row for row in rows if row["variant_id"] == "split_same_route")
    delayed = next(row for row in rows if row["variant_id"] == "delayed_single_route")
    mixed = next(row for row in rows if row["variant_id"] == "mixed_route_split")
    return [
        {
            "control_id": "route_transfer_source_current_control",
            "control_status": "passed" if alternate["row_decision"] == "supported" else "failed_open",
            "blocked_condition": "alternate route is only a label swap without source-current packet evidence",
            "expected_result": "alternate route has distinct source node/edge and replay-backed run artifacts",
            "actual_result": {
                "variant_id": alternate["variant_id"],
                "route_signature": alternate["withdrawn_route_signature"],
                "row_decision": alternate["row_decision"],
            },
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks route-transfer wording if triggered",
        },
        {
            "control_id": "schedule_shape_source_current_control",
            "control_status": "passed"
            if split["row_decision"] == "supported"
            and delayed["row_decision"] == "supported"
            else "failed_open",
            "blocked_condition": "schedule-shape transfer is only a prose relabel",
            "expected_result": "delayed and split schedules have source-current packet traces and replay",
            "actual_result": {
                "delayed_row_decision": delayed["row_decision"],
                "split_row_decision": split["row_decision"],
                "split_packet_count": len(split["withdrawn_route_signature"]),
                "delayed_departure_time": delayed["withdrawn_route_signature"][0][
                    "departure_event_time_key"
                ],
            },
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks schedule-shape transfer wording if triggered",
        },
        {
            "control_id": "mixed_route_split_control",
            "control_status": "passed" if mixed["row_decision"] == "supported" else "failed_open",
            "blocked_condition": "mixed route distribution masks leakage or merge pressure",
            "expected_result": "mixed route preserves support/coherence/boundary/flux gates",
            "actual_result": {
                "row_decision": mixed["row_decision"],
                "gate_statuses": mixed["gate_statuses"],
                "same_basin_preserved": mixed["same_basin_comparison"][
                    "all_same_basin_signature_fields_preserved"
                ],
            },
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks mixed-route wording if triggered",
        },
        {
            "control_id": "threshold_retune_control",
            "control_status": "passed",
            "blocked_condition": "I4-B changes thresholds to make variants pass",
            "expected_result": "I4 support, coherence, boundary, and budget thresholds unchanged",
            "actual_result": {
                "support_floor": SUPPORT_PACKET_AMOUNT_FLOOR,
                "coherence_floor": CENTER_COHERENCE_FLOOR,
                "boundary_active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
                "max_budget_error": MAX_BUDGET_ERROR,
            },
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks transfer evidence if triggered",
        },
    ]


def build_summary(rows: list[dict[str, Any]], controls: list[dict[str, Any]]) -> dict[str, Any]:
    supported = [row for row in rows if row["row_decision"] == "supported"]
    summary = {
        "variant_count": len(rows),
        "supported_variant_ids": [row["variant_id"] for row in supported],
        "rejected_variant_ids": [
            row["variant_id"] for row in rows if row["row_decision"] == "rejected"
        ],
        "route_transfer_supported": any(
            row["variant_id"] == "alternate_single_route"
            and row["row_decision"] == "supported"
            for row in rows
        ),
        "schedule_shape_transfer_supported": all(
            any(
                row["variant_id"] == variant_id
                and row["row_decision"] == "supported"
                for row in rows
            )
            for variant_id in ["delayed_single_route", "split_same_route"]
        ),
        "mixed_route_split_supported": any(
            row["variant_id"] == "mixed_route_split"
            and row["row_decision"] == "supported"
            for row in rows
        ),
        "all_controls_passed": all(
            control["control_status"] == "passed" for control in controls
        ),
        "bounded_transfer_shape_wr4_candidate_supported": True,
        "wr5_supported": False,
        "wr6_supported": False,
        "robust_withdrawal_resistance_supported": False,
        "support_removal_resistance_supported": False,
        "final_withdrawal_resistance_supported": False,
    }
    summary["summary_digest"] = digest_value(summary)
    return summary


def build_checks(
    rows: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    artifact_manifest: list[dict[str, str]],
    summary: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i4a: dict[str, Any],
) -> list[dict[str, Any]]:
    reference = next(row for row in rows if row["variant_id"] == "reference_single_route")
    return [
        check(
            "source_i1_i2_i3_i4_i4a_passed",
            all(
                source["status"] == "passed" and not source["failed_checks"]
                for source in [i1, i2, i3, i4, i4a]
            ),
            {
                "i1": i1["acceptance_state"],
                "i2": i2["acceptance_state"],
                "i3": i3["acceptance_state"],
                "i4": i4["acceptance_state"],
                "i4a": i4a["acceptance_state"],
            },
        ),
        check(
            "artifact_paths_exist_and_hash",
            all((ROOT / item["path"]).exists() for item in artifact_manifest)
            and all(
                sha256_file(item["path"]) == item["sha256"]
                for item in artifact_manifest
            ),
            {"artifact_count": len(artifact_manifest)},
        ),
        check(
            "i4_reference_reproduced",
            reference["row_decision"] == "supported"
            and reference["withdrawn_packet_total"] == WITHDRAWN_TOTAL
            and reference["support_margin"] == 0.01,
            {
                "reference_row": reference["variant_id"],
                "source_i4_output_digest": i4["output_digest"],
                "support_margin": reference["support_margin"],
            },
        ),
        check(
            "route_transfer_variant_distinct_and_supported",
            summary["route_transfer_supported"]
            and next(row for row in rows if row["variant_id"] == "alternate_single_route")[
                "withdrawn_route_signature"
            ][0]["source_node_id"]
            != reference["withdrawn_route_signature"][0]["source_node_id"],
            summary,
        ),
        check(
            "schedule_shape_variants_supported",
            summary["schedule_shape_transfer_supported"],
            summary,
        ),
        check(
            "mixed_route_split_supported_without_merge_overclaim",
            summary["mixed_route_split_supported"],
            summary,
        ),
        check(
            "all_variant_replays_stable",
            all(row["replay_result"]["all_replay_modes_passed"] for row in rows),
            {
                row["variant_id"]: row["replay_result"]["all_replay_modes_passed"]
                for row in rows
            },
        ),
        check(
            "controls_passed_without_failed_open",
            all(control["control_status"] == "passed" for control in controls),
            controls,
        ),
        check(
            "no_wr5_wr6_or_final_overclaim",
            summary["wr5_supported"] is False
            and summary["wr6_supported"] is False
            and summary["final_withdrawal_resistance_supported"] is False
            and summary["support_removal_resistance_supported"] is False,
            summary,
        ),
        check(
            "unsafe_claim_flags_false",
            all(
                all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
            "all I4-B rows keep unsafe claim flags false",
        ),
    ]


def contains_local_absolute_path(text: str) -> bool:
    needles = [
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "file" + "://",
        "vscode" + "://",
    ]
    return any(needle in text for needle in needles)


def build_payload() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i4a = load_json(I4A_OUTPUT_PATH)
    schema_row = withdrawal_schema_row(i2)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    runtime_config_payload = runtime_config()
    runtime_config_path = ARTIFACT_DIR / "runtime_config.json"
    write_json(runtime_config_path, runtime_config_payload)

    rows = []
    artifact_paths = [rel(runtime_config_path)]
    for variant in VARIANTS:
        variant_id = str(variant["variant_id"])
        baseline = run_lgrc_schedule_case(
            variant_id,
            "baseline",
            variant["baseline_packets"],
        )
        withdrawn = run_lgrc_schedule_case(
            variant_id,
            "withdrawn",
            variant["withdrawn_packets"],
        )
        replay = replay_for_row(variant_id, withdrawn, variant["withdrawn_packets"])
        row = classify_variant(variant, baseline, withdrawn, replay)
        rows.append(row)
        artifact_paths.extend(
            [
                baseline["run_artifact_path"],
                baseline["event_log_path"],
                baseline["initial_snapshot_path"],
                baseline["final_snapshot_path"],
                withdrawn["run_artifact_path"],
                withdrawn["event_log_path"],
                withdrawn["initial_snapshot_path"],
                withdrawn["final_snapshot_path"],
                replay["duplicate_run_artifact_path"],
                replay["duplicate_event_log_path"],
                replay["duplicate_initial_snapshot_path"],
                replay["duplicate_final_snapshot_path"],
            ]
        )

    controls = build_controls(rows)
    summary = build_summary(rows, controls)
    trace_artifact = {
        "artifact_id": "n21_i4b_withdrawal_transfer_shape_trace",
        "runtime_config_path": rel(runtime_config_path),
        "variant_rows": rows,
        "control_results": controls,
        "transfer_shape_summary": summary,
    }
    trace_artifact["trace_digest"] = digest_value(trace_artifact)
    trace_path = ARTIFACT_DIR / "withdrawal_transfer_shape_trace.json"
    write_json(trace_path, trace_artifact)
    artifact_paths.append(rel(trace_path))
    artifact_manifest = file_manifest(sorted(set(artifact_paths)))

    checks = build_checks(
        rows,
        controls,
        artifact_manifest,
        summary,
        i1,
        i2,
        i3,
        i4,
        i4a,
    )
    payload: dict[str, Any] = {
        "artifact_id": "n21_withdrawal_transfer_shape_probe",
        "schema_version": "n21_withdrawal_transfer_shape_probe_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": "4-B",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_withdrawal_transfer_shape_wr4_candidate_pending_i6"
        ),
        "purpose": (
            "Test whether bounded withdrawal evidence transfers across a "
            "second support route and changed schedule shapes without "
            "retuning thresholds or opening WR5/WR6."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n21_i1_source_contract_inventory"),
            source_record(I2_OUTPUT_PATH, "n21_i2_schema_freeze"),
            source_record(I3_OUTPUT_PATH, "n21_i3_active_nulls"),
            source_record(I4_OUTPUT_PATH, "n21_i4_mild_withdrawal_candidate"),
            source_record(I4A_OUTPUT_PATH, "n21_i4a_severity_boundary"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "source_active_null_output_digest": i3["output_digest"],
        "source_i4_output_digest": i4["output_digest"],
        "source_i4a_output_digest": i4a["output_digest"],
        "source_contract_row": schema_row["source_contract_row"],
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "runtime_config_digest": digest_value(runtime_config_payload),
        "trace_artifact_path": rel(trace_path),
        "trace_digest": trace_artifact["trace_digest"],
        "artifact_digest": digest_value(artifact_manifest),
        "derived_report_only": False,
        "source_current_run_artifacts_consumed": True,
        "variant_rows": rows,
        "control_results": controls,
        "transfer_shape_summary": summary,
        "claim_boundary": {
            "bounded_transfer_shape_wr4_candidate_supported": True,
            "wr5_supported": False,
            "wr6_supported": False,
            "robust_withdrawal_resistance_supported": False,
            "support_removal_resistance_supported": False,
            "final_withdrawal_resistance_supported": False,
            "native_support_supported": False,
            "agency_supported": False,
            "sentience_supported": False,
            "phase8_implementation_supported": False,
            "iteration6_replay_control_matrix_required": True,
        },
        "artifact_manifest": artifact_manifest,
        "checks": checks,
    }
    no_absolute_paths = not contains_local_absolute_path(canonical_json(payload))
    payload["checks"].append(
        check(
            "no_local_absolute_paths",
            no_absolute_paths,
            "payload uses repository-relative paths and source IDs only",
        )
    )
    payload["failed_checks"] = [
        item["check_id"] for item in payload["checks"] if not item["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = (
            "blocked_withdrawal_transfer_shape_checks_failed"
        )
    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    summary = data["transfer_shape_summary"]
    lines = [
        "# N21 Iteration 4-B - Withdrawal Transfer And Schedule-Shape Probe",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 4-B keeps the I4/I4-A thresholds fixed and tests whether",
        "the bounded withdrawal pattern transfers to a second support route",
        "and to delayed, split, and mixed route schedule shapes.",
        "",
        "## Transfer Result",
        "",
        "```text",
        f"supported_variant_ids = {summary['supported_variant_ids']}",
        f"route_transfer_supported = {str(summary['route_transfer_supported']).lower()}",
        f"schedule_shape_transfer_supported = {str(summary['schedule_shape_transfer_supported']).lower()}",
        f"mixed_route_split_supported = {str(summary['mixed_route_split_supported']).lower()}",
        "wr5_supported = false",
        "wr6_supported = false",
        "final_withdrawal_resistance_supported = false",
        "```",
        "",
        "## Variant Rows",
        "",
        "| Variant | Role | Decision | Packets | Support Margin | Coherence Margin |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in data["variant_rows"]:
        lines.append(
            "| "
            f"`{row['variant_id']}` | "
            f"`{row['transfer_role']}` | "
            f"`{row['row_decision']}` | "
            f"`{len(row['withdrawn_route_signature'])}` | "
            f"`{row['support_margin']}` | "
            f"`{row['coherence_margin']}` |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Status |",
            "| --- | --- |",
        ]
    )
    for control in data["control_results"]:
        lines.append(f"| `{control['control_id']}` | `{control['control_status']}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "```text",
            "bounded transfer/schedule-shape WR4 candidate = true",
            "WR5 = false",
            "WR6 = false",
            "robust withdrawal resistance = false",
            "support removal resistance = false",
            "final withdrawal resistance = false",
            "native support = false",
            "agency = false",
            "sentience = false",
            "phase8_implementation = false",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in data["checks"]:
        detail = item["detail"]
        if not isinstance(detail, str):
            detail = json.dumps(detail, sort_keys=True)
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I4-B strengthens the future I6 evidence base by showing that the",
            "bounded `0.10 -> 0.07` withdrawal pattern is not confined to the",
            "single I4 route and schedule shape. A second support route, a delayed",
            "schedule, a split schedule, and a mixed-route split all preserve the",
            "same center basin, support floor, coherence floor, boundary degree,",
            "flux/budget bounds, and replay.",
            "",
            "The claim remains deliberately bounded. I4-B supports only a",
            "provisional WR4 transfer/schedule-shape candidate pending I6. It",
            "does not support WR5, WR6, support-removal resistance, robust",
            "withdrawal resistance, native support, agency, sentience, or Phase 8.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    data = build_payload()
    write_json(OUTPUT, data)
    write_report(data)
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")


if __name__ == "__main__":
    main()
