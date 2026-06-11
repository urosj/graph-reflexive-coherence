# Phase 6 GRC9 Telemetry Contract

## Purpose

This note records the explicit `GRC9` telemetry extension contract used by the
Phase 6 artifact lanes.

The shared telemetry core remains unchanged:

- step rows
- event rows
- run summaries
- experiment reports
- comparison reports

`GRC9` adds family-specific payloads only through:

- `family_extensions["grc9"]` on step rows
- `family_extensions["grc9"]` on event rows
- `family_extensions["grc9"]` on run summaries

The canonical contract version for the current Phase 6 slice is:

- `phase6_iter10_v1`

## Family Key

- family key: `grc9`
- contract version: `phase6_iter10_v1`

These values are currently defined in:

- [experiments.py](../src/pygrc/telemetry/experiments.py)

## Shared Extension Rule

Unlike the richer `GRCV3` telemetry surface, the current `GRC9` family
extension is intentionally compact.

The runner passes one shared `grc9` extension payload through:

- step rows
- event rows
- run summaries

and then adds one summary-only field:

- `final_expansion_count`

There is currently no separate:

- per-step `grc9` family extension builder
- per-event `grc9` family extension classifier
- checkpoint-specific `grc9` extension contract

This is a deliberate scope choice for the mechanical Phase 6 baseline, not an
accident in the recorder.

## Shared Fields

Every current `GRC9` artifact lane should carry these fields under
`family_extensions["grc9"]`:

- `contract_version`
- `abundance_contract`
- `source_reference`

The representative lane also carries:

- `lane_name`
- `role`

The seed-driven structural lane also carries:

- `profile_name`
- `seed_source_reference`
- `source_lowering_mode`

For the current Phase 6 seed-driven lane, `source_lowering_mode` should be
read together with one more unstated-but-required interpretation rule:

- the lane reuses the existing `GRCV2` landscape blueprint boundary
- therefore it is a structural bridge into `GRC9`, not a complete family-native
  `GRCL-9` lowering layer

## Step-Row Extension Payload

### Representative Lane

Each representative step row currently carries:

- `contract_version`
- `lane_name`
- `role`
- `abundance_contract`
- `source_reference`

Interpretation:

- `lane_name` identifies the representative artifact lane
- `role` distinguishes `primary` from `replay`
- `abundance_contract` records that `abundance` is computed from a local,
  non-persisted topology-updated sink diagnostic using the current stored flux
  field
- `source_reference` points to the normative Phase 6 runtime doc

### Seed-Driven Structural Lane

Each seed-driven structural step row currently carries:

- `contract_version`
- `profile_name`
- `abundance_contract`
- `seed_source_reference`
- `source_reference`
- `source_lowering_mode`

Interpretation:

- `profile_name` identifies the closeout-facing structural lane configuration
- `seed_source_reference` points back to the original seed/source identity
- `source_reference` points to the Phase 6 closeout-facing documentation
- `source_lowering_mode = structural_graph_graft_v1` means the lane is a
  structural lowering onto the nine-slot substrate, not a `GRC9V3` semantic
  projector
- it also means the lane should not be read as a claim that `GRCL-9` already
  exists as a family-native source implementation

## Event-Row Extension Payload

Current `GRC9` event rows reuse the same shared family extension payload as the
step rows for the corresponding lane.

That means:

- representative event rows currently carry the representative shared fields
- seed-driven event rows currently carry the seed-driven shared fields

The event rows do **not** currently add a separate `grc9` classification layer
such as:

- event domain
- lifecycle stage
- topology mutation flags

Those remain available through the raw `event_kind` and raw event payload. If a
later family phase needs a richer `GRC9` event contract, that should be added
explicitly rather than implied retroactively.

## Run-Summary Extension Payload

Each `GRC9` run summary currently carries the same shared lane payload plus:

- `final_expansion_count`

So the representative run summary carries:

- `contract_version`
- `lane_name`
- `role`
- `abundance_contract`
- `source_reference`
- `final_expansion_count`

And the seed-driven structural run summary carries:

- `contract_version`
- `profile_name`
- `abundance_contract`
- `seed_source_reference`
- `source_reference`
- `source_lowering_mode`
- `final_expansion_count`

Interpretation:

- `final_expansion_count` is the end-of-run size of the live expansion
  registry, not a full historical event count
- event-count and observable-delta interpretation still belongs primarily to
  the shared event rows and comparison reports

## Observable Contract Recorded Here

The most important family-specific telemetry contract choice in Phase 6 is the
meaning of `abundance`.

The recorded value is:

- `topology_updated_current_flux_diagnostic`

Meaning:

- `abundance` is not defined as the persisted step-6 `sink_set`
- it is not a second full reflexive pass after continuity
- it is a local, non-persisted sink diagnostic recomputed from the settled
  topology plus the currently stored flux field

This contract should stay synchronized with:

- [Phase-6-StepLoop.md](./Phase-6-StepLoop.md)
- [Phase-6-Closeout.md](./Phase-6-Closeout.md)

## Current Limits

This Phase 6 `GRC9` telemetry contract does not yet provide:

- graph-checkpoint-specific `grc9` family extensions
- a richer `grc9` event taxonomy beyond raw event kinds/payloads
- dense rich-source semantic telemetry
- any claim that seed-driven `GRC9` lowering is already `GRC9V3`
- any claim that the current seed-driven bridge is already a completed
  `GRCL-9` layer

Those are later-family or later-phase concerns, not hidden requirements of the
current mechanical closeout.
