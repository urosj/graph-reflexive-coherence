# N21 - LGRC Withdrawal Resistance And Naturalization Depth

N21 is the first becoming-primitive evidence experiment after the N20 contract.
It consumes the N20 Iteration 5 same-basin continuation contract and asks
whether a basin signature can persist when declared support is weakened,
removed, or no longer supplied by the original probe.

The core questions are:

```text
Can a basin signature persist when declared support is weakened or removed?

Can a basin persist without the original probe or scaffold?
```

N21 is not a general agency experiment. It tests two bounded LGRC becoming
primitives:

```text
withdrawal_resistance
naturalization_depth
```

## Evidence Standard

N21 must produce source-backed probe evidence, not another contract-only layer.
N20 already closed the contract. N21 must move from contract to run evidence.

Good N21 evidence requires:

```text
actual LGRC/source-current run artifacts
declared withdrawal or probe-absence condition before evaluation
baseline-vs-withdrawn comparison for withdrawal resistance
probe-present-vs-probe-absent comparison for naturalization depth
replayable same-basin trace
controls that fail closed
```

Insufficient N21 evidence:

```text
generated report rows only
scripted labels saying support was removed
proxy margin without replay
post-hoc basin signature construction
synthetic rows that do not consume run artifacts
```

Operational definition:

```text
source_current = emitted by the LGRC runtime or replay from declared run
artifacts, not invented by a report builder, label, post-hoc parser, or
producer-only policy.
```

Positive evidence rows must include a run-artifact admissibility surface:

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

## Source Boundary

N21 must consume the N20 I5 contract rows:

```text
withdrawal_resistance source row = n20_i5_row_01_withdrawal_resistance
naturalization_depth source row = n20_i5_row_02_naturalization_depth
```

Primary source artifacts:

```text
experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_same_basin_continuation_contract.json
experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/outputs/n20_closeout_and_n21_handoff.json
experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md
experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md
```

N21 may not redefine the N20 basin signature, continuation condition,
proxy-only success blocker, or producer-residue classification in order to pass.

## Fixed Readiness Gate

Every N21 row must preserve these gates:

```text
must_consume_i5_contract = true
may_redefine_n20_contract_to_pass = false
must_declare_row_specific_thresholds_before_use = true
must_produce_source_backed_pass_fail_evidence = true
must_fail_closed_on_hidden_support = true
must_fail_closed_on_proxy_only_success = true
must_keep_primitive_evidence_separate_from_contract = true
must_keep_agency_native_phase8_sentience_claims_blocked = true
```

## Primitive Readings

### Withdrawal Resistance

Withdrawal resistance means:

```text
the same declared basin signature remains source-visible through a bounded
support weakening or removal window while support, coherence, boundary
integrity, flux, and replay criteria remain inside the declared contract.
```

The withdrawal condition must be declared before outcome inspection:

```text
withdrawal_mode = weaken | remove | ramp_down | step_down
withdrawal_target = support | scaffold | producer_surface
withdrawal_start
withdrawal_end
withdrawal_amount
recovery_window
floor_crossing_policy
```

If `withdrawal_target = producer_surface`, the claim is restricted:

```text
producer-surface withdrawal can support producer-dependence or residue
analysis; it cannot by itself support source-current substrate-carried
withdrawal resistance unless basin continuation persists in declared
source-current fields.
```

It is not:

```text
willpower
resilience as identity
agency
native support
semantic goal preservation
```

N21 classifies withdrawal resistance with a primitive-evidence ladder:

```text
WR0 = no withdrawal evidence
WR1 = declared withdrawal attempted
WR2 = source-visible persistence signal
WR3 = same-basin withdrawal candidate
WR4 = replay-backed withdrawal candidate
WR5 = control-backed withdrawal candidate
WR6 = artifact-level withdrawal-resistance candidate
```

The strongest allowed WR claim is:

```text
artifact_level_withdrawal_resistance_candidate
```

### Naturalization Depth

Naturalization depth means:

```text
the same declared basin signature remains source-visible after the original
probe or scaffold is absent, across the declared post-probe replay window,
without hidden producer support or proxy-only success.
```

N21 should report this as:

```text
bounded naturalization-depth candidate evidence
```

N21 defines a local naturalization-depth primitive-evidence ladder:

```text
ND0 = probe-dependent only
ND1 = probe-absent trace
ND2 = post-probe same-basin candidate
ND3 = replay-backed post-probe candidate
ND4 = residue-controlled naturalization candidate
ND5 = producer-debt-bounded naturalization candidate
ND6 = artifact-level naturalization-depth candidate
```

A single probe-present/probe-absent result is not enough to establish general
naturalization depth. It can assign only the rung supported by source-backed
N21 evidence.

The N21 `ND0...ND6` ladder is a local artifact ladder, not the full cross-scale
naturalization-depth ladder from the theory.

Probe/scaffold absence must be runtime-visible:

```text
probe_absent_runtime_input = true
probe_residue_digest_absent = true
support_annotation_not_used_as_evidence = true
producer_probe_schedule_disabled = true
```

The strongest allowed ND claim is:

```text
bounded_N21_naturalization_depth_candidate
```

It is not:

```text
native absorption by label
identity acceptance
selfhood
sentience
Phase 8 implementation
```

## Required Distinctions

N21 must distinguish:

```text
same-basin continuation
support/coherence floor preservation
boundary integrity preservation
withdrawal schedule visibility
probe-present versus probe-absent state
hidden producer support
proxy-only success
label-only continuation
post-hoc trace construction
producer-mediated state relabeled as native support
semantic agency or sentience relabel
```

## Classification Ladders

N21 uses two primitive-evidence ladders plus one combined closeout ladder:

```text
withdrawal_resistance_ladder = WR0...WR6
naturalization_depth_ladder = ND0...ND6
n21_closeout_ladder = N21-C0...N21-C6
```

These ladders are not agency scores. They classify how much source-backed
evidence appears for the first two becoming diagnostics.

Assignment rule:

```text
A ladder rung may be assigned only from source-backed N21 evidence rows.
N20 contract completeness can define eligibility but cannot assign WR, ND, or
N21-C rungs.
```

Demotion rule:

```text
Probe rungs assigned in Iterations 4 and 5 are provisional.
Final WR and ND rungs are assigned only after the Iteration 6 replay/control
matrix.
Any fail-closed control demotes the rung to the highest level still supported.
```

Replay and control status values:

```text
passed
failed_closed
failed_open
not_run
not_applicable
```

Replay requirements:

```text
WR4 requires artifact replay AND snapshot/load replay AND duplicate replay.
If any required replay mode fails or is not_run, WR4 and stronger rungs are
blocked.

ND3 requires declared multi-window replay without the original probe/scaffold.
If declared multi-window replay fails or is not_run, ND3 and stronger rungs are
blocked.
```

Combined closeout rungs:

```text
N21-C0 = contract-only closeout
N21-C1 = baselines/control discipline established
N21-C2 = single primitive partial
N21-C3 = single primitive candidate
N21-C4 = dual primitive candidate
N21-C5 = dual replay/control-backed candidate
N21-C6 = N22-ready bounded primitive evidence
```

Maximum N21 closeout claim:

```text
bounded_artifact_level_withdrawal_and_naturalization_candidate
```

Exact primitive closeout status enums:

```text
withdrawal_resistance_supported_artifact_level_candidate
withdrawal_resistance_partial_or_blocked
withdrawal_resistance_rejected

naturalization_depth_supported_bounded_N21_candidate
naturalization_depth_rung_limited_candidate
naturalization_depth_partial_or_blocked
naturalization_depth_rejected
```

## Claim Boundary

N21 may support only bounded primitive evidence if source-backed probes and
controls pass. It must keep these claims blocked:

```text
agency
semantic action
semantic perception
semantic goal ownership
semantic intention
semantic choice
selfhood
identity acceptance
native support
Phase 8 implementation
fully native integration
organism/life behavior
sentience
consciousness
native ant agency
native colony agency
unrestricted autonomy
```

## Expected Output Shape

Initial planned artifacts:

```text
outputs/n21_source_contract_inventory.json
reports/n21_source_contract_inventory.md
scripts/build_n21_source_contract_inventory.py

outputs/n21_withdrawal_schema_and_thresholds.json
reports/n21_withdrawal_schema_and_thresholds.md
scripts/build_n21_withdrawal_schema_and_thresholds.py

outputs/n21_withdrawal_active_nulls.json
reports/n21_withdrawal_active_nulls.md
scripts/build_n21_withdrawal_active_nulls.py

outputs/n21_withdrawal_resistance_probe.json
reports/n21_withdrawal_resistance_probe.md
scripts/build_n21_withdrawal_resistance_probe.py

outputs/n21_naturalization_depth_probe.json
reports/n21_naturalization_depth_probe.md
scripts/build_n21_naturalization_depth_probe.py

outputs/n21_replay_and_control_matrix.json
reports/n21_replay_and_control_matrix.md
scripts/build_n21_replay_and_control_matrix.py

outputs/n21_closeout_and_n22_handoff.json
reports/n21_closeout_and_n22_handoff.md
scripts/build_n21_closeout_and_n22_handoff.py
```

These names are provisional until each iteration freezes its exact artifact
schema.
