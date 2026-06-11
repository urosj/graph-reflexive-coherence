# Phase V GRC9 Visualization

## Purpose

This note records the intended Phase V visualization boundary for `GRC9`.

It follows the same documentation role as
`Phase-V-GRCV3-RepresentativeVisualization.md`: the shared Phase V plan and
checklist define the implementation sequence, while this family note defines
what GRC9 visuals are supposed to mean.

GRC9 visualization must not be a relabeled GRCV3 visualization. It should make
the Phase T-GRC9 paper-facing telemetry visible as GRC9:

- fixed nine-port charts,
- row and column structure,
- spark gates,
- expansion modules,
- coherence transfer and internal bond initialization,
- growth on inactive ports,
- coarse-graining and reconstruction diagnostics,
- budget correction,
- identity-fission candidate and confirmed persistence diagnostics.

Post-closeout growth correction: visuals that include growth must distinguish
corrected `grc9_front_capacity` evidence from historical
`legacy_any_inactive_port` broad-growth diagnostics. Legacy broad-growth
visuals remain reproducible for inspection only, require `--force-legacy-growth`
on guarded tools, and are non-evidence.

## Renderer Boundary

The first Phase V-GRC9 implementation should be generic. It should render any
saved artifact lane whose step/event/run-summary rows carry
`family_extensions["grc9"]`.

Current lanes are useful as smoke fixtures and early evidence, but they are not
yet canonical scientific GRC9 structure lanes. Run and motif selection belongs
to downstream GRC9 structure-discovery work, not to Phase V renderer
implementation.

## Example Input Lanes

### Representative Mechanical Lane

Default lane:

- experiment path:
  - `outputs/representative/grc9/<lane_name>/`
- lane name:
  - `phase_t_grc9_iter6_representative`
- run roles:
  - `primary`
  - `replay`

This lane is a useful first smoke fixture for the paired-run renderer. It
should render from saved step rows, event rows, reports, run summaries, and
`grc9` family extensions. It should not be treated as a final scientific
visualization target by the renderer itself.

### Seed-Driven Structural Lane

Default lane:

- experiment path:
  - `outputs/representative/grc9_landscape/<profile_name>/`
- profile name:
  - `phase_t_grc9_iter7_seed`
- run roles:
  - `cell-1`
  - `cell-4`

This lane is a structurally grafted seed bridge. `cell-1` and `cell-4` are
shared landscape fixtures originally used through the GRCV2 blueprint path, not
native GRC9 source structures. Visuals may display
`source_lowering_mode = structural_graph_graft_v1`, but must not describe it as
`GRCL-9` lowering, `GRC9V3` source semantics, or a canonical GRC9 motif lane
unless later structure discovery justifies that claim.

### Diagnostic Probe

Entrypoint:

- `telemetry.build_grc9_diagnostic_probe()`

The diagnostic probe is useful for a later compact paper-facing panel. It is
not a substitute for saved run-lane artifacts.

## Behavior Visual Meaning

The minimum GRC9 behavior bundle should reuse the shared Phase V artifact
layout:

- `visualization/trajectories.png`
- `visualization/events.png`
- `visualization/report_panel.png`
- comparison `visualization/comparison_trajectories.png`
- comparison `visualization/comparison_panel.png`

The trajectory selections should be GRC9-specific. Candidate series include:

- port chart:
  - `family_extensions.grc9.port_chart.num_nodes`
  - `family_extensions.grc9.port_chart.num_port_edges`
  - `family_extensions.grc9.port_chart.saturated_node_count`
  - `family_extensions.grc9.port_chart.near_saturated_node_count`
- row tensor:
  - `family_extensions.grc9.row_tensor.row_tensor_mean`
  - `family_extensions.grc9.row_tensor.row_tensor_anisotropy_max`
  - `family_extensions.grc9.row_tensor.row_mismatch_term_max`
- column diagnostic:
  - `family_extensions.grc9.column_diagnostic.column_proxy_candidate_count`
  - `family_extensions.grc9.column_diagnostic.sign_crossing_candidate_count`
  - `family_extensions.grc9.column_diagnostic.column_profile_sparsity`
- transport:
  - `family_extensions.grc9.transport.conductance_mean`
  - `family_extensions.grc9.transport.flux_abs_mean`
- identity and abundance:
  - `family_extensions.grc9.identity_abundance.sink_count`
  - `family_extensions.grc9.identity_abundance.max_basin_size`
  - `family_extensions.grc9.identity_abundance.successor_tie_count`
  - `family_extensions.grc9.identity_abundance.scale_weighted_abundance`
- coarse-graining:
  - `family_extensions.grc9.coarse_graining.coarse_field_count`
  - `family_extensions.grc9.coarse_graining.column_profile_sparsity_mean`
- budget:
  - `family_extensions.grc9.budget_correction.budget_error_after`

Run and comparison panels should flatten and expose:

- lifecycle event counts,
- expansion summary,
- growth summary,
- calibration summary,
- diagnostic status summary.

## Event Visual Meaning

Generic event counts are not enough for GRC9 closeout.

A later GRC9-specific event surface should make these event families visible:

- spark:
  - instability gate,
  - column-proxy gate,
  - sign-crossing gate,
  - predicted module size,
- expansion:
  - module size,
  - boundary reassignment counts by column,
  - coherence transfer ratios,
  - bond mode and internal conductance stats,
- growth:
  - selected parent port,
  - outward flux pressure,
  - birth probability,
- budget and coarse invalidation events when present.

This can start as an enriched `events.png` and later become a dedicated
`grc9_events.png` if the generic event renderer becomes too crowded.

## Downstream Structure Discovery

After generic GRC9 visualization exists, downstream GRC9 work should perform
theory-first structure discovery. This is not a Phase V implementation slice,
but Phase V should leave the renderer usable for validating generated
structures after they have been run through Phase T-GRC9 telemetry.

The dedicated discovery plan is
[`GRC9-PhenomenologyDiscovery-Plan.md`](./GRC9-PhenomenologyDiscovery-Plan.md).

The discovery layer should reason from GRC9 paper mechanisms to graph-local
preconditions, generate structures from those hypotheses, and then validate:

- spark precursor windows,
- expansion modules and boundary reassignment patterns,
- growth loci and birth-pressure windows,
- row/column or column-diagnostic regimes,
- coarse-graining/profile-sparsity regimes,
- budget-correction regimes when present,
- identity-fission candidate and confirmed windows.

The output should be a manifest or report that records:

- generated structure identity,
- motivating paper mechanism and graph preconditions,
- selected step/event windows,
- selected node/module/edge identifiers where available,
- predicted and observed `family_extensions["grc9"]` field paths that justify
  each selection,
- and explicit non-claims.

Visualization can then consume that manifest to render discovered motifs. This
avoids choosing visuals just because a smoke lane exists.

Terminology guard:

- pure GRC9 discovery should use spark, expansion, growth, and fission
  diagnostic language.
- GRCV3 split/collapse language belongs to GRCV3 or explicit cross-family
  comparison, not to pure GRC9.
- GRC9 collapse-adjacent structural probes may be visualized only as
  `collapse_candidate`, `structural_collapse_probe`, or deferred diagnostics
  when saved Phase T-GRC9 telemetry or graph checkpoints explicitly provide
  that status.

Collapse-adjacent visualization decision:

- [Phase-V-GRC9-CollapseAdjacentVisualizationReview.md](./Phase-V-GRC9-CollapseAdjacentVisualizationReview.md)
  accepts manifest-driven structural visualization over existing behavior
  plots, graph checkpoints, and GRCL-9 provenance for the next GRCL-9 batch.
- It reuses the GRCV3 transparent-source/arrow/target visual grammar only for
  selector-backed `collapse_adjacent_structural_probe` overlays. It does not
  add a GRC9 collapse event row or unqualified collapsed-node status.

## Graph Visual Boundary

GRC9 graph visualization is port-chart visualization, not generic GRCV3 graph
visualization.

The optional graph surface renders checkpoint-backed GRC9 port graphs:

- fixed nine-port node structure,
- occupied versus inactive ports,
- row and column occupancy,
- module core/satellite/helper roles,
- reassigned boundary edges by column,
- internal expansion-module edges,
- conductance as structural coupling,
- signed flux as directional activity when checkpoint artifacts include it,
- basin/sink overlays,
- identity-fission candidate and confirmed overlays when run-summary data
  supports them,
- collapse-adjacent structural probe overlays only when an upstream
  GRCL-9/selector artifact provides motif roles and evidence status. These
  overlays use transparent marked source nodes and dashed arrows for visual
  continuity with GRCV3 collapse views, but remain structural-probe labels.

Existing checkpoint exporter:

- `src/pygrc/models/grc_9_checkpoints.py`
- checkpoint `graph_kind = "port_graph"`
- checkpoint payload:
  - `port_chart_module_overlay_v1`

Current requirement:

- the source GRC9 lane must be run with `record_graph_checkpoints=True`.

When saved port-graph checkpoints are absent from the artifact lane, graph
rendering must fail explicitly rather than reach into live model state.

## Non-Claims

GRC9 visuals must not claim:

- GRCV3 hierarchy, choice, collapse, or settlement semantics,
- runtime GRC9 collapse unless a future Phase T-GRC9 contract defines it,
- collapse-adjacent labels without upstream selector/report evidence,
- `GRCL-9` lowering,
- `GRC9V3` source semantics,
- Lorentzian causal-layer behavior,
- observer-local unpredictability,
- boundary barrier/ghost runtime behavior,
- signed graph flow where checkpoint artifacts do not contain signed flux.
- canonical GRC9 structure discovery from `cell-1` / `cell-4` unless later
  discovery evidence supports it.

## First Implementation Slice

The first code slice starts with behavior and now includes representative graph
rendering when checkpoint artifacts exist:

1. Add GRC9 behavior observable constants to the shared renderer.
2. Add a configurable paired-run behavior visual suite.
3. Add checkpoint-backed representative graph rendering.
4. Add checkpoint-backed seed-driven landscape graph rendering.
5. Use representative `primary` / `replay` and seed-driven `cell-1` /
   `cell-4` artifacts as smoke fixtures.
6. Add CLI wrappers.

GRC9 structure discovery and GRCL-9 translation planning are downstream
GRC9/GRCL-9 work outside Phase V.

## Current Status / Closeout

Phase V-GRC9 is closed for the current GRC9 family cycle.

Implemented visualization coverage now includes:

- representative behavior plots for GRC9 Phase T lanes,
- checkpoint-backed GRC9 port-graph rendering,
- graph visualization for saved GRC9/GRCL-9 replay sessions,
- CLI wrappers for replayed visualization sessions,
- collapse-adjacent structural-probe overlays when backed by upstream
  GRCL-9 selector/report evidence,
- and the S0024 phase-diagram visual index:
  `outputs/grcl9/lowering/sessions/S0024/visualizations/phase_diagram_visual_index.md`.

The accepted closeout boundary is:

- S0024 provides the strongest phase-diagram visualization evidence,
- S0025 records the accepted collapse-diagnostic catalog evidence,
- corrected front-capacity growth visuals supersede legacy broad-growth growth
  claims through the growth-correction migration (`S0031` corrected visuals and
  `S0036` corrected GRCL-9 growth catalog),
- collapse-adjacent visuals remain diagnostic/source-role overlays,
- and no visual surface claims a native GRC9 collapse event, observer-local
  semantics, Lorentzian causal layer, or GRCV3 hierarchy semantics.

No Phase V-GRC9 implementation item is currently open. Future visual work
should be tied to a new Phase T-GRC9 contract surface or a new GRCL-9
Revision 2 evidence lane.
