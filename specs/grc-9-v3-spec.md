# GRC9V3 Specification

Source papers:

- `papers/2026-04-GRC-9.md`
- `papers/2026-02-GRC-V3.md`

## Purpose

`GRC9V3` is the hybrid class:

- the **substrate** is `GRC9`,
- the **semantic lift** is `GRCV3`.

So this class keeps:

- nine ordered ports,
- row/column mechanics,
- mechanical expansion,

while adding:

- basin-attribute nodes,
- signed basin Hessian semantics,
- explicit hierarchy,
- optional choice/collapse semantics,
- budget interpreted as RC quadrature.

## Class

```python
class GRC9V3(GRCModel):
    ...
```

## Capabilities

`GRC9V3.list_capabilities()` must include:

- `port_graph`
- `mechanical_refinement`
- `column_coarse_graining`
- `basin_attributes`
- `hierarchy_tracking`
- `multi_metric_edges`
- `choice_collapse_semantics`
- `quadrature_budget`
- `intrinsic_frame`

`GRC9V3.list_capabilities()` may additionally include:

- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

It must not claim:

- `host_embedding_frame`

## State Specification

```python
@dataclass
class GRC9V3NodeState:
    coherence: float
    gradient_row_basis: ArrayLike
    signed_hessian_row_basis: ArrayLike
    net_flux_summary: ArrayLike
    basin_mass: float
    basin_id: str | int
    parent_id: str | int | None
    depth: int

@dataclass
class GRC9V3State(GRCState):
    # Inherited shared runtime fields:
    # step_index, time, budget_target, remainder, cached_quantities,
    # event_log, observables, rng_state, params_identity.
    nodes: dict[NodeId, GRC9V3NodeState]
    port_edges: dict[EdgeId, PortEdge]
    base_conductance: dict[EdgeId, float]
    geometric_length: dict[EdgeId, float]
    temporal_delay: dict[EdgeId, float]
    flux_coupling: dict[EdgeId, float]
    potential: dict[NodeId, float]
    sink_set: set[NodeId]
    basins: dict[NodeId, set[NodeId]]
    hierarchy: dict[str | int, list[str | int]]
    choice_registry: dict[str, Any]
    collapse_registry: dict[str, Any]
    coarse_cache: dict[str, Any]
    rng_state: Any | None
```

`GRC9V3State` extends the shared `GRCState` contract. The fields listed above
are the GRC9V3-specific state surface; inherited runtime fields remain part of
the runtime and snapshot contract and must be preserved by save/load.

## Parameters

Includes all `GRC9` parameters plus:

- basin seed thresholds
- signed Hessian thresholds
- explicit spark-lane documentation
- attractor-count change registration policy
- node measure / quadrature mode
- choice/collapse scoring parameters
- explicit `frame_mode`
- explicit `boundary_mode`
- explicit `expansion_distribution_mode`
- `edge_label_selection`
- explicit `curvature_backend`
- analytic edge-label parameters

`frame_mode` must default to:

- `fixed_port_chart`

`boundary_mode` must be one of:

- `prune`
- `barrier`
- `ghost`

`expansion_distribution_mode` must be one of:

- `equal`
- `custom`

## Required Step Semantics

Each `step()` must perform:

1. compute row-based gradient summaries
2. compute row-basis Hessian summaries and signed Hessian convention
3. update node tensors
4. update base conductance
5. compute selected analytic edge labels
6. compute potential
7. compute flux
8. extract sinks and basins
9. identify basin seeds from gradient/Hessian conditions
10. detect spark candidates from saturation plus basin degeneracy
11. execute mechanical expansion
12. register completed sparks only after post-event child-basin stabilization
13. update optional choice/collapse/learning state
14. apply configured boundary behavior
15. apply continuity update
16. enforce quadrature-style budget
17. refresh/invalidate coarse-state cache

## Spark Semantics

This is the main difference from `GRC9`.

The baseline `GRC9V3` spark lane is the **current-hybrid signed-Hessian
lane**. In this lane, a spark candidate requires:

- local saturation of representational capacity,
- basin-interior behavior in gradient/Hessian terms,
- local degeneracy in the signed basin Hessian.

A completed spark requires:

- post-event gain of at least one stable child basin or attractor.

This preserves the mechanical refinement of `GRC9` while using the richer RC semantics of `GRCV3`.

The core `GRC9` column diagnostic `H_s^(b)` remains a distinct paper-facing
mechanical diagnostic. `GRC9V3` exposes direct column-`H` spark evidence only
through the named opt-in GRC9V3 column-H-assisted lane, with explicit
configuration, tests, telemetry/checkpoint evidence, and comparison against the
baseline signed-Hessian lane. A derived column-cancellation proxy must not be
reported as a direct spark gate under Lane A.

The implementation documentation must therefore distinguish:

| Lane | Meaning | Status Rule |
|---|---|---|
| `current_hybrid_signed_hessian` | GRC9 saturation plus GRCV3 basin-interior and signed-Hessian degeneracy evidence | Baseline `GRC9V3` spark semantics |
| `grc9v3_column_h_assisted` | GRC9V3 saturation and basin-interior envelope with signed-Hessian degeneracy or direct runtime-computed per-column `H_s^(b)` proxy threshold/sign-crossing evidence | Separate opt-in implementation lane; direct column-H proxy-branch evidence only for runs using this lane |
| `comparison` | Runs selected fixtures under both lanes | Analysis lane; not a replacement for either runtime contract |

Changing the default spark predicate from the signed-Hessian lane to a direct
column-`H`-assisted lane is a semantic runtime change. It must be documented as
such and must not happen as an incidental observability or experiment-support
patch.

The name `canonical_column_h` may be used in implementation notes for the core
`GRC9` diagnostic source. It is not the preferred GRC9V3 runtime lane name for
the column-H-assisted spark predicate.

## Expansion Semantics

Expansion remains mechanical and column-preserving, but it is interpreted as:

- basin refinement,
- local chart atlas expansion,
- possible parent-to-child hierarchy creation.

The implementation must therefore update hierarchy fields whenever expansion stabilizes child identities.

## Boundary Semantics

The implementation must expose its boundary handling rule explicitly through `boundary_mode`.

- `prune` is allowed as the baseline graph-regularization rule.
- `barrier` means the implementation preserves a boundary-region representation and raises traversal cost or equivalent resistance as coherence approaches the support threshold.
- `ghost` means the implementation retains explicit low-coherence support nodes or edges for boundary bookkeeping instead of collapsing the region immediately.

If `boundary_mode="prune"`, the implementation documentation must state clearly that this is a discrete regularization choice rather than a literal realization of the continuum boundary-horizon geometry.

If `boundary_mode` is `barrier` or `ghost`, `list_capabilities()` must include `boundary_barrier`.

## Choice / Collapse / Learning

This class must expose concrete event logic, not only prose semantics.

Minimum implementation requirement:

- provide sink-compatibility scores,
- detect nodes/modules in multi-basin choice regimes,
- detect collapse when one route becomes dominant,
- log learning as a post-collapse state change event with affected nodes/modules.

## Edge Labels

As in `GRCV3`, this class must distinguish:

- `base_conductance`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`

The storage location may be per occupied port-pair rather than per abstract edge, but the public meaning is the same.

Selection is controlled by `edge_label_selection`, whose default is `"all"`. Non-selected label families may remain empty in runtime state, but the selection policy must be serialized.

When all three labels are selected, any selected label that cannot be computed from a stronger ambient or induced geometry must still be populated using the common-interface availability contract and tagged with the corresponding computation mode metadata.

Baseline `GRC9V3` still uses scalar `base_conductance` on each occupied port-pair for the actual update equations. If an implementation adds channel-specific or tensor-derived transport beyond this scalar rule, it must advertise `anisotropic_edges` explicitly rather than implying that the row-basis semantics already carry full continuum tensor freedom.

## Frame Semantics

The baseline `GRC9V3` frame is the nine-slot constitutive chart.

- `fixed_port_chart` means the local directional basis is given by the 3x3 row/column bundle itself.

This class must advertise `intrinsic_frame` because the row/column chart is part of the model substrate rather than host-supplied metadata.

## Budget Semantics

`GRC9V3` must support:

$$
B = \sum_i \mu_i C_i
$$

with `mu_i == 1` as the default. Mechanical expansion must preserve this quantity explicitly.

## Temporal and Causal Semantics

`temporal_delay` is an analytic propagation label. In baseline `GRC9V3`, it must not be presented as proper time or as a complete discrete Lorentzian metric.

If an implementation adds lapse/shift-like data, causal cones, or other explicit spacetime structure, it must advertise `causal_layer` explicitly and serialize the extra causal-state fields needed to make that layer reproducible.

## Scale Semantics

Baseline `GRC9V3` has the discrete multiscale ladder inherited from `GRC9` together with basin hierarchy semantics, but it does not require a scale-indexed coherence field.

If an implementation carries multi-scale coherence values, scale-coupling operators, or an explicit discrete analogue of the FRC $\sigma$ coordinate, it must advertise `multiscale_sigma` explicitly and serialize the corresponding scale-state data.

## Observables

Required observables:

- all `GRC9` observables
- all `GRCV3` basin/hierarchy observables
- child-basin count after expansion
- choice regime count
- collapse count
- max hierarchy depth

Recommended observables:

- per-column basin mass distribution
- port utilization by hierarchy depth

## Serialization

A `GRC9V3` snapshot must include:

- all port-graph information,
- all basin-attribute fields,
- hierarchy,
- analytic edge labels,
- `edge_label_computation_mode`,
- `edge_label_params`,
- `frame_mode`,
- `boundary_mode`,
- `expansion_distribution_mode`,
- `edge_label_selection`,
- `curvature_backend`,
- spark-lane metadata when multiple lanes are implemented,
- choice/collapse registries,
- quadrature mode,
- expansion-progress state.

## Explicit Distinction from GRC9

`GRC9V3` is not just `GRC9` plus extra metadata.

It must differ behaviorally in:

- spark registration semantics,
- identity seed semantics,
- hierarchy semantics,
- event logging for choice/collapse,
- budget interpretation.
