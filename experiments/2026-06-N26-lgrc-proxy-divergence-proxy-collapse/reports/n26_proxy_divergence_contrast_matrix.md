# N26 Iteration 5 - Proxy Divergence Contrast Matrix

Status: `passed`

Acceptance state: `accepted_replay_backed_pd3_proxy_basin_contrast_no_controlled_divergence`

## Summary

I5 pairs the two scoped N25.2 child-basin candidates across each I4-A
stress axis. The matrix supports replay-backed proxy/basin contrast
at PD3. It does not support controlled proxy divergence: no row shows
proxy improvement while basin persistence/deepening stalls or degrades
under independent measurement.

## Contrast Rows

| Row | Axis | Stress | Class | Reference Gap | Peer Gap | PD4 |
| --- | --- | --- | --- | ---: | ---: | --- |
| `n26_i5_child_basin_persistence_window_multi_window_2_persistence_replay` | `child_basin_persistence_window` | `multi_window_2_persistence_replay` | `aligned_zero_gap_pass` | 0.000000 | 0.000000 | `false` |
| `n26_i5_child_basin_persistence_window_multi_window_3_persistence_replay` | `child_basin_persistence_window` | `multi_window_3_persistence_replay` | `aligned_zero_gap_pass` | 0.000000 | 0.000000 | `false` |
| `n26_i5_child_basin_persistence_window_source_one_window_replay` | `child_basin_persistence_window` | `source_one_window_replay` | `aligned_zero_gap_pass` | 0.000000 | 0.000000 | `false` |
| `n26_i5_flow_window_threshold_relaxed_threshold_replay` | `flow_window_threshold` | `relaxed_threshold_replay` | `aligned_zero_gap_pass` | 0.000000 | 0.000000 | `false` |
| `n26_i5_flow_window_threshold_source_threshold_replay` | `flow_window_threshold` | `source_threshold_replay` | `aligned_zero_gap_pass` | 0.000000 | 0.000000 | `false` |
| `n26_i5_flow_window_threshold_tightened_threshold_fail_closed` | `flow_window_threshold` | `tightened_threshold_fail_closed` | `aligned_nonzero_gap_fail_closed` | 0.083333 | 0.031250 | `false` |
| `n26_i5_merge_leakage_pressure_injected_merge_leakage_pressure_fail_closed` | `merge_leakage_pressure` | `injected_merge_leakage_pressure_fail_closed` | `aligned_nonzero_gap_fail_closed` | 1.000000 | 1.000000 | `false` |
| `n26_i5_merge_leakage_pressure_source_merge_leakage_ceiling` | `merge_leakage_pressure` | `source_merge_leakage_ceiling` | `aligned_zero_gap_pass` | 0.000000 | 0.000000 | `false` |

## Claim Boundary

`candidate_pd_ladder_rung = PD3`

`n26_closeout_ceiling = N26-C4_source_current_proxy_derivation_and_replay_backed_contrast_supported`

`controlled_proxy_divergence_candidate_supported = false`

I5 supports contrast, not divergence. Proxy collapse remains I6 scope.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_ready` | `true` |
| `all_candidate_required_fields_present` | `true` |
| `pd3_artifact_roles_present` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `peer_or_control_basin_present` | `true` |
| `replay_backed_contrast_present` | `true` |
| `controlled_proxy_divergence_not_supported` | `true` |
| `proxy_collapse_not_opened` | `true` |
| `ap5_dependency_recorded_without_native_ap5_upgrade` | `true` |
| `scoped_mb6_boundary_preserved` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_proxy_divergence_contrast_matrix.json
outputs/n26_proxy_divergence_contrast_matrix_artifacts/
reports/n26_proxy_divergence_contrast_matrix.md
scripts/build_n26_proxy_divergence_contrast_matrix.py
```
