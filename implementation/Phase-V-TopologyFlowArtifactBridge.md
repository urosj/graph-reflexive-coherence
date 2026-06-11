# Phase V Topology And Flow Artifact Bridge

This document closes **Phase V Iteration 6** by defining the minimum artifact
surface required before `PyGRC` can render graph structure and flow activity
honestly.

It is intentionally a **bridge contract**, not a renderer design and not a
runtime implementation. The goal is to make the upstream extension point
explicit so later graph visuals are driven by saved artifacts rather than by
live model state or visualization-side reconstruction.

## Why This Bridge Exists

Current Phase T artifacts are strong enough for:

- scalar trajectories from `steps.jsonl`
- event timelines from `events.jsonl`
- run panels from `run_summary.json`
- comparison panels from `experiment_report.json` and
  `comparison_report.json`

Current artifacts are **not** strong enough for:

- checkpoint graph snapshots
- graph-local event overlays
- per-edge flow visuals
- topology-delta views across time

That gap must be closed explicitly. Phase V must not invent graph structure,
edge flux, or node layout from observables that were never saved.

## Bridge Decisions

### 1. Topology/Flow Data Must Be Checkpointed Sidecar Artifacts

Topology and flow should **not** be injected into `steps.jsonl`.

`steps.jsonl` should remain lightweight and scalar-first, as established in
Phase T. Graph-shaped data should instead live in optional checkpoint sidecars
under the run directory.

Recommended run-directory extension:

- `graph_checkpoints/index.json`
- `graph_checkpoints/step-00000000.json`
- `graph_checkpoints/step-00000025.json`
- `graph_checkpoints/step-00000050.json`
- `graph_checkpoints/step-00000100.json`

Rationale:

- graph snapshots may become large
- checkpoint artifacts are naturally interval-driven rather than per-step by
  default
- individual checkpoint files are easier to inspect, diff, and load selectively
  than one monolithic JSON blob
- this preserves the current Phase T discipline where full state is optional
  and scalar telemetry remains the default evidence surface

### 2. One Checkpoint Artifact Must Carry Both Topology And Flow Overlays

The bridge should not split graph structure into one artifact family and flow
into another unless a concrete size/performance reason emerges later.

Each checkpoint artifact should therefore contain:

- checkpoint identity metadata
- topology payload
- node overlays
- edge overlays
- optional layout hints
- optional family extensions

This makes one saved checkpoint sufficient for:

- static graph rendering
- graph-local event/context overlays
- flow overlays
- later conversion into `networkx` or `pyvis` adapter structures

### 3. The Contract Must Be Family-Extensible

The checkpoint surface must support at least:

- `GRCV2`
- `GRCV3`
- `GRC9`

without forcing those families into one fake topology model.

The bridge must therefore expose:

- a common checkpoint wrapper
- a topology kind discriminator
- common overlay names where semantics truly align
- and `family_extensions` for anything family-specific

Recommended `graph_kind` values:

- `weighted_graph`
- `port_graph`

More can be added later if a future family needs them.

## Minimum Checkpoint Identity Contract

Each checkpoint file must carry enough identity to stand on its own when loaded
outside the rest of the run.

Minimum required checkpoint metadata:

- `artifact_type`
  - recommended value: `graph_checkpoint`
- `artifact_version`
- `run_id`
- `model_family`
- `params_identity`
- `step_index`
- `time`
- `checkpoint_label`
  - examples:
    - `initial`
    - `interval`
    - `eventful`
    - `final`

Recommended metadata:

- `seed_name`
- `param_family`
- `rng_seed`
- `label_computation_modes`
  - especially relevant for:
    - `geometric_length`
    - `temporal_delay`
    - `flux_coupling`

Rationale:

- the visualization layer must be able to cite what it is drawing
- checkpoint interpretation should not depend on hidden runtime context
- analytic edge labels may be exact or surrogate depending on family/mode and
  that must remain visible to downstream tools

## Minimum Topology Payload

Every checkpoint must export enough structure to reconstruct the graph without
guessing.

Minimum required topology fields:

- `graph_kind`
- `node_ids`
- `edges`

`edges` must be a deterministic list, not a mapping with unstable iteration
semantics.

For `weighted_graph`, each edge record must carry:

- `edge_id`
- `source_node_id`
- `target_node_id`

For `port_graph`, each edge record must carry at least:

- `edge_id`
- `source_node_id`
- `source_port_id`
- `target_node_id`
- `target_port_id`

Recommended common topology metadata:

- `node_count`
- `edge_count`
- `topology_extensions`

Rationale:

- graph rendering must not infer connectivity from basin labels or observables
- stable edge IDs are required for consistent overlays across checkpoints
- port graphs need explicit endpoint detail rather than a collapsed weighted
  surrogate

## Minimum Node Overlay Contract

Node overlays are values that a graph renderer may color, size, label, or
filter on top of the saved topology.

### Required Common Node Overlays

Every checkpoint should carry these node-level quantities when they exist for
the family:

- `coherence`

This is the one truly universal quantity across the current GRC families and is
the minimum required node visual signal.

### Recommended Common Node Overlays

These should be exported whenever the family computes them meaningfully:

- `potential`
- `sink_flag`
- `basin_id`
- `net_flux`
- `depth`
- `parent_id`

### Family-Specific Node Overlays

Anything outside the common layer should live under:

- `family_extensions`

Examples:

- Hessian summaries for `GRCV3`
- port-bundle state for `GRC9`
- split-progress state if a family wants graph-local split rendering later

Rationale:

- the common layer should stay small and honest
- later families need room to expose richer local structure without forcing it
  into a fake shared schema

## Minimum Edge Overlay Contract

Edge overlays are values that a graph renderer may vary by width, color,
opacity, label, or directional decoration.

### Required Common Edge Overlays

Every checkpoint should carry:

- `base_conductance`

This is the minimum graph-local edge quantity required for any honest
graph-facing rendering.

### Recommended Common Edge Overlays

These should be exported when the family computes them:

- `geometric_length`
- `temporal_delay`
- `flux_coupling`

### Flow-Specific Edge Overlays

When flow export is enabled, each edge should additionally carry:

- `signed_flux`

with interpretation tied to the saved edge orientation:

- positive means flow in the stored `source -> target` direction
- negative means flow against that stored direction

Rationale:

- conductance and flow must remain distinct
- `flux_coupling = |J_ij|` is useful but insufficient for directional flow
  rendering
- explicit orientation is required for stable arrow/gradient overlays

## Minimum Flow Contract

### Preferred Export

The preferred flow representation is:

- per-edge `signed_flux`

This supports:

- directional overlays
- flow-threshold filtering
- net-flow checks
- later comparison of conductance versus realized transport

### Allowed Fallback

If a family or checkpoint mode cannot export signed flux yet, the bridge may
allow:

- `flux_coupling`

but the checkpoint metadata must then declare:

- `flow_representation = "magnitude_only_surrogate"`

The renderer must treat that honestly:

- no directional arrows
- no signed net-flow interpretation
- no claims about source/target dominance

### Recommended Node-Level Flow Summaries

When available, checkpoints should also expose:

- `net_flux`
- `in_flux`
- `out_flux`

These are not substitutes for per-edge flow, but they are useful for node
highlighting and sanity checks.

## Conductance Versus Flux Rule

The bridge makes this distinction explicit:

- `base_conductance`
  - transport capacity or metric coupling
- `signed_flux`
  - realized directed transport at the checkpoint
- `flux_coupling`
  - absolute transport magnitude

Visualization must never substitute one for another.

That means:

- no arrow directions derived from conductance
- no flow heat inferred from topology alone
- no claim that a thick conductance edge is a high-flow edge unless
  `signed_flux` or `flux_coupling` says so

## Layout Policy

Coordinates are **optional layout aids**, not mandatory source semantics.

### Allowed Sources Of Layout

The bridge allows three layout situations:

1. `layout_hints` absent
   - renderer uses a deterministic layout policy at draw time
2. `layout_hints` present as host embedding
   - renderer may place nodes using the supplied host geometry
3. `layout_hints` present as intrinsic/render hint
   - renderer may use saved positions as a stable visualization aid without
     treating them as physical coordinates

### Layout Metadata Requirements

If layout hints are saved, the checkpoint should declare:

- `layout_mode`
  - examples:
    - `host_embedding`
    - `intrinsic_projection`
    - `render_hint`
- `layout_dimensions`

### Deterministic Fallback Requirement

If layout hints are absent, visualization must use a deterministic policy based
on:

- saved topology
- saved run/checkpoint identity
- stable layout parameters

Rationale:

- reproducibility matters even when coordinates are not part of the model
- layout should not become hidden semantics
- this stays consistent with RC/GRC’s commitment that geometry is induced
  rather than imposed

## Checkpoint Selection Policy

Iteration 6 does not fix one final cadence, but it does fix the rule that graph
artifacts are **checkpointed**, not recorded blindly at every step.

Minimum supported checkpoint selectors should later include:

- `initial`
- `final`
- `every_n_steps`
- `explicit_step_indices`
- `eventful_steps`

Default expectation for first implementation:

- `initial`
- `final`
- optional `every_n_steps`

Rationale:

- first graph visuals do not need full animation-grade telemetry
- checkpointing keeps artifacts tractable
- eventful-step capture provides a path to birth/spark-local inspection later

## Required Upstream Extension Point

The required upstream extension point belongs in **telemetry/runtime capture**,
not in visualization.

Iteration 6 therefore recommends a future telemetry-side addition with three
parts:

### 1. Schema Layer

Add explicit graph-checkpoint schema definitions under:

- `src/pygrc/telemetry/schema.py`

### 2. Artifact I/O Layer

Add save/load helpers and deterministic path builders under:

- `src/pygrc/telemetry/io.py`

### 3. Recorder Hook

Extend runtime capture so checkpoint artifacts can be emitted from the model or
family adapter under:

- `src/pygrc/telemetry/recorder.py`

This should be driven by explicit capture config, not by visualization code.

Recommended future capture knobs:

- `record_graph_checkpoints`
- `checkpoint_selector`
- `include_flow_overlays`
- `include_layout_hints`

### Family Export Boundary

The telemetry recorder should not synthesize family-local graph state by
guessing. It should call a family-aware export hook or adapter that returns a
checkpoint artifact in the shared bridge shape.

That boundary should remain downstream of runtime truth and upstream of
visualization.

## What Iteration 6 Resolves

Iteration 6 now resolves:

- where graph-shaped artifacts belong
- what the minimum checkpoint identity is
- what topology must be saved
- what node/edge overlays are required or recommended
- how flow is represented honestly
- how layout hints are treated
- where the upstream implementation must attach

## What Iteration 6 Intentionally Defers

Iteration 6 does **not** yet finalize:

- the exact Python dataclass/API names for graph checkpoint objects
- the final checkpoint cadence defaults
- event-to-checkpoint linking details
- renderer-specific styling rules
- graph animation or playback surfaces

Those belong in the later Iteration 8 and Iteration 9 contract work and then
in the eventual telemetry/runtime implementation phase that makes this bridge
real.
