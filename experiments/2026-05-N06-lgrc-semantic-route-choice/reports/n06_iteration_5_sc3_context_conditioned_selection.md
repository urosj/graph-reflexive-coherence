# N06 Iteration 5 SC3 Context-Conditioned Selection

- status: `passed`
- generated: `2026-06-05T21:12:10.685695+00:00`
- command: `.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_5_sc3_context_conditioned_selection.py`
- context A selected: `route_a`
- context B selected: `route_b`

## Boundary

- SC3 proves context-conditioned route selection under the same serialized native arbitration policy.
- It does not commit topology, schedule post-selection packets, or promote semantic-choice/agency/memory/identity/movement claims.

## Payload Scope

Full candidate route records are retained in the JSON artifact as replay payloads because the context relation lives in candidate runtime-visible inputs, score components, budget predictions, and lineage maps. The report/checklist summarize by digest and selected/rejected route ids.

```json
{
  "full_candidate_route_records_in_json": true,
  "reason": "SC3 and SC6 replay need candidate runtime-visible context inputs, score components, budget predictions, and lineage maps.",
  "report_and_checklist_summarize_by_digest": true,
  "visual_or_summary_rows_are_not_source_of_truth": true
}
```

## Candidate-Set Identity

Candidate-set ids are not treated as context-unique. Candidate-set digests distinguish the context lanes.

```json
{
  "candidate_set_digests_equal": false,
  "candidate_set_id_is_not_context_unique": true,
  "candidate_set_ids_equal": true,
  "context_a_candidate_set_digest": "b2e4fc1d53538a2c75a0127e5876ddc5de2f8faba102759774d5a8ad855af081",
  "context_a_candidate_set_id": "native-route-candidate-set:a729de2d50f5c669f262616f7281e106",
  "context_b_candidate_set_digest": "e721a542cde7652fd3ef6ef341a166575c96de5022bc34ba937923e1921ec218",
  "context_b_candidate_set_id": "native-route-candidate-set:a729de2d50f5c669f262616f7281e106",
  "context_unique_key": "candidate_set_digest"
}
```

## Acceptance

```json
{
  "claim_ceiling": "context_conditioned_route_selection_candidate",
  "context_a_selected_route": "route_a",
  "context_b_selected_route": "route_b",
  "context_relation_replayable": true,
  "packet_scheduled_by_arbitration": false,
  "same_serialized_policy": true,
  "sc_level": "SC3",
  "selection_changes_with_context": true,
  "semantic_choice_claim_allowed": false,
  "status": "passed",
  "topology_event_committed": false
}
```

## Context A Replay

```json
{
  "active_context_node_id": 4,
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
  "arbitration_hidden_inputs": [],
  "arbitration_runtime_visible_inputs": [
    "active_context_node_id:4",
    "candidate_order_key",
    "candidate_route_score",
    "candidate_set_order_key",
    "compatible_route_id:route_a",
    "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
  ],
  "arbitration_score": 1.0,
  "candidate_score_component_sums": {
    "route_a": 1.0,
    "route_b": 0.4
  },
  "checks": {
    "arbitration_context_fields_serialized": true,
    "arbitration_hidden_inputs_absent": true,
    "arbitration_reason_selected_highest_score": true,
    "arbitration_score_equals_selected_candidate_score": true,
    "candidate_arbitration_context_consistent": true,
    "candidate_context_evidence_replayable": true,
    "candidate_route_scores_equal_component_sums": true,
    "hidden_inputs_absent": true,
    "selected_route_has_highest_score": true,
    "selected_route_matches_context_relation": true,
    "selected_route_matches_serialized_context_relation": true,
    "serialized_context_matches_expected_context": true,
    "serialized_context_values_agree_across_candidates": true
  },
  "compatible_route_id": "route_a",
  "context_relation_replayable": true,
  "context_state_id": "context_a",
  "per_candidate": {
    "route_a": {
      "actual_score": 1.0,
      "actual_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.6,
        "lineage_ready": 0.2
      },
      "checks": {
        "active_context_node_serialized": true,
        "candidate_route_id_serialized": true,
        "compatible_route_id_serialized": true,
        "context_fields_runtime_visible": true,
        "context_surface_digest_serialized": true,
        "no_hidden_inputs": true,
        "score_components_match_context_template": true,
        "score_matches_context_template": true
      },
      "expected_score": 1.0,
      "expected_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.6,
        "lineage_ready": 0.2
      },
      "hidden_inputs": [],
      "replay_ok": true,
      "runtime_visible_field_names": [
        "active_context_node_id",
        "candidate_budget_prediction",
        "candidate_lineage_transfer_map",
        "candidate_route_id",
        "candidate_score_components",
        "candidate_source_surface_digest",
        "compatible_route_id",
        "context_surface_digest",
        "serialized_route_arbitration_policy"
      ],
      "serialized_context_values": {
        "active_context_node_id": [
          "4"
        ],
        "compatible_route_id": [
          "route_a"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      }
    },
    "route_b": {
      "actual_score": 0.4,
      "actual_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.0,
        "lineage_ready": 0.2
      },
      "checks": {
        "active_context_node_serialized": true,
        "candidate_route_id_serialized": true,
        "compatible_route_id_serialized": true,
        "context_fields_runtime_visible": true,
        "context_surface_digest_serialized": true,
        "no_hidden_inputs": true,
        "score_components_match_context_template": true,
        "score_matches_context_template": true
      },
      "expected_score": 0.4,
      "expected_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.0,
        "lineage_ready": 0.2
      },
      "hidden_inputs": [],
      "replay_ok": true,
      "runtime_visible_field_names": [
        "active_context_node_id",
        "candidate_budget_prediction",
        "candidate_lineage_transfer_map",
        "candidate_route_id",
        "candidate_score_components",
        "candidate_source_surface_digest",
        "compatible_route_id",
        "context_surface_digest",
        "serialized_route_arbitration_policy"
      ],
      "serialized_context_values": {
        "active_context_node_id": [
          "4"
        ],
        "compatible_route_id": [
          "route_a"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      }
    }
  },
  "route_scores": {
    "route_a": 1.0,
    "route_b": 0.4
  },
  "score_tolerance": 1e-09,
  "selected_candidate_score": 1.0,
  "selected_route_id": "route_a",
  "serialized_context_summary": {
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
  "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
}
```

## Context B Replay

```json
{
  "active_context_node_id": 5,
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
  "arbitration_hidden_inputs": [],
  "arbitration_runtime_visible_inputs": [
    "active_context_node_id:5",
    "candidate_order_key",
    "candidate_route_score",
    "candidate_set_order_key",
    "compatible_route_id:route_b",
    "context_surface_digest:8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
  ],
  "arbitration_score": 1.0,
  "candidate_score_component_sums": {
    "route_a": 0.4,
    "route_b": 1.0
  },
  "checks": {
    "arbitration_context_fields_serialized": true,
    "arbitration_hidden_inputs_absent": true,
    "arbitration_reason_selected_highest_score": true,
    "arbitration_score_equals_selected_candidate_score": true,
    "candidate_arbitration_context_consistent": true,
    "candidate_context_evidence_replayable": true,
    "candidate_route_scores_equal_component_sums": true,
    "hidden_inputs_absent": true,
    "selected_route_has_highest_score": true,
    "selected_route_matches_context_relation": true,
    "selected_route_matches_serialized_context_relation": true,
    "serialized_context_matches_expected_context": true,
    "serialized_context_values_agree_across_candidates": true
  },
  "compatible_route_id": "route_b",
  "context_relation_replayable": true,
  "context_state_id": "context_b",
  "per_candidate": {
    "route_a": {
      "actual_score": 0.4,
      "actual_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.0,
        "lineage_ready": 0.2
      },
      "checks": {
        "active_context_node_serialized": true,
        "candidate_route_id_serialized": true,
        "compatible_route_id_serialized": true,
        "context_fields_runtime_visible": true,
        "context_surface_digest_serialized": true,
        "no_hidden_inputs": true,
        "score_components_match_context_template": true,
        "score_matches_context_template": true
      },
      "expected_score": 0.4,
      "expected_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.0,
        "lineage_ready": 0.2
      },
      "hidden_inputs": [],
      "replay_ok": true,
      "runtime_visible_field_names": [
        "active_context_node_id",
        "candidate_budget_prediction",
        "candidate_lineage_transfer_map",
        "candidate_route_id",
        "candidate_score_components",
        "candidate_source_surface_digest",
        "compatible_route_id",
        "context_surface_digest",
        "serialized_route_arbitration_policy"
      ],
      "serialized_context_values": {
        "active_context_node_id": [
          "5"
        ],
        "compatible_route_id": [
          "route_b"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      }
    },
    "route_b": {
      "actual_score": 1.0,
      "actual_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.6,
        "lineage_ready": 0.2
      },
      "checks": {
        "active_context_node_serialized": true,
        "candidate_route_id_serialized": true,
        "compatible_route_id_serialized": true,
        "context_fields_runtime_visible": true,
        "context_surface_digest_serialized": true,
        "no_hidden_inputs": true,
        "score_components_match_context_template": true,
        "score_matches_context_template": true
      },
      "expected_score": 1.0,
      "expected_score_components": {
        "budget_validity": 0.2,
        "context_match": 0.6,
        "lineage_ready": 0.2
      },
      "hidden_inputs": [],
      "replay_ok": true,
      "runtime_visible_field_names": [
        "active_context_node_id",
        "candidate_budget_prediction",
        "candidate_lineage_transfer_map",
        "candidate_route_id",
        "candidate_score_components",
        "candidate_source_surface_digest",
        "compatible_route_id",
        "context_surface_digest",
        "serialized_route_arbitration_policy"
      ],
      "serialized_context_values": {
        "active_context_node_id": [
          "5"
        ],
        "compatible_route_id": [
          "route_b"
        ],
        "context_surface_digest": [
          "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
        ]
      }
    }
  },
  "route_scores": {
    "route_a": 0.4,
    "route_b": 1.0
  },
  "score_tolerance": 1e-09,
  "selected_candidate_score": 1.0,
  "selected_route_id": "route_b",
  "serialized_context_summary": {
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
  "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
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
  "context_order_inversion": {
    "control_id": "context_order_inversion",
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
  "hidden_context": {
    "control_id": "hidden_context",
    "detail": {
      "artifact_replay_gate": {
        "failure_reasons": [
          "native_route_arbitration_hidden_input_rejected:route_a:['hidden_fixture_state']",
          "corrupted_native_route_candidate_record:route_a:native route-arbitration inputs contain hidden inputs: ['hidden_fixture_state']",
          "candidate_set_missing_candidate:native-route-candidate-set:a729de2d50f5c669f262616f7281e106:6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde",
          "native_route_arbitration_missing_selected_candidate:native-route-arbitration:60c268a4a965f371a105666dd4e5da56"
        ],
        "passed": true
      },
      "candidate_emission_gate": {
        "detail": "native_route_arbitration_hidden_input_rejected: ['hidden_fixture_state']",
        "passed": true
      }
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_hidden_input_rejected",
    "scope": "native_candidate_emission_and_artifact_replay"
  },
  "producer_mutation": {
    "control_id": "producer_mutation",
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
    "primary_blocker": "n06_producer_mutation_boundary_violation",
    "scope": "boundary_control"
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
    "scope": "n06_semantic_validator"
  }
}
```

## Artifact Digests

```json
{
  "acceptance_digest": "16c412651fd1666d86fd4caa4694c3f5b79d921d38bd50c1ce97974964954737",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "context_a_lane_digest": "c7367cbb552a5dee7ab2feee28bad9d33124dc0de805d6d2372f73fffdd728a1",
  "context_b_lane_digest": "4c2fcb77b3186423358641ccf9779e290f5efd2b71d34f7c5b3274ebf6d7544b",
  "controls_digest": "363bfc093449a8a5a7fb568e48499af33218401eac571860f503c8c5a01fb50a"
}
```
