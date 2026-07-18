# N31 Iteration 4 - D0a Representation Gate

Status: `passed`

Acceptance state: `accepted_scoped_spatial_D0a_exact_projection_representation_gate_no_positive_decay_evidence`

Output digest: `b7b6f34e3978ec4a410a77e36bc1b548f1baf96dbda7987803d544fc737c3597`

## I3 Revision Lineage

I4 consumes the committed I3 artifact as revision `N31-I3R1`. The previously
reviewed I3 package and the committed artifact have different file and output
digests because the committed artifact added validator-derived receipts,
bad/repaired-fixture evidence, and future resolver/transition schemas. The
lineage record verifies that the 70 control identities, their scientific
semantics, the no-positive-evidence status, and the DR0 ceiling are unchanged.

```text
revision lineage = experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_i3_revision_lineage_r1.json
revision lineage digest = b6f6c1948f723d5fbb6008348b804b778993718da18c4b7efb3a499a8757de64
consumed I3 revision = N31-I3R1
```

## Result

I4 admits one bounded D0a representation lane:

```text
global D0a representation status = represented_by_exact_projection
admitted scope = registered-route spatial C distribution and internal oriented flux
separate boundary-transfer channel = instantaneous oriented boundary flux
positive decay evidence = not opened
DR ceiling = DR0
```

The status is deliberately scoped. It means LGRC9V3 current scientific state
can be factored into a route-mass channel, a spatial-organization coordinate
channel, a separate boundary-transfer channel, and an exact matched
continuation-state context. It does
not mean every proposed organization domain is represented, and it does not
show persistence, weakening, or a later readout effect.

## Exact Projection

The conformance fixture uses public LGRC9V3 operations, processes one internal
packet departure, and leaves that packet in flight. The projection starts from
`lgrc9v3_restoration_identity_v1`, not from a hand-picked report row. It removes
the registered route's node-coherence and internal signed-flux coordinates,
separates boundary signed flux from organization, retains all other scientific
state in an exact context channel, then reconstructs the identity. The machine
contract records ordered route nodes, the anchor, coordinate maps and
orientations, and every excluded/reinserted restoration-identity path.

Identity v1 is intentional here because I4 projects only current scientific
state and never invokes reset. The fixture also records identity v2 provenance;
any later reset-sensitive row must use v2.

```text
projection contract = n31_i4_registered_route_coordinate_projection_v1
identity roundtrip exact = true
observed reconstruction error = 0.0
reconstruction bound = 1e-12
projection persisted as runtime state = false
projection fed into runtime = false
```

This is an exact derived projection, not a new slow variable. Its authority is
recomputation from current native state. The representation may therefore be
used to define a later I7 intervention, but it cannot mediate a later readout
until a source-current causal probe demonstrates that role.

## Mass Is Not Organization

The paired conformance contrast keeps registered route mass at
`2.5` and keeps node `1`
at `0.75`, while changing the complete
route C distribution through public `LGRC9V3.set_state()`. Internal flux,
boundary transfer, and the exact non-organization context are unchanged.

That proves the representation can distinguish:

```text
one node scalar
route mass
route organization
```

It does not prove the fourth distinction, causal mediation. `set_state()` is
admitted here only as a surgical matched-state clamp. Coherence bounds, total
node coherence, packet-ledger budget, and queue context remain valid, but
constitutive dependent fields were not recomputed. The clamp therefore cannot
serve as native formation or autonomous weakening evidence. A later causal row
must use a native trajectory or explicitly recompute dependent fields and keep
the claim limited to the declared clamp.

## Route Measurement Boundary

The fixture exactly enumerates support nodes `[0, 1, 2]`,
internal edges `[0, 1]`, and boundary edges
`[2]`. The current signed outward boundary-flux rate
is `0.03125`.

This is an instantaneous native edge-flux measurement. I4 does not integrate a
post-formation window and therefore does not claim exported route mass or
closed boundary continuity.

For I7, the route-mass window must count an internal departure and its in-flight
packet once, integrate a boundary crossing once, avoid counting outside arrival
as another export, and count re-entry as signed inward transfer. Support or
boundary changes require an explicit reclassification term.

## Complete-State Crosswalk

| Theory state group | Status | Runtime/contract source | Update owner |
|---|---|---|---|
| registered_route_support_and_boundary | `represented_by_exact_projection` | GRC9V3State.topology plus experiment-registered support/orientation | native_topology; experiment_contract_selects_route |
| node_coherence_distribution | `represented_by_exact_projection` | LGRC9V3RuntimeState.base_state.nodes[*].coherence | native_GRC9V3_and_LGRC9V3_packet_transport |
| route_mass | `represented_by_exact_projection` | registered node C plus route-owned in-flight packet amounts | native_node_and_packet_ledger_state |
| signed_route_and_boundary_flux | `represented_by_exact_projection` | GRC9V3State.port_edges[*].flux_uv | native_GRC9V3_edge_state |
| edge_geometry_and_functional_coupling | `represented_natively` | base_conductance, geometric_length, temporal_delay, flux_coupling | native_GRC9V3_state_and_frozen_constitutive_policy |
| packet_identity_and_in_flight_state | `represented_natively` | LGRC9V3RuntimeState.packet_ledger | native_LGRC9V3_packet_transport |
| event_ordering_and_local_time | `represented_natively` | event_queue, event_time_key, node_proper_time, edge_causal_delay | native_LGRC9V3_scheduler_and_local_update |
| constitutive_and_causal_policies | `represented_natively` | restoration identity parameter identity and causal_modes | frozen_model_configuration |
| other_scientific_continuation_state | `represented_natively` | lgrc9v3_restoration_identity_v1 context channel | native_GRC9V3_LGRC9V3_runtime |
| later_local_readout_and_causal_mediation | `missing` | not_created_by_representation_projection | pending_source_current_I7_probe |

## Organization Domains

| Domain | Representation | Authority | Standalone carrier | I7 role | Remaining condition |
|---|---|---|---:|---|---|
| `spatial_distribution` | `represented_by_exact_projection` | `exact_derived_projection` | `true` | selected_load_bearing_carrier_candidate | persistence_weakening_and_mediation_still_unmeasured |
| `induced_geometry` | `represented_by_exact_projection` | `exact_derived_projection` | `false` | derived_response_component_of_selected_spatial_lane | local_transport_intervention_required_for_causal_D0a |
| `functional_coupling` | `represented_natively` | `native_state` | `false` | native_response_context_of_selected_spatial_lane | no_weakening_law_or_load_bearing_use_established_by_I4 |
| `temporal_alignment` | `missing` | `missing` | `false` | blocked_as_load_bearing_carrier | no_native_coincidence_resonance_or_alignment_mediator |
| `arrival_time_distribution` | `missing` | `missing_for_D0a` | `false` | D0b_observable_only_not_D0a_carrier | no_native_persistent_load_bearing_distribution_state |
| `mixed` | `missing` | `unresolved` | `false` | blocked_until_load_bearing_domain_resolved | must_resolve_one_load_bearing_domain |
| `other` | `missing` | `missing` | `false` | blocked_without_new_representation_contract | new_source_backed_representation_contract_required |

Native event times, proper times, and delays remain exact inputs, but they do
not constitute a native temporal-alignment mediator. An arrival-time
distribution can be reconstructed as a D0b history observable; it is not a
persistent D0a state. Induced geometry and functional coupling are admitted
only as response components of the selected spatial C/J_C lane, not as
standalone carrier claims. Mixed rows remain blocked until one load-bearing
domain is isolated.

Induced geometry remains a response component only. It cannot become a
load-bearing D0a carrier without its own source-current geometry state or exact
projection, preregistered weakening order, local-transport intervention,
matched mass/transfer controls, later-readout dependence, and clamp/ablation
effect.

## Spectral Boundary

A truncated slow-mode spectrum is lossy and is not admitted. A full graph
spectrum is not used as a shortcut because N31 has not frozen a canonical
degeneracy policy or a source-current spectral intervention contract. The
admitted representation instead uses a canonical finite route-coordinate
basis with an exact identity roundtrip.

## Closeout Position

The I3 active-null component and I4 representation component now establish the
current `N31-C2` progress rung and ceiling. The terminal closeout rung remains
unassigned until final N31 closeout. No positive candidate row exists, so no DR
rung is assigned.

I5 may run the D0c instantaneous comparator. I7 has representation admission,
but execution remains blocked until a candidate-specific observable, stronger
and weaker orientation, threshold, tolerance, trajectory rule, monotonicity
rule, and sign-ambiguity resolution are frozen before outcomes. Exact
representability alone does not define weakening.

## Checks

- `I2_source_chain_exact` = `true`
- `I3_source_chain_exact` = `true`
- `I3R1_revision_lineage_closed` = `true`
- `complete_D0a_state_crosswalk_present` = `true`
- `route_mass_organization_mediation_separate` = `true`
- `support_boundary_and_instantaneous_flux_exact` = `true`
- `exact_projection_roundtrip_passed` = `true`
- `machine_projection_mapping_complete` = `true`
- `exact_projection_schema_complete` = `true`
- `projection_has_no_independent_causal_state` = `true`
- `all_organization_domains_dispositioned` = `true`
- `blocked_domains_not_admitted` = `true`
- `one_standalone_D0a_carrier_lane_admitted` = `true`
- `one_global_D0a_status_assigned` = `true`
- `spectral_shortcut_not_used` = `true`
- `timing_annotations_not_promoted` = `true`
- `no_persistent_slow_state_invented` = `true`
- `no_positive_decay_evidence_opened` = `true`
- `set_state_clamp_bounded_to_representation_role` = `true`
- `src_diff_empty` = `true`
- `protected_runtime_contract_diff_empty` = `true`
- `no_absolute_paths_in_records` = `true`
