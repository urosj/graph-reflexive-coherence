# N10 Iteration 3 Support-Aware Regulation Replay

Status: `passed`.

## Result

Iteration 3 replayed N09 goal-proxy regulation as support-aware under
the N07 support-intact baseline. This is an ALI2 row, not full
route-memory-regulation composition and not A6/ALI6.

```text
integration_level = A4
n10_category_level = ALI2
integration_outcome_tag = support_aware_regulation_candidate
route/memory consumed = false
artifact_only = true
runtime_state_used = false
```

## Support Evidence

```json
{
  "final_A_support_retention": 0.9731535762447039,
  "final_basin_separability": 0.9731535762447039,
  "final_budget_error": 0.0,
  "lane_digest": "359d248493fc4ce8ee57f5f682d043cc745762671ab1a67fb8c779e38ed67bdb",
  "source_lane_id": "support_intact_reference",
  "support_survival_passed": true
}
```

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

Iteration 3 claims source-artifact budget compatibility only. It does
not claim one continuous packet ledger across separate N07 and N09
runs.

```text
budget_mode = source_artifact_budget_compatibility_not_single_runtime_continuity
node_plus_packet_budget_error = 0.0
```

## Controls

```json
{
  "budget_surface_ambiguity": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "Iteration 3 claims source-artifact budget compatibility only, not cross-artifact live ledger continuity"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "ALI2 support-aware regulation replay cannot emit agency, A6, identity acceptance, or goal-ownership claims"
  },
  "hidden_support_assumption": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "support state is read from N07 Iteration 13 support_intact_reference lane"
  },
  "missing_goal_proxy_regulation_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_goal_proxy_regulation_artifact",
    "reason": "support-aware replay requires N09 GPR closeout evidence"
  },
  "missing_identity_support_artifact": {
    "control_passed": true,
    "primary_blocker": "missing_identity_support_artifact",
    "reason": "support-aware replay requires N07 Iteration 13 support lane evidence"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N07/N09 source artifact digests are rechecked against Iteration 1"
  }
}
```

## Checks

```json
{
  "a6_not_supported_by_iteration_3": true,
  "artifact_only_replay": true,
  "claim_flags_all_false": true,
  "controls_passed": true,
  "integration_level_is_a4_not_a6": true,
  "integration_row_digest_valid": true,
  "integration_row_required_fields_present": true,
  "n09_budget_control_passed": true,
  "n09_goal_proxy_candidate_available": true,
  "n09_gpr6_available": true,
  "n10_category_level_is_ali2": true,
  "route_memory_not_consumed_for_ali2": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_3": true,
  "support_intact_lane_survives": true,
  "support_lane_budget_error_zero": true,
  "support_state_tag_valid": true
}
```

## Acceptance

Iteration 3 passes if N09 goal-proxy regulation can be replayed as support-aware under the N07 support-intact baseline without hidden support assumptions or claim promotion.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_3_support_aware_regulation_replay.py
```

Output digest:

```text
74c5764cdf8f9309fe84188359e3c64f9dea869d962b3121e657d55ca582378c
```
