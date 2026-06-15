# N14 Consequence-Sensitive Selection Candidate

Status: `passed`.

## Acceptance State

```text
accepted_consequence_sensitive_selection_candidate_pending_controls
```

## Interpretation

```json
{
  "acceptance_state": "accepted_consequence_sensitive_selection_candidate_pending_controls",
  "next_required_step": "Run Iteration 5 controls against hidden outcomes, post-hoc labels, stale records, invalid budgets, missing records, fixture labels, and claim relabels.",
  "plain_language_interpretation": "Iteration 4 resolves the Iteration 3 affordance/consequence conflict by derived consequence evidence. The selected route is route_b, while the immediate-affordance winner route_a is rejected. The positive candidate is memory-dominant: support and regulation sources are compatible but not route-specific yet. This is still only a provisional AP4 candidate because adversarial controls, replay/snapshot checks, and final claim-boundary classification remain pending.",
  "record_id": "n14_i4_interpretation_selection_candidate_v1",
  "supported_interpretation": "N14 now has a provisional AP4 candidate selection: the deterministic artifact-only rule selects route_b by a derived, memory-dominant pre-selection consequence rank even though immediate affordance favors route_a.",
  "unsupported_interpretations": [
    "final AP4 support",
    "intention",
    "agency",
    "semantic choice",
    "semantic goal ownership",
    "identity acceptance",
    "selfhood",
    "personhood",
    "biological behavior",
    "native support",
    "fully native integration"
  ]
}
```

## Selection Decision

```json
{
  "affordance_consequence_conflict_present": true,
  "affordance_consequence_conflict_resolved_by_consequence": true,
  "candidate_set_digest": "cc28d581e856d3782a840c63157f7b1d4d565387e8c00ed28b8365cba7b5f4a9",
  "consequence_rank_source": "derived_from_serialized_consequence_score_components",
  "consequence_signal_scope": "memory_dominant_provisional_candidate; support and regulation sources are compatible but not route-specific in Iteration 3",
  "consequence_top_route": "route_b",
  "decision_record_id": "n14_i4_consequence_sensitive_selection_decision_v1",
  "eligible_candidate_set_id": "native-route-candidate-set:2eb3d1248ced33eb4f89aa22ad208b39",
  "eligible_routes": [
    "route_a",
    "route_b"
  ],
  "final_ap4_supported": false,
  "immediate_affordance_top_route": "route_a",
  "provisional_ap_level": "AP4_candidate",
  "rejected_routes": [
    "route_a"
  ],
  "selected_route": "route_b",
  "selected_route_consequence_rank": 1,
  "selected_route_consequence_score": 0.12,
  "selected_route_immediate_affordance_rank": 2,
  "selection_depends_on_downstream_consequence_vector": true,
  "selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1"
}
```

## Candidate Records

| Route | Immediate rank | Consequence score | Consequence rank | Selected rank | Selection status |
| --- | ---: | ---: | ---: | ---: | --- |
| `route_a` | 1 | -0.1597545 | 2 | 2 | `rejected` |
| `route_b` | 2 | 0.12 | 1 | 1 | `selected` |

The selected route is `route_b`. Immediate affordance favors
`route_a`, so this is a matched conflict case resolved by the
pre-selection consequence vector. The positive candidate is
memory-dominant; support and regulation sources are compatible
but are not route-specific consequence evidence yet. Final `AP4`
remains unsupported until controls, replay/snapshot checks, and
claim-boundary classification pass in later iterations.

## Selection Rule

```json
{
  "allowed_inputs": [
    "complete_candidate_route_set",
    "pre_selection_consequence_records",
    "serialized_consequence_score_components",
    "derived_consequence_rank",
    "budget_validity",
    "tie_policy"
  ],
  "deterministic": true,
  "executed_controls_status": "not_executed_until_iteration_5; current missing/stale/budget handling is recorded as policy only",
  "forbidden_inputs": [
    "hidden_outcome_table",
    "post_hoc_consequence_score",
    "runtime_state_not_serialized_in_artifact",
    "semantic_intention_label",
    "agency_label",
    "native_support_label"
  ],
  "idempotency_digest_plan": "digest complete candidate set, source artifact sha256, source output digest, sorted route ids, ranks, budget validity, and selected route",
  "missing_consequence_record_policy": "reject_or_mark_unsupported",
  "positive_candidate_scope": "memory_dominant_provisional_ap4_candidate",
  "selection_order": [
    "reject candidates with missing consequence records",
    "reject candidates without budget-valid source surfaces",
    "require consequence_rank_source derived from serialized score components",
    "sort by derived consequence_rank ascending",
    "if consequence_rank ties, sort by immediate_affordance_rank ascending",
    "if still tied, sort by route_candidate_id lexicographically"
  ],
  "selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1",
  "stale_record_policy": "source_window_pinned_reject_or_mark_unsupported",
  "tie_policy": "tie_policy_explicit_replayable_no_tie_observed; consequence rank tie would use immediate_affordance_rank then route_candidate_id"
}
```

## Checks

```json
{
  "affordance_consequence_conflict_resolved_by_consequence": true,
  "all_eligible_candidates_recorded": true,
  "budget_validity_recorded": true,
  "candidate_set_complete": true,
  "claim_flags_forced_false": true,
  "consequence_rank_derived_from_score_components": true,
  "consequence_rank_recorded": true,
  "consequence_score_components_serialized": true,
  "controls_pending_recorded": true,
  "controls_recorded_as_policy_not_executed": true,
  "deterministic_selection_rule_present": true,
  "final_ap4_not_frozen": true,
  "hidden_outcome_table_not_used": true,
  "immediate_affordance_rank_recorded": true,
  "matched_or_conflicting_affordance_case_present": true,
  "memory_dominant_candidate_scope_recorded": true,
  "missing_consequence_records_rejected": true,
  "native_supported_flags_false": true,
  "only_provisional_ap4_assigned": true,
  "phase8_opened_false": true,
  "post_hoc_scoring_not_used": true,
  "rejected_candidate_records_present": true,
  "replay_pending_recorded": true,
  "route_records_source_passed": true,
  "runtime_state_used_false": true,
  "schema_source_passed": true,
  "selected_rank_recorded": true,
  "selected_route_is_consequence_top": true,
  "selected_route_is_not_immediate_affordance_top": true,
  "selection_depends_on_downstream_consequence_vector": true,
  "selection_records_satisfy_schema": true,
  "selection_status_record_present": true,
  "src_diff_empty": true,
  "tie_policy_explicit_and_replayable": true
}
```

## Claim Boundary

```text
provisional AP4 candidate != final AP4 support
consequence-sensitive selection candidate != intention
selected route by derived consequence rank != semantic choice
source-backed consequence vector != semantic goal ownership
artifact-level selection candidate != native support
N14 Iteration 4 != agency
```

## Output Digest

```text
d867b665e3ca96df4a78576b89fb2b89a19ff2761f0099e48d057f00c6b8cfdd
```
