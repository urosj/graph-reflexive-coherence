# Phase T Implementation Checklist

This document tracks the execution of **Phase T: Telemetry + Post-Processing**.

It is intentionally separate from
[`Phase-T-ImplementationPlan.md`](./Phase-T-ImplementationPlan.md):

- the plan defines scope, workstreams, boundaries, and acceptance criteria,
- this checklist records how the telemetry phase is executed iteration by
  iteration.

Each iteration should contain:

- a bounded implementation slice,
- concrete checkboxes that can be ticked off during execution,
- implementation notes recorded alongside the work,
- verification steps tied to the iteration output,
- and a short summary when the iteration closes.

## Usage Rules

- Keep telemetry schema decisions explicit and close to the iteration that
  introduces them.
- Prefer reportable structured payloads over debug-only convenience output.
- Treat Phase T as shared telemetry infrastructure with family extensions, not
  as permanently `GRCV2`-shaped code.
- Keep Phase T aligned with:
  - [`Phase-L1-ImplementationPlan.md`](./Phase-L1-ImplementationPlan.md)
  - [`Phase-L1-ImplementationChecklist.md`](./Phase-L1-ImplementationChecklist.md)
  - [`GRCV3-Closeout.md`](./GRCV3-Closeout.md)
  - [`Phase-5-StepLoop.md`](./Phase-5-StepLoop.md)
  - [`Phase-5-RepresentativeRuntime.md`](./Phase-5-RepresentativeRuntime.md)
  - [`Phase-T-ExperimentsRefactorPlan.md`](./Phase-T-ExperimentsRefactorPlan.md)
  - [`Phase-T-ExperimentsRefactorChecklist.md`](./Phase-T-ExperimentsRefactorChecklist.md)
  - `rc-sim/simulations/active/simulation-v22-cuda.py`
  - `rc-sim/experiments/papers/24D-CoherenceLoops-ExperimentationLog.md`
- Keep visualization concerns out of this phase unless they are required to
  define a downstream contract.

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

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / test / review check>
- [ ] <Boundary / acceptance check>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Checklist Bootstrap

### Goal

Create the Phase T execution checklist and align it with the telemetry phase
plan and top-level implementation ordering.

### Checks

- [x] Create `Phase-T-ImplementationPlan.md`
- [x] Create `Phase-T-ImplementationChecklist.md`
- [x] Link Phase T from `ImplementationPhases.md`
- [x] Record the downstream distinction between telemetry (`T`) and visualization (`V`)
- [x] Record the agreed telemetry defaults for:
  - common cross-family contract first
  - in-memory summary always / artifact writing opt-in
  - JSONL rows plus JSON summaries/reports
  - relative run-directory artifact layout
  - summary-first comparison surfaces
  - `balanced_baseline` as the initial reporting lane for `cell-1` and `cell-4`
  - lightweight per-step scalars by default with optional snapshot intervals

### Implementation Notes

- Phase T is now the required next step after Phase L1 and before any new family
  implementation.
- The division is explicit:
  - Phase T owns telemetry, summaries, reports, and experiment artifacts
  - Phase V owns visual surfaces built on top of those artifacts
- The agreed defaults are now recorded in the Phase T plan itself so later
  iterations inherit the same telemetry boundary rather than re-deciding it
  ad hoc.

### Verification

- [x] The plan/checklist pair exists under `implementation/`
- [x] `ImplementationPhases.md` lists both `T` and `V` in the correct order
- [x] The next-step boundary is explicit at the top-level phase registry

### Summary

Phase T now exists as the next implementation phase, and the telemetry versus
visualization boundary is explicit in the project plan.

## Iteration 1. Telemetry Package Boundary

### Goal

Create the shared telemetry package and define the first public telemetry
surface.

### Checks

- [x] Create `src/pygrc/telemetry/`
- [x] Define the first public export surface
- [x] Keep telemetry code out of family-local modules except for narrow hook calls
- [x] Add import-smoke coverage

### Implementation Notes

- The first boundary should stay small and explicit.
- Do not let telemetry logic spread ad hoc through `models/` or `landscapes/`.
- Implemented the first shared telemetry package as:
  - `src/pygrc/telemetry/__init__.py`
  - `src/pygrc/telemetry/schema.py`
- Chosen Iteration 1 export surface:
  - generic `TelemetryRecord`
  - named envelopes:
    - initial per-step / per-event / summary names, later refined in Iteration 2
    - `RunTelemetrySummary`
    - `TelemetryComparisonReport`
    - `TelemetryExperimentReport`
  - shared kind constants:
    - `STEP_TELEMETRY_KIND`
    - `EVENT_TELEMETRY_KIND`
    - `RUN_SUMMARY_KIND`
    - `COMPARISON_REPORT_KIND`
    - `EXPERIMENT_REPORT_KIND`
- Chosen extension model:
  - one common `common` mapping for cross-family fields
  - one `extensions` mapping keyed by family name for family-specific payloads
- Chosen boundary discipline:
  - Iteration 1 defines names and extension shape only
  - canonical row contents are deferred to Iteration 2
  - no telemetry logic was added under `src/pygrc/models/` or `src/pygrc/landscapes/`
- Added import/boundary tests in:
  - initially `tests/telemetry/test_imports.py`
  - later superseded by `tests/telemetry/test_schema.py` once the row contracts
    became explicit

### Verification

- [x] Telemetry imports cleanly
- [x] The shared telemetry vocabulary is visible and intentional
- [x] Existing model imports still work after exposing `pygrc.telemetry`

### Summary

Completed the first telemetry boundary slice. `PyGRC` now exposes a shared
`telemetry` package with explicit common record names and a family-extension
surface, while leaving actual step/event/summary field selection to the next
iteration. Import-smoke coverage is in place, and the boundary stays outside
family-local runtime code.

## Iteration 2. Step And Run Summary Schema

### Goal

Define the canonical telemetry row and run-summary contracts.

### Checks

- [x] Define step telemetry schema
- [x] Define event-row or event-family telemetry schema
- [x] Define run-summary schema
- [x] Decide identity/provenance fields

### Implementation Notes

- Reuse existing runtime surfaces where possible:
  - observables
  - events
  - params identity
  - seed identity
- Do not invent names that silently conflict with model terms.
- Implemented canonical schema types in:
  - `src/pygrc/telemetry/schema.py`
- Chosen telemetry identity surface:
  - `RunTelemetryIdentity`
  - fields:
    - `run_id`
    - `model_family`
    - `params_identity`
    - `seed_name`
    - `seed_source_reference`
    - `seed_path`
    - `param_family`
    - `rng_seed`
    - `requested_steps`
- Chosen deterministic run-id inputs:
  - `model_family`
  - `params_identity`
  - `seed_name`
  - `seed_source_reference`
  - `seed_path`
  - `param_family`
  - `rng_seed`
  - `requested_steps`
  - explicit overrides when present
- Chosen step-row schema:
  - `identity`
  - `step_index`
  - `time`
  - `event_count`
  - `event_counts_by_kind`
  - `observables`
  - `bookkeeping`
  - `family_extensions`
- Chosen event-row schema:
  - `identity`
  - `step_index`
  - `event_index`
  - `event_kind`
  - `source_family`
  - `payload`
  - `family_extensions`
- Chosen run-summary schema:
  - `identity`
  - `completed_steps`
  - `final_step_index`
  - `initial_time`
  - `final_time`
  - `total_event_count`
  - `event_counts_by_kind`
  - `initial_observables`
  - `final_observables`
  - `resolved_params`
  - `raw_params`
  - `parameter_overrides`
  - `status`
  - `family_extensions`
- Chosen parameter-returnability rule:
  - static run parameters are stored at the run-summary/report level
  - if parameters ever become dynamic during execution, telemetry must later
    extend to per-step effective-parameter identity/deltas or explicit
    parameter-change events
- Added builder helpers that map directly from the current runtime surface:
  - `step_row_from_step_result(...)`
  - `event_rows_from_events(...)`
  - `run_summary_from_step_results(...)`
- `run_summary_from_step_results(...)` now fixes `initial_time` to the pre-run
  instant so it stays aligned with `initial_observables` rather than the time
  after the first completed step.
- All schema payloads freeze nested mappings/lists at the telemetry boundary so
  later I/O and reports do not mutate the in-memory source objects accidentally.
- Added contract tests in:
  - `tests/telemetry/test_schema.py`

### Verification

- [x] Step and summary payloads are explicit and testable
- [x] Identity/provenance fields are sufficient for replay traceability
- [x] Existing model/runtime imports still work with the expanded telemetry surface

### Summary

Completed the canonical schema layer for Phase T. The project now has explicit
step rows, event rows, run summaries, and a deterministic run-identity surface
built from replay-critical inputs rather than ad hoc labels. The builders map
directly from `StepResult` and `GRCEvent`, so the telemetry vocabulary stays
aligned with the existing runtime rather than inventing a parallel contract.

## Iteration 3. Artifact Layout And I/O

### Goal

Implement deterministic output layout and read/write support for telemetry and
summary artifacts.

### Checks

- [x] Decide row-file format and naming
- [x] Implement telemetry writers/loaders
- [x] Implement summary/report writers/loaders
- [x] Keep paths relative and repo-shareable

### Implementation Notes

- The PDE side strongly suggests JSONL rows plus summary/report sidecars.
- Naming and layout should be deterministic and future-family-safe.
- Implemented the artifact I/O layer in:
  - `src/pygrc/telemetry/io.py`
- Chosen default telemetry root:
  - `outputs/experiments`
- Chosen experiment-grouping policy:
  - callers may supply a relative `experiment_path`
  - the effective root becomes `outputs/experiments/<experiment_path>` by default
  - absolute paths and `..` traversal are rejected for that grouping segment
- Chosen repository-sharing policy:
  - `outputs/` is treated as generated local state and is gitignored
  - cross-user reuse should happen through reconstruction scripts or replay
    recipes, not by committing telemetry artifacts
- Chosen run-directory layout:
  - one directory per `run_id`
  - default shape:
    - `outputs/experiments/<run_id>/telemetry/steps.jsonl`
    - `outputs/experiments/<run_id>/telemetry/events.jsonl`
    - `outputs/experiments/<run_id>/telemetry/run_summary.json`
    - `outputs/experiments/<run_id>/telemetry/comparison_report.json`
    - `outputs/experiments/<run_id>/telemetry/experiment_report.json`
  - grouped shape when an experiment lane is configured:
    - `outputs/experiments/<experiment_path>/<run_id>/telemetry/steps.jsonl`
    - `outputs/experiments/<experiment_path>/<run_id>/telemetry/events.jsonl`
    - `outputs/experiments/<experiment_path>/<run_id>/telemetry/run_summary.json`
    - `outputs/experiments/<experiment_path>/<run_id>/telemetry/comparison_report.json`
    - `outputs/experiments/<experiment_path>/<run_id>/telemetry/experiment_report.json`
- Chosen file-format policy:
  - `steps.jsonl` for step rows
  - `events.jsonl` for event rows
  - canonical JSON for summary/report sidecars
- Implemented atomic writers for:
  - step rows
  - event rows
  - run summary
  - comparison report
  - experiment report
- Implemented strict loaders for the same payload families plus a standard
  `TelemetryArtifactPack` loader/saver for one run directory.
- Current `TelemetryArtifactPack` load contract includes:
  - step rows
  - event rows
  - run summary
  - optional experiment report when present
  - optional comparison report when present
- The default layout remains repo-shareable because:
  - the default root is relative
  - no machine-local absolute path is embedded into the layout contract itself
- Added I/O contract tests in:
  - `tests/telemetry/test_io.py`

### Verification

- [x] One run can emit a deterministic artifact pack
- [x] Saved telemetry artifacts can be restored without live runtime access
- [x] Invalid JSON artifacts are rejected strictly

### Summary

Completed the first deterministic telemetry artifact layer. `PyGRC` now has a
project-relative run-directory layout, atomic JSONL/JSON writers, strict
loaders, and a standard artifact-pack boundary that can be consumed without
live runtime access. This closes the storage/layout question before runtime
telemetry hooks are added in the next iteration.

## Iteration 4. Runtime Recording Hooks

### Goal

Capture structured telemetry from executable seed-driven `GRCV2` runs.

### Checks

- [x] Define where telemetry hooks attach to the existing runner path
- [x] Record per-step observables and event surfaces
- [x] Record run-summary payloads
- [x] Verify telemetry does not alter model behavior

### Implementation Notes

- The model itself should stay mostly telemetry-agnostic.
- Prefer runner-level integration and explicit recorder helpers.
- Implemented runtime capture helpers in:
  - `src/pygrc/telemetry/recorder.py`
- Chosen runtime-capture surface:
  - `TelemetryCaptureConfig`
  - `TelemetryCaptureResult`
  - `capture_run_telemetry(...)`
- Chosen run-level parameter capture surface:
  - `resolved_params`
  - `raw_params`
  - `overrides` captured as `parameter_overrides`
- Chosen runtime output-location surface:
  - `TelemetryCaptureConfig.root_dir`
  - `TelemetryCaptureConfig.experiment_path`
- Chosen hook location:
  - telemetry is captured once inside `run_grcv2_landscape_seed(...)`
  - after:
    - initial observables are collected
    - stepping is complete
    - final observables are collected
  - no telemetry logic was moved into `GRCV2.step()` or the family model core
- Chosen capture policy:
  - in-memory telemetry capture is always produced by the runner helper
  - artifact writing remains opt-in through `telemetry_root`
  - if `telemetry_root` is omitted:
    - `GRCV2LandscapeRunResult.telemetry` still contains step rows, event rows,
      and run summary
    - no files are written
- Added `telemetry` to `GRCV2LandscapeRunResult` so the runner now returns:
  - executable model/result objects
  - plus the structured telemetry capture derived from the same run
- `run_grcv2_landscape_seed(...)` now accepts:
  - `telemetry_root` for the project-relative telemetry root
  - `telemetry_experiment_path` for the configuration-owned lane under that
    root
- Current family extension block for `GRCV2` runtime capture records:
  - `param_family`
  - `seed_schema`
  - `budget_mode`
- Added runtime-hook tests in:
  - `tests/telemetry/test_recorder.py`
  - `tests/models/test_grc_v2_landscape_runtime.py`

### Verification

- [x] Telemetry-enabled runs remain deterministic
- [x] Step rows and run summaries are produced for representative runs
- [x] Artifact writing can be enabled without changing the underlying runtime trajectory

### Summary

Completed the runtime hook layer for Phase T. Seed-driven `GRCV2` runner calls
now always produce structured in-memory telemetry, and they can optionally emit
artifact packs when `telemetry_root` is provided. The capture stays at the
runner boundary rather than inside the model loop, so the model remains
telemetry-agnostic while representative runs become directly inspectable.

## Iteration 5. Post-Processing And Reports

### Goal

Build first post-processing helpers and experiment report payloads.

### Checks

- [x] Implement trajectory summarization helpers
- [x] Implement comparison/report helpers
- [x] Define first report payloads
- [x] Make reports cite source artifact identities

### Implementation Notes

- Phase T should produce reportable evidence surfaces before any plotting work.
- Reports should be useful without requiring visualization.
- Implemented post-processing helpers in:
  - `src/pygrc/telemetry/reports.py`
  - `src/pygrc/telemetry/compare.py`
- Chosen phase-minimum report types:
  - one run-level experiment report:
    - `trajectory_summary_v1`
  - one pairwise comparison report:
    - `run_summary_comparison_v1`
- Chosen trajectory summarization helpers:
  - `summarize_numeric_observable_trajectory(...)`
  - `list_changed_observables(...)`
  - `build_run_experiment_report(...)`
- Chosen comparison helper:
  - `compare_run_summaries(...)`
- Chosen comparison metric naming:
  - directional deltas use explicit `right_minus_left` naming
  - current minimum set:
    - `completed_steps_right_minus_left`
    - `total_event_count_right_minus_left`
    - `event_counts_by_kind_right_minus_left`
    - `final_observables_right_minus_left`
- Chosen artifact citation policy:
  - reports cite source artifacts through shareable relative references
  - if the layout root is relative, the experiment grouping is preserved in the
    cited path
  - no machine-local absolute root path is embedded into report payloads
  - helper:
    - `build_artifact_references(...)`
- Current run experiment report includes:
  - run identity fields
  - run-level parameter payloads:
    - `resolved_params`
    - `raw_params`
    - `parameter_overrides`
  - source artifact references
  - event counts
  - changed observable names
  - numeric observable trajectory ranges/deltas
  - checkpoint overview
- Current comparison report includes left/right parameter context:
  - `*_params_identity`
  - `*_resolved_params`
  - `*_raw_params`
  - `*_parameter_overrides`
- Added report/comparison tests in:
  - `tests/telemetry/test_reports.py`
- Recorded accepted non-blockers for later telemetry iterations:
  - `_is_finite_number` is currently duplicated in `reports.py` and
    `compare.py`
  - trajectory summaries intentionally repeat initial/final values for direct
    query convenience
  - pairwise comparison is summary-first and currently limited to
    `final_observables`
  - checkpoint/window discipline remains intentionally minimal at this stage

### Verification

- [x] Telemetry artifacts can be converted into report payloads
- [x] Comparison/report outputs are stable and testable
- [x] Report payloads cite source artifact identities without relying on absolute paths

### Summary

Completed the first post-processing/report layer for Phase T. `PyGRC` can now
turn telemetry-backed runs into a trajectory-summary experiment report and a
stable pairwise comparison report, with explicit metric names and artifact
references that preserve the configured experiment lane without leaking
machine-local absolute roots. This makes the telemetry
output analytically useful before any visualization work begins.

## Iteration 6. Representative Experiment Surface

### Goal

Use `cell-1` and `cell-4` as the first telemetry-backed experiment lanes.

### Checks

- [x] Emit telemetry artifacts for `cell-1`
- [x] Emit telemetry artifacts for `cell-4`
- [x] Generate representative summaries/reports
- [x] Verify experiment outputs show more than raw observables dumps

### Implementation Notes

- The first representative experiment surface should be small but defensible.
- Focus on proving that the new seed-driven path is analytically inspectable.
- Implemented the first representative experiment helper in:
  - `src/pygrc/telemetry/experiments.py`
- Chosen representative lane defaults:
  - seeds:
    - `configs/landscapes/seed/cell-1.seed.yaml`
    - `configs/landscapes/seed/cell-4.seed.yaml`
  - family:
    - `balanced_baseline`
  - step count:
    - `3`
  - RNG seed:
    - `7`
- Implemented representative helper surface:
  - `run_grcv2_representative_experiment(...)`
  - result bundle:
    - `GRCV2RepresentativeExperimentResult`
- Chosen representative output grouping:
  - default base lane:
    - `outputs/experiments/grcv2/representative/<family_name>/`
  - per-seed sub-lanes:
    - `.../cell-1/<run_id>/...`
    - `.../cell-4/<run_id>/...`
- Current representative experiment output includes:
  - telemetry artifact packs for both canonical seeds
  - one trajectory-summary experiment report per run
  - one pairwise comparison report shared across the two run directories
  - report/checkpoint content that goes beyond raw observables dumps:
    - changed observable names
    - numeric observable trajectory ranges/deltas
    - event counts
    - checkpoint overview
    - final-summary comparison deltas
- This iteration intentionally does **not** claim `rc-sim` 25* classification
  equivalence yet. It establishes the first telemetry-backed experiment lane
  that can now be judged against that standard in Iteration 7.
- Added representative experiment tests in:
  - `tests/telemetry/test_experiments.py`

### Verification

- [x] `cell-1` produces telemetry and summary/report artifacts
- [x] `cell-4` produces telemetry and summary/report artifacts
- [x] Representative metrics/checkpoints are explicit
- [x] Representative outputs are loadable from disk without live runtime state

### Summary

Completed the first representative experiment surface for Phase T. `cell-1`
and `cell-4` now run through a single helper that emits telemetry artifacts,
per-run experiment reports, and a pairwise comparison report under the default
`balanced_baseline` lane. The outputs are now rich enough to support an honest
next-step judgment about how far current `PyGRC` telemetry is from the
classification discipline seen in the PDE-side 25* papers.

## Iteration 7. Validation Gate And Phase V Handoff

### Goal

Validate the telemetry phase against PDE-style experimental discipline and define
the downstream visualization boundary.

### Checks

- [x] Review telemetry surfaces against the Phase T design goals
- [x] Record remaining telemetry limitations explicitly
- [x] Define the Phase V downstream contract
- [x] Verify no unresolved telemetry blocker remains for representative seed-driven runs

### Implementation Notes

- The final question is whether `PyGRC` is now experiment-capable rather than
  only runnable.
- Visualization should consume telemetry/report artifacts rather than become a
  substitute for them.
- Validation basis now includes the representative helper:
  - `run_grcv2_representative_experiment(...)`
  - default lane:
    - `cell-1`
    - `cell-4`
    - `balanced_baseline`
    - `num_steps = 3`
    - `rng_seed = 7`
- Representative validation observation from the current lane:
  - both canonical seeds produce deterministic telemetry/report artifacts
  - both current experiment reports identify changed observables including:
    - `abundance`
    - `average_conductance`
    - `sink_count`
    - `weighted_abundance`
  - current event counts are empty in that representative lane
  - current comparison reports expose explicit summary deltas and artifact
    references
- Explicit remaining telemetry limitations at Phase T closeout:
  - the current telemetry/report stack is strong enough for structured
    experiment inspection, but it is not yet equivalent to the PDE-side `25*`
    classification layer
  - only `GRCV2` is currently wired into the full telemetry-backed experiment
    lane
  - checkpoint/window discipline remains minimal:
    - first/last step index
    - step count
    - but not richer temporal segmentation
  - pairwise comparison remains summary-first and centered on final observables
  - classification-oriented trajectory features such as onset windows, plateau
    durations, or oscillation descriptors are not yet first-class report fields
  - current visible output is behavior-facing only:
    - trajectories
    - event timelines
    - report/comparison panels
  - graph-visible and flow-visible output is still blocked because telemetry
    does not yet export:
    - checkpoint topology artifacts
    - checkpoint node/edge overlay artifacts
    - checkpoint flow artifacts
  - accepted non-blockers remain open:
    - duplicated `_is_finite_number`
    - intentionally redundant initial/final trajectory exposure
- Defined the Phase V downstream contract in:
  - `implementation/Phase-V-Handoff.md`
- Defined the next telemetry-side requirement for graph/flow visuals:
  - future checkpoint artifact schema + recorder support
- Phase T closure claim:
  - `PyGRC` is now telemetry-backed and experiment-capable for seed-driven
    `GRCV2` runs
  - it is not yet classification-complete relative to the PDE-side research
    workflow
  - it does not yet provide saved graph-visible output from telemetry artifacts

### Verification

- [x] The telemetry/report path is reviewable against the governing docs
- [x] No unresolved blocker remains for telemetry-backed `cell-1` / `cell-4` experiments
- [x] Phase V has an explicit downstream contract that forbids bypassing telemetry/report artifacts

### Summary

Closed Phase T. The project now has a deterministic telemetry-backed
experiment surface for seed-driven `GRCV2`, including schema contracts,
artifact layout, runtime capture, post-processing helpers, per-run experiment
reports, and a representative `cell-1` / `cell-4` lane. The remaining limits
are explicit: this is now experiment-capable and reviewable, but not yet at
full PDE-side `25*` classification richness. Current downstream visible output
is limited to the behavior-facing scalar/report layer; graph-visible and
flow-visible output still require future checkpoint topology/flow telemetry
artifacts. Phase V can therefore proceed honestly only within that boundary
until telemetry grows the missing graph checkpoint surfaces.

## Iteration 8. Graph Checkpoint Schema

### Goal

Define the checkpoint artifact schema and deterministic on-disk layout needed
for graph-visible telemetry.

### Checks

- [x] Define checkpoint index schema
- [x] Define checkpoint payload schema
- [x] Define deterministic run-directory layout for checkpoint artifacts
- [x] Define strict save/load validation rules
- [x] Add schema and I/O tests for checkpoint artifacts

### Implementation Notes

- This iteration should implement the schema-level contract already written in:
  - `implementation/Phase-V-TopologyFlowArtifactBridge.md`
  - `implementation/Phase-V-GraphEvolutionContract.md`
  - `implementation/Phase-V-FlowActivityContract.md`
- Graph-shaped artifacts should remain sidecars rather than being injected into
  `steps.jsonl`.
- The expected shape is:
  - `graph_checkpoints/index.json`
  - one deterministic checkpoint JSON file per saved frame
- Implemented checkpoint schema datatypes in:
  - `src/pygrc/telemetry/schema.py`
    - `GraphCheckpointArtifact`
    - `GraphCheckpointReference`
    - `GraphCheckpointIndex`
- Implemented checkpoint I/O support in:
  - `src/pygrc/telemetry/io.py`
    - `build_graph_checkpoint_path(...)`
    - `save_graph_checkpoint(...)`
    - `load_graph_checkpoint(...)`
    - `save_graph_checkpoint_index(...)`
    - `load_graph_checkpoint_index(...)`
- Extended `TelemetryArtifactLayout` with:
  - `graph_checkpoints_dir`
  - `graph_checkpoint_index_path`
- Extended `TelemetryArtifactPack` with:
  - `graph_checkpoint_index`
  - `graph_checkpoints`
- Added checkpoint schema/I/O tests in:
  - `tests/telemetry/test_checkpoints.py`

### Verification

- [x] Checkpoint artifacts are schema-defined rather than ad hoc
- [x] Invalid checkpoint JSON is rejected strictly
- [x] Save/load behavior is deterministic

### Summary

Completed the checkpoint schema and I/O layer. Telemetry now has deterministic
graph-checkpoint artifact types, run-directory layout support, canonical
save/load helpers, and strict validation for checkpoint payloads and the
checkpoint index.

## Iteration 9. Recorder And Export Hooks

### Goal

Extend telemetry capture so runs can request and record checkpoint artifacts
without collapsing telemetry concerns back into visualization.

### Checks

- [x] Add checkpoint recording options to telemetry capture config
- [x] Define checkpoint selection policy surface
- [x] Define family export hook boundary for graph checkpoints
- [x] Ensure recorder integration does not alter model behavior
- [x] Add recorder-level tests for checkpoint capture selection

### Implementation Notes

- This iteration should add the telemetry-side knobs that later phases will
  use, for example:
  - whether graph checkpoints are recorded
  - interval vs explicit vs eventful selection
  - whether flow overlays are requested
- The recorder should call a family-aware export hook or adapter rather than
  trying to reconstruct graph state by inspection.
- Implemented recorder-side checkpoint config in:
  - `src/pygrc/telemetry/recorder.py`
    - `GraphCheckpointCaptureConfig`
- Extended `TelemetryCaptureConfig` with:
  - `graph_checkpoints`
- Extended `TelemetryCaptureResult` with:
  - `graph_checkpoint_index`
  - `graph_checkpoints`
- Implemented recorder-side checkpoint index builder:
  - `_build_graph_checkpoint_index(...)`
- Current family export boundary is explicit in the runner path:
  - `src/pygrc/models/grc_v2_landscape.py`
  - via `export_grcv2_graph_checkpoint(...)`
- Recorder/runner behavior remained observational:
  - scalar telemetry path still works unchanged when checkpoint capture is off
  - checkpoint capture is opt-in through config/runner flags

### Verification

- [x] Checkpoint capture can be configured independently of scalar telemetry
- [x] Recorder remains telemetry-observational rather than model-defining
- [x] The family export boundary is explicit

### Summary

Completed the recorder/config extension for checkpoint telemetry. The telemetry
layer can now carry graph-checkpoint capture policy alongside the existing
scalar telemetry path, and the family-aware export boundary is explicit rather
than hidden in visualization code.

## Iteration 10. GRCV2 Checkpoint Export

### Goal

Implement the first real graph checkpoint exporter for `GRCV2`.

### Checks

- [x] Export weighted-graph checkpoint topology for `GRCV2`
- [x] Export minimum node overlays:
  - [x] `coherence`
- [x] Export minimum edge overlays:
  - [x] `base_conductance`
- [x] Export recommended common overlays where available
- [x] Support at least:
  - [x] `initial`
  - [x] `final`
  - [x] `every_n_steps`
- [x] Add `GRCV2` checkpoint export tests

### Implementation Notes

- This is the first implementation lane, not the final cross-family definition.
- The exporter must stay aligned with:
  - `graph_kind = weighted_graph`
  - stable node IDs
  - stable edge IDs
- It should emit artifacts that are usable without a live runtime object.
- Implemented `GRCV2` checkpoint exporter in:
  - `src/pygrc/models/grc_v2_checkpoints.py`
    - `export_grcv2_graph_checkpoint(...)`
- Exported weighted-graph checkpoint payload includes:
  - stable node IDs
  - stable edge IDs
  - node `payload`
  - edge `payload`
  - node `coherence`
  - edge `base_conductance`
  - available common overlays:
    - `potential`
    - `sink_flag`
    - `basin_id`
    - `parent_id`
    - `geometric_length`
    - `temporal_delay`
    - `flux_coupling`
- Implemented checkpoint capture in the `GRCV2` landscape runner:
  - `src/pygrc/models/grc_v2_landscape.py`
  - current supported selectors:
    - `initial`
    - `final`
    - `every_n_steps`

### Verification

- [x] `GRCV2` runs can emit real checkpoint artifacts
- [x] Exported topology is loadable and deterministic
- [x] Minimum overlay surface is present

### Summary

Completed the first real `GRCV2` graph-checkpoint exporter. Seed-driven runs
can now emit deterministic weighted-graph checkpoint artifacts with stable
topology identity and the minimum common overlay surface required for later
graph-facing work.

## Iteration 11. Flow Overlay Export

### Goal

Export the first honest flow overlay surface for checkpoint artifacts.

### Checks

- [x] Export preferred per-edge flow quantity:
  - [x] `signed_flux` when available
- [x] Implement explicit fallback:
  - [x] `flux_coupling` as `magnitude_only_surrogate`
- [x] Export node flow summaries when available:
  - [x] `net_flux`
  - [x] `in_flux`
  - [x] `out_flux`
- [x] Export flow metadata fields
- [x] Add flow export tests and strict validation tests

### Implementation Notes

- This iteration must preserve the distinction between:
  - `base_conductance`
  - `signed_flux`
  - `flux_coupling`
- If `signed_flux` cannot yet be emitted in some path, the artifact must state
  that it is magnitude-only rather than pretending direction exists.
- Implemented flow-capable checkpoint export in:
  - `src/pygrc/models/grc_v2_checkpoints.py`
- Current flow export behavior:
  - post-step checkpoints export per-edge `signed_flux` when present
  - flow metadata declares:
    - `flow_representation`
    - `flow_cadence`
  - node records export:
    - `net_flux`
    - `in_flux`
    - `out_flux`
  - pre-step initial checkpoints declare:
    - `flow_representation = not_available_pre_step`
    because flux has not been computed yet
- The explicit surrogate contract remains available in the schema/I/O surface
  even though the implemented `GRCV2` path currently emits signed edge flux for
  post-step checkpoints.

### Verification

- [x] Flow overlays are exported under an explicit contract
- [x] Surrogate mode is declared explicitly when used
- [x] No flow quantity is inferred silently at visualization time

### Summary

Completed the first honest flow overlay export path for checkpoint telemetry.
`GRCV2` checkpoint artifacts now distinguish conductance from realized flow,
export signed edge flux where available, export node net-flow summaries, and
declare flow metadata explicitly.

## Iteration 12. Checkpoint Artifact Validation Lane

### Goal

Validate the new checkpoint telemetry on the canonical representative lane and
close the handoff back to graph-facing Phase V work.

### Checks

- [x] Run representative checkpoint telemetry for:
  - [x] `cell-1`
  - [x] `cell-4`
- [x] Verify checkpoint artifact determinism
- [x] Verify checkpoint artifact loadability without live runtime state
- [x] Verify topology and flow overlays match the implemented contract
- [x] Record the handoff boundary back to Phase V graph/flow rendering

### Implementation Notes

- The representative validation lane should use the same baseline family and
  seeds already established for telemetry and behavior visualization.
- The purpose is not only to save artifacts, but to prove that graph-visible
  and flow-visible Phase V work can now begin on real saved evidence.
- Validation basis now includes:
  - `balanced_baseline`
  - `num_steps = 100`
  - `rng_seed = 7`
  - `checkpoint_every_n_steps = 25`
  - `include_flow_overlays = True`
- Executed representative validation lane produced:
  - 5 checkpoints for `cell-1`
  - 5 checkpoints for `cell-4`
  - `graph_checkpoints/index.json`
  - `step-00000000.json`
  - `step-00000025.json`
  - `step-00000050.json`
  - `step-00000075.json`
  - `step-00000100.json`
- Representative example paths now exist under:
  - `outputs/experiments/grcv2/representative/balanced_baseline/cell-1/<run_id>/telemetry/graph_checkpoints/`
  - `outputs/experiments/grcv2/representative/balanced_baseline/cell-4/<run_id>/telemetry/graph_checkpoints/`
- The saved final checkpoints now contain real:
  - weighted-graph topology
  - node coherence overlays
  - edge conductance overlays
  - signed flow overlays
  - node net-flow summaries

### Verification

- [x] Representative runs produce checkpoint artifacts successfully
- [x] Artifacts are deterministic and reviewable
- [x] Phase V no longer needs to block graph/flow rendering on missing telemetry

### Summary

Closed the checkpoint telemetry follow-on for Phase T. The representative
`cell-1` / `cell-4` lane now produces real checkpoint topology and flow
artifacts that can be loaded without live runtime state. The missing blocker
for graph-facing Phase V work is no longer telemetry absence, but the actual
implementation of graph rendering on top of these saved checkpoint artifacts.

## Iteration 13. Dense Checkpoint Streaming Mode

### Goal

Add dense checkpoint export support for graph-evolution study without requiring
full-run graph retention in memory.

### Checks

- [x] Define dense checkpoint cadence support:
  - [x] `every_step`
  - [x] or an equivalent dense mode
- [x] Define dense retention/storage modes separately from cadence
- [x] Implement bounded-memory checkpoint streaming or chunking
- [x] Keep sparse per-checkpoint file mode available for milestone inspection
- [x] Add dense-mode load/replay tests
- [x] Validate dense checkpoint artifacts on a representative lane

### Implementation Notes

- Sparse checkpoints are already sufficient to get a structural picture of the
  run.
- Dense mode is needed to actually study temporal graph evolution rather than
  only milestone states.
- The intended design direction is:
  - build one checkpoint artifact in memory
  - hand it off immediately to a retention sink
  - do not retain the full run's checkpoint history in memory by default
- For dense mode, chunked/streamed persistence is preferred over one-file-per-step
  once checkpoint counts become large.
- This is still telemetry work, not visualization work, and should land before
  Phase V expands into serious graph-evolution rendering.
- Implemented dense checkpoint cadence and storage separation in:
  - `src/pygrc/telemetry/recorder.py`
    - `GraphCheckpointCaptureConfig.every_step`
    - `GraphCheckpointCaptureConfig.storage_mode`
    - `GraphCheckpointCaptureConfig.chunk_size`
- Implemented chunk-backed checkpoint persistence in:
  - `src/pygrc/telemetry/io.py`
    - `GraphCheckpointChunkWriter`
    - `build_graph_checkpoint_chunk_path(...)`
    - `load_graph_checkpoint_from_reference(...)`
- Extended index serialization so checkpoint references can target:
  - standalone file checkpoints
  - JSONL chunk checkpoints with `chunk_line_index`
- Implemented dense-mode runner support in:
  - `src/pygrc/models/grc_v2_landscape.py`
    - `checkpoint_every_step`
    - `checkpoint_storage_mode`
    - `checkpoint_chunk_size`
- Dense chunk mode is artifact-backed by design:
  - each checkpoint artifact is built in memory once
  - written immediately to the chunk sink
  - only lightweight `GraphCheckpointReference` entries are retained in memory
- Sparse per-checkpoint JSON files remain available through:
  - `checkpoint_storage_mode="per_checkpoint_files"`
- Added dense-mode validation in:
  - `tests/telemetry/test_checkpoints.py`
    - chunked every-step runner path
    - explicit failure when chunked storage is requested without `telemetry_root`
- Representative validation lane executed with:
  - `cell-1`
  - `cell-4`
  - `balanced_baseline`
  - `num_steps = 10`
  - `checkpoint_every_step = True`
  - `checkpoint_storage_mode = "jsonl_chunks"`
  - `checkpoint_chunk_size = 4`
  - `include_flow_overlays = True`
- Resulting representative runs produced:
  - 11 checkpoint references per run (`initial` + 10 step checkpoints with final folded into step 10)
  - chunk files `chunk-00000001.jsonl` through `chunk-00000003.jsonl`
  - deterministic dense checkpoint indexes under `graph_checkpoints/index.json`

### Verification

- [x] Dense checkpoint export does not require unbounded memory growth
- [x] Dense artifacts remain deterministic and loadable
- [x] Phase V can consume dense graph-evolution artifacts without touching live state

### Summary

Dense checkpoint capture now supports streamed chunked storage with a stable
chunk index, so longer runs no longer require one JSON file per checkpoint
frame while remaining replayable and layout-deterministic.

## Iteration 14. Cross-Family Telemetry Expansion Boundary

### Goal

Reframe Phase T from the first `GRCV2` telemetry implementation into a shared
telemetry framework that can be extended cleanly to `GRCV3`.

### Checks

- [x] Update the Phase T plan to state that Phase T is a common telemetry
      architecture rather than a `GRCV2`-only phase
- [x] Record the common-versus-family telemetry boundary explicitly
- [x] Add a family-extension matrix covering `GRCV2` and `GRCV3`
- [x] Record the initial `GRCV3` telemetry extension surface to implement next

### Implementation Notes

- Added [Phase-T-FamilyExtensionMatrix.md](./Phase-T-FamilyExtensionMatrix.md)
  as the explicit split between:
  - common telemetry core
  - family-specific telemetry extensions
- Updated [Phase-T-ImplementationPlan.md](./Phase-T-ImplementationPlan.md) so
  it now reads as a family-general telemetry phase with:
  - `GRCV2` as the first completed telemetry lane
  - `GRCV3` as the next extension lane
- Recorded the initial `GRCV3` extension targets:
  - basin-attribute summaries
  - signed-Hessian metadata
  - hierarchy summaries
  - spark lifecycle summaries
  - choice/collapse lifecycle summaries

### Verification

- [x] The plan no longer reads as if telemetry is effectively synonymous with
      `GRCV2`
- [x] The common/family boundary is now explicit in project docs
- [x] The next `GRCV3` telemetry slice can proceed without inventing a parallel
      telemetry architecture

### Summary

Phase T now explicitly owns shared telemetry infrastructure plus family
extensions. `GRCV3` can extend the existing telemetry architecture directly,
rather than starting a separate telemetry phase or silently bending the shared
contract around family-local needs.

## Iteration 15. GRCV3 Telemetry Planning Boundary

### Goal

Turn the Phase T family-extension direction into an explicit execution lane for
`GRCV3` before any new telemetry code is written.

### Checks

- [x] Add a `GRCV3` telemetry extension section to the Phase T plan
- [x] Define the `GRCV3` telemetry scope and explicit non-goals for the first
      slice
- [x] Record the required Phase 5 inputs that constrain the telemetry design
- [x] Define the next `GRCV3` telemetry iteration order inside the Phase T plan
- [x] Record in this checklist that planning was completed before new code
      resumed

### Implementation Notes

- The shared Phase T documents now state a dedicated `GRCV3` telemetry lane
  rather than leaving it implied by the family-extension matrix alone.
- The first `GRCV3` telemetry slice is intentionally behavior-first:
  - shared telemetry rows stay unchanged
  - `GRCV3` adds explicit family extensions
  - the representative runtime lane comes from Phase 5 rather than from a new
    landscape projector path
- Explicitly deferred for this slice:
  - `GRCV3` graph checkpoints
  - `GRCV3` visualization outputs
  - broad cross-family comparison claims
- During this turn an accidental jump into `GRCV3` telemetry code was reverted
  so the repository remains aligned with the documented planning-first order.

### Verification

- [x] `Phase-T-ImplementationPlan.md` contains a dedicated `GRCV3` telemetry
      extension section
- [x] The checklist now names concrete upcoming `GRCV3` telemetry iterations
- [x] No `GRCV3` telemetry implementation was left half-started in the codebase

### Summary

Phase T now has an explicit planning boundary for `GRCV3` telemetry. The next
steps are documented as a proper execution lane instead of being inferred from
the shared-family matrix.

## Iteration 16. GRCV3 Family-Extension Contract

### Goal

Define the first concrete `GRCV3` telemetry extension payloads before runtime
integration.

### Checks

- [x] Define the canonical `GRCV3` step-row extension payload
- [x] Define the canonical `GRCV3` event-row extension payload
- [x] Define the canonical `GRCV3` run-summary extension payload
- [x] Record required versus optional `GRCV3` telemetry fields
- [x] Record any compression/aggregation rules applied to Phase 5 state

### Implementation Notes

- This iteration should stay purely contract-facing.
- The output should make it obvious which Phase 5 quantities are directly
  surfaced and which are summarized.
- Implemented the explicit contract module in:
  - `src/pygrc/telemetry/grcv3_contract.py`
- Exported the contract through:
  - `src/pygrc/telemetry/__init__.py`
- Added the field-level contract note:
  - [Phase-T-GRCV3-TelemetryContract.md](./Phase-T-GRCV3-TelemetryContract.md)
- Chosen canonical `GRCV3` step-row extension groups:
  - `backend_summary`
  - `signed_hessian`
  - `basin_summary`
  - `spark_state`
  - `hierarchy_state`
  - `choice_state`
- Chosen canonical `GRCV3` event-row extension groups:
  - event classification:
    - `event_domain`
    - `lifecycle_stage`
    - `topology_mutation`
    - `hierarchy_mutation`
  - optional event-local identifiers:
    - `primary_node_id`
    - `primary_basin_id`
    - `registry_key`
- Chosen canonical `GRCV3` run-summary extension groups:
  - `backend_summary`
  - `signed_hessian`
  - `final_basin_summary`
  - `final_spark_state`
  - `final_hierarchy_state`
  - `final_choice_state`
  - fixed-surface `lifecycle_event_counts`
- Chosen compression rule:
  - Iteration 16 records counts, backend identities, and small lifecycle
    summaries only
  - it deliberately does not serialize per-node gradient/Hessian/net-flux
    payloads or whole runtime registries in step rows/run summaries
- Added contract tests in:
  - `tests/telemetry/test_grcv3_contract.py`

### Verification

- [x] The `GRCV3` extension payloads are explicit and testable on paper
- [x] No shared-schema field names are redefined for `GRCV3`

### Summary

Iteration 16 established the first explicit `GRCV3` telemetry contract. The
shared telemetry core remains unchanged, while `GRCV3` now has a field-level
extension surface for step rows, event rows, and run summaries together with a
contract note and direct tests.

## Iteration 17. GRCV3 Runtime Capture Integration

### Goal

Attach the `GRCV3` telemetry extension payloads to the executable
representative runtime path without changing model semantics.

### Checks

- [x] Add `GRCV3` family-extension assembly at the telemetry boundary
- [x] Wire the representative `GRCV3` runtime lane into shared telemetry
      capture
- [x] Keep `GRCV3.step()` telemetry-agnostic
- [x] Preserve save/load and replay behavior with telemetry enabled
- [x] Add focused tests for `GRCV3` telemetry capture

### Implementation Notes

- The integration point should stay outside the constitutive step loop.
- If a helper is needed, prefer runner-level assembly over model-local
  instrumentation.
- Extended `capture_run_telemetry(...)` to support:
  - per-step family extensions
  - per-event family extensions
  - run-summary family extensions
- The recorder now validates:
  - step-extension sequence length against `step_results`
  - event-extension sequence lengths against per-step event counts
- Kept the model boundary unchanged:
  - no telemetry logic was added to `src/pygrc/models/grc_v3.py`
  - `GRCV3.step()` remains telemetry-agnostic
- Added `GRCV3` runner-side assembly in:
  - `src/pygrc/telemetry/experiments.py`
- The representative lane builds family extensions from:
  - runtime backend selections
  - cached signed-Hessian state
  - geometric identity summaries
  - split registry summaries
  - hierarchy summaries
  - choice/collapse summaries

### Verification

- [x] `GRCV3` runs emit valid shared telemetry plus `GRCV3` family extensions
- [x] Telemetry capture does not alter representative runtime results

### Summary

Iteration 17 integrated `GRCV3` telemetry at the runner boundary. The shared
recorder can now accept per-step, per-event, and per-summary family extensions,
while `GRCV3.step()` itself remains untouched.

## Iteration 18. GRCV3 Representative Report Surface

### Goal

Make the first artifact-backed `GRCV3` reports and representative experiment
surface inspectable.

### Checks

- [x] Define the first `GRCV3` representative telemetry helper
- [x] Build `GRCV3` experiment reports from saved telemetry artifacts
- [x] Decide the first truthful comparison surface for `GRCV3`
- [x] Persist artifacts under the standard Phase T output layout
- [x] Add report/comparison validation tests

### Implementation Notes

- The comparison surface should be truthful and narrow.
- Same-run replay equivalence is preferable to forced cross-family comparison
  if broader claims are not yet justified.
- Implemented the first `GRCV3` representative experiment helper:
  - `run_grcv3_representative_experiment(...)`
- Chosen comparison surface:
  - `primary` vs `replay` of the same Phase 5 representative runtime lane
- Added representative result types:
  - `GRCV3RepresentativeRunResult`
  - `GRCV3RepresentativeExperimentResult`
- Representative artifacts now write under:
  - `outputs/representative/grcv3/<lane_name>/primary/`
  - `outputs/representative/grcv3/<lane_name>/replay/`
- The representative identity is intentionally synthetic for this slice:
  - `seed_path = synthetic/grcv3/<lane_name>/<role>`
  - `param_family = None`
  - `rng_seed = None`
- Recorded the representative surface in:
  - [Phase-T-GRCV3-RepresentativeTelemetry.md](./Phase-T-GRCV3-RepresentativeTelemetry.md)

### Verification

- [x] A representative `GRCV3` telemetry lane produces artifact-backed reports
- [x] Reports remain readable without live model access

### Summary

Iteration 18 established the first artifact-backed `GRCV3` representative
report surface. The comparison is intentionally narrow and truthful:
deterministic `primary` versus `replay` agreement on the Phase 5 reference
lane.

## Iteration 19. GRCV3 Telemetry Validation And Closeout

### Goal

Close the first `GRCV3` telemetry slice with explicit validation, limits, and
handoff notes.

### Checks

- [x] Run the representative `GRCV3` telemetry lane end-to-end
- [x] Verify determinism/replay stability of the saved telemetry artifacts
- [x] Record what remains deferred after the first `GRCV3` telemetry slice
- [x] Patch Phase T docs if any shared-contract boundary changed during
      implementation
- [x] Record the downstream implication for visualization and later family
      work

### Implementation Notes

- This closeout should state clearly whether the next justified step is:
  - `GRCV3` checkpoint telemetry
  - renewed visualization work
  - or another shared telemetry refinement
- Added reconstruction entrypoint:
  - `scripts/run_grcv3_representative_telemetry.py`
- Executed the representative telemetry lane with:
  - `lane_name = "phase_t_iter19_closeout"`
  - `steps = 3`
- Recorded the representative-lane interpretation notes:
  - `hessian_sign` is available because telemetry assembly happens after
    stepping
  - zero lifecycle counts in this lane are by design because the
    representative configuration suppresses sparks
- Recorded the closeout and deferred boundary in:
  - [Phase-T-GRCV3-Closeout.md](./Phase-T-GRCV3-Closeout.md)
- Patched the Phase T plan to reflect the now-implemented recorder boundary:
  - shared run-level extensions
  - per-step extensions
  - per-event extensions
  - run-summary extensions

### Verification

- [x] No unresolved blockers remain for the first `GRCV3` telemetry slice
- [x] Deferred work is documented rather than implied

### Summary

Iteration 19 closed the first `GRCV3` telemetry slice with artifact-backed
evidence. The minimal behavior-facing telemetry lane is now validated,
replay-stable, and documented. At the time of this iteration, richer `GRCV3`
graph-visible inspection remained explicitly deferred to future checkpoint
telemetry work; later Iterations 20-26 and Phase V have since closed those
graph-facing lanes.

## Iteration 20. GRCV3 Checkpoint-Telemetry Planning Boundary

### Goal

Record the later Phase T follow-on that will be needed for `GRCV3`
graph-visible work, without starting it before the behavior-facing Phase V lane
is done.

### Checks

- [x] Add the later `GRCV3` checkpoint-telemetry lane to the Phase T plan
- [x] Record the intended sequencing:
      Phase V behavior first, then Phase T `GRCV3` checkpoint telemetry
- [x] Add the pending checkpoint-telemetry iterations to this checklist

### Implementation Notes

- This is a planning boundary only.
- It exists to make the cross-phase sequence explicit.
- Updated the Phase T plan so the later `GRCV3` checkpoint-telemetry lane is
  now explicit rather than buried inside the generic future-work boundary.
- Recorded the intended cross-phase order:
  - Phase V `GRCV3` behavior visualization first
  - later Phase T `GRCV3` checkpoint telemetry
  - later Phase V `GRCV3` graph visualization
- Added the pending later iterations:
  - Iteration 21: `GRCV3` checkpoint export contract
  - Iteration 22: `GRCV3` representative checkpoint export lane
  - Iteration 23: `GRCV3` checkpoint-telemetry closeout

### Verification

- [x] The later `GRCV3` checkpoint lane is documented but not prematurely mixed
      into the completed minimal telemetry slice

### Summary

Iteration 20 now records the later `GRCV3` checkpoint-telemetry lane without
starting it prematurely. The cross-phase sequence is explicit: behavior-facing
visualization now, graph telemetry later, graph-visible visualization after
that.

## Iteration 21. GRCV3 Checkpoint Export Contract

### Goal

Define the family-specific checkpoint export contract for `GRCV3`.

### Checks

- [x] Define the required `GRCV3` node payload surface for checkpoints
- [x] Define the required `GRCV3` edge payload surface for checkpoints
- [x] Define the `GRCV3` flow-overlay contract if exported
- [x] Record what reuses the common checkpoint schema versus what is
      family-specific

### Implementation Notes

- This should reuse shared checkpoint infrastructure rather than fork it.
- Added [Phase-T-GRCV3-CheckpointContract.md](./Phase-T-GRCV3-CheckpointContract.md)
  as the explicit contract note for the later `GRCV3` checkpoint exporter.
- The contract keeps `GRCV3` on the shared
  [GraphCheckpointArtifact](../src/pygrc/telemetry/schema.py) surface rather
  than introducing a family-local checkpoint schema.
- Locked shared/common reuse:
  - `graph_kind = weighted_graph`
  - shared checkpoint identity/index/layout fields
  - shared event-window metadata
  - shared `label_computation_modes`
  - shared `topology_extensions`
- Locked required `GRCV3` node payload surface:
  - `coherence`
  - `basin_id`
  - `depth`
  - `basin_mass`
  - `gradient`
  - `gradient_norm`
  - `hessian`
  - `net_flux`
  - optional:
    - `parent_id`
    - `potential`
    - `sink_flag`
- Locked required `GRCV3` edge payload surface:
  - `base_conductance`
  - `geometric_length_available`
  - optional:
    - `geometric_length`
    - `temporal_delay`
    - `flux_coupling`
    - `directionality_semantics`
    - `geometric_length_mode`
- Locked `GRCV3` flow-overlay rule:
  - use the same honest signed-edge-flux contract as `GRCV2` when realized
    edge flux exists
  - keep `BasinAttributes.net_flux` separate from edge-derived
    `net_edge_flux`
  - declare `flow_representation = not_available_pre_step` for initial
    checkpoints where realized edge flux does not yet exist
- Locked first `family_extensions["grcv3"]` checkpoint surface:
  - `contract_version`
  - `params_identity`
  - `budget_target`
  - `remainder`
  - `hessian_sign`
  - `backend_summary`
  - `hierarchy_summary`
  - `spark_summary`
  - `choice_summary`
- Explicitly deferred from the first checkpoint slice:
  - full hierarchy dumps
  - full split/choice/collapse registry dumps
  - per-node signed-Hessian eigenvalue caches
  - exporter-side layout algorithms

### Verification

- [x] The `GRCV3` checkpoint surface is explicit before export code is added

### Summary

Closed. The later `GRCV3` checkpoint exporter now has an explicit family
contract before any export code is added. The shared checkpoint schema remains
the container, while node semantics, edge semantics, honest flow overlays, and
`family_extensions["grcv3"]` are now defined tightly enough that Iteration 22
can proceed without inventing checkpoint meaning ad hoc.

## Iteration 22. GRCV3 Representative Checkpoint Export Lane

### Goal

Export the first representative `GRCV3` checkpoint artifacts.

### Checks

- [x] Add `GRCV3` checkpoint export hooks at the telemetry boundary
- [x] Export representative `GRCV3` graph checkpoints
- [x] Export honest flow overlays only if the artifact surface supports them
- [x] Add focused save/load and export tests

### Implementation Notes

- This should stay artifact-first and runner-level, not model-local.
- Implemented the first `GRCV3` checkpoint exporter in:
  - [src/pygrc/models/grc_v3_checkpoints.py](../src/pygrc/models/grc_v3_checkpoints.py)
    - `export_grcv3_graph_checkpoint(...)`
- Exported node payload surface now includes:
  - `coherence`
  - `basin_id`
  - `depth`
  - `basin_mass`
  - `gradient`
  - `gradient_norm`
  - `hessian`
  - `net_flux`
  - optional:
    - `parent_id`
    - `potential`
    - `sink_flag`
    - edge-derived `net_edge_flux`, `in_flux`, `out_flux` when flow overlays
      are honest
- Exported edge payload surface now includes:
  - `base_conductance`
  - `geometric_length_available`
  - optional:
    - `geometric_length`
    - `temporal_delay`
    - `flux_coupling`
    - `directionality_semantics`
    - `geometric_length_mode`
    - signed flux overlay fields when available
- Exported `family_extensions["grcv3"]` now includes:
  - `contract_version = phase_t_iter26_v1`
  - `params_identity`
  - `budget_target`
  - `remainder`
  - `hessian_sign`
  - `backend_summary`
  - `hierarchy_summary`
  - `spark_summary`
  - `choice_summary`
- Implemented representative-runner checkpoint capture in:
  - [src/pygrc/telemetry/experiments.py](../src/pygrc/telemetry/experiments.py)
    - `run_grcv3_representative_experiment(...)`
    - `_run_grcv3_representative_lane(...)`
- The representative runner now mirrors the `GRCV2` checkpoint boundary:
  - opt-in checkpoint recording
  - initial/final cadence support
  - interval/every-step cadence support
  - per-file and chunked storage support through shared recorder/I/O plumbing
- Added representative CLI checkpoint flags in:
  - [scripts/run_grcv3_representative_telemetry.py](../scripts/run_grcv3_representative_telemetry.py)
- Important pre-step checkpoint detail:
  - the representative model now performs a deterministic
    `rebuild_basin_attributes()` + `rebuild_identity_state()` preparation before
    initial checkpoint capture so `hessian_sign` and identity-local summaries
    are honest on saved pre-step artifacts
- Focused validation now covers:
  - direct exporter surface validation
  - representative save/load checkpoint artifacts through the real experiment
    helper

### Verification

- [x] `GRCV3` representative runs can emit checkpoint artifacts without live
      model access in the visualization layer

Verification commands:

- `./.venv/bin/python -m unittest tests.telemetry.test_checkpoints`
- `./.venv/bin/python -m unittest tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/run_grcv3_representative_telemetry.py --outputs-root /tmp/pygrc-grcv3-checkpoint-smoke --lane-name phase_t_iter23_smoke --steps 2 --record-graph-checkpoints --checkpoint-every-n-steps 1 --include-flow-overlays`

### Summary

Closed. `GRCV3` now has a real representative checkpoint-export lane. The
shared checkpoint schema is reused unchanged, representative runs can emit
artifact-backed graph checkpoints through the telemetry boundary, and honest
post-step flow overlays are saved when requested. Export validation now covers
both the direct `GRCV3` checkpoint surface and the real representative
runner/save-load path.

## Iteration 23. GRCV3 Checkpoint-Telemetry Closeout

### Goal

Close the later `GRCV3` checkpoint-telemetry slice and hand it back to Phase V.

### Checks

- [x] Validate saved representative `GRCV3` checkpoint artifacts end-to-end
- [x] Record any still-missing graph/flow surfaces explicitly
- [x] Record the handoff boundary to later `GRCV3` graph visualization work

### Implementation Notes

- This is the point where graph-visible Phase V work becomes justified.
- End-to-end validation basis:
  - representative lane: `phase5_reference`
  - steps: `2`
  - checkpoint cadence: `every_n_steps = 1`
  - flow overlays: enabled
- Artifact-backed validation now confirms:
  - saved representative packs load graph checkpoints without live model state
  - each run emits `3` checkpoints:
    - `initial`
    - `interval`
    - `final`
  - initial checkpoints declare:
    - `flow_representation = not_available_pre_step`
  - post-step checkpoints can declare:
    - `flow_representation = signed_edge_flux`
  - saved checkpoint graph kind is:
    - `weighted_graph`
  - saved checkpoint family extension surface is:
    - `family_extensions["grcv3"]["contract_version"] = phase_t_iter26_v1`
- Still-missing graph/flow surfaces are now explicit:
  - no `GRCV3` graph-visible renderer has been implemented yet
  - the synthetic representative lane does not currently carry ambient chart
    layout hints, so later graph rendering will need an explicit layout policy
  - landscape-seed-driven `GRCV3` checkpoint lanes are still not exported
  - richer hierarchy/spark overlay groups beyond the first checkpoint contract
    remain deferred
- Handoff boundary:
  - telemetry is no longer the blocker for representative `GRCV3` graph-visible
    work
  - the next blocker is Phase V rendering and layout policy on top of these
    saved checkpoint artifacts

### Verification

- [x] The downstream dependency for `GRCV3` graph visualization is satisfied

Verification commands:

- `./.venv/bin/python -m unittest tests.telemetry.test_checkpoints`
- `./.venv/bin/python -m unittest tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/run_grcv3_representative_telemetry.py --outputs-root /tmp/pygrc-grcv3-checkpoint-smoke --lane-name phase_t_iter23_smoke --steps 2 --record-graph-checkpoints --checkpoint-every-n-steps 1 --include-flow-overlays`

### Summary

Closed. The later `GRCV3` checkpoint-telemetry slice is now established for the
representative runtime lane. Saved checkpoint artifacts are deterministic,
loadable without live state, and explicit about both flow availability and
family-local node semantics. The telemetry blocker for later `GRCV3`
graph-visible visualization is now removed; what remains is renderer/layout
work, plus later expansion to landscape-driven and richer overlay surfaces.

## Iteration 24. GRCV3 Landscape Checkpoint Planning Boundary

### Goal

Record the missing final Phase T lane needed to close `GRCV3` graph telemetry
on the real seed-driven `cell-1` / `cell-4` runtime rather than only on the
representative replay lane.

### Checks

- [x] Update the Phase T plan so it names the seed-driven landscape checkpoint
      lane as the remaining `GRCV3` telemetry gap
- [x] Record the intended landscape checkpoint iteration order in this
      checklist
- [x] Record that representative checkpoint telemetry is complete but not
      sufficient for full family closeout

### Implementation Notes

- This is the telemetry-side equivalent of the Phase V representative-versus-
  landscape boundary correction.
- The representative lane remains the checkpoint contract proving ground.
- The remaining family-wide telemetry gap is specifically:
  - `run_grcv3_landscape_experiment(...)`
  - `cell-1`
  - `cell-4`
  - checkpoint artifacts under the shared checkpoint schema

### Verification

- [x] The remaining `GRCV3` telemetry gap is documented precisely
- [x] The next seed-driven checkpoint iterations are explicit

### Summary

Iteration 24 established the final telemetry-side boundary for `GRCV3`.
Representative checkpoint telemetry remained closed, but the seed-driven
landscape checkpoint lane was recorded explicitly as the last missing telemetry
slice before family-wide graph-visible closeout could move back to Phase V.

## Iteration 25. GRCV3 Landscape Checkpoint Export Lane

### Goal

Extend the seed-driven `GRCV3` landscape runtime so real `cell-1` / `cell-4`
runs can emit checkpoint artifacts through the shared telemetry boundary.

### Checks

- [x] Add checkpoint recording options to `run_grcv3_landscape_experiment(...)`
- [x] Export checkpoint topology for the seed-driven `GRCV3` landscape lane
- [x] Export the required node and edge overlays through the shared checkpoint
      schema
- [x] Export honest flow overlays when available
- [x] Add focused checkpoint export tests for the landscape lane

### Implementation Notes

- This should reuse the existing representative-lane checkpoint exporter and
  recorder plumbing where possible.
- The new work is the seed-driven runtime hook, not a second checkpoint schema.
- Extended:
  - [src/pygrc/telemetry/experiments.py](../src/pygrc/telemetry/experiments.py)
    - `run_grcv3_landscape_experiment(...)`
    - `_capture_grcv3_landscape_run(...)`
- The landscape lane now mirrors the representative checkpoint boundary:
  - opt-in checkpoint recording
  - initial/final cadence support
  - interval/every-step cadence support
  - per-file and chunked storage support through shared recorder/I/O plumbing
- Added landscape CLI checkpoint flags in:
  - [scripts/run_grcv3_landscape_telemetry.py](../scripts/run_grcv3_landscape_telemetry.py)
- The checkpoint exporter remains shared:
  - [src/pygrc/models/grc_v3_checkpoints.py](../src/pygrc/models/grc_v3_checkpoints.py)
    - `export_grcv3_graph_checkpoint(...)`
- Focused validation now covers:
  - landscape experiment checkpoint emission
  - landscape script checkpoint emission
  - save/load checkpoint artifacts through the real seed-driven lane

### Verification

- [x] Seed-driven `GRCV3` landscape runs can emit checkpoint artifacts
- [x] Exported landscape checkpoint packs are loadable without live model state

### Summary

Iteration 25 landed the missing checkpoint-export path for the real
seed-driven `GRCV3` lane. `cell-1` / `cell-4` runs can now emit graph
checkpoint artifacts through the shared telemetry boundary without introducing
any family-local checkpoint schema.

## Iteration 26. GRCV3 Landscape Checkpoint Closeout

### Goal

Close the Phase T side of seed-driven `GRCV3` graph telemetry and hand the real
`cell-1` / `cell-4` lane back to Phase V for graph-visible rendering.

### Checks

- [x] Run the seed-driven `GRCV3` landscape telemetry lane with checkpoint
      export enabled
- [x] Verify checkpoint artifact determinism and loadability
- [x] Record any still-missing landscape graph/flow surfaces explicitly
- [x] Record the handoff boundary back to Phase V landscape graph rendering

### Implementation Notes

- This closeout should use the real seed lane rather than the synthetic
  representative replay lane.
- The intended validation basis is:
  - `profile_name = "seed_baseline"` or the then-current truthful default
  - `cell-1`
  - `cell-4`
  - explicit checkpoint cadence and storage mode
- Concrete artifact-backed landscape checkpoint lane executed:
  - `experiment_path = "representative/grcv3_landscape_checkpoint"`
  - `profile_name = "seed_baseline"`
  - `num_steps = 3`
  - `checkpoint_every_step = True`
  - `include_flow_overlays = True`
  - chunked storage selected automatically for dense cadence
  - cell-1 run id:
    - `3f87fb9dbb4e3724d9c3c973b7885ac500bc89304af13eea4caf8e6fe138f823`
  - cell-4 run id:
    - `8046610fa18891bd036ffbcba29bf9e762186f4bcae4bfe34973c7cec75dc5a4`
- Artifact-backed validation confirms:
  - each run emits `4` checkpoints:
    - `initial`
    - `interval`
    - `interval`
    - `final`
  - initial checkpoints declare:
    - `flow_representation = not_available_pre_step`
  - post-step checkpoints declare:
    - `flow_representation = signed_edge_flux`
  - saved checkpoint graph kind is:
    - `weighted_graph`
  - saved checkpoint family extension surface is:
    - `family_extensions["grcv3"]["contract_version"] = phase_t_iter26_v1`
  - chunk-backed artifact layout exists under:
    - `.../telemetry/graph_checkpoints/index.json`
    - `.../telemetry/graph_checkpoints/chunk-00000001.jsonl`
- Still-missing graph/flow surfaces are now narrower:
  - no landscape graph-visible renderer has been enabled yet in Phase V
  - richer hierarchy/spark/choice overlay groups beyond the first checkpoint
    contract remain deferred
- Handoff boundary:
  - telemetry is no longer the blocker for seed-driven `GRCV3` graph-visible
    work
  - at the time of this iteration, the remaining blocker was the Phase V
    landscape graph surface on top of these saved checkpoint artifacts

### Verification

- [x] The downstream telemetry dependency for seed-driven `GRCV3` graph
      visualization is satisfied
- [x] Any remaining richer overlay gaps are explicit rather than implied

Verification commands:

- `./.venv/bin/python -m unittest tests.telemetry.test_checkpoints`
- `./.venv/bin/python -m unittest tests.telemetry.test_experiments`
- `./.venv/bin/python scripts/run_grcv3_landscape_telemetry.py --outputs-root outputs --experiment-path representative/grcv3_landscape_checkpoint --profile seed_baseline --steps 3 --record-graph-checkpoints --checkpoint-every-step --include-flow-overlays`

### Summary

Closed. The final Phase T `GRCV3` landscape checkpoint lane is now established
on real `cell-1` / `cell-4` artifacts. Saved landscape checkpoint artifacts are
deterministic, loadable without live state, and explicit about both flow
availability and family-local node semantics. At the time of this iteration,
the remaining blocker for full `GRCV3` graph-visible closeout was Phase V
landscape rendering rather than telemetry; that visualization-side blocker has
since been closed as well.

## Short Telemetry Caveat

One important `GRCV3` telemetry lesson is that artifact review must stay part of
the semantic validation loop.

Why:

- the model/runtime can look correct while saved event rows still reveal a real
  instrumentation defect
- this happened in `GRCV3` when choice/collapse events were being appended
  twice at runtime-source level before the saved artifacts were rechecked

So the practical rule for later families is:

- do not stop at “tests pass” or “the recorder writes files”
- inspect at least one saved event/report lane directly before declaring the
  telemetry surface closed
