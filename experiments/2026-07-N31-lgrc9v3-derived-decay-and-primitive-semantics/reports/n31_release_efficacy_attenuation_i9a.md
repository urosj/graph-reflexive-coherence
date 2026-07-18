# N31 Iteration 9-A - Release-Efficacy Attenuation

## Result

```text
status = passed
acceptance_state = accepted_source_current_producer_mediated_release_efficacy_attenuation_candidate_pending_I10
semantic_class = A
authority = producer_mediated
current_rung = DR3 expression attenuation
DR4_shape_observed = true
DR4_supported = false
DR5_supported = false
native_lane = D0a / DR2 unchanged
```

I9-A runs two packet-creation branches from the exact same post-formation LGRC
snapshot. The fresh branch evaluates the registered producer before applying
the exact formation-arrival receipt. The aged branch applies that receipt once.
Native state, queue, requested amount, release-source coherence, topology, and
receiver are matched at release; only the serialized closure phase bundle
differs.
The fresh branch is therefore a matched closure-callback suppression
intervention after native formation, not an elapsed-time branch in which the
qualifying receipt naturally failed to occur.

## Geometric And Causal Result

```text
fresh q_created = 0.2
aged q_created = 0.1
aged/fresh ratio = 0.5
```

The producer changes how much new coherence is expressed into the native packet
carrier. Once created, each packet keeps the same amount through departure and
arrival. Source debit, in-flight amount, and receiver credit match exactly, and
the unexpressed amount remains ordinary release-source coherence rather than a
new reservoir. An unrelated native event increases runtime event count but does
not age the release phase.

This is a causal expression result. The receiver-credit difference is the
immediate conserved destination of the selected packet amount, however, not an
independent later receiver operation. It records a `DR4`-shaped consequence but
does not satisfy `DR4`. A matched receiver-side native readout remains required.
The result is not field-state decay or in-flight attenuation. The registered
phase and amount policy remain producer state and therefore cannot upgrade
native D0a beyond DR2.

## Classification

I9-A supports a producer-mediated `DR3` expression-attenuation candidate.
`DR4` remains blocked by the missing independent later receiver readout. `DR5`
also remains blocked until I10 instantiates the formal recursive candidate row
and resolves the complete 57-control matrix. This iteration is explicitly a
source-current trace-evidence artifact, not that final formal row.

## Checks

| Check | Passed |
|---|---:|
| `exact_I2_I9_and_candidate_contract_sources_consumed` | true |
| `candidate_A_admission_contract_consumed_exactly` | true |
| `canonical_executable_topology_matches_I9` | true |
| `exact_formation_arrival_ages_phase_once` | true |
| `unrelated_event_does_not_age_release_phase` | true |
| `fresh_and_aged_native_state_matched_before_release` | true |
| `fresh_and_aged_closure_difference_is_registered_phase_bundle_only` | true |
| `release_efficacy_relation_matches_preregistration` | true |
| `packet_amount_selected_only_at_creation_and_stable_in_flight` | true |
| `source_debit_packet_amount_and_receiver_credit_exact` | true |
| `q_unreleased_remains_source_C_without_reservoir` | true |
| `node_plus_packet_budget_conserved` | true |
| `immediate_receiver_credit_difference_is_not_DR4_readout` | true |
| `receipt_count_is_validation_only_and_malformed_pairs_refuse` | true |
| `release_policy_identity_matches_I9_contract` | true |
| `semantic_edge_payload_excluded_from_producer_inputs` | true |
| `source_current_input_allowlist_observed_exactly` | true |
| `native_and_closure_restoration_exact` | true |
| `duplicate_branch_outcome_replay_exact` | true |
| `composed_native_closure_policy_topology_identity_recorded` | true |
| `lane_control_statuses_normalized_without_failed_open` | true |
| `I9_revision_lineage_and_formal_row_boundary_explicit` | true |
| `complete_control_matrix_remains_pending_I10` | true |
| `artifact_manifest_exact` | true |
| `DR3_ceiling_with_DR4_and_DR5_blocked` | true |
| `native_lane_not_upgraded` | true |
| `unsafe_claim_flags_false` | true |
| `src_diff_empty` | true |
| `protected_runtime_contract_diff_empty` | true |
| `no_absolute_paths_in_records` | true |
