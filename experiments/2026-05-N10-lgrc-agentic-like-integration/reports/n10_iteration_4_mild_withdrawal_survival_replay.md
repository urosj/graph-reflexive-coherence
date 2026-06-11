# N10 Iteration 4 Mild Withdrawal Survival Replay

Status: `passed`.

## Result

Iteration 4 replayed the N09 goal-proxy regulation evidence against
the N07 mild support-weakening lane. The support lane remains above
its survival threshold without restoration, so the row remains
consumable as ALI2 support-aware regulation evidence.

This is A5-relevant support-survival evidence, but it does not close
ALI3, A5, or A6. Disrupted-support and explicit-restoration controls
remain assigned to Iterations 5 and 6.

```text
integration_level = A4
n10_category_level = ALI2
integration_outcome_tag = support_aware_regulation_candidate
support_state_tag = mild_withdrawal_survives
a5_relevance = mild_withdrawal_survival_component_not_a5_closeout
route/memory consumed = false
artifact_only = true
runtime_state_used = false
```

## Support Evidence

```json
{
  "final_A_support_retention": 0.8758382186202335,
  "final_basin_separability": 0.8758382186202335,
  "final_budget_error": 0.0,
  "identity_support_outcome_tag": "support_withdrawal_survival_baseline",
  "lane_digest": "d5fae1cee95b0650287173c3e0456f1df42464771336b4e6e02cfb4e095bff69",
  "reference_A_support_retention": 0.9731535762447039,
  "restoration_fraction": 0.0,
  "source_lane_id": "mild_support_weakening",
  "support_loss_from_reference": 0.09731535762447041,
  "support_survival_passed": true,
  "support_survival_threshold": 0.85,
  "withdrawal_depth": 0.1,
  "withdrawal_kind": "partial_support_weakening"
}
```

Interpretation:

```text
final_A_support_retention = 0.8758382186202335
support_survival_threshold = 0.85
support_loss_from_reference = 0.09731535762447041
withdrawal_depth = 0.1
restoration_fraction = 0.0
```

The mild-withdrawal lane weakens support but does not destroy it. N10
therefore keeps the support-aware regulation row consumable while
recording that this is not yet a disruption/restoration closeout.

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

Iteration 4 claims source-artifact budget compatibility only. It does
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
    "reason": "Iteration 4 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "mild withdrawal survival does not emit agency, A6, identity acceptance, or goal-ownership claims"
  },
  "hidden_restoration_not_used": {
    "control_passed": true,
    "primary_blocker": "restoration_required_but_missing",
    "reason": "the mild-withdrawal lane remains above threshold without consuming restoration evidence"
  },
  "hidden_support_assumption": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "support survival is backed by the N07 lane threshold, not by an N10-side assumption"
  },
  "missing_goal_proxy_regulation_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_goal_proxy_regulation_artifact",
    "reason": "mild-withdrawal replay requires N09 GPR closeout evidence"
  },
  "missing_identity_support_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_identity_support_artifact",
    "reason": "mild-withdrawal replay requires N07 Iteration 13 support lane evidence"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N07/N09 source artifact digests are rechecked against Iteration 1"
  },
  "stale_identity_support_baseline": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "mild support state is read from the current N07 Iteration 13 lane and matched against the N10 manifest summary"
  }
}
```

## Checks

```json
{
  "a5_relevant_not_a5_closeout": true,
  "a6_not_supported_by_iteration_4": true,
  "artifact_only_replay": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "fixture_required_support_state_tag_matched": true,
  "integration_level_is_a4_not_a6": true,
  "integration_row_digest_valid": true,
  "integration_row_required_fields_present": true,
  "mild_support_budget_error_zero": true,
  "mild_support_lane_survives": true,
  "mild_support_retention_meets_threshold": true,
  "n09_budget_control_passed": true,
  "n09_goal_proxy_candidate_available": true,
  "n09_gpr6_available": true,
  "n10_category_level_is_ali2": true,
  "no_hidden_restoration_used": true,
  "route_memory_not_consumed_for_ali2": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_4": true,
  "support_state_tag_is_mild_withdrawal": true
}
```

## Acceptance

Iteration 4 passes if N10 records whether support-aware regulation remains consumable under mild support weakening, with source-backed support survival and no hidden restoration.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_4_mild_withdrawal_survival_replay.py
```

Output digest:

```text
2741abb505c2491c73ca0d7b8efc780ad70934f52724f4cacb7dff28d4b4b542
```
