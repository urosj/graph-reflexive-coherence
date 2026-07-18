# N31 Iteration 9-C.2 - Native Exact-History Constitutive Closure

## Result

```text
status = passed
acceptance_state = accepted_generalized_relation_and_native_restoration_DR2_and_LGRC_faithful_producer_step_provisional_DR4_pending_I10_with_native_runtime_lane_DR0_and_deferred_conditional_naturalization_requirements_recorded
candidate = C_native_exact_history_constitutive_closure
relation/carrier lane = DR2
producer extension lane = provisional_DR4_pending_I10
native runtime lane = DR0
highest observed evidence ceiling = DR4
highest observed evidence status = provisional_pending_I10
LGRC-faithful producer step executed = true
native candidate extension supported = false
RCAE admission = blocked until DR5 and reusable provider contract
next action = Iteration 10 added-mechanism replay and controls
```

## What N31 Could Establish

C.2 replaces C.1's fixture matcher with a structural relation. A committed
arrival on the registered oriented route contributes transferred coherence.
Later committed arrivals on other physical edges incident to that route's
source advance causal distance. The relation consumes packet-processing order,
amount, edge, orientation, and registered route support; it does not consume
event IDs, packet IDs, lineage labels, absolute times, scheduler indices, or
fixture-specific node numbers.

The generalized relation forms at
`S=0.9` and the progressed history
derives `S=0.6265625`. Native
`LGRC9V3.load()` round trips preserve both values exactly. Identifier, lineage,
clock, semantic-label, wrong-direction interspersion, and role-preserving
renumbering controls leave the value unchanged; removing a real progression
receipt changes it predictably; duplicate committed identity fails closed; and
injected `S` has no authority.

These gates support a **generalized relation/carrier lane at `DR2`**: formation
from native serialized history plus exact native restoration. This is stronger
than a contract-only `DR0` result, but it is not a native runtime extension.

The operational source is **native discrete coherence-current history**. Packet
amount represents transferred coherence, edge and orientation represent current
support and direction, and committed record order supplies causal ordering.
Equivalence to a broader continuous `J_C` representation is not established.

The current distance is the count of qualifying committed arrivals. Therefore
packetization invariance is still open: one `0.10` progression packet has not
yet been compared with two `0.05` packets under matched integrated coherence
and physical interval. Native admission must either prove equal `S` or declare
event granularity physically load-bearing. Integrated local activity or a
registered proper-time distance is the preferred future interpretation.

## What Susceptibility Means Here

`S` is a bounded multiplier on native conductance, not an enhancement beyond
native geometry:

```text
S = 1.0   unattenuated native conductance
S = 0.5   unformed candidate-mode conductance floor
formation reduces candidate attenuation
relaxation returns toward the candidate floor
```

The weakening is **activity-indexed local susceptibility relaxation**. It does
not proceed during quiescence or from wall-clock time. Route use reinforces the
relation; other committed incident activity advances attenuation. Generic
passive or autonomous temporal decay remains unsupported. A feature-on,
history-absent producer/runtime control at the `S=0.5` floor remains pending.

## LGRC-Faithful Producer Step

The existing examples establish a producer/executor pattern: producer logic
may inspect current LGRC state and schedule causal work, while `LGRC9V3.step()`
owns packet debit, in-flight accounting, arrival credit, and history emission.
C.2 uses that same boundary rather than requiring all candidate logic inside
the library's current `step()` implementation.

For both the formed and progressed histories, an experiment-owned candidate
step derives `S`, runs native GRC9V3 conductance/potential/flux kernels on a
state copy, converts the oriented flux into a preregistered packet amount, and
schedules one public LGRC packet departure. It does not mutate live
conductance, node coherence, or packet state. Two ordinary `LGRC9V3.step()`
calls then execute departure and arrival.

The equal reduced-state branches schedule different packet amounts:

```text
formed history packet = 0.04412859842731302
progressed history packet = 0.0370241918428932
```

In both rows, source debit equals packet amount, receiver credit equals packet
amount, and node-plus-packet coherence remains invariant. The completed packet
enters native history and changes the next derived relation. This supports a
**producer-mediated candidate-extension lane at provisional `DR4` pending
I10**: generalized formation, native restoration, producer-mediated weakening,
causal transport, and one feedback derivation. It is stronger than C.1's
diagnostic-only wrapper because transport actually executes and changes native
state.

The exact causal chain still requires direct mediation controls. A common-`S`
clamp, derived-`S` bypass, same-`S`/different-history comparison, and
same-history/recomputed-`S` comparison remain unrun. Those controls must prove
that the packet split is specifically caused by
`history -> S -> geometry -> flux -> packet`, not hidden branch logic.

The producer uses `q_packet=max(0,J_e)*0.25`. The coefficient is preregistered
and not outcome-tuned, but its physical or numerical meaning is unresolved.
Before native admission it must become a dimensioned integration or
packetization interval, with zero/negative flux, insufficient-source,
source-bound, and unit-closure controls.

Only one feedback depth has been demonstrated:

```text
transport -> changed native history -> second S derivation
```

A second `S -> geometry -> transport -> history` cycle, saturation behavior,
double-counting rejection, cascade bounds, and long-run nonnegative coherence
remain pending. The present positive reinforcement is bounded by `S_max`, but
multi-cycle stability has not been established.

## Why The Native Runtime Lane Remains DR0

C.2 asks for a native loop that the current accepted LGRC9V3 runtime does not
implement: serialized packet history must determine a route susceptibility,
ordinary `LGRC9V3.step()` must consume that relation as constitutive geometry,
the resulting flux must cause an actual conservative packet transition, and
that current must enter the history used by the next derivation.

The current runtime already serializes `packet_processing_log` and routes
arrival-triggered work through its ordinary local-update path. It does not,
however, derive susceptibility from that history or rebuild and consume
history-conditioned conductance, potential, and flux during the ordinary step.
That is the precise native gap. N31 is not authorized to change `src/*`, so it
cannot execute the runtime-consumption lane honestly.

The producer step is LGRC-faithful, but it is still experiment-owned candidate
logic. It therefore cannot upgrade `existing_native_support`, claim that the
current library's ordinary step derives susceptibility, or raise the native
runtime lane above `DR0`. Likewise, the weakening trajectory is
producer-mediated: its progression packets were scheduled by I9-C rather than
generated by an ordinary autonomous native progression rule.

Native ownership does not require all logic to live literally inside
`LGRC9V3.step()`. Either an integrated native step or a canonical library-owned
producer plus the native executor may qualify. In both cases the provider must
be library-owned, specified, invoked canonically without an experiment harness,
fully restored by provider identity, default-off, derived-only, and
conservative.

## Frozen Native Contract

The future native runtime lane starts at `DR0` and must implement:

```text
native discrete coherence-current history
-> exact derived S_e with no independent authority
-> native effective conductance
-> native potential and flux
-> native packet admission and transport
-> conservative C update
-> changed packet/current history
-> next S_e derived from that history
```

The relation may consume transferred coherence amount, physical edge and
orientation, committed event kind, causal order or local proper-time distance,
and registered route support. It may not causally consume event or packet IDs,
semantic lineage labels, absolute scheduler indices, hard-coded timestamps, or
fixture node numbers. A removable exact cache is allowed; authoritative stored
`S` is not.

Topology lifecycle is unresolved. Edge deletion/recreation, orientation
reversal, parallel replacement, route-source change, and topology-version
change need a frozen invalidation, versioned-identity, or explicit-migration
policy. Historical contributions may never silently attach to a reused ID.

Exact full-history scanning also remains a scaling debt. An incremental cache
is acceptable only if full recomputation is exact, cache removal is neutral,
injection has no authority, mismatches fail closed, identity includes relation
parameters and topology version, and pruning has an explicit cutoff/error
contract.

## Handoff

The generated handoff is a deferred conditional naturalization record, not an
implementation selection. It freezes the required default-off runtime surface,
canonical provider/executor integration, conservative transport, derived-only
telemetry, invariance controls, and disabled-baseline conformance. It does not
block I10. If an authorized implementation is selected later, its native lane
must restart at `DR0`; relation-lane `DR2` is a prerequisite, not an automatic
runtime upgrade. I9-C and I9-C.1 remain separate evidence and are not rewritten.
I10 remains unopened by C.2 and is the next N31 iteration.

The native tranche must re-earn `DR1` through `DR4`, including canonical
formation, exact restoration/cache removal, non-experiment-authored
progression, canonical relation-dependent conservative transport, a subsequent
native feedback cycle, byte-identical disabled baseline, and provider mismatch
refusal. It cannot inherit producer `DR4`. RCAE admission remains blocked until
`DR5` and a reusable provider contract.

## C.1 Revision Lineage

C.2 consumes corrected C.1 output digest
`2853511bbb0e8604e69b5b1b805c6e49f22eb8b6b17d1630f669064adae3015e`.
An earlier reviewed, non-repository artifact was identified by digest prefix
`33e77c892977`. It is recorded only as lineage and is not consumed. Corrections
separated reduced projection from complete native state, retained causal
history from eliminated independent `S`, fixture scope from generality,
classification from fresh execution, and normalized control meanings. The
provisional C.1 ceiling did not change; scope, authority, and debt became more
precise.

## Control Status

```text
control_plan_complete = true
relation_controls_executed = true
producer_transport_controls_executed = true
native_runtime_controls_executed = false
packetization_invariance = not_run
direct_mediation_controls = not_run
multi_cycle_stability_controls = not_run
topology_lifecycle_controls = not_run
cache_pruning_controls = not_run
```

`control_plan_complete` means the required control surface is declared. It does
not mean every runtime control has executed.

## Checks

| Check | Passed |
|---|---:|
| `source_identities_exact` | true |
| `C_and_C1_preserved_as_separate_evidence` | true |
| `current_runtime_gap_classified_from_source` | true |
| `general_physical_history_contract_frozen` | true |
| `independent_S_authority_forbidden` | true |
| `ordinary_native_transport_gate_not_backfilled_by_wrapper` | true |
| `control_plan_declared_and_execution_scope_explicit` | true |
| `generalized_relation_formation_gate_passed` | true |
| `native_restoration_exact_derivability_gate_passed` | true |
| `generalized_relation_invariance_controls_passed` | true |
| `LGRC_faithful_producer_step_executes_conservative_transport` | true |
| `relation_and_native_runtime_lanes_separated` | true |
| `deferred_naturalization_handoff_is_explicit` | true |
| `weakening_and_susceptibility_semantics_are_explicit` | true |
| `deferred_naturalization_debt_and_readmission_gates_are_explicit` | true |
| `C1_revision_lineage_is_explicit` | true |
| `src_and_protected_contracts_unchanged` | true |
| `I10_remains_unopened` | true |
| `no_absolute_paths_in_records` | true |
