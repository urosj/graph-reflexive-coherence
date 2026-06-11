# N10 Iteration 10 Full-Composition Disrupted Support Control

Status: `passed`.

## Result

Iteration 10 takes the Iteration 9 Hypothesis A closeout as the
positive full-composition source, preserves the route, memory, and
goal-proxy regulation links, and replaces the support lane with the
N07 N09-matched disrupted-support lane.

The result is intentionally negative: the full composition blocks for a
support-specific reason. This strengthens Hypothesis B because the
support-disruption control now operates at the full A6/ALI6 boundary,
not only at the earlier support/regulation sub-chain.

```text
attempted_integration_level = A6
attempted_n10_category_level = ALI6
accepted_integration_level = None
accepted_n10_category_level = None
integration_allowed = False
positive_integration_row_emitted = False
primary_blocker = support_disrupted_but_integration_allowed
artifact_only = true
runtime_state_used = false
```

## Preserved Links

```json
{
  "goal_proxy_regulation_link_present": true,
  "identity_support_link_present": true,
  "memory_affordance_link_present": true,
  "n10_hypothesis_a_closeout_link_present": true,
  "route_choice_link_present": true
}
```

## Support Evidence

```json
{
  "final_A_support_retention": 0.7298651821835279,
  "final_basin_separability": 0.7298651821835279,
  "final_budget_error": 0.0,
  "identity_support_outcome_tag": "support_disrupted_by_withdrawal_without_restoration",
  "lane_digest": "987651daaf122f47d3e26d3fd9d7611ceebb3149879b0326e6ca2775a18e4387",
  "manifest_lane_digest": "987651daaf122f47d3e26d3fd9d7611ceebb3149879b0326e6ca2775a18e4387",
  "n09_withdrawal_digest": "8e09a8de0b8d66e57e425a6c15a52abdf2e5090c65878eaf434c0751cc43fd84",
  "no_restoration": true,
  "reference_A_support_retention": 0.9731535762447039,
  "restoration_fraction": 0.0,
  "source_lane_id": "n09_matched_partial_support_withdrawal",
  "support_below_threshold": true,
  "support_loss_from_reference": 0.24328839406117597,
  "support_survival_passed": false,
  "support_survival_threshold": 0.85,
  "withdrawal_depth": 0.25,
  "withdrawal_kind": "partial_support_weakening"
}
```

Interpretation:

```text
final_A_support_retention = 0.7298651821835279
support_survival_threshold = 0.85
support_loss_from_reference = 0.24328839406117597
support_survival_passed = false
restoration_fraction = 0.0
```

The route/memory/regulation chain did not fail because a source was
missing. It failed because the support baseline was below the declared
survival threshold and no explicit restoration was present.

## Controls

```json
{
  "artifact_only_replay_missing_link": {
    "control_passed": true,
    "primary_blocker": "artifact_only_replay_missing_link",
    "reason": "the blocked row is still reconstructable from exported source artifacts only"
  },
  "budget_surface_ambiguity": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "route, memory, support, and proxy budgets remain source-artifact compatibility checks, not a cross-run live ledger claim"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "blocked full composition cannot emit agency, identity acceptance, goal ownership, or fully native agentic-like claims"
  },
  "hidden_experiment_side_steering": {
    "control_passed": true,
    "primary_blocker": "hidden_experiment_side_steering",
    "reason": "N10 does not override the disrupted support lane by report-side steering"
  },
  "missing_goal_proxy_regulation_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_goal_proxy_regulation_artifact",
    "reason": "full-composition control keeps the N09 goal-proxy regulation source link present"
  },
  "missing_identity_support_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_identity_support_artifact",
    "reason": "full-composition control consumes the N07 disrupted support lane"
  },
  "missing_memory_affordance_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_memory_affordance_artifact",
    "reason": "full-composition control keeps the N08 memory/trail source link present"
  },
  "missing_route_choice_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_route_choice_artifact",
    "reason": "full-composition control keeps the N06 route-choice source link present"
  },
  "restoration_required_but_missing": {
    "control_passed": true,
    "primary_blocker": "restoration_required_but_missing",
    "reason": "full composition may resume only through an explicit restoration record"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N06/N07/N08/N09 source digests are checked against the Iteration 1 baseline"
  },
  "stale_identity_support_baseline": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "the disrupted lane digest is matched against the frozen N10 manifest lane summary"
  },
  "support_disrupted_but_full_composition_allowed": {
    "control_passed": true,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "reason": "the A6/ALI6 source chain is blocked because support is disrupted"
  }
}
```

## Checks

```json
{
  "a6_not_accepted_under_disrupted_support": true,
  "accepted_integration_level_absent": true,
  "artifact_only_replay": true,
  "attempted_integration_level_is_a6": true,
  "attempted_n10_category_level_is_ali6": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "disrupted_support_budget_error_zero": true,
  "disrupted_support_lane_fails_survival": true,
  "disrupted_support_retention_below_threshold": true,
  "full_composition_sources_preserved": true,
  "integration_allowed_false": true,
  "integration_record_digest_valid": true,
  "integration_record_required_fields_present": true,
  "iteration_8_main_window_available": true,
  "iteration_9_hypothesis_a_closeout_available": true,
  "memory_link_present": true,
  "memory_scope_preserved": true,
  "no_restoration_available": true,
  "positive_integration_row_not_emitted": true,
  "primary_blocker_support_specific": true,
  "regulation_link_present": true,
  "route_context_selection_only_preserved": true,
  "route_link_present": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_10": true,
  "support_state_tag_is_n09_matched_disruption": true
}
```

## Acceptance

```json
{
  "acceptance_statement": "Iteration 10 passes if the full Hypothesis A route-memory-support-regulation composition blocks or downgrades under the N07 N09-matched disrupted-support lane with a distinct support-specific blocker, while preserving route, memory, and regulation source links and all claim boundaries.",
  "achieved": true,
  "status": "passed"
}
```

## Claim Boundary

All claim flags remain false. Iteration 10 does not emit agency,
semantic goal ownership, identity acceptance, ACO, biological,
personhood, unrestricted agency, or fully native agentic-like
integration claims.

## Reproduction

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_10_full_composition_disrupted_support_control.py
```

Output digest:

```text
bcda2eb478e64228c3de65b5e76903817ec83da68cf9e0323eca902ff2072fcc
```
