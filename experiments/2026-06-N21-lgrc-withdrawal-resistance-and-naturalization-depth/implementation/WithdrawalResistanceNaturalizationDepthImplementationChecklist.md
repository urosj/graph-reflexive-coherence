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

- [ ] Use source IDs, titles, and relative paths only.
- [ ] Confirm generated records contain no local absolute paths.
- [ ] Consume N20 I5 withdrawal-resistance row without redefinition.
- [ ] Consume N20 I5 naturalization-depth row without redefinition.
- [ ] Declare row-specific thresholds before use.
- [ ] Require actual LGRC/source-current run artifacts for positive primitive
      evidence.
- [ ] Reject report-only or synthetic-row success as insufficient evidence.
- [ ] Separate N20 contract evidence from N21 primitive evidence.
- [ ] Treat producer-mediated fields as producer residue unless source-backed
      naturalization evidence is produced.
- [ ] Treat naturalization-debt fields as debt unless source-backed
      naturalization evidence is produced.
- [ ] Reject blocked relabel fields when used as evidence.
- [ ] Fail closed on hidden producer support.
- [ ] Fail closed on proxy-only success.
- [ ] Fail closed on label-only continuation.
- [ ] Fail closed on post-hoc trace construction.
- [ ] Force unsafe claim flags false in every row.
- [ ] Do not modify `src/*`.
- [ ] Do not write ant-ecology implementation specs in N21.
- [ ] Keep agency, native support, sentience, and Phase 8 claims blocked.

## Iteration 1. Source Contract Inventory

- [ ] Build N21 source contract inventory.
- [ ] Read N20 closeout and N21 handoff.
- [ ] Read N20 I5 same-basin continuation contract.
- [ ] Record withdrawal-resistance source row.
- [ ] Record naturalization-depth source row.
- [ ] Record N21 readiness gates.
- [ ] Record source-current fields, producer-mediated fields, naturalization
      debt fields, and blocked relabel fields.
- [ ] Record required controls for each primitive.
- [ ] Confirm no primitive evidence is opened.
- [ ] Confirm no agency, native support, sentience, Phase 8, or ant-ecology
      implementation claim is opened.

Expected artifacts:

```text
outputs/n21_source_contract_inventory.json
reports/n21_source_contract_inventory.md
scripts/build_n21_source_contract_inventory.py
```

## Iteration 2. Withdrawal And Naturalization Schema Freeze

- [ ] Freeze N21 row schema.
- [ ] Freeze local definition of `source_current`.
- [ ] Freeze run-artifact admissibility schema.
- [ ] Freeze threshold declaration policy.
- [ ] Freeze withdrawal window schema.
- [ ] Freeze withdrawal fields: mode, target, start, end, amount, recovery
      window, and floor-crossing policy.
- [ ] Freeze restricted claim handling for `withdrawal_target =
      producer_surface`.
- [ ] Freeze probe-present/probe-absent schema.
- [ ] Freeze probe absence fields: runtime input absent, residue digest absent,
      support annotation not evidence, producer probe schedule disabled.
- [ ] Freeze support/coherence/boundary/flux result schema.
- [ ] Freeze replay result schema.
- [ ] Freeze fail-closed control schema.
- [ ] Freeze replay/control status enum: `passed`, `failed_closed`,
      `failed_open`, `not_run`, `not_applicable`.
- [ ] Freeze active-null comparability rule.
- [ ] Freeze withdrawal-resistance ladder `WR0...WR6`.
- [ ] Freeze naturalization-depth ladder `ND0...ND6`.
- [ ] Confirm `ND0...ND6` is a local artifact ladder, not the full cross-scale
      theoretical naturalization-depth ladder.
- [ ] Freeze combined closeout ladder `N21-C0...N21-C6`.
- [ ] Freeze rule that N20 contract completeness defines eligibility but cannot
      assign WR, ND, or N21-C rungs.
- [ ] Freeze rule that ladder rungs may be assigned only from source-backed N21
      evidence rows.
- [ ] Freeze demotion precedence: I4/I5 rungs are provisional until I6 replay
      and controls complete.
- [ ] Freeze WR4 as requiring artifact replay AND snapshot/load replay AND
      duplicate replay.
- [ ] Freeze ND3 as requiring declared multi-window replay without original
      probe/scaffold.
- [ ] Freeze exact closeout status enums for WR and ND.
- [ ] Freeze row-decision policy.
- [ ] Confirm `supported` does not automatically permit unsafe claims.
- [ ] Confirm `partial`, `blocked`, and `rejected` do not permit primitive
      support claims.
- [ ] Confirm no positive primitive evidence is opened.

Expected artifacts:

```text
outputs/n21_withdrawal_schema_and_thresholds.json
reports/n21_withdrawal_schema_and_thresholds.md
scripts/build_n21_withdrawal_schema_and_thresholds.py
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
