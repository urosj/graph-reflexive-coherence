# N28 Iteration 4-G - Higher-Margin Competitive Redistribution Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_higher_margin_competitive_redistribution_ge3_candidate_pending_replay_stress`
- Output digest: `8bc907a97b07c09c72fd7ceda63811555c335c0d45d6dbef6cfb29489f463e72`
- Provisional GE rung: `GE3`
- Ready for I5-B replay: `true`

I4-G is a focused source-current variant that targets the I6-B competitive
flattening bottleneck. It does not replace I4-D and does not retune the
shared policy. It widens the opposed route-lobe margins and lowers
flattening/extraction pressure while keeping aggregate neighborhood deltas
near neutral.

## Margin Comparison

```text
i4d_route_lobe_b_margin = 0.01
i4g_route_lobe_b_margin = 0.028
i4d_flattening_margin = 0.006
i4g_flattening_margin = 0.011
same_shared_policy_family = true
i4d_replaced = false
```

## Interpretation

Geometrically, I4-G is still a competitive redistribution regime: the
focal basin remains stable, aggregate neighbor capacity remains near
neutral, and one route lobe gains while the opposed lobe loses. The
difference from I4-D is margin placement. I4-G widens the lobe separation
and leaves more room below flattening/extraction ceilings, directly
addressing the I6-B competitive flattening bottleneck.

This is not GE4/GE5 yet. It is a GE3 source-current row pending I5-B
replay/control and I6-C stress/envelope validation.

## Checks

| Check | Passed |
|---|---|
| `i4d_competitive_baseline_consumed` | `true` |
| `i6b_bottleneck_context_consumed` | `true` |
| `competitive_lobe_margins_improved_vs_i4d` | `true` |
| `flattening_margin_improved_vs_i4d` | `true` |
| `same_shared_policy_family_preserved` | `true` |
| `competitive_not_promoted_to_generative_or_extractive` | `true` |
| `artifact_manifest_hashes_match` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
