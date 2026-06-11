# D2 Predictive Role Separation Scoring Report

Status: complete as an artifact scorecard; fitted CV remains limited.

Classification: `role_separation_supported_with_scorecard_cv_limitations`.

## Scope

D2 aggregates completed A-G and D1/D3/D4/D5/D6/D7/D8 artifact scores
into a feature-family comparison. The scorecard compares row, column,
port, random grouping, and degree/adjacency features where the completed
artifacts expose matching targets.

## Best Feature Family By Target

| Target Class | Target | Best Family | Score | Metric | CV Status |
| --- | --- | --- | ---: | --- | --- |
| edge_local | d6_signed_edge_local_interaction | port | 1.000000 | r2 | saturated_factorial_no_statistical_cv |
| edge_local | experiment_g_observer_local_motion | port | 1.000000 | canonical_control_success | clean_motion_controls_no_fitted_cv |
| generic_activity | d4_lane_a_saturation_gate | degree_adjacency_baseline | 1.000000 | gate_formula_match | transform_invariant_h0_competitive |
| generic_activity | experiment_f_edge_label_path_disagreement | degree_adjacency_baseline | 1.000000 | edge_label_path_control_success | edge_label_fixture_h0_competitive |
| geometric_differential | d3_row_geometry_transpose_delta | row | 0.627051 | mean_role_response | artifact_reuse_no_fitted_cv |
| geometric_differential | experiment_a_row_dominance | row | 1.000000 | classification_accuracy | proxy_transform_controls_available |
| identity_level_persistence | d8_configured_window_identity | port_plus_column_plus_global_basin_context | 1.000000 | accepted_identity_criteria_success | configured_window_fixture_only_partial |
| interface_routing_refinement | d5_immediate_refinement_column_memory | column | 1.000000 | endpoint_column_match_accuracy | identity_fixture_only_no_heldout_fit |
| interface_routing_refinement | d5_post_window_column_memory | column | 0.888889 | persistent_endpoint_column_accuracy | identity_fixture_only_degree_baseline_competitive |
| interface_routing_refinement | d7_multiscale_semantic_columns_immediate | column | 1.000000 | grouping_target_accuracy | identity_fixture_only_no_heldout_fit |
| interface_routing_refinement | experiment_b_column_proxy_dominance | column | 1.000000 | classification_accuracy | proxy_transform_controls_available |

## H0-Competitive Targets

- `d5_post_window_column_memory`
- `d4_lane_a_saturation_gate`
- `experiment_f_edge_label_path_disagreement`

## Random Grouping Controls

| Control | Target Class | Score | Comparison | Status |
| --- | --- | ---: | ---: | --- |
| d1_sampled_s9_random_triple_proxy | factorization_sensitive_artifacts | 0.000000 | 1.000000 | structured_beats_random |
| d5_post_window_random_triple | interface_routing_refinement | 0.222222 | 0.888889 | true_column_beats_random |
| d6_signed_target_random_triple | edge_local | 0.100000 | 1.000000 | port_beats_random |
| d7_immediate_random_triple | interface_routing_refinement | 0.222222 | 1.000000 | true_column_beats_random |
| shuffled_target_labels | all |  |  | inconclusive_small_deterministic_fixture_set |

## Interpretation

D2 supports predictive role separation at the artifact-scorecard level.
Rows are strongest for geometric/differential targets, columns are
strongest for interface/refinement/multiscale targets, and port-level
features are strongest for the signed edge-local and observer-local
motion targets. Degree/adjacency remains competitive for Lane A
saturation and edge-label path disagreement, so H0 is not globally
rejected by D2.

## Cross-Validation Boundary

The completed artifact set is made of clean deterministic fixtures.
D2 records transform and source-fixture proxy splits where available,
but a full fitted held-out-landscape cross-validation pass remains
inconclusive.

## Manifest Fields

- required manifest fields: `discriminator_id, iteration, script_path, command, git_commit, lane_id, fixture_id, transform_id, seed, runtime_params, artifact_schema_version, artifact_source_map, output_paths`
- evidence labels: `direct, derived, partial, blocked, inconclusive`
- summary boundary: D2 compares completed artifact scores by feature family. It supports role separation for row, column, and port-sensitive targets, while degree/adjacency remains competitive for Lane A saturation and edge-label path targets. Full fitted cross-validation remains limited by the small deterministic fixture set.
