# Common GRC Class and Interface Specification

## Purpose

All GRC implementations share the same reflexive core:

$$
C \rightarrow K[C] \rightarrow w \rightarrow \Phi \rightarrow J \rightarrow C.
$$

The library therefore needs one common abstract interface for:

- model lifecycle,
- state serialization,
- stepping and event handling,
- observables,
- reproducibility,
- and capability discovery.

This spec defines the Python contract that every concrete implementation must satisfy.

## Design Goals

1. Keep the common interface small.
2. Preserve theoretical differences between model families instead of hiding them.
3. Make simulations scriptable and serializable.
4. Support deterministic and stochastic variants without changing the public API.
5. Support stepping, inspection, and event logging.

## Core Concepts

### Abstract model

Every implementation is a subclass of an abstract base:

```python
class GRCModel(ABC):
    ...
```

The base class represents a configured simulation engine plus its mutable state.

### State

Every model owns a `GRCState` object, which contains:

- topology,
- node values,
- edge values,
- time-step index,
- physical time,
- conserved budget bookkeeping,
- cached derived quantities,
- event log since last step or snapshot.

`GRCState` may be subclassed by each concrete model family.

### Parameters

Every model owns an immutable or effectively immutable parameter object:

```python
@dataclass(frozen=True)
class GRCParams:
    dt: float
    ...
```

Concrete variants define stricter parameter subclasses.

Parameters are a **first-class model contract**, not loose globals. Any quantity that changes the actual model evolution must belong either to `GRCParams` itself or to an explicitly nested sub-record inside it.

## Parameter Domains

The common interface distinguishes four parameter domains.

### 1. Evolution parameters

These directly affect the discrete equations or topology events and therefore belong to the core model params.

Examples:

- transport and constitutive coefficients,
- spark thresholds,
- split / birth / refinement coefficients,
- budget / measure semantics,
- edge-label selection when label families are part of model output.

### 2. Constitutive and semantic mode parameters

These choose how the model should be interpreted or constructed and therefore also belong to the core params.

Examples:

- `frame_mode`,
- `boundary_mode`,
- `measure_mode`,
- `curvature_backend`,
- `edge_label_selection`.

### 3. Numerical backend parameters

These belong to the core params only when they affect the mathematical result of the step logic rather than only performance.

Examples:

- regularization strengths,
- local regression weights,
- Hessian backend selection,
- approximation backend choices that change computed values.

### 4. Runtime, observer, and tooling parameters

These do **not** belong to the core model params unless they explicitly change the evolution equations.

Examples:

- device placement (`cpu`, `cuda`, sharding),
- snapshot cadence,
- storage mode,
- viewer / renderer settings,
- telemetry emission settings,
- machine-driver patch policy,
- observer comparison policy,
- readback / instrumentation contracts.

These belong to the integration layer, embedding layer, or external runtime configuration.

## Parameter Boundary Rule

The boundary is:

- if changing the value changes the model state trajectory for the same initial state and RNG seed, it is a core model parameter,
- if changing the value only changes execution environment, inspection, storage, or reporting, it is not a core model parameter.

If a family intentionally promotes a normally external policy into an evolution-affecting mechanism, that promotion must be made explicit in the family spec and serialized as part of the params.

## Parameter Anti-Patterns

The parameter architecture is intended to prevent a specific class of design failures.

Implementations should avoid:

- **parameter drift into globals**
  - evolution coefficients or constitutive modes living as module-level constants, mutable singleton state, or hidden environment overrides after construction
- **observer/runtime pollution of the core model**
  - telemetry, debugger, readback, viewer, storage, or device policies being stored in `GRCParams` even though they do not define the equations
- **silent non-reproducibility**
  - unresolved config differing from resolved runtime params, or environment-dependent behavior changing results without being reflected in serialized params
- **semantic ambiguity**
  - treating `frame_mode`, `boundary_mode`, `curvature_backend`, or similar constitutive choices as incidental implementation details rather than part of the model definition
- **cross-layer leakage**
  - integration or embedding policies accidentally changing the model trajectory without being explicitly promoted into evolution semantics

The purpose of these rules is not stylistic purity. It is to preserve:

- reproducibility,
- clear ownership boundaries,
- stable comparison across implementations,
- and the ability to reason about which layer is responsible when a run changes.

### Step result

Each call to `step()` returns a `StepResult`:

```python
@dataclass
class StepResult:
    step_index: int
    time: float
    events: list[GRCEvent]
    observables: dict[str, Any]
```

This is the minimum required return object.

## Required Public Interface

Every concrete class must provide the following methods.

### Construction

```python
@classmethod
def from_config(cls, config: Mapping[str, Any]) -> "GRCModel": ...
```

Creates a model from a JSON/YAML-friendly configuration mapping.

```python
@classmethod
def from_state(cls, state: Mapping[str, Any], params: Mapping[str, Any]) -> "GRCModel": ...
```

Restores a model from serialized state and parameters.

### State access

```python
def get_state(self) -> "GRCState": ...
def set_state(self, state: "GRCState") -> None: ...
def get_params(self) -> "GRCParams": ...
def snapshot(self) -> dict[str, Any]: ...
```

Rules:

- `get_state()` may return the live state object.
- `get_params()` must return the resolved parameter object actually governing the current model.
- `snapshot()` must return a serialization-safe deep representation.
- `set_state()` must validate compatibility with the model family.

### Simulation lifecycle

```python
def step(self) -> StepResult: ...
def run(self, num_steps: int) -> list[StepResult]: ...
def reset(self) -> None: ...
```

Rules:

- `step()` advances exactly one simulation step.
- `run()` is a convenience loop over `step()`.
- `reset()` restores the initial state used at construction time.

### Diagnostics

```python
def compute_observables(self) -> dict[str, Any]: ...
def list_capabilities(self) -> set[str]: ...
```

Capability flags are strings such as:

- `single_weight_edges`
- `basin_attributes`
- `multi_metric_edges`
- `port_graph`
- `mechanical_refinement`
- `choice_collapse_semantics`
- `quadrature_budget`
- `hierarchy_tracking`
- `intrinsic_frame`
- `host_embedding_frame`
- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

When a model advertises `multi_metric_edges`, the shared edge-label names are:

- `geometric_length`
- `temporal_delay`
- `flux_coupling`

### Serialization

```python
def save(self, path: str) -> None: ...
@classmethod
def load(cls, path: str) -> "GRCModel": ...
```

The storage format is implementation-defined, but it must preserve:

- params,
- resolved params,
- params hash or equivalent canonical identity,
- state,
- random generator state if stochastic,
- model family identifier,
- file format version.

## Recommended Internal Hooks

Concrete models should implement internal hooks with these names where possible:

```python
def _compute_geometry(self) -> None: ...
def _compute_metric(self) -> None: ...
def _compute_potential(self) -> None: ...
def _compute_flux(self) -> None: ...
def _detect_identities(self) -> None: ...
def _detect_events(self) -> list["GRCEvent"]: ...
def _apply_topology_changes(self, events: list["GRCEvent"]) -> None: ...
def _apply_continuity(self) -> None: ...
def _enforce_budget(self) -> None: ...
```

These are not public API requirements, but concrete implementations should map their step logic to this sequence.

## Shared Datatypes

### Base state

Minimum required fields:

```python
@dataclass
class GRCState:
    step_index: int
    time: float
    budget_target: float
    remainder: float | None
```

Concrete state subclasses must add their own node and edge storage.

### Events

All topology or semantic changes must be represented as typed events:

```python
@dataclass
class GRCEvent:
    kind: str
    step_index: int
    payload: dict[str, Any]
```

Event kinds may include:

- `spark`
- `soft_split`
- `birth`
- `prune`
- `expand`
- `merge`
- `collapse`
- `choice_detected`

Not every model family supports every event kind.

### Observables

Every model must expose at least:

- `budget_current`
- `budget_error`
- `num_nodes`
- `num_edges`
- `abundance`

Optional observables depend on capabilities.

## Shared Edge-Label Semantics

All model families use the same naming convention for edge-level transport quantities:

- `base_conductance`: the dynamical weight actually used by the update equations,
- `geometric_length`: an analytic label for induced geometric separation,
- `temporal_delay`: an analytic label for operational propagation delay,
- `flux_coupling`: an analytic label for functional exchange strength.

`base_conductance` is the update weight. The other three labels are analytic products of the same state unless a family explicitly documents otherwise.

When a model advertises `multi_metric_edges`, it must expose these exact three analytic names even if the internal storage is edge-based, port-pair-based, or computed lazily.

## Analytic Edge Label Availability

When `edge_label_selection="all"`, the implementation must populate all three analytic edge-label families. If a selected label cannot be computed in the strongest ambient-geometric sense because of the constitutive choices of the model, the implementation must still populate that label using the best family-consistent construction and record how it was obtained.

Required rules:

- `flux_coupling` must be computed as the absolute directed exchange magnitude on the selected storage substrate:
  $$
  \mathrm{flux\_coupling}_{ij} := |J_{ij}|.
  $$
- `geometric_length` may be computed in one of three ways:
  - `ambient_metric`: from an ambient displacement or host-supplied geometry,
  - `induced_intrinsic`: from an induced local basis or intrinsic chart construction,
  - `intrinsic_surrogate`: from a graph-intrinsic monotone surrogate when no stronger geometric construction is available.
- `temporal_delay` must be derived from the chosen `geometric_length` and `flux_coupling` labels using the standard transport-ratio form
  $$
  \mathrm{temporal\_delay}_{ij}
  =
  \frac{\mathrm{geometric\_length}_{ij}}{v_0 + \rho\,\mathrm{flux\_coupling}_{ij} + \varepsilon_\tau},
  \qquad v_0,\rho,\varepsilon_\tau > 0,
  $$
  unless a family spec explicitly defines a different formula.

Every implementation that advertises `multi_metric_edges` must serialize:

- `edge_label_selection`,
- `edge_label_computation_mode`: a mapping from label family name to computation mode string,
- `edge_label_params`: any parameters needed to reproduce the selected label construction.

Recommended mode strings are:

- for `geometric_length`: `ambient_metric`, `induced_intrinsic`, `intrinsic_surrogate`
- for `temporal_delay`: `transport_ratio`
- for `flux_coupling`: `absolute_flux`

## Constitutive Modes

Some model families require explicit constitutive choices that are stronger than ordinary numeric parameters. When such a choice changes the interpretation of geometry or topology, it must be exposed in config and snapshot metadata rather than left implicit.

Examples include:

- `frame_mode`: whether local directional structure is supplied by a host embedding, an induced local basis, or a combinatorial construction,
- `boundary_mode`: whether low-coherence boundaries are handled by pruning, barrier inflation, ghost support, or another documented rule,
- `measure_mode`: whether node values are unit-cell quantities or already absorb quadrature weights,
- `edge_label_selection`: whether the model computes all analytic edge labels or only a selected subset.

Family-specific schemas are allowed. For example, a nine-slot substrate may use a fixed constitutive port-chart mode such as `fixed_port_chart` instead of the graph-family modes used by `GRCV2` or `GRCV3`.

The common interface does not force one schema for these fields, but every implementation must serialize enough metadata for the constitutive reading of the state to be recoverable.

For `edge_label_selection`, the recommended schema is:

- `"all"` as the default, meaning compute and expose all three analytic labels,
- or an explicit subset drawn from:
  - `geometric_length`
  - `temporal_delay`
  - `flux_coupling`

When a label is not selected, the implementation may leave its stored family empty, compute it lazily on demand, or omit it from runtime caches, but the selection policy itself must be serialized.

## Parameter Resolution and Canonicalization

Every model family must define a deterministic resolution boundary between:

- user-provided config,
- family defaults,
- environment-derived defaults if allowed,
- and resolved params actually used at runtime.

Required rules:

- environment variables must not silently override resolved params after model construction,
- all default expansion must happen at construction time,
- the resolved param object must be immutable or treated as immutable during stepping,
- canonical serialization of resolved params must be deterministic,
- and the canonical identity of the resolved params must be preserved in save/load artifacts.

Recommended metadata names:

- `params_resolved`
- `params_hash`
- `params_canonicalization`

## Parameter Grouping Guidance

For larger families, the parameter object should be grouped into named sub-records rather than a flat bag of scalars.

Recommended group names:

- `evolution`
- `constitutive`
- `topology`
- `numerics`
- `labels`

This is guidance rather than a strict schema, but the goal is to prevent coefficients, semantic modes, and numerical backend choices from becoming indistinguishable ad-hoc globals.

## Budget Bookkeeping Guidance

The common interface already allows exact preservation or explicitly bounded remainder. For the reference implementation, the recommended strategy is:

- store the target budget explicitly,
- store a running `remainder` only when a step cannot be closed exactly in floating-point arithmetic,
- clear that remainder by an explicit correction step as soon as practical,
- and never allow silent drift to accumulate across many steps.

Families that enforce simplex projection, explicit redistribution, or quadrature-style correction may still keep `remainder=None` in the common case.

## Curvature Backend Strategy

The allowed curvature backend names are defined by the family specs, but the reference implementation rollout strategy is:

- `none` is the baseline default,
- `forman` is the first in-house curvature backend to implement,
- `ollivier` is an advanced backend to add later after the baseline graph families are stable.

This strategy exists to preserve the backend boundary established elsewhere in the specs:

- no third-party graph library is required for core execution,
- the first authoritative curvature implementations are owned by `PyGRC`,
- and advanced curvature backends must not force the core model layer to depend on external graph packages.

## Graph Requirements

The common interface does not force one graph backend, but all models must support:

- node iteration,
- edge iteration,
- neighbor lookup,
- node insertion/removal,
- edge insertion/removal,
- weighted edge attributes,
- deterministic serialization order.

The reference implementation must provide **in-house deterministic graph backends** for both the standard weighted-graph families and the port-graph families.

This requirement exists because the core library needs:

- stable IDs,
- exact snapshot control,
- deterministic mutation semantics,
- and specialized port-graph behavior that general-purpose graph libraries do not model naturally.

For `GRCV2` and `GRCV3`, a standard weighted graph abstraction is sufficient.

For `GRC9` and `GRC9V3`, the graph abstraction must additionally support:

- ordered ports,
- port occupancy,
- port-to-edge lookup,
- deterministic rewiring by row/column.

## Backend Policy

The implementation should be **backend-pluggable by design**, but the first authoritative backend must be the in-house reference backend.

That means:

- the core model layer depends on graph protocols or narrow internal abstractions,
- the default simulation backends are owned by `PyGRC`,
- external libraries such as `networkx` may be supported later through adapters or import/export helpers,
- and visualization libraries such as `pyvis` belong to export or integration tooling, not to the core simulation substrate.

The core model layer must not require `networkx`, `pyvis`, or any other general-purpose graph or visualization library in order to execute model steps.

## Reference Python Realization Notes

The common interface is normative; the following implementation choices are allowed and recommended for the reference Python realization:

- stable integer node and edge IDs,
- tombstoned graph slots rather than ID reuse,
- array-backed node and edge field vectors aligned to stable IDs,
- narrow graph and operator protocols so geometry, physics, identity, and topology operators do not depend on one concrete graph class,
- object-stored observables and event logs as an implementation strategy, even when `step()` also returns a `StepResult`.

These notes do not constrain alternative implementations. They clarify that the reference Python library may use a storage and operator design similar to the existing prototype while still exposing the public interface defined above.

They also clarify the backend strategy: first-party deterministic backends in the core, optional third-party adapters later.

## Numerical Requirements

All models must:

- preserve antisymmetry of directed flux,
- preserve non-negativity of coherence after budget correction,
- preserve the target budget exactly or to explicitly bounded remainder,
- produce deterministic results given identical state and RNG seed.

## Error Handling

The implementation must raise explicit exceptions for:

- invalid topology,
- invalid parameter ranges,
- negative coherence after correction,
- unsupported capability requests,
- incompatible state deserialization.

## Concrete Class Names

The library must expose these concrete model classes:

```python
class GRCV2(GRCModel): ...
class GRCV3(GRCModel): ...
class GRC9(GRCModel): ...
class GRC9V3(GRCModel): ...
```

## Interoperability Contract

All concrete classes must satisfy:

1. `snapshot()` returns a mapping with a `model_family` field.
2. `save()` and `load()` preserve the exact family.
3. `list_capabilities()` reflects real implementation support, not aspirational support.
4. Variant-specific fields remain accessible through concrete state objects, not erased by the common interface.
