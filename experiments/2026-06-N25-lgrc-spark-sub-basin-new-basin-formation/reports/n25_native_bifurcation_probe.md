# N25 Iteration 4 - Native Optional-Branch Bifurcation Probe

Status: `passed`
Acceptance state: `accepted_native_source_current_bf2_bifurcation_partial_pending_i5_controls`
Output digest: `9df1111ec04d785b7f037b208062d1b660faf85a18bbe09a01d24469b4bdd652`

## Scope

I4 runs the native path first. It reuses the existing LGRC9V3 Lane-B
causal spark and active topology integration surfaces instead of adding
producer spark code.

## Result

```text
bf_ceiling = BF2_native_source_current_bifurcation_partial
formation_class = bifurcation_partial
provisional_formation_class_target = sub_basin_candidate
provisional_bf3_candidate_pending_i5 = true
basin_formation_claim_allowed = false
native_flux_debt_bound = 1e-09
native_flux_debt_widened = false
producer_assisted_lane_opened = false
```

## Geometric Interpretation

A Lane-B column-H spark at the saturated root sink routes into an active topology expansion. The old center is replaced by a module with internal edges, giving a source-current boundary candidate. The module has zero-margin support/coherence floors and no replay yet, so this is BF2 with a provisional BF3 target, not stable basin formation.

The spark is not just a report label: the event sequence contains
`lgrc9v3_causal_spark_candidate`, `hybrid_mechanical_expansion`,
`lgrc9v3_refinement_packet_transport`, and proper-time inheritance.
The old root sink is replaced by module nodes and internal edges. That
is enough for BF2 native bifurcation evidence and a provisional BF3
target, but I5 must still test replay, transient rejection, and
merge/leakage controls before any stronger closeout.

The refinement packet transport event is structurally present with
`amount_total = 0.0`. This is recorded as an interpretation boundary:
the packet-triggered spark and mechanical expansion are source-current,
while residual packet transport does not contribute measurable carried
flux in I4. Conservation is therefore read from the expansion budget
trace, where `budget_error = 0.0`.

## Controls

- `label_only_new_basin_rejected`: `passed`; allows BF2 bifurcation evidence; label-only path absent
- `single_basin_thickening_relabel_rejected`: `passed`; permits provisional sub-basin candidate interpretation pending I5
- `reshaped_old_boundary_relabel_rejected`: `passed`; keeps candidate distinct from boundary wrinkle interpretation
- `hidden_producer_insertion_rejected`: `passed`; keeps I4 native-lane only
- `native_flux_debt_remains_row_local`: `passed`; native row remains admissible for BF2
- `n24_optionality_relabel_as_formation_rejected`: `passed`; N24 AB5/N24-C5 remains context only; I4 evidence is not a relabel
- `merge_leakage_masquerading_as_new_basin_rejected`: `not_run`; blocks BF4+ and final BF3 closeout until I5
- `non_replayable_transient_rejected`: `not_run`; blocks BF4+ and final BF3 closeout until I5
- `producer_success_as_native_relabel_control`: `not_applicable`; scope reason: native-only I4 row
- `producer_assisted_success_does_not_overwrite_native_failure`: `not_applicable`; scope reason: producer lane not opened in I4
- `producer_schedule_post_hoc_control`: `not_applicable`; scope reason: native-only I4 row
- `producer_hidden_support_control`: `not_applicable`; scope reason: native-only I4 row
- `producer_threshold_relaxation_control`: `not_applicable`; scope reason: native-only I4 row
- `producer_basin_insertion_without_trace_control`: `passed`; producer insertion without trace remains blocked
- `producer_success_overwrites_native_failure_control`: `not_applicable`; scope reason: native-only I4 row
- `native_spark_source_policy_rejected`: `passed`; native-spark-first policy satisfied
- `producer_before_native_spark_path_rejected`: `passed`; producer-before-native ordering blocked
- `ap4_gap_prose_only_rejected`: `passed`; AP4 gap remains explicit
- `ap5_proxy_target_omission_rejected_when_applicable`: `not_applicable`; scope reason: no AP5-dependent proxy/target formation in I4
- `semantic_learning_relabel_rejected`: `passed`; semantic learning relabel blocked
- `semantic_choice_relabel_rejected`: `passed`; semantic choice relabel blocked
- `agency_relabel_rejected`: `passed`; agency relabel blocked
- `native_support_relabel_rejected`: `passed`; native support relabel blocked
- `phase8_relabel_rejected`: `passed`; Phase 8 relabel blocked
- `ant_ecology_relabel_rejected`: `passed`; ant ecology relabel blocked

## Artifacts

- `bifurcation_trace`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_lgrc9v3_bifurcation_trace.json`
- `merge_leakage_trace`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_merge_leakage_trace.json`
- `native_flux_debt_trace`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_native_flux_debt_trace.json`
- `new_basin_support_coherence_trace`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_new_region_support_coherence_trace.json`
- `new_boundary_candidate_trace`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_new_boundary_candidate_trace.json`
- `old_basin_relation_trace`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_old_basin_relation_trace.json`
- `producer_intervention_ledger`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_empty_producer_intervention_ledger.json`
- `runtime_trace`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_runtime_trace.json`
- `threshold_record`: `experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/outputs/n25_native_bifurcation_probe_artifacts/n25_i4_thresholds_declared_before_use.json`

## Checks

- PASS: `i1_inventory_passed`
- PASS: `i2_schema_passed`
- PASS: `i3_active_nulls_passed`
- PASS: `existing_lgrc9v3_spark_path_reused`
- PASS: `native_flux_debt_preserved`
- PASS: `n20_contract_rows_match_inventory`
- PASS: `n24_optionality_relabel_control_present`
- PASS: `source_current_inputs_non_circular`
- PASS: `runtime_trace_artifact_present`
- PASS: `producer_intervention_ledger_artifact_present`
- PASS: `all_plan_controls_scoped_in_i4`
- PASS: `bf2_formation_class_not_overclaimed`
- PASS: `temporal_window_start_end_fields_present`
- PASS: `source_current_bifurcation_trace_present`
- PASS: `label_and_thickening_controls_absent`
- PASS: `bf_ceiling_conservative`
- PASS: `artifact_manifest_valid`
- PASS: `unsafe_claim_flags_false`
