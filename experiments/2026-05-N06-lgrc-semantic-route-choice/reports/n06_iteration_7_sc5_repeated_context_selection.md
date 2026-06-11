# N06 Iteration 7 SC5 Repeated Context-Conditioned Selection

- status: `passed`
- generated: `2026-06-05T22:55:22.215738+00:00`
- command: `.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_7_sc5_repeated_context_selection.py`
- context sequence: `['context_a', 'context_b', 'context_a', 'context_b']`
- selected route sequence: `['route_a', 'route_b', 'route_a', 'route_b']`

## Boundary

- SC5 repeats context-conditioned native route arbitration across distinct independent runtime windows.
- This is not a single-runtime persistence or accumulated budget-drift test.
- Each selected route is reconstructed from serialized context evidence in its own window.
- No topology event is committed, no packet is scheduled, and no semantic-choice/agency/memory/identity/movement claim is promoted.

## Scope Notes

```json
{
  "cross_window_budget_accumulation_tested": false,
  "cross_window_state_persistence_tested": false,
  "hidden_schedule_control_scope": "N06 experiment-level semantic artifact replay control; native LGRC route arbitration only rejects the hidden-input fields in its current contract.",
  "independent_runtime_instances_per_cycle": true,
  "memory_or_trail_deferred_to": "N08",
  "repeated_windows_not_long_lived_memory": true,
  "selection_causality_basis": "artifact replay checks serialized context fields, context score components, selected/rejected digests, and native arbitration records for each independent cycle.",
  "selection_sequence_alone_is_not_causality_proof": true,
  "single_runtime_multi_window_persistence_tested": false,
  "stale_context_and_order_controls": "N06 artifact-level semantic replay controls until a future Phase 8 native semantic-context validator exists."
}
```

## Acceptance

```json
{
  "artifact_only_replay_reconstructs_every_selection": true,
  "budget_exact": true,
  "claim_ceiling": "repeated_context_conditioned_route_selection_candidate",
  "context_sequence": [
    "context_a",
    "context_b",
    "context_a",
    "context_b"
  ],
  "cross_window_budget_accumulation_tested": false,
  "cycle_count": 4,
  "distinct_window_ids": true,
  "hidden_schedule_or_preauthored_selection_used": false,
  "independent_runtime_instances_per_cycle": true,
  "packet_scheduled_by_arbitration": false,
  "sc_level": "SC5",
  "selected_route_sequence": [
    "route_a",
    "route_b",
    "route_a",
    "route_b"
  ],
  "selected_route_sequence_matches_context_sequence": true,
  "selection_causality_basis": "serialized_context_relation_replay_and_native_selection_replay",
  "semantic_choice_claim_allowed": false,
  "single_runtime_multi_window_persistence_tested": false,
  "status": "passed",
  "topology_event_committed": false,
  "trail_like_state_created": false
}
```

## Cycle Replay

```json
{
  "arbitration_window_ids": [
    "n06_window_context_state_candidate_emission_v1:cycle_0",
    "n06_window_context_state_candidate_emission_v1:cycle_1",
    "n06_window_context_state_candidate_emission_v1:cycle_2",
    "n06_window_context_state_candidate_emission_v1:cycle_3"
  ],
  "checks": {
    "arbitration_window_ids_distinct": true,
    "candidate_set_digests_distinct": true,
    "cycle_count_is_four": true,
    "cycle_ids_distinct": true,
    "distinct_context_input_signatures": true,
    "every_cycle_replayable": true,
    "no_forbidden_runtime_inputs": true,
    "no_trail_like_runtime_inputs": true,
    "repeated_context_input_signatures_stable": true,
    "selected_route_sequence_matches_context_sequence": true,
    "serialized_context_causality_replayable_all_cycles": true
  },
  "context_input_signatures_by_context": {
    "context_a": [
      [
        "active_context_node_id:4",
        "compatible_route_id:route_a",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      [
        "active_context_node_id:4",
        "compatible_route_id:route_a",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ]
    ],
    "context_b": [
      [
        "active_context_node_id:5",
        "compatible_route_id:route_b",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      [
        "active_context_node_id:5",
        "compatible_route_id:route_b",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ]
    ]
  },
  "context_sequence": [
    "context_a",
    "context_b",
    "context_a",
    "context_b"
  ],
  "expected_route_sequence_from_context": [
    "route_a",
    "route_b",
    "route_a",
    "route_b"
  ],
  "forbidden_runtime_inputs": [],
  "per_cycle": [
    {
      "arbitration_window_id": "n06_window_context_state_candidate_emission_v1:cycle_0",
      "candidate_set_digest": "cc28d581e856d3782a840c63157f7b1d4d565387e8c00ed28b8365cba7b5f4a9",
      "checks": {
        "arbitration_window_id_present": true,
        "artifact_selection_replay_clean": true,
        "budget_exact": true,
        "candidate_set_window_matches_cycle": true,
        "claim_flags_remain_false": true,
        "cycle_id_present": true,
        "no_forbidden_runtime_inputs": true,
        "no_packet_scheduled": true,
        "no_topology_commit": true,
        "route_arbitration_consumes_candidate_set": true,
        "selected_and_rejected_digests_present": true,
        "selected_route_matches_current_context": true,
        "serialized_context_replayable": true,
        "uses_committed_current_context_evidence": true
      },
      "context_input_signature": [
        "active_context_node_id:4",
        "compatible_route_id:route_a",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "context_state_id": "context_a",
      "cycle_id": "cycle_0",
      "cycle_index": 0,
      "expected_compatible_route": "route_a",
      "rejected_candidate_route_digests": [
        "56eba296ce0ae91bb1e0b9c44557be6b52dd2932cd0bd6453156608114f07b0a"
      ],
      "replay_ok": true,
      "selected_candidate_route_digest": "7e94c09f12ba57b1a057b462d3e3f8931a65e399511ad5fd8255fdc97d5cdcd8",
      "selected_route": "route_a"
    },
    {
      "arbitration_window_id": "n06_window_context_state_candidate_emission_v1:cycle_1",
      "candidate_set_digest": "5c8918b0cdf07c3c5b303bf2c71d4c5c184370f5b875dc01af6b3aaff2506648",
      "checks": {
        "arbitration_window_id_present": true,
        "artifact_selection_replay_clean": true,
        "budget_exact": true,
        "candidate_set_window_matches_cycle": true,
        "claim_flags_remain_false": true,
        "cycle_id_present": true,
        "no_forbidden_runtime_inputs": true,
        "no_packet_scheduled": true,
        "no_topology_commit": true,
        "route_arbitration_consumes_candidate_set": true,
        "selected_and_rejected_digests_present": true,
        "selected_route_matches_current_context": true,
        "serialized_context_replayable": true,
        "uses_committed_current_context_evidence": true
      },
      "context_input_signature": [
        "active_context_node_id:5",
        "compatible_route_id:route_b",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "context_state_id": "context_b",
      "cycle_id": "cycle_1",
      "cycle_index": 1,
      "expected_compatible_route": "route_b",
      "rejected_candidate_route_digests": [
        "6c56a159bc33d047f6017d8baec972244bff49ca3df60954c1bbf0a41b6cf707"
      ],
      "replay_ok": true,
      "selected_candidate_route_digest": "21ff5096388e202c1c708be518b6966013049873a36fb34e9eedf245e9d79c63",
      "selected_route": "route_b"
    },
    {
      "arbitration_window_id": "n06_window_context_state_candidate_emission_v1:cycle_2",
      "candidate_set_digest": "30217e1dcc8c533d3175131d2b2be0a265829a41714fe338a1330982b6c8e510",
      "checks": {
        "arbitration_window_id_present": true,
        "artifact_selection_replay_clean": true,
        "budget_exact": true,
        "candidate_set_window_matches_cycle": true,
        "claim_flags_remain_false": true,
        "cycle_id_present": true,
        "no_forbidden_runtime_inputs": true,
        "no_packet_scheduled": true,
        "no_topology_commit": true,
        "route_arbitration_consumes_candidate_set": true,
        "selected_and_rejected_digests_present": true,
        "selected_route_matches_current_context": true,
        "serialized_context_replayable": true,
        "uses_committed_current_context_evidence": true
      },
      "context_input_signature": [
        "active_context_node_id:4",
        "compatible_route_id:route_a",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "context_state_id": "context_a",
      "cycle_id": "cycle_2",
      "cycle_index": 2,
      "expected_compatible_route": "route_a",
      "rejected_candidate_route_digests": [
        "a7e307a6e2a456fa2765169f936361f8591e9c382a79d7acffc18c89779c3f7b"
      ],
      "replay_ok": true,
      "selected_candidate_route_digest": "56df5ea777c43a139b3d26d314b41affc82cedafd8dc54e7f1af615cb43d52a1",
      "selected_route": "route_a"
    },
    {
      "arbitration_window_id": "n06_window_context_state_candidate_emission_v1:cycle_3",
      "candidate_set_digest": "cc8603974788f12118e143fb8f6c96ae3ef6eb1c021e3a6c6c14aba8469db765",
      "checks": {
        "arbitration_window_id_present": true,
        "artifact_selection_replay_clean": true,
        "budget_exact": true,
        "candidate_set_window_matches_cycle": true,
        "claim_flags_remain_false": true,
        "cycle_id_present": true,
        "no_forbidden_runtime_inputs": true,
        "no_packet_scheduled": true,
        "no_topology_commit": true,
        "route_arbitration_consumes_candidate_set": true,
        "selected_and_rejected_digests_present": true,
        "selected_route_matches_current_context": true,
        "serialized_context_replayable": true,
        "uses_committed_current_context_evidence": true
      },
      "context_input_signature": [
        "active_context_node_id:5",
        "compatible_route_id:route_b",
        "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "context_state_id": "context_b",
      "cycle_id": "cycle_3",
      "cycle_index": 3,
      "expected_compatible_route": "route_b",
      "rejected_candidate_route_digests": [
        "7bd9d0e3c92cc61ef267466ee39de3f53d5dfe4dacbd7c33b9d4b91583afb2b8"
      ],
      "replay_ok": true,
      "selected_candidate_route_digest": "1732ca519398908214633ffb085a0c5d25b7c772891a025f5e7c1df0a5da7304",
      "selected_route": "route_b"
    }
  ],
  "replay_ok": true,
  "selected_route_sequence": [
    "route_a",
    "route_b",
    "route_a",
    "route_b"
  ],
  "trail_like_runtime_inputs": []
}
```

## Artifact-Only Replay

```json
{
  "all_cycles_reconstructed": true,
  "artifact_only": true,
  "cycle_count": 4,
  "independent_native_validator_invoked_per_cycle": true,
  "per_cycle": [
    {
      "artifact_only": true,
      "context_relation_replayable": true,
      "cycle_id": "cycle_0",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:eace620e6fcb858637b0c4665dedf6a8:0"
      ],
      "independent_native_validator_invoked": true,
      "matches_lane_selection_contract": true,
      "native_validator_valid": false,
      "replay_ok": true,
      "route_selection_reconstructed_from_artifacts": true,
      "runtime_state_used": false,
      "selection_contract_valid_under_pre_topology_scope": true,
      "unexpected_failure_reasons": []
    },
    {
      "artifact_only": true,
      "context_relation_replayable": true,
      "cycle_id": "cycle_1",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:cedb62d6f7288c3b80e66cae4d985410:0"
      ],
      "independent_native_validator_invoked": true,
      "matches_lane_selection_contract": true,
      "native_validator_valid": false,
      "replay_ok": true,
      "route_selection_reconstructed_from_artifacts": true,
      "runtime_state_used": false,
      "selection_contract_valid_under_pre_topology_scope": true,
      "unexpected_failure_reasons": []
    },
    {
      "artifact_only": true,
      "context_relation_replayable": true,
      "cycle_id": "cycle_2",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:ef3e9c9a4d37bb19f8b312c71b9989b5:0"
      ],
      "independent_native_validator_invoked": true,
      "matches_lane_selection_contract": true,
      "native_validator_valid": false,
      "replay_ok": true,
      "route_selection_reconstructed_from_artifacts": true,
      "runtime_state_used": false,
      "selection_contract_valid_under_pre_topology_scope": true,
      "unexpected_failure_reasons": []
    },
    {
      "artifact_only": true,
      "context_relation_replayable": true,
      "cycle_id": "cycle_3",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:fcbf3151d9f779a74ca5d1a43cffaeea:0"
      ],
      "independent_native_validator_invoked": true,
      "matches_lane_selection_contract": true,
      "native_validator_valid": false,
      "replay_ok": true,
      "route_selection_reconstructed_from_artifacts": true,
      "runtime_state_used": false,
      "selection_contract_valid_under_pre_topology_scope": true,
      "unexpected_failure_reasons": []
    }
  ],
  "runtime_state_used": false,
  "validator_scope": "sc5_repeated_context_selection_pre_topology_commit"
}
```

## Controls

```json
{
  "budget_drift": {
    "control_id": "budget_drift",
    "detail": {
      "cross_cycle_budget_accumulation_tested": false,
      "scope_note": "Single-candidate budget-mismatch control reused as the SC5 budget guard. Cross-cycle accumulated budget drift is not tested because SC5 uses independent runtime windows.",
      "source_control": {
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
      }
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_budget_invalid",
    "scope": "native_arbitration_control"
  },
  "claim_promotion": {
    "control_id": "claim_promotion",
    "detail": {
      "per_cycle": [
        {
          "cycle_id": "cycle_0",
          "detail": [
            "native_route_arbitration_claim_promotion_blocked:native-route-arbitration:eace620e6fcb858637b0c4665dedf6a8",
            "corrupted_native_route_arbitration_record:native-route-arbitration:eace620e6fcb858637b0c4665dedf6a8:native route arbitration cannot promote claim flag: semantic_choice_claim_allowed"
          ],
          "passed": true,
          "primary_blocker": "native_route_arbitration_claim_promotion_blocked"
        },
        {
          "cycle_id": "cycle_1",
          "detail": [
            "native_route_arbitration_claim_promotion_blocked:native-route-arbitration:cedb62d6f7288c3b80e66cae4d985410",
            "corrupted_native_route_arbitration_record:native-route-arbitration:cedb62d6f7288c3b80e66cae4d985410:native route arbitration cannot promote claim flag: semantic_choice_claim_allowed"
          ],
          "passed": true,
          "primary_blocker": "native_route_arbitration_claim_promotion_blocked"
        },
        {
          "cycle_id": "cycle_2",
          "detail": [
            "native_route_arbitration_claim_promotion_blocked:native-route-arbitration:ef3e9c9a4d37bb19f8b312c71b9989b5",
            "corrupted_native_route_arbitration_record:native-route-arbitration:ef3e9c9a4d37bb19f8b312c71b9989b5:native route arbitration cannot promote claim flag: semantic_choice_claim_allowed"
          ],
          "passed": true,
          "primary_blocker": "native_route_arbitration_claim_promotion_blocked"
        },
        {
          "cycle_id": "cycle_3",
          "detail": [
            "native_route_arbitration_claim_promotion_blocked:native-route-arbitration:fcbf3151d9f779a74ca5d1a43cffaeea",
            "corrupted_native_route_arbitration_record:native-route-arbitration:fcbf3151d9f779a74ca5d1a43cffaeea:native route arbitration cannot promote claim flag: semantic_choice_claim_allowed"
          ],
          "passed": true,
          "primary_blocker": "native_route_arbitration_claim_promotion_blocked"
        }
      ]
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_claim_promotion_blocked",
    "scope": "artifact_replay_control_all_cycles"
  },
  "duplicate_arbitration": {
    "control_id": "duplicate_arbitration",
    "detail": {
      "count_after_first": 1,
      "count_after_second": 1,
      "idempotency_key_reconstructable": true,
      "reconstructed_idempotency_key": "e92bb157e29275dcaa11cd1c3bc70009a677d2b4864233f6f354e7531edb71fc",
      "recorded_idempotency_key": "e92bb157e29275dcaa11cd1c3bc70009a677d2b4864233f6f354e7531edb71fc",
      "same_arbitration_digest": true,
      "same_idempotency_key": true,
      "same_route_arbitration_artifact": true
    },
    "passed": true,
    "primary_blocker": "duplicate_native_route_arbitration_suppressed",
    "scope": "native_runtime_duplicate_suppression"
  },
  "hidden_schedule": {
    "control_id": "hidden_schedule",
    "detail": {
      "per_cycle": [
        {
          "cycle_id": "cycle_0",
          "failure_reasons": [
            "n06_hidden_schedule_rejected"
          ],
          "forbidden_runtime_inputs": [
            "hidden_schedule:cycle_index_to_route",
            "preauthored_route_sequence:route_a,route_b,route_a,route_b"
          ],
          "passed": true,
          "valid": false
        },
        {
          "cycle_id": "cycle_1",
          "failure_reasons": [
            "n06_hidden_schedule_rejected"
          ],
          "forbidden_runtime_inputs": [
            "hidden_schedule:cycle_index_to_route",
            "preauthored_route_sequence:route_a,route_b,route_a,route_b"
          ],
          "passed": true,
          "valid": false
        },
        {
          "cycle_id": "cycle_2",
          "failure_reasons": [
            "n06_hidden_schedule_rejected"
          ],
          "forbidden_runtime_inputs": [
            "hidden_schedule:cycle_index_to_route",
            "preauthored_route_sequence:route_a,route_b,route_a,route_b"
          ],
          "passed": true,
          "valid": false
        },
        {
          "cycle_id": "cycle_3",
          "failure_reasons": [
            "n06_hidden_schedule_rejected"
          ],
          "forbidden_runtime_inputs": [
            "hidden_schedule:cycle_index_to_route",
            "preauthored_route_sequence:route_a,route_b,route_a,route_b"
          ],
          "passed": true,
          "valid": false
        }
      ],
      "scope_note": "N06 experiment-level semantic artifact replay control; native LGRC has no dedicated hidden-schedule validator yet."
    },
    "passed": true,
    "primary_blocker": "n06_hidden_schedule_rejected",
    "scope": "artifact_semantic_replay_control_all_cycles"
  },
  "producer_mutation": {
    "control_id": "producer_mutation",
    "detail": {
      "per_cycle": [
        {
          "cycle_id": "cycle_0",
          "detail": {
            "attempted_forbidden_writes": [
              "active_node_coherence",
              "packet_ledger",
              "topology",
              "route_arbitration_record",
              "claim_flags"
            ],
            "packet_scheduled": false,
            "producer_invoked": false,
            "rejected_by_boundary": true
          },
          "passed": true,
          "primary_blocker": "n06_producer_mutation_boundary_violation"
        },
        {
          "cycle_id": "cycle_1",
          "detail": {
            "attempted_forbidden_writes": [
              "active_node_coherence",
              "packet_ledger",
              "topology",
              "route_arbitration_record",
              "claim_flags"
            ],
            "packet_scheduled": false,
            "producer_invoked": false,
            "rejected_by_boundary": true
          },
          "passed": true,
          "primary_blocker": "n06_producer_mutation_boundary_violation"
        },
        {
          "cycle_id": "cycle_2",
          "detail": {
            "attempted_forbidden_writes": [
              "active_node_coherence",
              "packet_ledger",
              "topology",
              "route_arbitration_record",
              "claim_flags"
            ],
            "packet_scheduled": false,
            "producer_invoked": false,
            "rejected_by_boundary": true
          },
          "passed": true,
          "primary_blocker": "n06_producer_mutation_boundary_violation"
        },
        {
          "cycle_id": "cycle_3",
          "detail": {
            "attempted_forbidden_writes": [
              "active_node_coherence",
              "packet_ledger",
              "topology",
              "route_arbitration_record",
              "claim_flags"
            ],
            "packet_scheduled": false,
            "producer_invoked": false,
            "rejected_by_boundary": true
          },
          "passed": true,
          "primary_blocker": "n06_producer_mutation_boundary_violation"
        }
      ]
    },
    "passed": true,
    "primary_blocker": "n06_producer_mutation_boundary_violation",
    "scope": "boundary_control_all_cycles"
  },
  "stale_context": {
    "control_id": "stale_context",
    "detail": {
      "failure_reasons": [
        "n06_stale_context_surface_blocked",
        "n06_context_evidence_not_replayable"
      ],
      "valid": false
    },
    "passed": true,
    "primary_blocker": "n06_stale_context_surface_blocked",
    "scope": "n06_sc5_validator"
  }
}
```

## Artifact Digests

```json
{
  "acceptance_digest": "93ad1330a3fae8dc7e9ea2583a9741aba2e4f798929ab71982570a4cdc5120d7",
  "artifact_only_replay_digest": "5043144f64df88a8a53f4d39e8ea395974c2b247918efc86e3d9d4d9a714b217",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "controls_digest": "be586f452e4695090040a88b1ca44095160d1de3e31ec5698372d0b5c9337c91",
  "cycle_replay_digest": "bd29bcf83ed78806ab6175235def176b7ee6df7cec078eeeee18a0078dcbb884",
  "lanes_digest": "09566526c057b358c163ccf01a6b2b492624da53b1bdd93489f1eccf1a3f012e"
}
```
