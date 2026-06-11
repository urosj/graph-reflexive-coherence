# Phase T Experiments Refactor: Iteration 4A Test Inventory

## Purpose

Record the pre-split baseline, the one-to-one relocation map used in
Iteration 4A, and the public entry-point coverage preserved by the first-pass
test partition.

## Pre-Split Baseline

- Discovery command:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
- Pre-split discovered id count: `64`
- Pre-split discovery shape:
  - every id lived under `test_experiments.TelemetryRepresentativeExperimentTest.*`

This means the baseline relocation rule can stay simple:

- keep the same module: `test_experiments`
- keep the same `test_*` method names
- change only the owning test class according to the concern group below
- introduce no one-to-many replacements and no dropped tests

## Relocation Map

### `TelemetryRepresentativeExperimentTest`

Old prefix:
- `test_experiments.TelemetryRepresentativeExperimentTest.*`

New prefix:
- `test_experiments.TelemetryRepresentativeExperimentTest.*`

Methods kept in place:
- `test_run_grcv2_representative_experiment_emits_artifacts_and_reports`
- `test_run_grcv2_representative_experiment_defaults_to_behavior_only_artifacts`
- `test_run_grcv3_representative_experiment_emits_artifacts_and_replay_stable_reports`
- `test_run_grcv3_representative_experiment_can_emit_checkpoint_artifacts`
- `test_grcv3_representative_script_rejects_non_positive_steps`
- `test_grcv3_basin_summary_does_not_fallback_to_node_count`
- `test_grcv3_rich_v4_probe_transient_observability_is_emitted`

### `TelemetryFailureTraceTest`

Old prefix:
- `test_experiments.TelemetryRepresentativeExperimentTest.*`

New prefix:
- `test_experiments.TelemetryFailureTraceTest.*`

Relocated methods:
- `test_grcv3_rich_v4_path_failure_trace_identifies_geometry_failure`
- `test_grcv3_rich_v4_open_center_path_failure_trace_keeps_the_same_geometry_failure`
- `test_grcv3_rich_v4_asymmetric_center_coupling_trace_moves_the_path_lane_to_a_later_failure_mode`
- `test_grcv3_rich_v4_candidate_transition_trace_identifies_unsettled_candidate_sites`
- `test_grcv3_rich_v4_asymmetric_pair_mediation_trace_localizes_direct_candidate_site_but_not_path_settlement`
- `test_grcv3_rich_v4_mediated_spill_branch_trace_recovers_path_candidate_at_path_node`

### `TelemetrySettlementTraceTest`

Old prefix:
- `test_experiments.TelemetryRepresentativeExperimentTest.*`

New prefix:
- `test_experiments.TelemetrySettlementTraceTest.*`

Relocated methods:
- `test_grcv3_rich_v4_settlement_locus_regime_trace_distinguishes_carrier_and_path_regimes`
- `test_grcv3_rich_v4_explicit_settlement_regime_trace_matches_known_regimes`
- `test_grcv3_rich_v4_settlement_regime_decomposition_keeps_path_anchor_but_stops_later_migration`
- `test_grcv3_rich_v4_carrier_site_split_child_inheriting_does_not_open_new_regime`
- `test_grcv3_rich_v4_role_locked_spill_policy_closes_settlement_regimes`
- `test_grcv3_rich_v4_path_node_regime_is_topology_specific_to_single_intermediate`
- `test_grcv3_rich_v4_post_split_reentry_trace_isolates_child_settlement_block`
- `test_grcv3_rich_v4_reentry_neighborhood_trace_isolates_neighbor_role_mix`
- `test_grcv3_rich_v4_reentry_support_isolation_trace_isolates_secondary_role`
- `test_grcv3_rich_v4_secondary_support_counterfactual_trace_is_decisive`
- `test_grcv3_rich_v4_secondary_support_authorability_trace_shows_existing_structure_is_sufficient`

### `TelemetryCollapseTraceTest`

Old prefix:
- `test_experiments.TelemetryRepresentativeExperimentTest.*`

New prefix:
- `test_experiments.TelemetryCollapseTraceTest.*`

Relocated methods:
- `test_grcv3_rich_v4_collapse_regime_trace_shows_path_specific_support_to_carrier_collapse`
- `test_grcv3_broad_collapse_survey_shows_plural_heterogeneous_collapse_lanes`
- `test_grcv3_pre_spark_collapse_decomposition_tracks_existing_structure`
- `test_grcv3_post_spark_collapse_boundary_is_already_authored_by_transfer_mediation`
- `test_grcv3_post_spark_late_window_stability_shows_blocked_lane_only_later_partially_converges`
- `test_grcv3_post_spark_delay_authorability_shows_existing_transfer_mediation_is_sufficient`
- `test_grcv3_post_collapse_geometry_exclusion_shows_sink_reroute_is_geometry_mediated`

### `TelemetryLandscapeExperimentTest`

Old prefix:
- `test_experiments.TelemetryRepresentativeExperimentTest.*`

New prefix:
- `test_experiments.TelemetryLandscapeExperimentTest.*`

Relocated methods:
- `test_run_grcv3_landscape_experiment_emits_artifacts_and_reports`
- `test_run_grcv3_landscape_experiment_can_emit_checkpoint_artifacts`
- `test_grcv3_landscape_script_rejects_non_positive_steps`

### `TelemetryScriptTest`

Old prefix:
- `test_experiments.TelemetryRepresentativeExperimentTest.*`

New prefix:
- `test_experiments.TelemetryScriptTest.*`

Relocated methods:
- `test_grcv3_path_failure_trace_script_rejects_non_positive_steps`
- `test_grcv3_landscape_script_can_emit_checkpoint_artifacts`
- `test_grcv3_path_failure_trace_script_emits_trace`
- `test_grcv3_candidate_transition_trace_script_rejects_non_positive_steps`
- `test_grcv3_candidate_transition_trace_script_emits_trace`
- `test_grcv3_settlement_locus_trace_script_rejects_non_positive_steps`
- `test_grcv3_settlement_locus_trace_script_emits_trace`
- `test_grcv3_settlement_reentry_trace_script_rejects_non_positive_steps`
- `test_grcv3_settlement_reentry_trace_script_emits_trace`
- `test_grcv3_settlement_reentry_neighborhood_trace_script_rejects_non_positive_steps`
- `test_grcv3_settlement_reentry_neighborhood_trace_script_emits_trace`
- `test_grcv3_settlement_reentry_support_isolation_trace_script_rejects_non_positive_steps`
- `test_grcv3_settlement_reentry_support_isolation_trace_script_emits_trace`
- `test_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_rejects_non_positive_steps`
- `test_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_emits_trace`
- `test_grcv3_secondary_support_authorability_trace_script_rejects_non_positive_steps`
- `test_grcv3_secondary_support_authorability_trace_script_emits_trace`
- `test_grcv3_collapse_regime_trace_script_rejects_non_positive_steps`
- `test_grcv3_collapse_regime_trace_script_emits_trace`
- `test_grcv3_broad_collapse_survey_script_emits_trace`
- `test_grcv3_pre_spark_collapse_decomposition_trace_script_rejects_non_positive_steps`
- `test_grcv3_pre_spark_collapse_decomposition_trace_script_emits_trace`
- `test_grcv3_post_spark_collapse_boundary_trace_script_rejects_non_positive_steps`
- `test_grcv3_post_spark_collapse_boundary_trace_script_emits_trace`
- `test_grcv3_post_spark_late_window_stability_trace_script_rejects_non_positive_steps`
- `test_grcv3_post_spark_late_window_stability_trace_script_emits_trace`
- `test_grcv3_post_spark_delay_authorability_trace_script_rejects_non_positive_steps`
- `test_grcv3_post_spark_delay_authorability_trace_script_emits_trace`
- `test_grcv3_post_collapse_geometry_exclusion_trace_script_rejects_non_positive_steps`
- `test_grcv3_post_collapse_geometry_exclusion_trace_script_emits_trace`

## Preserved Public Entry-Point Coverage

- `TelemetryRepresentativeExperimentTest`
  - `telemetry.run_grcv2_representative_experiment`
  - `telemetry.run_grcv3_representative_experiment`
  - representative script entrypoint
  - representative-facing extension-builder hooks exposed via
    `pygrc.telemetry.experiments`
- `TelemetryFailureTraceTest`
  - `telemetry.build_grcv3_landscape_path_failure_trace`
  - `telemetry.build_grcv3_landscape_candidate_transition_trace`
- `TelemetrySettlementTraceTest`
  - `telemetry.build_grcv3_landscape_settlement_locus_regime_trace`
  - `telemetry.build_grcv3_landscape_settlement_reentry_trace`
  - `telemetry.build_grcv3_landscape_settlement_reentry_neighborhood_trace`
  - `telemetry.build_grcv3_landscape_settlement_reentry_support_isolation_trace`
  - `telemetry.build_grcv3_landscape_settlement_reentry_secondary_support_counterfactual_trace`
  - `telemetry.build_grcv3_landscape_secondary_support_authorability_trace`
- `TelemetryCollapseTraceTest`
  - `telemetry.build_grcv3_landscape_collapse_regime_trace`
  - `telemetry.build_grcv3_landscape_broad_collapse_survey`
  - `telemetry.build_grcv3_landscape_pre_spark_collapse_decomposition_trace`
  - `telemetry.build_grcv3_landscape_post_spark_collapse_boundary_trace`
  - `telemetry.build_grcv3_landscape_post_spark_late_window_stability_trace`
  - `telemetry.build_grcv3_landscape_post_spark_delay_authorability_trace`
  - `telemetry.build_grcv3_landscape_post_collapse_geometry_exclusion_trace`
- `TelemetryLandscapeExperimentTest`
  - `telemetry.run_grcv3_landscape_experiment`
  - landscape script parameter validation
- `TelemetryScriptTest`
  - the existing trace-script emission and validation surface, kept intact but
    isolated into its own class until helper consolidation and deduplication

## Post-Split Verification

- Post-split discovered id count: `64`
- Post-split class ownership:
  - `TelemetryRepresentativeExperimentTest`: `7`
  - `TelemetryFailureTraceTest`: `6`
  - `TelemetrySettlementTraceTest`: `11`
  - `TelemetryCollapseTraceTest`: `7`
  - `TelemetryLandscapeExperimentTest`: `3`
  - `TelemetryScriptTest`: `30`
- Full verification command:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
- Result:
  - `Ran 64 tests in 602.593s`
  - `OK`

## Boundary Notes

- Iteration 4A intentionally stopped at class partition inside the existing
  `tests/telemetry/test_experiments.py` module.
- This keeps helper/loader consolidation out of the relocation pass and leaves
  Iteration 4B responsible for shared loader/fixture cleanup.
- No test body, fixture value, expected label, or public telemetry entry point
  was intentionally changed in this pass.
