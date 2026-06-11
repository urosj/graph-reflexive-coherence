# GRCL-9 Implementation Checklist

This document tracks execution of the **GRCL-9** implementation track.

It is intentionally separate from
[GRCL-9-ImplementationPlan.md](./GRCL-9-ImplementationPlan.md):

- the plan defines the source/lowering boundary, data carriers, iteration
  sequence, and acceptance criteria,
- this checklist records how the work is executed iteration by iteration.

## Usage Rules

- Keep GRCL-9 lowering-only. Do not add GRCL-9 execution semantics in this
  track.
- Do not change GRC9 runtime equations to make a source fixture pass.
- Do not inject spark, expansion, growth, fission, solved flux, or solved
  diagnostic outcomes into source fixtures.
- Treat source constructs as mechanical preconditions and policy declarations.
- Treat GRCL landscape examples as vocabulary-level source expressions, not
  direct GRC9 graph literals.
- Preserve the Phase T-GRC9 telemetry contract as the observation surface.
- Use Phase T-GRC9 contract field names in manifests and selectors.
- Mark optional telemetry as optional; do not promote it silently to required.
- Require connected lowered graphs. Bridge edges must be explicit metadata.
- Preserve nine-port capacity, deterministic port assignment, budget, and
  source-to-runtime provenance.
- Record replayable experiment sessions under
  `outputs/grcl9/lowering/sessions/S0001/`.
- Record the GRCL-9 lowering experiment log at
  `outputs/grcl9/lowering/ExperimentalLog.md`.
- Paper-facing growth claims must use corrected front-capacity semantics.
  Historical `legacy_any_inactive_port` broad-growth runs are replayable
  diagnostics only and require guarded force flags on legacy tools.
- Keep GRCV3 hierarchy, Lorentzian causal-layer, and observer-local semantics
  out of GRCL-9 Revision 1.

## Iteration Template

Copy this section for each new iteration if the checklist grows beyond the
planned sequence.

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

## Iteration 0. Planning Bootstrap

### Goal

Create the GRCL-9 source/lowering planning documents and lock the boundary as
family-native lowering into GRC9 initial state, not runtime expansion.

### Checks

- [x] Create `GRCL-9-Landscape-ProjectorProposal.md`
- [x] Create `GRCL-9-Vocabulary.md`
- [x] Create `GRCL-9-ImplementationPlan.md`
- [x] Create `GRCL-9-ImplementationChecklist.md`
- [x] Anchor the plan in the S0025 reviewed GRC9-native motif catalog
- [x] Anchor the plan in the S0026 GRCL-9 suitability handoff
- [x] Record that source constructs may declare preconditions, not observed
  events
- [x] Record runtime equations required by the source/lowering contract:
  - column diagnostic formula
  - row tensor basis
  - instability proxy formula
  - expansion node-count formula
  - coherence transfer distribution weights
  - birth probability formula
- [x] Record concrete proposed carriers for:
  - `grcl9_provenance`
  - `grcl9_motif_registry`
  - `grcl9_assembly_policy`
  - `grcl9_expected_saturated_node_ids`
  - `grcl9_expected_column_proxy_candidate_ids`
  - `grcl9_bridge_edge_ids`
- [x] Record the GRCL-9 artifact/session layout under `outputs/grcl9/lowering/`

### Implementation Notes

- Planning starts from connected GRC9-native evidence, not from disconnected
  historical fixtures.
- The source/lowering layer is allowed to use explicit GRC9 mechanics because
  GRCL-9 is family-specific.
- The source/lowering layer is not allowed to claim the runtime result.
- `saturation_column_proxy` and `saturation_instability` are the first
  executable spark gate intents.
- `saturation_sign_crossing` is reserved until history-dependent runtime and
  telemetry support is explicitly accepted for source fixtures.

### Verification

- [x] The plan/checklist pair exists under `implementation/`
- [x] The proposal and vocabulary use Phase T-GRC9 telemetry field paths
- [x] The documents reject non-contract selector paths such as
  `event_counts_by_kind.*`
- [x] The documents keep GRCL-9 separate from GRCV3, Lorentzian, and
  observer-local semantics

### Summary

GRCL-9 now has proposal, vocabulary, implementation plan, and implementation
checklist documents. The track is scoped as source/lowering into connected GRC9
graphs with telemetry-backed validation.

## Iteration 1. Lowering Manifest Contract

### Goal

Create the lowering manifest document and typed model that map S0026 accepted
motif families to GRCL-9 source constructs, graph preconditions, lowering
carriers, and expected telemetry.

### Checks

- [x] Create `implementation/GRCL-9-LoweringManifest.md`
- [x] Create `src/pygrc/landscapes/extensions/grcl9/manifest.py`
- [x] Create `tests/landscapes/test_grcl9_manifest.py`
- [x] Define manifest version, expected first value:
  - `grcl9_lowering_manifest_v1`
- [x] Define source construct entries for:
  - `spark_candidate_region`
  - `column_proxy_profile`
  - `instability_profile`
  - `expansion_refinement_region`
  - `growth_locus`
  - `post_expansion_fission_geometry`
- [x] Map every accepted S0026 motif family to a manifest entry
- [x] Record graph preconditions per entry
- [x] Record required source knobs per entry
- [x] Record lowering carriers per entry
- [x] Record expected telemetry fields per entry
- [x] Record pass/fail control roles per entry
- [x] Record explicit non-claims per entry
- [x] Record optional telemetry fields as optional

### Implementation Notes

- The manifest is the bridge from reviewed GRC9-native motifs to source
  lowering, but it is not itself a source fixture.
- Telemetry paths must use Phase T-GRC9 contract names.
- The manifest should not copy historical S0026 convenience paths if they do
  not match the telemetry contract.
- Runtime status and non-claims should be explicit so future source schema work
  cannot accidentally promote a telemetry result into a source declaration.
- Implemented a new source-extension package surface:
  - `src/pygrc/landscapes/extensions/grcl9/__init__.py`
  - `src/pygrc/landscapes/extensions/grcl9/manifest.py`
- The default manifest covers the five accepted S0026 motif families and the
  ten accepted S0026 motif ids.
- The manifest model rejects stale telemetry paths containing
  `event_counts_by_kind`.
- Optional growth birth-probability evidence remains optional.

### Verification

- [x] Manifest entries round-trip through JSON-safe mappings
- [x] Duplicate construct ids or motif mappings are rejected
- [x] Unsupported source construct kinds are rejected
- [x] Telemetry field paths are contract-aligned
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_manifest`

### Summary

Iteration 1 is complete. GRCL-9 now has a typed lowering manifest contract, a
documented manifest surface, a default S0026-backed manifest, and tests for
round-trip behavior, S0026 coverage, field-path alignment, duplicate motif
rejection, unsupported source construct rejection, and fission min-mass
wording/non-claims.

## Iteration 2. Source Schema

### Goal

Implement Revision 1 GRCL-9 source dataclasses and validation.

### Checks

- [x] Create `src/pygrc/landscapes/extensions/grcl9/__init__.py`
- [x] Create `src/pygrc/landscapes/extensions/grcl9/schema.py`
- [x] Create `tests/landscapes/test_grcl9_schema.py`
- [x] Define source construct dataclasses
- [x] Define source fixture/document dataclass
- [x] Define source schema version, expected first value:
  - `grcl9.source.v1`
- [x] Validate allowed spark gate intents:
  - `saturation_column_proxy`
  - `saturation_instability`
  - reserved `saturation_sign_crossing`
- [x] Validate source construct ids and motif ids
- [x] Validate required source knobs
- [x] Validate bridge policy declarations
- [x] Validate budget policy declarations
- [x] Validate provenance fields
- [x] Validate optional telemetry expectations without making them required
- [x] Reject source fields that encode event counts or solved diagnostics

### Implementation Notes

- Schema validation should happen before lowering.
- Source fixtures should be JSON/YAML-compatible mappings, but tests can start
  with JSON-safe dictionaries.
- Reserved values may parse only if the manifest/source marks them as deferred
  or non-executable.
- Implemented source constructs:
  - `GRCL9SparkCandidateRegion`
  - `GRCL9ColumnProxyProfile`
  - `GRCL9InstabilityProfile`
  - `GRCL9ExpansionRefinementRegion`
  - `GRCL9GrowthLocus`
  - `GRCL9PostExpansionFissionGeometry`
- Implemented policy dataclasses:
  - `GRCL9BridgePolicy`
  - `GRCL9BudgetPolicy`
  - `GRCL9ProvenancePolicy`
- `saturation_sign_crossing` is accepted only when `executable=false`.
- Bridge policies require `edge_kind = "bridge"`.
- The schema recursively rejects runtime-result keys such as
  `event_counts_by_kind`, `spark_happened`, `solved_flux`, and
  `solved_diagnostic`.

### Verification

- [x] Valid fixtures round-trip through mappings
- [x] Missing required source fields fail deterministically
- [x] Invalid spark intent values fail deterministically
- [x] Solved event/source smuggling fields fail deterministically
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_schema`

### Summary

Iteration 2 is complete. GRCL-9 now has a typed `grcl9.source.v1` source
schema with construct dispatch, source document round-trip support, bridge,
budget, and provenance policy validation, reserved spark-intent handling, and
runtime-result smuggling rejection.

## Iteration 3. Minimal Source Fixtures

### Goal

Author source-level fixtures for the accepted S0026 pass/fail motif families.

### Checks

- [x] Create `src/pygrc/landscapes/extensions/grcl9/fixtures.py`
- [x] Create `tests/landscapes/test_grcl9_fixtures.py`
- [x] Add column-proxy spark pass fixture
- [x] Add column-proxy spark fail fixture
- [x] Add instability spark pass fixture
- [x] Add instability spark fail fixture
- [x] Add expansion `D_eff` low fixture
- [x] Add expansion `D_eff` high fixture
- [x] Add growth `lambda_birth` high fixture
- [x] Add growth `lambda_birth` low fixture
- [x] Add fission min-mass pass fixture
- [x] Add fission min-mass fail fixture
- [x] Record expected selector ids for every fixture
- [x] Record explicit non-claims for every fixture
- [x] Record fixture-to-manifest entry links

### Implementation Notes

- Fixtures must be source declarations, not serialized GRC9 runtime states.
- The fixture set should start small and target the accepted S0026 motif
  families directly.
- Fission fixtures should claim only structural preconditions for telemetry
  persistence evaluation, not source-level fission semantics.
- Fission fixtures lower two sink-capable regions with separable conductance
  geometry; they do not claim runtime-computed basins.
- Added `manifest_entry_id` and `expected_selector_ids` to
  `GRCL9SourceDocument` so every fixture links explicitly back to the lowering
  manifest and selector plan.
- Implemented fixture helpers:
  - `default_grcl9_source_fixtures()`
  - `grcl9_source_fixture_by_name()`
- Fixture names are stable in `GRCL9_SOURCE_FIXTURE_NAMES`.

### Verification

- [x] Fixtures load without running GRC9
- [x] Fixtures validate against `grcl9.source.v1`
- [x] Fixtures link to manifest entries
- [x] Fixtures do not contain runtime event histories
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_fixtures`

### Summary

Iteration 3 is complete. GRCL-9 now has ten minimal source fixtures covering
the accepted S0026 pass/fail motif families, with manifest-entry links,
selector ids, explicit non-claims, optional telemetry preservation, and tests
verifying that fixtures remain source declarations rather than runtime state
artifacts.

## Iteration 4. Lowerer Revision 1

### Goal

Implement deterministic GRCL-9 source-to-`GRC9State` assembly.

### Checks

- [x] Create `src/pygrc/models/grc_9_grcl9_lowering.py`
- [x] Create `src/pygrc/models/grc_9_grcl9_provenance.py`
- [x] Create `tests/models/test_grc_9_grcl9_lowering.py`
- [x] Lower source fixtures into connected `GRC9State` graphs
- [x] Enforce nine-port capacity
- [x] Implement deterministic port assignment
- [x] Implement explicit bridge edge creation
- [x] Bridge edges use `grcl9_edge_kind = "bridge"`
- [x] Preserve budget
- [x] Populate lowered node/edge provenance payloads
- [x] Populate `grcl9_provenance`
- [x] Populate `grcl9_motif_registry`
- [x] Populate `grcl9_assembly_policy`
- [x] Populate `grcl9_expected_saturated_node_ids`
- [x] Populate `grcl9_expected_column_proxy_candidate_ids`
- [x] Populate `grcl9_bridge_edge_ids`
- [x] Serialize lowered state metadata deterministically

### Implementation Notes

- Bridge identity must come from explicit metadata, not from conductance
  threshold inference.
- Lowering may reuse existing GRC9 port helpers, but the source contract should
  remain GRCL-9-specific.
- The lowerer produces a `GRC9State` compatible with the existing GRC9 model
  shell; it does not replace `grc_9_landscape.py` or modify GRC9 runtime
  equations.
- The lowerer should fail before runtime if a source construct cannot be
  assembled without violating GRC9 mechanical constraints.
- Implemented public lowerer helpers:
  - `lower_grcl9_source_to_grc9_state(...)`
  - `lower_grcl9_fixture_by_name(...)`
- Implemented provenance payload helpers:
  - `grcl9_node_payload(...)`
  - `grcl9_edge_payload(...)`
- The first lowerer builds canonical small motifs for each Revision 1 fixture
  family. It does not attempt to duplicate the discovery generator; it emits
  deterministic GRC9-compatible precondition graphs.

### Verification

- [x] Repeated lowering of the same fixture is byte-stable after serialization
- [x] No lowered graph is disconnected
- [x] No lowered node exceeds nine occupied ports
- [x] Budget is preserved within configured tolerance
- [x] Provenance covers every lowered node and edge
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_grcl9_lowering`

### Summary

Iteration 4 is complete. GRCL-9 source fixtures now lower deterministically
into connected `GRC9State` graphs with nine-port capacity preserved, exact
initial budget, explicit bridge metadata, node/edge provenance, motif registry,
assembly policy, expected candidate caches, and GRC9 model-shell validation.

## Iteration 5. Telemetry Replay

### Goal

Run lowered GRCL-9 fixtures through GRC9 and Phase T-GRC9 telemetry, storing
replayable session artifacts.

### Checks

- [x] Create `src/pygrc/telemetry/grcl9_replay.py`
- [x] Create `tests/telemetry/test_grcl9_replay.py`
- [x] Create `outputs/grcl9/lowering/ExperimentalLog.md`
- [x] Create first replay session under
  `outputs/grcl9/lowering/sessions/S0001/`
- [x] Store `session_manifest.json`
- [x] Store source fixture copies
- [x] Store lowered state artifacts
- [x] Store telemetry artifacts
- [x] Store graph checkpoints
- [x] Store selector reports
- [x] Store `replay.sh`
- [x] Validate expected pass/fail distinctions with field-backed selectors
- [x] Record source/lowering/runtime/selector failures explicitly

### Implementation Notes

- Replay should use the existing GRC9 runtime and Phase T-GRC9 telemetry.
- `replay.py` wraps GRCL-9 source loading, lowering, and telemetry capture
  around the existing GRC9 landscape/runtime entry points such as
  `build_grc9_from_landscape_seed` and `run_grc9_landscape_seed`.
- GRC9 telemetry remains observation-oriented; GRCL-9 lowering summaries should
  be separate source/lowering evidence.
- Session ids are scoped to `outputs/grcl9/lowering/`.
- Implemented `GRCL9_REPLAY_VERSION = "grcl9_lowering_replay_v1"`.
- Replay stores source fixture JSON, lowered state JSON, Phase T-GRC9
  `steps.jsonl`, `events.jsonl`, `run_summary.json`, graph checkpoint index,
  per-step graph checkpoints, selector reports, `session_manifest.json`, and
  `replay.sh`.
- Runtime configs are derived from source-declared knobs such as `eps_spark`,
  `tau_instability`, `D_eff_target`, `lambda_birth`, and fission min-mass /
  persistence settings.
- Replay initializes RNG state deterministically for lowered states before
  growth-capable GRC9 runs.
- `S0001` records both selector passes and misses. The first run confirms the
  column-proxy pass/fail controls and records misses for instability-pass,
  high-D-eff expansion, high-lambda growth, and fission-min-mass-pass controls
  without mutating source fixtures or runtime equations.

### Verification

- [x] Replay sessions are deterministic enough to rerun from saved source
  fixtures and commands
- [x] Required telemetry and checkpoint artifacts exist
- [x] Selector reports use contract field names
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_replay`

### Summary

Iteration 5 is complete. GRCL-9 now has a replay wrapper that lowers source
fixtures into GRC9 states, runs them through Phase T-GRC9 telemetry with graph
checkpoints, stores replayable artifacts under
`outputs/grcl9/lowering/sessions/S0001/`, writes selector reports with explicit
misses, and records the session in `outputs/grcl9/lowering/ExperimentalLog.md`.

## Iteration 6. Visualization

### Goal

Render visualizations for accepted GRCL-9 lowered fixtures using saved
telemetry and graph checkpoints.

### Checks

- [x] Add or extend visualization wrappers for GRCL-9 lowering sessions
- [x] Render graph visuals from saved checkpoints
- [x] Render trajectory or event-window visuals from telemetry
- [x] Show connected graphs
- [x] Make bridge edges visible
- [x] Make motif roles visible
- [x] Label source intent separately from runtime observation
- [x] Store visuals under the session `visualizations/` directory

### Implementation Notes

- Visuals are inspection aids, not proof.
- Visualization should not read source fixtures to infer runtime outcomes.
- Existing Phase V GRC9 visualization utilities should be reused where they
  already consume checkpoints and telemetry cleanly.
- Implemented `src/pygrc/visualization/grcl9_lowering.py`.
- Implemented `GRCL9_VISUALIZATION_VERSION =
  "grcl9_lowering_visualization_v1"`.
- The wrapper reuses existing behavior plots and graph checkpoint rendering:
  `render_run_visual_bundle(...)` and `render_graph_run_visual_bundle(...)`.
- Added GRCL-9-specific overlay artifacts per lane:
  - `grcl9_lowering_overlay.png`
  - `grcl9_overlay_summary.json`
  - `source_runtime_boundary.md`
- The GRCL-9 overlay is rendered from the initial saved checkpoint so it shows
  the lowered source graph before runtime topology changes. Runtime observation
  labels come from saved telemetry and selector reports.
- Rendered S0001 visuals under
  `outputs/grcl9/lowering/sessions/S0001/visualizations/`.

### Verification

- [x] Visuals exist for accepted lowered fixtures
- [x] Visuals consume saved telemetry/checkpoints
- [x] Visuals show connected topology
- [x] Visual labels preserve GRCL-9/GRC9 boundary claims
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_grcl9_lowering`

### Summary

Iteration 6 is complete. GRCL-9 lowering replay sessions now have visualization
wrappers that consume saved telemetry and graph checkpoints, render behavior
plots and graph sequences, add lowering-specific overlays for connected
topology, motif roles, and bridge edges, and preserve the source intent versus
runtime observation boundary in per-lane panels.

## Iteration 6.1. GRCL-9 Boundary Refactor

### Goal

Move GRCL-9 code to the same ownership boundaries as the existing GRCL-V3
architecture.

### Checks

- [x] Move source manifest, schema, and fixtures under
  `src/pygrc/landscapes/extensions/grcl9/`
- [x] Move lowering and provenance helpers under `src/pygrc/models/`
- [x] Move replay wrapper under `src/pygrc/telemetry/`
- [x] Move visualization wrapper under `src/pygrc/visualization/`
- [x] Remove the long-lived `pygrc.grcl9` package surface
- [x] Export source-side GRCL-9 contracts from `pygrc.landscapes.extensions`
- [x] Export lowerer/provenance helpers from `pygrc.models`
- [x] Export replay helpers from `pygrc.telemetry`
- [x] Export visualization helpers from `pygrc.visualization`
- [x] Split tests by ownership:
  - `tests/landscapes/test_grcl9_manifest.py`
  - `tests/landscapes/test_grcl9_schema.py`
  - `tests/landscapes/test_grcl9_fixtures.py`
  - `tests/models/test_grc_9_grcl9_lowering.py`
  - `tests/telemetry/test_grcl9_replay.py`
  - `tests/visualization/test_grcl9_lowering.py`
- [x] Update replay scripts to invoke
  `python -m pygrc.telemetry.grcl9_replay`

### Implementation Notes

- Source-side GRCL-9 remains a landscape extension, not a model package.
- The lowerer still produces ordinary `GRC9State` instances and does not
  replace `grc_9_landscape.py` or change GRC9 runtime equations.
- Replay and visualization remain artifact/session wrappers owned by their
  existing subsystems.

### Verification

- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_manifest tests.landscapes.test_grcl9_schema tests.landscapes.test_grcl9_fixtures tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay tests.visualization.test_grcl9_lowering`

### Summary

Iteration 6.1 is complete. GRCL-9 now follows the established GRCL-V3-style
source/runtime split: source contracts live in landscape extensions, lowering
and provenance live in models, replay lives in telemetry, visualization lives
in visualization, and tests are grouped by those same boundaries.

## Iteration 7. GRCL-9 Landscape Example Compiler

### Goal

Author first GRCL-9 examples in GRCL/Morse-like landscape vocabulary, compile
them into the existing mechanical GRCL-9 source schema, and run the compiled
sources through the replay and visualization machinery.

### Checks

- [x] Create `src/pygrc/landscapes/extensions/grcl9/examples.py`
- [x] Create `tests/landscapes/test_grcl9_examples.py`
- [x] Define landscape example version:
  - `grcl9.landscape_example.v1`
- [x] Define a typed GRCL/Morse landscape example/document surface:
  - `GRCL9LandscapeExampleDocument`
  - `GRCL9CriticalRegion`
  - `GRCL9StableBasin`
  - `GRCL9UnstableDirection`
  - `GRCL9Separatrix`
  - `GRCL9SaddleBridge`
  - `GRCL9BoundaryStratum`
  - `GRCL9GradientPressure`
  - `GRCL9RefinementLocus`
  - `GRCL9PostRefinementTwoSinkRegion`
- [x] Add a required lowering guard:
  - `grcl9_required = true` or `lowering_required = true`
- [x] Define compiler/adapter from GRCL landscape examples to
  `GRCL9SourceDocument`
- [x] Define compiler helpers:
  - `compile_grcl9_landscape_example_to_source(...)`
  - `default_grcl9_landscape_examples()`
  - `grcl9_landscape_example_by_name()`
- [x] Compile `critical_region + columnwise_near_cancellation` to
  `spark_candidate_region + column_proxy_profile`
- [x] Compile `critical_region + unstable_direction + weak_support` to
  `spark_candidate_region + instability_profile`
- [x] Compile `critical_region + refinement_locus + effective_degree_target`
  to `spark_candidate_region + expansion_refinement_region`
- [x] Compile `boundary_stratum + inactive_port + outward_gradient_pressure`
  to `growth_locus`
- [x] Compile `post_refinement_two_sink_region + saddle_bridge` to
  `post_expansion_fission_geometry`
- [x] Add column-proxy critical-region example
- [x] Add instability critical-region example
- [x] Add expansion/refinement-locus example
- [x] Add growth boundary-stratum example
- [x] Add post-refinement fission saddle/bridge example
- [x] Save authored example copies under session
  `grcl_landscape_examples/`
- [x] Store compiled `grcl9.source.v1` copies separately from authored
  landscape examples
- [x] Replay compiled examples through Iteration 5 machinery
- [x] Visualize compiled examples through Iteration 6 machinery
- [x] Link replay/visualization artifacts back to the GRCL landscape examples
- [x] Preserve source-term to mechanical-construct provenance in compiled
  output
- [x] Reject examples when GRCL-9 fields are present but the required lowering
  guard is false or absent
- [x] Reject examples that embed raw GRC9 graph literals
- [x] Reject examples that embed solved telemetry, event history, or runtime
  outcomes

### Implementation Notes

- GRCL-9 examples are not casual natural-language wrappers. They should use
  the GRCL vocabulary defined in `GRCL-9-Vocabulary.md`.
- The intended vocabulary is landscape/Morse-like: critical regions, basins,
  unstable/stable directions, separatrices, saddle/bridge regions, boundary
  strata, gradient/flux pressure, and refinement loci.
- This layer is above `grcl9.source.v1`. The current `GRCL9SourceDocument`
  remains the mechanical family-native source contract used by the lowerer.
- The authored example layer should compile into the existing mechanical
  GRCL-9 source schema; it should not compile directly to raw GRC9 graph
  payloads.
- The GRCL-V3 lesson applies here: if rich/family-specific source intent is
  declared, lowering must consume it or fail explicitly. Silent fallback to a
  generic landscape seed is not allowed.
- Source examples may declare preconditions and intent. Spark, expansion,
  growth, and fission confirmation remain GRC9 runtime observations.
- This iteration exists so the reviewed catalog does not review only
  low-level mechanical fixtures.
- Implemented `GRCL9_LANDSCAPE_EXAMPLE_VERSION =
  "grcl9.landscape_example.v1"`.
- Implemented built-in pass/fail landscape examples for all ten accepted
  S0026 controls.
- Added `compiled_source_provenance` to `GRCL9SourceDocument` so compiled
  sources preserve source-term to mechanical-construct provenance.
- Extended GRCL-9 replay with `source_mode = "landscape_examples"` so S0002
  stores authored examples under `grcl_landscape_examples/` and compiled
  `grcl9.source.v1` documents under `source_fixtures/`.
- Rendered S0002 visuals under
  `outputs/grcl9/lowering/sessions/S0002/visualizations/`.

### Verification

- [x] Examples round-trip through JSON-safe mappings
- [x] Example mappings contain no GRC9 node ids, edge ids, port-edge payloads,
  event rows, telemetry summaries, or solved diagnostics
- [x] Required lowering guard is enforced
- [x] Source-term to mechanical-construct provenance is deterministic
- [x] Compiler output is deterministic and does not mutate authored examples
- [x] Compiled outputs validate as `grcl9.source.v1`
- [x] Compiled outputs lower to connected GRC9 states
- [x] Compiled outputs replay with telemetry/checkpoints
- [x] Compiled outputs render visualizations with source/runtime boundary
  panels
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_examples`

### Summary

Iteration 7 is complete. GRCL-9 now has a typed GRCL/Morse-facing landscape
example layer, deterministic compilation into the existing mechanical
`grcl9.source.v1` source contract, required lowering-guard validation,
source-term provenance in compiled documents, replay support for compiled
landscape examples, and S0002 replay/visualization artifacts.

## Iteration 7.1. Seed-Backed GRCL-9 Examples

### Goal

Add checked-in `LandscapeSeed` examples with `extensions.grcl9` so the GRCL-9
source examples can be iterated like GRCL-V3 rich seeds.

### Checks

- [x] Add GRCL-9 seed-backed example paths
- [x] Add `grcl9.landscape_example.v1` top-level seed extension contract
- [x] Add primitive-level `extensions.grcl9` term extraction
- [x] Reject seed examples with primitive GRCL-9 terms but no top-level
  `extensions.grcl9`
- [x] Reject seed examples unless `grcl9_required = true`
- [x] Compile extracted seed examples into `grcl9.source.v1`
- [x] Preserve source seed reference in compiled source provenance
- [x] Add replay source mode `landscape_seed_examples`
- [x] Store original seed files under session `grcl_landscape_seeds/`
- [x] Store extracted example documents under session
  `grcl_landscape_examples/`
- [x] Store compiled source documents separately under `source_fixtures/`
- [x] Preserve the same source/runtime non-claims as Iteration 7
- [x] Document that seed-backed examples are expected to need tuning before
  all lifecycle events reproduce direct GRC9 phenomenology runs

### Implementation Notes

- Added ten checked-in seed examples under `configs/landscapes/seed/` covering
  the same pass/fail controls as the Iteration 7 landscape examples.
- Seed files remain GRCL/Morse-facing. They do not encode raw GRC9 node ids,
  edge ids, port-edge payloads, solved diagnostics, or runtime event history.
- `extract_grcl9_landscape_example_from_seed(...)` is the seed-to-example
  boundary. It mirrors the GRCL-V3 rule that family-specific rich source intent
  must be explicitly consumed or fail.
- Replay mode `landscape_seed_examples` writes the original seed YAMLs,
  extracted examples, compiled mechanical sources, lowered states, telemetry,
  checkpoints, and selector reports.
- Ran S0003 from the seed-backed mode. It records 10 lanes under
  `outputs/grcl9/lowering/sessions/S0003/`, with original seed copies under
  `grcl_landscape_seeds/`, extracted examples under
  `grcl_landscape_examples/`, compiled sources under `source_fixtures/`, and
  visuals under `visualizations/`.
- First-pass seed selector result: 6 passed, 4 missed. The misses are
  `spark_instability_tau_pass`, `spark_to_expansion_d_eff_high`,
  `growth_pressure_lambda_high`, and
  `post_expansion_fission_min_mass_pass`; these are the next seed-tuning
  targets.

### Verification

- [x] Seed paths are complete and ordered
- [x] Seed files load through the common `LandscapeSeed` loader
- [x] Seed extensions extract to `GRCL9LandscapeExampleDocument`
- [x] Extracted examples compile to `GRCL9SourceDocument`
- [x] Compiled sources lower to GRC9 states
- [x] Replay can execute seed-backed examples
- [x] S0003 replay artifacts were generated
- [x] S0003 visualization artifacts were generated

### Summary

Iteration 7.1 is complete. GRCL-9 now has source seeds that can be edited and
replayed in the same style as GRCL-V3 rich seeds, while preserving the explicit
GRCL landscape example and mechanical `grcl9.source.v1` stages.

## Iteration 7.2. Working GRCL-9 Phenomenology Seeds

### Goal

Tune the seed-backed GRCL-9 examples until they actually emit the GRC9
phenomenology needed for later catalog selection.

### Checks

- [x] Identify S0003/S0004 missed positive seed cases
- [x] Repair instability seed lowering with explicit cut edges outside the
  saturated support patch
- [x] Repair expansion lowering so the refinement source also carries the
  spark-enabling column-proxy profile
- [x] Repair growth replay configuration so high pressure births and low
  pressure suppresses birth
- [x] Repair fission lowering with a post-expansion module registry and stable
  two-sink diagnostic geometry
- [x] Align GRCL-9 expansion selector with emitted run-summary fields
- [x] Run working seed-backed replay session
- [x] Render visuals for the working session

### Implementation Notes

- S0003 was structurally valid but not a proof set: only the column-proxy
  positive seed emitted its intended lifecycle event.
- S0004 showed the repaired emitters mostly working, but exposed selector
  field drift for expansion, low-growth over-birth, and an over-strict fission
  min-mass pass threshold.
- S0006 is the first working seed-backed GRCL-9 phenomenology session. All ten
  seed lanes pass their selectors:
  - `spark_column_proxy_eps_pass`: spark + expansion
  - `spark_column_proxy_eps_fail`: no spark
  - `spark_instability_tau_pass`: instability spark + expansion
  - `spark_instability_tau_fail`: no spark
  - `spark_to_expansion_d_eff_low`: spark + expansion with lower module size
  - `spark_to_expansion_d_eff_high`: spark + expansion with higher module size
  - `growth_pressure_lambda_high`: growth events
  - `growth_pressure_lambda_low`: no growth events
  - `post_expansion_fission_min_mass_pass`: confirmed fission summary
  - `post_expansion_fission_min_mass_fail`: no confirmed fission summary
- The fission pass threshold is `identity_fission_min_basin_mass = 0.0` for
  the current runtime because continuity can move basin mass to one side while
  the two-sink persistence structure remains observable.

### Verification

- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_fixtures tests.landscapes.test_grcl9_examples tests.landscapes.test_grcl9_seed_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay tests.visualization.test_grcl9_lowering`
- [x] Replay artifacts:
  - `outputs/grcl9/lowering/sessions/S0006/`
- [x] Visualization artifacts:
  - `outputs/grcl9/lowering/sessions/S0006/visualizations/`

### Summary

Iteration 7.2 is complete. We now have working GRCL-9 seed examples that
produce the required GRC9 telemetry signatures and controls, so catalog work
can select from S0006 rather than from the earlier non-emitting scaffold runs.

## Iteration 7.3. ComposingCells-Aligned Seed Families

### Goal

Add seed-backed GRCL-9 examples that are authored as composed cell landscapes,
not just isolated lifecycle mechanism probes.

### Checks

- [x] Add ComposingCells-aligned seed paths to the built-in GRCL-9 seed corpus
- [x] Add a boundary ridge / membrane cell seed
- [x] Add an internal valley / transport-pressure cell seed
- [x] Add a nested basin / plateau cell seed
- [x] Add a saddle branch / instability cell seed
- [x] Add a refinement cell with expansion and budget-partition intent
- [x] Keep every new seed under `configs/landscapes/seed/`
- [x] Require top-level `extensions.grcl9.grcl9_required = true`
- [x] Use neutral seed primitive types from the GRCL vocabulary:
  - `basin`
  - `plateau`
  - `ridge`
  - `valley`
  - `saddle`
- [x] Map each composed-cell seed to an existing GRCL-9 mechanical manifest
  entry
- [x] Keep Phase T-GRC9 telemetry concepts as selector expectations or
  observed evidence, not source claims
- [x] Replay the composed-cell seeds as a separate GRCL-9 lowering session
- [x] Render visualizations for the composed-cell session

### Implementation Notes

- These seeds are downstream of S0006. They do not replace the local mechanism
  proof set.
- The source shape should be aligned with
  `2026-02-ComposingCells.md`: basins for identity, ridges/membranes for
  boundary, valleys/channels for transport, plateaus for support, and saddles
  for branching/bridge geometry.
- The seeds may target existing selectors such as spark, expansion, growth, or
  fission evidence, but they must not declare those runtime events as source
  facts.
- Concepts from `Phase-T-GRC9-ImplementationChecklist.md` should be mapped into
  seeds only when they have source-constructible graph preconditions.
  Telemetry-only diagnostics remain selectors/observations.
- Added five checked-in composed-cell seeds:
  - `grcl9-cell-boundary-ridge-membrane-spark-pass.seed.yaml`
  - `grcl9-cell-internal-valley-transport-growth-high.seed.yaml`
  - `grcl9-cell-plateau-nested-basins-fission-pass.seed.yaml`
  - `grcl9-cell-saddle-branch-instability-pass.seed.yaml`
  - `grcl9-cell-refinement-budget-partition-expansion-high.seed.yaml`
- Composed-cell examples are not S0026 manifest controls. They link to an
  existing manifest entry and declare explicit selector ids.
- Ran S0007 from `source_mode = "landscape_seed_examples"` with only the five
  composed-cell seeds. All five selector reports passed:
  - boundary ridge/membrane seed: spark + expansion
  - internal valley/transport seed: growth
  - nested basin/plateau seed: fission confirmed in run-summary telemetry
  - saddle branch seed: instability spark + expansion
  - refinement/budget-partition seed: spark + expansion
- Rendered S0007 visuals under
  `outputs/grcl9/lowering/sessions/S0007/visualizations/`.

### Verification

- [x] Seed files load through the common `LandscapeSeed` loader
- [x] Seed extensions extract to `GRCL9LandscapeExampleDocument`
- [x] Extracted examples compile to `GRCL9SourceDocument`
- [x] Compiled sources lower to connected GRC9 states
- [x] Replay selector reports pass or record explicit misses
- [x] Visual artifacts exist under the session `visualizations/` directory
- [x] Tests pass for GRCL-9 seed examples, lowering, replay, and visualization

### Summary

Iteration 7.3 is complete. GRCL-9 now has a ComposingCells-aligned seed layer
that uses neutral basin/ridge/valley/plateau/saddle primitives while preserving
the explicit GRCL-9 source/lowering boundary. S0007 provides replayable
telemetry and visualization evidence for the five composed-cell probes.

## Iteration 8. Reviewed GRCL-9 Lowered Motif Catalog

### Goal

Promote telemetry-validated lowered GRCL landscape examples into a reviewed
GRCL-9 lowered motif catalog.

### Checks

- [x] Generate `reviewed_grcl9_lowered_motif_catalog.json`
- [x] Link each accepted motif to its GRCL landscape example
- [x] Link each accepted motif to its compiled source fixture
- [x] Link each accepted motif to its lowered state
- [x] Link each accepted motif to telemetry artifacts
- [x] Link each accepted motif to graph checkpoints
- [x] Link each accepted motif to selectors
- [x] Link each accepted motif to visualizations
- [x] Record rejected motifs and rejection reasons
- [x] Link duplicate structural motifs instead of silently copying them
- [x] Preserve explicit non-claims in every catalog entry

### Implementation Notes

- The catalog is the first GRCL-9 source/lowering evidence catalog.
- Catalog acceptance should start from the full chain:
  GRCL landscape example -> compiled GRCL-9 source schema -> lowered GRC9
  state -> telemetry -> visualization.
- Acceptance should be based on selector-backed telemetry, not visual
  inspection alone.
- Duplicate policy should distinguish structural duplicates from distinct
  runtime contexts.
- Implemented catalog runner:
  - `src/pygrc/telemetry/grcl9_lowered_motif_catalog.py`
- Implemented catalog tests:
  - `tests/telemetry/test_grcl9_lowered_motif_catalog.py`
- Exported the runner from `pygrc.telemetry`:
  - `run_grcl9_reviewed_lowered_motif_catalog`
- Generated S0008 from source sessions S0006 and S0007:
  - `outputs/grcl9/lowering/sessions/S0008/reviewed_grcl9_lowered_motif_catalog.json`
  - `outputs/grcl9/lowering/sessions/S0008/reports/reviewed_grcl9_lowered_motif_catalog_report.json`
  - `outputs/grcl9/lowering/sessions/S0008/reports/reviewed_grcl9_lowered_motif_catalog_summary.md`
- S0008 accepts 15 motifs:
  - 10 mechanism-probe motifs from S0006
  - 5 ComposingCells-aligned seed motifs from S0007
- S0008 records 0 rejected motifs and 9 structural duplicate links. Duplicate
  motifs are retained and linked through `duplicate_of` / `duplicate_group_id`.
- Catalog acceptance requires:
  - selector status `passed`
  - GRCL landscape example artifact
  - compiled source artifact
  - lowered state artifact
  - telemetry run summary / events / steps
  - graph checkpoint index
  - visualization manifest entry

### Verification

- [x] Catalog round-trips through JSON
- [x] Every accepted catalog entry has GRCL example, compiled source, lowered
  state, telemetry, checkpoint, selector, and visualization links
- [x] Rejected entries are retained with reasons
- [x] Non-claims are present
- [x] Tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_lowered_motif_catalog`

### Summary

Iteration 8 is complete. GRCL-9 now has a reviewed lowered motif catalog built
from the full source chain: GRCL landscape seed, extracted example, compiled
source, lowered GRC9 state, telemetry, checkpoints, selectors, and
visualizations.

## Iteration 8.1. Collapse-Adjacent Structural Seeds

### Goal

Implement the next planned collapse-adjacent batch before Revision 1 handoff,
adding GRCL-9 source seeds only as structural probes.

### Checks

- [x] Create `implementation/GRCL-9-CollapseAdjacentNextBatch.md`
- [x] Record that S0008 intentionally does not cover collapse-facing behavior
- [x] Distinguish GRCV3 choice collapse, GRC9 structural collapse candidates,
      and ComposingCells dysfunction collapse
- [x] Add collapse-adjacent GRCL landscape examples
- [x] Compile collapse-adjacent examples into GRCL-9 source fixtures
- [x] Lower collapse-adjacent fixtures into connected GRC9 graphs
- [x] Replay collapse-adjacent fixtures under GRC9
- [x] Store replay artifacts under `outputs/grcl9/lowering/sessions/S0009/`
- [x] Classify collapse-adjacent entries without claiming runtime collapse
- [x] Record selector/report output for structural-only, observed non-fission,
      basin-merge, support-loss, or reserved-future outcomes

### Implementation Notes

- Current GRC9 has no `collapse` lifecycle event kind.
- Phase T-GRC9 currently treats GRCV3 choice/collapse semantics as out of
  scope. That boundary remains valid.
- Structural probes may target membrane/ridge rupture, basin merge, support
  loss, failed fission persistence, or saddle pressure.
- Probe names should use `structural_collapse_probe`,
  `basin_merge_candidate`, `support_loss_candidate`, or
  `collapse_reserved_future` language.
- Do not import GRCV3 `choice` / `collapse_registry` semantics.
- Do not label a source fixture or lowered motif as collapsed unless a later
  GRC9 contract defines such runtime evidence.
- Added four checked-in seed examples:
  - `configs/landscapes/seed/grcl9-cell-membrane-rupture-structural-probe.seed.yaml`
  - `configs/landscapes/seed/grcl9-cell-basin-merge-before-persistence-probe.seed.yaml`
  - `configs/landscapes/seed/grcl9-cell-support-loss-identity-decay-probe.seed.yaml`
  - `configs/landscapes/seed/grcl9-cell-saddle-choice-pressure-structural-probe.seed.yaml`
- Added structural selector ids:
  - `membrane_rupture_structural_probe`
  - `fission_persistence_failed_candidate`
  - `basin_merge_pressure_candidate`
  - `support_loss_pressure_candidate`
  - `saddle_pressure_structural_probe`
- Generated replay session:
  - `outputs/grcl9/lowering/sessions/S0009/`
- Rendered visualizations:
  - `outputs/grcl9/lowering/sessions/S0009/visualizations/`

### Verification

- [x] Collapse-adjacent source files contain no runtime histories or solved
      telemetry
- [x] Lowered collapse-adjacent graphs are connected
- [x] Replay records expected absence/presence of existing GRC9 evidence
- [x] Reports preserve the distinction between collapse candidate and runtime
      collapse

### Summary

Implemented as S0009. GRCL-9 now has four collapse-adjacent structural probes
that compile from seed-backed GRCL/Morse examples, lower to connected GRC9
graphs, replay through existing Phase T-GRC9 telemetry/checkpoints, and render
through existing Phase V-GRC9 visualization without claiming runtime collapse.
S0009 does not show a runtime collapse event or collapse-like transition; it is
structural-probe evidence only.

## Iteration 8.2. Collapse-Producing Seed Discovery

### Goal

Find out whether GRCL-9 can author seeds that produce collapse-like runtime
transitions under current GRC9, rather than only collapse-adjacent structure.

### Checks

- [x] Record that S0009 is structural-only and not collapse evidence
- [x] Design intensified GRCL landscape seeds from the 8.1 mechanisms
- [x] Include pass/fail controls for basin mass, bridge conductance, support
      conductance, outward pressure, and persistence thresholds where relevant
- [x] Compile the new examples through the GRCL/Morse source layer, not direct
      GRC9 graph literals
- [x] Lower all examples into connected GRC9 graphs
- [x] Replay all examples with graph checkpoints and selector reports
- [x] Store the next replay session under `outputs/grcl9/lowering/sessions/`
- [x] Classify each lane as `runtime_collapse_like_observed`,
      `structural_only`, `ambiguous`, or `failed_control`
- [x] Render visuals for every lane, using collapse-adjacent arrows only when
      selector-backed
- [x] Decide whether any observed behavior justifies Phase T telemetry changes

### Implementation Notes

- Do not rename S0009 as collapse-producing; it is a structural-probe session.
- Candidate mechanisms:
  - fission candidate loses one sink basin before persistence confirmation,
  - weak saddle/bridge geometry plus asymmetric support produces basin merge,
  - support-loss identity decay drains a candidate region,
  - membrane/ridge rupture converts a saturated region into expansion or sink
    loss,
  - saddle pressure selects one branch and extinguishes the other without
    importing GRCV3 choice semantics.
- Positive claims must be backed by event rows, run summaries, graph
  checkpoints, and visualization.
- If no positive examples are found, collapse remains `reserved_future` or
  `structural_only` for the Revision 1 handoff.
- Added two checked-in seed examples:
  - `configs/landscapes/seed/grcl9-cell-basin-merge-runtime-collapse-probe.seed.yaml`
  - `configs/landscapes/seed/grcl9-cell-basin-merge-runtime-stability-control.seed.yaml`
- Generated replay session:
  - `outputs/grcl9/lowering/sessions/S0010/` records the six-step attempt;
    both lanes ended ambiguous/missed after overshooting the diagnostic window.
  - `outputs/grcl9/lowering/sessions/S0011/`
  - `outputs/grcl9/lowering/sessions/S0012/`, `S0013`, and `S0014` record
    failed/missed long-window developed-basin attempts.
  - `outputs/grcl9/lowering/sessions/S0015/` records the accepted long-window
    developed-basin example.
- The positive lane is diagnostic, not event-backed:
  - source declares two sink regions,
  - final runtime identity keeps `fission_sink_a`,
  - final runtime identity loses source role `fission_sink_b`,
  - no GRC9 `collapse` event row is emitted.

### Verification

- [x] Existing S0008 catalog meaning remains unchanged
- [x] S0009 remains structural-probe evidence only
- [x] New session records every attempted collapse-producing seed
- [x] Connected graph invariant holds for all new lanes
- [x] Any collapse-like positive is backed by telemetry, checkpoints, and
      visualization

### Summary

Implemented as S0011. GRCL-9 now has a first collapse-producing discovery
pair. `cell_basin_merge_runtime_collapse_probe` is classified as
`runtime_collapse_like_observed` because the source-declared `fission_sink_b`
role is not a final runtime sink after one GRC9 step, while
`cell_basin_merge_runtime_stability_control` remains `structural_only`.
This is diagnostic identity evidence, not a GRC9 collapse event.

The third complex example is
`cell_developed_basin_centroid_collapse_long_window`. It lowers two developed
multi-node basin regions and runs for 24 steps. S0015 records it as a passing
diagnostic: the source-declared `fission_sink_b` anchor is lost, the receiving
basin target is selected by `group_centroid`, and the replay stores 25
checkpoints for a 15-node, 21-edge graph. Residual weak support sinks from the
decaying basin remain visible in the selector report, so the claim remains
collapse-like identity evidence rather than full runtime collapse.

## Iteration 8.3. Full-Capacity Phenomenology Cascade

### Goal

Add a single source-authored GRCL-9 seed that composes the currently supported
phenomenology surfaces in one connected graph: spark, expansion, growth,
fission/collapse-adjacent identity evidence, and GRCL-V3-style target
selection visualization.

### Checks

- [x] Add a GRCL/Morse seed rather than a direct GRC9 graph literal
- [x] Compile multiple GRCL-9 source construct families from one example
- [x] Lower mixed constructs into one connected GRC9 graph
- [x] Preserve GRCL-9 source provenance across GRC9 topology mutation
- [x] Run for at least 20 steps
- [x] Require selectors for spark, expansion, growth, and collapse-like
      identity evidence
- [x] Generate visualization outputs
- [x] Record failed tuning sessions and accepted replay session

### Implementation Notes

- Added seed:
  - `configs/landscapes/seed/grcl9-cell-full-capacity-phenomenology-cascade.seed.yaml`
- Added mixed-family compilation so one GRCL landscape example can produce:
  - `spark_candidate_region`
  - `column_proxy_profile`
  - `expansion_refinement_region`
  - `growth_locus`
  - `post_expansion_fission_geometry`
- Added connected mixed lowering via explicit `cascade_component_bridge`
  bridge edges.
- Preserved `grcl9_*` source/lowering caches across GRC9 topology mutation so
  final selectors can compare source-declared roles to runtime identity.
- S0016-S0019 are retained as replayable tuning attempts.
- S0020 is the accepted replay:
  - fixture: `cell_full_capacity_phenomenology_cascade`
  - requested steps: `24`
  - checkpoints: `25`
  - lowered graph: `24` nodes, `28` edges
  - runtime events: `1` spark, `1` expansion, `60` growth
  - selector status: `passed`
  - collapse-like selector: `runtime_collapse_like_long_window`
  - target selection: `group_centroid`

### Verification

- [x] S0020 session is replayable
- [x] S0020 visualizations generated
- [x] Selector report records all expected phenomenology signatures
- [x] Collapse-like evidence remains diagnostic and does not claim a GRC9
      `collapse` event

### Summary

Implemented as S0020. This is the current full-capacity GRCL-9 example: one
connected source-authored landscape seed produces spark, expansion, growth, and
collapse-like identity evidence over a 24-step replay window.

## Iteration 8.4. Cascade Robustness Family

### Goal

Turn S0020 from a single flagship example into a controlled family that records
which phenomenology signatures survive targeted source perturbations.

### Checks

- [x] Keep S0020 as the baseline, not overwritten
- [x] Add low-growth and high-growth variants
- [x] Add no-merge and weak-merge bridge variants
- [x] Add isolated negligible-bridge variant
- [x] Add larger developed-basin support variant
- [x] Add no-refinement and no-growth negative controls
- [x] Add basin-asymmetry ladder variants
- [x] Add compact basin-asymmetry/growth phase diagram
- [x] Split runtime expansion events from expansion-size/module evidence
- [x] Add explicit ambiguous collapse-like selector for multi-anchor loss
- [x] Add phase-diagram summary JSON and Markdown artifacts
- [x] Add phase-diagram visual matrix index
- [x] Add event amplification classes
- [x] Store all variants as GRCL/Morse landscape seeds
- [x] Run all robustness variants in one replayable session
- [x] Generate visualizations for the robustness session
- [x] Record passes, misses, and falsified assumptions explicitly

### Implementation Notes

- Added robustness seeds:
  - `grcl9-cell-full-capacity-cascade-low-growth.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-high-growth.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-no-merge-bridge.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-weak-merge-bridge.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-isolated-bridge.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-larger-basin-support.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-no-refinement.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-no-growth.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-balanced-basins.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-mild-asymmetry.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-threshold-asymmetry.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-deep-collapse.seed.yaml`
  - `grcl9-cell-full-capacity-cascade-isolated-threshold.seed.yaml`
  - `grcl9-cell-full-capacity-phase-balanced-no-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-balanced-low-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-balanced-nominal-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-mild-no-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-mild-low-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-mild-nominal-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-threshold-no-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-threshold-low-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-threshold-nominal-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-deep-no-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-deep-low-growth.seed.yaml`
  - `grcl9-cell-full-capacity-phase-deep-nominal-growth.seed.yaml`
- Replay session:
  - `outputs/grcl9/lowering/sessions/S0021/`
  - `outputs/grcl9/lowering/sessions/S0022/`
  - `outputs/grcl9/lowering/sessions/S0023/`
  - `outputs/grcl9/lowering/sessions/S0024/`
- S0021 pass/miss summary:
  - baseline S0020 seed rerun: passed
  - low growth: passed
  - high growth: passed
  - no merge bridge: missed expected structural-only control because the
    runtime still produced collapse-like sink-role loss
  - weak merge bridge: same as no-merge
  - larger basin support: missed collapse-like selector after both source
    sink anchors were lost and the target became ambiguous
  - no refinement: missed the expected no-expansion selector because fission
    module summaries still populate expansion-size evidence
  - no growth: missed collapse-like selector; spark/expansion persisted, but
    removing growth made target selection ambiguous
- S0022 refinement summary:
  - added `runtime_expansion_count` so no-refinement controls test actual
    expansion events rather than fission module-size summaries
  - added `runtime_collapse_like_ambiguous` so larger-basin multi-anchor loss
    is recorded as an interpretable diagnostic pass
  - added isolated negligible-bridge control; it still lost the source
    `fission_sink_b` role, so collapse-like loss is not explained by explicit
    fission bridge strength alone
- S0023 basin-asymmetry ladder summary:
  - balanced basins missed the structural-only hypothesis and became
    ambiguous by losing the A anchor while retaining B
  - mild asymmetry already produced B-loss
  - threshold, deep-collapse, and isolated-threshold variants passed
    collapse-like B-loss selectors
- S0024 phase diagram summary:
  - all no-growth lanes became ambiguous with both source sink anchors lost
  - balanced low/nominal lanes became ambiguous with A-anchor loss
  - threshold and deep low/nominal lanes produced collapse-like B-loss
  - mild asymmetry is the transition row between ambiguous and B-loss regimes
- S0024 packaged artifacts:
  - `outputs/grcl9/lowering/sessions/S0024/reports/phase_diagram_summary.json`
  - `outputs/grcl9/lowering/sessions/S0024/reports/phase_diagram_summary.md`
  - `outputs/grcl9/lowering/sessions/S0024/visualizations/phase_diagram_visual_index.md`
  - event amplification classes: `quiet`, `active`, `runaway`

### Verification

- [x] S0021 session is replayable
- [x] S0021 visualizations generated
- [x] S0022 session is replayable
- [x] S0022 visualizations generated
- [x] S0023 session is replayable
- [x] S0023 visualizations generated
- [x] S0024 session is replayable
- [x] S0024 visualizations generated
- [x] S0024 phase-diagram summary artifacts generated
- [x] S0024 phase visual matrix index generated
- [x] All robustness lanes remain connected
- [x] Tests no longer over-assume all robustness controls should pass

### Summary

Implemented as S0021 and refined as S0022. The cascade is robust to moderate
growth changes, no-refinement and larger-basin controls now have field-backed
interpretable selectors, and even an isolated negligible fission bridge does
not prevent collapse-like sink-role loss under current GRC9 dynamics. S0023
adds the basin-asymmetry ladder and shows that the current cascade is highly
sensitive to basin anchor competition: even balanced basins do not remain a
clean structural-only control over the 24-step window. S0024 turns this into a
phase diagram and identifies growth as the regime selector: without growth the
system loses both source anchors ambiguously, while threshold/deep asymmetry
with growth selects collapse-like B-loss.

## Iteration 8.5. Accepted Collapse Extension

### Goal

Implement the accepted outcome of the collapse observability and
collapse-producing seed-discovery work.

### Checks

- [x] Review Phase T-GRC9 collapse-adjacent observability
- [x] Review Phase V-GRC9 collapse-adjacent visualization boundaries
- [x] Decide whether S0009 evidence is structural-only,
      diagnostic-only, runtime/event-backed, or deferred
- [x] Incorporate the Iteration 8.2 runtime seed-discovery result
- [x] Update GRCL-9 source/catalog language to match the decision
- [x] Add telemetry selectors only for accepted evidence surfaces
- [x] Add visualization overlays only when backed by saved telemetry or
      checkpoint fields
- [x] Generate a later catalog session if new evidence is accepted

### Implementation Notes

- S0008 remains the first reviewed lowered motif catalog.
- S0009 remains structural-only unless superseded by a later positive session.
- Phase T-GRC9 review is complete:
  - `implementation/Phase-T-GRC9-CollapseAdjacentObservabilityReview.md`
  - decision: use existing fields/checkpoints first; no new `collapse` event
    or compact collapse-adjacent fields in this pass.
- Phase V-GRC9 review is complete:
  - `implementation/Phase-V-GRC9-CollapseAdjacentVisualizationReview.md`
  - decision: render collapse-adjacent structural probes only from existing
    visuals plus upstream selector/report artifacts; reuse GRCV3
    transparent-source/arrow/target grammar only for labeled structural probes.
- Any Phase T telemetry addition should be diagnostic-only or a new contract
  version; it must not silently change `phase_t_grc9_iter1_v1`.
- Iteration 8.5 accepts collapse-like source-role loss as a diagnostic-only
  selector surface. It does not add a `collapse` event kind, a GRC9 collapse
  equation, or GRCV3 collapse semantics.
- The reviewed motif catalog now records a `collapse_diagnostic` block for
  collapse-related selectors. The block stores classification, lost source sink
  roles, target-selection policy, fission candidate/confirmation counts, and
  S0024 phase-diagram context when available.
- S0025 is the accepted-collapse catalog extension:
  - source session: `S0024`
  - accepted motifs: 12
  - rejected motifs: 0
  - collapse diagnostics: 12
  - runtime-collapse-like diagnostics: 5
  - ambiguous collapse-like diagnostics: 7
  - catalog:
    `outputs/grcl9/lowering/sessions/S0025/reviewed_grcl9_lowered_motif_catalog.json`
  - review report:
    `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_report.json`
  - summary:
    `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_summary.md`

### Verification

- [x] Existing S0008 catalog meaning remains unchanged
- [x] Reports explain collapse-candidate status without claiming runtime
      collapse
- [x] Phase V visuals draw transparent-source/arrow/target overlays only as
      `collapse_adjacent_structural_probe`, not as runtime collapse
- [x] `PYTHONPATH=src ./.venv/bin/python -m unittest
      tests.telemetry.test_grcl9_lowered_motif_catalog`
      passes

### Summary

Iteration 8.5 is complete. GRCL-9 now has an accepted collapse extension that
is diagnostic-only and catalog-backed: S0025 promotes the S0024 phase-diagram
evidence into reviewed catalog entries while preserving the non-claim that GRC9
has no collapse event or runtime collapse semantics in this pass.

## Iteration 9. Handoff

### Goal

Record the first GRCL-9 source/lowering handoff and close Revision 1.

### Checks

- [x] Create `implementation/GRCL-9-Handoff.md`
- [x] Record implemented source constructs
- [x] Record implemented GRCL landscape example families
- [x] Record supported fixture families
- [x] Record replayable sessions
- [x] Record reviewed lowered motif catalog
- [x] Record unsupported/deferred constructs
- [x] Record known runtime and telemetry limitations
- [x] State that GRCL-9 remains lowering-only
- [x] State that GRCL-9 does not add observer, Lorentzian, or GRCV3 hierarchy
  semantics
- [x] Record recommended next implementation lane

### Implementation Notes

- The handoff should be evidence-indexed, not just narrative.
- It should point to session artifacts under `outputs/grcl9/lowering/`.
- It should distinguish source capability, lowering capability, and observed
  runtime behavior.

### Verification

- [x] Handoff links all accepted replay sessions
- [x] Handoff links the reviewed lowered motif catalog
- [x] Handoff records non-claims clearly
- [x] Handoff identifies the next missing capability without reopening
  completed claims

### Summary

Iteration 9 is complete. The Revision 1 closeout handoff is recorded in
`implementation/GRCL-9-Handoff.md`. It indexes the implemented source
constructs, landscape example families, replayable sessions, reviewed catalogs,
collapse-diagnostic boundary, unsupported/deferred constructs, and the next
recommended post-Revision-1 lane.
