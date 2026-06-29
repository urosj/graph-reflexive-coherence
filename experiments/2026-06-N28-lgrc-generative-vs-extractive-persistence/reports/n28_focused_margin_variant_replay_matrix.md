# N28 Iteration 5-B - Focused Margin Variant Replay Matrix

## Summary

- Status: `passed`
- Acceptance state: `accepted_focused_margin_variants_ge4_replay_control_backed_pending_stress`
- Output digest: `0ce6c4dcb35f4c7bef0f2e17c8ab2ff87bde958706c390fd05e016b5092fb08e`
- Provisional GE rung: `GE4`
- Ready for I6-C stress: `true`

I5-B replays the focused higher-margin variants I4-F and I4-G. It does
not replace I5; it validates that the targeted neutral and competitive
margin-strengthening rows are consumable as GE4 before focused stress.

## Replay Rows

| Row | Source | Regime | Decision | Rung |
|---|---|---|---|---|
| `n28_i5b_replay_n28_i4f_row_higher_margin_neutral_circulation_contrast` | `4-F` | `neutral` | `supported` | `GE4` |
| `n28_i5b_replay_n28_i4g_row_higher_margin_competitive_redistribution_contrast` | `4-G` | `competitive` | `supported` | `GE4` |

## Interpretation

Both focused variants replay under the same shared policy family. Neutral
circulation and competitive redistribution remain contrast rows, not
generative rows. GE5 remains pending I6-C stress/envelope validation.

## Checks

| Check | Passed |
|---|---|
| `all_focused_sources_present` | `true` |
| `all_source_digests_match_expected` | `true` |
| `artifact_snapshot_duplicate_replay_passed` | `true` |
| `all_regime_labels_stable_under_replay` | `true` |
| `all_capacity_attribution_controls_passed` | `true` |
| `single_shared_policy_family_preserved` | `true` |
| `all_rows_consumable_as_ge4` | `true` |
| `ge5_still_pending_i6c` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
