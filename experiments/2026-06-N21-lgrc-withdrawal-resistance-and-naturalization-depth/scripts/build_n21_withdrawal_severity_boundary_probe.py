#!/usr/bin/env python3
"""Build N21 Iteration 4-A withdrawal severity/removal boundary probe."""

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
OUTPUT = EXPERIMENT / "outputs" / "n21_withdrawal_severity_boundary_probe.json"
REPORT = EXPERIMENT / "reports" / "n21_withdrawal_severity_boundary_probe.md"
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n21_withdrawal_severity_boundary_probe_artifacts"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_withdrawal_severity_boundary_probe.py"
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

RUN_ID = "n21_i4a_withdrawal_severity_boundary_lgrc9v3"
BASELINE_PACKET_AMOUNT = 0.10
SEVERITY_AMOUNTS = [0.09, 0.07, 0.06, 0.05, 0.03, 0.00]
SUPPORT_PACKET_AMOUNT_FLOOR = 0.06
CENTER_COHERENCE_FLOOR = 10.05
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
MAX_BUDGET_ERROR = 1e-9
EPSILON = 1e-12


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


def amount_label(amount: float) -> str:
    return f"amount_{amount:.2f}".replace(".", "_")


def round_measure(value: float) -> float:
    return round(value, 12)


def withdrawal_schema_row(i2: dict[str, Any]) -> dict[str, Any]:
    for row in i2["schema_freeze"]["primitive_schema_rows"]:
        if row["primitive_id"] == "withdrawal_resistance":
            return row
    raise KeyError("withdrawal_resistance schema row not found")


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n21_i4a_withdrawal_severity_boundary_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "severity_amounts": SEVERITY_AMOUNTS,
        "support_surface": {
            "kind": "packetized_causal_flux_support_surface",
            "source_node_id": 1,
            "target_node_id": 0,
            "edge_id": 0,
            "baseline_packet_amount": BASELINE_PACKET_AMOUNT,
            "withdrawal_mode": "severity_sweep",
            "withdrawal_target": "support",
            "withdrawal_amounts": [
                round_measure(BASELINE_PACKET_AMOUNT - amount)
                for amount in SEVERITY_AMOUNTS
            ],
            "recovery_window": [1.0, 2.0],
            "floor_crossing_policy": "crossing_blocks_WR3_and_stronger",
        },
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


def run_geometry(model: LGRC9V3, packet_amount: float) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    source = state.base_state.nodes[1]
    ledger = state.packet_ledger
    assert ledger is not None
    packet_records = [record.to_record() for record in ledger.packet_records]
    event_records = [record.to_record() for record in ledger.packet_event_records]
    final_geometry = {
        "center_node_id": 0,
        "support_source_node_id": 1,
        "support_edge_id": 0,
        "declared_support_packet_amount": packet_amount,
        "center_node_coherence": center.coherence,
        "source_node_coherence": source.coherence,
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


def run_lgrc_case(run_role: str, packet_amount: float) -> dict[str, Any]:
    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    initial_geometry = run_geometry(model, packet_amount=0.0)
    initial_snapshot_path = ARTIFACT_DIR / f"{run_role}_initial_snapshot.json"
    model.save(str(initial_snapshot_path))

    if packet_amount > 0.0:
        model.schedule_packet_departure(
            source_node_id=1,
            target_node_id=0,
            edge_id=0,
            amount=packet_amount,
            departure_event_time_key=1.0,
            scheduler_event_index=1,
        )

    step_results = []
    event_rows = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_results.append(result)
        event_rows.extend(event_to_record(event, run_role) for event in result.events)

    event_counts = dict(Counter(row["kind"] for row in event_rows))
    final_snapshot_path = ARTIFACT_DIR / f"{run_role}_final_snapshot.json"
    model.save(str(final_snapshot_path))
    event_log_path = ARTIFACT_DIR / f"{run_role}_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    run_artifact = {
        "artifact_id": f"n21_i4a_{run_role}_lgrc9v3_support_run",
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "declared_packet_support_surface_severity_sweep",
        "runtime_config_digest": digest_value(runtime_config()),
        "support_packet_amount": packet_amount,
        "source_current_inputs_emitted": True,
        "derived_report_only": False,
        "initial_snapshot_path": rel(initial_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "initial_geometry": initial_geometry,
        "final_geometry": run_geometry(model, packet_amount=packet_amount),
        "step_summaries": [step_summary(result) for result in step_results],
        "event_counts_by_kind": event_counts,
        "final_observables": dict(model.compute_observables()),
        "source_current_trace": {
            "support_packet_departure_and_arrival_present": packet_amount > 0.0,
            "center_node_coherence_after": model.get_state().base_state.nodes[
                0
            ].coherence,
            "source_node_coherence_after": model.get_state().base_state.nodes[
                1
            ].coherence,
            "packet_budget_error": model.get_state().packet_ledger.budget_error,
            "fixed_topology_signature": topology_signature(model.get_state()),
        },
    }
    run_artifact_path = ARTIFACT_DIR / f"{run_role}_run.json"
    write_json(run_artifact_path, run_artifact)
    return {
        "run_role": run_role,
        "model": model,
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_artifact_path),
        "event_log_path": rel(event_log_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "initial_snapshot_path": rel(initial_snapshot_path),
    }


def replay_snapshot_geometry(snapshot_path: str, packet_amount: float) -> dict[str, Any]:
    model = LGRC9V3.load(str(ROOT / snapshot_path))
    return run_geometry(model, packet_amount=packet_amount)


def file_manifest(paths: list[str]) -> list[dict[str, str]]:
    return [{"path": path, "sha256": sha256_file(path)} for path in sorted(paths)]


def same_basin_comparison(baseline: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    baseline_geometry = baseline["run_artifact"]["final_geometry"]
    row_geometry = row["run_artifact"]["final_geometry"]
    comparison = {
        "center_node_id_same": baseline_geometry["center_node_id"]
        == row_geometry["center_node_id"],
        "center_basin_id_same": baseline_geometry["basin_signature"][
            "center_basin_id"
        ]
        == row_geometry["basin_signature"]["center_basin_id"],
        "topology_signature_same": baseline_geometry["topology_signature"]
        == row_geometry["topology_signature"],
        "active_degree_same": baseline_geometry["active_degree"]
        == row_geometry["active_degree"],
        "basin_member_count_same": len(
            baseline_geometry["basin_signature"]["basin_members"]
        )
        == len(row_geometry["basin_signature"]["basin_members"]),
    }
    comparison["all_same_basin_signature_fields_preserved"] = all(
        comparison.values()
    )
    return comparison


def replay_for_row(row_run: dict[str, Any], amount: float) -> dict[str, Any]:
    snapshot_geometry = replay_snapshot_geometry(row_run["final_snapshot_path"], amount)
    duplicate = run_lgrc_case(f"{row_run['run_role']}_duplicate", amount)
    original_geometry = row_run["run_artifact"]["final_geometry"]
    duplicate_geometry = duplicate["run_artifact"]["final_geometry"]
    replay = {
        "source_run_artifact_path": row_run["run_artifact_path"],
        "source_final_snapshot_path": row_run["final_snapshot_path"],
        "duplicate_run_artifact_path": duplicate["run_artifact_path"],
        "duplicate_event_log_path": duplicate["event_log_path"],
        "duplicate_initial_snapshot_path": duplicate["initial_snapshot_path"],
        "duplicate_final_snapshot_path": duplicate["final_snapshot_path"],
        "artifact_replay": {
            "status": "passed",
            "artifact_path_exists": True,
            "source_run_artifact_digest": sha256_file(row_run["run_artifact_path"]),
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


def classify_severity_row(
    amount: float,
    baseline: dict[str, Any],
    row_run: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    geometry = row_run["run_artifact"]["final_geometry"]
    support_margin = round_measure(amount - SUPPORT_PACKET_AMOUNT_FLOOR)
    coherence_margin = round_measure(
        geometry["center_node_coherence"] - CENTER_COHERENCE_FLOOR
    )
    support_status = (
        "preserved"
        if amount + EPSILON >= SUPPORT_PACKET_AMOUNT_FLOOR
        else "crossed_floor"
    )
    coherence_status = (
        "preserved"
        if geometry["center_node_coherence"] + EPSILON >= CENTER_COHERENCE_FLOOR
        else "crossed_floor"
    )
    boundary_status = (
        "preserved"
        if geometry["active_degree"] >= BOUNDARY_ACTIVE_DEGREE_FLOOR
        and geometry["topology_signature"]
        == baseline["run_artifact"]["final_geometry"]["topology_signature"]
        else "missing"
    )
    flux_status = (
        "preserved"
        if abs(geometry["budget_error"]) <= MAX_BUDGET_ERROR
        and geometry["in_flight_packet_total"] == 0.0
        else "exceeded_bound"
    )
    same_basin = same_basin_comparison(baseline, row_run)
    gate_statuses = {
        "support_floor_result": support_status,
        "coherence_floor_result": coherence_status,
        "boundary_integrity_result": boundary_status,
        "flux_or_leakage_result": flux_status,
    }
    all_gates_preserved = (
        same_basin["all_same_basin_signature_fields_preserved"]
        and support_status == "preserved"
        and coherence_status == "preserved"
        and boundary_status == "preserved"
        and flux_status == "preserved"
        and replay["all_replay_modes_passed"]
    )
    if all_gates_preserved and support_margin > 0.0:
        row_decision = "supported"
        primitive_claim_allowed = True
        wr_ladder_rung = "WR4"
        severity_role = "positive_margin_withdrawal_candidate"
    elif all_gates_preserved and support_margin == 0.0:
        row_decision = "partial"
        primitive_claim_allowed = False
        wr_ladder_rung = "WR3_floor_boundary_partial"
        severity_role = "floor_boundary_zero_margin"
    else:
        row_decision = "rejected"
        primitive_claim_allowed = False
        wr_ladder_rung = None
        severity_role = "fail_closed_boundary_row"

    failure_modes = []
    if support_status != "preserved":
        failure_modes.append("support_floor_crossed")
    if coherence_status != "preserved":
        failure_modes.append("coherence_floor_crossed")
    if boundary_status != "preserved":
        failure_modes.append("boundary_integrity_not_preserved")
    if flux_status != "preserved":
        failure_modes.append("flux_or_budget_bound_exceeded")
    if not same_basin["all_same_basin_signature_fields_preserved"]:
        failure_modes.append("same_basin_signature_not_preserved")
    if not replay["all_replay_modes_passed"]:
        failure_modes.append("replay_not_stable")

    row = {
        "row_id": f"n21_i4a_row_{amount_label(amount)}",
        "primitive_id": "withdrawal_resistance",
        "support_packet_amount": amount,
        "withdrawal_amount": round_measure(BASELINE_PACKET_AMOUNT - amount),
        "support_retention_ratio": round_measure(amount / BASELINE_PACKET_AMOUNT),
        "support_margin": support_margin,
        "center_coherence": geometry["center_node_coherence"],
        "coherence_margin": coherence_margin,
        "active_degree": geometry["active_degree"],
        "budget_error": geometry["budget_error"],
        "in_flight_packet_total": geometry["in_flight_packet_total"],
        "event_count": sum(row_run["run_artifact"]["event_counts_by_kind"].values()),
        "packet_count": geometry["packet_count"],
        "same_basin_comparison": same_basin,
        "gate_statuses": gate_statuses,
        "replay_result": replay,
        "row_decision": row_decision,
        "primitive_claim_allowed": primitive_claim_allowed,
        "wr_ladder_rung": wr_ladder_rung,
        "wr_ladder_rung_status": (
            "provisional_pending_iteration6_control_matrix"
            if row_decision == "supported"
            else "not_positive_candidate"
        ),
        "severity_role": severity_role,
        "failure_modes": failure_modes,
        "claim_ceiling": (
            "bounded support-weakening evidence only; no support-removal "
            "resistance, robust withdrawal resistance, native support, agency, "
            "sentience, or Phase 8 claim"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "run_artifact_path": row_run["run_artifact_path"],
        "event_log_path": row_run["event_log_path"],
        "final_snapshot_path": row_run["final_snapshot_path"],
    }
    row["row_digest"] = digest_value(row)
    return row


def support_relevance_control(
    baseline: dict[str, Any],
    removal: dict[str, Any],
) -> dict[str, Any]:
    baseline_geometry = baseline["run_artifact"]["final_geometry"]
    removal_geometry = removal["run_artifact"]["final_geometry"]
    center_delta = round_measure(
        baseline_geometry["center_node_coherence"]
        - removal_geometry["center_node_coherence"]
    )
    source_delta = round_measure(
        removal_geometry["source_node_coherence"]
        - baseline_geometry["source_node_coherence"]
    )
    packet_count_delta = (
        baseline_geometry["packet_count"] - removal_geometry["packet_count"]
    )
    event_count_delta = sum(baseline["run_artifact"]["event_counts_by_kind"].values()) - sum(
        removal["run_artifact"]["event_counts_by_kind"].values()
    )
    control_passed = (
        abs(center_delta) >= 0.05
        and packet_count_delta > 0
        and event_count_delta > 0
    )
    return {
        "control_id": "support_necessity_or_relevance_control",
        "control_status": "passed" if control_passed else "failed_open",
        "blocked_condition": (
            "support surface can be changed or removed with no measurable "
            "source-current geometric effect"
        ),
        "expected_result": (
            "support removal changes coherence, packet records, and event trace"
        ),
        "actual_result": {
            "baseline_packet_amount": BASELINE_PACKET_AMOUNT,
            "removal_packet_amount": 0.0,
            "center_coherence_delta": center_delta,
            "source_coherence_delta": source_delta,
            "packet_count_delta": packet_count_delta,
            "event_count_delta": event_count_delta,
        },
        "claim_allowed_when_control_triggers": False,
        "rung_effect": (
            "demotes positive rows to same-basin invariance under irrelevant "
            "support perturbation if triggered"
        ),
    }


def build_boundary_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    supported = [row for row in rows if row["row_decision"] == "supported"]
    partial = [row for row in rows if row["row_decision"] == "partial"]
    rejected = [row for row in rows if row["row_decision"] == "rejected"]
    min_supported_amount = min(row["support_packet_amount"] for row in supported)
    max_supported_withdrawal = round_measure(
        BASELINE_PACKET_AMOUNT - min_supported_amount
    )
    removal_row = next(row for row in rows if row["support_packet_amount"] == 0.0)
    first_rejected_below_floor = max(
        row["support_packet_amount"]
        for row in rejected
        if row["support_packet_amount"] < SUPPORT_PACKET_AMOUNT_FLOOR
    )
    summary = {
        "supported_positive_margin_amounts": [
            row["support_packet_amount"] for row in supported
        ],
        "floor_boundary_amounts": [row["support_packet_amount"] for row in partial],
        "fail_closed_amounts": [row["support_packet_amount"] for row in rejected],
        "min_positive_margin_supported_packet_amount": min_supported_amount,
        "max_positive_margin_supported_withdrawal_amount": max_supported_withdrawal,
        "floor_boundary_packet_amount": partial[0]["support_packet_amount"]
        if partial
        else None,
        "failure_boundary_interval": [
            SUPPORT_PACKET_AMOUNT_FLOOR,
            first_rejected_below_floor,
        ],
        "full_removal_status": removal_row["row_decision"],
        "full_removal_failure_modes": removal_row["failure_modes"],
        "support_removal_resistance_supported": False,
        "robust_withdrawal_resistance_supported": False,
        "bounded_support_weakening_scope_supported": True,
        "severity_boundary_interpretation": (
            "I4 survives one mild weakening. I4-A maps the local boundary: "
            "positive-margin rows above the 0.06 floor support bounded "
            "weakening, the exact floor row is zero-margin partial, and rows "
            "below the floor fail closed. Full removal is rejected."
        ),
    }
    summary["boundary_summary_digest"] = digest_value(summary)
    return summary


def build_checks(
    rows: list[dict[str, Any]],
    artifact_manifest: list[dict[str, str]],
    support_control: dict[str, Any],
    i1: dict[str, Any],
    i2: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    boundary_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    amounts = [row["support_packet_amount"] for row in rows]
    i4_row = next(row for row in rows if row["support_packet_amount"] == 0.07)
    return [
        check(
            "source_i1_i2_i3_i4_passed",
            all(
                source["status"] == "passed" and not source["failed_checks"]
                for source in [i1, i2, i3, i4]
            ),
            {
                "i1": i1["acceptance_state"],
                "i2": i2["acceptance_state"],
                "i3": i3["acceptance_state"],
                "i4": i4["acceptance_state"],
            },
        ),
        check(
            "severity_amounts_match_plan",
            amounts == SEVERITY_AMOUNTS,
            {"expected": SEVERITY_AMOUNTS, "actual": amounts},
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
            "i4_row_reproduced",
            i4_row["row_decision"] == "supported"
            and i4_row["support_packet_amount"] == 0.07
            and i4_row["support_margin"] == 0.01
            and i4_row["gate_statuses"]["support_floor_result"] == "preserved",
            {
                "row_decision": i4_row["row_decision"],
                "support_packet_amount": i4_row["support_packet_amount"],
                "support_margin": i4_row["support_margin"],
                "source_i4_output_digest": i4["output_digest"],
            },
        ),
        check(
            "support_relevance_control_passed",
            support_control["control_status"] == "passed",
            support_control,
        ),
        check(
            "positive_boundary_and_fail_closed_rows_present",
            boundary_summary["supported_positive_margin_amounts"] == [0.09, 0.07]
            and boundary_summary["floor_boundary_amounts"] == [0.06]
            and boundary_summary["fail_closed_amounts"] == [0.05, 0.03, 0.0],
            boundary_summary,
        ),
        check(
            "full_removal_rejected_no_removal_overclaim",
            boundary_summary["full_removal_status"] == "rejected"
            and not boundary_summary["support_removal_resistance_supported"]
            and not boundary_summary["robust_withdrawal_resistance_supported"],
            boundary_summary,
        ),
        check(
            "all_replays_stable",
            all(row["replay_result"]["all_replay_modes_passed"] for row in rows),
            {
                row["row_id"]: row["replay_result"]["all_replay_modes_passed"]
                for row in rows
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(
                all(value is False for value in row["unsafe_claim_flags"].values())
                for row in rows
            ),
            "all severity rows keep unsafe claim flags false",
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
    schema_row = withdrawal_schema_row(i2)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    runtime_config_payload = runtime_config()
    runtime_config_path = ARTIFACT_DIR / "runtime_config.json"
    write_json(runtime_config_path, runtime_config_payload)

    baseline = run_lgrc_case("baseline_amount_0_10", BASELINE_PACKET_AMOUNT)
    severity_rows = []
    severity_runs = {}
    replay_artifacts = {}
    artifact_paths = [
        rel(runtime_config_path),
        baseline["run_artifact_path"],
        baseline["event_log_path"],
        baseline["initial_snapshot_path"],
        baseline["final_snapshot_path"],
    ]
    for amount in SEVERITY_AMOUNTS:
        label = amount_label(amount)
        run = run_lgrc_case(label, amount)
        severity_runs[label] = run
        replay = replay_for_row(run, amount)
        replay_artifacts[label] = replay
        row = classify_severity_row(amount, baseline, run, replay)
        severity_rows.append(row)
        artifact_paths.extend(
            [
                run["run_artifact_path"],
                run["event_log_path"],
                run["initial_snapshot_path"],
                run["final_snapshot_path"],
                replay["duplicate_run_artifact_path"],
                replay["duplicate_event_log_path"],
                replay["duplicate_initial_snapshot_path"],
                replay["duplicate_final_snapshot_path"],
            ]
        )

    support_control = support_relevance_control(
        baseline,
        severity_runs[amount_label(0.0)],
    )
    boundary_summary = build_boundary_summary(severity_rows)
    trace_artifact = {
        "artifact_id": "n21_i4a_withdrawal_severity_boundary_trace",
        "runtime_config_path": rel(runtime_config_path),
        "baseline_run_artifact_path": baseline["run_artifact_path"],
        "severity_rows": severity_rows,
        "support_necessity_or_relevance_control": support_control,
        "boundary_summary": boundary_summary,
    }
    trace_artifact["trace_digest"] = digest_value(trace_artifact)
    trace_path = ARTIFACT_DIR / "withdrawal_severity_boundary_trace.json"
    write_json(trace_path, trace_artifact)
    artifact_paths.append(rel(trace_path))
    artifact_manifest = file_manifest(sorted(set(artifact_paths)))

    checks = build_checks(
        severity_rows,
        artifact_manifest,
        support_control,
        i1,
        i2,
        i3,
        i4,
        boundary_summary,
    )
    payload: dict[str, Any] = {
        "artifact_id": "n21_withdrawal_severity_boundary_probe",
        "schema_version": "n21_withdrawal_severity_boundary_probe_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": "4-A",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_withdrawal_severity_boundary_mapped_no_removal_overclaim"
        ),
        "purpose": (
            "Map how far the declared LGRC9V3 packetized support surface can "
            "be weakened or removed before same-basin continuation fails closed."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n21_i1_source_contract_inventory"),
            source_record(I2_OUTPUT_PATH, "n21_i2_schema_freeze"),
            source_record(I3_OUTPUT_PATH, "n21_i3_active_nulls"),
            source_record(I4_OUTPUT_PATH, "n21_i4_mild_withdrawal_candidate"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "source_active_null_output_digest": i3["output_digest"],
        "source_i4_output_digest": i4["output_digest"],
        "source_contract_row": schema_row["source_contract_row"],
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "runtime_config_digest": digest_value(runtime_config_payload),
        "trace_artifact_path": rel(trace_path),
        "trace_digest": trace_artifact["trace_digest"],
        "artifact_digest": digest_value(artifact_manifest),
        "derived_report_only": False,
        "source_current_run_artifacts_consumed": True,
        "severity_rows": severity_rows,
        "boundary_summary": boundary_summary,
        "support_necessity_or_relevance_control": support_control,
        "claim_boundary": {
            "bounded_support_weakening_scope_supported": True,
            "support_removal_resistance_supported": False,
            "robust_withdrawal_resistance_supported": False,
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
            "blocked_withdrawal_severity_boundary_checks_failed"
        )
    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    summary = data["boundary_summary"]
    control = data["support_necessity_or_relevance_control"]
    lines = [
        "# N21 Iteration 4-A - Withdrawal Severity And Removal Boundary Probe",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 4-A keeps the I4 producer family fixed and sweeps the",
        "declared packetized support surface across mild weakening, floor,",
        "below-floor, strong-withdrawal, and full-removal rows.",
        "",
        "## Boundary Result",
        "",
        "```text",
        f"supported_positive_margin_amounts = {summary['supported_positive_margin_amounts']}",
        f"floor_boundary_amounts = {summary['floor_boundary_amounts']}",
        f"fail_closed_amounts = {summary['fail_closed_amounts']}",
        f"max_positive_margin_supported_withdrawal_amount = {summary['max_positive_margin_supported_withdrawal_amount']}",
        f"failure_boundary_interval = {summary['failure_boundary_interval']}",
        f"full_removal_status = {summary['full_removal_status']}",
        "support_removal_resistance_supported = false",
        "robust_withdrawal_resistance_supported = false",
        "```",
        "",
        "## Severity Rows",
        "",
        "| Packet Amount | Withdrawal | Decision | Role | Failure Modes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in data["severity_rows"]:
        failures = ", ".join(row["failure_modes"]) if row["failure_modes"] else "none"
        lines.append(
            "| "
            f"`{row['support_packet_amount']}` | "
            f"`{row['withdrawal_amount']}` | "
            f"`{row['row_decision']}` | "
            f"`{row['severity_role']}` | "
            f"`{failures}` |"
        )
    lines.extend(
        [
            "",
            "## Support Relevance Control",
            "",
            "```text",
            f"control_status = {control['control_status']}",
            f"center_coherence_delta = {control['actual_result']['center_coherence_delta']}",
            f"source_coherence_delta = {control['actual_result']['source_coherence_delta']}",
            f"packet_count_delta = {control['actual_result']['packet_count_delta']}",
            f"event_count_delta = {control['actual_result']['event_count_delta']}",
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "bounded support-weakening scope = supported",
            "support removal resistance = false",
            "robust withdrawal resistance = false",
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
            "I4-A does not invalidate I4. It sharpens its scope. Geometrically,",
            "the same center basin survives positive-margin weakening at `0.09`",
            "and `0.07`, reaches a zero-margin floor boundary at `0.06`, and",
            "fails closed below the declared support floor at `0.05`, `0.03`,",
            "and `0.00`. The full-removal row is rejected, so the supported",
            "claim remains bounded support weakening, not support-removal",
            "resistance or broad withdrawal resistance.",
            "",
            "The support-relevance control also passes: removing the support",
            "surface changes source-current coherence, packet records, and event",
            "trace. That prevents the positive rows from being dismissed as",
            "same-basin invariance under an irrelevant support perturbation.",
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
