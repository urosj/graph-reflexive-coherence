# Phase 7 Equation Map

This document maps `GRC9V3` spec objects onto planned code ownership.

Its purpose is to prevent three failure modes:

- treating `GRC9V3` as `GRC9` plus metadata,
- treating `GRC9V3` as `GRCV3` on a different graph container,
- or hiding genuinely new hybrid behavior behind parent-family helpers.

## Scope

This map covers the core `GRC9V3` runtime defined by:

- [`../specs/grc-9-v3-spec.md`](../specs/grc-9-v3-spec.md)
- [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)
- [`../specs/grc-v3-spec.md`](../specs/grc-v3-spec.md)
- [`Phase-7-ImplementationPlan.md`](./Phase-7-ImplementationPlan.md)

It does not define:

- Phase T-GRC9V3 telemetry,
- Phase V-GRC9V3 visualization,
- GRC9V3 phenomenology discovery,
- or GRCL/source-seed lowering for GRC9V3.

At core Phase 7 scope, those are downstream tracks rather than part of the
runtime equation map.

Current status: those downstream tracks have now been completed as the Phase 7
post-core evidence and source-layer closure. This equation map remains the
core-runtime ownership map; the completed downstream artifacts are linked from
[ImplementationPhases.md](./ImplementationPhases.md) and
[GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md).

## Ownership Legend

| Ownership | Meaning |
|---|---|
| `GRC9 mechanical` | inherited from the nine-slot port substrate and mechanical expansion rules |
| `GRCV3 semantic` | inherited from basin attributes, signed Hessian, hierarchy, choice/collapse, or quadrature semantics |
| `GRC9V3 hybrid` | behavior that only exists when the GRC9 substrate and GRCV3 semantic lift interact |

## Planned Code Ownership

| Concern | Planned owner |
|---|---|
| Public model class and step orchestration | `src/pygrc/models/grc_9_v3.py` |
| Hybrid state dataclasses | `src/pygrc/models/grc_9_v3_state.py` |
| Port helper reuse | `src/pygrc/models/grc_9_ports.py` |
| Row-basis differential summaries | `src/pygrc/models/grc_9_v3_runtime.py` |
| Hybrid spark and stabilization helpers | `src/pygrc/models/grc_9_v3_sparks.py` |
| Choice/collapse/learning helpers | `src/pygrc/models/grc_9_v3_choice.py` |
| Mechanical expansion reuse/adapters | `src/pygrc/models/grc_9_expansion.py` plus hybrid adapter |
| Serialization and snapshot shape | existing shared serialization plus GRC9V3 state builders |

Exact filenames may change, but the ownership split should remain explicit.

## State Carrier Map

### `GRC9V3NodeState`

Spec carrier:

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
```

Ownership:

- `coherence`: GRC9 mechanical value field, interpreted through GRCV3 basin
  semantics
- `gradient_row_basis`: GRC9V3 hybrid
- `signed_hessian_row_basis`: GRC9V3 hybrid
- `net_flux_summary`: GRC9V3 hybrid
- `basin_mass`, `basin_id`, `parent_id`, `depth`: GRCV3 semantic

`basin_mass` is a derived semantic quantity, not seed metadata. For GRC9V3 it
must be refreshed from the current basin membership after identity extraction:

```text
M_b = sum_{i in basin(b)} mu_i C_i
```

The baseline implementation uses `quadrature_mode = "unit_measure"`, so
`mu_i = 1`. A runtime that merely preserves a previous `basin_mass` value while
basin membership changes is incomplete with respect to Appendix G.

Direct tests:

- `tests/models/test_grc_9_v3_state.py`
- `tests/models/test_grc_9_v3_differential.py`

### `GRC9V3State`

Spec carrier:

```python
@dataclass
class GRC9V3State(GRCState):
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

Ownership:

- `port_edges`: GRC9 mechanical
- `base_conductance`: GRC9 mechanical transport carrier with GRCV3 label split
- analytic edge labels: shared GRCV3 semantic label meaning on GRC9 port-pairs
- `sink_set`, `basins`: shared identity surface, with separate flux-topology
  and geometric validation layers
- `hierarchy`: GRCV3 semantic
- `choice_registry`, `collapse_registry`: GRCV3 semantic
- `coarse_cache`: GRC9 mechanical column coarse-graining plus hybrid summaries

Direct tests:

- `tests/models/test_grc_9_v3_state.py`
- `tests/models/test_grc_9_v3_serialization.py`

## Operator Map

| Spec object / operation | Anchor | Ownership | Planned hook | Planned evidence | Direct test target |
|---|---|---|---|---|---|
| Ordered nine ports | GRC9 | GRC9 mechanical | port helpers | topology snapshot | state/port tests |
| Row/column chart | GRC9 | GRC9 mechanical | port helpers | topology + diagnostics | port tests |
| Row-basis gradient summary | GRC9V3 spec step 1 | GRC9V3 hybrid | `compute_row_basis_gradient` | node state | differential tests |
| Signed Hessian row-basis summary | GRC9V3 spec Eq. G3 | GRC9V3 hybrid | `compute_signed_hessian_row_basis` with `hessian_backend` | node state + sign convention + backend | Hessian tests |
| Weighted least-squares Hessian | GRCV3 Appendix A.3 | GRCV3 semantic comparison backend | `compute_weighted_least_squares_hessian` | comparison diagnostic | Hessian backend tests |
| Net-flux row summary | GRC9V3 state | GRC9V3 hybrid | `compute_net_flux_summary` | node state | differential tests |
| Hybrid node tensor | GRC9 Eq. (1) in GRC9V3 row basis | GRC9V3 hybrid | `compute_node_tensors` | optional diagnostic | tensor tests |
| Base conductance | GRC9V3 edge labels | GRC9 mechanical with GRCV3 label split | `compute_base_conductance` | `base_conductance` | transport tests |
| Geometric length | GRC9/GRCV3 labels | shared analytic label | `compute_edge_labels` | label dict + computation mode | label tests |
| Temporal delay | GRC9/GRCV3 labels | shared analytic label, not Lorentzian time | `compute_edge_labels` | label dict + computation mode | label tests |
| Flux coupling | GRC9/GRCV3 labels | shared analytic label | `compute_edge_labels` | label dict + computation mode | label tests |
| Potential | GRC9/GRCV3 transport | GRC9 mechanical | `compute_potential` | `potential` | transport tests |
| Flux | GRC9/GRCV3 transport | GRC9 mechanical | `compute_flux` | port-edge flux / row summaries | transport tests |
| Flux-topology sinks/basins | both parents | shared identity | `detect_identities` | `sink_set`, `basins` | identity tests |
| Geometric basin seeds | GRCV3 | GRCV3 semantic | `validate_basin_seeds` | diagnostics + node fields | identity tests |
| Effective basin mass `M_i` | Appendix G Eq. G1/G9/G10 | GRCV3 semantic over GRC9V3 graph | `compute_effective_basin_masses` | node state + identity cache + checkpoint node records | basin-mass tests |
| Spark candidate saturation gate | GRC9 | GRC9 mechanical | `detect_hybrid_spark_candidates` | candidate diagnostics | spark tests |
| Spark degeneracy gate | GRCV3 | GRCV3 semantic | `detect_hybrid_spark_candidates` | candidate diagnostics | spark tests |
| Hybrid spark candidate | GRC9V3 | GRC9V3 hybrid | `detect_hybrid_spark_candidates` | candidate event/diagnostic | spark tests |
| Mechanical expansion | GRC9 | GRC9 mechanical | `apply_mechanical_expansion` | topology/event payload | expansion tests |
| Child-basin stabilization | GRC9V3 | GRC9V3 hybrid | `evaluate_child_basin_stabilization` | completion diagnostic | spark/expansion tests |
| Completed hybrid spark | GRC9V3 | GRC9V3 hybrid | `register_completed_spark` | event row + registry | spark tests |
| Hierarchy update | GRCV3 | GRCV3 semantic | `update_hierarchy_after_stabilization` | `hierarchy`, node depth | hierarchy tests |
| Choice detection | GRCV3 | GRCV3 semantic | `update_choice_state` | choice event/registry | choice tests |
| Collapse detection | GRCV3 | GRCV3 semantic | `update_choice_state` | collapse event/registry | collapse tests |
| Learning state change | GRCV3 | GRCV3 semantic | `apply_learning_update` | state mutation + event | learning tests |
| Boundary behavior | GRC9V3 spec | capability-gated | `apply_boundary_behavior` | topology/state + capability | boundary tests |
| Quadrature budget | GRCV3 | GRCV3 semantic applied to GRC9 values | `enforce_quadrature_budget` | budget fields/remainder | budget tests |
| Column coarse-graining | GRC9 | GRC9 mechanical on GRC9V3 port chart | `coarse_grain_columns`, `split_columns` | coarse cache + reconstruction checks | coarse tests |
| Port utilization by hierarchy depth | GRC9V3 observable | GRC9V3 hybrid | `compute_observables` | observables | observable tests |

## Backend And Config Surface

Baseline public config:

| Surface | Default | Notes |
|---|---|---|
| `frame_mode` | `fixed_port_chart` | required intrinsic frame |
| `boundary_mode` | `prune` | `barrier` and `ghost` require `boundary_barrier` |
| `expansion_distribution_mode` | `equal` | inherited from GRC9 |
| `edge_label_selection` | `all` | inherited label-selection contract |
| `curvature_backend` | `none` | stronger backends may be added later |
| `hessian_backend` | `row_basis_diagonal` | baseline Eq. G3; `weighted_least_squares` allowed for geometry comparison |
| `choice_backend` | deterministic baseline | must be explicit if multiple scoring rules exist |
| `quadrature_mode` | `unit_measure` | `mu_i == 1` default |

Optional capability-gated surfaces:

- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`
- `spark_signed_crossing`

## Column Coarse-Graining Rule

`GRC9V3` inherits the GRC9 nine-port chart, so its
`column_coarse_graining` capability must mean the actual Section 9 operator
surface:

```text
coarse_grain_columns(field_name) -> coarse state (column totals + profiles)
split_columns(coarse_state) -> reconstructed fine port field
```

Coarse-cache invalidation alone is not sufficient to satisfy the capability.

Implementation requirements:

- reuse the pure GRC9 helpers in `src/pygrc/models/grc_9_coarse.py`,
- support exact nonnegative fields such as `conductance`, `geometric_length`,
  `temporal_delay`, `flux_coupling`, and `abs_flux`,
- support exact signed flux through the `J+ / J-` split mode,
- store cache entries with the same mode names as GRC9:
  - `exact_column_profile`
  - `signed_flux_split`
- invalidate cached coarse states after topology or value changes,
- prove `Split(G(X)) = X` for supported fields in direct tests.

Current correctness status: Iteration 9.2 repaired this operator surface.
`GRC9V3.coarse_grain_columns(...)` and `GRC9V3.split_columns(...)` now provide
the public Section 9 operator/Split surface for supported live port fields.
`refresh_coarse_cache()` remains cache hygiene and is not treated as the
operator itself.

## Hessian Backend Rule

Phase 7 must support an explicit Hessian backend choice.

The baseline is:

```text
hessian_backend = "row_basis_diagonal"
```

This is the GRC9V3 fixed-port-chart diagonal row-basis form from Eq. G3.

The comparison backend is:

```text
hessian_backend = "weighted_least_squares"
```

This reuses the GRCV3 Appendix A.3 style geometry where feasible. It exists to
compare the effect of the richer GRCV3 Hessian on basin seeds, spark
degeneracy, and collapse geometry. It must not become an implicit default.

## Hybrid Tensor Rule

The Phase 7 tensor must preserve the GRC9 Eq. (1) row-basis tensor structure.

The baseline tensor is diagonal in the fixed row basis:

```text
K_i[a,a] =
    lambda_c * C_i
  + xi_c * sum_{j in row a} w_ij * (C_j - C_i)^2
  + zeta_c * (sum_j J_ij)^2
```

The `xi_c` term is row-local and diagonal. It is not
`gradient_row_basis outer gradient_row_basis`.

The `zeta_c` term is isotropic because the scalar total net flux squared is
added to each diagonal entry. It is not
`net_flux_summary outer net_flux_summary`.

## Hybrid Spark Rule

Phase 7 must distinguish three states:

1. candidate source condition:
   - saturated local port capacity,
   - basin-interior behavior,
   - signed-Hessian degeneracy.
2. mechanical expansion:
   - GRC9 module construction and column-preserving reassignment occurred.
3. completed hybrid spark:
   - post-expansion child basin or attractor gain is detected and registered.

This distinction is mandatory. It is the main behavioral difference from pure
GRC9.

## Budget Rule

The GRC9V3 budget target is:

```text
B = sum_i mu_i * C_i
```

Baseline `quadrature_mode = "unit_measure"` sets `mu_i = 1`.

Mechanical expansion must preserve this weighted budget. If a later iteration
adds non-unit measures, expansion transfer and correction rules must operate on
weighted mass, not raw coherence alone.

The baseline budget-correction methods are:

- `uniform_shift`
- `simplex_projection`

The simplex projection path is required because it preserves positivity while
enforcing the budget target.

## Non-Claims

This equation map does not claim:

- Lorentzian causal semantics from `temporal_delay`,
- host embedding frame,
- anisotropic edge transport beyond scalar `base_conductance`,
- multiscale sigma field,
- barrier/ghost boundary behavior without capability support,
- or GRCL/source-language lowering for GRC9V3 as part of the core runtime.

GRCL-9V3 source-language lowering is now implemented as a downstream
source/lowering layer, not as a widening of the core equation map.
