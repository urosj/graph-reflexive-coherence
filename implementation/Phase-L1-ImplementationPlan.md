# Phase L1 Implementation Plan

This document is the detailed execution plan for **Phase L1: Landscape To
`GRCV2` Realization**.

Phase L1 closes the practical gap left intentionally open by Phase L:

- Phase L produced validated, normalized `LandscapeSeed` objects,
- Phase 4 produced an executable, paper-aligned `GRCV2`,
- but there is not yet an implementation path that turns canonical landscape
  seeds such as `cell-1` and `cell-4` into executable `GRCV2` runs under
  PDE-informed parameter families.

Phase L1 exists to make that bridge real code.

## Purpose

Phase L1 must establish:

- a family-specific `LandscapeSeed -> GRCV2` realization path,
- an explicit mapping policy from neutral seed primitives into weighted-graph
  initialization,
- a first executable parameter-family surface that reuses the PDE parameter
  bridge without pretending to do direct coefficient transfer,
- and a deterministic runner path that can execute representative seeds for
  `N` steps and report how they evolve.

The goal is not to generalize all future family projectors in advance. The goal
is to make the first seed-driven executable workflow real, documented, and
testable.

## Inputs From Earlier Phases

Phase L1 assumes the following outputs already exist and remain authoritative:

- Phase 0 determinism conventions in
  [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
- shared contracts and state surfaces from Phases 1 to 3
- the executable `GRCV2` baseline from Phase 4:
  - [`Phase-4-ImplementationPlan.md`](./Phase-4-ImplementationPlan.md)
  - [`Phase-4-ImplementationChecklist.md`](./Phase-4-ImplementationChecklist.md)
  - [`Phase-4-DiscretizationDefense.md`](./Phase-4-DiscretizationDefense.md)
  - [`Phase-4-Retrospective.md`](./Phase-4-Retrospective.md)
- the neutral seed layer from Phase L:
  - [`Phase-L-ImplementationPlan.md`](./Phase-L-ImplementationPlan.md)
  - [`Phase-L-ImplementationChecklist.md`](./Phase-L-ImplementationChecklist.md)
  - [`Phase-L-ProjectorBoundary.md`](./Phase-L-ProjectorBoundary.md)
- the theory-facing landscape bridge:
  - [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)
  - [`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)
  - [`PDELandscapeToSeedTranslation.md`](./PDELandscapeToSeedTranslation.md)
  - [`LandscapeToGRCPlan.md`](./LandscapeToGRCPlan.md)
- the PDE regime bridge in
  [`PDE-ParameterFamilyBridge.md`](./PDE-ParameterFamilyBridge.md)

Phase L1 should not silently contradict those documents. If realization pressure
forces a change in seed meaning or baseline `GRCV2` semantics, that must be
recorded explicitly in the relevant design or phase document.

## In Scope

- a `LandscapeSeed -> GRCV2` projector module and public entry points
- seed-primitive-to-weighted-graph realization rules
- seed-driven initial `GRCV2State` construction
- parameter-family presets or resolvers for PDE-informed `GRCV2` regimes
- executable runner support for:
  - selecting a seed
  - selecting a parameter family or explicit override
  - running `N` steps
  - returning trajectory/observable/event data
- end-to-end smoke coverage for:
  - `cell-1`
  - `cell-4`
- deterministic replay validation for seed-driven runs

## Out Of Scope

- generalized multi-family projector protocol
- direct `LandscapeSeed -> GRCV3` / `GRC9` implementation
- broad parameter search or fitting loops
- visualization dashboards
- machine-driver orchestration
- host-integration APIs
- claiming cross-family realization equivalence beyond the implemented `GRCV2`
  path

## Phase L1 Design Constraints

### 1. Phase L Remains Neutral

Phase L1 may consume the neutral seed layer, but it must not move family logic
back into `src/pygrc/landscapes/`.

This means:

- no family-specific fields are added to neutral seed meaning just to make the
  projector easier,
- and any `GRCV2` realization choice is documented as projector policy rather
  than retroactively declared seed truth.

### 2. First Realization, Not Premature Generalization

Phase L1 should implement the first real projector cleanly before inventing a
shared cross-family projector abstraction.

That means:

- concrete `GRCV2` realization code first,
- common protocol later only if real duplication appears.

### 3. Parameter Families Are Regime Bridges, Not Direct Copies

The PDE bridge already established that direct numeric copying is unsafe.

Phase L1 should therefore implement:

- named parameter families or preset resolvers,
- with explicit mapping from PDE-facing regime axes into resolved `GRCV2`
  parameters,
- and with clear override semantics.

It should not claim:

- that copied PDE coefficients are mathematically identical to discrete-family
  coefficients.

### 4. Determinism Must Survive Projection

For the same:

- validated seed,
- parameter family,
- explicit overrides,
- and RNG seed,

Phase L1 should produce the same initial `GRCV2` construction and the same run
trajectory.

Projection-time topology ordering, node/edge allocation order, and any default
tie-breaking must therefore be deterministic and test-visible.

### 5. Realization Policy Must Be Reviewable

The main risk in this phase is not syntax but silent interpretation drift.

So Phase L1 must record explicitly:

- how basins become node support,
- how ridges affect edge/connectivity or local barriers,
- how valleys become channels,
- how junction/saddle hints influence routing topology,
- and how transport intent influences initialization without pretending to set
  solved flux directly.

### 6. Start With Representative Seeds, Not Arbitrary Coverage Claims

The first required executable seeds are:

- `cell-1`
- `cell-4`

Those should become the acceptance targets for the first projector/runner path.

Other seeds, such as `s6-periodic-seam-ring`, may be added later if the
realization policy is already stable enough to interpret them honestly.

## Expected Code Shape After Phase L1

The exact split may evolve, but the intended boundary is close to:

```text
src/pygrc/
  models/
    grc_v2.py
    grc_v2_state.py
    grc_v2_landscape.py
  landscapes/
    seed.py
    validation.py
    io.py
    pde_translation.py
```

Supporting tests will likely expand under:

```text
tests/
  models/
    test_grc_v2_landscape_*.py
```

If a tiny helper module is warranted for named parameter families, it should
remain adjacent to the family-specific realization boundary rather than
reopening the neutral seed package.

## Workstreams

## 1. Projector Module Boundary

### Tasks

- Decide where the `GRCV2` landscape projector lives in code.
- Define the public entry points for:
  - projection only
  - projection plus model construction
  - trajectory execution helper
- Keep the boundary family-specific and explicit.

### Required Decisions

- whether the module lives next to `grc_v2.py` or in another family-local place
- whether projection returns a `GRCV2State`, a `GRCV2`, or both through separate
  entry points
- what the public naming should be

### Acceptance Criteria

- there is one obvious implementation entry point for seed-driven `GRCV2`
  construction
- the neutral seed package remains family-neutral
- later families can copy the boundary pattern without inheriting v2 semantics

## 2. Primitive-To-Topology Realization Policy

### Tasks

- Define how each neutral primitive kind participates in the initial weighted
  graph:
  - basin
  - plateau
  - ridge
  - valley
  - junction/saddle
- Decide what counts as:
  - direct support node creation
  - adjacency creation
  - barrier/connector influence
  - routing-hub influence

### Required Decisions

- how many initial nodes a primitive contributes in the baseline projector
- whether certain primitives map to node attributes, edge attributes, or both
- how deterministic tie-breaking works when multiple seeds imply the same
  connection opportunity

### Acceptance Criteria

- every supported primitive type has an explicit realization rule
- unsupported or ambiguous cases fail explicitly rather than degrading silently
- the initial graph topology for the same seed is reproducible

## 3. Seed-To-State Initialization Policy

### Tasks

- Define how neutral seed meaning initializes concrete `GRCV2State` fields:
  - node coherence
  - edge conductance
  - optional label priors
  - budget target
  - time / step index
  - cached quantities if any are initialized eagerly
- Define how constitutive profile and transport intent influence the initial
  state without violating `GRCV2` semantics.

### Required Decisions

- whether coherence priors are normalized directly to initial node masses
- how `budget_B` is interpreted if present in seed constitutive profile
- whether transport intent becomes:
  - topology bias only
  - potential bias only
  - or another explicit initialization hook

### Acceptance Criteria

- the projector constructs a valid `GRCV2State`
- budget initialization is explicit and reproducible
- seed meaning and `GRCV2` initialization responsibilities stay distinct

## 4. PDE-Informed Parameter Family Surface

### Tasks

- Define the first executable parameter-family surface for seed-driven `GRCV2`
  runs.
- Reuse the PDE bridge language for named families or latent regime axes.
- Support explicit parameter override on top of named presets.

### Required Decisions

- whether the first public surface is:
  - named presets
  - latent-axis resolver
  - or both
- what minimum preset set exists for first execution
- how override precedence is defined

### Acceptance Criteria

- a caller can choose a PDE-informed `GRCV2` regime without hand-building the
  entire parameter dict
- the mapping from family selection to resolved params is documented and
  test-visible
- the resulting params still pass standard `GRCV2` validation

## 5. Construction And Runner Surface

### Tasks

- Define the executable API for seed-driven construction and multi-step runs.
- Support:
  - loading a seed object or seed path
  - selecting a parameter family or explicit param dict
  - selecting run length `N`
  - selecting explicit RNG seed
  - returning per-step observables/events/state snapshots as needed

### Required Decisions

- whether runner utilities live in the projector module or a thin adjacent
  helper module
- what trajectory result shape looks like
- how much state history is retained by default versus optionally

### Acceptance Criteria

- the repo has one clear executable path from seed to multi-step `GRCV2` run
- runner outputs are deterministic and inspectable
- the path is small enough to be reused in smoke tests and examples

## 6. Representative Seed Coverage

### Tasks

- Make `cell-1` and `cell-4` executable through the new path.
- Decide what the first smoke assertions should check:
  - construction success
  - step progression
  - event production
  - observables trajectory
  - replay determinism

### Required Decisions

- whether `cell-1` and `cell-4` use the same default parameter family
- what minimal run length is enough to prove the path works
- what counts as a meaningful smoke rather than a superficial import test

### Acceptance Criteria

- `cell-1` can be projected and run for `N` steps
- `cell-4` can be projected and run for `N` steps
- smoke coverage checks actual runtime evolution rather than only construction

## 7. Determinism, Persistence, And Replay

### Tasks

- Verify that projected runs are deterministic across repeated construction.
- Verify that projected models still use the Phase 3/4 save-load path cleanly.
- Verify that RNG-dependent behavior remains replayable through explicit
  `rng_seed` / serialized `rng_state`.

### Required Decisions

- what replay equality means for seed-driven runs
- whether initial projection metadata is recorded in snapshot metadata or state
  extensions
- which projector inputs must be preserved for reproducibility

### Acceptance Criteria

- the same seed/family/override/RNG inputs reproduce the same run
- projected `GRCV2` models survive normal save-load roundtrip
- no projector-specific nondeterminism leaks through ordering or implicit
  defaults

## 8. Validation Gate And Follow-On Boundary

### Tasks

- Validate the resulting path against:
  - Phase L seed meaning
  - Phase 4 `GRCV2` semantics
  - the PDE parameter-bridge cautions
- Record remaining limitations explicitly.
- Define what later phases should reuse from this realization phase.

### Required Decisions

- what is now authoritative projector policy for `GRCV2`
- what remains family-specific and non-transferable
- what later `GRCV3` / `GRC9` work should imitate versus rethink

### Acceptance Criteria

- the first executable seed-driven family path is documented and reviewable
- no unresolved blocker remains for running representative seeds through `GRCV2`
- the reuse boundary for later families is explicit

## Suggested Iteration Order

The recommended implementation order is:

1. projector module boundary
2. primitive-to-topology realization policy
3. seed-to-state initialization policy
4. PDE-informed parameter family surface
5. construction and runner surface
6. representative seed coverage
7. determinism, persistence, and replay
8. validation gate and follow-on boundary

## Exit Criteria

Phase L1 is complete when:

- there is a documented and implemented `LandscapeSeed -> GRCV2` projector path
- named PDE-informed parameter families can be resolved into valid `GRCV2`
  params
- `cell-1` and `cell-4` can be executed for `N` steps through a stable runner
  path
- replay is deterministic for fixed seed, parameter family, overrides, and RNG
  seed
- the projector policy is documented tightly enough that future family
  realization work can compare against it rather than improvise from scratch

At that point, the project can honestly say that canonical landscape seeds are
not only translatable, but executable through the first discrete family.
