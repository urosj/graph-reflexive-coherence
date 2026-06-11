# Phase 0 Implementation Plan

This document is the detailed execution plan for **Phase 0: Repository Bootstrap**.

It turns the high-level phase plan into concrete implementation work, locked design decisions, and objective acceptance criteria.

Phase 0 exists to create a clean implementation boundary before any family logic is written.

## Purpose

Phase 0 must establish:

- the package and test layout under `src/` and `tests/`,
- the baseline implementation conventions for deterministic behavior,
- the initial project metadata and developer command surface,
- the first implementation-tracker documents under `implementation/`,
- and the locked early decisions that later phases must treat as fixed unless deliberately revised.

This phase does **not** implement model equations.

## In Scope

- repository and package skeleton
- test skeleton
- packaging/bootstrap metadata
- implementation-facing conventions
- locked reference decisions already implied by the specs
- validation commands for import, test discovery, and repository shape

## Out of Scope

- graph backend implementation
- `GRCModel` interfaces
- params/state/event classes
- serialization logic
- family model logic
- numerical kernels
- external adapters

## Locked Decisions Carried Into Implementation

These are no longer open design questions for Phase 0.

### Split / Expansion Distribution

- `GRCV2` default `split_distribution_mode = "equal"`
- `GRCV3` default `split_distribution_mode = "equal"`
- `GRC9` default `expansion_distribution_mode = "equal"`
- `GRC9V3` default `expansion_distribution_mode = "equal"`

Phase 0 should only encode these as conventions and future constructor/config defaults. It must not introduce heuristic asymmetry yet.

### Curvature Backend Rollout

- baseline default: `curvature_backend = "none"`
- first in-house implemented backend: `forman`
- later advanced backend: `ollivier`

Phase 0 must not introduce any required dependency on `networkx`, `ricci`, or other third-party graph libraries for core execution.

### Differential Reference Backend

The reference implementation path for `induced_local_frame`, gradient, and Hessian follows the canonical backend defined in `grc-v3-spec.md`.

Phase 0 must record this as the baseline implementation commitment so later phases do not invent competing defaults.

### Backend Policy

- authoritative execution backends are first-party and in-house
- third-party graph libraries may appear later only as adapters or interchange helpers
- visualization libraries are export/integration tools, not simulation substrate

## Expected Repository Shape After Phase 0

The exact files may evolve, but Phase 0 should leave the repo in a shape close to:

```text
src/
  pygrc/
    __init__.py
    core/
      __init__.py
    models/
      __init__.py
    integrations/
      __init__.py
    utils/
      __init__.py

tests/
  core/
  models/
  integrations/

implementation/
  ImplementationPhases.md
  Phase-0-ImplementationPlan.md
  Phase-0-ImplementationChecklist.md
```

Additional bootstrap files such as `pyproject.toml`, `README` updates, or minimal config files are allowed and expected.

## Workstreams

## 1. Package Bootstrap

### Tasks

- Create `src/pygrc/` and all first-level package directories:
  - `core/`
  - `models/`
  - `integrations/`
  - `utils/`
- Add minimal `__init__.py` files so the package imports cleanly.
- Ensure the package name and import root are stable and consistent with later phases.
- Decide whether package versioning is placeholder-only in Phase 0 or already sourced from package metadata.
- Keep module contents minimal; Phase 0 should not pre-implement later abstractions.

### Acceptance Criteria

- `import pygrc` succeeds in the local development environment.
- `pygrc`, `pygrc.core`, `pygrc.models`, `pygrc.integrations`, and `pygrc.utils` are all importable.
- No placeholder module creates false API commitments beyond package boundaries.

## 2. Test Bootstrap

### Tasks

- Create `tests/` tree with at least:
  - `tests/core/`
  - `tests/models/`
  - `tests/integrations/`
- Add a minimal smoke test that validates package import.
- Add any minimal test configuration needed for discovery.
- Decide the project-standard test runner command and record it.

### Acceptance Criteria

- Test discovery runs without import errors.
- An empty or near-empty suite passes cleanly.
- The chosen test command is documented in repo-local implementation notes or project metadata.

## 3. Packaging And Tooling Bootstrap

### Tasks

- Create or finalize `pyproject.toml` if not already present.
- Define minimal package metadata needed for editable local development.
- Record baseline developer commands for:
  - formatting
  - linting
  - type checking
  - tests
- Keep tooling lightweight; Phase 0 should avoid overcommitting to a large toolchain unless required.
- Make sure any tooling config does not encode model semantics or runtime-specific behavior.
- Define the minimum supported Python version for the implementation baseline.
- Decide the type-checking strategy for the repository.
- Create or verify baseline repository hygiene files:
  - `.gitignore`
  - `LICENSE` or an explicit license decision record

### Acceptance Criteria

- The package can be installed or used in editable local-development mode.
- The canonical local commands for formatting, linting, type checking, and testing are documented.
- The minimum supported Python version is recorded.
- Tooling configuration is isolated from model parameters and simulation semantics.

## 4. Determinism And Convention Seed Rules

### Tasks

- Define the project-local deterministic ordering convention for:
  - nodes
  - edges
  - ports
  - event logs
  - serialized field order aligned to spec groups
- Define the stable ID type/format for:
  - node IDs
  - edge IDs
  - port identifiers where applicable
- Define ID stability expectations:
  - stable IDs
  - no accidental reuse after deletion
  - reproducible ordering independent of Python object identity
- Define float-tolerance policy categories:
  - exact equality where required
  - bounded tolerance where numerically unavoidable
- Define snapshot naming/versioning convention for future serialization work.
- Define whether tombstoning is the default storage expectation for later graph backends.

### Acceptance Criteria

- A written convention exists for deterministic ordering and ID stability.
- The ID type/format is fixed strongly enough to avoid Phase 1 refactors.
- The conventions are specific enough that two implementers would produce compatible snapshots.
- No convention depends on non-deterministic dictionary or object traversal behavior.

## 5. Spec-Bound Early Decisions Recording

### Tasks

- Record the baseline split/expansion distribution defaults from the specs.
- Record the curvature backend rollout strategy from the specs.
- Record the reference differential backend commitment from the specs.
- Record the backend policy:
  - first-party execution backends first
  - adapters later
  - no `networkx` dependency in the core execution path
- Make sure these appear in implementation-facing docs so later phases do not reopen them implicitly.

### Acceptance Criteria

- A developer starting Phase 1 or Phase 2 can discover these decisions without rereading the full specs corpus.
- The recorded decisions match the current spec language.
- No Phase 0 doc contradicts `specs/` on these baseline choices.

## 6. Implementation Tracker Bootstrap

### Tasks

- Keep `ImplementationPhases.md` as the top-level roadmap.
- Keep `Phase-0-ImplementationPlan.md` as the detailed Phase 0 plan.
- Create `Phase-0-ImplementationChecklist.md` as the execution tracker with iteration checklists.
- Use the execution checklist itself as the decision record:
  - decisions are recorded alongside the relevant iteration items,
  - and iteration summaries capture the rationale and outcome.
- Keep planning artifacts in `implementation/`, not in source comments.

### Acceptance Criteria

- `implementation/` clearly separates roadmap, plan, and execution/decision tracking responsibilities.
- Later phases have an obvious location for design notes and reversals.
- Planning artifacts do not leak into source code as long explanatory comments.

## 7. Validation Pass

### Tasks

- Run an import smoke test.
- Run test discovery or the initial smoke suite.
- Verify the package/test tree matches the intended boundaries.
- Verify that no accidental runtime dependency on third-party graph tooling has been introduced into `src/pygrc/core/` or `src/pygrc/models/`.
- Verify that any allowed third-party graph tooling usage remains isolated to `tests/` or `integrations/`.
- Verify that repo docs point to `implementation/` for execution planning.

### Acceptance Criteria

- Imports succeed.
- Tests pass.
- The repository tree matches the intended bootstrap boundary.
- Phase 0 finishes without implementing Phase 1 abstractions early.

## Deliverables Checklist

- [ ] `src/pygrc/__init__.py` exists
- [ ] `src/pygrc/core/__init__.py` exists
- [ ] `src/pygrc/models/__init__.py` exists
- [ ] `src/pygrc/integrations/__init__.py` exists
- [ ] `src/pygrc/utils/__init__.py` exists
- [ ] `tests/` exists with `core/`, `models/`, and `integrations/`
- [ ] minimal smoke import test exists
- [ ] package metadata/bootstrap config exists and is usable
- [ ] minimum supported Python version is documented
- [ ] formatting/lint/type-check/test commands are documented
- [ ] `.gitignore` exists or its handling is explicitly recorded
- [ ] license handling is explicit
- [ ] deterministic ordering convention is written down
- [ ] ID stability convention is written down
- [ ] ID type/format convention is written down
- [ ] float tolerance policy is written down
- [ ] future snapshot naming/versioning convention is written down
- [ ] split/expansion default distribution decisions are recorded
- [ ] curvature backend rollout strategy is recorded
- [ ] reference differential backend commitment is recorded
- [ ] backend policy is recorded
- [ ] `implementation/` tracker structure is usable for later phases

## Thorough Acceptance Criteria

Phase 0 is complete only if all of the following are true.

### A. Structural Acceptance

- The `src/` package structure exists and imports cleanly.
- The `tests/` structure exists and test discovery succeeds.
- The repo contains a clear home for ongoing implementation planning under `implementation/`.

### B. Boundary Acceptance

- No Phase 0 artifact introduces family-specific model logic.
- No Phase 0 artifact introduces graph algorithm code prematurely.
- Core package bootstrap does not depend on `networkx`, `pyvis`, or other graph/visualization libraries for import or smoke tests.

### C. Specification Alignment Acceptance

- The Phase 0 docs reflect the spec-defined defaults for split/expansion distribution.
- The Phase 0 docs reflect the spec-defined curvature backend strategy.
- The Phase 0 docs reflect the spec-defined first-party backend policy.
- The Phase 0 docs reflect the spec-defined canonical differential backend commitment.

### D. Reproducibility Acceptance

- Deterministic ordering and ID stability conventions are written before storage code begins.
- ID type/format is fixed before common state and graph abstractions are implemented.
- Float tolerance categories are defined before numerical verification code begins.
- Snapshot versioning expectations are written before serialization code begins.

### E. Developer-Onboarding Acceptance

- A new contributor can determine:
  - where code goes,
  - where tests go,
  - where implementation decisions are recorded,
  - which early design choices are fixed,
  - and which developer commands to run first.

### F. Phase Boundary Acceptance

- Phase 0 ends with a clean bootstrap, not an accidental partial Phase 1 implementation.
- Any unresolved item is explicitly recorded as deferred rather than silently omitted.

## Evidence To Collect Before Closing Phase 0

- repository tree snapshot or equivalent review
- successful import smoke command
- successful initial test command
- note confirming no third-party graph dependency has entered the core bootstrap path
- note confirming any permitted third-party graph dependency usage is isolated to `tests/` or `integrations/`
- checklist marked complete or annotated with explicit deferrals

## Suggested Closeout Note

When Phase 0 is complete, record:

1. what was created,
2. what conventions were locked,
3. what was intentionally deferred to Phase 1,
4. and whether any spec clarification is still needed before implementation continues.
