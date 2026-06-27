# N24 Abundance Surplus-Supported Optionality Implementation Checklist

## Initialization

- [x] Create `experiment-N24` branch.
- [x] Create N24 experiment directory.
- [x] Add top-level N24 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N24 scoped to abundance / surplus-supported optionality.
- [x] Confirm N24 starts from N20/N23 handoff evidence, not N24 primitive
      evidence.

## Global Rules

- [x] Use source IDs, titles, and relative paths only.
- [x] Confirm generated records contain no local absolute paths.
- [x] Consume N20 `surplus_supported_optionality` contract without
      redefinition.
- [x] Consume N23 closeout as prerequisite context only.
- [x] Make N23 context consumption conditional on source-inventory validation.
- [x] Confirm N23 live-continuation collapse evidence is not used as N24
      abundance evidence.
- [x] Treat N19/N23 AP context as AP-gap boundary/context only, not final global
      AP4 reclassification.
- [x] Record `n20_source_downstream_consumption_status` when inherited.
- [x] Record `n23_source_closeout_status` when inherited.
- [x] Record `n23_ap4_bridge_status` when inherited.
- [ ] Declare row-specific thresholds before positive evidence use.
- [ ] Record `source_current_inputs` in every candidate row.
- [ ] Require `artifact_manifest` in every candidate row.
- [ ] Require `all_artifact_sha256_match_file_contents = true` for positive
      support.
- [ ] Require actual LGRC/source-current run artifacts for positive N24
      evidence.
- [ ] Reject report-only or synthetic-row success as insufficient evidence.
- [x] Separate source-current optionality geometry from branch labels, reward
      labels, and producer enumeration.
- [x] Treat producer-mediated optionality enumeration or exploration schedules
      as producer residue unless source-backed naturalization evidence is
      produced.
- [x] Treat naturalization-debt fields as debt unless source-backed evidence is
      produced.
- [x] Reject blocked relabel fields when used as evidence.
- [x] Carry AP4 bridge context without final global AP4 reclassification.
- [x] Carry conditional AP5 dependency when proxy/reward/target formation
      participates.
- [x] Use closed AP4/AP5 dependency status enums.
- [ ] Record `ap4_condition_reason` and `ap5_condition_reason` per row.
- [ ] Freeze maintenance floors before positive probes.
- [ ] Require surplus above maintenance floor for AB2+.
- [ ] Require optional continuation set trace for AB3+.
- [ ] Require maintenance support/coherence floors to remain preserved while
      optional branches are open.
- [ ] Require boundary integrity under optionality for AB3+.
- [ ] Require optional flux not to drain maintenance support for AB3+.
- [ ] Require `optionality_not_label_reassignment = true`.
- [ ] Block hidden budget relief, floor crossing, proxy-only gain, optional
      label-only rows, post-hoc surplus, N23 relabel, reward relabel, agency
      relabel, native-support relabel, and Phase 8 relabel controls.
- [x] Force unsafe claim flags false in every row.
- [x] Do not modify `src/*` for scaffold creation.
- [x] Do not write ant-ecology implementation specs in N24.
- [x] Keep reward maximization, semantic choice, intention, agency, native
      support, sentience, and Phase 8 claims blocked.

Global-rule freeze note:

```text
Iteration 2 freezes the schema for row-specific threshold declaration,
source_current_inputs, artifact manifests, SHA validation, source-current
artifact admissibility, report-only rejection, AP condition reasons,
maintenance floors, AB2/AB3 gates, boundary/flux preservation,
optionality_not_label_reassignment, and fail-closed controls.

Unchecked runtime-row obligations remain unchecked until candidate rows exist.
They must be satisfied by later positive rows before AB support can be admitted.
```

## Iteration 1. Source Handoff Inventory

- [x] Build N24 source handoff inventory.
- [x] Read N20 closeout and same-basin continuation contract.
- [x] Read N20 surplus-supported optionality contract row.
- [x] Read N23 closeout and N24 handoff.
- [x] Require N23 closeout artifact.
- [x] Fail closed to `max_ab_rung = AB0` if N23 closeout is missing.
- [x] Downgrade N23 context if final N23 rungs are below LC6/N23-C6.
- [x] Record N23 LC6/N23-C6 bounded selection-geometry context.
- [x] Record N23 AP4 bridge candidate context as context only.
- [x] Record AP4/AP5 gap discipline.
- [x] Record required source-current surplus/optionality fields.
- [x] Record producer-mediated fields and naturalization-debt fields.
- [x] Record required controls.
- [x] Confirm no surplus-supported optionality evidence is opened.
- [x] Confirm no reward maximization, semantic choice, agency, native support,
      sentience, Phase 8, or ant-ecology claim is opened.

Expected artifacts:

```text
outputs/n24_source_handoff_inventory.json
reports/n24_source_handoff_inventory.md
scripts/build_n24_source_handoff_inventory.py
```

Iteration 1 result:

```text
status = passed
acceptance_state = accepted_source_handoff_inventory_no_surplus_optionality_evidence
failed_checks = []
output_digest = f9293344b8ca23ec14438c3762cd681d9543aaa528f45182b638631af7abde57
source_contract_row = n20_i4_row_05_surplus_supported_optionality
source_consumable_contract_row = n20_i5_row_05_surplus_supported_optionality
n20_contract_status = complete
n23_closeout_validated = true
n23_context_consumption = n23_bridge_candidate_consumed
final_supported_lc_ladder_rung = LC6
final_n23_closeout_ladder_rung = N23-C6
n23_ap4_bridge_status = bridge_candidate_supported
final_global_ap4_reclassification_supported = false
ab_ladder_rung_assigned = false
n24_closeout_ladder_rung = N24-C0_inventory_only
ready_for_iteration_2_schema_freeze = true
```

Iteration 1 review follow-up:

```text
final_global_ap4_reclassification_supported now defaults fail-closed to false
if the N23 source field is missing.

N23 downgrade path is implemented:
  validated LC6/N23-C6 -> n23_bridge_candidate_consumed
  lower present closeout -> bounded_lower_rung_context_only
  missing/invalid closeout -> not_available
```

Iteration 1 interpretation:

```text
I1 is a source handoff inventory only. It confirms that N24 has a complete N20
surplus-supported optionality contract, validates N23 closeout as conditional
bounded LC6/N23-C6 selection-geometry context, and preserves the AP4/AP5
boundary. It does not support surplus margin, optional continuation space, an
AB rung, reward maximization, semantic choice, agency, native support,
sentience, Phase 8, or ant ecology.
```

## Iteration 2. Schema, Ladder, And Control Freeze

- [x] Freeze N24 candidate evidence row schema.
- [x] Freeze `source_current_inputs` candidate field.
- [x] Freeze `row_specific_thresholds_declared_before_use` candidate field.
- [x] Freeze `n20_source_downstream_consumption_status`.
- [x] Freeze `n23_source_closeout_status`.
- [x] Freeze `n23_ap4_bridge_status`.
- [x] Split N20 I4 primitive contract row digest from N20 I5 consumable
      same-basin/control contract row digest.
- [x] Freeze source-current surplus definition.
- [x] Freeze maintenance floor policy.
- [x] Freeze numeric surplus formulas before probes.
- [x] Freeze optional continuation set definition.
- [x] Freeze original optional continuation set as same-source-current-run only.
- [x] Freeze declared replay family as replay/stress validation only, not
      original AB3 optionality creation.
- [x] Freeze optional continuation availability count.
- [x] Freeze jointly admissible optional continuation count.
- [x] Freeze `AB3` requirement:
      `optional_continuation_availability_count >= 2`.
- [x] Freeze `AB5` requirement:
      `jointly_admissible_optional_continuation_count >= 2` under stress.
- [x] Freeze optional branch record schema.
- [x] Freeze operational optionality acceptance gates.
- [x] Freeze surplus budget owner enum.
- [x] Freeze surplus budget owner rung ceilings.
- [x] Freeze hidden budget relief blocker.
- [x] Freeze reward/proxy label blocker.
- [x] Freeze surplus-without-optionality demotion/block rule.
- [x] Freeze optionality-without-surplus blocker.
- [x] Freeze independent-run optional assembly blocker.
- [x] Freeze maintenance basin shift blocker.
- [x] Freeze floor renormalization blocker.
- [x] Freeze run-artifact admissibility.
- [x] Freeze artifact manifest schema.
- [x] Freeze artifact path and SHA equality with manifest path and SHA fields.
- [x] Freeze artifact role enum and positive-support artifact role restrictions.
- [x] Freeze optionality window schema.
- [x] Freeze support/coherence/boundary/flux result schema.
- [x] Freeze replay requirements.
- [x] Freeze `failed_closed` semantics as a satisfied negative control, not
      automatic positive-candidate demotion.
- [x] Freeze active-null comparability rule.
- [x] Freeze local `AB0...AB6` ladder.
- [x] Freeze `AB0...AB6` rung support requirements.
- [x] Freeze that rows below `AB3` cannot support optionality.
- [x] Freeze that `AB6` is an N25 handoff rung, not agency or semantic choice.
- [x] Freeze N24 closeout ladder `N24-C0...N24-C6`.
- [x] Freeze AP4/AP5 dependency policy.
- [x] Freeze AP4/AP5 dependency status enums.
- [x] Freeze `ap4_context_status` enum.
- [x] Freeze `final_global_ap4_reclassification_supported = false`.
- [x] Freeze row decision policy.
- [x] Freeze claim boundary and unsafe flags.
- [x] Confirm no positive N24 evidence is opened.

Expected artifacts:

```text
outputs/n24_abundance_schema_and_controls.json
reports/n24_abundance_schema_and_controls.md
scripts/build_n24_abundance_schema_and_controls.py
```

Iteration 2 result:

```text
status = passed
acceptance_state = accepted_abundance_schema_and_controls_frozen_no_surplus_optionality_evidence
failed_checks = []
output_digest = d4f82aeebdcd975e02058ce85b6682ee6e6a687ea5f65ae45e49966761012d22
i1_output_digest = f9293344b8ca23ec14438c3762cd681d9543aaa528f45182b638631af7abde57
source_contract_row_digest = 7f962755c36a8ae6b0acdc831bbdcbecdc6ed6169ac8d7176954cbd900cede84
source_consumable_contract_row_digest = daf53d4eed625cbdda0c391a5371748859f89552ce4bd3bd8aff6f55132e3233
candidate_evidence_required_field_count = 103
AB_ladder_frozen = true
N24_C_ladder_frozen = true
surplus_formulas_frozen = true
optional_branch_record_schema_frozen = true
original_optional_set_same_run_only = true
declared_replay_family_cannot_create_AB3_original_set = true
final_global_ap4_reclassification_supported = false
primitive_evidence_opened = false
ab_ladder_rung_assigned = false
ready_for_iteration_3_active_nulls = true
```

Iteration 2 review follow-up:

```text
direct N23 closeout artifact is recorded in source_artifacts with SHA/digest.
source_current_inputs are split from source_current_required_fields.
surplus_channel_policy is frozen as:
  support_surplus_required_and_coherence_floor_preserved
optional_branch_evidence_mode is frozen with rung effects.
control_results are list records with control_id/status/condition/result/rung effect.
reward_maximization_claim_allowed = false is row-local.
final_global_ap4_reclassification_supported = false is row-local.
N23/AP4 context cross-field invariants are frozen.
support measurement scope and aggregation method are frozen.
```

Iteration 2 second review follow-up:

```text
Plan required evidence fields are synchronized with the implementation schema:
source_current_required_fields, maintenance_basin_id,
maintenance_basin_signature_digest, support_measurement_scope,
support_aggregation_method, surplus_channel_policy,
optional_branch_evidence_mode, reward_maximization_claim_allowed, and
final_global_ap4_reclassification_supported are all explicit row fields.

optional_continuation_count is descriptive only. AB3 uses
optional_continuation_availability_count, and AB5 uses
jointly_admissible_optional_continuation_count.

same_basin_rule_freeze embeds the inherited N20 I5 same-basin rule content,
not just a pointer.

control_results not_applicable policy requires a scope reason and affected
rung, and cannot satisfy required AB4/AB5 controls.

AB3 replay interaction is frozen: replay is not required for provisional AB3,
but replay is required for AB4+ and cannot create the original AB3 optional
set after the fact.

output_digest is computed over the final artifact state with output_digest
itself excluded.
```

Iteration 2 interpretation:

```text
I2 is a schema/control freeze only. It makes later N24 evidence fail closed
unless surplus formulas, same-run original optionality, AB3/AB5 count gates,
surplus budget ownership, artifact admissibility, AP4/AP5 status, replay, and
negative controls are all satisfied. It blocks hidden budget relief, floor
crossing, proxy-only gain, optional labels, independent-run assembly,
maintenance-basin shift, floor renormalization, N23 context relabeling, reward
maximization, semantic choice, agency, native support, Phase 8, and ant
ecology. No positive N24 evidence is opened.
```

## Iteration 3. Active Nulls And Failure Baselines

- [ ] Build active-null/failure-baseline artifact.
- [ ] Instantiate `hidden_budget_relief_as_surplus`.
- [ ] Instantiate `floor_crossing_as_abundance`.
- [ ] Instantiate `surplus_without_optional_continuation`.
- [ ] Instantiate `optionality_without_surplus`.
- [ ] Instantiate `proxy_only_optional_branch_gain`.
- [ ] Instantiate `optional_branch_label_only`.
- [ ] Instantiate `single_branch_relabel_as_optionality`.
- [ ] Instantiate `independent_run_optional_assembly`.
- [ ] Instantiate `maintenance_basin_shift_as_surplus`.
- [ ] Instantiate `floor_renormalization_as_surplus`.
- [ ] Instantiate `post_hoc_surplus_construction`.
- [ ] Instantiate `n23_selection_context_relabel_as_abundance`.
- [ ] Instantiate `reward_maximization_relabel`.
- [ ] Instantiate `missing_maintenance_floor`.
- [ ] Instantiate `missing_boundary_integrity_trace`.
- [ ] Instantiate `optional_flux_drains_maintenance_support`.
- [ ] Instantiate `ap4_final_reclassification_relabel`.
- [ ] Instantiate `ap5_proxy_gap_omission`.
- [ ] Instantiate unsafe semantic/agency/native-support/Phase-8 relabel rows.
- [ ] Confirm every active null fails closed.
- [ ] Confirm no AB rung above null/control scope is assigned.

Expected artifacts:

```text
outputs/n24_active_nulls_and_failure_baselines.json
reports/n24_active_nulls_and_failure_baselines.md
scripts/build_n24_active_nulls_and_failure_baselines.py
```

## Iteration 4. Minimal Source-Current Surplus Probe

- [ ] Run minimal source-current surplus probe.
- [ ] Declare maintenance floors before use.
- [ ] Record support surplus margin trace.
- [ ] Record coherence surplus margin trace if applicable.
- [ ] Record maintenance floor trace.
- [ ] Record boundary/flux state.
- [ ] Confirm hidden budget relief is absent or declared as producer residue.
- [ ] Assign at most AB2/provisional AB3 pending optionality/replay/control
      evidence.

Expected artifacts:

```text
outputs/n24_minimal_surplus_probe.json
reports/n24_minimal_surplus_probe.md
scripts/build_n24_minimal_surplus_probe.py
```

## Iteration 5. Optional Continuation Set Probe

- [ ] Run optional continuation set probe.
- [ ] Record optional continuation set trace.
- [ ] Record optional branch support/coherence traces.
- [ ] Record optional branch boundary/flux traces.
- [ ] Confirm maintenance support/coherence floors remain preserved.
- [ ] Confirm optional flux does not drain maintenance support below floor.
- [ ] Confirm optional branches are not labels, reward/proxy scores, or N23
      relabels.
- [ ] Assign at most provisional AB3 pending replay/control matrix.

Expected artifacts:

```text
outputs/n24_optional_continuation_set_probe.json
reports/n24_optional_continuation_set_probe.md
scripts/build_n24_optional_continuation_set_probe.py
```

## Iteration 6. Replay And Control Matrix

- [ ] Replay positive/provisional candidate rows.
- [ ] Run hidden budget relief control.
- [ ] Run floor-crossing control.
- [ ] Run proxy-only optional branch gain control.
- [ ] Run optional branch label-only control.
- [ ] Run single-branch relabel control.
- [ ] Run post-hoc surplus construction control.
- [ ] Run N23 context relabel control.
- [ ] Run reward maximization relabel control.
- [ ] Run AP4/AP5 gap controls.
- [ ] Run unsafe claim relabel controls.
- [ ] Demote rows when replay or controls fail.
- [ ] Determine AB4 eligibility.

Expected artifacts:

```text
outputs/n24_replay_and_control_matrix.json
reports/n24_replay_and_control_matrix.md
scripts/build_n24_replay_and_control_matrix.py
```

## Iteration 7. Stress And Threshold Matrix

- [ ] Map surplus margin thresholds.
- [ ] Map optional branch capacity thresholds.
- [ ] Map maintenance floor boundary.
- [ ] Map flux/leakage stress boundary.
- [ ] Confirm hidden-budget, proxy-only, floor-crossing, and label-only
      controls remain fail-closed under stress.
- [ ] Determine whether AB5 is supported or only a narrow AB4 edge case.

Expected artifacts:

```text
outputs/n24_stress_threshold_matrix.json
reports/n24_stress_threshold_matrix.md
scripts/build_n24_stress_threshold_matrix.py
```

## Iteration 8. Closeout And N25 Handoff

- [ ] Classify final AB ladder rung.
- [ ] Classify final N24-C closeout rung.
- [ ] Preserve AP4/AP5 ledger.
- [ ] Preserve N23 context boundary.
- [ ] Confirm final global AP4 reclassification remains unsupported unless a
      source-backed later review explicitly changes it.
- [ ] Confirm reward maximization remains unsupported.
- [ ] Confirm semantic choice and agency remain unsupported.
- [ ] Confirm native support remains unsupported.
- [ ] Confirm sentience, Phase 8, and ant ecology remain unopened.
- [ ] Confirm `src_diff_empty`.
- [ ] Record N25 handoff.

Expected artifacts:

```text
outputs/n24_closeout_and_n25_handoff.json
reports/n24_closeout_and_n25_handoff.md
scripts/build_n24_closeout_and_n25_handoff.py
```
