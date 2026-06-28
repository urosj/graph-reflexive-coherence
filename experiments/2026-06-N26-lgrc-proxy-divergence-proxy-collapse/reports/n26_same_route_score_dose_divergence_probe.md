# N26 Iteration 5-C - Same-Route Score-Dose Divergence Probe

Status: `passed`

Acceptance state: `accepted_provisional_pd4_same_route_score_dose_divergence_candidate_pending_i7`

## Summary

I5-C uses the lesson from I5-B: PD4 needs paired basin traces under a
fixed proxy surface. It therefore runs two mirrored same-route native
LGRC9V3 score-dose families. In each family the selected sink, packet
schedule, fixture, basin metric, and threshold/control envelope remain
fixed while the route arbitration score changes.

Both rows show route-score proxy improvement with basin geometry stalled.
The result is a provisional producer-mediated PD4 proxy-divergence
candidate pending I7 replay/control classification. It does not support
proxy collapse or native AP5.

## Rows

| Row | Proxy Delta | Basin Delta | Claim |
| --- | ---: | ---: | --- |
| `n26_i5c_same_route_score_dose_sink0_fixed_route` | 0.400000 | 0.000000 | `PD4_candidate_pending_I7` |
| `n26_i5c_same_route_score_dose_sink2_fixed_route` | 0.400000 | 0.000000 | `PD4_candidate_pending_I7` |

## Interpretation

Geometrically, I5-C keeps the emitted child-basin membership, support,
coherence, boundary, and flux surfaces fixed while increasing a
runtime-visible route-score proxy. The route-score proxy improves;
the basin does not deepen. That is the first positive controlled
proxy-divergence shape in N26.

The claim is deliberately bounded. The score surface is producer
mediated route-candidate input, so I5-C can support a provisional
PD4 divergence candidate but cannot close native AP5 or count the
score as native support.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_ready` | `true` |
| `score_dose_runtime_rows_emitted` | `true` |
| `all_rows_have_proxy_delta_with_basin_stall` | `true` |
| `pd4_candidates_are_provisional_and_producer_mediated` | `true` |
| `native_ap5_bridge_remains_blocked` | `true` |
| `scoped_mb6_boundary_preserved` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_same_route_score_dose_divergence_probe.json
outputs/n26_same_route_score_dose_divergence_probe_artifacts/
reports/n26_same_route_score_dose_divergence_probe.md
scripts/build_n26_same_route_score_dose_divergence_probe.py
```
