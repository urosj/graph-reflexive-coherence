# Phase L1 Implementation Checklist

This document tracks the execution of **Phase L1: Landscape To `GRCV2`
Realization**.

It is intentionally separate from
[`Phase-L1-ImplementationPlan.md`](./Phase-L1-ImplementationPlan.md):

- the plan defines scope, boundaries, workstreams, and acceptance criteria,
- this checklist records how the Phase L1 work is executed iteration by
  iteration.

Each iteration should contain:

- a bounded implementation slice,
- concrete checkboxes that can be ticked off during execution,
- implementation notes recorded alongside the work,
- verification steps tied to the iteration output,
- and a short summary when the iteration closes.

## Usage Rules

- Keep projector-policy decisions close to the iteration that introduces them.
- If realization pressure reveals a seed-meaning problem, update the relevant
  Phase L or schema document explicitly instead of patching around it in code.
- Keep Phase L1 aligned with:
  - [`Phase-L-ProjectorBoundary.md`](./Phase-L-ProjectorBoundary.md)
  - [`LandscapeToGRCPlan.md`](./LandscapeToGRCPlan.md)
  - [`PDE-ParameterFamilyBridge.md`](./PDE-ParameterFamilyBridge.md)
  - [`Phase-4-DiscretizationDefense.md`](./Phase-4-DiscretizationDefense.md)
  - [`Phase-4-Retrospective.md`](./Phase-4-Retrospective.md)

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

Create the Phase L1 execution checklist and align it with the new realization
phase plan.

### Checks

- [x] Create `Phase-L1-ImplementationChecklist.md`
- [x] Create `Phase-L1-ImplementationPlan.md`
- [x] Link the new phase from `ImplementationPhases.md`
- [x] Record the Phase L1 follow-on explicitly in the Phase L documents

### Implementation Notes

- Phase L1 exists because the project can already:
  - translate PDE landscapes into normalized seeds,
  - and run standalone `GRCV2`,
  but cannot yet run canonical seeds end to end through `GRCV2`.
- The first acceptance targets are:
  - `cell-1`
  - `cell-4`
- The first bridge is intentionally family-specific:
  - `LandscapeSeed -> GRCV2`
  - not a generalized cross-family projector protocol

### Verification

- [x] The plan/checklist pair exists under `implementation/`
- [x] `ImplementationPhases.md` lists Phase L1 explicitly
- [x] Phase L no longer leaves the next executable bridge only implicit

### Summary

Phase L1 now exists as the explicit follow-on phase for turning normalized
landscape seeds into executable `GRCV2` runs.

## Iteration 1. Projector Module Boundary

### Goal

Define and implement the family-local module boundary for seed-driven `GRCV2`
construction.

### Checks

- [x] Decide where the projector module lives
- [x] Define the first public constructor/projection entry points
- [x] Keep neutral seed meaning out of family-local code changes
- [x] Add import-smoke coverage for the new public surface

### Implementation Notes

- The preferred direction is to keep the projector adjacent to `GRCV2`, likely
  under `src/pygrc/models/`, so the neutral `landscapes/` package remains free
  of family semantics.
- This iteration should answer whether projection returns:
  - state only,
  - model only,
  - or both via separate entry points.
- Chosen module boundary:
  - `src/pygrc/models/grc_v2_landscape.py`
- Chosen public surface:
  - `prepare_grcv2_landscape_projection(...)`
  - `project_landscape_seed_to_grcv2_state(...)`
  - `build_grcv2_from_landscape_seed(...)`
- Chosen API shape:
  - one preparation function that normalizes `LandscapeSeed | path` plus
    `GRCParams | config mapping` into a family-local
    `GRCV2LandscapeProjectionRequest`
  - separate projection and model-construction entry points on top of that
- Iteration 1 deliberately stops before primitive realization logic:
  - the projector/build functions exist,
  - they reuse the existing seed and `GRCV2` parameter validation boundaries,
  - and they raise `NotImplementedError` until Iteration 2 defines the
    primitive-to-topology policy
- Neutral seed meaning stayed out of family-local code:
  - no changes were made under `src/pygrc/landscapes/`
  - the new family-local boundary lives only under `src/pygrc/models/`
- Added boundary smoke coverage in:
  - `tests/models/test_grc_v2_landscape_import.py`

### Verification

- [x] The repo has one obvious import path for seed-driven `GRCV2` construction
- [x] No family-specific projector code was added under `src/pygrc/landscapes/`

### Summary

Implemented the Phase L1 family-local projector boundary. The repo now exposes
one explicit `LandscapeSeed -> GRCV2` module under `src/pygrc/models/`, with a
validated request-preparation surface and separate projection/build entry
points. Realization logic remains intentionally deferred to Iteration 2, but
the import path and family-local boundary are now fixed and test-visible.

## Iteration 2. Primitive Realization Policy

### Goal

Lock the baseline mapping from neutral seed primitives into initial weighted
graph structure.

### Checks

- [x] Define basin realization rules
- [x] Define plateau realization rules
- [x] Define ridge realization rules
- [x] Define valley realization rules
- [x] Define junction/saddle realization rules
- [x] Record deterministic tie-breaking and ambiguity rejection rules

### Implementation Notes

- The main deliverable is a reviewable realization policy, not premature
  optimization.
- Any unsupported structure should fail explicitly rather than being silently
  collapsed into generic adjacency.
- Chosen baseline realization surface:
  - `realize_grcv2_landscape_blueprint(...)`
  - plus immutable blueprint dataclasses for node- and edge-carrying primitives
- Chosen baseline `GRCV2` projection policy:
  - basin -> one node blueprint
  - plateau -> one node blueprint
  - junction/saddle -> one routing node blueprint
  - valley -> one edge blueprint between node-carrying primitives
  - ridge -> one support edge when it resolves to explicit adjacent or
    parent/host-supported node carriers
  - ridge -> explicit metadata-only boundary marker only for root-owned
    `ridge_kind="boundary"` cases with no realizable support target
- Chosen deterministic ordering rule:
  - preserve normalized seed primitive order
  - realize all carriers in one forward pass over the seed
  - no projector-local sorting is introduced beyond frozen metadata-key ordering
- Chosen ambiguity / rejection rules:
  - valley endpoints must be node-carrying primitives
  - ridge `owner_id` and `adjacent_ids` must reference node-carrying primitives
  - unresolved non-boundary ridges raise `InvalidLandscapeSeedError`
  - ridge realizations must not produce duplicate edge identities
  - basin `boundary_ids` must reference ridge primitives
  - plateau `hosted_primitive_ids` must reference node-carrying primitives
  - junction `host_id` and `branch_target_ids` must reference node-carrying primitives
  - hostless junctions are allowed only when they are not truly floating
  - baseline `GRCV2` requires hostless junctions to have either
    `chart_center_hint` or at least one incident valley
  - duplicate primitive ids are rejected inside the projector path even when
    `validate_seed=False`
  - unsupported uses raise `InvalidLandscapeSeedError`
- Implemented this policy in:
  - `src/pygrc/models/grc_v2_landscape.py`
- Added direct blueprint-policy tests in:
  - `tests/models/test_grc_v2_landscape_blueprint.py`
- Updated the Iteration 1 smoke test so the new blueprint surface is visible at
  the public models-package boundary.

### Verification

- [x] Each supported primitive type has an explicit baseline realization rule
- [x] Ambiguous or unsupported projector cases are rejected explicitly

### Summary

Locked the baseline primitive-to-topology policy for the first `GRCV2`
projector. The implementation now materializes an explicit immutable blueprint
where basin/plateau/junction primitives become nodes, valleys become edges, and
ridges either become support edges or explicit metadata-only root-boundary
markers. Invalid carrier references, duplicate identities, and unsupported
ridge realizations fail explicitly, and the policy is now covered directly by
tests before state construction begins.

## Iteration 3. Seed-To-State Initialization

### Goal

Project realized topology and seed meaning into a valid initial `GRCV2State`.

### Checks

- [x] Define coherence-prior to node-mass initialization
- [x] Define initial edge conductance initialization
- [x] Define budget target and initial time/step initialization
- [x] Decide how transport intent biases initialization
- [x] Construct valid `GRCV2State` objects from projected seeds

### Implementation Notes

- This iteration should keep seed meaning separate from `GRCV2` runtime
  semantics:
  transport intent is not pre-solved flux, and chart hints are not ontological
  coordinates.
- If `budget_B` is present, the normalization policy must be explicit and
  reproducible.
- Chosen node-mass policy:
  - every node-carrying primitive must provide `coherence_prior`
  - initial node masses are normalized to:
    - `budget_b` when present
    - otherwise the sum of node priors
- Chosen edge-weight policy:
  - valley edge weights come from coherence prior plus width attenuation
  - ridge support edges use interior/exterior hints plus thickness attenuation
- Chosen transport-intent policy:
  - intent does not set initial flux
  - when `carrier_id` names a realized edge, it multiplies that edge's initial
    weight deterministically using magnitude and priority hints
  - non-carrier intent remains recorded as metadata only
- Implemented `project_landscape_seed_to_grcv2_state(...)` as a real state
  constructor on top of the blueprint layer.
- Projection now stores explicit initialization metadata in
  `state.cached_quantities` so the realized seed/runtime bridge is inspectable.

### Verification

- [x] Projected state passes normal `GRCV2` validation
- [x] Initial budget semantics are explicit and deterministic

### Summary

Implemented the seed-to-state initialization policy. `LandscapeSeed` inputs now
produce valid initial `GRCV2State` objects with explicit node-mass
normalization, deterministic edge-weight initialization, budget targeting,
transport-intent weight bias without pre-solved flux, and projection metadata
recorded on state.

## Iteration 4. PDE-Informed Parameter Families

### Goal

Introduce the first executable parameter-family surface for seed-driven `GRCV2`
runs.

### Checks

- [x] Decide the first public family-selection surface
- [x] Implement named presets or a regime-axis resolver
- [x] Support explicit param overrides on top of family selection
- [x] Document the mapping from PDE-facing regime language into resolved
  `GRCV2` params

### Implementation Notes

- The mapping should reuse the cautions from
  [`PDE-ParameterFamilyBridge.md`](./PDE-ParameterFamilyBridge.md):
  regime transfer is allowed, direct coefficient identity is not assumed.
- This iteration should produce executable families, not exhaustive search.
- Chosen public surface:
  - `list_grcv2_landscape_param_families()`
  - `get_grcv2_landscape_param_family(name)`
  - `resolve_grcv2_landscape_params(...)`
- Implemented the first preset library:
  - `quiet_conservative`
  - `balanced_baseline`
  - `hot_exploratory`
  - `precursor_sensitive`
  - `commitment_dominant`
  - `holdout_counterexample_locked`
- Chosen parameter mapping style:
  - latent PDE-facing axes resolve deterministically into the `GRCV2` parameter
    surface
  - seed constitutive profile supplies `dt`, `lambda_c`, `xi_c`, `zeta_c`,
    `kappa_c`
  - seed potential is projected into the current `GRCV2`
    `site_potential_selection` surface
  - explicit overrides deep-merge on top of the family-derived config before
    `GRCV2` validation runs
- The current seed potential mapping uses a documented quadratic surrogate for
  `double_well`, with the source potential retained under
  `numerical_backend.seed_potential_projection`.

### Verification

- [x] A caller can choose a PDE-informed `GRCV2` regime without hand-writing the
  full param dict
- [x] Resolved family params pass ordinary `GRCV2` validation

### Summary

Implemented the first executable PDE-informed family surface for seed-driven
`GRCV2`. Named families now resolve into valid `GRCV2` params through a
deterministic latent-axis mapping, while seed constitutive coefficients remain
the constitutive base and explicit overrides stay supported.

## Iteration 5. Construction And Runner Surface

### Goal

Create the executable path from seed selection to multi-step `GRCV2` run.

### Checks

- [x] Implement seed-to-model construction helper
- [x] Implement multi-step runner helper
- [x] Return inspectable observables/event trajectory data
- [x] Support explicit `N` and explicit RNG seed inputs

### Implementation Notes

- The runner should be small enough to reuse in smokes and examples.
- It should not become a general integration framework or visualization layer.
- Added:
  - `build_grcv2_from_landscape_family(...)`
  - `run_grcv2_landscape_seed(...)`
  - `GRCV2LandscapeRunResult`
- Chosen runner result shape:
  - validated request
  - realized blueprint
  - live model
  - initial observables
  - per-step `StepResult` list
  - final observables
- The runner remains intentionally small:
  - no visualization hooks
  - no host integration
  - just the executable seed/family/N-step path

### Verification

- [x] A caller can go from seed input to `N` executable steps through one clear
  path
- [x] The trajectory result is inspectable and stable enough for tests

### Summary

Implemented the executable construction and runner surface. A caller can now
resolve a family, build a seed-driven `GRCV2`, and execute `N` steps through a
single narrow API without introducing a new integration layer.

## Iteration 6. Representative End-To-End Coverage

### Goal

Make the canonical `cell-1` and `cell-4` seeds executable through the new path
and verify meaningful runtime evolution.

### Checks

- [x] Add `cell-1` end-to-end tests
- [x] Add `cell-4` end-to-end tests
- [x] Check construction, stepping, and trajectory observables
- [x] Add at least one smoke path that verifies actual evolution, not just
  successful construction

### Implementation Notes

- This iteration should create conditions under which meaningful stepping really
  happens.
- The acceptance target is not a superficial runner call; it is observable model
  evolution with deterministic replay.
- End-to-end runtime tests now cover both:
  - `cell-1`
  - `cell-4`
- The projector was adjusted so ridge primitives can synthesize support edges to
  adjacent or parent/host node carriers where the seed structure justifies it.
  This keeps representative seeds executable rather than trivially disconnected.
- Root-owned outer boundary ridges with no realizable support target now remain
  explicit metadata-only markers, while unresolved non-boundary ridges are
  rejected instead of degrading silently.
- `cell-4` trajectory checks now assert real runtime evolution through changing
  observables rather than only successful construction.

### Verification

- [x] `cell-1` runs for `N` steps successfully
- [x] `cell-4` runs for `N` steps successfully
- [x] Smoke assertions inspect real runtime changes

### Summary

Representative seed coverage is now real. `cell-1` and `cell-4` both project
into executable `GRCV2` models and step successfully, and the `cell-4` checks
inspect actual runtime evolution rather than only construction success.

## Iteration 7. Determinism And Persistence

### Goal

Verify that projected runs remain deterministic and compatible with the Phase 3
/ Phase 4 persistence path.

### Checks

- [x] Add fixed-input replay tests
- [x] Add projected save/load roundtrip coverage
- [x] Verify RNG-dependent behavior is reproducible
- [x] Verify projector ordering does not leak nondeterminism

### Implementation Notes

- Projection-time ID allocation and ordering are likely the most fragile
  determinism points here.
- Snapshot metadata may need to preserve enough projector provenance to explain
  how the run was initialized.
- Added deterministic replay checks for fixed:
  - seed
  - family
  - RNG seed
  - step count
- Added projected save/load roundtrip coverage after stepping a seed-driven
  model.
- Determinism is currently carried by:
  - normalized seed order
  - deterministic blueprint realization
  - stable backend allocation order
  - explicit `rng_seed` and serialized runtime RNG state

### Verification

- [x] Fixed seed/family/override/RNG inputs reproduce identical runs
- [x] Projected models survive normal save/load roundtrip

### Summary

The seed-driven `GRCV2` path now has replay and persistence evidence. Fixed
inputs reproduce identical runs, and projected models survive ordinary
save/load roundtrip without losing runtime progression or topology identity.

## Iteration 8. Validation Gate

### Goal

Validate the resulting end-to-end path against Phase L, Phase 4, and the PDE
bridge cautions before calling the realization phase complete.

### Checks

- [x] Review projector behavior against neutral seed meaning
- [x] Review parameter-family behavior against the PDE bridge language
- [x] Record any remaining realization limitations explicitly
- [x] Verify no unresolved blocker remains for seed-driven `GRCV2` execution on
  `cell-1` and `cell-4`

### Implementation Notes

- This gate should answer whether the project can honestly say:
  validated canonical seeds are executable through `GRCV2`.
- Remaining limitations are acceptable only if they are explicit and narrow.
- Phase L boundary check:
  - family-specific projector logic remains in `src/pygrc/models/grc_v2_landscape.py`
  - no family-specific realization logic was moved back into
    `src/pygrc/landscapes/`
  - neutral seed meaning remains the consumed input, not a redefined output
- Phase 4 compatibility check:
  - projected state construction reuses ordinary `GRCV2` validation
  - seed-driven models step, serialize, load, and replay through the existing
    Phase 4 runtime surface rather than a parallel path
- PDE bridge caution check:
  - named families are implemented as regime-transfer presets
  - they are not claimed as direct PDE coefficient equivalence
- Explicit remaining limitations:
  - `double_well` seed potential currently projects to a documented quadratic
    surrogate because baseline `GRCV2` does not yet expose a native double-well
    site-potential backend
  - ridge-derived support edges are a `GRCV2` projector policy used to keep
    representative seeds executable; they are not elevated into neutral seed
    ontology or claimed as a mandatory cross-family rule
  - root-owned outer boundary ridges may remain metadata-only projector markers
    when no realizable support edge exists; this is now an explicit, recorded
    projector choice rather than silent degradation
  - the initial representative runs prove executable evolution and replay, but
    they do not yet prove that one chosen family such as
    `balanced_baseline` is the empirically best PDE analogue
  - the representative `cell-1` / `cell-4` smokes currently close the
    execution-path question, not the later backend-comparison question
- None of those limitations block the central Phase L1 claim:
  canonical validated seeds can now be executed through the first family.

### Verification

- [x] The seed-driven `GRCV2` path is reviewable against the governing docs
- [x] No unresolved blocker remains for the initial representative seeds

- Verification basis:
  - full local suite:
    - `./.venv/bin/python -m unittest discover tests`
  - direct executable smoke:
    - `cell-1` through `run_grcv2_landscape_seed(..., family_name='balanced_baseline', rng_seed=7, num_steps=3)`
    - `cell-4` through `run_grcv2_landscape_seed(..., family_name='balanced_baseline', rng_seed=7, num_steps=3)`
  - observed smoke result:
    - both seeds run successfully through the new end-to-end path
    - `cell-4` shows nontrivial runtime evolution in observables
    - replay remains deterministic for fixed seed/family/RNG inputs

### Summary

Completed the Phase L1 validation gate. The project can now honestly claim that
canonical validated landscape seeds are executable through `GRCV2` via a
documented projector, a named PDE-informed family surface, and a deterministic
runner path. The remaining limitations are explicit and narrow: the family
presets are regime bridges rather than PDE calibration, `double_well` currently
maps through a documented quadratic surrogate in baseline `GRCV2`, and
ridge-derived support edges remain projector policy rather than neutral-seed
ontology. Those limits do not block the representative `cell-1` / `cell-4`
execution path, so Phase L1 closes as the first end-to-end seed-to-family
runtime bridge.
