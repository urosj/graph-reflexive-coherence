# N09 Goal-Proxy Regulation Implementation Plan

This document records the implementation plan for
`2026-05-N09-lgrc-goal-proxy-regulation`.

N09 asks whether prior LGRC evidence can support regulation of a serialized
runtime-visible proxy condition without promoting intention, agency, or goal
ownership.

## Scope

N09 is experiment-local unless a separate Phase 8/core implementation task is
opened. Scripts, configs, reports, and outputs live under:

```text
experiments/2026-05-N09-lgrc-goal-proxy-regulation/
```

Do not change `src/*` for N09 without stopping and opening a separate Phase 8
task. Existing LGRC9V3 route-arbitration, producer, packet, topology,
surface-lineage, topology-state reabsorption, snapshot, telemetry, and
artifact-replay surfaces may be used, but N09 experiment-local code must not
silently redefine their semantics.

## Inherited Evidence

N09 should cite these prior results as source context, not as automatic N09
evidence:

```text
N05:
    O5 self_sustained_oscillator_candidate
    O6 blocked by missing_route_conductance_memory_policy

N06:
    SC6 artifact_only_semantic_route_choice_candidate

N07:
    ID6 artifact-only source-specific bounded_non_destructive_exchange
    runtime identity acceptance remains blocked

N08:
    Hypothesis A:
        artifact_only_route_memory_or_trail_affordance_candidate
        scope = artifact_only_serialized_producer_policy_route_memory_or_trail

    Hypothesis B:
        static_positive_geometry_route_response_persistence_candidate
        blocker = native_route_conductance_memory_policy_missing
```

N09 may consume N08 Hypothesis A only within its scoped artifact-only serialized
memory/trail claim. N09 may cite N08 Hypothesis B as a static geometry response
design direction, but must not treat it as native trail memory.

## A-Ladder Boundary

N09 targets the roadmap's A4 rung:

```text
A4 = goal-proxy regulation of a runtime-visible condition
```

N09 may produce A5-relevant observations, but it does not close A5. Identity
continuity under regulation is a handoff condition for N10 unless a later N09
extension explicitly opens an identity-continuous regulation branch.

Required identity/support outcome tags:

```text
identity_not_tested_under_regulation
identity_preserved_under_regulation
identity_disrupted_under_regulation
support_preserved_under_regulation
support_disrupted_under_regulation
```

If regulation disrupts the N07 support/identity evidence, that is a meaningful
result and must be recorded. It blocks N10 consumption of that lane, but does
not automatically erase lower GPR evidence if the proxy-regulation chain is
otherwise valid.

## Hypotheses

N09 keeps two hypotheses separate.

```text
Hypothesis A:
    serialized producer/policy goal-proxy regulation

Hypothesis B:
    native substrate-mediated goal-proxy regulation
```

Iterations 1-9 follow the Hypothesis A path, but Hypothesis B remains an
active staged question rather than a discarded branch:

```text
B0 inventory:
    identify which native/substrate-mediated ingredients from N05-N08 could
    carry proxy, error, response, or route-bias evidence

B1 probe:
    after the A-path identifies load-bearing variables and response laws, try a
    geometry/substrate-mediated regulation probe without experiment-local
    correction logic

B2 blocker/absorption decision:
    if a pure native loop requires a missing LGRC policy surface, record the
    blocker and the minimal surface that would be needed
```

Expected Hypothesis B blocker until tested:

```text
native_goal_proxy_regulation_policy_missing
```

Only full native absorption is deferred. That follows the roadmap rule: do not
add core LGRC mechanisms until the experiments identify the minimal policy
surface that should be absorbed.

## Core Definition

Goal-proxy regulation means:

```text
runtime-visible proxy condition
-> serialized target band
-> error signal
-> route choice, producer scheduling, or packet work selected because of the
   proxy error
-> later proxy condition moves toward, stays within, or recovers toward the
   target band
-> artifact replay reconstructs the chain
```

The proxy is not a desire, intention, reward, utility function, or owned goal.
It is a declared measurement target used to test regulation mechanics.

Arc-of-Becoming orienting question:

```text
Can this system regulate something it can observe, using memory-shaped choice,
while preserving identity/support and clean claim boundaries?
```

Use this as the interpretation frame for N09. The experiment should classify
what appears before promoting anything:

```text
no regulation
wrong-direction response
probe-supported correction
repeated bounded correction
support-dependent regulation
identity-anchored regulation
artifact-only regulation candidate
native-policy gap or native expression candidate
```

These are observation and classification outcomes. They do not imply
intention, agency, goal ownership, identity acceptance, or semantic goal
understanding.

The first N09 tranche is single-variable regulation. Multi-variable regulation,
cross-context policy composition, or adaptive policy switching should be
recorded as N10 handoff material unless N09 later opens an explicit extension.

## Proxy Surface Contract

The authoritative proxy row schema is frozen in Iteration 2. At minimum, every
GPR1+ row should serialize:

```text
proxy_id
proxy_kind
regulated_variable_id
regulated_variable_surface
regulated_variable_digest
measurement_value
target_band
error_metric
error_value
proxy_policy_id
proxy_policy_digest
event_time_key
scheduler_event_index
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
source_artifacts
source_reports
claim_flags
```

The README and implementation plan use this as the canonical contract. Any
shorter field list is descriptive only; the Iteration 2 fixture manifest must
freeze the operational schema.

Allowed `regulated_variable_surface` values:

```text
node_coherence_band
route_aspect_mass_band
support_area_balance
dual_basin_exchange_balance
oscillator_return_amplitude_band
memory_surface_strength_band
candidate_route_usage_balance
```

The default Iteration 2 fixture should prefer a simple, replayable proxy:

```text
source or target node coherence band
```

because it is directly budget-auditable. More semantic labels such as "home",
"food", or "resource" must remain aliases for runtime-visible surfaces, not
evidence by themselves.

## Regulation Policy Contract

The regulation policy must serialize:

```text
regulation_policy_id
regulation_policy_digest
regulated_variable_id
target_band
error_metric
action_candidates
selection_rule
producer_policy_id if producer-mediated
native_route_arbitration_policy_id if route-arbitrated
memory_surface_digest if memory-shaped
identity_support_digest if identity-anchored
```

Allowed policy roles:

```text
threshold trigger
candidate-score component
route-arbitration compatibility component
packet scheduling eligibility
bounded correction policy
```

Forbidden policy roles:

```text
hidden controller
reward optimizer
semantic desire
unserialized target change
coherence source term
direct producer mutation
claim emission
```

### Memory-Shaped Regulation Lane

N09 must explicitly test whether regulation consumes N08 memory-shaped choice
rather than merely having memory available in the background.

At GPR3+, include paired lanes:

```text
memory_shaped_lane:
    same proxy / same target / same policy with N08 memory-surface evidence

no_memory_control_lane:
    same proxy / same target / same policy without N08 memory-surface evidence
```

The control must either fail with a specific blocker or produce a distinct
response classification. Valid blockers include:

```text
memory_surface_required_for_regulation
memory_surface_not_used
memory_surface_missing
```

### Oscillator Regulation Fixture

The default fixture should start with a directly budget-auditable node
coherence band. Oscillator regulation is a secondary fixture family:

```text
oscillator_return_amplitude_band
```

It should be deferred until the simple proxy path is understood, then used to
close the N05 -> N09 loop if still needed.

## GPR Ladder

GPR levels are evidence classifications, not claim flags.

```text
GPR0:
    no regulation / label-only proxy.

GPR1:
    proxy measurement. Runtime-visible condition and target band are serialized.

GPR2:
    error signal. Error is computed from serialized proxy evidence under a
    declared policy.

GPR3:
    proxy-conditioned eligibility. Route candidate, producer eligibility, or
    schedule request changes because of the proxy error.

GPR4:
    single-cycle correction. One selected action measurably reduces error or
    returns the proxy condition toward the target band.

GPR5:
    repeated bounded regulation. Multiple cycles keep the proxy bounded or
    recover from small perturbation under the same policy. If N07 support
    evidence is consumed, identity/support preservation or disruption must be
    tagged.

GPR6:
    artifact-only goal-proxy regulation candidate. Replay reconstructs proxy,
    error, eligibility/selection, packet work, response, identity/support
    outcome tags where applicable, and controls.
```

## Regulation Outcome Taxonomy

Every regulation run should classify its outcome:

```text
no_response_to_error
wrong_direction_response
single_cycle_error_reduction
single_cycle_band_return
bounded_repeated_regulation
overshoot_oscillation
saturation_no_recovery
policy_saturation
memory_poisoning
budget_violation
identity_disrupted_under_regulation
identity_preserved_under_regulation
native_policy_gap
```

These are observation classes and should be preserved even when the result is
negative.

## Mechanism Status Tags

Every positive result must record:

```text
mechanism_status =
    producer_mediated |
    threshold_authorized |
    native_route_arbitrated |
    memory_shaped |
    identity_anchored |
    constitutive_native |
    native_policy_gap
```

More than one tag may apply. `constitutive_native` should remain false unless
the regulator is expressed entirely by existing serialized LGRC-native policy
and artifact replay.

`memory_shaped` and `identity_anchored` are N09-local extensions to the
roadmap mechanism-status tags. They record which upstream evidence is consumed;
they do not mean the mechanism is constitutive native.

## Dissolution Path

N09 should classify how far the regulation mechanism has been dissolved:

```text
producer-mediated regulation scaffold
-> threshold-authorized regulation
-> native route-arbitrated regulation
-> constitutive native policy if current LGRC can express it
```

The expected initial result is producer-mediated or threshold-authorized. A
native-policy gap is a valid finding if the artifact evidence identifies the
missing LGRC surface precisely.

## Budget And Boundary Rules

N09 must preserve:

```text
sum(active node coherence)
+ in_flight_packet_total
== conserved_budget_total
```

Proxy/error bookkeeping does not create or delete coherence. If a proxy policy
uses memory-surface strength, the N08 memory budget remains separate from
node-plus-packet coherence budget.

Producers may emit records and schedule only. They must not mutate coherence,
packet ledgers, topology, proxy state, memory state, support masks, identity
state, or claims directly.

## Controls

Negative controls must fail with distinct primary blockers:

```text
missing_proxy_surface
proxy_surface_digest_mismatch
hidden_proxy_target
posthoc_target_band_change
proxy_error_mismatch
hidden_reward_input
experiment_side_if_else
producer_mutation_boundary_violation
direct_proxy_state_rewrite
budget_discontinuity
memory_scope_overclaim
memory_surface_not_used
identity_acceptance_overclaim
identity_disrupted_under_regulation
stale_proxy_read
order_inversion
duplicate_proxy_update
no_response_to_error
wrong_direction_response
overshoot_oscillation
saturation_no_recovery
policy_saturation
memory_poisoning
claim_promotion
```

## Perturbation And Withdrawal Schema

Iteration 2 must define perturbation and support-withdrawal fields before
Iteration 8 runs:

```text
perturbation_id
perturbation_kind
perturbation_amplitude
perturbation_duration_windows
perturbation_target_surface
support_withdrawal_kind
support_withdrawal_depth
support_withdrawal_duration_windows
expected_recovery_window_count
recovery_success_criterion
identity_support_outcome_tag
```

Perturbation magnitude must be serialized. Report-side labels such as "small"
are not sufficient without numeric or categorical fixture-defined values.

## Claim Discipline

Allowed if supported by gates:

- goal-proxy measurement candidate;
- proxy error signal candidate;
- proxy-conditioned route-selection candidate;
- single-cycle proxy-correction candidate;
- repeated bounded proxy-regulation candidate;
- artifact-only goal-proxy regulation candidate.

Blocked in N09:

- intention;
- agency;
- desire;
- reward optimization;
- semantic goal understanding;
- goal ownership;
- identity acceptance;
- RC identity collapse;
- ACO or colony-like behavior;
- locomotion-like behavior;
- biological behavior;
- personhood;
- unrestricted identity;
- unrestricted movement.

`goal_proxy_regulation_claim_allowed` remains false until GPR6 artifact-only
replay passes. Even then, it is a goal-proxy regulation evidence claim only,
not intention or agency.

## Ceiling Algorithm

The N09 ceiling is the highest GPR level whose required gates pass. A failed
later gate records a primary blocker and leaves the ceiling at the strongest
passing level.

```text
GPR6 fails but GPR5 passes:
    ceiling = repeated_bounded_proxy_regulation_candidate
    blocker = artifact_only_goal_proxy_replay_failed

GPR5 fails but GPR4 passes:
    ceiling = single_cycle_proxy_correction_candidate
    blocker = repeated_regulation_not_bounded

GPR4 fails but GPR3 passes:
    ceiling = proxy_conditioned_route_selection_candidate
    blocker = no_response_to_error | wrong_direction_response
```

Identity/support disruption blocks N10 handoff for that lane, but lower N09
regulation evidence may remain valid if source artifacts and budgets pass.

## N10 Handoff Artifact Fields

N09 closeout should prepare explicit N10 handoff fields:

```text
goal_proxy_regulation_policy_digest
proxy_surface_digest
error_policy_digest
regulation_response_digest
memory_surface_digest if memory-shaped
identity_support_digest if identity-anchored
mechanism_status_tags
regulation_outcome_tag
identity_support_outcome_tag
native_policy_gap_records
```

Minimum useful handoff is GPR5 repeated bounded regulation. Preferred handoff
is GPR6 artifact-only goal-proxy regulation.

## Planned Iterations

```text
Iteration 0:
    Planning and stubs. Create N09 docs, directories, ladder, claim boundary,
    and inherited-source summary. No probes.

Iteration 1:
    Baseline and source inventory. Inventory N05/N06/N07/N08 source artifacts,
    available native/producers surfaces for proxy measurement and regulation,
    missing native regulation policy surfaces, Hypothesis B staged status,
    and claim flags.

Iteration 2:
    Fixture manifest and proxy-regulation contract. Define proxy surface rows,
    target-band schema, error policy, regulation policy, controls, and artifact
    replay fields before any positive probe. Also freeze memory/no-memory
    lanes, perturbation magnitude schema, identity/support outcome tags,
    ceiling algorithm, and N10 handoff fields.

Iteration 3:
    GPR1 proxy measurement. Emit source-backed proxy measurement rows from a
    runtime-visible condition without regulation.

Iteration 4:
    GPR2 error signal. Compute error from serialized proxy evidence and target
    band under a declared policy.

Iteration 5:
    GPR3 proxy-conditioned eligibility. Show that route candidate score,
    producer eligibility, or schedule request changes because of the proxy
    error, not hidden fixture code. Include a dedicated memory-shaped lane and
    no-memory control lane.

Iteration 6:
    GPR4 single-cycle correction. Process one selected route/packet action and
    verify that the proxy state moves in the expected direction with exact
    budget accounting.

Iteration 7:
    GPR5 repeated bounded regulation. Run repeated correction windows with the
    same policy. Record boundedness, saturation, overshoot, oscillation, or
    failure under the regulation outcome taxonomy.

Iteration 8:
    Perturbation, withdrawal, and identity/support checks. Test whether
    regulation survives small perturbation or weakened scaffold, and whether it
    remains source/support-specific without identity-acceptance promotion.
    Record identity preservation or identity disruption explicitly.

Iteration 9:
    GPR6 artifact-only replay and closeout. Reconstruct proxy measurement,
    error, route/producer evidence, scheduled/processed packet work, response,
    budgets, controls, N10 handoff fields, and claim boundaries from artifacts
    only.

Iteration 10:
    Hypothesis B0 native/substrate inventory. Reopen the staged B-path after
    the A-path closeout, inventory the load-bearing A-path variables
    (proxy surface, target band, error sign, response direction, packet
    correction, repeated boundedness, perturbation recovery), and map them
    against native/substrate-mediated ingredients from N05-N08 and current
    LGRC. Record which parts can be represented without experiment-local
    correction scheduling and which require missing native policy surfaces.

Iteration 11:
    Hypothesis B1 geometry/substrate-mediated regulation probe. Try one
    minimal native/substrate response probe that perturbs the same proxy and
    observes whether fixed geometry, conductance, flux, or existing LGRC
    substrate dynamics move the proxy toward the declared band without using
    the A-path producer correction scheduler. Classify any return, bounded
    degradation, wrong-direction response, saturation, or no-response result
    as evidence, not a native-regulation claim.

Iteration 11-A:
    Hypothesis B1 refinement: positive geometry return-scaffold probe. Use the
    Iteration 11 no-response result as a baseline, then add one predeclared
    conserved return-channel scaffold before the post-perturbation error is
    observed. Test whether the proxy can return to the declared band without
    consuming the A-path producer correction scheduler, candidate set, or
    producer record. If successful, freeze only a scoped
    native/substrate-mediated goal-proxy regulation design candidate and keep
    general native regulation blocked until a native proxy/error/response
    policy surface exists.

Iteration 11-B:
    Hypothesis B1 refinement: band-buffered return-scaffold family probe. Use
    Arc-of-Becoming method to move from a single true/false matched-return
    result to a regime question: what envelope does the predeclared return
    geometry express? Keep one fixed return amount across a perturbation family
    and record band return, bounded partial return, wrong-direction response,
    or degradation without adapting the return amount from post-perturbation
    error. Treat the strongest positive result as a finite-envelope scaffold
    design candidate, not general native regulation.

Deferred cultivation note:
    An optional 11-C can later explore multi-stage geometry-envelope
    cultivation, such as multiple fixed return channels or delayed staged
    returns, to see whether the finite envelope can be widened without reading
    post-perturbation error. This is not required for N09 closeout because
    Iteration 11-B already exposes the relevant boundary: geometry can improve
    regulation-like behavior inside a finite envelope, while broader native
    regulation still requires response-magnitude policy support.

Iteration 12:
    Hypothesis B2 native/substrate closeout. Reconstruct the B-path inventory
    and probe artifacts, including Iteration 11, 11-A, and 11-B if present.
    Freeze either a scoped native/substrate-mediated regulation design
    candidate or explicit blockers, and keep Hypothesis A closed without
    promoting it into B. If pure native regulation requires a missing LGRC
    policy surface, record the blocker, expected minimal policy surface, and
    N10/Phase-8 handoff.
```

## Closeout Target

The strongest intended N09 closeout is:

```text
artifact_only_goal_proxy_regulation_candidate
```

N09 should hand off to N10 only when the goal-proxy regulation ceiling is
explicit and all stronger claim boundaries remain clean.

The B-path extension does not change the A-path closeout by default. Its
strongest expected positive result is a scoped
`native_substrate_mediated_goal_proxy_regulation_design_candidate`; its most
likely blocker remains `native_goal_proxy_regulation_policy_missing`, refined
into the smallest missing proxy/error/response policy surface the evidence
requires.
