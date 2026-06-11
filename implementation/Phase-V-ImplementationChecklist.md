# Phase V Implementation Checklist

This document tracks the execution of **Phase V: Visualization Surfaces**.

It is intentionally separate from
[`Phase-V-ImplementationPlan.md`](./Phase-V-ImplementationPlan.md):

- the plan defines the boundary, workstreams, and acceptance criteria,
- this checklist records the implementation sequence and decisions.

## Iteration 0. Checklist Bootstrap

### Goal

Create the Phase V execution checklist and align it with the existing telemetry
handoff and the actual 100-step representative lane.

### Checks

- [x] Create `Phase-V-ImplementationPlan.md`
- [x] Create `Phase-V-ImplementationChecklist.md`
- [x] Link the Phase V plan/checklist from `ImplementationPhases.md`
- [x] Record the distinction between:
  - visuals already supported by current Phase T artifacts
  - graph/flow visuals that require additional artifact support
- [x] Record the 100-step `cell-1` / `cell-4` representative lane as the first
  serious visualization target

### Implementation Notes

- Phase V starts from a stronger baseline than originally assumed.
- The 3-step representative lane was enough for telemetry contract work, but
  the 100-step lane is the correct visualization baseline because it already
  exposes:
  - quiescent relaxation in `cell-1`
  - delayed, extended birth activity in `cell-4`
  - topology-count divergence
  - stable budget conservation in both runs
- Current telemetry can already support:
  - scalar trajectory plots
  - event timelines
  - report/comparison panels
- Current telemetry cannot yet support:
  - saved graph snapshots over time
  - graph-local event overlays
  - saved flow-field visuals

### Verification

- [x] Phase V now has a dedicated plan/checklist pair
- [x] The visualization boundary remains downstream of telemetry artifacts
- [x] The first visualization lane is grounded in an existing saved run set

### Summary

Phase V now exists as an executable implementation phase rather than just a
handoff note. The project has an explicit visualization plan centered on the
artifact-backed 100-step `cell-1` / `cell-4` lane, with a clear distinction
between visuals that can be built immediately and graph/flow visuals that still
need additional artifact support.

## Iteration 1. Visualization Package Boundary

### Goal

Create the shared visualization package and define the artifact-first rendering
boundary.

### Checks

- [x] Create `src/pygrc/visualization/`
- [x] Define the first public visualization export surface
- [x] Keep rendering code downstream of telemetry/report artifacts
- [x] Decide the visualization output-root convention under `outputs/`
- [x] Lock the standard plotting backend to `matplotlib`
- [x] Lock the graph interchange/rendering stack to `networkx` + `pyvis`
- [x] Record that Phase V will not implement a bespoke graph renderer
- [x] Add import-smoke coverage for the visualization package

### Implementation Notes

- The visualization layer should consume:
  - `TelemetryArtifactPack`
  - `TelemetryExperimentReport`
  - `TelemetryComparisonReport`
- The first boundary should stay narrow and explicit:
  - artifact loading
  - figure/panel generation
  - output-path helpers
- The intended rendering strategy is:
  - `matplotlib` for trajectories, timelines, and report panels
  - `networkx` as the graph interchange layer for graph-capable artifacts
  - `pyvis` for interactive graph rendering once checkpoint graph artifacts
    exist
  - `PyGRC` custom code only for adapters, layout policy, and composition
- Do not let Phase V reach directly into family model internals when the same
  information already exists in saved artifacts.
- Do not spend Phase V effort building custom graph drawing/layout logic beyond
  trivial debug helpers.
- Implemented visualization package/modules:
  - `src/pygrc/visualization/layout.py`
  - `src/pygrc/visualization/render.py`
  - `src/pygrc/visualization/representative.py`
  - `src/pygrc/visualization/__init__.py`
- Implemented representative rendering CLI:
  - `src/pygrc/cli/grcv2_representative_visuals.py`
- The representative CLI now exposes the current scope explicitly through:
  - `--surface behavior`
- Graph-facing surface requests are intentionally rejected for now rather than
  silently pretending graph outputs exist.
- Added a dedicated future graph entrypoint:
  - `src/pygrc/cli/grcv2_representative_graphs.py`
  - it currently fails explicitly with the topology/flow blocker message
- Chosen output convention:
  - per-run visuals under `outputs/experiments/.../<run_id>/visualization/`
  - comparison visuals under
    `outputs/experiments/.../comparison/<left>__vs__<right>/visualization/`

### Verification

- [x] Visualization imports cleanly from the package boundary
- [x] No live `GRCV2` model instance is required for the first-pass rendering path
- [x] Output-path conventions remain relative and repo-shareable
- [x] The backend strategy is explicit enough that graph rendering is delegated
  to standard libraries rather than reinvented locally

### Summary

Completed the shared visualization package boundary for the first-pass Phase V
slice. Visualization is now an artifact-driven package with deterministic
output layouts, a representative rendering CLI, and an explicit non-bespoke
backend strategy built around `matplotlib` now and `networkx`/`pyvis` later.

## Iteration 2. Trajectory Plot Contract

### Goal

Implement deterministic one-run trajectory plots from `steps.jsonl` and
`run_summary.json`.

### Checks

- [x] Define the trajectory-plot input contract
- [x] Implement one-run trajectory rendering helpers
- [ ] Cover the minimum observables:
  - [x] `budget_current`
  - [x] `budget_error`
  - [x] `num_nodes`
  - [x] `num_edges`
  - [x] `sink_count`
  - [x] `birth_count`
  - [x] `average_conductance`
  - [x] `abundance`
  - [x] `weighted_abundance`
- [x] Define figure naming/output conventions for one-run trajectory artifacts
- [x] Add deterministic rendering/load tests

### Implementation Notes

- This iteration should make budget conservation and growth/relaxation visually
  inspectable without any comparison logic yet.
- The default demonstration run should be the saved 100-step representative
  lane, not the original 3-step telemetry lane.

### Verification

- [x] `cell-1` renders as a quiescent/settling trajectory
- [x] `cell-4` renders as a growth-capable trajectory
- [x] budget-conservation lines are visibly flat for both runs

### Summary

Completed the first one-run trajectory rendering slice. The saved 100-step
representative runs now render deterministic multi-observable trajectory PNGs,
including budget-conservation lines and the main growth/relaxation observables.

## Iteration 3. Event Timelines

### Goal

Render event timing explicitly from `events.jsonl` and per-step event counts.

### Checks

- [x] Define the event-timeline input contract
- [x] Implement per-run event timeline rendering
- [x] Implement per-step event-count rendering
- [x] Define empty-event rendering behavior
- [x] Add tests for both empty-event and eventful runs

### Implementation Notes

- Empty-event runs must render honestly as event-free, not as missing data.
- `cell-4` should make delayed onset directly visible.
- `cell-1` should validate the no-event path.

### Verification

- [x] Empty-event runs produce valid visuals
- [x] Eventful runs show onset and late-run activity clearly
- [x] Timeline labels map directly to saved event fields

### Summary

Completed the event-timeline slice. Empty-event runs render honestly as
event-free, while eventful runs render both a timeline and per-step event-count
panel from the saved step/event artifacts.

## Iteration 4. Comparison Plots

### Goal

Implement deterministic two-run comparison visuals from saved reports and
telemetry artifacts.

### Checks

- [x] Define the comparison-plot input contract
- [x] Implement pairwise observable comparison rendering
- [x] Implement direct use of `comparison_report.json`
- [x] Make comparison labeling identity-safe:
  - [x] run IDs
  - [x] seed names
  - [x] family name
  - [x] step count
  - [x] RNG seed when available
- [x] Add comparison rendering tests

### Implementation Notes

- Comparison visuals should come from explicit report fields and shared
  telemetry structures rather than from hand-written alignment logic.
- The first pair should remain:
  - `cell-1`
  - `cell-4`
  - `balanced_baseline`
  - `num_steps = 100`

### Verification

- [x] The `cell-1` / `cell-4` behavioral split is visually obvious
- [x] Final-summary deltas match the saved comparison report
- [x] No live model object is required to render the comparison

### Summary

Completed the pairwise comparison rendering slice. The first-pass comparison
PNG now overlays the main observable trajectories for `cell-1` versus `cell-4`
and is driven directly by the saved report/telemetry artifacts.

## Iteration 5. Experiment Panels

### Goal

Turn experiment and comparison reports into compact report-facing panels.

### Checks

- [x] Render changed-observables panels
- [x] Render event-count panels
- [x] Render checkpoint-overview panels
- [x] Render final-summary delta panels
- [x] Define panel composition/layout conventions
- [x] Add tests for report-driven panels

### Implementation Notes

- This iteration should not invent new report fields.
- Panels must map directly to existing report payloads from Phase T.
- The goal is legibility of evidence, not dashboard complexity.

### Verification

- [x] Report panels can be regenerated directly from saved report files
- [x] Panel labels correspond to explicit report keys
- [x] The panel set is sufficient to explain the representative runs without
  prose-only interpretation

### Summary

Completed the first report-panel slice. Run and comparison panels are now
generated directly from saved report payloads and capture changed observables,
event counts, checkpoint overview, and final-summary deltas without scraping
raw JSON by hand.

## Iteration 6. Topology And Flow Artifact Bridge

### Goal

Define the missing topology and flow artifact requirements before nontrivial
graph rendering work begins.

### Checks

- [x] Define minimum topology snapshot requirements:
  - [x] node IDs
  - [x] edge connectivity
  - [x] checkpoint identity
  - [x] node overlay attributes
  - [x] edge overlay attributes
- [x] Define minimum flow export requirements:
  - [x] per-edge flux or explicit flow surrogate
  - [x] node net-flux summaries when relevant
  - [x] conductance versus flux distinction
- [x] Decide layout policy expectations:
  - [x] saved layout hints optional
  - [x] deterministic render-time layout acceptable
- [x] Record the required upstream extension point

### Implementation Notes

- This iteration is intentionally earlier than graph rendering.
- The point is to avoid starting `networkx`/`pyvis` work without graph-shaped
  artifact data to feed them.
- Coordinates should be treated as optional layout aids, not mandatory source
  semantics.
- Recorded the bridge contract in:
  - `implementation/Phase-V-TopologyFlowArtifactBridge.md`
- Chosen artifact-shape rule:
  - graph-shaped data lives in optional checkpoint sidecars rather than in
    `steps.jsonl`
- Chosen checkpoint storage convention:
  - `graph_checkpoints/index.json`
  - one checkpoint JSON file per saved step/checkpoint
- Chosen minimum common topology payload:
  - checkpoint identity
  - `graph_kind`
  - stable node IDs
  - deterministic edge list with stable edge IDs
- Chosen minimum common overlays:
  - node:
    - `coherence`
  - edge:
    - `base_conductance`
- Chosen flow rule:
  - prefer per-edge `signed_flux`
  - allow `flux_coupling` only as an explicitly declared
    `magnitude_only_surrogate`
- Chosen layout rule:
  - saved layout hints remain optional
  - deterministic render-time layout is acceptable when hints are absent
- Chosen upstream attachment point:
  - future schema, I/O, and recorder extensions in the telemetry layer
  - family-aware export hook/adapter upstream of visualization

### Verification

- [x] The topology/flow artifact gap is written down explicitly
- [x] The required upstream changes are identifiable
- [x] No graph-rendering work depends on invented or unsaved data

### Summary

Closed the topology/flow artifact bridge at the contract level. Phase V now
has a written bridge document that defines checkpoint sidecar artifacts,
minimum topology payload, minimum node/edge overlays, honest flow
representation rules, optional layout-hint policy, and the telemetry-side
extension point required before graph rendering begins in earnest.

## Iteration 7. Representative Lane Closeout

### Goal

Use the 100-step representative lane to validate the first-pass visualization
stack end to end.

### Checks

- [x] Render the full first-pass visual set for:
  - [x] `cell-1`
  - [x] `cell-4`
  - [x] `cell-1` vs `cell-4` comparison
- [x] Verify budget conservation is directly visible
- [x] Verify delayed birth onset is directly visible
- [x] Verify topology-count divergence is directly visible
- [x] Record any visualization limitations discovered from the representative lane

### Implementation Notes

- This is the phase-level reality check.
- The visuals should make it easy to see:
  - `cell-1` settles
  - `cell-4` branches and expands
  - both preserve budget
- If anything still requires manual interpretation from raw JSON, it should be
  treated as an unresolved visualization gap.
- Representative rendered outputs now exist under:
  - `outputs/experiments/grcv2/representative/balanced_baseline/`
- Observed milestone-level evidence from the saved lane:
  - `cell-1` remains event-free and visually reads as a settling run
  - `cell-4` shows delayed birth onset and extended birth activity
  - budget-conservation lines are flat in both runs
  - node/edge/sink growth divergence is directly visible
  - report panels are strong enough to explain the scalar/report behavior
    without reopening raw telemetry files
- Recorded the milestone separately in:
  - `implementation/Phase-V-Milestone-1.md`
- The current CLI contract is intentionally scoped to:
  - `--surface behavior`
  - with graph surfaces deferred until the topology/flow artifact bridge lands

### Verification

- [x] The representative visualization lane is reviewable from saved artifacts only
- [x] No unresolved blocker remains for trajectory/event/report visuals
- [x] The outputs are strong enough to support later graph-facing extensions

### Summary

Closed the first representative visualization milestone. The saved 100-step
`cell-1` / `cell-4` lane now renders trajectories, event timelines, and
report/comparison panels strongly enough to distinguish quiescent relaxation
from delayed expansive behavior while keeping budget conservation directly
inspectable. The remaining gap is now clearly isolated to graph/flow artifact
support rather than to the scalar/report visualization layer.

## Iteration 8. Graph-Evolution Contract

### Goal

Write the artifact contract needed for honest graph-evolution rendering.

### Checks

- [x] Define checkpoint-topology export requirements
- [x] Define node-attribute export requirements
- [x] Define edge-attribute export requirements
- [x] Define event-to-checkpoint linking requirements
- [x] Record what Phase T or a bridge iteration must add upstream

### Implementation Notes

- This is a contract-design iteration, not a speculative rendering iteration.
- The resulting document should make it possible to implement graph evolution
  later without reaching back into live model state.
- Recorded the graph-evolution contract in:
  - `implementation/Phase-V-GraphEvolutionContract.md`
- Chosen graph-evolution artifact family:
  - `graph_checkpoints/index.json`
  - one checkpoint payload file per saved frame
- Chosen checkpoint-linking rule:
  - each checkpoint entry must link to an explicit event window
  - preferably through `event_row_range`, otherwise through `event_step_range`
- Chosen identity rule:
  - stable node IDs and stable edge IDs across checkpoints
- Chosen upstream additions:
  - checkpoint index schema
  - checkpoint payload schema
  - checkpoint save/load helpers
  - recorder support for interval/explicit/eventful checkpoint selection
  - family-aware graph-checkpoint export hooks

### Verification

- [x] A written graph-evolution artifact contract exists
- [x] The contract is family-extensible rather than `GRCV2`-only
- [x] The contract is explicit about what is currently missing

### Summary

Closed the graph-evolution contract. Phase V now has a written checkpoint
sequence contract that defines index and payload artifacts, stable topology
identity across checkpoints, required node/edge overlay surfaces, explicit
event-window linkage, and the telemetry/runtime extensions required before
graph-evolution rendering can begin honestly.

## Iteration 9. Flow-Activity Contract

### Goal

Write the artifact contract needed for honest flow-activity rendering.

### Checks

- [x] Define per-edge flux export requirements
- [x] Define node net-flux export requirements
- [x] Distinguish conductance overlays from flux overlays
- [x] Define checkpoint or per-step export cadence expectations
- [x] Record what upstream telemetry extensions are required

### Implementation Notes

- Flow activity is visually important, but it is not currently exported by the
  saved Phase T lane.
- The deliverable here is a strict artifact requirement set, not a visual mock
  on invented data.
- Recorded the flow-activity contract in:
  - `implementation/Phase-V-FlowActivityContract.md`
- Chosen preferred flow export:
  - per-edge `signed_flux`
- Chosen allowed fallback:
  - `flux_coupling` only as explicitly declared `magnitude_only_surrogate`
- Chosen conductance/flow distinction:
  - `base_conductance`
  - `signed_flux`
  - `flux_coupling`
  - all treated as separate visual channels
- Chosen cadence rule:
  - checkpoint-based flow export is the first honest default
  - per-step flow export is an explicit higher-cost future mode
- Chosen upstream additions:
  - checkpoint edge-flow payloads
  - node flow summaries
  - flow metadata fields
  - recorder controls for flow export and cadence

### Verification

- [x] A written flow-activity artifact contract exists
- [x] The contract does not rely on unsaved live model state
- [x] The contract makes the next upstream extension step obvious

### Summary

Closed the flow-activity contract. Phase V now has a written flow artifact
surface that defines preferred signed edge flux export, node net-flow
summaries, explicit conductance-versus-flow separation, checkpoint-first
cadence expectations, and the telemetry/runtime extensions required before
flow visuals can be rendered honestly.

## Iteration 10. Graph Snapshot Rendering

### Goal

Render checkpoint-backed static graph visuals without touching live model state.

### Checks

- [x] Implement graph bundle rendering from `TelemetryArtifactPack.graph_checkpoints`
- [x] Convert checkpoint payloads into a standard graph interchange model
- [x] Define one deterministic layout policy reused across all frames in a run
- [x] Render one PNG snapshot per saved checkpoint
- [x] Render a compact sequence/contact-sheet figure for each run
- [x] Render a side-by-side final-checkpoint comparison figure
- [x] Add direct graph-render tests

### Implementation Notes

- Rendering is now strictly artifact-driven from saved graph checkpoints.
- The graph adapter targets `networkx`; `PyGRC` owns only:
  - payload adaptation
  - deterministic layout policy
  - styling/composition
- Chosen layout policy:
  - compute a union-of-checkpoints graph per run
  - derive one deterministic spring layout for that union
  - reuse that same layout for every checkpoint frame
- This intentionally favors temporal stability over per-frame re-layout.
- Existing nodes therefore stay fixed on the canvas across frames instead of
  jittering between checkpoints.

### Verification

- [x] Saved checkpoints render to stable static PNG snapshots
- [x] The comparison view is generated from checkpoint artifacts only
- [x] No graph render path requires a live model instance

### Summary

Closed the first graph-rendering implementation slice. Phase V now renders
checkpoint-backed graph snapshots, run-level contact sheets, and a final
comparison figure directly from saved telemetry artifacts while keeping the
layout fixed across the full run.

## Iteration 11. Interactive HTML And Dense Animation

### Goal

Turn graph checkpoints into reviewable outputs for both sparse and dense
cadence runs.

### Checks

- [x] Emit an interactive final-graph HTML artifact for each run
- [x] Emit a deterministic layout JSON sidecar for graph review/reuse
- [x] Emit a dense animation artifact when more than one checkpoint exists
- [x] Make the dense output an actual animation rather than just frame dumps
- [x] Keep graph animation tied to the stable run-level layout
- [x] Add tests covering HTML and animation output

### Implementation Notes

- Interactive HTML is generated from the final checkpoint using `pyvis`.
- Dense animation is currently emitted as a deterministic GIF assembled from
  saved snapshot frames.
- Sparse cadence remains useful through:
  - individual PNG snapshots
  - sequence/contact-sheet figures
- Dense cadence now adds:
  - `graph_animation.gif`
- The layout JSON sidecar records the reused run-level positions so the visual
  contract is inspectable rather than implicit.

### Verification

- [x] Final interactive HTML files are written for graph-capable runs
- [x] Dense checkpoint runs emit animation artifacts
- [x] Frame-to-frame node positions remain stable because the layout is reused

### Summary

Closed the dense-output requirement for Phase V. Graph-capable runs now emit
interactive final HTML and, when checkpoint cadence is dense enough, a true
animation artifact rather than just isolated still frames.

## Iteration 12. Representative Graph Surface Integration

### Goal

Expose the graph visualization surface cleanly through the representative APIs,
CLI entrypoints, and explicit missing-artifact errors.

### Checks

- [x] Replace the old graph blocker API with real representative graph rendering
- [x] Support `surface=graph` in the representative visualization suite
- [x] Support `surface=all` in the representative visualization suite
- [x] Keep explicit failure when graph checkpoints were not recorded
- [x] Update the dedicated representative graph CLI
- [x] Update visualization tests from blocker expectations to output expectations

### Implementation Notes

- The old "graph blocked until bridge lands" boundary is now gone.
- The current boundary is stricter and more useful:
  - graph rendering works when checkpoint artifacts exist
  - graph rendering fails explicitly when those artifacts are absent
- This keeps the phase artifact-first while removing the stale blocker posture.

### Verification

- [x] `render_grcv2_representative_graph_suite()` produces graph outputs
- [x] `--surface graph` works when checkpoints exist
- [x] `--surface graph` fails explicitly when checkpoints do not exist
- [x] Dense representative runs emit graph animations

### Summary

Closed the representative graph integration slice. Phase V now exposes graph
rendering as a real checkpoint-backed surface through both the dedicated graph
command and the shared representative visualization CLI, while preserving
explicit erroring for telemetry lanes that were recorded without graph
checkpoints.

## Iteration 13. GRCV3 Visualization Planning Boundary

### Goal

Record the correct next-family visualization order after the `GRCV3` telemetry
slice landed.

### Checks

- [x] Update the Phase V plan so `GRCV3` is named as the next behavior-facing
      visualization lane
- [x] Record that completed `GRCV2` graph visualization does not imply
      completed `GRCV3` graph visualization
- [x] Record that `GRCV3` graph-visible visualization is blocked on later Phase
      T checkpoint telemetry
- [x] Record the intended next `GRCV3` visualization iterations in this
      checklist

### Implementation Notes

- This is a planning/documentation boundary, not new rendering code.
- The purpose is to stop the family statuses from drifting together.
- Updated the Phase V plan to read in a family-specific way:
  - `GRCV2` visualization lane remains the mature graph-capable lane
  - `GRCV3` is now the next behavior-facing lane only
- Added two new Phase V workstreams:
  - `GRCV3` behavior visualization lane
  - deferred `GRCV3` graph visualization boundary
- Added the next pending `GRCV3` visualization iterations:
  - Iteration 14: `GRCV3` behavior visualization lane
  - Iteration 15: `GRCV3` behavior visualization closeout
- Coordinated the dependency back to Phase T:
  - later `GRCV3` checkpoint telemetry remains upstream of any graph-visible
    `GRCV3` rendering

### Verification

- [x] Phase V now reads correctly for both `GRCV2` and `GRCV3`
- [x] The dependency on later Phase T `GRCV3` graph telemetry is explicit

### Summary

Iteration 13 corrected the family boundary in Phase V. The completed `GRCV2`
graph lane is no longer implied to cover `GRCV3`, and the next justified Phase
V work is now explicitly the behavior-facing `GRCV3` lane.

## Iteration 14. GRCV3 Behavior Visualization Lane

### Goal

Render the first behavior-facing `GRCV3` visuals from saved telemetry and
report artifacts only.

### Checks

- [x] Define the representative `GRCV3` visualization input lane
- [x] Render `primary` run behavior-facing visuals
- [x] Render `replay` run behavior-facing visuals
- [x] Render `primary` vs `replay` comparison visuals
- [x] Surface `grcv3` family-extension summaries in an experiment-facing form
- [x] Add focused tests for the `GRCV3` behavior visualization path

### Implementation Notes

- This should reuse the existing artifact-first visualization stack rather than
  inventing a `GRCV3`-local renderer.
- Graph surfaces are still out of scope here.
- Landed API surface:
  - `render_grcv3_representative_visual_suite(...)`
- Landed CLI surface:
  - `src/pygrc/cli/grcv3_representative_visuals.py`
- The behavior figures now expose:
  - direct saved `GRCV3` observables
  - selected numeric step-row `grcv3` family-extension traces
- The run/comparison text panels now flatten family extensions, so the
  experiment-facing output includes:
  - `grcv3` run-summary extension content on per-run report panels
  - left/right `grcv3` extension content on comparison panels
- Recorded the representative lane and its explicit graph boundary in:
  - [Phase-V-GRCV3-RepresentativeVisualization.md](./Phase-V-GRCV3-RepresentativeVisualization.md)

### Verification

- [x] `GRCV3` behavior visuals are generated from saved artifacts only
- [x] Replay agreement is visible without reopening raw telemetry JSON

### Summary

Completed the first behavior-facing `GRCV3` visualization lane. The renderer
now consumes the saved `primary` / `replay` telemetry artifacts directly,
surfaces selected `grcv3` step-extension traces, and exposes run/comparison
family-extension summaries through saved report panels.

## Iteration 15. GRCV3 Behavior Visualization Closeout

### Goal

Close the first justified `GRCV3` visualization lane and record the remaining
graph-facing boundary.

### Checks

- [x] Run the representative `GRCV3` behavior visualization lane end-to-end
- [x] Record the behavior-facing outputs and what they make legible
- [x] Record explicitly that `GRCV3` graph visualization remains deferred
- [x] Link the deferred graph boundary back to the later Phase T graph
      telemetry extension plan

### Implementation Notes

- This closes the currently justified `GRCV3` Phase V work, not all future
  `GRCV3` visualization work.
- End-to-end validation is now covered through:
  - `tests.visualization.test_visualization`
  - the `GRCV3` representative visualization CLI path
- Concrete artifact-backed closeout lane executed:
  - `lane_name = "phase_v_iter15_closeout"`
  - primary run id:
    - `c1a316ae3353277f9f855f9fad503ab1360132d69209d9d02f20e7fb0ccc769c`
  - replay run id:
    - `44af789a13845c353d68af641b7fe02d2b5a2c8cd666323f727ce7f737f61cc8`
  - matching final snapshot digest:
    - `09364e2b22779d26185666d767a3dc54e512992301bc5a4f9ad53efc45594dd9`
- Verified saved Phase V outputs on disk:
  - `primary/.../visualization/trajectories.png`
  - `primary/.../visualization/events.png`
  - `primary/.../visualization/report_panel.png`
  - `replay/.../visualization/trajectories.png`
  - `replay/.../visualization/events.png`
  - `replay/.../visualization/report_panel.png`
  - `comparison/.../visualization/comparison_trajectories.png`
  - `comparison/.../visualization/comparison_panel.png`
- The remaining deferred boundary stays explicit:
  - current `GRCV3` behavior visualization is complete
  - later Phase T `GRCV3` checkpoint telemetry is still required before any
    graph-visible `GRCV3` rendering is attempted

### Verification

- [x] No unresolved blocker remains for behavior-facing `GRCV3` visualization
- [x] The remaining graph dependency is documented rather than implied

### Summary

Closed the currently justified `GRCV3` Phase V lane. Behavior-facing
visualization is now implemented and tested from saved artifacts. At the time
of this iteration, the graph-visible boundary still remained explicitly
deferred to later Phase T checkpoint telemetry work; that later checkpoint lane
and the final landscape graph lane have since been closed.

## Iteration 16. GRCV3 Actual Cell-Pair Closeout

### Goal

Move the `GRCV3` Phase V closeout from the replay-only bridge lane onto the
real seed-driven `cell-1` / `cell-4` artifact lane.

### Checks

- [x] Implement a seed-driven `GRCV3` landscape runner for real seed files
- [x] Add a telemetry-backed `cell-1` / `cell-4` `GRCV3` experiment helper
- [x] Add a behavior-only `cell-1` / `cell-4` `GRCV3` visualization helper
- [x] Add focused model, telemetry, and visualization tests for the real seed
      lane
- [x] Run the real `cell-1` / `cell-4` `GRCV3` telemetry lane end to end
- [x] Render the real `cell-1` / `cell-4` behavior visuals from saved artifacts
- [x] Update the Phase V documentation so the closeout evidence points to the
      real seed lane rather than only the replay bridge lane

### Implementation Notes

- Landed seed-driven `GRCV3` bridge:
  - `src/pygrc/models/grc_v3_landscape.py`
- Landed telemetry experiment helper:
  - `run_grcv3_landscape_experiment(...)`
- Landed behavior visualization helper:
  - `render_grcv3_landscape_visual_suite(...)`
- Landed CLI / script surfaces:
  - `scripts/run_grcv3_landscape_telemetry.py`
  - `src/pygrc/cli/grcv3_landscape_visuals.py`
- Concrete artifact-backed closeout lane executed:
  - `profile_name = "seed_baseline"`
  - `num_steps = 12`
  - cell-1 run id:
    - `958f1834b76a03eed800d9c055b35f41d2f087617f6e2fcacf7769329ecb1964`
  - cell-4 run id:
    - `4e9f456b7568dfd6080424607a6dbd0cb796d1a09cfaa0e4eafd8fcc8e5203ee`
- Saved visualization outputs verified on disk:
  - `cell-1/.../visualization/trajectories.png`
  - `cell-1/.../visualization/events.png`
  - `cell-1/.../visualization/report_panel.png`
  - `cell-4/.../visualization/trajectories.png`
  - `cell-4/.../visualization/events.png`
  - `cell-4/.../visualization/report_panel.png`
  - `comparison/.../visualization/comparison_trajectories.png`
  - `comparison/.../visualization/comparison_panel.png`
- The current real-seed closeout difference made visible from artifacts is:
  - `cell-1 final active_basin_count = 1`
  - `cell-4 final active_basin_count = 3`
  - comparison delta:
    - `active_basin_count_right_minus_left = 2`

### Verification

- [x] `./.venv/bin/python -m unittest tests.models.test_grc_v3_landscape_runtime`
- [x] `./.venv/bin/python -m unittest tests.telemetry.test_experiments`
- [x] `./.venv/bin/python -m unittest tests.visualization.test_visualization`
- [x] `./.venv/bin/python scripts/run_grcv3_landscape_telemetry.py --outputs-root outputs --profile seed_baseline --steps 12`
- [x] `./.venv/bin/python -m pygrc.cli.grcv3_landscape_visuals --telemetry-root outputs --profile seed_baseline --surface behavior`

### Summary

Iteration 16 moved the `GRCV3` Phase V closeout onto actual `cell-1` /
`cell-4` artifacts. The replay lane remains useful as a bridge and stability
check, but the authoritative behavior-facing evidence now comes from the real
seed-driven lane under `outputs/representative/grcv3_landscape/seed_baseline/`.

## Iteration 17. GRCV3 Graph Boundary Refresh

### Goal

Resync the Phase V boundary after Phase T landed checkpoint telemetry for the
representative `GRCV3` lane.

### Checks

- [x] Update the Phase V plan so it no longer describes all `GRCV3` graph
      visualization as blocked
- [x] Record that the representative `primary` / `replay` lane is now
      graph-capable when it was recorded with checkpoint export enabled
- [x] Record that the seed-driven `cell-1` / `cell-4` lane remains behavior-only
      until it has its own graph checkpoint telemetry
- [x] Add explicit follow-on iterations for representative graph rendering and
      its closeout evidence

### Implementation Notes

- This is the documentation boundary reset after Phase T iterations 20-23.
- The critical distinction is now:
  - representative `GRCV3`: behavior + optional graph surfaces
  - landscape `GRCV3`: behavior only
- Updated the Phase V plan so Workstream 10 names the new split honestly
  instead of treating the entire family as graph-blocked.

### Verification

- [x] Phase V now states the correct post-Phase-T `GRCV3` graph boundary
- [x] The remaining missing lane is named precisely as the seed-driven
      landscape checkpoint lane

### Summary

Iteration 17 corrected the Phase V family boundary after the representative
checkpoint telemetry landed. `GRCV3` is no longer globally graph-blocked, but
its graph capability is still lane-local rather than family-wide.

## Iteration 18. GRCV3 Representative Graph Surface

### Goal

Expose checkpoint-backed graph visualization for the representative
`primary` / `replay` `GRCV3` lane through the shared Phase V API and CLI
surface.

### Checks

- [x] Add a dedicated representative `GRCV3` graph rendering entrypoint
- [x] Extend the shared representative visualization API so
      `surface = "graph"` and `surface = "all"` work for the representative
      `GRCV3` lane
- [x] Preserve explicit failure when the representative lane was recorded
      without graph checkpoints
- [x] Keep the seed-driven landscape `GRCV3` lane explicitly graph-blocked
- [x] Update the representative and landscape CLIs so their supported surface
      behavior matches the real artifact boundary
- [x] Add focused visualization tests for:
  - [x] representative graph rendering with checkpoints
  - [x] representative graph failure without checkpoints
  - [x] representative graph CLI success
  - [x] representative graph CLI failure
  - [x] continued landscape graph failure

### Implementation Notes

- Landed representative graph entrypoint:
  - `render_grcv3_representative_graph_suite(...)`
- Extended representative visualization result surface:
  - `GRCV3RepresentativeVisualizationResult`
    - `primary_graph_visualization_layout`
    - `replay_graph_visualization_layout`
    - `graph_comparison_visualization_layout`
- Updated shared Phase V API:
  - `render_grcv3_representative_visual_suite(...)`
- Updated CLI surface:
  - `src/pygrc/cli/grcv3_representative_visuals.py`
  - `src/pygrc/cli/grcv3_landscape_visuals.py`
- At the end of Iteration 19, the landscape CLI accepted the shared surface
  vocabulary but still failed explicitly because that lane did not yet export
  graph checkpoints. Iterations 20-22 close that later landscape lane.

### Verification

- [x] `GRCV3` representative graph rendering now reuses the shared graph
      renderer rather than forking a family-local path
- [x] Graph requests fail only for missing checkpoint artifacts, not because of
      stale CLI/API hard blocks

### Summary

Iteration 18 unlocked checkpoint-backed representative graph visualization for
`GRCV3`. The representative lane now supports the same `behavior` /
`graph` / `all` surface vocabulary as the rest of Phase V, while the
seed-driven landscape lane remains explicitly blocked until its checkpoint
telemetry exists.

## Iteration 19. GRCV3 Representative Graph Closeout

### Goal

Close the currently justified `GRCV3` graph visualization slice with concrete
artifact-backed evidence from the representative lane.

### Checks

- [x] Run the representative `GRCV3` telemetry lane with graph checkpoint export
- [x] Render the representative `GRCV3` graph visualization surface end to end
- [x] Record the concrete output paths and artifact identity in the closeout doc
- [x] Update `ImplementationPhases.md` so the post-Phase-5 read reflects the
      new representative-graph milestone

### Implementation Notes

- This closeout is intentionally lane-local.
- It does **not** claim that the seed-driven `GRCV3` landscape lane is now
  graph-capable.
- Concrete artifact-backed representative graph lane executed:
  - `lane_name = "phase_v_iter19_graph"`
  - `num_steps = 3`
  - primary run id:
    - `e403cd0bf1b0f8808d8105914a2432dadb6d8929ec6aeabcfef2c27964131050`
  - replay run id:
    - `c68e00806f946ff0e45d7b917c51543b257b521d12683db49a77cd88a12a6159`
  - matching final snapshot digest:
    - `09364e2b22779d26185666d767a3dc54e512992301bc5a4f9ad53efc45594dd9`
- Saved visualization outputs verified on disk:
  - `primary/.../visualization/trajectories.png`
  - `primary/.../visualization/events.png`
  - `primary/.../visualization/report_panel.png`
  - `primary/.../visualization/graph_sequence.png`
  - `primary/.../visualization/graph_animation.gif`
  - `primary/.../visualization/graph_html/`
  - `primary/.../visualization/graph_layouts.json`
  - `replay/.../visualization/trajectories.png`
  - `replay/.../visualization/events.png`
  - `replay/.../visualization/report_panel.png`
  - `replay/.../visualization/graph_sequence.png`
  - `replay/.../visualization/graph_animation.gif`
  - `replay/.../visualization/graph_html/`
  - `replay/.../visualization/graph_layouts.json`
  - `comparison/.../visualization/comparison_trajectories.png`
  - `comparison/.../visualization/comparison_panel.png`
  - `comparison/.../visualization/graph_comparison.png`

### Verification

- [x] Representative graph visuals exist on disk under `outputs/`
- [x] Remaining landscape-lane graph deferral is still explicit

### Summary

Iteration 19 closed the currently justified `GRCV3` graph slice on actual saved
artifacts. The representative `primary` / `replay` lane now has concrete
behavior and graph visuals under `outputs/`, while the seed-driven landscape
lane remains explicitly deferred until it exports its own graph checkpoints.

## Iteration 20. GRCV3 Landscape Graph Boundary Refresh

### Goal

Record the remaining Phase V work needed after representative `GRCV3` graph
visualization is complete but before family-wide graph closeout can be claimed.

### Checks

- [x] Update the Phase V plan so it names the seed-driven landscape graph lane
      as the final `GRCV3` visualization gap
- [x] Record the intended landscape graph iteration order in this checklist
- [x] Link the remaining dependency back to the matching Phase T landscape
      checkpoint lane

### Implementation Notes

- This iteration exists to stop the project from informally treating
  representative graph closure as full-family graph closure.
- The remaining visualization gap is specifically:
  - `outputs/representative/grcv3_landscape/<profile>/cell-1/...`
  - `outputs/representative/grcv3_landscape/<profile>/cell-4/...`
  - checkpoint-backed graph snapshots/comparison/animation for that lane

### Verification

- [x] The remaining `GRCV3` graph-visualization gap is documented precisely
- [x] The next seed-driven landscape graph iterations are explicit

### Summary

Iteration 20 refreshed the Phase V boundary after the earlier representative
graph closeout. It recorded that the only remaining family-visible
`GRCV3` visualization gap was the seed-driven checkpoint-backed
`cell-1` / `cell-4` landscape graph lane, and it linked that dependency
explicitly to the landed Phase T landscape checkpoint telemetry work.

## Iteration 21. GRCV3 Landscape Graph Surface

### Goal

Expose checkpoint-backed graph visualization for the real seed-driven `GRCV3`
`cell-1` / `cell-4` lane through the shared Phase V API and CLI surface.

### Checks

- [x] Extend the seed-driven `GRCV3` visualization API so
      `surface = "graph"` and `surface = "all"` work once checkpoints exist
- [x] Render checkpoint-backed graph outputs for:
  - [x] `cell-1`
  - [x] `cell-4`
  - [x] pairwise comparison
- [x] Preserve explicit failure when the landscape lane was recorded without
      graph checkpoints
- [x] Add focused visualization tests for the seed-driven graph path

### Implementation Notes

- This should reuse the shared graph renderer and the existing landscape
  discovery/layout helpers rather than forking a family-local graph stack.
- The main change is enabling the landscape lane once Phase T has supplied the
  saved checkpoint artifacts.

### Verification

- [x] Seed-driven `GRCV3` landscape graph rendering is artifact-driven only
- [x] Graph requests fail only for missing checkpoint artifacts, not because of
      stale family-local hard blocks

### Summary

Iteration 21 enabled the seed-driven landscape graph surface end to end.
`render_grcv3_landscape_visual_suite(...)` now accepts `surface = "graph"` and
`surface = "all"` when the saved telemetry lane contains graph checkpoints,
and it still fails explicitly with a checkpoint-specific message when that
artifact prerequisite is missing. Focused tests now cover both the positive
artifact-backed path and the negative missing-checkpoint path.

## Iteration 22. GRCV3 Landscape Graph Closeout

### Goal

Close the remaining `GRCV3` graph-visible lane on actual seed-driven
`cell-1` / `cell-4` artifacts and record full telemetry-plus-visualization
closeout.

### Checks

- [x] Run the seed-driven `GRCV3` landscape telemetry lane with graph checkpoint
      export enabled
- [x] Render the seed-driven `GRCV3` graph visualization surface end to end
- [x] Record the concrete output paths and artifact identity in the closeout doc
- [x] Update `ImplementationPhases.md` so `GRCV3` is no longer described as
      having an open landscape graph lane

### Implementation Notes

- This is the final family-visible closeout slice for `GRCV3` telemetry plus
  visualization.
- It should still keep the richer `GRCL-v3` / projector questions separate from
  the narrower question of whether the seed-driven graph lane is wired through
  telemetry and visualization.

### Verification

- [x] Seed-driven `GRCV3` graph visuals exist on disk under `outputs/`
- [x] No unresolved telemetry/visualization blocker remains for `GRCV3`

### Summary

Iteration 22 closed the seed-driven `GRCV3` landscape graph lane on concrete
checkpoint-backed artifacts. The end-to-end command
`./.venv/bin/python -m pygrc.cli.grcv3_landscape_visuals --telemetry-root outputs --experiment-path representative/grcv3_landscape_checkpoint --profile seed_baseline --surface all`
completed successfully and produced:

- `cell-1` visualization root:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/cell-1/3f87fb9dbb4e3724d9c3c973b7885ac500bc89304af13eea4caf8e6fe138f823/visualization/`
- `cell-4` visualization root:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/cell-4/8046610fa18891bd036ffbcba29bf9e762186f4bcae4bfe34973c7cec75dc5a4/visualization/`
- pairwise comparison root:
  - `outputs/representative/grcv3_landscape_checkpoint/seed_baseline/comparison/3f87fb9dbb4e3724d9c3c973b7885ac500bc89304af13eea4caf8e6fe138f823__vs__8046610fa18891bd036ffbcba29bf9e762186f4bcae4bfe34973c7cec75dc5a4/visualization/`

Verified files now include, per run:

- `trajectories.png`
- `events.png`
- `report_panel.png`
- `graph_sequence.png`
- `graph_animation.gif`
- `graph_html/final_graph.html`
- `graph_layouts.json`
- `graph_snapshots/*.png`

and for the comparison lane:

- `comparison_trajectories.png`
- `comparison_panel.png`
- `graph_comparison.png`

With Iteration 22 closed, `GRCV3` no longer has any open telemetry or
visualization blocker. The remaining open `GRCV3` work is semantic and
projector-side rather than telemetry/visualization-side.

Post-closeout renderer refinement also landed afterward:

- edge activity is no longer effectively color-only
- graph rendering now separates:
  - structural conductance as the background edge layer
  - realized signed flow as the directed overlay layer
- static checkpoint figures now show arrows when signed edge flux exists
- edge width now responds to flow magnitude instead of only conductance
- final HTML graph output is directed when checkpoint flow data is present
- inactive collapsed nodes now fade visually, collapse targets are highlighted,
  and dashed collapse links show `from -> into` explicitly
- if a node later re-enters a live choice regime, current choice styling
  overrides stale collapse styling so the node becomes visually active again

Verification for that refinement:

- `./.venv/bin/python -m unittest tests.visualization.test_visualization`
  passed with the new renderer semantics

Supplementary artifact record:

- the family-native rich lane was rerun through the refined renderer:
  - `./.venv/bin/python scripts/run_grcv3_rich_fulltest.py`
- artifact root:
  - `outputs/grcv3-rich-fulltest/grcv3-rich/seed_baseline/grcv3-rich-basin-boundary-channel-probe/bdbf3d42b68cbb43795b390e4ab84386804c49d0a1afd06d171868ae7da2de8e/visualization/`
- the dedicated collapse-example lane was also rerun so the collapse-specific
  overlays are evidenced on a trajectory with early collapse:
  - `outputs/grcv3-rich-collapse-example-100/grcv3-rich/hot_exploratory/grcv3-rich-collapse-example/365e4feb0f57492e9814d8dc79d47ba626ba8bbb2801a5c20f765fbd4b8a5df0/visualization/`

## Iteration 23. GRC9 Visualization Boundary And Representation

### Goal

Extend the existing Phase V plan/checklist for GRC9 and add a family-specific
GRC9 visualization representation note, following the structure used for the
GRCV3 representation document. The boundary is generic renderer capability
first, not a specific canonical run.

### Checks

- [x] Reuse `Phase-V-ImplementationPlan.md` as the shared Phase V plan
- [x] Reuse `Phase-V-ImplementationChecklist.md` as the shared Phase V checklist
- [x] Add GRC9 as a Phase V family-specific visualization workstream
- [x] Add `Phase-V-GRC9-RepresentativeVisualization.md`
- [x] Identify Phase T-GRC9 representative input lane as a smoke/evidence
      fixture
- [x] Identify Phase T-GRC9 seed-driven landscape input lane as a smoke/evidence
      fixture, not a native GRC9 source structure
- [x] Identify diagnostic probe as a later panel surface
- [x] Separate behavior visuals from graph/checkpoint visuals
- [x] Record that structure discovery is downstream GRC9 work, not a Phase V
      implementation iteration
- [x] Record that GRCL-9 translation is downstream GRC9 work, not a Phase V
      implementation iteration
- [x] Record original graph blocker: GRC9 experiment lanes did not yet expose
      checkpoint capture controls
- [x] Preserve explicit non-claims:
  - [x] no GRCV3 hierarchy / choice / collapse semantics
  - [x] no GRCL-9 lowering claim
  - [x] no Lorentzian causal-layer visualization
  - [x] no observer-local visualization before observer telemetry exists
  - [x] no boundary barrier/ghost runtime visualization

### Implementation Notes

- This iteration intentionally changes documentation only.
- The standalone GRC9 visualization plan/checklist draft was collapsed into the
  shared Phase V plan/checklist structure to avoid two competing planning
  surfaces.
- GRC9-specific visual representation belongs in the family note, not in a
  separate Phase V implementation plan.
- Current representative and `cell-1` / `cell-4` GRC9 lanes may be used to
  exercise the renderer, but the renderer must not treat them as canonical
  scientific GRC9 structures.

### Verification

- [x] Shared Phase V plan names the GRC9 workstream
- [x] Shared Phase V checklist records the GRC9 visualization sequence
- [x] GRC9 representation note records generic renderer boundary, example lanes,
      graph boundary, downstream handoff, and non-claims

### Summary

Planning structure updated. Phase V remains the single visualization phase.
GRC9 now enters as a generic artifact-driven visualization capability.
Structure discovery and GRCL-9 translation are recorded only as downstream
GRC9 handoff items, not Phase V implementation iterations.

## Iteration 24. GRC9 Behavior Visual Constants

### Goal

Add GRC9-specific observable lists for behavior trajectory and comparison
figures.

### Checks

- [x] Add `DEFAULT_GRC9_RUN_OBSERVABLES`
- [x] Add `DEFAULT_GRC9_COMPARISON_OBSERVABLES`
- [x] Include port-chart metrics
- [x] Include row-tensor metrics
- [x] Include column diagnostic metrics
- [x] Include transport metrics
- [x] Include identity/abundance metrics
- [x] Include coarse-graining metrics
- [x] Include budget-correction metrics
- [x] Export constants from `pygrc.visualization`

### Verification

- [x] Unit test `_trajectory_series` for at least one GRC9 family-extension path
- [x] Unit test that GRC9 observable constants are exported

### Summary

Implemented. GRC9 behavior and comparison observable constants now live in the
shared visualization renderer and are exported from `pygrc.visualization`.
The renderer also supports a virtual `.length` path segment so list/map-backed
GRC9 telemetry such as `coarse_fields_list` can be used as numeric trajectory
series without changing the telemetry contract.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9_observable_constants_are_exported tests.visualization.test_visualization.VisualizationTest.test_grc9_extension_trajectory_series_are_available`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization`

## Iteration 25. GRC9 Representative Visual Suite

### Goal

Add a generic paired-run GRC9 visual suite. The Phase T-GRC9 representative
`primary` / `replay` lane is the first smoke fixture, not a scientific closeout
target.

### Checks

- [x] Add `GRC9RepresentativeVisualizationResult`
- [x] Add `render_grc9_representative_visual_suite`
- [x] Discover `primary` and `replay` run artifact directories
- [x] Load saved telemetry artifact packs
- [x] Render primary behavior files
- [x] Render replay behavior files
- [x] Render comparison trajectories and panel
- [x] Add checkpoint-backed representative graph suite
- [x] Render primary/replay graph sequence, final HTML, and animation files
- [x] Render graph comparison panel
- [x] Default lane is `phase_t_grc9_iter6_representative`
- [x] Keep lane selection configurable
- [x] Avoid hard-coding representative-lane scientific interpretation
- [x] Do not require graph checkpoints for behavior rendering
- [x] Require saved graph checkpoints for graph rendering
- [x] Export public functions and result dataclasses

### Verification

- [x] Test representative suite writes expected behavior files
- [x] Test report panel includes `grc9` family extensions
- [x] Test comparison panel includes left/right `grc9` extensions
- [x] Test graph surface reports checkpoint requirement without checkpoints
- [x] Test graph surface writes expected graph files with checkpoint artifacts

### Summary

Implemented. The representative GRC9 visual suite now renders behavior
trajectories, event timelines, and report panels for the Phase T-GRC9
`primary` / `replay` lane using the GRC9 observable defaults. With opt-in GRC9
checkpoint artifacts available, the same suite now renders checkpoint-backed
`port_graph` sequence, animation, final HTML, and graph-comparison outputs.
Behavior rendering does not require checkpoints; graph rendering requires
rerunning the source telemetry lane with `record_graph_checkpoints=True`.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9_report_lines_include_family_extensions tests.visualization.test_visualization.VisualizationTest.test_grc9_comparison_report_lines_include_family_extensions tests.visualization.test_visualization.VisualizationTest.test_render_grc9_representative_visual_suite_writes_behavior_outputs tests.visualization.test_visualization.VisualizationTest.test_render_grc9_representative_visual_suite_rejects_graph_surface`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_render_grc9_representative_visual_suite_writes_graph_outputs`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization`

## Iteration 26. GRC9 Seed-Driven Landscape Visual Suite

### Goal

Add a generic two-run GRC9 landscape visual suite. The Phase T-GRC9 `cell-1` /
`cell-4` lane is a structurally grafted smoke fixture, not a native GRCL-9
source structure or canonical GRC9 motif lane.

### Checks

- [x] Add `GRC9LandscapeVisualizationResult`
- [x] Add `render_grc9_landscape_visual_suite`
- [x] Discover `cell-1` and `cell-4` run artifact directories
- [x] Load saved telemetry artifact packs
- [x] Render cell-1 behavior files
- [x] Render cell-4 behavior files
- [x] Render comparison trajectories and panel
- [x] Add checkpoint-backed seed-driven landscape graph suite
- [x] Render cell-1/cell-4 graph sequence, final HTML, and animation files
- [x] Render graph comparison panel
- [x] Default profile is `phase_t_grc9_iter7_seed`
- [x] Preserve `source_lowering_mode = structural_graph_graft_v1` as bridge
      metadata only
- [x] Avoid describing `cell-1` / `cell-4` as native GRC9 structures
- [x] Require saved graph checkpoints for graph rendering
- [x] Export public functions and result dataclasses

### Verification

- [x] Test landscape suite writes expected behavior files
- [x] Test report panel includes `grc9` family extensions
- [x] Test comparison panel includes left/right `grc9` extensions
- [x] Test no GRCL-9 lowering claim appears in visualization-specific labels
- [x] Test graph surface reports checkpoint requirement without checkpoints
- [x] Test graph surface writes expected graph files with checkpoint artifacts

### Summary

Implemented. The seed-driven GRC9 landscape visual suite now renders behavior
trajectories, event timelines, and report panels for the Phase T-GRC9
`cell-1` / `cell-4` structural graft lane using the GRC9 observable defaults.
When the source lane was run with `record_graph_checkpoints=True`, the same
suite renders checkpoint-backed `port_graph` sequence, animation, final HTML,
and graph-comparison outputs. The lane preserves
`source_lowering_mode = structural_graph_graft_v1` as bridge metadata and does
not label the grafted seeds as native GRCL-9 structures.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9_landscape_report_lines_include_family_extensions tests.visualization.test_visualization.VisualizationTest.test_grc9_landscape_comparison_report_lines_include_family_extensions tests.visualization.test_visualization.VisualizationTest.test_render_grc9_landscape_visual_suite_writes_behavior_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9_landscape_visual_labels_do_not_claim_grcl9_lowering tests.visualization.test_visualization.VisualizationTest.test_render_grc9_landscape_visual_suite_rejects_graph_surface_without_checkpoints tests.visualization.test_visualization.VisualizationTest.test_render_grc9_landscape_visual_suite_writes_graph_outputs`

## Iteration 27. GRC9 CLI Wrappers

### Goal

Expose Phase V-GRC9 behavior and checkpoint-backed graph rendering through CLI
wrappers parallel to GRCV3.

### Checks

- [x] Add `src/pygrc/cli/grc9_representative_visuals.py`
- [x] Add `src/pygrc/cli/grc9_landscape_visuals.py`
- [x] Support `--telemetry-root`
- [x] Support `--experiment-path`
- [x] Support `--visualization-root`
- [x] Support `--lane-name` for representative visuals
- [x] Support `--profile` for landscape visuals
- [x] Support `--surface behavior`
- [x] Accept `--surface graph` and fail clearly when graph checkpoints are absent
- [x] Print output directories consistently with GRCV3 CLI wrappers

### Verification

- [x] Test representative CLI writes behavior outputs
- [x] Test representative CLI writes graph outputs
- [x] Test landscape CLI writes behavior outputs
- [x] Test landscape CLI writes graph outputs
- [x] Test graph CLI path reports checkpoint requirement when artifacts lack
      checkpoints

### Summary

Implemented. GRC9 representative and seed-driven landscape visual wrappers now
render saved Phase T-GRC9 artifacts from the command line. Both wrappers accept
telemetry root, experiment path, visualization root, lane/profile selectors, and
`--surface behavior|graph|all`. Behavior surfaces work without graph
checkpoints; graph surfaces render when checkpoint artifacts exist and report
the `record_graph_checkpoints=True` requirement when they do not.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9_representative_visuals_cli_writes_behavior_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9_representative_visuals_cli_writes_graph_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9_representative_visuals_cli_rejects_graph_surface_without_checkpoints tests.visualization.test_visualization.VisualizationTest.test_grc9_landscape_visuals_cli_writes_behavior_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9_landscape_visuals_cli_writes_graph_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9_landscape_visuals_cli_rejects_graph_surface_without_checkpoints`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization`

## Downstream GRC9 Handoff

Structure discovery and GRCL-9 translation are intentionally not Phase V
iterations.

After generic GRC9 visualization exists, downstream GRC9 work can use it to
inspect saved Phase T-GRC9 artifacts and identify spark, expansion, growth,
column-regime, coarse-graining, budget, and fission-diagnostic motifs. That
work should produce its own plan/checklist or manifest contract outside this
Phase V checklist.

GRCL-9 translation planning should start only after structure discovery
identifies GRC9-native motifs worth producing intentionally from source-level
structures. That planning belongs to a later GRCL-9 phase, not to Phase V.

Collapse-adjacent GRCL-9 probes are the next planned downstream batch after
the current Phase V GRC9 suite. The existing GRC9 visual suite may reuse the
GRCV3 transparent-source/arrow/target visual grammar only for labeled,
selector-backed `collapse_adjacent_structural_probe` overlays.

Phase V-GRC9 collapse-adjacent review:

- [x] Create `implementation/Phase-V-GRC9-CollapseAdjacentVisualizationReview.md`
- [x] Accept manifest-driven structural visualization over existing behavior
      plots, graph checkpoints, and GRCL-9 provenance
- [x] Keep unqualified GRCV3 collapse links and collapsed-node status out of
      GRC9
- [x] Reuse transparent marked source nodes and dashed arrows only for
      selector-backed collapse-adjacent structural probes
- [x] Require upstream selector/report evidence before showing
      collapse-adjacent labels
- [x] Defer automatic basin-merge, sink-loss, support-loss, and collapse-event
      overlays until a future Phase T-GRC9 contract defines compact evidence

If Phase T-GRC9 later accepts diagnostic-only structural-collapse fields, a
later visualization pass may add automatic overlays for basin merge candidates,
sink-status loss, membrane/ridge rupture, support loss, or failed fission
persistence using only saved telemetry/checkpoint evidence.

## Iteration 28. GRC9V3 Visualization Boundary And Representation

### Goal

Extend the existing Phase V plan/checklist for `GRC9V3` without creating a
separate Phase V sub-plan. The boundary is representative artifact-driven
renderer capability over Phase T-GRC9V3 telemetry and checkpoints.

### Checks

- [x] Reuse `Phase-V-ImplementationPlan.md` as the shared Phase V plan
- [x] Reuse `Phase-V-ImplementationChecklist.md` as the shared Phase V
      checklist
- [x] Add GRC9V3 as a Phase V family-specific visualization workstream
- [x] Keep the GRC9V3 representative visualization meaning inside the shared
      Phase V plan/checklist rather than adding a special file
- [x] Identify Phase T-GRC9V3 Appendix E representative telemetry as the first
      input artifact lane
- [x] Identify saved graph checkpoints and `family_extensions["grc9v3"]`
      overlays as the only graph-visualization source
- [x] Separate behavior, event, run-summary, and graph surfaces
- [x] Record ownership boundaries:
  - [x] `grc9_mechanical`
  - [x] `grcv3_semantic`
  - [x] `grc9v3_hybrid`
  - [x] `shared_runtime`
- [x] Record explicit non-claims:
  - [x] no GRC9V3 phenomenology discovery claim
  - [x] no GRCL/source lowering claim
  - [x] no Lorentzian causal-layer visualization
  - [x] no observer-local visualization before observer telemetry exists
  - [x] no boundary barrier/ghost runtime visualization
  - [x] no adiabatic expansion visualization

### Implementation Notes

- This iteration intentionally changes documentation only.
- GRC9V3 follows the same shared Phase V structure used by GRC9: a common plan
  and checklist with family-specific representation text.
- The first visualization target is the Phase T-GRC9V3
  `appendix_e_cell_division` artifact pack. It is representative runtime
  evidence, not source-language evidence.
- GRC9V3 visualizations should show hybrid interaction explicitly rather than
  flattening the lane into either GRC9 mechanics or GRCV3 semantics alone.

### Verification

- [x] Shared Phase V plan names the GRC9V3 workstream
- [x] Shared Phase V checklist records the GRC9V3 visualization sequence
- [x] GRC9V3 representation text records behavior, event, run-summary, graph,
      overlay, and non-claim boundaries

### Summary

Planning structure updated. Phase V remains the single visualization phase.
GRC9V3 now enters as an artifact-driven representative visualization
capability over saved Phase T-GRC9V3 telemetry and graph checkpoints.

## Iteration 29. GRC9V3 Behavior Visual Constants

### Goal

Add GRC9V3-specific observable lists for behavior trajectory and report-panel
figures.

### Checks

- [x] Add `DEFAULT_GRC9V3_RUN_OBSERVABLES`
- [x] Defer `DEFAULT_GRC9V3_COMPARISON_OBSERVABLES` until a paired lane
      exists
- [x] Include port-chart metrics
- [x] Include row-basis differential metrics
- [x] Include hybrid-tensor metrics
- [x] Include transport metrics
- [x] Include identity/basin metrics
- [x] Include hierarchy metrics
- [x] Include hybrid-spark metrics
- [x] Include choice/collapse metrics
- [x] Include budget-correction metrics
- [x] Export constants from `pygrc.visualization`

### Verification

- [x] Unit test `_trajectory_series` for at least one GRC9V3
      family-extension path
- [x] Unit test that GRC9V3 observable constants are exported
- [x] Unit test that missing optional GRC9V3 fields do not crash the behavior
      renderer

### Summary

Implemented. GRC9V3 behavior observable constants now live in the shared
visualization renderer and are exported from `pygrc.visualization`.
The first observable set targets the representative single-lane Appendix E
artifact surface. Pairwise comparison constants are intentionally deferred
until a real paired GRC9V3 lane exists.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9v3_observable_constants_are_exported tests.visualization.test_visualization.VisualizationTest.test_grc9v3_extension_trajectory_series_are_available tests.visualization.test_visualization.VisualizationTest.test_grc9v3_missing_optional_fields_do_not_crash_behavior_renderer`

## Iteration 30. GRC9V3 Representative Visual Suite

### Goal

Add a representative GRC9V3 visual suite over the Phase T-GRC9V3 Appendix E
cell-division lane.

### Checks

- [x] Add `GRC9V3RepresentativeVisualizationResult`
- [x] Add `render_grc9v3_representative_visual_suite`
- [x] Discover the latest saved `appendix_e_cell_division` artifact pack unless
      an explicit artifact path is supplied
- [x] Load saved telemetry artifact packs
- [x] Render behavior trajectories
- [x] Render event timeline
- [x] Render report panel
- [x] Include replay flags and digest-match status in the report panel
- [x] Include Appendix E summary fields when present
- [x] Keep representative-lane interpretation configurable
- [x] Export public function and result dataclass

### Verification

- [x] Test representative suite writes expected behavior files
- [x] Test report panel includes `grc9v3` family extensions
- [x] Test report panel includes replay/digest flags from the saved experiment
      report
- [x] Test Appendix E summary fields appear when present
- [x] Test behavior rendering does not require graph checkpoints

### Summary

Implemented. The GRC9V3 representative visual suite now renders the saved
Phase T-GRC9V3 Appendix E artifact lane as a single-run behavior surface. It
discovers the latest saved fixture run by default, accepts an explicit
artifact path for reproducibility, renders trajectories/events/report panels
from saved telemetry only, and merges the saved experiment report with the
GRC9V3 run-summary extension so Appendix E and replay/digest fields are visible
in the report panel.

Graph/all surfaces intentionally fail with a Phase V iteration 31 message
until checkpoint graph rendering is implemented.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_render_grc9v3_representative_visual_suite_writes_behavior_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9v3_report_panel_includes_family_replay_and_appendix_e_fields tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visual_suite_accepts_explicit_artifact_path tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visual_suite_rejects_graph_surface_until_iteration_31`

## Iteration 31. GRC9V3 Checkpoint Graph Visual Suite

### Goal

Add checkpoint-backed graph rendering for GRC9V3 representative artifacts using
the saved `port_graph` checkpoints and GRC9V3 overlays.

### Checks

- [x] Render graph snapshots from saved checkpoint index
- [x] Render graph sequence panels
- [x] Render final interactive HTML graph view
- [x] Render animation files when checkpoint cadence is present
- [x] Use `node_overlay` for coherence, differential, identity, hierarchy,
      module, and choice markers
- [x] Use `port_overlay` for occupied/free ports and saturation
- [x] Use `edge_overlay` for conductance and flux summaries
- [x] Use `module_overlay` for expansion module and daughter sink highlights
- [x] Use `choice_overlay` for choice/collapse source and target highlights
- [x] Fail clearly when checkpoint artifacts are absent
- [x] Fail clearly when required overlay families are absent

### Verification

- [x] Test graph surface reports checkpoint requirement without checkpoints
- [x] Test graph surface writes expected graph files with checkpoint artifacts
- [x] Test graph surface reads GRC9V3 overlay payloads from checkpoint family
      extensions
- [x] Test graph surface does not infer overlays from live runtime state

### Summary

Implemented. The GRC9V3 representative graph suite now renders saved
checkpoint-backed `port_graph` artifacts for the Appendix E lane. Graph
surfaces require saved checkpoints and enabled GRC9V3 checkpoint overlays
(`node_overlay`, `port_overlay`, `edge_overlay`, `module_overlay`, and
`choice_overlay`) before rendering. The representative visual suite now
supports `surface_mode="graph"` and `surface_mode="all"`.

The generic graph renderer was also updated to recognize the GRC9V3
`signed_flux_source_to_target` edge field so port-graph flux direction can be
shown without live runtime access.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visual_suite_rejects_graph_surface_without_checkpoints tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visual_suite_writes_graph_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visual_suite_rejects_disabled_overlays tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visual_suite_all_writes_behavior_and_graph_outputs`

## Iteration 32. GRC9V3 CLI Wrapper

### Goal

Expose Phase V-GRC9V3 behavior and checkpoint-backed graph rendering through a
CLI wrapper parallel to the GRC9 and GRCV3 wrappers.

### Checks

- [x] Add `src/pygrc/cli/grc9v3_representative_visuals.py`
- [x] Support `--telemetry-root`
- [x] Support `--experiment-path`
- [x] Support `--visualization-root`
- [x] Support `--fixture-name`
- [x] Support `--artifact-path`
- [x] Support `--surface behavior`
- [x] Support `--surface graph`
- [x] Support `--surface all`
- [x] Print output directories consistently with existing Phase V CLI wrappers
- [x] Report missing checkpoint artifacts clearly for graph/all surfaces

### Verification

- [x] Test CLI writes behavior outputs
- [x] Test CLI writes graph outputs
- [x] Test CLI rejects graph surface without checkpoint artifacts
- [x] Test CLI can target an explicit artifact pack path

### Summary

Implemented. The GRC9V3 representative visual wrapper now exposes the
artifact-backed Appendix E behavior and graph surfaces from the command line.
It supports fixture discovery and explicit artifact-pack targeting through
`--artifact-path`, so repeatable records can pin a specific telemetry run
directory.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visuals_cli_writes_behavior_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visuals_cli_writes_graph_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visuals_cli_rejects_graph_surface_without_checkpoints tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visuals_cli_accepts_explicit_artifact_path`

## Iteration 33. GRC9V3 Visualization Closeout

### Goal

Record the completed Phase V-GRC9V3 visual evidence and close the
representative visualization slice.

### Checks

- [x] Generate representative behavior visuals from saved Phase T-GRC9V3
      artifacts
- [x] Generate representative graph visuals from saved checkpoints
- [x] Record output paths
- [x] Record command lines needed to reproduce each visual artifact
- [x] Record source telemetry artifact path and digest
- [x] Record which overlay families were used
- [x] Update this checklist with verification commands
- [x] Update `ImplementationPhases.md` to note Phase V-GRC9V3 closeout status

### Verification

- [x] Run the GRC9V3 visualization unit tests
- [x] Run the representative CLI on the saved Appendix E artifact pack
- [x] Verify behavior, event, report, graph, and animation outputs exist
- [x] Verify generated visuals are deterministic across repeated CLI runs

### Artifact Record

Source telemetry artifact:

- `outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98/`

Source run details:

- run id:
  - `2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98`
- fixture:
  - `appendix_e_cell_division`
- final snapshot digest:
  - `8e596eba7c37d1dc6465768c2ff10139ec12e8ebfec51f34aecbfafd8018cdfb`
- replay checks:
  - `replay_step_rows_match = true`
  - `replay_event_rows_match = true`
  - `replay_digest_match = true`
- checkpoint count:
  - `4`
- checkpoint cadence:
  - `initial+every_step`

Generated visualization outputs:

- `visualization/trajectories.png`
- `visualization/events.png`
- `visualization/report_panel.png`
- `visualization/graph_sequence.png`
- `visualization/graph_animation.gif`
- `visualization/graph_layouts.json`
- `visualization/graph_html/final_graph.html`
- `visualization/graph_snapshots/step-000000--time-00000.0000--initial.png`
- `visualization/graph_snapshots/step-000001--time-00000.0500--post_step.png`
- `visualization/graph_snapshots/step-000002--time-00000.1000--post_step.png`
- `visualization/graph_snapshots/step-000003--time-00000.1500--final.png`

Checkpoint overlay families used:

- `node_overlay`
- `port_overlay`
- `edge_overlay`
- `module_overlay`
- `choice_overlay`

Reproduction command:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.cli.grc9v3_representative_visuals \
  --artifact-path outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98 \
  --surface all
```

Determinism check:

```bash
find outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98/visualization -type f -print0 | sort -z | xargs -0 sha256sum > /tmp/grc9v3_visual_hashes_before.txt
PYTHONPATH=src ./.venv/bin/python -m pygrc.cli.grc9v3_representative_visuals --artifact-path outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98 --surface all
find outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98/visualization -type f -print0 | sort -z | xargs -0 sha256sum > /tmp/grc9v3_visual_hashes_after.txt
diff -u /tmp/grc9v3_visual_hashes_before.txt /tmp/grc9v3_visual_hashes_after.txt
```

The diff was empty.

### Summary

Implemented. Phase V-GRC9V3 now has behavior, event, report-panel, checkpoint
graph sequence, graph snapshot, final HTML, and animation outputs over the
real Phase T-GRC9V3 Appendix E artifact pack. The visual report builder also
normalizes the custom Phase T-GRC9V3 replay report into the standard Phase V
report-panel shape while preserving replay/digest and Appendix E fields.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization.VisualizationTest.test_grc9v3_report_panel_includes_family_replay_and_appendix_e_fields tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visuals_cli_writes_behavior_outputs tests.visualization.test_visualization.VisualizationTest.test_grc9v3_representative_visuals_cli_writes_graph_outputs`
- `PYTHONPATH=src ./.venv/bin/python -m pygrc.cli.grc9v3_representative_visuals --artifact-path outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98 --surface all`

## Iteration 34. GRC9V3 Lane B Visual Catch-Up

### Goal

Make the existing GRC9V3 visual surfaces Lane B-aware now that core
`GRC9V3` supports the opt-in `grc9v3_column_h_assisted` spark lane.

This is an interpretability pass. Lane B graph animation is already
structurally valid because Lane B reuses the existing
`hybrid_spark_candidate` and mechanical-expansion lifecycle. This iteration
should make the spark cause visually legible.

### Checks

- [x] Add Lane B observables to `DEFAULT_GRC9V3_RUN_OBSERVABLES` where numeric:
  - `family_extensions.grc9v3.hybrid_spark_state.last_candidate_min_abs_column_h`
  - `family_extensions.grc9v3.hybrid_spark_state.last_candidate_column_h_branch_hit`
- [x] Keep `last_candidate_spark_lane` as report/timeline metadata rather than
      a numeric trajectory series.
- [x] Update event timeline/report rendering so `hybrid_spark_candidate`
      events can distinguish:
  - Lane A `current_hybrid_signed_hessian` candidates;
  - Lane B signed-Hessian-only candidates;
  - Lane B column-H threshold/sign-crossing branch candidates.
- [x] Use candidate payload fields rather than event kind alone:
  - `spark_lane`;
  - `column_h_branch_hit`;
  - `gate_reasons`.
- [x] Add graph/checkpoint visual labeling or styling for nodes where:
  - `node_overlay.column_h_branch_hit == true`.
- [x] Preserve Lane A visual backward compatibility when Lane B fields are
      absent.
- [x] Document that Lane B direct evidence means direct runtime evidence that
      the column-H proxy branch fired; `H_s[b]` remains a proxy.

### Verification

- [x] Add visualization tests for Lane B optional fields in behavior rendering.
- [x] Add visualization tests for Lane B candidate labels in event/report
      rendering.
- [x] Add graph/checkpoint tests for `node_overlay.column_h_branch_hit` visual
      labeling or styling.
- [x] Re-run GRC9V3 representative visualization tests.

### Summary

Implemented. GRC9V3 behavior visuals now include Lane B column-H numeric
observables, event/report rendering can distinguish Lane A, Lane B
signed-Hessian-only, and Lane B column-H proxy-branch candidate causes from
saved candidate payload fields, and checkpoint-backed graph rendering labels
column-H proxy-branch nodes with a green border and `H` node-label suffix when
`node_overlay.column_h_branch_hit == true`.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization`
- `PYTHONPATH=src ./.venv/bin/ruff check src/pygrc/visualization/render.py src/pygrc/visualization/representative.py src/pygrc/visualization/graph_render.py tests/visualization/test_visualization.py`
