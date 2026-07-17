# N31 Iteration 9-B - Conserved Leakage

## Result

```text
status = passed
acceptance_state = accepted_provisional_producer_mediated_B_R_DR4_conserved_leakage_pending_I10
candidate = B conserved source leakage
semantic subtype = B-R conserved export policy
relation authority = producer-mediated
transport authority = native LGRC9V3 packet runtime
current rung = DR4
D0-R bridge = not tested
DR5_supported = false
native lane = D0a / DR2 unchanged
```

## Geometric Dynamics

Before formation, the route already has a positive source contrast:

```text
O_B_baseline = 0.35 - 0.30 = 0.05
```

The formation packet moves `0.05` coherence from node 0 into node 1. It
strengthens, rather than creates, the route-local source contrast:

```text
O_B_formed = C_leakage_source - C_formation_source = 0.40 - 0.25 = 0.15
formation_effect_O_B = 0.15 - 0.05 = 0.10
```

The attributable effect exceeds the preregistered minimum effect of `0.04`.
The absolute formed-organization floor remains descriptive and is not used by
itself as proof that formation caused the contrast.

The registered one-shot export policy then schedules `0.04` from node 1 to the
explicit destination node 2. Native LGRC packet mechanics debit node 1, carry
the packet in flight, and credit node 2. The route contrast becomes `0.11`, so
the weakening delta is `0.04`; route mass also falls by exactly `0.04`, and the
same amount appears at the destination. No coherence is destroyed or hidden.

The matched mass-loss control removes the same `0.04` route mass symmetrically
from nodes 0 and 1. It leaves `O_B=0.15` and preserves the later readout. Thus
route-mass decrease alone is not substituted for organization weakening.

## Later Readout And Isolation

The later readout is a separate native departure request from node 1 to node 3
at `q=0.37`. The no-export branch (`C_1=0.40`) admits it; the
export branch (`C_1=0.36`) rejects it. Balanced source-C clamps reverse this
result. Balanced destination-C clamps leave the export result rejected.
Destination node 2 is outside path `[0, 1, 3]`, emits no return packet, and is
not read by either the export policy or the native departure-admission gate.

This is bounded partial mediation of departure admission by local leakage-source
coherence, not complete-state mediation of the full post-arrival branch.

## Persistence And Reconstruction Scope

I9-B supports persistence after formation activity stops at the exact
post-formation checkpoint and through v1/v2 restoration. It does not claim that
the formed relation survived an unrelated native continuation before export;
that stronger continuation scope was not run. The composed-state controls admit
the matched closure receipt/native packet pair and fail closed when consumed
state, packet presence, amount, or destination disagree.

## Classification

I9-B supports provisional producer-mediated `B-R / DR4`: a registered local
event triggers a bounded, conserved export; the preregistered route contrast
weakens; and its local leakage-source component changes a distinct later native
departure-admission operation. The producer owns export eligibility, amount,
time, and destination, while native
LGRC owns debit, transport, and credit. Therefore the result is not ordinary
`D0-R`, native decay, a global scheduler, or coherence destruction. `DR5`
remains pending the formal candidate row and complete I10 replay/control matrix.
I10 also retains the preregistered readout-threshold sweep around the narrow
`q=0.37` split.

## Checks

| Check | Passed |
|---|---:|
| `exact_I2_I9_and_contract_sources_consumed` | true |
| `candidate_B_contract_consumed` | true |
| `canonical_four_node_topology_reconstructed` | true |
| `qualifying_local_event_exact` | true |
| `formation_stops_and_relation_restores_before_export` | true |
| `absolute_formed_route_organization_supported` | true |
| `formation_effect_threshold_bound_to_I9_contract` | true |
| `route_organization_attributably_strengthened_from_baseline` | true |
| `positive_bounded_export_emitted` | true |
| `route_organization_weakened` | true |
| `route_boundary_continuity_and_full_conservation_close` | true |
| `policy_sweep_matches_bounded_relation` | true |
| `one_shot_receipt_consumption_and_restoration_pass` | true |
| `unrelated_event_does_not_trigger_export` | true |
| `later_native_readout_depends_on_exported_source_state` | true |
| `destination_isolated_from_later_readout` | true |
| `route_mass_loss_not_substituted_for_organization_weakening` | true |
| `rejected_readouts_atomic` | true |
| `duplicate_export_and_readout_replay_exact` | true |
| `composed_receipt_event_mismatches_fail_closed` | true |
| `producer_ownership_and_input_audit_explicit` | true |
| `ownership_facts_derived_from_calls_and_packet_lineage` | true |
| `source_current_input_allowlist_exact` | true |
| `B_R_not_promoted_to_D0_R` | true |
| `selected_candidate_controls_pass_without_failed_open` | true |
| `formal_recursive_candidate_row_pending_I10` | true |
| `artifact_manifest_exact` | true |
| `provisional_B_R_DR4_only_pending_I10` | true |
| `native_lane_and_D0_R_not_upgraded` | true |
| `unsafe_claim_flags_false` | true |
| `src_diff_empty` | true |
| `protected_runtime_contract_diff_empty` | true |
| `no_absolute_paths_in_records` | true |
