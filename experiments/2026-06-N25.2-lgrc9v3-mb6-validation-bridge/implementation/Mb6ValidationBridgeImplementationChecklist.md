# N25.2 Implementation Checklist - LGRC9V3 MB6 Validation Bridge

## Ground Rules

- N25.2 validates, classifies, and hands off. It does not add new runtime code
  by default.
- Consume N25 as scoped BF5 / N25-C6 context, not as independent multi-basin
  evidence.
- Consume N25.1 as MB ladder and requirements context, not as runtime evidence.
- Consume Phase 8 multi-basin closeout as MB5 evidence, not automatic MB6.
- Run existing closed LGRC9V3 runtime implementation as primary N25.2 evidence.
- Do not modify `src`, `specs`, `tests`, examples, or implementation sources
  inside N25.2. Defects become blockers or repair targets.
- Treat examples and visual artifacts as corroboration only.
- Preserve producer/native mutation discipline.
- N26 unscoped multi-basin substrate consumption remains blocked unless MB6
  passes.
- Unsafe claim flags remain false in every artifact.
- No absolute paths in records.

## Iteration 1. Source Inventory And Admissibility Audit

Status: passed.

### Goal

Build the source inventory and admissibility map for N25.2.

### Checks

- [x] Read N25 closeout and N26 handoff.
- [x] Read N25.1 closeout and Phase 8 extension requirements.
- [x] Read Phase 8 multi-basin formation closeout.
- [x] Read Phase 8 multi-basin plan, checklist, and contract schema.
- [x] Read LGRC9V3 spec multi-basin section.
- [x] Read examples README and relevant example interpretations.
- [x] Classify every source by role.
- [x] Freeze `may_consume_as` and `must_not_consume_as`.
- [x] Confirm starting Phase 8 ceiling is MB5.
- [x] Confirm starting MB6 status is false/blocked.
- [x] Confirm N26 unscoped consumption remains false.
- [x] Confirm unsafe claims remain false.
- [x] Confirm no absolute paths in records.

Expected artifacts:

```text
outputs/n25_2_source_inventory_and_admissibility_audit.json
reports/n25_2_source_inventory_and_admissibility_audit.md
```

### Result

```text
status = passed
acceptance_state = accepted_source_inventory_admissibility_audit_ready_for_i2_no_mb6
source_row_count = 23
failed_checks = []
starting_phase8_mb_ceiling = MB5_control_backed_native_multi_basin_formation_candidate
starting_mb6_status = blocked
mb5_evidence_admissible_for_validation = true
mb6_supported = false
mb6_gate_applied = false
mb6_gate_schema_frozen = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = blocked_pending_mb6_gate
runtime_implementation_opened = false
existing_lgrc9v3_runtime_execution_allowed_in_later_iterations = true
src_diff_expected = false
ready_for_iteration_2_mb6_gate_schema = true
implementation_modification_allowed = false
implementation_defect_fix_allowed_in_n25_2 = false
implementation_defect_disposition = record_as_blocker_or_repair_target_only
n25_2_closeout_ceiling = N25.2-C1_source_inventory_and_admissibility_audit_passed
n25_2_closeout_ladder_rung_assigned = false
output_digest = 3134b384b529b8c04bb6d78aff18f287884ef1cba536ed39637727157f25dd26
artifact_sha256 = 585accaf91af0dc4d569912bb3e5b0d436fe9f54642578436e1e694b9b583d70
report_sha256 = 620f6ecd0fd5b2e369d40d7d155501a71cdc262b2486be756466e09ee6870ab8
```

### Interpretation

Iteration 1 validates the N25.2 source map only. It makes Phase 8 MB5 evidence
admissible for the next schema step, but it does not support MB6, does not open
N26 unscoped multi-basin substrate consumption, and does not modify runtime
implementation.

The source-role split is load-bearing:

```text
N25 = scoped BF5 / N25-C6 context, not independent multi-basin evidence
N25.1 = MB ladder and requirements context, not runtime evidence
Phase 8 closeout = MB5 implementation evidence, not automatic MB6
examples = telemetry/visual corroboration only, not proof by visualization
tests/code = admissibility and implementation-boundary evidence, not claim
             support without artifacts
```

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_source_inventory_and_admissibility_audit.py
passed
```

## Iteration 2. MB6 Gate Schema And Controls

Status: passed.

### Goal

Freeze the schema that decides whether MB6 can be supported.

### Checks

- [x] Freeze MB6 support gate fields.
- [x] Freeze N26 consumption effects.
- [x] Freeze source artifact admissibility rules.
- [x] Freeze replay/control requirements.
- [x] Freeze producer/native discipline.
- [x] Freeze visual-evidence limitations.
- [x] Freeze active blockers for label-only, old-basin thickening, transient
      flow sink, collapse/reabsorption relabel, graph-visual-only success,
      hidden producer insertion, producer success as native support, and
      MB5-as-MB6 relabel.
- [x] Freeze unsafe claim flags.
- [x] Confirm no MB6 claim is made in Iteration 2.

Expected artifacts:

```text
outputs/n25_2_mb6_gate_schema_and_controls.json
reports/n25_2_mb6_gate_schema_and_controls.md
```

### Result

```text
status = passed
acceptance_state = accepted_mb6_gate_schema_and_controls_frozen_no_mb6_evidence
i1_output_digest = 3134b384b529b8c04bb6d78aff18f287884ef1cba536ed39637727157f25dd26
failed_checks = []
mb6_gate_schema_frozen = true
mb6_gate_applied = false
mb6_gate_status = not_applied
mb6_supported = false
phase8_mb5_evidence_chain_audited = false
mb5_demoted = false
n26_unscoped_consumption_allowed = false
n26_consumption_effect = unscoped_consumption_blocked
n26_consumption_blocker = blocked_pending_mb6_gate
runtime_implementation_opened = false
existing_lgrc9v3_runtime_execution_allowed = true
runtime_execution_is_primary_positive_evidence = true
implementation_source_modification_allowed = false
defect_disposition = record_as_blocker_or_repair_target_only
src_diff_expected = false
n25_2_closeout_ceiling = N25.2-C3_MB6_gate_schema_and_active_blockers_frozen
n25_2_closeout_ladder_rung_assigned = false
ready_for_iteration_3_phase8_mb5_evidence_chain_audit = true
output_digest = fe84d14ccf3f71f96453cc67653d080e3b3d172776ccc7ffaa061a6c4716485f
artifact_sha256 = ad3a04cc84cd230f8cb30ed0828133e62c45577c41a4aaa20fbb1fb91d7fdaae
report_sha256 = e2c04a0036d4b522073548730454931b16188534caf12bd0429267bb25e17a07
```

### Interpretation

Iteration 2 freezes the MB6 gate and fail-closed control schema only. It does
not audit the Phase 8 MB5 evidence chain, does not apply the MB6 support
matrix, does not claim MB6, and does not open N26 unscoped multi-basin
substrate consumption.

The frozen evidence policy makes existing LGRC9V3 runtime execution the primary
positive-evidence source. Artifact reconstruction and replay validate
runtime-emitted records; they do not replace runtime execution.

I4+ runtime artifacts must record source-tree and implementation digests,
runtime artifact roles, child-basin state record fields, and no-modification
proof:

```text
implementation_source_modification_observed = false
src_diff_observed = false
spec_diff_observed = false
test_diff_observed = false
example_diff_observed = false
runtime_execution_from_closed_implementation = true
defect_fix_attempted = false
defect_disposition = record_as_blocker_or_repair_target_only
```

The frozen gate requires source-backed runtime surfaces, child-basin state
records, replay-backed child-basin persistence, artifact/snapshot/duplicate
replay, merge/leakage controls, clean producer/native mutation ownership,
front-capacity or boundary-birth provenance when used, hidden-producer and
label-only controls, visual-evidence limits, explicit N26 scope, and unsafe
claim flags false.

N26 remains blocked from unscoped multi-basin consumption. If MB6 is later
supported, the only allowed handoff effect is scoped MB6 substrate consumption,
not vague unscoped consumption. If MB5 is demoted, N26 substrate consumption is
blocked.

### Verification

```text
.venv/bin/python experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/build_n25_2_mb6_gate_schema_and_controls.py
passed
```

## Iteration 3. Phase 8 MB5 Evidence Chain Audit

Status: pending.

### Goal

Validate whether the closed Phase 8 MB5 evidence chain remains admissible
before new N25.2 runtime probes.

### Checks

- [ ] Validate runtime surfaces.
- [ ] Validate child-basin state records.
- [ ] Validate replay evidence.
- [ ] Validate merge/leakage control evidence.
- [ ] Validate producer compatibility audit.
- [ ] Validate telemetry/example interpretations.
- [ ] Classify MB5 chain status as one of:
      `mb5_chain_validated_for_runtime_probe`,
      `mb5_chain_validated_with_blockers`,
      `mb5_demoted_repair_required`, or
      `mb5_chain_unreadable_blocks_runtime_probe`.
- [ ] Confirm MB5 remains supported, remains usable only with blockers, or is
      demoted with repair target.
- [ ] Confirm I4 runtime probes cannot retroactively fix an I3 MB5-chain flaw.
- [ ] Confirm MB6 remains unassigned until the MB6 matrix.
- [ ] Confirm no implementation source is modified.

Expected artifacts:

```text
outputs/n25_2_phase8_mb5_evidence_chain_audit.json
reports/n25_2_phase8_mb5_evidence_chain_audit.md
```

## Iteration 4. Native LGRC9V3 Runtime Positive Probe

Status: pending.

### Goal

Run existing LGRC9V3 runtime with native multi-basin policy enabled and emit a
source-current positive runtime candidate.

### Checks

- [ ] Run existing runtime only; no implementation edits.
- [ ] Emit runtime execution trace.
- [ ] Emit flow-window records.
- [ ] Emit child-basin state records.
- [ ] Emit topology/refinement provenance.
- [ ] Emit producer/native mutation ownership ledger.
- [ ] Record implementation source digests and runtime config digest.
- [ ] Record child-basin fields: id, birth/detection step,
      parent/source basin, provenance, support/coherence core nodes, basin
      signature digest, topology before/after, flow-window id, merge/leakage
      status, persistence-window status, mutation owner, trace origin, and
      trace digest.
- [ ] Record no-modification proof for `src`, `specs`, `tests`, examples, and
      implementation sources.
- [ ] Record source-current inputs and artifact digests.
- [ ] Confirm replay, controls, stress, MB6, and N26 remain pending.
- [ ] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_native_runtime_positive_probe.json
reports/n25_2_native_runtime_positive_probe.md
```

## Iteration 4-A. Native Runtime Variant / Companion Probe

Status: pending.

### Goal

Run at least one alternative native runtime probe without changing the
implementation.

### Checks

- [ ] Run a source-backed variant or companion fixture.
- [ ] Prefer front-capacity boundary-birth companion and/or topology/seed
      variation already supported by the closed runtime.
- [ ] Confirm the variant is not a retuned copy of I4.
- [ ] Record declared variant axis and comparability digest.
- [ ] Confirm variant evidence cannot backfill unrelated MB5 rows.
- [ ] Emit comparable flow-window and child-basin records.
- [ ] Preserve producer/native mutation discipline.
- [ ] Confirm no implementation source is modified.
- [ ] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_native_runtime_variant_probe.json
reports/n25_2_native_runtime_variant_probe.md
```

## Iteration 5. Replay And Persistence Matrix

Status: pending.

### Goal

Replay I4/I4-A runtime-emitted artifacts and validate child-basin persistence.

### Checks

- [ ] Run artifact replay.
- [ ] Run snapshot/load replay.
- [ ] Run duplicate replay.
- [ ] Run multi-window child-basin persistence replay.
- [ ] Confirm reconstruction validates runtime-emitted records only.
- [ ] Confirm missing or failed replay blocks MB6.
- [ ] Confirm no implementation source is modified.
- [ ] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_replay_persistence_matrix.json
reports/n25_2_replay_persistence_matrix.md
```

## Iteration 6. Fail-Closed Control Matrix

Status: pending.

### Goal

Run fail-closed controls against runtime-emitted candidates.

### Checks

- [ ] Run label-only basin formation control.
- [ ] Run old-basin thickening relabel control.
- [ ] Run transient flow sink relabel control.
- [ ] Run collapse/reabsorption relabel control.
- [ ] Run graph-visual-only success control.
- [ ] Run hidden producer basin insertion control.
- [ ] Run producer success as native support control.
- [ ] Run front-capacity backfill control.
- [ ] Run MB5-as-MB6 relabel control.
- [ ] Run unsafe semantic / agency / native-support relabel controls.
- [ ] Confirm controls fail closed.
- [ ] Confirm failed-open controls block MB6.
- [ ] Confirm no implementation source is modified.
- [ ] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_fail_closed_control_matrix.json
reports/n25_2_fail_closed_control_matrix.md
```

## Iteration 7. Stress / Threshold / Variant Matrix

Status: pending.

### Goal

Stress the strongest replay/control-backed native multi-basin candidate without
modifying runtime implementation.

### Checks

- [ ] Stress flow-window thresholds.
- [ ] Stress merge/leakage pressure.
- [ ] Stress child-basin persistence window.
- [ ] Stress front-capacity / boundary-birth provenance where applicable.
- [ ] Stress seed or topology fixture variation where source-backed.
- [ ] Record whether evidence remains MB5, strengthens toward MB6, or exposes
      repair target.
- [ ] Confirm no implementation source is modified.
- [ ] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_stress_variant_matrix.json
reports/n25_2_stress_variant_matrix.md
```

## Iteration 8. MB6 Support / Blocker Matrix

Status: pending.

### Goal

Apply the MB6 gate and classify N26 consumption.

### Checks

- [ ] Apply all MB6 gates to I3-I7 evidence.
- [ ] Record support/blocker status per gate.
- [ ] Record whether MB6 is supported.
- [ ] Record exact blocker list if MB6 is blocked.
- [ ] Record N26 consumption effect.
- [ ] Confirm N25.2-C closeout rung remains separate from MB ladder support.
- [ ] Confirm no implementation source is modified.
- [ ] Confirm unsafe claims remain false.

Expected artifacts:

```text
outputs/n25_2_mb6_support_blocker_matrix.json
reports/n25_2_mb6_support_blocker_matrix.md
```

## Iteration 9. Closeout And N26 Handoff

Status: pending.

### Goal

Close N25.2 and hand off to N26 with explicit MB status.

### Checks

- [ ] Record final MB status.
- [ ] Record final N25.2-C rung.
- [ ] Record final N26 consumption permission.
- [ ] Record whether MB6 is supported or blocked.
- [ ] Record whether MB5 remains valid or was demoted.
- [ ] Record all remaining blockers.
- [ ] Confirm source artifacts are repo-relative.
- [ ] Confirm unsafe claims remain false.
- [ ] Confirm no implementation source was modified.
- [ ] Record any implementation defect as blocker or repair target only.

Expected artifacts:

```text
outputs/n25_2_closeout_and_n26_handoff.json
reports/n25_2_closeout_and_n26_handoff.md
```
