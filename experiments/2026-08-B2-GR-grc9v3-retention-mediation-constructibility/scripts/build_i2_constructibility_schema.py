"""Build the B2-GR Iteration 2 constructibility schema freeze."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from typing import Any

from b2_artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    assert_envelope_digest,
    envelope,
    finalize_receipt,
    find_absolute_paths,
    git,
    read_json,
    repo_relative,
    sha256_file,
    verify_file_manifest,
    write_json,
)


COMMAND = ".venv/bin/python experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/scripts/build_i2_constructibility_schema.py"
CONFIG_RELATIVE = "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/configs/b2_i2_constructibility_schema_contract.json"
I1_ARTIFACT_RELATIVE = "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/b2_i1_source_handoff_inventory.json"
I1_PROTECTED_RELATIVE = "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/b2_i1_protected_path_manifest.json"
I1_RECEIPT_RELATIVE = "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/gates/b2_i1_result_receipt.json"
I1_ANCHOR_RELATIVE = "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/gates/b2_i1_acceptance_anchor.json"


REQUIRED_CANDIDATE_FIELDS = (
    "candidate_id",
    "source_iteration",
    "source_current_inputs",
    "evidence_provenance_class",
    "positive_evidence_admissible",
    "rung_lane_id",
    "unchanged_runtime_identity_id",
    "runtime_unchanged",
    "artifact_manifest",
    "artifact_digest_algorithm",
    "artifact_sha256_status",
    "all_artifact_sha256_match_file_contents",
    "artifact_paths_equal_manifest_paths",
    "derived_report_only",
    "threshold_record_path",
    "threshold_record_sha256",
    "row_specific_thresholds_declared_before_use",
    "accepted_B1_branch_id",
    "source_B1_branch_id",
    "candidate_branch_id",
    "branch_family_id",
    "branch_sheet_identity",
    "branch_lineage",
    "runtime_parameter_vector",
    "evaluation_runtime_parameter_vector",
    "preparation_parameter_history",
    "topology_digest",
    "fixed_topology",
    "event_free",
    "causal_stratum_id",
    "same_causal_stratum",
    "runtime_revision",
    "runtime_config_digest",
    "seed_or_pairing_rule",
    "preparation_provenance",
    "preparation_driver_class",
    "preparation_driver_history",
    "preparation_driver_removed_at",
    "driver_carrier_overlap_status",
    "driver_authored_carrier_component",
    "runtime_generated_carrier_component",
    "formation_attribution_rule",
    "forming_intervention_status",
    "forming_intervention_exhausted",
    "sham_preparation_id",
    "sham_preparation_trace_digest",
    "sham_k0_state_digest",
    "formation_contrast_vector",
    "formation_contrast_norm",
    "formation_contrast_margin",
    "native_write_status",
    "runtime_generated_carrier_above_formation_floor",
    "full_path_cleanliness_result",
    "load_bearing_clipping",
    "load_bearing_budget_projection",
    "post_driver_k0_state_digest",
    "runtime_reached_state",
    "native_activity_history",
    "native_activity_digest",
    "carrier_definition_id",
    "carrier_class",
    "carrier_vector",
    "carrier_metric",
    "carrier_predeclared_before_candidate_search",
    "carrier_projector_id",
    "carrier_complement_rule",
    "carrier_separation_norm",
    "carrier_separation_margin",
    "carrier_state_fields",
    "carrier_state_digest",
    "carrier_lineage_id",
    "carrier_at_formation",
    "carrier_at_formation_digest",
    "carrier_at_persistence",
    "carrier_at_persistence_digest",
    "carrier_at_probe",
    "carrier_at_probe_digest",
    "carrier_alignment_across_phases",
    "carrier_transport_rule",
    "carrier_causal_eligibility_class",
    "carrier_equivalence_class_id",
    "carrier_nesting_relation",
    "carrier_overlap_measure",
    "primary_carrier_attribution",
    "branch_tangent_rule",
    "tangent_component_norm",
    "transverse_component_norm",
    "unresolved_component_norm",
    "fixed_config_nearest_branch_id",
    "fixed_config_branch_distance",
    "fixed_config_tangent_component",
    "parameter_family_tangent_component",
    "branch_relation_class",
    "branch_relocation_rejected",
    "branch_search_radius",
    "branch_search_continuation_directions",
    "branch_search_solver_seed_count",
    "branch_search_residual_threshold",
    "branch_search_coverage_fraction",
    "branch_search_boundary_coverage",
    "branch_search_condition_number",
    "branch_search_sufficiency",
    "temporal_metric",
    "temporal_operator_id",
    "temporal_operator_domain",
    "carrier_is_independent_causal_coordinate",
    "carrier_observation_map",
    "carrier_projection_of_slow_cluster",
    "slow_cluster_rule",
    "slow_mode_class",
    "slow_cluster_exists",
    "slow_cluster_occupancy_ratio",
    "formation_specific_occupancy_excess",
    "formation_specific_occupancy_margin",
    "slow_projector_reference_state",
    "slow_projector_transport_rule",
    "projector_overlap_by_horizon",
    "projector_conditioning_by_horizon",
    "slow_cluster_isolation_margin",
    "cluster_condition_number",
    "cluster_uncertainty_bound",
    "persistence_horizons",
    "persistence_ratio",
    "probe_kind",
    "probe_provenance_class",
    "probe_amplitude_sweep",
    "no_probe_baselines",
    "zero_probe_control",
    "carrier_by_probe_interaction",
    "oriented_interaction_vector",
    "interaction_vector_uncertainty",
    "interaction_margin",
    "interaction_direction_consistency",
    "interaction_linearity_status",
    "noncarrier_match_provenance",
    "noncarrier_match_norm",
    "noncarrier_match_margin",
    "noncarrier_match_residual_by_block",
    "mediation_path",
    "carrier_pre_probe_digest",
    "probe_application_stage",
    "first_stage_that_reads_candidate_carrier",
    "first_stage_that_rewrites_candidate_carrier",
    "readout_stage",
    "carrier_at_read_stage",
    "reset_result",
    "swap_result",
    "bypass_result",
    "control_results",
    "control_applicability_results",
    "control_identifiability",
    "replay_results",
    "active_null_results",
    "persistence_mechanism_class",
    "event_margin",
    "positivity_margin",
    "conductance_floor_margin",
    "budget_projection_noop",
    "validity_margin_bundle",
    "witness_validity",
    "robustness_class",
    "search_phase",
    "search_row_id",
    "search_budget_id",
    "search_stratum_id",
    "discovery_feature_record",
    "adjudication_feature_accessed_during_discovery",
    "attempt_status",
    "rejection_reason",
    "budget_consumed",
    "resolved_status",
    "symmetry_orbit_id",
    "candidate_deduplication_id",
    "duplicate_class",
    "carrier_equivalent_witness_id",
    "fresh_process_confirmation_result",
    "fresh_process_confirmation_digest",
    "maximum_GRR_rung",
    "row_decision",
    "claim_ceiling",
    "blocked_relabels",
    "primary_demotion_reason",
    "secondary_demotion_reasons",
)


BOOLEAN_FIELDS = {
    "derived_report_only",
    "positive_evidence_admissible",
    "runtime_unchanged",
    "all_artifact_sha256_match_file_contents",
    "artifact_paths_equal_manifest_paths",
    "row_specific_thresholds_declared_before_use",
    "fixed_topology",
    "event_free",
    "same_causal_stratum",
    "forming_intervention_exhausted",
    "runtime_generated_carrier_above_formation_floor",
    "load_bearing_clipping",
    "load_bearing_budget_projection",
    "carrier_predeclared_before_candidate_search",
    "carrier_is_independent_causal_coordinate",
    "branch_relocation_rejected",
    "branch_search_boundary_coverage",
    "slow_cluster_exists",
    "adjudication_feature_accessed_during_discovery",
    "budget_projection_noop",
}

NUMBER_FIELDS = {
    "carrier_separation_norm",
    "carrier_separation_margin",
    "formation_contrast_norm",
    "formation_contrast_margin",
    "carrier_overlap_measure",
    "tangent_component_norm",
    "transverse_component_norm",
    "unresolved_component_norm",
    "fixed_config_branch_distance",
    "fixed_config_tangent_component",
    "parameter_family_tangent_component",
    "branch_search_radius",
    "branch_search_solver_seed_count",
    "branch_search_residual_threshold",
    "branch_search_coverage_fraction",
    "branch_search_condition_number",
    "slow_cluster_occupancy_ratio",
    "formation_specific_occupancy_excess",
    "formation_specific_occupancy_margin",
    "slow_cluster_isolation_margin",
    "cluster_condition_number",
    "cluster_uncertainty_bound",
    "persistence_ratio",
    "interaction_margin",
    "interaction_direction_consistency",
    "noncarrier_match_norm",
    "noncarrier_match_margin",
    "event_margin",
    "positivity_margin",
    "conductance_floor_margin",
    "budget_consumed",
}

ARRAY_FIELDS = {
    "source_current_inputs",
    "artifact_manifest",
    "preparation_parameter_history",
    "preparation_driver_history",
    "formation_contrast_vector",
    "native_activity_history",
    "carrier_vector",
    "branch_search_continuation_directions",
    "carrier_state_fields",
    "projector_overlap_by_horizon",
    "projector_conditioning_by_horizon",
    "persistence_horizons",
    "probe_amplitude_sweep",
    "oriented_interaction_vector",
    "interaction_vector_uncertainty",
    "no_probe_baselines",
    "control_applicability_results",
    "replay_results",
    "active_null_results",
    "control_results",
    "blocked_relabels",
    "secondary_demotion_reasons",
}

OBJECT_FIELDS = {
    "runtime_parameter_vector",
    "evaluation_runtime_parameter_vector",
    "runtime_reached_state",
    "carrier_at_formation",
    "carrier_at_persistence",
    "carrier_at_probe",
    "carrier_alignment_across_phases",
    "carrier_projection_of_slow_cluster",
    "zero_probe_control",
    "carrier_by_probe_interaction",
    "noncarrier_match_residual_by_block",
    "mediation_path",
    "carrier_at_read_stage",
    "reset_result",
    "swap_result",
    "bypass_result",
    "control_identifiability",
    "validity_margin_bundle",
    "witness_validity",
    "fresh_process_confirmation_result",
    "discovery_feature_record",
}


ACTIVE_NULLS = (
    "finite_horizon_persistence_as_slow_cluster",
    "branch_tangent_relocation_as_retained_carrier",
    "synthetic_only_preparation_as_runtime_reached",
    "driver_authored_carrier_relabelled_as_native_write",
    "off_manifold_internal_state_as_native_carrier",
    "different_no_probe_baseline_as_mediation",
    "frozen_W_sensitivity_as_native_full_step_mediation",
    "probe_main_effect_without_carrier_probe_interaction",
    "full_noncarrier_causal_state_mismatch",
    "forming_intervention_not_exhausted",
    "reset_does_not_remove_effect",
    "swap_does_not_follow_carrier",
    "bypass_preserves_claimed_effect",
    "post_hoc_branch_selection",
    "post_hoc_threshold_selection",
    "label_only_readback",
    "retention_as_memory_or_learning",
    "failed_search_as_impossibility",
    "extension_selected_by_missing_symbol",
    "ordinary_slow_C_relaxation_relabelled_as_history_specific_carrier",
    "parameter_continuation_tangent_relabelled_as_same_configuration_branch_relocation",
    "conservation_or_gauge_mode_relabelled_as_retained_slow_cluster",
    "candidate_selected_under_one_metric_then_projector_changed_to_capture_it",
    "projector_recomputed_to_follow_candidate_across_horizons",
    "artificial_independent_W_or_J_eigensystem_relabelled_as_admitted_temporal_mode",
    "externally_maintained_difference_relabelled_as_post_input_retention",
    "regenerated_W_from_retained_C_relabelled_as_durable_W_carrier",
    "event_or_topology_change_relabelled_as_fixed_topology_retention",
    "budget_projection_or_clipping_supported_persistence",
    "probe_changes_carrier_before_the_measured_readout",
    "matched_pair_differs_in_hidden_causal_state_or_administrative_phase",
    "cross_lineage_rung_composition_relabelled_as_GRR5",
    "zero_probe_control_relabelled_as_core_passive_null",
    "synthetic_reset_or_swap_outside_constitutive_manifold_treated_as_native_control",
    "bypass_implemented_by_skipping_native_runtime_stage",
    "single_pathological_zero_margin_witness_treated_as_clean_constructibility",
    "failure_to_generalize_across_branches_relabelled_as_witness_failure",
    "no_matched_sham_as_native_formation",
    "ordinary_drift_against_original_branch_as_native_write",
    "eventful_preparation_as_clean_primary_lane",
    "search_budget_migrated_after_outcome",
    "discovery_optimized_on_future_gate_adjudication_score",
    "slow_cluster_exists_without_formation_specific_excess_occupancy",
    "overlapping_carrier_representations_as_independent_witnesses",
    "serialized_diagnostic_surface_as_causal_carrier",
    "insufficient_branch_manifold_coverage_as_relocation_rejected",
    "synthetic_internal_probe_as_native_GRR4",
    "response_norm_difference_without_oriented_interaction",
    "unrelated_state_residual_as_reset_swap_or_bypass_failure",
    "control_null_false_or_missing_collapsed_into_status",
    "budget_consumed_as_resolved_coverage",
    "distinct_histories_same_state_as_independent_retention_witnesses",
)


BLOCKED_RELABELS = (
    "core_ReadBack",
    "write_back",
    "closed_loop",
    "memory",
    "learning",
    "identity",
    "agency",
    "extension_necessity",
    "global_impossibility",
)


def field_schema() -> dict[str, dict[str, Any]]:
    schema: dict[str, dict[str, Any]] = {}
    for name in REQUIRED_CANDIDATE_FIELDS:
        if name in BOOLEAN_FIELDS:
            field_type = "boolean"
        elif name in NUMBER_FIELDS:
            field_type = "number_or_status_when_not_applicable"
        elif name in ARRAY_FIELDS:
            field_type = "array"
        elif name in OBJECT_FIELDS:
            field_type = "object"
        else:
            field_type = "string_or_closed_enum"
        schema[name] = {"required": True, "type": field_type}

    schema["artifact_manifest"].update(
        {
            "minimum_items_for_positive_row": 1,
            "item_required_fields": ["path", "sha256", "artifact_role"],
        }
    )
    schema["source_current_inputs"].update({"minimum_items_for_positive_row": 1})
    schema["unchanged_runtime_identity_id"]["positive_required_rule"] = (
        "equals_accepted_I1_unchanged_runtime_identity_id"
    )
    schema["threshold_record_path"]["positive_required_rule"] = (
        "repo_relative_existing_preexecution_record"
    )
    schema["threshold_record_sha256"]["positive_required_rule"] = (
        "matches_threshold_record_file_contents"
    )
    schema["control_results"].update(
        {
            "item_required_fields": [
                "control_id",
                "control_status",
                "blocked_condition",
                "expected_result",
                "actual_result",
                "claim_allowed_when_control_triggers",
                "rung_effect",
            ]
        }
    )
    schema["derived_report_only"]["positive_required_value"] = False
    schema["positive_evidence_admissible"]["positive_required_value"] = True
    schema["runtime_unchanged"]["positive_required_value"] = True
    schema["all_artifact_sha256_match_file_contents"]["positive_required_value"] = True
    schema["artifact_paths_equal_manifest_paths"]["positive_required_value"] = True
    schema["row_specific_thresholds_declared_before_use"]["positive_required_value"] = (
        True
    )
    schema["fixed_topology"]["primary_positive_required_value"] = True
    schema["event_free"]["primary_positive_required_value"] = True
    schema["same_causal_stratum"]["derivative_or_projector_positive_required_value"] = (
        True
    )
    schema["load_bearing_clipping"]["positive_required_value"] = False
    schema["load_bearing_budget_projection"]["positive_required_value"] = False
    schema["artifact_sha256_status"]["positive_required_value"] = "all_match"
    schema["artifact_digest_algorithm"]["required_value"] = "SHA-256"
    schema["evidence_provenance_class"]["allowed_values"] = [
        "native_runtime_reached",
        "synthetic_valid",
        "reduced_model",
        "derived_report",
    ]
    schema["preparation_provenance"]["allowed_values"] = [
        "native_spontaneous",
        "runtime_realized_from_upstream_preparation",
        "synthetic_internal_state",
    ]
    schema["native_write_status"]["allowed_values"] = [
        "native_write_supported",
        "runtime_reached_without_native_write",
        "initial_condition_only",
        "formation_not_identifiable",
        "not_run",
    ]
    schema["full_path_cleanliness_result"]["allowed_values"] = [
        "passed_clean_primary_lane",
        "eventful_history_persistence",
        "constraint_supported_history",
        "failed",
        "not_run",
    ]
    schema["carrier_class"]["allowed_values"] = [
        "C_sector",
        "W_sector",
        "joint_C_W_sector",
    ]
    schema["carrier_causal_eligibility_class"]["allowed_values"] = [
        "independent_complete_step_causal_coordinate",
        "stage_local_load_bearing_surface",
        "derived_causal_observable",
        "mixed_nested_representation",
        "diagnostic_only_surface",
        "administrative_state",
    ]
    schema["branch_search_sufficiency"]["allowed_values"] = [
        "sufficient",
        "insufficient_unresolved",
        "not_run",
    ]
    schema["slow_mode_class"]["allowed_values"] = [
        "positive_decaying",
        "negative_oscillatory_decaying",
        "complex_decaying_pair",
        "marginal",
        "unstable",
        "deadbeat",
        "defective_or_ill_conditioned",
        "nonnormal_transient",
        "not_run",
    ]
    schema["probe_provenance_class"]["allowed_values"] = [
        "native_exposed_probe",
        "runtime_realized_probe_from_upstream_input",
        "synthetic_internal_probe",
        "reduced_or_analytical_probe",
        "not_run",
    ]
    schema["duplicate_class"]["allowed_values"] = [
        "not_duplicate",
        "state_duplicate",
        "history_distinct_same_state",
        "symmetry_duplicate",
        "carrier_equivalent_duplicate",
    ]
    schema["noncarrier_match_provenance"]["allowed_values"] = [
        "naturally_matched_pair",
        "runtime_constructed_matched_pair",
        "synthetic_counterfactual_match",
        "not_run",
    ]
    schema["persistence_mechanism_class"]["allowed_values"] = [
        "passive_retention",
        "activity_maintained_retention",
        "regenerated_carrier_from_retained_state",
        "transferred_retention",
        "externally_maintained_difference",
        "not_run",
    ]
    schema["maximum_GRR_rung"]["allowed_values"] = [
        "GRR0",
        "GRR1",
        "GRR2",
        "GRR3",
        "GRR4",
        "GRR5",
        "not_assigned",
    ]
    schema["row_decision"]["allowed_values"] = [
        "positive_witness",
        "bounded_negative",
        "search_unresolved",
        "numerical_failure",
        "source_or_provenance_failure",
        "required_assumption_failed",
        "required_control_failed",
        "required_control_not_identifiable",
        "invalid_candidate",
        "duplicate_candidate",
        "outside_envelope",
    ]
    schema["blocked_relabels"]["required_rule"] = (
        "contains_every_applicable_global_and_row_local_blocked_relabel"
    )
    return schema


def load_and_validate_i1(input_revision: str) -> dict[str, Any]:
    anchor = read_json(REPO_ROOT / I1_ANCHOR_RELATIVE)
    artifact = read_json(REPO_ROOT / I1_ARTIFACT_RELATIVE)
    protected = read_json(REPO_ROOT / I1_PROTECTED_RELATIVE)
    receipt = read_json(REPO_ROOT / I1_RECEIPT_RELATIVE)
    assert_envelope_digest(artifact)
    assert_envelope_digest(protected)

    expected = {
        "acceptance_status": "accepted",
        "assigned_closeout_rung": "B2-C0",
        "ready_for_iteration_2": True,
        "B2_positive_evidence_opened": False,
        "GRR_rung_assigned": False,
    }
    for key, value in expected.items():
        if anchor.get(key) != value:
            raise ValueError(f"I1 acceptance anchor {key} mismatch")
    bindings = {
        I1_ARTIFACT_RELATIVE: anchor["result_artifact_sha256"],
        I1_PROTECTED_RELATIVE: anchor["protected_manifest_sha256"],
        I1_RECEIPT_RELATIVE: anchor["result_receipt_sha256"],
    }
    for relative, digest in bindings.items():
        if sha256_file(REPO_ROOT / relative) != digest:
            raise ValueError(f"I1 acceptance binding mismatch: {relative}")
    if artifact["payload_sha256"] != anchor["result_artifact_payload_sha256"]:
        raise ValueError("I1 artifact payload binding mismatch")
    if protected["payload_sha256"] != anchor["protected_manifest_payload_sha256"]:
        raise ValueError("I1 protected manifest payload binding mismatch")
    if receipt["receipt_payload_sha256"] != anchor["result_receipt_payload_sha256"]:
        raise ValueError("I1 receipt payload binding mismatch")
    if not verify_file_manifest(protected["payload"]):
        raise ValueError("I1 protected manifest no longer matches live protected tree")
    result_revision = anchor["result_revision"]
    git("cat-file", "-e", f"{result_revision}^{{commit}}")
    if git("merge-base", "--is-ancestor", result_revision, input_revision):
        raise AssertionError("unreachable")
    return {
        "anchor": anchor,
        "artifact": artifact,
        "protected": protected,
        "receipt": receipt,
    }


def grr_ladder(i1_payload: dict[str, Any]) -> dict[str, Any]:
    source = i1_payload["GRR_ladder_definition"]
    return {
        "source": "accepted_B1_authoritative_ladder_verbatim",
        "source_section_sha256": source["section_sha256"],
        "claim_ceiling": source["claim_ceiling"],
        "rungs": deepcopy(source["rungs"]),
        "redefined_by_B2": False,
        "cumulative_row_local_dependencies": {
            "GRR3": [
                "same_lineage_native_write_or_GRR1",
                "same_lineage_GRR2",
                "isolated_slow_cluster",
            ],
            "GRR4": ["same_lineage_GRR3", "matched_carrier_by_probe_interaction"],
            "GRR5": [
                "same_lineage_write",
                "same_lineage_GRR3",
                "same_lineage_GRR4",
                "applicable_controls",
                "required_replay",
            ],
        },
        "cross_lineage_composition_allowed": False,
    }


def rung_contracts(
    i1_payload: dict[str, Any], contract: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    inherited = i1_payload["GRR_ladder_definition"]["rungs"]
    hardening = contract["rung_admission_hardening"]
    result: dict[str, dict[str, Any]] = {}
    for rung in [f"GRR{i}" for i in range(6)]:
        result[rung] = {
            "inherited_semantic_definition": inherited[rung],
            "B2_operational_admission_criteria": deepcopy(hardening[rung]),
            "B2_redefines_inherited_meaning": False,
        }
    return result


def closeout_ladder() -> dict[str, str]:
    return {
        "B2-C0": "accepted source and unchanged-runtime admission",
        "B2-C1": "constructibility protocol and schema frozen",
        "B2-C2": "false-positive surface admitted through active nulls",
        "B2-C3": "native discovery candidate set frozen after fresh-process confirmation",
        "B2-C4": "GRR3 slow-cluster and branch-transversality classification frozen",
        "B2-C5": "GRR4 matched-probe mediation classification frozen",
        "B2-C6": "controlled classification and next-route closeout accepted",
    }


def active_null_schema() -> list[dict[str, Any]]:
    return [
        {
            "null_id": null_id,
            "required_iteration": "B2-I3",
            "required_status": "failed_closed",
            "positive_evidence_admissible": False,
            "maximum_GRR_rung": "not_assigned",
        }
        for null_id in ACTIVE_NULLS
    ]


def build_checks(payload: dict[str, Any]) -> dict[str, bool]:
    fields = payload["candidate_row_schema"]["fields"]
    carrier_ids = [row["carrier_definition_id"] for row in payload["carrier_schema"]]
    grr = payload["GRR_ladder"]["rungs"]
    closeout = payload["B2_closeout_ladder"]
    return {
        "i1_acceptance_anchor_consumed": payload["source_contract"][
            "I1_acceptance_status"
        ]
        == "accepted",
        "i1_B2_C0_consumed": payload["source_contract"]["I1_assigned_closeout_rung"]
        == "B2-C0",
        "i1_result_revision_bound": len(
            payload["source_contract"]["I1_result_revision"]
        )
        == 40,
        "i1_protected_manifest_live": payload["source_contract"][
            "protected_manifest_live_verification"
        ],
        "all_required_candidate_fields_frozen": set(REQUIRED_CANDIDATE_FIELDS)
        == set(fields),
        "all_candidate_fields_typed": all(row.get("type") for row in fields.values()),
        "artifact_manifest_fail_closed": fields["artifact_manifest"][
            "minimum_items_for_positive_row"
        ]
        == 1,
        "derived_report_only_blocks_positive": fields["derived_report_only"][
            "positive_required_value"
        ]
        is False,
        "GRR0_through_GRR5_frozen": list(grr)
        == ["GRR0", "GRR1", "GRR2", "GRR3", "GRR4", "GRR5"],
        "GRR_meanings_not_redefined": payload["GRR_ladder"]["redefined_by_B2"] is False,
        "rung_contracts_separate_meaning_from_hardening": all(
            row["inherited_semantic_definition"] == grr[rung]
            and row["B2_redefines_inherited_meaning"] is False
            and set(row["B2_operational_admission_criteria"])
            == {
                "required_predecessor_rung",
                "required_assumptions",
                "required_validity_controls",
                "optional_hardening_controls",
                "allowed_positive_wording",
                "blocked_relabels",
            }
            for rung, row in payload["GRR_rung_contracts"].items()
        ),
        "B2_C0_through_B2_C6_frozen": list(closeout) == [f"B2-C{i}" for i in range(7)],
        "ladders_separate": payload["GRR_ladder"]["rungs"]
        != payload["B2_closeout_ladder"],
        "positive_provenance_closed": payload["provenance_schema"]["positive_eligible"]
        == ["native_spontaneous", "runtime_realized_from_upstream_preparation"],
        "evidence_provenance_classes_explicit": set(
            payload["provenance_schema"]["evidence_classes"]
        )
        == {
            "native_runtime_reached",
            "synthetic_valid",
            "reduced_model",
            "derived_report",
        },
        "direct_internal_state_authorship_blocked": "synthetic_internal_state"
        in payload["provenance_schema"]["diagnostic_only"],
        "all_48_B1_branches_admitted_without_ranking": payload["search_envelope"][
            "source_branch_count"
        ]
        == 48
        and "without_ranking" in payload["search_envelope"]["source_branch_rule"],
        "discovery_row_budget_arithmetic_frozen": payload["search_envelope"][
            "discovery_row_count_breakdown"
        ]["total"]
        == payload["search_envelope"]["maximum_discovery_rows"]
        == 9648,
        "search_allocation_stratified_and_nonmigrating": sum(
            row["allocated_attempts"]
            for row in payload["search_envelope"]["stratified_allocation"]
        )
        == 9648
        and payload["search_envelope"][
            "budget_migration_between_strata_after_outcome_allowed"
        ]
        is False,
        "primary_grid_has_no_success_based_early_stop": payload["search_envelope"][
            "early_stopping_after_confirmed_witness_allowed"
        ]
        is False,
        "discovery_excludes_future_gate_scores": not set(
            payload["search_envelope"]["discovery_feature_whitelist"]
        ).intersection(
            payload["search_envelope"]["future_gate_adjudication_feature_blacklist"]
        ),
        "attempt_ledger_separates_budget_from_resolution": payload[
            "search_attempt_ledger_schema"
        ]["every_attempt_serialized"]
        and payload["search_attempt_ledger_schema"][
            "budget_consumed_true_implies_resolved"
        ]
        is False,
        "primary_lane_fixed_topology_event_free": payload["primary_lane"][
            "fixed_topology"
        ]
        and payload["primary_lane"]["event_free"],
        "primary_lane_cleanliness_covers_full_ancestry": payload["primary_lane"][
            "cleanliness_interval"
        ][0]
        == "accepted_source_branch"
        and payload["primary_lane"]["cleanliness_interval"][-1]
        == "required_control_windows",
        "native_formation_requires_matched_sham": payload["formation_schema"][
            "matched_sham_required"
        ]
        and payload["formation_schema"][
            "original_source_snapshot_is_not_automatic_sham"
        ],
        "same_configuration_separate_from_parameter_tangent": payload[
            "branch_relation_schema"
        ]["parameter_continuation_tangent_recorded_separately"],
        "branch_relocation_requires_sufficient_manifold_coverage": payload[
            "branch_relation_schema"
        ]["failed_bounded_search_implies_no_branch"]
        is False
        and payload["branch_relation_schema"]["minimum_resolved_seed_fraction"] == 0.95,
        "carrier_set_finite": carrier_ids
        == ["C_ZERO_SUM_V1", "W_EDGE_CONDUCTANCE_OBSERVATION_V1", "JOINT_C_W_BLOCK_V1"],
        "no_open_ended_other_carrier": len(carrier_ids) == 3
        and not any("OTHER" in item for item in carrier_ids),
        "W_not_independent_temporal_state": payload["carrier_schema"][1][
            "independent_causal_coordinate"
        ]
        is False,
        "carrier_eligibility_and_equivalence_frozen": all(
            "causal_eligibility_class" in row
            and "carrier_equivalence_class_id" in row
            and "primary_carrier_attribution_rule" in row
            and "inherited_GRR_effect_requirement" in row
            for row in payload["carrier_schema"]
        )
        and payload["carrier_equivalence_schema"][
            "same_equivalence_class_counts_as_independent_replication"
        ]
        is False,
        "slow_mode_and_formation_occupancy_split_frozen": set(
            payload["slow_mode_schema"]["classes"]
        )
        == {
            "positive_decaying",
            "negative_oscillatory_decaying",
            "complex_decaying_pair",
            "marginal",
            "unstable",
            "deadbeat",
            "defective_or_ill_conditioned",
            "nonnormal_transient",
        }
        and payload["slow_mode_schema"]["GRR3_requires"][-1]
        == "formation_specific_excess_occupancy_above_calibrated_floor",
        "temporal_operator_is_admitted_complete_step_C": payload[
            "temporal_operator_schema"
        ]["domain"].startswith("fixed_total_zero_sum_C"),
        "projector_cannot_follow_candidate": payload["temporal_operator_schema"][
            "projector_recomputation_to_follow_candidate_allowed"
        ]
        is False,
        "driver_carrier_overlap_fails_closed": all(
            "driver_carrier_overlap_effect" in row for row in payload["carrier_schema"]
        ),
        "carrier_lineage_is_cumulative": payload["carrier_lineage_schema"][
            "cross_row_or_lane_rung_composition_allowed"
        ]
        is False,
        "matched_probe_is_difference_in_differences": payload["probe_schema"][
            "difference_in_differences_required"
        ],
        "zero_probe_not_core_passive_null": payload["probe_schema"][
            "zero_probe_is_core_passive_null"
        ]
        is False,
        "full_noncarrier_state_matching_frozen": len(
            payload["probe_schema"]["full_noncarrier_state_blocks"]
        )
        >= 10,
        "read_before_rewrite_required": payload["probe_schema"][
            "read_before_rewrite_required"
        ],
        "synthetic_internal_probe_cannot_open_native_GRR4": payload["probe_schema"][
            "probe_provenance_classes"
        ]["synthetic_internal_probe"]
        == "diagnostic_only_not_native_GRR4"
        and payload["probe_schema"]["probe_classes"][1]["native_full_step_allowed"]
        is False,
        "oriented_GRR4_interaction_precedes_norm_reduction": payload["probe_schema"][
            "GRR4_effect_statistic"
        ]["orientation_must_be_tested_before_norm_reduction"],
        "reduced_frozen_W_is_diagnostic": "reduced_frozen_W_diagnostic"
        in payload["probe_schema"]["lanes"],
        "control_statuses_closed": set(payload["control_statuses"])
        == {
            "passed",
            "failed",
            "failed_closed",
            "failed_open",
            "not_run",
            "not_identifiable",
            "not_applicable_with_reason",
        },
        "bypass_does_not_silently_strengthen_GRR5": "specific_mediation_claim_only"
        in payload["control_applicability_schema"]["all_carriers"]["bypass"],
        "control_expected_effects_and_truth_table_frozen": set(
            payload["control_expected_effects"]
        )
        == {"reset", "swap", "bypass"}
        and payload["control_truth_table"]["null_false_or_missing_alias_allowed"]
        is False,
        "persistence_classes_frozen": len(payload["persistence_classes"]) == 5,
        "external_maintenance_separate": payload["persistence_classes"][-1]
        == "externally_maintained_difference",
        "result_statuses_closed": len(payload["result_statuses"]) == 11,
        "witness_and_robustness_separate": payload["validity_and_robustness_schema"][
            "robustness_failure_invalidates_clean_witness"
        ]
        is False,
        "all_required_active_nulls_frozen": len(payload["active_null_schema"])
        == len(ACTIVE_NULLS),
        "all_active_nulls_fail_closed": all(
            row["required_status"] == "failed_closed"
            for row in payload["active_null_schema"]
        ),
        "thresholds_predeclared": payload["threshold_schema"][
            "declared_before_positive_search"
        ],
        "I3_calibration_recipes_frozen_with_maxima": len(
            payload["threshold_schema"]["calibration_recipes"]
        )
        == 4
        and all(
            row["maximum_permitted_threshold"] > 0
            and row["rounding_rule"] == "round_up_to_12_decimal_places"
            for row in payload["threshold_schema"]["calibration_recipes"]
        )
        and payload["threshold_schema"]["I3_may_change_recipe_after_results"] is False,
        "row_threshold_artifact_fields_explicit": all(
            name in fields
            for name in [
                "threshold_record_path",
                "threshold_record_sha256",
                "row_specific_thresholds_declared_before_use",
            ]
        ),
        "zero_margin_blocked": payload["threshold_schema"][
            "zero_margin_witness_allowed"
        ]
        is False,
        "replay_modes_all_required": payload["replay_schema"]["required_modes"]
        == [
            "artifact_replay",
            "snapshot_load_replay",
            "duplicate_replay",
            "fresh_process_replay",
        ],
        "duplicate_classes_frozen": payload["duplicate_policy"]["classes"]
        == [
            "not_duplicate",
            "state_duplicate",
            "history_distinct_same_state",
            "symmetry_duplicate",
            "carrier_equivalent_duplicate",
        ],
        "artifact_roles_closed": len(
            payload["artifact_admissibility_schema"]["allowed_artifact_roles"]
        )
        == 13,
        "demotion_precedence_frozen": set(payload["demotion_precedence"])
        == set(payload["result_statuses"])
        and payload["demotion_precedence"][-1] == "positive_witness",
        "extension_selection_deferred": payload["extension_selection_schema"][
            "selection_before_iteration_8_allowed"
        ]
        is False,
        "no_positive_evidence_opened": payload["claim_boundary"][
            "B2_positive_evidence_opened"
        ]
        is False,
        "no_GRR_rung_assigned": payload["claim_boundary"]["GRR_rung_assigned"] is False,
        "B2_C1_only_ready": payload["claim_boundary"]["B2_closeout_ceiling"]
        == "B2-C1-ready"
        and payload["claim_boundary"]["B2_closeout_rung_assigned"] is False,
        "unsafe_claims_blocked": all(
            not value for value in payload["unsafe_claim_flags"].values()
        ),
        "no_absolute_paths": find_absolute_paths(payload) == [],
    }


def build_payload(input_revision: str) -> dict[str, Any]:
    contract = read_json(REPO_ROOT / CONFIG_RELATIVE)
    source = load_and_validate_i1(input_revision)
    i1_payload = source["artifact"]["payload"]
    oriented_edge_count = sum(
        2 * len(row["edge_order"]) for row in i1_payload["B1_branch_crosswalk"]["rows"]
    )
    expected_oriented_edge_count = contract["search_envelope"][
        "discovery_row_count_breakdown"
    ]["source_total_oriented_edge_count"]
    if oriented_edge_count != expected_oriented_edge_count:
        raise ValueError("I2 search-envelope oriented-edge count does not match I1")
    source_strata: dict[str, dict[str, int]] = {}
    for row in i1_payload["B1_branch_crosswalk"]["rows"]:
        fixture_id = row["fixture_id"]
        stratum = source_strata.setdefault(
            fixture_id, {"branch_count": 0, "oriented_edge_count": 0}
        )
        stratum["branch_count"] += 1
        stratum["oriented_edge_count"] += 2 * len(row["edge_order"])
    configured_strata = {
        row["stratum_id"].split("_", 1)[0]: {
            "branch_count": row["branch_count"],
            "oriented_edge_count": row["oriented_edge_count"],
        }
        for row in contract["search_envelope"]["stratified_allocation"]
    }
    if source_strata != configured_strata:
        raise ValueError("I2 stratified search allocation does not match I1 branches")
    if contract["search_envelope"]["carrier_adjudication_slots"] != contract[
        "search_envelope"
    ]["maximum_discovery_rows"] * len(contract["carrier_definitions"]):
        raise ValueError("I2 carrier adjudication-slot arithmetic mismatch")
    carrier_schema = deepcopy(contract["carrier_definitions"])
    for row in carrier_schema:
        row["driver_carrier_overlap_effect"] = row.pop("direct_C_driver_overlap_effect")

    payload: dict[str, Any] = {
        "gate_id": "B2-I2",
        "status": "passed",
        "acceptance_state": "awaiting_scientific_review",
        "schema_instantiation_only": True,
        "contract_schema_version": contract["schema_version"],
        "supersession": deepcopy(contract["supersession"]),
        "source_contract": {
            "I1_acceptance_anchor_path": I1_ANCHOR_RELATIVE,
            "I1_acceptance_anchor_sha256": sha256_file(REPO_ROOT / I1_ANCHOR_RELATIVE),
            "I1_acceptance_status": source["anchor"]["acceptance_status"],
            "I1_assigned_closeout_rung": source["anchor"]["assigned_closeout_rung"],
            "I1_result_revision": source["anchor"]["result_revision"],
            "I1_result_payload_sha256": source["artifact"]["payload_sha256"],
            "I1_receipt_payload_sha256": source["receipt"]["receipt_payload_sha256"],
            "unchanged_runtime_identity_id": i1_payload["unchanged_runtime_identity"][
                "identity_id"
            ],
            "unchanged_runtime_tree_sha256": i1_payload["unchanged_runtime_identity"][
                "runtime_tree_sha256"
            ],
            "accepted_B1_branch_population_count": i1_payload["B1_branch_crosswalk"][
                "accepted_B1_branch_population_count"
            ],
            "accepted_B1_branch_population_digest": i1_payload["B1_branch_crosswalk"][
                "accepted_B1_branch_population_digest"
            ],
            "protected_manifest_live_verification": verify_file_manifest(
                source["protected"]["payload"]
            ),
        },
        "candidate_row_schema": {
            "additional_fields_allowed": True,
            "additional_fields_may_relax_frozen_gate": False,
            "required_field_count": len(REQUIRED_CANDIDATE_FIELDS),
            "fields": field_schema(),
        },
        "GRR_ladder": grr_ladder(i1_payload),
        "GRR_rung_contracts": rung_contracts(i1_payload, contract),
        "B2_closeout_ladder": closeout_ladder(),
        "provenance_schema": deepcopy(contract["provenance_classes"]),
        "primary_lane": deepcopy(contract["primary_lane"]),
        "formation_schema": deepcopy(contract["formation_contract"]),
        "search_envelope": deepcopy(contract["search_envelope"]),
        "threshold_schema": deepcopy(contract["thresholds"]),
        "carrier_schema": carrier_schema,
        "carrier_equivalence_schema": deepcopy(contract["carrier_equivalence"]),
        "slow_mode_schema": deepcopy(contract["slow_mode_taxonomy"]),
        "carrier_lineage_schema": {
            "required_phases": [
                "runtime_written",
                "persistent",
                "probed",
                "controlled",
            ],
            "same_carrier_lineage_id_required": True,
            "declared_transport_or_observation_map_allowed": True,
            "cross_row_or_lane_rung_composition_allowed": False,
            "mediation_without_GRR3_role": "causal_role_diagnostic_only",
            "persistence_without_mediation_role": "lower_rung_retention_result_only",
        },
        "temporal_operator_schema": deepcopy(contract["temporal_operator"]),
        "branch_relation_schema": deepcopy(contract["branch_relation"]),
        "probe_schema": deepcopy(contract["probe_contract"]),
        "control_statuses": deepcopy(contract["control_statuses"]),
        "control_status_meanings": {
            "passed": "required control executed and its acceptance condition passed",
            "failed": "required positive-row control executed and its expected-effect condition failed",
            "failed_closed": "false-positive condition triggered and the dependent claim was correctly rejected",
            "failed_open": "blocker triggered but the dependent claim remained admitted; candidate invalid",
            "not_run": "required control absent; dependent rung blocked",
            "not_identifiable": "structurally valid control cannot be constructed; dependent rung blocked without mechanism-failure inference",
            "not_applicable_with_reason": "outside frozen control scope with reason and affected-rung record",
        },
        "control_applicability_schema": deepcopy(contract["control_applicability"]),
        "control_expected_effects": deepcopy(contract["control_expected_effects"]),
        "control_truth_table": deepcopy(contract["control_truth_table"]),
        "persistence_classes": deepcopy(contract["persistence_classes"]),
        "persistence_qualification": {
            "passive_retention": "eligible_for_GRR2_or_stronger",
            "activity_maintained_retention": "eligible_if_maintenance_is_native_and_forming_driver_is_exhausted",
            "regenerated_carrier_from_retained_state": "eligible_only_on_the_actual_retained_carrier_lineage_not_as_durable_regenerated_surface",
            "transferred_retention": "separate_mechanism_requires_lineage_and_budget_accounting",
            "externally_maintained_difference": "blocks_post_input_GRR2_or_stronger",
        },
        "result_statuses": deepcopy(contract["result_statuses"]),
        "search_attempt_ledger_schema": deepcopy(contract["search_attempt_ledger"]),
        "duplicate_policy": deepcopy(contract["duplicate_policy"]),
        "validity_and_robustness_schema": {
            "witness_validity_gates": [
                "artifact_admissibility",
                "runtime_reachability",
                "forming_driver_exhaustion",
                "fixed_topology_event_free_same_stratum",
                "numerical_resolution",
                "positive_admissibility_margins",
                "branch_relation",
                "carrier_lineage",
                "required_replay",
                "applicable_causal_controls",
            ],
            "robustness_characterization_gates": [
                "other_branch_families",
                "symmetry_partners",
                "substantially_different_amplitudes",
                "wider_horizons",
                "parameter_neighborhoods",
            ],
            "robustness_failure_invalidates_clean_witness": False,
            "robustness_failure_effect": "bounds_prevalence_or_generalization_only",
        },
        "active_null_schema": active_null_schema(),
        "replay_schema": {
            "required_modes": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "fresh_process_replay",
            ],
            "all_required_modes_must_pass": True,
            "duplicate_replay_meaning": "second_consumption_is_idempotent_and_does_not_duplicate_effect",
            "not_run_effect": "blocks_dependent_rung",
            "failed_open_effect": "invalidates_candidate_claim",
        },
        "artifact_admissibility_schema": {
            "allowed_artifact_roles": deepcopy(contract["artifact_roles"]),
            "positive_row_manifest_nonempty": True,
            "repo_relative_paths_required": True,
            "sha256_algorithm": "SHA-256",
            "all_digests_must_match": True,
            "missing_artifact_blocks_dependent_rung": True,
            "derived_report_only_blocks_positive_support": True,
        },
        "demotion_precedence": deepcopy(contract["demotion_precedence"]),
        "demotion_recording_rule": {
            "exactly_one_primary_status_required": True,
            "all_other_applicable_reasons_retained_as_secondary": True,
            "primary_precedence_source": "config.demotion_precedence",
        },
        "empty_path_semantics": {
            "zero_I4_runtime_reached_candidates": "I5_to_I7_positive_lanes_not_applicable_then_bounded_closeout",
            "zero_I5_GRR3_rows": "I6_diagnostics_may_run_but_GRR4_cannot_open",
            "zero_I6_GRR4_rows": "I7_may_harden_lower_rungs_but_GRR5_cannot_open",
        },
        "extension_selection_schema": deepcopy(contract["extension_selection"]),
        "claim_boundary": {
            "B2_positive_evidence_opened": False,
            "candidate_rows_classified": False,
            "scientific_transition_executed": False,
            "GRR_rung_assigned": False,
            "B2_closeout_rung_assigned": False,
            "B2_closeout_ceiling": "B2-C1-ready",
            "ready_for_iteration_3_after_acceptance": True,
        },
        "unsafe_claim_flags": {name: False for name in BLOCKED_RELABELS},
    }
    checks = build_checks(payload)
    payload["checks"] = checks
    payload["check_count"] = len(checks)
    payload["passed_check_count"] = sum(checks.values())
    payload["failed_checks"] = [name for name, passed in checks.items() if not passed]
    payload["status"] = "passed" if not payload["failed_checks"] else "blocked"
    return payload


def render_report(artifact: dict[str, Any]) -> str:
    payload = artifact["payload"]
    carrier_ids = ", ".join(
        row["carrier_definition_id"] for row in payload["carrier_schema"]
    )
    lines = [
        "# B2-GR Iteration 2 - Constructibility Schema Freeze",
        "",
        "## Result",
        "",
        "```text",
        f"status = {payload['status']}",
        f"acceptance_state = {payload['acceptance_state']}",
        f"checks = {payload['passed_check_count']}/{payload['check_count']} passed",
        f"failed_checks = {payload['failed_checks']}",
        f"candidate_required_field_count = {payload['candidate_row_schema']['required_field_count']}",
        f"carrier_definition_count = {len(payload['carrier_schema'])}",
        f"active_null_count = {len(payload['active_null_schema'])}",
        f"supersedes_result_revision = {payload['supersession']['supersedes_result_revision']}",
        "B2_positive_evidence_opened = false",
        "GRR_rung_assigned = false",
        "B2_closeout_ceiling = B2-C1-ready",
        "```",
        "",
        "## Frozen Scientific Surface",
        "",
        f"The finite carrier set is `{carrier_ids}`. `W` is an observation/lift of the admitted complete-step zero-sum `C` operator, not an independently invented temporal coordinate. There is no post-I2 `other` carrier escape hatch.",
        "",
        "The primary lane is fixed-topology, event-free, same-stratum unchanged GRC9V3. All 48 accepted B1 branches remain in the deterministic search envelope without branch ranking or symmetry reduction.",
        "",
        "Native formation is a carrier-projected positive-versus-matched-sham contrast. The sham has the same source branch, native-step timing, evaluation configuration, and causal administrative/RNG state. A directly authored carrier component cannot earn native-write or retention credit. The fixed-topology, event-free, no-load-bearing-constraint requirement covers the complete path from source branch through preparation, persistence, probe, and controls.",
        "",
        "The 9,648-row deterministic primary grid is allocated before outcomes across F1, F2, and F3 as 1,936, 1,936, and 5,776 attempts. Budget cannot migrate after outcomes, success cannot stop the primary grid early, every attempt remains in the ledger, and consumed budget is reported separately from resolved coverage.",
        "",
        "## Retention And Mediation",
        "",
        "Slow-cluster evidence is defined only on the admitted complete-step `C` causal operator with a fixed-reference projector. GRR3 requires an eligible slow cluster, candidate occupancy, and formation-specific excess occupancy over sham/null. Positive, negative oscillatory, complex-plane, marginal, unstable, deadbeat, defective, and nonnormal cases have distinct frozen classifications.",
        "",
        "`C`, `W`, and joint `C-W` are finite preregistered representations with explicit causal eligibility, nesting, overlap, and primary-attribution rules. Equivalent or symmetry-related representations do not create independent witnesses. `W` remains a stage-local load-bearing observation/lift rather than an independently invented complete-step coordinate.",
        "",
        "GRR4 requires a signed, oriented carrier-by-probe difference-in-differences vector before norm reduction, a zero-probe baseline, complete non-carrier state matching, positive carrier separation, and proof that the retained carrier is read before the probe rewrites it. Direct internal `C` or old-`J` probes are diagnostic-only; only native-exposed or runtime-realized upstream probes can open native GRR4. The zero-probe control is not the stronger core Read-Back passive-null condition.",
        "",
        "## Controls And Claims",
        "",
        "Artifact, snapshot/load, duplicate, and fresh-process replay are all required. Reset targets the carrier contrast/interaction, swap asks whether the interaction follows the carrier, and bypass targets only the claimed mediator-dependent interaction. Their truth table distinguishes pass, fail-closed, fail-open, not-run, not-identifiable, and scoped not-applicable states. These B2 controls harden admission without redefining inherited GRR5.",
        "",
        "I3 must instantiate four preregistered calibration recipes without changing their formulas. A missing null population or a value above its frozen maximum blocks I4 and requires a revised, reaccepted I2.",
        "",
        "Iteration 2 freezes protocol only. It assigns no GRR rung, opens no candidate evidence, selects no extension, and leaves core Read-Back, write-back, loop, memory, learning, identity, and agency blocked.",
        "",
        "## Decision",
        "",
        "The schema is mechanically complete and ready for scientific review. Human acceptance may assign `B2-C1` and open Iteration 3 active nulls.",
        "",
        f"Artifact payload SHA-256: `{artifact['payload_sha256']}`",
        "",
    ]
    return "\n".join(lines)


def execute(output_root: Path, report_root: Path) -> dict[str, Any]:
    if git("status", "--porcelain"):
        raise RuntimeError("B2 I2 requires a clean committed execution package")
    input_revision = git("rev-parse", "HEAD")
    payload = build_payload(input_revision)
    payload["input_execution_revision"] = input_revision
    payload["generating_script_path"] = repo_relative(Path(__file__))
    payload["generating_script_sha256"] = sha256_file(Path(__file__))
    payload["config_path"] = CONFIG_RELATIVE
    payload["config_sha256"] = sha256_file(REPO_ROOT / CONFIG_RELATIVE)
    artifact = envelope(payload, "b2_i2_constructibility_schema_v2", COMMAND)

    artifact_path = output_root / "b2_i2_constructibility_schema.json"
    report_path = report_root / "b2_i2_constructibility_schema.md"
    write_json(artifact_path, artifact)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(artifact), encoding="utf-8")

    receipt = finalize_receipt(
        {
            "gate_id": "B2-I2",
            "input_execution_revision": input_revision,
            "generating_script_path": repo_relative(Path(__file__)),
            "generating_script_sha256": sha256_file(Path(__file__)),
            "config_path": CONFIG_RELATIVE,
            "config_sha256": sha256_file(REPO_ROOT / CONFIG_RELATIVE),
            "prerequisite_result_receipt_digests": [
                {
                    "path": I1_RECEIPT_RELATIVE,
                    "sha256": sha256_file(REPO_ROOT / I1_RECEIPT_RELATIVE),
                    "receipt_payload_sha256": read_json(
                        REPO_ROOT / I1_RECEIPT_RELATIVE
                    )["receipt_payload_sha256"],
                }
            ],
            "prerequisite_acceptance_anchors": [
                {
                    "path": I1_ANCHOR_RELATIVE,
                    "sha256": sha256_file(REPO_ROOT / I1_ANCHOR_RELATIVE),
                    "acceptance_status": "accepted",
                    "assigned_closeout_rung": "B2-C0",
                    "result_revision": read_json(REPO_ROOT / I1_ANCHOR_RELATIVE)[
                        "result_revision"
                    ],
                }
            ],
            "output_artifact_digests": {
                repo_relative(artifact_path): sha256_file(artifact_path),
                repo_relative(report_path): sha256_file(report_path),
            },
            "output_payload_sha256": artifact["payload_sha256"],
            "supersession": deepcopy(payload["supersession"]),
            "status": "awaiting_scientific_review"
            if payload["status"] == "passed"
            else "blocked",
            "blocked_gates": ["B2-I3", "B2-I4", "B2-I5", "B2-I6", "B2-I7", "B2-I8"],
            "claim_ceiling": "B2-C1-ready_schema_only_no_positive_constructibility_evidence",
        }
    )
    receipt_path = output_root / "gates/b2_i2_result_receipt.json"
    write_json(receipt_path, receipt)
    return {"artifact": artifact, "receipt": receipt}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=EXPERIMENT_ROOT / "outputs")
    parser.add_argument("--report-root", type=Path, default=EXPERIMENT_ROOT / "reports")
    args = parser.parse_args()
    execute(args.output_root, args.report_root)


if __name__ == "__main__":
    main()
