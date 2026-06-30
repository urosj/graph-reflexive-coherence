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

N28-derived circulation and exchange rows need special handling. N28 showed
source-backed generative, extractive, competitive, neutral, processor, and
transition-surface regimes under replay and stress, but it did not prove an
ordered environmental circulation loop. In N29, these rows may define bridge
motifs and future composition targets. They must not be upgraded into closed
capacity cycles unless a later runtime row shows ordered dependency:

```text
leg A changes local capacity distribution
leg B consumes A's changed distribution as source-current input
leg B returns or redirects capacity along the reverse or complementary arc
later A-side state depends on B's changed distribution
```

Likewise, a phase-coupled generator/extractor exchange is a future composition
candidate, not a current Prototype D result. The guard is that the generative
leg must remain generative, the extractive leg must remain extractive, the
phase relation must be source-current, neither leg may be relabeled as the
other, and closed-circulation replay/control checks must pass before any loop
claim is made.

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
Iteration 14-A - Prototype D Runtime Admission Schema
Iteration 14.1 - Generative Enrichment Runtime Prototype
Iteration 14.2 - Extractive Depletion Runtime Prototype
Iteration 14.3 - Processor / Redistribution Runtime Prototype
Iteration 14-B - Controls For I14.1-I14.3
Iteration 14-C - Replay / Stress For I14.1-I14.3
Iteration 14.4 - Neutral Circulation Composition Attempt
Iteration 14.5 - Phase-Coupled Generator / Extractor Composition Attempt
Iteration 14-D - Loop / Composition Controls For I14.4-I14.6-2
Iteration 14-E - Replay / Stress For I14.4-I14.6-2
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

Prototype C starts at I13 and has a third center of gravity. It should not
repeat Prototype A's trace / pressure / loop pattern or Prototype B's
boundary / shared-medium unit. Prototype C asks whether a bridge component can
be built around history-conditioned re-entry:

```text
prior interaction / proxy divergence / susceptibility update
  -> bounded changed geometry or proxy state
  -> later re-entry into the same or transferred configuration
  -> bounded differential response or collapse
```

In agentic ecology terms, this is the low-level scaffold underneath future
language such as "returning to a place", "foodward susceptibility",
"role-capture", "cargo-shaped response", "avoidance", or "choice under prior
experience". I13 must not claim those semantic or biological readings. Its job
is narrower: identify whether N22/N23/N26/N27 already provide source-backed
pieces that can be assembled into a controlled proxy / susceptibility /
re-entry bridge miniature.

Primary source families:

```text
N22 = susceptibility update / durable geometry modification
N23 = live-continuation collapse / selection geometry
N26 = proxy divergence / proxy collapse
N27 = configuration / substrate transfer and re-entry mapping
```

N29 I5-I8 may be used as indexes and coverage maps only. I13 must return to
the original experiment artifacts for full source rows, digests, controls, and
claim ceilings.

The intended I13 bridge row has four distinguishable parts:

```text
proxy_or_perturbation_state
susceptibility_delta_or_modified_geometry
reentry_or_transfer_trace
collapse_or_differential_response_trace
```

I13 should first be an admission / design step. If it finds a clean source
chain, later I13-A/B/C can extract an exact runtime or artifact row, run
controls, and replay/stress it. If the source chain is only mapping-level, I13
must classify the row as mapping-only with debt rather than pretending it is a
runnable ecology prototype.

I13-A/B/C may still be useful after a mapping-only I13 result, but their role
changes. They should not become a hidden positive runtime tranche. Instead:

```text
I13-A = exact row extraction attempt / source-chain localization
I13-B = mapping relabel and cross-experiment stitching controls
I13-C = replay / stress admissibility decision over the admitted record
```

If I13-A does not find one exact source-current row, I13-B and I13-C should
remain control/debt records: they may stabilize the mapping record and preserve
claim boundaries, but they cannot support runtime Prototype C.

If I13-A/B/C close as mapping/debt only, N29 may still try a constructive
composition step. That step should be called I13.1, not I13-D, because it is
not another validation record over the inherited source chain. I13.1 asks
whether N29 can build a new source-current composed prototype from the
source-backed mechanisms:

```text
proxy pressure / perturbation state
  -> route-local susceptibility or geometry update
  -> same-budget re-entry / transfer readback
  -> bounded differential response or collapse
```

I13.1 must be judged as new N29 evidence. It may use N22/N23/N26/N27 as design
constraints and claim ceilings, but it must not claim that prior artifacts
already proved the composed row. A positive I13.1 result can support a bounded
Prototype C runtime candidate. It still cannot support final ecology success,
semantic learning, choice, agency, native AP4/AP5 closure, native support, or
ant-role behavior.

After a positive I13.1 runtime candidate, run the usual follow-up pair:

```text
I13.1-B = controls over the composed runtime candidate
I13.1-C = replay / stress over the composed runtime candidate
```

These are different from I13-B/C. I13-B/C protect the mapping-only source
chain. I13.1-B/C validate the newly composed N29 runtime row. If I13.1-B/C
pass, Prototype C can be carried forward as a control-backed and
replay/stress-backed bounded runtime candidate under its local envelope, but
still not as final ecology success.

If the I13.1-C envelope is narrow, N29 may add I13.2 as an alternative composed
runtime candidate. I13.2 should not replace I13.1 and should not retune I13.1.
It should test repeatability and possible margin headroom in a different
proxy/susceptibility/re-entry geometry. If I13.2 passes, run I13.2-B/C before
classifying it as control-backed or replay/stress-backed.

After I13.1-C and I13.2-C, add a compact I13* synthesis before moving to I14.
The synthesis should classify Prototype C as a two-geometry bounded runtime
pattern, preserve the mapping hygiene records, identify the strongest local
candidate, and keep all semantic, native-support, and ecology-success claims
blocked.

Claim blockers:

```text
semantic goal
semantic choice
preference ownership
intentional return
identity transfer
learning as semantic knowledge
native AP4/AP5 closure
native support
ant role behavior
ecology success
```

The correct positive result is a bounded proxy / susceptibility / re-entry
bridge candidate, not learning, choice, agency, native role selection, or
semantic return.

Prototype D starts at I14 and has a fourth center of gravity. It should not
rerun N28 replay/stress matrices or try to prove an environmental loop. It
should synthesize N28's source-backed medium-reshaping regimes into five
ecology-facing motifs:

```text
generative_enrichment_motif:
  focal basin persists while neighboring or surrounding capacity becomes more
  distinguishable, better supported, or better bounded.

extractive_depletion_motif:
  focal basin persists while neighboring or surrounding capacity is depleted,
  flattened, or made less basin-forming.

processor_redistribution_motif:
  one region is depleted while another is enriched, with the focal persistence
  and role distinction preserved.

neutral_circulation_implication:
  balanced or near-neutral redistribution suggests a possible circulation
  construction when paired with an opposite orientation, but it is not itself a
  closed circulation loop.

phase_coupled_generator_extractor_implication:
  a future construction target where a generative enrichment leg and an
  extractive depletion leg are phase-related as source-current exchange, but
  the current row remains motif/debt only.
```

I14 should return to the original N28 artifacts, reports, visual manifests,
and closeout rows for the source basis. N29 I5-I8 may be used as indexes only.
Each motif row should record the N28 source basis, ecology demand served,
supplied capability, bridge motif, remaining producer / medium /
naturalization debt, downstream ecology probe suggested, and claim ceiling.

The intended positive result is:

```text
N28 supplies replay/stress-backed environmental exchange regimes that can seed
N29 ecology bridge motifs.
```

The blocked results are:

```text
closed environmental circulation loop
resource economy
coordinated exchange cycle
agentic ecology runtime
cooperation
exploitation
altruism
biological agency
```

I14 is a start, not the end of Prototype D. If N29 next seeks runtime
prototypes, the tranche should be staged so the first three source-backed
medium-reshaping motifs are not given the same evidential status as the two
loop-like composition implications.

Provisional Prototype D runtime structure:

```text
I14-A  = Prototype D Runtime Admission Schema
  Freeze shared fixture rules, source-current requirements, producer visibility,
  motif-specific thresholds, controls, replay policy, visualization caveats,
  and claim ceilings for Prototype D runtime rows.

I14.1  = Generative Enrichment Runtime Prototype
  Runtime exemplar for focal persistence plus neighboring capacity gain.

I14.2  = Extractive Depletion Runtime Prototype
  Runtime exemplar for focal persistence plus neighboring capacity loss,
  depletion, or flattening.

I14.3  = Processor / Redistribution Runtime Prototype
  Runtime exemplar for local capacity redistribution where one region is
  depleted while another is enriched.

I14-B  = Controls for I14.1-I14.3
  Label-only, visual-only, report-only, focal-survival-only, resource/economy,
  cooperation/exploitation, producer-hidden-state, N28-relabel, and
  aggregate-only redistribution controls. The N28-relabel control must fail
  only when a row copies N28 by label; it must still allow N28 source-current
  rows to serve as source inputs when the N29 row creates its own artifact,
  manifest, threshold record, lineage audit, and claim boundary.

I14-C  = Replay / Stress for I14.1-I14.3
  Artifact replay, snapshot/load, duplicate replay, order checks where
  applicable, and bounded stress over the three direct runtime motifs. Stress
  should include neighbor-gain ablation for I14.1, degradation / leakage-boundary
  separation for I14.2, and route-lobe opposition removal or aggregate-only
  redistribution for I14.3.

I14.2-1 = Clean Extractive Alternative Source Search
  If I14-C preserves the I14.2 leakage caveat, search the existing
  source-backed N28 extractive rows for a cleaner replacement: supported,
  source-current, extractive, negative-neighbor-capacity evidence with
  merge/leakage below its declared ceiling. This row must not consume
  neutral-gap, transition, rejected, or unclassified rows as extractive
  positives. If no clean replacement is found, record the blocker and do not
  rerun I14-B/C for I14.2-1.

I14.2-1-B = Focused Clean Extractive Controls
  If I14.2-1 finds no replacement, run focused controls over the blocker:
  over-ceiling extractor as clean support, neutral-gap transition substitution,
  threshold retuning, caveat erasure, report-only search as runtime, rerun
  without candidate, source-manifest gaps, and exploitation/resource relabels.
  All must fail closed. This validates the blocker; it does not create support.

I14.2-1-C = Focused Clean Extractive Replay / Stress
  Replay/stress must be explicitly blocked or not applicable when no
  replacement runtime candidate exists. This records that there is no clean
  extractor artifact to replay or stress. I14.5 may still consume original
  I14.2 only with its leakage caveat intact.

I14.2-2 = Extractive Reinforcement Runtime Candidate
  Add a different kind of alternative from I14.2-1. This row should not search
  for clean bounded leakage and should not replace I14.2. Instead, consume a
  supported source-current N28 extractive mechanism-diversity row to reinforce
  I14.2 as an extractive/depletion motif with a different geometry. The
  expected role is mechanism-diversity reinforcement with the leakage caveat
  preserved: useful extractor evidence, not clean leakage support, not
  exploitation, and not ecology success. It requires its own focused controls
  and replay/stress before being used as control-backed Prototype D evidence.

I14.2-2-B = Focused Extractive Reinforcement Controls
  Validate the I14.2-2 reinforcement row against label-only mechanism
  diversity, report-only runtime, N28 relabel, focal-survival-only,
  polarity-ablation, mechanism-attribution-ablation, clean-leakage relabel,
  threshold-retune, replacement-overclaim, and exploitation/resource relabel
  controls. The row may survive controls only as caveated reinforcement.

I14.2-2-C = Focused Extractive Reinforcement Replay / Stress
  Replay and stress the I14.2-2 runtime artifact. Stable replay and bounded
  stress may support a second extractor mechanism for Prototype D, but only
  with the over-ceiling merge/leakage caveat intact. This can strengthen I14.5
  as extractor-side mechanism diversity, not as clean bounded leakage.

I14.2-3 = Leakage-Gated Extractor Construction Attempt
  Try a different path from I14.2-1 and I14.2-2: construct an extractor from
  the primary I14.2 source-current trace under a declared producer policy that
  preserves the extractive capacity deltas while adding an explicit leakage
  gate. This may count only if all neighbor/medium capacity deltas remain
  negative and above degradation floors, focal floors remain preserved,
  merge/leakage falls below the original ceiling with a non-rounding-level
  margin, no neutral-gap rows are consumed, and thresholds are not retuned.
  If successful, classify it as a producer-mediated leakage-gated extractor
  construction candidate pending focused controls and replay/stress, not
  native LGRC evidence or final clean extractor support. Uniform attenuation
  that clears leakage only by rounding-scale headroom does not count.

I14.2-3-B = Focused Leakage-Gated Extractor Controls
  Validate the I14.2-3 leakage-gated row against hidden gate, gate-as-native,
  threshold-retune, uniform-attenuation, neutral-gap backfill, label-only,
  source-caveat erasure, rounding-margin, report-only, and ecology/resource
  relabel controls. The row may survive controls only as explicit
  producer-mediated bridge evidence pending replay/stress.

I14.2-3-C = Focused Leakage-Gated Extractor Replay / Stress
  Replay and stress the I14.2-3 runtime artifact. Stable replay and bounded
  stress may support the leakage-gated extractor as producer-mediated
  clean bounded-leakage bridge evidence. It must not retroactively upgrade the
  original I14.2 source row, must not make the leakage gate native LGRC, and
  must not open ecology, resource, exploitation, cooperation, or agency claims.

I14.4  = Neutral Circulation Composition Attempt
  Opposite-orientation or ordered-dependency construction attempt for the
  neutral circulation implication. This remains a composition attempt until
  ordered source-current dependency and replay/order controls pass.
  The first admissible outcome may be a blocked/partial record if only a
  single source-current circulation direction exists. A label-swapped reverse
  leg must be rejected rather than counted as closed circulation.

I14.4-1 = Neutral Circulation Loop-Closure Bridge Attempt
  If I14.4 finds only a single source-current circulation leg, try a bounded
  N29 bridge construction that derives a reverse leg from the forward post-state.
  This can support only a producer-mediated ordered loop-closure candidate
  pending I14-D/E. It must not be described as native LGRC closed circulation.

I14.4-2 = Native-Only Neutral Circulation Closure Search
  Search existing native/source-current circulation rows for an opposite-
  orientation leg that consumes the I4-F forward post-state. No producer
  fallback is allowed. If no such leg exists, record the native closure blocker
  explicitly and keep I14.4-1 as bridge evidence only.

I14.4-3 = Native Directed Circulation Cycle Search
  Correct the I14.4-2 scope: a loop does not require bounce-back or sign-
  inverted reverse orientation. It may be a directed cycle where each leg
  continues forward, as long as a later leg consumes the changed medium and
  closes dependency back to the starting pattern class. Search for that broader
  native directed cycle without producer fallback.

I14.4-4 = Producer-Mediated Directed Cycle Bridge
  Resolve the I14.4-3 blocker only in the bridge lane. Keep the I14.4-3 native
  result negative, then add a producer-mediated frame-shifted forward leg that
  consumes the source-current I4-F changed medium and returns dependency to the
  starting pattern class. This is not the I14.4-1 reverse-return bridge: every
  local leg remains forward in its own frame. The result may support an
  all-forward directed-cycle bridge candidate pending I14-D/E, but it must not
  upgrade native LGRC directed-cycle support or open resource-economy,
  cooperation, exploitation, ecology-success, or agency claims.

I14.5  = Phase-Coupled Generator / Extractor Composition Attempt
  Generator leg plus extractor leg with source-current phase relation. This
  remains a composition attempt until gain/loss dependency is ordered,
  source-current, and replay/control-backed. If the clean extractor leg comes
  from an explicit N29 producer-mediated bridge, the result can only be a
  producer-mediated phase bridge candidate, not native ecology or resource
  economy.

I14.5-1 = Generator / Extractor Feedback Bridge
  Strengthen I14.5 by adding the missing feedback dependency: the extractor's
  changed medium must condition a later generator state. This tests a
  generator -> extractor -> generator bridge rather than the one-way
  generator -> extractor transition in I14.5. It should preserve role polarity:
  generator remains enrichment, extractor remains depletion, and the feedback
  bridge must not collapse them into generic redistribution or a win/loss
  transfer. If the later generator leg is producer-mediated, classify the row
  as producer-mediated phase-feedback candidate pending I14-D/E, not native
  phase-coupled exchange.

I14.5-2 = Buffered Generator / Extractor Feedback Bridge
  Strengthen I14.5-1 by inserting the processor/redistribution motif between
  extractor and later generator. This should test a different mechanism:
  generator -> extractor -> processor/buffer -> later generator. It must not
  be a direct retune of I14.5-1. A useful result should preserve generator,
  extractor, and processor roles, improve residual headroom using a declared
  buffer policy, and keep the claim ceiling producer-mediated pending I14-D/E.

I14.6 = Multi-Role Phase-Coupled Loop Composition
  Optional next composition tier after I14.5-2. Instead of using only one
  generator and one extractor, compose a more complex system from generators,
  extractors, processors, and circulation motifs to test whether a
  "perpetual" phase-coupled loop can be generated as an ordered dependency
  cycle. I14.6 may use producer-mediated bridge surfaces if native runtime
  surfaces are missing, but it must record lane ceilings explicitly and must
  not use producer-mediated success to upgrade native ecology, resource
  economy, cooperation, exploitation, or agency claims.

I14.6-1 = Multi-Leg Leakage Aggregation Probe
  Address the main I14.6 weakness. I14.6 has per-leg leakage gates, but no
  aggregate shared leakage frame. I14.6-1 should map the phase-feedback and
  directed-cycle leakages into a common producer-mediated bridge frame, reject
  cancellation, overlap credit, hidden sinks/sources, and double-counting
  discounts, and record whether full-sum aggregate leakage stays within a
  declared aggregate ceiling. A supported row may strengthen I14.6 only in the
  producer-mediated bridge lane; it must not support native shared-medium
  leakage aggregation or ecology/resource/agency claims.

I14.6-2 = Wider-Margin Multi-Leg Leakage Aggregation Variant
  Strengthen I14.6-1 if its aggregate margin is too narrow. Preserve the same
  aggregate ceiling and full-sum aggregation policy, reject cancellation,
  overlap credit, hidden sinks/sources, and double-counting discounts, and use
  a declared producer-mediated interface guard to reduce net channel leakage.
  Captured leakage must be recorded as producer/naturalization debt, not hidden
  native success. A supported row can widen the producer-mediated bridge
  margin, but still cannot support native shared-medium leakage aggregation or
  ecology/resource/agency claims.

I14-D  = Loop / Composition Controls for I14.4-I14.6-2
  Order inversion, missing feedback, label-only circulation, hidden producer
  coupling, regime-averaging, merge/leakage-as-cycle, and resource-economy
  relabel controls. If I14.4-1 or I14.4-4 is consumed, controls must preserve
  the distinction between native blocked rows and producer-mediated bridge
  rows.

I14-E  = Replay / Stress for I14.4-I14.6-2
  Replay and stress only if I14.4/I14.4-1/I14.4-4/I14.5/I14.5-1/I14.5-2/
  I14.6/I14.6-1/I14.6-2 produce admissible source-current composition rows
  or explicit producer-mediated bridge rows. Otherwise record blocked
  composition debt.

I14* = Prototype D Synthesis
  Synthesize I14 through I14.2-3-C into a compact carry-forward record. The
  synthesis must distinguish direct source-current motifs from the
  producer-mediated leakage-gated extractor, preserve the original I14.2
  leakage caveat, keep native clean extractor support blocked, and hand
  I14.4/I14.5/I14.5-1/I14.6 a searchable composition Prototype D state without opening
  closed circulation, exchange cycle, resource economy, ecology success,
  cooperation, exploitation, or agency claims.

I14Y = Complete Prototype D Synthesis
  Synthesize the full Prototype D tranche after I14-E. The synthesis must
  explicitly preserve the split between native/source-current motif evidence,
  blocked native composition evidence, and replay/stress-backed
  producer-mediated composition bridge evidence. It should record row roles
  for I14X, I14.4-I14.6-2, I14-D, and I14-E, carry forward naturalization
  targets, keep final atlas classification pending I15, and block native
  ecology, resource economy, cooperation, exploitation, and agency claims.

I15 = Prototype Composition And Atlas Classification
  Classify Prototypes A-D as bridge exemplars and compose selected prototype
  families only where source support permits. I15 may open atlas-level
  composition rows as source-backed probe-contract seeds, but it must not
  claim a composed ecology runtime. Every composition row must reference
  admitted prototype IDs, record order/hidden-coupling/medium-debt/claim-ceiling
  controls, preserve producer and medium debt, and point to the next runnable
  probe implication. Mapping-only rows and missing runtime surfaces remain
  explicit inputs for I16 rather than hidden evidence.
```

The important split is:

```text
I14.1-I14.3 = runtime prototypes of already supported N28 motif classes
I14.4-I14.6 = new composition attempts that may become loop candidates
```

I14.1-I14.3 should be read as candidate creation unless I14-B and I14-C pass.
I14.2 has an explicit caveat: its merge/leakage value is above the N28 ceiling,
so it can only be interpreted as extractive-mechanism exceedance evidence, not
as clean bounded leakage. I14.2-1 is the follow-up admission/search row for a
cleaner source-backed extractor. If it finds no replacement, I14.5 may still
use I14.2 only with the leakage caveat intact. I14.2-1-B/C validates that this
blocker fails closed and that replay/stress is blocked by the absence of a
runtime replacement. I14.2-2 is a different follow-up: it reinforces I14.2 via
an alternative extractive mechanism while preserving the same kind of leakage
caveat. I14.2-2-B/C can make that reinforcement replay/stress-backed, but it
still cannot support clean bounded leakage. I14.2-3 is the leakage-gated
construction attempt and must be kept separate from both: it may create a
cleaner extractor only as producer-mediated candidate pending focused controls
and replay/stress, and only if the leakage margin is not rounding-scale. I14.3
must be evaluated through opposed route-lobe capacity deltas; aggregate
near-neutral capacity alone is not enough.

For now, I14's five motifs are sufficient for Prototype D admission. Loop
composition remains downstream debt until the I14.4-I14.6 path exists and
passes its own controls.

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
