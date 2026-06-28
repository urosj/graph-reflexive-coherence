# N26 Iteration 5-A - Alternative Proxy Surface Divergence Probe

Status: `passed`

Acceptance state: `accepted_alternative_proxy_surface_divergence_shape_detected_pd4_blocked`

## Summary

I5-A tries alternative proxy surfaces over the existing N25.2 scoped
substrate: threshold margin and replay-window surplus. Both can create
divergence-shaped signals, but the signals are mediated by changed
threshold policy or changed evaluation window requirements. They are
therefore rejected as controlled PD4 proxy divergence.

## Rows

| Row | Proxy Surface | Candidate | Proxy Delta | Basin Delta | Blocker |
| --- | --- | --- | ---: | ---: | --- |
| `n26_i5a_threshold_margin_i4_reference_child_basin_core_0` | `threshold_margin` | `i4_reference_child_basin_core_0` | 0.100000 | 0.000000 | `threshold_policy_relaxation_mediated_proxy_improvement` |
| `n26_i5a_window_surplus_i4_reference_child_basin_core_0` | `window_surplus` | `i4_reference_child_basin_core_0` | 1.000000 | 0.000000 | `evaluation_window_requirement_shift_mediated_proxy_improvement` |
| `n26_i5a_threshold_margin_i4a_route_variant_child_basin_core_2` | `threshold_margin` | `i4a_route_variant_child_basin_core_2` | 0.100000 | 0.000000 | `threshold_policy_relaxation_mediated_proxy_improvement` |
| `n26_i5a_window_surplus_i4a_route_variant_child_basin_core_2` | `window_surplus` | `i4a_route_variant_child_basin_core_2` | 1.000000 | 0.000000 | `evaluation_window_requirement_shift_mediated_proxy_improvement` |

## Claim Boundary

`candidate_pd_ladder_rung = PD3`

`controlled_proxy_divergence_candidate_supported = false`

I5-A strengthens the negative result: proxy divergence-shaped signals
can be induced by proxy/evaluation-surface changes, but those signals
fail closed and do not upgrade I5.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_ready` | `true` |
| `divergence_shaped_signal_observed` | `true` |
| `all_divergence_shaped_rows_fail_closed_for_PD4` | `true` |
| `i5_conclusion_not_overwritten` | `true` |
| `scoped_mb6_boundary_preserved` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_alternative_proxy_surface_divergence_probe.json
outputs/n26_alternative_proxy_surface_divergence_probe_artifacts/
reports/n26_alternative_proxy_surface_divergence_probe.md
scripts/build_n26_alternative_proxy_surface_divergence_probe.py
```
