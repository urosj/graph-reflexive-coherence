# N26 Iteration 5-B - Fixed-Surface Divergence Search

Status: `passed`

Acceptance state: `accepted_fixed_surface_divergence_search_no_admissible_pd4_pair`

## Summary

I5-B applies the stricter PD4 question that I5-A could not answer:
can an existing native N25.2 source show proxy improvement while the
basin metric stalls or degrades without changing the proxy surface,
basin metric, threshold policy, or control envelope?

The search finds no admissible fixed-surface PD4 pair. The native route
arbitration records provide selected-vs-rejected route-score contrast,
but rejected routes do not emit child-basin state traces. The selected
cross-route candidates both emit child-basin state, but their child
scope and threshold surfaces differ, and no route-score improvement
appears between them.

## Rows

| Row | Role | Proxy Delta | Basin Delta | PD4 Blocker |
| --- | --- | ---: | --- | --- |
| `n26_i5b_reference_selected_vs_rejected_route_pair` | `selected_vs_rejected_route_candidate_pair` | 0.500000 | `not_evaluable_missing_rejected_route_basin_trace` | `rejected_route_lacks_child_basin_state_trace` |
| `n26_i5b_variant_selected_vs_rejected_route_pair` | `selected_vs_rejected_route_candidate_pair` | 0.500000 | `not_evaluable_missing_rejected_route_basin_trace` | `rejected_route_lacks_child_basin_state_trace` |
| `n26_i5b_cross_variant_selected_route_score_pair` | `cross_variant_selected_route_fixed_proxy_pair` | 0.000000 | `2.000000` | `cross_variant_child_scope_and_threshold_surface_mismatch` |
| `n26_i5b_source_threshold_surface_pair` | `source_threshold_fixed_gap_pair` | 0.000000 | `2.000000` | `no_proxy_improvement_and_threshold_surface_mismatch` |

## Interpretation

This is a stronger negative result than I5-A. I5-A showed that
proxy-looking divergence can be induced by changing proxy/evaluation
surfaces. I5-B holds the surface fixed and asks whether the current
native evidence contains a real PD4 pair. It does not.

The correct ceiling remains:

```text
PD3 replay-backed proxy/basin contrast supported
PD4 controlled proxy divergence blocked
proxy collapse not opened
AP5 bridge closeout not supported
```

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_ready` | `true` |
| `fixed_surface_search_executed` | `true` |
| `no_admissible_pd4_fixed_surface_pair` | `true` |
| `selected_vs_rejected_pairs_blocked_by_missing_rejected_basin_trace` | `true` |
| `cross_variant_pairs_blocked_by_scope_or_threshold_mismatch` | `true` |
| `i5_and_i5a_not_overwritten` | `true` |
| `scoped_mb6_boundary_preserved` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_fixed_surface_divergence_search.json
outputs/n26_fixed_surface_divergence_search_artifacts/
reports/n26_fixed_surface_divergence_search.md
scripts/build_n26_fixed_surface_divergence_search.py
```
