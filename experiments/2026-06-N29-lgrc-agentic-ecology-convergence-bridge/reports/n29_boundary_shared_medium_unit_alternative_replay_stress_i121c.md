# Prototype B - Alternative Unit Replay And Stress

Status: `passed`

Acceptance state: `accepted_alternative_boundary_shared_medium_bridge_candidate_controlled_replay_stress`

Output digest: `09a8717a2079adb047f21e30dddfe36f6030a2d6875cb72bf2e9d54d8af51693`

## Replay / Stress

| Row | Status |
|---|---|
| `artifact_only_replay` | `passed` |
| `snapshot_load_replay` | `passed` |
| `duplicate_replay` | `passed` |
| `medium_coupling_stress` | `passed` |
| `merge_pressure_stress` | `passed` |
| `counterpart_separability_stress` | `passed` |

Alternative bridge candidate supported: `true`

Repeatability strengthened: `true`

## Margin Interpretation

Interpretation: `repeatability_strengthening_not_widened_stress_margin`

I12 basin-side support/coherence: `1.1`

I12.1 basin-side support/coherence: `3.1`

Basin-side delta: `2.0`

I12 observed incident flux: `0.0`

I12.1 observed incident flux: `0.0`

Declared merge/leakage ceiling: `0.0`

The sibling variant improves basin-side support/coherence and repeatability across orientation, but it does not widen the I12 stress envelope or improve merge/leakage headroom.

## Checks

| Check | Passed |
|---|---|
| `i121a_passed` | `true` |
| `i121b_passed` | `true` |
| `i121b_failed_open_count_zero` | `true` |
| `all_replay_stress_rows_pass_or_demote_cleanly` | `true` |
| `alternative_is_repeatability_not_replacement` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
