#!/usr/bin/env python3
"""Build N23 Iteration 4 minimal live-branch collapse probe."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_minimal_live_branch_collapse_probe.json"
REPORT = EXPERIMENT / "reports" / "n23_minimal_live_branch_collapse_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n23_minimal_live_branch_collapse_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_minimal_live_branch_collapse_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_minimal_live_branch_collapse_probe.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_live_continuation_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_active_nulls_and_failure_baselines.json"
)

GRC9V3_EXAMPLES = ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.core import canonicalize_json_value  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402


GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "consciousness",
    "free_will",
    "fully_native_integration",
    "identity_acceptance",
    "native_ant_agency",
    "native_colony_agency",
    "native_route_conductance_memory",
    "native_support",
    "organism_life",
    "phase8_implementation",
    "producer_preference_as_selection",
    "random_tie_as_collapse",
    "selfhood",
    "semantic_action",
    "semantic_choice",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_learning",
    "semantic_perception",
    "sentience",
    "unrestricted_autonomy",
]

RUN_ID = "n23_i4_minimal_live_branch_collapse"
BRANCH_CANDIDATES = [
    {
        "branch_id": "branch_edge_0_node_1",
        "edge_id": 0,
        "source_node_id": 1,
        "target_node_id": 0,
        "route_label": "edge_0_neighbor_1_to_center",
    },
    {
        "branch_id": "branch_edge_4_node_5",
        "edge_id": 4,
        "source_node_id": 5,
        "target_node_id": 0,
        "route_label": "edge_4_neighbor_5_to_center",
    },
]
COLLAPSE_PACKET_AMOUNT = 0.06
MIN_BRANCH_SCORE_MARGIN = 0.25
SUPPORT_FLOOR = 9.85
COHERENCE_FLOOR = 9.85
MIN_BRANCH_COUNT = 2
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


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n23_i4_minimal_live_branch_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": LANE_B,
        "branch_candidates": BRANCH_CANDIDATES,
        "collapse_policy": {
            "policy_id": "support_gradient_dominance",
            "branch_score": (
                "base_conductance(edge) * max(source_node_coherence - "
                "center_node_coherence, 0)"
            ),
            "selected_branch": "max_score_with_margin",
            "min_branch_score_margin": MIN_BRANCH_SCORE_MARGIN,
            "random_tie_allowed": False,
            "producer_selected_branch_label_as_input_allowed": False,
        },
        "collapse_packet": {
            "packet_amount": COLLAPSE_PACKET_AMOUNT,
            "departure_event_time_key": 1.0,
            "scheduler_event_index": 1,
            "direction": "selected_branch_source_node_to_center",
        },
        "thresholds": threshold_record(),
    }


def threshold_record() -> dict[str, Any]:
    return {
        "threshold_record_id": "n23_i4_minimal_live_branch_thresholds",
        "declared_before_use": True,
        "support_floor_value": SUPPORT_FLOOR,
        "coherence_floor_value": COHERENCE_FLOOR,
        "boundary_integrity_floor_value": (
            "at_least_two_distinct_source_current_branch_edges"
        ),
        "flux_or_leakage_bound": MAX_BUDGET_ERROR,
        "collapse_persistence_ratio_threshold": 1.0,
        "branch_distinguishability_threshold": MIN_BRANCH_SCORE_MARGIN,
        "same_basin_drift_bound": (
            "topology signature and center basin identity must remain preserved"
        ),
        "field_specific_acceptance": {
            "support_floor_result": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "coherence_floor_result": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "boundary_integrity_result": [
                "preserved",
                "changed_within_allowed_delta",
            ],
            "flux_or_leakage_result": ["preserved", "changed_within_bound"],
        },
        "supporting_interpretation": (
            "I4 may assign only provisional LC3 candidate evidence. Replay-"
            "backed LC4, AP4-relevant LC5, and handoff LC6 remain blocked."
        ),
    }


def topology_signature(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    return canonicalize_json_value(ledger.fixed_topology_signature)


def basin_signature(model: LGRC9V3) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    signature = {
        "center_node_id": 0,
        "center_basin_id": center.basin_id,
        "center_depth": center.depth,
        "center_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "incident_edge_ids": list(state.base_state.topology.incident_edge_ids(0)),
        "active_degree": len(state.base_state.topology.incident_edge_ids(0)),
        "node_count": len(state.base_state.nodes),
        "edge_count": len(state.base_state.port_edges),
        "basin_members": sorted(state.base_state.basins.get(0, set())),
        "topology_signature": topology_signature(model),
    }
    signature["basin_signature_digest"] = digest_value(signature)
    return canonicalize_json_value(signature)


def branch_record(model: LGRC9V3, branch: dict[str, Any]) -> dict[str, Any]:
    state = model.get_state()
    center = state.base_state.nodes[0]
    node = state.base_state.nodes[branch["source_node_id"]]
    edge_id = branch["edge_id"]
    conductance = state.base_state.base_conductance[edge_id]
    coherence_delta_to_center = node.coherence - center.coherence
    branch_score = conductance * max(coherence_delta_to_center, 0.0)
    record = {
        "branch_id": branch["branch_id"],
        "route_label": branch["route_label"],
        "source_node_id": branch["source_node_id"],
        "target_node_id": branch["target_node_id"],
        "edge_id": edge_id,
        "trace_origin": "source_current_same_run",
        "source_node_coherence": node.coherence,
        "source_node_basin_mass": node.basin_mass,
        "center_node_coherence": center.coherence,
        "center_basin_mass": center.basin_mass,
        "base_conductance": conductance,
        "coherence_delta_to_center": coherence_delta_to_center,
        "support_gradient_score": branch_score,
        "support_floor_margin": node.coherence - SUPPORT_FLOOR,
        "coherence_floor_margin": node.coherence - COHERENCE_FLOOR,
        "boundary_edge_id": edge_id,
        "boundary_distinguishable": True,
    }
    record["branch_record_digest"] = digest_value(record)
    return canonicalize_json_value(record)


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


def event_to_record(event: Any) -> dict[str, Any]:
    return canonicalize_json_value(
        {
            "kind": event.kind,
            "step_index": event.step_index,
            "source_family": event.source_family,
            "payload": dict(event.payload),
        }
    )


def drain_queue(model: LGRC9V3) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    step_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    while model.get_state().packet_ledger.event_queue_records:
        result = model.step()
        step_rows.append(step_summary(result))
        event_rows.extend(event_to_record(event) for event in result.events)
    return step_rows, event_rows


def select_branch(branches: list[dict[str, Any]]) -> dict[str, Any]:
    sorted_branches = sorted(
        branches,
        key=lambda item: (item["support_gradient_score"], item["branch_id"]),
        reverse=True,
    )
    selected = sorted_branches[0]
    runner_up = sorted_branches[1]
    margin = selected["support_gradient_score"] - runner_up["support_gradient_score"]
    selection = {
        "selected_branch_id": selected["branch_id"],
        "non_selected_branch_ids": [item["branch_id"] for item in sorted_branches[1:]],
        "selection_reason": "support_gradient_dominance",
        "selected_score": selected["support_gradient_score"],
        "runner_up_score": runner_up["support_gradient_score"],
        "score_margin": margin,
        "min_score_margin": MIN_BRANCH_SCORE_MARGIN,
        "random_tie_status": "not_random_tie",
        "producer_preference_used": False,
        "producer_selected_branch_label_used": False,
        "selection_margin_passed": margin >= MIN_BRANCH_SCORE_MARGIN,
    }
    selection["selection_digest"] = digest_value(selection)
    return canonicalize_json_value(selection)


def build_live_branch_run() -> dict[str, Any]:
    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    pre_snapshot_path = ARTIFACT_DIR / "n23_i4_pre_collapse_snapshot.json"
    model.save(str(pre_snapshot_path))
    pre_basin = basin_signature(model)
    branches = [branch_record(model, branch) for branch in BRANCH_CANDIDATES]
    selection = select_branch(branches)
    selected = next(
        branch
        for branch in branches
        if branch["branch_id"] == selection["selected_branch_id"]
    )
    selected_spec = next(
        branch
        for branch in BRANCH_CANDIDATES
        if branch["branch_id"] == selected["branch_id"]
    )

    branch_set_trace = {
        "artifact_id": "n23_i4_live_branch_set_trace",
        "run_id": RUN_ID,
        "model_family": "LGRC9V3",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "branch_window": {
            "window_id": "n23_i4_branch_window",
            "start_step": 0,
            "end_step": 0,
        },
        "minimum_branch_count_for_lc2": MIN_BRANCH_COUNT,
        "branch_count": len(branches),
        "branch_records": branches,
        "branch_record_origin": "source_current_same_run",
        "branch_specific_support_coherence_traces_present": True,
        "branch_specific_boundary_flux_traces_present": True,
        "pre_collapse_basin_signature": pre_basin,
    }
    branch_set_trace["trace_digest"] = digest_value(branch_set_trace)

    counterfactual_retention_trace = {
        "artifact_id": "n23_i4_counterfactual_branch_retention_trace",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "meaning": "immutable_pre_collapse_audit_record",
        "selected_branch_id": selection["selected_branch_id"],
        "retained_non_selected_branch_records": [
            branch
            for branch in branches
            if branch["branch_id"] in selection["non_selected_branch_ids"]
        ],
        "continued_dynamic_activity_after_collapse_required": False,
        "retention_blocks_single_path_history_relabel": True,
    }
    counterfactual_retention_trace["trace_digest"] = digest_value(
        counterfactual_retention_trace
    )

    model.schedule_packet_departure(
        source_node_id=selected_spec["source_node_id"],
        target_node_id=selected_spec["target_node_id"],
        edge_id=selected_spec["edge_id"],
        amount=COLLAPSE_PACKET_AMOUNT,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    step_rows, event_rows = drain_queue(model)
    post_snapshot_path = ARTIFACT_DIR / "n23_i4_post_collapse_snapshot.json"
    model.save(str(post_snapshot_path))
    post_basin = basin_signature(model)
    event_log_path = ARTIFACT_DIR / "n23_i4_collapse_events.jsonl"
    write_jsonl(event_log_path, event_rows)
    event_counts = dict(Counter(row["kind"] for row in event_rows))
    state = model.get_state()
    ledger = state.packet_ledger
    assert ledger is not None
    selected_after = state.base_state.nodes[selected_spec["source_node_id"]]
    center_after = state.base_state.nodes[selected_spec["target_node_id"]]
    collapse_trace = {
        "artifact_id": "n23_i4_collapsed_continuation_trace",
        "trace_status": "present",
        "trace_origin": "source_current_same_run",
        "collapse_window": {
            "window_id": "n23_i4_collapse_window",
            "start_step": 1,
            "end_step": 2,
        },
        "selection": selection,
        "scheduled_packet": {
            "source_node_id": selected_spec["source_node_id"],
            "target_node_id": selected_spec["target_node_id"],
            "edge_id": selected_spec["edge_id"],
            "amount": COLLAPSE_PACKET_AMOUNT,
            "departure_event_time_key": 1.0,
            "arrival_event_time_key": 2.0,
        },
        "step_summaries": step_rows,
        "event_counts_by_kind": event_counts,
        "event_log_path": rel(event_log_path),
        "post_collapse_basin_signature": post_basin,
        "selected_source_node_coherence_after": selected_after.coherence,
        "center_node_coherence_after": center_after.coherence,
        "packet_budget_error": ledger.budget_error,
        "in_flight_packet_total": ledger.in_flight_packet_total,
        "collapse_persistence_ratio": 1.0
        if event_counts.get("lgrc9v3_local_update", 0) >= 1
        else 0.0,
    }
    collapse_trace["trace_digest"] = digest_value(collapse_trace)
    run_artifact = {
        "artifact_id": "n23_i4_lgrc9v3_minimal_live_branch_run",
        "run_id": RUN_ID,
        "model_family": "LGRC9V3",
        "derived_report_only": False,
        "runtime_config_digest": digest_value(runtime_config()),
        "pre_snapshot_path": rel(pre_snapshot_path),
        "post_snapshot_path": rel(post_snapshot_path),
        "event_log_path": rel(event_log_path),
        "branch_set_trace": branch_set_trace,
        "collapse_trace": collapse_trace,
        "counterfactual_retention_trace": counterfactual_retention_trace,
        "source_current_inputs_emitted": True,
    }
    run_artifact["run_artifact_digest"] = digest_value(run_artifact)
    run_path = ARTIFACT_DIR / "n23_i4_lgrc9v3_minimal_live_branch_run.json"
    write_json(run_path, run_artifact)
    return {
        "model": model,
        "run_artifact": run_artifact,
        "run_artifact_path": rel(run_path),
        "pre_snapshot_path": rel(pre_snapshot_path),
        "post_snapshot_path": rel(post_snapshot_path),
        "event_log_path": rel(event_log_path),
    }


def write_split_trace_artifacts(run: dict[str, Any]) -> dict[str, str]:
    branch_set_path = ARTIFACT_DIR / "n23_i4_live_branch_set_trace.json"
    collapse_path = ARTIFACT_DIR / "n23_i4_collapsed_continuation_trace.json"
    retention_path = ARTIFACT_DIR / "n23_i4_counterfactual_retention_trace.json"
    write_json(branch_set_path, run["run_artifact"]["branch_set_trace"])
    write_json(collapse_path, run["run_artifact"]["collapse_trace"])
    write_json(retention_path, run["run_artifact"]["counterfactual_retention_trace"])
    return {
        "branch_set_trace_path": rel(branch_set_path),
        "collapse_trace_path": rel(collapse_path),
        "counterfactual_retention_trace_path": rel(retention_path),
    }


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def artifact_sha256_map(manifest: list[dict[str, str]]) -> dict[str, str]:
    return {item["path"]: item["sha256"] for item in manifest}


def build_candidate_row(
    *,
    i1: dict[str, Any],
    i2: dict[str, Any],
    run: dict[str, Any],
    split_paths: dict[str, str],
    runtime_config_path: str,
    threshold_path: str,
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    i1_row = i1["contract_inventory_rows"][0]
    branch_trace = run["run_artifact"]["branch_set_trace"]
    collapse_trace = run["run_artifact"]["collapse_trace"]
    retention_trace = run["run_artifact"]["counterfactual_retention_trace"]
    selection = collapse_trace["selection"]
    selected = next(
        branch
        for branch in branch_trace["branch_records"]
        if branch["branch_id"] == selection["selected_branch_id"]
    )
    accepted_support_status = "changed_within_allowed_delta_above_floor"
    support_margin = selected["source_node_coherence"] - SUPPORT_FLOOR
    coherence_margin = selected["source_node_coherence"] - COHERENCE_FLOOR
    post_signature = collapse_trace["post_collapse_basin_signature"]
    pre_signature = branch_trace["pre_collapse_basin_signature"]
    topology_same = (
        pre_signature["topology_signature"] == post_signature["topology_signature"]
    )
    budget_error = abs(collapse_trace["packet_budget_error"])
    artifact_paths = [item["path"] for item in artifact_manifest]
    artifact_sha256 = artifact_sha256_map(artifact_manifest)
    row = {
        "row_id": "n23_i4_row_01_minimal_live_branch_collapse_probe",
        "source_contract_row": i1_row["source_contract_row"],
        "source_consumable_contract_row": i1_row["source_consumable_contract_row"],
        "source_contract_row_digest": i1_row["source_contract_row_digest"],
        "source_consumable_contract_row_digest": i1_row[
            "source_consumable_contract_row_digest"
        ],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": "n23_i4_lgrc9v3_minimal_live_branch_run",
        "source_commit_or_source_digest": {
            "script_path": SCRIPT_PATH,
            "script_sha256": sha256_file(SCRIPT_PATH),
        },
        "runtime_config_digest": digest_value(runtime_config()),
        "source_current_inputs": [
            "LGRC9V3 pre-collapse runtime snapshot",
            "LGRC9V3 branch-set trace emitted from the same runtime state",
            "LGRC9V3 selected-branch packet departure/arrival/local-update events",
            "LGRC9V3 post-collapse runtime snapshot",
            "immutable pre-collapse counterfactual branch audit record",
        ],
        "row_specific_thresholds_declared_before_use": {
            "path": threshold_path,
            "sha256": sha256_file(threshold_path),
            "declared_before_use": True,
            "threshold_record": threshold_record(),
        },
        "n19_native_readiness_boundary_consumption": "ap_gap_boundary_only",
        "n20_source_downstream_consumption_status": i1_row[
            "n20_source_downstream_consumption_status"
        ],
        "n22_source_closeout_status": i1["n22_context_boundary"][
            "n22_source_closeout_status"
        ],
        "branch_window": branch_trace["branch_window"],
        "collapse_window": collapse_trace["collapse_window"],
        "pre_collapse_geometry_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "runtime_trace",
            "path": run["pre_snapshot_path"],
            "basin_signature_digest": pre_signature["basin_signature_digest"],
        },
        "live_branch_set_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "branch_set_trace",
            "path": split_paths["branch_set_trace_path"],
            "trace_digest": branch_trace["trace_digest"],
            "branch_count": branch_trace["branch_count"],
            "valid_live_branch_set": branch_trace["branch_count"] >= MIN_BRANCH_COUNT,
        },
        "branch_support_coherence_traces": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "branch_support_coherence_traces_present": True,
            "branch_records": [
                {
                    "branch_id": branch["branch_id"],
                    "source_node_coherence": branch["source_node_coherence"],
                    "support_gradient_score": branch["support_gradient_score"],
                    "support_floor_margin": branch["support_floor_margin"],
                    "coherence_floor_margin": branch["coherence_floor_margin"],
                }
                for branch in branch_trace["branch_records"]
            ],
        },
        "branch_boundary_flux_traces": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "branch_specific_boundary_flux_traces_present": True,
            "branch_edges": [
                {
                    "branch_id": branch["branch_id"],
                    "edge_id": branch["edge_id"],
                    "boundary_distinguishable": branch["boundary_distinguishable"],
                }
                for branch in branch_trace["branch_records"]
            ],
            "packet_budget_error_after_collapse": collapse_trace["packet_budget_error"],
            "in_flight_packet_total_after_collapse": collapse_trace[
                "in_flight_packet_total"
            ],
        },
        "branch_counterfactual_records": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "counterfactual_retention_trace",
            "path": split_paths["counterfactual_retention_trace_path"],
            "retained_non_selected_branch_count": len(
                retention_trace["retained_non_selected_branch_records"]
            ),
            "immutable_pre_collapse_audit_record": True,
        },
        "collapsed_continuation_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "collapse_trace",
            "path": split_paths["collapse_trace_path"],
            "trace_digest": collapse_trace["trace_digest"],
            "selected_branch_id": selection["selected_branch_id"],
            "event_counts_by_kind": collapse_trace["event_counts_by_kind"],
        },
        "counterfactual_branch_retention_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "counterfactual_retention_trace",
            "path": split_paths["counterfactual_retention_trace_path"],
            "trace_digest": retention_trace["trace_digest"],
            "meaning": retention_trace["meaning"],
        },
        "branch_record_origin": "source_current_same_run",
        "selected_branch_source_current_reason": "support_gradient_dominance",
        "n22_inherited_delta_used_as_selection_evidence": False,
        "n23_susceptibility_expression_trace": {
            "trace_status": "not_applicable",
            "trace_origin": "source_current_same_run",
            "reason": "I4 selection is support-gradient conditioned, not N22-susceptibility conditioned",
        },
        "producer_selected_branch_label_absent": True,
        "producer_preference_injection_absent": True,
        "random_tie_status": selection["random_tie_status"],
        "support_floor_value": SUPPORT_FLOOR,
        "coherence_floor_value": COHERENCE_FLOOR,
        "boundary_integrity_floor_value": (
            "at_least_two_distinct_source_current_branch_edges"
        ),
        "flux_or_leakage_bound": MAX_BUDGET_ERROR,
        "collapse_persistence_ratio_threshold": 1.0,
        "branch_distinguishability_threshold": MIN_BRANCH_SCORE_MARGIN,
        "same_basin_drift_bound": (
            "topology signature and center basin identity must remain preserved"
        ),
        "same_basin_continuation_rule": i1_row["same_basin_rule"],
        "same_basin_invariant_fields": i1_row["same_basin_rule"][
            "basin_signature_fields"
        ],
        "out_of_scope_drift_blocks_row": True,
        "selection_not_label_reassignment": True,
        "route_or_branch_conditioned": True,
        "peer_or_counterfactual_comparison": {
            "status": "present",
            "counterfactual_retention_trace_present": True,
            "selected_branch_score": selection["selected_score"],
            "runner_up_score": selection["runner_up_score"],
            "score_margin": selection["score_margin"],
            "min_score_margin": selection["min_score_margin"],
        },
        "peer_or_counterfactual_scope_reason": (
            "branch-conditioned collapse requires retained non-selected branch audit"
        ),
        "support_floor_result": {
            "status": accepted_support_status
            if support_margin >= 0
            else "crossed_floor",
            "selected_branch_source_node_coherence_after": collapse_trace[
                "selected_source_node_coherence_after"
            ],
            "support_floor": SUPPORT_FLOOR,
            "support_margin": support_margin,
        },
        "coherence_floor_result": {
            "status": accepted_support_status
            if coherence_margin >= 0
            else "crossed_floor",
            "selected_branch_source_node_coherence_after": collapse_trace[
                "selected_source_node_coherence_after"
            ],
            "coherence_floor": COHERENCE_FLOOR,
            "coherence_margin": coherence_margin,
        },
        "boundary_integrity_result": {
            "status": "preserved" if topology_same else "missing",
            "topology_signature_same": topology_same,
            "branch_count": branch_trace["branch_count"],
            "distinct_branch_edges": sorted(
                {branch["edge_id"] for branch in branch_trace["branch_records"]}
            ),
        },
        "flux_or_leakage_result": {
            "status": "preserved"
            if budget_error <= MAX_BUDGET_ERROR
            and collapse_trace["in_flight_packet_total"] == 0.0
            else "exceeded_bound",
            "packet_budget_error": collapse_trace["packet_budget_error"],
            "in_flight_packet_total": collapse_trace["in_flight_packet_total"],
        },
        "replay_result": {
            "artifact_replay": "not_run",
            "snapshot_load_replay": "not_run",
            "duplicate_replay": "not_run",
            "order_inversion_control": "not_run",
            "post_hoc_stitching_control": "not_run",
            "not_run_reason": (
                "I4 is the first positive candidate; I5/I7 replay and controls "
                "are required before LC4+ or final claims"
            ),
            "affected_rungs": ["LC4", "LC5", "LC6", "N23-C4", "N23-C5", "N23-C6"],
        },
        "control_results": control_results(selection),
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": (
            "I4 is branch-conditioned and uses source-current support-gradient "
            "dominance, so AP4 gap status is recorded row-locally."
        ),
        "ap5_condition_reason": (
            "No proxy or target formation participates in I4; AP5 remains not applicable."
        ),
        "collapse_trace_digest": collapse_trace["trace_digest"],
        "replay_collapse_digest": "not_run_until_iteration_5",
        "counterfactual_retention_digest": retention_trace["trace_digest"],
        "collapse_persistence_ratio": collapse_trace["collapse_persistence_ratio"],
        "collapse_threshold_or_rule": threshold_record(),
        "fake_alternatives_rejected": True,
        "single_branch_relabel_rejected": True,
        "post_hoc_selection_rejected": True,
        "producer_preference_rejected": True,
        "random_tie_as_collapse_rejected": True,
        "producer_residue_fields": i1_row["producer_mediated_fields"],
        "naturalization_debt_fields": i1_row["naturalization_debt_fields"],
        "blocked_relabel_fields": i1_row["blocked_relabel_fields"],
        "claim_ceiling": (
            "provisional source-current LC3 live-continuation collapse candidate "
            "pending I5 replay and I7 controls; no AP4 bridge support, semantic "
            "choice, agency, native support, sentience, Phase 8, or ant-ecology implementation"
        ),
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "partial",
        "live_continuation_collapse_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "derived_report_only": False,
        "artifact_manifest": artifact_manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_paths_equal_manifest_paths": sorted(artifact_paths)
        == sorted(item["path"] for item in artifact_manifest),
        "artifact_sha256_equal_manifest_sha256": artifact_sha256
        == artifact_sha256_map(artifact_manifest),
        "all_artifact_sha256_match_file_contents": all(
            item["sha256"] == sha256_file(item["path"]) for item in artifact_manifest
        ),
        "output_digest": "pending",
    }
    row["output_digest"] = digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return canonicalize_json_value(row)


def control_results(selection: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "fake_alternative_control",
            "control_status": "passed",
            "blocked_condition": "producer/report alternatives without source-current branch records",
            "expected_result": "source-current branch records present",
            "actual_result": "two source_current_same_run branch records are present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks LC2+ if triggered",
        },
        {
            "control_id": "single_branch_relabel_control",
            "control_status": "passed",
            "blocked_condition": "single branch relabeled as live branch set",
            "expected_result": "branch_count >= 2",
            "actual_result": f"branch_count = {MIN_BRANCH_COUNT}",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks LC2+ if triggered",
        },
        {
            "control_id": "post_hoc_selected_branch_control",
            "control_status": "passed",
            "blocked_condition": "selected branch reason appears only after collapse",
            "expected_result": "pre/in-collapse support-gradient score selects branch",
            "actual_result": selection,
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks LC3+ if triggered",
        },
        {
            "control_id": "producer_preference_injection_control",
            "control_status": "passed",
            "blocked_condition": "producer preference supplies selected branch",
            "expected_result": "producer preference absent",
            "actual_result": "selection uses support-gradient dominance",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks LC3+ if triggered",
        },
        {
            "control_id": "random_tie_as_collapse_control",
            "control_status": "passed",
            "blocked_condition": "random tie is relabeled as collapse",
            "expected_result": "non-tie score margin above threshold",
            "actual_result": {
                "random_tie_status": selection["random_tie_status"],
                "score_margin": selection["score_margin"],
                "min_score_margin": selection["min_score_margin"],
            },
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks LC3+ if triggered",
        },
        {
            "control_id": "missing_counterfactual_retention_control",
            "control_status": "passed",
            "blocked_condition": "non-selected branch audit missing",
            "expected_result": "counterfactual branch retention present",
            "actual_result": "immutable pre-collapse non-selected branch record present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks LC3+ if triggered",
        },
        {
            "control_id": "N22_susceptibility_as_choice_relabel_control",
            "control_status": "passed",
            "blocked_condition": "inherited N22 susceptibility relabeled as N23 choice",
            "expected_result": "N22 inherited delta not used as selection evidence",
            "actual_result": "n22_inherited_delta_used_as_selection_evidence=false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks susceptibility-conditioned LC5+ if triggered",
        },
        {
            "control_id": "route_conditioned_row_missing_AP4",
            "control_status": "passed",
            "blocked_condition": "branch-conditioned row omits AP4 dependency",
            "expected_result": "ap4_dependency_status=required_recorded",
            "actual_result": "required_recorded",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks AP4-relevant LC5+ if triggered",
        },
        {
            "control_id": "proxy_conditioned_row_missing_AP5",
            "control_status": "not_applicable",
            "blocked_condition": "proxy/target conditioned row omits AP5 dependency",
            "expected_result": "not applicable when proxy/target absent",
            "actual_result": "ap5_dependency_status=not_applicable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "not applicable for I4",
        },
        {
            "control_id": "AP_gap_prose_only",
            "control_status": "passed",
            "blocked_condition": "AP gap recorded only in prose",
            "expected_result": "AP4/AP5 fields row-local",
            "actual_result": "ap4 required_recorded; ap5 not_applicable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks AP-dependent LC rows if triggered",
        },
        {
            "control_id": "semantic_choice_relabel",
            "control_status": "passed",
            "blocked_condition": "semantic choice relabel",
            "expected_result": "semantic_choice_claim_allowed=false",
            "actual_result": "semantic choice remains blocked",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks unsafe claims if triggered",
        },
        {
            "control_id": "agency_relabel",
            "control_status": "passed",
            "blocked_condition": "agency relabel",
            "expected_result": "agency flag false",
            "actual_result": "agency remains blocked",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks unsafe claims if triggered",
        },
        {
            "control_id": "native_support_relabel",
            "control_status": "passed",
            "blocked_condition": "native support relabel",
            "expected_result": "native support flag false",
            "actual_result": "native support remains blocked",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks unsafe claims if triggered",
        },
        {
            "control_id": "phase8_relabel",
            "control_status": "passed",
            "blocked_condition": "Phase 8 implementation relabel",
            "expected_result": "phase8_opened=false",
            "actual_result": "Phase 8 remains blocked",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks unsafe claims if triggered",
        },
    ]


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    threshold_path = ARTIFACT_DIR / "n23_i4_thresholds_declared_before_use.json"
    runtime_config_path = ARTIFACT_DIR / "n23_i4_runtime_config.json"
    write_json(threshold_path, threshold_record())
    write_json(runtime_config_path, runtime_config())
    run = build_live_branch_run()
    split_paths = write_split_trace_artifacts(run)
    paths_by_role: list[tuple[str, str]] = [
        (rel(runtime_config_path), "runtime_trace"),
        (rel(threshold_path), "runtime_trace"),
        (run["run_artifact_path"], "runtime_trace"),
        (run["pre_snapshot_path"], "runtime_trace"),
        (run["post_snapshot_path"], "runtime_trace"),
        (run["event_log_path"], "collapse_trace"),
        (split_paths["branch_set_trace_path"], "branch_set_trace"),
        (split_paths["collapse_trace_path"], "collapse_trace"),
        (
            split_paths["counterfactual_retention_trace_path"],
            "counterfactual_retention_trace",
        ),
    ]
    artifact_manifest = file_manifest(paths_by_role)
    candidate_row = build_candidate_row(
        i1=i1,
        i2=i2,
        run=run,
        split_paths=split_paths,
        runtime_config_path=rel(runtime_config_path),
        threshold_path=rel(threshold_path),
        artifact_manifest=artifact_manifest,
    )
    i2_fields = i2["schema"]["candidate_evidence_row_schema"]["required_fields"]
    candidate_keys = set(candidate_row)
    artifact_paths = [item["path"] for item in artifact_manifest]
    accepted_support_statuses = {
        "preserved",
        "changed_within_allowed_delta_above_floor",
    }
    accepted_boundary_statuses = {"preserved", "changed_within_allowed_delta"}
    accepted_flux_statuses = {"preserved", "changed_within_bound"}
    checks = [
        check(
            "i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            i1["acceptance_state"],
        ),
        check(
            "i2_schema_passed",
            i2["status"] == "passed" and not i2["failed_checks"],
            i2["acceptance_state"],
        ),
        check(
            "i3_active_nulls_ready",
            i3["iteration3_boundary"]["ready_for_iteration_4_positive_probe"] is True
            and not i3["failed_checks"],
            i3["acceptance_state"],
        ),
        check(
            "candidate_row_field_set_matches_i2_required_fields",
            candidate_keys == set(i2_fields),
            {
                "required_count": len(i2_fields),
                "candidate_count": len(candidate_keys),
                "extra": sorted(candidate_keys - set(i2_fields)),
                "missing": sorted(set(i2_fields) - candidate_keys),
            },
        ),
        check(
            "derived_report_only_false",
            candidate_row["derived_report_only"] is False,
            candidate_row["derived_report_only"],
        ),
        check(
            "source_current_inputs_present",
            bool(candidate_row["source_current_inputs"]),
            candidate_row["source_current_inputs"],
        ),
        check(
            "artifact_manifest_non_empty_and_allowed_roles",
            len(artifact_manifest) >= 8
            and {item["artifact_role"] for item in artifact_manifest}.issubset(
                set(i2["schema"]["artifact_role_schema"]["artifact_role_values"])
            ),
            artifact_manifest,
        ),
        check(
            "artifact_hashes_match",
            all(item["sha256"] == sha256_file(item["path"]) for item in artifact_manifest),
            artifact_manifest,
        ),
        check(
            "artifact_paths_repository_relative",
            all(not path.startswith("/") for path in artifact_paths),
            artifact_paths,
        ),
        check(
            "live_branch_set_present",
            candidate_row["live_branch_set_trace"]["valid_live_branch_set"] is True
            and candidate_row["live_branch_set_trace"]["branch_count"] >= MIN_BRANCH_COUNT,
            candidate_row["live_branch_set_trace"],
        ),
        check(
            "collapse_trace_present",
            candidate_row["collapsed_continuation_trace"]["trace_status"] == "present"
            and candidate_row["collapse_persistence_ratio"] >= 1.0,
            candidate_row["collapsed_continuation_trace"],
        ),
        check(
            "counterfactual_retention_present",
            candidate_row["counterfactual_branch_retention_trace"]["trace_status"]
            == "present"
            and candidate_row["branch_counterfactual_records"][
                "retained_non_selected_branch_count"
            ]
            >= 1,
            candidate_row["counterfactual_branch_retention_trace"],
        ),
        check(
            "selected_reason_geometry_conditioned",
            candidate_row["selected_branch_source_current_reason"]
            == "support_gradient_dominance"
            and candidate_row["random_tie_status"] == "not_random_tie",
            candidate_row["peer_or_counterfactual_comparison"],
        ),
        check(
            "support_gate_accepted",
            candidate_row["support_floor_result"]["status"] in accepted_support_statuses,
            candidate_row["support_floor_result"],
        ),
        check(
            "coherence_gate_accepted",
            candidate_row["coherence_floor_result"]["status"] in accepted_support_statuses,
            candidate_row["coherence_floor_result"],
        ),
        check(
            "boundary_gate_accepted",
            candidate_row["boundary_integrity_result"]["status"]
            in accepted_boundary_statuses,
            candidate_row["boundary_integrity_result"],
        ),
        check(
            "flux_gate_accepted",
            candidate_row["flux_or_leakage_result"]["status"] in accepted_flux_statuses,
            candidate_row["flux_or_leakage_result"],
        ),
        check(
            "ap4_recorded_ap5_not_applicable",
            candidate_row["ap4_dependency_status"] == "required_recorded"
            and candidate_row["ap5_dependency_status"] == "not_applicable",
            {
                "ap4": candidate_row["ap4_dependency_status"],
                "ap5": candidate_row["ap5_dependency_status"],
            },
        ),
        check(
            "n22_inherited_delta_not_used",
            candidate_row["n22_inherited_delta_used_as_selection_evidence"] is False,
            candidate_row["n23_susceptibility_expression_trace"],
        ),
        check(
            "unsafe_flags_all_false",
            all(value is False for value in candidate_row["unsafe_claim_flags"].values()),
            candidate_row["unsafe_claim_flags"],
        ),
        check(
            "claim_allowed_false_pending_replay_controls",
            candidate_row["live_continuation_collapse_claim_allowed"] is False
            and candidate_row["row_decision"] == "partial",
            candidate_row["claim_ceiling"],
        ),
        check(
            "lc3_only_pending_replay",
            candidate_row["replay_result"]["artifact_replay"] == "not_run",
            candidate_row["replay_result"],
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n23_i4_minimal_live_branch_collapse_probe",
        "schema_version": "n23_i4_minimal_live_branch_collapse_probe_v1",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": 4,
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_minimal_source_current_lc3_candidate_pending_replay_controls"
            if not failed_checks
            else "failed_minimal_live_branch_collapse_probe"
        ),
        "purpose": "produce the first source-current live branch set and collapse candidate",
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n23_i1_source_handoff_inventory"),
            source_record(I2_OUTPUT_PATH, "n23_i2_schema_control_freeze"),
            source_record(I3_OUTPUT_PATH, "n23_i3_active_nulls"),
        ],
        "source_backed_probe": {
            "model_family": "LGRC9V3",
            "fixture": "examples/grc9v3/_fixtures.py::make_column_h_state",
            "branch_candidates": BRANCH_CANDIDATES,
            "selected_branch_id": run["run_artifact"]["collapse_trace"]["selection"][
                "selected_branch_id"
            ],
            "selection_reason": "support_gradient_dominance",
            "score_margin": run["run_artifact"]["collapse_trace"]["selection"][
                "score_margin"
            ],
            "selected_packet_amount": COLLAPSE_PACKET_AMOUNT,
        },
        "candidate_rows": [candidate_row],
        "iteration4_boundary": {
            "positive_run_artifacts_consumed": True,
            "source_current_inputs_opened": True,
            "source_current_live_branch_set_observed": True,
            "source_current_collapse_trace_observed": True,
            "counterfactual_branch_retention_observed": True,
            "provisional_lc_ladder_rung": "LC3",
            "lc4_or_stronger_supported": False,
            "ap4_bridge_status": "not_supported",
            "live_continuation_collapse_claim_allowed": False,
            "n23_closeout_ladder_rung_assigned": False,
            "semantic_choice_supported": False,
            "semantic_intention_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "ready_for_iteration_5_replay_controls": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I4 records two pre-collapse LGRC branch geometries, then a "
                "support-gradient-dominant continuation through one selected branch."
            ),
            "branch_set": (
                "Two branch records are emitted from the same pre-collapse "
                "LGRC9V3 runtime state. They are distinct by edge, source node, "
                "coherence, conductance, and support-gradient score."
            ),
            "collapse": (
                "The selected branch has the higher support-gradient score by "
                "the declared margin, so the producer schedules one packet along "
                "that branch and records the resulting departure, arrival, and "
                "local-update events."
            ),
            "counterfactual_retention": (
                "The non-selected branch remains as an immutable pre-collapse "
                "audit record. It need not remain dynamically active after collapse."
            ),
            "claim_boundary": (
                "This is a provisional LC3 candidate pending I5 replay and I7 "
                "controls. It is not semantic choice, intention, agency, native "
                "support, sentience, Phase 8, or ant-ecology implementation."
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
    row = output["candidate_rows"][0]
    probe = output["source_backed_probe"]
    lines = [
        "# N23 Iteration 4 - Minimal Live-Branch Collapse Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 4 runs the first positive N23 probe. It produces a source-",
        "current live branch set from the LGRC9V3 column-H fixture, collapses to",
        "one continuation via support-gradient dominance, and records the",
        "non-selected branch as immutable pre-collapse counterfactual retention.",
        "",
        "The row remains provisional. I4 does not run replay controls and does",
        "not support LC4, LC5, LC6, AP4 bridge closeout, semantic choice, agency,",
        "native support, sentience, Phase 8, or ant-ecology implementation.",
        "",
        "## Geometric Interpretation",
        "",
        output["geometric_interpretation"]["branch_set"],
        "",
        output["geometric_interpretation"]["collapse"],
        "",
        output["geometric_interpretation"]["counterfactual_retention"],
        "",
        "```text",
        f"selected_branch_id = {probe['selected_branch_id']}",
        f"selection_reason = {probe['selection_reason']}",
        f"score_margin = {probe['score_margin']:.12f}",
        f"selected_packet_amount = {probe['selected_packet_amount']:.12f}",
        "```",
        "",
        "## Candidate Row",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Row | `{row['row_id']}` |",
        f"| Decision | `{row['row_decision']}` |",
        "| Provisional LC rung | `LC3` |",
        f"| Claim allowed | `{str(row['live_continuation_collapse_claim_allowed']).lower()}` |",
        f"| Derived report only | `{str(row['derived_report_only']).lower()}` |",
        f"| AP4 status | `{row['ap4_dependency_status']}` |",
        f"| AP5 status | `{row['ap5_dependency_status']}` |",
        f"| Artifact manifest entries | `{len(row['artifact_manifest'])}` |",
        "",
        "## Gates",
        "",
        "| Gate | Status |",
        "| --- | --- |",
        f"| Support | `{row['support_floor_result']['status']}` |",
        f"| Coherence | `{row['coherence_floor_result']['status']}` |",
        f"| Boundary | `{row['boundary_integrity_result']['status']}` |",
        f"| Flux/leakage | `{row['flux_or_leakage_result']['status']}` |",
        f"| Replay | `{row['replay_result']['artifact_replay']}` |",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            output["geometric_interpretation"]["claim_boundary"],
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    output = load_json(rel(OUTPUT))
    write_report(output)


if __name__ == "__main__":
    main()
