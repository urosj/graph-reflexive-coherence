# N29 Agentic Ecology Convergence Bridge Implementation Plan

## Purpose

N29 is the first formal bridge from the full `N05-N28` LGRC/GRC experiment
record into the `reflexive-coherence-agentic-ecology` project.

The center of gravity is:

```text
What does agentic ecology need?
What can N05-N28 actually supply?
What bridge compositions can be built now?
What remains producer / medium / naturalization debt?
What runnable ecology probes become possible?
```

N29 should not become another chronological validation pass over prior
experiments. It should transform prior results into bridge-facing artifacts:

```text
ecology demand model
N05-N28 capability atlas
demand/supply coverage and debt matrix
bridge motif library
prototype atlas
first ecology probe contracts
```

Repository role boundary:

```text
graph-reflexive-coherence:
  proves and maintains LGRC/GRC building blocks
  records minimal producers and missing native mechanisms
  emits bridge artifacts for safe composition

reflexive-coherence-agentic-ecology:
  composes building blocks into ecology-specific dynamics
  explores multi-component interactions
  runs domain probes such as RC-Ant-style scenarios
```

N29 sits between them. It must make combinations concrete enough for handoff,
but it should not pull full ecology construction back into this repository.

Bidirectional handoff rule:

```text
outbound handoff:
  target = reflexive-coherence-agentic-ecology
  includes = probe contracts, bridge exemplars, motif library, debt ledger,
             claim ceilings, blocked relabels

inbound handoff:
  target = N30+ experiments in graph-reflexive-coherence
  includes = missing native mechanisms, naturalization debt, producer surfaces
             to naturalize, medium surfaces to strengthen, primitive robustness
             gaps, and agency-component follow-up targets
```

N29 closeout must include both directions. If it only exports ecology probe
contracts and does not say what N30+ should continue improving, it is
incomplete.

N29 remains a bridge experiment. It must not claim native ant agency, native
colony agency, biological agency, organism/life, sentience, consciousness,
fully native shared-medium coordination, or Phase 8 completion.

## Source Policy

### Experiment Evidence Sources

N29 consumes `N05-N28` as a capability stack.

The source blocks are:

```text
N05-N11:
  historical LGRC agentic-like mechanism evidence

N12:
  native/producers review gate for N05-N11

N13-N18:
  artifact-level AP3-AP8 agency-prerequisite ladder

N19:
  native-readiness review gate for N13-N18

N20-N28:
  becoming-primitive and ecology-relevant primitive arc
```

Consumption rule:

```text
older concrete mechanisms may be referenced directly for structure
current claim status must respect later closeouts/reviews
review gates may restrict or downgrade older evidence
```

The plan should avoid one iteration per historical group unless a later
implementation needs that granularity. N29 should import these as capability
cards.

### Agency Interpretation Sources

N29 consumes:

```text
geometric-reflexive-coherence/essays/2026-06-12-AgencyOfBecoming-InterpretationThroughRC.md
Arc of Becoming method sources
```

Allowed role:

```text
diagnostic vocabulary
method vocabulary
interpretive constraints
claim-boundary context
```

Blocked role:

```text
implementation evidence
native agency evidence
ant ecology evidence
prototype proof
```

### Ecology Target Sources

N29 consumes:

```text
reflexive-coherence-agentic-ecology/README.md
reflexive-coherence-agentic-ecology/papers/2026-06-FromStateToBecoming.md
reflexive-coherence-agentic-ecology/papers/2026-06-RC-AgenticEcology.md
reflexive-coherence-agentic-ecology/papers/2026-06-TheSharedMedium.md
reflexive-coherence-agentic-ecology/papers/2026-06-SharedMediumCoordination-EngineeringSpec.md
```

Allowed role:

```text
target ecology vocabulary
shared-medium engineering vocabulary
RC-Ant component target
producer-residue / medium-debt language
handoff target
```

Blocked role:

```text
runtime implementation evidence
native shared-medium coordination proof
native ant behavior proof
```

## Work Product Schemas

### Ecology Demand Model

Each demand row should include:

```text
demand_id
ecology_component
source_spec_reference
required_dynamics
required_state_surfaces
required_trace_surfaces
required_controls
blocked_relabels
first_probe_relevance
```

Required ecology demand families:

```text
parent basin
shared medium
medium surface
perturbation
trace
pressure
susceptibility
co-response
resonance
parent-basin modulation
message scaffold
medium debt
producer residue
naturalization condition
```

RC-Ant worked-domain demand families:

```text
colony parent basin
mobile boundary expression
nest / home basin
food / resource coupling
route-support trace
foodward affordance surface
homeward affordance surface
cargo-shaped susceptibility
reserve / hunger pressure
alarm / threat pressure
nursery demand
waste isolation
construction tension
crowding / congestion cost
role susceptibility / division of labor
surplus-supported split / reproduction
```

### Capability Atlas

Each N05-N28 capability card should include:

```text
capability_id
source_experiment
source_artifacts
source_claim_ceiling
review_gate_status
native_readiness_status
supplied_geometry_or_dynamic
producer_residue
naturalization_debt
medium_debt
possible_ecology_demands
blocked_ecology_relabels
prototype_potential
```

The capability atlas should answer:

```text
what concrete LGRC/GRC surface exists?
what is artifact-level only?
what is native-ready?
what is producer-mediated?
what cannot be consumed by ecology yet?
```

### Coverage And Debt Matrix

Each coverage row should include:

```text
source_experiment_or_spec
ecology_demand
candidate_capability_sources
bridge_motif
agency_diagnostic_role
coverage_status
coverage_reason
producer_residue
medium_debt
naturalization_debt
native_readiness_status
native_readiness_gap
blocked_relabels
first_probe_implication
claim_ceiling
why_not_stronger
```

Coverage statuses:

```text
source_backed
prototype_candidate
producer_mediated
medium_debt
naturalization_debt
native_ready_surface
control_only
blocked_relabel
missing_runtime_surface
not_applicable
```

Iteration 7 should keep this as a normalized join: one canonical coverage row
per ecology demand, with ranked `candidate_capability_sources` and an optional
sparse `candidate_link_rows` table for nontrivial demand/supply edges. It
should not emit a full demand-by-capability Cartesian matrix. Bridge motif
labels in I7 are hints for Iteration 8 only, not motif rows or motif success.

### Bridge Motif Library

Each motif row should include:

```text
motif_id
motif_family
ecology_demands_connected
capability_sources
ordered_composition
expected_dynamic
runtime_or_reconstruction_status
producer_residue
medium_debt
controls
prototype_candidate
first_probe_relevance
claim_ceiling
why_not_stronger
```

Initial motif families:

```text
trace_pressure_loop
reserve_optionality_formation
boundary_shared_medium_unit
proxy_susceptibility_reentry
transfer_replay_role_relocation
generative_extractive_medium_reshaping
composition
```

I8 motif rows are definitions and reconstruction targets, not motif-success
evidence. A motif may be marked `source_backed_reconstruction` only when its
component coverage rows carry original source artifacts through I7 and do not
depend on unresolved producer, medium, naturalization, or prototype-candidate
debt. Debt-heavy motifs should stay `artifact_only_reconstruction` or
`mapping_only_no_runtime_surface`. None of these statuses opens a prototype row,
runtime ecology proof, native ecology, or native shared-medium coordination
claim.

### Prototype Atlas

N29 should prefer prototypes when source support exists.

Prototype rows are bridge exemplars. They do not exist to add another proof
layer to previous experiments. They exist to show how a supplied capability can
serve an ecology demand in a concrete downstream structure.

Prototype status:

```text
runnable_runtime
source_backed_reconstruction
artifact_only_reconstruction
visual_diagnostic_only
mapping_only_no_runtime_surface
blocked_by_missing_source
blocked_by_claim_boundary
blocked_by_debt
blocked_by_controls
blocked_by_phase_boundary
```

Prototype classes:

```text
trace_aftereffect
reserve_pressure
boundary_mobile_expression
closed_loop_perturbation_response
proxy_collapse
configuration_transfer
generative_extractive_medium_reshaping
composition
```

Prototype rows must include:

```text
prototype_id
prototype_family
admission_source_motif_id
source_rows
source_digests
source_artifacts
ecology_demand_role
supplied_capability
bridge_motif
bridge_exemplar_role
composition_role
agency_diagnostic_role
runtime_or_reconstruction_status
producer_residue
medium_debt
naturalization_gap
controls
control_results
next_probe_contract
source_digest_status
debt_summary
debt_source_refs
claim_ceiling
unsafe_claim_flags
why_admitted
why_not_stronger
```

Every prototype row must answer:

```text
what ecology demand does this serve?
which N05-N28 capability supplies it?
what bridge motif does it instantiate?
what composition, if any, makes it useful?
what debt remains before ecology can use it freely?
what exact next probe should agentic ecology run?
```

If no prototype is possible:

```text
prototype_status = mapping_only_no_runtime_surface
missing_surface_reason = ...
first_probe_requirement = ...
```

I10 is an admission contract, not prototype admission. It may freeze allowed
prototype families, route-specific statuses, source/digest requirements,
controls, debt summaries, and claim ceilings, but it must not claim that a
route is already a prototype or that a motif has succeeded as ecology.

Future prototype rows must include evaluated `control_results`, not just a
list of required controls. A control status of `not_run` blocks the dependent
claim, and `failed_open` invalidates the row. Legacy source artifacts may use
content SHA-256 as canonical when `source_output_digest` is missing; future
generated artifacts require output digests.

Composition is not directly admissible from I10. It may open only in I15 after
at least two non-composition prototype rows are admitted, ordered composition
references admitted prototype IDs, order-inversion / hidden-producer /
medium-debt-hidden controls pass, and the composition does not raise the claim
ceiling.

I11 should start minimally: one primary route, one primary demand cluster, two
to four primary source artifacts, one explicit reconstruction or mapping basis,
all required controls evaluated, one exact next probe contract, and no
composition.

The trace leg must be source-fidelity checked. If the primary I10 route does
not directly include a trace coverage row, I11 must either add a trace coverage
row as a secondary trace-basis audit or explicitly explain why the trace row is
absent. Secondary trace rows may clarify the leg, but they must not become an
extra primary proof source or raise the claim ceiling.

I11 is the first actual bridge prototype after Phase B mapping and I10
admission schema. Its ecology role is to test the smallest bridge structure
needed by later agentic ecology patterns:

```text
trace / aftereffect
+ pressure / reserve condition
+ bounded loop or re-entry response
= bounded trace-pressure-loop bridge exemplar candidate
```

In agentic-ecology terms, this is a lower-level scaffold for later phenomena
such as pheromone-like trails, alarm pressure, hunger pressure, route support,
or nest/food loops. I11 must not claim those higher-level phenomena. It should
show only that something source-backed happened before, left an admissible
trace or aftereffect, a later pressure condition makes that trace relevant,
and a bounded loop/re-entry response can be reconstructed under I10 controls.

Allowed I11 ceiling:

```text
bounded trace-pressure-loop bridge exemplar candidate
```

Blocked I11 readings:

```text
pheromone communication
ant route behavior
hunger or alarm semantics
semantic signal
semantic action
native ecology behavior
agency
native shared-medium coordination
```

Decision after I11 review:

```text
I11 is a valid first artifact-only bridge exemplar, but Phase C should not stop
at library rows when runtime evidence is feasible.
```

This becomes the directional template for the remaining prototype families:

```text
base prototype row:
  source-backed bridge exemplar or mapping row with debt visible

runtime strengthening row:
  minimal runtime instantiation if existing LGRC/GRC surfaces permit it

perturbation/control row:
  remove or invert the key leg and require failure closed

replay/stress row:
  replay, duplicate, perturbation envelope, margin, and claim-boundary checks
```

The strengthening rows do not make N29 an ant-ecology implementation. They
turn a bridge motif from a catalogue entry into a minimal runnable bridge when
the runtime already supports it, while preserving all claim ceilings. If a
prototype family cannot reach runtime evidence, the gap must be recorded as
medium, producer, naturalization, or implementation debt instead of patched by
labels.

Native runtime evidence is preferred, but it is not the only admissible bridge
strengthening mode. If full native LGRC runtime support does not yet exist, a
producer-assisted runtime row is valid when the producer is at the same
discipline level as producers used in N05-N28: declared before use, source
visible, replayable, bounded, non-semantic, and recorded as producer residue or
naturalization debt. Such rows help identify the minimal LGRC extension needed
to make the bridge native later. They cannot upgrade the result to native
ecology, native shared-medium coordination, agency, or ant behavior.

For I11 specifically:

```text
I11   = artifact-only trace/pressure/loop bridge exemplar
I11-A = minimal runtime trace/pressure/loop instantiation
I11-B = perturbation / ablation / order controls
I11-C = replay / stress / margin matrix
```

I11-B should be a runtime null/control packet over I11-A, not an attempt to
raise the claim ceiling. Its job is to validate that the bridge requires the
trace, pressure, route/order structure, idempotent producer surface, and
producer/step ownership recorded by I11-A.

Required I11-B controls:

```text
no_parent_arrival_trace_control
below_threshold_pressure_control
near_threshold_margin_control
wrong_expected_channel_control
route_aspect_digest_mismatch_control
channel_sequence_shuffle_control
same_causal_surface_replay_idempotency_control
direct_queue_injection_control
unprocessed_child_departure_control
producer_disabled_control
semantic_pheromone_hunger_relabel_control
producer_success_as_native_runtime_success_control
```

Expected I11-B acceptance:

```text
accepted_trace_pressure_loop_runtime_controls_fail_closed_producer_assisted_only
failed_open_count = 0
```

### Bidirectional Handoff Ledger

Each final handoff row should include:

```text
handoff_direction
handoff_target
handoff_payload
source_rows
bridge_motifs
prototype_exemplars
unresolved_debt
claim_ceiling
blocked_relabels
next_action
why_not_stronger
```

Allowed directions:

```text
outbound_to_agentic_ecology
inbound_to_n30_plus_core_primitives
```

## Phase Boundary Rules

Iteration 4 freezes Phase A as the Phase A -> Phase B validation boundary.
Capability cards are orientation/index records only. Source-backed coverage,
motif, prototype, and handoff claims must return to original experiment
artifacts, closeouts, reports, runtime records, or visual manifests where the
visual claim is explicit.

The canonical claim flag location is `claim_boundary_audit`; top-level flags
are convenience mirrors only. The blocked claim list must match the
`claim_boundary_audit` keys.

Unknown fields are allowed only when namespaced with `x_`, paired with
`x_unknown_field_review_status`, and unable to raise the claim ceiling or
replace a required field.

Phase B separation:

```text
I5 = ecology demand matrix only
  must not import N05-N28 evidence, match demand to supply, create bridge
  motifs, or open prototype rows.

I6 = capability supply atlas only
  reorganizes I3 capability cards into normalized supply families, preserves
  review gates, source claim ceilings, producer residue, medium debt,
  naturalization debt, blocked relabels, and original source artifact manifests.
  I3 cards are orientation indexes, not full data sources. Later source-backed
  coverage, motif, prototype, runtime, or visual claims must return to original
  source artifacts, closeouts, runtime records, source reports, or visual
  manifests. I6 may identify prototype potential only; it must not create
  coverage/debt matches, bridge motifs, prototype rows, or positive ecology
  evidence.

I7 = demand/supply coverage-debt matching only
  must not create bridge motifs, open prototype rows, or claim native ecology.
```

## Composition Discipline

N29 should test composition as bridge structure, not as native ecology proof.

Important composition families:

```text
N28 generative + N28 generative:
  enrichment cascade candidate

N28 extractive + N28 generative:
  source/sink exchange or depletion/repair candidate

N28 neutral circulation + N22 susceptibility update:
  route field changes and later biases traversal

N24 surplus + N25.2 basin formation:
  surplus-supported child/multi-basin formation candidate

N17 loop + N08 trace:
  loop leaves aftereffect; later pass responds differently

N26 proxy collapse + N28 medium reshaping:
  proxy-guided medium change succeeds or collapses depending on substrate support
```

Every composition row must have controls for:

```text
label-only composition
report-only composition
hidden producer coupling
medium debt hidden as native relation
component order inversion
missing source row
unsafe ecology relabel
```

## Iteration Plan

### Phase A - Demand, Supply, And Bridge Schema

```text
Iteration 1  - Ecology Demand Extraction
Iteration 2  - Agency Diagnostic And Method Constraint Extraction
Iteration 3  - N05-N28 Capability Card Import
Iteration 4  - Bridge Schema And Claim Boundary Freeze
```

### Phase B - Coverage, Debt, And Motifs

```text
Iteration 5  - Ecology Demand Matrix
Iteration 6  - N05-N28 Capability Supply Atlas
Iteration 7  - Demand / Supply Coverage And Debt Matrix
Iteration 8  - Bridge Motif Library
Iteration 9  - Motif Relabel Nulls And Composition Controls
```

Iteration 9 closes Phase B only if motif relabels, debt-as-native readings,
composition order hiding, missing source rows, missing review gates, AP4/AP5
gap hiding, report-only composition, visual-only evidence promotion, early
prototype rows, runnable ecology probe contracts, and native ecology / agency
promotions all fail closed. Passing I9 makes Iteration 10 prototype admission
schema ready; it does not open Phase C prototypes by itself.

I9 nulls must be derived from row-local forbidden promotion edges, not from
generic caution. The required chain is:

```text
source row -> valid bounded claim -> tempting stronger relabel -> expected rejection
```

Each null must name its source motif or global boundary row, source rows, valid
bounded claim, attempted relabel, relabel path, failure if accepted, claim
ceiling after rejection, and a paired near-positive control. Near-positive
controls must pass the bounded bridge reading while the unsafe relabel fails
closed. The null adequacy table must cover every motif family, all required
composition controls, global blocked claims, producer / medium /
naturalization debt clusters, review gates, AP4/AP5/NAT4 gap erasure, and
failed-open count zero.

### Phase C - Prototype Atlas

```text
Iteration 10 - Prototype Admission Schema
Iteration 11 - Prototype A: Trace / Pressure / Loop
Iteration 11-A - Runtime Trace / Pressure / Loop Instantiation
Iteration 11-B - Trace / Pressure / Loop Perturbation Controls
Iteration 11-C - Trace / Pressure / Loop Replay And Stress Matrix
Iteration 11.1 - Stronger Trace / Pressure / Loop Sibling Candidate
Iteration 11.1-A - Stronger Runtime Instantiation
Iteration 11.1-B - Stronger Perturbation Controls
Iteration 11.1-C - Stronger Replay And Stress Matrix
Iteration 12 - Prototype B: Boundary / Shared-Medium Unit
Iteration 13 - Prototype C: Proxy / Susceptibility / Re-Entry
Iteration 14 - Prototype D: Generative / Extractive Medium Reshaping
Iteration 15 - Prototype Composition And Atlas Classification
```

I11 remains the minimal edge trace / pressure / loop prototype and construction
contrast. I11.1 is the primary positive evidence for Prototype A once it passes
I11.1-A/B/C. It exists because I11-C passed but exposed a narrow pressure
boundary: the two-pole fixture supported a minimal runnable bridge, but the
representative prototype library needs a less knife-edge pattern where the same
rules, controls, and claim ceiling hold with larger margins. I11.1 therefore
keeps the same trace / pressure / loop motif and producer-assisted claim
ceiling while using a three-pole route cycle with larger predeclared surplus
margin and more route contexts.

Evidence hierarchy for Prototype A:

```text
primary positive evidence:
  I11.1 / I11.1-A / I11.1-B / I11.1-C

minimal edge / construction contrast:
  I11 / I11-A / I11-B / I11-C
```

Later Prototype A summaries should cite I11.1-C first. I11-C should be used to
explain how the motif was first made runnable, why the stronger sibling was
needed, and where the minimal pressure boundary sits.

Prototype B starts at I12 and has a different center of gravity. It is not
another trace / pressure / loop row. It should orient around a bounded
boundary/shared-medium unit: a distinguishable basin-side state, a shared or
adjacent medium, and a counterpart region whose separability can be audited
without turning merge, leakage, or labels into success. I12 should consume N16
for AP6 boundary discipline, N25/N25.1/N25.2 for child-basin and multi-basin
runtime surfaces, and N24/N28 only where medium-capacity or medium-reshaping
context is needed. It should block body/environment, colony boundary,
pheromone/trail substrate, resource ownership, multi-agent interaction, agency,
and native shared-medium coordination readings.

I12 should run first as an admission/design step. If it fixes a clean unit,
source basis, controls, and runtime availability, I12-A/B/C may then be run as
one tranche.

I12-A/B/C must preserve I12's source-role discipline row-locally:

```text
N16 = boundary discipline / separability source, not native shared-medium evidence
N25.2 = primary scoped multi-basin runtime source, not wholesale ecology success
N25/N25.1 = gap and requirements history, not MB6 runtime evidence
N24/N28 = medium-capacity / medium-reshaping context only
Prototype A context = contrast only, not Prototype B evidence
```

The bridge row must remain a three-part geometry:

```text
basin_side_state
shared_or_adjacent_medium
counterpart_region
```

I12-A must extract one exact source-current runtime row with all three parts.
I12-B must run label-only, visual-only, merge/leakage-as-success,
old-basin-thickening, producer-as-native, N16 artifact relabel, N25.2 MB6 as
ant ecology relabel, native shared-medium coordination relabel, semantic
trail/pheromone relabel, and agent-body relabel controls. I12-C must run
artifact-only, snapshot/load, duplicate replay, medium-coupling, merge-pressure,
and counterpart-separability stress. Do not move to I13 until I12-A/B/C pass or
explicitly demote the Prototype B row.

If I12-A/B/C pass only on one exact reference unit, add I12.1 as an alternative
sibling before I13 when practical. I12.1 should not optimize the reference row
or widen the I12 envelope. It should test repeatability by extracting a distinct
N25.2 route-variant boundary/shared-medium unit, then run the same runtime,
control, and replay/stress sequence:

```text
I12.1 = alternative sibling admission
I12.1-A = exact variant runtime extraction
I12.1-B = controls over that variant
I12.1-C = replay/stress over that variant
```

The intended interpretation is two controlled source-current variants for
Prototype B, not replacement of the primary I12 reference and not a native
shared-medium coordination claim. If I12.1 has a higher basin-side
support/coherence value, record that as a local sibling-state difference only.
Do not describe I12.1 as a higher-margin stress result unless merge/leakage
headroom, replay/stress envelope, or declared thresholds actually improve.

If I12/I12.1 still leave the shared medium looking too passive, add I12.2 as an
active-medium separability probe before I13. I12.2 should not seek higher
merge/leakage headroom, because the declared ceiling remains zero. Instead it
should ask whether the source-current medium is active or stress-bearing while
boundary separability remains intact:

```text
I12.2 = active-medium separability admission
I12.2-A = source-current active-medium runtime extraction
I12.2-B = active-medium controls and claim blockers
I12.2-C = active-medium replay/stress close
```

The correct positive result is active-medium separability, not nonzero leakage
tolerance, native shared-medium coordination, or ecology success.

### Phase D - Probe Contracts And Closeout

```text
Iteration 16 - Minimal Runnable Ecology Probe Contract
Iteration 17 - Stronger / Alternative Ecology Probe Contract
Iteration 18 - Closeout And Agentic Ecology Handoff
```

This iteration count is intentionally smaller than a primitive-proof experiment.
N29 is not trying to prove another primitive. It is trying to construct the
bridge surface that lets the ecology project start from actual LGRC/GRC
capabilities rather than from abstract aspiration.

## Claim Boundary

Allowed maximum claim:

```text
N29 supports a claim-clean bridge and prototype atlas from N05-N28 LGRC/GRC
evidence to first RC-agentic-ecology probe contracts.
```

Blocked claims:

```text
native ant agency
native colony agency
biological agency
organism/life
consciousness
sentience
semantic goals
semantic cooperation
native shared-medium coordination
fully native ecology
Phase 8 completion
unrestricted autonomy
```
