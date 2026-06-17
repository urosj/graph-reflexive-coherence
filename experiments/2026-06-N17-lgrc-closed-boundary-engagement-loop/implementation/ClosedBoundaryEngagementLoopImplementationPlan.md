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
```

Extensions:

```text
Iteration 7 - resource/support modulation loop
Iteration 8 - shared-medium reciprocal loop
```

Closeout:

```text
Iteration 9 - comparative requirements and final AP7 classification
Iteration 10 - closeout and N18 handoff
```

N17-MVP can close a perturbation-response-recovery AP7 candidate with
Iterations 1-6 plus final closeout if controls pass. Iterations 7-8 are
extensions and must be explicitly marked as included or deferred before final
closeout:

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

Expected artifacts:

```text
outputs/n17_claim_boundary_record.json
reports/n17_claim_boundary_record.md
scripts/build_n17_claim_boundary_record.py
```

### Iteration 7. Resource/Support Modulation Loop

Extend from perturbation-response-recovery to resource/support modulation.

Expected artifacts:

```text
outputs/n17_resource_support_modulation_loop.json
reports/n17_resource_support_modulation_loop.md
scripts/build_n17_resource_support_modulation_loop.py
```

### Iteration 8. Shared-Medium Reciprocal Loop

Test whether shared-medium reciprocal closure can occur without basin merge or
loss of boundary exclusivity.

Expected artifacts:

```text
outputs/n17_shared_medium_reciprocal_loop.json
reports/n17_shared_medium_reciprocal_loop.md
scripts/build_n17_shared_medium_reciprocal_loop.py
```

### Iteration 9. Comparative Requirements And AP7 Classification

Synthesize loop requirements, controls, replay, and claim classification.
Record whether Iterations 7-8 are included or deferred before comparative AP7
classification.

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
