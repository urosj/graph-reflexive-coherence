# Phase L Implementation Checklist

This document tracks the execution of **Phase L: Landscape Bridge**.

It is intentionally separate from [`Phase-L-ImplementationPlan.md`](./Phase-L-ImplementationPlan.md):

- the plan defines scope, workstreams, boundaries, and acceptance criteria,
- this checklist records how the Phase L work is actually executed iteration by iteration.

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
- Keep landscape implementation notes aligned with:
  - [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)
  - [`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)
  - [`PDELandscapeToSeedTranslation.md`](./PDELandscapeToSeedTranslation.md)
  - [`PDEToGRCLMathematicalEquivalenceChecklist.md`](./PDEToGRCLMathematicalEquivalenceChecklist.md)
  - [`Phase-L-ImplementationPlan.md`](./Phase-L-ImplementationPlan.md)

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

Create the Phase L execution checklist and align it with the Phase L implementation plan.

### Checks

- [x] Create `Phase-L-ImplementationChecklist.md`
- [x] Link the checklist from `ImplementationPhases.md`
- [x] Align the checklist structure with the Phase L workstreams
- [x] Decide whether Phase L needs any additional companion planning docs before implementation starts

### Implementation Notes

- The execution checklist follows the same separation-of-concerns pattern used in earlier phases.
- The Phase L plan remains the normative planning document; this file is the execution tracker.
- Possible companion docs for this phase may become useful later:
  - `Phase-L-TranslationMatrix.md`
  - `Phase-L-FixturePolicy.md`
  - `Phase-L-ProjectorBoundary.md`
- Those companion docs are optional and should only be created if implementation pressure outgrows the main plan and checklist.
- No additional companion doc is required before implementation starts.

### Verification

- [x] The checklist file exists under `implementation/`
- [x] `ImplementationPhases.md` points to the checklist
- [x] The checklist iterations map cleanly onto the Phase L plan

### Summary

Phase L now has a paired plan and execution checklist. Companion notes remain optional until implementation pressure makes them necessary.

## Iteration 1. Landscape Package Boundary

### Goal

Create the landscape package and define its initial public/runtime boundary.

### Checks

- [x] Create `src/pygrc/landscapes/`
- [x] Add package exports for the initial public surface
- [x] Decide the first module split between seed model, validation, I/O, and source translation
- [x] Add landscape-package import smoke coverage

### Implementation Notes

- The package should stay neutral-seed-oriented rather than family-oriented.
- The first pass should avoid over-splitting files before the runtime model is clear.
- Public exports should be minimal and intentional.
- Added `src/pygrc/landscapes/` with the initial neutral split:
  - `seed.py`
  - `validation.py`
  - `io.py`
  - `pde_translation.py`
- Chosen Iteration 1 public surface:
  - package-level export of module namespaces only
  - no runtime seed classes or translator functions are exported yet
  - this keeps the boundary stable without pretending Iteration 2 functionality already exists
- Updated `src/pygrc/__init__.py` so `pygrc.landscapes` is part of the top-level package surface.
- Added import-smoke coverage in:
  - `tests/landscapes/test_import_smoke.py`
  - and extended `tests/core/test_import_smoke.py` to include the new package
- The module split is now fixed early enough that later iterations can add code without reopening package placement.

### Verification

- [x] `pygrc.landscapes` imports cleanly
- [x] The package boundary is visible in tests and does not leak into `core/` or `models/`

- Focused verification executed with:
  - `./.venv/bin/python -m unittest tests.core.test_import_smoke tests.landscapes.test_import_smoke`
- `.venv` is the default repo interpreter for subsequent Phase L verification.

### Summary

Implemented the initial `pygrc.landscapes` package boundary with a minimal public module surface and dedicated import-smoke coverage. The runtime model and validation logic remain deferred to later iterations, but the package split is now fixed and test-visible.

## Iteration 2. Seed Runtime Model

### Goal

Implement the normalized seed runtime types.

### Checks

- [x] Define the top-level seed runtime object
- [x] Define runtime structures for:
  - [x] constitutive profile
  - [x] primitives
  - [x] transport intent
  - [x] geometry hints
  - [x] extensions
- [x] Decide how primitive variants are represented
- [x] Keep source-chart hint fields explicit in the runtime model

### Implementation Notes

- The runtime model should reflect the schema directly enough for validation and translation work.
- Family-specific extensions must remain namespaced payloads rather than creeping into neutral fields.
- The representation should stay friendly to later serialization and fixture comparison.
- Chosen runtime-model style:
  - dataclasses, consistent with the existing Phase 1 and Phase 4 contract surface
- Added concrete seed runtime dataclasses in `src/pygrc/landscapes/seed.py` for:
  - `SeedDocumentMeta`
  - `SeedPotential`
  - `SeedConstitutiveProfile`
  - `SeedGeometryHints`
  - `SeedTransportIntent`
  - `LandscapeSeed`
- Chosen primitive representation:
  - one shared `SeedPrimitive` base dataclass
  - concrete variant dataclasses for:
    - `BasinSeedPrimitive`
    - `PlateauSeedPrimitive`
    - `RidgeSeedPrimitive`
    - `ValleySeedPrimitive`
    - `JunctionSeedPrimitive`
  - `JunctionSeedPrimitive.type` may be either `junction` or `saddle`
- Added exported primitive and translation-mode constants so later validation and
  translation code use one shared vocabulary.
- Kept source-chart bookkeeping explicit in field names:
  - `chart_center_hint`
  - `chart_scale_hint`
  - `chart_principal_axis_hint`
  - `SeedGeometryHints.source_chart`
- Updated `pygrc.landscapes` exports so Iteration 2 introduces the real runtime
  type surface without exposing validation or translator behavior prematurely.
- Added focused runtime-type tests in:
  - `tests/landscapes/test_seed_types.py`

### Verification

- [x] Runtime seed objects can be instantiated for representative seed data
- [x] Primitive variants are distinguishable without family-specific code

- Focused verification executed with:
  - `./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_seed_types`
- Iteration 2 expanded the package export surface beyond module namespaces:
  - the import-smoke test was updated accordingly so the public boundary remains
    intentional and test-visible.

### Summary

Implemented the normalized seed runtime type surface with dataclass-based document,
profile, primitive, geometry-hint, and transport-intent structures. The runtime
layer now has one shared vocabulary for primitive kinds and translation modes,
while keeping source-chart hint fields explicit and family-specific extensions
namespaced.

## Iteration 3. Seed Validation Layer

### Goal

Implement validation for normalized seed documents and runtime objects.

### Checks

- [x] Validate required top-level groups
- [x] Validate constitutive profile fields and value presence
- [x] Validate primitive types and per-primitive required fields
- [x] Validate cross-references:
  - [x] `parent_id`
  - [x] `owner_id`
  - [x] `from_id`
  - [x] `to_id`
  - [x] `host_id`
  - [x] `branch_target_ids`
- [x] Validate containment acyclicity
- [x] Validate `depth_hint` consistency when present
- [x] Validate extension namespaces permissively by default

### Implementation Notes

- Validation should reject malformed neutral data before any projector uses it.
- Unknown extension namespaces should not fail default validation unless a stricter mode is explicitly introduced.
- Validation errors should be explicit and readable.
- Added `InvalidLandscapeSeedError` to the shared core error surface so the
  landscape boundary has an explicit contract-level exception type.
- Implemented `validate_landscape_seed(...)` in `src/pygrc/landscapes/validation.py`.
- Chosen validation style:
  - explicit field-by-field validation against the runtime dataclasses
  - direct `InvalidLandscapeSeedError` messages rather than aggregated error lists
  - permissive treatment of unknown extension namespaces by default
- Implemented validation for:
  - top-level seed identity
  - constitutive profile presence and numeric sanity
  - primitive IDs and allowed primitive kinds
  - cross-references for parent/owner/flow/host/branch relationships
  - containment acyclicity
  - `depth_hint` consistency with the implied parent hierarchy
  - transport-intent references
  - source-chart hint shape for point-valued fields
- Exported `validate_landscape_seed` from `pygrc.landscapes` as part of the
  public landscape boundary.
- Added focused tests in:
  - `tests/landscapes/test_seed_validation.py`

### Verification

- [x] Valid seeds pass validation
- [x] Malformed seeds fail for the right reasons
- [x] Unknown extension namespaces do not break neutral validation by default

- Focused verification executed with:
  - `./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_seed_types tests.landscapes.test_seed_validation`
- Unknown extension namespaces remain permissive by default at the neutral
  validation layer; only structural violations of required neutral data are
  rejected.

### Summary

Implemented the normalized seed validation layer with one explicit
`validate_landscape_seed(...)` entry point and a dedicated
`InvalidLandscapeSeedError` contract. The validation surface now covers required
top-level fields, primitive references, containment/hierarchy consistency,
transport-intent references, and permissive extension handling by default.

## Iteration 4. Seed I/O And Parser Strategy

### Goal

Decide and implement the initial seed load/save path.

### Checks

- [x] Decide the Phase L parser strategy for seed files
- [x] Implement in-memory seed-to-dict / dict-to-seed conversion
- [x] Implement file-based seed load support
- [x] Implement file-based seed save support if included in the chosen strategy
- [x] Keep configuration parsing isolated from core model execution

### Implementation Notes

- The repo currently has no runtime YAML dependency; this iteration must either add one explicitly or define a narrower initial support path.
- The parser decision must be recorded in the notes here and reflected in code/doc boundaries.
- File I/O should preserve provenance and extension data without reinterpretation.
- Chosen Phase L direction:
  - YAML is the preferred human-facing seed format
  - normalized runtime data is the semantic comparison form
  - canonical JSON is only a derived machine-stable representation when needed
- Installed `PyYAML` into `.venv` and added `PyYAML>=6.0` to `pyproject.toml`.
- Added explicit `pip` requirements files for the default `.venv` workflow:
  - `requirements.txt`
  - `requirements-dev.txt`
- Implemented the seed I/O surface in `src/pygrc/landscapes/io.py`:
  - `landscape_seed_from_data(...)`
  - `landscape_seed_to_data(...)`
  - `landscape_seed_to_canonical_json(...)`
  - `load_landscape_seed(...)`
  - `save_landscape_seed(...)`
- Chosen runtime file-format boundary:
  - YAML is the preferred authoring/storage format
  - JSON is also supported as an interchange format
  - canonical JSON is derived from normalized runtime data rather than treated
    as the primary human-facing format
- Chosen package export rule after Iteration 4:
  - public function exports for the I/O entry points
  - no need to export the `io` module namespace itself from `pygrc.landscapes`
- Implemented conversion through normalized runtime data first, then format
  rendering/parsing second, so semantic equality remains independent of file text.
- Tightened the config-layer error boundary in `src/pygrc/landscapes/io.py`:
  - malformed dict payloads raise `InvalidLandscapeSeedError`
  - malformed YAML/JSON parse failures are wrapped as `InvalidLandscapeSeedError`
  - non-mapping file payloads are rejected explicitly before runtime construction
- Added focused tests in:
  - `tests/landscapes/test_seed_io.py`

### Verification

- [x] Seed files can be loaded into runtime objects
- [x] Roundtrip behavior is defined and tested for the chosen format support
- [x] The parser boundary is explicit in code and docs

- Focused verification executed with:
  - `./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_seed_types tests.landscapes.test_seed_validation tests.landscapes.test_seed_io`
- Verified parser-boundary behavior includes:
  - in-memory dict-to-runtime and runtime-to-dict roundtrips
  - YAML file load/save roundtrip
  - JSON interchange roundtrip
  - malformed payload rejection through `InvalidLandscapeSeedError`
  - canonical JSON as a derived normalized representation

### Summary

Implemented the Phase L seed I/O boundary with real YAML runtime support, JSON
interchange support, normalized in-memory conversion, and derived canonical JSON
output. The parser strategy is now explicit in both code and dependency
configuration instead of remaining a planning-only decision. Iteration 4 also
closed the malformed-input boundary so configuration errors fail through the
landscape-layer exception contract rather than raw parser or constructor errors.

## Iteration 5. PDE Source Translation Surface

### Goal

Implement conservative PDE landscape JSON to normalized seed translation.

### Checks

- [x] Implement top-level source-to-seed mapping
- [x] Implement constitutive profile translation
- [x] Implement `basin` translation
- [x] Implement `ridge` translation
- [x] Implement `valley` translation
- [x] Preserve source compile and potential-compile metadata under `extensions.source_pde`
- [x] Preserve translator provenance fields in `meta`

### Implementation Notes

- Default translation mode should be `lossless_source_normalization`.
- Translation should preserve source meaning conservatively rather than synthesizing richer primitives by default.
- Source field naming differences such as `lambda_C` versus `lambda_c` should be normalized in one shared translation layer only.
- Implemented the first conservative translator in `src/pygrc/landscapes/pde_translation.py`.
- Added public translator entry points:
  - `translate_pde_landscape_data(...)`
  - `translate_pde_landscape_json(...)`
- Added translator metadata constants:
  - `PDE_TRANSLATOR_NAME`
  - `PDE_TRANSLATOR_VERSION`
- Implemented top-level normalization for:
  - `schema_version`
  - `meta`
  - `params`
  - `potential`
  - `geometry`
  - `compile`
  - `initial_flux`
  - explicit `primitives`
- Implemented explicit primitive translation only for source-declared:
  - `basin`
  - `ridge`
  - `valley`
- Implemented constitutive-profile normalization:
  - `lambda_C -> lambda_c`
  - `xi_C -> xi_c`
  - `zeta_C -> zeta_c`
  - `kappa_C -> kappa_c`
  - `dt -> dt`
  - `potential.type -> constitutive_profile.potential.type`
  - `potential.params -> constitutive_profile.potential.params`
- Implemented source-derived `budget_b` only when:
  - `compile.mass_normalization.mode == target_mass`
  - and a numeric `target` is present
- Implemented geometry-hint normalization:
  - `euclidean -> source_chart: planar_hint`
  - `periodic_torus -> source_chart: planar_periodic_hint`
  - periodic geometry sets `geometry_hints.periodicity`
  - full source geometry remains preserved under `extensions.source_pde.geometry`
- Implemented transport-intent translation conservatively:
  - no transport intent when `initial_flux` is disabled and channel-free
  - channelized source transport becomes `SeedTransportIntent` records
  - valley channels bind `carrier_id` to a matching translated valley when possible
- Hardened translation edge cases at the source boundary:
  - reject non-positive ridge radius ordering before seed construction
  - detect `unit_box` scale with floating-point tolerance rather than strict equality
  - snap quadrant-axis trigonometric hints to exact `0.0` / `1.0` / `-1.0`
  - reject unsupported `initial_flux.direction` values explicitly
  - reject ambiguous valley-carrier resolution instead of silently dropping `carrier_id`
  - reject whitespace-only source identifiers explicitly
  - deep-copy extension payloads so translated seeds do not alias source objects
- Preserved source-side metadata at the correct boundary:
  - `extensions.source_pde.meta`
  - `extensions.source_pde.compile`
  - `extensions.source_pde.potential_compile_policy`
  - `extensions.source_pde.initial_flux`
- Derived `depth_hint` for translated basins from the source parent chain.
- Explicitly deferred from Iteration 5 to Iteration 6:
  - routing-hub / saddle-like annotation
  - plateau inference
  - semantic-enrichment mode beyond rejecting non-default translation mode

### Verification

- [x] Representative PDE source specs translate programmatically
- [x] Default translation does not synthesize enrichment-only primitives
- [x] Source provenance is preserved explicitly

- Focused verification executed with:
  - `./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_seed_types tests.landscapes.test_seed_validation tests.landscapes.test_seed_io tests.landscapes.test_pde_translation tests.landscapes.test_pde_equivalence`
- Added focused translation coverage in:
  - `tests/landscapes/test_pde_translation.py`
- Added focused translation-equivalence coverage in:
  - `tests/landscapes/test_pde_equivalence.py`
- Added executable seed-layer equivalence validation in:
  - `src/pygrc/landscapes/equivalence.py`
- Recorded the mathematical-claim boundary in:
  - `implementation/PDEToGRCLMathematicalEquivalenceChecklist.md`
- Verified translation behavior includes:
  - conservative explicit-primitive mapping
  - constitutive-profile normalization
  - periodic geometry-hint mapping
  - source compile metadata preservation
  - source potential-compile-policy preservation
  - transport-intent channel translation
  - no default synthesis of `saddle` or `plateau`
  - executable checking of seed-layer mathematical invariants against PDE source
  - early rejection of malformed source geometry / direction / carrier ambiguity
  - extension isolation from later source mutation

### Summary

Implemented the first conservative PDE landscape translator with explicit basin,
ridge, and valley mapping into normalized seeds. The translator now preserves
source provenance and compile-only metadata at the seed boundary, derives basin
depth hints, maps transport intent without injecting runtime flux, and keeps
semantic enrichment explicitly out of the default path.

## Iteration 6. Source-Implied Structures And Translation Notes

### Goal

Implement conservative handling for source-implied semantics such as routing hubs.

### Checks

- [x] Implement annotation support for source-implied roles
- [x] Detect and annotate saddle-like routing hubs conservatively
- [x] Keep plateau inference disabled by default
- [x] Record translation notes for nontrivial interpretations
- [x] Decide whether enrichment mode is represented in code now or deferred

### Implementation Notes

- `cell-4` is the key representative case for this iteration.
- The default path should annotate implied structure rather than inventing explicit `saddle` primitives.
- Any enrichment mode must be opt-in and clearly separated from conservative translation.
- Implemented a post-translation interpretation pass in `src/pygrc/landscapes/pde_translation.py`
  so source-implied semantics are layered on after explicit primitive mapping.
- Conservative routing-hub handling now:
  - preserves the hub as `type: basin`
  - preserves attached channels as `type: valley`
  - annotates the hub under `primitive.extensions.source_pde`
    with:
    - `implied_role: saddle_like_hub`
    - `implied_structure.outgoing_valley_ids`
    - `implied_structure.incoming_valley_ids`
    - `implied_structure.owned_ridge_ids`
- Nontrivial interpretation is now recorded in both:
  - `meta.translation_notes`
  - `extensions.source_pde.translation_notes`
- Plateau inference remains disabled by default:
  - no `plateau` primitives are synthesized from source composition
- Added conservative passthrough support for explicit source-authentic:
  - `type: plateau -> PlateauSeedPrimitive`
  - `type: saddle -> JunctionSeedPrimitive(type=\"saddle\")`
  - `type: junction -> JunctionSeedPrimitive(type=\"junction\")`
- Explicit source passthrough remains distinct from enrichment:
  - explicit `plateau` / `saddle` are accepted and preserved
  - inferred `plateau` / `saddle` synthesis still does not occur in lossless mode
- Enrichment-mode decision for Phase L:
  - `semantic_enrichment` remains explicitly deferred
  - non-default translation mode requests are rejected rather than half-supported
- Added a representative `cell-4`-like routing example in:
  - `tests/landscapes/pde_source_examples.py`

### Verification

- [x] Conservative translation records implied routing semantics without changing primitive class
- [x] Translation notes are present when interpretation occurs
- [x] No silent enrichment happens in default mode

- Focused verification executed with:
  - `./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_seed_types tests.landscapes.test_seed_validation tests.landscapes.test_seed_io tests.landscapes.test_pde_translation tests.landscapes.test_pde_equivalence`
- Added focused Iteration 6 coverage in:
  - `tests/landscapes/test_pde_translation.py`
- Verified Iteration 6 behavior includes:
  - conservative annotation of a `cell-4`-like routing hub as `saddle_like_hub`
  - conservative passthrough of explicit source `plateau` and `saddle`
  - translation notes when implied structure is recognized
  - no synthesized `saddle` or `plateau` primitives in lossless mode
  - explicit rejection of `semantic_enrichment` requests while deferred

### Summary

Implemented conservative source-implied structure handling for PDE-to-seed
translation. Routing hubs are now annotated rather than reified into new neutral
primitives, translation notes capture the interpretation, plateau inference
remains disabled, explicit source `plateau` / `saddle` now pass through as
source-authentic neutral primitives, and semantic enrichment stays explicitly
deferred for a later phase.

## Iteration 7. Canonical Fixture Verification

### Goal

Verify translator behavior against the canonical `cell-1`, `cell-4`, and `s6` seed fixtures.

### Checks

- [x] Load the canonical seed fixtures under `configs/landscapes/seed/`
- [x] Compare translated `cell-1` output against fixture
- [x] Compare translated `cell-4` output against fixture
- [x] Compare translated `s6` output against fixture
- [x] Decide and document the fixture comparison strategy
- [x] Add landscape-fixture tests under `tests/landscapes/`

### Implementation Notes

- Fixture verification should test the translator, not just the fixture parser.
- Comparison strategy should be stable and readable:
  - object-based or normalized-dict-based is likely better than brittle raw-text comparison
- Any intentional fixture update should require an explicit code/doc/test change.
- Chosen comparison rule:
  - normalized runtime object equality or normalized-dict equality
  - not raw YAML text equality
- Added exact fixture-aligned PDE source examples in:
  - `tests/landscapes/pde_source_examples.py`
    for:
    - `cell-1`
    - `cell-4`
    - `s6-periodic-seam-ring`
- Added canonical fixture verification tests in:
  - `tests/landscapes/test_fixture_alignment.py`
- Fixture verification compares:
  - `landscape_seed_to_data(load_landscape_seed(fixture))`
  - against `landscape_seed_to_data(translate_pde_landscape_data(source))`
- Updated `configs/landscapes/seed/cell-4.seed.yaml` so the canonical fixture
  matches the current executable conservative-routing annotation contract.
- Recorded the comparison rule in:
  - `configs/landscapes/seed/README.md`

### Verification

- [x] Translator output matches canonical fixture expectations
- [x] Fixture drift is detected by tests
- [x] Representative landscape families are covered

- Focused verification executed with:
  - `./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_seed_types tests.landscapes.test_seed_validation tests.landscapes.test_seed_io tests.landscapes.test_pde_translation tests.landscapes.test_pde_equivalence tests.landscapes.test_fixture_alignment`
- Verified fixture coverage now includes:
  - `cell-1`
  - `cell-4`
  - `s6-periodic-seam-ring`

### Summary

Canonical seed fixtures are now executable test targets rather than prose-only
examples. Translator output is checked against `cell-1`, `cell-4`, and `s6`
through normalized runtime-data equality, and fixture drift is now caught by
tests.

## Iteration 8. Projector Boundary Closeout

### Goal

Define the implementation-facing handoff from normalized seeds to later family projectors.

### Checks

- [x] Decide what the seed runtime layer exposes to future projectors
- [x] Document the Phase L handoff boundary in implementation-facing terms
- [x] Confirm Phase L stops before family-specific realization logic
- [x] Verify no unresolved Phase L blockers remain for later family phases

### Implementation Notes

- This iteration should make later `GRCV3` / `GRC9` work easier without starting those projectors prematurely.
- If one projector protocol or adapter boundary is helpful, it should stay small and neutral.
- The main deliverable is clarity, not preemptive family logic.
- Chosen Iteration 8 boundary decision:
  - no code-level projector protocol is introduced in Phase L
  - later family phases should consume validated `LandscapeSeed`
  - raw YAML / raw PDE source payloads are not projector inputs
- Added the implementation-facing handoff doc:
  - `implementation/Phase-L-ProjectorBoundary.md`
- Updated the future-family handoff order in:
  - `implementation/Phase-5-Handoff.md`
  so later phases explicitly read:
  - the mathematical equivalence checklist
  - the Phase L implementation state
  - and the Phase L projector boundary
- Confirmed the Phase L stop line remains explicit:
  - Phase L owns seed meaning, validation, translation, and fixture verification
  - later family phases own substrate realization and projector policy

### Verification

- [x] The later-projector boundary is explicit enough for future phases
- [x] No family-specific seed consumption logic was accidentally pulled into Phase L

- Verification basis:
  - `implementation/Phase-L-ProjectorBoundary.md` defines the stable handoff
    surface and explicit non-goals
  - no new family-specific projector code was added under `src/pygrc/models/`
    or `src/pygrc/integrations/`
  - the landscape package remains neutral-seed-oriented

### Summary

Phase L now has an explicit later-projector boundary. Future family work is
expected to consume validated `LandscapeSeed` objects and the documented seed
surface rather than rediscovering the translation layer or pulling family
realization logic back into Phase L.

## Post-Phase Follow-On

Phase L closed with the neutral seed layer complete, but one practical gap
remained intentionally open:

- canonical seeds are validated and loadable,
- standalone `GRCV2` is executable,
- but there is not yet an end-to-end `LandscapeSeed -> GRCV2` execution path.

That gap is now tracked explicitly in:

- [`Phase-L1-ImplementationPlan.md`](./Phase-L1-ImplementationPlan.md)
- [`Phase-L1-ImplementationChecklist.md`](./Phase-L1-ImplementationChecklist.md)

Phase L therefore remains closed as the neutral bridge phase, while Phase L1
owns the first executable family realization from seed to runtime trajectory.
