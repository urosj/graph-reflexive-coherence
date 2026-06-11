# Phase T GRC9V3 Telemetry Contract

## Purpose

This document records the first explicit telemetry contract for the
`GRC9V3` hybrid family.

The shared telemetry core remains unchanged:

- step rows,
- event rows,
- run summaries,
- reports,
- optional graph checkpoints.

`GRC9V3` adds family-specific payloads only through:

```text
family_extensions["grc9v3"]
```

The first contract version is:

```text
phase_t_grc9v3_iter1_v1
```

## Family Key

- family key: `grc9v3`
- contract version: `phase_t_grc9v3_iter1_v1`

Expected implementation module:

- `src/pygrc/telemetry/grc9v3_contract.py`

Expected private builder module:

- `src/pygrc/telemetry/_grc9v3_extensions.py`

Expected public helpers:

- `grc9v3_step_family_extensions(...)`
- `grc9v3_event_family_extensions(...)`
- `grc9v3_run_summary_family_extensions(...)`
- `classify_grc9v3_event_extension(...)`

## Availability Convention

Paper-facing and future-facing fields must use explicit availability:

- `artifact_backed`
- `diagnostic_only`
- `reserved_future`
- `out_of_scope`

Examples:

- row-basis gradients are `artifact_backed`;
- weighted least-squares Hessian is `artifact_backed` when selected or cached
  as the comparison backend;
- `temporal_delay` is an analytic edge label, not a causal-layer claim;
- barrier/ghost boundary behavior is `reserved_future`;
- GRCL/source-seed lowering is `out_of_scope` for this telemetry contract.

## Ownership Convention

Each payload group should be interpretable as one of:

- `grc9_mechanical`,
- `grcv3_semantic`,
- `grc9v3_hybrid`.

The contract should prefer explicit `ownership` or group-level interpretation
notes over silent reuse.

## Step-Row Extension Payload

Each step row should carry:

- `contract_version`
- `lane_context`
- `backend_config`
- `port_chart`
- `row_basis_differential`
- `hybrid_tensor`
- `transport`
- `identity_basin`
- `hybrid_spark_state`
- `hierarchy_state`
- `choice_collapse`
- `growth_state`
- `budget_correction`
- `coarse_cache`

### `lane_context`

Required fields:

- `source_reference`
- `fixture_name`
- `run_role`

Optional fields:

- `experiment_id`
- `representative_lane_name`
- `source_runtime_artifact`

Interpretation:

- `source_runtime_artifact`, when present, may point to the Phase 7 runtime
  evidence fixture, but the telemetry row itself must use the GRC9V3 telemetry
  contract.

Ownership:

- `shared_runtime`

### `backend_config`

Required fields:

- `frame_mode`
- `hessian_backend`
- `curvature_backend`
- `choice_backend`
- `boundary_mode`
- `quadrature_mode`
- `budget_correction_method`
- `expansion_distribution_mode`
- `edge_label_selection`
- `spark_signed_crossing`

Optional fields:

- `spark_lane`
- `spark_lane_version`
- `default_evolution_provenance`
- `reserved_modes`

Interpretation:

- `frame_mode = "fixed_port_chart"` is the core Phase 7 baseline.
- `boundary_mode = "prune"` is currently artifact-backed.
- `barrier` and `ghost` are reserved until runtime capability support exists.
- `spark_lane`, when present, records the configured spark predicate lane for
  the run. The default Lane A value is `current_hybrid_signed_hessian`; opt-in
  Lane B is `grc9v3_column_h_assisted`.
- `spark_lane` is configuration evidence, not candidate evidence. Candidate
  causality still comes from `hybrid_spark_candidate` payloads and checkpoint
  overlays.

Ownership:

- `shared_runtime`

### `port_chart`

Required fields:

- `num_nodes`
- `num_port_edges`
- `active_degree_histogram`
- `inactive_port_count`
- `saturated_node_count`
- `saturated_node_ids_sample`
- `row_occupancy_totals`
- `column_occupancy_totals`

Optional fields:

- `inactive_capacity_by_node_sample`
- `module_node_count`

Ownership:

- `grc9_mechanical`

### `row_basis_differential`

Required fields:

- `gradient_norm_min`
- `gradient_norm_max`
- `gradient_norm_mean`
- `signed_hessian_min`
- `signed_hessian_max`
- `signed_hessian_mean`
- `current_min_signed_hessian_min`
- `hessian_backend`
- `hessian_sign`

Optional fields:

- `previous_min_signed_hessian_available`
- `signed_hessian_history_pruned_count`
- `weighted_least_squares_hessian_available`
- `geometric_seed_count`

Ownership:

- `grcv3_semantic` in a GRC9V3 row basis.

Interpretation:

- `hessian_sign` is an artifact-backed runtime convention cached by the
  differential rebuild. It is not expected to vary step-by-step in normal
  representative runs.
- `hessian_backend` records the backend that drives signed-Hessian semantics.
- `weighted_least_squares_hessian_available` records whether the comparison
  diagnostic cache is present. It does not imply that weighted least squares is
  the active signed-Hessian backend.

### `hybrid_tensor`

Required fields:

- `tensor_trace_min`
- `tensor_trace_max`
- `tensor_trace_mean`
- `tensor_anisotropy_max`
- `row_mismatch_sum_max`
- `flux_feedback_sum_mean`

Optional fields:

- `tensor_hotspot_node_ids_sample`
- `row_mismatch_hotspot_node_ids_sample`

Ownership:

- `grc9v3_hybrid`

Interpretation:

- This is the GRC9 Eq. (1) tensor expressed in the fixed GRC9V3 row basis.
- It is not a claim of unrestricted continuum tensor geometry.

### `transport`

Required fields:

- `base_conductance_min`
- `base_conductance_max`
- `base_conductance_mean`
- `potential_min`
- `potential_max`
- `flux_abs_sum`
- `positive_flux_edge_count`
- `negative_flux_edge_count`
- `label_availability`
- `label_computation_mode`

`label_availability` should contain:

- `geometric_length_available`
- `temporal_delay_available`
- `flux_coupling_available`

Interpretation:

- `temporal_delay` remains an analytic label.
- Scalar base conductance remains the dynamical transport weight.

### `identity_basin`

Required fields:

- `sink_count`
- `basin_count`
- `basin_size_min`
- `basin_size_max`
- `basin_size_mean`
- `geometric_seed_count`
- `validated_basin_count`
- `successor_self_loop_count`

Optional fields:

- `successor_tie_count`
- `basin_mass_summary`
- `module_sink_count`
- `daughter_sink_count`

Ownership:

- `grc9v3_hybrid`

### `hybrid_spark_state`

Required fields:

- `hybrid_spark_candidate_count`
- `completed_hybrid_spark_count`
- `last_candidate_saturation_gate`
- `last_candidate_basin_interior_gate`
- `last_candidate_signed_hessian_gate`
- `last_child_stabilization_pass`

Optional fields:

- `signed_crossing_status`
- `last_candidate_gradient_norm`
- `last_candidate_min_signed_hessian`
- `last_candidate_spark_lane`
- `last_candidate_column_h`
- `last_candidate_min_abs_column_h`
- `last_candidate_min_abs_column_h_column`
- `last_candidate_column_h_branch_hit`
- `last_candidate_column_h_gate_reasons`
- `evaluated_candidate_count`
- `candidate_pass_rate`
- `candidate_failure_reason`
- `last_stabilized_child_node_ids`
- `last_module_sink_node_ids`

Ownership:

- `grc9v3_hybrid`

Interpretation:

- Candidate, expansion, and completed spark are different lifecycle states.
- Lane A candidates remain backward-compatible and do not require Lane B-only
  column-H fields.
- Lane B direct column-H proxy-branch evidence is present only when
  `last_candidate_spark_lane == "grc9v3_column_h_assisted"` and the candidate
  event payload records a column-H branch reason.
- Completed spark requires post-expansion child-basin or attractor gain.
- `candidate_failure_reason` should be populated when evaluated candidate
  surfaces exist but no candidate passes all gates.

### `hierarchy_state`

Required fields:

- `hierarchy_root_count`
- `hierarchy_child_link_count`
- `max_hierarchy_depth`

Optional fields:

- `last_hierarchy_parent`
- `last_hierarchy_children`

Ownership:

- `grcv3_semantic` updated by GRC9V3 hybrid sparks.

### `choice_collapse`

Required fields:

- `choice_backend`
- `choice_regime_count`
- `collapse_registry_count`
- `evaluated_node_count`
- `learning_state_count`

Optional fields:

- `last_choice_node_id`
- `last_collapse_node_id`
- `last_collapsed_sink_id`
- `epsilon_choice`
- `epsilon_collapse`

Ownership:

- `grcv3_semantic` evaluated over GRC9 port-flux successors.

### `growth_state`

Required fields:

- `birth_rule_mode`
- `parent_selection_mode`
- `growth_event_count`

Optional fields:

- `last_parent_node_id`
- `last_child_node_id`
- `last_birth_probability`
- `last_outward_flux_pressure`

Ownership:

- `grc9_mechanical` with `grcv3_semantic` state updates.

### `budget_correction`

Required fields:

- `quadrature_mode`
- `budget_correction_method`
- `budget_target`
- `budget_before`
- `budget_after`
- `budget_error`
- `negative_mass_correction`

Optional fields:

- `post_expansion_budget_check_available`
- `budget_target_source`

Ownership:

- `grcv3_semantic` budget interpretation over the GRC9V3 graph.

### `coarse_cache`

Required fields:

- `coarse_cache_state`
- `coarse_cache_invalidated`
- `coarse_cache_invalidation_reason`

Optional fields:

- `coarse_cache_refresh_mode`
- `coarse_fields_list`
- `coarse_field_types`

Ownership:

- shared runtime/cache hygiene, with GRC9 column/coarse implications.

Interpretation:

- `coarse_cache_invalidation_reason` remains the primary cache-hygiene signal.
- `coarse_cache_refresh_mode = operator_backed` means the public
  `GRC9V3.coarse_grain_columns(...)` operator populated the cache.
- `coarse_fields_list` records the warm operator-backed fields, such as
  `conductance` or `signed_flux`.
- `coarse_field_types` records the corresponding Split mode class:
  `nonnegative`, `signed_lossless`, or `unknown`.

## Event-Row Extension Payload

Each event row should carry:

- `contract_version`
- `lane_context`
- `event_domain`
- `lifecycle_stage`
- `ownership`
- `topology_mutation`
- `hierarchy_mutation`
- `budget_mutation`

Optional subject fields:

- `primary_node_id`
- `primary_edge_id`
- `registry_key`
- `expansion_id`

### Event Domains

- `spark`
- `expansion`
- `choice`
- `collapse`
- `growth`
- `budget`
- `coarse`
- `boundary`
- `other`

### Lifecycle Stages

- `candidate`
- `module_created`
- `completed`
- `detected`
- `resolved`
- `collapsed`
- `child_attached`
- `corrected`
- `invalidated`
- `other`

Unknown event kinds should classify to:

- `event_domain = "other"`
- `lifecycle_stage = "other"`

### Classification Table

- `hybrid_spark_candidate` -> `spark` / `candidate`
- `hybrid_mechanical_expansion` -> `expansion` / `module_created`
- `hybrid_spark_completed` -> `spark` / `completed`
- `choice_detected` -> `choice` / `detected`
- `choice_resolved` -> `choice` / `resolved`
- `collapse` -> `collapse` / `collapsed`
- `growth` -> `growth` / `child_attached`

### Event Ownership Table

- `spark` / `candidate` -> `grc9v3_hybrid`
- `expansion` / `module_created` -> `grc9_mechanical`
- `spark` / `completed` -> `grc9v3_hybrid`
- `choice` / `detected` -> `grcv3_semantic`
- `choice` / `resolved` -> `grcv3_semantic`
- `collapse` / `collapsed` -> `grcv3_semantic`
- `growth` / `child_attached` -> `grc9_mechanical`
- `budget` / `corrected` -> `grcv3_semantic`
- `coarse` / `invalidated` -> `shared_runtime`
- `boundary` / `other` -> `shared_runtime`
- unknown domain/stage pairs -> `shared_runtime`

Interpretation:

- growth mutates the GRC9 port graph and also updates GRCV3-style node state;
  its event ownership is mechanical, with semantic state updates recorded in
  the evidence payload.
- `hybrid_spark_candidate` is a shared event kind. Consumers must use the
  payload field `spark_lane`, when present, to distinguish Lane B
  `grc9v3_column_h_assisted` candidates from default Lane A candidates.
- budget events are owned by the GRCV3 semantic budget interpretation over the
  GRC9V3 graph.

### Spark Evidence

Spark event extensions should include when available:

- `candidate_node_id`
- `sink_node_id`
- `active_degree`
- `saturation_gate`
- `basin_interior_gate`
- `gradient_norm`
- `signed_hessian_degeneracy_gate`
- `min_signed_hessian`
- `signed_crossing_enabled`
- `signed_crossing_gate`
- `depth`
- `spark_lane`
- `spark_lane_version`
- `candidate_event_id`
- `state_epoch`
- `column_h_computation_version`
- `column_h`
- `min_abs_column_h`
- `min_abs_column_h_column`
- `eps_column_h`
- `column_h_threshold_hit`
- `column_h_sign_crossing_enabled`
- `column_h_sign_crossing_mode`
- `eps_column_h_crossing_zero`
- `previous_column_h_status`
- `previous_column_h_values`
- `column_h_sign_crossing_hit`
- `column_h_sign_crossing_columns`
- `column_h_branch_hit`
- `lane_b_candidate_hit`
- `gate_reasons`
- `near_saturation_enabled`
- `virtual_stubs_used`
- `linked_expansion_event_id`

Interpretation:

- Lane A candidates may omit Lane B-only fields and remain backward-compatible.
- Lane B candidates reuse the `hybrid_spark_candidate` event kind. Consumers
  must use `spark_lane`, not event kind alone, to distinguish Lane A from Lane
  B.
- `lane_b_candidate_hit` means the full Lane B v1 predicate fired.
- `column_h_branch_hit` means the direct runtime-computed column-H proxy branch
  fired. A Lane B signed-Hessian-only candidate can have
  `lane_b_candidate_hit = true` and `column_h_branch_hit = false`.
- `gate_reasons` is the branch-attribution surface. It should distinguish
  `signed_hessian_hit`, `column_h_threshold_hit`, and
  `column_h_sign_crossing_hit`.
- Lane B direct evidence means direct runtime evidence that the column-H proxy
  branch fired. `H_s[b]` remains a proxy, not the true geometric Hessian.

### Expansion Evidence

Expansion event extensions should include when available:

- `parent_sink_id`
- `target_effective_degree`
- `requested_node_count`
- `module_node_ids`
- `internal_edge_ids`
- `distribution_weights`
- `core_coherence_fraction`
- `core_coherence`
- `budget_before`
- `budget_after`
- `budget_error`
- `budget_preservation_path`
- `reassignment_count`

### Completion Evidence

Completed hybrid spark extensions should include when available:

- `stabilized_child_node_ids`
- `stable_child_basin_count`
- `hierarchy_parent`
- `hierarchy_children`

### Choice / Collapse Evidence

Choice and collapse extensions should include when available:

- `node_id`
- `viable_sink_ids`
- `winner_sink_id`
- `winner_margin`
- `collapsed_sink_id`
- `epsilon_choice`
- `epsilon_collapse`
- `persistence_mode`

### Growth Evidence

Growth extensions should include when available:

- `parent_node_id`
- `child_node_id`
- `parent_port_id`
- `child_port_id`
- `outward_flux_pressure`
- `birth_probability`
- `rng_sample`
- `coherence_transfer`

## Run-Summary Extension Payload

Each run summary should carry:

- `contract_version`
- `lane_context`
- `backend_summary`
- `final_port_chart_summary`
- `final_differential_summary`
- `final_identity_basin_summary`
- `final_hierarchy_summary`
- `final_choice_collapse_summary`
- `final_budget_summary`
- `lifecycle_event_counts`
- `representative_appendix_e_summary`

### `lifecycle_event_counts`

Required fixed fields:

- `hybrid_spark_candidate_count`
- `hybrid_mechanical_expansion_count`
- `hybrid_spark_completed_count`
- `choice_detected_count`
- `choice_resolved_count`
- `collapse_count`
- `growth_count`
- `budget_correction_count`
- `coarse_invalidation_count`
- `boundary_event_count`

### `representative_appendix_e_summary`

Required fields when the representative fixture is used:

- `fixture_name`
- `spark_completed`
- `daughter_sink_count`
- `daughter_sink_node_ids`
- `module_basin_mass`
- `hierarchy_parent`
- `hierarchy_children`
- `budget_preserved`
- `replay_digest_match`

Interpretation:

- This summary is valid for the representative Appendix E fixture only.
- General GRC9V3 phenomenology discovery belongs outside this telemetry
  contract. It has since been implemented as a downstream discovery track.

## Graph Checkpoint Extension Payload

Graph checkpoint `family_extensions["grc9v3"]` may include:

- `node_overlay`
- `port_overlay`
- `edge_overlay`
- `module_overlay`
- `choice_overlay`

### `node_overlay`

Recommended fields per node:

- `coherence`
- `gradient_norm`
- `min_signed_hessian`
- `basin_id`
- `parent_id`
- `depth`
- `is_sink`
- `is_geometric_seed`
- `is_module_node`
- `spark_lane`
- `column_h_computation_version`
- `column_h`
- `min_abs_column_h`
- `min_abs_column_h_column`
- `column_h_branch_hit`
- `column_h_gate_reasons`
- `column_h_diagnostic_source`

Interpretation:

- `column_h_diagnostic_source = "latest_candidate_event"` means the overlay is
  backed by candidate-event evidence.
- `column_h_diagnostic_source = "current_column_h_cache"` means the overlay is
  diagnostic state from the current column-H cache and should not by itself be
  interpreted as a candidate gate.
- Checkpoint overlays support visual inspection and replay. Candidate payloads
  remain the primary causal evidence for spark-gate claims.

### `port_overlay`

Recommended fields:

- occupied/free slot state,
- row totals,
- column totals,
- saturation flag.

### `edge_overlay`

Recommended fields per edge:

- `base_conductance`
- `flux_uv`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`

### `module_overlay`

Recommended fields:

- expansion id,
- parent sink id,
- module node ids,
- module sink ids,
- stabilized child node ids.

### `choice_overlay`

Recommended fields:

- choice-regime nodes,
- viable sink ids,
- collapsed nodes,
- learned basin ids.

## Compression Rules

Step rows and run summaries must stay compact:

- no full per-node vectors in step rows,
- no full tensor matrices in step rows,
- no full successor map in summaries,
- no full port occupancy matrix in every step row unless explicitly sampled.

Full graph-local detail belongs in checkpoints.

## Boundary Rules

This contract does not claim:

- Phase V-GRC9V3 visualization,
- GRC9V3 phenomenology discovery,
- reviewed GRC9V3 motif catalogs,
- GRCL/source-seed lowering for GRC9V3,
- barrier/ghost boundary behavior,
- Lorentzian causal semantics,
- anisotropic edge transport,
- multiscale sigma fields,
- non-unit quadrature measures,
- or adiabatic expansion execution.

Downstream note: Phase V-GRC9V3 visualization, GRC9V3 phenomenology discovery,
reviewed catalogs, and GRCL-9V3 source lowering are now complete as separate
tracks. This does not change the telemetry contract boundary.

Those surfaces require later contracts or contract versions.
