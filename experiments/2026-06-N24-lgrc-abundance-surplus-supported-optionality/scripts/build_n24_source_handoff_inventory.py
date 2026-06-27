#!/usr/bin/env python3
"""Build N24 Iteration 1 source handoff inventory."""

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
OUTPUT = EXPERIMENT / "outputs" / "n24_source_handoff_inventory.json"
REPORT = EXPERIMENT / "reports" / "n24_source_handoff_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_source_handoff_inventory.py"
)

N20_CLOSEOUT_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_closeout_and_n21_handoff.json"
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
N19_CLOSEOUT_PATH = (
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "outputs/n19_closeout_and_handoff.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"

SOURCE_CONTRACT_ROW = "n20_i4_row_05_surplus_supported_optionality"
CONSUMABLE_CONTRACT_ROW = "n20_i5_row_05_surplus_supported_optionality"
PRIMITIVE_ID = "surplus_supported_optionality"

EXPECTED_SOURCE_CURRENT_FIELDS = [
    "surplus_supported_optionality.support_surplus_margin_trace",
    "surplus_supported_optionality.optional_continuation_set_trace",
    "surplus_supported_optionality.maintenance_floor_trace",
    "surplus_supported_optionality.boundary_integrity_under_optionality_trace",
]
EXPECTED_CONSUMPTION_INPUTS = [
    "surplus_support_condition",
    "optional_continuation_space",
    "floor_crossing_controls",
    "hidden_budget_relief_control",
]
EXPECTED_CONTROLS = {
    "label_only_success_control",
    "proxy_only_success_control",
    "hidden_producer_support_control",
    "post_hoc_trace_construction_control",
    "semantic_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control",
    "floor_crossing_control",
    "hidden_budget_relief_control",
    "optional_branch_label_only_control",
}
PLANNED_N24_CANONICAL_CONTROL_IDS = [
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
REQUIRED_FUTURE_CANDIDATE_FIELDS = [
    "source_current_inputs",
    "row_specific_thresholds_declared_before_use",
    "maintenance_floor_policy",
    "support_floor_value",
    "coherence_floor_value",
    "boundary_integrity_floor_value",
    "flux_or_leakage_bound",
    "optionality_window",
    "support_surplus_margin_trace",
    "coherence_surplus_margin_trace",
    "residual_support_margin_under_optionality",
    "residual_coherence_margin_under_optionality",
    "optional_flux_drain_margin",
    "maintenance_floor_trace",
    "optional_continuation_set_trace",
    "optional_continuation_availability_count",
    "jointly_admissible_optional_continuation_count",
    "optional_branch_records",
    "boundary_integrity_under_optionality_trace",
    "optional_flux_does_not_drain_maintenance_support",
    "surplus_budget_owner",
    "hidden_budget_relief_absent",
    "same_basin_continuation_rule",
    "artifact_manifest",
    "artifact_sha256",
    "all_artifact_sha256_match_file_contents",
]
SURPLUS_FORMULAS_TO_FREEZE = {
    "support_surplus_margin": "observed_support - support_floor_value",
    "coherence_surplus_margin": "observed_coherence - coherence_floor_value",
    "residual_support_margin_under_optionality": (
        "min_support_during_optionality_window - support_floor_value"
    ),
    "residual_coherence_margin_under_optionality": (
        "min_coherence_during_optionality_window - coherence_floor_value"
    ),
    "optional_flux_drain_margin": (
        "flux_or_leakage_bound - observed_optional_flux_drain"
    ),
}
SURPLUS_BUDGET_OWNER_ENUM = [
    "source_current_geometry",
    "declared_producer_surface",
    "mixed_declared",
    "hidden_budget_relief_blocks_row",
    "not_recorded_blocks_row",
]
AP4_CONTEXT_STATUS_ENUM = [
    "n23_bridge_candidate_consumed",
    "lower_n23_context_consumed",
    "not_applicable",
    "missing_blocks_row",
]
AP_DEPENDENCY_STATUS_ENUM = [
    "required_recorded",
    "conditional_required_recorded",
    "not_applicable",
    "missing_blocks_row",
]
BLOCKED_CLAIMS = [
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
    else:
        record["parseable_json"] = False
        record["status"] = "markdown_context_only"
    return record


def find_contract_row(contract_data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in contract_data.get("contract_rows", []):
        if isinstance(row, dict) and row.get("row_id") == row_id:
            return row
    raise KeyError(f"Missing contract row: {row_id}")


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


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in BLOCKED_CLAIMS}


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
        "n24_consumption_role": "standing_primitive_contract_context_only",
    }


def n23_context_boundary(n23: dict[str, Any]) -> dict[str, Any]:
    final = n23["final_classification"]
    handoff = n23["n24_handoff"]
    lc_rung = str(final.get("final_supported_lc_ladder_rung", "not_recorded"))
    closeout_rung = str(final.get("final_n23_closeout_ladder_rung", "not_recorded"))
    ap4_bridge_status = str(final.get("ap4_bridge_status", "not_recorded"))
    closeout_valid = (
        n23.get("status") == "passed"
        and n23.get("acceptance_state")
        == "accepted_n23_lc6_closeout_n24_handoff_ready"
        and lc_rung == "LC6"
        and closeout_rung == "N23-C6"
        and ap4_bridge_status == "bridge_candidate_supported"
        and final.get("final_ap4_supported") is False
        and handoff.get("ready_for_n24") is True
    )
    closeout_present_but_lower = (
        n23.get("status") == "passed"
        and handoff.get("ready_for_n24") is True
        and not closeout_valid
        and lc_rung not in {"not_recorded", "None"}
        and closeout_rung not in {"not_recorded", "None"}
    )
    if closeout_valid:
        context_consumption = "n23_bridge_candidate_consumed"
        consumable_ap4_status = ap4_bridge_status
        n24_claim_ceiling = (
            "source inventory only; bounded N23 bridge context available"
        )
    elif closeout_present_but_lower:
        context_consumption = "bounded_lower_rung_context_only"
        consumable_ap4_status = "not_consumable_as_bridge_candidate"
        n24_claim_ceiling = "contract_only_or_downgraded_context"
    else:
        context_consumption = "not_available"
        consumable_ap4_status = "not_consumable_as_bridge_candidate"
        n24_claim_ceiling = "contract_only_or_downgraded_context"
    return {
        "source_artifact": N23_CLOSEOUT_PATH,
        "n23_closeout_required": True,
        "n23_closeout_artifact_present": (ROOT / N23_CLOSEOUT_PATH).exists(),
        "n23_closeout_validated": closeout_valid,
        "n23_context_consumption": context_consumption,
        "n23_source_closeout_status": str(n23["status"]),
        "n23_source_closeout_acceptance_state": str(n23["acceptance_state"]),
        "final_supported_lc_ladder_rung": lc_rung,
        "final_n23_closeout_ladder_rung": closeout_rung,
        "n23_ap4_bridge_status": consumable_ap4_status,
        "n23_source_ap4_bridge_status": ap4_bridge_status,
        "final_global_ap4_reclassification_supported": bool(
            final.get("final_ap4_supported", False)
        ),
        "n24_claim_ceiling": n24_claim_ceiling,
        "ready_for_n24": bool(handoff.get("ready_for_n24")),
        "n24_may_consume_as": list(handoff.get("n24_may_consume_as", [])),
        "n24_must_not_consume_as": list(handoff.get("n24_must_not_consume_as", [])),
        "claim_ceiling": str(final.get("final_claim_ceiling", "not_recorded")),
        "consumption_boundary": (
            "bounded LC6/N23-C6 selection-geometry context only; not N24 "
            "surplus, optionality, reward, choice, agency, native support, "
            "sentience, Phase 8, or ant ecology evidence"
        ),
    }


def contract_inventory_row(
    native_row: dict[str, Any],
    same_basin_row: dict[str, Any],
) -> dict[str, Any]:
    controls = same_basin_row["minimum_controls"]
    same_basin_rule = same_basin_row["same_basin_continuation_rule"]
    return {
        "row_id": "n24_i1_row_01_surplus_supported_optionality_contract_input",
        "primitive_id": PRIMITIVE_ID,
        "source_contract_row": SOURCE_CONTRACT_ROW,
        "source_consumable_contract_row": CONSUMABLE_CONTRACT_ROW,
        "source_i4_contract_status": str(native_row["contract_status"]),
        "source_i4_row_decision": str(native_row["row_decision"]),
        "source_i5_contract_status": str(same_basin_row["contract_status"]),
        "n20_source_downstream_consumption_status": str(
            same_basin_row["downstream_consumption_status"]
        ),
        "inventory_decision": "supported_as_contract_input_only",
        "row_decision": "not_applicable",
        "ab_ladder_rung": "not_assigned_contract_inventory_only",
        "n24_closeout_ladder_rung": "N24-C0_inventory_only",
        "primitive_evidence_opened": False,
        "source_current_fields": list(same_basin_row["LGRC_visible_fields"]),
        "primitive_specific_consumption_inputs": list(
            same_basin_row["primitive_specific_consumption_inputs"]
        ),
        "same_basin_rule_id": str(same_basin_rule["rule_id"]),
        "same_basin_rule": same_basin_rule,
        "minimum_control_ids": control_ids(controls),
        "all_controls_fail_closed_in_contract": bool(
            controls["all_controls_fail_closed"]
        ),
        "control_execution_status": "not_run_inventory_only",
        "producer_mediated_fields": list(same_basin_row["producer_mediated_fields"]),
        "naturalization_debt_fields": list(
            same_basin_row["naturalization_debt_fields"]
        ),
        "blocked_relabel_fields": list(same_basin_row["blocked_relabel_fields"]),
        "unsafe_claim_flags": dict(same_basin_row["unsafe_claim_flags"]),
        "claim_ceiling": (
            "source contract input only; no N24 abundance, optionality, reward, "
            "choice, agency, native support, sentience, Phase 8, or ant ecology"
        ),
    }


def ap_gap_boundary(n19: dict[str, Any], n23: dict[str, Any]) -> dict[str, Any]:
    final = n23["final_classification"]
    return {
        "n19_source_artifact": N19_CLOSEOUT_PATH,
        "n19_status": str(n19["status"]),
        "ap_levels_lacking_nat4_evidence": list(
            n19["ap_levels_lacking_nat4_evidence"]
        ),
        "current_implementation_can_generate_claimed_ap_ladder": bool(
            n19["current_implementation_can_generate_claimed_ap_ladder"]
        ),
        "claimed_ladder_generation_status": str(
            n19["claimed_ladder_generation_status"]
        ),
        "n23_ap4_bridge_status": str(final["ap4_bridge_status"]),
        "n23_ap4_bridge_candidate_supported": bool(
            final["ap4_bridge_candidate_supported"]
        ),
        "final_global_ap4_reclassification_supported": bool(
            final["final_ap4_supported"]
        ),
        "ap4_context_status": "n23_bridge_candidate_consumed",
        "ap5_dependency_status": "conditional_required_when_proxy_reward_target_participates",
        "n24_boundary": (
            "consume N23 AP4 bridge as local context only; keep final global "
            "AP4 reclassification false and carry AP5 dependency when proxy, "
            "reward, or target formation participates"
        ),
    }


def build_output() -> dict[str, Any]:
    n20_closeout = load_json(N20_CLOSEOUT_PATH)
    native_contract = load_json(N20_NATIVE_FUNCTION_PATH)
    same_basin_contract = load_json(N20_SAME_BASIN_PATH)
    n23_closeout = load_json(N23_CLOSEOUT_PATH)
    n19_closeout = load_json(N19_CLOSEOUT_PATH)
    native_row = find_contract_row(native_contract, SOURCE_CONTRACT_ROW)
    same_basin_row = find_contract_row(same_basin_contract, CONSUMABLE_CONTRACT_ROW)

    source_artifacts = [
        source_record(N20_CLOSEOUT_PATH, "n20_closeout_and_handoff_context"),
        source_record(N20_NATIVE_FUNCTION_PATH, "n20_i4_native_function_proxy_contract"),
        source_record(N20_SAME_BASIN_PATH, "n20_i5_same_basin_contract"),
        source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        source_record(N19_CLOSEOUT_PATH, "n19_native_readiness_boundary"),
        source_record(N20_HANDOFF_PATH, "n20_n29_handoff"),
        source_record(N20_ROADMAP_PATH, "n20_n29_roadmap"),
    ]

    contract_row = contract_inventory_row(native_row, same_basin_row)
    n23_boundary = n23_context_boundary(n23_closeout)
    ap_boundary = ap_gap_boundary(n19_closeout, n23_closeout)
    claim_boundary = {
        "abundance_evidence_opened": False,
        "surplus_supported_optionality_supported": False,
        "ab_ladder_rung_assigned": False,
        "n24_closeout_ladder_rung": "N24-C0_inventory_only",
        "semantic_choice_supported": False,
        "reward_maximization_supported": False,
        "agency_supported": False,
        "native_support_supported": False,
        "sentience_supported": False,
        "phase8_opened": False,
        "ant_ecology_implementation_opened": False,
        "unsafe_claim_flags": unsafe_claim_flags(),
    }
    operational_i2_freeze_targets = {
        "surplus_formulas_to_freeze": SURPLUS_FORMULAS_TO_FREEZE,
        "surplus_budget_owner_enum": SURPLUS_BUDGET_OWNER_ENUM,
        "ap4_context_status_enum": AP4_CONTEXT_STATUS_ENUM,
        "ap_dependency_status_enum": AP_DEPENDENCY_STATUS_ENUM,
        "planned_canonical_controls": PLANNED_N24_CANONICAL_CONTROL_IDS,
        "optionality_acceptance_targets": [
            "original optional continuation set must be same-source-current-run",
            "declared replay family may validate but not create AB3 optional set",
            "AB3 requires optional_continuation_availability_count >= 2",
            "AB5 requires jointly_admissible_optional_continuation_count >= 2",
            "optional_branch_record schema must be frozen",
            "hidden budget relief blocks positive support",
            "maintenance basin shift and floor renormalization fail closed",
        ],
    }

    checks = [
        {
            "check": "n20_i5_surplus_contract_present_and_complete",
            "passed": same_basin_row["contract_status"] == "complete",
            "detail": {
                "row_id": same_basin_row["row_id"],
                "source_i4_row_id": same_basin_row["source_i4_row_id"],
                "contract_status": same_basin_row["contract_status"],
                "downstream_consumption_status": same_basin_row[
                    "downstream_consumption_status"
                ],
            },
        },
        {
            "check": "n20_i4_surplus_descriptor_present",
            "passed": (
                native_row["row_id"] == SOURCE_CONTRACT_ROW
                and native_row["primitive_id"] == PRIMITIVE_ID
            ),
            "detail": {
                "row_id": native_row["row_id"],
                "contract_status": native_row["contract_status"],
                "row_decision": native_row["row_decision"],
            },
        },
        {
            "check": "n20_closeout_boundary_parsed",
            "passed": (
                n20_closeout["status"] == "passed"
                and n20_closeout["n20_contract_complete"] is True
                and n20_closeout["primitive_evidence_opened"] is False
            ),
            "detail": n20_closeout_boundary(n20_closeout),
        },
        {
            "check": "source_current_fields_match_contract",
            "passed": (
                same_basin_row["LGRC_visible_fields"] == EXPECTED_SOURCE_CURRENT_FIELDS
                and native_row["LGRC_visible_fields"] == EXPECTED_SOURCE_CURRENT_FIELDS
            ),
            "detail": {
                "expected": EXPECTED_SOURCE_CURRENT_FIELDS,
                "native_function_contract": native_row["LGRC_visible_fields"],
                "same_basin_contract": same_basin_row["LGRC_visible_fields"],
            },
        },
        {
            "check": "required_n24_inputs_match_handoff",
            "passed": (
                same_basin_row["primitive_specific_consumption_inputs"]
                == EXPECTED_CONSUMPTION_INPUTS
            ),
            "detail": {
                "expected": EXPECTED_CONSUMPTION_INPUTS,
                "contract": same_basin_row["primitive_specific_consumption_inputs"],
            },
        },
        {
            "check": "n23_closeout_required_and_validated",
            "passed": n23_boundary["n23_closeout_validated"] is True,
            "detail": n23_boundary,
        },
        {
            "check": "ap_gap_boundary_preserved",
            "passed": (
                "AP4" in ap_boundary["ap_levels_lacking_nat4_evidence"]
                and "AP5" in ap_boundary["ap_levels_lacking_nat4_evidence"]
                and ap_boundary["n23_ap4_bridge_status"]
                == "bridge_candidate_supported"
                and ap_boundary["final_global_ap4_reclassification_supported"]
                is False
            ),
            "detail": ap_boundary,
        },
        {
            "check": "required_controls_recorded",
            "passed": EXPECTED_CONTROLS.issubset(set(contract_row["minimum_control_ids"])),
            "detail": contract_row["minimum_control_ids"],
        },
        {
            "check": "planned_canonical_controls_ready_for_i2_i3",
            "passed": len(PLANNED_N24_CANONICAL_CONTROL_IDS) == 19,
            "detail": PLANNED_N24_CANONICAL_CONTROL_IDS,
        },
        {
            "check": "producer_and_debt_fields_recorded",
            "passed": bool(contract_row["producer_mediated_fields"])
            and bool(contract_row["naturalization_debt_fields"])
            and bool(contract_row["blocked_relabel_fields"]),
            "detail": {
                "producer_mediated_fields": contract_row["producer_mediated_fields"],
                "naturalization_debt_fields": contract_row["naturalization_debt_fields"],
                "blocked_relabel_fields": contract_row["blocked_relabel_fields"],
            },
        },
        {
            "check": "no_surplus_optionality_evidence_opened",
            "passed": claim_boundary["abundance_evidence_opened"] is False
            and claim_boundary["surplus_supported_optionality_supported"] is False
            and claim_boundary["ab_ladder_rung_assigned"] is False,
            "detail": claim_boundary,
        },
        {
            "check": "unsafe_claim_flags_false",
            "passed": all_false(contract_row["unsafe_claim_flags"])
            and all_false(n23_closeout["unsafe_claim_flags"])
            and all_false(claim_boundary["unsafe_claim_flags"]),
            "detail": {
                "n20_source_unsafe_claim_flags": contract_row["unsafe_claim_flags"],
                "n23_unsafe_claim_flags": n23_closeout["unsafe_claim_flags"],
                "n24_unsafe_claim_flags": claim_boundary["unsafe_claim_flags"],
            },
        },
        {
            "check": "inventory_decision_uses_standard_row_decision",
            "passed": contract_row["row_decision"] == "not_applicable",
            "detail": {
                "inventory_decision": contract_row["inventory_decision"],
                "row_decision": contract_row["row_decision"],
            },
        },
        {
            "check": "controls_declared_not_executed_in_inventory",
            "passed": contract_row["control_execution_status"] == "not_run_inventory_only",
            "detail": {
                "control_execution_status": contract_row["control_execution_status"],
                "all_controls_fail_closed_in_contract": contract_row[
                    "all_controls_fail_closed_in_contract"
                ],
            },
        },
    ]

    output: dict[str, Any] = {
        "artifact_id": "n24_i1_source_handoff_inventory",
        "schema_version": "n24_source_handoff_inventory_v1",
        "experiment": "N24",
        "iteration": 1,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "source handoff inventory only; no N24 primitive evidence",
        "status": "passed",
        "acceptance_state": (
            "accepted_source_handoff_inventory_no_surplus_optionality_evidence"
        ),
        "source_artifacts": source_artifacts,
        "source_artifact_statuses_purpose": (
            "validate N20 contract rows, conditional N23 closeout consumption, "
            "and AP gap boundary before N24 evidence opens"
        ),
        "n20_closeout_boundary": n20_closeout_boundary(n20_closeout),
        "contract_inventory_rows": [contract_row],
        "n23_context_boundary": n23_boundary,
        "n19_ap_gap_boundary": ap_boundary,
        "required_future_candidate_fields": REQUIRED_FUTURE_CANDIDATE_FIELDS,
        "operational_i2_freeze_targets": operational_i2_freeze_targets,
        "claim_boundary": claim_boundary,
        "evidence_boundary": {
            "surplus_supported_optionality_evidence_opened": False,
            "surplus_margin_supported": False,
            "optional_continuation_set_supported": False,
            "ab_ladder_rung_assigned": False,
            "n24_closeout_ladder_rung": "N24-C0_inventory_only",
            "ready_for_iteration_2_schema_freeze": True,
        },
        "checks": checks,
        "failed_checks": [
            check["check"] for check in checks if check["passed"] is not True
        ],
    }
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
        output["acceptance_state"] = "blocked_source_handoff_inventory"
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    source_lines = [
        "| Role | Path | Status | SHA-256 |",
        "| --- | --- | --- | --- |",
    ]
    for source in output["source_artifacts"]:
        source_lines.append(
            "| {role} | `{path}` | `{status}` | `{sha}` |".format(
                role=source["source_role"],
                path=source["path"],
                status=source["status"],
                sha=source["sha256"],
            )
        )

    contract = output["contract_inventory_rows"][0]
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

    report = "\n".join(
        [
            "# N24 Iteration 1 - Source Handoff Inventory",
            "",
            "## Summary",
            "",
            f"Status: `{output['status']}`",
            "",
            f"Acceptance state: `{output['acceptance_state']}`",
            "",
            f"Output digest: `{output['output_digest']}`",
            "",
            "Iteration 1 is source/handoff inventory only. It records the N20",
            "`surplus_supported_optionality` contract, validates N23 closeout",
            "as conditional bounded LC6/N23-C6 context, and preserves the AP",
            "gap boundary. It does not assign AB rungs or open N24 abundance",
            "evidence.",
            "",
            "## Source Artifacts",
            "",
            *source_lines,
            "",
            "## N20 Closeout Boundary",
            "",
            "```text",
            f"status = {output['n20_closeout_boundary']['status']}",
            "acceptance_state = "
            f"{output['n20_closeout_boundary']['acceptance_state']}",
            "n20_contract_complete = "
            f"{str(output['n20_closeout_boundary']['n20_contract_complete']).lower()}",
            "primitive_evidence_opened = "
            f"{str(output['n20_closeout_boundary']['primitive_evidence_opened']).lower()}",
            "n24_consumption_role = "
            f"{output['n20_closeout_boundary']['n24_consumption_role']}",
            "```",
            "",
            "## Surplus Optionality Contract Row",
            "",
            "| Primitive | Source row | Consumable row | Contract | Source fields | Controls | Evidence opened |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
            "| `{primitive}` | `{source}` | `{consumable}` | `{contract}` | {fields} | {controls} | `{opened}` |".format(
                primitive=contract["primitive_id"],
                source=contract["source_contract_row"],
                consumable=contract["source_consumable_contract_row"],
                contract=contract["source_i5_contract_status"],
                fields=len(contract["source_current_fields"]),
                controls=len(contract["minimum_control_ids"]),
                opened=str(contract["primitive_evidence_opened"]).lower(),
            ),
            "",
            "## N23 Context Boundary",
            "",
            "```text",
            "n23_closeout_required = true",
            "n23_closeout_validated = "
            f"{str(output['n23_context_boundary']['n23_closeout_validated']).lower()}",
            "n23_context_consumption = "
            f"{output['n23_context_boundary']['n23_context_consumption']}",
            "final_supported_lc_ladder_rung = "
            f"{output['n23_context_boundary']['final_supported_lc_ladder_rung']}",
            "final_n23_closeout_ladder_rung = "
            f"{output['n23_context_boundary']['final_n23_closeout_ladder_rung']}",
            "n23_ap4_bridge_status = "
            f"{output['n23_context_boundary']['n23_ap4_bridge_status']}",
            "final_global_ap4_reclassification_supported = "
            f"{str(output['n23_context_boundary']['final_global_ap4_reclassification_supported']).lower()}",
            "ready_for_n24 = "
            f"{str(output['n23_context_boundary']['ready_for_n24']).lower()}",
            "N23 may be consumed as bounded selection-geometry context only.",
            "N23 cannot satisfy N24 surplus optionality, reward, choice,",
            "agency, native support, sentience, Phase 8, or ant ecology.",
            "```",
            "",
            "## AP Gap Boundary",
            "",
            "```text",
            "ap_levels_lacking_nat4_evidence = "
            f"{output['n19_ap_gap_boundary']['ap_levels_lacking_nat4_evidence']}",
            "n23_ap4_bridge_status = "
            f"{output['n19_ap_gap_boundary']['n23_ap4_bridge_status']}",
            "ap4_context_status = "
            f"{output['n19_ap_gap_boundary']['ap4_context_status']}",
            "final_global_ap4_reclassification_supported = false",
            "ap5_dependency_status = "
            f"{output['n19_ap_gap_boundary']['ap5_dependency_status']}",
            "```",
            "",
            "## Required Future Candidate Fields",
            "",
            "```text",
            *output["required_future_candidate_fields"],
            "```",
            "",
            "## Operational Freeze Targets For Iteration 2",
            "",
            "```text",
            "original optional continuation set must be same-source-current-run",
            "declared replay family may validate but not create AB3 optional set",
            "AB3 requires optional_continuation_availability_count >= 2",
            "AB5 requires jointly_admissible_optional_continuation_count >= 2",
            "surplus formulas must be frozen before probes",
            "surplus budget owner enum and rung ceilings must be frozen",
            "hidden budget relief, floor crossing, proxy-only gain, label-only",
            "optionality, independent-run assembly, maintenance basin shift,",
            "and floor renormalization controls must fail closed",
            "```",
            "",
            "## Evidence Boundary",
            "",
            "```text",
            "surplus_supported_optionality_evidence_opened = false",
            "surplus_margin_supported = false",
            "optional_continuation_set_supported = false",
            "ab_ladder_rung_assigned = false",
            "n24_closeout_ladder_rung = N24-C0_inventory_only",
            "semantic_choice_supported = false",
            "reward_maximization_supported = false",
            "agency_supported = false",
            "native_support_supported = false",
            "sentience_supported = false",
            "phase8_opened = false",
            "ant_ecology_implementation_opened = false",
            "```",
            "",
            "## Checks",
            "",
            *checks_lines,
            "",
            "## Interpretation",
            "",
            "Iteration 1 passes only as a source handoff inventory. The strongest",
            "recorded result is that N24 has a complete N20 surplus optionality",
            "contract and a validated N23 closeout context to consume. No",
            "surplus margin, optional continuation set, AB rung, reward",
            "maximization, semantic choice, agency, native support, sentience,",
            "Phase 8, or ant-ecology claim is opened.",
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
