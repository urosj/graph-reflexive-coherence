# N06 Iteration 8 SC6 Artifact-Only Replay And Closeout

- status: `passed`
- generated: `2026-06-06T00:04:46.183716+00:00`
- command: `.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_8_sc6_closeout.py`
- strongest supported SC level: `SC6`
- strongest claim ceiling: `artifact_only_semantic_route_choice_candidate`

## Boundary

- SC6 is an artifact-only evidence classification for N06 selection-only route choice.
- No selected topology event, post-selection packet scheduling, memory/trail, agency, identity, ACO, locomotion, biology, or unrestricted movement claim is promoted.
- Scheduled/processed packet evidence is marked not applicable for this pre-topology N06 closeout.

## Acceptance

```json
{
  "agency_claim_allowed": false,
  "artifact_only_replay_passed": true,
  "biological_claim_allowed": false,
  "budget_conservation_passed": true,
  "controls_passed": true,
  "identity_acceptance_claim_allowed": false,
  "locomotion_like_claim_allowed": false,
  "memory_or_trail_claim_allowed": false,
  "n07_handoff_ready": true,
  "producer_boundary_passed": true,
  "semantic_choice_claim_allowed": false,
  "status": "passed",
  "strongest_claim_ceiling": "artifact_only_semantic_route_choice_candidate",
  "strongest_supported_sc_level": "SC6",
  "unrestricted_movement_claim_allowed": false
}
```

## Artifact-Only Closeout

Native validator valid=false is expected because N06 SC6 is pre-topology and selection-only. Replay passes when the selection contract is valid and the only incomplete native-validator reason is missing selected-topology-event evidence.

```json
{
  "artifact_only": true,
  "candidate_set_identity": {
    "candidate_set_digests_distinct": true,
    "candidate_set_id_behavior": "candidate_set_id is stable across equivalent source/policy shape; candidate_set_digest is the context-specific replay key",
    "candidate_set_id_is_context_unique": true,
    "candidate_set_ids": [
      "native-route-candidate-set:2eb3d1248ced33eb4f89aa22ad208b39",
      "native-route-candidate-set:4cdd988a298d9525dcae631890e292ad",
      "native-route-candidate-set:64fa9d7e547e9e17c2be84140b7244e8",
      "native-route-candidate-set:d22fa40e0d2d09309fd5128c700f5095"
    ]
  },
  "checks": {
    "all_cycles_replayed": true,
    "artifact_only": true,
    "candidate_set_digests_distinct_across_cycles": true,
    "candidate_set_id_behavior_documented": true,
    "candidate_sets_replayed": true,
    "candidate_source_surface_provenance_replayed": true,
    "context_field_consistency_replayed": true,
    "context_relations_replayed": true,
    "expected_pre_topology_validator_incomplete_only": true,
    "native_arbitration_records_replayed": true,
    "record_claim_flags_remain_false": true,
    "runtime_state_not_used": true,
    "scheduled_processed_packet_evidence_scoped": true,
    "score_component_invariants_replayed": true,
    "selected_and_rejected_digests_replayed": true
  },
  "per_cycle": [
    {
      "arbitration_context_values": {
        "active_context_node_id": [
          "4"
        ],
        "compatible_route_id": [
          "route_a"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "arbitration_score": 1.0,
      "candidate_context_values": {
        "active_context_node_id": [
          "4"
        ],
        "candidate_route_id": [
          "route_a",
          "route_b"
        ],
        "compatible_route_id": [
          "route_a"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "candidate_score_component_sums": {
        "route_a": 1.0,
        "route_b": 0.4
      },
      "candidate_score_invariants": {
        "route_a": true,
        "route_b": true
      },
      "candidate_set_digest": "cc28d581e856d3782a840c63157f7b1d4d565387e8c00ed28b8365cba7b5f4a9",
      "candidate_set_id": "native-route-candidate-set:2eb3d1248ced33eb4f89aa22ad208b39",
      "candidate_source_surface_digests": [
        "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "checks": {
        "arbitration_candidate_context_fields_match": true,
        "arbitration_score_equals_selected_candidate_score": true,
        "candidate_route_records_replayed": true,
        "candidate_route_scores_equal_component_sums": true,
        "candidate_set_record_replayed": true,
        "candidate_source_surface_digest_matches_lane": true,
        "candidate_source_surface_digest_resolves_to_committed_source": true,
        "candidate_source_surface_digest_single": true,
        "candidate_source_surface_digests_non_null": true,
        "context_surface_and_relation_replayed": true,
        "native_route_arbitration_record_replayed": true,
        "native_selection_replayable_under_selection_only_scope": true,
        "native_validator_expected_pre_topology_incomplete": true,
        "processed_packet_evidence_not_applicable": true,
        "record_claim_flags_false": true,
        "rejected_candidate_digests_match_candidate_set": true,
        "runtime_state_not_used": true,
        "scheduled_packet_evidence_not_applicable": true,
        "selected_candidate_digest_in_candidate_set": true
      },
      "context_relation_replayable": true,
      "context_state_id": "context_a",
      "cycle_id": "cycle_0",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:eace620e6fcb858637b0c4665dedf6a8:0"
      ],
      "native_validator_valid": false,
      "record_claim_flags_false": {
        "candidate_records": true,
        "candidate_set_record": true,
        "route_arbitration_record": true
      },
      "rejected_candidate_route_digests": [
        "56eba296ce0ae91bb1e0b9c44557be6b52dd2932cd0bd6453156608114f07b0a"
      ],
      "replay_ok": true,
      "scheduled_processed_packet_evidence": {
        "applicability": "not_applicable_pre_topology_selection_only_scope",
        "processed_packet_count": 0,
        "scheduled_packet_count": 0
      },
      "selected_candidate_route_digest": "7e94c09f12ba57b1a057b462d3e3f8931a65e399511ad5fd8255fdc97d5cdcd8",
      "selected_candidate_route_score": 1.0,
      "selected_route": "route_a",
      "selection_contract_valid_under_pre_topology_scope": true,
      "source_surface_provenance": {
        "candidate_sources_committed": true,
        "primary_blocker_for_unknown_source": "native_route_candidate_committed_source_surface_required",
        "source_artifact": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json",
        "source_iteration": 3,
        "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9",
        "source_surface_id": "surface:lgrc9v3-packet-event-e4640f8f786889f0:route_local_pulse_contact",
        "source_surface_kind": "route_local_pulse_contact",
        "unknown_source_digest_control_passed": true
      },
      "unexpected_failure_reasons": []
    },
    {
      "arbitration_context_values": {
        "active_context_node_id": [
          "5"
        ],
        "compatible_route_id": [
          "route_b"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "arbitration_score": 1.0,
      "candidate_context_values": {
        "active_context_node_id": [
          "5"
        ],
        "candidate_route_id": [
          "route_a",
          "route_b"
        ],
        "compatible_route_id": [
          "route_b"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "candidate_score_component_sums": {
        "route_a": 0.4,
        "route_b": 1.0
      },
      "candidate_score_invariants": {
        "route_a": true,
        "route_b": true
      },
      "candidate_set_digest": "5c8918b0cdf07c3c5b303bf2c71d4c5c184370f5b875dc01af6b3aaff2506648",
      "candidate_set_id": "native-route-candidate-set:d22fa40e0d2d09309fd5128c700f5095",
      "candidate_source_surface_digests": [
        "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "checks": {
        "arbitration_candidate_context_fields_match": true,
        "arbitration_score_equals_selected_candidate_score": true,
        "candidate_route_records_replayed": true,
        "candidate_route_scores_equal_component_sums": true,
        "candidate_set_record_replayed": true,
        "candidate_source_surface_digest_matches_lane": true,
        "candidate_source_surface_digest_resolves_to_committed_source": true,
        "candidate_source_surface_digest_single": true,
        "candidate_source_surface_digests_non_null": true,
        "context_surface_and_relation_replayed": true,
        "native_route_arbitration_record_replayed": true,
        "native_selection_replayable_under_selection_only_scope": true,
        "native_validator_expected_pre_topology_incomplete": true,
        "processed_packet_evidence_not_applicable": true,
        "record_claim_flags_false": true,
        "rejected_candidate_digests_match_candidate_set": true,
        "runtime_state_not_used": true,
        "scheduled_packet_evidence_not_applicable": true,
        "selected_candidate_digest_in_candidate_set": true
      },
      "context_relation_replayable": true,
      "context_state_id": "context_b",
      "cycle_id": "cycle_1",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:cedb62d6f7288c3b80e66cae4d985410:0"
      ],
      "native_validator_valid": false,
      "record_claim_flags_false": {
        "candidate_records": true,
        "candidate_set_record": true,
        "route_arbitration_record": true
      },
      "rejected_candidate_route_digests": [
        "6c56a159bc33d047f6017d8baec972244bff49ca3df60954c1bbf0a41b6cf707"
      ],
      "replay_ok": true,
      "scheduled_processed_packet_evidence": {
        "applicability": "not_applicable_pre_topology_selection_only_scope",
        "processed_packet_count": 0,
        "scheduled_packet_count": 0
      },
      "selected_candidate_route_digest": "21ff5096388e202c1c708be518b6966013049873a36fb34e9eedf245e9d79c63",
      "selected_candidate_route_score": 1.0,
      "selected_route": "route_b",
      "selection_contract_valid_under_pre_topology_scope": true,
      "source_surface_provenance": {
        "candidate_sources_committed": true,
        "primary_blocker_for_unknown_source": "native_route_candidate_committed_source_surface_required",
        "source_artifact": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json",
        "source_iteration": 3,
        "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9",
        "source_surface_id": "surface:lgrc9v3-packet-event-e4640f8f786889f0:route_local_pulse_contact",
        "source_surface_kind": "route_local_pulse_contact",
        "unknown_source_digest_control_passed": true
      },
      "unexpected_failure_reasons": []
    },
    {
      "arbitration_context_values": {
        "active_context_node_id": [
          "4"
        ],
        "compatible_route_id": [
          "route_a"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "arbitration_score": 1.0,
      "candidate_context_values": {
        "active_context_node_id": [
          "4"
        ],
        "candidate_route_id": [
          "route_a",
          "route_b"
        ],
        "compatible_route_id": [
          "route_a"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "candidate_score_component_sums": {
        "route_a": 1.0,
        "route_b": 0.4
      },
      "candidate_score_invariants": {
        "route_a": true,
        "route_b": true
      },
      "candidate_set_digest": "30217e1dcc8c533d3175131d2b2be0a265829a41714fe338a1330982b6c8e510",
      "candidate_set_id": "native-route-candidate-set:64fa9d7e547e9e17c2be84140b7244e8",
      "candidate_source_surface_digests": [
        "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "checks": {
        "arbitration_candidate_context_fields_match": true,
        "arbitration_score_equals_selected_candidate_score": true,
        "candidate_route_records_replayed": true,
        "candidate_route_scores_equal_component_sums": true,
        "candidate_set_record_replayed": true,
        "candidate_source_surface_digest_matches_lane": true,
        "candidate_source_surface_digest_resolves_to_committed_source": true,
        "candidate_source_surface_digest_single": true,
        "candidate_source_surface_digests_non_null": true,
        "context_surface_and_relation_replayed": true,
        "native_route_arbitration_record_replayed": true,
        "native_selection_replayable_under_selection_only_scope": true,
        "native_validator_expected_pre_topology_incomplete": true,
        "processed_packet_evidence_not_applicable": true,
        "record_claim_flags_false": true,
        "rejected_candidate_digests_match_candidate_set": true,
        "runtime_state_not_used": true,
        "scheduled_packet_evidence_not_applicable": true,
        "selected_candidate_digest_in_candidate_set": true
      },
      "context_relation_replayable": true,
      "context_state_id": "context_a",
      "cycle_id": "cycle_2",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:ef3e9c9a4d37bb19f8b312c71b9989b5:0"
      ],
      "native_validator_valid": false,
      "record_claim_flags_false": {
        "candidate_records": true,
        "candidate_set_record": true,
        "route_arbitration_record": true
      },
      "rejected_candidate_route_digests": [
        "a7e307a6e2a456fa2765169f936361f8591e9c382a79d7acffc18c89779c3f7b"
      ],
      "replay_ok": true,
      "scheduled_processed_packet_evidence": {
        "applicability": "not_applicable_pre_topology_selection_only_scope",
        "processed_packet_count": 0,
        "scheduled_packet_count": 0
      },
      "selected_candidate_route_digest": "56df5ea777c43a139b3d26d314b41affc82cedafd8dc54e7f1af615cb43d52a1",
      "selected_candidate_route_score": 1.0,
      "selected_route": "route_a",
      "selection_contract_valid_under_pre_topology_scope": true,
      "source_surface_provenance": {
        "candidate_sources_committed": true,
        "primary_blocker_for_unknown_source": "native_route_candidate_committed_source_surface_required",
        "source_artifact": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json",
        "source_iteration": 3,
        "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9",
        "source_surface_id": "surface:lgrc9v3-packet-event-e4640f8f786889f0:route_local_pulse_contact",
        "source_surface_kind": "route_local_pulse_contact",
        "unknown_source_digest_control_passed": true
      },
      "unexpected_failure_reasons": []
    },
    {
      "arbitration_context_values": {
        "active_context_node_id": [
          "5"
        ],
        "compatible_route_id": [
          "route_b"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "arbitration_score": 1.0,
      "candidate_context_values": {
        "active_context_node_id": [
          "5"
        ],
        "candidate_route_id": [
          "route_a",
          "route_b"
        ],
        "compatible_route_id": [
          "route_b"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      },
      "candidate_score_component_sums": {
        "route_a": 0.4,
        "route_b": 1.0
      },
      "candidate_score_invariants": {
        "route_a": true,
        "route_b": true
      },
      "candidate_set_digest": "cc8603974788f12118e143fb8f6c96ae3ef6eb1c021e3a6c6c14aba8469db765",
      "candidate_set_id": "native-route-candidate-set:4cdd988a298d9525dcae631890e292ad",
      "candidate_source_surface_digests": [
        "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
      ],
      "checks": {
        "arbitration_candidate_context_fields_match": true,
        "arbitration_score_equals_selected_candidate_score": true,
        "candidate_route_records_replayed": true,
        "candidate_route_scores_equal_component_sums": true,
        "candidate_set_record_replayed": true,
        "candidate_source_surface_digest_matches_lane": true,
        "candidate_source_surface_digest_resolves_to_committed_source": true,
        "candidate_source_surface_digest_single": true,
        "candidate_source_surface_digests_non_null": true,
        "context_surface_and_relation_replayed": true,
        "native_route_arbitration_record_replayed": true,
        "native_selection_replayable_under_selection_only_scope": true,
        "native_validator_expected_pre_topology_incomplete": true,
        "processed_packet_evidence_not_applicable": true,
        "record_claim_flags_false": true,
        "rejected_candidate_digests_match_candidate_set": true,
        "runtime_state_not_used": true,
        "scheduled_packet_evidence_not_applicable": true,
        "selected_candidate_digest_in_candidate_set": true
      },
      "context_relation_replayable": true,
      "context_state_id": "context_b",
      "cycle_id": "cycle_3",
      "expected_incomplete_reasons": [
        "selected_topology_event_count_mismatch:native-route-arbitration:fcbf3151d9f779a74ca5d1a43cffaeea:0"
      ],
      "native_validator_valid": false,
      "record_claim_flags_false": {
        "candidate_records": true,
        "candidate_set_record": true,
        "route_arbitration_record": true
      },
      "rejected_candidate_route_digests": [
        "7bd9d0e3c92cc61ef267466ee39de3f53d5dfe4dacbd7c33b9d4b91583afb2b8"
      ],
      "replay_ok": true,
      "scheduled_processed_packet_evidence": {
        "applicability": "not_applicable_pre_topology_selection_only_scope",
        "processed_packet_count": 0,
        "scheduled_packet_count": 0
      },
      "selected_candidate_route_digest": "1732ca519398908214633ffb085a0c5d25b7c772891a025f5e7c1df0a5da7304",
      "selected_candidate_route_score": 1.0,
      "selected_route": "route_b",
      "selection_contract_valid_under_pre_topology_scope": true,
      "source_surface_provenance": {
        "candidate_sources_committed": true,
        "primary_blocker_for_unknown_source": "native_route_candidate_committed_source_surface_required",
        "source_artifact": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json",
        "source_iteration": 3,
        "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9",
        "source_surface_id": "surface:lgrc9v3-packet-event-e4640f8f786889f0:route_local_pulse_contact",
        "source_surface_kind": "route_local_pulse_contact",
        "unknown_source_digest_control_passed": true
      },
      "unexpected_failure_reasons": []
    }
  ],
  "runtime_state_used": false,
  "scope": "selection_only_pre_topology_commit",
  "source_surface_provenance": {
    "candidate_sources_committed": true,
    "primary_blocker_for_unknown_source": "native_route_candidate_committed_source_surface_required",
    "source_artifact": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_3_sc1_candidate_alternatives.json",
    "source_iteration": 3,
    "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9",
    "source_surface_id": "surface:lgrc9v3-packet-event-e4640f8f786889f0:route_local_pulse_contact",
    "source_surface_kind": "route_local_pulse_contact",
    "unknown_source_digest_control_passed": true
  },
  "valid_under_selection_only_scope": true,
  "validator_scope_note": "Native validator valid=false is expected because N06 SC6 is pre-topology and selection-only. Replay passes when the selection contract is valid and the only incomplete native-validator reason is missing selected-topology-event evidence."
}
```

## Controls

```json
{
  "budget_mismatch": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_budget_invalid",
    "scope": "native_arbitration_control",
    "source_iteration": 5
  },
  "claim_promotion": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_claim_promotion_blocked",
    "scope": "artifact_replay_control_all_cycles",
    "source_iteration": 7
  },
  "duplicate_arbitration": {
    "passed": true,
    "primary_blocker": "duplicate_native_route_arbitration_suppressed",
    "scope": "native_runtime_duplicate_suppression",
    "source_iteration": 7
  },
  "experiment_side_if_else": {
    "passed": true,
    "primary_blocker": "n06_experiment_side_selection_rejected",
    "scope": "sc6_artifact_level_hidden_input_control",
    "source_iteration": 8
  },
  "hidden_context": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_hidden_input_rejected",
    "scope": "native_candidate_emission_and_artifact_replay",
    "source_iteration": 5
  },
  "hidden_preference": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_hidden_input_rejected:hidden_route_preference",
    "scope": "sc6_artifact_level_hidden_input_control",
    "source_iteration": 8
  },
  "no_candidates": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_no_candidates",
    "scope": "native_runtime_with_experiment_injected_empty_candidate_set",
    "source_iteration": 4
  },
  "order_inversion": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_order_invalid",
    "scope": "native_runtime_with_experiment_injected_order_invalid_candidate_set",
    "source_iteration": 4
  },
  "policy_disabled": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_policy_disabled",
    "scope": "native_runtime",
    "source_iteration": 4
  },
  "posthoc_threshold_change": {
    "passed": true,
    "primary_blocker": "n06_posthoc_threshold_change_rejected",
    "scope": "sc6_artifact_level_hidden_input_control",
    "source_iteration": 8
  },
  "preselected_sink": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_hidden_input_rejected:preselected_sink",
    "scope": "sc6_artifact_level_hidden_input_control",
    "source_iteration": 8
  },
  "producer_mutation": {
    "passed": true,
    "primary_blocker": "n06_producer_mutation_boundary_violation",
    "scope": "boundary_control_all_cycles",
    "source_iteration": 7
  },
  "report_side_selection": {
    "passed": true,
    "primary_blocker": "n06_report_side_selection_rejected",
    "scope": "sc6_artifact_level_hidden_input_control",
    "source_iteration": 8
  },
  "stale_candidate": {
    "passed": true,
    "primary_blocker": "n06_stale_candidate_route_blocked",
    "scope": "sc6_artifact_semantic_replay_control",
    "source_iteration": 8
  },
  "stale_context": {
    "passed": true,
    "primary_blocker": "n06_stale_context_surface_blocked",
    "scope": "n06_sc5_validator",
    "source_iteration": 7
  },
  "unresolved_tie": {
    "passed": true,
    "primary_blocker": "native_route_arbitration_unresolved_tie",
    "scope": "native_runtime",
    "source_iteration": 4
  }
}
```

## N07 Handoff

```json
{
  "artifact_replay_passed": true,
  "artifact_replay_required": true,
  "blocked_inheritance": [
    "memory_or_trail_claim",
    "agency_claim",
    "agentic_like_claim",
    "rc_identity_collapse_claim",
    "identity_acceptance_claim",
    "goal_proxy_regulation_claim",
    "locomotion_like_claim",
    "biological_claim",
    "ant_colony_claim",
    "unrestricted_movement_claim"
  ],
  "budget_conservation_passed": true,
  "budget_conservation_required": true,
  "claim_boundary_clean": true,
  "handoff_scope": "N07 may use N06's artifact-only route-choice candidate as route selection background, but must independently validate RC identity and attractor invariance.",
  "minimum_sc_level_met": "SC6",
  "recommendation": "proceed_to_N07_rc_identity_attractor_invariance",
  "required_controls_passed": true
}
```

## Artifact Digests

```json
{
  "acceptance_digest": "e3207fdfea331cb8f6247969cc862832e4d0d5e189b4606d732efd4f621c18a8",
  "artifact_only_closeout_digest": "2ddaa59790379e61a6ad4e8c1b9dfa8f6ec1497e99d579cfcafb5b0ea6ff1e49",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "closeout_digest": "4c1be1ca6e0f2789ca0ed31d1b612b502e41b1585faca7f941d58eda39f3f456",
  "control_matrix_digest": "6be8ce15fe33797dbd739ab1194e2daf7a95ec095c5a09789365a7311778fe60",
  "control_summary_digest": "7df542decb40be021f340a0cbbd57039d1fdb4e56e0314c4803e90d5334f2609",
  "n07_handoff_digest": "379622e310655b53f2211437a145114a035a1963e41f7ee51d150405d1fe3514",
  "positive_artifacts_digest": "bd5a9bfa5c34aa915d67404afc9848fa8dabc1871ec08cdff7b56231ec681f64",
  "source_artifacts_digest": "af85abce7cc36b2a967f8f2beb75cac955edb6b69f41705a39e94959539889d0"
}
```
