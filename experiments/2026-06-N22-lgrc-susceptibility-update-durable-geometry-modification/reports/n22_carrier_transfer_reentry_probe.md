# N22 Iteration 6-A - Carrier Transfer / Re-entry Probe

Status: `passed`

Acceptance state: `accepted_producer_mediated_carrier_transfer_candidates_pending_i7_no_final_su5`

Output digest: `e919277fbf8b3d40a3da977be9bafba38675cd0af893ef7f594bc25659009678`

## Summary

I6-A shows that the I5-C edge/conductance carriers remain present through delayed target re-entry and peer-corridor flux followed by target re-entry. No new carrier update is applied after loading the I5-C snapshots.

This is a provisional producer-mediated SU5 carrier-transfer candidate pending I7 controls. It does not supersede the existing I6 packet-readout result, does not support native conductance memory, and does not support SU6, final N22, the N21 ND6 bridge, semantic learning, choice, agency, native support, sentience, or Phase 8.

## Transfer Rows

| Row | Decision | Rung | Contexts Passed | SU5 Final |
| --- | --- | --- | ---: | --- |
| `route_conductance_geometry_carrier` | `partial` | `SU5_producer_mediated_carrier_transfer_candidate_pending_I7` | 2/2 | `false` |
| `neutral_reservoir_buffered_carrier` | `partial` | `SU5_producer_mediated_carrier_transfer_candidate_pending_I7` | 2/2 | `false` |
| `band_buffered_return_carrier` | `partial` | `SU5_producer_mediated_carrier_transfer_candidate_pending_I7` | 2/2 | `false` |

## Context Details

| Row | Context | Ratio | Margin | New Carrier Update | Passed |
| --- | --- | ---: | ---: | --- | --- |
| `route_conductance_geometry_carrier` | `delayed_target_reentry_then_readback` | 1.000000 | 0.180000 | `false` | `true` |
| `route_conductance_geometry_carrier` | `peer_corridor_flux_then_target_reentry_readback` | 1.000000 | 0.180000 | `false` | `true` |
| `neutral_reservoir_buffered_carrier` | `delayed_target_reentry_then_readback` | 1.000000 | 0.120000 | `false` | `true` |
| `neutral_reservoir_buffered_carrier` | `peer_corridor_flux_then_target_reentry_readback` | 1.000000 | 0.120000 | `false` | `true` |
| `band_buffered_return_carrier` | `delayed_target_reentry_then_readback` | 1.000000 | 0.070000 | `false` | `true` |
| `band_buffered_return_carrier` | `peer_corridor_flux_then_target_reentry_readback` | 1.000000 | 0.070000 | `false` | `true` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i5c_passed` | `true` | {"candidate_row_count": 4, "existing_i6_superseded": false, "final_n22_supported": false, "i6_rerun_or_i7_controls_required": true, "n21_... |
| `thresholds_declared_before_use` | `true` | {"coherence_floor": 9.85, "consumes_i5c_only": true, "control_contexts": ["peer_label_swap_reentry_control", "active_carrier_update_carry... |
| `source_i5c_su4_candidate_count` | `true` | ["n22_i5c_row_route_conductance_geometry_carrier", "n22_i5c_row_neutral_reservoir_buffered_carrier", "n22_i5c_row_band_buffered_return_ca... |
| `artifact_manifest_non_empty` | `true` | 47 |
| `artifact_hashes_match` | `true` | 47 |
| `all_positive_contexts_passed` | `true` | [{"contexts": [{"context_id": "delayed_target_reentry_then_readback", "passed": true}, {"context_id": "peer_corridor_flux_then_target_ree... |
| `all_rows_provisional_su5_candidates` | `true` | ["SU5_producer_mediated_carrier_transfer_candidate_pending_I7", "SU5_producer_mediated_carrier_transfer_candidate_pending_I7", "SU5_produ... |
| `carrier_update_disabled_after_load` | `true` | no new carrier update after I5-C snapshots |
| `peer_label_swap_controls_fail_closed` | `true` | ["n22_i6a_row_route_conductance_geometry_carrier", "n22_i6a_row_neutral_reservoir_buffered_carrier", "n22_i6a_row_band_buffered_return_ca... |
| `native_conductance_memory_still_blocked` | `true` | native policy gap preserved |
| `controls_fail_closed` | `true` | ["peer_label_swap_reentry_control", "active_carrier_update_carryover_control", "native_conductance_memory_relabel_control", "peer_label_s... |
| `unsafe_flags_all_false` | `true` | all rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |
