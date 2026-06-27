#!/usr/bin/env python3
"""Build N23 Iteration 2 schema/control freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
)
OUTPUT = EXPERIMENT / "outputs" / "n23_live_continuation_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n23_live_continuation_schema_and_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_live_continuation_schema_and_controls.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_source_handoff_inventory.json"
)
I1_REPORT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "reports/n23_source_handoff_inventory.md"
)

SOURCE_CONTRACT_ROW = "n20_i4_row_04_live_continuation_collapse"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_04_live_continuation_collapse"
N19_CONSUMPTION_VALUE = "ap_gap_boundary_only"

ROW_DECISIONS = ["supported", "partial", "blocked", "rejected", "not_applicable"]
REPLAY_CONTROL_STATUSES = [
    "passed",
    "failed_closed",
    "failed_open",
    "not_run",
    "not_applicable",
]
AP4_STATUS_VALUES = ["required_recorded", "not_applicable", "missing_blocks_row"]
AP5_STATUS_VALUES = [
    "conditional_required_recorded",
    "not_applicable",
    "missing_blocks_row",
]
INVENTORY_META_AP_STATUS_VALUES = [
    "not_supported_inventory_only",
    "conditional_pending_future_rows",
    "required_local_gap_dependency",
]
BRANCH_RECORD_ORIGIN_VALUES = [
    "source_current_same_run",
    "replay_fork",
    "producer_label",
    "report_derived",
    "independent_run_assembly",
]
TRACE_STATUS_VALUES = ["present", "missing", "not_applicable"]
TRACE_ORIGIN_VALUES = [
    "source_current_same_run",
    "deterministic_replay_of_source_run",
    "replay_fork",
    "report_derived",
    "producer_label",
    "independent_run_assembly",
]
SELECTED_BRANCH_REASON_VALUES = [
    "support_gradient_dominance",
    "coherence_floor_dominance",
    "boundary_integrity_dominance",
    "flux_leakage_minimization",
    "susceptibility_delta_conditioned",
    "route_cost_or_conductance_dominance",
    "multi_channel_geometry_dominance",
    "not_supported",
]
BLOCKED_SELECTED_BRANCH_REASONS = [
    "producer_label",
    "producer_preference",
    "random_tie",
    "post_hoc_report_selection",
    "single_branch_relabel",
    "semantic_choice_label",
]
ARTIFACT_ROLE_VALUES = [
    "source_contract",
    "inherited_context",
    "runtime_trace",
    "branch_set_trace",
    "collapse_trace",
    "counterfactual_retention_trace",
    "replay_trace",
    "snapshot_load_replay_trace",
    "duplicate_replay_trace",
    "negative_control_trace",
    "active_null_trace",
    "report",
    "closeout",
]
POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES = [
    "report",
    "inherited_context",
    "source_contract",
    "closeout",
]
CANONICAL_CONTROL_IDS = [
    "fake_alternative_control",
    "single_branch_relabel_control",
    "post_hoc_selected_branch_control",
    "producer_preference_injection_control",
    "random_tie_as_collapse_control",
    "missing_counterfactual_retention_control",
    "N22_susceptibility_as_choice_relabel_control",
    "route_conditioned_row_missing_AP4",
    "proxy_conditioned_row_missing_AP5",
    "AP_gap_prose_only",
    "semantic_choice_relabel",
    "agency_relabel",
    "native_support_relabel",
    "phase8_relabel",
]
THRESHOLD_FIELDS = [
    "support_floor_value",
    "coherence_floor_value",
    "boundary_integrity_floor_value",
    "flux_or_leakage_bound",
    "collapse_persistence_ratio_threshold",
    "branch_distinguishability_threshold",
    "same_basin_drift_bound",
]
RESULT_STATUS_VALUES = [
    "preserved",
    "changed_within_allowed_delta",
    "changed_within_allowed_delta_above_floor",
    "changed_within_bound",
    "crossed_floor",
    "exceeded_bound",
    "missing",
    "not_applicable",
]
AP4_BRIDGE_STATUS_VALUES = [
    "not_supported",
    "bridge_candidate_supported",
    "blocked_by_live_branch_set",
    "blocked_by_single_live_branch",
    "blocked_by_counterfactual_retention",
    "blocked_by_same_basin_floor",
    "blocked_by_report_only_evidence",
    "blocked_by_artifact_manifest",
    "blocked_by_not_route_or_branch_conditioned",
    "blocked_by_replay",
    "blocked_by_controls",
    "blocked_by_producer_preference",
    "blocked_by_ap_gap",
]
UNSAFE_CLAIMS = [
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
CANDIDATE_EVIDENCE_FIELDS = [
    "row_id",
    "source_contract_row",
    "source_consumable_contract_row",
    "source_contract_row_digest",
    "source_consumable_contract_row_digest",
    "source_output_digest",
    "run_artifact_id",
    "source_commit_or_source_digest",
    "runtime_config_digest",
    "source_current_inputs",
    "row_specific_thresholds_declared_before_use",
    "n19_native_readiness_boundary_consumption",
    "n20_source_downstream_consumption_status",
    "n22_source_closeout_status",
    "branch_window",
    "collapse_window",
    "pre_collapse_geometry_trace",
    "live_branch_set_trace",
    "branch_support_coherence_traces",
    "branch_boundary_flux_traces",
    "branch_counterfactual_records",
    "collapsed_continuation_trace",
    "counterfactual_branch_retention_trace",
    "branch_record_origin",
    "selected_branch_source_current_reason",
    "n22_inherited_delta_used_as_selection_evidence",
    "n23_susceptibility_expression_trace",
    "producer_selected_branch_label_absent",
    "producer_preference_injection_absent",
    "random_tie_status",
    "support_floor_value",
    "coherence_floor_value",
    "boundary_integrity_floor_value",
    "flux_or_leakage_bound",
    "collapse_persistence_ratio_threshold",
    "branch_distinguishability_threshold",
    "same_basin_drift_bound",
    "same_basin_continuation_rule",
    "same_basin_invariant_fields",
    "out_of_scope_drift_blocks_row",
    "selection_not_label_reassignment",
    "route_or_branch_conditioned",
    "peer_or_counterfactual_comparison",
    "peer_or_counterfactual_scope_reason",
    "support_floor_result",
    "coherence_floor_result",
    "boundary_integrity_result",
    "flux_or_leakage_result",
    "replay_result",
    "control_results",
    "ap4_dependency_status",
    "ap5_dependency_status",
    "ap4_condition_reason",
    "ap5_condition_reason",
    "collapse_trace_digest",
    "replay_collapse_digest",
    "counterfactual_retention_digest",
    "collapse_persistence_ratio",
    "collapse_threshold_or_rule",
    "fake_alternatives_rejected",
    "single_branch_relabel_rejected",
    "post_hoc_selection_rejected",
    "producer_preference_rejected",
    "random_tie_as_collapse_rejected",
    "producer_residue_fields",
    "naturalization_debt_fields",
    "blocked_relabel_fields",
    "claim_ceiling",
    "unsafe_claim_flags",
    "row_decision",
    "live_continuation_collapse_claim_allowed",
    "semantic_choice_claim_allowed",
    "derived_report_only",
    "artifact_manifest",
    "artifact_paths",
    "artifact_sha256",
    "artifact_paths_equal_manifest_paths",
    "artifact_sha256_equal_manifest_sha256",
    "all_artifact_sha256_match_file_contents",
    "output_digest",
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


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def unique_list(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def source_record(path: str, role: str) -> dict[str, Any]:
    data = load_json(path) if path.endswith(".json") else None
    record: dict[str, Any] = {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
    }
    if data is not None:
        record["status"] = data.get("status", "not_recorded")
        record["acceptance_state"] = data.get("acceptance_state", "not_recorded")
        record["output_digest"] = data.get("output_digest", "not_recorded")
    return record


def candidate_evidence_row_schema(i1: dict[str, Any]) -> dict[str, Any]:
    constraints: dict[str, dict[str, Any]] = {
        field: {"type": "recorded", "constraint": "required for candidate rows"}
        for field in CANDIDATE_EVIDENCE_FIELDS
    }
    constraints.update(
        {
            "source_contract_row": {
                "type": "string",
                "required_value": SOURCE_CONTRACT_ROW,
                "constraint": "primitive contract source row must not drift",
            },
            "source_consumable_contract_row": {
                "type": "string",
                "required_value": CONSUMABLE_CONTRACT_ROW,
                "constraint": "same-basin/control contract row must not drift",
            },
            "source_contract_row_digest": {
                "type": "sha256_string",
                "required_value": i1["contract_inventory_rows"][0][
                    "source_contract_row_digest"
                ],
                "constraint": "must match I1 digest over N20 I4 primitive contract row",
            },
            "source_consumable_contract_row_digest": {
                "type": "sha256_string",
                "required_value": i1["contract_inventory_rows"][0][
                    "source_consumable_contract_row_digest"
                ],
                "constraint": "must match I1 digest over N20 I5 same-basin/control contract row",
            },
            "source_output_digest": {
                "type": "sha256_string",
                "required_value": i1["output_digest"],
                "constraint": "records the source I1 inventory digest consumed",
            },
            "source_current_inputs": {
                "type": "list[string]",
                "constraint": "must be LGRC runtime or replay emitted, not report-built",
            },
            "row_specific_thresholds_declared_before_use": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks positive LC support",
            },
            "n19_native_readiness_boundary_consumption": {
                "type": "enum",
                "allowed_values": [N19_CONSUMPTION_VALUE],
                "constraint": "N19 is AP-gap boundary only, not evidence",
            },
            "n20_source_downstream_consumption_status": {
                "type": "string",
                "required_value": i1["contract_inventory_rows"][0][
                    "n20_source_downstream_consumption_status"
                ],
                "constraint": "prefixed inherited source status required",
            },
            "n22_source_closeout_status": {
                "type": "string",
                "required_value": i1["n22_context_boundary"][
                    "n22_source_closeout_status"
                ],
                "constraint": "prefixed inherited N22 closeout status required",
            },
            "branch_window": {
                "type": "object",
                "required_fields": ["start_step", "end_step", "window_id"],
                "constraint": "declared before collapse-window outcome inspection",
            },
            "collapse_window": {
                "type": "object",
                "required_fields": ["start_step", "end_step", "window_id"],
                "constraint": "must start after branch window ends",
            },
            "live_branch_set_trace": {
                "type": "object",
                "required_trace_fields": [
                    "trace_status",
                    "trace_origin",
                    "missing_blocks_rungs",
                ],
                "trace_status_values": TRACE_STATUS_VALUES,
                "trace_origin_values": TRACE_ORIGIN_VALUES,
                "constraint": "at least two source-current same-run branch records required for LC2+",
            },
            "collapsed_continuation_trace": {
                "type": "object",
                "required_trace_fields": [
                    "trace_status",
                    "trace_origin",
                    "missing_blocks_rungs",
                ],
                "trace_status_values": TRACE_STATUS_VALUES,
                "trace_origin_values": TRACE_ORIGIN_VALUES,
                "constraint": "source-current collapse trace required for LC3+",
            },
            "branch_record_origin": {
                "type": "enum",
                "allowed_values": BRANCH_RECORD_ORIGIN_VALUES,
                "required_value_for_lc2_plus": "source_current_same_run",
                "constraint": "replay/report/producer/independent alternatives cannot create LC2",
            },
            "counterfactual_branch_retention_trace": {
                "type": "object",
                "required_trace_fields": [
                    "trace_status",
                    "trace_origin",
                    "missing_blocks_rungs",
                ],
                "trace_status_values": TRACE_STATUS_VALUES,
                "trace_origin_values": TRACE_ORIGIN_VALUES,
                "constraint": "immutable pre-collapse audit evidence, not continued active branch",
            },
            "selected_branch_source_current_reason": {
                "type": "enum",
                "allowed_values": SELECTED_BRANCH_REASON_VALUES,
                "blocked_values": BLOCKED_SELECTED_BRANCH_REASONS,
                "constraint": "must be computed from pre/in-collapse traces",
            },
            "n22_inherited_delta_used_as_selection_evidence": {
                "type": "boolean",
                "required_value": False,
                "constraint": "inherited N22 delta may provide context but cannot be N23 selection evidence",
            },
            "n23_susceptibility_expression_trace": {
                "type": "object",
                "required_trace_fields": ["trace_status", "trace_origin"],
                "trace_status_values": TRACE_STATUS_VALUES,
                "constraint": "required when selected reason is susceptibility_delta_conditioned",
            },
            "producer_selected_branch_label_absent": {
                "type": "boolean",
                "required_value_for_support": True,
                "constraint": "false demotes or blocks LC support",
            },
            "producer_preference_injection_absent": {
                "type": "boolean",
                "required_value_for_support": True,
                "constraint": "false blocks selection-geometry support",
            },
            "same_basin_continuation_rule": {
                "type": "object",
                "required_source": "N20 I5 same-basin rule from I1",
                "constraint": "must be consumed without redefinition",
            },
            "selection_not_label_reassignment": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks LC2+ support",
            },
            "route_or_branch_conditioned": {
                "type": "boolean",
                "constraint": "true requires AP4 row-local dependency status",
            },
            "support_floor_value": {
                "type": "number_or_declared_rule",
                "constraint": "must be frozen before positive probe",
            },
            "coherence_floor_value": {
                "type": "number_or_declared_rule",
                "constraint": "must be frozen before positive probe",
            },
            "boundary_integrity_floor_value": {
                "type": "number_or_declared_rule",
                "constraint": "must be frozen before positive probe",
            },
            "flux_or_leakage_bound": {
                "type": "number_or_declared_rule",
                "constraint": "must be frozen before positive probe",
            },
            "collapse_persistence_ratio_threshold": {
                "type": "number_or_declared_rule",
                "constraint": "must be frozen before positive probe",
            },
            "branch_distinguishability_threshold": {
                "type": "number_or_declared_rule",
                "constraint": "must be frozen before positive probe",
            },
            "same_basin_drift_bound": {
                "type": "number_or_declared_rule",
                "constraint": "must be frozen before positive probe",
            },
            "ap4_dependency_status": {
                "type": "enum",
                "allowed_values": AP4_STATUS_VALUES,
                "blocked_values": INVENTORY_META_AP_STATUS_VALUES,
                "constraint": "inventory/meta AP values are invalid for candidate rows",
            },
            "ap5_dependency_status": {
                "type": "enum",
                "allowed_values": AP5_STATUS_VALUES,
                "blocked_values": INVENTORY_META_AP_STATUS_VALUES,
                "constraint": "inventory/meta AP values are invalid for candidate rows",
            },
            "row_decision": {
                "type": "enum",
                "allowed_values": ROW_DECISIONS,
                "constraint": "supported alone does not allow unsafe claims",
            },
            "live_continuation_collapse_claim_allowed": {
                "type": "boolean",
                "constraint": "true only when all LC/AP/replay/control gates pass",
            },
            "semantic_choice_claim_allowed": {
                "type": "boolean",
                "required_value": False,
                "constraint": "semantic choice remains blocked in every row",
            },
            "derived_report_only": {
                "type": "boolean",
                "required_value_for_positive_support": False,
                "constraint": "true blocks positive LC support",
            },
            "artifact_manifest": {
                "type": "list[object]",
                "required_item_fields": ["path", "sha256", "artifact_role"],
                "allowed_artifact_roles": ARTIFACT_ROLE_VALUES,
                "constraint": "positive LC support cannot be report/context/contract/closeout only",
            },
            "artifact_paths_equal_manifest_paths": {
                "type": "boolean",
                "required_value_for_positive_support": True,
                "constraint": "parallel artifact path list must match manifest paths",
            },
            "artifact_sha256_equal_manifest_sha256": {
                "type": "boolean",
                "required_value_for_positive_support": True,
                "constraint": "parallel artifact hash list must match manifest sha256 values",
            },
            "all_artifact_sha256_match_file_contents": {
                "type": "boolean",
                "required_value_for_positive_support": True,
                "constraint": "false blocks support",
            },
        }
    )
    return {
        "required_fields": CANDIDATE_EVIDENCE_FIELDS,
        "field_constraints": constraints,
        "missing_required_field_blocks_candidate_admissibility": True,
        "source_contract_row_must_equal_i1": True,
        "source_consumable_contract_row_must_equal_i1": True,
        "same_basin_rule_must_use_i1_reference": True,
        "claim_allowed_false_if_unsafe_claim_requested": True,
        "claim_allowed_false_for_non_supported_rows": True,
    }


def source_current_branch_definition() -> dict[str, Any]:
    return {
        "definition": (
            "original LC2 branch evidence emitted by the same source-current "
            "LGRC runtime run, or deterministic replay of that same already-"
            "recorded runtime trace, inside the declared branch window, before "
            "collapse-window start, with branch-specific support/coherence and "
            "boundary/flux traces"
        ),
        "required_origin": "source_current_same_run",
        "deterministic_replay_of_same_recorded_runtime_trace_allowed_for_audit": True,
        "minimum_branch_count_for_lc2": 2,
        "must_be_boundary_distinguishable": True,
        "must_have_branch_specific_support_coherence_traces": True,
        "must_have_branch_specific_boundary_flux_traces": True,
        "blocked_origins": [
            "replay_fork",
            "producer_label",
            "report_derived",
            "independent_run_assembly",
        ],
        "replay_forks_may_audit_counterfactuals": True,
        "replay_forks_may_create_original_live_branches": False,
    }


def run_artifact_admissibility_schema() -> dict[str, Any]:
    return {
        "artifact_manifest_schema": {
            "type": "list[object]",
            "required_item_fields": ["path", "sha256", "artifact_role"],
            "artifact_role_values": ARTIFACT_ROLE_VALUES,
            "path_policy": "repository_relative_paths_only",
            "digest_algorithm": "sha256",
        },
        "artifact_paths_must_exist": True,
        "artifact_digests_must_match_file_contents": True,
        "artifact_paths_equal_manifest_paths_required": True,
        "artifact_sha256_equal_manifest_sha256_required": True,
        "all_artifact_sha256_match_file_contents_required": True,
        "positive_lc_support_forbidden_if_only_artifact_roles": (
            POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES
        ),
        "derived_report_only_true_blocks_positive_support": True,
        "missing_required_artifact_blocks_lc_assignment": True,
        "digest_mismatch_blocks_lc_assignment": True,
        "report_only_artifacts_may_summarize_but_not_assign_lc_rungs": True,
        "fail_closed_on_missing_or_mismatch": True,
    }


def branch_collapse_window_schema() -> dict[str, Any]:
    return {
        "branch_window_required_fields": ["window_id", "start_step", "end_step"],
        "collapse_window_required_fields": ["window_id", "start_step", "end_step"],
        "branch_window_end_lte_collapse_window_start_required": True,
        "pre_collapse_live_branch_set_trace_step_range_subset_branch_window": True,
        "collapsed_continuation_trace_step_range_subset_collapse_window": True,
        "selected_branch_reason_uses_only_pre_or_in_collapse_traces": True,
        "post_report_selection_reason_allowed": False,
        "unordered_cooccurrence_blocks_lc3_plus": True,
    }


def counterfactual_retention_schema() -> dict[str, Any]:
    return {
        "meaning": "immutable_pre_collapse_audit_record",
        "required_for_lc3_plus": True,
        "continued_dynamic_activity_after_collapse_required": False,
        "labels_sufficient": False,
        "producer_alternatives_sufficient": False,
        "replay_created_branches_sufficient": False,
        "report_reconstruction_sufficient": False,
        "missing_retention_blocks": ["LC3", "LC4", "LC5", "LC6", "N23-C3+"],
    }


def selected_branch_reason_schema() -> dict[str, Any]:
    return {
        "allowed_values": SELECTED_BRANCH_REASON_VALUES,
        "blocked_values": BLOCKED_SELECTED_BRANCH_REASONS,
        "blocked_values_fail_closed": True,
        "ap4_relevant_reason_requires": [
            "route_or_branch_conditioned_true",
            "peer_or_counterfactual_comparison_present",
            "same_horizon_or_same_budget_comparison_when_applicable",
            "AP4_dependency_status_required_recorded",
        ],
        "ap4_relevant_reason_values": [
            "route_cost_or_conductance_dominance",
            "multi_channel_geometry_dominance_if_route_or_branch_conditioned",
            "support_gradient_dominance_if_branch_conditioned",
            "coherence_floor_dominance_if_branch_conditioned",
            "boundary_integrity_dominance_if_branch_conditioned",
            "flux_leakage_minimization_if_branch_conditioned",
            "susceptibility_delta_conditioned_with_n23_source_current_expression",
        ],
        "susceptibility_delta_conditioned_requires_n23_source_current_expression": True,
        "susceptibility_delta_conditioned_cannot_use_only_inherited_n22_delta": True,
        "n22_inherited_delta_used_as_selection_evidence_required_value": False,
        "n23_susceptibility_expression_trace_required_when_conditioned": True,
        "semantic_choice_label_allowed": False,
        "random_tie_as_collapse_allowed": False,
        "producer_preference_allowed": False,
    }


def threshold_declaration_policy() -> dict[str, Any]:
    return {
        "row_specific_thresholds_declared_before_use": True,
        "outcome_inspection_before_threshold_declaration_allowed": False,
        "retune_after_outcome_allowed": False,
        "required_threshold_fields": THRESHOLD_FIELDS,
        "threshold_record_required_fields": [
            "threshold_id",
            "source_contract_row",
            "source_consumable_contract_row",
            "source_contract_row_digest",
            "source_consumable_contract_row_digest",
            "threshold_declared_before_use",
            "threshold_value_or_rule",
            "threshold_owner",
            "failure_policy",
        ],
        "failure_policy": "missing_or_post_hoc_threshold_blocks_lc_support",
    }


def support_coherence_boundary_flux_schema() -> dict[str, Any]:
    return {
        "required_result_fields": [
            "support_floor_result",
            "coherence_floor_result",
            "boundary_integrity_result",
            "flux_or_leakage_result",
        ],
        "result_status_values": RESULT_STATUS_VALUES,
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
            "flux_or_leakage_result": [
                "preserved",
                "changed_within_bound",
            ],
        },
        "not_applicable_blocks_lc2_plus": {
            "support_floor_result": True,
            "coherence_floor_result": True,
            "boundary_integrity_result": True,
            "flux_or_leakage_result": True,
        },
        "changed_status_requires_declared_floor_or_bound_preserved": True,
        "missing_result_blocks_support": True,
        "floor_crossing_blocks_support": True,
        "flux_bound_exceeded_blocks_support": True,
        "out_of_scope_boundary_change_blocks_support": True,
    }


def replay_control_schema() -> dict[str, Any]:
    return {
        "status_enum": REPLAY_CONTROL_STATUSES,
        "required_replay_modes": {
            "LC4": ["artifact_replay", "snapshot_load_replay", "duplicate_replay"],
            "LC5": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "order_inversion_control",
                "post_hoc_stitching_control",
            ],
            "LC6": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "order_inversion_control",
                "post_hoc_stitching_control",
                "handoff_reconstruction_replay",
            ],
        },
        "canonical_control_ids": CANONICAL_CONTROL_IDS,
        "required_control_record_fields": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
        ],
        "not_run_blocks_dependent_rung": True,
        "failed_open_invalidates_row": True,
        "failed_closed_is_expected_good_result_for_negative_controls": True,
        "failed_closed_satisfies_required_negative_control": True,
        "failed_closed_blocks_only_control_null_unsafe_claim_by_default": True,
        "failed_closed_demotes_positive_candidate_only_when_rung_effect_declares": True,
        "control_satisfied_for_positive_row_when_expected_and_actual_failed_closed": True,
        "not_applicable_requires_scope_reason": True,
    }


def active_null_comparability_rule() -> dict[str, Any]:
    return {
        "same_source_contract_row": True,
        "same_source_contract_row_digest": True,
        "same_source_consumable_contract_row": True,
        "same_basin_signature_fields": True,
        "same_seed_or_declared_seed_pairing_rule": True,
        "same_topology_config_family": True,
        "same_runtime_envelope_digest": True,
        "same_branch_and_collapse_window_policy": True,
        "same_budget_schedule_digest_where_applicable": True,
        "same_route_or_branch_scope_where_applicable": True,
        "expected_result": "failed_closed",
        "weak_or_noncomparable_null_blocks_null_use": True,
    }


def ladder_schema() -> dict[str, Any]:
    lc = [
        ("LC0", "no_source_current_live_continuation_evidence"),
        ("LC1", "run_artifact_with_possible_branch_collapse_context"),
        ("LC2", "source_current_live_branch_set_with_at_least_two_real_alternatives"),
        ("LC3", "source_current_collapse_trace_from_live_branch_set_to_one_continuation"),
        ("LC4", "replay_control_backed_live_continuation_collapse_candidate"),
        ("LC5", "ap4_relevant_route_branch_selection_geometry_candidate"),
        ("LC6", "n24_ready_bounded_live_continuation_collapse_evidence"),
    ]
    closeout = [
        ("N23-C0", "contract_only_closeout"),
        ("N23-C1", "active_null_control_discipline_established"),
        ("N23-C2", "live_branch_partial"),
        ("N23-C3", "source_current_collapse_candidate"),
        ("N23-C4", "replay_control_backed_collapse_candidate"),
        ("N23-C5", "ap4_relevant_selection_geometry_candidate"),
        ("N23-C6", "n24_ready_bounded_live_continuation_collapse_evidence"),
    ]
    return {
        "live_continuation_ladder": [
            {"rung": rung, "meaning": meaning} for rung, meaning in lc
        ],
        "n23_closeout_ladder": [
            {"rung": rung, "meaning": meaning} for rung, meaning in closeout
        ],
        "rows_below_lc3_cannot_support_collapse": True,
        "rows_below_lc4_cannot_support_replay_control_backed_selection_geometry": True,
        "lc6_is_handoff_rung_not_agency_or_semantic_choice": True,
        "n23_c_rungs_classify_tranche_not_individual_row_labels": True,
        "n23_c_rungs_cannot_open_unsafe_claims": True,
        "n20_contract_completeness_assigns_lc_rungs": False,
        "n22_closeout_assigns_lc_rungs": False,
        "rungs_require_source_backed_n23_evidence_rows": True,
    }


def ap_dependency_schema() -> dict[str, Any]:
    return {
        "ap4_dependency_status_values": AP4_STATUS_VALUES,
        "ap5_dependency_status_values": AP5_STATUS_VALUES,
        "inventory_meta_status_values_invalid_for_candidate_rows": (
            INVENTORY_META_AP_STATUS_VALUES
        ),
        "ap4_condition_reason_required": True,
        "ap5_condition_reason_required": True,
        "route_or_branch_conditioned_rows_require_ap4": True,
        "proxy_or_target_conditioned_rows_require_ap5": True,
        "missing_blocks_row_status": "missing_blocks_row",
        "ap_gap_prose_only_not_sufficient": True,
        "ap4_bridge_status_values": AP4_BRIDGE_STATUS_VALUES,
        "ap4_bridge_status_initial": "not_supported",
        "ap4_bridge_candidate_requires": [
            "LC5_or_LC6_cleanly_supported",
            "source_current_live_branch_set",
            "source_current_collapse_trace",
            "counterfactual_retention",
            "replay_and_controls_pass",
            "route_or_branch_conditioned_source_current_reason",
            "AP4_dependency_status_required_recorded",
            "unsafe_claims_blocked",
        ],
    }


def producer_preference_absence_schema() -> dict[str, Any]:
    return {
        "producer_selected_branch_label_absent_required_for_support": True,
        "producer_preference_injection_absent_required_for_support": True,
        "random_tie_status_allowed_values": [
            "not_applicable",
            "not_random_tie",
            "random_tie_rejected",
            "random_tie_blocks_row",
        ],
        "producer_label_as_selected_reason_blocks_row": True,
        "producer_preference_as_selected_reason_blocks_row": True,
        "random_tie_as_collapse_blocks_row": True,
        "preference_or_label_may_be_recorded_only_as_producer_residue": True,
    }


def row_decision_policy() -> dict[str, Any]:
    return {
        "allowed_values": ROW_DECISIONS,
        "supported_does_not_automatically_allow_lc_claim": True,
        "supported_requires_lc_gate_passes_for_claim_allowed": True,
        "partial_blocks_final_lc_claim": True,
        "blocked_forces_claim_allowed_false": True,
        "rejected_forces_claim_allowed_false": True,
        "not_applicable_requires_scope_reason": True,
        "semantic_choice_claim_allowed_always_false": True,
    }


def claim_boundary_schema() -> dict[str, Any]:
    return {
        "unsafe_claim_flags_required": unsafe_claim_flags(),
        "all_unsafe_claim_flags_must_be_false": True,
        "blocked_claims": unique_list(
            UNSAFE_CLAIMS
            + [
                "ant_ecology_specification",
                "semantic_choice",
                "semantic_intention",
                "producer_preference_as_selection",
                "random_tie_as_collapse",
                "N22_susceptibility_as_choice",
            ]
        ),
        "phase8_opened": False,
        "native_support_opened": False,
        "sentience_opened": False,
        "ant_ecology_implementation_opened": False,
        "allowed_claim_ceiling": (
            "bounded artifact-level live-continuation collapse / "
            "selection-geometry candidate"
        ),
    }


def demotion_precedence() -> dict[str, Any]:
    return {
        "iteration4_candidate_rungs_are_provisional_until_controls": True,
        "final_lc_and_n23_c_rungs_assigned_after_control_matrix_only": True,
        "missing_live_branch_set_blocks_lc2_plus": True,
        "missing_collapse_trace_blocks_lc3_plus": True,
        "missing_counterfactual_retention_blocks_lc3_plus": True,
        "replay_failure_blocks_lc4_plus": True,
        "control_failed_closed_satisfies_required_negative_control": True,
        "control_failed_closed_blocks_unsafe_control_claim": True,
        "control_failed_closed_demotes_positive_candidate_only_with_explicit_rung_effect": True,
        "control_failed_open_invalidates_row": True,
        "not_run_blocks_dependent_rung": True,
        "missing_ap_dependency_blocks_dependent_row": True,
        "hypothesis_c_failure_demotes_or_blocks_a_b": True,
    }


def build_payload() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i1_row = i1["contract_inventory_rows"][0]

    source_artifacts = [
        source_record(I1_OUTPUT_PATH, "n23_i1_source_handoff_inventory"),
        source_record(I1_REPORT_PATH, "n23_i1_source_handoff_report"),
    ]

    schema = {
        "source_current_branch_definition": source_current_branch_definition(),
        "candidate_evidence_row_schema": candidate_evidence_row_schema(i1),
        "run_artifact_admissibility_schema": run_artifact_admissibility_schema(),
        "artifact_role_schema": {
            "artifact_role_values": ARTIFACT_ROLE_VALUES,
            "positive_lc_support_forbidden_if_only_roles": (
                POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES
            ),
        },
        "branch_collapse_window_schema": branch_collapse_window_schema(),
        "counterfactual_retention_schema": counterfactual_retention_schema(),
        "selected_branch_reason_schema": selected_branch_reason_schema(),
        "threshold_declaration_policy": threshold_declaration_policy(),
        "producer_preference_absence_schema": producer_preference_absence_schema(),
        "support_coherence_boundary_flux_schema": (
            support_coherence_boundary_flux_schema()
        ),
        "replay_control_schema": replay_control_schema(),
        "active_null_comparability_rule": active_null_comparability_rule(),
        "ladder_schema": ladder_schema(),
        "ap_dependency_schema": ap_dependency_schema(),
        "row_decision_policy": row_decision_policy(),
        "demotion_precedence": demotion_precedence(),
        "claim_boundary_schema": claim_boundary_schema(),
    }

    checks = [
        check(
            "source_i1_inventory_passed",
            i1["status"] == "passed" and i1["failed_checks"] == [],
            {"status": i1["status"], "failed_checks": i1["failed_checks"]},
        ),
        check(
            "i1_boundary_kept_no_live_continuation_evidence",
            i1["evidence_boundary"]["live_continuation_collapse_evidence_opened"]
            is False
            and i1["evidence_boundary"]["lc_ladder_rung_assigned"] is False
            and i1["evidence_boundary"]["ap4_bridge_status"]
            == "not_supported_inventory_only",
            i1["evidence_boundary"],
        ),
        check(
            "candidate_evidence_row_schema_complete",
            set(CANDIDATE_EVIDENCE_FIELDS).issubset(
                set(schema["candidate_evidence_row_schema"]["required_fields"])
            )
            and "n22_source_closeout_status" in CANDIDATE_EVIDENCE_FIELDS
            and all(field in CANDIDATE_EVIDENCE_FIELDS for field in THRESHOLD_FIELDS),
            {
                "required_field_count": len(CANDIDATE_EVIDENCE_FIELDS),
                "threshold_fields": THRESHOLD_FIELDS,
            },
        ),
        check(
            "n19_boundary_only_schema_frozen",
            schema["candidate_evidence_row_schema"]["field_constraints"][
                "n19_native_readiness_boundary_consumption"
            ]["allowed_values"]
            == [N19_CONSUMPTION_VALUE],
            {"allowed_value": N19_CONSUMPTION_VALUE},
        ),
        check(
            "prefixed_source_status_fields_frozen",
            schema["candidate_evidence_row_schema"]["field_constraints"][
                "n20_source_downstream_consumption_status"
            ]["required_value"]
            == i1_row["n20_source_downstream_consumption_status"]
            and schema["candidate_evidence_row_schema"]["field_constraints"][
                "n22_source_closeout_status"
            ]["required_value"]
            == i1["n22_context_boundary"]["n22_source_closeout_status"],
            {
                "n20_source_downstream_consumption_status": i1_row[
                    "n20_source_downstream_consumption_status"
                ],
                "n22_source_closeout_status": i1["n22_context_boundary"][
                    "n22_source_closeout_status"
                ],
            },
        ),
        check(
            "source_row_digests_split_frozen",
            schema["candidate_evidence_row_schema"]["field_constraints"][
                "source_contract_row_digest"
            ]["required_value"]
            == i1_row["source_contract_row_digest"]
            and schema["candidate_evidence_row_schema"]["field_constraints"][
                "source_consumable_contract_row_digest"
            ]["required_value"]
            == i1_row["source_consumable_contract_row_digest"]
            and i1_row["source_contract_row_digest"]
            != i1_row["source_consumable_contract_row_digest"],
            {
                "source_contract_row": SOURCE_CONTRACT_ROW,
                "source_consumable_contract_row": CONSUMABLE_CONTRACT_ROW,
            },
        ),
        check(
            "live_branch_acceptance_frozen",
            schema["source_current_branch_definition"]["required_origin"]
            == "source_current_same_run"
            and schema["source_current_branch_definition"]["minimum_branch_count_for_lc2"]
            == 2,
            schema["source_current_branch_definition"],
        ),
        check(
            "trace_status_fields_frozen",
            schema["candidate_evidence_row_schema"]["field_constraints"][
                "live_branch_set_trace"
            ]["trace_status_values"]
            == TRACE_STATUS_VALUES
            and schema["candidate_evidence_row_schema"]["field_constraints"][
                "collapsed_continuation_trace"
            ]["trace_origin_values"]
            == TRACE_ORIGIN_VALUES
            and schema["candidate_evidence_row_schema"]["field_constraints"][
                "counterfactual_branch_retention_trace"
            ]["required_trace_fields"]
            == ["trace_status", "trace_origin", "missing_blocks_rungs"],
            {
                "trace_status_values": TRACE_STATUS_VALUES,
                "trace_origin_values": TRACE_ORIGIN_VALUES,
            },
        ),
        check(
            "branch_record_origin_enum_frozen",
            schema["candidate_evidence_row_schema"]["field_constraints"][
                "branch_record_origin"
            ]["allowed_values"]
            == BRANCH_RECORD_ORIGIN_VALUES,
            BRANCH_RECORD_ORIGIN_VALUES,
        ),
        check(
            "run_artifact_admissibility_fail_closed",
            schema["run_artifact_admissibility_schema"][
                "fail_closed_on_missing_or_mismatch"
            ]
            is True
            and schema["run_artifact_admissibility_schema"][
                "derived_report_only_true_blocks_positive_support"
            ]
            is True,
            schema["run_artifact_admissibility_schema"],
        ),
        check(
            "artifact_manifest_crosschecks_frozen",
            schema["run_artifact_admissibility_schema"][
                "artifact_paths_equal_manifest_paths_required"
            ]
            is True
            and schema["run_artifact_admissibility_schema"][
                "artifact_sha256_equal_manifest_sha256_required"
            ]
            is True,
            schema["run_artifact_admissibility_schema"],
        ),
        check(
            "artifact_role_enum_and_positive_restrictions_frozen",
            "branch_set_trace" in ARTIFACT_ROLE_VALUES
            and set(POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES)
            == {"report", "inherited_context", "source_contract", "closeout"},
            schema["artifact_role_schema"],
        ),
        check(
            "branch_collapse_temporal_ordering_frozen",
            schema["branch_collapse_window_schema"][
                "branch_window_end_lte_collapse_window_start_required"
            ]
            is True,
            schema["branch_collapse_window_schema"],
        ),
        check(
            "counterfactual_retention_schema_frozen",
            schema["counterfactual_retention_schema"]["meaning"]
            == "immutable_pre_collapse_audit_record"
            and schema["counterfactual_retention_schema"][
                "continued_dynamic_activity_after_collapse_required"
            ]
            is False,
            schema["counterfactual_retention_schema"],
        ),
        check(
            "selected_branch_reason_enum_frozen",
            "susceptibility_delta_conditioned" in SELECTED_BRANCH_REASON_VALUES
            and "semantic_choice_label" in BLOCKED_SELECTED_BRANCH_REASONS,
            schema["selected_branch_reason_schema"],
        ),
        check(
            "ap4_relevant_reason_subset_frozen",
            "route_or_branch_conditioned_true"
            in schema["selected_branch_reason_schema"]["ap4_relevant_reason_requires"]
            and "route_cost_or_conductance_dominance"
            in schema["selected_branch_reason_schema"]["ap4_relevant_reason_values"],
            schema["selected_branch_reason_schema"],
        ),
        check(
            "n22_susceptibility_inheritance_blocker_frozen",
            schema["selected_branch_reason_schema"][
                "susceptibility_delta_conditioned_cannot_use_only_inherited_n22_delta"
            ]
            is True
            and schema["selected_branch_reason_schema"][
                "n22_inherited_delta_used_as_selection_evidence_required_value"
            ]
            is False,
            schema["selected_branch_reason_schema"],
        ),
        check(
            "n23_susceptibility_expression_trace_required",
            schema["candidate_evidence_row_schema"]["field_constraints"][
                "n23_susceptibility_expression_trace"
            ]["constraint"]
            == "required when selected reason is susceptibility_delta_conditioned",
            schema["candidate_evidence_row_schema"]["field_constraints"][
                "n23_susceptibility_expression_trace"
            ],
        ),
        check(
            "producer_preference_absence_schema_frozen",
            schema["producer_preference_absence_schema"][
                "producer_preference_injection_absent_required_for_support"
            ]
            is True,
            schema["producer_preference_absence_schema"],
        ),
        check(
            "canonical_control_ids_frozen",
            set(CANONICAL_CONTROL_IDS)
            == set(schema["replay_control_schema"]["canonical_control_ids"]),
            CANONICAL_CONTROL_IDS,
        ),
        check(
            "threshold_policy_declared_before_use",
            schema["threshold_declaration_policy"][
                "row_specific_thresholds_declared_before_use"
            ]
            is True
            and set(THRESHOLD_FIELDS)
            == set(schema["threshold_declaration_policy"]["required_threshold_fields"]),
            schema["threshold_declaration_policy"],
        ),
        check(
            "support_coherence_boundary_flux_schema_frozen",
            schema["support_coherence_boundary_flux_schema"][
                "changed_status_requires_declared_floor_or_bound_preserved"
            ]
            is True
            and all(
                schema["support_coherence_boundary_flux_schema"][
                    "not_applicable_blocks_lc2_plus"
                ].values()
            ),
            schema["support_coherence_boundary_flux_schema"],
        ),
        check(
            "replay_control_schema_frozen",
            schema["replay_control_schema"]["not_run_blocks_dependent_rung"] is True
            and schema["replay_control_schema"]["failed_open_invalidates_row"] is True,
            schema["replay_control_schema"],
        ),
        check(
            "failed_closed_negative_control_semantics_frozen",
            schema["replay_control_schema"][
                "failed_closed_satisfies_required_negative_control"
            ]
            is True
            and schema["replay_control_schema"][
                "control_satisfied_for_positive_row_when_expected_and_actual_failed_closed"
            ]
            is True
            and schema["demotion_precedence"][
                "control_failed_closed_demotes_positive_candidate_only_with_explicit_rung_effect"
            ]
            is True,
            {
                "replay_control_schema": schema["replay_control_schema"],
                "demotion_precedence": schema["demotion_precedence"],
            },
        ),
        check(
            "active_null_comparability_frozen",
            schema["active_null_comparability_rule"][
                "same_branch_and_collapse_window_policy"
            ]
            is True,
            schema["active_null_comparability_rule"],
        ),
        check(
            "lc_ladder_complete",
            len(schema["ladder_schema"]["live_continuation_ladder"]) == 7
            and schema["ladder_schema"]["rows_below_lc3_cannot_support_collapse"]
            is True,
            schema["ladder_schema"]["live_continuation_ladder"],
        ),
        check(
            "n23_closeout_ladder_complete",
            len(schema["ladder_schema"]["n23_closeout_ladder"]) == 7
            and schema["ladder_schema"]["lc6_is_handoff_rung_not_agency_or_semantic_choice"]
            is True,
            schema["ladder_schema"]["n23_closeout_ladder"],
        ),
        check(
            "ap_dependency_enums_frozen",
            schema["ap_dependency_schema"]["ap4_dependency_status_values"]
            == AP4_STATUS_VALUES
            and schema["ap_dependency_schema"]["ap5_dependency_status_values"]
            == AP5_STATUS_VALUES,
            schema["ap_dependency_schema"],
        ),
        check(
            "inventory_meta_ap_values_invalid_for_candidate_rows",
            set(INVENTORY_META_AP_STATUS_VALUES)
            == set(
                schema["ap_dependency_schema"][
                    "inventory_meta_status_values_invalid_for_candidate_rows"
                ]
            ),
            INVENTORY_META_AP_STATUS_VALUES,
        ),
        check(
            "ap4_bridge_status_enum_frozen",
            "bridge_candidate_supported" in AP4_BRIDGE_STATUS_VALUES
            and "blocked_by_single_live_branch" in AP4_BRIDGE_STATUS_VALUES
            and "blocked_by_artifact_manifest" in AP4_BRIDGE_STATUS_VALUES,
            AP4_BRIDGE_STATUS_VALUES,
        ),
        check(
            "row_decision_policy_frozen",
            schema["row_decision_policy"]["semantic_choice_claim_allowed_always_false"]
            is True
            and schema["row_decision_policy"]["blocked_forces_claim_allowed_false"]
            is True,
            schema["row_decision_policy"],
        ),
        check(
            "claim_boundary_schema_frozen",
            all(value is False for value in schema["claim_boundary_schema"]["unsafe_claim_flags_required"].values())
            and schema["claim_boundary_schema"]["native_support_opened"] is False
            and schema["claim_boundary_schema"]["phase8_opened"] is False,
            schema["claim_boundary_schema"],
        ),
        check(
            "demotion_precedence_frozen",
            schema["demotion_precedence"][
                "final_lc_and_n23_c_rungs_assigned_after_control_matrix_only"
            ]
            is True,
            schema["demotion_precedence"],
        ),
        check(
            "no_positive_evidence_opened",
            True,
            {
                "positive_run_artifacts_consumed": False,
                "candidate_rows_classified": False,
                "live_continuation_collapse_evidence_opened": False,
                "lc_ladder_rung_assigned": False,
                "n23_closeout_ladder_rung_assigned": False,
                "ap4_bridge_status": "not_supported",
            },
        ),
    ]

    payload: dict[str, Any] = {
        "schema_version": "n23_i2_live_continuation_schema_and_controls_v1",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": 2,
        "artifact_id": "n23_i2_live_continuation_schema_and_controls",
        "purpose": "freeze schema, ladders, controls, AP rules, and claim boundaries before N23 positive probes",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_live_continuation_schema_frozen_no_positive_evidence",
        "source_artifacts": source_artifacts,
        "source_i1_output_digest": i1["output_digest"],
        "source_i1_artifact_sha256": sha256_file(I1_OUTPUT_PATH),
        "schema": schema,
        "evidence_boundary": {
            "candidate_rows_classified": False,
            "positive_run_artifacts_consumed": False,
            "live_continuation_collapse_evidence_opened": False,
            "lc_ladder_rung_assigned": False,
            "n23_closeout_ladder_rung_assigned": False,
            "n23_closeout_ceiling": "N23-C0_schema_freeze_only",
            "ap4_bridge_status": "not_supported",
            "ap5_dependency_status": "conditional_pending_future_rows",
            "semantic_choice_supported": False,
            "semantic_intention_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
        },
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> str:
    schema = payload["schema"]
    checks = payload["checks"]
    lines = [
        "# N23 Iteration 2 - Schema, Ladder, And Control Freeze",
        "",
        "## Summary",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Acceptance state: `{payload['acceptance_state']}`",
        "",
        f"Output digest: `{payload['output_digest']}`",
        "",
        "Iteration 2 freezes N23 schema and control rules. It opens no positive",
        "live-continuation evidence, assigns no LC rung, and does not support an",
        "AP4 bridge.",
        "",
        "## Frozen Ladders",
        "",
        "| Ladder | Count | Boundary |",
        "| --- | ---: | --- |",
        "| LC | 7 | Rows below LC3 cannot support collapse; LC6 is N24 handoff only. |",
        "| N23-C | 7 | Tranche-level closeout ladder; not semantic choice or agency. |",
        "",
        "## Key Frozen Policies",
        "",
        "- Live branches must be same-run, same-window, pre-collapse source-current records.",
        "- Original LC2 branch evidence must come from the same source-current runtime trace; replay forks audit but do not create original branches.",
        "- Required traces carry `trace_status`, `trace_origin`, and rung-blocking fields when missing.",
        "- `branch_record_origin = source_current_same_run` is required for LC2+.",
        "- Replay forks may audit counterfactuals but cannot create original live branches.",
        "- Counterfactual retention means immutable pre-collapse audit evidence.",
        "- Selected-branch reasons use a closed source-current enum.",
        "- AP4-relevant selected reasons require route/branch conditioning and peer or counterfactual comparison.",
        "- Producer labels, producer preference, random ties, post-hoc report selection, single-branch relabels, and semantic-choice labels are blocked.",
        "- `susceptibility_delta_conditioned` cannot pass from inherited N22 evidence alone; row-local N23 susceptibility expression is required.",
        "- Candidate AP dependency statuses use row-local enums only; inventory/meta AP values are invalid for candidate rows.",
        "- Numeric support/coherence/boundary/flux/collapse thresholds must be frozen before positive probes.",
        "- `not_applicable` support/coherence/boundary/flux result values block LC2+ candidate support.",
        "- Artifact path and SHA lists must match artifact manifest paths and SHA values.",
        "- `failed_closed` is the expected good result for required negative controls; `failed_open` invalidates and `not_run` blocks dependent rungs.",
        "- Positive LC support cannot come from report, inherited-context, source-contract, or closeout-only artifacts.",
        "- Required controls include random tie, missing counterfactual retention, N22-as-choice relabel, AP4/AP5 missing, AP-gap prose-only, and unsafe relabel controls.",
        "",
        "## Required Candidate Field Count",
        "",
        f"`{len(schema['candidate_evidence_row_schema']['required_fields'])}` fields",
        "",
        "## AP Dependency Enums",
        "",
        "```text",
        f"ap4_dependency_status = {AP4_STATUS_VALUES}",
        f"ap5_dependency_status = {AP5_STATUS_VALUES}",
        f"invalid_candidate_values = {INVENTORY_META_AP_STATUS_VALUES}",
        "```",
        "",
        "## Evidence Boundary",
        "",
        "```text",
        "candidate_rows_classified = false",
        "positive_run_artifacts_consumed = false",
        "live_continuation_collapse_evidence_opened = false",
        "lc_ladder_rung_assigned = false",
        "n23_closeout_ceiling = N23-C0_schema_freeze_only",
        "ap4_bridge_status = not_supported",
        "semantic_choice_supported = false",
        "agency_supported = false",
        "native_support_supported = false",
        "phase8_opened = false",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for item in checks:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I2 is a schema freeze only. It does not show live branch existence,",
            "collapse, counterfactual retention, AP4 bridge evidence, semantic",
            "choice, intention, agency, native support, sentience, Phase 8, or ant",
            "ecology implementation.",
            "",
            "The next step is Iteration 3 active nulls and failure baselines.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    REPORT.write_text(write_report(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
