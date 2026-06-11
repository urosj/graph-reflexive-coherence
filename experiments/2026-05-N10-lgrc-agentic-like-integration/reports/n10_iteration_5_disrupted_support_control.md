# N10 Iteration 5 Disrupted Support Control

Status: `passed`.

## Result

Iteration 5 consumed the N07 N09-matched partial-withdrawal lane and
attempted the same support-aware regulation replay used in Iterations
3 and 4. The support lane is below its survival threshold and has no
explicit restoration evidence, so N10 blocks the integration attempt.

This is an ALI3 support-sensitivity control component, not an ALI3
closeout by itself. Iteration 6 must still show explicit restoration
before integration can resume after disruption.

```text
attempted_integration_level = A4
accepted_integration_level = None
n10_category_level = ALI3
integration_outcome_tag = support_disruption_blocked_integration
support_state_tag = n09_matched_withdrawal_disrupts_support
integration_allowed = False
positive_integration_row_emitted = False
primary_blocker = support_disrupted_but_integration_allowed
route/memory consumed = false
artifact_only = true
runtime_state_used = false
```

## Support Evidence

```json
{
  "final_A_support_retention": 0.7298651821835279,
  "final_basin_separability": 0.7298651821835279,
  "final_budget_error": 0.0,
  "identity_support_outcome_tag": "support_disrupted_by_withdrawal_without_restoration",
  "lane_digest": "987651daaf122f47d3e26d3fd9d7611ceebb3149879b0326e6ca2775a18e4387",
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
withdrawal_depth = 0.25
restoration_fraction = 0.0
```

The N09-matched withdrawal disrupts support because retention drops
below threshold. N10 therefore records a blocked attempt instead of a
positive support-aware regulation row.

## Regulation Evidence

```json
{
  "source_artifact_only_runtime_fallback_blocked": true,
  "source_budget_control_passed": true,
  "source_claim_ceiling": "artifact_only_goal_proxy_regulation_candidate",
  "source_gpr_level": "GPR6",
  "source_hypothesis_a_status": "closed"
}
```

## Budget Boundary

Iteration 5 claims source-artifact budget compatibility only. It does
not claim one continuous packet ledger across separate N07 and N09
runs.

```text
budget_mode = source_artifact_budget_compatibility_not_single_runtime_continuity
node_plus_packet_budget_error = 0.0
support_lane_final_budget_error = 0.0
```

## Controls

```json
{
  "budget_surface_ambiguity": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "Iteration 5 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "disrupted support cannot emit agency, A6, identity acceptance, or goal-ownership claims"
  },
  "missing_goal_proxy_regulation_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_goal_proxy_regulation_artifact",
    "reason": "disrupted-support control requires N09 GPR closeout evidence"
  },
  "missing_identity_support_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_identity_support_artifact",
    "reason": "disrupted-support control requires N07 Iteration 13 support lane evidence"
  },
  "restoration_required_but_missing": {
    "control_passed": true,
    "primary_blocker": "restoration_required_but_missing",
    "reason": "integration may resume only in a later explicit-restoration lane"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N07/N09 source artifact digests are rechecked against Iteration 1"
  },
  "stale_identity_support_baseline": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "disrupted support state is read from the current N07 Iteration 13 lane and matched against the N10 manifest summary"
  },
  "support_disrupted_but_integration_allowed": {
    "control_passed": true,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "reason": "the N09-matched support withdrawal is below threshold, so the attempted support-aware regulation replay is blocked"
  }
}
```

## Checks

```json
{
  "a6_not_supported_by_iteration_5": true,
  "accepted_integration_level_absent": true,
  "ali3_relevant_not_ali3_closeout": true,
  "artifact_only_replay": true,
  "attempted_integration_level_is_a4": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "disrupted_support_budget_error_zero": true,
  "disrupted_support_lane_fails_survival": true,
  "disrupted_support_retention_below_threshold": true,
  "fixture_required_support_state_tag_matched": true,
  "integration_allowed_false": true,
  "integration_record_digest_valid": true,
  "integration_record_required_fields_present": true,
  "n09_budget_control_passed": true,
  "n09_goal_proxy_candidate_available": true,
  "n09_gpr6_available": true,
  "n10_category_level_is_ali3_control_component": true,
  "no_restoration_available": true,
  "positive_integration_row_not_emitted": true,
  "primary_blocker_recorded": true,
  "route_memory_not_consumed_for_control": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_5": true,
  "support_state_tag_is_n09_matched_disruption": true
}
```

## Acceptance

Iteration 5 passes if N10 fails closed when the identity/support baseline is disrupted. A disrupted-support lane must not become an agentic-like integration row unless explicit restoration evidence exists.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_5_disrupted_support_control.py
```

Output digest:

```text
8e130ae971734d32c94d1986ea8d2be6f60fb40f9a2c59291f472ac0d16053f2
```
