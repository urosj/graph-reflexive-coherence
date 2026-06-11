# N06 Iteration 6 SC4 Context-Swap Controls

- status: `passed`
- generated: `2026-06-05T21:45:05.481754+00:00`
- command: `.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_6_sc4_context_swap_controls.py`
- context A selected: `route_a`
- context B selected: `route_b`

## Boundary

- SC4 confirms matched context-swap behavior using the same serialized native route-arbitration policy and validator.
- The current fixture is context-swap scoped; no independent polarity surface is claimed.
- No topology event is committed, no packet is scheduled, and no semantic-choice/agency/memory/identity/movement claim is promoted.

## Acceptance

```json
{
  "budget_exact": true,
  "claim_ceiling": "context_swap_route_selection_candidate",
  "context_a_selected_route": "route_a",
  "context_b_selected_route": "route_b",
  "fixture_scope": "context_swap_only_no_independent_polarity_surface",
  "forbidden_runtime_inputs_absent": true,
  "hidden_direction_labels_absent": true,
  "packet_scheduled_by_arbitration": false,
  "same_policy_thresholds_and_validator": true,
  "sc_level": "SC4",
  "selection_swapped_by_serialized_context": true,
  "semantic_choice_claim_allowed": false,
  "status": "passed",
  "topology_event_committed": false
}
```

## Matched Settings

```json
{
  "arbitration_rule": "highest_score",
  "budget_tolerance": 1e-09,
  "candidate_set_order_key": "score_desc_then_candidate_id",
  "checks": {
    "same_arbitration_rule": true,
    "same_budget_tolerance": true,
    "same_candidate_set_order_key": true,
    "same_fixture_id": true,
    "same_policy_id": true,
    "same_score_tolerance": true,
    "same_source_surface_digest": true,
    "same_unresolved_tie_policy": true,
    "same_validator_scope": true
  },
  "context_a_budget_errors": [
    0.0,
    0.0
  ],
  "context_a_score_tolerance": 1e-09,
  "context_b_budget_errors": [
    0.0,
    0.0
  ],
  "context_b_score_tolerance": 1e-09,
  "fixture_id": "N06_S0_source_two_route_context_fork_v1",
  "matched": true,
  "policy_id": "score_ordered_topology_route_candidates",
  "score_tolerance": 1e-09,
  "unresolved_tie_policy": "fail_closed",
  "validator_scope": "sc4_context_swap_pre_topology_commit"
}
```

## Swap Replay

```json
{
  "checks": {
    "candidate_set_digests_distinct": true,
    "context_a_rejected_route_b": true,
    "context_a_relation_replayable": true,
    "context_a_selected_route_a": true,
    "context_b_rejected_route_a": true,
    "context_b_relation_replayable": true,
    "context_b_selected_route_b": true,
    "no_direction_or_polarity_labels": true,
    "no_forbidden_runtime_inputs": true,
    "selected_candidate_digests_distinct": true,
    "selection_swapped": true
  },
  "context_a_direction_labels": [],
  "context_a_forbidden_runtime_inputs": [],
  "context_a_rejected_candidate_digests": [
    "a2242288597254149c8a2e49161cd5f94843d3e01ebdaac4d1237995993e7edf"
  ],
  "context_a_rejected_routes": [
    "route_b"
  ],
  "context_a_selected_candidate_digest": "6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde",
  "context_a_selected_route": "route_a",
  "context_b_direction_labels": [],
  "context_b_forbidden_runtime_inputs": [],
  "context_b_rejected_candidate_digests": [
    "7085bb595cd67defdbbfd74cafec61158c5476097efed680111833e2f4cb3d9a"
  ],
  "context_b_rejected_routes": [
    "route_a"
  ],
  "context_b_selected_candidate_digest": "43b70f9309c436d9a19073a197b3d6290133fe6f6cd0e2ddb637e1362acdbb3d",
  "context_b_selected_route": "route_b",
  "swap_replayable": true
}
```

## Controls

```json
{
  "budget_mismatch": {
    "control_id": "budget_mismatch",
    "detail": {
      "budget_tolerance": 1e-09,
      "mutated_budget_prediction": {
        "node_plus_packet_budget_after": 5.0,
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_error": -1.0
      },
      "route_arbitration_record": {
        "arbitration_reason_code": "native_route_arbitration_budget_invalid",
        "arbitration_rule": "highest_score",
        "arbitration_runtime_visible_inputs": [
          "candidate_route_score",
          "candidate_order_key",
          "candidate_set_order_key",
          "active_context_node_id:4",
          "compatible_route_id:route_a",
          "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ],
        "arbitration_score": 0.0,
        "artifact_kind": "lgrc9v3_native_route_arbitration_record",
        "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
        "candidate_set_digest": "c8fcc81a44a1da681df7f6b283e30959fe4d44ca55d58684f5b6d020c4fdeb67",
        "candidate_set_id": "native-route-candidate-set:a729de2d50f5c669f262616f7281e106",
        "causal_layer_mode": "topology_changing_causal_history",
        "claim_flags": {
          "adaptive_topology_entry_allowed": false,
          "adaptive_topology_movement_claim_allowed": false,
          "agency_claim_allowed": false,
          "biological_claim_allowed": false,
          "identity_acceptance_claim_allowed": false,
          "locomotion_like_claim_allowed": false,
          "loop_driven_movement_claim_allowed": false,
          "movement_claim_allowed": false,
          "native_lgrc_choice_selection_claim_allowed": false,
          "native_m6": false,
          "rc_identity_collapse_claim_allowed": false,
          "semantic_choice_claim_allowed": false,
          "topology_mutating_movement_claim_allowed": false,
          "unrestricted_movement_claim_allowed": false
        },
        "event_time_key": 1.0,
        "evidence_class": "native_route_arbitration",
        "idempotency_key": "7b8fff308d50690c5ad2b1b5a1dee187d7a388c6f850ebfaf58107a4aa41329b",
        "lgrc_runtime_level": "lgrc3",
        "mode_version": "lgrc3_topology_contract_v1",
        "native_route_arbitration_digest": "b50646a07b1b6cd0d764dc8da49968cfd8ad0d81409085f5dbd16636b4003628",
        "native_route_arbitration_enabled": true,
        "native_route_arbitration_policy_id": "score_ordered_topology_route_candidates",
        "native_route_arbitration_record_id": "native-route-arbitration:dba40dbdc5c8af5b496a8bc8cc1e200d",
        "rejected_candidate_route_digests": [
          "0d5d653624559d5f8a4c34f74de42215109e9730120f5705e53d720848ecd95a",
          "a2242288597254149c8a2e49161cd5f94843d3e01ebdaac4d1237995993e7edf"
        ],
        "runtime_family": "LGRC9V3",
        "scheduler_event_index": 1,
        "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
        "selected_candidate_route_digest": null,
        "selected_candidate_route_id": null,
        "selected_topology_event_digest": null,
        "selected_topology_event_id": null
      }
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_budget_invalid",
    "scope": "native_arbitration_control"
  },
  "claim_promotion": {
    "control_id": "claim_promotion",
    "detail": [
      "native_route_arbitration_claim_promotion_blocked:native-route-arbitration:60c268a4a965f371a105666dd4e5da56",
      "corrupted_native_route_arbitration_record:native-route-arbitration:60c268a4a965f371a105666dd4e5da56:native route arbitration cannot promote claim flag: semantic_choice_claim_allowed"
    ],
    "passed": true,
    "primary_blocker": "native_route_arbitration_claim_promotion_blocked",
    "scope": "artifact_replay_control"
  },
  "hidden_direction": {
    "control_id": "hidden_direction",
    "detail": {
      "artifact_semantic_validator": {
        "failure_reasons": [
          "n06_hidden_direction_label_rejected"
        ],
        "valid": false
      },
      "injected_direction_labels": [
        "direction_label:route_a"
      ],
      "positive_lane_direction_labels": []
    },
    "passed": true,
    "primary_blocker": "n06_hidden_direction_label_rejected",
    "scope": "artifact_semantic_replay_control"
  },
  "order_inversion": {
    "control_id": "order_inversion",
    "detail": {
      "failure_reasons": [
        "n06_context_order_inversion_blocked"
      ],
      "valid": false
    },
    "passed": true,
    "primary_blocker": "n06_context_order_inversion_blocked",
    "scope": "artifact_corruption_control"
  },
  "unswapped_context": {
    "control_id": "unswapped_context",
    "detail": {
      "checks": {
        "paired_context_b_changes_selection": true,
        "same_context_repeats_same_selection": true
      },
      "first_context": "context_a",
      "first_selected_route": "route_a",
      "paired_context_changes_route": true,
      "paired_swap_context": "context_b",
      "paired_swap_selected_route": "route_b",
      "second_context": "context_a",
      "second_selected_route": "route_a",
      "selection_swapped": false
    },
    "passed": true,
    "primary_blocker": "n06_unswapped_context_blocked",
    "scope": "n06_sc4_validator"
  },
  "wrong_polarity": {
    "control_id": "wrong_polarity",
    "detail": {
      "actual_lane_context_state_id": "context_b",
      "expected_underlying_reasons": [
        "n06_stale_context_surface_blocked",
        "n06_context_relation_mismatch",
        "n06_context_evidence_not_replayable"
      ],
      "expected_underlying_reasons_present": [
        "n06_stale_context_surface_blocked",
        "n06_context_relation_mismatch",
        "n06_context_evidence_not_replayable"
      ],
      "semantic_validator": {
        "failure_reasons": [
          "n06_stale_context_surface_blocked",
          "n06_context_relation_mismatch",
          "n06_context_evidence_not_replayable"
        ],
        "valid": false
      },
      "wrong_expected_context_state_id": "context_a"
    },
    "passed": true,
    "primary_blocker": "n06_wrong_context_or_polarity_blocked",
    "scope": "n06_sc4_validator"
  }
}
```

## Artifact Digests

```json
{
  "acceptance_digest": "2c2c1c138ad04de179b351caacd0c3638cac27f9ce3f286a3d25da68f9d0238f",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "context_a_lane_digest": "153d2255f0f31656ce56b1ae5a5f6ebc06000c8df69bd0c9b23288e703783d97",
  "context_b_lane_digest": "d1b96176bfc224b9eb29b79389b0140bf3fb2a3f933d7f2ff120e74185217c8b",
  "controls_digest": "53abaa7f7457b7aa511f7972acea95b6056644a01431fb521d79059c18e81bdd",
  "matched_settings_digest": "f9c67eb7959616231b20c9ed3cffd1a713cd7d9d0cc7b2fd48f61095cb7b5a2c",
  "swap_replay_digest": "b3bf8e48e429cff26e8fef4b7f8965e61461f6acb3fba5bba1bdfdbb9f26de43"
}
```
