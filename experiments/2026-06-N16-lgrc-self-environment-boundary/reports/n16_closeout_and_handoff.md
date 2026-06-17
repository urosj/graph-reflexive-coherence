# N16 Closeout And N17 Handoff

## Status

Status: `passed`.

```text
acceptance_state = closed_claim_clean_ap6_artifact_level_self_environment_boundary_candidate
final_supported_ap_level = AP6
final_ap6_supported = true
final_claim_ceiling = artifact_level_ap6_self_environment_boundary_candidate_with_controlled_basin_boundary_requirements
artifact_level_ap6_supported = true
final_artifact_level_ap6_frozen = true
phase8_opened = false
native_support_opened = false
fully_native_integration_opened = false
closed_action_perception_loop_opened = false
```

N16 closes with supported artifact-level `AP6` evidence for a
self/environment boundary candidate. The final scope is separability
of internal support-relevant state from external resource,
perturbation, structured-state, and shared-medium pressures in
generated artifacts and controls.

## Hypotheses

| Hypothesis | Closeout decision |
| --- | --- |
| `hypothesis_a_boundary_source_inventory` | `closed_supported` |
| `hypothesis_b_artifact_basin_boundary_stability` | `closed_supported` |
| `hypothesis_c_selfhood_identity_agency_boundary` | `closed_supported` |

## Closeout Result

```json
{
  "agency_claim_opened": false,
  "artifact_level": true,
  "artifact_only": true,
  "closed_action_perception_loop_opened": false,
  "final_ap6_supported": true,
  "final_claim_ceiling": "artifact_level_ap6_self_environment_boundary_candidate_with_controlled_basin_boundary_requirements",
  "final_scope": "internal support-relevant state and external resource, perturbation, structured-state, and shared-medium pressures are separable in generated artifacts and controls",
  "final_supported_ap_level": "AP6",
  "fully_native": false,
  "fully_native_integration_opened": false,
  "identity_acceptance_opened": false,
  "n17_handoff_ready": true,
  "native_support_opened": false,
  "native_supported_flag_detail": {
    "fully_native_integration_opened": false,
    "native_support_opened": false,
    "phase8_opened": false
  },
  "native_supported_flags": false,
  "phase8_opened": false,
  "selfhood_claim_opened": false,
  "semantic_goal_ownership_opened": false,
  "status": "closed_claim_clean_ap6_artifact_level_self_environment_boundary_candidate",
  "targeted_phase8_required_before_n17": false
}
```

## Final Controls

```json
{
  "all_negative_controls_fail_closed": true,
  "all_replay_controls_stable": true,
  "ap6_gate_summary": {
    "all_ap6_gates_validated": true,
    "blocked_gate_count": 0,
    "blocked_gates": [],
    "gate_count": 39,
    "validated_gate_count": 39
  },
  "claim_boundary_summary": {
    "all_boundary_claims_blocked": true,
    "all_unsafe_boundary_promotions_blocked": true,
    "artifact_ap6_boundary_candidate_supported": true,
    "blocked_claims": [
      "selfhood",
      "identity_acceptance",
      "semantic_goal_ownership",
      "closed_action_perception_loop",
      "native_support",
      "fully_native_agentic_like_integration",
      "agency_environment_model",
      "autonomous_repair",
      "native_multi_basin_selfhood",
      "selective_uptake_resource_assimilation_life",
      "schema_control_overclaim"
    ],
    "boundary_row_count": 11,
    "closed_action_perception_loop_blocked": true,
    "duplicate_replay_schema_backing_acknowledged": true,
    "identity_acceptance_blocked": true,
    "native_support_blocked": true,
    "selfhood_blocked": true,
    "semantic_goal_ownership_blocked": true
  },
  "duplicate_replay_backing": {
    "acknowledged": true,
    "control_present": true,
    "expected_backing": "i7_run_level_replay_extension_not_i2_schema_control",
    "handoff_note_contains_control_id": true,
    "schema_backed": false,
    "schema_backed_field_present": true
  },
  "negative_control_count": 20,
  "negative_controls": [
    {
      "ap6_claim_allowed": false,
      "blocker": "artifact_replay_instability_blocks_ap6",
      "control_id": "artifact_only_replay_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "stable"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "boundary_drift_outside_policy_blocked",
      "control_id": "boundary_drift_outside_policy_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "duplicate_replay_instability_blocks_ap6",
      "control_id": "duplicate_replay_control",
      "fail_closed": true,
      "schema_backed": false,
      "status": "stable"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "externally_supplied_boundary_blocked",
      "control_id": "externally_supplied_boundary_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "hidden_external_state_injection_blocked",
      "control_id": "hidden_external_state_injection_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "identity_acceptance_relabel_blocked",
      "control_id": "identity_acceptance_relabel_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "missing_boundary_side_state_blocked",
      "control_id": "missing_boundary_side_state_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "multi_basin_merge_or_leakage_recorded",
      "control_id": "multi_basin_merge_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked_or_recorded_failure"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "native_support_relabel_blocked",
      "control_id": "native_support_relabel_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "order_inversion_instability_blocks_ap6",
      "control_id": "order_inversion_replay_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "stable"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "post_hoc_boundary_label_blocked",
      "control_id": "post_hoc_boundary_label_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "resource_relabel_as_self_blocked",
      "control_id": "resource_relabel_as_self_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "self_support_relabel_as_external_blocked",
      "control_id": "self_support_relabel_as_external_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "selfhood_personhood_relabel_blocked",
      "control_id": "selfhood_personhood_relabel_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "semantic_goal_ownership_relabel_blocked",
      "control_id": "semantic_goal_ownership_relabel_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "snapshot_load_instability_blocks_ap6",
      "control_id": "snapshot_load_replay_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "stable"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "stale_external_state_blocked",
      "control_id": "stale_external_state_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "stale_internal_state_blocked",
      "control_id": "stale_internal_state_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "structured_external_coherence_false_boundary_blocked",
      "control_id": "structured_external_coherence_rejection_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked_or_rejected"
    },
    {
      "ap6_claim_allowed": false,
      "blocker": "untracked_boundary_crossing_blocked",
      "control_id": "untracked_boundary_crossing_control",
      "fail_closed": true,
      "schema_backed": true,
      "status": "blocked"
    }
  ],
  "replay_summary": {
    "artifact_only_replay_stable": true,
    "duplicate_replay_stable": true,
    "order_inversion_replay_stable": true,
    "snapshot_load_replay_stable": true
  }
}
```

## Final Source Row Roles

```json
[
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "artifact_level_ap5_endogenous_proxy_formation_candidate",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "boundary_crossing_trace_context",
      "claim_boundary_blocker"
    ],
    "initial_provisional_ap_level": "AP5",
    "mechanism_name": "artifact_level_ap5_endogenous_proxy_formation_candidate",
    "mechanism_role": "old_best_ap5_proxy_target_axis",
    "row_id": "n16_i1_row_01_n15_closeout_ap5",
    "source_experiment": "N15",
    "source_role_classification": [
      "internal_support_state",
      "boundary_crossing_trace",
      "claim_boundary_blocker"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "provisional_runtime_derived_target_candidate_pending_controls",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "AP5_candidate_at_iteration_3_scope",
    "mechanism_name": "runtime_derived_target_candidate_from_old_best_inputs",
    "mechanism_role": "source_current_target_generation_context",
    "row_id": "n16_i1_row_02_n15_runtime_derived_target_candidate",
    "source_experiment": "N15",
    "source_role_classification": [
      "internal_support_state",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "bounded_drift_replay_context_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "external_perturbation_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "AP5_control_context",
    "mechanism_name": "bounded_drift_replay_matrix",
    "mechanism_role": "replay_and_drift_control_context",
    "row_id": "n16_i1_row_03_n15_bounded_drift_replay",
    "source_experiment": "N15",
    "source_role_classification": [
      "internal_support_state",
      "external_perturbation_state",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_ap6_positive_evidence",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "claim_boundary_context_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "external_structured_state_rejection_context",
      "claim_boundary_blocker"
    ],
    "initial_provisional_ap_level": "AP0_boundary",
    "mechanism_name": "n15_claim_boundary_record",
    "mechanism_role": "unsafe_claim_relabel_blocker_source",
    "row_id": "n16_i1_row_04_n15_claim_boundary",
    "source_experiment": "N15",
    "source_role_classification": [
      "external_structured_state",
      "claim_boundary_blocker"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "artifact_level_ap4_consequence_sensitive_route_selection_candidate",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "external_resource_state_context",
      "boundary_crossing_trace_context",
      "claim_boundary_blocker"
    ],
    "initial_provisional_ap_level": "AP4",
    "mechanism_name": "artifact_level_ap4_consequence_sensitive_route_selection",
    "mechanism_role": "old_best_ap4_consequence_selection_axis",
    "row_id": "n16_i1_row_05_n14_closeout_ap4",
    "source_experiment": "N14",
    "source_role_classification": [
      "external_resource_state",
      "boundary_crossing_trace",
      "claim_boundary_blocker"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "constructed_route_conditioned_followout_context_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "external_resource_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "AP4_context",
    "mechanism_name": "constructed_route_conditioned_support_regulation_followout",
    "mechanism_role": "constructed_external_route_context",
    "row_id": "n16_i1_row_06_n14_constructed_followout",
    "source_experiment": "N14",
    "source_role_classification": [
      "external_resource_state",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "boundary_crossing_trace_context",
      "claim_boundary_blocker"
    ],
    "initial_provisional_ap_level": "AP3",
    "mechanism_name": "artifact_level_ap3_support_seeking_regulation",
    "mechanism_role": "old_best_ap3_support_regulation_axis",
    "row_id": "n16_i1_row_07_n13_closeout_ap3",
    "source_experiment": "N13",
    "source_role_classification": [
      "internal_support_state",
      "boundary_crossing_trace",
      "claim_boundary_blocker"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "support_disruption_restoration_context_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "external_perturbation_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "AP3_stress_context",
    "mechanism_name": "support_disruption_restoration_stress_matrix",
    "mechanism_role": "repair_and_support_error_context",
    "row_id": "n16_i1_row_08_n13_support_disruption_restoration",
    "source_experiment": "N13",
    "source_role_classification": [
      "internal_support_state",
      "external_perturbation_state",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "readiness_only_not_native_support",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "readiness_only_context"
    ],
    "initial_provisional_ap_level": "AP0_readiness",
    "mechanism_name": "phase8_readiness_matrix",
    "mechanism_role": "readiness_only_context",
    "row_id": "n16_i1_row_09_n12_phase8_readiness",
    "source_experiment": "N12",
    "source_role_classification": [
      "readiness"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "artifact_surface_inventory_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "boundary_lineage_evidence"
    ],
    "initial_provisional_ap_level": "pre_AP_boundary_lineage",
    "mechanism_name": "basin_sink_parent_surface_inventory",
    "mechanism_role": "localized_basin_surface_lineage",
    "row_id": "n16_i1_row_10_n03_artifact_surface_inventory",
    "source_experiment": "N03",
    "source_role_classification": [
      "boundary_role"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "native_lgrc9v3_packet_loop_reproduced",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "boundary_lineage_evidence",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "pre_AP_boundary_lineage",
    "mechanism_name": "native_lgrc9v3_packetized_basin_loop",
    "mechanism_role": "localized_basin_loop_lineage",
    "row_id": "n16_i1_row_11_n03_native_packet_loop_closeout",
    "source_experiment": "N03",
    "source_role_classification": [
      "boundary_role",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "taxonomy_inventory_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "boundary_lineage_evidence",
      "external_resource_state_context"
    ],
    "initial_provisional_ap_level": "pre_AP_boundary_lineage",
    "mechanism_name": "movement_boundary_persistence_taxonomy_inventory",
    "mechanism_role": "boundary_and_persistence_taxonomy_lineage",
    "row_id": "n16_i1_row_12_n04_taxonomy_inventory",
    "source_experiment": "N04",
    "source_role_classification": [
      "boundary_role",
      "external_resource_state"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "boundary_coupled_pulse_fixture_validation",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "external_resource_state_context",
      "boundary_crossing_trace_context",
      "boundary_lineage_evidence"
    ],
    "initial_provisional_ap_level": "pre_AP_boundary_lineage",
    "mechanism_name": "boundary_coupled_pulse_fixture",
    "mechanism_role": "boundary_coupling_lineage",
    "row_id": "n16_i1_row_13_n04_boundary_coupled_pulse",
    "source_experiment": "N04",
    "source_role_classification": [
      "external_resource_state",
      "boundary_crossing_trace",
      "boundary_role"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "topology_mutating_movement_candidate",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "boundary_lineage_evidence",
      "claim_boundary_blocker"
    ],
    "initial_provisional_ap_level": "pre_AP_boundary_lineage",
    "mechanism_name": "topology_mutating_movement_candidate_closeout",
    "mechanism_role": "boundary_claim_boundary_and_topology_caveat",
    "row_id": "n16_i1_row_14_n04_taxonomy_continuation_closeout",
    "source_experiment": "N04",
    "source_role_classification": [
      "boundary_role",
      "claim_boundary_blocker"
    ]
  },
  {
    "direct_historic_ap6_support_status": "indirect_lineage_not_direct_ap6",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "artifact_only_source_specific_bounded_non_destructive_exchange",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "boundary_lineage_evidence"
    ],
    "initial_provisional_ap_level": "ID6_context_not_AP",
    "mechanism_name": "bounded_non_destructive_exchange_id6_evidence",
    "mechanism_role": "support_persistence_and_dual_basin_lineage",
    "row_id": "n16_i1_row_15_n07_long_horizon_compatibility_closeout",
    "source_experiment": "N07",
    "source_role_classification": [
      "internal_support_state",
      "boundary_role"
    ]
  },
  {
    "direct_historic_ap6_support_status": "indirect_lineage_not_direct_ap6",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "identity_support_withdrawal_baseline_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "external_perturbation_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "ID6_context_not_AP",
    "mechanism_name": "identity_support_withdrawal_and_restoration_baseline",
    "mechanism_role": "support_persistence_and_repair_lineage",
    "row_id": "n16_i1_row_16_n07_identity_support_withdrawal_baseline",
    "source_experiment": "N07",
    "source_role_classification": [
      "internal_support_state",
      "external_perturbation_state",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "artifact_only_route_memory_or_trail_affordance_candidate",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "external_resource_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "AP2_context",
    "mechanism_name": "route_memory_trail_affordance_closeout",
    "mechanism_role": "memory_and_route_alternative_context",
    "row_id": "n16_i1_row_17_n08_memory_trail_closeout",
    "source_experiment": "N08",
    "source_role_classification": [
      "external_resource_state",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "repeated_bounded_proxy_regulation_candidate",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "external_perturbation_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "AP2_context",
    "mechanism_name": "bounded_goal_proxy_regulation_closeout",
    "mechanism_role": "bounded_regulation_context",
    "row_id": "n16_i1_row_18_n09_goal_proxy_regulation_closeout",
    "source_experiment": "N09",
    "source_role_classification": [
      "internal_support_state",
      "external_perturbation_state",
      "boundary_crossing_trace"
    ]
  },
  {
    "direct_historic_ap6_support_status": "not_direct_ap6_support",
    "final_ap6_source_use": "source_backed_context_or_lineage_for_artifact_level_ap6_boundary",
    "final_boundary_claim_allowed_from_source_row_alone": false,
    "final_claim_boundary": "perturbation_recovery_context_only",
    "final_claim_promotion_allowed": false,
    "final_roles": [
      "internal_support_state_context",
      "external_perturbation_state_context",
      "boundary_crossing_trace_context"
    ],
    "initial_provisional_ap_level": "AP2_context",
    "mechanism_name": "perturbation_recovery_and_support_withdrawal_record",
    "mechanism_role": "explicit_perturbation_and_support_withdrawal_context",
    "row_id": "n16_i1_row_19_n09_perturbation_withdrawal_support",
    "source_experiment": "N09",
    "source_role_classification": [
      "internal_support_state",
      "external_perturbation_state",
      "boundary_crossing_trace"
    ]
  }
]
```

## Final Claim Boundary

```json
{
  "agency_environment_model_supported": false,
  "agency_supported": false,
  "artifact_level_ap6_self_environment_boundary_candidate_supported": true,
  "autonomous_repair_supported": false,
  "biological_behavior_supported": false,
  "closed_action_perception_loop_supported": false,
  "fully_native_agentic_like_integration_supported": false,
  "identity_acceptance_supported": false,
  "intention_supported": false,
  "native_multi_basin_selfhood_supported": false,
  "native_support_supported": false,
  "organism_life_supported": false,
  "personhood_supported": false,
  "resource_assimilation_supported": false,
  "runtime_identity_acceptance_supported": false,
  "selective_uptake_supported": false,
  "selfhood_supported": false,
  "semantic_choice_supported": false,
  "semantic_goal_ownership_supported": false,
  "semantic_goal_understanding_supported": false,
  "unrestricted_agency_supported": false
}
```

## N17 Handoff

```json
{
  "handoff_caveats": [
    "N16 AP6 is an artifact-level boundary candidate, not selfhood or agency.",
    "N17 must show selected action consequences changing later selection inputs, not only boundary separability.",
    "Boundary-crossing traces from N16 are allowed context but do not themselves prove a closed action-perception loop.",
    "Phase 8 remains unopened and native support remains false."
  ],
  "n17_allowed_inputs": [
    "N16 final artifact-level AP6 self/environment boundary closeout",
    "N15 final artifact-level AP5 endogenous proxy formation closeout",
    "N14 final artifact-level AP4 consequence-sensitive route selection closeout",
    "N13 final artifact-level AP3 support-seeking regulation closeout",
    "N08 memory/context and N09 bounded-regulation context as artifact evidence"
  ],
  "n17_blocked_inputs": [
    "selfhood",
    "personhood",
    "identity acceptance",
    "semantic goal ownership",
    "intention",
    "semantic choice",
    "agency",
    "native support",
    "fully native agentic-like integration",
    "organism or biological behavior",
    "unrestricted agency"
  ],
  "n17_primary_question": "Can selected actions alter substrate or environment state, and can those altered conditions feed back into later selection?",
  "n17_required_controls": [
    "action consequence missing blocked",
    "stale consequence read blocked",
    "producer direct mutation blocked",
    "environment change without selected action blocked",
    "boundary crossing without feedback blocked",
    "semantic agency relabel blocked",
    "identity/selfhood/personhood relabel blocked",
    "native support relabel blocked",
    "artifact-only, snapshot/load, duplicate, and order-inversion replay stable"
  ],
  "recommended_branch": "experiment-N17",
  "recommended_next": "N17_closed_action_perception_loop",
  "target_ap_level": "AP7",
  "targeted_phase8_required_before_n17": false,
  "targeted_phase8_status": "optional_deferred_not_required_for_n17"
}
```

## Final Blockers

```json
[
  {
    "blocker_id": "closed_action_perception_loop_not_tested_until_N17",
    "rationale": "N16 records boundary-crossing traces but does not close action-perception feedback.",
    "status": "blocked"
  },
  {
    "blocker_id": "selfhood_personhood_identity_acceptance_blocked",
    "rationale": "Artifact boundary-side assignment is not selfhood, personhood, or identity acceptance.",
    "status": "blocked"
  },
  {
    "blocker_id": "semantic_goal_ownership_and_intention_blocked",
    "rationale": "Internal support-relevant state is not semantic goal ownership, intention, or semantic choice.",
    "status": "blocked"
  },
  {
    "blocker_id": "agency_and_agency_environment_model_blocked",
    "rationale": "External resource/challenge descriptors are not an agency environment model.",
    "status": "blocked"
  },
  {
    "blocker_id": "native_support_and_phase8_blocked",
    "rationale": "N16 leaves native support, Phase 8, and fully native integration unopened.",
    "status": "blocked"
  },
  {
    "blocker_id": "autonomous_repair_blocked",
    "rationale": "B3_C4 is artifact-level breach/reclosure evidence, not autonomous repair.",
    "status": "blocked"
  },
  {
    "blocker_id": "native_multi_basin_selfhood_blocked",
    "rationale": "B4_C5 is artifact-level shared-medium separability evidence only.",
    "status": "blocked"
  },
  {
    "blocker_id": "selective_uptake_resource_assimilation_life_blocked",
    "rationale": "N16 excludes selective uptake, resource assimilation, organism, and life claims.",
    "status": "blocked"
  },
  {
    "blocker_id": "reverse_basin_perspective_deferred_as_stronger_scope_limit",
    "rationale": "One-sided B4_C5 evidence is enough for this artifact-level claim ceiling but blocks stronger symmetric/native multi-basin claims.",
    "status": "blocked"
  },
  {
    "blocker_id": "direct_historic_ap6_support_absent",
    "rationale": "Final AP6 is constructed and controlled from prior claims plus N16 evidence, not inherited directly from a historic AP6 row.",
    "status": "blocked"
  }
]
```

## Whole Experiment Interpretation

```json
{
  "claim_boundary_summary": "The closeout supports AP6 only as an artifact-level boundary candidate. It does not support selfhood, identity acceptance, semantic goal ownership, agency, native support, a closed action-perception loop, organism/life claims, or unrestricted agency.",
  "plain_language_interpretation": "N16 closes with claim-clean artifact-level AP6 evidence for a self/environment boundary candidate. The evidence supports separability of internal support-relevant state from external resource, perturbation, structured-state, and shared-medium pressures across generated artifacts, controls, and replay.",
  "record_id": "n16_i9_whole_experiment_interpretation_v1",
  "supported_interpretation": "artifact_level_ap6_self_environment_boundary_candidate_with_controlled_basin_boundary_requirements",
  "supporting_evidence_summary": [
    "I1 pins source rows and records direct historic AP6 support as absent.",
    "I2 freezes the B-axis, C-axis, row schema, controls, and AP6 gates.",
    "I3-I6 generate calibration, challenge, boundary-state, and selected interaction evidence.",
    "I7 converts I3-I6 evidence into a full controlled requirements matrix.",
    "I8 validates all 39 AP6 gates and keeps unsafe promotions blocked.",
    "I9 freezes final supported AP level AP6 at artifact-level candidate scope."
  ],
  "why_it_matters_for_roadmap": "N16 gives N17 a source-backed boundary substrate for testing closed action-perception feedback without relabeling AP6 as agency."
}
```

## Checks

```json
{
  "absolute_path_absence": true,
  "all_source_rows_have_final_roles": true,
  "artifact_ap6_supported_and_frozen": true,
  "closed_action_perception_loop_not_opened": true,
  "digest_reproducibility": true,
  "every_ap6_gate_validated": true,
  "final_blockers_recorded": true,
  "final_claim_boundary_unsafe_false": true,
  "final_claim_ceiling_recorded": true,
  "final_controls_recorded": true,
  "final_supported_ap_level_ap6": true,
  "fully_native_integration_opened_false": true,
  "hypothesis_a_closed_supported": true,
  "hypothesis_b_closed_supported": true,
  "hypothesis_c_closed_supported": true,
  "idempotency_digest_plan_reproducible": true,
  "inventory_source_passed": true,
  "iteration_3_source_passed": true,
  "iteration_4_source_passed": true,
  "iteration_5_source_passed": true,
  "iteration_6_source_passed": true,
  "iteration_7_source_passed": true,
  "iteration_8_acceptance_state_valid": true,
  "iteration_8_output_digest_matches_reviewed_record": true,
  "iteration_8_source_passed": true,
  "iteration_9_closeout_ready": true,
  "n17_handoff_recorded": true,
  "native_supported_flags_false": true,
  "no_unclassified_source_rows": true,
  "phase8_opened_false": true,
  "schema_source_passed": true,
  "source_digest_presence": true,
  "src_diff_empty": true,
  "targeted_phase8_not_required_for_n17": true,
  "unsafe_claim_flags_false": true
}
```

## Claim Boundary

```text
artifact self/environment boundary != selfhood
boundary-side assignment != identity acceptance
internal support-relevant state != semantic goal ownership
external resource/challenge state != agency environment model
boundary-crossing trace != closed action-perception loop
artifact-level AP6 != native support
N16 AP6 != fully native agentic-like integration
N16 AP6 != organism, life, biological behavior, or unrestricted agency
```

## Output Digest

```text
fb073257cde92b544ff5dbfb169d8177720cfba7622de09d913b670ce3fcebdf
```
