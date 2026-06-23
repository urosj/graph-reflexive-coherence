# N22 Susceptibility Update And Durable Geometry Implementation Checklist

## Initialization

- [x] Create `experiment-N22` branch.
- [x] Create N22 experiment directory.
- [x] Add top-level N22 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N22 scoped to susceptibility update / durable geometry
      modification.
- [x] Confirm N22 starts from N20/N21 handoff evidence, not N22 primitive
      evidence.

## Global Rules

- [ ] Use source IDs, titles, and relative paths only.
- [ ] Confirm generated records contain no local absolute paths.
- [ ] Consume N20 I5 `susceptibility_update` row without redefinition.
- [ ] Consume N21 closeout as prerequisite context only.
- [ ] Confirm N21 WR/ND evidence is not used as susceptibility evidence.
- [ ] Preserve N21 as closed at bounded local `ND5`; do not reopen N21.
- [ ] Record N21 `ND6` bridge status only as a candidate bridge field, not as
      direct N21 closeout.
- [ ] Declare row-specific thresholds before use.
- [ ] Record `source_current_inputs` in every candidate row.
- [ ] Record `row_specific_thresholds_declared_before_use` in every candidate
      row.
- [ ] Require actual LGRC/source-current run artifacts for positive
      susceptibility evidence.
- [ ] Reject report-only or synthetic-row success as insufficient evidence.
- [ ] Separate source-current geometry from route labels and producer
      reinforcement schedules.
- [ ] Treat producer-mediated fields as producer residue unless source-backed
      naturalization evidence is produced.
- [ ] Treat naturalization-debt fields as debt unless source-backed evidence is
      produced.
- [ ] Reject blocked relabel fields when used as evidence.
- [ ] Carry AP4 dependency row-locally when route-conditioned selection
      participates.
- [ ] Carry conditional AP5 dependency when proxy or target formation
      participates.
- [ ] Use closed AP4/AP5 dependency status enums.
- [ ] Record `ap4_condition_reason` and `ap5_condition_reason` per row.
- [ ] Freeze allowed delta fields separately from same-basin invariant fields.
- [ ] Block rows when out-of-scope drift exceeds the declared update scope.
- [ ] Require `delta_not_label_reassignment = true`.
- [ ] Include peer/same-budget comparison for route- or region-conditioned
      susceptibility rows.
- [ ] Record durability metrics and delta digests before closeout.
- [ ] Fail closed on route-label-only success.
- [ ] Fail closed on reinforcement-schedule hidden support.
- [ ] Fail closed on one-window transient success.
- [ ] Fail closed on post-hoc delta construction.
- [ ] Force unsafe claim flags false in every row.
- [ ] Do not modify `src/*`.
- [ ] Do not write ant-ecology implementation specs in N22.
- [ ] Keep semantic learning, choice, agency, native support, sentience, and
      Phase 8 claims blocked.

## Iteration 1. Source Handoff Inventory

- [ ] Build N22 source handoff inventory.
- [ ] Read N20 closeout and N21 handoff.
- [ ] Read N20 I5 same-basin continuation contract.
- [ ] Read N21 closeout and N22 handoff.
- [ ] Record susceptibility-update source row.
- [ ] Record N21 WR6/ND5/N21-C6 context.
- [ ] Record N21 `ND6` blocker and N22 bridge question.
- [ ] Record required source-current fields.
- [ ] Record producer-mediated fields and naturalization-debt fields.
- [ ] Record AP4/AP5 dependency rules.
- [ ] Record required controls.
- [ ] Confirm no susceptibility evidence is opened.
- [ ] Confirm no semantic learning, choice, agency, native support, sentience,
      Phase 8, or ant-ecology claim is opened.

Expected artifacts:

```text
outputs/n22_source_handoff_inventory.json
reports/n22_source_handoff_inventory.md
scripts/build_n22_source_handoff_inventory.py
```

## Iteration 2. Schema, Ladder, And Control Freeze

- [ ] Freeze N22 candidate evidence row schema.
- [ ] Freeze `source_current_inputs` candidate field.
- [ ] Freeze `row_specific_thresholds_declared_before_use` candidate field.
- [ ] Freeze source-current definition.
- [ ] Freeze run-artifact admissibility.
- [ ] Freeze interaction window schema.
- [ ] Freeze later re-entry window schema.
- [ ] Freeze susceptibility delta schema.
- [ ] Freeze allowed delta fields.
- [ ] Freeze same-basin invariant fields.
- [ ] Freeze `out_of_scope_drift_blocks_row`.
- [ ] Freeze `delta_not_label_reassignment`.
- [ ] Freeze peer/same-budget comparison schema.
- [ ] Freeze durability metric schema: interaction, replay, re-entry delta
      digests, persistence ratio, threshold/rule, and transient rejection.
- [ ] Freeze support/coherence/boundary/flux result schema.
- [ ] Freeze artifact replay, snapshot/load replay, and duplicate replay
      requirements.
- [ ] Freeze active-null comparability rule.
- [ ] Freeze local `SU0...SU6` ladder.
- [ ] Freeze AP4/AP5 dependency policy.
- [ ] Freeze AP4/AP5 dependency status enums.
- [ ] Freeze `ap4_condition_reason` and `ap5_condition_reason`.
- [ ] Freeze N21 `ND6` bridge status enum.
- [ ] Freeze row decision policy.
- [ ] Freeze claim boundary and unsafe flags.
- [ ] Confirm no positive N22 evidence is opened.

Expected artifacts:

```text
outputs/n22_susceptibility_schema_and_controls.json
reports/n22_susceptibility_schema_and_controls.md
scripts/build_n22_susceptibility_schema_and_controls.py
```

## Iteration 3. Active Nulls And Failure Baselines

- [ ] Show route-label-only change cannot pass.
- [ ] Show reinforcement-schedule-only change cannot pass.
- [ ] Show one-window flux transient cannot pass as durable modification.
- [ ] Show global drift cannot pass as route- or region-conditioned
      susceptibility.
- [ ] Show same-budget peer route/region change cannot be ignored when it
      carries the same delta.
- [ ] Show missing later re-entry blocks durable susceptibility evidence.
- [ ] Show post-hoc delta construction fails closed.
- [ ] Show hidden producer reinforcement fails closed.
- [ ] Show AP4 dependency omission fails closed when route-conditioned.
- [ ] Show AP5 dependency omission fails closed when proxy-conditioned.
- [ ] Show semantic learning/choice/agency relabels fail closed.
- [ ] Confirm active nulls do not assign SU rungs above control scope.

Expected artifacts:

```text
outputs/n22_active_nulls_and_failure_baselines.json
reports/n22_active_nulls_and_failure_baselines.md
scripts/build_n22_active_nulls_and_failure_baselines.py
```

## Iteration 4. Minimal Susceptibility Update Probe

- [ ] Run first source-backed susceptibility-update candidate.
- [ ] Record pre-interaction geometry trace.
- [ ] Record source-current inputs.
- [ ] Record row-specific thresholds declared before use.
- [ ] Record interaction trace.
- [ ] Record post-interaction geometry trace.
- [ ] Record susceptibility delta trace.
- [ ] Record later route or region re-entry trace.
- [ ] Record allowed delta fields and same-basin invariant fields.
- [ ] Record peer/same-budget comparison when route or region conditioning is
      claimed.
- [ ] Confirm same-basin continuation.
- [ ] Confirm support/coherence/boundary/flux gates.
- [ ] Confirm `derived_report_only = false`.
- [ ] Assign only provisional SU rung pending replay/control matrix.
- [ ] Keep final N22 support blocked pending later iterations.

Expected artifacts:

```text
outputs/n22_minimal_susceptibility_update_probe.json
reports/n22_minimal_susceptibility_update_probe.md
scripts/build_n22_minimal_susceptibility_update_probe.py
```

## Iteration 5. Durability Replay Probe

- [ ] Replay the provisional susceptibility delta.
- [ ] Record interaction delta digest.
- [ ] Record post-replay delta digest.
- [ ] Record re-entry delta digest.
- [ ] Record delta persistence ratio.
- [ ] Record delta threshold or rule.
- [ ] Run artifact-only replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay where applicable.
- [ ] Remove or neutralize producer reinforcement schedule where required.
- [ ] Confirm delta persists without hidden reinforcement.
- [ ] Confirm one-window transient control fails closed.
- [ ] Confirm `one_window_transient_rejected = true`.
- [ ] Keep semantic learning and agency claims blocked.

Expected artifacts:

```text
outputs/n22_durability_replay_probe.json
reports/n22_durability_replay_probe.md
scripts/build_n22_durability_replay_probe.py
```

## Iteration 6. Transfer / Re-entry Probe

- [ ] Declare later route, boundary, corridor, or region re-entry context.
- [ ] Test whether susceptibility delta is expressed in later re-entry.
- [ ] Confirm same-budget peer route/region does not show the same delta unless
      the row is demoted to global drift.
- [ ] Confirm re-entry result is not a label swap.
- [ ] Confirm re-entry result is not producer schedule carryover.
- [ ] Confirm replay and same-basin gates remain in scope.
- [ ] Keep general learning, choice, agency, native support, and Phase 8
      blocked.

Expected artifacts:

```text
outputs/n22_transfer_reentry_probe.json
reports/n22_transfer_reentry_probe.md
scripts/build_n22_transfer_reentry_probe.py
```

## Iteration 7. Replay And Control Matrix

- [ ] Consume all provisional N22 candidate rows.
- [ ] Consume all active-null and failure-baseline rows.
- [ ] Run required replay and negative controls.
- [ ] Record every required control status as `passed`, `failed_closed`,
      `failed_open`, `not_run`, or `not_applicable`.
- [ ] Demote or block rows with failed-open or not-run required controls.
- [ ] Assign I7-consumable SU rungs only after controls.
- [ ] Keep closeout pending Iteration 8.

Expected artifacts:

```text
outputs/n22_replay_and_control_matrix.json
reports/n22_replay_and_control_matrix.md
scripts/build_n22_replay_and_control_matrix.py
```

## Iteration 8. Closeout And N23 Handoff

- [ ] Classify final N22 susceptibility-update result.
- [ ] Record final SU ladder rung.
- [ ] Record producer residue.
- [ ] Record naturalization debt.
- [ ] Record AP4/AP5 dependency status.
- [ ] Record N21 `ND6` bridge status.
- [ ] Record final claim ceiling.
- [ ] Record unsafe claim blockers.
- [ ] Confirm semantic learning, choice, agency, native support, sentience,
      Phase 8, and ant-ecology implementation remain blocked.
- [ ] Confirm `src_diff_empty`.
- [ ] Record N23 handoff for live-continuation collapse / selection geometry.

Expected artifacts:

```text
outputs/n22_closeout_and_n23_handoff.json
reports/n22_closeout_and_n23_handoff.md
scripts/build_n22_closeout_and_n23_handoff.py
```
