# N31 Derived Decay And Primitive Semantics Implementation Checklist

## Current Status

```text
branch = experiment-N31
status = initialized
positive_evidence_opened = false
decay_semantics_selected = false
native_runtime_change_authorized = false
decay_relation_ladder_rung = DR0
n31_closeout_ladder_rung = N31-C0
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
- [ ] Commit the initialized N31 package.

## Iteration 1 - Source Inventory And Authority Admission

- [ ] Record exact graph revision and clean source state.
- [ ] Verify RCAE demand revision `ae11be2008b1902df1749faec531420432056c37`.
- [ ] Digest all required RCAE demand records.
- [ ] Verify theory revision `e0d25bf69b8bf681eb8d092ba416497030e5d88e`.
- [ ] Verify all seven theory/substrate source digests.
- [ ] Read theory/substrate sources directly rather than consuming RCAE summaries as evidence.
- [ ] Inventory LGRC9V3 state, packet, queue, proper-time, event-time, conductance, and surface APIs.
- [ ] Inventory route-support, boundary-flux, organization-observable, and local-readout APIs separately.
- [ ] Classify lapse, proper-time relation, edge-delay, queue, and arrival-distribution runtime surfaces.
- [ ] Distinguish executable timing behavior from paper-defined or missing timing policy.
- [ ] Inventory restoration identity v1/v2 and reset-baseline correction.
- [ ] Inventory load-bearing runtime tests.
- [ ] Inventory N08 source artifacts and native-memory blocker.
- [ ] Inventory N22 source artifacts, producer carrier, and naturalization debt.
- [ ] Inventory N30 closeout and source-current participant/medium rows.
- [ ] Record N30+ roadmap/handoff as planning boundary only.
- [ ] Give every source `may_consume_as` and `must_not_consume_as` fields.
- [ ] Record paper/specification-to-runtime capability dispositions.
- [ ] Record current missing surfaces without treating absence as negative theory evidence.
- [ ] Keep DR and N31-C positive rungs unassigned.
- [ ] Keep `positive_evidence_opened = false`.
- [ ] Emit source inventory JSON and report.
- [ ] Verify deterministic rerun and artifact hashes.

Expected ceiling:

```text
N31-C1_source_and_authority_inventory_only
```

## Iteration 2 - Semantic, Representation, And Control Schema Freeze

- [ ] Freeze primary semantic classes as exactly D0a/D0b/D0c/A/B/C.
- [ ] Freeze representation/authority classes separately from semantic classes.
- [ ] Freeze candidate dispositions separately from semantic and authority classes.
- [ ] Enforce one primary semantic class per candidate row.
- [ ] Freeze DR0-DR6 ladder and rung gates.
- [ ] Freeze N31-C0 through N31-C6 ladder.
- [ ] Freeze D0a representation status enum.
- [ ] Freeze exact-projection contract fields.
- [ ] Freeze lossy/missing representation blocker.
- [ ] Freeze `n31_decay_candidate_schema_v2` and schema change-record identity.
- [ ] Freeze D0-R as a D0 subtype and B-R as a Candidate B subtype.
- [ ] Freeze route-mass contract, outward-positive sign policy, and continuity residual.
- [ ] Freeze route-organization contract and observable-authority enum.
- [ ] Freeze organization-domain enum across spatial, geometric, functional, temporal, and mixed relations.
- [ ] Define organization domain as mediator domain, separate from observed diagnostic domains.
- [ ] Require mixed-domain rows to isolate one load-bearing domain or remain unresolved.
- [ ] Freeze weakening-trajectory enum including relaxation, drift, recurrence, broadening, and transience.
- [ ] Freeze causal-mediation contract and full/partial/unresolved statuses.
- [ ] Freeze `organization_mediated_readout_change = true` for intervention-backed full or bounded-partial mediation only.
- [ ] Freeze full versus qualified-partial D0-R interpretation ceilings.
- [ ] Freeze independent-later-probe and forming-packet-exclusion statuses.
- [ ] Freeze temporal-intervention matching and added coincidence/resonance policy fields.
- [ ] Freeze weakening-mode and D0-subclass enums.
- [ ] Freeze independent mass, organization, readout, and mediation fact fields.
- [ ] Freeze D0-R/B-R policy-owner facts and bridge-status enum.
- [ ] Require future validators to reject missing or superseded contract schemas.
- [ ] Require deterministic migration or regeneration of any future stale fixtures.
- [ ] Freeze candidate row schema and required artifact manifest.
- [ ] Freeze internal-time owner/advance-event schema.
- [ ] Freeze coherence and non-coherence invariant schemas.
- [ ] Freeze candidate-specific topology contract.
- [ ] Freeze local causal-readout contract.
- [ ] Freeze D0 producer allowance and prohibition.
- [ ] Freeze post-formation producer-call policy and call-level audit fields.
- [ ] Freeze producer-call audit status as complete-no-mutation, reclassified, or blocking-incomplete.
- [ ] Require empty state-mutating producer calls for D0.
- [ ] Reclassify export-authoring producer calls mechanically as B-R.
- [ ] Block native-autonomy calls whose timing gates the aftereffect or supplies export details.
- [ ] Freeze A packet-creation versus in-flight boundary.
- [ ] Freeze B destination and conservation boundary.
- [ ] Freeze C independent-state/closure boundary.
- [ ] Freeze v1 versus v2 restoration use.
- [ ] Freeze external state composition requirements.
- [ ] Freeze cache recomputation separately from execution reconstruction.
- [ ] Freeze control result status enum and demotion precedence.
- [ ] Freeze exact protected runtime/contract paths and diff-empty requirements.
- [ ] Keep specification, runtime, test, example, and dependency changes in a revision-distinct tranche.
- [ ] Freeze RCAE return manifest schema.
- [ ] Assign no positive DR rung.
- [ ] Emit schema/control JSON and report.

## Iteration 3 - Active Nulls And Failure Baselines

- [ ] Instantiate `label_only_decay`.
- [ ] Instantiate `wall_clock_decay`.
- [ ] Instantiate `post_hoc_weakening_trace`.
- [ ] Instantiate `forming_activity_never_stopped`.
- [ ] Instantiate `relation_persists_but_does_not_weaken`.
- [ ] Instantiate `relation_weakens_but_has_no_later_readout_effect`.
- [ ] Instantiate `global_route_selector`.
- [ ] Instantiate `hidden_producer_update`.
- [ ] Instantiate unrecorded post-formation producer call.
- [ ] Instantiate export-authoring producer call retained as D0-R.
- [ ] Instantiate `missing_internal_time_owner`.
- [ ] Instantiate `missing_invariant`.
- [ ] Instantiate `missing_restoration_state`.
- [ ] Instantiate `report_digest_as_runtime_state`.
- [ ] Instantiate `native_relabel_from_producer`.
- [ ] Instantiate `RCAE_demand_as_graph_evidence`.
- [ ] Instantiate `trail_or_stigmergy_relabel`.
- [ ] Instantiate D0-specific false-positive controls.
- [ ] Instantiate route-mass loss as organization-weakening relabel.
- [ ] Instantiate organization weakening without causal mediation.
- [ ] Instantiate constant-mass internal reorganization as export relabel.
- [ ] Instantiate unclosed route-boundary continuity.
- [ ] Instantiate added export policy as ordinary D0-R relabel.
- [ ] Instantiate mass-unmatched organization intervention.
- [ ] Instantiate `proper_time_annotation_as_causal_alignment`.
- [ ] Instantiate `added_coincidence_window_as_native_temporal_organization`.
- [ ] Instantiate `arrival_histogram_as_causal_mediation`.
- [ ] Instantiate `fixed_delay_single_path_as_dispersion`.
- [ ] Instantiate `periodic_rephasing_as_monotonic_decay`.
- [ ] Instantiate `diagnostic_domain_as_mediator_domain`.
- [ ] Instantiate `mixed_domain_without_load_bearing_isolation`.
- [ ] Instantiate `forming_packet_continuation_as_later_independent_readout`.
- [ ] Instantiate `temporal_intervention_with_unmatched_state`.
- [ ] Instantiate `geometric_observable_without_local_transport_intervention`.
- [ ] Instantiate A/B/C-specific invariant and relabel controls.
- [ ] Require all active nulls to fail closed.
- [ ] Record `failed_open_rows = 0` before positive admission.
- [ ] Assign no positive DR rung from active-null fixtures.
- [ ] Record active nulls as derived fixtures, not scientific evidence.
- [ ] Emit active-null JSON and report with clear `failed_closed` semantics.

## Iteration 4 - D0a Representation Gate

- [ ] Enumerate complete D0a state needed by the theory claim.
- [ ] Compare it field-by-field with source-current LGRC9V3 state.
- [ ] Separate node scalar coherence from complete spatial/flux organization.
- [ ] Separate route mass from route organization and later causal mediation.
- [ ] Determine whether route support, boundary, and net flux are exactly measurable.
- [ ] Determine organization-observable authority and update owner.
- [ ] Determine representability separately for each admitted organization domain.
- [ ] Do not infer native resonance or eligibility from timing annotations alone.
- [ ] Determine whether organization intervention can hold route mass and other state equal.
- [ ] Determine whether graph topology and edge/packet state form an exact discrete representation.
- [ ] Determine whether a spectral decomposition is exact, lossy, or missing.
- [ ] Freeze projection basis and operators if exact projection is claimed.
- [ ] Freeze overlap/orthogonality and temporal support.
- [ ] Freeze intervention semantics and reconstruction error bound.
- [ ] Prove projection has no independent causal state.
- [ ] Assign exactly one D0a representation status.
- [ ] Block positive D0a if status is lossy or missing.
- [ ] Do not invent persistent slow-state variables.
- [ ] Record theory support separately from runtime representation support.
- [ ] Emit representation-gate JSON and report.

## Iteration 5 - D0c Instantaneous Geometry Comparator

- [ ] Declare source-current fixture and route-local geometry relation.
- [ ] Declare thresholds before execution.
- [ ] Record complete forming-current state.
- [ ] Record instantaneous C/J_C-derived geometry/readout.
- [ ] Stop forming activity explicitly.
- [ ] Record immediate post-withdrawal state/readout.
- [ ] Verify whether effect disappears with current.
- [ ] Preserve conservation and local encounter.
- [ ] Reject durable-aftereffect relabel when persistence is absent.
- [ ] Record maximum D0c/DR ceiling honestly.
- [ ] Emit source-current artifacts, JSON, and report.

## Iteration 6 - D0b Finite-Window Derived Relation

- [ ] Define exact history support and window semantics.
- [ ] Build relation from admitted source-current packet/flux history.
- [ ] Prove cache recomputation from exact history.
- [ ] Stop forming activity.
- [ ] Show old history leaving the window under internal progression.
- [ ] Record weakening of the derived relation.
- [ ] Remove/recompute cache and compare identity.
- [ ] Verify cache has no independent causal freedom.
- [ ] Disconnect observable from transport and compare later readout.
- [ ] Restore and replay source history and cache.
- [ ] Keep fading observable below DR4 absent causal mediation.
- [ ] Emit source-current artifacts, JSON, and report.

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
