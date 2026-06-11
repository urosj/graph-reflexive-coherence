# Phase V-GRC9 Collapse-Adjacent Visualization Review

## Purpose

This review records the Phase V-GRC9 visualization decision for the next
GRCL-9 collapse-adjacent work batch.

Phase T-GRC9 accepted selector-backed structural diagnostics over existing
telemetry and checkpoints. Phase V-GRC9 should therefore make those existing
surfaces inspectable without implying a runtime GRC9 collapse event.

## Decision

Phase V-GRC9 accepts **manifest-driven structural visualization using existing
GRC9 graph checkpoints, behavior plots, and event timelines** for the next
GRCL-9 batch.

Phase V-GRC9 may reuse the **GRCV3 collapse visual grammar** for structural
readability when upstream GRCL-9 selector/report evidence names a
collapse-adjacent probe:

- transparent marked source node,
- highlighted target node,
- dashed directed arrow from source to target,
- explicit label `collapse_adjacent_structural_probe`.

This is a shared view convention only. It is not a runtime GRC9 collapse link.

Phase V-GRC9 does not add, in this pass:

- unqualified GRCV3 collapse links,
- inactive-collapsed-node styling without a structural-probe label,
- a GRC9 collapse event timeline row,
- a generic `collapse_candidate` overlay independent of upstream evidence,
- or any visual claim that a GRC9 runtime collapse occurred.

The next GRCL-9 batch should provide the candidate status, source construct,
motif role, selected step window, and evidence fields in its selector/report
artifacts. Phase V should render those artifacts as structural probes.

## Accepted Visual Surfaces

### Failed Fission Persistence

Status: renderable from existing summary/checkpoint evidence.

Visual treatment:

- show the candidate module and sink/basin overlays at selected checkpoint
  steps,
- draw a transparent marked sink/source node with a dashed arrow toward the
  competing sink only when the selector report identifies the structural
  pressure direction,
- show fission candidate versus confirmed summary values in the report panel,
- label the window as `failed_fission_persistence_candidate` only when the
  selector report provides that status.

Non-claim:

- do not draw a split/collapse transition,
- do not describe the two-sink candidate as GRCV3 hierarchy.

### Sink And Basin Pressure

Status: renderable from existing behavior plots and checkpoints.

Visual treatment:

- plot `sink_count`, `basin_count`, and basin-size fields over the selected
  window,
- render checkpoint basin/sink overlays at before/after steps when available,
- use the transparent-source/arrow/target convention for selector-backed
  basin-merge pressure candidates,
- use selector-provided labels such as `basin_merge_pressure_candidate` or
  `sink_loss_pressure_candidate`.

Non-claim:

- do not mark a sink as collapsed unless a future GRC9 contract defines that
  status.

### Transport And Support Pressure

Status: renderable from existing transport plots and checkpoint edge records.

Visual treatment:

- plot `flux_abs_sum`, `flux_signed_balance`, conductance summaries, and
  strongest-edge samples when available,
- render checkpoint edge conductance/flux for selected support paths,
- use the transparent-source/arrow/target convention for selector-backed
  support-loss pressure candidates,
- use GRCL-9 provenance roles to identify membrane, ridge, bridge, or support
  edges.

Non-claim:

- do not infer membrane semantics from generic GRC9 telemetry alone.

### Membrane Or Ridge Rupture Structure

Status: renderable only when GRCL-9 provenance/checkpoint labels identify the
structure.

Visual treatment:

- show the source-authored region, motif role, and edge/path roles from the
  selector or checkpoint artifact,
- use the transparent-source/arrow/target convention for selector-backed
  membrane or ridge structural probes,
- compare before/after conductance or occupancy when the selected window
  provides it,
- label as `membrane_rupture_structural_probe`, not collapse.

Non-claim:

- no generic GRC9 membrane runtime is introduced.

## Artifact Requirements For GRCL-9 Iteration 8.1

GRCL-9 collapse-adjacent selector/report artifacts should provide:

- source fixture name,
- structural probe kind,
- selected step window,
- selected checkpoint ids,
- selected node ids, edge ids, and module ids where available,
- selected visual source and target node ids for collapse-adjacent arrows,
- evidence field paths queried,
- candidate status:
  - `artifact_backed`,
  - `structural_only`,
  - `reserved_future`,
- explicit non-claims.

Without those artifacts, Phase V should render only the generic GRC9 behavior
and graph views, not collapse-adjacent labels.

## Deferred Visual Elements

The following remain deferred until a future Phase T-GRC9 contract defines
runtime or compact diagnostic evidence:

- GRC9 collapse links,
- collapsed-node styling without `collapse_adjacent_structural_probe` labels,
- collapse event rows,
- automatic basin-merge overlays,
- automatic sink-loss overlays,
- automatic support-loss overlays.

## Non-Claims

- This review does not add runtime collapse to GRC9.
- This review reuses GRCV3 collapse visual grammar only as a labeled
  structural-probe convention.
- This review does not make ComposingCells membrane rupture a generic GRC9
  runtime semantic.
- This review does not reinterpret failed fission persistence as collapse.
