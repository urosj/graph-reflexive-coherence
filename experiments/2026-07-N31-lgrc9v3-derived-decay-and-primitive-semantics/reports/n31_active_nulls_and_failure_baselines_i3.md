# N31 Iteration 3 - Active Nulls And Failure Baselines

Status: `passed`

Acceptance state: `accepted_active_nulls_fail_closed_no_positive_decay_evidence`

Output digest: `e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea`

## Scope

I3 instantiates every I2 control as a claim-relative, derived-fixture active
null. It establishes which false-positive paths must be rejected before a
positive candidate is admitted. It does not execute a source-current decay
probe and cannot assign a positive DR rung.

`failed_closed` means that the declared blocker was present and the specific
overclaim was correctly rejected. It does not mean that a runtime experiment
failed. `failed_open` would be the governance failure; I3 has zero such rows.

## Family Summary

| Family | Rows | Failed closed | Failed open |
|---|---:|---:|---:|
| common | 16 | 16 | 0 |
| D0 | 28 | 28 | 0 |
| A | 5 | 5 | 0 |
| B | 8 | 8 | 0 |
| C | 5 | 5 | 0 |
| schema_relation | 8 | 8 | 0 |

The five affirmative, five dimensional, and five ownership controls are
overlapping tags on these same 70 rows. They are not additional families or
executions.

## Validator Receipts

Every row retains a named predicate, bad-fixture digest, exact rejected gate,
repair mutation, repaired-fixture digest, and both predicate outcomes. I3
assigns `failed_closed` only when the bad fixture is rejected and the same
fixture with the targeted blocker repaired is no longer rejected. The repaired
fixture is explicitly not positive evidence.

## Semantic Comparability

Every row records semantic class, authority, organization domain,
load-bearing domain, internal-time policy, candidate schema, carrier, and
continuation-state contract. Matching topology alone is not comparability. A
later positive row may consume an I3 null only when this semantic contract
matches; otherwise the null must be regenerated for that candidate.

I3 is therefore a baseline control library, not a universal control pass. The
frozen future resolver requires candidate ID, control ID, matched null ID,
comparability status/digest, regeneration decision, and resolved source-current
control artifact. No future candidate may inherit the phrase "all controls
passed" from I3.

## Scientific Boundaries Exercised

- Route mass, route organization, and causal mediation remain independent.
- Boundary flux is time-integrated exported coherence, not an instantaneous
  rate; boundary crossings are counted once.
- Producer ownership is derived from calls, scheduled events, mutation paths,
  and export decisions. Scheduling without direct mutation can still author
  the aftereffect.
- B-R classification records policy ownership but does not establish positive
  B-R decay support.
- Persistent D0c requires a new D0a candidate identity. Causal use of D0b
  requires exact-derived causal authority or closure classification.
- Contradictory disposition, authority, mediation, and DR combinations are
  machine-rejected.

The transition record must preserve the source row, trigger, new candidate ID,
new semantic class or authority, and `old_row_unchanged = true`; in-place
semantic upgrades are prohibited.

## Affirmative Discriminators

Five controls are affirmative discriminators viewed relative to a specific
overclaim: cache recomputation, observable disconnection, slow-organization
clamping, an allegedly complete or node-scalar-complete history contrast, and
equal-C/different-S future contrast. Their `failed_closed` status rejects the
overclaim under test. Any
orthogonal positive implication remains a future source-current probe and is
not evidence from I3.

## Source-Current Execution Boundary

I3 proves validator and control semantics over derived fixtures. It does not
prove that future runtime rows expose enough call lineage, packet identities,
runtime masks, state mutations, read-path guards, or restoration state to
evaluate those controls. I7-I10 must resolve applicable controls against actual
candidate traces; an I3 fixture cannot substitute for that execution.

## Control Matrix

| Control | Family | Class | Mediator domain | Violated gate | Status |
|---|---|---|---|---|---|
| `label_only_decay` | common | D0a | spatial_distribution | `source_current_relation_gate` | `failed_closed` |
| `wall_clock_decay` | common | D0a | temporal_alignment | `internal_time_owner_gate` | `failed_closed` |
| `post_hoc_weakening_trace` | common | D0b | spatial_distribution | `source_current_trace_gate` | `failed_closed` |
| `forming_activity_never_stopped` | common | D0c | spatial_distribution | `formation_stopped_gate` | `failed_closed` |
| `relation_persists_but_does_not_weaken` | common | D0a | spatial_distribution | `weakening_gate` | `failed_closed` |
| `relation_weakens_but_has_no_later_readout_effect` | common | D0a | spatial_distribution | `causal_mediation_gate` | `failed_closed` |
| `global_route_selector` | common | D0a | functional_coupling | `locality_and_owner_gate` | `failed_closed` |
| `hidden_producer_update` | common | D0a | functional_coupling | `producer_visibility_gate` | `failed_closed` |
| `unrecorded_post_formation_producer_call` | common | D0a | spatial_distribution | `producer_call_audit_gate` | `failed_closed` |
| `missing_internal_time_owner` | common | D0a | temporal_alignment | `internal_time_schema_gate` | `failed_closed` |
| `missing_invariant` | common | D0a | spatial_distribution | `invariant_gate` | `failed_closed` |
| `missing_restoration_state` | common | D0a | spatial_distribution | `restoration_gate` | `failed_closed` |
| `report_digest_as_runtime_state` | common | D0b | spatial_distribution | `runtime_state_identity_gate` | `failed_closed` |
| `native_relabel_from_producer` | common | D0a | spatial_distribution | `authority_relabel_gate` | `failed_closed` |
| `RCAE_demand_as_graph_evidence` | common | D0a | spatial_distribution | `source_authority_gate` | `failed_closed` |
| `trail_or_stigmergy_relabel` | common | D0a | spatial_distribution | `claim_boundary_gate` | `failed_closed` |
| `lossy_node_scalar_match_as_complete_state` | D0 | D0a | spatial_distribution | `complete_state_representation_gate` | `failed_closed` |
| `invented_C_slow_state` | D0 | D0a | spatial_distribution | `native_state_authority_gate` | `failed_closed` |
| `producer_scheduled_D0_decay` | D0 | D0a | temporal_alignment | `aftereffect_owner_gate` | `failed_closed` |
| `export_authoring_producer_call_retained_as_D0_R` | D0 | D0a | functional_coupling | `export_policy_owner_gate` | `failed_closed` |
| `instantaneous_geometry_as_durable_decay` | D0 | D0c | induced_geometry | `post_formation_persistence_gate` | `failed_closed` |
| `derived_observable_as_causal_trail` | D0 | D0b | functional_coupling | `independent_causal_state_gate` | `failed_closed` |
| `cache_removed_and_recomputed` | D0 | D0b | spatial_distribution | `independent_state_gate` | `failed_closed` |
| `cache_divergence` | D0 | D0b | spatial_distribution | `exact_recomputation_gate` | `failed_closed` |
| `observable_disconnected_from_transport` | D0 | D0b | functional_coupling | `causal_mediation_gate` | `failed_closed` |
| `slow_organization_clamp` | D0 | D0a | spatial_distribution | `mediator_intervention_gate` | `failed_closed` |
| `complete_state_matched_history_contrast` | D0 | D0a | mixed | `complete_state_identity_gate` | `failed_closed` |
| `ordinary_outward_flux_as_added_leakage_relabel` | D0 | D0a | spatial_distribution | `policy_owner_classification_gate` | `failed_closed` |
| `route_mass_loss_as_organization_weakening_relabel` | D0 | D0a | spatial_distribution | `mass_organization_separation_gate` | `failed_closed` |
| `organization_weakening_without_mediation_as_causal_decay_relabel` | D0 | D0a | spatial_distribution | `causal_mediation_gate` | `failed_closed` |
| `constant_mass_internal_reorganization_as_export_relabel` | D0 | D0a | spatial_distribution | `route_mass_export_gate` | `failed_closed` |
| `unclosed_route_boundary_continuity` | D0 | D0a | spatial_distribution | `integrated_route_boundary_continuity_gate` | `failed_closed` |
| `added_export_policy_as_D0_R_relabel` | D0 | D0a | functional_coupling | `export_policy_owner_gate` | `failed_closed` |
| `mass_unmatched_organization_intervention` | D0 | D0a | spatial_distribution | `matched_intervention_gate` | `failed_closed` |
| `proper_time_annotation_as_causal_alignment` | D0 | D0b | temporal_alignment | `temporal_mediator_authority_gate` | `failed_closed` |
| `added_coincidence_window_as_native_temporal_organization` | D0 | D0a | temporal_alignment | `added_temporal_policy_authority_gate` | `failed_closed` |
| `arrival_histogram_as_causal_mediation` | D0 | D0b | arrival_time_distribution | `causal_mediation_gate` | `failed_closed` |
| `fixed_delay_single_path_as_dispersion` | D0 | D0b | arrival_time_distribution | `dispersion_definition_gate` | `failed_closed` |
| `periodic_rephasing_as_monotonic_decay` | D0 | D0a | temporal_alignment | `weakening_trajectory_gate` | `failed_closed` |
| `diagnostic_domain_as_mediator_domain` | D0 | D0b | mixed | `load_bearing_domain_gate` | `failed_closed` |
| `mixed_domain_without_load_bearing_isolation` | D0 | D0a | mixed | `mixed_domain_resolution_gate` | `failed_closed` |
| `forming_packet_continuation_as_later_independent_readout` | D0 | D0a | functional_coupling | `formation_packet_exclusion_gate` | `failed_closed` |
| `temporal_intervention_with_unmatched_state` | D0 | D0a | temporal_alignment | `temporal_intervention_matching_gate` | `failed_closed` |
| `geometric_observable_without_local_transport_intervention` | D0 | D0b | induced_geometry | `local_transport_intervention_gate` | `failed_closed` |
| `in_flight_packet_attenuation` | A | A | temporal_alignment | `in_flight_immutability_gate` | `failed_closed` |
| `carrier_amount_vs_release_efficacy_confound` | A | A | temporal_alignment | `carrier_efficacy_separation_gate` | `failed_closed` |
| `unregistered_age_or_phase` | A | A | temporal_alignment | `registered_internal_phase_gate` | `failed_closed` |
| `unreleased_coherence_as_destroyed` | A | A | temporal_alignment | `source_conservation_gate` | `failed_closed` |
| `route_label_in_amount_policy` | A | A | functional_coupling | `route_independent_amount_gate` | `failed_closed` |
| `local_loss_without_destination` | B | B | spatial_distribution | `destination_and_conservation_gate` | `failed_closed` |
| `source_debit_packet_amount_target_credit_mismatch` | B | B | spatial_distribution | `transfer_conservation_gate` | `failed_closed` |
| `hidden_reservoir` | B | B | spatial_distribution | `closed_system_boundary_gate` | `failed_closed` |
| `new_leakage_policy_as_ordinary_D0_relabel` | B | B | spatial_distribution | `authority_relabel_gate` | `failed_closed` |
| `global_emission_scheduler` | B | B | functional_coupling | `local_policy_owner_gate` | `failed_closed` |
| `unbounded_emitted_amount` | B | B | spatial_distribution | `bounded_emission_gate` | `failed_closed` |
| `receiver_in_later_read_path` | B | B | functional_coupling | `direct_readout_path_exclusion_gate` | `failed_closed` |
| `B_R_as_D0_R_without_bridge` | B | B | spatial_distribution | `D0_R_bridge_gate` | `failed_closed` |
| `conductance_label_only` | C | C | functional_coupling | `independent_state_gate` | `failed_closed` |
| `susceptibility_without_restoration` | C | C | functional_coupling | `external_state_restoration_gate` | `failed_closed` |
| `history_carried_by_hidden_producer` | C | C | functional_coupling | `state_owner_and_identity_gate` | `failed_closed` |
| `same_complete_C_different_S_changes_future` | C | C | functional_coupling | `coherence_only_completeness_gate` | `failed_closed` |
| `producer_closure_as_native_memory` | C | C | functional_coupling | `authority_relabel_gate` | `failed_closed` |
| `bounded_partial_disposition_with_supported_row_decision` | schema_relation | D0a | spatial_distribution | `disposition_decision_relation_gate` | `failed_closed` |
| `blocked_representation_with_supported_row_decision` | schema_relation | D0a | spatial_distribution | `representation_decision_relation_gate` | `failed_closed` |
| `full_mediation_with_false_mediated_change` | schema_relation | D0a | spatial_distribution | `mediation_boolean_relation_gate` | `failed_closed` |
| `absent_mediation_with_true_mediated_change` | schema_relation | D0a | spatial_distribution | `mediation_boolean_relation_gate` | `failed_closed` |
| `mixed_domain_unresolved_claims_DR4` | schema_relation | D0a | mixed | `mixed_domain_rung_ceiling_gate` | `failed_closed` |
| `blocked_D0a_authority_as_coherence_only_positive` | schema_relation | D0a | spatial_distribution | `D0a_authority_gate` | `failed_closed` |
| `D0c_persistence_retained_as_same_D0c_row` | schema_relation | D0c | spatial_distribution | `semantic_transition_gate` | `failed_closed` |
| `D0b_transport_feedback_without_authority_reclassification` | schema_relation | D0b | functional_coupling | `semantic_authority_transition_gate` | `failed_closed` |

## Closeout Position

`positive_evidence_opened = false`

`decay_relation_ladder_ceiling = DR0_no_source_current_decay_evidence`

The active-null component of `N31-C2` is satisfied. The representation
component remains pending I4, so the N31 closeout ceiling remains `N31-C1`.

## Checks

- `I2_status_passed` = `true`
- `I2_output_digest_matches_frozen_value` = `true`
- `I2_artifact_sha256_matches` = `true`
- `control_registry_instantiated_exactly_once` = `true`
- `control_family_counts_match_I2` = `true`
- `all_active_null_required_fields_present` = `true`
- `semantic_classes_valid` = `true`
- `authority_classes_valid` = `true`
- `organization_domains_valid` = `true`
- `semantic_comparability_explicit` = `true`
- `false_positive_scenarios_explicit` = `true`
- `validator_receipts_and_repair_mutations_pass` = `true`
- `all_controls_failed_closed` = `true`
- `failed_open_rows_zero` = `true`
- `affirmative_discriminators_claim_relative` = `true`
- `cross_field_contradictions_rejected` = `true`
- `dimensional_controls_rejected` = `true`
- `trace_derived_ownership_controls_rejected` = `true`
- `semantic_transition_controls_present` = `true`
- `cross_cut_tags_are_subsets_not_families` = `true`
- `derived_fixtures_not_positive_evidence` = `true`
- `unsafe_claim_flags_false` = `true`
- `src_diff_empty` = `true`
- `protected_runtime_contract_diff_empty` = `true`
- `no_absolute_paths_in_records` = `true`
