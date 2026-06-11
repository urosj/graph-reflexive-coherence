# N07 RC Identity Attractor Invariance

N07 asks whether LGRC evidence can support an RC identity candidate as a
stable, self-maintaining attractor basin, rather than as a label, node id,
route choice, or movement trace.

This experiment follows:

```text
N05:
    coherence waves and oscillators

N06:
    artifact-only semantic route-choice candidate
```

N06 can supply route-selection background, but N07 must independently validate
identity. A selected route is not an identity, and identity continuity is not
agency.

## Current Closeout

Iteration 12 closes the core N07 question with an artifact-only,
source-specific ID6 evidence classification:

```text
frozen_long_horizon_c3_class =
    bounded_non_destructive_exchange

frozen_n07_ceiling =
    ID6
```

This means the completed 11-* branch series replayed from artifacts only and
classified connected dual basins as capable of bounded, non-destructive
exchange under `neutral_absorber_reservoir_v1`. It does not mean runtime
identity acceptance, RC identity collapse, semantic choice, agency,
biological identity, personhood, or unrestricted identity. All claim flags
remain false.

## Post-Closeout N10 Compatibility Baseline

Iteration 13 adds a narrow post-closeout compatibility baseline for N10. It
does not reopen the N07 identity ladder and does not promote the Iteration 12
ID6 evidence classification into runtime identity acceptance.

The reason for Iteration 13 is cross-experiment hygiene. N09 preserved the
blocker:

```text
n07_identity_withdrawal_baseline_not_available
```

That was the correct boundary. N09 could regulate a proxy, but without an N07
support-withdrawal baseline it could not decide whether support weakening
disrupted the identity substrate or merely exposed an untested N07 condition.

Iteration 13 supplies a source-backed baseline for N10:

```text
support_intact_reference:
    support survives under the Iteration 12 bounded-exchange baseline.

mild_support_weakening:
    support survives a smaller weakening.

n09_matched_partial_support_withdrawal:
    the N09 0.25 partial support withdrawal disrupts support without
    restoration.

restored_after_n09_partial_withdrawal:
    explicit restoration recovers support survival.
```

N10 may consume this as an identity/support baseline. Old N09 artifacts are
not retroactively changed, and runtime identity acceptance, RC identity
collapse, semantic choice, agency, biological identity, personhood, and
unrestricted identity claims remain blocked.

## Theory Basis

N07 uses a layered theory stack, not only the core RC identity paper.

```text
RC:
    papers/2025-11-RC-IdentityChoiceAbundance.md
    continuous definition of identity as a stable self-maintaining attractor
    basin; collapse/choice and local irreducibility boundary.

GRC-V2:
    papers/2025-12-GRC-V2.md
    discrete reflexive loop, directed-flux graph, sinks, identity basins,
    spark detection, budget preservation.

GRC-V3:
    papers/2026-02-GRC-V3.md
    basin-attribute nodes: gradient, Hessian, net flux, basin mass, identity
    id, parent, depth, hierarchy, and multi-metric structure.

GRC-9 / GRC9V3:
    papers/2026-04-GRC-9.md
    nine-port basin charts, identity basins, spark/refinement mechanics,
    child-basin emergence, and the boundary that refinement is not identity
    fission by itself.

LGRC / LGRC9V3:
    papers/2026-05-LGRC-9.md
    causal histories, local proper time, lineage maps, packet ledgers, and
    proper-time identity persistence windows.

Native causal pulse-substrate surfaces:
    papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md
    identity-carrier taxonomy separating surface rows, deformation tokens,
    boundary signals, and runtime coherence basins.

Arc of Becoming methodology:
    Classification of Becoming
    Interrogation of Becoming
    Naturalization of Becoming
    Cultivation of Becoming
    observation-first classification, bounded probes as questions,
    support-withdrawal, naturalization, and activity-history integration.
```

The core RC paper answers what identity is. The GRC/LGRC papers answer how a
discrete runtime can represent, transport, time-order, and validate identity
evidence. The Arc of Becoming papers answer how to interpret uncertain results
without forcing proof or losing non-promoting evidence.

N07 uses the following definitions as gates.

Reflexive coherence state:

```text
S_coh = (C(x,t), J_C(x,t))
J_C = C v_C
partial_t C + div J_C = 0
```

Coherence functional:

```text
P[C] = integral((kappa_C / 2) grad C . grad C - V(C)) sqrt(-g[C]) d^4x
```

Attractors are stationary/stable configurations of this functional under the
coherence-induced geometry.

Global coherence invariance:

```text
C_sys(t) = integral_{Omega_t} C(x,t) dV_g
dC_sys/dt = 0
```

For LGRC experiments, this maps to exact node-plus-packet budget accounting:

```text
sum(active node coherence)
+ in_flight_packet_total
== conserved_budget_total
```

An RC identity basin is a region `A subset Omega_t` satisfying:

```text
stability:
    A contains a stable local curvature / potential well.

attractivity:
    flux from an open neighborhood U converges toward A.

invariance:
    Phi_t(A) = A for the relevant reflexive window, modulo explicit lineage.

reflexive closure:
    coherence entering A contributes to maintaining or deepening A.

coherence compatibility:
    A coexists with nearby modes without destructive interference.
```

N07 translates those gates to discrete LGRC evidence. A support area is not an
identity by itself. It becomes an identity candidate only if support, budget,
flux, invariance, closure, and compatibility all pass with artifact replay.

Because N07 enters unknown identity territory, every result must be classified
at the lowest valid rung. A probe-supported identity-like response is not
native identity evidence. It is a question-answer pair until withdrawal,
controls, and naturalization checks show what support was supplied and whether
the system can generate the relevant support function itself.

Discrete GRC/LGRC additions are also required:

```text
identity basin:
    directed-flux attraction domain around a sink / basin chart.

basin attributes:
    gradient summary, Hessian summary, net flux summary, basin mass, identity
    id, parent id, and depth.

lineage-current identity:
    after topology changes, identity evidence must be transported through
    explicit lineage maps and must not use stale node ids.

proper-time identity:
    persistence is measured over local or lineage proper time, not raw
    scheduler or checkpoint windows.

identity carrier:
    only runtime coherence basins are eligible identity carriers. Surface
    rows, deformation tokens, and boundary signals are supporting evidence
    only.
```

## Schema And Control Discipline

N07 uses ID levels as evidence classifications, not claim flags. Every
identity row must keep the candidate carrier, evidence surface, native support
status, gate vector, blocked claims, source artifacts, source reports, and
SHA-256 digests explicit. Rows must also separate native LGRC observables from
experiment-local observables:

```text
native_support_status =
    pure_native | mixed_native_experiment_local | experiment_local | blocked

native_observables_used =
    runtime-visible LGRC/native observable ids consumed by the row

experiment_local_observables_used =
    declared experiment-local observable ids consumed by the row
```

Support-area and activity-history digests are SHA-256 digests over canonical
JSON with sorted keys. Visual references are non-authoritative unless a row
explicitly marks them as evidence and backs them with source artifacts.

Gate-vector values are:

```text
pass
fail
blocked
not_measured
not_applicable
```

Conditional gates are handled by the ceiling algorithm. For example,
`lineage_current` must pass when topology mutation occurs; otherwise it is
`not_applicable`.

Canonical controls:

```text
label_only_null_topology
missing_support_area
external_label_only
duplicate_support_row
budget_discontinuity
stale_node_id_replay
missing_topology_state_reabsorption
lineage_map_scrambled
support_drift_beyond_threshold
unstable_basin_no_local_well
hidden_potential_or_report_side_well_score
posthoc_threshold_change
identity_threshold_missing
wrong_support_area
no_reentry
closure_not_consumed_by_later_cycle
improper_proper_time_threshold
failed_persistence
non_attractive_flux
wrong_basin
wrong_polarity
subthreshold_flux
hidden_route_context_steering
destructive_interference
ambiguous_overlap
hidden_support_field
producer_mutation_boundary_violation
direct_state_or_topology_rewrite
unauthorized_identity_acceptance_event
identity_claim_promotion
agency_claim_promotion
```

Blocked claim flags remain false unless a later experiment separately validates
them:

```text
semantic_choice_claim_allowed
agency_claim_allowed
agentic_like_claim_allowed
intention_claim_allowed
memory_or_trail_claim_allowed
goal_proxy_regulation_claim_allowed
movement_claim_allowed
locomotion_like_claim_allowed
biological_claim_allowed
ant_colony_claim_allowed
identity_acceptance_claim_allowed
rc_identity_collapse_claim_allowed
personhood_claim_allowed
unrestricted_identity_claim_allowed
unrestricted_movement_claim_allowed
```

## Topology Ladder

N07 treats topology design as part of the evidence object, not as a neutral
container. Each topology should isolate one identity gate so support,
stability, attractivity, invariance, reflexive closure, and compatibility do
not collapse into one vague persistence observation.

```text
T0 label-only null topology:
    named node or region without runtime-visible support evidence. Ceiling ID0.

T1 support-area fixture topology:
    declared support nodes, edges, ports, lineage status, event keys, digest,
    and budget fields. Ceiling ID1.

T2 stable local well topology:
    support area with declared retention / well / persistence proxy and exact
    budget accounting. Ceiling ID2.

T3 attractor-neighborhood topology:
    declared neighborhood U whose flux converges toward the support area under
    wrong-polarity, subthreshold, wrong-basin, and budget controls. Ceiling
    ID3.
    A single flux window is only a first-pass attractivity candidate. Stronger
    T3 evidence requires multi-source, multi-window convergence from U, with
    distance/potential decrease or equivalent runtime-visible approach
    evidence and controls against hidden route steering.

T4 no-mutation invariance topology:
    repeated cycles and mild perturbation without topology lineage complexity.
    Ceiling ID4.

T5 lineage-current invariance topology:
    topology changes are allowed only if support remains lineage-current
    through surface lineage and topology-state reabsorption. Ceiling ID4.
    Stronger T5 stress evidence may include split and lineage-authorized birth
    events across more than the minimum proper-time window count, but birth is
    still topology lineage only, not identity acceptance or agency.
    Support overlap under topology change is lineage-weighted over the
    declared lineage transfer map; literal node-set overlap must be serialized
    separately so transported support is not mistaken for set intersection.

T6 reflexive-closure topology:
    re-entry updates artifact-visible basin evidence and later cycles consume
    the updated evidence. Ceiling ID5. Current Iteration 7 evidence is
    experiment-local probe evidence. Iteration 7-B strengthens this to
    source-backed artifact-derived T6 evidence from serialized state rows plus
    digest-linked experiment-local packet/producer records. Native runtime
    reflexive-closure support remains false.

T7 compatibility topology:
    nearby modes coexist without destructive interference, ambiguous overlap,
    hidden support, incompatible lineage, or budget discontinuity. Ceiling
    ID5 or ID6 depending artifact-only replay completeness.
```

The first N07 fixture manifest should freeze only these canonical families:

```text
n07_T1_support_area_minimal
n07_T2_stable_well_basin
n07_T3_attractor_neighborhood
n07_T5_lineage_current_invariance
n07_T6_reflexive_closure
```

T4 no-mutation recurrence remains deferred as a separate baseline. Later
topologies derive from these families. Avoid a first positive lane that
combines route arbitration, topology mutation, oscillators, movement traces,
and reflexive closure in one fixture; such a lane would be hard to diagnose.
Also avoid treating an authored central node as identity. The candidate must
be a runtime coherence basin supported by evidence, not a fixture label.

## Composite Topology Suite

Primitive topology families are unit tests for the identity taxonomy. They make
the gates legible. They are not the final experiment shape.

N07 should also include composite identity ecologies: topologies that combine
primitive blocks and then classify the result against the ID ladder. The rule
is:

```text
primitive fixtures prove the gates are legible;
composite fixtures prove the taxonomy is useful.
```

Composite cases should be recorded as evidence classifiers, not as automatic
identity promotions:

```text
C1 recurrent single-basin identity candidate:
    support + stable well + attractor U + re-entry loop. Distinguishes ID4
    cycle persistence from ID5 reflexive self-maintenance.

C2 lineage-current topology-mutating identity candidate:
    support + stable well + attractor U + topology split + lineage-current
    support. Distinguishes stale node/label continuity from lineage-current
    basin continuity.

C3 competing-basin compatibility candidate:
    A basin + B basin + shared neighborhood U + compatibility/interference
    lane. Tests whether one candidate remains coherent near other modes.
    This is the planned post-Iteration-8 N07 continuation, not part of the
    current C1/T6 single-basin closeout.

C4 route-fed but route-independent identity candidate:
    N06-style route arbitration feeds a candidate basin, while route selection
    remains evidence context only. A route is not identity.

C5 movement-carried but movement-independent identity candidate:
    N04-style topology-mutating movement carries or perturbs basin support,
    while movement remains evidence context only. Movement is not identity
    acceptance.

C6 parent/child refinement identity-boundary candidate:
    parent basin + child basin/refinement + lineage + compatibility. Tests
    when refinement preserves parent identity and when a child basin becomes a
    separate candidate.
```

Every composite topology must emit a gate vector:

```text
support
stability
attractivity
invariance
lineage_current
reflexive_closure
compatibility
artifact_replay
```

Gate values are `pass`, `fail`, `blocked`, `not_measured`, or
`not_applicable`. The derived ID ceiling comes from the weakest required gate
and the primary blocker, not from the topology name. Any row above ID0 must use
`candidate_identity_carrier_type = coherence_basin`; surface rows, deformation
tokens, boundary signals, routes, and movement traces are evidence context
only.

## Current Iteration 8-10+ Scope

Iteration 8 closes the current source-backed C1/T6 chain. It should reconstruct
the single-basin support, stability, attractivity, invariance, reflexive
closure, and proper-time evidence from artifacts only, then freeze the current
ceiling at ID5 without importing C3 compatibility as a passed gate.

Iteration 9 opens the C3/T7 compatibility continuation:

```text
Iteration 9:
    design the competing-basin fixture and freeze compatibility metrics,
    support-area digest replay inputs, source-control replay requirements, and
    frozen ID row fields;

Iteration 9-B:
    run A-basin/B-basin/shared-U compatibility and interference probes,
    emitting source-backed probe/control rows with gate-specific ceilings;

Iteration 9-B2:
    stress the 9-B leakage/support-loss boundary over repeated windows and
    record whether one-window compatibility survives longer-horizon pressure;

Iteration 9-C:
    replay and close out the short-window evidence chain from artifacts only,
    including the 9-B one-window compatibility pass and the 9-B2 prolonged
    stress blocker, without treating this as persistent C3 compatibility;

Iterations 10+:
    reuse the 1-9 evidence to design and test a compatibility/recovery regime
    that can survive over longer periods.
```

C3 asks whether a candidate basin remains coherent near other modes. It may
strengthen the N07 identity candidate in a bounded window, but 9-B2 shows that
one-window compatibility is not enough to claim persistent C3 compatibility.
It is not identity acceptance, RC identity collapse, agency, semantic choice,
biological identity, personhood, or unrestricted identity.

In C3, "competing" means structurally coupled alternatives on the same
coherence/flux field, not goal-directed or agentic competition. Basin A and
Basin B share or border a local neighborhood `U`, so coherence, flux, support
evidence, or basin legibility can be captured by, leaked into, or disturbed by
either basin. The C3 question is whether Basin A remains distinct, coherent,
and artifact-replayable as A when Basin B is source-backed and present in the
same shared-`U` compatibility fixture.

The current C3/T7 result must be read as:

```text
Iterations 1-9:
    short-window source-backed identity and compatibility evidence;

Iteration 9-B2:
    prolonged no-recovery stress blocks persistent C3 compatibility at
    wrong_basin leakage;

Iteration 9-C:
    short-window artifact closeout only;

Iterations 10+:
    long-horizon survivable compatibility search.
```

Iteration 9 inherits the stricter Iteration 8 closeout rule: source artifacts,
not visual cards or fixture names, carry evidence; controls are replayed from
probe artifacts; and any closeout row must keep the frozen ID schema, frozen
becoming tags, and false claim flags.

## N07 Identity Ladder

The N07 ladder is evidence classification, not claim permission.

```text
ID0:
    no identity evidence; labels, node ids, or support names only.

ID1:
    runtime-visible support area candidate.

ID2:
    stable basin candidate with local well / curvature / persistence evidence.

ID3:
    attractor candidate: flux from a declared neighborhood converges into the
    support area under exact budget accounting.

ID4:
    invariant basin candidate: support and identity evidence persist across
    repeated cycles, perturbations, or declared lineage maps.

ID5:
    reflexively self-maintaining identity candidate: re-entry into the basin
    maintains or strengthens the basin using runtime-visible state, not hidden
    fixture logic. This requires later proper-time cycles to consume the
    updated basin evidence digest and does not by itself authorize identity
    acceptance, RC identity collapse, agency, or native identity support.

ID6:
    artifact-only RC identity acceptance candidate: the full support ->
    stability -> attractivity -> invariance -> closure -> compatibility chain
    replays from artifacts, with controls and clean claim boundaries.
```

Do not read `ID6` as broad identity acceptance, personhood, agency, or
biological identity. It is an experiment-local RC identity candidate ceiling.

## Observable Mapping

N07 may use existing LGRC/N04/N06 surfaces, but it must record which surface
each identity claim uses.

Allowed evidence surfaces:

```text
native_lgrc_telemetry
native_causal_pulse_substrate_surface
native_route_arbitration_artifacts
topology_state_reabsorption_artifacts
surface_lineage_artifacts
proper_time_identity_evaluation_artifacts
motion_identity_diagnostic_artifacts
experiment_local_identity_gate_records
```

The preferred path is native when available. Experiment-local identity gate
records may support exploratory evidence only; they cannot be described as
pure native LGRC identity support.

## Claim Boundary

N07 keeps these false unless a later experiment separately validates them:

```text
semantic_choice_claim_allowed = false
agency_claim_allowed = false
agentic_like_claim_allowed = false
intention_claim_allowed = false
memory_or_trail_claim_allowed = false
goal_proxy_regulation_claim_allowed = false
movement_claim_allowed = false
locomotion_like_claim_allowed = false
biological_claim_allowed = false
ant_colony_claim_allowed = false
identity_acceptance_claim_allowed = false
rc_identity_collapse_claim_allowed = false
personhood_claim_allowed = false
unrestricted_identity_claim_allowed = false
unrestricted_movement_claim_allowed = false
```

N07 may discuss agency only as a boundary condition from the theory: agency-like
phenomenology requires identity plus locally irreducible collapse/choice from
an internal vantage point. N07 does not prove agency.

## Starting Point

N06 closed at:

```text
strongest_supported_sc_level = SC6
strongest_claim_ceiling = artifact_only_semantic_route_choice_candidate
semantic_choice_claim_allowed = false
```

N07 starts from that clean boundary and asks:

```text
Can the selected or recurrent basin be validated as the same RC identity
attractor across time, perturbation, and topology/lineage contexts?
```

## Planned Artifacts

```text
implementation/RCIdentityAttractorInvarianceImplementationPlan.md
implementation/RCIdentityAttractorInvarianceImplementationChecklist.md
configs/n07_fixture_manifest_v1.json
outputs/n07_iteration_*.json
reports/n07_iteration_*.md
```
