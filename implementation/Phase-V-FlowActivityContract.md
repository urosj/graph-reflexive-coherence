# Phase V Flow-Activity Contract

This document closes **Phase V Iteration 9** by defining the artifact contract
required for honest flow-activity rendering.

It refines the broader bridge defined in
[`Phase-V-TopologyFlowArtifactBridge.md`](./Phase-V-TopologyFlowArtifactBridge.md)
and complements the checkpoint sequencing rules defined in
[`Phase-V-GraphEvolutionContract.md`](./Phase-V-GraphEvolutionContract.md).

## Scope

This contract covers:

- per-edge flow export
- node-level net-flow summaries
- conductance versus flow distinction
- cadence expectations for flow artifacts
- telemetry-side extension points required to support flow visuals

This contract does **not** define:

- graph-evolution sequencing in general
- visualization styling
- PDE equivalence claims
- family-local numeric methods for computing flow

## Why Flow Needs Its Own Contract

Flow visuals are especially vulnerable to accidental invention.

If a checkpoint only saves:

- topology
- node coherence
- edge conductance

then a renderer can still produce a nice graph picture, but it cannot honestly
show transport.

It must not:

- draw arrows from conductance alone
- infer direction from node size or color
- assume high conductance implies high realized transport

Flow therefore needs its own saved evidence surface.

## Core Rule

Flow activity must be rendered only from explicitly saved flow quantities.

Phase V must not synthesize flow visuals from:

- topology alone
- conductance alone
- scalar observables such as `average_conductance`
- or live model access when the saved run artifacts do not contain flow data

## Preferred Flow Representation

The preferred graph-local flow quantity is:

- `signed_flux`

stored per edge in checkpoint artifacts.

### Interpretation Rule

Each edge record must define a stable orientation:

- `source_node_id`
- `target_node_id`

Then:

- `signed_flux > 0`
  - means realized transport in the stored `source -> target` direction
- `signed_flux < 0`
  - means realized transport in the opposite direction
- `signed_flux = 0`
  - means no realized transport at that checkpoint under the stored edge
    orientation

This rule must be held fixed across the artifact family.

## Allowed Surrogate Representation

If a family or checkpoint mode cannot yet export signed flux, the bridge may
allow:

- `flux_coupling`

with explicit metadata:

- `flow_representation = "magnitude_only_surrogate"`

### Consequences Of Surrogate Mode

In surrogate mode, visualization may show:

- edge magnitude intensity
- thresholded “active transport” overlays

but must **not** show:

- directional arrows
- signed source/sink interpretation
- node-level signed conservation claims derived from unsaved edge directions

## Minimum Per-Edge Flow Export Requirements

For honest flow-activity rendering, each checkpoint edge record should export:

- `base_conductance`
- and either:
  - `signed_flux`
  - or `flux_coupling` plus explicit surrogate metadata

Recommended edge-level fields:

- `flux_coupling`
- `temporal_delay`
- `geometric_length`

Rationale:

- conductance versus realized transport is a core comparison surface
- temporal-delay and geometric-length overlays may help interpret why some
  channels are active or inactive

## Minimum Node Net-Flow Export Requirements

Node-level flow summaries are not a substitute for per-edge flow, but they are
important for:

- highlighting active sinks/sources
- validating conservation visually
- summarizing crowded local neighborhoods

### Recommended Node Fields

When available, checkpoints should export:

- `net_flux`
- `in_flux`
- `out_flux`

### Minimal Rule

If only one node-level flow field is available, it should be:

- `net_flux`

### Interpretation Rule

Node-level summaries must be derived from saved edge-local flow quantities or
from a family-local export hook that uses the same orientation/sign rules.

Visualization must not recompute node net flow from incomplete or surrogate
inputs without explicit metadata allowing it.

## Conductance Versus Flux Distinction

This distinction is mandatory and should be preserved in names, metadata, and
rendering APIs.

### Conductance

- `base_conductance`
- describes transport capacity, coupling, or effective metric weight

### Flux

- `signed_flux`
- describes realized directed transport

### Magnitude

- `flux_coupling`
- describes transport magnitude without sign

### Required Visualization Rule

The renderer must treat these as separate channels.

That means:

- edge width based on conductance is not equivalent to edge width based on flow
- edge color based on `signed_flux` is not equivalent to color based on
  `flux_coupling`
- legends and captions must say which channel is being displayed

## Flow Cadence Expectations

Iteration 9 must define whether flow is checkpoint-based or per-step.

### Default Rule

The first honest flow visualization surface should be **checkpoint-based**.

Rationale:

- it aligns with the checkpoint graph contract
- it keeps artifacts tractable
- it supports static graph snapshots with transport overlays
- it avoids forcing a heavy per-step graph payload into every run

### Optional Higher-Fidelity Mode

Later telemetry may add:

- per-step flow artifacts

but that should be treated as an explicit higher-cost mode rather than the
default baseline.

### Minimum Supported Flow Cadences

The future telemetry config should support:

- `checkpoint_only`
- `every_n_steps`
- `eventful_checkpoints`

If per-step flow is later added, it should be named explicitly rather than
smuggled in as the default:

- `every_step`

## Required Flow Metadata

Each checkpoint payload that includes flow should declare:

- `flow_representation`
  - examples:
    - `signed_edge_flux`
    - `magnitude_only_surrogate`
- `flow_cadence`
  - examples:
    - `checkpoint_only`
    - `every_n_steps`
    - `eventful_checkpoints`

Recommended:

- `flow_backend`
  - if families later expose backend choices that affect flow export
- `flow_extensions`

## Family-Extensibility Rules

The common flow contract should stay narrow.

### Common Layer

- `signed_flux`
- `flux_coupling`
- `net_flux`
- `in_flux`
- `out_flux`
- representation metadata

### Family Layer

Anything more specific belongs in:

- `family_extensions`

Examples:

- `GRCV3`
  - signed directional labels tied to richer basin geometry
- `GRC9`
  - row/column or port-bundle transport decomposition

## Required Upstream Extensions

Iteration 9 makes the following upstream work explicit:

### Telemetry Schema

Add schema support for:

- checkpoint edge flow payloads
- checkpoint node flow summaries
- flow metadata fields

### Telemetry I/O

Add deterministic save/load support for those fields as part of the checkpoint
artifact family.

### Recorder / Runtime Hook

Extend telemetry capture config to control:

- whether flow overlays are recorded
- whether signed flux is required
- checkpoint cadence for flow export

### Family Export Hook

Each family must eventually expose a flow-export surface that returns saved
flow quantities without requiring Phase V to inspect live model internals.

## What Counts As “Currently Missing”

At the close of Iteration 9, the following remain explicitly missing from the
saved artifact lane:

- per-edge `signed_flux` checkpoint exports
- explicit `flux_coupling` checkpoint overlays
- node `net_flux` / `in_flux` / `out_flux` checkpoint summaries
- flow representation metadata
- checkpoint or cadence metadata dedicated to flow export

Phase V should continue to block flow-activity rendering until those surfaces
exist.
