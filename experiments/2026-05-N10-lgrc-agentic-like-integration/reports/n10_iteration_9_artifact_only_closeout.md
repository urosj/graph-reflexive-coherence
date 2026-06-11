# N10 Iteration 9 Artifact-Only Replay And Closeout

Status: `passed`.

## Result

Iteration 9 reconstructed the N10 integration chain from exported
artifacts only. The closeout validates the support/regulation base,
the disrupted-support negative control, explicit restoration, the
route-memory-regulation composition, and the bounded repeated
integration window.

```text
final_n10_ceiling = bounded_artifact_only_agentic_like_integration_candidate
integration_level = A6
n10_category_level = ALI6
bounded_window_count = 4
artifact_only = true
runtime_state_used = false
```

## Boundary

This closeout is an artifact-only bounded integration candidate. It is
not a claim of agency, intention, semantic goal ownership, identity
acceptance, ACO behavior, biological behavior, personhood, or
unrestricted agency.

```json
{
  "claim_flags": {
    "aco_like_claim_allowed": false,
    "agency_claim_allowed": false,
    "agentic_like_claim_allowed": false,
    "ant_colony_claim_allowed": false,
    "biological_claim_allowed": false,
    "goal_ownership_claim_allowed": false,
    "identity_acceptance_claim_allowed": false,
    "intention_claim_allowed": false,
    "locomotion_like_claim_allowed": false,
    "personhood_claim_allowed": false,
    "rc_identity_collapse_claim_allowed": false,
    "runtime_identity_acceptance_claim_allowed": false,
    "semantic_choice_claim_allowed": false,
    "semantic_goal_understanding_claim_allowed": false,
    "unrestricted_agency_claim_allowed": false,
    "unrestricted_identity_claim_allowed": false,
    "unrestricted_movement_claim_allowed": false
  },
  "memory_scope": "N08_MEM6_serialized_producer_policy_memory_or_trail",
  "native_policy_gaps_preserved": [
    "native_agentic_like_integration_policy_missing",
    "native_identity_acceptance_validator_missing",
    "native_response_magnitude_policy_missing_for_unbounded_perturbations",
    "native_route_conductance_memory_policy_missing"
  ],
  "regulation_scope": "N09_GPR5_repeated_window_and_GPR6_closeout",
  "route_context_scope": "N06_SC6_selection_only_pre_topology_commit",
  "support_scope": "support_intact_main_lane_with_mild_withdrawal_companion"
}
```

## Interpretation

What makes the N10 closeout significant is not that it proves agency;
it explicitly does not. It shows that the N06-N09 pieces can be
composed into a bounded, replayable integration chain:

```text
route choice
-> memory-shaped affordance
-> identity/support survival
-> goal-proxy regulation
```

The composition survives repeated cycles with clean source links, exact
budget checks, stale-source controls, hidden-steering controls, and no
claim leakage. The mild-withdrawal companion is especially useful
because it shows the integration is not only valid in the perfectly
intact support baseline.

## Positive Replay Records

```json
[
  {
    "artifact_key": "n10_iteration_3_support_aware_regulation_replay",
    "artifact_only": true,
    "checks_passed": true,
    "claim_flags_false": true,
    "controls_passed": true,
    "integration_level": "A4",
    "n10_category_level": "ALI2",
    "replay_step_digest": "2ae4ff9386e233650b145b59425700d567e97b14a6f7079f3a274218d6667fad",
    "row_digest": "9fbae51d0b50441a11f7a6005948af283de6b8a1baea2bfc1029eabfe998b220",
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 3,
    "step": "support_intact_regulation_replay",
    "support_state_tag": "support_intact_survives"
  },
  {
    "artifact_key": "n10_iteration_4_mild_withdrawal_survival_replay",
    "artifact_only": true,
    "checks_passed": true,
    "claim_flags_false": true,
    "controls_passed": true,
    "integration_level": "A4",
    "n10_category_level": "ALI2",
    "replay_step_digest": "06cb90561604f6a96d35f34ab790753fe759dd5ef6d96df4afec37bcdfe8db1f",
    "row_digest": "e285f5245df3710111445b5eeb9688d378c63824b30153be1b9dc53901faf313",
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 4,
    "step": "mild_withdrawal_support_survival_replay",
    "support_state_tag": "mild_withdrawal_survives"
  },
  {
    "artifact_key": "n10_iteration_6_explicit_restoration_replay",
    "artifact_only": true,
    "checks_passed": true,
    "claim_flags_false": true,
    "controls_passed": true,
    "integration_allowed": true,
    "integration_level": "A4",
    "n10_category_level": "ALI3",
    "replay_step_digest": "04da60e6264cca8b9f1a6c1c91bfb9e4f3645f6672c3748c5ba8083731671ea9",
    "row_digest": "7dd3f8df667d098a22ca34af5ca3d72f027b7471b3966f55b87bd14da6a4e5cf",
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 6,
    "step": "explicit_restoration_resumes_support_sensitive_replay",
    "support_state_tag": "explicit_restoration_recovers_support"
  },
  {
    "artifact_key": "n10_iteration_7_route_memory_regulation_composition",
    "artifact_only": true,
    "checks_passed": true,
    "claim_flags_false": true,
    "controls_passed": true,
    "integration_allowed": true,
    "integration_level": "A4",
    "memory_scope_tag": "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "n10_category_level": "ALI4",
    "replay_step_digest": "3871a41644d6642e95b87895df7cdc7b80e205af1b083adbf2e80e9ca4a0960f",
    "route_context_tag": "route_context_selection_only",
    "row_digest": "61c9878ab7b25bbdba922804d3b9cd9a6e5dfb4f467ddc20375a5e956ddd7f79",
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 7,
    "step": "route_memory_regulation_composition",
    "support_state_tag": "support_intact_survives"
  },
  {
    "artifact_key": "n10_iteration_8_bounded_repeated_integration",
    "artifact_only": true,
    "checks_passed": true,
    "claim_flags_false": true,
    "controls_passed": true,
    "integration_allowed": true,
    "integration_level": "A5",
    "memory_scope_tag": "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "n10_category_level": "ALI5",
    "replay_step_digest": "3f2d08507f13699b218d729479d1242eb9f998f5271dfb7c4bc233c5ad659ab4",
    "route_context_tag": "route_context_selection_only",
    "row_digest": "8ad9934bc4cef846dfbc510661dc70f1bef1fa34b354a8c7087a70d25722559e",
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 8,
    "step": "bounded_repeated_integration_main",
    "support_state_tag": "support_intact_survives",
    "window_count": 4
  },
  {
    "artifact_key": "n10_iteration_8_bounded_repeated_integration",
    "artifact_only": true,
    "checks_passed": true,
    "claim_flags_false": true,
    "controls_passed": true,
    "integration_allowed": true,
    "integration_level": "A5",
    "memory_scope_tag": "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "n10_category_level": "ALI5",
    "replay_step_digest": "b2129e8271b579c62170a951f0dcdd2b62732d1168b8793e2f98ffe6ac41683b",
    "route_context_tag": "route_context_selection_only",
    "row_digest": "d56e47861c728bcd694e4601bb9fde17919373a7374306e1995acc33931f6bf3",
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 8,
    "step": "bounded_repeated_integration_mild_withdrawal_companion",
    "support_state_tag": "mild_withdrawal_survives",
    "window_count": 4
  }
]
```

## Negative Controls

```json
{
  "budget_controls": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "source_iterations": [
      3,
      4,
      5,
      6,
      7,
      8
    ]
  },
  "claim_promotion_controls": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "source_iterations": [
      3,
      4,
      5,
      6,
      7,
      8
    ]
  },
  "explicit_restoration_resumes_without_erasing_disruption": {
    "control_passed": true,
    "primary_blocker": null,
    "source_iterations": [
      5,
      6
    ]
  },
  "hidden_steering_controls": {
    "control_passed": true,
    "primary_blocker": "hidden_experiment_side_steering",
    "source_iterations": [
      7,
      8
    ]
  },
  "stale_source_controls": {
    "control_passed": true,
    "primary_blocker": "stale_source_control_failed",
    "source_iterations": [
      7,
      8
    ]
  },
  "support_disruption_blocks": {
    "blocked_record_digest": "56e2de6ab77b877a02cbc2df948f43be9461b4fa734232396d934b358edf426d",
    "control_passed": true,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "source_iteration": 5
  }
}
```

## Checks

```json
{
  "all_required_artifacts_present": true,
  "all_required_artifacts_status_passed": true,
  "budget_controls_passed": true,
  "claim_promotion_controls_passed": true,
  "closeout_ceiling_is_ali6": true,
  "closeout_claim_flags_all_false": true,
  "closeout_row_digest_valid": true,
  "explicit_restoration_control_passed": true,
  "hidden_steering_controls_passed": true,
  "iteration_8_main_is_ali5": true,
  "iteration_8_mild_companion_is_ali5": true,
  "positive_replay_record_digests_valid": true,
  "positive_replay_records_all_pass": true,
  "positive_replay_records_artifact_only": true,
  "prior_output_digests_valid": true,
  "runtime_state_not_used": true,
  "src_clean_for_iteration_9": true,
  "stale_source_controls_passed": true,
  "support_disruption_control_passed": true
}
```

## N11 Handoff

```json
{
  "carry_forward_boundaries": [
    "N10 is artifact-only and source-backed, not native agency",
    "N06 route context remains selection-only",
    "N08 memory/trail is serialized producer-policy evidence",
    "N09 regulation remains goal-proxy regulation, not goal ownership",
    "N07 support evidence is support/invariance evidence, not identity acceptance"
  ],
  "next_question": "Does bounded agentic-like integration generalize across changing contexts, support states, and proxy conditions without hidden steering or claim leakage?",
  "ready": true
}
```

## Acceptance

Iteration 9 passes if an artifact-only closeout validator reconstructs the bounded N10 route-memory-support-regulation integration chain and all controls without private runtime state. The closeout must either set the conservative ceiling to `bounded_artifact_only_agentic_like_integration_candidate` or record the exact blocker that prevents it.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_9_artifact_only_closeout.py
```

Output digest:

```text
97346d8284d684f535170627226a1ca5d7c4cadbf05fe8ee46a82771755e51eb
```
