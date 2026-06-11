# D7 Multiscale Discriminator Report

Status: complete.

Classification: `reconstruction_supported_semantic_columns_supported_with_boundaries`.

## Scope

D7 separates exact mathematical reconstruction from semantic grouping
usefulness. Experiment E supplies true-column G/Split reconstruction
evidence. D5 supplies interface/refinement rows for true-column versus
row/random grouping comparison.

## Reconstruction

- all eligible fields near exact: `True`
- max exact reconstruction error: `1.1102230246251565e-16`
- signed flux J+/J- available: `True`

## Signed Flux Controls

| Control | Classification | Error | Notes |
| --- | --- | --- | --- |
| signed_flux | exact_j_plus_j_minus | 0.0 | Signed flux reconstructs exactly through J+/J- column split. |
| signed_flux_compressed_total | lossy_compressed_diagnostic | 2.0833333333333335 | Lossy signed compression diagnostic only; not exact reconstruction. |

## Semantic Grouping Comparison

| Target | Grouping | Score | Delta vs True Column | Evidence |
| --- | --- | --- | --- | --- |
| immediate_refinement_endpoint_column | true_column | 1.000000 | 0.000000 | direct |
| immediate_refinement_endpoint_column | true_row | 0.333333 | -0.666667 | derived |
| immediate_refinement_endpoint_column | random_column | 0.222222 | -0.777778 | derived |
| immediate_refinement_endpoint_column | random_triple | 0.222222 | -0.777778 | derived |
| immediate_refinement_endpoint_column | single_nine_port_total | 0.333333 | -0.666667 | partial |
| post_window_persistent_endpoint_column | true_column | 0.888889 | 0.000000 | direct |
| post_window_persistent_endpoint_column | true_row | 0.222222 | -0.666667 | derived |
| post_window_persistent_endpoint_column | random_column | 0.222222 | -0.666667 | derived |
| post_window_persistent_endpoint_column | random_triple | 0.222222 | -0.666667 | derived |
| post_window_persistent_endpoint_column | single_nine_port_total | 0.333333 | -0.555556 | partial |

## Findings

- immediate true-column score: `1.0`
- immediate true-row score: `0.3333333333333333`
- immediate random-triple score: `0.2222222222222222`
- post-window true-column score: `0.8888888888888888`
- post-window true-row score: `0.2222222222222222`
- post-window random-triple score: `0.2222222222222222`
- compressed signed flux lossy error: `2.0833333333333335`

## Interpretation

D7 supports exact true-column G/Split reconstruction for eligible
Experiment E fields and signed flux through J+/J-. It also supports
true-column semantic usefulness for interface/refinement targets:
true columns outperform true rows, sampled random triples, and a
single-total baseline on D5 immediate and post-window targets.

The compressed signed-flux total is reported only as a lossy
diagnostic, not an exact reconstruction path.

## Boundaries

- before/after refinement E-style G/Split checkpoints remain blocked;
- semantic grouping comparison is clean-fixture evidence only;
- D7 does not claim arbitrary rows/random triples cannot be made
  mathematically invertible with their own profiles.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: D7 supports exact true-column G/Split reconstruction for Experiment E fields and true-column semantic usefulness for D5 interface/refinement targets. Before/after refinement E-style G/Split checkpoints remain blocked.
