# GRC Embedding Profile Specification

## Purpose

Some projects will not start by adopting the full GRC library surface.

They may already have:

- a simple weighted graph,
- a domain-specific schema,
- their own command surface,
- and their own storage model.

For those projects, the first practical goal is often smaller:

- replace or augment the internal graph engine with a GRC-backed model,
- call `step()` or a short run loop,
- preserve domain-specific data around the graph,
- and optionally attach IDE inspection later.

This document defines that lightweight embedding profile.

## Intended Use

This profile is for external host projects such as:

- graph-authoritative basin systems,
- domain-specific CLIs,
- workflow tools with weighted local structure,
- research prototypes that want GRC dynamics without immediate full runtime adoption.

The host project remains the top-level application.

The GRC library supplies:

- the graph/state engine,
- the step logic,
- theory-aligned observables,
- and optional adapter hooks.

## Design Rule

The host project should be able to depend only on:

- the core model layer,
- and optionally a very small adapter surface.

It must not be forced to adopt:

- the full IDE runtime,
- the RIL language layer,
- patch workflows,
- or debugger session management

just to use a GRC-backed graph.

## Minimal Embedding Contract

An external project using the embedding profile should be able to do the following:

```python
model = GRCV2.from_config(config)
model.set_state(state)
result = model.step()
snapshot = model.snapshot()
observables = model.compute_observables()
```

At minimum, the embedding profile assumes support for:

- model construction,
- state injection or restoration,
- single-step evolution,
- snapshot export,
- observable readout,
- capability discovery.

If the selected model family uses `frame_mode="host_embedding"`, the embedding profile also assumes deterministic delivery of the host geometry fields required by that model.

## Host Responsibilities

The host application remains responsible for:

- domain-specific file schemas,
- domain-specific node and edge semantics outside the GRC core,
- command routing,
- user-facing workflow rules,
- non-GRC metadata,
- storage layout outside model snapshots.

The host may keep a richer application-level graph object and embed a GRC model inside it, or it may progressively migrate its graph storage into the GRC model itself.

## Geometry Sourcing Rule

The embedding boundary must state explicitly where local geometric structure comes from.

Three cases are allowed:

- the host supplies coordinates, directions, or displacement surrogates to the model,
- the model derives a local basis from graph state internally,
- the model uses a purely combinatorial directional surrogate.

The host must not assume these readings are interchangeable. The selected `frame_mode` is part of the model contract and must survive snapshotting and restore.

## Mapping Rule

When a host project has an existing weighted graph, it should be able to define a bounded mapping:

- host node identity -> GRC node identity
- host edge identity -> GRC edge identity
- host weight fields -> GRC coherence / conductance / labels
- host geometry fields -> GRC local frame inputs when `frame_mode="host_embedding"`
- host metadata -> sidecar metadata or domain-layer fields

This mapping may be partial at first.

It does not need to convert the whole host schema into canonical GRC semantics on day one.

## Recommended Embedding Shapes

Two shapes are acceptable.

### 1. GRC-owned graph

The host project treats the GRC model as the authoritative graph/state engine.

The host stores only:

- domain metadata,
- file paths,
- user annotations,
- or derived indexes.

### 2. Host-owned graph with GRC mirror

The host project keeps its own graph as the authoritative domain object and derives or synchronizes a GRC state from it.

This is acceptable for transition periods, but the synchronization boundary must be explicit and deterministic.

If both graphs are mutable, the project must define which one is authoritative for each field.

If the host supplies geometric fields, it must also define which side is authoritative for those fields and when they are recomputed.

## Mapping Validation During Transition

When using the host-owned mirror shape, the embedding must provide:

1. deterministic mapping functions in both directions:
   - `host_to_grc()`
   - `grc_to_host()`
2. a synchronization validation step after each sync boundary,
3. explicit authority metadata for mirrored fields.

Minimum validation contract:

```python
assert abs(host_budget - grc_budget_current) < tolerance
```

Minimum authority metadata:

- `sync_authority["coherence"]`
- `sync_authority["geometry"]`
- `sync_authority["topology"]`

If a host keeps additional mirrored fields, the same authority rule must be extended to those fields as well.

The purpose of this contract is to prevent silent drift between host and GRC representations during the transition period.

## Lightweight Adapter Recommendation

Projects following this profile should normally expose one small wrapper of their own, for example:

```python
class BasinGraphRuntime:
    def __init__(self, model: GRCModel, domain_state: Any) -> None: ...
    def step(self) -> StepResult: ...
    def snapshot(self) -> dict[str, Any]: ...
    def inspect_summary(self) -> dict[str, Any]: ...
```

This keeps the host project decoupled from the full integration layer while still making later IDE attachment straightforward.

## Optional IDE Attachment

The embedding profile should support a later upgrade path:

1. adopt core model and step loop,
2. stabilize state/snapshot boundaries,
3. add a machine-driver adapter for IDE inspection.

That means the embedded host should preserve:

- deterministic node and edge identifiers,
- deterministic snapshot export,
- inspectable node/edge/budget views,
- stable family and capability metadata.

If those are present, an IDE-facing machine driver can usually be attached without redesigning the host application.

## Optional Inspection Surface

Even before a full IDE driver exists, the host project should prefer exposing a small inspection surface compatible with later driver wrapping.

Recommended methods:

- `state_summary()`
- `inspect_node(node_id)`
- `inspect_edge(u, v)`
- `inspect_budget()`
- `inspect_local(origin, radius, fields=None)`
- `list_capabilities()`

These do not need to satisfy the full machine-driver spec initially.

They only need deterministic output and stable identifiers.

If a project wants to preserve the phenomenology of observer-local information, this lightweight inspection surface should prefer locality-preserving queries over whole-state dumps.

## Non-Goals

This profile does not require:

- RIL integration,
- debugger checkpoints,
- reversible patches,
- assembler edit groups,
- language-driver program counters,
- full event-history replay.

Those belong to the integration layer and can be added later.

## Compatibility With Machine Driver Spec

The embedding profile is intentionally compatible with `grc-machine-driver.md`.

A host project is considered “IDE-ready enough” when it can expose or derive:

- deterministic serialized state,
- state digest,
- node/edge/basin inspection views,
- invariant checks,
- budget projection or validation,
- stable capability metadata.

At that point, a thin adapter can implement the full machine-driver contract without changing the embedded core model.

## Guidance For Reference Implementation

The reference library should eventually provide a small helper surface for embedded hosts, such as:

```python
pygrc.integrations.host/
  graph_adapter.py
  state_bridge.py
  inspect.py
```

This helper layer should remain lighter than `ril_v0` or `ide_v0`.

Its purpose is not to recreate those environments.
Its purpose is to make gradual adoption practical for projects that currently only need a GRC-backed graph and a `step()` loop.
