# GRC9 Specification

Source paper: `papers/2026-04-GRC-9.md`

## Purpose

`GRC9` is the mechanically explicit nine-slot substrate:

- port-labeled graph,
- 3×3 row/column bundle,
- row-based coherence tensor,
- one conductance per occupied port-pair,
- three optional analytic edge labels on the same occupied port-pairs,
- sink/basin extraction,
- simple mechanical spark trigger,
- local module expansion,
- invertible column coarse-graining.

This class is intentionally simpler than `GRCV3`.

## Class

```python
class GRC9(GRCModel):
    ...
```

## Capabilities

`GRC9.list_capabilities()` must include:

- `port_graph`
- `mechanical_refinement`
- `column_coarse_graining`
- `single_weight_edges`
- `multi_metric_edges`
- `intrinsic_frame`

`GRC9.list_capabilities()` may additionally include:

- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

It must not claim:

- `basin_attributes`
- `hierarchy_tracking`
- `choice_collapse_semantics`
- `host_embedding_frame`
- `quadrature_budget`

unless those are actually implemented. Those belong to `GRC9V3`.

## State Specification

```python
PortId = int                      # 1..9
ModeRow = int                     # 1..3
PolarityColumn = int              # 1..3

@dataclass
class PortEdge:
    node_u: NodeId
    port_u: PortId
    node_v: NodeId
    port_v: PortId
    conductance: float
    flux_uv: float

@dataclass
class GRC9State(GRCState):
    node_coherence: dict[NodeId, float]
    port_edges: dict[EdgeId, PortEdge]
    geometric_length: dict[EdgeId, float]
    temporal_delay: dict[EdgeId, float]
    flux_coupling: dict[EdgeId, float]
    potential: dict[NodeId, float]
    sink_set: set[NodeId]
    basins: dict[NodeId, set[NodeId]]
    expansion_registry: dict[str, Any]
    coarse_cache: dict[str, Any]
    rng_state: Any | None
```

## Topology Requirements

The implementation must support:

- exactly nine ordered ports per node,
- active/inactive port occupancy,
- deterministic conversion `r <-> (a, b)`,
- lookup from a node and port to the unique incident edge if occupied,
- deterministic rewiring by column family.

## Parameters

Includes standard GRC parameters plus:

- expansion policy parameters
- target effective degree policy
- bond weight initialization policy
- explicit `curvature_backend`
- explicit `frame_mode`
- optional `boundary_mode`
- explicit `expansion_distribution_mode`
- `edge_label_selection`
- optional adiabatic expansion schedule
- coarse-graining cache policy

`frame_mode` must default to:

- `fixed_port_chart`

`boundary_mode`, when implemented, should be one of:

- `prune`
- `barrier`
- `ghost`

`expansion_distribution_mode` must be one of:

- `equal`
- `custom`

`curvature_backend` must be one of:

- `ollivier`
- `forman`
- `none`

## Required Step Semantics

Each `step()` must perform:

1. compute row-based node tensor
2. update edge conductance
3. compute selected analytic edge labels:
   geometric length, temporal delay, flux coupling
4. compute potential
5. compute flux
6. compute successor map, sink set, basins
7. detect sparks using the simple mechanical trigger
8. expand modules where triggered
9. apply growth on lowest-index inactive ports
10. apply configured boundary behavior if implemented
11. apply continuity update
12. enforce exact budget preservation
13. refresh or invalidate coarse-state cache

## Tensor

`GRC9` must compute the row-based tensor from:

- density term,
- row-wise mismatch term,
- flux feedback term.

The row basis is mandatory in this class.

## Frame Semantics

The baseline `GRC9` frame is the nine-slot constitutive chart.

- `fixed_port_chart` means the local directional basis is given by the 3x3 row/column bundle itself.

This class must advertise `intrinsic_frame` because the row/column chart is part of the model substrate rather than host-supplied metadata.

If an implementation enriches the analytic edge labels using host-supplied geometry in addition to the fixed port chart, it must document that auxiliary rule explicitly without changing the meaning of the core nine-slot basis.

## Edge Labels

`GRC9` must support the shared analytic edge-label family on occupied port-pairs:

- `geometric_length`
- `temporal_delay`
- `flux_coupling`

Selection is controlled by `edge_label_selection`, whose default is `"all"`.

When all three labels are selected, any selected label that cannot be computed from a stronger ambient or induced geometry must still be populated using the common-interface availability contract and tagged with the corresponding computation mode metadata.

The public meaning of these labels matches the common interface even when the internal storage is attached to occupied port-pairs rather than abstract undirected edges. The update equations continue to use only the single dynamical conductance on each occupied port-pair.

If an implementation adds channel-specific or tensor-derived transport beyond the baseline scalar conductance on each occupied port-pair, it must advertise `anisotropic_edges` explicitly rather than implying that the row-resolved core already provides full continuum tensor freedom.

## Boundary Semantics

Core `GRC9` does not require a separate low-coherence boundary-management pass beyond its explicit topology events. If an implementation adds one, it must expose that rule through `boundary_mode`.

- `prune` means low-coherence support can be removed by graph regularization.
- `barrier` means low-coherence boundary regions are retained and traversal cost is increased instead of immediate removal.
- `ghost` means explicit low-coherence support nodes or edges are retained for boundary bookkeeping.

If `boundary_mode` is `barrier` or `ghost`, `list_capabilities()` must include `boundary_barrier`.

## Spark Trigger

The core spark rule in `GRC9` is intentionally mechanical.

Minimum required trigger:

- `deg_act(s) == 9`
- and either:
  - local instability proxy, or
  - small-magnitude column diagnostic

The implementation must not silently replace this with the richer `GRCV3` semantics in the core `GRC9` class.

## Expansion

Expansion is the canonical topology event in `GRC9`.

Required behavior:

- replace a sink by a connected module,
- preserve column families when reattaching boundary edges,
- preserve total budget,
- keep deterministic wiring convention,
- allow optional gradualization over substeps.

## Expansion Distribution Rule

Baseline single-field `GRC9` uses a deterministic expansion-distribution rule controlled by `expansion_distribution_mode`.

- `equal` is the default and means the expansion mass transferred from the parent is divided equally among the primary child targets defined by the expansion operator.
- `custom` is reserved for a documented alternative implementation rule and must serialize the extra parameters needed to reproduce it.

The reference implementation starts with `equal` as the authoritative rule. More complex asymmetry heuristics are allowed later, but they must not replace the default baseline silently.

## Column Coarse-Graining

The implementation must expose:

```python
def coarse_grain_columns(self, field_name: str) -> dict[str, Any]: ...
def split_columns(self, coarse_state: Mapping[str, Any]) -> dict[str, Any]: ...
```

These are required features of `GRC9`, not optional extras.

Supported field types:

- nonnegative scalar fields on occupied ports,
- signed flux via positive/negative decomposition or compressed mode.

## Temporal and Causal Semantics

`temporal_delay` is an analytic propagation label when selected. In baseline `GRC9`, it must not be presented as proper time or as a complete discrete Lorentzian metric.

If an implementation adds lapse/shift-like data, causal cones, or other explicit spacetime structure, it must advertise `causal_layer` explicitly and serialize the extra causal-state fields needed to make that layer reproducible.

## Scale Semantics

Baseline `GRC9` provides an explicit discrete multiscale ladder through column coarse-graining and Split, but it does not require a scale-indexed coherence field.

If an implementation carries multi-scale coherence values or an explicit discrete analogue of the FRC $\sigma$ coordinate beyond the coarse-graining ladder, it must advertise `multiscale_sigma` explicitly and serialize the corresponding scale-state data.

## Observables

Required observables:

- `abundance`
- `budget_current`
- `budget_error`
- `num_nodes`
- `num_port_edges`
- `spark_count`
- `active_degree_histogram`

Recommended observables:

- column profile sparsity
- expansion count
- sink-module sizes

## Serialization

A `GRC9` snapshot must include:

- port occupancy,
- port-edge structure,
- node coherence,
- selected analytic edge-label families,
- `edge_label_computation_mode`,
- `edge_label_params`,
- conductance and flux per occupied port-pair,
- `curvature_backend`,
- `frame_mode`,
- `expansion_distribution_mode`,
- `edge_label_selection`,
- `boundary_mode` if implemented,
- expansion in-progress state,
- optional coarse-graining cache metadata.
