# GRCL-9 Collapse-Adjacent Next Batch

## Purpose

This document records the planned collapse-adjacent work batch after the first
reviewed GRCL-9 lowered motif catalog.

`S0008` proves that GRCL-9 can author and lower source structures for spark,
expansion, growth, and identity-fission diagnostics. Collapse-adjacent
ComposingCells behavior was intentionally not part of that first catalog batch
and is scheduled as the next focused extension.

The purpose of this review is to keep three meanings separate:

- **GRCV3 choice collapse**: an explicit runtime event where a choice state
  resolves to one dominant sink.
- **GRC9 structural collapse candidate**: source-constructible GRC9 geometry
  that may express support loss, basin merge, membrane rupture, or failed
  persistence, but has no current `collapse` event semantics.
- **ComposingCells dysfunction collapse**: source-level cell-language notions
  such as membrane rupture or identity basin loss.

Current GRCL-9 must not relabel any of these as the others.

## Current Evidence And Next Batch

Implemented and replayable:

- `S0006`: mechanism-probe GRCL-9 seeds for spark, expansion, growth, and
  fission pass/fail controls.
- `S0007`: ComposingCells-aligned seeds for boundary ridge/membrane,
  internal valley/transport, nested basin/plateau, saddle branch, and
  refinement/budget partition.
- `S0008`: reviewed lowered motif catalog over `S0006` and `S0007`.

Planned next batch:

- add GRCL-9 seeds that target collapse-adjacent structure,
- keep current GRC9 runtime semantics unchanged while reviewing whether any
  diagnostic collapse-adjacent evidence is warranted,
- keep the Phase T-GRC9 contract stable unless a new diagnostic-only group or
  new version is accepted,
- add Phase V-GRC9 visual language only after saved telemetry/checkpoint
  evidence defines what should be shown.

## Phase T-GRC9 Review Outcome

Phase T-GRC9 currently treats choice/collapse semantics as out of scope. That
boundary remains correct for GRCV3-style choice collapse.

The Phase T-GRC9 review is recorded in
[Phase-T-GRC9-CollapseAdjacentObservabilityReview.md](./Phase-T-GRC9-CollapseAdjacentObservabilityReview.md).
It accepts selector-backed structural diagnostics over existing telemetry and
checkpoints for the next GRCL-9 batch.

Accepted existing evidence:

- failed fission persistence through identity-fission run-summary fields,
- sink/basin pressure through `identity_abundance` step fields and checkpoints,
- transport/support pressure through `transport` step fields and checkpoints,
- membrane/ridge rupture only as structural/checkpoint-backed evidence through
  GRCL-9 provenance.

The review did not add a `collapse` lifecycle event, a `collapse_evidence`
group, or compact collapse-adjacent summary fields.

Future Phase T work may still consider whether any of the following deserve
compact diagnostic telemetry after the next GRCL-9 probe batch:

- basin merge candidate,
- sink loss or sink dominance loss,
- module support failure,
- membrane/ridge rupture as structural boundary loss,
- failed identity-fission persistence after a two-sink candidate appears,
- strong support asymmetry that collapses a post-expansion region back into a
  single sink.

Reserved telemetry names, if later justified:

- `structural_integrity_summary`
- `basin_merge_candidate_count`
- `sink_loss_candidate_count`
- `membrane_rupture_candidate_count`
- `support_loss_candidate_count`
- `collapse_candidate_summary`

These names are placeholders. They are not part of the current Phase T-GRC9
contract.

Required boundary:

- do not add GRCV3 `choice` / `collapse_registry` semantics to GRC9,
- do not add a `collapse` event kind unless GRC9 runtime criteria are accepted,
- prefer diagnostic-only summaries first,
- preserve current `phase_t_grc9_iter1_v1` meaning unless a new contract
  version is introduced.

## Phase V-GRC9 Review Outcome

Phase V-GRC9 already renders port charts, flux, modules, basins, sinks, and
identity-fission overlays. The Phase V-GRC9 review is recorded in
[Phase-V-GRC9-CollapseAdjacentVisualizationReview.md](./Phase-V-GRC9-CollapseAdjacentVisualizationReview.md).
It accepts manifest-driven structural visualization over existing behavior
plots, graph checkpoints, and GRCL-9 provenance for the next collapse-adjacent
batch.

Accepted visualization needs:

- show basin merge candidates as basin-overlap or basin-convergence overlays,
- show sink-loss candidates as sink-status changes over time,
- show membrane/ridge rupture candidates as boundary edge weakening or
  inactive-boundary loss,
- show support-loss candidates as disappearing or asymmetric support paths,
- show failed fission persistence as a two-sink candidate that does not satisfy
  the persistence window.

Required boundary:

- do not draw GRCV3 collapse links for GRC9,
- do not label a GRC9 node as collapsed unless Phase T defines such telemetry,
- use `collapse_candidate`, `structural_collapse_probe`,
  `basin_merge_pressure_candidate`, or `support_loss_pressure_candidate` labels
  only when the upstream selector/report artifact explicitly provides that
  status.

## Planned GRCL-9 Seed Scope

GRCL-9 can add source seeds for collapse-adjacent structure before GRC9 has a
collapse event. Those seeds should be treated as structural probes.

Proposed Iteration 8.1 seed families:

- `cell_membrane_rupture_structural_probe`
- `cell_basin_merge_before_persistence_probe`
- `cell_support_loss_identity_decay_probe`
- `cell_saddle_choice_pressure_structural_probe`

Expected classification in replay/catalog artifacts:

- `structural_only`
- `observed_non_fission`
- `basin_merge_candidate`
- `support_loss_candidate`
- `collapse_reserved_future`

Selectors should use existing fields where possible:

- lifecycle counts for absence of spark/expansion/growth where relevant,
- identity-fission confirmed versus candidate summaries,
- basin size and sink count summaries,
- transport/support summaries,
- graph checkpoint topology and motif-role overlays.

## Planned Iteration Sequence

### Iteration 8.1: Collapse-Adjacent Structural Seeds

Document and run the next batch of collapse-adjacent GRCL-9 source seeds as
structural probes. Do not claim collapse.

Expected outputs:

- this review document,
- updated GRCL-9 plan/checklist,
- Phase T-GRC9 review notes,
- Phase V-GRC9 review notes,
- collapse-adjacent seed examples,
- a replay session, expected `S0009`,
- selector or report output that classifies the gap honestly.

Implemented S0009 outputs:

- `outputs/grcl9/lowering/sessions/S0009/session_manifest.json`
- `outputs/grcl9/lowering/sessions/S0009/source_fixtures/`
- `outputs/grcl9/lowering/sessions/S0009/lowered_states/`
- `outputs/grcl9/lowering/sessions/S0009/reports/`
- `outputs/grcl9/lowering/sessions/S0009/visualizations/`

S0009 lanes:

- `cell_membrane_rupture_structural_probe`
- `cell_basin_merge_before_persistence_probe`
- `cell_support_loss_identity_decay_probe`
- `cell_saddle_choice_pressure_structural_probe`

All four selector reports passed. They classify structural probes and
candidate evidence only; none claims runtime collapse. Checking S0009 visuals
confirmed the same boundary: the transparent-source/arrow/target overlays are
collapse-adjacent structural markers, not observed runtime collapse.

### Phase T/V Collapse Observability Review

Phase T-GRC9 review is complete: use existing fields and checkpoints first,
and defer compact collapse-adjacent fields until selector failures justify
them. Phase V-GRC9 review is complete: render structural probes from existing
visuals plus upstream selector/report artifacts, with the same
transparent-source/arrow/target visual grammar used by GRCV3 collapse views
when the overlay is explicitly labeled `collapse_adjacent_structural_probe`.

Expected decision:

- visualization from existing fields/checkpoints,
- manifest-driven collapse-adjacent labels when upstream reports provide them,
- unified transparent-source/arrow/target visual affordance for labeled
  structural probes,
- compact-telemetry-driven collapse overlays deferred until future compact
  telemetry exists.

### Iteration 8.2: Collapse-Producing Seed Discovery

S0009 is not enough to close the collapse question. It proves GRCL-9 can author
collapse-adjacent structure, but not that current GRC9 dynamics produce a
collapse-like transition from those seeds.

Implement a targeted discovery pass before any extension/handoff step:

- author intensified GRCL landscape seeds from the 8.1 mechanisms,
- vary basin mass, bridge conductance, support conductance, outward pressure,
  and persistence thresholds in pass/fail families,
- compile through the GRCL/Morse example layer,
- lower to connected GRC9 graphs,
- replay with checkpoints, selector reports, and visuals,
- classify lanes as `runtime_collapse_like_observed`, `structural_only`,
  `ambiguous`, or `failed_control`.

Expected result:

- a replayable session after `S0009`,
- a clear decision on whether collapse-like behavior can be produced by
  source-authored GRCL-9 seeds under current GRC9,
- or an explicit record that collapse remains structural-only/reserved-future.

Implemented replay outputs:

- `outputs/grcl9/lowering/sessions/S0010/` records the six-step attempt. It is
  replayable but not accepted as positive evidence because both lanes ended
  ambiguous/missed after the diagnostic window.

- `outputs/grcl9/lowering/sessions/S0011/session_manifest.json`
- `outputs/grcl9/lowering/sessions/S0011/source_fixtures/`
- `outputs/grcl9/lowering/sessions/S0011/lowered_states/`
- `outputs/grcl9/lowering/sessions/S0011/reports/`
- `outputs/grcl9/lowering/sessions/S0011/visualizations/`

S0011 lanes:

- `cell_basin_merge_runtime_collapse_probe`
  - selector: `runtime_collapse_like_observed`
  - observed classification: `runtime_collapse_like_observed`
  - lost source sink role: `fission_sink_b`
- `cell_basin_merge_runtime_stability_control`
  - selector: `structural_only`
  - observed classification: `structural_only`
  - lost source sink roles: none

This establishes a GRC9-native diagnostic collapse-like observation from
runtime identity/sink telemetry and checkpoints. It still does not add a GRC9
`collapse` event kind.

Follow-up long-window developed-basin run:

- `outputs/grcl9/lowering/sessions/S0012/` records the first 24-step
  developed-basin attempt. It remained a selector miss.
- `outputs/grcl9/lowering/sessions/S0013/` records the second 24-step
  developed-basin attempt after support-bridge tuning. It remained a selector
  miss.
- `outputs/grcl9/lowering/sessions/S0014/` records the third 24-step attempt
  after diagnostic classifier broadening. It remained a selector miss because
  the long-window selector still expected its own id rather than the accepted
  observed classification.
- `outputs/grcl9/lowering/sessions/S0015/` records the accepted third complex
  example:
  - fixture: `cell_developed_basin_centroid_collapse_long_window`
  - requested steps: `24`
  - checkpoints: `25`
  - lowered graph size: `15` nodes, `21` edges
  - selector: `runtime_collapse_like_long_window`
  - observed classification: `runtime_collapse_like_observed`
  - target selection policy: `group_centroid`
  - selected target node: `1`

The S0015 result is intentionally more cautious than GRCV3 collapse: the source
anchor `fission_sink_b` is lost as a final runtime sink and the receiving basin
target is selected by centroid policy, but several weak support nodes from the
decaying basin remain final sinks. The report therefore preserves
`residual_collapsing_basin_sink_roles` instead of claiming full basin collapse.

Full-capacity cascade run:

- `outputs/grcl9/lowering/sessions/S0016/` and `S0017` record initial cascade
  attempts where spark/expansion/growth fired but the fission/collapse-like
  selector missed.
- `outputs/grcl9/lowering/sessions/S0018/` and `S0019` record tuning attempts
  that reduced overgrowth and prevented extra fission-region sparks, but still
  missed before GRCL-9 provenance was preserved across topology mutation.
- `outputs/grcl9/lowering/sessions/S0020/` is accepted:
  - fixture: `cell_full_capacity_phenomenology_cascade`
  - requested steps: `24`
  - lowered graph size: `24` nodes, `28` edges
  - runtime events: `1` spark, `1` expansion, `60` growth
  - selector status: `passed`
  - collapse-like selector: `runtime_collapse_like_long_window`
  - selected target node: `14`
  - target selection policy: `group_centroid`

S0020 shows the largest current GRCL-9 source-authored example: multiple
phenomenology mechanisms are present in one connected GRC9 replay. The same
non-claim remains in force: no GRC9 `collapse` event kind is introduced.

Robustness family:

- `outputs/grcl9/lowering/sessions/S0021/` records the S0020 perturbation
  family over eight lanes and 24 steps per lane.
- Accepted robustness lanes:
  - `cell_full_capacity_phenomenology_cascade`
  - `cell_full_capacity_cascade_low_growth`
  - `cell_full_capacity_cascade_high_growth`
- Diagnostic misses:
  - `cell_full_capacity_cascade_no_merge_bridge`
  - `cell_full_capacity_cascade_weak_merge_bridge`
  - `cell_full_capacity_cascade_larger_basin_support`
  - `cell_full_capacity_cascade_no_refinement`
  - `cell_full_capacity_cascade_no_growth`

The S0021 result is important because it falsifies the simplest bridge
necessity assumption: removing or weakening the explicit merge bridge did not
prevent collapse-like sink-role loss under the current GRC9 dynamics. The
larger-basin, no-refinement, and no-growth variants remain diagnostic controls
for selector boundaries rather than accepted cascade examples.

Refined robustness run:

- `outputs/grcl9/lowering/sessions/S0022/` adds a ninth lane,
  `cell_full_capacity_cascade_isolated_bridge`, with negligible fission bridge
  conductance.
- S0022 also refines selectors:
  - `runtime_expansion_count` checks actual expansion events instead of
    fission module-size summaries,
  - `runtime_collapse_like_ambiguous` records larger-basin multi-anchor loss
    as an explicit diagnostic classification.
- Accepted diagnostic lanes in S0022:
  - baseline, low-growth, high-growth,
  - larger-basin ambiguous classification,
  - no-refinement negative expansion-event control.
- Still-missed bridge controls:
  - no-merge bridge,
  - weak-merge bridge,
  - isolated negligible bridge.

The isolated-bridge miss strengthens the S0021 conclusion: current
collapse-like sink-role loss is not explained by explicit fission bridge
strength alone. Growth removal remains the cleanest lifecycle negative control.

Basin-asymmetry ladder:

- `outputs/grcl9/lowering/sessions/S0023/` keeps the full-capacity cascade
  fixed and varies only post-refinement basin mass/stability.
- `cell_full_capacity_cascade_balanced_basins` misses the structural-only
  hypothesis and classifies as ambiguous: the source A anchor is lost while B
  remains.
- `cell_full_capacity_cascade_mild_asymmetry` already produces collapse-like
  B-loss.
- `cell_full_capacity_cascade_threshold_asymmetry`,
  `cell_full_capacity_cascade_deep_collapse`, and
  `cell_full_capacity_cascade_isolated_threshold` all pass collapse-like
  B-loss selectors.

S0023 shows that the full-capacity cascade is more sensitive to identity-anchor
competition than the initial mass-ladder hypothesis expected. It also
reinforces the S0022 bridge conclusion: the isolated-threshold lane still
produces B-loss.

Phase diagram:

- `outputs/grcl9/lowering/sessions/S0024/` crosses four basin regimes with
  three growth regimes:
  - balanced, mild, threshold, deep,
  - no-growth, low-growth, nominal-growth.
- All no-growth lanes classify as ambiguous with both source sink anchors
  lost.
- Balanced low/nominal lanes classify as ambiguous with A-anchor loss.
- Threshold and deep low/nominal lanes classify as collapse-like B-loss.
- Mild asymmetry is the transition row:
  - no-growth is ambiguous,
  - low-growth is ambiguous after runaway event amplification,
  - nominal-growth is collapse-like B-loss.

S0024 is the strongest current mechanism evidence: collapse-like sink-role loss
appears as a basin-asymmetry/growth-pressure regime boundary, while explicit
bridge strength remains secondary in the tested family.

S0024 is packaged for citation:

- `outputs/grcl9/lowering/sessions/S0024/reports/phase_diagram_summary.json`
- `outputs/grcl9/lowering/sessions/S0024/reports/phase_diagram_summary.md`
- `outputs/grcl9/lowering/sessions/S0024/visualizations/phase_diagram_visual_index.md`

### Iteration 8.5: Collapse Extension Implementation

Implemented the accepted path from the review and the 8.2 discovery pass:

- Phase T remains unchanged; no GRC9 `collapse` event or collapse equation is
  introduced.
- Phase V remains checkpoint/telemetry-backed; collapse-like views are rendered
  as source-role overlays and phase summaries, not runtime-collapse claims.
- The reviewed catalog generator records an additive `collapse_diagnostic`
  block for accepted collapse-related selectors.

Accepted catalog result:

- keep `S0008` as the first reviewed lowered motif catalog,
- create `S0025` from source session `S0024`,
- accept 12 S0024 phase-diagram motifs,
- record 5 `runtime_collapse_like_diagnostic` entries and 7
  `ambiguous_collapse_like_diagnostic` entries,
- link each catalog entry back to the S0024 phase-diagram summary and visual
  index.

Artifacts:

- `outputs/grcl9/lowering/sessions/S0025/reviewed_grcl9_lowered_motif_catalog.json`
- `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_report.json`
- `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_summary.md`

## Non-Claims

- This document does not add collapse semantics to GRC9.
- This document does not import GRCV3 choice/collapse behavior into GRCL-9.
- Structural collapse seeds are not proof of runtime collapse.
- ComposingCells dysfunction language remains source-side unless telemetry
  evidence is explicitly added.
