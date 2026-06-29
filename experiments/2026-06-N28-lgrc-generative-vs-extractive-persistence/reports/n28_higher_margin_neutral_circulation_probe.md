# N28 Iteration 4-F - Higher-Margin Neutral Circulation Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_higher_margin_neutral_circulation_ge3_candidate_pending_replay_stress`
- Output digest: `1848a9ffe8c4c0242ef2b670527b65bedbcd9ea5ae0c57a15a8208acf1ab0921`
- Provisional GE rung: `GE3`
- Ready for I5-B replay: `true`

I4-F is a focused source-current variant that targets the I6-B neutral
bottlenecks. It does not replace I4-E and does not retune the shared
policy. It widens the neutral circulation lobe margins and lowers
merge/leakage while keeping aggregate neighborhood deltas near neutral.

## Margin Comparison

```text
i4e_outflow_margin = 0.005
i4f_outflow_margin = 0.02
i4e_merge_leakage_margin = 0.005
i4f_merge_leakage_margin = 0.01
same_shared_policy_family = true
i4e_replaced = false
```

## Interpretation

Geometrically, I4-F is still a neutral/circulatory regime: the focal
basin remains stable, aggregate neighbor capacity remains near neutral,
and the environment is not broadly enriched or depleted. The difference
from I4-E is margin placement. I4-F routes more capacity through the
inflow/outflow circulation pair and keeps merge/leakage further below
ceiling, directly addressing the I6-B outflow-lobe and merge/leakage
bottlenecks.

This is not GE4/GE5 yet. It is a GE3 source-current row pending I5-B
replay/control and I6-C stress/envelope validation.

## Checks

| Check | Passed |
|---|---|
| `i4e_neutral_baseline_consumed` | `true` |
| `i6b_bottleneck_context_consumed` | `true` |
| `neutral_lobe_margins_improved_vs_i4e` | `true` |
| `merge_leakage_margin_improved_vs_i4e` | `true` |
| `same_shared_policy_family_preserved` | `true` |
| `neutral_not_promoted_to_generative_or_extractive` | `true` |
| `artifact_manifest_hashes_match` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
