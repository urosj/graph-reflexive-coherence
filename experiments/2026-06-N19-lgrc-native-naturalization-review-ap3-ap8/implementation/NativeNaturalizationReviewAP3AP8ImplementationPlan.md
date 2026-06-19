# N19 Native Naturalization Review AP3-AP8 Implementation Plan

## Goal

Classify the N13-N18 AP3-AP8 agency-prerequisite stack using the N12 native
naturalization ladder and Phase 8 readiness discipline.

N19 should answer:

```text
Which AP3-AP8 mechanisms are only artifact scaffolds?
Which are native contract candidates?
Which are Phase 8-ready native policy candidates?
Which are implementation-gap blockers?
Which are theory-sensitive blockers?
Which unsafe promotions must remain rejected?
```

N19 is a review/classification experiment. It does not implement native
producer code and does not open Phase 8.

## Non-Goals

N19 must not:

```text
create AP9
open Phase 8
open native support
modify src/*
claim agency
claim semantic action or semantic perception
claim semantic goal ownership
claim selfhood
claim identity acceptance
claim organism/life behavior
claim fully native agentic-like integration
claim unrestricted autonomy
```

## Method

N19 uses N12 as the method template:

```text
source inventory
NAT ladder replay
schema freeze
candidate classification rows
Phase 8 readiness matrix
claim-boundary controls
closeout and handoff
```

The N12 ladder is reused unchanged:

```text
NAT0 = producer-only artifact scaffold
NAT1 = source-backed producer pattern
NAT2 = replayable producer pattern with controls
NAT3 = native contract candidate
NAT4 = Phase 8-ready native policy candidate, no native implementation
NAT5 = native implementation exists but is not integrated
NAT6 = native implementation validates within composition replay
```

N19 may classify rows up to `NAT4`. `NAT5` and `NAT6` are out of scope.

`phase8_ready` is derived:

```text
phase8_ready = true only when nat_level = NAT4
```

It is not native support.

## Source Scope

Required source tranche:

```text
N12 native naturalization and Phase 8 readiness records
N13 AP3 closeout and support/regulation artifacts
N14 AP4 closeout and consequence/selection artifacts
N15 AP5 closeout and proxy/target artifacts
N16 AP6 closeout and boundary artifacts
N17 AP7 closeout and loop artifacts
N18 AP8 closeout, control/classification, and stress artifacts
```

N19 should preserve each source claim ceiling. A stronger N19 native-readiness
classification cannot make a source experiment stronger than its own closeout.

## Candidate Row Schema

Each candidate row should include:

```text
row_id
source_experiment
source_iteration_or_closeout
source_artifacts
source_reports
source_sha256
source_output_digest
source_final_supported_ap_level
source_final_claim_ceiling
artifact_supported
artifact_claim_scope
native_question
primary_disposition
nat_level
phase8_ready
phase8_ready_derivation
native_policy_or_telemetry_surface_name
runtime_visible_inputs
native_state_needed
state_mutation_owner
record_schema_sketch
default_off_flags
enabled_validated_supported_separation
budget_surface
telemetry_requirements
snapshot_replay_requirements
negative_controls
non_rc_quantity_audit
minimal_producer_code_needed
implementation_boundary
claim_flags
blocked_claims
phase8_opened
native_support_opened
src_diff_empty
row_decision
```

Every row gets exactly one `primary_disposition`:

```text
scaffold
native_contract_candidate
phase8_ready_native_policy_candidate
implementation_gap_blocker
theory_sensitive_blocker
unsafe_relabel_rejected
not_applicable
```

Rows may also have secondary tags, but the primary disposition must be
unambiguous.

`row_decision` is frozen as:

```text
supported
partial
blocked
rejected
not_applicable
```

## NAT4 Readiness Gates

For `nat_level = NAT4`, every gate must be explicit:

```text
native policy or telemetry surface name present
record schema sketch present
default-off flags present
enabled / validated / supported fields separated
runtime-visible inputs source-backed
state mutation owner specified
budget surface specified
telemetry requirements specified
snapshot/replay requirements specified
negative controls specified
non-RC quantity audit passes
claim flags forced false
phase8_opened = false
native_support_opened = false
src_diff_empty = true
```

If any gate is missing, the row cannot reach NAT4.

## Initial Candidate Families

N13 AP3 support-seeking regulation:

```text
candidate question:
  Can support-margin measurement and bounded response magnitude become a
  native regulation policy surface?

likely native surface:
  native_support_margin_and_response_magnitude_policy

high-risk blockers:
  native support relabel
  self-maintenance relabel as selfhood
  support-seeking relabel as semantic goal ownership
```

N14 AP4 consequence-sensitive route selection:

```text
candidate question:
  Can route consequence records and route-conditioned selection context become
  a native selection telemetry or policy surface?

likely native surface:
  native_route_consequence_selection_telemetry

high-risk blockers:
  constructed followout relabel as observed upstream support
  selection relabel as semantic choice or intention
```

N15 AP5 endogenous proxy formation:

```text
candidate question:
  Can source-current target/proxy derivation become a native proxy policy
  surface without semantic goal ownership?

likely native surface:
  native_proxy_derivation_policy

high-risk blockers:
  generated target relabel as semantic goal
  readiness-only context relabel as native support
```

N16 AP6 self/environment boundary:

```text
candidate question:
  Can boundary side assignments, leakage, separability, and shared-medium
  metrics become native boundary telemetry surfaces?

likely native surface:
  native_boundary_side_state_and_separability_telemetry

high-risk blockers:
  boundary relabel as selfhood
  shared-medium separability relabel as native multi-basin selfhood
```

N17 AP7 closed boundary engagement loop:

```text
candidate question:
  Can ordered loop trace legs and replay controls become native closed-loop
  telemetry contracts?

likely native surface:
  native_ordered_loop_trace_telemetry

high-risk blockers:
  closed loop relabel as agency
  response relabel as semantic action
  external feedback relabel as semantic perception
```

N18 AP8 limited long-horizon closure:

```text
candidate question:
  Can horizon, budget, replay, and cross-axis continuity constraints become
  native long-horizon validation contracts?

likely native surface:
  native_horizon_budget_replay_validation_contract

high-risk blockers:
  limited h4/L5 result relabel as general AP8
  artifact replay relabel as native support
  Phase 8 relabel without implementation
```

These are starting questions, not final classifications.

## Iteration Plan

### Iteration 1. Source Inventory And N12 Ladder Replay

Build a source inventory over N12-N18 and freeze that N19 consumes N12 as the
classification method, not as native support.

Expected artifacts:

```text
outputs/n19_ap3_ap8_source_inventory.json
reports/n19_ap3_ap8_source_inventory.md
scripts/build_n19_ap3_ap8_source_inventory.py
```

Acceptance:

```text
all required N13-N18 closeouts found
N12 NAT ladder replayed
source digests recorded
source claim ceilings preserved
direct native support evidence absent unless source-backed
phase8_opened = false
native_support_opened = false
```

### Iteration 2. Schema And Control Freeze

Freeze the N19 row schema, NAT ladder fields, disposition enum, NAT4 gates,
claim flags, and fail-closed controls before candidate classification.

Expected artifacts:

```text
outputs/n19_naturalization_schema_v1.json
reports/n19_naturalization_schema_v1.md
scripts/build_n19_naturalization_schema_v1.py
```

Acceptance:

```text
primary_disposition enum frozen
nat_level enum frozen
phase8_ready derivation frozen
claim flags forced false
unsafe relabel controls defined
src_diff_empty required
no candidate rows classified yet
```

### Iteration 3. AP3-AP5 Lower-Stack Candidate Classification

Classify N13 AP3, N14 AP4, and N15 AP5 native-readiness candidates and blockers.

Expected output:

```text
support/regulation native-readiness rows
consequence/selection native-readiness rows
proxy/target native-readiness rows
```

Acceptance:

```text
no selfhood or goal ownership relabel
constructed followout not promoted to observed native support
N12 readiness-only context not relabeled as native support
candidate NAT levels justified gate by gate
```

### Iteration 4. AP6 Boundary Native-Readiness Classification

Classify N16 AP6 boundary, leakage, separability, side assignment, and
shared-medium geometry/telemetry candidates.

Acceptance:

```text
boundary telemetry candidates distinguished from selfhood
B4/C5 shared-medium evidence remains artifact-level unless native telemetry is specified
original B4/C5 one-sidedness is not backfilled by later derived evidence
native multi-basin selfhood remains blocked
```

### Iteration 5. AP7 Loop Native-Readiness Classification

Classify N17 AP7 ordered loop trace, replay, controls, resource/support, and
shared-medium loop contracts.

Acceptance:

```text
G3/G5/G6 trace evidence not relabeled as agency
response not relabeled as semantic action
feedback not relabeled as semantic perception
loop telemetry requirements explicit
one-way crossing relabel remains rejected
```

### Iteration 6. AP8 Horizon And Budget Native-Readiness Classification

Classify N18 AP8 limited h4/L5 horizon, budget, cross-axis continuity, replay,
and stress controls as native validation contract candidates or blockers.

Acceptance:

```text
limited h4/L5 result not widened to general AP8
h8/h16 remain blocked
boundary_to_loop_feedback bottleneck preserved
artifact replay not relabeled as native support
Phase 8 remains unopened
```

### Iteration 7. Phase 8 Readiness Matrix

Synthesize all candidate rows into a readiness matrix.

Expected artifacts:

```text
outputs/n19_candidate_classification_matrix.json
outputs/n19_phase8_readiness_matrix.json
reports/n19_candidate_classification_matrix.md
reports/n19_phase8_readiness_matrix.md
scripts/build_n19_candidate_classification_matrix.py
scripts/build_n19_phase8_readiness_matrix.py
```

Acceptance:

```text
each candidate has one primary disposition
NAT4 rows, if any, satisfy every NAT4 gate
blocked rows have distinct blockers
minimal producer code needed is recorded for implementation-gap rows
no native implementation claim is made
```

### Iteration 8. Closeout And Handoff

Close N19 as a native-readiness review and hand off any Phase 8 implementation
tasks explicitly.

Expected artifacts:

```text
outputs/n19_closeout_and_handoff.json
reports/n19_closeout_and_handoff.md
scripts/build_n19_closeout_and_handoff.py
```

Acceptance:

```text
final_claim_ceiling = artifact_level_phase8_readiness_review_for_ap3_ap8
phase8_opened = false
native_support_opened = false
src_diff_empty = true
unsafe claims blocked
future Phase 8 tasks named without being implemented
```

## Controls

Required fail-closed controls:

```text
artifact replay relabeled as native support
NAT3 relabeled as NAT4
NAT4 relabeled as native implementation
Phase 8 opened by classification flag
native support flag written directly
AP evidence relabeled as agency
response relabeled as semantic action
feedback relabeled as semantic perception
proxy relabeled as semantic goal
boundary relabeled as selfhood
identity acceptance relabel
organism/life relabel
limited h4/L5 relabeled as general AP8
derived B4/C5 evidence backfilled into original B4/C5
non-RC quantity inserted to make candidate pass
src diff non-empty
absolute path in generated records
```

## Closeout Target

The strongest acceptable N19 closeout is:

```text
status = n19_closed
final_claim_ceiling = artifact_level_phase8_readiness_review_for_ap3_ap8
phase8_opened = false
native_support_opened = false
native_supported_flags = false
ap9_opened = false
src_diff_empty = true
```
