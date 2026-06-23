# N22 Iteration 6 - Transfer / Re-entry Probe

Status: `passed`

Acceptance state: `accepted_transfer_readout_expression_no_su5_due_consumptive_boundary`

Output digest: `00263f30abb5cfcf224bd7b61d72ffae31472efb4e334f707a2de1ff9854da95`

## Summary

I6 turns the I5/I5-A replay-backed route_b susceptibility signal into local transfer/readout expression for four rows, but I5-B prevents promotion to SU5 because the readout is consumptive rather than non-consumptive durable geometry. The narrow complementary split row still demotes on target-over-peer separation.

I5-A showed stress-limited SU3 preservation and a repeated re-entry depletion boundary. I6 consumes that boundary, then asks whether the same source-current route_b delta is expressed through declared later re-entry contexts rather than only clean replay. The positive contexts are delayed boundary re-entry and corridor peer-flux followed by route_b re-entry. The single route and bounded-dose rows express the readout, but I5-B shows that repeated readout consumes the residual below the non-consumptive floor. The complementary split row is demoted because its adjacent-path component prevents a route_b-specific transfer margin.

## Transfer Rows

| Row | Source | Rung | Positive Contexts | Controls | Narrow |
| --- | --- | --- | --- | --- | --- |
| `i4_minimal_route_b` | `I4` | `SU3_transfer_readout_expression_no_SU5` | `true` | `true` | `false` |
| `dose_08_i4_reference` | `I4-A` | `SU3_transfer_readout_expression_no_SU5` | `true` | `true` | `false` |
| `dose_14_stronger_bounded` | `I4-A` | `SU3_transfer_readout_expression_no_SU5` | `true` | `true` | `false` |
| `single_route_b_reference` | `I4-B` | `SU3_transfer_readout_expression_no_SU5` | `true` | `true` | `false` |
| `complementary_split_route_b_adjacent` | `I4-B` | `demoted_before_SU5` | `false` | `true` | `true` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i5_passed` | `true` | accepted_replay_backed_su3_candidates_pending_i7_controls |
| `i5a_passed` | `true` | accepted_replay_stress_limited_su3_candidates_pending_i7_controls |
| `i5b_passed` | `true` | accepted_consumptive_readout_boundary_no_nonconsumptive_durability |
| `i5_su3_candidate_count` | `true` | ["n22_i5_row_i4_minimal_route_b", "n22_i5_row_dose_08_i4_reference", "n22_i5_row_dose_14_stronger_bounded", "n22_i5_row_single_route_b_re... |
| `i5a_rows_cover_i5_rows` | `true` | ["n22_i5_row_i4_minimal_route_b", "n22_i5_row_dose_08_i4_reference", "n22_i5_row_dose_14_stronger_bounded", "n22_i5_row_single_route_b_re... |
| `i5b_rows_cover_i5_rows` | `true` | ["n22_i5_row_i4_minimal_route_b", "n22_i5_row_dose_08_i4_reference", "n22_i5_row_dose_14_stronger_bounded", "n22_i5_row_single_route_b_re... |
| `thresholds_declared_before_use` | `true` | {"boundary_active_degree_floor": 9, "coherence_floor": 9.85, "consumes_i5a_depletion_boundary": true, "consumes_i5b_consumptive_readout_b... |
| `artifact_manifest_non_empty` | `true` | 121 |
| `artifact_hashes_match` | `true` | 121 |
| `non_narrow_rows_positive_transfer_contexts_passed` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `narrow_complementary_row_demoted_without_overclaim` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `all_rows_controls_failed_closed` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `repeated_boundary_preserved_for_all_rows` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `consumptive_boundary_preserved_for_all_rows` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `transfer_readout_expression_subset_recorded` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `narrow_complementary_row_tracked` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `all_claims_still_blocked` | `true` | [{"consumptive_readout_boundary_preserved": true, "control_contexts_failed_closed": true, "i6_consumable_role": "transfer_readout_express... |
| `unsafe_flags_all_false` | `true` | all transfer rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |

## Claim Boundary

I6 supports only transfer/readout expression of consumptive SU3-limited rows pending I7 controls. It does not support SU5, SU6, final N22, the N21 ND6 bridge, semantic learning, choice, agency, native support, sentience, Phase 8, or ant-ecology implementation.

I6 does not run the full I7 control matrix and cannot assign SU6.
