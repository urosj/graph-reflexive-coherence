# GRCL-9 Handoff

This document closes GRCL-9 Revision 1 and records how to resume the next
source/lowering step without blurring source language, GRC9 runtime behavior,
telemetry observation, and visualization evidence.

Post-closeout note: growth-bearing GRCL-9 evidence has completed the dedicated
GRC9 / GRCL-9 growth semantics migration. Historical broad inactive-port growth
sessions remain replayable only to reproduce or debug the old behavior; they
are not evidence for any paper-facing claim. Accepted growth claims now come
from explicit front-capacity provenance. See
[GRC9-GRCL9-GrowthCorrection-Plan.md](./GRC9-GRCL9-GrowthCorrection-Plan.md)
and
[GRC9-GRCL9-GrowthCorrection-Checklist.md](./GRC9-GRCL9-GrowthCorrection-Checklist.md),
plus closeout handoff
[GRC9-GRCL9-GrowthCorrection-Handoff.md](./GRC9-GRCL9-GrowthCorrection-Handoff.md).

GRCL-9 Revision 1 is now a family-specific source and lowering layer for
authoring GRC9 mechanical graph preconditions. It is not an execution family,
not a solved-state cache, and not an observer or Lorentzian semantics layer.

## 1. Read First

Before resuming GRCL-9, read these documents in order:

1. [GRCL-9-Vocabulary.md](./GRCL-9-Vocabulary.md)
2. [GRCL-9-Landscape-ProjectorProposal.md](./GRCL-9-Landscape-ProjectorProposal.md)
3. [GRCL-9-LoweringManifest.md](./GRCL-9-LoweringManifest.md)
4. [GRCL-9-ImplementationPlan.md](./GRCL-9-ImplementationPlan.md)
5. [GRCL-9-ImplementationChecklist.md](./GRCL-9-ImplementationChecklist.md)
6. [Phase-T-GRC9-CollapseAdjacentObservabilityReview.md](./Phase-T-GRC9-CollapseAdjacentObservabilityReview.md)
7. [Phase-V-GRC9-CollapseAdjacentVisualizationReview.md](./Phase-V-GRC9-CollapseAdjacentVisualizationReview.md)

For upstream evidence, also keep these close:

- [GRC9-PhenomenologyDiscovery-Plan.md](./GRC9-PhenomenologyDiscovery-Plan.md)
- [GRC9-PhenomenologyDiscovery-Checklist.md](./GRC9-PhenomenologyDiscovery-Checklist.md)
- `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.md`
- `outputs/grcl9/lowering/ExperimentalLog.md`

## 2. Current Scope

GRCL-9 Revision 1 translates authored Morse-style landscape terms into
GRC9-native graph structure.

The source language may declare:

- critical regions
- stable basins
- unstable directions
- separatrices
- saddle bridges
- boundary strata
- gradient pressure
- refinement loci
- post-refinement two-sink regions

The source language may not declare:

- that a spark, expansion, growth, fission, or collapse happened
- solved flux, row tensor, column diagnostic, or basin outcomes
- GRCV3 hierarchy semantics
- Lorentzian causal semantics
- observer-local semantics

The deciding rule is unchanged: a source construct is valid only if it names a
pre-run structural condition that can be lowered into GRC9 graph mechanics.

## 3. Implemented Source Constructs

Revision 1 implements these source-schema constructs in
`src/pygrc/landscapes/extensions/grcl9/schema.py`:

| Source construct | Purpose |
|---|---|
| `spark_candidate_region` | Saturated candidate region for GRC9 spark gates |
| `column_proxy_profile` | Column diagnostic cancellation or imbalance intent |
| `instability_profile` | Row/instability support and cut intent |
| `expansion_refinement_region` | Effective-degree and module-size refinement intent |
| `growth_locus` | Boundary/inactive-port growth-pressure intent |
| `post_expansion_fission_geometry` | Two sink-capable regions plus bridge geometry |

The lowering manifest records five executable families:

- `grcl9_lowering_spark_column_proxy_v1`
- `grcl9_lowering_spark_instability_v1`
- `grcl9_lowering_expansion_refinement_v1`
- `grcl9_lowering_growth_pressure_v1`
- `grcl9_lowering_post_expansion_fission_v1`

These are implemented as source-to-GRC9 lowering, not as new GRC9 runtime
equations.

## 4. Implemented Example Families

The GRCL-9 landscape example layer lives under:

- `src/pygrc/landscapes/extensions/grcl9/examples.py`
- `configs/landscapes/seed/grcl9-*.seed.yaml`

Revision 1 includes:

- minimal pass/fail fixtures for spark column proxy, spark instability,
  expansion, growth, and fission min-mass controls
- ComposingCells-style source examples for membrane/ridge spark, internal
  valley growth, nested basin fission, saddle-branch instability, and
  refinement/budget partition
- collapse-adjacent structural probes
- runtime collapse-like discovery examples
- full-capacity cascade examples combining spark, expansion, growth, fission,
  and collapse-like source sink-role loss
- a 4-by-3 basin-asymmetry/growth phase diagram

The most important final example family is S0024:

- `balanced`, `mild`, `threshold`, and `deep` basin regimes
- `no_growth`, `low_growth`, and `nominal_growth` regimes
- 12 replayed lanes over 24 steps each
- 5 runtime-collapse-like diagnostics
- 7 ambiguous collapse-like diagnostics

S0024 is the strongest current GRCL-9 Revision 1 evidence surface.

## 5. Replayable Sessions

All sessions below are under `outputs/grcl9/lowering/sessions/`.

| Session | Role | Status |
|---|---|---|
| `S0006` | minimal mechanism fixtures | historical catalog source |
| `S0007` | first ComposingCells source examples | historical catalog source |
| `S0008` | first reviewed lowered motif catalog | stable historical catalog |
| `S0009` | early collapse-adjacent structural probes | superseded by later positive diagnostics |
| `S0010`-`S0019` | structural and collapse-producing seed development | intermediate evidence |
| `S0020` | first full-capacity cascade | positive combined-phenomenology evidence |
| `S0021` | first robustness family | intermediate robustness evidence |
| `S0022` | refined robustness family | selector/control repair evidence |
| `S0023` | basin-asymmetry ladder | transition evidence |
| `S0024` | basin-asymmetry/growth phase diagram | historical runtime-diagnostic evidence; broad-growth parts superseded for growth claims |
| `S0025` | accepted collapse-diagnostic catalog | historical Revision 1 closeout catalog |
| `S0031` | corrected front-capacity composite replay | current corrected GRCL-9 replay evidence |
| `S0032` | forced legacy broad-growth replay | diagnostic non-evidence only |
| `S0033` | corrected selector validation plus legacy supersession | current selector-backed corrected evidence |
| `S0036` | corrected GRCL-9 growth catalog | accepted corrected growth catalog |
| `S0037` | growth correction supersession summary | migration closeout |

Reproduce the strongest historical Revision 1 diagnostic evidence from the
repository root:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0024 --requested-steps 24 --source-mode landscape_seed_examples --fixture cell_full_capacity_phase_balanced_no_growth --fixture cell_full_capacity_phase_balanced_low_growth --fixture cell_full_capacity_phase_balanced_nominal_growth --fixture cell_full_capacity_phase_mild_no_growth --fixture cell_full_capacity_phase_mild_low_growth --fixture cell_full_capacity_phase_mild_nominal_growth --fixture cell_full_capacity_phase_threshold_no_growth --fixture cell_full_capacity_phase_threshold_low_growth --fixture cell_full_capacity_phase_threshold_nominal_growth --fixture cell_full_capacity_phase_deep_no_growth --fixture cell_full_capacity_phase_deep_low_growth --fixture cell_full_capacity_phase_deep_nominal_growth
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9_lowering --session-root outputs/grcl9/lowering/sessions/S0024
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_lowered_motif_catalog --session-id S0025 --source-session-id S0024
```

Reproduce the corrected front-capacity growth closeout:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_corrected_growth_catalog --session-id S0036
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grc9_grcl9_growth_supersession_summary --session-id S0037
```

Legacy broad-growth diagnostic replay requires an explicit force flag:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0032 --source-mode legacy_growth_landscape_seed_examples --force-legacy-growth --requested-steps 3
```

The expanded commands for S0020-S0025 are recorded in
`outputs/grcl9/lowering/ExperimentalLog.md`.

## 6. Reviewed Catalogs

S0008 remains the first reviewed lowered motif catalog:

- `outputs/grcl9/lowering/sessions/S0008/reviewed_grcl9_lowered_motif_catalog.json`

S0025 is the accepted collapse-diagnostic extension:

- `outputs/grcl9/lowering/sessions/S0025/reviewed_grcl9_lowered_motif_catalog.json`
- `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_report.json`
- `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_summary.md`

S0025 records:

- accepted motifs: 12
- rejected motifs: 0
- collapse diagnostics: 12
- runtime-collapse-like diagnostics: 5
- ambiguous collapse-like diagnostics: 7

Each S0025 accepted motif links back to:

- source seed
- compiled GRCL-9 source document
- lowered GRC9 state
- telemetry steps/events/run summary
- graph checkpoint index
- visualization artifacts
- S0024 phase-diagram context where available

S0036 records the accepted corrected growth catalog:

- accepted corrected GRCL-9 growth motifs: 21
- accepted corrected no-growth/control motifs: 7
- rejected motifs: 0
- accepted legacy broad-growth motifs: 0

S0037 records the migration summary and supersession boundary. Use S0036/S0037
for growth claims; use S0024/S0025 only for historical collapse-diagnostic
context and replay comparison.

## 7. Collapse Boundary

Collapse-like evidence is accepted only as diagnostic source-role loss.

The accepted diagnostic means:

- a source-declared two-sink region was lowered,
- telemetry/checkpoints show which source sink roles remain or are lost,
- the selector classifies the result as `runtime_collapse_like_observed`,
  `ambiguous`, or `structural_only`,
- and S0024 shows that basin asymmetry plus growth pressure selects a stable
  B-loss regime.

The accepted diagnostic does not mean:

- GRC9 has a new collapse event kind,
- GRC9 has a collapse runtime equation,
- GRCL-9 can prescribe collapse outcomes,
- or GRCV3 collapse semantics have been imported.

The useful current statement is:

> GRCL-9 Revision 1 can author source-side structures whose lowered GRC9 runs
> produce observable source sink-role loss diagnostics.

That statement should not be shortened to "GRCL-9 implements collapse."

## 8. Unsupported And Deferred

Unsupported in Revision 1:

- source-level event declarations
- solved diagnostics in source payloads
- direct GRCL-9 execution semantics
- observer-local views
- Lorentzian causal layer
- GRCV3 hierarchy semantics
- GRCL-9 lowering into any runtime family other than GRC9
- compact collapse telemetry fields beyond the diagnostic selector surface

Deferred or reserved:

- true GRC9 collapse event semantics
- observer-facing local unpredictability views
- boundary barrier/ghost modes beyond current GRC9 support
- adiabatic expansion runtime substep semantics beyond recorded schedule fields
- richer source-language families beyond the Revision 1 construct set
- multi-family GRCL vocabulary shared with GRCL-V3

## 9. What Should Not Be Reopened Casually

Do not reopen the following unless a concrete later artifact exposes a real
source-language gap:

- whether GRCL-9 should prescribe runtime events directly
- whether S0025 collapse diagnostics are GRC9 collapse events
- whether GRCV3 collapse/hierarchy vocabulary should be imported
- whether source-side terms should store solved telemetry results
- whether S0008 should be rewritten as the first catalog

S0008 is historical. S0025 is the later accepted collapse-diagnostic catalog.
Both should remain stable.

## 10. Recommended Next Lane

The next implementation lane should be a narrow post-Revision-1 extension, not
a rewrite of Revision 1.

Recommended next lane:

- build a GRCL-9 Revision 2 planning slice for one missing source-side
  distinction exposed by S0024/S0025,
- require a direct control and replayable session before adding any field,
- and keep all new claims diagnostic unless Phase T-GRC9 first accepts a new
  telemetry contract surface.

The strongest candidate question is:

- whether basin-asymmetry/growth phase boundaries need a first-class
  source-language parameter, or whether the existing `stable_basin`,
  `gradient_pressure`, and `post_refinement_two_sink_region` terms already
  author the distinction sufficiently.

That question should start as an authorability test, not as a schema change.

## 11. Final Handoff Rule

When resuming GRCL-9:

1. Start from S0024 and S0025, not from an isolated early probe.
2. Treat GRCL-9 as source/lowering only.
3. Keep GRC9 runtime equations and Phase T-GRC9 telemetry meanings stable.
4. Promote a new source term only after proving existing terms cannot author
   the needed condition.
5. Record every accepted example as a replayable session under
   `outputs/grcl9/lowering/sessions/`.

GRCL-9 Revision 1 is closed at the level of source schema, lowering, replay,
visualization, reviewed cataloging, and diagnostic collapse-adjacent evidence.
