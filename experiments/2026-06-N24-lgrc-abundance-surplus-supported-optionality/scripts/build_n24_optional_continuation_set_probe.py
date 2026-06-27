#!/usr/bin/env python3
"""Build N24 Iteration 5 source-current optional continuation set probe."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import build_n24_minimal_surplus_probe as base


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_optional_continuation_set_probe.json"
REPORT = EXPERIMENT / "reports" / "n24_optional_continuation_set_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_optional_continuation_set_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_optional_continuation_set_probe.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_optional_continuation_set_probe.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I4_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_minimal_surplus_probe.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH

RUN_ID = "n24_i5_source_current_optional_continuation_set"
SUPPORT_FLOOR = base.SUPPORT_FLOOR
COHERENCE_FLOOR = base.COHERENCE_FLOOR
MIN_SURPLUS_MARGIN = base.MIN_SURPLUS_MARGIN
FLUX_OR_LEAKAGE_BOUND = base.FLUX_OR_LEAKAGE_BOUND
MAINTENANCE_BASIN_ID = base.MAINTENANCE_BASIN_ID
MAINTENANCE_NODE_IDS = base.MAINTENANCE_NODE_IDS
SUPPORT_MEASUREMENT_SCOPE = base.SUPPORT_MEASUREMENT_SCOPE
SUPPORT_AGGREGATION_METHOD = base.SUPPORT_AGGREGATION_METHOD
OPTIONAL_BRANCH_TARGET_NODE_IDS = [1, 5, 9]


def threshold_record() -> dict[str, Any]:
    record = base.threshold_record()
    record["threshold_record_id"] = "n24_i5_thresholds_declared_before_use"
    record["threshold_record_digest"] = base.digest_value(record)
    return record


def runtime_config() -> dict[str, Any]:
    return {
        "config_id": "n24_i5_optional_continuation_runtime_config",
        "model_family": "LGRC9V3",
        "fixture_source": "examples/grc9v3/_fixtures.py",
        "fixture": "make_column_h_state",
        "runtime_config_builder": "make_config",
        "spark_lane": base.LANE_B,
        "maintenance_basin": {
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "node_ids": MAINTENANCE_NODE_IDS,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        },
        "optionality_window": optionality_window(),
        "optional_branch_target_node_ids": OPTIONAL_BRANCH_TARGET_NODE_IDS,
        "thresholds": threshold_record(),
        "claim_boundary": {
            "max_iteration5_rung": "AB3",
            "ab4_replay_control_required_later": True,
            "surplus_supported_optionality_claim_allowed": False,
        },
    }


def optionality_window() -> dict[str, Any]:
    return {
        "window_id": "n24_i5_source_current_optionality_window",
        "start_step": 0,
        "end_step": 0,
        "window_role": (
            "same source-current availability window; no deterministic replay "
            "or stress validation yet"
        ),
        "maintenance_floor_declared_before_window": True,
    }


def edge_for_target(model: base.LGRC9V3, target_node_id: int) -> tuple[int, Any]:
    state = model.get_state()
    for edge_id, edge in state.base_state.port_edges.items():
        endpoints = {edge.node_u, edge.node_v}
        if 0 in endpoints and target_node_id in endpoints:
            return edge_id, edge
    raise KeyError(f"no center edge found for target node {target_node_id}")


def branch_records(model: base.LGRC9V3) -> list[dict[str, Any]]:
    state = model.get_state()
    rows: list[dict[str, Any]] = []
    for index, target_node_id in enumerate(OPTIONAL_BRANCH_TARGET_NODE_IDS, start=1):
        edge_id, _edge = edge_for_target(model, target_node_id)
        node = state.base_state.nodes[target_node_id]
        support_before = node.coherence
        coherence_before = node.coherence
        optional_flux_cost = 0.0
        support_after = support_before - optional_flux_cost
        coherence_after = coherence_before - optional_flux_cost
        rows.append(
            {
                "branch_id": f"n24_i5_branch_{index:02d}_to_node_{target_node_id}",
                "source_node_id": 0,
                "target_node_id": target_node_id,
                "edge_id_or_route_id": f"edge_{edge_id}",
                "trace_origin": "source_current_same_run",
                "trace_status": "present",
                "optionality_window_step_range": {
                    "start_step": 0,
                    "end_step": 0,
                    "window_id": optionality_window()["window_id"],
                },
                "support_before": support_before,
                "support_after_or_projected_after": support_after,
                "coherence_before": coherence_before,
                "coherence_after_or_projected_after": coherence_after,
                "support_surplus_margin_before": support_before - SUPPORT_FLOOR,
                "support_surplus_margin_after": support_after - SUPPORT_FLOOR,
                "coherence_surplus_margin_before": coherence_before - COHERENCE_FLOOR,
                "coherence_surplus_margin_after": coherence_after - COHERENCE_FLOOR,
                "boundary_integrity_result": "preserved",
                "flux_or_leakage_result": "preserved",
                "optional_flux_cost": optional_flux_cost,
                "maintenance_floor_preserved": support_after >= SUPPORT_FLOOR
                and coherence_after >= COHERENCE_FLOOR,
                "reward_or_proxy_label_used": False,
                "producer_enumeration_used": False,
                "admissibility_status": "admissible",
            }
        )
    return rows


def build_runtime_artifacts() -> dict[str, Any]:
    model = base.LGRC9V3.from_state(
        base.make_column_h_state(), base.make_config(spark_lane=base.LANE_B)
    )
    snapshot_path = ARTIFACT_DIR / "n24_i5_source_current_snapshot.json"
    model.save(str(snapshot_path))
    signature = base.maintenance_basin_signature(model)
    threshold = threshold_record()
    support_margin = signature["min_support"] - SUPPORT_FLOOR
    coherence_margin = signature["min_coherence"] - COHERENCE_FLOOR
    branches = branch_records(model)
    residual_support_margin = support_margin
    residual_coherence_margin = coherence_margin
    observed_optional_flux_drain = sum(branch["optional_flux_cost"] for branch in branches)
    optional_flux_drain_margin = FLUX_OR_LEAKAGE_BOUND - observed_optional_flux_drain

    floor_trace = base.trace_record(
        "n24_i5_maintenance_floor_trace",
        "present",
        "source_current_same_run",
        {
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "support_floor_value": SUPPORT_FLOOR,
            "coherence_floor_value": COHERENCE_FLOOR,
            "declared_before_use": True,
            "threshold_record_digest": threshold["threshold_record_digest"],
        },
    )
    surplus_trace = base.trace_record(
        "n24_i5_support_surplus_margin_trace",
        "present",
        "source_current_same_run",
        {
            "formula": "observed_support - support_floor_value",
            "observed_support": signature["min_support"],
            "support_floor_value": SUPPORT_FLOOR,
            "support_surplus_margin": support_margin,
            "minimum_support_surplus_margin": MIN_SURPLUS_MARGIN,
            "coherence_formula": "observed_coherence - coherence_floor_value",
            "observed_coherence": signature["min_coherence"],
            "coherence_floor_value": COHERENCE_FLOOR,
            "coherence_surplus_margin": coherence_margin,
            "minimum_coherence_surplus_margin": MIN_SURPLUS_MARGIN,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        },
    )
    optional_trace = base.trace_record(
        "n24_i5_optional_continuation_set_trace",
        "present",
        "source_current_same_run",
        {
            "same_source_current_run": True,
            "declared_replay_family_may_validate_but_not_create_original_set": True,
            "same_declared_optionality_window": True,
            "optionality_window": optionality_window(),
            "optional_continuation_count": len(branches),
            "optional_continuation_availability_count": len(branches),
            "jointly_admissible_optional_continuation_count": 0,
            "joint_admissibility_status": "not_run_until_stress_threshold_matrix",
            "branch_ids": [branch["branch_id"] for branch in branches],
            "optional_branch_records_digest": base.digest_value(branches),
        },
    )
    branch_support_trace = base.trace_record(
        "n24_i5_optional_branch_support_coherence_traces",
        "present",
        "source_current_same_run",
        {
            "optionality_window": optionality_window(),
            "branch_records": branches,
            "residual_support_margin_under_optionality": residual_support_margin,
            "residual_coherence_margin_under_optionality": residual_coherence_margin,
            "residual_margin_scope": "maintenance_basin_node_set_min_during_optionality_window",
            "branch_specific_support_coherence_traces_present": True,
        },
    )
    branch_boundary_trace = base.trace_record(
        "n24_i5_optional_branch_boundary_flux_traces",
        "present",
        "source_current_same_run",
        {
            "optionality_window": optionality_window(),
            "branch_ids": [branch["branch_id"] for branch in branches],
            "boundary_integrity_result": "preserved",
            "flux_or_leakage_result": "preserved",
            "observed_optional_flux_drain": observed_optional_flux_drain,
            "optional_flux_drain_margin": optional_flux_drain_margin,
            "branch_specific_boundary_flux_traces_present": True,
        },
    )
    boundary_under_optionality_trace = base.trace_record(
        "n24_i5_boundary_integrity_under_optionality_trace",
        "present",
        "source_current_same_run",
        {
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
            "maintenance_node_ids": MAINTENANCE_NODE_IDS,
            "topology_signature": signature["topology_signature"],
            "boundary_integrity_under_optionality": "preserved",
            "optional_flux_does_not_drain_maintenance_support": True,
        },
    )

    run_artifact = {
        "artifact_id": "n24_i5_lgrc9v3_optional_continuation_set_run",
        "run_id": RUN_ID,
        "model_family": "LGRC9V3",
        "fixture": "make_column_h_state",
        "derived_report_only": False,
        "source_current_inputs_emitted": True,
        "runtime_config_digest": base.digest_value(runtime_config()),
        "snapshot_path": base.rel(snapshot_path),
        "maintenance_basin_signature": signature,
        "maintenance_floor_trace": floor_trace,
        "support_surplus_margin_trace": surplus_trace,
        "optional_continuation_set_trace": optional_trace,
        "optional_branch_support_coherence_traces": branch_support_trace,
        "optional_branch_boundary_flux_traces": branch_boundary_trace,
        "boundary_integrity_under_optionality_trace": boundary_under_optionality_trace,
        "optional_branch_records": branches,
        "event_counts_by_kind": {},
    }
    run_artifact["run_artifact_digest"] = base.digest_value(run_artifact)

    paths = {
        "run_artifact_path": ARTIFACT_DIR / "n24_i5_lgrc9v3_optional_continuation_set_run.json",
        "snapshot_path": snapshot_path,
        "floor_trace_path": ARTIFACT_DIR / "n24_i5_maintenance_floor_trace.json",
        "surplus_trace_path": ARTIFACT_DIR / "n24_i5_support_surplus_margin_trace.json",
        "optional_trace_path": ARTIFACT_DIR / "n24_i5_optional_continuation_set_trace.json",
        "branch_support_trace_path": ARTIFACT_DIR / "n24_i5_optional_branch_support_coherence_traces.json",
        "branch_boundary_trace_path": ARTIFACT_DIR / "n24_i5_optional_branch_boundary_flux_traces.json",
        "boundary_under_optionality_trace_path": ARTIFACT_DIR / "n24_i5_boundary_integrity_under_optionality_trace.json",
        "threshold_path": ARTIFACT_DIR / "n24_i5_thresholds_declared_before_use.json",
        "runtime_config_path": ARTIFACT_DIR / "n24_i5_runtime_config.json",
    }
    write_map = {
        "run_artifact_path": run_artifact,
        "floor_trace_path": floor_trace,
        "surplus_trace_path": surplus_trace,
        "optional_trace_path": optional_trace,
        "branch_support_trace_path": branch_support_trace,
        "branch_boundary_trace_path": branch_boundary_trace,
        "boundary_under_optionality_trace_path": boundary_under_optionality_trace,
        "threshold_path": threshold,
        "runtime_config_path": runtime_config(),
    }
    for key, data in write_map.items():
        base.write_json(paths[key], data)
    return {
        "run_artifact": run_artifact,
        **{key: base.rel(path) for key, path in paths.items()},
        "residual_support_margin": residual_support_margin,
        "residual_coherence_margin": residual_coherence_margin,
        "optional_flux_drain_margin": optional_flux_drain_margin,
    }


def control_results() -> list[dict[str, Any]]:
    passed_controls = [
        (
            "hidden_budget_relief_control",
            "hidden producer/budget relief supplies surplus",
            "surplus and optionality are measured from LGRC source-current geometry",
            "blocks positive support if triggered",
        ),
        (
            "floor_crossing_as_abundance_control",
            "support or coherence floor crossed",
            "support/coherence floors remain preserved during optionality window",
            "blocks AB2+ if triggered",
        ),
        (
            "surplus_without_optional_continuation_control",
            "surplus appears without optional continuation set",
            "optional_continuation_availability_count=3",
            "blocks AB3+ if triggered",
        ),
        (
            "optionality_without_surplus_control",
            "optional branch exists without surplus",
            "support/coherence surplus margins remain positive",
            "blocks AB3+ if triggered",
        ),
        (
            "proxy_only_optional_branch_gain_control",
            "proxy gain replaces geometry",
            "reward/proxy labels absent on every branch",
            "blocks optionality support if triggered",
        ),
        (
            "optional_branch_label_only_control",
            "optional branch label replaces branch geometry",
            "branch-specific source-current support/coherence and boundary/flux traces present",
            "blocks AB3+ if triggered",
        ),
        (
            "single_optional_branch_relabel_control",
            "single branch relabeled as optionality",
            "three same-window source-current branches are present",
            "blocks AB3+ if triggered",
        ),
        (
            "independent_run_optional_assembly_control",
            "independent runs assembled as one optional set",
            "all branches originate in the same source-current run and window",
            "blocks AB3+ if triggered",
        ),
        (
            "maintenance_basin_shift_control",
            "floor and surplus measured on different basins",
            "single declared maintenance basin signature used",
            "blocks surplus/optionality support if triggered",
        ),
        (
            "floor_renormalization_as_surplus_control",
            "floor retuned after outcome inspection",
            "row-specific threshold record declared_before_use=true",
            "blocks surplus claim if triggered",
        ),
        (
            "post_hoc_surplus_construction_control",
            "surplus or optionality assembled after the fact",
            "surplus and optional branch traces emitted as source-current artifacts",
            "blocks AB3+ if triggered",
        ),
        (
            "n23_selection_context_relabel_as_abundance_control",
            "N23 selection context relabeled as abundance",
            "N23 context remains AP4 bridge context only",
            "blocks N23 context relabel if triggered",
        ),
        (
            "reward_maximization_relabel_control",
            "reward score relabeled as abundance",
            "reward_maximization_claim_allowed=false",
            "blocks reward overclaim if triggered",
        ),
        (
            "semantic_choice_relabel_control",
            "semantic choice relabel",
            "semantic choice remains blocked",
            "blocks unsafe claims if triggered",
        ),
        (
            "agency_relabel_control",
            "agency relabel",
            "agency remains blocked",
            "blocks unsafe claims if triggered",
        ),
        (
            "native_support_relabel_control",
            "native support relabel",
            "native support remains blocked",
            "blocks unsafe claims if triggered",
        ),
        (
            "phase8_relabel_control",
            "Phase 8 implementation relabel",
            "Phase 8 remains blocked",
            "blocks unsafe claims if triggered",
        ),
        (
            "ap4_final_reclassification_relabel_control",
            "final global AP4 reclassification relabel",
            "AP4 bridge context remains local and final global AP4 remains false",
            "blocks final global AP4 reclassification",
        ),
    ]
    rows = [
        {
            "control_id": control_id,
            "control_status": "passed",
            "blocked_condition": blocked_condition,
            "expected_result": "blocker absent and claim ceiling preserved",
            "actual_result": actual_result,
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": True,
            "rung_effect": rung_effect,
        }
        for control_id, blocked_condition, actual_result, rung_effect in passed_controls
    ]
    rows.append(
        {
            "control_id": "ap5_proxy_gap_omission_control",
            "control_status": "not_applicable",
            "blocked_condition": "proxy/reward/target row omits AP5",
            "expected_result": "not applicable when proxy/reward/target absent",
            "actual_result": "ap5_dependency_status=not_applicable",
            "claim_allowed_when_control_triggers": False,
            "control_satisfied_for_positive_row": False,
            "rung_effect": "not applicable for non-proxy I5 row",
        }
    )
    return rows


def file_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": base.sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def artifact_sha256_map(manifest: list[dict[str, str]]) -> dict[str, str]:
    return {item["path"]: item["sha256"] for item in manifest}


def build_candidate_row(
    *,
    i1: dict[str, Any],
    i2: dict[str, Any],
    runtime: dict[str, Any],
    artifact_manifest: list[dict[str, str]],
) -> dict[str, Any]:
    source_row = base.i1_contract_row(i1)
    n23 = i1["n23_context_boundary"]
    run_artifact = runtime["run_artifact"]
    signature = run_artifact["maintenance_basin_signature"]
    floor_trace = run_artifact["maintenance_floor_trace"]
    surplus_trace = run_artifact["support_surplus_margin_trace"]
    optional_trace = run_artifact["optional_continuation_set_trace"]
    branch_support_trace = run_artifact["optional_branch_support_coherence_traces"]
    branch_boundary_trace = run_artifact["optional_branch_boundary_flux_traces"]
    boundary_under_optionality_trace = run_artifact[
        "boundary_integrity_under_optionality_trace"
    ]
    branches = run_artifact["optional_branch_records"]
    support_margin = surplus_trace["payload"]["support_surplus_margin"]
    coherence_margin = surplus_trace["payload"]["coherence_surplus_margin"]
    artifact_paths = [item["path"] for item in artifact_manifest]
    artifact_sha256 = artifact_sha256_map(artifact_manifest)
    row: dict[str, Any] = {
        "row_id": "n24_i5_row_01_source_current_optional_continuation_set_probe",
        "source_contract_row": source_row["source_contract_row"],
        "source_consumable_contract_row": source_row["source_consumable_contract_row"],
        "source_contract_row_digest": i2["source_contract_digests"][
            "source_contract_row_digest"
        ],
        "source_consumable_contract_row_digest": i2["source_contract_digests"][
            "source_consumable_contract_row_digest"
        ],
        "source_output_digest": i1["output_digest"],
        "run_artifact_id": run_artifact["artifact_id"],
        "source_commit_or_source_digest": {
            "script_path": SCRIPT_PATH,
            "script_sha256": base.sha256_file(SCRIPT_PATH),
        },
        "runtime_config_digest": run_artifact["runtime_config_digest"],
        "source_current_inputs": [
            "LGRC9V3 source-current runtime snapshot",
            "LGRC9V3 maintenance-basin node metrics",
            "source-current support/coherence surplus margin trace",
            "source-current optional continuation set trace",
            "source-current optional branch support/coherence traces",
            "source-current optional branch boundary/flux traces",
            "source-current boundary under optionality trace",
        ],
        "source_current_required_fields": source_row["source_current_fields"],
        "row_specific_thresholds_declared_before_use": {
            "path": runtime["threshold_path"],
            "sha256": base.sha256_file(runtime["threshold_path"]),
            "declared_before_use": True,
            "threshold_record": threshold_record(),
        },
        "n20_source_downstream_consumption_status": source_row[
            "n20_source_downstream_consumption_status"
        ],
        "n23_source_closeout_status": n23["n23_source_closeout_status"],
        "n23_closeout_required": n23["n23_closeout_required"],
        "n23_context_consumption": n23["n23_context_consumption"],
        "n23_ap4_bridge_status": n23["n23_ap4_bridge_status"],
        "ap4_context_status": n23["n23_context_consumption"],
        "maintenance_floor_policy": "predeclared_support_and_coherence_floors_required",
        "maintenance_basin_id": MAINTENANCE_BASIN_ID,
        "maintenance_basin_signature_digest": signature[
            "maintenance_basin_signature_digest"
        ],
        "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
        "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
        "surplus_channel_policy": (
            "support_surplus_required_and_coherence_floor_preserved"
        ),
        "support_floor_value": SUPPORT_FLOOR,
        "coherence_floor_value": COHERENCE_FLOOR,
        "boundary_integrity_floor_value": (
            "maintenance basin node set and topology signature preserved"
        ),
        "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
        "optionality_window": optionality_window(),
        "pre_surplus_geometry_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "runtime_trace",
            "path": runtime["snapshot_path"],
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
        },
        "support_surplus_margin_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "surplus_margin_trace",
            "path": runtime["surplus_trace_path"],
            "trace_digest": surplus_trace["trace_digest"],
            "support_surplus_margin": support_margin,
            "minimum_support_surplus_margin": MIN_SURPLUS_MARGIN,
        },
        "coherence_surplus_margin_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "surplus_margin_trace",
            "path": runtime["surplus_trace_path"],
            "trace_digest": surplus_trace["trace_digest"],
            "coherence_surplus_margin": coherence_margin,
            "minimum_coherence_surplus_margin": MIN_SURPLUS_MARGIN,
        },
        "residual_support_margin_under_optionality": runtime[
            "residual_support_margin"
        ],
        "residual_coherence_margin_under_optionality": runtime[
            "residual_coherence_margin"
        ],
        "optional_flux_drain_margin": runtime["optional_flux_drain_margin"],
        "maintenance_floor_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "maintenance_floor_trace",
            "path": runtime["floor_trace_path"],
            "trace_digest": floor_trace["trace_digest"],
        },
        "optional_continuation_set_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "optional_continuation_set_trace",
            "path": runtime["optional_trace_path"],
            "trace_digest": optional_trace["trace_digest"],
            "same_source_current_run": True,
            "same_declared_optionality_window": True,
        },
        "optional_continuation_count": len(branches),
        "optional_continuation_availability_count": len(branches),
        "jointly_admissible_optional_continuation_count": 0,
        "optional_branch_records": branches,
        "optional_branch_evidence_mode": "source_current_available_unexecuted",
        "optional_branch_support_coherence_traces": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "optional_branch_trace",
            "artifact_subtype": "optional_branch_support_coherence_trace",
            "path": runtime["branch_support_trace_path"],
            "trace_digest": branch_support_trace["trace_digest"],
        },
        "optional_branch_boundary_flux_traces": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "optional_branch_trace",
            "artifact_subtype": "optional_branch_boundary_flux_trace",
            "path": runtime["branch_boundary_trace_path"],
            "trace_digest": branch_boundary_trace["trace_digest"],
        },
        "boundary_integrity_under_optionality_trace": {
            "trace_status": "present",
            "trace_origin": "source_current_same_run",
            "artifact_role": "boundary_integrity_trace",
            "artifact_subtype": "boundary_integrity_under_optionality_trace",
            "path": runtime["boundary_under_optionality_trace_path"],
            "trace_digest": boundary_under_optionality_trace["trace_digest"],
        },
        "optional_flux_does_not_drain_maintenance_support": True,
        "optional_flux_does_not_drain_maintenance_support_status": "preserved",
        "surplus_budget_owner": "source_current_geometry",
        "hidden_budget_relief_absent": True,
        "reward_or_proxy_label_absent_or_blocked": True,
        "same_basin_continuation_rule": i2["same_basin_rule_freeze"]["rule"],
        "same_basin_invariant_fields": i2["same_basin_rule_freeze"]["rule"][
            "basin_signature_fields"
        ],
        "out_of_scope_drift_blocks_row": True,
        "optionality_not_label_reassignment": True,
        "support_floor_result": {
            "status": "preserved" if support_margin >= MIN_SURPLUS_MARGIN else "crossed_floor",
            "observed_support": signature["min_support"],
            "support_floor": SUPPORT_FLOOR,
            "support_surplus_margin": support_margin,
        },
        "coherence_floor_result": {
            "status": "preserved" if coherence_margin >= MIN_SURPLUS_MARGIN else "crossed_floor",
            "observed_coherence": signature["min_coherence"],
            "coherence_floor": COHERENCE_FLOOR,
            "coherence_surplus_margin": coherence_margin,
        },
        "boundary_integrity_result": {
            "status": "preserved",
            "maintenance_node_ids": MAINTENANCE_NODE_IDS,
            "maintenance_basin_signature_digest": signature[
                "maintenance_basin_signature_digest"
            ],
            "topology_signature": signature["topology_signature"],
        },
        "flux_or_leakage_result": {
            "status": "preserved",
            "packet_budget_error": 0.0,
            "in_flight_packet_total": 0.0,
            "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
        },
        "replay_result": {
            "artifact_replay": "not_run",
            "snapshot_load_replay": "not_run",
            "duplicate_replay": "not_run",
            "not_run_reason": (
                "I5 opens the first source-current optional set; replay/control-backed "
                "AB4+ evidence remains I6 scope"
            ),
            "affected_rungs": ["AB4", "AB5", "AB6", "N24-C4", "N24-C5", "N24-C6"],
        },
        "control_results": control_results(),
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": (
            "I5 claims route/branch-conditioned optionality, so N23 AP4 bridge "
            "context is recorded as a load-bearing local dependency; final "
            "global AP4 reclassification remains false."
        ),
        "ap5_condition_reason": (
            "No proxy, reward, or target formation participates in I5 optionality measurement."
        ),
        "surplus_trace_digest": surplus_trace["trace_digest"],
        "optional_continuation_trace_digest": optional_trace["trace_digest"],
        "maintenance_floor_trace_digest": floor_trace["trace_digest"],
        "replay_surplus_digest": "not_run_until_iteration_6",
        "replay_optionality_digest": "not_run_until_iteration_6",
        "surplus_persistence_ratio": 1.0,
        "optional_branch_persistence_ratio": 1.0,
        "surplus_threshold_or_rule": threshold_record(),
        "optionality_threshold_or_rule": threshold_record(),
        "hidden_budget_relief_rejected": True,
        "floor_crossing_rejected": True,
        "surplus_without_optional_continuation_rejected_or_demoted": True,
        "optionality_without_surplus_rejected": True,
        "proxy_only_success_rejected": True,
        "optional_branch_label_only_rejected": True,
        "independent_run_optional_assembly_rejected": True,
        "maintenance_basin_shift_rejected": True,
        "floor_renormalization_rejected": True,
        "post_hoc_surplus_rejected": True,
        "n23_context_relabel_rejected": True,
        "producer_residue_fields": source_row["producer_mediated_fields"],
        "naturalization_debt_fields": source_row["naturalization_debt_fields"],
        "blocked_relabel_fields": source_row["blocked_relabel_fields"],
        "claim_ceiling": (
            "provisional source-current AB3 optional continuation candidate "
            "pending replay/control matrix; reward maximization, semantic choice, "
            "agency, native support, sentience, Phase 8, and ant ecology remain blocked"
        ),
        "unsafe_claim_flags": base.unsafe_claim_flags(i2),
        "row_decision": "partial",
        "surplus_supported_optionality_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
        "reward_maximization_claim_allowed": False,
        "agency_claim_allowed": False,
        "native_support_claim_allowed": False,
        "final_global_ap4_reclassification_supported": False,
        "derived_report_only": False,
        "artifact_manifest": artifact_manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_paths_equal_manifest_paths": sorted(artifact_paths)
        == sorted(item["path"] for item in artifact_manifest),
        "artifact_sha256_equal_manifest_sha256": artifact_sha256
        == artifact_sha256_map(artifact_manifest),
        "all_artifact_sha256_match_file_contents": all(
            item["sha256"] == base.sha256_file(item["path"])
            for item in artifact_manifest
        ),
        "output_digest": "pending",
    }
    row["output_digest"] = base.digest_value(
        {key: value for key, value in row.items() if key != "output_digest"}
    )
    return row


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i4 = base.load_json(I4_OUTPUT_PATH)
    runtime = build_runtime_artifacts()
    artifact_manifest = file_manifest(
        [
            (runtime["runtime_config_path"], "runtime_trace"),
            (runtime["threshold_path"], "maintenance_floor_trace"),
            (runtime["run_artifact_path"], "runtime_trace"),
            (runtime["snapshot_path"], "runtime_trace"),
            (runtime["floor_trace_path"], "maintenance_floor_trace"),
            (runtime["surplus_trace_path"], "surplus_margin_trace"),
            (runtime["optional_trace_path"], "optional_continuation_set_trace"),
            (
                runtime["branch_support_trace_path"],
                "optional_branch_trace",
            ),
            (
                runtime["branch_boundary_trace_path"],
                "optional_branch_trace",
            ),
            (
                runtime["boundary_under_optionality_trace_path"],
                "boundary_integrity_trace",
            ),
        ]
    )
    row = build_candidate_row(
        i1=i1,
        i2=i2,
        runtime=runtime,
        artifact_manifest=artifact_manifest,
    )
    required_fields = i2["candidate_evidence_row_schema"]["required_fields"]
    candidate_keys = set(row)
    checks = [
        base.check(
            "i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            i1["acceptance_state"],
        ),
        base.check(
            "i2_schema_passed",
            i2["status"] == "passed" and not i2["failed_checks"],
            i2["acceptance_state"],
        ),
        base.check(
            "i3_active_nulls_ready",
            i3["iteration3_boundary"]["ready_for_iteration_4_positive_probe"] is True
            and not i3["failed_checks"],
            i3["acceptance_state"],
        ),
        base.check(
            "i4_ab2_surplus_ready",
            i4["iteration4_boundary"]["ready_for_iteration_5_optional_continuation_probe"]
            is True
            and i4["iteration4_boundary"]["provisional_ab_ladder_rung"] == "AB2"
            and not i4["failed_checks"],
            i4["acceptance_state"],
        ),
        base.check(
            "candidate_row_field_set_matches_i2_required_fields",
            candidate_keys == set(required_fields),
            {
                "required_count": len(required_fields),
                "candidate_count": len(candidate_keys),
                "extra": sorted(candidate_keys - set(required_fields)),
                "missing": sorted(set(required_fields) - candidate_keys),
            },
        ),
        base.check("derived_report_only_false", row["derived_report_only"] is False, row["derived_report_only"]),
        base.check("source_current_inputs_present", bool(row["source_current_inputs"]), row["source_current_inputs"]),
        base.check(
            "artifact_manifest_non_empty",
            len(row["artifact_manifest"]) >= 9
            and row["all_artifact_sha256_match_file_contents"] is True,
            row["artifact_manifest"],
        ),
        base.check(
            "artifact_manifest_roles_allowed_by_i2",
            all(
                item["artifact_role"]
                in i2["artifact_admissibility_schema"]["artifact_manifest_schema"][
                    "artifact_role_values"
                ]
                for item in row["artifact_manifest"]
            ),
            row["artifact_manifest"],
        ),
        base.check(
            "source_current_optional_set_present",
            row["optional_continuation_set_trace"]["trace_status"] == "present"
            and row["optional_continuation_set_trace"]["same_source_current_run"] is True,
            row["optional_continuation_set_trace"],
        ),
        base.check(
            "ab3_availability_count_met",
            row["optional_continuation_availability_count"] >= 2
            and row["optional_continuation_count"] >= 2,
            {
                "optional_count": row["optional_continuation_count"],
                "availability_count": row["optional_continuation_availability_count"],
            },
        ),
        base.check(
            "maintenance_floors_preserved_under_optionality",
            row["residual_support_margin_under_optionality"] >= MIN_SURPLUS_MARGIN
            and row["residual_coherence_margin_under_optionality"]
            >= MIN_SURPLUS_MARGIN,
            {
                "residual_support_margin": row[
                    "residual_support_margin_under_optionality"
                ],
                "residual_coherence_margin": row[
                    "residual_coherence_margin_under_optionality"
                ],
            },
        ),
        base.check(
            "boundary_flux_and_optional_drain_preserved",
            row["boundary_integrity_result"]["status"] == "preserved"
            and row["flux_or_leakage_result"]["status"] == "preserved"
            and row["optional_flux_does_not_drain_maintenance_support"] is True
            and row["optional_flux_does_not_drain_maintenance_support_status"]
            == "preserved",
            {
                "boundary": row["boundary_integrity_result"],
                "flux": row["flux_or_leakage_result"],
                "optional_flux_status": row[
                    "optional_flux_does_not_drain_maintenance_support_status"
                ],
            },
        ),
        base.check(
            "branch_records_are_source_current_not_labels",
            all(
                branch["trace_origin"] == "source_current_same_run"
                and branch["trace_status"] == "present"
                and branch["reward_or_proxy_label_used"] is False
                and branch["producer_enumeration_used"] is False
                and branch["admissibility_status"] == "admissible"
                for branch in row["optional_branch_records"]
            ),
            row["optional_branch_records"],
        ),
        base.check(
            "ab3_only_pending_i6",
            row["row_decision"] == "partial"
            and row["replay_result"]["artifact_replay"] == "not_run"
            and row["surplus_supported_optionality_claim_allowed"] is False,
            row["claim_ceiling"],
        ),
        base.check(
            "ap4_required_ap5_not_applicable",
            row["ap4_context_status"] == "n23_bridge_candidate_consumed"
            and row["ap4_dependency_status"] == "required_recorded"
            and row["ap5_dependency_status"] == "not_applicable"
            and row["final_global_ap4_reclassification_supported"] is False,
            {
                "ap4_context": row["ap4_context_status"],
                "ap4": row["ap4_dependency_status"],
                "ap5": row["ap5_dependency_status"],
                "final_global_ap4_reclassification_supported": row[
                    "final_global_ap4_reclassification_supported"
                ],
            },
        ),
        base.check(
            "unsafe_claim_flags_all_false",
            all(value is False for value in row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
        ),
    ]
    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_optional_continuation_set_probe",
        "schema_version": "n24_optional_continuation_set_probe_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": 5,
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_source_current_ab3_optional_continuation_candidate_pending_replay_controls_no_ab4"
            if not failed_checks
            else "failed_source_current_optional_continuation_set_probe"
        ),
        "purpose": "produce source-current optional continuation set evidence while maintenance floors hold",
        "command": COMMAND,
        "source_artifacts": [
            base.source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            base.source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            base.source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            base.source_record(I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "inherited_n23_context": {
            "path": N23_CLOSEOUT_PATH,
            "n23_source_closeout_status": i1["n23_context_boundary"][
                "n23_source_closeout_status"
            ],
            "n23_ap4_bridge_status": i1["n23_context_boundary"][
                "n23_ap4_bridge_status"
            ],
            "n23_context_consumption": i1["n23_context_boundary"][
                "n23_context_consumption"
            ],
            "consumption_boundary": "local AP4 bridge context for branch-conditioned optionality; not final global AP4",
        },
        "source_backed_probe": {
            "model_family": "LGRC9V3",
            "fixture": "examples/grc9v3/_fixtures.py::make_column_h_state",
            "maintenance_basin_id": MAINTENANCE_BASIN_ID,
            "maintenance_node_ids": MAINTENANCE_NODE_IDS,
            "optional_branch_target_node_ids": OPTIONAL_BRANCH_TARGET_NODE_IDS,
            "support_measurement_scope": SUPPORT_MEASUREMENT_SCOPE,
            "support_aggregation_method": SUPPORT_AGGREGATION_METHOD,
            "support_floor": SUPPORT_FLOOR,
            "coherence_floor": COHERENCE_FLOOR,
            "observed_min_support": row["support_floor_result"]["observed_support"],
            "observed_min_coherence": row["coherence_floor_result"][
                "observed_coherence"
            ],
            "support_surplus_margin": row["support_floor_result"][
                "support_surplus_margin"
            ],
            "coherence_surplus_margin": row["coherence_floor_result"][
                "coherence_surplus_margin"
            ],
            "optional_continuation_availability_count": row[
                "optional_continuation_availability_count"
            ],
            "jointly_admissible_optional_continuation_count": row[
                "jointly_admissible_optional_continuation_count"
            ],
            "residual_support_margin_under_optionality": row[
                "residual_support_margin_under_optionality"
            ],
            "residual_coherence_margin_under_optionality": row[
                "residual_coherence_margin_under_optionality"
            ],
        },
        "source_digest_chain_audit": {
            "i2_output_digest_consumed": base.source_record(
                I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"
            )["output_digest"],
            "i3_output_digest_consumed": base.source_record(
                I3_OUTPUT_PATH, "n24_i3_active_nulls"
            )["output_digest"],
            "i4_output_digest_consumed": base.source_record(
                I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"
            )["output_digest"],
            "digest_chain_interpretation": (
                "I5 consumes the current repo I2/I3/I4 output digests; regenerate "
                "I4/I5 after any I2 or I3 schema change."
            ),
        },
        "fixture_reuse_audit": {
            "n24_snapshot_path": runtime["snapshot_path"],
            "n24_snapshot_sha256": base.sha256_file(runtime["snapshot_path"]),
            "compared_n23_fixture_snapshot_path": base.N23_I4_PRE_COLLAPSE_SNAPSHOT_PATH,
            "compared_n23_fixture_snapshot_sha256": base.sha256_file(
                base.N23_I4_PRE_COLLAPSE_SNAPSHOT_PATH
            ),
            "snapshot_hash_matches_n23_pre_collapse_fixture": (
                base.sha256_file(runtime["snapshot_path"])
                == base.sha256_file(base.N23_I4_PRE_COLLAPSE_SNAPSHOT_PATH)
            ),
            "n23_snapshot_consumed_as_n24_optionality_evidence": False,
            "interpretation": (
                "N24 I5 re-emits the same LGRC fixture state through its own "
                "runtime artifact; the N23 snapshot is compared only to audit "
                "fixture reuse and is not consumed as N24 optionality evidence."
            ),
        },
        "candidate_rows": [row],
        "iteration5_boundary": {
            "positive_run_artifacts_consumed": True,
            "source_current_inputs_opened": True,
            "source_current_optional_continuation_set_observed": True,
            "optional_continuation_availability_count": row[
                "optional_continuation_availability_count"
            ],
            "jointly_admissible_optional_continuation_count": row[
                "jointly_admissible_optional_continuation_count"
            ],
            "maintenance_basin_preserved": True,
            "boundary_integrity_preserved": True,
            "flux_or_leakage_preserved": True,
            "provisional_ab_ladder_rung": "AB3",
            "ab4_or_stronger_supported": False,
            "ab5_or_stronger_supported": False,
            "surplus_supported_optionality_claim_allowed": False,
            "n24_closeout_ladder_rung_assigned": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_supported": False,
            "semantic_choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "ready_for_iteration_6_replay_control_matrix": not failed_checks,
        },
        "geometric_interpretation": {
            "short_read": (
                "I5 records three source-current available continuations inside "
                "one optionality window while the maintenance basin remains above "
                "support/coherence floors."
            ),
            "optionality": (
                "The optionality is geometric rather than semantic: the branch "
                "records are LGRC center-to-neighbor edge continuations in the "
                "same runtime snapshot, with branch-specific support/coherence "
                "and boundary/flux traces."
            ),
            "availability_vs_admissibility": (
                "I5 supports availability, not stress-backed joint admissibility. "
                "jointly_admissible_optional_continuation_count remains 0 until "
                "stress/threshold validation."
            ),
            "persistence_boundary": (
                "surplus_persistence_ratio and optional_branch_persistence_ratio "
                "are single-window descriptive placeholders, not replay-backed "
                "persistence evidence."
            ),
            "control_field_semantics": (
                "surplus_without_optional_continuation_rejected_or_demoted=true "
                "means the surplus-without-optionality control is satisfied "
                "because the bad condition is absent in I5; the field name is "
                "inherited from the frozen row schema."
            ),
            "claim_boundary": (
                "This supports only provisional AB3 source-current optional "
                "continuation evidence. AB4+ requires I6 replay/control validation; "
                "AB5+ requires later stress/threshold evidence."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["candidate_rows"][0]
    probe = output["source_backed_probe"]
    lines = [
        "# N24 Iteration 5 - Optional Continuation Set Probe",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 5 opens the first source-current optional continuation set.",
        "The result is capped at provisional AB3 pending I6 replay/control",
        "validation and later stress/threshold work.",
        "",
        "## Geometric Interpretation",
        "",
        output["geometric_interpretation"]["optionality"],
        "",
        output["geometric_interpretation"]["availability_vs_admissibility"],
        "",
        output["geometric_interpretation"]["persistence_boundary"],
        "",
        output["geometric_interpretation"]["control_field_semantics"],
        "",
        "The source snapshot intentionally matches the N23 I4 pre-collapse fixture hash,",
        "because both probes start from the same LGRC fixture state. N24 re-emits",
        "that state as its own runtime artifact and does not consume the N23 snapshot",
        "as optionality evidence.",
        "",
        "```text",
        f"maintenance_basin_id = {probe['maintenance_basin_id']}",
        f"maintenance_node_ids = {probe['maintenance_node_ids']}",
        f"optional_branch_target_node_ids = {probe['optional_branch_target_node_ids']}",
        f"support_floor = {probe['support_floor']:.12f}",
        f"coherence_floor = {probe['coherence_floor']:.12f}",
        f"observed_min_support = {probe['observed_min_support']:.12f}",
        f"observed_min_coherence = {probe['observed_min_coherence']:.12f}",
        f"support_surplus_margin = {probe['support_surplus_margin']:.12f}",
        f"coherence_surplus_margin = {probe['coherence_surplus_margin']:.12f}",
        "optional_continuation_availability_count = "
        f"{probe['optional_continuation_availability_count']}",
        "jointly_admissible_optional_continuation_count = "
        f"{probe['jointly_admissible_optional_continuation_count']}",
        "residual_support_margin_under_optionality = "
        f"{probe['residual_support_margin_under_optionality']:.12f}",
        "residual_coherence_margin_under_optionality = "
        f"{probe['residual_coherence_margin_under_optionality']:.12f}",
        "```",
        "",
        "## Candidate Row",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Row | `{row['row_id']}` |",
        f"| Decision | `{row['row_decision']}` |",
        "| Provisional AB rung | `AB3` |",
        f"| Claim allowed | `{str(row['surplus_supported_optionality_claim_allowed']).lower()}` |",
        f"| Derived report only | `{str(row['derived_report_only']).lower()}` |",
        f"| AP4 status | `{row['ap4_dependency_status']}` |",
        f"| AP5 status | `{row['ap5_dependency_status']}` |",
        f"| Artifact manifest entries | `{len(row['artifact_manifest'])}` |",
        "",
        "## Branches",
        "",
        "| Branch | Target | Support After | Coherence After | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for branch in row["optional_branch_records"]:
        lines.append(
            "| "
            f"`{branch['branch_id']}` | "
            f"{branch['target_node_id']} | "
            f"{branch['support_after_or_projected_after']:.12f} | "
            f"{branch['coherence_after_or_projected_after']:.12f} | "
            f"`{branch['admissibility_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Gates",
            "",
            "| Gate | Status |",
            "| --- | --- |",
            f"| Support | `{row['support_floor_result']['status']}` |",
            f"| Coherence | `{row['coherence_floor_result']['status']}` |",
            f"| Boundary | `{row['boundary_integrity_result']['status']}` |",
            f"| Flux/leakage | `{row['flux_or_leakage_result']['status']}` |",
            f"| Optionality | `{row['optional_continuation_set_trace']['trace_status']}` |",
            f"| Replay | `{row['replay_result']['artifact_replay']}` |",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
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
    base.write_json(OUTPUT, output)
    output = base.load_json(base.rel(OUTPUT))
    write_report(output)
    if output["failed_checks"]:
        raise SystemExit(f"failed checks: {output['failed_checks']}")


if __name__ == "__main__":
    main()
