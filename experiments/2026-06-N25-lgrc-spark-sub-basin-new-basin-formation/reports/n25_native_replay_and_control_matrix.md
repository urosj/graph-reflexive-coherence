# N25 Iteration 5 - Native Replay And Control Matrix

Status: `passed`
Acceptance state: `accepted_native_bf4_replay_control_backed_sub_basin_candidate_zero_margin`
Output digest: `b922ab52e616e94231905e626087c07258aeb2d9adfcee349ab270a386a300db`

## Scope

I5 replays and controls the I4 native candidate. It does not introduce
producer-assisted flux conditioning and it does not run a stress/threshold
matrix.

## Result

```text
bf_ceiling = BF4_native_replay_control_backed_sub_basin_differentiation_candidate
native_bf4_candidate_supported = true
native_bf5_supported = false
zero_margin_native_support_coherence_debt = true
basin_formation_claim_allowed = false
producer_assisted_lane_opened = false
```

## Geometric Interpretation

The same LGRC9V3 spark-to-expansion geometry reappears under duplicate runtime replay and artifact reconstruction. The module boundary, old-center replacement, budget-preserved expansion, and native 1e-9 packet bound are stable, so label-only, thickening, reshaped-boundary, transient, merge/leakage, and hidden-producer interpretations fail closed. The candidate remains narrow because its support/coherence floors have zero margin.

This upgrades I4 from a BF2 native bifurcation partial to a BF4 candidate
because the candidate is replay/control-backed. It does not support BF5
or BF6 because the native support/coherence margins remain zero and no
stress/threshold matrix has been run.

## Controls

- `label_only_new_basin_rejected`: `passed`; label-only path remains blocked
- `single_basin_thickening_relabel_rejected`: `passed`; old-basin-thickening interpretation remains blocked
- `reshaped_old_boundary_relabel_rejected`: `passed`; reshaped-boundary-only interpretation remains blocked
- `merge_leakage_masquerading_as_new_basin_rejected`: `passed`; merge/leakage budget control clean for replay-backed candidate
- `non_replayable_transient_rejected`: `passed`; transient-only interpretation rejected
- `hidden_producer_insertion_rejected`: `passed`; hidden producer path remains blocked
- `native_flux_debt_remains_row_local`: `passed`; native row remains row-local under inherited N24 debt
- `n24_optionality_relabel_as_formation_rejected`: `passed`; N24 optionality remains context only under replay/control
- `producer_assisted_success_does_not_overwrite_native_failure`: `not_applicable`; scope reason: producer lane not opened in I5
- `producer_schedule_post_hoc_control`: `not_applicable`; scope reason: native-only I5 matrix
- `producer_hidden_support_control`: `not_applicable`; scope reason: native-only I5 matrix
- `producer_threshold_relaxation_control`: `not_applicable`; scope reason: native-only I5 matrix
- `producer_basin_insertion_without_trace_control`: `passed`; producer insertion without trace remains blocked
- `producer_success_overwrites_native_failure_control`: `not_applicable`; scope reason: native-only I5 matrix
- `native_spark_source_policy_rejected`: `passed`; native-spark-first policy remains satisfied
- `producer_before_native_spark_path_rejected`: `passed`; producer-before-native ordering remains blocked
- `ap4_gap_prose_only_rejected`: `passed`; AP4 gap remains explicit
- `ap5_proxy_target_omission_rejected_when_applicable`: `not_applicable`; scope reason: no AP5-dependent proxy/target formation in I5
- `semantic_learning_relabel_rejected`: `passed`; semantic learning relabel blocked
- `semantic_choice_relabel_rejected`: `passed`; semantic choice relabel blocked
- `agency_relabel_rejected`: `passed`; agency relabel blocked
- `native_support_relabel_rejected`: `passed`; native support relabel blocked
- `phase8_relabel_rejected`: `passed`; Phase 8 relabel blocked
- `ant_ecology_relabel_rejected`: `passed`; ant ecology relabel blocked
- `producer_success_as_native_relabel_control`: `not_applicable`; scope reason: native-only replay/control matrix

## Replay

- Runtime replay stable: `true`
- Artifact reconstruction stable: `true`
- Replay distinction persistence ratio: `1.0`

## Checks

- PASS: `i1_inventory_passed`
- PASS: `i2_schema_passed`
- PASS: `i3_active_nulls_passed`
- PASS: `i4_native_probe_passed`
- PASS: `duplicate_runtime_replay_stable`
- PASS: `artifact_reconstruction_stable`
- PASS: `required_controls_clean`
- PASS: `all_plan_controls_scoped_in_i5`
- PASS: `merge_leakage_trace_reference_unmodified`
- PASS: `bf4_ceiling_conservative`
- PASS: `zero_margin_debt_preserved`
- PASS: `native_flux_debt_preserved`
- PASS: `n20_contract_rows_match_i4`
- PASS: `n24_optionality_relabel_control_present`
- PASS: `source_current_inputs_non_circular`
- PASS: `artifact_manifest_valid`
- PASS: `unsafe_claim_flags_false`
