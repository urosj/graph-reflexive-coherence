# N16 Boundary Source Inventory

Status: `passed`.

## Summary

```json
{
  "b_axis_lineage_rows": 6,
  "by_boundary_state": {
    "B0": 1,
    "B1": 5,
    "B2": 9,
    "B3": 9,
    "B4": 4
  },
  "by_challenge_class": {
    "C0": 3,
    "C1": 10,
    "C2": 10,
    "C3": 1,
    "C4": 9,
    "C5": 5
  },
  "by_direct_historic_support_status": {
    "absent": 16,
    "partial": 2,
    "rejected": 1
  },
  "by_evidence_strategy": {
    "b_axis_lineage_source": 3,
    "b_axis_lineage_source_and_c2_analog": 1,
    "b_axis_lineage_source_and_c_axis_analog": 1,
    "b_axis_lineage_source_for_b2_b3": 1,
    "boundary_and_blocked_input_audit": 1,
    "constructed_ap6_context_from_old_best_claims": 1,
    "constructed_context_with_upstream_observation_caveat": 1,
    "control_context_for_ap6_replay_requirements": 1,
    "lineage_caveat_and_blocked_identity_boundary": 1,
    "old_best_claims_construction_context": 1,
    "old_best_claims_construction_input": 4,
    "readiness_only_context": 1,
    "repair_context_for_b3_but_not_ap6": 1,
    "repair_context_with_identity_support_caveat": 1
  },
  "by_evidence_strategy_class": {
    "control_context": 1,
    "lineage_derivation": 9,
    "old_best_claims_construction": 7,
    "readiness_only": 1,
    "rejected": 1
  },
  "by_experiment": {
    "N03": 2,
    "N04": 3,
    "N07": 2,
    "N08": 1,
    "N09": 2,
    "N12": 1,
    "N13": 2,
    "N14": 2,
    "N15": 4
  },
  "by_source_role_classification": {
    "boundary_crossing_trace": 13,
    "boundary_role": 6,
    "claim_boundary_blocker": 5,
    "external_perturbation_state": 5,
    "external_resource_state": 5,
    "external_structured_state": 1,
    "internal_support_state": 9,
    "readiness": 1
  },
  "direct_historic_ap6_support_rows": 0,
  "old_best_claim_input_records": 6,
  "old_best_claims_construction_input_rows": 4,
  "readiness_only_rows": 1,
  "row_count": 19
}
```

## Acceptance State

```text
accepted_boundary_source_inventory_only_no_ap6
```

## Interpretation

```json
{
  "acceptance_state": "accepted_boundary_source_inventory_only_no_ap6",
  "next_required_step": "Freeze the N16 boundary schema, B-axis lineage contract, C-axis challenge-class contract, row decisions, source roles, budget surface, replay digest, and AP6 gates.",
  "plain_language_interpretation": "Iteration 1 pins N16's evidence base. It finds no direct historic AP6 support, but records old-best AP3-AP5 inputs, B-axis lineage from prior basin/boundary examples, and operational C-axis challenge classes for later schema work.",
  "supported_interpretation": "N16 has sufficient pinned source coverage to proceed to schema freeze. AP6 remains unassigned; the strongest path is constructed from old-best claims plus newly generated N16 boundary rows.",
  "unsupported_interpretations": [
    "final AP6 self/environment boundary support",
    "native support",
    "selfhood",
    "personhood",
    "identity acceptance",
    "semantic goal ownership",
    "intention",
    "agency",
    "selective uptake",
    "organism or life claims"
  ]
}
```

Iteration 1 is a source inventory only. It pins source artifacts, derives provisional B0-B4 lineage from prior N** evidence, records C0-C5 as operational challenge classes, and confirms no final `AP6` claim is assigned.

The global roadmap and handoff are listed as context documents in the JSON but are not SHA-pinned by this artifact, because they are updated after iteration artifacts and would otherwise create a self-referential digest.

`generated_at` is fixed for deterministic reconstruction and is excluded from `output_digest` with git working-tree metadata.

## Direct Historic AP6 Support

```json
{
  "direct_historic_support_status": "absent",
  "interpretation": "No pinned historic source directly supports AP6 internal/external state separability. Prior records provide B-axis lineage, challenge analogs, controls, and old-best AP3-AP5 construction inputs only.",
  "status": "none_found"
}
```

## Old-Best Claim Inputs

| Input | Why included | Supports | Does not support | Required N16 addition | Claim ceiling |
| --- | --- | --- | --- | --- | --- |
| `N15_AP5` | strongest closed AP prerequisite before N16; supplies source-current target/proxy formation discipline | artifact-level target/proxy condition generated from source-current support, memory, regulation, and AP4 context | internal/external boundary-side assignment, semantic goal ownership, agency, identity acceptance, or native support | separate internal support-relevant state from external resource, perturbation, or structured state under AP6 controls and replay | `artifact_level_ap5_endogenous_proxy_formation_candidate` |
| `N14_AP4` | supplies the strongest closed route/consequence context for external resource and directional-flux analogs | artifact-level consequence-sensitive route selection and constructed route-conditioned support/regulation followout | intention, semantic choice, agency, or observed upstream route-conditioned support/regulation | boundary-side descriptors that keep route/resource context separate from internal support state | `artifact_level_ap4_consequence_sensitive_route_selection_candidate` |
| `N13_AP3` | supplies the strongest closed support-maintenance and bounded response context for B2/B3 | artifact-level support-seeking regulation and support disruption/restoration stress context | selfhood, agency, identity acceptance, native support, or AP6 boundary-side separability | source-current boundary rows that distinguish maintained internal support from external challenge state | `artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation` |
| `N08` | supplies route-memory context for old-best construction and weak B4 shared-medium analogs | artifact-only route memory, trail/affordance context, and geometry-mediated alternatives | multi-basin separability, identity acceptance, native memory support, or AP6 boundary evidence | explicit shared-medium boundary rows if memory alternatives are used for B4 | `artifact_only_route_memory_or_trail_affordance_candidate` |
| `N09` | supplies perturbation/recovery and bounded-regulation context for B3 and C1/C4 | artifact-level bounded proxy regulation and perturbation recovery context | endogenous boundary repair, semantic goal ownership, native regulation, or identity support outcome | breach/reclosure rows that distinguish repair from explicit support restoration or post-hoc relabeling | `repeated_bounded_proxy_regulation_candidate` |
| `N12_NAT4` | records Phase 8 readiness constraints and prevents readiness from being relabeled as native support | readiness-only context for later native-policy work | native support, AP6 boundary evidence, or fully native integration | keep readiness weight/context separate from boundary-side evidence unless a separate Phase 8 task is opened | `readiness_only_not_native_support` |

## Source Rows

| Row | Source | Role | Strategy class | Direct support | Provisional level | Claim ceiling | Boundary relevance | Missing gates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `n16_i1_row_01_n15_closeout_ap5` | `N15` | `internal_support_state, boundary_crossing_trace, claim_boundary_blocker` | `old_best_claims_construction` | `absent` | `AP5` | `artifact_level_ap5_endogenous_proxy_formation_candidate` | `B2, B3` | `ap6_internal_external_boundary_schema_not_frozen, ap6_boundary_rows_not_generated, ap6_controls_not_run` |
| `n16_i1_row_02_n15_runtime_derived_target_candidate` | `N15` | `internal_support_state, boundary_crossing_trace` | `old_best_claims_construction` | `absent` | `AP5_candidate_at_iteration_3_scope` | `provisional_runtime_derived_target_candidate_pending_controls` | `B2, B3` | `target_condition_is_not_boundary_side_assignment, internal_external_state_separation_not_built, ap6_claim_boundary_not_classified` |
| `n16_i1_row_03_n15_bounded_drift_replay` | `N15` | `internal_support_state, external_perturbation_state, boundary_crossing_trace` | `control_context` | `absent` | `AP5_control_context` | `bounded_drift_replay_context_only` | `B2, B3` | `boundary_side_replay_digest_not_frozen, challenge_class_rows_not_generated` |
| `n16_i1_row_04_n15_claim_boundary` | `N15` | `external_structured_state, claim_boundary_blocker` | `rejected` | `rejected` | `AP0_boundary` | `claim_boundary_context_only` | `B0` | `positive_ap6_boundary_evidence_absent` |
| `n16_i1_row_05_n14_closeout_ap4` | `N14` | `external_resource_state, boundary_crossing_trace, claim_boundary_blocker` | `old_best_claims_construction` | `absent` | `AP4` | `artifact_level_ap4_consequence_sensitive_route_selection_candidate` | `B4` | `route_selection_is_not_boundary_separability, shared_medium_boundary_rows_not_generated` |
| `n16_i1_row_06_n14_constructed_followout` | `N14` | `external_resource_state, boundary_crossing_trace` | `old_best_claims_construction` | `absent` | `AP4_context` | `constructed_route_conditioned_followout_context_only` | `B4` | `upstream_observed_route_conditioned_support_missing, upstream_observed_route_conditioned_regulation_missing, not_multi_basin_separability_evidence` |
| `n16_i1_row_07_n13_closeout_ap3` | `N13` | `internal_support_state, boundary_crossing_trace, claim_boundary_blocker` | `old_best_claims_construction` | `absent` | `AP3` | `artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation` | `B2, B3` | `support_regulation_is_not_selfhood, boundary_side_assignment_not_built, external_state_descriptors_not_built` |
| `n16_i1_row_08_n13_support_disruption_restoration` | `N13` | `internal_support_state, external_perturbation_state, boundary_crossing_trace` | `lineage_derivation` | `absent` | `AP3_stress_context` | `support_disruption_restoration_context_only` | `B3` | `boundary_reclosure_policy_not_defined, external_perturbation_boundary_side_not_frozen` |
| `n16_i1_row_09_n12_phase8_readiness` | `N12` | `readiness` | `readiness_only` | `absent` | `AP0_readiness` | `readiness_only_not_native_support` | `none` | `phase8_implementation_not_opened, native_supported_flags_false, not_boundary_evidence` |
| `n16_i1_row_10_n03_artifact_surface_inventory` | `N03` | `boundary_role` | `lineage_derivation` | `absent` | `pre_AP_boundary_lineage` | `artifact_surface_inventory_only` | `B1` | `configured_parent_region_not_ap6_boundary, inside_outside_boundary_schema_not_frozen` |
| `n16_i1_row_11_n03_native_packet_loop_closeout` | `N03` | `boundary_role, boundary_crossing_trace` | `lineage_derivation` | `absent` | `pre_AP_boundary_lineage` | `native_lgrc9v3_packet_loop_reproduced` | `B1, B2` | `loop_evidence_is_not_self_environment_boundary, movement_and_agency_claims_blocked` |
| `n16_i1_row_12_n04_taxonomy_inventory` | `N04` | `boundary_role, external_resource_state` | `lineage_derivation` | `absent` | `pre_AP_boundary_lineage` | `taxonomy_inventory_only` | `B1, B2, B3` | `movement_taxonomy_is_not_ap6_boundary_taxonomy, challenge_classes_are_n16_operational_conditions` |
| `n16_i1_row_13_n04_boundary_coupled_pulse` | `N04` | `external_resource_state, boundary_crossing_trace, boundary_role` | `lineage_derivation` | `absent` | `pre_AP_boundary_lineage` | `boundary_coupled_pulse_fixture_validation` | `B1` | `boundary_coupling_is_not_boundary_persistence, movement_claims_blocked` |
| `n16_i1_row_14_n04_taxonomy_continuation_closeout` | `N04` | `boundary_role, claim_boundary_blocker` | `lineage_derivation` | `absent` | `pre_AP_boundary_lineage` | `topology_mutating_movement_candidate` | `B1, B2` | `rc_identity_through_topology_mutation_blocked, movement_candidate_is_not_ap6_boundary` |
| `n16_i1_row_15_n07_long_horizon_compatibility_closeout` | `N07` | `internal_support_state, boundary_role` | `lineage_derivation` | `partial` | `ID6_context_not_AP` | `artifact_only_source_specific_bounded_non_destructive_exchange` | `B2, B4` | `id6_is_not_runtime_identity_acceptance, dual_basin_exchange_is_not_ap6_shared_medium_boundary` |
| `n16_i1_row_16_n07_identity_support_withdrawal_baseline` | `N07` | `internal_support_state, external_perturbation_state, boundary_crossing_trace` | `lineage_derivation` | `partial` | `ID6_context_not_AP` | `identity_support_withdrawal_baseline_only` | `B2, B3` | `identity_support_baseline_is_not_selfhood, restoration_is_explicit_not_native_boundary_repair` |
| `n16_i1_row_17_n08_memory_trail_closeout` | `N08` | `external_resource_state, boundary_crossing_trace` | `old_best_claims_construction` | `absent` | `AP2_context` | `artifact_only_route_memory_or_trail_affordance_candidate` | `B4` | `route_memory_is_not_multi_basin_separability, native_memory_support_not_opened` |
| `n16_i1_row_18_n09_goal_proxy_regulation_closeout` | `N09` | `internal_support_state, external_perturbation_state, boundary_crossing_trace` | `old_best_claims_construction` | `absent` | `AP2_context` | `repeated_bounded_proxy_regulation_candidate` | `B3` | `external_proxy_regulation_is_not_endogenous_boundary, semantic_goal_ownership_blocked` |
| `n16_i1_row_19_n09_perturbation_withdrawal_support` | `N09` | `internal_support_state, external_perturbation_state, boundary_crossing_trace` | `lineage_derivation` | `absent` | `AP2_context` | `perturbation_recovery_context_only` | `B3` | `support_withdrawal_identity_boundary_gap_preserved, not_native_boundary_repair` |

## Source Pinning

| Row | Source artifact | Artifact SHA-256 | Source report | Report SHA-256 |
| --- | --- | --- | --- | --- |
| `n16_i1_row_01_n15_closeout_ap5` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_closeout_and_handoff.json` | `9a86c0e3f5fcc96dd055a8c05baf8b0cd22edc91693a67dc6a8ee209db862fa5` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_closeout_and_handoff.md` | `7fd4773de2bb4cce79799caf287f22b13e056b567a44da562d22665d07fda4ee` |
| `n16_i1_row_02_n15_runtime_derived_target_candidate` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_runtime_derived_target_candidate.json` | `30c834b47a7decf2bb32f3dabb8dcb436b2b7876be5b0e9c79fe76b7de010873` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_runtime_derived_target_candidate.md` | `c54c784652e004a23f1283d8e716f370993636b72e4d9ade46f2d9d7c071277c` |
| `n16_i1_row_03_n15_bounded_drift_replay` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_bounded_drift_replay_matrix.json` | `c9c5307c408836d7a54e88507ceb85cf6dae4755444b20ab072409cddbc7b3d0` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_bounded_drift_replay_matrix.md` | `8766f392358f7aa675a591c076e3cec5a97f91af5ed5f382bc306a9809a13728` |
| `n16_i1_row_04_n15_claim_boundary` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_claim_boundary_record.json` | `99781fbd38ea972c07c1f1313cbcce95bbbc99eeec05cdafb2678a445810bb87` | `experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_claim_boundary_record.md` | `9a7f9558adeda1449f5b728cf330bea1a4906a99094d9a8fa5c8a310284845fe` |
| `n16_i1_row_05_n14_closeout_ap4` | `experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/n14_closeout_and_handoff.json` | `47d794a5fd53e96e9017d5cbdcf8959d5372d6dfa52467661a0dc14661eadbc1` | `experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_closeout_and_handoff.md` | `5f058dd6802065954e2c4e0f8d663d93fb8d55b2520a43edafbf79b3a14e1c7a` |
| `n16_i1_row_06_n14_constructed_followout` | `experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/n14_route_conditioned_followout_probe.json` | `450dd43f4f35a7ba375fa0b197c34c11a0ddac324b2d26660d75c98b201ccaa4` | `experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_route_conditioned_followout_probe.md` | `6b25d12a8f8cf9412d317ebb398972be68b19f9ae8cc8f683b59fbf69316533f` |
| `n16_i1_row_07_n13_closeout_ap3` | `experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/outputs/n13_closeout_and_handoff.json` | `4a6aefc94f50d90795c64199e7cf84b430a197aa5f0e07c9215e6fa66b362806` | `experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/reports/n13_closeout_and_handoff.md` | `e2b46f6790e95488c0b3eef70469fcfd618b31ff6b2b9aa13ead1c8ed9ae3b45` |
| `n16_i1_row_08_n13_support_disruption_restoration` | `experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/outputs/n13_support_disruption_restoration_matrix.json` | `35270298acde53f910eb9b88582d7c326d89ca601f30bef44aaaf68b657c9363` | `experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/reports/n13_support_disruption_restoration_matrix.md` | `3bbf1027e535b3c6136223ca1559f6bdd4e29c6a736fe1f19dbc559f0870685b` |
| `n16_i1_row_09_n12_phase8_readiness` | `experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_phase8_readiness_matrix.json` | `c4106d4f61cfe19ab43b29d0c045565d739f90cdf71aea33a21a938237d2bf14` | `experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/reports/n12_phase8_readiness_matrix.md` | `7eb21e99caa2293f8fdd6baa2afdf487b291f73fef3cd7e2a64ff115110c88c5` |
| `n16_i1_row_10_n03_artifact_surface_inventory` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/artifact_surface_inventory.json` | `a2d5cc1ba7656287a5fc3a2ae269ef0771200b85202b90799fb023c166226283` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/artifact_surface_inventory.md` | `d4a91a89f39ed1b2343d7e51f438752bf8f7d2b28b331cd0830e38094ab91d9e` |
| `n16_i1_row_11_n03_native_packet_loop_closeout` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_closeout.json` | `75e02858f32484a8c4e9a24d9751c0ce98e4ef603fd6e550d8a47f7466e2288e` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_closeout.md` | `92c697eb444168ae1182b481ed0fbe10671892b341dc078f57d2f2944aa15c8d` |
| `n16_i1_row_12_n04_taxonomy_inventory` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_inventory_v1.json` | `40dcf56c001f25909c92e3b39e570889e6f52f8b44b425533ba6e31eb942c72a` | `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_inventory_v1.md` | `827336ad46f1d6319dd4a2ec538b9d6e23a19b2d0aa969e5b5a964e85eb5998b` |
| `n16_i1_row_13_n04_boundary_coupled_pulse` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_report.json` | `c1ff70f62955be6120a59665753073c2f409a7f0e2c15ea879dbec850d6a8abd` | `experiments/2026-05-N04-grc9v3-movement-ladders/reports/boundary_coupled_pulse_report.md` | `6a1174c6756c3e34d378abe202f05c2bf15cc5a5ef5a36188d32343b6db0aa1a` |
| `n16_i1_row_14_n04_taxonomy_continuation_closeout` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json` | `36a96f188b2d0d32ee7d8840305bec34554b54de68f46c433f96271c2c53d780` | `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_continuation_closeout.md` | `8b48f9b68b2314e40c0a52279101d922adb152d405515c5f70e7ae65956a3841` |
| `n16_i1_row_15_n07_long_horizon_compatibility_closeout` | `experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_12_long_horizon_compatibility_closeout.json` | `af966c2f8063d88078d7a1c5fb9cfc0286b383ce7970221bdd8248e443c5c189` | `experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_12_long_horizon_compatibility_closeout.md` | `33bfb5c32c7212cce496d1d0e2495dda95b9627ffe510fe79afe4981548d7bc8` |
| `n16_i1_row_16_n07_identity_support_withdrawal_baseline` | `experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_13_identity_support_withdrawal_baseline.json` | `a33659fe4d755a696f506b543c41be9578c4c4d1fa4076502bcca9aac1fadc5b` | `experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_13_identity_support_withdrawal_baseline.md` | `b56bfe04e4249eb16500d87b5d1911979153298d99efe3417b9d6c354faac0bc` |
| `n16_i1_row_17_n08_memory_trail_closeout` | `experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_8_mem6_closeout.json` | `73c0681ff6f2d32fe259f2153e3398abad03095e6d9dcfd364b55bf23c48454e` | `experiments/2026-05-N08-lgrc-memory-trail-affordance/reports/n08_iteration_8_mem6_closeout.md` | `f60aa7ab93ca41823c117f45ddd4e4443721f284bc16456f53ea8b8213162d81` |
| `n16_i1_row_18_n09_goal_proxy_regulation_closeout` | `experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_9_gpr6_closeout.json` | `f2023e4b3aa456ac7aa301494b25e4a190226260fb90adc1c292182dccee3b68` | `experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_9_gpr6_closeout.md` | `9fc0e91a58892746a55d67c0a5d6c0ab29912a40c8790a9f186091d56f7319f0` |
| `n16_i1_row_19_n09_perturbation_withdrawal_support` | `experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_8_perturbation_withdrawal_support.json` | `873114340bf655becf39f47dbbd4758f46204eee05a1fb93a0a7457db3caa472` | `experiments/2026-05-N09-lgrc-goal-proxy-regulation/reports/n09_iteration_8_perturbation_withdrawal_support.md` | `9d72834521f0b4f30bc83747992c41acb3eada9661e0d04d0c5a51302e6a710b` |

## Source Role Taxonomy

| Role |
| --- |
| `internal_support_state` |
| `external_resource_state` |
| `external_perturbation_state` |
| `external_structured_state` |
| `boundary_crossing_trace` |
| `readiness` |
| `boundary_role` |
| `claim_boundary_blocker` |

## B-Axis Lineage

| State | Name | Claim ceiling | Required N16 evidence |
| --- | --- | --- | --- |
| `B0` | null / external coherence only | `active_null_control_no_boundary_claim` | B0 x C3 must reject structured external coherence as self-boundary |
| `B1` | localized basin partition | `localized_basin_partition_candidate_pending_n16_schema` | quiet B1 row must extract boundary edges without supplied labels; B1 x C2 must expose failure threshold under flux |
| `B2` | support-persistent basin | `support_persistent_basin_candidate_pending_n16_matrix` | B2 x C0, C1, and C2 must be evaluated before B3 is unlocked; boundary-side assignments must be replayable and source-current |
| `B3` | regulated repair / reabsorption boundary | `regulated_repair_candidate_locked_until_b2_calibration` | B3 remains locked until B2 C0-C2 evaluations are present or explicitly blocked; B3 x C4 must distinguish reclosure from relabeling |
| `B4` | coupled multi-basin separability candidate | `multi_basin_separability_candidate_new_n16_evidence_required` | B4 x C5 must test shared-medium multi-basin exclusivity; B4 x C2 must remain partial or not_applicable if shared substrate support is insufficient |

## C-Axis Challenge Classes

| Class | Name | Operational role | Claim boundary |
| --- | --- | --- | --- |
| `C0` | quiet reference | calibration condition with no intended boundary stress | `operational_challenge_class_not_environment_taxonomy` |
| `C1` | unstructured perturbation | random or noisy disturbance around or across the boundary | `operational_challenge_class_not_environment_taxonomy` |
| `C2` | directional flux | one-sided pressure, drift, or flow across the boundary | `operational_challenge_class_not_environment_taxonomy` |
| `C3` | structured external coherence | active null for coherent outside pattern that must not be mistaken for self-boundary | `false_positive_pressure_not_perturbation_unless_crossing_or_disruption_recorded` |
| `C4` | breach and repair | local boundary disruption followed by reclosure, reabsorption, or fail-closed classification | `operational_challenge_class_not_environment_taxonomy` |
| `C5` | coupled neighbor / shared medium | more than one candidate basin interacting through a shared substrate | `new_n16_shared_medium_evidence_required` |

## Checks

```json
{
  "all_required_source_experiments_present": true,
  "arc_method_mapping_recorded": true,
  "b0_b4_lineage_recorded": true,
  "c0_c5_challenge_records_recorded": true,
  "c3_structured_external_not_perturbation_by_default": true,
  "claim_ceiling_preservation_passed": true,
  "claim_flags_forced_false": true,
  "direct_historic_ap6_status_mapping_complete": true,
  "direct_historic_ap6_status_values_valid": true,
  "direct_historic_ap6_support_absent": true,
  "direct_historic_support_status_values_valid": true,
  "every_row_has_source_report_sha256": true,
  "every_row_has_source_sha256": true,
  "every_source_row_pinned_with_artifact_report_and_digests": true,
  "evidence_strategy_class_values_valid": true,
  "external_structured_state_classification_present": true,
  "final_ap6_not_assigned": true,
  "inventory_summary_matches_rows": true,
  "inventory_summary_row_count_matches": true,
  "lineage_sources_reference_valid_rows": true,
  "native_support_not_opened": true,
  "no_absolute_paths_recorded": true,
  "old_best_claim_inputs_have_required_fields": true,
  "old_best_claim_inputs_recorded": true,
  "old_best_summary_names_unambiguous": true,
  "phase8_opened_false": true,
  "provisional_only": true,
  "required_roles_present": true,
  "required_source_paths_exist": true,
  "role_classification_incompatibility_audit_passed": true,
  "row_decision_values_valid": true,
  "row_decisions_fail_closed": true,
  "source_status_values_valid": true,
  "source_statuses_loaded": true,
  "src_diff_empty": true
}
```

## Claim Boundary

```text
source inventory != self/environment boundary
B-axis lineage != invented generic boundary taxonomy
C-axis challenge class != inherited environment taxonomy
N15 AP5 != AP6
N14 AP4 != intention or agency
N13 AP3 != selfhood or native support
N12 NAT4 readiness != native support
N07 ID6 context != runtime identity acceptance
N16 Iteration 1 != selective uptake or resource assimilation
```

## Output Digest

```text
5c8972426df7b4d1b28e6de4f1fd19d093e3ac6f3b70f40f790207175ebc3b65
```
