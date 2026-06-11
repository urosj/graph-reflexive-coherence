# N10 Iteration 6 Explicit Restoration Replay

Status: `passed`.

## Result

Iteration 6 consumed the N07 explicit-restoration lane and resumed the
support-aware regulation replay only after source-backed restoration
evidence. The restored lane remains above its survival threshold and
references the same N09 withdrawal digest as the Iteration 5 disrupted
support control.

This closes the ALI3 support-sensitive regulation path for the bounded
artifact-only support/regulation replay. It does not close ALI4, ALI5,
ALI6, A5, A6, agency, or identity acceptance.

```text
attempted_integration_level = A4
accepted_integration_level = A4
n10_category_level = ALI3
ali3_status = support_sensitive_regulation_closed_for_artifact_only_support_regulation_path
integration_outcome_tag = restoration_gated_integration_candidate
support_state_tag = explicit_restoration_recovers_support
integration_allowed = True
positive_integration_row_emitted = True
route/memory consumed = false
artifact_only = true
runtime_state_used = false
```

## Support Evidence

```json
{
  "explicit_restoration_present": true,
  "final_A_support_retention": 0.9244958974324687,
  "final_basin_separability": 0.9244958974324687,
  "final_budget_error": 0.0,
  "identity_support_outcome_tag": "explicit_restoration_recovers_support_survival_baseline",
  "lane_digest": "0a7c864269cbf0ffb1d1b2d02f95b5b3bd5a9e9c3fbc1b45b2a4d751902b5f5f",
  "n09_withdrawal_digest": "8e09a8de0b8d66e57e425a6c15a52abdf2e5090c65878eaf434c0751cc43fd84",
  "reference_A_support_retention": 0.9731535762447039,
  "restoration_fraction": 0.8,
  "source_lane_id": "restored_after_n09_partial_withdrawal",
  "support_above_threshold_after_restoration": true,
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
support_loss_from_reference = 0.04865767881223515
withdrawal_depth = 0.25
restoration_fraction = 0.8
```

## Preserved Disruption History

```json
{
  "blocked_record_digest": "56e2de6ab77b877a02cbc2df948f43be9461b4fa734232396d934b358edf426d",
  "disruption_history_preserved": true,
  "integration_allowed": false,
  "n09_withdrawal_digest": "8e09a8de0b8d66e57e425a6c15a52abdf2e5090c65878eaf434c0751cc43fd84",
  "positive_integration_row_emitted": false,
  "primary_blocker": "support_disrupted_but_integration_allowed",
  "source_iteration": 5,
  "support_lane_digest": "987651daaf122f47d3e26d3fd9d7611ceebb3149879b0326e6ca2775a18e4387",
  "support_lane_id": "n09_matched_partial_support_withdrawal",
  "support_survival_passed": false,
  "withdrawal_depth": 0.25
}
```

The disrupted-support blocker remains part of the replay chain. The
restored row resumes integration after that blocker; it does not erase
or overwrite it.

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

Iteration 6 claims source-artifact budget compatibility only. It does
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
    "reason": "Iteration 6 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "explicit restoration does not emit agency, A6, identity acceptance, or goal-ownership claims"
  },
  "disruption_history_preserved": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "restoration references the same N09 withdrawal digest and preserves the Iteration 5 blocked history"
  },
  "missing_goal_proxy_regulation_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_goal_proxy_regulation_artifact",
    "reason": "restoration replay requires N09 GPR closeout evidence"
  },
  "missing_identity_support_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_identity_support_artifact",
    "reason": "restoration replay requires N07 Iteration 13 support lane evidence"
  },
  "restoration_required_but_missing": {
    "control_passed": true,
    "primary_blocker": "restoration_required_but_missing",
    "reason": "integration resumes only because the explicit restoration lane is present and above threshold"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N07/N09 source artifact digests are rechecked against Iteration 1"
  },
  "stale_identity_support_baseline": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "restored support state is read from the current N07 Iteration 13 lane and matched against the N10 manifest summary"
  },
  "support_disrupted_control_not_erased": {
    "control_passed": true,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "reason": "restoration resumes after, rather than deletes, the disrupted-support blocker"
  }
}
```

## Checks

```json
{
  "a5_relevant_not_a5_closeout": true,
  "a6_not_supported_by_iteration_6": true,
  "accepted_integration_level_is_a4": true,
  "ali3_closed_for_support_regulation_path": true,
  "artifact_only_replay": true,
  "attempted_integration_level_is_a4": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "explicit_restoration_present": true,
  "fixture_required_support_state_tag_matched": true,
  "integration_allowed_true_after_restoration": true,
  "integration_row_digest_valid": true,
  "integration_row_required_fields_present": true,
  "n09_budget_control_passed": true,
  "n09_goal_proxy_candidate_available": true,
  "n09_gpr6_available": true,
  "n10_category_level_is_ali3": true,
  "positive_integration_row_emitted": true,
  "primary_blocker_absent_after_restoration": true,
  "prior_disruption_history_preserved": true,
  "prior_disruption_was_blocked": true,
  "restored_support_budget_error_zero": true,
  "restored_support_lane_survives": true,
  "restored_support_retention_meets_threshold": true,
  "route_memory_not_consumed_for_ali3": true,
  "same_n09_withdrawal_digest_as_disruption": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_6": true,
  "support_state_tag_is_explicit_restoration": true
}
```

## Acceptance

Iteration 6 passes if integration can resume after support disruption only through explicit, source-backed restoration evidence, while preserving the history of disruption and restoration.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_6_explicit_restoration_replay.py
```

Output digest:

```text
64a06e25f579994ca386376f24e53ed9aa12fb798b524704e20beca94704087c
```
