# GRCL-9V3 Implementation Plan

## Purpose

This document defines the implementation lane for **GRCL-9V3**, the
GRC9V3-specific source and lowering surface that turns authored GRCL/Morse
landscape statements into deterministic `GRC9V3` runtime seed examples.

The purpose is not to create new `GRC9V3` runtime equations.
The purpose is narrower:

- define vocabulary/source constructs for hybrid GRC9V3 phenomena,
- map reviewed runtime motifs into a lowering manifest,
- lower deterministic source examples into connected `GRC9V3` states,
- replay those states through existing GRC9V3 runtime/telemetry/visualization,
- and publish a reviewed source-seed/lowered-motif catalog.

Source may declare structural preconditions and policies.
Source must not declare solved runtime events.

## Inputs

This plan is downstream of:

- [Phase-7-ImplementationPlan.md](./Phase-7-ImplementationPlan.md)
- [Phase-7-EquationMap.md](./Phase-7-EquationMap.md)
- [Phase-7-StepLoop.md](./Phase-7-StepLoop.md)
- [Phase-T-GRC9V3-TelemetryContract.md](./Phase-T-GRC9V3-TelemetryContract.md)
- [Phase-V-GRC9V3-ImplementationPlan.md](./Phase-V-GRC9V3-ImplementationPlan.md)
- [GRC9V3-PhenomenologyDiscovery-Plan.md](./GRC9V3-PhenomenologyDiscovery-Plan.md)
- [GRC9V3-PhenomenologyDiscovery-Checklist.md](./GRC9V3-PhenomenologyDiscovery-Checklist.md)
- [GRCL-9V3-Vocabulary.md](./GRCL-9V3-Vocabulary.md)
- `outputs/grc9v3/phenomenology_discovery/sessions/S0013/expanded_motif_catalog.json`
- `outputs/grc9v3/phenomenology_discovery/sessions/S0014/source_language_handoff.json`

It is also intentionally aligned with the proven source/lowering patterns in:

- [GRCL-9-ImplementationPlan.md](./GRCL-9-ImplementationPlan.md)
- [GRCL-9-ImplementationChecklist.md](./GRCL-9-ImplementationChecklist.md)
- [GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)
- [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)

## Why This Is The Right Next Step

The GRC9V3 runtime, telemetry, visualization, and runtime phenomenology
discovery tracks are now closed enough for a source-language layer:

- S0013 contains an expanded reviewed runtime motif surface,
- S0014 classifies those motifs into source candidates, vocabulary-needed
  records, and runtime-only diagnostics,
- and all handoff entries remain `runtime_evidence_only`.

That means the next question is no longer whether `GRC9V3` can produce the
phenomena. It can.

The next question is whether a source-facing GRCL-9V3 declaration can author
the structural conditions that lead to those phenomena without smuggling in the
observed result.

## Core Boundary

GRCL-9V3 should be implemented as a family-native landscape extension under:

```text
src/pygrc/landscapes/extensions/grcl9v3/
```

It should not be implemented under:

```text
src/pygrc/grcl9v3/
```

Allowed:

- top-level `extensions.grcl9v3`
- primitive-level `extensions.grcl9v3`
- typed GRCL-9V3 source documents
- deterministic lowering into `GRC9V3State`
- provenance metadata on lowered nodes, edges, and cached quantities
- replay through the existing GRC9V3 runtime
- validation through Phase T-GRC9V3 telemetry
- visualization through saved graph checkpoints

Forbidden:

- changing `GRC9V3` runtime equations to make a source seed pass
- injecting solved event histories into source fixtures
- source fields that declare spark, expansion, choice, collapse, growth, or
  daughter-sink confirmation happened
- disconnected lowered graphs
- collapsing GRC9 mechanical and GRCV3 semantic ownership into a single
  untagged source blob
- Lorentzian causal-layer claims
- observer-local claims

## Target Outcome

The first complete GRCL-9V3 slice should prove:

1. GRCL-9V3 source can express at least the accepted source-expression
   candidates from S0014.
2. Source documents validate without running the runtime.
3. Lowered states are connected, deterministic, and preserve provenance.
4. Replayed telemetry matches the expected selector evidence.
5. Visualizations consume saved telemetry/checkpoints, not source claims.
6. A reviewed lowered-source catalog identifies accepted, strong, diagnostic,
   rejected, duplicate, and needs-rerun records.

## S0014 Handoff Policy

S0014 splits 26 expanded GRC9V3 runtime records into:

- 8 source-expression candidates,
- 12 records requiring new source vocabulary,
- 6 runtime-only records.

Revision 1 should start with the 8 source-expression candidates and the
minimum vocabulary-needed controls required to make pass/fail examples useful.

Runtime-only records should not become source constructs in Revision 1:

- Hessian backend comparison stays a runtime comparator.
- Budget preservation stays a runtime invariant/diagnostic.
- Coarse-cache invalidation stays runtime/cache hygiene.

They may appear as expected telemetry or validation side conditions, but not as
source-level ontology.

## Source Construct Set

Revision 1 should implement:

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

Each construct should carry:

- `construct_id`
- `motif_id`
- `source_role`
- `ownership`
- source parameters
- expected telemetry selectors
- explicit non-claims

Ownership values should distinguish:

- `grc9_mechanical`
- `grcv3_semantic`
- `grc9v3_hybrid`
- `shared_runtime`

## Lowering Manifest

The lowering manifest should map S0014 handoff entries into source constructs,
graph preconditions, lowering carriers, and expected telemetry.

Expected first version:

```text
grcl9v3_lowering_manifest_v1
```

Expected source schema version:

```text
grcl9v3.source.v1
```

The manifest should record:

- source motif id,
- source construct kinds,
- required source knobs,
- ownership tags,
- lowering carriers,
- expected telemetry fields,
- pass/fail control roles,
- runtime-only exclusions,
- explicit non-claims.

## Lowering Carriers

Lowered `GRC9V3State` objects should preserve at least:

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

Node and edge payloads should include:

- `grcl9v3_construct_id`
- `grcl9v3_construct_kind`
- `grcl9v3_motif_role`
- `grcl9v3_ownership`
- `grcl9v3_edge_kind` when applicable

Bridge edges should use:

```text
grcl9v3_edge_kind = "bridge"
```

## Artifact Layout

Replayable sessions should live under:

```text
outputs/grcl9v3/lowering/sessions/S0001/
```

The experiment log should live at:

```text
outputs/grcl9v3/lowering/ExperimentalLog.md
```

Each replay session should include:

- `session_manifest.json`
- source fixture copies,
- lowered state payloads,
- telemetry artifacts,
- graph checkpoints,
- selector reports,
- visualization outputs when applicable,
- replay command,
- review summary.

## Iteration Sequence

### Iteration 0: Planning Bootstrap

- Create GRCL-9V3 vocabulary, plan, and checklist.
- Anchor the track in S0013/S0014.
- Record source/runtime boundary and artifact layout.

### Iteration 1: Lowering Manifest Contract

- Implement typed lowering manifest under `src/pygrc/landscapes/extensions/grcl9v3/`.
- Map S0014 source-expression candidates to source constructs.
- Preserve runtime-only records as manifest exclusions.
- Status: complete.
- The default manifest records 8 source-expression candidates, 12 future
  vocabulary records, and 6 runtime-only exclusions from S0014.
- Reviewed motif ids use explicit GRC9V3 motif-id validation, while source
  tokens remain strict snake-case.
- S0014 drift is checked by an explicit manifest-to-handoff validator.
- Selector ids remain tokenized placeholders until Iteration 6 selector
  validation resolves them against field-backed selectors.
- Lowering carriers are constrained to GRCL-9V3 namespaces, and manifest graph
  preconditions reject runtime-result smuggling keys.

### Iteration 2: Source Schema

- Implement `grcl9v3.source.v1` dataclasses.
- Validate source constructs, ownership tags, non-claims, and selector
  expectations.
- Reject runtime-result smuggling.
- Status: complete.
- The schema defines ten Revision 1 construct dataclasses plus bridge, budget,
  and provenance policies.
- Source documents validate and round-trip without constructing the runtime
  `GRC9V3` model.
- Source construct ids remain snake-case, while source `motif_id` values use
  reviewed S0014 motif ids.
- Source documents can be explicitly checked against the lowering manifest via
  `validate_grcl9v3_source_document_against_manifest()`.
- Runtime-result smuggling is rejected in constructs and document notes.
- `executable=false` is reserved for non-executable source declarations and
  requires the `non_executable_source_construct` non-claim.
- The forbidden runtime key list is static in Revision 1 and should be updated
  when Phase T-GRC9V3 or runtime event vocabulary expands.

### Iteration 3: Minimal Source Fixtures

- Author pass/fail source fixtures for spark, expansion, Appendix E,
  choice/collapse, growth, transport, and quiescent controls.
- Keep fixtures source-level; do not serialize runtime state.
- Status: complete.
- The first fixture corpus contains 12 source documents:
  - 5 executable manifest-entry fixtures,
  - 7 future-vocabulary control fixtures.
- Future-vocabulary fixtures are intentionally source-valid but not yet
  executable lowering entries.

### Iteration 4: Lowerer Revision 1

- Lower source fixtures into connected `GRC9V3State` graphs.
- Preserve budget, topology, ownership, and provenance.
- Do not change GRC9V3 runtime equations.
- Status: complete. Revision 1 uses a model-side lowerer that consumes
  `grcl9v3.source.v1` documents and emits native `GRC9V3State` objects with
  GRCL-9V3 provenance, motif registry, assembly-policy, expected-region, and
  bridge-edge caches.

### Iteration 5: Replay Runner

- Replay lowered source fixtures through the existing `GRC9V3` runtime.
- Store telemetry, checkpoints, manifests, and replay commands under
  `outputs/grcl9v3/lowering/`.
- Status: complete. `pygrc.telemetry.grcl9v3_replay` writes replayable
  source-fixture, lowered-state, telemetry, checkpoint, lane report, session
  manifest, replay script, and experimental-log artifacts. `S0001` is the
  initial lowered-source replay smoke session. Runtime event quality remains
  an Iteration 6 selector-validation and Iteration 8 refinement concern.

### Iteration 6: Selector Validation

- Apply Phase T-GRC9V3 field-backed selectors to lowered-source sessions.
- Record pass/fail, missing surfaces, and ambiguous records.
- Status: complete for the first lowered-source replay batch. `S0002`
  validates `S0001` with field-backed selectors, preserving source-facing
  selector ids while expanding them into concrete Phase T-GRC9V3 telemetry
  fields. The selector expansion table is owned by the GRCL-9V3 extension
  layer. The first pass produced 5 strong candidates, 3 candidates, 1
  ambiguous record, 3 weak candidates, and 3 missing surfaces, which feed
  Iteration 8 seed refinement.

### Iteration 7: Visualization Review

- Generate visualization suites from saved telemetry/checkpoints.
- Treat visuals as supporting evidence only.
- Status: complete for the first lowered-source selector batch. `S0003`
  renders the 9 selector-backed motif records from `S0002` and records the 3
  weak selector records as skipped, so visuals cannot promote records without
  telemetry evidence. Each rendered lane includes dense telemetry trajectories,
  event timelines, graph sequences/animations/HTML, and a GRCL-9V3
  source/runtime boundary panel. Visual metadata records deterministic layout
  seeds, explicit selector ids, dense/sparse graph-surface paths, and
  source-derived versus runtime-added graph elements.

### Iteration 8: Source-Seed Discovery And Refinement

GRCL-9V3 should follow the successful GRCL-9 route before reviewed catalog
promotion. The current mechanical source fixtures are useful smoke evidence,
but the catalog should be built from authored GRCL/Morse-like source examples
and checked-in source seeds that actually reproduce the intended hybrid
phenomenology.

Post-review validity note: Iterations 8.2 through 8.6 are now classified as
alternative-development diagnostics wherever their conclusions depend on
growth. They remain useful as replayable evidence of how the legacy
over-aggressive `growth_locus` model develops, and they inform corrected seed
design, but they are not valid paper-facing GRCL-9V3 source evidence until
reproduced under Iteration 9 front-growth semantics. Iteration 8.1 remains
valid as compiler/source-layer infrastructure; non-growth evidence inside later
8.x sessions may still be reviewed independently when selector surfaces
separate it from legacy growth behavior.

#### Iteration 8.1: GRCL-9V3 Landscape Example Compiler

- Add a typed GRCL/Morse-facing landscape example layer above
  `grcl9v3.source.v1`.
- Compile critical regions, basins, saddles, ridges, valleys, boundary strata,
  refinement loci, tensor/Hessian profiles, choice/collapse regions, growth
  loci, and Appendix E cell-division regions into the existing GRCL-9V3
  mechanical source schema.
- Require an explicit GRCL-9V3 lowering guard.
- Preserve source-term to mechanical-construct provenance.
- Reject raw GRC9V3 graph literals, solved telemetry, event histories, and
  runtime outcomes.
- Status: complete. `pygrc.landscapes.extensions.grcl9v3.examples` now defines
  `grcl9v3.landscape_example.v1`, typed GRCL/Morse-facing terms, authored
  default examples for the 12 current GRCL-9V3 control lanes, deterministic
  forward compilation into `grcl9v3.source.v1`, and compiled source
  provenance. The compiler maps term profiles into mechanical source
  constructs directly; it does not reverse-lookup or replace pre-existing
  fixtures. This is source-layer work only; checked-in seed YAMLs and replay
  modes remain Iteration 8.2.

#### Iteration 8.2: Seed-Backed GRCL-9V3 Examples

- Add checked-in `LandscapeSeed` examples under `configs/landscapes/seed/`
  with `extensions.grcl9v3`.
- Extract GRCL-9V3 landscape examples from seed extensions.
- Compile extracted examples into `grcl9v3.source.v1`.
- Store original seeds, extracted examples, compiled source documents, lowered
  states, telemetry, checkpoints, selector reports, and visuals under replay
  sessions.
- Status: complete as a seed-backed pipeline slice. Five checked-in seeds are
  anchored in the S0014 GRC9V3 discovery handoff and extract through
  `extensions.grcl9v3` into `grcl9v3.landscape_example.v1`. `S0004` replays
  the extracted seed examples, `S0005` validates them with selectors, and
  `S0006` renders the selector-backed visuals. The first replay confirms the
  seed-backed source chain and records two strong selector-backed elementary
  motifs (growth and quiescent). Spark, expansion, and choice/collapse remain
  weak and move to Iteration 8.2.1.
- Post-review status: the seed-backed growth result is needs-rerun for
  paper-facing growth claims under Iteration 9 front-growth semantics. The
  seed pipeline and non-growth evidence remain valid. The affected growth lane
  used the over-aggressive legacy `growth_locus` model, where inactive
  interior ports could become growth parents without explicit spark/front
  capacity provenance.

#### Iteration 8.2.1: Elementary Seed Tuning Gate

- Tune the individual seed-backed examples until each intended elementary
  signature is either selector-backed or explicitly rejected.
- Repair hybrid spark, spark-to-expansion, choice/collapse, Appendix E,
  transport, and required negative/control seed-backed examples.
- Keep each tuning attempt replayable and selector-scored.
- Do not compose multiple elementary mechanisms here; composition belongs to
  Iteration 8.3.
- Status: complete for the first tuning pass. `S0007` replays seven
  seed-backed elementary examples, `S0008` validates them, and `S0009` renders
  visuals. Six records are strong selector-backed candidates: hybrid spark,
  spark-to-expansion, choice/collapse, growth, transport rerouting, and
  quiescent control. Appendix E now emits spark, expansion, and completed spark
  evidence, but remains a candidate rather than a composition-ready elementary
  motif because the representative Appendix E daughter/hierarchy selectors do
  not yet pass.
- Post-review status: the growth elementary candidate is needs-rerun for
  growth-specific catalog acceptance. Non-growth elementary candidates remain
  eligible according to their selector evidence. The old growth candidate used
  standalone growth-locus semantics instead of a corrected front-capacity
  declaration.

#### Iteration 8.2.2: Elementary Completeness Pass

- Complete the elementary seed-backed representation before hybrid composition.
- Upgrade Appendix E / hierarchy from candidate to selector-backed strong
  evidence.
- Add explicit negative/control seed-backed examples for spark, expansion,
  choice/collapse, and growth so absence-of-event evidence is replayable rather
  than inferred from missing positive examples.
- Keep Hessian backend comparison as a runtime diagnostic surface for GRC9V3,
  not a GRCL source seed, unless a future source-language construct is accepted.
- Status: complete. `S0010` replays eleven seed-backed elementary examples,
  `S0011` validates them, and `S0012` renders visuals. All eleven selector
  records are strong candidates with no missing surfaces, ambiguous records, or
  rejected records. Appendix E is now composition-ready through the tuned
  `target_effective_degree=51` seed.
- Post-review status: growth positive/negative controls are needs-rerun under
  Iteration 9. Other elementary motifs and controls remain catalog-eligible.
  These controls calibrated the over-aggressive legacy growth-locus model.

#### Iteration 8.2.3: Hessian Backend Diagnostic Probe

- Run a focused GRC9V3-specific Hessian comparison before hybrid composition.
- Keep this as a runtime diagnostic probe over existing seed-backed GRCL-9V3
  sources, not as a new GRCL source construct.
- Pair each selected source with two runtime backends:
  `row_basis_diagonal` and `weighted_least_squares`.
- Compare row-basis differential fields, tensor fields, and lifecycle event
  counts to identify where the two Hessian equations diverge most.
- Status: complete. `S0013` replays five paired configurations across ten
  lanes, `S0014` validates them, and `S0015` renders visuals. All ten selector
  records are strong candidates. The largest metric divergence is in
  `expansion_gate`, followed by `anisotropic_spark`; no paired configuration
  produced a lifecycle event-count delta.

#### Iteration 8.3: Hybrid Composition From Proven Seed Examples

- Compose only already-proven elementary seed-backed examples into hybrid
  examples.
- Require each hybrid example to state which 8.2 elementary seeds it composes.
- Cover at least spark + expansion, expansion + growth, and choice/collapse +
  basin structure from the strong elementary seeds. Appendix E / hierarchy may
  now be used as a composed seed ingredient because Iteration 8.2.2 upgraded it
  to strong selector-backed evidence.
- Use `row_basis_diagonal` as the default hybrid-composition backend unless a
  hybrid explicitly opts into a diagnostic backend comparison. Iteration 8.2.3
  found Hessian metric divergence but no lifecycle event-count divergence.
- Keep failed hybrid compositions replayable and documented, but do not use
  8.3 to repair missing elementary signatures.
- Status: complete. Four composed seeds were added under
  `configs/landscapes/seed/` and replayed in `S0016`, validated in `S0017`,
  and rendered in `S0018`. All four selector records are strong candidates
  with no missing surfaces or ambiguous records. The full composition emits
  spark candidate, mechanical expansion, completed spark, growth,
  choice-detection, and collapse events from one connected lowered graph. The
  composed Appendix E ingredients use generic hybrid expansion selectors in
  this pass because `representative_appendix_e_summary` is intentionally
  reserved for the standalone representative Appendix E fixture.
- Post-review status: hybrid records containing growth are needs-rerun for
  their growth claims. Their non-growth evidence can still be reviewed
  independently where selector surfaces separate it. Growth density in those
  hybrids came from the over-aggressive legacy growth-locus model, not
  corrected paper-facing front capacity.

#### Iteration 8.4: ComposingCells-Aligned Hybrid Seeds

- Add composed-cell seeds aligned with `2026-02-ComposingCells.md`.
- Use neutral GRCL primitives such as basins, ridges/membranes, valleys,
  plateaus, saddles, separatrices, boundary strata, and refinement loci.
- Map source-constructible Phase T-GRC9V3 concepts into seeds while keeping
  telemetry-only diagnostics as selectors/observations.
- Status: complete. Seven ComposingCells-aligned seeds were added under
  `configs/landscapes/seed/`, replayed in `S0019`, validated in `S0020`, and
  rendered in `S0021`. All seven selector records are strong candidates with
  no missing surfaces, ambiguous records, or rejected records. The batch covers
  boundary membrane spark, internal valley growth/transport, nested
  basin/hierarchy, saddle tensor choice, refinement/budget-partition intent,
  choice/collapse, and Appendix E cell division. Budget-partition remains a
  source intent observed through expansion/budget telemetry, not a source
  claim.
- Post-review status: ComposingCells records containing growth are needs-rerun
  for growth-specific claims. Non-growth cell motifs remain eligible. The
  old growth-bearing cell examples used over-aggressive growth loci rather
  than explicitly exposed spark/refinement front capacity.

#### Iteration 8.5: Full-Capacity Hybrid Cascade And Robustness

- Build a single connected source-authored seed that composes the currently
  supported GRCL-9V3 phenomenology surfaces.
- Run for a longer window and require selectors for the intended hybrid
  signatures.
- Add targeted perturbations and negative controls to record which signatures
  are robust, ambiguous, or falsified.
- Generate visualization and summary artifacts for the cascade family.
- Status: complete. `S0022` replayed the 20-step full-capacity cascade family,
  `S0023` validated selectors, and `S0024` rendered visuals. Two records are
  strong candidates: the baseline cascade and the balanced-choice perturbation.
  Two low-growth perturbations remain candidates because low `lambda_birth`
  reduces growth sharply but does not eliminate growth over 20 steps. This is
  recorded as an explicit robustness finding, not hidden as a failed run.
- Post-review status: the full-capacity growth and low-growth robustness
  claims are diagnostic until rerun under Iteration 9 front-growth semantics.
  Their large growth counts reflect the over-aggressive legacy growth-locus
  model and should not be interpreted as paper-facing front growth.

#### Iteration 8.5.1: Calibrated Growth Robustness

- Reuse the 8.5 finding that `lambda_birth=0.02` is a growth-reduction control,
  not a no-growth control over 20 steps.
- Add calibrated follow-up probes for ultra-low birth, exact zero birth,
  structural closed-growth, and zero-birth plus balanced-choice composition.
- Score ultra-low birth as bounded growth, not as a no-growth claim.
- Score exact zero-birth and structural closed-growth as no-growth controls.
- Preserve the same full-capacity cascade context so the result is comparable
  to `S0022`/`S0023`/`S0024`.
- Status: complete. `S0025` replayed the calibrated probes, `S0026` validated
  all four as strong candidates with no missing surfaces, and `S0027` rendered
  visuals. The calibrated result separates bounded residual growth
  (`lambda_birth=0.002`, two growth events) from true no-growth
  (`lambda_birth=0.0` or omitted growth locus). The combined zero-birth plus
  balanced-choice probe suppresses both growth and choice/collapse while
  preserving spark/expansion/Appendix E/tensor/transport evidence.
- Post-review status: calibrated growth robustness remains an old-model
  diagnostic. Iteration 9 decides which no-growth controls remain paper-facing
  after front-capacity correction. These controls calibrated the
  over-aggressive legacy growth-locus topology.

#### Iteration 8.6: Multi-Center Collapse And Basin-Assignment Learning

- Extend source lowering where safe so one GRCL-9V3 source document can lower
  multiple growth loci and multiple choice/collapse regions instead of silently
  using only the first construct of each type.
- Build source-authored multi-center seeds in which initially comparable
  growing centers compete, one center eventually wins, and other centers or
  saddle regions collapse into the winner.
- Treat learning narrowly and explicitly: Iteration 8.6 claims only
  runtime-observed basin-assignment learning from collapse
  (`choice_learning_state`, `learning_state_count`, and updated basin ids), not
  general adaptive or semantic learning.
- Run a bounded high-growth window rather than lowering the growth pressure.
  The accepted replay uses 20 steps so dense growth remains tractable while the
  seed still stresses growth-driven competition.
- Require selectors for growth-before-collapse, repeated choice detection,
  collapse, nonzero learning state, final collapse registry, and recorded
  collapsed sink.
- Render visuals that mark competing centers, collapse sources, and the winning
  sink/center while preserving the rule that telemetry remains primary.
- Diagnostic sessions: `S0028` replay and `S0029` selectors exposed that
  preseeded choice registries could collapse before observed growth.
- Accepted sessions: `S0030` replay, `S0031` selectors, and `S0032` visuals.
  `multi_center_collapse_learning` is a strong candidate with growth before
  later collapse and nonzero learning state; the delayed variant remains a
  candidate because collapse occurred before the first growth event in the
  20-step selector window.
- Status after growth-semantics review: these sessions remain replayable
  diagnostics for the old executable growth-locus interpretation. Growth claims
  from this iteration are not paper-facing until Iteration 9 reruns them under
  front-capacity semantics. The observed dense inner-node growth is expected
  from the over-aggressive legacy model and is not paper-facing.

#### Iteration 8.6.1: Collapse-Learning Timing And Sink Provenance Probe

- Probe the delayed multi-center source over a fixed lowered structure with
  controlled runtime `lambda_birth` values rather than adding new source
  ontology terms.
- Record timing thresholds for first growth, first collapse, first
  collapse-after-growth, and the point where the delayed lane becomes a strong
  growth-before-collapse candidate.
- Record whether the final collapsed sink is source-declared or runtime-grown.
  This distinguishes static winner selection from basin-assignment learning
  that moves into newly grown runtime structure.
- Keep the probe diagnostic: it is evidence about runtime behavior under one
  source-authored GRCL-9V3 seed, not a new claim about source-language solved
  outcomes.
- Sessions: `S0033` established that the delayed lane becomes strong at 50
  steps for `lambda_birth=0.2`; `S0035`/`S0036` run the systematic
  lambda-birth sweep and selector validation.
- Result after correcting event-order diagnostics to compare `(step_index,
  event_index)`: all four 50-step sweep lanes are strong candidates, with
  `lambda_birth=0.05` as the first strong growth-before-collapse value. Every
  final collapsed sink in the sweep is runtime-grown, not source-declared.
- Status after growth-semantics review: this lambda sweep is diagnostic only.
  It varies the old runtime growth-locus activation pressure and must not feed
  the reviewed source catalog without a front-capacity rerun.

#### Iteration 8.6.2: Recurrent Growth-Collapse Relay Probe

- Test whether the 8.6.1 runtime-grown collapsed sinks form a recurrent relay:
  growth child, later collapsed sink, and later growth parent.
- Keep the distinction between partial and full relay explicit:
  `growth child -> collapsed sink` and `collapsed sink -> growth parent` are
  useful partial relay evidence, but the full claim requires the same node to
  satisfy all three roles in order.
- Use a 100-step `lambda_birth=0.20` diagnostic replay first. This value keeps
  the replay dense enough to expose relay structure without using the densest
  `0.40` lane.
- Do not claim scale-free behavior in this iteration. Scale-free-like growth
  would require separate distributional checks over larger runs.
- Sessions: `S0037` is the exploratory 100-step replay; `S0038`/`S0039` are
  the accepted relay replay and selector validation.
- Result after correcting event-order diagnostics to compare `(step_index,
  event_index)`: the 100-step `lambda_birth=0.20` replay records full
  same-node relay evidence (`80` growth-child-later-collapsed-sink cases, `4`
  collapsed-sink-later-growth-parent cases, and `3` full growth-child ->
  collapsed-sink -> growth-parent relays).
- Status after growth-semantics review: the relay result is valuable runtime
  evidence under the old standalone growth-locus model, but it is not accepted
  GRCL-9V3 paper-facing evidence until reproduced from spark/front-created
  inactive capacity. The relay relied on over-aggressive inner growth.

#### Iteration 8.6.3: Relay-Port Sink-Then-Source Geometry Probe

- Use the 8.6.2 result to change the source geometry, not the runtime
  equations: the missing structure is a birth-port chamber whose grown child is
  first sink-facing and can later become source-facing.
- Add a relay-port growth profile over the delayed multi-center source:
  calibrated support edges keep the parent initially below the child in
  potential, while a weak outlet gives the birth-port neighborhood a delayed
  escape path.
- Run several deterministic relay-port variants that sweep support strength,
  `alpha_seed`, `w_bond`, and `lambda_birth`.
- Preserve the evidence distinction from 8.6.2: partial relay evidence remains
  useful, but the full claim requires the same node to appear in order as
  growth child, collapsed sink, and growth parent.
- Sessions: `S0040` is the accepted relay-port replay; `S0041` is selector
  validation.
- Result: relay-port geometry strengthens the growth-child -> collapsed-sink
  half of the relay (`85`, `150`, and `221` cases across the three variants),
  but it does not preserve the collapsed-sink -> later-growth-parent half. The
  simpler 8.6.2 delayed multi-center geometry remains the stronger full-relay
  example.
- Status after growth-semantics review: relay-port geometry remains a
  diagnostic design probe only. Any future accepted relay claim must use the
  corrected front-growth source boundary from Iteration 9. The probe still used
  legacy growth-locus activation.

### Iteration 9: Growth Semantics Correction And Rerun Gate

This iteration is split so the semantic/code correction is completed before
any corrected evidence is generated.

#### Iteration 9.1: Growth Source Semantics Correction

- Correct the GRCL-9V3 source boundary against
  `papers/2026-04-GRC-9.md`, Sections 8.3.3, 8.4, and 11:
  growth may use the paper's outward-flux birth pressure, but the selected
  port must be the deterministic lowest-index inactive port, and
  paper-facing source growth must attach to explicit front capacity rather
  than stand alone as an executable source mechanism.
- Reinterpret executable `growth_locus` fixtures as historical diagnostics
  unless they are paired with spark/refinement/front-created inactive
  capacity. Introduce the corrected source-facing concept as a front-growth
  annotation or capacity declaration, not a solved growth event.
- Update lowering and telemetry where needed so reruns can record the growth
  parent capacity source, such as `expansion_generated_front`,
  `preexisting_front`, or `legacy_source_growth_locus`.
- Add validation/tests proving standalone executable `growth_locus` cannot be
  accepted as paper-facing source evidence.
- Status: complete. `GRCL9V3GrowthLocus` now records explicit
  `growth_semantics`, `front_capacity_source`, and optional
  `front_source_construct_id`. Legacy standalone growth remains loadable as
  diagnostic evidence, but `validate_grcl9v3_paper_facing_growth_semantics`
  rejects it for paper-facing source claims. Lowering records
  front-growth-eligible ports, growth parent capacity sources, legacy
  growth-locus ids, and a growth semantics status. GRC9V3 growth can now be
  gated by `growth_parent_eligibility = "grcl9v3_front_capacity"`, preserving
  the paper's probabilistic birth activation while restricting parent/port
  eligibility to explicit front capacity. Replay telemetry mirrors the
  provenance, and selector validation has a `front_growth_provenance_present`
  field-backed selector.

#### Iteration 9.2: Corrected Growth Reruns

- Mark lightly affected Iteration 8.2-8.5 growth examples as needs-rerun for
  growth claims while preserving their non-growth evidence.
- Mark heavily affected Iteration 8.6-8.6.3 relay and learning claims as
  diagnostic/superseded under old standalone-growth semantics.
- Preserve old sessions as replayable history rather than rewriting their
  artifacts.
- Define corrected replay source-mode/session naming conventions for the
  9.2.x reruns.
- Update `outputs/grcl9v3/lowering/ExperimentalLog.md` with corrected rerun
  sessions.
- Require every corrected growth selector report to include
  `front_growth_provenance_present`.
- Require visual review for corrected selector-backed sessions, while keeping
  visuals supporting-only evidence.
- Record which old growth claims are superseded, replaced, or still diagnostic
  only.
- Status: complete as a rerun gate. `S0042` records the affected legacy
  sessions, catalog eligibility rules, selector/visual requirements, and
  9.2.x batch structure. It generates no runtime telemetry; executable
  corrected reruns begin in 9.2.1.

##### Iteration 9.2.1: Corrected Elementary Growth Seeds

- Rebuild the 8.2, 8.2.1, and 8.2.2 growth positive/negative controls with
  `front_capacity` semantics.
- Prove corrected `growth_events` together with
  `front_growth_provenance_present`.
- Establish corrected no-growth controls under front-capacity gating.
- Status: complete. Added corrected positive and no-growth front-capacity
  seeds. `S0043` replays both for three steps; the positive lane emits exactly
  one growth event and no choice/collapse events, while the no-growth control
  emits no lifecycle events. `S0044` validates both as strong candidates with
  `front_growth_provenance_present`, and `S0045` renders supporting-only
  visuals.

##### Iteration 9.2.2: Corrected Hybrid Growth Compositions

- Rebuild the 8.3 growth-bearing hybrid compositions.
- Keep spark, expansion, Appendix E, transport, and choice/collapse evidence
  separable from corrected growth evidence.
- Require corrected growth provenance in selector reports.
- Status: completed with corrected seed examples
  `corrected_hybrid_spark_expansion_growth_composition`,
  `corrected_hybrid_appendix_e_growth_composition`, and
  `corrected_hybrid_full_composition`. `S0046` replayed the lanes, `S0047`
  selector-scored all three as strong candidates with
  `front_growth_provenance_present`, and `S0048` rendered supporting-only
  visuals. The full composition preserves choice/collapse and transport
  evidence while growth remains bounded to explicit front capacity.

##### Iteration 9.2.3: Corrected ComposingCells Growth Seeds

- Rebuild the 8.4 ComposingCells-aligned growth seeds with front-capacity
  language.
- Preserve GRCL/Morse vocabulary: valleys, ridges, boundary strata,
  refinement loci, and front annotations.
- Validate that cell-internal growth is actually front/refinement growth.
- Status: completed for the only 8.4 ComposingCells seed with a direct growth
  claim, `corrected_cell_internal_valley_growth_transport`. `S0049` replayed
  one bounded front-capacity growth event, `S0050` selector-scored it as a
  strong candidate with transport evidence and no missing surfaces, and `S0051`
  rendered supporting-only visuals. Non-growth ComposingCells motifs remain
  separately reviewable.

##### Iteration 9.2.4: Corrected Full-Capacity Cascade And Robustness

- Rebuild 8.5 and 8.5.1 full-capacity cascade/robustness probes under
  front-capacity gating.
- Re-test bounded growth, zero-birth, closed-front, and balanced-choice
  controls.
- Expect lower growth density than the legacy over-aggressive model and record
  any remaining dense growth as front-capacity bounded.
- Status: completed with five corrected robustness lanes in `S0052`, selector
  validation in `S0053`, and visuals in `S0054`. Growth-positive lanes are
  bounded to one front-capacity event in the three-step window. Zero-birth and
  closed-front are explicitly separated: zero-birth keeps front-capacity
  provenance with `lambda_birth = 0`, while closed-front has no growth
  provenance. Balanced choice remains separable by preserving front growth
  while suppressing choice/collapse.

##### Iteration 9.2.5: Corrected Collapse/Learning/Relay Feasibility

- Revisit 8.6, 8.6.1, 8.6.2, and 8.6.3 under corrected front-growth
  semantics.
- Determine whether growth-before-collapse and relay patterns remain feasible.
- If feasible, produce corrected candidates; otherwise keep the old 8.6.*
  records as alternative-development diagnostics only.
- Status: completed with corrected feasibility replay in `S0055`, selector
  validation in `S0056`, and visuals in `S0057`. Corrected multi-center
  collapse/learning and delayed collapse/learning are strong candidates with
  explicit `front_capacity` provenance. The corrected relay attempt remains
  diagnostic-only: growth, collapse, and learning occur, but the same-node
  relay selectors do not pass.

##### Iteration 9.2.5.1: Corrected Propagated-Front Relay Reproduction

- Run the corrected relay attempt for a longer window to test whether the
  9.2.5 relay miss is only a timing issue.
- Add a bounded propagated-front relay probe that lets a grown child inherit a
  source-declared front-capacity port without reopening legacy standalone
  growth.
- Keep the 8.6.2 relay selectors unchanged: full reproduction still requires
  the same node to appear in order as growth child, collapsed sink, and later
  growth parent.
- Status: completed with long-window baseline `S0058`/`S0059`, propagated-front
  replay `S0066`, selector validation `S0067`, and visuals `S0070`. The
  long-window baseline still has no relay evidence. The propagated-front probe
  recovers the first half of the old relay (`growth_child_later_collapsed_sink`)
  but not `collapsed_sink_later_growth_parent` or
  `full_growth_collapse_relay`. Old 8.6.2 full relay remains legacy diagnostic
  evidence.

##### Iteration 9.2.6: Legacy Growth Seed Quarantine

- After corrected replacements are available, move over-aggressive
  standalone-growth GRCL-9V3 seeds to
  `configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/`.
- Keep corrected front-growth seeds and non-growth GRCL-9V3 seeds in the main
  seed directory.
- Exclude quarantined legacy growth seeds from normal default seed discovery.
- Add or preserve an explicit diagnostic loader/source mode for replaying
  quarantined legacy growth seeds when needed.
- Update seed README and replay documentation so old sessions remain
  reproducible without conflating legacy growth with paper-facing seeds.
- Status: completed. Default seed discovery now excludes the quarantined
  standalone-growth seeds. Corrected `grcl9v3-corrected-*` front-growth seeds
  and unaffected non-growth GRCL-9V3 seeds remain in the main seed directory.
  Historical diagnostics are preserved through the explicit
  `legacy_growth_landscape_seed_examples` replay source mode, while the older
  collapse-learning and relay probe source modes resolve their legacy base seed
  only through that diagnostic path. Replay smoke `S0071` records the legacy
  delayed multi-center seed under the quarantined source mode.

### Iteration 10: Reviewed Lowered-Source Catalog

- Publish reviewed JSON/Markdown catalog for GRCL-9V3 lowered motifs.
- Distinguish accepted, strong candidate, diagnostic, rejected, duplicate, and
  needs-rerun records.
- Accept unaffected non-growth motifs from earlier sessions.
- Accept growth/front motifs only from Iteration 9 corrected reruns.
- Preserve old standalone-growth 8.x records in a diagnostic appendix or
  `superseded_by_growth_semantics_correction` status.
- Status: completed with catalog session `S0072`. The reviewed catalog accepts
  28 records, keeps 2 corrected relay records as strong candidates, and marks
  26 old standalone-growth records as
  `superseded_by_growth_semantics_correction`. Accepted growth/front motifs
  come only from corrected Iteration 9 sessions and require
  `front_growth_provenance`.

### Iteration 11: Closeout And Handoff

- Record what GRCL-9V3 Revision 1 can express.
- Record gaps requiring future vocabulary or runtime telemetry.
- Link final artifacts back into `ImplementationPhases.md`.
- Status: completed. [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md) closes
  Revision 1, records the S0072 reviewed catalog, preserves the corrected
  front-growth boundary, and lists unsupported/deferred work. `ImplementationPhases.md`
  and `Phase-7-Closeout.md` now record the post-core Phase 7 completion state.
