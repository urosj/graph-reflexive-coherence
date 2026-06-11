# Phase T Telemetry Experiments Refactor Plan

## Purpose

This note records the structural refactor plan for the telemetry experiment
surface.

Its purpose is not to redesign `GRCV2` or `GRCV3` semantics.
Its purpose is to make the Phase T experiment layer easier to navigate, safer
to extend, and less prone to copy-paste drift.

The immediate trigger is the current growth of:

- `src/pygrc/telemetry/experiments.py`
- `tests/telemetry/test_experiments.py`

into large multi-concern files that now carry:

- experiment orchestration,
- trace construction,
- diagnostic interpretation,
- telemetry extension assembly,
- checkpoint/run-loop logic,
- script-facing helpers,
- and test-side script loading plus validation patterns

inside one flat surface.

## Problem Statement

The current experiment layer is working, but its structure is now the problem.

The main source file has accumulated:

- public experiment entry points,
- many private trace builders,
- duplicated lane-execution logic,
- telemetry extension builders,
- result dataclasses,
- utility functions,
- and a growing set of defaults/constants

without stable module boundaries.

The main test file has mirrored the same growth:

- one monolithic test class,
- many repeated script loader helpers,
- repeated script validation/emission patterns,
- and mixed representative, landscape, settlement, and collapse concerns in one
  file

If this continues, each new telemetry trace or experiment helper will make:

- the source harder to reason about,
- the test file harder to maintain,
- and refactors riskier because structural changes are not localized.

## Scope

### In Scope

- `src/pygrc/telemetry/experiments.py`
- `src/pygrc/telemetry/__init__.py`
- new private telemetry helper modules under `src/pygrc/telemetry/`
- `tests/telemetry/test_experiments.py`
- new test modules/helpers under `tests/telemetry/`
- implementation notes/checklists documenting the refactor

### Out Of Scope

- changing telemetry schema semantics
- changing saved artifact meaning
- changing `GRCV2` or `GRCV3` runtime equations
- changing the already-recorded `GRCL-v3` phenomenology conclusions
- changing script behavior merely to “fit” a refactor

## Boundary Rules

The refactor should preserve these rules.

### 1. Public Behavior Stays Stable First

The initial refactor target is internal structure.

That means:

- existing public functions in `pygrc.telemetry.experiments` should keep working
- existing script entrypoints should keep working
- `pygrc.telemetry` re-exports should remain stable during the first pass

If the public surface is later reduced, that should happen only after internal
seams are stable and documented.

### 2. Non-Negotiable Refactor Invariants

The following must **not** change as a side effect of the structural refactor
unless a later iteration explicitly reopens them as separate work:

- the meaning of emitted telemetry rows, summaries, and trace payloads
- checkpoint artifact semantics, filenames, and indexing behavior
- script CLI behavior and parameter meaning
- the top-level return shapes of public experiment/trace helpers
- the structure of public experiment result dataclasses currently exposed through
  `__all__`, including:
  - `GRCV2RepresentativeExperimentResult`
  - `GRCV3RepresentativeExperimentResult`
  - `GRCV3RepresentativeRunResult`
  - `GRCV3LandscapeExperimentResult`
- the saved-artefact interpretation already used by current docs/tests
- `GRCV2` / `GRCV3` runtime behavior
- the already-recorded `GRCL-v3` phenomenology conclusions derived from those
  artifacts

More concretely, the refactor must not:

- rename or silently drop public experiment functions during the early stages
- change default experiment seeds/profiles/step counts merely to make tests pass
- change JSON field names or nested trace shape merely for internal neatness
- change checkpoint cadence semantics or when checkpoints are recorded
- change script output contracts merely because helpers moved
- “fix” diagnostics by changing interpretation strings without a separate
  content-facing justification

If any of those need to change, the work is no longer a pure structural
refactor and must be recorded as a separate decision.

### 3. Behavioral Parity Beats File Purity

During the first refactor stages, prefer temporary re-export indirection over a
cleaner-looking but behavior-breaking split.

That means:

- private modules may be introduced before public modules are simplified
- wrapper functions may remain temporarily if they preserve the public surface
- duplicated code should be reduced deliberately, but not at the cost of hidden
  semantic changes

### 4. `experiments.py` Becomes A Facade, Not A Dumping Ground

The long-term target is:

- `experiments.py` remains the public experiment surface
- but most implementation moves behind explicit private helpers/modules

This avoids breaking imports while still restoring file-level structure.

### 5. Structural Refactor Comes Before API Cleanup

The first step should not be:

- broad public API redesign
- `Enum` conversion everywhere
- or mass renaming of trace helpers

The first step should be:

- isolate duplicated execution logic,
- isolate checkpoint configuration,
- isolate extension-building logic,
- then split trace families behind those stable seams

### 6. Test Refactor Must Track Source Refactor

Do not treat the test file as separate cleanup.

If source concerns are split, the tests should follow the same concern
boundaries so that ownership remains visible.

### 7. Every Iteration Must State Its Preserved Boundaries

For each execution iteration, record explicitly:

- which public surfaces are expected to remain byte-for-byte or shape-for-shape
  compatible
- which tests/scripts are the parity checks for that claim
- and whether any observed change is structural only or content-affecting

If an iteration cannot state those boundaries clearly, it is too large.

## Target Architecture

The target shape should be explicit.

### Lane A. Public Experiment Facade

Likely file:

- `src/pygrc/telemetry/experiments.py`

Responsibilities:

- public dataclass/result types, or re-exports of them
- public experiment entry points
- public trace entry points
- stable re-export surface for scripts/tests

### Lane B. Shared Lane Execution Helpers

Private module(s), for example:

- `src/pygrc/telemetry/_lane_runner.py`
- `src/pygrc/telemetry/_checkpointing.py`

Responsibilities:

- checkpoint config dataclass(es)
- shared `GRCV3` lane step loop
- factory/callback inputs for the parts that differ between representative and
  landscape execution:
  - model bootstrapping
  - initial observables
  - step-result sourcing
  - optional transient landscape observability builders
- checkpoint decision logic
- event-count accumulation
- graph checkpoint indexing
- telemetry capture assembly shared by representative and landscape runs

### Lane C. Extension Builders

Private module, for example:

- `src/pygrc/telemetry/_grcv3_extensions.py`

Responsibilities:

- `GRCV3` step extension building
- run-summary extension building
- basin/spark/hierarchy/choice/lifecycle helpers
- backend/signature summary helpers

The contract module should stay declarative rather than absorbing these
builders.

These builder extractions should move their cohesive helper surface with them,
including utility functions such as:

- signed-Hessian/vector helpers
- observed interior-site builders
- monitoring-context helpers

If a helper is only used by the extension-builder cluster, it should move with
that cluster rather than remain stranded in `experiments.py`.

### Lane D. Trace Family Modules

Private modules, likely grouped by concern:

- failure / candidate traces
- settlement / reentry traces
- collapse traces

The exact filenames matter less than keeping each family internally coherent.

One additional shared layer is likely needed:

- a private trace-utility module for helpers genuinely shared across settlement,
  reentry, and collapse traces

Examples include:

- realized-key lookup helpers
- node snapshot cache helpers
- event-anchor / event-locus site summaries
- split-descendant collection helpers

Those should not remain interleaved arbitrarily between family modules.

### Lane E. Test Modules By Concern

Likely split:

- representative experiment tests
- landscape experiment tests
- failure/candidate trace tests
- settlement trace tests
- collapse trace tests
- script entrypoint tests

Shared test helpers should move into private test modules instead of being
repeated in one giant class.

## Refactor Priorities

### P0. Shared Run Loop + Checkpoint Config

This is the best first seam.

Why:

- it removes duplicated behaviorally critical code
- it lowers risk for later file splitting
- it aligns directly with the existing Phase T checkpoint/window discipline

Required result:

- representative and landscape `GRCV3` runs share one internal lane runner
- checkpoint parameters are carried through an internal config object rather
  than repeated argument clusters
- the shared runner is callback/factory-driven rather than assuming identical
  model bootstrap semantics

### P0. Extension Builder Extraction

This is the second seam.

Why:

- the builder cluster is already cohesive
- it is largely orthogonal to trace-family logic
- it lets `experiments.py` stop mixing orchestration and payload construction

Required result:

- `GRCV3` extension-building helpers live in a private helper module
- public traces and runs keep using the same returned payload shapes

### P1. Trace Family Module Split

Once the shared seams exist, the trace families can move out cleanly.

Required result:

- failure/candidate logic is grouped
- settlement/reentry logic is grouped
- collapse logic is grouped
- `experiments.py` remains the public entry facade

### P1. Test Surface Split

The source refactor is incomplete if the tests remain one monolith.

Required result:

- `test_experiments.py` is decomposed into multiple concern-shaped modules, or
  the same effect is achieved through clearly separated classes plus helpers
- repeated script loader logic is centralized
- repeated script validation/emission patterns use shared helpers or
  parameterized/subtest-style structure

### P2. Public Surface Cleanup

Only after the internal refactor is stable:

- reconsider which `DEFAULT_*` constants belong in `__all__`
- consider moving result types into a dedicated module
- consider narrower config/result dataclasses for public APIs
- consider `Enum` conversion for diagnostic outcomes if it improves clarity more
  than it adds churn

## Proposed Execution Stages

### Stage 1. Execution Boundary Extraction

Create:

- an internal `GRCV3` checkpoint config object
- a shared internal lane runner for representative/landscape execution

Acceptance:

- duplicate run-loop logic is removed or reduced to thin wrappers
- checkpoint cadence/storage decisions are centralized
- the shared runner is parameterized by factory/callback inputs for the known
  representative-vs-landscape differences
- existing representative/landscape tests still pass

### Stage 2. Extension Builder Extraction

Move the `GRCV3` extension-building cluster into a private helper module.

Acceptance:

- `experiments.py` no longer owns low-level extension assembly directly
- emitted telemetry payload shapes remain unchanged

### Stage 3. Trace Family Partition

Move trace families behind private concern-based modules.

Acceptance:

- the public trace functions still exist
- internal grouping is clear by concern
- shared trace utilities have an explicit home rather than remaining
  opportunistically interleaved
- the file size and responsibility of `experiments.py` drop materially

### Stage 4. Test Partition

Split the experiments test surface by concern and centralize repeated script
test helpers.

Acceptance:

- no single test file owns the whole experiment surface
- the pre-split discovered test inventory is recorded and used as the parity
  baseline
- every original test id has a one-to-one destination or an explicit documented
  replacement map
- script validation/emission logic is not repeated dozens of times
- helper loading logic is centralized
- repeated script tests are driven by shared helper or parameterized/subtest
  structure rather than copy-paste pairs
- the first migration pass preserves the same assertions and public entry-point
  coverage before any further deduplication

Discipline:

- treat the first pass as relocation, not redesign
- move test bodies with the same names, inputs, and assertions first
- only introduce table-driven/script-helper deduplication after discovery and
  coverage parity are already proven
- do not delete the old monolithic test file until the post-split inventory
  matches the pre-split baseline, or every intentional difference is recorded

Recommended execution slices:

- `4A. Test Inventory And Relocation Baseline`
  - record the discovered test inventory
  - create the one-to-one migration map
  - split the monolithic file into concern-shaped files/classes
  - keep names, inputs, and assertions unchanged on this first move
  - current closure:
    - use a concern-shaped class partition inside
      `tests/telemetry/test_experiments.py` as the lowest-risk relocation
      baseline
    - preserve the full `64`-test discovery surface before any helper
      consolidation or script deduplication
- `4B. Shared Loader And Fixture Consolidation`
  - centralize script loader helpers
  - move shared seed/script constants or fixture setup into explicit helpers
  - keep discovery parity and public entry-point coverage unchanged
  - current closure:
    - extract the shared seed/script block into a private test support module
    - keep `test_experiments.py` as the discovered test surface until
      Iteration 4C changes internal script-test structure deliberately
- `4C. Script Test Deduplication`
  - replace repeated script validation/emission pairs with shared table-driven
    or `subTest` structure
  - only after `4A` and `4B` already prove relocation parity
  - current closure:
    - keep the same discovered script-test ids while generating them from a
      shared spec table
    - treat any helper bug found during the first full pass as a refactor bug
      to fix before recording closure

### Stage 5. Surface Cleanup Review

Review what should remain public after the structural split stabilizes.

Acceptance:

- public exports are deliberate rather than incidental
- helper placement is clearer
- `DEFAULT_*` constant placement and export status are reviewed deliberately
- remaining debt is recorded explicitly if not addressed

Current closure:

- keep `src/pygrc/telemetry/experiments.py` as the public facade
- move defaults and result types into private modules with re-exports for
  compatibility
- make `experiments.py` `__all__` complete and intentional rather than leaving
  a stale partial subset
- defer any compatibility-breaking shrink of the package-root default surface

## Suggested Verification

At minimum, the refactor should continue to prove:

1. representative `GRCV2` experiments still run
2. representative `GRCV3` experiments still run
3. landscape `GRCV3` experiments still run
4. existing trace helpers still emit the same top-level shapes expected by tests
5. script entrypoints still validate parameters and emit traces

The first execution slice should favor:

- targeted `unittest` coverage for the shared runner boundary
- then the existing representative/landscape tests
- then the relevant trace/script tests affected by each extraction

## Failure Interpretation

If the first refactor stage cannot extract the shared lane runner cleanly, that
would be an important design signal:

- either the representative and landscape execution surfaces have hidden
  semantic divergence that should be made explicit
- or the current function boundaries are still too entangled for a safe split

In either case, the right response would be:

- record the blocking coupling explicitly,
- then refactor toward a cleaner execution boundary,
- not skip directly to cosmetic module shuffling

## Execution Tracker

Use:

- [Phase-T-ExperimentsRefactorChecklist.md](./Phase-T-ExperimentsRefactorChecklist.md)

as the execution log for this refactor.
