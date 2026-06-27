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
- [x] Declare row-specific thresholds before positive evidence use.
- [x] Record `source_current_inputs` in every candidate row.
- [x] Require `artifact_manifest` in every candidate row.
- [x] Require `all_artifact_sha256_match_file_contents = true` for positive
      support.
- [x] Require actual LGRC/source-current run artifacts for positive N24
      evidence.
- [x] Reject report-only or synthetic-row success as insufficient evidence.
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
- [x] Record `ap4_condition_reason` and `ap5_condition_reason` per row.
- [x] Freeze maintenance floors before positive probes.
- [x] Require surplus above maintenance floor for AB2+.
- [ ] Require optional continuation set trace for AB3+.
- [ ] Require maintenance support/coherence floors to remain preserved while
      optional branches are open.
- [ ] Require boundary integrity under optionality for AB3+.
- [ ] Require optional flux not to drain maintenance support for AB3+.
- [ ] Require `optionality_not_label_reassignment = true`.
- [x] Block hidden budget relief, floor crossing, proxy-only gain, optional
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
output_digest = df1725c0e726ad233bd57751393e7aa6b0bcf18f7a0d67cdf220e8e3e0e6c503
i1_output_digest = f9293344b8ca23ec14438c3762cd681d9543aaa528f45182b638631af7abde57
source_contract_row_digest = 7f962755c36a8ae6b0acdc831bbdcbecdc6ed6169ac8d7176954cbd900cede84
source_consumable_contract_row_digest = daf53d4eed625cbdda0c391a5371748859f89552ce4bd3bd8aff6f55132e3233
candidate_evidence_required_field_count = 104
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
optional_flux_does_not_drain_maintenance_support_status is frozen so AB2-only
rows can record optional flux as not_run instead of a misleading failed gate.
row_specific_thresholds_declared_before_use is frozen as the expanded threshold
record object with nested declared_before_use=true, not as a bare boolean.
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

Iteration 2 third review follow-up:

```text
support_measurement_scope now uses maintenance_basin_node_set rather than
maintenance_basin_total. The scope names the declared maintenance-basin node
set; support_aggregation_method = min names the statistic over that set.
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

- [x] Build active-null/failure-baseline artifact.
- [x] Instantiate `hidden_budget_relief_as_surplus`.
- [x] Instantiate `floor_crossing_as_abundance`.
- [x] Instantiate `surplus_without_optional_continuation`.
- [x] Instantiate `optionality_without_surplus`.
- [x] Instantiate `proxy_only_optional_branch_gain`.
- [x] Instantiate `optional_branch_label_only`.
- [x] Instantiate `single_branch_relabel_as_optionality`.
- [x] Instantiate `independent_run_optional_assembly`.
- [x] Instantiate `maintenance_basin_shift_as_surplus`.
- [x] Instantiate `floor_renormalization_as_surplus`.
- [x] Instantiate `post_hoc_surplus_construction`.
- [x] Instantiate `n23_selection_context_relabel_as_abundance`.
- [x] Instantiate `reward_maximization_relabel`.
- [x] Instantiate `missing_maintenance_floor`.
- [x] Instantiate `missing_boundary_integrity_trace`.
- [x] Instantiate `optional_flux_drains_maintenance_support`.
- [x] Instantiate `ap4_final_reclassification_relabel`.
- [x] Instantiate `ap5_proxy_gap_omission`.
- [x] Instantiate unsafe semantic/agency/native-support/Phase-8 relabel rows.
- [x] Confirm every active null fails closed.
- [x] Confirm no AB rung above null/control scope is assigned.

Expected artifacts:

```text
outputs/n24_active_nulls_and_failure_baselines.json
reports/n24_active_nulls_and_failure_baselines.md
scripts/build_n24_active_nulls_and_failure_baselines.py
```

Iteration 3 result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_evidence
failed_checks = []
output_digest = 4748bb45748339f13c4ce437b917f7c2f0e33c401cfc058cf211b9393e2494df
row_count = 19
failed_closed_rows = 19
failed_open_rows = 0
positive_abundance_evidence_opened = false
surplus_supported_optionality_supported = false
ab_ladder_rung_assigned_above_control_scope = false
n24_closeout_ladder_rung_assigned = false
n24_closeout_ceiling = N24-C1_active_null_control_discipline_established
final_global_ap4_reclassification_supported = false
ready_for_iteration_4_positive_probe = true
```

Iteration 3 review follow-up:

```text
I3 source chain is reproducible against the current committed I2 artifact:
source_schema_output_digest = df1725c0e726ad233bd57751393e7aa6b0bcf18f7a0d67cdf220e8e3e0e6c503.

A control_alias_map documents the broader canonical controls used by:
  missing_maintenance_floor -> floor_crossing_as_abundance_control
  missing_boundary_integrity_trace -> optional_branch_label_only_control
  optional_flux_drains_maintenance_support -> floor_crossing_as_abundance_control

optional_flux_drain_status distinguishes:
  preserved
  failed
  missing
  not_applicable

This keeps optional-flux interpretation scoped for rows where optionality is
absent, while the original boolean remains a required candidate-row gate for
future positive AB3+ rows.

The report groups rows by blocker family:
  surplus blockers
  optionality blockers
  artifact/provenance blockers
  AP blockers
  unsafe relabel blockers
```

Iteration 3 geometric interpretation:

```text
I3 does not show an abundant basin. It shows what cannot count as abundance.

The geometric blockers are:
  hidden support injected from a producer channel is not surplus;
  branch opening below the maintenance floor is depletion, not abundance;
  surplus without same-window alternatives is only spare support;
  branch labels, proxy gains, reward scores, and independent-run assembly are
  not source-current optional continuation geometry;
  maintenance-basin shifts and floor renormalization create false margins;
  N23 selection context is not N24 surplus evidence;
  missing boundary/flux traces mean the basin did not preserve itself while
  branches were available;
  AP4/AP5 omissions and unsafe semantic/native/Phase-8 relabels remain blocked.

So I3 establishes fail-closed control discipline only:
  N24-C1 active-null/control discipline established,
  no AB evidence opened,
  no surplus-supported optionality supported.
```

## Iteration 4. Minimal Source-Current Surplus Probe

- [x] Run minimal source-current surplus probe.
- [x] Declare maintenance floors before use.
- [x] Record support surplus margin trace.
- [x] Record coherence surplus margin trace if applicable.
- [x] Record maintenance floor trace.
- [x] Record boundary/flux state.
- [x] Confirm hidden budget relief is absent or declared as producer residue.
- [x] Assign at most AB2/provisional AB3 pending optionality/replay/control
      evidence.

Expected artifacts:

```text
outputs/n24_minimal_surplus_probe.json
reports/n24_minimal_surplus_probe.md
scripts/build_n24_minimal_surplus_probe.py
```

Iteration 4 result:

```text
status = passed
acceptance_state = accepted_minimal_source_current_ab2_surplus_candidate_pending_optionality_replay_controls
failed_checks = []
output_digest = 2898f018c650a9d3fe6b93f82a540ae67d8ce8947081573b1e581e6e99afe9a3
candidate_row_count = 1
provisional_ab_ladder_rung = AB2
ab3_or_stronger_supported = false
source_current_surplus_above_floor_observed = true
positive_run_artifacts_consumed = true
source_current_inputs_opened = true
surplus_supported_optionality_claim_allowed = false
ready_for_iteration_5_optional_continuation_probe = true
```

Iteration 4 measured surplus:

```text
model_family = LGRC9V3
fixture = examples/grc9v3/_fixtures.py::make_column_h_state
maintenance_basin_id = n24_i4_core_support_maintenance_basin
maintenance_node_ids = [0, 1, 5, 6, 7, 8, 9]
support_measurement_scope = maintenance_basin_node_set
support_aggregation_method = min
support_floor = 9.85
coherence_floor = 9.85
observed_min_support = 10.0
observed_min_coherence = 10.0
support_surplus_margin = 0.15000000000000036
coherence_surplus_margin = 0.15000000000000036
boundary_integrity_result = preserved
flux_or_leakage_result = preserved
```

Iteration 4 interpretation:

```text
I4 is the first positive N24 source-current row, but it supports only AB2
surplus input evidence.

The surplus is geometric: it is computed from an LGRC9V3 runtime snapshot over
a declared maintenance-basin node set, using the frozen min aggregation method
and predeclared support/coherence floors.

It does not yet support surplus-supported optionality because no same-window
optional continuation set is opened. The surplus-without-optionality control
therefore fails closed as a cap: AB2 may be retained, but AB3+ remains blocked
until I5.

N23 context is recorded directly and remains inherited AP4/context only, not
N24 surplus evidence. AP5 is not applicable because no proxy/reward/target
formation participates.
```

Iteration 4 review follow-up:

```text
I4 records the current source digest chain explicitly:
  i2_output_digest_consumed = df1725c0e726ad233bd57751393e7aa6b0bcf18f7a0d67cdf220e8e3e0e6c503
  i3_output_digest_consumed = 4748bb45748339f13c4ce437b917f7c2f0e33c401cfc058cf211b9393e2494df

The N24 source-current snapshot intentionally matches the N23 I4 pre-collapse
fixture snapshot hash:
  n24_snapshot_sha256 = 9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4
  n23_pre_collapse_snapshot_sha256 = 9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4

This is fixture reuse, not evidence relabeling. N24 re-emits the LGRC state
through its own runtime artifact and does not consume the N23 snapshot as N24
surplus evidence.

For I4, optional flux is not a failed gate:
  optional_flux_does_not_drain_maintenance_support = not_applicable_until_I5
  optional_flux_does_not_drain_maintenance_support_status = not_run

For I4, AP4 is contextual rather than load-bearing:
  ap4_context_status = n23_bridge_candidate_consumed
  ap4_dependency_status = not_applicable
  AP4 becomes load-bearing in I5 rows that actually claim route/branch optionality.

The threshold declaration field now matches the schema:
  row_specific_thresholds_declared_before_use = threshold record object
  row_specific_thresholds_declared_before_use.declared_before_use = true

False rejection flags for optional_branch_label_only_rejected and
independent_run_optional_assembly_rejected mean those controls were not
applicable before optionality was opened, not that those relabel paths are
allowed. surplus_persistence_ratio = 1.0 is a single-snapshot descriptive
placeholder for the preserved surplus row, not replay-backed persistence
evidence.
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
