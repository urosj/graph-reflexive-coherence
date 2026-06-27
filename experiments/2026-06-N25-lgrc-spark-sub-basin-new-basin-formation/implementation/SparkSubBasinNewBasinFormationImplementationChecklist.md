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
- [x] Keep AP4/AP5 gap handling row-local.
- [x] Keep agency, semantic choice, native support, sentience, Phase 8, and ant ecology blocked.
- [x] Avoid absolute paths in records.

Global guard freeze note:

```text
Iterations 1 and 2 freeze source consumption, lane separation, row-level lane
ceilings, native flux-debt handling, producer-assisted non-upgrade policy,
formation classifications, artifact roles, AP4/AP5 discipline, and unsafe
claim blockers.

Positive runtime-row obligations remain unchecked until candidate rows exist.
They must be satisfied by I4+ before BF support can be admitted.
```

## Iteration 1. Source And Handoff Inventory

- [x] Read N20 native-function/proxy contract.
- [x] Read N20 same-basin/continuation contract.
- [x] Read N24 closeout and N25 handoff.
- [x] Read N24 I7-C producer flux-conditioning artifact.
- [x] Verify N20 spark/sub-basin/new-basin rows exist.
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
output_digest = c7ec4d1f1ca359863dab19dac831ac4f6b3a43c712d41715b07c3601ac1aced4
source_contract_row = n20_i4_row_06_spark_sub_basin_new_basin_formation
source_consumable_contract_row = n20_i5_row_06_spark_sub_basin_new_basin_formation
n24_native_lane = AB5_N24-C5_surplus_supported_optionality
n24_native_c6_supported = false
n24_native_flux_debt = flux_envelope_not_widened_above_1e-9
n24_producer_assisted_lane = producer_mediated_flux_conditioning_scaffold
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
- [x] Freeze `producer_assisted_result_class` enum.
- [x] Freeze sub-basin versus new-basin definitions.
- [x] Freeze `formation_class` enum.
- [x] Freeze `formation_source` enum.
- [x] Freeze required source-current fields.
- [x] Freeze row-level digest/provenance fields.
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
output_digest = eef875053c66bc84f0df7b4c3d206d8f342be0e473c9730f328fcc488c9a72ce
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
```

## Iteration 3. Active Nulls And Failure Baselines

- [ ] Instantiate label-only new-basin null.
- [ ] Instantiate single-basin thickening relabel null.
- [ ] Instantiate reshaped-old-boundary-only null.
- [ ] Instantiate merge/leakage-as-basin null.
- [ ] Instantiate non-replayable transient null.
- [ ] Instantiate hidden producer insertion null.
- [ ] Instantiate N24 optionality relabel null.
- [ ] Instantiate producer-assisted native-upgrade relabel null.
- [ ] Instantiate native flux debt omitted null.
- [ ] Instantiate AP gap prose-only null.
- [ ] Instantiate unsafe semantic/agency/native-support/Phase-8 relabel nulls.
- [ ] Confirm all fail closed.
- [ ] Assign no BF rung above active-null scope.

Expected artifacts:

```text
outputs/n25_active_nulls_and_failure_baselines.json
reports/n25_active_nulls_and_failure_baselines.md
scripts/build_n25_active_nulls_and_failure_baselines.py
```

## Iteration 4. Native Optional-Branch Bifurcation Probe

- [ ] Build source-current native bifurcation probe under N24 native lane.
- [ ] Preserve inherited `1e-9` flux/leakage bound.
- [ ] Record `native_flux_debt_bound = 1e-9`.
- [ ] Record `native_flux_debt_widened = false`.
- [ ] Record `native_flux_debt_status`.
- [ ] Record bifurcation trace.
- [ ] Record new boundary candidate trace.
- [ ] Record support/coherence floor traces for candidate region.
- [ ] Record old-basin relation trace.
- [ ] Record formation class and formation source.
- [ ] Record distinguishability margins.
- [ ] Reject label-only and old-basin thickening interpretations.
- [ ] Keep producer-assisted lane out of native row.

Expected artifacts:

```text
outputs/n25_native_bifurcation_probe.json
reports/n25_native_bifurcation_probe.md
scripts/build_n25_native_bifurcation_probe.py
```

## Iteration 5. Native Replay And Control Matrix

- [ ] Replay any native candidate.
- [ ] Run label-only control.
- [ ] Run thickened-old-basin control.
- [ ] Run merge/leakage control.
- [ ] Run transient control.
- [ ] Run hidden producer control.
- [ ] Confirm old-basin thickening, reshaped-boundary, merge/leakage, transient, and label-only blockers are explicit.
- [ ] Determine native BF ceiling.

Expected artifacts:

```text
outputs/n25_native_replay_and_control_matrix.json
reports/n25_native_replay_and_control_matrix.md
scripts/build_n25_native_replay_and_control_matrix.py
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
