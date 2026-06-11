# N10 Agentic-Like Integration Implementation Plan

This document records the implementation plan for
`2026-05-N10-lgrc-agentic-like-integration`.

N10 asks whether prior LGRC evidence can be composed into a bounded
agentic-like integration candidate without promoting agency, intention,
semantic goal ownership, identity acceptance, biological behavior, personhood,
or unrestricted agency.

## Scope

N10 is experiment-local unless a separate Phase 8/core implementation task is
opened. Scripts, configs, reports, and outputs live under:

```text
experiments/2026-05-N10-lgrc-agentic-like-integration/
```

Do not change `src/*` for N10 without stopping and opening a separate Phase 8
task. Existing LGRC9V3 route-arbitration, producer, packet, topology,
surface-lineage, topology-state reabsorption, snapshot, telemetry, and
artifact-replay surfaces may be used. N10 experiment-local code must not
silently redefine their semantics.

## Inherited Evidence

N10 should cite these prior results as source context and prerequisite
evidence:

```text
N05:
    O5 self_sustained_oscillator_candidate
    O6 blocked by missing_route_conductance_memory_policy

N06:
    SC6 artifact_only_semantic_route_choice_candidate

N07:
    ID6 artifact-only source-specific bounded_non_destructive_exchange
    Iteration 13 identity/support withdrawal baseline
    runtime identity acceptance remains blocked

N08:
    Hypothesis A:
        artifact_only_route_memory_or_trail_affordance_candidate
        scope = artifact_only_serialized_producer_policy_route_memory_or_trail

    Hypothesis B:
        static_positive_geometry_route_response_persistence_candidate
        blocker = native_route_conductance_memory_policy_missing

N09:
    A-path:
        artifact_only_goal_proxy_regulation_candidate

    B-path:
        native_substrate_mediated_goal_proxy_regulation_design_candidate
        blocker = native_response_magnitude_policy_missing_for_unbounded_perturbations
```

Inherited evidence is not automatic N10 evidence. Every N10 integration row
must cite source artifacts, source reports, and source digests.

## Target

N10 targets the roadmap's A6 rung:

```text
A6 = bounded agentic-like integration: route choice, memory-shaped affordance,
     identity/support baseline, and goal-proxy regulation compose in one
     artifact-valid chain without hidden experiment-side steering
```

N10 may record A5 evidence if regulation remains identity/support-aware across
cycles, perturbations, or topology changes. N10 does not close A7. N11 is the
broader/general integration experiment.

The full-composition lanes must keep this boundary explicit:

```text
support-intact composition:
    can contribute to ALI4/ALI5/ALI6 under bounded source-backed conditions

mild-withdrawal composition companion:
    can contribute A5-relevant evidence if the full composition remains
    source-current and support-aware under mild support weakening

broader/general cross-context integration:
    deferred to N11
```

If the mild-withdrawal companion is not run or fails, N10 may still close an
ALI6 bounded source-backed integration candidate under the support-intact
scope, but it must not overstate A5/generalization.

## N10 Category Ladder

N10 freezes a local Agentic-Like Integration ladder. This is the category
ladder used by N10 rows; it maps to the roadmap A-ladder but should not be
collapsed into an agency claim.

```text
ALI0:
    no integration; inventory, schema, or externally juxtaposed artifacts only

ALI1:
    source-backed bookkeeping composition; all prerequisite artifacts are
    present and schema-valid, but no causal integration replay exists

ALI2:
    support-aware regulation replay; N09 regulation evidence is attached to a
    surviving N07 support baseline

ALI3:
    support-sensitive regulation; support-survival, support-disruption, and
    explicit-restoration controls determine whether integration proceeds,
    blocks, or resumes

ALI4:
    route-memory-regulation composition; N06 route choice, N08 memory/trail
    affordance, N07 support, and N09 regulation compose into one source-backed
    row

ALI5:
    bounded repeated integration; the composition remains source-current,
    budget-safe, and claim-clean across a bounded repeated window

ALI6:
    bounded artifact-only agentic-like integration candidate; artifact-only
    replay reconstructs the full route-memory-support-regulation chain and all
    controls pass
```

`ALI6` is the local N10 completion target and maps to roadmap A6.

## Core Definition

Bounded agentic-like integration means:

```text
source-backed route-choice evidence
-> source-backed memory/trail affordance evidence
-> source-backed identity/support baseline
-> source-backed goal-proxy regulation evidence
-> one artifact-only integration chain
-> exact budget accounting
-> controls showing stale, hidden, disrupted, budget-invalid, and
   claim-promoting compositions fail closed
```

This is not intention, agency, semantic goal ownership, identity acceptance,
or ACO.

N05 is contextual, not compositional. It supplies coherence-wave, oscillator,
and route-aspect background for interpreting later mechanisms. The N10
composition chain itself is:

```text
N06 route choice
-> N08 memory/trail affordance
-> N07 identity/support baseline
-> N09 goal-proxy regulation
```

N10 should not force N05 into a dedicated chain field unless a later iteration
opens a concrete oscillator-coupled integration branch.

Arc-of-Becoming orienting question:

```text
Can a system that can choose a route, remember route-affordance history, keep a
support identity baseline, and regulate a proxy condition show a bounded
agentic-like integration pattern without hidden steering?
```

Use this as the interpretation frame. N10 should classify what appears before
promoting anything:

```text
no integration
bookkeeping-only composition
support-aware regulation
memory-shaped support-aware regulation
route-memory-regulation composition
support-disruption-sensitive integration
restoration-gated integration
bounded artifact-only agentic-like integration candidate
native-policy gap
```

Route-choice scope constraint:

```text
N06 SC6 is selection-only and pre-topology scoped. N10 full-composition rows
must use route_context_tag = route_context_selection_only unless a later source
artifact supplies broader route-execution evidence. This constraint may limit
the interpretation of ALI4/ALI5/ALI6 rows and must be recorded in Iterations
7-9.
```

## Integration Schema

The authoritative integration row schema is frozen in Iteration 2. At minimum,
every integration row should serialize:

```text
integration_row_id
integration_level
n10_category_level
integration_policy_id
integration_policy_digest
event_time_key
scheduler_event_index
source_experiment_ids
source_artifacts
source_reports
source_artifact_digests
route_choice_artifact
route_choice_digest
memory_affordance_artifact
memory_affordance_digest
identity_support_artifact
identity_support_digest
goal_proxy_regulation_artifact
goal_proxy_regulation_digest
support_state_tag
route_context_tag
memory_scope_tag
regulation_scope_tag
integration_outcome_tag
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
memory_budget_surface
proxy_budget_surface
artifact_only
runtime_state_used
producer_scaffold_used
native_policy_gap
blocked_claims
claim_flags
```

The Iteration 2 fixture manifest is the authoritative schema. This plan
describes the intended shape; validators should consume the manifest.

Required support-state tags:

```text
support_intact_survives
mild_withdrawal_survives
n09_matched_withdrawal_disrupts_support
explicit_restoration_recovers_support
support_state_not_applicable
```

Required integration outcome tags:

```text
bookkeeping_only
support_aware_regulation_candidate
memory_shaped_support_aware_regulation_candidate
route_memory_regulation_composition_candidate
support_disruption_blocked_integration
restoration_gated_integration_candidate
bounded_artifact_only_agentic_like_integration_candidate
native_policy_gap
```

## Budget Extraction And Continuity

N10 starts from source artifacts produced by separate experiments. Therefore
artifact-only N10 rows may claim source-artifact budget compatibility, not
single-runtime packet-ledger continuity across N05-N09.

Budget modes:

```text
source_artifact_budget_compatibility:
    Each consumed source artifact has internally valid budget evidence or a
    recorded budget blocker. N10 may compose those artifacts as evidence, but
    must not claim one continuous live packet ledger across independent runs.

same_run_node_plus_packet_continuity:
    If a later N10 script performs a new run, it must record
    node_plus_packet_budget_before, node_plus_packet_budget_after, and
    node_plus_packet_budget_error from that same run.
```

Extraction policy:

```text
N06:
    route-selection budget evidence only; do not inherit packet execution
    because SC6 is selection-only.

N07:
    support-lane budget compatibility from Iteration 13
    withdrawal_lanes[].final_budget_error. Support retention and separability
    are evidence metrics, not budget surfaces.

N08:
    memory-budget surface compatibility where serialized; keep memory budget
    separate from node-plus-packet and proxy budgets.

N09:
    goal-proxy regulation budget compatibility from GPR closeout rows and
    controls; keep proxy budget separate from memory and node-plus-packet
    budgets.
```

Cross-artifact budget continuity is blocked unless all components are produced
inside a single N10 runtime chain.

## Hypotheses

N10 keeps three hypotheses separate.

```text
Hypothesis A:
    bounded artifact-only integration can compose prior N05-N09 mechanisms
    without hidden steering

Hypothesis B:
    integration is support-sensitive: lanes with disrupted identity/support
    must block or downgrade unless explicit restoration evidence is present

Hypothesis C:
    a fully native substrate version remains blocked until the minimal native
    policy surfaces identified by N05-N09 are absorbed into LGRC
```

Hypothesis C is not a failure of N10 if it is recorded precisely. The roadmap
expects producer scaffolds to reveal mechanism shape before Phase 8/native
absorption is considered.

`native_agentic_like_integration_policy_missing` is a meta-gap. N10 can
identify the fields and policies such a native surface would need, but it does
not resolve that native policy inside the experiment-local tranche.

## Controls

Each N10 validator should include distinct blockers for:

```text
missing_route_choice_artifact
missing_memory_affordance_artifact
missing_identity_support_artifact
missing_goal_proxy_regulation_artifact
source_artifact_digest_mismatch
stale_route_context
stale_memory_surface
stale_identity_support_baseline
support_disrupted_but_integration_allowed
restoration_required_but_missing
hidden_experiment_side_steering
producer_direct_mutation
budget_surface_ambiguity
node_plus_packet_budget_discontinuity
artifact_only_replay_missing_link
claim_promotion_blocked
agency_overclaim_blocked
```

The controls matter as much as positive rows. A support-disruption block is a
useful result because it protects N10 from treating regulation as integrated
when the support identity baseline no longer holds.

## Iteration Plan

### Iteration 0. Planning And Stubs

Create the N10 experiment skeleton, README, implementation plan, checklist,
and hypotheses directory. Freeze N10 as A6 bounded integration and reserve A7
for N11.

### Iteration 1. Baseline And Source Inventory

Inventory source artifacts from N05-N09. Verify that the N07 Iteration 13
withdrawal baseline and N09 Iteration 12 closeout are available. Record
current source digests, current ceilings, and all blocked claims.

### Iteration 2. Integration Schema And Fixture Manifest

Freeze the integration row schema, support-state tags, integration outcome
tags, control blockers, and fixture manifest. Validate that source artifacts
are present and that no N10 run has occurred yet.

### Iteration 3. Support-Aware Regulation Replay

Build the first source-backed integration replay using N09 regulation and N07
support-intact evidence. The goal is not broader agency; it is to show that a
goal-proxy regulation chain can be attached to a still-valid support baseline.

### Iteration 4. Mild Withdrawal Survival Replay

Replay the same integration question under the N07 mild-withdrawal lane. If
support survives, record whether support-aware regulation remains consumable.

### Iteration 5. Disrupted Support Control

Consume the N07 N09-matched withdrawal lane. The expected result is a blocked
or downgraded integration row, because the support baseline is disrupted.
Passing this control is essential for N10.

### Iteration 6. Explicit Restoration Replay

Consume the N07 explicit-restoration lane. Integration may resume only if the
restoration artifact is explicit, source-backed, and replayable.

### Iteration 7. Route-Memory-Regulation Composition

Compose N06 route-choice evidence, N08 memory/trail affordance evidence, N07
support evidence, and N09 regulation evidence into one replayable composition
row. Reject hidden route labels, hidden memory surfaces, and experiment-side
steering.

Because N06 SC6 is selection-only, positive rows in this iteration must use
`route_context_tag = route_context_selection_only` unless a later source
artifact supplies broader route-execution evidence.

### Iteration 8. Bounded Repeated Integration

Run or replay a bounded repeated integration window. Verify that route,
memory, support, and proxy-regulation links remain source-current, budget-safe,
and claim-clean across repeated cycles.

Include a mild-withdrawal full-composition companion lane when possible. This
does not create broad A7 generalization, but it gives N10 an A5-relevant
support-sensitivity check for the full composition rather than only the
regulation sub-chain.

### Iteration 9. Artifact-Only Replay And Closeout

Build an artifact-only validator and closeout report. Decide whether the N10
ceiling is `bounded_artifact_only_agentic_like_integration_candidate` or a
specific blocker for the bounded Hypothesis A path. Record carry-forward
boundaries for Hypotheses B and C.

### Iteration 10. Full-Composition Disrupted Support Control

Take the accepted Iteration 9 route-memory-support-regulation composition and
consume it under the N07 `n09_matched_withdrawal_disrupts_support` lane. The
expected useful result is a blocked or downgraded full-composition row with a
distinct support blocker. This tests Hypothesis B at the full A6/ALI6
composition boundary, not only at the earlier support/regulation sub-chain.

The route, memory, and regulation source links should remain present and
valid. The row should fail because the identity/support baseline is disrupted,
not because one of the source artifacts is missing.

### Iteration 11. Full-Composition Explicit Restoration Replay

Replay the full composition after the N07 explicit-restoration lane. The goal
is to verify that the composition can resume only when restoration evidence is
explicit, source-backed, ordered after disruption, and replayable. Restoration
must not erase the prior disrupted-support control.

This iteration may record a restoration-gated full-composition candidate. It
does not create broad A7 generalization or identity acceptance.

### Iteration 12. Hypothesis B Support-State Matrix Closeout

Validate the full-composition support-state matrix:

```text
support_intact_survives
mild_withdrawal_survives
n09_matched_withdrawal_disrupts_support
explicit_restoration_recovers_support
```

The closeout should decide whether Hypothesis B is supported under the bounded
N10 scope: intact/mild/restored support states may allow the composition, while
disrupted support must block or downgrade it. All rows remain artifact-only and
claim-clean.

Closeout result:

```text
Iteration 12 passed.
hypothesis_b_status = supported_bounded_support_sensitive_full_composition
support_intact_survives -> composition preserved
mild_withdrawal_survives -> bounded companion preserved
n09_matched_withdrawal_disrupts_support -> attempted A6/ALI6 blocked
explicit_restoration_recovers_support -> A6/ALI6 resumed through explicit
    restoration evidence
```

This closes Hypothesis B for the bounded N10 scope. It does not open
A7/generalization, fully native agentic-like integration, agency, semantic
goal ownership, identity acceptance, RC identity collapse, ACO, biological,
personhood, or unrestricted agency claims.

### Iteration 13. Hypothesis C Native Policy Gap Inventory

Inventory which fields in the Hypothesis A/B composition are load-bearing but
still producer-mediated, artifact-local, or validator-local. At minimum,
review:

```text
N06 route context / native route arbitration boundary
N08 serialized producer-policy memory and route-conductance memory gap
N09 goal-proxy regulation and response-magnitude policy gap
N07 support/invariance validation and identity-acceptance boundary
N10 agentic-like integration policy gap
```

Separate bookkeeping fields from constitutive policy fields. Do not open a
native support flag in this iteration.

Inventory result:

```text
Iteration 13 passed.
inventory_status = native_policy_gap_inventory_complete
gap_row_count = 10
bounded_artifact_only_agentic_like_integration_supported = true
support_sensitive_integration_supported = true
fully_native_agentic_like_integration_supported = false
native_support_flags_opened = false
```

Primary blockers carried into Iteration 14:

```text
native_route_conductance_memory_policy_missing
native_response_magnitude_policy_missing_for_unbounded_perturbations
native_identity_acceptance_validator_missing
native_agentic_like_integration_policy_missing
```

### Iteration 14. Hypothesis C Native Contract Requirements

Convert the native gap inventory into minimal native contract requirements and
control expectations for a future Phase 8/native absorption pass. The output
should identify required policy records, runtime-visible inputs, ordering
constraints, budget surfaces, stale-context blockers, and claim-promotion
controls.

This is still contract/handoff work. It should not change `src/*`, implement
new LGRC behavior, or claim native agentic-like integration support.

Contract result:

```text
Iteration 14 passed.
contract_status = native_contract_requirements_complete
contract_row_count = 6
covered_policy_record_count = 10
phase_8_absorption_step_count = 6
fully_native_agentic_like_integration_supported = false
native_support_flags_opened = false
```

Iteration 14 defines contract rows for route context, route conductance /
geometry conductance memory, goal-proxy regulation / response magnitude,
identity/support validation, native agentic-like integration gating, and
budget-surface separation. Each row records runtime-visible inputs, ordering
requirements, stale-context blockers, budget surfaces, artifact replay
requirements, negative controls, and claim-boundary controls.

The future native absorption order is:

```text
1. cross-cutting budget/replay contract
2. route conductance memory absorption
3. goal-proxy response magnitude absorption
4. identity/support validator hardening
5. route context contract hardening if needed
6. native agentic-like integration meta-policy
```

This keeps Hypothesis C as a native-contract handoff. It does not implement
the policy surfaces, open native support flags, or promote agency,
identity-acceptance, ACO, biological, personhood, or fully native
agentic-like integration claims.

### Iteration 15. Hypothesis C Closeout And Handoff

Close the N10 native-policy-gap track. Record the exact blocker set for a fully
native version, the minimal Phase 8/native absorption order, and the constraints
that N11 must preserve if it consumes N10. The expected conservative closeout
is that N10 supports a bounded artifact-only agentic-like integration candidate
with support-sensitive B-path evidence, while fully native agentic-like
integration remains blocked by named native policy gaps.

Closeout result:

```text
Iteration 15 passed.
n10_final_status =
    closed_bounded_artifact_only_agentic_like_integration_with_support_sensitive_and_native_contract_handoff
final_n10_ceiling = bounded_artifact_only_agentic_like_integration_candidate
integration_level = A6
n10_category_level = ALI6
bounded_artifact_only_agentic_like_integration_supported = true
support_sensitive_integration_supported = true
fully_native_agentic_like_integration_supported = false
native_support_flags_opened = false
```

The final native blocker set is:

```text
native_route_conductance_memory_policy_missing
native_response_magnitude_policy_missing_for_unbounded_perturbations
native_identity_acceptance_validator_missing
native_agentic_like_integration_policy_missing
```

N11 may consume the Hypothesis A closeout, Hypothesis B support matrix, and
Hypothesis C native contract handoff. It must preserve that N10 is bounded,
artifact-only, support-sensitive, and not a claim of agency, intention,
semantic goal ownership, identity acceptance, RC identity collapse, ACO,
biological behavior, personhood, unrestricted agency, or fully native
agentic-like integration.

## Acceptance

N10 Hypothesis A passes if it produces source-backed integration artifacts
showing that route choice, memory-shaped affordance, identity/support baseline,
and goal-proxy regulation compose into a bounded artifact-valid chain under
declared controls.

The full N10 continuation passes if Hypothesis B then confirms the composition
is support-sensitive across intact, mild-withdrawal, disrupted, and restored
support states, and Hypothesis C records the exact native policy gaps needed
for a future fully native version. The integration must be replayable without
private runtime state, preserve budget accounting, block support-disrupted
lanes unless explicit restoration exists, reject hidden steering and claim
promotion, and keep all agency, intention, identity-acceptance, biological,
personhood, and unrestricted agency claims false.
