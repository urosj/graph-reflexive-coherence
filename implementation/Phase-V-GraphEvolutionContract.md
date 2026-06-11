# Phase V Graph-Evolution Contract

This document closes **Phase V Iteration 8** by defining the artifact contract
required for honest graph-evolution rendering.

It refines the broader bridge defined in
[`Phase-V-TopologyFlowArtifactBridge.md`](./Phase-V-TopologyFlowArtifactBridge.md).
The purpose here is narrower:

- define what a checkpointed graph-evolution surface must contain,
- define how events relate to checkpoints,
- and define what telemetry must export before Phase V can render structural
  change over time without reopening live model state.

## Scope

This contract covers:

- checkpoint topology exports
- node overlays at checkpoints
- edge overlays at checkpoints
- event-to-checkpoint linkage
- checkpoint-selection semantics for graph evolution

This contract does **not** define:

- flow-specific rendering rules beyond what graph evolution needs for context
- renderer styling
- animation playback UX
- family-local implementation details of how checkpoints are captured

## Why Graph Evolution Needs Its Own Contract

The topology/flow bridge establishes the minimum graph-shaped artifact family.
Graph evolution adds a second requirement:

- multiple checkpoints must be relatable to one another over time

That means Phase V needs more than “a graph snapshot exists.” It needs:

- stable identity across checkpoints
- a way to know why a checkpoint exists
- a way to relate saved events to the structural frames
- and enough overlay continuity that topology deltas are interpretable rather
  than just visually different pictures

## Core Rule

Graph evolution must be rendered only from saved checkpoint artifacts plus
saved event rows and checkpoint index metadata.

Phase V must not reconstruct graph evolution by:

- re-running the model,
- diffing ad hoc live states,
- or inferring checkpoint timing from scalar trajectory plots alone

## Checkpoint Artifact Family

Graph evolution depends on a checkpoint artifact family with two levels:

### 1. Checkpoint Index

One index file per run:

- `graph_checkpoints/index.json`

The index must list all saved checkpoints in deterministic order.

Minimum checkpoint-index fields:

- `artifact_type`
  - recommended value: `graph_checkpoint_index`
- `artifact_version`
- `run_id`
- `model_family`
- `params_identity`
- `checkpoints`

Each checkpoint entry must carry:

- `checkpoint_id`
- `step_index`
- `time`
- `checkpoint_label`
- `path`

Recommended checkpoint-entry fields:

- `reason`
  - examples:
    - `initial`
    - `interval`
    - `eventful`
    - `final`
- `event_count_window`
- `event_kinds_window`

Rationale:

- the index is the canonical temporal spine for graph-evolution rendering
- visualization should not scan directories and guess which files belong in the
  sequence

### 2. Checkpoint Payload

One checkpoint file per saved graph frame:

- `graph_checkpoints/<checkpoint_id>.json`

The payload must satisfy the topology/flow bridge and additionally support
cross-checkpoint comparison.

## Stable Identity Requirements

Graph evolution depends on the same entity being traceable across multiple
frames.

### Node Identity

Every checkpoint must use stable node IDs for surviving nodes.

Rules:

- node IDs must not be renumbered between checkpoints
- removed nodes may disappear from later checkpoints
- newly created nodes must use backend-assigned stable IDs

### Edge Identity

Every checkpoint must use stable edge IDs where the family/backend can support
them.

Rules:

- surviving edges retain the same edge ID
- deleted edges disappear rather than being overwritten in place
- newly created edges receive new stable IDs

### Port-Graph Note

For `port_graph` families, stable identity may involve:

- edge ID
- endpoint node IDs
- endpoint port IDs

Phase V should treat the full endpoint tuple as the stable connectivity anchor
even when the visual surface later collapses some detail.

## Minimum Checkpoint Topology Export Requirements

Each checkpoint payload must include:

- checkpoint identity metadata
- `graph_kind`
- `node_ids`
- deterministic `edges`

For graph-evolution rendering, the following are additionally required:

- `node_count`
- `edge_count`

Recommended:

- `created_node_ids`
- `removed_node_ids`
- `created_edge_ids`
- `removed_edge_ids`

If created/removed lists are not exported, Phase V may still derive structural
diffs by comparing consecutive checkpoints, but only from saved checkpoint
files. Those lists are recommended because they make overlays and review much
cleaner.

## Node-Attribute Export Requirements

### Required Common Node Attributes

For graph-evolution rendering, checkpoints must export:

- `coherence`

This is the minimum node attribute required to show how the topology carries
mass/coherence through time.

### Recommended Common Node Attributes

These should be exported whenever available:

- `sink_flag`
- `basin_id`
- `parent_id`
- `depth`
- `potential`
- `net_flux`

### Graph-Evolution-Specific Guidance

If a family supports topology-changing events, checkpoints should also expose
enough node-local metadata to explain those changes later.

Recommended fields:

- `birth_origin`
- `split_parent_id`
- `lineage_role`

These may live in `family_extensions` if they are not truly common.

## Edge-Attribute Export Requirements

### Required Common Edge Attributes

For graph-evolution rendering, checkpoints must export:

- `base_conductance`

### Recommended Common Edge Attributes

- `geometric_length`
- `temporal_delay`
- `flux_coupling`

### Graph-Evolution-Specific Guidance

When possible, the checkpoint should make it obvious whether an edge is:

- persistent
- newly created
- scheduled for removal

Recommended fields:

- `edge_status`
- `creation_reason`
- `removal_reason`

These are optional, but they reduce the need for visualization-side diff logic.

## Event-To-Checkpoint Linking Contract

Graph evolution cannot stop at “we have events” and “we have graph frames.” It
must also state how those two surfaces align.

### Required Rule

Every checkpoint entry in `graph_checkpoints/index.json` must be linkable to a
window of event rows.

Minimum required linking fields on each checkpoint entry:

- `event_row_range`
  - recommended shape:
    - `start_inclusive`
    - `end_exclusive`

If row ranges are not practical, the index must instead provide:

- `event_step_range`
  - recommended shape:
    - `start_step_inclusive`
    - `end_step_inclusive`

### Recommended Event Summary Fields

Each checkpoint entry should also include:

- `event_count_window`
- `event_counts_by_kind_window`
- `triggering_event_ids`

Rationale:

- graph-local event overlays must be able to cite which events happened between
  frames
- “eventful checkpoint” must mean something explicit, not just “the visualizer
  decided this frame looks interesting”

## Checkpoint Selection Contract

Graph evolution requires deterministic frame selection.

### Minimum Supported Selectors

The telemetry-side checkpoint exporter should later support:

- `initial`
- `final`
- `every_n_steps`
- `explicit_step_indices`
- `eventful_steps`

### Recommended First Implementation

The first implementation should support:

- `initial`
- `final`
- `every_n_steps`

with optional `eventful_steps` once event-to-checkpoint linkage is wired.

### Selection Metadata

The checkpoint index should preserve the selection basis via:

- `selection_policy`
- `selection_params`

Examples:

- `{"selection_policy": "every_n_steps", "selection_params": {"n": 25}}`
- `{"selection_policy": "eventful_steps", "selection_params": {"kinds": ["birth"]}}`

## Family-Extensibility Rules

This contract must not hardcode `GRCV2`.

### Common Layer

The common graph-evolution layer is limited to:

- checkpoint identity
- stable topology identity
- minimal node/edge overlays
- event-window linkage

### Family Layer

Anything beyond that belongs in:

- `family_extensions`

Examples:

- `GRCV3`
  - Hessian, gradient, basin-bundle summaries
- `GRC9`
  - port-bundle occupancy, row/column activation, module lineage

## Required Upstream Additions

Iteration 8 makes the following upstream needs explicit:

### Telemetry Schema

Add schema objects for:

- graph checkpoint index
- graph checkpoint payload

### Telemetry I/O

Add deterministic save/load helpers for:

- checkpoint index
- checkpoint payloads

### Recorder / Runtime Hook

Extend checkpoint capture config so runs can record:

- no graph checkpoints
- interval checkpoints
- explicit checkpoints
- eventful checkpoints

### Family Export Hook

Each family must eventually expose a graph-checkpoint export hook or adapter
that returns:

- topology
- node overlays
- edge overlays
- family extensions

without visualization guessing how to derive them.

## What Counts As “Currently Missing”

At the close of Iteration 8, the following remain explicitly missing from the
saved artifact lane:

- checkpoint index artifacts
- checkpoint graph payloads
- event-window linkage from checkpoints to `events.jsonl`
- created/removed node/edge delta hints

Phase V should continue to block graph-evolution rendering until those surfaces
exist.
