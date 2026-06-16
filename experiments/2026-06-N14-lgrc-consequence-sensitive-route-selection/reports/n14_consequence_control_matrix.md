# N14 Consequence Control Matrix

Status: `passed`.

## Acceptance State

```text
accepted_adversarial_control_matrix_pending_replay
```

## Interpretation

```json
{
  "acceptance_state": "accepted_adversarial_control_matrix_pending_replay",
  "next_required_step": "Run Iteration 6 consequence perturbation and replay matrix to test source-sensitive rank changes and replay stability.",
  "plain_language_interpretation": "The Iteration 4 candidate is no longer relying only on declared control policies: Iteration 5 constructs corrupted variants and confirms each fails with a distinct blocker. The clean conflict case still selects route_b by consequence evidence. Final AP4 remains pending because replay and perturbation controls are not run until Iteration 6 and claim classification is not frozen until Iteration 7.",
  "record_id": "n14_i5_interpretation_control_matrix_v1",
  "supported_interpretation": "N14 Iteration 5 executes adversarial controls for the provisional memory-dominant AP4 candidate. Hidden outcomes, post-hoc scores, stale records, budget-invalid routes, missing records, cherry-picked candidate sets, ambiguous ties, fixture labels, immediate-affordance relabels, and unsafe claim relabels fail closed.",
  "unsupported_interpretations": [
    "final AP4 support",
    "support-specific route consequence support",
    "regulation-specific route consequence support",
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

## Selection Contract Enforcement

```json
{
  "contract_id": "n14_i5_selection_contract_hardening_v1",
  "enforced_order": [
    "reject hidden outcome, post-hoc, stale, relabel, and fixture-label metadata",
    "reject candidate-set cherry-picking",
    "reject missing consequence records",
    "reject candidates without budget-valid source surfaces before ranking",
    "require consequence_rank_source derived from serialized score components",
    "sort by consequence_rank, immediate_affordance_rank, and route_candidate_id",
    "apply explicit tie-policy removal control only when removal is explicit"
  ],
  "source_selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1"
}
```

## Control Records

| Control | Expected | Observed | Blocker | Passed |
| --- | --- | --- | --- | --- |
| `hidden_outcome_table_control` | `blocked` | `blocked` | `hidden_outcome_table_blocked` | `true` |
| `post_hoc_consequence_scoring_control` | `blocked` | `blocked` | `post_hoc_consequence_scoring_blocked` | `true` |
| `fabricated_consequence_rank_source_control` | `blocked` | `blocked` | `invalid_consequence_rank_source_blocked` | `true` |
| `stale_consequence_record_control` | `blocked` | `blocked` | `stale_consequence_record_blocked` | `true` |
| `budget_invalid_route_control` | `blocked` | `blocked` | `budget_invalid_route_blocked` | `true` |
| `missing_consequence_record_control` | `blocked` | `blocked` | `missing_consequence_record_blocked` | `true` |
| `candidate_set_cherry_picking_control` | `blocked` | `blocked` | `candidate_set_cherry_picking_blocked` | `true` |
| `tie_policy_ambiguity_control` | `blocked` | `blocked` | `tie_policy_ambiguity_blocked` | `true` |
| `immediate_affordance_only_relabel_control` | `blocked` | `blocked` | `immediate_affordance_only_relabel_blocked` | `true` |
| `matched_affordance_conflict_control` | `selected_route_b` | `selected:route_b` | `none` | `true` |
| `fixture_label_preference_control` | `blocked` | `blocked` | `fixture_label_preference_blocked` | `true` |
| `semantic_intention_relabel_control` | `blocked` | `blocked` | `semantic_intention_relabel_blocked` | `true` |
| `agency_relabel_control` | `blocked` | `blocked` | `agency_relabel_blocked` | `true` |
| `native_support_relabel_control` | `blocked` | `blocked` | `native_support_relabel_blocked` | `true` |
| `identity_acceptance_relabel_control` | `blocked` | `blocked` | `identity_acceptance_relabel_blocked` | `true` |
| `selfhood_relabel_control` | `blocked` | `blocked` | `selfhood_relabel_blocked` | `true` |
| `personhood_relabel_control` | `blocked` | `blocked` | `personhood_relabel_blocked` | `true` |
| `biological_behavior_relabel_control` | `blocked` | `blocked` | `biological_behavior_relabel_blocked` | `true` |
| `semantic_choice_relabel_control` | `blocked` | `blocked` | `semantic_choice_relabel_blocked` | `true` |
| `semantic_goal_ownership_relabel_control` | `blocked` | `blocked` | `semantic_goal_ownership_relabel_blocked` | `true` |
| `unrestricted_agency_relabel_control` | `blocked` | `blocked` | `unrestricted_agency_relabel_blocked` | `true` |

Iteration 5 executes adversarial controls against the Iteration 4
selection candidate. It does not run perturbation/replay regimes
and does not close final `AP4`.

## Checks

```json
{
  "agency_relabel_blocked": true,
  "all_controls_executed": true,
  "all_controls_passed": true,
  "biological_behavior_relabel_blocked": true,
  "budget_invalid_route_blocked": true,
  "budget_validity_checked_before_ranking": true,
  "candidate_set_cherry_picking_blocked": true,
  "claim_flags_forced_false": true,
  "consequence_rank_source_validated_before_ranking": true,
  "distinct_negative_blockers_present": true,
  "final_ap4_not_supported": true,
  "fixture_label_preference_blocked": true,
  "hidden_outcome_table_blocked": true,
  "identity_acceptance_relabel_blocked": true,
  "immediate_affordance_only_relabel_blocked": true,
  "invalid_consequence_rank_source_blocked": true,
  "matched_affordance_conflict_resolved_by_consequence": true,
  "missing_consequence_record_blocked": true,
  "native_support_opened_false": true,
  "native_support_relabel_blocked": true,
  "negative_controls_blocked": true,
  "personhood_relabel_blocked": true,
  "phase8_opened_false": true,
  "post_hoc_consequence_scoring_blocked": true,
  "route_records_source_passed": true,
  "runtime_state_used_false": true,
  "selection_source_passed": true,
  "selfhood_relabel_blocked": true,
  "semantic_choice_relabel_blocked": true,
  "semantic_goal_ownership_relabel_blocked": true,
  "semantic_intention_relabel_blocked": true,
  "src_diff_empty": true,
  "stale_consequence_record_blocked": true,
  "tie_policy_ambiguity_blocked": true,
  "tie_policy_removal_requires_explicit_metadata": true,
  "unrestricted_agency_relabel_blocked": true
}
```

## Claim Boundary

```text
control matrix passed != final AP4 support
memory-dominant AP4 candidate != support-specific route consequence support
memory-dominant AP4 candidate != regulation-specific route consequence support
consequence control pass != intention
consequence control pass != agency
artifact-level controls != native support
N14 Iteration 5 != semantic choice or goal ownership
```

## Output Digest

```text
d9ff2a2ff515eec26226048b25a990faa9f7c7ba94cea14ef833a89f8d9292e7
```
