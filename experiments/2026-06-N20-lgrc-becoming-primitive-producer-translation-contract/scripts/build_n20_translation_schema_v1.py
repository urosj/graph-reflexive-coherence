#!/usr/bin/env python3
"""Build N20 Iteration 2 translation schema and control freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-22T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract"
)
INVENTORY = EXPERIMENT / "outputs" / "n20_source_method_inventory.json"
OUTPUT = EXPERIMENT / "outputs" / "n20_translation_schema_v1.json"
REPORT = EXPERIMENT / "reports" / "n20_translation_schema_v1.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "scripts/build_n20_translation_schema_v1.py"
)

INVARIANTS = {
    "primitive_evidence_opened": False,
    "agency_claim_opened": False,
    "phase8_opened": False,
    "native_support_opened": False,
    "sentience_opened": False,
    "ant_ecology_spec_opened": False,
    "src_diff_empty_required": True,
}

SOURCE_ROLES = [
    "method_source",
    "diagnostic_vocabulary_source",
    "boundary_source",
    "implementation_boundary_source",
    "roadmap_source",
    "future_application_context",
]

SOURCE_ROLE_EVIDENCE_GATES = {
    "method_source": {
        "may_define": ["method_step", "probe_design_rule", "control_design_rule"],
        "may_not_satisfy": [
            "primitive_evidence_gate",
            "native_support_gate",
            "agency_claim_gate",
        ],
    },
    "diagnostic_vocabulary_source": {
        "may_define": ["field_names", "diagnostic_terms", "control_targets"],
        "may_not_satisfy": [
            "primitive_evidence_gate",
            "implementation_gate",
            "native_support_gate",
            "agency_claim_gate",
        ],
    },
    "boundary_source": {
        "may_define": ["claim_boundary", "blocked_claim", "historical_context"],
        "may_not_satisfy": ["primitive_evidence_gate", "agency_claim_gate"],
    },
    "implementation_boundary_source": {
        "may_define": [
            "current_classification_boundary",
            "implementation_gap",
            "gap_propagation_rule",
        ],
        "may_not_satisfy": [
            "primitive_evidence_gate",
            "Phase_8_implementation_gate",
            "native_support_gate",
        ],
    },
    "roadmap_source": {
        "may_define": ["experiment_order", "claim_boundary", "handoff_target"],
        "may_not_satisfy": ["primitive_evidence_gate", "implementation_gate"],
    },
    "future_application_context": {
        "may_define": ["future_context", "deferred_medium_debt_placeholder"],
        "may_not_satisfy": [
            "primitive_evidence_gate",
            "implementation_gate",
            "ant_ecology_spec_gate_before_N29",
        ],
    },
}

VARIABLE_CLASSIFICATION_ENUM = [
    "substrate_carried",
    "producer_mediated",
    "naturalization_debt",
    "blocked_relabel",
]

VARIABLE_CLASSIFICATION_DEFINITIONS = {
    "substrate_carried": (
        "quantity is carried by source-current LGRC geometry or committed source "
        "artifacts under replay"
    ),
    "producer_mediated": (
        "quantity is introduced, routed, preserved, scheduled, or labeled by an "
        "explicit producer surface"
    ),
    "naturalization_debt": (
        "quantity is necessary for the proposed primitive but is not yet "
        "source-current or replay-carried in the required way"
    ),
    "blocked_relabel": (
        "quantity would only pass by semantic, post-hoc, or claim-inflating relabel"
    ),
}

NATURALIZATION_DEBT_TYPE_ENUM = [
    "telemetry_debt",
    "policy_debt",
    "state_mutation_debt",
    "replay_debt",
    "budget_debt",
    "source_currentness_debt",
    "claim_boundary_debt",
]

CONTRACT_STATUS_ENUM = [
    "complete",
    "incomplete_missing_producer_residue_classification",
    "incomplete_missing_continuation_function",
    "incomplete_missing_proxy_metric",
    "incomplete_missing_support_scaffold_declaration",
    "incomplete_missing_same_basin_rule",
    "incomplete_missing_controls",
    "incomplete_missing_claim_ceiling",
    "incomplete_missing_unsafe_claim_flags",
    "incomplete_missing_variable_classification",
    "incomplete_missing_debt_subtype",
    "blocked_by_relabel",
]

ROW_DECISION_ENUM = [
    "supported",
    "partial",
    "blocked",
    "rejected",
    "not_applicable",
]

UNSAFE_CLAIM_FLAGS = [
    "agency",
    "semantic_intention",
    "semantic_choice",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]

EXPECTED_PRIMITIVE_IDS = [
    "withdrawal_resistance",
    "naturalization_depth",
    "susceptibility_update",
    "live_continuation_collapse",
    "surplus_supported_optionality",
    "spark_sub_basin_new_basin_formation",
    "proxy_divergence_proxy_collapse",
    "configuration_substrate_transfer",
    "generative_extractive_persistence",
]

PRIMITIVE_ROW_REQUIRED_FIELDS = [
    "primitive_id",
    "primitive_name",
    "roadmap_target",
    "diagnostic_source_titles",
    "source_inventory_row_ids",
    "source_role_dependencies",
    "LGRC_visible_fields",
    "producer_mediated_fields",
    "naturalization_debt_fields",
    "blocked_relabel_fields",
    "variable_classification_records",
    "continuation_function_descriptor",
    "native_function_descriptor_alias",
    "proxy_metric_definition",
    "support_scaffold_declaration",
    "same_basin_continuation_rule",
    "contract_status",
    "row_decision",
    "minimum_controls",
    "ap_gap_dependencies",
    "conditional_gap_dependencies",
    "expected_first_positive_experiment",
    "claim_ceiling",
    "unsafe_claim_flags",
    "artifact_invariants",
    "source_consumption_rules",
]

PRODUCER_REQUIRED_FIELDS = [
    "producer_surface_name",
    "introduced_quantity",
    "update_rule_owner",
    "source_current_visibility",
    "replay_visibility",
    "budget_surface",
    "claim_boundary",
    "naturalization_debt",
    "negative_controls",
]

CONTINUATION_FUNCTION_DESCRIPTOR_FIELDS = [
    "descriptor_id",
    "basin_signature",
    "support_floor",
    "coherence_floor",
    "boundary_condition",
    "flux_condition",
    "continuation_condition",
    "withdrawal_condition",
    "transfer_condition",
    "proxy_metric",
    "proxy_divergence_blocker",
    "claim_ceiling",
]

PROXY_METRIC_FIELDS = [
    "proxy_id",
    "measured_quantity",
    "source_current_inputs",
    "producer_inputs",
    "expected_relation_to_continuation_function",
    "divergence_condition",
    "collapse_condition",
    "proxy_only_success_blocker",
]

SUPPORT_SCAFFOLD_FIELDS = [
    "support_id",
    "support_source",
    "support_surface",
    "withdrawal_condition",
    "producer_role",
    "naturalization_debt",
    "hidden_support_control",
]

SAME_BASIN_FIELDS = [
    "basin_signature_fields",
    "allowed_drift",
    "required_support_floor",
    "required_coherence_floor",
    "boundary_integrity_floor",
    "flux_balance_bounds",
    "replay_requirement",
    "failure_modes",
    "blocked_relabels",
]

MINIMUM_CONTROLS = [
    "label_only_success_control",
    "proxy_only_success_control",
    "hidden_producer_support_control",
    "post_hoc_trace_construction_control",
    "semantic_relabel_control",
    "native_support_relabel_control",
    "phase8_relabel_control",
]

CONTRACT_COMPLETE_REQUIRED_OBJECTS = [
    "producer_residue_classification",
    "continuation_function_descriptor",
    "proxy_metric_definition",
    "support_scaffold_declaration",
    "same_basin_continuation_rule",
    "minimum_controls",
    "claim_ceiling",
    "unsafe_claim_flags",
]

PRIMITIVE_HANDOFF_MAP = {
    "withdrawal_resistance": "N21",
    "naturalization_depth": "N21",
    "susceptibility_update": "N22",
    "live_continuation_collapse": "N23",
    "surplus_supported_optionality": "N24",
    "spark_sub_basin_new_basin_formation": "N25",
    "proxy_divergence_proxy_collapse": "N26",
    "configuration_substrate_transfer": "N27",
    "generative_extractive_persistence": "N28",
}

BLOCKED_RELABEL_VARIABLE_EXAMPLES = [
    "semantic_choice",
    "semantic_goal",
    "agency",
    "identity_acceptance",
    "sentience",
    "native_ant_agency",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path.name} must contain a JSON object")
    return data


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def source_inventory_reference(source_inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": rel(INVENTORY),
        "sha256": sha256_file(INVENTORY),
        "output_digest": source_inventory["output_digest"],
        "status": source_inventory["status"],
        "acceptance_state": source_inventory["acceptance_state"],
        "row_count": source_inventory["row_count"],
    }


def source_consumption_schema(source_inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "required_fields_per_source_row": [
            "source_role",
            "may_consume_as",
            "must_not_consume_as",
            "source_consumption_rule",
        ],
        "source_roles": SOURCE_ROLES,
        "source_role_evidence_gates": SOURCE_ROLE_EVIDENCE_GATES,
        "source_precedence_rule": {
            "N12_N18_rows": "historical_prerequisite_context_only",
            "N19_row": "current_classification_boundary",
            "rule": (
                "Later schemas may use N12-N18 rows as historical context, but "
                "must consume N19 as the current implementation/native-readiness "
                "classification boundary."
            ),
            "historical_rows": [
                row["row_id"]
                for row in source_inventory["source_rows"]
                if row["source_id"] in {"N12_N18_ROADMAP", "N12_N18_HANDOFF"}
            ],
            "current_boundary_row": "n20_i1_row_01_n19_implementation_boundary",
        },
        "diagnostic_vocabulary_rule": (
            "Diagnostic vocabulary may define fields, names, and controls, but "
            "cannot satisfy evidence gates."
        ),
        "sentience_boundary_rule": (
            "Sentience as Read-Back may be consumed only as boundary source; "
            "sentience/read-back/interiority claims remain closed."
        ),
    }


def ap_gap_schema(source_inventory: dict[str, Any]) -> dict[str, Any]:
    source_map = source_inventory["ap_gap_propagation_map"]
    return {
        "source_map": {
            "path": rel(INVENTORY),
            "output_digest": source_inventory["output_digest"],
            "ap4_gap_carried_forward": source_map["ap4_gap_carried_forward"],
            "ap5_gap_carried_forward": source_map["ap5_gap_carried_forward"],
            "gap_status": source_map["gap_status"],
        },
        "required_gap_dependencies": {
            "ap4": source_map["ap4_gap"]["affected_primitives"],
            "ap5": source_map["ap5_gap"]["affected_primitives"],
        },
        "conditional_gap_dependencies": {
            "ap4": [
                {
                    "primitive": "configuration_substrate_transfer",
                    "condition": "route-conditioned selection is part of transfer",
                    "required_action": "carry AP4/N14 gap until source-backed route-conditioned naturalization result exists",
                }
            ],
            "ap5": [
                {
                    "primitive": "live_continuation_collapse",
                    "condition": "proxy or target formation participates in branch valuation",
                    "required_action": "carry AP5/N15 gap until source-backed proxy/target naturalization result exists",
                }
            ],
        },
        "propagation_rule": source_map["propagation_rule"],
        "gap_resolution_rule": (
            "A primitive may remove an AP4/AP5 gap only by recording a "
            "source-backed naturalization result; a label, roadmap reference, "
            "or essay citation cannot remove the gap."
        ),
        "row_local_dependency_rule": (
            "Every affected primitive row must carry its own AP4/AP5 dependency "
            "record; global gap maps are not sufficient for later support."
        ),
    }


def primitive_row_schema() -> dict[str, Any]:
    return {
        "required_fields": PRIMITIVE_ROW_REQUIRED_FIELDS,
        "allowed_primitive_ids": EXPECTED_PRIMITIVE_IDS,
        "classification_before_iteration3_allowed": False,
        "consumable_row_rule": (
            "N21-N28 may consume only rows with contract_status = complete and "
            "row_decision = supported."
        ),
        "variable_classification_record_schema": {
            "required_fields": [
                "variable_id",
                "classification",
                "source_current_visibility",
                "producer_surface",
                "naturalization_debt_type",
                "claim_boundary",
            ],
            "exactly_one_classification_required": True,
            "naturalization_debt_type_required_when": "classification = naturalization_debt",
            "producer_mediated_to_substrate_carried_conversion_rule": (
                "allowed only with source-backed naturalization result"
            ),
            "field_partition_rule": (
                "A variable_id may appear in exactly one of LGRC_visible_fields, "
                "producer_mediated_fields, naturalization_debt_fields, or "
                "blocked_relabel_fields."
            ),
            "blocked_relabel_variable_rule": (
                "Unsafe semantic labels are variable classifications of "
                "blocked_relabel, not producer-mediated variables."
            ),
            "blocked_relabel_variable_examples": BLOCKED_RELABEL_VARIABLE_EXAMPLES,
        },
        "native_function_descriptor_alias_rule": (
            "native_function_descriptor may appear only as an alias for "
            "continuation_function_descriptor and must not mean purpose, goal, "
            "semantic function, biological function, intention, or goal ownership."
        ),
        "contract_status_gate_schema": {
            "complete_requires": CONTRACT_COMPLETE_REQUIRED_OBJECTS,
            "missing_producer_residue_classification_maps_to": "incomplete_missing_producer_residue_classification",
            "missing_continuation_function_maps_to": "incomplete_missing_continuation_function",
            "missing_proxy_metric_maps_to": "incomplete_missing_proxy_metric",
            "missing_support_scaffold_declaration_maps_to": "incomplete_missing_support_scaffold_declaration",
            "missing_same_basin_rule_maps_to": "incomplete_missing_same_basin_rule",
            "missing_controls_maps_to": "incomplete_missing_controls",
            "missing_claim_ceiling_maps_to": "incomplete_missing_claim_ceiling",
            "missing_unsafe_claim_flags_maps_to": "incomplete_missing_unsafe_claim_flags",
            "missing_variable_classification_maps_to": "incomplete_missing_variable_classification",
            "missing_debt_subtype_maps_to": "incomplete_missing_debt_subtype",
            "unsafe_relabel_maps_to": "blocked_by_relabel",
        },
        "primitive_handoff_map": PRIMITIVE_HANDOFF_MAP,
    }


def contract_object_schemas() -> dict[str, Any]:
    return {
        "producer_definition": (
            "explicit implementation surface that introduces, updates, routes, "
            "schedules, labels, or preserves a quantity not yet carried by LGRC "
            "source-current geometry"
        ),
        "producer_required_fields": PRODUCER_REQUIRED_FIELDS,
        "continuation_function_descriptor_required_fields": (
            CONTINUATION_FUNCTION_DESCRIPTOR_FIELDS
        ),
        "proxy_metric_definition_required_fields": PROXY_METRIC_FIELDS,
        "support_scaffold_declaration_required_fields": SUPPORT_SCAFFOLD_FIELDS,
        "same_basin_continuation_required_fields": SAME_BASIN_FIELDS,
        "minimum_controls": MINIMUM_CONTROLS,
    }


def enums() -> dict[str, Any]:
    return {
        "source_roles": SOURCE_ROLES,
        "variable_classification": VARIABLE_CLASSIFICATION_ENUM,
        "naturalization_debt_type": NATURALIZATION_DEBT_TYPE_ENUM,
        "contract_status": CONTRACT_STATUS_ENUM,
        "row_decision": ROW_DECISION_ENUM,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "expected_primitive_ids": EXPECTED_PRIMITIVE_IDS,
    }


def validator_rules() -> list[str]:
    return [
        "source inventory must have passed",
        "primitive rows cannot be classified before schema freeze",
        "every future artifact must include the N20 invariant block",
        "every source row must expose may_consume_as and must_not_consume_as",
        "diagnostic vocabulary cannot satisfy evidence gates",
        "N19 is the current classification boundary; N12-N18 are historical context",
        "every variable receives exactly one classification",
        "the same variable cannot appear in multiple classification field buckets",
        "naturalization_debt variables require a debt subtype",
        "blocked_relabel fields cannot be producer_mediated variables",
        "every primitive row has continuation_function_descriptor",
        "every primitive row has proxy_metric_definition",
        "every primitive row has support_scaffold_declaration",
        "every primitive row has same_basin_continuation_rule",
        "every primitive row has minimum_controls",
        "applicable AP4/AP5 gaps must be carried forward",
        "affected primitives must carry AP4/AP5 dependencies row-locally",
        "every primitive has an expected N21-N28 handoff target",
        "unsafe claim flags must remain false per row",
        "absolute local paths are rejected",
    ]


def no_absolute_paths(data: Any) -> bool:
    return not absolute_path_strings(data)


def absolute_path_strings(data: Any) -> list[str]:
    found: list[str] = []
    if isinstance(data, str):
        if data.startswith("/") or data.startswith("file://"):
            found.append(data)
        elif len(data) >= 3 and data[1] == ":" and data[2] in {"\\", "/"}:
            found.append(data)
        return found
    if isinstance(data, dict):
        for value in data.values():
            found.extend(absolute_path_strings(value))
    elif isinstance(data, list):
        for value in data:
            found.extend(absolute_path_strings(value))
    return found


def build_checks(artifact: dict[str, Any], source_inventory: dict[str, Any]) -> list[dict[str, Any]]:
    source_rows = source_inventory["source_rows"]
    checks = [
        {
            "check_id": "source_inventory_passed",
            "passed": source_inventory["status"] == "passed"
            and not source_inventory["failed_checks"],
            "detail": source_inventory["acceptance_state"],
        },
        {
            "check_id": "source_inventory_ready_for_iteration2",
            "passed": source_inventory["ready_for_iteration_2_schema"] is True,
            "detail": source_inventory["ready_for_iteration_2_schema"],
        },
        {
            "check_id": "no_primitive_rows_classified_before_schema_freeze",
            "passed": artifact["primitive_rows_classified"] is False
            and artifact["primitive_evidence_opened"] is False,
            "detail": {
                "primitive_rows_classified": artifact["primitive_rows_classified"],
                "primitive_evidence_opened": artifact["primitive_evidence_opened"],
            },
        },
        {
            "check_id": "source_rows_have_positive_and_negative_consumption_fields",
            "passed": all(
                row["may_consume_as"]
                and row["must_not_consume_as"]
                and row["source_consumption_rule"]
                for row in source_rows
            ),
            "detail": len(source_rows),
        },
        {
            "check_id": "diagnostic_vocabulary_cannot_satisfy_evidence_gates",
            "passed": (
                "primitive_evidence_gate"
                in artifact["source_consumption_schema"]["source_role_evidence_gates"][
                    "diagnostic_vocabulary_source"
                ]["may_not_satisfy"]
            ),
            "detail": artifact["source_consumption_schema"]["diagnostic_vocabulary_rule"],
        },
        {
            "check_id": "n19_is_current_boundary_n12_n18_historical",
            "passed": (
                artifact["source_consumption_schema"]["source_precedence_rule"][
                    "current_boundary_row"
                ]
                == "n20_i1_row_01_n19_implementation_boundary"
                and artifact["source_consumption_schema"]["source_precedence_rule"][
                    "historical_rows"
                ]
                == [
                    "n20_i1_row_12_n12_n18_prerequisites_roadmap",
                    "n20_i1_row_13_n12_n18_prerequisites_handoff",
                ]
            ),
            "detail": artifact["source_consumption_schema"]["source_precedence_rule"],
        },
        {
            "check_id": "ap4_ap5_gap_dependencies_frozen",
            "passed": (
                artifact["ap_gap_dependency_schema"]["source_map"][
                    "ap4_gap_carried_forward"
                ]
                is True
                and artifact["ap_gap_dependency_schema"]["source_map"][
                    "ap5_gap_carried_forward"
                ]
                is True
                and artifact["ap_gap_dependency_schema"]["conditional_gap_dependencies"][
                    "ap4"
                ][0]["primitive"]
                == "configuration_substrate_transfer"
                and artifact["ap_gap_dependency_schema"]["conditional_gap_dependencies"][
                    "ap5"
                ][0]["primitive"]
                == "live_continuation_collapse"
            ),
            "detail": artifact["ap_gap_dependency_schema"]["conditional_gap_dependencies"],
        },
        {
            "check_id": "ap4_ap5_dependencies_are_row_local",
            "passed": "row_local_dependency_rule" in artifact["ap_gap_dependency_schema"],
            "detail": artifact["ap_gap_dependency_schema"]["row_local_dependency_rule"],
        },
        {
            "check_id": "contract_object_schemas_present",
            "passed": all(
                artifact["contract_object_schemas"][field]
                for field in [
                    "producer_required_fields",
                    "continuation_function_descriptor_required_fields",
                    "proxy_metric_definition_required_fields",
                    "support_scaffold_declaration_required_fields",
                    "same_basin_continuation_required_fields",
                    "minimum_controls",
                ]
            ),
            "detail": list(artifact["contract_object_schemas"].keys()),
        },
        {
            "check_id": "variable_classification_enum_exactly_one",
            "passed": artifact["primitive_row_schema"][
                "variable_classification_record_schema"
            ]["exactly_one_classification_required"]
            and artifact["enums"]["variable_classification"]
            == VARIABLE_CLASSIFICATION_ENUM,
            "detail": artifact["enums"]["variable_classification"],
        },
        {
            "check_id": "variable_field_partition_rule_frozen",
            "passed": "field_partition_rule"
            in artifact["primitive_row_schema"]["variable_classification_record_schema"],
            "detail": artifact["primitive_row_schema"][
                "variable_classification_record_schema"
            ]["field_partition_rule"],
        },
        {
            "check_id": "blocked_relabel_is_variable_classification",
            "passed": "blocked_relabel_variable_rule"
            in artifact["primitive_row_schema"]["variable_classification_record_schema"]
            and "blocked_relabel" in artifact["enums"]["variable_classification"],
            "detail": artifact["primitive_row_schema"][
                "variable_classification_record_schema"
            ]["blocked_relabel_variable_rule"],
        },
        {
            "check_id": "continuation_function_alias_rule_frozen",
            "passed": "continuation_function_descriptor"
            in artifact["primitive_row_schema"]["native_function_descriptor_alias_rule"],
            "detail": artifact["primitive_row_schema"][
                "native_function_descriptor_alias_rule"
            ],
        },
        {
            "check_id": "contract_status_complete_gate_hard_to_earn",
            "passed": artifact["primitive_row_schema"]["contract_status_gate_schema"][
                "complete_requires"
            ]
            == CONTRACT_COMPLETE_REQUIRED_OBJECTS
            and all(
                value in CONTRACT_STATUS_ENUM
                for key, value in artifact["primitive_row_schema"][
                    "contract_status_gate_schema"
                ].items()
                if key.endswith("_maps_to")
            ),
            "detail": artifact["primitive_row_schema"]["contract_status_gate_schema"],
        },
        {
            "check_id": "all_primitives_have_handoff_targets",
            "passed": sorted(artifact["primitive_row_schema"]["primitive_handoff_map"].keys())
            == sorted(EXPECTED_PRIMITIVE_IDS)
            and set(artifact["primitive_row_schema"]["primitive_handoff_map"].values())
            == {"N21", "N22", "N23", "N24", "N25", "N26", "N27", "N28"},
            "detail": artifact["primitive_row_schema"]["primitive_handoff_map"],
        },
        {
            "check_id": "unsafe_claim_flags_required_per_row",
            "passed": artifact["enums"]["unsafe_claim_flags"] == UNSAFE_CLAIM_FLAGS
            and "unsafe_claim_flags" in artifact["primitive_row_schema"]["required_fields"],
            "detail": len(artifact["enums"]["unsafe_claim_flags"]),
        },
        {
            "check_id": "artifact_invariants_preserved",
            "passed": artifact["artifact_invariants"] == INVARIANTS,
            "detail": artifact["artifact_invariants"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(artifact),
            "detail": "schema paths are relative",
        },
    ]
    return checks


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N20 Iteration 2 - Translation Schema V1",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"acceptance_state = {artifact['acceptance_state']}",
        f"candidate_rows_classified = {str(artifact['candidate_rows_classified']).lower()}",
        f"primitive_evidence_opened = {str(artifact['primitive_evidence_opened']).lower()}",
        f"agency_claim_opened = {str(artifact['agency_claim_opened']).lower()}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        "```",
        "",
        "Source precedence:",
        "",
        "```text",
        "N12-N18 = historical prerequisite context",
        "N19 = current classification boundary",
        "```",
        "",
        "Frozen enums:",
        "",
        "```json",
        json.dumps(artifact["enums"], indent=2, sort_keys=True),
        "```",
        "",
        "Primitive row required fields:",
        "",
        "```json",
        json.dumps(artifact["primitive_row_schema"]["required_fields"], indent=2),
        "```",
        "",
        "Contract object schemas:",
        "",
        "```json",
        json.dumps(artifact["contract_object_schemas"], indent=2, sort_keys=True),
        "```",
        "",
        "Source consumption evidence gates:",
        "",
        "```json",
        json.dumps(
            artifact["source_consumption_schema"]["source_role_evidence_gates"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "AP4/AP5 dependency rules:",
        "",
        "```json",
        json.dumps(artifact["ap_gap_dependency_schema"], indent=2, sort_keys=True),
        "```",
        "",
        "Validator rules:",
        "",
        "```json",
        json.dumps(artifact["validator_rules"], indent=2),
        "```",
        "",
        "Checks:",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.extend(
        [
            "",
            "Claim boundary:",
            "",
            "```text",
            artifact["claim_boundary"],
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    source_inventory = load_json(INVENTORY)
    artifact: dict[str, Any] = {
        "artifact_id": "n20_translation_schema_v1",
        "schema_version": "n20_translation_schema_v1",
        "experiment": "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract",
        "iteration": 2,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Freeze N20 translation schema, source consumption rules, producer "
            "definition, variable classification, continuation/proxy/support/"
            "same-basin contracts, claim flags, and gap propagation rules before "
            "primitive evidence is classified."
        ),
        "source_inventory": source_inventory_reference(source_inventory),
        "artifact_invariants": INVARIANTS,
        "candidate_rows_classified": False,
        "primitive_rows_classified": False,
        "primitive_evidence_opened": False,
        "agency_claim_opened": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "sentience_opened": False,
        "ant_ecology_spec_opened": False,
        "source_consumption_schema": source_consumption_schema(source_inventory),
        "primitive_row_schema": primitive_row_schema(),
        "contract_object_schemas": contract_object_schemas(),
        "ap_gap_dependency_schema": ap_gap_schema(source_inventory),
        "enums": enums(),
        "validator_rules": validator_rules(),
        "claim_boundary": (
            "N20 Iteration 2 freezes schema only. It does not classify primitive "
            "rows, open primitive evidence, use diagnostic vocabulary as proof, "
            "open Phase 8, open native support, open agency, or open sentience."
        ),
        "output_digest": "pending",
    }
    checks = build_checks(artifact, source_inventory)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact["checks"] = checks
    artifact["failed_checks"] = failed_checks
    artifact["status"] = "passed" if not failed_checks else "failed"
    artifact["acceptance_state"] = (
        "accepted_translation_schema_frozen_no_primitive_evidence"
        if not failed_checks
        else "failed_translation_schema_freeze"
    )
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()
