# N22 Iteration 5-C - Alternative Non-Consumptive Carrier Probe

Status: `passed`

Acceptance state: `accepted_producer_mediated_non_consumptive_carrier_candidate_native_gap_preserved`

Output digest: `b2bc2089b24ba5e945e861b0e2fd93974c1a7d882905fcaa75f24d3f6ba0bfed`

## Summary

I5-C finds an alternative non-consumptive carrier path by moving the durable quantity from route-b packet residue into serialized edge/conductance geometry. Repeated Lane-B readback does not spend that carrier, unlike the I5-B packet readout path.

The positive I5-C rows are producer-mediated carrier candidates. They do not prove native route-conductance memory, semantic learning, choice, agency, native support, final N22, SU5/SU6, or the N21 ND6 bridge. N08/N10/N11 native conductance and integration gaps remain load-bearing.

## Carrier Rows

| Row | Carrier | Decision | Rung | Delta | Peer Margin | Second Readback |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `route_conductance_geometry_carrier` | `route_conductance_geometry_carrier` | `partial` | `SU4_producer_mediated_non_consumptive_carrier_candidate_pending_I7` | 0.180000 | 0.180000 | 1.000000 |
| `neutral_reservoir_buffered_carrier` | `neutral_reservoir_buffered_carrier` | `partial` | `SU4_producer_mediated_non_consumptive_carrier_candidate_pending_I7` | 0.120000 | 0.120000 | 1.000000 |
| `band_buffered_return_carrier` | `band_buffered_return_carrier` | `partial` | `SU4_producer_mediated_non_consumptive_carrier_candidate_pending_I7` | 0.070000 | 0.070000 | 1.000000 |
| `reduced_packet_readout_dose_boundary` | `reduced_packet_readout_boundary` | `partial` | `SU3_reduced_readout_boundary_no_SU4` | 0.080000 | 0.000000 | 0.750000 |

## Controls

| Control | Status | Reason |
| --- | --- | --- |
| `n05_cyclic_packet_activity_as_susceptibility_relabel` | `failed_closed` | N05 cyclic/self-rearm packet activity is not durable susceptibility by itself. |
| `n06_route_selection_label_as_susceptibility_relabel` | `failed_closed` | N06 repeated route selection is context selection, not source-current durable carrier update. |
| `n08_producer_memory_as_native_conductance_relabel` | `failed_closed` | N08 positive geometry route response remains blocked as native conductance memory. |
| `n07_reservoir_policy_as_native_support_relabel` | `failed_closed` | N07 neutral reservoir is a non-destructive exchange method, not native support. |
| `n10_n11_native_policy_gap_bypass` | `failed_closed` | Native route-conductance memory and native integration gaps cannot be bypassed by I5-C. |
| `hidden_carrier_write` | `failed_closed` | Carrier deltas must be recorded as producer-mediated source-current state mutations. |
| `same_budget_peer_equivalent_delta` | `failed_closed` | If the same-budget peer shows the same target carrier delta, SU4 support is blocked. |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i5b_consumptive_boundary_consumed` | `true` | {"agency_supported": false, "choice_supported": false, "consumptive_readout_detected_count": 5, "durable_geometry_modification_supported"... |
| `thresholds_declared_before_use` | `true` | {"coherence_floor": 9.85, "declared_before_use": true, "i5b_threshold_policy_not_relaxed": true, "max_budget_error": 1e-09, "max_second_r... |
| `artifact_manifest_non_empty` | `true` | 35 |
| `artifact_hashes_match` | `true` | 35 |
| `at_least_one_alternative_carrier_candidate` | `true` | ["n22_i5c_row_route_conductance_geometry_carrier", "n22_i5c_row_neutral_reservoir_buffered_carrier", "n22_i5c_row_band_buffered_return_ca... |
| `same_budget_peer_margin_preserved_for_su4_rows` | `true` | [{"margin": 0.17999999999999994, "row_id": "n22_i5c_row_route_conductance_geometry_carrier"}, {"margin": 0.12, "row_id": "n22_i5c_row_neu... |
| `second_readback_non_consumptive_for_su4_rows` | `true` | [{"loss": 0.0, "ratio": 1.0, "row_id": "n22_i5c_row_route_conductance_geometry_carrier"}, {"loss": 0.0, "ratio": 1.0, "row_id": "n22_i5c_... |
| `reduced_readout_dose_not_promoted` | `true` | ["n22_i5c_row_reduced_packet_readout_dose_boundary"] |
| `native_conductance_memory_still_blocked` | `true` | N08/N10 native conductance gap preserved |
| `controls_fail_closed` | `true` | ["n05_cyclic_packet_activity_as_susceptibility_relabel", "n06_route_selection_label_as_susceptibility_relabel", "n08_producer_memory_as_n... |
| `unsafe_flags_all_false` | `true` | all rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |
