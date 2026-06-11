# D1 Factorization Discriminator

Status: complete.

## Scope

D1 reuses completed O-style outputs to test whether structured
row/column transforms preserve semantic artifacts better than a
non-factorized S9 relabel. It does not add runtime behavior.

This run is based on the shared Iteration 1 discriminator harness
`outputs/discriminator_harness_schema.json`.

Lane A saturation and mechanical refinement convention artifacts are
reported separately from factorization-sensitive row/column artifacts.

## Semantic Error Metric

`semantic_error = 0.0` means the transformed artifact preserves the
expected row/column semantic class for the relevant structured transform
or control.

`semantic_error = 1.0` means the transformed or regrouped artifact no
longer preserves the expected predefined row/column semantic class.

The S9/random-triple control is a sampled non-factorized proxy generated
from the deterministic degree-preserving random relabel in the shared
fixture harness. It is not an exhaustive statement over all `9!`
relabelings.

## Result

- classification: `supported_with_lane_a_boundaries`
- structured factorization mean semantic error: `0`
- S9/random-triple-proxy mean semantic error: `1`
- S9 error exceeds structured error: `true`

## Equivariance Matrix

| Regime | Artifact | Transform | Evidence | Mean Semantic Error | Match Rate |
| --- | --- | --- | --- | ---: | ---: |
| core_loop_factorization | derived_column_cancellation_proxy | column_permutation_312 | derived | 0 | 1 |
| core_loop_factorization | derived_column_cancellation_proxy | degree_preserving_random_relabel | derived | 1 | 0 |
| core_loop_factorization | derived_column_cancellation_proxy | identity | derived | 0 | 1 |
| core_loop_factorization | derived_column_cancellation_proxy | row_column_transpose | derived | 1 | 0 |
| core_loop_factorization | derived_column_cancellation_proxy | row_permutation_231 | derived | 0 | 1 |
| core_loop_factorization | row_differential_signature | column_permutation_312 | derived | 0 | 1 |
| core_loop_factorization | row_differential_signature | degree_preserving_random_relabel | derived | 1 | 0 |
| core_loop_factorization | row_differential_signature | identity | derived | 0 | 1 |
| core_loop_factorization | row_differential_signature | row_column_transpose | derived | 1 | 0 |
| core_loop_factorization | row_differential_signature | row_permutation_231 | derived | 0 | 1 |
| lane_a_spark_capacity | lane_a_saturation_gate | column_permutation_312 | direct | 0 | 1 |
| lane_a_spark_capacity | lane_a_saturation_gate | degree_preserving_random_relabel | direct | 0 | 1 |
| lane_a_spark_capacity | lane_a_saturation_gate | identity | direct | 0 | 1 |
| lane_a_spark_capacity | lane_a_saturation_gate | row_column_transpose | direct | 0 | 1 |
| lane_a_spark_capacity | lane_a_saturation_gate | row_permutation_231 | direct | 0 | 1 |
| mechanical_refinement_convention | post_refinement_column_mapping | column_permutation_312 | direct | 0 | 1 |
| mechanical_refinement_convention | post_refinement_column_mapping | degree_preserving_random_relabel | partial | 1 | 1 |
| mechanical_refinement_convention | post_refinement_column_mapping | identity | direct | 0 | 1 |
| mechanical_refinement_convention | post_refinement_column_mapping | row_column_transpose | partial | 1 | 1 |
| mechanical_refinement_convention | post_refinement_column_mapping | row_permutation_231 | direct | 0 | 1 |

## Interpretation

D1 supports the factorization claim for row/column-sensitive artifacts:
structured row and column transforms preserve the expected row and
derived-column signatures, while the non-factorized S9 relabel has
higher semantic error.

The Lane A saturation gate is direct runtime evidence but is expected to
be invariant under row/column and S9 relabels, so it is not counted as
factorization evidence.

Post-refinement column preservation is direct mechanical evidence. It is
reported separately because current-port column preservation does not
by itself establish semantic equivalence under non-factorized S9
relabeling.

## Evidence Labels

- row differential signature: derived from Experiment A artifacts
- column cancellation proxy: derived under Lane A from Experiment B
- Lane A saturation gate: direct candidate/event evidence from Experiment C
- post-refinement mapping: direct mechanical mapping, partial as S9 semantic evidence
