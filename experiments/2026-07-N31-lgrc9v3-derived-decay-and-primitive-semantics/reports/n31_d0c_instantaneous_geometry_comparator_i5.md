# N31 Iteration 5 - D0c Instantaneous Geometry Comparator

Status: `passed`

Acceptance state: `accepted_source_current_D0c_DR1_instantaneous_geometry_comparator_no_persistence_no_decay`

Output digest: `95d1a1f2c3003a7eeaa1edeaf9a0e843ac92e2c4af010e04a045233b445ac88b`

## I4 Revision Lineage

I5 consumes the committed I4 artifact as `N31-I4R1`. The pre-hardening reviewed
package had a different artifact/output identity. The generated lineage retains
both identities and records that I4R1 added provenance, machine projection,
channel-separation, surgical-clamp, and I7-preregistration detail without
changing the scoped exact-representation result, DR0 ceiling, evidence
quarantine, or I5 admission.

```text
I4R1 lineage = experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_i4_revision_lineage_r1.json
I4R1 lineage digest = 6dbd1441b5fcdce666d8eeca287cd59205cc4d34495016a0aefe3da9b818eb16
```

## Result

I5 supports one source-current `D0c` comparator at `DR1`:

```text
forming packet-current L1 = 0.30000000000000004
first post-withdrawal packet-current L1 = 0.0
registered route mass, forming = 3.0
registered route mass, post = 3.0
persistence supported = false
weakening supported = false
causal mediation supported = false
```

This is positive evidence for an instantaneous state/flux geometry relation,
not positive evidence for decay.

## State-Flux Dynamics

The registered route is a three-node cycle. Three equal native LGRC packets
depart simultaneously, one on each oriented internal edge. During transit,
the node-coherence distribution is shifted uniformly, so its anchor-relative
coordinates remain unchanged, while the oriented packet-current cycle is
nonzero. Route mass remains constant because each internal departure is counted
as one in-flight packet amount.

The current signs are stored in two explicit conventions:

```text
registered cycle orientation = {'0': 0.1, '1': 0.1, '2': 0.1}
canonical native edge orientation = {'0': 0.1, '1': 0.1, '2': -0.1}
node divergence (outflow - inflow) = {'0': 0.0, '1': 0.0, '2': 0.0}
```

Edge `2` is positive in the registered `2 -> 0` cycle direction and negative in
the canonical restoration-identity `0 -> 2` edge direction. Both vectors encode
the same physical transport. The zero node divergence verifies that the cycle
is balanced.

The next three native events are the corresponding arrivals. They restore the
original node-coherence distribution, empty the in-flight ledger and event
queue, and make the exact packet-current projection zero. No `set_state()`,
post-formation producer, static edge-flux cancellation, or hidden label is used.

```text
baseline C coordinates = {'0': 0.3999999999999999, '1': 0.19999999999999996}
forming C coordinates = {'0': 0.3999999999999998, '1': 0.19999999999999996}
post C coordinates = {'0': 0.3999999999999999, '1': 0.19999999999999996}
```

This isolates the instantaneous `J_C` component from route mass and the
spatial `C` coordinates. It is an instantaneous state-flux geometry comparator,
not an induced metric, curvature, Hessian, or geometric transport intervention.
It demonstrates that current-indexed transport geometry can be formed and
removed by native packet transport. Because the selected component
is already zero at the first post-arrival checkpoint, it does not demonstrate a
durable aftereffect or a relation that persists and later weakens.

## Withdrawal Meaning

Two lifecycle boundaries are retained. Formation input stops after the final
predeclared departure is processed. The three packets then remain the active
forming carrier from event time `0` to `1`; this is not a post-formation
persistence window. Carrier exhaustion occurs only after all three arrivals
commit and the queue becomes empty. Historical arrived-packet records remain in
the scientific state, but the exact projection counts only currently in-flight
packets. Those records therefore cannot backfill current or persistence.

## Authority And Residue

The D0c observable is an exact recomputable projection of current LGRC9V3
state. It has no independent causal freedom and is not fed back into transport.
The experiment owns the initial packet schedule, which remains producer residue
for formation. No producer acts after formation. Autonomous native production
of the cycle, persistence, weakening, and mediation remain debt.

## Controls

- `label_only_decay` = `passed` (`regenerated_candidate_specific`): native_packet_current_trace_and_full_identities_present
- `forming_activity_never_stopped` = `passed` (`regenerated_candidate_specific`): all_packets_arrived_queue_empty_no_post_calls
- `instantaneous_geometry_as_durable_decay` = `failed_closed` (`regenerated_candidate_specific`): first_post_checkpoint_current_component_equals_zero
- `route_mass_loss_as_organization_weakening_relabel` = `passed` (`regenerated_candidate_specific`): forming_and_post_route_mass_equal
- `D0c_persistence_retained_as_same_D0c_row` = `not_applicable` (`regenerated_candidate_specific`): no_persistence_observed
- `post_withdrawal_history_as_current_candidate_specific` = `failed_closed` (`candidate_specific_no_I3_source_control`): history_present_but_projected_current_is_zero

`failed_closed` means the attempted stronger relabel was rejected. In
particular, `instantaneous_geometry_as_durable_decay` fails closed and caps the
row at DR1. Every frozen-I3 control meaning used here is regenerated against
the exact I5 contract (`D0c`, exact-derived authority, functional-coupling
domain, packet-current carrier). None of the generic I3 fixtures is directly
consumed as if it already matched this candidate.

## Classification

```text
primary semantic class = D0c
authority = exact_derived_projection
candidate disposition = supported
DR rung = DR1
N31 progress ceiling = N31-C2
N31-C3 D0c component = satisfied
N31-C3 overall = pending I6/I7 classifications
```

## Checks

- `I2_source_chain_exact` = `true`
- `I3R1_source_chain_exact` = `true`
- `I4_handoff_exact_and_I5_ready` = `true`
- `I4R1_revision_lineage_closed` = `true`
- `runtime_trace_passed` = `true`
- `candidate_schema_complete` = `true`
- `source_current_D0c_relation_formed` = `true`
- `instantaneous_component_absent_after_withdrawal` = `true`
- `mass_and_budget_invariants_pass` = `true`
- `no_post_formation_producer_authorship` = `true`
- `instantaneous_as_durable_control_failed_closed` = `true`
- `candidate_specific_controls_regenerated` = `true`
- `current_orientation_and_divergence_contract_passed` = `true`
- `formation_input_and_carrier_exhaustion_separate` = `true`
- `artifact_manifest_exact` = `true`
- `positive_decay_claims_remain_closed` = `true`
- `protected_runtime_contract_diff_empty` = `true`
- `no_absolute_paths_in_records` = `true`
