# N04 Movement Ladders Handoff

Updated: 2026-05-23.

This handoff records the N04 resume point after Iteration 23 closed the
topology-mutating taxonomy tranche.

## Current Status

N04 has completed the M-taxonomy/topology continuation through Iteration 23,
including the Iteration 21-B native route-arbitration rerun and Iteration 22-B
identity-boundary rerun.

Current ceiling:

```text
claim_ceiling = topology_mutating_movement_candidate
geometry_scope = topology_mutating
substrate_class = port_graph
adaptive_topology_entry_allowed = true
topology_mutating_movement_claim_allowed = true
movement_claim_allowed = false
```

This means native LGRC9V3 can now run the strict topology-mutating movement
candidate chain:

```text
committed topology event
-> transported native pulse-substrate surface row
-> topology-state reabsorption record
-> active state and packet ledger rebased together
-> producer reads transported surface digest plus reabsorption digest
-> post-topology packet work scheduled
-> step() processes scheduled departure/arrival
-> node-plus-packet budget remains exact
-> artifact-only replay validates the chain
```

Iteration 20 adds:

```text
3/3 matched repeatability lanes pass
matched reversed topology-mutating lane passes
lineage-accounted perturbation lane passes
multiple committed topology events pass at runtime/budget level
multi-topology artifact replay passes after Phase 8 time-scoped lineage replay
```

Iteration 21 adds:

```text
competing topology-mutating continuations are executable when supplied
route A and route B both artifact-replay and preserve exact budget
native LGRC route arbitration is not exposed
selection still enters through experiment-supplied topology-event arguments
native_lgrc_route_arbitration_candidate is blocked
```

Iteration 21-B adds:

```text
candidate route sets are emitted from committed runtime-visible evidence
native route arbitration selects exactly one route
selected topology event references the route-arbitration record
lineage, reabsorption, producer scheduling, and step() consume the selection
artifact-only route-arbitration replay passes
semantic choice, agency, RC identity collapse, and identity acceptance remain blocked
```

Iteration 22 adds:

```text
topology-aware continuity of surface evidence passes
active state and packet ledger continuity through topology mutation passes
producer scheduling from current reabsorbed evidence passes
artifact-only replay passes
RC identity through topology mutation is not validated
rc_identity_through_topology_mutation_candidate is blocked
```

Iteration 22-B adds:

```text
identity boundary is rerun with native route-arbitrated topology
selected topology event comes from native route arbitration
route, lineage, reabsorption, producer scheduling, and step() replay artifact-only
stable RC coherence-basin identity is still not serialized
attractor-basin invariance through topology mutation is still not validated
rc_identity_through_native_route_arbitrated_topology_candidate is blocked
```

Iteration 23 closes:

```text
topology_mutating_movement_candidate is frozen as the current N04 ceiling
taxonomy inventory and tag schema include the final 21-B and 22-B rows
native route arbitration is runtime support, not semantic choice
RC identity through topology remains blocked
handoff is ready for a new tranche decision
```

This does not mean:

```text
native LGRC choice selection
RC identity collapse
semantic choice
agency
locomotion-like behavior
biological behavior
identity acceptance
movement inherited from N03
unrestricted movement
```

Those remain blocked.

## Evidence Path

The current path is:

```text
Iterations 5-12:
    fixed-substrate tranche, M0-M6 evidence, native same-fixture M6 candidate.

Iterations 13-14:
    taxonomy inventory and class/tag freeze.

Iteration 15 series:
    S0 stress, perturbation, tolerance, and shock-resilient geometry probes.

Iterations 16-17:
    corridor and ring transfer/recovery probes.

Iteration 18 series:
    S3 grid route, turn, two-input/two-output, composed 1D fork,
    balanced local preference, integrated 2D composed gate.

Iteration 19:
    role-based S3-to-S7 fixed-port mapping contract.

Iteration 19-A:
    S7 fixed-port composed-gate execution passes.

Iteration 19-B:
    topology-lineage/adaptive gate fails closed at surface-lineage support.

Phase 8 surface-lineage continuation:
    native causal pulse-substrate surface lineage transport closes 19-B's
    runtime blocker.

Iteration 19-C:
    adaptive-topology entry candidate passes.

Iteration 19-D:
    strict topology-mutating movement fails closed at active-state/packet-ledger
    reabsorption.

Phase 8 topology-state reabsorption continuation:
    active state and packet ledger can be rebased together after committed
    topology events.

Iteration 19-E:
    strict topology-mutating movement candidate passes.

Iteration 20:
    repeatability, reversed-direction, and lineage-accounted perturbation
    stress passes; multi-topology runtime/budget stress and artifact-only
    replay pass after Phase 8 time-scoped lineage replay hardening.

Iteration 21:
    native LGRC route-arbitration promotion is blocked at
    native_lgrc_topology_route_selection_not_exposed.

Iteration 21-B:
    after Phase 8 native route arbitration, the old route-selection exposure
    blocker is resolved as runtime route arbitration; semantic choice, agency,
    RC identity collapse, and identity acceptance remain blocked.

Iteration 22:
    RC identity-through-topology promotion is blocked at
    rc_identity_basin_invariance_not_validated_across_topology_mutation.

Iteration 22-B:
    native route-arbitrated topology continuity passes, but RC identity-through
    topology remains blocked at
    rc_identity_basin_invariance_not_validated_across_topology_mutation.

Iteration 23:
    topology-mutating taxonomy tranche is closed at
    topology_mutating_movement_candidate.
```

## Source Artifacts

Primary current source of truth:

```text
outputs/n04_taxonomy_continuation_closeout.json
reports/n04_taxonomy_continuation_closeout.md

outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json
reports/n04_iter19e_topology_mutating_movement_after_state_reabsorption.md

outputs/n04_iter20_topology_mutating_repeatability_stress.json
reports/n04_iter20_topology_mutating_repeatability_stress.md

outputs/n04_iter21_native_lgrc_choice_selection_boundary.json
reports/n04_iter21_native_lgrc_choice_selection_boundary.md

outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json
reports/n04_iter21b_native_lgrc_route_arbitration_rerun.md

outputs/n04_iter22_identity_through_topology_mutation_boundary.json
reports/n04_iter22_identity_through_topology_mutation_boundary.md

outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json
reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md

outputs/n04_taxonomy_inventory_v1.json
reports/n04_taxonomy_inventory_v1.md

outputs/n04_taxonomy_tag_schema_v1.json
reports/n04_taxonomy_class_separation_v1.md
```

Relevant preceding N04 artifacts:

```text
outputs/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.json
reports/n04_iter19c_s7_adaptive_gate_with_native_surface_lineage.md

outputs/n04_iter19d_topology_mutating_movement_probe.json
reports/n04_iter19d_topology_mutating_movement_probe.md

outputs/n04_iter19a_s7_fixed_port_execution_report.json
reports/n04_iter19a_s7_fixed_port_execution_report.md
```

Relevant Phase 8 closeouts:

```text
implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json
implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.md

implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json
implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md

implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json
implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md

implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json
implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.md
```

Historical but still useful visual/reference artifacts:

```text
outputs/m_taxonomy_visual_reference.json
reports/m_taxonomy_visual_reference.md
outputs/m_taxonomy_visual_reference/index.html
```

## Closed Tranche

Iterations 19-23 are closed as:

```text
s7_port_graph_and_topology_mutating_movement
```

Closed result:

```text
topology_mutating_movement_candidate
```

The result is candidate-scoped because it proves native topology-mutating
packet/surface/state behavior under the N04 gate, not general locomotion,
agency, choice, or identity acceptance.

## Resume Point

Resume at:

```text
Choose the next post-topology-mutating tranche.
```

Closed Phase 8 branch:

```text
Phase-8-LGRC9-NativeRouteArbitrationPlan.md
Phase-8-LGRC9-NativeRouteArbitrationChecklist.md
Phase-8-LGRC9-NativeRouteArbitrationCloseout.md
```

Suggested first checks:

```text
start from outputs/n04_taxonomy_continuation_closeout.json
preserve topology_mutating_movement_candidate as the inherited N04 ceiling
do not treat native route arbitration as semantic choice
do not treat 22-B continuity as RC identity acceptance
pick a new tranche explicitly before adding new probes
```

## Planned Next Topics

```text
Potential next tranche:
    N05 coherence waves / delayed oscillators / coherence circuits first.
    Later branches should open semantic choice, RC identity/invariance,
    memory/trail formation, and goal-proxy regulation before any integrated
    agentic-like or locomotion-like claim.
```

## Experiment Split Guidance

N04 should now be treated as the movement parent/baseline experiment. It has
closed the movement/topology-mutating tranche at
`topology_mutating_movement_candidate`; later work may cite that ceiling as an
input, but should not overwrite it.

The whole N05-N11 continuation is recorded at:

```text
../../N05-N11-LGRC-AgenticLikeFoundationRoadmap.md
```

Choice, RC identity/invariance, memory/trail formation, goal-proxy regulation,
agentic-like integration, and locomotion-like dynamics are adjacent to
movement, but each has enough independent ladder structure that it should open
as its own experiment if pursued seriously. Before those, open N05 to establish
the lower-level wave/oscillator primitives they may need.

ACO-like behavior should not be opened as a single immediate branch. Split it
into smaller prerequisites first: route choice, identity anchors, and
memory/trail or affordance formation. Otherwise "nest", "food", and "trail"
are only fixture labels.

```text
N04:
    movement taxonomy and topology-mutating movement candidate baseline

N05:
    coherence waves, delayed pulses, reflection/amplification, and oscillator
    circuits

N06:
    choice / route-selection / semantic choice ladder

N07:
    RC identity, attractor invariance, and identity-acceptance ladder

N08:
    memory / trail / affordance formation ladder

N09:
    goal-proxy regulation ladder

N10:
    agentic-like integration ladder

N11:
    broader/general agentic-like integration ladder

Later:
    locomotion-like dynamics ladder, if still useful after N10/N11
```

Highway/path aftereffect can go either way. If it remains a movement evidence
extension, it can be an N04 follow-up. If it develops into path memory,
affordance, or highway-formation taxonomy, it should become its own experiment.

Decision rule:

```text
If the next work needs its own inventory, ladder rungs, controls, and claim
flags, start a new experiment and cite N04 as source evidence.

If the next work only adds another stress or visualization pass for the closed
movement candidate, keep it as an N04 follow-up.
```

N05 should not try to prove ants, semantic choice, RC identity, or locomotion.
Its job is to prove the primitive coherence-circuit behavior:

```text
source emits a structured pulse
pulse travels with causal delay
target reflects or amplifies the pulse
return pulse is budget-accounted against a reservoir/surplus source
cycles repeat as artifact-replayable oscillation evidence
```

This makes N05 a useful prerequisite for later choice, invariance, memory,
regulation, agentic-like integration, and locomotion-like experiments, but not
a claim promotion from N04.

Agentic-like behavior should remain its own explicit ladder, not a label
attached just because several mechanisms work:

```text
A0:
    passive relaxation or externally scripted response

A1:
    state-triggered action from runtime-visible evidence

A2:
    native choice among alternatives

A3:
    memory-shaped choice through recorded trail/affordance state

A4:
    goal-proxy regulation of a runtime-visible condition

A5:
    identity-continuous regulation across cycles, perturbations, or topology
    changes

A6:
    cross-context adaptive policy with artifact-only replay and no hidden
    experiment-side steering
```

Even at A6, the conservative label is `agentic_like_dynamics_candidate`, not
`agent`.

## Do Not Overread

The current result means:

```text
post-topology packet work can be scheduled and processed from lineage-current,
reabsorbed native state under a committed topology event.
```

It does not mean:

```text
LGRC performs native choice/collapse
the system has agency or locomotion
the moved entity has passed RC identity acceptance
movement claims are inherited from N03
N04 taxonomy is closed forever
```
