# N26 Iteration 6 - Proxy Collapse Perturbation Matrix

Status: `passed`

Acceptance state: `accepted_provisional_pd5_proxy_collapse_candidate_pending_i7`

## Summary

I6 uses I5-C's provisional divergence result as the input and asks a
stronger collapse question: under the same declared perturbation floor,
does the proxy-optimized path fail while a basin-deepened contrast
survives?

Both mirrored route families support that shape. The high-score proxy
path fails the support/coherence challenge, while the lower-score but
source-current basin-deepened path survives the same challenge.

## Rows

| Row | Proxy Path Survives | Basin Path Survives | Proxy Advantage | Basin Advantage |
| --- | --- | --- | ---: | ---: |
| `n26_i6_proxy_collapse_perturbation_sink0_proxy_collapse` | `false` | `true` | 0.400000 | 0.500000 |
| `n26_i6_proxy_collapse_perturbation_sink2_proxy_collapse` | `false` | `true` | 0.400000 | 0.500000 |

## Interpretation

Geometrically, I6 separates route-score optimization from basin capacity.
The proxy-optimized path has the higher route score, but its emitted
child-basin support/coherence floor is below the perturbation floor.
The basin-deepened path has lower route score, but the source-current
geometry variant raises support/coherence enough to survive.

The claim remains bounded. This is a provisional producer-mediated PD5
candidate pending I7 replay/control/AP5 classification. The score and
deepening surfaces do not count as native AP5 target formation or native
support.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_ready` | `true` |
| `shared_perturbation_matrix_rows_emitted` | `true` |
| `proxy_optimized_paths_fail_under_perturbation` | `true` |
| `basin_deepened_paths_survive_same_perturbation` | `true` |
| `pd5_candidates_are_provisional_and_producer_mediated` | `true` |
| `native_ap5_bridge_remains_blocked` | `true` |
| `scoped_mb6_boundary_preserved` | `true` |
| `artifact_sha256_match_file_contents` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_proxy_collapse_perturbation_matrix.json
outputs/n26_proxy_collapse_perturbation_matrix_artifacts/
reports/n26_proxy_collapse_perturbation_matrix.md
scripts/build_n26_proxy_collapse_perturbation_matrix.py
```
