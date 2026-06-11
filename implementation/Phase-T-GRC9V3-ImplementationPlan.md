# Phase T GRC9V3 Implementation Plan

This document is the execution plan for **Phase T-GRC9V3: GRC9V3 Hybrid
Telemetry Extension**.

Core Phase 7 closed `GRC9V3` as an executable hybrid runtime. It deliberately
stopped before telemetry, visualization, phenomenology discovery, and
GRCL/source-seed lowering.

Current status: those post-core layers are now complete through GRCL-9V3
Revision 1. This plan remains the Phase T telemetry execution record.

Post-Lane-B status: the core GRC9V3 runtime now has an opt-in Lane B spark
predicate, `grc9v3_column_h_assisted`. Phase T event, step, and checkpoint
surfaces are Lane B-aware through candidate payloads, `hybrid_spark_state`, and
node overlays. Backend/run configuration also records the selected
`spark_lane`, so lane selection is visible even before a candidate fires.
Candidate payloads remain the source of causal gate evidence.

Phase T-GRC9V3 starts the next layer: make the hybrid runtime observable in
shared telemetry artifacts without changing the runtime equations.

## Purpose

Phase T-GRC9V3 must expose the hybrid behavior that is not visible from either
parent family alone:

- GRC9 nine-slot port mechanics,
- GRCV3 basin-attribute semantics on those ports,
- row-basis gradient and signed-Hessian diagnostics,
- GRC9 Eq. (1) tensors in the fixed row basis,
- scalar transport plus analytic edge labels,
- flux-topology identities and geometric basin seeds,
- hybrid spark candidates,
- mechanical expansion events,
- post-expansion child-basin stabilization,
- completed hybrid sparks,
- hierarchy updates from completed sparks,
- choice/collapse/learning over GRC9 port-flux successor structure,
- inactive-port growth,
- quadrature budget closure,
- and coarse-cache invalidation after topology/value changes.

The telemetry must also preserve ownership boundaries:

- GRC9-owned mechanics stay separately inspectable.
- GRCV3-owned semantic fields stay separately inspectable.
- GRC9V3-only hybrid behavior is named explicitly.

## Inputs

Authoritative inputs:

- [Phase-7-Closeout.md](./Phase-7-Closeout.md)
- [Phase-7-RepresentativeRuntime.md](./Phase-7-RepresentativeRuntime.md)
- [Phase-7-EquationMap.md](./Phase-7-EquationMap.md)
- [Phase-7-StepLoop.md](./Phase-7-StepLoop.md)
- [Phase-T-GRC9-TelemetryContract.md](./Phase-T-GRC9-TelemetryContract.md)
- [Phase-T-GRCV3-TelemetryContract.md](./Phase-T-GRCV3-TelemetryContract.md)
- [papers/2026-04-GRC-9.md](../papers/2026-04-GRC-9.md), especially Appendix G
  and Appendix E

Runtime implementation inputs:

- `src/pygrc/models/grc_9_v3.py`
- `src/pygrc/models/grc_9_v3_state.py`
- `src/pygrc/models/grc_9_v3_runtime.py`
- `src/pygrc/models/grc_9_v3_sparks.py`
- `src/pygrc/models/grc_9_v3_choice.py`

Representative evidence input:

- `outputs/phase7-grc9v3-representative/grc9v3/appendix_e_cell_division/`

That Phase 7 artifact is runtime evidence, not yet telemetry evidence.
Phase T-GRC9V3 may reuse the same fixture and command shape, but must write a
new telemetry artifact lane with a new contract version.

## Relationship To Parent Telemetry

GRC9V3 telemetry should not flatten into either parent contract.

From GRC9 telemetry, it inherits:

- port chart summaries,
- mechanical expansion evidence,
- growth through inactive ports,
- edge labels,
- budget correction,
- graph checkpoint overlays.

From GRCV3 telemetry, it inherits:

- signed-Hessian summaries,
- basin attributes,
- hierarchy state,
- choice/collapse state,
- lifecycle counts.

GRC9V3 adds hybrid-specific surfaces:

- row-basis differential summaries on the nine-slot port chart,
- hybrid tensor summaries,
- spark candidate evidence requiring saturation plus basin-interior
  signed-Hessian degeneracy,
- opt-in Lane B candidate evidence where the direct runtime-computed column-H
  proxy branch can fire inside the same GRC9V3 saturation / basin-interior
  envelope,
- child-basin stabilization after mechanical expansion,
- completed hybrid spark evidence,
- choice/collapse over GRC9 port-flux successors,
- and Appendix E daughter-sink run summaries.

## Family Key

The telemetry family key should be:

```text
grc9v3
```

The first contract version should be:

```text
phase_t_grc9v3_iter1_v1
```

The expected implementation target is:

```text
src/pygrc/telemetry/grc9v3_contract.py
```

Private builders may live in:

```text
src/pygrc/telemetry/_grc9v3_extensions.py
```

## In Scope

- telemetry contract document,
- typed contract dataclasses,
- family-extension wrapper helpers,
- step-row extension builders,
- event-row classifier and evidence builders,
- run-summary builders,
- representative telemetry lane using the Phase 7 Appendix E fixture,
- optional graph checkpoint overlays,
- tests for contract validation, builders, replay, and row/event consistency,
- closeout document for Phase T-GRC9V3.

## Out Of Scope

This phase does not implement:

- new GRC9V3 runtime equations,
- Phase V-GRC9V3 visualization,
- GRC9V3 phenomenology discovery,
- reviewed GRC9V3 motif catalogs,
- GRCL/source-seed lowering for GRC9V3,
- barrier/ghost boundary runtime behavior,
- Lorentzian causal semantics,
- anisotropic edge transport,
- multiscale sigma fields,
- non-unit quadrature measures,
- or adiabatic expansion execution.

Current status: Phase V-GRC9V3 visualization, GRC9V3 phenomenology discovery,
reviewed catalogs, and GRCL-9V3 source lowering are now implemented as separate
downstream tracks. They do not widen the Phase T telemetry contract.

These may be named as reserved or unavailable telemetry surfaces, but they must
not be claimed as artifact-backed.

## Workstreams

### Workstream 1. Contract

Create `Phase-T-GRC9V3-TelemetryContract.md` and lock:

- family key,
- contract version,
- step-row groups,
- event-row groups,
- run-summary groups,
- graph checkpoint overlays,
- availability conventions,
- compression rules,
- and parent/hybrid ownership rules.

### Workstream 2. Typed Contract Module

Add `grc9v3_contract.py` with:

- dataclasses for each payload group,
- validation helpers,
- `grc9v3_step_family_extensions(...)`,
- `grc9v3_event_family_extensions(...)`,
- `grc9v3_run_summary_family_extensions(...)`,
- and `classify_grc9v3_event_extension(...)`.

### Workstream 3. Step Builders

Build step extensions from live `GRC9V3` state:

- backend/config,
- port chart,
- row-basis differential,
- hybrid tensor,
- transport labels,
- identity/basin,
- spark state,
- hierarchy,
- choice/collapse,
- growth/budget/coarse state.

Post-Lane-B catch-up:

- `backend_config` records `spark_lane` when available, so Lane A versus
  Lane B run selection is visible even before any candidate event appears.
- `hybrid_spark_state` should continue to expose the latest candidate lane and
  latest column-H proxy-branch evidence when a Lane B candidate exists.
- Step telemetry should not treat a configured Lane B run as proof that the
  column-H branch fired; branch attribution belongs to candidate payloads.

### Workstream 4. Event Builders

Classify event rows into:

- `spark`,
- `expansion`,
- `choice`,
- `collapse`,
- `growth`,
- `budget`,
- `coarse`,
- `boundary`,
- `other`.

Preserve raw event kinds. The extension is a stable taxonomy and evidence
layer, not a replacement for runtime event payloads.

Post-Lane-B catch-up:

- `hybrid_spark_candidate` remains a shared event kind.
- Lane B candidates are distinguished by payload fields such as `spark_lane`,
  `lane_b_candidate_hit`, `column_h_branch_hit`, and `gate_reasons`.
- Consumers must not infer Lane A or Lane B from event kind alone.

### Workstream 5. Run Summary

Emit fixed-width lifecycle counts and final summaries for:

- candidate sparks,
- mechanical expansions,
- completed hybrid sparks,
- daughter-sink stabilization,
- hierarchy,
- choice/collapse,
- growth,
- budget,
- replay determinism.

### Workstream 6. Representative Telemetry

Use the Phase 7 `appendix_e_cell_division` fixture to produce a telemetry lane
that writes:

- steps,
- events,
- run summary,
- report,
- initial/final snapshots,
- optional graph checkpoints.

The representative telemetry document should be:

```text
Phase-T-GRC9V3-RepresentativeTelemetry.md
```

The lane should be distinct from the Phase 7 runtime evidence lane.

### Workstream 7. Closeout

Close Phase T-GRC9V3 only after:

- the contract is implemented,
- representative telemetry is replayable,
- event rows and summary counts agree,
- snapshot replay is deterministic,
- and deferred downstream tracks are recorded.

Post-Lane-B documentation catch-up is separate from the original Phase T close:
it records that Lane B is now implemented, keeps Lane A telemetry
backward-compatible, and records backend/config lane visibility.

## Acceptance Criteria

Phase T-GRC9V3 is complete when:

- `family_extensions["grc9v3"]` exists on representative step rows, event rows,
  run summaries, and checkpoint overlays when enabled,
- the contract version is `phase_t_grc9v3_iter1_v1`,
- row-basis semantic fields and nine-slot mechanical fields remain distinct,
- hybrid-only event semantics are visible,
- completed spark evidence distinguishes expansion from child-basin
  stabilization,
- Lane B candidate payloads, when present, distinguish signed-Hessian-only
  candidates from column-H proxy-branch candidates,
- backend/run configuration records `spark_lane`,
- choice/collapse evidence is represented without pretending it belongs to
  pure GRC9,
- representative telemetry replays deterministically,
- and downstream Phase V / phenomenology / GRCL-GRC9V3 work can consume the
  artifacts without reaching around the telemetry surface.
