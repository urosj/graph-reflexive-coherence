#!/usr/bin/env python3
"""Build the GRC9V4 D10 claim-topology synthesis artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "implementation/investigations/grc9v4-constitutive-design"
DECISIONS = BASE / "decisions"


def canonical_digest(data: dict[str, Any], digest_field: str) -> str:
    payload = {key: value for key, value in data.items() if key != digest_field}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict[str, Any], digest_field: str) -> None:
    data[digest_field] = canonical_digest(data, digest_field)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n")


def accepted_sources() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(DECISIONS.glob("*.json")):
        if path.name.startswith("D10"):
            continue
        data = json.loads(path.read_text())
        if data.get("status") not in {"accepted", "accepted_bounded"}:
            continue
        record_id = data.get("record_id") or data.get("artifact_id")
        digest_field = (
            "decision_record_digest"
            if "decision_record_digest" in data
            else "artifact_digest"
        )
        stored_digest = data[digest_field]
        computed_digest = canonical_digest(data, digest_field)
        if stored_digest != computed_digest:
            raise ValueError(f"noncanonical accepted source: {path}")
        rows.append(
            {
                "source_id": record_id,
                "source_kind": "accepted_decision_or_support_record",
                "path": path.relative_to(ROOT).as_posix(),
                "source_digest": stored_digest,
                "file_sha256": file_sha(path),
                "consumed_as": "accepted_claim_debt_and_architecture_lineage",
            }
        )
    return rows


def claim(
    claim_id: str,
    claim_class: str,
    statement: str,
    evidence_refs: list[str],
    bearing_debt_ids: list[str],
    normative_effect: str,
    blocked_relabels: list[str],
    activation_condition: str = "always",
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim_class": claim_class,
        "statement": statement,
        "evidence_refs": evidence_refs,
        "bearing_debt_ids": bearing_debt_ids,
        "activation_condition": activation_condition,
        "normative_effect": normative_effect,
        "blocked_relabels": blocked_relabels,
    }


def historical_claim_id(debt_id: str) -> str:
    return f"D10-HCL-{debt_id}"


CLAIMS = [
    claim(
        "D10-CL-N-001",
        "normative",
        "GRC9V4_is_a_profile_explicit_architecture_with_one_common_resource_state_authority_current_geometry_lifecycle_interface_and_invariant_contract_while_constitutive_current_and_geometry_laws_are_supplied_by_the_selected_profile",
        ["GRC9V4-CD-D7G-v2", "GRC9V4-GTRS-COMP-v1", "GRC9V4-CD-D9-v1"],
        [
            "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION",
            "GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS",
            "D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER",
        ],
        "the_spec_must_define_the_common_interface_and_invariant_contract_and_require_an_explicit_complete_profile_identity_without_flattening_A_C_or_selecting_one_candidate_or_realization_as_universally_preferred",
        [
            "unique_candidate_selected",
            "unique_realization_selected",
            "design_constructibility_is_architecture_superiority",
        ],
    ),
    claim(
        "D10-CL-N-002",
        "normative",
        "C_is_the_only_resource_coordinate_and_each_enabled_profile_declares_its_authoritative_nonresource_state_while_T_C_h_J_solver_and_analysis_surfaces_remain_derived_or_transient",
        ["GRC9V4-CD-D1-v1", "GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D9-v1"],
        ["D7-DEBT-A-CORE-STATUS", "D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER"],
        "the_spec_must_publish_state_authority_per_profile_and_must_not_promote_derived_Candidate_C_or_solver_state",
        [
            "Candidate_C_T_C_is_authoritative",
            "solver_cache_is_state",
            "B_is_present_without_U_B",
        ],
    ),
    claim(
        "D10-CL-N-003",
        "normative",
        "every_profile_uses_a_declared_complete_step_with_one_authoritative_current_one_continuity_write_postcontinuity_refresh_atomic_failure_and_no_hidden_same_beat_authority",
        ["GRC9V4-CD-D6V2-v1", "GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D9-v1"],
        [
            "GTRS-CI-DEBT-A-NONZERO-CHAIN-WITNESS",
            "GTRS-CI-DEBT-C-NONZERO-CHAIN-WITNESS",
            "D7-DEBT-FORMED-BRANCH-RUNTIME",
        ],
        "the_spec_must_freeze_order_atomicity_and_authority_but_must_not_call_the_unexecuted_endpoint_effect_empirically_verified",
        [
            "formal_consumer_is_executed_endpoint_witness",
            "failed_substage_partially_commits",
        ],
    ),
    claim(
        "D10-CL-N-004",
        "normative",
        "complete_step_charge_budget_and_tangent_are_derived_from_the_actual_resource_write_path_with_typed_external_and_event_receipts",
        ["GRC9V4-CD-D8B-CI-v1", "GRC9V4-CD-D9-v1"],
        [],
        "the_spec_must_define_Q_varpi_Q_target_the_charge_tangent_and_identity_budget_stage_before_final_C_consumers",
        [
            "nonresource_state_is_charge",
            "budget_repair_after_writers",
            "impulse_is_zero_duration_beat",
        ],
    ),
    claim(
        "D10-CL-N-005",
        "normative",
        "lifecycle_identity_contains_current_state_reset_baseline_and_Q_target_while_typed_event_and_migration_receipts_bind_ordered_source_and_target_complete_profile_identities_and_transform_the_whole_tuple_before_atomic_commit",
        ["GRC9V4-CD-D9-v1"],
        ["D5V2-DEBT-CURRENT-SINGULAR-SUCCESSOR"],
        "the_spec_must_encode_typed_lossy_continuation_and_fail_closed_outside_admitted_regular_or_event_profiles",
        [
            "reset_resurrects_old_graph",
            "untyped_topology_event",
            "regular_profile_crosses_singularity",
        ],
    ),
    claim(
        "D10-CL-N-006",
        "normative",
        "K4_and_graph_Hodge_objects_use_the_corrected_form_space_typing_reference_pairing_covariance_and_typed_event_transport_contract",
        [
            "GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1",
            "GRC9V4-CD-D8A-v1",
            "GRC9V4-CD-D9-v1",
        ],
        [
            "D8A-DEBT-HODGE-CORRECTION-NORMATIVE-ENCODING",
            "D8A-DEBT-C-NONIDENTITY-FLAT-SHARP-WITNESS",
            "D7GV2-DEBT-METRIC-INVERSE-SOLVER-AND-COVARIANCE-VERIFICATION",
            "D7G-DEBT-STAR-PAIR-NORMALIZATION-ALTERNATIVES",
        ],
        "the_spec_must_encode_the_correction_and_name_the_reference_normalization_without_claiming_unique_continuum_normalization_or_executable_general_SPD_validation",
        [
            "vertex_space_K4",
            "transpose_without_typed_adjoint",
            "reference_normalization_is_unique_continuum_law",
        ],
    ),
    claim(
        "D10-CL-N-007",
        "normative",
        "each_profile_has_scoped_disabled_transition_state_observable_and_lifecycle_reduction_surfaces_to_GRC9V3",
        ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D9-v1"],
        [],
        "the_spec_must_state_each_reduction_surface_separately_and_must_not_infer_snapshot_or_event_equivalence_from_transition_equivalence",
        ["single_disabled_witness_proves_all_equivalence_surfaces"],
    ),
    claim(
        "D10-CL-N-008",
        "normative",
        "all_profile_parameters_units_gauge_normalization_domain_solver_and_composition_choices_are_declared_profile_identity_not_hidden_universal_constants",
        ["GRC9V4-CD-D7V2-v1", "GRC9V4-GTRS-COMP-v1", "GRC9V4-CD-D9-v1"],
        [
            "D7-DEBT-A-UNITS-AND-GAUGE",
            "D7GV2-DEBT-H4-CAPACITY-AND-PROFILE-COMPARABILITY",
            "D7G-DEBT-STAR-PAIR-NORMALIZATION-ALTERNATIVES",
            "GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS",
        ],
        "the_spec_must_require_profile_local_dimensional_and_gauge_declarations_and_block_cross_profile_magnitude_comparison_without_a_separate_bridge",
        [
            "one_profile_scale_is_universal",
            "common_symbol_implies_common_capacity",
            "gain_two_is_amplitude_equivalent_to_CI_or_PC",
        ],
    ),
    claim(
        "D10-CL-N-009",
        "normative",
        "every_executable_GRC9V4_instance_binds_exactly_one_admitted_constitutive_family_and_exactly_one_admitted_realization_as_one_unambiguous_complete_profile_identity",
        ["GRC9V4-CD-D7V2-v1", "GRC9V4-GTRS-COMP-v1", "GRC9V4-CD-D9-v1"],
        [
            "D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER",
            "GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS",
        ],
        "the_spec_must_define_the_current_executable_profile_set_as_A_C_cross_CI_OS_RG2b_PC_CI_PC_allow_implementations_to_support_any_nonempty_subset_and_require_each_runtime_state_to_bind_exactly_one_complete_identity",
        [
            "executable_profile_has_no_candidate",
            "executable_profile_has_no_realization",
            "runtime_state_has_ambiguous_profile_identity",
            "Candidate_B_is_executable_before_writer_readmission",
        ],
    ),
    claim(
        "D10-CL-O-001",
        "optional",
        "Candidate_A_is_an_admitted_normalized_nondimensional_revision_specific_temporalized_mobility_and_Read_Back_profile_family",
        ["GRC9V4-CD-D7-v1", "GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D8A-v1"],
        [
            "D7-DEBT-A-CORE-STATUS",
            "D7-DEBT-A-ABSORBABILITY",
            "D7-DEBT-A-UNITS-AND-GAUGE",
        ],
        "the_spec_may_define_the_present_A_law_as_a_named_optional_normalized_nondimensional_family_without_inherited_core_provenance_unique_completion_or_universally_nonabsorbable_status;_physical_dimensionalization_requires_a_future_units_and_gauge_bridge",
        [
            "current_A_law_is_inherited_core_by_provenance",
            "A_is_unique_V4",
            "A_is_universally_nonabsorbable",
            "normalized_A_is_already_physically_dimensionalized",
        ],
    ),
    claim(
        "D10-CL-O-002",
        "optional",
        "Candidate_C_is_an_admitted_revision_specific_derived_C_sector_Hodge_response_profile_family",
        ["GRC9V4-CD-D4V2-v1", "GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D8A-v1"],
        [
            "D6V2-DEBT-C-MATHEMATICAL-ABSORBABILITY",
            "D8A-DEBT-C-NONIDENTITY-FLAT-SHARP-WITNESS",
        ],
        "the_spec_may_define_C_as_a_named_optional_family_with_T_C_derived_and_without_universal_nonabsorbability_or_general_numeric_conditioning_claims",
        [
            "Candidate_C_T_C_is_authoritative",
            "C_is_universally_nonabsorbable",
            "identity_metric_witness_is_general_SPD_validation",
        ],
    ),
    claim(
        "D10-CL-O-003",
        "optional",
        "coupled_implicit_admits_A_with_bounded_domain_uniqueness_under_the_declared_self_map_and_contraction_contract_and_C_with_stratum_local_uniqueness_plus_exactly_one_required_self_consistent_regular_root_across_strata",
        [
            "GRC9V4-GTRS-CI-v1",
            "GRC9V4-CD-D8B-CI-v1",
            "GRC9V4-CD-D9-v1",
            "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1",
        ],
        [
            "GTRS-CI-DEBT-A-NONZERO-CHAIN-WITNESS",
            "GTRS-CI-DEBT-C-NONZERO-CHAIN-WITNESS",
            "D8B-CI-DEBT-A-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-C-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-A-TEMPORAL-STABILITY",
            "D8B-CI-DEBT-C-TEMPORAL-STABILITY",
            "D8B-CI-DEBT-A-ANALYSIS-METRIC",
        ],
        "the_spec_may_define_A_CI_on_its_declared_bounded_contraction_domain_and_C_CI_on_regular_selector_strata_with_unique_self_consistent_root_selection_without_numeric_stability_endpoint_or_preference_claims",
        [
            "local_root_is_global",
            "regularness_is_stability",
            "formal_path_is_endpoint_witness",
        ],
    ),
    claim(
        "D10-CL-O-004",
        "optional",
        "operator_split_is_an_admitted_one_pass_predictor_geometry_corrector_realization_for_A_and_C_with_an_explicit_split_consistency_residual",
        ["GRC9V4-GTRS-OS-v1"],
        [
            "GTRS-OS-DEBT-A-COMPLETE-CHAIN-WITNESS",
            "GTRS-OS-DEBT-C-COMPLETE-CHAIN-WITNESS",
        ],
        "the_spec_may_define_OS_as_optional_and_must_preserve_its_nonzero_bounded_split_defect_and_no_second_iteration_rule",
        [
            "OS_equals_CI",
            "split_defect_is_time_truncation_without_proof",
            "formal_consumer_is_endpoint_witness",
        ],
    ),
    claim(
        "D10-CL-O-005",
        "optional",
        "RG2b_is_an_admitted_bounded_reconstructed_geometry_realization_for_A_and_C_relative_to_a_frozen_equivariant_extension_profile",
        ["GRC9V4-GTRS-RG-v1"],
        ["GTRS-RG-DEBT-C1-SECTION-REGULARITY"],
        "the_spec_may_define_RG2b_as_Lipschitz_only_and_must_exclude_classical_derivative_or_continuation_spectrum_claims_without_a_C1_successor",
        ["RG_section_is_C1", "extension_relative_uniqueness_is_extension_independence"],
    ),
    claim(
        "D10-CL-O-006",
        "optional",
        "PC_current_is_an_admitted_scalar_ZOH_one_tau_PC_independent_persistent_K4_history_realization_for_A_and_C",
        ["GRC9V4-GTRS-PC-v1"],
        [
            "GTRS-PC-DEBT-A-COMPLETE-CHAIN-WITNESS",
            "GTRS-PC-DEBT-C-COMPLETE-CHAIN-WITNESS",
        ],
        "the_spec_may_define_the_current_scalar_ZOH_one_tau_PC_profile_with_explicit_Z4_authority_writer_lifecycle_and_release_while_leaving_committed_endpoint_hysteresis_as_evidence_debt_and_routing_materially_distinct_persistent_carrier_laws_to_successor_admission",
        [
            "distinct_Z_is_endpoint_hysteresis",
            "PC_is_relabelled_as_B",
            "current_PC_is_the_universal_persistent_carrier_law",
        ],
    ),
    claim(
        "D10-CL-O-007",
        "optional",
        "CI_plus_PC_is_an_admitted_revision_specific_unit_immediate_plus_unit_retained_composition_for_A_with_bounded_domain_contraction_uniqueness_and_C_with_stratum_local_composite_contraction_plus_exactly_one_self_consistent_regular_root_and_steady_source_gain_two",
        [
            "GRC9V4-GTRS-CI-PC-v1",
            "GRC9V4-CD-D9-v1",
            "GRC9V4-D9-PROFILE-STATE-LIFECYCLE-REGISTRY-v1",
        ],
        [
            "GTRS-CI-PC-DEBT-COMPLETE-CHAIN-AND-ANALYSIS",
            "GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS",
        ],
        "the_spec_may_define_this_exact_gain_two_profile_as_optional_but_not_unique_required_amplitude_equivalent_core_or_preferred",
        [
            "CI_PC_is_unique_composition",
            "gain_two_is_amplitude_equivalent",
            "joint_root_nonannihilation_is_committed_endpoint_hysteresis",
        ],
    ),
    claim(
        "D10-CL-C-001",
        "conditional",
        "classical_structural_Hessian_and_alpha_claims_require_the_declared_C2_subchart_a_formed_branch_and_instantiated_coefficients_normalization_and_operator",
        ["GRC9V4-CD-D8B-CI-v1"],
        ["D8B-CI-DEBT-A-FORMED-BRANCH-ALPHA", "D8B-CI-DEBT-C-FORMED-BRANCH-ALPHA"],
        "the_spec_may_define_the_formal_operator_surface_but_evidence_profiles_must_gate_numeric_alpha_or_structural_stability",
        ["formal_Hessian_is_numeric_alpha", "C1_branch_has_unqualified_Hessian"],
        "formed_branch_structural_analysis_claimed",
    ),
    claim(
        "D10-CL-C-002",
        "conditional",
        "lossless_history_preserving_topology_continuation_requires_sufficient_typed_event_lineage_and_target_profile_readmission",
        ["GRC9V4-CD-D9-v1"],
        [],
        "the_spec_must_default_to_archive_or_reset_without_lineage_and_may_admit_stronger_preservation_only through_L_K4_evt_or_typed_W_lineage",
        ["generic_lossless_history_without_lineage"],
        "lossless_event_history_preservation_claimed",
    ),
    claim(
        "D10-CL-C-003",
        "conditional",
        "passage_through_current_singularity_requires_a_separately_admitted_named_singular_successor_profile_is_not_supplied_by_the_currently_admitted_regular_A_C_profiles_and_is_not_implied_merely_by_reopening_Candidate_B",
        ["GRC9V4-CD-D5V2-v1", "GRC9V4-CD-D9-v1"],
        ["D5V2-DEBT-CURRENT-SINGULAR-SUCCESSOR"],
        "the_initial_spec_must_fail_closed_at_singular_boundaries_and_reserve_a_successor_extension_point",
        [
            "singular_boundary_is_regular_transition",
            "solver_failure_is_event_semantics",
        ],
        "singular_boundary_passage_claimed",
    ),
    claim(
        "D10-CL-C-004",
        "conditional",
        "nonzero_committed_endpoint_effect_requires_a_complete_chain_witness_and_cannot_be_inferred_from_equation_level_consumption_root_level_nonannihilation_or_distinct_retained_state",
        [
            "GRC9V4-GTRS-CI-v1",
            "GRC9V4-GTRS-OS-v1",
            "GRC9V4-GTRS-PC-v1",
            "GRC9V4-GTRS-CI-PC-v1",
        ],
        [
            "GTRS-CI-DEBT-A-NONZERO-CHAIN-WITNESS",
            "GTRS-CI-DEBT-C-NONZERO-CHAIN-WITNESS",
            "GTRS-OS-DEBT-A-COMPLETE-CHAIN-WITNESS",
            "GTRS-OS-DEBT-C-COMPLETE-CHAIN-WITNESS",
            "GTRS-PC-DEBT-A-COMPLETE-CHAIN-WITNESS",
            "GTRS-PC-DEBT-C-COMPLETE-CHAIN-WITNESS",
            "GTRS-CI-PC-DEBT-COMPLETE-CHAIN-AND-ANALYSIS",
            "D8A-DEBT-C-NONIDENTITY-FLAT-SHARP-WITNESS",
        ],
        "the_spec_may_define_the_causal_path_but_runtime_or_evidence_profiles_must_gate_endpoint_effect_and_hysteresis_claims",
        ["formal_path_is_endpoint_effect", "distinct_state_is_hysteresis"],
        "endpoint_effect_or_hysteresis_claimed",
    ),
    claim(
        "D10-CL-C-005",
        "conditional",
        "temporal_or_structural_stability_continuation_spectrum_and_slow_mode_claims_require_formed_branch_numeric_operators_and_declared_analysis_metrics",
        ["GRC9V4-CD-D8B-CI-v1", "GRC9V4-GTRS-COMP-v1"],
        [
            "D8B-CI-DEBT-A-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-C-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-A-TEMPORAL-STABILITY",
            "D8B-CI-DEBT-C-TEMPORAL-STABILITY",
            "D8B-CI-DEBT-A-ANALYSIS-METRIC",
            "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION",
            "GTRS-RG-DEBT-C1-SECTION-REGULARITY",
        ],
        "the_design_spec_must_not_claim_stability_or_continuation_spectrum;_a_separate_evidence_profile_may_after_these_gates_pass",
        [
            "constructibility_is_stability",
            "lifecycle_continuation_is_spectrum_identity",
            "arbitrary_metric_is_nonnormality",
        ],
        "stability_or_continuation_spectrum_claimed",
    ),
    claim(
        "D10-CL-C-006",
        "conditional",
        "general_SPD_conditioning_executable_covariance_and_runtime_solver_claims_require_implementation_level_verification",
        ["GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1", "GRC9V4-CD-D8A-v1"],
        [
            "D7GV2-DEBT-METRIC-INVERSE-SOLVER-AND-COVARIANCE-VERIFICATION",
            "D7-DEBT-COVARIANCE-VERIFICATION",
            "D8A-DEBT-C-NONIDENTITY-FLAT-SHARP-WITNESS",
        ],
        "the_spec_may freeze typed equations and covariance laws_but_must_not_claim_executable_conformance",
        ["formula_covariance_is_runtime_verified", "identity_metric_is_general_SPD"],
        "implemented_conditioning_or_covariance_claimed",
    ),
    claim(
        "D10-CL-C-007",
        "conditional",
        "A_or_C_physical_nonabsorbability_requires_a_declared_baseline_model_class_and_an_exact_or_causal_nonredundancy_result",
        ["GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D8A-v1"],
        [
            "D7-DEBT-A-ABSORBABILITY",
            "D6V2-DEBT-C-MATHEMATICAL-ABSORBABILITY",
            "D7-DEBT-PHYSICAL-CHANNEL-ATTRIBUTION",
        ],
        "the_spec_may define_the_operator_paths_but_must_not_label_them_universally_irreducible_or_physically_distinct",
        [
            "operator_factorization_is_physical_channel",
            "closed_transition_is_nonabsorbability",
        ],
        "nonabsorbability_or_physical_channel_claimed",
    ),
    claim(
        "D10-CL-C-008",
        "conditional",
        "exclusive_profile_preference_or_numeric_ranking_requires_a_matched_formed_branch_charge_metric_and_runtime_discrimination_matrix",
        ["GRC9V4-GTRS-COMP-v1"],
        [
            "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION",
            "D7GV2-DEBT-H4-CAPACITY-AND-PROFILE-COMPARABILITY",
            "D8B-CI-DEBT-A-ANALYSIS-METRIC",
        ],
        "the_spec_must remain_nonranking_and_profile_explicit_until_a_successor_evidence_tranche_supports_comparison",
        [
            "first_working_profile_is_preferred",
            "common_symbol_is_common_capacity",
            "design_bound_is_numeric_superiority",
        ],
        "exclusive_preference_or_numeric_ranking_claimed",
    ),
    claim(
        "D10-CL-C-009",
        "conditional",
        "RG_classical_derivative_analysis_requires_C1_or_equivalent_bunching_regularization_beyond_the_accepted_Lipschitz_section",
        ["GRC9V4-GTRS-RG-v1"],
        ["GTRS-RG-DEBT-C1-SECTION-REGULARITY"],
        "the_spec_must type_RG_as_Lipschitz_only_and_route_derivative_analysis_to_a_named_successor",
        ["Lipschitz_is_C1", "RG_classical_Jacobian_without_regularization"],
        "RG_derivative_or_spectrum_claimed",
    ),
    claim(
        "D10-CL-C-010",
        "conditional",
        "physical_dimensionalization_of_the_present_A_profile_or_cross_candidate_capacity_gain_or_magnitude_comparison_requires_an_explicit_units_gauge_normalization_and_profile_bridge",
        ["GRC9V4-CD-D7G-v2", "GRC9V4-GTRS-COMP-v1"],
        [
            "D7GV2-DEBT-H4-CAPACITY-AND-PROFILE-COMPARABILITY",
            "D7-DEBT-A-UNITS-AND-GAUGE",
            "D7G-DEBT-STAR-PAIR-NORMALIZATION-ALTERNATIVES",
        ],
        "the_spec_must keep_capacity_and_gain_profile_local",
        [
            "shared_H4_symbol_is_equal_capacity",
            "profile_local_scale_is_cross_profile_metric",
        ],
        "physical_A_dimensionalization_or_cross_profile_magnitude_claimed",
    ),
    claim(
        "D10-CL-C-011",
        "conditional",
        "promotion_of_the_lineage_local_GRC9V4_contract_to_generic_Graph_GRC_V4_or_other_substrate_identity_requires_an_independent_equation_by_equation_substrate_provenance_audit_and_graph_generic_derivation",
        ["GRC9V4-CD-D0-v1", "GRC9V4-CD-D9-v1"],
        [],
        "D10_may_authorize_lineage_local_GRC9V4_specification_writing_but_final_substrate_identity_and_promotion_remain_open_until_the_preclosure_audit",
        [
            "GRC9_lineage_is_proof_of_nine_port_intrinsicness",
            "graph_generic_promotion_by_renaming",
            "final_substrate_identity_is_closed_at_D10",
        ],
        "promotion_beyond_lineage_local_GRC9V4_naming_claimed",
    ),
    claim(
        "D10-CL-C-012",
        "conditional",
        "the_current_A_C_cross_CI_OS_RG2b_PC_CI_PC_roster_is_complete_for_the_initial_lineage_local_specification_population_but_is_not_a_completeness_theorem_over_future_constitutive_families_temporal_or_history_realizations_hybrids_or_geometry_profiles",
        [
            "GRC9V4-CD-D0-v1",
            "GRC9V4-CD-D1-v1",
            "GRC9V4-CD-D7G-v2",
            "GRC9V4-GTRS-COMP-v1",
        ],
        [],
        "a_materially_distinct_successor_requires_explicit_provenance_or_derivation_a_new_complete_profile_identity_and_reopening_of_the_earliest_accepted_contract_whose_authority_staging_state_geometry_accounting_or_lifecycle_semantics_it_changes",
        [
            "A_C_exhaust_all_future_constitutive_families",
            "five_realizations_are_exhaustive",
            "current_PC_is_the_universal_persistent_carrier_law",
        ],
        "new_constitutive_realization_hybrid_or_geometry_profile_proposed",
    ),
    claim(
        "D10-CL-U-001",
        "open",
        "Candidate_B_requires_a_source_backed_U_B_formation_retention_release_capacity_and_lifecycle_writer_before_readmission",
        ["GRC9V4-CD-D7V2-v1", "GRC9V4-GTRS-COMP-v1", "GRC9V4-CD-D9-v1"],
        ["D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER"],
        "reserve_a_named_B_extension_slot_but_do_not_include_B_as_an_executable_V4_profile",
        ["B_is_rejected", "PC_is_B", "A_or_C_writer_is_copied_into_B"],
        "B_reopened",
    ),
    claim(
        "D10-CL-U-002",
        "open",
        "formed_branch_runtime_reachability_formation_retention_release_replay_and_nonzero_endpoint_effect_remain_unexecuted",
        ["GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D9-v1"],
        [
            "D7-DEBT-FORMED-BRANCH-RUNTIME",
            "GTRS-CI-DEBT-A-NONZERO-CHAIN-WITNESS",
            "GTRS-CI-DEBT-C-NONZERO-CHAIN-WITNESS",
            "GTRS-OS-DEBT-A-COMPLETE-CHAIN-WITNESS",
            "GTRS-OS-DEBT-C-COMPLETE-CHAIN-WITNESS",
            "GTRS-PC-DEBT-A-COMPLETE-CHAIN-WITNESS",
            "GTRS-PC-DEBT-C-COMPLETE-CHAIN-WITNESS",
            "GTRS-CI-PC-DEBT-COMPLETE-CHAIN-AND-ANALYSIS",
        ],
        "the_specification_may_be_written_but_runtime_capability_claims_wait_for_implementation_and_evidence",
        ["design_record_is_runtime_evidence"],
        "runtime_evidence_claimed",
    ),
    claim(
        "D10-CL-U-003",
        "open",
        "physical_channel_attribution_and_A_C_nonabsorbability_remain_model_class_and_evidence_questions",
        ["GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D8A-v1"],
        [
            "D7-DEBT-PHYSICAL-CHANNEL-ATTRIBUTION",
            "D7-DEBT-A-ABSORBABILITY",
            "D6V2-DEBT-C-MATHEMATICAL-ABSORBABILITY",
        ],
        "keep_the_operator_paths_without_physical_irreducibility_labels",
        ["formal_operator_is_physical_channel"],
        "physical_attribution_study_exists",
    ),
    claim(
        "D10-CL-U-004",
        "open",
        "numeric_structural_temporal_and_matched_profile_evidence_remains_to_be_instantiated",
        ["GRC9V4-CD-D8B-CI-v1", "GRC9V4-GTRS-COMP-v1"],
        [
            "D8B-CI-DEBT-A-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-C-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-A-TEMPORAL-STABILITY",
            "D8B-CI-DEBT-C-TEMPORAL-STABILITY",
            "D8B-CI-DEBT-A-ANALYSIS-METRIC",
            "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION",
        ],
        "route_to_post_spec_verification_without_blocking_bounded_design_specification",
        ["no_numeric_evidence_means_no_design_spec"],
        "numeric_evidence_tranche_runs",
    ),
    claim(
        "D10-CL-U-005",
        "open",
        "alternative_star_pair_normalizations_and_richer_DEC_edge_volume_profiles_remain_available_as_named_successor_profiles",
        ["GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1", "GRC9V4-CD-D8A-v1"],
        ["D7G-DEBT-STAR-PAIR-NORMALIZATION-ALTERNATIVES"],
        "encode_the_accepted_reference_normalization_as_a_named_profile_not_a_uniqueness_theorem",
        ["reference_normalization_exhausts_all_lawful_profiles"],
        "alternative_discretization_profile_proposed",
    ),
    claim(
        "D10-CL-X-001",
        "negative",
        "generic_lossless_history_preservation_without_sufficient_event_lineage_is_not_canonically_definable",
        ["GRC9V4-CD-D9-v1"],
        [],
        "the_spec_must_use_explicit_archive_or_reset_as_the_generic_fallback",
        ["arbitrary_history_embedding_is_native_continuation"],
    ),
    claim(
        "D10-CL-X-002",
        "negative",
        "the_accepted_design_evidence_does_not_support_unique_candidate_unique_realization_unique_composition_or_stability_based_architecture_preference",
        ["GRC9V4-GTRS-COMP-v1", "GRC9V4-CD-D9-v1"],
        [
            "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION",
            "D7GV2-DEBT-H4-CAPACITY-AND-PROFILE-COMPARABILITY",
        ],
        "the_spec_must_be_profile_explicit_and_nonranking",
        [
            "A_preferred_because_first",
            "CI_preferred_because_first",
            "constructibility_is_superiority",
        ],
    ),
    claim(
        "D10-CL-X-003",
        "negative",
        "bounded_constructibility_regularness_lifecycle_validity_and_persistence_do_not_establish_temporal_or_structural_stability",
        ["GRC9V4-CD-D8B-CI-v1", "GRC9V4-CD-D9-v1"],
        [
            "D8B-CI-DEBT-A-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-C-FORMED-BRANCH-ALPHA",
            "D8B-CI-DEBT-A-TEMPORAL-STABILITY",
            "D8B-CI-DEBT-C-TEMPORAL-STABILITY",
        ],
        "the_spec_claim_ceiling_stops_below_stability",
        ["regularness_is_stability", "retention_timescale_is_slow_mode_evidence"],
    ),
    claim(
        "D10-CL-X-004",
        "negative",
        "the_present_Candidate_A_completion_is_not_inherited_core_by_provenance_because_it_is_an_explicit_revision_specific_constitutive_completion",
        ["GRC9V4-CD-D7-v1", "GRC9V4-CD-D7V2-v1"],
        ["D7-DEBT-A-CORE-STATUS"],
        "classify_the_present_A_law_as_revision_specific_optional_constitutive_content_without_claiming_that_no_A_like_law_can_ever_be_derived_from_core",
        [
            "present_A_is_native_core_by_provenance",
            "revision_specific_use_of_core_surfaces_is_inherited_core_derivation",
        ],
    ),
    claim(
        "D10-CL-X-006",
        "negative",
        "Candidate_A_is_not_a_unique_GRC9V4_constitutive_completion_because_Candidate_C_also_survives_bounded_constitutive_admission",
        ["GRC9V4-CD-D7V2-v1", "GRC9V4-CD-D9-v1"],
        ["D7-DEBT-A-CORE-STATUS"],
        "the_spec_must_not_present_A_as_the_unique_required_or_preferred_V4_completion",
        ["A_is_unique_completion", "A_is_preferred_because_constructed_first"],
    ),
    claim(
        "D10-CL-X-005",
        "negative",
        "PC_does_not_supply_or_substitute_for_Candidate_Bs_missing_source_backed_writer",
        ["GRC9V4-GTRS-PC-v1", "GRC9V4-GTRS-COMP-v1", "GRC9V4-CD-D9-v1"],
        ["D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER"],
        "keep_B_routed_not_rejected_and_PC_separate",
        ["PC_is_B", "B_is_rejected_by_missing_writer"],
    ),
]


TRANSFORMATIONS: dict[str, dict[str, Any]] = {
    "GTRS-RG-DEBT-C1-SECTION-REGULARITY": {
        "blocked": "D10-CL-C-009",
        "supported": "D10-CL-O-005",
        "transformation": "narrowed",
        "successors": ["D10-CL-O-005", "D10-CL-C-009"],
        "effect": "RG2b_is_optional_Lipschitz_only;_classical_derivative_and_spectrum_claims_are_excluded",
        "verification": None,
    },
    "GTRS-OS-DEBT-A-COMPLETE-CHAIN-WITNESS": {
        "blocked": "D10-CL-C-004",
        "supported": "D10-CL-O-004",
        "transformation": "routed",
        "successors": ["D10-CL-O-004", "D10-CL-U-002"],
        "effect": "OS_A_design_profile_is_admissible_but_endpoint_effect_waits_for_verification",
        "verification": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
    },
    "GTRS-OS-DEBT-C-COMPLETE-CHAIN-WITNESS": {
        "blocked": "D10-CL-C-004",
        "supported": "D10-CL-O-004",
        "transformation": "routed",
        "successors": ["D10-CL-O-004", "D10-CL-U-002"],
        "effect": "OS_C_design_profile_is_admissible_but_endpoint_effect_waits_for_verification",
        "verification": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
    },
    "D8B-CI-DEBT-A-FORMED-BRANCH-ALPHA": {
        "blocked": "D10-CL-C-001",
        "supported": "D10-CL-O-003",
        "transformation": "routed",
        "successors": ["D10-CL-C-001", "D10-CL-U-004"],
        "effect": "formal_A_operator_surface_may_be_specified_but_numeric_alpha_is_not_a_design_claim",
        "verification": "D10-VERIFY-FORMED-BRANCH-STRUCTURAL-TEMPORAL",
    },
    "D8B-CI-DEBT-C-FORMED-BRANCH-ALPHA": {
        "blocked": "D10-CL-C-001",
        "supported": "D10-CL-O-003",
        "transformation": "routed",
        "successors": ["D10-CL-C-001", "D10-CL-U-004"],
        "effect": "formal_C_operator_surface_may_be_specified_but_numeric_alpha_is_not_a_design_claim",
        "verification": "D10-VERIFY-FORMED-BRANCH-STRUCTURAL-TEMPORAL",
    },
    "D8B-CI-DEBT-A-TEMPORAL-STABILITY": {
        "blocked": "D10-CL-C-005",
        "supported": "D10-CL-O-003",
        "transformation": "routed",
        "successors": ["D10-CL-C-005", "D10-CL-U-004", "D10-CL-X-003"],
        "effect": "CI_A_is_design_admissible_without_temporal_stability_status",
        "verification": "D10-VERIFY-FORMED-BRANCH-STRUCTURAL-TEMPORAL",
    },
    "D8B-CI-DEBT-C-TEMPORAL-STABILITY": {
        "blocked": "D10-CL-C-005",
        "supported": "D10-CL-O-003",
        "transformation": "routed",
        "successors": ["D10-CL-C-005", "D10-CL-U-004", "D10-CL-X-003"],
        "effect": "CI_C_is_design_admissible_without_temporal_stability_status",
        "verification": "D10-VERIFY-FORMED-BRANCH-STRUCTURAL-TEMPORAL",
    },
    "D8B-CI-DEBT-A-ANALYSIS-METRIC": {
        "blocked": "D10-CL-C-005",
        "supported": "D10-CL-O-003",
        "transformation": "routed",
        "successors": ["D10-CL-C-005", "D10-CL-U-004"],
        "effect": "no_absolute_A_nonnormality_or_cross_architecture_temporal_metric_enters_the_design_spec",
        "verification": "D10-VERIFY-A-ANALYSIS-METRIC",
    },
    "GTRS-CI-DEBT-A-NONZERO-CHAIN-WITNESS": {
        "blocked": "D10-CL-C-004",
        "supported": "D10-CL-O-003",
        "transformation": "narrowed",
        "successors": ["D10-CL-O-003", "D10-CL-C-004", "D10-CL-U-002"],
        "effect": "CI_A_is_specifiable_as_equation_level_load_bearing_without_an_endpoint_effect_claim",
        "verification": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
    },
    "GTRS-CI-DEBT-C-NONZERO-CHAIN-WITNESS": {
        "blocked": "D10-CL-C-004",
        "supported": "D10-CL-O-003",
        "transformation": "narrowed",
        "successors": ["D10-CL-O-003", "D10-CL-C-004", "D10-CL-U-002"],
        "effect": "CI_C_is_specifiable_as_equation_level_load_bearing_without_an_endpoint_effect_claim",
        "verification": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
    },
    "D8A-DEBT-C-NONIDENTITY-FLAT-SHARP-WITNESS": {
        "blocked": "D10-CL-C-006",
        "supported": "D10-CL-O-002",
        "transformation": "routed",
        "successors": ["D10-CL-O-002", "D10-CL-C-006"],
        "effect": "typed_C_pipeline_is_normative_but_general_nonidentity_numeric_conformance_is_verification",
        "verification": "D10-VERIFY-EXECUTABLE-COVARIANCE-HODGE",
    },
    "D7GV2-DEBT-H4-CAPACITY-AND-PROFILE-COMPARABILITY": {
        "blocked": "D10-CL-C-010",
        "supported": "D10-CL-N-008",
        "transformation": "narrowed",
        "successors": ["D10-CL-N-008", "D10-CL-C-010", "D10-CL-X-002"],
        "effect": "capacity_and_gain_are_profile_local_and_cannot_rank_A_C_or_realizations",
        "verification": None,
    },
    "D7GV2-DEBT-METRIC-INVERSE-SOLVER-AND-COVARIANCE-VERIFICATION": {
        "blocked": "D10-CL-C-006",
        "supported": "D10-CL-N-006",
        "transformation": "routed",
        "successors": ["D10-CL-N-006", "D10-CL-C-006"],
        "effect": "typed_maps_enter_the_spec_while_executable_conditioning_and_covariance_wait",
        "verification": "D10-VERIFY-EXECUTABLE-COVARIANCE-HODGE",
    },
    "D7G-DEBT-STAR-PAIR-NORMALIZATION-ALTERNATIVES": {
        "blocked": "D10-CL-C-010",
        "supported": "D10-CL-N-006",
        "transformation": "split",
        "successors": ["D10-CL-N-006", "D10-CL-U-005", "D10-CL-C-010"],
        "effect": "the_corrected_reference_normalization_is_a_named_profile_not_a_unique_continuum_law",
        "verification": None,
    },
    "D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER": {
        "blocked": "D10-CL-U-001",
        "supported": "D10-CL-X-005",
        "transformation": "routed",
        "successors": ["D10-CL-U-001", "D10-CL-X-005"],
        "effect": "B_is_reserved_as_a_successor_extension_slot_and_is_neither_executable_nor_rejected",
        "verification": None,
    },
    "D6V2-DEBT-C-MATHEMATICAL-ABSORBABILITY": {
        "blocked": "D10-CL-C-007",
        "supported": "D10-CL-O-002",
        "transformation": "narrowed",
        "successors": ["D10-CL-O-002", "D10-CL-U-003", "D10-CL-C-007"],
        "effect": "C_operator_family_is_optional_without_universal_nonabsorbability_or_physical_channel_status",
        "verification": None,
    },
    "D7-DEBT-A-CORE-STATUS": {
        "blocked": historical_claim_id("D7-DEBT-A-CORE-STATUS"),
        "supported": "D10-CL-O-001",
        "transformation": "resolved_negative",
        "successors": ["D10-CL-O-001", "D10-CL-X-004", "D10-CL-X-006"],
        "effect": "the_present_A_law_is_revision_specific_optional_content_not_inherited_core_by_provenance_and_not_a_unique_completion;_future_core_derivation_of_an_A_like_law_remains_unclaimed",
        "verification": None,
    },
    "D7-DEBT-A-ABSORBABILITY": {
        "blocked": "D10-CL-C-007",
        "supported": "D10-CL-O-001",
        "transformation": "narrowed",
        "successors": ["D10-CL-O-001", "D10-CL-U-003", "D10-CL-C-007"],
        "effect": "A_operator_family_is_optional_without_universal_nonabsorbability_or_physical_channel_status",
        "verification": None,
    },
    "D7-DEBT-A-UNITS-AND-GAUGE": {
        "blocked": "D10-CL-C-010",
        "supported": "D10-CL-O-001",
        "transformation": "split",
        "successors": ["D10-CL-N-008", "D10-CL-C-010", "D10-CL-O-001"],
        "effect": "the_present_A_law_is_admitted_only_as_a_normalized_nondimensional_reference_profile;_physical_dimensionalization_and_cross_profile_comparison_require_a_future_units_gauge_normalization_bridge",
        "verification": None,
    },
    "D7-DEBT-FORMED-BRANCH-RUNTIME": {
        "blocked": "D10-CL-U-002",
        "supported": "D10-CL-N-003",
        "transformation": "routed",
        "successors": ["D10-CL-U-002"],
        "effect": "runtime_reachability_is_not_required_to_write_the_bounded_design_spec_but_blocks_runtime_capability_claims",
        "verification": "D10-VERIFY-RUNTIME-FORMATION-RETENTION-RELEASE",
    },
    "D7-DEBT-PHYSICAL-CHANNEL-ATTRIBUTION": {
        "blocked": "D10-CL-U-003",
        "supported": "D10-CL-C-007",
        "transformation": "routed",
        "successors": ["D10-CL-U-003", "D10-CL-C-007"],
        "effect": "physical_attribution_remains_a_scientific_successor_question_and_is_not_relabelled_as_implementation_verification",
        "verification": None,
    },
    "D7-DEBT-COVARIANCE-VERIFICATION": {
        "blocked": "D10-CL-C-006",
        "supported": "D10-CL-N-006",
        "transformation": "routed",
        "successors": ["D10-CL-C-006"],
        "effect": "formula_level_covariance_is_normative_while_executable_conformance_waits",
        "verification": "D10-VERIFY-EXECUTABLE-COVARIANCE-HODGE",
    },
    "D5V2-DEBT-CURRENT-SINGULAR-SUCCESSOR": {
        "blocked": "D10-CL-C-003",
        "supported": "D10-CL-N-005",
        "transformation": "routed",
        "successors": ["D10-CL-C-003"],
        "effect": "the_initial_spec_is_regular_profile_only_and_fails_closed_at_current_singularity",
        "verification": None,
    },
    "D8A-DEBT-HODGE-CORRECTION-NORMATIVE-ENCODING": {
        "blocked": historical_claim_id("D8A-DEBT-HODGE-CORRECTION-NORMATIVE-ENCODING"),
        "supported": "D10-CL-N-006",
        "transformation": "confirmed",
        "successors": ["D10-CL-N-006"],
        "effect": "the_accepted_Hodge_type_correction_must_be_encoded_in_the_normative_spec",
        "verification": None,
    },
    "GTRS-PC-DEBT-A-COMPLETE-CHAIN-WITNESS": {
        "blocked": "D10-CL-C-004",
        "supported": "D10-CL-O-006",
        "transformation": "routed",
        "successors": ["D10-CL-O-006", "D10-CL-U-002"],
        "effect": "PC_A_is_optional_but_endpoint_hysteresis_waits_for_a_complete_chain_witness",
        "verification": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
    },
    "GTRS-PC-DEBT-C-COMPLETE-CHAIN-WITNESS": {
        "blocked": "D10-CL-C-004",
        "supported": "D10-CL-O-006",
        "transformation": "routed",
        "successors": ["D10-CL-O-006", "D10-CL-U-002"],
        "effect": "PC_C_is_optional_but_endpoint_hysteresis_waits_for_a_complete_chain_witness",
        "verification": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
    },
    "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION": {
        "blocked": "D10-CL-C-008",
        "supported": "D10-CL-X-002",
        "transformation": "routed",
        "successors": ["D10-CL-X-002", "D10-CL-U-004", "D10-CL-C-008"],
        "effect": "current_evidence_supports_a_nonranking_architecture_while_the_open_scientific_question_of_matched_profile_discrimination_routes_to_verification",
        "verification": "D10-VERIFY-MATCHED-PROFILE-DISCRIMINATION",
    },
    "GTRS-CI-PC-DEBT-COMPLETE-CHAIN-AND-ANALYSIS": {
        "blocked": "D10-CL-C-004",
        "supported": "D10-CL-O-007",
        "transformation": "routed",
        "successors": ["D10-CL-O-007", "D10-CL-U-002", "D10-CL-U-004"],
        "effect": "CI_PC_is_optional_at_joint_root_and_complete_transition_design_level_without_endpoint_or_stability_evidence",
        "verification": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
    },
    "GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS": {
        "blocked": historical_claim_id("GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS"),
        "supported": "D10-CL-O-007",
        "transformation": "narrowed",
        "successors": ["D10-CL-O-007", "D10-CL-N-008", "D10-CL-X-002"],
        "effect": "the_exact_unit_plus_unit_gain_two_law_is_a_named_optional_revision_specific_profile_not_unique_required_core_or_amplitude_equivalent",
        "verification": None,
    },
}


VERIFICATION_OBLIGATIONS = [
    {
        "obligation_id": "D9-VERIFY-QUANTITATIVE-PARAMETER-ENVELOPES",
        "scope": "instantiate_and_pressure_OS_RG_CI_PC_and_CI_PC_bounds_conditioning_release_and_source_closure_constants",
        "claim_ids_blocked": ["D10-CL-U-004", "D10-CL-C-008"],
        "kind": "numeric_conformance",
    },
    {
        "obligation_id": "D9-VERIFY-LIFECYCLE-RUNTIME-CONFORMANCE",
        "scope": "execute_snapshot_reset_duplicate_failure_atomicity_replay_whole_lifecycle_tuple_event_and_profile_migration_contracts",
        "claim_ids_blocked": ["D10-CL-U-002"],
        "kind": "runtime_conformance",
    },
    {
        "obligation_id": "D9-VERIFY-MIGRATION-AND-EVENT-CONFORMANCE",
        "scope": "execute_A_C_profile_and_topology_migrations_over_current_reset_and_Q_target_with_typed_history_transport_or_loss_receipts",
        "claim_ids_blocked": ["D10-CL-U-002"],
        "kind": "runtime_conformance",
    },
    {
        "obligation_id": "D9-VERIFY-CHARGE-AND-EVENT-RECEIPTS",
        "scope": "verify_general_charge_conservation_positivity_Q_target_updates_sources_impulses_and_event_receipts",
        "claim_ids_blocked": ["D10-CL-U-002"],
        "kind": "runtime_conformance",
    },
    {
        "obligation_id": "D10-VERIFY-COMPLETE-CHAIN-WITNESSES",
        "scope": "execute_A_C_CI_OS_PC_and_CI_PC_complete_chain_nonannihilation_and_committed_endpoint_witnesses",
        "claim_ids_blocked": ["D10-CL-C-004", "D10-CL-U-002"],
        "kind": "runtime_and_numeric_evidence",
    },
    {
        "obligation_id": "D10-VERIFY-FORMED-BRANCH-STRUCTURAL-TEMPORAL",
        "scope": "instantiate_formed_branches_Hessians_complete_step_Jacobians_alpha_mu_gamma_nonnormal_growth_and_stability",
        "claim_ids_blocked": ["D10-CL-C-001", "D10-CL-C-005", "D10-CL-U-004"],
        "kind": "numeric_evidence",
    },
    {
        "obligation_id": "D10-VERIFY-A-ANALYSIS-METRIC",
        "scope": "freeze_and_pressure_a_dimensionally_consistent_A_complete_state_analysis_metric_before_absolute_nonnormality_or_cross_architecture_comparison",
        "claim_ids_blocked": ["D10-CL-C-005", "D10-CL-C-008"],
        "kind": "analysis_conformance",
    },
    {
        "obligation_id": "D10-VERIFY-EXECUTABLE-COVARIANCE-HODGE",
        "scope": "verify_general_SPD_flat_sharp_inverse_solver_conditioning_graph_relabel_orientation_component_cycle_boundary_and_adapter_covariance",
        "claim_ids_blocked": ["D10-CL-C-006"],
        "kind": "implementation_conformance",
    },
    {
        "obligation_id": "D10-VERIFY-MATCHED-PROFILE-DISCRIMINATION",
        "scope": "run_preregistered_matched_formed_branch_profile_comparisons_before_any_preference_or_numeric_ranking",
        "claim_ids_blocked": ["D10-CL-C-008", "D10-CL-U-004"],
        "kind": "numeric_evidence",
    },
    {
        "obligation_id": "D10-VERIFY-RUNTIME-FORMATION-RETENTION-RELEASE",
        "scope": "show_runtime_reachability_formation_retention_release_replay_and_failure_atomicity_for_implemented_profiles",
        "claim_ids_blocked": ["D10-CL-U-002"],
        "kind": "runtime_evidence",
    },
    {
        "obligation_id": "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT",
        "scope": "classify_every_selected_normative_equation_and_contract_as_nine_port_intrinsic_GRC9V3_derived_but_abstractable_generic_graph_derived_or_core_substrate_independent_and_require_an_independent_graph_generic_derivation_before_promotion_out_of_the_GRC9_lineage",
        "claim_ids_blocked": ["D10-CL-C-011"],
        "kind": "preclosure_scientific_provenance_audit",
    },
]


def iter_debt_occurrences(value: Any, debt_ids: set[str], pointer: str = ""):
    if isinstance(value, dict):
        if value.get("debt_id") in debt_ids:
            yield value["debt_id"], pointer or "/", value
        for key, child in value.items():
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            yield from iter_debt_occurrences(child, debt_ids, f"{pointer}/{escaped}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_debt_occurrences(child, debt_ids, f"{pointer}/{index}")


def build_lineage(source_rows: list[dict[str, Any]], debt_ids: set[str]):
    by_debt: dict[str, list[dict[str, Any]]] = {debt_id: [] for debt_id in debt_ids}
    for source in source_rows:
        path = ROOT / source["path"]
        data = json.loads(path.read_text())
        occurrences: dict[str, list[dict[str, Any]]] = {}
        for debt_id, pointer, row in iter_debt_occurrences(data, debt_ids):
            contract_fields = {
                key: row[key]
                for key in (
                    "blocking_scope",
                    "candidate_scope",
                    "issue",
                    "assumption_forbidden_downstream",
                    "resolution_gate",
                    "must_close_before_D10",
                )
                if key in row
            }
            occurrences.setdefault(debt_id, []).append(
                {
                    "json_pointer": pointer,
                    "status_or_disposition": row.get("status")
                    or row.get("disposition"),
                    "debt_contract": contract_fields or None,
                }
            )
        for debt_id, found in occurrences.items():
            by_debt[debt_id].append(
                {
                    "record_id": source["source_id"],
                    "path": source["path"],
                    "source_digest": source["source_digest"],
                    "file_sha256": source["file_sha256"],
                    "occurrences": found,
                }
            )
    return by_debt


def representative_debt_contract(
    debt_id: str, lineage: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    contracts = [
        occurrence["debt_contract"]
        for record in lineage[debt_id]
        for occurrence in record["occurrences"]
        if occurrence["debt_contract"]
    ]
    if not contracts:
        return {}
    return max(
        contracts,
        key=lambda row: (len(row), json.dumps(row, sort_keys=True, ensure_ascii=True)),
    )


def build() -> None:
    sources = accepted_sources()
    claims = [dict(row) for row in CLAIMS]
    current_claim_ids = {row["claim_id"] for row in claims}
    if len(current_claim_ids) != len(claims):
        raise ValueError("duplicate claim IDs")

    d9_path = DECISIONS / "D9ResidualDebtLedger.json"
    d9 = json.loads(d9_path.read_text())
    carried = [
        row for row in d9["predecessor_dispositions"] if row["status"] == "carried"
    ]
    carried_ids = {row["debt_id"] for row in carried}
    if len(carried) != 29 or carried_ids != set(TRANSFORMATIONS):
        raise ValueError(
            "D10 transformation map does not equal the accepted D9 debt union"
        )

    lineage = build_lineage(sources, carried_ids)
    if not all(lineage.values()):
        raise ValueError("a carried debt has no predecessor lineage")

    d9_by_id = {row["debt_id"]: row for row in carried}
    historical_claims = []
    for debt_id in [row["debt_id"] for row in carried]:
        contract = representative_debt_contract(debt_id, lineage)
        statement = contract.get("issue", d9_by_id[debt_id]["reason"])
        stronger_claim_blocked = contract.get("blocking_scope")
        assumption_forbidden = contract.get("assumption_forbidden_downstream")
        if debt_id == "D7-DEBT-A-CORE-STATUS":
            statement = (
                "inherited_core_provenance_of_the_present_A_completion_was_unclassified"
            )
            stronger_claim_blocked = (
                "the_present_A_completion_is_inherited_core_by_provenance"
            )
            assumption_forbidden = (
                "use_of_core_or_GRC9V3_surfaces_proves_inherited_core_provenance"
            )
        historical_claims.append(
            {
                "claim_id": historical_claim_id(debt_id),
                "claim_class": "historical_predecessor",
                "statement": statement,
                "stronger_claim_blocked": stronger_claim_blocked,
                "assumption_forbidden_downstream": assumption_forbidden,
                "D9_predecessor_reason": d9_by_id[debt_id]["reason"],
                "evidence_refs": sorted(
                    {record["record_id"] for record in lineage[debt_id]}
                ),
                "transformed_by_debt_id": debt_id,
                "successor_claim_ids": sorted(
                    {
                        TRANSFORMATIONS[debt_id]["supported"],
                        *TRANSFORMATIONS[debt_id]["successors"],
                    }
                ),
            }
        )
    historical_claim_ids = {row["claim_id"] for row in historical_claims}
    all_claim_ids = current_claim_ids | historical_claim_ids

    for row in TRANSFORMATIONS.values():
        referenced = {row["blocked"], row["supported"], *row["successors"]}
        if not referenced <= all_claim_ids:
            raise ValueError(
                f"unknown claim ID in transformation: {referenced - all_claim_ids}"
            )

    categories = {
        name: []
        for name in ("normative", "optional", "conditional", "open", "negative")
    }
    for row in claims:
        categories[row["claim_class"]].append(row["claim_id"])

    debt_rows = []
    claim_by_id = {row["claim_id"]: row for row in claims}
    for debt_id in [row["debt_id"] for row in carried]:
        transform = TRANSFORMATIONS[debt_id]
        related_claim_ids = {
            row["claim_id"] for row in claims if debt_id in row["bearing_debt_ids"]
        }
        related_claim_ids.update(
            claim_id
            for claim_id in {
                transform["blocked"],
                transform["supported"],
                *transform["successors"],
            }
            if claim_id in current_claim_ids
        )
        supported_claim_ids = {transform["supported"]}
        conditioned_claim_ids = set()
        negative_successor_claim_ids = set()
        routed_claim_ids = set()
        for claim_id in related_claim_ids:
            claim_class = claim_by_id[claim_id]["claim_class"]
            if claim_class in {"normative", "optional"}:
                supported_claim_ids.add(claim_id)
            elif claim_class == "conditional":
                conditioned_claim_ids.add(claim_id)
            elif claim_class == "negative":
                negative_successor_claim_ids.add(claim_id)
            elif claim_class == "open":
                routed_claim_ids.add(claim_id)
        blocked_claim_ids = {transform["blocked"]}
        successor_claim_ids = {
            *transform["successors"],
            *related_claim_ids,
            *supported_claim_ids,
            *conditioned_claim_ids,
            *negative_successor_claim_ids,
            *routed_claim_ids,
        }
        debt_rows.append(
            {
                "debt_id": debt_id,
                "D9_predecessor_status": d9_by_id[debt_id]["status"],
                "D9_predecessor_reason": d9_by_id[debt_id]["reason"],
                "predecessor_claim_ids": [historical_claim_id(debt_id)],
                "blocked_claim_id": transform["blocked"],
                "supported_claim_id": transform["supported"],
                "blocked_claim_ids": sorted(blocked_claim_ids),
                "supported_claim_ids": sorted(supported_claim_ids),
                "conditioned_claim_ids": sorted(conditioned_claim_ids),
                "negative_successor_claim_ids": sorted(negative_successor_claim_ids),
                "routed_claim_ids": sorted(routed_claim_ids),
                "evidence_refs": sorted(
                    {record["record_id"] for record in lineage[debt_id]}
                ),
                "activation_condition": next(
                    row["activation_condition"]
                    for row in claims
                    if row["claim_id"] == transform["blocked"]
                )
                if transform["blocked"] in current_claim_ids
                else "historical_claim_transformed",
                "transformation": transform["transformation"],
                "successor_claim_ids": sorted(successor_claim_ids),
                "normative_effect": transform["effect"],
                "verification_obligation": transform["verification"],
                "predecessor_lineage": lineage[debt_id],
                "predecessor_lineage_complete": True,
            }
        )

    debt_by_id = {row["debt_id"]: row for row in debt_rows}
    for row in historical_claims:
        row["successor_claim_ids"] = debt_by_id[row["transformed_by_debt_id"]][
            "successor_claim_ids"
        ]
    claim_debt_edges = []
    for row in claims:
        related_debt_ids = sorted(
            {
                debt_id
                for debt_id, debt_row in debt_by_id.items()
                if any(
                    row["claim_id"] in debt_row[field]
                    for field in (
                        "blocked_claim_ids",
                        "supported_claim_ids",
                        "conditioned_claim_ids",
                        "negative_successor_claim_ids",
                        "routed_claim_ids",
                        "successor_claim_ids",
                    )
                )
            }
            | set(row["bearing_debt_ids"])
        )
        row["bearing_debt_ids"] = related_debt_ids
        edges = []
        for debt_id in related_debt_ids:
            debt_row = debt_by_id[debt_id]
            edge_types = []
            memberships = (
                ("blocked_claim_ids", "blocked_by"),
                ("supported_claim_ids", "supported_by"),
                ("conditioned_claim_ids", "conditioned_by"),
                ("negative_successor_claim_ids", "negative_successor_of"),
                ("routed_claim_ids", "routed_through"),
                ("successor_claim_ids", "successor_of"),
            )
            for field, edge_type in memberships:
                if row["claim_id"] in debt_row[field]:
                    edge_types.append(edge_type)
            if not edge_types:
                raise ValueError(
                    f"claim/debt edge has no reciprocal type: {row['claim_id']} / {debt_id}"
                )
            edge = {"debt_id": debt_id, "edge_types": edge_types}
            edges.append(edge)
            claim_debt_edges.append({"claim_id": row["claim_id"], **edge})
        row["debt_edges"] = edges

    for row in historical_claims:
        debt_row = debt_by_id[row["transformed_by_debt_id"]]
        edge_types = ["predecessor_claim"]
        if row["claim_id"] in debt_row["blocked_claim_ids"]:
            edge_types.append("blocked_by")
        edge = {
            "claim_id": row["claim_id"],
            "debt_id": row["transformed_by_debt_id"],
            "edge_types": edge_types,
        }
        row["debt_edges"] = [
            {"debt_id": edge["debt_id"], "edge_types": edge["edge_types"]}
        ]
        claim_debt_edges.append(edge)

    topology = {
        "schema_version": "grc9v4_d10_claim_topology_v2",
        "artifact_id": "GRC9V4-D10-CLAIM-TOPOLOGY-v2",
        "gate_id": "D10",
        "status": "accepted_bounded",
        "governing_rule": "debt_is_not_a_checklist_item_it_is_a_stressed_edge_in_an_evolving_claim_topology",
        "invariants": [
            "no_debt_disposition_without_a_claim_ledger_disposition",
            "no_normative_D10_claim_without_tracing_all_debts_that_bear_on_it",
            "every_claim_to_debt_edge_has_a_corresponding_typed_debt_to_claim_edge",
            "historical_predecessor_claims_remain_first_class_nodes",
            "blocked_by_applies_only_to_historical_predecessors_or_still_unearned_conditional_or_open_current_claims",
            "scope_exclusion_is_routed_not_scientifically_resolved",
            "resolved_negatives_are_first_class_claims",
            "implementation_and_numeric_obligations_do_not_masquerade_as_scientific_design_debt",
            "the_current_complete_profile_roster_is_not_a_completeness_theorem_over_future_lawful_V4_profiles",
            "successor_work_activates_claim_local_topology_without_a_prescribed_linear_schedule",
        ],
        "architecture_selection": {
            "selected_architecture": "profile_explicit_lineage_local_GRC9V4_common_substrate_interface_with_named_A_C_and_CI_OS_RG2b_PC_CI_PC_complete_profiles",
            "unique_candidate_selected": False,
            "unique_realization_selected": False,
            "selection_basis": "shared_authority_complete_step_lifecycle_representation_and_claim_ceiling_contract_not_numeric_ranking",
            "current_admitted_profile_population_is_future_exhaustive": False,
            "final_substrate_identity_closed": False,
        },
        "claim_categories": categories,
        "claims": claims,
        "historical_claim_nodes": historical_claims,
        "claim_debt_edges": claim_debt_edges,
        "claim_count": len(claims),
        "historical_claim_count": len(historical_claims),
        "total_claim_node_count": len(claims) + len(historical_claims),
        "claim_debt_edge_count": len(claim_debt_edges),
        "category_counts": {key: len(value) for key, value in categories.items()},
        "artifact_digest": "",
    }
    topology_path = DECISIONS / "D10NormativeClaimTopology.json"
    write_json(topology_path, topology, "artifact_digest")

    debt_ledger = {
        "schema_version": "grc9v4_d10_debt_claim_transformation_v2",
        "artifact_id": "GRC9V4-D10-DEBT-CLAIM-TRANSFORMATION-LEDGER-v2",
        "gate_id": "D10",
        "status": "accepted_bounded",
        "predecessor_record_id": "GRC9V4-CD-D9-v1",
        "predecessor_decision_digest": next(
            row["source_digest"]
            for row in sources
            if row["source_id"] == "GRC9V4-CD-D9-v1"
        ),
        "governing_rule": "claim_to_debt_to_pressure_or_evidence_to_claim_transformation",
        "allowed_transformations": [
            "confirmed",
            "strengthened",
            "narrowed",
            "generalized",
            "split",
            "replaced",
            "resolved_negative",
            "routed",
        ],
        "forbidden_disposition": "open_to_resolved_without_claim_transformation",
        "reciprocal_edge_rule": "every_claim_to_debt_edge_has_a_corresponding_typed_debt_to_claim_edge",
        "lineage_scan_scope": "all_accepted_D0_through_D9_decision_and_support_JSON_records_in_the_constitutive_design_decisions_directory",
        "debt_transformations": debt_rows,
        "debt_count": len(debt_rows),
        "transformation_counts": {
            name: sum(row["transformation"] == name for row in debt_rows)
            for name in (
                "confirmed",
                "strengthened",
                "narrowed",
                "generalized",
                "split",
                "replaced",
                "resolved_negative",
                "routed",
            )
        },
        "claimless_debt_disposition_count": sum(
            not row["successor_claim_ids"] for row in debt_rows
        ),
        "verification_obligations": VERIFICATION_OBLIGATIONS,
        "verification_obligation_count": len(VERIFICATION_OBLIGATIONS),
        "scientific_open_claims_preserved": [
            "D10-CL-U-001",
            "D10-CL-U-002",
            "D10-CL-U-003",
            "D10-CL-U-004",
            "D10-CL-U-005",
        ],
        "artifact_digest": "",
    }
    debt_path = DECISIONS / "D10DebtClaimTransformationLedger.json"
    write_json(debt_path, debt_ledger, "artifact_digest")

    executable_candidates = ["A", "C"]
    executable_realizations = ["CI", "OS", "RG2b", "PC", "CI_PC"]
    executable_complete_profiles = [
        f"{candidate}_{realization}"
        for candidate in executable_candidates
        for realization in executable_realizations
    ]
    profile = {
        "schema_version": "grc9v4_d10_specification_authorization_profile_v2",
        "artifact_id": "GRC9V4-D10-SPECIFICATION-AUTHORIZATION-PROFILE-v2",
        "gate_id": "D10",
        "status": "accepted_bounded",
        "selected_architecture": "profile_explicit_lineage_local_GRC9V4_common_substrate_interface_with_named_complete_constitutive_and_realization_profiles",
        "normative_common_claim_ids": categories["normative"],
        "optional_profile_claim_ids": categories["optional"],
        "conditional_claim_ids": categories["conditional"],
        "open_claim_ids": categories["open"],
        "negative_claim_ids": categories["negative"],
        "candidate_profiles": {
            "A": "named_optional_normalized_nondimensional_revision_specific_profile_family",
            "C": "named_optional_revision_specific_profile_family",
            "B": "reserved_successor_extension_slot_routed_not_rejected_no_executable_profile",
        },
        "realization_profiles": {
            "CI": "named_optional_A_bounded_domain_contraction_unique_and_C_stratum_local_contraction_unique_self_consistent_profile",
            "OS": "named_optional_one_pass_profile_with_split_residual",
            "RG2b": "named_optional_bounded_Lipschitz_profile",
            "PC": "named_optional_scalar_ZOH_one_tau_PC_independent_persistent_K4_history_profile",
            "CI_PC": "named_optional_revision_specific_gain_two_A_bounded_domain_and_C_stratified_unique_composition_profile",
        },
        "executable_profile_conformance_grammar": {
            "constitutive_family_cardinality_per_runtime_state": "exactly_one",
            "realization_cardinality_per_runtime_state": "exactly_one",
            "admitted_constitutive_families": executable_candidates,
            "admitted_realizations": executable_realizations,
            "admitted_complete_profile_ids": executable_complete_profiles,
            "admitted_complete_profile_count": len(executable_complete_profiles),
            "implementation_support_rule": "an_implementation_may_support_any_nonempty_subset_of_the_admitted_complete_profiles",
            "runtime_state_binding_rule": "X_current_X_reset_and_each_snapshot_bind_exactly_one_unambiguous_complete_profile_identity",
            "profile_migration_receipt_binding_rule": "each_migration_receipt_binds_the_ordered_pair_p_source_p_target",
            "topology_event_receipt_binding_rule": "each_topology_event_receipt_binds_the_ordered_pair_p_source_p_target_with_equality_when_the_complete_profile_is_unchanged",
            "current_admitted_profile_population_scope": "complete_for_the_initial_lineage_local_specification_population_not_exhaustive_over_future_lawful_V4_profiles",
            "current_profile_population_is_future_exhaustive": False,
            "future_profile_admission_rule": "a_materially_distinct_successor_requires_explicit_provenance_or_derivation_a_new_complete_profile_identity_and_reopening_of_the_earliest_accepted_contract_whose_authority_staging_state_geometry_accounting_or_lifecycle_semantics_it_changes",
            "zero_candidate_or_zero_realization_executable_instance_allowed": False,
            "Candidate_B_executable": False,
        },
        "unfolding_trajectory": {
            "current_topology_role": "freeze_the_currently_justified_claim_topology_and_currently_admitted_specification_population_not_a_fixed_successor_schedule",
            "normative_claim_route": "may_unfold_into_specification_after_D10_acceptance",
            "conditional_and_open_activation_rule": "activate_only_when_the_named_stronger_claim_or_successor_direction_is_attempted",
            "verification_obligation_rule": "gate_only_the_claims_they_name_not_a_mandatory_linear_backlog",
            "successor_profile_admission_rule": "new_constitutive_realization_hybrid_or_geometry_profiles_require_explicit_successor_admission_and_earliest_affected_contract_reopening",
            "negative_claim_rule": "remain_current_boundaries_until_new_evidence_transforms_them",
            "preclosure_convergence_rule": "the_substrate_provenance_audit_remains_mandatory_before_final_V4_substrate_naming_and_closure",
            "prescribed_successor_schedule": False,
        },
        "normative_specification_requirements": [
            "common_resource_state_authority_current_geometry_lifecycle_interface_and_invariant_contract_with_profile_supplied_constitutive_laws",
            "exactly_one_constitutive_family_plus_exactly_one_realization_per_executable_runtime_state",
            "ordered_source_target_complete_profile_identity_pairs_on_migration_and_topology_event_receipts",
            "current_ten_profile_population_is_complete_for_initial_specification_but_not_exhaustive_over_future_lawful_V4_profiles",
            "explicit_candidate_realization_normalization_units_gauge_domain_solver_and_composition_profile_identity",
            "accepted_graph_Hodge_type_correction_and_typed_K4_event_transport",
            "profile_local_claim_ceilings_and_blocked_relabels",
            "B_extension_slot_without_B_rejection_or_PC_relabel",
            "verification_obligation_registry_separate_from_scientific_claim_topology",
            "lineage_local_GRC9V4_naming_until_the_preclosure_substrate_provenance_audit",
        ],
        "selection_prohibitions": [
            "no_unique_candidate_or_realization_preference",
            "no_stability_or_continuation_spectrum_claim",
            "no_universal_nonabsorbability_or_physical_channel_claim",
            "no_runtime_implemented_or_formed_branch_claim",
            "no_cross_profile_capacity_or_numeric_ranking",
            "no_current_profile_roster_as_future_completeness_theorem",
            "no_current_scalar_ZOH_PC_as_universal_persistent_carrier_law",
            "no_promotion_to_generic_Graph_GRC_V4_without_independent_derivation",
        ],
        "authorization_scope": "lineage_local_profile_explicit_GRC9V4_specification_only",
        "final_substrate_identity_closed": False,
        "preclosure_obligation_id": "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT",
        "D10_disposition": "accepted_bounded_lineage_local_profile_explicit_spec_authorization",
        "specification_authorized_after_human_acceptance": True,
        "specification_authorized_now": True,
        "implementation_authorized": False,
        "runtime_or_src_change_authorized": False,
        "artifact_digest": "",
    }
    profile_path = DECISIONS / "D10SpecificationAuthorizationProfile.json"
    write_json(profile_path, profile, "artifact_digest")

    support_paths = [topology_path, debt_path, profile_path]
    manifest = []
    for role, path in zip(
        (
            "normative_claim_topology",
            "debt_claim_transformation_ledger",
            "specification_authorization_profile",
        ),
        support_paths,
        strict=True,
    ):
        data = json.loads(path.read_text())
        manifest.append(
            {
                "role": role,
                "path": path.relative_to(ROOT).as_posix(),
                "artifact_digest": data["artifact_digest"],
                "file_sha256": file_sha(path),
            }
        )

    controls = [
        "accepted_D9_predecessor_digest_and_SHA_match",
        "all_accepted_D0_D9_sources_are_bound_by_digest_and_SHA",
        "claim_categories_are_normative_optional_conditional_open_negative",
        "claim_ids_are_unique",
        "all_29_D9_carried_debts_are_present_exactly_once",
        "no_non_D9_debt_is_invented",
        "every_debt_names_blocked_and_supported_claims",
        "every_debt_names_a_nonbinary_claim_transformation",
        "every_debt_names_successor_claims",
        "every_debt_has_full_predecessor_lineage",
        "all_lineage_paths_are_repo_relative",
        "all_lineage_digests_and_SHAs_match",
        "no_scope_exclusion_is_called_scientific_resolution",
        "resolved_negative_claims_are_preserved",
        "verification_obligations_are_separate_from_scientific_design_debt",
        "all_normative_claims_list_bearing_debts_or_an_empty_exact_set",
        "all_claim_debt_references_exist",
        "all_debt_claim_references_exist",
        "all_29_historical_predecessor_claim_nodes_are_preserved",
        "every_claim_to_debt_edge_has_a_corresponding_typed_debt_to_claim_edge",
        "every_debt_to_claim_edge_has_a_corresponding_claim_to_debt_edge",
        "blocked_by_is_temporally_restricted_to_historical_conditional_or_open_claims",
        "profile_explicit_architecture_is_selected",
        "unique_candidate_selection_is_false",
        "unique_realization_selection_is_false",
        "Candidate_A_is_normalized_nondimensional_revision_specific_optional",
        "Candidate_C_is_revision_specific_optional",
        "Candidate_B_is_routed_not_rejected",
        "PC_does_not_relabel_as_B",
        "every_executable_runtime_state_binds_exactly_one_complete_profile",
        "current_reset_and_snapshot_each_bind_one_complete_profile_identity",
        "migration_receipts_bind_ordered_source_and_target_complete_profile_identities",
        "topology_event_receipts_bind_ordered_source_and_target_complete_profile_identities",
        "implementations_may_support_any_nonempty_subset_of_the_ten_complete_profiles",
        "current_ten_profile_roster_is_not_a_future_completeness_theorem",
        "current_PC_is_scalar_ZOH_one_tau_not_the_universal_persistent_carrier_law",
        "future_profiles_require_explicit_successor_admission_and_earliest_affected_contract_reopening",
        "unfolding_trajectory_does_not_prescribe_a_fixed_successor_schedule",
        "verification_obligations_gate_named_claims_not_a_linear_backlog",
        "negative_claims_remain_boundaries_until_transformed_by_new_evidence",
        "Candidate_B_is_excluded_from_the_current_executable_profile_set",
        "CI_preserves_D9_bounded_and_stratified_uniqueness",
        "OS_is_optional_with_split_residual",
        "RG2b_is_optional_Lipschitz_only",
        "PC_is_optional_independent_history",
        "CI_PC_is_optional_gain_two_revision_specific",
        "CI_PC_preserves_D9_bounded_and_stratified_uniqueness",
        "A_present_law_inherited_core_provenance_is_resolved_negative",
        "A_future_core_derivability_is_not_resolved_negative",
        "A_unique_completion_is_resolved_negative",
        "A_physical_dimensionalization_requires_a_future_bridge",
        "A_nonabsorbability_is_not_claimed",
        "C_nonabsorbability_is_not_claimed",
        "physical_channel_attribution_is_open",
        "formed_branch_runtime_is_open",
        "numeric_stability_is_open",
        "matched_profile_ranking_is_not_claimed",
        "matched_profile_discrimination_debt_is_routed_not_resolved_negative",
        "cross_profile_capacity_comparison_is_conditional",
        "reference_Hodge_normalization_is_not_unique",
        "Hodge_type_correction_is_normative",
        "general_SPD_runtime_conformance_is_not_claimed",
        "regular_profiles_fail_closed_at_current_singularity",
        "lossless_event_history_requires_lineage",
        "generic_no_lineage_history_preservation_remains_resolved_negative",
        "typed_lifecycle_does_not_imply_continuation_spectrum_identity",
        "complete_chain_consumption_does_not_imply_endpoint_effect",
        "constructibility_does_not_imply_stability",
        "lineage_local_spec_authorization_does_not_close_final_substrate_identity",
        "preclosure_substrate_provenance_audit_is_registered",
        "specification_authorization_follows_bounded_human_acceptance",
        "implementation_authorization_is_false",
        "runtime_or_src_change_authorization_is_false",
    ]
    control_contract = [
        {"control_id": f"D10-C{index:03d}", "status": "passed", "rule": rule}
        for index, rule in enumerate(controls, start=1)
    ]

    decision = {
        "schema_version": "grc9v4_constitutive_design_d10_v2",
        "record_type": "design_synthesis_and_specification_authorization_decision",
        "record_id": "GRC9V4-CD-D10-v1",
        "gate_id": "D10",
        "status": "accepted_bounded",
        "predecessor_record_id": "GRC9V4-CD-D9-v1",
        "predecessor_decision_digest": next(
            row["source_digest"]
            for row in sources
            if row["source_id"] == "GRC9V4-CD-D9-v1"
        ),
        "source_identities": sources,
        "artifact_manifest": manifest,
        "decision": {
            "governing_rule": "debt_is_a_stressed_edge_in_an_evolving_claim_topology_not_a_checklist_item",
            "claim_flow": "claim_to_debt_to_pressure_or_evidence_to_claim_transformation",
            "selected_architecture": profile["selected_architecture"],
            "selection_semantics": "select_the_lineage_local_profile_explicit_common_interface_and_invariant_architecture_without_flattening_or_ranking_candidate_or_realization_profiles",
            "claim_topology": {
                "normative": categories["normative"],
                "optional": categories["optional"],
                "conditional": categories["conditional"],
                "open": categories["open"],
                "negative": categories["negative"],
                "historical_predecessor_claim_node_count": len(historical_claims),
                "reciprocal_typed_claim_debt_edge_count": len(claim_debt_edges),
            },
            "debt_synthesis": {
                "D9_carried_debt_count": 29,
                "D10_transformed_debt_count": 29,
                "claimless_debt_disposition_count": 0,
                "transformation_counts": debt_ledger["transformation_counts"],
                "scientific_open_claim_count": len(categories["open"]),
                "verification_obligation_count": len(VERIFICATION_OBLIGATIONS),
            },
            "candidate_disposition": profile["candidate_profiles"],
            "realization_disposition": profile["realization_profiles"],
            "executable_profile_conformance_grammar": profile[
                "executable_profile_conformance_grammar"
            ],
            "unfolding_trajectory": profile["unfolding_trajectory"],
            "scientific_disposition": "accepted_bounded_lineage_local_profile_explicit_spec_authorization",
            "claim_ceiling": "bounded_design_level_lineage_local_profile_explicit_GRC9V4_architecture_with_exactly_one_A_or_C_and_exactly_one_CI_OS_RG2b_PC_or_CI_PC_runtime_identity_typed_lifecycle_and_unclosed_final_substrate_identity",
            "blocked_relabels": profile["selection_prohibitions"],
        },
        "control_contract": control_contract,
        "control_contract_count": len(control_contract),
        "verification": {
            "accepted_source_count": len(sources),
            "supporting_artifact_count": len(manifest),
            "supporting_artifact_digest_and_SHA_match": True,
            "claim_count": len(claims),
            "historical_claim_count": len(historical_claims),
            "total_claim_node_count": len(claims) + len(historical_claims),
            "reciprocal_typed_claim_debt_edge_count": len(claim_debt_edges),
            "claim_category_counts": topology["category_counts"],
            "D9_carried_debt_count": 29,
            "D10_transformed_debt_count": 29,
            "claimless_debt_disposition_count": 0,
            "debt_without_full_lineage_count": 0,
            "unknown_claim_reference_count": 0,
            "scope_exclusion_relabelled_as_resolution_count": 0,
            "verification_obligation_count": len(VERIFICATION_OBLIGATIONS),
            "unique_candidate_selected": False,
            "unique_realization_selected": False,
            "Candidate_B_rejected": False,
            "executable_complete_profile_count": len(executable_complete_profiles),
            "preclosure_substrate_provenance_audit_registered": True,
            "specification_authorized_after_human_acceptance": True,
            "specification_authorization_scope": "lineage_local_profile_explicit_GRC9V4",
            "final_substrate_identity_closed": False,
            "preclosure_substrate_provenance_audit_required": True,
            "specification_authorized": True,
            "implementation_authorized": False,
            "runtime_or_src_changed": False,
            "control_count": len(control_contract),
            "duplicate_control_id_count": 0,
            "human_acceptance_recorded": True,
            "absolute_machine_local_paths_in_record": False,
        },
        "authorization_effect": {
            "D10_complete_after_human_acceptance": True,
            "specification_authorized_after_human_acceptance": True,
            "specification_authorization_scope": "lineage_local_profile_explicit_GRC9V4",
            "final_substrate_identity_closed": False,
            "preclosure_substrate_provenance_audit_required": True,
            "specification_authorized": True,
            "implementation_plan_authorized": False,
            "implementation_authorized": False,
            "runtime_or_src_change_authorized": False,
        },
        "human_acceptance": {
            "accepted": True,
            "status": "accepted_bounded_2026-08-26",
            "scope": "lineage_local_profile_explicit_specification_authorization_only",
        },
        "decision_record_digest": "",
    }
    decision_path = DECISIONS / "D10DesignSynthesisAndSpecWritingDecision.json"
    write_json(decision_path, decision, "decision_record_digest")

    digest = decision["decision_record_digest"]
    lines = [
        "# D10 Design Synthesis And Specification Authorization Decision",
        "",
        "**Record:** `GRC9V4-CD-D10-v1`  ",
        "**Status:** `accepted_bounded`  ",
        f"**Decision digest:** `{digest}`",
        "",
        "## Governing Rule",
        "",
        "> Debt is not a checklist item; it is a stressed edge in an evolving claim topology.",
        "",
        "D10 therefore starts from proposed claims, activates only debts that bear on those claims, and records the resulting claim transformation. It never treats `open -> resolved` as a sufficient debt disposition.",
        "",
        "```text",
        "claim -> debt -> pressure/evidence -> claim transformation",
        "```",
        "",
        "The machine-enforced topology invariants are:",
        "",
        "```text",
        "no debt disposition without a claim-ledger disposition",
        "no normative D10 claim without tracing every debt that bears on it",
        "every claim-to-debt edge has a corresponding typed debt-to-claim edge",
        "```",
        "",
        "## Architecture Decision",
        "",
        "D10 selects a **lineage-local, profile-explicit GRC9V4 architecture**, not a uniquely preferred candidate or timing/history realization. The common normative layer is an interface and invariant contract for resource/state authority, current/geometry ownership, charge, complete-step ordering, lifecycle identity, typed events and migrations, representation/Hodge typing, and reduction surfaces. It does not flatten A and C into one universal current law: constitutive current and geometry laws come from the selected complete profile.",
        "",
        "Candidate A and Candidate C remain named optional revision-specific profile families. The present A law is explicitly normalized and nondimensional. CI, OS, RG2b, the current scalar-ZOH one-`tau_PC` PC realization, and the exact CI+PC gain-two composition remain named optional realizations. Every executable state, reset baseline, and snapshot binds exactly one candidate and one realization, selecting one of the ten currently admitted A/C by CI/OS/RG2b/PC/CI+PC complete identities. Migration and topology-event receipts instead bind the ordered source/target pair `(p-, p+)`, with equality when an event leaves the complete profile unchanged. An implementation may support any nonempty subset. This roster is complete for the initial lineage-local specification population, not exhaustive over future lawful V4 constitutive, realization, hybrid, or geometry profiles. Candidate B remains a reserved successor slot because its source-backed writer is still missing; it is neither executable, rejected, nor supplied by relabelling PC.",
        "",
        "## Claim Topology",
        "",
        f"The current topology contains `{len(categories['normative'])}` normative, `{len(categories['optional'])}` optional, `{len(categories['conditional'])}` conditional, `{len(categories['open'])}` open, and `{len(categories['negative'])}` negative claims. It also preserves `{len(historical_claims)}` historical predecessor claim nodes, one for every D9-carried debt.",
        "",
        "- **Normative:** common architecture and profile-governance contracts that the specification may encode.",
        "- **Optional:** bounded candidate and realization profiles that may be enabled without implying preference.",
        "- **Conditional:** stronger claims whose activation requires named evidence or a successor contract.",
        "- **Open:** B, formed runtime behavior, physical attribution, numeric comparison, and alternative normalization work.",
        "- **Negative:** no generic lossless history without lineage, no ranking supported by current evidence, no stability from constructibility, no inherited-core provenance for the present A completion, no unique A completion, and no PC-as-B relabel.",
        "",
        "Historical nodes retain the proposition or assumption under pressure. Every current claim-to-debt edge is typed reciprocally as supported, blocked, conditioned, routed, negative-successor, or successor evidence. `blocked_by` is temporally restricted to historical predecessor claims or current conditional/open claims that remain unearned; transformed normative, optional, and negative successors are supported rather than blocked. This closes the machine graph rather than leaving earlier propositions embedded only in prose.",
        "",
        "## Debt Transformations",
        "",
        f"All 29 debts carried by D9 are transformed with full predecessor lineage and explicit predecessor claim nodes. The transformation counts are `{json.dumps(debt_ledger['transformation_counts'], sort_keys=True)}`. No debt is dispositioned without typed supported, blocked, conditioned, routed, negative-successor, and successor claim relations where applicable.",
        "",
        "Important transformations include:",
        "",
        "- RG is narrowed to a bounded Lipschitz profile; C1 derivative and spectrum claims remain conditional.",
        "- A and C are admitted as optional constitutive profiles without universal nonabsorbability claims.",
        "- CI, OS, PC, and CI+PC design profiles remain admissible while endpoint, hysteresis, and stability claims route to evidence obligations.",
        "- the Hodge correction is confirmed for normative encoding, while the reference normalization is named rather than declared unique.",
        "- matched runtime discrimination is routed to verification; only the current-evidence ranking claim is negative.",
        "- the present A law is resolved negatively as inherited-core by provenance and as a unique completion, without claiming that no A-like law could ever be derived from core.",
        "- A is admitted as a normalized nondimensional profile; physical dimensionalization and cross-profile comparison require a future units/gauge/normalization bridge.",
        "- D9's bounded-domain A root uniqueness and stratum-local, uniquely self-consistent C root selection are preserved for CI and CI+PC.",
        "- B is routed to a source-backed writer successor and remains unrejected.",
        "- CI+PC is narrowed to the exact preregistered unit-plus-unit gain-two profile, not generalized into a unique composition law.",
        "",
        "## Unfolding Trajectory",
        "",
        "D10 freezes the currently justified claim topology and currently admitted specification population; it does not prescribe a fixed successor schedule. Normative claims may unfold into specification after acceptance. Conditional and open claims expose admissible successor directions and activate only when their stronger claim is attempted. Verification obligations gate the claims they name rather than forming a mandatory linear backlog. New constitutive, realization, hybrid, or geometry profiles enter only through explicit successor admission, a new complete-profile identity, and reopening of the earliest accepted contract whose authority, staging, state, geometry, accounting, or lifecycle semantics they change. Negative claims remain current boundaries unless new evidence transforms them. The substrate-provenance audit remains mandatory before final V4 substrate naming and closure.",
        "",
        "The ten current A/C by CI/OS/RG2b/PC/CI+PC identities are therefore the complete **currently admitted** executable set, not a completeness theorem over all lawful future V4 profiles. The current PC identity denotes specifically the scalar-ZOH, one-`tau_PC` persistent-`K_4` realization; a materially distinct persistent semigroup or carrier law requires successor admission rather than inheritance of the PC label.",
        "",
        "## Claim Ceiling",
        "",
        "D10 supports a bounded, design-level, lineage-local, profile-explicit GRC9V4 architecture with complete-profile conformance grammar and typed lifecycle/event closure. It does not support runtime implementation, formed-branch reachability, endpoint hysteresis, structural or temporal stability, continuation-spectrum identity, universal nonabsorbability, physical-channel attribution, physical dimensionalization of A, cross-profile capacity comparison, numeric ranking, architecture preference, or promotion to generic Graph GRC V4.",
        "",
        "## Pre-Closure Substrate Provenance",
        "",
        "`D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT` is registered as an obligation, not as unresolved D10 mathematics. Before final closure, every selected equation and contract must be classified as `9-port intrinsic`, `GRC9V3-derived but abstractable`, `generic graph-derived`, or `core/substrate-independent`. Promotion out of the GRC9 lineage requires an independent graph-generic derivation. D10 therefore authorizes only lineage-local specification writing; final substrate identity and naming remain open.",
        "",
        "## Disposition",
        "",
        "```text",
        "status = accepted_bounded",
        "human_acceptance = accepted_bounded_2026-08-26",
        "scientific_disposition = accepted_bounded_lineage_local_profile_explicit_spec_authorization",
        "specification_authorized_after_human_acceptance = true",
        "specification_authorized = true",
        "implementation_plan_authorized = false",
        "implementation_authorized = false",
        "runtime_or_src_changed = false",
        "```",
        "",
        "Bounded human acceptance authorizes lineage-local normative GRC9V4 specification writing. It does not authorize an implementation plan, implementation, runtime changes, final substrate naming, or graph-generic promotion. The pre-closure provenance audit remains mandatory before final substrate naming or graph-generic promotion.",
        "",
        "## Authoritative Artifacts",
        "",
        "- [`D10DesignSynthesisAndSpecWritingDecision.json`](./D10DesignSynthesisAndSpecWritingDecision.json)",
        "- [`D10NormativeClaimTopology.json`](./D10NormativeClaimTopology.json)",
        "- [`D10DebtClaimTransformationLedger.json`](./D10DebtClaimTransformationLedger.json)",
        "- [`D10SpecificationAuthorizationProfile.json`](./D10SpecificationAuthorizationProfile.json)",
    ]
    claim_roster = [
        "## Claim Roster",
        "",
        "| Class | Claim ID | Current claim |",
        "|---|---|---|",
        *[
            f"| `{row['claim_class']}` | `{row['claim_id']}` | {row['statement'].replace('_', ' ')} |"
            for row in claims
        ],
        "",
    ]
    historical_roster = [
        "## Historical Claim Nodes",
        "",
        "These nodes preserve the proposition under pressure before D10 transformed it. They are lineage nodes, not current claim-category members.",
        "",
        "| Historical claim | Debt edge | Prior proposition | Current successors |",
        "|---|---|---|---|",
        *[
            "| `{claim_id}` | `{debt_id}` | {statement} | {successors} |".format(
                claim_id=row["claim_id"],
                debt_id=row["transformed_by_debt_id"],
                statement=row["statement"].replace("_", " "),
                successors=", ".join(
                    f"`{claim_id}`" for claim_id in row["successor_claim_ids"]
                ),
            )
            for row in historical_claims
        ],
        "",
    ]
    debt_matrix = [
        "## Debt-To-Claim Matrix",
        "",
        "| Debt | Transformation | Supported claim | Blocked claim | Verification |",
        "|---|---|---|---|---|",
        *[
            "| `{debt_id}` | `{transformation}` | `{supported_claim_id}` | "
            "`{blocked_claim_id}` | {verification} |".format(
                debt_id=row["debt_id"],
                transformation=row["transformation"],
                supported_claim_id=row["supported_claim_id"],
                blocked_claim_id=row["blocked_claim_id"],
                verification=(
                    f"`{row['verification_obligation']}`"
                    if row["verification_obligation"]
                    else "none"
                ),
            )
            for row in debt_rows
        ],
        "",
    ]
    verification_roster = [
        "## Verification Obligations",
        "",
        "These obligations do not silently become unresolved D10 design mathematics. They gate the implementation, runtime, numerical, analysis, or pre-closure provenance claims named in the machine ledger.",
        "",
        "| Obligation | Kind | Scope |",
        "|---|---|---|",
        *[
            f"| `{row['obligation_id']}` | `{row['kind']}` | {row['scope'].replace('_', ' ')} |"
            for row in VERIFICATION_OBLIGATIONS
        ],
        "",
    ]
    claim_ceiling_index = lines.index("## Claim Ceiling")
    lines[claim_ceiling_index:claim_ceiling_index] = [
        *claim_roster,
        *historical_roster,
        *debt_matrix,
        *verification_roster,
    ]
    (DECISIONS / "D10DesignSynthesisAndSpecWritingDecision.md").write_text(
        "\n".join(lines) + "\n"
    )


if __name__ == "__main__":
    build()
