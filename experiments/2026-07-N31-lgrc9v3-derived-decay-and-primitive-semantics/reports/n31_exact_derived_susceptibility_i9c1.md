# N31 Iteration 9-C.1 - Exact-Derived Route Susceptibility

## Result

```text
status = passed
acceptance_state = accepted_provisional_exact_derived_fixture_history_C_R_DR4_pending_I10
candidate = C_derived_history_susceptibility
current rung = provisional exact-derived-fixture-history C-R / DR4
DR5_supported = false
DR6_supported = false
native lane = D0a / DR2 unchanged
```

## Independent-State Elimination

C.1 does not serialize `S`. It reads the native packet-processing history from
each restored LGRC snapshot and recomputes:

```text
S = S_floor + alpha * q_use * rho ** N_after_formation
```

The post-formation snapshot gives `S=0.9`. The snapshot
containing four qualifying progression receipts gives
`S=0.6265625`. Removing any temporary cache and recomputing
returns the same values. A conflicting injected `S=0.9` is ignored; only the
native-restored history has authority.

No external receipt archive is consumed. The source is the serialized native
`packet_processing_log`, and tampering that history changes both restoration
identities. An invalid duplicate fails closed. Receipt deletion,
edge/lineage/amount changes, or moving a receipt before formation are valid
semantic-history changes that predictably change the result. Mere storage order
or topology-label changes do not.

## Projection And Complete-State Boundary

The formed and relaxed snapshots have the same current coherence, geometry,
conductance, and flux projection, but they are not the same complete native
state: their serialized packet histories and restoration identities differ.
They therefore derive different `S`. C.1 is non-Markovian only relative to the
reduced current projection and state-complete relative to the full native
snapshot. It eliminates independent susceptibility state, but retains native
causal-history state and does not become current-state D0a.

The packet log is an operational discrete `J_C`-history proxy: receipt amount
represents transferred coherence, edge and orientation represent current
support and direction, and event time/order represent causal ordering. This
correspondence is not yet a general `C/J_C` functional.

## Causal Diagnostic Readout

The experiment wrapper inserts the recomputed `S * g_native`; lower-substrate
GRC9V3 kernels compute potential and diagnostic flux. The derived relation changes
effective conductance by `0.16584822726517323` and signed flux by
`0.028417626337679303`. No packet transport or coherence transition is
executed by the readout, and exact native state is restored afterwards.

## Classification

C.1 re-establishes provisional `DR4` from `DR0` under new carrier semantics:
formation, persistence, weakening, exact recomputation, history/restoration
controls, and causal diagnostic consumption all pass. It is not a fresh runtime
replicate because it consumes I9-C's native trajectory. The functional is
fixture-bound: it recognizes exact node, time, scheduler, and lineage fields,
while transfer across equivalent identifiers and role-preserving renumbering is
untested. It is therefore an exact-derived native-packet-history closure and a
discrete `C/J_C`-history proxy, not yet a general route-history law.

C.1 is closer to the strict theory than independent-state Candidate C because
`S` has no independent freedom, but causal memory remains in the native packet
log and wrapper-mediated constitutive insertion remains non-native. It does not
retroactively replace I9-C. Comparative A/B/C ranking remains for I11; DR5
remains for I10.

## Checks

| Check | Passed |
|---|---:|
| `exact_sources_consumed` | true |
| `I9C_script_and_native_snapshots_exact` | true |
| `independent_S_absent_and_external_history_not_required` | true |
| `native_history_roundtrip_and_derived_recomputation_exact` | true |
| `derived_relation_reproduces_formed_and_relaxed_trajectory` | true |
| `same_current_projection_different_complete_native_state_classified` | true |
| `conflicting_injected_S_has_no_authority` | true |
| `history_integrity_semantic_change_and_storage_neutrality_partitioned` | true |
| `native_restoration_identity_binds_history` | true |
| `derived_relation_changes_registered_lower_GRC9V3_kernel_readout` | true |
| `readout_cleanup_exact_and_transport_not_claimed` | true |
| `candidate_C1_controls_resolved_without_preempting_I10` | true |
| `C1_reestablishes_DR4_under_new_carrier_without_native_upgrade` | true |
| `protected_runtime_contracts_unchanged` | true |
| `artifact_manifest_exact` | true |
| `no_absolute_paths_in_records` | true |
| `unsafe_claim_flags_false` | true |
