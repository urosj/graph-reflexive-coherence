# Phase V GRC9V3 Implementation Plan

This document is the execution plan for **Phase V-GRC9V3: Hybrid
Visualization Surfaces**.

Execution is tracked in the shared Phase V checklist:

- [Phase-V-ImplementationChecklist.md](./Phase-V-ImplementationChecklist.md)

GRC9V3 visualization iterations live in that shared checklist rather than in a
separate GRC9V3 checklist.

Phase T-GRC9V3 closed with typed telemetry, replayable representative
artifacts, and GRC9V3 checkpoint overlays. Phase V-GRC9V3 should consume those
saved artifacts and make the hybrid runtime visually legible without reaching
back into live model internals.

Post-Lane-B status: core `GRC9V3` now has an opt-in Lane B spark predicate,
`grc9v3_column_h_assisted`. Existing Phase V graph animation remains
structurally correct because Lane B reuses the existing candidate and
mechanical-expansion lifecycle. The remaining visualization gap is
interpretive: Lane B column-H proxy-branch candidates should be visually
distinguishable from Lane A signed-Hessian candidates and Lane B
signed-Hessian-only candidates.

## Purpose

Phase V-GRC9V3 must visualize the hybrid behavior that only exists when the
GRC9 port substrate and GRCV3 semantic lift interact:

- fixed nine-port mechanics,
- row-basis gradient and signed-Hessian summaries,
- hybrid Eq. (1) tensor diagnostics,
- analytic edge labels,
- flux-topology identities,
- geometric basin seeds,
- hybrid spark candidates,
- mechanical expansion modules,
- child-basin stabilization,
- completed hybrid sparks,
- hierarchy updates,
- choice/collapse/learning on GRC9 port-flux successor structure,
- growth through inactive ports when present,
- quadrature budget closure,
- and checkpoint-local node/port/edge/module/choice overlays.

The first visualization target is the Phase T-GRC9V3 representative telemetry
lane:

```text
outputs/phase-t-grc9v3/representative/appendix_e_cell_division/
```

This is the same Appendix E-style fixture as Phase 7, but rendered from Phase
T-GRC9V3 telemetry and graph checkpoints rather than runtime-only evidence.

## Inputs

Authoritative documents:

- [Phase-T-GRC9V3-Closeout.md](./Phase-T-GRC9V3-Closeout.md)
- [Phase-T-GRC9V3-RepresentativeTelemetry.md](./Phase-T-GRC9V3-RepresentativeTelemetry.md)
- [Phase-T-GRC9V3-TelemetryContract.md](./Phase-T-GRC9V3-TelemetryContract.md)
- [Phase-7-Closeout.md](./Phase-7-Closeout.md)
- [Phase-7-RepresentativeRuntime.md](./Phase-7-RepresentativeRuntime.md)
- [Phase-7-EquationMap.md](./Phase-7-EquationMap.md)
- [Phase-7-StepLoop.md](./Phase-7-StepLoop.md)
- GRC9V3 representative visualization notes in
  [Phase-V-ImplementationChecklist.md](./Phase-V-ImplementationChecklist.md)

Saved artifact input:

```text
outputs/phase-t-grc9v3/representative/appendix_e_cell_division/2646c58bb897cefe70765eec4f87fec0fba322afeb7431f6c524881864f99d98/
```

Runtime source input is allowed only for fixture meaning and replay commands,
not for visualization data extraction:

- `scripts/run_grc9v3_representative_runtime.py`
- `scripts/run_grc9v3_representative_telemetry.py`

## Relationship To Existing Phase V

Phase V-GRC9V3 should reuse the shared visualization package:

- `src/pygrc/visualization/render.py`
- `src/pygrc/visualization/graph_render.py`
- `src/pygrc/visualization/representative.py`
- `src/pygrc/visualization/representative_graphs.py`
- `src/pygrc/visualization/layout.py`

But it should not flatten into the existing `GRC9` or `GRCV3` visual meaning.

From GRC9 visualization it reuses:

- `port_graph` rendering,
- port occupancy visual grammar,
- module overlays,
- signed port flux,
- graph checkpoint artifact loading.

From GRCV3 visualization it reuses:

- differential/semantic trajectory style,
- hierarchy and choice/collapse panels,
- collapse visual grammar where actual GRC9V3 collapse events exist.

GRC9V3 adds:

- hybrid spark candidate views,
- Lane B column-H proxy-branch spark-cause views,
- expansion versus child-basin stabilization separation,
- Appendix E daughter-sink summary panels,
- row-basis semantic diagnostics on the nine-slot chart,
- and integrated module/hierarchy/choice graph overlays.

## In Scope

- family-specific observable selections for `family_extensions["grc9v3"]`,
- representative behavior visual suite,
- representative event visual suite,
- representative graph visual suite using checkpoint overlays,
- Lane B spark-lane and column-H proxy-branch visual interpretation,
- Appendix E summary panel,
- CLI wrapper for the representative lane,
- documentation of generated outputs,
- tests that render from saved artifacts without live runtime access.

## Out Of Scope

This phase does not implement:

- new runtime equations,
- new telemetry fields,
- GRC9V3 phenomenology discovery,
- reviewed GRC9V3 motif catalogs,
- GRCL/source-seed lowering for GRC9V3,
- new representative seeds beyond the Phase T artifact lane,
- Lorentzian or observer semantics,
- barrier/ghost boundary visualization unless runtime artifacts provide them,
- non-unit quadrature visuals,
- or adiabatic expansion visualization.

Lane B visual catch-up does not change runtime equations. It may consume
already-emitted Lane B telemetry and checkpoint fields such as `spark_lane`,
`last_candidate_min_abs_column_h`, `last_candidate_column_h_branch_hit`, and
node-overlay `column_h_branch_hit`.

Those are downstream tracks.

Current status: those downstream tracks are now complete through GRC9V3
phenomenology discovery and GRCL-9V3 Revision 1. This Phase V document remains
the visualization workstream record, not the source/lowering closeout.

## Workstreams

### Workstream 1. Observable Selection

Define GRC9V3 behavior observables from existing step-row family extensions.

Candidate series:

- port chart:
  - `port_chart.num_nodes`
  - `port_chart.num_port_edges`
  - `port_chart.saturated_node_count`
  - `port_chart.inactive_port_count`
- row-basis differential:
  - `row_basis_differential.gradient_norm_mean`
  - `row_basis_differential.signed_hessian_mean`
  - `row_basis_differential.current_min_signed_hessian_min`
- hybrid tensor:
  - `hybrid_tensor.tensor_trace_mean`
  - `hybrid_tensor.tensor_anisotropy_max`
  - `hybrid_tensor.row_mismatch_sum_max`
- transport:
  - `transport.base_conductance_mean`
  - `transport.flux_abs_sum`
- identity/basin:
  - `identity_basin.sink_count`
  - `identity_basin.basin_count`
  - `identity_basin.daughter_sink_count`
- spark/hierarchy:
  - `hybrid_spark_state.hybrid_spark_candidate_count`
  - `hybrid_spark_state.completed_hybrid_spark_count`
  - `hybrid_spark_state.last_candidate_min_abs_column_h`
  - `hybrid_spark_state.last_candidate_column_h_branch_hit`
  - `hierarchy_state.max_hierarchy_depth`
- choice/collapse:
  - `choice_collapse.choice_regime_count`
  - `choice_collapse.collapse_registry_count`
- budget:
  - `budget_correction.budget_error`

### Workstream 2. Representative Behavior Suite

Render:

- trajectory plot,
- event timeline,
- report panel,
- Appendix E panel,
- replay status panel.

Lane B catch-up should make the event timeline and report panel distinguish:

- Lane A `current_hybrid_signed_hessian` candidates,
- Lane B signed-Hessian-only candidates,
- Lane B column-H threshold/sign-crossing branch candidates.

The timeline should not infer the branch from event kind alone. It should use
candidate payload fields such as `spark_lane`, `column_h_branch_hit`, and
`gate_reasons`.

Because the Phase T representative lane is a single primary run with replay
verification embedded in the report, comparison visuals should be optional.
The first implementation should not invent a primary/replay pair when the
artifact lane is intentionally one canonical run.

### Workstream 3. Representative Graph Suite

Render checkpoint-backed graph visuals from:

- `graph_checkpoints/index.json`,
- per-checkpoint JSON artifacts,
- `family_extensions["grc9v3"].node_overlay`,
- `port_overlay`,
- `edge_overlay`,
- `module_overlay`,
- `choice_overlay`.

Minimum graph outputs:

- checkpoint sequence/contact sheet,
- final graph snapshot,
- interactive final graph HTML,
- optional animation,
- Appendix E module/daughter-sink visual.

Graph rendering must fail explicitly if checkpoints or overlays are missing
and the requested surface requires them.

Lane B catch-up should label or style checkpoint nodes with
`node_overlay.column_h_branch_hit == true` as column-H proxy-branch candidates.
The animation path is already structurally valid for Lane B refinements; this
additional styling makes the spark cause legible.

### Workstream 4. CLI Wrapper

Add a CLI wrapper that can render:

- `behavior`,
- `graph`,
- or `all`.

The default input should be the current Phase T-GRC9V3 representative telemetry
artifact path, with override flags for:

- telemetry root,
- experiment path,
- run id,
- visualization root,
- surface mode.

### Workstream 5. Representative Visualization Note

Create/update:

```text
Phase-V-GRC9V3-RepresentativeVisualization.md
```

The note should record:

- source telemetry artifact,
- replay command,
- visual output layout,
- what each visual means,
- what is not claimed,
- and current implementation status.

The note should include a Lane B interpretation section:

- Lane B direct evidence means direct runtime evidence that the column-H proxy
  branch fired.
- `H_s[b]` remains a proxy.
- Mechanical expansion remains distinct from identity acceptance.
- Existing Lane A visual outputs remain valid and backward-compatible.

### Workstream 6. Closeout

Close Phase V-GRC9V3 only after:

- behavior visuals render from saved artifacts,
- graph visuals render from checkpoint overlays,
- CLI wrapper works,
- tests pass,
- visual output paths are documented,
- and downstream phenomenology/discovery/GRCL boundaries are preserved.

Current status: the downstream boundaries were preserved and then completed as
separate tracks. The final source/lowering closeout is
[GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md).

## Acceptance Criteria

Phase V-GRC9V3 is complete when:

- the representative lane renders without live model access,
- behavior visuals consume `family_extensions["grc9v3"]`,
- graph visuals consume checkpoint overlays,
- Lane B visual surfaces distinguish `spark_lane` and column-H proxy-branch
  hits when those fields are present,
- Appendix E daughter sinks are visually identifiable,
- expansion action and child-basin stabilization remain visually distinct,
- choice/collapse visuals are labeled as GRC9V3 hybrid semantics,
- output paths are deterministic and documented,
- tests validate generated artifacts exist,
- and the closeout states the next track: GRC9V3 phenomenology discovery.

Post-completion note: GRC9V3 phenomenology discovery and GRCL-9V3 source
lowering are now complete; the final reviewed lowered-source catalog is `S0072`.
