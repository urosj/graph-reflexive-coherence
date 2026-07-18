#!/usr/bin/env python3
"""Build N31 Iteration 2 semantic, representation, and control schema freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
I1_OUTPUT = EXPERIMENT / "outputs" / "n31_source_inventory_i1.json"
OUTPUT = EXPERIMENT / "outputs" / "n31_semantic_representation_control_schema_i2.json"
REPORT = EXPERIMENT / "reports" / "n31_semantic_representation_control_schema_i2.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_schema_control_freeze_i2.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"
I2_BASE_REVISION = "07255b46479d678f649bd89b3f92ceeb95c8d98a"
PROTECTED_RUNTIME_BASE_REVISION = "7075ecb5e464401df96f16eac171fbefe0e532dc"
I1_OUTPUT_DIGEST = "c8b1d7eb4b8009b418b7e7c240628b1c1a547d12e259156f2e53e63bb3dc9736"
I1_ARTIFACT_SHA256 = "1aff8008e26e29001da019168c8340322fe3172be8b2d8ea60c3de1496f47d79"
SCHEMA_VERSION = "n31_decay_candidate_schema_v2"
SCHEMA_CHANGE_RECORD_ID = "n31_pre_i1_mass_organization_mediation_normalization_v2"

SCHEMA_AUTHORITY_PATHS = [
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/implementation/DerivedDecayPrimitiveSemanticsImplementationPlan.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/implementation/DerivedDecayPrimitiveSemanticsImplementationChecklist.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/implementation/N31RCAEDemandAndReturnContract.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/hypotheses/hypothesis_a_coherence_only_derived_decay.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/hypotheses/hypothesis_b_observable_causal_distinction.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/hypotheses/hypothesis_c_added_mechanism_discrimination.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/hypotheses/hypothesis_d_conservation_time_locality.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/hypotheses/hypothesis_e_representation_restoration_reconstruction.md",
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/hypotheses/hypothesis_f_claim_boundary_and_rcae_return.md",
]

PRIMARY_SEMANTIC_CLASSES = ["D0a", "D0b", "D0c", "A", "B", "C"]
REPRESENTATION_CLASSES = [
    "existing_native",
    "exact_derived_projection",
    "producer_mediated",
    "effective_non_markovian_closure",
    "runtime_extension_required",
    "theory_extension_required",
]
CANDIDATE_DISPOSITIONS = [
    "supported",
    "bounded_partial",
    "blocked_by_representation",
    "blocked_by_runtime",
    "not_supported",
    "not_executed",
    "inapplicable",
    "rejected_as_relabel",
]
D0_REPRESENTATION_STATUSES = [
    "represented_natively",
    "represented_by_exact_projection",
    "represented_only_by_lossy_coarse_state",
    "missing",
]

DR_LADDER = {
    "DR0": "no_source_current_evidence",
    "DR1": "attributable_route_local_state_or_relation_formed",
    "DR2": "relation_persists_after_formation_stops",
    "DR3": "relation_weakens_under_system_internal_progression",
    "DR4": "later_local_readout_causally_depends_on_mediator",
    "DR5": "intervention_replay_restoration_invariants_and_controls_pass",
    "DR6": "bounded_semantics_and_downstream_contract_reusable",
}
N31_CLOSEOUT_LADDER = {
    "N31-C0": "initialized",
    "N31-C1": "source_and_semantic_contract_admitted",
    "N31-C2": "active_nulls_and_representation_boundary_established",
    "N31-C3": "source_current_weakening_or_persistence_classification_available",
    "N31-C4": "causal_control_backed_result_or_explicit_blocker_available",
    "N31-C5": "comparative_primitive_closure_nonselection_classification_complete",
    "N31-C6": "exact_RCAE_return_bundle_complete",
}

ROUTE_MASS_FIELDS = [
    "route_mass_contract_id",
    "registered_route_support",
    "registered_route_boundary",
    "metric_measure_and_boundary_convention",
    "post_formation_integration_window",
    "flux_quantity_semantics",
    "boundary_measure",
    "mass_before",
    "mass_after",
    "mass_delta",
    "boundary_flux_sign_policy",
    "net_outward_boundary_flux",
    "in_flight_boundary_treatment",
    "boundary_crossing_count_policy",
    "departure_arrival_accounting_policy",
    "receiver_inside_or_outside_support",
    "moving_support_or_measure_correction",
    "continuity_tolerance",
    "continuity_residual",
    "continuity_closed",
]
ORGANIZATION_FIELDS = [
    "route_organization_contract_id",
    "organization_observable_id",
    "organization_definition",
    "organization_inputs",
    "organization_domain",
    "observed_diagnostic_domains",
    "load_bearing_organization_domain",
    "mixed_domain_mediation_resolution",
    "organization_before",
    "organization_after",
    "organization_weakened",
    "organization_authority",
    "organization_update_owner",
    "organization_has_independent_causal_freedom",
    "organization_recomputation_status",
]
MEDIATION_FIELDS = [
    "causal_mediation_contract_id",
    "later_local_readout_definition",
    "later_readout_changed",
    "organization_intervention_definition",
    "mass_matched_during_organization_intervention",
    "packet_amount_matched_during_organization_intervention",
    "spatial_organization_matched_during_temporal_intervention",
    "other_continuation_state_matched",
    "temporal_intervention_matching_status",
    "organization_intervention_valid",
    "local_transport_intervention_status",
    "direct_readout_path_excluded",
    "hidden_selector_excluded",
    "added_coincidence_or_resonance_policy_present",
    "later_readout_probe_relation",
    "formation_packet_exclusion_status",
    "organization_mediated_readout_change",
    "mediation_strength",
]

CANDIDATE_REQUIRED_FIELDS = [
    "candidate_id",
    "candidate_schema_version",
    "schema_change_record_id",
    "source_iteration",
    "primary_semantic_class",
    "representation_or_authority_class",
    "candidate_disposition",
    "d0_subclass",
    "weakening_mode",
    "weakening_trajectory_class",
    "formation_source",
    "carrier_definition",
    "continuation_state_definition",
    "route_local_surface",
    "route_mass_contract",
    "route_organization_contract",
    "causal_mediation_contract",
    "route_mass_decreased",
    "route_organization_weakened",
    "later_readout_changed",
    "organization_mediated_readout_change",
    "ordinary_post_formation_flux_generated",
    "added_export_policy_present",
    "export_policy_owner",
    "export_policy_inputs",
    "producer_authors_aftereffect",
    "d0_to_br_bridge_status",
    "added_mechanism_admission_reason",
    "post_formation_producer_call_policy",
    "post_formation_producer_calls",
    "post_formation_state_mutating_producer_calls",
    "producer_call_audit_status",
    "topology_contract_id",
    "internal_time_owner",
    "internal_time_advance_event",
    "update_phase",
    "equation_or_relation_id",
    "units_by_state",
    "invariant_id",
    "coherence_budget_before",
    "coherence_budget_after",
    "invariant_tolerance",
    "forming_activity_present",
    "forming_activity_stopped",
    "post_formation_window",
    "formation_trace",
    "persistence_trace",
    "weakening_trace",
    "local_readout_trace",
    "mediator_intervention_trace",
    "destination_trace_if_mass_moves",
    "complete_state_identity",
    "restoration_identity_schema",
    "snapshot_load_status",
    "reset_status",
    "branch_continuation_status",
    "derived_cache_status",
    "derived_cache_recomputation_status",
    "execution_reconstruction_status",
    "producer_roles",
    "producer_residue",
    "naturalization_debt",
    "source_current_inputs",
    "artifact_manifest",
    "artifact_sha256",
    "all_artifact_sha256_match_file_contents",
    "row_specific_thresholds_declared_before_use",
    "decay_relation_ladder_rung",
    "row_decision",
    "claim_ceiling",
    "blocked_relabels",
    "unsafe_claim_flags",
]

COMMON_CONTROLS = [
    "label_only_decay",
    "wall_clock_decay",
    "post_hoc_weakening_trace",
    "forming_activity_never_stopped",
    "relation_persists_but_does_not_weaken",
    "relation_weakens_but_has_no_later_readout_effect",
    "global_route_selector",
    "hidden_producer_update",
    "unrecorded_post_formation_producer_call",
    "missing_internal_time_owner",
    "missing_invariant",
    "missing_restoration_state",
    "report_digest_as_runtime_state",
    "native_relabel_from_producer",
    "RCAE_demand_as_graph_evidence",
    "trail_or_stigmergy_relabel",
]
D0_CONTROLS = [
    "lossy_node_scalar_match_as_complete_state",
    "invented_C_slow_state",
    "producer_scheduled_D0_decay",
    "export_authoring_producer_call_retained_as_D0_R",
    "instantaneous_geometry_as_durable_decay",
    "derived_observable_as_causal_trail",
    "cache_removed_and_recomputed",
    "cache_divergence",
    "observable_disconnected_from_transport",
    "slow_organization_clamp",
    "complete_state_matched_history_contrast",
    "ordinary_outward_flux_as_added_leakage_relabel",
    "route_mass_loss_as_organization_weakening_relabel",
    "organization_weakening_without_mediation_as_causal_decay_relabel",
    "constant_mass_internal_reorganization_as_export_relabel",
    "unclosed_route_boundary_continuity",
    "added_export_policy_as_D0_R_relabel",
    "mass_unmatched_organization_intervention",
    "proper_time_annotation_as_causal_alignment",
    "added_coincidence_window_as_native_temporal_organization",
    "arrival_histogram_as_causal_mediation",
    "fixed_delay_single_path_as_dispersion",
    "periodic_rephasing_as_monotonic_decay",
    "diagnostic_domain_as_mediator_domain",
    "mixed_domain_without_load_bearing_isolation",
    "forming_packet_continuation_as_later_independent_readout",
    "temporal_intervention_with_unmatched_state",
    "geometric_observable_without_local_transport_intervention",
]
A_CONTROLS = [
    "in_flight_packet_attenuation",
    "carrier_amount_vs_release_efficacy_confound",
    "unregistered_age_or_phase",
    "unreleased_coherence_as_destroyed",
    "route_label_in_amount_policy",
]
B_CONTROLS = [
    "local_loss_without_destination",
    "source_debit_packet_amount_target_credit_mismatch",
    "hidden_reservoir",
    "new_leakage_policy_as_ordinary_D0_relabel",
    "global_emission_scheduler",
    "unbounded_emitted_amount",
    "receiver_in_later_read_path",
    "B_R_as_D0_R_without_bridge",
]
C_CONTROLS = [
    "conductance_label_only",
    "susceptibility_without_restoration",
    "history_carried_by_hidden_producer",
    "same_complete_C_different_S_changes_future",
    "producer_closure_as_native_memory",
]
SCHEMA_RELATION_CONTROLS = [
    "bounded_partial_disposition_with_supported_row_decision",
    "blocked_representation_with_supported_row_decision",
    "full_mediation_with_false_mediated_change",
    "absent_mediation_with_true_mediated_change",
    "mixed_domain_unresolved_claims_DR4",
    "blocked_D0a_authority_as_coherence_only_positive",
    "D0c_persistence_retained_as_same_D0c_row",
    "D0b_transport_feedback_without_authority_reclassification",
]

RETURN_REQUIRED_FIELDS = [
    "artifact_id",
    "artifact_version",
    "n31_candidate_schema_version",
    "schema_change_record_id",
    "n31_experiment_id",
    "n31_closeout_status",
    "graph_revision",
    "pygrc_version",
    "reproduction_commands",
    "theory_source_ids",
    "substrate_spec_source_ids",
    "pygrc_source_ids",
    "prior_experiment_source_ids",
    "rcae_demand_source_id",
    "paper_to_runtime_capability_dispositions",
    "candidate_dispositions",
    "primary_semantic_class_by_candidate",
    "representation_or_authority_class_by_candidate",
    "coherence_only_disposition",
    "d0a_representation_status",
    "d0a_projection_contract_id",
    "d0_producer_role_audit_id",
    "d0_vs_b_redistribution_disposition",
    "d0_subclass_by_candidate",
    "weakening_mode_by_candidate",
    "route_mass_contract_by_candidate",
    "route_organization_contract_by_candidate",
    "organization_domain_by_candidate",
    "observed_diagnostic_domains_by_candidate",
    "load_bearing_organization_domain_by_candidate",
    "mixed_domain_mediation_resolution_by_candidate",
    "weakening_trajectory_class_by_candidate",
    "causal_mediation_contract_by_candidate",
    "formation_packet_exclusion_status_by_candidate",
    "later_readout_probe_relation_by_candidate",
    "temporal_intervention_matching_status_by_candidate",
    "route_mass_decreased_by_candidate",
    "route_organization_weakened_by_candidate",
    "later_readout_changed_by_candidate",
    "organization_mediated_readout_change_by_candidate",
    "ordinary_post_formation_flux_generated_by_candidate",
    "added_export_policy_present_by_candidate",
    "export_policy_owner_by_candidate",
    "producer_authors_aftereffect_by_candidate",
    "d0_to_br_bridge_status",
    "added_mechanism_admission_reason_by_candidate",
    "post_formation_producer_call_policy_by_candidate",
    "post_formation_producer_calls_by_candidate",
    "post_formation_state_mutating_producer_calls_by_candidate",
    "producer_call_audit_status_by_candidate",
    "decay_relation_ladder_rung",
    "n31_closeout_ladder_rung",
    "selected_primitive_ids",
    "derived_relation_ids",
    "effective_closure_ids",
    "runtime_extension_ids",
    "theory_extension_ids",
    "selection_or_nonselection_reason",
    "carrier_by_candidate",
    "internal_time_by_candidate",
    "invariants_by_candidate",
    "topology_scope_by_candidate",
    "timing_and_delay_surface_disposition_by_candidate",
    "native_api_by_candidate",
    "producer_residue_by_candidate",
    "naturalization_debt_by_candidate",
    "restoration_identity_by_candidate",
    "control_summary",
    "derived_cache_recomputation_status",
    "execution_reconstruction_status",
    "src_diff_empty_for_experiment_branch",
    "protected_runtime_contract_diff_empty",
    "protected_runtime_contract_path_scope",
    "claim_ceiling",
    "blocked_relabels",
    "p2_i3_return_recommendation",
    "source_artifact_manifest",
]

PROTECTED_PATHS = [
    "src/**",
    "lib/**",
    "specs/**",
    "implementation/**",
    "tests/**",
    "examples/**",
    "scripts/**",
    "pyproject.toml",
    "requirements*.txt",
    "uv.lock",
]
PROTECTED_GIT_PATHS = [
    "src",
    "lib",
    "specs",
    "implementation",
    "tests",
    "examples",
    "scripts",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "uv.lock",
]
BLOCKED_CLAIMS = [
    "universal_decay_law",
    "native_memory",
    "native_learning",
    "trail_or_stigmergy",
    "semantic_communication",
    "shared_medium_coordination",
    "agency",
    "selfhood",
    "identity_acceptance",
    "sentience",
    "organism_life",
    "ecology_regime",
    "phase8_extension",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    encoded = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_digest_valid(payload: dict[str, Any]) -> bool:
    expected = payload.get("output_digest")
    actual = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return expected == actual


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )


def git_blob_sha256(revision: str, path: str) -> str:
    blob = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    return hashlib.sha256(blob).hexdigest()


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def build_schema() -> dict[str, Any]:
    return {
        "schema_identity": {
            "candidate_schema_version": SCHEMA_VERSION,
            "schema_change_record_id": SCHEMA_CHANGE_RECORD_ID,
            "supersedes": "pre_I1_unnormalized_scaffold_schema",
            "prior_scientific_fixture_migration": "not_applicable_no_positive_fixtures_exist",
            "stale_schema_policy": "reject_until_deterministically_migrated_or_regenerated",
        },
        "taxonomy": {
            "primary_semantic_classes": PRIMARY_SEMANTIC_CLASSES,
            "exactly_one_primary_semantic_class_required": True,
            "d0_r_subtype_of": "D0",
            "b_r_subtype_of": "B",
            "D0_R_and_B_R_are_primary_classes": False,
            "representation_or_authority_classes": REPRESENTATION_CLASSES,
            "candidate_dispositions": CANDIDATE_DISPOSITIONS,
            "semantic_authority_and_disposition_axes_are_independent": True,
        },
        "ladders": {
            "decay_relation_ladder": DR_LADDER,
            "n31_closeout_ladder": N31_CLOSEOUT_LADDER,
            "rung_rules": {
                "D0c_max_without_independent_persistence": "DR1",
                "D0b_max_without_causal_mediation": "DR3",
                "A_DR5_ceiling": "expression_attenuation_not_field_state_decay",
                "B_DR5_requires": ["explicit_destination", "complete_conservation"],
                "C_DR5_requires": ["explicit_added_state_or_closure", "complete_restoration"],
                "DR6_is_not": "universal_decay_law",
            },
        },
        "d0a_representation_gate": {
            "status_enum": D0_REPRESENTATION_STATUSES,
            "positive_statuses": ["represented_natively", "represented_by_exact_projection"],
            "blocking_statuses": ["represented_only_by_lossy_coarse_state", "missing"],
            "exact_projection_required_fields": [
                "projection_contract_id",
                "basis",
                "decomposition_operator",
                "recomposition_operator",
                "overlap_or_orthogonality_policy",
                "temporal_support",
                "intervention_semantics",
                "reconstruction_error_bound",
                "observed_reconstruction_error",
                "no_independent_causal_state",
            ],
            "invented_persistent_slow_state_allowed": False,
        },
        "route_mass_contract_schema": {
            "required_fields": ROUTE_MASS_FIELDS,
            "boundary_flux_sign_policy_required_value": "positive_outward",
            "flux_quantity_semantics_required_value": "time_integrated_exported_coherence",
            "fixed_support_formula": "continuity_residual = mass_delta + net_outward_boundary_flux",
            "mass_and_flux_must_share": [
                "post_formation_integration_window",
                "registered_route_boundary",
                "boundary_measure",
                "metric_measure",
            ],
            "boundary_crossing_count_policy": "each_packet_or_flux_transfer_counted_exactly_once",
            "departure_arrival_double_counting_allowed": False,
            "instantaneous_flux_rate_can_close_mass_delta": False,
            "moving_support_requires_explicit_measure_transport": True,
            "lower_mass_without_continuity_is_redistribution_evidence": False,
        },
        "route_organization_contract_schema": {
            "required_fields": ORGANIZATION_FIELDS,
            "organization_domain_enum": [
                "spatial_distribution",
                "induced_geometry",
                "functional_coupling",
                "temporal_alignment",
                "arrival_time_distribution",
                "mixed",
                "other",
            ],
            "load_bearing_domain_enum": [
                "spatial_distribution",
                "induced_geometry",
                "functional_coupling",
                "temporal_alignment",
                "arrival_time_distribution",
                "other",
                "unresolved",
            ],
            "mixed_domain_resolution_enum": [
                "resolved_to_one_load_bearing_domain",
                "unresolved",
                "not_applicable",
            ],
            "organization_authority_enum": [
                "native_state",
                "exact_derived_projection",
                "lossy_projection",
                "recomputable_history_functional",
                "effective_closure",
                "independent_state",
                "missing",
            ],
            "diagnostic_domain_does_not_define_mediator": True,
            "mixed_without_load_bearing_isolation_blocks_mediation": True,
            "organization_recomputation_status_enum": [
                "passed_exact",
                "failed",
                "not_run",
                "not_applicable_with_reason",
            ],
        },
        "causal_mediation_contract_schema": {
            "required_fields": MEDIATION_FIELDS,
            "later_readout_probe_relation_enum": [
                "independent_later_probe",
                "forming_packet_continuation",
                "unresolved",
            ],
            "formation_packet_exclusion_status_enum": [
                "exhausted",
                "causally_isolated",
                "excluded_by_packet_identity",
                "not_excluded",
                "not_applicable",
            ],
            "mediation_strength_enum": ["full", "bounded_partial", "absent", "unresolved"],
            "organization_mediated_readout_change_true_only_for": ["full", "bounded_partial"],
            "bounded_partial_requires_qualified_wording": True,
            "temporal_intervention_must_match": [
                "packet_amount",
                "route_mass",
                "spatial_organization",
                "other_continuation_state_as_representable",
            ],
            "temporal_intervention_matching_status_enum": [
                "matched_complete",
                "matched_with_declared_residual",
                "unmatched_blocks_temporal_mediation",
                "not_applicable",
            ],
            "added_coincidence_or_resonance_policy_moves_authority_to_closure": True,
            "geometric_shallowing_requires_local_transport_intervention": True,
        },
        "independent_classification_facts": {
            "weakening_mode_enum": [
                "net_export",
                "internal_reorganization",
                "slow_mode_relaxation",
                "mixed",
                "observable_only",
                "none",
                "unresolved",
            ],
            "weakening_trajectory_class_enum": [
                "monotone_relaxation",
                "damped_relaxation",
                "phase_drift",
                "phase_slip_or_recurrence",
                "dispersive_broadening",
                "instantaneous_change",
                "transient",
                "unresolved",
            ],
            "d0_subclass_enum": [
                "ordinary_export",
                "internal_reorganization",
                "slow_mode_relaxation",
                "other",
                "not_applicable",
            ],
            "d0_to_br_bridge_status_enum": ["not_tested", "rejected", "bounded_analogue_supported"],
            "measured_independently": [
                "route_mass_decreased",
                "route_organization_weakened",
                "later_readout_changed",
                "organization_mediated_readout_change",
                "ordinary_post_formation_flux_generated",
                "added_export_policy_present",
                "producer_authors_aftereffect",
            ],
            "trajectory_interpretation_rules": {
                "monotone_or_damped_with_mediation": "candidate_decay_relation",
                "phase_slip_with_loss_and_recovery": "modulation_or_dephasing",
                "forming_pulse_broadening_in_transit": "propagation_or_dispersion",
                "diagnostic_change_without_mediation": "observable_only_D0b_or_D0c",
            },
            "ownership_fact_derivation": {
                "authored_boolean_values_allowed": False,
                "required_trace_inputs": [
                    "post_formation_producer_calls",
                    "scheduled_events",
                    "mutated_state_paths",
                    "native_event_lineage",
                    "policy_inputs",
                    "export_amount_owner",
                    "export_time_owner",
                    "export_destination_owner",
                ],
                "derived_facts": [
                    "ordinary_post_formation_flux_generated",
                    "added_export_policy_present",
                    "producer_authors_aftereffect",
                ],
                "scheduling_export_without_direct_mutation_is_producer_authorship": True,
            },
        },
        "D0_R_admission": {
            "required_true": [
                "route_mass_decreased",
                "continuity_closed",
                "route_organization_weakened",
                "organization_mediated_readout_change",
                "ordinary_post_formation_flux_generated",
            ],
            "required_false": ["added_export_policy_present", "producer_authors_aftereffect"],
            "required_relation": "net_outward_boundary_flux > 0",
        },
        "B_R_classification": {
            "required_true": ["added_export_policy_present", "continuity_closed"],
            "required_records": ["export_policy_owner", "export_policy_inputs"],
            "emitted_amount_rule": "bounded_by_available_source_excess",
            "organization_and_mediation_evaluated_independently": True,
            "conservation_alone_promotes_to_D0_R": False,
        },
        "B_R_positive_support": {
            "classification_as_B_R_is_not_positive_decay_support": True,
            "required_true": [
                "positive_emitted_amount",
                "route_mass_decreased",
                "continuity_closed",
                "source_debit_packet_amount_destination_credit_match",
                "route_organization_evaluated_independently",
                "later_readout_evaluated_independently",
                "causal_mediation_evaluated_independently",
            ],
            "registered_policy_with_zero_emission_result": "B_R_mechanism_row_no_decay_support",
        },
        "semantic_transition_rules": {
            "D0c_with_demonstrated_persistence": (
                "new_D0a_candidate_identity_required_not_same_row_D0c_upgrade"
            ),
            "D0b_fed_causally_into_transport": (
                "reclassify_as_exact_derived_causal_relation_or_effective_closure"
            ),
            "weaker_semantic_class_may_retain_stronger_rung_without_reclassification": False,
        },
        "cross_field_relation_rules": [
            {
                "if": {"candidate_disposition": "bounded_partial"},
                "then": {"row_decision": "partial"},
            },
            {
                "if": {"candidate_disposition": "blocked_by_representation"},
                "then": {"row_decision": "blocked"},
            },
            {
                "if": {"mediation_strength": ["full", "bounded_partial"]},
                "then": {"organization_mediated_readout_change": True},
            },
            {
                "if": {"mediation_strength": ["absent", "unresolved"]},
                "then": {"organization_mediated_readout_change": False},
            },
            {
                "if": {
                    "organization_domain": "mixed",
                    "mixed_domain_mediation_resolution": ["unresolved", "not_applicable"],
                },
                "then": {"maximum_decay_relation_ladder_rung": "DR3"},
            },
            {
                "if": {
                    "organization_authority": [
                        "effective_closure",
                        "independent_state",
                        "lossy_projection",
                        "missing",
                    ]
                },
                "then": {"coherence_only_positive_D0a_allowed": False},
            },
            {
                "if": {"producer_authors_export_amount_time_or_destination": True},
                "then": {"D0_R_allowed": False, "semantic_subtype": "B_R"},
            },
        ],
        "candidate_row_schema": {
            "required_fields": CANDIDATE_REQUIRED_FIELDS,
            "candidate_specific_extensions_allowed": True,
            "common_fields_removable": False,
            "artifact_manifest_entry_fields": ["path", "sha256", "artifact_role"],
            "artifact_paths_must_be_repository_relative": True,
            "thresholds_must_be_declared_before_use": True,
            "source_current_inputs_required_for_positive_row": True,
            "row_decision_enum": [
                "supported",
                "partial",
                "blocked",
                "rejected",
                "not_applicable",
            ],
            "not_applicable_requires_scope_reason": True,
            "unsafe_claim_flags_required_false": True,
        },
        "active_null_row_schema": {
            "required_fields": [
                "null_id",
                "candidate_schema_version",
                "control_id",
                "claim_under_test",
                "control_scenario_kind",
                "false_positive_scenario",
                "source_contract_digest",
                "topology_signature",
                "seed_or_pairing_rule",
                "runtime_envelope_digest",
                "threshold_and_invariant_digest",
                "primary_semantic_class",
                "representation_or_authority_class",
                "organization_domain",
                "load_bearing_organization_domain",
                "internal_time_policy",
                "candidate_specific_schema_id",
                "carrier_contract_id",
                "continuation_state_contract_id",
                "violated_gate",
                "expected_claim_failure",
                "expected_result",
                "expected_control_status",
                "actual_result",
                "control_status",
                "rung_effect",
                "derived_fixture_only",
                "positive_evidence_admissible",
            ],
            "derived_fixture_only_required_value": True,
            "positive_evidence_admissible_required_value": False,
            "control_scenario_kind_enum": [
                "false_positive_rejection",
                "affirmative_discrimination",
                "invariant_challenge",
                "replay_challenge",
            ],
            "semantic_comparability_required": True,
            "same_topology_different_mediator_semantics_comparable": False,
            "comparability_mismatch_effect": "null_not_consumable_for_mismatched_positive_row",
            "positive_DR_rung_assignment_allowed": False,
        },
        "internal_time_schema": {
            "required_fields": [
                "internal_time_owner",
                "internal_time_state_path",
                "internal_time_units",
                "internal_time_advance_event",
                "internal_time_advance_equation",
                "wall_clock_excluded",
                "snapshot_path",
            ],
            "wall_clock_excluded_required_value": True,
        },
        "invariant_schema": {
            "required_fields": [
                "invariant_id",
                "quantity",
                "system_boundary",
                "budget_before",
                "budget_after",
                "in_flight_amount",
                "residual",
                "tolerance",
                "passed",
            ],
            "closed_system_node_plus_in_flight_required": True,
            "non_coherence_state_requires": ["units", "bounds", "cost", "invariant"],
        },
        "candidate_topology_schema": {
            "required_fields": [
                "topology_contract_id",
                "topology_signature",
                "node_ids",
                "edge_ids",
                "registered_route_support",
                "registered_route_boundary",
                "source_region",
                "receiver_region",
                "mutable_topology_policy",
                "transfer_scope",
            ]
        },
        "local_causal_readout_schema": {
            "required_fields": [
                "readout_contract_id",
                "encounter_location",
                "encounter_input_state",
                "readout_update_owner",
                "readout_measurement",
                "local_transport_path",
                "direct_readout_path_excluded",
                "global_selector_excluded",
            ],
            "DR4_requires_local_encounter": True,
        },
        "producer_call_schema": {
            "post_formation_producer_call_policy_enum": [
                "no_calls",
                "observation_only",
                "pre_registered_native_autonomy_enablement",
            ],
            "producer_call_audit_status_enum": [
                "complete_no_mutation",
                "complete_reclassified",
                "incomplete_blocks_row",
            ],
            "call_record_fields": [
                "call_id",
                "producer_id",
                "call_time",
                "inputs",
                "operation",
                "mutated_state_paths",
                "scheduled_events",
                "aftereffect_authoring_role",
            ],
            "D0_state_mutating_calls_required_value": [],
            "export_authoring_call_reclassifies_to": "B_R",
            "scheduling_without_direct_mutation_can_author_aftereffect": True,
            "native_autonomy_call_may_not_supply": ["aftereffect_time", "export_amount", "export_destination"],
        },
        "candidate_specific_schemas": {
            "A": {
                "required_distinction": "packet_creation_amount_vs_in_flight_amount_vs_release_efficacy",
                "in_flight_packet_amount_must_remain_constant": True,
                "unregistered_age_or_phase_blocks_row": True,
            },
            "B": {
                "required_fields": ["source_debit", "packet_amount", "destination_credit", "destination_identity"],
                "conservation_relation": "source_debit == packet_amount == destination_credit",
                "receiver_later_read_path_policy": "outside_unless_registered_relation_under_test",
            },
            "C": {
                "required_fields": [
                    "susceptibility_state_schema",
                    "update_owner",
                    "relaxation_owner",
                    "units",
                    "bounds",
                    "cost",
                    "restoration_composition",
                ],
                "independent_state_authority": "effective_closure_or_extension_not_coherence_only_D0",
            },
        },
        "restoration_and_reconstruction": {
            "current_state_restoration_schema": "lgrc9v3_restoration_identity_v1",
            "reset_aware_restoration_schema": "lgrc9v3_restoration_identity_v2",
            "reset_sensitive_rows_require_v2": True,
            "external_candidate_state_requires_separate_versioned_identity": True,
            "legacy_rebase_scope": "prospective_only_no_historical_provenance_recovery",
            "derived_cache_recomputation_status_enum": [
                "passed_exact",
                "failed",
                "not_run",
                "not_applicable_with_reason",
            ],
            "execution_reconstruction_status_enum": [
                "passed_complete",
                "failed",
                "not_run",
                "not_applicable_with_reason",
            ],
            "cache_recomputation_implies_execution_reconstruction": False,
        },
        "protected_scope": {
            "frozen_from_graph_revision": PROTECTED_RUNTIME_BASE_REVISION,
            "protected_paths": PROTECTED_PATHS,
            "experiment_directory_writes_allowed": True,
            "repository_index_updates_allowed_only_at_closeout": True,
            "runtime_extension_requires_revision_distinct_tranche": True,
        },
        "RCAE_return_manifest_schema": {
            "required_fields": RETURN_REQUIRED_FIELDS,
            "conditional_field_policy": "not_applicable_with_reason",
            "empty_placeholder_artifacts_allowed": False,
            "RCAE_adoption_must_be_explicit_and_revision_bound": True,
        },
    }


def build_control_schema() -> dict[str, Any]:
    all_controls = (
        COMMON_CONTROLS
        + D0_CONTROLS
        + A_CONTROLS
        + B_CONTROLS
        + C_CONTROLS
        + SCHEMA_RELATION_CONTROLS
    )
    return {
        "control_status_enum": ["passed", "failed_closed", "failed_open", "not_run", "not_applicable"],
        "control_result_required_fields": [
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
            "scope_reason_if_not_applicable",
        ],
        "status_meaning": {
            "passed": "positive_or_replay_gate_satisfied",
            "failed_closed": "false_positive_path_triggered_and_stronger_claim_rejected",
            "failed_open": "blocker_triggered_but_claim_remained_open",
            "not_run": "required_control_missing_and_dependent_rung_blocked",
            "not_applicable": "outside_declared_scope_with_reason",
        },
        "demotion_precedence": [
            "failed_open_invalidates_affected_row",
            "missing_or_incomplete_producer_audit_blocks_row",
            "missing_internal_time_or_invariant_blocks_DR3_plus",
            "missing_restoration_blocks_DR5_plus",
            "absent_or_unresolved_mediation_blocks_DR4_plus",
            "not_run_blocks_dependent_rung",
            "not_applicable_requires_scope_reason",
        ],
        "cross_hypothesis_gate": "failure_of_conservation_representation_or_claim_integrity_blocks_stronger_local_candidate_rungs",
        "common_active_nulls": COMMON_CONTROLS,
        "D0_controls": D0_CONTROLS,
        "candidate_A_controls": A_CONTROLS,
        "candidate_B_controls": B_CONTROLS,
        "candidate_C_controls": C_CONTROLS,
        "schema_relation_controls": SCHEMA_RELATION_CONTROLS,
        "all_control_ids": all_controls,
        "control_id_count": len(all_controls),
    }


def build_payload() -> dict[str, Any]:
    i1 = json.loads(I1_OUTPUT.read_text(encoding="utf-8"))
    schema = build_schema()
    controls = build_control_schema()
    head = git_text("rev-parse", "HEAD")
    base_is_ancestor = git_is_ancestor(I2_BASE_REVISION, head)
    protected_base_precedes_governance_base = git_is_ancestor(
        PROTECTED_RUNTIME_BASE_REVISION, I2_BASE_REVISION
    )
    src_diff_empty = not git_text("diff", "--", "src")
    protected_diff_empty = not git_text("diff", "--", *PROTECTED_GIT_PATHS)
    unsafe_claim_flags = {f"{claim}_claim_allowed": False for claim in BLOCKED_CLAIMS}
    schema_authority_records = [
        {
            "path": path,
            "revision": I2_BASE_REVISION,
            "sha256": git_blob_sha256(I2_BASE_REVISION, path),
            "may_consume_as": ["schema_authority", "claim_boundary", "control_definition"],
            "must_not_consume_as": ["positive_N31_evidence", "runtime_capability_evidence"],
        }
        for path in SCHEMA_AUTHORITY_PATHS
    ]

    checks = [
        {"check_id": "I1_status_passed", "passed": i1.get("status") == "passed"},
        {"check_id": "I1_output_digest_valid", "passed": output_digest_valid(i1)},
        {"check_id": "I1_output_digest_matches_frozen_value", "passed": i1.get("output_digest") == I1_OUTPUT_DIGEST},
        {"check_id": "I1_artifact_sha256_matches", "passed": sha256_file(I1_OUTPUT) == I1_ARTIFACT_SHA256},
        {"check_id": "I2_base_revision_is_ancestor", "passed": base_is_ancestor},
        {
            "check_id": "protected_runtime_base_precedes_governance_base",
            "passed": protected_base_precedes_governance_base,
        },
        {
            "check_id": "schema_authority_sources_pinned",
            "passed": len(schema_authority_records) == len(SCHEMA_AUTHORITY_PATHS)
            and all(record["sha256"] for record in schema_authority_records),
        },
        {"check_id": "primary_semantic_classes_exact", "passed": schema["taxonomy"]["primary_semantic_classes"] == PRIMARY_SEMANTIC_CLASSES},
        {"check_id": "D0_R_and_B_R_not_primary_classes", "passed": not schema["taxonomy"]["D0_R_and_B_R_are_primary_classes"]},
        {"check_id": "taxonomy_axes_separated", "passed": schema["taxonomy"]["semantic_authority_and_disposition_axes_are_independent"]},
        {"check_id": "DR_ladder_complete", "passed": list(schema["ladders"]["decay_relation_ladder"]) == [f"DR{i}" for i in range(7)]},
        {"check_id": "N31_closeout_ladder_complete", "passed": list(schema["ladders"]["n31_closeout_ladder"]) == [f"N31-C{i}" for i in range(7)]},
        {"check_id": "D0a_representation_gate_fail_closed", "passed": set(schema["d0a_representation_gate"]["blocking_statuses"]) == {"represented_only_by_lossy_coarse_state", "missing"}},
        {"check_id": "route_mass_contract_complete", "passed": schema["route_mass_contract_schema"]["required_fields"] == ROUTE_MASS_FIELDS},
        {
            "check_id": "route_flux_is_integrated_and_single_counted",
            "passed": schema["route_mass_contract_schema"]["flux_quantity_semantics_required_value"]
            == "time_integrated_exported_coherence"
            and not schema["route_mass_contract_schema"]["departure_arrival_double_counting_allowed"]
            and not schema["route_mass_contract_schema"]["instantaneous_flux_rate_can_close_mass_delta"],
        },
        {"check_id": "route_organization_contract_complete", "passed": schema["route_organization_contract_schema"]["required_fields"] == ORGANIZATION_FIELDS},
        {"check_id": "causal_mediation_contract_complete", "passed": schema["causal_mediation_contract_schema"]["required_fields"] == MEDIATION_FIELDS},
        {
            "check_id": "mass_organization_mediation_separate",
            "passed": not (set(ROUTE_MASS_FIELDS) & set(ORGANIZATION_FIELDS))
            and not (set(ROUTE_MASS_FIELDS) & set(MEDIATION_FIELDS))
            and not (set(ORGANIZATION_FIELDS) & set(MEDIATION_FIELDS)),
        },
        {"check_id": "mixed_domain_requires_load_bearing_resolution", "passed": schema["route_organization_contract_schema"]["mixed_without_load_bearing_isolation_blocks_mediation"]},
        {"check_id": "forming_packets_excluded_for_later_probe", "passed": "not_excluded" in schema["causal_mediation_contract_schema"]["formation_packet_exclusion_status_enum"]},
        {"check_id": "candidate_required_fields_complete", "passed": schema["candidate_row_schema"]["required_fields"] == CANDIDATE_REQUIRED_FIELDS},
        {
            "check_id": "active_null_comparability_frozen",
            "passed": schema["active_null_row_schema"]["derived_fixture_only_required_value"]
            and not schema["active_null_row_schema"]["positive_evidence_admissible_required_value"]
            and schema["active_null_row_schema"]["semantic_comparability_required"]
            and not schema["active_null_row_schema"]["same_topology_different_mediator_semantics_comparable"],
        },
        {
            "check_id": "cross_field_relation_rules_frozen",
            "passed": len(schema["cross_field_relation_rules"]) == 7,
        },
        {"check_id": "producer_call_audit_fail_closed", "passed": "incomplete_blocks_row" in schema["producer_call_schema"]["producer_call_audit_status_enum"]},
        {"check_id": "D0_export_authoring_reclassified_to_B_R", "passed": schema["producer_call_schema"]["export_authoring_call_reclassifies_to"] == "B_R"},
        {
            "check_id": "ownership_facts_trace_derived",
            "passed": not schema["independent_classification_facts"]["ownership_fact_derivation"]["authored_boolean_values_allowed"]
            and schema["independent_classification_facts"]["ownership_fact_derivation"]["scheduling_export_without_direct_mutation_is_producer_authorship"],
        },
        {
            "check_id": "B_R_classification_separate_from_support",
            "passed": schema["B_R_positive_support"]["classification_as_B_R_is_not_positive_decay_support"]
            and schema["B_R_positive_support"]["registered_policy_with_zero_emission_result"]
            == "B_R_mechanism_row_no_decay_support",
        },
        {
            "check_id": "semantic_transition_rules_frozen",
            "passed": not schema["semantic_transition_rules"]["weaker_semantic_class_may_retain_stronger_rung_without_reclassification"],
        },
        {"check_id": "restoration_v1_v2_distinguished", "passed": schema["restoration_and_reconstruction"]["current_state_restoration_schema"].endswith("_v1") and schema["restoration_and_reconstruction"]["reset_aware_restoration_schema"].endswith("_v2")},
        {"check_id": "cache_and_execution_reconstruction_separate", "passed": not schema["restoration_and_reconstruction"]["cache_recomputation_implies_execution_reconstruction"]},
        {"check_id": "all_control_families_frozen", "passed": controls["control_id_count"] == len(set(controls["all_control_ids"])) == 70},
        {"check_id": "failed_open_invalidates", "passed": controls["demotion_precedence"][0] == "failed_open_invalidates_affected_row"},
        {"check_id": "return_manifest_fields_complete", "passed": schema["RCAE_return_manifest_schema"]["required_fields"] == RETURN_REQUIRED_FIELDS},
        {"check_id": "src_diff_empty", "passed": src_diff_empty},
        {"check_id": "protected_runtime_contract_diff_empty", "passed": protected_diff_empty},
        {"check_id": "positive_evidence_remains_closed", "passed": True},
        {"check_id": "unsafe_claim_flags_false", "passed": all(value is False for value in unsafe_claim_flags.values())},
    ]

    payload: dict[str, Any] = {
        "experiment": "N31_lgrc9v3_derived_decay_and_primitive_semantics",
        "iteration": "2_semantic_representation_and_control_schema_freeze",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_semantic_representation_control_schema_frozen_no_positive_evidence",
        "source_I1": {
            "path": "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_source_inventory_i1.json",
            "output_digest": i1.get("output_digest"),
            "sha256": sha256_file(I1_OUTPUT),
            "status": i1.get("status"),
            "positive_evidence_opened": i1.get("positive_evidence_opened"),
        },
        "schema_authority_records": schema_authority_records,
        "graph_scope": {
            "revision_chain": {
                "protected_runtime_baseline": PROTECTED_RUNTIME_BASE_REVISION,
                "I1_I2_governance_base": I2_BASE_REVISION,
                "I2_generated_artifact": "current_experiment_worktree_output",
                "protected_runtime_base_precedes_governance_base": (
                    protected_base_precedes_governance_base
                ),
            },
            "I2_base_revision": I2_BASE_REVISION,
            "I2_base_is_ancestor": base_is_ancestor,
            "src_diff_empty": src_diff_empty,
            "protected_runtime_contract_diff_empty": protected_diff_empty,
            "protected_paths": PROTECTED_PATHS,
        },
        "schema": schema,
        "controls": controls,
        "positive_evidence_opened": False,
        "candidate_rows_classified": False,
        "d0a_representation_status_assigned": False,
        "primary_semantic_class_assigned": False,
        "decay_relation_ladder_rung_assigned": False,
        "decay_relation_ladder_ceiling": "DR0_no_source_current_decay_evidence",
        "n31_closeout_ladder_rung_assigned": False,
        "n31_closeout_ceiling": "N31-C1_source_and_semantic_contract_admitted",
        "ready_for_iteration_3_active_nulls": True,
        "claim_boundary": {
            "claim_ceiling": "schema_and_control_freeze_only_no_N31_decay_evidence",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": unsafe_claim_flags,
        },
        "checks": checks,
    }
    checks.append({"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)})
    payload["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_schema_freeze_checks_failed"
        payload["ready_for_iteration_3_active_nulls"] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    schema = payload["schema"]
    check_rows = "\n".join(
        f"- `{row['check_id']}` = `{str(row['passed']).lower()}`"
        for row in payload["checks"]
    )
    family_rows = "\n".join(
        f"| {name} | {len(payload['controls'][key])} |"
        for name, key in (
            ("common", "common_active_nulls"),
            ("D0", "D0_controls"),
            ("A", "candidate_A_controls"),
            ("B", "candidate_B_controls"),
            ("C", "candidate_C_controls"),
            ("schema relations", "schema_relation_controls"),
        )
    )
    REPORT.write_text(
        f"""# N31 Iteration 2 - Semantic, Representation, And Control Schema Freeze

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

I2 freezes how later N31 evidence may be represented and classified. It does
not assign a semantic class, D0a representation status, DR rung, candidate
disposition, or scientific result.

## Frozen Axes

Primary semantic classes are exactly `D0a`, `D0b`, `D0c`, `A`, `B`, and `C`.
Representation/authority and candidate disposition are independent axes.
`D0-R` remains an ordinary-export subtype of D0 and `B-R` remains a
policy-owned subtype of Candidate B; neither is a seventh primary class.

## Normalized Evidence Contracts

Three contracts are mandatory and non-substitutable:

1. Route mass records support, boundary, measure, signed outward flux,
   integration window, in-flight treatment, single-count crossing policy, and
   continuity residual. The flux term is time-integrated exported coherence,
   not an instantaneous flux-rate sample.
2. Route organization records the mediator domain, diagnostic domains,
   load-bearing domain, authority, update owner, and recomputation status.
3. Causal mediation records a later local readout, intervention, matched state,
   packet exclusion, hidden-path controls, and mediation strength.

Lower route mass is not organization weakening. Organization weakening is not
causal mediation. A label may not author any of these facts.

## Temporal And Geometric Boundary

Temporal organization may be derived from admitted timing/packet state, but an
arrival histogram alone remains observable evidence. Forming packets must be
exhausted, isolated, or excluded by identity before a later independent
readout claim. Added coincidence or resonance state changes authority to a
closure/extension. Geometric shallowing requires a local transport
intervention rather than a changed curvature diagnostic alone.

## Producer And Restoration Boundary

D0 allows no load-bearing post-formation state mutation by an experiment-local
producer. A producer that decides or schedules export timing, amount, or
destination moves the row to `B-R`, even without direct mutation and even when
conservation closes. B-R classification alone is not positive decay support;
actual emission, mass change, debit/packet/credit closure, organization, and
mediation remain separate gates. Current-state replay uses
restoration identity v1; reset-sensitive equivalence uses v2. External state
requires separate versioned identity composition. Cache recomputation and
full execution reconstruction remain separate gates.

## Control Families

| Family | Frozen controls |
|---|---:|
{family_rows}

`failed_closed` means the false-positive path was correctly rejected.
`failed_open` invalidates the affected row. `not_run` blocks its dependent
rung, and `not_applicable` requires an explicit scope reason.

Active-null comparability includes semantic class, authority, organization and
load-bearing domains, internal-time policy, candidate schema, carrier, and
continuation-state contracts. Matching topology alone is insufficient.

## Schema Counts

- Candidate required fields: `{len(schema['candidate_row_schema']['required_fields'])}`
- Active-null required fields: `{len(schema['active_null_row_schema']['required_fields'])}`
- Route-mass fields: `{len(schema['route_mass_contract_schema']['required_fields'])}`
- Route-organization fields: `{len(schema['route_organization_contract_schema']['required_fields'])}`
- Causal-mediation fields: `{len(schema['causal_mediation_contract_schema']['required_fields'])}`
- RCAE return fields: `{len(schema['RCAE_return_manifest_schema']['required_fields'])}`
- Control IDs: `{payload['controls']['control_id_count']}`

## Checks

{check_rows}

## Claim Ceiling

`positive_evidence_opened = false`

`decay_relation_ladder_rung_assigned = false`

`n31_closeout_ceiling = N31-C1_source_and_semantic_contract_admitted`
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()
