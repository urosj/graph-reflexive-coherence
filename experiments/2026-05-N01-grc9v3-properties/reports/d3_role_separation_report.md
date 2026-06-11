# D3 Row/Column Transpose Role Separation Report

Status: complete.

Classification: `supported_with_available_controls`.

## Scope

D3 reuses completed O-style artifacts and does not add runtime
behavior. Geometry response is reconstructed from Experiment A
`response_dominance_ratio`. Interface response is reconstructed from
Experiment B's Lane A derived column-cancellation proxy. Direct
column-H gating remains blocked under Lane A.

## Scoring

- `geometry_response_score`: row-response dominance ratio from Experiment A.
- `interface_response_score`: max per-column cancellation score from Experiment B.
- `role_separation_index = geometry(row local) + interface(column local) - geometry(transposed row local) - interface(transposed column local)`.

## Aggregate Result

| Geometry Row-Local | Geometry Transposed | Interface Column-Local | Interface Transposed | Role Separation Index |
| --- | --- | --- | --- | --- |
| 0.627051 | 0.333333 | 0.988678 | 0.000000 | 1.282396 |

The positive role-separation index means the row-local pattern carries
the stronger geometry/differential response, while the column-local
pattern carries the stronger interface-proxy response. Transpose changes
which artifact class is supported rather than preserving anonymous-port
equivalence.

## Pair Rows

| Pattern | Class | Geometry Base | Geometry Transpose | Interface Base | Interface Transpose | Index | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| a_row_1_stress_seed_0 | single_row_high | 0.6406992361759353 | 0.33333333333333337 |  |  | 0.3073659028426019 | derived |
| a_row_2_stress_seed_0 | single_row_high | 0.6202275769057038 | 0.33333333333333337 |  |  | 0.2868942435723705 | derived |
| a_row_3_stress_seed_0 | single_row_high | 0.6202275769057038 | 0.33333333333333337 |  |  | 0.2868942435723705 | derived |
| b_column_1_near_cancellation_near_zero_seed_0 | single_column_high_proxy |  |  | 0.9886779479761213 | 0.0 | 0.9886779479761213 | derived |
| b_column_2_near_cancellation_near_zero_seed_0 | single_column_high_proxy |  |  | 0.9886779479761213 | 0.0 | 0.9886779479761213 | derived |
| b_column_3_near_cancellation_near_zero_seed_0 | single_column_high_proxy |  |  | 0.9886779479761213 | 0.0 | 0.9886779479761213 | derived |
| a_balanced_diagonal_seed_0 | symmetric_isotropic_control | 0.33333333333333337 | 0.33333333333333337 |  |  | 0.0 | derived |

## Controls

| Control | Status | Evidence | Notes |
| --- | --- | --- | --- |
| single_row_high | available | derived | A row-stress identities and transpose controls provide row-local geometry responses. |
| single_column_high | available_as_derived_proxy | derived | B column-cancellation identities and transpose controls provide derived interface responses. |
| diagonal_symmetric | available | derived | A balanced diagonal row-response control is transpose-stable and avoids a false positive. |
| anti_diagonal | blocked | blocked | No anti-diagonal transpose fixture has been run; not inferred. |
| rank_1_row_x_column | blocked | blocked | No explicit rank-1 row x column pattern has been run; not inferred. |
| symmetric_isotropic | available | derived | Balanced row-response rows have equal row scores before and after transpose. |
| pre_event_dynamics_phase | available | derived | D3 scoring is computed from pre-event row and derived column artifact rows. |
| event_capable_dynamics_phase | inconclusive | inconclusive | No transpose-specific event-capable D3 fixture is available without new runtime work. |
| row_permutation | available | derived | Structured row permutations preserve the expected row/column semantic class. |
| column_permutation | available | derived | Structured column permutations preserve the expected row/column semantic class. |
| arbitrary_s9_relabel | available_sampled_proxy | derived | The control is sampled and non-factorized; it is not exhaustive over all 9! relabels. |
| random_triple_regrouping | available_sampled_proxy | derived | Random triple regrouping is represented by the sampled non-factorized proxy. |

## Interpretation

Experiment D3 supports row/column role separation for the available
pre-event artifact classes. It does not establish direct column-H
spark gating, event-capable transpose-specific refinement behavior,
or exhaustive S9 null coverage.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: D3 uses existing A/B pre-event artifact rows. Column evidence is a Lane A derived proxy, direct column-H proxy-branch evidence remains blocked, and transpose-specific event-capable behavior is inconclusive.
