# N24 Iteration 6 - Replay And Control Matrix

Status: `passed`

Acceptance state: `accepted_replay_control_backed_ab4_candidate_no_ab5`

Output digest: `da1d7e517c69e3b8e652291f097d973d7a3eea686a7d3245e78e3a05de82a455`

## Summary

Iteration 6 replays the I4 AB2 surplus row and the I5 AB3 optional-continuation
row. I4 remains AB2 because replay cannot create optionality. I5 advances
to a provisional AB4 candidate because the optional set survives artifact,
snapshot/load, and duplicate replay while the control matrix stays fail-closed.

AB5 and N24 closeout remain pending Iteration 7 stress/threshold testing and
Iteration 8 closeout.

## Geometric Interpretation

I6 validates that the I5 optional branches are not merely labels: the same LGRC snapshot reloads, the same maintenance basin signature reappears, the same three branch records remain in one source-current window, and support/coherence margins remain positive.

I4 is replay-stable AB2 surplus evidence only. Its surplus margin replays from the snapshot, but it has no optional set, so it cannot become AB4 by replay alone.

I5 becomes a provisional AB4 candidate because the AB3 optional set survives artifact, snapshot/load, and duplicate replay while hidden-budget, floor-crossing, proxy-only, label-only, post-hoc, N23 relabel, reward, AP-gap, and unsafe relabel controls stay closed.

AB5 remains blocked because stress/threshold backing and joint admissibility under stress are I7 scope. The row is not reward maximization, semantic choice, agency, native support, sentience, Phase 8, or ant ecology.

## Replay Matrix

| Source | Candidate | Artifact | Snapshot/load | Duplicate | Optional set | Final rung |
| --- | --- | --- | --- | --- | --- | --- |
| I4 | `n24_i4_row_01_minimal_source_current_surplus_probe` | `passed` | `passed` | `passed` | `not_applicable` | `AB2` |
| I5 | `n24_i5_row_01_source_current_optional_continuation_set_probe` | `passed` | `passed` | `passed` | `passed` | `AB4` |

## I5 Optionality Replay

```text
optional_continuation_availability_count = 3
branch_count = 3
residual_support_margin = 0.150000000000
residual_coherence_margin = 0.150000000000
boundary_integrity_status = preserved
flux_or_leakage_status = preserved
```

## Controls

| Candidate | Failed-open controls | Controls accept candidate |
| --- | --- | --- |
| I4 | `0` | `true` |
| I5 | `0` | `true` |

The negative control matrix uses `failed_closed` to mean the blocker
triggered and the overclaim was rejected. It does not mean validation failed.

## Boundary

```text
provisional_ab_ladder_rung = AB4
ab4_candidate_supported = true
ab5_or_stronger_supported = false
n24_closeout_ladder_rung_assigned = false
provisional_n24_closeout_ceiling = N24-C4
surplus_supported_optionality_claim_allowed = false
```

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_passed` | `true` |
| `i4_ab2_source_current_surplus_ready` | `true` |
| `i5_ab3_optional_continuation_ready` | `true` |
| `artifact_manifest_non_empty_and_sha_match` | `true` |
| `artifact_replay_modes_passed` | `true` |
| `i5_optional_set_survives_replay` | `true` |
| `i5_optional_branches_remain_same_run_same_window` | `true` |
| `i5_replayed_residual_margins_positive` | `true` |
| `i5_replayed_boundary_flux_clean` | `true` |
| `required_controls_present_and_no_failed_open` | `true` |
| `negative_controls_fail_closed_or_scope_clean` | `true` |
| `ab4_eligible_ab5_still_blocked` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `no_absolute_paths` | `true` |
