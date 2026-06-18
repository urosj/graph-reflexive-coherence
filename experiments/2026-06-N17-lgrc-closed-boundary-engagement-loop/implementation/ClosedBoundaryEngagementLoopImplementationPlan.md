# N17 Closed Boundary Engagement Loop Implementation Plan

## Purpose

N17 tests whether an artifact-level AP6 boundary candidate can support a
source-current closed boundary engagement loop.

The thesis is:

```text
N17 tests whether an artifact-level AP6 boundary candidate can support a
source-current closed boundary engagement loop: external state crosses or
pressures the boundary, internal support responds, the response modifies
external state, and the modified external state feeds back into later internal
support, under replay and fail-closed controls.
```

The bounded conclusion, if supported, is:

```text
artifact_level_closed_boundary_engagement_loop_candidate
```

Internally this maps to:

```text
AP7 = artifact-level closed action-perception loop candidate
```

N17 must not support agency, choice, intention, semantic perception, semantic
action, native self/environment model, life, organism behavior, native support,
fully native integration, or unrestricted agency.

## Source Rules

Iteration 1 must pin source artifacts before loop interpretation. Primary
source lanes are:

```text
N16 AP6 self/environment boundary closeout and claim boundary
N16 B3/C4 breach-reclosure candidate evidence
N16 B4/C5 shared-medium separability candidate evidence
N15 AP5 endogenous proxy formation closeout
N14 AP4 consequence-sensitive route selection closeout
N13 AP3 support-seeking regulation closeout
N09 bounded regulation and perturbation recovery context
N08 memory/context evidence
N12 NAT4 readiness records
```

N17 may consume N16 only as artifact-level AP6 boundary evidence. N16 boundary
crossing trace is not closed-loop evidence by itself.

N17 may consume N15 only as artifact-level AP5 endogenous proxy formation
context. N17 may consume N14 only as artifact-level AP4 consequence-sensitive
selection context. N17 may consume N13 only as artifact-level AP3 support
regulation context. N12 NAT4 records remain readiness-only unless a separate
Phase 8 task opens.

## Evidence Strategy

Iteration 1 should first check whether historic artifacts directly support
ordered loop closure:

```text
external -> internal -> external -> later internal
```

If direct support exists, use it only if source-backed, claim-clean,
replay-clean, order-clean, and control-clean.

The expected construction starts from N16 AP6 separability and tests whether
one-way crossing becomes closure:

```text
N16 boundary sides and boundary-crossing traces
N13/N15 internal support response context
N14 consequence-sensitive selection context
N08/N09 memory and bounded regulation context
```

The proof target is not the presence of an "action" label. The proof target is
ordered trace dependence:

```text
external_to_internal_trace
internal_response_trace
response_to_external_change_trace
external_feedback_to_internal_trace
```

## Loop Ladder

N17 should use a local loop ladder:

```text
G0:
  one-way boundary crossing trace

G1:
  internal update after external crossing

G2:
  outbound response changes external state

G3:
  changed external state feeds back into later internal state

G4:
  replay-stable closed loop

G5:
  challenge-stable closed loop under perturbation or flux

G6:
  shared-medium closed loop without basin merge

G7:
  claim-clean AP7 candidate, unsafe promotions blocked
```

G3 is the critical transition. A row below G3 is not closed-loop evidence.
G3 is the first admissible closed-loop evidence rung; G0/G1/G2 may support
diagnostics or active nulls, but they cannot support AP7.

Claim-boundary classification and evidence-rung advancement must remain
separate. Iteration 6 can classify the replay/control-clean MVP row at
artifact-level AP7 scope, but it must not imply G5 challenge stability or G6
shared-medium evidence. The evidence rung stays G4 until Iteration 6-A or
Iteration 6-B produces challenge-stability evidence.

Every candidate loop row must preserve monotonic phase ordering:

```text
t0 external pressure/crossing
t1 internal support update
t2 response-caused external change
t3 later internal support conditioned by changed external state
```

## Example Families

### Perturbation-Response-Recovery Loop

This is the first N17 core case.

```text
external perturbation crosses boundary
internal support shifts
bounded response or reclosure occurs
external perturbation field changes
later internal support depends on changed external state
```

Primary question:

```text
Does reclosure become part of a closed loop, or is it only a one-step recovery?
```

### Resource/Support Modulation Loop

This is an extension after the perturbation loop.

```text
external resource/support condition changes
internal support-relevant state updates
response changes access/path/pressure around the resource
modified resource condition changes later internal support
```

Primary question:

```text
Can external resource state and internal support state participate in a closed
trace without claiming semantic goal ownership?
```

### Shared-Medium Reciprocal Loop

This is the hardest extension and should not be the first tranche.

```text
basin A and basin B share a medium
external/shared-medium condition changes A
A response changes shared medium
changed shared medium affects B or later A
separability remains preserved
```

Primary question:

```text
Can a closed loop exist in a shared medium without merging basins or losing
boundary exclusivity?
```

## Staged Implementation Tranches

Mandatory contract work:

```text
Iteration 1 - source inventory and loop contract
Iteration 2 - schema / AP7 gate
```

MVP tranche:

```text
Iteration 3 - one-way crossing active null
Iteration 4 - perturbation-response-recovery loop
Iteration 5 - replay and order controls
Iteration 6 - claim boundary record
Iteration 6-A - bounded breach/flux G5 challenge-stability probe
Iteration 6-B - alternative target-band G5 challenge-stability probe
```

Extensions:

```text
Iteration 7 - resource/support modulation loop
Iteration 7-A - resource/support challenge-stability probe
Iteration 7-B - alternative resource/support G5 setup
Iteration 8 - shared-medium reciprocal loop
```

Closeout:

```text
Iteration 9 - comparative requirements and final AP7 classification
Iteration 10 - closeout and N18 handoff
```

N17-MVP can close a perturbation-response-recovery AP7 candidate with
Iterations 1-6-B plus final closeout if controls pass. Iterations 7-8 are
extensions and must be explicitly marked as included or deferred before final
closeout. Iteration 7-A is required if the resource/support family is included
as local G5 evidence rather than only a G4 extension. Iteration 7-B may add a
separate resource/support G5 setup, but it must not be treated as a refinement
or rescue of 7-A. Iteration 9 must compare 6-A and 6-B as bounded G5
alternatives rather than treating 6-B as a retuned repair of 6-A, and it must
separately classify any included 7-A/7-B evidence:

```text
extension_mode = extensions_deferred | extensions_included
included_iterations = [...]
deferred_iterations = [...]
```

## Common Loop Row Schema

Iteration 2 should freeze at least these row fields:

```text
row_id
loop_id
loop_family
loop_phase_count
monotonic_phase_ordering
phase_order_trace
case_id
source_experiment
source_iteration
source_artifact
source_report
source_sha256
source_report_sha256
source_role_classification
loop_ladder_rung
external_state_descriptor
internal_support_state_descriptor
boundary_side_assignments
boundary_crossing_trace
external_to_internal_trace
internal_response_trace
response_to_external_change_trace
external_feedback_to_internal_trace
loop_closure_evidence
feedback_removed_control
one_way_trace_control
post_hoc_loop_stitching_control
hidden_external_state_memory_control
hidden_internal_state_carryover_control
outbound_response_relabel_control
external_change_not_caused_by_response_control
feedback_order_inversion_control
resource_depletion_relabel_as_goal_pursuit_control
shared_medium_merge_relabel_as_reciprocal_loop_control
artifact_only_replay_status
snapshot_load_status
duplicate_replay_status
order_inversion_replay_status
budget_validity
dependency_trace
row_decision
closed_loop_claim_allowed
claim_ceiling
blocked_claims
final_ap7_supported
```

`row_decision` must use one of:

```text
supported
blocked
partial
rejected
not_applicable
```

`closed_loop_claim_allowed` must remain false unless AP7 gates, replay,
controls, budget validity, and claim-boundary checks pass.

## Required Controls

N17 inherits the N16 control discipline and adds loop-specific controls:

```text
feedback removed control
post-hoc loop stitching control
hidden external-state memory control
hidden internal-state carryover control
outbound response relabel control
external change not caused by internal response control
feedback order inversion control
one-way crossing relabel as closed-loop control
resource depletion relabel as goal pursuit control
shared-medium merge relabel as reciprocal loop control
semantic agency relabel control
semantic intention relabel control
semantic perception/action relabel control
native support relabel control
selfhood/personhood/identity relabel control
artifact-only replay
snapshot/load replay
duplicate replay
order-inversion replay
```

The most important control is:

```text
one-way crossing trace must not be promoted into closed loop
```

The paired causal ablation is:

```text
feedback_removed_control:
  preserve external -> internal and internal -> external traces
  remove or freeze the later external feedback state
  expected result: closed_loop_claim_allowed = false
```

## Replay Digest

Replay digest uses SHA-256 over canonical JSON with sorted keys and no
wall-clock timestamp. The digest scope must include:

```text
source artifact digests
selected source rows
loop policy
old best claim inputs
external_to_internal_trace
internal_response_trace
response_to_external_change_trace
external_feedback_to_internal_trace
loop_closure_evidence
feedback_removed_control
monotonic_phase_ordering
boundary_side_assignments
boundary_crossing_trace
case_id
loop_id
loop_family
loop_ladder_rung
row_decision
closed_loop_claim_allowed
budget surface
dependency trace
claim flags
```

`generated_at`, local absolute paths, and git working-tree metadata must be
excluded from the digest.

## Iterations

### Iteration 1. Source Inventory And Loop Contract

Collect source artifacts and classify which prior records can supply loop
phases:

```text
external-to-internal pressure or crossing
internal support update
internal response or reclosure
response-caused external change
later internal update conditioned by changed external state
claim boundary blockers
```

Expected artifacts:

```text
outputs/n17_loop_source_inventory.json
reports/n17_loop_source_inventory.md
scripts/build_n17_loop_source_inventory.py
```

Iteration 1 must not assign final `AP7`.

### Iteration 2. Loop Schema And AP7 Gate

Freeze loop row schema, loop ladder, trace fields, replay digest, budget
validity, controls, and AP7 gates. Iteration 2 must freeze that G3 is the first
admissible closed-loop rung and that G0-G2 cannot support AP7.

Expected artifacts:

```text
outputs/n17_loop_schema_v1.json
reports/n17_loop_schema_v1.md
scripts/build_n17_loop_schema_v1.py
scripts/validate_n17_loop_row.py
configs/n17_source_registry.json
configs/n17_loop_policy_v1.json
configs/n17_budget_limits_v1.json
configs/n17_control_variants_v1.json
configs/n17_replay_policy_v1.json
```

### Iteration 3. One-Way Crossing Active Null

Show that one-way boundary crossing and internal support response are not
closed-loop evidence unless changed external state feeds back into later
internal support.

Expected artifacts:

```text
outputs/n17_one_way_crossing_active_null.json
reports/n17_one_way_crossing_active_null.md
scripts/build_n17_one_way_crossing_active_null.py
```

### Iteration 4. Perturbation-Response-Recovery Loop

Run the minimal closed loop candidate.
The candidate must record the monotonic t0-t3 phase order and show that the
later internal state depends on the changed external state, not only that all
four trace fields exist.

Expected artifacts:

```text
outputs/n17_perturbation_response_recovery_loop.json
reports/n17_perturbation_response_recovery_loop.md
scripts/build_n17_perturbation_response_recovery_loop.py
```

### Iteration 5. Replay And Order Controls

Run loop replay, hidden-state, order-inversion, post-hoc stitching, and one-way
relabel controls, including the feedback-removed control.

Expected artifacts:

```text
outputs/n17_loop_replay_and_control_matrix.json
reports/n17_loop_replay_and_control_matrix.md
scripts/build_n17_loop_replay_and_control_matrix.py
```

### Iteration 6. Claim Boundary Record

Resolve whether the MVP perturbation-response-recovery loop can be classified
as an AP7 candidate without promoting unsafe claims. This is not the full
comparative AP7 classification unless Iterations 7-8 are explicitly included
and synthesized later.

This iteration does not advance the evidence rung beyond G4. It records
artifact-level MVP AP7 claim classification only; G5 challenge stability is
reserved for Iteration 6-A and the alternative Iteration 6-B probe.

Expected artifacts:

```text
outputs/n17_claim_boundary_record.json
reports/n17_claim_boundary_record.md
scripts/build_n17_claim_boundary_record.py
```

### Iteration 6-A. MVP Challenge-Stability Probe

Test whether the already replay/control-clean perturbation-response-recovery
loop remains a closed loop under controlled challenge variation. This is the
targeted G5 bridge before resource/support and shared-medium extensions.

Keep the loop family fixed:

```text
perturbation-response-recovery only
no resource/support modulation
no shared-medium reciprocal loop
```

Allowed challenge variations:

```text
perturbation magnitude
perturbation duration or window
boundary leakage pressure
external noise or flux pressure
feedback delay
partial feedback attenuation
```

Required outcome:

```text
same four ordered trace legs remain present
response-caused external change remains explicit
later internal dependence on changed external state remains explicit
G0-G2 relabels still fail closed
unsafe claims remain blocked
```

Expected artifacts:

```text
outputs/n17_mvp_challenge_stability_probe.json
reports/n17_mvp_challenge_stability_probe.md
scripts/build_n17_mvp_challenge_stability_probe.py
```

### Iteration 6-B. Alternative G5 Challenge Probe

Test an independent target-band-gated G5 configuration for the same MVP
perturbation-response-recovery loop. This is not a 6-A threshold refinement and
must not retune failed 6-A rows. It uses old-best source-backed support values
from N13/N09/N15 to ask whether a different configuration gives a stronger but
still bounded G5 claim.

Keep the loop family fixed:

```text
perturbation-response-recovery only
no resource/support modulation
no shared-medium reciprocal loop
```

Required outcome:

```text
source values pinned before row evaluation
target-band pass/fail rule frozen before row evaluation
mild attenuation and source-window delay may pass only inside target band
target-band crossing and response-budget exceedance fail closed
unsafe claims remain blocked
final AP7 remains blocked
```

Expected artifacts:

```text
outputs/n17_alternative_g5_challenge_probe.json
reports/n17_alternative_g5_challenge_probe.md
scripts/build_n17_alternative_g5_challenge_probe.py
```

### Iteration 7. Resource/Support Modulation Loop

Extend from perturbation-response-recovery to resource/support modulation.
This opens the first extension after the MVP loop. A supported row must not
relabel resource depletion or route/access modulation as semantic goal pursuit.
Because this is a new loop family, it does not inherit G5 challenge stability
from the MVP perturbation-response-recovery loop. Iteration 7 can support a G4
resource/support extension candidate; this family needs its own challenge probe
before any G5 resource/support claim.

Required outcome:

```text
G4 resource/support extension candidate at most
external resource/support condition change recorded
internal support-relevant update recorded
response-caused access/path/pressure change recorded
later internal support conditioned by modified resource state recorded
resource depletion as semantic goal pursuit blocked
native support, intention, agency, and selfhood blocked
shared-medium reciprocal loop remains unopened
```

Expected artifacts:

```text
outputs/n17_resource_support_modulation_loop.json
reports/n17_resource_support_modulation_loop.md
scripts/build_n17_resource_support_modulation_loop.py
```

### Iteration 7-A. Resource/Support Challenge-Stability Probe

Test local G5 challenge stability for the exact Iteration 7 resource/support
row. Keep the positive route_b row fixed; do not retune the route, source
values, claim ceiling, or unsafe-claim policy to make the extension pass.

Required outcome:

```text
fixed_source_row = route_b_resource_support_access_modulation
retune_allowed = false
same route_b identity preserved
all four trace legs remain substantive for supported rows
response-caused access/path/pressure change remains explicit
later internal support depends on the modified resource state
projected support remains above floor and inside target band for supported rows
resource/support attenuation, access delay, and route_b reduction envelope recorded
target-band crossing and response-budget exceedance fail closed
missing modified-resource feedback fails closed
resource label-only relabel fails closed
resource depletion as semantic goal pursuit fails closed
unsafe claims remain blocked
shared-medium reciprocal loop remains unopened
final AP7 remains blocked
```

Expected artifacts:

```text
outputs/n17_resource_support_challenge_stability_probe.json
reports/n17_resource_support_challenge_stability_probe.md
scripts/build_n17_resource_support_challenge_stability_probe.py
```

### Iteration 7-B. Alternative Resource/Support G5 Setup

Test a second resource/support G5 configuration that is not a 7-A refinement.
The setup must be selected before challenge evaluation and must use a different
source-backed construction from the fixed I7 route_b row used by 7-A.

Required outcome:

```text
alternative_setup_id frozen before row evaluation
iteration_7a thresholds not reused
not a rescue of failed 7-A controls
different source-current support anchor recorded
all four trace legs remain substantive for supported rows
response-caused access/path/pressure change remains explicit
later internal support depends on modified resource state
projected support remains above floor and inside target band for supported rows
support-floor crossing, target-band crossing, and budget exceedance fail closed
missing modified-resource feedback fails closed
resource label-only relabel fails closed
resource depletion as semantic goal pursuit fails closed
unsafe claims remain blocked
shared-medium reciprocal loop remains unopened
final AP7 remains blocked
```

Expected artifacts:

```text
outputs/n17_alternative_resource_support_g5_probe.json
reports/n17_alternative_resource_support_g5_probe.md
scripts/build_n17_alternative_resource_support_g5_probe.py
```

### Iteration 8. Shared-Medium Reciprocal Loop

Test whether shared-medium reciprocal closure can occur without basin merge or
loss of boundary exclusivity.

The shared-medium row must remain one-sided and artifact-level unless reverse
perspective replay is explicitly supplied later. A passing row may support a
local one-sided G6 shared-medium reciprocal candidate only if it keeps basin
separation, boundary exclusivity, leakage, merge pressure, internal support,
coherence, ordered trace dependence, and merge/leakage controls inside the
frozen B4/C5 policy. General shared-medium G6 robustness, reverse-perspective
shared-medium replay, symmetric multi-basin claims, and final AP7 remain
blocked unless later evidence explicitly supports them.

I8 must block:

```text
general shared-medium G6 robustness
reverse-perspective shared-medium replay
B2/C5 shared-medium pressure as enough for reciprocity
B4/C2 flux distribution relabel as C5 shared-medium separability
shared-medium leakage over ceiling
merge pressure over ceiling
neighbor leakage counted as intended basin retention
missing changed shared-medium feedback
shared-medium label-only relabel
one-sided B4/C5 promoted to symmetric/native multi-basin claims
final AP7
```

Expected artifacts:

```text
outputs/n17_shared_medium_reciprocal_loop.json
reports/n17_shared_medium_reciprocal_loop.md
scripts/build_n17_shared_medium_reciprocal_loop.py
```

### Iteration 8-A. Shared-Medium Reverse-Perspective Probe

Probe the open I8 limitation without relabeling I8 as general G6. The first
question is whether B4/C5 itself can supply reverse-perspective replay. If the
N16 source still records reverse basin perspective as deferred, that row must
remain blocked. The second question is whether another source-backed
shared-medium setup can strengthen the G6 candidate family.

8-A may use N07 11-B/12 as alternate dual-basin bounded-exchange evidence
because it records artifact-only replay, both basin supports surviving, basin
separability preserved, nonzero leakage bounded below threshold, exact budget,
and control replay. This strengthens shared-medium evidence only as an
alternate-source artifact-level candidate; it does not convert B4/C5 into
reverse replay and does not establish general G6.

8-A must block:

```text
B4/C5 reverse-perspective replay from N16-only evidence
general G6 from I8-only relabel
zero-leakage relabel
missing reservoir absorption
hidden reservoir routing
asymmetric absorber preference
support destroyed by allowed exchange
budget discontinuity
native identity relabel
final AP7
```

Expected artifacts:

```text
outputs/n17_shared_medium_reverse_perspective_probe.json
reports/n17_shared_medium_reverse_perspective_probe.md
scripts/build_n17_shared_medium_reverse_perspective_probe.py
```

### Iteration 8-B. B4/C5 Reverse-Perspective Replay Probe

Test the original N16 B4/C5 row specifically. This is narrower than 8-A:
8-A establishes alternate-source multi-basin evidence through N07, while 8-B
asks whether the original B4/C5 source itself can become perspective-paired.

8-B must distinguish:

```text
B4/C5 is multi-basin
B4/C5 is not automatically perspective-paired
neighbor basin as external side is not neighbor basin as reverse internal side
leakage/merge metrics are not reverse support/coherence metrics
label swap is not reverse replay
```

8-B may support B4/C5 reverse-perspective replay only if the source contains:

```text
reverse internal-side boundary assignment
reverse internal support floor measurement
reverse coherence margin measurement
reverse boundary edge
reverse response-caused shared-medium change
later reverse-internal state conditioned by changed shared medium
```

Expected artifacts:

```text
outputs/n17_b4c5_reverse_perspective_replay_probe.json
reports/n17_b4c5_reverse_perspective_replay_probe.md
scripts/build_n17_b4c5_reverse_perspective_replay_probe.py
```

### Iteration 8-C. Paired-Perspective Shared-Medium Probe

Construct a separate local paired-perspective shared-medium probe. This is not
a rescue of B4/C5 and not another alternate-source broadening pass. It must
record basin A perspective, basin B perspective, and a joint paired row in one
source-backed protocol.

8-C may use N07 dual-basin bounded-exchange evidence only if it records:

```text
basin A internal perspective trace
basin B internal perspective trace
same-protocol paired perspective requirement
response-caused shared-medium change
later support for both basins conditioned by changed shared medium
artifact-only replay and control replay
bounded leakage, separability, interference, exchange, and budget margins
```

8-C must preserve:

```text
B4/C5 reverse replay remains blocked by 8-B
one-sided I8 cannot be promoted to paired perspective
label swap is not paired replay
hidden reservoir routing remains blocked
merge/leakage cannot be counted as reciprocity
asymmetric perspective preference remains blocked
general shared-medium G6 remains blocked
symmetric native multi-basin replay remains blocked
final AP7 remains blocked
```

Expected artifacts:

```text
outputs/n17_paired_perspective_shared_medium_probe.json
reports/n17_paired_perspective_shared_medium_probe.md
scripts/build_n17_paired_perspective_shared_medium_probe.py
```

### Iteration 8-D. B4/C5-Derived Paired-Perspective Loop Probe

Test whether the original B4/C5 source can seed a new two-cycle paired
perspective protocol without relabeling the original B4/C5 artifact as
reverse-perspective replay.

8-D must distinguish:

```text
8-B = original B4/C5 reverse-perspective replay probe
8-C = independent/local paired-perspective shared-medium construction
8-D = B4/C5-derived two-cycle perspective-pairing probe
```

8-D may support a B4/C5-derived paired-perspective candidate only if the new
second cycle generates source-backed reverse-side evidence:

```text
cycle 1 forward B4/C5 A -> shared medium trace
cycle 2 changed shared medium becomes neighbor/B-side input
reverse internal-side state exists in cycle 2
reverse support/coherence metrics exist in cycle 2
reverse boundary-side assignment and boundary edge exist in cycle 2
reverse changed-medium feedback trace exists in cycle 2
leakage and merge pressure remain below ceiling
```

8-D must preserve:

```text
original B4/C5 row remains one-sided
8-C evidence cannot backfill B4/C5 reverse replay
label swap is not reverse perspective
neighbor leakage is not reverse retention
merge/leakage is not reciprocity
hidden shared-medium routing remains blocked
general shared-medium G6 remains blocked
final AP7 remains blocked
```

Expected artifacts:

```text
outputs/n17_b4c5_derived_paired_perspective_probe.json
reports/n17_b4c5_derived_paired_perspective_probe.md
scripts/build_n17_b4c5_derived_paired_perspective_probe.py
```

### Iteration 9. Comparative Requirements And AP7 Classification

Synthesize loop requirements, controls, replay, and claim classification.
Record whether Iterations 7-8-D are included or deferred before comparative
AP7 classification.

Resource/support comparison must preserve the 7-A/7-B distinction:

```text
7-A = local G5 for the original fixed I7 route_b resource/support loop
7-B = alternative local G5 under a lower-margin support bridge
7-B does not replace 7-A
7-B does not widen the 7-A envelope

resource/support closure requirement:
  supported_by: I7, I7-A, I7-B
  strongest_envelope: I7-A
  alternative_low_margin_support: I7-B
  blocked_by: support-floor crossing, target-band crossing, budget exceedance,
              missing feedback, label-only relabel, goal-pursuit relabel
```

Expected artifacts:

```text
outputs/n17_closed_loop_requirements_matrix.json
reports/n17_closed_loop_requirements_matrix.md
scripts/build_n17_closed_loop_requirements_matrix.py
```

### Iteration 10. Closeout And N18 Handoff

Freeze final supported AP level if warranted, record final blockers, and
handoff to N18 long-horizon closure stress test.

Expected artifacts:

```text
outputs/n17_closeout_and_handoff.json
reports/n17_closeout_and_handoff.md
scripts/build_n17_closeout_and_handoff.py
```

## Claim Boundary

```text
closed boundary engagement loop != agency
closed boundary engagement loop != intention
closed boundary engagement loop != semantic action or perception
closed boundary engagement loop != semantic goal ownership
closed boundary engagement loop != selfhood or identity acceptance
artifact-level AP7 != native support
N17 AP7 != organism, life, biological behavior, fully native integration, or unrestricted agency
```
