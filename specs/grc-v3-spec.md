# GRCV3 Specification

Source paper: `papers/2026-02-GRC-V3.md`

## Purpose

`GRCV3` extends `GRCV2` by:

- turning nodes into basin charts with explicit differential summaries,
- separating base conductance from analytic edge labels,
- supporting hierarchy,
- tightening basin and spark semantics,
- optionally supporting discrete choice/collapse/learning events.

`GRCV3` is the semantic-rich graph class in the library.

## Class

```python
class GRCV3(GRCModel):
    ...
```

## Capabilities

`GRCV3.list_capabilities()` must include:

- `basin_attributes`
- `multi_metric_edges`
- `hierarchy_tracking`
- `quadrature_budget`
- `choice_collapse_semantics`

`GRCV3.list_capabilities()` may additionally include:

- `intrinsic_frame`
- `host_embedding_frame`
- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

## State Specification

```python
@dataclass
class BasinAttributes:
    coherence: float
    gradient: ArrayLike
    hessian: ArrayLike
    net_flux: ArrayLike
    basin_mass: float
    basin_id: str | int
    parent_id: str | int | None
    depth: int

@dataclass
class GRCV3State(GRCState):
    nodes: dict[NodeId, BasinAttributes]
    base_conductance: dict[EdgeId, float]
    geometric_length: dict[EdgeId, float]
    temporal_delay: dict[EdgeId, float]
    flux_coupling: dict[EdgeId, float]
    flux: dict[OrientedEdgeId, float]
    potential: dict[NodeId, float]
    sink_set: set[NodeId]
    basins: dict[NodeId, set[NodeId]]
    hierarchy: dict[str | int, list[str | int]]
    choice_registry: dict[str, Any]
    collapse_registry: dict[str, Any]
    rng_state: Any | None
```

## Parameters

Includes all `GRCV2` parameters plus:

- basin gradient threshold
- Hessian stability threshold
- spark degeneracy threshold
- optional quadrature weights or node measure mode
- explicit `frame_mode`
- explicit `boundary_mode`
- explicit `split_distribution_mode`
- `edge_label_selection`
- explicit `curvature_backend`
- edge-label parameters for geometric length and temporal delay
- compatibility score parameters for choice/collapse if enabled

`frame_mode` must be one of:

- `host_embedding`
- `induced_local_frame`
- `combinatorial`

`boundary_mode` must be one of:

- `prune`
- `barrier`
- `ghost`

`split_distribution_mode` must be one of:

- `equal`
- `custom`

`curvature_backend` must be one of:

- `ollivier`
- `forman`
- `none`

## Required Step Semantics

Each `step()` must perform:

1. compute basin attribute summaries:
   gradient, Hessian, net flux summary, basin mass/hierarchy updates
2. compute node tensors from basin attributes
3. compute base conductance
4. compute selected analytic edge labels:
   geometric length, temporal delay, flux coupling
5. compute potential
6. compute flux
7. detect sinks and attraction basins
8. validate or seed basins from basin attributes
9. detect sparks from local degeneracy
10. apply split/birth and configured boundary behavior
11. update optional choice/collapse state
12. apply continuity update
13. enforce budget as graph quadrature invariant
14. update observables

## Basin Attributes

The implementation must store and expose:

- node coherence,
- gradient summary,
- Hessian summary,
- net flux summary,
- effective basin mass,
- basin id,
- parent id,
- depth.

These must be queryable from the public state.

## Boundary Semantics

The implementation must expose its boundary handling rule explicitly through `boundary_mode`.

- `prune` is allowed as the baseline graph-regularization rule.
- `barrier` means the implementation preserves a boundary-region representation and raises traversal cost or equivalent resistance as coherence approaches the support threshold.
- `ghost` means the implementation retains explicit low-coherence support nodes or edges for boundary bookkeeping instead of collapsing the region immediately.

If `boundary_mode="prune"`, the implementation documentation must state clearly that this is a discrete regularization choice rather than a literal realization of the continuum boundary-horizon geometry.

If `boundary_mode` is `barrier` or `ghost`, `list_capabilities()` must include `boundary_barrier`.

## Frame Semantics

The implementation must expose its directional-frame convention explicitly through `frame_mode`.

- `host_embedding` means local directions or displacements are provided by the embedding host.
- `induced_local_frame` means the model derives a local basis from the current graph state and recomputes it deterministically.
- `combinatorial` means the model uses a purely graph-native directional surrogate with no external coordinates.

If `frame_mode="host_embedding"`, the model config or state must identify the required host-supplied geometric fields.

If `frame_mode` is `induced_local_frame` or `combinatorial`, the implementation must document the deterministic rule by which gradients, Hessians, and geometric edge labels are constructed from the graph.

`list_capabilities()` must include exactly one of:

- `host_embedding_frame`
- `intrinsic_frame`

## Edge Labels

The model must distinguish:

- `base_conductance`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`

The step equations use only `base_conductance`. The others are analytic products of the same state.

Selection is controlled by `edge_label_selection`, whose default is `"all"`. Non-selected label families may remain empty in runtime state, but the selection policy must be serialized.

When all three labels are selected, any selected label that cannot be computed from a stronger ambient or induced geometry must still be populated using the common-interface availability contract and tagged with the corresponding computation mode metadata.

Baseline `GRCV3` uses scalar `base_conductance` on each edge. If an implementation adds channel-specific or tensor-derived edge transport beyond this scalar rule, it must advertise `anisotropic_edges` explicitly rather than implying that the baseline conductance already carries full continuum anisotropy.

## Identity Semantics

`GRCV3` must support two compatible identity layers:

1. flux-topology layer from sinks and attraction domains
2. geometric layer from gradient/Hessian conditions

The implementation may require agreement between them, or allow one to validate the other, but it must expose both.

## Spark Semantics

The implementation must support signed-basin-Hessian semantics.

Required logic:

- choose a global Hessian sign convention,
- identify basin seeds from small gradient plus positive-definite signed Hessian,
- identify spark candidates from basin-interior degeneracy,
- register completed sparks only when local attractor structure gains at least one new stable child basin or sink.

Spark detection in the core model may use the full state needed by the discrete equations. Observer-limited visibility, partial-state inspection, or causal-horizon restrictions belong to integration and driver layers unless a model family explicitly introduces them into the dynamics.

## Choice / Collapse / Learning

Support is required at least at the event level.

Implementation contract:

- expose an optional sink-compatibility scoring method,
- detect `choice_detected` when multiple sink continuations are viable,
- detect `collapse` when routing sharpens to one continuation,
- treat learning as persistent post-collapse deformation in state updates,
- log events even if no special topology change occurs.

## Budget Semantics

`GRCV3` must interpret budget as:

$$
B = \sum_i \mu_i C_i
$$

with unit-measure mode allowed as the default. The implementation must either:

- store explicit node measures, or
- document that node values are already measure-absorbed.

## Temporal and Causal Semantics

`temporal_delay` is an analytic propagation label. In baseline `GRCV3`, it must not be presented as proper time or as a complete discrete Lorentzian metric.

If an implementation adds lapse/shift-like data, causal cones, or other explicit spacetime structure, it must advertise `causal_layer` explicitly and serialize the extra causal-state fields needed to make that layer reproducible.

## Scale Semantics

Baseline `GRCV3` is a single-scale graph realization with explicit basin hierarchy. It does not require a scale-indexed coherence field.

If an implementation carries multi-scale coherence values, scale-coupling operators, or an explicit discrete analogue of the FRC $\sigma$ coordinate, it must advertise `multiscale_sigma` explicitly and serialize the corresponding scale-state data.

## Observables

Required observables:

- all `GRCV2` observables
- average gradient norm
- curvature diagnostics
- max hierarchy depth
- number of active basins
- number of collapse events
- number of choice regimes

Recommended observables:

- path statistics under the analytic edge labels
- basin mass distribution

## Serialization

A `GRCV3` snapshot must include:

- full basin attribute bundles,
- all edge-label families,
- hierarchy,
- choice/collapse registry if enabled,
- budget measure mode,
- `edge_label_selection`,
- `edge_label_computation_mode`,
- `edge_label_params`,
- `frame_mode`,
- `boundary_mode`,
- `split_distribution_mode`,
- `curvature_backend`.

## Appendix A. Canonical Discrete Differential Summary Backend

This appendix defines the canonical reference backend for `gradient`, `hessian`, and `induced_local_frame` semantics in `GRCV3`. Implementations may provide equivalent alternatives, but any non-reference backend must be documented explicitly and serialized.

### A.1 Canonical local coordinates for `induced_local_frame`

For a node $i$, let $\mathcal N(i)$ be its neighbours and let $G_i^{\mathrm{ego}}$ be the weighted ego-graph on $\{i\}\cup\mathcal N(i)$ with symmetric weights given by the current `base_conductance`.

The canonical induced local frame of dimension $d$ is constructed as follows:

1. Build the normalized weighted Laplacian of $G_i^{\mathrm{ego}}$.
2. Take the first $d$ non-trivial eigenvectors, ordered by increasing eigenvalue.
3. Fix the sign of each eigenvector deterministically by requiring the largest-magnitude component to be positive; break ties by stable node ordering.
4. Define the pseudo-displacement from $i$ to a neighbour $j$ by
   $$
   \Delta y_{ij}
   :=
   \big(u_1(j)-u_1(i),\dots,u_d(j)-u_d(i)\big)^\top .
   $$

This gives a deterministic graph-intrinsic local chart for `induced_local_frame`. If `frame_mode="host_embedding"`, the host-supplied displacement or local coordinates replace $\Delta y_{ij}$ directly.

### A.2 Weighted least-squares gradient

Let $a_{ij}>0$ be the local regression weights; the canonical choice is
$$
a_{ij} := \mathrm{base\_conductance}_{ij}.
$$

Define the local moment matrix
$$
M_i := \sum_{j\in\mathcal N(i)} a_{ij}\,\Delta y_{ij}\Delta y_{ij}^{\!\top} + \lambda_{\mathrm{reg}} I,
\qquad \lambda_{\mathrm{reg}}>0.
$$

The canonical gradient estimate is
$$
\mathbf g_i
:=
M_i^{-1}
\sum_{j\in\mathcal N(i)} a_{ij}\,\Delta y_{ij}\,(C_j-C_i).
$$

This is the weighted least-squares solution of the first-order local fit.

### A.3 Weighted least-squares Hessian

Let the first-order residual be
$$
r_{ij} := C_j - C_i - \mathbf g_i^\top \Delta y_{ij}.
$$

Let $\mathrm{vech}(H)$ denote the vector of unique entries of a symmetric matrix $H$, and define the quadratic feature vector $\psi(\Delta y)\in\mathbb R^{d(d+1)/2}$ by:

- diagonal entries: $\tfrac12 \Delta y_a^2$,
- off-diagonal entries: $\Delta y_a\Delta y_b$ for $a<b$.

Then the canonical Hessian coefficients are the weighted least-squares solution
$$
h_i
:=
\arg\min_h
\sum_{j\in\mathcal N(i)}
a_{ij}\,

\bigl(
r_{ij} - \psi(\Delta y_{ij})^\top h
\bigr)^2
+
\lambda_H \|h\|^2,
\qquad \lambda_H \ge 0,
$$
and the Hessian summary $H_i$ is the symmetric matrix reconstructed from $h_i=\mathrm{vech}(H_i)$.

This is the canonical second-order discrete differential summary used by the reference `GRCV3` backend.

### A.4 Canonical sign convention initialization

The signed Hessian convention is
$$
\widetilde H_i := s_H H_i,
\qquad s_H\in\{+1,-1\}.
$$

The canonical initialization procedure is:

1. On the initial calibrated state (or a short burn-in window), collect candidate basin seeds from the sink-based identity layer.
2. Evaluate both choices $s_H=+1$ and $s_H=-1$.
3. Choose the sign that maximizes agreement between:
   - small gradient norm,
   - positive-definite signed Hessian,
   - and sink-seed membership.
4. Serialize the chosen `hessian_sign` once and keep it fixed for the whole run unless the implementation explicitly supports recalibration.

### A.5 Required serialization for non-reference backends

If the implementation does not use this reference backend, the snapshot must still include enough metadata to reproduce the discrete differential summaries:

- `frame_mode`
- `curvature_backend`
- `differential_backend`
- backend parameters for local basis, regression weights, and regularization
