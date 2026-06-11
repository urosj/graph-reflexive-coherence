# Artifact Surface Inventory

Date: 2026-05-05

Updated: 2026-05-06 for `grc9v3_column_h_assisted` Lane B v1 documentation
alignment.

Checklist iteration:

- `implementation/ExperimentSpecificationChecklist.md`
- Iteration 1: Artifact Surface Inventory

## Summary

The existing `GRC9V3` runtime already exposes enough surface to start the
O-style experiment program without mutating `src/pygrc`.

The strongest surfaces are:

- full `GRC9V3State` / snapshot state for exact row, port, edge, sink, basin,
  hierarchy, expansion, and coarse-cache data,
- graph checkpoints for auditable node/edge/port/module overlays,
- telemetry step/event family extensions for compressed GRC9V3 summaries and
  lifecycle evidence,
- motion loader and observers for checkpoint-window motion claims.

The main caution is column-cancellation language. In Lane A `GRC9V3`, hybrid
spark candidates are gated by saturation plus basin-interior and signed-Hessian
degeneracy checks. A GRC9-style column cancellation/H proxy can be reconstructed
from ports, conductance, flux, and coherence, but for Lane A it is an
analysis-derived proxy. Lane B v1 now exposes direct runtime-computed column-H
proxy-branch evidence only when `spark_lane == "grc9v3_column_h_assisted"` and
the candidate payload records a column-H branch reason. Experiments B and D5
should therefore report Lane A column-cancellation as derived evidence and
reserve direct gate language for explicit Lane B runs.

## Source Surfaces Inspected

- `src/pygrc/models/grc_9_v3_state.py`
- `src/pygrc/models/grc_9_v3.py`
- `src/pygrc/models/grc_9_v3_runtime.py`
- `src/pygrc/models/grc_9_v3_sparks.py`
- `src/pygrc/models/grc_9_checkpoints.py`
- `src/pygrc/telemetry/grc9v3_contract.py`
- `src/pygrc/telemetry/grcl9v3_replay.py`
- `src/pygrc/landscapes/motion_loader.py`
- `src/pygrc/landscapes/motion_*.py`
- `tests/models/test_grc_9_v3_*.py`
- `tests/telemetry/test_grc9v3_*.py`

## Availability Legend

| Status | Meaning |
|---|---|
| `available` | Directly present in runtime state, checkpoint, telemetry, or observer artifact. |
| `derived` | Reconstructable from existing artifacts without changing runtime behavior. |
| `partial` | Present only in compressed form, or only under specific capture modes. |
| `blocked` | Not currently reconstructable from existing artifacts. |

## Node-Level Observations

| Observation | Status | Artifact Source | Reconstruction Method | Notes |
|---|---|---|---|---|
| Coherence density `C` | `available` | `GRC9V3State.nodes[*].coherence`; checkpoint `node_records[*].coherence`; GRC9V3 `node_overlay[*].coherence` | Direct read | Full state is exact; checkpoints are enough for reports and motion. |
| Active degree | `available` | topology incident edges; checkpoint node records; GRC9V3 `port_overlay.by_node[*].active_degree` | Direct read or count incident edges | Saturation tests can use this directly. |
| Occupied/free ports | `available` | topology ports; GRC9V3 `port_overlay.by_node[*].occupied_ports/free_ports`; GRC9 checkpoint `port_overlays` | Direct read | Full per-port row/column is available in GRC9 checkpoint surface; GRC9V3 overlay gives occupied/free ports. |
| Row/column occupancy | `available` | checkpoint row/column totals; GRC9 checkpoint `port_overlays`; topology plus port mapping | Direct or derived from port ids | Per-node row/column occupancy is derivable from occupied ports. |
| Sink status | `available` | `GRC9V3State.sink_set`; checkpoint `is_sink` / `sink_flag`; motion node evidence | Direct read | Required before spark and identity claims. |
| Basin assignment | `available` | `GRC9V3State.basins`; `nodes[*].basin_id`; `cached_quantities.geometric_identity`; checkpoint node records | Direct read | Flux basins and geometric identity caches should be distinguished. |
| Basin mass | `available` | `nodes[*].basin_mass`; `cached_quantities.geometric_identity.basin_mass_by_*`; checkpoint node records | Direct read | Unit-measure basin mass source is recorded in caches. |
| Hierarchy parent/depth | `available` | `nodes[*].parent_id/depth`; `state.hierarchy`; checkpoint node records/overlay | Direct read | Useful for post-refinement lineage and D8. |
| Row gradient vector | `available` | `nodes[*].gradient_row_basis` | Direct read from state/snapshot | Checkpoints usually expose compressed gradient norm, not the full vector. |
| Signed Hessian row vector | `available` | `nodes[*].signed_hessian_row_basis`; caches `row_basis_hessian_unsigned`, `current_min_signed_hessian_by_node` | Direct read from state/snapshot | Checkpoints/telemetry expose min/summary values. |
| Net flux row summary | `available` | `nodes[*].net_flux_summary`; runtime `compute_net_flux_summary_rows` | Direct read from state/snapshot | Useful for row-mode stress and mixed row/column motion. |
| Row mismatch sums | `available` | `cached_quantities.row_mismatch_sums` | Direct read from state/snapshot after differential rebuild | Required for row-local tensor response scoring. |
| Hybrid node tensor `K` | `available` | `cached_quantities.hybrid_node_tensors`; telemetry `hybrid_tensor` summaries | Direct read from state/snapshot; compressed telemetry summary | Exact matrix is in state cache; telemetry summaries are not enough for per-row scoring. |
| Isotropic `K` dominance | `derived` | `hybrid_node_tensors`, row mismatch sums, coherence, net flux summaries | Compare diagonal common terms to row-differential terms | Needed to avoid false negatives in Experiment A. |

## Edge And Port Observations

| Observation | Status | Artifact Source | Reconstruction Method | Notes |
|---|---|---|---|---|
| Edge endpoint nodes and ports | `available` | topology `edge_ports`; checkpoint edge records; GRC9V3 `_edge_records` | Direct read | Port ids are enough to derive row/column. |
| Port row/column | `derived` | endpoint port id | Use `port_to_rc(port_id)` / `((port-1)//3)+1`, `((port-1)%3)+1` | No runtime change needed. |
| Conductance/base weight | `available` | `port_edges[*].conductance`; `base_conductance`; checkpoint edge records/overlay | Direct read | Use `base_conductance` when present for GRC9V3 analytic labels. |
| Oriented/signed flux | `available` | `port_edges[*].flux_uv`; `cached_quantities.oriented_flux`; checkpoint edge records | Direct read with endpoint orientation | Motion loader normalizes signed edge flux when checkpoints expose it. |
| Absolute flux / functional coupling | `available` | `flux_coupling`; `abs(port_edges[*].flux_uv)` | Direct read or derived absolute value | `flux_coupling` mode is `absolute_flux`. |
| Geometric separation / metric length | `available` | `geometric_length`; checkpoint edge label if selected | Direct read | GRC9V3 mode is currently `inverse_base_conductance`. |
| Temporal delay | `available` | `temporal_delay`; checkpoint edge label if selected | Direct read | GRC9V3 mode is `transport_ratio`. |
| Edge-label computation modes | `available` | `edge_label_computation_mode`; checkpoint `label_computation_modes`; telemetry transport summary | Direct read | Reports should record modes with path comparisons. |
| Port-attached nonnegative fields | `available` | public `coarse_grain_columns(field_name)` for conductance, labels, abs flux | Direct operator call | Eligible fields reconstruct through exact column profile. |
| Signed flux split | `available` | public `coarse_grain_columns("signed_flux")`, `split_columns` | Direct operator call | Exact signed reconstruction uses positive/negative decomposition. |
| Column cancellation/H proxy | `derived` under Lane A; `available` for explicit Lane B candidate events | Lane A: endpoint ports, conductance, neighbor coherence, signed flux where needed; Lane B: candidate payload `column_h`, telemetry spark evidence, checkpoint node overlay | Lane A reconstructs column-local sums by `(node, column)`; Lane B reads direct runtime-computed values | Direct proxy-branch gate evidence exists only when `spark_lane == "grc9v3_column_h_assisted"` and `column_h_branch_hit` is true. |

## Event And Refinement Observations

| Observation | Status | Artifact Source | Reconstruction Method | Notes |
|---|---|---|---|---|
| Hybrid spark candidate | `available` | `StepResult.events`; telemetry event rows; `cached_quantities.hybrid_spark_candidate_count`; candidate event payload | Direct read when events are captured | Candidate payload includes active degree, saturation gate, basin interior gate, min signed Hessian, and thresholds. |
| Saturation gate | `available` | candidate payload; active degree from topology/checkpoint | Direct read or derived active degree | Must be paired with sink/interior/degeneracy evidence. |
| Instability/degeneracy evidence | `available` | candidate payload `gradient_norm`, `min_signed_hessian`, gates; node row Hessian state | Direct read | This is signed-Hessian degeneracy for GRC9V3. |
| Mechanical expansion event | `available` | event kind `hybrid_mechanical_expansion`; `expansion_registry`; checkpoint module overlay | Direct read | Event payload is the richest source. |
| Old boundary edge reassignment | `available` | expansion event payload `reassignment_map`; `cached_quantities.last_hybrid_expansion` | Direct read from event/cached payload | Checkpoint module overlays may be insufficient by themselves. |
| Budget before/after expansion | `available` | expansion event payload; `cached_quantities.last_budget_preservation`; telemetry budget summaries | Direct read | Required for D/D8 accepted claims. |
| Child basin stabilization | `available` | `cached_quantities.last_child_basin_stabilization`; completed event payload | Direct read | Persistence over multiple checkpoints is still an experiment-level criterion. |
| Completed hybrid spark | `available` | event kind `hybrid_spark_completed`; hierarchy cache/telemetry | Direct read | This is stronger than mechanical expansion but still should be checked against persistent basin windows. |
| Choice/collapse registries | `available` | `choice_registry`, `collapse_registry`; checkpoint choice overlay; telemetry summaries | Direct read | Useful for D8 outcome classification. |
| Growth events | `partial` | telemetry lifecycle counts; step/event rows when captured | Direct event read if runs include events | Not central to first tranche. |

## Motion Surfaces

| Observation | Status | Artifact Source | Reconstruction Method | Notes |
|---|---|---|---|---|
| Checkpoint window availability | `available` | `load_motion_window` | Direct loader result | Requires at least two checkpoints for local motion claims. |
| Node coherence/basin/sink over time | `available` | motion checkpoint node evidence | Direct loader result | Supports coherence, representative, identity, and boundary observers. |
| Edge flux/conductance over time | `available` | motion checkpoint edge evidence | Direct loader result | Edge labels beyond conductance/flux are not normalized by motion loader yet. |
| Port matrix availability flag | `available` | motion checkpoint evidence | Direct loader result | Current motion layer records availability, not full port histories. |
| Full port-history motion classification | `partial` | graph checkpoints and GRC9V3 port/edge overlays | Derived from checkpoint overlays outside current motion loader | Experiment G can use a local analyzer over checkpoints before asking for reusable motion support. |

## Per-Experiment Surface Classification

| Experiment | Surface Status | Notes |
|---|---|---|
| A row-mode stress | `available` | Exact row vectors, row mismatch sums, and tensors are in state/snapshot caches. |
| B column-interface cancellation | `derived` under Lane A; direct only in explicit Lane B runs | Column grouping is available; cancellation/H-style proxy is derived for Lane A. Lane B candidate payloads can expose direct runtime-computed column-H proxy-branch evidence. |
| C saturation and near-saturation | `available` | Active degree, sink status, candidate gates, expansion events, and budget evidence are available. |
| D refinement and child identity | `available` | Expansion payload, reassignment map, module registry, sink/basin, hierarchy, and budget evidence are available. Persistence thresholding is experiment logic. |
| E coarse-graining and Split | `available` | Public `coarse_grain_columns` and `split_columns` support the required fields. |
| F path disagreement | `available` | Edge labels and signed flux are available; path scoring conventions remain experiment logic. |
| G mixed row/column motion | `partial` | Checkpoint windows and port overlays are available; current motion loader does not normalize full per-port history, so local experiment analysis should read graph checkpoint overlays directly. |

## Blocked Or Inconclusive Surfaces

No Iteration-1 observation category is fully blocked.

The following are partial or derived and must be handled carefully:

- direct GRC9V3 column-cancellation gate evidence is not the canonical hybrid
  spark gate; report it as an analysis-derived proxy unless a concrete lane
  records a column-proxy fallback,
- full row vectors and exact tensors are state/snapshot surfaces; compressed
  checkpoint/telemetry summaries may be insufficient for per-row scoring,
- full port-history motion classification is not currently normalized by the
  motion loader; use graph checkpoint overlays in experiment-local analysis,
- event payloads are richer than graph checkpoint module overlays, so
  refinement mapping claims should cite event rows or saved step results where
  possible.

## Iteration-1 Conclusion

Iteration 1 can be marked complete. The existing runtime and artifact surfaces
are sufficient to proceed to the shared fixture and transform harness without
adding new runtime behavior.
