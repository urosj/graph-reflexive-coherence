# N06 Iteration 2 Fixture Manifest Validation

Status: passed

Command:

```bash
.venv/bin/python experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/validate_n06_fixture_manifest.py
```

Manifest: `experiments/2026-05-N06-lgrc-semantic-route-choice/configs/n06_fixture_manifest_v1.json`

Manifest SHA-256: `867a2bb464bbbdc0c782f334cf3bb9821b3d8f60d792dceab4644695b947363b`

Canonical manifest digest: `69175ec19d0a43223b726348e0e98cbdd13244b3d7533b6323236405ba7cd7f5`

No semantic route-choice probes were run in this iteration.

## Fixture

| Field | Value |
|---|---|
| fixture_id | `N06_S0_source_two_route_context_fork_v1` |
| source_node_id | `0` |
| branch_node_id | `1` |
| sink_node_ids | `[2, 3]` |
| context_node_ids | `[4, 5]` |
| native policy | `score_ordered_topology_route_candidates` |
| order key | `score_desc_then_candidate_id` |
| unresolved tie policy | `fail_closed` |

## Context Score Templates

| Context | Route | Score | Component Sum |
|---|---|---:|---:|
| `context_a` | `route_a` | `1.0` | `1.0` |
| `context_a` | `route_b` | `0.4` | `0.4` |
| `context_b` | `route_a` | `0.4` | `0.4` |
| `context_b` | `route_b` | `1.0` | `1.0` |

Context-to-score derivation:

```json
{
  "budget_validity": {
    "derivation_rule": "0.2 when candidate budget surface is node_plus_packet, non-ambiguous, and predicted error is within budget_tolerance",
    "source_artifact_kind": "LGRC9V3NativeRouteCandidateRecord.candidate_budget_prediction",
    "value_if_valid": 0.2
  },
  "context_match": {
    "derivation_rule": "context_match is 0.6 when candidate route id equals the runtime-visible compatible route for the active context node, otherwise 0.0",
    "hidden_context_lookup_allowed": false,
    "runtime_visible_input_fields": [
      "active_context_node_id",
      "candidate_route_id",
      "compatible_route_id",
      "context_surface_digest"
    ],
    "source_artifact_kind": "LGRC9V3CausalPulseSubstrateSurfaceRow",
    "source_surface_kind": "route_local_pulse_contact_or_feedback_eligibility",
    "value_if_context_route_matches": 0.6,
    "value_if_context_route_mismatches": 0.0
  },
  "lineage_ready": {
    "derivation_rule": "0.2 when candidate lineage transfer map covers all transferred nodes with string lineage ids",
    "does_not_require_prior_topology_state_reabsorption_for_sc1": true,
    "source_artifact_kind": "LGRC9V3NativeRouteCandidateRecord.candidate_lineage_transfer_map",
    "value_if_valid": 0.2
  }
}
```

## Iteration 3 Transition Criteria

- each emitted candidate record has a non-null candidate_source_surface_digest
- candidate_source_surface_digest resolves to a committed native causal pulse-substrate surface row or equivalent native source surface
- candidate_source_producer_record_id is non-null when candidate emission is producer-backed
- candidate_source_topology_state_reabsorption_digest is null/not required for the first pre-topology SC1 candidate set
- no route-arbitration record, selected topology event, scheduled packet, or claim flag is emitted by SC1 candidate exposure

SC1 candidate exposure does not require a topology-state reabsorption digest;
that digest is required only for post-topology candidate sources.

## Arbitration Window

```json
{
  "boundary_artifact_mapping": {
    "candidate_event_artifact_kind": "LGRC9V3NativeRouteCandidateRecord",
    "end_event_artifact_kind": "LGRC9V3NativeRouteCandidateSetRecord",
    "producer_policy": "n06_experiment_local_candidate_emission_wrapper_until_native_candidate_producer_exists",
    "producer_trigger": "native_route_candidate_emission_from_committed_context_surface_row",
    "start_event_artifact_kind": "LGRC9V3CausalPulseSubstrateSurfaceRow"
  },
  "timing": {
    "causal_epoch": "n06_epoch_context_candidate_emission_v1",
    "checkpoint_index": 0,
    "event_time_key_range": {
      "monotonic_non_decreasing": true
    },
    "scheduler_event_index_range": {
      "candidate_records_before_candidate_set": true,
      "candidate_set_after_all_candidate_records": true,
      "start_min": 0
    }
  }
}
```

## Checks

| Check | Passed |
|---|---|
| `all_required_controls_declared` | `True` |
| `arbitration_policy_declared` | `True` |
| `arbitration_timing_declared` | `True` |
| `arbitration_window_artifact_mapping_declared` | `True` |
| `arbitration_window_declared` | `True` |
| `budget_tolerance_declared` | `True` |
| `candidate_ordering_declared` | `True` |
| `candidate_scores_equal_component_sums` | `True` |
| `candidate_set_frozen_before_arbitration` | `True` |
| `candidate_source_post_topology_fields_declared` | `True` |
| `candidate_source_reabsorption_digest_required_post_topology` | `True` |
| `candidate_source_requires_native_surface` | `True` |
| `candidate_source_sc1_reabsorption_digest_conditional` | `True` |
| `candidate_source_sc1_required_fields_declared` | `True` |
| `candidate_templates_valid` | `True` |
| `claim_flags_all_false` | `True` |
| `claim_flags_complete` | `True` |
| `context_a_b_select_different_routes` | `True` |
| `context_nodes_exist` | `True` |
| `context_relation_declared` | `True` |
| `context_runtime_visible` | `True` |
| `context_states_a_b_declared` | `True` |
| `context_surface_mapping_preferred_native` | `True` |
| `context_to_score_mapping_declared` | `True` |
| `control_blockers_are_distinct` | `True` |
| `default_off_no_emission_declared` | `True` |
| `default_off_policy_declared` | `True` |
| `edge_count_matches` | `True` |
| `edge_endpoints_exist` | `True` |
| `edge_ids_unique` | `True` |
| `hidden_context_sources_blocked` | `True` |
| `iteration_3_transition_criteria_declared` | `True` |
| `lgrc2_native_route_arbitration_blocked` | `True` |
| `native_dependencies_declared` | `True` |
| `native_dependency_chain_policy_declared` | `True` |
| `native_lgrc3_gate_declared` | `True` |
| `native_route_intents_declared` | `True` |
| `no_positive_sc_evidence_generated` | `True` |
| `no_route_choice_probe_run` | `True` |
| `node_count_matches` | `True` |
| `node_ids_unique` | `True` |
| `producer_boundary_declared` | `True` |
| `producer_forbidden_writes_declared` | `True` |
| `producer_scheduling_deferred` | `True` |
| `redirect_caveat_declared` | `True` |
| `route_arbitration_alone_not_semantic_choice` | `True` |
| `routes_resolve_to_existing_edges` | `True` |
| `runtime_family_declared` | `True` |
| `sc1_selection_non_actions_declared` | `True` |
| `schema_matches` | `True` |
| `score_invariant_declared` | `True` |
| `selected_topology_event_behavior_declared` | `True` |
| `source_branch_and_sinks_exist` | `True` |
| `tie_policy_fail_closed` | `True` |
| `tiebreaker_fields_serialized` | `True` |
| `two_routes_declared` | `True` |

## Controls

| Control | Primary Blocker | Required |
|---|---|---|
| `policy_disabled` | `native_route_arbitration_policy_disabled` | `True` |
| `no_candidates` | `native_route_arbitration_no_candidates` | `True` |
| `unresolved_tie` | `native_route_arbitration_unresolved_tie` | `True` |
| `hidden_context` | `native_route_arbitration_hidden_input_rejected:hidden_context` | `True` |
| `hidden_route_preference` | `native_route_arbitration_hidden_input_rejected:hidden_route_preference` | `True` |
| `preselected_sink` | `native_route_arbitration_hidden_input_rejected:preselected_sink` | `True` |
| `experiment_side_if_else` | `n06_experiment_side_selection_rejected` | `True` |
| `report_side_selection` | `n06_report_side_selection_rejected` | `True` |
| `posthoc_threshold_change` | `n06_posthoc_threshold_change_rejected` | `True` |
| `budget_mismatch` | `native_route_arbitration_budget_invalid` | `True` |
| `order_inversion` | `native_route_arbitration_order_invalid` | `True` |
| `stale_candidate` | `n06_stale_candidate_route_blocked` | `True` |
| `stale_context` | `n06_stale_context_surface_blocked` | `True` |
| `duplicate_arbitration` | `duplicate_native_route_arbitration` | `True` |
| `producer_mutation` | `n06_producer_mutation_boundary_violation` | `True` |
| `claim_promotion` | `native_route_arbitration_claim_promotion_blocked` | `True` |

## Claim Flags

| Flag | Value |
|---|---|
| `agency_claim_allowed` | `False` |
| `agentic_like_claim_allowed` | `False` |
| `ant_colony_claim_allowed` | `False` |
| `biological_claim_allowed` | `False` |
| `goal_proxy_regulation_claim_allowed` | `False` |
| `identity_acceptance_claim_allowed` | `False` |
| `locomotion_like_claim_allowed` | `False` |
| `memory_or_trail_claim_allowed` | `False` |
| `movement_claim_allowed` | `False` |
| `rc_identity_collapse_claim_allowed` | `False` |
| `semantic_choice_claim_allowed` | `False` |
| `unrestricted_movement_claim_allowed` | `False` |

## Acceptance

Iteration 2 declares the N06 source-plus-two-routes fixture, native
context-score mapping, context A/B states, arbitration window, candidate source
fields, route intents, selected-topology-event behavior, deterministic ordering,
budget tolerance, default-off policy, producer boundary, and fail-closed
controls before any semantic route-choice probe runs.
