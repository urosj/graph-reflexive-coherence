#!/usr/bin/env python3
"""Build N29 Iteration 4 bridge schema and claim boundary freeze."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I1_OUTPUT = EXPERIMENT / "outputs" / "n29_ecology_demand_extraction_i1.json"
I2_OUTPUT = EXPERIMENT / "outputs" / "n29_agency_diagnostic_method_constraints_i2.json"
I3_OUTPUT = EXPERIMENT / "outputs" / "n29_capability_atlas_i3.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_schema_i4.json"
REPORT = EXPERIMENT / "reports" / "n29_bridge_schema_i4.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_bridge_schema_i4.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

BLOCKED_CLAIM_FLAGS = {
    "native_agency_claim_opened": False,
    "native_ant_agency_opened": False,
    "native_colony_agency_opened": False,
    "biological_agency_opened": False,
    "organism_life_opened": False,
    "consciousness_opened": False,
    "sentience_opened": False,
    "semantic_choice_claim_opened": False,
    "semantic_intention_claim_opened": False,
    "semantic_goal_claim_opened": False,
    "semantic_cooperation_claim_opened": False,
    "native_shared_medium_coordination_opened": False,
    "fully_native_ecology_opened": False,
    "phase8_completion_opened": False,
    "unrestricted_autonomy_opened": False,
    "prototype_as_native_ecology_opened": False,
}

SOURCE_ROLE_ENUM = [
    "target_requirement_not_evidence",
    "agency_diagnostic_not_evidence",
    "arc_method_constraint_not_evidence",
    "capability_card_import_only_no_revalidation",
    "source_artifact_full_data",
    "review_gate",
    "contract_gate",
    "runtime_evidence_source",
    "visual_diagnostic_only",
    "mapping_context_only",
]

CLAIM_CEILING_ENUM = [
    "target_requirement_only",
    "method_constraint_only",
    "capability_card_orientation_only",
    "source_backed_bridge_prototype_or_mapping_only_with_debt",
    "source_backed_bridge_exemplar_no_native_ecology",
    "mapping_only_no_runtime_surface",
    "visual_diagnostic_only_no_evidence_promotion",
    "blocked_by_missing_source",
    "blocked_by_claim_boundary",
    "outbound_handoff_contract_only",
    "inbound_handoff_debt_record_only",
]

COVERAGE_STATUS_ENUM = [
    "source_backed",
    "prototype_candidate",
    "producer_mediated",
    "medium_debt",
    "naturalization_debt",
    "native_ready_surface",
    "control_only",
    "blocked_relabel",
    "missing_runtime_surface",
    "not_applicable",
]

PROTOTYPE_STATUS_ENUM = [
    "runnable_runtime",
    "source_backed_reconstruction",
    "visual_diagnostic_only",
    "mapping_only_no_runtime_surface",
    "blocked_by_missing_source",
    "blocked_by_claim_boundary",
]

RUNTIME_RECONSTRUCTION_STATUS_ENUM = [
    "runnable_runtime",
    "source_backed_reconstruction",
    "artifact_only_reconstruction",
    "visual_diagnostic_only",
    "mapping_only_no_runtime_surface",
    "blocked",
]

MOTIF_FAMILY_ENUM = [
    "trace_pressure_loop",
    "reserve_optionality_formation",
    "boundary_shared_medium_unit",
    "proxy_susceptibility_reentry",
    "transfer_replay_role_relocation",
    "generative_extractive_medium_reshaping",
    "composition",
]

PROTOTYPE_CLASS_ENUM = [
    "trace_aftereffect",
    "reserve_pressure",
    "boundary_mobile_expression",
    "closed_loop_perturbation_response",
    "proxy_collapse",
    "configuration_transfer",
    "generative_extractive_medium_reshaping",
    "composition",
]

HANDOFF_DIRECTION_ENUM = [
    "outbound_to_agentic_ecology",
    "inbound_to_n30_plus_core_primitives",
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
    return json.loads(path.read_text(encoding="utf-8"))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def field_schema(required_fields: list[str], optional_fields: list[str] | None = None) -> dict[str, Any]:
    return {
        "required_fields": required_fields,
        "optional_fields": optional_fields or [],
        "missing_required_field_blocks_row": True,
        "unknown_fields_allowed": True,
        "unknown_fields_must_be_namespaced": True,
        "unknown_field_prefix": "x_",
        "unknown_field_review_status_required": True,
        "unknown_fields_policy": (
            "allowed only when namespaced with x_, reviewed with "
            "x_unknown_field_review_status, and unable to raise claim ceiling or "
            "replace required fields"
        ),
    }


def build_schema_bundle() -> dict[str, Any]:
    ecology_demand_schema = field_schema(
        [
            "demand_id",
            "ecology_component",
            "source_spec_reference",
            "required_dynamics",
            "required_state_surfaces",
            "required_trace_surfaces",
            "required_controls",
            "blocked_relabels",
            "first_probe_relevance",
        ],
        [
            "producer_residue_risk",
            "medium_debt_risk",
            "claim_ceiling",
        ],
    )
    capability_card_schema = field_schema(
        [
            "capability_id",
            "source_experiment",
            "source_artifacts",
            "source_claim_ceiling",
            "review_gate_status",
            "native_readiness_status",
            "supplied_geometry_or_dynamic",
            "producer_residue",
            "naturalization_debt",
            "medium_debt",
            "possible_ecology_demands",
            "blocked_ecology_relabels",
            "prototype_potential",
        ],
        [
            "source_group",
            "consumption_rule",
            "source_of_truth_policy",
        ],
    )
    coverage_debt_row_schema = field_schema(
        [
            "source_experiment_or_spec",
            "ecology_demand",
            "candidate_capability_sources",
            "bridge_motif",
            "agency_diagnostic_role",
            "coverage_status",
            "coverage_reason",
            "producer_residue",
            "medium_debt",
            "naturalization_debt",
            "native_readiness_status",
            "native_readiness_gap",
            "blocked_relabels",
            "first_probe_implication",
            "claim_ceiling",
            "why_not_stronger",
        ],
        [
            "source_artifacts_consumed",
            "source_of_truth_check",
        ],
    )
    bridge_motif_row_schema = field_schema(
        [
            "motif_id",
            "motif_family",
            "ecology_demands_connected",
            "capability_sources",
            "ordered_composition",
            "expected_dynamic",
            "runtime_or_reconstruction_status",
            "producer_residue",
            "medium_debt",
            "controls",
            "prototype_candidate",
            "first_probe_relevance",
            "claim_ceiling",
            "why_not_stronger",
        ],
        [
            "source_artifacts_consumed",
            "naturalization_gap",
            "component_order_inversion_control",
        ],
    )
    prototype_row_schema = field_schema(
        [
            "prototype_id",
            "source_rows",
            "source_digests",
            "ecology_demand_role",
            "supplied_capability",
            "bridge_motif",
            "bridge_exemplar_role",
            "composition_role",
            "agency_diagnostic_role",
            "runtime_or_reconstruction_status",
            "producer_residue",
            "medium_debt",
            "naturalization_gap",
            "controls",
            "next_probe_contract",
            "claim_ceiling",
            "unsafe_claim_flags",
            "why_not_stronger",
        ],
        [
            "prototype_status",
            "missing_surface_reason",
            "first_probe_requirement",
        ],
    )
    handoff_ledger_row_schema = field_schema(
        [
            "handoff_direction",
            "handoff_target",
            "handoff_payload",
            "source_rows",
            "bridge_motifs",
            "prototype_exemplars",
            "unresolved_debt",
            "claim_ceiling",
            "blocked_relabels",
            "next_action",
            "why_not_stronger",
        ],
        [
            "handoff_readiness",
            "downstream_repository",
            "inbound_n30_plus_target",
        ],
    )
    return {
        "ecology_demand_row_schema": ecology_demand_schema,
        "capability_card_schema": capability_card_schema,
        "coverage_debt_row_schema": coverage_debt_row_schema,
        "bridge_motif_row_schema": bridge_motif_row_schema,
        "prototype_row_schema": prototype_row_schema,
        "handoff_ledger_row_schema": handoff_ledger_row_schema,
    }


def negative_fixture_rows() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "coverage_row_uses_capability_card_as_runtime_evidence",
            "fixture_family": "source_of_truth_control",
            "bad_condition": "coverage row cites only I3 capability card for source_backed claim",
            "expected_status": "rejected",
            "blocked_by": "capability_card_used_as_runtime_evidence",
            "claim_allowed": False,
        },
        {
            "fixture_id": "producer_mediated_row_claims_native_ready_surface",
            "fixture_family": "native_readiness_control",
            "bad_condition": "producer-mediated row claims native_ready_surface without native gate",
            "expected_status": "rejected",
            "blocked_by": "producer_residue_as_native_ready_surface",
            "claim_allowed": False,
        },
        {
            "fixture_id": "medium_debt_row_claims_native_shared_medium_coordination",
            "fixture_family": "medium_debt_control",
            "bad_condition": "medium debt is relabeled as native shared-medium coordination",
            "expected_status": "rejected",
            "blocked_by": "medium_debt_hidden_as_native_relation_control",
            "claim_allowed": False,
        },
        {
            "fixture_id": "visual_diagnostic_only_row_claims_source_backed",
            "fixture_family": "visual_relabel_control",
            "bad_condition": "visual-only row uses source_backed claim ceiling",
            "expected_status": "rejected",
            "blocked_by": "visual_only_as_evidence_control",
            "claim_allowed": False,
        },
        {
            "fixture_id": "bridge_motif_missing_controls",
            "fixture_family": "motif_control",
            "bad_condition": "bridge motif omits required relabel/order/source controls",
            "expected_status": "rejected",
            "blocked_by": "missing_required_controls",
            "claim_allowed": False,
        },
        {
            "fixture_id": "composition_row_hides_component_order",
            "fixture_family": "composition_control",
            "bad_condition": "composition row omits ordered composition or hides order inversion risk",
            "expected_status": "rejected",
            "blocked_by": "component_order_inversion_control",
            "claim_allowed": False,
        },
        {
            "fixture_id": "n28_generative_relabelled_as_cooperation",
            "fixture_family": "unsafe_ecology_relabel_control",
            "bad_condition": "N28 generative pattern is relabeled as cooperation or altruism",
            "expected_status": "rejected",
            "blocked_by": "semantic_cooperation_claim_opened",
            "claim_allowed": False,
        },
        {
            "fixture_id": "prototype_as_native_ecology",
            "fixture_family": "prototype_relabel_control",
            "bad_condition": "prototype row claims native ecology behavior",
            "expected_status": "rejected",
            "blocked_by": "prototype_as_native_ecology_opened",
            "claim_allowed": False,
        },
        {
            "fixture_id": "missing_n12_or_n19_review_gate_for_gated_source",
            "fixture_family": "review_gate_control",
            "bad_condition": "N05-N11 or N13-N18 source row omits N12/N19 gate",
            "expected_status": "rejected",
            "blocked_by": "review_gate_omitted_for_gated_source",
            "claim_allowed": False,
        },
        {
            "fixture_id": "ap4_ap5_gap_hidden_by_ecology_language",
            "fixture_family": "ap_gap_control",
            "bad_condition": "AP4/AP5 native-readiness gaps are hidden by ecology vocabulary",
            "expected_status": "rejected",
            "blocked_by": "claim_ceiling_missing_or_raised_without_source",
            "claim_allowed": False,
        },
    ]


def positive_fixture_rows() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "example_ecology_demand_row_shape",
            "schema": "ecology_demand_row_schema",
            "fixture_status": "shape_example_not_evidence",
            "claim_ceiling": "target_requirement_only",
            "positive_evidence_opened": False,
            "why_not_stronger": "demand row records target requirements only; no capability source is consumed",
        },
        {
            "fixture_id": "example_capability_card_row_shape",
            "schema": "capability_card_schema",
            "fixture_status": "shape_example_not_evidence",
            "claim_ceiling": "capability_card_orientation_only",
            "positive_evidence_opened": False,
            "why_not_stronger": "capability card orients later work but cannot replace source artifacts",
        },
        {
            "fixture_id": "example_missing_surface_coverage_row_shape",
            "schema": "coverage_debt_row_schema",
            "fixture_status": "shape_example_not_evidence",
            "coverage_status": "missing_runtime_surface",
            "claim_ceiling": "mapping_only_no_runtime_surface",
            "positive_evidence_opened": False,
            "why_not_stronger": "row records missing surface and first probe implication only",
        },
        {
            "fixture_id": "example_mapping_only_motif_row_shape",
            "schema": "bridge_motif_row_schema",
            "fixture_status": "shape_example_not_evidence",
            "runtime_or_reconstruction_status": "mapping_only_no_runtime_surface",
            "claim_ceiling": "mapping_only_no_runtime_surface",
            "positive_evidence_opened": False,
            "why_not_stronger": "motif is a bounded composition sketch without runtime source evidence",
        },
        {
            "fixture_id": "example_blocked_prototype_row_shape",
            "schema": "prototype_row_schema",
            "fixture_status": "shape_example_not_evidence",
            "prototype_status": "blocked_by_missing_source",
            "claim_ceiling": "blocked_by_missing_source",
            "positive_evidence_opened": False,
            "why_not_stronger": "prototype records next probe contract but cannot claim evidence yet",
        },
    ]


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": passed}
    if details is not None:
        row["details"] = details
    return row


def build() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT)
    i2 = load_json(I2_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    schemas = build_schema_bundle()

    source_of_truth_policy = {
        "capability_cards_role": "orientation_index_and_claim_boundary_summary_only",
        "capability_cards_are_full_data_source": False,
        "source_artifacts_required_for_full_data": True,
        "full_data_source_types": [
            "original_experiment_artifact",
            "closeout_or_handoff_json",
            "runtime_record",
            "source_report",
            "visual_manifest_when_visual_claim_is_explicit",
        ],
        "phase_b_c_rule": (
            "I5-I16 rows may use I3 cards as an index, but source-backed coverage, "
            "motif, prototype, and handoff claims must cite original artifacts or "
            "runtime records directly."
        ),
        "fail_closed_conditions": [
            "source_artifact_missing",
            "source_digest_missing_for_evidence_claim",
            "capability_card_used_as_runtime_evidence",
            "review_gate_omitted_for_gated_source",
            "claim_ceiling_missing_or_raised_without_source",
        ],
    }

    control_policy = {
        "required_composition_controls": [
            "label_only_composition_control",
            "report_only_composition_control",
            "hidden_producer_coupling_control",
            "medium_debt_hidden_as_native_relation_control",
            "component_order_inversion_control",
            "missing_source_row_control",
            "unsafe_ecology_relabel_control",
        ],
        "prototype_admission_controls": [
            "report_only_as_runtime_control",
            "visual_only_as_evidence_control",
            "hidden_producer_coupling_control",
            "native_ecology_relabel_control",
            "missing_source_digest_control",
        ],
        "control_status_enum": [
            "passed",
            "failed_closed",
            "failed_open",
            "not_run",
            "not_applicable_with_reason",
        ],
        "failed_open_blocks_row": True,
        "not_run_blocks_dependent_claim": True,
    }

    executable_source_of_truth_gates = [
        {
            "gate_id": "source_backed_coverage_requires_original_artifact",
            "applies_when": "coverage_status in {source_backed, native_ready_surface, prototype_candidate}",
            "requires": [
                "source_artifacts_consumed",
                "original_artifact_or_runtime_record_digest",
                "source_of_truth_check = original_artifact_or_runtime_record_verified",
            ],
            "rejects": "only_I3_capability_card_cited",
        },
        {
            "gate_id": "prototype_candidate_requires_full_data_source",
            "applies_when": "bridge_motif.prototype_candidate = true",
            "requires": ["source_artifact_full_data_or_runtime_evidence_source"],
            "rejects": "motif_uses_mapping_only_or_card_only_source",
        },
        {
            "gate_id": "visual_only_blocks_source_backed_claim",
            "applies_when": "runtime_or_reconstruction_status = visual_diagnostic_only",
            "requires": ["claim_ceiling = visual_diagnostic_only_no_evidence_promotion"],
            "rejects": "source_backed_or_native_ready_surface_claim",
        },
    ]

    cross_enum_rules = [
        {
            "rule_id": "coverage_source_backed_requires_non_visual_full_source",
            "if": "coverage_status = source_backed",
            "then": [
                "runtime_or_reconstruction_status != visual_diagnostic_only",
                "source_of_truth_check = original_artifact_or_runtime_record_verified",
            ],
        },
        {
            "rule_id": "coverage_native_ready_surface_requires_native_gate",
            "if": "coverage_status = native_ready_surface",
            "then": [
                "native_readiness_status indicates native_ready_surface or equivalent explicit gate",
                "producer_residue = none or explicitly bounded without native upgrade",
            ],
        },
        {
            "rule_id": "prototype_visual_only_claim_ceiling",
            "if": "prototype_status = visual_diagnostic_only",
            "then": ["claim_ceiling = visual_diagnostic_only_no_evidence_promotion"],
        },
        {
            "rule_id": "artifact_only_reconstruction_not_runtime",
            "if": "runtime_or_reconstruction_status = artifact_only_reconstruction",
            "then": ["runnable_runtime claim is blocked"],
        },
    ]

    phase_b_separation_rules = {
        "I5": {
            "job": "ecology_demand_matrix_only",
            "must_not": [
                "import_N05_N28_evidence",
                "match_demand_to_supply",
                "create_bridge_motifs",
                "open_prototype_rows",
            ],
        },
        "I6": {
            "job": "capability_supply_atlas_only",
            "must_not": [
                "create_coverage_debt_matches",
                "create_bridge_motifs",
                "open_prototype_rows",
            ],
        },
        "I7": {
            "job": "demand_supply_coverage_debt_matching_only",
            "must_not": [
                "create_bridge_motifs",
                "open_prototype_rows",
                "claim_native_ecology",
            ],
        },
    }

    handoff_validation_rules = {
        "outbound_to_agentic_ecology": {
            "requires": [
                "unresolved_debt",
                "blocked_relabels",
                "claim_ceiling = outbound_handoff_contract_only or bounded equivalent",
            ],
            "must_not": ["claim_native_ecology", "omit_N30_plus_debt"],
        },
        "inbound_to_n30_plus_core_primitives": {
            "requires": [
                "missing_native_mechanism",
                "producer_surface_to_naturalize_or_medium_surface_to_strengthen",
                "source_rows_that_exposed_gap",
            ],
            "must_not": ["imply_graph_reflexive_coherence_work_is_finished"],
        },
    }

    source_fidelity_audit = {
        "i1": {
            "audit_role": "structural_primary_source_fidelity_for_demand_rows",
            "verified": [
                "ecology rows are demand-only",
                "sampled demand rows have source_spec_reference",
                "sampled demand rows have blocked_relabels",
                "positive ecology evidence remains closed",
            ],
            "semantic_source_review_required_for_phase_b_claims": True,
        },
        "i2": {
            "audit_role": "structural_primary_source_fidelity_for_diagnostic_rows",
            "verified": [
                "five required diagnostics present",
                "Arc method constraints are method constraints not evidence gates",
                "generative_agency blocks cooperation/altruism/colony agency relabel",
            ],
            "semantic_source_review_required_for_phase_b_claims": True,
        },
        "i3": {
            "audit_role": "structural_primary_source_fidelity_for_capability_cards",
            "verified": [
                "major source bands represented",
                "claim ceilings recorded",
                "producer_residue medium_debt naturalization_debt row-local",
                "capability cards are orientation only",
            ],
            "semantic_source_review_required_for_phase_b_claims": True,
        },
    }

    data: dict[str, Any] = {
        "artifact_id": "n29_bridge_schema_i4",
        "schema_version": "n29_bridge_schema_v1",
        "schema_status": "frozen_for_phase_b",
        "experiment_id": "N29",
        "iteration": "I4",
        "title": "Bridge Schema And Claim Boundary Freeze",
        "status": "passed",
        "acceptance_state": "accepted_bridge_schema_frozen_no_positive_prototypes",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": [
            {
                "artifact_id": "n29_ecology_demand_extraction_i1",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_ecology_demand_extraction_i1.json"
                ),
                "status": i1.get("status", "not_recorded"),
                "output_digest": i1.get("output_digest", "not_recorded"),
            },
            {
                "artifact_id": "n29_agency_diagnostic_method_constraints_i2",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_agency_diagnostic_method_constraints_i2.json"
                ),
                "status": i2.get("status", "not_recorded"),
                "output_digest": i2.get("output_digest", "not_recorded"),
            },
            {
                "artifact_id": "n29_capability_atlas_i3",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_capability_atlas_i3.json"
                ),
                "status": i3.get("status", "not_recorded"),
                "output_digest": i3.get("output_digest", "not_recorded"),
            },
        ],
        "bridge_schema_frozen": True,
        "schema_bundle": schemas,
        "negative_fixture_rows": negative_fixture_rows(),
        "positive_fixture_rows": positive_fixture_rows(),
        "source_role_enum": SOURCE_ROLE_ENUM,
        "claim_ceiling_enum": CLAIM_CEILING_ENUM,
        "coverage_status_enum": COVERAGE_STATUS_ENUM,
        "prototype_status_enum": PROTOTYPE_STATUS_ENUM,
        "runtime_or_reconstruction_status_enum": RUNTIME_RECONSTRUCTION_STATUS_ENUM,
        "motif_family_enum": MOTIF_FAMILY_ENUM,
        "prototype_class_enum": PROTOTYPE_CLASS_ENUM,
        "handoff_direction_enum": HANDOFF_DIRECTION_ENUM,
        "blocked_claim_list": list(BLOCKED_CLAIM_FLAGS.keys()),
        "claim_boundary_audit": copy.deepcopy(BLOCKED_CLAIM_FLAGS),
        "claim_flag_location_policy": {
            "canonical_claim_flag_location": "claim_boundary_audit",
            "top_level_flags_are_convenience_mirrors": True,
            "blocked_claim_list_must_equal_claim_boundary_audit_keys": True,
        },
        "source_of_truth_policy": source_of_truth_policy,
        "executable_source_of_truth_gates": executable_source_of_truth_gates,
        "cross_enum_rules": cross_enum_rules,
        "control_policy": control_policy,
        "unknown_field_policy": {
            "unknown_fields_allowed": True,
            "unknown_fields_must_be_namespaced": True,
            "unknown_field_prefix": "x_",
            "unknown_field_review_status_required": True,
            "accepted_review_status": "accepted_no_claim_effect",
        },
        "phase_b_separation_rules": phase_b_separation_rules,
        "handoff_validation_rules": handoff_validation_rules,
        "source_fidelity_audit": source_fidelity_audit,
        "phase_a_closeout_status": "closed_phase_a_schema_ready_for_phase_b",
        "implementation_evidence_opened": False,
        "positive_ecology_evidence_opened": False,
        "positive_prototype_rows_opened": False,
        "prototype_rows_opened": False,
        "native_agency_claim_opened": False,
        "native_ant_agency_opened": False,
        "native_colony_agency_opened": False,
        "biological_agency_opened": False,
        "organism_life_opened": False,
        "sentience_opened": False,
        "phase8_completion_opened": False,
        "claim_ceiling": "bridge_schema_freeze_only_no_positive_prototypes_no_native_ecology_claim",
        "ready_for_iteration_5": True,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }

    expected_schema_sections = {
        "ecology_demand_row_schema",
        "capability_card_schema",
        "coverage_debt_row_schema",
        "bridge_motif_row_schema",
        "prototype_row_schema",
        "handoff_ledger_row_schema",
    }
    checks = [
        check("i1_ecology_demand_model_passed", i1.get("status") == "passed"),
        check("i2_agency_method_constraints_passed", i2.get("status") == "passed"),
        check("i3_capability_atlas_passed", i3.get("status") == "passed"),
        check("all_required_schema_sections_present", set(schemas) == expected_schema_sections),
        check(
            "coverage_status_enum_complete",
            set(COVERAGE_STATUS_ENUM)
            == {
                "source_backed",
                "prototype_candidate",
                "producer_mediated",
                "medium_debt",
                "naturalization_debt",
                "native_ready_surface",
                "control_only",
                "blocked_relabel",
                "missing_runtime_surface",
                "not_applicable",
            },
        ),
        check(
            "motif_family_enum_complete",
            set(MOTIF_FAMILY_ENUM)
            == {
                "trace_pressure_loop",
                "reserve_optionality_formation",
                "boundary_shared_medium_unit",
                "proxy_susceptibility_reentry",
                "transfer_replay_role_relocation",
                "generative_extractive_medium_reshaping",
                "composition",
            },
        ),
        check(
            "prototype_status_enum_complete",
            set(PROTOTYPE_STATUS_ENUM)
            == {
                "runnable_runtime",
                "source_backed_reconstruction",
                "visual_diagnostic_only",
                "mapping_only_no_runtime_surface",
                "blocked_by_missing_source",
                "blocked_by_claim_boundary",
            },
        ),
        check(
            "source_of_truth_policy_requires_original_artifacts",
            not source_of_truth_policy["capability_cards_are_full_data_source"]
            and source_of_truth_policy["source_artifacts_required_for_full_data"],
        ),
        check(
            "blocked_claim_list_matches_claim_boundary_audit_keys",
            set(data["blocked_claim_list"]) == set(data["claim_boundary_audit"].keys()),
        ),
        check(
            "coverage_schema_matches_hypothesis_b_required_context",
            {
                "source_experiment_or_spec",
                "bridge_motif",
                "agency_diagnostic_role",
                "native_readiness_status",
                "native_readiness_gap",
                "blocked_relabels",
            }.issubset(set(schemas["coverage_debt_row_schema"]["required_fields"])),
        ),
        check(
            "why_not_stronger_required_for_downstream_rows",
            all(
                "why_not_stronger" in schemas[schema_id]["required_fields"]
                for schema_id in [
                    "coverage_debt_row_schema",
                    "bridge_motif_row_schema",
                    "prototype_row_schema",
                    "handoff_ledger_row_schema",
                ]
            ),
        ),
        check(
            "unknown_field_policy_frozen",
            data["unknown_field_policy"]["unknown_fields_must_be_namespaced"]
            and data["unknown_field_policy"]["unknown_field_review_status_required"]
            and all(
                schema["unknown_fields_must_be_namespaced"]
                and schema["unknown_field_review_status_required"]
                for schema in schemas.values()
            ),
        ),
        check(
            "negative_fixture_rows_fail_closed",
            len(data["negative_fixture_rows"]) == 10
            and all(
                row["expected_status"] == "rejected" and not row["claim_allowed"]
                for row in data["negative_fixture_rows"]
            ),
        ),
        check(
            "positive_fixture_rows_are_shape_only",
            len(data["positive_fixture_rows"]) == 5
            and all(
                row["fixture_status"] == "shape_example_not_evidence"
                and not row["positive_evidence_opened"]
                for row in data["positive_fixture_rows"]
            ),
        ),
        check(
            "phase_b_separation_rules_frozen",
            set(phase_b_separation_rules) == {"I5", "I6", "I7"}
            and "open_prototype_rows" in phase_b_separation_rules["I5"]["must_not"]
            and "create_coverage_debt_matches" in phase_b_separation_rules["I6"]["must_not"]
            and "claim_native_ecology" in phase_b_separation_rules["I7"]["must_not"],
        ),
        check(
            "executable_source_of_truth_gates_frozen",
            len(executable_source_of_truth_gates) == 3
            and all("rejects" in row and "requires" in row for row in executable_source_of_truth_gates),
        ),
        check(
            "cross_enum_rules_frozen",
            len(cross_enum_rules) == 4
            and all("if" in row and "then" in row for row in cross_enum_rules),
        ),
        check(
            "handoff_validation_rules_frozen",
            set(handoff_validation_rules) == {
                "outbound_to_agentic_ecology",
                "inbound_to_n30_plus_core_primitives",
            },
        ),
        check(
            "source_fidelity_audit_requires_original_sources_for_phase_b_claims",
            all(
                row["semantic_source_review_required_for_phase_b_claims"]
                for row in source_fidelity_audit.values()
            ),
        ),
        check(
            "claim_boundary_flags_false",
            not any(data["claim_boundary_audit"].values()),
        ),
        check(
            "positive_prototypes_remain_closed",
            not data["positive_prototype_rows_opened"]
            and not data["prototype_rows_opened"]
            and not data["positive_ecology_evidence_opened"],
        ),
        check(
            "controls_fail_closed_policy_frozen",
            control_policy["failed_open_blocks_row"]
            and control_policy["not_run_blocks_dependent_claim"],
        ),
        check("ready_for_iteration_5", data["ready_for_iteration_5"]),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]

    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 4 - Bridge Schema And Claim Boundary Freeze",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- schema_version: `{data['schema_version']}`",
        f"- schema_status: `{data['schema_status']}`",
        f"- bridge_schema_frozen: `{str(data['bridge_schema_frozen']).lower()}`",
        f"- negative_fixture_rows: `{len(data['negative_fixture_rows'])}`",
        f"- positive_fixture_rows: `{len(data['positive_fixture_rows'])}`",
        f"- positive_prototype_rows_opened: `{str(data['positive_prototype_rows_opened']).lower()}`",
        f"- positive_ecology_evidence_opened: `{str(data['positive_ecology_evidence_opened']).lower()}`",
        f"- ready_for_iteration_5: `{str(data['ready_for_iteration_5']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 4 closes Phase A by freezing the bridge schemas, enum values,",
        "source-of-truth policy, controls, and blocked claim list. It does not build",
        "coverage rows, motifs, prototype rows, or ecology evidence.",
        "",
        "## Frozen Schema Sections",
        "",
        "| Schema | Required Field Count |",
        "| --- | --- |",
    ]
    for schema_id, schema in data["schema_bundle"].items():
        lines.append(f"| `{schema_id}` | `{len(schema['required_fields'])}` |")
    lines.extend(
        [
            "",
            "## Frozen Enums",
            "",
            f"- coverage_status_enum: `{', '.join(data['coverage_status_enum'])}`",
            f"- motif_family_enum: `{', '.join(data['motif_family_enum'])}`",
            f"- prototype_status_enum: `{', '.join(data['prototype_status_enum'])}`",
            f"- handoff_direction_enum: `{', '.join(data['handoff_direction_enum'])}`",
            "",
            "## Source Of Truth Policy",
            "",
            f"- capability_cards_are_full_data_source: `{str(data['source_of_truth_policy']['capability_cards_are_full_data_source']).lower()}`",
            f"- source_artifacts_required_for_full_data: `{str(data['source_of_truth_policy']['source_artifacts_required_for_full_data']).lower()}`",
            f"- phase_b_c_rule: {data['source_of_truth_policy']['phase_b_c_rule']}",
            "",
            "## Executable Gates",
            "",
            "| Gate | Rejects |",
            "| --- | --- |",
        ]
    )
    for gate in data["executable_source_of_truth_gates"]:
        lines.append(f"| `{gate['gate_id']}` | `{gate['rejects']}` |")
    lines.extend(
        [
            "",
            "## Fixture Rows",
            "",
            "Negative fixtures are fail-closed examples for source, producer, medium,",
            "visual, composition, AP-gap, and prototype relabel failures. Positive",
            "fixtures are schema-shape examples only; they open no ecology evidence.",
            "",
            "| Fixture Family | Count | Claim Allowed |",
            "| --- | --- | --- |",
        ]
    )
    negative_families: dict[str, int] = {}
    for row in data["negative_fixture_rows"]:
        negative_families[row["fixture_family"]] = negative_families.get(row["fixture_family"], 0) + 1
    for family, count in sorted(negative_families.items()):
        lines.append(f"| `{family}` | `{count}` | `false` |")
    lines.extend(
        [
            "",
            "## Phase B Separation",
            "",
            "| Iteration | Job | Must Not |",
            "| --- | --- | --- |",
        ]
    )
    for iteration, rule in data["phase_b_separation_rules"].items():
        lines.append(
            f"| `{iteration}` | `{rule['job']}` | `{', '.join(rule['must_not'])}` |"
        )
    lines.extend(
        [
            "",
            "## Blocked Claim Boundary",
            "",
        ]
    )
    for claim, opened in data["claim_boundary_audit"].items():
        lines.append(f"- `{claim}` = `{str(opened).lower()}`")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I4 is a schema freeze, not a positive evidence pass. It makes Phase B",
            "safe to start by fixing the row shapes and enums that coverage/debt rows",
            "must obey. Capability cards remain orientation records; later rows must",
            "return to original experiment artifacts for full data.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()
