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
- [ ] Confirm generated records contain no local absolute paths.
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
- [ ] Use closed AP4/AP5 dependency status enums.
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

## Iteration 1. Source Handoff Inventory

- [ ] Build N24 source handoff inventory.
- [ ] Read N20 closeout and same-basin continuation contract.
- [ ] Read N20 surplus-supported optionality contract row.
- [ ] Read N23 closeout and N24 handoff.
- [ ] Require N23 closeout artifact.
- [ ] Fail closed to `max_ab_rung = AB0` if N23 closeout is missing.
- [ ] Downgrade N23 context if final N23 rungs are below LC6/N23-C6.
- [ ] Record N23 LC6/N23-C6 bounded selection-geometry context.
- [ ] Record N23 AP4 bridge candidate context as context only.
- [ ] Record AP4/AP5 gap discipline.
- [ ] Record required source-current surplus/optionality fields.
- [ ] Record producer-mediated fields and naturalization-debt fields.
- [ ] Record required controls.
- [ ] Confirm no surplus-supported optionality evidence is opened.
- [ ] Confirm no reward maximization, semantic choice, agency, native support,
      sentience, Phase 8, or ant-ecology claim is opened.

Expected artifacts:

```text
outputs/n24_source_handoff_inventory.json
reports/n24_source_handoff_inventory.md
scripts/build_n24_source_handoff_inventory.py
```

## Iteration 2. Schema, Ladder, And Control Freeze

- [ ] Freeze N24 candidate evidence row schema.
- [ ] Freeze `source_current_inputs` candidate field.
- [ ] Freeze `row_specific_thresholds_declared_before_use` candidate field.
- [ ] Freeze `n20_source_downstream_consumption_status`.
- [ ] Freeze `n23_source_closeout_status`.
- [ ] Freeze `n23_ap4_bridge_status`.
- [ ] Split N20 I4 primitive contract row digest from N20 I5 consumable
      same-basin/control contract row digest.
- [ ] Freeze source-current surplus definition.
- [ ] Freeze maintenance floor policy.
- [ ] Freeze numeric surplus formulas before probes.
- [ ] Freeze optional continuation set definition.
- [ ] Freeze original optional continuation set as same-source-current-run only.
- [ ] Freeze declared replay family as replay/stress validation only, not
      original AB3 optionality creation.
- [ ] Freeze optional continuation availability count.
- [ ] Freeze jointly admissible optional continuation count.
- [ ] Freeze `AB3` requirement:
      `optional_continuation_availability_count >= 2`.
- [ ] Freeze `AB5` requirement:
      `jointly_admissible_optional_continuation_count >= 2` under stress.
- [ ] Freeze optional branch record schema.
- [ ] Freeze operational optionality acceptance gates.
- [ ] Freeze surplus budget owner enum.
- [ ] Freeze surplus budget owner rung ceilings.
- [ ] Freeze hidden budget relief blocker.
- [ ] Freeze reward/proxy label blocker.
- [ ] Freeze surplus-without-optionality demotion/block rule.
- [ ] Freeze optionality-without-surplus blocker.
- [ ] Freeze independent-run optional assembly blocker.
- [ ] Freeze maintenance basin shift blocker.
- [ ] Freeze floor renormalization blocker.
- [ ] Freeze run-artifact admissibility.
- [ ] Freeze artifact manifest schema.
- [ ] Freeze artifact path and SHA equality with manifest path and SHA fields.
- [ ] Freeze artifact role enum and positive-support artifact role restrictions.
- [ ] Freeze optionality window schema.
- [ ] Freeze support/coherence/boundary/flux result schema.
- [ ] Freeze replay requirements.
- [ ] Freeze `failed_closed` semantics as a satisfied negative control, not
      automatic positive-candidate demotion.
- [ ] Freeze active-null comparability rule.
- [ ] Freeze local `AB0...AB6` ladder.
- [ ] Freeze `AB0...AB6` rung support requirements.
- [ ] Freeze that rows below `AB3` cannot support optionality.
- [ ] Freeze that `AB6` is an N25 handoff rung, not agency or semantic choice.
- [ ] Freeze N24 closeout ladder `N24-C0...N24-C6`.
- [ ] Freeze AP4/AP5 dependency policy.
- [ ] Freeze AP4/AP5 dependency status enums.
- [ ] Freeze `ap4_context_status` enum.
- [ ] Freeze `final_global_ap4_reclassification_supported = false`.
- [ ] Freeze row decision policy.
- [ ] Freeze claim boundary and unsafe flags.
- [ ] Confirm no positive N24 evidence is opened.

Expected artifacts:

```text
outputs/n24_abundance_schema_and_controls.json
reports/n24_abundance_schema_and_controls.md
scripts/build_n24_abundance_schema_and_controls.py
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
