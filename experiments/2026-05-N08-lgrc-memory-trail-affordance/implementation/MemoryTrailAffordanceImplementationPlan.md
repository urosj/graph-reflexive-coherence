# N08 Memory Trail Affordance Implementation Plan

This document records the implementation plan for
`2026-05-N08-lgrc-memory-trail-affordance`.

N08 asks whether prior route use or coherence flow can create a serialized,
runtime-visible memory, trail, or affordance state that later shapes route
selection. It follows N05, N06, and N07 and should not repeat their questions:

```text
N05:
    coherence waves / oscillators

N06:
    context-conditioned semantic route choice

N07:
    RC identity attractor / bounded dual-basin exchange

N08:
    memory / trail / affordance formation
```

## Two Hypotheses

N08 intentionally keeps two hypotheses separate.

```text
Hypothesis A: serialized producer/policy memory
    Route use creates artifact-visible memory/trail attributes such as
    `memory_strength`. Later producers, candidate scoring, or route
    arbitration can read those serialized attributes. This path is useful for
    designing pheromone-like producer behavior and for identifying native policy
    requirements, but it may introduce quantities beyond the coherence field
    and loop dynamics.

Hypothesis B: native geometry-mediated trail memory
    Route use changes native LGRC geometry/topology/support state, such as by
    splitting an edge, inserting a node, changing node/edge geometry, changing
    local support shape, or changing a conductance-like metric that is itself
    part of the declared substrate. Future flux/routing changes because the
    substrate changed. The trail is a derived observable, not an independent
    memory substance.
```

Iterations 1-8 primarily explore Hypothesis A. They should not be treated as a
direct solution to Hypothesis B. If `memory_strength` remains an independent
scalar state, then it is producer/policy scaffolding, not pure native RC memory.
The stronger native route-memory problem remains open until the apparent trail
is expressed through existing coherence, packet/loop, topology, or geometry
state without an unaccounted extra quantity.

Native geometry-mediated acceptance should require:

```text
no independent memory_strength field
trail observable derived from node/edge/packet/topology state
route use changes geometry/topology/support through declared LGRC mechanisms
future routing changes because native flux follows changed geometry
all active coherence and packet budgets remain conserved
any relaxation/decay destination is explicit and conserved
```

## Scope

N08 is experiment-local unless a separate Phase 8/core implementation task is
opened. Scripts, configs, reports, and outputs live under:

```text
experiments/2026-05-N08-lgrc-memory-trail-affordance/
```

Do not change `src/*` for N08 without stopping and opening a separate Phase 8
task. Existing LGRC9V3 route-arbitration, candidate-route, candidate-set,
producer, packet, topology, surface-lineage, topology-state reabsorption,
snapshot, telemetry, and artifact-replay surfaces may be used, but N08 must not
silently redefine their semantics.

## Inherited Evidence

N08 should cite these prior results as source context, not as N08 evidence by
themselves.

```text
N05:
    strongest_supported_o_level = O5
    strongest_claim_ceiling = self_sustained_oscillator_candidate
    route_aspect_serialized = true
    O6 route-coupled oscillator blocked by
        missing_route_conductance_memory_policy

N06:
    strongest_supported_sc_level = SC6
    strongest_claim_ceiling = artifact_only_semantic_route_choice_candidate
    memory_or_trail_claim_allowed = false

N07:
    frozen_n07_ceiling = ID6
    frozen_long_horizon_c3_class = bounded_non_destructive_exchange
    runtime_identity_acceptance_claim_allowed = false
```

N05 provides carrier/oscillator background. N06 provides route-arbitration and
artifact-replay precedent. N07 provides identity/support anchors so route
memory is not merely a label.

N08 should cite the following N07 fields directly when memory is anchored to
identity/support context:

```text
frozen_long_horizon_c3_class = bounded_non_destructive_exchange
support_area_id
support_area_digest
source_support_area_digest
bounded_non_destructive_exchange trajectory records
claim-boundary fields
```

The N07 neutral absorber reservoir is not inherited as N08 memory. It may be
cited as compatible dual-basin substrate context only.

## Core Definition

For N08, memory means:

```text
a runtime-visible persisted state derived from prior route use or coherence
flow that later changes candidate-route evidence under a serialized policy.
```

That definition is the Hypothesis A working definition. Hypothesis B uses a
stricter definition: the persisted route trace must be a substrate
geometry/topology/support deformation or residue that future flux responds to
without reading an independent memory scalar.

The minimum positive causal chain is:

```text
committed route-use event
-> trail / affordance memory surface row
-> serialized decay or reinforcement update
-> candidate-route score component cites memory digest
-> native route-arbitration record selects according to memory-shaped score
-> artifact-only replay reconstructs the full chain
```

Memory must be observable through artifacts. A route that is selected because a
script remembered it is not N08 evidence.

### Route-Use Event Boundary

N08 distinguishes selection from use:

```text
route selection:
    native route-arbitration selected a candidate route.

route use:
    an N08 route-use event records that the selected route was actually
    consumed by the memory lane.
```

N06 SC6 is explicitly selection-only and pre-topology-commit. N08 may use N06
selection artifacts as source provenance, but MEM1 requires a new committed
route-use event record. For early N08 lanes, `committed` means the event is
ordered, serialized, budget-audited, digest-pinned, and eligible as a source
for memory formation. It does not require a topology event unless a later lane
explicitly chooses a topology-committing route-use fixture.

Required route-use fields:

```text
route_use_event_id
route_use_commit_status = committed
source_arbitration_record_digest
selected_candidate_route_digest
selected_route_id
route_aspect_digest
event_time_key
scheduler_event_index
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
route_use_event_digest
```

### Memory Surface Contract

N08 memory surfaces are experiment-local serialized records unless a later
Phase 8 task adds native memory surfaces. The storage format is JSON artifact
rows, not hidden process memory.

Default memory surface key:

```text
route_id
source_support_area_digest
target_support_area_digest
route_aspect_digest
memory_policy_id
```

The row field `memory_surface_key` is a canonical JSON object with exactly
those fields, not a scalar string. The companion digest is:

```text
memory_surface_key_digest = sha256(canonical_json(memory_surface_key))
```

Digest rule:

```text
memory_surface_digest =
    sha256(canonical_json(memory_surface_record_without_digest))
```

Every MEM2+ row must serialize either the full `memory_surface_state_snapshot`
or the relevant `memory_surface_rows` needed to replay later arbitration. A
digest without serialized state is not enough for MEM6.

### Memory Budget Semantics

N08 keeps two budget surfaces separate:

```text
node_plus_packet budget:
    physical coherence accounting. Must remain exact and cannot be repaired by
    memory bookkeeping.

memory budget:
    serialized trail/affordance strength accounting. It measures memory
    strength capacity and update consistency, not node coherence.
```

The default memory budget is a bookkeeping conservation surface:

```text
memory_budget_before
+ reinforcement_input
- decay_loss
- saturation_clamp_loss
== memory_budget_after
```

Decay loss and saturation clamp loss must be recorded. They are not coherence
deletion because memory strength is not node coherence.

`decay_loss` is an artifact-level signal attenuation quantity, not physical RC
flux. It has no implicit destination surface and must not be read as node
coherence, packet mass, or conserved substrate budget. If a later iteration
uses memory decay to transfer into coherence pockets, that transfer must declare
an explicit conserved destination surface and prove that the main
node-plus-packet RC budget remains exact. Without that destination, treating
`decay_loss` as physical flux is a divergent path and remains blocked.

Any conversion from memory strength into candidate score must be score evidence
only and must not modify node-plus-packet budget.

## RC Compatibility Boundary

N08 memory policies must preserve the RC closed-system interpretation:

```text
sum(active node coherence)
+ in_flight_packet_total
== conserved_budget_total
```

Allowed memory mechanisms:

```text
serialized route-use traces
serialized trail/affordance surface rows
explicit decay policy
explicit reinforcement policy
candidate-score component derived from memory surface state
budget-neutral memory bookkeeping
```

Forbidden mechanisms:

```text
hidden source terms
silent coherence injection
silent coherence deletion
preselected route ids
hidden route history arrays
report-side memory reconstruction
post-hoc thresholds
agency / intention / goal labels
```

If current LGRC cannot express a needed memory/trail surface as serialized
runtime-visible policy, N08 must record a native-policy blocker rather than
hiding the missing mechanism in fixture code.

### MEM4 Score Component Contract

N08 memory-shaped arbitration must use serialized candidate score components.
The preferred component names are:

```text
memory_trail_strength
memory_surface_digest_match
memory_recency_weight
memory_decay_adjusted_strength
```

Each memory-derived component must also be present in
`candidate_runtime_visible_inputs`, including:

```text
memory_surface_id
memory_surface_digest
memory_surface_state_snapshot_digest
memory_policy_id
route_use_event_digest
memory_event_time_key
```

The existing native invariant remains load-bearing:

```text
candidate_route_score == sum(candidate_score_components)
```

Iteration 1 must inventory native forbidden-input keys. Iteration 2 must reject
any memory component that appears in the forbidden-input set. A hidden memory
component is not allowed to become a route score.

## MEM Ladder

MEM levels are evidence classifications, not claim flags.

```text
MEM0:
    external/label-only memory; no runtime-visible route-use event.

MEM1:
    route-use event trace recorded with route id, selected candidate digest,
    event time, scheduler index, budget surface, and digest.

MEM2:
    trail or affordance memory surface exists after the route-use event and
    cites the route-use digest.

MEM3:
    memory surface updates through serialized decay or reinforcement policy,
    preserving budget accounting and replayable order.

MEM4:
    candidate-route score components cite the memory surface digest and alter
    route arbitration.

MEM5:
    repeated memory-shaped selection over multiple cycles; memory strengthens,
    decays, or redirects under controls without hidden steering.

MEM6:
    artifact-only replay reconstructs route use, memory updates, memory-shaped
    candidate scores, route arbitration, and controls with distinct blockers.
```

## Row Schema

Every N08 row should include:

```text
mem_level
mem_level_is_evidence_classification = true
claim_ceiling
claim_flags
source_artifacts
source_reports
route_id
route_use_event_digest
memory_surface_id
memory_surface_digest
memory_surface_key
memory_surface_key_digest
memory_policy_id
memory_policy_digest
decay_policy_id
reinforcement_policy_id
memory_surface_state_snapshot
memory_surface_state_snapshot_digest
candidate_route_digests
candidate_set_digest
selected_candidate_route_digest
rejected_candidate_route_digests
native_route_arbitration_record_digest
event_time_key
scheduler_event_index
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
memory_budget_surface
memory_budget_before
memory_budget_after
memory_budget_error
native_support_status
native_policy_blockers
visual_reference
visual_is_evidence_source
```

Claim flags must stay separate from MEM evidence classification.

## Claim Discipline

Allowed if supported by gates:

- route-use trace candidate;
- trail memory surface candidate;
- affordance memory surface candidate;
- decay/reinforcement memory candidate;
- memory-shaped route-selection candidate;
- repeated memory-shaped selection candidate;
- artifact-only trail-memory candidate.

Blocked in N08:

- ACO or colony-like behavior;
- agency or intention;
- goal-proxy regulation;
- RC identity collapse;
- runtime identity acceptance;
- locomotion-like behavior;
- biological pheromone behavior;
- personhood;
- unrestricted identity;
- unrestricted movement.

Required claim flags:

```json
{
  "memory_or_trail_claim_allowed": false,
  "aco_like_claim_allowed": false,
  "agency_claim_allowed": false,
  "agentic_like_claim_allowed": false,
  "ant_colony_claim_allowed": false,
  "intention_claim_allowed": false,
  "goal_proxy_regulation_claim_allowed": false,
  "semantic_choice_claim_allowed": false,
  "rc_identity_collapse_claim_allowed": false,
  "identity_acceptance_claim_allowed": false,
  "runtime_identity_acceptance_claim_allowed": false,
  "locomotion_like_claim_allowed": false,
  "biological_claim_allowed": false,
  "personhood_claim_allowed": false,
  "movement_claim_allowed": false,
  "unrestricted_identity_claim_allowed": false,
  "unrestricted_movement_claim_allowed": false
}
```

`memory_or_trail_claim_allowed` remains false until artifact-only replay closes
the MEM ladder. Even then, it is a route-memory/trail evidence claim only, not
ACO or agency.

Promotion criteria for the narrow N08 memory/trail evidence flag:

```text
MEM6 required
artifact-only replay passes
route-use events replay
memory surface state reconstructs
decay/reinforcement policies replay
memory-derived candidate scores recompute exactly
controls fail with distinct blockers
node-plus-packet and memory budgets pass
```

MEM4 or MEM5 may support a memory-shaped route-selection candidate, but
`memory_or_trail_claim_allowed` remains false until MEM6 closeout.

## Controls

N08 controls must fail with distinct primary blockers:

```text
hidden_route_history
missing_route_use_event
memory_surface_missing
memory_surface_digest_mismatch
memory_surface_poisoned
memory_policy_missing
memory_policy_hidden_preference
decay_policy_missing
reinforcement_policy_missing
candidate_score_memory_digest_missing
candidate_score_hidden_memory_input
arbitration_memory_order_invalid
memory_budget_discontinuity
node_plus_packet_budget_discontinuity
stale_memory_surface_read
cross_cycle_memory_leak
duplicate_memory_update
policy_disabled
producer_mutation_boundary_violation
no_memory_surface_read_by_arbitration
posthoc_memory_threshold_change
claim_promotion
```

Control distinction:

```text
hidden_route_history:
    a route history exists only in fixture/report code and is not serialized.

memory_policy_hidden_preference:
    the memory update policy is serialized but contains an undeclared A/B or
    route preference not derived from route-use evidence.
```

## Native Policy Blockers

Expected native-policy blockers may include:

```text
native_route_conductance_memory_policy_missing
native_trail_memory_surface_missing
native_memory_surface_serialization_policy_missing
native_memory_surface_keying_policy_missing
native_memory_budget_accounting_policy_missing
native_memory_cross_cycle_persistence_policy_missing
native_memory_decay_policy_missing
native_memory_reinforcement_policy_missing
native_memory_candidate_score_component_missing
native_memory_artifact_replay_validator_missing
```

These blockers are useful results. They identify what a later Phase 8/native
absorption pass would need to add.

## Planned Iterations

```text
Iteration 0:
    planning and handoff

Iteration 1:
    baseline and schema inventory. Inventory N05/N06/N07 source artifacts,
    available native route-arbitration fields, and missing native memory
    policy surfaces. Freeze the MEM ladder and claim flags.

Iteration 2:
    fixture manifest and route-use trace contract. Define route-use events,
    memory-surface rows, memory budgets, event ordering, and controls before
    running memory probes. Freeze memory surface storage, keying, digest,
    state-snapshot, score-component, budget, and route-use commitment
    semantics.

Iteration 3:
    MEM1 route-use trace. Emit source-backed route-use event traces from
    selected route artifacts without creating memory yet.

Iteration 4:
    MEM2 trail / affordance memory surface. Convert route-use traces into a
    persisted memory surface with digest and budget accounting.

Iteration 5:
    MEM3 decay / reinforcement update. Apply serialized decay and reinforcement
    policies to memory surface rows over ordered windows.

    Default policy shape:
        decay is exponential per memory window:
            strength_after_decay = strength_before * decay_factor
        reinforcement is saturating additive:
            strength_after = min(max_strength,
                                 strength_after_decay + reinforcement_amount)
        floor = 0.0
        max_strength = 1.0
        decay and reinforcement may occur in the same window only if the event
        order is serialized.

Iteration 6:
    MEM4 memory-shaped route arbitration. Candidate-route score components cite
    memory surface digests and alter native route selection. Require a
    counterfactual lane:
        same source/context/policy without memory component
        vs same source/context/policy with memory component.
    Record selected-route delta and memory_score_delta.

Iteration 7:
    MEM5 repeated memory-shaped selection. Show repeated cycles where memory
    strengthens, decays, or redirects selection under controls.

    Minimum cycle count is four, matching N06 SC5 repeated-context precedent.
    Record saturation, extinction, and competing-memory behavior:
        saturation plateau
        decay-to-floor / extinction
        two remembered routes competing
        convergence, bounded oscillation, or unresolved tie

Iteration 8:
    MEM6 artifact-only replay and closeout. Reconstruct the route-use ->
    memory -> arbitration chain from artifacts only and freeze the strongest
    Hypothesis A ceiling without ACO, agency, intention, or goal-regulation
    claims.

    Replay reads:
        N08 route-use events
        memory surface rows / snapshots
        decay and reinforcement policy records
        candidate route records
        candidate set records
        native route-arbitration records
        scheduled/processed packet records if the fixture uses them

    Replay failures:
        missing route-use event
        digest mismatch
        memory state reconstruction mismatch
        score component mismatch
        event-order inversion
        stale memory read
        duplicate update
        budget discontinuity
        claim promotion

Iteration 9:
    Native geometry trail baseline. Freeze the Hypothesis B question and
    inventory native LGRC mechanisms that can change routing without an
    independent `memory_strength` quantity:
        topology event / edge split / inserted node
        fixed-geometry node or edge parameter change
        support-shape or local coupling geometry change
        packet/loop residue visible in existing state
    Record which mechanisms are already available and which require Phase 8.
    Do not run memory-shaped scoring in this iteration.

Iteration 10:
    Geometry-mediated trail formation probe. Prior route use creates a declared
    topology or geometry trace, such as an inserted node on an edge, a modified
    edge geometry, or a support deformation. The trace must be represented in
    native topology/geometry/support state, not in `memory_strength`.
    Verify exact node-plus-packet conservation and artifact-visible lineage.
    If the trace uses a zero-coherence inserted node, record it as a
    theory-caveated boundary probe rather than as a theory-clean active carrier
    or reinforcement geometry.

Iteration 11:
    Future flux/routing response to geometry trace. Run the same source/context
    with and without the geometry trace and classify what future flux/routing
    does around the trace: leakage/absorption, avoidance/no-response, or a
    stronger response from a positive-coherence or rebalanced geometry
    candidate. Reject any hidden route preference, score-only memory input, or
    independent memory scalar. If the response metric is only diagnostic
    because no native route-conductance memory policy exists, record that
    blocker explicitly.

Iteration 11-A:
    Positive-coherence geometry route-arbitration response. Use the Iteration
    11 leakage/absorption result to test a theory-clean positive-coherence
    trace. Compare no-trace, zero-trace, and positive-trace lanes. Native route
    arbitration must fail closed without geometry evidence, reject the
    zero-coherence absorber as reinforcement, and select the positive trace
    only from runtime-visible geometry score components. This may support a
    positive-coherence geometry route-response candidate, but pure
    flux/conductance trail memory remains blocked until native route-
    conductance memory policy exists.

Iteration 12:
    Native trace persistence and relaxation. Test whether the positive
    geometry route-response candidate from Iteration 11-A persists over
    repeated windows when the declared geometry is held fixed. Classify this
    separately from adaptive trail memory: static geometry persistence may
    support a route-response persistence candidate, but it does not by itself
    prove route conductance memory, strengthening, or pure flux trail memory.
    If a relaxation/decay quantity moves mass, require an explicit conserved
    destination surface. If relaxation is only policy/geometry bookkeeping,
    require a serialized policy and record it as non-flux. Without native route
    conductance update/relaxation policy, keep pure flux claims blocked by
    `native_route_conductance_memory_policy_missing`.

Iteration 13:
    Native geometry-mediated trail replay and closeout. Reconstruct route use,
    geometry/topology/support trace formation, future flux/routing response,
    persistence/relaxation, and controls from artifacts only. Freeze whether
    Hypothesis B reached a native geometry-mediated trail candidate or remains
    blocked by missing native mechanisms.
```

## Closeout Target

The strongest intended Hypothesis A closeout is:

```text
artifact_only_route_memory_or_trail_affordance_candidate
```

The strongest intended Hypothesis B closeout is:

```text
static_positive_geometry_route_response_persistence_candidate
```

The stronger Hypothesis B target remains blocked by:

```text
native_route_conductance_memory_policy_missing
```

Iteration 8 closes only the serialized producer/policy path. Iteration 13
closes the native geometry-mediated branch as a bounded
producer/scaffold-to-native-policy discovery result, not as native
route-conductance trail memory. N08 should hand off to N09-N11 with the
Hypothesis A ceiling explicit, the Hypothesis B bounded ceiling explicit, and
all stronger claim boundaries clean.

N09-N11 dependency:

```text
N09 goal-proxy regulation requires at least MEM4 and preferably MEM6.
N10 agentic-like integration requires memory-shaped choice evidence from N08.
N11 broader/general agentic-like integration should not consume memory/trail
claims unless N08 closed them cleanly.
Later locomotion-like dynamics should not consume memory/trail claims unless
the N10/N11 integration boundary remains clean.
```
