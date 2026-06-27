#!/usr/bin/env python3
"""Build N24 Iteration 2 schema/control freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_abundance_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n24_abundance_schema_and_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_abundance_schema_and_controls.py"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_source_handoff_inventory.json"
)
I1_REPORT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "reports/n24_source_handoff_inventory.md"
)
N20_NATIVE_FUNCTION_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_native_function_proxy_contract.json"
)
N20_SAME_BASIN_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N23_CLOSEOUT_PATH = (
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "outputs/n23_closeout_and_n24_handoff.json"
)

SOURCE_CONTRACT_ROW = "n20_i4_row_05_surplus_supported_optionality"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_05_surplus_supported_optionality"
PRIMITIVE_ID = "surplus_supported_optionality"

ROW_DECISIONS = ["supported", "partial", "blocked", "rejected", "not_applicable"]
REPLAY_CONTROL_STATUSES = [
    "passed",
    "failed_closed",
    "failed_open",
    "not_run",
    "not_applicable",
]
AP4_DEPENDENCY_STATUS_VALUES = [
    "required_recorded",
    "not_applicable",
    "missing_blocks_row",
]
AP5_DEPENDENCY_STATUS_VALUES = [
    "conditional_required_recorded",
    "not_applicable",
    "missing_blocks_row",
]
AP4_CONTEXT_STATUS_VALUES = [
    "n23_bridge_candidate_consumed",
    "lower_n23_context_consumed",
    "not_applicable",
    "missing_blocks_row",
]
TRACE_STATUS_VALUES = ["present", "missing", "not_applicable"]
TRACE_ORIGIN_VALUES = [
    "source_current_same_run",
    "deterministic_replay_of_source_run",
    "declared_replay_family",
    "producer_label",
    "report_derived",
    "independent_run_assembly",
]
OPTIONAL_BRANCH_EVIDENCE_MODE_VALUES = [
    "source_current_available_unexecuted",
    "source_current_executed",
    "source_current_cost_projection",
    "deterministic_replay_validation",
]
SUPPORT_MEASUREMENT_SCOPE_VALUES = [
    "maintenance_basin_node_set",
    "maintenance_basin_min_node",
    "declared_support_region",
    "route_local_support",
]
SUPPORT_AGGREGATION_METHOD_VALUES = [
    "min",
    "sum",
    "mean",
    "declared_rule",
]
SURPLUS_BUDGET_OWNER_VALUES = [
    "source_current_geometry",
    "declared_producer_surface",
    "mixed_declared",
    "hidden_budget_relief_blocks_row",
    "not_recorded_blocks_row",
]
ARTIFACT_ROLE_VALUES = [
    "source_contract",
    "inherited_context",
    "runtime_trace",
    "surplus_margin_trace",
    "maintenance_floor_trace",
    "optional_continuation_set_trace",
    "optional_branch_trace",
    "boundary_integrity_trace",
    "flux_leakage_trace",
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
RESULT_STATUS_VALUES = [
    "preserved",
    "changed_within_allowed_delta_above_floor",
    "changed_within_bound",
    "crossed_floor",
    "exceeded_bound",
    "missing",
    "not_applicable",
]
CONTROL_IDS = [
    "hidden_budget_relief_control",
    "floor_crossing_as_abundance_control",
    "surplus_without_optional_continuation_control",
    "optionality_without_surplus_control",
    "proxy_only_optional_branch_gain_control",
    "optional_branch_label_only_control",
    "single_optional_branch_relabel_control",
    "independent_run_optional_assembly_control",
    "maintenance_basin_shift_control",
    "floor_renormalization_as_surplus_control",
    "post_hoc_surplus_construction_control",
    "n23_selection_context_relabel_as_abundance_control",
    "reward_maximization_relabel_control",
    "semantic_choice_relabel_control",
    "agency_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control",
    "ap4_final_reclassification_relabel_control",
    "ap5_proxy_gap_omission_control",
]
UNSAFE_CLAIMS = [
    "agency",
    "ant_ecology_implementation",
    "consciousness",
    "free_will",
    "fully_native_integration",
    "identity_acceptance",
    "native_ant_agency",
    "native_colony_agency",
    "native_support",
    "organism_life",
    "phase8_implementation",
    "reward_maximization",
    "selfhood",
    "semantic_action",
    "semantic_choice",
    "semantic_goal",
    "semantic_goal_ownership",
    "semantic_intention",
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
    "source_current_required_fields",
    "row_specific_thresholds_declared_before_use",
    "n20_source_downstream_consumption_status",
    "n23_source_closeout_status",
    "n23_closeout_required",
    "n23_context_consumption",
    "n23_ap4_bridge_status",
    "ap4_context_status",
    "maintenance_floor_policy",
    "maintenance_basin_id",
    "maintenance_basin_signature_digest",
    "support_measurement_scope",
    "support_aggregation_method",
    "surplus_channel_policy",
    "support_floor_value",
    "coherence_floor_value",
    "boundary_integrity_floor_value",
    "flux_or_leakage_bound",
    "optionality_window",
    "pre_surplus_geometry_trace",
    "support_surplus_margin_trace",
    "coherence_surplus_margin_trace",
    "residual_support_margin_under_optionality",
    "residual_coherence_margin_under_optionality",
    "optional_flux_drain_margin",
    "maintenance_floor_trace",
    "optional_continuation_set_trace",
    "optional_continuation_count",
    "optional_continuation_availability_count",
    "jointly_admissible_optional_continuation_count",
    "optional_branch_records",
    "optional_branch_evidence_mode",
    "optional_branch_support_coherence_traces",
    "optional_branch_boundary_flux_traces",
    "boundary_integrity_under_optionality_trace",
    "optional_flux_does_not_drain_maintenance_support",
    "optional_flux_does_not_drain_maintenance_support_status",
    "surplus_budget_owner",
    "hidden_budget_relief_absent",
    "reward_or_proxy_label_absent_or_blocked",
    "same_basin_continuation_rule",
    "same_basin_invariant_fields",
    "out_of_scope_drift_blocks_row",
    "optionality_not_label_reassignment",
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
    "surplus_trace_digest",
    "optional_continuation_trace_digest",
    "maintenance_floor_trace_digest",
    "replay_surplus_digest",
    "replay_optionality_digest",
    "surplus_persistence_ratio",
    "optional_branch_persistence_ratio",
    "surplus_threshold_or_rule",
    "optionality_threshold_or_rule",
    "hidden_budget_relief_rejected",
    "floor_crossing_rejected",
    "surplus_without_optional_continuation_rejected_or_demoted",
    "optionality_without_surplus_rejected",
    "proxy_only_success_rejected",
    "optional_branch_label_only_rejected",
    "independent_run_optional_assembly_rejected",
    "maintenance_basin_shift_rejected",
    "floor_renormalization_rejected",
    "post_hoc_surplus_rejected",
    "n23_context_relabel_rejected",
    "producer_residue_fields",
    "naturalization_debt_fields",
    "blocked_relabel_fields",
    "claim_ceiling",
    "unsafe_claim_flags",
    "row_decision",
    "surplus_supported_optionality_claim_allowed",
    "semantic_choice_claim_allowed",
    "reward_maximization_claim_allowed",
    "agency_claim_allowed",
    "native_support_claim_allowed",
    "final_global_ap4_reclassification_supported",
    "derived_report_only",
    "artifact_manifest",
    "artifact_paths",
    "artifact_sha256",
    "artifact_paths_equal_manifest_paths",
    "artifact_sha256_equal_manifest_sha256",
    "all_artifact_sha256_match_file_contents",
    "output_digest",
]
OPTIONAL_BRANCH_RECORD_FIELDS = [
    "branch_id",
    "source_node_id",
    "target_node_id",
    "edge_id_or_route_id",
    "trace_origin",
    "trace_status",
    "optionality_window_step_range",
    "support_before",
    "support_after_or_projected_after",
    "coherence_before",
    "coherence_after_or_projected_after",
    "support_surplus_margin_before",
    "support_surplus_margin_after",
    "coherence_surplus_margin_before",
    "coherence_surplus_margin_after",
    "boundary_integrity_result",
    "flux_or_leakage_result",
    "optional_flux_cost",
    "maintenance_floor_preserved",
    "reward_or_proxy_label_used",
    "producer_enumeration_used",
    "admissibility_status",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def digest_output(output: dict[str, Any]) -> str:
    digest_source = dict(output)
    digest_source.pop("output_digest", None)
    return digest_value(digest_source)


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def find_contract_row(contract_data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in contract_data.get("contract_rows", []):
        if isinstance(row, dict) and row.get("row_id") == row_id:
            return row
    raise KeyError(f"Missing contract row: {row_id}")


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
    return {claim: False for claim in UNSAFE_CLAIMS}


def all_false(flags: dict[str, Any]) -> bool:
    return bool(flags) and all(value is False for value in flags.values())


def has_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/") or value.startswith("file" + "://") or (
            len(value) > 2 and value[1] == ":" and value[2] in ("\\", "/")
        )
    if isinstance(value, dict):
        return any(has_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(has_absolute_path(item) for item in value)
    return False


def candidate_evidence_row_schema(i1: dict[str, Any], i4_digest: str, i5_digest: str) -> dict[str, Any]:
    constraints: dict[str, dict[str, Any]] = {
        field: {"type": "recorded", "constraint": "required for candidate rows"}
        for field in CANDIDATE_EVIDENCE_FIELDS
    }
    constraints.update(
        {
            "source_contract_row": {
                "type": "string",
                "required_value": SOURCE_CONTRACT_ROW,
                "constraint": "N20 I4 primitive contract source row must not drift",
            },
            "source_consumable_contract_row": {
                "type": "string",
                "required_value": CONSUMABLE_CONTRACT_ROW,
                "constraint": "N20 I5 same-basin/control row must not drift",
            },
            "source_contract_row_digest": {
                "type": "sha256_string",
                "required_value": i4_digest,
                "constraint": "digest over N20 I4 primitive descriptor row",
            },
            "source_consumable_contract_row_digest": {
                "type": "sha256_string",
                "required_value": i5_digest,
                "constraint": "digest over N20 I5 same-basin/control row",
            },
            "source_output_digest": {
                "type": "sha256_string",
                "required_value": i1["output_digest"],
                "constraint": "records consumed I1 inventory digest",
            },
            "source_current_inputs": {
                "type": "list[string]",
                "constraint": (
                    "actual LGRC runtime, replay, snapshot, event-log, optional "
                    "branch, or trace artifact inputs consumed by this row; not "
                    "limited to the canonical primitive fields"
                ),
            },
            "source_current_required_fields": {
                "type": "list[string]",
                "required_values": i1["contract_inventory_rows"][0][
                    "source_current_fields"
                ],
                "constraint": (
                    "canonical N20 surplus-supported optionality fields that "
                    "candidate rows must map from their source_current_inputs"
                ),
            },
            "row_specific_thresholds_declared_before_use": {
                "type": "object",
                "required_fields": [
                    "path",
                    "sha256",
                    "declared_before_use",
                    "threshold_record",
                ],
                "required_nested_values": {"declared_before_use": True},
                "constraint": (
                    "candidate rows must carry the predeclared threshold "
                    "record artifact; missing object or declared_before_use=false "
                    "blocks AB2+ support"
                ),
            },
            "n20_source_downstream_consumption_status": {
                "type": "string",
                "required_value": i1["contract_inventory_rows"][0][
                    "n20_source_downstream_consumption_status"
                ],
                "constraint": "prefixed inherited source status required",
            },
            "n23_source_closeout_status": {
                "type": "string",
                "required_value": i1["n23_context_boundary"][
                    "n23_source_closeout_status"
                ],
                "constraint": "prefixed inherited N23 closeout status required",
            },
            "n23_closeout_required": {
                "type": "boolean",
                "required_value": True,
                "constraint": "missing or invalid N23 closeout blocks N23 bridge context",
            },
            "n23_context_consumption": {
                "type": "enum",
                "allowed_values": [
                    "n23_bridge_candidate_consumed",
                    "bounded_lower_rung_context_only",
                    "not_available",
                ],
                "constraint": "N23 context is conditional and fail-closed",
            },
            "n23_ap4_bridge_status": {
                "type": "enum",
                "allowed_values": [
                    "bridge_candidate_supported",
                    "not_consumable_as_bridge_candidate",
                ],
                "constraint": "lower/missing N23 closeout cannot supply AP4 bridge context",
            },
            "ap4_context_status": {
                "type": "enum",
                "allowed_values": AP4_CONTEXT_STATUS_VALUES,
                "constraint": "local context only; not final global AP4 reclassification",
            },
            "maintenance_basin_id": {
                "type": "string",
                "constraint": "identifies the maintenance basin whose surplus is measured",
            },
            "maintenance_basin_signature_digest": {
                "type": "sha256_string",
                "constraint": "detects maintenance-basin shift or identity drift",
            },
            "support_measurement_scope": {
                "type": "enum",
                "allowed_values": SUPPORT_MEASUREMENT_SCOPE_VALUES,
                "constraint": (
                    "freezes the support locus before support surplus is computed; "
                    "maintenance_basin_node_set means the full declared basin node "
                    "set, with aggregation method recorded separately"
                ),
            },
            "support_aggregation_method": {
                "type": "enum",
                "allowed_values": SUPPORT_AGGREGATION_METHOD_VALUES,
                "constraint": "freezes support aggregation before support surplus is computed",
            },
            "surplus_channel_policy": {
                "type": "enum",
                "allowed_values": [
                    "support_surplus_required_and_coherence_floor_preserved",
                    "support_and_coherence_surplus_required",
                    "support_or_coherence_surplus_with_other_floor_preserved",
                ],
                "required_value": "support_surplus_required_and_coherence_floor_preserved",
                "constraint": (
                    "AB2 requires support surplus above floor while coherence "
                    "floor remains preserved"
                ),
            },
            "support_floor_value": {
                "type": "number_or_declared_rule",
                "constraint": "must be declared before surplus outcome inspection",
            },
            "coherence_floor_value": {
                "type": "number_or_declared_rule",
                "constraint": "must be declared before surplus outcome inspection",
            },
            "boundary_integrity_floor_value": {
                "type": "number_or_declared_rule",
                "constraint": "must be declared before optionality outcome inspection",
            },
            "flux_or_leakage_bound": {
                "type": "number_or_declared_rule",
                "constraint": "must be declared before optionality outcome inspection",
            },
            "optionality_window": {
                "type": "object",
                "required_fields": ["window_id", "start_step", "end_step"],
                "constraint": "declared before optionality outcome inspection",
            },
            "support_surplus_margin_trace": {
                "type": "object",
                "formula": "observed_support - support_floor_value",
                "constraint": "AB2 requires positive support surplus margin",
            },
            "coherence_surplus_margin_trace": {
                "type": "object",
                "formula": "observed_coherence - coherence_floor_value",
                "constraint": "AB2 support should preserve coherence surplus or declared floor",
            },
            "residual_support_margin_under_optionality": {
                "type": "number_or_trace",
                "formula": "min_support_during_optionality_window - support_floor_value",
                "constraint": "AB3 requires positive residual support margin",
            },
            "residual_coherence_margin_under_optionality": {
                "type": "number_or_trace",
                "formula": "min_coherence_during_optionality_window - coherence_floor_value",
                "constraint": "AB3 requires positive residual coherence margin",
            },
            "optional_flux_drain_margin": {
                "type": "number_or_trace",
                "formula": "flux_or_leakage_bound - observed_optional_flux_drain",
                "constraint": "AB3 requires optional flux not to drain maintenance support",
            },
            "optional_continuation_set_trace": {
                "type": "object",
                "constraint": "AB3 requires original same-run source-current optional set",
            },
            "optional_continuation_count": {
                "type": "integer",
                "constraint": (
                    "descriptive count of optional continuation records; does "
                    "not by itself satisfy AB3 or AB5"
                ),
                "rung_effect": (
                    "AB3 uses optional_continuation_availability_count; AB5 "
                    "uses jointly_admissible_optional_continuation_count"
                ),
            },
            "optional_continuation_availability_count": {
                "type": "integer",
                "minimum_for_ab3": 2,
                "constraint": "available same-window source-current alternatives",
            },
            "jointly_admissible_optional_continuation_count": {
                "type": "integer",
                "minimum_for_ab5": 2,
                "constraint": "jointly admissible under same maintenance surplus and budget envelope",
            },
            "optional_branch_records": {
                "type": "list[object]",
                "required_item_fields": OPTIONAL_BRANCH_RECORD_FIELDS,
                "constraint": "branch records must follow frozen schema",
            },
            "optional_branch_evidence_mode": {
                "type": "enum",
                "allowed_values": OPTIONAL_BRANCH_EVIDENCE_MODE_VALUES,
                "rung_effects": {
                    "source_current_available_unexecuted": (
                        "can support AB3 if same-window and floors hold"
                    ),
                    "source_current_cost_projection": (
                        "can support only bounded/provisional AB3 unless replay validates it"
                    ),
                    "source_current_executed": "eligible for AB4+ if replay/control gates pass",
                    "deterministic_replay_validation": "eligible for AB4+ as replay validation",
                },
            },
            "surplus_budget_owner": {
                "type": "enum",
                "allowed_values": SURPLUS_BUDGET_OWNER_VALUES,
                "constraint": "sets producer-mediated/native-support claim ceiling",
            },
            "hidden_budget_relief_absent": {
                "type": "boolean",
                "required_value_for_positive_support": True,
                "constraint": "false blocks positive AB support",
            },
            "reward_or_proxy_label_absent_or_blocked": {
                "type": "boolean",
                "required_value_for_positive_support": True,
                "constraint": "reward/proxy label cannot replace surplus optionality",
            },
            "same_basin_continuation_rule": {
                "type": "object",
                "required_source": "N20 I5 same-basin rule from I1",
                "inherited_rule_content": i1["contract_inventory_rows"][0][
                    "same_basin_rule"
                ],
                "constraint": "must be consumed without redefinition",
            },
            "optionality_not_label_reassignment": {
                "type": "boolean",
                "required_value": True,
                "constraint": "false blocks AB3+ support",
            },
            "optional_flux_does_not_drain_maintenance_support": {
                "type": "boolean_or_scope_status",
                "required_value_for_ab3_plus": True,
                "allowed_non_ab3_values": ["not_applicable_until_I5", "not_run"],
                "constraint": (
                    "AB3+ requires true; AB2-only surplus rows should mark "
                    "optional flux as not applicable/not run rather than false"
                ),
            },
            "optional_flux_does_not_drain_maintenance_support_status": {
                "type": "enum",
                "allowed_values": [
                    "preserved",
                    "failed",
                    "not_run",
                    "not_applicable",
                    "missing",
                ],
                "constraint": (
                    "positive AB3+ rows require preserved; AB2-only rows may "
                    "record not_run until optionality is opened"
                ),
            },
            "support_floor_result": {
                "type": "enum",
                "allowed_for_support": [
                    "preserved",
                    "changed_within_allowed_delta_above_floor",
                ],
                "allowed_values": RESULT_STATUS_VALUES,
            },
            "coherence_floor_result": {
                "type": "enum",
                "allowed_for_support": [
                    "preserved",
                    "changed_within_allowed_delta_above_floor",
                ],
                "allowed_values": RESULT_STATUS_VALUES,
            },
            "boundary_integrity_result": {
                "type": "enum",
                "allowed_for_support": [
                    "preserved",
                    "changed_within_allowed_delta_above_floor",
                ],
                "allowed_values": RESULT_STATUS_VALUES,
            },
            "flux_or_leakage_result": {
                "type": "enum",
                "allowed_for_support": ["preserved", "changed_within_bound"],
                "allowed_values": RESULT_STATUS_VALUES,
            },
            "replay_result": {
                "type": "object",
                "required_modes": [
                    "artifact_replay",
                    "snapshot_load_replay",
                    "duplicate_replay",
                ],
                "status_values": REPLAY_CONTROL_STATUSES,
                "constraint": (
                    "not_run blocks AB4+; AB3 may be provisional without "
                    "replay when original same-run optionality and floor gates pass"
                ),
            },
            "control_results": {
                "type": "list[object]",
                "required_item_fields": [
                    "control_id",
                    "control_status",
                    "blocked_condition",
                    "expected_result",
                    "actual_result",
                    "claim_allowed_when_control_triggers",
                    "control_satisfied_for_positive_row",
                    "rung_effect",
                ],
                "required_control_ids": CONTROL_IDS,
                "status_values": REPLAY_CONTROL_STATUSES,
                "constraint": "failed_open invalidates row; not_run blocks dependent rung",
            },
            "ap4_dependency_status": {
                "type": "enum",
                "allowed_values": AP4_DEPENDENCY_STATUS_VALUES,
                "constraint": "route/branch-conditioned optionality requires required_recorded",
            },
            "ap5_dependency_status": {
                "type": "enum",
                "allowed_values": AP5_DEPENDENCY_STATUS_VALUES,
                "constraint": "proxy/reward/target-conditioned rows require conditional_required_recorded",
            },
            "row_decision": {
                "type": "enum",
                "allowed_values": ROW_DECISIONS,
                "constraint": "supported alone does not allow unsafe claims",
            },
            "surplus_supported_optionality_claim_allowed": {
                "type": "boolean",
                "constraint": "true only when AB gates, replay, controls, and claim boundary pass",
            },
            "semantic_choice_claim_allowed": {
                "type": "boolean",
                "required_value": False,
                "constraint": "semantic choice remains blocked",
            },
            "reward_maximization_claim_allowed": {
                "type": "boolean",
                "required_value": False,
                "constraint": "reward maximization remains blocked row-locally",
            },
            "agency_claim_allowed": {
                "type": "boolean",
                "required_value": False,
                "constraint": "agency remains blocked",
            },
            "native_support_claim_allowed": {
                "type": "boolean",
                "required_value": False,
                "constraint": "native support remains blocked",
            },
            "final_global_ap4_reclassification_supported": {
                "type": "boolean",
                "required_value": False,
                "constraint": (
                    "N24 may consume local N23 AP4 context but cannot finalize "
                    "global AP4 reclassification"
                ),
            },
            "derived_report_only": {
                "type": "boolean",
                "required_value_for_positive_support": False,
                "constraint": "true blocks positive AB support",
            },
            "artifact_manifest": {
                "type": "list[object]",
                "required_item_fields": ["path", "sha256", "artifact_role"],
                "allowed_artifact_roles": ARTIFACT_ROLE_VALUES,
            },
            "artifact_paths_equal_manifest_paths": {
                "type": "boolean",
                "required_value_for_positive_support": True,
            },
            "artifact_sha256_equal_manifest_sha256": {
                "type": "boolean",
                "required_value_for_positive_support": True,
            },
            "all_artifact_sha256_match_file_contents": {
                "type": "boolean",
                "required_value_for_positive_support": True,
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
        "unsafe_claim_request_forces_claim_allowed_false": True,
        "claim_allowed_false_for_non_supported_rows": True,
    }


def optional_branch_record_schema() -> dict[str, Any]:
    return {
        "required_fields": OPTIONAL_BRANCH_RECORD_FIELDS,
        "trace_origin_allowed_values": TRACE_ORIGIN_VALUES,
        "trace_status_allowed_values": TRACE_STATUS_VALUES,
        "optional_branch_evidence_mode_values": OPTIONAL_BRANCH_EVIDENCE_MODE_VALUES,
        "optional_branch_evidence_mode_rung_effects": {
            "source_current_available_unexecuted": (
                "can support AB3 if same-window and floors hold"
            ),
            "source_current_cost_projection": (
                "can support only bounded/provisional AB3 unless replay validates it"
            ),
            "source_current_executed": "eligible for AB4+ if replay/control gates pass",
            "deterministic_replay_validation": "eligible for AB4+ as replay validation",
        },
        "admissibility_status_values": [
            "admissible",
            "blocked_by_floor",
            "blocked_by_boundary",
            "blocked_by_flux",
            "blocked_by_label_only",
            "blocked_by_independent_run_assembly",
            "blocked_by_hidden_budget",
        ],
        "reward_or_proxy_label_used_must_be_false_for_support": True,
        "producer_enumeration_used_is_producer_residue": True,
    }


def surplus_schema() -> dict[str, Any]:
    return {
        "source_current_surplus_definition": (
            "observed support/coherence above declared maintenance floors in "
            "LGRC-visible traces, before optionality outcome inspection"
        ),
        "maintenance_floor_policy": {
            "support_floor_declared_before_use": True,
            "coherence_floor_declared_before_use": True,
            "boundary_integrity_floor_declared_before_use": True,
            "flux_or_leakage_bound_declared_before_use": True,
            "floor_renormalization_after_outcome_blocks_row": True,
            "maintenance_basin_shift_blocks_surplus_claim": True,
        },
        "surplus_formulas": {
            "support_surplus_margin": "observed_support - support_floor_value",
            "coherence_surplus_margin": (
                "observed_coherence - coherence_floor_value"
            ),
            "residual_support_margin_under_optionality": (
                "min_support_during_optionality_window - support_floor_value"
            ),
            "residual_coherence_margin_under_optionality": (
                "min_coherence_during_optionality_window - coherence_floor_value"
            ),
            "optional_flux_drain_margin": (
                "flux_or_leakage_bound - observed_optional_flux_drain"
            ),
        },
        "ab2_support_rule": "support surplus margin must be positive",
        "ab3_support_rule": (
            "residual support and coherence margins remain positive while "
            "optional branches are open"
        ),
    }


def optionality_schema() -> dict[str, Any]:
    return {
        "original_optional_continuation_set_trace": {
            "must_be_same_source_current_run": True,
            "must_be_inside_declared_optionality_window": True,
            "must_not_be_created_by_declared_replay_family": True,
            "must_not_be_independent_run_assembly": True,
            "must_not_be_label_only": True,
        },
        "declared_replay_family": {
            "may_validate_replay_stability": True,
            "may_validate_repeatability": True,
            "may_validate_stress_behavior": True,
            "may_create_original_ab3_optional_set": False,
        },
        "availability_vs_joint_admissibility": {
            "optional_continuation_availability_count": (
                "same-window source-current optional alternatives"
            ),
            "jointly_admissible_optional_continuation_count": (
                "alternatives jointly admissible under same maintenance surplus "
                "and budget envelope"
            ),
            "ab3_minimum_availability_count": 2,
            "ab5_minimum_jointly_admissible_count": 2,
        },
        "optional_branch_record_schema": optional_branch_record_schema(),
        "optional_branch_evidence_mode_policy": {
            "source_current_available_unexecuted_can_support_ab3": True,
            "source_current_cost_projection_is_provisional_until_replay": True,
            "source_current_executed_or_replay_validated_needed_for_ab4_plus": True,
        },
        "optional_flux_does_not_drain_maintenance_support_required": True,
    }


def surplus_budget_owner_schema() -> dict[str, Any]:
    return {
        "allowed_values": SURPLUS_BUDGET_OWNER_VALUES,
        "rung_ceilings": {
            "source_current_geometry": "may support AB2..AB6 if all other gates pass",
            "declared_producer_surface": (
                "may support producer-mediated AB2/AB3/AB4 candidate only; "
                "cannot support native support, Phase 8, or naturalized abundance"
            ),
            "mixed_declared": (
                "must record producer residue and naturalization debt; cannot "
                "exceed bounded producer-mediated candidate without source-"
                "backed naturalization evidence"
            ),
            "hidden_budget_relief_blocks_row": "blocks positive support",
            "not_recorded_blocks_row": "blocks positive support",
        },
    }


def artifact_schema() -> dict[str, Any]:
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
        "positive_ab_support_forbidden_if_only_artifact_roles": (
            POSITIVE_SUPPORT_FORBIDDEN_IF_ONLY_ROLES
        ),
        "derived_report_only_true_blocks_positive_support": True,
        "missing_required_artifact_blocks_ab_assignment": True,
        "digest_mismatch_blocks_ab_assignment": True,
    }


def control_matrix_schema() -> dict[str, Any]:
    return {
        "required_control_ids": CONTROL_IDS,
        "status_values": REPLAY_CONTROL_STATUSES,
        "failed_closed_meaning": "blocker triggered and claim was correctly rejected",
        "failed_open_meaning": "blocker triggered but claim still passed",
        "not_run_blocks_dependent_rung": True,
        "not_applicable_policy": {
            "allowed_only_with_scope_reason": True,
            "scope_reason_required": True,
            "affected_rung_required": True,
            "not_applicable_cannot_satisfy_required_control": True,
            "not_applicable_for_required_ab4_or_ab5_control_blocks_dependent_rung": True,
        },
        "control_effects": {
            "hidden_budget_relief_control": "blocks positive support",
            "floor_crossing_as_abundance_control": "blocks AB2+",
            "surplus_without_optional_continuation_control": "allows AB2 but blocks AB3+",
            "optionality_without_surplus_control": "blocks AB2+ and AB3+",
            "proxy_only_optional_branch_gain_control": "blocks optionality support",
            "optional_branch_label_only_control": "blocks AB3+",
            "single_optional_branch_relabel_control": "blocks AB3+",
            "independent_run_optional_assembly_control": "blocks original AB3 optional set",
            "maintenance_basin_shift_control": "blocks surplus claim",
            "floor_renormalization_as_surplus_control": "blocks surplus claim",
            "post_hoc_surplus_construction_control": "blocks AB2+",
            "n23_selection_context_relabel_as_abundance_control": "blocks N23 context relabel",
            "reward_maximization_relabel_control": "blocks reward/goal overclaim",
            "semantic_choice_relabel_control": "blocks semantic choice",
            "agency_relabel_control": "blocks agency",
            "native_support_relabel_control": "blocks native support",
            "phase8_relabel_control": "blocks Phase 8",
            "ap4_final_reclassification_relabel_control": "blocks final global AP4 reclassification",
            "ap5_proxy_gap_omission_control": "blocks proxy/reward rows missing AP5 dependency",
        },
    }


def ladder_schema() -> dict[str, Any]:
    return {
        "ab_ladder": [
            {"rung": "AB0", "meaning": "no source-current surplus optionality evidence"},
            {"rung": "AB1", "meaning": "run artifact with possible surplus or optionality context"},
            {"rung": "AB2", "meaning": "source-current surplus above declared maintenance floor"},
            {"rung": "AB3", "meaning": "surplus opens source-current optional continuation set while floors hold"},
            {"rung": "AB4", "meaning": "replay/control-backed surplus-supported optionality candidate"},
            {"rung": "AB5", "meaning": "stress/threshold-backed abundance candidate with hidden-budget, proxy, and floor controls clean"},
            {"rung": "AB6", "meaning": "N25-ready bounded surplus-supported optionality evidence"},
        ],
        "ab_rung_rules": {
            "rows_below_ab3_cannot_support_optionality": True,
            "rows_below_ab4_cannot_support_replay_control_backed_abundance": True,
            "ab6_is_handoff_not_agency_or_semantic_choice": True,
        },
        "n24_closeout_ladder": [
            {"rung": "N24-C0", "meaning": "contract-only closeout"},
            {"rung": "N24-C1", "meaning": "active-null/control discipline established"},
            {"rung": "N24-C2", "meaning": "surplus partial"},
            {"rung": "N24-C3", "meaning": "source-current optional continuation candidate"},
            {"rung": "N24-C4", "meaning": "replay/control-backed surplus optionality candidate"},
            {"rung": "N24-C5", "meaning": "stress/threshold-backed abundance candidate"},
            {"rung": "N24-C6", "meaning": "N25-ready bounded surplus-supported optionality evidence"},
        ],
        "closeout_ladder_claim_boundary": (
            "tranche classification only; not semantic choice, agency, native "
            "support, sentience, Phase 8, or ant ecology"
        ),
    }


def ap_gap_schema(i1: dict[str, Any]) -> dict[str, Any]:
    return {
        "ap4_dependency_status_values": AP4_DEPENDENCY_STATUS_VALUES,
        "ap5_dependency_status_values": AP5_DEPENDENCY_STATUS_VALUES,
        "ap4_context_status_values": AP4_CONTEXT_STATUS_VALUES,
        "ap4_context_status_from_i1": i1["n19_ap_gap_boundary"]["ap4_context_status"],
        "final_global_ap4_reclassification_supported": False,
        "route_or_branch_conditioned_optionality_requires_ap4": True,
        "proxy_reward_target_conditioned_optionality_requires_ap5": True,
        "ap4_condition_reason_required": True,
        "ap5_condition_reason_required": True,
        "ap_gap_prose_only_allowed": False,
    }


def claim_boundary_schema() -> dict[str, Any]:
    return {
        "unsafe_claim_flags": unsafe_claim_flags(),
        "all_unsafe_claim_flags_required_false": True,
        "surplus_supported_optionality_claim_allowed_requires_all_ab_gates": True,
        "semantic_choice_claim_allowed": False,
        "agency_claim_allowed": False,
        "native_support_claim_allowed": False,
        "reward_maximization_claim_allowed": False,
        "sentience_claim_allowed": False,
        "phase8_opened": False,
        "ant_ecology_implementation_opened": False,
        "hypothesis_a_or_b_demoted_if_hypothesis_c_fails": True,
    }


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    native_contract = load_json(N20_NATIVE_FUNCTION_PATH)
    same_basin_contract = load_json(N20_SAME_BASIN_PATH)
    native_row = find_contract_row(native_contract, SOURCE_CONTRACT_ROW)
    same_basin_row = find_contract_row(same_basin_contract, CONSUMABLE_CONTRACT_ROW)
    native_row_digest = digest_value(native_row)
    same_basin_row_digest = digest_value(same_basin_row)
    candidate_schema = candidate_evidence_row_schema(
        i1,
        native_row_digest,
        same_basin_row_digest,
    )
    claim_boundary = claim_boundary_schema()
    output: dict[str, Any] = {
        "artifact_id": "n24_i2_abundance_schema_and_controls",
        "schema_version": "n24_abundance_schema_and_controls_v1",
        "experiment": "N24",
        "iteration": 2,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "schema, ladder, and control freeze only; no N24 primitive evidence",
        "status": "passed",
        "acceptance_state": (
            "accepted_abundance_schema_and_controls_frozen_no_surplus_optionality_evidence"
        ),
        "source_artifacts": [
            source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            source_record(I1_REPORT_PATH, "n24_i1_source_handoff_report"),
            source_record(N20_NATIVE_FUNCTION_PATH, "n20_i4_native_function_proxy_contract"),
            source_record(N20_SAME_BASIN_PATH, "n20_i5_same_basin_contract"),
            source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "i1_inventory_reference": {
            "path": I1_OUTPUT_PATH,
            "status": i1["status"],
            "acceptance_state": i1["acceptance_state"],
            "output_digest": i1["output_digest"],
            "n23_closeout_validated": i1["n23_context_boundary"][
                "n23_closeout_validated"
            ],
            "n23_context_consumption": i1["n23_context_boundary"][
                "n23_context_consumption"
            ],
            "ab_ladder_rung_assigned": i1["evidence_boundary"][
                "ab_ladder_rung_assigned"
            ],
        },
        "source_contract_digests": {
            "source_contract_row": SOURCE_CONTRACT_ROW,
            "source_contract_row_digest": native_row_digest,
            "source_consumable_contract_row": CONSUMABLE_CONTRACT_ROW,
            "source_consumable_contract_row_digest": same_basin_row_digest,
            "digests_are_distinct": native_row_digest != same_basin_row_digest,
        },
        "candidate_evidence_row_schema": candidate_schema,
        "source_current_surplus_schema": surplus_schema(),
        "optional_continuation_schema": optionality_schema(),
        "same_basin_rule_freeze": {
            "source": "N20 I5 same-basin rule from I1",
            "must_be_consumed_without_redefinition": True,
            "rule": i1["contract_inventory_rows"][0]["same_basin_rule"],
        },
        "surplus_budget_owner_schema": surplus_budget_owner_schema(),
        "support_measurement_schema": {
            "maintenance_basin_id_required": True,
            "maintenance_basin_signature_digest_required": True,
            "support_measurement_scope_values": SUPPORT_MEASUREMENT_SCOPE_VALUES,
            "support_aggregation_method_values": SUPPORT_AGGREGATION_METHOD_VALUES,
            "measurement_scope_frozen_before_surplus_calculation": True,
            "maintenance_basin_shift_blocks_surplus_claim": True,
        },
        "n23_ap4_context_invariants": {
            "if_n23_ap4_bridge_status_bridge_candidate_supported": {
                "ap4_context_status_may_be": ["n23_bridge_candidate_consumed"],
            },
            "if_n23_ap4_bridge_status_not_consumable": {
                "ap4_context_status_must_not_be": ["n23_bridge_candidate_consumed"],
            },
            "if_n23_context_consumption_bounded_lower_rung_context_only": {
                "ap4_context_status_must_be": "lower_n23_context_consumed",
            },
            "if_n23_context_consumption_not_available": {
                "ap4_context_status_must_be": "missing_blocks_row",
            },
        },
        "artifact_admissibility_schema": artifact_schema(),
        "support_coherence_boundary_flux_result_schema": {
            "result_status_values": RESULT_STATUS_VALUES,
            "support_floor_allowed_for_support": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "coherence_floor_allowed_for_support": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "boundary_integrity_allowed_for_support": [
                "preserved",
                "changed_within_allowed_delta_above_floor",
            ],
            "flux_or_leakage_allowed_for_support": [
                "preserved",
                "changed_within_bound",
            ],
            "not_applicable_blocks_ab2_plus_when_field_required": True,
        },
        "replay_requirements": {
            "required_modes_for_ab4_plus": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
            ],
            "replay_required_for_ab3": False,
            "ab3_without_replay_status": "provisional_source_current_optionality_candidate",
            "declared_replay_family_cannot_create_original_ab3_set": True,
            "not_run_blocks_dependent_rung": True,
            "failed_open_invalidates_row": True,
        },
        "control_matrix_schema": control_matrix_schema(),
        "active_null_comparability_schema": {
            "same_source_contract_row_digest": True,
            "same_consumable_contract_row_digest": True,
            "same_basin_signature_fields": True,
            "same_runtime_envelope_or_declared_pairing_rule": True,
            "same_budget_schedule_digest_when_applicable": True,
            "comparability_failure_blocks_control_consumption": True,
        },
        "local_ladders": ladder_schema(),
        "ap_gap_schema": ap_gap_schema(i1),
        "row_decision_policy": {
            "allowed_values": ROW_DECISIONS,
            "supported_does_not_automatically_allow_claim": True,
            "rejected_or_blocked_forces_claim_allowed_false": True,
            "partial_keeps_final_closeout_provisional": True,
            "not_applicable_requires_scope_reason": True,
        },
        "claim_boundary_schema": claim_boundary,
        "evidence_boundary": {
            "primitive_evidence_opened": False,
            "surplus_supported_optionality_supported": False,
            "ab_ladder_rung_assigned": False,
            "n24_closeout_ladder_rung_assigned": False,
            "candidate_rows_classified": False,
            "ready_for_iteration_3_active_nulls": True,
        },
    }
    checks = [
        {
            "check": "i1_inventory_consumed_and_passed",
            "passed": i1["status"] == "passed" and not i1["failed_checks"],
            "detail": output["i1_inventory_reference"],
        },
        {
            "check": "n23_closeout_context_gate_preserved",
            "passed": i1["n23_context_boundary"]["n23_closeout_validated"] is True
            and i1["n23_context_boundary"]["n23_context_consumption"]
            == "n23_bridge_candidate_consumed",
            "detail": i1["n23_context_boundary"],
        },
        {
            "check": "candidate_schema_required_fields_complete",
            "passed": set(i1["required_future_candidate_fields"]).issubset(
                set(CANDIDATE_EVIDENCE_FIELDS)
            )
            and len(candidate_schema["required_fields"]) == len(CANDIDATE_EVIDENCE_FIELDS),
            "detail": {
                "required_field_count": len(candidate_schema["required_fields"]),
                "i1_required_future_fields": i1["required_future_candidate_fields"],
            },
        },
        {
            "check": "direct_n23_closeout_source_recorded",
            "passed": any(
                source["path"] == N23_CLOSEOUT_PATH
                and source["source_role"] == "n23_closeout_and_n24_handoff_context"
                and source.get("status") == "passed"
                for source in output["source_artifacts"]
            ),
            "detail": [
                source
                for source in output["source_artifacts"]
                if source["path"] == N23_CLOSEOUT_PATH
            ],
        },
        {
            "check": "source_contract_digests_split",
            "passed": native_row_digest != same_basin_row_digest,
            "detail": output["source_contract_digests"],
        },
        {
            "check": "surplus_formulas_frozen",
            "passed": set(output["source_current_surplus_schema"]["surplus_formulas"])
            == {
                "support_surplus_margin",
                "coherence_surplus_margin",
                "residual_support_margin_under_optionality",
                "residual_coherence_margin_under_optionality",
                "optional_flux_drain_margin",
            },
            "detail": output["source_current_surplus_schema"]["surplus_formulas"],
        },
        {
            "check": "optional_branch_record_schema_frozen",
            "passed": output["optional_continuation_schema"][
                "optional_branch_record_schema"
            ]["required_fields"]
            == OPTIONAL_BRANCH_RECORD_FIELDS,
            "detail": output["optional_continuation_schema"][
                "optional_branch_record_schema"
            ],
        },
        {
            "check": "source_current_inputs_split_from_required_fields",
            "passed": (
                output["candidate_evidence_row_schema"]["field_constraints"][
                    "source_current_inputs"
                ]["type"]
                == "list[string]"
                and output["candidate_evidence_row_schema"]["field_constraints"][
                    "source_current_required_fields"
                ]["required_values"]
                == i1["contract_inventory_rows"][0]["source_current_fields"]
            ),
            "detail": {
                "source_current_inputs": output["candidate_evidence_row_schema"][
                    "field_constraints"
                ]["source_current_inputs"],
                "source_current_required_fields": output["candidate_evidence_row_schema"][
                    "field_constraints"
                ]["source_current_required_fields"],
            },
        },
        {
            "check": "surplus_channel_policy_frozen",
            "passed": output["candidate_evidence_row_schema"]["field_constraints"][
                "surplus_channel_policy"
            ]["required_value"]
            == "support_surplus_required_and_coherence_floor_preserved",
            "detail": output["candidate_evidence_row_schema"]["field_constraints"][
                "surplus_channel_policy"
            ],
        },
        {
            "check": "optional_branch_evidence_mode_frozen",
            "passed": output["optional_continuation_schema"][
                "optional_branch_record_schema"
            ]["optional_branch_evidence_mode_values"]
            == OPTIONAL_BRANCH_EVIDENCE_MODE_VALUES,
            "detail": output["optional_continuation_schema"][
                "optional_branch_record_schema"
            ]["optional_branch_evidence_mode_rung_effects"],
        },
        {
            "check": "control_results_record_schema_frozen",
            "passed": output["candidate_evidence_row_schema"]["field_constraints"][
                "control_results"
            ]["type"]
            == "list[object]",
            "detail": output["candidate_evidence_row_schema"]["field_constraints"][
                "control_results"
            ],
        },
        {
            "check": "row_local_reward_and_ap4_blockers_frozen",
            "passed": output["candidate_evidence_row_schema"]["field_constraints"][
                "reward_maximization_claim_allowed"
            ]["required_value"]
            is False
            and output["candidate_evidence_row_schema"]["field_constraints"][
                "final_global_ap4_reclassification_supported"
            ]["required_value"]
            is False,
            "detail": {
                "reward_maximization_claim_allowed": output[
                    "candidate_evidence_row_schema"
                ]["field_constraints"]["reward_maximization_claim_allowed"],
                "final_global_ap4_reclassification_supported": output[
                    "candidate_evidence_row_schema"
                ]["field_constraints"][
                    "final_global_ap4_reclassification_supported"
                ],
            },
        },
        {
            "check": "n23_ap4_context_invariants_frozen",
            "passed": output["n23_ap4_context_invariants"][
                "if_n23_context_consumption_bounded_lower_rung_context_only"
            ]["ap4_context_status_must_be"]
            == "lower_n23_context_consumed",
            "detail": output["n23_ap4_context_invariants"],
        },
        {
            "check": "support_measurement_scope_frozen",
            "passed": output["support_measurement_schema"][
                "maintenance_basin_signature_digest_required"
            ]
            is True
            and "maintenance_basin_node_set"
            in output["support_measurement_schema"]["support_measurement_scope_values"],
            "detail": output["support_measurement_schema"],
        },
        {
            "check": "optional_continuation_count_descriptive_only",
            "passed": "does not by itself satisfy AB3 or AB5"
            in output["candidate_evidence_row_schema"]["field_constraints"][
                "optional_continuation_count"
            ]["constraint"],
            "detail": output["candidate_evidence_row_schema"]["field_constraints"][
                "optional_continuation_count"
            ],
        },
        {
            "check": "same_basin_rule_content_frozen",
            "passed": output["same_basin_rule_freeze"]["rule"]["rule_id"]
            == "n20_i5_surplus_supported_optionality_same_basin_rule",
            "detail": output["same_basin_rule_freeze"],
        },
        {
            "check": "control_not_applicable_policy_frozen",
            "passed": output["control_matrix_schema"]["not_applicable_policy"][
                "scope_reason_required"
            ]
            is True
            and output["control_matrix_schema"]["not_applicable_policy"][
                "not_applicable_cannot_satisfy_required_control"
            ]
            is True,
            "detail": output["control_matrix_schema"]["not_applicable_policy"],
        },
        {
            "check": "ab3_replay_interaction_frozen",
            "passed": output["replay_requirements"]["replay_required_for_ab3"]
            is False
            and output["replay_requirements"][
                "declared_replay_family_cannot_create_original_ab3_set"
            ]
            is True,
            "detail": output["replay_requirements"],
        },
        {
            "check": "same_run_original_optionality_rule_frozen",
            "passed": output["optional_continuation_schema"][
                "original_optional_continuation_set_trace"
            ]["must_be_same_source_current_run"]
            is True
            and output["optional_continuation_schema"]["declared_replay_family"][
                "may_create_original_ab3_optional_set"
            ]
            is False,
            "detail": output["optional_continuation_schema"],
        },
        {
            "check": "ab3_ab5_count_requirements_frozen",
            "passed": output["optional_continuation_schema"][
                "availability_vs_joint_admissibility"
            ]["ab3_minimum_availability_count"]
            == 2
            and output["optional_continuation_schema"][
                "availability_vs_joint_admissibility"
            ]["ab5_minimum_jointly_admissible_count"]
            == 2,
            "detail": output["optional_continuation_schema"][
                "availability_vs_joint_admissibility"
            ],
        },
        {
            "check": "surplus_budget_owner_rung_ceilings_frozen",
            "passed": set(output["surplus_budget_owner_schema"]["allowed_values"])
            == set(SURPLUS_BUDGET_OWNER_VALUES)
            and "hidden_budget_relief_blocks_row"
            in output["surplus_budget_owner_schema"]["rung_ceilings"],
            "detail": output["surplus_budget_owner_schema"],
        },
        {
            "check": "canonical_controls_frozen",
            "passed": output["control_matrix_schema"]["required_control_ids"]
            == CONTROL_IDS,
            "detail": output["control_matrix_schema"]["required_control_ids"],
        },
        {
            "check": "artifact_admissibility_fail_closed",
            "passed": output["artifact_admissibility_schema"][
                "all_artifact_sha256_match_file_contents_required"
            ]
            is True
            and output["artifact_admissibility_schema"][
                "derived_report_only_true_blocks_positive_support"
            ]
            is True,
            "detail": output["artifact_admissibility_schema"],
        },
        {
            "check": "ladders_frozen",
            "passed": len(output["local_ladders"]["ab_ladder"]) == 7
            and len(output["local_ladders"]["n24_closeout_ladder"]) == 7,
            "detail": output["local_ladders"],
        },
        {
            "check": "ap_gap_schema_frozen",
            "passed": output["ap_gap_schema"][
                "final_global_ap4_reclassification_supported"
            ]
            is False
            and output["ap_gap_schema"][
                "proxy_reward_target_conditioned_optionality_requires_ap5"
            ]
            is True,
            "detail": output["ap_gap_schema"],
        },
        {
            "check": "claim_boundary_forces_unsafe_false",
            "passed": all_false(claim_boundary["unsafe_claim_flags"])
            and claim_boundary["agency_claim_allowed"] is False
            and claim_boundary["native_support_claim_allowed"] is False,
            "detail": claim_boundary,
        },
        {
            "check": "no_positive_n24_evidence_opened",
            "passed": output["evidence_boundary"]["primitive_evidence_opened"] is False
            and output["evidence_boundary"]["ab_ladder_rung_assigned"] is False
            and output["evidence_boundary"]["candidate_rows_classified"] is False,
            "detail": output["evidence_boundary"],
        },
    ]
    output["checks"] = checks
    output["no_absolute_paths"] = not has_absolute_path(output)
    output["checks"].append(
        {
            "check": "no_absolute_paths",
            "passed": output["no_absolute_paths"],
            "detail": "all stored paths are repository-relative",
        }
    )
    output["failed_checks"] = [
        check["check"] for check in output["checks"] if check["passed"] is not True
    ]
    if output["failed_checks"]:
        output["status"] = "blocked"
        output["acceptance_state"] = "blocked_abundance_schema_and_controls"
    output["output_digest"] = digest_output(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    checks_lines = [
        "| Check | Passed | Detail |",
        "| --- | --- | --- |",
    ]
    for check in output["checks"]:
        checks_lines.append(
            "| `{name}` | `{passed}` | {detail} |".format(
                name=check["check"],
                passed=str(check["passed"]).lower(),
                detail=json.dumps(
                    check["detail"],
                    sort_keys=True,
                    ensure_ascii=True,
                    separators=(",", ":"),
                ),
            )
        )
    source_lines = [
        "| Role | Path | Status | SHA-256 |",
        "| --- | --- | --- | --- |",
    ]
    for source in output["source_artifacts"]:
        source_lines.append(
            "| {role} | `{path}` | `{status}` | `{sha}` |".format(
                role=source["source_role"],
                path=source["path"],
                status=source.get("status", "markdown_context_only"),
                sha=source["sha256"],
            )
        )
    report = "\n".join(
        [
            "# N24 Iteration 2 - Abundance Schema And Controls",
            "",
            "## Summary",
            "",
            f"Status: `{output['status']}`",
            "",
            f"Acceptance state: `{output['acceptance_state']}`",
            "",
            f"Output digest: `{output['output_digest']}`",
            "",
            "Iteration 2 freezes the N24 candidate evidence schema, surplus",
            "formulas, optionality acceptance gates, control matrix, ladders,",
            "AP gap discipline, and claim boundary. It opens no N24 primitive",
            "evidence and assigns no AB rung.",
            "",
            "## Source Artifacts",
            "",
            *source_lines,
            "",
            "## I1 Reference",
            "",
            "```text",
            f"i1_status = {output['i1_inventory_reference']['status']}",
            "i1_acceptance_state = "
            f"{output['i1_inventory_reference']['acceptance_state']}",
            f"i1_output_digest = {output['i1_inventory_reference']['output_digest']}",
            "n23_closeout_validated = "
            f"{str(output['i1_inventory_reference']['n23_closeout_validated']).lower()}",
            "n23_context_consumption = "
            f"{output['i1_inventory_reference']['n23_context_consumption']}",
            "```",
            "",
            "## Frozen Contract Digests",
            "",
            "```text",
            "source_contract_row = "
            f"{output['source_contract_digests']['source_contract_row']}",
            "source_contract_row_digest = "
            f"{output['source_contract_digests']['source_contract_row_digest']}",
            "source_consumable_contract_row = "
            f"{output['source_contract_digests']['source_consumable_contract_row']}",
            "source_consumable_contract_row_digest = "
            f"{output['source_contract_digests']['source_consumable_contract_row_digest']}",
            "digests_are_distinct = "
            f"{str(output['source_contract_digests']['digests_are_distinct']).lower()}",
            "```",
            "",
            "## Core Freeze",
            "",
            "```text",
            "candidate_evidence_required_field_count = "
            f"{len(output['candidate_evidence_row_schema']['required_fields'])}",
            "AB ladder frozen = true",
            "N24-C ladder frozen = true",
            "surplus formulas frozen = true",
            "optional branch record schema frozen = true",
            "original optional set same-run only = true",
            "declared replay family cannot create AB3 original set = true",
            "surplus budget owner rung ceilings frozen = true",
            "final_global_ap4_reclassification_supported = false",
            "unsafe claim flags false = true",
            "```",
            "",
            "## Surplus Formulas",
            "",
            "```text",
            *[
                f"{name} = {formula}"
                for name, formula in output["source_current_surplus_schema"][
                    "surplus_formulas"
                ].items()
            ],
            "```",
            "",
            "## Required Controls",
            "",
            "```text",
            *output["control_matrix_schema"]["required_control_ids"],
            "```",
            "",
            "## Evidence Boundary",
            "",
            "```text",
            "primitive_evidence_opened = false",
            "surplus_supported_optionality_supported = false",
            "ab_ladder_rung_assigned = false",
            "n24_closeout_ladder_rung_assigned = false",
            "candidate_rows_classified = false",
            "ready_for_iteration_3_active_nulls = true",
            "```",
            "",
            "## Checks",
            "",
            *checks_lines,
            "",
            "## Interpretation",
            "",
            "Iteration 2 is a schema/control freeze only. It makes it impossible",
            "for later N24 rows to pass by using hidden budget relief, floor",
            "crossing, proxy gain, optional labels, independent-run assembly,",
            "maintenance basin shift, floor renormalization, or N23 selection",
            "context relabeling as abundance. Positive evidence remains unopened",
            "until later source-current probes.",
            "",
        ]
    )
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()
