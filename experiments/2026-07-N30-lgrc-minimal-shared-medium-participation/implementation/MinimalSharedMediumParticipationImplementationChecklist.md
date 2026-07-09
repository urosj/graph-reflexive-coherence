# N30 Minimal Shared-Medium Participation Implementation Checklist

## Current Status

```text
experiment = N30
status = iteration_3_active_nulls_passed
positive_evidence_opened = false
final_n30_closeout_rung = not_assigned
ready_for_iteration_4 = true
```

## Setup

- [x] Create N30 experiment directory.
- [x] Add README with core question, source basis, claim ceiling, and blocked claims.
- [x] Add hypotheses A-E.
- [x] Add implementation plan.
- [x] Add implementation checklist.
- [x] Add configs / outputs / reports / scripts README placeholders.

## Iteration 1 - Source Inventory And Method Admission

- [x] Consume N30+ roadmap package.
- [x] Consume shared-medium essay as conceptual transition source.
- [x] Consume shared-medium engineering spec as method/control/debt source.
- [x] Consume N27 closeout/source artifacts as participant-continuity guardrail.
- [x] Consume N28 closeout/source artifacts as environment-effect guardrail.
- [x] Consume N29 closeout / ecology handoff as bridge context.
- [x] Consume Claim Boundary Index.
- [x] Record source roles and must-not-consume-as rules.
- [x] Record `source_id`, `source_path_or_url`, `source_role`, `allowed_use`, `blocked_use`, `commit_or_digest`, `consumed_sections`, `claim_boundary_imported`, and `runtime_evidence_allowed`.
- [x] Pin external shared-medium sources by content digest or commit identifier.
- [x] Confirm no positive N30 evidence opened.

Result:

```text
status = passed
acceptance_state = accepted_source_inventory_method_admission_no_positive_evidence
output = outputs/n30_source_inventory_i1.json
report = reports/n30_source_inventory_i1.md
script = scripts/build_n30_source_inventory_i1.py
output_digest = 2a7bc77d5c7034e0b329dd80a85de44e8bafa56ac966ca61ac501b89ae2f61a4
source_record_count = 10
failed_checks = []
positive_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
```

Interpretation:

```text
I1 admits source and method basis only. The shared-medium essay and engineering
spec are pinned and consumed as vocabulary, method, control, and debt sources;
they do not supply LGRC runtime evidence. N27, N28, and N29 are consumed as
continuity, environment-effect, and ecology-bridge guardrails, not as N30
positive evidence.

Digest convention:
output_digest = canonical payload digest
file_sha256 = exact artifact file-content digest

If N27/N28 closeout summaries do not expose the participant-recognizability or
environment-effect fields required by a later positive N30 row, that row must
consume the underlying N27/N28 result artifacts rather than relying on closeout
summary text.
```

## Iteration 2 - Participant / Medium Schema Freeze

- [x] Freeze participant ladder P0-P7.
- [x] Freeze shared-medium relation ladder M0-M6.
- [x] Freeze N30 closeout ladder N30-C0-N30-C6.
- [x] Freeze candidate evidence fields.
- [x] Freeze coupled relation-chain fields.
- [x] Freeze sharedness gate and `medium_surface_scope` enum.
- [x] Freeze participant / medium separation audit.
- [x] Freeze predeclared later-response metric fields.
- [x] Freeze medium debt and producer residue status enums.
- [x] Freeze direct-message and hidden-producer control policy.
- [x] Freeze replay requirements.
- [x] Freeze claim ceiling and blocked relabels.

Result:

```text
status = passed
acceptance_state = accepted_participant_medium_schema_controls_frozen_no_positive_evidence
output = outputs/n30_schema_control_freeze_i2.json
report = reports/n30_schema_control_freeze_i2.md
script = scripts/build_n30_schema_control_freeze_i2.py
output_digest = 1286b3242c3a466c34289be0d4d1589be428c10782ac64eadff7611483b1462c
candidate_required_field_count = 46
required_control_count = 20
hypothesis_manifest = Hypothesis A-E
failed_checks = []
positive_evidence_opened = false
final_n30_closeout_rung = not_assigned
n30_closeout_ceiling = N30-C2_schema_and_active_null_controls_frozen
ready_for_iteration_3_active_nulls = true
```

Interpretation:

```text
I2 freezes the contract. Later rows may not pass as minimal shared-medium
participation by showing participant continuity, medium perturbation, trace
change, or later response separately. N30-C5/C6 require one ordered causal
lineage: participant continuity -> medium surface perturbation -> trace/surface
change -> later eligibility or susceptibility change, with direct-message,
hidden-producer, label-only, post-hoc, wrong-surface, time-reversal, and
semantic relabel paths failing closed.

C5/C6 minimum policy:
N30-C3 may close with P1.
N30-C4 may close with P1 + M1.
N30-C5 and N30-C6 require P2 + M2.

Same-identifier policy:
same participant_carrier_id == medium_surface_id blocks N30-C5/C6. Such rows
may be recorded as internal aftereffect, medium-mediated self-aftereffect, or
partial rows, but not as minimal shared-medium participation.

Telemetry-only policy:
report/log-only surfaces cannot count as medium surfaces. A packet/event
history surface must condition runtime later response; otherwise it is
classified as post-hoc trace construction or label-only surface.

I3 null-row mapping:
active null rows must record blocked_gate, blocked_rung, dependent_hypothesis,
and control_equivalent_id in addition to the base null-row fields.

Traceability note:
The I2 digest supersedes the earlier intermediate digest
`afba7d70973c5dae28b57e9e38e5de5479276b1113b74b4f002132063f38967d` after
the claim-boundary naming was aligned with I1, machine-readable field/control
counts were added, and the hypothesis manifest was surfaced for I3 linkage.
```

## Iteration 3 - Active Nulls And Failure Baselines

- [x] Run or synthesize active null rows for direct-message-only relabel.
- [x] Run medium-surface label-only null.
- [x] Run hidden global-controller null.
- [x] Run hidden producer-routing null.
- [x] Run post-hoc trace-construction null.
- [x] Run participant label-drift null.
- [x] Run generic redistribution relabel null.
- [x] Run no-perturbation null.
- [x] Run trace-ablation null.
- [x] Run wrong-surface null.
- [x] Run time-reversed-trace null.
- [x] Run semantic communication / coordination / cooperation / agency relabel nulls.
- [x] Record `null_row_id`, `null_type`, `expected_fail_reason`, `observed_fail_reason`, and `fail_closed` for every null row.
- [x] Confirm all nulls fail closed.
- [x] Confirm no positive evidence opened.

Result:

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_evidence
output = outputs/n30_active_nulls_i3.json
report = reports/n30_active_nulls_i3.md
script = scripts/build_n30_active_nulls_i3.py
output_digest = 20de953306725e68bb866f5a71c65b1239cec4ecfc36abb3710d95ae9e4a5c49
active_null_count = 20
failed_closed_count = 20
failed_open_rows = []
null_fixture_config_digest = aaf2736324b8284f7d7da6137309276e1f7ac706cd9579c3ed5a742b2e321beb
null_generation_policy_digest = df29a80fa0120267362c2680387f77c12fd6e58577a822c33b94282505d2aeb1
blocked_rungs = [N30-C3, N30-C4, N30-C5, N30-C6]
dependent_hypotheses = [Hypothesis B, Hypothesis C, Hypothesis D, Hypothesis E]
positive_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
ready_for_iteration_4_participant_admissibility_probe = true
```

Interpretation:

```text
I3 establishes the pre-positive false-positive boundary. It can block unsafe
paths, but it cannot support participant admissibility, medium trace evidence,
later eligibility dependency, or N30-C5/C6. Direct messages, label-only
surfaces, hidden producers, global controllers, post-hoc traces, no
perturbation, trace ablation, wrong surfaces, time reversal, trace shuffling,
false trace injection, decay manipulation, susceptibility inversion,
participant label drift, generic redistribution, semantic communication,
semantic coordination, cooperation/agency relabels, and native shared-medium
organization relabels all fail closed.

I3-to-I7 rule:
I3 nulls are pre-positive false-positive blockers. They do not substitute for
I7 runtime controls. I7 must rerun or reinstantiate equivalent controls against
the actual I4-I6 positive candidate fixture.

Observation-source note:
The `observed_fail_reason` field is preserved because I2 requires it, but in
I3 its observation source is `pre_positive_synthetic_active_null_fixture`.
These values are declared fail-closed fixture conditions, not runtime
measurements.

I4 ceiling guard:
I4 may test only participant admissibility. It cannot assign a medium-relation
rung, medium perturbation claim, trace-mediated eligibility claim, or minimal
shared-medium participation claim. Same label is not same carrier; I4 must
record carrier digest or trace continuity, recognizability metric, threshold,
replay status, and label-drift control result.
```

## Iteration 4 - Minimal Participant Admissibility Probe

- [ ] Declare participant carrier.
- [ ] Declare bounded persistence window.
- [ ] Record participant attribution trace.
- [ ] Check N27-style recognizability / replay discipline.
- [ ] Block selfhood, identity, agency, and semantic participant relabels.

## Iteration 5 - Medium Surface Perturbation / Trace Probe

- [ ] Declare medium surface.
- [ ] Declare `medium_surface_scope`.
- [ ] Confirm medium surface is non-private or classify as self-aftereffect / partial.
- [ ] Record participant / medium distinctness.
- [ ] Record perturbation source and timing.
- [ ] Record trace or surface-state change.
- [ ] Record persistence/decay behavior.
- [ ] Block label-only medium and hidden producer routes.

## Iteration 6 - Later Eligibility / Susceptibility Probe

- [ ] Record later eligibility, cost, support, routing, susceptibility, or capacity change.
- [ ] Predeclare `later_response_metric`, `expected_direction`, `response_window`, `baseline_window`, `acceptance_threshold`, and `normalization_denominator`.
- [ ] Record effect size and counterfactual row.
- [ ] Show later change depends on the changed medium surface.
- [ ] Link participant event, perturbation event, trace/surface change, and later response in one `relation_chain_id`.
- [ ] Preserve N28-style environment-effect distinction where relevant.
- [ ] Block generic redistribution and semantic relation relabels.

## Iteration 7 - Replay, Controls, And Medium Debt Matrix

- [ ] Run artifact-only replay.
- [ ] Run duplicate replay.
- [ ] Run snapshot/load replay.
- [ ] Run direct-message removal control.
- [ ] Run no-perturbation control.
- [ ] Run trace-ablation control.
- [ ] Run wrong-surface control.
- [ ] Run time-reversed trace control.
- [ ] Run medium-freeze control.
- [ ] Run trace-shuffle control.
- [ ] Run false-trace injection control.
- [ ] Run decay manipulation control.
- [ ] Run susceptibility inversion control.
- [ ] Run hidden producer / global controller controls.
- [ ] Record medium debt and producer residue per row.

## Iteration 8 - Classification And N31 Handoff

- [ ] Classify strongest participant ladder rung.
- [ ] Classify strongest shared-medium relation rung.
- [ ] Classify coupled relation-chain support.
- [ ] Confirm N30-C5/C6 are blocked unless participant + non-private medium surface + trace/surface change + later eligibility dependency pass replay/control.
- [ ] Assign N30 closeout rung if warranted.
- [ ] Record final claim ceiling.
- [ ] Record blocked claims.
- [ ] Record N31 handoff target if supported.
- [ ] Confirm shared-medium coordination, parent-basin modulation, resonance, native shared-medium organization, agency, ecology regime, sentience, organism/life, and unrestricted autonomy remain blocked.
