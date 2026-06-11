# Phase 3 Implementation Plan

This document is the detailed execution plan for **Phase 3: Serialization + Determinism Base**.

It turns the Phase 3 summary in `ImplementationPhases.md` into concrete serialization,
canonicalization, hashing, and roundtrip workstreams.

Phase 3 exists to make model state, params, and save/load behavior reproducible before
family-level simulation logic becomes substantially more complex.

## Purpose

Phase 3 must establish:

- canonical JSON-safe serialization for snapshots and state-like structures,
- deterministic snapshot building on top of the Phase 1 contract and Phase 2 storage substrate,
- stable save/load behavior for the reference implementation,
- canonical params and state digest support,
- explicit RNG-state persistence hooks,
- and deterministic roundtrip testing before the first executable model family is built.

Phase 3 should make later model-family implementations easy to persist, compare, replay,
and debug without forcing ad hoc serializer logic into each family.

## Inputs From Earlier Phases

Phase 3 assumes the following outputs already exist and remain authoritative:

- Phase 0 determinism conventions in [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
- Phase 0 implementation boundaries in [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
- Phase 1 shared contracts in `src/pygrc/core/`
- Phase 2 graph/storage substrate in `src/pygrc/core/`

In particular, Phase 3 builds on:

- the Phase 1 snapshot contract in `src/pygrc/core/serialization.py`
- the canonical params identity support in `src/pygrc/core/params.py`
- the stable ID and tombstoning behavior from `src/pygrc/core/ids.py`
- the weighted and port-graph backends in `src/pygrc/core/storage.py`

Phase 3 must not silently contradict those documents or reinterpret their boundaries.

## In Scope

- canonical JSON-safe serialization helpers
- deterministic deep conversion of snapshot/state content into canonical data
- snapshot builder utilities for weighted and port-graph substrates
- deterministic save/load path for shared substrate objects
- param serialization and param-hash preservation
- state digest support
- RNG-state persistence hooks at the shared layer
- bounded remainder serialization rules
- roundtrip and reproducibility tests

## Out Of Scope

- `GRCV2` step equations
- `GRCV3` differential summaries
- `GRC9` refinement/expansion mechanics
- causal or observer-level projection logic
- machine-driver diff/patch workflows
- external adapter implementations
- visualization/export tooling beyond canonical snapshot form

## Phase 3 Design Constraints

### 1. Contract Before Family Logic

Phase 3 must finish the shared save/load and digest story before Phase 4 introduces
the first full model loop.

Family implementations should inherit or call into a common serialization layer rather
than reimplementing persistence independently.

### 2. Canonical Form Over Convenient Form

The reference implementation must prefer deterministic canonical forms over merely
serializable forms.

That means Phase 3 should preserve:

- canonical top-level snapshot group order,
- ordered node/edge tables as lists,
- deterministic key ordering inside mappings,
- JSON-safe primitive normalization,
- and stable preservation of `params_hash`, `next_node_id`, `next_edge_id`, and
  other deterministic metadata.

### 3. Substrate-Aware, Family-Neutral

The serializer layer must understand the shared weighted and port graph substrates
without hardcoding model-family equations or basin semantics.

Phase 3 should support:

- weighted graph topology export,
- port graph topology export,
- common state bookkeeping export,
- and later family-specific extension groups layered on top.

### 4. No Third-Party Serialization Dependency

The canonical serializer must be implemented in-house and must not rely on an external
graph or persistence framework.

Standard-library JSON support is acceptable. The important boundary is that canonical
serialization semantics remain under direct project control.

### 5. Replay-Oriented Determinism

The save/load path should support deterministic replay for later model families.

That means Phase 3 must explicitly carry:

- resolved params,
- params hash,
- stable next-ID counters,
- bounded remainder representation,
- and RNG state hooks where relevant.

## Expected Code Shape After Phase 3

The exact files may still evolve, but the intended Phase 3 shape is close to:

```text
src/pygrc/
  core/
    serialization.py
    params.py
    storage.py
    digests.py
```

The exact split may differ, but the serialization/digest boundary should already be clear.

## Workstreams

## 1. Canonical Serialization Primitives

### Tasks

- Define canonical deep-conversion helpers for JSON-safe serialization.
- Normalize supported scalar, sequence, and mapping forms into deterministic output.
- Decide how tuples, sets, frozensets, and other non-JSON-native values are encoded.
- Keep the canonicalization rules consistent with Phase 0 snapshot determinism.

### Required Decisions

- canonical mapping order is deterministic
- ordered tables remain lists
- non-finite floats are rejected from canonical snapshots
- canonical JSON output uses one stable formatting rule

### Acceptance Criteria

- Canonical conversion has one shared implementation entry point.
- Snapshot builders do not need to hand-roll JSON normalization.
- The canonical form is stable for identical semantic input.

## 2. Snapshot Builder Layer

### Tasks

- Extend the Phase 1 snapshot contract into real snapshot builder helpers.
- Define shared builders for:
  - metadata group
  - topology group
  - dynamics group
  - event export
  - cache export policy
- Keep group emission aligned with the canonical group ordering from Phase 0.

### Required Decisions

- unsupported groups are omitted rather than emitted empty unless explicitly needed
- node/edge tables are emitted as ordered lists of records
- topology export for weighted vs port graphs is explicit and not flattened
- standard snapshots serialize live records only and exclude mutation-history journals
- future exact-replay or machine-driver modes may add extra history metadata, but they
  must not redefine the standard snapshot baseline

### Acceptance Criteria

- A common builder path exists for substrate-backed snapshots.
- Snapshot group order follows the Phase 0 conventions.
- The builder layer is ready for family-specific extensions in Phase 4 and later.

## 3. Weighted And Port Topology Export

### Tasks

- Define deterministic topology export from `WeightedGraphBackend`.
- Define deterministic topology export from `PortGraphBackend`.
- Decide how incidence and port-structure metadata are represented.
- Decide what restoration-oriented metadata belongs in snapshots versus internal-only storage.

### Required Decisions

- canonical node and edge tables include stable IDs explicitly
- port topology export exposes row/column-relevant occupancy structure without leaking backend internals
- canonical snapshots serialize live records only unless an exact-replay mode is explicitly introduced later

### Acceptance Criteria

- Both backends can be exported into the common `topology` group deterministically.
- Exported topology remains compatible with the Phase 1 snapshot contract.
- Weighted and port topology are both readable without requiring backend internals.

## 4. Save/Load Path

### Tasks

- Implement deterministic snapshot-to-disk save helpers.
- Implement deterministic load helpers back into shared substrate objects.
- Reuse or extend the Phase 1 `validate_snapshot_contract(...)` path before converting
  incoming data into substrate objects.
- Decide where file I/O helpers live versus pure in-memory serializer helpers.
- Ensure save/load preserves canonical metadata and next-ID counters.
- Define the reference write strategy for durable saves.

### Required Decisions

- save/load format versioning is explicit
- the incoming load path performs structural validation before substrate restoration
- the reference write path uses atomic file replacement rather than in-place overwrite
- model-family mismatch remains a hard validation error where appropriate
- load paths restore substrate state without reassigning IDs
- Phase 3 uses a strict validation baseline by default; any future lenient mode must
  be an explicit opt-in extension rather than the default behavior

### Versioning Strategy

- `snapshot_version` remains the schema/version field in the metadata group
- Phase 3 supports the current version only and treats unknown versions as hard errors
- migration helpers are deferred unless a second concrete snapshot version appears
- if later phases introduce schema evolution, migration should happen in an explicit
  compatibility layer rather than being hidden inside normal substrate restoration

### Acceptance Criteria

- Save/load roundtrip is stable for shared substrate objects.
- Canonical metadata survives roundtrip intact.
- Load does not silently alter IDs, counters, or topology structure.
- Malformed or schema-mismatched incoming data is rejected before restoration begins.

## 5. State Digest And Comparison Support

### Tasks

- Define a canonical digest for serialized snapshots or state groups.
- Decide the digest boundary:
  - full snapshot digest
  - topology-only digest
  - params digest reuse
- Keep digest computation deterministic and shared.

### Required Decisions

- digest algorithm is explicit and stable
- digest input is the canonical serialized form, not ad hoc object reprs
- digest helpers remain family-neutral

### Digest Baseline

- Phase 3 uses `sha256` as the reference digest algorithm
- digests are computed over canonical serialized bytes or their canonical JSON string
- digest helpers must not depend on Python object identity or repr formatting

### Acceptance Criteria

- Identical canonical state produces identical digests.
- State digesting is ready for later replay and verification work.
- Digest helpers do not depend on model-family equations.

## 6. RNG State And Remainder Persistence

### Tasks

- Define the shared persistence rule for optional RNG state.
- Define bounded remainder serialization in line with the common state contract.
- Decide what it means for a family to omit RNG state.
- Ensure these values flow through snapshot/save/load helpers cleanly.
- Select the Phase 3 reference RNG baseline for persisted shared-state hooks.

### Required Decisions

- RNG state is included when present and omitted when absent
- remainder is preserved as represented state, not recomputed on load
- no hidden environment state may alter replay after load
- Phase 3 uses Python `random` state shape as the reference shared RNG hook when
  a common-library RNG baseline is needed; other RNG engines may be added later but
  must serialize through an explicit tagged representation

### Acceptance Criteria

- RNG and remainder persistence are explicit in the shared serializer layer.
- Later stochastic or partially stochastic families do not need to invent their own persistence rules.
- Replay-critical bookkeeping survives roundtrip.

## 7. Family Stub Integration

### Tasks

- Upgrade the family stubs so they can use the shared save/load path.
- Replace any temporary stub-only snapshot behavior that is now superseded by the common serializer.
- Keep family stubs non-executable as models while making their persistence path real.

### Acceptance Criteria

- Family stubs use the shared serialization layer rather than isolated ad hoc logic.
- Phase 4 can build `GRCV2` on top of a stable persistence boundary.
- No family-specific equation logic is introduced in Phase 3.

## 8. Roundtrip And Determinism Tests

### Tasks

- Add tests for canonical JSON conversion.
- Add save/load roundtrip tests for weighted and port substrate snapshots.
- Add digest-stability tests.
- Add tests for params-hash preservation across roundtrip.
- Add tests that malformed or mismatched incoming snapshots are rejected before restoration.
- Add tests for RNG-state and remainder persistence where applicable.
- Add tests for atomic-save helper behavior at the file-path boundary.

### Acceptance Criteria

- Serialization tests are deterministic and comprehensive enough to trust before Phase 4.
- Roundtrip tests exercise both positive and invalid/mismatch cases.
- The shared serialization layer is test-backed as a coherent whole.

## Deliverables

Phase 3 should produce:

- canonical serialization helpers
- substrate-aware snapshot builders
- deterministic save/load path
- state digest support
- RNG/remainder persistence rules
- upgraded family-stub persistence path
- serialization-focused tests

## Acceptance Criteria

Phase 3 is complete only if all of the following are true.

### A. Structural Acceptance

- The serialization/digest modules exist and import cleanly.
- Weighted and port substrate snapshots can be built through shared code.
- Family stubs rely on the shared save/load path.

### B. Determinism Acceptance

- Canonical JSON output is stable for identical semantic input.
- Save/load roundtrip preserves IDs, counters, params identity, and ordering.
- Identical canonical state produces identical digests.

### C. Specification Alignment Acceptance

- Snapshot group ordering remains aligned with Phase 0 conventions.
- Raw params, resolved params, and params hash are preserved as required by the specs.
- RNG-state and remainder persistence rules match the current common contract.

### D. Boundary Acceptance

- No family equations are implemented in the serialization layer.
- No third-party graph or persistence framework is required for the reference path.
- The serializer understands the substrates without depending on adapter-layer code.

### E. Developer-Onboarding Acceptance

- A contributor can see where to add:
  - family-specific snapshot groups
  - replay-related digests
  - stricter exact-replay metadata later
  - machine-driver serialization extensions later

## Suggested Follow-On Documents

Once Phase 3 execution begins, it will likely be useful to add:

- `Phase-3-ImplementationChecklist.md`
- `Phase-3-SnapshotMatrix.md`
- `Phase-3-DigestPolicy.md` only if digest or replay rules outgrow the main checklist
