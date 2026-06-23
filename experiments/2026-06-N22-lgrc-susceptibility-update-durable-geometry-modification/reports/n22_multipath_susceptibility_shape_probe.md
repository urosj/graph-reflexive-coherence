# N22 Iteration 4-B - Multi-Path Susceptibility Shape Probe

Status: `passed`

Acceptance state: `accepted_multipath_shape_su2_extension_pending_replay_controls`

Output digest: `4ac32cc56502ebc9f4723f171fdc40bb2b059e6a5c167f0d1e837b873064f266`

## Summary

Iteration 4-B keeps the I4/I4-A fixture and thresholds fixed, then tests
whether route/path shape matters for provisional SU2 evidence. It includes
single-route, competing-route, complementary split, insufficient split,
and over-coupled split rows.

The competing alternate route spends the same budget away from route_b and fails closed because route_b susceptibility delta is absent.

The complementary split preserves a sufficient route_b component while adding adjacent-route flux, so it remains a provisional SU2 multi-path candidate without becoming cooperation or strategy.

## Path Rows

| Path | Class | Decision | Role | Classification | Target Delta | Peer Delta | Re-entry Ratio | Coherence Margin |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `single_route_b_reference` | `single_target_route` | `partial` | `source_current_SU2_shape_evidence_only` | `bounded_single_target_route_SU2_candidate` | 0.080000000000 | 0.000000000000 | 0.500000000000 | 0.110000000000 |
| `competing_alternate_route_same_budget` | `competing_alternate_route` | `rejected` | `failure_baseline_only` | `path_shape_control_failed_closed` | 0.000000000000 | 0.080000000000 | 0.000000000000 | 0.110000000000 |
| `complementary_split_route_b_adjacent` | `complementary_split` | `partial` | `source_current_SU2_shape_evidence_only` | `bounded_complementary_split_SU2_candidate` | 0.080000000000 | 0.000000000000 | 0.500000000000 | 0.050000000000 |
| `split_unrelated_insufficient_route_b` | `insufficient_target_component_split` | `rejected` | `failure_baseline_only` | `path_shape_control_failed_closed` | 0.040000000000 | 0.000000000000 | 0.000000000000 | 0.110000000000 |
| `overcoupled_multipath_gate_block` | `overcoupled_split` | `blocked` | `gate_blocker_only` | `out_of_scope_multipath_drift_failed_closed` | 0.120000000000 | 0.000000000000 | 0.666666666667 | -0.050000000000 |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_passed` | `true` | accepted_source_handoff_inventory_no_susceptibility_evidence |
| `i2_schema_passed` | `true` | accepted_susceptibility_schema_frozen_no_positive_evidence |
| `i3_active_nulls_passed` | `true` | accepted_active_nulls_fail_closed_no_positive_evidence |
| `i4_minimal_probe_passed` | `true` | accepted_minimal_source_current_su2_candidate_pending_replay_controls |
| `i4a_dose_probe_passed` | `true` | accepted_dose_boundary_su2_extension_pending_replay_controls |
| `threshold_policy_matches_i4` | `true` | {"boundary_active_degree_floor": 9, "coherence_floor": 9.85, "declared_before_use": true, "inherits_i4_threshold_policy": true, "max_budg... |
| `path_rows_declared_before_use` | `true` | [{"path_id": "single_route_b_reference", "path_shape_class": "single_target_route", "peer_segments": [{"amount": 0.08, "edge_id": 1, "sou... |
| `artifact_manifest_non_empty` | `true` | 87 |
| `artifact_hashes_match` | `true` | 87 |
| `single_and_complementary_positive` | `true` | [{"classification": "bounded_single_target_route_SU2_candidate", "coherence_status": "changed_within_allowed_delta_above_floor", "path_id... |
| `competing_and_insufficient_fail_closed` | `true` | [{"classification": "bounded_single_target_route_SU2_candidate", "coherence_status": "changed_within_allowed_delta_above_floor", "path_id... |
| `overcoupled_high_path_blocks` | `true` | [{"classification": "bounded_single_target_route_SU2_candidate", "coherence_status": "changed_within_allowed_delta_above_floor", "path_id... |
| `positive_rows_reject_global_drift` | `true` | [{"global_drift_rejected": true, "peer_route_delta": 0.0, "same_total_prior_interaction_budget": true, "status": "passed", "target_over_p... |
| `positive_partial_rows_scoped_as_su2_input_only` | `true` | [{"i4b_consumable_role": "source_current_SU2_shape_evidence_only", "row_decision": "partial", "row_decision_scope": "provisional_SU2_inpu... |
| `rejected_su1_rows_are_failure_baselines_only` | `true` | [{"i4b_consumable_role": "failure_baseline_only", "provisional_su_ladder_rung": "SU1", "row_id": "n22_i4b_row_competing_alternate_route_s... |
| `durability_controls_deferred_to_i5` | `true` | I4-B remains path-shape only |
| `all_rows_claim_allowed_false` | `true` | ["partial", "rejected", "partial", "rejected", "blocked"] |
| `durable_geometry_not_supported` | `true` | I4-B is path shape only |
| `unsafe_flags_all_false` | `true` | all path rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |

## Claim Boundary

The result strengthens provisional SU2 input evidence only. Replay-backed SU3, durable SU4, transfer SU5, SU6, final N22, and the N21 ND6 bridge remain blocked.

Complementary path evidence is geometric only. It is not cooperation,
strategy, choice, agency, native support, sentience, Phase 8, or
ant-ecology implementation.

The positive `partial` rows are consumable only as
`source_current_SU2_shape_evidence_only`. Rejected `SU1` rows are
failure baselines only. `one_window_transient_rejected` remains false
until I5 runs durability replay.
