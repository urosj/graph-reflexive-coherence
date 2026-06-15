# N13 Self-Maintenance And Support-Seeking Regulation Implementation Plan

This document records the implementation plan for
`2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation`.

N13 is an agency-prerequisite experiment. It asks whether artifact-level LGRC
composition can regulate toward source-current support conditions rather than
only an externally declared proxy.

## Scope

N13 is experiment-local unless a separate Phase 8/native implementation task is
opened. Scripts, configs, reports, outputs, hypotheses, and implementation
records live under:

```text
experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/
```

Do not change `src/*` for N13 without stopping and opening a separate Phase 8
task. If Phase 8 is later opened, inspect native telemetry surfaces under
`src/pygrc/telemetry` as well as core/model code.

## Inherited Evidence

N13 consumes N12 as the direct source boundary, and through N12 consumes N07,
N09, N10, and N11 support/regulation evidence.

Direct N12 source state:

```text
final_status = closed_claim_clean_bridge_experiment
strongest_recorded_level = NAT4
phase8_ready_contracts = native_route_conductance_memory_policy, native_response_magnitude_policy
native_supported_flags = false
phase8_opened = false
phase8_implementation_opened = false
```

N12 handoff for N13:

```text
consume support-survival, support-disruption, explicit restoration,
route-memory, and bounded response evidence
do not consume identity acceptance
begin as support-seeking regulation, not identity-seeking regulation
```

## Target

N13 targets:

```text
AP3 = self-maintenance candidate
```

This means:

```text
source-backed support-condition inventory
-> support-condition schema and AP mapping
-> support-derived target candidate
-> support-seeking regulation candidate
-> external proxy and hidden target controls
-> support disruption/restoration stress matrix
-> identity/agency boundary record
-> no Phase 8 implementation unless separately opened
```

This is not agency, intention, semantic goal ownership, identity acceptance,
selfhood, biological behavior, personhood, unrestricted agency, or fully
native agentic-like integration.

## AP Ladder

N13 uses the `AP0-AP8` ladder from the N12-N18 roadmap:

```text
AP0 = passive integrated replay
AP1 = runtime-visible trigger produces bounded response
AP2 = support-sensitive regulation preserves a declared support condition
AP3 = self-maintenance candidate
AP4 = consequence-sensitive selection
AP5 = endogenous proxy candidate
AP6 = self/environment boundary candidate
AP7 = closed action-perception loop candidate
AP8 = long-horizon agentic-like closure candidate
```

N13 aims for `AP3`. `AP4` and later require later experiments.

`AP3` means the regulated target is derived from source-current support state
rather than only from an external fixture label. It does not imply identity
acceptance, semantic goal ownership, intention, or agency.

## Candidate Row Shape

Iteration 2 should freeze the final schema, but Iteration 1 inventory rows
should include at least:

```text
row_id
source_experiment
source_iteration
source_artifact
source_report
source_sha256
source_report_sha256
mechanism_name
mechanism_role
support_state_fields
external_proxy_fields
producer_decision_fields
bookkeeping_fields
runtime_visible_surfaces
budget_surfaces
response_surfaces
support_condition_name
target_derivation
provisional_ap_level
provisional_self_maintenance_candidate
claim_ceiling
blocked_claims
missing_gates
control_requirements
```

## Required Controls

Every candidate row must preserve:

```text
external_proxy_relabel_blocked
hidden_support_target_blocked
post_hoc_support_label_blocked
support_disrupted_regulation_blocked
identity_acceptance_relabel_blocked
semantic_goal_ownership_relabel_blocked
agency_relabel_blocked
budget_ambiguity_blocked
stale_source_replay_blocked
native_support_relabel_blocked
```

## Hypothesis Tracks

Hypothesis A:

```text
Source-backed support-state evidence can be inventoried into candidate support
conditions without promoting support survival into identity acceptance.
```

Hypothesis B:

```text
Support-seeking regulation can be distinguished from external proxy regulation
when the target condition is derived from source-current support state,
serialized, replayable, budgeted, and control-clean.
```

Hypothesis C:

```text
Even if support-seeking regulation is observed, identity acceptance, semantic
goal ownership, intention, agency, and fully native integration remain blocked
unless separate theory and native implementation gates are satisfied.
```

## Iterations

### Iteration 0. Planning And Stubs

Create the N13 experiment root, README, implementation plan, implementation
checklist, hypotheses files, and directory stubs. Freeze N13 as an
artifact-level agency-prerequisite experiment, not a native implementation or
agency claim.

Result:

```text
Status: complete.
Target agency-prerequisite level: AP3.
Phase 8 implementation opened: false.
Native support opened: false.
Identity acceptance opened: false.
Agency claim opened: false.
```

### Iteration 1. Baseline Source And Support-Condition Inventory

Collect N07 support survival/disruption/restoration evidence, N09 bounded
proxy regulation evidence, N10 support-sensitive integration evidence, N11
GALI7 artifact-only generalization evidence, and N12 readiness/blocker records.
Record exact source paths, report paths, SHA-256 digests, support-state fields,
external proxy fields, producer decisions, bookkeeping fields, response
surfaces, budget surfaces, claim ceilings, and blocked claims.

Expected artifacts:

```text
outputs/n13_support_condition_inventory.json
reports/n13_support_condition_inventory.md
scripts/build_n13_support_condition_inventory.py
```

Acceptance statement:

```text
Iteration 1 passes if every support-condition row is source-backed and N13
records support-state, external-proxy, producer-decision, budget, replay, and
claim-boundary fields without promoting support survival into identity
acceptance or native support.
```

Result:

```text
Status: passed.
Artifact: outputs/n13_support_condition_inventory.json
Report: reports/n13_support_condition_inventory.md
Output digest: 4c8cd0a1ea074d27ff1a7cd5cdd176b789ef57da808223c1fa08750355732e23
```

Iteration 1 records seven source-backed rows from N07, N09, N10, N11, and N12.
The inventory contains two `AP0` boundary/envelope rows, two `AP1` bounded
response/readiness rows, three `AP2` support-condition or support-sensitive
rows, and zero `AP3` self-maintenance rows. The summary separates actual
support-condition rows from N11/N12 boundary rows. It records support-state
fields, external proxy fields, producer decisions, bookkeeping fields,
runtime-visible surfaces, budget surfaces, response surfaces, claim ceilings,
blocked claims, and source/report SHA-256 digests. Identity acceptance, native
support, Phase 8 implementation, and agency remain unopened.

### Iteration 2. Support-Condition Schema And AP Mapping

Define the final row schema, AP-level criteria, support-condition tags,
support-derived target fields, external proxy separation fields, claim flags,
budget/replay fields, telemetry requirements, and fail-closed controls.

Expected artifacts:

```text
outputs/n13_support_schema_v1.json
reports/n13_support_schema_v1.md
scripts/build_n13_support_schema_v1.py
```

Acceptance statement:

```text
Iteration 2 passes if the schema distinguishes AP2 support-sensitive
regulation from AP3 self-maintenance candidates and rejects identity
acceptance, semantic goal ownership, agency, stale source use, hidden target
use, and budget ambiguity.
```

Result:

```text
Status: passed.
Artifact: outputs/n13_support_schema_v1.json
Report: reports/n13_support_schema_v1.md
Output digest: 7691834eb654dc15ee8aabf8ce732a10a72c375d95f3fa97290a8b6cf6984a4f
```

Iteration 2 freezes the `AP0-AP8` mapping for N13, the support-condition row
schema, AP2/AP3 criteria, primary dispositions, control flags, fail-closed
blockers, forced-false claim flags, and validation-scope note. It explicitly
states that AP3 assignment requires all AP3 gates and that row validation
against AP3 starts in Iterations 3-7.

### Iteration 3. Support-State Derived Target Candidate

Evaluate whether source-current support-state fields can define a target
condition without external fixture labels or post-hoc interpretation.

Required checks:

```text
support_state_fields
support_condition_name
target_derivation
source_current_requirement
runtime_visible_surfaces
producer_decision_split
bookkeeping_split
identity_acceptance_relabel_blocked
semantic_goal_ownership_relabel_blocked
```

Expected artifacts:

```text
outputs/n13_support_derived_target_candidate.json
reports/n13_support_derived_target_candidate.md
scripts/build_n13_support_derived_target_candidate.py
```

Result:

```text
Status: passed.
Artifact: outputs/n13_support_derived_target_candidate.json
Report: reports/n13_support_derived_target_candidate.md
Output digest: 917e65721362fcda37ea4777489a5e3289a35ef550a16b3774884c803584ac3e
```

Iteration 3 isolates `support_retention_above_threshold_source_current` as a
source-current support-derived target candidate. The derivation rule is
`final_A_support_retention >= support_survival_threshold`, using N07 support
lane fields and threshold records. The target excludes N09 external proxy
fields, matches all N07 source lanes, cross-checks against the N10 support
matrix, and records post-hoc-label and hidden-target audits. It assigns only
provisional `AP2` target-candidate status: final `AP3`, self-maintenance
support, support-seeking regulation, native support, Phase 8 implementation,
identity acceptance, semantic goal ownership, and agency remain unopened.

### Iteration 4. Support-Seeking Regulation Candidate

Evaluate whether bounded regulation responses preserve or restore the derived
support condition under source-current replay.

Iteration 4 may assign only a candidate or provisional AP level. Final AP3
support must wait until Iterations 5-7 external-proxy, hidden-target,
post-hoc-label, support-disruption, restoration, and claim-boundary controls
pass.

Required checks:

```text
support_error_signal
response_magnitude_surface
bounded_window
budget_debit_surface
support_trend
saturation_status
overcorrection_status
out_of_envelope_blocker
```

Expected artifacts:

```text
outputs/n13_support_seeking_regulation_candidate.json
reports/n13_support_seeking_regulation_candidate.md
scripts/build_n13_support_seeking_regulation_candidate.py
```

Result:

```text
Status: passed.
Artifact: outputs/n13_support_seeking_regulation_candidate.json
Report: reports/n13_support_seeking_regulation_candidate.md
Output digest: a6c367246eaeba14953b87c4a89862238b5bde4568308f1ee4c7ef1d9c85116b
```

Iteration 4 records `support_error_bounded_response_candidate` as a bounded
support-error response candidate against the Iteration 3 source-current support
target. The support error signal is
`max(0, support_survival_threshold - final_A_support_retention)`, and the
response magnitude surface uses the N12/N09 bounded response readiness input:
`max_correction_per_window = 0.07`, `bounded_window_count = 4`,
`total_bounded_correction_capacity = 0.28`, and
`out_of_envelope_blocker = unbounded_perturbation_envelope_blocked`.

The disrupted N07 lane has support error `0.120134817816`, requiring two
bounded scheduled response packets under the policy-envelope estimate:
`[0.07, 0.050134817816]`. This is recorded as a candidate response schedule
with explicit budget debit and packet scheduling boundary. It does not mutate
native state and does not count the raw disrupted lane as supported before
response.

Iteration 4 assigns only candidate `AP3` status:

```text
candidate_ap_level = AP3
provisional_ap_level = AP3_candidate_pending_controls
final_ap3_supported = false
self_maintenance_candidate_supported = false
phase8_opened = false
native_support_opened = false
```

External-proxy, hidden-target, post-hoc-label, support-disruption/restoration,
and claim-boundary controls remain pending for Iterations 5-7.

### Iteration 5. External Proxy And Hidden Target Controls

Build controls that fail if the candidate is merely an externally declared
proxy, hidden producer target, post-hoc support label, or budget-ambiguous
correction.

Expected artifacts:

```text
outputs/n13_external_proxy_control_matrix.json
reports/n13_external_proxy_control_matrix.md
scripts/build_n13_external_proxy_control_matrix.py
```

Result:

```text
Status: passed.
Artifact: outputs/n13_external_proxy_control_matrix.json
Report: reports/n13_external_proxy_control_matrix.md
Output digest: 4894859811d54d1ebd80411847de5bd4670bfe8e282f3bffea3c0d0712ce7d16
```

Iteration 5 runs ten fail-closed controls around the Iteration 4
`support_error_bounded_response_candidate`: the nine planned controls plus an
explicit `native_support_without_phase8_control`. All controls reject their
adversarial interpretation:

```text
external_proxy_only_control = rejected
hidden_support_target_control = rejected
post_hoc_support_label_control = rejected
support_disrupted_regulation_control = rejected
stale_source_replay_control = rejected
budget_ambiguous_correction_control = rejected
identity_acceptance_relabel_control = rejected
semantic_goal_ownership_relabel_control = rejected
agency_relabel_control = rejected
native_support_without_phase8_control = rejected
```

Iteration 5 does not freeze final AP3 support. It updates the candidate state
only to:

```text
provisional_ap_level = AP3_candidate_control_clean_pending_stress_and_boundary
final_ap3_supported = false
self_maintenance_candidate_supported = false
phase8_opened = false
native_support_opened = false
```

Support-disruption/restoration stress remains pending for Iteration 6, and the
final identity, goal-ownership, agency, native-support, and integration claim
boundary record remains pending for Iteration 7.

Interpretation record:

```text
record_id = n13_i5_interpretation_external_proxy_controls_v1
meaning = Iteration 5 makes the Iteration 4 candidate control-clean against
external-proxy, hidden-target, post-hoc-label, stale-source, budget-ambiguity,
and unsafe claim-relabel explanations. It does not make final AP3 support.
supported_interpretation = artifact-level source-current support-error
bounded-response candidate, pending stress and boundary closure.
```

### Iteration 6. Support Disruption And Restoration Stress Matrix

Test whether the support-seeking candidate behaves differently under support
disruption, restoration, neutral perturbation, and no-support-control regimes.

Expected artifacts:

```text
outputs/n13_support_disruption_restoration_matrix.json
reports/n13_support_disruption_restoration_matrix.md
scripts/build_n13_support_disruption_restoration_matrix.py
```

Result:

```text
Status: passed.
Artifact: outputs/n13_support_disruption_restoration_matrix.json
Report: reports/n13_support_disruption_restoration_matrix.md
Output digest: f515ff673d38adba5d401088762040899add0e0f91d29f1f9d37de9100db7100
```

Iteration 6 stress-tests the candidate across five regimes:

```text
support_present_baseline = passed
support_disrupted_regime = passed
explicit_restoration_regime = passed
neutral_or_non_disruptive_perturbation_regime = passed
no_support_control_regime = passed
```

The candidate schedules a bounded budgeted response only for the source-current
support deficit. It avoids false-positive responses when support remains valid,
and it blocks response when no source-current support target is available.

Iteration 6 updates the candidate state to:

```text
support_disruption_restoration_stress_matrix_passed = true
support_seeking_regulation_survives_controls = true
provisional_ap_level = AP3_candidate_stress_clean_pending_claim_boundary
final_ap3_supported = false
self_maintenance_candidate_supported = false
phase8_opened = false
native_support_opened = false
```

Interpretation record:

```text
record_id = n13_i6_interpretation_stress_matrix_v1
meaning = stress-clean artifact-level AP3 support-seeking regulation candidate,
pending the Iteration 7 claim-boundary record.
```

### Iteration 7. Identity, Goal-Ownership, And Agency Boundary Record

Record why any positive N13 result is still not identity acceptance, semantic
goal ownership, intention, agency, selfhood, biological behavior, personhood,
or fully native integration.

Expected artifacts:

```text
outputs/n13_claim_boundary_record.json
reports/n13_claim_boundary_record.md
scripts/build_n13_claim_boundary_record.py
```

### Iteration 8. N13 Closeout And Handoff

Freeze supported AP level, close hypotheses, list blockers, and decide whether
next work is N14 or targeted Phase 8.

Expected artifacts:

```text
outputs/n13_closeout_and_handoff.json
reports/n13_closeout_and_handoff.md
scripts/build_n13_closeout_and_handoff.py
```

Acceptance statement:

```text
Iteration 8 passes if N13 classifies support-seeking regulation at its
supported AP level with source-backed controls and a claim-clean handoff,
without implementing Phase 8 or promoting support survival into identity
acceptance, semantic goal ownership, or agency.
```
