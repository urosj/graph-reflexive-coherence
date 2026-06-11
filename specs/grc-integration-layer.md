# GRC Integration Layer Specification

## Purpose

The core GRC library should implement the papers as directly and cleanly as possible.

Downstream environments such as `ril_v0`, `ide_v0`, notebooks, telemetry systems, or future CLIs may require additional adapter behavior:

- opaque machine state handles,
- debugger-oriented inspection,
- programmatic topology operations,
- patch and snapshot workflows,
- or custom observation and trace payloads.

These requirements must not distort the core model classes.

This document specifies the integration layer that sits on top of the core model layer.

## Layer Boundary

The library is split conceptually into:

1. core model layer,
2. integration layer.

The core model layer contains:

- `GRCModel`,
- concrete classes `GRCV2`, `GRCV3`, `GRC9`, `GRC9V3`,
- graph/state/field storage,
- numerical operators,
- model-native events and observables,
- model serialization.

The integration layer contains:

- adapters to external runtimes,
- driver interfaces,
- observation translation,
- patch/diff tooling,
- debugger-friendly inspection views,
- compatibility shims for older environments,
- lightweight host-project embedding helpers.

Optional graph-analysis or visualization adapters also belong here rather than in the core simulation layer.

Dependency rule:

- integration code may depend on core code,
- core code must not depend on integration code.

## Goals

1. Preserve paper-faithful core implementations.
2. Avoid reimplementing `ril_v0` or `ide_v0` inside the core.
3. Make it possible to expose any model family through a stable adapter surface.
4. Support multiple downstream runtimes without changing the core public model API.
5. Support gradual adoption by external projects that only need a GRC-backed graph and stepping surface initially.

## Required Concepts

Every integration adapter should define or use the following concepts.

### Model binding

An integration adapter binds to exactly one concrete model instance or model family instance.

Example:

```python
adapter = RILAdapter(model)
```

The adapter may wrap:

- a live `GRCModel`,
- a frozen snapshot,
- or an opaque serialized/restored state.

### Capability translation

The adapter must expose only operations actually supported by the underlying model.

Examples:

- `GRCV2` may support `detect_sparks` and `soft_split`, but not `choice_detected`.
- `GRCV3` may support richer basin and collapse inspection.
- `GRC9` may support port inspection and rewiring-specific reports.

The adapter must map model capabilities into integration-facing feature flags or method availability.

### Observation translation

The adapter may convert model-native observables and events into runtime-specific observation payloads.

This translation is allowed to:

- rename fields,
- aggregate fields,
- omit fields,
- add integration metadata.

It must not silently change model semantics.

### Visibility translation

An adapter may project the full model state into an observer-limited or neighborhood-limited view for downstream tools.

This translation is allowed to:

- restrict visible nodes or edges,
- mask fields outside a declared horizon,
- attach policy metadata describing what was hidden.

It must not relabel a restricted view as the full model state.

### Deterministic inspection

Any adapter-facing inspection that returns collections must use deterministic ordering.

This includes:

- nodes,
- edges,
- basins,
- ports,
- events,
- snapshots,
- diffs.

## Recommended Package Shape

```text
pygrc/
  core/
  models/
  integrations/
    ril_v0/
      adapter.py
      observations.py
      trace.py
    ide_v0/
      machine_driver.py
      serializers.py
      patches.py
      telemetry.py
```

This is guidance only. The hard requirement is the separation of responsibilities.

## Lightweight Host Embedding

Not every downstream user needs a full runtime integration.

Some projects may only need:

- a GRC-backed graph/state engine,
- a `step()` loop,
- model snapshots,
- and a small inspection surface.

For those cases, the integration layer may provide a lightweight host-project adapter that is smaller than both `ril_v0` and `ide_v0`.

This path is specified in `grc-embedding-profile.md`.

## Adapter Contract

Every integration adapter should provide:

```python
class GRCIntegrationAdapter(Protocol):
    def model_family(self) -> str: ...
    def list_capabilities(self) -> set[str]: ...
    def get_model(self) -> GRCModel: ...
    def get_state(self) -> Any: ...
```

The integration adapter may additionally provide runtime-specific operations such as:

- `detect_sparks()`
- `soft_split(...)`
- `seed(...)`
- `prune()`
- `project_budget()`
- `observe(...)`
- `state_summary()`
- `inspect_node(...)`
- `inspect_edge(...)`
- `observer_view(...)`
- `diff_states(...)`

These methods are not required for every integration.

## External Library Adapters

If the project later supports external graph or visualization libraries, they should be introduced as adapters at the integration boundary.

Typical examples:

- `networkx` for interchange, analysis, or import/export,
- `pyvis` for visualization/export of graph state.

These libraries must not be treated as the authoritative execution substrate of the core model families. The authoritative simulation backends remain the in-house deterministic backends defined by the core layer.

## Integration Responsibilities

The integration layer is responsible for:

- translating between opaque runtime handles and model/state objects,
- formatting observations for runtime consumption,
- exposing deterministic snapshots and digests where needed,
- implementing runtime-specific patch and diff formats,
- implementing restricted-view inspection policies where needed,
- carrying runtime, observer, and tooling policies that do not belong to core model params,
- projecting core errors into integration-friendly error objects.

The integration layer is not responsible for:

- redefining model semantics,
- changing the core step order,
- weakening theoretical invariants,
- storing shadow state that can drift from the underlying model.

## Parameter Ownership Boundary

Integrations must preserve the distinction between:

- **core model params**, which govern state evolution and belong to `GRCParams`,
- and **runtime / observer / tooling params**, which govern execution, visibility, or reporting and belong to the integration or host runtime.

Examples of integration-owned parameter domains:

- device mapping,
- telemetry cadence,
- observer comparison thresholds,
- readback contracts,
- patch / diff policy,
- debugger checkpoint retention,
- runtime storage policy.

These must not be silently inserted into the core model params unless the wrapped model family explicitly promotes them into evolution semantics.

## Core Responsibilities Exposed To Integrations

The core model layer should expose enough hooks for adapters to build on top of it:

- state snapshots,
- model serialization,
- capability introspection,
- observables,
- event streams,
- optional fine-grained operations where the model family supports them.

If a downstream integration needs a convenience operation not present in the core common interface, it should normally be implemented as an adapter composition over core primitives rather than pushed into `GRCModel`.

The same rule applies to host projects with existing graph schemas: preserve the host application's domain logic at the host boundary and translate into GRC semantics through a bounded adapter layer.

## Versioning

Integrations must version themselves independently from the core model family.

For example:

- model family: `grc_v3`
- integration family: `ide_v0`
- adapter implementation: `pygrc.integrations.ide_v0.machine_driver`

This prevents runtime compatibility concerns from freezing core model evolution.

## Compatibility Notes

The reference implementation should support:

- adaptation of `GRCV2` to `ril_v0`,
- adaptation of `GRCV2` and later families to `ide_v0`,
- introduction of future integrations without any required change to the core model API.

When an older integration cannot express a newer model feature exactly, the adapter must:

- omit the feature,
- expose it as optional metadata,
- or report unsupported capability explicitly.

It must not mislabel an approximation as an exact semantic equivalent.

The same rule applies to temporal and causal language: an integration must not present `temporal_delay` as proper time or Lorentzian causality unless the wrapped model actually advertises `causal_layer`.
