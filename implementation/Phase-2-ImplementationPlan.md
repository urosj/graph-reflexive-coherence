# Phase 2 Implementation Plan

This document is the detailed execution plan for **Phase 2: Core Graph + Storage**.

It turns the Phase 2 summary in `ImplementationPhases.md` into concrete graph/storage workstreams, implementation boundaries, and acceptance criteria.

Phase 2 exists to provide the deterministic in-house execution substrate that later family implementations will use directly.

## Purpose

Phase 2 must establish:

- the graph/storage protocols shared across model families,
- the first authoritative in-house weighted-graph backend,
- the first authoritative in-house port-graph backend,
- stable node/edge identity handling,
- deterministic iteration and snapshot ordering,
- and the mutation/invalidation rules needed for later simulation logic.

This phase should make later family implementations possible without yet implementing family equations.

## Inputs From Earlier Phases

Phase 2 assumes the following are already in place and remain authoritative:

- Phase 0 determinism conventions in [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
- Phase 0 backend and family-boundary decisions in [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
- Phase 1 shared contracts in `src/pygrc/core/`
- Phase 1 family stubs in `src/pygrc/models/`

Phase 2 must not silently contradict those documents.

## In Scope

- graph/storage protocols
- weighted-graph backend for `GRCV2` / `GRCV3`
- port-graph backend for `GRC9` / `GRC9V3`
- stable ID allocation and no-reuse semantics
- tombstoning behavior
- deterministic node/edge/port iteration
- adjacency and incidence lookup
- port lookup and row/column conversion rules
- mutation operations:
  - insert node
  - remove node
  - insert edge
  - remove edge
  - port occupancy updates
  - rewiring helpers for port-graph families
- cache invalidation rules for derived fields attached to graph/state storage
- graph/storage tests

## Out Of Scope

- model-family step logic
- flux/potential/continuity equations
- spark detection
- basin extraction
- curvature implementations
- induced local frame or Hessian kernels
- canonical JSON serializer implementation
- external adapter implementations (`networkx`, `pyvis`)
- machine-driver diff/patch logic

## Phase 2 Design Constraints

### 1. First-Party Backend Authority

The execution backends created in this phase are in-house and authoritative.

The core model layer must not depend on:

- `networkx`
- `pyvis`
- or any other general-purpose graph/visualization package

to execute graph/storage operations.

### 2. Determinism First

The backends must follow the Phase 0 determinism conventions:

- stable integer IDs
- no ID reuse
- tombstoned slots by default
- deterministic node/edge/port ordering
- deterministic row/column port mapping

### 3. Backend-Neutral Public Contracts

The rest of the library should depend on:

- protocols,
- narrow interfaces,
- or thin abstractions

rather than on one concrete graph class everywhere.

### 4. Family Separation

`GRCV2` / `GRCV3` and `GRC9` / `GRC9V3` do not share one graph substrate.

Phase 2 should expose:

- a weighted-graph backend for graph families
- a port-graph backend for nine-slot families

without pretending that the port-graph is just a decorated ordinary edge list.

## Expected Code Shape After Phase 2

The exact files may still evolve, but the intended Phase 2 shape is close to:

```text
src/pygrc/
  core/
    graph.py
    storage.py
    ids.py
```

This may later be split more finely, but the graph/storage boundary should already be clear.

## Workstreams

## 1. Graph And Storage Protocols

### Tasks

- Define the narrow graph/storage protocols used by later phases.
- Separate:
  - weighted-graph operations
  - port-graph operations
  - shared ID and iteration expectations
- Decide whether protocols live in one module or split across graph/storage concerns.
- Keep the protocol surface minimal enough that later backends and adapters can both satisfy it.

### Protocol Requirements

The shared graph/storage protocol layer should support at least:

- node iteration
- edge iteration
- node existence checks
- edge existence checks
- neighbor lookup
- node insertion/removal
- edge insertion/removal
- deterministic order exposure
- access to stable IDs

The protocol layer should also be designed so that a future third-party
adapter can satisfy it without changes to the core model layer. In
particular, the protocol surface should describe required behaviors and
iteration guarantees, not implementation-specific storage details from the
reference backends.

The port-graph protocol must additionally support:

- ordered ports
- port occupancy
- port-to-edge lookup
- row/column conversion
- deterministic rewiring

### Acceptance Criteria

- Later model code can depend on the protocols without binding to one concrete class.
- Weighted and port-graph needs are both represented explicitly.
- No third-party graph dependency appears in the protocol layer.

## 2. ID Allocation And Tombstoning

### Tasks

- Implement stable node/edge ID allocation helpers.
- Encode monotone `next_node_id` / `next_edge_id` behavior.
- Define the exact tombstone representation used by the reference backends.
- Decide how deleted records remain addressable internally while disappearing from live iteration.
- Make the ID rules compatible with later save/load restoration.

### Acceptance Criteria

- IDs are never reused.
- New insertions always allocate fresh IDs.
- Deleted objects do not appear in live iteration.
- Save/load-compatible counters exist at the storage layer.

## 3. Weighted-Graph Backend

### Tasks

- Implement the reference weighted-graph backend for `GRCV2` / `GRCV3`.
- Support node storage, edge storage, adjacency, and neighbor queries.
- Implement insertion/removal semantics consistent with tombstoning.
- Implement deterministic iteration over live nodes and edges.
- Define the storage shape for node and edge payload slots without assuming family-specific fields.

### Acceptance Criteria

- The weighted backend supports the protocol requirements for graph families.
- Iteration order is deterministic.
- The backend is ready for later family-specific node/edge field attachment.

## 4. Port-Graph Backend

### Tasks

- Implement the reference port-graph backend for `GRC9` / `GRC9V3`.
- Encode exactly nine ordered ports per node.
- Implement canonical row/column <-> slot conversion.
- Implement port occupancy tracking.
- Implement port-to-edge lookup.
- Implement deterministic rewiring helpers needed by later expansion logic.
- Keep the backend substrate generic enough that Phase 6/7 can add real mechanics later.

### Acceptance Criteria

- The port backend supports exact ordered-port semantics.
- Port occupancy and edge lookup are deterministic.
- Row/column conversion is canonical and test-backed.

## 5. Mutation Semantics

### Tasks

- Define the mutation API for node insertion/removal.
- Define the mutation API for edge insertion/removal.
- Decide how removal cascades interact with adjacency and port occupancy.
- Keep mutation semantics deterministic and side-effect visibility clear.
- Ensure the mutation API is sufficient for later split/birth/expand operations without implementing those operations now.

### Acceptance Criteria

- Mutation operations are explicit and testable.
- Removal behavior cannot leave the backend in an inconsistent state.
- Port-graph mutation semantics are compatible with later expansion/refinement.

## 6. Cache Invalidation Rules

### Tasks

- Define how graph/storage backends invalidate derived caches after mutation.
- Align the invalidation design with `GRCState.cached_quantities` from Phase 1.
- Decide whether invalidation markers live on the graph backend, state object, or both.
- Define a hook, callback, or explicit invalidation signal by which graph/storage
  mutation can tell the owning state object to clear or mark specific entries in
  `cached_quantities`.
- Keep the invalidation mechanism family-neutral.
- Avoid embedding actual geometric or physics cache contents in Phase 2.

### Acceptance Criteria

- Graph/storage mutation has a clear invalidation policy.
- The invalidation policy is explicitly compatible with `GRCState.cached_quantities`.
- Later phases can attach derived caches without inventing ad hoc invalidation rules.
- The invalidation policy does not depend on family equations.

## 7. Adapter Boundary Definition

### Tasks

- Define the optional future adapter boundary for third-party tools.
- Record where `networkx`-style adapters would attach later.
- Record where `pyvis`-style export/visualization adapters would attach later.
- Keep those boundaries out of the authoritative execution path.
- Ensure the Phase 2 protocol surface is broad enough that a future
  `networkx`-style adapter can satisfy it without changing core model code.

### Acceptance Criteria

- The adapter story is clear without requiring implementation now.
- No external adapter is needed by the Phase 2 backends.
- A future adapter can target the protocol layer rather than requiring a new
  core-model-specific API.

## 8. Graph/Storage Tests

### Tasks

- Add tests for ID allocation and no-reuse behavior.
- Add tests for deterministic live iteration order.
- Add tests for tombstoning behavior.
- Add tests for weighted-graph adjacency and mutation.
- Add tests for port ordering, occupancy, and lookup.
- Add tests for row/column conversion.
- Add tests for cache invalidation markers or invalidation hooks.

### Acceptance Criteria

- The graph/storage substrate is test-backed before model logic begins.
- Tests exercise structure and mutation, not model equations.
- Tests are deterministic and do not depend on later family implementations.

## Deliverables

Phase 2 should produce:

- graph/storage protocol definitions
- ID/tombstone handling for the reference backends
- weighted-graph backend
- port-graph backend
- mutation and invalidation rules
- graph/storage-focused tests

## Acceptance Criteria

Phase 2 is complete only if all of the following are true.

### A. Structural Acceptance

- The graph/storage modules exist and import cleanly.
- Both weighted and port-graph backends exist.
- Tests cover the shared substrate at least at a structural/mutation level.

### B. Boundary Acceptance

- No family equations are implemented in the graph/storage layer.
- No third-party graph or visualization library is required for core execution.
- Adapter boundaries are defined without outsourcing the execution substrate.

### C. Specification Alignment Acceptance

- The backends follow the Phase 0 determinism conventions.
- The port-graph backend respects the fixed nine-slot chart assumptions.
- The weighted backend remains compatible with the common contracts from Phase 1.

### D. Reproducibility Acceptance

- IDs are stable and never reused.
- Live iteration order is deterministic.
- Tombstoning and counter restoration are consistent with later snapshot/save-load work.

### E. Developer-Onboarding Acceptance

- A contributor can see where to add:
  - node/edge payload fields
  - mutation hooks
  - adapter layers later
  - family-specific graph operations without breaking the common substrate

## Suggested Follow-On Documents

Once Phase 2 execution begins, it will likely be useful to add:

- `Phase-2-ImplementationChecklist.md`
- `Phase-2-BackendMatrix.md`
- `Phase-2-PortGraphConventions.md` only if the port-graph details outgrow the main checklist
