# N15 Endogenous Proxy Formation Implementation Plan

## Purpose

N15 tests whether proxy or target conditions can be generated from
runtime-visible support, memory, regulation, or support/identity-condition
state rather than supplied as experiment-declared targets.

N15 targets `AP5` at most:

```text
AP5 = endogenous proxy candidate
```

The expected final ceiling, if supported, is:

```text
artifact_level_ap5_endogenous_proxy_formation_candidate
```

This is not semantic goal ownership, intention, semantic choice, agency,
identity acceptance, selfhood, personhood, biological behavior, native support,
or fully native agentic-like integration.

## Source Rules

Iteration 1 must pin source artifacts before mechanism interpretation. Primary
source lanes are:

```text
N08 route memory / affordance evidence
N09 bounded response regulation evidence
N12 NAT4 readiness records
N13 AP3 support-seeking regulation closeout and support candidate
N14 AP4 consequence-sensitive route selection closeout and constructed
followout record
```

N15 may consume N14 only as artifact-level AP4 consequence-sensitive route
selection evidence. N14 constructed support/regulation followout must remain
distinguished from upstream observed N09/N13 route-conditioned evidence.

N15 may consume N13 only as artifact-level AP3 support-seeking regulation
evidence. N15 may consume N12 NAT4 records only as Phase 8 readiness evidence,
not native support.

## Evidence Strategy

Iteration 1 should first check whether historic artifacts directly support
runtime-derived proxy or target formation. If direct support exists, use it
only as source-backed, claim-clean evidence and still run the N15 controls.

The strongest N15 proof path is a constructed candidate built from the old best
closed claims rather than from a new declared target fixture:

```text
N13 AP3 support-seeking regulation
N14 AP4 consequence-sensitive route selection
N08 route memory context
N09 bounded regulation context
N12 NAT4 readiness records as readiness-only context
```

The construction must preserve each source experiment's claim boundary. It may
combine old best claims to form an AP5 candidate, but it must not promote N13
into selfhood or identity acceptance, N14 into intention or semantic goal
ownership, or N12 into native support.

## Arc Of Becoming Method

Use the Arc of Becoming method sources as the operating method for N15. They
are referenced by title and portable filename only because they live outside
this repository:

```text
Classification of Becoming
    2026-05-ClassificationOfBecoming.md

Interrogation of Becoming
    2026-05-InterrogationofBecoming.md

Naturalization of Becoming
    2026-05-NaturalizationOfBecoming.md

Cultivation of Becoming
    2026-05-CultivationOfBecoming.md
```

N15 applies them as follows:

```text
Classification:
  first classify what the prior artifacts and constructed candidate actually
  express. Do not promote local observation tags into AP5 unless they are
  reusable or generative and pass the AP5 gate.

Interrogation:
  treat derivation variants, controls, and perturbations as bounded questions.
  A generated target is a question-answer record about proxy formation, not
  proof of semantic goal ownership.

Naturalization:
  keep probe-supported, constructed, readiness-only, and native-support
  evidence separate. AP5 can close artifact-level while native support remains
  unopened.

Cultivation:
  cultivate the function of endogenous target formation from prior best
  claims. Do not optimize a local target proxy merely because it is measurable.
```

## Pre-Implementation Contract

### Terminology

Use `runtime-visible artifact state` for state captured in runtime artifacts
before proxy formation and available for replay. This is an artifact visibility
claim, not a semantic claim that the system understands or owns the state.

Use `support/identity-condition descriptor` for support-relevant condition
descriptors carried forward from prior artifacts. This is not identity
acceptance.

### AP4 To AP5 Bridge

N14 AP4 supplies source-backed consequence-sensitive selection:

```text
route/action selection depends on downstream support, memory, or regulation
effect records
```

N15 AP5 requires an additional boundary crossing:

```text
a target/proxy condition is generated before downstream use from
source-current runtime-visible artifact state
```

AP5 is not a relabel of AP4. N15 uses AP4 as the strongest available
construction substrate, but the AP5 candidate must add pre-use target
formation with its own derivation trace, drift bounds, budget validity, and
controls. AP5 could be tested without AP4 in principle, but this experiment's
strongest path uses N14 AP4 plus N13 AP3 and supporting N08/N09 context.

### Old-Best-Claims Composition

The old-best-claims construction operator is trace-preserving composition:

```text
N13 AP3 -> support-seeking regulation axis
N14 AP4 -> consequence-sensitive selection axis
N08 -> memory/context axis
N09 -> bounded-regulation axis
N12 NAT4 -> readiness-only context
```

Composition rules:

```text
1. source rows are consumed only at their closed claim ceilings
2. every source contribution is recorded in `old_best_claim_inputs`
3. every derived target field has a dependency-trace entry
4. N12 readiness records cannot contribute native-support evidence
5. constructed N14 followout remains constructed followout, not upstream
   observed route-conditioned support/regulation
6. the result can be at most `AP5_candidate` until controls and replay pass
```

### Endogenous Derivation Policy

`endogenous_derivation_policy` is a deterministic, serialized transformation
from source-current runtime-visible artifact state to a target condition.

The policy must contain:

```text
policy_id
policy_version
input_fields
input_normalization
ordinal_codebook_or_numeric_scale
composition_weights_or_rule_order
target_center_rule
target_tolerance_rule
drift_bound_rule
clamp_rule
budget_rule
missing_input_policy
stale_input_policy
digest_scope
```

Default Iteration 2 candidate policy:

```text
1. normalize support, memory, and regulation descriptors to a serialized
   ordinal or numeric state vector
2. derive `target_center` from the current support baseline plus bounded
   adjustments from memory, regulation, and AP4 consequence context
3. derive `target_tolerance` from the source support margin and bounded
   regulation confidence
4. clamp `target_center` and `target_tolerance` by the bounded drift policy
5. fail closed on missing, stale, externally injected, or untraceable inputs
```

If a numeric source scale is unavailable, Iteration 2 must define an explicit
ordinal codebook before Iteration 3 can generate a target.

### Target Band Contract

Target formation must emit:

```text
target_condition_surface
target_center
target_tolerance
target_band = [target_center - target_tolerance,
               target_center + target_tolerance]
```

For ordinal targets, `target_band` is the allowed ordinal category or adjacent
category set defined by the codebook. `target_tolerance` is then an ordinal
radius rather than a numeric width.

### Dependency Trace Format

`dependency_trace` is a field-level provenance list. Each entry must include:

```text
target_field
source_row_id
source_artifact
source_digest
source_field
transform_id
transform_parameters
claim_ceiling_of_source
```

A trace is incomplete if any emitted target field lacks a source row,
transform, or claim ceiling.

### Bounded Drift Policy

Iteration 2 must freeze concrete drift bounds before candidate generation.
The default policy to validate or replace is:

```text
numeric target_center:
    max absolute update = 10 percent of the declared source scale per
    derivation step

numeric target_tolerance:
    max absolute update = 5 percent of the declared source scale per
    derivation step

ordinal target:
    max update = one adjacent ordinal category per derivation step

clamp:
    any larger update is clamped and marked `drift_clamped = true`;
    unbounded or unconfigured drift fails closed
```

### Budget Cost Surface

Budget is artifact-local and must be checked before target use. The cost
surface must record:

```text
source_row_count
transform_count
serialized_input_bytes
serialized_output_bytes
replay_count
validation_count
```

Iteration 2 must freeze validity limits for those units. A row is
budget-invalid if any limit is missing, evaluated after target use, or
exceeded without an explicit rejection record.

### Replay Digest

Replay digest uses SHA-256 over canonical JSON with sorted keys and no
wall-clock timestamp. The digest scope must include:

```text
source artifact digests
selected source rows
endogenous_derivation_policy
old_best_claim_inputs
runtime state vector
drift policy
budget surface
dependency trace
target condition
claim flags
```

`generated_at`, local filesystem paths, and git working-tree metadata must be
excluded from the digest.

### Output And Validation Shape

Iteration outputs should use a top-level JSON object:

```text
experiment
iteration
artifact_id
acceptance_state
source_artifacts
schema_version
rows
controls
checks
claim_flags
output_digest
errors
```

Schema validation may be implemented with a project-local Python validator or
JSON Schema, but the validator must check required fields, claim flags, control
outcomes, source digest presence, and digest reproducibility.

### Error Handling

All scripts should fail closed with distinct blocker labels for:

```text
missing source artifact
source digest mismatch
stale source state
missing derivation policy
missing dependency trace
budget invalid before target use
non-deterministic derivation
control unexpectedly passes
unsafe claim flag true
absolute path recorded in output
```

## AP5 Gate

Assign `AP5` only when all of the following canonical gate IDs are present and
validated:

```text
runtime_visible_source_state_inventory_present
source_artifact_report_digest_for_each_state_input
source_current_freshness_record_present
support_state_descriptor_present
memory_state_descriptor_or_explicit_absence_present
regulation_state_descriptor_or_explicit_absence_present
support_identity_condition_descriptor_or_explicit_absence_present
declared_external_proxy_absent
externally_injected_target_rejection_policy_present
hidden_target_derivation_rejection_policy_present
hidden_target_derivation_control_fails_closed
endogenous_derivation_policy_present
target_condition_generated_before_downstream_use
target_condition_surface_present
target_center_present
target_band_or_threshold_present
target_tolerance_present
bounded_drift_policy_present
drift_clamp_policy_present
budget_cost_surface_present
budget_units_present
budget_validity_policy_present
dependency_trace_from_source_state_to_target_condition_present
idempotency_digest_plan_present
generated_target_consumable_by_rank_or_regulation_without_goal_ownership_relabel
artifact_only_replay_requirement_present
snapshot_load_equivalence_requirement_present
order_inversion_replay_requirement_present
post_hoc_proxy_formation_rejection_policy_present
negative_controls_present
compatibility_checks_present
claim_flags_forced_false
src_diff_empty_true
native_supported_flags_false
phase8_opened_false
fully_native_integration_opened_false
```

`AP5` is a final closeout level only after controls, bounded-drift replay, and
claim-boundary classification pass. Earlier iterations may use
`provisional_ap_level`.

## Frozen Proxy Formation Row Schema

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
source_role_classification
evidence_strategy
old_best_claim_inputs
direct_historic_support_status
arc_method_mapping
runtime_state_surface_id
state_source_window
source_current
support_state_descriptor
identity_condition_descriptor
memory_state_descriptor
regulation_state_descriptor
declared_proxy_absent
external_target_input_absent
endogenous_derivation_policy
target_condition_generated_at
target_condition_surface
target_band
target_tolerance
target_center
drift_bound
drift_update_rule
drift_clamp_policy
dependency_trace
budget_cost_surface
budget_units
budget_validity
replay_digest_inputs
replay_digest_algorithm
idempotency_digest_plan
fully_native_integration_opened
artifact_only_replay_status
snapshot_load_status
order_inversion_replay_status
externally_injected_target_control
hidden_target_derivation_control
post_hoc_proxy_formation_control
unbounded_target_drift_control
budget_surface_ambiguity_control
semantic_goal_ownership_relabel_control
identity_acceptance_relabel_control
native_support_relabel_control
provisional_ap_level
provisional_claim_ceiling
blocked_claims
missing_gates
```

## Iterations

### Iteration 1. Baseline And Proxy Source Inventory

Collect source artifacts and classify which prior records can supply:

```text
runtime-visible support state
runtime-visible memory state
runtime-visible regulation state
support/identity-condition descriptors
declared external proxy baselines
constructed N14 followout context
Phase 8 readiness records
claim boundary blockers
```

Source inventory must record both:

```text
direct historic support status
old-best-claims construction inputs
Arc of Becoming method mapping
```

Expected artifacts:

```text
outputs/n15_proxy_source_inventory.json
reports/n15_proxy_source_inventory.md
scripts/build_n15_proxy_source_inventory.py
```

Result:

```text
Status: passed.
Artifact: outputs/n15_proxy_source_inventory.json
Report: reports/n15_proxy_source_inventory.md
Acceptance state: accepted_proxy_source_inventory_only_no_ap5
Output digest: 66ebd8bf90e31d3aa1a59d9de46e85bf581f44c3c70e5cf1a3a76d8f535aa4c1
```

Iteration 1 classified nine source rows: one direct historic N13
support-derived target candidate at AP2 scope, five old-best-claims
construction inputs, one constructed N14 followout context row, one N14 claim
boundary row, and one N12 readiness-only row. It records that no direct
historic AP5 support exists; the strongest proof path remains construction
from N13 AP3, N14 AP4, N08 memory context, N09 bounded regulation context, and
N12 readiness-only context.

Interpretation:

```text
N15 has sufficient pinned source coverage to proceed to schema freeze. It does
not yet freeze a derivation policy, generate a target condition, run controls,
open Phase 8, open native support, or assign final AP5.
```

Iteration 1 must not assign final `AP5`.

### Iteration 2. Proxy Formation Schema And AP5 Gate

Freeze the N15 schema:

```text
runtime-visible source state fields
freshness and source-window fields
support, memory, regulation, and support/identity-condition descriptor fields
external proxy absence fields
endogenous derivation policy fields
target condition and target band fields
bounded drift fields
budget validity fields
dependency trace fields
old-best-claims composition fields
direct historic support fields
replay digest fields
top-level JSON output shape
schema validation and fail-closed error labels
artifact-only replay, snapshot/load, and order-inversion replay fields
negative controls
claim flags
AP5 acceptance gates
```

Expected artifacts:

```text
outputs/n15_proxy_formation_schema_v1.json
reports/n15_proxy_formation_schema_v1.md
scripts/build_n15_proxy_formation_schema_v1.py
scripts/validate_n15_row.py
configs/n15_source_registry.json
configs/n15_derivation_policy_v1.json
configs/n15_budget_limits_v1.json
configs/n15_control_variants_v1.json
configs/n15_replay_policy_v1.json
```

Iteration 2 freezes the contract only. Row validation and AP5 support start in
later iterations.

Result:

```text
Status: passed.
Artifact: outputs/n15_proxy_formation_schema_v1.json
Report: reports/n15_proxy_formation_schema_v1.md
Acceptance state: accepted_schema_freeze_no_row_validation
Output digest: 3894554145fe84a7f594983ead562442cda686fd53d6b240164626b578f2ee67
```

Iteration 2 freezes 55 row-schema fields, 36 AP5 required gates, 12 negative
control requirements, 5 materialized config-file contracts, and 10 fail-closed
error labels. It also freezes the deterministic endogenous derivation policy,
old-best-claims composition operator, bounded drift policy, budget limits,
dependency trace format, replay digest scope, perturbation defaults, hypothesis
decision rubric, split runtime/schema-freeze top-level output contracts, and a
project-local row validator.

Interpretation:

```text
N15 now has a frozen contract for constructing and testing a runtime-derived
target candidate. The strongest path remains N13 AP3 + N14 AP4 + N08/N09/N12
context under trace-preserving old-best-claims composition. Iteration 2 does
not validate a candidate row, generate a target, run controls, open Phase 8,
open native support, or assign final AP5.
```

### Iteration 3. Runtime-Derived Target Candidate

Build a candidate target condition from source-current runtime-visible state:

```text
select source-current state inputs
prefer old-best-claims construction unless direct historic AP5 support is
stronger and claim-clean
derive target band or threshold using the frozen policy
record dependency trace
record target formation timing before downstream use
record budget validity before target use
record replay digest inputs
record target consumability by rank or regulation behavior without semantic
goal ownership relabel
classify provisional AP level
```

Expected artifacts:

```text
outputs/n15_runtime_derived_target_candidate.json
reports/n15_runtime_derived_target_candidate.md
scripts/build_n15_runtime_derived_target_candidate.py
```

Iteration 3 may support only a provisional candidate pending contrast and
controls.

Result:

```text
Status: passed.
Artifact: outputs/n15_runtime_derived_target_candidate.json
Report: reports/n15_runtime_derived_target_candidate.md
Acceptance state: accepted_runtime_derived_target_candidate_with_bridge_pending_controls
Output digest: 7fcb73f4b70fdd4f4aadaa9e931040f8299669ca1598c9a1391c560637a26fbc
```

Iteration 3 follows the stronger construction path from N13 AP3, N14 AP4,
N08, N09, and N12 readiness-only context. It records the direct historic N13
AP2 target evidence as a gap record rather than promoting it to AP5. The
generated target center is `0.887594607287`, tolerance is `0.07`, and target
band is `[0.817594607287, 0.957594607287]`.

Bridge interpretation:

```text
target condition exists != target condition functions as AP5-relevant proxy input
```

The bridge probe consumes the generated target band before ranking regulation
candidates: the bounded N13 support response enters the generated band at
`0.85`, while no-response remains outside the band at `0.729865182184`. This
supports only a provisional AP5 candidate pending Iterations 4-7.

The generated report records the full `Iteration 3 Explanation` section for
the composition, inputs, bridge result, and claim boundary.

Post-review closure records the I3 top-level output contract, aligns the
idempotency digest scope with the replay inputs, includes the constructed N14
followout in the candidate path, traces context rows and bounded bridge
response fields, emits the I2 validator check names, and records the control
value convention plus the Iteration 6 replay design note.

### Iteration 4. External Proxy Contrast Matrix

Compare runtime-derived target formation against declared-proxy baselines:

```text
declared target fixture contrast
externally injected target rejection
hidden target derivation rejection
post-hoc proxy formation rejection
source-current runtime derivation replay
budget-validity-before-use check
```

Expected artifacts:

```text
outputs/n15_external_proxy_contrast_matrix.json
reports/n15_external_proxy_contrast_matrix.md
scripts/build_n15_external_proxy_contrast_matrix.py
```

Iteration 4 should establish whether the candidate is distinguishable from
declared proxy regulation.

Result:

```text
Status: passed.
Artifact: outputs/n15_external_proxy_contrast_matrix.json
Report: reports/n15_external_proxy_contrast_matrix.md
Acceptance state: accepted_external_proxy_contrast_matrix_pending_adversarial_controls_replay_and_claim_boundary
Output digest: bc97c3125ffdc83c0e97a02c7a6534fadfb95e0141f7082af3d1439c974fea59
```

Iteration 4 establishes that the I3 candidate is distinguishable from declared
proxy regulation at artifact level. The same-band declared fixture is blocked
by fixture provenance, externally injected target variants are blocked, hidden
target derivation variants are blocked, and post-hoc proxy formation variants
are blocked. The source-current derivation replays from the serialized I3
runtime state vector, and the I3 budget validity record is confirmed before
target use.

The generated report records the full `Iteration 4 Explanation` section for
the contrast inputs, contrast rule, same-band fixture result, end result, and
claim boundary.

Scope boundary:

```text
I4 contrast clean != final AP5
I4 budget-before-use check != full I5 budget ambiguity control
I4 source-current replay != full I6 artifact-only/snapshot/order replay
```

### Iteration 5. Adversarial Control Matrix

Execute the required negative controls:

```text
externally injected target blocked
hidden target derivation blocked
semantic goal ownership relabel blocked
post-hoc proxy formation blocked
unbounded target drift blocked
budget-surface ambiguity blocked
identity acceptance relabel blocked
native support relabel blocked
fixture-label proxy blocked
stale source state blocked
missing source state blocked
dependency trace omission blocked
```

Expected artifacts:

```text
outputs/n15_proxy_control_matrix.json
reports/n15_proxy_control_matrix.md
scripts/build_n15_proxy_control_matrix.py
```

Iteration 5 must produce distinct blockers for negative controls.

Result:

```text
Status: passed.
Artifact: outputs/n15_proxy_control_matrix.json
Report: reports/n15_proxy_control_matrix.md
Acceptance state: accepted_proxy_control_matrix_pending_bounded_drift_replay_and_claim_boundary
Output digest: 251116879e10182729ace752d2f684acf6878a2d2d3db74c7f39bef1a7a76a7f
```

Iteration 5 executes all twelve frozen adversarial controls and records
distinct blockers for every negative control. It carries forward I4's external
proxy blockers, then closes the deferred semantic goal ownership relabel,
identity acceptance relabel, native support relabel, unbounded drift,
budget-surface ambiguity, stale source state, missing source state, and
dependency-trace omission controls.

The generated report records the full `Iteration 5 Explanation` section for
the control inputs, control rule, deferred controls closed in I5, end result,
and claim boundary.

Post-review hardening records the I5 top-level output-field declaration,
idempotency digest plan, explicit control execution-scope record, and duplicate
record identity check for the flat and structured control records.

Scope boundary:

```text
I5 control-clean candidate != final AP5
I5 stale/missing source controls != full I6 artifact replay
I5 unbounded drift control != full I6 bounded perturbation matrix
```

### Iteration 6. Bounded Drift And Replay Matrix

Test bounded target formation under perturbation and replay:

```text
support-state perturbation
memory-state perturbation
regulation-state perturbation
stale-state perturbation
budget-invalid perturbation
unbounded-drift null
duplicate replay
artifact-only filesystem replay
snapshot/load replay
order-inversion replay
```

Perturbation defaults to validate or replace in Iteration 6:

```text
support-state perturbation:
    one bounded step toward lower and higher support margin

memory-state perturbation:
    one bounded step across the memory/context ordinal or numeric scale

regulation-state perturbation:
    one bounded step across the regulation deficit/confidence scale

stale-state perturbation:
    source_current = false or source window outside the frozen freshness policy

budget-invalid perturbation:
    at least one frozen budget limit exceeded before target use

order inversion:
    source rows are serialized in reversed and shuffled order while preserving
    row ids and digests; canonical replay must reproduce the same target
```

Expected artifacts:

```text
outputs/n15_bounded_drift_replay_matrix.json
reports/n15_bounded_drift_replay_matrix.md
scripts/build_n15_bounded_drift_replay_matrix.py
```

Iteration 6 should show whether target formation changes only when serialized
source-current state changes within the bounded drift policy.

Result:

```text
Status: passed.
Artifact: outputs/n15_bounded_drift_replay_matrix.json
Report: reports/n15_bounded_drift_replay_matrix.md
Acceptance state: accepted_bounded_drift_replay_matrix_pending_claim_boundary_classification
Output digest: b73f05459697a18117ab5db0ef3f3bf5dff41c78a4dbacc40af11676a8b0532a
```

Iteration 6 accepts the bounded drift and replay matrix. Support, memory,
regulation, and AP4 consequence-context perturbations produce target changes
only within the frozen bounded drift policy. Stale source state,
budget-invalid input, and unbounded-drift variants fail closed. Duplicate
replay, artifact-only filesystem replay, snapshot/load replay, and
order-inversion replay reproduce the target.

The generated report records the full `Iteration 6 Explanation` section for
the I5 candidate input, replay rule, bounded drift rule, end result, and claim
boundary.

Post-review hardening records the I6 top-level output-field declaration,
idempotency digest plan, explicit record execution-scope record, AP4
consequence-context perturbation, split target-change direction checks, and
identity checks for retained flat/nested matrix records.

Scope boundary:

```text
I6 replay-clean candidate != final AP5
I6 bounded target drift != semantic goal ownership
I6 artifact replay equality != native support
```

### Iteration 7. Claim Boundary And AP5 Classification

Classify the candidate against the AP5 gate and claim boundary:

```text
AP5 gate resolution
hypothesis acceptance states
unsafe claim flags forced false
native support and Phase 8 flags
blocked-input audit
constructed followout caveat audit
whole-experiment interpretation draft
```

Hypothesis classification rubric:

```text
supported:
    every required gate for the hypothesis is validated and all associated
    negative controls fail closed

deferred:
    source coverage exists but a required gate, replay, or control has not
    been executed

rejected:
    a required gate fails or a negative control passes without a valid blocker

partial_or_scope_limited:
    a narrower candidate is supported but the full AP5 claim is blocked by an
    explicit scope caveat
```

Expected artifacts:

```text
outputs/n15_claim_boundary_record.json
reports/n15_claim_boundary_record.md
scripts/build_n15_claim_boundary_record.py
scripts/validate_n15_claim_boundary_record.py
```

Result:

```text
Status: passed.
Artifact: outputs/n15_claim_boundary_record.json
Report: reports/n15_claim_boundary_record.md
Acceptance state: accepted_ap5_classification_claim_boundary_clean_pending_closeout
Classified AP level: AP5
AP5 classification supported: true
Final AP5 supported: false
Output digest: 76d2258795d5799503cca9ad26fd24df512c2dbfb3450055c349e3162cef0266
```

Iteration 7 validates all 36 AP5 gates, classifies Hypotheses A, B, and C as
supported, audits blocked inputs, preserves the N14 constructed followout
caveat, and records the claim boundary rows needed before closeout. The result
is an artifact-level AP5 endogenous proxy formation candidate, boundary-clean
pending Iteration 8 closeout.

Post-review hardening records the I7 output-shape evolution from the I2 schema
contract, the intentional empty `rows` scope, flat/nested boundary-record
identity, canonical interpretation-record ownership, dedicated versus
claim-flag/I4 blocked-claim control coverage, exact I4 blocked-claim set
validation, exact I6 iteration-result key validation, and an independent I7
validator.

Iteration 7 must not close the experiment until all source rows, controls, and
claim flags are resolved.

### Iteration 8. N15 Closeout And N16 Handoff

Close hypotheses, freeze the supported AP level, list blockers, and decide
whether the next work is N16 or targeted Phase 8.

Expected artifacts:

```text
outputs/n15_closeout_and_handoff.json
reports/n15_closeout_and_handoff.md
scripts/build_n15_closeout_and_handoff.py
```

Result:

```text
Status: passed.
Artifact: outputs/n15_closeout_and_handoff.json
Report: reports/n15_closeout_and_handoff.md
Acceptance state: closed_claim_clean_ap5_artifact_level_endogenous_proxy_formation
Final supported AP level: AP5
Final AP5 supported: true
Final claim ceiling: artifact_level_ap5_endogenous_proxy_formation_candidate
Output digest: 715153a1cd8336a5376cd4e2f4a4c7fcb0becce28ef63f252de2c90122b93ba9
```

Iteration 8 freezes final N15 support at artifact-level AP5, records the final
claim ceiling, final controls, final blockers, final source-row roles, and the
N16 handoff. Targeted Phase 8 remains optional/deferred and not required before
N16; native support and fully native integration remain unopened.

N15 closes only when every source row is classified, every AP5 gate is either
validated or recorded as a blocker, every control has a pass/fail result, and
all unsafe claim flags remain false.

## Claim Boundary

```text
endogenous proxy formation != semantic goal ownership
runtime-derived target != intention
support-derived target != agency
support/identity-condition descriptor != identity acceptance
artifact-level AP5 != native support
N15 AP5 != fully native agentic-like integration
```
