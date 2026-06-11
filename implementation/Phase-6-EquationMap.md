# Phase 6 Equation Map

This document maps the `GRC9` paper/spec objects onto the planned code
structure.

Its purpose is to answer, before the implementation expands:

- where each major paper object will live,
- which runtime hook owns it,
- which backend or family config surface controls any constitutive variation,
- how it is serialized,
- and how it is tested directly.

This is the paper-to-code anchor for Phase 6.

## Scope

This map covers the baseline `GRC9` realization defined by:

- [`../papers/2026-04-GRC-9.md`](../papers/2026-04-GRC-9.md)
- [`../specs/grc-9-spec.md`](../specs/grc-9-spec.md)
- [`Phase-6-ImplementationPlan.md`](./Phase-6-ImplementationPlan.md)

It covers the pure `GRC9` mechanical substrate only.

It does not define:

- `GRC9V3` basin attributes,
- signed-Hessian semantics,
- hierarchy,
- or choice/collapse logic.

Those belong to Phase 7 unless the phase boundary is explicitly revised.

## Phase 6 Backend And Config Surface

These are the Phase 6 public backend/config categories and defaults:

| Category / config surface | Default | Other public names currently reserved |
| --- | --- | --- |
| `geometry` / `frame_mode` | `fixed_port_chart` | none reserved yet |
| `metric` | `tensor_exponential` | none reserved yet |
| `curvature` | `none` | `forman`, `ollivier` |
| `spark` | `mechanical_saturation_with_instability_or_column_proxy` | `mechanical_saturation`, `mechanical_saturation_with_column_proxy` |
| `birth` | `outward_flux_parent_selection` | none reserved yet |
| `coarse_graining` | `exact_column_profile` | `signed_flux_split` |
| `boundary_mode` | `prune` or omitted | `barrier`, `ghost` reserved until explicit boundary behavior and `boundary_barrier` support are implemented |
| `expansion_distribution_mode` | `equal` | `custom` |
| `edge_label_selection` | `all` | subset modes may be added later |

Shared config surfaces kept outside the backend registry:

- `boundary_mode`
- `expansion_distribution_mode`
- `edge_label_selection`

## Planned Code Ownership

The default ownership plan is:

| Concern | Planned owner |
| --- | --- |
| Public `GRC9` model class / step orchestration | `src/pygrc/models/grc_9.py` |
| Pure port helpers and row/column membership helpers | `src/pygrc/models/grc_9_ports.py` |
| `PortEdge` and `GRC9State` | `src/pygrc/models/grc_9_state.py` |
| Tensor, metric, potential, flux, and basin helpers | `src/pygrc/models/grc_9_runtime.py` |
| Spark expansion and growth helpers | `src/pygrc/models/grc_9_expansion.py` |
| Column coarse-graining / Split helpers | `src/pygrc/models/grc_9_coarse.py` |
| Shared backend-selection datatypes | existing `src/pygrc/core/backends.py` |
| Shared snapshot encoding / decoding | existing Phase 3 serializer path |

Exact filenames may still evolve, but this ownership boundary should remain.

## State Carrier Map

## `PortEdge`

Spec object:

```python
@dataclass
class PortEdge:
    node_u: NodeId
    port_u: PortId
    node_v: NodeId
    port_v: PortId
    conductance: float
    flux_uv: float
```

Planned code carrier:

- `src/pygrc/models/grc_9_state.py`

Canonical runtime convention:

- `PortEdge` stores one canonical endpoint ordering
- baseline ordering is by ascending `node_id`
- oriented flux views are derived from this canonical carrier rather than stored
  twice

Direct tests:

- `tests/models/test_grc_9_state.py`
- `tests/models/test_grc_9_runtime.py`

## `GRC9State`

Spec object:

```python
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

Planned code carrier:

- `src/pygrc/models/grc_9_state.py`

Required structured additions from the Phase 6 plan:

- typed `expansion_registry` entries containing:
  - `parent_sink_id`
  - `module_node_ids`
  - `expansion_step`
  - `distribution_weights`
  - optional in-progress schedule metadata
- `prev_column_diagnostic: dict[NodeId, list[float]]` if sign-crossing support
  is enabled
- deterministic replay support through explicit `rng_state`

Direct tests:

- `tests/models/test_grc_9_state.py`
- `tests/models/test_grc_9_serialization.py`

## Row-Diagonal Tensor Representation

Paper object:

$$
K_i^{(k)}=
\lambda_C\,C_i^{(k)}\,I
+\xi_C\sum_{a=1}^{3}\Biggl(\sum_{j:\ (i,j)\in \mathcal T_i^{(a)}} w_{ij}^{(k)}\bigl(C_{j}^{(k)}-C_i^{(k)}\bigr)^2\Biggr)\mathbf e_a\otimes\mathbf e_a
+\zeta_C\Bigl(\sum_{j\in\mathcal N(i)}J_{ij}^{(k)}\Bigr)^2 I.
\tag{1}
$$

Planned runtime carrier:

- a compact row-diagonal payload, not a dense 3x3 matrix
- baseline choice:
  - `dict[ModeRow, float]`
  - or one ordered length-3 sequence

Inspectability rule:

- `K_i` does not need to be persisted in snapshots
- but it must remain inspectable through deterministic runtime access, such as:
  - a typed cached/runtime field
  - or a helper/debug surface that reconstructs the current row-diagonal tensor
    from the current state without ambiguity

Owner:

- `src/pygrc/models/grc_9_runtime.py`

Direct tests:

- `tests/models/test_grc_9_tensor.py`

## Operator Map

| Paper object | Paper anchor | Planned hook | Backend / config owner | Planned code owner | Serialized evidence | Direct test target |
| --- | --- | --- | --- | --- | --- | --- |
| Port index map `r <-> (a,b)` | paper Sec. 1.2, spec topology requirements | helper-level, used everywhere | family-fixed baseline | `grc_9_ports.py` | not required as stored state | `test_grc_9_state.py` |
| Row set `T_i^(a)` | Eq. (1) setup | `_compute_geometry()` | family-fixed baseline | `grc_9_runtime.py` | recomputable from topology + port helpers | `test_grc_9_tensor.py` |
| Local coherence tensor `K_i` | Eq. (1) | `_compute_geometry()` | `geometry = fixed_port_chart` | `grc_9_runtime.py` | optional diagnostic only; not required in snapshots | `test_grc_9_tensor.py` |
| Edge conductance `w_ij` / occupied port-pair conductance | Eq. (2) | `_compute_metric()` | `metric`, `curvature` | `grc_9_runtime.py` | `port_edges[*].conductance` | `test_grc_9_runtime.py` |
| Curvature term `kappa^Ric_ij` | Eq. (2), Appendix A note | `_compute_metric()` | `curvature_backend` | `grc_9_runtime.py` | config + backend selection + optional diagnostics | `test_grc_9_runtime.py` |
| Coherence functional `P[C]` | Eq. (3) | `_compute_potential()` conceptually | family-fixed baseline | `grc_9_runtime.py` | not required as stored state | `test_grc_9_runtime.py` |
| Node potential `Phi_i` | Eq. (4) | `_compute_potential()` | family-fixed baseline | `grc_9_runtime.py` | `potential` | `test_grc_9_runtime.py` |
| Flux `J_ij` | Eq. (5) | `_compute_flux()` | family-fixed baseline | `grc_9_runtime.py` | `port_edges[*].flux_uv` via canonical orientation | `test_grc_9_runtime.py` |
| Continuity update | Eq. (6) | `_apply_continuity()` | family-fixed baseline | `grc_9.py` / `grc_9_runtime.py` | post-step `node_coherence` | `test_grc_9_step.py` |
| Exact budget target `B` | Eq. (7) | state construction / `_enforce_budget()` fallback | family-fixed baseline | `grc_9.py` | `budget_target`, `budget_target_source`, `remainder`, observables | `test_grc_9_step.py` |
| Uniform shift rule | Sec. 7.1 | `_enforce_budget()` | family-fixed baseline | `grc_9.py` | post-step state / observables | `test_grc_9_step.py` |
| Simplex projection fallback | Sec. 7.2 | `_enforce_budget()` | family-fixed baseline | `grc_9.py` | post-step state / observables | `test_grc_9_step.py` |
| Successor map `f(i)` | Eq. (8) | `_detect_identities()` | family-fixed baseline | `grc_9_runtime.py` | optional diagnostics; not required in snapshot | `test_grc_9_runtime.py` |
| Sink set `S` | Eq. (9) | `_detect_identities()` | family-fixed baseline | `grc_9_runtime.py` | `sink_set` | `test_grc_9_runtime.py` |
| Basin `B_s` | Eq. (10) | `_detect_identities()` | family-fixed baseline | `grc_9_runtime.py` | `basins` | `test_grc_9_runtime.py` |
| Column diagnostic `H_s^(b)` | Eq. (11) | `_compute_column_diagnostic()` / `_detect_events()` | `spark` | `grc_9_runtime.py` or `grc_9.py` | optional diagnostics, previous-step cached values if sign-crossing is enabled | `test_grc_9_runtime.py` / `test_grc_9_step.py` |
| Spark predicate `Spark(s)` | Eq. (12) | `_detect_events()` | `spark` | `grc_9.py` / `grc_9_expansion.py` | event log + optional diagnostics | `test_grc_9_step.py` |
| Expansion size `n(D_eff)` | Eq. (13) | `_apply_topology_changes()` | family-fixed baseline under expansion policy | `grc_9_expansion.py` | expansion registry / event payload | `test_grc_9_expansion.py` |
| Canonical internal spine | Eq. (14) | `_apply_topology_changes()` | family-fixed baseline | `grc_9_expansion.py` | expansion registry / topology snapshot | `test_grc_9_expansion.py` |
| Boundary reassignment by column | Eq. (15) | `_apply_topology_changes()` | family-fixed baseline | `grc_9_expansion.py` | topology snapshot / event payload | `test_grc_9_expansion.py` |
| Coherence transfer `C_s -> {s1,s2,s3,c}` | Eq. (16) | `_apply_topology_changes()` | `expansion_distribution_mode` | `grc_9_expansion.py` | expansion registry / post-event node coherence | `test_grc_9_expansion.py` |
| Front growth rule | Sec. 8.4 | `_apply_growth()` | `birth` + family deterministic port rule | `grc_9_expansion.py` | topology snapshot / event payload | `test_grc_9_expansion.py` |
| Abundance | Eq. (17) | `compute_observables()` | family-fixed baseline | `grc_9.py` | observables | `test_grc_9_step.py` |
| Column total `\bar X` | Eq. (18) | `coarse_grain_columns(...)` | `coarse_graining` | `grc_9_coarse.py` | `coarse_cache` or returned coarse state | `test_grc_9_coarse.py` |
| Intra-column profile `pi^X` | Eq. (19) | `coarse_grain_columns(...)` | `coarse_graining` | `grc_9_coarse.py` | `coarse_cache` or returned coarse state | `test_grc_9_coarse.py` |
| Coarse-graining operator `G(X)` | Eq. (20) | `coarse_grain_columns(...)` | `coarse_graining` | `grc_9_coarse.py` | returned coarse state / optional cache | `test_grc_9_coarse.py` |
| Exact Split | Eq. (21) | `split_columns(...)` | `coarse_graining` | `grc_9_coarse.py` | returned fine state / optional cache | `test_grc_9_coarse.py` |
| Invertibility claim | Eq. (22), Lemma 1 | coarse-graining verification | `coarse_graining` | `grc_9_coarse.py` | not a stored field; proven by tests | `test_grc_9_coarse.py` |
| Exact signed-flux decomposition | Sec. 9.1 | `coarse_grain_columns(...)` / `split_columns(...)` | `coarse_graining = signed_flux_split` | `grc_9_coarse.py` | returned coarse state / optional cache | `test_grc_9_coarse.py` |
| Compressed signed-flux mode | Sec. 9.1 | optional diagnostic-only path | optional extension | `grc_9_coarse.py` | explicitly labeled non-exact diagnostics if implemented | `test_grc_9_coarse.py` |

## Spark Semantics Note

The baseline `GRC9` spark rule is intentionally mechanical.

The implementation anchor is therefore:

- `deg_act(s) == 9`
- and either:
  - `Instability(s) >= tau_instability`
  - or `min_b |H_s^(b)| < eps_spark`

Phase 6 implementation decisions fixed by the plan:

- the optional near-saturation rule `deg_act >= 8` is deferred unless the phase
  is explicitly re-scoped
- the baseline instability proxy is defined exactly as:
  - `U(s) = {s} ∪ N(s)`
  - `cut_out(U)` = sum of occupied-port-pair conductances with exactly one
    endpoint in `U`
  - `support_in(U)` = sum of occupied-port-pair conductances with both
    endpoints in `U`
  - `Instability(s) = cut_out(U) / max(cut_out(U) + support_in(U), eps)`
- spark handling is sequential, not batch-applied
- `SparkKind` should remain explicit:
  - `saturation_instability`
  - `saturation_column_proxy`
  - `saturation_sign_crossing`
- one eligible sink should receive one deterministic spark classification with
  explicit precedence:
  - `saturation_instability`
  - then `saturation_column_proxy`
  - then `saturation_sign_crossing`
- `prev_column_diagnostic` should be persisted on each spark-detection pass for
  replay/debugging and telemetry even when sign-crossing support is disabled;
  the sign-crossing predicate is what remains optional

This is not a hidden `GRC9V3` lift.
If later work wants basin-Hessian semantics, that belongs in Phase 7.

## Expansion Semantics Note

The canonical `GRC9` expansion operator owns four constitutive commitments:

1. the parent sink is replaced by a connected module
2. old boundary edges are reassigned by column family
3. new boundary capacity remains explicit as inactive ports
4. budget is verified immediately after expansion and corrected only if drift is
   detected

Phase 6 default conventions fixed by the plan:

- internal spine:
  - `(c,2) <-> (s1,5)`
  - `(c,5) <-> (s2,5)`
  - `(c,8) <-> (s3,5)`
- if `n > 4`, extra nodes form a tree under the satellites:
  - round-robin by column
  - using port `5` on the new node
  - using the lowest-index available port on the existing tree node
- state transfer defaults:
  - `C_c = 0`
  - `p_b = 1/3`
- if a satellite inherits no boundary edges and local aggregate bond
  initialization is therefore undefined, fall back to fixed `w_bond`

## Growth Semantics Note

The paper gives two distinct decisions that must not be conflated:

- parent selection may depend on outward flux pressure
- chosen-port selection is deterministic and always uses the lowest-index
  inactive port on the selected parent

The Phase 6 config surface keeps those separate:

- `birth = outward_flux_parent_selection`
- deterministic lowest-index port choice remains family-fixed, not a backend
  branch

## Hook Order Map

The exact implemented Phase 6 baseline runtime order is recorded in
[`Phase-6-StepLoop.md`](./Phase-6-StepLoop.md).

At a high level, the loop makes four `GRC9`-specific commitments explicit:

1. row-organized geometry is built before metric update
2. spark detection happens only after successor/sink/basin extraction
3. topology events happen before continuity
4. coarse-cache refresh or invalidation happens after budget closure, not
   before

The spec-level step order is authoritative for implementation.
The paper’s compact algorithmic loop does not break out a separate
boundary-management step, so the discrete spec order should be treated as the
implementation reference.

## Serialization Map

The following pieces must be serialized explicitly rather than left implicit:

- canonical params and resolved params
- backend selections by category when used
- `frame_mode`
- `curvature_backend`
- `boundary_mode` if implemented; Phase 6 currently serializes only the
  executable `prune` baseline and should reject reserved `barrier` / `ghost`
  modes before runtime
- `expansion_distribution_mode`
- `edge_label_selection`
- port occupancy
- port-edge structure
- node coherence
- selected analytic edge-label families
- `edge_label_computation_mode`
- `edge_label_params`
- expansion in-progress state
- optional coarse-cache metadata if cache state is persisted
- `rng_state`

The following may remain recomputable if clearly documented:

- row-diagonal tensor `K_i`
- successor map
- the functional `P[C]`
- raw column diagnostics when they are not needed for replaying a deferred
  sign-crossing branch

## Test Class Map

The minimum direct test surface should include:

| Test file | Primary evidence |
| --- | --- |
| `tests/models/test_grc_9_state.py` | state dataclasses, invariants, param resolution, port helpers |
| `tests/models/test_grc_9_tensor.py` | row tensor and row/column semantics |
| `tests/models/test_grc_9_runtime.py` | metric, potential, flux, successor map, sinks, basins |
| `tests/models/test_grc_9_expansion.py` | spark trigger, expansion, rewiring, growth |
| `tests/models/test_grc_9_coarse.py` | coarse-graining, Split, exactness, invalidation |
| `tests/models/test_grc_9_serialization.py` | snapshot roundtrip and replay identity |
| `tests/models/test_grc_9_step.py` | ordered step-loop behavior, event integration, and `SparkKind` determinism |

## Explicit Open Questions To Resolve During Implementation

These are acceptable implementation-time decisions, but they must not remain
implicit:

1. whether the baseline stores row-diagonal tensor state only ephemerally or
   keeps it in typed runtime state/cache
2. align the runtime with the documented persistence rule for
   `prev_column_diagnostic: dict[NodeId, list[float]]` on every spark-detection
   pass, even though sign-crossing consumption remains optional
3. whether the first exact signed-flux coarse path is exposed only through the
   public coarse methods, or also cached in `coarse_cache`
4. whether the first representative artifact lane needs a family-local telemetry
   extension or can ride entirely on the shared surfaces

These should be resolved explicitly in implementation notes, not left to
emerge accidentally from code shape.
