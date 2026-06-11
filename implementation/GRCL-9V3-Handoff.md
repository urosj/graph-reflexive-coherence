# GRCL-9V3 Handoff

This document closes GRCL-9V3 Revision 1 and records how to resume future
source/lowering work without blurring GRCL/Morse source language, GRC9V3
runtime behavior, telemetry observation, visualization evidence, and reviewed
catalog status.

GRCL-9V3 Revision 1 is a family-specific source and lowering layer for
authoring GRC9V3 hybrid graph preconditions. It is not an execution family, not
a solved-state cache, and not an observer, Lorentzian, or source-level event
semantics layer.

## 1. Read First

Before resuming GRCL-9V3, read these documents in order:

1. [GRCL-9V3-Vocabulary.md](./GRCL-9V3-Vocabulary.md)
2. [GRCL-9V3-ImplementationPlan.md](./GRCL-9V3-ImplementationPlan.md)
3. [GRCL-9V3-ImplementationChecklist.md](./GRCL-9V3-ImplementationChecklist.md)
4. [GRC9V3-PhenomenologyDiscovery-Plan.md](./GRC9V3-PhenomenologyDiscovery-Plan.md)
5. [GRC9V3-PhenomenologyDiscovery-Checklist.md](./GRC9V3-PhenomenologyDiscovery-Checklist.md)
6. [Phase-T-GRC9V3-TelemetryContract.md](./Phase-T-GRC9V3-TelemetryContract.md)
7. [Phase-V-ImplementationPlan.md](./Phase-V-ImplementationPlan.md)
8. [Phase-V-ImplementationChecklist.md](./Phase-V-ImplementationChecklist.md)

For evidence, keep these close:

- `outputs/grc9v3/phenomenology_discovery/sessions/S0014/source_language_handoff.json`
- `outputs/grcl9v3/lowering/ExperimentalLog.md`
- `outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json`
- `outputs/grcl9v3/lowering/sessions/S0072/reports/reviewed_grcl9v3_lowered_motif_catalog_summary.md`

## 2. Current Scope

GRCL-9V3 Revision 1 translates authored GRCL/Morse-style landscape terms into
GRC9V3-native hybrid graph structure.

The source language may declare:

- critical regions and saturation preconditions,
- column-proxy and row-basis Hessian profiles,
- hybrid tensor profiles,
- expansion/refinement regions,
- explicit front-capacity growth annotations,
- transport rerouting regions,
- choice/collapse structural regions,
- Appendix E cell-division regions,
- and quiescent controls.

The source language may not declare:

- that a spark, expansion, growth, choice, collapse, learning update, or
  hierarchy update happened,
- solved flux, tensor, Hessian, basin, successor, or event outcomes,
- source-level daughter-sink confirmation,
- source-level relay success,
- GRCV3 semantics outside the GRC9V3 runtime contract,
- Lorentzian causal semantics,
- or observer-local semantics.

The deciding rule is unchanged: a source construct is valid only if it names a
pre-run structural condition that can be lowered into GRC9V3 graph mechanics
and then evaluated by runtime telemetry.

## 3. Implemented Source Constructs

Revision 1 implements the source-schema constructs in
`src/pygrc/landscapes/extensions/grcl9v3/schema.py`:

| Source construct | Purpose |
|---|---|
| `hybrid_spark_region` | Saturated candidate region for hybrid spark gates |
| `row_basis_hessian_profile` | Row-basis signed-Hessian precondition intent |
| `hybrid_tensor_profile` | Hybrid tensor anisotropy/mismatch intent |
| `column_proxy_fallback_profile` | Column diagnostic fallback intent |
| `expansion_refinement_region` | Effective-degree and expansion-module intent |
| `front_growth_region` | Corrected front-capacity growth precondition |
| `growth_locus` | Legacy diagnostic growth-locus construct, not paper-facing by itself |
| `choice_collapse_region` | Choice/collapse structural precondition |
| `transport_rerouting_region` | Transport and rerouting structural precondition |
| `appendix_e_division_region` | Appendix E cell-division structural precondition |
| `quiescent_hybrid_region` | No-event control structure |

The growth boundary is important. The paper-facing Revision 1 source construct
is front-capacity growth: birth pressure may be probabilistic, but parent/port
eligibility must come from explicit front capacity. Older standalone
`growth_locus` seeds remain loadable only to reproduce or debug the old
behavior; they are not evidence for paper-facing claims.

## 4. Implemented Example Families

The GRCL-9V3 example layer lives under:

- `src/pygrc/landscapes/extensions/grcl9v3/examples.py`
- `configs/landscapes/seed/grcl9v3-*.seed.yaml`
- `configs/landscapes/seed/grcl9v3-corrected-*.seed.yaml`

Revision 1 includes:

- minimal source fixtures for spark, expansion, Appendix E, choice/collapse,
  transport, quiescence, and corrected front growth,
- GRCL/Morse-facing landscape examples compiled into mechanical source,
- seed-backed examples derived from GRC9V3 phenomenology discovery,
- hybrid compositions combining spark, expansion, front growth, transport, and
  choice/collapse,
- ComposingCells-aligned seeds for membrane, valley, nested basin, saddle, and
  refinement/budget structures,
- corrected full-capacity cascade and robustness probes,
- corrected multi-center collapse/learning probes,
- and propagated-front relay diagnostics.

Legacy over-aggressive standalone-growth seeds moved to:

```text
configs/landscapes/seed/legacy/grcl9v3-overaggressive-growth/
```

They remain replayable through `legacy_growth_landscape_seed_examples`, but
they are not paper-facing evidence.

## 5. Replayable Sessions

All sessions below are under `outputs/grcl9v3/lowering/sessions/`.

| Session | Role | Status |
|---|---|---|
| `S0010`-`S0012` | elementary seed-backed source evidence | partially superseded for growth |
| `S0013`-`S0015` | Hessian backend probe | diagnostic |
| `S0016`-`S0018` | first hybrid compositions | growth-bearing records superseded |
| `S0019`-`S0021` | ComposingCells-aligned examples | non-growth motifs eligible, growth rerun required |
| `S0022`-`S0027` | old full-capacity cascade/robustness | superseded for growth claims |
| `S0030`-`S0041` | old multi-center and relay probes | diagnostic, superseded for growth |
| `S0042` | corrected growth rerun gate | planning/evidence gate |
| `S0043`-`S0045` | corrected elementary front growth | accepted evidence source |
| `S0046`-`S0048` | corrected hybrid growth compositions | accepted evidence source |
| `S0049`-`S0051` | corrected ComposingCells growth | accepted evidence source |
| `S0052`-`S0054` | corrected full-capacity cascade/robustness | accepted evidence source |
| `S0055`-`S0057` | corrected collapse/learning/relay feasibility | accepted plus strong-candidate evidence |
| `S0058`-`S0070` | corrected propagated-front relay attempts | strong-candidate/diagnostic evidence |
| `S0071` | legacy growth diagnostic replay smoke | diagnostic path verification |
| `S0072` | reviewed lowered-source catalog | Revision 1 closeout catalog |

Rebuild the closeout catalog from repository root:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_lowered_motif_catalog --session-id S0072
```

The expanded commands for replay, selector validation, visualization, and
legacy diagnostic replay are recorded in
`outputs/grcl9v3/lowering/ExperimentalLog.md`.

## 6. Reviewed Catalog

S0072 is the Revision 1 reviewed lowered-source catalog:

- `outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json`
- `outputs/grcl9v3/lowering/sessions/S0072/reports/reviewed_grcl9v3_lowered_motif_catalog_report.json`
- `outputs/grcl9v3/lowering/sessions/S0072/reports/reviewed_grcl9v3_lowered_motif_catalog_summary.md`

S0072 records:

- reviewed records: 56
- accepted motifs: 28
- strong candidates: 2
- superseded legacy standalone-growth records: 26
- rejected records: 0
- accepted corrected growth/front motifs: 12

Every accepted motif links back to:

- source fixture or seed reference,
- compiled GRCL-9V3 source document,
- lowered GRC9V3 state,
- telemetry steps/events/run summary,
- graph checkpoint index,
- selector validation,
- and visualization artifacts when available.

Visuals remain supporting evidence only. They do not promote records without
selector-backed telemetry.

## 7. Growth Boundary

The largest Revision 1 correction was growth semantics.

The GRC-9 paper allows the birth probability:

```text
p_birth(i) = 1 - exp(-lambda * F_i^out)
```

but GRCL-9V3 source growth is paper-facing only when it targets front capacity:
the source must lower explicit front-growth-eligible ports, and runtime
telemetry must record `front_growth_provenance`.

Accepted growth/front records therefore require:

- corrected front-capacity source structure,
- selector evidence for growth or no-growth behavior,
- `front_growth_provenance`,
- no legacy standalone growth-locus dependency.

Old 8.x standalone-growth records are preserved as
`superseded_by_growth_semantics_correction`. They remain valuable because they
exposed development patterns, but they are not accepted paper-facing GRCL-9V3
growth evidence.

## 8. Proven Statements

The useful Revision 1 statements are:

- GRCL-9V3 can author source-side structures that lower into connected GRC9V3
  graphs.
- GRCL-9V3 can express hybrid spark, expansion, Appendix E, choice/collapse,
  transport, quiescent, and corrected front-growth preconditions.
- Corrected front-growth examples produce bounded runtime growth from explicit
  front capacity.
- Multi-center corrected examples can produce growth-before-collapse and
  basin-assignment learning telemetry.
- Relay-like propagated-front evidence is currently a strong candidate, not an
  accepted full relay theorem.
- Reviewed catalog acceptance is selector-backed telemetry evidence, not source
  truth.

These statements should not be shortened to "GRCL-9V3 implements events" or
"GRCL-9V3 solves hybrid phenomenology."

## 9. Unsupported And Deferred

Unsupported in Revision 1:

- source-level event declarations,
- solved diagnostics in source payloads,
- direct GRCL-9V3 execution semantics,
- accepted full same-node growth-collapse-growth relay,
- observer-local views,
- Lorentzian causal layer,
- compact source-level proof of Appendix E daughter sinks,
- and source-level learning semantics beyond observed runtime telemetry.

Deferred or future work:

- richer shared GRCL vocabulary across GRCL-V3, GRCL-9, and GRCL-9V3,
- source ergonomics for authored front-capacity structures,
- stronger propagated-front relay geometry,
- larger distributional checks for scale-free-like growth,
- boundary barrier/ghost mode integration when the runtime supports it,
- and additional telemetry compression for expected-vs-observed region linkage.

## 10. Verification

Focused catalog test:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_lowered_motif_catalog
```

Full GRCL-9V3 slice:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9v3_lowered_motif_catalog tests.landscapes.test_import_smoke tests.landscapes.test_grcl9v3_manifest tests.landscapes.test_grcl9v3_examples tests.landscapes.test_grcl9v3_schema tests.landscapes.test_grcl9v3_fixtures tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.visualization.test_grcl9v3_lowering
```

Current result:

```text
91 tests OK
```

## 11. Closeout Result

GRCL-9V3 Revision 1 is closed as a source/lowering and evidence layer:

- source vocabulary is defined,
- source schema and fixtures are implemented,
- seed examples compile into source documents,
- source documents lower into connected GRC9V3 states,
- replay, selector validation, and visualization are available,
- corrected growth semantics are enforced,
- legacy standalone growth is quarantined,
- and S0072 publishes the reviewed lowered-source catalog.
