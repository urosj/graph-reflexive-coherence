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

- [x] Confirm Iteration 4 admitted native or exact representation.
- [x] Skip with explicit blocker if representation is lossy or missing.
- [x] Declare fixture, thresholds, and finite attempt matrix before execution.
- [x] Form attributable route-local coherence organization.
- [x] Instantiate separate route-mass, route-organization, and causal-mediation contracts.
- [x] Stop forming activity.
- [x] Demonstrate bounded persistence.
- [x] Demonstrate weakening under experiment-authored, natively executed internal progression.
- [x] Show later local readout dependence on the local source-node C component.
- [x] Clamp/intervene on represented route C and change/remove the local readout effect.
- [x] Match route mass and all other continuation state during organization intervention where possible.
- [x] Report bounded-partial local-C mediation and retain full route-distribution mediation as unresolved.
- [x] Close signed boundary-flux continuity before claiming conservative export.
- [x] Classify weakening mode and D0 subtype from independent facts.
- [x] Record organization domain and weakening trajectory class.
- [x] Separate observed diagnostic domains from the load-bearing mediator domain.
- [x] Resolve a mixed row to one load-bearing domain or retain unresolved mediation.
- [x] For a temporal lane, prove the relation derives from admitted native timing state without added phase or coincidence state.
- [x] Match packet amount, route mass, spatial organization, and other continuation state in temporal intervention.
- [x] Distinguish propagation of forming packets from a later encountered route mediator.
- [x] Exhaust, causally isolate, or identity-exclude forming packets before independent-readout language.
- [x] Require local-transport intervention before promoting geometric shallowing to causal D0a.
- [x] Require ordinary post-formation flux and no added export policy for D0-R.
- [x] Compare instantaneous D0c and observable-only D0b controls.
- [x] Enforce strict D0 producer-role audit.
- [x] Record every post-formation producer call and prove the state-mutating call list is empty.
- [x] Preserve complete conservation.
- [x] Record complete-state inequality for the direction matrix and matched-except-C identity for interventions.
- [x] Emit source-current artifacts, JSON, and report.

Iteration 7 result:

```text
status = passed
acceptance_state = accepted_native_spatial_D0a_DR2_formation_persistence_and_conditional_reorganization_probe
primary_semantic_class = D0a
representation_or_authority_class = exact_derived_projection
organization_domain = spatial_distribution
weakening_mode = internal_reorganization
weakening_mode_qualifier = experiment_authored_conditional_directional_packet_transfer
native_D0a_ladder_ceiling = DR2
conditional_internal_reorganization_relation = supported
mediation_strength = bounded_partial
full_spatial_distribution_mediation_supported = false
n31_closeout_progress_rung = N31-C3
final_D0a_supported = false
final_N31_supported = false
ready_for_iteration_8_replay_controls_classification = true
output_digest = ada29118f7c3cad7db308ff0c026ee09270afbad620c3a613d378f28c35086d1
```

I7 records two separate evidential objects even though they share one runtime
trace:

```text
native_spatial_D0a:
  formation = supported
  persistence = supported
  decay_relation_ladder_rung = DR2
  autonomous_weakening = unsupported

conditional_internal_reorganization:
  perturbation_owner = experiment_fixture
  execution_owner = native_LGRC9V3_runtime
  weakening_direction = supported
  reverse_reinforcement = supported
  local_source_C_consequence = supported_bounded_partial
  native_D0a_rung_effect = separate_not_rung_raising
  D0_decay_relation = false
```

Machine surfaces normalize the same boundary:

```text
provisional_DR4_status = superseded_not_a_native_decay_rung
decay_relation_ladder_rung = DR2_native_D0a_ceiling
mediation_strength = bounded_partial
load_bearing_mediator = local_source_node_C
full_route_distribution_mediation = unresolved
producer_authors_weakening = true
ordinary_autonomous_weakening_generated = false
```

The candidate row, nested mediation/organization contracts, comparison table,
claim flags, and provisional RCAE return projection carry these same facts.
The RCAE projection permits no automatic adoption and is not a final return
manifest. Its added producer-mechanism lane remains open pending I8 confirmation
and I9 admission.

Normalized I7 control summary:

```text
producer_scheduled_D0_decay = failed_closed
forming_packet_exclusion = passed
route_mass_match = passed
direction_matrix = perturbation_control
proper_time_alignment = not_applicable
```

I7 consumes the exact spatial representation admitted by I4 and freezes a
three-row direction matrix before execution. The route begins with coherence
`[0.48, 0.04, 0.48]`. A native `0 -> 1` packet of `0.20` forms a positive
`C[1] - C[2]` effect of `0.20`. A disjoint outside packet advances native LGRC
event time while the effect remains `0.20`. Equal-dose progression then gives:

```text
disjoint hold            = 0.20
internal 1 -> 2 weakening = 0.12
internal 2 -> 1 control   = 0.28
```

Thus event-time advance alone does not weaken the route, the registered
weakening direction reduces but does not erase organization, and reversing the
same internal packet reinforces it. These are different preregistered future
packet queues, not equal-state continuation branches. Route mass remains `1.0`,
closed-system coherence remains `2.0`, no packet crosses the route boundary,
and the signed integrated outward transfer is zero. I7 therefore establishes a
directional internal-redistribution perturbation matrix rather than autonomous
weakening, route-mass loss, or conservative export.

The later readout is a `1 -> 0` packet of `0.22`, also queued before the first
event. The persisted route has source coherence `0.24` and admits the readout
with margin `+0.02`. The weakened route has source coherence `0.20` and rejects
it with margin `-0.02`. A baseline-C clamp removes eligibility from the hold
branch, while restoring formed C rescues the weakened branch. Both controls
preserve route mass; restoration identity v1/v2 is exact before intervention;
and the complete identity differs only at route-node C paths. Native departure
eligibility reads local `C[1]`, so the result establishes a bounded local-C
causal effect. It does not isolate the complete `C[1]-C[2]` distribution as the
mediator, and `set_state()` does not validate induced-geometric causality.

The binary readout is valid but narrow: differentiated admission exists only
for `0.20 < q <= 0.24`. The selected `q = 0.22` was preregistered and gives
`+0.02`/`-0.02` margins, but it is not broad traversal retuning.

The forming packet is exhausted before persistence, progression, and readout.
All packet schedules occur before the first runtime event, and every
post-formation producer-call list is empty. This does not erase producer
authorship: the fixture selects the weakening time, amount, direction, source,
and destination. Native LGRC executes conservative packet transport. The
`producer_scheduled_D0_decay` control therefore fails closed and caps native
spatial D0a at `DR2` for formation and persistence. The conditional
reorganization and local-C readout effect remain useful separate evidence, but
they are not autonomous D0a decay or a native `DR4` result. Temporal and mixed
lanes are out of scope; D0-R is not claimed because there is no boundary export.
I8 remains responsible for replay, reconstruction, control consumption, and
final D0a/D0b/D0c classification.

## Iteration 8 - D0 Replay, Controls, And Classification

- [x] Consume D0c, D0b, and any admissible D0a candidate rows.
- [x] Run artifact replay.
- [x] Distinguish `45` manifest references from `25` unique artifact paths and record `20` repeated cross-source references.
- [x] Require every manifest reference hash to match even when paths repeat across source artifacts.
- [x] Record direct builder replay as I3/I5/I6/I7 and I2/I4 governance/representation verification as transitive.
- [x] Run snapshot/load replay.
- [x] Use restoration identity v2 for reset-sensitive rows.
- [x] Run duplicate replay.
- [x] Run equal-state branch continuation.
- [x] Limit equal-state continuation to replay correctness; add no weakening, mediation, or route-causality evidence.
- [x] Do not consume the I7 directional perturbation matrix as equal-state continuation.
- [x] Preserve the I7 native D0a ceiling at `DR2` unless new autonomous source-current weakening evidence is produced.
- [x] Preserve bounded-partial local-C mediation and full-route mediation debt.
- [x] Record the triggered `producer_scheduled_D0_decay` control as `failed_closed`.
- [x] Audit the narrow readout interval; use a preregistered amount sweep if extending the claim.
- [x] Classify `q = 0.24` as the native floating-point eligibility boundary with effectively zero hold margin.
- [x] Run mediator and complete-state interventions.
- [x] Run cache recomputation and execution reconstruction separately.
- [x] Run conservation and timing audits.
- [x] Run all D0 controls.
- [x] Keep I3 generic pre-positive nulls separate from I5-I7 candidate-specific controls.
- [x] Record all required controls as resolved with no `failed_open` or `not_run` dependent control.
- [x] Demote or reject failed-open rows.
- [x] Classify D0a/D0b/D0c separately.
- [x] Preserve D0-R as one D0 subtype rather than all coherence-only decay.
- [x] Record D0-R as uninstantiated in executed fixtures rather than globally refuted.
- [x] Retain route mass, organization, readout, and mediation results separately.
- [x] Classify geometric, temporal-alignment, and arrival-distribution variants without promoting observables.
- [x] Classify recurrence as modulation rather than monotonic decay.
- [x] Treat intervention-backed bounded partial mediation as Boolean-supported but qualified-partial only.
- [x] Block causal D0-R when mediation is absent or unresolved.
- [x] Decide whether added-mechanism admission is scientifically justified.
- [x] Do not infer added mechanism solely from missing D0 representation.
- [x] Emit replay/control/classification JSON and report.

Iteration 8 result:

```text
status = passed
acceptance_state = accepted_replay_control_backed_D0_classification_with_native_D0a_DR2_ceiling_and_autonomous_weakening_mechanism_need
n31_closeout_progress_rung = N31-C4
native_spatial_D0a_ladder_ceiling = DR2
autonomous_D0a_weakening_supported = false
conditional_internal_reorganization_supported = true
conditional_reorganization_is_D0_decay = false
mediation_strength = bounded_partial_local_source_C
full_route_distribution_mediation = unresolved
added_mechanism_admission_reason = d0_insufficient
added_mechanism_admission_reason_qualifier = d0_insufficient_for_autonomous_causal_weakening
D0_wholly_insufficient = false
ready_for_iteration_9_added_mechanism_admission = true
final_N31_supported = false
output_digest = bf7d5eb98ab6b84e16a86fe4eba662e9b99ac648abd9b9490dcc6598c40cb5d8
```

I8 reconstructs and replays the evidence stack rather than opening another
positive D0 probe. It directly reruns I3, I5, I6, and I7, while I2/I4
governance and representation dependencies are verified transitively through
the exact source chains. It verifies `45` artifact-manifest references resolving
to `25` unique paths, with `20` repeated cross-source references and every
reference hash exact. It also performs exact roundtrips for `19` I7 snapshots
under restoration identities v1 and v2, exact fresh reconstruction and
duplicate replay for all three I7 attempts, and an equal-state continuation
from one complete pre-readout snapshot. Equal-state continuation establishes
replay correctness only; it adds no weakening, mediation, or route-causality
evidence. The I7 direction matrix is explicitly excluded from that equal-state
claim.

The preregistered readout sweep confirms the bounded threshold shape:

```text
q <= 0.20        = hold and weakened branches both admit
0.20 < q <= 0.24 = hold admits and weakened rejects
q > 0.24         = both reject
```

This is a narrow local source-C eligibility interval, not broad traversal
retuning or full route-distribution mediation. The upper endpoint has effectively
zero hold margin and is retained only as the native floating-point eligibility
boundary, not a meaningful positive-margin endpoint.

All `70` I3 generic pre-positive active nulls remain failed closed. They remain
separate from and are not presented as direct per-candidate null consumption.
Across I5-I7 candidate controls,
`22` pass, `6` fail closed as intended, `2` are not applicable with scope, and
none are `failed_open` or `not_run`. I7 retains:

```text
producer_scheduled_D0_decay = failed_closed
forming_packet_exclusion = passed
route_mass_match = passed
direction_matrix = perturbation_control
proper_time_alignment = not_applicable
```

The comparative result is:

```text
D0c = DR1 instantaneous comparator, no persistence or mediation
D0b = DR3 finite-window fading observable, no causal mediation
native spatial D0a = DR2 formation and persistence, no autonomous weakening
conditional reorganization = replay-clean perturbation with bounded local-C effect
D0-R = not instantiated in executed fixtures; ordinary export remains untested
```

Existing LGRC therefore supports spatial formation and persistence plus
conservative externally specified reorganization, but not a native autonomous
weakening trajectory. This supports the schema-valid `d0_insufficient` I9
admission enum only under the qualifier
`d0_insufficient_for_autonomous_causal_weakening`; D0 is not wholly
insufficient. D0-R is not globally refuted because no dedicated ordinary-export
fixture was executed. I8 does not select candidate A, B, or C; all three remain
open for separate admission, and no automatic RCAE adoption is allowed.

## Iteration 9 - Added-Mechanism Admission

- [x] Record one allowed added-mechanism admission reason before opening candidates.
- [x] Permit D0 insufficiency, representation blocker, semantic control, bridge test, or downstream-reusability rationale.
- [x] Do not require added-mechanism execution after D0 success.
- [x] Decide A/B/C execute, classify-only, or inapplicable status separately.
- [x] Freeze candidate-specific topologies.
- [x] Freeze equations/relations, units, phases, and clocks.
- [x] Freeze candidate-specific invariants and controls.
- [x] Freeze fail-closed source-current input allowlists with path, role, phase, historical depth, and forbidden adjacent inputs.
- [x] Separate lane-specific controls from inherited common, D0, and schema-relation obligations.
- [x] Require candidate-specific control regeneration and prohibit direct I3-null consumption.
- [x] Record reviewed I8 versus corrected consumed I8 lineage without a scientific-result change.
- [x] Preserve native carrier authority as `existing_native` and organization-observable authority as `exact_derived_projection`.
- [x] Freeze numeric fixture IDs, ports, orientation, delay, conductance, payloads, role maps, and canonical topology digests.
- [x] Resolve Candidate A formation/release/receiver roles and exact qualifying-event semantics.
- [x] Resolve Candidate B leakage-source role, organization-versus-mass contract, destination isolation, and one-shot receipt semantics.
- [x] Freeze Candidate C's actual conductance consumer path and the missing normal-step hook as closure debt.
- [x] Freeze producer/native/closure status before execution.
- [x] Freeze separate `native_decay_classification` and `added_mechanism_decay_classifications` surfaces before A/B/C execution.
- [x] Use one DR evidence-strength ladder with lane, semantic-class, and authority qualifiers rather than inventing an interchangeable producer ladder.
- [x] Treat the lane split as an additive aggregation projection over I2-frozen fields, not a candidate-schema or rung redefinition.
- [x] Preserve the native lane as `D0a / existing_native carrier / exact-derived organization projection / DR2` with autonomous weakening unsupported.
- [x] Record A, B, and C as separate added-mechanism lanes with independent dispositions and rung qualifiers.
- [x] Record candidate authority using the frozen enum: `producer_mediated`, `effective_non_markovian_closure`, or `runtime_extension_required` where applicable.
- [x] Record the causal-transition owner, producer residue, naturalization debt, and reusable-contract status for every added-mechanism lane.
- [x] Set `native_upgrade_allowed = false` for every added-mechanism lane.
- [x] Assign no positive added-mechanism rung from admission alone.
- [x] Permit later lane-qualified DR5 evidence for A expression attenuation, B conserved export, or C susceptibility relaxation only when candidate-specific gates pass.
- [x] Permit added-mechanism DR6 only for reusable bounded semantics and downstream contract completeness.
- [x] Do not interpret producer-assisted or closure-owned DR5/DR6 as native DR5/DR6.
- [x] Require a future native runtime implementation to be rerun on the native lane before naturalization can change its native rung.
- [x] Keep N31-C6 closeout completeness distinct from DR6 mechanism evidence.
- [x] Do not use one generic scalar decay law.
- [x] Do not rank nonequivalent candidates by raw effect size.
- [x] Emit admission JSON and report.

I9 admission must preserve the bounded I8 capability record:

```text
D0c = DR1 instantaneous geometry
D0b = DR3 fading derived observable without causal mediation
native spatial D0a = DR2 formation and persistence
conditional reorganization = separate experiment-authored perturbation evidence
missing transition = producer-owned autonomous causal weakening
```

A tests release efficacy, B tests conserved leakage/export, and C tests
susceptibility/conductance relaxation. Producer-assisted success cannot
retroactively raise native D0a, and D0-R remains uninstantiated unless a
dedicated ordinary-export probe supports it.

I9 will therefore preserve two simultaneous result surfaces:

```text
native_decay_classification:
  semantic_class = D0a
  carrier_state_authority = existing_native
  organization_observable_authority = exact_derived_projection
  rung = DR2
  autonomous_weakening = unsupported

added_mechanism_decay_classifications:
  A | B | C:
    authority = producer_mediated | effective_non_markovian_closure | runtime_extension_required
    rung = DR0...DR6, earned independently
    rung_qualifier = candidate-specific
    native_upgrade_allowed = false
    producer_residue = explicit
    naturalization_debt = explicit
```

An added-mechanism result may reach DR5 after its intervention, replay,
restoration, invariant, and control gates pass. It may reach DR6 when its
bounded semantics and downstream contract are reusable. Neither result changes
the native DR2 ceiling. If a corresponding mechanism is later naturalized in
LGRC, it must earn a new native classification from source-current native
runtime evidence.

### Iteration 9 Result

```text
status = passed
acceptance_state = accepted_lane_qualified_added_mechanism_admission_frozen_no_candidate_evidence
pre_execution_contract_completeness = passed_after_I9_revision
added_mechanism_admission_reason = d0_insufficient
admission_reason_qualifier = d0_insufficient_for_autonomous_causal_weakening
native_decay_classification = D0a / existing_native carrier / exact-derived organization projection / DR2
A_execution_decision = execute_I9_A
B_execution_decision = execute_I9_B
C_execution_decision = execute_I9_C
A_current_rung = DR0
B_current_rung = DR0
C_current_rung = DR0
positive_candidate_evidence_opened = false
n31_closeout_progress_rung = N31-C4
ready_for_I9_A = true
ready_for_I9_B = true
ready_for_I9_C = true
final_N31_supported = false
source_current_input_counts = A:10 / B:7 / C:7
complete_control_counts = A:57 / B:60 / C:57
direct_I3_null_consumption_count = 0
I8R1_scientific_conclusion_changed = false
output_digest = 4cf2043eebf54d26ce9b98aee77ad8a846cf90e4e1f452dc065fd327633b761d
```

### Iteration 9 Interpretation

I9 is an admission and preregistration result, not an A/B/C support result. It
consumes the exact I2 schema and I8 classification, preserves native spatial
D0a at `DR2`, and admits three separate added-mechanism executions:

```text
A:
  producer-mediated release-efficacy expression policy
  next iteration = I9-A
  current rung = DR0
  maximum bounded meaning = DR5 expression attenuation, not field-state decay

B:
  producer-mediated, coherence-conserving B-R export policy
  next iteration = I9-B
  current rung = DR0
  DR5 requires explicit destination and exact conservation
  DR6 additionally requires a reusable bounded B-R contract

C:
  effective non-Markovian susceptibility closure
  next iteration = I9-C
  current rung = DR0
  DR5 requires restored independent state, causal readout, and controls
  DR6 additionally requires a reusable bounded susceptibility contract
```

Each lane has its own executable canonical topology, fail-closed input
allowlist, relation, units, internal clock, invariant, lane controls, inherited
control obligations, producer ownership, residue, and naturalization debt.
All I3-derived controls must be regenerated for the new carrier and authority;
I9 consumes no I3 null row directly.

A does not attenuate packets in flight. Node 1 is the exact release source;
only created coherence is debited, while `q_unreleased` remains source `C` and
is not a reservoir. Only the registered formation-arrival receipt advances
release phase. B uses node 1 as the leakage source and node 2 as a declared
destination outside the later readout path. It cannot be called D0-R without a
separate bridge, and export mass loss does not count as organization weakening
without the frozen source-contrast and destination-isolation controls.

C owns an independently restored susceptibility state and cannot be called
native memory or coherence-only D0. Its closure applies `S * g_native` after
native conductance reconstruction and before native potential/flux operations.
Ordinary `LGRC9V3.step()` lacks this hook and would overwrite a prior write, so
partial-pipeline ordering remains explicit producer/closure debt. The
susceptibility ledger records update magnitude only; it is not a resource cost.
"Effective non-Markovian" is relative to LGRC state alone, not necessarily the
composed LGRC-plus-S state.

No candidate is ranked by raw effect magnitude or reduced to one generic decay
factor. Every added-mechanism lane records `native_upgrade_allowed = false`.
Thus a later producer-assisted `DR5` or `DR6` result can coexist with native
`DR2`, but cannot alter it. `N31-C6` remains return-bundle completeness rather
than mechanism `DR6` evidence.

## Iteration 9-A - Release-Efficacy Attenuation

- [x] Vary registered internal age/phase under matched carrier state.
- [x] Select packet amount only at creation.
- [x] Prove in-flight packet amount remains unchanged.
- [x] Prove source debit equals packet amount equals target credit.
- [x] Record unreleased coherence remaining at source.
- [x] Exclude route labels/global selection.
- [x] Make release phase load-bearing and receipt count validation-only.
- [x] Reject malformed phase/count pairs before amount selection.
- [x] Bind the efficacy table with a versioned release-policy identity.
- [x] Bind numeric topology roles without reading semantic edge payloads.
- [x] Restore all age/phase continuation state.
- [x] Compose native-v2, closure, policy, and topology identities.
- [x] Keep I9-A as trace evidence pending a formal I10 candidate row.
- [x] Classify expression attenuation versus field-state decay.

### Iteration 9-A Result

```text
status = passed
acceptance_state = accepted_source_current_producer_mediated_release_efficacy_attenuation_candidate_pending_I10
semantic_class = A
authority = producer_mediated
fresh_q_created = 0.20
aged_q_created = 0.10
aged_to_fresh_ratio = 0.50
packet_amount_stable_in_flight = true
source_debit_packet_receiver_credit_exact = true
q_unreleased_retained_at_release_source = true
unrelated_event_phase_control_status = failed_closed
lane_control_status_counts = passed:4 / failed_closed:1 / failed_open:0
native_and_closure_restoration_exact = true
duplicate_branch_replay_exact = true
composed_candidate_identity_recorded = true
receipt_count_validation_only = true
semantic_edge_payload_read = false
lane_specific_controls_resolved = 5 / 5
complete_controls_resolved = 16 / 57
current_decay_relation_ladder_rung = DR3
DR4_shape_observed = true
DR4_supported = false
DR4_blocker = independent_later_receiver_readout_pending
DR5_supported = false
native_decay_classification = D0a / DR2 unchanged
n31_closeout_progress_rung = N31-C4
output_digest = cdb2bd7f27bfba52e6b007b5a54d9c2bd04d20723bf3037162d94268c69a22c0
```

### Iteration 9-A Interpretation

I9-A is the first source-current added-mechanism result. It does not decay an
existing packet. It uses a serialized producer-owned release phase to choose
how much new packet coherence is expressed. Both branches start from the same
post-formation native LGRC snapshot: fresh evaluates before the exact formation
receipt is applied to the closure, while aged evaluates after that one receipt.
The native state and queue are therefore matched; the registered closure phase
bundle carries the only branch difference. Fresh is specifically a matched
closure-callback suppression intervention after formation, not evidence for
elapsed-time aging.

Fresh expression creates `0.20`; aged expression creates `0.10`. Once created,
both packets keep their amount through departure and arrival. The source loses
exactly the created amount and the receiver gains exactly that amount. In the
aged branch, the remaining `0.10` is ordinary node-1 coherence, not hidden or
destroyed state. A nonqualifying native event increments runtime event history
without changing the release phase, proving that a global event counter is not
the age carrier.

The phase-selected amount changes immediate receiver credit, but that credit is
the conserved destination of the created packet rather than an independent
later receiver operation. The row therefore supports producer-mediated `DR3`
expression attenuation and only a `DR4` shape. `DR4` remains blocked pending a
matched receiver-side native readout. It is not field-state decay, in-flight
attenuation, or native decay. Full `DR5` remains blocked because I10 must create
the formal recursive candidate row, add the independent readout, and regenerate
the unresolved controls; I9-A intentionally does not consume I3 null results
as evidence.

## Iteration 9-A.1 - Independent Downstream Readout

- [x] Consume the exact I9-A result, trace, composed identity, and final snapshots.
- [x] Keep the Candidate A attenuation producer unchanged.
- [x] Add no second decay producer.
- [x] Verify original release packets are complete before readout.
- [x] Keep Candidate A producer state unloaded during readout.
- [x] Preregister a five-point native receiver-departure sweep.
- [x] Record that the experiment authors the probe request.
- [x] Keep admission, debit, transport, and credit native to LGRC.
- [x] Prove the fresh/aged admission split at the middle thresholds.
- [x] Reverse the split with balanced receiver-C interventions.
- [x] Preserve the split under a common target-C intervention.
- [x] Exclude immediate receiver credit by executing a separate later operation.
- [x] Preserve node-plus-packet coherence and exact duplicate replay.
- [x] Prove state-neutral atomic refusal for every rejected native request.
- [x] Limit mediation to local receiver-C departure admission.
- [x] Qualify native binary-floating-point boundaries and retain `0.35` as the robust interior.
- [x] Normalize conformance controls to `passed` rather than `failed_closed`.
- [x] Preserve auxiliary controls outside the inherited 57-control count.
- [x] Record reviewed-to-current I9/I9-A revision lineage.
- [x] Keep the formal recursive candidate row and full controls pending I10.

### Why I9-A.1 Does Not Use A Different Producer

The I9-A demotion from provisional `DR4` to `DR3` was an evidence-boundary
correction, not a finding that Candidate A required a stronger producer. I9-A
proved that its registered phase changes `q_created`; it did not yet prove that
the changed receiver state affects a distinct later operation. A different
producer in I9-A.1 could author that later difference and would therefore
confound the causal chain.

I9-A.1 keeps the original producer fixed and absent during readout:

```text
Candidate A producer selects q_created
  -> native packet arrives and queue becomes empty
  -> no producer is loaded or called
  -> experiment requests the same later native operation
  -> LGRC natively admits or rejects that operation from receiver C
```

The request remains experiment-authored probe instrumentation. The result does
not establish autonomous native readout scheduling or autonomous native decay.

### Iteration 9-A.1 Result

```text
status = passed
acceptance_state = accepted_provisional_producer_mediated_DR4_independent_native_receiver_readout_pending_I10
relation_authority = producer_mediated
readout_authority = native_LGRC9V3_runtime
readout_request_authority = experiment_probe_harness
autonomous_native_readout_scheduling_supported = false
q_probe_values = [0.25, 0.30, 0.35, 0.40, 0.45]
fresh_admission_pattern = [true, true, true, true, false]
aged_admission_pattern = [true, true, false, false, false]
split_q = 0.35
native_eligibility_split = aged_C < q_probe <= fresh_C
endpoint_values_are_observed_binary_floats_not_theoretical_reals = true
nextafter_boundary_controls_pending_I10 = true
receiver_C_clamp_reverses_split = true
target_C_clamp_preserves_split = true
mediation_strength = bounded_partial_local_receiver_C
other_continuation_state_matched = false_with_declared_mass_compensator
receiver_C_mediates_departure_eligibility = true
full_complete_state_mediation = false
producer_active_during_readout = false
successful_native_readouts_conserve_budget = true
duplicate_replay_exact = true
all_rejected_readouts_atomic = true
cumulative_complete_controls_resolved = 18 / 57
auxiliary_controls_separately_enumerated = true
auxiliary_controls_disjoint_from_inherited_matrix = true
current_decay_relation_ladder_rung = DR4 provisional
DR5_supported = false
native_decay_classification = D0a / DR2 unchanged
n31_closeout_progress_rung = N31-C4
revision_lineage_output_digest = a9301bd8e3b98894ad648637d1c0412df98e078432c1fc3ef9bcbdc1cc555ee3
targeted_LGRC_runtime_conformance = 413 passed, 89 subtests passed
output_digest = 0a10639f3d6e9b42806655a2c90c4b9fdeb384c21d8b35622bcffd14d4149f91
```

### Iteration 9-A.1 Interpretation

The receiver-side readout is separate from I9-A's immediate credit. Both source
release packets have completed before the new operation is scheduled. The
experiment then asks receiver node 2 to emit a native packet back across edge 1.
Fresh and aged both admit `0.25` and `0.30`; only fresh admits `0.35` and `0.40`;
both reject `0.45`.

Balanced clamps identify the load-bearing state. Moving fresh receiver C from
`0.40` to `0.30` blocks the `0.35` operation, and moving aged receiver C from
`0.30` to `0.40` admits it. Equalizing the target node at `C=0.45` does not
remove the split. The later effect is therefore mediated by receiver C rather
than target state, a second producer, or route labels.

This is bounded local mediation, not complete-state mediation. The receiver-C
clamps preserve total coherence by changing compensator node 0, so
`other_continuation_state_matched` is explicitly
`false_with_declared_mass_compensator`. The load-bearing result is native
departure admission only; the complete post-arrival branch is not claimed.

Rejected native requests are atomically state-neutral relative to the queued
pre-step request state. Both restoration identities, the event queue, packet
ledger, scheduler/time, packet-record count, and budget remain unchanged, and
the receipt authority is explicitly an experiment audit of native refusal.
The `0.30` and `0.40` endpoints are observed binary-floating-point behavior;
the robust interior result is `q=0.35`, with exact `nextafter` controls retained
as I10 debt.

Original-packet exclusion, separate-readout status, and absence of a different
producer are conformance checks and therefore record `passed`, not
`failed_closed`. Five auxiliary I9-A.1 controls remain separately enumerated
and do not inflate the inherited matrix, which remains `18 / 57` resolved. The
revision-lineage artifact binds prior and current I9/I9-A identities and states
that the numerical outcome did not change while the evidence classification
was corrected.

This closes the missing provisional `DR4` gate for Candidate A. The result is
still producer-mediated expression attenuation: the relation comes from the
Candidate A closure, while its downstream readout is native. It is not native
decay, autonomous scheduling, field-state decay, or `DR5`. I10 retains the
formal candidate-row and complete replay/control obligations.

## Iteration 9-B - Conserved Leakage

- [x] Declare source, destination, amount, schedule, and internal clock.
- [x] Record B-R export-policy owner and all policy inputs.
- [x] Bound emitted amount by available source excess and source floor.
- [x] Debit source through admitted packet mechanics.
- [x] Record exact in-flight amount and destination credit.
- [x] Audit full node-plus-in-flight conservation.
- [x] Exclude hidden reservoir and destruction.
- [x] Distinguish new leakage policy from ordinary D0 outward flux.
- [x] Exclude the receiver from the later read path during the registered probe window.
- [x] Keep D0-R analogue status `not_tested` unless a separate bridge passes.
- [x] Test local encounter/readout.
- [x] Restore all lifecycle state.
- [x] Sweep the bounded export relation below, at, and above the source floor.
- [x] Consume zero-emission and positive one-shot receipts atomically.
- [x] Refuse repeated and restored second triggers without state mutation.
- [x] Reject unrelated native arrivals as export triggers.
- [x] Separate route-mass loss from route-organization weakening.
- [x] Reverse the later readout with balanced source-C clamps.
- [x] Preserve the later result under balanced destination-C clamps.
- [x] Prove atomic state-neutral refusal for rejected native readouts.
- [x] Keep mediation bounded to local departure admission.
- [x] Record preformation `O_B` and gate attributable formation delta separately from absolute formed organization.
- [x] Scope DR2 persistence to post-formation checkpoint/restoration evidence.
- [x] Fail closed composed receipt/event presence, amount, and destination mismatches.
- [x] Retain corrected I9 revision lineage in the source chain.
- [x] Keep the formal recursive candidate row and full controls pending I10.

### Iteration 9-B Result

```text
status = passed
acceptance_state = accepted_provisional_producer_mediated_B_R_DR4_conserved_leakage_pending_I10
candidate_id = B_conserved_source_leakage
semantic_subtype = B_R_conserved_export_policy
relation_authority = producer_mediated
transport_authority = native_LGRC9V3_packet_runtime
baseline_O_B = 0.04999999999999999
formed_O_B = 0.14999999999999997
formation_effect_O_B = 0.09999999999999998
minimum_attributable_formation_effect = 0.04
formation_effect_gate_passed = true
post_export_O_B = 0.10999999999999999
organization_weakening_delta = 0.03999999999999998
organization_weakening_fraction_of_formed_O_B = 0.2666666666666666
q_emit = 0.04
source_debit = 0.03999999999999998
route_mass_decrease = 0.039999999999999925
destination_credit = 0.04000000000000001
continuity_closed = true
route_mass_export_fraction = 0.06153846153846143
source_debit_fraction = 0.09999999999999996
readout_q = 0.37
no_export_readout_admitted = true
export_readout_admitted = false
minimum_readout_margin = 0.010000000000000009
minimum_readout_margin_fraction_of_probe = 0.027027027027027053
source_C_clamps_reverse_readout = true
destination_C_clamps_preserve_readout = true
mass_loss_substitution_rejected = true
all_rejected_readouts_atomic = true
duplicate_replay_exact = true
resolved_complete_controls = 16 / 60
current_decay_relation_ladder_rung = DR4 provisional
DR5_supported = false
D0_R_bridge_status = not_tested
native_decay_classification = D0a / DR2 unchanged
DR2_persistence_scope = post-formation checkpoint and restoration only
unrelated_native_continuation_persistence_claimed = false
composed_receipt_event_mismatches_fail_closed = true
n31_closeout_progress_rung = N31-C4
targeted_LGRC_runtime_conformance = verification-only; not retained as candidate evidence
output_digest = 4427aa0c5d5d1e864f304873edbe2190ec3e975c0702e4f1ef3ed4ac81adc9b3
```

### Iteration 9-B Geometric Interpretation

The fixture already has directional contrast `O_B=0.05` on route `[0, 1]`.
Formation moves coherence from node 0 into node 1 and strengthens that contrast
to `0.15`, for an attributable formation effect of `0.10`. Candidate B then
exports `0.04` from node 1
across boundary edge 1 into explicit destination node 2. The route is weakened
because node 1 falls while node 0 remains fixed, not merely because total route
mass is lower. The matched mass-loss control removes `0.02` from both route
nodes; route mass falls by the same `0.04`, but their contrast remains `0.15`
and the later readout still passes.

The separate readout asks node 1 to emit `0.37` toward node 3. Without export,
node 1 retains `0.40` and admits the operation. After export, it retains `0.36`
and refuses. Source-C clamps reverse this split; destination-C clamps do not.
The destination is therefore an accounting endpoint, not a hidden return path
or a global selector. The supported mediator is local departure eligibility,
not the full branch state.

The persistence claim is similarly bounded. Formation activity is exhausted,
the `O_B=0.15` checkpoint restores exactly under both identity schemas, and the
export begins from that restored state. No unrelated native continuation was
inserted between formation and export, so I9-B does not claim that stronger
persistence scope. Cross-state controls nevertheless reject a consumed receipt
without its export packet, an unconsumed receipt with an export packet, and
receipt/packet amount or destination mismatches.

The result is a producer-owned `B-R` relation. The producer reads the exact
local event receipt, current source C, frozen floor/cap, one-shot state, and
numeric topology bindings; it selects export amount, time, and destination.
Native LGRC conservatively executes the packet. That division is the evidence:
it shows a workable added mechanism and precisely identifies the native policy
surface still missing. It does not support ordinary `D0-R`, native decay,
coherence destruction, a global scheduler, or `DR5`.

The runtime conformance counts used during implementation are verification
notes, not retained candidate evidence. I10 must rerun and retain any test
receipt it intends to consume, and it must sweep readout requests at `0.35`,
`0.36`, `0.37`, `0.38`, `0.40`, and `0.41` around the narrow current split.

## Iteration 9-B.1 - Formation Attribution And Bounded Export Response Shape

- [x] Consume exact I9-B result, trace, preregistration, and producer implementation identities.
- [x] Reconstruct baseline `O_B=0.05`, formed `O_B=0.15`, and attributable effect `0.10`.
- [x] Preserve the `0.04` minimum attributable formation-effect gate.
- [x] Exhaust and restore formation before independent progression.
- [x] Process one disjoint native boundary-birth trial without topology admission.
- [x] Advance native scheduler/checkpoint state while preserving topology and `O_B`.
- [x] Record the trial as experiment-scheduled native progression, not autonomous persistence.
- [x] Record ordinary state-mutating native persistence as not tested.
- [x] Keep the exact Candidate B producer, topology, floor, and cap.
- [x] Produce `q_emit = 0`, `0.01`, `0.02`, and `0.04` under predeclared source states.
- [x] Keep route mass fixed across diagnostic pre-export source states.
- [x] Close organization, route-mass, debit, in-flight, and destination equations per row.
- [x] Retain at least three distinct positive export levels.
- [x] Scope B.1 to linear response through the cap boundary.
- [x] Cite inherited I9-B above-cap rows as plateau evidence rather than attributing the plateau to B.1.
- [x] Separate zero-export native identity, closure-receipt consumption, and packet creation.
- [x] Enforce response-row native-state diff whitelists and exact closure reset.
- [x] Probe no-export and export branches below, at, and above local source C.
- [x] Record `nextafter` boundary behavior without using it as a semantic relabel.
- [x] Prove paired admission-boundary shift equals `q_emit` at every level.
- [x] Prove rejected readout probes are atomic and state-neutral.
- [x] Consume I9-B source/destination/mass-substitution/mismatch controls without inflating the 60-control matrix.
- [x] Preserve bounded-partial local-source-C mediation.
- [x] Preserve provisional `B-R / DR4`; keep `DR5` and `DR6` false.
- [x] Keep `D0-R` untested and native D0a at `DR2`.
- [x] Retain the reviewed-to-corrected I9-B revision lineage receipt.
- [x] Preserve I9-B as the I10 core positive row and B.1 as complementary evidence.
- [x] Keep runtime and protected contracts unchanged.

### Iteration 9-B.1 Result

```text
status = passed
acceptance_state = accepted_I9B1_formation_attribution_persistence_and_bounded_export_response_shape_at_provisional_B_R_DR4
baseline_O_B = 0.04999999999999999
formed_O_B = 0.14999999999999997
formation_effect_O_B = 0.09999999999999998
independent_native_progression_persistence_supported = true
progression_authority = experiment_scheduled_native_runtime_trial
persistence_through_ordinary_state_mutating_activity = not_tested
topology_events_routed = 0
topology_unchanged = true
q_emit_levels = [0.0, 0.009999999999999981, 0.01999999999999999, 0.03999999999999998]
distinct_positive_q_level_count = 3
all_response_equations_close = true
all_diff_whitelists_pass = true
zero_export_native_identity_unchanged = true
zero_export_closure_receipt_consumed = true
zero_export_packet_created = false
B1_response_shape_scope = monotonic_linear_through_cap_boundary
I9B_inherited_above_cap_plateau_row_count = 2
all_robust_below_admitted = true
all_robust_above_rejected = true
all_rejected_rows_atomic = true
all_boundary_shifts_equal_q_emit = true
paired_boundary_shift_monotonic_non_decreasing = true
mediation_strength = bounded_partial_local_leakage_source_C
current_decay_relation_ladder_rung = DR4 provisional
DR5_supported = false
DR6_supported = false
D0_R_bridge_status = not_tested
native_decay_classification = D0a / DR2 unchanged
output_digest = 867337e1b5adf04356e5fb6172de3ca42f6c5e0619ce6f8d38e02766f5f4a15e
```

### Iteration 9-B.1 Interpretation

I9-B.1 strengthens three empirically thin parts of I9-B. Formation is now
reconstructed as a change from an existing contrast, not merely reported at its
final value. Persistence survives exact restoration and a disjoint native
runtime trial that advances scheduler/checkpoint state without changing route
coherence or topology. The trial is scheduled by the experiment and fails to
admit a boundary birth, so the result is not autonomous persistence. It is also
state-neutral; persistence through ordinary state-mutating native activity was
not tested.

The response matrix uses controlled source states with constant route mass.
Those states are diagnostic interventions, not additional naturally formed
relations. Under the unchanged policy, three positive export levels establish a
bounded response shape: organization and route mass each fall by `q_emit`, and
native debit, packet transport, and destination credit close to the same amount.
The B.1 result is linear through the cap boundary. The two inherited I9-B rows
with source excess above `0.04` supply the separate plateau evidence.

At zero export, native identity remains unchanged, the one-shot closure receipt
is consumed, and no packet is created. Every response row also passes the
preregistered state-diff whitelist and exact closure-reset rule.

For downstream effect, the meaningful monotonic quantity is not absolute
post-export C across different initial states. It is the paired shift from each
row's no-export native admission boundary to its export boundary. That shift is
exactly `0`, `0.01`, `0.02`, and `0.04`. Robust below-boundary probes admit,
robust above-boundary probes reject atomically, exact-boundary probes admit, and
the immediately adjacent `nextafter` probes split on the expected side.

This is serious response-shape and attribution evidence for Candidate B, but it
does not pre-empt I10. Candidate B remains producer-mediated `B-R / DR4`; full
controls, formal recursive admission, `DR5`, `DR6`, ordinary `D0-R`, autonomous
native export, and complete-route mediation remain unsupported or pending.
The I9-BR1 receipt preserves reviewed and corrected identities and confirms the
scientific DR4 conclusion is unchanged. I10 must retain I9-B as the core
positive execution and consume B.1 as complementary attribution and shape
evidence, not as a replacement row.

## Iteration 9-C - Susceptibility Relaxation

- [x] Consume exact I2 and corrected I9 Candidate C contract identities.
- [x] Reconstruct the frozen three-node, two-edge topology exactly.
- [x] Declare `S` as dimensionless route-local closure state with bounds `[0.5, 1.0]`.
- [x] Declare formation and relaxation laws separately before execution.
- [x] Trigger producer-owned `S` formation from an exact native route-use arrival receipt.
- [x] Exhaust formation traffic before progression and readout.
- [x] Serialize and restore native and closure state independently.
- [x] Run matched native progression in closure-active and closure-omitted branches.
- [x] Prove native v1/v2 identities and budgets match after progression.
- [x] Apply one bounded relaxation update per exact native arrival receipt.
- [x] Preserve wall-clock and global-event-count exclusion.
- [x] Match complete native state before formed/relaxed readout comparison.
- [x] Apply `g_effective = S * g_native` only at the frozen partial-pipeline phase.
- [x] Use native GRC9V3 kernels for potential/flux computation without calling the result an ordinary LGRC step.
- [x] Restore exact pre-application native v1/v2 identities and complete snapshot after every readout hook.
- [x] Audit formation, relaxation, and readout input paths against exact allowlists.
- [x] Classify the readout as diagnostic flux computation, not packet transport or a coherence transition.
- [x] Prove monotonic `S`, effective-conductance, and signed-flux response shape.
- [x] Keep mediation bounded to registered-edge conductance and record graph-level potential scope.
- [x] Resolve all five Candidate C lane-specific controls.
- [x] Keep the susceptibility-update magnitude ledger report-only and noncausal; do not relabel it a cost ledger.
- [x] Separate functional reflexive-geometry resemblance from strict ontological fidelity.
- [x] Preserve closure/producer/native distinctions and naturalization debt.
- [x] Preserve provisional producer-mediated `C-R / DR4` and leave DR5/DR6 pending.
- [x] Keep runtime and protected contracts unchanged.

### Iteration 9-C Result

```text
status = passed
acceptance_state = accepted_provisional_producer_mediated_C_R_DR4_route_susceptibility_relaxation_pending_I10
candidate_id = C_route_susceptibility_relaxation
semantic_subtype = C_R_route_susceptibility_relaxation
relation_authority = producer_mediated_effective_non_markovian_closure
readout_request_authority = experiment_harness
susceptibility_and_conductance_insertion_authority = candidate_C_closure
potential_flux_computation_authority = native_GRC9V3_kernels
ordinary_LGRC_step_consumes_S = false
readout_kind = native_potential_flux_diagnostic
state_mutating_native_transport_consequence_supported = false
initial_S = 0.5
formed_S = 0.9
relaxed_S = 0.6265625
S_weakening = 0.2734375
g_native = 0.6065306597126334
formed_g_effective = 0.5458775937413701
relaxed_g_effective = 0.3800293664761969
g_effective_weakening = 0.16584822726517323
formed_signed_flux = 0.1765143937092521
relaxed_signed_flux = 0.1480967673715728
signed_flux_change = 0.028417626337679303
matched_native_progression_identity_exact = true
lane_specific_controls_resolved = 5 / 5
current_decay_relation_ladder_rung = DR4 provisional
DR5_supported = false
DR6_supported = false
D0_R_bridge_status = not_tested
native_decay_classification = D0a / DR2 unchanged
strict_ontology_closest_added_mechanism = Candidate B
candidate_C_strict_ontology_disposition = effective closure or possible theory extension
candidate_C_functional_reflexive_geometry_resemblance = closest among added mechanisms
functional_resemblance_is_not_ontological_fidelity = true
output_digest = f9a7a96c26474277a5009ad2a5a56c7d5bfa000fe801bdbc5178c59e2c26f8ad
```

### Iteration 9-C Geometric Interpretation

The registered route-use packet transfers `0.4` coherence from node 1 to node
2 through edge 1. Native LGRC conserves this packet flow. Candidate C does
something separate: its exact arrival receipt raises the closure-owned
susceptibility multiplier on that same route from `0.5` to `0.9`. The route is
therefore more able to carry the later native conductance relation, but that
ability is stored outside native LGRC state.

Four subsequent packets move back and forth on edge 0. Both compared branches
execute the same packets and end with byte-identical native snapshots. In the
active branch, the closure consumes each arrival receipt and contracts `S`
toward its `0.5` floor. In the omitted branch, no closure call occurs and `S`
stays at `0.9`. The experiment therefore isolates susceptibility relaxation
from route-mass loss, topology change, native-event differences, or labels.

The later readout starts from one common native snapshot. The experiment harness
requests it, Candidate C inserts `S * g_native` on edge 1, and native GRC9V3
kernels compute graph-level potential and diagnostic flux. Formed `S` returns
signed flux `0.1765`; relaxed `S` returns `0.1481`. This is a changed registered
readout, not packet transport, a coherence transition, or ordinary native
continuation. Exact pre-hook native identities and snapshot are restored.

The result is strong Candidate C evidence because it contains source-current
formation, bounded persistence, exact event-driven weakening, and a separate
native-kernel diagnostic consequence. Its limit is equally important: ordinary LGRC
steps would recompute and overwrite the conductance unless the closure owns the
partial-pipeline order. No resource cost has been established, and independent
`S` remains outside RC coherence accounting. Candidate C is therefore provisional producer-mediated
`C-R / DR4`, not native D0 decay. I10 retains formal DR5 admission and full
control responsibility; reusable-contract DR6 remains later work.

Candidate C is closest to the functional image of reflexive geometry, but not
to the strict 2025-11 coherence-only ontology. Identical complete native `C`
with different independently restored `S` produces different diagnostics, so
`S` is an added causal degree of freedom. Strict ontological alignment is
`D0a > B > A > C`, with B the closest added mechanism; functional resemblance
is `C > D0a > B > A`. Naturalizing C would require `S` to be exactly derived
from `C/J_C` history with no independent freedom, or represented as a native
slow coherence mode.

## Iteration 9-C.1 - Exact-Derived Route Susceptibility

- [x] Preserve I9-C as the independent-state Candidate C result rather than replacing it.
- [x] Start `C_derived_history_susceptibility` at `DR0` with no inherited rung.
- [x] Freeze the exact history relation from I9-C's preregistered floor, ceiling, `alpha`, and `rho`.
- [x] Use only native-restored `packet_processing_log` receipts as history authority.
- [x] Prohibit stored `S`, hidden relaxation cursors, receipt counts, route age, and external receipt archives.
- [x] Prove formed and weakened `S` recompute exactly after native snapshot/load.
- [x] Prove deleting any optional derived cache does not change recomputation.
- [x] Prove a conflicting injected independent `S` has no readout authority.
- [x] Detect or predict receipt truncation, duplication, edge, lineage, amount, and causal-order tampering.
- [x] Prove storage-order shuffling and semantic labels are causally neutral.
- [x] Compare equal reduced current projections with different complete native states and histories.
- [x] Classify the relation as non-Markovian to the reduced projection but state-complete to the full native snapshot.
- [x] Record the packet log as retained causal-history state and an operational discrete `J_C` proxy.
- [x] Record the exact event matcher as fixture-bound and general route-history transfer as unsupported.
- [x] Separate invalid duplicate controls, valid semantic-history changes, and storage-only changes.
- [x] Causally consume derived `S` through the bounded wrapper-owned conductance insertion.
- [x] Use lower-substrate GRC9V3 kernels for potential and diagnostic flux.
- [x] Restore exact native state after every diagnostic readout.
- [x] Keep packet transport, coherence transition, and ordinary LGRC-step claims false.
- [x] Re-establish provisional `C-R / DR4` from `DR0` under new carrier semantics; leave `DR5/DR6` pending.
- [x] Record that source native trajectories are inherited from I9-C rather than freshly executed.
- [x] Keep native D0a at `DR2` and defer comparative A/B/C ranking to I11.
- [x] Keep runtime and protected contracts unchanged.

### Iteration 9-C.1 Result

```text
status = passed
acceptance_state = accepted_provisional_exact_derived_fixture_history_C_R_DR4_pending_I10
candidate_id = C_derived_history_susceptibility
source_candidate = C_route_susceptibility_relaxation
initial_rung = DR0
current_decay_relation_ladder_rung = DR4 provisional
semantic_class = exact_derived_fixture_history_susceptibility
authority_class = exact_derived_native_packet_history_closure
theory_correspondence = discrete_C_JC_history_proxy
insertion_class = producer_or_wrapper_mediated_constitutive_insertion
history_source = native_snapshot.dynamics.lgrc9v3_runtime.packet_processing_log
history_identity_included_in_restoration = true
external_history_archive_required = false
stored_S_state_present = false
independent_susceptibility_state_eliminated = true
causal_history_state_eliminated = false
history_carrier = native_packet_processing_log
slow_coherence_mode_realized = false
formed_derived_S = 0.9
relaxed_derived_S = 0.6265625
S_weakening = 0.2734375
g_effective_weakening = 0.16584822726517323
signed_flux_change = 0.028417626337679303
current_C_JC_geometry_projection_equal = true
complete_native_state_equal = false
different_native_history_state = true
non_markovian_relative_to_current_projection = true
markovian_relative_to_complete_native_snapshot = true
fixture_bound_exact_history_functional = true
general_route_history_functional_supported = false
transfer_to_equivalent_event_identifiers_tested = false
DR4_reestablished_under_new_carrier_semantics = true
independent_classification_from_DR0 = true
fresh_independent_runtime_execution = false
source_native_trajectory_inherited_from_I9C = true
DR5_supported = false
DR6_supported = false
I9C_independent_state_result_replaced = false
current_state_D0a_supported = false
native_D0a_unchanged = DR2
native_upgrade_allowed = false
checks_passed = 17 / 17
output_digest = 2853511bbb0e8604e69b5b1b805c6e49f22eb8b6b17d1630f669064adae3015e
```

### Iteration 9-C.1 Geometric Interpretation

C.1 retains the same geometric effect measured by I9-C but removes the
independently serialized susceptibility field. The formed native snapshot
contains one qualifying edge-1 route-use receipt and derives `S=0.9`. The
weakened snapshot contains the same formation receipt plus four ordered native
progression receipts and derives `S=0.6265625`. No separate susceptibility
value or external history ledger is needed to reproduce either state.

The two snapshots have equal reduced current coherence, geometry, conductance,
and flux projections, but they are not the same complete native state. Their
serialized packet histories and restoration identities differ. The relation is
therefore non-Markovian relative to the reduced current projection and
state-complete relative to the full native snapshot.

Independent `S` is gone, but causal memory has not disappeared: it resides in
the native `packet_processing_log`. The experiment treats packet amount, edge
orientation, and internal ordering as an operational discrete `J_C`-history
proxy. This is stronger theory alignment than independently free `S`, but it is
not a realized slow-coherence mode.

The exact matcher remains fixture-bound to I9-C node, event-time,
scheduler-index, and lineage fields. Equivalent identifiers, shifted clocks,
role-preserving renumbering, and irrelevant-event interspersion have not been
tested, so general route-history transfer is unsupported.

For the diagnostic consequence, the wrapper inserts the recomputed
`S * g_native` on the registered edge and lower-substrate GRC9V3 kernels
calculate potential and flux. The readout changes and exact native state is
restored, so the relation is causal rather than report-only. Ordinary LGRC
continuation still has no hook that consumes derived `S`; the constitutive
insertion remains producer/naturalization debt.

C.1 re-establishes provisional exact-derived-fixture-history `C-R / DR4` from
`DR0` under new carrier semantics. This is an independent classification, not
a fresh runtime replicate: the native trajectory comes from I9-C. It does not
support native D0a, `DR5`, or `DR6`, and it does not replace I9-C. I10 must
eventually keep independent-state C and fixture-bound exact-history C.1
separate, while I11 retains authority for comparative theory ranking.

## Iteration 9-C.2 - Generalized Exact-History Relation And LGRC-Faithful Step

- [x] Preserve I9-C and I9-C.1 as separate evidence rather than replacing either result.
- [x] Start `C_native_exact_history_constitutive_closure` from an existing-native-runtime ceiling of `DR0`.
- [x] Replace C.1's fixture matcher with a generalized physical-role relation over native packet-processing records.
- [x] Restrict physical inputs to committed amount, edge, orientation, registered route role, and causal record order.
- [x] Use event identity only to reject duplicate committed arrivals.
- [x] Prove packet/event ID, lineage, semantic-label, clock, scheduler-index, and role-preserving topology changes do not alter the relation.
- [x] Prove real history removal changes the relation and malformed duplicate identity fails closed.
- [x] Prove conflicting injected `S` has no authority.
- [x] Restore formed and progressed relations exactly through native `LGRC9V3.load()`.
- [x] Record relation/carrier evidence independently from producer and native-runtime evidence.
- [x] Follow the existing LGRC producer/executor pattern documented by the LGRC9V3 examples.
- [x] Derive history-conditioned geometry with native GRC9V3 kernels on a state copy.
- [x] Keep the producer from mutating live conductance, node coherence, packets, or packet history.
- [x] Schedule causal work through the public LGRC packet API.
- [x] Let `LGRC9V3.step()` alone execute packet debit and arrival.
- [x] Prove exact source debit, receiver credit, and node-plus-in-flight coherence conservation.
- [x] Prove different admitted histories produce different packet amounts.
- [x] Prove completed native transport enters the history and changes the later derived relation.
- [x] Keep ordinary LGRC derivation/constitutive consumption false.
- [x] Keep existing native support, native D0a, autonomous decay, `DR5`, and `DR6` false.
- [x] Record deferred conditional naturalization requirements without selecting, implementing, or admitting the native extension.
- [x] Keep I10 unopened and runtime/protected contracts unchanged.

### Iteration 9-C.2 Result

```text
status = passed
acceptance_state = accepted generalized relation/restoration DR2 plus LGRC-faithful producer-step provisional DR4 pending I10 with native-runtime DR0 and deferred conditional naturalization requirements recorded
candidate_id = C_native_exact_history_constitutive_closure
source_candidate = C_derived_history_susceptibility
relation_carrier_lane_rung = DR2
producer_extension_lane_rung = provisional_DR4_pending_I10
producer_extension_lane_ceiling = DR4
native_runtime_lane_rung = DR0
highest_observed_evidence_ceiling = DR4
highest_observed_evidence_status = provisional_pending_I10
formed_derived_S = 0.9
progressed_derived_S = 0.6265625
weakening_direction_observed = true
formed_history_packet_amount = 0.04412859842731302
progressed_history_packet_amount = 0.0370241918428932
formed_history_post_step_S = 0.9441285984273131
progressed_history_post_step_S = 0.6635866918428932
maximum_conservation_error = 2.220446049250313e-16
LGRC_faithful_producer_step_executed = true
native_runtime_extension_executed = false
existing_native_support = false
native_candidate_extension_supported = false
native_D0a_unchanged = DR2
weakening_class = activity_indexed_local_susceptibility_relaxation
quiescence_decay = false
wall_clock_decay = false
route_use_reinforcement = true
other_incident_activity_relaxation = true
RCAE_admission_status = blocked_until_DR5_and_reusable_provider_contract
I9C_replaced = false
I9C1_replaced = false
I10_opened = false
checks_passed = 20 / 20
output_digest = 93d2c5341d0398e27991e6f6ca4d364e795e009ed502d223c1b8197f875402fe
```

### Iteration 9-C.2 Geometric Interpretation

C.2 generalizes the carrier question before asking for a native runtime
extension. A committed packet arrival on the registered oriented route forms a
susceptibility contribution. Later committed arrivals on other physical edges
incident to the route source increase causal distance and attenuate that
contribution. The relation therefore weakens from `S=0.9` to `S=0.6265625`
without consuming fixture IDs, semantic labels, absolute time, or scheduler
indices. Native restoration preserves both values exactly.

The custom step is LGRC-faithful but experiment-owned. It reads native history,
uses native GRC9V3 geometry kernels on a copy, and schedules a packet through
the public API. It does not write live geometry or coherence. Native
`LGRC9V3.step()` performs the debit and arrival, preserves total
node-plus-in-flight coherence, and writes the resulting native history. The
formed and progressed histories schedule different packet amounts, and each
completed packet changes the relation derived from the next history. This is a
real producer/executor feedback composition, not a report-only readout.

That result supports provisional producer-mediated `DR4`, but it does not make
the mechanism built-in. Ordinary LGRC neither derives `S` nor inserts it into
constitutive geometry, so the existing native-runtime lane remains `DR0`.
The generalized relation itself reaches `DR2` from formation and exact native
restoration. These lane assignments must remain separate.

The scientific consequence is more precise than either “DR0 only” or “native
DR4”: N31 has an executable LGRC-compatible producer pattern and a generalized
restorable carrier. Native admission is optional future work only if C.2 is
later selected for naturalization. C.2 does not replace C/C.1, upgrade native
D0a, or open I10; I10 is the next N31 iteration.

### Iteration 9-C.2 Consumption Constraints

The operational carrier is native discrete coherence-current history, not yet
an unqualified continuous `J_C` trajectory. `S=1` means unattenuated native
conductance and `S=0.5` means the candidate-mode floor. Formation recovers from
that floor; relaxation returns toward it. The candidate never demonstrates
conductance above native geometry.

The weakening is activity-indexed. It does not proceed under quiescence or wall
time. Route-use arrivals reinforce the relation, while other committed incident
activity advances attenuation. Later consumers must not relabel this as passive
or autonomous temporal decay.

The producer's `DR4` is provisional pending I10. It proves one chain:

```text
history -> S -> geometry -> flux -> packet
packet -> native history -> second S
```

It does not prove direct mediation clamps, a second geometry/transport cycle,
long-run stability, or native ownership. The producer uses a preregistered but
not yet naturalized `0.25` transport multiplier. It remains experiment policy
until it has a dimensioned integration/packetization meaning and zero,
negative, insufficient-source, source-bound, and units controls.

### C.1 Revision Receipt

C.2 consumes corrected C.1 digest
`2853511bbb0e8604e69b5b1b805c6e49f22eb8b6b17d1630f669064adae3015e`.
The earlier reviewed artifact identified by prefix `33e77c892977` is not retained
and is not consumed. Its corrections tightened current projection versus
complete state, retained causal memory, fixture scope, discrete-current proxy
wording, classification versus execution, and control semantics. The C.1
provisional ceiling remained unchanged.

### I10+ Mechanism-Family Comparison Admission Policy

```text
A-family:
  evidence_bundle = [I9-A, I9-A.1]
  independent_comparison_weight = 1

B-family:
  evidence_bundle = [I9-B, I9-B.1]
  independent_comparison_weight = 1

C-family:
  canonical_comparison_candidate = C_native_exact_history_constitutive_closure
  evidence_bundle = [I9-C.2]
  ancestor_evidence = [I9-C, I9-C.1]
  ancestor_positive_weight = 0
  independent_comparison_weight = 1
```

- [x] Make C.2 the sole comparison-, ranking-, and selection-eligible C-family representative.
- [x] Retain C/C.1 only for lineage, ablation, theory-boundary, and naturalization-debt interpretation.
- [x] Prohibit separate scores, votes, ranks, or accumulated positive weight for C/C.1.
- [x] Consume A/A.1 as one A-family evidence bundle rather than two candidates.
- [x] Consume B/B.1 as one B-family evidence bundle rather than two candidates.
- [x] Require comparison axis before rung consumption.
- [x] Use C.2 `DR2` only for carrier/restoration comparison.
- [x] Consume C.2 provisional producer `DR4` as the pre-I10 input and use producer `DR5` only after I10 final-state replay/control admission.
- [x] Use C.2 native-runtime `DR0` for native implementation comparison.
- [x] Prohibit maximum-label inheritance across ancestry or bundle members.
- [x] Keep producer viability from inflating native support.
- [x] Keep native `DR0` from erasing producer/executor viability.

## Iteration 10 - Added-Mechanism Replay And Controls

- [x] Consume every executed A/B/C row as explicit bundle evidence without making every row an independent comparison candidate.
- [x] Emit one comparison record per mechanism family rather than per sub-iteration.
- [x] Record A/A.1 and B/B.1 as strengthening bundles with independent weight `1` each.
- [x] Record C.2 as the sole C-family representative with independent weight `1`.
- [x] Record C/C.1 ancestry with positive weight `0` and ranking/selection eligibility false.
- [x] Record `comparison_axis` and lane-specific rung for every cross-family comparison.
- [x] Run artifact, snapshot/load, duplicate, and branch replay.
- [x] Run candidate-specific invariant controls.
- [x] For Candidate C, run duplicate-receipt, wrong-lineage, wrong-edge, nonqualifying-event, and restored-receipt-set controls.
- [x] Consume I9-C and I9-C.1 as separate carrier/authority rows; do not let C.1 retroactively naturalize C.
- [x] For Candidate C.1, preserve native-history identity, exact recomputation, injected-state rejection, history-tamper, and constitutive-insertion controls.
- [x] Consume I9-C.2 as three separate lane records; do not relabel its producer-extension `DR5` as native-runtime support.
- [x] Preserve C.2 generalized-relation invariance, native restoration, producer/executor authority, conservation, feedback, and no-`src` controls.
- [x] Retain C.2 post-transport native snapshots and verify exact v1/v2 restoration, post-feedback `S` rederivation, and the next candidate-step result.
- [x] Separate runtime-executed controls, inherited I3 schema nulls, positive conformance observations, and scope-not-applicable rows.
- [x] Keep inherited schema nulls and C/C.1 representation-boundary controls non-contributory to the C.2 rung.
- [x] Separate A/B candidate-native runtime admission from the ambient native D0a context rung.
- [x] Emit a claim-level replay-mode map for I11.
- [x] Carry admitted D0a/D0b/D0c rows into I11 alongside the three added-mechanism units.
- [x] Require multi-axis/Pareto comparison in I11; prohibit a single scalar ranking.
- [x] Run local-encounter and global-selector controls.
- [x] Run hidden-state and producer/native controls.
- [x] Run topology-specific controls.
- [x] Use v2 for reset-sensitive equivalence.
- [x] Demote or reject failed-open rows.
- [x] Emit replay/control JSON and report.

### Iteration 10 Result

```text
status = passed
acceptance_state = accepted_added_mechanism_family_replay_controls_with_lane_specific_DR5_and_no_native_upgrade
source_artifact_manifest_references_replayed = 66
all_source_identities_exact = true
all_manifest_hashes_exact = true
A_replay_modes = artifact + snapshot/load + duplicate + branch passed
B_replay_modes = artifact + snapshot/load + duplicate + branch passed
C_replay_modes = artifact + source/final snapshot-load + duplicate + branch + post-feedback continuation passed
C2_post_feedback_restoration_witness = passed
control_registry_rows_resolved = 70
family_control_resolution_rows = 210
runtime_controls_executed = 14
inherited_schema_nulls_consumed = 76
positive_conformance_observations = 30
scope_not_applicable_rows = 90
failed_open_count = 0
frozen_I10_registry_not_run_count = 0
deferred_conditional_C2_controls_in_I10_registry = false
A_added_mechanism_rung = DR5
B_added_mechanism_rung = DR5
A_candidate_native_runtime_lane = not_admitted
B_candidate_native_runtime_lane = not_admitted
existing_native_D0a_context_rung = DR2
C2_relation_carrier_rung = DR2
C2_producer_extension_rung = DR5
C2_native_runtime_rung = DR0
native_D0a_rung = DR2 unchanged
DR6_supported = false
n31_closeout_progress_rung = N31-C4
n31_closeout_ladder_rung_assigned = false
ready_for_iteration_11_comparative_classification = true
added_mechanism_comparison_unit_count = 3
admitted_Dx_comparison_row_count = 3
total_I11_comparison_row_count = 6
single_scalar_I11_ranking_allowed = false
RCAE_automatic_adoption_allowed = false
src_diff_empty = true
output_digest = 29314dc62908e445deeb868ad04719dc1c23bd856562ac159098f5a3b081e257
```

I10 is the first full added-mechanism family replay matrix. It reruns actual
family behavior rather than merely aggregating I9 reports. A reproduces both
the fresh/aged expression split and the later native readout split. B
reconstructs the unconsumed one-shot closure from the exact formation receipt,
reproduces export and readout behavior, and separately proves that the
committed receipt cannot schedule a second export. C.2 rederives its relation
from native packet history, replays producer/native-step transport, and retains
the final post-arrival native state. Both duplicate branches have equal complete
restoration identities, rederive the same post-feedback `S`, and produce the
same next candidate-step result after load. This final-state witness, rather
than source-state roundtrip alone, is what admits the C.2 producer lane at
`DR5`.

The `70` control count names the frozen registry, not `70` runtime executions.
Each of the `210` family-resolution rows identifies its resolution mode and
receipt. An inherited `failed_closed` result points to the exact I3
schema-validator fixture and means that the false-positive claim was rejected;
it is not a family runtime failure and does not raise a rung. Positive
conformance observations and the `14` actually executed runtime controls are
reported separately. Deferred conditional C.2 naturalization controls are not
members of the frozen I10 registry.

The result is lane-specific. A and B reach producer-mediated `DR5`; they do not
become native D0. C.2 reaches producer-extension `DR5`, while its exact-history
carrier remains `DR2` and the current native runtime remains `DR0`. Its
producer result therefore cannot be used as native implementation evidence.
Conversely, native `DR0` does not erase the viable producer/executor result.

C and C.1 remain separate explanatory records for independent-state and
fixture-exact-history authority. Each has comparison weight `0`; neither can
add a score, vote, rank, or control-count contribution to C.2. A/A.1 and B/B.1
are likewise consumed once per family. A and B do not own a native `DR2` lane;
that rung belongs to the ambient D0a context. I10 admits three added-mechanism
units and the admitted D0a/D0b/D0c rows for I11. I11 must compare all six rows
as multi-axis profiles or a Pareto set, not collapse them into one scalar score.

The deferred C.2 naturalization list is not an unfinished I10 control set.
Packetization, native constitutive integration, multi-cycle stability,
topology lifecycle, cache policy, and native readmission remain conditional
future implementation requirements if C.2 is selected later.

Artifacts:

```text
outputs/n31_i10_added_mechanism_replay_control_artifacts/
outputs/n31_i10_added_mechanism_replay_control_trace.json
outputs/n31_added_mechanism_replay_controls_i10.json
reports/n31_added_mechanism_replay_controls_i10.md
```

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

## Deferred C.2 Naturalization Requirements (Outside N31)

This is not an unfinished N31 iteration and does not block I10, I11, or I12.
It is a conditional implementation record for use only if a later decision
selects C.2 for LGRC naturalization. C.2's current N31 evidence is complete at
relation `DR2`, replay/control-backed producer-mediated `DR5`, and native
runtime `DR0`.

- [ ] Test packetization invariance: one `0.10` versus two `0.05` progression packets under matched integrated coherence and physical interval.
- [ ] Run a feature-enabled, no-history floor control at `S=0.5`.
- [ ] Run common-`S` clamp and derived-`S` bypass controls.
- [ ] Prove same `S` with different histories gives the same packet amount.
- [ ] Prove the same history with recomputed `S` gives the same packet amount.
- [ ] Naturalize the transport interval and close its units.
- [ ] Test zero flux, negative flux, insufficient source, atomic refusal/clipping, and source bounds.
- [ ] Execute at least two complete feedback cycles.
- [ ] Test saturation/oscillation, double counting, cascade bounds, and long-run conserved nonnegative coherence.
- [ ] Freeze edge deletion/recreation, orientation reversal, replacement, source-change, and topology-version policy.
- [ ] Prove full-history recomputation equals any incremental cache.
- [ ] Prove cache removal is neutral, injection has no authority, and mismatch fails closed.
- [ ] Define exact history-pruning or approximation semantics.
- [ ] Re-earn native `DR1` through `DR4` without inheriting producer `DR5`.
- [ ] Prove feature-disabled byte identity and provider mismatch refusal.
- [ ] Keep RCAE admission blocked until `DR5` and a reusable provider contract.

Native ownership may use either an integrated step or a library-owned canonical
producer plus `LGRC9V3.step()`. The gate is library ownership, specification,
canonical invocation, provider restoration identity, default-off behavior,
derived-only authority, and conservative execution, not literal placement of
all code inside `step()`.
