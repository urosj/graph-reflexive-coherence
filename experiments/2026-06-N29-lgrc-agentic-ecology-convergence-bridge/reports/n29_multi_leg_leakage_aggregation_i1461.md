# Prototype D I14.6-1 Multi-Leg Leakage Aggregation Probe

Status: `passed`

Acceptance state: `accepted_multi_leg_leakage_aggregation_bridge_candidate_pending_i14d_i14e`

Output digest: `51c409081b93492d3f4991f5a7ca7353cb10bd29e0a95aad02552339974ade26`

## Summary

```text
multi_leg_leakage_aggregation_supported = true
native_aggregate_shared_medium_leakage_supported = false
producer_mediated_bridge_lane_recorded = true
ready_for_i14d_i14e = true
ready_for_iteration_15 = false
```

## Geometry

I14.6-1 puts the I14.5-2 phase-feedback leg and the I14.4-4 directed-cycle leg into a common producer-mediated leakage frame. It does not cancel one leakage value against the other and does not discount overlap. The aggregate leakage is the full sum of both legs. That supports a narrow bridge-lane aggregate leakage record, while native shared-medium leakage aggregation remains unsupported.

The aggregation is intentionally conservative: both leg leakages are
summed. No cancellation, overlap credit, hidden sink/source, or
double-counting discount is used.

## Leakage

```text
phase_feedback_leg_merge_leakage = 0.018
directed_cycle_leg_merge_leakage = 0.019
aggregate_merge_leakage = 0.037
aggregate_merge_leakage_ceiling = 0.04
aggregate_merge_leakage_margin = 0.003
narrow_margin_recorded = true
```

## Claim Boundary

Claim ceiling: `producer_mediated_multi_leg_leakage_aggregation_candidate_pending_controls_replay`

The row supports only producer-mediated aggregate leakage attribution.
Native shared-medium leakage aggregation, resource economy, cooperation,
exploitation, ecology success, and agency remain blocked.

## Remaining Debt

- I14-D composition controls pending
- I14-E replay/stress pending
- aggregate leakage margin is narrow
- aggregation frame is producer-mediated, not native shared-medium LGRC
- resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked

## Checks

| Check | Passed |
|---|---:|
| `i14_6_prior_per_leg_only` | `true` |
| `shared_leakage_frame_declared` | `true` |
| `all_channels_mapped` | `true` |
| `full_sum_aggregation_passed` | `true` |
| `leakage_cancellation_rejected` | `true` |
| `overlap_credit_rejected` | `true` |
| `hidden_sink_or_source_rejected` | `true` |
| `double_counting_discount_rejected` | `true` |
| `native_aggregate_shared_medium_blocked` | `true` |
| `artifact_manifest_sha_match` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
