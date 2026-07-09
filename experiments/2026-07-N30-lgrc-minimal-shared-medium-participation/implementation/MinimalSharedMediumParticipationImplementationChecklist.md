# N30 Minimal Shared-Medium Participation Implementation Checklist

## Current Status

```text
experiment = N30
status = iteration_8_closed
positive_evidence_opened = bounded_minimal_shared_medium_participation_candidate
n30_c5_candidate_supported = true
n30_c6_spiral_ready_closeout_supported = true
final_n30_closeout_rung = N30-C6_post_N30_spiral_ready_minimal_shared_medium_participation_closeout
post_n30_handoff_mode = cross_project_spiral
agentic_ecology_demand_pass_recommended = true
candidate_n31_selected = false
next_lgrc_experiment_fixed = false
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

- [x] Declare medium surface.
- [x] Declare `medium_surface_scope`.
- [x] Confirm medium surface is non-private or classify as self-aftereffect / partial.
- [x] Record participant / medium distinctness.
- [x] Record perturbation source and timing.
- [x] Record trace or surface-state change.
- [x] Record persistence/decay behavior.
- [x] Block label-only medium and hidden producer routes.

Result:

```text
status = passed
acceptance_state = accepted_medium_surface_perturbation_trace_M1_candidate_no_later_eligibility
output = outputs/n30_medium_surface_trace_i5.json
report = reports/n30_medium_surface_trace_i5.md
script = scripts/build_n30_medium_surface_trace_i5.py
output_digest = f84cfb6ca3ce06f699a8be2a680cdb75707a637b4b6abb167dbc66b681ccc971
participant_ladder_rung = P2_candidate_with_I4B_P4_guardrail
strongest_N30_I5_row_participant_rung = P2_candidate
source_i4b_strongest_participant_guardrail = P4_candidate
medium_relation_ladder_rung = M1_candidate
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
runtime_origin = inherited_N28_source_current_artifact
n30_fresh_runtime = false
i5_claim_type = inherited_medium_surface_trace_admission
participant_carrier_id = n28_i4a_focal_basin_beta
medium_surface_id = n28_i4a_neighbor_capacity_shell_beta
medium_surface_scope = shared_local
medium_surface_scope_status = shared_local_candidate_pending_later_encounter
participant_medium_distinct = true
neighbor_distinguishability_delta = 0.154
neighbor_support_delta = 0.087
neighbor_boundary_delta = 0.145
environment_capacity_delta = 0.134
trace_persistence_status = replay_persistent_no_decay_curve
source_guardrail_controls = N28_controls_only
n30_relation_controls = pending_iteration_7
trace_dependency_control_ids = pending_iteration_7
artifact_count = 8
source_current_input_count = 12
failed_checks = []
medium_surface_trace_evidence_opened = true
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
ready_for_iteration_6_later_eligibility_probe = true
```

Interpretation:

```text
I5 opens the medium-surface side of N30 by consuming the N28 I4-A source-current
generative strengthening row and its N28 replay trace. The declared medium
surface is the N28 neighbor capacity shell, not the focal basin itself. It is
classified as `shared_local` because the shell is distinct from the focal basin
and exposes support, boundary, distinguishability, and environment-capacity
fields rather than private participant state.

I5 is inherited/source-current medium-surface admission, not fresh N30 runtime
evidence. N28 artifacts may support C4/M1 surface-trace admission. They may not
support C5/M2 later eligibility dependency unless I6/I7 add a new N30
relation-chain dependency test.

Geometrically, the N28 focal basin remains viable while the adjacent capacity
surface becomes more distinguishable, better supported, better bounded, and
more basin-forming. This supports an M1 medium perturbation / trace candidate.
Replay shows the surface-change record is persistent enough for I5, but no
decay curve is measured.

I4-B is consumed as participant-side discipline: N30 already has a bounded P4
participant guardrail. That P4 value is a source guardrail, not the I5 row's
own participant rung. The I5 row remains `P2_candidate_with_I4B_P4_guardrail`.
I5 does not claim that the N27 I4-A carrier itself perturbed the N28 surface.
The load-bearing medium trace is the N28 source-current focal/neighbor
relation.

The N28 controls consumed by I5 are source guardrail controls, not N30 relation
controls. I7 must still run or instantiate direct-message removal,
trace-ablation, wrong-surface, time-reversal, medium-freeze, trace-shuffle,
false-trace, decay, susceptibility-inversion, and hidden-producer controls
against the actual I5/I6 relation chain.

I5 still does not support trace-mediated eligibility, later susceptibility,
minimal shared-medium participation, shared-medium coordination, native
shared-medium organization, semantic communication, cooperation, agency,
selfhood, or ecology-regime claims. N30-C5/C6 remain blocked until I6/I7 show
that a later response depends on the changed medium surface and controls pass.

C4 and C5 remain separate: C4 means a changed medium surface exists; C5 means
a later response depends on that changed surface. I5 supports C4 only.
```

## Iteration 5-A - Mechanism-Diverse Medium Surface Trace Strengthening

- [x] Consume I5 as the primary minimal M1 medium-surface trace row.
- [x] Consume the N28 I4-A2 mechanism-diversity source-current artifacts.
- [x] Consume the N28 I4-A2 replay trace.
- [x] Declare a second medium surface without replacing I5.
- [x] Record participant / medium distinctness for the I4-A2 focal/split-shell pair.
- [x] Record medium-surface deltas and replay persistence.
- [x] Compare I5 and I5-A as mechanism-diverse evidence rather than margin upgrade.
- [x] Confirm later eligibility, M2, C5, coordination, and native shared-medium claims remain closed.

Result:

```text
status = passed
acceptance_state = accepted_mechanism_diverse_medium_surface_trace_M1_strengthening_no_later_eligibility
output = outputs/n30_medium_surface_trace_i5a.json
report = reports/n30_medium_surface_trace_i5a.md
script = scripts/build_n30_medium_surface_trace_i5a.py
output_digest = 519cc4efb48963232d969a6ecbf9d67e1b8dda005d89faed5f17995c233590ef
source_i5_output_digest = f84cfb6ca3ce06f699a8be2a680cdb75707a637b4b6abb167dbc66b681ccc971
source_n28_i4a2_output_digest = f2785e97307704bff58e413eb071aff10311f0a3d6bd753ebccfb4c1975b6c20
participant_ladder_rung = P2_candidate_with_I4B_P4_guardrail
strongest_N30_I5A_row_participant_rung = P2_candidate
source_i4b_strongest_participant_guardrail = P4_candidate
medium_relation_ladder_rung = M1_candidate
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
runtime_origin = inherited_N28_source_current_artifact
n30_fresh_runtime = false
i5a_claim_type = inherited_medium_surface_trace_admission
participant_carrier_id = n28_i4a2_focal_basin_epsilon
medium_surface_id = n28_i4a2_split_neighbor_capacity_shell_epsilon
medium_surface_scope = shared_local
medium_surface_scope_status = shared_local_candidate_pending_later_encounter
participant_medium_distinct = true
neighbor_distinguishability_delta = 0.141
neighbor_support_delta = 0.084
neighbor_boundary_delta = 0.132
environment_capacity_delta = 0.127
trace_persistence_status = replay_persistent_no_decay_curve
i5_replaced = false
i5a_strengthens_i5 = true
i5a_strengthening_kind = mechanism_diversity_repeatability_not_margin_upgrade
margin_upgrade_claimed = false
source_guardrail_controls = N28_controls_only
n30_relation_controls = pending_iteration_7
trace_dependency_control_ids = pending_iteration_7
artifact_count = 9
source_current_input_count = 13
failed_checks = []
medium_surface_trace_evidence_opened = true
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
ready_for_iteration_6_later_eligibility_probe = true
```

Interpretation:

```text
I5-A strengthens I5 by showing that the N30 M1 medium-surface trace result is
not confined to the I5 single-shell strengthening mechanism. It consumes the
N28 I4-A2 split-shell / delayed-boundary mechanism-diversity row and replay
trace. The local participant side is the I4-A2 focal basin, and the medium
surface is the distinct split neighboring capacity shell.

Like I5, I5-A is inherited/source-current medium-surface admission, not fresh
N30 runtime evidence. N28 I4-A2 artifacts may support C4/M1 surface-trace
admission. They may not support C5/M2 later eligibility dependency unless I6/I7
add a new N30 relation-chain dependency test.

Geometrically, the focal basin remains viable while a split neighboring shell
becomes more distinguishable, better supported, better bounded, and more
basin-forming. This is the same M1 kind of medium-surface perturbation / trace
evidence as I5, but through a different source-current mechanism.

I5-A is not a larger-margin upgrade. Its deltas are slightly smaller than I5:
0.141 / 0.084 / 0.132 / 0.127 versus I5's
0.154 / 0.087 / 0.145 / 0.134. The value is repeatability and mechanism
diversity. I5 remains the primary minimal M1 row; I5-A is additional
mechanism-diverse M1 evidence. It does not replace I5, widen M1 into M2,
support later eligibility dependency, or support minimal shared-medium
participation.

The N28 controls consumed by I5-A are source guardrail controls, not N30
relation controls. I7 must still run or instantiate direct-message removal,
trace-ablation, wrong-surface, time-reversal, medium-freeze, trace-shuffle,
false-trace, decay, susceptibility-inversion, and hidden-producer controls
against the actual I5-A/I6 relation chain.
```

## Iteration 5-B - Medium Surface Persistence / Scope-Window Probe

- [x] Consume I5 as the primary single-shell C4/M1 medium-surface trace row.
- [x] Consume I5-A as the split-shell mechanism-diverse C4/M1 medium-surface trace row.
- [x] Consume N28 neighbor-capacity stress rows for the I5 and I5-A source mechanisms.
- [x] Test whether a broader local medium-surface scope is supported.
- [x] Test whether replay/stress-variant persistence is supported.
- [x] Separate stress/replay persistence from true temporal decay.
- [x] Block slow-trace, medium-memory, C5/M2, and minimal shared-medium participation claims.

Result:

```text
status = passed
acceptance_state = accepted_C4_M1_scope_window_audit_split_scope_supported_temporal_decay_blocked
output = outputs/n30_medium_surface_scope_window_i5b.json
report = reports/n30_medium_surface_scope_window_i5b.md
script = scripts/build_n30_medium_surface_scope_window_i5b.py
output_digest = b795a864f4db404b4a620fac248d9fc47f6ef508c2929d6e82639dca9427d956
source_i5_output_digest = f84cfb6ca3ce06f699a8be2a680cdb75707a637b4b6abb167dbc66b681ccc971
source_i5a_output_digest = 519cc4efb48963232d969a6ecbf9d67e1b8dda005d89faed5f17995c233590ef
source_n28_stress_matrix_output_digest = fe051d860391bdbceddc2892abd49dc117b8a5797b3802d77609b1578e1ad756
medium_relation_ladder_rung = M1_candidate
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
runtime_origin = inherited_N28_source_current_artifact
n30_fresh_runtime = false
larger_local_scope_supported = true
scope_extension_kind = local split-shell surface broader than the I5 single-shell medium surface, not a global shared medium
shared_global_scope_supported = false
replay_and_stress_variant_persistence_supported = true
longer_temporal_window_supported = false
temporal_decay_window_supported = false
slow_trace_or_medium_memory_supported = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
artifact_count = 4
source_current_input_count = 5
failed_checks = []
ready_for_iteration_6_later_eligibility_probe = true
```

Interpretation:

```text
I5-B strengthens C4/M1 by showing that the medium-surface trace portfolio is
not limited to the I5 single-shell surface. I5-A supplies a broader local
split-shell surface, and both I5 and I5-A survive replay plus the N28
neighbor-capacity compression stress variant. This supports local
scope-broadening and replay/stress-variant persistence for the C4 surface
trace.

I5-B does not support a true longer temporal window. Stress variants, duplicate
replay, and snapshot/load replay are not decay curves. Therefore slow trace,
medium memory, long-horizon persistence, C5/M2, and minimal shared-medium
participation remain blocked. I6 may consume the exact I5/I5-A surface ids and
relation chains, but it must add new later-response dependency evidence rather
than inheriting it from I5-B.
```

## Iteration 6 - Later Eligibility / Susceptibility Probe

- [x] Record later eligibility, cost, support, routing, susceptibility, or capacity change.
- [x] Predeclare `later_response_metric`, `expected_direction`, `response_window`, `baseline_window`, `acceptance_threshold`, and `normalization_denominator`.
- [x] Record effect size and counterfactual row.
- [x] Show later change depends on the changed medium surface.
- [x] Link participant event, perturbation event, trace/surface change, and later response in one `relation_chain_id`.
- [x] Preserve N28-style environment-effect distinction where relevant.
- [x] Block generic redistribution and semantic relation relabels.

Result:

```text
status = passed
acceptance_state = accepted_provisional_M2_later_eligibility_dependency_candidate_pending_I7_controls
output = outputs/n30_later_eligibility_i6.json
report = reports/n30_later_eligibility_i6.md
script = scripts/build_n30_later_eligibility_i6.py
output_digest = 44281258a0b7f62fa01a067bd4e308c4d35996e7c36333e2987458c672d3a7f4
source_i5_output_digest = f84cfb6ca3ce06f699a8be2a680cdb75707a637b4b6abb167dbc66b681ccc971
source_i5a_output_digest = 519cc4efb48963232d969a6ecbf9d67e1b8dda005d89faed5f17995c233590ef
source_i5b_output_digest = b795a864f4db404b4a620fac248d9fc47f6ef508c2929d6e82639dca9427d956
source_n28_transition_matrix_output_digest = e6b0afbf81873e519db458e611cc01a1c11b2e9b5c2dead899946b270077700d
participant_ladder_rung = P2_candidate_with_I4B_P4_guardrail
medium_relation_ladder_rung = M2_candidate_pending_I7_controls
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate_with_provisional_C5_input_evidence
later_eligibility_dependency_evidence_opened = true
n30_c5_input_evidence_supported = true
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
final_n30_c6_claim_allowed = false
runtime_origin = inherited_N28_source_current_transition_artifacts
n30_fresh_runtime = false
candidate_row_count = 2
minimum_threshold_margin = 0.002
minimum_effect_size_vs_neutral = 1.028056
minimum_effect_size_vs_extractive_cross = 1.738751
effect_margin_class = narrow_positive
artifact_count = 6
source_current_input_count = 10
failed_checks = []
ready_for_iteration_7_replay_controls = true
```

Interpretation:

```text
I6 opens provisional M2 input evidence by linking each I5/I5-A participant
event, medium perturbation, medium-surface change, and later same-policy
boundary-edge eligibility trace into a single ordered relation chain. The later
eligibility metric is predeclared as the same-policy generative boundary-edge
eligibility score normalized by the I5/I5-A surface-change thresholds.

The geometric dependency is narrow but explicit: the later boundary-edge
response stays eligible only when the medium surface retains positive
distinguishability, support, boundary, and environment-capacity deltas above
threshold. The neutral-gap counterfactual has no medium-surface gain and stays
unclassified. The extractive-cross counterfactual changes the surface in the
opposite direction and stays extractive. This blocks label-only eligibility and
generic redistribution relabels for I6.

I6 is not final N30-C5. The minimum positive threshold margin is 0.002, and the
full replay/control matrix has not run. Therefore minimal shared-medium
participation, N30-C5 closeout, N30-C6 handoff, coordination, native
shared-medium organization, agency, sentience, and ecology-regime claims remain
blocked pending I7/I8.
```

Margin interpretation:

```text
The 0.002 I6 margin is raw threshold headroom, not transmitted mass. It is the
smallest distance between a later medium-conditioned axis and its declared
surface-change threshold.

Observed I6 edge axes:
  environment_capacity_delta = 0.092 against threshold 0.090
  neighbor_boundary_delta = 0.082 against threshold 0.080
  neighbor_distinguishability_delta = 0.082 against threshold 0.080
  neighbor_support_delta = 0.052 against threshold 0.050

Mean observed axis delta ~= 0.077
Mean threshold ~= 0.075
Raw mean headroom ~= 0.002
Relative headroom vs mean threshold ~= 2.7%
Mean normalized score = 1.028056

So I6 is a narrow positive result in normalized geometric-threshold terms,
not just a raw 0.2% result. The weakest raw headroom remains 0.002, which is
why the row stays provisional pending I7 controls.
```

## Iteration 6-A - Later Eligibility Contrast-Margin Probe

- [x] Consume I6 as the provisional M2 later-eligibility dependency candidate.
- [x] Predeclare a separate counterfactual contrast-margin policy.
- [x] Confirm N28 thresholds are not retuned and I6 threshold margin is not reinterpreted.
- [x] Measure separation from neutral-gap counterfactuals.
- [x] Measure separation from opposite-regime extractive counterfactuals.
- [x] Preserve the narrow I6 threshold-margin caveat.
- [x] Keep final C5/C6 and minimal shared-medium participation claims blocked.

Result:

```text
status = passed
acceptance_state = accepted_M2_dependency_contrast_margin_strengthening_no_threshold_margin_upgrade
output = outputs/n30_later_eligibility_margin_i6a.json
report = reports/n30_later_eligibility_margin_i6a.md
script = scripts/build_n30_later_eligibility_margin_i6a.py
output_digest = 145d5bf2acda7b049df43c5c9b5742fb33920e0dfc11d955cd795b5620cecad7
source_i6_output_digest = 44281258a0b7f62fa01a067bd4e308c4d35996e7c36333e2987458c672d3a7f4
medium_relation_ladder_rung = M2_candidate_pending_I7_controls
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate_with_strengthened_provisional_C5_input_evidence
source_i6_threshold_margin = 0.002
higher_threshold_margin_supported = false
dependency_contrast_margin_supported = true
minimum_dependency_contrast_margin_vs_neutral = 0.042
minimum_dependency_contrast_margin_vs_extractive = 0.044
n30_c5_input_evidence_supported = true
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
final_n30_c6_claim_allowed = false
artifact_count = 3
failed_checks = []
ready_for_iteration_7_replay_controls = true
```

Interpretation:

```text
I6-A strengthens I6 by separating two margin meanings. The original I6
threshold margin remains narrow at 0.002; I6-A does not improve or hide that.
Instead, I6-A asks whether the same M2 dependency is clearly separated from the
active counterfactuals.

The answer is positive: the minimum axis-level dependency contrast margin is
0.042 against the neutral-gap counterfactual and 0.044 against the
extractive-cross counterfactual. This makes the later-eligibility dependency
less label-fragile than the raw threshold margin suggests, while preserving the
claim boundary. I6-A strengthens provisional M2 input evidence; it does not
finalize N30-C5/C6.
```

## Alternative Source Tranche - I4-C through I6-C

Reason:

```text
I6/I6-A prove the dependency shape, but they remain tied to the N28 generative
edge threshold margin of 0.002. The alternative tranche tests whether the N30
contract holds on a different source geometry: N28 I4-F higher-margin neutral
circulation, where the medium is a route-conductance / circulatory neighbor
surface rather than a generative enrichment surface.
```

### Iteration 4-C - Alternative Participant / Source Fixture Admission

- [x] Consume N28 I4-F higher-margin neutral circulation as an alternative source fixture.
- [x] Admit the focal basin as a P2 participant candidate.
- [x] Keep medium relation claims closed.

Result:

```text
status = passed
acceptance_state = accepted_alternative_P2_participant_source_fixture_no_medium_claim
output = outputs/n30_alternative_participant_source_i4c.json
report = reports/n30_alternative_participant_source_i4c.md
output_digest = 80f5346ac422749246050bc5e4514c323ea63f7dc7d49394628ad2b6860d668d
participant_ladder_rung = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung = not_assigned
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
failed_checks = []
```

### Iteration 5-C - Alternative Medium-Surface Trace

- [x] Declare the N28 I4-F wide circulatory neighbor field as the medium surface.
- [x] Record lobe exchange as the surface-change mechanism.
- [x] Keep later eligibility and final C5 claims closed.

Result:

```text
status = passed
acceptance_state = accepted_alternative_M1_circulatory_medium_surface_trace
output = outputs/n30_alternative_medium_surface_i5c.json
report = reports/n30_alternative_medium_surface_i5c.md
output_digest = 754c8cabeeb35d4274b2841ecc7458eeebb9c1eee8c1c5d26782c38a4bf2b335
participant_ladder_rung = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung = M1_candidate_alternative_circulatory_surface
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
minimum_lobe_exchange_margin = 0.02
minimal_shared_medium_participation_claim_allowed = false
failed_checks = []
```

### Iteration 5-D - Alternative Scope / Stress Audit

- [x] Consume N28 focused replay and stress envelope for I4-F.
- [x] Record stress margins for the alternative circulatory surface.
- [x] Keep later eligibility claims closed until I6-B.

Result:

```text
status = passed
acceptance_state = accepted_alternative_M1_circulatory_surface_replay_stress_audit
output = outputs/n30_alternative_scope_stress_i5d.json
report = reports/n30_alternative_scope_stress_i5d.md
output_digest = 5052dc86851af8f12bc26949a640b6df4eb766183255b83a8b90416eeff13b92
participant_ladder_rung = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung = M1_candidate_alternative_circulatory_surface
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
minimum_current_margin = 0.006
neighbor_capacity_current_margin = 0.01
failed_checks = []
```

### Iteration 6-B - Alternative Later Eligibility Probe

- [x] Link the circulatory medium surface to later route-conductance eligibility.
- [x] Record improved threshold margin relative to original I6.
- [x] Keep final C5/C6 blocked pending I7.

Result:

```text
status = passed
acceptance_state = accepted_alternative_M2_later_eligibility_candidate_pending_I7_controls
output = outputs/n30_alternative_later_eligibility_i6b.json
report = reports/n30_alternative_later_eligibility_i6b.md
output_digest = df9d1789199368ac62385e3e0052d2dcfaf4858bb44eecc338e66b07240f10f5
participant_ladder_rung = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung = M2_candidate_alternative_source_pending_I7_controls
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate_with_alternative_C5_input_evidence
alternative_neighbor_capacity_threshold_margin = 0.01
alternative_lobe_exchange_margin = 0.02
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
failed_checks = []
```

Margin interpretation:

```text
I6-B contains two margin meanings.

Lobe-exchange margin:
  inflow_lobe_capacity_delta = 0.062
  outflow_lobe_capacity_delta_abs = 0.060
  mixed_lobe_delta_min = 0.040
  minimum_lobe_exchange_margin = 0.020

This is about 50% headroom relative to the lobe threshold, or about 33% of the
observed minimum lobe delta. That is stronger than the original I6 threshold
edge.

Neighbor-capacity stress margin:
  neighbor_capacity_stress_margin = 0.010

This is the stress-envelope gate headroom used for the 5x comparison against
the original I6 0.002 edge margin. It is not itself the lobe-transfer amount.
The underlying stress artifact records the limiting field and gate headroom,
but not enough observed-value/threshold detail to compute a clean relative
percentage for that stress margin.
```

### Iteration 6-C - Alternative Contrast / Margin Audit

- [x] Compare the alternative I6-B margin to the original I6 edge margin.
- [x] Record mechanism contrast against the competitive direct two-lobe counterfactual.
- [x] Preserve the final C5/C6 claim boundary.

Result:

```text
status = passed
acceptance_state = accepted_alternative_source_margin_and_mechanism_contrast_audit_no_final_C5
output = outputs/n30_alternative_contrast_margin_i6c.json
report = reports/n30_alternative_contrast_margin_i6c.md
output_digest = bb4930b3423156f4aac9b023cb14efb3c7bc8d707518395b2b95fe79fd39a403
participant_ladder_rung = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung = M2_candidate_alternative_source_pending_I7_controls
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate_with_alternative_C5_input_evidence
threshold_margin_delta_vs_i6 = 0.008
threshold_margin_ratio_vs_i6 = 5.0
alternative_lobe_exchange_margin = 0.02
broad_margin_robustness_supported = false
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
failed_checks = []
```

Interpretation:

```text
The alternative source tranche does not replace I6. It adds a second M2-shaped
source family with different medium geometry. The original I6 remains the
generative-edge relation with narrow 0.002 threshold margin. I6-B/I6-C add a
circulatory route-conductance relation with 0.010 neighbor-capacity threshold
margin and 0.020 lobe-exchange margin. This is a fivefold threshold-margin
improvement relative to I6, but not broad robustness. Final N30-C5/C6 remain
blocked until I7 relation controls pass.
```

Detailed margin reading:

```text
The 5x statement compares only raw gate headroom:
  original I6 edge threshold margin = 0.002
  alternative I6-B neighbor-capacity stress margin = 0.010
  ratio = 5.0

It should not be read as "five times the transmitted capacity." The stronger
capacity-change evidence in I6-B is the lobe exchange:
  0.060/0.062 observed lobe deltas against a 0.040 threshold.

Thus the fuller interpretation is:
  I6 = narrow normalized generative-edge eligibility headroom (~2.7-2.8% over
       the mean threshold, raw weakest margin 0.002).
  I6-B = stronger lobe-exchange medium geometry plus a 5x larger raw stress
         gate headroom, but still pending I7 replay/control.
```

## Iteration 7 - Replay, Controls, And Medium Debt Matrix

- [x] Run artifact-only replay.
- [x] Run duplicate replay.
- [x] Run snapshot/load replay.
- [x] Recompute later-response metric for each candidate row.
- [x] Run direct-message removal control.
- [x] Run no-perturbation control.
- [x] Run trace-ablation control.
- [x] Run wrong-surface control.
- [x] Run time-reversed trace control.
- [x] Run medium-freeze control.
- [x] Run trace-shuffle control.
- [x] Run false-trace injection control.
- [x] Run decay manipulation control.
- [x] Run susceptibility inversion control.
- [x] Run hidden producer / global controller controls.
- [x] Reinstantiate all I2/I3 required fail-closed controls against positive rows.
- [x] Record medium debt and producer residue per row.

Result:

```text
status = passed
acceptance_state = accepted_replay_control_backed_C5_candidate_pending_I8_closeout
output = outputs/n30_replay_controls_i7.json
report = reports/n30_replay_controls_i7.md
script = scripts/build_n30_replay_controls_i7.py
output_digest = 46f7eba93fa206355f4dc3eb5b2ae8e70dd1126eba975030a2e2fc15f1603fec
candidate_row_count = 3
required_control_count = 20
total_control_result_count = 60
failed_open_control_count = 0
not_run_control_count = 0
all_required_replay_modes_passed = true
all_required_controls_failed_closed = true
participant_ladder_rung = P2_candidate_with_I4B_P4_guardrail
medium_relation_ladder_rung = M2_replay_control_backed_C5_candidate
n30_closeout_ceiling = N30-C5_replay_control_backed_candidate_pending_I8
n30_c5_candidate_supported = true
minimal_shared_medium_participation_candidate_supported = true
final_n30_closeout_rung = not_assigned
final_n30_c5_claim_allowed = false
final_n30_c6_claim_allowed = false
failed_checks = []
ready_for_iteration_8_classification_closeout = true
ready_for_iteration_8_classification_spiral_handoff = true
post_n30_handoff_mode = cross_project_spiral_pending_I8
agentic_ecology_demand_pass_recommended = true
candidate_n31_interface_available_pending_i8 = true
candidate_n31_selected = false
next_lgrc_experiment_fixed = false
```

Candidate coverage:

```text
original generative-edge family:
  n30_i6_row_01_i5_single_shell_later_eligibility_candidate
  n30_i6_row_02_i5a_split_shell_later_eligibility_candidate

alternative circulatory family:
  n30_i6b_row_01_i4f_circulatory_route_eligibility_candidate
```

Interpretation:

```text
I7 is the first replay/control-backed N30-C5 candidate layer. It consumes the
original I6/I6-A generative-edge M2 rows and the alternative I6-B/I6-C
circulatory M2 row. For each row, artifact-only replay, duplicate replay,
snapshot/load replay, and later-response metric recomputation pass.

All 20 required I2/I3 controls are reinstantiated against each positive row,
for 60 total control results. Every false-positive path fails closed; there
are no failed-open or not-run controls.

This supports N30-C5 candidate evidence, not final N30 closeout. I8 still has
to assign the final closeout rung, record the post-N30 cross-project spiral
handoff, decide whether a candidate N31 interface is available without selecting
N31 by default, and preserve medium/producer debt. N30-C6, shared-medium
coordination, parent-basin modulation, resonance, native shared-medium
organization, agency, sentience, and ecology-regime claims remain blocked.
```

## Iteration 8 - Classification And Post-N30 Spiral Handoff

- [x] Classify strongest participant ladder rung.
- [x] Classify strongest shared-medium relation rung.
- [x] Classify coupled relation-chain support.
- [x] Confirm N30-C5/C6 are blocked unless participant + non-private medium surface + trace/surface change + later eligibility dependency pass replay/control.
- [x] Assign N30 closeout rung if warranted.
- [x] Record final claim ceiling.
- [x] Record blocked claims.
- [x] Record `post_n30_handoff_mode = cross_project_spiral`.
- [x] Record whether an agentic ecology demand/composition pass is recommended.
- [x] Record whether a candidate N31 interface is available.
- [x] Keep `candidate_n31_selected = false` unless a demand map justifies selecting N31 now.
- [x] Keep `next_lgrc_experiment_fixed = false` unless a demand map justifies fixing the next LGRC experiment now.
- [x] Confirm shared-medium coordination, parent-basin modulation, resonance, native shared-medium organization, agency, ecology regime, sentience, organism/life, and unrestricted autonomy remain blocked.

Result:

```text
status = passed
acceptance_state = accepted_N30_C6_post_N30_spiral_ready_minimal_shared_medium_participation_closeout
output = outputs/n30_closeout_and_spiral_handoff_i8.json
report = reports/n30_closeout_and_spiral_handoff_i8.md
script = scripts/build_n30_closeout_i8.py
output_digest = 7971163b1d7bd4027f5375270cfb2445cfe4698a8869b28e26f9273d0a5b5af6
source_i7_output_digest = 46f7eba93fa206355f4dc3eb5b2ae8e70dd1126eba975030a2e2fc15f1603fec
participant_ladder_rung = P2_minimally_stable_participant_with_P4_guardrail_context
medium_relation_ladder_rung = M2_trace_mediated_eligibility_replay_control_backed_candidate
final_n30_closeout_rung = N30-C6_post_N30_spiral_ready_minimal_shared_medium_participation_closeout
n30_c5_replay_control_backed_candidate_supported = true
n30_c6_spiral_ready_closeout_supported = true
bounded_minimal_shared_medium_participation_candidate_supported = true
trace_mediated_eligibility_primitive_candidate_supported = true
post_n30_handoff_mode = cross_project_spiral
agentic_ecology_demand_pass_recommended = true
candidate_n31_interface_available = true
candidate_n31_selected = false
next_lgrc_experiment_fixed = false
ready_for_agentic_ecology_demand_pass = true
ready_for_fixed_N31_selection = false
failed_checks = []
```

Interpretation:

```text
I8 closes N30 at N30-C6, but only as a bounded artifact-level minimal
shared-medium participation candidate. The result is supported by I7
replay/control evidence across both the original generative-edge family and
the alternative circulatory family.

The final claim is not shared-medium coordination, communication, cooperation,
agency, native shared-medium organization, parent-basin modulation, resonance,
sentience, or ecology regime. N30 establishes that the minimal relation chain
can be made replay/control-clean:
  participant continuity
  -> non-private medium surface perturbation
  -> source-current trace/surface change
  -> later eligibility/susceptibility dependence

The post-N30 handoff is a cross-project spiral. N30 exposes a candidate
interface for future N31-style LGRC work, but it does not select N31 by default.
The next recommended step is an agentic-ecology demand/composition pass that
decides which shared-medium building block should be tested next.

Margin interpretation:
  I6 original generative-edge rows remain narrow in raw threshold headroom
  (minimum 0.002), but have stronger contrast margins against neutral/extractive
  counterfactuals (0.042/0.044). I6-B contributes the alternative circulatory
  source with threshold margin 0.01 and lobe-exchange margin 0.02. The fivefold
  raw threshold-margin improvement strengthens confidence, but does not turn
  the result into broad shared-medium robustness or native organization.
```

## Closure-Continuation Interpretation

```text
N30's large-scheme contribution is that "shared medium" is no longer only a
theoretical or ecological phrase inside the N30+ roadmap. N30 grounds it as a
minimal LGRC relation form:

  participant continuity
  -> non-private medium surface perturbation
  -> source-current trace / surface change
  -> later eligibility or susceptibility depends on that changed surface
  -> replay/control validation

Before N30, the relevant pieces were separate:
  N27 showed configuration/topology recognizability across transfer.
  N28 showed generative, extractive, competitive, and neutral environmental
      reshaping regimes.
  N29 showed that these pieces can be arranged into bridge motifs.
  Shared-medium ecology documents supplied vocabulary and engineering
      discipline.

N30 adds the missing lowest shared-medium rung. It shows that a fully stable
self or agency candidate is not required before shared-medium participation can
begin. A minimally stable participant can participate if its trace changes a
non-private surface and later eligibility depends on that changed surface.

What N30 enables:
  trace-conditioned eligibility:
    a participant leaves a surface change that makes later routes, basins, or
    interactions more or less admissible.

  shared support redistribution:
    a participant changes a local support/capacity field, and later
    participants become easier or harder to sustain because of that field.

  slow conductance / memory trace:
    the medium carries a persistent or decaying conductance change, not a
    private message.

  boundary-mediated exchange:
    participants affect one another indirectly through boundary surfaces,
    permeability, or route costs.

  stigmergic trail-like fields:
    not semantic communication, but trace-mediated eligibility where prior
    passage changes later passage conditions.

  capacity circulation:
    N28-style generative, extractive, and neutral patterns can become later
    routing or eligibility conditions.

  ecological demand mapping:
    agentic ecology can now ask which medium surfaces forest, colony, niche,
    or support-field motifs require, and which of those LGRC can express.

This is why N30 should not hand off directly to a fixed N31. The correct
continuation is:

  N30 LGRC result
  -> agentic ecology demand/composition pass
  -> selected N31+ primitive or building-block experiment

Claim boundary:
  N30 enables composable environmental participation patterns.
  N30 does not claim shared-medium coordination, cooperation, communication,
  agency, native shared-medium organization, parent-basin modulation, resonance,
  sentience, organism/life, or ecology regime.
```
