# Phase T GRC9 Telemetry Contract

## Purpose

This note records the explicit `GRC9` telemetry extension contract for
**Phase T-GRC9: GRC9 Mechanical Telemetry Extension**.

The shared telemetry core remains unchanged:

- step rows
- event rows
- run summaries
- experiment reports
- comparison reports
- optional graph checkpoints

`GRC9` adds family-specific payloads only through:

- `family_extensions["grc9"]` on step rows
- `family_extensions["grc9"]` on event rows
- `family_extensions["grc9"]` on run summaries
- `family_extensions["grc9"]` on graph checkpoint artifacts when checkpoint
  export is enabled

The first extended contract version for this phase is:

- `phase_t_grc9_iter1_v1`

This contract is paper-facing. It is meant to expose GRC9-specific mechanical
phenomenology from `papers/2026-04-GRC-9.md`, not merely preserve the compact
closeout metadata from Phase 6.

## Family Key

- family key: `grc9`
- contract version: `phase_t_grc9_iter1_v1`

The implementation target for the typed contract is:

- `src/pygrc/telemetry/grc9_contract.py`

Expected public helpers:

- `grc9_step_family_extensions(...)`
- `grc9_event_family_extensions(...)`
- `grc9_run_summary_family_extensions(...)`
- `classify_grc9_event_extension(...)`

The shared recorder should remain family-agnostic.

## Relationship To Phase 6 Contract

The compact Phase 6 contract remains valid historical closeout evidence:

- old contract version: `phase6_iter10_v1`
- recorded in:
  - [`Phase-6-GRC9-TelemetryContract.md`](./Phase-6-GRC9-TelemetryContract.md)
  - [`Phase-6-GRC9-RepresentativeTelemetry.md`](./Phase-6-GRC9-RepresentativeTelemetry.md)

Phase 6 used one compact `family_extensions["grc9"]` payload copied onto step
rows and event rows, plus a small summary-only addition:

- `contract_version`
- `lane_name` or `profile_name`
- `role` for representative `primary` / `replay`
- `abundance_contract`
- `source_reference`
- `seed_source_reference` for seed-driven lanes
- `source_lowering_mode` for seed-driven lanes
- `final_expansion_count` on run summaries

Phase T-GRC9 keeps those fields as lane/provenance context where applicable,
but expands the payload into typed mechanical summaries.

The old `phase6_iter10_v1` artifacts should not be retroactively rewritten or
reinterpreted as if they emitted this contract.

## Availability Convention

The contract distinguishes four statuses for paper-facing fields:

- `artifact_backed`: computed and emitted from current saved artifacts
- `diagnostic_only`: computed as an observational diagnostic, not a core
  runtime claim
- `reserved_future`: named for a paper-facing surface that needs later runtime
  or source work
- `out_of_scope`: explicitly not a GRC9 core telemetry claim

When a field group contains future-facing data, the payload should prefer an
explicit status field over silent omission.

Recommended status fields:

- `availability`
- `diagnostic_status`
- `reserved_reason`

Examples:

- `boundary_mode = "barrier"` remains `reserved_future` until the runtime
  implements barrier behavior and advertises the corresponding capability.
- Lorentzian causal-cone telemetry is `out_of_scope`; `temporal_delay` remains
  an analytic label only.
- `source_lowering_mode = "structural_graph_graft_v1"` must not be read as a
  full `GRCL-9` source implementation.

## Shared Lane Context

Every `GRC9` family extension payload should include a compact lane context.

Required fields:

- `contract_version`
- `abundance_contract`
- `source_reference`

Representative-lane fields:

- `lane_name`
- `role`

Seed-driven structural-lane fields:

- `profile_name`
- `seed_source_reference`
- `source_lowering_mode`

Interpretation:

- `abundance_contract` remains:
  - `topology_updated_current_flux_diagnostic`
- `source_lowering_mode`, when present, remains:
  - `structural_graph_graft_v1`
- the seed-driven structural lane is not `GRCL-9`
- neither lane is `GRC9V3`

## Step-Row Extension Payload

Each step row should carry:

- `contract_version`
- `lane_context`
- `backend_config`
- `port_chart`
- `row_tensor`
- `column_diagnostic`
- `transport`
- `identity_abundance`
- `coarse_graining`
- `budget_correction`

### `backend_config`

Required fields:

- `frame_mode`
- `curvature_backend`
- `metric_backend`
- `spark_backend`
- `birth_backend`
- `growth_parent_eligibility_mode`
- `coarse_graining_backend`
- `boundary_mode`
- `budget_preservation_policy`
- `expansion_distribution_mode`
- `expansion_schedule`
- `edge_label_selection`

Optional fields:

- `source_lowering_mode`
- `expansion_schedule_tau`
- `reserved_modes`

Interpretation:

- `frame_mode` should be `fixed_port_chart` for the Phase T-GRC9 baseline.
- `expansion_distribution_mode` records the policy behind Eq. (16).
- `budget_preservation_policy` records configured policy. The actual
  correction path belongs in `budget_correction`.
- `growth_parent_eligibility_mode` distinguishes historical broad inactive-port
  growth from paper-facing front-capacity growth.
- `expansion_schedule` should be `instantaneous` unless adiabatic expansion is
  actually implemented.
- `boundary_mode = "barrier"` and `boundary_mode = "ghost"` are reserved until
  implemented.

### `port_chart`

Required fields:

- `num_nodes`
- `num_port_edges`
- `active_degree_histogram`
- `inactive_port_count`
- `saturated_node_count`
- `near_saturated_node_count`
- `row_occupancy_totals`
- `column_occupancy_totals`

Optional fields:

- `saturated_node_ids_sample`
- `inactive_capacity_by_column`

Interpretation:

- rows and columns must stay separate.
- full per-port occupancy should be checkpoint data, not mandatory step-row
  data.

### `row_tensor`

Required fields:

- `row_tensor_min`
- `row_tensor_max`
- `row_tensor_mean`
- `row_tensor_anisotropy_max`
- `density_term_mean`
- `row_mismatch_term_max`
- `flux_feedback_term_mean`

Optional fields:

- `row_mismatch_hotspots`
- `row_tensor_by_node_sample`

Interpretation:

- this is the compressed telemetry surface for Eq. (1).
- it reports the reduced three-row GRC9 tensor basis.
- it must not imply unrestricted continuum tensor freedom.

### `column_diagnostic`

Required fields:

- `column_diagnostic_min_abs`
- `column_diagnostic_mean_abs`
- `column_proxy_candidate_count`
- `sign_crossing_candidate_count`
- `column_profile_sparsity`

Optional fields:

- `column_diagnostic_by_candidate`
- `column_diagnostic_hotspots`
- `spark_calibration`

`spark_calibration`, when present, should contain:

- `spark_threshold`
- `spark_threshold_mode`
- `burn_in_M_H`
- `burn_in_M_C`

Interpretation:

- this is the compressed telemetry surface for Eq. (11) and the column-proxy
  branch of Eq. (12).
- calibration fields are diagnostic unless the run actually used calibrated
  threshold selection.

### `transport`

Required fields:

- `conductance_min`
- `conductance_max`
- `conductance_mean`
- `flux_abs_sum`
- `flux_signed_balance`
- `positive_flux_edge_count`
- `negative_flux_edge_count`
- `strongest_flux_edges_sample`

Optional fields:

- `potential_min`
- `potential_max`
- `potential_range`
- `label_availability`
- `label_computation_mode`

`label_availability` should include:

- `overall`
- `geometric_length_available`
- `temporal_delay_available`
- `flux_coupling_available`

`label_computation_mode` should include per-label modes when available.

Interpretation:

- conductance remains the single dynamical edge weight.
- analytic labels remain labels, not extra dynamical weights.
- `temporal_delay` is not a Lorentzian proper-time claim.

### `identity_abundance`

Required fields:

- `sink_count`
- `basin_count`
- `basin_size_min`
- `basin_size_max`
- `basin_size_mean`
- `abundance_contract`

Optional fields:

- `scale_weighted_abundance`
- `scale_weighted_abundance_gamma`
- `successor_self_loop_count`
- `successor_tie_count`
- `successor_tie_break_policy`
- `basin_mass_summary`

Interpretation:

- `scale_weighted_abundance` is the telemetry surface for Eq. (17).
- successor ties should use the Phase 6 deterministic tie-break rule.

### `coarse_graining`

Required fields:

- `coarse_fields_list`
- `coarse_cache_state`
- `coarse_cache_invalidation_reason`
- `exact_split_supported_fields`
- `signed_flux_mode`

Optional fields:

- `coarse_field_types`
- `max_reconstruction_error_by_field`
- `column_total_sparsity_by_field`
- `dominant_mode_profile_count`
- `profile_compression_mode`

`coarse_field_types` should distinguish:

- `nonnegative`
- `signed_lossless`
- `signed_compressed`

`profile_compression_mode` should distinguish:

- `full`
- `dominant_index_residual`
- `custom`

Interpretation:

- exact Split claims require reconstruction checks.
- compressed signed-flux mode must be labeled non-exact if added later.

### `budget_correction`

Required fields:

- `budget_current`
- `budget_target`
- `budget_error`
- `budget_preservation_policy`
- `last_budget_correction_path`

Optional fields:

- `uniform_shift_delta`
- `simplex_projection_applied`
- `negative_clamp_count`

Interpretation:

- configured budget policy is not enough; telemetry should record the actual
  correction path taken by the step when available.
- if the runtime uses a uniform correction with positivity-preserving fallback,
  the fallback must be observable.

## Event-Row Extension Payload

Each event row should carry:

- `contract_version`
- `lane_context`
- `event_domain`
- `lifecycle_stage`
- `topology_mutation`
- `port_mutation`
- `budget_mutation`

Optional subject fields:

- `primary_node_id`
- `primary_edge_id`
- `registry_key`

Event domains:

- `spark`
- `expansion`
- `growth`
- `coarse`
- `budget`
- `boundary`
- `other`

Lifecycle stages:

- `candidate`
- `confirmed`
- `fission_confirmed`
- `module_created`
- `boundary_reassigned`
- `child_attached`
- `invalidated`
- `corrected`
- `other`

Unknown event kinds should classify to:

- `event_domain = "other"`
- `lifecycle_stage = "other"`

### Spark Evidence

Spark event extensions should include when available:

- `spark_kind`
- `active_degree`
- `saturation_gate_pass`
- `instability_score`
- `instability_gate_pass`
- `column_proxy_min_abs`
- `column_proxy_gate_pass`
- `sign_crossing_gate_pass`
- `trigger_column`
- `predicted_D_eff`
- `predicted_module_size`
- `predicted_satellite_count`

Interpretation:

- spark evidence captures why the chart failed.
- predicted module fields describe expected refinement, not the completed
  topology mutation.

### Expansion Evidence

Expansion event extensions should include when available:

- `parent_sink_id`
- `target_effective_degree`
- `module_size_formula`
- `module_node_count`
- `core_node_id`
- `satellite_node_ids`
- `helper_node_ids`
- `reassigned_edge_count`
- `reassigned_edge_count_by_column`
- `internal_edge_count`
- `coherence_transfer_mode`
- `coherence_transfer_ratios`
- `coherence_transfer_ratios_sum`
- `bond_weight_mode`
- `bond_weight`
- `internal_conductance_stats`
- `expansion_schedule`
- `expansion_substeps`
- `budget_preserved_by_construction`

Interpretation:

- expansion telemetry captures the mechanical refinement action.
- `coherence_transfer_ratios` should be a length-3 sequence when present.
- `coherence_transfer_ratios_sum` should be close to `1.0` when ratios are
  emitted.
- `module_size_formula` should identify the Eq. (13) policy or implementation
  variant used.

### Growth Evidence

Growth event extensions should include when available:

- `parent_node_id`
- `child_node_id`
- `selected_parent_port`
- `child_port`
- `parent_selection_mode`
- `parent_eligibility_mode`
- `parent_capacity_source`
- `front_growth_provenance_present`
- `legacy_broad_growth`
- `outward_flux_pressure`
- `birth_rule`
- `birth_probability`

Interpretation:

- selected-port telemetry is GRC9-specific and should show lowest inactive
  port selection.
- `parent_eligibility_mode = "grc9_front_capacity"` plus non-legacy
  `parent_capacity_source` is the corrected paper-facing front-growth signal.
- `legacy_broad_growth = true` marks historical broad inactive-port growth as
  diagnostic, not accepted paper-facing growth.
- `birth_probability` reports the evaluated Section 8.4 birth rule when
  available.

### Budget Evidence

Budget event extensions should include when available:

- `budget_preservation_policy`
- `correction_path`
- `uniform_shift_delta`
- `simplex_projection_applied`
- `budget_error_before`
- `budget_error_after`

## Run-Summary Extension Payload

Each run summary should carry:

- `contract_version`
- `lane_context`
- `backend_summary`
- `final_port_chart_summary`
- `final_row_tensor_summary`
- `final_column_diagnostic_summary`
- `final_transport_summary`
- `final_identity_summary`
- `final_coarse_graining_summary`
- `lifecycle_event_counts`
- `expansion_summary`
- `growth_summary`

Optional groups:

- `calibration_summary`
- `diagnostic_status_summary`

### `lifecycle_event_counts`

Required fields:

- `spark_candidate_count`
- `spark_confirmed_count`
- `spark_instability_count`
- `spark_column_proxy_count`
- `spark_sign_crossing_count`
- `expansion_count`
- `growth_count`
- `coarse_cache_invalidation_count`
- `budget_correction_count`
- `budget_uniform_correction_count`
- `budget_simplex_correction_count`

### `expansion_summary`

Required fields:

- `final_expansion_registry_size`
- `total_module_nodes_created`
- `total_boundary_reassignments`
- `max_module_node_count`
- `identity_fission_candidate_count`
- `identity_fission_confirmed_count`
- `identity_fission_max_persistence_steps`

Interpretation:

- identity fission is an observed post-expansion diagnostic.
- confirmed fission requires a persistence window and minimum basin-mass rule.
- this is not GRCV3 hierarchy tracking.

### `growth_summary`

Required fields:

- `growth_count`
- `unique_growth_parent_count`
- `lowest_port_attachment_count`
- `front_capacity_growth_count`
- `legacy_broad_growth_count`

Optional fields:

- `birth_probability_min`
- `birth_probability_max`
- `birth_probability_mean`

### `calibration_summary`

Required fields when present:

- `spark_threshold`
- `spark_threshold_mode`
- `burn_in_M_H`
- `burn_in_M_C`
- `spark_rate_observed`

Interpretation:

- calibration summaries are only required for lanes that actually perform or
  replay a calibration window.

## Graph Checkpoint Extension Payload

Graph checkpoints remain optional. When GRC9 checkpoint extensions are emitted,
they should use `family_extensions["grc9"]`.

### Node Overlays

Recommended fields:

- `active_degree`
- `row_occupancy`
- `column_occupancy`
- `coherence`
- `potential`
- `sink_role`
- `basin_id`
- `module_id`
- `module_role`

### Port Overlays

Recommended fields:

- `node_id`
- `port_id`
- `row`
- `column`
- `occupied`
- `incident_edge_id`

### Edge Overlays

Recommended fields:

- `edge_id`
- `endpoint_ports`
- `conductance`
- `oriented_flux`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`
- `internal_module_edge`
- `reassigned_boundary_edge`

### Module Overlays

Recommended fields:

- `module_id`
- `parent_sink_id`
- `core_node_id`
- `satellite_node_ids`
- `helper_node_ids`
- `internal_edge_ids`
- `reassigned_boundary_edge_ids_by_column`

## Migration From Current Code

Current GRC9 telemetry is assembled directly in
`src/pygrc/telemetry/experiments.py` using compact dictionaries.

Phase T-GRC9 should migrate to:

```text
src/pygrc/telemetry/
  grc9_contract.py
  _grc9_extensions.py
```

Expected migration steps:

1. Keep `capture_run_telemetry(...)` as the shared recorder.
2. Move contract constants into `grc9_contract.py`.
3. Build step payloads before capture and pass them through
   `step_family_extensions`.
4. Build event payloads before capture and pass them through
   `event_family_extensions_by_step`.
5. Build run-summary payloads and pass them through
   `summary_family_extensions`.
6. Keep compact Phase 6 lane reconstruction available where needed.
7. Write new extended artifacts under new lane/profile names.

The common schema does not need to know the internal shape of the GRC9 payload.
That validation belongs to the GRC9 contract dataclasses and tests.

## Boundary Rules

This contract does not claim:

- `GRC9V3` basin attributes
- hierarchy tracking
- choice/collapse semantics
- family-native `GRCL-9` source lowering
- signed-Hessian spark semantics as core GRC9 spark semantics
- Lorentzian causal cones or proper-time dynamics
- FRC scale-indexed coherence fields
- observer-local unpredictability

If later phases add those layers, they should introduce new contract versions or
new family extension groups rather than silently changing the meaning of
`phase_t_grc9_iter1_v1`.

GRCL-9 collapse-adjacent source probes do not change this contract. Current
GRC9 telemetry has no `collapse_evidence` group and no `collapse` lifecycle
domain. If a later review accepts GRC9-native structural-collapse diagnostics,
they should be added as diagnostic-only fields or a new contract version, while
preserving the historical meaning of `phase_t_grc9_iter1_v1`.

The Phase T-GRC9 collapse-adjacent observability review accepts only
selector-backed use of existing fields for the next GRCL-9 batch. In
particular:

- failed fission persistence may use existing `expansion_summary`
  identity-fission fields,
- sink/basin pressure may use existing `identity_abundance` fields and
  checkpoints,
- support pressure may use existing `transport` fields and checkpoints,
- membrane/ridge rupture remains structural/checkpoint-backed through GRCL-9
  provenance, not a generic GRC9 runtime semantic.

Reserved compact names such as `structural_integrity_summary`,
`basin_merge_candidate_count`, `sink_loss_candidate_count`,
`membrane_rupture_candidate_count`, `support_loss_candidate_count`, and
`collapse_candidate_summary` are not part of this contract version.
