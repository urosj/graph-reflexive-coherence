# N04 Movement Ladders Implementation Plan

This document records the implementation plan for
`2026-05-N04-grc9v3-movement-ladders`.

The experiment asks whether conserved internal pulse dynamics can couple to
basin boundary and geometry to produce identity-preserving movement. It does
not assume that movement exists because N03 produced a native LGRC9V3
self-rearming packet pulse.

## Scope

N04 is experiment-local unless explicitly promoted later. Scripts, configs,
reports, and outputs should live under:

```text
experiments/2026-05-N04-grc9v3-movement-ladders/
```

Do not change `src/*` for N04 without stopping and opening a separate core
implementation task. Existing GRC9V3 and LGRC9V3 runtime surfaces may be used
as execution substrates, but experiment-local code must not silently redefine
their semantics.

## N03 Handoff

N03 provides the following input evidence:

```text
native fixed-topology GRC9V3 proposal flux:
    negative for polarized loop formation on tested fixtures

native LGRC9V3 packetized causal execution:
    positive for D2.3-equivalent self-rearming packet-loop behavior

movement claim:
    not opened in N03
```

Therefore N04 may use the E3 native LGRC9V3 packet loop as a pulse substrate,
but it must independently test movement:

```text
E3 heartbeat != movement
E3 heartbeat + boundary coupling + identity-preserving displacement gates
    may support movement claims if N04 gates pass
```

The synchronous GRC9V3 proposal-flux path remains a useful negative/control
surface, not the positive loop source.

## Core Claim Discipline

Allowed if supported by gates:

- movement response;
- basin drift;
- identity-preserving displacement;
- boundary-coupled movement;
- loop-driven movement;
- conserved pulse-driven displacement;
- movement aftereffect;
- locomotion-like basin dynamics.

Blocked unless a later plan explicitly opens and validates them:

- agency;
- intention;
- decision-making;
- biological locomotion;
- external energy harvesting;
- movement through absolute Euclidean space;
- graph topology change as movement itself.

Adaptive topology may not promote a movement class until fixed-substrate
movement has passed.

## Execution Surfaces

N04 should separate three execution surfaces:

```text
surface_a_fixed_substrate_metrics:
    experiment-local chain/ring/grid fixtures, basin extraction, movement
    observables, controls, and classifier

surface_b_grc9v3_control:
    existing GRC9V3 proposal-flux execution used for nulls/control comparison
    and not promoted as a loop source

surface_c_lgrc9v3_e3_pulse:
    native LGRC9V3 E3 packet-loop pulse used as P4/P5 drive candidate after
    fixed-substrate movement metrics are validated
```

Each report must state the execution surface used.

## Required Gates

The first implementation should preserve the paper's ladders:

```text
M: movement level
T: persistence level
I: identity-continuity level
R: front/rear level
B: boundary-management level
G: shape-preservation level
H: highway/aftereffect level
Q: budget/economy level
F: feedback/control level
```

Minimum quantitative gates for early fixed-substrate claims:

```text
budget_abs_error_max <= epsilon_budget
identity_mass_ratio_min >= identity_mass_ratio_min
centroid_displacement_abs >= displacement_min for M1+
shape_width_relative_change <= 0.15 for G2+
profile_similarity >= 0.8 for G3+
topology_changed = false
```

Movement claims must be downgraded or blocked if identity continuity, budget
conservation, or fixed-topology audit fails.

## Report Schema

Initial reports should use:

```text
movement_ladder_report_v1
```

The paper draft's `grc9v3_movement_ladder_report_v1` name is retained as the
historical draft name, but implementation reports use the runtime-neutral name
above because N04 may include GRC9V3 controls, LGRC9V3 E3 pulse lanes, and
experiment-local fixture runners.

Required top-level fields:

```json
{
  "schema": "movement_ladder_report_v1",
  "run_id": "",
  "runtime_family": "GRC9V3|LGRC9V3|experiment_local",
  "execution_surface": "",
  "native_lgrc9v3_e3_pulse_used": false,
  "native_grc9v3_proposal_flux_control_used": false,
  "substrate": {},
  "loop_dependency": {},
  "drive": {},
  "identity_tracking": {},
  "movement_metrics": {},
  "taxonomies": {},
  "conservation": {},
  "topology": {},
  "gates": {},
  "claim_ceiling": "",
  "blocked_claims": []
}
```

Specialized validation artifacts may include:

```json
{
  "schema": "movement_ladder_report_v1",
  "report_kind": "e3_pulse_import_validation_v1|..."
}
```

`report_kind` is a schema extension used to identify validation/report
subtypes while preserving the runtime-neutral movement report schema.

Conservation fields must distinguish synchronous node-only budgets from
LGRC9V3 packet budgets:

```json
{
  "conservation": {
    "budget_surface": "node_only|node_plus_packet",
    "node_budget": 0.0,
    "in_flight_packet_budget": 0.0,
    "total_budget": 0.0,
    "budget_abs_error_max": 0.0
  }
}
```

For E3 pulse lanes, the budget surface is:

```text
B = sum_i C_i + sum_p C_p
```

where `C_p` is in-flight packet coherence.

If imported E3 artifacts expose only max event budget error and not the exact
node/in-flight split, N04 reports must preserve that limitation explicitly and
must not invent `node_budget`, `in_flight_packet_budget`, or `total_budget`
values.

E3 pulse import uses a local pulse-readiness taxonomy until a broader pulse
taxonomy is promoted:

```text
P0 no pulse metadata
P1 pulse metadata available but inactive
P2 packet activity present without self-rearm evidence
P3 state-triggered packet departure present
P4 self-rearm evidence present below D2.3 control parity
P5 native LGRC9V3 D2.3-equivalent self-rearming packet pulse under controls
```

Movement fixtures must declare coordinate and direction policies:

```json
{
  "coordinate_policy": {
    "node_coordinate_policy": "chain_index|ring_circular|grid_xy|custom",
    "centroid_coordinate_frame": "linear|circular|unwrapped|xy",
    "coordinate_periodic": false,
    "ring_unwrap_policy": "not_applicable|circular_mean|tracked_basin_representative"
  },
  "front_rear_definition": {
    "direction_source": "packet_route|centroid_velocity|configured|perturbation|none",
    "direction_vector": []
  },
  "null_displacement_envelope": {
    "mean": 0.0,
    "max": 0.0,
    "std": 0.0
  }
}
```

The displacement gate must exceed the null/jitter envelope:

```text
displacement_min = max(configured_min, null_mean + k * null_std)
```

or else the report must state that the displacement threshold is uncalibrated
and block strong movement claims.

Identity tracking for packet-driven lanes must distinguish identity failure
from packet-induced mass oscillation inside one parent basin:

```json
{
  "identity_tracking": {
    "mass_oscillation_amplitude": 0.0,
    "parent_basin_preserved": true,
    "support_change_due_to_packet_transfer": false
  }
}
```

Reports that import the E3 pulse must include:

```json
{
  "loop_dependency": {
    "source_experiment": "N03",
    "source_result": "E3_native_LGRC9V3_D2_3_equivalent_packet_loop",
    "loop_ladder_level": "L5",
    "movement_claim_inherited": false
  }
}
```

## Controls

Required controls for fixed-substrate movement:

```text
uniform field
symmetric basin bump
asymmetric bump with reversed tilt
one-time kick with reversed sign
budget projection audit
identity tracking null
topology-disabled audit
```

First-tranche drive types:

```text
none:
    no active drive is applied after initialization

none_after_initialization:
    a structured initial asymmetry is present, then the lane evolves with no
    active drive, kick, pulse, or repeated forcing

one_time_zero_sum_kick:
    a single conserved front/rear perturbation is applied at initialization
    and no repeated drive is applied afterward
```

Required controls for loop-driven movement:

```text
E3 pulse active with boundary coupling disabled
E3 pulse disabled
same pulse with symmetric boundary coupling
reversed pulse direction
shuffled front/rear boundary masks
loop phase scrambled or non-self-rearming control
native GRC9V3 proposal-flux control if feasible
```

Required controls for adaptive topology, if opened later:

```text
fixed_substrate_movement_passed = true
topology enabled vs disabled comparison
growth/pruning/spark event audit
identity parent/child tracking
no promotion from topology-only displacement
```

## Iterations 13-19. Movement Taxonomy And Topology Search

Iterations 13-19 start after Iteration 12 closes the initial
fixed-substrate/M0-M6 tranche. Their purpose is to inventory and separate the
movement classes N04 has already exposed, then test whether the strongest
candidates transfer across geometries.

The taxonomy continuation reuses the M0-M6 ladder as the primary evidence
ladder. It does not create M7 or promote adaptive topology by default.
Geometry transfer is tracked with orthogonal tags:

```text
movement_level = M0|M1|M2|M3|M4|M5|M6
geometry_scope = same_fixture | transferred_geometry | topology_mutating
substrate_class = chain | corridor | ring | grid | port_graph
identity_kind = coherence_basin | deformation_token | boundary_signal | null
identity_surface = fixed_substrate | boundary_fixture | deformation_surface | native_causal_pulse_substrate_surface
implementation_surface = experiment_local | mapped_e3_fixture | native_lgrc_telemetry | native_causal_pulse_substrate_surface
d_level = D0|D1|D2|D3|D4|D5|null
m_level_projection = M0|M1|M2|M3|M4|M5|M6|null
projection_blocker = ...
claim_ceiling = ...
```

This keeps the ladder stable while making evidence breadth explicit. For
example, current M6 is:

```text
movement_level = M6
geometry_scope = same_fixture
substrate_class = chain
identity_kind = coherence_basin
identity_surface = native_causal_pulse_substrate_surface
claim_ceiling = native_m6_same_fixture_self_renewal_candidate
```

The geometry transfer order should minimize false positives from ambiguous
coordinate conventions:

```text
Iteration 13: inventory existing evidence.
Iteration 14: define taxonomy tags and transfer criteria.
Iteration 15: replay/stress S0 chain over longer windows.
Iteration 15-B: test S0 perturbation recovery for T6/R6.
Iteration 16: transfer to S4 corridor or widened chain.
Iteration 17: test S1 ring only after explicit unwrap/front-rear policy.
Iteration 18: test S3 grid with route-defined front/rear.
Iteration 18-B: test an actual two-axis turn on S3 grid.
Iteration 18-C: test state-gated two-input/two-output S3 routing.
Iteration 18-D: test geometry-scored competing output-basin selection.
Iteration 18-E: test composed 1D LGRC fork competition without external scoring.
Iteration 18-F: test balanced local preference tie-breaking without global bias.
Iteration 18-G: integrate the fixed-topology 2D composed gate.
Iteration 18-H: close out the S3 grid series without a new probe.
Iteration 19: freeze the S3-to-S7 fixed-port mapping contract.
Iteration 19-A: execute the S7 fixed-port composed gate.
Iteration 19-B: test topology-lineage/adaptive cases last.
```

Ring evidence should not be used to promote M5/M6 until unwrap, front/rear,
centroid, and direction conventions are frozen before the run. Adaptive
topology remains blocked until a topology-specific suite proves lineage,
identity, budget, and no topology-only displacement promotion.

The taxonomy continuation acceptance requires:

- every evidence item points to a source artifact;
- D-level deformation evidence is inventoried as first-class rows, not only as
  M-level projections;
- every transfer probe declares geometry tags before execution;
- M0-M6 gates remain unchanged unless a later explicit ladder-revision
  decision is made;
- adaptive topology stays blocked until topology controls pass;
- any proposed M6 subtype split is evidence-driven and recorded as a review
  item, not assumed at Iteration 13;
- all declared geometry and perturbation probes are complete or explicitly
  deferred with a rationale;
- the tag schema is validated on S0 plus at least two of S1, S3, or S4 before
  any broad geometry-transfer claim is considered;
- a closeout report records the strongest ceiling per geometry and the
  decision on whether adaptive topology should be opened.

## Iteration Plan

### Iteration 0. Planning And Handoff Record

Create the N04 implementation plan/checklist and record the N03/E3 handoff
boundary.

Acceptance:

- plan and checklist exist;
- implementation README links them;
- N03/E3 is recorded as pulse substrate evidence only;
- no movement claim is inherited.

### Iteration 1. Hypothesis And Baseline Inventory

Create a concise hypothesis document and inventory usable runtime surfaces,
configs, and N03/E3 artifacts.

Acceptance:

- hypothesis states null, movement-response, and loop-driven movement claims;
- baseline commands are recorded;
- `src/*` change policy is recorded;
- E3 artifact paths and claim flags are listed.

### Iteration 2. Fixture Manifest And Metric Defaults

Define first fixtures and metric thresholds.

Initial fixture targets:

```text
S0_chain_v1
S1_ring_v1
optional S3_grid_v1 as later extension
```

Acceptance:

- fixture manifests are replayable;
- node coordinates and basin masks are explicit;
- metric defaults include budget, displacement, identity, shape, and topology
  thresholds;
- fixtures can represent U0/B0/B1/K1 lanes.

### Iteration 3. Initializers And Projection

Implement experiment-local initializers:

```text
uniform field
symmetric canonical bump
locally tapered asymmetric bump
zero-sum kick
conserved nonnegative projection
```

Acceptance:

- initialization formulas are serialized;
- budget and nonnegativity are verified after projection;
- asymmetric tilt is local, not a global background gradient;
- reversed controls are generated deterministically.

### Iteration 4. Movement Observables

Implement movement observables:

```text
centroid
support/boundary assignment
boundary flips
front/rear masks
mass and width
profile similarity
front/rear curvature or Hessian proxy where available
movement cost
budget audit
topology audit
```

Acceptance:

- observables are tested on synthetic positive and negative traces;
- centroid drift is separated from boundary movement;
- shape preservation is separated from spreading/smearing;
- reports include enough time-series evidence to replay classifications.

### Iteration 5. Fixed-Substrate Nulls And One-Time Response

Run U0, B0, B1, K1, and reversed controls on S0/S1.

Acceptance:

- U0 and B0 reject directed movement;
- B1/K1 may show movement response only if gates pass;
- reversed lanes reverse displacement or are reported as substrate-biased;
- no loop-driven or locomotion-like claim is emitted.

### Iteration 6. M0-M3 Classifier Freeze

Freeze early movement classifier behavior.

Acceptance:

- M0/M1/M2/M3 classification is deterministic;
- blocked reasons are explicit;
- budget/identity/topology failures block movement promotion;
- report schema v1 is stable enough for later loop-driven runs.

### Iteration 7. E3 Pulse Import Adapter

Import E3 pulse evidence as a drive source without claiming movement.

Acceptance:

- E3 pulse metadata is loaded or reproduced through native LGRC9V3;
- pulse lane is recorded as P4/P5 candidate depending on mode;
- movement reports state `movement_claim_inherited = false`;
- disabled/scrambled/reversed pulse controls are available;
- reversed direction validates structural route reversal, not only count
  symmetry;
- route-aspect, pole-region, and channel-sequence digest scopes are recorded;
- import mutation audit is explicitly read-only/no-op by construction.

### Iteration 7-B. Packet-Loop Geometry Coupling Audit

Before any boundary movement claim, audit whether the imported E3 packet loop
changes movement-relevant state surfaces.

Measure:

```text
pole mass oscillation
node C changes near route vs off-route
edge delay/proper-time asymmetry
conductance/coupling changes if available
boundary metric changes with boundary coupling disabled
```

Acceptance:

- E3 pulse-active / boundary-coupling-disabled control does not claim movement;
- reports state whether pulse activity changes movement-relevant geometry;
- no boundary displacement is directly scripted by the coupling adapter;
- claim ceiling is `packet_loop_geometry_coupling_audit`.

### Iteration 8. Boundary-Coupled Pulse Fixture

Create a fixture where pulse timing can couple asymmetrically to front/rear
boundary masks.

Before defining boundary coupling, Iteration 8 must define the mapping from the
N03/E3 four-pole route fixture onto the active N04 movement substrate. E3's
native positive fixture is a 4-node route-aspect loop; N04's active fixtures are
the 21-node chain and 24-node ring. A movement fixture must therefore declare
how route poles/channels map to movement nodes, regions, or boundary masks
before a boundary-coupled pulse claim can be tested.

First active mapping:

```text
mapping_id: e3_four_pole_to_s0_chain_boundary_v1
target_fixture_id: S0_chain_v1
S1 -> source/core region [10]
K2 -> front-inner region [11, 12]
S2 -> front-boundary region [13, 14]
K1 -> rear-boundary region [6, 7]
front_boundary_mask = [13, 14]
rear_boundary_mask = [6, 7]
center_reservoir_mask = [9, 10, 11]
```

This mapping is region-based, not node-id preserving. It is a state-mediated
coherence coupling from E3 pulse telemetry to N04 movement nodes. It must not
write support masks, centroids, displacement, or topology directly. `S1_ring_v1`
mapping remains deferred until a separate ring unwrap/front-rear policy is
defined.

Acceptance:

- symmetric coupling null is negative for net movement;
- asymmetric coupling is measurable;
- front advance and rear retraction are reported separately;
- boundary coupling score is serialized;
- claim ceiling is `boundary_coupled_pulse_fixture_validation`;
- centroid displacement is recomputed from serialized node coherence rather
  than written directly;
- forward/reverse coupling symmetry is recorded;
- Iteration 8 reversal is coupling-direction reversal only; a true
  reversed-E3-pulse telemetry lane is deferred to Iteration 9;
- the frozen Iteration 5 displacement threshold is read and reported, but not
  used to promote Iteration 8 claims;
- per-lane timeseries are emitted as JSONL artifacts with digest verification;
- K2/S2 route regions are mapped for completeness, while
  `coupling_signal_v1` uses S1/K1 only;
- `coupling_strength = 0.5` is documented as a first fixture-validation value,
  with sensitivity analysis deferred;
- movement, boundary-coupled movement, loop-driven movement, and
  locomotion-like claims remain blocked until Iteration 9 classifier gates run.

### Iteration 9. Loop-Driven Movement Classifier M4-M5

Classify whether pulse-driven runs satisfy organized/repeated movement gates.

Acceptance:

- M4 requires coordinated front/rear boundary change;
- M5 requires repeated displacement over a finite window;
- E3 pulse must remain budget-conserving;
- controls remain negative for the correct gate reasons;
- candidate M5 evidence is separated from full movement-claim allowance;
- M5 response counts use distinct pulse-locked response windows, not repeated
  plateau samples;
- if native true reversed-E3-pulse telemetry is unavailable, the classifier must
  preserve the candidate signal but block full loop-driven movement claims.

### Lane B. True Reversed-E3-Pulse Direction Parity

Lane B resolves the specific Iteration 9 direction-parity blocker before any
broader pulse-substrate mechanism work is opened.

Result:

```text
status = passed
claim_ceiling = m5_direction_parity_supported_boundary_response
true_reversed_e3_telemetry_available = true
lock_audit_status = passed
movement_claim_allowed = false
loop_driven_movement_claim_allowed = false
```

Lock record:

```text
status = locked
locked_on = 2026-05-16
lock_artifact = outputs/n04_lane_b_lock_audit.json
lock_report = reports/n04_lane_b_lock_audit.md
m6_opened = false
```

The native counter-clockwise E3 telemetry was generated through the existing
N03/E3 LGRC9V3 runtime path, verified as native D2.3-equivalent packet-loop
telemetry, and run through the existing S0 boundary-coupled fixture under the
frozen Iteration 9 M4/M5 policy. It produced opposite-signed displacement with
matched magnitude, matched boundary coupling score, and matched pulse-locked
window count relative to the forward E3 lane.

Interpretation:

```text
Lane B clears the direction-parity blocker for repeated loop-driven boundary
response on the fixed S0 boundary fixture. It does not by itself open M6,
locomotion-like, adaptive-topology, biological, agency, or unrestricted
movement claims.
```

The Lane B lock audit verifies:

- the reversed E3 telemetry is native LGRC9V3 telemetry, not synthetic reversal;
- the forward and reversed lanes use the same S0 fixture, mapping, masks,
  coupling strength, thresholds, and frozen M4/M5 classifier policy;
- boundary masks, displacement sign convention, and support extraction do not
  change;
- matched response metrics are recomputed from serialized time series;
- pulse-disabled, symmetric-null, and scrambled-order controls remain negative;
- claim flags preserve the bounded boundary-response ceiling.

### Lane A2. Post-Iteration-10 Retrospective Review

Lane A2 updates the retrospective evidence ladder after Lane B and Iteration
10. It preserves the A1 fixed-substrate result, records Lane B's promotion to
`m5_direction_parity_supported_boundary_response`, and records Iteration 10 as
`m6_not_opened_feedback_path_absent`.

Result:

```text
status = passed
claim_ceiling = m5_direction_parity_supported_boundary_response__m6_blocked
movement_claim_allowed = false
m6_opened = false
```

Interpretation:

```text
The strongest current N04 result is direction-parity-supported repeated
boundary response on the fixed S0 boundary fixture. M6 remains blocked because
there is no feedback path from S0 boundary response back to native E3
pulse-generating conditions.
```

### Lane A3. Iteration 10 Failure Review

Lane A3 reviews the Iteration 10 failure directly. It distinguishes the gates
that passed before the failure from the M6 gates that failed.

Result:

```text
status = passed
failure = no_feedback_path_from_boundary_response_to_pulse_generation
not_failed_due_to = budget | identity | shape/economy | direction_parity
needed_to_reopen_m6 = movement_substrate_state_feeds_back_into_pulse_generation
```

Interpretation:

```text
Iteration 10 failed for the right reason. The current fixture can read out a
direction-parity-supported repeated boundary response, but it cannot regenerate
the pulse-producing condition that would make the response self-renewing.
```

### Lane C. Feedback-Coupled Pulse Regeneration

Lane C is the targeted mechanism lane for reopening the Iteration 10 M6 gate.
It does not reinterpret the failed Iteration 10 result. It defines the missing
causal feedback path:

```text
S0 boundary response -> runtime-visible pulse eligibility/polarity state ->
feedback-triggered next pulse
```

Scope:

- define a serialized feedback contract from movement-substrate state to pulse
  eligibility;
- measure whether post-boundary-response state restores pulse-generating
  conditions;
- verify feedback-triggered pulse regeneration after the boundary response has
  committed;
- re-run the M6 gate only from feedback-regeneration artifacts;
- keep movement, locomotion-like, adaptive-topology, biological, agency, and
  inherited-N03 claims blocked unless a later closeout explicitly opens them.

Claim ceilings:

```text
C1 feedback_contract_defined
C2 pulse_condition_restoration_candidate
C3 feedback_triggered_pulse_regeneration
C4 m6_feedback_coupled_self_renewal_candidate
```

Result:

```text
status = passed
claim_ceiling = m6_feedback_coupled_self_renewal_candidate
m6_feedback_candidate_gate_passed = true
feedback_adapter_scope = experiment_local
native_feedback_producer = false
movement_claim_allowed = false
loop_driven_movement_claim_allowed = false
locomotion_like_claim_allowed = false
adaptive_topology_entry_allowed = false
```

Interpretation:

```text
Lane C supplies an experiment-local feedback-coupled self-renewal candidate on
top of the locked Lane B fixture. Serialized S0 boundary polarity can restore
pulse eligibility, authorize regenerated pulses, and sustain repeated feedback
cycles under controls. This is not yet native LGRC9V3 M6 because the feedback
adapter is not a native producer.
```

Native LGRC decision:

```text
Lane C is compatible with the Lane E causal pulse-substrate surface
candidate core extension = native_causal_pulse_substrate_surface
candidate specialization = policy_gated_feedback_producer
```

Lane C identifies the smallest primitive that unlocks feedback-coupled
regeneration. The Lane E compatibility probe shows that this primitive can be
represented as a policy-gated producer specialization over the broader native
causal pulse-substrate surface, instead of a separate Lane-C-only core addon.
Any native extension should remain default-off, policy-gated, producer-only for
scheduling, `step()`-only for mutation, and fully visible in
ledger/telemetry/snapshot artifacts.

Lane C / Lane E compatibility:

```text
command = .venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_hybrid_lgrc_lane_c_feedback_surface_compatibility.py
status = passed
claim_ceiling = lane_c_feedback_policy_compatible_with_causal_pulse_substrate_surface
shared_surface = native_causal_pulse_substrate_surface
lane_c_projection = feedback_policy_specialization
lane_c_feedback_surface = boundary_polarity_score
lane_c_specific_core_primitive_needed = false
native_specialization_if_promoted = policy_gated_feedback_producer
native_lgrc_pulse_substrate_supported = false
native_feedback_producer_supported = false
movement_claim_allowed = false
```

Acceptance:

- feedback reads runtime-visible movement-substrate state, not hidden fixture
  internals;
- feedback does not directly write support, centroid, displacement, topology,
  or claim flags;
- post-response state changes pulse eligibility or polarity in the expected
  direction;
- regenerated pulse is not copied from the original E3 schedule;
- repeated-cycle persistence is self-renewed, not inherited from the original
  pulse schedule;
- controls block pulse-disabled, feedback-disabled, subthreshold, wrong
  polarity, scrambled timing/order, and budget-violating cases.

### Iteration 10. Self-Renewing Movement Candidate M6

Only open from the locked Lane B baseline with an explicit self-renewal gate.
Lane B supports direction-parity-controlled repeated boundary response, but it
does not by itself show that movement restores the conditions required for
another pulse.

Result:

```text
status = passed_fail_closed
claim_ceiling = m6_not_opened_feedback_path_absent
m6_opened = false
primary_blocker = no_feedback_path_from_boundary_response_to_pulse_generation
```

Interpretation:

```text
The repeated S0 boundary responses remain driven by the native E3 pulse
schedule. The boundary fixture does not feed movement-substrate state back into
native E3 surplus-trigger or pulse-producing conditions, so it does not support
self-renewing movement. M6 and locomotion-like claims remain blocked.
```

Acceptance:

- repeated movement is not externally rescheduled: not satisfied;
- polarity regeneration is measured: measured as absent/unavailable;
- identity continuity reaches required threshold: satisfied for the boundary
  fixture;
- shape/economy gates remain bounded: satisfied for the boundary fixture;
- claim remains locomotion-like basin dynamics, not biology or agency: not
  opened; all locomotion-like, biology, and agency claims remain blocked.

### Lane D. Pulse-Substrate Coupling Mechanism

Lane D is the broader mechanistic probe formerly tracked as Lane C. It asks
whether a pulse can travel through a substrate and carry a local deformation.
It is useful, but it is not the direct Iteration 10 unlock path. Lane C already
supplies an experiment-local feedback candidate; Lane D asks whether a more
natural substrate-level mechanism can produce that kind of feedback.

Native LGRC promotion is deferred to Lane E until Lane D closes. Lane D remains
experiment-local through D5, and `src/*` should not change during Lane D.

Lane D should be run as a mini-series, not as five single steps:

```text
D1.x pulse transport
D2.x local geometry coupling
D3.x traveling deformation
D4.x direction/null controls
D5.x D-to-M reclassification and native-extension decision input
```

This structure keeps the exploration method explicit: first prove local pulse
transport, then prove local geometry response, then prove traveling deformation,
then controls, then movement-ladder reclassification.

D1 result:

```text
status = passed
claim_ceiling = pulse_transport_only
peak_sequence = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
peak_source = argmax_post_transfer_pulse_field
max_hop_distance = 1
nonlocal_jump_detected = false
max_budget_error = 0.0
wrong_direction_control_negative = true
```

Interpretation:

```text
Local pulse transport is established on the S0 chain with exact pulse-budget
conservation and no nonlocal jumps. The peak is computed from the transferred
pulse field, not from an itinerary. No geometry coupling or movement claim is
opened by D1.
```

D2 result:

```text
status = passed
claim_ceiling = pulse_local_geometry_coupling
primary_surface = local_support_mass
coupling_count = 11
max_support_delta = 0.10000000000000009
max_locality_distance = 1
max_off_contact_delta = 0.0
geometry_budget_abs_error_max = 0.0
```

Interpretation:

```text
Local geometry/support response is established at pulse contact. The response
is local, budget-conserving, nonnegative, and writes only the declared geometry
state. It does not yet establish traveling deformation or movement.
```

D3 result:

```text
status = passed
claim_ceiling = traveling_deformation_candidate
geometry_response_policy = causal_one_step_lagged_local_support_coupling
pulse_peak_sequence = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
deformation_peak_sequence = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
phase_lag_nodes = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
causal_time_lag_steps = 1
causal_lag_matches = true
deformation_displacement = 10
reversed_deformation_displacement = -4
width_profile_preserved = true
instantaneous_reference_phase_lag_nodes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

Interpretation:

```text
Traveling deformation is established as an experiment-local D-lane candidate.
The primary deformation lane now uses a one-step causal lag: deformation at
step t is linked to pulse contact at step t-1. The instantaneous D2 response is
kept only as a reference lane. Reversed pulse direction reverses deformation
direction on the same substrate and coupling rule, while static pulse and
disabled controls block traveling deformation for distinct reasons. D3 still
does not open movement, loop-driven movement, M6, or native LGRC
pulse-substrate claims; D5 must reclassify the deformation evidence through the
movement ladder.
```

Claim boundary:

```text
traveling deformation is not movement until frozen movement gates classify it;
native M6 remains blocked unless feedback-coupled regeneration is promoted to a
native runtime producer.
```

D4 result:

```text
status = passed
claim_ceiling = direction_controlled_traveling_deformation_supported
disabled_controls_negative = true
direction_controls_passed = true
scrambled_order_negative = true
scrambled_preserves_mass_event_window = true
symmetric_null_negative = true
budget_blocker_negative = true
nonnegative_blocker_negative = true
```

Interpretation:

```text
D4 hardens the D3 mechanism with a control matrix. Disabled pulse, disabled
geometry coupling, and static pulse fail for distinct reasons. Reversed pulse
and the wrong-direction fixture validate direction control. Scrambled timing
preserves mass profile, event count, pulse budget, and observation window while
destroying canonical order. Symmetric coupling remains balanced. Budget and
nonnegative synthetic blockers fail only through their intended hard gates.
This supports direction-controlled traveling deformation as mechanism evidence;
movement and native LGRC claims still require D5 reclassification and Lane E
promotion decisions.
```

D5 result:

```text
status = passed
claim_ceiling = substrate_carried_deformation_movement_candidate
d_level_label = D5_direction_controlled_traveling_deformation_supported
movement_level_projection = M3_shape_preserving_identity_displacement_candidate_on_deformation_surface
m5_style_deformation_candidate = true
strict_movement_claim_allowed = false
primary_full_claim_blocker = deformation_surface_is_not_runtime_coherence_basin
```

Interpretation:

```text
D5 finds a movement-style candidate on the deformation surface. The
direction-controlled traveling deformation projects through the frozen
movement-style gates as a shape-preserving, repeated, direction-controlled
surface candidate. The result remains blocked as a full movement claim because
the moved identity is a causal geometry-deformation token rather than a runtime
coherence basin. The reusable primitive suggested by Lane C plus Lane D is
broader than a one-off feedback adapter: Lane E should evaluate a hybrid
causal pulse-substrate surface contract that can cover pulse transport, local
geometry coupling, feedback regeneration, artifact replay, and
budget/nonnegative gates before native promotion is considered.
```

### Lane E. Hybrid LGRC Pulse-Substrate Surface Probe

Status: Complete.

Lane E should use LGRC9V3 as it exists today. It should not change core LGRC
yet. The purpose is to run a hybrid proof-of-contract:

```text
existing native LGRC9V3 pulse telemetry
+ experiment-local native_causal_pulse_substrate_surface driver
+ D5 classifier/replay stack
```

This lane tests whether the broader surface contract really unifies Lane C
feedback regeneration and Lane D pulse-substrate deformation before the project
commits to a core implementation. The driver may model the proposed
`native_causal_pulse_substrate_surface`, but its status remains
experiment-local until Lane F.

Candidate primitive under test:

```text
native_causal_pulse_substrate_surface
```

Entry criteria:

- Lane D D5 closeout exists;
- the hybrid surface contract is explicit and serialized;
- existing LGRC9V3 pulse telemetry is read as input, not modified;
- the experiment-local surface driver is separate from core LGRC;
- default-off policy gating is defined;
- producer/step boundary is preserved;
- ledger, telemetry, and snapshot requirements are known.

Acceptance:

- existing LGRC9V3 artifacts remain native and unchanged;
- the hybrid driver can reproduce Lane C-style feedback regeneration and
  Lane D-style pulse-substrate deformation through one surface contract;
- artifact-only replay can validate the hybrid surface evidence;
- claim flags distinguish `hybrid_lgrc_surface_probe = true` from
  `native_lgrc_pulse_substrate_supported = false`;
- no `src/*` changes are made in Lane E.

Lane E is organized as six completed checks:

```text
E1 Hybrid Surface Contract Definition
E2 Native LGRC Input Import
E3 Lane D-Style Deformation Reproduction
E4 Lane C-Style Feedback Eligibility
E5 D5 Classifier/Replay Stack And Claim Boundary
E6 Theory Alignment Audit
```

The theory alignment audit checks:

| Constraint | Lane E status |
|---|---|
| Producer/step boundary | Preserved by direct-write policy and experiment-local surface driver. |
| Native budget surface | `node_plus_packet`, with native final budget error `0.0`. |
| Surface budget separation | Experiment-local surface uses `node_only`; budgets are not merged. |
| Causal availability | Native event at `t` drives surface response at `t+1`. |
| Implementation specialization | Contract status remains `experiment_local_driver`; no `src/*` changes. |
| Claim discipline | Native support, movement, locomotion-like, adaptive-topology, biology, agency, and inherited-N03 claims remain blocked. |
| RC identity boundary | Deformation token is not a runtime coherence basin. |

Result:

```text
command = .venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_hybrid_lgrc_pulse_substrate_surface_probe.py
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

Lane C compatibility result:

```text
status = passed
claim_ceiling = lane_c_feedback_policy_compatible_with_causal_pulse_substrate_surface
same_surface_can_host_lane_c_feedback_policy = true
lane_c_specific_core_primitive_needed = false
native_specialization_if_promoted = policy_gated_feedback_producer
native_feedback_producer_supported = false
```

Interpretation:

```text
Lane E validates the hybrid surface contract only. Existing native LGRC9V3 E3
pulse-contact artifacts can drive an experiment-local causal pulse-substrate
surface that reproduces Lane D-style deformation and represents Lane C-style
feedback eligibility. A focused Lane C compatibility probe also validates that
Lane C feedback regeneration can be represented as a policy-gated producer
specialization over the same surface. This is evidence that the broader native
surface is worth theory and implementation planning, not evidence that LGRC
already has native pulse-substrate semantics.
```

### Lane F. Native LGRC Pulse-Substrate Semantics

Lane F is the native LGRC implementation bridge after Lane E and the theory
updates. Its surface-support bridge is complete as of Phase 8 Iteration 56.
It opened only after:

```text
Lane E hybrid proof passes (complete)
LGRC paper extension records the causal pulse-substrate surface (complete:
papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md)
Phase 8 implementation plan/checklist is updated for the native surface
(complete:
implementation/Phase-8-LGRC9-CausalPulseSubstratePlan.md
implementation/Phase-8-LGRC9-CausalPulseSubstrateChecklist.md)
```

Possible native implementation choices:

```text
native_causal_pulse_substrate_surface
native_pulse_substrate_coupling_producer
native_feedback_coupled_pulse_producer
```

The preferred hypothesis was that the broader
`native_causal_pulse_substrate_surface` should come first, with coupling and
feedback producers as policy-gated specializations. Phase 8 Iteration 56 now
supports that hypothesis at the native surface level:

```text
artifact = outputs/native_lgrc_lane_f_surface_bridge.json
native_lgrc_pulse_substrate_supported = true
movement_claim_allowed = false
native_m6 = false
```

Lane F is also closed at the N04 level:

```text
closeout = outputs/n04_lane_f_native_surface_closeout.json
lane_f_status = native_surface_support_complete
claim_ceiling = native_lgrc_pulse_substrate_surface_supported
validated_chain = source_packet_event -> surface_row -> producer_record ->
                  scheduled_packet -> processed_packet_event
```

This is not a movement or M6 promotion. It means the native surface/producers
are available as artifact-validatable LGRC scheduling evidence for future N04
validators. Movement, loop-driven movement, native M6, locomotion-like,
adaptive-topology, agency, biology, identity-acceptance, and inherited-N03
movement claims remain blocked.

The corresponding Phase 8 native continuation is closed in:

```text
implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.md
```

### Lane G/H. Native M6 Evidence And Same-Fixture Validator

Lane G first reviewed whether Lane C and Lane F artifacts were already enough
to open native M6. The answer was fail-closed: the native feedback producer
blocker was cleared, but no same-fixture native M6 validator had replayed Lane
C's self-renewal gate on S0 using native producer artifacts.

Lane H then ran that validator:

```text
artifact = outputs/native_m6_same_fixture_validator.json
audit = outputs/native_m6_validation_checklist_audit.json
status = passed
claim_ceiling = native_m6_same_fixture_self_renewal_candidate
native_m6_candidate_gate_passed = true
native_m6 = true
movement_claim_allowed = false
```

Interpretation:

```text
Lane H supports a bounded native M6 same-fixture self-renewal candidate. After
one seeded packet contact on S0_chain_v1, native feedback eligibility rows
authorize regenerated packet work through the native feedback producer for
both forward and reversed boundary polarity. This opens native M6 candidate
evidence, but not locomotion-like behavior, adaptive topology, biology,
agency, identity-acceptance, inherited-N03 movement, or unrestricted movement.
```

### Iteration 11. Visualization And Replay

Add static and animated visualizations for representative lanes.

Acceptance:

- visualizations are generated from reports/artifacts;
- positive and negative controls are visually distinguishable;
- visualization cannot promote a claim not present in the report.
- same seed rerun produces the same classification;
- artifact replay produces the same classification.

### Iteration 11-B. M2 Runtime Shape-Blocked Fixture

Replace the classifier-only M2 visual rung with a replayable S0 runtime-style
timeseries. The lane must pass displacement, budget, identity, topology, and
directed boundary reassignment, then fail shape/profile so the frozen M0-M3
classifier stops at M2 rather than promoting to M3.

Acceptance:

- emitted timeseries and report classify as
  `M2_identity_preserving_displacement`;
- primary blocked reason is `shape_gate_failed`;
- M3 and movement-like claims remain blocked;
- the M-taxonomy visual reference pack uses the runtime M2 timeseries.

### Iteration 12. Tranche Closeout And Taxonomy-Handoff Decision

Close the initial fixed-substrate/M0-M6 tranche and hand off to Iterations 13-19 for
movement-taxonomy/topology search. This is a boundary marker, not a final N04
stop.

Acceptance:

- closeout records the strongest current ceiling as
  `native_m6_same_fixture_self_renewal_candidate`;
- M0-M6 source-of-truth artifacts are preserved, including the Iteration 11-B
  M2 runtime fixture and visual reference pack;
- Iterations 13-19 are opened as the next taxonomy/topology search sequence;
- adaptive topology remains blocked until Iterations 13-19 earn it under explicit
  topology controls;
- locomotion-like, biological, agency, identity-acceptance, inherited-N03, and
  unrestricted movement claims remain blocked;
- output cleanup is considered only after replay needs are satisfied;
- any core implementation need is recorded as a separate task.

### Iteration 13. Taxonomy Inventory

Build the first taxonomy inventory from existing reports only. This iteration
does not run new probes and does not promote claims.

Acceptance:

- every M0-M6 rung has source artifact pointers;
- Lane C/D/E supporting classes are included as non-M-axis evidence;
- later 15-C/15-D/15-E resilience results may be added as source-backed M6
  extension rows without promoting broad geometry-transfer or locomotion-like
  claims;
- Lane D deformation evidence has first-class rows with `d_level`,
  `m_level_projection`, and `projection_blocker`;
- every row records movement level, geometry scope, substrate class,
  identity kind, identity surface, implementation surface, claim ceiling, and
  blocked claims.

### Iteration 14. Class Separation And Tag Freeze

Freeze the taxonomy tag schema and separate classes that can otherwise be
overread as movement.

Acceptance:

- centroid displacement is separated from identity-preserving movement;
- boundary response is separated from basin movement;
- traveling deformation is separated from runtime coherence-basin movement;
- same-fixture self-renewal is separated from locomotion-like movement;
- M6 resilience extensions are separated from broad geometry-transfer,
  locomotion-like, and adaptive-topology claims;
- fixed topology is separated from topology-mutating evidence;
- current M1 and M3 rows are recorded as classifier/observable-fixture evidence
  rather than empirical native runtime movement lanes;
- the M4 `mapped_e3_fixture` to M5 `native_lgrc_telemetry` implementation
  surface transition is documented;
- orthogonal README taxonomy tags (`R`, `B`, `G`, `Q`, `F`, `H`, `E`, `T`) are
  either frozen as per-row fields or explicitly deferred with rationale;
- D-to-M projection rules are frozen:
  - D0 maps to M0 only;
  - D1 is local response only without M-level promotion;
  - D2 may project to M4 candidate only if boundary coordination passes;
  - D3 provides direction-parity evidence for an M5 candidate;
  - D4 is a shape/profile analog, not direct M3 promotion;
  - D5 may support M5-style control evidence but remains blocked from
    coherence-basin movement when `identity_kind = deformation_token`.

### Iteration 15. S0 Chain Replay And Longer-Window Stress

Replay the strongest chain candidates before transferring geometry.

Acceptance:

- current M5/M6 chain candidates rerun with unchanged gates and policies;
- longer-window/cost scaling is measured with
  `cost_metric = total_redistribution_load_per_cycle`, using the Q3 movement
  cost/economy convention from the N04 README;
- boundedness criterion is declared before the run: cost per cycle may not
  grow superlinearly with cycle count;
- failure conditions are declared before the run: cost per cycle doubling
  between cycle 3 and cycle 5, or budget error accumulating beyond
  `epsilon_budget`, must downgrade the geometry-transfer entry ceiling;
- seeded-first-contact and feedback-renewed cycles remain distinct;
- perturbation/recovery remains blocked and deferred to Iteration 15-B;
- broader movement and adaptive-topology claims remain blocked;
- go/no-go before Iteration 15-B: if M6 does not sustain at least five
  feedback-renewed cycles with bounded cost, either stop and reopen the S0
  mechanism question or run perturbation recovery with the degraded ceiling
  stated.

### Iteration 15-B. S0 Perturbation Recovery Probe

Test whether the same-fixture S0 M6 candidate recovers after an explicit
perturbation before transferring geometry.

Acceptance:

- perturbation policy is declared before the run, including timing, affected
  nodes/surface rows, mass amount, and whether it targets polarity, support, or
  feedback eligibility;
- perturbation is budget-neutral, topology-fixed, and does not directly write
  support masks, centroid, displacement, topology, or claim flags;
- pre-perturbation baseline has at least five feedback-renewed cycles from
  Iteration 15;
- post-perturbation recovery window is finite and declared before the run;
- verify whether front/rear polarity resets or re-establishes (`R6`);
- verify whether the displacement/self-renewal cycle recovers (`T6`);
- if recovery fails, record `T6 = tested_negative` or equivalent and keep
  geometry-transfer entry ceiling at the Iteration 15 stress ceiling;
- if recovery passes, record `T6_candidate` / `R6_candidate` without promoting
  locomotion-like, adaptive-topology, biological, agency, identity-acceptance,
  inherited-N03, or unrestricted movement claims;
- go/no-go before Iteration 15-C: if recovery fails, map the S0 perturbation
  tolerance envelope before geometry transfer; if recovery passes, still record
  the recoverable perturbation range before using it as a transfer challenge.

### Iteration 15-C. S0 Perturbation Tolerance Envelope

Map where the current same-fixture S0 recovery stability actually lives.

Acceptance:

- perturbation sweep values are declared before the run;
- every sweep point uses the same native S0 surface, feedback policy, recovery
  window, budget, topology, and claim gates as Iteration 15-B;
- each perturbation point records whether recovery passes, partially recovers,
  or fails closed, with a primary blocker such as `subthreshold`,
  `wrong_polarity`, or `source_budget_exhausted`;
- record the largest perturbation that recovers within the declared window and
  the smallest perturbation that fails;
- verify all perturbations are budget-neutral and topology-fixed;
- no support, centroid, displacement, topology, producer-claim, or claim-flag
  writes are introduced;
- claim ceiling remains `s0_same_fixture_perturbation_tolerance_profile`; no
  T6/R6 claim is promoted from a single threshold point;
- go/no-go before Iteration 15-D: use the first failing S0 perturbation as the
  resilience challenge unless the whole sweep recovers, in which case use the
  largest tested perturbation and record that the failure threshold remains
  open.

### Iteration 15-D. Shock-Resistant Recovery Geometry Probe

Design and test a recovery-capable geometry variant before the formal geometry
transfer sequence. This is a resilience-design probe, not a broad geometry
transfer claim.

Rationale from Iteration 15-C: the current S0 mechanism does not fail T6
primarily because perturbations are too large. It fails the declared
three-cycle recovery window even at the zero-perturbation reservoir control
because the source reservoir can fund only two recovery cycles after the
five-cycle baseline. R6 polarity recovery remains available for small
perturbations, so the feedback signal and causal ordering are not the main
bottleneck. Iteration 15-D therefore targets recovery capacity:

```text
Can a geometry/reservoir design fix source-budget exhaustion without
directly scripting support, centroid, displacement, topology, or claims?
```

Acceptance:

- candidate recovery geometry is declared before the run, including reservoir,
  corridor, or buffer structure and why it could address the Iteration 15-B/C
  failure mode;
- the challenge perturbation is inherited from Iteration 15-C, preferably the
  smallest perturbation that broke S0;
- the native causal pulse-substrate surface and feedback producer are reused
  where possible; any policy differences are declared before execution;
- recovery must occur through native packet event -> surface row -> feedback
  eligibility -> scheduled packet work -> `step()` mutation, not direct
  support/centroid/displacement/topology writes;
- compare against the S0 result at the same perturbation amount;
- record whether the geometry improves recovery cycle count, avoids
  source-budget exhaustion, restores polarity, and restores the
  displacement/self-renewal cycle;
- if successful, record a scoped resilience result such as
  `shock_resistant_same_family_geometry_recovery_candidate`;
- do not promote locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, unrestricted movement, or broad geometry
  transfer claims;
- go/no-go before Iteration 16: formal geometry transfer proceeds with the
  strongest explicit S0/resilience ceiling, and the Iteration 16 fixture must
  state whether it is testing ordinary transfer or resilience-informed
  geometry.

### Iteration 15-E. Large-Shock Absorber Geometry Probe

Design a same-family geometry specifically to absorb larger front/rear polarity
shocks before the formal geometry-transfer sequence.

Rationale from Iteration 15-D: adding source-reservoir capacity fixes the first
positive S0 T6-failing perturbation and avoids source-budget exhaustion at the
stronger `0.15` stress point, but the `0.15` stress still fails the T6
centroid-restoration criterion. The remaining design question is therefore not
only source capacity:

```text
Can a geometry absorb a large boundary-polarity shock while preserving native
feedback recovery and centroid restoration?
```

Acceptance:

- candidate absorber geometry is declared before the run, including source
  reservoir, boundary absorber/buffer nodes, compensating budget debits, and
  why the design targets the `0.15` failure mode;
- challenge perturbation is the `0.15` stress point from Iterations 15-B and
  15-D;
- native causal pulse-substrate surface and feedback producer semantics remain
  unchanged;
- absorber initialization is budget-neutral, topology-fixed during runtime, and does not
  directly write support masks, centroid, displacement, topology, producer
  claims, or claim flags;
- fixture-defined recovery-channel edges are recorded separately from runtime
  topology mutation;
- centroid deltas declare their coordinate/sign frame, including
  direction-normalized signed deltas for reversed lanes;
- recovery cost records the inherited Iteration 15 native feedback packet cost
  metric rather than introducing a new cost schedule;
- recovery must occur through native packet event -> surface row -> feedback
  eligibility -> scheduled packet work -> `step()` mutation;
- compare against both plain S0 and the 15-D source-reservoir geometry at
  perturbation `0.15`;
- pass criteria require avoiding source-budget exhaustion, restoring R6
  polarity, and satisfying the T6 centroid-restoration criterion at `0.15`;
- if successful, record only a scoped result such as
  `large_shock_absorber_same_family_recovery_candidate`;
- if unsuccessful, record the new blocker and carry the 15-D scoped ceiling
  into Iteration 16;
- keep locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, unrestricted movement, and broad geometry
  transfer claims blocked;
- go/no-go before Iteration 16: formal geometry transfer should state whether
  it uses source-reservoir-only resilience from 15-D or absorber-informed
  resilience from 15-E.

### Iteration 16. S4 Corridor Or Widened-Chain Geometry Transfer

Transfer the chain result to the lowest-risk non-identical geometry.

Acceptance:

- corridor/widened-chain fixture declares frozen front/rear direction;
- pulse-substrate and feedback policies are transferred or differences are
  declared;
- direction parity, budget, nonnegativity, identity, shape, and self-renewal
  gates are checked under `geometry_scope = transferred_geometry`;
- go/no-go before Iteration 17: if corridor transfer does not reach at least
  M4, ring transfer must be scoped to the corridor-achieved ceiling rather than
  assumed to test M5/M6.

### Iteration 16-B. S4 Corridor Perturbation Probe

Map the perturbation envelope of the S4 corridor transfer before moving to the
ring.

Acceptance:

- reuse the Iteration 16 corridor fixture and native feedback policy;
- sweep declared budget-neutral front/rear polarity perturbations;
- record the strongest M4/M5/M6-style recovery boundary on the corridor;
- expose the T-axis persistence result directly in the report;
- keep full T6, ring/grid/port-graph transfer, broad geometry-transfer,
  locomotion-like, adaptive-topology, biological, agency, identity-acceptance,
  inherited-N03, and unrestricted movement claims blocked.

### Iteration 16-C. High-Shock Corridor Resilience Probe

Determine whether the S4 corridor high-shock boundary is geometry-limited or
feedback-capacity-limited before entering ring transfer.

Acceptance:

- use the Iteration 16-B `0.175` T6-candidate failure boundary as the first
  challenge;
- keep fixture/runtime distinction explicit: geometry-only changes must not be
  confused with changed feedback capacity;
- test declared recovery-capacity variants without promoting them to the
  default corridor policy;
- record the minimum recovery capacity needed to recover higher shocks;
- keep full T6, ring/grid/port-graph transfer, broad geometry-transfer,
  locomotion-like, adaptive-topology, biological, agency, identity-acceptance,
  inherited-N03, and unrestricted movement claims blocked.

### Iteration 17. S1 Ring With Explicit Unwrap Policy

Test ring transfer only after the coordinate conventions are frozen.

Acceptance:

- unwrap, front/rear, centroid, and direction policies are fixed before run;
- antipodal/tie-breaking artifacts cannot promote M5/M6;
- ring claims remain scoped to the declared unwrap convention;
- go/no-go before Iteration 18: grid transfer is optional and should open as an
  M5/M6 transfer only if corridor transfer reached M5+; otherwise it should
  inherit the weaker corridor/ring ceiling.

### Iteration 17-A. Ring Unwrap-Robustness Probe

Test whether the Iteration 17 ring result depends on one particular unwrap
origin or remains stable across equivalent declared unwrap policies.

Acceptance:

- multiple unwrap origins are declared before execution;
- each accepted unwrap keeps the active route away from the seam;
- front/rear masks, positive direction, centroid policy, and tie policy are
  frozen per unwrap before scoring;
- forward/reversed M4/M5/M6 candidate gates are recomputed from native surface
  artifacts for every unwrap, not copied from Iteration 17;
- equivalent unwraps produce matched achieved levels, direction parity, and
  recovery status within declared tolerance;
- any unwrap whose seam intersects the active route is excluded from
  robustness promotion and recorded as a seam-sensitive control;
- claim ceiling may improve only to `s1_ring_unwrap_robust_transfer_candidate`;
- circular locomotion, wrap-crossing movement, broad geometry-transfer,
  adaptive-topology, biology, agency, identity-acceptance, inherited-N03, and
  unrestricted movement claims remain blocked.

### Iteration 17-B. Circular Ring Motion Evidence Probe

Test whether the ring supports a stronger circular-motion evidence class under
a circular metric instead of a single linear unwrap. This is not merged into
17-A because 17-A tests coordinate-policy invariance, while 17-B tests
wrap-safe circular transport/response.

Acceptance:

- circular phase/centroid metric is declared before execution;
- seam-crossing and wrap-crossing routes are tested with circular distances,
  not linear unwrap shortcuts;
- circular front/rear or phase-leading/trailing policy is declared before
  scoring;
- static, wrong-direction, seam-artifact, and unwrap-only controls fail for
  distinct reasons;
- native surface and feedback producer semantics remain unchanged;
- no direct centroid, support, topology, displacement, or claim writes occur;
- artifact-only validators reconstruct packet event -> surface row -> producer
  record -> scheduled packet -> processed packet chains;
- claim ceiling may improve only to
  `s1_ring_circular_motion_evidence_candidate`;
- locomotion-like, adaptive-topology, biological, agency,
  identity-acceptance, inherited-N03, and unrestricted movement claims remain
  blocked unless a later explicit closeout opens them.

### Iteration 17-C. Ring Geometry Closeout

Summarize the ring series without running a new probe.

Acceptance:

- consume Iteration 17, 17-A, and 17-B artifacts as source inputs;
- record the combined ring-series ceiling;
- preserve the distinction between single-unwrap transfer, unwrap robustness,
  and circular wrap-route evidence;
- verify all ring-series rows remain M6/T6-candidate scoped evidence;
- keep broad geometry-transfer, locomotion-like, adaptive-topology, biology,
  agency, identity-acceptance, inherited-N03, and unrestricted movement claims
  blocked;
- route Iteration 18 to test whether the ring-series ceiling transfers to S3
  grid route-defined front/rear geometry.

### Iteration 18. S3 Grid Route-Defined Front/Rear

Test transfer to a 2D route-defined substrate.

Reasoning:

Iteration 18 is intentionally a first grid-survival probe, not a full 2D
movement claim. It asks whether the existing M6/T6 candidate survives embedding
in a 2D substrate while remaining constrained to a declared one-axis route. It
therefore tests lateral leakage, diagonal-shortcut leakage, and route-defined
front/rear transfer, but it does not yet test true two-axis pulse behavior,
junction choice, or state-gated routing.

Acceptance:

- route-based direction and front/rear masks are declared before run;
- boundary response and self-renewal gates are checked on the grid;
- diagonal/route shortcuts do not directly script displacement.

### Iteration 18-B. S3 Grid Two-Axis Turn Route

Test whether the grid candidate can turn across axes rather than only survive
as a one-axis route embedded in 2D.

Reasoning:

A one-dimensional pulsar loop can be embedded in a grid without becoming a 2D
movement mechanism. The next stricter probe is a declared L-shaped route whose
active movement changes axis, for example west input through the center to a
north output, with a reversed/parity lane using the opposite turn. This keeps
the route declared before execution while proving that the candidate is no
longer only ring-like or chain-like behavior drawn on a grid.

Acceptance:

- declare the L-shaped turn route, ingress/egress gates, and turn node before
  the run;
- verify the active displacement has nonzero components on both grid axes
  across the route episode;
- verify turn output is feedback-authorized from committed surface evidence,
  not copied from a preauthored schedule;
- run reversed/paired turn parity with matched route policy and thresholds;
- keep diagonal shortcuts, post-hoc masks, direct displacement writes,
  locomotion-like, adaptive-topology, port-graph, and unrestricted movement
  claims blocked.

### Iteration 18-C. S3 Grid State-Gated Two-Input/Two-Output Routing

Test whether a fixed-topology grid junction can choose among declared 2D gates
from pulse-contact history.

Reasoning:

If 18-B proves a declared two-axis turn, 18-C asks the more mechanistic design
question: can the same junction expose two input gates and two output gates,
then select the output gate from serialized local surface state and feedback
eligibility? This is the first grid probe aimed at 2D pulsation rather than a
single route.

The current 18-C scope is a design prototype over native LGRC primitives. The
packet work, surface rows, feedback eligibility rows, producer scheduling, and
artifact validation are native LGRC. The gate-selection decision itself is an
experiment-level serialized policy in this tranche. Therefore 18-C can justify
a design direction for state-gated 2D routing, but it cannot yet claim a native
LGRC two-input/two-output gate-selection producer.

The intended native direction is geometry-driven: gate selection should emerge
from declared junction geometry and committed pulse-substrate surface evidence,
not from an external decision function. A later native implementation should
replace experiment-level gate selection with a default-off, policy-gated LGRC
producer or equivalent geometry-surface mechanism that reads committed rows,
emits evidence, and schedules packet work only through LGRC.

Acceptance:

- declare two input gates, two output gates, and a serialized gate-selection
  policy before the run;
- verify different committed pulse/contact histories select different output
  gates under the same fixed grid topology;
- verify disabled gate policy, wrong-polarity, scrambled-order, and diagonal
  shortcut controls fail with distinct blockers;
- verify regenerated pulse work is feedback-authorized and not copied from an
  original schedule;
- record whether gate selection is native geometry-driven or experiment-level
  design-prototype logic;
- keep topology mutation, adaptive-topology, locomotion-like, biological,
  agency, identity-acceptance, inherited-N03, and unrestricted movement claims
  blocked.

### Iteration 18-D. S3 Grid Geometry-Scored Competing Basin Selection

Test whether output-gate selection can be moved closer to geometry itself:
competing output basins are declared, the input pulse carries a flux-shape
signature, and the selected output is the basin with the strongest
geometry/flux compatibility score.

Reasoning:

Iteration 18-C still uses experiment-level policy to map ingress history to an
output gate. 18-D is a stricter design prototype for the theory's
selection/collapse intuition: two candidate basins compete, and the flux should
resolve into one selected route because the input flux shape fits one output
basin better than the other. This is a selection/collapse analogue only. It is
not RC identity collapse, semantic choice, agency, or a native LGRC
gate-selection producer until that mechanism exists in runtime.

Acceptance:

- declare competing output basins, their geometry descriptors, and the
  compatibility scoring rule before the run;
- derive output choice from serialized input flux-shape evidence and declared
  basin geometry, not from direct input-to-output lookup;
- verify two distinct input flux shapes resolve to different output basins;
- verify tie/ambiguous flux, disabled competition, wrong-output, and diagonal
  shortcut controls fail with distinct blockers;
- verify selected output pulse work is scheduled through native LGRC feedback
  machinery and is not copied from an original schedule;
- record that the current implementation is a geometry-scored design prototype,
  not native geometry-driven LGRC selection/collapse;
- record the stricter blocker: 18-D uses external experiment scoring logic,
  not just a native LGRC scheduling policy. Earlier native policy extensions
  ordered or scheduled already-declared packet work from committed evidence;
  18-D evaluates competing futures and suppresses the non-selected basin;
- keep RC identity-collapse, agency, adaptive-topology, port-graph,
  locomotion-like, biological, inherited-N03, and unrestricted movement claims
  blocked.

### Iteration 18-E. S3 Grid Composed 1D Fork Competition

Test whether the selection problem can be reframed as LGRC composition rather
than external scoring: build a fork from two native one-dimensional LGRC route
elements sharing an input/source, then measure whether branch eligibility,
budget, and feedback dynamics select a branch without experiment-level argmax
or compatibility scoring.

Reasoning:

Iteration 18-D is a useful example of the desired geometry/flux relation, but
it is not the native mechanism. Its scorer is external logic that evaluates
candidate output futures. A closer LGRC-native probe should compose simple 1D
elements into a 2D gate structure and let declared runtime dynamics determine
which branch remains eligible, self-renews, or exhausts. If both branches remain
equally eligible, that is an important negative result: current LGRC composition
does not yet provide branch arbitration/choice.

Acceptance:

- declare two 1D LGRC branch elements and their shared fork source before the
  run;
- use the same native causal pulse-substrate surface and feedback producer
  semantics on both branches;
- prohibit external geometry compatibility scoring, direct argmax selection,
  direct branch suppression, and preauthored input-to-output lookup;
- define selection observables as branch dominance, branch survival,
  feedback-renewed cycle count, budget exhaustion, or failed arbitration;
- run symmetric-tie, single-branch-disabled, swapped-flux, and budget-limited
  controls with distinct blockers;
- record whether the result is native branch competition, no-arbitration,
  or still requires a new native branch-competition primitive;
- keep RC identity-collapse, semantic choice, agency, adaptive-topology,
  port-graph, locomotion-like, biological, inherited-N03, and unrestricted
  movement claims blocked.

### Iteration 18-F. Balanced Local Preference Fork Tie-Breaking

Test whether the 18-E no-arbitration blocker can be reduced by balanced local
preferences: tiny declared local asymmetries resolve local near-ties, while the
sum of preferences over the fixture remains globally unbiased.

Reasoning:

Iteration 18-E shows that composed 1D branches can compete through native
eligibility, but a symmetric eligible fork remains unresolved. A single global
epsilon would be a hidden selector. A better design is paired local
symmetry-breaking: one local fork weakly prefers one branch, another local fork
weakly prefers the opposite branch, and the global preference sum is zero. The
epsilon may break a near-tie but must not override real branch evidence.

Acceptance:

- declare the balanced local preference policy before the run, including
  epsilon, local preference sites, and global preference sum;
- verify no-preference fork still reproduces the 18-E no-arbitration blocker;
- verify paired local preferences resolve local near-ties in opposite
  directions;
- verify the global branch-preference sum is zero;
- verify a dominant opposing branch overrides local preference;
- verify epsilon does not force a choice when both branches remain strongly
  eligible;
- verify recovery still uses native packet event -> surface row -> feedback
  eligibility -> scheduled packet work -> `step()` mutation;
- keep native LGRC choice selection, RC identity collapse, semantic choice,
  agency, adaptive-topology, port-graph, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked.

### Iteration 18-G. Integrated Fixed-Topology 2D Composed Gate

Integrate the S3 pieces into one fixed-topology 2D composed-gate candidate:
two input gates, two output branches, composed 1D LGRC branch elements, and
balanced local preference tie-breaking.

Reasoning:

Iteration 18-C defined the two-input/two-output gate shape. Iteration 18-D
showed the desired geometry/flux relation but used an external scorer.
Iteration 18-E removed the scorer by composing 1D branches, and Iteration 18-F
added balanced local preferences to reduce local near-tie no-arbitration
without introducing a global selector. Iteration 18-G should test these as one
integrated fixed-topology 2D mechanism.

Acceptance:

- declare two input gates and two output branches before the run;
- compose the gate from native one-dimensional LGRC branch elements;
- use balanced local preferences with zero global branch-preference sum;
- verify west/south inputs select distinct output branches by native branch
  eligibility, not external scoring or argmax;
- verify no-preference still reproduces 18-E no-arbitration;
- verify dominant branch evidence overrides local preference;
- verify epsilon does not force a choice when both branches remain strongly
  eligible;
- verify recovery still uses native packet event -> surface row -> feedback
  eligibility -> scheduled packet work -> `step()` mutation;
- keep native LGRC choice selection, RC identity collapse, semantic choice,
  agency, adaptive-topology, port-graph, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked.

### Iteration 18-H. S3 Grid Series Closeout

Summarize the S3 grid series without running a new probe.

Acceptance:

- consume Iterations 18, 18-B, 18-C, 18-D, 18-E, 18-F, and 18-G artifacts as
  source inputs;
- record the strongest scoped S3 ceiling as
  `s3_grid_integrated_2d_composed_gate_candidate`;
- preserve the progression from route-defined grid survival through
  fixed-topology integrated 2D composed gate;
- explicitly record that 18-D used an external scorer and that 18-E/18-F/18-G
  remove that scorer by composition plus balanced local preferences;
- keep native LGRC choice selection, RC identity collapse, semantic choice,
  agency, port-graph transfer, adaptive topology, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked;
- route Iteration 19 to test whether the S3 fixed-topology 2D composed-gate
  ceiling transfers to S7 port mechanics.

### Iteration 19. S7 Port-Graph Mapping Contract

Freeze the S3 integrated 2D composed-gate to S7 fixed-port mapping before
execution. This is a contract/mapping step, not a behavior probe.

Reasoning:

Iteration 18-H closed the S3 grid series as a fixed-topology 2D composed-gate
candidate. Before executing it as S7, the port roles must be explicit so later
evidence cannot change the meaning of input ports, output ports, branch ports,
local preferences, or topology lineage after seeing the result.

Acceptance:

- consume Iteration 18-H as the source ceiling;
- define `s3_integrated_2d_gate_to_s7_fixed_port_graph_v1` as a role-based
  mapping, not node-id preserving;
- map west/south input roles, north/east output roles, shared fork, branch
  ports, and balance ports;
- freeze balanced local preference representation with zero global preference
  sum;
- record topology mutation, edge rewiring, port creation, and port deletion as
  disabled by default;
- keep behavior execution, port-graph transfer, adaptive topology, topology-
  mutating movement, native choice/collapse, agency, and locomotion-like claims
  blocked;
- route Iteration 19-A to execute the fixed-port graph under this contract.

### Iteration 19-A. S7 Fixed-Port Composed-Gate Execution

Execute the mapped S7 fixed-port graph with topology mutation disabled.

Reasoning:

This tests whether the S3 integrated fixed-topology 2D composed-gate ceiling
transfers to S7 port mechanics without opening adaptive topology. The target is
fixed-port execution evidence only: native packet/surface/feedback machinery
may schedule and process work, but ports and topology must remain fixed.

Acceptance:

- consume Iteration 19 mapping contract;
- execute `west_in -> north_out` and `south_in -> east_out` lanes;
- verify branch selection comes from native branch eligibility, not external
  scoring or argmax;
- verify artifact-only validators pass for the native packet event -> surface
  row -> feedback eligibility -> scheduled packet -> processed packet chain;
- verify budget, nonnegative, identity/shape, and recovery gates pass;
- preserve no-preference, dominant-branch, and strong-two-branch controls from
  the S3 composed-gate series;
- verify topology mutation and port rewiring remain disabled with no emitted
  topology events;
- keep adaptive topology, topology-mutating movement, native LGRC choice
  selection, RC identity collapse, agency, locomotion-like, biological,
  inherited-N03, and unrestricted movement claims blocked;
- route later work to an explicit topology-lineage/adaptive gate only if
  fixed-port execution passes.

### Iteration 19-B. S7 Topology-Lineage / Adaptive Gate

Open topology only as an explicit gate suite, not as a side effect of port
transfer.

Acceptance:

- preserve Iteration 19-A as the topology-disabled fixed-port baseline;
- verify native LGRC-3 topology/lineage replay is available and budget
  conserving;
- test whether causal pulse-substrate surface rows can carry topology lineage
  through the adaptive event;
- fail closed if the pulse-substrate surface remains fixed-topology only;
- topology-disabled and topology-enabled comparisons are run;
- identity parent/child tracking and budget through topology events pass;
- topology-only displacement cannot promote claims;
- adaptive topology remains blocked unless this suite passes;
- any M6 subtype split is evidence-driven and recorded as a review decision;
- regenerate the M-taxonomy visual reference pack with any accepted geometry
  transfer evidence, preserving the visual-reference claim boundary.

### N04 Pause Before Phase 8 Surface-Lineage Work

Close N04 at the Iteration 19-B boundary before opening more adaptive-topology
probes.

Acceptance:

- record the current ceiling as `s7_fixed_port_composed_gate_candidate`;
- record the blocker as
  `causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status`;
- keep adaptive topology, topology-mutating movement, native LGRC choice
  selection, RC identity collapse, agency, locomotion-like, identity-
  acceptance, and unrestricted movement claims blocked;
- route next runtime work to
  `Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md` and
  `Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md`;
- record the return path as N04 Iteration 19-C: rerun the S7 topology-
  lineage/adaptive gate with native pulse-surface lineage transport enabled.

### N04 Return After Phase 8 Surface-Lineage Closeout

Phase 8 now supports native causal pulse-substrate surface lineage transport.
This resolves the runtime blocker exposed by Iteration 19-B, but does not
promote 19-B into adaptive topology.

Resume with Iteration 19-C:

- consume the Phase 8 surface-lineage closeout;
- preserve Iteration 19-A as the fixed-port baseline;
- rerun the S7 topology-lineage/adaptive gate with native pulse-surface
  lineage transport enabled;
- verify transported/superseded surface rows, producer stale-read prevention,
  artifact-only lineage replay, and topology-only claim-promotion controls;
- keep topology-mutating movement, native LGRC choice selection, RC identity
  collapse, agency, locomotion-like behavior, biological behavior, identity
  acceptance, and unrestricted movement blocked unless 19-C validators
  independently pass.

Iteration 19-C result:

- `adaptive_topology_entry_candidate` is supported;
- committed topology events transport or supersede native pulse-substrate
  surface rows;
- producers read transported surface digests rather than stale source digests;
- stale source reads fail with a distinct blocker;
- artifact-only lineage replay passes for the 19-C surface lineage artifacts;
- topology-mutating movement, native LGRC choice selection, RC identity
  collapse, agency, locomotion-like behavior, biological behavior, identity
  acceptance, inherited-N03 movement, and unrestricted movement remain blocked.

Resume with Iteration 19-D:

- consume the 19-C adaptive-topology entry result;
- attempt the stricter `topology_mutating_movement_candidate` promotion;
- require a committed topology event and transported native pulse-substrate
  surface row;
- attempt post-topology packet work through native producer scheduling and
  `step()` processing;
- keep artifact-only lineage replay, stale-read controls, and topology-only
  claim-promotion controls active;
- preserve topology-mutating movement, native LGRC choice selection, RC
  identity collapse, agency, locomotion-like behavior, biological behavior,
  identity acceptance, inherited-N03 movement, and unrestricted movement
  blocked unless post-topology packet work passes under the same native
  ledger/state contract.

Iteration 19-D result:

- attempted promotion: `topology_mutating_movement_candidate`;
- promotion result: `blocked`;
- current ceiling remains `adaptive_topology_entry_candidate`;
- committed topology event and transported surface row are present;
- artifact-only lineage replay still passes;
- post-topology packet work is not scheduled or processed;
- primary blocker:
  `packet_ledger_state_reabsorption_mismatch_after_topology_event`;
- required runtime mechanism: native topology-state reabsorption must
  update/rebase active graph state and packet ledger totals together before
  post-topology packet work can become topology-mutating movement evidence.

### N04 Return After Phase 8 Topology-State Reabsorption Closeout

Phase 8 now supports default-off native topology-state reabsorption:

- closeout:
  `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`;
- committed topology events can rebase active node/edge state and
  packet-ledger accounting together through explicit lineage maps;
- producers can schedule post-topology packet work only from transported
  surface evidence plus a matching topology-state reabsorption record;
- artifact-only replay validates the packet/surface/topology/reabsorption/
  producer/scheduled-packet chain without private runtime state.

Resume with a strict follow-up topology-mutating movement probe, likely
Iteration 19-E:

- consume the Phase 8 topology-state reabsorption closeout;
- rerun the 19-D topology-mutating movement probe with native
  topology-state reabsorption enabled;
- require post-topology packet scheduling and `step()` processing to pass from
  lineage-current, reabsorbed state;
- preserve artifact-only replay, stale-state-read, direct-rewrite,
  budget-discontinuity, and topology-only claim-promotion controls;
- keep topology-mutating movement, native LGRC choice selection, RC identity
  collapse, agency, locomotion-like behavior, biological behavior, identity
  acceptance, inherited-N03 movement, and unrestricted movement blocked unless
  the strict N04 validator passes.

Iteration 19-E result:

- attempted promotion: `topology_mutating_movement_candidate`;
- promotion result: `supported_candidate`;
- current ceiling: `topology_mutating_movement_candidate`;
- committed topology event, transported native surface row, and
  topology-state reabsorption record are present;
- the coupling producer reads the transported surface digest plus matching
  topology-state reabsorption record digest;
- post-topology packet work is scheduled and processed by `step()`;
- node-plus-packet budget remains exact after reabsorption and post-topology
  packet processing;
- artifact-only replay passes;
- native LGRC choice selection, RC identity collapse, agency, locomotion-like
  behavior, biological behavior, identity acceptance, inherited-N03 movement,
  and unrestricted movement remain blocked.

### Iteration 19 Closeout

Iteration 19 is closed as the S7 port-graph and topology-mutating movement
tranche. The current N04 ceiling is:

```text
topology_mutating_movement_candidate
```

This ceiling means native LGRC can now produce a committed topology event,
transport the native pulse-substrate surface row, reabsorb active state and
packet ledger through the same lineage map, schedule post-topology packet work
from the lineage-current reabsorbed chain, process that packet work through
`step()`, and preserve exact node-plus-packet budget with artifact-only replay.

It still does not mean:

```text
native LGRC choice selection
RC identity collapse
semantic choice
agency
locomotion-like behavior
biological behavior
identity acceptance
inherited-N03 movement
unrestricted movement
```

Those remain the next boundaries.

### Iterations 20-23. Next Exploration Topics

Iteration 20 should stress the 19-E result:

- repeated topology-mutating cycles;
- reversed or matched-opposite topology-mutating lane;
- perturbation before or after topology mutation;
- multiple committed topology events in one run;
- artifact-only replay and exact node-plus-packet budget throughout.

Iteration 20 result:

- status: `passed` as a boundary/stress probe;
- current ceiling remains `topology_mutating_movement_candidate`;
- three matched native repeats passed;
- reversed matched topology-mutating lane passed;
- lineage-accounted perturbation lane passed;
- multiple committed topology events in one run passed at the runtime/budget
  level with exact node-plus-packet accounting;
- multi-topology artifact-only replay passes after Phase 8 time-scoped lineage
  replay hardening, which evaluates producer stale-read status at the
  producer's scheduler time rather than from the final topology state.

This strengthens the 19-E candidate for repeatability, reversal, and
lineage-accounted perturbation. Choice, agency, identity-collapse,
locomotion-like, biological, inherited-N03, and unrestricted movement claims
remain blocked.

Iteration 21 should test the native LGRC choice-selection boundary:

- competing eligible topology-mutating routes;
- no experiment-level selection logic;
- distinguish deterministic local preference from native choice;
- preserve no-choice controls where competing branches remain unresolved.

Iteration 21 result:

- status: `passed` as a boundary probe;
- attempted promotion: `native_lgrc_choice_selection_candidate`;
- promotion result: `blocked`;
- primary blocker: `native_lgrc_topology_route_selection_not_exposed`;
- both competing topology-mutating continuations execute and artifact-replay
  when supplied;
- route selection still enters through experiment-supplied topology-event
  arguments, not a native LGRC route arbitrator;
- deterministic local preference remains bias, not native choice.

The current ceiling remains `topology_mutating_movement_candidate`. Choice,
agency, semantic choice, RC identity collapse, locomotion-like, biological,
inherited-N03, and unrestricted movement claims remain blocked.

Iteration 21-B result after Phase 8 native route arbitration:

- status: `passed`;
- attempted promotion: `native_lgrc_route_arbitration_selection_candidate`;
- promotion result:
  `runtime_route_arbitration_supported_choice_claim_blocked`;
- previous primary blocker:
  `native_lgrc_topology_route_selection_not_exposed`;
- primary blocker: none for runtime route arbitration;
- candidate route set emitted from committed runtime-visible evidence;
- native route-arbitration record selected exactly one route;
- selected topology event referenced the route-arbitration record/digest;
- surface lineage, topology-state reabsorption, producer scheduling, and
  `step()` processing consumed the selected event;
- artifact-only route-arbitration replay passed;
- unresolved-tie and hidden-input controls failed closed.

This resolves the old route-selection exposure blocker as runtime route
arbitration. It does not promote semantic choice, agency, RC identity collapse,
identity acceptance, locomotion-like behavior, biological behavior,
inherited-N03 movement, or unrestricted movement.

Iteration 22 result:

- attempted promotion:
  `rc_identity_through_topology_mutation_candidate`;
- promotion result: blocked;
- primary blocker:
  `rc_identity_basin_invariance_not_validated_across_topology_mutation`;
- topology-aware continuity of surface evidence, active state, packet ledger,
  and producer scheduling is supported;
- stable RC coherence-basin identity and attractor-basin invariance through
  topology mutation are not serialized or validated.

The current ceiling remains `topology_mutating_movement_candidate`. RC identity
collapse, identity acceptance, choice, agency, semantic choice,
locomotion-like, biological, inherited-N03, and unrestricted movement claims
remain blocked.

Iteration 22-B result after Phase 8 native route arbitration and N04
Iteration 21-B:

- status: `passed` as a boundary probe;
- attempted promotion:
  `rc_identity_through_native_route_arbitrated_topology_candidate`;
- promotion result: blocked;
- primary blocker:
  `rc_identity_basin_invariance_not_validated_across_topology_mutation`;
- native route arbitration, selected topology event, surface lineage,
  topology-state reabsorption, producer scheduling, and `step()` processing
  replay artifact-only;
- stable RC coherence-basin identity and attractor-basin invariance through
  native route-arbitrated topology are not serialized or validated.

Iteration 23 result:

- status: `passed`;
- closed tranche: `s7_port_graph_and_topology_mutating_movement`;
- current claim ceiling: `topology_mutating_movement_candidate`;
- strongest supported result: M6 projected topology-mutating port-graph
  candidate with `T5_candidate` persistence evidence;
- native route arbitration is recorded as runtime support, not semantic choice
  or agency;
- RC identity through topology, RC identity collapse, identity acceptance,
  locomotion-like behavior, biological behavior, inherited-N03 movement, and
  unrestricted movement remain blocked.

Next branch:

- choose a new tranche after the topology-mutating closeout.

## Stop Conditions

Stop and record instead of continuing if:

- a movement claim depends on a hidden external source/sink term;
- topology changes are needed before fixed-substrate movement passes;
- the E3 pulse is treated as movement evidence by itself;
- the classifier promotes centroid drift while identity/shape gates fail;
- ring centroid movement depends on an undeclared wrap/unwrap convention;
- packet activity is treated as movement without geometry/boundary coupling;
- boundary displacement is directly scripted by a coupling adapter rather than
  caused by packet-loop effects on runtime coherence or geometry;
- experiment-local code needs to change `src/*`;
- controls pass only because thresholds were weakened after seeing results.

## Initial Success Criterion

The first useful N04 result is not necessarily positive movement. It is a
replayable movement-ladder harness that can distinguish:

```text
no movement
centroid drift
boundary reassignment
shape-preserving displacement
loop-driven repeated displacement
```

under exact budget, identity, topology, and control audits.
