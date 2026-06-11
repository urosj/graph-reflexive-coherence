# Experiment D Refinement And Child Identity

Status: complete.

## Scope

This report tests whether mechanical refinement preserves column interface
structure and whether child identity support is backed by post-event
sink/basin persistence artifacts under Lane A.

Mechanical refinement is reported separately from identity support.
The identity-side claim is configured-window child-basin persistence,
not identity fission from expansion alone.

## Outputs

- `../outputs/experiment_d_refinement_identity_reassignments.csv`
- `../outputs/experiment_d_refinement_identity_persistence.csv`
- `../outputs/experiment_d_refinement_identity_thresholds.csv`
- `../outputs/experiment_d_refinement_identity_conditions.csv`
- `../outputs/experiment_d_refinement_identity_summary.json`
- `../outputs/experiment_d_refinement_identity_manifest.json`
- `../reports/experiment_d_refinement_identity_blocked_observations.csv`

## Identity Transform Conditions

| Condition | Refinements | Edge Reassignments | Column Preserved | Budget Error | Persistent Children |
| --- | ---: | ---: | --- | ---: | ---: |
| d_equal_transfer_refinement | 1 | 9 | `true` | 0.0 | 3 |
| d_column_1_skewed_transfer | 1 | 9 | `true` | 0.0 | 3 |
| d_column_2_skewed_transfer | 1 | 9 | `true` | 0.0 | 3 |
| d_column_3_skewed_transfer | 1 | 9 | `true` | 0.0 | 3 |
| d_degree_8_no_refinement_control | 0 | 0 | `false` |  | 0 |

## Summary

- all refinement rows preserve budget: `true`
- all refinement rows preserve columns by reassigned port: `true`
- all refinement rows preserve columns by module location: `true`
- no-refinement controls have no reassignment map: `true`
- configured-window child basin persistence: `true`
- persistence window steps: `3`
- max persistence trace steps: `5`
- minimum basin mass threshold: `1.0`
- snapshot source: `experiment-local runtime state`
- checkpoint-window source: `inconclusive`
- lineage source: `expansion payload + post-event basin assignment`
- budget tolerance: `1e-12`

## Interpretation

Experiment D supports column-preserving mechanical refinement under
the Lane A baseline in clean raw fixtures. Each observed mechanical
expansion exposes a direct
`hybrid_mechanical_expansion.payload.reassignment_map`. All nine old
boundary edges are reassigned, and each old boundary column matches
the new module endpoint column. Unit-measure budget is preserved
within tolerance.

The post-event child sink/basin artifacts persist over the configured
three-step runtime-state window with minimum basin mass `1.0`. This
supports configured-window child-basin persistence in these clean
fixtures.

The result does not show that expansion alone is identity fission,
does not establish landscape-general identity behavior, and does
not yet establish checkpoint-window persistence through persisted
observer records.

## Deferred Unblocking Decisions

The following items are intentionally not unblocked in Iteration 7.1:

- inflow-weighted transfer remains blocked because the current runtime
  exposes equal/custom expansion distribution weights, not an
  inflow-weighted transfer lane; implementing such a lane belongs to
  repo-level runtime work
- landscape-general child identity remains inconclusive because this
  iteration uses clean raw central-node fixtures, not a landscape/seed
  robustness suite
- direct column-H gating and near-saturation remain blocked under Lane A

The following items are candidates for a small addendum or for D8:

- persisted checkpoint-window identity persistence
- before/after topology-change G/Split reconstruction using the
  refinement fixture produced here
