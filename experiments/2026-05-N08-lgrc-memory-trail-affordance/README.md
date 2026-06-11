# N08 LGRC Memory Trail Affordance

N08 asks whether previous coherence flow can leave a serialized,
runtime-visible memory, trail, or affordance state that later shapes route
selection without hidden experiment-side steering.

The core question is:

```text
Can route history become a runtime-visible causal surface that persists,
decays, reinforces, and later influences native route arbitration?
```

N08 now explicitly tracks two hypotheses:

```text
Hypothesis A: serialized producer/policy memory
    Route use creates artifact-visible trail/affordance attributes. Producers
    or candidate-scoring policies can later read those attributes. This is
    useful for designing pheromone-like scheduling behavior, but it introduces
    memory quantities outside the pure coherence field unless they are only
    treated as score evidence.

Hypothesis B: native geometry-mediated trail memory
    Route use changes existing LGRC geometry/topology or node/edge support
    structure. Future flux/routing changes because the substrate geometry has
    changed. The trail is a derived observable of coherence/loop/geometry
    dynamics, not an independent `memory_strength` substance.
```

Iterations 1-8 primarily explore Hypothesis A. They are not sufficient by
themselves to prove Hypothesis B or a pure coherence/flux pheromone mechanism.
If `memory_strength` remains an independent scalar surface, it should be
treated as producer/policy scaffolding, not as native RC memory. A pure native
route-memory result must avoid unaccounted quantities beyond the coherence
field, packet/loop dynamics, and declared topology/geometry state.

N08 is not ACO, agency, intention, goal regulation, locomotion, or biological
pheromone behavior. It is the memory/trail layer required before those stronger
interpretations can even be considered.

## Roadmap Position

```text
N05:
    coherence waves and oscillators
    strongest O-level = O5
    O6 blocked by missing_route_conductance_memory_policy

N06:
    artifact-only semantic route-choice candidate
    strongest SC-level = SC6
    memory/trail remains blocked

N07:
    artifact-only, source-specific ID6 evidence classification for bounded
    non-destructive dual-basin exchange
    runtime identity acceptance remains blocked

N08:
    memory / trail / affordance formation
```

N08 uses N05 oscillation/circuit evidence as a carrier background, N06
route-arbitration evidence as a selection surface, and N07 identity/support
evidence as the anchor that prevents "source", "target", "home", "route", or
"affordance" from being only fixture labels.

## Route-Use Boundary

N08 distinguishes route selection from route use.

```text
route selection:
    a native route-arbitration record selects one candidate route.

route use:
    a committed, ordered event records that the selected route was actually
    consumed by the fixture lane as the source for memory formation.
```

N06 SC6 is selection-only and pre-topology-commit. N08 may cite N06 selection
artifacts as source provenance, but MEM1 requires a new N08 route-use event
record that references the selected candidate digest and declares the route
consumed for memory formation. If a future N08 lane needs committed topology or
packet execution rather than selection-consumption evidence, that lane must say
so explicitly before it runs.

## Memory Definition

For N08, memory means a persisted runtime-visible state derived from prior
route use or coherence flow.

Minimum valid chain:

```text
route-use event
-> trail / affordance memory surface
-> decay or reinforcement update
-> later candidate-route score component
-> native route-arbitration record
-> artifact-only replay
```

Invalid memory sources:

```text
hidden fixture arrays
report-side route history
experiment if/else
preselected route ids
post-hoc threshold changes
unserialized Python state
semantic labels without source events
```

## Memory Surface Contract

N08 memory surfaces are experiment-local serialized records unless a later
Phase 8 task adds native memory surfaces. The default `memory_surface_key` is
a canonical JSON object, not a scalar string, with these fields:

```text
route_id
source_support_area_digest
target_support_area_digest
route_aspect_digest
memory_policy_id
```

The key digest is:

```text
memory_surface_key_digest = sha256(canonical_json(memory_surface_key))
```

The memory digest is SHA-256 over canonical JSON with sorted keys and excludes
the digest field itself. Every memory-shaped arbitration row must serialize the
memory surface rows or a `memory_surface_state_snapshot` sufficient for
artifact-only replay.

The memory budget is a bookkeeping/conservation surface for memory strength,
not a coherence source. It measures serialized trail/affordance strength and
must remain separate from node-plus-packet coherence budget. Decay and
reinforcement may redistribute or update memory strength only through declared
policy; they must not create or remove node coherence.

For Hypothesis B, the stronger native acceptance condition is different:

```text
no independent memory_strength field
trail observable derived from node/edge/packet/topology state
route use changes geometry/topology/support in a conserved way
future routing changes because native flux follows the changed substrate
decay or relaxation has an explicit conserved destination if it moves mass
```

## MEM Ladder

The MEM ladder is evidence classification only. It does not set claim flags.

```text
MEM0:
    external/label-only memory. No runtime-visible route-use history.

MEM1:
    route-use event trace recorded with source route, event time, budget, and
    digest.

MEM2:
    persistent trail or affordance surface exists after the route-use event.

MEM3:
    memory surface updates by serialized decay or reinforcement policy.

MEM4:
    route arbitration reads memory state as a candidate score component.

MEM5:
    repeated memory-shaped route selection occurs over multiple cycles with
    controls.

MEM6:
    artifact-only replay reconstructs the route-use -> memory update -> route
    arbitration chain and all controls fail with distinct blockers.
```

## Claim Boundary

Allowed if supported by gates:

```text
route-use trace candidate
trail memory surface candidate
affordance memory surface candidate
decay/reinforcement memory candidate
memory-shaped route-selection candidate
artifact-only trail-memory candidate
```

Blocked in N08:

```text
ACO or colony-like behavior
agency
intention
goal-proxy regulation
identity acceptance
RC identity collapse
locomotion-like behavior
biological pheromone behavior
personhood
unrestricted movement
unrestricted identity
```

## Compatibility With RC Theory

N08 memory policies must be compatible with the RC closed-system boundary. A
memory update may redistribute, persist, decay by explicit policy, or influence
candidate scores through serialized runtime-visible state. It must not inject
hidden coherence, delete budget silently, preselect a route, or emit agency.

The strongest intended N08 closeout is:

```text
artifact_only_route_memory_or_trail_affordance_candidate
```

not:

```text
ant_colony_behavior
agentic_like_behavior
agency
intention
```

## Current Closeout

N08 now has two separated closeouts.

```text
Hypothesis A:
    ceiling = artifact_only_route_memory_or_trail_affordance_candidate
    memory_or_trail_claim_allowed = true
    scope = artifact_only_serialized_producer_policy_route_memory_or_trail

Hypothesis B:
    ceiling = static_positive_geometry_route_response_persistence_candidate
    blocker = native_route_conductance_memory_policy_missing
    native_geometry_mediated_trail_claim_allowed = false
    pure_coherence_flux_trail_claim_allowed = false
```

The Hypothesis B result is a roadmap-aligned producer/scaffold-to-native-policy
discovery result. It shows that declared positive geometry can shape native
route arbitration and persist as a static route response. It does not show
native route-conductance update, strengthening, relaxation, or pure flux trail
memory.

## Native Scope

N08 is experiment-local unless a separate Phase 8/core task is opened.
Existing native route-arbitration, causal surface, packet, topology, snapshot,
telemetry, and artifact-replay infrastructure may be used. Missing native
memory/trail policy support must be recorded as a blocker, not hidden inside
fixture code.

## Planned Continuation

Iterations 1-8 cover Hypothesis A, the serialized producer/policy memory
ladder. The native geometry-mediated branch continues after that:

```text
Iteration 9:
    native geometry trail baseline and mechanism inventory

Iteration 10:
    geometry/topology/support trace formation from prior route use, with
    zero-coherence traces treated as theory-caveated boundary probes

Iteration 11:
    future flux/routing response classification around the trace: leakage,
    avoidance/no-response, or positive-coherence design direction

Iteration 11-A:
    positive-coherence geometry route-arbitration response. Test whether a
    conserved positive trace can shape native route arbitration through
    runtime-visible geometry evidence without `memory_strength`.

Iteration 12:
    static positive geometry route-response persistence and relaxation
    boundary audit. Repeated windows may show that a fixed positive geometry
    keeps shaping route arbitration, but this is not adaptive trail memory
    unless native conductance update/relaxation policy exists.

Iteration 13:
    artifact-only replay and closeout for the native geometry-mediated branch
```

This branch seeks `native_geometry_mediated_route_trail_candidate`, not an ACO,
agency, intention, locomotion, biological, or unrestricted movement claim.
