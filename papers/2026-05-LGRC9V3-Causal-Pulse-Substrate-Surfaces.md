# Causal Pulse-Substrate Surfaces in LGRC9V3

## A Conservative Extension For Packet-Contact History And Producer Eligibility

Copyright © 2026 Uroš Jovanovič, CC BY-SA 4.0.

## Abstract

This paper defines a proposed LGRC9V3 implementation-specialization surface:
the native causal pulse-substrate surface.

The surface is motivated by the N04 movement-ladders experiment. N03/E3
established a native LGRC9V3 self-rearming packet loop: packetized coherence
can circulate through route-aspect semantics under exact node-plus-packet
conservation. N04 then asked whether that packetized pulse can support
movement-like substrate effects. The first boundary-coupled probes produced a
direction-parity-supported repeated boundary-response candidate, but full
self-renewing movement remained blocked until an explicit feedback path was
introduced. Lane C showed that an experiment-local feedback producer can
reopen the M6 feedback gate. Lane D showed that pulse transport can drive a
direction-controlled traveling deformation on a causal geometry surface. Lane
E then showed that both Lane C feedback regeneration and Lane D
pulse-substrate deformation can be represented by one hybrid surface contract
driven from existing native LGRC9V3 E3 pulse artifacts.

The proposed native addon is therefore not a movement axiom and not a new
source term. It is a serializable causal surface that exposes packet-contact
history, local pulse/substrate response, and producer eligibility evidence to
policy-gated producers. Producers may observe, record, and schedule causal
work. They may not mutate coherence directly. Packet/coherence mutation
remains the responsibility of `step()`, and the authoritative LGRC budget
remains:

$$
B(t)
=
\sum_i C_i(t)
+
\sum_{p\in P_{\mathrm{flight}}(t)} C_p(t).
$$

The supported status at this paper stage is:

```text
hybrid_lgrc_causal_pulse_substrate_surface_contract_supported
native_lgrc_pulse_substrate_supported = false
movement_claim_allowed = false
```

Native implementation remains future work. This paper defines what the native
surface should be if it is promoted.

## 1. Scope

This paper is an implementation-specialization proposal. It does not replace
the base LGRC paper and does not modify the minimal LGRC definition.

The base LGRC paper defines:

```text
causal histories
event queues
local proper time
edge delay
packet departure and arrival
node-plus-packet conservation
scheduler/proper-time/checkpoint separation
```

The native packet-loop paper records one validated LGRC9V3 specialization:

```text
route-aspects
measured surplus triggers
self-rearm evidence
D2.3-equivalent packet-loop controls
```

This paper defines the next candidate specialization surface:

```text
native_causal_pulse_substrate_surface
```

with policy-gated producer specializations:

```text
native_pulse_substrate_coupling_producer
native_feedback_coupled_pulse_producer
```

The surface is intended to make pulse/substrate causality replayable. It does
not by itself claim movement, locomotion, agency, biological behavior, or
native synchronous GRC9V3 proposal-flux loops.

This surface is not a new LGRC axiom. It is a conservative implementation
specialization of existing LGRC commitments:

```text
causal packet histories
event-ordered mutation
local proper-time evidence
replayable ledgers
node-plus-packet conservation
```

The surface does not add a new kind of coherence, a new source term, or a new
identity primitive. It only records and exposes causal relations between
committed packet events, local substrate response, and later policy-gated
scheduling eligibility.

This surface requires LGRC-2 or higher. It depends on packetized causal flux,
committed packet departure/arrival events, event-queue ordering, and the
node-plus-packet budget invariant. It is not available at LGRC-0 or LGRC-1,
where causal annotation or proper-time eligibility may exist without the
packetized event queue needed to generate committed packet-contact rows.

## 2. RC And LGRC Compatibility

The proposed surface remains RC-compatible because it does not create or
destroy coherence. It records internal causal relationships between already
valid packet events, local substrate state, and later scheduling eligibility.

The valid sequence is:

```text
packet event commits through step()
-> causal pulse-substrate surface records contact and local state
-> policy-gated producer observes the surface
-> producer emits eligibility evidence and may schedule later packet work
-> step() processes scheduled packet departure/arrival and mutates budget
```

The invalid sequence is:

```text
packet event
-> direct support/centroid/displacement/coherence write by producer
-> movement claim
```

The surface is therefore a packet-scheduling and causal-history surface. It is
not an escape hatch around conservation. If a native producer is later added,
it must preserve the same producer/step boundary established by native
packet-loop semantics:

```text
producer observes / records / schedules
step() mutates coherence
ledger proves conservation and ordering
```

The pulse-substrate surface is not an external affordance field. It is a
runtime-visible internal record of how already-conserved packet events contact
and deform declared substrate state. Any apparent affordance must be traceable
to serialized state, declared policy, and committed event history. Nothing
outside the LGRC ledger may act as a hidden source of direction, energy,
eligibility, or claim promotion.

Causal order comes before interpretation. The interpretive order is:

```text
1. committed packet event
2. conserved packet/node budget record
3. pulse-substrate contact row
4. local surface response
5. producer eligibility evidence
6. scheduled packet work, if policy allows
7. movement-ladder or identity-ladder interpretation
```

No later interpretive layer may be used to justify an earlier causal layer.

In the synchronous GRC reduction limit, the pulse-substrate surface is inert.
When lapse is uniform, edge delay is constant, all nodes are synchronously
eligible, and no in-flight packet state is retained, there are no packet
departure or arrival events from which to emit pulse-substrate rows. In that
limit the surface adds no behavior to ordinary synchronous GRC execution and
no producer scheduling occurs.

## 3. Motivation From N04

N04 started from a strict claim boundary:

```text
N03/E3 heartbeat = pulse-substrate evidence only
E3 heartbeat != movement
movement_claim_inherited_from_n03 = false
```

The fixed-substrate movement tranche was negative for movement response. The
first E3-to-S0 boundary-coupled fixture then showed a measurable repeated
boundary response, and Lane B resolved the direction-parity blocker using true
native reversed E3 pulse telemetry.

The result was still not a native self-renewing movement result. Iteration 10
failed closed because there was no feedback path:

```text
boundary response
-> no native path back to pulse-generation conditions
-> M6 not opened
```

Lane C introduced that missing path in experiment-local form:

```text
S0 boundary response
-> runtime-visible boundary polarity score
-> feedback-triggered next pulse
```

Lane D asked a broader mechanistic question:

```text
Can a pulse travel through a substrate and locally alter geometry/support
state so that a deformation travels with it?
```

Lane D showed local pulse transport, local geometry coupling, direction
controls, and a D5 substrate-carried deformation candidate. It still did not
claim native LGRC support because the deformation surface was experiment-local
and was not a runtime coherence basin.

Lane E then tested whether Lane C and Lane D require separate native addons or
one shared surface. The result was:

```text
status = passed
claim_ceiling = hybrid_lgrc_causal_pulse_substrate_surface_contract_supported
native_lgrc_input_budget_surface = node_plus_packet
experiment_local_surface_budget_surface = node_only
native_contact_count = 13
surface_displacement = 12
surface_width_profile_preserved = true
max_surface_budget_error = 0.0
feedback_eligible_windows = 10
feedback_regeneration_candidate = true
hybrid_lgrc_surface_probe = true
native_lgrc_pulse_substrate_supported = false
movement_claim_allowed = false
```

A focused Lane C compatibility probe then showed:

```text
status = passed
claim_ceiling = lane_c_feedback_policy_compatible_with_causal_pulse_substrate_surface
shared_surface = native_causal_pulse_substrate_surface
lane_c_projection = feedback_policy_specialization
lane_c_specific_core_primitive_needed = false
native_specialization_if_promoted = policy_gated_feedback_producer
native_feedback_producer_supported = false
```

The implementation implication is narrow: the reusable native primitive should
be a causal pulse-substrate surface, with feedback and coupling producers as
policy-gated specializations.

The minimal reusable primitive is not a feedback producer and not a
deformation producer. It is the causal pulse-substrate surface that both
producers read. Feedback and deformation are policy specializations over the
same causal record:

```text
packet contact
local state response
ordering evidence
declared eligibility
```

This preserves LGRC minimality while allowing specialized mechanisms to be
added without changing the meaning of packet coherence or identity.

## 4. Surface Contract

A native causal pulse-substrate surface should be serializable, replayable,
and digest-bearing. It should contain exactly the information needed to
connect packet pulse events to local substrate responses and producer
eligibility.

The surface policy is the serialized activation gate controlling whether
surface rows are emitted and whether producer specializations evaluate
eligibility. When policy is disabled, the surface is inert: no rows are
emitted and no producers run, except for inert configuration or compatibility
metadata if the implementation records it.

Minimal contract shape:

```text
surface_id
schema_version
route_aspect_id
route_aspect_digest
pulse_event_id
pulse_packet_id
pulse_event_kind
pulse_channel_id
pulse_route_step
event_time_key
scheduler_event_index
node_proper_time
source_node_id
target_node_id
contact_amount
surface_state_id
surface_state_digest
surface_kind
surface_nodes
surface_values_before
surface_values_after
surface_update_policy
surface_budget_surface
surface_budget_before
surface_budget_after
surface_budget_error
eligibility_records
producer_records
claim_flags
surface_digest
```

The surface should distinguish:

```text
native LGRC packet budget:
    node_plus_packet

experiment-local or derived surface budget:
    node_only or declared surface budget
```

These accounting surfaces must not be silently merged. The LGRC
node-plus-packet budget is the physical conservation invariant. The derived
surface budget and claim/economy budget are replay, scheduling, and
interpretive accounting surfaces; they are not new conserved coherence
equations. A packet loop can conserve node-plus-packet budget while a derived
surface separately tracks a local support/deformation score.

The implementation must distinguish one LGRC conservation budget from two
derived accounting surfaces:

| Budget | Meaning | Claim impact |
|---|---|---|
| LGRC packet budget | Node coherence plus in-flight packet coherence. | Physical RC/LGRC conservation invariant. |
| Derived surface accounting | Local support/deformation accounting declared by surface policy. | Replay and scheduling eligibility audit. |
| Claim/economy accounting | Movement-ladder cost or economy statistic. | Claim gating and interpretation only. |

These surfaces may be linked, but they are not interchangeable. Conservation
of the LGRC packet budget does not imply validity of a derived surface or
movement claim unless the report declares the mapping and audits it. Likewise,
a bounded movement/economy statistic is not evidence of conserved coherence.

## 5. Event Links And Ordering

Every surface update must link to a committed causal event. A valid pulse
surface row has the ordering:

```text
source packet event committed by step()
-> surface row emitted after source event
-> producer evaluation reads committed surface row
-> optional scheduled packet has a later scheduler index
```

The row must include enough timing evidence to distinguish:

```text
scheduler order
event time
node proper time
checkpoint/replay order
```

A native implementation should reject or downgrade:

```text
surface row without source event
producer evaluation before source event
missing event_time_key
missing scheduler_event_index
missing route_aspect_digest when route-bound
surface digest mismatch
```

## 6. Surface Update Semantics

The surface records local response to packet pulse contact. It may represent
several substrate-facing state surfaces, but each row must declare which one
is active.

Here "response" is mechanical. It means a declared, replayable surface-state
update computed from committed packet-contact evidence and runtime-visible
state under a serialized `surface_update_policy`. It does not imply autonomous
reaction, agency, intention, or untracked substrate behavior.

Candidate surface kinds:

```text
local_support_mass
boundary_polarity_score
surface_deformation
proper_time_phase
route_local_pulse_contact
feedback_eligibility
```

The first native target should be conservative and small:

```text
native_causal_pulse_substrate_surface
```

not a separate movement engine.

The surface may record derived local state such as:

```text
front_mass
rear_mass
boundary_polarity_score
surface_deformation_displacement
feedback_eligibility
feedback_polarity
```

Each `surface_kind` must declare its runtime-visible inputs:

| Surface kind | Runtime-visible inputs |
|---|---|
| `local_support_mass` | Sum of node coherence $C_i$ over a declared support mask. |
| `boundary_polarity_score` | Derived from front/rear mass aggregates of $C_i$ over declared boundary masks. |
| `proper_time_phase` | Node proper time $\tau_i$ at contact nodes or declared local masks. |
| `surface_deformation` | Declared function of $C_i$, $\tau_i$, or other serialized runtime fields over `surface_nodes`. |
| `route_local_pulse_contact` | Packet contact amount, route step, channel id, and contact node ids from committed packet events. |
| `feedback_eligibility` | Derived from declared surface values, references, thresholds, and polarity policy. |

Hidden fixture arrays, preauthored itineraries, or post-hoc movement
classifications are not valid runtime-visible inputs.

The surface must not directly write:

```text
node coherence
packet coherence
support masks
centroid
displacement
topology
claim flags
```

If a later policy schedules packet work, that work must go through existing
LGRC scheduling and `step()` processing.

The first native surface target is fixed-topology. If topology changes through
refinement or module expansion before an LGRC-3 lineage policy is implemented,
surface rows that reference affected nodes must fail closed or be marked
unsupported with `topology_lineage_deferred`. A future LGRC-3 extension may
transport affected rows through the lineage map $\beta$, but the v1 surface
must not silently reuse stale node ids after refinement.

## 7. Producer Specializations

The surface supports producer specializations. These are policy-gated and
disabled by default.

### 7.1 Pulse-Substrate Coupling Producer

The pulse-substrate coupling producer observes surface rows such as:

```text
pulse contact
local support mass response
proper-time phase response
surface deformation response
```

It may emit:

```text
producer_policy
surface_id
surface_digest
source_pulse_event_id
observed_surface_value
reference_surface_value
coupling_delta
threshold
eligible_action
reason_code
event_time_key
```

It may schedule later causal work through LGRC scheduling if policy allows.
It may not mutate coherence or geometry directly.

### 7.2 Feedback-Coupled Pulse Producer

The feedback producer is the native counterpart of N04 Lane C's
experiment-local adapter. It observes a runtime-visible surface such as:

```text
boundary_polarity_score = (front_mass - rear_mass) - reference_delta
```

and may authorize a later pulse only after the source packet event has been
processed by `step()` and the resulting surface row has been emitted. The
producer reads the committed surface row, not hidden fixture state.

Minimum evidence:

```text
feedback_surface_id
feedback_surface_digest
runtime_visible_inputs
reference_value
observed_value
threshold
polarity
eligible_next_route_or_channel
scheduled_packet_id if scheduled
reason_code
source_surface_event_id
producer_record_id
event_time_key
scheduler_event_index
```

Controls should block:

```text
pulse disabled
feedback disabled
subthreshold feedback
wrong polarity
scrambled timing/order
budget-violating synthetic blocker
```

Feedback eligibility is weaker than self-renewing movement. A feedback
producer may show that a surface response can restore the mechanical
conditions for a later pulse. Self-renewing movement additionally requires
that the moving runtime identity restores the conditions for continued
movement while preserving identity, budget, shape, and control parity. The
surface can support feedback eligibility; it does not by itself establish
self-renewing movement.

## 8. Producer/Step Boundary

The native packet-loop paper established the critical runtime boundary:

```text
produce_events(...):
    inspect runtime state and enqueue eligible causal work

step():
    consume exactly one queued event and mutate runtime state
```

The causal pulse-substrate surface must preserve the same boundary.

Allowed producer behavior:

```text
read committed packet and surface evidence
compute local surface values
emit eligibility records
emit non-trigger records
schedule packet departure through native LGRC scheduling
```

Forbidden producer behavior:

```text
debit or credit coherence
write support masks
write centroid or displacement
change topology
mark a packet departure as processed
emit claim labels or claim promotion decisions
```

This is what keeps the addon a causal scheduling surface rather than a hidden
mutator.

Claims are the responsibility of experiment-level validators and reports, not
runtime producers. A producer emits evidence; it does not interpret that
evidence as movement, identity, agency, or native M6.

Producer eligibility is not choice. It is a policy-gated mechanical readiness
record. A producer may schedule causal work only when declared thresholds and
ordering constraints pass. This is not intention, agency, decision-making, or
semantic goal pursuit. Any future choice/identity-collapse interpretation
would require a separate RC identity-resolution ladder.

## 9. Snapshot, Telemetry, And Replay

The surface must survive snapshots and telemetry export. A later validator
must be able to reconstruct the chain from artifacts alone:

```text
packet event
-> pulse-substrate surface row
-> producer eligibility row
-> scheduled packet, if any
-> processed packet event, if any
```

Snapshot/telemetry should include:

```text
surface contract
surface schema version
surface rows
surface digests
route_aspect_digest references
producer records
reason codes
budget records
proper-time/event-time evidence
claim flags
direct-write policy
```

Loading a snapshot must not regenerate or duplicate surface evidence.

## 10. Controls

A native implementation should not be accepted without controls.

Minimum controls:

| Control | Expected blocker |
|---|---|
| policy disabled | no surface producer records beyond inert config |
| pulse disabled | no pulse-contact surface rows |
| coupling disabled | pulse rows may exist, no coupling eligibility |
| feedback disabled | feedback surface rows may exist, no next-pulse scheduling |
| subthreshold | observed surface value below threshold |
| wrong polarity | polarity gate failed |
| scrambled order | canonical causal order failed |
| missing source event | surface row rejected |
| pre-source producer | ordering gate failed |
| budget violation | budget gate failed |
| direct-write attempt | mutation-boundary gate failed |

Controls should fail for explicit primary blockers. A negative control that
only "does not pass" is not strong enough.

## 11. N04 Hybrid Evidence

The current evidence is hybrid, not native.

Lane E:

```text
existing native LGRC9V3 E3 pulse telemetry
+ experiment-local causal pulse-substrate surface driver
+ D5 classifier/replay stack
```

passed as:

```text
hybrid_lgrc_causal_pulse_substrate_surface_contract_supported
```

The Lane E driver:

```text
read existing native LGRC9V3 artifacts
linked 13 native pulse-contact events
generated experiment-local surface rows
reproduced Lane D-style deformation
represented Lane C-style feedback eligibility
kept native_lgrc_pulse_substrate_supported = false
kept movement_claim_allowed = false
```

This proves contract coherence, not native runtime support.

The evidence ladder is:

| Evidence | Supported | Blocked |
|---|---|---|
| N03/E3 | Native self-rearming packet pulse. | Movement. |
| N04 Lane B | Direction-parity repeated boundary response. | Locomotion, M6. |
| N04 Lane C | Experiment-local feedback regeneration candidate. | Native feedback producer. |
| N04 Lane D | Deformation-surface movement candidate. | Runtime coherence-basin movement. |
| N04 Lane E | Shared hybrid surface contract coherence. | Native LGRC pulse-substrate support. |

## 12. Claim Discipline

Supported by this paper:

```text
causal pulse-substrate surface is a coherent LGRC9V3 addon target
Lane C feedback and Lane D deformation can share one surface primitive
feedback can be a policy-gated producer specialization
native implementation should start with the broad surface, not a one-off adapter
```

Not yet supported:

```text
native_lgrc_pulse_substrate_supported
native_feedback_producer_supported
native_m6
full movement response
loop-driven movement
locomotion-like basin dynamics
adaptive topology movement
biological behavior
agency
identity acceptance
```

The proposed surface may become useful for movement experiments, but movement
requires separate movement-ladder gates. A surface row is not a moving basin.
A traveling deformation is not automatically locomotion.

Claim promotion rule:

```text
A causal pulse-substrate surface may promote only the claims whose gates are
native to that surface:

- packet contact evidence;
- local substrate response;
- producer eligibility;
- feedback/coupling scheduling evidence.

It may not promote movement, identity, agency, locomotion-like behavior, or
adaptive topology unless those claims are independently gated by their
respective ladders.
```

## 13. Relation To RC Identity And Acceptance

The causal pulse-substrate surface is not itself an identity. It records
causal deformation, contact, and policy-gated scheduling eligibility evidence
associated with packet events and local substrate response. A surface row may
support later identity analysis, but it is not an accepted identity token
unless a separate identity-continuity gate binds it to a runtime coherence
basin.

In RC terms, the surface records a history-dependent local deformation of the
field/substrate. It does not assert agency, choice, semantic intention, or
identity acceptance. Collapse/choice-like language remains blocked unless a
separate identity-resolution or action-selection ladder is opened and
validated.

The intended identity-carrier taxonomy is:

| Carrier | Runtime status | Identity status | Claim ceiling |
|---|---|---|---|
| `packet` | In-flight conserved coherence. | Causal transport object. | Packetized pulse. |
| `surface_row` | Committed packet/substrate contact record. | Evidence row, not identity. | Causal contact evidence. |
| `deformation_token` | Tracked surface response over time. | Not an RC identity carrier. | Traveling deformation candidate. |
| `producer_record` | Policy-gated eligibility evidence. | Scheduler evidence, not agency. | Feedback/coupling eligibility. |
| `coherence_basin` | Runtime attractor/support continuity. | Candidate RC identity carrier. | Movement identity gate eligible. |

This distinction preserves the D5/N04 boundary:

```text
traveling deformation on a causal surface
!= accepted runtime coherence-basin movement
```

It also keeps producer records non-agentic. A producer record is mechanical
policy-gated scheduling eligibility evidence. It does not imply intention,
preference, action selection, or identity acceptance.

## 14. Failure Modes

The native surface must fail closed under:

```text
surface rows without committed source packet events
producer records emitted before source event commitment
missing route_aspect_digest or surface_digest
direct coherence/support/centroid/topology writes by a producer
budget-surface ambiguity
snapshot reload duplicating surface rows
feedback eligibility generated from hidden fixture state
deformation token promoted as coherence-basin identity
movement claim emitted by surface contract alone
producer eligibility interpreted as choice or agency
```

Failure should be explicit. Reports should include a primary blocker, blocked
claims, and the failed gate rather than merely saying that a lane did not
pass.

## 15. Native Implementation Requirements

Before Lane F opens core implementation, the native plan should require:

```text
default-off policy gate
explicit surface schema and digests
route_aspect_digest linkage where route-bound
surface rows emitted only from committed source events
producer/step boundary preserved
no direct support/centroid/displacement/topology writes
node-plus-packet packet budget preserved
surface budget declared separately
snapshot and telemetry round-trip
artifact-only validation
negative controls with primary blockers
claim flags in every report
```

Minimal native claim flags:

```text
native_causal_pulse_substrate_surface_enabled = true|false
native_causal_pulse_substrate_surface_validated = true|false
native_pulse_substrate_coupling_producer_enabled = true|false
native_pulse_substrate_coupling_producer_validated = true|false
native_feedback_coupled_pulse_producer_enabled = true|false
native_feedback_coupled_pulse_producer_validated = true|false
native_lgrc_pulse_substrate_supported = true|false
native_m6 = true|false
movement_claim_allowed = false by default
loop_driven_movement_claim_allowed = false by default
locomotion_like_claim_allowed = false by default
adaptive_topology_entry_allowed = false by default
```

The `enabled` flags record whether a surface or producer was active during a
run. The `validated` flags record whether the corresponding contract and
controls passed. A mechanism may be enabled without being validated.

A run may enable native surface emission without supporting the native surface
claim. Support requires passing schema, ordering, budget, snapshot/replay, and
negative-control validators.

## 16. Relation To The LGRC Paper

The base LGRC paper should remain minimal. It should define packetized causal
flux, event queues, proper-time ordering, and node-plus-packet conservation.

This paper should be cited as an implementation-specialization extension:

```text
LGRC supports causal packet histories.
LGRC9V3 native packet loops instantiate self-rearming packetized pulses.
The causal pulse-substrate surface is a proposed native observability and
producer-eligibility layer over those packet histories.
```

The surface should not be read as saying that all LGRC systems require
movement ladders, pulse-substrate deformation, or feedback-coupled pulse
producers.

## 17. Remaining Work

The next implementation work is:

```text
update the Phase 8 native implementation plan/checklist
define Lane F native surface schema
implement default-off native surface emission
add policy-gated producer specializations
add snapshot/telemetry persistence
add artifact-only validators
run N04 Lane F controls
```

Only after those pass may the project consider:

```text
native_lgrc_pulse_substrate_supported = true
native_feedback_producer_supported = true
```

Movement, locomotion-like behavior, adaptive topology movement, biology, and
agency remain separate claim ladders.

## Bibliography

- `papers/2026-05-LGRC-9.md`: base Lorentzian/event-driven Graph Reflexive
  Coherence paper.
- `papers/2026-05-LGRC9V3-Native-Packet-Loops.md`: native LGRC9V3 packet-loop
  implementation-specialization paper.
- `papers/2025-11-RC-IdentityChoiceAbundance.md`: RC identity, choice, and
  acceptance framing.
