# Phase 2 Implementation Checklist

This document tracks the execution of **Phase 2: Core Graph + Storage**.

It is intentionally separate from [`Phase-2-ImplementationPlan.md`](./Phase-2-ImplementationPlan.md):

- the plan defines scope, workstreams, boundaries, and acceptance criteria,
- this checklist records how the Phase 2 work is actually executed iteration by iteration.

Each iteration should contain:

- a bounded implementation slice,
- concrete checkboxes that can be ticked off during execution,
- implementation notes recorded alongside the work,
- verification steps tied to the iteration output,
- and a short summary when the iteration closes.

## Usage Rules

- Keep iterations small enough that verification remains clear.
- Update checkboxes during implementation, not after the fact.
- Record design decisions near the affected work rather than in a separate log.
- If a plan change is needed, update the plan document first or in the same change.
- If an item is deferred, leave it unchecked and add a short reason in the notes or summary.
- Keep graph/storage notes aligned with:
  - [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
  - [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
  - [`Phase-2-ImplementationPlan.md`](./Phase-2-ImplementationPlan.md)

## Iteration Template

Copy this section for each new iteration.

```markdown
## Iteration N. <Short Name>

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>
- [ ] <Concrete task 3>

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / test / review check>
- [ ] <Boundary / acceptance check>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Checklist Bootstrap

### Goal

Create the Phase 2 execution checklist and align it with the existing Phase 2 implementation plan.

### Checks

- [x] Create `Phase-2-ImplementationChecklist.md`
- [x] Link the checklist from `ImplementationPhases.md`
- [x] Align the checklist structure with the Phase 2 workstreams
- [x] Decide whether Phase 2 needs any additional companion planning docs before implementation starts

### Implementation Notes

- The execution checklist follows the same separation-of-concerns pattern used in Phase 0 and Phase 1.
- The Phase 2 plan remains the normative planning document; this file is the execution tracker.
- Possible companion docs for this phase were already identified in the plan:
  - `Phase-2-BackendMatrix.md`
  - `Phase-2-PortGraphConventions.md`
- Those companion docs are optional and should only be created if the implementation work outgrows the main checklist and plan.

### Verification

- [x] The checklist file exists under `implementation/`
- [x] `ImplementationPhases.md` points to the checklist
- [x] The checklist iterations map cleanly onto the Phase 2 plan

### Summary

Phase 2 now has a paired plan and execution checklist. Additional companion docs remain optional until implementation pressure makes them necessary.

## Iteration 1. Graph And Storage Protocols

### Goal

Define the protocol layer that later weighted-graph and port-graph backends will implement.

### Checks

- [x] Create the core graph/storage protocol module or modules
- [x] Define the weighted-graph protocol surface
- [x] Define the port-graph protocol surface
- [x] Define the shared stable-ID and deterministic-iteration expectations in the protocol layer
- [x] Keep protocol semantics focused on behavior rather than reference-backend storage details
- [x] Ensure the protocol surface is broad enough for future adapters without changing core model code

### Implementation Notes

- The protocol layer should be narrow, durable, and family-neutral.
- Weighted and port-graph families need separate protocol expression; Phase 2 should not flatten them into one artificial universal graph API.
- Protocols should be explicit enough that later model code can depend on them directly without reaching into concrete backend internals.
- The protocol layer must not depend on `networkx`, `pyvis`, or any other third-party graph package.
- Implemented the initial protocol layer in `src/pygrc/core/graph.py`.
- Chosen shared base protocol: `GraphStorageProtocol`.
- Chosen concrete protocol split:
  - `WeightedGraphProtocol` for `GRCV2` / `GRCV3`
  - `PortGraphProtocol` for `GRC9` / `GRC9V3`
- Chosen shared stable-ID vocabulary:
  - `NodeId`
  - `EdgeId`
  - `PortSlot`
- Chosen deterministic-iteration naming:
  - `iter_live_node_ids()`
  - `iter_live_edge_ids()`
- The protocol surface is intentionally behavioral:
  - live iteration
  - existence checks
  - adjacency/incidence queries
  - topology mutation hooks
  - port lookup and rewiring hooks
- Storage details such as tombstone representation, payload slots, and adjacency data structures remain deferred to later iterations.
- The fixed nine-slot chart is represented at the protocol level through:
  - `PORT_ROW_COUNT = 3`
  - `PORT_COLUMN_COUNT = 3`
  - `PORTS_PER_NODE = 9`
- Added runtime-checkable structural tests in `tests/core/test_graph_protocols.py`.
- Updated `src/pygrc/core/__init__.py` and `tests/core/test_module_imports.py` so the new protocol layer is part of the shared core surface.

### Verification

- [x] Graph/storage protocol modules import cleanly
- [x] The weighted and port-graph protocol differences are explicit
- [x] No third-party graph dependency appears in the protocol layer

### Summary

Defined the Phase 2 protocol layer in `src/pygrc/core/graph.py` and made it part of the exported core surface. The iteration fixed the shared stable-ID vocabulary, the deterministic live-iteration API, and the distinct weighted vs. port-graph contract shapes without committing to any backend storage representation yet.

## Iteration 2. ID Allocation And Tombstoning

### Goal

Implement the shared ID-allocation and tombstoning rules used by the reference graph backends.

### Checks

- [x] Create shared ID allocation helpers or storage primitives
- [x] Implement monotone `next_node_id` allocation
- [x] Implement monotone `next_edge_id` allocation
- [x] Define the tombstone representation for deleted nodes and edges
- [x] Ensure deleted records are excluded from live iteration while remaining internally restorable
- [x] Keep the storage shape compatible with later save/load restoration

### Implementation Notes

- This iteration must follow the Phase 0 determinism decisions exactly:
  - stable non-negative integer IDs
  - no ID reuse
  - tombstoned slots by default
- Tombstoning should be treated as part of the authoritative storage semantics, not as an incidental implementation detail.
- The storage layer should preserve enough information for later snapshot/save-load support without implementing full serializer logic yet.
- Implemented the shared ID/storage primitive module in `src/pygrc/core/ids.py`.
- Chosen monotone counter primitive: `MonotoneIdSource`.
- Chosen deleted-record representation: the explicit `TOMBSTONE` sentinel with `TombstoneMarker`.
- Chosen shared storage primitive: `TombstoneSlotTable[T]`.
- `TombstoneSlotTable` provides:
  - monotone fresh allocation,
  - raw slot inspection,
  - live-record access,
  - live deterministic iteration,
  - explicit tombstoning,
  - restored counter support through `next_id`.
- The storage primitive deliberately keeps tombstoned slots internally addressable via `inspect_slot(...)` while excluding them from:
  - `has_live(...)`
  - `get_live(...)`
  - `iter_live_ids()`
  - `iter_live_items()`
- Restoration-oriented compatibility choice:
  - `TombstoneSlotTable` accepts both `slots=` and `next_id=`
  - if restored `next_id` is ahead of the visible slot count, later allocation backfills the gap with tombstones
  - this keeps the primitive compatible with later save/load and exact-replay restoration needs
- Updated `src/pygrc/core/__init__.py` to export the new primitives.
- Added dedicated tests in `tests/core/test_ids.py`.
- Updated `tests/core/test_module_imports.py` so `pygrc.core.ids` is part of the common import surface.

### Verification

- [x] ID allocation is monotone and deterministic
- [x] Deleted records do not appear in live iteration
- [x] Counter restoration requirements are visible in the storage design

### Summary

Implemented the shared ID and tombstone primitives in `src/pygrc/core/ids.py`. Phase 2 now has a reusable monotone counter and a deterministic tombstoned slot table that preserves dead IDs internally, skips them in live iteration, and keeps `next_id` restoration explicit for later snapshot/save-load work.

## Iteration 3. Weighted-Graph Backend

### Goal

Implement the in-house weighted-graph backend for `GRCV2` and `GRCV3`.

### Checks

- [x] Create the weighted-graph backend module
- [x] Implement node storage
- [x] Implement edge storage
- [x] Implement adjacency and neighbor lookup
- [x] Implement node insertion/removal using the shared tombstoning semantics
- [x] Implement edge insertion/removal using the shared tombstoning semantics
- [x] Implement deterministic live node iteration
- [x] Implement deterministic live edge iteration
- [x] Keep node and edge payload storage family-neutral

### Implementation Notes

- The weighted backend is the reference substrate for the ordinary graph families.
- This backend must be generic enough to accept later field attachments without embedding family equations now.
- Deterministic iteration order matters as much as the mutation API; both are part of the model contract.
- Implemented the weighted backend in `src/pygrc/core/storage.py` as `WeightedGraphBackend`.
- Chosen storage shape:
  - node slots store family-neutral `dict[str, Any]` payload mappings
  - edge slots store `WeightedEdgeRecord(node_a, node_b, payload)`
- Chosen backing primitives:
  - `TombstoneSlotTable[dict[str, Any]]` for nodes
  - `TombstoneSlotTable[WeightedEdgeRecord]` for edges
  - adjacency map `dict[node_id, set[edge_id]]` for live incidence tracking
- Chosen adjacency reconstruction rule:
  - rebuild adjacency from live edge records during backend construction/restoration
  - reject restored live edges whose endpoints are not live nodes
- Chosen deterministic iteration behavior:
  - live node iteration is ascending `node_id` from the node slot table
  - live edge iteration is ascending `edge_id` from the edge slot table
  - incident edges are exposed in ascending `edge_id`
  - neighbors are exposed by ascending neighbor `node_id`, with first-seen `edge_id` used as the deterministic tie-break source
- Chosen removal behavior for this backend:
  - removing an edge tombstones the edge slot and clears adjacency links
  - removing a node deterministically removes all incident live edges first, then tombstones the node slot
- Chosen payload handling:
  - caller payload mappings are copied on insertion
  - payload slots remain mutable dictionaries for later family field attachment
- Added backend tests in `tests/core/test_weighted_graph_backend.py`.
- Updated `src/pygrc/core/__init__.py` and `tests/core/test_module_imports.py` so the storage backend is part of the shared core surface.

### Verification

- [x] The weighted backend satisfies the weighted-graph protocol
- [x] Live node and edge iteration order is deterministic
- [x] The backend remains free of family-specific equation logic

### Summary

Implemented the reference weighted-graph backend in `src/pygrc/core/storage.py`. Phase 2 now has a deterministic tombstoned graph substrate with stable IDs, adjacency lookup, deterministic neighbor and incident-edge ordering, node-removal cascade handling, and family-neutral payload slots ready for later `GRCV2` and `GRCV3` field attachment.

## Iteration 4. Port-Graph Backend

### Goal

Implement the in-house nine-slot port-graph backend for `GRC9` and `GRC9V3`.

### Checks

- [x] Create the port-graph backend module
- [x] Encode exactly nine ordered ports per node
- [x] Implement canonical row/column to slot conversion
- [x] Implement canonical slot to row/column conversion
- [x] Implement port occupancy tracking
- [x] Implement port-to-edge lookup
- [x] Implement node insertion/removal with deterministic port handling
- [x] Implement edge insertion/removal with deterministic port handling
- [x] Keep the substrate generic enough for later refinement/expansion mechanics

### Implementation Notes

- This backend is not “just a weighted graph with extra metadata”.
- The fixed nine-slot chart is constitutive and must be reflected directly in storage and lookup semantics.
- Port ordering and lookup must follow the Phase 0 determinism rules exactly.
- Implemented the port backend in `src/pygrc/core/storage.py` as `PortGraphBackend`.
- Chosen storage shape:
  - node slots store family-neutral `dict[str, Any]` payload mappings
  - edge slots store `PortEdgeRecord(endpoint_a, endpoint_b, payload)`
- Chosen occupancy representation:
  - per-node live occupancy index `dict[node_id, list[edge_id | None]]`
  - exactly nine canonical slots per live node
  - occupancy is rebuilt from live edge records during restoration
- Chosen constitutive slot conventions:
  - canonical slot range `0..8`
  - canonical row/column conversion uses zero-based row-major order
  - invalid row/column or slot inputs raise `ValueError`
- Chosen deterministic iteration behavior:
  - live node iteration is ascending `node_id`
  - live edge iteration is ascending `edge_id`
  - `iter_port_slots(node_id)` always returns `0..8`
  - incident edges are exposed in ascending `edge_id`
  - neighbors are exposed by ascending neighbor `node_id`, with first-seen `edge_id` used as the deterministic tie-break source
- Chosen mutation behavior for this backend:
  - `connect_ports(...)` requires both target slots to be free
  - `rewire_edge(...)` permits reuse of the edge's current occupied slots but rejects occupation by a different live edge
  - removing an edge clears both occupied endpoints and tombstones the edge slot
  - removing a node removes all incident live edges first, then tombstones the node slot and drops its occupancy table
- Chosen restoration validation:
  - restored live edges must reference live nodes
  - restored live occupancy must remain unique per node/slot
  - duplicate occupancy during rebuild raises `ValueError`
- The backend remains generic:
  - no expansion mechanics are implemented
  - no family equations are embedded
  - payload slots remain mutable dictionaries for later `GRC9` / `GRC9V3` field attachment
- Added backend tests in `tests/core/test_port_graph_backend.py`.
- Updated `src/pygrc/core/__init__.py` so the new port backend and record type are part of the shared core surface.

### Verification

- [x] The port backend satisfies the port-graph protocol
- [x] Row/column and slot conversion are canonical and testable
- [x] Port occupancy and edge lookup are deterministic

### Summary

Implemented the reference nine-slot port-graph backend in `src/pygrc/core/storage.py`. Phase 2 now has a deterministic constitutive port substrate with canonical row/column conversion, exact nine-slot occupancy tracking, explicit rewiring, node-removal cascade handling, and family-neutral payload slots ready for later `GRC9` and `GRC9V3` mechanics.

## Iteration 5. Mutation Semantics And Cache Invalidation

### Goal

Define and implement explicit mutation rules together with the family-neutral invalidation mechanism for derived caches.

### Checks

- [x] Define the explicit mutation API for node insertion/removal
- [x] Define the explicit mutation API for edge insertion/removal
- [x] Define removal cascade behavior for adjacency and port occupancy
- [x] Define how mutation signals invalidation of derived graph/state caches
- [x] Align the invalidation mechanism with `GRCState.cached_quantities`
- [x] Decide whether invalidation markers live on the backend, the state object, or both
- [x] Implement a hook, callback, or explicit invalidation signal that later state objects can use to clear specific cached quantities

### Implementation Notes

- The invalidation design should remain family-neutral and should not embed any concrete geometric or physical cache contents.
- The graph backend does not own all state, so invalidation needs a clean boundary with `GRCState.cached_quantities`.
- Removal semantics must be explicit and deterministic; silent cascade behavior will become a source of later bugs.
- Implemented the shared mutation/invalidation contract in `src/pygrc/core/mutations.py`.
- Chosen explicit mutation record type: `GraphMutation`.
- Chosen invalidation contract type: `CacheInvalidation`.
- Chosen default topology invalidation policy: `TOPOLOGY_MUTATION_INVALIDATION` with `clear_all=True`.
- This means the Phase 2 reference rule is conservative:
  - any topology mutation may invalidate all derived cached quantities
  - later phases may add narrower invalidation keys without changing the contract shape
- Chosen graph-state boundary:
  - invalidation markers live on the backend as emitted mutation metadata
  - actual cache clearing may happen on the state object through a registered hook
- Implemented shared invalidation helpers:
  - `apply_cache_invalidation(...)`
  - `invalidate_state_cached_quantities(...)`
- Extended the protocol layer in `src/pygrc/core/graph.py` with `MutationAwareStorageProtocol`.
- Chosen mutation visibility mechanism for both backends:
  - `set_cache_invalidation_hook(...)`
  - `clear_cache_invalidation_hook()`
  - `consume_pending_mutations()`
- Chosen mutation emission behavior:
  - `add_node`, `add_edge`, `remove_edge`, and `remove_node` emit explicit `GraphMutation` records on the weighted backend
  - `connect_ports`, `rewire_edge`, `remove_edge`, and `remove_node` emit explicit `GraphMutation` records on the port backend
- Chosen cascade representation:
  - `remove_node` records include `cascade_edge_ids`
  - actual incident edge removals still emit their own explicit `remove_edge` mutations
- This keeps the cascade visible without hiding the underlying edge-removal sequence.
- Updated `src/pygrc/core/__init__.py` to export the mutation/invalidation surface.
- Added dedicated tests in `tests/core/test_mutations_and_invalidation.py`.
- Updated `tests/core/test_module_imports.py` so `pygrc.core.mutations` is part of the shared core import surface.

### Verification

- [x] Mutation operations are explicit and testable
- [x] Removal cannot leave adjacency or port occupancy in an inconsistent state
- [x] The invalidation policy is explicitly compatible with `GRCState.cached_quantities`

### Summary

Implemented the explicit mutation and cache-invalidation layer for Phase 2. Both graph backends now emit deterministic `GraphMutation` records, expose a narrow mutation-aware contract, and can notify an owning `GRCState` to clear `cached_quantities` through a registered invalidation hook without embedding any family-specific cache semantics.

## Iteration 6. Adapter Boundary Definition

### Goal

Record the future adapter boundary clearly enough that later `networkx` and visualization adapters can attach without changing the execution substrate.

### Checks

- [x] Define where future analysis/interchange adapters attach to the protocol layer
- [x] Define where future visualization/export adapters attach
- [x] Confirm that no external adapter is required for authoritative execution
- [x] Confirm that future adapters can target the protocol layer rather than a new core-model-specific API
- [x] Keep adapter definitions out of `src/pygrc/core/` execution logic if no implementation is required yet

### Implementation Notes

- This iteration may be mostly documentation and boundary-shaping rather than executable code.
- The important outcome is a stable attachment story, not early adapter implementation.
- Any adapter mention must remain consistent with the no-`networkx`/no-`pyvis` core execution rule.
- Added the companion boundary doc `implementation/Phase-2-BackendMatrix.md`.
- That document records the authoritative execution rule explicitly:
  - `WeightedGraphBackend` remains authoritative for `GRCV2` / `GRCV3`
  - `PortGraphBackend` remains authoritative for `GRC9` / `GRC9V3`
  - `networkx`, `pyvis`, and similar libraries remain non-authoritative adapters only
- Implemented the integration-side boundary module in `src/pygrc/integrations/graph_adapter_boundary.py`.
- Chosen integration-side boundary types:
  - `AdapterBoundary`
  - `WeightedGraphInterchangeAdapter`
  - `PortGraphInterchangeAdapter`
  - `GraphVisualizationAdapter`
- Chosen boundary attachment points:
  - future weighted interchange/analysis adapters target `WeightedGraphProtocol`
  - future port interchange/analysis adapters target `PortGraphProtocol`
  - future visualization/export adapters target `GraphStorageProtocol`
- Chosen import direction for authoritative execution:
  - weighted interchange adapters import into `WeightedGraphBackend`
  - port interchange adapters import into `PortGraphBackend`
- This keeps the authoritative execution substrate in-house while still making the integration boundary concrete in code.
- Updated `src/pygrc/integrations/__init__.py` to export the integration-side boundary surface.
- Added focused integration tests in `tests/integrations/test_graph_adapter_boundary.py`.

### Verification

- [x] The adapter boundary is explicit in code and/or planning notes
- [x] No external adapter is required by the Phase 2 backends
- [x] The protocol layer remains broad enough for future adapter satisfaction

### Summary

Defined the Phase 2 adapter boundary in both `implementation/Phase-2-BackendMatrix.md` and `src/pygrc/integrations/graph_adapter_boundary.py`. Future `networkx`-style and visualization adapters now have a concrete integration-side attachment point that targets the protocol surface and imports back into the authoritative in-house backends instead of replacing the core execution substrate.

## Iteration 7. Graph/Storage Tests

### Goal

Build the Phase 2 structural and mutation-focused test suite for the graph/storage substrate.

### Checks

- [x] Add tests for monotone ID allocation
- [x] Add tests for no-reuse semantics
- [x] Add tests for tombstoning behavior
- [x] Add tests for deterministic live iteration order
- [x] Add tests for weighted-graph adjacency and mutation
- [x] Add tests for port ordering, occupancy, and lookup
- [x] Add tests for row/column conversion
- [x] Add tests for invalidation markers, hooks, or signals
- [x] Keep the tests focused on substrate structure and mutation rather than model equations

### Implementation Notes

- Phase 2 tests should prove substrate correctness before model-family logic begins.
- Tests should stay deterministic and independent of later family implementations.
- The test suite should cover both positive structure behavior and negative or inconsistent-mutation cases where relevant.
- Expanded `tests/core/test_ids.py` to cover:
  - negative counter initialization rejection
  - forward restore behavior
  - stable `iter_live_items()` output
  - invalid restoration shape rejection
- Expanded `tests/core/test_weighted_graph_backend.py` to cover:
  - restoration from raw node/edge slots
  - restored adjacency rebuild
  - rejection of restored live edges with dead endpoints
  - node-ID no-reuse after deletion
- Expanded `tests/core/test_port_graph_backend.py` to cover:
  - rewiring rejection when a target slot is occupied by a different live edge
  - edge-ID no-reuse after deletion
  - restoration of live occupancy and counters
  - rejection of duplicate restored port occupancy
- Expanded `tests/core/test_mutations_and_invalidation.py` to cover:
  - clearing the invalidation hook
  - port-node removal cascade recording
- Iteration 7 broadened coverage without changing substrate semantics.
- The Phase 2 substrate suite now exercises:
  - normal mutation paths
  - restoration paths
  - invalid restoration paths
  - explicit invalidation hook behavior
  - deterministic ordering guarantees
  - ID non-reuse behavior across both backends

### Verification

- [x] The graph/storage test modules import and run cleanly
- [x] Tests cover both weighted and port-graph backends
- [x] Tests do not depend on family equations or third-party graph libraries

### Summary

Expanded the Phase 2 graph/storage suite across IDs, restoration, negative paths, deterministic ordering, and invalidation hooks. The full repo test suite now passes with 79 deterministic tests, and the substrate layer is covered as a coherent whole rather than only by per-iteration smoke checks.

## Iteration 8. Validation And Phase Closeout

### Goal

Close Phase 2 by validating the graph/storage substrate against the plan, the specs, and the Phase 0 boundary documents.

### Checks

- [x] Run the full test suite relevant to Phase 2
- [x] Verify the graph/storage modules import cleanly
- [x] Verify the backends satisfy the intended protocol boundaries
- [x] Verify weighted and port-graph substrates both exist and are test-backed
- [x] Verify no family equations leaked into the graph/storage layer
- [x] Verify no third-party graph or visualization library is required in the core execution path
- [x] Verify tombstoning, stable IDs, and deterministic iteration remain aligned with Phase 0
- [x] Verify the adapter boundary remains optional and non-authoritative
- [x] Verify Phase 2 implementation notes do not contradict the `specs/` corpus

### Implementation Notes

- This closeout should be explicit, not implied by earlier passing tests.
- If Phase 2 produces companion docs during implementation, they should also be checked here for consistency with the plan and specs.
- The main question at closeout is whether the substrate is ready for Phase 3 and Phase 4 without reopening graph/storage fundamentals.
- Full verification run used:
  - `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
- Verification result:
  - `Ran 79 tests ... OK`
- Boundary scan confirmed that `networkx` / `pyvis` appear only in:
  - specs
  - implementation docs
  - integration-boundary definitions
  - and not in `src/pygrc/core/` or `src/pygrc/models/` as execution dependencies
- Phase 2 outputs now present in code:
  - protocol layer in `src/pygrc/core/graph.py`
  - ID/tombstone layer in `src/pygrc/core/ids.py`
  - mutation/invalidation layer in `src/pygrc/core/mutations.py`
  - reference weighted and port backends in `src/pygrc/core/storage.py`
  - integration-side adapter boundary in `src/pygrc/integrations/graph_adapter_boundary.py`
- Phase 0 consistency review was performed against:
  - `Phase-0-DeterminismConventions.md`
  - `Phase-0-BoundaryDecisions.md`
- Results of that review:
  - stable integer IDs remain monotone and non-reused
  - tombstoned slots remain the default storage expectation
  - deterministic ordering remains ascending by stable IDs
  - port-slot mapping remains canonical zero-based row-major `0..8`
  - third-party graph libraries remain non-authoritative and outside core execution
- Spec-alignment review was also performed against the current `specs/` corpus.
- No contradictions were found between:
  - the Phase 2 implementation docs
  - the actual Phase 2 code
  - and the current graph/storage expectations in the specs
- No Phase 2 blockers remain for:
  - Phase 3 serialization/determinism work
  - Phase 4 `GRCV2` baseline implementation

### Verification

- [x] Phase 2 outputs satisfy the acceptance criteria in `Phase-2-ImplementationPlan.md`
- [x] The graph/storage layer remains consistent with:
  - [x] `Phase-0-DeterminismConventions.md`
  - [x] `Phase-0-BoundaryDecisions.md`
  - [x] `specs/` corpus
- [x] No unresolved Phase 2 blockers remain for serialization or `GRCV2` baseline work

### Summary

Phase 2 is complete. The repo now has the deterministic in-house graph/storage substrate promised by the plan: shared protocols, stable IDs, tombstoned reference backends for weighted and port graphs, explicit mutation/invalidation signaling, and an integration-side adapter boundary that does not compromise core execution authority. The full test suite passes with 79 tests, and there are no remaining Phase 2 blockers for Phase 3 or the `GRCV2` baseline.
