# N22 Iteration 5-B - Residual / Non-Consumptive Durability Probe

Status: `passed`

Acceptance state: `accepted_consumptive_readout_boundary_no_nonconsumptive_durability`

Output digest: `f946824e63737323e44611623c97f37df84f1795168c0013c44b8ef7765e3f0f`

## Summary

I5-B shows the I5/I5-A route_b signal is a consumptive readout boundary, not non-consumptive durable geometry modification.

I5-A recorded repeated re-entry depletion. I5-B makes that explicit by measuring the residual route_b delta after the first readout, after an idle window, and after a second readout. A first residual remains and is idle-stable, but the second readout spends the residual below the non-consumptive floor.

## Residual Rows

| Row | Source | After First | After Second | Consumptive | Rung |
| --- | --- | ---: | ---: | --- | --- |
| `i4_minimal_route_b` | `I4` | 0.500000 | 0.000000 | `true` | `SU3_consumptive_readout_limited` |
| `dose_08_i4_reference` | `I4-A` | 0.500000 | 0.000000 | `true` | `SU3_consumptive_readout_limited` |
| `dose_14_stronger_bounded` | `I4-A` | 0.714286 | 0.428571 | `true` | `SU3_consumptive_readout_limited` |
| `single_route_b_reference` | `I4-B` | 0.500000 | 0.000000 | `true` | `SU3_consumptive_readout_limited` |
| `complementary_split_route_b_adjacent` | `I4-B` | 0.500000 | 0.000000 | `true` | `SU3_consumptive_readout_limited` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i5_passed` | `true` | accepted_replay_backed_su3_candidates_pending_i7_controls |
| `i5a_passed` | `true` | accepted_replay_stress_limited_su3_candidates_pending_i7_controls |
| `i5_su3_candidate_count` | `true` | ["n22_i5_row_i4_minimal_route_b", "n22_i5_row_dose_08_i4_reference", "n22_i5_row_dose_14_stronger_bounded", "n22_i5_row_single_route_b_re... |
| `i5a_rows_cover_i5_rows` | `true` | ["n22_i5_row_i4_minimal_route_b", "n22_i5_row_dose_08_i4_reference", "n22_i5_row_dose_14_stronger_bounded", "n22_i5_row_single_route_b_re... |
| `thresholds_declared_before_use` | `true` | {"boundary_active_degree_floor": 9, "coherence_floor": 9.85, "consumes_i5a_repeated_reentry_boundary": true, "declared_before_use": true,... |
| `artifact_manifest_non_empty` | `true` | 51 |
| `artifact_hashes_match` | `true` | 51 |
| `first_residual_present_for_all_rows` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `idle_residual_stable_for_all_rows` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `all_rows_consumptive_readout_detected` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `no_rows_support_non_consumptive_durability` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `all_rows_block_su4_or_stronger` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `i6_reclassification_required` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `narrow_complementary_row_tracked` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `all_claims_still_blocked` | `true` | [{"after_first_ratio": 0.5000000000000111, "after_second_ratio": 2.2204460492503112e-14, "consumptive_readout_detected": true, "first_res... |
| `unsafe_flags_all_false` | `true` | all residual rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |

## Claim Boundary

I5-B supports only consumptive-readout-limited SU3 evidence. It blocks durable SU4, transfer SU5 as durable susceptibility, SU6, final N22, the N21 ND6 bridge, semantic learning, choice, agency, native support, sentience, Phase 8, and ant-ecology implementation.

I5-B requires I6 to avoid treating transfer/readout expression as non-consumptive durable susceptibility.
