# Phase T Family Extension Matrix

## Purpose

Phase T should now be treated as shared telemetry infrastructure for executable
families, not as permanently `GRCV2`-shaped tooling.

This matrix separates:

- the common telemetry contract every family should reuse
- the family-specific extension surfaces each family may add without rewriting
  the shared contract

## Common Core

The following telemetry layers are family-neutral and should remain shared:

- run identity and provenance
- step rows
- event rows
- run summaries
- experiment reports
- comparison reports
- artifact layout
- deterministic writer/loader behavior
- parameter recording and replay identity
- optional checkpoint cadence plumbing

These belong to `src/pygrc/telemetry/` and should not be redefined inside
family-local modules.

## Family Extension Surface

Family-specific detail should enter through explicit extension payloads rather
than family-local ad hoc schemas.

The main extension points are:

- `family_extensions` on step rows
- `family_extensions` on event rows
- `family_extensions` on run summaries
- optional family-specific checkpoint payload groups when checkpoint export is
  enabled

## Current Family Matrix

### GRCV2

`GRCV2` telemetry currently exposes or should expose:

- shared observables and event counts
- seed/projector identity
- front birth and split event streams
- optional graph checkpoint exports
- optional flow overlays when graph checkpoints are enabled

### GRCV3

`GRCV3` telemetry should extend the shared contract with, at minimum:

- basin-attribute summaries
  - active basin count
  - geometric seed count
  - validated geometric basin count
  - max hierarchy depth
- signed-Hessian metadata
  - `hessian_sign`
  - differential backend identity when relevant to replay and analysis
- spark lifecycle state
  - candidate / pending / confirmed counts
  - split-progress state where relevant to summary views
- hierarchy state
  - hierarchy root count
  - child-basin counts or equivalent lightweight summary
- choice lifecycle state
  - choice-regime count
  - collapse count
  - explicit `choice_detected`, `choice_resolved`, and `collapse` event
    coverage

The first explicit field-level contract for this extension surface is recorded
in [Phase-T-GRCV3-TelemetryContract.md](./Phase-T-GRCV3-TelemetryContract.md).

If later telemetry iterations add checkpoint export for `GRCV3`, the extension
surface may also include:

- node basin-attribute payload snapshots
- hierarchy snapshots
- spark/choice overlays

but those are checkpoint extensions, not replacements for the shared contract.

The first explicit checkpoint-level contract for that later slice is recorded
in [Phase-T-GRCV3-CheckpointContract.md](./Phase-T-GRCV3-CheckpointContract.md).

## Rule For Future Families

Any later family such as `GRC9` or `GRC9V3` should follow the same rule:

1. reuse the shared telemetry core first
2. add explicit family extensions second
3. record the extension surface here or in a linked family-specific telemetry
   contract note

If a later family needs a new shared telemetry concept, update the common Phase
T plan rather than smuggling that concept through one family's extension block.
