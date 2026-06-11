# N10 Iteration 11 Full-Composition Explicit Restoration Replay

Status: `passed`.

## Result

Iteration 11 consumes the explicit N07 restoration lane after the
Iteration 10 disrupted-support block. The full composition can resume
because restoration is explicit, source-backed, above threshold, and
linked to the same N09 withdrawal event.

```text
attempted_integration_level = A6
accepted_integration_level = A6
accepted_n10_category_level = ALI6
integration_outcome_tag = restoration_gated_integration_candidate
integration_allowed = True
positive_integration_row_emitted = True
artifact_only = true
runtime_state_used = false
```

## Prior Disruption Link

```json
{
  "history_preserved": true,
  "iteration_10_record_digest": "22b6166b43401ea2ceab6577f6ad6748771663995a8163ac803b55716836ebec",
  "iteration_10_record_digest_valid": true,
  "prior_integration_allowed": false,
  "prior_n09_withdrawal_digest": "8e09a8de0b8d66e57e425a6c15a52abdf2e5090c65878eaf434c0751cc43fd84",
  "prior_positive_row_emitted": false,
  "prior_primary_blocker": "support_disrupted_but_integration_allowed",
  "prior_support_lane_digest": "987651daaf122f47d3e26d3fd9d7611ceebb3149879b0326e6ca2775a18e4387",
  "prior_support_lane_id": "n09_matched_partial_support_withdrawal",
  "prior_support_survival_passed": false
}
```

## Restoration Evidence

```json
{
  "explicit_restoration_present": true,
  "final_A_support_retention": 0.9244958974324687,
  "final_basin_separability": 0.9244958974324687,
  "final_budget_error": 0.0,
  "identity_support_outcome_tag": "explicit_restoration_recovers_support_survival_baseline",
  "lane_digest": "0a7c864269cbf0ffb1d1b2d02f95b5b3bd5a9e9c3fbc1b45b2a4d751902b5f5f",
  "manifest_lane_digest": "0a7c864269cbf0ffb1d1b2d02f95b5b3bd5a9e9c3fbc1b45b2a4d751902b5f5f",
  "n09_withdrawal_digest": "8e09a8de0b8d66e57e425a6c15a52abdf2e5090c65878eaf434c0751cc43fd84",
  "reference_A_support_retention": 0.9731535762447039,
  "restoration_fraction": 0.8,
  "source_lane_id": "restored_after_n09_partial_withdrawal",
  "support_above_threshold": true,
  "support_loss_from_reference": 0.04865767881223515,
  "support_survival_passed": true,
  "support_survival_threshold": 0.85,
  "withdrawal_depth": 0.25,
  "withdrawal_kind": "partial_support_weakening_with_explicit_restoration"
}
```

Interpretation:

```text
final_A_support_retention = 0.9244958974324687
support_survival_threshold = 0.85
restoration_fraction = 0.8
support_survival_passed = true
prior disrupted-support history preserved = true
```

This does not erase Iteration 10. It records that the full composition
may resume only through explicit restoration evidence that references
the same disrupted-support event.

## Controls

```json
{
  "artifact_only_replay_missing_link": {
    "control_passed": true,
    "primary_blocker": "artifact_only_replay_missing_link",
    "reason": "the restored row is reconstructable from exported source artifacts only"
  },
  "budget_surface_ambiguity": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "route, memory, support, and proxy budgets remain source-artifact compatibility checks"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "restoration-gated full composition cannot emit agency, identity acceptance, goal ownership, A7, or fully native agentic-like claims"
  },
  "hidden_experiment_side_steering": {
    "control_passed": true,
    "primary_blocker": "hidden_experiment_side_steering",
    "reason": "N10 does not invent restoration; it consumes the recorded N07 restoration lane"
  },
  "missing_goal_proxy_regulation_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_goal_proxy_regulation_artifact",
    "reason": "full restoration replay keeps the N09 regulation source link present"
  },
  "missing_identity_support_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_identity_support_artifact",
    "reason": "full restoration replay consumes the N07 restored support lane"
  },
  "missing_memory_affordance_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_memory_affordance_artifact",
    "reason": "full restoration replay keeps the N08 memory/trail source link present"
  },
  "missing_route_choice_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_route_choice_artifact",
    "reason": "full restoration replay keeps the N06 route-choice source link present"
  },
  "prior_disruption_history_preserved": {
    "control_passed": true,
    "primary_blocker": "support_history_erased",
    "reason": "restoration references the same N09 withdrawal digest as the Iteration 10 disrupted-support block"
  },
  "restoration_required_but_missing": {
    "control_passed": true,
    "primary_blocker": "restoration_required_but_missing",
    "reason": "full composition resumes only because explicit restoration is present"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N06/N07/N08/N09 source digests are checked against the Iteration 1 baseline"
  },
  "stale_identity_support_baseline": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "the restored lane digest is matched against the frozen N10 manifest lane summary"
  }
}
```

## Checks

```json
{
  "a7_not_claimed": true,
  "accepted_integration_level_is_a6": true,
  "accepted_n10_category_level_is_ali6": true,
  "artifact_only_replay": true,
  "attempted_integration_level_is_a6": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "explicit_restoration_present": true,
  "integration_allowed_true": true,
  "integration_record_digest_valid": true,
  "integration_record_required_fields_present": true,
  "iteration_10_disruption_record_available": true,
  "iteration_9_hypothesis_a_closeout_available": true,
  "memory_link_present": true,
  "memory_scope_preserved": true,
  "positive_integration_row_emitted": true,
  "prior_disruption_digest_valid": true,
  "prior_disruption_history_preserved": true,
  "regulation_link_present": true,
  "restored_support_lane_survives": true,
  "restored_support_retention_above_threshold": true,
  "route_context_selection_only_preserved": true,
  "route_link_present": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_11": true,
  "support_state_tag_is_explicit_restoration": true
}
```

## Acceptance

```json
{
  "acceptance_statement": "Iteration 11 passes if the full composition can resume only through explicit, source-backed restoration evidence that follows the disrupted-support record. The result may support a restoration-gated bounded composition candidate, but does not erase the disruption control or promote A7, agency, or identity acceptance claims.",
  "achieved": true,
  "status": "passed"
}
```

## Claim Boundary

All claim flags remain false. Iteration 11 does not emit agency,
semantic goal ownership, identity acceptance, ACO, biological,
personhood, unrestricted agency, A7 generalization, or fully native
agentic-like integration claims.

## Reproduction

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_11_full_composition_explicit_restoration_replay.py
```

Output digest:

```text
6513e248421090b7b039e002ced29f89465dc80ca0351e751005d91635e6db6e
```
