# N05 LGRC Coherence Waves And Oscillators

N05 studies whether LGRC can support coherence-wave and delayed-oscillator
primitives before opening semantic-choice, RC-identity, memory/trail,
goal-proxy regulation, agentic-like, or locomotion-like experiments.

N04 closed the movement/topology-mutating tranche at:

```text
topology_mutating_movement_candidate
```

N05 uses that result as background, not as a claim to extend automatically.
The goal here is lower-level: prove whether coherence can be sent as a
structured pulse, delayed, reflected or amplified, returned with budget
accounting, and repeated as an artifact-replayable oscillator.

## Core Question

```text
Can LGRC sustain delayed, replayable, budget-valid coherence-wave and
oscillator cycles without treating the result as choice, agency, identity,
ants, or locomotion?
```

## Why This Comes Before Choice, Invariance, Memory, Regulation, And Agency

Route choice, identity invariance, memory/trail formation, goal-proxy
regulation, agentic-like behavior, and locomotion-like behavior all depend on
more primitive circuit behavior:

```text
source -> delayed pulse -> target interaction -> return pulse -> repeated cycle
```

If that primitive is not stable, later ladders risk hiding the missing physics
behind producers or classifiers. N05 isolates the circuit first.

ACO-like behavior should not be opened immediately after N05. It should be
split into prerequisites: semantic route-choice evidence, identity/invariance
anchors, and memory/trail formation. Until those exist, labels such as "nest",
"food", and "trail" remain fixture roles in a coherence circuit, not validated
semantic objects.

## Working Model

N05 treats an "ant" or "traveler" as a visible packet/wave peak, not as an
agent object. The substrate is a coherence circuit:

```text
source / nest:
    reservoir or excitable source

target / food:
    interaction site that can reflect, amplify, or release stored coherence

trail / channel:
    delayed LGRC route carrying packetized coherence

cycle:
    outbound pulse, target interaction, return pulse, source absorption
```

This can be explored in stages. Early stages may use producers as explicit
scheduling mechanisms. Later stages should dissolve producer logic into
declared runtime-visible thresholds, potentials, metric maps, or existing LGRC
policies when those are available.

N05 should reuse existing native LGRC9V3 support surfaces where they fit:

```text
packet departure from declared flux routes:
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE

packet departure from route-aspect surplus:
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
    with LGRC9V3.set_route_aspect_surplus_trigger(...)

bounded autonomous execution:
    LGRC9V3.run_autonomous(...)

native self-rearm evidence:
    validate_lgrc9v3_self_rearm_evidence_artifacts(...)

native causal pulse-substrate surface:
    validate_lgrc9v3_causal_pulse_substrate_surface_artifacts(...)

native route arbitration:
    native_lgrc_route_arbitration_supported surfaces
```

If a needed oscillator behavior cannot be represented through these existing
surfaces, N05 should record the runtime capability gap instead of rebuilding a
parallel experiment-local substitute.

N05 uses the native route-aspect contract for serialized route semantics where
possible:

```text
LGRC9V3RouteAspect / LGRC9V3RouteAspectChannel / LGRC9V3RouteAspectHop
route_aspect_digest / pole_region_digest / channel_sequence_digest
```

For O3 and above, the preferred reservoir-to-runtime mapping is ordinary
runtime-visible node coherence or the native route-aspect surplus trigger:

```text
observed_mass = pole_mass
reference_mass = serialized policy value
surplus = observed_mass - reference_mass
```

Hidden reservoir arrays or report-side surplus values are invalid.

## Oscillation Ladder

The O-ladder is local to N05. It describes coherence-wave and oscillator
evidence. It does not imply movement, choice, agency, identity, or locomotion.

```text
O0: no oscillation / passive relaxation
    Coherence relaxes or diffuses without a delayed outbound-return cycle.

O1: delayed outbound pulse
    A source emits a structured pulse that travels to a target with causal
    delay and artifact-visible packet accounting.

O2: reflected return pulse
    Target interaction produces a return pulse linked to the outbound event.
    The return may be explicit producer-scheduled, but must be ledger-visible.

O3: amplified return with reservoir accounting
    Return pulse carries more coherence than the outbound pulse, and the
    increase is accounted for by a declared target reservoir or surplus source.

O4: repeated source-target-source cycle
    At least two outbound-return cycles repeat under the same declared policy,
    with exact node-plus-packet accounting and artifact-only replay.

O5: self-sustained delayed oscillator
    The cycle repeats from runtime-visible circuit state rather than a
    preauthored event list. Producers, if present, remain scheduling/evidence
    mechanisms and do not emit claims.

O6: route-coupled / trail-reinforced oscillator
    Oscillation couples to route or edge memory, such as declared conductance,
    flux-history, or trail reinforcement surfaces, while preserving replay,
    budget accounting, and claim boundaries.
```

O-levels are evidence classifications, not claim flags. The frozen
implementation map is:

```text
O0 -> LGRC-0 or synchronous control -> no_oscillation
O1 -> LGRC-2 packetized causal flux -> delayed_pulse_candidate
O2 -> LGRC-2 packet contact/return scheduling -> reflected_pulse_candidate
O3 -> LGRC-2 plus declared reservoir/surplus trigger -> amplified_return_candidate
O4 -> LGRC-2 plus repeated-cycle/self-rearm evidence -> repeated_oscillator_cycle_candidate
O5 -> LGRC-2 plus bounded autonomous execution -> self_sustained_oscillator_candidate
O6 -> LGRC-2 fixed-route coupling or LGRC-3 topology-aware coupling -> route_coupled_oscillator_candidate
```

## Current Closeout

N05 closes at:

```text
strongest_supported_o_level = O5
strongest_claim_ceiling = self_sustained_oscillator_candidate
```

The strongest positive evidence is the O5 producer-mediated/native self-rearm
oscillator boundary: three reconstructed self-rearm cycles from serialized
LGRC9V3 route-aspect evidence with exact node-plus-packet accounting.

O6 remains blocked:

```text
o6_route_coupled_oscillator_supported = false
trail_memory_blocker = missing_route_conductance_memory_policy
```

The O5 route-aspect surface is serialized and runtime-visible, but current N05
artifacts do not include a native route conductance memory or trail
reinforcement surface. N05 therefore does not promote memory/trail, semantic
choice, agency, RC identity collapse, identity acceptance, ACO, locomotion-like,
biological, or unrestricted movement claims.

Handoff: N06 may open semantic route-choice work using N05 O5 as
oscillator/circuit background, but it must not inherit any of the blocked
claims above.

## Implementation Stages

N05 should use a dissolution strategy:

```text
Stage 1: Hybrid explicit scheduling
    Producers schedule outbound and return packets from declared events or
    visible node state. This proves ledger mechanics and budget accounting.

Stage 2: Threshold / surplus-driven scheduling
    Return pulses are triggered by target coherence state, not by hidden
    packet role logic. Producers observe committed state and schedule only.

Stage 3: Constitutive oscillator
    Where current LGRC supports it, replace scheduling logic with declared
    potentials, delays, metric maps, or passive continuity policies. If current
    LGRC cannot express a needed potential or metric field, record that as a
    runtime capability gap rather than faking purity.
```

Important caveat: Phase 3 is only "pure existing LGRC" if the current runtime
can express the required mechanism as serialized policy, such as custom node
potentials, potential inversion, flux-facilitated metric maps, delayed passive
response, or equivalent native fields. If those are not currently expressible,
Phase 3 must record a runtime capability gap and stop short of a pure-native
claim. Phase 1 and Phase 2 probes can still run now with producers, but those
producers must be labeled as scheduling/evidence mechanisms, not hidden agency
or constitutive oscillator dynamics.

## Producer Scaffolds For N05-N11

N05-N11 may use producers as exploration scaffolds before a pure-native
implementation exists. This is acceptable only when producers observe committed
runtime-visible state, emit evidence records, schedule through LGRC queues, and
never mutate coherence, topology, identity, or claims directly.

Producer-mediated results are therefore proof-of-contract evidence for later
mechanism design, not final constitutive substrate laws. N05 should record
whether each positive result is:

```text
producer_mediated
threshold_authorized
constitutive_native
native_policy_gap
```

After N05-N11, a retrospective Phase 8/native-absorption pass should identify:

```text
which producer decisions were essential
which producer fields were only bookkeeping
which thresholds or response laws should become serialized LGRC policies
which runtime-visible surfaces LGRC lacks
which claims stay blocked until producer logic is dissolved
```

This avoids guessing the pure-native implementation too early. It also prevents
producer-mediated oscillator, choice, memory, or regulation evidence from being
misread as agency or pure native constitutive dynamics.

## Required Evidence

Every positive N05 row should record:

```text
source node / target node
lgrc_runtime_level
event_time_key / scheduler_event_index / snapshot_index where available
node_proper_time and source/target node proper time where available
edge_causal_delay
outbound packet id and digest
outbound amount
target reservoir/surplus before and after
return packet id and digest
return amount
cycle id
causal delay / scheduler order
node-plus-packet budget before and after
artifact-only replay result
claim flags
```

LGRC timing vocabulary:

```text
scheduler_event_index = kappa, computational scheduler order
snapshot_index = k, observer/replay order
event_time_key = T_e, event queue ordering key
node_proper_time = tau_i, local accumulated proper time
edge_causal_delay = tau_ij, causal delay on an edge
```

For O3 and above, the return pulse may exceed the outbound pulse only if the
extra coherence is debited from a declared reservoir or external boundary
source. Silent amplification is invalid.

## Claim Boundary

N05 may support:

```text
coherence_wave_candidate
delayed_pulse_candidate
reflected_pulse_candidate
amplified_return_candidate
coherence_oscillator_candidate
```

N05 must not emit or imply:

```text
movement_claim_allowed
semantic_choice_claim_allowed
agency_claim_allowed
rc_identity_collapse_claim_allowed
identity_acceptance_claim_allowed
locomotion_like_claim_allowed
biological_claim_allowed
ant_colony_claim_allowed
trail_memory_claim_allowed
goal_proxy_regulation_claim_allowed
agentic_like_claim_allowed
unrestricted_movement_claim_allowed
```

## Relationship To Future Experiments

The full N05-N11 continuation is also recorded in:

```text
../N05-N11-LGRC-AgenticLikeFoundationRoadmap.md
```

```text
N04:
    movement taxonomy and topology-mutating movement candidate baseline

N05:
    coherence waves, delayed pulses, reflected/amplified returns, oscillators

N06:
    semantic choice / route-selection-as-choice ladder

N07:
    RC identity, attractor invariance, identity acceptance

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

N05 should feed those later experiments only as component evidence. A later
experiment must still earn its own claims with its own inventory, controls,
and validators.

The intended high-level sequence is:

```text
N05:
    wave first

N06:
    choice second

N07:
    identity third

N08:
    memory/trail fourth

N09:
    regulation fifth

N10:
    bounded integration sixth

N11:
    broader/general integration seventh

Later:
    locomotion-like dynamics only after integration clarifies the movement /
    identity / support coupling target
```

This keeps "agentic-like" as an earned integration claim, not a synonym for
producer scheduling.

The shared target is a native substrate foundation for:

```text
native_lgrc_agentic_like_dynamics_candidate
```

That target remains blocked until later experiments validate native choice,
identity/invariance, memory/trail formation, goal-proxy regulation,
perturbation recovery, and artifact-only replay without hidden experiment-side
steering. N05 can only contribute oscillator/circuit evidence to that later
composition.

## First Planned Iterations

```text
Iteration 1:
    Baseline and artifact inventory from N03/N04/Phase 8.
    Define O-ladder row schema and claim flags.

Iteration 2:
    Fixture manifest and controls. Freeze source/target/reservoir/route/delay
    fixtures, cycle definition, budget surfaces, and hidden-controller
    controls.

Iteration 3:
    O1 delayed outbound pulse on a minimal source-target fixture.

Iteration 4:
    O2 reflected return pulse, with outbound-return lineage.

Iteration 5:
    O3 amplified return with explicit reservoir accounting.

Iteration 6:
    O4 repeated source-target-source cycle under replay.

Iteration 7:
    O5 self-sustained delayed oscillator boundary.

Iteration 8:
    O6 route-coupled / trail-reinforced oscillator boundary.
    Closeout freezes the strongest supported O-level, records blocked claims,
    and decides whether N06 has enough coherence-circuit evidence to open.
```

Stop and open a Phase 8 implementation task if a required behavior needs new
native LGRC support, such as custom serialized potentials, flux-facilitated
metric maps, or passive continuity policies that do not currently exist.

## Acceptance Boundary

N05 is complete enough to hand off when the strongest supported O-level is
source-backed, artifact-replayable, budget-accounted, and bounded by explicit
claim flags. A successful N05 closeout may provide component evidence for N06
through N11, but it does not by itself prove semantic choice, RC identity
invariance, trail memory, goal-proxy regulation, ACO-like behavior,
locomotion-like behavior, biology, agency, or unrestricted movement.
