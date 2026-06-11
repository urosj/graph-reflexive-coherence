# Phase L Implementation Plan

This document is the detailed execution plan for **Phase L: Landscape Bridge**.

It turns the landscape-bridge documents into concrete implementation workstreams
for the first executable seed layer in `PyGRC`.

Phase L exists to make the landscape work real code rather than only theory and
schema notes. It should provide one authoritative runtime bridge between:

- the PDE landscape DSL,
- the normalized seed schema,
- and later family-specific projectors.

## Purpose

Phase L must establish:

- a runtime representation for normalized landscape seeds,
- explicit validation for that representation,
- configuration-layer load/save support,
- conservative PDE landscape JSON to seed translation,
- canonical translation fixtures that can be verified in tests,
- and a clear handoff boundary from neutral seeds into later family-specific
  realization work.

The goal is not yet to build `GRCV2` or `GRCV3` from seeds directly. The goal is
to stop carrying the landscape bridge only as prose and to give later phases one
stable implementation surface they can rely on.

## Inputs From Earlier Phases

Phase L assumes the following outputs already exist and remain authoritative:

- Phase 0 determinism conventions in [`Phase-0-DeterminismConventions.md`](./Phase-0-DeterminismConventions.md)
- Phase 0 implementation boundaries in [`Phase-0-BoundaryDecisions.md`](./Phase-0-BoundaryDecisions.md)
- Phase 1 shared contracts in `src/pygrc/core/`
- Phase 3 canonical serialization helpers in `src/pygrc/core/serialization.py`
- the landscape meaning guide in [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)
- the neutral seed schema in [`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)
- the PDE-to-seed mapping note in [`PDELandscapeToSeedTranslation.md`](./PDELandscapeToSeedTranslation.md)
- the canonical seed fixtures under `configs/landscapes/seed/`

Phase L should not silently contradict those documents. If runtime pressure
reveals a schema or translation problem, the relevant design document should be
updated explicitly rather than bypassed in code.

For mathematical-claim boundaries at the translation layer, Phase L also relies
on:

- [`PDEToGRCLMathematicalEquivalenceChecklist.md`](./PDEToGRCLMathematicalEquivalenceChecklist.md)

## In Scope

- runtime seed dataclasses / typed structures
- seed validation and normalization logic
- seed load/save support
- parser-boundary decision for seed configuration files
- conservative PDE landscape JSON translation into normalized seeds
- provenance and translation-note preservation
- canonical fixture verification for representative landscapes
- explicit later-projector boundary definition

## Out Of Scope

- direct `GRCV2` / `GRCV3` / `GRC9` projector implementations
- graph construction from seeds into executable model state
- PDE compiler reimplementation
- landscape visualization tooling
- parameter-family search or fitting
- observer/integration-layer use of seeds
- machine-driver diff/patch support for seed documents

Those projector and executable-realization concerns are now explicitly deferred
to the follow-on phase:

- [`Phase-L1-ImplementationPlan.md`](./Phase-L1-ImplementationPlan.md)

## Phase L Design Constraints

### 1. Meaning Before Projection

Phase L must preserve the landscape semantics already fixed in the translation
guide and schema.

Runtime code must not quietly redefine:

- what counts as a basin, ridge, valley, plateau, or saddle/junction,
- what belongs to constitutive profile versus transport intent,
- or what counts as a source-chart hint rather than derived geometry.

### 2. Neutral Seed First, Family Projector Later

Phase L must stop at the neutral seed layer.

It may define:

- one runtime seed object model,
- one validation boundary,
- and one translation result shape.

It must not let one family's loader needs redefine the neutral seed contract.

### 3. Source-Chart Hints Are Not Ontological Coordinates

Fields such as:

- `chart_center_hint`
- `chart_scale_hint`
- `chart_principal_axis_hint`
- `geometry_hints.source_chart`

must remain source-chart bookkeeping only.

Phase L code must preserve them and validate them, but not treat them as the
final geometry of the realized `GRC` object.

### 4. Conservative Translation By Default

The first translator implementation should use the
`lossless_source_normalization` mode as the default.

That means:

- explicit source primitives map directly,
- source-implied structures such as `saddle` or `plateau` are not synthesized
  unless an explicit enrichment path is requested,
- and translation losses or approximations are recorded rather than hidden.

### 5. Configuration-Layer Dependency Boundary Must Be Explicit

The repo currently has no runtime parsing dependency for YAML.

Phase L must make an explicit decision about seed I/O strategy:

- JSON-only runtime support,
- YAML support via a dedicated dependency,
- or another constrained approach.

Whatever the decision is, it must stay in the configuration layer and not bleed
into the core model execution path.

Chosen direction for Phase L:

- YAML is the preferred human-facing seed authoring and storage format
- normalized in-memory runtime objects or dicts are the semantic comparison form
- canonical JSON may be derived from normalized seed data when a stricter
  machine-stable representation is needed for hashing, fixture normalization, or
  reproducible interchange

Phase L should therefore optimize for:

- human-readable seed files at the config boundary,
- deterministic normalized runtime data internally,
- and canonical JSON only as a derived representation rather than the primary
  authoring format.

### 6. Provenance Is Part Of The Contract

Translated seeds must preserve enough provenance to answer:

- which source spec they came from,
- which translator mode produced them,
- which source-side compile metadata was preserved but not elevated,
- and what semantic enrichments or losses occurred.

### 7. Deterministic Translation Targets

For the same source input and translation mode, the translator output must be
deterministic.

This does not mean Phase L must immediately define one final seed text
serialization format identical to snapshot rules, but it does mean that:

- field population,
- ordering choices where ordering matters,
- and canonical fixture expectations

must be stable and testable.

Fixture equality should be based on:

- normalized runtime objects,
- or normalized dict-like structures derived from them,

not on raw YAML text equality.

## Expected Code Shape After Phase L

The exact split may evolve, but the intended package boundary is close to:

```text
src/pygrc/
  landscapes/
    __init__.py
    seed.py
    validation.py
    io.py
    pde_translation.py
```

Supporting tests should likely live under:

```text
tests/
  landscapes/
```

If the implementation pressure justifies more files, the split should still
keep:

- seed model,
- validation,
- I/O,
- and source translation

as separate concerns.

## Workstreams

## 1. Landscape Package Boundary

### Tasks

- Create the `src/pygrc/landscapes/` package.
- Decide the module split between seed model, validation, I/O, and translation.
- Export one clear public runtime surface for later phases.

### Required Decisions

- landscape functionality lives outside `core/` and `models/`
- the package boundary is neutral-seed-oriented rather than family-oriented
- public exports are minimal and intentional

### Acceptance Criteria

- the repo has one dedicated landscape package
- import paths for seed runtime code are clear and stable
- later family phases have one obvious place to integrate from

## 2. Seed Runtime Model

### Tasks

- Define typed runtime structures for the normalized seed document.
- Decide where enums or literal domains are represented.
- Represent primitives, constitutive profile, transport intent, geometry hints,
  and extensions explicitly enough for validation and translation.

### Required Decisions

- whether runtime model uses dataclasses, typed dicts, or a hybrid
- how primitive polymorphism is represented
- how optional extension namespaces are carried without overfitting one family

### Acceptance Criteria

- normalized seeds have one programmatic runtime shape
- code can distinguish basin/ridge/valley/plateau/junction-saddle cleanly
- runtime types reflect the schema without leaking family internals

## 3. Seed Validation Layer

### Tasks

- Implement structural validation for normalized seed documents.
- Validate cross-references, hierarchy, primitive types, and constitutive fields.
- Validate source-chart hint fields according to their neutral role.

### Required Decisions

- strict versus lenient validation behavior
- how unknown extension namespaces are handled
- how runtime validation errors are represented

### Acceptance Criteria

- malformed seeds are rejected before projector code would consume them
- valid seeds can be normalized into one stable runtime shape
- extension namespaces do not break neutral validation by default

## 4. Seed I/O And Parser Strategy

### Tasks

- Decide the initial runtime parser strategy for seed files.
- Implement load/save helpers for normalized seeds.
- Keep parser concerns isolated from the core execution path.

### Required Decisions

- whether Phase L supports YAML at runtime immediately
- whether JSON support exists as a fallback or canonical interchange form
- where file I/O lives versus pure in-memory conversion

### Chosen Baseline

- Phase L should support YAML seed files at runtime
- any JSON form should be treated as a derived interchange/canonicalization form,
  not the preferred authoring format
- equality and verification should operate on normalized runtime data rather than
  source text

### Acceptance Criteria

- the parser strategy is explicit in code and docs
- seeds can be loaded into runtime structures and written back predictably
- configuration parsing does not contaminate core model layers

## 5. PDE Source Translation

### Tasks

- Implement translation from the current PDE landscape JSON into normalized seed runtime objects.
- Normalize top-level fields, constitutive profile, primitives, geometry, and source metadata.
- Preserve source-side compile policy and initial flux under extensions where required.

### Required Decisions

- source-field-to-seed-field mapping remains aligned with `PDELandscapeToSeedTranslation.md`
- default translation mode is `lossless_source_normalization`
- translator output records source provenance and translation mode explicitly

### Acceptance Criteria

- representative PDE source specs can be translated programmatically
- translation does not invent enrichment-only primitives in default mode
- source metadata and compile-only fields are preserved in the correct boundary
- seed-layer mathematical invariants are executable and test-visible

## 6. Source-Implied Structure Handling

### Tasks

- Implement explicit handling for source-implied structures such as routing hubs.
- Decide how conservative annotations are represented in translated seeds.
- Keep enrichment behavior off by default unless explicitly enabled.

### Required Decisions

- where `implied_role`-style annotations live
- how enrichment mode is requested if supported at all in Phase L
- how losses or inferences are recorded

### Acceptance Criteria

- default translation is conservative and reproducible
- inferred saddle/plateau semantics are never smuggled in silently
- translation notes capture any nontrivial interpretation

## 7. Canonical Fixture Verification

### Tasks

- Verify translator output against the canonical `cell-1`, `cell-4`, and `s6`
  normalized seed fixtures.
- Decide how fixture comparisons are performed.
- Keep fixture expectations stable and readable.

### Required Decisions

- whether fixture comparison is object-based, dict-based, or text-based
- how translation notes and source extensions are compared
- how fixture drift is detected in tests

### Chosen Baseline

- fixture comparison should be object-based or normalized-dict-based
- textual equality of YAML files should not be the semantic correctness rule
- if a canonical textual form is needed for debugging, it should be derived from
  normalized data rather than used as the primary acceptance criterion

### Acceptance Criteria

- canonical fixtures are not prose-only; they are test targets
- translator behavior is checked against representative source families
- any intentional fixture change requires an explicit test/document update

## 8. Later Projector Boundary

### Tasks

- Define the explicit handoff from normalized seeds into later family projectors.
- Decide what Phase L should expose for future `GRCV2` / `GRCV3` / `GRC9`
  loader work without implementing those projectors yet.
- Document what is preserved versus deferred.

### Required Decisions

- whether one projector protocol or adapter boundary is introduced now
- what shape later projector inputs should consume
- what remains out of scope for Phase L

### Acceptance Criteria

- later phases do not need to rediscover the seed boundary
- family projectors have one stable input layer
- Phase L ends before family semantics are reintroduced

## Suggested Iteration Order

The recommended implementation order is:

1. landscape package boundary
2. seed runtime model
3. validation layer
4. parser strategy and seed I/O
5. PDE source translation
6. source-implied structure handling
7. canonical fixture verification
8. projector boundary closeout

## Exit Criteria

Phase L is complete when:

- `src/pygrc/landscapes/` exists with a stable public surface
- normalized seeds can be loaded and validated programmatically
- PDE source landscapes can be translated into normalized seeds deterministically
- the canonical `cell-1`, `cell-4`, and `s6` fixtures are verified by tests
- the later family-projector boundary is documented in implementation-facing terms

At that point, landscape work is no longer blocked on prose-only definitions and
later family phases can begin using one stable bridge layer.

## Follow-On Phase

Phase L intentionally stops at the neutral seed boundary.

The next concrete phase for making canonical landscapes executable through the
first family is:

- [`Phase-L1-ImplementationPlan.md`](./Phase-L1-ImplementationPlan.md)

That follow-on phase owns:

- `LandscapeSeed -> GRCV2` realization,
- PDE-informed `GRCV2` parameter-family resolution,
- and end-to-end seed-driven runtime execution for representative seeds such as
  `cell-1` and `cell-4`.
