# N09 Iteration 2 Fixture Manifest Validation

Status: passed

Iteration 2 is contract-only. No proxy-regulation probe was run and no positive regulation evidence was generated.

## Contract Summary

- Default fixture family: `n09_default_active_node_band_regulation_v1`
- Memory-shaped lane required: True
- No-memory comparator required: True
- N06 packet execution inherited: False
- N07 withdrawal baseline available: False
- Oscillator fixture status: `deferred_secondary_fixture`
- Native goal-proxy regulation policy available: False

## Frozen Schemas

- Proxy surface row schema
- Target-band schema
- Error signal and error policy schema
- Regulation policy and response schema
- Route/producer evidence contract
- Packet scheduling/processing response contract
- Perturbation and support-withdrawal schemas
- Artifact-only replay requirements

## Boundary Records

- `n07_identity_support_area` is excluded from `allowed_proxy_kinds`; it remains an identity/support anchor, not a runtime-visible regulated variable.
- Memory-shaped response fields attach directly to the regulation response and map N09 names to N08 `memory_policy_digest` and `memory_strength` fields.
- N06 route arbitration is selection-only for N09; GPR4+ must produce N09 scheduling and processed-packet evidence.
- N06 source rows do not serialize direct candidate budget predictions; missing prediction fails with `candidate_budget_prediction_missing`.
- N07 withdrawal stability is not available; support withdrawal checks carry `n07_identity_withdrawal_baseline_not_available`.
- N08 memory-shaped rows may be consumed only as serialized producer/policy memory evidence.
- Perturbation artifacts must declare expected recovery window count and recovery success criterion.
- Oscillator-return regulation is a deferred secondary fixture unless explicitly selected.

## Validation Checks

Passed checks: 46/46

```json
{
  "allowed_proxy_kinds_runtime_visible": true,
  "artifact_only_replay_chain_declared": true,
  "artifact_only_replay_chain_includes_perturbation_and_withdrawal": true,
  "ceiling_algorithm_inherited": true,
  "claim_flag_keys_match_baseline": true,
  "claim_flags_all_false": true,
  "control_blockers_match_contract": true,
  "controls_have_distinct_blockers": true,
  "default_fixture_is_budget_auditable_node_band": true,
  "error_signal_schema_complete": true,
  "identity_support_outcome_tags_declared": true,
  "memory_lane_field_mapping_to_n08_declared": true,
  "memory_lane_required": true,
  "n06_candidate_budget_prediction_gap_recorded": true,
  "n06_packet_execution_not_inherited": true,
  "n06_unknown_source_blocker_preserved": true,
  "n07_identity_support_area_excluded_as_proxy_kind": true,
  "n07_withdrawal_gap_preserved": true,
  "n08_support_anchor_consistency_revalidated": true,
  "n10_handoff_fields_inherited": true,
  "native_policy_gaps_recorded": true,
  "no_memory_comparator_required": true,
  "node_plus_packet_budget_separate_and_exact": true,
  "oscillator_fixture_deferred": true,
  "packet_response_fields_complete": true,
  "perturbation_recovery_fields_declared": true,
  "perturbation_schema_complete": true,
  "positive_regulation_evidence_not_generated": true,
  "producer_record_linkage_schema_structured": true,
  "proxy_budget_ambiguity_blocker_declared": true,
  "proxy_surface_schema_complete": true,
  "regulation_outcome_taxonomy_inherited": true,
  "regulation_policy_digest_rule_declared": true,
  "regulation_probe_not_run": true,
  "regulation_response_attaches_identity_support_fields": true,
  "regulation_response_attaches_memory_lane_fields": true,
  "regulation_response_schema_complete": true,
  "required_controls_present": true,
  "route_arbitration_context_constraint_visible": true,
  "route_producer_evidence_fields_complete": true,
  "same_proxy_target_policy_required_for_lane_comparison": true,
  "source_baseline_digest_matches": true,
  "support_withdrawal_kind_declared": true,
  "support_withdrawal_schema_complete": true,
  "target_band_bounds_valid_for_coherence": true,
  "target_band_schema_complete": true
}
```

## Controls

```json
{
  "artifact_order_inversion": {
    "primary_blocker": "artifact_order_inversion",
    "status": "blocked"
  },
  "candidate_budget_prediction_missing": {
    "primary_blocker": "candidate_budget_prediction_missing",
    "status": "blocked"
  },
  "claim_promotion": {
    "primary_blocker": "claim_promotion_blocked",
    "status": "blocked"
  },
  "duplicate_regulation_response": {
    "primary_blocker": "duplicate_regulation_response",
    "status": "blocked"
  },
  "error_policy_missing": {
    "primary_blocker": "error_policy_missing",
    "status": "blocked"
  },
  "error_signal_digest_mismatch": {
    "primary_blocker": "error_signal_digest_mismatch",
    "status": "blocked"
  },
  "hidden_proxy_source": {
    "primary_blocker": "hidden_proxy_source_rejected",
    "status": "blocked"
  },
  "hidden_proxy_target": {
    "primary_blocker": "hidden_proxy_target_rejected",
    "status": "blocked"
  },
  "hidden_reward_or_goal_label": {
    "primary_blocker": "hidden_reward_or_goal_label_rejected",
    "status": "blocked"
  },
  "identity_support_digest_mismatch": {
    "primary_blocker": "identity_support_digest_mismatch",
    "status": "blocked"
  },
  "memory_surface_missing_for_memory_lane": {
    "primary_blocker": "memory_surface_missing_for_memory_lane",
    "status": "blocked"
  },
  "memory_surface_read_in_no_memory_lane": {
    "primary_blocker": "memory_surface_read_in_no_memory_lane",
    "status": "blocked"
  },
  "missing_proxy_surface": {
    "primary_blocker": "proxy_surface_missing",
    "status": "blocked"
  },
  "n06_packet_execution_inherited": {
    "primary_blocker": "n06_selection_only_no_packet_execution_for_regulation",
    "status": "blocked"
  },
  "node_plus_packet_budget_discontinuity": {
    "primary_blocker": "node_plus_packet_budget_discontinuity",
    "status": "blocked"
  },
  "oscillator_fixture_without_explicit_opt_in": {
    "primary_blocker": "oscillator_regulation_fixture_requires_explicit_opt_in",
    "status": "blocked"
  },
  "perturbation_schema_missing": {
    "primary_blocker": "perturbation_schema_missing",
    "status": "blocked"
  },
  "posthoc_target_change": {
    "primary_blocker": "posthoc_target_change_rejected",
    "status": "blocked"
  },
  "processed_packet_missing": {
    "primary_blocker": "processed_packet_missing",
    "status": "blocked"
  },
  "producer_direct_mutation": {
    "primary_blocker": "producer_direct_mutation_blocked",
    "status": "blocked"
  },
  "proxy_budget_ambiguity": {
    "primary_blocker": "proxy_budget_ambiguity",
    "status": "blocked"
  },
  "proxy_surface_digest_mismatch": {
    "primary_blocker": "proxy_surface_digest_mismatch",
    "status": "blocked"
  },
  "regulation_policy_missing": {
    "primary_blocker": "regulation_policy_missing",
    "status": "blocked"
  },
  "scheduled_packet_missing": {
    "primary_blocker": "scheduled_packet_missing",
    "status": "blocked"
  },
  "support_withdrawal_baseline_missing": {
    "primary_blocker": "n07_identity_withdrawal_baseline_not_available",
    "status": "blocked"
  },
  "target_band_missing": {
    "primary_blocker": "target_band_missing",
    "status": "blocked"
  },
  "unknown_candidate_source_surface": {
    "primary_blocker": "native_route_candidate_committed_source_surface_required",
    "status": "blocked"
  },
  "wrong_direction_response": {
    "primary_blocker": "wrong_direction_response",
    "status": "blocked"
  }
}
```

## Digests

- Manifest digest: `084925ff201f49c53db6040e22fa9970736ca9a5e7ad4d090165966bd8efab2a`
- Validation digest: `6c49700ab9f3a735bbfe2fec2b88b5e0c6920fc935fd896b5587e6f1dc9059ac`
- Manifest SHA-256: `e8ac646605f8524e344f378ae060bb6c25420c6701024f8802a7972e77d59c45`

## Acceptance

Iteration 2 passes if N09 has a replayable proxy-regulation fixture contract with target/error policies, producer/route boundaries, budget separation, memory/no-memory lanes, perturbation/support schemas, identity/support outcome tags, ceiling algorithm, N10 handoff fields, controls, and claim flags frozen before any positive regulation probe.

Acceptance achieved: True
