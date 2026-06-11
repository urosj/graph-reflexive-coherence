# N07 RC Identity Attractor Invariance Implementation Plan

This document records the implementation plan for
`2026-05-N07-rc-identity-attractor-invariance`.

N07 asks whether a basin in LGRC can be validated as an RC identity attractor:
a stable, attractive, invariant, reflexively closed, coherence-compatible
region of the coherence dynamics.

## Scope

N07 is experiment-local unless a separate Phase 8/core task is opened. Scripts,
configs, reports, and outputs should live under:

```text
experiments/2026-05-N07-rc-identity-attractor-invariance/
```

Do not change `src/*` for N07 without stopping and opening a separate Phase 8
implementation task. Existing LGRC9V3 identity, route-arbitration, topology,
surface-lineage, topology-state reabsorption, packet ledger, telemetry,
snapshot, and artifact-replay surfaces may be used, but N07 experiment-local
code must not silently redefine their semantics.

All runtime mutation in N07 must stay behind existing LGRC boundaries.
Experiment-local scripts may build fixtures, run validators, and classify
artifacts, but they must not mutate node coherence, edge state, packet ledgers,
or topology outside `step()` and committed topology machinery. Topology changes
must consume committed topology events and lineage/reabsorption artifacts, not
report-side rewrites.

## Roadmap Position

```text
N05:
    coherence waves and oscillators

N06:
    semantic route choice through context-conditioned native route selection

N07:
    RC identity, support area, attractor invariance, identity-acceptance
    boundary

N08:
    memory / trail / affordance formation

N09:
    goal-proxy regulation
```

N07 should hand off to N08 only after the identity ceiling is explicit and all
claim boundaries remain clean.

## Theory Stack

N07 uses all identity-bearing theory layers:

```text
papers/2025-11-RC-IdentityChoiceAbundance.md:
    continuous RC identity, attractor basins, reflexive closure, collapse,
    local irreducibility / agency boundary.

papers/2025-12-GRC-V2.md:
    graph identity basins as directed-flux attraction domains around sinks,
    spark detection, conservation, and abundance.

papers/2026-02-GRC-V3.md:
    basin-attribute nodes with gradient, Hessian, net flux, basin mass,
    identity id, parent id, and depth.

papers/2026-04-GRC-9.md:
    nine-port basin charts, spark/refinement mechanics, child identity
    emergence, and the rule that mechanical refinement is not identity fission
    by itself.

papers/2026-05-LGRC-9.md:
    local proper time, causal histories, lineage maps, packet ledger
    conservation, and proper-time identity windows.

papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md:
    identity-carrier taxonomy and the boundary between surface evidence,
    deformation tokens, boundary signals, and runtime coherence basins.

Arc of Becoming methodology:
    Classification of Becoming
    Interrogation of Becoming
    Naturalization of Becoming
    Cultivation of Becoming
    observation-first classification, bounded probes as questions,
    probe/support withdrawal, naturalization, and activity-history integration.
```

The core RC paper defines the mathematical identity object. GRC and GRC-v3
define the discrete basin object. GRC-9/GRC9V3 define the nine-port basin-chart
substrate. LGRC/LGRC9V3 define the causal/proper-time and lineage requirements
for runtime identity evidence. The Arc of Becoming methodology defines how to
interpret unknown results without promoting probe-supported expression into
native identity.

## Becoming-Method Discipline

N07 must classify what appears before deciding what to probe next. A result can
be useful without promoting identity. Every row should record:

```text
becoming_class_status =
    observation_tag | reusable_class | generative_class |
    coherence_preserving_class

probe_role =
    none | diagnostic_probe | constructive_probe | boundary_probe |
    withdrawal_probe | naturalization_probe

boundary_rung =
    eligible_state | event | substrate_consequence | structured_consequence |
    source_specific_expression | recurrence_or_continuation |
    natural_regime_expression

support_dependency_status =
    not_tested | probe_dependent | weakened_support_survives |
    regime_assisted | endogenous_precondition_candidate |
    native_expression_candidate | recurrent_native_expression_candidate

withdrawal_test_status =
    not_tested | support_weakened_passed | support_removed_passed |
    support_removed_failed | not_applicable
```

The naturalization rungs are recorded as `Nat0` through `Nat6` to avoid
confusion with experiment ids:

```text
Nat0:
    probe-dependent expression.

Nat1:
    expression survives weaker support but not removal.

Nat2:
    regime-assisted expression still requiring a trigger.

Nat3:
    endogenous precondition formation.

Nat4:
    native expression under declared conditions.

Nat5:
    recurrent native expression.

Nat6:
    self-interrogating regime: the system endogenously generates a boundary
    condition, perturbation class, or support function equivalent to the
    original probe.
```

N07 does not need to reach any naturalization rung to close. The rung is a
scope tag that prevents overclaiming. Probe-supported identity evidence remains
probe-supported until withdrawal and endogenous support generation are shown.

## Theory-To-Experiment Translation

The theory source defines RC identity as an invariant attractor basin of the
coherence dynamics. N07 freezes the following translation.

### 1. Coherence Budget

Theory:

```text
C_sys(t) = integral_{Omega_t} C(x,t) dV_g
dC_sys/dt = 0
```

LGRC observable:

```text
sum(active node coherence)
+ in_flight_packet_total
== conserved_budget_total
```

Budget conservation is necessary for every ID level above ID0. It is never
sufficient for identity.

### 2. Support Area

Theory:

```text
A subset Omega_t
```

LGRC observable:

```text
support_area = declared set of nodes / ports / edges / lineage ids carrying
artifact-visible experiment-local basin evidence
```

Support area evidence must include:

```text
support_area_id
support_node_ids
support_edge_ids
support_port_ids if port-local
support_surface_digest
lineage_status
event_time_key
scheduler_event_index
budget_before / budget_after / budget_error
```

A support area is a carrier, not an identity claim.

Support-area digests and duplicate suppression use canonical JSON with sorted
keys over:

```text
support_area_id
candidate_identity_carrier_type
support_node_ids sorted
support_edge_ids sorted
support_port_ids sorted when present
lineage_status
lineage_map_digest when present
support_surface_digest
event_time_key
scheduler_event_index
budget_surface
budget_before
budget_after
budget_error
```

The digest field itself is excluded from the digest input. A duplicate support
row is any row with the same support-area idempotency key:

```text
support_area_id
support_area_digest
event_time_key
scheduler_event_index
lineage_status
```

GRC/GRC-v3 requirements:

```text
support_area must identify its basin chart / sink relation when available.
basin_attribute_bundle must record gradient, Hessian/well proxy, net flux,
basin mass, identity id, parent id, and depth when available.
```

### 3. Stability

Theory:

```text
grad C(x*) = 0
Hess(C)|_{x*} positive definite
```

LGRC observable:

```text
stable basin/well proxy around the support area
```

Allowed proxies:

```text
proper-time persistence window
local inflow dominance
support-area mass retention
curvature/well score if serialized by policy
discrete Hessian / second-difference proxy if declared in manifest
```

If current LGRC cannot express a needed potential, Hessian, or curvature proxy
as serialized policy, record a native-policy blocker instead of hiding the
calculation in report code.

An experiment-local proxy is allowed only when the proxy formula, threshold,
input fields, and digest scope are declared in the fixture manifest before the
run. If any required observable uses an experiment-local proxy, the row must
record the corresponding native-policy blocker and mark the result
`experiment_local`, not pure native LGRC identity support.

GRC-v3/GRC9V3 requirement:

```text
stability should prefer basin-attribute Hessian / signed-Hessian evidence over
ad hoc report-side curvature scores.
```

### 4. Attractivity

Theory:

```text
for x0 in U, Phi_t(x0) approaches A
```

LGRC observable:

```text
neighborhood flux and packet work converge into the support area
```

Attractivity requires a declared neighborhood and controls showing that
non-neighborhood, wrong-polarity, subthreshold, or budget-invalid flux does not
count.

### 5. Invariance

Theory:

```text
Phi_t(A) = A
```

LGRC observable:

```text
support area remains the same identity carrier across cycles, perturbations,
or explicit topology lineage maps
```

In topology-changing contexts, invariant support means lineage-current support,
not stale node ids.

The fixture manifest must declare:

```text
metric_id = n07_invariance_support_overlap_lineage_v1
overlap_computation_method =
    lineage_weighted_jaccard_over_declared_lineage_transfer_map
support_overlap_kind = lineage_weighted
lineage_current_overlap_method =
    fraction_of_lineage_mapped_support_nodes_retaining_current_support_membership
literal_node_set_overlap_serialized = true
support_overlap_threshold
lineage_current_overlap_threshold
proper_time_persistence_threshold
perturbation_magnitude
perturbation_window
destructive_perturbation_blocker
native_policy_available = false
native_policy_blocker = native_identity_invariance_policy_missing
```

Default thresholds are not inferred from successful output. If a threshold is
missing, the row fails with `identity_threshold_missing`.

Iteration 6 treats invariance evaluation as an experiment-local identity gate
over runtime-visible support, perturbation, and lineage evidence. The current
native LGRC topology-lineage and topology-state reabsorption support may be
cited as infrastructure context, but native identity-invariance policy remains
missing and must not be implied from topology support. Required controls are
`stale_node_id_replay`, `missing_topology_state_reabsorption`,
`lineage_map_scrambled`, `support_drift_beyond_threshold`,
`budget_discontinuity`, and `identity_claim_promotion`.

Iteration 6-B is a stress extension of the same ID4 gate. It should include a
longer lineage-proper-time sequence than the minimum Iteration 6 pass, with
committed topology split and lineage-authorized birth events. The born support
node must have explicit parent lineage and topology-state reabsorption
evidence. Birth here means topology lineage only; it must not be recorded as
identity acceptance, RC identity collapse, reproduction, agency, or native
identity support. 6-B may strengthen the ID4 invariant-basin candidate, but it
must not promote to ID5 because reflexive closure and later-cycle consumption
of updated basin evidence are Iteration 7 concerns.

LGRC requirement:

```text
identity windows are proper-time or lineage-proper-time windows, not raw
scheduler or checkpoint windows.
```

### 6. Reflexive Closure

Theory:

```text
coherence arriving in A contributes to maintaining or deepening A
```

LGRC observable:

```text
re-entry into the support area updates artifact-visible basin evidence that
later cycles can consume. In the current Iteration 7 fixture this is
experiment-local probe evidence, not native LGRC reflexive-closure observation.
```

Producer scheduling may help explore this mechanism, but producers must not
mutate identity, coherence, topology, or claim flags.

The default reflexive-closure metric is:

```text
reentry_coherence_into_support > 0
basin_evidence_after_reentry >= basin_evidence_before_reentry
later_cycle_consumed_updated_basin_evidence = true
budget_error == 0
```

`basin_evidence` must be a manifest-declared bundle such as support-area mass,
retention score, native basin attribute digest, or proper-time persistence
score. If the later cycle uses the pre-reentry digest, the row fails with
`closure_not_consumed_by_later_cycle`.

### 7. Coherence Compatibility

Theory:

```text
<grad C, grad C_i>_K >= 0
```

LGRC observable:

```text
candidate basin coexists with nearby modes without destructive interference,
budget discontinuity, negative state, hidden source terms, or incompatible
lineage
```

Compatibility controls must include destructive-interference, wrong-basin,
ambiguous-overlap, and hidden-support cases.

The default discrete compatibility metric is:

```text
budget_error == 0
min_active_node_coherence >= 0
candidate_support_overlap_with_competitor <= declared_overlap_threshold
lineage_conflict_detected = false
hidden_support_source_detected = false
destructive_interference_score <= declared_interference_threshold
```

Compatibility controls may be deferred until the T7/C3 topology families are
implemented, but the manifest must still define the metric and blocker names in
Iteration 2.

Identity-carrier requirement:

```text
surface rows, deformation tokens, and boundary signals may support an identity
case, but only runtime coherence basins are eligible identity carriers.
```

## Topology Design Policy

N07 topologies are gate-isolating fixtures. Topology design is part of the
experiment, not a background container. A positive topology should have one
candidate basin that is visible enough to emit support evidence, deep enough
to test stability, open enough to attract flux from a declared neighborhood,
bounded enough not to absorb everything, lineage-trackable when topology
changes, and re-entry-sensitive when reflexive closure is tested.

Negative topologies should each break one property and fail with a distinct
primary blocker. Do not start with a rich omnibus topology that combines route
arbitration, topology mutation, oscillators, movement traces, and identity
closure in one positive lane.

Every topology family in the manifest must declare:

```text
topology_family_id
target_id_level
candidate_identity_carrier_type
candidate_runtime_coherence_basin
support_area
neighborhood_U
gate_under_test
primary_positive_metric
paired_negative_control_topology
expected_primary_blocker
expected_maximum_id_ceiling
topology_mutation_occurs
lineage_current_support_required
budget_surface
claim_flags
```

The topology ladder is:

```text
T0:
    label-only null topology. Ceiling ID0.

T1:
    support-area fixture topology. Ceiling ID1.

T2:
    stable local well topology. Ceiling ID2.

T3:
    attractor-neighborhood topology. Ceiling ID3.

T4:
    no-mutation invariance topology. Ceiling ID4.

T5:
    lineage-current invariance topology. Ceiling ID4.

T6:
    reflexive-closure topology. Ceiling ID5.

T7:
    compatibility topology. Ceiling ID5 or ID6 only if replay completeness
    also passes.
```

Iteration 2 should freeze the canonical topology families needed by the first
identity ladder pass:

```text
n07_T1_support_area_minimal
n07_T2_stable_well_basin
n07_T3_attractor_neighborhood
n07_T5_lineage_current_invariance
n07_T6_reflexive_closure
```

T4 is deferred from the first manifest because it is the no-mutation
invariance baseline for later recurrence probes. T5 is included early because
lineage-current support is the higher-risk boundary inherited from N04/N06.
T6 is included once Iteration 7 starts so reflexive closure is not recorded
under the T5 lineage-current family. T4 should still be implemented before
interpreting any topology-free recurrence as stronger than ID4.

Controls should be derived from those families instead of unrelated fixtures.
The central controls are:

```text
label_only_null_topology
missing_support_area
external_label_only
duplicate_support_row
unstable_basin_no_local_well
non_attractive_flux
wrong_polarity
subthreshold_flux
wrong_basin
hidden_route_context_steering
budget_discontinuity
stale_node_id_replay
missing_topology_state_reabsorption
lineage_map_scrambled
support_drift_beyond_threshold
destructive_interference
ambiguous_overlap
hidden_support_field
hidden_potential_or_report_side_well_score
posthoc_threshold_change
identity_threshold_missing
wrong_support_area
no_reentry
closure_not_consumed_by_later_cycle
improper_proper_time_threshold
failed_persistence
producer_mutation_boundary_violation
direct_state_or_topology_rewrite
unauthorized_identity_acceptance_event
identity_claim_promotion
agency_claim_promotion
```

## Composite Topology Policy

Primitive topology families test individual identity gates. Composite topology
families test taxonomy placement when several identity-like ingredients
coexist. A composite topology must not assign an ID level by name; it must
derive the ceiling from an observed gate vector.

Every composite topology must declare:

```text
composite_topology_id
primitive_blocks_combined
expected_id_ceiling
informative_lower_ceilings
false_positive_confusion_under_test
imported_prior_experiment_surfaces
imported_surfaces_are_evidence_only
identity_carrier_surface
gate_vector
derived_id_ceiling
primary_blocker
claim_flags
```

The gate vector is:

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

Initial composite suite:

```text
C1 recurrent single-basin identity candidate:
    support + stable well + attractor U + re-entry loop. Tests ID4 vs ID5.

C2 lineage-current topology-mutating identity candidate:
    support + stable well + attractor U + topology split + lineage-current
    support. Tests stale node/label continuity vs lineage-current basin
    continuity.

C3 competing-basin compatibility candidate:
    A basin + B basin + shared neighborhood U + compatibility/interference
    lane. Tests compatibility and ambiguous-overlap blockers.

C4 route-fed but route-independent identity candidate:
    N06-style route arbitration + candidate basin + recurrent support area.
    Route selection is imported context only, not identity evidence.

C5 movement-carried but movement-independent identity candidate:
    N04 topology-mutating movement fixture + candidate basin support +
    lineage-current identity window. Movement is imported context only, not
    identity acceptance.

C6 parent/child refinement identity-boundary candidate:
    parent basin + child basin/refinement + lineage + compatibility. Tests
    whether refinement preserves parent identity, creates a child candidate, or
    remains only mechanical refinement.
```

Composite topology classification should be added only after the primitive
gate fixtures are legible enough to make failures diagnosable.

## ID-Ladder Row Schema And Gate Vector

Iteration 1 must freeze the ID-ladder row schema before probes run. The minimum
row fields are:

```text
row_id
id_level
topology_family_id
composite_topology_id
candidate_identity_carrier_type
identity_carrier_surface
support_area_id
support_area_digest
source_artifacts
source_artifact_sha256
source_reports
runtime_family
implementation_surface
gate_vector
derived_id_ceiling
primary_blocker
native_support_status
native_observables_used
experiment_local_observables_used
native_policy_blockers
becoming_class_status
probe_role
boundary_rung
support_dependency_status
withdrawal_test_status
naturalization_rung
activity_history_digest
claim_flags
visual_reference
visual_is_evidence_source
```

`candidate_identity_carrier_type` must be `coherence_basin` for any ID1-ID6
candidate row. Rows whose strongest carrier is `surface_row`,
`deformation_token`, or `boundary_signal` may be supporting evidence rows only;
they cannot derive an ID ceiling above ID0.

Gate-vector fields are ordinal:

```text
pass
fail
not_applicable
not_measured
blocked
```

`blocked` requires a `primary_blocker`. `pass` requires source artifact
evidence and any manifest-declared threshold. The ceiling algorithm is
weakest-gate, ordered by the identity ladder:

Conditional gates are represented by the ceiling algorithm, not by extra
gate-vector values. In particular, `lineage_current` must be `pass` when
`topology_mutation_occurs = true`; otherwise it is `not_applicable`.

Schema formats and enums:

```text
native_support_status =
    pure_native | mixed_native_experiment_local | experiment_local | blocked

runtime_family =
    LGRC9V3 | experiment_local | hybrid_lgrc9v3_experiment_local |
    not_applicable

implementation_surface =
    experiment_local | native_lgrc_telemetry |
    native_causal_pulse_substrate_surface | surface_lineage_transport |
    topology_state_reabsorption | native_route_arbitration |
    proper_time_identity_evaluation | artifact_only_validator |
    not_applicable

source_artifacts =
    list of objects with name, path, exists, sha256, and available status /
    claim_ceiling / primary_blocker fields

source_reports =
    list of objects with name, path, exists, sha256

native_observables_used =
    list of runtime-visible LGRC/native observable ids consumed by the row

experiment_local_observables_used =
    list of declared experiment-local observable ids consumed by the row

activity_history_digest =
    SHA-256 of canonical JSON over orient/observe/classify/probe/withdraw/
    naturalize/integrate events; null if no activity history exists

visual_reference =
    optional relative path or null

visual_is_evidence_source =
    boolean; false unless the visual itself is backed by source artifact
    evidence and declared as evidence
```

```text
ID0:
    no runtime-visible coherence-basin support, or carrier is not
    coherence_basin.

ID1:
    support = pass.

ID2:
    support = pass and stability = pass.

ID3:
    support = pass, stability = pass, and attractivity = pass.

ID4:
    ID3 gates pass and invariance = pass. If topology changes,
    lineage_current must also pass.

ID5:
    ID4 gates pass and reflexive_closure = pass.

ID6:
    ID5 gates pass, compatibility = pass, artifact_replay = pass, and all
    controls fail with distinct primary blockers.
```

Any `fail`, `blocked`, or required `not_measured` gate sets the derived ceiling
to the strongest preceding ID level and records the gate as the primary blocker
unless a more specific blocker is declared.

Boundary-rung progression is descriptive and must not promote claims:

```text
ID0:
    eligible_state or event, depending on whether any runtime-visible carrier
    evidence exists.

ID1:
    substrate_consequence; a support area is visible as a substrate-local
    consequence but is not yet stable identity evidence.

ID2:
    substrate_consequence; stability/local-well evidence remains tied to the
    substrate support object.

ID3:
    structured_consequence; support + stability + attractivity form a
    structured basin consequence, still probe-supported and not invariant.

ID4:
    recurrence_or_continuation; invariance requires repeated-cycle,
    perturbation, or lineage-current continuation evidence.

ID5:
    recurrence_or_continuation; reflexive closure requires later cycles to
    consume updated basin evidence.

ID6:
    source_specific_expression; artifact replay and compatibility can freeze a
    source-backed identity candidate, but not agency or unrestricted identity.
```

ID5 reflexive closure is frozen as a descriptor gate, not an identity-acceptance
claim. The reflexive-closure metric is
`n07_reflexive_closure_reentry_v1` and requires all of:

```text
reentry_coherence_into_support > 0
basin_evidence_after_reentry >= basin_evidence_before_reentry
later_cycle_consumed_updated_basin_evidence = true
budget_error == 0
```

The source-backed basin evidence bundle is `support_area_mass`,
`retention_score`, `proper_time_persistence_score`, and
`basin_evidence_digest`. Proper-time persistence requires at least three
proper-time evidence points and must not be substituted with a raw scheduler
window. Native reflexive-closure policy is currently unavailable
(`native_reflexive_closure_policy_missing`), and identity acceptance remains
blocked unless a native identity-acceptance contract exists
(`unauthorized_identity_acceptance_event`). Iteration 7 controls are
`no_reentry`, `closure_not_consumed_by_later_cycle`,
`improper_proper_time_threshold`, `failed_persistence`,
`unauthorized_identity_acceptance_event`,
`producer_mutation_boundary_violation`, and `agency_claim_promotion`.

## Identity Ladder

```text
ID0:
    no identity evidence; external labels only.

ID1:
    runtime-visible support area candidate.

ID2:
    stable basin candidate.

ID3:
    attractor candidate with neighborhood flux convergence.

ID4:
    invariant basin candidate across cycles, perturbations, or lineage.

ID5:
    reflexively self-maintaining identity candidate.

ID6:
    artifact-only RC identity acceptance candidate.
```

ID levels are evidence classifications. They do not automatically set claim
flags.

## Claim Discipline

Allowed if supported by gates:

- support-area candidate;
- stable basin candidate;
- attractor candidate;
- invariant basin candidate;
- reflexively self-maintaining identity candidate;
- artifact-only RC identity acceptance candidate.

Blocked in N07 unless explicitly and separately validated:

- agency;
- agentic-like behavior;
- intention;
- semantic choice promotion;
- memory/trail formation;
- goal-proxy regulation;
- movement;
- locomotion-like behavior;
- biological behavior;
- ant-colony behavior;
- RC identity collapse;
- runtime identity acceptance;
- personhood;
- unrestricted identity acceptance;
- unrestricted movement.

N07 may cite the RC theory of local computational irreducibility only as
motivation and boundary. It must not claim agency from identity evidence.

N07 may emit an experiment-local ID6 closeout row only if artifact-only replay
passes and the required compatibility gate is passed over the explicitly
declared scope. For the current C1/T6 single-basin chain, compatibility is
deferred to Iteration 9, so Iteration 8 must freeze the ceiling at ID5 even if
artifact replay passes. After Iteration 9-B2, persistent C3 compatibility is
known to be blocked under prolonged no-recovery stress, so Iteration 9-C must
not treat C3 as closed ID6 evidence. Any future ID6 row requires a later
long-horizon compatibility/recovery branch to pass and replay from artifacts.
Any ID6 row is an evidence classification, not a runtime identity-acceptance
event and not unrestricted identity acceptance. A runtime identity-acceptance
event must not be emitted unless an explicit native contract exists and the row
records the policy id; otherwise the control fails with
`unauthorized_identity_acceptance_event`.

## Planned Iterations

```text
Iteration 0:
    planning and handoff

Iteration 1:
    baseline and theory/schema inventory

Iteration 2:
    topology design policy, fixture manifest, and discrete RC observable
    mapping

Iteration 3:
    ID1 support-area candidate

Iteration 4:
    ID2 stability / local well candidate

Iteration 5:
    ID3 attractivity / flux convergence

Iteration 5-B:
    ID3 attractivity stress / multi-source, multi-window convergence

Iteration 6:
    ID4 invariance across cycles, perturbations, and topology lineage

Iteration 6-B:
    ID4 split/birth topology invariance stress

Iteration 7:
    ID5 reflexive closure design/probe and proper-time identity persistence
    boundary

Iteration 7-B:
    ID5 source-backed artifact-derived T6 reflexive closure from serialized
    state rows plus digest-linked experiment-local packet/producer records

Iteration 8:
    C1/T6 artifact-only replay and ID5 closeout for the current source-backed
    single-basin chain

Iteration 9:
    C3/T7 competing-basin compatibility fixture design. Freeze A/B support
    areas, shared-U compatibility metrics, support-area digest replay inputs,
    source-control replay requirements, and frozen ID row fields before any
    probe runs.

Iteration 9-B:
    C3 compatibility/interference run with A basin, B basin, shared
    neighborhood U, and distinct destructive-interference / ambiguous-overlap
    controls. Emit real source probe/control rows with gate-specific derived
    ceilings; do not synthesize blockers in the closeout.

Iteration 9-B2:
    Prolong the 9-B compatibility boundary with a repeated-window stress model.
    Record whether the 4% wrong-basin leakage and support loss remain bounded
    over longer pressure. This is stress evidence, not native LGRC dynamics and
    not ID6.

Iteration 9-C:
    Short-window artifact-only replay and evidence closeout for Iterations
    1-9/9-B/9-B2. Replay controls from source artifacts, recompute A/B
    support-area digests, validate semantic consistency, require all frozen ID
    row fields, and keep claim flags false. Record 9-B as one-window
    compatibility evidence and 9-B2 as prolonged-stress failure; do not close
    persistent C3 compatibility.

Iteration 10:
    Long-horizon compatibility design. Reuse the 9-B and 9-B2 boundary to
    freeze survivability criteria, recovery/re-separation hypotheses, leakage
    budgets, support-retention thresholds, stress horizons, and a
    change-function / trajectory contract before new probes. The fixed horizon
    is a measurement frame, not the evidence interpretation: endpoint pass/fail
    gates claims, while leakage, support-retention, interference, and budget
    trajectories classify what compatibility regime was expressed.

Iteration 11:
    Long-horizon compatibility/recovery learning series. Treat 11 as the start
    of an 11-* branch set, not as a single forced final probe. Test whether
    explicit recovery or re-separation mechanisms can keep wrong-basin leakage,
    destructive interference, support drift, and budget drift bounded across
    repeated windows. Emit per-window metric series, first differences, slopes,
    endpoint status, first failure window, and a trajectory regime label; do not
    treat a fixed-window true/false result as sufficient identity evidence.
    Continue with 11-A, 11-B, and later 11-* branches while each branch exposes
    a new regime, blocker, or recovery/re-separation mechanism relevant to
    long-term C3 basin classification.

    C3 redirection for 11-B:
        Connected basins should not be required to express zero leakage. The
        stronger question is whether leakage becomes bounded, non-destructive
        exchange that does not erase either basin. 11-A is therefore incomplete
        not because leakage exists, but because its support, leakage, and
        destructive-interference slopes still degrade. 11-B should test whether
        `neutral_absorber_reservoir_v1` can express
        `bounded_non_destructive_exchange`,
        `bounded_flat_leakage_after_transient`, and
        `dual_basin_survival_with_exchange`.

Iteration 12:
    Artifact-only replay and closeout of the long-horizon compatibility branch
    series. Enter 12 only after the 11-* series has enough source-backed
    trajectory evidence to classify the current long-term C3 basin regime, or
    after a repeated unresolved blocker is recorded as the stop condition. If
    11-* remains blocked, preserve the strongest blocked ceiling; if it passes,
    replay the survivable chain from artifacts before any ID6 wording.

Iteration 13:
    Post-closeout identity-support withdrawal baseline for N10. N07 Iteration
    12 closes the source-specific ID6 bounded-exchange evidence chain, but N09
    preserves the blocker `n07_identity_withdrawal_baseline_not_available`.
    Iteration 13 supplies that missing baseline without reopening broad
    identity theory or promoting runtime identity acceptance. It must replay
    the Iteration 12 support digest and the N09 support-withdrawal handoff,
    then emit support-intact, mild-withdrawal, N09-matched partial-withdrawal,
    and explicit-restoration lanes. The result is a baseline N10 can consume to
    distinguish surviving support, disrupted support, and explicitly restored
    support.
```

Scope boundary:

```text
Iteration 8 closes the current single-basin identity chain. It should not
absorb C3 compatibility work or reclassify unresolved compatibility controls
as passed. Iterations 9 through 9-C close only the short-window C3 evidence
chain: 9-B provides one-window compatibility evidence and 9-B2 blocks
persistent compatibility under prolonged no-recovery stress. Iterations 10+
therefore design and close the long-horizon compatibility regime. Iteration 12
freezes the source-specific ID6 bounded-exchange evidence classification.
Iteration 13 is post-closeout compatibility support for N10: it adds a
withdrawal baseline for consuming identity support in goal-proxy regulation
contexts. None of these iterations may promote identity acceptance, RC identity
collapse, agency, semantic choice, biological identity, personhood, or
unrestricted identity claims.

Long-horizon compatibility follows the Arc-of-Becoming reading that a probe is
not exhausted by its pass/fail endpoint. Following Classification of Becoming,
the record must first classify what property was expressed. Following
Cultivation of Becoming, each probe should sharpen the next question rather
than merely prove or disprove a label. Following Naturalization of Becoming,
stronger future evidence must ask whether compatibility support is regenerated
by the regime itself rather than only supplied by the fixture.
```

Iteration 9 inherits the Iteration 8 artifact standard: visual or fixture
labels are non-authoritative, support-area digests must recompute from declared
inputs, controls must be replayed from source artifacts with their original
gate-specific ceilings, and closeout rows must use the frozen ID row schema and
becoming enum values.

C3 "competition" is a structural compatibility condition, not a choice or
agency claim. Competing basins share or border a local neighborhood `U`, so
coherence, flux, support evidence, or basin legibility can be captured by,
leaked into, or disturbed by either basin. Iteration 9-B asks whether Basin A
is distinct and coherent in one serialized shared-`U` window when Basin B is
source-backed and present. Iteration 9-B2 asks whether that result survives
longer pressure; the current answer is no under no-recovery stress.

## Required Controls

Every positive lane must be paired with controls that fail for distinct primary
blockers from this canonical taxonomy:

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

Controls that require deferred topology families, such as
`destructive_interference` and `ambiguous_overlap`, must be declared in
Iteration 2 and run when T7/C3 compatibility fixtures are implemented. Until
then, they are recorded as deferred controls, not silently omitted.

## Artifact-Only Replay

The final validator should reconstruct:

```text
source packet / flux events
-> support-area row
-> stability evidence
-> attractivity evidence
-> invariance / lineage evidence
-> reflexive-closure evidence
-> proper-time identity evaluation if used
-> identity closeout row
```

without private runtime state.

## Native Policy Caveat

N07 may discover that current LGRC cannot express one of the required RC
observables natively:

```text
custom basin potential
discrete Hessian / curvature well score
support-area compatibility metric
attractor neighborhood definition
reflexive closure update policy
identity-specific artifact replay validator
```

If so, record the native-policy blocker and keep the result experiment-local.
Do not hide missing native support in fixture code.

Partial native support must be explicit. Each row must record:

```text
native_observables_used
experiment_local_observables_used
native_policy_blockers
native_support_status = pure_native | mixed_native_experiment_local |
    experiment_local | blocked
```

If any required observable is experiment-local, the row may still be useful
evidence, but it must not be described as pure native LGRC identity support.

## Iteration 5-B Attractivity Strengthening

Iteration 5 records a first-pass ID3 attractivity candidate from one declared
flux-convergence window. Iteration 5-B strengthens that result before moving to
invariance.

The purpose is to test whether the candidate support area behaves like an
attractor over the declared neighborhood `U`, not merely whether one packet
work window had positive inflow. 5-B should therefore require:

```text
multi_source:
    at least two distinct source points in U converge toward the support area.

multi_window:
    convergence repeats across more than one event/proper-time window.

approach_evidence:
    distance-to-support, potential-decrease, or equivalent runtime-visible
    approach metric improves monotonically or non-increasingly by the declared
    criterion.

retention_after_inflow:
    support-area evidence remains stable after inflow; incoming flux is not
    immediately lost or routed through.

controls:
    non_attractive_flux, wrong_basin, wrong_polarity, subthreshold_flux,
    hidden_route_context_steering, failed_persistence, and
    budget_discontinuity fail with distinct blockers.
```

5-B may keep the same ID3 ceiling if it passes. It should not promote to ID4,
identity acceptance, agency, semantic choice, or native LGRC identity support.
It should record whether current LGRC has a native attractor-neighborhood
policy; if not, keep `native_support_status = experiment_local` and record the
native policy blocker.
