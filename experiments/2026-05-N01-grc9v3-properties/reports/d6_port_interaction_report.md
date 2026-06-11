# D6 Port-Interaction Discriminator Report

Status: complete.

Classification: `supported_for_signed_edge_local_target_with_runtime_abs_control`.

## Scope

D6 runs matched single-port perturbations for all nine canonical ports
`1..9`. All treatments use the same perturbation magnitude and the same
central degree-9 leaf-neighbor shell.

The primary target is a signed edge-local flux surface with a row x
column checkerboard sign pattern. The runtime absolute-flux target is
reported as a control, because it does not require interaction in this
fixture.

## Primary Signed Edge-Local Target

| Model | R2 | SSE | Improvement Over Additive |
| --- | --- | --- | --- |
| intercept_only | 0.000000 | 0.800000 | -0.200000 |
| row_only | 0.100000 | 0.720000 | -0.100000 |
| column_only | 0.100000 | 0.720000 | -0.100000 |
| row_plus_column_additive | 0.200000 | 0.640000 | 0.000000 |
| row_x_column_interaction | 1.000000 | 0.000000 | 0.800000 |
| port_level | 1.000000 | 0.000000 | 0.800000 |
| random_triple_group_mean | 0.100000 | 0.720000 | -0.100000 |

## Runtime Absolute-Flux Control

| Model | R2 | SSE | Improvement Over Additive |
| --- | --- | --- | --- |
| intercept_only | 0.000000 | 0.000010 | -1.000000 |
| row_only | 1.000000 | 0.000000 | 0.000000 |
| column_only | 0.000000 | 0.000010 | -1.000000 |
| row_plus_column_additive | 1.000000 | 0.000000 | 0.000000 |
| row_x_column_interaction | 1.000000 | 0.000000 | 0.000000 |
| port_level | 1.000000 | 0.000000 | 0.000000 |
| random_triple_group_mean | 0.000000 | 0.000010 | -1.000000 |

## Findings

- canonical ports tested: `[1, 2, 3, 4, 5, 6, 7, 8, 9]`
- matched perturbation magnitude: `True`
- neighbor shell equal: `True`
- primary additive R2: `0.19999999999999996`
- primary interaction R2: `1.0`
- primary port-level R2: `1.0`
- runtime absolute-flux additive R2: `1.0`
- runtime absolute-flux interaction required: `False`

## Interpretation

D6 supports the claim that at least one edge-local port surface
requires row x column interaction or port-level features: the primary
signed edge-local target is not fit by additive row+column summaries,
while the interaction and port-level models fit exactly.

The runtime absolute-flux control is not a positive interaction
witness in this matched fixture, so D6 should not be read as saying
all runtime edge-local responses require interaction.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: D6 supports interaction need for the signed edge-local target. The runtime absolute-flux transport control does not require an interaction term in this matched fixture.
