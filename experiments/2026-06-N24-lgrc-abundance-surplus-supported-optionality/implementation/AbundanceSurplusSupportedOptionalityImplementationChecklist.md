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
- [x] Require optional continuation set trace for AB3+.
- [x] Require maintenance support/coherence floors to remain preserved while
      optional branches are open.
- [x] Require boundary integrity under optionality for AB3+.
- [x] Require optional flux not to drain maintenance support for AB3+.
- [x] Require `optionality_not_label_reassignment = true`.
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

- [x] Run optional continuation set probe.
- [x] Record optional continuation set trace.
- [x] Record optional branch support/coherence traces.
- [x] Record optional branch boundary/flux traces.
- [x] Confirm maintenance support/coherence floors remain preserved.
- [x] Confirm optional flux does not drain maintenance support below floor.
- [x] Confirm optional branches are not labels, reward/proxy scores, or N23
      relabels.
- [x] Normalize artifact manifest roles against the I2 artifact-role enum.
- [x] Assign at most provisional AB3 pending replay/control matrix.

Expected artifacts:

```text
outputs/n24_optional_continuation_set_probe.json
reports/n24_optional_continuation_set_probe.md
scripts/build_n24_optional_continuation_set_probe.py
```

Iteration 5 result:

```text
status = passed
acceptance_state = accepted_source_current_ab3_optional_continuation_candidate_pending_replay_controls_no_ab4
failed_checks = []
output_digest = 77a9c3027bb8913a6443379cde883d29157026a8fba21aee8aac1795741e75cb
candidate_row_count = 1
provisional_ab_ladder_rung = AB3
ab4_or_stronger_supported = false
ab5_or_stronger_supported = false
source_current_optional_continuation_set_observed = true
optional_continuation_availability_count = 3
jointly_admissible_optional_continuation_count = 0
surplus_supported_optionality_claim_allowed = false
ready_for_iteration_6_replay_control_matrix = true
```

Iteration 5 measured optionality:

```text
model_family = LGRC9V3
fixture = examples/grc9v3/_fixtures.py::make_column_h_state
maintenance_basin_id = n24_i4_core_support_maintenance_basin
maintenance_node_ids = [0, 1, 5, 6, 7, 8, 9]
optional_branch_target_node_ids = [1, 5, 9]
support_floor = 9.85
coherence_floor = 9.85
observed_min_support = 10.0
observed_min_coherence = 10.0
support_surplus_margin = 0.15000000000000036
coherence_surplus_margin = 0.15000000000000036
residual_support_margin_under_optionality = 0.15000000000000036
residual_coherence_margin_under_optionality = 0.15000000000000036
optional_flux_drain_margin = 1e-09
ap4_dependency_status = required_recorded
ap5_dependency_status = not_applicable
```

Iteration 5 interpretation:

```text
I5 is the first positive N24 optionality row. It supports only provisional
AB3 source-current optional continuation evidence.

The optionality is geometric: three center-to-neighbor LGRC edge continuations
to nodes [1, 5, 9] are recorded in the same source-current runtime snapshot
and optionality window. Each branch has source-current support/coherence and
boundary/flux traces, no reward/proxy label, no producer enumeration, and no
independent-run assembly.

The residual support/coherence margins are intentionally conservative. They
use the declared maintenance-basin node-set minimum during the optionality
window, not the stronger branch-target margins.

I5 supports availability, not replay-backed persistence or stress-backed joint
admissibility:
  optional_continuation_availability_count = 3
  jointly_admissible_optional_continuation_count = 0
  replay = not_run

So AB4+ remains blocked until I6 replay/control validation, and AB5+ remains
blocked until stress/threshold evidence.

Because I5 claims route/branch-conditioned optionality, AP4 is load-bearing
as local bridge context:
  ap4_context_status = n23_bridge_candidate_consumed
  ap4_dependency_status = required_recorded

This still does not make final global AP4 reclassification, semantic choice,
reward maximization, agency, native support, sentience, Phase 8, or ant
ecology claims.
```

Iteration 5 review follow-up:

```text
Artifact roles are normalized to the frozen I2 artifact-role enum:
  optional branch support/coherence trace -> optional_branch_trace
  optional branch boundary/flux trace -> optional_branch_trace
  boundary under optionality trace -> boundary_integrity_trace

The row-level trace objects keep more specific subtypes:
  artifact_subtype = optional_branch_support_coherence_trace
  artifact_subtype = optional_branch_boundary_flux_trace
  artifact_subtype = boundary_integrity_under_optionality_trace

I5 now validates this directly:
  artifact_manifest_roles_allowed_by_i2 = true

I5 records the current digest chain:
  i2_output_digest_consumed = df1725c0e726ad233bd57751393e7aa6b0bcf18f7a0d67cdf220e8e3e0e6c503
  i3_output_digest_consumed = 4748bb45748339f13c4ce437b917f7c2f0e33c401cfc058cf211b9393e2494df
  i4_output_digest_consumed = 2898f018c650a9d3fe6b93f82a540ae67d8ce8947081573b1e581e6e99afe9a3

I5 source snapshot reuse is audited:
  n24_i5_snapshot_sha256 = 9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4
  n23_i4_pre_collapse_snapshot_sha256 = 9df7da8c3b53c1c2bf1d5488c28fbdaa61fa8b5fa3a934885c7ff6484f5b22d4
  n23_snapshot_consumed_as_n24_optionality_evidence = false

The shared hash means the same LGRC fixture state is re-emitted by N24, not
that N23 evidence is relabeled as N24 optionality.

surplus_without_optional_continuation_rejected_or_demoted = true means the
control is satisfied because the bad condition is absent in I5. It does not
mean I5 lacks optionality.

I6 must test the availability record rather than merely restate it:
  artifact_replay = passed
  snapshot_load_replay = passed
  duplicate_replay = passed
  optional continuation set survives replay
  branch records remain same-run / same-window
  residual support/coherence margins stay positive
  boundary/flux preservation survives replay
```

## Iteration 6. Replay And Control Matrix

- [x] Replay positive/provisional candidate rows.
- [x] Confirm I5 availability evidence survives artifact replay.
- [x] Confirm I5 availability evidence survives snapshot/load replay.
- [x] Confirm I5 availability evidence survives duplicate replay.
- [x] Confirm replayed optional branch records remain same-run / same-window.
- [x] Confirm replayed residual support/coherence margins stay positive.
- [x] Confirm replayed boundary/flux preservation remains clean.
- [x] Run hidden budget relief control.
- [x] Run floor-crossing control.
- [x] Run proxy-only optional branch gain control.
- [x] Run optional branch label-only control.
- [x] Run single-branch relabel control.
- [x] Run post-hoc surplus construction control.
- [x] Run N23 context relabel control.
- [x] Run reward maximization relabel control.
- [x] Run AP4/AP5 gap controls.
- [x] Run unsafe claim relabel controls.
- [x] Demote rows when replay or controls fail.
- [x] Determine AB4 eligibility.

Expected artifacts:

```text
outputs/n24_replay_and_control_matrix.json
reports/n24_replay_and_control_matrix.md
scripts/build_n24_replay_and_control_matrix.py
```

Iteration 6 result:

```text
status = passed
acceptance_state = accepted_replay_control_backed_ab4_candidate_no_ab5
failed_checks = []
output_digest = da1d7e517c69e3b8e652291f097d973d7a3eea686a7d3245e78e3a05de82a455
artifact_replay_passed = true
snapshot_load_replay_passed = true
duplicate_replay_passed = true
i4_final_consumable_rung = AB2
i5_final_consumable_rung = AB4
provisional_ab_ladder_rung = AB4
ab4_candidate_supported = true
ab5_or_stronger_supported = false
n24_closeout_ladder_rung_assigned = false
provisional_n24_closeout_ceiling = N24-C4
surplus_supported_optionality_claim_allowed = false
ready_for_iteration_7_stress_threshold_matrix = true
```

Iteration 6 replay matrix:

```text
I4:
  candidate = n24_i4_row_01_minimal_source_current_surplus_probe
  artifact_replay = passed
  snapshot_load_replay = passed
  duplicate_replay = passed
  optional_set_survival_replay = not_applicable
  final_consumable_rung = AB2

I5:
  candidate = n24_i5_row_01_source_current_optional_continuation_set_probe
  artifact_replay = passed
  snapshot_load_replay = passed
  duplicate_replay = passed
  optional_set_survival_replay = passed
  final_consumable_rung = AB4
```

Iteration 6 geometric interpretation:

```text
I6 validates that the I5 optional branches are not merely labels. The same
LGRC snapshot reloads, the same maintenance-basin signature reappears, the
same three branch records remain in one source-current window, and
support/coherence margins remain positive.

I4 is replay-stable AB2 surplus evidence only. Its surplus margin replays from
the snapshot, but it has no optional set, so it cannot become AB4 by replay
alone.

I5 becomes a provisional AB4 candidate because the AB3 optional set survives
artifact, snapshot/load, and duplicate replay while hidden-budget,
floor-crossing, proxy-only, label-only, post-hoc, N23 relabel, reward,
AP-gap, and unsafe relabel controls stay closed.

AB5 remains blocked because stress/threshold backing and joint admissibility
under stress are I7 scope. The row is not reward maximization, semantic choice,
agency, native support, sentience, Phase 8, or ant ecology.
```

## Iteration 7. Stress And Threshold Matrix

- [x] Map surplus margin thresholds.
- [x] Map optional branch capacity thresholds.
- [x] Map maintenance floor boundary.
- [x] Map flux/leakage stress boundary.
- [x] Confirm hidden-budget, proxy-only, floor-crossing, and label-only
      controls remain fail-closed under stress.
- [x] Determine whether AB5 is supported or only a narrow AB4 edge case.

Expected artifacts:

```text
outputs/n24_stress_threshold_matrix.json
reports/n24_stress_threshold_matrix.md
scripts/build_n24_stress_threshold_matrix.py
```

Iteration 7 result:

```text
status = passed
acceptance_state = accepted_narrow_at_bound_stress_threshold_backed_ab5_candidate
failed_checks = []
output_digest = 03ec855cec08cc8838599b77356d9b8d132245a68eec276987b15273c663060f
provisional_ab_ladder_rung = AB5
ab4_candidate_supported = true
ab5_candidate_supported = true
ab5_or_stronger_supported = true
n24_closeout_ladder_rung_assigned = false
provisional_n24_closeout_ceiling = N24-C5
surplus_supported_optionality_claim_allowed = false
ready_for_iteration_8_closeout = true
```

Iteration 7 stress boundary:

```text
base_support_margin = 0.15000000000000036
base_coherence_margin = 0.15000000000000036
highest_stress_preserving_minimum_surplus_margin = 0.05
highest_stress_preserving_floor = 0.15

best_combined_per_branch_support_cost = 0.05
best_combined_optional_flux_stress = 1e-09
best_combined_joint_count = 2
```

Iteration 7 interpretation:

```text
I7 supports a narrow, at-bound AB5 candidate. The support-budget axis can
tolerate a small joint branch cost: with per-branch support cost 0.05, two
optional branches remain jointly admissible above the maintenance floor.

The limiting axis is flux/leakage. The frozen flux/leakage bound is 1e-9.
A combined row passes only at that bound:
  optional_flux_stress = 1e-09

Stress above that bound fails closed, so this is not broad abundance
robustness. The correct ceiling is narrow artifact-level threshold-backed
AB5 candidate pending I8 closeout, not reward maximization, semantic choice,
agency, native support, sentience, Phase 8, or ant ecology.
```

## Iteration 5-A. Alternative High-Margin Optionality Probe

- [x] Add an alternative source-current optionality variant.
- [x] Keep the same floor, AB rules, claim boundary, and unsafe blockers.
- [x] Confirm original I5/I6/I7 are not replaced.
- [x] Record the alternative maintenance basin and optional branch set.
- [x] Confirm the alternative margin is higher than I5.
- [x] Assign at most provisional AB3 pending I6-A replay/control.

Expected artifacts:

```text
outputs/n24_optional_continuation_set_probe_i5a.json
reports/n24_optional_continuation_set_probe_i5a.md
scripts/build_n24_optional_continuation_set_probe_i5a.py
```

Iteration 5-A result:

```text
status = passed
acceptance_state = accepted_alternative_high_margin_ab3_optional_continuation_candidate_pending_i6a
failed_checks = []
output_digest = 694994ac8393f7e8a8cd148706d6d8e7caf71da4b9c46fd6e9abc53eb60b6c44
variant_id = i5a_high_margin_target_supported_optional_set
i5_replaced = false
i6_replaced = false
i7_replaced = false
provisional_ab_ladder_rung = AB3
ready_for_iteration_6a_replay_control_matrix = true
```

Iteration 5-A measured margin:

```text
maintenance_basin_id = n24_i5a_high_margin_target_supported_basin
maintenance_node_ids = [1, 5, 9]
optional_branch_target_node_ids = [1, 5, 9]
support_floor = 9.85
coherence_floor = 9.85
observed_min_support = 11.0
observed_min_coherence = 11.0
support_surplus_margin = 1.1500000000000004
coherence_surplus_margin = 1.1500000000000004
```

Iteration 5-A interpretation:

```text
I5-A reuses the same LGRC fixture family but declares a different source-current
maintenance basin over high-support optional target nodes [1, 5, 9]. This
raises the support/coherence margin from I5's 0.15 to 1.15 without changing the
floor, AB ladder, AP boundary, or unsafe claim rules.

This is additional evidence only. It does not replace I5, does not relabel I5,
and does not open AB4/AB5 until replay/control and stress testing run.
```

## Iteration 6-A. Alternative Replay And Control Matrix

- [x] Replay the I5-A high-margin optionality variant.
- [x] Confirm artifact replay passes.
- [x] Confirm snapshot/load replay uses the I5-A maintenance-basin signature.
- [x] Confirm duplicate replay passes.
- [x] Confirm optional set survival replay passes.
- [x] Confirm controls accept the I5-A candidate with no failed-open controls.
- [x] Assign I5-A at most AB4 pending I7-A stress.

Expected artifacts:

```text
outputs/n24_replay_and_control_matrix_i6a.json
reports/n24_replay_and_control_matrix_i6a.md
scripts/build_n24_replay_and_control_matrix_i6a.py
```

Iteration 6-A result:

```text
status = passed
acceptance_state = accepted_i5a_replay_control_backed_ab4_candidate_pending_i7a
failed_checks = []
output_digest = 6a57579a029dd7a5c08bb995e3c455dc44db556f96201dd88db53c78d14169e3
artifact_replay = passed
snapshot_load_replay = passed
duplicate_replay = passed
optional_set_survival_replay = passed
i5a_final_consumable_rung = AB4
ab4_candidate_supported = true
ab5_or_stronger_supported = false
does_not_replace_i6 = true
ready_for_iteration_7a_stress_threshold_matrix = true
```

Iteration 6-A interpretation:

```text
I6-A confirms the high-margin I5-A optional set survives artifact, snapshot/load,
duplicate, and optional-set replay under the same control discipline as I6.

The snapshot/load replay uses the I5-A maintenance-basin signature, not the
original I5 maintenance basin. This avoids silently validating the wrong basin.

This is an alternative AB4 candidate only. It does not replace I6 and does not
open AB5, reward, semantic choice, agency, native support, sentience, Phase 8,
or ant ecology.
```

## Iteration 7-A. Alternative Stress And Threshold Matrix

- [x] Stress-test the I5-A/I6-A high-margin variant.
- [x] Confirm support-budget axis is stronger than I7.
- [x] Confirm the flux/leakage bottleneck remains at the frozen bound.
- [x] Confirm AB5 support is corroborating additional evidence, not replacement.
- [x] Preserve all claim-boundary blockers.

Expected artifacts:

```text
outputs/n24_stress_threshold_matrix_i7a.json
reports/n24_stress_threshold_matrix_i7a.md
scripts/build_n24_stress_threshold_matrix_i7a.py
```

Iteration 7-A result:

```text
status = passed
acceptance_state = accepted_alternative_higher_margin_ab5_candidate_flux_bottleneck_remains
failed_checks = []
output_digest = ea9893c6ec5b195f0ebd11eb20d57f92ea3eb4494495e2f45eb27b9a187f248e
provisional_ab_ladder_rung = AB5
ab4_candidate_supported = true
ab5_candidate_supported = true
ab5_or_stronger_supported = true
does_not_replace_i7 = true
support_axis_stronger_than_i7 = true
flux_axis_bottleneck_remains = true
ready_for_iteration_8_closeout = true
```

Iteration 7-A stress boundary:

```text
best_combined_per_branch_support_cost = 0.5
best_combined_optional_flux_stress = 1e-09
best_combined_joint_count = 2
```

Iteration 7-A interpretation:

```text
I7-A strengthens the support-budget side of N24: the alternative variant keeps
two branches jointly admissible at per-branch cost 0.5, much wider than I7's
0.05.

However, I7-A does not broaden the flux result. The flux axis still only passes
at the frozen 1e-9 bound, and stress above that bound fails closed.

So the strengthened final N24 state is:
  original I7 = narrow at-bound AB5 candidate
  I7-A = higher-margin support-axis AB5 corroboration
  remaining bottleneck = flux/leakage bound

This still does not support reward maximization, semantic choice, agency,
native support, sentience, Phase 8, or ant ecology.
```

## Iteration 7-B. Flux Envelope Probe

- [x] Probe whether current N24 AB5 candidates widen the flux envelope above
      the frozen `1e-9` bound.
- [x] Keep thresholds, support rules, and control policy unchanged.
- [x] Confirm no hidden budget relief, proxy, label-only, or reward relabel can
      create flux readiness.
- [x] Determine whether N24-C6 flux readiness is supported or blocked.

Expected artifacts:

```text
outputs/n24_flux_envelope_probe_i7b.json
reports/n24_flux_envelope_probe_i7b.md
scripts/build_n24_flux_envelope_probe_i7b.py
```

Iteration 7-B result:

```text
status = passed
acceptance_state = accepted_flux_envelope_not_widened_n24c6_flux_blocker_recorded
failed_checks = []
output_digest = 09387f3989903bdb95b58679e9d45c2f93e1ead1788f29dd68977b75224cfe6a
ab5_candidate_supported_from_i7 = true
ab5_candidate_supported_from_i7a = true
flux_envelope_widened = false
n24_c6_flux_readiness_supported = false
n24_c6_blocker = flux_envelope_not_widened_above_1e-9
ready_for_iteration_8_closeout = true
```

Iteration 7-B flux envelope:

```text
flux_or_leakage_bound = 1e-09
all_candidates_pass_at_bound = true
all_candidates_fail_above_bound = true
any_candidate_widens_flux_envelope = false

I7:
  best_preserved_flux = 1e-09
  first_above_bound_failure = 1.01e-09

I7-A:
  best_preserved_flux = 1e-09
  first_above_bound_failure = 1.01e-09
```

Iteration 7-B interpretation:

```text
I7-B confirms the current N24 AB5 candidates pass at the frozen 1e-9 flux bound
but do not widen the flux envelope above it.

This means another I5-B/I6-B/I7-C candidate would need a genuinely different
source-current flux geometry, not just more support margin. The current N24
evidence supports AB5, but it does not support N24-C6 readiness because the
flux/leakage envelope remains unwidened.

The correct closeout target is therefore:
  final_ab_ladder_rung = AB5
  final_n24_closeout_rung = N24-C5
  N25 handoff = explicit flux/leakage debt

This still does not support reward maximization, semantic choice, agency,
native support, sentience, Phase 8, or ant ecology.
```

## Iteration 7-C. Producer-Mediated Flux Conditioning Probe

- [x] Add a declared RC-compatible flux-conditioning producer.
- [x] Keep the native `1e-9` flux/leakage bound unchanged.
- [x] Require source-visible conditioning windows and intervention ledger.
- [x] Confirm the producer adds no support/coherence and does not relax floors.
- [x] Confirm native N24-C6 remains blocked.
- [x] Record producer-mediated flux scaffold as naturalization debt, not native
      abundance robustness.

Expected artifacts:

```text
outputs/n24_producer_flux_conditioning_probe_i7c.json
reports/n24_producer_flux_conditioning_probe_i7c.md
scripts/build_n24_producer_flux_conditioning_probe_i7c.py
```

Iteration 7-C result:

```text
status = passed
acceptance_state = accepted_producer_mediated_flux_conditioning_scaffold_native_c6_still_blocked
failed_checks = []
output_digest = 8b1b1bfab623cd986a317f9b71e49c70d4be445be3683cc36c81175ed25ce0de
producer_mediated_flux_scaffold_supported = true
producer_mediated_flux_envelope_widened = true
highest_producer_conditioned_attempted_flux = 1e-08
native_n24_c6_flux_readiness_supported = false
native_n24_c6_blocker_preserved = flux_envelope_not_widened_above_1e-9
ready_for_iteration_8_closeout = true
```

Iteration 7-C producer contract:

```text
producer_role = producer_mediated_flux_conditioning_surface
producer_kind = rc_compatible_packet_schedule_manager
classification = producer_mediated
substrate_carried_native_evidence = false
max_conditioning_windows = 10
native_flux_or_leakage_bound = 1e-09
thresholds_unchanged = true
support_added = 0.0
coherence_added = 0.0
hidden_budget_relief_allowed = false
floor_relaxation_allowed = false
native_n24c6_relabel_allowed = false
```

Iteration 7-C geometric interpretation:

```text
I7-C shows that the N24 flux bottleneck can be helped by a declared producer
that splits attempted optional flux into source-visible windows. Each
conditioned window remains under the native 1e-9 per-window leakage bound.

This does not make native N24-C6 true. The original I7-B blocker remains:
unconditioned N24 optionality still fails above the 1e-9 flux envelope.

The result is useful because it identifies a precise naturalization target:
native LGRC would need a source-current flux routing or rate-limiting surface
to turn this producer result into native flux readiness.
```

Iteration 7-C closeout effect:

```text
native N24 closeout target remains:
  final_ab_ladder_rung = AB5
  final_n24_closeout_rung = N24-C5

additional producer-mediated handoff:
  producer_assisted_n25_flux_scaffold_candidate = true
  native_flux_leakage_debt = still open
  naturalization_debt = native_flux_routing_or_rate_limiting_surface
```

## Iteration 8. Closeout And N25 Handoff

- [x] Classify final AB ladder rung.
- [x] Classify final N24-C closeout rung.
- [x] Preserve AP4/AP5 ledger.
- [x] Preserve N23 context boundary.
- [x] Confirm final global AP4 reclassification remains unsupported unless a
      source-backed later review explicitly changes it.
- [x] Confirm reward maximization remains unsupported.
- [x] Confirm semantic choice and agency remain unsupported.
- [x] Confirm native support remains unsupported.
- [x] Confirm sentience, Phase 8, and ant ecology remain unopened.
- [x] Confirm `src_diff_empty`.
- [x] Record N25 handoff.

Expected artifacts:

```text
outputs/n24_closeout_and_n25_handoff.json
reports/n24_closeout_and_n25_handoff.md
scripts/build_n24_closeout_and_n25_handoff.py
```

Iteration 8 result:

```text
status = passed
acceptance_state = accepted_ab5_n24c5_closeout_with_producer_flux_scaffold_n25_handoff
failed_checks = []
output_digest = 2301cdb702c935419f4eaeaf9b102cb4a975571beb9fd375baed5ec235edcbb0
final_ab_ladder_rung = AB5
final_n24_closeout_rung = N24-C5
native_n24_c6_supported = false
native_n24_c6_blocker = flux_envelope_not_widened_above_1e-9
producer_mediated_flux_scaffold_supported = true
producer_assisted_n25_flux_scaffold_candidate = true
src_diff_empty = true
```

Final interpretation:

```text
N24 closes natively at AB5 / N24-C5. It supports bounded artifact-level
surplus-supported optionality with replay/control and stress-backed jointly
admissible optional branches.

Native N24-C6 remains blocked because flux/leakage does not widen above the
frozen 1e-9 bound. I7-C adds a producer-mediated scaffold that can condition
attempted optional flux up to 1e-8, but that result remains producer-mediated
and cannot be relabeled as native N24-C6.
```

N25 handoff:

```text
next_experiment = N25_spark_sub_basin_new_basin_formation
handoff_status = ready_with_native_flux_debt_and_producer_scaffold

native_lane:
  consumable_result = AB5_N24-C5_surplus_supported_optionality
  blocking_debt = native_flux_leakage_envelope_not_widened_above_1e-9
  question = Can one N24 optional continuation become a distinguishable
             sub-basin or new-basin candidate while preserving the inherited
             native 1e-9 flux/leakage bound?

producer_assisted_lane:
  consumable_result = producer_mediated_flux_conditioning_scaffold
  naturalization_target = native_flux_routing_or_rate_limiting_surface
  question = Does producer-mediated flux conditioning permit a sub-basin or
             new-basin candidate, and can that mechanism be specified as
             future native LGRC naturalization debt?
```

Claim boundary:

```text
reward_maximization_supported = false
semantic_choice_supported = false
agency_supported = false
native_support_supported = false
sentience_supported = false
phase8_opened = false
ant_ecology_implementation_opened = false
producer_assisted_success_does_not_overwrite_native_failure = true
```
