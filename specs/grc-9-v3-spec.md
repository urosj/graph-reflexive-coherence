# GRC9V3 Specification

Source papers:

- `papers/2026-04-GRC-9.md`
- `papers/2026-02-GRC-V3.md`

Implemented Phase 7 contract:

- [`../implementation/Phase-7-ImplementationPlan.md`](../implementation/Phase-7-ImplementationPlan.md)
- [`../implementation/Phase-7-EquationMap.md`](../implementation/Phase-7-EquationMap.md)
- [`../implementation/Phase-7-StepLoop.md`](../implementation/Phase-7-StepLoop.md)
- [`../implementation/Phase-7-ImplementationChecklist.md`](../implementation/Phase-7-ImplementationChecklist.md)
- [`../implementation/Phase-7-MidGate-Review.md`](../implementation/Phase-7-MidGate-Review.md)
- [`../implementation/Phase-7-RepresentativeRuntime.md`](../implementation/Phase-7-RepresentativeRuntime.md)
- [`../implementation/Phase-7-Closeout.md`](../implementation/Phase-7-Closeout.md)

Verification profile:

- [`grc-9-v3-evidence-profile.md`](grc-9-v3-evidence-profile.md)

This file is the normative contract for the legacy synchronous `GRC9V3`
profile. The evidence profile records the bounded verification basis for the
causal-state and retention boundaries below. Experimental counts and search
results do not define runtime semantics by themselves.

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

Serialization of a field does not by itself make that field an independent
complete-step causal coordinate. On verified smooth, fixed-topology,
event-free strata, `coherence` (`C`) is the admitted independent complete-step
coordinate. Differential summaries, `base_conductance` (`W`), potential, and
port-edge flux (`J`) are load-bearing within a beat, but are reconstructed or
stage-dependent under the baseline step contract. Topology, registries, event
state, RNG state, and reset-baseline state remain lifecycle state and are not
covered by that smooth-stratum coordinate statement.

## Complete-Step Causal-State Semantics

Baseline `GRC9V3` is a synchronous graph-RC realization with immediate
constitutive recurrence. On the verified fixed-topology, event-free profile,
the relevant stage relation is:

```text
incoming C and port-edge J
  -> differential summaries
  -> W from C, gradient differences, and sign-even incoming J^2
  -> potential from C and W
  -> fresh potential-flow J
  -> continuity update of C
  -> final reconstruction of differential, transport, and identity surfaces
```

The runtime stores `W`, potential, labels, and `J` so a complete snapshot can
be restored and inspected exactly under the applicable restoration contract.
That storage does not change their causal type:

- `W` is recomputed from current coherence, differential summaries, and the
  incoming edge flux magnitude before fresh potential and flux are computed;
- the incoming-current term is quadratic and sign-even, so it can carry
  magnitude or an unoriented-axis effect but not historical current direction;
- fresh `J` is reconstructed from the current scalar conductance and potential
  difference; and
- the final refresh reconstructs these surfaces again after continuity,
  boundary, growth, event, and budget stages.

Consequently, baseline `W` and `J` must not be advertised as independent slow
coordinates merely because they are serialized or participate causally within
the beat. A revision that gives either field independent complete-step
evolution, relaxation, or retained-state authority is a new constitutive
profile and must be specified separately.

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

1. rebuild row-based gradient, Hessian, flux-summary, and node-tensor surfaces
   from the incoming complete-step state;
2. rebuild scalar conductance from coherence, gradients, and incoming
   current-squared;
3. compute pre-flux labels, potential, fresh potential-flow current, and
   post-flux labels;
4. refresh differential summaries against the fresh current;
5. rebuild sink, basin, geometric-seed, and basin-mass identity surfaces;
6. detect spark candidates, execute any admitted mechanical expansion, and
   register completed sparks only after child-basin stabilization;
7. update optional choice/collapse/learning state;
8. apply configured growth and boundary behavior;
9. apply the continuity update;
10. enforce the quadrature-style budget;
11. rebuild pre-transport differential surfaces, transport surfaces,
    post-transport differential surfaces, and identity surfaces for the final
    complete-step state;
12. refresh/invalidate coarse-state cache, compute observables, and advance the
    step index and synchronous time.

The ordering is causal, not presentational. In particular, callers must not
interpret incoming stored `W` or `J` as independent state that bypasses the
reconstruction stages. Reduced or frozen-surface experiments may hold a stage
surface fixed for analysis, but that does not change the native `step()`
contract.

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

The legacy `learning` name on this event surface denotes the configured
post-collapse state-change and event bookkeeping defined by the Phase 7
contract. It does not assert retained memory, adaptive learning, agentic
learning, or core Read-Back.

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

## Historical Persistence, Retention, And Read-Back

The legacy profile distinguishes four claims that must not be collapsed:

```text
constitutive recurrence
  a field participates in the ordered native step and changes a later stage

ordinary state persistence
  a complete-step coordinate remains displaced on later beats

retained historical sector
  a separately identified post-driver carrier persists relative to its
  reference branch and has an admitted formation/update relation

Read-Back
  a later present-current-conditioned directional read relation consumes an
  admitted retained sector under the required passive and rival controls
```

Baseline `GRC9V3` specifies the first relation. It does not specify a distinct
retained-state primitive, constitutive retained-sector projector,
retained-carrier update law, or native read current. An analysis-only projector
or observer surface derived from existing state does not by itself add a
runtime causal object.

The stage-local path from incoming current magnitude into conductance is real:

```text
incoming J^2 -> reconstructed W -> potential -> fresh J -> later C
```

It is not by itself a retained-history implementation. In particular:

- `base_conductance` is a load-bearing mechanical transport field, but its
  baseline complete-step value is reconstructed and must not be called durable
  memory merely because incoming current contributes to that reconstruction;
- the quadratic current contribution is sign-even and does not retain
  historical current orientation;
- potential-flow current is freshly reconstructed, so incoming orientation is
  not a native independently relaxing current coordinate; and
- persistence of `C` alone may be ordinary state continuation, neutral
  coordinate displacement, or branch relocation and does not establish a
  separate retained historical sector.

The bounded B1-GR and B2-GR evidence supporting this type boundary is recorded
in [`grc-9-v3-evidence-profile.md`](grc-9-v3-evidence-profile.md). That evidence
does not establish that GRC9V3 can never form a retained carrier, that retention
is globally absent, or that any particular replacement mechanism is required.

Any future profile that introduces independent conductance/current relaxation,
a new retained causal carrier or update law, a retained-sector projector that
is consumed constitutively by the runtime, or native Read-Back changes the
constitutive causal state. It must use a revision-distinct specification and
capability/profile identity rather than reinterpret this legacy contract.
Analysis-only projectors or observer surfaces do not by themselves define a new
runtime profile.

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
