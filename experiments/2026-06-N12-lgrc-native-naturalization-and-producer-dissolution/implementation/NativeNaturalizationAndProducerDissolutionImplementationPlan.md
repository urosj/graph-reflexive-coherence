# N12 Native Naturalization And Producer Dissolution Implementation Plan

This document records the implementation plan for
`2026-06-N12-lgrc-native-naturalization-and-producer-dissolution`.

N12 is a bridge experiment. It classifies N05-N11 producer-layer mechanisms
into native-absorption candidates, blocked theory-sensitive mechanisms, and
experiment-local scaffolds while preserving the RC theory boundary.

## Scope

N12 is experiment-local unless a separate Phase 8/native implementation task is
opened. Scripts, configs, reports, outputs, hypotheses, and implementation
records live under:

```text
experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/
```

Do not change `src/*` for N12 without stopping and opening a separate Phase 8
task. If Phase 8 is later opened, inspect native telemetry surfaces under
`src/pygrc/telemetry` as well as core/model code.

## Inherited Evidence

N12 consumes N11 as the direct source boundary, and through N11 consumes the
N05-N10 chain.

Direct N11 source state:

```text
final_supported_gali_ceiling = GALI7
final_claim_ceiling = broader_general_artifact_only_agentic_like_integration_candidate
fully_native = false
artifact_only = true
```

Native blockers inherited from N11:

```text
native_route_conductance_memory_policy_missing
native_response_magnitude_policy_missing_for_unbounded_perturbations
native_identity_acceptance_validator_missing
native_agentic_like_integration_policy_missing
```

N12 should cite exact N11 source artifacts and digests when building the
Iteration 1 inventory. N12 should not consume older N05-N10 rows as native
support unless the N11/N10 handoff records already identify their boundaries.

## Target

N12 targets:

```text
NAT4 = Phase 8-ready native policy candidate
```

This means:

```text
source-backed mechanism inventory
-> naturalization schema and rejection rules
-> concrete candidate evaluation
-> theory-sensitive boundary records
-> Phase 8 readiness matrix
-> no Phase 8 implementation unless separately opened
```

This is not agency, intention, semantic goal ownership, identity acceptance,
biological behavior, personhood, unrestricted agency, or fully native
agentic-like integration.

Native absorption must remain compatible with RC causality, coherence, LGRC
geometry, packet scheduling, topology lineage, and budget conservation. N12
must not add non-RC quantities to make a candidate pass.

## Local Ladder

N12 uses the `NAT0-NAT6` ladder from the root README:

```text
NAT0 = producer-only artifact scaffold
NAT1 = source-backed producer pattern
NAT2 = replayable producer pattern with controls
NAT3 = native contract candidate
NAT4 = Phase 8-ready native policy candidate
NAT5 = native implementation exists but not integrated into agentic-like composition
NAT6 = native implementation validates within composition replay
```

N12 aims for `NAT4`. `NAT5` and `NAT6` require later Phase 8 implementation
and composition replay validation.

### NAT3 And NAT4 Gates

`NAT3` means the row has a plausible native contract target but is not yet
Phase 8-ready. A `NAT3` row may still lack complete controls, telemetry,
idempotency, replay, budget, or compatibility gates.

`NAT4` means the row is ready to open targeted Phase 8 work. A row cannot reach
`NAT4` unless it records:

```text
native policy name
record schema sketch
default-off flags
enabled/validated/supported separation
idempotency/digest plan
runtime-visible inputs
budget surfaces
telemetry requirements
snapshot/replay requirements
negative controls
compatibility tests
claim flags forced false
non_rc_quantity_audit
mutation_boundary
producer_or_policy_may_schedule_only
step_or_topology_event_owns_state_mutation
src_diff_empty = true
native_supported_flags = false
phase8_opened = false
```

## Candidate Disposition

Every N12 candidate row should be assigned exactly one primary disposition:

```text
primary_disposition =
    scaffold
    native_absorption_candidate
    theory_sensitive_blocker
    blocked_missing_source_or_gate

nat_level =
    NAT0..NAT6

phase8_ready =
    true only when nat_level = NAT4
```

`phase8_ready` is derived from `nat_level = NAT4`. It is not a competing
primary class.

Rows may also carry secondary tags:

```text
producer_mediated
validator_local
bookkeeping_only
native_supported_selection_only
native_policy_gap
cross_cutting_contract
```

## Provisional Iteration 1 Row Shape

Iteration 2 freezes the final schema, but Iteration 1 must not use ad hoc
inventory rows. Each Iteration 1 row should include at least:

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
producer_decision_fields
bookkeeping_fields
runtime_visible_surfaces
budget_surfaces
native_gap
provisional_primary_disposition
provisional_nat_level
provisional_phase8_ready
claim_ceiling
blocked_claims
missing_gates
non_rc_quantity_audit
```

`provisional_primary_disposition` should map to the primary disposition
vocabulary unless the row is explicitly marked `blocked_missing_source_or_gate`.
`provisional_phase8_ready` must be false unless `provisional_nat_level = NAT4`.

## Non-RC Quantity Audit

Every candidate row must include:

```text
non_rc_quantity_audit
```

At minimum, that audit should answer:

```text
is the mechanism expressible as RC causality, coherence, LGRC geometry, flux,
packet scheduling, topology lineage, or budget accounting?
is the mechanism only producer bookkeeping?
does decay, relaxation, or response sizing conserve or debit an accounted
quantity?
does the candidate require a new scalar state outside RC accounting?
if an extra quantity is required, what NAT4 blocker prevents readiness?
```

If a candidate requires an extra unaccounted quantity, it cannot reach `NAT4`.

Response magnitude candidate rows should also answer:

```text
is proxy measurement a derived observable or new state?
is target band exogenous or runtime-visible policy?
is response gain serialized and replayable?
does correction debit node-plus-packet budget?
does response sizing require hidden optimization or external controller state?
```

## Seed Rows From N11

N12 begins with these seed rows from the N11 native generalization gap report.
They are not accepted N12 results until later iterations rebuild them from
source artifacts.

```text
route_context_and_native_route_arbitration_boundary:
    provisional disposition =
        scaffold unless future scope exceeds selection-only

N08_memory_trail_affordance_consumed_by_N10_N11:
    provisional disposition =
        native_absorption_candidate
    native gap =
        native_route_conductance_memory_policy_missing

N09_goal_proxy_regulation_and_response_sizing:
    provisional disposition =
        native_absorption_candidate
    native gap =
        native_response_magnitude_policy_missing_for_unbounded_perturbations

N07_support_invariance_and_identity_acceptance_boundary:
    provisional disposition =
        theory_sensitive_blocker
    native gap =
        native_identity_acceptance_validator_missing

artifact_only_generalization_validator:
    provisional disposition =
        scaffold for budget/replay contract fields,
        theory_sensitive_blocker for native integration meta-policy
    secondary tag =
        cross_cutting_contract
    native gap =
        native_agentic_like_integration_policy_missing
```

## Hypothesis Tracks

Hypothesis A:

```text
Some N05-N11 producer mechanisms are valid scaffolds but remain
artifact/producer-layer only.
```

Hypothesis B:

```text
Some mechanisms can be naturalized as native LGRC policy surfaces without
adding non-RC quantities.
```

Likely Hypothesis B candidates:

```text
native_route_conductance_memory_policy
native_response_magnitude_policy
```

Hypothesis C:

```text
Some mechanisms are theory-sensitive and must stay blocked until identity,
acceptance, or agency semantics are formalized.
```

Likely Hypothesis C candidates:

```text
native_identity_acceptance_validator
native_agentic_like_integration_policy
```

## Iterations

### Iteration 0. Planning And Stubs

Create the N12 experiment root, README, implementation plan, implementation
checklist, hypotheses files, and directory stubs. Freeze N12 as a bridge
experiment and Phase 8 gate-definition track, not a native implementation or
agency claim.

Result:

```text
Status: complete.
Target naturalization level: NAT4.
Phase 8 implementation opened: false.
Native support opened: false.
```

### Iteration 1. Baseline And Mechanism Inventory

Collect N05-N11 mechanisms, source artifacts, claim ceilings, and native
blockers. Record source paths, reports, SHA-256 digests, gap rows, producer
decisions, bookkeeping fields, thresholds to serialize, runtime-visible
surfaces needed, blocked claims, and the provisional row-shape fields defined
above.

Expected artifacts:

```text
outputs/n12_native_naturalization_inventory.json
reports/n12_native_naturalization_inventory.md
scripts/build_n12_native_naturalization_inventory.py
```

Acceptance statement:

```text
Iteration 1 passes if every inventory row is backed by N11/N10 source artifacts
and uses the provisional row shape, includes a non_rc_quantity_audit, and no
producer-mediated result is promoted into native support.
```

Result:

```text
Status: passed.
Artifact: outputs/n12_native_naturalization_inventory.json
Report: reports/n12_native_naturalization_inventory.md
Output digest: cd58000592e06cb4a48f3059b9c8e8538f93b2589d37c242137eec2aed8dfb9a
```

Iteration 1 records five source-backed rows: two `NAT3`
native-absorption candidates for route conductance memory and response
magnitude policy, three `NAT2` scaffold/blocker rows, zero `NAT4` rows, and
zero Phase 8-ready rows. All rows include the provisional row shape and
`non_rc_quantity_audit`; N12 opens no new native support. Inherited N11 native
route-arbitration support remains selection-only.

### Iteration 2. Naturalization Schema And Ladder

Define the NAT ladder, row schema, tags, claim flags, native-readiness
criteria, rejection rules, RC-compatibility fields, budget-conservation fields,
non-RC quantity audit fields, NAT3/NAT4 gates, derived phase8_ready semantics,
and fail-closed blocker tags.

Expected artifacts:

```text
outputs/n12_naturalization_schema_v1.json
reports/n12_naturalization_schema_v1.md
scripts/build_n12_naturalization_schema_v1.py
```

Acceptance statement:

```text
Iteration 2 passes if the NAT ladder and schema reject native support,
non-RC quantities, claim promotion, stale source use, hidden producer mutation,
and budget ambiguity without opening Phase 8 implementation.
```

Result:

```text
Status: passed.
Artifact: outputs/n12_naturalization_schema_v1.json
Report: reports/n12_naturalization_schema_v1.md
Output digest: f6e025deff124593dee73891fa15a196338d0c05351119556e905ebf6e525327
```

Iteration 2 freezes the `NAT0-NAT6` ladder, final row fields,
non-overlapping `primary_disposition` values, derived `phase8_ready` rule,
NAT3/NAT4 gates, non-RC quantity audit schema, mutation boundary schema,
forced-false claim flags, rejection rules, and planned artifacts for
Iterations 3-7. Iteration 2 freezes declarations only; candidate-row
validation against the final schema starts in Iterations 3-7.

### Iteration 3. Route Conductance Memory Candidate

Evaluate the N08 memory trail / affordance mechanism as a native
route-conductance policy candidate.

Required checks:

```text
producer-side route memory pattern
native geometry/conductance policy candidate
native coherence/flux mechanism
geometry-vs-bookkeeping decision
mutation_boundary
producer_or_policy_may_schedule_only
step_or_topology_event_owns_state_mutation
route-use-linked memory update rule
memory relaxation or decay rule
route-scope handling through runtime-visible policy
conductance eligibility threshold
route conductance memory budget surface
non_rc_quantity_audit:
    is memory a coherence, geometry, or flux effect?
    is it only producer bookkeeping?
    does decay or relaxation conserve an accounted quantity?
    does it require a new scalar state outside RC accounting?
controls against ACO, ant-colony behavior, intention, agency, and native
support relabeling
if assigning NAT4, every NAT4 gate frozen in Iteration 2 must be present
```

Expected artifacts:

```text
outputs/n12_route_conductance_memory_candidate.json
reports/n12_route_conductance_memory_candidate.md
scripts/build_n12_route_conductance_memory_candidate.py
```

Acceptance statement:

```text
Iteration 3 passes if route conductance memory is classified at its supported
NAT level with source links, RC-compatible policy surfaces, serialized
thresholds, geometry-vs-bookkeeping split, mutation boundary, non-RC audit,
controls, and no native support claim.
```

Result:

```text
Status: passed.
Artifact: outputs/n12_route_conductance_memory_candidate.json
Report: reports/n12_route_conductance_memory_candidate.md
Output digest: c41482f5fbefc2af7572139daa60f73bb06ab29e83fbf03a1b61f5e4a6b7afe1
```

Iteration 3 classifies `native_route_conductance_memory_policy` as a `NAT4`
Phase 8-ready native policy candidate with no implementation and no native
support claim. Producer-side N08 `memory_strength` remains an artifact-only
scaffold. The native candidate is limited to route geometry/conductance state
updated by committed route-use/topology events, with default-off flags,
idempotent digests, telemetry requirements, snapshot/replay gates, negative
controls, compatibility tests, non-RC quantity audit, mutation boundary, and
claim flags forced false. The generated NAT4 gate audit records `present`,
`validated`, and `source` for each gate. The candidate also names
`src/pygrc/telemetry` as the native telemetry namespace, keeps telemetry
default-off and backward-compatible while disabled, and types the relaxation
destination as a reversible baseline relaxation account inside route-conductance
accounting. Post-review tightening adds row-level `native_support_opened =
false`, documents all candidate-specific extension fields beyond the Iteration
2 final row schema, records a source digest policy for upstream artifacts with
mixed digest conventions, and fixes `generated_at` to the experiment timestamp
so file SHA values are reproducible across reruns with unchanged sources and
git HEAD.

### Iteration 4. Response Magnitude Candidate

Evaluate N09-N11 regulation sizing as a native response-magnitude policy
candidate.

Required checks:

```text
proxy measurement surface
target band
response gain
max correction per window
error_trend
saturation_status
overcorrection_status
bounded_window
out-of-envelope blocker threshold
response packet scheduling boundary
mutation_boundary
producer_or_policy_may_schedule_only
step_or_topology_event_owns_state_mutation
proxy and node-plus-packet budget surfaces
non_rc_quantity_audit:
    is proxy measurement a derived observable or new state?
    is target band exogenous or runtime-visible policy?
    is response gain serialized and replayable?
    does correction debit node-plus-packet budget?
    does response sizing require hidden optimization or external controller
    state?
controls against goal ownership, intention, agency, unbounded response, and
native support relabeling
if assigning NAT4, every NAT4 gate frozen in Iteration 2 must be present
```

Expected artifacts:

```text
outputs/n12_response_magnitude_candidate.json
reports/n12_response_magnitude_candidate.md
scripts/build_n12_response_magnitude_candidate.py
```

Acceptance statement:

```text
Iteration 4 passes if response magnitude policy is classified at its supported
NAT level with source links, RC-compatible policy surfaces, serialized
thresholds, trend/stability fields, mutation boundary, non-RC audit, controls,
and no native support claim.
```

Result:

```text
Status: passed.
Artifact: outputs/n12_response_magnitude_candidate.json
Report: reports/n12_response_magnitude_candidate.md
Output digest: 347a66e30fb532899664a475f6240239de70229573dc09f5947a2033e45614b4
```

Iteration 4 classifies `native_response_magnitude_policy` as a
bounded/envelope-gated `NAT4` Phase 8-ready response magnitude policy candidate
with no implementation and no native support claim. The candidate is limited to
runtime-visible proxy measurement, serialized target-band and gain policy,
bounded packet scheduling, and node-plus-packet budget debits. N09-N11 producer
regulation remains artifact-only evidence for a policy surface and opens no
native support claim for regulation, semantic goal ownership, intention, or
agency. The generated NAT4 gate audit records `present`, `validated`, and
`source` for each gate; trend and stability fields preserve bounded-error,
saturation, overcorrection, and out-of-envelope blocker evidence. The candidate
names `src/pygrc/telemetry` as the native telemetry namespace, keeps telemetry
default-off and backward-compatible while disabled, records the mutation
boundary as schedule-only policy with state mutation owned by `step()` or
topology events, and forces all native support and agency-related claim flags
false.

### Iteration 5. Identity Acceptance Boundary

Record why identity acceptance is not Phase 8-ready yet and what theory gates
are missing.

Required checks:

```text
support survival separated from identity acceptance
identity continuity separated from runtime acceptance
RC identity collapse claims blocked
validator-local support fields identified
missing formal acceptance semantics recorded
```

Expected artifacts:

```text
outputs/n12_identity_acceptance_boundary.json
reports/n12_identity_acceptance_boundary.md
scripts/build_n12_identity_acceptance_boundary.py
```

Acceptance statement:

```text
Iteration 5 passes if identity acceptance remains blocked with explicit theory
entry gates and no identity acceptance claim.
```

Result:

```text
Status: passed.
Artifact: outputs/n12_identity_acceptance_boundary.json
Report: reports/n12_identity_acceptance_boundary.md
Output digest: 22637fb4210725ac87cd5be283294d1f252ee4584058fe83acb68ad9270c9295
```

Iteration 5 classifies `native_identity_acceptance_validator` as a
theory-sensitive blocked boundary at `NAT2`, not a Phase 8-ready native policy
candidate. N07/N10/N11 support-survival evidence remains source-backed and
replayable, but support survival, identity continuity, and explicit restoration
are not promoted into identity acceptance, runtime acceptance, RC identity
collapse, native support, or agency. The row records missing theory entry gates,
keeps `phase8_ready = false`, preserves `native_supported_flags_false`, and
forces identity acceptance, runtime identity acceptance, RC identity collapse,
native support, and agency-related claim flags false.

### Iteration 6. Agentic-Like Integration Boundary

Record why full native agentic-like integration is a meta-gap, not one small
mechanism.

Required checks:

```text
component native policies not treated as integration meta-policy
artifact-only replay not treated as fully native integration
semantic agency claims blocked
budget/replay cross-cutting contract separated from agency semantics
```

Expected artifacts:

```text
outputs/n12_agentic_like_integration_boundary.json
reports/n12_agentic_like_integration_boundary.md
scripts/build_n12_agentic_like_integration_boundary.py
```

Acceptance statement:

```text
Iteration 6 passes if full native agentic-like integration remains blocked
until component native policies exist and composition replay validates them.
```

Result:

```text
Status: passed.
Artifact: outputs/n12_agentic_like_integration_boundary.json
Report: reports/n12_agentic_like_integration_boundary.md
Output digest: 2ed8ae9f591a7c435f012c70502c0871275a755d5355e7c95efa6d46a10c2601
```

Iteration 6 classifies `native_agentic_like_integration_policy` as a blocked
meta-policy boundary at `NAT2`, not a Phase 8-ready native policy candidate.
Route conductance memory and response magnitude remain `NAT4` component
candidates, while identity acceptance remains a `NAT2` blocked boundary; those
component results do not constitute native integration support. N11 GALI7 stays
artifact-only replay evidence, not fully native integration, native support, or
agency. The row records the missing cross-cutting budget/replay contract,
component native policy records, native composition replay, and integration
meta-policy gates, with all native support, fully native integration, and agency
claim flags forced false.

### Iteration 7. Phase 8 Readiness Package, No Implementation

Produce a concrete list of Phase 8-ready contracts, blockers, controls,
telemetry requirements, and test gates. Iteration 7 must explicitly record:

```text
src_diff_empty = true
native_supported_flags = false
phase8_opened = false
```

Expected artifacts:

```text
outputs/n12_phase8_readiness_matrix.json
reports/n12_phase8_readiness_matrix.md
scripts/build_n12_phase8_readiness_matrix.py
```

Acceptance statement:

```text
Iteration 7 passes if route conductance memory and response magnitude policy
are either classified as Phase 8-ready contracts or fail closed with distinct
missing-gate blockers, while identity acceptance and full native integration
remain blocked and no implementation has been opened.
```

### Iteration 8. N12 Closeout And Handoff

Freeze NAT levels, update the roadmap if needed, and decide whether next work
is targeted Phase 8 or N13.

Done condition:

```text
every seed row is classified
every NAT level is frozen
every Phase 8-ready row has controls, telemetry requirements, and tests
every deferred row has a blocker and rationale
src_diff_empty = true
native_supported_flags = false
phase8_opened = false
```

Expected artifacts:

```text
outputs/n12_closeout_and_handoff.json
reports/n12_closeout_and_handoff.md
scripts/build_n12_closeout_and_handoff.py
```

Acceptance statement:

```text
Iteration 8 passes if N12 classifies the N05-N11 producer mechanisms into
native absorption candidates, Phase 8-ready contracts derived from `NAT4`,
experiment-local scaffolds, and theory-sensitive blockers without implementing
Phase 8 or promoting artifact-only evidence into native LGRC support.
```
