#!/usr/bin/env python3
"""Build N22 Iteration 1 source handoff inventory."""

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
OUTPUT = EXPERIMENT / "outputs" / "n22_source_handoff_inventory.json"
REPORT = EXPERIMENT / "reports" / "n22_source_handoff_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_source_handoff_inventory.py"
)

N20_CLOSEOUT_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_closeout_and_n21_handoff.json"
)
N20_I5_CONTRACT_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)
N21_CLOSEOUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_closeout_and_n22_handoff.json"
)
N19_CLOSEOUT_PATH = (
    "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
    "outputs/n19_closeout_and_handoff.json"
)
N20_HANDOFF_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md"
N20_ROADMAP_PATH = "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md"

SUSCEPTIBILITY_ROW_ID = "n20_i5_row_03_susceptibility_update"
EXPECTED_SOURCE_CURRENT_FIELDS = [
    "susceptibility_update.pre_interaction_geometry_trace",
    "susceptibility_update.post_interaction_geometry_trace",
    "susceptibility_update.susceptibility_delta_trace",
    "susceptibility_update.route_or_region_reentry_trace",
]
EXPECTED_N22_INPUTS = [
    "susceptibility_fields",
    "replay_requirement",
    "durable_geometry_modification_controls",
    "AP4_gap_dependency_if_route_conditioned",
    "AP5_gap_dependency_if_proxy_conditioned",
]
EXPECTED_CONTROLS = {
    "label_only_success_control",
    "proxy_only_success_control",
    "hidden_producer_support_control",
    "post_hoc_trace_construction_control",
    "semantic_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control",
    "durable_geometry_modification_control",
    "route_label_only_control",
    "reinforcement_schedule_removed_control",
    "AP4_gap_dependency_if_route_conditioned",
    "AP5_gap_dependency_if_proxy_conditioned",
}
BLOCKED_CLAIMS = [
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
    else:
        record["parseable_json"] = False
        record["status"] = "markdown_context_only"
    return record


def all_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in BLOCKED_CLAIMS}


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


def find_contract_row(contract_data: dict[str, Any]) -> dict[str, Any]:
    for row in contract_data["contract_rows"]:
        if row["row_id"] == SUSCEPTIBILITY_ROW_ID:
            return row
    raise KeyError(f"Missing {SUSCEPTIBILITY_ROW_ID}")


def contract_row_digest(row_data: dict[str, Any]) -> str:
    return digest_value(row_data)


def susceptibility_inventory_row(row_data: dict[str, Any]) -> dict[str, Any]:
    same_basin_rule = row_data["same_basin_continuation_rule"]
    support_scaffold = row_data["support_scaffold_declaration"]
    proxy_metric = row_data["proxy_metric_definition"]
    continuation_function = row_data["continuation_function_descriptor"]
    minimum_controls = row_data["minimum_controls"]
    global_flags = unsafe_claim_flags()

    return {
        "row_id": "n22_i1_row_01_susceptibility_update_contract_input",
        "primitive_id": "susceptibility_update",
        "primitive_name": str(row_data["primitive_name"]),
        "source_contract_row": str(row_data["row_id"]),
        "source_i4_row_id": str(row_data["source_i4_row_id"]),
        "source_contract_row_digest": contract_row_digest(row_data),
        "source_artifact": N20_I5_CONTRACT_PATH,
        "source_contract_status": str(row_data["contract_status"]),
        "source_downstream_consumption_status": str(
            row_data["downstream_consumption_status"]
        ),
        "n20_source_downstream_consumption_status": str(
            row_data["downstream_consumption_status"]
        ),
        "contract_consumed_without_redefinition": True,
        "n22_inventory_role": "source_contract_input_only",
        "n22_primitive_evidence_opened": False,
        "n22_susceptibility_update_supported": False,
        "n22_ladder_rung_assigned": False,
        "su_ladder_rung": "not_assigned_contract_inventory_only",
        "allowed_next_assignment_source": "source_backed_N22_evidence_rows_only",
        "source_current_fields": list(row_data["LGRC_visible_fields"]),
        "producer_mediated_fields": list(row_data["producer_mediated_fields"]),
        "naturalization_debt_fields": list(row_data["naturalization_debt_fields"]),
        "blocked_relabel_fields": list(row_data["blocked_relabel_fields"]),
        "source_role_dependencies": row_data["source_role_dependencies"],
        "ap_gap_contract": row_data["ap_gap_contract"],
        "ap5_dependency_split": row_data["ap5_dependency_split"],
        "required_n22_inputs": list(row_data["primitive_specific_consumption_inputs"]),
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
            "expected_relation_to_continuation_function": proxy_metric[
                "expected_relation_to_continuation_function"
            ],
            "divergence_condition": proxy_metric["divergence_condition"],
            "collapse_condition": proxy_metric["collapse_condition"],
            "proxy_success_replaces_continuation": proxy_metric[
                "proxy_success_replaces_continuation"
            ],
            "proxy_only_success_blocker": proxy_metric[
                "proxy_only_success_blocker"
            ],
        },
        "required_control_ids": control_ids(minimum_controls),
        "controls_declared_fail_closed_in_contract": bool(
            minimum_controls["all_controls_fail_closed"]
        ),
        "control_execution_status": "not_run",
        "global_unsafe_claim_flags": global_flags,
        "source_unsafe_claim_flags": row_data["unsafe_claim_flags"],
        "unsafe_claim_flags": global_flags,
        "global_unsafe_claim_flags_all_false": all_false(global_flags),
        "source_unsafe_claim_flags_all_false": all_false(
            row_data["unsafe_claim_flags"]
        ),
        "blocked_claims_carried_forward": BLOCKED_CLAIMS,
        "claim_ceiling": (
            "source contract input only; no N22 susceptibility-update evidence, "
            "semantic learning, choice, agency, native support, Phase 8, "
            "sentience, or ant-ecology implementation"
        ),
        "inventory_decision": "supported_as_contract_input_only",
        "row_decision": "not_applicable",
    }


def nd6_bridge_contract(n21_closeout: dict[str, Any]) -> dict[str, Any]:
    combined = n21_closeout["combined_closeout"]
    nd = n21_closeout["naturalization_depth_closeout"]
    return {
        "n21_is_closed": True,
        "n21_ladder_rung": combined["n21_closeout_ladder_rung"],
        "n21_naturalization_depth_ladder_rung": nd[
            "naturalization_depth_ladder_rung"
        ],
        "n21_nd6_supported": False,
        "n21_source_mutation_supported": False,
        "n22_bridge_question": (
            "Does N22 produce source-backed durable susceptibility delta evidence "
            "that can serve as a bridge candidate for the missing N21 ND6 condition?"
        ),
        "n22_direct_nd6_claim_allowed": False,
        "bridge_status_initial": "not_supported",
        "allowed_bridge_status_values": [
            "not_supported",
            "bridge_candidate_supported",
            "blocked_by_replay",
            "blocked_by_controls",
            "blocked_by_AP_gap",
            "blocked_by_producer_residue",
        ],
        "bridge_candidate_requires": [
            "SU5_or_SU6_cleanly_supported",
            "source_backed_durable_susceptibility_delta",
            "replay_and_reentry_support",
            "peer_same_budget_comparison_when_route_or_region_conditioned",
            "AP4_AP5_dependency_controls_intact",
            "unsafe_claims_blocked",
        ],
    }


def evidence_boundary() -> dict[str, Any]:
    return {
        "iteration_1_role": "source_handoff_inventory_only",
        "source_current_definition": (
            "emitted by the LGRC runtime or replay from declared run artifacts, "
            "not invented by a report builder, label, post-hoc parser, "
            "producer-only policy, or semantic learning vocabulary"
        ),
        "positive_evidence_requires_future_run_artifacts": True,
        "required_future_candidate_fields": [
            "source_current_inputs",
            "row_specific_thresholds_declared_before_use",
            "pre_interaction_geometry_trace",
            "post_interaction_geometry_trace",
            "susceptibility_delta_trace",
            "route_or_region_reentry_trace",
            "allowed_delta_fields",
            "same_basin_invariant_fields",
            "peer_same_budget_comparison",
            "interaction_delta_digest",
            "post_replay_delta_digest",
            "reentry_delta_digest",
            "delta_persistence_ratio",
            "delta_threshold_or_rule",
            "one_window_transient_rejected",
        ],
        "derived_report_only_true_blocks_positive_support": True,
        "n20_contract_completeness_assigns_su_rungs": False,
        "n21_closeout_assigns_su_rungs": False,
        "su_rungs_require_source_backed_n22_evidence": True,
    }


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def build_checks(
    n20_closeout: dict[str, Any],
    n20_contract: dict[str, Any],
    n21_closeout: dict[str, Any],
    row: dict[str, Any],
    source_row: dict[str, Any],
) -> list[dict[str, Any]]:
    n22_handoff = n21_closeout["n22_handoff"]
    combined = n21_closeout["combined_closeout"]
    ap_gap = n22_handoff["ap_gap_contract"]
    source_artifact_invariants = source_row["artifact_invariants"]

    return [
        check(
            "n20_closeout_present_and_contract_only",
            n20_closeout.get("status") == "passed"
            and bool(n20_closeout.get("primitive_evidence_opened")) is False,
            {
                "status": n20_closeout.get("status"),
                "primitive_evidence_opened": n20_closeout.get(
                    "primitive_evidence_opened"
                ),
            },
        ),
        check(
            "n20_i5_contract_present_and_complete",
            n20_contract.get("status") == "passed"
            and n20_contract.get("acceptance_state")
            == "accepted_same_basin_control_contract_complete_no_primitive_evidence"
            and source_row.get("contract_status") == "complete",
            {
                "status": n20_contract.get("status"),
                "acceptance_state": n20_contract.get("acceptance_state"),
                "source_contract_status": source_row.get("contract_status"),
            },
        ),
        check(
            "susceptibility_source_row_present",
            row["source_contract_row"] == SUSCEPTIBILITY_ROW_ID
            and row["primitive_id"] == "susceptibility_update",
            {
                "source_contract_row": row["source_contract_row"],
                "primitive_id": row["primitive_id"],
            },
        ),
        check(
            "n21_closeout_ready_for_n22",
            n21_closeout.get("status") == "passed"
            and combined["ready_for_n22"] is True
            and combined["n21_closeout_ladder_rung"] == "N21-C6",
            {
                "status": n21_closeout.get("status"),
                "ready_for_n22": combined["ready_for_n22"],
                "n21_closeout_ladder_rung": combined["n21_closeout_ladder_rung"],
            },
        ),
        check(
            "n21_consumed_as_context_only",
            n22_handoff["n21_consumable_inputs"]["withdrawal_resistance_ladder_rung"]
            == "WR6"
            and n22_handoff["n21_consumable_inputs"][
                "naturalization_depth_ladder_rung"
            ]
            == "ND5"
            and row["n22_susceptibility_update_supported"] is False,
            n22_handoff["n21_consumable_inputs"],
        ),
        check(
            "source_current_fields_match_handoff",
            row["source_current_fields"] == EXPECTED_SOURCE_CURRENT_FIELDS
            == n22_handoff["source_current_fields"],
            {
                "row": row["source_current_fields"],
                "handoff": n22_handoff["source_current_fields"],
            },
        ),
        check(
            "required_n22_inputs_match_handoff",
            row["required_n22_inputs"] == EXPECTED_N22_INPUTS
            == n22_handoff["required_n22_inputs"],
            {
                "row": row["required_n22_inputs"],
                "handoff": n22_handoff["required_n22_inputs"],
            },
        ),
        check(
            "producer_and_debt_fields_recorded",
            row["producer_mediated_fields"]
            and row["naturalization_debt_fields"]
            and "susceptibility_update.peer_route_same_budget_comparison"
            in row["naturalization_debt_fields"],
            {
                "producer_mediated_fields": row["producer_mediated_fields"],
                "naturalization_debt_fields": row["naturalization_debt_fields"],
            },
        ),
        check(
            "ap_gap_contract_present",
            ap_gap["ap_gap_dependencies"][0]["ap_level"] == "AP4"
            and ap_gap["conditional_gap_dependencies"][0]["ap_level"] == "AP5"
            and row["ap5_dependency_split"]["status"]
            == "explicit_split_not_gap_removal",
            {
                "handoff_ap_gap": ap_gap,
                "source_ap5_split": row["ap5_dependency_split"],
            },
        ),
        check(
            "required_controls_recorded",
            EXPECTED_CONTROLS.issubset(set(row["required_control_ids"])),
            row["required_control_ids"],
        ),
        check(
            "same_basin_and_support_scaffold_recorded",
            bool(row["same_basin_rule"]["basin_signature_fields"])
            and bool(row["support_scaffold"]["required_supports"])
            and row["same_basin_rule"]["hidden_producer_support_allowed"] is False,
            {
                "same_basin_rule": row["same_basin_rule"]["rule_id"],
                "support_scaffold": row["support_scaffold"]["support_id"],
            },
        ),
        check(
            "primitive_evidence_not_opened",
            row["n22_primitive_evidence_opened"] is False
            and row["n22_susceptibility_update_supported"] is False
            and source_row["primitive_evidence_opened"] is False
            and source_artifact_invariants["primitive_evidence_opened"] is False,
            {
                "n22_row_primitive_evidence_opened": row[
                    "n22_primitive_evidence_opened"
                ],
                "n22_susceptibility_update_supported": row[
                    "n22_susceptibility_update_supported"
                ],
                "source_row_primitive_evidence_opened": source_row[
                    "primitive_evidence_opened"
                ],
            },
        ),
        check(
            "su_ladder_not_assigned",
            row["n22_ladder_rung_assigned"] is False
            and row["su_ladder_rung"] == "not_assigned_contract_inventory_only",
            {
                "n22_ladder_rung_assigned": row["n22_ladder_rung_assigned"],
                "su_ladder_rung": row["su_ladder_rung"],
            },
        ),
        check(
            "nd6_bridge_not_supported_in_inventory",
            row["inventory_decision"] == "supported_as_contract_input_only",
            "N22 I1 records the ND6 bridge question only; no bridge support is assigned.",
        ),
        check(
            "global_and_source_unsafe_claim_flags_false",
            row["global_unsafe_claim_flags_all_false"]
            and row["source_unsafe_claim_flags_all_false"],
            {
                "global_unsafe_claim_flags": row["global_unsafe_claim_flags"],
                "source_unsafe_claim_flags": row["source_unsafe_claim_flags"],
            },
        ),
        check(
            "claim_boundary_unopened",
            not n21_closeout["claim_boundary"]["agency_supported"]
            and not n21_closeout["claim_boundary"]["native_support_supported"]
            and not n21_closeout["claim_boundary"]["sentience_supported"]
            and not n21_closeout["claim_boundary"]["phase8_opened"]
            and not n21_closeout["claim_boundary"][
                "ant_ecology_implementation_opened"
            ],
            n21_closeout["claim_boundary"],
        ),
        check(
            "inventory_decision_uses_standard_row_decision",
            row["row_decision"] == "not_applicable"
            and row["inventory_decision"] == "supported_as_contract_input_only",
            {
                "row_decision": row["row_decision"],
                "inventory_decision": row["inventory_decision"],
            },
        ),
        check(
            "controls_declared_not_executed_in_inventory",
            row["controls_declared_fail_closed_in_contract"] is True
            and row["control_execution_status"] == "not_run",
            {
                "controls_declared_fail_closed_in_contract": row[
                    "controls_declared_fail_closed_in_contract"
                ],
                "control_execution_status": row["control_execution_status"],
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
    n20_closeout = load_json(N20_CLOSEOUT_PATH)
    n20_contract = load_json(N20_I5_CONTRACT_PATH)
    n21_closeout = load_json(N21_CLOSEOUT_PATH)
    n19_closeout = load_json(N19_CLOSEOUT_PATH)
    source_row = find_contract_row(n20_contract)
    row = susceptibility_inventory_row(source_row)
    source_artifacts = [
        source_record(N20_CLOSEOUT_PATH, "n20_closeout_and_n21_handoff"),
        source_record(N20_I5_CONTRACT_PATH, "n20_i5_same_basin_contract"),
        source_record(N21_CLOSEOUT_PATH, "n21_closeout_and_n22_handoff"),
        source_record(N19_CLOSEOUT_PATH, "n19_native_readiness_boundary"),
        source_record(N20_HANDOFF_PATH, "n20_n29_handoff"),
        source_record(N20_ROADMAP_PATH, "n20_n29_roadmap"),
    ]

    checks = build_checks(n20_closeout, n20_contract, n21_closeout, row, source_row)

    payload: dict[str, Any] = {
        "artifact_id": "n22_source_handoff_inventory",
        "schema_version": "n22_source_handoff_inventory_v1",
        "experiment": (
            "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
        ),
        "iteration": 1,
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_source_handoff_inventory_no_susceptibility_evidence",
        "purpose": (
            "Inventory N20 susceptibility_update contract, N21 closeout handoff, "
            "and AP4/AP5 dependency context without opening N22 primitive evidence."
        ),
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "source_context_boundary": {
            "markdown_sources_context_only": [
                N20_HANDOFF_PATH,
                N20_ROADMAP_PATH,
            ],
            "n21_closeout_may_consume_as": [
                "prerequisite_context",
                "WR6_ND5_N21-C6_readiness_boundary",
                "N22_handoff_contract",
            ],
            "n21_closeout_must_not_consume_as": [
                "susceptibility_update_evidence",
                "durable_geometry_delta",
                "SU_ladder_assignment_source",
                "semantic_learning_evidence",
                "native_support_evidence",
            ],
        },
        "source_closeout_summary": {
            "n20_status": n20_closeout["status"],
            "n20_acceptance_state": n20_closeout["acceptance_state"],
            "n20_output_digest": n20_closeout["output_digest"],
            "n19_claimed_ladder_generation_status": n19_closeout[
                "claimed_ladder_generation_status"
            ],
            "n21_status": n21_closeout["status"],
            "n21_acceptance_state": n21_closeout["acceptance_state"],
            "n21_output_digest": n21_closeout["output_digest"],
            "n21_closeout_ladder_rung": n21_closeout["combined_closeout"][
                "n21_closeout_ladder_rung"
            ],
            "ready_for_n22": n21_closeout["combined_closeout"]["ready_for_n22"],
            "n22_handoff_scope": n21_closeout["n22_handoff"]["handoff_scope"],
            "n22_handoff_blockers": n21_closeout["n22_handoff"][
                "handoff_blockers"
            ],
        },
        "source_contract_rows": [row],
        "n21_nd6_bridge_contract": nd6_bridge_contract(n21_closeout),
        "evidence_boundary": evidence_boundary(),
        "iteration1_boundary": {
            "susceptibility_evidence_opened": False,
            "susceptibility_update_supported": False,
            "durable_geometry_modification_supported": False,
            "su_ladder_rung_assigned": False,
            "n21_nd6_bridge_status": "not_supported",
            "n21_reopened": False,
            "positive_run_artifacts_consumed": False,
            "source_handoff_inventory_only": True,
            "ready_for_iteration_2_schema_freeze": True,
        },
        "blocked_claims": BLOCKED_CLAIMS,
        "checks": checks,
    }

    serialized_without_no_path_check = canonical_json(payload)
    no_absolute_paths = not contains_local_absolute_path(serialized_without_no_path_check)
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
        payload["acceptance_state"] = "blocked_source_handoff_inventory_checks_failed"

    digest_payload = dict(payload)
    digest_payload.pop("output_digest", None)
    payload["output_digest"] = digest_value(digest_payload)
    return payload


def write_report(data: dict[str, Any]) -> None:
    row = data["source_contract_rows"][0]
    lines: list[str] = [
        "# N22 Iteration 1 - Source Handoff Inventory",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "Iteration 1 is source/handoff inventory only. It records the N20",
        "`susceptibility_update` contract, N21 closeout context, and AP4/AP5",
        "dependency boundary. It does not assign SU rungs or open N22 evidence.",
        "",
        "## Source Artifacts",
        "",
        "| Role | Path | Status | SHA-256 |",
        "| --- | --- | --- | --- |",
    ]

    for source in data["source_artifacts"]:
        lines.append(
            "| {role} | `{path}` | `{status}` | `{sha}` |".format(
                role=source["source_role"],
                path=source["path"],
                status=source.get("status", "not_json"),
                sha=source["sha256"],
            )
        )

    lines.extend(
        [
            "",
            "## Susceptibility Contract Row",
            "",
            "| Primitive | Source row | Contract | Source fields | Controls | Evidence opened |",
            "| --- | --- | --- | ---: | ---: | --- |",
            "| `{primitive}` | `{source_row}` | `{status}` | {field_count} | {control_count} | `{opened}` |".format(
                primitive=row["primitive_id"],
                source_row=row["source_contract_row"],
                status=row["source_contract_status"],
                field_count=len(row["source_current_fields"]),
                control_count=len(row["required_control_ids"]),
                opened=str(row["n22_primitive_evidence_opened"]).lower(),
            ),
            "",
            "## N21 Context Boundary",
            "",
            "```text",
            f"n21_closeout_ladder_rung = {data['source_closeout_summary']['n21_closeout_ladder_rung']}",
            f"ready_for_n22 = {str(data['source_closeout_summary']['ready_for_n22']).lower()}",
            "N21 WR/ND evidence may be consumed as prerequisite context only.",
            "N21 WR/ND evidence cannot satisfy susceptibility_update.",
            "```",
            "",
            "## N21 ND6 Bridge Boundary",
            "",
            "```text",
            "n21_nd6_bridge_status = not_supported",
            "n22_direct_nd6_claim_allowed = false",
            "bridge_candidate_requires = SU5/SU6 cleanly supported with durable",
            "  source-current susceptibility delta, replay/re-entry support,",
            "  peer/same-budget comparison where applicable, and AP/claim controls",
            "```",
            "",
            "## Required Future Candidate Fields",
            "",
            "```text",
            "\n".join(data["evidence_boundary"]["required_future_candidate_fields"]),
            "```",
            "",
            "## AP Gap Boundary",
            "",
            "```json",
            json.dumps(row["ap_gap_contract"], indent=2, sort_keys=True),
            "```",
            "",
            "## Evidence Boundary",
            "",
            "```text",
            "susceptibility_evidence_opened = false",
            "susceptibility_update_supported = false",
            "durable_geometry_modification_supported = false",
            "su_ladder_rung_assigned = false",
            "positive_run_artifacts_consumed = false",
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
            "Iteration 1 passes only as a source handoff inventory. It confirms the",
            "N20 susceptibility-update contract is complete, N21 is ready for N22,",
            "and the AP4/AP5 dependency split is present. It does not support",
            "susceptibility update, durable geometry modification, semantic",
            "learning, choice, agency, native support, sentience, Phase 8, or",
            "ant-ecology implementation.",
            "",
        ]
    )

    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    data = build_payload()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")


if __name__ == "__main__":
    main()
