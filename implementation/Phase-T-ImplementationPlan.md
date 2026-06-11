# Phase T Implementation Plan

This document is the detailed execution plan for **Phase T: Telemetry +
Post-Processing**.

Phase T exists because executable runs alone are not enough. After Phase L1,
the project could first run canonical seeds such as `cell-1` and `cell-4`
through `GRCV2`, and after Phase 5 it now also has an executable `GRCV3`
baseline. The project still lacks the experiment-facing telemetry, artifact,
and post-processing surfaces needed to make those runs analytically useful
across families.

The PDE program already demonstrated that telemetry was not optional tooling. It
was part of the method:

- `simulation-v22-cuda.py` exposes step hooks, JSONL telemetry streams,
  run-summary sidecars, and explicit report surfaces,
- `24D-CoherenceLoops-ExperimentationLog.md` relies on report artifacts,
  summaries, comparator outputs, and telemetry-linked evidence rather than
  narrative observation alone.

Phase T should import that lesson directly into `PyGRC`.

It should now be read in two roles:

- the shared telemetry architecture for executable families
- the concrete implementation lane first proven on `GRCV2` and next extended to
  `GRCV3`

## Purpose

Phase T must establish:

- a structured telemetry contract for executable `PyGRC` runs,
- deterministic artifact layout for run traces, summaries, and comparisons,
- post-processing helpers for extracting metrics and building reports,
- and a clean handoff boundary to a later visualization phase.

The goal is not yet to produce polished visuals. The goal is to ensure that
experiment evidence in `PyGRC` comes from structured telemetry and derived
reports rather than from screenshots, ad hoc printouts, or manual inspection.

## Inputs From Earlier Phases

Phase T assumes the following outputs already exist and remain authoritative:

- determinism and serialization guarantees from Phases 0 to 3
- executable `GRCV2` semantics and replay guarantees from Phase 4
- seed-driven `GRCV2` execution from Phase L1:
  - [`Phase-L1-ImplementationPlan.md`](./Phase-L1-ImplementationPlan.md)
  - [`Phase-L1-ImplementationChecklist.md`](./Phase-L1-ImplementationChecklist.md)
- executable `GRCV3` baseline closure from Phase 5:
  - [`GRCV3-Closeout.md`](./GRCV3-Closeout.md)
  - [`Phase-5-StepLoop.md`](./Phase-5-StepLoop.md)
  - [`Phase-5-RepresentativeRuntime.md`](./Phase-5-RepresentativeRuntime.md)
- the PDE experimental references:
  - `rc-sim/simulations/active/simulation-v22-cuda.py`
  - `rc-sim/experiments/papers/24D-CoherenceLoops-ExperimentationLog.md`

Phase T should not silently bypass the existing runtime or serialization
surfaces. Telemetry must be layered on top of the executable model and
reproducible artifact path already established, not implemented as an
independent second runtime.

## Recorded Refactor Follow-On

Phase T now also has a dedicated structural refactor lane for the experiment
surface:

- [Phase-T-ExperimentsRefactorPlan.md](./Phase-T-ExperimentsRefactorPlan.md)
- [Phase-T-ExperimentsRefactorChecklist.md](./Phase-T-ExperimentsRefactorChecklist.md)

That refactor lane is intentionally separate from feature/content work.
Its immediate purpose is to reduce structural drift in:

- `src/pygrc/telemetry/experiments.py`
- `tests/telemetry/test_experiments.py`

The first execution slice is explicitly:

- shared `GRCV3` lane-runner extraction
- plus checkpoint-config consolidation

before any broader module split or public-surface cleanup.

## In Scope

- telemetry schema for step rows, event rows, and run summaries
- recorder/writer support for deterministic telemetry artifacts
- artifact layout for run directories and report outputs
- post-processing helpers for:
  - metric extraction
  - trajectory summarization
  - comparison summaries
  - experiment reports
- telemetry-backed experiment surfaces for executable families, beginning with:
  - seed-driven `GRCV2`
  - representative-runtime `GRCV3`
- explicit boundary to later visualization work

## Agreed Defaults

The following defaults are already chosen for Phase T and should be treated as
the starting contract unless a later iteration records an explicit revision.

### 1. Cross-Family Core Contract First

Phase T started with `GRCV2`, but the telemetry vocabulary must be defined at
the common layer.

That means:

- common run metadata,
- common step-row fields,
- common event-row fields,
- common run-summary fields,
- and explicit family-extension surfaces rather than family-local ad hoc
  payloads.

`GRCV2` is the first implementation lane, not the definition of the whole
contract. `GRCV3` should extend the same telemetry core through explicit
family-extension payloads rather than by inventing a second telemetry dialect.

The current common-versus-family boundary is recorded in
[Phase-T-FamilyExtensionMatrix.md](./Phase-T-FamilyExtensionMatrix.md).

### 2. In-Memory Summary Always, Artifact Writing Opt-In

Executable runs should always be able to return an in-memory telemetry/result
summary suitable for tests, notebooks, or higher-level orchestration.

Writing telemetry artifacts to disk should remain explicit and opt-in.

This preserves a light execution path while keeping artifact production
deterministic when enabled.

### 3. Artifact Format Defaults

The default artifact family for Phase T is:

- JSONL for per-step rows,
- JSONL for per-event rows when event streams are emitted,
- JSON for run summaries,
- JSON for comparison/report sidecars.

This follows the PDE-side experimental pattern and keeps machine-readable
artifacts line-oriented where streaming or incremental inspection matters.

### 4. Run-Directory Layout With Relative, Shareable Paths

Artifact layout should be organized by run directories under a project-relative
root, not by machine-local absolute paths embedded into the contract.

The default expectation is:

- `outputs/experiments` is the project-default experiment-artifact root,
- experiment lanes may add a configuration-owned relative subpath under that
  root,
- generated telemetry/report artifacts under `outputs/` are local run products,
  not repository source,
- if a result needs to be shared across users, the preferred mechanism is a
  reconstruction script or replay recipe that regenerates the same artifacts,
- one run directory per executed run,
- telemetry artifacts under `<run_id>/telemetry/`,
- later visualization artifacts under `<run_id>/visualization/`,
- stable relative filenames inside those directories,
- and metadata that records source/config identities without making the
  repository unshareable.

### 5. Summary-First Comparison

Phase T should prioritize summary and comparison surfaces before any later
visualization layer.

The intended order is:

- step/event traces for auditability,
- run summaries for direct inspection,
- comparison/report payloads for experiment claims,
- visualization later as a consumer of those artifacts.

The current downstream state should be explicit:

- behavior-facing visualization is already possible from saved
  telemetry/report artifacts,
- graph-visible and flow-visible artifacts are available when checkpoint export
  is enabled explicitly,
- the default representative telemetry lane remains behavior-only,
- and future graph/flow visuals should consume optional checkpoint artifacts
  rather than assuming they are present for every run.

### 6. Default Reporting Lane

The first representative reporting lane should use:

- `cell-1`
- `cell-4`
- `balanced_baseline`

This does not make `balanced_baseline` the only supported family, but it is the
default reporting lane that initial telemetry and report examples should target.

Its default artifact surface is intentionally basic:

- step rows
- event rows
- run summaries
- experiment/comparison reports

Graph checkpoint export is optional and must be requested explicitly.

For `GRCV3`, the first representative telemetry lane should be the Phase 5
closeout smoke/reconstruction lane rather than a landscape-driven experiment.
That keeps the next telemetry extension grounded in an already reproducible
runtime baseline before richer phenomenology is added.

### 7. Lightweight Per-Step Scalars By Default

Every recorded step should emit lightweight state/topology scalars by default.

These should include enough information to understand trajectory evolution
without forcing full snapshot persistence at every step.

Full state snapshots should therefore be optional and interval-driven rather
than mandatory on every step.

### 8. Parameter Returnability Is Part Of The Artifact Contract

Telemetry artifacts must preserve enough parameter information to validate the
exact settings under which a run was produced.

The default Phase T rule is:

- if parameters are static for the whole run:
  - store them at the run-summary/report level
- if parameters become dynamic during a run:
  - extend telemetry to include either:
    - step-level effective-parameter identity/deltas, or
    - explicit parameter-change events

Phase T should therefore treat parameter hashes alone as insufficient for full
artifact returnability. Hashes remain useful, but saved artifacts should also
carry the resolved parameter payload needed for audit and replay.

### 9. Visualization Is Downstream Of Telemetry

Visualization is not part of the telemetry contract itself.

Phase T artifacts must stand on their own as experiment evidence and as inputs
to later visual surfaces. Phase V should consume telemetry/report artifacts, not
replace them.

At the current boundary, that means:

- trajectories, event timelines, and report/comparison panels are legitimate
  downstream products of the existing artifact contract,
- graph snapshots, graph-local overlays, and flow visuals are legitimate only
  when checkpoint export was explicitly enabled for the run,
- and absence of checkpoint artifacts should be read as behavior-only capture
  rather than missing telemetry.

### 10. Family Extensions Must Stay Explicit

The telemetry contract should now be read in two layers:

- shared core telemetry semantics
- family-specific telemetry extensions

For `GRCV3`, expected extension surfaces include:

- basin-attribute summaries
- signed-Hessian metadata
- hierarchy summaries
- spark lifecycle summaries
- choice/collapse lifecycle summaries

Those should be added through explicit extension payloads and documented
contracts, not by weakening the shared schema vocabulary.

In the implemented recorder boundary, family extensions may be attached at four
explicit levels:

- shared run-level extensions
- per-step extensions
- per-event extensions
- run-summary extensions

That allows family-local telemetry to vary across the trajectory without
turning model code into telemetry code or forking the shared telemetry dialect.

## Out Of Scope

- polished charting/plot design
- interactive dashboards
- graph animation or video rendering
- full campaign orchestration
- multi-family comparison beyond what telemetry contracts make possible
- machine-driver integration
- redefinition of the shared telemetry core separately for each family

## Phase T Design Constraints

### 1. Telemetry Is Evidence, Not Debug Noise

Phase T should treat telemetry as part of the experiment method.

That means:

- explicit schemas,
- stable field names,
- deterministic output structure,
- and clear report derivation paths.

It must not devolve into:

- freeform logging,
- one-off print statements,
- or undocumented ad hoc JSON blobs.

### 2. Runtime And Telemetry Must Stay Separable

Telemetry should observe and record the run, not redefine the model.

So Phase T must keep separate:

- model execution,
- telemetry capture,
- post-processing,
- and later visualization.

This separation matters because later experiment reports should be reproducible
from saved artifacts without rerunning visualization or touching live model
state.

The same principle applies across families:

- family code owns runtime semantics
- Phase T owns recording and post-processing contracts
- family telemetry extensions should describe family state, not reimplement it

### 3. Deterministic Artifact Layout

For the same:

- seed,
- parameter family,
- overrides,
- RNG seed,
- and step count,

the telemetry artifact structure and summary payloads should be reproducible.

This does not require byte-for-byte equality for every optional output, but it
does require:

- stable schemas,
- deterministic row ordering,
- explicit metadata hashes/identities where relevant,
- and report-generation behavior that does not depend on hidden runtime state.

### 3.1 Parameter Snapshots Must Be Auditable

Saved run artifacts should preserve:

- resolved parameters,
- raw parameters when available,
- and explicit overrides when applied.

This should happen at the run level for static-parameter runs so artifacts can
be audited without consulting external family registries.

### 4. Summary And Comparison Surfaces Come Before Visualization

The PDE references show that experiment work depends on:

- run summaries,
- comparator outputs,
- manifest-like artifacts,
- and report payloads.

Phase T should therefore prioritize:

- telemetry rows,
- summary JSON,
- comparison/report JSON,

before Phase V begins building:

- plots,
- overlays,
- or topology visuals.

### 5. Window/Checkpoint Discipline Should Be Explicit

`24D` repeatedly relies on checkpoints, windows, summary rows, and correspondence
rules across artifacts.

Phase T should encode from the start:

- how step windows are selected,
- how checkpoints are named,
- how summary intervals are configured,
- and how report derivation references those windows.

### 6. Telemetry Must Support Nontrivial Family Growth Later

Phase T starts from `GRCV2`, but the contract should not trap later families.

So the telemetry design should separate:

- common fields that every family can emit,
- family-specific extension fields,
- and report logic that can tolerate richer future families.

The current common-versus-family split is tracked in
[Phase-T-FamilyExtensionMatrix.md](./Phase-T-FamilyExtensionMatrix.md).

## Expected Code Shape After Phase T

The exact split may evolve, but the intended boundary is close to:

```text
src/pygrc/
  telemetry/
    __init__.py
    schema.py
    recorder.py
    io.py
    reports.py
    compare.py
```

Possible tests:

```text
tests/
  telemetry/
```

If some helpers naturally belong near the existing `GRCV2` landscape runner,
they should still delegate to a shared telemetry package rather than creating a
second telemetry vocabulary inside `models/`.

## Workstreams

## 1. Telemetry Contract Boundary

### Tasks

- Define the public telemetry package boundary.
- Decide which telemetry types are common and which are family-extended.
- Fix naming for:
  - step telemetry
  - event telemetry
  - run summary
  - comparison/report outputs

### Required Decisions

- whether telemetry rows are dataclasses, typed dicts, or plain canonical mappings
- how family-specific extensions are represented
- how telemetry contracts align with existing `GRCEvent` and observable surfaces

### Acceptance Criteria

- there is one explicit telemetry vocabulary
- executable runs do not emit undocumented ad hoc payloads
- later families can extend the same contract without renaming basics

## 2. Step And Run Summary Schema

### Tasks

- Define canonical fields for per-step telemetry rows.
- Define run-summary fields derived from full trajectories.
- Define metadata/provenance fields for replay and experiment traceability.

### Required Decisions

- which core observables are always recorded
- which event aggregates are step-level versus summary-level
- how params identity, seed identity, and run identity are represented

### Acceptance Criteria

- step rows and run summaries have explicit schemas
- replay-critical identity fields are included
- summaries can be regenerated from step telemetry deterministically

## 3. Artifact Layout And I/O

### Tasks

- Define deterministic output layout for telemetry artifacts.
- Implement writers/loaders for telemetry rows and summaries.
- Decide how report sidecars and comparison outputs are named.

### Required Decisions

- whether rows use JSONL, canonical JSON arrays, or both
- where run summaries and comparison outputs live
- how artifact layout remains repo-shareable and relative-path-safe

### Acceptance Criteria

- one run can emit a deterministic artifact pack
- artifact readers can restore telemetry/report payloads without live runtime access
- output naming is explicit and documented

## 4. Runtime Recording Hooks

### Tasks

- Record telemetry from executable `GRCV2` seed-driven runs.
- Decide whether capture is:
  - always on in runner helpers
  - optional through configuration
  - or both
- Ensure event and observables surfaces are recorded without mutating semantics.

### Required Decisions

- where recorder hooks are invoked in the runner path
- whether model stepping remains telemetry-agnostic
- what minimum telemetry every run must emit

### Acceptance Criteria

- seed-driven `GRCV2` runs can emit structured step telemetry and run summaries
- telemetry hooks do not alter model behavior
- deterministic replay still holds when telemetry is enabled

## 5. Post-Processing And Reports

### Tasks

- Implement helpers for:
  - summary extraction
  - trajectory aggregation
  - pairwise comparison
  - report JSON generation
- Define first report payloads that mirror PDE-style experiment reasoning.

### Required Decisions

- which report types are phase-minimum
- how comparison metrics are named
- how report payloads cite source artifacts and identities

### Acceptance Criteria

- telemetry artifacts can be transformed into stable report payloads
- comparison/report surfaces are usable without visualization
- representative reports are inspectable and testable

## 6. Representative Experiment Surface

### Tasks

- Use `cell-1` and `cell-4` as the first telemetry-backed experiment lanes.
- Decide what telemetry-backed checks count as meaningful:
  - evolution summaries
  - event/no-event runs
  - family comparison
  - checkpoint comparison

### Required Decisions

- which parameter family is the baseline reporting lane
- which run lengths/checkpoints are canonical for first experiments
- which metrics must appear in first summaries

### Acceptance Criteria

- `cell-1` and `cell-4` produce telemetry artifacts and summaries
- first reports show more than raw observables dumps
- experiment outputs are strong enough to support later comparison work

## 7. Telemetry Validation Gate

### Tasks

- Validate the telemetry phase against the PDE references and current runtime.
- Record remaining limitations explicitly.
- Define the handoff contract to Phase V visualization.
- Make explicit what visible outputs are currently justified by saved artifacts
  and what remains blocked on new checkpoint telemetry.

### Required Decisions

- what telemetry is now authoritative for evidence
- what remains provisional until more families exist
- what visualization is forbidden to infer beyond telemetry
- whether graph-visible output requires new telemetry artifact families rather
  than more Phase V rendering work

### Acceptance Criteria

- the project can claim structured telemetry-backed experimentation for seed-driven runs
- the visualization phase has a stable downstream contract
- telemetry limitations are explicit rather than hidden in plotting code
- the boundary between current behavior-visible output and still-missing
  graph/flow-visible output is explicit

## Suggested Iteration Order

The recommended implementation order is:

1. telemetry package boundary
2. step/run summary schema
3. artifact layout and I/O
4. runtime recording hooks
5. post-processing and report builders
6. representative experiment surface
7. validation gate and Phase V handoff

## Phase T Follow-On: Checkpoint Telemetry Extension

The original seven-iteration Phase T closeout remains historically valid for
the first telemetry/report layer. However, the later Phase V work made one more
requirement explicit:

- graph-visible and flow-visible output cannot be produced honestly until
  telemetry exports checkpoint topology/flow artifacts

That work still belongs to telemetry rather than visualization. The clean
follow-on is therefore an in-place Phase T extension rather than a new phase.

The recommended follow-on implementation order is:

8. graph checkpoint schema
9. recorder and export hooks
10. `GRCV2` checkpoint export
11. flow overlay export
12. checkpoint artifact validation lane
13. dense checkpoint streaming mode

These iterations extend Phase T from:

- telemetry-backed behavior inspection

to:

- telemetry-backed graph/flow artifact export suitable for later Phase V
  rendering

Dense checkpoint mode should **not** be dismissed as a remote optimization.
Sparse checkpoints are enough to establish graph structure and milestone-level
behavior, but they are not enough to study fine temporal evolution. For that
reason, high-cadence checkpoint export belongs to Phase T follow-on work before
serious graph-facing Phase V work resumes.

## Phase T Next Lane: GRCV3 Telemetry Extension

With the shared telemetry core now in place and `GRCV3` closed as an
executable baseline in Phase 5, the next telemetry task is not new
infrastructure from scratch. It is a disciplined extension of the current
Phase T contract to a second family.

This lane should stay narrower than the original `GRCV2` telemetry build:

- reuse the shared telemetry package as-is wherever possible
- add only explicit `GRCV3` family extensions
- prove the extension first on the Phase 5 representative runtime lane
- defer any new graph-checkpoint or visualization-specific work unless the
  existing telemetry core cannot express the required state honestly

The purpose of this lane is to make `GRCV3` analytically inspectable with the
same experimental discipline already available for `GRCV2`, while preserving a
single telemetry dialect across the project.

### GRCV3 Telemetry Scope

This extension lane should cover:

- `GRCV3` family-extension payload design for:
  - step rows
  - event rows
  - run summaries
- runtime capture of `GRCV3`-specific lightweight state summaries
- representative experiment/report helpers for the Phase 5 reference runtime
- artifact-backed validation that `GRCV3` telemetry is deterministic,
  replay-stable, and returnable
- explicit documentation of what remains deferred after the first `GRCV3`
  telemetry slice

This lane should **not** yet assume:

- landscape-seed projector support for `GRCV3`
- `GRCV3` graph-checkpoint export
- `GRCV3`-specific visualization outputs
- multi-family comparison claims beyond what the saved summaries actually
  support

### GRCV3 Telemetry Required Inputs

The `GRCV3` telemetry extension should stay aligned with:

- [`GRCV3-Closeout.md`](./GRCV3-Closeout.md)
- [`Phase-5-StepLoop.md`](./Phase-5-StepLoop.md)
- [`Phase-5-ConstitutiveReview.md`](./Phase-5-ConstitutiveReview.md)
- [`Phase-5-RepresentativeRuntime.md`](./Phase-5-RepresentativeRuntime.md)
- [Phase-T-FamilyExtensionMatrix.md](./Phase-T-FamilyExtensionMatrix.md)

Those Phase 5 records define the executable state surface that telemetry is
allowed to summarize. Phase T should describe that surface, not reinterpret it.

### GRCV3 Extension Workstreams

## A. Family-Extension Contract

### Tasks

- define the initial `GRCV3` extension payloads for step rows, event rows, and
  run summaries
- decide which `GRCV3` quantities are required in the first telemetry slice
- fix the extension-key naming so `GRCV3` data remains clearly separated from
  the shared schema

### Required Decisions

- which basin-attribute summaries are always emitted
- whether `hessian_sign` is recorded per step, per summary, or both
- how hierarchy, spark, and choice/collapse state are compressed into
  lightweight telemetry payloads

### Acceptance Criteria

- the `GRCV3` extension payload surface is explicit before runtime hooks are
  added
- no `GRCV3` telemetry data is smuggled through unnamed bookkeeping blobs
- the same extension naming can be reused by later reports and Phase V
  consumers

## B. Runtime Capture Integration

### Tasks

- wire the `GRCV3` runner/representative runtime path to emit shared telemetry
  rows plus `GRCV3` extensions
- keep the model step loop telemetry-agnostic
- ensure telemetry capture does not modify Phase 5 semantics

### Required Decisions

- where `GRCV3` family extensions are assembled
- whether extension payloads are captured from state, from `StepResult`, or
  from both
- how representative runtime helpers expose telemetry artifacts cleanly

### Acceptance Criteria

- a representative `GRCV3` run can emit shared telemetry artifacts plus
  explicit `GRCV3` extensions
- save/load and replay behavior remain unchanged by telemetry capture
- telemetry does not require special-case logic inside the `GRCV3` step loop

## C. Report And Comparison Surface

### Tasks

- define the first report payloads for `GRCV3`
- ensure trajectory/report helpers can consume `GRCV3` extension payloads
  without redefining the common schema
- decide what the first `GRCV3` comparison surface actually means

### Required Decisions

- whether the first comparison surface is:
  - same-run replay equivalence
  - parameter-lane comparison within `GRCV3`
  - or both
- which `GRCV3` extension summaries belong in the experiment report by default
- which fields remain family-specific and should not leak into the common
  comparison core

### Acceptance Criteria

- `GRCV3` reports are artifact-backed and inspectable without live runtime
- the comparison surface makes a truthful claim rather than a forced
  cross-family comparison
- post-processing helpers do not fork into a separate `GRCV3` reporting stack

## D. Validation And Deferred Boundary

### Tasks

- run a representative `GRCV3` telemetry lane end-to-end
- verify determinism and returnability of the saved artifacts
- record the next deferred items explicitly

### Required Decisions

- which representative runtime lane becomes the default Phase T `GRCV3`
  telemetry example
- which limits are still deferred after the first extension slice
- whether any shared telemetry concepts must change before Phase V resumes

### Acceptance Criteria

- a documented `GRCV3` telemetry lane exists with reproducible artifacts
- deferred work is explicit rather than hidden in TODOs
- the project can proceed to either `GRCV3` checkpoint telemetry or renewed
  visualization work with a stable boundary

### Suggested GRCV3 Iteration Order

After the completed Phase T iterations for `GRCV2` and shared checkpoint
telemetry, the recommended `GRCV3` extension order is:

15. `GRCV3` telemetry planning boundary
16. `GRCV3` family-extension schema and payload design
17. `GRCV3` runtime capture integration
18. `GRCV3` representative experiment/report surface
19. `GRCV3` validation and deferred-boundary closeout

That closes the minimal behavior-facing telemetry lane only. The intended next
cross-phase sequence after Iteration 19 is:

1. Phase V behavior-facing `GRCV3` visualization from the saved minimal
   telemetry lane
2. a later Phase T follow-on for `GRCV3` checkpoint telemetry
3. a later Phase V follow-on for `GRCV3` graph-visible visualization

Recorded outcome:

- all three later follow-ons are now implemented
- behavior-facing `GRCV3` visualization is closed on real `cell-1` / `cell-4`
  artifacts
- representative `GRCV3` checkpoint telemetry and graph visualization are
  closed
- seed-driven `GRCV3` landscape checkpoint telemetry and graph visualization
  are also closed
- the remaining open `GRCV3` work is therefore no longer telemetry/visualization
  infrastructure, but projector-side and `GRCL-v3` semantic work

## Phase T Later Follow-On: GRCV3 Checkpoint Telemetry

After the current behavior-facing Phase V lane is complete, the next telemetry
extension for `GRCV3` should be checkpoint telemetry rather than more minimal
step/report work.

This later follow-on should cover:

- graph-checkpoint schema reuse or extension for `GRCV3`
- family-aware `GRCV3` checkpoint export hooks
- optional flow-overlay export when the saved surface is honest
- representative validation of saved checkpoint artifacts for `GRCV3`

It should **not** be started until the current behavior-facing visualization
lane has first made the existing `GRCV3` results visible.

### Suggested Later GRCV3 Checkpoint Iteration Order

20. `GRCV3` checkpoint-telemetry planning boundary
21. `GRCV3` checkpoint export contract and family-extension mapping
22. `GRCV3` representative checkpoint export lane
23. `GRCV3` checkpoint-telemetry validation and closeout

Recorded outcome:

- the later representative `GRCV3` checkpoint lane is now implemented
- the representative runtime can export checkpoint artifacts through the shared
  telemetry boundary with:
  - weighted-graph topology
  - `GRCV3` node semantics
  - honest flow overlays when available
  - explicit `grcv3` family checkpoint extensions
- the remaining blocker for graph-visible `GRCV3` work is therefore no longer
  checkpoint telemetry itself, but later rendering/layout policy and any richer
  family-specific overlay surfaces

That representative outcome was later extended to the seed-driven `cell-1` /
`cell-4` landscape lane as well, so checkpoint telemetry is now closed for both
the representative and landscape `GRCV3` evidence lanes.

The intended dense-mode design direction is:

- build one checkpoint artifact in memory at a time,
- hand it off immediately to a retention sink,
- default to streaming/chunked persistence rather than retaining the full run in
  memory,
- and keep cadence separate from retention policy.

In other words:

- `every_step` checkpoint capture may arrive before graph rendering expands,
- but it should be implemented as telemetry infrastructure, not as a
  visualization workaround.

This follow-on is now implemented for the first family:

- cadence and storage are separated explicitly,
- dense cadence is available through `every_step`,
- dense storage is available through chunked JSONL checkpoint persistence,
- sparse one-file-per-checkpoint storage remains available for milestone
  inspection,

## Phase T Final GRCV3 Follow-On: Landscape Checkpoint Telemetry

To close `GRCV3` end to end rather than only on the representative lane, Phase
T still needs one more family-local checkpoint follow-on for the seed-driven
landscape runtime.

This final follow-on should cover:

- seed-driven `cell-1` / `cell-4` `GRCV3` checkpoint export through
  `run_grcv3_landscape_experiment(...)`
- reuse of the shared checkpoint schema for landscape-driven `GRCV3` runs
- honest landscape-lane flow overlays when the saved surface supports them
- representative cell-pair validation of saved checkpoint artifacts for the
  real seed lane
- explicit handoff back to Phase V landscape graph rendering

It should stay aligned with the already landed representative checkpoint lane:

- same checkpoint schema and recorder boundary
- same opt-in cadence/storage controls
- same explicit separation between behavior-only telemetry and checkpoint-backed
  graph telemetry

### Suggested Final GRCV3 Landscape Checkpoint Iteration Order

24. `GRCV3` landscape checkpoint-telemetry planning boundary
25. `GRCV3` landscape checkpoint export lane
26. `GRCV3` landscape checkpoint validation and closeout

Acceptance focus:

- the real seed-driven `cell-1` / `cell-4` lane can emit checkpoint artifacts
  without live model access in the visualization layer
- saved landscape checkpoint packs are deterministic and loadable
- the remaining blocker for full `GRCV3` graph-visible closeout moves from
  Phase T to Phase V rather than remaining ambiguous

Recorded outcome:

- the final seed-driven `GRCV3` landscape checkpoint lane is now implemented
- `run_grcv3_landscape_experiment(...)` can export checkpoint artifacts through
  the shared telemetry boundary with:
  - weighted-graph topology
  - `GRCV3` node semantics
  - honest post-step flow overlays when requested
  - explicit `grcv3` family checkpoint extensions
- the real `cell-1` / `cell-4` lane now has loadable checkpoint artifacts
  under the shared schema
- the remaining blocker identified at that stage was later closed in Phase V,
  so full `GRCV3` telemetry-plus-visualization closeout is now complete

The implemented landscape lane also preserves the already chosen dense-mode
discipline:

- cadence and storage remain separate,
- `every_step` capture can stream through chunked JSONL storage,
- and the run does not need to retain the whole checkpoint history in memory.

## Exit Criteria

Phase T is complete when:

- seed-driven `GRCV2` runs emit structured deterministic telemetry artifacts
- those artifacts can be loaded and summarized without live runtime state
- representative `cell-1` / `cell-4` runs produce summary/report outputs
- visualization can begin downstream of a stable telemetry/report contract
- and it is explicit that graph-visible output still depends on future
  checkpoint topology/flow telemetry extensions

At that point, `PyGRC` has moved from “runnable” to “experiment-capable” for
the first family.

The checkpoint-telemetry follow-on closes only when:

- graph checkpoint schemas and save/load support exist
- recorder/config surfaces can emit checkpoint artifacts deterministically
- `GRCV2` can export checkpoint topology and overlays
- flow overlays are exported under an explicit signed/surrogate contract
- and representative runs produce real graph/flow checkpoint artifacts that
  Phase V can consume without touching live model state

If dense cadence is required for graph-evolution study, an additional
follow-on closeout should also ensure:

- `every_step` or equivalently dense checkpoint export is supported,
- dense export uses bounded-memory streaming/chunking rather than full-run
  retention by default,
- and dense-mode artifacts remain loadable and reconstructable without live
  model state.

Those dense-mode closeout conditions are now satisfied for `GRCV2`.
