# N22 Iteration 6-B - Carrier Transfer Stress-Boundary Probe

Status: `passed`

Acceptance state: `accepted_producer_mediated_carrier_transfer_stress_boundary_pending_i7_no_final_su5`

Output digest: `3ee5f391766d9d75db6d794f8fe0f33341e5dfd96eee4e4bca6254ec5be7e9a6`

## Summary

I6-B stress-tests the I5-C/I6-A edge/conductance carriers under longer delay, stronger peer-corridor flux, repeated target re-entry, and mixed peer/target corridor stress. The carrier remains present without any new producer carrier update after loading I5-C snapshots.

This is bounded producer-mediated SU5 stress-boundary evidence pending I7 controls. It does not replace I6-A, does not rescue the packet-readout branch, does not support native conductance memory, and does not support final SU5, SU6, final N22, the N21 ND6 bridge, semantic learning, choice, agency, native support, sentience, or Phase 8.

## Stress Rows

| Row | Decision | Rung | Stress Contexts Passed | Min Ratio | Min Margin | SU5 Final |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `route_conductance_geometry_carrier` | `partial` | `SU5_producer_mediated_carrier_transfer_stress_boundary_candidate_pending_I7` | 4/4 | 1.000000 | 0.180000 | `false` |
| `neutral_reservoir_buffered_carrier` | `partial` | `SU5_producer_mediated_carrier_transfer_stress_boundary_candidate_pending_I7` | 4/4 | 1.000000 | 0.120000 | `false` |
| `band_buffered_return_carrier` | `partial` | `SU5_producer_mediated_carrier_transfer_stress_boundary_candidate_pending_I7` | 4/4 | 1.000000 | 0.070000 | `false` |

## Stress Context Details

| Row | Context | Ratio | Margin | New Carrier Update | Passed |
| --- | --- | ---: | ---: | --- | --- |
| `route_conductance_geometry_carrier` | `long_idle_delay_target_reentry` | 1.000000 | 0.180000 | `false` | `true` |
| `route_conductance_geometry_carrier` | `strong_peer_corridor_then_target_reentry` | 1.000000 | 0.180000 | `false` | `true` |
| `route_conductance_geometry_carrier` | `repeated_target_reentry_pair` | 1.000000 | 0.180000 | `false` | `true` |
| `route_conductance_geometry_carrier` | `mixed_peer_target_corridor_sequence` | 1.000000 | 0.180000 | `false` | `true` |
| `neutral_reservoir_buffered_carrier` | `long_idle_delay_target_reentry` | 1.000000 | 0.120000 | `false` | `true` |
| `neutral_reservoir_buffered_carrier` | `strong_peer_corridor_then_target_reentry` | 1.000000 | 0.120000 | `false` | `true` |
| `neutral_reservoir_buffered_carrier` | `repeated_target_reentry_pair` | 1.000000 | 0.120000 | `false` | `true` |
| `neutral_reservoir_buffered_carrier` | `mixed_peer_target_corridor_sequence` | 1.000000 | 0.120000 | `false` | `true` |
| `band_buffered_return_carrier` | `long_idle_delay_target_reentry` | 1.000000 | 0.070000 | `false` | `true` |
| `band_buffered_return_carrier` | `strong_peer_corridor_then_target_reentry` | 1.000000 | 0.070000 | `false` | `true` |
| `band_buffered_return_carrier` | `repeated_target_reentry_pair` | 1.000000 | 0.070000 | `false` | `true` |
| `band_buffered_return_carrier` | `mixed_peer_target_corridor_sequence` | 1.000000 | 0.070000 | `false` | `true` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i5c_passed` | `true` | {"candidate_row_count": 4, "existing_i6_superseded": false, "final_n22_supported": false, "i6_rerun_or_i7_controls_required": true, "n21_... |
| `i6a_passed` | `true` | {"existing_i6_superseded": false, "final_n22_supported": false, "i5c_branch_status": "provisional_producer_mediated_SU5_candidate_pending... |
| `thresholds_declared_before_use` | `true` | {"carrier_retune_allowed": false, "coherence_floor": 9.85, "consumes_i5c_and_i6a_only": true, "control_contexts": ["peer_label_swap_under... |
| `source_i5c_su4_candidate_count` | `true` | ["n22_i5c_row_route_conductance_geometry_carrier", "n22_i5c_row_neutral_reservoir_buffered_carrier", "n22_i5c_row_band_buffered_return_ca... |
| `source_i6a_su5_candidate_count` | `true` | 3 |
| `artifact_manifest_non_empty` | `true` | 77 |
| `artifact_hashes_match` | `true` | 77 |
| `all_stress_contexts_passed` | `true` | [{"contexts": [{"context_id": "long_idle_delay_target_reentry", "passed": true}, {"context_id": "strong_peer_corridor_then_target_reentry... |
| `all_rows_provisional_su5_stress_candidates` | `true` | ["SU5_producer_mediated_carrier_transfer_stress_boundary_candidate_pending_I7", "SU5_producer_mediated_carrier_transfer_stress_boundary_c... |
| `carrier_update_disabled_after_load` | `true` | no new carrier update after I5-C snapshots |
| `peer_label_swap_controls_fail_closed` | `true` | ["n22_i6b_row_route_conductance_geometry_carrier", "n22_i6b_row_neutral_reservoir_buffered_carrier", "n22_i6b_row_band_buffered_return_ca... |
| `native_conductance_memory_still_blocked` | `true` | native policy gap preserved |
| `controls_fail_closed` | `true` | ["peer_label_swap_under_stress_control", "active_carrier_update_carryover_control", "native_conductance_memory_relabel_control", "stress_... |
| `unsafe_flags_all_false` | `true` | all rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |
| `final_claims_blocked` | `true` | {"existing_i6_superseded": false, "final_n22_supported": false, "i5c_i6a_branch_status": "provisional_producer_mediated_SU5_stress_bounda... |
