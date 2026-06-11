# Experiment E Coarse-Graining And Split Reconstruction

Status: complete.

## Scope

This report tests GRC9V3 public column `G/Split` operators for eligible
port-attached fields under the Lane A baseline.

This is a reconstruction test. Semantic grouping comparison against rows
or random triples is deferred to D7.

## Outputs

- `../outputs/experiment_e_coarse_graining_split_errors.csv`
- `../outputs/experiment_e_coarse_graining_split_summary.json`
- `../outputs/experiment_e_coarse_graining_split_manifest.json`
- `../reports/experiment_e_coarse_graining_split_blocked_observations.csv`

## Reconstruction Results

| Field | Class | Mode | Max Abs Error | Eligible |
| --- | --- | --- | ---: | --- |
| conductance | nonnegative | exact_column_profile | 1.11022302463e-16 | `true` |
| geometric_length | nonnegative | exact_column_profile | 0 | `true` |
| temporal_delay | nonnegative | exact_column_profile | 0 | `true` |
| flux_coupling | nonnegative | exact_column_profile | 0 | `true` |
| abs_flux | nonnegative | exact_column_profile | 0 | `true` |
| signed_flux | signed_flux_j_plus_j_minus | signed_flux_split | 0 | `true` |
| signed_flux_compressed_total | compressed_signed_flux_lossy_control | compressed_signed_column_total_uniform_split | 2.08333333333 | `false` |

## Controls

- all eligible fields near exact: `true`
- reconstruction tolerance: `1e-12`
- max exact reconstruction error: `1.11022302463e-16`
- zero-column controls pass: `true`
- single-active-port-in-column controls pass: `true`
- J+/J- signed flux available: `true`
- compressed signed-flux lossy control error: `2.08333333333`
- signed flux orientation: `GRC9V3._build_signed_flux_port_field uses local oriented flux: PortEdge.flux_uv at node_u and -flux_uv at node_v`
- J+/J- formula: `J = Split(G(J+)) - Split(G(J-))`
- compressed signed formula: `sum signed flux per column, then uniformly split the signed total across the three ports in that column`

## Interpretation

Experiment E supports the exact reconstruction part of the GRC9 column
multiscale claim for eligible nonnegative port-attached fields. Signed
flux reconstructs exactly when represented through separate `J+` and
`J-` channels.

The compressed signed-flux control is explicitly lossy in the mixed-sign
column fixture. That distinguishes exact signed reconstruction through
positive/negative decomposition from lossy signed-total compression.
