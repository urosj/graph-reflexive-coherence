# GRCL-9V3 Implementation Checklist

This document tracks execution of the **GRCL-9V3** source-seed/lowering layer.

It is intentionally separate from
[GRCL-9V3-ImplementationPlan.md](./GRCL-9V3-ImplementationPlan.md):

- the plan defines source/lowering boundary, data carriers, iteration sequence,
  and acceptance criteria,
- this checklist records execution iteration by iteration.

## Usage Rules

- Keep GRCL-9V3 source/lowering-only. Do not add runtime semantics here.
- Do not change GRC9V3 runtime equations to make a source seed pass.
- Do not inject solved spark, expansion, choice, collapse, growth, daughter
  sink, flux, tensor, or basin outcomes into source fixtures.
- Treat source constructs as structural preconditions and policy declarations.
- Preserve ownership tags:
  - `grc9_mechanical`
  - `grcv3_semantic`
  - `grc9v3_hybrid`
  - `shared_runtime`
- Preserve Phase T-GRC9V3 telemetry as the observation surface.
- Use contract field names from `Phase-T-GRC9V3-TelemetryContract.md`.
- Mark optional telemetry as optional.
- Require connected lowered graphs.
- Preserve deterministic assembly, budget, topology, and provenance.
- Record replayable sessions under:
  - `outputs/grcl9v3/lowering/sessions/S0001/`
- Record the experiment log at:
  - `outputs/grcl9v3/lowering/ExperimentalLog.md`
- Keep Lorentzian causal-layer, observer-local, and visual-only claims out of
  Revision 1.

## Iteration Template

```markdown
## Iteration N. <Short Name>

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / test / review check>

### Summary

<Short outcome summary once iteration is complete>
```

## Iteration 0. Planning Bootstrap

### Goal

Create the GRCL-9V3 source/lowering planning documents and lock the boundary
as family-native lowering into GRC9V3 initial state, not runtime execution.

### Checks

- [x] Create `GRCL-9V3-Vocabulary.md`
- [x] Create `GRCL-9V3-ImplementationPlan.md`
- [x] Create `GRCL-9V3-ImplementationChecklist.md`
- [x] Anchor the plan in S0013 expanded GRC9V3 motif catalog
- [x] Anchor the plan in S0014 source-language handoff
- [x] Record source constructs may declare preconditions, not observed events
- [x] Record the implementation location:
  - `src/pygrc/landscapes/extensions/grcl9v3/`
- [x] Record the artifact/session layout:
  - `outputs/grcl9v3/lowering/sessions/S0001/`
  - `outputs/grcl9v3/lowering/ExperimentalLog.md`
- [x] Record runtime-only exclusions:
  - Hessian backend comparison
  - budget preservation diagnostics
  - coarse-cache invalidation diagnostics
- [x] Record required non-claims

### Implementation Notes

- Planning starts from the reviewed GRC9V3 runtime catalog, not from source
  imagination.
- The first source layer should express accepted lifecycle motifs and enough
  controls to preserve pass/fail distinctions.
- Runtime-only records can appear as validation side conditions but should not
  become source ontology in Revision 1.

### Verification

- [x] The vocabulary/plan/checklist documents exist under `implementation/`
- [x] The plan names the S0013/S0014 input artifacts
- [x] The plan keeps source claims separate from runtime telemetry
- [x] The plan uses the family-native landscape extension location

### Summary

Iteration 0 is complete. GRCL-9V3 now has a vocabulary document, implementation
plan, and execution checklist. The track is scoped as source/lowering into
connected GRC9V3 runtime seeds with telemetry-backed validation.

## Iteration 1. Lowering Manifest Contract

### Goal

Create the typed lowering manifest that maps S0014 handoff entries to
GRCL-9V3 source constructs, graph preconditions, ownership tags, and expected
telemetry.

### Checks

- [x] Create `src/pygrc/landscapes/extensions/grcl9v3/__init__.py`
- [x] Create `src/pygrc/landscapes/extensions/grcl9v3/manifest.py`
- [x] Create `tests/landscapes/test_grcl9v3_manifest.py`
- [x] Define manifest version:
  - `grcl9v3_lowering_manifest_v1`
- [x] Define source schema version reference:
  - `grcl9v3.source.v1`
- [x] Map S0014 source-expression candidates to manifest entries
- [x] Preserve vocabulary-needed records as future/source-control entries
- [x] Preserve runtime-only records as exclusions
- [x] Record required source knobs per entry
- [x] Record ownership tags per entry
- [x] Record lowering carriers per entry
- [x] Record expected Phase T-GRC9V3 telemetry fields per entry
- [x] Record pass/fail control roles
- [x] Record explicit non-claims

### Implementation Notes

- The manifest is not a source fixture and not a lowerer.
- Telemetry paths must match `Phase-T-GRC9V3-TelemetryContract.md`.
- Runtime-only records should not be silently promoted into source constructs.
- Implemented typed manifest exports in:
  - `src/pygrc/landscapes/extensions/grcl9v3/__init__.py`
  - `src/pygrc/landscapes/extensions/grcl9v3/manifest.py`
  - `src/pygrc/landscapes/extensions/__init__.py`
- The default manifest records:
  - 8 S0014 source-expression candidate motif ids as lowering entries
  - 12 S0014 vocabulary-needed records as future vocabulary records
  - 6 S0014 runtime-only records as exclusions
- Transport rerouting and quiescent controls are intentionally not executable
  manifest entries yet; they are preserved as future vocabulary records.
- Runtime-only budget, Hessian backend, and coarse-cache diagnostics are
  preserved as exclusions, not source constructs.
- Reviewed S0014 motif ids intentionally use hyphenated reviewed-catalog ids
  and are validated with an explicit GRC9V3 motif-id pattern, separate from
  snake-case source tokens.
- Selector ids in Iteration 1 are manifest placeholders for Iteration 6
  selector validation; they are validated as stable tokens but are not yet
  resolved against selector definitions.
- Added an explicit S0014 drift validator:
  - `validate_grcl9v3_manifest_against_handoff()`
- Lowering carriers are restricted to GRCL-9V3 namespaces:
  - `extensions.grcl9v3`
  - `node_payload.grcl9v3_*`
  - `edge_payload.grcl9v3_*`
  - `cached_quantities.grcl9v3_*`
- Manifest graph preconditions reject runtime-result smuggling keys such as
  `event_counts_by_kind`, solved diagnostics, and solved event flags.
- The telemetry namespace is centralized as:
  - `GRCL9V3_TELEMETRY_FIELD_PREFIX`

### Verification

- [x] Manifest entries round-trip through JSON-safe mappings
- [x] Duplicate motif ids are rejected
- [x] Unsupported source construct kinds are rejected
- [x] Invalid telemetry field paths are rejected
- [x] Runtime-only records are present as exclusions, not source constructs
- [x] Reviewed motif ids use explicit hyphenated motif-id validation
- [x] S0014 handoff drift is checked against the manifest
- [x] Runtime-result smuggling keys are rejected in graph preconditions
- [x] Lowering carriers are restricted to GRCL-9V3 namespaces
- [x] Telemetry field prefix is centralized
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_manifest`

### Summary

Iteration 1 is complete. GRCL-9V3 now has a typed lowering manifest contract
rooted in the S0014 source-language handoff. It maps the 8 source-expression
candidates into manifest entries, preserves 12 records as future vocabulary
work, and preserves 6 runtime-only diagnostics as explicit exclusions.

## Iteration 2. Source Schema

### Goal

Implement `grcl9v3.source.v1` source dataclasses and validation.

### Checks

- [x] Create `src/pygrc/landscapes/extensions/grcl9v3/schema.py`
- [x] Create `tests/landscapes/test_grcl9v3_schema.py`
- [x] Define source document dataclass
- [x] Define construct dataclasses:
  - `hybrid_spark_region`
  - `row_basis_hessian_profile`
  - `hybrid_tensor_profile`
  - `column_proxy_fallback_profile`
  - `expansion_refinement_region`
  - `choice_collapse_region`
  - `growth_locus`
  - `transport_rerouting_region`
  - `appendix_e_division_region`
  - `quiescent_hybrid_region`
- [x] Validate construct ids and motif ids
- [x] Validate ownership tags
- [x] Validate expected telemetry selectors
- [x] Validate explicit non-claims
- [x] Reject runtime-result smuggling fields

### Implementation Notes

- Source schema validation should run without constructing `GRC9V3`.
- Source fixtures should remain JSON/YAML-compatible.
- Source can state expected selectors, but not observed selector results.
- Implemented source schema exports in:
  - `src/pygrc/landscapes/extensions/grcl9v3/schema.py`
  - `src/pygrc/landscapes/extensions/grcl9v3/__init__.py`
  - `src/pygrc/landscapes/extensions/__init__.py`
- Added source policy dataclasses:
  - `GRCL9V3BridgePolicy`
  - `GRCL9V3BudgetPolicy`
  - `GRCL9V3ProvenancePolicy`
- Source construct ids and fixture ids remain snake-case source tokens.
- Source `motif_id` values intentionally use reviewed S0014 motif ids.
- Every construct carries:
  - `source_role`
  - `ownership`
  - `expected_selector_ids`
  - `executable`
  - `non_claims`
- The schema validates source documents without importing or constructing the
  runtime `GRC9V3` model.
- Source document `notes` are checked for runtime-result smuggling just like
  construct payloads.
- Manifest linkage is explicit and opt-in through:
  - `validate_grcl9v3_source_document_against_manifest()`
- The `executable` flag is now meaningful: non-executable constructs must
  carry the `non_executable_source_construct` non-claim.
- Column proxy fallback directly enforces the three-column GRC9 range `[1, 3]`.
- The forbidden runtime key list remains a static schema boundary for Revision
  1; future telemetry/runtime event additions should update this list during
  contract maintenance.

### Verification

- [x] Valid source documents round-trip through mappings
- [x] Missing required source fields fail deterministically
- [x] Invalid ownership values fail deterministically
- [x] Solved event/source smuggling fails deterministically
- [x] All ten Revision 1 construct dataclasses dispatch and round-trip
- [x] Bridge, budget, and provenance policies validate deterministically
- [x] Source document notes reject runtime-result smuggling
- [x] Source documents can be validated against the lowering manifest
- [x] Non-executable constructs require an explicit non-claim
- [x] Column proxy target columns validate directly against `[1, 3]`
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_schema`

### Summary

Iteration 2 is complete. GRCL-9V3 now has a typed `grcl9v3.source.v1` schema
with source document round-trip support, ten source construct dataclasses,
ownership validation, reviewed motif-id validation, expected selector tokens,
policy validation, and runtime-result smuggling rejection.

## Iteration 3. Minimal Source Fixtures

### Goal

Author minimal source fixtures for the first GRCL-9V3 pass/fail and control
examples.

### Checks

- [x] Create `src/pygrc/landscapes/extensions/grcl9v3/fixtures.py`
- [x] Create `tests/landscapes/test_grcl9v3_fixtures.py`
- [x] Add hybrid spark pass/fail fixtures
- [x] Add spark-to-expansion pass/fail fixtures
- [x] Add Appendix E division pass/fail fixtures
- [x] Add choice/collapse pass/fail fixtures
- [x] Add growth pass/fail fixtures
- [x] Add transport rerouting fixture
- [x] Add quiescent no-event fixture
- [x] Link every fixture to a manifest entry or future-vocabulary record
- [x] Record expected selector ids
- [x] Preserve explicit non-claims

### Implementation Notes

- Fixtures are source declarations, not serialized `GRC9V3State` payloads.
- Pass/fail controls should be minimal perturbations when possible.
- Implemented fixture exports in:
  - `src/pygrc/landscapes/extensions/grcl9v3/fixtures.py`
  - `src/pygrc/landscapes/extensions/grcl9v3/__init__.py`
  - `src/pygrc/landscapes/extensions/__init__.py`
- Fixture names are stable in:
  - `GRCL9V3_SOURCE_FIXTURE_NAMES`
- The first fixture set includes 12 source documents:
  - 5 executable manifest-entry fixtures for accepted S0014 source-expression
    candidates
  - 7 future-vocabulary fixtures for negative/control/transport/quiescent
    source declarations
- Future-vocabulary fixtures validate through
  `validate_grcl9v3_source_document_against_manifest(..., allow_future_vocabulary=True)`.
- Future-vocabulary fixture ids are derived from the matching manifest
  `future_vocabulary_records` entry by motif id, so fixture linkage follows
  manifest phenomenon naming instead of duplicating string conventions.
- Future-vocabulary selector ids remain placeholders until field-backed GRCL-9V3
  selector resolution is added; those fixtures intentionally keep
  `expected_telemetry=()` so they do not inherit runtime claims prematurely.
- No fixture serializes `GRC9V3State`, runtime event histories, solved flux,
  solved tensors, or solved diagnostics.

### Verification

- [x] Fixtures load without running GRC9V3
- [x] Fixtures validate against `grcl9v3.source.v1`
- [x] Fixtures link to manifest entries or future-vocabulary records
- [x] Fixtures do not contain runtime event histories
- [x] Pass/fail fixtures preserve distinct source preconditions
- [x] Transport and quiescent fixtures remain future-vocabulary records
- [x] Non-executable source construct validation is covered in schema tests
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_fixtures`

### Summary

Iteration 3 is complete. GRCL-9V3 now has 12 minimal source fixtures covering
hybrid spark, spark-to-expansion, Appendix E division, choice/collapse, growth,
transport rerouting, and quiescent controls. The fixtures remain source
documents only; executable records link to manifest entries, while
negative/control/transport/quiescent records link to future-vocabulary records.

## Iteration 4. Lowerer Revision 1

### Goal

Lower GRCL-9V3 source fixtures into connected `GRC9V3State` graphs.

### Checks

- [x] Create a family-native lowerer module
- [x] Lower source fixtures into connected graphs
- [x] Enforce nine-port capacity where GRC9 mechanics apply
- [x] Preserve GRCV3 semantic ownership fields
- [x] Preserve GRC9V3 hybrid ownership fields
- [x] Preserve deterministic node/edge assembly
- [x] Preserve budget target initialization
- [x] Populate `grcl9v3_provenance`
- [x] Populate `grcl9v3_motif_registry`
- [x] Populate `grcl9v3_assembly_policy`
- [x] Populate expected-region caches
- [x] Mark bridge edges with `grcl9v3_edge_kind = "bridge"`

### Implementation Notes

- The lowerer produces a `GRC9V3State` compatible with the existing model.
- It does not replace or modify `GRC9V3` runtime equations.
- It should follow the family-native lowering direction used by mature GRCL-v3
  and GRCL-9 work.
- Implemented model-side modules:
  - `src/pygrc/models/grc_9_v3_grcl9v3_lowering.py`
  - `src/pygrc/models/grc_9_v3_grcl9v3_provenance.py`
- The source schema remains in `src/pygrc/landscapes/extensions/grcl9v3`;
  lowering consumes source documents and emits native `GRC9V3State`.
- Lowered state caches include:
  - `grcl9v3_provenance`
  - `grcl9v3_motif_registry`
  - `grcl9v3_assembly_policy`
  - `grcl9v3_expected_saturated_node_ids`
  - `grcl9v3_expected_tensor_hotspot_node_ids`
  - `grcl9v3_expected_column_proxy_node_ids`
  - `grcl9v3_expected_hessian_profile_node_ids`
  - `grcl9v3_expected_expansion_region_ids`
  - `grcl9v3_expected_choice_region_ids`
  - `grcl9v3_expected_growth_locus_ids`
  - `grcl9v3_expected_transport_region_ids`
  - `grcl9v3_expected_quiescent_region_ids`
  - `grcl9v3_expected_appendix_e_region_ids`
  - `grcl9v3_bridge_edge_ids`
- Revision 1 rejects non-executable source constructs at lowering time, even
  when the schema-level non-claim is present.
- Revision 1 accepts at most one construct per construct kind per fixture; this
  keeps `_first(...)` lowering semantics explicit rather than silently dropping
  duplicate source declarations.
- Hessian backend metadata is source-owned. If a source fixture has no
  `row_basis_hessian_profile`, lowering records the source default
  `row_basis_diagonal` instead of reading runtime params.
- Component bridge assembly preflights free ports before connecting anchors.

### Verification

- [x] Lowered graphs are connected
- [x] Lowering is deterministic
- [x] Provenance maps source constructs to lowered nodes/edges
- [x] Budget and topology invariants hold
- [x] Auxiliary expected-region caches are populated
- [x] Non-executable constructs are rejected by the lowerer
- [x] Duplicate construct kinds are rejected by the lowerer
- [x] Hessian backend fallback is source-owned
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_grcl9v3_lowering`

### Summary

Iteration 4 is complete. GRCL-9V3 source fixtures now lower into connected
`GRC9V3State` graphs with deterministic topology, native V3 node state,
source-to-runtime provenance, motif registry records, expected-region caches,
explicit bridge-edge payloads, and initialized quadrature budget targets.

## Iteration 5. Replay Runner

### Goal

Run lowered source fixtures through the existing `GRC9V3` runtime and store
replayable artifacts.

### Checks

- [x] Create replay/session runner
- [x] Write session manifests
- [x] Write source fixture copies
- [x] Write lowered state payloads
- [x] Write telemetry artifacts
- [x] Write graph checkpoints
- [x] Write replay commands
- [x] Update `outputs/grcl9v3/lowering/ExperimentalLog.md`

### Implementation Notes

- Replay should use existing GRC9V3 runtime APIs.
- Replay should not special-case runtime events based on source fixture names.
- The runner lives in `src/pygrc/telemetry/grcl9v3_replay.py`.
- The replay command is recorded in each session as `replay.sh`; the Python
  entrypoint is `python -m pygrc.telemetry.grcl9v3_replay`.
- Replay records source fixture JSON, lowered `GRC9V3State` payload JSON,
  Phase T-GRC9V3 telemetry rows, graph checkpoints, per-lane reports, a session
  manifest, and the lowering experimental log.
- Session manifests record the exact replay command, including `--steps` and
  selected `--fixture` arguments. `replay.sh` uses the same command.
- `ExperimentalLog.md` is cumulative by session id: rerunning the same session
  refreshes its row without dropping other sessions.
- The lowerer initializes deterministic `rng_state` and records the RNG seed
  source in lowered-state caches, so replay determinism is owned by the lowered
  state rather than by runner-side patching.
- Telemetry family extensions mirror the GRCL-9V3 expected-region caches from
  the lowered state, and lane context points at the GRCL-9V3 source/lowering
  plan plus the source fixture artifact.
- Iteration 5 verifies deterministic replay and artifact shape only. Selector
  scoring and fixture refinement are intentionally deferred to Iterations 6
  and 8.

### Verification

- [x] Sessions replay deterministically
- [x] Step/event/run-summary telemetry files exist
- [x] Graph checkpoints exist
- [x] Experimental log records every session

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_replay
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_replay tests.models.test_grc_9_v3_grcl9v3_lowering tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_grcl9_lowering tests.landscapes.test_grcl9_manifest tests.landscapes.test_grcl9_schema tests.landscapes.test_grcl9_fixtures
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0001 --steps 3
```

### Summary

Complete. `S0001` contains 12 lowered-source replay lanes under
`outputs/grcl9v3/lowering/sessions/S0001/`. Each lane has replay-matching step
rows, event rows, and final digest, plus source fixture copies, lowered state
payloads, graph checkpoints, and per-lane replay reports. The run observed 17
runtime events across the smoke session and records them as runtime evidence,
not as accepted motif claims.

## Iteration 6. Selector Validation

### Goal

Apply Phase T-GRC9V3 field-backed selectors to lowered-source sessions.

### Checks

- [x] Build selector validation over lowered-source artifacts
- [x] Record missing telemetry surfaces
- [x] Record pass/fail/ambiguous outcomes
- [x] Preserve source fixture links
- [x] Preserve runtime evidence paths

### Implementation Notes

- Selectors observe telemetry; they do not inspect source claims as proof.
- The validator lives in
  `src/pygrc/telemetry/grcl9v3_selector_validation.py`.
- Source fixture selector ids remain vocabulary-facing. Iteration 6 expands
  them into concrete Phase T-GRC9V3 selectors only inside the validation
  report. The expansion table is anchored in
  `src/pygrc/landscapes/extensions/grcl9v3/selector_expansions.py`:
  - `hybrid_spark_events`
  - `hybrid_tensor_available`
  - `hybrid_expansion_events`
  - `appendix_e_summary`
  - `appendix_e_no_completion`
  - `choice_collapse_events`
  - `no_choice_collapse_events`
  - `growth_events`
  - `no_growth_events`
  - `transport_rerouting_signature`
  - `no_lifecycle_events`
- Every lane also validates common lowered-source links:
  `contract_version_valid`, `grcl9v3_source_fixture_link_present`, and
  `grcl9v3_expected_region_caches_present`.
- `S0002` validates `S0001` and writes:
  - `outputs/grcl9v3/lowering/sessions/S0002/selector_manifest.json`
  - `outputs/grcl9v3/lowering/sessions/S0002/reports/selector_validation_report.json`
  - `outputs/grcl9v3/lowering/sessions/S0002/reports/selector_validation_summary.md`

### Verification

- [x] Selector output is deterministic
- [x] Missing surfaces are reported explicitly
- [x] Source/runtime evidence links are complete

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_selector_validation tests.telemetry.test_grcl9v3_replay
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_selector_validation tests.telemetry.test_grcl9v3_replay tests.models.test_grc_9_v3_grcl9v3_lowering tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0002 --source-session-ids S0001
```

### Summary

Complete for the initial lowered-source batch. `S0002` validated 12 lanes from
`S0001`: 5 strong candidates, 3 candidates, 1 ambiguous record, 3 weak
candidates, and 0 rejected records. It reported 3 missing surfaces, all tied to
absent Appendix E summary fields in the current lowered replay. The strongest
records are growth, transport rerouting, quiescent no-event, Appendix E
no-completion, and choice/collapse no-event controls. The ambiguous Appendix E
positive record and the weak spark/expansion positive records identify the next
source-seed refinement targets rather than replay infrastructure failures.

## Iteration 7. Visualization Review

### Goal

Generate visual review artifacts for lowered-source sessions.

### Checks

- [x] Generate graph visualizations from checkpoints
- [x] Generate dense/sparse telemetry graph outputs where applicable
- [x] Link visuals back to selector records
- [x] Keep visuals as supporting evidence only

### Verification

- [x] Visual artifacts exist for selector-backed candidates
- [x] Visual links do not promote records without telemetry evidence

### Summary

Complete. Iteration 7 adds `pygrc.visualization.grcl9v3_lowering` and the
`render_grcl9v3_lowering_visual_review` CLI/API. `S0003` renders the 9
selector-backed motif records from `S0002` and records the 3 weak selector
records as skipped with `no_selector_backed_motif`. Rendered records include
trajectory plots, event timelines, graph sequences, graph animations, graph
layout JSON, final graph HTML, GRCL-9V3 overlays, overlay summaries, and
source/runtime boundary panels. Every overlay summary and boundary panel states
that visuals are supporting evidence only and that selector telemetry remains
primary. The refined visual metadata records deterministic layout seeds,
explicit selector ids, dense/sparse graph-surface paths, and the
source-derived/runtime-added graph distinction. Ambiguous selector-backed
records are rendered as diagnostic supporting evidence rather than skipped.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_grcl9v3_lowering
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0003 --selector-session-id S0002 --output-root outputs/grcl9v3/lowering
```

Primary artifacts:

- `outputs/grcl9v3/lowering/sessions/S0003/visual_index.json`
- `outputs/grcl9v3/lowering/sessions/S0003/reports/visual_review_report.json`
- `outputs/grcl9v3/lowering/sessions/S0003/reports/visual_review_summary.md`
- `outputs/grcl9v3/lowering/sessions/S0003/visualizations/`

## Iteration 8. Source-Seed Discovery And Refinement

### Goal

Build the GRCL-9V3 source-seed evidence layer before reviewed catalog
promotion. The current mechanical source fixtures are useful smoke evidence,
but Revision 1 should also have authored GRCL/Morse examples, checked-in seed
artifacts, working hybrid phenomenology seeds, composed-cell examples, and at
least one complex robustness family.

### Scope Notes

- Follow the GRCL-9 Iteration 7/8 pattern, adapted to GRC9V3 hybrid
  semantics.
- Keep all examples source-facing. Do not shortcut by writing raw GRC9V3 graph
  literals.
- Source examples may declare landscape preconditions and lowering intent.
  Sparks, expansions, growth, choice/collapse, Appendix E completion, and
  runtime summaries remain telemetry observations.
- Preserve the source/runtime boundary in replay, selector validation, and
  visualization.

### Post-Review Validity Note

Iterations 8.2 through 8.6 are classified as **alternative-development
diagnostics** wherever their conclusions depend on growth. They should not be
treated as valid paper-facing GRCL-9V3 evidence for growth, growth/collapse, or
growth-relay motifs. They remain valuable replayable records of how the legacy
over-aggressive `growth_locus` model developed, and they should inform
Iteration 9 corrected seed design. Iteration 8.1 remains valid
compiler/source-layer infrastructure. Non-growth evidence inside later 8.x
sessions can still be reviewed independently when selector surfaces separate it
from legacy growth behavior.

## Iteration 8.1. GRCL-9V3 Landscape Example Compiler

### Goal

Add a typed GRCL/Morse-facing landscape example layer above
`grcl9v3.source.v1`, then compile those authored examples into the existing
mechanical source schema.

### Checks

- [x] Create GRCL-9V3 landscape example module under
  `src/pygrc/landscapes/extensions/grcl9v3/`
- [x] Define landscape example version, e.g. `grcl9v3.landscape_example.v1`
- [x] Define typed GRCL/Morse landscape document classes
- [x] Include critical-region, stable-basin, unstable-direction,
  separatrix/saddle, ridge/membrane, valley/channel, plateau/support,
  boundary-stratum, refinement-locus, tensor/Hessian, choice/collapse,
  growth-locus, transport-rerouting, quiescent, and Appendix E region terms
- [x] Require explicit `grcl9v3_required = true` or equivalent lowering guard
- [x] Author default landscape examples directly instead of deriving them from
  existing mechanical source fixtures
- [x] Compile landscape examples into `GRCL9V3SourceDocument`
- [x] Map term profiles into concrete mechanical construct fields
- [x] Preserve source-term to mechanical-construct provenance
- [x] Reject examples with GRCL-9V3 fields but no lowering guard
- [x] Reject examples that embed raw GRC9V3 graph literals
- [x] Reject examples that embed solved telemetry, event histories, or runtime
  outcomes

### Verification

- [x] Example documents round-trip through JSON-safe mappings
- [x] Compiler output is deterministic
- [x] Compiler output validates as `grcl9v3.source.v1`
- [x] Compiled output lowers to connected `GRC9V3State` graphs
- [x] Tests cover rejection of graph literals and solved runtime fields
- [x] Tests prove authored term profile changes alter compiled construct fields

### Summary

Complete. Iteration 8.1 adds
`src/pygrc/landscapes/extensions/grcl9v3/examples.py` with
`grcl9v3.landscape_example.v1`, typed GRCL/Morse-facing terms, authored
default examples for the 12 current GRCL-9V3 control lanes, deterministic
forward compilation into `GRCL9V3SourceDocument`, and compiled source
provenance. The compiler now builds mechanical source constructs from
landscape terms and their profiles directly; it does not look up existing
fixtures as compilation targets. The compiled examples validate against the
GRCL-9V3 manifest or future-vocabulary records and lower to connected
`GRC9V3State` graphs. This iteration does not add checked-in seed YAMLs or
replay source modes; those remain Iteration 8.2.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering
```

## Iteration 8.2. Seed-Backed GRCL-9V3 Examples

### Goal

Add checked-in `LandscapeSeed` examples with `extensions.grcl9v3` so GRCL-9V3
examples can be edited, replayed, and tuned like GRCL-V3 rich seeds and GRCL-9
source seeds.

### Checks

- [x] Add GRCL-9V3 seed-backed example paths under
  `configs/landscapes/seed/`
- [x] Define top-level seed extension contract for `extensions.grcl9v3`
- [x] Extract primitive-level GRCL-9V3 terms from seed extensions
- [x] Reject seed examples with primitive GRCL-9V3 terms but no top-level
  `extensions.grcl9v3`
- [x] Reject seed examples unless `grcl9v3_required = true`
- [x] Compile extracted seed examples into `grcl9v3.source.v1` using the
  Iteration 8.1 compiler
- [x] Preserve source seed reference in compiled source provenance
- [x] Add replay source mode for landscape seed examples
- [x] Store original seed files under session `grcl_landscape_seeds/` or
  `grcl9v3_landscape_seeds/`
- [x] Store extracted example documents separately from compiled source
  documents
- [x] Replay seed-backed examples through the existing lower/replay machinery
- [x] Validate seed-backed sessions with selectors
- [x] Render seed-backed visualizations

### Verification

- [x] Seed files load through the common `LandscapeSeed` loader
- [x] Seed extensions extract to GRCL-9V3 landscape example documents
- [x] Extracted examples compile to `GRCL9V3SourceDocument`
- [x] Compiled sources lower to connected `GRC9V3State` graphs
- [x] Replay artifacts are generated and reproducible
- [x] Visual artifacts link back to selectors and source seeds

### Summary

Complete as a seed-backed pipeline slice. Iteration 8.2 has the seed-backed
infrastructure and first replay/selector/visual pass. It does not claim the
elementary seed corpus is fully proven; that gate is tracked separately as
Iteration 8.2.1 before Iteration 8.3 starts composing hybrids.

The first checked-in seed-backed GRCL-9V3 examples live under
`configs/landscapes/seed/`, anchored in the S0014 GRC9V3 discovery handoff:

- `grcl9v3-hybrid-spark-gate-positive.seed.yaml`
- `grcl9v3-spark-to-expansion-positive.seed.yaml`
- `grcl9v3-appendix-e-cell-division-positive.seed.yaml`
- `grcl9v3-choice-collapse-positive.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-growth-pressure-positive.seed.yaml`
- `grcl9v3-transport-basin-rerouting-positive.seed.yaml`
- `grcl9v3-quiescent-hybrid-control.seed.yaml`

The seed path is now explicit and test-covered:

```text
LandscapeSeed YAML
-> extract_grcl9v3_landscape_example_from_seed(...)
-> compile_grcl9v3_landscape_example_to_source(...)
-> lower_grcl9v3_source_to_grc9v3_state(...)
-> replay / selectors / visuals
```

`S0004` is the first seed-backed replay session using
`source_mode = "landscape_seed_examples"`. `S0005` validates `S0004` with
selectors, and `S0006` renders selector-backed visuals. Growth and quiescent
seed-backed examples are strong candidates; hybrid spark, spark-to-expansion,
and choice/collapse are weak candidates and move to Iteration 8.2.1. They
should not be pushed into 8.3, because 8.3 composes already proven elementary
seeds.

Post-review status: the seed-backed growth example is needs-rerun for
paper-facing growth claims under Iteration 9 front-growth semantics. Non-growth
seed infrastructure and non-growth evidence remain valid. The affected growth
lane used the over-aggressive legacy `growth_locus` model, where inactive
interior ports could become growth parents without explicit spark/front
capacity provenance.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples tests.telemetry.test_grcl9v3_replay
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_examples tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0004 --steps 3 --source-mode landscape_seed_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0005 --source-session-ids S0004
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0006 --selector-session-id S0005
```

## Iteration 8.2.1. Elementary Seed Tuning Gate

### Goal

Tune or explicitly reject individual seed-backed GRCL-9V3 examples before any
hybrid composition begins. This is the gate between seed-backed authoring and
hybrid composition.

### Checks

- [x] Use S0004/S0005/S0006 as the baseline failure/evidence set
- [x] Tune hybrid spark seed until spark selectors pass or record an explicit
  rejected elementary seed
- [x] Tune spark-to-expansion seed until expansion selectors pass or record an
  explicit rejected elementary seed
- [x] Tune choice/collapse seed until choice/collapse selectors pass or record
  an explicit rejected elementary seed
- [x] Add and tune Appendix E seed-backed example
- [x] Add and tune transport rerouting seed-backed example
- [x] Record controls already present in this elementary batch; defer additional
  negative/control seed-backed examples until a selector needs them
- [x] Keep all failed tuning attempts replayable
- [x] Render visuals for the tuned elementary seed session
- [x] Do not add hybrid composition seeds in this iteration

### Verification

- [x] Elementary seed-backed motifs needed for first composition are selector-backed
  or explicitly rejected with replayable evidence
- [x] Positive and negative controls are distinguishable by selectors where
  controls are required
- [x] Weak, candidate, or ambiguous records are not promoted by visuals alone
- [x] Tests cover seed extraction, lowering, replay, selectors, and visuals

### Summary

Complete for the first elementary tuning gate. `S0007` replays seven
seed-backed examples, `S0008` selector-validates them, and `S0009` renders
visual review artifacts. Selector outcome:

- Strong candidates: hybrid spark, spark-to-expansion, choice/collapse,
  growth pressure, transport rerouting, and quiescent no-event control.
- Candidate: Appendix E cell division. It now emits hybrid spark candidate,
  mechanical expansion, and completed spark evidence, but it still does not
  satisfy the representative Appendix E daughter-sink/hierarchy selectors.
  Keep it out of composition until a later focused Appendix E pass or an
  explicit diagnostic exception.

Post-review status: the growth-pressure strong candidate is needs-rerun for
paper-facing growth claims under Iteration 9. The other elementary signatures
remain eligible according to their own selector evidence. The growth-pressure
lane used the over-aggressive legacy `growth_locus` source construct rather
than a front-capacity declaration tied to spark/refinement boundary capacity.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_examples tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0007 --steps 3 --source-mode landscape_seed_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0008 --source-session-ids S0007
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0009 --selector-session-id S0008
```

## Iteration 8.2.2. Elementary Completeness Pass

### Goal

Close the remaining elementary seed-backed coverage before hybrid composition.
This iteration adds explicit controls and upgrades Appendix E / hierarchy from
candidate evidence to selector-backed strong evidence.

### Checks

- [x] Use S0007/S0008/S0009 as the tuned baseline
- [x] Tune Appendix E until daughter/hierarchy selectors pass without visual-only
  promotion
- [x] Add spark negative/control seed-backed example
- [x] Add spark-to-expansion negative/control seed-backed example
- [x] Add choice/collapse negative/control seed-backed example
- [x] Add growth-pressure negative/control seed-backed example
- [x] Keep Hessian backend comparison as a runtime diagnostic, not a GRCL source
  seed construct
- [x] Prevent incidental choice/collapse events in no-lifecycle seed-backed
  controls through replay configuration rather than selector leniency
- [x] Replay the expanded elementary seed set
- [x] Selector-score every elementary seed-backed lane
- [x] Render visuals for the selector-backed elementary completeness session
- [x] Do not add hybrid composition seeds in this iteration

### Verification

- [x] Eleven seed-backed elementary lanes replay under a single session
- [x] Selector validation returns eleven strong candidates
- [x] Missing-surface, ambiguous, candidate-only, and rejected counts are zero
- [x] Positive and negative controls are distinguishable by lifecycle selectors
- [x] Appendix E / hierarchy is composition-ready after this pass

### Summary

Complete. `S0010` replays eleven seed-backed elementary examples, `S0011`
selector-validates them, and `S0012` renders visual review artifacts. Selector
outcome:

- Strong candidates: hybrid spark positive/negative, spark-to-expansion
  positive/negative, Appendix E cell division, choice/collapse positive/negative,
  growth pressure positive/negative, transport rerouting, and quiescent no-event
  control.
- No candidates, ambiguous records, rejected records, or missing telemetry
  surfaces.

Post-review status: growth-pressure positive/negative controls are needs-rerun
for growth-specific catalog acceptance. Non-growth elementary motifs and
absence controls remain catalog-eligible. The old growth controls exercised
over-aggressive standalone growth-locus semantics, not the corrected
front-growth dependency.

Appendix E is upgraded by the checked-in seed
`grcl9v3-appendix-e-cell-division-positive.seed.yaml`, which now uses
`target_effective_degree=51` to produce the representative daughter/hierarchy
evidence required by the selector contract.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_examples tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0010 --steps 3 --source-mode landscape_seed_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0011 --source-session-ids S0010
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0012 --selector-session-id S0011
```

## Iteration 8.2.3. Hessian Backend Diagnostic Probe

### Goal

Probe where the GRC9V3 row-basis diagonal Hessian and weighted least-squares
Hessian equations diverge most, without promoting Hessian backend choice into
GRCL-9V3 source ontology.

### Checks

- [x] Add a replay source mode for paired Hessian backend diagnostics
- [x] Reuse existing seed-backed GRCL-9V3 sources as the graph/source basis
- [x] Generate paired runtime lanes for:
  - anisotropic spark
  - expansion gate
  - saddle choice
  - transport corridor
  - quiescent isotropic control
- [x] Run each pair with `row_basis_diagonal`
- [x] Run each pair with `weighted_least_squares`
- [x] Keep source documents manifest-valid by storing diagnostic selector intent
  as runtime-probe notes rather than replacing source selector contracts
- [x] Add source-selector expansions for Hessian diagnostic validation
- [x] Write a pair report ranking metric divergence
- [x] Replay, selector-score, and visualize the probe session

### Verification

- [x] `S0013` replay has ten lanes and five complete pairs
- [x] `S0014` selector validation has ten strong candidates
- [x] `S0015` visual review renders all ten records as supporting evidence
- [x] The pair report records no lifecycle event-count deltas
- [x] The pair report ranks `expansion_gate` as the largest metric divergence
- [x] Runtime Hessian comparison remains diagnostic-only

### Summary

Complete. `S0013` replays five paired runtime diagnostic configurations over
existing seed-backed GRCL-9V3 sources. `S0014` validates all ten backend lanes
as strong candidates with no missing surfaces, and `S0015` renders visual
review artifacts.

The diagnostic report is:

```text
outputs/grcl9v3/lowering/sessions/S0013/reports/hessian_backend_probe_report.json
```

Observed divergence ranking:

1. `expansion_gate`
2. `anisotropic_spark`
3. `transport_corridor`
4. `saddle_choice`
5. `quiescent_isotropic`

The largest deltas are in row-basis differential fields, especially
`current_min_signed_hessian_min`. Tensor fields and lifecycle event counts stay
stable across the backend pairs in this probe. This supports using
`row_basis_diagonal` as the default backend for Iteration 8.3 composition while
keeping backend comparison available as a diagnostic mode.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0013 --steps 3 --source-mode hessian_backend_probe
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0014 --source-session-ids S0013
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0015 --selector-session-id S0014
```

## Iteration 8.3. Hybrid Composition From Proven Seed Examples

### Goal

Compose already-proven elementary GRCL-9V3 seed-backed examples into hybrid
examples. This iteration should increase complexity; it should not repair
missing elementary seed signatures from 8.2.

### Checks

- [x] Select only 8.2 elementary seed-backed examples that are strong
  selector-backed candidates, or explicitly mark any diagnostic exception
- [x] Add a spark + expansion hybrid seed once both elementary signatures are
  proven
- [x] Add an expansion + growth hybrid seed once both elementary signatures are
  proven
- [x] Add a choice/collapse + basin-structure hybrid seed once the elementary
  choice/collapse seed is proven
- [x] Add an Appendix E / hierarchy hybrid seed using the strong elementary
  Appendix E evidence from Iteration 8.2.2
- [x] Use `row_basis_diagonal` as the default backend unless a composed seed is
  explicitly marked as a Hessian diagnostic comparison
- [x] Record composed-source ancestry for each hybrid seed
- [x] Keep all failed tuning attempts replayable
- [x] Render visuals for the hybrid composition session

### Verification

- [x] Each hybrid seed lists its source elementary seed ancestry
- [x] Hybrid selector reports record explicit pass/miss outcomes
- [x] Weak or ambiguous records are not promoted by visuals alone
- [x] Tests cover seed extraction, lowering, replay, selectors, and visuals

### Summary

Iteration 8.3 is complete. Added four seed-backed hybrid compositions:

- `legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-spark-expansion-growth.seed.yaml`
- `grcl9v3-hybrid-choice-transport.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-appendix-e-growth.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-full-composition.seed.yaml`

`S0016` replays the four composed seeds for three steps. All replays are
deterministic (`replay_step_rows_match`, `replay_event_rows_match`, and
`replay_digest_match` are true). `S0017` validates all four records as strong
candidates with zero missing surfaces and zero ambiguous records. `S0018`
renders all four visual records; every rendered lowered graph is connected and
visuals remain supporting-only evidence.

The strongest lane is `hybrid_full_composition`, which emits:

- `hybrid_spark_candidate`: 1
- `hybrid_mechanical_expansion`: 1
- `hybrid_spark_completed`: 1
- `growth`: 64
- `choice_detected`: 4
- `collapse`: 5

The composed Appendix E seeds retain Appendix E source terms, but selector
expectations use generic `hybrid_expansion_events` in this iteration because
`representative_appendix_e_summary` is intentionally fixture-specific to the
standalone representative Appendix E lane.

Post-review status: hybrid lanes containing growth are needs-rerun for their
growth claims. Their spark, expansion, Appendix E, transport, and
choice/collapse evidence can still be reviewed independently where selectors
support that separation. The growth-bearing hybrids used the over-aggressive
legacy growth-locus model, so interior growth density in those runs should not
be read as paper-facing front growth.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0016 --steps 3 --source-mode landscape_seed_examples --fixture hybrid_spark_expansion_growth_composition --fixture hybrid_choice_transport_composition --fixture hybrid_appendix_e_growth_composition --fixture hybrid_full_composition
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0017 --source-session-ids S0016
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0018 --selector-session-id S0017
```

## Iteration 8.4. ComposingCells-Aligned Hybrid Seeds

### Goal

Add composed-cell GRCL-9V3 seeds that use the GRCL vocabulary and
`2026-02-ComposingCells.md` style rather than isolated mechanism probes.

### Checks

- [x] Add ComposingCells-aligned GRCL-9V3 seed paths
- [x] Add boundary ridge / membrane hybrid seed
- [x] Add internal valley / transport-pressure hybrid seed
- [x] Add nested basin / plateau / hierarchy seed
- [x] Add saddle branch / tensor-Hessian instability seed
- [x] Add refinement cell with expansion and budget-partition intent
- [x] Add choice/collapse cell seed
- [x] Add Appendix E cell-division seed
- [x] Use neutral seed primitive types such as `basin`, `plateau`, `ridge`,
  `valley`, and `saddle`
- [x] Map each composed-cell seed to a GRCL-9V3 source/lowering manifest entry
- [x] Keep Phase T-GRC9V3 telemetry concepts as selector expectations or
  observed evidence, not source claims
- [x] Replay composed-cell seeds as a separate session
- [x] Render visualizations for the composed-cell session

### Verification

- [x] Seed files load through the common `LandscapeSeed` loader
- [x] Extracted examples compile to `GRCL9V3SourceDocument`
- [x] Compiled sources lower to connected `GRC9V3State` graphs
- [x] Selector reports pass or record explicit misses
- [x] Visual artifacts exist and preserve source/runtime boundary language

### Summary

Iteration 8.4 is complete. Added seven ComposingCells-aligned GRCL-9V3 seed
examples:

- `grcl9v3-cell-boundary-membrane-spark.seed.yaml`
- `grcl9v3-cell-internal-valley-growth-transport.seed.yaml`
- `grcl9v3-cell-nested-basin-hierarchy.seed.yaml`
- `grcl9v3-cell-saddle-tensor-choice.seed.yaml`
- `grcl9v3-cell-refinement-budget-expansion.seed.yaml`
- `grcl9v3-cell-choice-collapse.seed.yaml`
- `grcl9v3-appendix-e-cell-division-composing-cell.seed.yaml`

`S0019` replays all seven for three steps. All replays are deterministic
(`replay_step_rows_match`, `replay_event_rows_match`, and
`replay_digest_match` are true). `S0020` validates all seven as strong
candidates with zero missing surfaces, zero ambiguous records, and zero
rejections. `S0021` renders all seven visual records with connected lowered
graphs and supporting-only visual boundaries.

Observed event coverage:

- `cell_boundary_membrane_spark`: spark candidate, expansion, completed spark
- `cell_internal_valley_growth_transport`: growth plus transport selectors
- `cell_nested_basin_hierarchy`: spark candidate, expansion, completed spark
- `cell_saddle_tensor_choice`: spark/expansion plus choice/collapse
- `cell_refinement_budget_expansion`: spark candidate, expansion, completed spark
- `cell_choice_collapse`: choice/collapse
- `appendix_e_cell_division_composing_cell`: representative Appendix E
  daughter/hierarchy selectors plus spark/expansion

Budget partition in `cell_refinement_budget_expansion` is a source intent and
telemetry observation surface, not a source-level solved outcome.

Post-review status: ComposingCells examples containing growth are needs-rerun
for growth-specific claims under Iteration 9 front-growth semantics. Non-growth
cell motifs remain eligible for the reviewed catalog. The old growth-bearing
cell examples used over-aggressive growth loci rather than explicitly exposed
spark/refinement front capacity.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0019 --steps 3 --source-mode landscape_seed_examples --fixture cell_boundary_membrane_spark --fixture cell_internal_valley_growth_transport --fixture cell_nested_basin_hierarchy --fixture cell_saddle_tensor_choice --fixture cell_refinement_budget_expansion --fixture cell_choice_collapse --fixture appendix_e_cell_division_composing_cell
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0020 --source-session-ids S0019
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0021 --selector-session-id S0020
```

## Iteration 8.5. Full-Capacity Hybrid Cascade And Robustness

### Goal

Add a complex source-authored GRCL-9V3 seed and a controlled robustness family
that records which hybrid signatures survive targeted source perturbations.

### Checks

- [x] Add one connected GRCL/Morse seed composing multiple supported
  GRCL-9V3 phenomena
- [x] Compile multiple GRCL-9V3 source construct families from one example
- [x] Lower mixed constructs into one connected `GRC9V3State`
- [x] Preserve GRCL-9V3 source provenance across topology mutation
- [x] Run for a longer window, at least 20 steps unless runtime cost requires
  a documented shorter window
- [x] Require selectors for intended hybrid signatures:
  spark, expansion, growth, choice/collapse, Appendix E or hierarchy,
  tensor/Hessian, transport, and budget/coarse where applicable
- [x] Add targeted perturbations and negative controls
- [x] Add robustness summary JSON/Markdown artifacts
- [x] Add visual matrix or index artifacts when multiple variants are run
- [x] Record passes, misses, ambiguous outcomes, and falsified assumptions
  explicitly

### Verification

- [x] Cascade session is replayable
- [x] Robustness family session is replayable
- [x] Selector reports record all expected signatures or explicit misses
- [x] Visualizations are generated
- [x] No visual-only promotion occurs
- [x] Tests no longer over-assume all robustness controls should pass

### Summary

Complete. Added four full-capacity GRCL-9V3 seed examples:

- `appendix_e_cell_division_full_capacity_cascade`
- `appendix_e_cell_division_full_capacity_low_growth`
- `appendix_e_cell_division_full_capacity_balanced_choice`
- `appendix_e_cell_division_full_capacity_low_growth_balanced_choice`

`S0022` replayed all four lanes for 20 steps with deterministic replay checks.
The baseline cascade emitted 3050 lifecycle events: spark candidate, mechanical
expansion, completed spark, 2873 growth events, 163 choice detections, and 11
collapses. The balanced-choice perturbation remained a strong candidate while
removing choice/collapse events. The low-growth perturbations remained
candidates because `lambda_birth=0.02` reduced but did not eliminate growth
over 20 steps. This falsified the stronger no-growth expectation and is
recorded in `outputs/grcl9v3/lowering/sessions/S0023/reports/robustness_summary.md`.

`S0023` produced two strong candidates, two candidates, zero missing surfaces,
and zero rejected records. `S0024` rendered visual artifacts for all four
records with no visual-only promotion.

Post-review status: full-capacity cascade and low-growth robustness claims are
needs-rerun for growth-specific acceptance. The old runs remain useful
diagnostics about bounded growth pressure and hybrid interactions. Their large
growth counts are a symptom of the over-aggressive legacy growth-locus model
and must not be interpreted as paper-facing front-growth capacity.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0022 --steps 20 --source-mode landscape_seed_examples --fixture appendix_e_cell_division_full_capacity_cascade --fixture appendix_e_cell_division_full_capacity_low_growth --fixture appendix_e_cell_division_full_capacity_balanced_choice --fixture appendix_e_cell_division_full_capacity_low_growth_balanced_choice
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0023 --source-session-ids S0022
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0024 --selector-session-id S0023
```

## Iteration 8.5.1. Calibrated Growth Robustness

### Goal

Reuse the 8.5 finding that low `lambda_birth` reduces but does not eliminate
growth, and run calibrated full-capacity probes that separate bounded growth,
exact zero-birth no-growth, and structural no-growth.

### Checks

- [x] Add ultra-low birth full-capacity probe
- [x] Add exact zero-birth full-capacity probe
- [x] Add structural closed-growth full-capacity probe
- [x] Add combined zero-birth and balanced-choice probe
- [x] Score ultra-low birth as bounded growth, not no-growth
- [x] Score zero-birth and closed-growth probes as no-growth controls
- [x] Keep all examples source-authored through the 8.1 compiler path
- [x] Preserve comparability with 8.5 full-capacity context

### Verification

- [x] Replay session is deterministic
- [x] Selector validation has no missing surfaces
- [x] Visual review is generated when selector results are informative
- [x] Robustness summary records whether zero-birth and structural no-growth
  differ
- [x] Tests cover the new selector expansion

### Summary

Complete. `S0025` replayed four calibrated full-capacity growth probes for 20
steps. `S0026` validated all four as strong candidates with zero missing
surfaces, and `S0027` rendered visuals for all four records.

Results:

- `appendix_e_cell_division_full_capacity_ultra_low_growth`: 2 growth events,
  41 choice detections, 5 collapses. This is bounded-growth evidence, not
  no-growth.
- `appendix_e_cell_division_full_capacity_zero_birth`: 0 growth events, 41
  choice detections, 5 collapses. Exact zero birth is a true no-growth control.
- `appendix_e_cell_division_full_capacity_closed_growth_port`: 0 growth events,
  22 choice detections, 3 collapses. Structural closed-growth is also a true
  no-growth control.
- `appendix_e_cell_division_full_capacity_zero_birth_balanced_choice`: 0
  growth, 0 choice, and 0 collapse events. Zero birth and balanced choice
  compose independently.

The calibrated summary is recorded in
`outputs/grcl9v3/lowering/sessions/S0026/reports/calibrated_growth_summary.md`.

Post-review status: calibrated growth robustness remains diagnostic. Zero-birth
and closed-growth controls are useful old-model controls, but corrected
front-growth reruns must decide which controls remain paper-facing. These
controls calibrated the over-aggressive legacy growth-locus model, not the
corrected spark/front-capacity topology.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_selector_validation
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0025 --steps 20 --source-mode landscape_seed_examples --fixture appendix_e_cell_division_full_capacity_ultra_low_growth --fixture appendix_e_cell_division_full_capacity_zero_birth --fixture appendix_e_cell_division_full_capacity_closed_growth_port --fixture appendix_e_cell_division_full_capacity_zero_birth_balanced_choice
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0026 --source-session-ids S0025
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0027 --selector-session-id S0026
```

## Iteration 8.6. Multi-Center Collapse And Basin-Assignment Learning

### Goal

Discover and validate a GRCL-9V3 source-authored long-run structure where
multiple comparable growing centers compete, one center becomes selected, and
other centers or saddle regions collapse into it. Learning claims are limited
to runtime-observed basin-assignment learning caused by collapse.

### Scope

This iteration prioritizes correctness over speed. If the current lowerer only
uses the first construct of a kind, extend it safely rather than flattening the
source language into one artificial construct. The target language remains pure
GRCL/Morse-style source preconditions; no source document may inject solved
collapse, solved winner, or solved learning outcomes.

### Checks

- [x] Extend lowerer support for multiple growth loci where safe
- [x] Extend lowerer support for multiple choice/collapse regions where safe
- [x] Reject or document source documents whose repeated constructs remain
  unsupported
- [x] Add multi-center source seed with comparable initial centers
- [x] Add growth-driven multi-center source seed where growth precedes collapse
- [x] Add delayed-collapse source seed intended for a longer window
- [x] Add no-collapse or balanced-control seed for comparison
- [x] Add source notes that learning means basin-assignment learning only
- [x] Add selector expansion for growth-before-collapse evidence
- [x] Add selector expansion for nonzero learning-state evidence
- [x] Add selector expansion for final collapsed sink/center evidence
- [x] Add bounded high-growth replay session at 20 steps
- [x] Preserve high growth pressure instead of lowering it for the accepted
  replay
- [x] Add selector validation over the long-run session
- [x] Add visual review marking competing centers, collapse sources, and
  winning sink/center
- [x] Add collapse-learning summary JSON/Markdown artifact

### Verification

- [x] Replay session is deterministic
- [x] Selector validation has no missing surfaces
- [x] At least one lane records growth before collapse
- [x] At least one lane records `learning_state_count > 0`
- [x] At least one lane records a final collapsed sink/center
- [x] Balanced/no-collapse control is preserved as absence evidence or
  explicitly marked as a miss
- [x] Visuals are supporting evidence only
- [x] Tests cover repeated-construct lowering or the explicit unsupported path
- [x] Tests cover new selector expansions

### Planned Sessions

- `S0028`: diagnostic replay with calibrated lower growth pressure
- `S0029`: diagnostic selector validation
- `S0030`: accepted 20-step high-growth replay
- `S0031`: accepted selector validation
- `S0032`: visual review

### Summary

Complete. `S0030` preserves the high-growth source intent over a bounded
20-step replay. `multi_center_collapse_learning` is a strong candidate with
`growth=1658`, `choice_detected=110`, and `collapse=4`; selectors confirm
growth-before-collapse, nonzero learning state, and a final collapsed sink.
`multi_center_delayed_collapse_learning` remains a candidate because collapse
and learning occur, but no collapse occurs after the first growth event in the
20-step selector window. `multi_center_balanced_no_collapse` is a strong
absence-control candidate with one growth event and no choice/collapse events.
Summary artifacts are in
`outputs/grcl9v3/lowering/sessions/S0031/reports/collapse_learning_summary.*`.

Post-review status: diagnostic/superseded for paper-facing growth claims.
These sessions tested the legacy executable growth-locus interpretation. They
remain replayable runtime diagnostics, but growth-before-collapse evidence must
be rerun through Iteration 9 front-growth semantics before catalog acceptance.
The observed dense inner-node growth is expected from the over-aggressive
legacy model and is not paper-facing.

## Iteration 8.6.1. Collapse-Learning Timing And Sink Provenance Probe

### Goal

Refine the 8.6 delayed multi-center result by isolating growth pressure as a
runtime diagnostic variable over the same source-authored GRCL-9V3 structure.
The goal is to learn when delayed collapse becomes growth-before-collapse, and
whether the final collapsed sink is source-declared or runtime-grown.

### Scope

This is a diagnostic probe, not a new source ontology layer. It may use
`runtime_diagnostic_overrides.lambda_birth` in replay source documents, but it
must preserve the same lowered GRCL-9V3 source structure and the same source
claim boundary: no source document declares solved winners, solved collapse, or
solved learning.

### Checks

- [x] Add collapse-learning probe source mode
- [x] Generate deterministic variants over
  `multi_center_delayed_collapse_learning`
- [x] Sweep `lambda_birth` across at least four values
- [x] Record first growth event/step
- [x] Record first collapse event/step
- [x] Record first collapse-after-growth event/step
- [x] Record `learning_state_count`
- [x] Record final collapsed sink id
- [x] Classify final collapsed sink as source-declared or runtime-grown
- [x] Write probe report JSON
- [x] Run selector validation for probe lanes
- [x] Preserve replay commands in session manifests

### Verification

- [x] Replay session is deterministic
- [x] Selector validation has no missing surfaces
- [x] At least one probe lane is a strong growth-before-collapse candidate
- [x] Probe report identifies the first strong `lambda_birth`
- [x] Probe report identifies any runtime-grown final sink
- [x] Tests cover the probe source mode and report shape

### Planned Sessions

- `S0035`: collapse-learning lambda sweep replay
- `S0036`: selector validation

### Summary

Complete. `S0035` replays four 50-step variants over the delayed
multi-center structure. After correcting event-order diagnostics to compare
`(step_index, event_index)`, `S0036` validates all four lanes as strong
candidates with no missing surfaces. The first strong growth-before-collapse
value in the sweep is `lambda_birth=0.05`; all four lanes produce
growth-before-collapse ordering and finish with runtime-grown collapsed sinks,
which strengthens the narrow basin-assignment-learning interpretation. Reports:
`outputs/grcl9v3/lowering/sessions/S0035/reports/collapse_learning_probe_report.*`
and `outputs/grcl9v3/lowering/sessions/S0036/reports/selector_validation_report.json`.

Post-review status: diagnostic/superseded for paper-facing growth claims. The
lambda sweep remains useful old-model runtime evidence, but it is not eligible
for the reviewed catalog until reproduced from explicit front capacity. It
sweeps the over-aggressive legacy growth-locus activation pressure.

## Iteration 8.6.2. Recurrent Growth-Collapse Relay Probe

### Goal

Test whether the runtime-grown collapsed sinks observed in 8.6.1 participate in
a recurrent relay pattern: a node appears as a growth child, later appears as a
collapsed sink, and later appears as a growth parent.

### Scope

This is a runtime diagnostic over the delayed multi-center source structure. It
does not claim a topological cycle, because GRC9V3 growth is monotone in
topology. It also does not claim scale-free behavior. The full relay claim is
reserved for same-node ordered evidence; partial relay evidence must be reported
separately.

### Checks

- [x] Add recurrent relay probe source mode
- [x] Generate deterministic relay variant over
  `multi_center_delayed_collapse_learning`
- [x] Use `lambda_birth=0.20` as the first strong 8.6.1 threshold
- [x] Run a 100-step replay window
- [x] Record growth-child-later-collapsed-sink count
- [x] Record collapsed-sink-later-growth-parent count
- [x] Record full same-node relay count
- [x] Add selector expansion for relay diagnostics
- [x] Add field-backed selectors for partial and full relay evidence
- [x] Write relay probe report JSON/Markdown
- [x] Run selector validation
- [x] Preserve partial-vs-full relay distinction in summary

### Verification

- [x] Replay session is deterministic
- [x] Selector validation has no missing surfaces
- [x] Partial relay evidence is recorded if present
- [x] Full relay evidence is recorded only when the same node satisfies all
  roles in order
- [x] Tests cover relay source mode and selector expansion

### Planned Sessions

- `S0037`: exploratory 100-step replay over the `lambda_birth=0.20` probe
- `S0038`: accepted relay replay
- `S0039`: selector validation

### Summary

Complete. `S0038` replays the `lambda_birth=0.20` relay probe for 100 steps
and `S0039` validates selectors with no missing surfaces. The run records
`growth=1247`, `choice_detected=2908`, and `collapse=467`. After correcting
event-order diagnostics to compare `(step_index, event_index)`, it records full
same-node relay evidence: `80` nodes appear as growth children and later
collapsed sinks, `4` collapsed sinks later act as growth parents, and `3` nodes
complete the full growth-child -> collapsed-sink -> growth-parent chain.
Reports:
`outputs/grcl9v3/lowering/sessions/S0038/reports/growth_collapse_relay_probe_report.*`
and `outputs/grcl9v3/lowering/sessions/S0039/reports/selector_validation_report.json`.

Post-review status: diagnostic/superseded for paper-facing growth claims. The
same-node relay is an old standalone-growth result and must be rerun under
front-capacity semantics before it can become accepted source evidence. The
relay relied on over-aggressive inner growth and cannot be treated as a
paper-facing front-growth relay.

## Iteration 8.6.3. Relay-Port Sink-Then-Source Geometry Probe

### Goal

Test the geometry inferred from 8.6.2: a birth-port chamber where the
runtime-grown child can first act as a sink/collapse target and later acquire
outward flux as a growth parent.

### Scope

This is still a runtime diagnostic over source-declared geometry. It does not
change GRC9V3 runtime equations and does not claim a solved cycle in the source
document. The source declares calibrated relay-port support and a weak outlet;
telemetry must prove any same-node relay.

### Checks

- [x] Add relay-port growth-locus profile handling in the lowerer
- [x] Add deterministic `relay_port_probe` source mode
- [x] Generate variants over the delayed multi-center source
- [x] Sweep support strength, `alpha_seed`, `w_bond`, and `lambda_birth`
- [x] Preserve partial/full relay diagnostics from 8.6.2
- [x] Write relay-port probe report JSON
- [x] Run selector validation
- [x] Preserve same-node full relay as the acceptance condition

### Verification

- [x] Replay source mode is deterministic
- [x] Selector validation has no missing surfaces
- [x] Full relay is recorded only for same-node ordered evidence
- [x] Tests cover relay-port source mode

### Planned Sessions

- `S0040`: relay-port geometry replay
- `S0041`: selector validation

### Summary

Complete. `S0040` replays three relay-port variants for 100 steps each and
`S0041` validates selectors with no missing surfaces. The relay-port scaffold
increases the growth-child -> collapsed-sink half of the relay (`85`, `150`,
and `221` ordered cases), but none of the three variants produces a
collapsed-sink -> later-growth-parent case or a full same-node relay. This
shows the relay-port geometry is useful for sink capture but too absorbing for
the second source-facing phase; the simpler 8.6.2 delayed multi-center geometry
remains the stronger full-relay example.

Post-review status: diagnostic/superseded for paper-facing growth claims. The
relay-port geometry remains a design probe until rerun from corrected
front-growth source declarations. The probe still used the over-aggressive
legacy growth-locus activation model.

## Iteration 9. Growth Semantics Correction And Rerun Gate

### Goal

Correct GRCL-9V3 growth semantics against the 2026-04-GRC-9 paper and rerun the
affected growth-dependent source evidence without rewriting historical
sessions. Growth may still use the paper's outward-flux birth pressure, but
paper-facing source growth must fill explicit front capacity and the chosen port
must be the deterministic lowest-index inactive port.

### Scope

This iteration is an erratum and rerun gate. It preserves Iteration 8.x outputs
only for replaying and debugging the old behavior; those outputs are not
evidence for paper-facing GRCL-9V3 motifs.

## Iteration 9.1. Growth Source Semantics Correction

### Goal

Fix what `growth_locus` means before generating any corrected evidence.
Paper-facing GRCL-9V3 growth must be a front-growth annotation/capacity
declaration tied to spark/refinement-created inactive boundary capacity, not an
independent source construct that can create nodes wherever an inactive port
exists.

### Checks

- [x] Add growth-semantics erratum note to the plan/checklist
- [x] Update source vocabulary so executable growth is a front-growth
  annotation/capacity declaration, not an independent solved source mechanism
- [x] Update lowering so paper-facing growth declarations attach to explicit
  spark/refinement/front-created inactive capacity
- [x] Preserve the deterministic lowest-index inactive port rule
- [x] Preserve outward-flux birth pressure only as parent/birth activation, not
  as port-selection semantics
- [x] Add telemetry or replay metadata for growth parent capacity source
- [x] Add selector checks for corrected front-growth provenance
- [x] Reject or downgrade standalone executable `growth_locus` for
  paper-facing source evidence
- [x] Preserve legacy standalone growth-locus behavior only as diagnostic mode

### Verification

- [x] Source schema/lowering rejects standalone paper-facing growth claims
- [x] Corrected growth constructs preserve source/runtime boundaries
- [x] Tests cover front-capacity provenance and lowest-index port behavior
- [x] Tests cover legacy diagnostic growth-locus status

### Summary

Complete. Source `growth_locus` now carries explicit growth semantics:
`legacy_growth_locus` for diagnostic old-model records and `front_capacity` for
paper-facing corrected growth. Paper-facing validation rejects standalone
legacy growth claims. Lowering records front-growth eligible ports, capacity
source provenance, legacy growth ids, and growth semantics status. Replay and
checkpoint telemetry mirror these fields, selector validation exposes
`front_growth_provenance_present`, and GRC9V3 growth can be gated by
`growth_parent_eligibility = "grcl9v3_front_capacity"` so probabilistic birth
activation applies only after front-capacity eligibility is established.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_schema tests.models.test_grc_9_v3_grcl9v3_lowering
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_import_smoke tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_examples tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering
```

## Iteration 9.2. Corrected Growth Reruns

### Goal

Use the corrected Iteration 9.1 semantics to rerun affected growth-dependent
GRCL-9V3 examples and produce the only growth evidence eligible for the
reviewed catalog.

### Checks

- [x] Mark Iteration 8.2-8.5 growth-dependent claims as needs-rerun for growth
  evidence while preserving non-growth evidence
- [x] Mark Iteration 8.6-8.6.3 relay/learning growth claims as
  diagnostic/superseded
- [x] Preserve old sessions as replayable history without rewriting artifacts
- [x] Define corrected 9.2.x replay source-mode and session naming conventions
- [x] Update ExperimentalLog with the 9.2 rerun-gate session and require 9.2.x
  corrected rerun sessions to append their own rows
- [x] Require selector validation over every corrected rerun batch
- [x] Require visual review for corrected selector-backed sessions
- [x] Require `front_growth_provenance_present` in corrected growth selector
  reports
- [x] Record which old growth claims are superseded, replaced, or still
  diagnostic only

### Verification

- [x] 9.2 records no accepted corrected growth runs; executable corrected runs
  are deferred to 9.2.1-9.2.5
- [x] Every future accepted growth event must link to an explicit
  front-capacity source
- [x] No accepted growth motif may depend on legacy standalone growth-locus
  semantics
- [x] Non-growth evidence from earlier sessions remains catalog-eligible
- [x] Old growth-heavy sessions remain discoverable as diagnostic history
- [x] Corrected selector reports must have no missing front-growth provenance
  surfaces

### Summary

Complete as a rerun gate. `S0042` records the corrected growth-rerun policy,
affected legacy sessions, catalog eligibility rules, and 9.2.x batch structure.
No runtime telemetry was generated in 9.2. Executable corrected reruns begin in
9.2.1, and each 9.2.x rerun must append its own ExperimentalLog row, run
selector validation, and render visual review when selector-backed.

Artifacts:

- `outputs/grcl9v3/lowering/sessions/S0042/session_manifest.json`
- `outputs/grcl9v3/lowering/sessions/S0042/reports/growth_rerun_gate_report.json`
- `outputs/grcl9v3/lowering/sessions/S0042/reports/growth_rerun_gate_summary.md`

## Iteration 9.2.1. Corrected Elementary Growth Seeds

### Goal

Rebuild the elementary 8.2/8.2.1/8.2.2 growth examples using corrected
front-capacity semantics.

### Checks

- [x] Add corrected growth positive seed/control
- [x] Add corrected growth negative or no-growth control
- [x] Compile corrected sources with `growth_semantics = "front_capacity"`
- [x] Gate replay with `growth_parent_eligibility = "grcl9v3_front_capacity"`
- [x] Selector-score corrected elementary growth lanes
- [x] Render corrected elementary growth visuals

### Verification

- [x] Corrected growth event has front-capacity provenance
- [x] Corrected no-growth control does not rely on legacy growth-locus
  semantics
- [x] `front_growth_provenance_present` passes for growth-positive evidence
- [x] Corrected elementary session is deterministic

### Summary

Complete. Added two corrected elementary front-growth seeds:

- `grcl9v3-corrected-front-growth-positive.seed.yaml`
- `grcl9v3-corrected-front-growth-no-growth.seed.yaml`

`S0043` replays both for three steps under corrected front-capacity semantics.
The positive lane emits exactly one `growth` event and no choice/collapse
events; the no-growth control emits no lifecycle events. `S0044` validates both
as strong candidates with no missing surfaces. Both lanes pass
`front_growth_provenance_present`, and the no-growth control passes
`no_growth_events`. `S0045` renders supporting-only visual review for both
records.

Artifacts:

- `outputs/grcl9v3/lowering/sessions/S0043/session_manifest.json`
- `outputs/grcl9v3/lowering/sessions/S0044/reports/selector_validation_report.json`
- `outputs/grcl9v3/lowering/sessions/S0045/reports/visual_review_report.json`

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0043 --steps 3 --source-mode landscape_seed_examples --fixture corrected_front_growth_positive_control --fixture corrected_front_growth_no_growth_control
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0044 --source-session-ids S0043
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0045 --selector-session-id S0044
```

## Iteration 9.2.2. Corrected Hybrid Growth Compositions

### Goal

Rebuild the 8.3 growth-bearing hybrid compositions with corrected front-growth
semantics.

### Checks

- [x] Rebuild spark/expansion/growth hybrid
- [x] Rebuild Appendix E/growth hybrid if still meaningful
- [x] Rebuild full hybrid composition with corrected growth
- [x] Keep non-growth evidence separable from corrected growth evidence
- [x] Selector-score corrected hybrid lanes
- [x] Render corrected hybrid visuals

### Verification

- [x] Growth-bearing hybrid events link to front-capacity provenance
- [x] Spark/expansion/choice/transport evidence remains independently visible
- [x] No hybrid growth claim depends on legacy standalone growth-locus
  semantics

### Summary

Completed in `S0046` / `S0047` / `S0048`.

Added corrected landscape seed examples:

- `configs/landscapes/seed/grcl9v3-corrected-hybrid-spark-expansion-growth.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-hybrid-appendix-e-growth.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-hybrid-full-composition.seed.yaml`

`S0046` replayed the three corrected hybrid lanes for three steps. The
spark/expansion/growth and Appendix E/growth lanes each emitted exactly one
growth event plus the hybrid spark/expansion/completion sequence. The full
composition emitted the same bounded growth event and retained choice,
collapse, and transport evidence.

`S0047` selector validation scored all three lanes as strong candidates with
no missing telemetry surfaces. Each lane passed
`front_growth_provenance_present`, and no lane reported legacy growth-locus
ids. `S0048` rendered supporting-only visuals for all three corrected motifs.

Replay commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0046 --steps 3 --source-mode landscape_seed_examples --fixture corrected_hybrid_spark_expansion_growth_composition --fixture corrected_hybrid_appendix_e_growth_composition --fixture corrected_hybrid_full_composition
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0047 --source-session-ids S0046
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0048 --selector-session-id S0047
```

## Iteration 9.2.3. Corrected ComposingCells Growth Seeds

### Goal

Rebuild the 8.4 ComposingCells-aligned growth examples using GRCL/Morse
front-capacity language.

### Checks

- [x] Rebuild internal valley / growth / transport seed with front annotation
- [x] Rebuild any cell seed whose growth claim was growth-dependent
- [x] Preserve ridge, valley, boundary stratum, and refinement-front vocabulary
- [x] Selector-score corrected ComposingCells growth lanes
- [x] Render corrected ComposingCells visuals

### Verification

- [x] Cell-internal growth is tied to explicit front/refinement capacity
- [x] Non-growth cell motifs remain separately reviewable
- [x] Corrected ComposingCells session is deterministic

### Summary

Completed in `S0049` / `S0050` / `S0051`.

Added corrected ComposingCells growth seed:

- `configs/landscapes/seed/grcl9v3-corrected-cell-internal-valley-growth-transport.seed.yaml`

Only `cell_internal_valley_growth_transport` had a direct ComposingCells
growth claim in the 8.4 batch. The other ComposingCells examples remain
reviewable as non-growth cell motifs. The corrected seed keeps the GRCL/Morse
surface vocabulary of ridge, valley, boundary stratum, and refinement locus,
but changes the growth claim to explicit `front_capacity` semantics tied to a
refinement-front construct.

`S0049` replayed the corrected cell lane for three steps and produced exactly
one bounded growth event. `S0050` selector validation scored it as a strong
candidate with no missing surfaces; it passed growth, front-growth provenance,
transport, and no-choice/collapse selectors. `S0051` rendered supporting-only
visuals.

Replay commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0049 --steps 3 --source-mode landscape_seed_examples --fixture corrected_cell_internal_valley_growth_transport
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0050 --source-session-ids S0049
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0051 --selector-session-id S0050
```

## Iteration 9.2.4. Corrected Full-Capacity Cascade And Robustness

### Goal

Rebuild 8.5/8.5.1 full-capacity cascade and robustness probes under
front-capacity gating.

### Checks

- [x] Add corrected full-capacity cascade seed
- [x] Add bounded-growth perturbation
- [x] Add zero-birth control
- [x] Add closed-front control
- [x] Add balanced-choice composition control
- [x] Selector-score corrected robustness lanes
- [x] Render corrected robustness visuals
- [x] Write corrected robustness summary JSON/Markdown

### Verification

- [x] Growth density is front-capacity bounded
- [x] Zero-birth and closed-front controls are distinguished
- [x] Balanced-choice control remains separable from growth controls
- [x] Corrected robustness session is deterministic

### Summary

Completed in `S0052` / `S0053` / `S0054`.

Added corrected full-capacity robustness seeds:

- `configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-cascade.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-bounded-growth.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-zero-birth.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-closed-front.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-appendix-e-cell-division-full-capacity-balanced-choice.seed.yaml`

`S0052` replayed the five corrected robustness lanes for three steps.
Growth-positive lanes emitted one front-capacity growth event; bounded-growth
and zero-birth lanes emitted no growth in the window while preserving explicit
front-capacity provenance; closed-front emitted no growth and no front-growth
provenance. This distinguishes zero-birth from a structurally closed front.

`S0053` selector validation scored all five lanes as strong candidates with no
missing surfaces. `S0054` rendered supporting-only visuals for all five lanes.
Additional summary artifacts:

- `outputs/grcl9v3/lowering/sessions/S0052/reports/corrected_robustness_summary.json`
- `outputs/grcl9v3/lowering/sessions/S0052/reports/corrected_robustness_summary.md`

Replay commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0052 --steps 3 --source-mode landscape_seed_examples --fixture appendix_e_cell_division_corrected_full_capacity_cascade --fixture appendix_e_cell_division_corrected_full_capacity_bounded_growth --fixture appendix_e_cell_division_corrected_full_capacity_zero_birth --fixture appendix_e_cell_division_corrected_full_capacity_closed_front --fixture appendix_e_cell_division_corrected_full_capacity_balanced_choice
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0053 --source-session-ids S0052
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0054 --selector-session-id S0053
```

## Iteration 9.2.5. Corrected Collapse/Learning/Relay Feasibility

### Goal

Determine whether the 8.6 growth-before-collapse, learning, and relay patterns
remain feasible under corrected front-growth semantics.

### Checks

- [x] Rebuild a corrected multi-center collapse/learning probe if feasible
- [x] Rebuild a corrected delayed-collapse timing probe if feasible
- [x] Rebuild a corrected relay probe if feasible
- [x] Preserve old 8.6.* as alternative-development diagnostics if not
  reproducible
- [x] Selector-score corrected feasibility probes
- [x] Render corrected feasibility visuals when selector-backed
- [x] Record accepted/candidate/diagnostic-only outcome for each 8.6 family

### Verification

- [x] Any corrected growth-before-collapse claim links to front capacity
- [x] Any corrected relay claim uses same-node ordered evidence
- [x] Failed corrected relay attempts are recorded as diagnostic, not hidden
- [x] Corrected feasibility session is deterministic

### Summary

Completed with:

- `configs/landscapes/seed/grcl9v3-corrected-multi-center-collapse-learning.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-multi-center-delayed-collapse-learning.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-multi-center-relay-attempt.seed.yaml`

`S0055` replayed the three corrected feasibility lanes for 20 steps.
`corrected_multi_center_collapse_learning` emitted two growth events, one
collapse event, and 29 choice detections. `corrected_multi_center_delayed_collapse_learning`
emitted two growth events, four collapse events, and nine choice detections.
Both lanes preserve explicit `front_capacity` provenance and demonstrate that
growth-before-collapse plus basin-assignment learning remains feasible after the
paper-facing growth correction.

`corrected_multi_center_relay_attempt` emitted one growth event, two collapse
events, and 19 choice detections, but did not satisfy the same-node relay
selectors `growth_child_later_collapsed_sink`,
`collapsed_sink_later_growth_parent`, or `full_growth_collapse_relay`. It is
therefore recorded as diagnostic-only rather than accepted relay evidence.

`S0056` selector validation scored the two collapse/learning lanes as strong
candidates and the relay attempt as a candidate with explicit missing relay
selectors. `S0057` rendered supporting-only visuals for all three records.
Additional summary artifacts:

- `outputs/grcl9v3/lowering/sessions/S0055/reports/corrected_feasibility_summary.json`
- `outputs/grcl9v3/lowering/sessions/S0055/reports/corrected_feasibility_summary.md`

Old 8.6.* results remain alternative-development diagnostics only where they
depended on over-aggressive standalone growth.

Replay commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0055 --steps 20 --source-mode landscape_seed_examples --fixture corrected_multi_center_collapse_learning --fixture corrected_multi_center_delayed_collapse_learning --fixture corrected_multi_center_relay_attempt
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0056 --source-session-ids S0055
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0057 --selector-session-id S0056
```

## Iteration 9.2.5.1. Corrected Propagated-Front Relay Reproduction

### Goal

Try to reproduce the old 8.6.2 full same-node relay under corrected
front-capacity semantics without accepting legacy standalone growth.

### Checks

- [x] Run the existing corrected relay attempt over a longer window
- [x] Add a bounded propagated-front relay seed
- [x] Keep propagated growth source-declared and front-capacity gated
- [x] Require the same 8.6.2 relay selectors
- [x] Record partial relay evidence separately from full relay evidence
- [x] Render supporting-only visuals for the best corrected attempt

### Verification

- [x] Long-window baseline remains deterministic
- [x] Propagated-front attempt remains deterministic
- [x] Full relay is not claimed unless
  `full_growth_collapse_relay` passes
- [x] Failed full-relay reproduction is recorded, not hidden

### Summary

Completed with:

- `configs/landscapes/seed/grcl9v3-corrected-propagated-front-relay.seed.yaml`

`S0058` reran `corrected_multi_center_relay_attempt` for 100 steps. The lane
emitted one growth event, two collapse events, and 99 choice detections, but no
relay selectors passed. This proves that the 20-step 9.2.5 relay miss is not
simply a short-window artifact.

`S0066` replayed `corrected_propagated_front_relay` for 100 steps. The lane
emitted two growth events, two collapse events, and 11 choice detections.
`S0067` selector validation passed `growth_child_later_collapsed_sink`, but
still failed `collapsed_sink_later_growth_parent` and
`full_growth_collapse_relay`. `S0070` rendered supporting-only visuals for the
partial relay record.

Exploratory sessions `S0060`-`S0065` tested one-generation, two-generation, and
higher-transfer propagated-front variants. `S0068`/`S0069` tested an explicit
propagated-front outlet scaffold, which regressed the relay evidence. The best
corrected result remains partial relay, not full 8.6.2 reproduction.

Additional summary artifacts:

- `outputs/grcl9v3/lowering/sessions/S0066/reports/corrected_relay_reproduction_summary.json`
- `outputs/grcl9v3/lowering/sessions/S0066/reports/corrected_relay_reproduction_summary.md`

Replay commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0058 --steps 100 --source-mode landscape_seed_examples --fixture corrected_multi_center_relay_attempt
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0059 --source-session-ids S0058
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0066 --steps 100 --source-mode landscape_seed_examples --fixture corrected_propagated_front_relay
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0067 --source-session-ids S0066
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9v3_lowering --session-id S0070 --selector-session-id S0067
```

## Iteration 9.2.6. Legacy Growth Seed Quarantine

### Goal

Move over-aggressive standalone-growth GRCL-9V3 seeds out of the normal seed
directory after corrected replacements exist, while preserving replayability
for historical diagnostic sessions.

### Checks

- [x] Create `configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/`
- [x] Move legacy standalone-growth GRCL-9V3 seeds into the quarantine folder
- [x] Keep corrected front-growth seeds in the main seed directory
- [x] Keep non-growth GRCL-9V3 seeds in the main seed directory
- [x] Exclude quarantined legacy growth seeds from normal default seed
  discovery
- [x] Add or preserve explicit diagnostic loading for quarantined legacy seeds
- [x] Update `configs/landscapes/seed/README.md`
- [x] Update replay documentation for old sessions that reference moved seeds

### Verification

- [x] Default seed tests exclude quarantined over-aggressive growth seeds
- [x] Corrected front-growth seeds remain discoverable by default
- [x] Legacy growth seeds remain replayable through diagnostic path or
  documented path mapping
- [x] No reviewed catalog path treats quarantined growth seeds as paper-facing

### Summary

Completed. The over-aggressive standalone-growth GRCL-9V3 seed files now live
under
`configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/`. Corrected
front-capacity seeds and unaffected non-growth seeds remain in the main seed
directory and are still loaded by `landscape_seed_examples`.

Normal default seed discovery excludes the quarantined files. Historical
diagnostics remain replayable through the explicit source mode
`legacy_growth_landscape_seed_examples`, and the older diagnostic source modes
that depend on the legacy delayed multi-center seed still resolve it through
that diagnostic loader. Replay smoke session `S0071` verifies the legacy path
with deterministic step/event replay.

Replay command:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0071 --steps 1 --source-mode legacy_growth_landscape_seed_examples --fixture multi_center_delayed_collapse_learning
```

## Iteration 10. Reviewed Lowered-Source Catalog

### Goal

Publish reviewed GRCL-9V3 lowered-source motif catalog.

### Checks

- [x] Build reviewed catalog JSON
- [x] Build reviewed catalog Markdown
- [x] Preserve accepted records
- [x] Preserve strong candidates
- [x] Preserve diagnostics
- [x] Preserve rejected/duplicate/needs-rerun records
- [x] Accept growth/front motifs only from Iteration 9 corrected reruns
- [x] Mark old standalone-growth records with diagnostic or superseded status
- [x] Record review history
- [x] Record explicit non-claims

### Implementation Notes

- Implemented reviewed catalog runner:
  - `src/pygrc/telemetry/grcl9v3_lowered_motif_catalog.py`
- Added test coverage:
  - `tests/telemetry/test_grcl9v3_lowered_motif_catalog.py`
- Exported catalog helper from `pygrc.telemetry`:
  - `run_grcl9v3_reviewed_lowered_motif_catalog`
- Current catalog session:
  - `outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json`
  - `outputs/grcl9v3/lowering/sessions/S0072/reports/reviewed_grcl9v3_lowered_motif_catalog_report.json`
  - `outputs/grcl9v3/lowering/sessions/S0072/reports/reviewed_grcl9v3_lowered_motif_catalog_summary.md`
- `S0072` reviews selector sessions:
  - `S0011`, `S0017`, `S0020`, `S0023`, `S0026`, `S0031`,
    `S0036`, `S0039`, `S0041`, `S0044`, `S0047`, `S0050`,
    `S0053`, `S0056`, `S0067`
- Review policy:
  - non-growth records from earlier sessions remain eligible,
  - growth/front records are accepted only with Iteration 9 corrected
    front-growth provenance,
  - older standalone-growth records are preserved as
    `superseded_by_growth_semantics_correction`,
  - visuals are supporting links only and never promote records without
    selector evidence.

### Verification

- [x] Catalog round-trips through JSON
- [x] Every accepted record links source, lowered state, telemetry, and review
  evidence
- [x] No accepted record depends on visuals alone
- [x] No accepted growth record depends on legacy executable growth-locus
  semantics
- [x] `S0072` catalog summary:
  - accepted: `28`
  - strong candidates: `2`
  - superseded legacy-growth records: `26`
  - rejected: `0`
- [x] Focused tests pass:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_lowered_motif_catalog`
- [x] Full GRCL-9V3 slice passes:
  - `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_lowered_motif_catalog tests.landscapes.test_import_smoke tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_examples tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering`
  - `91 tests OK`

### Summary

Completed. GRCL-9V3 now has a reviewed lowered-source motif catalog. `S0072`
accepts 28 records, keeps two corrected relay records as strong candidates,
and preserves 26 old standalone-growth records as superseded diagnostics after
the Iteration 9 growth-semantics correction. The accepted set contains 12
corrected growth/front motifs, all backed by `front_growth_provenance` rather
than legacy executable growth-locus semantics.

## Iteration 11. Closeout And Handoff

### Goal

Close GRCL-9V3 Revision 1 and record follow-up work.

### Checks

- [x] Write closeout note
- [x] Summarize what source constructs are proven
- [x] Summarize source vocabulary gaps
- [x] Summarize runtime/telemetry gaps
- [x] Update `ImplementationPhases.md`

### Implementation Notes

- Added closeout handoff:
  - [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md)
- Updated Phase 7 closeout with a post-core completion update.
- Updated `ImplementationPhases.md` so the Phase 7 post-core track records
  GRCL-9V3 Revision 1 as complete through reviewed lowered-source catalog.
- Closeout anchors the final accepted catalog:
  - `outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json`

### Verification

- [x] Closeout links all replayable sessions
- [x] Closeout does not over-claim source/runtime equivalence

### Summary

Completed. GRCL-9V3 Revision 1 is closed as a source/lowering and evidence
layer. The handoff records implemented source constructs, corrected
front-growth semantics, replayable sessions, reviewed catalog status, explicit
non-claims, and deferred work.
