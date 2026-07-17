# N31 Derived Decay And Primitive Semantics Implementation Checklist

## Current Status

```text
branch = experiment-N31
status = iteration_2_passed
positive_evidence_opened = false
decay_semantics_selected = false
native_runtime_change_authorized = false
decay_relation_ladder_rung = DR0
n31_closeout_ladder_rung_assigned = false
n31_closeout_ceiling = N31-C1_source_and_authority_inventory_only
candidate_schema_version = n31_decay_candidate_schema_v2
rcae_return_ready = false
```

## Setup

- [x] Create `experiment-N31` from clean graph `main`.
- [x] Create N31 experiment directory structure.
- [x] Add README, hypotheses, implementation plan, checklist, and return contract.
- [x] Preserve RCAE demand as question/return authority rather than evidence.
- [x] Keep positive evidence, candidate selection, and runtime modification closed.
- [x] Normalize route mass, route organization, and causal mediation before I1.
- [x] Record schema change `n31_pre_i1_mass_organization_mediation_normalization_v2`.
- [x] Record that fixture migration is inapplicable because no positive scientific fixtures exist.
- [x] Commit the initialized N31 package.

## Iteration 1 - Source Inventory And Authority Admission

- [x] Record exact graph revision and clean source state.
- [x] Verify RCAE demand revision `ae11be2008b1902df1749faec531420432056c37`.
- [x] Digest all required RCAE demand records.
- [x] Verify theory revision `e0d25bf69b8bf681eb8d092ba416497030e5d88e`.
- [x] Verify all seven theory/substrate source digests.
- [x] Read theory/substrate sources directly rather than consuming RCAE summaries as evidence.
- [x] Inventory LGRC9V3 state, packet, queue, proper-time, event-time, conductance, and surface APIs.
- [x] Inventory route-support, boundary-flux, organization-observable, and local-readout APIs separately.
- [x] Classify lapse, proper-time relation, edge-delay, queue, and arrival-distribution runtime surfaces.
- [x] Distinguish executable timing behavior from paper-defined or missing timing policy.
- [x] Inventory restoration identity v1/v2 and reset-baseline correction.
- [x] Inventory load-bearing runtime tests.
- [x] Inventory N08 source artifacts and native-memory blocker.
- [x] Inventory N22 source artifacts, producer carrier, and naturalization debt.
- [x] Inventory N30 closeout and source-current participant/medium rows.
- [x] Record N30+ roadmap/handoff as planning boundary only.
- [x] Give every source `may_consume_as` and `must_not_consume_as` fields.
- [x] Record paper/specification-to-runtime capability dispositions.
- [x] Record current missing surfaces without treating absence as negative theory evidence.
- [x] Keep DR and N31-C positive rungs unassigned.
- [x] Keep `positive_evidence_opened = false`.
- [x] Emit source inventory JSON and report.
- [x] Verify deterministic rerun and artifact hashes.

Expected ceiling:

```text
N31-C1_source_and_authority_inventory_only
```

### Iteration 1 Result

```text
status = passed
acceptance_state = accepted_source_and_authority_inventory_only_no_decay_evidence
graph_frozen_I1_base_revision = 7075ecb5e464401df96f16eac171fbefe0e532dc
RCAE_demand_revision = ae11be2008b1902df1749faec531420432056c37
geometric_theory_revision = e0d25bf69b8bf681eb8d092ba416497030e5d88e
source_record_count = 46
runtime_capability_count = 16
all_seven_theory_digests_match = true
src_diff_empty = true
protected_runtime_contract_diff_empty = true
positive_evidence_opened = false
decay_relation_ladder_rung_assigned = false
decay_relation_ladder_ceiling = DR0_no_source_current_decay_evidence
n31_closeout_ladder_rung_assigned = false
n31_closeout_ceiling = N31-C1_source_and_authority_inventory_only
ready_for_iteration_2_schema_freeze = true
targeted_runtime_conformance = 46 passed, 27 subtests passed
output_digest = c8b1d7eb4b8009b418b7e7c240628b1c1a547d12e259156f2e53e63bb3dc9736
artifact_sha256 = 1aff8008e26e29001da019168c8340322fe3172be8b2d8ea60c3de1496f47d79
report_sha256 = 1d8323f044fe554e4d6aaa25ce96e935f3f15d59eb202c3fa1fe32cdda08fbaf
script_sha256 = d324765e5339098c043b5e3cf5cc4a66e293b32fb723f1a5dfab06478a23e049
```

### Iteration 1 Interpretation

I1 establishes authority and executable-surface boundaries only. LGRC9V3
already has source-current coherence, conductance/flux, lapse, proper-time,
event-time, edge-delay, packet queue, arrival, and local-update surfaces. Those
surfaces can support later N31 representations and interventions, but their
existence does not demonstrate a durable-yet-weakening relation.

Per-packet arrival times and exact event histories make temporal and
finite-window projections possible. The runtime does not currently expose a
native arrival-distribution decay state, coincidence/resonance policy, generic
persistent route-organization mediator, or susceptibility-relaxation law.
These absences are implementation/representation findings, not negative
evidence about RC theory. I4 must decide whether a candidate organization is an
exact projection, is blocked by representation, or requires an extension.

The historical boundary is also explicit:

```text
N08 = artifact memory/route-trace precedent; native memory policy blocked
N22 = producer-mediated conductance carrier; native update/relaxation debt
N30 = source-current participant/medium/readout precedent; temporal decay unresolved
```

Restoration identity v1 is available for current scientific state. V2 adds the
reset baseline; explicit legacy rebase yields prospective v2 identity without
recovering historical construction provenance. Later replay rows must choose
the identity matching the operation under test.

Verification used `.venv` and covered restoration v1/v2, reset-baseline
persistence, native packet-loop baseline/route behavior, and LGRC9V3 telemetry
contracts. This is runtime conformance support for the inventory, not N31
scientific evidence.

## Iteration 2 - Semantic, Representation, And Control Schema Freeze

- [x] Freeze primary semantic classes as exactly D0a/D0b/D0c/A/B/C.
- [x] Freeze representation/authority classes separately from semantic classes.
- [x] Freeze candidate dispositions separately from semantic and authority classes.
- [x] Enforce one primary semantic class per candidate row.
- [x] Freeze DR0-DR6 ladder and rung gates.
- [x] Freeze N31-C0 through N31-C6 ladder.
- [x] Freeze D0a representation status enum.
- [x] Freeze exact-projection contract fields.
- [x] Freeze lossy/missing representation blocker.
- [x] Freeze `n31_decay_candidate_schema_v2` and schema change-record identity.
- [x] Freeze D0-R as a D0 subtype and B-R as a Candidate B subtype.
- [x] Freeze route-mass contract, outward-positive sign policy, and continuity residual.
- [x] Require boundary flux to be time-integrated exported coherence over the declared post-formation window.
- [x] Require one boundary measure and exactly-once crossing accounting; block departure/arrival double counting.
- [x] Freeze route-organization contract and observable-authority enum.
- [x] Freeze organization-domain enum across spatial, geometric, functional, temporal, and mixed relations.
- [x] Define organization domain as mediator domain, separate from observed diagnostic domains.
- [x] Require mixed-domain rows to isolate one load-bearing domain or remain unresolved.
- [x] Freeze weakening-trajectory enum including relaxation, drift, recurrence, broadening, and transience.
- [x] Freeze causal-mediation contract and full/partial/unresolved statuses.
- [x] Freeze `organization_mediated_readout_change = true` for intervention-backed full or bounded-partial mediation only.
- [x] Freeze full versus qualified-partial D0-R interpretation ceilings.
- [x] Freeze independent-later-probe and forming-packet-exclusion statuses.
- [x] Freeze temporal-intervention matching and added coincidence/resonance policy fields.
- [x] Freeze cross-field contradiction rules between disposition, authority, mediation, and DR ceilings.
- [x] Freeze D0c-to-D0a and D0b-to-causal-authority semantic transition rules.
- [x] Freeze weakening-mode and D0-subclass enums.
- [x] Freeze independent mass, organization, readout, and mediation fact fields.
- [x] Freeze D0-R/B-R policy-owner facts and bridge-status enum.
- [x] Derive policy ownership from call/event/lineage traces, including scheduling without direct mutation.
- [x] Separate B-R ownership classification from positive B-R decay support.
- [x] Require future validators to reject missing or superseded contract schemas.
- [x] Require deterministic migration or regeneration of any future stale fixtures.
- [x] Freeze candidate row schema and required artifact manifest.
- [x] Freeze active-null comparability and derived-fixture-only schema.
- [x] Require active nulls to state the false-positive scenario and match mediator semantics, not topology alone.
- [x] Freeze internal-time owner/advance-event schema.
- [x] Freeze coherence and non-coherence invariant schemas.
- [x] Freeze candidate-specific topology contract.
- [x] Freeze local causal-readout contract.
- [x] Freeze D0 producer allowance and prohibition.
- [x] Freeze post-formation producer-call policy and call-level audit fields.
- [x] Freeze producer-call audit status as complete-no-mutation, reclassified, or blocking-incomplete.
- [x] Require empty state-mutating producer calls for D0.
- [x] Reclassify export-authoring producer calls mechanically as B-R.
- [x] Block native-autonomy calls whose timing gates the aftereffect or supplies export details.
- [x] Freeze A packet-creation versus in-flight boundary.
- [x] Freeze B destination and conservation boundary.
- [x] Freeze C independent-state/closure boundary.
- [x] Freeze v1 versus v2 restoration use.
- [x] Freeze external state composition requirements.
- [x] Freeze cache recomputation separately from execution reconstruction.
- [x] Freeze control result status enum and demotion precedence.
- [x] Freeze exact protected runtime/contract paths and diff-empty requirements.
- [x] Keep specification, runtime, test, example, and dependency changes in a revision-distinct tranche.
- [x] Record the protected runtime base, I1/I2 governance base, and generated I2 artifact as an explicit revision chain.
- [x] Freeze RCAE return manifest schema.
- [x] Assign no positive DR rung.
- [x] Emit schema/control JSON and report.

### Iteration 2 Result

```text
status = passed
acceptance_state = accepted_semantic_representation_control_schema_frozen_no_positive_evidence
source_I1_output_digest = c8b1d7eb4b8009b418b7e7c240628b1c1a547d12e259156f2e53e63bb3dc9736
schema_authority_source_count = 9
candidate_schema_version = n31_decay_candidate_schema_v2
primary_semantic_class_count = 6
candidate_required_field_count = 72
active_null_required_field_count = 28
route_mass_contract_field_count = 20
route_organization_contract_field_count = 15
causal_mediation_contract_field_count = 18
control_id_count = 70
RCAE_return_required_field_count = 77
src_diff_empty = true
protected_runtime_contract_diff_empty = true
positive_evidence_opened = false
candidate_rows_classified = false
d0a_representation_status_assigned = false
decay_relation_ladder_rung_assigned = false
decay_relation_ladder_ceiling = DR0_no_source_current_decay_evidence
n31_closeout_ladder_rung_assigned = false
n31_closeout_ceiling = N31-C1_source_and_semantic_contract_admitted
ready_for_iteration_3_active_nulls = true
output_digest = a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf
artifact_sha256 = 9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6
report_sha256 = 688ca8736ff713ab823f8311816fe6cd92ab5e2268c1ec757b9f114479961627
script_sha256 = a1751fc202b331e88b9b71f04eedec5a509308876297c962fa56ba2d502cd17b
```

### Iteration 2 Interpretation

I2 freezes the rules under which later N31 rows may be admitted. It does not
decide whether D0a is representable, select a candidate, or provide decay
evidence. The six semantic classes remain independent from representation
authority and outcome disposition; D0-R and B-R remain ownership subtypes.

The central evidential rule is now structural:

```text
route mass change != route organization change != causal mediation
```

Each fact requires its own contract. Lower route mass without signed boundary
closure is not demonstrated redistribution. Weaker organization without a
matched intervention is correlated weakening. A later changed readout without
local mediation does not support DR4.

The route-mass closure is dimensionally explicit. Boundary flux is the
time-integrated exported coherence over the declared post-formation window,
using the same boundary and measure as the route-mass delta. Crossings are
counted exactly once; an instantaneous rate sample or double-counted
departure/arrival record cannot close the continuity residual.

Temporal and geometric variants are likewise bounded. Proper-time annotations,
arrival histograms, and curvature diagnostics are observations until the
declared organization mediates a later local operation. Forming packets must be
excluded before a later independent relation is claimed, and an added
coincidence/resonance policy changes authority to a closure or extension.

Producer ownership is fail-closed: D0 permits no load-bearing post-formation
producer mutation. A producer that chooses export timing, amount, or
destination makes the row B-R even when conservation passes. Restoration v1
covers current-state equivalence; reset-sensitive claims require v2, while
external candidate state requires separate identity composition.

Ownership is derived from producer-call, scheduled-event, mutation-path,
native-lineage, and export-decision traces rather than authored booleans.
Scheduling an export without directly mutating state still establishes
producer authorship. B-R classification records that ownership; it is not
positive B-R evidence unless emission, route-mass change, continuity, and the
organization/readout/mediation gates also pass.

Cross-field validation now blocks contradictory rows mechanically. A blocked
representation cannot carry a supported row decision; full or bounded-partial
mediation cannot coexist with a false mediated-change flag; unresolved mixed
mediation cannot exceed DR3; and blocked D0a authority cannot be promoted into
coherence-only D0a evidence. Persistent D0c becomes a new D0a candidate rather
than an in-place D0c upgrade, while a D0b observable used causally by transport
must acquire exact-derived authority or be classified as a closure.

I3 may now instantiate the 70 false-positive controls as comparable,
derived-fixture-only nulls. Each null must identify the claim under test and
false-positive scenario and match the candidate's semantic class, authority,
mediator domain, internal-time policy, schema, carrier, and continuation
contract. Matching topology alone is insufficient. Those rows may close
false-positive paths but cannot assign a positive DR rung.

The revision chain is explicit: protected runtime baseline
`7075ecb5e464401df96f16eac171fbefe0e532dc`, I1/I2 governance base
`07255b46479d678f649bd89b3f92ceeb95c8d98a`, then this generated I2 artifact.
I2 changes no protected runtime or contract surface.

## Iteration 3 - Active Nulls And Failure Baselines

- [x] Instantiate `label_only_decay`.
- [x] Instantiate `wall_clock_decay`.
- [x] Instantiate `post_hoc_weakening_trace`.
- [x] Instantiate `forming_activity_never_stopped`.
- [x] Instantiate `relation_persists_but_does_not_weaken`.
- [x] Instantiate `relation_weakens_but_has_no_later_readout_effect`.
- [x] Instantiate `global_route_selector`.
- [x] Instantiate `hidden_producer_update`.
- [x] Instantiate unrecorded post-formation producer call.
- [x] Instantiate export-authoring producer call retained as D0-R.
- [x] Instantiate `missing_internal_time_owner`.
- [x] Instantiate `missing_invariant`.
- [x] Instantiate `missing_restoration_state`.
- [x] Instantiate `report_digest_as_runtime_state`.
- [x] Instantiate `native_relabel_from_producer`.
- [x] Instantiate `RCAE_demand_as_graph_evidence`.
- [x] Instantiate `trail_or_stigmergy_relabel`.
- [x] Instantiate D0-specific false-positive controls.
- [x] Instantiate route-mass loss as organization-weakening relabel.
- [x] Instantiate organization weakening without causal mediation.
- [x] Instantiate constant-mass internal reorganization as export relabel.
- [x] Instantiate unclosed route-boundary continuity.
- [x] Instantiate added export policy as ordinary D0-R relabel.
- [x] Instantiate mass-unmatched organization intervention.
- [x] Instantiate `proper_time_annotation_as_causal_alignment`.
- [x] Instantiate `added_coincidence_window_as_native_temporal_organization`.
- [x] Instantiate `arrival_histogram_as_causal_mediation`.
- [x] Instantiate `fixed_delay_single_path_as_dispersion`.
- [x] Instantiate `periodic_rephasing_as_monotonic_decay`.
- [x] Instantiate `diagnostic_domain_as_mediator_domain`.
- [x] Instantiate `mixed_domain_without_load_bearing_isolation`.
- [x] Instantiate `forming_packet_continuation_as_later_independent_readout`.
- [x] Instantiate `temporal_intervention_with_unmatched_state`.
- [x] Instantiate `geometric_observable_without_local_transport_intervention`.
- [x] Instantiate A/B/C-specific invariant and relabel controls.
- [x] Record semantic comparability per row and reject topology-only comparability.
- [x] Record claim under test, scenario direction, violated gate, and expected failure per row.
- [x] Retain a predicate receipt and blocker-repair mutation for every null row.
- [x] Require bad-fixture rejection and repaired-fixture non-rejection before `failed_closed`.
- [x] Machine-reject the eight frozen cross-field contradiction fixtures.
- [x] Machine-reject integrated-flux, matched-intervention, and ownership violations.
- [x] Treat affirmative discriminators relative to their overclaim, not as universal failures.
- [x] Keep six disjoint control families separate from overlapping affirmative, dimensional, and ownership tags.
- [x] Freeze the future candidate-to-null semantic comparability resolver schema.
- [x] Freeze new-identity records for D0c/D0b semantic transitions.
- [x] Keep candidate-specific source-current control execution pending later iterations.
- [x] Require all active nulls to fail closed.
- [x] Record `failed_open_rows = 0` before positive admission.
- [x] Assign no positive DR rung from active-null fixtures.
- [x] Record active nulls as derived fixtures, not scientific evidence.
- [x] Emit active-null JSON and report with clear `failed_closed` semantics.

### Iteration 3 Result

```text
status = passed
acceptance_state = accepted_active_nulls_fail_closed_no_positive_decay_evidence
source_I2_output_digest = a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf
active_null_row_count = 70
common_active_null_row_count = 16
D0_active_null_row_count = 28
candidate_A_active_null_row_count = 5
candidate_B_active_null_row_count = 8
candidate_C_active_null_row_count = 5
schema_relation_active_null_row_count = 8
affirmative_discriminator_row_count = 5
dimensional_control_row_count = 5
trace_derived_ownership_control_row_count = 5
cross_cut_counts_are_tags_not_additional_rows = true
validator_receipt_count = 70
validator_bad_fixture_rejection_count = 70
validator_repaired_fixture_non_rejection_count = 70
future_candidate_control_resolver_schema_frozen = true
future_semantic_transition_record_schema_frozen = true
failed_closed_rows = 70
failed_open_rows = 0
positive_evidence_opened = false
candidate_rows_classified = false
decay_relation_ladder_rung_assigned = false
decay_relation_ladder_ceiling = DR0_no_source_current_decay_evidence
n31_closeout_ladder_rung_assigned = false
n31_closeout_ceiling = N31-C1_source_and_semantic_contract_admitted
n31_c2_active_null_component_satisfied = true
n31_c2_representation_component_pending_iteration_4 = true
src_diff_empty = true
protected_runtime_contract_diff_empty = true
ready_for_iteration_4_D0a_representation_gate = true
output_digest = e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea
artifact_sha256 = b41d43e6b0a0e411b488ce7a9692ccd9183b9a023da4d479cd2f531e3de026ff
report_sha256 = e59ad5dd4a3093d596c14c1976b6605dd2c8765347fd08c3c4988487e2a09738
script_sha256 = 44c6c2c398eb2a66b7014e5dc3b9ce809ee0312bb013d4889eb6ca156773fcc8
```

### Iteration 3 Interpretation

I3 is the pre-positive admission boundary. Each frozen control is instantiated
as a claim-relative derived fixture with an explicit false-positive scenario,
violated gate, expected claim failure, and semantic comparability contract.
`failed_closed` means the blocker triggered and the specific overclaim was
rejected; it does not mean a scientific runtime probe failed. `failed_open`
would be a control-governance failure, and no such row exists.

The status is validator-derived rather than registry-authored. Every row stores
a named predicate, exact rejected gate, bad-fixture digest, targeted repair
mutation, repaired-fixture digest, and both predicate outcomes. A row receives
`failed_closed` only when the bad fixture is rejected and the repaired fixture
is not. Repair removes the targeted blocker; it does not create positive
evidence.

The nulls are not generic across semantic classes. A future positive row may
consume an I3 null only when semantic class, authority, organization and
load-bearing domains, internal-time policy, candidate schema, carrier, and
continuation-state contracts match. Equal topology alone is insufficient; a
nonmatching null must be regenerated for the positive candidate.

The 70 rows form six disjoint families. Affirmative, dimensional, and ownership
counts are overlapping tags on those rows, not another 15 executions. I3 is a
baseline control library rather than a universal pass. A later resolver must
record candidate ID, control ID, matched I3 null, comparability status/digest,
regeneration requirement, and the resolved source-current control artifact.

Five controls are affirmative discriminators viewed against a specific
overclaim: exact cache recomputation, observable disconnection, mediator
clamping, an allegedly complete or node-scalar-complete history contrast, and
equal-C/different-S future contrast. Their fail-closed result rejects the
overclaim under test. It does
not turn their orthogonal implication into positive I3 evidence.

The machine fixtures also enforce the distinctions introduced in I2. An
instantaneous outward flux rate cannot close a time-integrated route-mass
delta; mass loss cannot substitute for organization weakening; organization
weakening cannot substitute for mediation; and unmatched interventions cannot
support DR4. Producer ownership is derived from calls, scheduled events, and
export decisions, so scheduling without direct mutation can still force B-R
classification. B-R classification remains separate from positive B-R decay
support.

I3 demonstrates validator semantics over derived fixtures, not runtime
observability. Later source-current rows must still resolve call traces, event
lineage, packet identities, mutation paths, read-path guards, and restoration
state against candidate-specific controls. D0c persistence and causal D0b use
must create new candidate identities with the source row retained unchanged;
neither transition may rewrite the original row in place.

I3 does not satisfy the whole `N31-C2` rung. Its active-null component passes,
but I4 must still establish the D0a representation boundary. Therefore the
closeout ceiling remains `N31-C1`, no positive DR rung is assigned, and I3 is
ready only for the I4 representation gate.

## Iteration 4 - D0a Representation Gate

- [x] Enumerate complete D0a state needed by the theory claim.
- [x] Compare it field-by-field with source-current LGRC9V3 state.
- [x] Separate node scalar coherence from complete spatial/flux organization.
- [x] Separate route mass from route organization and later causal mediation.
- [x] Determine whether route support, boundary, and net flux are exactly measurable.
- [x] Determine organization-observable authority and update owner.
- [x] Determine representability separately for each admitted organization domain.
- [x] Do not infer native resonance or eligibility from timing annotations alone.
- [x] Determine whether organization intervention can hold route mass and other state equal.
- [x] Determine whether graph topology and edge/packet state form an exact discrete representation.
- [x] Determine whether a spectral decomposition is exact, lossy, or missing.
- [x] Freeze projection basis and operators if exact projection is claimed.
- [x] Record ordered route nodes, anchor, coordinate maps/orientations, and exact context exclusion/reinsertion paths.
- [x] Separate spatial organization from boundary-transfer flux.
- [x] Freeze overlap/orthogonality and temporal support.
- [x] Freeze intervention semantics and reconstruction error bound.
- [x] Classify `set_state()` as a surgical matched-state clamp and validate its invariants.
- [x] Block the clamp from native-formation and autonomous-weakening evidence.
- [x] Freeze the I7 weakening-order preregistration schema without selecting an outcome-dependent order.
- [x] Freeze the future I7 route-mass window accounting requirements.
- [x] Record induced geometry as a response component with a separate promotion gate.
- [x] Close the I3-to-I3R1 revision lineage and prove unchanged scientific control semantics.
- [x] Prove projection has no independent causal state.
- [x] Assign exactly one D0a representation status.
- [x] Block positive D0a if status is lossy or missing.
- [x] Do not invent persistent slow-state variables.
- [x] Record theory support separately from runtime representation support.
- [x] Emit representation-gate JSON and report.

### Iteration 4 Result

```text
status = passed
acceptance_state = accepted_scoped_spatial_D0a_exact_projection_representation_gate_no_positive_decay_evidence
d0a_representation_status = represented_by_exact_projection
d0a_representation_status_scope = registered-route spatial C distribution and internal oriented flux; separate boundary transfer; exact context
spatial_D0a_representation_gate_open = true
temporal_D0a_representation_gate_open = false
arrival_distribution_D0a_representation_gate_open = false
mixed_D0a_representation_gate_open = false
identity_roundtrip_exact = true
observed_reconstruction_error = 0.0
reconstruction_error_bound = 1e-12
positive_evidence_opened = false
decay_relation_ladder_ceiling = DR0_no_source_current_decay_evidence
n31_closeout_ceiling = N31-C2_active_nulls_and_representation_boundary_established
n31_progress_rung = N31-C2_active_nulls_and_representation_boundary_established
n31_progress_rung_assigned = true
n31_closeout_ladder_rung_assigned = false
ready_for_iteration_5_D0c_comparator = true
ready_for_iteration_7_spatial_D0a_probe = true
iteration_7_representation_admission_complete = true
iteration_7_execution_preconditions_complete = false
i3_revision_id = N31-I3R1
i3_revision_lineage_output_digest = b6f6c1948f723d5fbb6008348b804b778993718da18c4b7efb3a499a8757de64
i3_revision_lineage_sha256 = 2ac6582625b0898fd799c545de385a757925226eae4d38803d903549e2133398
output_digest = b7b6f34e3978ec4a410a77e36bc1b548f1baf96dbda7987803d544fc737c3597
artifact_sha256 = eab3b993ad9990c2a7ba47e2445f62b520e003d9c938bc9cbc9590e428dd3782
conformance_fixture_sha256 = d9aa3aedbb0af3521a273533505279810a71d2a77dfdfd8fa5d39ec706a0e23a
src_diff_empty = true
```

I4 consumes the committed I3 artifact as `N31-I3R1`. The earlier reviewed I3
package and I3R1 have different artifact/output digests because I3R1 adds
validator-derived receipts, bad/repaired-fixture evidence, and future
resolver/transition schemas. The generated revision-lineage record proves that
the 70 control identities, scientific meanings, no-positive-evidence status,
and DR0 ceiling did not change. The earlier package is recorded but is not
consumed by I4.

I4 establishes a representation boundary, not a decay result. The conformance
fixture executes public LGRC9V3 packet operations and derives its projection
from the complete current `lgrc9v3_restoration_identity_v1`. It factors the
registered route's C distribution and internal oriented flux into a spatial
organization channel, keeps boundary flux in a separate transfer channel, and
retains every other scientific field in an exact matched context. Ordered route
nodes, the anchor, coordinate maps and orientations, and all excluded and
reinserted identity paths are machine-readable. Recomposition has zero observed
error. The projection is recomputed, is not persisted as runtime state, and is
not fed back into transport, so it introduces no independent slow state.

The mass/organization contrast keeps route mass at `2.5`, keeps node `1`
coherence at `0.75`, and keeps every non-organization identity field matched,
while changing the complete route C distribution through public
`LGRC9V3.set_state()`. This demonstrates that one node scalar, route mass, and
route organization are distinct representational objects and that a matched
native-state intervention is representable. The intervention is explicitly a
`surgical_matched_state_clamp`: coherence bounds, total node coherence,
conserved budget, packet-ledger error, boundary transfer, and exact queue/context
are checked. Because dependent constitutive fields are not recomputed, the
clamp is not native formation or autonomous weakening evidence. It does not
demonstrate that organization mediates any later readout.

Support nodes, internal edges, the route boundary, and instantaneous signed
boundary flux are exactly enumerable for the registered route. The measured
`0.03125` outward value remains an instantaneous flux rate; I4 does not
integrate a post-formation window and does not claim exported route mass or
closed boundary continuity.

The future I7 route-mass contract must count internal departure/in-flight mass
once, integrate boundary crossing once, avoid recounting outside arrival, treat
re-entry as signed inward transfer, and record support/boundary reclassification
explicitly. Instantaneous flux cannot substitute for this window.

The global status is scoped to one admitted spatial C/J_C carrier lane.
Induced geometry and native functional-coupling state are representable only
as response components of that lane, not as standalone carrier claims. Native
timestamps, proper times, and delays do not create a temporal-alignment
mediator. An exact arrival-history relation remains a D0b observable candidate,
not persistent D0a state. Mixed mediation remains unresolved and blocked.
Induced geometry remains a response component rather than an independently
admitted carrier; promotion requires its own source-current state/projection,
weakening order, local-transport intervention, matched mass/transfer controls,
later-readout dependence, and clamp/ablation effect.

A truncated spectral slow mode is explicitly lossy. A full spectral route is
not admitted because no canonical degeneracy and intervention contract is
frozen, and it is unnecessary: the finite registered-route coordinate basis
already gives an exact roundtrip. I4 therefore permits a later spatial D0a
attempt without pre-claiming persistence, weakening, or causal mediation.
Before I7 executes, the candidate-specific observable, stronger/weaker
orientation, baseline, threshold, tolerance, trajectory rule, monotonicity, and
sign-ambiguity resolution must be frozen before outcomes. Representation
admission is complete; those execution preconditions are not.

`N31-C2` is recorded as the current progress rung and ceiling. The terminal
`n31_closeout_ladder_rung_assigned` flag remains false until final N31 closeout.

## Iteration 5 - D0c Instantaneous Geometry Comparator

- [x] Declare source-current fixture and route-local geometry relation.
- [x] Declare thresholds before execution.
- [x] Record complete forming-current state.
- [x] Record instantaneous C/J_C-derived geometry/readout.
- [x] Stop forming activity explicitly.
- [x] Record immediate post-withdrawal state/readout.
- [x] Verify whether effect disappears with current.
- [x] Preserve conservation and keep later local encounter out of scope at DR1.
- [x] Reject durable-aftereffect relabel when persistence is absent.
- [x] Reconcile the original reviewed I4 identity with committed `N31-I4R1`.
- [x] Record registered-cycle and canonical native-edge current orientations.
- [x] Verify balanced node-current divergence.
- [x] Separate formation-input stop from forming-carrier exhaustion.
- [x] Regenerate controls against the exact I5 semantic contract.
- [x] Record maximum D0c/DR ceiling honestly.
- [x] Emit source-current artifacts, JSON, and report.

### Iteration 5 Result

```text
status = passed
acceptance_state = accepted_source_current_D0c_DR1_instantaneous_geometry_comparator_no_persistence_no_decay
primary_semantic_class = D0c
representation_or_authority_class = exact_derived_projection
candidate_disposition = supported
row_decision = supported
forming_packet_current_l1_norm = 0.30000000000000004
post_withdrawal_packet_current_l1_norm = 0.0
signed_packet_current_by_registered_orientation = {0: 0.1, 1: 0.1, 2: 0.1}
signed_packet_current_by_native_edge_orientation = {0: 0.1, 1: 0.1, 2: -0.1}
maximum_absolute_node_current_divergence = 0.0
formation_input_stopped = true
formation_input_stop_checkpoint = forming_cycle_packets_in_flight
forming_carrier_exhausted = true
forming_carrier_exhaustion_checkpoint = first_post_withdrawal_arrival_complete
active_forming_carrier_interval_is_post_formation_window = false
route_mass_error_forming_to_post = 0.0
coherence_coordinate_error_forming_to_post = 1.1102230246251565e-16
closed_system_budget_span = 0.0
source_current_D0c_candidate_supported = true
positive_evidence_opened = true
positive_evidence_scope = source_current_D0c_instantaneous_comparator_only
positive_decay_evidence_opened = false
D0a_persistence_supported = false
D0a_weakening_supported = false
causal_mediation_supported = false
decay_relation_ladder_rung = DR1
n31_progress_rung = N31-C2_active_nulls_and_representation_boundary_established
n31_c3_D0c_classification_component_satisfied = true
n31_c3_overall_pending_D0b_and_D0a_classification = true
n31_closeout_ladder_rung_assigned = false
ready_for_iteration_6_D0b_finite_window_relation = true
direct_I3_null_consumption_count = 0
candidate_specific_control_regeneration_count = 6
i4_revision_id = N31-I4R1
i4_revision_lineage_output_digest = 6dbd1441b5fcdce666d8eeca287cd59205cc4d34495016a0aefe3da9b818eb16
i4_revision_lineage_sha256 = a8781a04980b0a650a0ebfeae41f34a067a188f72c57b71f140ad1048642d5ba
trace_output_digest = c5d2609960d765bd3b97b65664a2ca86e6d16228ad34bf0714e31d093f7fe395
trace_sha256 = 4e726a0a3ba9b9988a11addf5dd2712c9dcd8da9bd20580229416e415f4d0c5d
output_digest = 95d1a1f2c3003a7eeaa1edeaf9a0e843ac92e2c4af010e04a045233b445ac88b
artifact_sha256 = 6b4707cd8b7a10d563cb55f5b61fd4d857161c7b644218ed18cdc7b541be7704
src_diff_empty = true
```

I5 consumes the committed I4 artifact as `N31-I4R1`. The reviewed pre-hardening
I4 package and I4R1 have different artifact/output identities. The generated
lineage retains both identities and records the hardening reason. Its normalized
scientific-outcome comparison shows that exact spatial representation, DR0,
positive-evidence quarantine, and I5 admission are unchanged. The earlier full
artifact was not retained in the repository and is not claimed as the consumed
source; I5 consumes the exact committed I4R1 artifact.

I5 uses a registered three-node route arranged as an internal cycle. Three
equal native packets depart at the same event time, one along each oriented
edge. During transit, every route node has been debited by the same amount, so
the anchor-relative C coordinates are unchanged. Internal in-flight packet
mass is counted once, so registered route mass is also unchanged. What appears
is a nonzero oriented packet-current cycle, measured as packet amount divided
by native event-time transit duration.

The packet-current signs are explicit rather than inferred from edge IDs. The
registered cycle orientation is `0 -> 1`, `1 -> 2`, `2 -> 0`, producing the
signed vector `{+0.1,+0.1,+0.1}`. The canonical restoration identity stores
edge `2` as `0 -> 2`, producing `{+0.1,+0.1,-0.1}` in native-edge orientation.
Both encode the same transport. Outflow-minus-inflow divergence is zero at all
three route nodes.

The next three native events complete the three arrivals. They restore the
original node C distribution, remove all in-flight packet current, and empty
the queue. No `set_state()`, static edge-flux cancellation, hidden selector, or
post-formation producer is used. This cleanly isolates an instantaneous
`J_C`-indexed geometry component from route mass and spatial C coordinates.
It is an instantaneous state-flux geometry comparator, not an induced metric,
curvature, Hessian, or geometric transport intervention.

Formation input stops after the final predeclared departure is processed. The
packets then remain the active forming carrier from event time `0` to `1`; this
interval is not a post-formation persistence window. “Withdrawal” occurs when
all three native arrivals commit and the carrier is exhausted. Arrived-packet
records remain in the scientific state, but the exact current projection
consumes only in-flight records. Counting historical packets as current fails
closed.

The result supports `D0c` at `DR1`: an attributable source-current relation is
formed. It does not support DR2 because the selected current component is zero
at the first post-arrival checkpoint. There is consequently no persistent
relation to weaken, and no later-readout or mediation evidence. The
`instantaneous_geometry_as_durable_decay` control fails closed, so the result
is transient packet propagation/current geometry, not decay.

I5 does not directly consume generic I3 null fixtures. Each inherited control
meaning is compared against the I5 semantic contract (`D0c`, exact-derived,
functional coupling, packet-current carrier, complete current state). Because
at least one load-bearing field differs for every inherited control, all five
are regenerated against the source-current I5 trace with comparability digests.
The history-as-current control is candidate-specific and has no I3 source row.

I5 satisfies the D0c component needed for `N31-C3`, but the overall progress
ceiling remains `N31-C2` pending the I6 D0b and I7 D0a classifications. The
terminal closeout rung remains unassigned.

## Iteration 6 - D0b Finite-Window Derived Relation

- [x] Define exact history support and window semantics.
- [x] Build relation from admitted source-current packet/flux history.
- [x] Prove cache recomputation from exact history.
- [x] Stop forming activity.
- [x] Show old history leaving the window under internal progression.
- [x] Record weakening of the derived relation.
- [x] Remove/recompute cache and compare identity.
- [x] Verify cache has no independent causal freedom.
- [x] Run compute-versus-omit equal-branch continuation.
- [x] Classify compute-versus-omit as an observer-side-effect control, not an organization intervention.
- [x] Restore and replay source history and cache.
- [x] Instantiate and recursively validate the complete I2 nested contracts.
- [x] Freeze native-arrival packet-event measure semantics.
- [x] Test strict-left and inclusive-right window equality cases.
- [x] Record global-model-event-time scope and block route-local-clock decay wording.
- [x] Record I5-to-I5R1 provenance and unchanged scientific meaning.
- [x] Split positive-to-positive decreases, total decreases, and final expiry.
- [x] Keep fading observable below DR4 absent causal mediation.
- [x] Emit source-current artifacts, JSON, and report.

### Iteration 6 Result

```text
status = passed
acceptance_state = accepted_source_current_D0b_DR3_finite_window_observable_below_causal_trail
primary_semantic_class = D0b
representation_or_authority_class = exact_derived_projection
candidate_disposition = supported
row_decision = supported
window_interval = (T - 4.0, T]
route_arrival_event_times = [1.0, 1.5, 2.0]
relation_at_forming_carrier_exhaustion = 0.30000000000000004
post_formation_progression_values = [0.30000000000000004, 0.2, 0.1, 0.0]
route_mass_span = 0.0
closed_system_budget_span = 0.0
D0b_persistence_supported = true
D0b_weakening_supported = true
window_expiry_supported = true
derived_cache_recomputation_status = passed_exact
snapshot_load_status = passed_exact_source_history_and_relation
branch_continuation_status = passed_compute_vs_omit_observer_side_effect_control
branch_continuation_scope = observer_side_effect_only_not_mediator_intervention
organization_intervention_valid = false
local_transport_intervention_status = not_run
later_readout_probe_relation = unresolved
clock_scope = global_model_event_time
route_local_proper_time_advanced_during_expiry = false
local_clock_decay_claim_allowed = false
packet_transfer_measure = atomic_native_packet_arrival_measure
window_boundary_conformance = passed
positive_to_positive_decrease_count = 2
total_strict_decrease_count = 3
final_expiry_step_count = 1
route_mass_contract_required_fields = 20
route_organization_contract_required_fields = 15
causal_mediation_contract_required_fields = 18
missing_nested_required_fields = {}
causal_mediation_supported = false
positive_causal_decay_evidence_opened = false
decay_relation_ladder_rung = DR3
n31_progress_rung = N31-C2_active_nulls_and_representation_boundary_established
n31_c3_D0b_component_satisfied = true
n31_c3_overall_pending_D0a_classification = true
n31_closeout_ladder_rung_assigned = false
direct_I3_null_consumption_count = 0
candidate_specific_control_regeneration_count = 15
ready_for_iteration_7_D0a_source_current_causal_probe = true
i5_revision_id = N31-I5R1
i5_revision_lineage_output_digest = 1bb729f219fbb4e0e5f52615e4213567e4f46b195b7bc00a27376c283203e9c8
i5_revision_lineage_sha256 = 4d0e0dded207fc7c1da61114ee603835a168f58d155b7912edb2e6f189957aa0
trace_output_digest = 7941db25a5c048f450573725f3844c098f7060a0ca265cb2dd1711ced4e92f2f
trace_sha256 = 42f7436351b59181b9a55a2869e97de36a37646b79b05adeae9e12fc9c1b2039
output_digest = 206088cbe96bb37e119aa88a543f728170d206ad3ce15e9da24f1b9a5f77313a
artifact_sha256 = a076c8d78adeb0a92b0d28f1393f73a0e7731e9a39f16374b94d37b69ebf0a22
src_diff_empty = true
```

I6 instantiates the finite-window coherent-coupling relation defined in the
RC-Distance source. Three equal native packets complete transfers over one
registered internal route edge at event times `1.0`, `1.5`, and `2.0`. Each
completed transfer is counted once on arrival; departure and arrival are not
double-counted. The bridge uses an explicitly declared atomic native-arrival
event measure; it is an operational discretization of the theory relation, not
the uniquely implied discretization. With `DeltaT = 4.0`, the relation is:

```text
F_01(T; DeltaT) = sum |packet amount|
                  for route arrivals in (T - DeltaT, T]
```

When the final forming packet arrives at `T = 2.0`, all three source-current
records are inside the window and `F_01 = 0.3`. A disjoint, predeclared packet
lane then advances native LGRC event time. It neither intersects the route
support nor contributes to `F_01`. At the first progression checkpoint all
three route records remain in the window. At later checkpoints they leave one
by one, producing `0.3 -> 0.2 -> 0.1 -> 0.0`. This is a geometric change in
the recent-flux coupling graph: the registered route edge loses recent
transport support while route mass and total coherence remain unchanged.

The equality conformance fixture evaluates the retained source-current history
at `T = 2.0`, `5.0`, `5.5`, and `6.0`. The event at the right endpoint is
included; events exactly at the left endpoint are excluded. This directly
validates `(T - DeltaT, T]`, rather than only checking values away from equality.

The progression lane is an explicit experimental scaffold. All of its packet
schedule calls occur before the first runtime event, and no producer call is
made after route formation. Its native events provide bounded internal-time
progression, but I6 does not claim that the route autonomously generated that
progression. It advances global model event time, not route-local proper time,
so unrelated graph activity can age the relation. Autonomous progression and
route-local-clock decay therefore remain naturalization debt.

The relation is not an LGRC state variable. It is recomputed exactly from the
native packet ledger and current native event time. An experiment-local report
cache is removed and rebuilt at every checkpoint without changing restoration
identity. Snapshot/load restores both the source history and recomputed value
exactly. This supports exact-derived authority and rejects an independent
decay-state relabel.

The observer-side-effect control restores two equal branches from the same
post-formation state. One branch computes the observable and the other does
not; both then process the same native progression events and finish with
equal receipts and restoration identities. This proves that computing the
observable has no runtime side effect. It does not alter packet history or
clamp organization under matched continuation state, so it is not a mediator
intervention and no independent later probe is established. I6 supports `D0b`
at `DR3`, not `DR4`, a causal trail, or causal decay. Feeding the observable
back into transport later would require explicit authority reclassification as
an effective closure or added mechanism.

The candidate recursively instantiates all `20` route-mass, `15`
route-organization, and `18` causal-mediation fields frozen by I2; no nested
field is missing. The `N31-I5R1` lineage pins the earlier reviewed and current
I5/trace identities and records that provenance, orientation, carrier-phase,
and control hardening did not change I5's `D0c/DR1` scientific result.

All inherited control meanings are regenerated against the exact I6 contract:
`D0b`, exact-derived authority, functional-coupling domain, native route-
arrival history carrier, and complete LGRC continuation state plus declared
history functional. No generic I3 fixture is consumed directly as positive
source-current evidence.

I6 satisfies the D0b classification component needed for `N31-C3`. The
overall progress ceiling remains `N31-C2` until I7 classifies the admitted
spatial D0a lane. The terminal closeout rung remains unassigned.

## Iteration 7 - D0a Source-Current Causal Probe

- [ ] Confirm Iteration 4 admitted native or exact representation.
- [ ] Skip with explicit blocker if representation is lossy or missing.
- [ ] Declare fixture, thresholds, and finite attempt matrix before execution.
- [ ] Form attributable route-local coherence organization.
- [ ] Instantiate separate route-mass, route-organization, and causal-mediation contracts.
- [ ] Stop forming activity.
- [ ] Demonstrate bounded persistence.
- [ ] Demonstrate weakening under ordinary internal progression.
- [ ] Show later local readout dependence on the mediator.
- [ ] Clamp/intervene on slow organization and change/remove readout effect.
- [ ] Match route mass and all other continuation state during organization intervention where possible.
- [ ] Report bounded partial or unresolved mediation when exact matching is unavailable.
- [ ] Close signed boundary-flux continuity before claiming conservative export.
- [ ] Classify weakening mode and D0 subtype from independent facts.
- [ ] Record organization domain and weakening trajectory class.
- [ ] Separate observed diagnostic domains from the load-bearing mediator domain.
- [ ] Resolve a mixed row to one load-bearing domain or retain unresolved mediation.
- [ ] For a temporal lane, prove the relation derives from admitted native timing state without added phase or coincidence state.
- [ ] Match packet amount, route mass, spatial organization, and other continuation state in temporal intervention.
- [ ] Distinguish propagation of forming packets from a later encountered route mediator.
- [ ] Exhaust, causally isolate, or identity-exclude forming packets before independent-readout language.
- [ ] Require local-transport intervention before promoting geometric shallowing to causal D0a.
- [ ] Require ordinary post-formation flux and no added export policy for D0-R.
- [ ] Compare instantaneous D0c and observable-only D0b controls.
- [ ] Enforce strict D0 producer-role audit.
- [ ] Record every post-formation producer call and prove the state-mutating call list is empty.
- [ ] Preserve complete conservation.
- [ ] Record complete-state rather than node-scalar equality.
- [ ] Emit source-current artifacts, JSON, and report.

## Iteration 8 - D0 Replay, Controls, And Classification

- [ ] Consume D0c, D0b, and any admissible D0a candidate rows.
- [ ] Run artifact replay.
- [ ] Run snapshot/load replay.
- [ ] Use restoration identity v2 for reset-sensitive rows.
- [ ] Run duplicate replay.
- [ ] Run equal-state branch continuation.
- [ ] Run mediator and complete-state interventions.
- [ ] Run cache recomputation and execution reconstruction separately.
- [ ] Run conservation and timing audits.
- [ ] Run all D0 controls.
- [ ] Demote or reject failed-open rows.
- [ ] Classify D0a/D0b/D0c separately.
- [ ] Preserve D0-R as one D0 subtype rather than all coherence-only decay.
- [ ] Retain route mass, organization, readout, and mediation results separately.
- [ ] Classify geometric, temporal-alignment, and arrival-distribution variants without promoting observables.
- [ ] Classify recurrence as modulation rather than monotonic decay.
- [ ] Treat intervention-backed bounded partial mediation as Boolean-supported but qualified-partial only.
- [ ] Block causal D0-R when mediation is absent or unresolved.
- [ ] Decide whether added-mechanism admission is scientifically justified.
- [ ] Do not infer added mechanism solely from missing D0 representation.
- [ ] Emit replay/control/classification JSON and report.

## Iteration 9 - Added-Mechanism Admission

- [ ] Record one allowed added-mechanism admission reason before opening candidates.
- [ ] Permit D0 insufficiency, representation blocker, semantic control, bridge test, or downstream-reusability rationale.
- [ ] Do not require added-mechanism execution after D0 success.
- [ ] Decide A/B/C execute, classify-only, or inapplicable status separately.
- [ ] Freeze candidate-specific topologies.
- [ ] Freeze equations/relations, units, phases, and clocks.
- [ ] Freeze candidate-specific invariants and controls.
- [ ] Freeze producer/native/closure status before execution.
- [ ] Do not use one generic scalar decay law.
- [ ] Do not rank nonequivalent candidates by raw effect size.
- [ ] Emit admission JSON and report.

## Iteration 9-A - Release-Efficacy Attenuation

- [ ] Vary registered internal age/phase under matched carrier state.
- [ ] Select packet amount only at creation.
- [ ] Prove in-flight packet amount remains unchanged.
- [ ] Prove source debit equals packet amount equals target credit.
- [ ] Record unreleased coherence remaining at source.
- [ ] Exclude route labels/global selection.
- [ ] Restore all age/phase continuation state.
- [ ] Classify expression attenuation versus field-state decay.

## Iteration 9-B - Conserved Leakage

- [ ] Declare source, destination, amount, schedule, and internal clock.
- [ ] Record B-R export-policy owner and all policy inputs.
- [ ] Bound emitted amount by available source excess and source floor.
- [ ] Debit source through admitted packet mechanics.
- [ ] Record exact in-flight amount and destination credit.
- [ ] Audit full node-plus-in-flight conservation.
- [ ] Exclude hidden reservoir and destruction.
- [ ] Distinguish new leakage policy from ordinary D0 outward flux.
- [ ] Exclude the receiver from the later read path during the registered probe window.
- [ ] Keep D0-R analogue status `not_tested` unless a separate bridge passes.
- [ ] Test local encounter/readout.
- [ ] Restore all lifecycle state.

## Iteration 9-C - Susceptibility Relaxation

- [ ] Declare conductance/susceptibility carrier and units.
- [ ] Declare formation/reinforcement and relaxation laws separately.
- [ ] Use system-internal progression.
- [ ] Record whether state is independently causal.
- [ ] Match complete C while intervening on susceptibility where meaningful.
- [ ] Serialize and restore all state.
- [ ] Exclude hidden producer history.
- [ ] Preserve producer/closure/native distinction.
- [ ] Record naturalization debt.

## Iteration 10 - Added-Mechanism Replay And Controls

- [ ] Consume every executed A/B/C candidate row explicitly.
- [ ] Run artifact, snapshot/load, duplicate, and branch replay.
- [ ] Run candidate-specific invariant controls.
- [ ] Run local-encounter and global-selector controls.
- [ ] Run hidden-state and producer/native controls.
- [ ] Run topology-specific controls.
- [ ] Use v2 for reset-sensitive equivalence.
- [ ] Demote or reject failed-open rows.
- [ ] Emit replay/control JSON and report.

## Iteration 11 - Comparative Classification

- [ ] Compare semantic meaning rather than generic decay labels.
- [ ] Compare theory compatibility.
- [ ] Compare invariant closure.
- [ ] Compare internal-time ownership.
- [ ] Compare local causality.
- [ ] Compare representation and restoration completeness.
- [ ] Compare producer residue and naturalization debt.
- [ ] Compare topology and transfer scope.
- [ ] Record D0-versus-B redistribution boundary.
- [ ] Compare D0-R and B-R without presuming trajectory or readout equivalence.
- [ ] Record `d0_to_br_bridge_status` with exact supporting or rejecting artifacts.
- [ ] Compare route mass, organization, and mediation dispositions independently.
- [ ] Permit multiple mechanisms or non-selection.
- [ ] Record native admission or implementation requirements precisely.
- [ ] Assign DR and N31-C5 ceiling.
- [ ] Emit comparative classification JSON and report.

## Iteration 12 - Closeout And RCAE Return

- [ ] Produce machine-readable return manifest.
- [ ] Produce reader-facing closeout/return report.
- [ ] Map all mandatory return roles to exact artifacts.
- [ ] Record source revisions, digests, environment, and reproduction commands.
- [ ] Record all candidate dispositions.
- [ ] Record representation and projection status.
- [ ] Return route-mass, route-organization, and causal-mediation contracts.
- [ ] Return weakening mode, D0 subtype, export-policy ownership, and bridge status.
- [ ] Return organization domain and weakening trajectory class by candidate.
- [ ] Record cache recomputation and execution reconstruction separately.
- [ ] Record restoration identity by candidate.
- [ ] Record producer residue and naturalization debt.
- [ ] Record selected primitive/closure/extension or non-selection reason.
- [ ] Record outcome-specific P2-I3 recommendation.
- [ ] Record `src_diff_empty = true` for experiment branch.
- [ ] Record `protected_runtime_contract_diff_empty = true` over the frozen path scope.
- [ ] Keep unsafe claim flags false.
- [ ] Assign final DR and N31-C rungs.
- [ ] Mark N31-C6 only when return bundle is reconstructable.
- [ ] Update repository indexes and N30+ handoff after closeout, not before.

## Pre-I1 Schema Normalization Interpretation

The D0-R/B-R review does not add a candidate or iteration. It exposes a schema
ambiguity that must be removed before scientific rows are admitted:

```text
route mass decreased
does not imply
route organization weakened
does not imply
later readout changed because of that organization
```

N31 therefore uses separate route-mass, route-organization, and
causal-mediation contracts. D0-R is admitted only when ordinary post-formation
evolution closes conservative route-boundary export and the independently
measured organization mediates later local readout. An added policy that owns
export remains B-R even when conservation closes. No prior positive fixture
requires migration because this normalization occurred before Iteration 1.

## Closeout Claim Boundary

```text
allowed:
  bounded graph-side decay relation
  bounded fading observable
  bounded primitive or effective closure
  runtime/theory extension requirement
  explicit non-selection or missing-surface result

blocked:
  trail or stigmergic field
  communication or coordination
  memory or learning
  agency or selfhood
  native ecology
  sentience or organism/life
  automatic RCAE adoption
```
