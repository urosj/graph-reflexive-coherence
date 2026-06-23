#!/usr/bin/env python3
"""Build N22 Iteration 2 susceptibility schema/control freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
)
OUTPUT = EXPERIMENT / "outputs" / "n22_susceptibility_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n22_susceptibility_schema_and_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_susceptibility_schema_and_controls.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_source_handoff_inventory.json"
)
I1_REPORT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "reports/n22_source_handoff_inventory.md"
)

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
N19_CONSUMPTION_VALUES = [
    "context_only",
    "ap_gap_boundary_only",
    "evidence_source",
]
N21_ND6_BRIDGE_STATUS_VALUES = [
    "not_supported",
    "bridge_candidate_supported",
    "blocked_by_replay",
    "blocked_by_controls",
    "blocked_by_AP_gap",
    "blocked_by_producer_residue",
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
REQUIRED_RUN_ARTIFACT_FIELDS = [
    "run_artifact_id",
    "source_commit_or_source_digest",
    "runtime_config_digest",
    "source_contract_row_digest",
    "artifact_manifest",
    "pre_interaction_artifact_path",
    "interaction_artifact_path",
    "post_interaction_artifact_path",
    "reentry_artifact_path",
    "event_log_or_trace_path",
    "snapshot_or_replay_artifact_path",
    "artifact_sha256",
    "all_artifact_sha256_match_file_contents",
    "derived_report_only",
]
CANDIDATE_EVIDENCE_FIELDS = [
    "row_id",
    "source_contract_row",
    "source_contract_row_digest",
    "source_output_digest",
    "run_artifact_id",
    "source_commit_or_source_digest",
    "runtime_config_digest",
    "source_current_inputs",
    "row_specific_thresholds_declared_before_use",
    "n19_native_readiness_boundary_consumption",
    "n20_source_downstream_consumption_status",
    "interaction_window",
    "reentry_window",
    "pre_interaction_geometry_trace",
    "post_interaction_geometry_trace",
    "susceptibility_delta_trace",
    "route_or_region_reentry_trace",
    "same_basin_continuation_rule",
    "allowed_delta_fields",
    "same_basin_invariant_fields",
    "out_of_scope_drift_blocks_row",
    "delta_not_label_reassignment",
    "route_or_region_conditioned",
    "peer_same_budget_comparison",
    "peer_same_budget_comparison_scope_reason",
    "peer_route_or_region_trace",
    "historical_interaction_provenance_present",
    "active_reinforcement_schedule_disabled",
    "active_reinforcement_queue_empty",
    "reinforcement_budget_in_flight",
    "reinforcement_schedule_not_used_as_evidence",
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
    "interaction_delta_digest",
    "post_replay_delta_digest",
    "reentry_delta_digest",
    "delta_persistence_ratio",
    "delta_threshold_or_rule",
    "one_window_transient_rejected",
    "global_drift_rejected",
    "producer_residue_fields",
    "naturalization_debt_fields",
    "blocked_relabel_fields",
    "claim_ceiling",
    "unsafe_claim_flags",
    "row_decision",
    "susceptibility_update_claim_allowed",
    "derived_report_only",
    "artifact_manifest",
    "artifact_paths",
    "artifact_sha256",
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


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def source_current_definition() -> dict[str, Any]:
    return {
        "definition": (
            "emitted by the LGRC runtime or replay from declared run artifacts, "
            "not invented by a report builder, label, post-hoc parser, "
            "producer-only reinforcement policy, or semantic learning vocabulary"
        ),
        "required_future_inputs": [
            "susceptibility_update.pre_interaction_geometry_trace",
            "susceptibility_update.post_interaction_geometry_trace",
            "susceptibility_update.susceptibility_delta_trace",
            "susceptibility_update.route_or_region_reentry_trace",
        ],
        "allowed_sources": [
            "LGRC runtime output",
            "artifact-only replay from declared run artifacts",
            "snapshot/load replay from declared run artifacts",
            "duplicate replay from declared run artifacts",
        ],
        "blocked_sources": [
            "route label",
            "reinforcement schedule label",
            "learning label",
            "report-built row",
            "post-hoc parser construction",
            "N21 WR/ND closeout",
            "N19 AP-gap boundary artifact",
            "roadmap or handoff prose",
        ],
    }


def run_artifact_admissibility_schema() -> dict[str, Any]:
    return {
        "required_fields": REQUIRED_RUN_ARTIFACT_FIELDS,
        "artifact_manifest_schema": {
            "type": "list[object]",
            "required_item_fields": ["path", "sha256", "artifact_role"],
            "path_policy": "repository_relative_paths_only",
            "artifact_role_required": True,
        },
        "digest_algorithm": "sha256",
        "path_policy": "repository_relative_paths_only",
        "artifact_paths_must_exist": True,
        "artifact_digests_must_match_file_contents": True,
        "all_artifact_sha256_match_file_contents_required": True,
        "source_contract_row_digest_must_match_i1": True,
        "derived_report_only_true_blocks_positive_support": True,
        "missing_required_artifact_blocks_rung_assignment": True,
        "digest_mismatch_blocks_rung_assignment": True,
        "report_only_artifacts_may_summarize_but_not_assign_rungs": True,
        "fail_closed_on_missing_or_mismatch": True,
    }


def candidate_evidence_row_schema() -> dict[str, Any]:
    constraints: dict[str, dict[str, Any]] = {
        field: {"type": "recorded", "constraint": "required for candidate rows"}
        for field in CANDIDATE_EVIDENCE_FIELDS
    }
    constraints.update(
        {
            "source_contract_row": {
                "type": "string",
                "constraint": "must equal n20_i5_row_03_susceptibility_update",
            },
            "source_contract_row_digest": {
                "type": "sha256_string",
                "constraint": "must match N22 I1 contract digest",
            },
            "source_current_inputs": {
                "type": "list[string]",
                "constraint": "must be runtime/replay emitted, not report-built",
            },
            "row_specific_thresholds_declared_before_use": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks positive support",
            },
            "n19_native_readiness_boundary_consumption": {
                "type": "enum",
                "allowed_values": N19_CONSUMPTION_VALUES,
                "required_value": "ap_gap_boundary_only",
                "constraint": "evidence_source blocks susceptibility support",
            },
            "n20_source_downstream_consumption_status": {
                "type": "string",
                "constraint": "records inherited N20 status, not N22 iteration status",
            },
            "same_basin_continuation_rule": {
                "type": "object",
                "source": "N22 I1 frozen N20 I5 same-basin rule",
                "constraint": "must be consumed without redefinition",
            },
            "allowed_delta_fields": {
                "type": "list[string]",
                "constraint": "only declared source-current fields may change as delta evidence",
            },
            "same_basin_invariant_fields": {
                "type": "list[string]",
                "constraint": "must remain stable enough for same-basin continuation",
            },
            "out_of_scope_drift_blocks_row": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks support",
            },
            "delta_not_label_reassignment": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks support",
            },
            "route_or_region_conditioned": {
                "type": "boolean",
                "constraint": "determines whether peer comparison is mandatory",
            },
            "peer_same_budget_comparison": {
                "type": "object",
                "constraint": "mandatory when route_or_region_conditioned = true",
            },
            "peer_same_budget_comparison_scope_reason": {
                "type": "string",
                "constraint": (
                    "required when peer comparison is not_applicable; only "
                    "non_route_conditioned_SU2_only may bypass peer comparison"
                ),
            },
            "historical_interaction_provenance_present": {
                "type": "boolean",
                "constraint": "required when prior interaction is claimed",
            },
            "active_reinforcement_schedule_disabled": {
                "type": "boolean",
                "required_value_for_durable_delta_support": True,
                "constraint": "false demotes to producer residue",
            },
            "active_reinforcement_queue_empty": {
                "type": "boolean",
                "required_value_for_durable_delta_support": True,
                "constraint": "false demotes to producer residue",
            },
            "reinforcement_budget_in_flight": {
                "type": "number",
                "required_value_for_durable_delta_support": 0.0,
                "constraint": "nonzero demotes to producer residue",
            },
            "reinforcement_schedule_not_used_as_evidence": {
                "type": "boolean",
                "required_value_for_durable_delta_support": True,
                "constraint": "false blocks source-current durable geometry claim",
            },
            "ap4_dependency_status": {
                "type": "enum",
                "allowed_values": AP4_STATUS_VALUES,
                "constraint": "missing_blocks_row blocks route-conditioned rows",
            },
            "ap5_dependency_status": {
                "type": "enum",
                "allowed_values": AP5_STATUS_VALUES,
                "constraint": "missing_blocks_row blocks proxy-conditioned rows",
            },
            "delta_persistence_ratio": {
                "type": "number",
                "constraint": "must meet declared floor before use",
            },
            "delta_threshold_or_rule": {
                "type": "object_or_string",
                "constraint": "must be declared before outcome inspection",
            },
            "one_window_transient_rejected": {
                "type": "boolean",
                "required_value_for_durable_delta_support": True,
                "constraint": "false blocks SU4 and stronger",
            },
            "global_drift_rejected": {
                "type": "boolean",
                "required_value_for_route_conditioned_support": True,
                "constraint": "false blocks route/region-conditioned SU5/SU6",
            },
            "row_decision": {
                "type": "enum",
                "allowed_values": ROW_DECISIONS,
                "constraint": "partial, blocked, rejected, and not_applicable block support",
            },
            "susceptibility_update_claim_allowed": {
                "type": "boolean",
                "constraint": (
                    "true only when artifacts, thresholds, same-basin rule, replay, "
                    "controls, AP dependencies, durability, peer comparison, and "
                    "unsafe flags all pass"
                ),
            },
            "derived_report_only": {
                "type": "boolean",
                "required_value_for_positive_support": False,
                "constraint": "true blocks positive susceptibility support",
            },
            "artifact_manifest": {
                "type": "list[object]",
                "required_item_fields": ["path", "sha256", "artifact_role"],
                "constraint": "all row artifacts must be listed with role and digest",
            },
            "artifact_paths": {
                "type": "list[repository_relative_path]",
                "constraint": "must match artifact_manifest paths",
            },
            "artifact_sha256": {
                "type": "object_or_list",
                "constraint": "must match artifact_manifest sha256 values",
            },
            "all_artifact_sha256_match_file_contents": {
                "type": "boolean",
                "required_value_for_positive_support": True,
                "constraint": "false blocks positive support",
            },
        }
    )
    return {
        "required_fields": CANDIDATE_EVIDENCE_FIELDS,
        "field_constraints": constraints,
        "missing_required_field_blocks_candidate_admissibility": True,
        "source_contract_row_must_match_i1": True,
        "same_basin_rule_must_use_i1_reference": True,
        "claim_allowed_false_if_unsafe_claim_requested": True,
        "claim_allowed_false_for_non_supported_rows": True,
    }


def threshold_declaration_policy() -> dict[str, Any]:
    return {
        "row_specific_thresholds_declared_before_use": True,
        "outcome_inspection_before_threshold_declaration_allowed": False,
        "retune_after_outcome_allowed": False,
        "required_threshold_surfaces": [
            "support_floor",
            "coherence_floor",
            "boundary_integrity_floor",
            "flux_or_leakage_bound",
            "delta_persistence_ratio_floor",
            "replay_window_survival_rule",
            "reentry_survival_rule",
            "peer_same_budget_comparison_rule",
            "global_drift_rejection_rule",
        ],
        "threshold_record_required_fields": [
            "threshold_id",
            "source_contract_row",
            "source_contract_row_digest",
            "threshold_declared_before_use",
            "threshold_value_or_rule",
            "threshold_owner",
            "failure_policy",
        ],
        "failure_policy": "missing_or_post_hoc_threshold_blocks_support",
    }


def susceptibility_delta_schema() -> dict[str, Any]:
    return {
        "required_trace_fields": [
            "pre_interaction_geometry_trace",
            "interaction_window",
            "post_interaction_geometry_trace",
            "susceptibility_delta_trace",
            "reentry_window",
            "route_or_region_reentry_trace",
        ],
        "delta_must_be_source_current": True,
        "delta_not_label_reassignment": True,
        "post_hoc_delta_construction_blocks_support": True,
        "route_label_only_delta_blocks_support": True,
        "reinforcement_schedule_only_delta_blocks_support": True,
    }


def allowed_drift_schema() -> dict[str, Any]:
    return {
        "allowed_delta_fields": [
            "susceptibility_update.post_interaction_geometry_trace",
            "susceptibility_update.susceptibility_delta_trace",
            "susceptibility_update.route_or_region_reentry_trace",
        ],
        "same_basin_invariant_fields": [
            "source_contract_row",
            "same_basin_rule.rule_id",
            "support_floor_result",
            "coherence_floor_result",
            "boundary_integrity_result",
            "flux_or_leakage_result",
        ],
        "out_of_scope_drift_blocks_row": True,
        "large_topology_boundary_support_or_identity_drift_blocks_support": True,
        "delta_not_label_reassignment": True,
    }


def historical_interaction_reinforcement_schema() -> dict[str, Any]:
    return {
        "historical_interaction_provenance_present_required_when_claimed": True,
        "active_reinforcement_schedule_disabled_required": True,
        "active_reinforcement_queue_empty_required": True,
        "reinforcement_budget_in_flight_required_value": 0.0,
        "reinforcement_schedule_not_used_as_evidence_required": True,
        "active_reinforcement_remaining_demotes_to": "producer_residue_or_blocked",
        "active_reinforcement_remaining_rung_effect": {
            "SU1": "descriptive_allowed_if_source_current_trace_exists",
            "SU2": "descriptive_allowed_if_source_current_delta_exists",
            "SU3": "replay_limited_only_if_replay_not_reinforcement_carried",
            "SU4": "blocked",
            "SU5": "blocked",
            "SU6": "blocked",
            "N22-C4": "blocked",
            "N22-C5": "blocked",
            "N22-C6": "blocked",
            "n21_nd6_bridge_status": "blocked_by_producer_residue",
        },
        "historical_interaction_is_not_active_support": True,
    }


def peer_same_budget_schema() -> dict[str, Any]:
    return {
        "required_when_route_or_region_conditioned": True,
        "not_required_for_non_route_conditioned_su2_only": True,
        "not_applicable_scope_reason_required": True,
        "allowed_not_applicable_scope_reason": "non_route_conditioned_SU2_only",
        "target_route_or_region_receives_prior_interaction": True,
        "peer_route_or_region_receives_same_budget_without_same_prior_interaction": True,
        "same_delta_in_peer_blocks_route_conditioned_support": True,
        "missing_peer_comparison_blocks": ["SU5", "SU6", "N22-C5", "N22-C6"],
        "global_drift_rejected_required": True,
    }


def durability_metric_schema() -> dict[str, Any]:
    return {
        "required_metrics": [
            "interaction_delta_digest",
            "post_replay_delta_digest",
            "reentry_delta_digest",
            "delta_persistence_ratio",
            "delta_threshold_or_rule",
            "one_window_transient_rejected",
            "global_drift_rejected",
        ],
        "delta_persistence_ratio_floor_declared_before_use": True,
        "replay_window_survival_required": True,
        "later_reentry_survival_required": True,
        "one_window_transient_rejected_required": True,
        "global_drift_rejected_required_for_route_conditioned_rows": True,
        "missing_metric_blocks_durable_delta_support": True,
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
        "changed_status_requires_declared_floor_or_bound_preserved": True,
        "missing_result_blocks_support": True,
        "floor_crossing_blocks_support": True,
        "flux_bound_exceeded_blocks_support": True,
        "out_of_scope_boundary_change_blocks_support": True,
    }


def replay_control_schema() -> dict[str, Any]:
    return {
        "status_enum": REPLAY_CONTROL_STATUSES,
        "replay_name_aliases": {
            "artifact_replay": ["artifact_only_replay"],
        },
        "canonical_replay_names_required": True,
        "required_replay_modes": {
            "SU3": ["artifact_replay"],
            "SU4": ["artifact_replay", "snapshot_load_replay", "duplicate_replay"],
            "SU5": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "later_reentry_replay",
            ],
            "SU6": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "later_reentry_replay",
                "handoff_reconstruction_replay",
            ],
        },
        "required_control_records": [
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
        "failed_closed_demotes_or_blocks_dependent_rung": True,
        "not_applicable_requires_scope_reason": True,
    }


def active_null_comparability_rule() -> dict[str, Any]:
    return {
        "same_source_contract_row": True,
        "same_source_contract_row_digest": True,
        "same_basin_signature_fields": True,
        "same_seed_or_declared_seed_pairing_rule": True,
        "same_topology_config_family": True,
        "same_runtime_envelope_digest": True,
        "same_budget_schedule_family_where_applicable": True,
        "same_budget_schedule_digest_where_applicable": True,
        "same_route_or_region_scope_where_applicable": True,
        "expected_result": "fail_closed",
        "weak_or_noncomparable_null_blocks_null_use": True,
    }


def ladder_schema() -> dict[str, Any]:
    su = [
        ("SU0", "no_source_current_susceptibility_evidence"),
        ("SU1", "interaction_run_present"),
        ("SU2", "source_current_pre_post_geometry_delta_observed"),
        ("SU3", "replay_backed_susceptibility_update_candidate"),
        ("SU4", "control_backed_durable_geometry_modification_candidate"),
        ("SU5", "transfer_reentry_backed_susceptibility_update_candidate"),
        ("SU6", "n23_ready_bounded_durable_geometry_modification_evidence"),
    ]
    closeout = [
        ("N22-C0", "contract_only_closeout"),
        ("N22-C1", "active_null_control_discipline_established"),
        ("N22-C2", "susceptibility_partial"),
        ("N22-C3", "replay_backed_susceptibility_candidate"),
        ("N22-C4", "durable_geometry_modification_candidate"),
        ("N22-C5", "transfer_reentry_backed_susceptibility_candidate"),
        ("N22-C6", "n23_ready_bounded_durable_geometry_evidence"),
    ]
    return {
        "susceptibility_update_ladder": [
            {"rung": rung, "meaning": meaning} for rung, meaning in su
        ],
        "n22_closeout_ladder": [
            {"rung": rung, "meaning": meaning} for rung, meaning in closeout
        ],
        "rows_below_su3_cannot_support_durable_geometry_modification": True,
        "su6_is_handoff_rung_not_agency_claim": True,
        "n22_c_rungs_classify_tranche_not_individual_row_labels": True,
        "n22_c_rungs_cannot_open_unsafe_claims": True,
        "n20_contract_completeness_assigns_rungs": False,
        "n21_closeout_assigns_su_rungs": False,
        "rungs_require_source_backed_n22_evidence_rows": True,
    }


def ap_dependency_schema() -> dict[str, Any]:
    return {
        "ap4_dependency_status_values": AP4_STATUS_VALUES,
        "ap5_dependency_status_values": AP5_STATUS_VALUES,
        "ap4_condition_reason_required": True,
        "ap5_condition_reason_required": True,
        "route_conditioned_rows_require_ap4": True,
        "proxy_or_target_conditioned_rows_require_ap5": True,
        "missing_blocks_row_status": "missing_blocks_row",
        "ap_gap_prose_only_not_sufficient": True,
        "iteration3_active_null_expectations": [
            {
                "null_id": "route_conditioned_row_missing_AP4",
                "expected_status": "failed_closed",
            },
            {
                "null_id": "proxy_or_target_conditioned_row_missing_AP5",
                "expected_status": "failed_closed",
            },
            {
                "null_id": "AP_gap_prose_only",
                "expected_status": "failed_closed",
            },
        ],
    }


def n21_nd6_bridge_status_schema() -> dict[str, Any]:
    return {
        "allowed_values": N21_ND6_BRIDGE_STATUS_VALUES,
        "initial_status": "not_supported",
        "wording_policy": "ND6_bridge_candidate_only",
        "blocked_wording": [
            "N21 ND6 achieved",
            "N21 ND6 supported",
            "N21 reopened",
        ],
        "bridge_candidate_supported_requires": [
            "SU5_or_SU6_cleanly_supported",
            "source_backed_durable_susceptibility_delta",
            "replay_and_reentry_support",
            "peer_same_budget_comparison_when_route_or_region_conditioned",
            "AP4_AP5_dependency_controls_intact",
            "unsafe_claims_blocked",
        ],
        "does_not_reopen_n21": True,
        "does_not_retroactively_upgrade_n21": True,
    }


def demotion_precedence() -> dict[str, Any]:
    return {
        "iteration4_candidate_rungs_are_provisional_until_controls": True,
        "final_su_and_n22_c_rungs_assigned_after_control_matrix_only": True,
        "replay_failure_blocks_replay_backed_and_stronger": True,
        "control_failed_closed_blocks_control_backed_and_stronger": True,
        "control_failed_open_invalidates_row": True,
        "not_run_blocks_dependent_rung": True,
        "missing_peer_same_budget_blocks_su5_su6": True,
        "missing_ap_dependency_blocks_dependent_row": True,
        "active_reinforcement_remaining_blocks_durable_delta_support": True,
        "unsafe_claim_requested_blocks_claim": True,
    }


def row_decision_policy() -> dict[str, Any]:
    return {
        "row_decision_enum": ROW_DECISIONS,
        "supported_does_not_permit_unsafe_claims": True,
        "supported_null_control_does_not_permit_susceptibility_claim": True,
        "partial_blocks_susceptibility_claim": True,
        "blocked_blocks_susceptibility_claim": True,
        "rejected_blocks_susceptibility_claim": True,
        "inventory_contract_support_field": "inventory_decision",
        "inventory_rows_keep_row_decision": "not_applicable",
    }


def claim_boundary_schema() -> dict[str, Any]:
    return {
        "global_unsafe_claim_flags": unsafe_claim_flags(),
        "row_specific_blocked_relabels_separate": True,
        "producer_mediated_fields_are_not_substrate_carried": True,
        "naturalization_debt_fields_are_not_native_support": True,
        "n19_boundary_context_is_not_evidence": True,
        "n21_wr_nd_context_is_not_susceptibility_evidence": True,
        "blocked_claims": GLOBAL_UNSAFE_CLAIMS,
    }


def closeout_status_enums() -> dict[str, list[str]]:
    return {
        "susceptibility_update_status": [
            "susceptibility_update_supported_bounded_candidate",
            "susceptibility_update_partial_or_blocked",
            "susceptibility_update_rejected",
        ],
        "durable_geometry_modification_status": [
            "durable_geometry_modification_supported_bounded_candidate",
            "durable_geometry_modification_partial_or_blocked",
            "durable_geometry_modification_rejected",
        ],
        "n21_nd6_bridge_status": N21_ND6_BRIDGE_STATUS_VALUES,
    }


def primitive_schema_rows(i1: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in i1["source_contract_rows"]:
        rows.append(
            {
                "primitive_id": row["primitive_id"],
                "source_contract_row": row["source_contract_row"],
                "source_contract_row_digest": row["source_contract_row_digest"],
                "source_current_fields": row["source_current_fields"],
                "producer_mediated_fields": row["producer_mediated_fields"],
                "naturalization_debt_fields": row["naturalization_debt_fields"],
                "blocked_relabel_fields": row["blocked_relabel_fields"],
                "required_control_ids": row["required_control_ids"],
                "same_basin_continuation_rule": row["same_basin_rule"],
                "support_scaffold": row["support_scaffold"],
                "n20_source_downstream_consumption_status": row[
                    "n20_source_downstream_consumption_status"
                ],
                "claim_ceiling": row["claim_ceiling"],
                "schema_row_status": "frozen_from_i1_contract_inventory",
                "i1_contract_structures_read_only": True,
                "contract_consumed_without_redefinition_required": True,
                "row_specific_thresholds_required_before_use": True,
                "positive_evidence_requires_run_artifacts": True,
                "derived_report_only_true_blocks_support": True,
            }
        )
    return rows


def schema_freeze(i1: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_current_definition": source_current_definition(),
        "candidate_evidence_row_schema": candidate_evidence_row_schema(),
        "run_artifact_admissibility_schema": run_artifact_admissibility_schema(),
        "threshold_declaration_policy": threshold_declaration_policy(),
        "susceptibility_delta_schema": susceptibility_delta_schema(),
        "allowed_drift_same_basin_schema": allowed_drift_schema(),
        "historical_interaction_reinforcement_schema": historical_interaction_reinforcement_schema(),
        "peer_same_budget_comparison_schema": peer_same_budget_schema(),
        "durability_metric_schema": durability_metric_schema(),
        "support_coherence_boundary_flux_schema": support_coherence_boundary_flux_schema(),
        "replay_control_schema": replay_control_schema(),
        "active_null_comparability_rule": active_null_comparability_rule(),
        "classification_ladders": ladder_schema(),
        "ap_dependency_schema": ap_dependency_schema(),
        "n21_nd6_bridge_status_schema": n21_nd6_bridge_status_schema(),
        "demotion_precedence": demotion_precedence(),
        "row_decision_policy": row_decision_policy(),
        "claim_boundary_schema": claim_boundary_schema(),
        "closeout_status_enums": closeout_status_enums(),
        "primitive_schema_rows": primitive_schema_rows(i1),
    }


def context_boundary_from_i1(i1: dict[str, Any]) -> dict[str, Any]:
    boundary = i1["source_context_boundary"]
    return {
        "n21_closeout_may_consume_as": boundary["n21_closeout_may_consume_as"],
        "n21_closeout_must_not_consume_as": boundary[
            "n21_closeout_must_not_consume_as"
        ],
        "n19_native_readiness_boundary_consumption": "ap_gap_boundary_only",
        "n19_must_not_consume_as": [
            "susceptibility_update_evidence",
            "durable_geometry_delta",
            "SU_ladder_assignment_source",
        ],
        "markdown_sources_context_only": boundary["markdown_sources_context_only"],
    }


def build_checks(i1: dict[str, Any], freeze: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_schema = freeze["candidate_evidence_row_schema"]
    run_schema = freeze["run_artifact_admissibility_schema"]
    threshold_policy = freeze["threshold_declaration_policy"]
    delta_schema = freeze["susceptibility_delta_schema"]
    drift_schema = freeze["allowed_drift_same_basin_schema"]
    reinforcement_schema = freeze["historical_interaction_reinforcement_schema"]
    peer_schema = freeze["peer_same_budget_comparison_schema"]
    durability_schema = freeze["durability_metric_schema"]
    replay_schema = freeze["replay_control_schema"]
    ladders = freeze["classification_ladders"]
    ap_schema = freeze["ap_dependency_schema"]
    bridge_schema = freeze["n21_nd6_bridge_status_schema"]
    demotion = freeze["demotion_precedence"]
    row_policy = freeze["row_decision_policy"]
    claim_schema = freeze["claim_boundary_schema"]
    primitive_rows = freeze["primitive_schema_rows"]
    i1_row = i1["source_contract_rows"][0]

    return [
        check(
            "source_i1_inventory_passed",
            i1["status"] == "passed"
            and i1["acceptance_state"]
            == "accepted_source_handoff_inventory_no_susceptibility_evidence"
            and not i1["failed_checks"],
            {
                "status": i1["status"],
                "acceptance_state": i1["acceptance_state"],
                "failed_checks": i1["failed_checks"],
            },
        ),
        check(
            "i1_boundary_kept_no_susceptibility_evidence",
            not i1["iteration1_boundary"]["susceptibility_evidence_opened"]
            and not i1["iteration1_boundary"]["su_ladder_rung_assigned"]
            and not i1["iteration1_boundary"]["positive_run_artifacts_consumed"],
            i1["iteration1_boundary"],
        ),
        check(
            "candidate_evidence_row_schema_complete",
            candidate_schema["required_fields"] == CANDIDATE_EVIDENCE_FIELDS
            and set(candidate_schema["field_constraints"].keys())
            == set(CANDIDATE_EVIDENCE_FIELDS),
            {
                "required_field_count": len(candidate_schema["required_fields"]),
                "field_constraint_count": len(candidate_schema["field_constraints"]),
            },
        ),
        check(
            "n19_boundary_only_schema_frozen",
            candidate_schema["field_constraints"][
                "n19_native_readiness_boundary_consumption"
            ]["required_value"]
            == "ap_gap_boundary_only"
            and claim_schema["n19_boundary_context_is_not_evidence"],
            context_boundary_from_i1(i1),
        ),
        check(
            "n20_prefixed_status_frozen",
            primitive_rows[0]["n20_source_downstream_consumption_status"]
            == i1_row["n20_source_downstream_consumption_status"],
            primitive_rows[0]["n20_source_downstream_consumption_status"],
        ),
        check(
            "run_artifact_admissibility_fail_closed",
            run_schema["required_fields"] == REQUIRED_RUN_ARTIFACT_FIELDS
            and "artifact_manifest" in run_schema["required_fields"]
            and run_schema["artifact_paths_must_exist"]
            and run_schema["artifact_digests_must_match_file_contents"]
            and run_schema["all_artifact_sha256_match_file_contents_required"]
            and run_schema["derived_report_only_true_blocks_positive_support"],
            run_schema,
        ),
        check(
            "threshold_policy_declared_before_use",
            threshold_policy["row_specific_thresholds_declared_before_use"]
            and not threshold_policy[
                "outcome_inspection_before_threshold_declaration_allowed"
            ]
            and not threshold_policy["retune_after_outcome_allowed"],
            threshold_policy,
        ),
        check(
            "susceptibility_delta_schema_blocks_labels",
            delta_schema["delta_must_be_source_current"]
            and delta_schema["route_label_only_delta_blocks_support"]
            and delta_schema["reinforcement_schedule_only_delta_blocks_support"]
            and delta_schema["post_hoc_delta_construction_blocks_support"],
            delta_schema,
        ),
        check(
            "allowed_drift_and_same_basin_schema_frozen",
            drift_schema["out_of_scope_drift_blocks_row"]
            and drift_schema["delta_not_label_reassignment"]
            and bool(drift_schema["allowed_delta_fields"])
            and bool(drift_schema["same_basin_invariant_fields"]),
            drift_schema,
        ),
        check(
            "historical_interaction_active_reinforcement_split_frozen",
            reinforcement_schema["historical_interaction_provenance_present_required_when_claimed"]
            and reinforcement_schema["active_reinforcement_schedule_disabled_required"]
            and reinforcement_schema["active_reinforcement_queue_empty_required"]
            and reinforcement_schema["reinforcement_budget_in_flight_required_value"]
            == 0.0
            and reinforcement_schema["reinforcement_schedule_not_used_as_evidence_required"]
            and reinforcement_schema["active_reinforcement_remaining_rung_effect"][
                "SU4"
            ]
            == "blocked"
            and reinforcement_schema["active_reinforcement_remaining_rung_effect"][
                "n21_nd6_bridge_status"
            ]
            == "blocked_by_producer_residue",
            reinforcement_schema,
        ),
        check(
            "peer_same_budget_comparison_mandatory_when_conditioned",
            peer_schema["required_when_route_or_region_conditioned"]
            and peer_schema["not_required_for_non_route_conditioned_su2_only"]
            and peer_schema["not_applicable_scope_reason_required"]
            and peer_schema["same_delta_in_peer_blocks_route_conditioned_support"]
            and "SU5" in peer_schema["missing_peer_comparison_blocks"]
            and "SU6" in peer_schema["missing_peer_comparison_blocks"],
            peer_schema,
        ),
        check(
            "durability_metrics_frozen",
            set(durability_schema["required_metrics"])
            == {
                "interaction_delta_digest",
                "post_replay_delta_digest",
                "reentry_delta_digest",
                "delta_persistence_ratio",
                "delta_threshold_or_rule",
                "one_window_transient_rejected",
                "global_drift_rejected",
            }
            and durability_schema["delta_persistence_ratio_floor_declared_before_use"]
            and durability_schema["replay_window_survival_required"]
            and durability_schema["later_reentry_survival_required"],
            durability_schema,
        ),
        check(
            "support_coherence_boundary_flux_schema_frozen",
            support_coherence_boundary_flux_schema()["result_status_values"]
            == RESULT_STATUS_VALUES
            and support_coherence_boundary_flux_schema()["field_specific_acceptance"][
                "support_floor_result"
            ]
            == ["preserved", "changed_within_allowed_delta_above_floor"]
            and support_coherence_boundary_flux_schema()["field_specific_acceptance"][
                "flux_or_leakage_result"
            ]
            == ["preserved", "changed_within_bound"]
            and support_coherence_boundary_flux_schema()[
                "changed_status_requires_declared_floor_or_bound_preserved"
            ]
            and support_coherence_boundary_flux_schema()["floor_crossing_blocks_support"],
            support_coherence_boundary_flux_schema(),
        ),
        check(
            "replay_control_schema_frozen",
            replay_schema["status_enum"] == REPLAY_CONTROL_STATUSES
            and replay_schema["replay_name_aliases"]["artifact_replay"]
            == ["artifact_only_replay"]
            and replay_schema["canonical_replay_names_required"]
            and "artifact_replay" in replay_schema["required_replay_modes"]["SU3"]
            and "later_reentry_replay" in replay_schema["required_replay_modes"]["SU5"]
            and replay_schema["not_run_blocks_dependent_rung"]
            and replay_schema["failed_open_invalidates_row"],
            replay_schema,
        ),
        check(
            "active_null_comparability_frozen",
            freeze["active_null_comparability_rule"]["expected_result"]
            == "fail_closed"
            and freeze["active_null_comparability_rule"][
                "weak_or_noncomparable_null_blocks_null_use"
            ],
            freeze["active_null_comparability_rule"],
        ),
        check(
            "su_ladder_complete",
            len(ladders["susceptibility_update_ladder"]) == 7
            and ladders["rows_below_su3_cannot_support_durable_geometry_modification"]
            and ladders["su6_is_handoff_rung_not_agency_claim"]
            and not ladders["n20_contract_completeness_assigns_rungs"]
            and not ladders["n21_closeout_assigns_su_rungs"],
            ladders["susceptibility_update_ladder"],
        ),
        check(
            "n22_closeout_ladder_complete",
            len(ladders["n22_closeout_ladder"]) == 7
            and ladders["n22_c_rungs_classify_tranche_not_individual_row_labels"]
            and ladders["n22_c_rungs_cannot_open_unsafe_claims"],
            ladders["n22_closeout_ladder"],
        ),
        check(
            "ap_dependency_enums_frozen",
            ap_schema["ap4_dependency_status_values"] == AP4_STATUS_VALUES
            and ap_schema["ap5_dependency_status_values"] == AP5_STATUS_VALUES
            and ap_schema["ap4_condition_reason_required"]
            and ap_schema["ap5_condition_reason_required"]
            and {
                row["null_id"]
                for row in ap_schema["iteration3_active_null_expectations"]
            }
            == {
                "route_conditioned_row_missing_AP4",
                "proxy_or_target_conditioned_row_missing_AP5",
                "AP_gap_prose_only",
            },
            ap_schema,
        ),
        check(
            "n21_nd6_bridge_status_enum_frozen",
            bridge_schema["allowed_values"] == N21_ND6_BRIDGE_STATUS_VALUES
            and bridge_schema["initial_status"] == "not_supported"
            and bridge_schema["wording_policy"] == "ND6_bridge_candidate_only"
            and bridge_schema["does_not_reopen_n21"]
            and bridge_schema["does_not_retroactively_upgrade_n21"],
            bridge_schema,
        ),
        check(
            "demotion_precedence_frozen",
            demotion["not_run_blocks_dependent_rung"]
            and demotion["missing_peer_same_budget_blocks_su5_su6"]
            and demotion["active_reinforcement_remaining_blocks_durable_delta_support"]
            and demotion["unsafe_claim_requested_blocks_claim"],
            demotion,
        ),
        check(
            "row_decision_policy_frozen",
            row_policy["row_decision_enum"] == ROW_DECISIONS
            and row_policy["inventory_rows_keep_row_decision"] == "not_applicable"
            and row_policy["supported_null_control_does_not_permit_susceptibility_claim"],
            row_policy,
        ),
        check(
            "claim_boundary_schema_frozen",
            set(claim_schema["global_unsafe_claim_flags"].keys())
            == set(GLOBAL_UNSAFE_CLAIMS)
            and all(value is False for value in claim_schema["global_unsafe_claim_flags"].values())
            and claim_schema["producer_mediated_fields_are_not_substrate_carried"]
            and claim_schema["naturalization_debt_fields_are_not_native_support"]
            and claim_schema["n21_wr_nd_context_is_not_susceptibility_evidence"],
            claim_schema,
        ),
        check(
            "closeout_status_enums_frozen",
            set(closeout_status_enums().keys())
            == {
                "susceptibility_update_status",
                "durable_geometry_modification_status",
                "n21_nd6_bridge_status",
            },
            closeout_status_enums(),
        ),
        check(
            "primitive_schema_row_frozen_from_i1",
            len(primitive_rows) == 1
            and primitive_rows[0]["source_contract_row"]
            == "n20_i5_row_03_susceptibility_update"
            and primitive_rows[0]["same_basin_continuation_rule"]
            == i1_row["same_basin_rule"]
            and primitive_rows[0]["support_scaffold"] == i1_row["support_scaffold"]
            and primitive_rows[0]["i1_contract_structures_read_only"],
            {
                "source_contract_row": primitive_rows[0]["source_contract_row"],
                "source_contract_row_digest": primitive_rows[0][
                    "source_contract_row_digest"
                ],
                "same_basin_rule_id": primitive_rows[0][
                    "same_basin_continuation_rule"
                ]["rule_id"],
                "support_scaffold_id": primitive_rows[0]["support_scaffold"][
                    "support_id"
                ],
            },
        ),
        check(
            "no_positive_evidence_opened",
            True,
            {
                "schema_freeze_only": True,
                "susceptibility_evidence_opened": False,
                "su_ladder_rung_assigned": False,
                "n22_closeout_ladder_rung_assigned": False,
                "positive_run_artifacts_consumed": False,
            },
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
    freeze = schema_freeze(i1)
    checks = build_checks(i1, freeze)

    payload: dict[str, Any] = {
        "artifact_id": "n22_susceptibility_schema_and_controls",
        "schema_version": "n22_susceptibility_schema_and_controls_v1",
        "experiment": (
            "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
        ),
        "iteration": 2,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_susceptibility_schema_frozen_no_positive_evidence",
        "purpose": (
            "Freeze N22 susceptibility-update schemas, ladders, source-current "
            "admissibility, durability metrics, AP dependency rules, active "
            "reinforcement controls, and claim boundary before positive probes."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n22_i1_source_handoff_inventory"),
            source_record(I1_REPORT_PATH, "n22_i1_source_handoff_inventory_report"),
        ],
        "source_inventory_output_digest": i1["output_digest"],
        "context_source_boundary": context_boundary_from_i1(i1),
        "schema_freeze": freeze,
        "iteration2_boundary": {
            "schema_freeze_only": True,
            "susceptibility_evidence_opened": False,
            "susceptibility_update_supported": False,
            "durable_geometry_modification_supported": False,
            "su_ladder_rung_assigned": False,
            "n22_closeout_ladder_rung_assigned": False,
            "n21_nd6_bridge_status": "not_supported",
            "positive_run_artifacts_consumed": False,
            "ready_for_iteration_3_active_nulls": True,
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
        payload["acceptance_state"] = "blocked_susceptibility_schema_checks_failed"

    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    freeze = data["schema_freeze"]
    checks = data["checks"]
    lines: list[str] = [
        "# N22 Iteration 2 - Susceptibility Schema And Controls",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 2 freezes the N22 schema and control contract. It opens no",
        "positive susceptibility evidence and assigns no SU or N22-C rung.",
        "",
        "## Frozen Ladders",
        "",
        "| Ladder | Count | Boundary |",
        "| --- | ---: | --- |",
        (
            "| SU | "
            f"{len(freeze['classification_ladders']['susceptibility_update_ladder'])} | "
            "Rows below SU3 cannot support durable geometry modification; SU6 is N23 handoff only. |"
        ),
        (
            "| N22-C | "
            f"{len(freeze['classification_ladders']['n22_closeout_ladder'])} | "
            "Tranche-level closeout ladder; not semantic learning or agency. |"
        ),
        "",
        "## Key Frozen Policies",
        "",
        "- N19 is consumed as `ap_gap_boundary_only`, not susceptibility evidence.",
        "- N20 inherited status is mirrored as `n20_source_downstream_consumption_status`.",
        "- Candidate rows require source-current inputs and thresholds declared before use.",
        "- Candidate rows require an `artifact_manifest` with repository-relative paths, roles, and SHA-256 digests.",
        "- Support/coherence/boundary/flux acceptance is field-specific; changed values must preserve the declared floor or bound.",
        "- Historical interaction provenance is separated from active reinforcement.",
        "- Active reinforcement schedule, queue, and in-flight budget must be absent for durable-delta support.",
        "- Active reinforcement can leave SU1/SU2 descriptive traces, but blocks SU4, SU5, SU6, N22-C4, N22-C5, N22-C6, and the ND6 bridge.",
        "- Route/region-conditioned rows require peer same-budget comparison and global-drift rejection.",
        "- Non-route SU2 rows may mark peer comparison `not_applicable` only with `non_route_conditioned_SU2_only` scope reason.",
        "- `artifact_only_replay` is an alias for canonical `artifact_replay`.",
        "- AP4/AP5 dependencies use closed enums and row-local condition reasons.",
        "- I3 must include AP-gap active nulls for missing AP4, missing AP5, and prose-only AP gap handling.",
        "- N21 ND6 bridge remains `not_supported` until source-backed SU5/SU6 evidence exists.",
        "",
        "## Required Candidate Field Count",
        "",
        f"`{len(freeze['candidate_evidence_row_schema']['required_fields'])}` fields",
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
            "I2 is a schema freeze. It does not show susceptibility update, durable",
            "geometry modification, semantic learning, choice, agency, native",
            "support, sentience, Phase 8, or ant-ecology implementation.",
            "",
            "The next step is Iteration 3 active nulls and failure baselines.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)
    if payload["failed_checks"]:
        raise SystemExit(f"failed checks: {payload['failed_checks']}")


if __name__ == "__main__":
    main()
