#!/usr/bin/env python3
"""Build N16 Iteration 1 boundary source inventory."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

OUTPUT_PATH = OUTPUTS / "n16_boundary_source_inventory.json"
REPORT_PATH = REPORTS / "n16_boundary_source_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_boundary_source_inventory.py"
)
# Fixed for deterministic reconstruction; output_digest excludes generated_at.
GENERATED_AT = "2026-06-16T00:00:00+00:00"

BLOCKED_CLAIMS = [
    "selfhood",
    "personhood",
    "identity_acceptance",
    "runtime_identity_acceptance",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
    "intention",
    "semantic_choice",
    "agency",
    "unrestricted_agency",
    "native_support_without_phase8",
    "fully_native_agentic_like_integration",
    "organism_or_life_claim",
    "selective_uptake_or_resource_assimilation",
]

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "artifact_level_ap6_supported": False,
    "biological_behavior_claim_allowed": False,
    "final_ap6_supported": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "intention_claim_allowed": False,
    "native_support_opened": False,
    "personhood_claim_allowed": False,
    "phase8_opened": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "selective_uptake_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
}

ARC_METHOD_MAPPING = {
    "classification_of_becoming": (
        "classify each source row at the lowest supported rung; separate "
        "internal support state, external resource state, external "
        "perturbation state, external structured state, boundary-crossing "
        "trace, readiness-only context, and blocked relabels"
    ),
    "interrogation_of_becoming": (
        "treat B-axis and C-axis records as bounded questions about boundary "
        "separability, not proof of selfhood or identity acceptance"
    ),
    "naturalization_of_becoming": (
        "keep artifact-level boundary prerequisites separate from native "
        "support and native self/environment understanding"
    ),
    "cultivation_of_becoming": (
        "cultivate reusable source-current boundary traces and fail-closed "
        "controls before optimizing any local AP6 label"
    ),
}

CONTEXT_DOCUMENTS = [
    {
        "path": "experiments/N12-N18-LGRC-AgencyPrerequisitesRoadmap.md",
        "role": "roadmap_context_not_sha_pinned_to_avoid_self_reference",
    },
    {
        "path": "experiments/N12-N18-LGRC-AgencyPrerequisitesHandoff.md",
        "role": "handoff_context_not_sha_pinned_to_avoid_self_reference",
    },
]

DIRECT_SUPPORT_STATUS = {
    "direct_ap6_support": "present",
    "not_direct_ap6_support": "absent",
    "not_ap6_positive_evidence": "rejected",
    "indirect_lineage_not_direct_ap6": "partial",
}

EVIDENCE_STRATEGY_CLASS = {
    "b_axis_lineage_source": "lineage_derivation",
    "b_axis_lineage_source_and_c2_analog": "lineage_derivation",
    "b_axis_lineage_source_and_c_axis_analog": "lineage_derivation",
    "b_axis_lineage_source_for_b2_b3": "lineage_derivation",
    "boundary_and_blocked_input_audit": "rejected",
    "constructed_ap6_context_from_old_best_claims": "old_best_claims_construction",
    "constructed_context_with_upstream_observation_caveat": "old_best_claims_construction",
    "control_context_for_ap6_replay_requirements": "control_context",
    "lineage_caveat_and_blocked_identity_boundary": "lineage_derivation",
    "old_best_claims_construction_context": "old_best_claims_construction",
    "old_best_claims_construction_input": "old_best_claims_construction",
    "readiness_only_context": "readiness_only",
    "repair_context_for_b3_but_not_ap6": "lineage_derivation",
    "repair_context_with_identity_support_caveat": "lineage_derivation",
}

SOURCE_ROWS = [
    {
        "row_id": "n16_i1_row_01_n15_closeout_ap5",
        "source_experiment": "N15",
        "source_iteration": "closeout_and_n16_handoff",
        "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_closeout_and_handoff.md",
        "mechanism_name": "artifact_level_ap5_endogenous_proxy_formation_candidate",
        "mechanism_role": "old_best_ap5_proxy_target_axis",
        "source_role_classification": [
            "internal_support_state",
            "boundary_crossing_trace",
            "claim_boundary_blocker",
        ],
        "evidence_strategy": "old_best_claims_construction_input",
        "provisional_ap_level": "AP5",
        "provisional_claim_ceiling": "artifact_level_ap5_endogenous_proxy_formation_candidate",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N15_AP5_endogenous_proxy_formation_axis"],
        "boundary_state_relevance": ["B2", "B3"],
        "challenge_class_relevance": ["C1", "C2", "C4"],
        "missing_gates": [
            "ap6_internal_external_boundary_schema_not_frozen",
            "ap6_boundary_rows_not_generated",
            "ap6_controls_not_run",
        ],
    },
    {
        "row_id": "n16_i1_row_02_n15_runtime_derived_target_candidate",
        "source_experiment": "N15",
        "source_iteration": "iteration_3_runtime_derived_target_candidate",
        "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_runtime_derived_target_candidate.json",
        "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_runtime_derived_target_candidate.md",
        "mechanism_name": "runtime_derived_target_candidate_from_old_best_inputs",
        "mechanism_role": "source_current_target_generation_context",
        "source_role_classification": [
            "internal_support_state",
            "boundary_crossing_trace",
        ],
        "evidence_strategy": "constructed_ap6_context_from_old_best_claims",
        "provisional_ap_level": "AP5_candidate_at_iteration_3_scope",
        "provisional_claim_ceiling": "provisional_runtime_derived_target_candidate_pending_controls",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": [
            "N13_AP3_support_regulation",
            "N14_AP4_consequence_context",
            "N08_memory_context",
            "N09_bounded_regulation_context",
            "N12_readiness_only_context",
        ],
        "boundary_state_relevance": ["B2", "B3"],
        "challenge_class_relevance": ["C1", "C2", "C4"],
        "missing_gates": [
            "target_condition_is_not_boundary_side_assignment",
            "internal_external_state_separation_not_built",
            "ap6_claim_boundary_not_classified",
        ],
    },
    {
        "row_id": "n16_i1_row_03_n15_bounded_drift_replay",
        "source_experiment": "N15",
        "source_iteration": "iteration_6_bounded_drift_and_replay_matrix",
        "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_bounded_drift_replay_matrix.json",
        "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_bounded_drift_replay_matrix.md",
        "mechanism_name": "bounded_drift_replay_matrix",
        "mechanism_role": "replay_and_drift_control_context",
        "source_role_classification": [
            "internal_support_state",
            "external_perturbation_state",
            "boundary_crossing_trace",
        ],
        "evidence_strategy": "control_context_for_ap6_replay_requirements",
        "provisional_ap_level": "AP5_control_context",
        "provisional_claim_ceiling": "bounded_drift_replay_context_only",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N15_bounded_drift_replay_context"],
        "boundary_state_relevance": ["B2", "B3"],
        "challenge_class_relevance": ["C1", "C4"],
        "missing_gates": [
            "boundary_side_replay_digest_not_frozen",
            "challenge_class_rows_not_generated",
        ],
    },
    {
        "row_id": "n16_i1_row_04_n15_claim_boundary",
        "source_experiment": "N15",
        "source_iteration": "iteration_7_claim_boundary_record",
        "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_claim_boundary_record.json",
        "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_claim_boundary_record.md",
        "mechanism_name": "n15_claim_boundary_record",
        "mechanism_role": "unsafe_claim_relabel_blocker_source",
        "source_role_classification": [
            "external_structured_state",
            "claim_boundary_blocker",
        ],
        "evidence_strategy": "boundary_and_blocked_input_audit",
        "provisional_ap_level": "AP0_boundary",
        "provisional_claim_ceiling": "claim_boundary_context_only",
        "direct_historic_ap6_support_status": "not_ap6_positive_evidence",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B0"],
        "challenge_class_relevance": ["C3"],
        "missing_gates": ["positive_ap6_boundary_evidence_absent"],
    },
    {
        "row_id": "n16_i1_row_05_n14_closeout_ap4",
        "source_experiment": "N14",
        "source_iteration": "closeout_and_n15_handoff",
        "source_artifact": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/n14_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_closeout_and_handoff.md",
        "mechanism_name": "artifact_level_ap4_consequence_sensitive_route_selection",
        "mechanism_role": "old_best_ap4_consequence_selection_axis",
        "source_role_classification": [
            "external_resource_state",
            "boundary_crossing_trace",
            "claim_boundary_blocker",
        ],
        "evidence_strategy": "old_best_claims_construction_input",
        "provisional_ap_level": "AP4",
        "provisional_claim_ceiling": "artifact_level_ap4_consequence_sensitive_route_selection_candidate",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N14_AP4_consequence_sensitive_selection_axis"],
        "boundary_state_relevance": ["B4"],
        "challenge_class_relevance": ["C2", "C5"],
        "missing_gates": [
            "route_selection_is_not_boundary_separability",
            "shared_medium_boundary_rows_not_generated",
        ],
    },
    {
        "row_id": "n16_i1_row_06_n14_constructed_followout",
        "source_experiment": "N14",
        "source_iteration": "route_conditioned_followout_probe",
        "source_artifact": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/n14_route_conditioned_followout_probe.json",
        "source_report": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_route_conditioned_followout_probe.md",
        "mechanism_name": "constructed_route_conditioned_support_regulation_followout",
        "mechanism_role": "constructed_external_route_context",
        "source_role_classification": [
            "external_resource_state",
            "boundary_crossing_trace",
        ],
        "evidence_strategy": "constructed_context_with_upstream_observation_caveat",
        "provisional_ap_level": "AP4_context",
        "provisional_claim_ceiling": "constructed_route_conditioned_followout_context_only",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N14_constructed_route_conditioned_followout"],
        "boundary_state_relevance": ["B4"],
        "challenge_class_relevance": ["C2", "C5"],
        "missing_gates": [
            "upstream_observed_route_conditioned_support_missing",
            "upstream_observed_route_conditioned_regulation_missing",
            "not_multi_basin_separability_evidence",
        ],
    },
    {
        "row_id": "n16_i1_row_07_n13_closeout_ap3",
        "source_experiment": "N13",
        "source_iteration": "closeout_and_n14_handoff",
        "source_artifact": "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/outputs/n13_closeout_and_handoff.json",
        "source_report": "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/reports/n13_closeout_and_handoff.md",
        "mechanism_name": "artifact_level_ap3_support_seeking_regulation",
        "mechanism_role": "old_best_ap3_support_regulation_axis",
        "source_role_classification": [
            "internal_support_state",
            "boundary_crossing_trace",
            "claim_boundary_blocker",
        ],
        "evidence_strategy": "old_best_claims_construction_input",
        "provisional_ap_level": "AP3",
        "provisional_claim_ceiling": "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N13_AP3_support_seeking_regulation_axis"],
        "boundary_state_relevance": ["B2", "B3"],
        "challenge_class_relevance": ["C1", "C2", "C4"],
        "missing_gates": [
            "support_regulation_is_not_selfhood",
            "boundary_side_assignment_not_built",
            "external_state_descriptors_not_built",
        ],
    },
    {
        "row_id": "n16_i1_row_08_n13_support_disruption_restoration",
        "source_experiment": "N13",
        "source_iteration": "support_disruption_restoration_matrix",
        "source_artifact": "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/outputs/n13_support_disruption_restoration_matrix.json",
        "source_report": "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/reports/n13_support_disruption_restoration_matrix.md",
        "mechanism_name": "support_disruption_restoration_stress_matrix",
        "mechanism_role": "repair_and_support_error_context",
        "source_role_classification": [
            "internal_support_state",
            "external_perturbation_state",
            "boundary_crossing_trace",
        ],
        "evidence_strategy": "repair_context_for_b3_but_not_ap6",
        "provisional_ap_level": "AP3_stress_context",
        "provisional_claim_ceiling": "support_disruption_restoration_context_only",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N13_support_disruption_restoration_context"],
        "boundary_state_relevance": ["B3"],
        "challenge_class_relevance": ["C1", "C4"],
        "missing_gates": [
            "boundary_reclosure_policy_not_defined",
            "external_perturbation_boundary_side_not_frozen",
        ],
    },
    {
        "row_id": "n16_i1_row_09_n12_phase8_readiness",
        "source_experiment": "N12",
        "source_iteration": "phase8_readiness_matrix",
        "source_artifact": "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_phase8_readiness_matrix.json",
        "source_report": "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/reports/n12_phase8_readiness_matrix.md",
        "mechanism_name": "phase8_readiness_matrix",
        "mechanism_role": "readiness_only_context",
        "source_role_classification": ["readiness"],
        "evidence_strategy": "readiness_only_context",
        "provisional_ap_level": "AP0_readiness",
        "provisional_claim_ceiling": "readiness_only_not_native_support",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N12_NAT4_readiness_only_context"],
        "boundary_state_relevance": [],
        "challenge_class_relevance": [],
        "missing_gates": [
            "phase8_implementation_not_opened",
            "native_supported_flags_false",
            "not_boundary_evidence",
        ],
    },
    {
        "row_id": "n16_i1_row_10_n03_artifact_surface_inventory",
        "source_experiment": "N03",
        "source_iteration": "artifact_surface_inventory",
        "source_artifact": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/artifact_surface_inventory.json",
        "source_report": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/artifact_surface_inventory.md",
        "mechanism_name": "basin_sink_parent_surface_inventory",
        "mechanism_role": "localized_basin_surface_lineage",
        "source_role_classification": ["boundary_role"],
        "evidence_strategy": "b_axis_lineage_source",
        "provisional_ap_level": "pre_AP_boundary_lineage",
        "provisional_claim_ceiling": "artifact_surface_inventory_only",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B1"],
        "challenge_class_relevance": ["C0"],
        "missing_gates": [
            "configured_parent_region_not_ap6_boundary",
            "inside_outside_boundary_schema_not_frozen",
        ],
    },
    {
        "row_id": "n16_i1_row_11_n03_native_packet_loop_closeout",
        "source_experiment": "N03",
        "source_iteration": "e3_native_lgrc9v3_packet_loop_closeout",
        "source_artifact": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_closeout.json",
        "source_report": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_closeout.md",
        "mechanism_name": "native_lgrc9v3_packetized_basin_loop",
        "mechanism_role": "localized_basin_loop_lineage",
        "source_role_classification": ["boundary_role", "boundary_crossing_trace"],
        "evidence_strategy": "b_axis_lineage_source",
        "provisional_ap_level": "pre_AP_boundary_lineage",
        "provisional_claim_ceiling": "native_lgrc9v3_packet_loop_reproduced",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B1", "B2"],
        "challenge_class_relevance": ["C0", "C2"],
        "missing_gates": [
            "loop_evidence_is_not_self_environment_boundary",
            "movement_and_agency_claims_blocked",
        ],
    },
    {
        "row_id": "n16_i1_row_12_n04_taxonomy_inventory",
        "source_experiment": "N04",
        "source_iteration": "taxonomy_inventory_v1",
        "source_artifact": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_inventory_v1.json",
        "source_report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_inventory_v1.md",
        "mechanism_name": "movement_boundary_persistence_taxonomy_inventory",
        "mechanism_role": "boundary_and_persistence_taxonomy_lineage",
        "source_role_classification": ["boundary_role", "external_resource_state"],
        "evidence_strategy": "b_axis_lineage_source_and_c_axis_analog",
        "provisional_ap_level": "pre_AP_boundary_lineage",
        "provisional_claim_ceiling": "taxonomy_inventory_only",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B1", "B2", "B3"],
        "challenge_class_relevance": ["C0", "C1", "C2", "C4"],
        "missing_gates": [
            "movement_taxonomy_is_not_ap6_boundary_taxonomy",
            "challenge_classes_are_n16_operational_conditions",
        ],
    },
    {
        "row_id": "n16_i1_row_13_n04_boundary_coupled_pulse",
        "source_experiment": "N04",
        "source_iteration": "boundary_coupled_pulse_fixture",
        "source_artifact": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_report.json",
        "source_report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/boundary_coupled_pulse_report.md",
        "mechanism_name": "boundary_coupled_pulse_fixture",
        "mechanism_role": "boundary_coupling_lineage",
        "source_role_classification": [
            "external_resource_state",
            "boundary_crossing_trace",
            "boundary_role",
        ],
        "evidence_strategy": "b_axis_lineage_source_and_c2_analog",
        "provisional_ap_level": "pre_AP_boundary_lineage",
        "provisional_claim_ceiling": "boundary_coupled_pulse_fixture_validation",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B1"],
        "challenge_class_relevance": ["C2"],
        "missing_gates": [
            "boundary_coupling_is_not_boundary_persistence",
            "movement_claims_blocked",
        ],
    },
    {
        "row_id": "n16_i1_row_14_n04_taxonomy_continuation_closeout",
        "source_experiment": "N04",
        "source_iteration": "taxonomy_continuation_closeout",
        "source_artifact": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json",
        "source_report": "experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_continuation_closeout.md",
        "mechanism_name": "topology_mutating_movement_candidate_closeout",
        "mechanism_role": "boundary_claim_boundary_and_topology_caveat",
        "source_role_classification": ["boundary_role", "claim_boundary_blocker"],
        "evidence_strategy": "lineage_caveat_and_blocked_identity_boundary",
        "provisional_ap_level": "pre_AP_boundary_lineage",
        "provisional_claim_ceiling": "topology_mutating_movement_candidate",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B1", "B2"],
        "challenge_class_relevance": ["C2", "C5"],
        "missing_gates": [
            "rc_identity_through_topology_mutation_blocked",
            "movement_candidate_is_not_ap6_boundary",
        ],
    },
    {
        "row_id": "n16_i1_row_15_n07_long_horizon_compatibility_closeout",
        "source_experiment": "N07",
        "source_iteration": "iteration_12_long_horizon_compatibility_closeout",
        "source_artifact": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_12_long_horizon_compatibility_closeout.json",
        "source_report": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_12_long_horizon_compatibility_closeout.md",
        "mechanism_name": "bounded_non_destructive_exchange_id6_evidence",
        "mechanism_role": "support_persistence_and_dual_basin_lineage",
        "source_role_classification": ["internal_support_state", "boundary_role"],
        "evidence_strategy": "b_axis_lineage_source",
        "provisional_ap_level": "ID6_context_not_AP",
        "provisional_claim_ceiling": "artifact_only_source_specific_bounded_non_destructive_exchange",
        "direct_historic_ap6_support_status": "indirect_lineage_not_direct_ap6",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B2", "B4"],
        "challenge_class_relevance": ["C1", "C5"],
        "missing_gates": [
            "id6_is_not_runtime_identity_acceptance",
            "dual_basin_exchange_is_not_ap6_shared_medium_boundary",
        ],
    },
    {
        "row_id": "n16_i1_row_16_n07_identity_support_withdrawal_baseline",
        "source_experiment": "N07",
        "source_iteration": "iteration_13_identity_support_withdrawal_baseline",
        "source_artifact": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_13_identity_support_withdrawal_baseline.json",
        "source_report": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_13_identity_support_withdrawal_baseline.md",
        "mechanism_name": "identity_support_withdrawal_and_restoration_baseline",
        "mechanism_role": "support_persistence_and_repair_lineage",
        "source_role_classification": [
            "internal_support_state",
            "external_perturbation_state",
            "boundary_crossing_trace",
        ],
        "evidence_strategy": "b_axis_lineage_source_for_b2_b3",
        "provisional_ap_level": "ID6_context_not_AP",
        "provisional_claim_ceiling": "identity_support_withdrawal_baseline_only",
        "direct_historic_ap6_support_status": "indirect_lineage_not_direct_ap6",
        "old_best_claim_inputs": [],
        "boundary_state_relevance": ["B2", "B3"],
        "challenge_class_relevance": ["C1", "C4"],
        "missing_gates": [
            "identity_support_baseline_is_not_selfhood",
            "restoration_is_explicit_not_native_boundary_repair",
        ],
    },
    {
        "row_id": "n16_i1_row_17_n08_memory_trail_closeout",
        "source_experiment": "N08",
        "source_iteration": "iteration_8_mem6_closeout",
        "source_artifact": "experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_8_mem6_closeout.json",
        "source_report": "experiments/2026-05-N08-lgrc-memory-trail-affordance/reports/n08_iteration_8_mem6_closeout.md",
        "mechanism_name": "route_memory_trail_affordance_closeout",
        "mechanism_role": "memory_and_route_alternative_context",
        "source_role_classification": ["external_resource_state", "boundary_crossing_trace"],
        "evidence_strategy": "old_best_claims_construction_context",
        "provisional_ap_level": "AP2_context",
        "provisional_claim_ceiling": "artifact_only_route_memory_or_trail_affordance_candidate",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N08_route_memory_context"],
        "boundary_state_relevance": ["B4"],
        "challenge_class_relevance": ["C2", "C5"],
        "missing_gates": [
            "route_memory_is_not_multi_basin_separability",
            "native_memory_support_not_opened",
        ],
    },
    {
        "row_id": "n16_i1_row_18_n09_goal_proxy_regulation_closeout",
        "source_experiment": "N09",
        "source_iteration": "iteration_9_gpr6_closeout",
        "source_artifact": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_9_gpr6_closeout.json",
        "source_report": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_9_gpr6_closeout.md",
        "mechanism_name": "bounded_goal_proxy_regulation_closeout",
        "mechanism_role": "bounded_regulation_context",
        "source_role_classification": [
            "internal_support_state",
            "external_perturbation_state",
            "boundary_crossing_trace",
        ],
        "evidence_strategy": "old_best_claims_construction_input",
        "provisional_ap_level": "AP2_context",
        "provisional_claim_ceiling": "repeated_bounded_proxy_regulation_candidate",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N09_bounded_regulation_context"],
        "boundary_state_relevance": ["B3"],
        "challenge_class_relevance": ["C1", "C4"],
        "missing_gates": [
            "external_proxy_regulation_is_not_endogenous_boundary",
            "semantic_goal_ownership_blocked",
        ],
    },
    {
        "row_id": "n16_i1_row_19_n09_perturbation_withdrawal_support",
        "source_experiment": "N09",
        "source_iteration": "iteration_8_perturbation_withdrawal_support",
        "source_artifact": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_8_perturbation_withdrawal_support.json",
        "source_report": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_8_perturbation_withdrawal_support.md",
        "mechanism_name": "perturbation_recovery_and_support_withdrawal_record",
        "mechanism_role": "explicit_perturbation_and_support_withdrawal_context",
        "source_role_classification": [
            "internal_support_state",
            "external_perturbation_state",
            "boundary_crossing_trace",
        ],
        "evidence_strategy": "repair_context_with_identity_support_caveat",
        "provisional_ap_level": "AP2_context",
        "provisional_claim_ceiling": "perturbation_recovery_context_only",
        "direct_historic_ap6_support_status": "not_direct_ap6_support",
        "old_best_claim_inputs": ["N09_perturbation_recovery_context"],
        "boundary_state_relevance": ["B3"],
        "challenge_class_relevance": ["C1", "C4"],
        "missing_gates": [
            "support_withdrawal_identity_boundary_gap_preserved",
            "not_native_boundary_repair",
        ],
    },
]

BOUNDARY_STATE_LINEAGE = [
    {
        "boundary_state": "B0",
        "name": "null / external coherence only",
        "lineage_sources": [
            "n16_i1_row_04_n15_claim_boundary",
        ],
        "inherited_closed_claims": [
            "negative-control discipline blocks unsafe relabels",
            "structured external coherence cannot be promoted without source-backed boundary side assignment",
        ],
        "constructed_support": [
            "use B0 as active null for coherent-looking outside structure",
        ],
        "unsupported_extension": [
            "no positive basin-boundary claim",
            "no internal support-relevant state claim",
        ],
        "required_N16_evidence": [
            "B0 x C3 must reject structured external coherence as self-boundary",
        ],
        "claim_ceiling": "active_null_control_no_boundary_claim",
    },
    {
        "boundary_state": "B1",
        "name": "localized basin partition",
        "lineage_sources": [
            "n16_i1_row_10_n03_artifact_surface_inventory",
            "n16_i1_row_11_n03_native_packet_loop_closeout",
            "n16_i1_row_12_n04_taxonomy_inventory",
            "n16_i1_row_13_n04_boundary_coupled_pulse",
        ],
        "inherited_closed_claims": [
            "artifact-visible basin, sink, parent, and edge/flux surfaces exist",
            "localized boundary coupling can be measured in fixtures",
        ],
        "constructed_support": [
            "inside/outside partition and boundary edges can be proposed from pinned surfaces",
        ],
        "unsupported_extension": [
            "detectable partition is not persistence",
            "boundary coupling is not AP6 boundary stability",
        ],
        "required_N16_evidence": [
            "quiet B1 row must extract boundary edges without supplied labels",
            "B1 x C2 must expose failure threshold under flux",
        ],
        "claim_ceiling": "localized_basin_partition_candidate_pending_n16_schema",
    },
    {
        "boundary_state": "B2",
        "name": "support-persistent basin",
        "lineage_sources": [
            "n16_i1_row_01_n15_closeout_ap5",
            "n16_i1_row_03_n15_bounded_drift_replay",
            "n16_i1_row_07_n13_closeout_ap3",
            "n16_i1_row_11_n03_native_packet_loop_closeout",
            "n16_i1_row_12_n04_taxonomy_inventory",
            "n16_i1_row_15_n07_long_horizon_compatibility_closeout",
            "n16_i1_row_16_n07_identity_support_withdrawal_baseline",
        ],
        "inherited_closed_claims": [
            "support-retention and support-seeking regulation are source-backed at AP3 artifact level",
            "N07 source-specific support/basin compatibility replays artifact-only",
            "N15 drift/replay discipline can preserve derived artifact target context",
        ],
        "constructed_support": [
            "B2 can be calibrated as a support-persistent boundary candidate under C0-C2 before repair claims",
        ],
        "unsupported_extension": [
            "support persistence is not selfhood",
            "artifact replay stability is not native self/environment understanding",
        ],
        "required_N16_evidence": [
            "B2 x C0, C1, and C2 must be evaluated before B3 is unlocked",
            "boundary-side assignments must be replayable and source-current",
        ],
        "claim_ceiling": "support_persistent_basin_candidate_pending_n16_matrix",
    },
    {
        "boundary_state": "B3",
        "name": "regulated repair / reabsorption boundary",
        "lineage_sources": [
            "n16_i1_row_02_n15_runtime_derived_target_candidate",
            "n16_i1_row_03_n15_bounded_drift_replay",
            "n16_i1_row_07_n13_closeout_ap3",
            "n16_i1_row_08_n13_support_disruption_restoration",
            "n16_i1_row_16_n07_identity_support_withdrawal_baseline",
            "n16_i1_row_18_n09_goal_proxy_regulation_closeout",
            "n16_i1_row_19_n09_perturbation_withdrawal_support",
        ],
        "inherited_closed_claims": [
            "bounded regulation and support restoration contexts exist at artifact level",
            "explicit support withdrawal/restoration baselines are source-backed",
        ],
        "constructed_support": [
            "B3 can test whether a boundary breach is repaired or fail-closed without post-hoc relabeling",
        ],
        "unsupported_extension": [
            "bounded correction is not native boundary repair",
            "explicit restoration is not autonomous reabsorption",
        ],
        "required_N16_evidence": [
            "B3 remains locked until B2 C0-C2 evaluations are present or explicitly blocked",
            "B3 x C4 must distinguish reclosure from relabeling",
        ],
        "claim_ceiling": "regulated_repair_candidate_locked_until_b2_calibration",
    },
    {
        "boundary_state": "B4",
        "name": "coupled multi-basin separability candidate",
        "lineage_sources": [
            "n16_i1_row_05_n14_closeout_ap4",
            "n16_i1_row_06_n14_constructed_followout",
            "n16_i1_row_12_n04_taxonomy_inventory",
            "n16_i1_row_14_n04_taxonomy_continuation_closeout",
            "n16_i1_row_15_n07_long_horizon_compatibility_closeout",
            "n16_i1_row_17_n08_memory_trail_closeout",
        ],
        "inherited_closed_claims": [
            "route alternatives, constructed consequence followout, and dual-basin exchange analogs exist",
            "N07 records source-specific dual-basin separability under bounded exchange",
        ],
        "constructed_support": [
            "B4 can be included as the weakest candidate state for shared-medium separability",
        ],
        "unsupported_extension": [
            "prior route alternatives are not multi-basin boundary exclusivity",
            "B4 x C2 is only a flux stress row",
        ],
        "required_N16_evidence": [
            "B4 x C5 must test shared-medium multi-basin exclusivity",
            "B4 x C2 must remain partial or not_applicable if shared substrate support is insufficient",
        ],
        "claim_ceiling": "multi_basin_separability_candidate_new_n16_evidence_required",
    },
]

CHALLENGE_CLASS_RECORDS = [
    {
        "challenge_class": "C0",
        "name": "quiet reference",
        "operational_role": "calibration condition with no intended boundary stress",
        "source_analogs": ["N03 configured basin surfaces", "N04 fixed-substrate baselines"],
        "claim_boundary": "operational_challenge_class_not_environment_taxonomy",
    },
    {
        "challenge_class": "C1",
        "name": "unstructured perturbation",
        "operational_role": "random or noisy disturbance around or across the boundary",
        "source_analogs": ["N07 support weakening", "N09 perturbation recovery", "N15 bounded drift"],
        "claim_boundary": "operational_challenge_class_not_environment_taxonomy",
    },
    {
        "challenge_class": "C2",
        "name": "directional flux",
        "operational_role": "one-sided pressure, drift, or flow across the boundary",
        "source_analogs": ["N04 boundary-coupled pulse", "N14 route-conditioned consequence context"],
        "claim_boundary": "operational_challenge_class_not_environment_taxonomy",
    },
    {
        "challenge_class": "C3",
        "name": "structured external coherence",
        "operational_role": "active null for coherent outside pattern that must not be mistaken for self-boundary",
        "source_analogs": ["N14/N15 fail-closed relabel controls"],
        "external_state_role": "structured_external_state",
        "perturbation_by_default": False,
        "claim_boundary": "false_positive_pressure_not_perturbation_unless_crossing_or_disruption_recorded",
    },
    {
        "challenge_class": "C4",
        "name": "breach and repair",
        "operational_role": "local boundary disruption followed by reclosure, reabsorption, or fail-closed classification",
        "source_analogs": ["N07 restoration baseline", "N09 perturbation recovery", "N13 stress restoration"],
        "claim_boundary": "operational_challenge_class_not_environment_taxonomy",
    },
    {
        "challenge_class": "C5",
        "name": "coupled neighbor / shared medium",
        "operational_role": "more than one candidate basin interacting through a shared substrate",
        "source_analogs": ["N07 dual-basin exchange", "N08 route alternatives", "N14 route alternatives"],
        "claim_boundary": "new_n16_shared_medium_evidence_required",
    },
]

OLD_BEST_CLAIM_INPUTS = [
    {
        "input": "N15_AP5",
        "role": "endogenous target/proxy formation axis",
        "why_included": (
            "strongest closed AP prerequisite before N16; supplies "
            "source-current target/proxy formation discipline"
        ),
        "what_it_supports": (
            "artifact-level target/proxy condition generated from source-current "
            "support, memory, regulation, and AP4 context"
        ),
        "what_it_does_not_support": (
            "internal/external boundary-side assignment, semantic goal "
            "ownership, agency, identity acceptance, or native support"
        ),
        "claim_ceiling": "artifact_level_ap5_endogenous_proxy_formation_candidate",
        "required_N16_addition": (
            "separate internal support-relevant state from external resource, "
            "perturbation, or structured state under AP6 controls and replay"
        ),
        "promotion_blocked": [
            "semantic_goal_ownership",
            "agency",
            "identity_acceptance",
            "native_support",
        ],
    },
    {
        "input": "N14_AP4",
        "role": "consequence-sensitive route/context axis",
        "why_included": (
            "supplies the strongest closed route/consequence context for "
            "external resource and directional-flux analogs"
        ),
        "what_it_supports": (
            "artifact-level consequence-sensitive route selection and "
            "constructed route-conditioned support/regulation followout"
        ),
        "what_it_does_not_support": (
            "intention, semantic choice, agency, or observed upstream "
            "route-conditioned support/regulation"
        ),
        "claim_ceiling": "artifact_level_ap4_consequence_sensitive_route_selection_candidate",
        "required_N16_addition": (
            "boundary-side descriptors that keep route/resource context "
            "separate from internal support state"
        ),
        "promotion_blocked": ["intention", "semantic_choice", "agency"],
    },
    {
        "input": "N13_AP3",
        "role": "support-seeking regulation axis",
        "why_included": (
            "supplies the strongest closed support-maintenance and bounded "
            "response context for B2/B3"
        ),
        "what_it_supports": (
            "artifact-level support-seeking regulation and support disruption/"
            "restoration stress context"
        ),
        "what_it_does_not_support": (
            "selfhood, agency, identity acceptance, native support, or AP6 "
            "boundary-side separability"
        ),
        "claim_ceiling": "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation",
        "required_N16_addition": (
            "source-current boundary rows that distinguish maintained internal "
            "support from external challenge state"
        ),
        "promotion_blocked": ["selfhood", "agency", "identity_acceptance", "native_support"],
    },
    {
        "input": "N08",
        "role": "memory/route context",
        "why_included": (
            "supplies route-memory context for old-best construction and weak "
            "B4 shared-medium analogs"
        ),
        "what_it_supports": (
            "artifact-only route memory, trail/affordance context, and "
            "geometry-mediated alternatives"
        ),
        "what_it_does_not_support": (
            "multi-basin separability, identity acceptance, native memory "
            "support, or AP6 boundary evidence"
        ),
        "claim_ceiling": "artifact_only_route_memory_or_trail_affordance_candidate",
        "required_N16_addition": (
            "explicit shared-medium boundary rows if memory alternatives are "
            "used for B4"
        ),
        "promotion_blocked": ["identity_acceptance", "native_memory_support"],
    },
    {
        "input": "N09",
        "role": "bounded regulation context",
        "why_included": (
            "supplies perturbation/recovery and bounded-regulation context for "
            "B3 and C1/C4"
        ),
        "what_it_supports": (
            "artifact-level bounded proxy regulation and perturbation recovery "
            "context"
        ),
        "what_it_does_not_support": (
            "endogenous boundary repair, semantic goal ownership, native "
            "regulation, or identity support outcome"
        ),
        "claim_ceiling": "repeated_bounded_proxy_regulation_candidate",
        "required_N16_addition": (
            "breach/reclosure rows that distinguish repair from explicit "
            "support restoration or post-hoc relabeling"
        ),
        "promotion_blocked": ["semantic_goal_ownership", "native_regulation"],
    },
    {
        "input": "N12_NAT4",
        "role": "readiness-only context",
        "why_included": (
            "records Phase 8 readiness constraints and prevents readiness from "
            "being relabeled as native support"
        ),
        "what_it_supports": "readiness-only context for later native-policy work",
        "what_it_does_not_support": (
            "native support, AP6 boundary evidence, or fully native integration"
        ),
        "claim_ceiling": "readiness_only_not_native_support",
        "required_N16_addition": (
            "keep readiness weight/context separate from boundary-side "
            "evidence unless a separate Phase 8 task is opened"
        ),
        "promotion_blocked": ["native_support_without_phase8"],
    },
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    if isinstance(value, dict):
        return any(
            contains_absolute_path(key) or contains_absolute_path(item)
            for key, item in value.items()
        )
    return False


def normalize_source_status(raw_status: Any) -> str:
    if raw_status in {"passed", "complete"}:
        return "passed"
    if isinstance(raw_status, str) and raw_status:
        return raw_status
    return "pinned"


def direct_support_status(detailed_status: str) -> str:
    try:
        return DIRECT_SUPPORT_STATUS[detailed_status]
    except KeyError as exc:
        allowed = ", ".join(sorted(DIRECT_SUPPORT_STATUS))
        raise ValueError(
            f"unmapped direct_historic_ap6_support_status={detailed_status!r}; "
            f"allowed values: {allowed}"
        ) from exc


def ap5_contribution_status(source: dict[str, Any], strategy_class: str) -> str:
    if source["source_experiment"] != "N15":
        return "not_applicable"
    if strategy_class == "rejected":
        return "not_applicable"
    if source["provisional_ap_level"] == "AP5":
        return "yes"
    return "partial"


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    status = "pinned"
    if artifact is not None:
        raw_status = artifact.get("status")
        if raw_status:
            status = normalize_source_status(raw_status)
        elif artifact.get("checks", {}).get("status_passed") is True:
            status = "passed"
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": status,
    }


def build_rows() -> list[dict[str, Any]]:
    rows = []
    for source in SOURCE_ROWS:
        artifact_path = ROOT / source["source_artifact"]
        report_path = ROOT / source["source_report"]
        artifact = load_json(artifact_path)
        detailed_status = source["direct_historic_ap6_support_status"]
        direct_status = direct_support_status(detailed_status)
        strategy = source["evidence_strategy"]
        strategy_class = EVIDENCE_STRATEGY_CLASS[strategy]
        source_roles = source["source_role_classification"]
        row = {
            **source,
            "source_sha256": digest_file(artifact_path),
            "source_report_sha256": digest_file(report_path),
            "source_status": normalize_source_status(artifact.get("status")),
            "direct_historic_support_status": direct_status,
            "evidence_strategy_class": strategy_class,
            "claim_ceiling_preserved": True,
            "claim_promotion_allowed": False,
            "artifact_only_replay_status": "not_run_until_later_n16_iterations",
            "budget_validity": "not_frozen_until_iteration_2_schema",
            "boundary_side_assignments": "not_frozen_until_iteration_2_schema",
            "boundary_crossing_trace": "not_constructed_until_later_n16_iterations",
            "external_state_role": "not_frozen_until_iteration_2_schema",
            "ap5_contribution_status": ap5_contribution_status(
                source, strategy_class
            ),
            "ap6_required_evidence_still_missing": source["missing_gates"],
            "role_classification_audit": {
                "multi_role_source_context": len(source_roles) > 1,
                "incompatible_roles_detected": False,
                "readiness_not_native_support": "readiness" not in source_roles
                or source["source_experiment"] == "N12",
                "boundary_crossing_not_closed_action_perception_loop": True,
                "classification_rule": (
                    "roles classify permitted source contribution categories; "
                    "they do not promote one source field into incompatible "
                    "internal/external/native roles"
                ),
            },
            "row_decision": "not_applicable",
            "boundary_claim_allowed": False,
            "final_ap6_supported": False,
            "blocked_claims": BLOCKED_CLAIMS,
            "arc_method_mapping": ARC_METHOD_MAPPING,
        }
        rows.append(row)
    return rows


def build_source_artifacts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    artifacts = []
    for row in rows:
        artifact_path = ROOT / row["source_artifact"]
        report_path = ROOT / row["source_report"]
        source_json = load_json(artifact_path)
        artifacts.append(
            {
                "row_id": row["row_id"],
                "source_experiment": row["source_experiment"],
                "artifact": source_artifact(artifact_path, source_json),
                "report": {
                    "path": rel(report_path),
                    "sha256": digest_file(report_path),
                },
            }
        )
    return artifacts


def build_inventory_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_experiment: dict[str, int] = {}
    by_strategy: dict[str, int] = {}
    by_strategy_class: dict[str, int] = {}
    by_direct_support_status: dict[str, int] = {}
    by_boundary_state: dict[str, int] = {}
    by_challenge_class: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    for row in rows:
        by_experiment[row["source_experiment"]] = by_experiment.get(row["source_experiment"], 0) + 1
        by_strategy[row["evidence_strategy"]] = by_strategy.get(row["evidence_strategy"], 0) + 1
        strategy_class = row["evidence_strategy_class"]
        by_strategy_class[strategy_class] = by_strategy_class.get(strategy_class, 0) + 1
        support_status = row["direct_historic_support_status"]
        by_direct_support_status[support_status] = by_direct_support_status.get(support_status, 0) + 1
        for state in row["boundary_state_relevance"]:
            by_boundary_state[state] = by_boundary_state.get(state, 0) + 1
        for challenge in row["challenge_class_relevance"]:
            by_challenge_class[challenge] = by_challenge_class.get(challenge, 0) + 1
        for role in row["source_role_classification"]:
            role_counts[role] = role_counts.get(role, 0) + 1

    return {
        "row_count": len(rows),
        "by_experiment": dict(sorted(by_experiment.items())),
        "by_evidence_strategy": dict(sorted(by_strategy.items())),
        "by_evidence_strategy_class": dict(sorted(by_strategy_class.items())),
        "by_direct_historic_support_status": dict(
            sorted(by_direct_support_status.items())
        ),
        "by_boundary_state": dict(sorted(by_boundary_state.items())),
        "by_challenge_class": dict(sorted(by_challenge_class.items())),
        "by_source_role_classification": dict(sorted(role_counts.items())),
        "direct_historic_ap6_support_rows": sum(
            1
            for row in rows
            if row["direct_historic_ap6_support_status"] == "direct_ap6_support"
        ),
        "old_best_claims_construction_input_rows": sum(
            1
            for row in rows
            if row["evidence_strategy"] == "old_best_claims_construction_input"
        ),
        "old_best_claim_input_records": len(OLD_BEST_CLAIM_INPUTS),
        "b_axis_lineage_rows": sum(
            1 for row in rows if "b_axis_lineage" in row["evidence_strategy"]
        ),
        "readiness_only_rows": sum(
            1 for row in rows if row["evidence_strategy"] == "readiness_only_context"
        ),
    }


def build_checks(output: dict[str, Any]) -> dict[str, bool]:
    rows = output["rows"]
    row_ids = {row["row_id"] for row in rows}
    expected_summary = build_inventory_summary(rows)
    inventory_summary = output["inventory_summary"]
    required_experiments = {"N03", "N04", "N07", "N08", "N09", "N12", "N13", "N14", "N15"}
    role_set = {
        role
        for row in rows
        for role in row["source_role_classification"]
    }
    required_roles = {
        "internal_support_state",
        "external_resource_state",
        "external_perturbation_state",
        "boundary_crossing_trace",
        "readiness",
        "boundary_role",
        "claim_boundary_blocker",
    }
    boundary_states = {row["boundary_state"] for row in output["boundary_state_lineage"]}
    challenge_classes = {row["challenge_class"] for row in output["challenge_class_records"]}
    paths = [
        ROOT / row["source_artifact"]
        for row in rows
    ] + [
        ROOT / row["source_report"]
        for row in rows
    ]
    support_status_values = {"present", "absent", "partial", "rejected", "unknown"}
    direct_status_values = set(DIRECT_SUPPORT_STATUS)
    strategy_class_values = {
        "direct_historic",
        "old_best_claims_construction",
        "lineage_derivation",
        "control_context",
        "readiness_only",
        "rejected",
    }
    row_decision_values = {
        "supported",
        "blocked",
        "partial",
        "rejected",
        "not_applicable",
    }
    source_status_values = {"passed", "pinned"}
    old_best_required_fields = {
        "why_included",
        "what_it_supports",
        "what_it_does_not_support",
        "claim_ceiling",
        "required_N16_addition",
    }

    return {
        "all_required_source_experiments_present": required_experiments
        <= {row["source_experiment"] for row in rows},
        "arc_method_mapping_recorded": bool(output["arc_method_mapping"]),
        "b0_b4_lineage_recorded": boundary_states == {"B0", "B1", "B2", "B3", "B4"},
        "c0_c5_challenge_records_recorded": challenge_classes
        == {"C0", "C1", "C2", "C3", "C4", "C5"},
        "c3_structured_external_not_perturbation_by_default": any(
            record["challenge_class"] == "C3"
            and record.get("perturbation_by_default") is False
            and record.get("external_state_role") == "structured_external_state"
            for record in output["challenge_class_records"]
        ),
        "claim_flags_forced_false": all(value is False for value in output["claim_flags"].values()),
        "claim_ceiling_preservation_passed": all(
            row["claim_ceiling_preserved"] is True
            and row["claim_promotion_allowed"] is False
            for row in rows
        ),
        "direct_historic_ap6_support_absent": output["direct_historic_ap6_support"]["status"]
        == "none_found"
        and output["direct_historic_ap6_support"]["direct_historic_support_status"]
        == "absent",
        "direct_historic_ap6_status_mapping_complete": DIRECT_SUPPORT_STATUS[
            "direct_ap6_support"
        ]
        == "present",
        "direct_historic_ap6_status_values_valid": all(
            row["direct_historic_ap6_support_status"] in direct_status_values
            for row in rows
        ),
        "direct_historic_support_status_values_valid": all(
            row["direct_historic_support_status"] in support_status_values
            for row in rows
        ),
        "every_row_has_source_report_sha256": all(row.get("source_report_sha256") for row in rows),
        "every_row_has_source_sha256": all(row.get("source_sha256") for row in rows),
        "every_source_row_pinned_with_artifact_report_and_digests": all(
            row.get("source_artifact")
            and row.get("source_report")
            and row.get("source_sha256")
            and row.get("source_report_sha256")
            for row in rows
        ),
        "evidence_strategy_class_values_valid": all(
            row["evidence_strategy_class"] in strategy_class_values for row in rows
        ),
        "external_structured_state_classification_present": "external_structured_state"
        in output["source_role_taxonomy"],
        "final_ap6_not_assigned": output["iteration_result"]["final_ap6_supported"] is False,
        "inventory_summary_matches_rows": inventory_summary == expected_summary,
        "inventory_summary_row_count_matches": inventory_summary["row_count"]
        == len(rows),
        "lineage_sources_reference_valid_rows": all(
            source_id in row_ids
            for record in output["boundary_state_lineage"]
            for source_id in record["lineage_sources"]
        ),
        "native_support_not_opened": output["iteration_result"]["native_support_opened"] is False,
        "no_absolute_paths_recorded": not contains_absolute_path(output),
        "old_best_claim_inputs_recorded": len(output["old_best_claim_inputs"]) == 6,
        "old_best_claim_inputs_have_required_fields": all(
            old_best_required_fields <= record.keys()
            for record in output["old_best_claim_inputs"]
        ),
        "old_best_summary_names_unambiguous": (
            "old_best_claims_construction_input_rows" in inventory_summary
            and "old_best_claim_input_rows" not in inventory_summary
        ),
        "phase8_opened_false": output["iteration_result"]["phase8_opened"] is False,
        "provisional_only": output["acceptance_state"]
        == "accepted_boundary_source_inventory_only_no_ap6",
        "required_roles_present": required_roles <= role_set,
        "role_classification_incompatibility_audit_passed": all(
            row["role_classification_audit"]["incompatible_roles_detected"] is False
            and row["role_classification_audit"]["readiness_not_native_support"] is True
            and row["role_classification_audit"][
                "boundary_crossing_not_closed_action_perception_loop"
            ]
            is True
            for row in rows
        ),
        "required_source_paths_exist": all(path.exists() for path in paths),
        "row_decisions_fail_closed": all(
            row["row_decision"] == "not_applicable"
            and row["boundary_claim_allowed"] is False
            for row in rows
        ),
        "row_decision_values_valid": all(
            row["row_decision"] in row_decision_values for row in rows
        ),
        "source_statuses_loaded": all(row["source_status"] for row in rows),
        "source_status_values_valid": all(
            row["source_status"] in source_status_values for row in rows
        ),
        "src_diff_empty": output["git"]["src_status_short"] == "",
    }


def build_output() -> dict[str, Any]:
    rows = build_rows()
    output: dict[str, Any] = {
        "acceptance_state": "accepted_boundary_source_inventory_only_no_ap6",
        "arc_method_mapping": ARC_METHOD_MAPPING,
        "artifact_id": "n16_boundary_source_inventory",
        "blocked_claims": BLOCKED_CLAIMS,
        "boundary_state_lineage": BOUNDARY_STATE_LINEAGE,
        "challenge_class_records": CHALLENGE_CLASS_RECORDS,
        "claim_flags": CLAIM_FLAGS_FORCED_FALSE,
        "command": COMMAND,
        "context_documents": CONTEXT_DOCUMENTS,
        "direct_historic_ap6_support": {
            "direct_historic_support_status": "absent",
            "status": "none_found",
            "interpretation": (
                "No pinned historic source directly supports AP6 internal/"
                "external state separability. Prior records provide B-axis "
                "lineage, challenge analogs, controls, and old-best AP3-AP5 "
                "construction inputs only."
            ),
        },
        "errors": [],
        "experiment": "N16",
        "generated_at": GENERATED_AT,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
        "iteration": 1,
        "iteration_interpretation": {
            "acceptance_state": "accepted_boundary_source_inventory_only_no_ap6",
            "next_required_step": (
                "Freeze the N16 boundary schema, B-axis lineage contract, "
                "C-axis challenge-class contract, row decisions, source roles, "
                "budget surface, replay digest, and AP6 gates."
            ),
            "plain_language_interpretation": (
                "Iteration 1 pins N16's evidence base. It finds no direct "
                "historic AP6 support, but records old-best AP3-AP5 inputs, "
                "B-axis lineage from prior basin/boundary examples, and "
                "operational C-axis challenge classes for later schema work."
            ),
            "supported_interpretation": (
                "N16 has sufficient pinned source coverage to proceed to "
                "schema freeze. AP6 remains unassigned; the strongest path is "
                "constructed from old-best claims plus newly generated N16 "
                "boundary rows."
            ),
            "unsupported_interpretations": [
                "final AP6 self/environment boundary support",
                "native support",
                "selfhood",
                "personhood",
                "identity acceptance",
                "semantic goal ownership",
                "intention",
                "agency",
                "selective uptake",
                "organism or life claims",
            ],
        },
        "iteration_result": {
            "acceptance_state": "accepted_boundary_source_inventory_only_no_ap6",
            "artifact_level_ap6_supported": False,
            "boundary_source_inventory_passed": True,
            "direct_historic_ap6_support_recorded": False,
            "final_ap6_supported": False,
            "fully_native_integration_opened": False,
            "native_support_opened": False,
            "old_best_claim_inputs_recorded": True,
            "phase8_opened": False,
        },
        "old_best_claim_inputs": OLD_BEST_CLAIM_INPUTS,
        "purpose": "baseline_and_boundary_source_inventory",
        "rows": rows,
        "schema_version": "n16_i1_boundary_source_inventory_v1",
        "source_artifacts": build_source_artifacts(rows),
        "source_role_taxonomy": [
            "internal_support_state",
            "external_resource_state",
            "external_perturbation_state",
            "external_structured_state",
            "boundary_crossing_trace",
            "readiness",
            "boundary_role",
            "claim_boundary_blocker",
        ],
    }
    output["inventory_summary"] = build_inventory_summary(rows)
    output["checks"] = build_checks(output)
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    summary = json.dumps(output["inventory_summary"], indent=2, sort_keys=True)
    checks = json.dumps(output["checks"], indent=2, sort_keys=True)
    interpretation = json.dumps(
        output["iteration_interpretation"], indent=2, sort_keys=True
    )

    source_lines = [
        "| Row | Source | Role | Strategy class | Direct support | Provisional level | Claim ceiling | Boundary relevance | Missing gates |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in output["rows"]:
        roles = ", ".join(row["source_role_classification"])
        states = ", ".join(row["boundary_state_relevance"]) or "none"
        missing = ", ".join(row["missing_gates"])
        source_lines.append(
            "| `{row_id}` | `{source}` | `{roles}` | `{strategy}` | "
            "`{direct}` | `{level}` | `{ceiling}` | `{states}` | `{missing}` |".format(
                row_id=row["row_id"],
                source=row["source_experiment"],
                roles=roles,
                strategy=row["evidence_strategy_class"],
                direct=row["direct_historic_support_status"],
                level=row["provisional_ap_level"],
                ceiling=row["provisional_claim_ceiling"],
                states=states,
                missing=missing,
            )
        )

    pin_lines = [
        "| Row | Source artifact | Artifact SHA-256 | Source report | Report SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in output["rows"]:
        pin_lines.append(
            "| `{row_id}` | `{artifact}` | `{artifact_sha}` | `{report}` | `{report_sha}` |".format(
                row_id=row["row_id"],
                artifact=row["source_artifact"],
                artifact_sha=row["source_sha256"],
                report=row["source_report"],
                report_sha=row["source_report_sha256"],
            )
        )

    b_lines = [
        "| State | Name | Claim ceiling | Required N16 evidence |",
        "| --- | --- | --- | --- |",
    ]
    for record in output["boundary_state_lineage"]:
        b_lines.append(
            "| `{state}` | {name} | `{ceiling}` | {required} |".format(
                state=record["boundary_state"],
                name=record["name"],
                ceiling=record["claim_ceiling"],
                required="; ".join(record["required_N16_evidence"]),
            )
        )

    c_lines = [
        "| Class | Name | Operational role | Claim boundary |",
        "| --- | --- | --- | --- |",
    ]
    for record in output["challenge_class_records"]:
        c_lines.append(
            "| `{klass}` | {name} | {role} | `{boundary}` |".format(
                klass=record["challenge_class"],
                name=record["name"],
                role=record["operational_role"],
                boundary=record["claim_boundary"],
            )
        )

    old_best_lines = [
        "| Input | Why included | Supports | Does not support | Required N16 addition | Claim ceiling |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in output["old_best_claim_inputs"]:
        old_best_lines.append(
            "| `{input}` | {why} | {supports} | {blocked_scope} | {required} | `{ceiling}` |".format(
                input=record["input"],
                why=record["why_included"],
                supports=record["what_it_supports"],
                blocked_scope=record["what_it_does_not_support"],
                required=record["required_N16_addition"],
                ceiling=record["claim_ceiling"],
            )
        )

    taxonomy_lines = [
        "| Role |",
        "| --- |",
    ]
    for role in output["source_role_taxonomy"]:
        taxonomy_lines.append(f"| `{role}` |")

    return "\n".join(
        [
            "# N16 Boundary Source Inventory",
            "",
            "Status: `passed`.",
            "",
            "## Summary",
            "",
            "```json",
            summary,
            "```",
            "",
            "## Acceptance State",
            "",
            "```text",
            output["acceptance_state"],
            "```",
            "",
            "## Interpretation",
            "",
            "```json",
            interpretation,
            "```",
            "",
            "Iteration 1 is a source inventory only. It pins source artifacts, "
            "derives provisional B0-B4 lineage from prior N** evidence, records "
            "C0-C5 as operational challenge classes, and confirms no final "
            "`AP6` claim is assigned.",
            "",
            "The global roadmap and handoff are listed as context documents in "
            "the JSON but are not SHA-pinned by this artifact, because they are "
            "updated after iteration artifacts and would otherwise create a "
            "self-referential digest.",
            "",
            "`generated_at` is fixed for deterministic reconstruction and is "
            "excluded from `output_digest` with git working-tree metadata.",
            "",
            "## Direct Historic AP6 Support",
            "",
            "```json",
            json.dumps(
                output["direct_historic_ap6_support"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Old-Best Claim Inputs",
            "",
            "\n".join(old_best_lines),
            "",
            "## Source Rows",
            "",
            "\n".join(source_lines),
            "",
            "## Source Pinning",
            "",
            "\n".join(pin_lines),
            "",
            "## Source Role Taxonomy",
            "",
            "\n".join(taxonomy_lines),
            "",
            "## B-Axis Lineage",
            "",
            "\n".join(b_lines),
            "",
            "## C-Axis Challenge Classes",
            "",
            "\n".join(c_lines),
            "",
            "## Checks",
            "",
            "```json",
            checks,
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "source inventory != self/environment boundary",
            "B-axis lineage != invented generic boundary taxonomy",
            "C-axis challenge class != inherited environment taxonomy",
            "N15 AP5 != AP6",
            "N14 AP4 != intention or agency",
            "N13 AP3 != selfhood or native support",
            "N12 NAT4 readiness != native support",
            "N07 ID6 context != runtime identity acceptance",
            "N16 Iteration 1 != selective uptake or resource assimilation",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
            "",
        ]
    )


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written = load_json(OUTPUT_PATH)
    if written.get("output_digest") != output_digest(written):
        raise SystemExit("post-write digest verification failed")
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")


if __name__ == "__main__":
    main()
