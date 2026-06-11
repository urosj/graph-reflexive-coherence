# GRCL-v3 Family-Native Lowering Refactor Plan

## Purpose

This note turns the recorded `GRCL-v3` lowering architecture decision into a
concrete refactor plan.

Its job is not to redesign `GRCV3` runtime equations.
Its job is to define how the codebase should migrate from:

- weaker-blueprint semantic dependence

to:

- family-native lowering for `grcv3.rich.v2+`

while preserving compatibility for weaker seed lanes.

## Problem Statement

The current `GRCV3` landscape path still boots through:

- `realize_grcv2_landscape_blueprint(...)`

and then adds `GRCV3`-specific lowering on top of that.

That was acceptable while:

- `GRCL` was still mainly neutral/common
- `grcv3.rich.v1` was still a narrow transitional probe

It becomes the wrong long-term shape once `grcv3.rich.v2+` can already express:

- local axes
- weak/stable curvature roles
- explicit attachment sites
- channel geometry
- boundary geometry

At that point, the projector should stop relying semantically on the weaker
`GRCV2` blueprint as the authoritative intermediate model.

## Target Architecture

The target split should be explicit.

### Lane A. Interpretive Projector Path

Applies to:

- neutral/common `GRCL`
- `grcv2`
- `grcv3.rich.v1`

Allowed behavior:

- heuristic enrichment
- weaker semantic inference
- reuse of the `GRCV2` blueprint as the main intermediate form

### Lane B. Family-Native Lowering Path

Applies to:

- `grcv3.rich.v2+`

Required behavior:

- common seed parsing/loading stays shared
- `grcv3` extension parsing/validation stays shared
- topology lowering becomes `GRCV3`-native
- explicit `GRCV3` source semantics are consumed directly rather than flattened
  into a weaker semantic blueprint first

## Boundary Rules

The refactor should preserve the following boundaries.

### What Stays Shared

- `landscapes/seed.py`
- `landscapes/io.py`
- `landscapes/validation.py`
- `landscapes/extensions/grcv3.py`
- top-level seed normalization and version dispatch

### What Stops Being Authoritative For `grcv3.rich.v2+`

- `GRCV2LandscapeBlueprint` as the semantic intermediate representation

This does **not** forbid temporary code reuse.
It means that `grcv3.rich.v2+` semantics must no longer be defined *through*
that blueprint.

### What Remains Allowed Under Family-Native Lowering

- motif discretization
- support-node counts
- channel sampling rules
- mass-distribution rules
- initial conductance/bootstrap rules
- explicit approximation notes

These are constitutive lowering choices, not semantic reinterpretation.

### What Must Stop Under Family-Native Lowering

- inferring weak axes already named by the seed
- inferring attachment sites already named by the seed
- mapping rich basin/channel/boundary roles into a weaker semantic form and then
  reconstructing them later
- using `GRCV2` compatibility artifacts as the authoritative meaning model for
  `grcv3.rich.v2+`

## Refactor Scope

The refactor should be intentionally narrow.

### In Scope

- `src/pygrc/models/grc_v3_landscape.py`
- new family-native lowering helpers if needed under:
  - `src/pygrc/models/grc_v3_landscape_*.py`
- tests for path selection and direct lowering behavior
- implementation notes/checklists documenting the migration

### Out Of Scope

- changing `GRCV3` step equations
- changing spark thresholds to compensate for source weakness
- changing neutral/common seed ontology
- removing the interpretive projector path for weaker schemas

## Required End-State Properties

The refactor should be treated as successful only if all of the following are
true.

1. `grcv3.rich.v2+` path selection is explicit in code.
2. The family-native path can lower rich basin/channel/boundary semantics
   without semantic dependence on `GRCV2LandscapeBlueprint`.
3. Neutral/common seeds and `grcv3.rich.v1` still work on the compatibility
   path.
4. The runtime artifacts record which lowering path was used.
5. Tests prove that the two lanes remain distinct.

## Proposed Execution Stages

### Stage 1. Path Split

Create an explicit dispatcher boundary in `grc_v3_landscape.py`:

- interpretive compatibility path
- family-native lowering path

Acceptance:

- `grcv3.rich.v2+` and weaker schemas take different code paths by design
- the selected path is recorded in cached diagnostics / snapshot metadata

### Stage 2. Direct Primitive Surface

Implement family-native lowering helpers that consume direct seed primitives
rather than a `GRCV2` semantic blueprint:

- basin/plateau
- junction/saddle
- valley
- ridge

Acceptance:

- direct lowering consumes source semantics from:
  - primitive fields
  - `extensions.grcv3`
- no semantic dependency on `GRCV2LandscapeBlueprint` remains in the
  `grcv3.rich.v2+` lane

### Stage 3. Topology Assembly And Diagnostics

Move graph assembly, mass distribution, attachment resolution, and diagnostic
recording fully into the family-native lane.

Acceptance:

- attachment decisions are traceable to source roles / preferences
- approximation notes remain explicit
- diagnostics state which path was used and why

### Stage 4. Regression And Comparison

Prove:

- weaker schemas still work on the compatibility lane
- `grcv3.rich.v2+` works on the native lane
- deterministic snapshots still hold

Acceptance:

- path-specific tests pass
- existing weaker-lane runtime tests remain green
- new native-lane tests pass

## Suggested Tests

At minimum, add tests that prove:

1. neutral/common seed -> compatibility path
2. `grcv3.rich.v1` -> compatibility path
3. `grcv3.rich.v2` -> family-native path
4. direct lowering uses source-declared roles without weaker-blueprint fallback
5. snapshots/diagnostics expose the chosen path

## Failure Interpretation

If the family-native refactor lands and rich seeds still fail to spark, the
result becomes much more informative:

- the failure can then be attributed to source semantics or lowering choices
- not to silent normalization by the weaker blueprint path

That is the main reason this refactor is worth doing even before spark success
is guaranteed.

## Recommended Next Artifact

The next execution artifact after this refactor plan should be:

- [GRCL-V3-FamilyNativeLoweringRefactorChecklist.md](./GRCL-V3-FamilyNativeLoweringRefactorChecklist.md)

That checklist should:

1. define the explicit path split
2. migrate one primitive family at a time
3. keep weaker-lane compatibility visible at every step
