# Hypothesis A: Serialized Producer/Policy Memory

## Statement

Route use creates artifact-visible memory or trail attributes, such as
`memory_strength`. Later producers, candidate-scoring policies, or route
arbitration can read those serialized attributes and use them as
runtime-visible evidence for route selection.

## Mechanism

The tested mechanism is:

```text
committed route-use event
-> serialized memory surface row
-> decay/reinforcement update
-> memory-derived candidate score components
-> native route-arbitration record
-> artifact-only replay
```

The memory surface is experiment-local serialized state. It is not node
coherence, packet mass, or physical flux.

## Implementation Result

Hypothesis A creates an ACO-like producer design pattern for route memory on
top of native RC/LGRC substrates.

The reusable pattern is:

```text
route use
-> serialized trail/memory row
-> decay/reinforcement update
-> memory-derived candidate score component
-> native route-arbitration bias
-> artifact-only replay
```

This is useful if a future experiment wants to add ACO-like producers above
native RC. The producer can use the serialized memory surface as route-history
evidence, while the runtime still preserves the producer/step boundary and
keeps the physical node-plus-packet budget separate from memory bookkeeping.

What this creates:

```text
artifact-validated producer-side route-memory model
pheromone-like scheduling scaffold
replayable trail-strength update contract
candidate-score integration pattern for route arbitration
control set for hidden preference, stale memory, duplicate update, budget
    discontinuity, and claim promotion
```

What this does not create:

```text
native geometry-mediated trail memory
pure coherence/flux pheromone field
biological pheromone behavior
ant-colony optimization
agency or intention
goal-proxy regulation
```

## Relation To Other Mechanisms

This branch is pheromone-like in structure because prior route use leaves a
trace that later biases route selection. It is not ant-colony optimization:
there are no ants, colony dynamics, biological pheromones, food/nest semantics,
or stochastic colony traversal.

This branch is not reinforcement learning. It does not optimize a reward
function, value function, policy gradient, Q-table, or loss. It applies an
explicit serialized update rule.

This branch resembles graph or neural weight updates only at the level of
"stored route value influences future routing." The stored value is not a
native graph geometry or neural weight unless a later branch encodes it into
declared LGRC substrate structure.

## Evidence

Iterations 1-8 close this branch.

Strongest result:

```text
MEM6 artifact-only replay
ceiling = artifact_only_route_memory_or_trail_affordance_candidate
```

Source closeout:

```text
outputs/n08_iteration_8_mem6_closeout.json
reports/n08_iteration_8_mem6_closeout.md
```

Iteration 8 reconstructs the Iteration 7 repeated route-use, memory-update,
candidate-score, candidate-set, and route-arbitration chain from exported
artifacts only.

## Claim Boundary

Allowed after Iteration 8:

```text
memory_or_trail_claim_allowed = true
scope = artifact_only_serialized_producer_policy_route_memory_or_trail
```

Still blocked:

```text
native_geometry_mediated_trail_claim_allowed = false
pure_coherence_flux_trail_claim_allowed = false
aco_like_claim_allowed = false
agentic_like_claim_allowed = false
agency_claim_allowed = false
ant_colony_claim_allowed = false
biological_claim_allowed = false
goal_proxy_regulation_claim_allowed = false
identity_acceptance_claim_allowed = false
intention_claim_allowed = false
locomotion_like_claim_allowed = false
movement_claim_allowed = false
personhood_claim_allowed = false
rc_identity_collapse_claim_allowed = false
runtime_identity_acceptance_claim_allowed = false
semantic_choice_claim_allowed = false
unrestricted_identity_claim_allowed = false
unrestricted_movement_claim_allowed = false
```

## Open Limitation

Because `memory_strength` remains an independent serialized score surface, this
branch does not prove pure native RC memory. It is useful producer/policy
scaffolding and a source-backed design pattern for later native mechanisms.
