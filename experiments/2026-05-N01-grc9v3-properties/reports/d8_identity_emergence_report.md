# D8 Identity-Emergence Discriminator Report

Status: complete.

Classification: `configured_window_persistent_child_identity_supported_with_boundaries`.

## Scope

D8 tests the identity guardrail directly: mechanical refinement is
classified separately from candidate or accepted identity emergence.
Accepted identity requires post-event child sink/basin persistence,
lineage, and budget evidence over the configured runtime-state window.

## Acceptance Criteria

- persistence window steps: `3`
- minimum basin mass: `1.0`
- required evidence: refinement event, child present across the window,
  child remains a sink across the window, lineage parent/depth rows, and
  unit budget preservation within tolerance
- mechanical expansion alone is not an identity-emergence claim

## Outcome Counts

- accepted identity window rows: `60`
- accepted identity events: `20`
- classified refinement events: `20`
- multi-child persistence events: `20`
- accepted budget audit pass: `True`
- strict threshold failure rows: `30`

## Sample Accepted Windows

| Condition | Transform | Child | Min Mass | Outcome | Budget Error |
| --- | --- | --- | --- | --- | --- |
| d_equal_transfer_refinement | identity | 411 | 5.999999999998 | persistent_child_identity | 0.0 |
| d_equal_transfer_refinement | identity | 412 | 5.0 | persistent_child_identity | 0.0 |
| d_equal_transfer_refinement | identity | 413 | 5.999999999998 | persistent_child_identity | 0.0 |
| d_equal_transfer_refinement | row_permutation_231 | 411 | 5.999999999998 | persistent_child_identity | 0.0 |
| d_equal_transfer_refinement | row_permutation_231 | 412 | 5.0 | persistent_child_identity | 0.0 |
| d_equal_transfer_refinement | row_permutation_231 | 413 | 5.999999999998 | persistent_child_identity | 0.0 |

## Negative Controls

| Control | Count | Interpretation |
| --- | ---: | --- |
| no_refinement_no_identity | 5 | No accepted identity without refinement or persistent sink/basin support. |
| threshold_sensitivity_rejects_child | 30 | Stricter basin-mass thresholds reject some child claims, so identity support is explicitly thresholded. |

## Outcome Classes

D8 output rows use the configured outcome vocabulary: blocked,
mechanical refinement only, transient child candidate, persistent
child identity, multi-child fission flag, and collapse/reabsorption
status. Available clean-fixture events classify as persistent child
identity under the configured runtime-state window; collapse or
reabsorption is inconclusive because no such event is present.

## Interpretation

D8 supports configured-window child-basin identity persistence in
the clean Experiment D refinement fixtures. The accepted claims are
thresholded and artifact-bound: they require persistent sink/basin
rows and budget evidence. The result does not claim that expansion
alone is identity fission, and it does not establish checkpoint-
window or landscape-general identity behavior.

## Boundaries

- checkpoint-window identity persistence remains inconclusive;
- no mechanical-refinement-only positive control is available in
  the completed clean fixture set;
- collapse/reabsorption is not observed in the current artifacts;
- landscape-general identity emergence remains inconclusive.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: D8 accepts configured-window child identity only when mechanical refinement, persistent post-event sink/basin support, lineage, and budget evidence are all present. It does not infer identity fission from expansion alone.
- negative control rows written: `35`
