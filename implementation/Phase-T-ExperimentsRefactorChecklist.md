# Phase T Telemetry Experiments Refactor Checklist

This document tracks execution of the telemetry experiment refactor.

It is intentionally separate from:

- [Phase-T-ImplementationChecklist.md](./Phase-T-ImplementationChecklist.md)

because the Phase T checklist already established:

- the telemetry contract,
- the representative experiment surface,
- the landscape experiment surface,
- and the first trace/report/checkpoint artifacts

This checklist starts after that proof.

Its purpose is not to add new telemetry content.
Its purpose is to refactor the experiment surface so Phase T can keep growing
without structural drift.

It is defined by:

- [Phase-T-ExperimentsRefactorPlan.md](./Phase-T-ExperimentsRefactorPlan.md)

## Usage Rules

- Preserve public behavior first; change internal structure before public API.
- Treat `src/pygrc/telemetry/experiments.py` as the public facade during the
  first refactor stages.
- Keep script entrypoints working throughout the refactor.
- Refactor tests alongside source code rather than leaving one monolith behind.
- If a staged extraction cannot be made behaviorally safe, record the blocking
  coupling explicitly before changing direction.
- Do not change telemetry payload meaning, checkpoint semantics, or script
  parameter meaning as part of a structural-only iteration.
- Do not change defaults, trace field names, or diagnostic labels merely to make
  a refactor easier.
- If any such change becomes necessary, record it as content-facing follow-on
  work rather than silently folding it into the refactor.
- Preserve the current structure of public result dataclasses until a later
  public-surface review explicitly reopens them.

## Iteration Template

Copy this section for each new iteration.

```markdown
## Iteration N. <Short Name>

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>
- [ ] <Concrete task 3>
- [ ] <State which public/runtime/artifact boundaries must remain unchanged>

### Implementation Notes

- <Important implementation detail, decision, or constraint>
- <List any invariants explicitly preserved during this iteration>

### Verification

- [ ] <Import / test / review check>
- [ ] <Boundary / acceptance check>
- [ ] <Parity check for unchanged payload/CLI/checkpoint behavior>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Checklist Bootstrap

### Goal

Create the dedicated refactor plan/checklist pair and record the first
execution order so the refactor does not drift.

### Checks

- [x] Create `Phase-T-ExperimentsRefactorPlan.md`
- [x] Create `Phase-T-ExperimentsRefactorChecklist.md`
- [x] Record the structural problem statement for:
  - `src/pygrc/telemetry/experiments.py`
  - `tests/telemetry/test_experiments.py`
- [x] Record the first execution priority as:
  - shared lane runner extraction
  - plus checkpoint config consolidation
- [x] Record explicit “must not change during refactor” boundaries
- [x] Link the refactor lane from the active implementation docs

### Implementation Notes

- This checklist is structural, not phenomenology-facing.
- The first step is intentionally narrow:
  - create the runner/checkpoint seam first
  - only then broaden into module splits
- `experiments.py` should remain the public facade during the early iterations.
- The refactor boundary is now also explicit:
  - no telemetry meaning changes
  - no checkpoint semantic changes
  - no script-contract changes
  - no silent diagnostic/content reinterpretation

### Verification

- [x] The plan/checklist pair exists under `implementation/`
- [x] The first stage is explicitly locked before execution starts
- [x] The preserved-boundary rules are explicit before code changes begin
- [x] The refactor is discoverable from the active Phase T docs

### Summary

Closed. The telemetry experiment refactor now has a dedicated execution lane,
separate from Phase T feature/content work. The first implementation slice is
explicitly fixed as shared `GRCV3` lane-runner extraction plus checkpoint
config consolidation.

## Iteration 1. Shared Lane Runner And Checkpoint Config

### Goal

Extract the duplicated representative/landscape `GRCV3` execution loop behind a
single internal lane runner and checkpoint config object.

### Checks

- [x] Introduce an internal checkpoint config dataclass for the current
  checkpoint parameter cluster
- [x] Extract a shared internal lane runner used by both:
  - representative `GRCV3` execution
  - landscape `GRCV3` execution
- [x] Use a factory/callback pattern so the shared runner can accept the known
  execution differences in:
  - model bootstrapping
  - initial observables
  - step-result sourcing
  - optional transient landscape observability
- [x] Reduce the existing representative/landscape wrappers to thin
  bootstrapping and result-assembly code
- [x] Keep current public function signatures working during the extraction
- [x] Keep current checkpoint recording semantics and artifact indexing behavior
  unchanged
- [x] Keep current representative/landscape result payload shapes unchanged
- [x] Keep the current public result dataclass structures unchanged

### Implementation Notes

- This is the highest-value first seam because it removes duplicated
  behaviorally critical code.
- The goal is not yet public API cleanup.
- If hidden semantic differences block extraction, they must be written down
  explicitly before broadening the refactor.
- The internal checkpoint config should cover the current six-field cluster:
  - `record_graph_checkpoints`
  - `checkpoint_every_step`
  - `checkpoint_every_n_steps`
  - `checkpoint_storage_mode`
  - `checkpoint_chunk_size`
  - `include_flow_overlays`
- Default-resolution logic that is currently scattered inline should be absorbed
  into the config object through `__post_init__` or a dedicated factory helper.
- This iteration is structural only:
  - no checkpoint behavior change
  - no payload-shape change
  - no script-interface change
- Implemented the shared seam in:
  - `src/pygrc/telemetry/_grcv3_lane_runner.py`
- Added:
  - `GRCV3CheckpointConfig`
  - `GRCV3LaneRunArtifacts`
  - `run_grcv3_lane_with_telemetry(...)`
- `GRCV3CheckpointConfig.__post_init__` now owns the previous inline storage-mode
  default:
  - `jsonl_chunks` when `checkpoint_every_step = true`
  - `per_checkpoint_files` otherwise
- The shared runner now owns the previously duplicated logic for:
  - basin/identity rebuilds
  - initial/final observable capture
  - per-step family extension collection
  - per-step event extension collection
  - checkpoint cadence decisions
  - checkpoint export and streamed chunk writing
  - graph checkpoint index assembly
- The callback seam is now explicit:
  - representative runs use a direct step-extension callback
  - landscape runs use a callback that builds transient landscape observability
    per replay step
- Follow-up cleanup after review:
  - the shared runner no longer hardcodes `rebuild_basin_attributes()` /
    `rebuild_identity_state()`
  - those rebuilds now come from an explicit caller-supplied
    `pre_step_setup` hook
  - the step-extension callback was simplified from
    `Callable[[GRCV3, StepResult], ...]` to `Callable[[GRCV3], ...]`
    because the shared runner does not need to force an unused `StepResult`
    parameter on landscape callbacks
- `run_grcv3_representative_experiment(...)` and
  `run_grcv3_landscape_experiment(...)` now construct one internal
  `GRCV3CheckpointConfig` each and pass it down unchanged.
- The public result dataclasses remain structurally unchanged:
  - `GRCV3RepresentativeRunResult`
  - `GRCV3RepresentativeExperimentResult`
  - `GRCV3LandscapeExperimentResult`

### Verification

- [x] The duplicated loop/checkpoint logic is materially reduced
- [x] The affected representative/landscape tests pass
- [x] The relevant scripts still run without interface changes
- [x] Representative/landscape artifact parity is preserved for checkpoint
  indexing and summary structure

Verification commands:

- `python -m py_compile src/pygrc/telemetry/experiments.py src/pygrc/telemetry/_grcv3_lane_runner.py`
- `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_representative_experiment_emits_artifacts_and_replay_stable_reports tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_representative_experiment_can_emit_checkpoint_artifacts tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_landscape_experiment_emits_artifacts_and_reports tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_landscape_experiment_can_emit_checkpoint_artifacts tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_landscape_script_can_emit_checkpoint_artifacts`

Observed result:

- `Ran 5 tests in 2.439s`
- `OK`

### Summary

Closed. Iteration 1 extracted the duplicated `GRCV3` representative/landscape
step-loop and checkpoint logic into a shared private runner without changing the
public experiment signatures, public result dataclass shapes, checkpoint
semantics, or script behavior. The shared runner now provides the execution seam
needed for later extension-builder and trace-family extraction work.

## Iteration 2. GRCV3 Extension Builder Extraction

### Goal

Move the `GRCV3` telemetry extension-building cluster behind a private helper
module.

### Checks

- [x] Extract the step/run-summary extension builders into a private telemetry
  module
- [x] Keep the same emitted payload shapes
- [x] Keep `experiments.py` as the public orchestration facade
- [x] Keep contract definitions separate from builder implementation logic
- [x] Move extension-builder-local helper utilities with the builder cluster
  rather than leaving them stranded in `experiments.py`
- [x] Record that landscape-specific monitoring/state coupling inside the
  extension builders remains acceptable in this layer

### Implementation Notes

- This stage should follow the shared runner extraction, not precede it.
- The contract module should remain declarative rather than absorbing builder
  code.
- Helpers that are only extension-builder concerns should move together with the
  builder module, including signed-Hessian/vector utilities,
  observed-interior-site builders, and monitoring-context helpers.
- Landscape-specific access such as cached node-id lookups is acceptable here
  because this module still belongs to telemetry extension construction, not to
  the shared runtime core.
- Extracted the builder cluster into:
  - `src/pygrc/telemetry/_grcv3_extensions.py`
- Moved the following cohesive builder/monitoring surface into that private
  module:
  - `_build_grcv3_backend_summary`
  - `_build_grcv3_step_extension`
  - `_build_grcv3_run_summary_extension`
  - `_build_grcv3_signed_hessian`
  - `_build_grcv3_basin_summary`
  - `_build_grcv3_spark_state`
  - `_build_grcv3_hierarchy_state`
  - `_build_grcv3_choice_state`
  - `_build_grcv3_lifecycle_event_counts`
  - `_build_grcv3_observed_interior_site`
  - `_build_grcv3_landscape_step_observability`
  - `_build_grcv3_landscape_run_summary`
  - plus their local monitoring/eigenvalue helpers
- `experiments.py` now re-imports those private names from
  `_grcv3_extensions.py`, so:
  - the public facade remains unchanged
  - existing private test hooks in `tests/telemetry/test_experiments.py` still
    resolve the same names from `telemetry.experiments`
- `grcv3_contract.py` remained declarative; only builder implementation moved.
- Landscape-specific coupling remains intentionally inside the extension module:
  - cached runtime assembly summaries
  - monitored primitive/node mapping
  - transient landscape observability
  These remain telemetry-extension concerns rather than shared runner concerns.

### Verification

- [x] The affected telemetry tests pass
- [x] No public trace/result payload changes are introduced accidentally

Verification commands:

- `python -m py_compile src/pygrc/telemetry/experiments.py src/pygrc/telemetry/_grcv3_extensions.py src/pygrc/telemetry/_grcv3_lane_runner.py`
- `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_basin_summary_does_not_fallback_to_node_count tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_rich_v4_probe_transient_observability_is_emitted tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_representative_experiment_emits_artifacts_and_replay_stable_reports tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_representative_experiment_can_emit_checkpoint_artifacts tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_landscape_experiment_emits_artifacts_and_reports tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_run_grcv3_landscape_experiment_can_emit_checkpoint_artifacts tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_landscape_script_can_emit_checkpoint_artifacts`

Observed result:

- `Ran 7 tests in 15.900s`
- `OK`

### Summary

Closed. Iteration 2 extracted the `GRCV3` extension-builder and
transient-landscape summary cluster into a private `_grcv3_extensions.py`
module while keeping `experiments.py` as the public facade. The contract module
remains declarative, landscape-specific monitoring/state coupling stayed inside
the extension layer where it belongs, and the focused extension plus
representative/landscape parity checks passed unchanged.

## Iteration 3. Trace Family Module Partition

### Goal

Split private trace/diagnostic families into concern-based modules behind the
same public facade.

### Checks

- [x] Group failure/candidate traces together
- [x] Group settlement/reentry traces together
- [x] Group collapse traces together
- [x] Keep existing public trace entry points in `experiments.py`
- [x] Move `_build_grcv3_failure_trace_*` and related `_diagnose_*` families
  with the failure/candidate trace module rather than leaving them in the
  facade
- [x] Give the shared settlement/reentry/collapse helpers an explicit home,
  preferably a private trace-utils module

### Implementation Notes

- This iteration should not redesign trace semantics.
- The goal is navigable internal ownership, not new trace content.
- The likely shared trace-utils surface includes helpers for realized-key lookup,
  snapshot-cache maintenance, event-anchor/locus summaries, and split-descendant
  collection.
- Those helpers should not remain opportunistically interleaved between family
  modules after the split.
- Extracted the shared trace/helper surface into:
  - `src/pygrc/telemetry/_telemetry_utils.py`
  - `src/pygrc/telemetry/_grcv3_trace_utils.py`
- Extracted concern-shaped trace families into:
  - `src/pygrc/telemetry/_grcv3_failure_traces.py`
  - `src/pygrc/telemetry/_grcv3_settlement_traces.py`
  - `src/pygrc/telemetry/_grcv3_collapse_traces.py`
- Moved the failure/candidate/settlement-locus family into
  `_grcv3_failure_traces.py`, including the `_build_grcv3_failure_trace_*`
  helpers, candidate blocker diagnosis, and settlement-locus trace builder.
- Moved the settlement/reentry family into `_grcv3_settlement_traces.py`,
  including the reentry boundary, neighborhood, support-isolation,
  counterfactual, and secondary-support authorability surface.
- Moved the collapse family into `_grcv3_collapse_traces.py`, including the
  narrow lane trace, broad survey, pre-spark decomposition, post-spark
  boundary/late-window/authorability passes, geometry-exclusion pass, and the
  spindle-lane collapse regime trace.
- `experiments.py` now acts as a public/default-bearing facade for these trace
  entry points instead of owning the private trace implementations directly.
- Shared helpers no longer remain interleaved between family regions in the
  facade:
  - generic recursive normalization now lives in `_telemetry_utils.py`
  - shared `GRCV3` trace helpers now live in `_grcv3_trace_utils.py`
  - public trace defaults, names, and call signatures remain in
    `experiments.py`
- Follow-up full-suite verification surfaced two real extraction regressions
  outside the narrow initial trace batch and they were corrected in-place:
  - restored representative/test-hook imports still intentionally exposed
    through `experiments.py`
  - widened `_to_plain_data(...)` back to generic `Mapping` handling so replay
    config reconstruction still normalizes `mappingproxy` values correctly

### Verification

- [x] The affected trace tests pass
- [x] The public import surface still works

Verification commands:

- `./.venv/bin/python -m py_compile src/pygrc/telemetry/experiments.py src/pygrc/telemetry/_telemetry_utils.py src/pygrc/telemetry/_grcv3_trace_utils.py src/pygrc/telemetry/_grcv3_failure_traces.py src/pygrc/telemetry/_grcv3_settlement_traces.py src/pygrc/telemetry/_grcv3_collapse_traces.py`
- `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_rich_v4_path_failure_trace_identifies_geometry_failure tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_rich_v4_post_split_reentry_trace_isolates_child_settlement_block tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_rich_v4_secondary_support_authorability_trace_shows_existing_structure_is_sufficient tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_rich_v4_collapse_regime_trace_shows_path_specific_support_to_carrier_collapse tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_post_collapse_geometry_exclusion_shows_sink_reroute_is_geometry_mediated tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_path_failure_trace_script_emits_trace tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_settlement_reentry_trace_script_emits_trace tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_collapse_regime_trace_script_emits_trace tests.telemetry.test_experiments.TelemetryRepresentativeExperimentTest.test_grcv3_post_collapse_geometry_exclusion_trace_script_emits_trace`

Observed result:

- `Ran 9 tests in 124.521s`
- `OK`

Follow-up full-file validation:

- `rg -n "^    def test_" tests/telemetry/test_experiments.py | wc -l`
  confirmed `64` test methods in the file.
- The remaining `55` methods were then executed in fail-fast `8`-test batches,
  skipping only the `9` methods already passed in the current refactor state.
- After the two extraction regressions above were fixed, the remaining coverage
  completed cleanly:
  - batch 1 rerun: `Ran 8 tests in 14.727s` / `OK`
  - batches 2-6: `Ran 8 tests` / `OK`
  - batch 7: `Ran 7 tests in 164.669s` / `OK`

Net verification state:

- `64 / 64` `tests/telemetry/test_experiments.py` methods now pass in the
  current Iteration 3 refactor state.

### Summary

Closed. Iteration 3 extracted the private trace families out of
`src/pygrc/telemetry/experiments.py` into concern-based private modules while
keeping the public/default-bearing trace entry points in the facade. Shared
trace utilities now have an explicit private home, failure/candidate,
settlement/reentry, and collapse code each have a navigable ownership boundary,
the follow-up extraction regressions were corrected, and the full
`test_experiments.py` surface now passes without changing trace semantics or
public call shapes.

## Iteration 4A. Test Inventory And Relocation Baseline

### Goal

Establish the no-drift baseline and relocate the monolithic experiment tests
into concern-shaped files/classes without changing their semantic scope.

### Checks

- [x] Split `tests/telemetry/test_experiments.py` into concern-based modules or
  equivalently separated classes/helpers
- [x] Record a pre-split inventory of current discovered `test_*` ids and use
  it as the migration baseline
- [x] Maintain an explicit one-to-one migration map from old test ids to new
  destinations, or document any intentional one-to-many replacement
- [x] Keep test ownership aligned with the new source module boundaries
- [x] Keep first-pass test bodies and assertions semantically unchanged while
  relocating them into new modules/classes
- [x] Preserve public experiment/trace entry-point coverage, not just raw test
  count parity
- [x] Prove post-split test discovery parity against the pre-split inventory
  before deleting the old monolithic file

### Implementation Notes

- The first move is relocation, not redesign:
  - move tests with the same names, inputs, and assertions first
  - do not centralize helpers or parameterize repeated patterns in the same
    step
- Pre/post migration review should answer three explicit parity questions:
  - are the discovered test ids the same set as before, or explicitly mapped
    replacements
  - do the moved tests still exercise the same public telemetry entry points
  - were any assertions, fixture values, or expected labels changed during the
    relocation step
- If one old test is replaced by multiple new tests, record that replacement
  map explicitly rather than allowing silent scope drift.

### Verification

- [x] The experiments test surface remains green after the split
- [x] No single test class remains responsible for the whole experiment surface
- [x] Pre-split and post-split discovered test inventories match, or every
  difference has an explicit migration note
- [x] Public entry-point-to-test coverage is preserved across the split

### Summary

Closed. Iteration 4A took the lowest-risk relocation path: instead of mixing
file splitting with helper cleanup, it repartitioned
`tests/telemetry/test_experiments.py` into six concern-shaped classes while
keeping method names, bodies, assertions, and public entry-point calls intact.

The recorded baseline and migration map are in
`implementation/Phase-T-ExperimentsRefactor-Iteration4A-TestInventory.md`.
Pre-split discovery found `64` ids, all under
`test_experiments.TelemetryRepresentativeExperimentTest.*`. Post-split
discovery still found `64` ids, now distributed across:

- `TelemetryRepresentativeExperimentTest`
- `TelemetryFailureTraceTest`
- `TelemetrySettlementTraceTest`
- `TelemetryCollapseTraceTest`
- `TelemetryLandscapeExperimentTest`
- `TelemetryScriptTest`

This preserved the public telemetry coverage surface while removing the single
owner-class bottleneck and leaving shared loader/fixture consolidation for
Iteration 4B.

Verification:

- discovery parity: `64 -> 64`
- full run:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
  - `Ran 64 tests in 602.593s`
  - `OK`

## Iteration 4B. Shared Loader And Fixture Consolidation

### Goal

Reduce repeated helper/setup structure in the split test surface without
changing test semantics or coverage shape.

### Checks

- [x] Centralize repeated script loader helpers
- [x] Give the top-of-file script/seed constant blocks an explicit shared home
  or move them next to the concern-shaped test modules that use them
- [x] Introduce shared fixtures/helpers only where they preserve the same test
  names, inputs, and assertions
- [x] Keep discovery parity and public entry-point coverage unchanged after the
  helper consolidation

### Implementation Notes

- This is still structural-only work.
- Helper reuse should not silently merge or drop test coverage.
- If a helper change affects more than one concern-shaped test module, record
  the preserved boundaries explicitly.

### Verification

- [x] The experiments test surface remains green after helper consolidation
- [x] Test discovery parity is unchanged from Iteration 4A
- [x] Public entry-point-to-test coverage is still preserved

### Summary

Closed. Iteration 4B extracted the shared top-of-file support block from
`tests/telemetry/test_experiments.py` into the private helper module
`tests/telemetry/_experiments_test_support.py`.

That helper now owns:

- shared script path constants
- shared seed constants
- the generic `_load_script_module(...)` loader
- the current named `_load_grcv3_*_script_module()` wrappers

`test_experiments.py` continues to own the discovered test surface and still
uses the same test method names, bodies, assertions, and concern-shaped
classes established in Iteration 4A. This keeps helper reuse structurally
separate from the later Iteration 4C deduplication work.

The detailed helper-boundary record is in
`implementation/Phase-T-ExperimentsRefactor-Iteration4B-HelperLayout.md`.

Verification:

- discovery parity unchanged from Iteration 4A: `64`
- syntax/import check:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m py_compile tests/telemetry/test_experiments.py tests/telemetry/_experiments_test_support.py`
- full run:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
  - `Ran 64 tests in 597.778s`
  - `OK`

## Iteration 4C. Script Test Deduplication

### Goal

Deduplicate the repeated script validation/emission patterns only after
relocation parity is already proven.

### Checks

- [x] Replace repeated script validation/emission patterns with shared helpers
  or `subTest`-style structure
- [x] Replace the repeated trace-script pairs with a shared table-driven pattern
  rather than keeping one bespoke method pair per script
- [x] Keep the same script coverage and expected payload/validation assertions
- [x] Keep discovery parity and public entry-point coverage explicit after the
  deduplication pass

### Implementation Notes

- This is the first Iteration 4 slice allowed to change internal test
  structure materially.
- Do not combine this with additional source refactors.
- Any one-to-many or many-to-one test replacement must be documented against
  the Iteration 4A inventory map.

### Verification

- [x] The experiments test surface remains green after script-test
  deduplication
- [x] Test discovery parity is unchanged from Iteration 4A, or every
  difference has an explicit migration note
- [x] Public entry-point-to-test coverage is still preserved

### Summary

Closed. Iteration 4C replaced the repeated bespoke script test methods in
`TelemetryScriptTest` with shared helper methods plus generated methods driven
by `_SCRIPT_REJECT_SPECS` and `_SCRIPT_EMIT_SPECS`.

This materially changed internal test structure while preserving the Iteration
4A discovery surface. The same `TelemetryScriptTest.test_*` ids remain
discoverable, but they are now attached from a shared spec-table pattern
instead of being written out one-by-one.

The detailed record is in
`implementation/Phase-T-ExperimentsRefactor-Iteration4C-ScriptDedup.md`.

Verification:

- discovery parity unchanged from Iteration 4A / 4B: `64`
- syntax/import check:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m py_compile tests/telemetry/test_experiments.py`
- targeted regression rerun:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryScriptTest.test_grcv3_landscape_script_can_emit_checkpoint_artifacts`
  - `Ran 1 test in 0.636s`
  - `OK`
- full run:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
  - `Ran 64 tests in 595.451s`
  - `OK`

## Iteration 5. Public Surface Cleanup Review

### Goal

Review which exports, defaults, helpers, and result types should remain public
after the structural split stabilizes.

### Checks

- [x] Review `__all__` for accidental public constants
- [x] Decide whether result types should move to a dedicated module
- [x] Decide whether additional public config dataclasses are justified
- [x] Review whether `DEFAULT_*` constants should remain in `experiments.py`,
  move to a dedicated config module, or remain re-exported for compatibility
- [x] Record any remaining structural debt explicitly

### Implementation Notes

- This is intentionally last.
- Do not broaden this into a public API redesign unless the internal structure
  is already stable.

### Verification

- [x] Public exports are deliberate and documented
- [x] Remaining cleanup is recorded explicitly if deferred

### Summary

Closed. Iteration 5 made the experiments surface deliberate without shrinking
compatibility.

Code changes:

- moved experiment defaults to `src/pygrc/telemetry/_experiment_defaults.py`
- moved result dataclasses to `src/pygrc/telemetry/_experiment_results.py`
- kept `src/pygrc/telemetry/experiments.py` as the compatibility-bearing facade
  by re-exporting those names
- expanded `experiments.py` `__all__` so it now matches the intended public
  module surface instead of a stale partial subset

Design decisions:

- additional public config dataclasses are deferred
- package-root default-surface shrink is deferred
- direct private-helper imports in `scripts/run_grcv3_rich_fulltest.py` remain
  recorded as structural debt
- residual non-blocking observations about facade size, the settlement trace
  cluster, test support module size, `_to_plain_data(...)`, and
  `GRCV3CheckpointConfig` readability are recorded in the Iteration 5 review
  note rather than promoted to new work

The detailed record is in
`implementation/Phase-T-ExperimentsRefactor-Iteration5-SurfaceReview.md`.

Verification:

- `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m py_compile src/pygrc/telemetry/__init__.py src/pygrc/telemetry/experiments.py src/pygrc/telemetry/_experiment_defaults.py src/pygrc/telemetry/_experiment_results.py`
- public-name spot check for both `pygrc.telemetry` and
  `pygrc.telemetry.experiments`
- full run:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
  - `Ran 64 tests in 595.318s`
  - `OK`
