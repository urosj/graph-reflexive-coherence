# Phase 3 Implementation Checklist

This document tracks the execution of **Phase 3: Serialization + Determinism Base**.

It is intentionally separate from [`Phase-3-ImplementationPlan.md`](./Phase-3-ImplementationPlan.md):

- the plan defines scope, workstreams, boundaries, and acceptance criteria,
- this checklist records how the Phase 3 work is actually executed iteration by iteration.

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
- Keep serialization/determinism notes aligned with:
  - [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
  - [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
  - [`Phase-3-ImplementationPlan.md`](./Phase-3-ImplementationPlan.md)

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

Create the Phase 3 execution checklist and align it with the existing Phase 3 implementation plan.

### Checks

- [x] Create `Phase-3-ImplementationChecklist.md`
- [x] Link the checklist from `ImplementationPhases.md`
- [x] Align the checklist structure with the Phase 3 workstreams
- [x] Decide whether Phase 3 needs any additional companion planning docs before implementation starts

### Implementation Notes

- The execution checklist follows the same separation-of-concerns pattern used in earlier phases.
- The Phase 3 plan remains the normative planning document; this file is the execution tracker.
- Possible companion docs for this phase were already identified in the plan:
  - `Phase-3-SnapshotMatrix.md`
  - `Phase-3-DigestPolicy.md`
- Those companion docs are optional and should only be created if the implementation work outgrows the main checklist and plan.

### Verification

- [x] The checklist file exists under `implementation/`
- [x] `ImplementationPhases.md` points to the checklist
- [x] The checklist iterations map cleanly onto the Phase 3 plan

### Summary

Phase 3 now has a paired plan and execution checklist. Additional companion docs remain optional until implementation pressure makes them necessary.

## Iteration 1. Canonical Serialization Primitives

### Goal

Define the shared canonical conversion and canonical JSON helpers used by snapshots, digests, and save/load.

### Checks

- [x] Create or extend the core canonical serialization helper module
- [x] Define one shared entry point for canonical deep conversion
- [x] Define one shared entry point for canonical JSON encoding
- [x] Decide how tuples, sets, frozensets, and other non-JSON-native values are normalized
- [x] Reject non-finite floats from canonical snapshot output
- [x] Keep canonicalization deterministic and independent of Python object reprs

### Implementation Notes

- Phase 3 should centralize canonical conversion rather than duplicating it in params, snapshots, and digest helpers.
- Canonicalization must preserve the ordered-list expectations from Phase 0 rather than flattening tables into arbitrary mappings.
- The canonical conversion layer must remain family-neutral and substrate-aware.
- Extended `src/pygrc/core/serialization.py` to provide the shared canonical helpers:
  - `canonicalize_json_value(...)`
  - `canonical_json_dumps(...)`
- Chosen canonical scalar support:
  - `None`
  - `bool`
  - `int`
  - finite `float`
  - `str`
- Chosen sequence normalization:
  - `list` and `tuple` normalize to JSON lists
- Chosen set normalization:
  - `set` and `frozenset` normalize to deterministically sorted JSON lists
  - sorting is based on canonical JSON encoding of the normalized members rather than Python object reprs
- Chosen mapping normalization:
  - ordinary mappings and `MappingProxyType` normalize to deterministically key-sorted dicts
  - non-string mapping keys are rejected at the canonical JSON layer
- Chosen non-finite-float rule:
  - `inf`, `-inf`, and `nan` raise `ValueError`
- Chosen unsupported-type rule:
  - unsupported values raise `TypeError` rather than being stringified implicitly
- Refactored `src/pygrc/core/params.py` to use the shared canonical helpers instead of a private canonical JSON implementation.
- This unifies the params-hash path with the broader serializer path before digest work begins.
- Exported the new helpers from `src/pygrc/core/__init__.py`.
- Added focused tests in `tests/core/test_canonical_serialization.py`.
- Extended `tests/core/test_serialization_contract.py` to cover the new core exports.

### Verification

- [x] Canonical serialization helpers import cleanly
- [x] Identical semantic input produces identical canonical output
- [x] Non-finite floats are rejected from canonical output

### Summary

Implemented the shared Phase 3 canonical serialization primitives in `src/pygrc/core/serialization.py` and refactored params to use them. The codebase now has one canonical deep-conversion path and one canonical JSON encoding path, with deterministic normalization for mappings, tuples, and sets, plus explicit rejection of non-finite floats and unsupported value types.

## Iteration 2. Snapshot Builder Layer

### Goal

Turn the Phase 1 snapshot contract into real deterministic snapshot builder helpers.

### Checks

- [x] Extend the snapshot helper layer beyond metadata validation
- [x] Define shared builders for metadata, topology, and optional groups
- [x] Preserve canonical top-level group ordering
- [x] Keep unsupported groups omitted unless explicitly needed
- [x] Exclude mutation-history journals from standard snapshots
- [x] Keep future exact-replay extensions out of the standard snapshot baseline

### Implementation Notes

- This iteration should produce a reusable builder layer, not ad hoc per-family dict assembly.
- The output should still satisfy the Phase 1 snapshot contract while becoming more implementation-capable.
- Standard snapshots should serialize live records only.
- Extended `src/pygrc/core/serialization.py` with shared builder helpers:
  - `build_topology_snapshot(...)`
  - `build_dynamics_group(...)`
  - `build_event_records(...)`
  - `build_standard_snapshot(...)`
- Added the canonical top-level group-order constant:
  - `SNAPSHOT_GROUP_ORDER`
- Chosen standard snapshot assembly rule:
  - required groups are `metadata` and `topology`
  - optional groups are included only when explicitly provided
  - omitted groups are not emitted as empty placeholders by default
- Chosen topology-builder behavior:
  - `nodes`, `edges`, `incidence`, and `port_structure` are independently optional
  - provided payloads are canonicalized through the shared Phase 3 canonical JSON path
- Chosen dynamics-builder behavior:
  - `state` is a named optional section
  - additional sections can be added by keyword
  - all included payloads are canonicalized before inclusion
- Chosen event-builder behavior:
  - event lists are canonicalized into stable JSON-safe record lists
  - standard snapshots treat events as ordinary event records, not as mutation journals
- Chosen standard snapshot policy:
  - top-level groups are emitted in the canonical Phase 0 order
  - mutation-history journals are explicitly rejected from the standard snapshot baseline
  - future exact-replay or machine-driver extensions must add extra history through separate paths rather than redefining standard snapshots
- Exported the new builder helpers from `src/pygrc/core/__init__.py`.
- Extended `tests/core/test_serialization_contract.py` with builder-level coverage for:
  - group ordering
  - omission policy
  - event canonicalization
  - mutation-history exclusion

### Verification

- [x] Shared snapshot builders import and run cleanly
- [x] Snapshot group order remains canonical
- [x] Standard snapshots exclude mutation-history journals

### Summary

Implemented the shared snapshot builder layer in `src/pygrc/core/serialization.py`. The codebase now has canonical builders for topology, dynamics, events, and standard snapshots, with explicit top-level group ordering, omitted unsupported groups by default, and a clear rule that standard snapshots exclude mutation-history journals.

## Iteration 3. Weighted And Port Topology Export

### Goal

Define deterministic topology export from the Phase 2 weighted and port backends into the common snapshot `topology` group.

### Checks

- [x] Implement weighted-backend topology export
- [x] Implement port-backend topology export
- [x] Include stable IDs explicitly in node and edge records
- [x] Define incidence and port-structure export policy
- [x] Keep exported topology readable without leaking backend internals
- [x] Keep canonical snapshots focused on live records unless exact-replay support is explicitly introduced later

### Implementation Notes

- Weighted and port topology export should be explicit rather than flattened into one ambiguous structure.
- Export helpers must preserve deterministic ordering established by the Phase 2 substrate.
- This iteration should remain substrate-focused and must not add family equations.
- Extended `src/pygrc/core/serialization.py` with substrate export helpers:
  - `export_weighted_topology(...)`
  - `export_port_topology(...)`
- Chosen weighted topology export shape:
  - `nodes` is an ordered list of live node records with:
    - `node_id`
    - `payload`
  - `edges` is an ordered list of live edge records with:
    - `edge_id`
    - `node_a`
    - `node_b`
    - `payload`
  - `incidence` maps node IDs to ordered incident edge ID lists
- Chosen port topology export shape:
  - `nodes` is an ordered list of live node records with:
    - `node_id`
    - `payload`
  - `edges` is an ordered list of live port-edge records with:
    - `edge_id`
    - `endpoint_a = {node_id, slot}`
    - `endpoint_b = {node_id, slot}`
    - `payload`
  - `incidence` maps node IDs to ordered incident edge ID lists
  - `port_structure` exposes per-node ordered port records with:
    - `slot`
    - `row`
    - `column`
    - `occupied`
    - `edge_id`
- Chosen live-record policy:
  - topology export serializes live nodes and edges only
  - tombstoned slots remain internal substrate state and are not part of the standard topology export
- Chosen readability boundary:
  - exports include stable IDs and occupancy information explicitly
  - exports do not expose raw slot tables, adjacency sets, or other backend internals directly
- Export helpers canonicalize payloads through the shared Phase 3 canonical JSON path.
- Exported the new topology helpers from `src/pygrc/core/__init__.py`.
- Extended `tests/core/test_serialization_contract.py` with topology-export coverage for:
  - deterministic weighted export
  - deterministic port export
  - live-record-only behavior
  - compatibility with the common snapshot contract

### Verification

- [x] Weighted topology export is deterministic
- [x] Port topology export is deterministic
- [x] Exported topology remains compatible with the common snapshot contract

### Summary

Implemented deterministic weighted and port topology export in `src/pygrc/core/serialization.py`. The shared snapshot layer can now turn both Phase 2 substrates into contract-compatible `topology` groups with explicit stable IDs, ordered incidence data, and readable port occupancy structure while keeping tombstoned slots and raw backend internals out of standard snapshots.

## Iteration 4. Save/Load Path

### Goal

Implement the deterministic save/load path for shared substrate-backed snapshots.

### Checks

- [x] Implement pure in-memory save/load helpers around the common snapshot form
- [x] Implement file-based save/load helpers
- [x] Reuse or extend `validate_snapshot_contract(...)` before substrate restoration
- [x] Keep strict validation as the default load mode
- [x] Preserve counters, IDs, params identity, and topology structure during load
- [x] Implement atomic write behavior for on-disk saves
- [x] Keep snapshot version handling explicit and current-version-only

### Implementation Notes

- Incoming data must be validated structurally before any substrate object is restored.
- Atomic writes should prevent partial-save corruption from overwriting a valid previous file.
- Migration helpers are out of scope unless a second snapshot version actually appears.
- Extended `src/pygrc/core/serialization.py` with shared save/load helpers:
  - `snapshot_to_json(...)`
  - `snapshot_from_json(...)`
  - `save_snapshot(...)`
  - `load_snapshot(...)`
- Chosen in-memory save/load rule:
  - `snapshot_to_json(...)` first validates the snapshot contract, then emits canonical JSON
  - `snapshot_from_json(...)` parses JSON and immediately applies strict snapshot validation
- Chosen strict-load baseline:
  - malformed JSON raises `SnapshotCompatibilityError`
  - non-mapping decoded payloads raise `SnapshotCompatibilityError`
  - schema-mismatched or structurally incomplete snapshots are rejected before any restoration begins
  - no lenient mode is implemented in Phase 3
- Chosen file-I/O behavior:
  - file saves use a temp file in the target directory
  - the temp file is flushed and fsynced
  - `os.replace(...)` performs the final atomic path replacement
- Chosen restoration helpers:
  - `restore_weighted_graph(...)`
  - `restore_port_graph(...)`
- Chosen restoration policy:
  - live IDs and `next_*_id` counters are preserved exactly from snapshot metadata
  - topology restoration rebuilds authoritative backends rather than fabricating ad hoc graph objects
  - duplicate IDs or structurally invalid endpoint data raise `SnapshotCompatibilityError`
- Chosen live-record restoration boundary:
  - standard snapshots restore live records only
  - tombstoned gaps may still be reconstructed internally when IDs imply sparse live tables
  - standard snapshots do not encode a separate exact-replay tombstone journal
- Current-version-only handling remains explicit through the existing `snapshot_version` contract and strict validation path.
- Exported the new helpers from `src/pygrc/core/__init__.py`.
- Extended `tests/core/test_serialization_contract.py` with save/load and restoration coverage for:
  - canonical JSON roundtrip
  - malformed input rejection
  - atomic file-save/load roundtrip
  - weighted substrate restoration
  - port substrate restoration

### Verification

- [x] Save/load roundtrip is stable for shared substrate objects
- [x] Malformed or schema-mismatched snapshots are rejected before restoration
- [x] Atomic write behavior is in place for file-based saves

### Summary

Implemented the shared deterministic save/load path in `src/pygrc/core/serialization.py`. The serializer now supports canonical in-memory snapshot text, strict incoming validation, atomic file writes, and restoration of both weighted and port substrates with stable IDs and counters preserved from snapshot metadata.

## Iteration 5. Digest And Persistence Policy

### Goal

Implement the shared digest layer together with RNG-state and remainder persistence rules.

### Checks

- [x] Create the shared digest helper module if needed
- [x] Define the canonical digest entry point
- [x] Use `sha256` over canonical serialized content
- [x] Define full-snapshot and/or topology-level digest helpers as planned
- [x] Preserve raw params, resolved params, and params hash through snapshot flow
- [x] Define the shared RNG-state persistence baseline
- [x] Define bounded remainder persistence handling

### Implementation Notes

- Digests must be computed from canonical serialized content rather than Python object structure or repr formatting.
- Phase 3 uses Python `random` state shape as the shared baseline when a common RNG hook is needed.
- Remainder must be preserved as represented state and not recomputed during load.
- Added the shared digest module at `src/pygrc/core/digests.py` with:
  - `DIGEST_ALGORITHM = "sha256"`
  - `digest_canonical_data(...)`
  - `digest_snapshot(...)`
  - `digest_topology(...)`
- Chosen digest rule:
  - digest input is the canonical JSON text emitted by `canonical_json_dumps(...)`
  - digest output is the lowercase hexadecimal `sha256` digest of that text's UTF-8 bytes
- Extended `src/pygrc/core/serialization.py` with shared persistence helpers:
  - `serialize_rng_state(...)`
  - `deserialize_rng_state(...)`
  - `serialize_runtime_rng_state(...)`
  - `build_state_payload(...)`
  - `restore_state_payload(...)`
- Chosen RNG persistence baseline:
  - Python `random` state is stored as tagged payload
    - `{"engine": "python_random", "state": ...}`
  - tagged RNG payloads are preserved as canonical JSON-safe mappings
  - untagged non-`None` RNG payloads are canonicalized as-is
- Chosen state-persistence rule:
  - `build_state_payload(...)` persists:
    - `topology`
    - `node_values`
    - `edge_values`
    - `step_index`
    - `time`
    - `budget_target`
    - `remainder`
    - `cached_quantities`
    - `event_log`
    - `observables`
    - `rng_state`
    - `params_identity`
  - `restore_state_payload(...)` rebuilds `GRCState` and `GRCEvent` objects from that serialized form
- Chosen remainder rule:
  - remainder is serialized exactly as represented state
  - restore logic preserves it directly and does not recompute it
- `build_snapshot_metadata(...)` now routes optional `rng_state` through the shared RNG serializer.
- Exported the digest helpers and the new state/RNG persistence helpers from `src/pygrc/core/__init__.py`.
- Added focused tests in `tests/core/test_digests_and_persistence.py`.
- Extended `tests/core/test_module_imports.py` to cover `pygrc.core.digests`.

### Verification

- [x] Identical canonical content produces identical digests
- [x] Params identity is preserved through snapshot/save/load flow
- [x] RNG-state and remainder persistence rules are explicit and testable

### Summary

Implemented the shared digest and persistence policy layer. Phase 3 now has explicit `sha256` digest helpers, tagged Python `random` state persistence, and a shared `GRCState` payload roundtrip that preserves remainder, params identity, observables, caches, and event-log structure without introducing any family equations.

## Iteration 6. Family Stub Integration

### Goal

Upgrade the family stubs so they use the shared serialization/save/load layer rather than temporary stub-only behavior.

### Checks

- [x] Replace any temporary stub-only snapshot behavior that is superseded by the shared serializer
- [x] Route family-stub save/load through the shared serialization path
- [x] Keep family stubs non-executable as models
- [x] Avoid introducing any family equations into Phase 3

### Implementation Notes

- This iteration should make persistence real for stubs without turning them into working model families.
- The point is to stabilize the persistence boundary before Phase 4, not to enrich family semantics.
- Updated `src/pygrc/models/_base.py` so family stubs no longer use ad hoc JSON read/write logic.
- Chosen stub snapshot policy:
  - `snapshot()` now builds its payload through the shared Phase 3 helpers:
    - `build_snapshot_metadata(...)`
    - `build_topology_snapshot(...)`
    - `build_state_payload(...)`
    - `build_dynamics_group(...)`
    - `build_standard_snapshot(...)`
  - stub topology remains the minimal empty topology group because Phase 3 still avoids family equations and substrate-specific model semantics here
- Chosen stub save/load policy:
  - `save(...)` now delegates to `save_snapshot(...)`
  - `load(...)` now delegates to `load_snapshot(...)`, then:
    - validates the family through `require_snapshot_family(...)`
    - restores state through `restore_state_payload(...)`
    - rebuilds params from serialized raw params in `metadata.params`
- Chosen persistence boundary:
  - stubs inherit the shared RNG serialization path automatically through:
    - `build_snapshot_metadata(...)`
    - `build_state_payload(...)`
  - stubs remain non-executable and still raise `NotImplementedError` from `step()`
- No family equations or family-specific serializer branches were introduced.
- Extended `tests/models/test_family_stubs.py` to verify:
  - save/load roundtrip through the shared serializer path
  - RNG metadata tagging on saved snapshots
  - params-hash preservation
  - shared snapshot group shape from the stub `snapshot()` path

### Verification

- [x] Family stubs use the shared serialization path
- [x] Family stubs remain non-executable as models
- [x] No family-specific equation logic appears in the serialization layer

### Summary

Upgraded the family stubs to the shared Phase 3 persistence path. Stub snapshots, file saves, and file loads now flow through the common serializer/builders instead of temporary JSON logic, while the stubs remain intentionally non-executable and free of family-equation behavior.

## Iteration 7. Roundtrip And Determinism Tests

### Goal

Build the serialization/determinism test suite for canonical conversion, digests, and roundtrip behavior.

### Checks

- [x] Add tests for canonical JSON conversion
- [x] Add tests for save/load roundtrip on weighted substrate snapshots
- [x] Add tests for save/load roundtrip on port substrate snapshots
- [x] Add tests for digest stability
- [x] Add tests for params-hash preservation across roundtrip
- [x] Add tests that malformed or mismatched snapshots are rejected before restoration
- [x] Add tests for RNG-state and remainder persistence where applicable
- [x] Add tests for atomic-save helper behavior

### Implementation Notes

- Phase 3 tests should prove reproducibility before the first executable family model is built.
- Tests should stay deterministic and should not depend on family equations.
- The suite should cover both positive roundtrip cases and invalid-input cases.
- Phase 3 test coverage now spans multiple focused modules rather than one monolithic file:
  - `tests/core/test_canonical_serialization.py`
  - `tests/core/test_serialization_contract.py`
  - `tests/core/test_digests_and_persistence.py`
  - `tests/models/test_family_stubs.py`
- Canonical JSON conversion coverage lives in:
  - `test_canonical_serialization.py`
  - plus export/builder canonicalization checks in `test_serialization_contract.py`
- Weighted substrate roundtrip coverage now includes:
  - in-memory snapshot roundtrip
  - atomic file save/load
  - weighted substrate restoration with ID/counter preservation
- Port substrate roundtrip coverage now includes:
  - deterministic topology export
  - substrate restoration
  - file-based snapshot save/load roundtrip with params-hash preservation
- Digest stability coverage now includes:
  - canonical-data digest stability across mapping order
  - snapshot/topology digest stability for equivalent content
- Invalid-input coverage now includes:
  - malformed JSON rejection
  - decoded non-mapping rejection
  - invalid contract rejection before restoration
  - family-mismatch rejection on stub load
- RNG/remainder persistence coverage now includes shared `GRCState` payload roundtrip and stub save/load persistence.
- Atomic-save behavior remains covered at the file-path boundary through `save_snapshot(...)` tests.

### Verification

- [x] Serialization test modules import and run cleanly
- [x] Roundtrip tests cover both weighted and port substrates
- [x] Tests do not depend on family equations or third-party persistence frameworks

### Summary

Completed the Phase 3 roundtrip/determinism test pass. The serializer, digests, RNG/remainder persistence rules, substrate restore paths, and stub persistence boundary are now covered by a coherent deterministic test suite across both weighted and port substrates.

## Iteration 8. Validation And Phase Closeout

### Goal

Close Phase 3 by validating the serialization/determinism layer against the plan, the specs, and the earlier deterministic boundary documents.

### Checks

- [x] Run the full test suite relevant to Phase 3
- [x] Verify the serialization and digest modules import cleanly
- [x] Verify canonical JSON output is stable for identical semantic input
- [x] Verify save/load preserves IDs, counters, params identity, and ordering
- [x] Verify weighted and port substrate snapshots both use shared serialization code
- [x] Verify no family equations leaked into the serialization layer
- [x] Verify no third-party graph or persistence framework is required for the reference path
- [x] Verify Phase 3 implementation notes do not contradict the `specs/` corpus
- [x] Verify no unresolved Phase 3 blockers remain for Phase 4

### Implementation Notes

- This closeout should be explicit, not implied by earlier passing tests.
- If Phase 3 produces companion docs during implementation, they should also be checked here for consistency with the plan and specs.
- The main question at closeout is whether persistence and determinism are now stable enough for the first executable family implementation.
- Full verification run used:
  - `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
  - result: `Ran 107 tests ... OK`
- Import-cleanliness is now covered both by the dedicated module-import tests and by the full suite.
- Save/load preservation is covered across:
  - weighted substrate snapshot/file/restore paths
  - port substrate snapshot/file/restore paths
  - family-stub save/load via the shared serializer path
- Specification-alignment review completed:
  - snapshot group ordering still follows the Phase 0 convention
  - raw params, resolved params, and params hash remain preserved
  - RNG-state and remainder persistence match the common-interface contract
  - standard snapshots still exclude mutation-history journals
- Boundary review completed:
  - no family equations were added to `src/pygrc/core/serialization.py` or `src/pygrc/core/digests.py`
  - no third-party graph or persistence framework is required anywhere in the reference path
  - serializer logic remains substrate-aware but adapter-independent
- No additional companion docs were needed for this phase.

### Verification

- [x] Phase 3 outputs satisfy the acceptance criteria in `Phase-3-ImplementationPlan.md`
- [x] The serialization/determinism layer remains consistent with:
  - [x] `Phase-0-DeterminismConventions.md`
  - [x] `Phase-0-BoundaryDecisions.md`
  - [x] `specs/` corpus
- [x] No unresolved Phase 3 blockers remain for `GRCV2` baseline work

### Summary

Phase 3 is complete. The repo now has a stable shared serialization and determinism base: canonical JSON conversion, substrate-aware snapshot builders, atomic save/load, digest helpers, RNG/remainder persistence rules, and stub integration, all backed by a full green test suite and aligned with the earlier determinism/spec boundary documents.
