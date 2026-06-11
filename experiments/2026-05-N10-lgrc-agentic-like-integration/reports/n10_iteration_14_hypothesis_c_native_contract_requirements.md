# N10 Iteration 14 Hypothesis C Native Contract Requirements

Status: `passed`.

## Result

Iteration 14 converts the Iteration 13 native gap inventory into
minimal native contract requirements. It does not implement native
behavior, edit `src/*`, or open native support flags.

```text
contract_status = native_contract_requirements_complete
fully_native_agentic_like_integration_supported = false
native_support_flags_opened = false
contract_row_count = 6
phase_8_absorption_step_count = 6
```

## Contract Interpretation

Iteration 14 turns the Phase 8-facing blockers into contract shape:
required policy records, runtime-visible inputs, ordering, stale
context blockers, budget surfaces, artifact replay requirements,
negative controls, and claim-boundary controls.

It still does not decide to implement all of them. Iteration 15 should
close the handoff and decide which blockers become future Phase 8
tasks and in what order.

## Native Contract Requirements

```json
[
  {
    "artifact_replay_requirements": [
      "artifact replay reconstructs selected route from native arbitration record",
      "replay records selection-only scope explicitly"
    ],
    "budget_surfaces": [
      "route_selection_budget_surface_if_scheduling_occurs"
    ],
    "claim_boundary_controls": [
      "semantic_choice_claim_promotion_blocked",
      "agency_claim_promotion_blocked"
    ],
    "claim_flags": {
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "native_agentic_like_integration_supported": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false
    },
    "contract_row_digest": "4a08686cc71005137608abbe514991a6b53703ada691a6490c1233c1879aad0a",
    "covered_policy_records": [
      "native_route_context_record"
    ],
    "implemented_in_iteration_14": false,
    "native_contract_status": "required_for_future_generalization",
    "native_support_opened_by_iteration_14": false,
    "negative_controls": [
      "hidden_route_context_rejected",
      "experiment_side_route_override_rejected",
      "route_context_order_inversion_rejected"
    ],
    "ordering_requirements": [
      "route context must follow committed candidate/arbitration evidence",
      "route context must precede downstream memory/regulation consumption"
    ],
    "phase_8_absorption_notes": "Not necessarily a standalone Phase 8 mechanism now; use as contract hardening unless N11 needs broader route execution context.",
    "phase_8_readiness": "schema_hardening_only_unless_scope_extends_beyond_selection",
    "policy_record": "native_route_context_record",
    "requirement_type": "native_context_contract",
    "row_id": "n10_i14_contract_01_route_context",
    "runtime_visible_inputs": [
      "route_context_source_digest",
      "selected_route_digest",
      "native_arbitration_policy_id",
      "arbitration_record_digest",
      "selection_only_scope_marker"
    ],
    "source_gap_row_ids": [
      "n10_c_gap_01_route_context_selection_boundary"
    ],
    "stale_context_blockers": [
      "stale_route_context_blocked",
      "route_context_relabelled_as_semantic_choice"
    ]
  },
  {
    "artifact_replay_requirements": [
      "replay reconstructs memory update and relaxation from serialized policy",
      "replay rejects hidden memory strength or report-side scoring"
    ],
    "budget_surfaces": [
      "route_conductance_memory_budget_surface",
      "node_plus_packet_budget_surface_separate"
    ],
    "claim_boundary_controls": [
      "aco_like_claim_promotion_blocked",
      "ant_colony_claim_promotion_blocked",
      "agency_claim_promotion_blocked"
    ],
    "claim_flags": {
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "native_agentic_like_integration_supported": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false
    },
    "contract_row_digest": "70fe3633a10c55c21e2233e4064f58c8708d7d4f962bc20118f23bde0995a84d",
    "covered_policy_records": [
      "native_route_conductance_memory_policy_record",
      "native_geometry_conductance_update_policy_record"
    ],
    "implemented_in_iteration_14": false,
    "native_contract_status": "required_before_native_memory_trail_support",
    "native_support_opened_by_iteration_14": false,
    "negative_controls": [
      "hidden_memory_policy_rejected",
      "producer_memory_relabelled_native_rejected",
      "memory_budget_surface_ambiguity_rejected",
      "conductance_update_without_route_use_rejected"
    ],
    "ordering_requirements": [
      "route use must precede conductance update",
      "conductance state must be current before route arbitration consumes it",
      "relaxation must be event-ordered and replayable"
    ],
    "phase_8_absorption_notes": "Likely first concrete Phase 8 candidate from C: absorb N08 memory/trail into a native route conductance or geometry-mediated memory policy.",
    "phase_8_readiness": "concrete_phase_8_candidate",
    "policy_record": "native_route_conductance_memory_policy_record",
    "requirement_type": "native_constitutive_policy",
    "row_id": "n10_i14_contract_02_route_conductance_memory",
    "runtime_visible_inputs": [
      "route_use_digest",
      "route_scope_digest",
      "conductance_state_before_digest",
      "conductance_state_after_digest",
      "memory_update_rule_id",
      "memory_relaxation_rule_id"
    ],
    "source_gap_row_ids": [
      "n10_c_gap_02_serialized_memory_policy",
      "n10_c_gap_03_native_geometry_trail_design_direction"
    ],
    "stale_context_blockers": [
      "stale_route_conductance_memory_blocked",
      "missing_route_use_digest_blocked",
      "conductance_memory_order_inversion_blocked"
    ]
  },
  {
    "artifact_replay_requirements": [
      "replay reconstructs proxy measurement, error, eligibility, and response magnitude",
      "replay rejects report-side target band or response sizing"
    ],
    "budget_surfaces": [
      "goal_proxy_budget_surface",
      "response_magnitude_budget_surface",
      "node_plus_packet_budget_surface_separate"
    ],
    "claim_boundary_controls": [
      "semantic_goal_ownership_claim_promotion_blocked",
      "intention_claim_promotion_blocked",
      "agency_claim_promotion_blocked"
    ],
    "claim_flags": {
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "native_agentic_like_integration_supported": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false
    },
    "contract_row_digest": "381572ef8768633551d727b53f86d15e33ba5580ef2db61101c84d5ece93c8c7",
    "covered_policy_records": [
      "native_goal_proxy_regulation_policy_record",
      "native_response_magnitude_policy_record"
    ],
    "implemented_in_iteration_14": false,
    "native_contract_status": "required_before_general_native_regulation_support",
    "native_support_opened_by_iteration_14": false,
    "negative_controls": [
      "hidden_proxy_target_rejected",
      "hidden_response_magnitude_rejected",
      "unbounded_perturbation_without_policy_rejected",
      "proxy_budget_ambiguity_rejected"
    ],
    "ordering_requirements": [
      "proxy measurement precedes error computation",
      "error computation precedes eligibility",
      "eligibility precedes response scheduling",
      "response magnitude policy precedes packet scheduling"
    ],
    "phase_8_absorption_notes": "Concrete Phase 8 candidate once the response magnitude semantics are constrained enough to avoid hidden goal ownership or intention.",
    "phase_8_readiness": "concrete_phase_8_candidate_after_memory_or_in_parallel",
    "policy_record": "native_goal_proxy_regulation_policy_record",
    "requirement_type": "native_constitutive_policy",
    "row_id": "n10_i14_contract_03_goal_proxy_regulation",
    "runtime_visible_inputs": [
      "proxy_surface_digest",
      "target_band_policy_id",
      "proxy_error_digest",
      "eligibility_record_digest",
      "response_magnitude_policy_id",
      "perturbation_envelope_digest"
    ],
    "source_gap_row_ids": [
      "n10_c_gap_04_goal_proxy_regulation_artifact_policy",
      "n10_c_gap_05_response_magnitude_policy"
    ],
    "stale_context_blockers": [
      "stale_proxy_surface_blocked",
      "stale_target_band_blocked",
      "response_magnitude_policy_missing",
      "unbounded_perturbation_envelope_blocked"
    ]
  },
  {
    "artifact_replay_requirements": [
      "replay reconstructs support state, disruption, restoration, and history preservation",
      "replay keeps support survival distinct from identity acceptance"
    ],
    "budget_surfaces": [
      "support_validation_budget_surface_if_native_runtime_measured"
    ],
    "claim_boundary_controls": [
      "identity_acceptance_claim_promotion_blocked",
      "rc_identity_collapse_claim_promotion_blocked",
      "runtime_identity_acceptance_claim_promotion_blocked"
    ],
    "claim_flags": {
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "native_agentic_like_integration_supported": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false
    },
    "contract_row_digest": "5abb915f8347db0c9d182b4621e52b5ed9645bf542ebed5da6ac183a26bf6c2f",
    "covered_policy_records": [
      "native_identity_support_validator_record"
    ],
    "implemented_in_iteration_14": false,
    "native_contract_status": "required_before_identity_acceptance_or_rc_collapse_claims",
    "native_support_opened_by_iteration_14": false,
    "negative_controls": [
      "support_invariance_relabelled_identity_acceptance_rejected",
      "hidden_restoration_rejected",
      "support_history_erasure_rejected"
    ],
    "ordering_requirements": [
      "support baseline precedes withdrawal",
      "withdrawal precedes disruption classification",
      "restoration evidence must follow disruption before resumption"
    ],
    "phase_8_absorption_notes": "Phase 8-facing but not first. It is claim-sensitive and should wait until identity acceptance and RC identity collapse gates are theory-frozen.",
    "phase_8_readiness": "defer_until_identity_acceptance_theory_is_precise",
    "policy_record": "native_identity_support_validator_record",
    "requirement_type": "native_validator_contract",
    "row_id": "n10_i14_contract_04_identity_support_validator",
    "runtime_visible_inputs": [
      "support_area_digest",
      "support_state_policy_id",
      "withdrawal_event_digest",
      "restoration_event_digest",
      "identity_acceptance_gate_id"
    ],
    "source_gap_row_ids": [
      "n10_c_gap_06_identity_support_not_acceptance"
    ],
    "stale_context_blockers": [
      "stale_support_baseline_blocked",
      "restoration_without_prior_disruption_blocked",
      "identity_acceptance_validator_missing"
    ]
  },
  {
    "artifact_replay_requirements": [
      "artifact replay reconstructs all component records and integration gate",
      "replay rejects private runtime state or hidden eligibility decisions"
    ],
    "budget_surfaces": [
      "node_plus_packet_budget_surface",
      "route_conductance_memory_budget_surface",
      "goal_proxy_budget_surface",
      "claim_economy_budget_surface_if_declared"
    ],
    "claim_boundary_controls": [
      "fully_native_agentic_like_claim_promotion_blocked",
      "agency_claim_promotion_blocked",
      "personhood_claim_promotion_blocked",
      "biological_claim_promotion_blocked"
    ],
    "claim_flags": {
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "native_agentic_like_integration_supported": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false
    },
    "contract_row_digest": "c87b4e13b56b7b9c5ae2fb8f398c8ce21685630f0771208e8d0e81dbc71a9513",
    "covered_policy_records": [
      "native_agentic_like_integration_policy_record",
      "native_support_state_integration_gate_record",
      "native_claim_boundary_contract_record"
    ],
    "implemented_in_iteration_14": false,
    "native_contract_status": "required_before_fully_native_agentic_like_integration",
    "native_support_opened_by_iteration_14": false,
    "negative_controls": [
      "missing_component_record_rejected",
      "stale_component_record_rejected",
      "hidden_integration_policy_rejected",
      "direct_native_support_flag_write_rejected"
    ],
    "ordering_requirements": [
      "component records must be committed before integration eligibility",
      "support state must be current at integration time",
      "integration record must not precede component policy records"
    ],
    "phase_8_absorption_notes": "Meta-gap. Do not implement before route memory, regulation, and support/identity validator contracts are available.",
    "phase_8_readiness": "meta_gap_after_component_policies",
    "policy_record": "native_agentic_like_integration_policy_record",
    "requirement_type": "native_integration_meta_policy",
    "row_id": "n10_i14_contract_05_native_integration_gate",
    "runtime_visible_inputs": [
      "route_context_record_digest",
      "route_conductance_memory_record_digest",
      "identity_support_state_digest",
      "goal_proxy_regulation_record_digest",
      "support_state_gate_digest",
      "claim_boundary_contract_digest"
    ],
    "source_gap_row_ids": [
      "n10_c_gap_07_artifact_only_integration_validator",
      "n10_c_gap_08_support_sensitive_integration_gate",
      "n10_c_gap_10_claim_boundary_flags"
    ],
    "stale_context_blockers": [
      "stale_component_record_blocked",
      "missing_component_policy_blocked",
      "support_disrupted_but_integration_allowed",
      "native_agentic_like_integration_policy_missing"
    ]
  },
  {
    "artifact_replay_requirements": [
      "replay verifies each budget surface separately",
      "replay rejects continuity claims across independent source artifacts"
    ],
    "budget_surfaces": [
      "node_plus_packet_budget_surface",
      "route_conductance_memory_budget_surface",
      "goal_proxy_budget_surface",
      "identity_support_budget_surface_if_native"
    ],
    "claim_boundary_controls": [
      "budget_evidence_relabelled_claim_support_blocked"
    ],
    "claim_flags": {
      "aco_like_claim_allowed": false,
      "agency_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "native_agentic_like_integration_supported": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false
    },
    "contract_row_digest": "f5a482437ae54c2d651eb3c960dad6b82b2a06df901316f34ddb916dfacbb0c1",
    "covered_policy_records": [
      "native_budget_surface_contract_record"
    ],
    "implemented_in_iteration_14": false,
    "native_contract_status": "required_for_any_native_absorption",
    "native_support_opened_by_iteration_14": false,
    "negative_controls": [
      "budget_surface_merge_rejected",
      "budget_discontinuity_rejected",
      "cross_artifact_live_ledger_claim_rejected"
    ],
    "ordering_requirements": [
      "budget surface must be declared before policy execution",
      "budget before/after must be serialized for each native policy action"
    ],
    "phase_8_absorption_notes": "Cross-cutting contract needed before any native absorption claims. It may be implemented as shared validation before component policies.",
    "phase_8_readiness": "required_cross_cutting_contract",
    "policy_record": "native_budget_surface_contract_record",
    "requirement_type": "cross_cutting_contract",
    "row_id": "n10_i14_contract_06_budget_surface_separation",
    "runtime_visible_inputs": [
      "node_plus_packet_budget_before_after",
      "route_memory_budget_before_after",
      "goal_proxy_budget_before_after",
      "surface_or_claim_budget_before_after_if_declared"
    ],
    "source_gap_row_ids": [
      "n10_c_gap_09_budget_surfaces_and_source_continuity"
    ],
    "stale_context_blockers": [
      "budget_surface_ambiguity_blocked",
      "cross_artifact_budget_relabelled_live_ledger_blocked"
    ]
  }
]
```

## Phase 8 Absorption Order

```json
[
  {
    "absorption_step_digest": "8bc9dbf49a930826000e1d1be74628206ab34ae8e8c33b6ce4258c785e05f99f",
    "contract_rows": [
      "n10_i14_contract_06_budget_surface_separation"
    ],
    "may_open_native_agentic_like_support": false,
    "order": 1,
    "phase": "cross_cutting_budget_and_replay_contract",
    "reason": "All later native policies need separated budget surfaces and replay rules."
  },
  {
    "absorption_step_digest": "1e86a5d069cd7074969d18bf0b2faadd6048ad6ca0010d84ce125edb98222ce5",
    "contract_rows": [
      "n10_i14_contract_02_route_conductance_memory"
    ],
    "may_open_native_agentic_like_support": false,
    "order": 2,
    "phase": "route_conductance_memory_absorption",
    "reason": "N08 memory/trail is a concrete missing constitutive policy."
  },
  {
    "absorption_step_digest": "e2749aa45c6ef370b1f282971e47020cd9a4604025bb3b0175dfd45e463c0a2b",
    "contract_rows": [
      "n10_i14_contract_03_goal_proxy_regulation"
    ],
    "may_open_native_agentic_like_support": false,
    "order": 3,
    "phase": "goal_proxy_response_magnitude_absorption",
    "reason": "N09 native regulation remains blocked by response magnitude policy."
  },
  {
    "absorption_step_digest": "eb59b4de081dd0c4ed2dd2af12492e56f9ff821d8a42f5788ef71be115a23dee",
    "contract_rows": [
      "n10_i14_contract_04_identity_support_validator"
    ],
    "may_open_native_agentic_like_support": false,
    "order": 4,
    "phase": "identity_support_validator_hardening",
    "reason": "Identity acceptance is theory-sensitive and must remain distinct from support survival."
  },
  {
    "absorption_step_digest": "39f87286162765dbe868ab203463b21b2676db6952260fa0cf31e5be97356266",
    "contract_rows": [
      "n10_i14_contract_01_route_context"
    ],
    "may_open_native_agentic_like_support": false,
    "order": 5,
    "phase": "route_context_contract_hardening_if_needed",
    "reason": "Route context is currently selection-only; broaden only if N11 needs it."
  },
  {
    "absorption_step_digest": "8f88bca65fc6d508018c1c31f951ec5ac047772d20140b18722defd3f843892f",
    "contract_rows": [
      "n10_i14_contract_05_native_integration_gate"
    ],
    "may_open_native_agentic_like_support": false,
    "order": 6,
    "phase": "native_agentic_like_integration_meta_policy",
    "reason": "The meta-policy should only follow component policy contracts."
  }
]
```

## Controls

```json
{
  "all_required_policy_records_defined": {
    "control_passed": true,
    "primary_blocker": "native_policy_contract_record_missing",
    "reason": "Every required native policy or cross-cutting contract record is defined."
  },
  "artifact_replay_requirements_defined": {
    "control_passed": true,
    "primary_blocker": "artifact_replay_contract_missing",
    "reason": "Every contract row defines artifact replay requirements."
  },
  "budget_surfaces_separated": {
    "control_passed": true,
    "primary_blocker": "budget_surface_contract_missing",
    "reason": "Every contract row defines budget surfaces."
  },
  "claim_boundary_controls_defined": {
    "control_passed": true,
    "primary_blocker": "claim_boundary_controls_missing",
    "reason": "Every contract row defines claim-boundary controls."
  },
  "iteration_13_inventory_consumed": {
    "control_passed": true,
    "primary_blocker": "iteration_13_gap_inventory_missing",
    "reason": "Iteration 14 consumes the passed Iteration 13 inventory."
  },
  "negative_controls_defined": {
    "control_passed": true,
    "primary_blocker": "native_policy_negative_controls_missing",
    "reason": "Every contract row defines negative controls."
  },
  "no_native_support_opened": {
    "control_passed": true,
    "primary_blocker": "native_support_opened_by_contract_only_iteration",
    "reason": "Iteration 14 is contract-only and opens no native support flags."
  },
  "ordering_and_stale_context_defined": {
    "control_passed": true,
    "primary_blocker": "native_policy_ordering_or_stale_blocker_missing",
    "reason": "Every contract row defines ordering and stale-context blockers."
  },
  "runtime_visible_inputs_required": {
    "control_passed": true,
    "primary_blocker": "runtime_visible_policy_inputs_missing",
    "reason": "Every contract row lists runtime-visible inputs."
  }
}
```

## Checks

```json
{
  "absorption_order_digests_valid": true,
  "all_contract_row_digests_valid": true,
  "all_required_policy_records_defined": true,
  "artifact_replay_requirements_defined": true,
  "budget_surfaces_defined": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "fully_native_agentic_like_integration_still_blocked": true,
  "iteration_13_blockers_preserved": true,
  "iteration_13_inventory_passed": true,
  "negative_and_claim_controls_defined": true,
  "ordering_and_stale_context_defined": true,
  "phase_8_absorption_order_defined": true,
  "runtime_visible_inputs_defined": true,
  "src_clean_for_iteration_14": true
}
```

## Claim Boundary

All native agentic-like integration, agency, intention, semantic goal
ownership, identity acceptance, RC identity collapse, ACO, biological,
personhood, locomotion-like, and unrestricted agency claims remain
blocked.

## Reproduction

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/build_n10_iteration_14_hypothesis_c_native_contract_requirements.py
```

Output digest:

```text
0ec283968d91de44d2960bcc15fbdce740658ba356c5603dc8183108b8069a7f
```
