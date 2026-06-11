# GRCV2 Specification

Source paper: `papers/2025-12-GRC-V2.md`

## Purpose

`GRCV2` is the baseline weighted-graph implementation of Reflexive Coherence:

- scalar coherence on nodes,
- one conductance weight per edge,
- three optional analytic edge labels on the same edge set,
- one directed flux per edge,
- graph functional and potential,
- sink/basin extraction,
- proxy spark detection,
- soft split,
- front birth,
- pruning,
- exact budget preservation.

It is the simplest full graph class in the library.

## Class

```python
class GRCV2(GRCModel):
    ...
```

## Capabilities

`GRCV2.list_capabilities()` must include:

- `single_weight_edges`
- `multi_metric_edges`
- `identity_basins`
- `proxy_sparks`
- `soft_split`
- `front_birth`
- `budget_preservation`

`GRCV2.list_capabilities()` may additionally include:

- `intrinsic_frame`
- `host_embedding_frame`
- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

It must not claim:

- `basin_attributes`
- `hierarchy_tracking`
- `choice_collapse_semantics`
- `quadrature_budget`
- `port_graph`
- `mechanical_refinement`
- `column_coarse_graining`

## State Specification

```python
@dataclass
class GRCV2State(GRCState):
    nodes: dict[NodeId, float]                  # C_i
    edges: dict[EdgeId, float]                  # w_ij
    geometric_length: dict[EdgeId, float]
    temporal_delay: dict[EdgeId, float]
    flux_coupling: dict[EdgeId, float]
    flux: dict[OrientedEdgeId, float]           # J_ij
    potential: dict[NodeId, float]              # Phi_i
    sink_set: set[NodeId]
    basins: dict[NodeId, set[NodeId]]
    split_registry: dict[str, Any]
    rng_state: Any | None
```

Minimum node quantity:

- `C_i`

Minimum edge quantities:

- `w_ij`
- `J_ij`

## Parameters

Required parameters:

- `dt`
- `alpha`, `beta`, `gamma`, `delta`
- `eta`
- `kappa_c`
- `lambda_c`, `xi_c`, `zeta_c`
- site potential selection and potential parameters
- `eps_spark` or `h_thr`
- `tau_split`
- `lambda_birth`
- `alpha_seed`
- `eps_prune`
- explicit `curvature_backend`
- explicit `frame_mode`
- explicit `boundary_mode`
- explicit `split_distribution_mode`
- `edge_label_selection`

Optional reproducibility parameter:

- `rng_seed`

`curvature_backend` must be one of:

- `ollivier`
- `forman`
- `none`

When `curvature_backend` is `forman` or `ollivier`, the implementation must provide a
real in-house weighted-substrate curvature computation for the named backend rather than
silently substituting a placeholder surrogate under the same public mode name.

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

## Required Step Semantics

Each `step()` must perform:

1. compute node tensors `K_i`
2. compute edge conductances `w_ij`
3. compute selected analytic edge labels:
   geometric length, temporal delay, flux coupling
4. build/update graph Laplacian if required
5. compute node potentials `Phi_i`
6. compute edge fluxes `J_ij`
7. detect sink set and attraction basins
8. detect sparks using eigenvalue or Cheeger proxy
9. apply soft-split initialization/progression
10. apply front birth
11. apply configured boundary behavior
12. apply continuity update to `C_i`
13. enforce exact budget preservation
14. compute observables

## Tensor and Metric

`GRCV2` must implement the node tensor and exponential conductance map of the v2 paper.

Required interpretation:

- the edge weight is the single dynamical conductance,
- the analytic edge labels are derived from the same graph state but do not replace the dynamical conductance,
- curvature term is optional but supported,
- local gradient pressure is reconstructed from neighbors, not stored as a node attribute.

## Edge Labels

`GRCV2` must support the shared analytic edge-label family:

- `geometric_length`
- `temporal_delay`
- `flux_coupling`

Selection is controlled by `edge_label_selection`, whose default is `"all"`.

When all three labels are selected, any selected label that cannot be computed from a stronger ambient or induced geometry must still be populated using the common-interface availability contract and tagged with the corresponding computation mode metadata.

The update equations continue to use only the single dynamical conductance `w_ij`. The analytic labels are interpretive products of the same state and do not turn `GRCV2` into a basin-attribute model.

If an implementation adds channel-specific or tensor-derived edge transport beyond the single scalar conductance rule, it must advertise `anisotropic_edges` explicitly rather than implying that the baseline `GRCV2` conductance already carries full continuum anisotropy.

## Boundary Semantics

The implementation must expose its boundary handling rule explicitly through `boundary_mode`.

- `prune` is the baseline graph-regularization rule for `GRCV2`.
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

If `frame_mode` is `induced_local_frame` or `combinatorial`, the implementation must document the deterministic rule by which geometric edge labels and any curvature backend inputs are constructed from the graph.

`list_capabilities()` must include exactly one of:

- `host_embedding_frame`
- `intrinsic_frame`

## Identity Basins

Identity extraction is flux-topology based:

- directed edge `i -> j` when `J_ij > 0`
- sink `s` requires:
  - `J_js >= 0` for every incident neighbor `j`
  - `sum_j J_js > 0`
- basin from repeated successor composition

No explicit basin attribute object is required.

## Sparks

`GRCV2` must support at least one of:

1. restricted Laplacian eigenvalue trigger
2. Cheeger conductance proxy trigger

The implementation may support both.

If both are available, the public config must allow choosing one.

## Topology Events

### Soft split

Soft split is the canonical topology response to sparks in this class.

Requirements:

- parent sink is not deleted immediately,
- child masses are initialized from a parent split ratio,
- edge weights evolve over `tau_split`,
- removal of the parent occurs only after split completion.

## Split Distribution Rule

Baseline single-field `GRCV2` uses a deterministic split-distribution rule controlled by `split_distribution_mode`.

- `equal` is the default and means the parent split mass is divided equally among the initialized children.
- `custom` is reserved for a documented alternative implementation rule and must serialize the extra parameters needed to reproduce it.

The reference implementation starts with `equal` as the authoritative rule. More complex asymmetry heuristics are allowed later, but they must not replace the default baseline silently.

### Birth

Birth is driven by outward flux pressure at frontier nodes.

Requirements:

- Bernoulli birth probability following the paper-facing rule
- new node creation,
- seed mass transfer from parent,
- seed edge creation,
- budget preservation immediately afterward.

The public `lambda_birth` parameter controls the Bernoulli birth law rather than a hard
threshold rule.

If `rng_state` is stored, it must be sufficient to replay the stochastic birth path
deterministically on load. If `rng_seed` is provided, it must seed the model's runtime
RNG deterministically without changing the Bernoulli birth semantics into a threshold
approximation.

### Pruning

Pruning removes non-viable isolated low-mass nodes and redistributes remaining mass.

If `boundary_mode` is `barrier` or `ghost`, the implementation may replace this pruning pass with the configured boundary-preservation rule while keeping exact budget preservation explicit.

## Temporal and Causal Semantics

`temporal_delay` is an analytic propagation label. In baseline `GRCV2`, it must not be presented as proper time or as a complete discrete Lorentzian metric.

If an implementation adds lapse/shift-like data, causal cones, or other explicit spacetime structure, it must advertise `causal_layer` explicitly and serialize the extra causal-state fields needed to make that layer reproducible.

## Scale Semantics

Baseline `GRCV2` is a single-scale graph realization. It does not require a scale-indexed coherence field.

If an implementation carries multi-scale coherence values, scale-coupling operators, or an explicit discrete analogue of the FRC $\sigma$ coordinate, it must advertise `multiscale_sigma` explicitly and serialize the corresponding scale-state data.

## Observables

Required observables:

- `abundance`
- `weighted_abundance`
- `sink_count`
- `budget_current`
- `budget_error`
- `num_nodes`
- `num_edges`

Recommended observables:

- `spark_count`
- `birth_count`
- `prune_count`
- average conductance

## Serialization

A `GRCV2` snapshot must include:

- node coherence values,
- edge conductances,
- selected analytic edge-label families,
- `edge_label_computation_mode`,
- `edge_label_params`,
- edge fluxes,
- potentials,
- sink/basin cache if stored,
- split-progress state,
- `curvature_backend`,
- `frame_mode`,
- `boundary_mode`,
- `split_distribution_mode`,
- `edge_label_selection`,
- params,
- RNG state if used.

For stochastic birth replay, the serialized state must preserve the RNG state in a form
that is sufficient to reproduce subsequent Bernoulli birth draws deterministically.

## Explicit Non-Goals

`GRCV2` does not attempt to store:

- gradient vectors,
- Hessian tensors,
- hierarchy labels,
- explicit basin-attribute objects.

Those belong to `GRCV3`.
