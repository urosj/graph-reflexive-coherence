# N21 Withdrawal Resistance And Naturalization Depth Implementation Plan

## Goal

N21 tests whether the N20 becoming-primitive contract can produce bounded,
source-backed primitive evidence for:

```text
withdrawal_resistance
naturalization_depth
```

N21 should answer:

```text
Can a basin signature persist when declared support is weakened or removed?

Can the same basin persist without the original probe or scaffold?
```

N21 does not test semantic agency, choice, learning, sentience, native support,
or Phase 8 implementation.

## Evidence Standard

N21 is the first becoming-primitive evidence experiment. It cannot close by
adding another contract or schema layer only.

Admissible positive evidence must include:

```text
actual LGRC/source-current run artifacts
declared withdrawal/probe-absence condition before outcome inspection
baseline-vs-withdrawn comparison for withdrawal resistance
probe-present-vs-probe-absent comparison for naturalization depth
replayable same-basin trace
fail-closed controls
```

Insufficient evidence:

```text
generated report rows only
scripted labels saying support was removed
proxy margin without replay
post-hoc basin signature construction
synthetic rows that do not consume source-current run artifacts
```

Operational definition:

```text
source_current = emitted by the LGRC runtime or replay from declared run
artifacts, not invented by a report builder, label, post-hoc parser, or
producer-only policy.
```

## Run-Artifact Admissibility

Iteration 2 must freeze the run-artifact admissibility schema before positive
evidence rows can be produced.

Required artifact fields:

```text
run_artifact_id
source_commit_or_source_digest
runtime_config_digest
source_contract_row_digest
baseline_artifact_path
withdrawn_or_probe_absent_artifact_path
event_log_or_trace_path
snapshot_or_replay_artifact_path
artifact_digest
derived_report_only = false
```

`derived_report_only = true` blocks positive primitive support. A report can
summarize evidence, but it cannot be the evidence source for WR or ND rung
assignment.

## Source Contract

Required N20 contract rows:

```text
withdrawal_resistance = n20_i5_row_01_withdrawal_resistance
naturalization_depth = n20_i5_row_02_naturalization_depth
```

N21 must consume these rows as fixed contracts. A row cannot pass by redefining:

```text
basin signature
support floor
coherence floor
boundary integrity floor
withdrawal condition
probe-present condition
probe-absent condition
proxy-only success blocker
hidden producer support blocker
blocked relabel fields
```

## Hypotheses

Hypothesis A:

```text
Source-backed withdrawal rows can preserve same-basin continuation under
declared support weakening or removal while hidden support, proxy-only success,
and label-only continuation fail closed.
```

Hypothesis B:

```text
Source-backed post-probe rows can preserve same-basin continuation after the
original probe or scaffold is absent, without relying on probe residue or
support annotation relabels.
```

Hypothesis C:

```text
N21 can keep primitive evidence, producer residue, naturalization debt, and
unsafe claim boundaries separated while testing withdrawal resistance and
naturalization depth.
```

## Non-Goals

N21 must not:

```text
modify src/*
change N20 contract definitions to pass
claim agency
claim semantic action or perception
claim semantic choice or intention
claim semantic goal ownership
claim selfhood
claim identity acceptance
claim native support
claim Phase 8 implementation
claim sentience or consciousness
claim organism/life behavior
claim native ant agency
claim native colony agency
claim unrestricted autonomy
write ant-ecology implementation specs before N29
```

## Method

N21 uses the Arc of Becoming as method:

```text
Classification:
  classify the two N20 primitives and their source contract rows without
  semantic promotion.

Interrogation:
  weaken or remove declared support/probe surfaces and run controls that expose
  hidden support, proxy-only success, and label-only continuation.

Naturalization:
  distinguish source-current basin continuation from producer-mediated
  residue and naturalization debt.

Cultivation:
  identify the minimal producer surface still required after successful or
  failed withdrawal/post-probe probes.
```

The method does not itself provide evidence. Evidence must come from generated
N21 artifacts and source-backed replay/control records.

## Row Decision Policy

Frozen row decisions:

```text
supported
partial
blocked
rejected
not_applicable
```

Decision relation:

```text
supported:
  row-specific primitive evidence may be counted only if all required gates,
  replay, controls, and claim-boundary checks pass.

partial:
  useful evidence exists, but at least one required gate, margin, replay, or
  scope limit prevents full support.

blocked:
  required source fields, controls, replay, or contract inputs are missing.

rejected:
  a fail-closed control or threshold crossing prevents the row from supporting
  the primitive.

not_applicable:
  the row is outside the declared primitive, support, or probe scope.
```

No row decision may open agency, native support, sentience, or Phase 8 claims.

## Replay And Control Status

Required replay and control records must use exactly one status:

```text
passed
failed_closed
failed_open
not_run
not_applicable
```

Status effects:

```text
passed:
  required positive replay/control condition passed.

failed_closed:
  blocker triggered and claim was rejected as expected.

failed_open:
  blocker triggered but claim was not rejected; row is invalid.

not_run:
  required replay/control was not run; any rung depending on it is blocked.

not_applicable:
  control is outside the declared row scope and must explain why.
```

## Withdrawal And Probe-Absence Schemas

Iteration 2 must freeze the withdrawal schema:

```text
withdrawal_mode = weaken | remove | ramp_down | step_down
withdrawal_target = support | scaffold | producer_surface
withdrawal_start
withdrawal_end
withdrawal_amount
recovery_window
floor_crossing_policy
```

The withdrawal schedule must be declared before outcome inspection. It cannot be
retuned after seeing whether the row passes.

If `withdrawal_target = producer_surface`, the positive claim is restricted:

```text
producer-surface withdrawal can support producer-dependence or residue
analysis; it cannot by itself support source-current substrate-carried
withdrawal resistance unless basin continuation persists in declared
source-current fields.
```

Iteration 2 must also freeze the probe/scaffold absence schema:

```text
probe_absent_runtime_input = true
probe_residue_digest_absent = true
support_annotation_not_used_as_evidence = true
producer_probe_schedule_disabled = true
```

Probe absence means absent from runtime/evaluation inputs, not merely absent
from a report label.

## Classification Ladders

Iteration 2 must freeze three primitive-evidence ladders before positive probes
run:

```text
withdrawal_resistance_ladder = WR0...WR6
naturalization_depth_ladder = ND0...ND6
n21_closeout_ladder = N21-C0...N21-C6
```

These ladders are not agency scores and must not be collapsed into a scalar
agency measure. They classify how much source-backed evidence appears for the
first two becoming diagnostics.

Global ladder assignment rule:

```text
A ladder rung may be assigned only from source-backed N21 evidence rows.
N20 contract completeness can define eligibility but cannot assign WR, ND, or
N21-C rungs.
```

Rung assignment and demotion precedence:

```text
Probe rungs assigned in Iterations 4 and 5 are provisional.
Final WR and ND rungs are assigned only after the Iteration 6 replay/control
matrix.
Any fail-closed control demotes the rung to the highest level still supported.
If replay fails, replay-backed and stronger rungs are blocked.
If a control fails closed, control-backed and stronger rungs are blocked.
If any required replay/control status is `not_run`, the rung depending on that
record is blocked.
If producer residue or naturalization debt is unrecorded, WR6, ND5, and ND6
are blocked.
```

### WR Ladder

```text
WR0 = no withdrawal evidence
  Contract consumed, but no valid withdrawal/probe run.

WR1 = declared withdrawal attempted
  Support weakening/removal is declared before use, but same-basin continuation
  is not yet shown.

WR2 = source-visible persistence signal
  Basin-like trace persists during withdrawal, but one or more required gates
  are missing: floor, boundary, flux, replay, or controls.

WR3 = same-basin withdrawal candidate
  Same-basin signature persists through bounded support weakening/removal,
  with support/coherence/boundary/flux gates recorded.

WR4 = replay-backed withdrawal candidate
  WR3 survives artifact replay AND snapshot/load replay AND duplicate replay.
  If any required replay mode fails or is not_run, WR4 and stronger rungs are
  blocked.

WR5 = control-backed withdrawal candidate
  WR4 survives fail-closed controls: hidden support, proxy-only success,
  label-only continuation, post-hoc trace construction, withdrawal schedule
  removed, and support floor crossing.

WR6 = artifact-level withdrawal-resistance candidate
  WR5 plus producer residue and naturalization debt are explicitly recorded,
  unsafe claims remain blocked, and no native-support, agency, Phase 8, or
  sentience claim opens.
```

Strongest allowed WR claim:

```text
artifact_level_withdrawal_resistance_candidate
```

### ND Ladder

N21 `ND0...ND6` is a local artifact ladder, not the full cross-scale
naturalization-depth ladder from the theory. It classifies only what N21 can
source-back through probe-present/probe-absent run artifacts, replay, and
controls.

```text
ND0 = probe-dependent only
  Basin/proxy appears only while the original probe/scaffold is present.

ND1 = probe-absent trace
  Some basin-like trace remains after probe/scaffold removal, but same-basin
  continuation is not established.

ND2 = post-probe same-basin candidate
  Same declared basin signature persists after original probe/scaffold is
  absent.

ND3 = replay-backed post-probe candidate
  ND2 survives declared multi-window replay without original probe/scaffold.
  If declared multi-window replay fails or is not_run, ND3 and stronger rungs
  are blocked.

ND4 = residue-controlled naturalization candidate
  ND3 survives probe residue, support annotation relabel, hidden support,
  label-only, proxy-only, and post-hoc construction controls.

ND5 = producer-debt-bounded naturalization candidate
  ND4 plus remaining producer-mediated and naturalization-debt fields are
  explicitly classified; no debt field is relabeled as native.

ND6 = artifact-level naturalization-depth candidate
  ND5 with source-backed pass/fail evidence, declared thresholds, preserved
  claim boundary, and N22 handoff.
```

Strongest allowed ND claim:

```text
bounded_N21_naturalization_depth_candidate
```

### N21 Closeout Ladder

```text
N21-C0 = contract-only closeout
  N20 contract consumed, but no primitive evidence opened.

N21-C1 = baselines/control discipline established
  Active nulls and failure baselines fail closed, but no positive primitive row.

N21-C2 = single primitive partial
  WR or ND has partial evidence, but required gates/replay/controls are
  missing.

N21-C3 = single primitive candidate
  WR or ND reaches artifact-level candidate support; the other remains partial,
  blocked, or rejected.

N21-C4 = dual primitive candidate
  Both WR and ND reach artifact-level candidate support under declared scope.

N21-C5 = dual replay/control-backed candidate
  Both WR and ND survive replay and fail-closed controls.

N21-C6 = N22-ready bounded primitive evidence
  C5 plus unresolved producer residue/naturalization debt are recorded, unsafe
  claims remain blocked, src diff is empty, and N22 handoff is valid.
```

Maximum N21 closeout:

```text
bounded_artifact_level_withdrawal_and_naturalization_candidate
```

## Required Evidence Fields

Every candidate evidence row must record:

```text
primitive_id
source_contract_row
contract_consumed_without_redefinition
row_specific_thresholds_declared_before_use
run_artifact_id
source_commit_or_source_digest
runtime_config_digest
source_contract_row_digest
baseline_artifact_path
withdrawn_or_probe_absent_artifact_path
event_log_or_trace_path
snapshot_or_replay_artifact_path
artifact_digest
derived_report_only
source_current_inputs
producer_mediated_fields
naturalization_debt_fields
blocked_relabel_fields
same_basin_continuation_rule
support_floor_result
coherence_floor_result
boundary_integrity_result
flux_or_leakage_result
replay_result
replay_result_status
control_results
control_result_statuses
wr_ladder_rung
nd_ladder_rung
row_decision
primitive_claim_allowed
unsafe_claim_flags
claim_ceiling
```

## Iteration Plan

### Iteration 1. Source Contract Inventory

Purpose:

```text
Read N20 closeout and I5 same-basin continuation contract rows.
Confirm N21 readiness gates.
Classify source rows, expected fields, controls, and non-claims.
```

Expected artifacts:

```text
outputs/n21_source_contract_inventory.json
reports/n21_source_contract_inventory.md
scripts/build_n21_source_contract_inventory.py
```

No primitive evidence is allowed in Iteration 1.

### Iteration 2. Withdrawal And Naturalization Schema Freeze

Purpose:

```text
Freeze N21 row schema, threshold policy, withdrawal window schema,
probe-present/probe-absent schema, run-artifact admissibility schema, active
null comparability rules, replay requirements, and fail-closed control policy
before any candidate probe runs. Freeze WR, ND, and N21-C ladder assignment and
demotion rules in the same artifact.
```

Expected artifacts:

```text
outputs/n21_withdrawal_schema_and_thresholds.json
reports/n21_withdrawal_schema_and_thresholds.md
scripts/build_n21_withdrawal_schema_and_thresholds.py
```

No positive primitive evidence is allowed in Iteration 2.

### Iteration 3. Active Nulls And Failure Baselines

Purpose:

```text
Show that label-only persistence, proxy-only improvement, hidden support,
post-hoc trace construction, and no-withdrawal/no-removal cases cannot pass as
withdrawal resistance or naturalization depth.
```

Active null rows must be comparable to candidate rows:

```text
same source contract row
same source contract row digest
same basin signature fields
same seed or declared seed-pairing rule
same topology/config family
same runtime envelope digest
same budget/schedule family where applicable
same budget schedule digest where applicable
no declared withdrawal or no probe absence
expected result = fail closed
```

Expected artifacts:

```text
outputs/n21_withdrawal_active_nulls.json
reports/n21_withdrawal_active_nulls.md
scripts/build_n21_withdrawal_active_nulls.py
```

Expected result:

```text
pre-positive active nulls fail closed before Iterations 4 and 5 are admitted.
post-positive replay/control matrix in Iteration 6 can demote or block
provisional WR/ND rungs.
```

### Iteration 4. Withdrawal Resistance Probe

Purpose:

```text
Run the first source-backed withdrawal-resistance candidate under declared
support weakening or removal, using actual source-current run artifacts rather
than report-only synthesis.
```

Required distinction:

```text
admissible run artifacts present
baseline with declared support present
withdrawn run with declared support weakened or removed
support weakened or removed
same basin persists
support/coherence floors preserved
boundary integrity preserved
hidden support absent
proxy-only success rejected
```

Expected artifacts:

```text
outputs/n21_withdrawal_resistance_probe.json
reports/n21_withdrawal_resistance_probe.md
scripts/build_n21_withdrawal_resistance_probe.py
```

### Iteration 5. Naturalization Depth Probe

Purpose:

```text
Run the first source-backed naturalization-depth candidate after original
probe/scaffold removal, using actual source-current run artifacts rather than
report-only synthesis.
```

Required distinction:

```text
admissible run artifacts present
probe present in baseline
probe absent in evaluated run
same basin persists over post-probe replay
probe residue rejected
support annotation relabel rejected
hidden support rejected
claim remains bounded candidate or rung-limited unless the explicit ND0...ND6
naturalization-depth ladder is defined and tested
```

Expected artifacts:

```text
outputs/n21_naturalization_depth_probe.json
reports/n21_naturalization_depth_probe.md
scripts/build_n21_naturalization_depth_probe.py
```

### Iteration 6. Replay And Control Matrix

Purpose:

```text
Try to break the positive candidate rows, if any, through replay and controls
that consume the same run artifacts rather than reconstructing success
post-hoc.
```

Required controls:

```text
artifact-only replay
snapshot/load replay
duplicate replay
order inversion
label-only continuation
proxy-only success
hidden producer support
post-hoc trace construction
withdrawal schedule removed
support floor crossing
probe-present only
probe residue
support source annotation relabel
native support relabel
semantic agency/sentience relabel
phase8 relabel
```

Expected artifacts:

```text
outputs/n21_replay_and_control_matrix.json
reports/n21_replay_and_control_matrix.md
scripts/build_n21_replay_and_control_matrix.py
```

### Iteration 7. Closeout And N22 Handoff

Purpose:

```text
Classify N21 results, record claim ceiling, carry unresolved naturalization
debt, and hand off to N22 susceptibility update / durable geometry
modification.
```

Expected artifacts:

```text
outputs/n21_closeout_and_n22_handoff.json
reports/n21_closeout_and_n22_handoff.md
scripts/build_n21_closeout_and_n22_handoff.py
```

Closeout must explicitly record:

```text
withdrawal_resistance status
withdrawal_resistance_ladder_rung
naturalization_depth status
naturalization_depth_ladder_rung
n21_closeout_ladder_rung
producer residue remaining
naturalization debt remaining
primitive claim ceiling
unsafe claim blockers
src_diff_empty
ready_for_n22
```

## Acceptance Boundary

N21 can close only if the final artifact records one of:

```text
withdrawal_resistance_supported_artifact_level_candidate
withdrawal_resistance_partial_or_blocked
withdrawal_resistance_rejected
naturalization_depth_supported_bounded_N21_candidate
naturalization_depth_rung_limited_candidate
naturalization_depth_partial_or_blocked
naturalization_depth_rejected
partial_or_blocked_due_to_source_backing_or_controls
rejected_due_to_fail_closed_controls
```

N21 cannot close as:

```text
agency supported
native support supported
sentience supported
Phase 8 opened
ant ecology specified
```
