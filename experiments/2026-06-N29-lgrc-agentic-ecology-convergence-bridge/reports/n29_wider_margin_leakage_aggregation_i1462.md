# Prototype D I14.6-2 Wider-Margin Leakage Aggregation Variant

Status: `passed`

Acceptance state: `accepted_wider_margin_leakage_aggregation_bridge_variant_pending_i14d_i14e`

Output digest: `57c86cb4776a71a246d7e72aea0c73b60beff0f27066aa5ba3d298ff1c2f4686`

## Summary

```text
wider_margin_multi_leg_leakage_aggregation_supported = true
native_aggregate_shared_medium_leakage_supported = false
producer_mediated_bridge_lane_recorded = true
ready_for_i14d_i14e = true
ready_for_iteration_15 = false
```

## Geometry

I14.6-2 strengthens I14.6-1 by routing both leakage channels through one declared producer-mediated interface guard before applying the same full-sum aggregation policy. The aggregate ceiling is unchanged. The wider margin comes from lower net channel leakage after a visible bridge guard, with captured leakage recorded as producer debt rather than hidden native success.

This is not a ceiling relaxation. The aggregate ceiling remains 0.04,
matching I14.6-1. The wider margin comes from a visible producer-mediated
interface guard applied uniformly to both channels, with captured leakage
recorded as producer debt.

## Leakage

```text
gross_aggregate_merge_leakage_before_window = 0.037
net_aggregate_merge_leakage = 0.0296
producer_guard_captured_leakage_total = 0.0074
aggregate_merge_leakage_ceiling = 0.04
aggregate_merge_leakage_margin = 0.0104
margin_improvement_over_i14_6_1 = 0.0074
target_margin_gate_passed = true
```

## Claim Boundary

Claim ceiling: `producer_mediated_wider_margin_leakage_aggregation_variant_pending_controls_replay`

The row supports only a producer-mediated wider-margin aggregation
variant. Native shared-medium leakage aggregation, resource economy,
cooperation, exploitation, ecology success, and agency remain blocked.

## Remaining Debt

- I14-D composition controls pending
- I14-E replay/stress pending
- wider leakage margin is producer-mediated through a bridge interface guard
- producer guard capture remains naturalization debt, not native shared-medium leakage support
- resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked

## Checks

| Check | Passed |
|---|---:|
| `i14_6_1_supported` | `true` |
| `same_aggregate_ceiling_preserved` | `true` |
| `full_sum_aggregation_preserved` | `true` |
| `same_factor_all_channels` | `true` |
| `target_margin_gate_passed` | `true` |
| `ceiling_relaxation_rejected` | `true` |
| `leakage_cancellation_rejected` | `true` |
| `overlap_credit_rejected` | `true` |
| `hidden_sink_or_source_rejected` | `true` |
| `double_counting_discount_rejected` | `true` |
| `native_aggregate_shared_medium_blocked` | `true` |
| `artifact_manifest_sha_match` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
