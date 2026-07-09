# N30 Minimal Shared-Medium Participation Implementation Checklist

## Current Status

```text
experiment = N30
status = iteration_4b_participant_boundary_support_sensitivity_passed
positive_evidence_opened = participant_admissibility_only
final_n30_closeout_rung = not_assigned
ready_for_iteration_5 = true
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

- [x] Declare participant carrier.
- [x] Declare bounded persistence window.
- [x] Record participant attribution trace.
- [x] Check N27-style recognizability / replay discipline.
- [x] Block selfhood, identity, agency, and semantic participant relabels.

Result:

```text
status = passed
acceptance_state = accepted_minimal_participant_admissibility_P2_candidate_no_medium_relation
output = outputs/n30_participant_admissibility_i4.json
report = reports/n30_participant_admissibility_i4.md
script = scripts/build_n30_participant_admissibility_i4.py
output_digest = 63f72c353b52f18eeeeece349fadde34d5f8a050d67c4f670d2397250b77774f
participant_ladder_rung = P2_candidate
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
positive_evidence_scope = participant_admissibility_only
participant_carrier_id = n30_i4_participant_carrier_basin_signature_A_mapped
recognizability_metric = signature_distance_under_declared_N27_mapping
recognizability_observed = 0.025
recognizability_threshold = 0.06
recognizability_margin = 0.035
replay_status = passed
label_drift_control_result = passed
artifact_count = 6
source_current_input_count = 12
failed_checks = []
medium_relation_ladder_rung_assigned = false
medium_surface_trace_evidence_opened = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
ready_for_iteration_5_medium_surface_trace_probe = true
```

Interpretation:

```text
I4 is the first positive N30 content row, but it supports participant
admissibility only. It consumes underlying N27 source-current traces and replay
records, not only N27 closeout summaries. The participant is treated as a
mapped basin-signature carrier: alpha-frame basin signature A maps into the
beta-frame basin signature while support, coherence, boundary mapping, and
bounded flux remain preserved. The carrier passes the declared recognizability
metric because mapped signature distance is 0.025 against a threshold of 0.06.
The threshold is inherited from N27's post-transfer basin-signature tolerance,
not independently tuned by N30, so the result remains a bounded participant
admissibility claim rather than a general stability or medium-relation claim.

This is enough for a bounded P2 participant-admissibility candidate and an
N30-C3 ceiling. It is not evidence for medium perturbation, trace-mediated
eligibility, minimal shared-medium participation, semantic identity, selfhood,
agency, shared-medium coordination, or native shared-medium organization.
```

## Iteration 4-A - P2 Participant Strengthening Variant

- [x] Consume I4 as the primary P2 participant-admissibility candidate.
- [x] Consume underlying N27 topology/fixture variant source-current artifacts.
- [x] Declare a second participant carrier without replacing I4.
- [x] Record topology/fixture difference from I4.
- [x] Record participant recognizability threshold and observed metric.
- [x] Record replay status and label-drift control.
- [x] Confirm medium-relation, later-eligibility, and shared-medium claims remain closed.

Result:

```text
status = passed
acceptance_state = accepted_topology_fixture_variant_P2_participant_strengthening_no_medium_relation
output = outputs/n30_participant_admissibility_i4a.json
report = reports/n30_participant_admissibility_i4a.md
script = scripts/build_n30_participant_admissibility_i4a.py
output_digest = 353b4417d6b278ee428de5e1adc88fdb7dd456f3aaa7e01c7d92a68d06296421
participant_ladder_rung = P2_candidate
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
positive_evidence_scope = participant_admissibility_strengthening_only
participant_carrier_id = n30_i4a_participant_carrier_branched_topology_signature
recognizability_metric = signature_distance_under_declared_N27_topology_fixture_mapping
recognizability_observed = 0.03
recognizability_threshold = 0.07
recognizability_margin = 0.04
replay_status = passed
label_drift_control_result = passed
artifact_count = 7
source_current_input_count = 14
failed_checks = []
i4_replaced = false
i4a_replaces_i4 = false
i4a_strengthens_i4 = true
medium_relation_ladder_rung_assigned = false
medium_surface_trace_evidence_opened = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
ready_for_iteration_4b_boundary_support_sensitive_participant_probe = true
ready_for_iteration_5_medium_surface_trace_probe = true
```

Interpretation:

```text
I4-A strengthens I4 by showing a second P2 participant-admissibility candidate
under a different N27 topology/fixture shape. It consumes the N27
topology-fixture variant's underlying pre/post basin-signature traces, mapping
trace, runtime trace, support/coherence/boundary/flux traces, hidden-support
ledger, and replay trace. It does not consume N27 closeout summaries as a
substitute for source-current evidence.

Geometrically, I4 used a three-node alpha/beta chain with one support lane.
I4-A uses a four-node gamma/delta branched/folded carrier with two support
lanes and four boundary edges. The support-branch count and boundary-edge
count remain preserved across the declared topology/fixture mapping, and the
mapped signature distance remains within threshold: 0.03 <= 0.07, margin 0.04.
The threshold is inherited from N27's topology-fixture transfer tolerance, not
independently tuned by N30. The topology-shape preservation check also now
requires `support_branch_count` and `boundary_edge_count` to exist on both
pre/post signature vectors before it can pass.

This improves repeatability of the P2 participant-admissibility result under
topology/fixture shape variation. It does not replace I4, does not widen N30
into medium evidence, and does not support medium perturbation,
trace-mediated eligibility, minimal shared-medium participation, semantic
identity, selfhood, agency, shared-medium coordination, or native
shared-medium organization.
```

## Iteration 4-B - Participant Boundary / Support-Sensitivity Probe

- [x] Consume I4 and I4-A participant candidates.
- [x] Consume N27 stress / mapping-variant matrix over both carriers.
- [x] Preserve the I4 boundary-limited result instead of upgrading it.
- [x] Test I4-A under boundary tightening, support drawdown, coherence drawdown, flux pressure, and combined stress.
- [x] Assign the strongest participant-side rung without opening a medium-relation rung.
- [x] Record source-current stress/control artifacts and claim boundary.
- [x] Confirm minimal shared-medium participation remains blocked.

Result:

```text
status = passed
acceptance_state = accepted_participant_boundary_support_sensitive_P4_candidate_no_medium_relation
output = outputs/n30_participant_boundary_support_i4b.json
report = reports/n30_participant_boundary_support_i4b.md
script = scripts/build_n30_participant_boundary_support_i4b.py
output_digest = b248e35e131071c606c2c5cc7c7ca1c2638f79ed2ea9fe2fda0959a88bd612d0
strongest_participant_ladder_rung = P4_candidate
strongest_participant_carrier_id = n30_i4a_participant_carrier_branched_topology_signature
i4_boundary_limited = true
i4a_boundary_support_sensitive_candidate_supported = true
i4_row_rung = P2_stress_limited
i4a_row_rung = P4_candidate
i4_failed_stress_ids = [boundary_tightening_0_05, combined_moderate_mapping_stress]
i4a_failed_stress_ids = []
i4a_minimum_residual_margin_across_stress = 0.007
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
artifact_count = 5
source_current_input_count = 7
failed_checks = []
check_count = 12
medium_relation_ladder_rung_assigned = false
medium_surface_trace_evidence_opened = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
ready_for_iteration_5_medium_surface_trace_probe = true
```

Interpretation:

```text
I4-B tests whether participant admissibility remains meaningful under declared
boundary/support stress. It consumes N27's stress/mapping-variant matrix rather
than creating a new synthetic stress label.

The I4 alpha/beta carrier remains a valid P2 participant-admissibility
candidate, but it is boundary-limited: its boundary margin is already at floor,
so boundary tightening and combined moderate stress fail closed. I4 is
therefore not upgraded.

The I4-A gamma/delta branched/folded carrier survives boundary tightening,
support drawdown, coherence drawdown, flux pressure, and combined bounded
stress with minimum residual margin 0.007. This supports a bounded P4
participant candidate: the participant is not only recognizable under replay,
but remains admissible under boundary/support-sensitive stress.

The I4-B rows now carry row-level `source_current_inputs`, `artifact_manifest`,
`derived_report_only = false`, and artifact SHA status, matching the row
metadata expected by downstream consumers. The top-level `source_guardrail_records`
also records that N27 stress artifacts were consumed and closeout summaries
were not used as a substitute. Empty stress-margin lists are treated as script
errors rather than silently passing.

This still does not open medium evidence. P4 is participant-side readiness
only. N30 still lacks a declared non-private medium surface, medium trace, and
later eligibility dependency, so N30-C4/C5/C6 remain blocked.
```

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
