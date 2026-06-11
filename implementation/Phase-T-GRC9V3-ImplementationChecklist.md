# Phase T GRC9V3 Implementation Checklist

This document tracks execution of **Phase T-GRC9V3: GRC9V3 Hybrid Telemetry
Extension**.

## Usage Rules

- Keep core Phase 7 closed. This phase adds telemetry, not runtime equations.
- Preserve the GRC9 / GRCV3 / GRC9V3 ownership boundary in every payload.
- Use `family_extensions["grc9v3"]`; do not overload `grc9` or `grcv3`.
- Use contract version `phase_t_grc9v3_iter1_v1`.
- Keep the Phase 7 representative runtime lane as source evidence, not as the
  telemetry lane itself.
- Put detailed graph state in checkpoints; keep step rows and summaries
  compressed.
- Mark unavailable theory-facing surfaces as `reserved_future` or
  `out_of_scope`.

Post-Lane-B note:

- Lane B `grc9v3_column_h_assisted` is now a core opt-in spark lane.
- Phase T event, step, and checkpoint surfaces already carry Lane B candidate
  evidence.
- Backend/config telemetry now records `spark_lane`, so lane selection is
  visible even before a candidate fires.

## Iteration 0. Planning And Contract Bootstrap

### Goal

Create the Phase T-GRC9V3 plan, checklist, and telemetry contract.

### Checks

- [x] Create `Phase-T-GRC9V3-ImplementationPlan.md`
- [x] Create `Phase-T-GRC9V3-ImplementationChecklist.md`
- [x] Create `Phase-T-GRC9V3-TelemetryContract.md`
- [x] Set family key:
  - `grc9v3`
- [x] Set contract version:
  - `phase_t_grc9v3_iter1_v1`
- [x] Record relationship to Phase 7 closeout
- [x] Record relationship to parent GRC9 and GRCV3 telemetry contracts
- [x] Record representative telemetry as an early implementation workstream
- [x] Record downstream boundaries:
  - Phase V-GRC9V3
  - phenomenology discovery
  - reviewed motif catalogs
  - GRCL/source-seed lowering

### Verification

- [x] Plan/checklist/contract docs exist
- [x] Contract preserves parent/hybrid ownership boundary
- [x] Contract records step, event, run-summary, and checkpoint payload groups

### Summary

Phase T-GRC9V3 is bootstrapped as a telemetry extension over the completed
Phase 7 runtime. The first contract is document-level only; typed code
implementation starts in Iteration 1.

## Iteration 1. Typed Contract Module

### Goal

Implement the typed telemetry contract surface.

### Checks

- [x] Add `src/pygrc/telemetry/grc9v3_contract.py`
- [x] Export family key and contract version
- [x] Add dataclasses for all step groups
- [x] Add dataclasses for all event groups
- [x] Add dataclasses for all run-summary groups
- [x] Add wrapper helpers:
  - `grc9v3_step_family_extensions(...)`
  - `grc9v3_event_family_extensions(...)`
  - `grc9v3_run_summary_family_extensions(...)`
- [x] Add event classifier:
  - `classify_grc9v3_event_extension(...)`
- [x] Export public symbols from `src/pygrc/telemetry/__init__.py`

### Verification

- [x] Add `tests/telemetry/test_grc9v3_contract.py`
- [x] Validate required fields
- [x] Validate enum/status fields
- [x] Validate unknown event kinds classify to `other` / `other`
- [x] JSON round-trip payloads

### Summary

Implemented the typed GRC9V3 telemetry contract module:

- `src/pygrc/telemetry/grc9v3_contract.py`
- exports in `src/pygrc/telemetry/__init__.py`
- `tests/telemetry/test_grc9v3_contract.py`

The module defines `phase_t_grc9v3_iter1_v1`, wraps payloads under
`family_extensions["grc9v3"]`, validates step/event/run-summary dataclasses,
classifies Phase 7 event kinds with explicit ownership, and defaults unknown
events to `other` / `other`.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_contract
```

Result: 6 tests OK.

## Iteration 2. Step Extension Builders

### Goal

Build per-step `family_extensions["grc9v3"]` payloads from live `GRC9V3` state.

### Checks

- [x] Add `src/pygrc/telemetry/_grc9v3_extensions.py`
- [x] Build `backend_config`
- [x] Build `port_chart`
- [x] Build `row_basis_differential`
- [x] Build `hybrid_tensor`
- [x] Build `transport`
- [x] Build `identity_basin`
- [x] Build `hybrid_spark_state`
- [x] Build `hierarchy_state`
- [x] Build `choice_collapse`
- [x] Build `growth_state`
- [x] Build `budget_correction`
- [x] Build `coarse_cache`

### Verification

- [x] Deterministic builder output
- [x] JSON round-trip
- [x] No model state mutation
- [x] Empty/missing caches produce explicit availability fields

### Summary

Implemented `src/pygrc/telemetry/_grc9v3_extensions.py` with a read-only
step extension builder for `family_extensions["grc9v3"]`. The builder compresses
live Phase 7 state into the Iteration 1 contract groups, including backend
configuration, port-chart occupancy, row-basis differential diagnostics,
hybrid tensor summaries, transport labels, identity/basin state, spark and
hierarchy state, choice/collapse state, growth state, quadrature budget closure,
and coarse-cache hygiene.

Added `tests/telemetry/test_grc9v3_extensions.py` to cover deterministic
builder output, JSON round-trip through step rows, no state mutation, explicit
availability fields for missing caches, and weighted-Hessian backend availability.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_extensions
```

Result: 3 tests OK.

## Iteration 3. Event Extension Builders

### Goal

Classify and enrich `GRC9V3` event rows.

### Checks

- [x] Classify hybrid spark candidates
- [x] Classify mechanical expansion events
- [x] Classify completed hybrid sparks
- [x] Classify choice events
- [x] Classify collapse events
- [x] Classify growth events
- [x] Include evidence groups from raw event payloads
- [x] Preserve raw event kind separately from taxonomy

### Verification

- [x] Event-row extension count matches raw events
- [x] Expansion evidence includes module and budget fields
- [x] Completed spark evidence includes stabilized child fields
- [x] Choice/collapse evidence includes sink/score fields

### Summary

Implemented `_build_grc9v3_event_extension(...)` and
`_build_grc9v3_event_extensions(...)` in
`src/pygrc/telemetry/_grc9v3_extensions.py`. The builders delegate taxonomy and
evidence construction to the typed contract classifier while preserving raw
runtime event kind on the canonical event row.

Extended `tests/telemetry/test_grc9v3_extensions.py` to verify representative
event taxonomy for hybrid spark candidate, mechanical expansion, completed
spark, choice, and collapse events; synthetic coverage for choice-resolved,
growth, and unknown events; and the Iteration 2 reserved boundary-mode
non-claim field.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_extensions
```

Result: 5 tests OK.

## Iteration 4. Run Summary Builders

### Goal

Emit fixed-width run-summary extensions.

### Checks

- [x] Add lifecycle event counts
- [x] Add final backend summary
- [x] Add final port/differential/identity/hierarchy summaries
- [x] Add final choice/collapse summary
- [x] Add final budget summary
- [x] Add representative Appendix E summary when fixture matches
- [x] Include replay determinism fields when available

### Verification

- [x] Event rows and lifecycle counts agree
- [x] Final summaries match final model state
- [x] Appendix E summary identifies two daughter sinks for representative lane

### Summary

Implemented `_build_grc9v3_run_summary_extension(...)` in
`src/pygrc/telemetry/_grc9v3_extensions.py`. The run-summary builder reuses the
final step builders for backend, port, differential, identity/basin, hierarchy,
choice/collapse, and budget surfaces; derives fixed lifecycle event counts from
the captured `StepResult` sequence; and emits the Appendix E representative
summary for the `appendix_e_cell_division` fixture when completed-spark evidence
is present.

Extended `tests/telemetry/test_grc9v3_extensions.py` to verify lifecycle counts,
final-state summary agreement, Appendix E daughter sinks `(12, 16)`, budget
preservation, and replay-digest status propagation.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_extensions
```

Result: 6 tests OK.

## Iteration 5. Representative Telemetry Lane

### Goal

Produce artifact-backed representative GRC9V3 telemetry.

### Checks

- [x] Add representative telemetry runner or extend existing experiment runner
- [x] Reuse the Phase 7 `appendix_e_cell_division` fixture
- [x] Write artifacts under a Phase T-GRC9V3-specific output path
- [x] Capture steps, events, run summary, report, snapshots, and checkpoints
- [x] Record replay command in `Phase-T-GRC9V3-RepresentativeTelemetry.md`
- [x] Verify replay step rows, event rows, and final digest match

### Verification

- [x] Representative telemetry artifacts exist
- [x] `family_extensions["grc9v3"]` appears on step rows
- [x] `family_extensions["grc9v3"]` appears on event rows
- [x] run summary has `family_extensions["grc9v3"]`
- [x] representative lane remains distinct from Phase 7 runtime evidence

### Summary

Implemented `scripts/run_grc9v3_representative_telemetry.py` and
`implementation/Phase-T-GRC9V3-RepresentativeTelemetry.md`.

The runner reuses the Phase 7 `appendix_e_cell_division` fixture, emits standard
telemetry artifacts with `family_extensions["grc9v3"]`, writes initial/final
snapshots, captures basic `port_graph` checkpoints, writes an experiment report,
and verifies replay step rows, event rows, and final snapshot digest.

Current artifact root:

```text
outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98/
```

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_representative_telemetry
PYTHONPATH=src ./.venv/bin/python scripts/run_grc9v3_representative_telemetry.py --outputs-root outputs --steps 3
```

Results:

- representative telemetry test: 1 test OK
- artifact run: 3 step rows, 7 event rows, 4 graph checkpoints
- replay step rows match: true
- replay event rows match: true
- replay final digest match: true

## Iteration 6. Graph Checkpoint Extensions

### Goal

Add optional GRC9V3 checkpoint overlays.

### Checks

- [x] Add node overlay
- [x] Add port overlay
- [x] Add edge overlay
- [x] Add module overlay
- [x] Add choice overlay
- [x] Keep checkpoint overlays optional

### Verification

- [x] Checkpoint index links to captured steps
- [x] Overlay payloads are deterministic
- [x] Full detail stays out of step rows

### Summary

Extended `scripts/run_grc9v3_representative_telemetry.py` so graph
checkpoints carry optional `family_extensions["grc9v3"]` overlay payloads:

- `node_overlay`
- `port_overlay`
- `edge_overlay`
- `module_overlay`
- `choice_overlay`

The overlays are enabled by default and can be disabled with
`--disable-checkpoint-overlays`. The checkpoint index still links the initial
and every-step checkpoints to captured step indices `(0, 1, 2, 3)`, and detailed
node/port/edge/module/choice state remains in graph checkpoints rather than step
rows.

Updated `implementation/Phase-T-GRC9V3-RepresentativeTelemetry.md` and
regenerated the representative artifact run. The current run has overlay status
`enabled` on graph checkpoints.

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_representative_telemetry
```

Result: 3 tests OK.

## Iteration 7. Closeout

### Goal

Close Phase T-GRC9V3 and prepare for Phase V-GRC9V3.

### Checks

- [x] Create `Phase-T-GRC9V3-Closeout.md`
- [x] Record implemented telemetry contract
- [x] Record representative telemetry evidence
- [x] Record deferred downstream surfaces
- [x] State Phase V-GRC9V3 as the next visualization layer

### Verification

- [x] Contract tests pass
- [x] Builder tests pass
- [x] Representative replay tests pass
- [x] Closeout preserves parent/hybrid ownership boundaries

### Summary

Created `implementation/Phase-T-GRC9V3-Closeout.md`.

The closeout records:

- family key `grc9v3`
- contract version `phase_t_grc9v3_iter1_v1`
- typed contract and builder modules
- representative telemetry artifact root
- replay step/event/digest checks
- checkpoint overlay status
- parent/hybrid ownership boundary
- deferred Phase V / discovery / GRCL surfaces
- Phase V-GRC9V3 as the next visualization layer

Verification command:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grc9v3_representative_telemetry tests.telemetry.test_grc9_extensions tests.telemetry.test_grcv3_contract
```

Result: 37 tests OK.

## Post-Closeout Lane B Telemetry Catch-Up

### Goal

Record the telemetry interpretation updates required after core Lane B
implementation.

### Checks

- [x] Record that Lane B is now `grc9v3_column_h_assisted`, not a future-only
  concept.
- [x] Record that `hybrid_spark_candidate` is a shared event kind and
  `payload.spark_lane` distinguishes Lane A from Lane B.
- [x] Record that candidate payloads and checkpoint overlays are the primary
  Lane B causal and visual-inspection surfaces.
- [x] Record that `column_h_branch_hit` means the column-H proxy branch fired,
  while `lane_b_candidate_hit` means the full Lane B predicate fired.
- [x] Record that `H_s[b]` remains a proxy even when the branch is direct
  runtime evidence.
- [x] Add `spark_lane` to backend/config telemetry so lane selection is visible
  before candidate events.
- [x] Add or update tests for backend/config `spark_lane` once implemented.

### Summary

The Lane B telemetry payload path is implemented through event, step, and
checkpoint evidence. Backend/config telemetry now records `spark_lane` for
both default Lane A and opt-in Lane B runs, and records `spark_lane_version`
for Lane B v1. This closes the configuration-visibility gap for runs where no
candidate event has yet appeared.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions`
- `PYTHONPATH=src ./.venv/bin/ruff check src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/_grc9v3_extensions.py src/pygrc/telemetry/__init__.py tests/telemetry/test_grc9v3_contract.py tests/telemetry/test_grc9v3_extensions.py`
