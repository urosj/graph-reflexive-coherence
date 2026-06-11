# Phase V Implementation Plan

This document is the detailed execution plan for **Phase V: Visualization
Surfaces**.

Phase V begins only after Phase T has made runs experimentally legible through
telemetry, summaries, reports, and deterministic artifact layout. Visualization
must therefore remain downstream of those artifacts. It is not a license to
re-open live model internals or to invent a second evidence layer.

At this point Phase V must be read with a family-specific boundary:

- `GRCV2` already has both behavior-facing and graph-facing visualization lanes
- `GRCV3` now has a checkpoint-backed representative graph lane in addition to
  its behavior-facing lanes
- `GRCV3` now also has a checkpoint-backed seed-driven landscape graph lane on
  saved `cell-1` / `cell-4` artifacts
- `GRC9` now has Phase T paper-facing telemetry plus generic artifact-driven
  behavior, graph, and CLI visualization capability for representative and
  seed-driven smoke lanes; no specific run is treated as scientifically
  canonical

The immediate motivation is now concrete rather than abstract. The existing
`GRCV2` representative runs already show behavior that needs to be seen, not
just read:

- `cell-1` stays small and effectively settles,
- `cell-4` exhibits delayed growth with births beginning around step `35` and
  continuing into the late run,
- budget remains conserved across the full trajectory,
- and topology-related observables (`num_nodes`, `num_edges`, `sink_count`) now
  move enough to justify graph-facing visual treatment.

`GRCV3` now adds two distinct graph-readiness tiers:

- representative `primary` versus `replay` telemetry artifacts already exist
- the saved representative lane now also has checkpoint-backed graph artifacts
  when it was recorded with graph checkpoint export enabled
- the saved seed-driven `cell-1` / `cell-4` lane now also has checkpoint-backed
  graph artifacts under `outputs/representative/grcv3_landscape_checkpoint/`
- so both representative and seed-driven graph questions can now be rendered
  from saved artifacts

## Inputs

Phase V assumes the following remain authoritative:

- [`Phase-T-ImplementationPlan.md`](./Phase-T-ImplementationPlan.md)
- [`Phase-T-ImplementationChecklist.md`](./Phase-T-ImplementationChecklist.md)
- [`Phase-T-GRCV3-Closeout.md`](./Phase-T-GRCV3-Closeout.md)
- [`Phase-T-GRC9-Closeout.md`](./Phase-T-GRC9-Closeout.md)
- [`Phase-T-GRC9-TelemetryContract.md`](./Phase-T-GRC9-TelemetryContract.md)
- [`Phase-V-Handoff.md`](./Phase-V-Handoff.md)
- the saved representative telemetry lane under:
  - `outputs/experiments/grcv2/representative/`
  - `outputs/representative/grcv3/`
  - `outputs/representative/grc9/`
  - `outputs/representative/grc9_landscape/`

## Purpose

Phase V must make saved experiment evidence legible through deterministic,
artifact-driven visuals.

The first visualization layer should answer questions like:

- how observables evolve over time,
- when events happen and whether they cluster,
- whether a run is quiescent, expanding, or structurally reorganizing,
- how two runs differ in timing and scale,
- how graph structure changes over time from saved checkpoints,
- how flow-facing overlays behave when they were actually exported,
- and how dense checkpoint lanes evolve when rendered as animations rather than
  isolated frames.

For `GRCV3`, those questions now split by lane:

- the representative `primary` / `replay` lane can answer both behavior-facing
  and checkpoint-backed graph questions from saved artifacts
- the seed-driven `cell-1` / `cell-4` lane can now also answer checkpoint-
  backed graph questions from saved artifacts

For `GRC9`, those questions now split by the Phase T smoke/evidence lanes:

- the representative `primary` / `replay` lane can answer behavior-facing and
  checkpoint-backed `port_graph` questions from saved artifacts
- the seed-driven `cell-1` / `cell-4` structural graft lane can answer
  behavior-facing and checkpoint-backed `port_graph` questions from saved
  artifacts
- both lanes can be rendered through importable CLI wrappers without reopening
  live model state

## Critical Boundary

Phase V must still separate **what is already renderable from saved artifacts**
from **what would require new artifact support**, but that boundary is now
family-specific.

For `GRCV2`, the implementation sequence is now:

- scalar/report visualization from Phase T artifacts,
- checkpoint-backed graph visualization from the landed topology/flow bridge,
- and only after that, denser or more specialized graph/flow surfaces that
  would need additional export scope.

For `GRCV3`, the implementation sequence should now be:

- scalar/report visualization from the landed behavior-facing lanes,
- checkpoint-backed representative graph visualization from the landed Phase T
  representative checkpoint lane,
- checkpoint-backed seed-driven landscape graph visualization from the landed
  Phase T landscape checkpoint lane,
- and only after that, denser or more specialized graph/flow surfaces.

For `GRC9`, the implementation sequence is now:

- GRC9-specific behavior observable constants from `family_extensions["grc9"]`,
- checkpoint-backed representative graph visualization from saved Phase T
  representative `port_graph` checkpoints,
- checkpoint-backed seed-driven landscape graph visualization from saved Phase
  T structural graft `port_graph` checkpoints,
- CLI wrappers for representative and seed-driven visual suites,
- and only after that, structure discovery and GRCL-9 translation work outside
  Phase V.

The downstream discovery track is documented in
[`GRC9-PhenomenologyDiscovery-Plan.md`](./GRC9-PhenomenologyDiscovery-Plan.md).

The representative visualization CLI should expose that split honestly for each
family:

- `behavior` renders scalar/report outputs only,
- `graph` renders checkpoint-backed graph outputs only,
- `all` renders both,
- and graph-facing requests fail explicitly only when the saved telemetry lane
  does not actually contain graph checkpoints.

### Already Supported By Current Phase T Artifacts

For `GRCV2`:

- scalar trajectory plots from `steps.jsonl`
- event timelines from `events.jsonl`
- run-summary and comparison panels from:
  - `run_summary.json`
  - `experiment_report.json`
  - `comparison_report.json`
- graph checkpoint sequences from:
  - `graph_checkpoints/index.json`
  - per-checkpoint JSON payloads or chunk-backed JSONL storage
- node and edge overlay rendering from saved checkpoint payloads:
  - `coherence`
  - `base_conductance`
  - `signed_flux` when present
  - geometry-label availability flags and payload metadata
- stable-layout graph snapshots generated from saved checkpoints
- interactive final-graph HTML views
- dense checkpoint animations generated from saved frame sequences
- growth/relaxation panels derived from:
  - `num_nodes`
  - `num_edges`
  - `sink_count`
  - `birth_count`
  - `average_conductance`
  - `abundance`
  - `weighted_abundance`
- `budget_current`
- `budget_error`

For `GRCV3`:

- scalar trajectory plots from `steps.jsonl`
- event timelines from `events.jsonl`
- run-summary and comparison panels from:
  - `run_summary.json`
  - `experiment_report.json`
  - `comparison_report.json`
- `grcv3` family-extension-aware behavior panels from:
  - step-row `family_extensions["grcv3"]`
  - run-summary `family_extensions["grcv3"]`
- representative-lane graph checkpoint sequences from:
  - `graph_checkpoints/index.json`
  - per-checkpoint JSON payloads or chunk-backed JSONL storage
- representative-lane node and edge overlay rendering from saved checkpoint
  payloads:
  - `coherence`
  - `base_conductance`
  - `signed_flux_source` when present
  - geometry-label availability flags and payload metadata
- representative-lane stable graph snapshots, interactive final HTML views,
  and dense animations generated from saved checkpoints
- seed-driven landscape graph checkpoint sequences from:
  - `graph_checkpoints/index.json`
  - per-checkpoint JSON payloads or chunk-backed JSONL storage
- seed-driven landscape stable graph snapshots, interactive final HTML views,
  graph comparison panels, and dense animations generated from saved
  checkpoints

For `GRC9`:

- scalar trajectory plots from `steps.jsonl`
- event timelines from `events.jsonl`
- run-summary and comparison panels from:
  - `run_summary.json`
  - `experiment_report.json`
  - `comparison_report.json`
- `grc9` family-extension-aware behavior panels from:
  - step-row `family_extensions["grc9"]`
  - event-row `family_extensions["grc9"]`
  - run-summary `family_extensions["grc9"]`
- representative `primary` / `replay` behavior lanes under:
  - `outputs/representative/grc9/<lane_name>/`
- seed-driven `cell-1` / `cell-4` behavior lanes under:
  - `outputs/representative/grc9_landscape/<profile_name>/`
- optional GRC9 port-graph checkpoints emitted by representative and
  seed-driven lanes when run with `record_graph_checkpoints=True`
- representative and seed-driven `port_graph` visual outputs from saved
  checkpoints:
  - stable graph sequence figures
  - final interactive graph HTML views
  - graph comparison panels
  - dense graph animations when checkpoint cadence is present
- CLI wrappers:
  - `pygrc.cli.grc9_representative_visuals`
  - `pygrc.cli.grc9_landscape_visuals`

The current representative and seed-driven GRC9 lanes are smoke/evidence
fixtures for renderer development. They are not yet canonical structure-
discovery lanes. The seed-driven `cell-1` / `cell-4` inputs in particular are
shared landscape fixtures structurally grafted into GRC9, not native GRCL-9
source structures.

### Not Yet Supported By Current Phase T Artifacts

Across families more generally:

- true per-step flow-field playback when no graph checkpoint cadence was saved
- higher-frequency graph playback beyond the recorded checkpoint lane
- graph-local overlays for artifact channels that are still not exported by the
  checkpoint payload
- any surface that would need live model access rather than the saved telemetry
  contract

For `GRC9` specifically:

- graph rendering is allowed only from saved `port_graph` checkpoint artifacts
- GRC9 port-chart graph grammar is not the same visual grammar as GRCV3 graph
  rendering and needs family-specific representation rules
- diagnostic-probe visualization is separate from saved run-lane visualization

Those remaining gaps are not reasons to reach into live model state. Phase V
should render only what the saved telemetry and checkpoint artifacts expose.

This means graph rendering in Phase V should evolve gradually:

- **Stage 1**:
  - trajectories
  - event timelines
  - report/comparison panels
- **Stage 2**:
  - checkpoint-backed graph snapshots
  - final-graph HTML views
  - side-by-side graph comparison panels
- **Stage 3**:
  - dense graph animations
  - richer graph-local overlays
  - more specialized flow visuals as export scope expands

## In Scope

- artifact-driven trajectory plots
- event timelines and event-density panels
- experiment summary/report panels
- pairwise comparison panels
- graph-evolution and flow-activity visuals driven by saved checkpoints
- any remaining artifact-gap definition needed for later graph-facing surfaces

## Out Of Scope

- direct live-model visualization as the primary path
- ad hoc notebook-only plotting logic with no stable boundary
- speculative semantics not grounded in telemetry/report artifacts
- PDE-style 2D heatmap equivalence claims where no 2D embedding exists

## Design Principles

### 1. Artifact First

Every first-pass visual must be reproducible from saved artifacts. If a visual
cannot be generated from artifacts, the missing artifact contract must be named
explicitly.

### 1.1 Standard Visualization Backends, Not A Custom Graph Renderer

Phase V should not attempt to build a bespoke graph-visualization engine.

The intended strategy is:

- use standard plotting libraries for scalar trajectories and report panels,
- use a standard graph-visualization backend for graph snapshots, graph-local
  overlays, and dense checkpoint animations once the needed artifacts exist,
- and keep `PyGRC` custom code limited to:
  - loading artifacts,
  - transforming them into backend-friendly structures,
  - selecting stable layouts/options,
  - and composing experiment-facing figures/panels.

In other words:

- **custom adapter layer**: yes
- **custom graph rendering engine**: no

### 1.2 Recommended Backend Split

The agreed Phase V backend stack is:

- **trajectory plots / event timelines / report panels**:
  - `matplotlib`
- **graph structure interchange layer**:
  - `networkx`
- **interactive graph views**:
  - `pyvis`
- **static graph snapshots when needed**:
  - generated from the `networkx` interchange model with the chosen standard
    plotting/rendering stack

The architectural decision should already be treated as fixed:

- Phase V owns adapters and figure composition,
- external libraries own graph rendering.

### 2. Graphs Are Not Heatmaps

The PDE-side intuition of spatial heatmaps still matters, but in `PyGRC` the
substrate is graph-based. The graph analogue is not a fake heatmap over an
imagined plane. It is a combination of:

- graph snapshots,
- node/edge attribute overlays,
- event-local markings,
- and time-indexed structural summaries.

For the first graph pass, Phase V should prefer:

- stable graph snapshots,
- side-by-side checkpoint comparison views,
- and dense animations only when checkpoint cadence is already available.

### 3. Show Change, Not Just State

The first useful graph-facing visuals should emphasize change:

- births over time,
- node/edge-count growth,
- sink formation,
- conductance relaxation,
- graph checkpoint deltas,
- and dense animations when checkpoint cadence is high enough to support them.

### 4. Honest Ceiling

If flow activity is not yet exported as artifact data, the visual surface must
say so. Phase V should not “fake” flow with arbitrary arrows or inferred edge
weights that were never saved.

## Workstreams

## Workstream 1. Visualization Boundary And Package Layout

Define the visualization package/module boundary and how it consumes telemetry
artifacts without reaching into family-local runtime internals.

Questions to settle:

- whether visualization lives under `src/pygrc/visualization/`
- what the public loader/renderer entrypoints are
- how file outputs under `outputs/` are organized

Required backend boundary:

- trajectory and panel rendering should target `matplotlib`
- graph rendering should target `networkx` plus `pyvis` through an adapter or
  export surface
- no workstream in Phase V should implement custom graph layout or graph
  rendering primitives beyond trivial fallback/debug helpers

Acceptance focus:

- one explicit visualization package boundary exists
- artifact-driven loading is the default path
- the backend strategy is explicit and does not rely on bespoke graph rendering

## Workstream 2. Trajectory Plots

Implement deterministic plotting surfaces for numeric observable trajectories.

Minimum targets:

- one-run trajectory figure
- two-run comparison figure
- plots for:
  - `budget_current`
  - `budget_error`
  - `num_nodes`
  - `num_edges`
  - `sink_count`
  - `birth_count`
  - `average_conductance`
  - `abundance`
  - `weighted_abundance`

Acceptance focus:

- `cell-1` and `cell-4` can be rendered without a live model object
- the budget-conservation line is visibly flat in both runs
- `cell-4` growth is visually distinguishable from `cell-1` quiescence

## Workstream 3. Event Timelines

Render event timing explicitly from `events.jsonl` and per-step event counts.

Minimum targets:

- event raster/timeline per run
- per-step event-count plot
- summary of first/last event times where events exist

Acceptance focus:

- empty-event runs render honestly as event-free timelines
- `cell-4` shows delayed onset and continued birth activity

## Workstream 4. Experiment Panels And Comparison Views

Turn report payloads into compact experiment-facing panels.

Minimum targets:

- changed-observables panel
- event-count panel
- checkpoint-overview panel
- final-summary delta panel for pairwise comparison

Acceptance focus:

- report visuals map directly to explicit report fields
- pairwise comparison does not require hand-written interpretation

## Workstream 5. Topology And Flow Artifact Bridge

The checkpoint-backed artifact bridge is now landed. This workstream remains as
the boundary document for what graph rendering is allowed to consume and what
still counts as missing export scope.

This bridge work should answer:

- what topology snapshots must be exported,
- what node/edge attributes must accompany them,
- what flow quantities must be exported,
- how checkpoints are selected,
- and whether stable layout hints should be saved or derived deterministically
  at visualization time.

Minimum required topology payload:

- node IDs
- edge connectivity
- checkpoint identity
- node attributes needed for visual overlays
- edge attributes needed for visual overlays

Minimum required flow payload:

- per-edge flux or a clearly scoped flow surrogate
- node net-flux summaries when relevant
- explicit distinction between conductance and flux quantities

Coordinates/layout note:

- fixed coordinates are **not required** to begin graph visualization
- but reproducible graph views will need either:
  - saved layout hints, or
  - a deterministic layout policy at render time

Acceptance focus:

- topology and flow visualization requirements are explicit
- coordinates are treated as optional layout aids rather than mandatory source
  semantics
- the next upstream extension step is obvious

Bridge contract for this workstream:

- [`Phase-V-TopologyFlowArtifactBridge.md`](./Phase-V-TopologyFlowArtifactBridge.md)

## Workstream 6. Graph-Evolution Visualization Contract

Define the render-time contract for honest graph evolution on top of saved
checkpoint artifacts.

Likely missing data to specify:

- checkpoint topology export
- node attributes at checkpoint steps
- edge attributes at checkpoint steps
- event-to-checkpoint linking

This workstream may design the contract even if implementation lands partly in
Phase T or as a bridge iteration.

Expected downstream use:

- checkpoint graph exports should convert cleanly into `networkx`
- graph snapshots should reuse one deterministic layout across frames
- dense runs should produce animations rather than only isolated still frames

Acceptance focus:

- a written contract exists for graph-evolution rendering
- the contract is artifact-driven and family-extensible

Contract for this workstream:

- [`Phase-V-GraphEvolutionContract.md`](./Phase-V-GraphEvolutionContract.md)

## Workstream 7. Flow-Activity Visualization Contract

Define the saved quantities required for flow visuals.

Likely missing data to specify:

- per-edge flux values by checkpoint or step
- node net-flux summaries when available
- conductance overlays distinct from flux overlays

Acceptance focus:

- flow visuals are not implemented on invented data
- the required export surface is explicit and can be handed upstream

Contract for this workstream:

- [`Phase-V-FlowActivityContract.md`](./Phase-V-FlowActivityContract.md)

## Workstream 8. Representative Visualization Lane

Use the existing representative `GRCV2` runs as the first visualization lane.

Primary starting lane:

- `cell-1`
- `cell-4`
- `balanced_baseline`
- `num_steps = 100`
- `rng_seed = 7`

This lane is preferred over the original 3-step lane because it already shows:

- delayed birth onset,
- long-horizon structural divergence,
- stable budget conservation,
- and a meaningful contrast between quiescent and expansive behavior.

Acceptance focus:

- Phase V visuals make the 100-step behavioral split obvious
- all visuals are reproducible from saved artifacts

## Workstream 9. GRCV3 Behavior Visualization Lane

Use a two-stage `GRCV3` behavior lane:

1. the replay-stability `primary` / `replay` lane as the bridge surface
2. the real seed-driven `cell-1` / `cell-4` lane as the actual closeout
   surface

The closeout lane should live under:

- `outputs/representative/grcv3_landscape/<profile_name>/`
- `cell-1`
- `cell-4`

The default first truthful closeout profile is:

- `profile_name = "seed_baseline"`

Purpose:

- prove that `GRCV3` telemetry artifacts can already support behavior-facing
  visuals
- surface the `grcv3` family-extension summaries in an experiment-facing way
- and then show a real seed-to-seed contrast rather than only replay
  equivalence

Acceptance focus:

- `GRCV3` behavior visuals are reproducible from saved artifacts only
- the bridge lane still makes replay equivalence legible
- the real `cell-1` versus `cell-4` lane makes an actual behavioral difference
  legible from artifacts
- `grcv3` extension summaries are legible without reopening raw JSON files

Implementation note:

- the landed behavior lane should reuse the shared run/comparison renderer
  rather than fork a `GRCV3`-local plotting stack
- `grcv3` specificity should appear through:
  - lane discovery (`primary` / `replay` for the bridge lane, `cell-1` /
    `cell-4` for the closeout lane)
  - selected behavior-facing trajectory series
  - flattened `grcv3` family-extension summaries in run/comparison panels
- the behavior surface is recorded in:
  - [Phase-V-GRCV3-RepresentativeVisualization.md](./Phase-V-GRCV3-RepresentativeVisualization.md)

## Workstream 10. GRCV3 Graph Visualization Boundary

Record and implement the explicit boundary between:

- `GRCV3` representative graph visualization that can now be done from saved
  checkpoints
- and `GRCV3` seed-driven landscape graph visualization that is now also
  available from its own saved checkpoint lane

This workstream should keep the lane split explicit:

- representative `primary` / `replay` graph visuals are now in scope
- seed-driven `cell-1` / `cell-4` graph visuals are now also in scope through
  the checkpoint-backed landscape telemetry lane

Acceptance focus:

- no one can mistake representative graph-capable `GRCV3` for full family-wide
  graph-capable `GRCV3`
- the lane split between representative and seed-driven evidence remains
  explicit even though both are now graph-capable
- the graph/telemetry closeout is kept separate from the still-open projector
  and `GRCL-v3` semantic questions

The final family-closeout slice now includes:

- seed-driven `cell-1` / `cell-4` graph snapshots from saved checkpoints
- seed-driven graph comparison panels from saved checkpoints
- seed-driven graph animation from saved checkpoint cadence when present
- explicit closeout of the remaining lane-local graph boundary

## Workstream 11. Generic GRC9 Visualization Capability

Extend Phase V to cover GRC9 through the shared visualization plan/checklist,
with a family-specific representation note rather than a separate Phase V
sub-plan.

The representation note is:

- [Phase-V-GRC9-RepresentativeVisualization.md](./Phase-V-GRC9-RepresentativeVisualization.md)

The current GRC9 deliverable is renderer capability, not a scientific closeout
run:

- render any saved `grc9` telemetry artifact lane that carries the Phase T-GRC9
  family extension,
- render representative `primary` / `replay` and seed-driven `cell-1` /
  `cell-4` behavior surfaces from saved artifacts,
- render representative and seed-driven `port_graph` surfaces only when saved
  graph checkpoints exist,
- expose both visual suites through importable CLI wrappers,
- use current representative and seed-driven lanes only as smoke fixtures,
- keep run selection and motif selection outside the renderer.

Purpose:

- make the Phase T-GRC9 telemetry visible without reopening model internals
- expose nine-port, row/column, spark, expansion, growth, coarse-graining,
  budget, and fission diagnostics as GRC9-specific visual evidence
- keep GRC9 graph visualization checkpoint-backed rather than inferring graph
  state from live runtime objects

Acceptance focus:

- behavior visuals are reproducible from saved artifacts only
- GRC9 trajectory selections use `family_extensions["grc9"]`
- report and comparison panels expose GRC9 summaries directly
- current `cell-1` / `cell-4` grafted seed lanes are not treated as native
  GRC9 structure evidence
- graph requests fail explicitly when checkpoint artifacts are missing
- `pygrc.cli.grc9_representative_visuals` and
  `pygrc.cli.grc9_landscape_visuals` render the same artifact-backed surfaces
  as the Python API
- GRC9 visualization does not claim GRCV3 hierarchy, GRCL-9 lowering,
  Lorentzian causal semantics, observer-local views, or boundary barrier/ghost
  runtime behavior

## Downstream GRC9 Work Outside Phase V

Structure discovery and GRCL-9 translation are not Phase V implementation
workstreams. They are downstream GRC9 work that can use the Phase V GRC9
visualization surfaces after new discovery structures have been generated and
run through telemetry.

The downstream structure-discovery step should reason from the GRC9 paper
mechanics to graph-local structure hypotheses, generate those structures, run
them through Phase T-GRC9 telemetry, and then identify which generated motifs
are worth visualizing:

This workstream should produce a manifest or report that can drive visuals:

- spark precursor windows,
- expansion modules and reassignment patterns,
- growth loci and birth-pressure windows,
- column diagnostic regimes,
- coarse-graining/profile-sparsity regimes,
- budget-correction regimes if present,
- identity-fission candidate and confirmed windows.

The output should be artifact-facing, for example:

- `grc9_structure_discovery_manifest.json`
- or a documented report payload consumed by visualization helpers.

Downstream acceptance focus:

- structure discovery does not treat existing GRC9 smoke lanes as the search
  space
- generated structures cite the paper mechanisms and graph preconditions that
  motivated them
- discovered windows cite predicted and observed telemetry fields that justify
  selection
- visualization can render selected motifs from the manifest
- terminology remains GRC9-native: spark, expansion, growth, fission
  diagnostic; not GRCV3 split/collapse unless the artifact is explicitly a
  cross-family comparison

Only after GRC9 structure discovery identifies meaningful motifs should the
project define GRCL-9 translation work.

Purpose:

- move beyond structurally grafted shared landscape fixtures,
- author source-level structures that intentionally lower into meaningful GRC9
  port graphs,
- preserve nine-port, row/column, expansion, growth, and fission-relevant
  mechanics in the lowered graph.

Downstream acceptance focus:

- GRCL-9 translation starts from discovered GRC9-native motifs
- current `cell-1` / `cell-4` fixtures remain regression/smoke inputs unless
  discovery proves they contain relevant GRC9-native structure
- translation work remains separate from visualization renderer capability
- no GRCL-9 lowering claim is made before a GRCL-9 source contract exists

## Workstream 12. Generic GRC9V3 Visualization Capability

Extend Phase V to cover `GRC9V3` through the shared visualization
plan/checklist, following the same artifact-first rule as the other families.
This workstream does not create a separate Phase V sub-plan. Its visual
representation contract lives in this shared document and in the checklist
iterations below.

The current input evidence is the Phase T-GRC9V3 representative artifact pack:

- source lane:
  - `appendix_e_cell_division`
- artifact root:
  - `outputs/phase-t-grc9v3/representative/appendix_e_cell_division/`
- canonical representative command:
  - `PYTHONPATH=src ./.venv/bin/python scripts/run_grc9v3_representative_telemetry.py --outputs-root outputs --steps 3`

The current GRC9V3 deliverable is a representative visualization capability
over saved telemetry and checkpoints, not a new runtime experiment:

- render saved `grc9v3` telemetry artifact packs that carry the Phase T-GRC9V3
  family extension,
- render behavior surfaces for the representative Appendix E cell-division
  lane,
- render event surfaces for hybrid spark candidates, mechanical expansion,
  completed hybrid sparks, choice detection, and collapse,
- render checkpoint-backed graph surfaces from saved `port_graph` checkpoints
  and their GRC9V3 overlays,
- expose behavior, event, run-summary, and graph surfaces through importable
  API and CLI wrappers,
- keep later GRC9V3 phenomenology discovery and any source/GRCL lowering out
  of this renderer implementation slice.

Purpose:

- make Phase T-GRC9V3 telemetry visible without reopening model internals,
- preserve the ownership split between `grc9_mechanical`, `grcv3_semantic`,
  and `grc9v3_hybrid` surfaces,
- show the hybrid interaction rather than flattening GRC9V3 into either parent
  family,
- make the Appendix E representative lane visually inspectable from saved
  artifacts and replay flags.

### GRC9V3 Representative Visual Meaning

The minimum GRC9V3 behavior bundle should reuse the shared Phase V artifact
layout:

- `visualization/trajectories.png`
- `visualization/events.png`
- `visualization/report_panel.png`

The trajectory selections should be GRC9V3-specific. Candidate series include:

- port chart:
  - `family_extensions.grc9v3.port_chart.num_nodes`
  - `family_extensions.grc9v3.port_chart.num_port_edges`
  - `family_extensions.grc9v3.port_chart.saturated_node_count`
- row-basis differential:
  - `family_extensions.grc9v3.row_basis_differential.gradient_norm_mean`
  - `family_extensions.grc9v3.row_basis_differential.signed_hessian_mean`
  - `family_extensions.grc9v3.row_basis_differential.current_min_signed_hessian_min`
- hybrid tensor:
  - `family_extensions.grc9v3.hybrid_tensor.tensor_trace_mean`
  - `family_extensions.grc9v3.hybrid_tensor.tensor_anisotropy_max`
- transport:
  - `family_extensions.grc9v3.transport.flux_abs_sum`
- identity and hierarchy:
  - `family_extensions.grc9v3.identity_basin.sink_count`
  - `family_extensions.grc9v3.identity_basin.basin_count`
  - `family_extensions.grc9v3.identity_basin.daughter_sink_count`
  - `family_extensions.grc9v3.hierarchy_state.max_hierarchy_depth`
- hybrid spark:
  - `family_extensions.grc9v3.hybrid_spark_state.hybrid_spark_candidate_count`
  - `family_extensions.grc9v3.hybrid_spark_state.completed_hybrid_spark_count`
  - `family_extensions.grc9v3.hybrid_spark_state.candidate_failure_reason`
- choice/collapse:
  - `family_extensions.grc9v3.choice_collapse.choice_regime_count`
  - `family_extensions.grc9v3.choice_collapse.collapse_registry_count`
- budget:
  - `family_extensions.grc9v3.budget_correction.budget_error`

The minimum event surface should make the hybrid sequence inspectable:

- spark candidate,
- expansion module creation,
- completed hybrid spark,
- choice detection,
- collapse,
- budget and coarse-cache events when present.

The minimum run-summary surface should show:

- lifecycle event counts,
- final port chart summary,
- final differential and tensor summaries,
- final identity, hierarchy, choice/collapse, and budget summaries,
- Appendix E representative summary,
- replay flags and digest-match status.

### GRC9V3 Graph Visual Boundary

GRC9V3 graph visualization is checkpoint-backed port-graph visualization with
hybrid overlays. It should not infer graph state from live runtime objects.

Required checkpoint surfaces:

- base `port_graph` node and edge topology,
- `family_extensions["grc9v3"].node_overlay`,
- `family_extensions["grc9v3"].port_overlay`,
- `family_extensions["grc9v3"].edge_overlay`,
- `family_extensions["grc9v3"].module_overlay`,
- `family_extensions["grc9v3"].choice_overlay`.

Representative Appendix E visuals should highlight, when present in saved
overlays:

- the saturated spark candidate before expansion,
- the mechanical expansion module and its node roles,
- daughter sink nodes,
- hierarchy parent and child links,
- choice/collapse source and target nodes,
- budget preservation status.

### GRC9V3 Non-Claims

GRC9V3 visualization must not claim:

- new GRC9V3 phenomenology discovery,
- source-level or GRCL lowering,
- Lorentzian causal semantics,
- observer-local views,
- boundary barrier/ghost runtime behavior,
- adiabatic expansion,
- full GRCV3 weighted least-squares geometry unless the saved artifact names
  that backend explicitly.

Acceptance focus:

- behavior visuals are reproducible from saved Phase T-GRC9V3 artifacts only,
- trajectory selections use `family_extensions["grc9v3"]`,
- graph views render only from saved checkpoint artifacts and explicit GRC9V3
  overlays,
- missing checkpoint or overlay artifacts fail clearly rather than producing
  inferred visuals,
- ownership tags are visible enough that a reader can distinguish mechanical,
  semantic, and hybrid fields,
- Appendix E cell-division evidence is rendered as representative GRC9V3
  evidence, not as GRCL/source evidence.

## Deliverables

- visualization package boundary
- one-run trajectory visuals
- two-run comparison visuals
- event timelines
- experiment report panels
- checkpoint-backed graph snapshots
- final interactive graph HTML views
- dense graph animations when checkpoint cadence is present
- written topology/flow artifact bridge requirements
- written contract for graph-evolution artifact support
- written contract for flow-activity artifact support
- `GRCV3` behavior-facing representative visuals from saved telemetry/report
  artifacts
- `GRCV3` representative graph-facing visuals from saved checkpoint artifacts
- seed-driven `GRCV3` landscape graph-facing visuals from saved checkpoint
  artifacts
- generic `GRC9` behavior-facing visual renderer for saved Phase T telemetry
  artifacts
- representative `GRC9` graph-facing visuals from saved port-graph checkpoint
  artifacts
- seed-driven `GRC9` landscape graph-facing visuals from saved port-graph
  checkpoint artifacts
- written GRC9 visualization representation note for nine-port mechanics and
  port-graph visualization
- generic `GRC9V3` behavior-facing visual renderer for saved Phase T-GRC9V3
  telemetry artifacts
- representative `GRC9V3` graph-facing visuals from saved port-graph
  checkpoint artifacts and GRC9V3 overlays
- written GRC9V3 visualization representation boundary inside this shared
  Phase V plan/checklist

## Exit Criteria

Phase V should be considered complete for its currently justified family lanes
only if:

- the key `cell-1` / `cell-4` behavioral difference is visible from saved
  artifacts,
- budget conservation is directly inspectable in the visuals,
- event timing is directly inspectable in the visuals,
- comparison views come from report artifacts rather than manual curation,
- graph snapshots and graph comparison views are reproducible from saved
  checkpoints without live model access,
- dense checkpoint lanes produce true animations rather than just frame dumps,
- graph/flow visualization dependencies remain explicit before any further
  nontrivial graph rendering begins,
- and the missing artifact requirements for graph evolution and flow activity
  are written down explicitly rather than hidden behind prototype code.

For the `GRCV3` family specifically, the currently justified closeout requires:

- the bridge `primary` versus `replay` agreement is visible from saved
  artifacts,
- the bridge `primary` versus `replay` graph evolution is also visible from
  saved checkpoints when that representative lane was recorded with graph
  export enabled,
- the real `cell-1` versus `cell-4` lane is also rendered from saved artifacts,
- the real `cell-1` versus `cell-4` graph evolution is also visible from saved
  checkpoints through the landed landscape checkpoint lane,
- step-order traces and `grcv3` family-extension summaries are visible through
  behavior-facing visuals,
- and the documentation states explicitly that telemetry/visualization closeout
  is complete while projector/semantic work remains open separately.

For the `GRC9` family specifically, the currently justified visualization slice
requires:

- generic behavior rendering works for saved Phase T-GRC9 artifacts without
  hard-coding a scientific run,
- GRC9-specific telemetry surfaces are visible through trajectories and panels,
- representative and seed-driven graph views render only from saved port-graph
  checkpoints,
- representative and seed-driven CLI wrappers expose behavior, graph, and all
  surfaces from saved artifacts,
- structure discovery and GRCL-9 translation remain downstream GRC9 work rather
  than Phase V implementation work,
- and the documentation states explicitly that visualization does not lift GRC9
  into GRCV3, GRCL-9, Lorentzian, observer-local, or boundary barrier/ghost
  semantics.

For the `GRC9V3` family specifically, the currently justified visualization
slice requires:

- generic behavior rendering works for saved Phase T-GRC9V3 artifacts without
  live runtime access,
- GRC9V3-specific telemetry surfaces are visible through trajectories and
  panels,
- event visuals distinguish hybrid spark, mechanical expansion, completed
  spark, choice, and collapse lifecycle stages,
- graph views render only from saved port-graph checkpoints with GRC9V3
  overlays,
- representative CLI wrappers expose behavior, graph, and all surfaces from
  saved artifacts,
- GRC9V3 phenomenology discovery and source/GRCL lowering are separate
  downstream tracks rather than Phase V implementation work, and are now closed
  through [GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md),
- and the documentation states explicitly that visualization does not flatten
  GRC9V3 into GRC9, GRCV3, GRCL/source, Lorentzian, observer-local, boundary
  barrier/ghost, or adiabatic-expansion semantics.
