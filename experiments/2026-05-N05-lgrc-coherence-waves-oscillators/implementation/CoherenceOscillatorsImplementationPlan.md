# N05 Coherence Waves And Oscillators Implementation Plan

This document records the implementation plan for
`2026-05-N05-lgrc-coherence-waves-oscillators`.

N05 asks whether LGRC can support delayed, replayable, budget-valid
coherence-wave and oscillator cycles. It is the first experiment in the
N05-N11 agentic-like foundation roadmap, but it does not attempt to prove
choice, identity acceptance, memory, regulation, ACO, agency, or locomotion.

## Scope

N05 is experiment-local unless a separate Phase 8/core task is opened. Scripts,
configs, reports, and outputs should live under:

```text
experiments/2026-05-N05-lgrc-coherence-waves-oscillators/
```

Do not change `src/*` for N05 without stopping and opening a separate Phase 8
implementation task. Existing LGRC9V3 packet scheduling, producer, ledger,
lineage, telemetry, snapshot, and artifact replay surfaces may be used, but
N05 experiment-local code must not silently redefine their semantics.

## Roadmap Position

N05 follows N04, which closed at:

```text
topology_mutating_movement_candidate
```

N05 contributes only oscillator/circuit evidence to the broader roadmap:

```text
N05:
    coherence waves and oscillators

N06:
    semantic route choice

N07:
    RC identity / attractor invariance

N08:
    memory / trail / affordance formation

N09:
    goal-proxy regulation

N10:
    bounded agentic-like integration

N11:
    broader/general agentic-like integration

Later:
    locomotion-like dynamics, if still useful after N10/N11
```

The shared long-range target is:

```text
native_lgrc_agentic_like_dynamics_candidate
```

That target remains blocked in N05.

## Core Claim Discipline

Allowed if supported by gates:

- coherence-wave candidate;
- delayed-pulse candidate;
- reflected-pulse candidate;
- amplified-return candidate;
- repeated oscillator candidate;
- self-sustained oscillator candidate;
- route-coupled oscillator candidate.

Blocked in N05:

- semantic choice;
- agency;
- RC identity collapse;
- identity acceptance;
- memory or trail formation claim;
- goal-proxy regulation;
- agentic-like behavior;
- locomotion-like behavior;
- biological behavior;
- ACO or colony-like behavior;
- unrestricted movement.

Producer scheduling is allowed only as a declared scheduling/evidence mechanism.
It is not agency, not native constitutive oscillator dynamics, and not a hidden
controller.

## RC Compatibility Boundary

Any new policy considered during N05 must be fully compatible with the RC
closed-system interpretation. Policies may shape causal routing, delay,
eligibility, conductance, or local response. They must not inject coherence,
delete coherence, preselect outcomes, or emit claims.

Allowed policy role:

```text
causal structure / geometry / response law
```

Forbidden policy role:

```text
external controller / agency / hidden source term
```

Potential future Phase 3 mechanisms such as custom node potentials, potential
inversion, flux-facilitated metric maps, delayed passive response, or route
conductance memory may be considered only if they are serialized,
runtime-visible, artifact-replayable, and budget-conserving. If current LGRC
cannot express them as native policies, N05 must record a runtime capability
gap rather than faking purity.

## Execution Stages

N05 uses a dissolution strategy:

```text
Stage 1:
    Hybrid explicit scheduling.
    Producers schedule outbound and return packets from declared events or
    committed runtime-visible state.

Stage 2:
    Threshold / surplus-driven scheduling.
    Producers observe committed source/target/reservoir state and schedule
    only when visible criteria pass.

Stage 3:
    Constitutive/native oscillator attempt.
    Replace producer timing with existing serialized LGRC policies if current
    LGRC can express the needed potentials, delays, metric maps, passive
    response, or memory surfaces.
```

Phase 1 and Phase 2 can run now. Phase 3 must begin with a support audit.

### Producer Scaffolds And Retrospective Native Absorption

For N05-N11, producer-mediated runs are valid exploration scaffolds when they
use serialized policy, runtime-visible inputs, LGRC scheduling, and `step()` as
the mutation boundary. They are not pure constitutive dynamics.

Each result should make the mechanism status explicit:

```text
producer_mediated
threshold_authorized
native_route_arbitrated
constitutive_native
native_policy_gap
```

The intended sequence is:

```text
use producers to discover oscillator / choice / identity / memory /
regulation mechanism shapes
-> close the relevant evidence ladders with claim boundaries intact
-> run a retrospective Phase 8/native-absorption pass
-> add only the minimal LGRC-native policy surfaces that the artifacts show are
   needed
```

The retrospective should separate essential producer decisions from
bookkeeping, identify thresholds or response laws that should become serialized
LGRC policies, and keep claims blocked until the relevant producer logic is
dissolved or separately validated as native.

## Native LGRC Surface Mapping

N05 should reuse existing Phase 8 LGRC9V3 surfaces before adding
experiment-local equivalents:

```text
Stage 1 / O1:
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
    producer over declared causal flux routes.

Stage 2 / O3-O5:
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    with LGRC9V3.set_route_aspect_surplus_trigger(...).

Repeated cycles / O4-O5:
    LGRC9V3.run_autonomous(...)
    validate_lgrc9v3_self_rearm_evidence_artifacts(...)

Target contact / O2-O3:
    native causal pulse-substrate surface rows and
    validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(...).

Topology-aware route coupling / O6:
    native route-arbitration records, surface lineage, topology-state
    reabsorption, and time-scoped lineage replay when LGRC-3 topology-changing
    evidence is in scope.
```

These surfaces remain evidence/scheduling infrastructure. They do not promote
choice, identity, memory, regulation, agency, ACO, or locomotion claims.

## O-Ladder

```text
O0:
    no oscillation / passive relaxation

O1:
    delayed outbound pulse

O2:
    reflected return pulse

O3:
    amplified return with reservoir accounting

O4:
    repeated source-target-source cycle

O5:
    self-sustained delayed oscillator

O6:
    route-coupled / trail-reinforced oscillator boundary
```

O-levels are evidence classifications, not claim flags.

Required LGRC runtime levels should be recorded per row:

```text
O0:
    LGRC-0 or synchronous control

O1:
    LGRC-2 packetized causal flux

O2:
    LGRC-2 packet arrival/contact plus return scheduling

O3:
    LGRC-2 plus declared surplus/reservoir trigger

O4:
    LGRC-2 plus native self-rearm evidence or equivalent cycle evidence

O5:
    LGRC-2 plus native trigger audit and bounded autonomous execution

O6:
    LGRC-2 for fixed-route coupling; LGRC-3 if route coupling consumes native
    route arbitration, surface lineage, topology-state reabsorption, or
    time-scoped lineage replay
```

## Required Evidence

Every positive row should record:

```text
run_id
o_level
o_level_is_evidence_classification
claim_ceiling
claim_flags
runtime_family
lgrc_runtime_level
execution_stage
scheduling_mode
producer_mediated
constitutive_native_claim_allowed
source_native_surfaces
fixture_id
source_node_id
target_node_id
route_id
event_time_key
scheduler_event_index
causal_epoch
node_proper_time
source_node_proper_time
target_node_proper_time
outbound_packet_id
outbound_packet_digest
outbound_amount
target_reservoir_before
target_reservoir_after
return_packet_id
return_packet_digest
return_amount
cycle_id
causal_delay
scheduler_order
node_plus_packet_budget_before
node_plus_packet_budget_after
node_plus_packet_budget_error
producer_records
cycle_semantics
scheduling_semantics
amplification_accounting
route_coupling
artifact_only_replay
blocked_claims
```

For O3 and above, any return amount greater than the outbound amount must be
debited from a declared target reservoir or declared boundary/surplus source.
Silent amplification is invalid.

## Report Schema

Initial reports should use:

```text
coherence_oscillator_report_v1
```

Required top-level fields:

```json
{
  "schema": "coherence_oscillator_report_v1",
  "run_id": "",
  "iteration": "",
  "runtime_family": "LGRC9V3|experiment_local",
  "lgrc_runtime_level": "lgrc0|lgrc1|lgrc2|lgrc3",
  "execution_stage": "hybrid_scheduling|threshold_scheduling|constitutive_native_audit",
  "source_native_surfaces": {},
  "fixture": {},
  "o_ladder": {},
  "pulse_chain": {},
  "timing": {},
  "cycle_semantics": {},
  "scheduling_semantics": {},
  "reservoir_accounting": {},
  "route_coupling": {},
  "producer_boundary": {},
  "conservation": {},
  "artifact_replay": {},
  "controls": {},
  "claim_boundary": {},
  "claim_flags": {},
  "claim_ceiling": "",
  "blocked_claims": []
}
```

Every positive row should include scheduling and cycle semantics:

```json
{
  "cycle_semantics": {
    "cycle_definition": "outbound_departure_target_contact_return_source_contact",
    "distinct_cycle_count": 0,
    "plateau_samples_counted_as_cycles": false
  },
  "scheduling_semantics": {
    "scheduling_mode": "explicit_schedule|runtime_threshold|constitutive_policy|native_policy_gap",
    "preauthored_event_list_used": false,
    "producer_mediated": true,
    "producer_mutated_state": false,
    "constitutive_native_claim_allowed": false
  },
  "claim_boundary": {
    "o_level_is_evidence_classification": true,
    "semantic_choice_claim_allowed": false,
    "memory_or_trail_claim_allowed": false,
    "agentic_like_claim_allowed": false
  }
}
```

Every positive row should include LGRC timing evidence where the runtime emits
it:

```json
{
  "timing": {
    "event_time_key": 0.0,
    "scheduler_event_index": 0,
    "causal_epoch": "pre_update|post_update|not_applicable",
    "node_proper_time": null,
    "source_node_proper_time": null,
    "target_node_proper_time": null
  }
}
```

For O3 and above, reservoir accounting should include:

```json
{
  "amplification_accounting": {
    "amplification_source_kind": "target_reservoir|boundary_surplus|none",
    "reservoir_runtime_visible": true,
    "reservoir_hidden_array_used": false,
    "reservoir_budget_before": 0.0,
    "reservoir_budget_after": 0.0,
    "return_excess_debited": 0.0
  }
}
```

Budget fields must distinguish node coherence from in-flight packets:

```json
{
  "conservation": {
    "budget_surface": "node_plus_packet",
    "node_budget": 0.0,
    "in_flight_packet_budget": 0.0,
    "total_budget": 0.0,
    "budget_abs_error_max": 0.0
  }
}
```

## Artifact Naming

Use predictable names:

```text
outputs/n05_<iteration>_<slug>.json
reports/n05_<iteration>_<slug>.md
configs/n05_<slug>.json
```

Each run script should record exact commands in the checklist.

## Iterations

### Iteration 0. Planning And Handoff

Create the N05 implementation plan and checklist. Link them from the
implementation README.

### Iteration 1. Baseline And Schema Inventory

Inventory source artifacts from N03, N04, Phase 8, and the N05-N11 roadmap.
Freeze the O-ladder row schema, claim flags, and baseline blocked claims. This
iteration runs no oscillator probes.

The inventory must explicitly record available native support surfaces:

```text
native packet-loop route-aspect and surplus-trigger surfaces
native self-rearm evidence and artifact validator
native causal pulse-substrate surface
surface lineage transport
topology-state reabsorption
time-scoped lineage replay
native route arbitration
LGRC9V3.run_autonomous(...)
LGRC9V3.load(...)
```

### Iteration 2. Fixture Manifest And Controls

Define the minimal source-target-reservoir fixtures, route policy, delay
policy, budget tolerances, and negative controls:

```text
policy disabled
pulse disabled
missing source
missing target
missing route
budget ambiguity
hidden schedule
producer mutation attempt
claim promotion attempt
snapshot continue-after-load
idempotent duplicate production
stale producer read
```

Freeze the cycle definition before O4:

```text
cycle =
    outbound departure
    -> target contact
    -> return eligibility
    -> return packet
    -> source contact/absorption
```

Repeated cycle counts must count distinct causal cycles with distinct
`cycle_id`s and packet ids, not repeated samples from one persistent contact or
plateau.

Iteration 2 must also choose fixture reuse strategy:

```text
reuse N03 E3 clockwise/counter-clockwise route-aspect fixtures
adapt N04 boundary/pulse-substrate fixtures
or define a new N05 source-target-reservoir fixture
```

The manifest must declare which conservative LGRC defaults are used for lapse,
edge delay, symmetric delay, packetized causal flux, and pending-flux/packet
ledger representation.

### Iteration 3. O1 Delayed Outbound Pulse

Emit one outbound packet from a declared source to a target with causal delay.
Verify packet ledger accounting, scheduler order, artifact replay, and default
off behavior. Prefer the existing
`LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE` producer
over experiment-local packet emitters.

### Iteration 4. O2 Reflected Return Pulse

Produce a return packet linked to the committed outbound arrival/target-contact
event. Verify outbound-return lineage, producer boundary, and stale/hidden
return controls. Prefer committed native causal pulse-substrate surface rows
for target-contact evidence where available.

### Iteration 5. O3 Amplified Return With Reservoir Accounting

Allow return amount to exceed outbound amount only if the excess is debited
from a declared target reservoir or boundary/surplus source. Reject silent
amplification and hidden reservoir arrays. Record `amplification_source_kind`,
reservoir before/after values, and `return_excess_debited`.

Reservoir mapping must be runtime-visible. Preferred mappings are:

```text
source node with observed mass above serialized reference mass
target node with declared stored coherence released by policy
route-aspect surplus trigger using observed_mass/reference_mass fields
```

### Iteration 6. O4 Repeated Cycle

Run at least two source-target-source cycles under one declared policy. Verify
cycle ids, duplicate suppression, budget conservation, artifact-only replay,
and controls for preauthored repeated schedules. Prefer
`LGRC9V3.run_autonomous(...)` and native self-rearm evidence validation for
bounded repeated-cycle lanes.

### Iteration 7. O5 Self-Sustained Oscillator Boundary

Test whether subsequent cycles are authorized by runtime-visible circuit state
rather than a preauthored event list. If producers remain required, label them
as scheduling/evidence mechanisms. Do not claim a pure native oscillator unless
producer logic is dissolved into existing serialized LGRC policies. Record the
O5 mode:

```text
o5_mode = threshold_authorized|producer_mediated|constitutive_native|native_policy_gap
```

The Phase 3 audit must fail closed with explicit fields such as:

```text
native_constitutive_oscillator_supported = false
native_policy_blocker = missing_serialized_delayed_passive_response_policy
```

O5 should record `run_autonomous_stop_condition` and distinguish
`max_events_reached` from natural exhaustion where no producer can schedule work
and queues are empty.

### Iteration 8. O6 Route-Coupled Oscillator Boundary And Closeout

Test whether oscillator traffic can couple to declared route or edge memory
without opening memory/trail claims. If current LGRC lacks the needed native
policy surface, record the blocker and close out at the strongest supported
O-level. Record `route_coupling_surface`, whether route coupling is
runtime-visible, and the memory/trail blocker. Decide whether N06 has enough
component evidence to open.

Native route arbitration may be used as a route-coupling surface only as
runtime route arbitration evidence. It does not promote semantic choice.

## Closeout Criteria

N05 closeout should record:

```text
strongest_supported_o_level
strongest_claim_ceiling
positive artifacts and SHA-256 digests
negative controls and primary blockers
artifact-only replay result
budget conservation result
producer boundary result
Phase 3 native-support blocker, if any
handoff recommendation for N06
```

N05 must not promote movement, semantic choice, identity acceptance, memory,
regulation, ACO, agency, locomotion, or biology claims.
