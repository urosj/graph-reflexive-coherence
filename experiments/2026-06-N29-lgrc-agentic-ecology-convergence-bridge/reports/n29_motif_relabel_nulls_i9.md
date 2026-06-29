# N29 Iteration 9 - Motif Relabel Nulls And Composition Controls

## Summary

- status: `passed`
- acceptance_state: `accepted_phase_b_controls_fail_closed_ready_for_phase_c`
- control rows: `33`
- schema negative controls: `10`
- motif control rows: `21`
- composition control rows: `2`
- failed_closed_rows: `33`
- failed_open_rows: `0`
- row-local null rows: `26`
- near-positive controls: `26`
- null_failed_closed_rows: `26`
- null_failed_open_rows: `0`
- phase_b_closed: `true`
- ready_for_iteration_10: `true`
- output_digest: `a6869a090698bf0c54601e34758408345eda978408a135c883fc495bf7c55a28`

Iteration 9 closes Phase B by deriving row-local nulls from forbidden
promotion edges: source row -> valid bounded claim -> tempting stronger
relabel -> expected rejection. Each null has a paired near-positive
control that preserves the legitimate bounded bridge reading.

## Control Families

| Family | Row Count |
| --- | ---: |
| `ap_gap_control` | 1 |
| `composition_control` | 3 |
| `debt_as_native_relabel_control` | 7 |
| `medium_debt_control` | 1 |
| `motif_control` | 1 |
| `motif_required_control_presence` | 7 |
| `motif_success_relabel_control` | 7 |
| `native_readiness_control` | 1 |
| `prototype_relabel_control` | 1 |
| `review_gate_control` | 1 |
| `source_of_truth_control` | 1 |
| `unsafe_ecology_relabel_control` | 1 |
| `visual_relabel_control` | 1 |

## Null Adequacy

| Null Family | Count | Motif Families | Adequacy |
| --- | ---: | --- | --- |
| `vocabulary_as_evidence_nulls` | 3 | `reserve_optionality_formation`, `trace_pressure_loop`, `transfer_replay_role_relocation` | `passed` |
| `ant_label_as_ant_behavior_nulls` | 2 | `reserve_optionality_formation`, `trace_pressure_loop` | `passed` |
| `message_scaffold_as_native_medium_nulls` | 1 | `boundary_shared_medium_unit` | `passed` |
| `producer_residue_as_native_capacity_nulls` | 2 | `proxy_susceptibility_reentry`, `transfer_replay_role_relocation` | `passed` |
| `medium_debt_as_native_shared_medium_nulls` | 3 | `boundary_shared_medium_unit`, `composition`, `generative_extractive_medium_reshaping` | `passed` |
| `visual_or_report_as_runtime_evidence_nulls` | 1 | `global_phase_b_boundary` | `passed` |
| `prototype_candidate_as_prototype_success_nulls` | 1 | `global_phase_b_boundary` | `passed` |
| `motif_as_native_ecology_success_nulls` | 2 | `composition`, `global_phase_b_boundary` | `passed` |
| `N28_generative_as_cooperation_nulls` | 1 | `generative_extractive_medium_reshaping` | `passed` |
| `composition_without_order_or_controls_nulls` | 5 | `composition` | `passed` |
| `source_summary_as_original_evidence_nulls` | 1 | `global_phase_b_boundary` | `passed` |
| `review_gate_bypass_nulls` | 1 | `global_phase_b_boundary` | `passed` |
| `AP4_AP5_NAT4_gap_erasure_nulls` | 2 | `global_phase_b_boundary`, `proxy_susceptibility_reentry` | `passed` |
| `naturalization_debt_as_native_support_nulls` | 1 | `global_phase_b_boundary` | `passed` |

## Null Derivation

The null set is not chosen by generic caution. It is derived from I7
coverage/debt rows, I8 motif rows, and the I4 claim boundary. A null
is accepted only when it names a source motif or global boundary,
preserves the bounded valid claim, names the attempted relabel path,
fails closed, and has a paired near-positive control.

The near-positive controls matter because they prove I9 is not simply
rejecting every bridge structure. I9 blocks unsafe promotion while
leaving bounded motif classification available for Phase C admission
work.

## Checks

| Check | Passed |
| --- | --- |
| `i4_bridge_schema_passed` | `true` |
| `i7_coverage_matrix_passed` | `true` |
| `i8_bridge_motif_library_passed` | `true` |
| `i7_coverage_matrix_digest_matches` | `true` |
| `i8_motif_library_digest_matches` | `true` |
| `i4_control_policy_digest_matches` | `true` |
| `all_control_rows_fail_closed` | `true` |
| `all_null_rows_fail_closed` | `true` |
| `no_failed_open_rows` | `true` |
| `null_failed_open_count_zero` | `true` |
| `all_nulls_have_source_rows` | `true` |
| `all_nulls_have_attempted_relabel` | `true` |
| `all_nulls_have_expected_status_failed_closed` | `true` |
| `all_nulls_have_failure_if_accepted_flag` | `true` |
| `all_nulls_have_near_positive_control` | `true` |
| `near_positive_controls_passed` | `true` |
| `all_schema_negative_fixtures_consumed` | `true` |
| `every_i8_motif_has_control_rows` | `true` |
| `composition_controls_present` | `true` |
| `motif_success_relabels_rejected` | `true` |
| `debt_as_native_relabels_rejected` | `true` |
| `all_required_null_families_present` | `true` |
| `all_motif_families_have_relabel_null_coverage` | `true` |
| `all_required_composition_controls_have_nulls` | `true` |
| `all_global_blocked_claims_covered` | `true` |
| `producer_residue_relabels_covered` | `true` |
| `medium_debt_relabels_covered` | `true` |
| `naturalization_debt_relabels_covered` | `true` |
| `review_gate_bypass_nulls_present` | `true` |
| `ap4_ap5_nat4_gap_erasure_nulls_present` | `true` |
| `null_adequacy_table_passed` | `true` |
| `prototype_and_runtime_probe_rows_remain_closed` | `true` |
| `phase_b_closed_phase_c_not_opened` | `true` |
| `native_ecology_and_agency_claims_closed` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
| `ready_for_iteration_10` | `true` |

## Interpretation

I9 supports Phase B closeout controls, not Phase C prototype admission.
All control rows and row-local null rows fail closed as intended. I9
blocks vocabulary-as-evidence, ant-label-as-behavior, message scaffold
as native medium, producer residue as native capacity, medium debt as
native shared medium, naturalization debt as native support, visual or
report artifacts as runtime evidence, prototype candidates as prototype
success, motifs as native ecology success, N28 generative/extractive
patterns as cooperation or biological agency, composition without
order/source/control support, source summaries as original evidence,
review-gate bypass, and AP4/AP5/NAT4 gap erasure.

Passing I9 means the Phase B bridge motif library is guarded against
known false promotions and ready for Iteration 10 prototype admission
schema. It does not open prototype rows, runtime ecology probes,
positive ecology evidence, native ecology, native ant/colony agency,
native shared-medium coordination, sentience, biological agency, or
Phase 8 completion claims.
