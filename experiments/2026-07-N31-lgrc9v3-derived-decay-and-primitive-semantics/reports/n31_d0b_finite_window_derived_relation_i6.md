# N31 Iteration 6 - D0b Finite-Window Derived Relation

Status: `passed`

Acceptance state: `accepted_source_current_D0b_DR3_finite_window_observable_below_causal_trail`

Output digest: `206088cbe96bb37e119aa88a543f728170d206ad3ce15e9da24f1b9a5f77313a`

## Result

I6 supports one source-current `D0b` finite-window coupling observable at
`DR3`:

```text
relation at forming-carrier exhaustion = 0.30000000000000004
post-formation progression values = [0.30000000000000004, 0.2, 0.1, 0.0]
persistence supported = true
weakening supported = true
window expiry supported = true
positive-to-positive decreases = 2
total strict decreases = 3
final expiry steps = 1
causal mediation supported = false
```

This is positive evidence for a fading derived graph observable. It is not
positive evidence for a causal trail or causal decay relation.

## Geometric And Runtime Meaning

Three equal native packets cross one registered internal route edge and arrive
at event times `1.0`, `1.5`, and `2.0`. The relation is the RC-Distance
finite-window coupling:

```text
F_01(T; DeltaT) = sum |packet amount|
                  for completed route transfers in (T - DeltaT, T]
DeltaT = 4.0 native event-time units
```

The packet event-measure convention is explicit: each completed transfer is an
atomic amount at its native arrival event. Native arrival is selected because
it is the single completion event for the registered-edge transfer. Departure
and arrival are not double-counted. This is the declared operational bridge to
the continuous-flux expression; it is not claimed as the unique possible
discretization. At carrier exhaustion all three transfers are
inside the window, so `F_01 = 0.3`. A disjoint packet lane then advances native
LGRC event time without touching the route support. The first progression
checkpoint retains all three transfers. Later checkpoints exclude them one by
one, producing `[0.30000000000000004, 0.2, 0.1, 0.0]` and finally
zero.

An equality-boundary fixture evaluates the retained native history at evaluation
times `2.0`, `5.0`, `5.5`, and `6.0`. It confirms that an arrival at the right endpoint
is included and arrivals exactly at `T - DeltaT` are excluded.

The route mass span is `0.0` and the closed-system
budget span is `0.0`. The changing quantity
is recent-transfer organization, not destroyed coherence or route-mass loss.

## Authority And Cache

The finite-window relation is an exact functional over native packet history
and native event time. It is not persisted in LGRC runtime state. At every
checkpoint an experiment-local cache is removed and recomputed exactly; doing
so leaves restoration identity unchanged. Snapshot/load restores both source
history and the recomputed relation exactly.

The progression lane is producer residue: its packet schedule is predeclared
before any runtime event and exists only to provide bounded native event-time
progression. It is disjoint from the route and contributes no route transfer.
No schedule call or state-mutating producer call occurs after route formation.
The clock scope is `global_model_event_time`: route-local proper time is not
advanced or tested. Unrelated model activity can therefore age this observable,
and I6 does not support a route-local-clock decay claim.

## Frozen Contract Conformance

I6 recursively instantiates and validates the complete frozen I2 contracts:

```text
route-mass required fields = 20
route-organization required fields = 15
causal-mediation required fields = 18
missing nested fields = {}
```

Route mass, recent-transfer organization, and causal mediation remain separate
objects. A complete schema does not upgrade the absent mediation result.

## I5 Revision Lineage

I6 consumes `N31-I5R1`, not the earlier reviewed I5 package. The lineage record
pins both identities, records the orientation/carrier/control hardening, and
shows that the scientific `D0c/DR1` result and no-decay ceiling did not change:

```text
lineage = experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_i5_revision_lineage_r1.json
lineage digest = 1bb729f219fbb4e0e5f52615e4213567e4f46b195b7bc00a27376c283203e9c8
```

## Causal Boundary

Two equal restored branches start from the first persistence checkpoint. One
computes the finite-window observable and one does not. They then process the
same native progression events and finish with equal receipts and equal
restoration identities. This proves only that computing or omitting the pure
report observable has no runtime side effect. It does not intervene on native
packet history or clamp the relation while holding other state matched.

No valid organization or local-transport intervention was run, and the later
independent-probe relation remains unresolved. I6 consequently reaches `DR3`
as an observable but fails closed at `DR4`. Using this value as a transport
input would require authority reclassification as a closure or added causal
mechanism.

## Controls

- `label_only_decay` = `passed` (`regenerated_candidate_specific`): native_packet_history_and_runtime_receipts_present
- `wall_clock_decay` = `passed` (`regenerated_candidate_specific`): window_evaluation_uses_LGRC9V3_event_time_key
- `post_hoc_weakening_trace` = `passed` (`regenerated_candidate_specific`): fixed_window_and_staggered_arrivals_recorded_in_threshold_contract
- `forming_activity_never_stopped` = `passed` (`regenerated_candidate_specific`): all_route_packets_arrived_at_event_time_2_and_no_later_route_packets_exist
- `relation_persists_but_does_not_weaken` = `passed` (`regenerated_candidate_specific`): [0.30000000000000004, 0.2, 0.1, 0.0]
- `missing_internal_time_owner` = `passed` (`regenerated_candidate_specific`): LGRC9V3_event_queue_progression_receipts_present
- `missing_invariant` = `passed` (`regenerated_candidate_specific`): budget_span=0.0
- `missing_restoration_state` = `passed` (`regenerated_candidate_specific`): all_checkpoint_snapshot_load_audits_exact
- `report_digest_as_runtime_state` = `passed` (`regenerated_candidate_specific`): report_cache_absent_from_runtime_identity
- `derived_observable_as_causal_trail` = `failed_closed` (`regenerated_candidate_specific`): computed_and_uncomputed_observer branches continue identically; no history intervention run
- `cache_removed_and_recomputed` = `failed_closed` (`regenerated_candidate_specific`): all checkpoint caches recompute exactly
- `cache_divergence` = `passed` (`regenerated_candidate_specific`): no cache divergence observed
- `observable_disconnected_from_transport` = `failed_closed` (`regenerated_candidate_specific`): after_identity_equal=True; organization_intervention_performed=false
- `route_mass_loss_as_organization_weakening_relabel` = `passed` (`regenerated_candidate_specific`): route_mass_span=0.0
- `D0b_transport_feedback_without_authority_reclassification` = `passed` (`regenerated_candidate_specific`): fed_back_into_transport=false

All I3 control meanings are resolved against the exact I6 semantic contract.
No generic I3 fixture is directly consumed as source-current evidence.

## Classification

```text
primary semantic class = D0b
authority = exact_derived_projection
candidate disposition = supported
DR rung = DR3
causal trail = blocked
causal decay = blocked
N31 progress ceiling = N31-C2
N31-C3 D0c component = satisfied
N31-C3 D0b component = satisfied
N31-C3 overall = pending I7 D0a classification
```

## Checks

- `I2_source_chain_exact` = `true`
- `I3R1_source_chain_exact` = `true`
- `I4R1_source_chain_exact` = `true`
- `I5R1_source_chain_exact_and_I6_ready` = `true`
- `runtime_trace_passed` = `true`
- `candidate_schema_complete` = `true`
- `I2_nested_contracts_recursively_complete` = `true`
- `I2_nested_contract_values_conform` = `true`
- `source_current_D0b_relation_persists_and_weakens` = `true`
- `cache_removal_recomputation_exact` = `true`
- `restoration_and_branch_disconnection_pass` = `true`
- `observer_side_effect_control_not_mislabeled_as_mediator_intervention` = `true`
- `global_clock_scope_and_local_clock_ceiling_explicit` = `true`
- `packet_event_measure_and_window_boundaries_explicit` = `true`
- `causal_trail_and_DR4_relabels_fail_closed` = `true`
- `candidate_specific_controls_regenerated` = `true`
- `mass_and_budget_invariants_pass` = `true`
- `artifact_manifest_exact` = `true`
- `positive_causal_decay_claims_remain_closed` = `true`
- `protected_runtime_contract_diff_empty` = `true`
- `no_absolute_paths_in_records` = `true`
