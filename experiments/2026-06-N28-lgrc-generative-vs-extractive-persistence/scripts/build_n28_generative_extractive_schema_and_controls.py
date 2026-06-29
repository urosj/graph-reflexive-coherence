#!/usr/bin/env python3
"""Build N28 Iteration 2 generative/extractive schema and controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
I1_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_source_inventory_and_contract_admission.json"
)
OUTPUT = EXPERIMENT / "outputs" / "n28_generative_extractive_schema_and_controls.json"
REPORT = EXPERIMENT / "reports" / "n28_generative_extractive_schema_and_controls.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_generative_extractive_schema_and_controls.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

EXPECTED_I1_DIGEST = "f30af50b1e1209039b82454b510f4765de7ee8befe214d96218dec3207db5985"

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "ap5_nat4_gap_resolution_claim_allowed": False,
    "generative_persistence_claim_allowed": False,
    "n28_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_cooperation_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_identity_claim_allowed": False,
    "semantic_learning_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}

REQUIRED_EVIDENCE_FIELDS = [
    "row_id",
    "iteration",
    "row_decision",
    "ge_ladder_rung",
    "n28_closeout_ceiling",
    "regime_label",
    "regime_evidence_role",
    "shared_regime_policy_id",
    "shared_regime_policy_status",
    "policy_divergence_record",
    "source_current_inputs",
    "source_inventory_output_digest",
    "source_ledger_row_digest",
    "descriptor_contract_row_digest",
    "consumable_contract_row_digest",
    "source_output_digest",
    "n20_producer_residue_row_digest",
    "n20_native_function_proxy_row_digest",
    "n20_same_basin_continuation_row_digest",
    "n27_closeout_output_digest",
    "n27_side_effect_precursor_output_digest",
    "run_artifact_id",
    "runtime_config_digest",
    "artifact_manifest",
    "all_artifact_sha256_match_file_contents",
    "derived_report_only",
    "row_specific_thresholds_declared_before_use",
    "focal_basin_id",
    "focal_basin_signature_trace",
    "focal_basin_stability_trace",
    "focal_support_coherence_floor_trace",
    "neighbor_or_sub_basin_scope",
    "neighbor_basin_distinguishability_trace",
    "neighbor_support_floor_trace",
    "neighbor_boundary_integrity_trace",
    "environment_basin_forming_capacity_trace",
    "neighborhood_capacity_delta_trace",
    "focal_extraction_cost_trace",
    "extractive_flattening_trace",
    "merge_leakage_trace",
    "capacity_attribution_trace",
    "medium_debt_record",
    "producer_residue_record",
    "generative_classification_policy_digest",
    "generative_classification_declared_before_use",
    "generative_classification_result",
    "regime_boundary_trace",
    "policy_retuned_for_label",
    "label_specific_thresholds_used",
    "post_hoc_boundary_shift_used",
    "generative_extractive_core",
    "generative_extractive_core_digest",
    "focal_survival_only_rejected",
    "neighbor_label_only_rejected",
    "merge_leakage_as_support_rejected",
    "extractive_flattening_masked_rejected",
    "transfer_success_as_n28_success_rejected",
    "semantic_cooperation_relabel_rejected",
    "replay_result",
    "control_results",
    "ap4_dependency_status",
    "ap4_condition_reason",
    "ap5_dependency_status",
    "ap5_condition_reason",
    "claim_ceiling",
    "unsafe_claim_flags",
]

CORE_FIELDS = [
    "focal_basin_id",
    "focal_signature_digest",
    "focal_stability_digest",
    "neighbor_scope_digest",
    "neighbor_distinguishability_digest",
    "neighbor_support_digest",
    "neighbor_boundary_digest",
    "environment_capacity_digest",
    "neighborhood_capacity_delta_digest",
    "extraction_cost_digest",
    "extractive_flattening_digest",
    "merge_leakage_digest",
    "capacity_attribution_digest",
    "classification_policy_digest",
    "classification_result",
    "regime_evidence_role",
]

CONTROL_IDS = [
    "source_digest_mismatch_control",
    "derived_report_only_positive_row_control",
    "artifact_manifest_failure_control",
    "threshold_declared_after_outcome_control",
    "missing_focal_stability_digest_control",
    "missing_neighbor_capacity_digest_control",
    "missing_extraction_cost_digest_control",
    "missing_merge_leakage_digest_control",
    "missing_capacity_attribution_digest_control",
    "malformed_generative_extractive_core_digest_control",
    "policy_retuning_to_fit_label_control",
    "label_specific_threshold_control",
    "post_hoc_regime_boundary_shift_control",
    "focal_survival_only_as_generative_control",
    "neighbor_label_only_as_capacity_control",
    "neighbor_count_only_as_capacity_control",
    "merge_leakage_as_support_control",
    "extractive_flattening_masked_control",
    "competitive_persistence_as_generative_control",
    "transfer_success_as_n28_success_control",
    "hidden_capacity_attribution_policy_control",
    "producer_generativity_label_control",
    "medium_segmentation_policy_hidden_control",
    "environment_capacity_budget_mismatch_control",
    "neighbor_support_floor_missing_control",
    "neighbor_boundary_integrity_missing_control",
    "replay_failure_control",
    "stress_variant_failure_control",
    "semantic_cooperation_relabel_control",
    "semantic_choice_goal_relabel_control",
    "native_support_relabel_control",
    "ant_ecology_relabel_control",
    "phase8_completion_relabel_control",
    "native_ap5_relabel_control",
    "ap5_nat4_gap_resolution_relabel_control",
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


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    home_marker = "/" + "home/"
    repo_marker = "Documents/" + "RC-github"
    return home_marker not in text and repo_marker not in text


def source_record_by_id(i1: dict[str, Any], source_id: str) -> dict[str, Any]:
    for record in i1.get("source_records", []):
        if record.get("source_id") == source_id:
            return record
    raise ValueError(f"missing I1 source record {source_id}")


def ge_ladder() -> list[dict[str, Any]]:
    return [
        {
            "rung": "GE0",
            "name": "no_source_current_generative_extractive_persistence_evidence",
            "support_allowed": False,
            "definition": "no source-current generative/extractive persistence evidence",
        },
        {
            "rung": "GE1",
            "name": "focal_persistence_trace_present",
            "support_allowed": False,
            "definition": "focal persistence trace present; environment-side effect not measured",
        },
        {
            "rung": "GE2",
            "name": "source_current_neighborhood_capacity_metrics_observed",
            "support_allowed": False,
            "definition": "focal persistence plus source-current neighborhood capacity metrics observed",
        },
        {
            "rung": "GE3",
            "name": "provisional_source_current_regime_classification_candidate",
            "support_allowed": "provisional_only",
            "definition": "provisional source-current regime classification candidate",
        },
        {
            "rung": "GE4",
            "name": "replay_control_backed_regime_separation_candidate",
            "support_allowed": "candidate_only",
            "definition": "replay/control-backed regime-separation candidate",
        },
        {
            "rung": "GE5",
            "name": "stress_variant_backed_paired_regime_separation_candidate",
            "support_allowed": "candidate_only",
            "definition": "stress/variant-backed paired-regime separation candidate",
        },
        {
            "rung": "GE6",
            "name": "n29_ready_bounded_generative_extractive_persistence_evidence",
            "support_allowed": "handoff_candidate_only",
            "definition": "N29-ready bounded generative/extractive persistence evidence with claim-clean handoff",
        },
    ]


def closeout_ladder() -> list[dict[str, Any]]:
    return [
        {"rung": "N28-C0", "definition": "initialized contract only"},
        {
            "rung": "N28-C1",
            "definition": "source inventory and generative/extractive contract admission passed",
        },
        {
            "rung": "N28-C2",
            "definition": "schema, controls, and classification policy frozen",
        },
        {"rung": "N28-C3", "definition": "active nulls fail closed"},
        {
            "rung": "N28-C4",
            "definition": "source-current generative/extractive candidate supported",
        },
        {
            "rung": "N28-C5",
            "definition": "replay/control/stress-backed generative/extractive candidate supported",
        },
        {
            "rung": "N28-C6",
            "definition": "N29-ready bounded generative/extractive closeout",
        },
    ]


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    source_records = {
        record["source_id"]: record for record in i1.get("source_records", [])
    }
    n20 = i1["n20_contract_admission"]
    n27 = i1["n27_handoff_admission"]

    source_digest_pins = {
        "source_inventory_output_digest": i1["output_digest"],
        "n20_i3_row_digest": n20["n20_i3_row_digest"],
        "n20_i4_row_digest": n20["n20_i4_row_digest"],
        "n20_i5_row_digest": n20["n20_i5_row_digest"],
        "n27_closeout_output_digest": source_record_by_id(
            i1, "n27_closeout_and_n28_handoff"
        )["output_digest"],
        "n27_side_effect_precursor_output_digest": source_record_by_id(
            i1, "n27_n28_precursor_side_effect_evaluation"
        )["output_digest"],
        "n27_side_effect_claim_classification_output_digest": source_record_by_id(
            i1, "n27_n28_precursor_claim_classification"
        )["output_digest"],
    }

    source_precedence = {
        "n20_i5_same_basin_continuation_contract": {
            "role": "normative",
            "consumption_rule": "same_basin_rule_and_minimum_control_contract",
            "row_digest": source_digest_pins["n20_i5_row_digest"],
        },
        "n20_i4_native_function_proxy_descriptor": {
            "role": "descriptor_context_only",
            "consumption_rule": "descriptor_and_proxy_boundary_not_evidence",
            "row_digest": source_digest_pins["n20_i4_row_digest"],
        },
        "n20_i3_producer_residue_ledger": {
            "role": "residue_and_naturalization_debt_context",
            "consumption_rule": "producer_residue_debt_and_blocked_relabel_boundary",
            "row_digest": source_digest_pins["n20_i3_row_digest"],
        },
        "n27_closeout": {
            "role": "bounded_ct6_precursor_context_only",
            "consumption_rule": "may_not_be_consumed_as_N28_generativity",
            "output_digest": source_digest_pins["n27_closeout_output_digest"],
        },
        "n27_side_effect_rows": {
            "role": "context_and_comparison_baseline_only",
            "consumption_rule": "metrics_context_not_N28_support",
            "output_digest": source_digest_pins[
                "n27_side_effect_precursor_output_digest"
            ],
        },
        "roadmap_handoff": {
            "role": "context_only",
            "consumption_rule": "scope_text_not_evidence",
        },
    }

    paired_regime_evidence_requirement = {
        "required_before_GE5_or_N28_C5": [
            "primary_generative_candidate",
            "alternative_generative_candidate",
            "primary_extractive_contrast",
            "alternative_extractive_contrast",
            "primary_competitive_or_neutral_contrast",
            "alternative_competitive_or_neutral_contrast",
        ],
        "single_positive_row_closeout_allowed": False,
        "contrast_rows_are_measured_regime_evidence": True,
        "extractive_or_competitive_promoted_to_generative_effect": "failed_open_blocker",
    }

    three_axis_classifier = {
        "axes": {
            "focal_persistence_axis": [
                "stable",
                "unstable",
                "missing",
            ],
            "neighborhood_capacity_axis": [
                "improves",
                "degrades",
                "neutral_or_mixed",
                "label_only",
                "missing",
            ],
            "extraction_leakage_axis": [
                "low_preserved_medium",
                "high_extraction_flattening_leakage_or_merge",
                "missing",
            ],
        },
        "rules": [
            {
                "classification": "generative",
                "requires": [
                    "focal_persistence_axis = stable",
                    "neighborhood_capacity_axis = improves",
                    "extraction_leakage_axis = low_preserved_medium",
                ],
            },
            {
                "classification": "extractive",
                "requires": [
                    "focal_persistence_axis = stable",
                    "neighborhood_capacity_axis = degrades",
                    "extraction_leakage_axis = high_extraction_flattening_leakage_or_merge",
                ],
            },
            {
                "classification": "competitive_or_neutral",
                "requires": [
                    "focal_persistence_axis = stable",
                    "neighborhood_capacity_axis = neutral_or_mixed",
                ],
            },
            {
                "classification": "blocked",
                "requires_any": [
                    "focal_persistence_axis = unstable",
                    "neighborhood_capacity_axis = label_only",
                    "missing source-current axis",
                    "post-hoc label or threshold retuning",
                ],
            },
        ],
        "policy_retuning_to_fit_label_allowed": False,
        "label_specific_thresholds_allowed": False,
        "post_hoc_boundary_shift_allowed": False,
    }

    formula_schema = {
        "focal_stability_formula": {
            "source_current_inputs": [
                "focal_basin_signature_trace",
                "focal_basin_stability_trace",
                "focal_support_coherence_floor_trace",
            ],
            "pass_condition": "focal basin remains stable above declared support/coherence floor",
        },
        "neighborhood_capacity_formula": {
            "source_current_inputs": [
                "neighbor_basin_distinguishability_trace",
                "neighbor_support_floor_trace",
                "neighbor_boundary_integrity_trace",
                "environment_basin_forming_capacity_trace",
            ],
            "pass_condition": "capacity improves by declared delta without label-only or merge/leakage substitution",
        },
        "extraction_flattening_merge_leakage_formula": {
            "source_current_inputs": [
                "focal_extraction_cost_trace",
                "extractive_flattening_trace",
                "merge_leakage_trace",
            ],
            "pass_condition": "cost, flattening, merge, and leakage remain below declared ceilings for generative rows",
            "extractive_condition": "cost, flattening, merge, or leakage explains focal persistence while neighborhood capacity degrades",
        },
        "capacity_attribution_formula": {
            "source_current_inputs": ["capacity_attribution_trace"],
            "pass_condition": "capacity change is attributed to source-current traces, not producer labels or hidden medium segmentation",
        },
    }

    classification_policy_schema = {
        "regime_labels": [
            "generative",
            "extractive",
            "competitive",
            "neutral",
            "blocked",
        ],
        "regime_evidence_roles": [
            "positive_candidate",
            "positive_candidate_alternative",
            "measured_contrast",
            "measured_contrast_alternative",
            "active_null",
            "control",
        ],
        "shared_regime_policy_status_enum": [
            "supported",
            "partially_supported",
            "split_policy_required",
            "blocked",
        ],
        "policy_divergence_record_required_fields": [
            "policy_id",
            "divergence_status",
            "affected_regimes",
            "same_policy_failed_reason",
            "split_policy_allowed",
            "post_hoc_retuning_used",
            "claim_effect",
        ],
    }

    medium_debt_and_residue_schema = {
        "medium_debt_record_required": True,
        "medium_debt_fields": i1["medium_debt_record"]["medium_debt_fields"],
        "medium_debt_as_success_allowed": False,
        "shared_medium_label_only_success_allowed": False,
        "direct_message_scaffold_as_native_medium_allowed": False,
        "producer_residue_record_required": True,
        "producer_residue_fields": n20["producer_residue_fields"],
        "producer_residue_as_substrate_carried_allowed": False,
        "capacity_attribution_trace_required": True,
        "producer_generativity_label_as_source_current_capacity_allowed": False,
    }

    artifact_roles = {
        "GE1": ["focal_basin_stability_trace"],
        "GE2": [
            "focal_basin_stability_trace",
            "neighborhood_capacity_trace",
            "extraction_leakage_trace",
        ],
        "GE3": [
            "generative_extractive_core",
            "classification_policy_trace",
            "regime_boundary_trace",
        ],
        "GE4": ["replay_trace", "control_trace", "core_digest_replay_trace"],
        "GE5": ["stress_trace", "variant_trace", "paired_regime_trace"],
        "GE6": ["closeout_trace", "N29_handoff_trace", "claim_boundary_trace"],
    }

    replay_schema = {
        "required_replay_modes_for_GE4_plus": [
            "artifact_only_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "core_digest_replay",
        ],
        "required_stress_modes_for_GE5_plus": [
            "focal_stability_stress",
            "neighbor_capacity_stress",
            "extraction_cost_stress",
            "merge_leakage_stress",
            "boundary_integrity_stress",
        ],
        "not_run_blocks_dependent_rung": True,
        "failed_open_invalidates_row": True,
    }

    ap_dependency_schema = {
        "ap4_dependency_status_enum": [
            "required_recorded",
            "not_applicable",
            "missing_blocks_row",
        ],
        "ap5_dependency_status_enum": [
            "conditional_required_recorded",
            "not_applicable",
            "missing_blocks_row",
        ],
        "not_applicable_requires_row_local_reason": True,
        "native_ap5_supported": False,
        "ap5_nat4_gap_resolution_supported": False,
        "ap4_nat4_gap_resolution_supported": False,
    }

    control_families = [
        {
            "control_id": control_id,
            "expected_result": "failed_closed_when_blocked_condition_present",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "blocks_GE3_or_stronger_unless_scope_limited_to_active_null",
        }
        for control_id in CONTROL_IDS
    ]

    generative_extractive_core_schema = {
        "object_name": "generative_extractive_core",
        "required_fields": CORE_FIELDS,
        "digest_field": "generative_extractive_core_digest",
        "canonicalization_policy": "sha256_of_canonical_json_sorted_keys_excluding_generated_timestamps_and_local_paths",
        "replay_reference_policy": "replay_control_and_stress_rows_reference_core_by_digest",
        "fail_closed_conditions": [
            "focal_survival_only",
            "neighbor_label_only",
            "neighbor_count_only",
            "transfer_success_only",
            "visual_similarity_only",
            "merge_leakage_as_support",
            "producer_attribution_without_source_current_trace",
        ],
    }

    evidence_state = {
        "positive_generative_evidence_opened": False,
        "positive_extractive_evidence_opened": False,
        "candidate_rows_classified": False,
        "ge_ladder_rung_assigned": False,
        "n28_closeout_ladder_rung_assigned": False,
        "native_support_opened": False,
        "phase8_completion_opened": False,
        "ant_ecology_opened": False,
        "ready_for_iteration_3": True,
    }

    required_sources = {
        "n20_i3": "n20_i3_generative_extractive_producer_residue_ledger",
        "n20_i4": "n20_i4_generative_extractive_native_function_proxy_contract",
        "n20_i5": "n20_i5_generative_extractive_same_basin_contract",
        "n27_closeout": "n27_closeout_and_n28_handoff",
        "n27_precursor": "n27_n28_precursor_side_effect_evaluation",
    }

    checks = [
        {
            "check_id": "i1_source_inventory_passed",
            "passed": i1.get("status") == "passed"
            and i1.get("failed_checks") == []
            and i1.get("output_digest") == EXPECTED_I1_DIGEST,
        },
        {
            "check_id": "source_precedence_frozen",
            "passed": source_precedence[
                "n20_i5_same_basin_continuation_contract"
            ]["role"]
            == "normative"
            and source_precedence["n27_side_effect_rows"]["role"]
            == "context_and_comparison_baseline_only",
        },
        {
            "check_id": "source_digest_pins_present",
            "passed": source_digest_pins["source_inventory_output_digest"]
            == EXPECTED_I1_DIGEST
            and all(source_records[source_id]["exists"] for source_id in required_sources.values())
            and source_digest_pins["n20_i3_row_digest"]
            == "2108f86e21cbf795a2ab0ef089a1f25f641c60865d97c0fb983119a4f34d50a0"
            and source_digest_pins["n20_i4_row_digest"]
            == "c08025d24b89807fc5ad245302f33ae4286ed8ad89bf7db450a94eb08c27d99b"
            and source_digest_pins["n20_i5_row_digest"]
            == "240de0c58bf066a6fb1ff610f13dbecb4f76a3f187ac08012927005de91563b7",
        },
        {
            "check_id": "ge_ladder_frozen",
            "passed": [row["rung"] for row in ge_ladder()]
            == ["GE0", "GE1", "GE2", "GE3", "GE4", "GE5", "GE6"],
        },
        {
            "check_id": "n28_closeout_ladder_frozen",
            "passed": [row["rung"] for row in closeout_ladder()]
            == ["N28-C0", "N28-C1", "N28-C2", "N28-C3", "N28-C4", "N28-C5", "N28-C6"],
        },
        {
            "check_id": "paired_regime_evidence_requirement_frozen",
            "passed": len(
                paired_regime_evidence_requirement[
                    "required_before_GE5_or_N28_C5"
                ]
            )
            == 6
            and paired_regime_evidence_requirement["single_positive_row_closeout_allowed"]
            is False,
        },
        {
            "check_id": "three_axis_classifier_frozen",
            "passed": set(three_axis_classifier["axes"].keys())
            == {
                "focal_persistence_axis",
                "neighborhood_capacity_axis",
                "extraction_leakage_axis",
            }
            and len(three_axis_classifier["rules"]) == 4,
        },
        {
            "check_id": "required_evidence_fields_present",
            "passed": len(REQUIRED_EVIDENCE_FIELDS) >= 60
            and all(
                field in REQUIRED_EVIDENCE_FIELDS
                for field in [
                    "medium_debt_record",
                    "producer_residue_record",
                    "capacity_attribution_trace",
                    "shared_regime_policy_id",
                    "shared_regime_policy_status",
                    "policy_divergence_record",
                    "generative_extractive_core",
                    "generative_extractive_core_digest",
                ]
            ),
        },
        {
            "check_id": "core_schema_and_digest_policy_frozen",
            "passed": generative_extractive_core_schema["required_fields"] == CORE_FIELDS
            and generative_extractive_core_schema["digest_field"]
            == "generative_extractive_core_digest",
        },
        {
            "check_id": "formulas_frozen",
            "passed": all(
                key in formula_schema
                for key in [
                    "focal_stability_formula",
                    "neighborhood_capacity_formula",
                    "extraction_flattening_merge_leakage_formula",
                    "capacity_attribution_formula",
                ]
            ),
        },
        {
            "check_id": "regime_policy_enums_frozen",
            "passed": set(classification_policy_schema["shared_regime_policy_status_enum"])
            == {"supported", "partially_supported", "split_policy_required", "blocked"}
            and "generative" in classification_policy_schema["regime_labels"]
            and "extractive" in classification_policy_schema["regime_labels"],
        },
        {
            "check_id": "medium_debt_and_producer_residue_frozen",
            "passed": medium_debt_and_residue_schema["medium_debt_record_required"]
            is True
            and medium_debt_and_residue_schema["producer_residue_record_required"]
            is True
            and medium_debt_and_residue_schema["medium_debt_as_success_allowed"]
            is False,
        },
        {
            "check_id": "artifact_roles_replay_ap_frozen",
            "passed": "GE6" in artifact_roles
            and "core_digest_replay" in replay_schema["required_replay_modes_for_GE4_plus"]
            and ap_dependency_schema["not_applicable_requires_row_local_reason"] is True,
        },
        {
            "check_id": "control_families_frozen",
            "passed": len(control_families) == len(CONTROL_IDS)
            and all(
                control_id in CONTROL_IDS
                for control_id in [
                    "focal_survival_only_as_generative_control",
                    "neighbor_label_only_as_capacity_control",
                    "neighbor_count_only_as_capacity_control",
                    "merge_leakage_as_support_control",
                    "extractive_flattening_masked_control",
                    "transfer_success_as_n28_success_control",
                    "missing_focal_stability_digest_control",
                    "missing_neighbor_capacity_digest_control",
                    "missing_extraction_cost_digest_control",
                    "missing_merge_leakage_digest_control",
                    "missing_capacity_attribution_digest_control",
                    "malformed_generative_extractive_core_digest_control",
                    "native_ap5_relabel_control",
                    "ap5_nat4_gap_resolution_relabel_control",
                ]
            ),
        },
        {
            "check_id": "no_positive_evidence_opened",
            "passed": all(
                evidence_state[key] is False
                for key in [
                    "positive_generative_evidence_opened",
                    "positive_extractive_evidence_opened",
                    "candidate_rows_classified",
                    "ge_ladder_rung_assigned",
                    "n28_closeout_ladder_rung_assigned",
                    "native_support_opened",
                    "phase8_completion_opened",
                    "ant_ecology_opened",
                ]
            ),
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in UNSAFE_CLAIM_FLAGS.values()),
        },
    ]

    output = {
        "artifact_id": "n28_generative_extractive_schema_and_controls",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_generative_extractive_schema_and_controls_frozen_no_positive_evidence"
        ),
        "experiment": "N28",
        "iteration": "2",
        "n28_closeout_ceiling": "N28-C2_schema_controls_and_classification_policy_frozen",
        "claim_ceiling": "schema_control_freeze_only_no_N28_positive_evidence",
        "source_inventory": {
            "path": I1_OUTPUT_PATH,
            "output_digest": i1["output_digest"],
            "source_artifact_sha256": sha256_file(I1_OUTPUT_PATH),
            "status": i1["status"],
            "acceptance_state": i1["acceptance_state"],
        },
        "source_digest_pins": source_digest_pins,
        "source_precedence": source_precedence,
        "ge_ladder": ge_ladder(),
        "n28_closeout_ladder": closeout_ladder(),
        "paired_regime_evidence_requirement": paired_regime_evidence_requirement,
        "three_axis_classifier": three_axis_classifier,
        "required_evidence_fields": REQUIRED_EVIDENCE_FIELDS,
        "generative_extractive_core_schema": generative_extractive_core_schema,
        "formula_schema": formula_schema,
        "classification_policy_schema": classification_policy_schema,
        "medium_debt_and_residue_schema": medium_debt_and_residue_schema,
        "rung_specific_artifact_roles": artifact_roles,
        "replay_schema": replay_schema,
        "ap_dependency_schema": ap_dependency_schema,
        "control_families": control_families,
        "evidence_state": evidence_state,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
    }
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(output),
        }
    )
    output["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N28 Iteration 2 - Generative / Extractive Schema And Controls",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Closeout ceiling: `{output['n28_closeout_ceiling']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- I1 digest: `{output['source_inventory']['output_digest']}`",
        f"- Positive generative evidence opened: `{str(output['evidence_state']['positive_generative_evidence_opened']).lower()}`",
        f"- GE rung assigned: `{str(output['evidence_state']['ge_ladder_rung_assigned']).lower()}`",
        f"- Ready for Iteration 3: `{str(output['evidence_state']['ready_for_iteration_3']).lower()}`",
        "",
        "I2 freezes the schema and control surface only. It defines how later rows "
        "must distinguish generative, extractive, competitive, and neutral "
        "persistence without treating N27 transfer success, medium debt, labels, "
        "or focal survival alone as N28 evidence.",
        "",
        "## Three-Axis Classifier",
        "",
        "| Axis | Allowed States |",
        "|---|---|",
    ]
    for axis, states in output["three_axis_classifier"]["axes"].items():
        lines.append(f"| `{axis}` | `{', '.join(states)}` |")

    lines.extend(
        [
            "",
            "## Source Digest Pins",
            "",
            "| Field | Digest |",
            "|---|---|",
        ]
    )
    for field, digest in output["source_digest_pins"].items():
        lines.append(f"| `{field}` | `{digest}` |")

    lines.extend(
        [
            "",
            "## Ladders",
            "",
            "| GE Rung | Definition |",
            "|---|---|",
        ]
    )
    for rung in output["ge_ladder"]:
        lines.append(f"| `{rung['rung']}` | {rung['definition']} |")

    lines.extend(
        [
            "",
            "| N28 Closeout Rung | Definition |",
            "|---|---|",
        ]
    )
    for rung in output["n28_closeout_ladder"]:
        lines.append(f"| `{rung['rung']}` | {rung['definition']} |")

    lines.extend(
        [
            "",
            "## Required Control Families",
            "",
            ", ".join(f"`{item['control_id']}`" for item in output["control_families"]),
            "",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for check in output["checks"]:
        lines.append(f"| `{check['check_id']}` | `{str(check['passed']).lower()}` |")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "All unsafe claim flags remain false. I2 assigns no GE rung and opens no "
            "positive generative/extractive evidence.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)

    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["script_sha256"] = sha256_file(SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"report_sha256", "script_sha256", "output_digest"}
        }
    )
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["report_sha256"] = sha256_file(str(REPORT.relative_to(ROOT)))
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")


if __name__ == "__main__":
    main()
