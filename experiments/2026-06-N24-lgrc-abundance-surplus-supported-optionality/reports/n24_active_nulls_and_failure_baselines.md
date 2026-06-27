# N24 Iteration 3 - Active Nulls And Failure Baselines

## Summary

Status: `passed`

Acceptance state: `accepted_active_nulls_fail_closed_no_positive_evidence`

Output digest: `4748bb45748339f13c4ce437b917f7c2f0e33c401cfc058cf211b9393e2494df`

Iteration 3 instantiates the frozen I2 schema as active nulls. It does
not expand the schema, open positive surplus/optionality evidence, or
assign AB/N24-C rungs above control scope.

## Active Null Matrix

| Row | Null | Result | Rung Effect |
| --- | --- | --- | --- |
| `n24_i3_row_01_hidden_budget_relief_as_surplus` | `hidden_budget_relief` | `failed_closed` | `blocks all positive AB support` |
| `n24_i3_row_02_floor_crossing_as_abundance` | `maintenance_floor_crossing` | `failed_closed` | `blocks AB2 and stronger` |
| `n24_i3_row_03_surplus_without_optional_continuation` | `surplus_without_optionality` | `failed_closed` | `may leave AB2 descriptive surplus only; blocks AB3+` |
| `n24_i3_row_04_optionality_without_surplus` | `optionality_without_surplus` | `failed_closed` | `blocks AB2 and AB3+` |
| `n24_i3_row_05_proxy_only_optional_branch_gain` | `proxy_only_gain` | `failed_closed` | `blocks optionality support` |
| `n24_i3_row_06_optional_branch_label_only` | `optional_branch_label_only` | `failed_closed` | `blocks AB3+` |
| `n24_i3_row_07_single_branch_relabel_as_optionality` | `single_branch_relabel` | `failed_closed` | `blocks AB3+` |
| `n24_i3_row_08_independent_run_optional_assembly` | `independent_run_assembly` | `failed_closed` | `blocks original AB3 optional set` |
| `n24_i3_row_09_maintenance_basin_shift_as_surplus` | `maintenance_basin_shift` | `failed_closed` | `blocks surplus claim` |
| `n24_i3_row_10_floor_renormalization_as_surplus` | `floor_renormalization` | `failed_closed` | `blocks surplus claim` |
| `n24_i3_row_11_post_hoc_surplus_construction` | `post_hoc_surplus_construction` | `failed_closed` | `blocks AB2 and stronger` |
| `n24_i3_row_12_n23_selection_context_relabel_as_abundance` | `n23_context_relabel` | `failed_closed` | `blocks N23 context relabel` |
| `n24_i3_row_13_reward_maximization_relabel` | `reward_relabel` | `failed_closed` | `blocks reward/goal overclaim` |
| `n24_i3_row_14_missing_maintenance_floor` | `missing_maintenance_floor` | `failed_closed` | `blocks AB2 and stronger` |
| `n24_i3_row_15_missing_boundary_integrity_trace` | `missing_boundary_integrity` | `failed_closed` | `blocks AB3+` |
| `n24_i3_row_16_optional_flux_drains_maintenance_support` | `optional_flux_drain` | `failed_closed` | `blocks AB3+` |
| `n24_i3_row_17_ap4_final_reclassification_relabel` | `ap4_final_reclassification_relabel` | `failed_closed` | `blocks final global AP4 reclassification` |
| `n24_i3_row_18_ap5_proxy_gap_omission` | `ap5_gap_omission` | `failed_closed` | `blocks proxy/reward rows missing AP5 dependency` |
| `n24_i3_row_19_semantic_choice_agency_native_support_phase8_relabels` | `unsafe_claim_relabels` | `failed_closed` | `blocks unsafe semantic, agency, native-support, and Phase 8 claims` |

## Summary Counts

- Rows: `19`
- Failed closed rows: `19`
- Failed open rows: `0`
- Positive abundance evidence opened: `false`

## Blocker Families

| Family | Nulls |
| --- | --- |
| `surplus_blockers` | `floor_crossing_as_abundance, floor_renormalization_as_surplus, hidden_budget_relief_as_surplus, maintenance_basin_shift_as_surplus, missing_maintenance_floor, optional_flux_drains_maintenance_support, post_hoc_surplus_construction` |
| `optionality_blockers` | `independent_run_optional_assembly, missing_boundary_integrity_trace, optional_branch_label_only, optionality_without_surplus, single_branch_relabel_as_optionality, surplus_without_optional_continuation` |
| `artifact_or_context_blockers` | `n23_selection_context_relabel_as_abundance, proxy_only_optional_branch_gain, reward_maximization_relabel` |
| `ap_blockers` | `ap4_final_reclassification_relabel, ap5_proxy_gap_omission` |
| `unsafe_relabel_blockers` | `semantic_choice_agency_native_support_phase8_relabels` |

## Control Alias Map

| Null | Canonical Control | Reason |
| --- | --- | --- |
| `missing_maintenance_floor` | `floor_crossing_as_abundance_control` | missing predeclared floor blocks the same AB2+ gate as a crossed floor |
| `missing_boundary_integrity_trace` | `optional_branch_label_only_control` | without boundary trace the branch is only a label-like optionality claim |
| `optional_flux_drains_maintenance_support` | `floor_crossing_as_abundance_control` | flux drain is treated as maintenance-floor depletion rather than surplus |

## Status Semantics

`failed_closed` means the false-positive blocker triggered and the
unsafe/null claim was rejected. It satisfies the negative-control
gate; it does not automatically demote future positive rows.

These rows are active-null fixtures only:
`trace_admissibility = active_null_fixture_only_not_positive_evidence`,
`positive_evidence_admissible = false`, and
`control_execution_kind = schema_instantiation_only`.

The N24-C ceiling after I3 is
`N24-C1_active_null_control_discipline_established`; no final
closeout rung is assigned.

## Row Field Policy

I3 rows use all `103` I2 candidate fields plus a declared active-null
metadata extension set. A validation check requires each row's field
set to equal `I2 required fields U active_null_extension_fields`.

## Geometric Interpretation

- `hidden_budget_relief_as_surplus`: The maintenance basin seems to have spare support, but the spare margin is supplied by an undeclared producer/budget channel rather than by the source-current basin geometry.
- `floor_crossing_as_abundance`: The apparent optional branch is paid for by eroding the maintenance basin below its support floor, so it is depletion, not abundance.
- `surplus_without_optional_continuation`: The basin has spare support above the floor, but the geometry does not open a second continuation route in the same window.
- `optionality_without_surplus`: The branch fan-out exists only by consuming maintenance support; the basin is branching under scarcity, not from surplus.
- `proxy_only_optional_branch_gain`: A scalar proxy improves, but no basin support margin or optional branch geometry is emitted as source-current trace.
- `optional_branch_label_only`: The graph carries branch names, but there are no branch-specific support, coherence, boundary, or flux traces.
- `single_branch_relabel_as_optionality`: The basin continues along a single route; there is no same-window alternative set, so continuation is not optionality.
- `independent_run_optional_assembly`: Two possible routes are observed in different runs, but the basin never had both available in the same source-current window.
- `maintenance_basin_shift_as_surplus`: The floor is measured on one basin signature and the surplus on another, so the apparent margin is a basin-scope swap.
- `floor_renormalization_as_surplus`: The same basin state is made to look abundant by moving the floor after seeing the run, not by preserving a predeclared margin.
- `post_hoc_surplus_construction`: The surplus margin is narrated after the fact instead of emitted as a predeclared source-current support/floor trace.
- `n23_selection_context_relabel_as_abundance`: A prior collapse/selection artifact is mistaken for a current surplus margin; no N24 maintenance-floor geometry is present.
- `reward_maximization_relabel`: A reward label changes, but the basin does not show surplus and same-window optional branch geometry.
- `missing_maintenance_floor`: Support cannot be called surplus because no predeclared maintenance floor anchors the measurement.
- `missing_boundary_integrity_trace`: The basin opens branches without showing that its boundary remains intact while those branches are available.
- `optional_flux_drains_maintenance_support`: The optional route is geometrically expensive: flux leaves the maintenance basin faster than the surplus margin can sustain.
- `ap4_final_reclassification_relabel`: A bridge-context classification is promoted into a global AP4 result without new N24 surplus geometry.
- `ap5_proxy_gap_omission`: The branch axis is proxy/reward conditioned, but the AP5 target or proxy dependency is not made row-local and auditable.
- `semantic_choice_agency_native_support_phase8_relabels`: A bounded artifact-level geometry condition is promoted into semantic choice, agency, native support, or implementation; none of those are N24 geometric evidence.

## Checks

| Check | Passed |
| --- | --- |
| `source_i1_inventory_passed` | `true` |
| `source_i2_schema_passed` | `true` |
| `source_digest_chain_aligned` | `true` |
| `required_active_null_matrix_complete` | `true` |
| `canonical_controls_covered` | `true` |
| `control_alias_map_documents_broader_controls` | `true` |
| `candidate_evidence_fields_present_in_all_rows` | `true` |
| `row_field_set_equals_i2_required_plus_active_null_extensions` | `true` |
| `schema_instantiated_without_expansion` | `true` |
| `active_null_fixtures_not_positive_evidence` | `true` |
| `all_active_nulls_fail_closed` | `true` |
| `failed_closed_semantics_are_not_positive_demotions` | `true` |
| `surplus_and_optionality_nulls_are_distinct` | `true` |
| `optional_label_and_independent_run_controls_present` | `true` |
| `ap_gap_and_final_ap4_relabel_controls_present` | `true` |
| `artifact_manifest_fields_present_but_not_positive` | `true` |
| `optional_flux_drain_status_scoped` | `true` |
| `no_source_current_inputs_opened` | `true` |
| `no_ab_or_n24c_rungs_above_control_scope` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `geometric_interpretations_present` | `true` |
| `no_local_absolute_paths` | `true` |

## Interpretation

I3 supports only fail-closed false-positive rejection discipline. It
does not support surplus-supported optionality, abundance, reward
maximization, semantic choice, agency, native support, sentience,
Phase 8, or ant-ecology implementation.
