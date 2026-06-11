# Phase L Projector Boundary

This document defines the implementation-facing handoff from the neutral
landscape seed layer into later family projectors.

Its purpose is to prevent later `GRCV2` / `GRCV3` / `GRC9` work from:

- consuming raw YAML directly,
- reinterpreting source DSL fields independently,
- or rediscovering the seed boundary ad hoc inside family code.

## 1. What Phase L Now Guarantees

Phase L now guarantees a stable neutral seed layer with:

- runtime seed dataclasses in `src/pygrc/landscapes/seed.py`
- structural validation through `validate_landscape_seed(...)`
- YAML/JSON load-save support through `src/pygrc/landscapes/io.py`
- PDE-to-seed translation through `src/pygrc/landscapes/pde_translation.py`
- seed-layer mathematical-invariant checks through
  `validate_pde_seed_translation_equivalence(...)`
- canonical executable fixtures under `configs/landscapes/seed/`

This means later projectors do **not** need to solve:

- seed parsing,
- seed validation,
- PDE field-name normalization,
- or source-provenance preservation.

## 2. Required Projector Input

Later family projectors should consume:

- a validated `LandscapeSeed`

not:

- raw YAML text
- raw JSON text
- raw `dict[str, Any]` payloads from the PDE DSL

Recommended projector entry pattern:

1. load or receive a `LandscapeSeed`
2. run `validate_landscape_seed(seed)` if the caller has not already done so
3. project the validated neutral seed into family-specific initialization state

If the seed was produced from a PDE source and a projector wants extra
assurance during development, it may also rely on:

- `validate_pde_seed_translation_equivalence(...)`

before family realization begins.

## 3. What The Neutral Seed Layer Exposes

The seed layer is the only Phase L surface later projectors should depend on.

The key exported pieces are:

- `LandscapeSeed`
- `LandscapePrimitive` and concrete primitive dataclasses
- `load_landscape_seed(...)`
- `save_landscape_seed(...)`
- `landscape_seed_from_data(...)`
- `landscape_seed_to_data(...)`
- `validate_landscape_seed(...)`

For translation-facing workflows, Phase L also exposes:

- `translate_pde_landscape_data(...)`
- `translate_pde_landscape_json(...)`
- `validate_pde_seed_translation_equivalence(...)`

## 4. What Later Projectors Should Read From The Seed

Later projectors should treat the following as authoritative neutral input:

- `constitutive_profile`
- `primitives`
- `transport_intent`
- `geometry_hints`
- `extensions`

More specifically:

- `constitutive_profile` defines the neutral constitutive regime to realize
- `primitives` define the semantic support/interface/channel structure
- `transport_intent` defines declared directional preference without prescribing
  runtime flux
- `geometry_hints` preserve source-chart intent only
- `extensions` preserve source or family-specific payloads without elevating
  them into neutral truth

## 5. What Projectors Must Not Silently Reinterpret

Later family projectors must not silently reinterpret:

- source-chart hints as ontological coordinates
- transport intent as pre-solved flux values
- source extensions as neutral mandatory semantics
- inferred routing-hub annotations as explicit source `saddle` declarations

If a family chooses a realization policy, that choice belongs in the projector
or family plan, not retroactively in Phase L.

Examples:

- `geometry_hints.source_chart` may guide initialization, but it is not the
  final geometry of a realized graph
- `extensions.source_pde.implied_role = saddle_like_hub` may inform one
  projector policy, but it is not equivalent to an explicit source `saddle`
- explicit source `saddle` and explicit inferred routing-hub annotations must
  remain distinguishable

## 6. No Projector Protocol Yet

Phase L intentionally does **not** introduce a code-level projector protocol.

That is a deliberate boundary decision:

- the seed layer is now stable enough for later family phases to consume
- but projector-interface design should happen with family needs in view
- not prematurely inside the landscape bridge

So the current decision is:

- **documented handoff now**
- **shared code protocol later, only if it proves necessary**

## 7. Minimal Projector Responsibilities

Every later family projector should be responsible for:

- mapping seed primitives into family substrate objects
- deciding how neutral geometry hints are realized for that family
- deciding how transport intent biases initialization
- deciding how source extensions relevant to that family are consumed
- recording any family-specific realization choices explicitly

These are projector responsibilities, not Phase L responsibilities.

## 8. What Stays Out Of Scope For Phase L

Phase L stops before:

- weighted-graph construction
- port-graph construction
- family-specific hierarchy policies
- family-specific warmup or stabilization policies
- family-specific observer hooks
- machine-driver integration

If one of those choices is needed, it belongs in the relevant family phase.

## 9. Read-First Order For Future Family Work

Before implementing a projector or family seed loader, read these documents in
this order:

1. `implementation/GRCL-Landscape-DSL-TranslationGuide.md`
2. `implementation/LandscapeSeedSchema.md`
3. `implementation/PDELandscapeToSeedTranslation.md`
4. `implementation/PDEToGRCLMathematicalEquivalenceChecklist.md`
5. `implementation/Phase-L-ImplementationPlan.md`
6. `implementation/Phase-L-ImplementationChecklist.md`
7. `implementation/Phase-L-ProjectorBoundary.md`

## 10. Final Boundary Statement

Phase L owns:

- seed meaning
- seed validation
- translation
- fixture verification

Later family phases own:

- realization into executable substrate/state
- family-specific semantics
- projector policy

That split should remain explicit.

## 11. First Concrete Follow-On

The first concrete realization phase after Phase L is now:

- [`Phase-L1-ImplementationPlan.md`](./Phase-L1-ImplementationPlan.md)
- [`Phase-L1-ImplementationChecklist.md`](./Phase-L1-ImplementationChecklist.md)

That phase owns the first executable:

- `LandscapeSeed -> GRCV2` projector,
- PDE-informed `GRCV2` parameter-family surface,
- and representative seed-driven run path for `cell-1` and `cell-4`.

This keeps the Phase L boundary honest:

- Phase L stops at neutral seed meaning,
- Phase L1 starts family-specific realization,
- later family phases can compare against a concrete first projector without
  pretending that Phase L already implemented it.
