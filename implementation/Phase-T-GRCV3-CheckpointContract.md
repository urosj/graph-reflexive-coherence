# Phase T GRCV3 Checkpoint Contract

## Purpose

This note records the family-specific graph-checkpoint contract that should be
used when `GRCV3` later gains checkpoint export in Phase T Iteration 22.

It extends the shared checkpoint schema already defined in
[src/pygrc/telemetry/schema.py](../src/pygrc/telemetry/schema.py) without
forking it.

The intent is:

- reuse the shared `GraphCheckpointArtifact` container,
- keep the checkpoint graph shape common across families,
- and make `GRCV3`-specific node/edge semantics explicit before exporter code
  lands.

## Common Schema Reuse

`GRCV3` checkpoint export should reuse the shared checkpoint schema fields for:

- `identity`
- `checkpoint_id`
- `step_index`
- `time`
- `checkpoint_label`
- `checkpoint_reason`
- `graph_kind`
- `node_count`
- `edge_count`
- `node_records`
- `edge_records`
- `event_step_range`
- `event_count_window`
- `event_counts_by_kind_window`
- `flow_representation`
- `flow_cadence`
- `layout_mode`
- `layout_dimensions`
- `layout_hints`
- `label_computation_modes`
- `topology_extensions`
- `family_extensions`

The family key for checkpoint extensions should be:

- `grcv3`

The current checkpoint-contract version should be:

- `phase_t_iter26_v1`

## Graph Kind

`GRCV3` should export:

- `graph_kind = "weighted_graph"`

Rationale:

- runtime topology still lives on `WeightedGraphBackend`
- the graph-visible checkpoint layer should describe the executable graph as it
  exists, not a separate semantic graph abstraction

`GRCV3`-specific semantics therefore belong in:

- node records
- edge records
- `family_extensions["grcv3"]`

not in a separate graph kind.

## Required Node Record Surface

Each `GRCV3` node record should include the shared graph fields:

- `node_id`
- `payload`

and the following required `GRCV3` fields:

- `coherence`
- `basin_id`
- `depth`
- `basin_mass`
- `gradient`
- `gradient_norm`
- `hessian`
- `net_flux`

The following fields are conditionally required when available:

- `parent_id`
  - required when the node belongs to a non-root hierarchy basin
- `potential`
  - required when the runtime state has a node potential for this node
- `sink_flag`
  - required when the node is in the current sink set

### Node Semantics

`coherence`:

- exported from `BasinAttributes.coherence`

`basin_id`, `parent_id`, `depth`, `basin_mass`:

- exported from `BasinAttributes`
- these are semantic node-local fields, not derived visualization labels

`gradient`:

- exported as the current differential gradient vector from
  `BasinAttributes.gradient`

`gradient_norm`:

- exported explicitly as a scalar convenience field so downstream graph
  rendering does not need to recompute it

`hessian`:

- exported as the raw stored Hessian matrix from `BasinAttributes.hessian`
- this should remain the raw family state, not a signed or thresholded variant

`net_flux`:

- exported as the node-local differential summary vector from
  `BasinAttributes.net_flux`
- this is distinct from checkpoint flow overlays derived from edge flux

### Optional Landscape-Carried Node Meaning

If the runtime node payload already contains projector or landscape metadata,
that metadata should remain inside:

- `payload`

Examples include:

- primitive identifiers
- role labels
- realization keys
- chart hints
- attachment or directionality tags

The checkpoint exporter should preserve that payload rather than attempting to
re-encode it into new top-level checkpoint fields.

### Landscape Monitoring Metadata

When the checkpoint comes from a rich `GRCV3` landscape lane with an explicit
monitored interior surface, `family_extensions["grcv3"]` should also carry:

- `landscape_monitoring_surface_kind`
- `landscape_monitored_node_ids_by_primitive_id`

Rationale:

- raw checkpoint node records already carry the full local differential state
- the missing piece for downstream consumers is the deterministic pointer to
  which node should be interpreted as the monitored interior site for the
  transient seed-to-spark path

## Required Edge Record Surface

Each `GRCV3` edge record should include the shared graph fields:

- `edge_id`
- `source_node_id`
- `target_node_id`
- `payload`

and the following required `GRCV3` fields:

- `base_conductance`
- `geometric_length_available`

The following analytic labels are conditionally required when present in state:

- `geometric_length`
- `temporal_delay`
- `flux_coupling`

The following interpretation fields are conditionally required when available:

- `directionality_semantics`
- `geometric_length_mode`

### Edge Semantics

`base_conductance`:

- exported from `state.base_conductance`
- this is the runtime edge conductance and should not be confused with any
  landscape seed prior or transport-intent multiplier

`geometric_length_available`:

- explicit boolean telling downstream consumers whether a geometric-length
  label was actually computed for the edge

`geometric_length`, `temporal_delay`, `flux_coupling`:

- exported only when present in state
- no visualization code should infer these labels if they are absent

`directionality_semantics`:

- exported when already present on the topology edge payload

`geometric_length_mode`:

- should be copied from the shared `label_computation_modes` surface when that
  mode exists for `geometric_length`

## Flow Overlay Contract

`GRCV3` should use the same checkpoint-level flow contract as `GRCV2` when
realized edge flux is available honestly.

### Edge-Level Flow Overlay

When `include_flow_overlays = True` and the checkpoint is taken after flux has
been computed for the current state, each edge record should export:

- `signed_flux`
- `signed_flux_source`
- `signed_flux_target`
- `flux_orientation_source_node_id`
- `flux_orientation_target_node_id`
- `flux_symmetry = "antisymmetric"`

The source-oriented value should be:

- `state.flux[(edge_id, source_node_id)]`

### Node-Level Flow Overlay

When edge-level flow overlays are exported, each node record should also export
the edge-derived flow summary scalars:

- `net_edge_flux`
- `in_flux`
- `out_flux`

These are distinct from the always-family-local differential vector:

- `net_flux`

To avoid ambiguity:

- `net_flux` means the stored `BasinAttributes.net_flux` vector
- `net_edge_flux` means the scalar sum of oriented checkpoint edge fluxes

### Initial / Pre-Step Checkpoints

When checkpoint cadence includes the initial pre-step state, the exporter may
find that no realized edge flux exists yet.

In that case:

- `flow_representation = "not_available_pre_step"`
- edge-level signed flux fields should not be fabricated
- node-level `net_edge_flux`, `in_flux`, and `out_flux` should not be
  fabricated

### Flow-Cadence Declaration

When flow overlays are exported, `GRCV3` should declare:

- `flow_cadence = "checkpoint_only"`

This keeps the first family extension aligned with the current shared
checkpoint cadence model.

## Layout Contract

`GRCV3` checkpoint export should not invent a new graph layout regime.

The first contract should therefore use:

- `layout_mode = "ambient_chart_hint"` when stable 2D chart hints are available
  on node payloads
- otherwise `layout_mode = None`

If `layout_mode = "ambient_chart_hint"`, the checkpoint should also declare:

- `layout_dimensions = 2`

and may provide lightweight shared hints in:

- `layout_hints`

The exporter should not run a graph-layout algorithm during checkpoint export.
Layout inference belongs later in visualization, not telemetry.

## GRCV3 Family Extension Payload

`family_extensions["grcv3"]` should include:

- `contract_version`
- `params_identity`
- `budget_target`
- `remainder`
- `hessian_sign`
- `backend_summary`
- `hierarchy_summary`
- `spark_summary`
- `choice_summary`

### Required Family-Extension Fields

`contract_version`:

- `phase_t_iter26_v1`

`backend_summary`:

- `geometry_backend`
- `differential_backend`
- `metric_backend`
- `spark_backend`
- `hierarchy_backend`
- `choice_backend`

`hierarchy_summary`:

- `hierarchy_root_count`
- `hierarchy_node_count`
- `child_basin_link_count`

`spark_summary`:

- `split_registry_size`
- `active_split_count`
- `confirmed_split_count`
- `pending_spark_count`

`choice_summary`:

- `choice_regime_count`
- `collapse_registry_count`
- `evaluated_node_count`

### Optional Family-Extension Fields

The first contract may also preserve lightweight lowering/runtime context when
present in cached quantities, for example:

- `landscape_lowering_lane`
- `landscape_lowering_semantic_authority`
- `landscape_runtime_assembly_mode`

These remain optional because the first representative checkpoint lane may use a
synthetic runtime model rather than a landscape-derived one.

## Topology Extensions

`topology_extensions` should continue to carry shared graph-backend bookkeeping:

- `next_node_id`
- `next_edge_id`

`GRCV3` should not move family semantics into `topology_extensions` unless the
information is genuinely backend/topology-wide rather than family-specific.

## Explicit Non-Goals For The First Checkpoint Slice

The first `GRCV3` checkpoint contract does **not** require:

- full hierarchy tree dumps beyond summary counts
- full `choice_registry` payload export
- full `collapse_registry` payload export
- full `split_registry` payload export
- signed-Hessian eigenvalue caches on every node
- spark-candidate overlays inferred when no candidate state exists
- graph-layout execution during export

Those may become later checkpoint extensions, but they should not be smuggled
into the first contract implicitly.

## Consequence For Iteration 22

With this contract in place, the Iteration 22 exporter should be able to
proceed mechanically:

1. reuse shared checkpoint writer/index infrastructure
2. export executable `WeightedGraphBackend` topology
3. map `GRCV3State` node/edge semantics into the contract above
4. emit flow overlays only when the saved surface supports them honestly

The exporter should not redefine checkpoint schema shape; it should only fill
the agreed `GRCV3` family surface.
