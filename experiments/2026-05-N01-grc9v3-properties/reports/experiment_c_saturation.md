# Experiment C Saturation And Near-Saturation

Status: complete.

## Scope

This report tests whether canonical Lane A saturation behaves as a
meaningful refinement gate under `current_hybrid_signed_hessian`.

The Lane A candidate predicate is active-degree saturation plus basin
interior evidence plus signed-Hessian degeneracy. Direct column-H and
near-saturation policies are not claimed.

## Outputs

- `../outputs/experiment_c_saturation_rows.csv`
- `../outputs/experiment_c_saturation_summary.json`
- `../outputs/experiment_c_saturation_manifest.json`
- `../reports/experiment_c_saturation_blocked_observations.csv`

## Canonical Gate

- formula: `active_degree == 9 AND gradient_norm < eps_gradient AND min_signed_hessian < eps_spark`
- near-saturation policy: `not_implemented_in_lane_a`
- derived column diagnostic role: `reported separately; not gate evidence`
- budget tolerance: `1e-12`

## Identity Transform Rows

| Condition | Degree | Saturation | Basin Interior | Degeneracy | Candidates | Refinements | Budget Error |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: |
| C1_degree_7_stressed | 7 | `false` | `true` | `true` | 0 | 0 |  |
| C2_degree_8_stressed | 8 | `false` | `true` | `true` | 0 | 0 |  |
| C3_degree_9_stressed | 9 | `true` | `true` | `true` | 1 | 1 | 0.0 |
| C5_degree_9_stable_hessian | 9 | `true` | `true` | `false` | 0 | 0 |  |

## Controls Summary

- central instability matched for stressed degree 7/8/9: `true`
- degree 7 or 8 stressed non-trigger: `true`
- degree 9 stressed candidate: `true`
- degree 9 stressed refines: `true`
- degree 9 without instability non-trigger: `true`
- candidate detection matches formula for all rows: `true`
- budget evidence available for canonical positive: `true`
- canonical positive budget within tolerance: `true`
- canonical positive candidate payload available: `true`
- canonical positive expansion payload available: `true`
- canonical positive reassignment map available: `true`
- canonical positive budget evidence source: `hybrid_mechanical_expansion.payload`

## Transform Invariance

| Condition | Candidate/refinement counts invariant across transforms |
| --- | --- |
| C1_degree_7_stressed | `true` |
| C2_degree_8_stressed | `true` |
| C3_degree_9_stressed | `true` |
| C5_degree_9_stable_hessian | `true` |

This invariance is expected for the Lane A gate because the predicate
depends on active degree, basin-interior evidence, and signed-Hessian
degeneracy. It supports capacity plus signed-Hessian bottleneck
behavior, not direct row/column semantic separation.

## Interpretation

Experiment C supports the Lane A representational-bottleneck claim.
Under the current `current_hybrid_signed_hessian` gate, active-degree
7 and active-degree 8 stressed fixtures do not produce spark candidates
or refinement events, even when matched to the central signed-Hessian
stress of the positive degree-9 fixture.

The active-degree 9 stressed fixture produces one spark candidate and
one mechanical expansion with budget evidence. The active-degree 9
stable-Hessian control does not trigger merely because all ports are
occupied. Therefore, under Lane A, fullness alone is insufficient,
signed-Hessian stress alone is insufficient when unsaturated, and the
positive event requires the combination of full nine-port occupancy
and signed-Hessian degeneracy.

Near-saturation remains blocked under Lane A because no active-degree-8
policy is implemented. Direct column-H gate evidence remains blocked
under Lane A. The observed expansion is event-level mechanical evidence
only; persistent child identity claims are deferred to Experiment D.
