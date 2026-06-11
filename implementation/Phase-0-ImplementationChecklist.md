# Phase 0 Implementation Checklist

This document tracks the execution of **Phase 0: Repository Bootstrap**.

It is intentionally separate from [`Phase-0-ImplementationPlan.md`](./Phase-0-ImplementationPlan.md):

- the plan defines scope, workstreams, locked decisions, and acceptance criteria,
- this checklist records how the work is actually executed iteration by iteration.

Each iteration should contain:

- a bounded implementation slice,
- concrete checkboxes that can be ticked off during execution,
- implementation notes added alongside or below the checks,
- and a short summary recorded when the iteration closes.

## Usage Rules

- Keep iterations small enough to complete and verify cleanly.
- Update checkboxes during implementation, not after the fact.
- Add implementation details only where they help future work.
- If an item is deferred, leave it unchecked and add a short reason.
- If a plan change is required, update the plan document first or in the same change.

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

## Iteration 0. Bootstrap Planning Setup

### Goal

Establish the planning documents and execution-tracking structure for Phase 0 before code changes begin.

### Checks

- [x] Rename the detailed Phase 0 document from checklist form to plan form.
- [x] Update `ImplementationPhases.md` to link both the Phase 0 plan and the execution checklist.
- [x] Create `Phase-0-ImplementationChecklist.md` with an iteration-based execution structure.
- [x] Decide that `DecisionLog.md` is not needed; implementation decisions live in iteration notes and summaries.

### Implementation Notes

- `Phase-0-ImplementationPlan.md` is the normative Phase 0 planning document.
- This checklist is the working execution log for implementation iterations.
- We are not creating a separate `DecisionLog.md`.
- Decision rationale belongs next to the relevant checklist items and in each iteration summary.

### Verification

- [x] Both Phase 0 documents exist under `implementation/`.
- [x] `ImplementationPhases.md` points to the correct files.
- [x] The plan/checklist split is clear from the document titles and opening sections.

### Summary

Planning and execution tracking are now separated. Phase 0 can proceed with bounded implementation iterations without overloading the plan document, and decisions will be recorded directly in this checklist rather than in a separate log.

## Iteration 1. Package Skeleton

### Goal

Create the initial `src/pygrc/` package structure without introducing Phase 1 abstractions early.

### Checks

- [x] Create `src/pygrc/`
- [x] Create `src/pygrc/__init__.py`
- [x] Create `src/pygrc/core/`
- [x] Create `src/pygrc/core/__init__.py`
- [x] Create `src/pygrc/models/`
- [x] Create `src/pygrc/models/__init__.py`
- [x] Create `src/pygrc/integrations/`
- [x] Create `src/pygrc/integrations/__init__.py`
- [x] Create `src/pygrc/utils/`
- [x] Create `src/pygrc/utils/__init__.py`
- [x] Verify that package files do not predeclare unstable public APIs beyond package boundaries
- [x] Record any package-root versioning convention chosen for Phase 0

### Implementation Notes

- Keep `__init__.py` files minimal.
- Avoid placeholder classes like `GRCModel` or `GRCParams` in this iteration; those belong to Phase 1.
- If version metadata is not settled yet, use a neutral placeholder strategy and record it explicitly.
- Chosen Phase 0 convention: the package root exports no public symbols and does not define `__version__` yet.
- Package versioning will be sourced from packaging metadata in Iteration 3 rather than from handwritten module constants.
- Import verification for this iteration uses `PYTHONPATH=src` because editable-install packaging is not part of Iteration 1.

### Verification

- [x] `import pygrc` succeeds
- [x] `import pygrc.core`, `pygrc.models`, `pygrc.integrations`, and `pygrc.utils` succeeds
- [x] Package tree matches the intended Phase 0 boundary

### Summary

Created the minimal `src/pygrc/` package skeleton with import-safe subpackages only. Import smoke validation passed via `PYTHONPATH=src`, and public API shape plus package version exposure remain intentionally deferred to later iterations.

## Iteration 2. Test Skeleton

### Goal

Create the minimal `tests/` structure and the first smoke-level validation path.

### Checks

- [x] Create `tests/`
- [x] Create `tests/core/`
- [x] Create `tests/models/`
- [x] Create `tests/integrations/`
- [x] Add a smoke test for package import
- [x] Add any minimal test configuration needed for discovery
- [x] Decide and record the standard Phase 0 test command
- [x] Confirm the test tree does not assume family-specific behavior yet

### Implementation Notes

- The smoke test should validate import/bootstrap only.
- Do not add behavioral tests for models, graph logic, or serialization in Phase 0.
- If `pytest` is used, keep the initial configuration minimal and repo-local.
- Chosen Phase 0 test command: `PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'`.
- No extra test runner dependency is introduced in this iteration; built-in `unittest` is sufficient for bootstrap validation.
- The import smoke test injects `src/` into `sys.path` directly so it remains usable before packaging metadata exists.
- Minimal discovery configuration for the nested test tree is provided via `tests/__init__.py` and per-subtree `__init__.py` files.

### Verification

- [x] Test discovery runs without import errors
- [x] The smoke suite passes
- [x] The chosen test command is documented in a stable location

### Summary

Created the `tests/` skeleton and a dependency-light import smoke test. The Phase 0 `unittest` discovery command now passes cleanly against the nested test layout.

## Iteration 3. Packaging And Developer Commands

### Goal

Create the minimal packaging/bootstrap metadata and document the baseline developer commands.

### Checks

- [x] Create or finalize `pyproject.toml`
- [x] Ensure editable local development is supported
- [x] Define the minimum supported Python version
- [x] Record the canonical formatting command
- [x] Record the canonical lint command
- [x] Decide and record the type-checking strategy
- [x] Record the canonical test command
- [x] Keep tooling configuration separate from model/runtime semantics
- [x] Create or update `.gitignore`
- [x] Decide on the license file path or record an explicit license decision
- [x] Check whether additional bootstrap files are needed:
  - [x] `README` update
  - [x] tool config files
  - [x] package metadata placeholders

### Implementation Notes

- Prefer a lightweight initial toolchain.
- Avoid encoding any model semantics in tooling config, environment defaults, or command wrappers.
- Type checking should be treated as part of engineering rigor, not as an optional afterthought.
- If a tool is intentionally deferred, record that rather than leaving the absence ambiguous.
- Minimum supported Python version for the implementation baseline: `3.11+`.
- Chosen formatting command: `ruff format .`
- Chosen lint command: `ruff check .`
- Chosen type-check command: `mypy src tests`
- Chosen Phase 0 test command in the default local environment: `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
- Direct source-tree fallback remains available as: `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
- Repo-local default environment: `.venv/`
- Repo-local `.venv` was provisioned with `setuptools` and `wheel`.
- Repo-local `.venv` usage was verified with:
  - `.venv/bin/python -m pip install -e . --no-deps --no-build-isolation`
  - `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
- Direct import fallback was also verified with:
  - `PYTHONPATH=src .venv/bin/python -c "import pygrc, pygrc.core, pygrc.models, pygrc.integrations, pygrc.utils"`
- The `setuptools` floor was relaxed to `>=68` to match the local bootstrap environment while remaining sufficient for the Phase 0 editable build path.
- The repo-local `.venv` created by Python 3.12 did not include `setuptools` by default, so Phase 0 now explicitly provisions it as part of the local environment setup.
- Root `LICENSE` already exists and is GPLv2; Phase 0 records that file as the authoritative license path.
- `README.md` is intentionally minimal and states that the repository is still in the implementation-planning stage.

### Verification

- [x] Local editable install path is defined and usable
- [x] Minimum Python version is written down
- [x] Formatting/lint/type-check/test commands are written down
- [x] Tooling config does not create hidden simulation defaults
- [x] `.gitignore` and license handling are not left ambiguous

### Summary

Created the Phase 0 packaging/tooling baseline: `pyproject.toml`, `README.md`, and `.gitignore`. The default local environment is now the repo-local `.venv`, provisioned with `setuptools` and `wheel`, and verified for editable-install and test execution.

## Iteration 4. Determinism Conventions

### Goal

Write down the deterministic conventions that later storage and serialization work must follow.

### Checks

- [x] Define deterministic node ordering convention
- [x] Define deterministic edge ordering convention
- [x] Define deterministic port ordering convention
- [x] Define deterministic event-log ordering convention
- [x] Define serialized field ordering convention aligned to spec groups:
  - [x] metadata
  - [x] topology
  - [x] basin attributes
  - [x] edge labels
  - [x] dynamics
- [x] Define ID type/format for node IDs
- [x] Define ID type/format for edge IDs
- [x] Define ID type/format for port identifiers where applicable
- [x] Define stable ID policy
- [x] Define no-reuse or tombstone expectation for deleted IDs
- [x] Define float-tolerance categories:
  - [x] exact equality cases
  - [x] bounded tolerance cases
- [x] Define snapshot naming/versioning convention
- [x] Decide whether tombstoning is the default storage expectation for later graph backends

### Implementation Notes

- These conventions should be documented before graph/storage code begins.
- The goal is to prevent two valid implementations from producing incompatible snapshots for incidental reasons.
- Use wording that is precise enough to guide both weighted-graph and port-graph backends.
- The serialization-order rule should map directly onto spec-defined attribute groups rather than relying on ad hoc field ordering.
- The conventions are recorded in [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md).
- Chosen ID format:
  - node IDs: non-negative `int`, starting at `0`
  - edge IDs: non-negative `int`, starting at `0`
  - port IDs: integer slot IDs `0..8`, using zero-based row-major mapping
- Chosen storage expectation: tombstoned slots with monotone `next_*_id` counters and no ID reuse.
- Chosen snapshot grouping order:
  - `metadata`
  - `topology`
  - `basin_attributes`
  - `edge_labels`
  - `dynamics`
  - `observables`
  - `events`
  - `caches`
- Chosen default numeric verification tolerances:
  - `abs_tol = 1e-12`
  - `rel_tol = 1e-9`

### Verification

- [x] Conventions are written clearly enough for independent implementation
- [x] ID type/format choices are explicit enough to prevent Phase 1 refactors
- [x] No convention relies on Python object identity or nondeterministic traversal
- [x] Conventions align with the common-interface determinism requirements

### Summary

Recorded the Phase 0 determinism contract in a dedicated implementation document. Later graph, state, and snapshot work now has fixed defaults for ID types, ordering, tombstoning, snapshot groups, and numeric comparison policy.

## Iteration 5. Spec-Bound Decisions And Boundaries

### Goal

Record the already-decided implementation boundaries so later phases do not reopen them implicitly.

### Checks

- [x] Record `split_distribution_mode = "equal"` as the Phase 0 baseline for `GRCV2`
- [x] Record `split_distribution_mode = "equal"` as the Phase 0 baseline for `GRCV3`
- [x] Record `expansion_distribution_mode = "equal"` as the Phase 0 baseline for `GRC9`
- [x] Record `expansion_distribution_mode = "equal"` as the Phase 0 baseline for `GRC9V3`
- [x] Record curvature backend rollout:
  - [x] default `none`
  - [x] first in-house backend `forman`
  - [x] later backend `ollivier`
- [x] Record reference differential backend commitment for:
  - [x] `induced_local_frame`
  - [x] gradient
  - [x] Hessian
- [x] Record backend policy:
  - [x] first-party execution backends are authoritative
  - [x] `networkx` is adapter/interchange only
  - [x] `pyvis` is visualization/export only
  - [x] no third-party graph dependency in the core execution path
- [x] Record that decisions are tracked in checklist notes and iteration summaries rather than a separate `DecisionLog.md`

### Implementation Notes

- This iteration is documentation-heavy by design.
- The main purpose is to stop later implementation drift.
- If any recorded decision conflicts with the specs, the specs must be corrected first rather than overridden here.
- This checklist is the authoritative implementation decision trail for Phase 0.
- The consolidated boundary document is [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md).
- Recorded family baselines:
  - `GRCV2`: `split_distribution_mode = "equal"`
  - `GRCV3`: `split_distribution_mode = "equal"`
  - `GRC9`: `expansion_distribution_mode = "equal"`
  - `GRC9V3`: `expansion_distribution_mode = "equal"`
- Recorded curvature rollout:
  - baseline `none`
  - first in-house backend `forman`
  - later backend `ollivier`
- Recorded differential backend commitment:
  - spec-defined canonical `induced_local_frame`
  - spec-defined canonical gradient backend
  - spec-defined canonical Hessian backend
- Recorded backend policy:
  - first-party execution substrate in core
  - `networkx` only later as adapter/interchange/analysis helper
  - `pyvis` only later as visualization/export helper
  - no third-party graph dependency in `src/pygrc/core/` or `src/pygrc/models/`
- Recorded decision-tracking policy:
  - no separate `DecisionLog.md`
  - rationale lives in checklist notes and iteration summaries

### Verification

- [x] A developer can discover the early fixed decisions without rereading the full specs corpus
- [x] The recorded decisions match current spec language
- [x] No implementation-planning document contradicts `specs/`

### Summary

Recorded the Phase 0 family baselines and implementation boundaries in a single document. Later phases now have one implementation-facing reference for distribution defaults, curvature rollout, differential backend commitment, adapter boundaries, and decision-tracking policy.

## Iteration 6. Validation And Phase Closeout

### Goal

Perform the Phase 0 validation pass and record closure status against the plan acceptance criteria.

### Checks

- [x] Run import smoke validation
- [x] Run test discovery or smoke-suite validation
- [x] Verify the repo tree matches the intended Phase 0 boundary
- [x] Verify no accidental dependency on third-party graph tooling has entered `src/pygrc/core/` or `src/pygrc/models/`
- [x] Verify any third-party graph tooling usage is isolated to `tests/` or `integrations/`
- [x] Verify the planning docs under `implementation/` are coherent and cross-linked
- [x] Verify `Phase-0-BoundaryDecisions.md` and `Phase-0-DeterminismConventions.md` do not contradict the `specs/` corpus
- [x] Review the Phase 0 plan acceptance criteria against the actual repo state
- [x] Mark all completed checklist items
- [x] Add deferral notes for any remaining unchecked items
- [x] Write a Phase 0 closeout summary:
  - [x] what was created
  - [x] what conventions were locked
  - [x] what was deferred to Phase 1
  - [x] whether any spec clarification is still needed

### Implementation Notes

- Phase 0 should close cleanly before Phase 1 begins.
- If Phase 0 uncovers unresolved design ambiguity, record it explicitly rather than carrying silent uncertainty into the common-contract work.
- Validation commands executed:
  - `.venv/bin/python -c "import pygrc, pygrc.core, pygrc.models, pygrc.integrations, pygrc.utils; print('imports-ok')"`
  - `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
- Dependency-boundary review:
  - no `networkx` or `pyvis` usage exists in `src/pygrc/core/` or `src/pygrc/models/`
  - existing mentions of `networkx` and `pyvis` are confined to planning/spec text about future adapter boundaries
- Spec-alignment review:
  - `Phase-0-BoundaryDecisions.md` was checked against the current `specs/` corpus
  - `Phase-0-DeterminismConventions.md` was checked against the current `specs/` corpus
  - no contradictions were identified at Phase 0 closeout
- Cross-link review:
  - `ImplementationPhases.md`, `Phase-0-ImplementationPlan.md`, `Phase-0-ImplementationChecklist.md`, `Phase-0-DeterminismConventions.md`, and `Phase-0-BoundaryDecisions.md` are coherent and linked with repo-relative paths
- Deferral note:
  - the only remaining unchecked boxes in this file are the reusable template placeholders near the top of the document
  - no operational Phase 0 tasks remain open

### Verification

- [x] Structural acceptance criteria are satisfied
- [x] Boundary acceptance criteria are satisfied
- [x] Specification alignment acceptance criteria are satisfied
- [x] Reproducibility acceptance criteria are satisfied
- [x] Developer-onboarding acceptance criteria are satisfied
- [x] Phase-boundary acceptance criteria are satisfied

### Summary

Phase 0 is complete.

Created:

- the `src/pygrc/` package skeleton
- the `tests/` skeleton with smoke import coverage
- the packaging/bootstrap baseline (`pyproject.toml`, `.gitignore`, `README.md`)
- the repo-local `.venv` default workflow
- the dedicated implementation docs for Phase 0 plan, checklist, determinism conventions, and boundary decisions

Locked conventions:

- repo-local `.venv` as the default local environment
- stable integer IDs with no reuse and tombstoned storage expectation
- canonical snapshot grouping/order and numeric verification tolerances
- equal split/expansion baselines for the family defaults
- curvature rollout `none -> forman -> ollivier`
- first-party core backends with third-party graph libraries deferred to adapters

Deferred to Phase 1 and later:

- common contracts (`GRCModel`, params, state, events)
- graph/storage implementations
- serialization machinery
- model-family logic
- integration/driver/runtime layers beyond planning

Spec clarification needed before Phase 1:

- none identified at Phase 0 closeout.
