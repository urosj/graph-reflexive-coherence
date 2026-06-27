#!/usr/bin/env python3
"""Build N23 Iteration 1 source handoff inventory."""

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
OUTPUT = EXPERIMENT / "outputs" / "n23_source_handoff_inventory.json"
REPORT = EXPERIMENT / "reports" / "n23_source_handoff_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/"
    "scripts/build_n23_source_handoff_inventory.py"
)

N20_CLOSEOUT_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_closeout_and_n21_handoff.json"
)
N20_SAME_BASIN_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N20_NATIVE_FUNCTION_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_native_function_proxy_contract.json"
)
N20_PRODUCER_LEDGER_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_producer_residue_ledger.json"
)
N22_CLOSEOUT_PATH = (
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "outputs/n22_closeout_and_n23_handoff.json"
)
N19_CLOSEOUT_PATH = (
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "outputs/n19_closeout_and_handoff.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"

SOURCE_CONTRACT_ROW = "n20_i4_row_04_live_continuation_collapse"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_04_live_continuation_collapse"
PRIMITIVE_ID = "live_continuation_collapse"
EXPECTED_SOURCE_CURRENT_FIELDS = [
    "live_continuation_collapse.live_branch_set_trace",
    "live_continuation_collapse.branch_support_coherence_traces",
    "live_continuation_collapse.collapsed_continuation_trace",
    "live_continuation_collapse.counterfactual_branch_retention_trace",
]
EXPECTED_CONSUMPTION_INPUTS = [
    "live_continuation_set",
    "fake_alternative_controls",
    "producer_preference_injection_blockers",
    "AP4_gap_dependency",
]
EXPECTED_CONTROLS = {
    "label_only_success_control",
    "proxy_only_success_control",
    "hidden_producer_support_control",
    "post_hoc_trace_construction_control",
    "semantic_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control",
    "fake_alternative_control",
    "single_branch_relabel_control",
    "producer_preference_injection_control",
    "post_hoc_selected_branch_control",
}
PLANNED_N23_CANONICAL_CONTROL_IDS = [
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
CANDIDATE_AP4_STATUS_ENUM = [
    "required_recorded",
    "not_applicable",
    "missing_blocks_row",
]
CANDIDATE_AP5_STATUS_ENUM = [
    "conditional_required_recorded",
    "not_applicable",
    "missing_blocks_row",
]
BRANCH_RECORD_ORIGIN_ENUM = [
    "source_current_same_run",
    "replay_fork",
    "producer_label",
    "report_derived",
    "independent_run_assembly",
]
THRESHOLD_FIELDS_TO_FREEZE = [
    "support_floor_value",
    "coherence_floor_value",
    "boundary_integrity_floor_value",
    "flux_or_leakage_bound",
    "collapse_persistence_ratio_threshold",
    "branch_distinguishability_threshold",
    "same_basin_drift_bound",
]
BLOCKED_CLAIMS = [
    "agency",
    "consciousness",
    "free_will",
    "fully_native_integration",
    "identity_acceptance",
    "native_ant_agency",
    "native_colony_agency",
    "native_support",
    "organism_life",
    "phase8_implementation",
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


def source_record(path: str, role: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
    }
    if path.endswith(".json"):
        data = load_json(path)
        record["parseable_json"] = True
        record["status"] = str(data.get("status", "not_recorded"))
        record["acceptance_state"] = str(data.get("acceptance_state", "not_recorded"))
        record["output_digest"] = str(data.get("output_digest", "not_recorded"))
        if role == "n19_native_readiness_boundary":
            record["n23_source_acceptance_interpretation"] = (
                "accepted_ap_gap_boundary_only_no_n23_evidence"
            )
    else:
        record["parseable_json"] = False
        record["status"] = "markdown_context_only"
    return record


def find_contract_row(contract_data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in contract_data.get("contract_rows", []):
        if isinstance(row, dict) and row.get("row_id") == row_id:
            return row
    raise KeyError(f"Missing contract row: {row_id}")


def all_false(flags: dict[str, Any]) -> bool:
    return bool(flags) and all(value is False for value in flags.values())


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in BLOCKED_CLAIMS}


def unique_list(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def control_ids(controls: dict[str, Any]) -> list[str]:
    shared = [
        str(control["control_id"])
        for control in controls.get("shared_controls", [])
        if isinstance(control, dict)
    ]
    primitive_specific = [
        str(control["control_id"])
        for control in controls.get("primitive_specific_controls", [])
        if isinstance(control, dict)
    ]
    return shared + primitive_specific


def source_status(path: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": path,
        "status": str(data.get("status", "not_recorded")),
        "acceptance_state": str(data.get("acceptance_state", "not_recorded")),
        "output_digest": str(data.get("output_digest", "not_recorded")),
    }


def n20_closeout_boundary(n20: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_artifact": N20_CLOSEOUT_PATH,
        "status": str(n20["status"]),
        "acceptance_state": str(n20["acceptance_state"]),
        "final_claim_ceiling": str(n20["final_claim_ceiling"]),
        "final_supported_status": str(n20["final_supported_status"]),
        "n20_contract_complete": bool(n20["n20_contract_complete"]),
        "primitive_evidence_opened": bool(n20["primitive_evidence_opened"]),
        "phase8_opened": bool(n20["phase8_opened"]),
        "native_support_opened": bool(n20["native_support_opened"]),
        "ready_for_n21": bool(n20["n21_handoff"]["ready_for_n21"]),
        "n23_consumption_role": "historical_contract_closeout_context_only",
    }


def contract_inventory_row(row: dict[str, Any], native_row: dict[str, Any]) -> dict[str, Any]:
    same_basin_rule = row["same_basin_continuation_rule"]
    support_scaffold = row["support_scaffold_declaration"]
    proxy_metric = row["proxy_metric_definition"]
    continuation_function = row["continuation_function_descriptor"]
    controls = row["minimum_controls"]

    return {
        "row_id": "n23_i1_row_01_live_continuation_collapse_contract_input",
        "primitive_id": PRIMITIVE_ID,
        "primitive_name": str(row["primitive_name"]),
        "source_contract_row": SOURCE_CONTRACT_ROW,
        "source_consumable_contract_row": str(row["row_id"]),
        "source_i4_row_id": str(row["source_i4_row_id"]),
        "source_contract_row_digest": digest_value(native_row),
        "source_consumable_contract_row_digest": digest_value(row),
        "source_artifact": N20_SAME_BASIN_PATH,
        "source_contract_status": str(row["contract_status"]),
        "n20_source_downstream_consumption_status": str(
            row["downstream_consumption_status"]
        ),
        "contract_consumed_without_redefinition": True,
        "n23_inventory_role": "source_contract_input_only",
        "n23_primitive_evidence_opened": False,
        "live_continuation_collapse_supported": False,
        "n23_ladder_rung_assigned": False,
        "lc_ladder_rung": "not_assigned_contract_inventory_only",
        "n23_closeout_ladder_rung": "not_assigned_inventory_only",
        "allowed_next_assignment_source": "source_backed_N23_evidence_rows_only",
        "source_current_fields": list(row["LGRC_visible_fields"]),
        "producer_mediated_fields": list(row["producer_mediated_fields"]),
        "naturalization_debt_fields": list(row["naturalization_debt_fields"]),
        "blocked_relabel_fields": list(row["blocked_relabel_fields"]),
        "source_role_dependencies": row["source_role_dependencies"],
        "ap_gap_contract": row["ap_gap_contract"],
        "required_n23_inputs": list(row["primitive_specific_consumption_inputs"]),
        "same_basin_rule": {
            "rule_id": same_basin_rule["rule_id"],
            "basin_signature_fields": same_basin_rule["basin_signature_fields"],
            "allowed_drift": same_basin_rule["allowed_drift"],
            "required_support_floor": same_basin_rule["required_support_floor"],
            "required_coherence_floor": same_basin_rule["required_coherence_floor"],
            "boundary_integrity_floor": same_basin_rule["boundary_integrity_floor"],
            "flux_balance_bounds": same_basin_rule["flux_balance_bounds"],
            "replay_requirement": same_basin_rule["replay_requirement"],
            "failure_modes": same_basin_rule["failure_modes"],
            "hidden_producer_support_allowed": same_basin_rule[
                "hidden_producer_support_allowed"
            ],
            "label_only_continuation_allowed": same_basin_rule[
                "label_only_continuation_allowed"
            ],
            "proxy_only_success_allowed": same_basin_rule[
                "proxy_only_success_allowed"
            ],
        },
        "support_scaffold": {
            "support_id": support_scaffold["support_id"],
            "declared_supports": support_scaffold["declared_supports"],
            "required_supports": support_scaffold["required_supports"],
            "optional_supports": support_scaffold["optional_supports"],
            "withdrawable_supports": support_scaffold["withdrawable_supports"],
            "hidden_support_allowed": support_scaffold["hidden_support_allowed"],
            "hidden_support_blocker": support_scaffold["hidden_support_blocker"],
            "producer_supplied_scaffolds": support_scaffold[
                "producer_supplied_scaffolds"
            ],
            "producer_role": support_scaffold["producer_role"],
            "naturalization_debt": support_scaffold["naturalization_debt"],
        },
        "continuation_function_descriptor": {
            "descriptor_id": continuation_function["descriptor_id"],
            "descriptor_kind": continuation_function["descriptor_kind"],
            "continuation_condition": continuation_function[
                "continuation_condition"
            ],
            "basin_signature": continuation_function["basin_signature"],
            "support_floor": continuation_function["support_floor"],
            "coherence_floor": continuation_function["coherence_floor"],
            "boundary_condition": continuation_function["boundary_condition"],
            "flux_condition": continuation_function["flux_condition"],
            "proxy_metric": continuation_function["proxy_metric"],
            "claim_ceiling": continuation_function["claim_ceiling"],
        },
        "proxy_metric_definition": {
            "proxy_id": proxy_metric["proxy_id"],
            "measured_quantity": proxy_metric["measured_quantity"],
            "source_current_inputs": proxy_metric["source_current_inputs"],
            "producer_inputs": proxy_metric["producer_inputs"],
            "proxy_kind": proxy_metric["proxy_kind"],
            "proxy_success_replaces_continuation": proxy_metric[
                "proxy_success_replaces_continuation"
            ],
            "expected_relation_to_continuation_function": proxy_metric[
                "expected_relation_to_continuation_function"
            ],
            "proxy_only_success_blocker": proxy_metric["proxy_only_success_blocker"],
            "collapse_condition": proxy_metric["collapse_condition"],
            "divergence_condition": proxy_metric["divergence_condition"],
        },
        "minimum_controls": {
            "status": controls["status"],
            "all_controls_fail_closed_in_contract": controls["all_controls_fail_closed"],
            "all_controls_have_fail_closed_acceptance_rules": controls[
                "all_controls_fail_closed"
            ],
            "control_ids": control_ids(controls),
            "control_execution_status": "not_run_inventory_only",
        },
        "artifact_invariants": row["artifact_invariants"],
        "source_unsafe_claim_flags": row["unsafe_claim_flags"],
        "unsafe_claim_flags": unsafe_claim_flags(),
        "claim_ceiling": (
            "source contract input only; no N23 primitive evidence, no semantic "
            "choice, no agency, no native support, no sentience, no Phase 8"
        ),
        "row_decision": "not_applicable",
        "inventory_decision": "supported_as_contract_input_only",
        "live_continuation_collapse_claim_allowed": False,
        "semantic_choice_claim_allowed": False,
    }


def n22_context_boundary(n22: dict[str, Any]) -> dict[str, Any]:
    final_closeout = n22["final_closeout"]
    handoff = n22["n23_handoff"]
    claim_boundary = n22["claim_boundary"]
    branch_closeout = n22["branch_closeout"]
    return {
        "source_artifact": N22_CLOSEOUT_PATH,
        "n22_source_closeout_status": str(n22["status"]),
        "n22_source_closeout_acceptance_state": str(n22["acceptance_state"]),
        "n22_source_closeout_final_supported_status": final_closeout[
            "final_supported_status"
        ],
        "status": str(n22["status"]),
        "acceptance_state": str(n22["acceptance_state"]),
        "n22_closeout_ladder_rung": final_closeout["n22_closeout_ladder_rung"],
        "n22_closeout_ladder_rung_assigned": final_closeout[
            "n22_closeout_ladder_rung_assigned"
        ],
        "final_supported_su_ladder_rung": final_closeout[
            "final_supported_su_ladder_rung"
        ],
        "final_supported_status": final_closeout["final_supported_status"],
        "ready_for_n23": final_closeout["ready_for_n23"],
        "producer_mediated_context": True,
        "carrier_branch": branch_closeout["carrier_branch"],
        "packet_branch": branch_closeout["packet_branch"],
        "n21_nd6_bridge": n22["n21_nd6_bridge"],
        "ap_gap_propagation": n22["ap_gap_propagation"],
        "consume_n22_as": handoff["consume_n22_as"],
        "must_not_consume_n22_as": handoff["must_not_consume_n22_as"],
        "handoff_claim_ceiling": handoff["handoff_claim_ceiling"],
        "claim_boundary": claim_boundary,
        "n22_may_supply_live_continuation_collapse_evidence": False,
        "n22_may_supply_semantic_choice_evidence": False,
        "n22_may_supply_native_route_memory_evidence": False,
    }


def n19_ap_gap_boundary(n19: dict[str, Any]) -> dict[str, Any]:
    coverage = n19["ap_level_nat4_coverage"]
    by_level = {row["ap_level"]: row for row in coverage}
    return {
        "source_artifact": N19_CLOSEOUT_PATH,
        "n19_native_readiness_boundary_consumption": "ap_gap_boundary_only",
        "current_implementation_can_generate_claimed_ap_ladder": n19[
            "current_implementation_can_generate_claimed_ap_ladder"
        ],
        "claimed_ladder_generation_status": n19[
            "claimed_ladder_generation_status"
        ],
        "ap_levels_lacking_nat4_evidence": n19["ap_levels_lacking_nat4_evidence"],
        "ap4": {
            "best_nat_level": by_level["AP4"]["best_nat_level"],
            "coverage_status": by_level["AP4"]["coverage_status"],
            "nat4_evidence_present": by_level["AP4"]["nat4_evidence_present"],
            "gap_explanation": by_level["AP4"]["nat4_gap_explanation"],
        },
        "ap5": {
            "best_nat_level": by_level["AP5"]["best_nat_level"],
            "coverage_status": by_level["AP5"]["coverage_status"],
            "nat4_evidence_present": by_level["AP5"]["nat4_evidence_present"],
            "gap_explanation": by_level["AP5"]["nat4_gap_explanation"],
        },
        "n23_ap4_bridge_status": "not_supported_inventory_only",
        "n23_ap5_dependency_status": "conditional_pending_future_rows",
        "candidate_row_ap_dependency_status_enums": {
            "ap4_dependency_status": CANDIDATE_AP4_STATUS_ENUM,
            "ap5_dependency_status": CANDIDATE_AP5_STATUS_ENUM,
            "inventory_meta_status_values_not_valid_for_candidate_rows": [
                "not_supported_inventory_only",
                "conditional_pending_future_rows",
                "required_local_gap_dependency",
            ],
        },
    }


def operational_i2_freeze_targets() -> dict[str, Any]:
    return {
        "live_branch_acceptance": {
            "same_source_current_run_required": True,
            "same_declared_branch_window_required": True,
            "pre_collapse_required": True,
            "branch_specific_support_coherence_required": True,
            "branch_specific_boundary_flux_required": True,
            "branch_record_origin_enum": BRANCH_RECORD_ORIGIN_ENUM,
            "positive_lc2_requires_branch_record_origin": "source_current_same_run",
            "independent_run_assembly_counts_as_live_branch": False,
            "replay_fork_counts_as_original_live_branch": False,
            "report_side_construction_counts_as_live_branch": False,
            "post_hoc_label_counts_as_live_branch": False,
        },
        "counterfactual_retention": {
            "meaning": "immutable_pre_collapse_audit_record",
            "continued_dynamic_activity_after_collapse_required": False,
            "labels_sufficient": False,
            "producer_alternatives_sufficient": False,
            "replay_created_branches_sufficient": False,
            "report_reconstruction_sufficient": False,
        },
        "temporal_ordering": {
            "branch_window_end_lte_collapse_window_start_required": True,
            "selected_reason_must_use_pre_or_in_collapse_traces": True,
            "post_report_selection_reason_allowed": False,
        },
        "selected_branch_reason_enum_to_freeze": [
            "support_gradient_dominance",
            "coherence_floor_dominance",
            "boundary_integrity_dominance",
            "flux_leakage_minimization",
            "susceptibility_delta_conditioned",
            "route_cost_or_conductance_dominance",
            "multi_channel_geometry_dominance",
            "not_supported",
        ],
        "blocked_selected_branch_reasons": [
            "producer_label",
            "producer_preference",
            "random_tie",
            "post_hoc_report_selection",
            "single_branch_relabel",
            "semantic_choice_label",
        ],
        "artifact_roles_to_freeze": [
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
        ],
        "positive_lc_support_forbidden_if_only_artifact_roles": [
            "report",
            "inherited_context",
            "source_contract",
            "closeout",
        ],
        "canonical_control_ids_to_freeze": PLANNED_N23_CANONICAL_CONTROL_IDS,
        "candidate_row_ap_dependency_status_enums": {
            "ap4_dependency_status": CANDIDATE_AP4_STATUS_ENUM,
            "ap5_dependency_status": CANDIDATE_AP5_STATUS_ENUM,
        },
        "threshold_fields_to_freeze_before_positive_probe": THRESHOLD_FIELDS_TO_FREEZE,
        "susceptibility_delta_conditioned_blocker": (
            "susceptibility_delta_conditioned cannot support selection geometry "
            "when the susceptibility delta is only inherited from N22 and not "
            "expressed in N23 source-current branch geometry"
        ),
    }


def build_payload() -> dict[str, Any]:
    n20_closeout = load_json(N20_CLOSEOUT_PATH)
    n20_same_basin = load_json(N20_SAME_BASIN_PATH)
    n20_native = load_json(N20_NATIVE_FUNCTION_PATH)
    n22_closeout = load_json(N22_CLOSEOUT_PATH)
    n19_closeout = load_json(N19_CLOSEOUT_PATH)

    contract_row = find_contract_row(n20_same_basin, CONSUMABLE_CONTRACT_ROW)
    native_row = find_contract_row(n20_native, SOURCE_CONTRACT_ROW)
    inventory_row = contract_inventory_row(contract_row, native_row)

    source_artifacts = [
        source_record(N20_CLOSEOUT_PATH, "n20_closeout_and_handoff_context"),
        source_record(N20_SAME_BASIN_PATH, "n20_i5_same_basin_contract"),
        source_record(N20_NATIVE_FUNCTION_PATH, "n20_i4_native_function_proxy_contract"),
        source_record(N20_PRODUCER_LEDGER_PATH, "n20_producer_residue_ledger"),
        source_record(N22_CLOSEOUT_PATH, "n22_closeout_and_n23_handoff_context"),
        source_record(N19_CLOSEOUT_PATH, "n19_native_readiness_boundary"),
        source_record(N20_HANDOFF_PATH, "n20_n29_handoff"),
        source_record(N20_ROADMAP_PATH, "n20_n29_roadmap"),
    ]

    checks = [
        {
            "check_id": "n20_i5_live_continuation_contract_present_and_complete",
            "passed": contract_row["contract_status"] == "complete"
            and contract_row["row_id"] == CONSUMABLE_CONTRACT_ROW
            and contract_row["source_i4_row_id"] == SOURCE_CONTRACT_ROW,
            "detail": {
                "row_id": contract_row["row_id"],
                "source_i4_row_id": contract_row["source_i4_row_id"],
                "contract_status": contract_row["contract_status"],
                "downstream_consumption_status": contract_row[
                    "downstream_consumption_status"
                ],
            },
        },
        {
            "check_id": "n20_closeout_boundary_parsed",
            "passed": n20_closeout["status"] == "passed"
            and n20_closeout["primitive_evidence_opened"] is False
            and n20_closeout["n20_contract_complete"] is True,
            "detail": {
                "status": n20_closeout["status"],
                "acceptance_state": n20_closeout["acceptance_state"],
                "n20_contract_complete": n20_closeout["n20_contract_complete"],
                "primitive_evidence_opened": n20_closeout[
                    "primitive_evidence_opened"
                ],
            },
        },
        {
            "check_id": "source_current_fields_match_contract",
            "passed": contract_row["LGRC_visible_fields"] == EXPECTED_SOURCE_CURRENT_FIELDS
            and native_row["LGRC_visible_fields"] == EXPECTED_SOURCE_CURRENT_FIELDS,
            "detail": {
                "expected": EXPECTED_SOURCE_CURRENT_FIELDS,
                "same_basin_contract": contract_row["LGRC_visible_fields"],
                "native_function_contract": native_row["LGRC_visible_fields"],
            },
        },
        {
            "check_id": "required_n23_inputs_match_handoff",
            "passed": contract_row["primitive_specific_consumption_inputs"]
            == EXPECTED_CONSUMPTION_INPUTS,
            "detail": {
                "expected": EXPECTED_CONSUMPTION_INPUTS,
                "contract": contract_row["primitive_specific_consumption_inputs"],
            },
        },
        {
            "check_id": "required_controls_recorded",
            "passed": set(inventory_row["minimum_controls"]["control_ids"])
            == EXPECTED_CONTROLS,
            "detail": inventory_row["minimum_controls"]["control_ids"],
        },
        {
            "check_id": "planned_canonical_controls_ready_for_i2_i3",
            "passed": {
                "random_tie_as_collapse_control",
                "missing_counterfactual_retention_control",
                "N22_susceptibility_as_choice_relabel_control",
                "route_conditioned_row_missing_AP4",
                "proxy_conditioned_row_missing_AP5",
                "AP_gap_prose_only",
                "agency_relabel",
            }.issubset(set(PLANNED_N23_CANONICAL_CONTROL_IDS)),
            "detail": PLANNED_N23_CANONICAL_CONTROL_IDS,
        },
        {
            "check_id": "producer_and_debt_fields_recorded",
            "passed": bool(inventory_row["producer_mediated_fields"])
            and bool(inventory_row["naturalization_debt_fields"])
            and bool(inventory_row["blocked_relabel_fields"]),
            "detail": {
                "producer_mediated_fields": inventory_row["producer_mediated_fields"],
                "naturalization_debt_fields": inventory_row[
                    "naturalization_debt_fields"
                ],
                "blocked_relabel_fields": inventory_row["blocked_relabel_fields"],
            },
        },
        {
            "check_id": "n22_closeout_ready_for_n23_context_only",
            "passed": n22_closeout["final_closeout"]["ready_for_n23"] is True
            and n22_closeout["final_closeout"]["n22_closeout_ladder_rung"] == "N22-C6"
            and n22_closeout["final_closeout"]["final_supported_su_ladder_rung"]
            == "SU5_producer_mediated_bounded_susceptibility_update_candidate"
            and "semantic_choice"
            in n22_closeout["n23_handoff"]["must_not_consume_n22_as"],
            "detail": {
                "ready_for_n23": n22_closeout["final_closeout"]["ready_for_n23"],
                "n22_closeout_ladder_rung": n22_closeout["final_closeout"][
                    "n22_closeout_ladder_rung"
                ],
                "final_supported_su_ladder_rung": n22_closeout["final_closeout"][
                    "final_supported_su_ladder_rung"
                ],
                "must_not_consume_n22_as": n22_closeout["n23_handoff"][
                    "must_not_consume_n22_as"
                ],
            },
        },
        {
            "check_id": "n22_source_closeout_status_prefixed_field_present",
            "passed": n22_context_boundary(n22_closeout)["n22_source_closeout_status"]
            == "passed",
            "detail": {
                "n22_source_closeout_status": n22_context_boundary(n22_closeout)[
                    "n22_source_closeout_status"
                ],
                "n22_source_closeout_acceptance_state": n22_context_boundary(
                    n22_closeout
                )["n22_source_closeout_acceptance_state"],
            },
        },
        {
            "check_id": "ap_gap_boundary_preserved",
            "passed": "AP4" in n19_closeout["ap_levels_lacking_nat4_evidence"]
            and "AP5" in n19_closeout["ap_levels_lacking_nat4_evidence"]
            and n22_closeout["ap_gap_propagation"]["ap4_dependency_status"]
            == "required_recorded"
            and n22_closeout["ap_gap_propagation"]["ap4_nat4_gap_resolved"] is False,
            "detail": {
                "n19_ap_levels_lacking_nat4_evidence": n19_closeout[
                    "ap_levels_lacking_nat4_evidence"
                ],
                "n22_ap_gap_propagation": n22_closeout["ap_gap_propagation"],
                "contract_ap_gap": contract_row["ap_gap_contract"],
            },
        },
        {
            "check_id": "no_live_continuation_evidence_opened",
            "passed": inventory_row["n23_primitive_evidence_opened"] is False
            and inventory_row["live_continuation_collapse_supported"] is False
            and inventory_row["n23_ladder_rung_assigned"] is False,
            "detail": {
                "n23_primitive_evidence_opened": inventory_row[
                    "n23_primitive_evidence_opened"
                ],
                "live_continuation_collapse_supported": inventory_row[
                    "live_continuation_collapse_supported"
                ],
                "lc_ladder_rung": inventory_row["lc_ladder_rung"],
            },
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all_false(inventory_row["unsafe_claim_flags"])
            and all_false(inventory_row["source_unsafe_claim_flags"])
            and all_false(n22_closeout["claim_boundary"]["unsafe_claim_flags"]),
            "detail": {
                "n23_unsafe_claim_flags": inventory_row["unsafe_claim_flags"],
                "n20_source_unsafe_claim_flags": inventory_row[
                    "source_unsafe_claim_flags"
                ],
                "n22_claim_boundary_flags": n22_closeout["claim_boundary"][
                    "unsafe_claim_flags"
                ],
            },
        },
        {
            "check_id": "inventory_decision_uses_standard_row_decision",
            "passed": inventory_row["row_decision"] == "not_applicable"
            and inventory_row["inventory_decision"] == "supported_as_contract_input_only",
            "detail": {
                "row_decision": inventory_row["row_decision"],
                "inventory_decision": inventory_row["inventory_decision"],
            },
        },
        {
            "check_id": "controls_declared_not_executed_in_inventory",
            "passed": inventory_row["minimum_controls"]["control_execution_status"]
            == "not_run_inventory_only",
            "detail": inventory_row["minimum_controls"],
        },
    ]

    payload: dict[str, Any] = {
        "schema_version": "n23_i1_source_handoff_inventory_v1",
        "experiment": "N23_lgrc_live_continuation_collapse_selection_geometry",
        "iteration": 1,
        "artifact_id": "n23_i1_source_handoff_inventory",
        "purpose": "inventory N20/N22/N19 sources before opening N23 evidence",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_source_handoff_inventory_no_live_continuation_evidence",
        "source_artifacts": source_artifacts,
        "source_artifact_statuses_purpose": (
            "compact parse/status subset for source JSONs consumed by I1; "
            "source_artifacts remains the full SHA/role inventory"
        ),
        "source_artifact_statuses": [
            source_status(N20_SAME_BASIN_PATH),
            source_status(N20_NATIVE_FUNCTION_PATH),
            source_status(N22_CLOSEOUT_PATH),
            source_status(N19_CLOSEOUT_PATH),
        ],
        "n20_closeout_boundary": n20_closeout_boundary(n20_closeout),
        "contract_inventory_rows": [inventory_row],
        "n22_context_boundary": n22_context_boundary(n22_closeout),
        "n19_ap_gap_boundary": n19_ap_gap_boundary(n19_closeout),
        "operational_i2_freeze_targets": operational_i2_freeze_targets(),
        "required_future_candidate_fields": [
            "source_current_inputs",
            "row_specific_thresholds_declared_before_use",
            "branch_window",
            "collapse_window",
            "pre_collapse_geometry_trace",
            "live_branch_set_trace",
            "branch_support_coherence_traces",
            "branch_boundary_flux_traces",
            "collapsed_continuation_trace",
            "counterfactual_branch_retention_trace",
            "selected_branch_source_current_reason",
            "branch_record_origin",
            "support_floor_value",
            "coherence_floor_value",
            "boundary_integrity_floor_value",
            "flux_or_leakage_bound",
            "collapse_persistence_ratio_threshold",
            "branch_distinguishability_threshold",
            "same_basin_drift_bound",
            "same_basin_continuation_rule",
            "artifact_manifest",
            "artifact_sha256",
            "all_artifact_sha256_match_file_contents",
        ],
        "evidence_boundary": {
            "positive_run_artifacts_consumed": False,
            "live_continuation_collapse_evidence_opened": False,
            "live_branch_set_supported": False,
            "collapse_supported": False,
            "counterfactual_retention_supported": False,
            "lc_ladder_rung_assigned": False,
            "n23_closeout_ladder_rung_assigned": False,
            "n23_closeout_ladder_rung": "N23-C0_inventory_only",
            "ap4_bridge_status": "not_supported_inventory_only",
            "ap5_dependency_status": "conditional_pending_future_rows",
            "semantic_choice_supported": False,
            "semantic_intention_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
        },
        "claim_boundary": {
            "claim_ceiling": (
                "source handoff inventory only; N23 evidence ceiling remains "
                "LC0/N23-C0 until source-current N23 run artifacts exist"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
            "blocked_claims": unique_list(
                BLOCKED_CLAIMS
                + [
                    "semantic_choice",
                    "semantic_intention",
                    "free_will",
                    "producer_preference_as_selection",
                    "random_tie_as_collapse",
                    "N22_susceptibility_as_choice",
                    "native_route_conductance_memory",
                    "ant_ecology_specification",
                ]
            ),
        },
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
    }
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> str:
    rows = payload["contract_inventory_rows"]
    n20 = payload["n20_closeout_boundary"]
    n22 = payload["n22_context_boundary"]
    ap = payload["n19_ap_gap_boundary"]
    lines: list[str] = [
        "# N23 Iteration 1 - Source Handoff Inventory",
        "",
        "## Summary",
        "",
        f"Status: `{payload['status']}`",
        "",
        f"Acceptance state: `{payload['acceptance_state']}`",
        "",
        f"Output digest: `{payload['output_digest']}`",
        "",
        "Iteration 1 is source/handoff inventory only. It records the N20",
        "`live_continuation_collapse` contract, N22 bounded producer-mediated",
        "susceptibility-update context, and N19 AP4/AP5 gap boundary. It does",
        "not assign LC rungs or open N23 live-continuation evidence.",
        "",
        "## Source Artifacts",
        "",
        "| Role | Path | Status | SHA-256 |",
        "| --- | --- | --- | --- |",
    ]
    for source in payload["source_artifacts"]:
        lines.append(
            f"| {source['source_role']} | `{source['path']}` | "
            f"`{source['status']}` | `{source['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## N20 Closeout Boundary",
            "",
            "```text",
            f"status = {n20['status']}",
            f"acceptance_state = {n20['acceptance_state']}",
            f"n20_contract_complete = {str(n20['n20_contract_complete']).lower()}",
            f"primitive_evidence_opened = {str(n20['primitive_evidence_opened']).lower()}",
            f"n23_consumption_role = {n20['n23_consumption_role']}",
            "```",
            "",
            "## Live-Continuation Contract Row",
            "",
            "| Primitive | Source row | Contract | Source fields | Controls | Evidence opened |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['primitive_id']}` | `{row['source_consumable_contract_row']}` "
            f"| `{row['source_contract_status']}` | "
            f"{len(row['source_current_fields'])} | "
            f"{len(row['minimum_controls']['control_ids'])} | "
            f"`{str(row['n23_primitive_evidence_opened']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## N22 Context Boundary",
            "",
            "```text",
            f"n22_source_closeout_status = {n22['n22_source_closeout_status']}",
            f"n22_source_closeout_acceptance_state = {n22['n22_source_closeout_acceptance_state']}",
            f"n22_closeout_ladder_rung = {n22['n22_closeout_ladder_rung']}",
            f"final_supported_su_ladder_rung = {n22['final_supported_su_ladder_rung']}",
            f"ready_for_n23 = {str(n22['ready_for_n23']).lower()}",
            "N22 may be consumed as producer-mediated susceptibility context only.",
            "N22 cannot satisfy live-continuation collapse, semantic choice, agency,",
            "native route memory, native support, sentience, Phase 8, or ant ecology.",
            "```",
            "",
            "## AP Gap Boundary",
            "",
            "```text",
            f"ap_levels_lacking_nat4_evidence = {ap['ap_levels_lacking_nat4_evidence']}",
            f"AP4 best NAT level = {ap['ap4']['best_nat_level']}",
            f"AP4 NAT4 evidence present = {str(ap['ap4']['nat4_evidence_present']).lower()}",
            f"AP5 best NAT level = {ap['ap5']['best_nat_level']}",
            f"AP5 NAT4 evidence present = {str(ap['ap5']['nat4_evidence_present']).lower()}",
            f"N23 AP4 bridge status = {ap['n23_ap4_bridge_status']}",
            "```",
            "",
            "## Required Future Candidate Fields",
            "",
            "```text",
            *payload["required_future_candidate_fields"],
            "```",
            "",
            "## Operational Freeze Targets For Iteration 2",
            "",
            "```text",
            "live branches must be same-run, same-window, pre-collapse records",
            "replay forks may audit counterfactuals but cannot create original live branches",
            "counterfactual retention means immutable pre-collapse audit evidence",
            "branch_record_origin must be source_current_same_run for LC2+",
            "selected branch reason must be source-current and pre/in-collapse",
            "candidate AP status enums must exclude inventory/meta values",
            "numeric support/coherence/boundary/flux/collapse thresholds must be frozen before I4",
            "N22 susceptibility may condition N23 geometry only when expressed in N23 source-current branch traces",
            "positive LC support cannot come from report/context/contract/closeout-only artifacts",
            "```",
            "",
            "## Evidence Boundary",
            "",
            "```text",
            "live_continuation_collapse_evidence_opened = false",
            "live_branch_set_supported = false",
            "collapse_supported = false",
            "counterfactual_retention_supported = false",
            "lc_ladder_rung_assigned = false",
            "n23_closeout_ladder_rung = N23-C0_inventory_only",
            "ap4_bridge_status = not_supported_inventory_only",
            "semantic_choice_supported = false",
            "agency_supported = false",
            "native_support_supported = false",
            "sentience_supported = false",
            "phase8_opened = false",
            "ant_ecology_implementation_opened = false",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in payload["checks"]:
        detail = json.dumps(check["detail"], sort_keys=True, ensure_ascii=True)
        lines.append(
            f"| `{check['check_id']}` | `{str(check['passed']).lower()}` | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Iteration 1 passes only as a source handoff inventory. The strongest",
            "recorded result is that N23 has a complete N20 contract row and a",
            "bounded N22 prerequisite context to consume. No live branch set,",
            "collapse, counterfactual-retention, AP4 bridge, semantic choice,",
            "agency, native support, sentience, Phase 8, or ant-ecology claim is",
            "opened.",
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
