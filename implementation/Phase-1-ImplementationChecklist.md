# Phase 1 Implementation Checklist

This document tracks the execution of **Phase 1: Common Contracts**.

It is intentionally separate from [`Phase-1-ImplementationPlan.md`](./Phase-1-ImplementationPlan.md):

- the plan defines scope, workstreams, boundaries, and acceptance criteria,
- this checklist records how the Phase 1 work is actually executed iteration by iteration.

Each iteration should contain:

- a bounded implementation slice,
- concrete checkboxes that can be ticked off during execution,
- implementation notes recorded alongside the work,
- verification steps tied to the iteration output,
- and a short summary when the iteration closes.

## Usage Rules

- Keep iterations small enough that verification remains clear.
- Update checkboxes during implementation, not after the fact.
- Record decisions near the affected work rather than in a separate log.
- If a plan change is needed, update the plan document first or in the same change.
- If an item is deferred, leave it unchecked and add a short reason in the notes or summary.

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

Create the Phase 1 execution checklist and align it with the existing Phase 1 implementation plan.

### Checks

- [x] Create `Phase-1-ImplementationChecklist.md`
- [x] Link the checklist from `ImplementationPhases.md`
- [x] Align the checklist structure with the Phase 1 workstreams
- [x] Decide whether Phase 1 needs any additional companion planning docs before implementation starts

### Implementation Notes

- The execution checklist follows the same separation-of-concerns pattern used in Phase 0.
- The Phase 1 plan remains the normative planning document; this file is the execution tracker.
- No additional Phase 1 companion planning docs are required before implementation starts; the current plan and checklist were sufficient.

### Verification

- [x] The checklist file exists under `implementation/`
- [x] `ImplementationPhases.md` points to the checklist
- [x] The checklist iterations map cleanly onto the Phase 1 plan

### Summary

Phase 1 now has a paired plan and execution checklist. No extra companion planning docs were needed during execution.

## Iteration 1. Core Interface Surface

### Goal

Define the shared `GRCModel` contract and the minimum public model surface all families must support.

### Checks

- [x] Create the core interface module
- [x] Define the base `GRCModel` contract
- [x] Define required methods:
  - [x] `from_config(cls, config)`
  - [x] `from_state(cls, state, params)`
  - [x] `get_state()`
  - [x] `set_state(state)`
  - [x] `get_params()`
  - [x] `list_capabilities()`
  - [x] `compute_observables()`
  - [x] `step()`
  - [x] `run(num_steps)`
  - [x] `reset()`
  - [x] `snapshot()`
  - [x] `save(path)`
  - [x] `load(path)`
- [x] Keep graph/storage assumptions out of the model interface

### Implementation Notes

- The interface should be minimal and durable.
- Convenience helpers are allowed, but the required surface should stay small and family-neutral.
- The method names in this iteration are intentionally aligned with the current `grc-common-interface` spec.
- The contract should be usable by both weighted-graph and port-graph families without special cases.
- Implemented `GRCModel` as an abstract base class in `src/pygrc/core/interfaces.py`.
- `run(num_steps)` is the only concrete lifecycle helper so far; it is implemented once on the base class and delegates to `step()`.
- Return positions for state, params, and step results intentionally remain lightweight (`Any`) in this iteration so the public method surface can be fixed before Iteration 2 and Iteration 3 define the concrete shared datatypes.
- No graph, storage, or serializer backend types appear in the interface module.

### Verification

- [x] Core interface module imports cleanly
- [x] The base interface is explicit enough for family stubs to implement
- [x] No backend-specific types leak into the public model surface

### Summary

Defined the common `GRCModel` abstract base class and locked the required public method names at the code level. Added contract tests that verify the abstract surface and the shared `run()` helper behavior without introducing graph or model-family logic.

## Iteration 2. Parameter Architecture

### Goal

Define the shared parameter abstractions and the parameter-domain boundary for all families.

### Checks

- [x] Create the core parameter module
- [x] Define the base parameter abstraction
- [x] Decide and implement the immutability strategy
- [x] Define raw-config vs resolved-params separation
- [x] Define central params canonicalization hooks or contract
- [x] Define params identity/hash boundary
- [x] Encode the allowed parameter domains:
  - [x] evolution parameters
  - [x] constitutive/semantic mode parameters
  - [x] numerical backend parameters that change results
  - [x] excluded runtime/tooling parameters
- [x] Ensure mode params like `frame_mode`, `boundary_mode`, `curvature_backend`, and `edge_label_selection` are treated as real model semantics

### Implementation Notes

- Phase 1 needs the parameter boundary to be enforceable in code, not just documented.
- Family-specific param subclasses may come later, but the base shape must be ready now.
- The common layer should not depend on one serialization format yet.
- Implemented the shared base parameter object as a frozen dataclass in `src/pygrc/core/params.py`.
- Chosen immutability strategy:
  - frozen dataclass for the root object
  - recursively frozen nested mappings via `MappingProxyType`
  - tuples for sequence-like nested values
- Chosen central resolution entry point: `GRCParams.from_mapping(...)`
- Chosen identity boundary:
  - canonical identity is derived from the resolved core param mapping only
  - exposed through `params_hash` and `canonical_identity()`
- Raw config vs resolved params are both retained:
  - `raw_config` preserves the caller-facing mapping
  - `resolved_config` stores the normalized core domains used for identity
- Chosen naming alignment:
  - the second core domain is named `constitutive_semantic_modes`
  - this avoids overloading `semantic` and stays closer to the spec language
- Excluded runtime/tooling domains are rejected at the core param boundary:
  - `runtime`
  - `observer`
  - `tooling`
- Mode parameters remain part of `constitutive_semantic_modes` and therefore stay inside the core param contract.

### Verification

- [x] Parameter module imports cleanly
- [x] Parameter objects are immutable or effectively immutable
- [x] The model/runtime boundary is visible in code structure
- [x] Canonical params identity has one clear entry point

### Summary

Defined the shared parameter base and locked the Phase 1 parameter boundary in code. Core params are now immutable, raw vs resolved config is explicit, excluded runtime/tooling domains are rejected centrally, and canonical params identity is produced from one entry point.

## Iteration 3. State And Step Result Contracts

### Goal

Define the shared state and `StepResult` abstractions with the minimum fields required by the spec.

### Checks

- [x] Create the core types/state module
- [x] Define the shared state abstraction
- [x] Include the minimum shared state surface:
  - [x] `step_index`
  - [x] `time`
  - [x] `budget_target`
  - [x] `remainder`
  - [x] params reference or params identity
  - [x] observables if stored on state
  - [x] event log if stored on state
  - [x] RNG state if used
- [x] Define the shared `StepResult`
- [x] Include the minimum `StepResult` surface:
  - [x] `step_index`
  - [x] `time`
  - [x] events
  - [x] observables
  - [x] optional status or bookkeeping fields
- [x] Keep family-specific topology payloads out of the common state base

### Implementation Notes

- The common state base should be extensible without pretending all families have identical topology/state shape.
- `StepResult` should be stable enough for tests, tooling, and later machine-driver work.
- Implemented shared dataclasses in `src/pygrc/core/types.py`:
  - `GRCState`
  - `StepResult`
- `GRCState` includes generic places for spec-level state categories:
  - `topology`
  - `node_values`
  - `edge_values`
  - `cached_quantities`
  - plus the explicitly required shared bookkeeping fields
- `StepResult` now carries the spec-minimum fields directly and also provides `bookkeeping` for optional status/auxiliary data.
- Event payloads remain typed as lightweight placeholders (`Any`) for now; Iteration 4 will tighten the common event datatype itself.
- `GRCModel` was updated to use `GRCState` and `StepResult` in its public method signatures.

### Verification

- [x] State/types module imports cleanly
- [x] Shared fields align with the common-interface spec
- [x] No family-specific topology fields leak into the common state base

### Summary

Defined the shared `GRCState` and `StepResult` dataclasses and updated the base model interface to use them. The common contract now has explicit state/result types with the required bookkeeping fields while keeping topology payloads generic for later family extensions.

## Iteration 4. Events, Observables, And Errors

### Goal

Define common event, observable, and error datatypes for the contract layer.

### Checks

- [x] Create the core events module
- [x] Create the core observables module
- [x] Create the core errors module
- [x] Define the base `GRCEvent` shape
- [x] Define required shared event fields:
  - [x] event kind/type
  - [x] step index
  - [x] deterministic payload
  - [x] model-family/source context if needed
- [x] Define the base observable contract
- [x] Decide whether observables are typed records, mappings, or both
- [x] Define explicit core exceptions for:
  - [x] invalid params
  - [x] unsupported capability requests
  - [x] incompatible snapshot loading
  - [x] invalid contract-level state transitions

### Implementation Notes

- Event ordering itself is governed by the Phase 0 determinism document, but the datatypes must be compatible with it.
- Keep the error surface small and intentional.
- Implemented shared modules:
  - `src/pygrc/core/events.py`
  - `src/pygrc/core/observables.py`
  - `src/pygrc/core/errors.py`
- Chosen common event shape:
  - `kind`
  - `step_index`
  - `payload`
  - optional `source_family`
- Chosen observable contract: both
  - `ObservableMap` as the common mapping contract
  - `ObservableSnapshot` as a small typed wrapper when a structured container is useful
- Chosen core error surface:
  - `GRCError`
  - `InvalidParamsError`
  - `UnsupportedCapabilityError`
  - `SnapshotCompatibilityError`
  - `InvalidStateTransitionError`
- `GRCState` and `StepResult` now use `GRCEvent` and `ObservableMap` instead of placeholder `Any` event types.

### Verification

- [x] Event/observable/error modules import cleanly
- [x] Common event shape is usable without any family implementation
- [x] Error types are explicit and stable enough for later phases

### Summary

Defined the shared `GRCEvent`, observable contract, and core error hierarchy. The common contract layer now has explicit event and error datatypes, and the temporary event placeholders in state/result types have been replaced with the shared event type.

## Iteration 5. Capability Vocabulary

### Goal

Define the shared capability vocabulary and capability discovery contract.

### Checks

- [x] Create the core capabilities module
- [x] Define canonical capability names/constants
- [x] Distinguish always-on family properties from optional capabilities
- [x] Preserve must-not-claim boundaries in the capability design
- [x] Define the return shape of `list_capabilities()`
- [x] Ensure the capability vocabulary stays aligned with the specs

### Implementation Notes

- Capability discovery should not require consumers to inspect concrete classes or raw params.
- The capability layer should expose shared vocabulary without erasing family distinctions.
- Implemented the shared capability vocabulary in `src/pygrc/core/capabilities.py`.
- Chosen capability design:
  - string constants for the shared vocabulary
  - `ALL_CAPABILITIES` as the central vocabulary set
  - `CapabilityProfile` for family-level required/optional/forbidden boundaries
  - `FAMILY_CAPABILITY_PROFILES` for the four baseline families
- The `list_capabilities()` return shape remains `set[str]`, matching the spec and the base interface.
- Family boundaries are encoded explicitly:
  - required capabilities
  - optional capabilities
  - forbidden capabilities
- Added `CapabilityProfile.validate_claims(...)` so later family stubs can check that the capabilities they expose are real and family-consistent.

### Verification

- [x] Capabilities module imports cleanly
- [x] Capability discovery shape works for all four families
- [x] The common vocabulary stays aligned with the specs

### Summary

Defined the shared capability vocabulary and encoded the baseline capability matrix for all four families in one central module. Later family stubs can now expose spec-aligned capability sets and validate them against explicit required/optional/forbidden boundaries.

## Iteration 6. Snapshot Contract

### Goal

Define the interface-level snapshot contract without implementing the full serializer.

### Checks

- [x] Define the base snapshot return shape for `snapshot()`
- [x] Define the base load contract for `load(...)`
- [x] Ensure the snapshot contract is compatible with Phase 0 determinism conventions
- [x] Define how family-specific snapshot extensions are layered onto the common contract
- [x] Define explicit incompatibility behavior for snapshot loading
- [x] Ensure the contract anticipates:
  - [x] metadata group
  - [x] topology group
  - [x] optional basin attributes
  - [x] optional edge labels
  - [x] dynamics / observables / events / caches

### Implementation Notes

- Phase 1 defines obligations and shape only; Phase 3 implements deterministic serializer machinery.
- The contract should already be stable enough for stub-family tests.
- Implemented the interface-level snapshot contract in `src/pygrc/core/serialization.py`.
- Chosen snapshot contract components:
  - `SnapshotMetadata`
  - `TopologySnapshot`
  - `BaseSnapshot`
- Chosen schema/version constants:
  - `SNAPSHOT_SCHEMA = "pygrc.snapshot"`
  - `SNAPSHOT_VERSION = 1`
- Chosen compatibility hooks:
  - `validate_snapshot_contract(...)`
  - `require_snapshot_family(...)`
- Chosen metadata builder:
  - `build_snapshot_metadata(...)`
- Family-specific snapshot extensions are layered through optional top-level groups on `BaseSnapshot`:
  - `basin_attributes`
  - `edge_labels`
  - `dynamics`
  - `observables`
  - `events`
  - `caches`
- `GRCModel.snapshot()` now returns `BaseSnapshot` at the interface level.
- The load contract remains path-based at the public interface (`load(path)`), while snapshot compatibility is checked through the shared validation helpers.

### Verification

- [x] Snapshot contract is explicit at the interface layer
- [x] Snapshot/load incompatibility is an explicit error path
- [x] The contract does not contradict the Phase 0 conventions

### Summary

Defined the interface-level snapshot contract and explicit compatibility checks without implementing the serializer itself. The common contract layer now has typed snapshot groups, schema/version constants, and a shared incompatibility path for family/load validation.

## Iteration 7. Family Stubs

### Goal

Add the minimal family classes that prove the common contracts are implementable.

### Checks

- [x] Create `src/pygrc/models/grc_v2.py`
- [x] Create `src/pygrc/models/grc_v3.py`
- [x] Create `src/pygrc/models/grc_9.py`
- [x] Create `src/pygrc/models/grc_9_v3.py`
- [x] Define `GRCV2` stub
- [x] Define `GRCV3` stub
- [x] Define `GRC9` stub
- [x] Define `GRC9V3` stub
- [x] Ensure each family stub:
  - [x] satisfies the common contract
  - [x] exposes the correct model-family identifier
  - [x] exposes a base capability set
  - [x] binds to the appropriate params/state/result abstractions
- [x] Keep simulation logic out of the stubs

### Implementation Notes

- The stubs are proof of contract usability, not partial model implementations.
- Family differences should still be visible at the stub level.
- Implemented a shared internal stub base in `src/pygrc/models/_base.py` to avoid duplicating contract-only behavior across the four families.
- Each family stub now exposes:
  - `MODEL_FAMILY`
  - `CAPABILITY_PROFILE`
  - shared contract methods via the internal base
- `step()` is intentionally non-executable in the stub base and raises `NotImplementedError`.
- `save()`/`load()` are implemented only far enough to prove the contract is usable with the shared snapshot helpers; they do not introduce full serializer machinery.
- The stubs bind directly to:
  - `GRCParams`
  - `GRCState`
  - `BaseSnapshot`
- `list_capabilities()` returns the required capability set for the family profile and validates those claims centrally.

### Verification

- [x] All four family modules import cleanly
- [x] The family stubs satisfy the common contract
- [x] No family stub contains real simulation logic yet

### Summary

Defined the four Phase 1 family stubs and a shared internal stub base. The family layer now proves the common contract is implementable, exposes model-family identifiers and base capability sets, and remains intentionally non-executable until later phases add real model logic.

## Iteration 8. Contract Tests

### Goal

Add tests that lock the common contract surface before Phase 2 begins.

### Checks

- [x] Add core contract import tests
- [x] Add parameter immutability/effective immutability tests
- [x] Add capability discovery tests
- [x] Add family-stub import tests
- [x] Add snapshot contract shape tests
- [x] Add negative tests for explicit error cases where practical
- [x] Keep tests focused on contract shape, not model behavior

### Implementation Notes

- These tests should protect the public contract from accidental drift while later internal work proceeds.
- The tests should avoid assuming graph/storage implementation details.
- Iteration 8 mainly hardens and rounds out the contract test suite because most of the core surface was already being tested incrementally during Iterations 1-7.
- Added broad module import coverage in `tests/core/test_module_imports.py`.
- Added extra family-stub negative tests for:
  - invalid `set_state(...)` input
  - snapshot family mismatch during `load(...)`
- Existing tests from Iterations 1-7 already covered:
  - parameter immutability
  - capability discovery/profile validation
  - snapshot contract shape
  - explicit error paths
  - non-executable stub behavior

### Verification

- [x] The Phase 1 contract suite passes
- [x] The tests cover imports, shape, and explicit error paths
- [x] No test depends on later graph or equation logic

### Summary

Hardened the Phase 1 contract suite by filling the remaining gaps in import coverage and explicit negative tests. The test layer now locks the shared contract surface without depending on graph backends or model equations.

## Iteration 9. Validation And Phase Closeout

### Goal

Perform the Phase 1 closeout pass against the plan acceptance criteria.

### Checks

- [x] Run the Phase 1 contract/import test suite
- [x] Verify all common-contract modules import cleanly
- [x] Verify all family stubs import cleanly
- [x] Verify no graph/backend implementation leaked into Phase 1
- [x] Verify no family equations leaked into Phase 1
- [x] Verify runtime/tooling parameters were not pulled into core params
- [x] Verify Phase 1 code remains aligned with Phase 0 determinism and boundary decisions
- [x] Review the Phase 1 plan acceptance criteria against the repo state
- [x] Mark all completed checklist items
- [x] Add deferral notes for any remaining unchecked items
- [x] Write a Phase 1 closeout summary:
  - [x] what was created
  - [x] what contract decisions were locked
  - [x] what was deferred to Phase 2
  - [x] whether any spec clarification is still needed

### Implementation Notes

- Phase 1 should close only when the contract layer is stable enough for Phase 2 graph/storage work to build on directly.
- If implementation reveals a real contract ambiguity, record it in this checklist and update the Phase 1 plan or specs as needed.
- Validation commands executed:
  - `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
  - `.venv/bin/python -c "import pygrc.core, pygrc.core.capabilities, pygrc.core.errors, pygrc.core.events, pygrc.core.interfaces, pygrc.core.observables, pygrc.core.params, pygrc.core.serialization, pygrc.core.types; import pygrc.models, pygrc.models.grc_v2, pygrc.models.grc_v3, pygrc.models.grc_9, pygrc.models.grc_9_v3; print('phase1-imports-ok')"`
- Boundary review:
  - no graph/backend implementation exists in Phase 1 code
  - no family equations or topology update logic exist in Phase 1 code
  - core params still reject `runtime`, `observer`, and `tooling` domains
- Alignment review:
  - Phase 1 code remains consistent with the Phase 0 determinism and boundary documents
  - no contradictions were identified during closeout
- Deferral note:
  - the only remaining unchecked boxes in this file are the reusable iteration-template placeholders near the top
  - no operational Phase 1 tasks remain open

### Verification

- [x] Structural acceptance criteria are satisfied
- [x] Boundary acceptance criteria are satisfied
- [x] Specification alignment acceptance criteria are satisfied
- [x] Reproducibility acceptance criteria are satisfied
- [x] Developer-onboarding acceptance criteria are satisfied

### Summary

Phase 1 is complete.

Created:

- the common contract modules under `src/pygrc/core/`
  - `interfaces.py`
  - `params.py`
  - `types.py`
  - `events.py`
  - `observables.py`
  - `errors.py`
  - `capabilities.py`
  - `serialization.py`
- the family stub modules under `src/pygrc/models/`
  - `grc_v2.py`
  - `grc_v3.py`
  - `grc_9.py`
  - `grc_9_v3.py`
  - shared internal stub base `_base.py`
- the Phase 1 contract test suite across `tests/core/` and `tests/models/`

Locked contract decisions:

- the exact public `GRCModel` method surface
- immutable shared parameter architecture with explicit core/excluded domains
- shared `GRCState` and `StepResult` datatypes
- shared `GRCEvent`, observable contract, and core error hierarchy
- central capability vocabulary plus family capability profiles
- interface-level snapshot contract with explicit compatibility checks
- non-executable family stubs as the Phase 1 proof of contract usability

Deferred to Phase 2:

- weighted-graph backend implementation
- port-graph backend implementation
- graph/storage mutation logic
- model-family step logic and equations
- deterministic serializer mechanics beyond the Phase 1 contract shape

Spec clarification needed before Phase 2:

- none identified at Phase 1 closeout.
