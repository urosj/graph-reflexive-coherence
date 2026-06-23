# N21 Withdrawal Resistance And Naturalization Depth Implementation Checklist

## Initialization

- [x] Create `experiment-N21` branch.
- [x] Create N21 experiment directory.
- [x] Add top-level N21 `README.md`.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add `configs/`, `hypotheses/`, `outputs/`, `reports/`, and `scripts/`
      scaffolds.
- [x] Add hypothesis records.
- [x] Keep N21 scoped to withdrawal resistance and naturalization depth.
- [x] Confirm N21 starts from N20 contract evidence, not primitive evidence.

## Global Rules

- [x] Use source IDs, titles, and relative paths only.
- [x] Confirm generated records contain no local absolute paths.
- [x] Consume N20 I5 withdrawal-resistance row without redefinition.
- [x] Consume N20 I5 naturalization-depth row without redefinition.
- [x] Declare row-specific thresholds before use.
- [x] Require actual LGRC/source-current run artifacts for positive primitive
      evidence.
- [x] Reject report-only or synthetic-row success as insufficient evidence.
- [x] Separate N20 contract evidence from N21 primitive evidence.
- [x] Treat producer-mediated fields as producer residue unless source-backed
      naturalization evidence is produced.
- [x] Treat naturalization-debt fields as debt unless source-backed
      naturalization evidence is produced.
- [x] Reject blocked relabel fields when used as evidence.
- [ ] Fail closed on hidden producer support.
- [ ] Fail closed on proxy-only success.
- [ ] Fail closed on label-only continuation.
- [ ] Fail closed on post-hoc trace construction.
- [x] Force unsafe claim flags false in every row.
- [x] Do not modify `src/*`.
- [x] Do not write ant-ecology implementation specs in N21.
- [x] Keep agency, native support, sentience, and Phase 8 claims blocked.

## Iteration 1. Source Contract Inventory

- [x] Build N21 source contract inventory.
- [x] Read N20 closeout and N21 handoff.
- [x] Read N20 I5 same-basin continuation contract.
- [x] Record withdrawal-resistance source row.
- [x] Record naturalization-depth source row.
- [x] Record N21 readiness gates.
- [x] Record source-current fields, producer-mediated fields, naturalization
      debt fields, and blocked relabel fields.
- [x] Record required controls for each primitive.
- [x] Confirm no primitive evidence is opened.
- [x] Confirm no agency, native support, sentience, Phase 8, or ant-ecology
      implementation claim is opened.

Expected artifacts:

```text
outputs/n21_source_contract_inventory.json
reports/n21_source_contract_inventory.md
scripts/build_n21_source_contract_inventory.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_source_contract_inventory_no_primitive_evidence
artifact = outputs/n21_source_contract_inventory.json
report = reports/n21_source_contract_inventory.md
script = scripts/build_n21_source_contract_inventory.py
command = .venv/bin/python experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/scripts/build_n21_source_contract_inventory.py
row_count = 2
output_digest = d7b7a37bc0781aedbe6f83c5b55ff8805bf559fe7d684c5e1d2a9be8a7cef3ee
artifact_sha256 = 9c4b35fad34d5bc1ec3cf740cd475f30b21ff4ee51a82ee0d148e2111769eb6e
report_sha256 = df1332a1901095249411394565e2a5a0afda8d65668aa3ed4daaa007ab4ee102
script_sha256 = 24dc7385f33f035358b336099210ef251687fd452d33817383c7cc6780536efd
failed_checks = []
check_count = 21
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
n21_closeout_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
source_contract_inventory_only = true
ready_for_iteration_2_schema_freeze = true
```

Iteration 1 is source-contract inventory only. It confirms N20 closeout marks
N21 ready, the required I5 rows exist and are complete, both rows are consumed
without redefinition, source-current fields and producer/debt/relabel fields are
recorded, required controls are listed, and no primitive evidence or unsafe
claim is opened. N20 contract completeness defines eligibility only; it does
not assign WR, ND, or N21-C ladder rungs.

Post-review tightening record:

```text
global_unsafe_claim_flags cover all blocked claims = true
row_specific_blocked_relabels separated from global unsafe flags = true
row_decision = not_applicable for inventory rows = true
inventory_decision = supported_as_contract_input_only = true
controls_declared_fail_closed_in_contract = true
control_execution_status = not_run
n20_source_downstream_consumption_status marked as inherited source status = true
markdown roadmap/handoff sources context-only = true
I2 artifact path/digest fail-closed requirements added = true
```

## Iteration 2. Withdrawal And Naturalization Schema Freeze

- [x] Freeze N21 row schema.
- [x] Freeze full candidate evidence row schema with every required evidence
      field.
- [x] Freeze `same_basin_continuation_rule` as an explicit candidate row
      schema field.
- [x] Freeze `primitive_claim_allowed` as an explicit candidate row schema
      field.
- [x] Freeze `claim_ceiling` as an explicit candidate row schema field.
- [x] Freeze I1 `same_basin_rule` structures as read-only primitive
      references.
- [x] Freeze I1 `support_scaffold` structures as read-only primitive
      references.
- [x] Freeze I1 `handoff_inputs` structures as read-only primitive references.
- [x] Freeze local definition of `source_current`.
- [x] Freeze run-artifact admissibility schema.
- [x] Freeze artifact path existence validation.
- [x] Freeze artifact digest algorithm declaration.
- [x] Freeze artifact digest match validation against file contents.
- [x] Freeze rule that `derived_report_only = true` blocks positive support.
- [x] Freeze rule that a missing required artifact blocks rung assignment.
- [x] Freeze Markdown roadmap/handoff sources as context-only, not evidence
      sources.
- [x] Freeze separation of `global_unsafe_claim_flags` from
      `row_specific_blocked_relabels`.
- [x] Freeze rule that inventory rows use `inventory_decision` for contract
      support and keep `row_decision = not_applicable`.
- [x] Freeze distinction between declared controls and executed controls.
- [x] Freeze threshold declaration policy.
- [x] Freeze withdrawal window schema.
- [x] Freeze withdrawal fields: mode, target, start, end, amount, recovery
      window, and floor-crossing policy.
- [x] Freeze restricted claim handling for `withdrawal_target =
      producer_surface`.
- [x] Freeze probe-present/probe-absent schema.
- [x] Freeze probe absence fields: runtime input absent, residue digest absent,
      support annotation not evidence, producer probe schedule disabled.
- [x] Freeze support/coherence/boundary/flux result schema.
- [x] Freeze replay result schema.
- [x] Freeze fail-closed control schema.
- [x] Freeze replay/control status enum: `passed`, `failed_closed`,
      `failed_open`, `not_run`, `not_applicable`.
- [x] Freeze active-null comparability rule.
- [x] Freeze withdrawal-resistance ladder `WR0...WR6`.
- [x] Freeze naturalization-depth ladder `ND0...ND6`.
- [x] Confirm `ND0...ND6` is a local artifact ladder, not the full cross-scale
      theoretical naturalization-depth ladder.
- [x] Freeze combined closeout ladder `N21-C0...N21-C6`.
- [x] Freeze rule that N20 contract completeness defines eligibility but cannot
      assign WR, ND, or N21-C rungs.
- [x] Freeze rule that ladder rungs may be assigned only from source-backed N21
      evidence rows.
- [x] Freeze demotion precedence: I4/I5 rungs are provisional until I6 replay
      and controls complete.
- [x] Freeze WR4 as requiring artifact replay AND snapshot/load replay AND
      duplicate replay.
- [x] Freeze ND3 as requiring declared multi-window replay without original
      probe/scaffold.
- [x] Freeze exact closeout status enums for WR and ND.
- [x] Freeze row-decision policy.
- [x] Confirm `supported` does not automatically permit unsafe claims.
- [x] Confirm `partial`, `blocked`, and `rejected` do not permit primitive
      support claims.
- [x] Confirm no positive primitive evidence is opened.

Expected artifacts:

```text
outputs/n21_withdrawal_schema_and_thresholds.json
reports/n21_withdrawal_schema_and_thresholds.md
scripts/build_n21_withdrawal_schema_and_thresholds.py
```

Implementation record:

```text
status = passed
acceptance_state = accepted_withdrawal_naturalization_schema_frozen_no_primitive_evidence
artifact = outputs/n21_withdrawal_schema_and_thresholds.json
report = reports/n21_withdrawal_schema_and_thresholds.md
script = scripts/build_n21_withdrawal_schema_and_thresholds.py
command = .venv/bin/python experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/scripts/build_n21_withdrawal_schema_and_thresholds.py
source_i1_output_digest = d7b7a37bc0781aedbe6f83c5b55ff8805bf559fe7d684c5e1d2a9be8a7cef3ee
output_digest = 49ec439aa4d3f2bb895dc11d8c7613a0f18f75d4f78fa38aead2282ebbf78bb7
artifact_sha256 = 3bfbfc843f5d627d1105b7b5e9c7b57fb7a17b566d785f4c9d13c61a807e8ff5
report_sha256 = e8c5befb1734e383f6a4e22eb39cf272b7fbb3e8b124f78570c67e97924b9d31
script_sha256 = dabefdc0e1bd6b5c1b422b531d24d3178b8b6e0a5609adfe0b6963fe61bd5a5d
failed_checks = []
check_count = 22
schema_freeze_only = true
primitive_evidence_opened = false
withdrawal_resistance_supported = false
naturalization_depth_supported = false
wr_ladder_rung_assigned = false
nd_ladder_rung_assigned = false
n21_closeout_ladder_rung_assigned = false
positive_run_artifacts_consumed = false
ready_for_iteration_3_active_nulls = true
```

Iteration 2 freezes the schema and no more. It locks source-current evidence,
candidate evidence row fields, run-artifact admissibility, threshold
declaration, withdrawal/probe absence, support/coherence/boundary/flux result
statuses, replay/control statuses, active-null comparability, WR/ND/N21-C
ladders, demotion precedence, row decisions, closeout enums, and claim
boundaries. It opens no positive primitive evidence and assigns no ladder
rungs.

Post-review tightening record:

```text
candidate_evidence_row_schema_complete = true
candidate_evidence_row_field_count = 33
same_basin_continuation_rule_schema_field_frozen = true
primitive_claim_allowed_schema_field_frozen = true
claim_ceiling_schema_field_frozen = true
i1_same_basin_rule_references_frozen_read_only = true
i1_support_scaffold_references_frozen_read_only = true
i1_handoff_inputs_references_frozen_read_only = true
i1_claim_ceiling_references_frozen = true
candidate_rows_missing_required_fields_blocked = true
```

## Iteration 3. Active Nulls And Failure Baselines

- [ ] Build active null rows.
- [ ] Confirm active nulls use the same source contract row as matching
      candidate rows.
- [ ] Confirm active nulls use the same source contract row digest.
- [ ] Confirm active nulls use the same basin signature fields.
- [ ] Confirm active nulls use the same seed or declared seed-pairing rule.
- [ ] Confirm active nulls use the same topology/config family.
- [ ] Confirm active nulls use the same runtime envelope digest.
- [ ] Confirm active nulls use the same budget/schedule family where
      applicable.
- [ ] Confirm active nulls use the same budget schedule digest where
      applicable.
- [ ] Show no-withdrawal/no-removal cannot pass as withdrawal resistance.
- [ ] Show label-only continuation cannot pass.
- [ ] Show proxy-only improvement cannot pass.
- [ ] Show hidden support cannot pass.
- [ ] Show post-hoc trace construction cannot pass.
- [ ] Show producer-mediated state cannot be relabeled as native support.
- [ ] Record fail-closed blockers distinctly.
- [ ] Confirm pre-positive active nulls fail closed before Iterations 4 and 5
      are admitted.

Expected artifacts:

```text
outputs/n21_withdrawal_active_nulls.json
reports/n21_withdrawal_active_nulls.md
scripts/build_n21_withdrawal_active_nulls.py
```

## Iteration 4. Withdrawal Resistance Probe

- [ ] Run bounded withdrawal-resistance candidate.
- [ ] Assign WR rung only from source-backed withdrawal evidence.
- [ ] Record run artifact ID and artifact digest.
- [ ] Record source commit or source digest.
- [ ] Record runtime config digest.
- [ ] Record source contract row digest.
- [ ] Record baseline artifact path.
- [ ] Record withdrawn artifact path.
- [ ] Record event log or trace path.
- [ ] Record snapshot or replay artifact path.
- [ ] Confirm `derived_report_only = false`.
- [ ] Record declared support weakening or removal.
- [ ] Record withdrawal mode, target, start, end, amount, recovery window, and
      floor-crossing policy.
- [ ] If `withdrawal_target = producer_surface`, restrict the positive claim to
      producer-dependence or residue analysis unless source-current basin
      continuation persists in declared fields.
- [ ] Record baseline-vs-withdrawn comparison.
- [ ] Confirm withdrawal evidence consumes source-current run artifacts.
- [ ] Record same-basin continuation result.
- [ ] Record support floor result.
- [ ] Record coherence floor result.
- [ ] Record boundary integrity result.
- [ ] Record flux/leakage result.
- [ ] Record withdrawal replay result.
- [ ] Record withdrawal replay status using the frozen replay/control status
      enum.
- [ ] Record hidden support control result.
- [ ] Record proxy-only success control result.
- [ ] Keep claim ceiling artifact-level and primitive-specific.

Expected artifacts:

```text
outputs/n21_withdrawal_resistance_probe.json
reports/n21_withdrawal_resistance_probe.md
scripts/build_n21_withdrawal_resistance_probe.py
```

## Iteration 5. Naturalization Depth Probe

- [ ] Run bounded naturalization-depth candidate.
- [ ] Assign ND rung only from source-backed post-probe evidence.
- [ ] Record run artifact ID and artifact digest.
- [ ] Record source commit or source digest.
- [ ] Record runtime config digest.
- [ ] Record source contract row digest.
- [ ] Record baseline artifact path.
- [ ] Record probe-absent artifact path.
- [ ] Record event log or trace path.
- [ ] Record snapshot or replay artifact path.
- [ ] Confirm `derived_report_only = false`.
- [ ] Record original probe/scaffold present in baseline.
- [ ] Record original probe/scaffold absent in evaluated run.
- [ ] Confirm `probe_absent_runtime_input = true`.
- [ ] Confirm `probe_residue_digest_absent = true`.
- [ ] Confirm `support_annotation_not_used_as_evidence = true`.
- [ ] Confirm `producer_probe_schedule_disabled = true`.
- [ ] Record probe-present-vs-probe-absent comparison.
- [ ] Confirm naturalization-depth evidence consumes source-current run
      artifacts.
- [ ] Record post-probe same-basin continuation result.
- [ ] Record post-probe support floor result.
- [ ] Record post-probe coherence floor result.
- [ ] Record post-probe boundary result.
- [ ] Record multi-window replay result.
- [ ] Record multi-window replay status using the frozen replay/control status
      enum.
- [ ] Record probe residue control result.
- [ ] Record support source annotation relabel control result.
- [ ] Report naturalization depth as candidate/rung-limited unless an explicit
      `ND0...ND6` rung ladder is defined and tested.
- [ ] Keep claim ceiling artifact-level and primitive-specific.

Expected artifacts:

```text
outputs/n21_naturalization_depth_probe.json
reports/n21_naturalization_depth_probe.md
scripts/build_n21_naturalization_depth_probe.py
```

## Iteration 6. Replay And Control Matrix

- [ ] Run artifact-only replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay.
- [ ] Run order-inversion control.
- [ ] Run label-only continuation control.
- [ ] Run proxy-only success control.
- [ ] Run hidden producer support control.
- [ ] Run post-hoc trace construction control.
- [ ] Run withdrawal schedule removed control.
- [ ] Run support floor crossing control.
- [ ] Run probe-present-only control.
- [ ] Run probe residue control.
- [ ] Run support source annotation relabel control.
- [ ] Run native support relabel control.
- [ ] Run semantic agency/sentience relabel control.
- [ ] Run Phase 8 relabel control.
- [ ] Record every required replay/control status as `passed`,
      `failed_closed`, `failed_open`, `not_run`, or `not_applicable`.
- [ ] Confirm negative controls fail closed as expected.
- [ ] Confirm controls consume or replay the same run artifacts and do not
      construct success post-hoc.
- [ ] Confirm controls can demote or block WR/ND ladder rungs when they fail.
- [ ] Confirm any required replay/control with status `not_run` blocks the rung
      that depends on it.
- [ ] Assign final WR/ND rungs only after I6 control results.

Expected artifacts:

```text
outputs/n21_replay_and_control_matrix.json
reports/n21_replay_and_control_matrix.md
scripts/build_n21_replay_and_control_matrix.py
```

## Iteration 7. Closeout And N22 Handoff

- [ ] Classify withdrawal-resistance result.
- [ ] Record final WR ladder rung.
- [ ] Classify naturalization-depth result.
- [ ] Record final ND ladder rung.
- [ ] Record final N21-C closeout ladder rung.
- [ ] Record exact WR status enum.
- [ ] Record exact ND status enum.
- [ ] Record remaining producer residue.
- [ ] Record remaining naturalization debt.
- [ ] Record final primitive claim ceiling.
- [ ] Record unsafe claim blockers.
- [ ] Confirm agency, native support, sentience, Phase 8, and ant-ecology
      implementation remain blocked.
- [ ] Confirm `src_diff_empty`.
- [ ] Record N22 handoff for susceptibility update / durable geometry
      modification.

Expected artifacts:

```text
outputs/n21_closeout_and_n22_handoff.json
reports/n21_closeout_and_n22_handoff.md
scripts/build_n21_closeout_and_n22_handoff.py
```

## Closeout Requirement

N21 closeout must answer:

```text
Did withdrawal resistance receive source-backed artifact-level primitive
candidate support?

Did naturalization depth receive source-backed artifact-level primitive
candidate or rung-limited support?

Which WR, ND, and N21-C rungs were source-backed, and which stronger rungs
remained blocked?

Which producer-mediated or naturalization-debt fields remain unresolved?

Did all unsafe relabels stay blocked?
```
