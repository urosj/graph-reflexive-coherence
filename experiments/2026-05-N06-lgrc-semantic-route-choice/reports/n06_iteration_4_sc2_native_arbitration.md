# N06 Iteration 4 SC2 Native Arbitration

- status: `passed`
- generated: `2026-06-05T20:31:25.617613+00:00`
- command: `.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_4_sc2_native_arbitration.py`
- selected candidate route: `route_a`
- selected candidate digest: `6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde`
- arbitration reason: `native_route_arbitration_selected_highest_score`
- authorized topology event digest: `78b06c790b612559c97716e521c485a769bc248693534f30b26a972ca54f3c01`

## Boundary

- SC2 emits one native route-arbitration record.
- The selected topology event id/digest is authorized by the arbitration record, but no topology event is committed in this iteration.
- No post-selection packet is scheduled and no claim flag is promoted.

## Acceptance

```json
{
  "candidate_set_consumed": true,
  "claim_ceiling": "native_route_arbitration_selection_no_context_swap",
  "context_swap_evidence_available": false,
  "exactly_one_route_selected": true,
  "packet_scheduled_by_arbitration": false,
  "route_arbitration_record_emitted": true,
  "sc_level": "SC2",
  "selected_route": "route_a",
  "selection_replayable_from_serialized_scores": true,
  "semantic_choice_claim_allowed": false,
  "status": "passed",
  "topology_event_committed": false
}
```

## Selection Replay

```json
{
  "arbitration_runtime_visible_inputs": [
    "candidate_order_key",
    "candidate_route_score",
    "candidate_set_order_key"
  ],
  "arbitration_score": 1.0,
  "candidate_scores": {
    "6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde": 1.0,
    "a2242288597254149c8a2e49161cd5f94843d3e01ebdaac4d1237995993e7edf": 0.4
  },
  "checks": {
    "arbitration_inputs_runtime_visible": true,
    "arbitration_score_equals_selected_candidate_score": true,
    "reason_code_selected_highest_score": true,
    "rejected_candidates_are_all_nonselected": true,
    "selected_candidate_has_highest_score": true,
    "selected_candidate_in_candidate_set": true,
    "selected_route_is_context_a_route_a": true
  },
  "expected_rejected_candidate_route_digests": [
    "a2242288597254149c8a2e49161cd5f94843d3e01ebdaac4d1237995993e7edf"
  ],
  "score_tolerance": 1e-09,
  "selected_candidate_route_digest": "6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde",
  "selected_candidate_route_id": "route_a",
  "selected_candidate_score": 1.0,
  "selection_replayable_from_serialized_scores": true
}
```

## Selection-Only Artifact Replay Scope

The full native route-arbitration validator expects a committed selected topology event. Iteration 4 records the expected pre-commit limitation and treats any other replay failure as a blocker.

```json
{
  "agency_claim_allowed": false,
  "artifact_only": true,
  "biological_claim_allowed": false,
  "candidate_route_count": 2,
  "candidate_set_count": 1,
  "candidate_set_reconstructed": true,
  "control_blockers": [],
  "downstream_lineage_reabsorption_producer_chain_reconstructed": false,
  "expected_incomplete_reasons": [
    "selected_topology_event_count_mismatch:native-route-arbitration:60c268a4a965f371a105666dd4e5da56:0"
  ],
  "failure_reasons": [
    "selected_topology_event_count_mismatch:native-route-arbitration:60c268a4a965f371a105666dd4e5da56:0"
  ],
  "identity_acceptance_claim_allowed": false,
  "lineage_replay_valid": null,
  "locomotion_like_claim_allowed": false,
  "native_lgrc_choice_selection_claim_allowed": false,
  "native_lgrc_route_arbitration_supported": false,
  "post_arbitration_linked_producer_count": 0,
  "rc_identity_collapse_claim_allowed": false,
  "route_arbitration_reconstructed": true,
  "route_arbitration_record_count": 1,
  "route_selection_reconstructed_from_artifacts": true,
  "runtime_state_used": false,
  "selected_route_arbitration_record_ids": [
    "native-route-arbitration:60c268a4a965f371a105666dd4e5da56"
  ],
  "selected_topology_event_count": 0,
  "selected_topology_event_reconstructed": false,
  "selection_contract_valid": true,
  "semantic_choice_claim_allowed": false,
  "unexpected_failure_reasons": [],
  "unrestricted_movement_claim_allowed": false,
  "valid": false,
  "validator": "validate_lgrc9v3_native_route_arbitration_artifacts",
  "validator_scope": "selection_only_pre_topology_commit"
}
```

## Controls

```json
{
  "budget_invalid": {
    "control_id": "budget_invalid",
    "detail": {
      "budget_error_exceeds_manifest_tolerance": true,
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
          "candidate_set_order_key"
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
        "native_route_arbitration_digest": "ca34bd5e13f3fa905a88a55a7e85cc603f1e366476a65762bd341199d20a51ad",
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
    "scope": "native_runtime"
  },
  "claim_promotion": {
    "control_id": "claim_promotion",
    "detail": {
      "failure_reasons": [
        "native_route_arbitration_claim_promotion_blocked:native-route-arbitration:60c268a4a965f371a105666dd4e5da56",
        "corrupted_native_route_arbitration_record:native-route-arbitration:60c268a4a965f371a105666dd4e5da56:native route arbitration cannot promote claim flag: semantic_choice_claim_allowed"
      ],
      "specific_claim_promotion_blocker_present": true
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_claim_promotion_blocked",
    "scope": "artifact_replay_control"
  },
  "duplicate_arbitration": {
    "control_id": "duplicate_arbitration",
    "detail": {
      "count_after_first": 1,
      "count_after_second": 1,
      "same_idempotency_key": true,
      "same_native_route_arbitration_digest": true,
      "same_route_arbitration_artifact": true
    },
    "passed": true,
    "primary_blocker": "duplicate_native_route_arbitration_suppressed",
    "scope": "native_runtime"
  },
  "hidden_input": {
    "control_id": "hidden_input",
    "detail": {
      "attempted_arbitration_runtime_visible_inputs": [
        "candidate_route_score",
        "report_code"
      ],
      "native_record_arbitration_runtime_visible_inputs": [
        "runtime_visible_input_validation"
      ],
      "route_arbitration_record": {
        "arbitration_reason_code": "native_route_arbitration_hidden_input_rejected",
        "arbitration_rule": "highest_score",
        "arbitration_runtime_visible_inputs": [
          "runtime_visible_input_validation"
        ],
        "arbitration_score": 0.0,
        "artifact_kind": "lgrc9v3_native_route_arbitration_record",
        "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
        "candidate_set_digest": "b2e4fc1d53538a2c75a0127e5876ddc5de2f8faba102759774d5a8ad855af081",
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
        "idempotency_key": "f37e3866a254c82d394321c1337fb1e7159ed503438adc25e8fbcdcd897b0f4e",
        "lgrc_runtime_level": "lgrc3",
        "mode_version": "lgrc3_topology_contract_v1",
        "native_route_arbitration_digest": "7750890443e9d0fd89d77cde43abf0693556286617abb41f9cc520a1dc65a78f",
        "native_route_arbitration_enabled": true,
        "native_route_arbitration_policy_id": "score_ordered_topology_route_candidates",
        "native_route_arbitration_record_id": "native-route-arbitration:e10c71f368fb73b7be0f440e881b4876",
        "rejected_candidate_route_digests": [
          "6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde",
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
    "primary_blocker": "native_route_arbitration_hidden_input_rejected",
    "scope": "native_runtime"
  },
  "no_candidates": {
    "control_id": "no_candidates",
    "detail": {
      "arbitration_reason_code": "native_route_arbitration_no_candidates",
      "arbitration_rule": "highest_score",
      "arbitration_runtime_visible_inputs": [
        "candidate_route_score",
        "candidate_order_key",
        "candidate_set_order_key"
      ],
      "arbitration_score": 0.0,
      "artifact_kind": "lgrc9v3_native_route_arbitration_record",
      "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
      "candidate_set_digest": "a0e4d6443b3f43e9de70f79dca7bf7b59b1e54347e7e14672c8ae81f70cd241a",
      "candidate_set_id": "native-route-candidate-set:a729de2d50f5c669f262616f7281e106:empty",
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
      "idempotency_key": "1a1465be17decdd2b516c78e00095678e0562f8bb2de7eccaac3e349a6641478",
      "lgrc_runtime_level": "lgrc3",
      "mode_version": "lgrc3_topology_contract_v1",
      "native_route_arbitration_digest": "c13bfe52ddd9fe69ae09439fc1f5ede8cc74b6200af90388ff44065b65abc913",
      "native_route_arbitration_enabled": true,
      "native_route_arbitration_policy_id": "score_ordered_topology_route_candidates",
      "native_route_arbitration_record_id": "native-route-arbitration:fb153efcada475b623fb26db095a9c9a",
      "rejected_candidate_route_digests": [],
      "runtime_family": "LGRC9V3",
      "scheduler_event_index": 1,
      "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
      "selected_candidate_route_digest": null,
      "selected_candidate_route_id": null,
      "selected_topology_event_digest": null,
      "selected_topology_event_id": null
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_no_candidates",
    "scope": "native_runtime_with_experiment_injected_empty_candidate_set"
  },
  "order_invalid": {
    "control_id": "order_invalid",
    "detail": {
      "arbitration_reason_code": "native_route_arbitration_order_invalid",
      "arbitration_rule": "highest_score",
      "arbitration_runtime_visible_inputs": [
        "candidate_route_score",
        "candidate_order_key",
        "candidate_set_order_key"
      ],
      "arbitration_score": 0.0,
      "artifact_kind": "lgrc9v3_native_route_arbitration_record",
      "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
      "candidate_set_digest": "92028056090ceace704fe508bed9d83ea53851241f52e202881a5a873aaf5402",
      "candidate_set_id": "native-route-candidate-set:a729de2d50f5c669f262616f7281e106:order-invalid",
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
      "idempotency_key": "a1655d78385a76e2ecabd8c0586a81f2eebe1397c6708826e4cca227b7f916c1",
      "lgrc_runtime_level": "lgrc3",
      "mode_version": "lgrc3_topology_contract_v1",
      "native_route_arbitration_digest": "91517f2efaef94e4f22f7bfc85bd85b7a257b3287a1d63f4a10e65722706d9c1",
      "native_route_arbitration_enabled": true,
      "native_route_arbitration_policy_id": "score_ordered_topology_route_candidates",
      "native_route_arbitration_record_id": "native-route-arbitration:46eaf5c64243f3fc6a8ad44c15d80f53",
      "rejected_candidate_route_digests": [
        "a2242288597254149c8a2e49161cd5f94843d3e01ebdaac4d1237995993e7edf",
        "6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde"
      ],
      "runtime_family": "LGRC9V3",
      "scheduler_event_index": 1,
      "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
      "selected_candidate_route_digest": null,
      "selected_candidate_route_id": null,
      "selected_topology_event_digest": null,
      "selected_topology_event_id": null
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_order_invalid",
    "scope": "native_runtime_with_experiment_injected_order_invalid_candidate_set"
  },
  "policy_disabled": {
    "control_id": "policy_disabled",
    "detail": {
      "emitted": false,
      "reason_code": "native_route_arbitration_policy_disabled",
      "route_arbitration_record": null
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_policy_disabled",
    "scope": "native_runtime"
  },
  "unresolved_tie": {
    "control_id": "unresolved_tie",
    "detail": {
      "arbitration_reason_code": "native_route_arbitration_unresolved_tie",
      "arbitration_rule": "highest_score",
      "arbitration_runtime_visible_inputs": [
        "candidate_route_score",
        "candidate_order_key",
        "candidate_set_order_key"
      ],
      "arbitration_score": 0.5,
      "artifact_kind": "lgrc9v3_native_route_arbitration_record",
      "artifact_schema_version": "lgrc9v3_native_route_arbitration_record_v1",
      "candidate_set_digest": "236dcd73947fc037ba841e334c82e3b0a1cc34df928312172703768b3394f752",
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
      "idempotency_key": "68f0e9ae2a2ce58ee8a4e655f1f5cba972c6f23242751008a0c0bcea1fedd558",
      "lgrc_runtime_level": "lgrc3",
      "mode_version": "lgrc3_topology_contract_v1",
      "native_route_arbitration_digest": "e40b612cec8074ec3b5532f5913b0875fa385497c692977b4e38919250e3dbfc",
      "native_route_arbitration_enabled": true,
      "native_route_arbitration_policy_id": "score_ordered_topology_route_candidates",
      "native_route_arbitration_record_id": "native-route-arbitration:d21a2cac9d25f28866bdae168226cf53",
      "rejected_candidate_route_digests": [
        "eba7ae0cf15cd63644eae79bff0060f034f56bbd87356f5e811ffddf8e6cea70",
        "6d7e7710858465e0ca9dd5a4f71e3a10f300ad09c0e49b41c857b2c4467ba54a"
      ],
      "runtime_family": "LGRC9V3",
      "scheduler_event_index": 1,
      "schema_version": "lgrc9v3_native_route_arbitration_record_v1",
      "selected_candidate_route_digest": null,
      "selected_candidate_route_id": null,
      "selected_topology_event_digest": null,
      "selected_topology_event_id": null
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_unresolved_tie",
    "scope": "native_runtime"
  }
}
```

## Artifact Digests

```json
{
  "acceptance_digest": "b1e6b8422201da05e71e339cca1b9464cf00a6314f1cbcca371e1b62f12269f5",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "controls_digest": "60af0cf7bbd9194ba5175e49e69551caf5552674e4722b83317899b7b436407a",
  "enabled_lane_digest": "3a8c41e74ae9299d04013957c1bc15a3d420d361e6b33f17ae9c996ade1eb225"
}
```
