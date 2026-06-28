# N26 Iteration 4-A - Proxy Derivation Sensitivity Probe

Status: `passed`

Acceptance state: `accepted_pd2_proxy_derivation_sensitivity_probe_no_pd3_no_divergence`

## Summary

I4-A checks whether the I4 proxy derivation responds to varied
source-current N25.2 stress rows. It uses the same coupling-gap family
as I4, with stress-normalized inputs from the N25.2 stress matrix.

The result is stronger than I4 in one specific way: zero-gap source rows
remain supported, while tightened-threshold and injected leakage rows
produce nonzero proxy gaps and fail closed. It does not add a passing
degraded positive row, and it does not support PD3, divergence, collapse,
or AP5 bridge closeout.

## Rows

| Row | Source | Axis | Stress | Gap | Decision |
| --- | --- | --- | --- | ---: | --- |
| `n26_i4a_i4_reference_child_basin_core_0_flow_window_threshold_source_threshold_replay` | `i4_reference_child_basin_core_0` | `flow_window_threshold` | `source_threshold_replay` | 0.000000 | `supported` |
| `n26_i4a_i4_reference_child_basin_core_0_flow_window_threshold_relaxed_threshold_replay` | `i4_reference_child_basin_core_0` | `flow_window_threshold` | `relaxed_threshold_replay` | 0.000000 | `supported` |
| `n26_i4a_i4_reference_child_basin_core_0_flow_window_threshold_tightened_threshold_fail_closed` | `i4_reference_child_basin_core_0` | `flow_window_threshold` | `tightened_threshold_fail_closed` | 0.083333 | `rejected` |
| `n26_i4a_i4_reference_child_basin_core_0_merge_leakage_pressure_source_merge_leakage_ceiling` | `i4_reference_child_basin_core_0` | `merge_leakage_pressure` | `source_merge_leakage_ceiling` | 0.000000 | `supported` |
| `n26_i4a_i4_reference_child_basin_core_0_merge_leakage_pressure_injected_merge_leakage_pressure_fail_closed` | `i4_reference_child_basin_core_0` | `merge_leakage_pressure` | `injected_merge_leakage_pressure_fail_closed` | 1.000000 | `rejected` |
| `n26_i4a_i4_reference_child_basin_core_0_child_basin_persistence_window_source_one_window_replay` | `i4_reference_child_basin_core_0` | `child_basin_persistence_window` | `source_one_window_replay` | 0.000000 | `supported` |
| `n26_i4a_i4_reference_child_basin_core_0_child_basin_persistence_window_multi_window_2_persistence_replay` | `i4_reference_child_basin_core_0` | `child_basin_persistence_window` | `multi_window_2_persistence_replay` | 0.000000 | `supported` |
| `n26_i4a_i4_reference_child_basin_core_0_child_basin_persistence_window_multi_window_3_persistence_replay` | `i4_reference_child_basin_core_0` | `child_basin_persistence_window` | `multi_window_3_persistence_replay` | 0.000000 | `supported` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_flow_window_threshold_source_threshold_replay` | `i4a_route_variant_child_basin_core_2` | `flow_window_threshold` | `source_threshold_replay` | 0.000000 | `supported` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_flow_window_threshold_relaxed_threshold_replay` | `i4a_route_variant_child_basin_core_2` | `flow_window_threshold` | `relaxed_threshold_replay` | 0.000000 | `supported` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_flow_window_threshold_tightened_threshold_fail_closed` | `i4a_route_variant_child_basin_core_2` | `flow_window_threshold` | `tightened_threshold_fail_closed` | 0.031250 | `rejected` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_merge_leakage_pressure_source_merge_leakage_ceiling` | `i4a_route_variant_child_basin_core_2` | `merge_leakage_pressure` | `source_merge_leakage_ceiling` | 0.000000 | `supported` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_merge_leakage_pressure_injected_merge_leakage_pressure_fail_closed` | `i4a_route_variant_child_basin_core_2` | `merge_leakage_pressure` | `injected_merge_leakage_pressure_fail_closed` | 1.000000 | `rejected` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_child_basin_persistence_window_source_one_window_replay` | `i4a_route_variant_child_basin_core_2` | `child_basin_persistence_window` | `source_one_window_replay` | 0.000000 | `supported` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_child_basin_persistence_window_multi_window_2_persistence_replay` | `i4a_route_variant_child_basin_core_2` | `child_basin_persistence_window` | `multi_window_2_persistence_replay` | 0.000000 | `supported` |
| `n26_i4a_i4a_route_variant_child_basin_core_2_child_basin_persistence_window_multi_window_3_persistence_replay` | `i4a_route_variant_child_basin_core_2` | `child_basin_persistence_window` | `multi_window_3_persistence_replay` | 0.000000 | `supported` |

## Claim Boundary

`candidate_pd_ladder_rung = PD2`

`n26_closeout_ceiling = N26-C3_active_nulls_fail_closed_with_PD2_sensitivity_checked_derivation_candidate`

I4-A strengthens source-current PD2 derivation sensitivity only. The
nonzero-gap rows are blocker evidence, not positive proxy divergence.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_ready` | `true` |
| `stress_rows_are_source_current_derived` | `true` |
| `sensitivity_rows_include_zero_and_nonzero_gaps` | `true` |
| `nonzero_gap_rows_fail_closed` | `true` |
| `i4_not_replaced_or_widened` | `true` |
| `scoped_mb6_boundary_preserved` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_proxy_derivation_sensitivity_probe.json
outputs/n26_proxy_derivation_sensitivity_probe_artifacts/
reports/n26_proxy_derivation_sensitivity_probe.md
scripts/build_n26_proxy_derivation_sensitivity_probe.py
```
