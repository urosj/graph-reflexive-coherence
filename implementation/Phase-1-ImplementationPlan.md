# Phase 1 Implementation Plan

This document is the detailed execution plan for **Phase 1: Common Contracts**.

It turns the Phase 1 summary in `ImplementationPhases.md` into concrete workstreams, implementation boundaries, and acceptance criteria for the first real code-bearing phase.

Phase 1 exists to define the shared contract surface that every model family and every later backend depends on.

## Purpose

Phase 1 must establish:

- the common public model interface,
- the shared parameter and state abstractions,
- the common event and observable datatypes,
- the central capability vocabulary,
- the parameter-domain boundary between core semantics and runtime/tooling config,
- and the initial snapshot/schema contract at the interface level.

Phase 1 should make later model families easy to build without committing to graph or numerical implementation details too early.

## Inputs From Phase 0

Phase 1 assumes the following Phase 0 outputs already exist and remain authoritative:

- package and test skeleton
- packaging/tooling bootstrap
- repo-local `.venv` workflow
- determinism conventions in [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
- implementation boundary decisions in [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)

Phase 1 must not silently contradict those documents.

## In Scope

- `GRCModel` interface and base protocol surface
- shared params abstractions
- shared state abstractions
- shared step-result abstraction
- shared event and observable datatypes
- capability naming and discovery contract
- parameter canonicalization and resolution boundary
- interface-level snapshot contract
- family stubs that prove the contracts are usable
- tests for the contract surface

## Out Of Scope

- weighted-graph implementation
- port-graph implementation
- graph mutation logic
- serializer implementation details
- model-family update equations
- curvature backends
- differential-summary kernels
- integration/runtime adapters
- machine-driver functionality

## Phase 1 Design Constraints

### 1. Family Neutrality

The common contracts must support:

- `GRCV2`
- `GRCV3`
- `GRC9`
- `GRC9V3`

without flattening their differences into one overloaded class.

### 2. Parameter Boundary Discipline

Core model params must contain only values that change the model semantics or numerical result.

Runtime, observer, tooling, renderer, and device-policy values must remain outside the core param objects.

### 3. Determinism First

The interfaces must be shaped so later implementations can satisfy:

- stable IDs,
- deterministic ordering,
- canonical params identity,
- canonical snapshot grouping,
- and reproducible save/load behavior.

### 4. No Premature Backend Coupling

Phase 1 must not hardwire the contracts to:

- one graph class,
- one storage layout,
- or one third-party dependency.

Graph/storage specifics belong to Phase 2.

## Expected Code Shape After Phase 1

The exact filenames may still evolve, but the intended Phase 1 shape is close to:

```text
src/pygrc/
  core/
    __init__.py
    interfaces.py
    params.py
    types.py
    events.py
    observables.py
    capabilities.py
    errors.py
  models/
    __init__.py
    grc_v2.py
    grc_v3.py
    grc_9.py
    grc_9_v3.py
```

Some of these files may start small. The important part is the boundary, not file volume.

## Workstreams

## 1. Core Interface Surface

### Tasks

- Define the base `GRCModel` contract.
- Define the minimum required methods for all families.
- Decide which methods are abstract requirements versus convenience helpers.
- Encode snapshot/load/reset/step capability at the interface level without tying them to one concrete backend.
- Make capability discovery a first-class part of the contract.

### Required Interface Shape

The common model surface should support at least:

- `from_config(...)`
- `from_state(...)`
- `get_state()`
- `set_state(...)`
- `step()`
- `run(...)`
- `reset()`
- `snapshot()`
- `save(...)`
- `load(...)`
- `get_params()`
- `list_capabilities()`
- `compute_observables()`

Additional helpers are allowed, but the required surface should stay minimal.

### Acceptance Criteria

- Every future family class can implement or inherit the same base model surface.
- The interface is clear enough that Phase 2 and later phases do not need to reinterpret what a model object is.
- No graph/storage assumptions leak into the model interface.

## 2. Parameter Architecture

### Tasks

- Define the base parameter abstraction for all families.
- Decide whether the common parameter base uses a frozen dataclass, immutable mapping wrapper, or equivalent immutable structure.
- Encode the parameter-domain boundary explicitly:
  - evolution parameters
  - constitutive/semantic mode parameters
  - numerical backend parameters that change results
  - excluded runtime/tooling parameters
- Define resolved-params access.
- Define the canonical params identity/hash boundary at the interface level.

### Required Decisions

- parameter objects are immutable or effectively immutable
- raw config vs resolved params are distinguishable
- canonicalization happens centrally, not ad hoc inside families
- capability/mode parameters such as `frame_mode`, `boundary_mode`, `curvature_backend`, and `edge_label_selection` are treated as real model semantics

### Acceptance Criteria

- The parameter structure supports all four model families without family-specific hacks in the base class.
- The model/runtime boundary is enforceable in code structure.
- Later serialization work has a clear place to obtain canonical params and params identity.

## 3. State And Step Result Contracts

### Tasks

- Define a shared state abstraction or typed state base.
- Define what all states must share at minimum.
- Define `StepResult` as the common return type for `step()`.
- Decide what belongs in the model object versus the step result versus the event log.
- Keep the base state family-neutral while still supporting later family-specific extensions.

### Minimum Shared State Surface

At minimum, the base state layer should have a place for:

- step index
- physical time
- budget target
- remainder
- params identity or resolved params reference
- observables if stored on state
- event log if stored on state
- RNG state if a family uses stochastic behavior

The common state base should not pretend that all families have the same topology or basin payloads.

### Step Result Expectations

The shared `StepResult` should be able to carry:

- updated step index
- updated time
- produced events
- observables snapshot
- optional status flags or bookkeeping fields

### Acceptance Criteria

- The base state/result contracts support later family-specific extension by composition or subclassing.
- No family-specific topology fields are forced into the common state base.
- The `step()` return shape is stable enough for tests and later tooling.

## 4. Event And Observable Datatypes

### Tasks

- Define common event datatypes or event base records.
- Decide the required shared event fields.
- Define the base observable contract.
- Decide whether observables are plain mappings, typed records, or both.
- Ensure the event structure can later support deterministic ordering from the Phase 0 conventions.

### Required Shared Event Fields

Every event record should have a shape that can represent at least:

- event kind/type
- model family or source context if needed
- step index
- deterministic payload

Exact family-specific payload schemas can be extended later.

### Acceptance Criteria

- Common events and observables can be used in tests before any family model is complete.
- Later model families can add richer events without replacing the base event concept.
- The event shape is compatible with deterministic replay and snapshot inclusion.

## 5. Capability Vocabulary

### Tasks

- Define the canonical capability names used by the reference implementation.
- Provide a single home for capability constants or typed identifiers.
- Distinguish:
  - always-on family properties
  - optional extensions
  - must-not-claim boundaries
- Define the runtime discovery contract for capabilities.

### Acceptance Criteria

- All four families can expose capabilities through one common mechanism.
- Capability discovery does not require callers to inspect internal classes or params manually.
- The common capability vocabulary stays aligned with the specs.

## 6. Snapshot Contract At The Interface Level

### Tasks

- Define the interface-level snapshot contract without implementing the serializer yet.
- Ensure the contract is compatible with the Phase 0 determinism conventions.
- Decide the base snapshot type shape returned by `snapshot()`.
- Define how `load_snapshot(...)` signals incompatibility.
- Define where family-specific snapshot extensions live.

### Constraints

- Phase 1 defines the shape and obligations.
- Phase 3 implements the deterministic serializer.
- The snapshot contract must already anticipate:
  - metadata group
  - topology group
  - optional basin attributes
  - optional edge labels
  - dynamics/observables/events/caches

### Acceptance Criteria

- Families can build on one snapshot contract without changing the method shape later.
- Snapshot incompatibility is treated as an explicit error, not undefined behavior.
- The interface aligns with the determinism conventions already written down.

## 7. Error Surface

### Tasks

- Define common exception types for interface-level failures.
- Provide explicit errors for:
  - invalid params
  - unsupported capability requests
  - incompatible snapshot loading
  - invalid state transitions at the contract boundary

### Acceptance Criteria

- Later phases can raise stable library-level exceptions instead of ad hoc `ValueError`/`RuntimeError` only.
- The error surface is small and intentional.

## 8. Family Stub Classes

### Tasks

- Add minimal model-family stubs:
  - `GRCV2`
  - `GRCV3`
  - `GRC9`
  - `GRC9V3`
- Make each stub inherit from or satisfy the common contracts.
- Do not implement family equations yet.
- Ensure each family can expose:
  - model family identifier
  - base capability set
  - params type binding

### Acceptance Criteria

- Imports of all four family classes succeed.
- Each family stub proves the shared contract is implementable.
- No family stub contains real simulation logic yet.

## 9. Contract Tests

### Tasks

- Add tests for the common interface surface.
- Add tests for params immutability/effective immutability.
- Add tests for capability discovery shape.
- Add tests for stub-family import and inheritance behavior.
- Add tests for snapshot contract shape at the interface level.

### Minimum Test Coverage

- import tests for core modules
- contract tests for base interfaces
- family-stub tests
- negative tests for explicit error cases where practical

### Acceptance Criteria

- The contract surface is executable and test-backed before graph/model logic begins.
- Future phases can refactor internals without changing the tested public contract unintentionally.

## Deliverables

Phase 1 should produce:

- shared core contract modules under `src/pygrc/core/`
- family stub modules under `src/pygrc/models/`
- contract-focused tests under `tests/core/` and `tests/models/`
- a clear code home for:
  - interfaces
  - params
  - types/state/result datatypes
  - events
  - observables
  - capabilities
  - errors

## Acceptance Criteria

Phase 1 is complete only if all of the following are true.

### A. Structural Acceptance

- The common contract modules exist and import cleanly.
- The family stub modules exist and import cleanly.
- Tests cover the contract surface at least at a smoke/shape level.

### B. Boundary Acceptance

- No graph implementation has leaked into Phase 1.
- No family equations or topology-update logic have leaked into Phase 1.
- Runtime/tooling parameters have not been pulled into the core param objects.

### C. Specification Alignment Acceptance

- Capability names and parameter modes remain aligned with the specs.
- Snapshot and error contracts do not contradict the specs or Phase 0 conventions.
- The family stubs preserve family distinctions rather than flattening them.

### D. Reproducibility Acceptance

- The contract surface is compatible with stable IDs and deterministic snapshots.
- Params canonicalization has one clear boundary.
- Snapshot/load incompatibility is explicit.

### E. Developer-Onboarding Acceptance

- A new contributor can identify where to add:
  - new params
  - new event types
  - new observables
  - new family-specific state extensions
- The common-contract layer is understandable without reading later graph/backend code.

## Suggested Follow-On Documents

Once Phase 1 execution begins, it will likely be useful to add:

- `Phase-1-ImplementationChecklist.md`
- `Phase-1-ContractMatrix.md`
- `Phase-1-OpenQuestions.md` only if real unresolved contract choices remain after implementation starts
