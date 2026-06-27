# N25 Implementation Checklist - Spark / Sub-Basin / New-Basin Formation

## Global Guards

- [x] Consume N20 contract row `n20_i4_row_06_spark_sub_basin_new_basin_formation`.
- [x] Consume N20 same-basin row `n20_i5_row_06_spark_sub_basin_new_basin_formation`.
- [x] Consume N24 native lane as AB5 / N24-C5 context only.
- [x] Consume N24 I7-C producer-assisted lane separately.
- [x] Preserve native N24 flux/leakage debt row-locally.
- [x] Prevent producer-assisted success from upgrading native N24-C6.
- [x] Prevent producer-assisted success from upgrading native BF.
- [x] Require row-level lane ceilings for every row.
- [x] Prevent N24 optionality from being relabeled as N25 basin formation.
- [x] Record that existing LGRC/LGRC9V3 spark mechanisms are expected and must be checked first.
- [x] Prevent new producer code from being introduced before native spark/example paths are considered.
- [x] Keep AP4/AP5 gap handling row-local.
- [x] Keep agency, semantic choice, native support, sentience, Phase 8, and ant ecology blocked.
- [x] Avoid absolute paths in records.

Global guard freeze note:

```text
Iterations 1 and 2 freeze source consumption, lane separation, row-level lane
ceilings, native flux-debt handling, producer-assisted non-upgrade policy,
formation classifications, artifact roles, AP4/AP5 discipline, and unsafe
claim blockers.
They also freeze the native-spark-first policy: N25 must inspect and reuse
existing LGRC/LGRC9V3 spark mechanisms/examples before adding producer code.

Positive runtime-row obligations remain unchecked until candidate rows exist.
They must be satisfied by I4+ before BF support can be admitted.
```

## Iteration 1. Source And Handoff Inventory

- [x] Read N20 native-function/proxy contract.
- [x] Read N20 same-basin/continuation contract.
- [x] Read N24 closeout and N25 handoff.
- [x] Read N24 I7-C producer flux-conditioning artifact.
- [x] Read `examples/lgrc9v3` spark-related example context.
- [x] Verify N20 spark/sub-basin/new-basin rows exist.
- [x] Verify existing LGRC9V3 spark-ish examples are available.
- [x] Verify N24 native lane is AB5 / N24-C5.
- [x] Verify native N24-C6 is blocked.
- [x] Verify producer-assisted N24 lane is available only as separate scaffold.
- [x] Record source digests and roles.
- [x] Assign no BF rung.
- [x] Open no positive N25 evidence.

Expected artifacts:

```text
outputs/n25_source_handoff_inventory.json
reports/n25_source_handoff_inventory.md
scripts/build_n25_source_handoff_inventory.py
```

Iteration 1 result:

```text
status = passed
acceptance_state = accepted_source_handoff_inventory_no_basin_formation_evidence
failed_checks = []
output_digest = f266f8719937c4d2b84be5c87a1be460bc384d698300dc79ad443c839787bce2
source_contract_row = n20_i4_row_06_spark_sub_basin_new_basin_formation
source_consumable_contract_row = n20_i5_row_06_spark_sub_basin_new_basin_formation
n24_native_lane = AB5_N24-C5_surplus_supported_optionality
n24_native_c6_supported = false
n24_native_flux_debt = flux_envelope_not_widened_above_1e-9
n24_producer_assisted_lane = producer_mediated_flux_conditioning_scaffold
existing_lgrc9v3_spark_examples_available = true
bf_ladder_rung_assigned = false
n25_closeout_ladder_rung = N25-C0_inventory_only
ready_for_iteration_2_schema_freeze = true
```

Iteration 1 interpretation:

```text
I1 is a source handoff inventory only. It validates N20's N25 primitive rows,
consumes N24 native AB5/N24-C5 as prerequisite optionality context, records
N24 native C6 as blocked by the 1e-9 flux/leakage debt, and records I7-C as a
separate producer-assisted flux scaffold. It does not support BF evidence,
new-basin formation, semantic learning, choice, agency, native support,
sentience, Phase 8, or ant ecology.
It also records that native LGRC/LGRC9V3 spark behavior already exists and
must be considered before producer extensions.

Review follow-up:

```text
unsafe_claim_flags now include semantic_learning, reward_maximization, and
ant_ecology_specification in addition to the previous blocked claim set.
```

## Iteration 2. Basin-Formation Schema And Controls

- [x] Freeze positive candidate row schema.
- [x] Freeze lane enum: `native`, `producer_assisted`.
- [x] Freeze row-level lane ceilings.
- [x] Freeze cross-field lane invariants.
- [x] Freeze native-row `n24_producer_lane_status = not_used_in_native_row`.
- [x] Freeze `producer_assisted_result_class` enum.
- [x] Freeze sub-basin versus new-basin definitions.
- [x] Freeze `formation_class` enum.
- [x] Freeze `bifurcation_partial` formation class for BF2 rows.
- [x] Freeze `formation_source` enum.
- [x] Freeze required source-current fields.
- [x] Freeze row-level digest/provenance fields.
- [x] Freeze native spark source policy.
- [x] Freeze temporal/window fields.
- [x] Freeze old-basin/candidate-basin signature digest fields.
- [x] Freeze distinguishability metrics.
- [x] Freeze explicit artifact roles.
- [x] Freeze BF0...BF6 ladder.
- [x] Freeze N25-C0...N25-C6 closeout ladder.
- [x] Freeze native flux debt handling.
- [x] Freeze producer-assisted flux bounds from I1.
- [x] Freeze producer-residue and naturalization-debt classifications.
- [x] Freeze replay requirements.
- [x] Freeze AP4/AP5 dependency statuses.
- [x] Freeze row decision policy.
- [x] Freeze active-null versus positive-row control status semantics.
- [x] Freeze I1-to-I2 control alias map.
- [x] Freeze fail-closed controls.
- [x] Confirm no positive N25 evidence is opened.

Expected artifacts:

```text
outputs/n25_basin_formation_schema_and_controls.json
reports/n25_basin_formation_schema_and_controls.md
scripts/build_n25_basin_formation_schema_and_controls.py
```

Iteration 2 result:

```text
status = passed
acceptance_state = accepted_basin_formation_schema_controls_frozen_no_positive_evidence
failed_checks = []
output_digest = 17511cc4a21aee172d0f80600c55636701e97af4c1c46f6578411b4e97c7192f
bf_ladder_rung_assigned = false
n25_closeout_ladder_rung = N25-C0_schema_only
basin_formation_evidence_opened = false
ready_for_iteration_3_active_nulls = true
```

Iteration 2 interpretation:

```text
I2 freezes the admissibility contract for later N25 rows. Positive candidate
rows must carry explicit native or producer-assisted lane ceilings, formation
class/source enums, distinguishability margins, native flux-debt status,
producer-residue/naturalization-debt records, AP4/AP5 statuses, artifact roles,
and fail-closed controls. It opens no positive basin-formation evidence.

Review follow-up:

```text
I2 now freezes active-null versus positive-row control status semantics:
  active-null false positives expect failed_closed
  positive candidate rows expect blocker absence as passed
  failed_open blocks row and closeout upgrade
  not_run blocks dependent rung
  not_applicable requires scope reason

I2 also freezes I1-to-I2 control aliases, source/provenance digest fields,
artifact path/SHA equality fields, temporal formation windows, old/candidate
basin signature digests, lane cross-field invariants, producer-assisted flux
bounds, and expanded artifact roles.
It additionally freezes that existing LGRC/LGRC9V3 spark examples must be
considered before new producer code is introduced.
Positive rows must use full `control_results`; active-null sentinel values are
allowed only when `schema_instantiation_only = true` and
`positive_evidence_admissible = false`.
```

## Iteration 3. Active Nulls And Failure Baselines

- [x] Instantiate label-only new-basin null.
- [x] Instantiate single-basin thickening relabel null.
- [x] Instantiate reshaped-old-boundary-only null.
- [x] Instantiate merge/leakage-as-basin null.
- [x] Instantiate non-replayable transient null.
- [x] Instantiate hidden producer insertion null.
- [x] Instantiate N24 optionality relabel null.
- [x] Instantiate producer-assisted native-upgrade relabel null.
- [x] Instantiate native flux debt omitted null.
- [x] Instantiate AP gap prose-only null.
- [x] Instantiate unsafe semantic/agency/native-support/Phase-8 relabel nulls.
- [x] Instantiate existing-LGRC9V3-spark-examples-skipped null.
- [x] Instantiate producer-before-native-spark-path null.
- [x] Confirm all fail closed.
- [x] Assign no BF rung above active-null scope.

Expected artifacts:

```text
outputs/n25_active_nulls_and_failure_baselines.json
reports/n25_active_nulls_and_failure_baselines.md
scripts/build_n25_active_nulls_and_failure_baselines.py
```

Iteration 3 result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_basin_formation_evidence
failed_checks = []
output_digest = 857e88aa4efbbe55458e538a29803e4f7b4731c5bf1872a56c303073797441c9
active_null_count = 14
failed_open_rows = []
bf_ceiling = BF0_active_null_control_scope
n25_closeout_ceiling = N25-C1_active_nulls_fail_closed
n25_closeout_ladder_rung_assigned = false
basin_formation_evidence_opened = false
ready_for_iteration_4_native_bifurcation_probe = true
```

Iteration 3 interpretation:

```text
I3 is a pre-positive false-positive rejection artifact. It rejects label-only
new-basin claims, old-basin thickening, reshaped old boundary, merge/leakage,
non-replayable transient sparks, hidden producer insertion, N24 optionality
relabels, producer-assisted native upgrades, omitted native flux debt, prose-only
AP handling, unsafe semantic/native-support claims, and bypassing existing
LGRC9V3 spark examples. It does not provide BF evidence or source-current
basin-formation support.
It also records full `control_results` per null row and clarifies that
`native_flux_debt_omitted` is blocked because the flux-debt record is omitted,
not widened.
The plan I3 list now enumerates all 14 active null rows, including the split
unsafe-claim rows and the two native-spark-first guard rows. I3 rows now also
carry `n20_source_contract_row`, `n20_consumable_contract_row`, `row_digest`,
and a row-level `output_digest` alias for schema-name consistency.
```

## Iteration 4. Native Optional-Branch Bifurcation Probe

- [x] Build source-current native bifurcation probe under N24 native lane.
- [x] Preserve inherited `1e-9` flux/leakage bound.
- [x] Record `native_flux_debt_bound = 1e-9`.
- [x] Record `native_flux_debt_widened = false`.
- [x] Record `native_flux_debt_status`.
- [x] Record bifurcation trace.
- [x] Record new boundary candidate trace.
- [x] Record support/coherence floor traces for candidate region.
- [x] Record old-basin relation trace.
- [x] Record formation class and formation source.
- [x] Record distinguishability margins.
- [x] Reject label-only and old-basin thickening interpretations.
- [x] Keep producer-assisted lane out of native row.

Expected artifacts:

```text
outputs/n25_native_bifurcation_probe.json
reports/n25_native_bifurcation_probe.md
scripts/build_n25_native_bifurcation_probe.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_native_source_current_bf2_bifurcation_partial_pending_i5_controls
output_digest = 9df1111ec04d785b7f037b208062d1b660faf85a18bbe09a01d24469b4bdd652

bf_ceiling = BF2_native_source_current_bifurcation_partial
formation_class = bifurcation_partial
provisional_formation_class_target = sub_basin_candidate
bf_ladder_rung_assigned = false
provisional_bf3_candidate_pending_i5 = true
n25_closeout_ceiling = N25-C2_spark_bifurcation_partial
n25_closeout_ladder_rung_assigned = false
basin_formation_claim_allowed = false

native_flux_debt_bound = 1e-9
native_flux_debt_widened = false
native_flux_debt_status = preserved
producer_assisted_lane_opened = false
```

Review follow-up:

```text
n20_source_contract_row = n20_i4_row_06_spark_sub_basin_new_basin_formation
n20_consumable_contract_row = n20_i5_row_06_spark_sub_basin_new_basin_formation
n24_optionality_relabel_as_formation_rejected = passed
runtime_trace_artifact_role_present = true
source_current_inputs_exclude_generated_i4_outputs = true
source_commit_or_source_digest_uses_file_sha256_map = true
bifurcation_window_has_start_end_step_fields = true
boundary_candidate_window_has_start_end_step_fields = true
boundary_distinguishability_margin_formula_recorded = true
old_basin_separation_margin_kind = binary_indicator
producer_intervention_ledger_artifact_role_present = true
all_plan_controls_scoped_in_i4 = true
refinement_packet_transport_amount_total = 0.0
transport_amount_total_interpretation = structural transport event present; no measurable residual carried flux
```

Geometric interpretation:

```text
I4 reuses the existing LGRC9V3 Lane-B causal spark and active topology
integration path. A packet bounded at the inherited native flux-debt value
1e-9 reaches the saturated root sink. The Lane-B column-H spark fires at the
arrival/local-update boundary, and the active topology path emits a mechanical
expansion. Geometrically, the old root center is replaced by a module with new
module nodes and internal edges, so the result is not a label-only basin and
not merely old-basin thickening.

The result remains BF2 because the new-region support/coherence floor trace is
zero-margin and replay, transient rejection, and merge/leakage controls are not
yet run. I4 therefore records a source-current native bifurcation and a
provisional BF3 target for I5, not stable sub-basin or new-basin formation.
The refinement packet transport event is structurally present with
`amount_total = 0.0`; I4 therefore reads conservation from the expansion budget
trace (`budget_error = 0.0`) rather than treating transport as measurable
residual carried flux.
```

## Iteration 5. Native Replay And Control Matrix

- [x] Replay any native candidate.
- [x] Run label-only control.
- [x] Run thickened-old-basin control.
- [x] Run merge/leakage control.
- [x] Run transient control.
- [x] Run hidden producer control.
- [x] Confirm old-basin thickening, reshaped-boundary, merge/leakage, transient, and label-only blockers are explicit.
- [x] Determine native BF ceiling.

Expected artifacts:

```text
outputs/n25_native_replay_and_control_matrix.json
reports/n25_native_replay_and_control_matrix.md
scripts/build_n25_native_replay_and_control_matrix.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_native_bf4_replay_control_backed_sub_basin_candidate_zero_margin
output_digest = b922ab52e616e94231905e626087c07258aeb2d9adfcee349ab270a386a300db

bf_ceiling = BF4_native_replay_control_backed_sub_basin_differentiation_candidate
native_bf4_candidate_supported = true
native_bf5_supported = false
native_bf6_supported = false
n25_closeout_ceiling = N25-C4_replay_control_backed_sub_basin_differentiation_candidate
n25_closeout_ladder_rung_assigned = false
basin_formation_claim_allowed = false

runtime_replay_stable = true
artifact_reconstruction_stable = true
replay_distinction_persistence_ratio = 1.0
zero_margin_native_support_coherence_debt = true
producer_assisted_lane_opened = false
```

Review follow-up:

```text
n20_source_contract_row = n20_i4_row_06_spark_sub_basin_new_basin_formation
n20_consumable_contract_row = n20_i5_row_06_spark_sub_basin_new_basin_formation
n24_optionality_relabel_as_formation_rejected = passed
source_current_inputs_exclude_generated_i5_outputs = true
native_row_n24_producer_lane_status = not_used_in_native_row
i5_row_control_results_count = 25
i5_control_matrix_trace_count = 25
artifact_reconstruction_source_i4_output_digest_matches_current_i4 = true
merge_leakage_trace_reference_unmodified = true
merge_leakage_i5_control_status = passed
```

Geometric interpretation:

```text
I5 reruns and reconstructs the I4 native LGRC9V3 spark-to-expansion geometry.
The same event sequence, module boundary, old-center replacement,
budget-preserved expansion, native 1e-9 packet bound, and source-current
boundary digest replay deterministically. That rejects the I3 false-positive
families for label-only formation, old-basin thickening, reshaped old boundary,
transient spark, merge/leakage-as-basin, hidden producer insertion, and omitted
native flux debt.

The native ceiling therefore rises from I4 BF2 partial to a BF4
replay/control-backed sub-basin differentiation candidate. It still does not
support BF5 or BF6 because the candidate's support/coherence floors remain
zero-margin and no stress/threshold matrix has been run.
```

## Iteration 6. Producer-Assisted Flux-Conditioned Formation Probe

- [ ] Consume N24 I7-C producer contract.
- [ ] Keep thresholds and floors unchanged.
- [ ] Record producer intervention ledger.
- [ ] Record producer flux window bound.
- [ ] Confirm producer flux window was declared before use.
- [ ] Test producer-assisted bifurcation/sub-basin candidate.
- [ ] Record producer residue and naturalization debt.
- [ ] Run producer schedule post-hoc control.
- [ ] Run producer hidden-support control.
- [ ] Run producer threshold-relaxation control.
- [ ] Run producer basin-insertion-without-trace control.
- [ ] Run producer-success-as-native relabel control.
- [ ] Confirm producer-assisted success does not overwrite native failure.

Expected artifacts:

```text
outputs/n25_producer_assisted_formation_probe.json
reports/n25_producer_assisted_formation_probe.md
scripts/build_n25_producer_assisted_formation_probe.py
```

## Iteration 7. Comparative Stress And Formation Boundary Matrix

- [ ] Compare native and producer-assisted candidates.
- [ ] Preserve native and producer-assisted row ceilings.
- [ ] Stress boundary distinguishability.
- [ ] Stress support/coherence floors.
- [ ] Stress merge/leakage controls.
- [ ] Identify whether producer scaffold points to native naturalization target.
- [ ] Keep unsafe claims false.

Expected artifacts:

```text
outputs/n25_comparative_stress_boundary_matrix.json
reports/n25_comparative_stress_boundary_matrix.md
scripts/build_n25_comparative_stress_boundary_matrix.py
```

## Iteration 8. Closeout And N26 Handoff

- [ ] Classify final BF ladder rung.
- [ ] Classify final N25-C closeout rung.
- [ ] Preserve AP4/AP5 ledger.
- [ ] Preserve N24 native and producer-assisted lane separation.
- [ ] Confirm producer-assisted success does not overwrite native BF or native N24-C6.
- [ ] Confirm final formation classes and sources are recorded.
- [ ] Confirm semantic learning, choice, agency, native support, sentience, Phase 8, and ant ecology remain blocked.
- [ ] Confirm `src_diff_empty`.
- [ ] Record N26 proxy divergence / proxy collapse handoff.

Expected artifacts:

```text
outputs/n25_closeout_and_n26_handoff.json
reports/n25_closeout_and_n26_handoff.md
scripts/build_n25_closeout_and_n26_handoff.py
```
