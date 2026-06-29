# N28 Iteration 5 - Replay And Capacity Attribution Matrix

## Summary

- Status: `passed`
- Acceptance state: `accepted_replay_control_backed_ge4_regime_separation_candidate_pending_stress`
- Output digest: `3fd8875fa01e4cbb91933bc89cf2db32a1a2d8396a6ebc16451c33a008af6caa`
- Provisional GE rung: `GE4`
- GE4 or stronger supported: `true`
- GE5 or stronger supported: `false`
- Shared policy status: `replay_control_backed_pending_stress`
- Ready for I6: `true`

I5 replays all eight I4-family regime rows: three generative, three extractive, and two competitive/neutral rows. Each row passes artifact replay, snapshot/load replay, duplicate replay, regime classification replay, capacity-attribution controls, merge/leakage controls, and focal-survival-only controls.

## Matrix Result

```text
source_row_count = 8
regime_counts = {'competitive': 1, 'extractive': 3, 'generative': 3, 'neutral': 1}
all_artifact_replay_passed = true
all_snapshot_load_replay_passed = true
all_duplicate_replay_passed = true
all_capacity_attribution_controls_passed = true
all_regime_labels_stable_under_replay = true
single_shared_policy_family_preserved = true
rows_demoted = []
```

## Replay Rows

| Source | Regime | Replay | Controls | Final rung | Demotion |
|---|---|---|---|---|---|
| `4` | `generative` -> `generative` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |
| `4-A` | `generative` -> `generative` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |
| `4-A2` | `generative` -> `generative` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |
| `4-B` | `extractive` -> `extractive` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |
| `4-C` | `extractive` -> `extractive` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |
| `4-C2` | `extractive` -> `extractive` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |
| `4-D` | `competitive` -> `competitive` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |
| `4-E` | `neutral` -> `neutral` | `passed/passed/passed` | `passed/passed/passed` | `GE4` | `none` |

## Interpretation

I5 upgrades the I4-family evidence from provisional GE3 source-current regime rows to a replay/control-backed GE4 regime-separation candidate. The upgrade is matrix-level: it depends on every generative, extractive, and competitive/neutral row replaying with stable classification and fail-closed attribution controls.

This still does not support GE5 or GE6. I6 must stress the same regime boundaries before N28 can claim stress/variant-backed paired-regime separation. I7 and I8 still need claim classification and closeout.

Duplicate replay uses the same convention as prior experiments: `first_emitted=true` and `second_emitted=false` means the second replay suppressed a duplicate while preserving the same digest.

## Checks

| Check | Passed |
|---|---|
| `i2_schema_consumed` | `true` |
| `i3_active_nulls_consumed` | `true` |
| `all_i4_family_rows_present` | `true` |
| `all_source_digests_match_expected` | `true` |
| `artifact_snapshot_duplicate_replay_passed` | `true` |
| `capacity_attribution_controls_passed` | `true` |
| `merge_leakage_controls_passed` | `true` |
| `focal_survival_only_controls_passed` | `true` |
| `all_regime_labels_stable_under_replay` | `true` |
| `single_shared_policy_family_preserved` | `true` |
| `all_rows_consumable_as_ge4` | `true` |
| `ge5_and_ge6_still_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

I5 supports only a GE4 replay/control-backed regime-separation candidate pending stress, claim classification, and closeout. It does not support GE5, GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, or ant ecology.
