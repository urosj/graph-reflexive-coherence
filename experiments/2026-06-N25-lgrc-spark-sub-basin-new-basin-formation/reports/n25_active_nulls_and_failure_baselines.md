# N25 Iteration 3 - Active Nulls And Failure Baselines

Status: `passed`
Acceptance state: `accepted_active_nulls_fail_closed_no_positive_basin_formation_evidence`
Output digest: `857e88aa4efbbe55458e538a29803e4f7b4731c5bf1872a56c303073797441c9`

## Scope

I3 instantiates false-positive rows only. It does not open source-current
basin-formation evidence and assigns no BF rung above active-null scope.

## Active Null Rows

- `label_only_new_basin`: `failed_closed`; no bifurcation, boundary, support/coherence, or replay distinction trace
- `single_basin_thickening`: `failed_closed`; candidate is not boundary-distinguishable from the old basin
- `reshaped_old_boundary_only`: `failed_closed`; boundary movement is not basin formation
- `merge_leakage_as_basin`: `failed_closed`; merge/leakage margin fails as formation evidence
- `non_replayable_transient`: `failed_closed`; replayable distinction persistence is missing
- `hidden_producer_insertion`: `failed_closed`; producer insertion is not native or producer-assisted formation evidence
- `n24_optionality_relabel`: `failed_closed`; AB5 optionality is prerequisite context only
- `producer_assisted_native_upgrade_relabel`: `failed_closed`; producer-assisted success has a separate ceiling
- `native_flux_debt_omitted`: `failed_closed`; native flux-debt invariant is missing
- `ap_gap_prose_only`: `failed_closed`; row-local AP statuses and reasons are required
- `unsafe_semantic_learning_relabel`: `failed_closed`; N25 basin formation is not semantic learning
- `unsafe_choice_agency_native_support_phase8_relabels`: `failed_closed`; unsafe claim boundary remains false
- `existing_lgrc9v3_spark_examples_skipped`: `failed_closed`; existing native spark mechanisms must be considered first
- `producer_before_native_spark_path`: `failed_closed`; producer extension requires native insufficiency justification

## Geometric Interpretation

These rows reject label-only, thickening-only, boundary-reshaping-only, merge/leakage, transient, hidden-producer, N24-relabel, AP-gap, and unsafe semantic/native-support interpretations before positive probes run.
They also reject bypassing existing LGRC9V3 spark examples or introducing producer spark scaffolds before the native spark path is evaluated.

## Checks

- PASS: `i1_inventory_passed`
- PASS: `i2_schema_passed`
- PASS: `all_required_nulls_present`
- PASS: `all_active_nulls_fail_closed`
- PASS: `failed_open_rows_absent`
- PASS: `no_positive_evidence_opened`
- PASS: `no_bf_rung_above_control_scope`
- PASS: `native_spark_source_skip_null_present`
- PASS: `producer_before_native_spark_path_null_present`
- PASS: `unsafe_claim_flags_false`

## Result

```text
active_null_count = 14
failed_open_rows = []
basin_formation_evidence_opened = false
bf_ceiling = BF0_active_null_control_scope
n25_closeout_ceiling = N25-C1_active_nulls_fail_closed
n25_closeout_ladder_rung_assigned = false
ready_for_iteration_4_native_bifurcation_probe = true
```
