"""GRV8 contradiction, extension, and theory-reopening routing."""

from __future__ import annotations

from typing import Any


ALLOWED_CONTRADICTION_ROUTES = {
    "substrate_nonrealization",
    "candidate_graph_mapping_error",
    "core_derived_claim_too_strong",
    "core_assumption_incompatible_with_this_realization",
    "required_assumption_failed",
    "required_assumption_not_identifiable",
    "construct_not_identifiable_with_available_interventions",
    "numerical_or_instrumentation_failure",
    "source_or_specification_mismatch",
}


def contradiction_entries() -> list[dict[str, Any]]:
    entries = [
        {
            "contradiction_id": "CR-GRV8-001",
            "subject": "native_GRC9V3_readback",
            "claim_ids": ["T-RW02", "T-RW07", "T-O01"],
            "observed_result": "no_distinct_native_present_current_conditioned_read_operator_identified",
            "route": "substrate_nonrealization",
            "theory_contradicted": False,
            "evidence_refs": [
                "outputs/conductance_retention_probe.json",
                "outputs/causal_role_matrix.json",
            ],
        },
        {
            "contradiction_id": "CR-GRV8-002",
            "subject": "unique_retained_projector",
            "claim_ids": ["T-M02", "T-M04", "T-RW11"],
            "observed_result": "bounded_cluster_and_neutral_coordinate_evidence_does_not_identify_one_constitutive_retained_sector",
            "route": "construct_not_identifiable_with_available_interventions",
            "theory_contradicted": False,
            "evidence_refs": [
                "outputs/slow_cluster_registry.json",
                "outputs/conductance_retention_probe.json",
            ],
        },
        {
            "contradiction_id": "CR-GRV8-003",
            "subject": "runtime_local_Hessian_as_continuation_or_temporal_threshold",
            "claim_ids": ["T-M01", "T-C01", "T-C02"],
            "observed_result": "bounded_clamped_W_counterexamples_separate_runtime_local_diagnostics_from_analytical_continuation_and_discrete_thresholds",
            "route": "candidate_graph_mapping_error",
            "theory_contradicted": False,
            "evidence_refs": ["outputs/spatial_temporal_threshold_matrix.json"],
        },
        {
            "contradiction_id": "CR-GRV8-004",
            "subject": "transient_W_as_specific_retention_mediator",
            "claim_ids": ["T-RW05", "T-RW06", "T-RW11"],
            "observed_result": "C_dominated_neutral_persistence_and_branch_relocation_remain_rival_explanations",
            "route": "construct_not_identifiable_with_available_interventions",
            "theory_contradicted": False,
            "evidence_refs": [
                "outputs/conductance_retention_probe.json",
                "outputs/causal_role_matrix.json",
            ],
        },
        {
            "contradiction_id": "CR-GRV8-005",
            "subject": "active_stationary_or_short_period_cycle_current",
            "claim_ids": ["T-A03", "T-A04", "T-A05"],
            "observed_result": "exact_zero_is_invariant_and_authored_cycle_seeds_are_overwritten_with_no_period_2_to_8_return_found",
            "route": "substrate_nonrealization",
            "theory_contradicted": False,
            "scope_limit": "bounded_search_only_not_global_nonexistence",
            "evidence_refs": ["outputs/return_orbit_registry.json"],
        },
        {
            "contradiction_id": "CR-GRV8-006",
            "subject": "algebraic_fast_current_readback_limit",
            "claim_ids": ["T-A01"],
            "observed_result": "no_independent_current_relaxation_sector_or_native_read_operator_is_available_for_identification",
            "route": "required_assumption_not_identifiable",
            "theory_contradicted": False,
            "evidence_refs": [
                "outputs/complete_step_jacobians.json",
                "outputs/conductance_retention_probe.json",
            ],
        },
    ]
    hardening = {
        "CR-GRV8-001": {
            "assumption_statuses": {"A-PASSIVE": "not_identifiable"},
            "secondary_alternatives": ["construct_not_identifiable_with_available_interventions"],
            "rejected_routes": ["theory_contradiction", "numerical_or_instrumentation_failure"],
            "required_next_action": "keep_native_readback_blocked_and_route_operator_form_to_a_separate_target_conditioned_investigation",
        },
        "CR-GRV8-002": {
            "assumption_statuses": {"A-BRANCH": "satisfied", "A-CLOCK": "satisfied", "A-REACHABLE": "satisfied"},
            "secondary_alternatives": ["branch_relocation_or_ordinary_persistent_state"],
            "rejected_routes": ["substrate_nonrealization", "theory_contradiction"],
            "required_next_action": "retain_analysis_only_cluster_and_constructibility_routes_without_selecting_a_carrier",
        },
        "CR-GRV8-003": {
            "assumption_statuses": {"A-SMOOTH": "satisfied_within_admitted_rows", "A-MOBILITY": "satisfied"},
            "secondary_alternatives": ["core_derived_claim_too_strong"],
            "rejected_routes": ["source_or_specification_mismatch", "numerical_or_instrumentation_failure"],
            "required_next_action": "preserve_runtime_diagnostic_continuation_and_full_temporal_objects_as_distinct",
        },
        "CR-GRV8-004": {
            "assumption_statuses": {"A-REACHABLE": "mixed_synthetic_valid_and_native_continuation", "A-STATE-CLOSURE": "satisfied_within_bounded_horizon"},
            "secondary_alternatives": ["branch_relocation", "C_dominated_neutral_persistence"],
            "rejected_routes": ["theory_contradiction", "native_readback"],
            "required_next_action": "retain_GRR3_to_GRR5_unchanged_runtime_constructibility_search_before_extension_selection",
        },
        "CR-GRV8-005": {
            "assumption_statuses": {"A-CLOSED": "satisfied", "A-UNIQUENESS": "satisfied", "A-MOBILITY": "satisfied"},
            "secondary_alternatives": ["unresolved_richer_fixture_or_relative_orbit"],
            "rejected_routes": ["global_substrate_nonrealization", "theory_contradiction"],
            "required_next_action": "preserve_bounded_null_and_leave_richer_or_relative_orbits_unresolved",
        },
        "CR-GRV8-006": {
            "assumption_statuses": {"A-REGULAR-SLAVING": "not_applicable", "A-LOOP-INVERT": "not_applicable", "A-FAST-SLOW": "not_applicable", "A-PASSIVE": "not_identifiable"},
            "secondary_alternatives": ["substrate_nonrealization_of_independent_current_state"],
            "rejected_routes": ["theory_contradiction", "declared_simplifying_limit_realized"],
            "required_next_action": "classify_native_recurrence_separately_and_keep_current_temporalization_target_conditioned",
        },
    }
    for entry in entries:
        if entry["route"] not in ALLOWED_CONTRADICTION_ROUTES:
            raise ValueError(f"invalid contradiction route: {entry['route']}")
        entry.update(hardening[entry["contradiction_id"]])
        entry["evidence_excluding_rejected_routes"] = entry["evidence_refs"]
    return entries


def extension_decisions(policy: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = policy["extension_decisions"]
    if len({row["decision_id"] for row in decisions}) != len(decisions):
        raise ValueError("duplicate extension decision ID")
    return decisions


def theory_reopening_decision(policy: dict[str, Any]) -> dict[str, Any]:
    decision = policy["theory_reopening_decision"]
    if decision["route"] != "no_theory_reopening_required":
        raise ValueError("GRV8 policy unexpectedly reopens theory")
    return decision


def superseded_exploratory_claims() -> list[dict[str, Any]]:
    return [
        {
            "exploratory_claim_id": "SX-GRV3-001",
            "superseded_statement": "stored_W_and_J_are_independent_complete_step_state_coordinates",
            "source_document_or_section": "GRV3_pre_hardening_causal_state_candidate",
            "reason_superseded": "stage_reconstruction_and_omitted_field_audits_do_not_admit_W_or_J_as_independent_complete_step_coordinates",
            "disposition": "rejected_mapping",
            "replacement": "C_is_the_admitted_independent_coordinate_on_bounded_strata_while_W_and_J_are_reconstructed_or_stage_dependent",
            "source_ref": "outputs/complete_step_jacobians.json",
            "supporting_gate_artifacts": ["outputs/complete_step_jacobians.json"],
        },
        {
            "exploratory_claim_id": "SX-GRV4-001",
            "superseded_statement": "frozen_W_and_full_recurrence_are_equivalent",
            "source_document_or_section": "GRV4_pre_acceptance_agreement_wording",
            "reason_superseded": "all_primary_rows_show_no_resolved_difference_within_a_weakly_discriminating_uncertainty_envelope_not_equivalence",
            "disposition": "narrowed",
            "replacement": "no_difference_is_resolved_within_the_admitted_first_order_uncertainty_envelope",
            "source_ref": "outputs/frozen_full_comparison.json",
            "supporting_gate_artifacts": ["outputs/frozen_full_comparison.json"],
        },
        {
            "exploratory_claim_id": "SX-GRV5-001",
            "superseded_statement": "transient_W_specifically_mediates_later_C_retention",
            "source_document_or_section": "GRV5_exploratory_retention_interpretation",
            "reason_superseded": "native_mediation_count_is_zero_and_C_dominated_persistence_does_not_exclude_branch_relocation",
            "disposition": "unverified_and_narrowed",
            "replacement": "bounded_C_dominated_neutral_persistence_with_branch_relocation_rival_unresolved",
            "source_ref": "outputs/conductance_retention_probe.json",
            "supporting_gate_artifacts": ["outputs/conductance_retention_probe.json", "outputs/causal_role_matrix.json"],
        },
        {
            "exploratory_claim_id": "SX-GRV6-001",
            "superseded_statement": "nonzero_or_seeded_current_is_active_recurrent_circulation",
            "source_document_or_section": "GRV6_seeded_cycle_exploration",
            "reason_superseded": "certified_cycle_seeds_are_overwritten_and_no_resolved_candidate_returns_to_full_causal_state",
            "disposition": "rejected_within_tested_envelope",
            "replacement": "authored_cycle_seeds_are_overwritten_and_no_primitive_period_2_to_8_return_was_found_in_scope",
            "source_ref": "outputs/return_orbit_registry.json",
            "supporting_gate_artifacts": ["outputs/return_orbit_registry.json"],
        },
        {
            "exploratory_claim_id": "SX-GRV7-001",
            "superseded_statement": "runtime_spatial_and_full_temporal_non_equivalence_is_supported",
            "source_document_or_section": "GRV7_pre_correction_non_equivalence_wording",
            "reason_superseded": "decisive_counterexamples_exist_only_for_the_reduced_clamped_W_comparator_and_no_full_map_threshold_crossing_was_reached",
            "disposition": "narrowed",
            "replacement": "only_clamped_W_reduced_spatial_continuation_and_discrete_threshold_non_equivalence_is_supported",
            "source_ref": "outputs/spatial_temporal_threshold_matrix.json",
            "supporting_gate_artifacts": ["outputs/spatial_temporal_threshold_matrix.json"],
        },
        {
            "exploratory_claim_id": "SX-GRV8-001",
            "superseded_statement": "unchanged_GRC9V3_implements_the_declared_j_equals_J_C_simplifying_limit",
            "source_document_or_section": "GRV8_P8_unaccepted_equivalence_candidate",
            "reason_superseded": "one_runtime_current_variable_is_reused_but_the_implementation_does_not_declare_or_satisfy_the_passive_null_and_carrier_sensitive_reduced_read_closure",
            "disposition": "rejected_mapping",
            "replacement": "native_current_recurrence_is_exact_while_j_equals_J_C_is_only_an_analogical_candidate_mapping",
            "source_ref": "outputs/conductance_retention_probe.json",
            "supporting_gate_artifacts": ["outputs/instrumentation_validation.json", "outputs/conductance_retention_probe.json"],
        },
    ]


def main() -> None:
    print("GRV8 routing helpers are consumed by classify_claims_and_extensions.py")


if __name__ == "__main__":
    main()
