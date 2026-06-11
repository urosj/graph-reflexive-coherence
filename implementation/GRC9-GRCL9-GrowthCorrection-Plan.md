# GRC9 / GRCL-9 Growth Correction Plan

## Purpose

This document defines the correction track for GRC9 and GRCL-9 growth
semantics after identifying that the implemented growth rule is too broad for
paper-facing Section 8.4 claims.

The mathematical birth probability rule remains valid:

```text
p_birth(i) = 1 - exp(-lambda * F_i^out)
```

The correction is topological. Paper-facing growth must fill explicit
front/boundary capacity exposed by spark/refinement structure. It must not be
interpreted as a standalone rule that allows any live node with an inactive port
and outward flux to become a birth parent.

## Problem Statement

The current GRC9 runtime implements the birth probability and lowest-index
inactive-port attachment rule, but parent eligibility is broad:

- every live node is scanned when `lambda_birth > 0`,
- any node with an inactive port and positive outward flux can become a growth
  parent,
- the selected port is the lowest inactive port on that parent.

The lowest-port part is aligned with the paper. The broad parent eligibility is
not sufficient for paper-facing front-growth claims.

GRCL-9 currently inherits this behavior because `growth_locus` is an executable
standalone source construct. It declares pressure and `lambda_birth`, and the
replay layer enables GRC9 growth globally. That makes growth-heavy GRCL-9
evidence historically useful but not acceptable as final paper-facing
front-growth evidence until rerun under corrected eligibility.

## Interpretation Policy

This is a semantic migration, not a full reset.

Historical artifacts remain replayable only for reproducing and debugging the
old behavior. They should not be deleted or rewritten.

Growth-bearing GRC9 / GRCL-9 records created under broad eligibility should be
classified as:

```text
legacy_broad_growth_non_evidence
```

or, for reviewed catalog entries:

```text
superseded_by_growth_semantics_correction
```

Broad-growth legacy results must not be used for any paper-facing evidence
claim after this correction, including non-growth claims inside mixed
broad-growth catalogs.

## Affected Surfaces

Affected:

- GRC9 core growth parent selection,
- Phase T-GRC9 growth telemetry,
- GRC9 phenomenology discovery growth/cascade/complex lanes,
- GRCL-9 `growth_locus` source semantics,
- GRCL-9 lowering/replay growth configuration,
- GRCL-9 growth-bearing visual and reviewed catalog claims.

Not automatically affected:

- spark detection,
- mechanical expansion,
- column diagnostic evidence,
- row/port/coarse/budget telemetry not dependent on growth topology,
- fission evidence when the lane does not rely on broad growth,
- visualizations as historical displays,
- replayability of previous sessions.

## Corrected Runtime Semantics

GRC9 core should support two explicit growth parent eligibility modes:

```text
legacy_any_inactive_port
grc9_front_capacity
```

`legacy_any_inactive_port` preserves historical replay.

`grc9_front_capacity` is required for paper-facing growth claims. In this mode:

- birth probability still uses outward flux pressure,
- parent/port candidates are filtered through explicit front-capacity metadata,
- the chosen port remains the lowest eligible inactive port,
- emitted growth events record their capacity source.

Proposed cached quantities:

```text
grc9_front_growth_eligible_ports
grc9_growth_parent_capacity_sources
birth_parent_eligibility_mode
```

Proposed growth event payload fields:

```text
growth_parent_eligibility_mode
growth_parent_capacity_source
parent_port_id
birth_probability
outward_flux
```

## Corrected GRCL-9 Source Semantics

GRCL-9 should preserve the name `growth_locus` only if it is explicitly
qualified by growth semantics:

```text
legacy_growth_locus
front_capacity
```

Paper-facing GRCL-9 source documents must use `front_capacity`.

Legacy standalone growth remains loadable only for replay diagnostics and
comparison against corrected behavior.

Corrected source fields should mirror the GRCL-9V3 migration:

```text
growth_semantics
front_capacity_source
front_source_construct_id
inactive_parent_port
```

Allowed paper-facing capacity sources should include:

```text
spark_refinement_front
expansion_generated_front
preexisting_front_capacity
propagated_front_growth
```

`legacy_source_growth_locus` may remain as a diagnostic-only value, but it must
not pass paper-facing validation.

## Evidence Migration

The migration should preserve earlier sessions and add corrected reruns.

Expected classification:

- old broad-growth runs: retained as replay-only non-evidence artifacts,
- old non-growth runs: retained when independent of growth,
- corrected GRC9 growth runs: new accepted runtime evidence candidates,
- corrected GRCL-9 growth runs: new accepted source/lowering candidates,
- catalogs: refreshed with explicit supersession links.

## Iteration Plan

### Iteration 0: Correction Planning

- Create this plan and the corresponding checklist.
- Record the non-reset policy.
- Record the affected and unaffected evidence boundaries.

### Iteration 1: GRC9 Core Growth Eligibility

- Add explicit growth parent eligibility mode to GRC9 params.
- Preserve `legacy_any_inactive_port` for replay.
- Add `grc9_front_capacity` filtering to `_apply_growth`.
- Add front-capacity cached quantities.
- Record capacity source on growth events.
- Test legacy replay behavior and corrected gating behavior separately.
- Status: complete. GRC9 core now supports explicit legacy and corrected
  front-capacity growth parent eligibility modes. Legacy remains the default;
  corrected mode requires `grc9_front_growth_eligible_ports` and records
  capacity-source evidence on growth events.

### Iteration 2: Phase T-GRC9 Telemetry Update

- Extend GRC9 telemetry contract and builders with growth eligibility and
  capacity-source fields.
- Add selectors for corrected front-growth provenance.
- Keep legacy broad-growth fields visible for diagnostics.
- Update representative telemetry docs.
- Status: complete. GRC9 telemetry now reports growth parent eligibility in the
  backend config, event-level front-capacity provenance and legacy-broad-growth
  flags, and run-summary counts for corrected versus legacy growth.

### Iteration 3: GRC9 Corrected Growth Discovery

This iteration is split because corrected discovery needs elementary controls
before larger compositions are meaningful.

#### Iteration 3.1: Elementary Corrected GRC9 Growth Seeds

- Add corrected GRC9 seed families with explicit front-capacity metadata.
- Add positive, no-front-capacity, zero-birth, and closed-front controls.
- Run the elementary corrected growth session.
- Status: complete. `S0027` ran
  `grc9_growth_correction_elementary_v1` with 4 lanes, 12 total steps, and
  one growth event. Only the positive lane emitted growth, and that event
  carried `grc9_front_capacity` provenance with capacity source
  `spark_refinement_boundary_front`. The no-front, zero-birth, and
  closed-front controls emitted no growth.

#### Iteration 3.2: Corrected GRC9 Combo Reruns

- Rerun spark-growth compositions.
- Rerun growth-fission compositions only where still meaningful.
- Record whether corrected growth changes downstream fission evidence.
- Status: complete. `S0028` ran
  `grc9_growth_correction_combo_v1` with 3 lanes, 16 total steps, and 7
  events. Every lane emitted exactly one front-capacity growth event and zero
  legacy broad-growth events. Spark-growth evidence remained present.
  Growth-fission still confirmed fission, while spark-growth-fission preserved
  the spark/expansion/growth chain but no longer confirmed fission under the
  corrected growth interaction.

#### Iteration 3.2.1: Corrected Spark-Growth-Fission Stabilization

- Strengthen the fission submodule structurally, without weakening the
  Appendix E persistence evaluator.
- Rerun corrected combo evidence as a distinct replayable session.
- Status: complete. `S0029` reran the corrected combo fixtures after boosting
  the spark-growth-fission daughter attractors. The full
  spark/expansion/growth/fission evidence is restored:
  `identity_fission_confirmed_count = 1`,
  `identity_fission_max_persistence_steps = 6`,
  `front_capacity_growth_count = 1`, and `legacy_broad_growth_count = 0`.

#### Iteration 3.3: Corrected GRC9 Full-Complex Reruns

- Rerun full-complex and robustness lanes that previously depended on growth.
- Check for runaway broad-growth removal.
- Record new misses and ambiguous outcomes.
- Status: generated-run complete. `S0030` reran the full-complex all-event
  graph and four robustness perturbations under
  `growth_parent_eligibility = grc9_front_capacity`. Each lane preserved
  `2` spark events, `2` expansion events, `1` bounded front-capacity growth
  event, and confirmed fission summary evidence while reporting
  `legacy_broad_growth_count = 0`. Selector replay/classification remains in
  the next iteration.

#### Iteration 3.4: GRC9 Discovery Legacy Classification

- Mark old broad-growth discovery sessions as replay-only non-evidence
  artifacts.
- Preserve old replay commands.
- Publish corrected motif evidence and supersession notes.
- Status: complete. The authoritative supersession index is
  `outputs/grc9/phenomenology_discovery/indexes/growth_semantics_correction.md`.
  Direct broad-growth runs and downstream mixed selector/review/handoff outputs
  are classified as `legacy_broad_growth_non_evidence`; corrected growth
  evidence begins at `S0027`, with `S0029` and `S0030` as the stabilized
  corrected combo and full-complex replacements.

### Iteration 4: GRCL-9 Source And Lowering Migration

This iteration is split across schema, lowering, and replay integration.

#### Iteration 4.1: GRCL-9 Source Growth Semantics

- Add source-level growth semantics to `GRCL9GrowthLocus`.
- Add paper-facing validation that rejects executable legacy growth claims.
- Keep legacy growth loadable for diagnostic replay.
- Status: complete. Pure GRCL-9 now matches the corrected GRCL-9V3 source
  discipline: `legacy_growth_locus` remains loadable for replay-only
  non-evidence documents, `front_capacity` records source/capacity provenance,
  and `validate_grcl9_paper_facing_growth_semantics(...)` rejects executable
  standalone legacy growth for paper-facing claims.

#### Iteration 4.2: GRCL-9 Lowering Front-Capacity Caches

- Lower `front_capacity` source declarations into GRC9 front-capacity caches.
- Record corrected front-capacity source provenance.
- Record legacy growth source ids in lowered state metadata.
- Status: complete. Lowered corrected GRCL-9 growth now emits
  `grc9_front_growth_eligible_ports` and
  `grc9_growth_parent_capacity_sources`, with mirrored `grcl9_*` metadata and
  `grcl9_legacy_growth_locus_ids` for old standalone growth. Legacy lowering
  remains graph-phenomenology equivalent; corrected event-level phenomenology
  changes only after 4.3 replay selects the corrected GRC9 mode.

#### Iteration 4.3: GRCL-9 Legacy Seed Quarantine

- Move over-aggressive standalone-growth GRCL-9 seeds to
  `configs/landscapes/seed/legacy/grcl9-overaggressive-growth/`.
- Keep non-growth and growth-independent GRCL-9 seeds in the main seed
  directory.
- Exclude quarantined legacy growth seeds from normal default seed discovery.
- Add an explicit diagnostic loader/source mode for quarantined legacy growth
  seeds.
- Update seed README and replay documentation so historical seed replay remains
  reproducible without conflating legacy growth with paper-facing seeds.
- Status: complete. Thirty pure GRCL-9 legacy standalone-growth seed files are
  quarantined under `legacy/grcl9-overaggressive-growth/`. Default GRCL-9
  seed discovery no longer loads them; diagnostic replay can still load them
  through `legacy_growth_landscape_seed_examples`.

#### Iteration 4.4: GRCL-9 Replay Integration

- Configure replay to use `growth_parent_eligibility = grc9_front_capacity`
  for corrected source documents.
- Preserve legacy broad-growth replay as an explicit diagnostic mode.
- Status: complete. GRCL-9 replay now derives the GRC9
  `growth_parent_eligibility` mode from source growth semantics. Corrected
  `front_capacity` documents run in `grc9_front_capacity` mode and persist the
  replay decision in lane metadata and telemetry family extensions. Legacy
  standalone `growth_locus` documents remain replayable in
  `legacy_any_inactive_port` mode through explicit fixture or quarantined-seed
  diagnostic paths, and are marked `legacy_broad_growth_non_evidence`. Legacy
  replay is therefore phenomenologically equivalent to the old broad-growth
  path only for diagnostics; corrected paper-facing replay is bounded to
  declared front-capacity ports.

### Iteration 5: GRCL-9 Corrected Replay, Selectors, And Visualization

This iteration is split because corrected examples, sessions, selectors, and
visuals are separate evidence surfaces.

#### Iteration 5.1: Elementary Corrected GRCL-9 Examples

- Add elementary corrected front-growth source examples.
- Add corrected no-growth controls.
- Replay and record elementary evidence.
- Status: complete. `S0027` ran the full elementary corrected source suite:
  positive high-birth, zero-birth no-growth, no-front-capacity, and
  closed-front controls. Only the positive lane emitted growth. All four lanes
  compile from normal seed files through the GRCL-9 landscape example compiler
  and run under corrected `grc9_front_capacity` provenance. `S0026` remains a
  preliminary incomplete two-lane attempt, not the completed 5.1 evidence.

#### Iteration 5.2: Corrected GRCL-9 Composite Reruns

- Rebuild affected cascade examples.
- Rebuild affected phase-diagram examples.
- Rebuild collapse-adjacent examples only when growth is part of the claim.
- Status: complete. `S0029` ran 28 corrected composite seed replacements
  covering the quarantined non-elementary GRCL-9 growth suite. All corrected
  growth constructs compile to `front_capacity` semantics. The run produced
  26 spark, 26 expansion, and 16 bounded front-capacity growth events. Older
  selector misses are recorded as diagnostic evidence that corrected growth no
  longer reproduces all broad-growth side effects; selector acceptance moves to
  Iteration 5.3. `S0028` remains only as the preliminary composite replay that
  exposed and fixed no-growth metadata still reporting the legacy eligibility
  mode.

#### Iteration 5.2.1: Corrected GRCL-9 Phenomenological Parity Tuning

- Classify `S0029` misses as real parity gaps, stale selector expectations,
  or intentionally lost broad-growth side effects.
- Tune only paper-valid/source-valid knobs.
- Rerun corrected parity session before selector acceptance.
- Status: complete. `S0030` improved corrected composite parity from 10
  passed / 18 missed to 19 passed / 9 missed while keeping all lanes in
  `grc9_front_capacity` mode. Recovered families include low-growth phase
  lanes, the full-capacity phenomenology cascade, low/high growth cascades,
  and threshold/deep collapse lanes. Remaining misses are selector/review
  diagnostics rather than broad-growth restoration targets.

#### Iteration 5.2.2: Corrected GRCL-9 Remaining Parity Misses

- Retune the 9 remaining missed lanes from `S0030`.
- Convert structural-control claims into explicit structural outcomes where
  the runtime no longer preserves old source sink roles.
- Retune isolated-threshold and no-growth/no-refinement claims without
  reintroducing broad-growth parent eligibility.
- Status: complete. `S0031` reran the 28 corrected composite seeds after
  tightening the remaining seed claims and one bridge geometry. Selector
  parity improved from `S0030`'s 19 passed / 9 missed to 28 passed / 0
  missed. Runtime evidence remained paper-aligned: all lanes used
  `grc9_front_capacity`, and the session emitted 32 spark, 32 expansion, and
  21 bounded front-capacity growth events. No no-growth control emitted
  growth.

#### Iteration 5.3: Corrected GRCL-9 Selector Validation

- Run selector validation over corrected sessions.
- Require front-growth provenance selectors for growth acceptance.
- Ensure selector reports do not accept legacy broad-growth records.
- Status: complete. `S0032` reran the quarantined legacy seed set under the
  explicit legacy replay path, and `S0033` validated corrected `S0031` plus
  legacy `S0032`. The validator accepted 28 corrected front-capacity records,
  superseded 30 legacy broad-growth records as non-evidence, and reported 0
  missing telemetry surfaces.

#### Iteration 5.4: Corrected GRCL-9 Visualization

- Render corrected visualizations with source/front-capacity overlays.
- Preserve old visuals as historical diagnostics.
- Mark visual metadata as corrected or legacy.
- Status: complete. `S0031` corrected visuals now mark all 28 lanes as
  `corrected_front_capacity_evidence` with `grc9_front_capacity`; `S0032`
  legacy visuals mark all 30 lanes as `legacy_broad_growth_non_evidence` with
  `legacy_any_inactive_port`. Boundary panels and overlay summaries expose
  front-capacity and legacy growth counts.

### Iteration 6: Reviewed Catalog Migration

This iteration is split to keep classification separate from catalog writing.

#### Iteration 6.1: Affected Record Classification

- Identify all reviewed records with growth-dependent claims.
- Separate retained non-growth records from superseded broad-growth records.
- Status: complete. `S0034` classified 47 historical reviewed records across
  the existing GRC9 and GRCL-9 reviewed catalogs. It retained 28 independent
  non-growth records and marked 19 growth-dependent records as
  `superseded_by_growth_semantics_correction`, with old motif ids preserved in
  `supersession_link`.

#### Iteration 6.2: GRC9 Corrected Growth Catalog

- Refresh the GRC9 corrected growth catalog.
- Link corrected motifs to old superseded motif ids where applicable.
- Status: complete. `S0035` published the corrected GRC9 growth catalog
  from `S0027`, `S0029`, and `S0030`, accepting 9 front-capacity growth
  motifs and 3 corrected controls with 0 accepted legacy broad-growth records.

#### Iteration 6.3: GRCL-9 Corrected Growth Catalog

- Refresh the GRCL-9 corrected growth catalog.
- Accept source/lowering growth motifs only with front-capacity provenance.
- Status: complete. `S0036` published the corrected GRCL-9 growth catalog
  from selector-backed `S0033` records, accepting 21 front-capacity
  source/lowering growth motifs and 7 corrected controls with 0 accepted
  legacy broad-growth records.

#### Iteration 6.4: Supersession Summary

- Publish summary counts and supersession notes.
- Record accepted, superseded, rejected, and unresolved growth records.
- Status: complete. `S0037` published the migration summary tying together
  `S0034`, `S0035`, and `S0036`: 28 retained non-growth records, 19
  superseded broad-growth records, 30 accepted corrected growth records,
  10 corrected controls, 0 rejected corrected records, and 2 unresolved
  superseded early GRCL-9 growth-pressure records.

### Iteration 7: Closeout And Guardrails

#### Iteration 7.1: Legacy Growth Execution Guards

- Add `--force-legacy-growth` to replay-only diagnostic paths that can load
  quarantined legacy broad-growth sources.
- Refuse legacy broad-growth source sessions by default in downstream selector,
  visualization, and reviewed-catalog builders.
- Preserve forced legacy outputs only as replayable diagnostics, with manifest
  fields that state they are non-evidence.
- Keep corrected catalog publishers strict: they must not accept legacy
  `legacy_any_inactive_port` growth as corrected growth evidence.
- Status: complete. Legacy replay, selector validation, visualization, and the
  old reviewed GRCL-9 catalog builder now reject legacy broad-growth sessions
  unless `--force-legacy-growth` is supplied; forced outputs remain diagnostic
  non-evidence.

#### Iteration 7.2: Documentation Closeout

- Add a correction handoff.
- Update Phase 6, Phase T-GRC9, Phase V-GRC9, GRC9 discovery, and GRCL-9
  closeout notes.
- Record replay commands and session references for corrected evidence.
- Status: complete. The closeout handoff and dependent documents now point to
  `S0034`-`S0037` as the completed migration and distinguish corrected
  front-capacity evidence from forced legacy broad-growth diagnostics.

## Non-Goals

This correction does not:

- change the Section 8.4 birth probability formula,
- change the lowest-index port attachment rule,
- remove legacy replay mode,
- claim observer-local, Lorentzian, GRCV3 hierarchy, or native collapse
  semantics for GRC9,
- retroactively rewrite historical outputs.

## Completion Definition

The correction is complete when:

- GRC9 core has a tested paper-facing front-capacity growth mode,
- Phase T-GRC9 exposes the growth eligibility and capacity-source evidence,
- GRC9 discovery has corrected growth-bearing reruns,
- GRCL-9 source documents can declare paper-facing front growth without
  standalone growth smuggling,
- old broad-growth GRCL-9 seeds are quarantined or clearly labeled,
- reviewed catalogs distinguish accepted corrected growth from superseded
  broad-growth diagnostics,
- and closeout docs state the migration boundary clearly.
