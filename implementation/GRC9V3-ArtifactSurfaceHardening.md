# GRC9V3 Artifact Surface Hardening

Status: Iteration 4 readiness note.

Scope: `current_hybrid_signed_hessian` Lane A only.

Post-readiness note: Lane B v1 is now implemented separately as
`grc9v3_column_h_assisted`. This document still defines the Lane A extraction
boundary. Lane B direct column-H proxy-branch fields are valid only for runs
whose candidate payload records `spark_lane = "grc9v3_column_h_assisted"`.

This note defines how Hessian, spark, expansion, checkpoint, and port-history
evidence should be extracted for the readiness experiments without changing
runtime semantics.

Companion schema:

- [GRC9V3-LaneA-SparkGateTraceSchema.md](./GRC9V3-LaneA-SparkGateTraceSchema.md)

## Boundary

This iteration is observability-only. It does not:

- change the default spark predicate,
- add direct column-H gating,
- define a column-H proxy formula,
- change expansion, identity, transport, or checkpoint runtime behavior.

Column-H / cancellation proxy evidence remains non-gating under Lane A. Under
Lane B v1, the runtime emits direct column-H proxy evidence in the candidate
payload and telemetry/checkpoint overlays only when
`spark_lane == "grc9v3_column_h_assisted"`.

## Evidence Labels

Use the same evidence labels as the spark-gate trace schema:

| Label | Meaning |
|---|---|
| `direct` | Read from event payloads, state fields, telemetry extensions, or checkpoint fields. |
| `reconstructed` | Computed from direct artifacts without changing runtime state. |
| `derived` | Analysis-level proxy, not a runtime predicate. |
| `partial` | Some expected fields or windows are missing. |
| `blocked` | Required fields are unavailable; do not infer the claim. |

All reports must preserve these labels. A derived or blocked field must not be
silently promoted to direct evidence.

## Candidate Event Extraction

Preferred source order:

1. `StepResult.events[kind=hybrid_spark_candidate].payload`
2. telemetry event row `family_extensions.grc9v3.spark_evidence`
3. checkpoint/state replay that reconstructs the same condition

Direct current payload fields:

- `candidate_node_id`
- `sink_node_id`
- `active_degree`
- `saturation_gate`
- `basin_interior_gate`
- `gradient_norm`
- `eps_gradient`
- `signed_hessian_degeneracy_gate`
- `min_signed_hessian`
- `eps_spark`
- `signed_crossing_enabled`
- `signed_crossing_gate`
- `basin_id`
- `parent_id`
- `depth`

State or snapshot fields may add:

- `GRC9V3State.time`
- `GRC9V3State.params_identity`
- `GRC9V3State.sink_set`
- `GRC9V3NodeState.gradient_row_basis`
- `GRC9V3NodeState.signed_hessian_row_basis`
- `cached_quantities.hessian_backend`
- `cached_quantities.hybrid_spark_signed_crossing_status`

If `sink_node_id` is available only from the candidate payload, record it as
candidate-context evidence. Do not claim an independently observed sink set
unless `GRC9V3State.sink_set`, snapshot `dynamics.state.sink_set`, or
telemetry identity evidence is available.

## Runtime Field Mapping

| Runtime / Snapshot Field | Trace Schema Destination | Evidence Label |
|---|---|---|
| `GRCEvent.kind == hybrid_spark_candidate` | `candidate_event.event_kind` | direct |
| `GRCEvent.step_index` | `candidate_event.step_index` | direct |
| `GRC9V3State.time` | `candidate_event.time` | direct when state is available |
| `GRC9V3State.params_identity` | `run.params_identity` | direct |
| `GRCParams.dt` | `run.dt` | direct |
| candidate payload `candidate_node_id` | `candidate_event.candidate_node_id` | direct |
| candidate payload `sink_node_id` | `candidate_event.sink_node_id` and `lane_a_gate_evidence.sink_status.source=candidate_payload` | direct candidate-context evidence |
| candidate payload `basin_id` | `candidate_event.basin_id` | direct |
| candidate payload `parent_id` | `candidate_event.parent_id` | direct |
| candidate payload `depth` | `candidate_event.depth` | direct |
| candidate payload `active_degree` | `lane_a_gate_evidence.active_degree` | direct |
| candidate payload `saturation_gate` | `lane_a_gate_evidence.saturation_gate` | direct |
| candidate payload `basin_interior_gate` | `lane_a_gate_evidence.basin_interior_gate` and `row_differential_evidence.basin_interior_gate` | direct |
| candidate payload `signed_hessian_degeneracy_gate` | `lane_a_gate_evidence.signed_hessian_degeneracy_gate` and `signed_hessian_evidence.signed_hessian_degeneracy_gate` | direct |
| candidate payload `gradient_norm` | `row_differential_evidence.gradient_norm` | direct |
| candidate payload `eps_gradient` | `row_differential_evidence.eps_gradient` | direct |
| candidate payload `min_signed_hessian` | `signed_hessian_evidence.min_signed_hessian` | direct |
| candidate payload `eps_spark` | `signed_hessian_evidence.eps_spark` | direct |
| candidate payload `signed_crossing_enabled` | `signed_hessian_evidence.signed_crossing_enabled` | direct |
| candidate payload `signed_crossing_gate` | `signed_hessian_evidence.signed_crossing_gate` | direct |
| `GRC9V3State.sink_set` or snapshot `dynamics.state.sink_set` | `lane_a_gate_evidence.sink_status.is_sink` | direct |
| `GRC9V3NodeState.gradient_row_basis` or snapshot `basin_attributes.nodes[*].gradient_row_basis` | `row_differential_evidence.gradient_row_basis` | direct |
| `GRC9V3NodeState.signed_hessian_row_basis` or snapshot `basin_attributes.nodes[*].signed_hessian_row_basis` | `signed_hessian_evidence.signed_hessian_row_basis` | direct |
| `cached_quantities.hessian_backend` or snapshot `dynamics.state.cached_quantities.hessian_backend` | `signed_hessian_evidence.hessian_backend` | direct |
| `cached_quantities.hybrid_spark_signed_crossing_status` or snapshot `dynamics.state.cached_quantities.hybrid_spark_signed_crossing_status` | `signed_hessian_evidence.signed_crossing_status` | direct |
| expansion payload `expansion_id` | `mechanical_expansion_followup.expansion_id` | direct |
| expansion payload `sink_node_id` | `mechanical_expansion_followup.sink_node_id` | direct |
| expansion payload `module_node_ids` | `mechanical_expansion_followup.module_node_ids` | direct |
| expansion payload `reassignment_map` | `mechanical_expansion_followup.reassignment_map` | direct |
| expansion payload `budget_*` fields | `mechanical_expansion_followup.budget_*` fields | direct |
| completion payload `stabilized_child_node_ids` | `identity_event_followup.stabilized_child_node_ids` | direct |
| completion payload `stable_child_basin_count` | `identity_event_followup.stable_child_basin_count` | direct |
| completion payload `hierarchy_parent` | `identity_event_followup.hierarchy_parent` | direct |
| completion payload `hierarchy_children` | `identity_event_followup.hierarchy_children` | direct |
| Lane B candidate payload `spark_lane == "grc9v3_column_h_assisted"` | `lane_b_gate_evidence.spark_lane` | direct for Lane B runs only |
| Lane B candidate payload `column_h` | `lane_b_gate_evidence.column_h` | direct for Lane B runs only |
| Lane B candidate payload `column_h_branch_hit` | `lane_b_gate_evidence.column_h_branch_hit` | direct proxy-branch gate evidence when true |
| Lane B candidate payload `gate_reasons` | `lane_b_gate_evidence.gate_reasons` | direct branch attribution for Lane B runs only |

## Expansion Evidence Priority

Expansion reassignment evidence must use this priority:

1. `StepResult.events[kind=hybrid_mechanical_expansion].payload.reassignment_map`
2. `cached_quantities.last_hybrid_expansion.reassignment_map`
3. `GRC9V3State.expansion_registry`
4. snapshot `basin_attributes.expansion_registry`

Interpretation:

- event payload reassignment is primary direct evidence,
- cached `last_hybrid_expansion` is direct corroborating runtime state,
- `expansion_registry` is direct registry evidence for expansion id, parent
  sink id, module node ids, expansion step, distribution weights, and schedule,
  but it does not store per-edge `reassignment_map`,
- snapshot `basin_attributes.expansion_registry` is persisted registry
  corroboration, not primary reassignment evidence.

When multiple sources exist, reports should record the chosen source and any
consistency check result. If lower-priority sources disagree with the event
payload, keep the event payload as primary and mark the disagreement as an
artifact inconsistency for follow-up.

## Completion / Identity Event Extraction

Preferred source order:

1. `StepResult.events[kind=hybrid_spark_completed].payload`
2. telemetry event row `family_extensions.grc9v3.completion_evidence`
3. `cached_quantities.last_completed_hybrid_spark`
4. snapshot `basin_attributes.hierarchy`, `basin_attributes.nodes`, and
   `basin_attributes.expansion_registry`

Reports should use `completed_identity_event` for interpretation. The runtime
event kind `hybrid_spark_completed` may be cited exactly, but the event alone
must not be treated as proof of persistent identity beyond its recorded child
basin evidence.

## Snapshot / Checkpoint Robustness Audit

The current `GRC9V3.snapshot()` / `GRC9V3.load()` format uses the standard
snapshot groups:

- `metadata`
- `topology`
- `basin_attributes`
- `edge_labels`
- `dynamics`
- `observables`
- `events`
- `caches`

Robust extractors should:

- accept missing optional groups and mark affected fields `partial` or
  `blocked`,
- validate `metadata.model_family == "grc9v3"` when available,
- validate `metadata.params_hash` / `dynamics.state.params_identity` consistency
  when both are available,
- sort checkpoints by `(step_index, time, checkpoint_label, checkpoint_id)`,
- sort node ids, edge ids, port ids, and event ids numerically where possible,
- reject stale endpoint references only in extractor validation, not by
  mutating checkpoint payloads,
- preserve raw ids and source paths in every extracted table.

Telemetry artifact packs may also carry graph-checkpoint
`family_extensions["grc9v3"]` overlays for visualization. Those overlays are
secondary convenience surfaces. The runtime snapshot groups above are the
source of truth for `GRC9V3.snapshot()` and `GRC9V3.load()`.

### `metadata`

Useful for:

- model family,
- step index,
- params,
- resolved params,
- params hash,
- capabilities,
- rng state,
- next node id,
- next edge id.

### `topology`

Useful for:

- live node ids,
- live edge ids,
- endpoint slots,
- incidence,
- port occupancy,
- port-history reconstruction.

Endpoint slots should be converted through `slot_to_port_id` before applying
GRC9V3 row/column interpretation.

### `basin_attributes`

Useful for:

- `coherence`
- `gradient_row_basis`
- `signed_hessian_row_basis`
- `net_flux_summary`
- `basin_id`
- `parent_id`
- `depth`
- `basin_mass`
- `hierarchy`
- `expansion_registry`

If only scalar telemetry fields such as `gradient_norm` or
`min_signed_hessian` are available, mark vector-level evidence `partial` rather
than reconstructing vectors from summaries.

### `edge_labels`

Useful for:

- `base_conductance`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`
- `edge_label_computation_mode`
- `edge_label_params`

`edge_labels` does not replace topology endpoint records. It annotates edge ids
that must still be resolved through `topology`.

### `dynamics`

Useful for:

- `dynamics.state.step_index`
- `dynamics.state.time`
- `dynamics.state.sink_set`
- `dynamics.state.basins`
- `dynamics.state.port_edges`
- `dynamics.state.potential`
- `dynamics.state.cached_quantities`
- `dynamics.state.params_identity`

`port_edges[*].flux_uv` is the signed flux carrier for orientation-aware
reports. If only `edge_labels.flux_coupling` exists, reports may use absolute
flux as a non-oriented magnitude only. They must not infer signed orientation
from absolute flux.

### `events`

Useful for:

- candidate payloads,
- expansion payloads,
- completion payloads,
- event step index,
- event source family.

Event payloads are the primary source for spark-gate traces when available.

### `caches`

Useful for:

- `coarse_cache`.

Most runtime cached quantities are serialized under `dynamics.state`, not the
top-level `caches` group.

## Full Port-History Reconstruction

Full port history is reconstructed only from an ordered snapshot/checkpoint
sequence plus topology endpoint records, `dynamics.state.port_edges`, and
`edge_labels`.

For each checkpoint:

1. read all live edges and endpoint slots from `topology`,
2. compute local `(node_id, port_id)` from endpoint slots via `slot_to_port_id`,
3. attach available `edge_labels` and `dynamics.state.port_edges[*].flux_uv`,
4. record occupancy for all ports 1 through 9 per live node,
5. emit a row keyed by `(run_id, checkpoint_id, step_index, time, node_id,
   port_id, edge_id)`.

Rules:

- no interpolation between checkpoints,
- no inferred signed flux when only absolute flux is available,
- missing checkpoints create partial windows,
- topology changes split the history into before/after segments,
- expansion event payloads define reassignment evidence when available.

## Deterministic Artifact Reports

Artifact reports should be deterministic:

- write canonical JSON with sorted keys,
- sort rows by stable ids,
- include schema id and source document version,
- include input artifact paths and source priority decisions,
- include blocked observation rows,
- avoid wall-clock timestamps in deterministic outputs,
- store floats as finite JSON numbers or explicit `null` when unavailable,
- write CSV columns in declared schema order.

Recommended report paths:

- `outputs/grc9v3/hessian_readiness/lane_a_spark_gate_traces.jsonl`
- `outputs/grc9v3/hessian_readiness/artifact_extraction_audit.md`
- `outputs/grc9v3/hessian_readiness/blocked_observations.csv`

These are future extractor outputs. Iteration 4 does not produce these files.

## Golden-Run Boundary

Iteration 4 does not add runtime artifact fields. The Iteration 1 golden-run
event/state digest remains the semantic baseline.

If future extractor code is added, it must either:

- reproduce the same golden-run state/event digests, or
- explicitly report that only non-semantic artifact fields were added.

## Iteration 4 Outcome

The artifact surface is now specified well enough for extraction work to start
without blurring direct runtime evidence, derived analysis evidence, and blocked
claims.
