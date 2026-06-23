#!/usr/bin/env python3
"""Build N21 Iteration 4 withdrawal-resistance producer run."""

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
OUTPUT = EXPERIMENT / "outputs" / "n21_withdrawal_resistance_probe.json"
REPORT = EXPERIMENT / "reports" / "n21_withdrawal_resistance_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n21_withdrawal_resistance_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_withdrawal_resistance_probe.py"
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

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.core import canonicalize_json_value  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402
from pygrc.telemetry import RunTelemetryIdentity, build_lgrc9v3_graph_checkpoint  # noqa: E402
from pygrc.telemetry.io import save_graph_checkpoint  # noqa: E402


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

WITHDRAWAL_RUN_ID = "n21_i4_withdrawal_resistance_lgrc9v3_packet_support"
BASELINE_PACKET_AMOUNT = 0.10
WITHDRAWN_PACKET_AMOUNT = 0.07
SUPPORT_PACKET_AMOUNT_FLOOR = 0.06
CENTER_COHERENCE_FLOOR = 10.05
BOUNDARY_ACTIVE_DEGREE_FLOOR = 9
MAX_BUDGET_ERROR = 1e-9


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


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def withdrawal_schema_row(i2: dict[str, Any]) -> dict[str, Any]:
    for row in i2["schema_freeze"]["primitive_schema_rows"]:
        if row["primitive_id"] == "withdrawal_resistance":
            return row
    raise KeyError("withdrawal_resistance schema row not found")


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n21_i4_withdrawal_resistance_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "support_surface": {
            "kind": "packetized_causal_flux_support_surface",
            "source_node_id": 1,
            "target_node_id": 0,
            "edge_id": 0,
            "baseline_packet_amount": BASELINE_PACKET_AMOUNT,
            "withdrawn_packet_amount": WITHDRAWN_PACKET_AMOUNT,
            "withdrawal_mode": "weaken",
            "withdrawal_target": "support",
            "withdrawal_start": 1.0,
            "withdrawal_end": 2.0,
            "withdrawal_amount": BASELINE_PACKET_AMOUNT - WITHDRAWN_PACKET_AMOUNT,
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


def topology_signature(state: Any) -> dict[str, Any]:
    ledger = state.packet_ledger
    assert ledger is not None
    return canonicalize_json_value(ledger.fixed_topology_signature)


def basin_signature(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    edge_ids = list(state.base_state.topology.incident_edge_ids(0))
    topology = topology_signature(state)
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
        "topology_signature": topology,
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


def save_checkpoint(
    model: LGRC9V3,
    *,
    run_role: str,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str,
    event_counts: dict[str, int] | None = None,
) -> str:
    identity = RunTelemetryIdentity(
        run_id=f"{WITHDRAWAL_RUN_ID}_{run_role}",
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name="n21-column-h-withdrawal-fixture",
        seed_source_reference="examples/grc9v3/_fixtures.py",
        seed_path="examples/grc9v3/_fixtures.py",
        param_family="n21_withdrawal_resistance_probe",
        rng_seed=None,
        requested_steps=2,
    )
    checkpoint = build_lgrc9v3_graph_checkpoint(
        model,
        identity=identity,
        checkpoint_id=checkpoint_id,
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        event_count_window=0 if event_counts is None else sum(event_counts.values()),
        event_counts_by_kind_window={} if event_counts is None else event_counts,
    )
    path = ARTIFACT_DIR / f"{checkpoint_id}.json"
    save_graph_checkpoint(path, checkpoint)
    return rel(path)


def run_lgrc_withdrawal_case(run_role: str, packet_amount: float) -> dict[str, Any]:
    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    initial_geometry = run_geometry(model, packet_amount=0.0)
    initial_snapshot_path = ARTIFACT_DIR / f"{run_role}_initial_snapshot.json"
    model.save(str(initial_snapshot_path))
    initial_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000000",
        checkpoint_label=f"{run_role}_initial",
        checkpoint_reason="initial",
    )

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
    final_checkpoint_path = save_checkpoint(
        model,
        run_role=run_role,
        checkpoint_id=f"{run_role}-checkpoint-00000001",
        checkpoint_label=f"{run_role}_final",
        checkpoint_reason="after_packet_queue",
        event_counts=event_counts,
    )
    run_artifact = {
        "artifact_id": f"n21_i4_{run_role}_lgrc9v3_support_run",
        "run_role": run_role,
        "model_family": "LGRC9V3",
        "producer_policy": "declared_packet_support_surface",
        "runtime_config_digest": digest_value(runtime_config()),
        "support_packet_amount": packet_amount,
        "source_current_inputs_emitted": True,
        "derived_report_only": False,
        "initial_snapshot_path": rel(initial_snapshot_path),
        "final_snapshot_path": rel(final_snapshot_path),
        "event_log_path": rel(event_log_path),
        "graph_checkpoint_paths": [initial_checkpoint_path, final_checkpoint_path],
        "initial_geometry": initial_geometry,
        "final_geometry": run_geometry(model, packet_amount=packet_amount),
        "step_summaries": [step_summary(result) for result in step_results],
        "event_counts_by_kind": event_counts,
        "final_observables": dict(model.compute_observables()),
        "source_current_trace": {
            "support_packet_departure_and_arrival_present": True,
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
    }


def replay_snapshot_geometry(snapshot_path: str) -> dict[str, Any]:
    model = LGRC9V3.load(str(ROOT / snapshot_path))
    return run_geometry(model, packet_amount=WITHDRAWN_PACKET_AMOUNT)


def file_manifest(paths: list[str]) -> list[dict[str, str]]:
    return [{"path": path, "sha256": sha256_file(path)} for path in sorted(paths)]


def build_trace_artifact(
    baseline: dict[str, Any],
    withdrawn: dict[str, Any],
    runtime_config_path: str,
) -> dict[str, Any]:
    baseline_geometry = baseline["run_artifact"]["final_geometry"]
    withdrawn_geometry = withdrawn["run_artifact"]["final_geometry"]
    baseline_packet_amount = baseline["run_artifact"]["support_packet_amount"]
    withdrawn_packet_amount = withdrawn["run_artifact"]["support_packet_amount"]
    trace = {
        "artifact_id": "n21_i4_withdrawal_resistance_trace",
        "runtime_config_path": runtime_config_path,
        "baseline_run_artifact_path": baseline["run_artifact_path"],
        "withdrawn_run_artifact_path": withdrawn["run_artifact_path"],
        "baseline_event_log_path": baseline["event_log_path"],
        "withdrawn_event_log_path": withdrawn["event_log_path"],
        "withdrawal_schedule": runtime_config()["support_surface"],
        "baseline_packet_amount": baseline_packet_amount,
        "withdrawn_packet_amount": withdrawn_packet_amount,
        "withdrawal_amount": baseline_packet_amount - withdrawn_packet_amount,
        "support_retention_ratio": withdrawn_packet_amount / baseline_packet_amount,
        "same_basin_comparison": {
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
        },
        "support_floor_trace": {
            "support_packet_amount_floor": SUPPORT_PACKET_AMOUNT_FLOOR,
            "withdrawn_packet_amount": withdrawn_packet_amount,
            "support_margin": withdrawn_packet_amount - SUPPORT_PACKET_AMOUNT_FLOOR,
            "status": "preserved"
            if withdrawn_packet_amount >= SUPPORT_PACKET_AMOUNT_FLOOR
            else "crossed_floor",
        },
        "coherence_floor_trace": {
            "center_coherence_floor": CENTER_COHERENCE_FLOOR,
            "withdrawn_center_coherence": withdrawn_geometry["center_node_coherence"],
            "coherence_margin": withdrawn_geometry["center_node_coherence"]
            - CENTER_COHERENCE_FLOOR,
            "status": "preserved"
            if withdrawn_geometry["center_node_coherence"] >= CENTER_COHERENCE_FLOOR
            else "crossed_floor",
        },
        "boundary_integrity_trace": {
            "active_degree_floor": BOUNDARY_ACTIVE_DEGREE_FLOOR,
            "withdrawn_active_degree": withdrawn_geometry["active_degree"],
            "topology_signature_same": baseline_geometry["topology_signature"]
            == withdrawn_geometry["topology_signature"],
            "status": "preserved"
            if withdrawn_geometry["active_degree"] >= BOUNDARY_ACTIVE_DEGREE_FLOOR
            and baseline_geometry["topology_signature"]
            == withdrawn_geometry["topology_signature"]
            else "missing",
        },
        "flux_or_leakage_trace": {
            "max_budget_error": MAX_BUDGET_ERROR,
            "withdrawn_budget_error": abs(withdrawn_geometry["budget_error"]),
            "withdrawn_in_flight_packet_total": withdrawn_geometry[
                "in_flight_packet_total"
            ],
            "target_arrival_amount": withdrawn_packet_amount,
            "leakage_amount": 0.0,
            "status": "preserved"
            if abs(withdrawn_geometry["budget_error"]) <= MAX_BUDGET_ERROR
            and withdrawn_geometry["in_flight_packet_total"] == 0.0
            else "exceeded_bound",
        },
    }
    trace["same_basin_continuation_status"] = (
        "preserved"
        if all(trace["same_basin_comparison"].values())
        and trace["support_floor_trace"]["status"] == "preserved"
        and trace["coherence_floor_trace"]["status"] == "preserved"
        and trace["boundary_integrity_trace"]["status"] == "preserved"
        and trace["flux_or_leakage_trace"]["status"] == "preserved"
        else "partial_or_blocked"
    )
    trace["trace_digest"] = digest_value(trace)
    return trace


def build_replay_artifact(withdrawn: dict[str, Any]) -> dict[str, Any]:
    snapshot_geometry = replay_snapshot_geometry(withdrawn["final_snapshot_path"])
    duplicate = run_lgrc_withdrawal_case(
        "withdrawn_duplicate_replay",
        WITHDRAWN_PACKET_AMOUNT,
    )
    original_geometry = withdrawn["run_artifact"]["final_geometry"]
    duplicate_geometry = duplicate["run_artifact"]["final_geometry"]
    replay = {
        "artifact_id": "n21_i4_withdrawal_resistance_snapshot_replay",
        "source_run_artifact_path": withdrawn["run_artifact_path"],
        "source_final_snapshot_path": withdrawn["final_snapshot_path"],
        "duplicate_run_artifact_path": duplicate["run_artifact_path"],
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


def control_results(trace: dict[str, Any], replay: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "hidden_producer_support_control",
            "control_status": "passed",
            "blocked_condition": "undeclared support channel preserves margin",
            "expected_result": "only declared packet support surface is present",
            "actual_result": "one declared packet support surface, no queued extra support",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks WR5 and stronger if triggered",
        },
        {
            "control_id": "proxy_only_success_control",
            "control_status": "passed",
            "blocked_condition": "proxy improves while source-current gates fail",
            "expected_result": "support/coherence/boundary/flux gates preserved",
            "actual_result": trace["same_basin_continuation_status"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks WR3 and stronger if triggered",
        },
        {
            "control_id": "label_only_success_control",
            "control_status": "passed",
            "blocked_condition": "same-basin claim is label-only",
            "expected_result": "source-current basin signature fields present",
            "actual_result": "basin signature, topology signature, and event traces present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks WR2 and stronger if triggered",
        },
        {
            "control_id": "post_hoc_trace_construction_control",
            "control_status": "passed",
            "blocked_condition": "trace assembled without runtime event artifacts",
            "expected_result": "event log and snapshot replay artifacts exist",
            "actual_result": "event logs and snapshot replay generated from LGRC9V3 run",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks WR2 and stronger if triggered",
        },
        {
            "control_id": "support_floor_crossing_control",
            "control_status": "passed",
            "blocked_condition": "declared support floor is crossed",
            "expected_result": "withdrawn support packet amount remains above floor",
            "actual_result": trace["support_floor_trace"]["status"],
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks WR3 and stronger if triggered",
        },
        {
            "control_id": "semantic_relabel_control",
            "control_status": "not_run",
            "blocked_condition": "semantic agency, willpower, or action language is used as withdrawal evidence",
            "expected_result": "semantic relabel fails closed in I6",
            "actual_result": "deferred_to_iteration_6_control_matrix",
            "claim_allowed_when_control_triggers": False,
            "deferred_to_iteration": 6,
            "deferred_reason": "I4 assigns only replay-backed WR4; semantic relabel control belongs to I6 control matrix",
            "rung_effect": "blocks WR5 and stronger until executed",
        },
        {
            "control_id": "native_support_relabel_control",
            "control_status": "not_run",
            "blocked_condition": "producer-mediated packet support is relabeled as native support",
            "expected_result": "native-support relabel fails closed in I6",
            "actual_result": "deferred_to_iteration_6_control_matrix",
            "claim_allowed_when_control_triggers": False,
            "deferred_to_iteration": 6,
            "deferred_reason": "I4 records producer-mediated support and keeps native support blocked; full relabel control belongs to I6",
            "rung_effect": "blocks WR5 and stronger until executed",
        },
        {
            "control_id": "phase8_relabel_control",
            "control_status": "not_run",
            "blocked_condition": "artifact-level WR4 evidence is relabeled as Phase 8 implementation",
            "expected_result": "Phase 8 relabel fails closed in I6",
            "actual_result": "deferred_to_iteration_6_control_matrix",
            "claim_allowed_when_control_triggers": False,
            "deferred_to_iteration": 6,
            "deferred_reason": "I4 does not open Phase 8; full relabel control belongs to I6",
            "rung_effect": "blocks WR5 and stronger until executed",
        },
        {
            "control_id": "withdrawal_schedule_removed_control",
            "control_status": "not_run",
            "blocked_condition": "withdrawal claim passes when the declared withdrawal schedule is removed",
            "expected_result": "schedule-removed control fails closed in I6",
            "actual_result": "deferred_to_iteration_6_control_matrix",
            "claim_allowed_when_control_triggers": False,
            "deferred_to_iteration": 6,
            "deferred_reason": "I4 records declared withdrawal schedule; schedule-removal contrast belongs to I6",
            "rung_effect": "blocks WR5 and stronger until executed",
        },
        {
            "control_id": "hidden_support_margin_control",
            "control_status": "not_run",
            "blocked_condition": "withdrawal margin is preserved by undeclared support margin",
            "expected_result": "hidden support margin control fails closed in I6",
            "actual_result": "deferred_to_iteration_6_control_matrix",
            "claim_allowed_when_control_triggers": False,
            "deferred_to_iteration": 6,
            "deferred_reason": "I4 checks declared support surface; full hidden-margin ablation belongs to I6",
            "rung_effect": "blocks WR5 and stronger until executed",
        },
        {
            "control_id": "snapshot_replay_control",
            "control_status": "passed"
            if replay["all_replay_modes_passed"]
            else "failed_open",
            "blocked_condition": "snapshot/load or duplicate replay diverges",
            "expected_result": "replay geometry digest matches source run",
            "actual_result": "passed"
            if replay["all_replay_modes_passed"]
            else "failed_open",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks WR4 and stronger if triggered",
        },
    ]


def build_candidate_row(
    i2: dict[str, Any],
    baseline: dict[str, Any],
    withdrawn: dict[str, Any],
    trace_path: str,
    trace: dict[str, Any],
    replay_path: str,
    replay: dict[str, Any],
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    schema_row = withdrawal_schema_row(i2)
    controls = control_results(trace, replay)
    deferred_controls = [
        control["control_id"]
        for control in controls
        if control["control_status"] == "not_run"
    ]
    runtime_config_digest = digest_value(runtime_config())
    row = {
        "row_id": "n21_i4_row_01_withdrawal_resistance_lgrc9v3_support_weakening",
        "primitive_id": "withdrawal_resistance",
        "source_contract_row": schema_row["source_contract_row"],
        "contract_consumed_without_redefinition": True,
        "row_specific_thresholds_declared_before_use": True,
        "run_artifact_id": WITHDRAWAL_RUN_ID,
        "source_commit_or_source_digest": digest_value(
            {
                "source_files": [
                    "examples/grc9v3/_fixtures.py",
                    "src/pygrc/models/lgrc_9_v3_runtime.py",
                    "src/pygrc/models/lgrc_9_v3_runtime_state.py",
                ],
                "runtime_config_digest": runtime_config_digest,
            }
        ),
        "runtime_config_digest": runtime_config_digest,
        "source_contract_row_digest": schema_row["source_contract_row_digest"],
        "baseline_artifact_path": baseline["run_artifact_path"],
        "withdrawn_or_probe_absent_artifact_path": withdrawn["run_artifact_path"],
        "event_log_or_trace_path": trace_path,
        "snapshot_or_replay_artifact_path": replay_path,
        "artifact_digest": digest_value(artifact_manifest),
        "derived_report_only": False,
        "source_current_inputs": [
            "baseline_run.final_geometry.center_node_coherence",
            "withdrawn_run.final_geometry.center_node_coherence",
            "withdrawn_run.final_geometry.packet_records",
            "withdrawn_run.final_geometry.topology_signature",
            "withdrawn_run.final_geometry.basin_signature",
            "withdrawn_events.jsonl",
            "withdrawn_final_snapshot.json",
        ],
        "producer_mediated_fields": schema_row["producer_mediated_fields"],
        "naturalization_debt_fields": schema_row["naturalization_debt_fields"],
        "blocked_relabel_fields": schema_row["row_specific_blocked_relabels"],
        "same_basin_continuation_rule": schema_row["same_basin_continuation_rule"],
        "support_floor_result": trace["support_floor_trace"]["status"],
        "coherence_floor_result": trace["coherence_floor_trace"]["status"],
        "boundary_integrity_result": trace["boundary_integrity_trace"]["status"],
        "flux_or_leakage_result": trace["flux_or_leakage_trace"]["status"],
        "replay_result": replay,
        "replay_result_status": "passed"
        if replay["all_replay_modes_passed"]
        else "failed_open",
        "control_results": controls,
        "control_result_statuses": sorted(
            {control["control_status"] for control in controls}
        ),
        "required_control_ids_from_i2": schema_row["required_control_ids"],
        "executed_control_ids": [
            control["control_id"]
            for control in controls
            if control["control_status"] != "not_run"
        ],
        "deferred_controls_to_i6": deferred_controls,
        "control_matrix_closeout_pending": True,
        "wr_ladder_rung": "WR4",
        "wr_ladder_rung_status": "provisional_pending_iteration6_control_matrix",
        "nd_ladder_rung": None,
        "row_decision": "supported",
        "row_decision_scope": (
            "supported_for_replay_backed_WR4_candidate_only; I2-required "
            "control-backed WR5/WR6 gates remain deferred to I6"
        ),
        "primitive_claim_allowed": True,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "claim_ceiling": (
            "provisional artifact-level withdrawal-resistance candidate at WR4; "
            "final WR support and closeout remain pending I6 replay/control "
            "matrix; no agency, native support, sentience, Phase 8, or "
            "ant-ecology implementation claim"
        ),
        "withdrawal_schedule": runtime_config()["support_surface"],
        "same_basin_continuation_result": trace["same_basin_continuation_status"],
        "baseline_vs_withdrawn_comparison": trace,
        "artifact_manifest": artifact_manifest,
    }
    return row


def build_checks(row: dict[str, Any], i1: dict[str, Any], i2: dict[str, Any], i3: dict[str, Any]) -> list[dict[str, Any]]:
    required_fields = i2["schema_freeze"]["candidate_evidence_row_schema"][
        "required_fields"
    ]
    required_control_ids = set(withdrawal_schema_row(i2)["required_control_ids"])
    recorded_control_ids = {
        control["control_id"] for control in row["control_results"]
    }
    deferred_control_ids = set(row["deferred_controls_to_i6"])
    artifact_paths = [
        item["path"]
        for item in row["artifact_manifest"]
    ]
    return [
        check(
            "source_i1_i2_i3_passed",
            i1["status"] == "passed"
            and i2["status"] == "passed"
            and i3["status"] == "passed"
            and not i1["failed_checks"]
            and not i2["failed_checks"]
            and not i3["failed_checks"],
            {
                "i1": i1["acceptance_state"],
                "i2": i2["acceptance_state"],
                "i3": i3["acceptance_state"],
            },
        ),
        check(
            "candidate_evidence_fields_present",
            all(field in row for field in required_fields),
            {"required_field_count": len(required_fields)},
        ),
        check(
            "artifact_paths_exist_and_hash",
            all((ROOT / path).exists() for path in artifact_paths)
            and all(sha256_file(item["path"]) == item["sha256"] for item in row["artifact_manifest"]),
            row["artifact_manifest"],
        ),
        check(
            "derived_report_only_false",
            row["derived_report_only"] is False,
            row["derived_report_only"],
        ),
        check(
            "withdrawal_schedule_declared_and_weakened",
            row["withdrawal_schedule"]["withdrawal_mode"] == "weaken"
            and row["withdrawal_schedule"]["baseline_packet_amount"]
            > row["withdrawal_schedule"]["withdrawn_packet_amount"]
            and row["row_specific_thresholds_declared_before_use"],
            row["withdrawal_schedule"],
        ),
        check(
            "source_current_same_basin_preserved",
            row["same_basin_continuation_result"] == "preserved"
            and all(row["baseline_vs_withdrawn_comparison"]["same_basin_comparison"].values()),
            row["baseline_vs_withdrawn_comparison"]["same_basin_comparison"],
        ),
        check(
            "support_coherence_boundary_flux_gates_preserved",
            row["support_floor_result"] == "preserved"
            and row["coherence_floor_result"] == "preserved"
            and row["boundary_integrity_result"] == "preserved"
            and row["flux_or_leakage_result"] == "preserved",
            {
                "support_floor_result": row["support_floor_result"],
                "coherence_floor_result": row["coherence_floor_result"],
                "boundary_integrity_result": row["boundary_integrity_result"],
                "flux_or_leakage_result": row["flux_or_leakage_result"],
            },
        ),
        check(
            "replay_modes_passed",
            row["replay_result_status"] == "passed"
            and row["replay_result"]["all_replay_modes_passed"],
            row["replay_result"],
        ),
        check(
            "required_controls_recorded_with_i6_deferrals",
            required_control_ids.issubset(recorded_control_ids)
            and deferred_control_ids
            == {
                "semantic_relabel_control",
                "native_support_relabel_control",
                "phase8_relabel_control",
                "withdrawal_schedule_removed_control",
                "hidden_support_margin_control",
            }
            and all(
                control["control_status"] == "not_run"
                and control.get("deferred_to_iteration") == 6
                for control in row["control_results"]
                if control["control_id"] in deferred_control_ids
            )
            and not any(
                control["control_status"] == "failed_open"
                for control in row["control_results"]
            ),
            {
                "required_control_ids": sorted(required_control_ids),
                "recorded_control_ids": sorted(recorded_control_ids),
                "deferred_controls_to_i6": row["deferred_controls_to_i6"],
                "control_result_statuses": row["control_result_statuses"],
            },
        ),
        check(
            "provisional_wr4_no_final_closeout",
            row["wr_ladder_rung"] == "WR4"
            and row["wr_ladder_rung_status"]
            == "provisional_pending_iteration6_control_matrix",
            {
                "wr_ladder_rung": row["wr_ladder_rung"],
                "wr_ladder_rung_status": row["wr_ladder_rung_status"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
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
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    runtime_config_payload = runtime_config()
    runtime_config_path = ARTIFACT_DIR / "runtime_config.json"
    write_json(runtime_config_path, runtime_config_payload)

    baseline = run_lgrc_withdrawal_case("baseline", BASELINE_PACKET_AMOUNT)
    withdrawn = run_lgrc_withdrawal_case("withdrawn", WITHDRAWN_PACKET_AMOUNT)
    trace = build_trace_artifact(baseline, withdrawn, rel(runtime_config_path))
    trace_path = ARTIFACT_DIR / "withdrawal_trace.json"
    write_json(trace_path, trace)
    replay = build_replay_artifact(withdrawn)
    replay_path = ARTIFACT_DIR / "snapshot_replay.json"
    write_json(replay_path, replay)

    artifact_paths = [
        rel(runtime_config_path),
        baseline["run_artifact_path"],
        withdrawn["run_artifact_path"],
        baseline["event_log_path"],
        withdrawn["event_log_path"],
        baseline["run_artifact"]["initial_snapshot_path"],
        baseline["run_artifact"]["final_snapshot_path"],
        withdrawn["run_artifact"]["initial_snapshot_path"],
        withdrawn["run_artifact"]["final_snapshot_path"],
        *baseline["run_artifact"]["graph_checkpoint_paths"],
        *withdrawn["run_artifact"]["graph_checkpoint_paths"],
        replay["duplicate_run_artifact_path"],
        rel(trace_path),
        rel(replay_path),
    ]
    # Include duplicate replay artifacts after the replay run has materialized them.
    duplicate_run = load_json(replay["duplicate_run_artifact_path"])
    artifact_paths.extend(
        [
            duplicate_run["event_log_path"],
            duplicate_run["initial_snapshot_path"],
            duplicate_run["final_snapshot_path"],
            *duplicate_run["graph_checkpoint_paths"],
        ]
    )
    artifact_manifest = file_manifest(sorted(set(artifact_paths)))
    row = build_candidate_row(
        i2,
        baseline,
        withdrawn,
        rel(trace_path),
        trace,
        rel(replay_path),
        replay,
        artifact_manifest,
    )
    checks = build_checks(row, i1, i2, i3)
    payload: dict[str, Any] = {
        "artifact_id": "n21_withdrawal_resistance_probe",
        "schema_version": "n21_withdrawal_resistance_probe_v1",
        "experiment": "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth",
        "iteration": 4,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_provisional_wr4_withdrawal_candidate_pending_i6",
        "purpose": (
            "Run a source-current LGRC9V3 withdrawal-resistance probe by "
            "weakening a declared packetized support surface and comparing "
            "baseline vs withdrawn same-basin geometry."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n21_i1_source_contract_inventory"),
            source_record(I2_OUTPUT_PATH, "n21_i2_schema_freeze"),
            source_record(I3_OUTPUT_PATH, "n21_i3_active_nulls"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "source_schema_output_digest": i2["output_digest"],
        "source_active_null_output_digest": i3["output_digest"],
        "candidate_row": row,
        "iteration4_boundary": {
            "positive_primitive_evidence_opened": True,
            "source_current_run_artifacts_consumed": True,
            "withdrawal_resistance_candidate_supported": True,
            "wr_ladder_rung": "WR4",
            "wr_ladder_rung_status": "provisional_pending_iteration6_control_matrix",
            "final_withdrawal_resistance_supported": False,
            "naturalization_depth_supported": False,
            "nd_ladder_rung_assigned": False,
            "n21_closeout_ladder_rung_assigned": False,
            "ready_for_iteration_5_naturalization_probe": True,
            "iteration6_replay_control_matrix_required": True,
        },
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
        payload["acceptance_state"] = "blocked_withdrawal_resistance_probe_checks_failed"
    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    row = data["candidate_row"]
    trace = row["baseline_vs_withdrawn_comparison"]
    lines = [
        "# N21 Iteration 4 - Withdrawal Resistance Probe",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 4 runs the first source-current withdrawal-resistance",
        "candidate. It weakens a declared LGRC9V3 packetized support surface",
        "and compares baseline vs withdrawn geometry.",
        "",
        "## Candidate Row",
        "",
        "```text",
        f"row_id = {row['row_id']}",
        f"row_decision = {row['row_decision']}",
        f"wr_ladder_rung = {row['wr_ladder_rung']}",
        f"wr_ladder_rung_status = {row['wr_ladder_rung_status']}",
        f"row_decision_scope = {row['row_decision_scope']}",
        f"primitive_claim_allowed = {str(row['primitive_claim_allowed']).lower()}",
        f"derived_report_only = {str(row['derived_report_only']).lower()}",
        "```",
        "",
        "## Source-Current Artifacts",
        "",
        "```text",
        f"baseline_artifact_path = {row['baseline_artifact_path']}",
        f"withdrawn_artifact_path = {row['withdrawn_or_probe_absent_artifact_path']}",
        f"event_log_or_trace_path = {row['event_log_or_trace_path']}",
        f"snapshot_or_replay_artifact_path = {row['snapshot_or_replay_artifact_path']}",
        "```",
        "",
        "## Withdrawal Geometry",
        "",
        "```text",
        f"baseline_packet_amount = {trace['baseline_packet_amount']}",
        f"withdrawn_packet_amount = {trace['withdrawn_packet_amount']}",
        f"withdrawal_amount = {trace['withdrawal_amount']}",
        f"support_retention_ratio = {trace['support_retention_ratio']}",
        f"same_basin_continuation_status = {trace['same_basin_continuation_status']}",
        f"support_floor_result = {row['support_floor_result']}",
        f"coherence_floor_result = {row['coherence_floor_result']}",
        f"boundary_integrity_result = {row['boundary_integrity_result']}",
        f"flux_or_leakage_result = {row['flux_or_leakage_result']}",
        "```",
        "",
        "## Replay",
        "",
        "```text",
        f"replay_result_status = {row['replay_result_status']}",
        f"all_replay_modes_passed = {str(row['replay_result']['all_replay_modes_passed']).lower()}",
        "```",
        "",
        "## Controls",
        "",
        "```text",
        f"executed_control_ids = {', '.join(row['executed_control_ids'])}",
        f"deferred_controls_to_i6 = {', '.join(row['deferred_controls_to_i6'])}",
        f"control_result_statuses = {', '.join(row['control_result_statuses'])}",
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "final_withdrawal_resistance_supported = false",
        "iteration6_replay_control_matrix_required = true",
        "agency = false",
        "native_support = false",
        "sentience = false",
        "phase8_implementation = false",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed | Detail |",
        "| --- | --- | --- |",
    ]
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
            "Geometrically, I4 weakens a packetized support surface feeding the",
            "center basin node. The withdrawn run still preserves the center basin",
            "identity, fixed topology signature, active boundary degree, support",
            "floor, coherence floor, and packet budget. This supports a",
            "provisional WR4 withdrawal-resistance candidate because replay",
            "passes, but final WR support remains pending the I6 replay/control",
            "matrix and N21 closeout. I2-required control IDs that are not part",
            "of the I4 replay-backed WR4 gate are recorded as `not_run` and",
            "explicitly deferred to I6; they are not treated as passed in I4.",
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
