# N06 Iteration 3 SC1 Candidate Alternatives

- status: `passed`
- generated: `2026-06-05T20:31:25.586292+00:00`
- command: `.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/run_n06_iteration_3_sc1_candidate_alternatives.py`
- source surface digest: `8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9`
- candidate route count: `2`
- candidate set digest: `b2e4fc1d53538a2c75a0127e5876ddc5de2f8faba102759774d5a8ad855af081`
- candidate order: `['route_a', 'route_b']`

## Boundary

- SC1 emits native candidate route records and one candidate set.
- It does not emit a route-arbitration record.
- It does not commit a selected topology event.
- It does not schedule packets or mutate state from candidate emission.
- It does not promote semantic choice, memory, agency, identity, movement, or ACO claims.

## Acceptance

```json
{
  "all_claim_flags_false": true,
  "candidate_alternatives_exposed": true,
  "candidate_set_contract_valid_pre_arbitration": true,
  "claim_ceiling": "candidate_alternatives_exposed_no_selection",
  "context_to_score_reconstructable": true,
  "default_off_no_candidates": true,
  "packet_scheduled_by_candidate_emission": false,
  "route_selected": false,
  "sc_level": "SC1",
  "semantic_choice_claim_allowed": false,
  "status": "passed",
  "topology_event_committed": false
}
```

## Candidate-Only Replay Scope

The full native route-arbitration validator is intentionally incomplete at SC1 because no arbitration record exists yet. Iteration 3 treats `no_native_route_arbitration_records` as the expected pre-arbitration limitation and fails on any other candidate/candidate-set replay issue.

```json
{
  "agency_claim_allowed": false,
  "artifact_only": true,
  "biological_claim_allowed": false,
  "candidate_route_count": 2,
  "candidate_set_contract_valid": true,
  "candidate_set_count": 1,
  "candidate_set_reconstructed": true,
  "control_blockers": [],
  "downstream_lineage_reabsorption_producer_chain_reconstructed": false,
  "expected_incomplete_reasons": [
    "no_native_route_arbitration_records"
  ],
  "failure_reasons": [
    "no_native_route_arbitration_records"
  ],
  "identity_acceptance_claim_allowed": false,
  "lineage_replay_valid": null,
  "locomotion_like_claim_allowed": false,
  "native_lgrc_choice_selection_claim_allowed": false,
  "native_lgrc_route_arbitration_supported": false,
  "post_arbitration_linked_producer_count": 0,
  "rc_identity_collapse_claim_allowed": false,
  "route_arbitration_reconstructed": false,
  "route_arbitration_record_count": 0,
  "route_selection_reconstructed_from_artifacts": false,
  "runtime_state_used": false,
  "selected_route_arbitration_record_ids": [],
  "selected_topology_event_count": 0,
  "selected_topology_event_reconstructed": false,
  "semantic_choice_claim_allowed": false,
  "unexpected_failure_reasons": [],
  "unrestricted_movement_claim_allowed": false,
  "valid": false,
  "validator": "validate_lgrc9v3_native_route_arbitration_artifacts",
  "validator_scope": "candidate_set_only_pre_arbitration"
}
```

## Context Derivation

```json
{
  "active_context_node_id": 4,
  "allowed_support_fields": [
    "candidate_budget_prediction",
    "candidate_lineage_transfer_map",
    "candidate_score_components",
    "candidate_source_surface_digest",
    "serialized_route_arbitration_policy"
  ],
  "comparison_tolerance": 1e-09,
  "compatible_route_id": "route_a",
  "context_state_id": "context_a",
  "context_to_score_reconstructable": true,
  "declared_context_fields": [
    "active_context_node_id",
    "candidate_route_id",
    "compatible_route_id",
    "context_surface_digest"
  ],
  "per_candidate": {
    "route_a": {
      "component_checks": {
        "budget_validity": true,
        "context_match": true,
        "lineage_ready": true
      },
      "reconstructable": true,
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
      "runtime_visible_input_checks": {
        "active_context_node_id_serialized": true,
        "candidate_route_id_serialized": true,
        "compatible_route_id_serialized": true,
        "context_surface_digest_serialized": true,
        "declared_context_fields_present": true,
        "no_undeclared_runtime_visible_fields": true
      },
      "undeclared_runtime_visible_field_names": []
    },
    "route_b": {
      "component_checks": {
        "budget_validity": true,
        "context_match": true,
        "lineage_ready": true
      },
      "reconstructable": true,
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
      "runtime_visible_input_checks": {
        "active_context_node_id_serialized": true,
        "candidate_route_id_serialized": true,
        "compatible_route_id_serialized": true,
        "context_surface_digest_serialized": true,
        "declared_context_fields_present": true,
        "no_undeclared_runtime_visible_fields": true
      },
      "undeclared_runtime_visible_field_names": []
    }
  },
  "source_surface_digest": "8fb2e0da8e055fc382aa74fdfeccdbec50c53afcfa161cfb3a7ba9db0b96f5d9"
}
```

## Controls

```json
{
  "claim_promotion": {
    "control_id": "claim_promotion",
    "detail": {
      "failure_reasons": [
        "native_route_arbitration_claim_promotion_blocked:route_a",
        "corrupted_native_route_candidate_record:route_a:native route candidate cannot promote claim flag: semantic_choice_claim_allowed",
        "candidate_set_missing_candidate:native-route-candidate-set:a729de2d50f5c669f262616f7281e106:6d04abb83cf639d1aca00ca27caaf8c00d0c95925075131966d588a6dc0c8bde",
        "no_native_route_arbitration_records"
      ],
      "side_effect_failures_allowed": [
        "corrupted record digest mismatch",
        "candidate set missing corrupted candidate digest",
        "no_native_route_arbitration_records at SC1 scope"
      ],
      "specific_claim_promotion_blocker_present": true
    },
    "passed": true,
    "primary_blocker": "native_route_arbitration_claim_promotion_blocked"
  },
  "duplicate_candidate": {
    "control_id": "duplicate_candidate",
    "detail": {
      "candidate_route_count_after_duplicate_input": 1,
      "candidate_set_route_digest_count": 1
    },
    "passed": true,
    "primary_blocker": "duplicate_native_route_candidate_suppressed"
  },
  "hidden_context": {
    "control_id": "hidden_context",
    "detail": "native_route_arbitration_hidden_input_rejected: ['hidden_fixture_state']",
    "passed": true,
    "primary_blocker": "native_route_arbitration_hidden_input_rejected"
  },
  "hidden_route": {
    "control_id": "hidden_route",
    "detail": "native_route_arbitration_hidden_input_rejected: ['experiment_if_else']",
    "passed": true,
    "primary_blocker": "native_route_arbitration_hidden_input_rejected"
  },
  "malformed_candidate": {
    "control_id": "malformed_candidate",
    "detail": "candidate_selected_sink_id must be in competing sinks",
    "passed": true,
    "primary_blocker": "native_route_candidate_schema_rejected_malformed_candidate"
  },
  "missing_budget_prediction": {
    "control_id": "missing_budget_prediction",
    "detail": "native_route_arbitration_budget_invalid: candidate_budget_prediction is required",
    "passed": true,
    "primary_blocker": "native_route_arbitration_budget_invalid"
  },
  "unknown_source_surface_digest": {
    "control_id": "unknown_source_surface_digest",
    "detail": "native route candidate requires committed source surface evidence",
    "passed": true,
    "primary_blocker": "native_route_candidate_committed_source_surface_required"
  }
}
```

## Artifact Digests

```json
{
  "acceptance_digest": "797e171d001749ee33d81798796dca1507e178113342bb2423be7f8728e4eb98",
  "claim_flags_digest": "9107d7c83c7cad6cf67508a0727b2ae7e6a1403c2ae889ecf04f35b885cb7fbd",
  "controls_digest": "0a282475cd1a0ecc5c7c2e90c0730db8ca43f51a14e0e5bfbac28d39468b6eca",
  "enabled_lane_digest": "c78e13ca3cfbfc3e3974aede500bad52632402bf4b8424a533c1c0a4e446b843"
}
```
