# N07 Iteration 8: C1/T6 Artifact-Only Replay And ID5 Closeout

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_8_c1_t6_artifact_replay_closeout.py
```

Iteration 8 reconstructs the current source-backed C1/T6 single-basin identity
chain from exported artifacts only. The replay passes, but C3/T7 compatibility
is deferred to Iteration 9, so the closeout freezes the current N07 ceiling at
ID5 rather than claiming ID6.

The replay preserves the Iteration 7-B scope: state rows are source-backed,
packet/producers are digest-linked experiment-local constructions, actual LGRC
`step()` processing is not claimed, and all claim flags remain false.

## Replay Rows

| Rung | Source iteration | Row | Digest match |
|---|---|---|---:|
| `ID1` | `iteration_3` | `id1_candidate_row` | `True` |
| `ID2` | `iteration_4` | `id2_candidate_row` | `True` |
| `ID3` | `iteration_5b` | `id3_attractivity_stress_candidate_row` | `True` |
| `ID4` | `iteration_6b` | `id4_topology_stress_candidate_row` | `True` |
| `ID5` | `iteration_7b` | `id5_source_backed_t6_candidate_row` | `True` |

## Closeout Row

```json
{
  "activity_history": {
    "classification": "ID5_reflexively_self_maintaining_identity_candidate",
    "integration": {
      "artifact_replay": "pass",
      "compatibility": "deferred_to_iteration_9",
      "derived_id_ceiling": "ID5",
      "next": "9_c3_t7_competing_basin_compatibility_fixture_design"
    },
    "naturalization": "Nat0_probe_dependent_expression",
    "observation": "source_backed_C1_T6_single_basin_chain_replayed",
    "orientation": "N07 Iteration 8 C1/T6 artifact-only replay closeout",
    "probe": "artifact_only_replay_validator",
    "withdrawal": "not_tested"
  },
  "activity_history_digest": "6ad8cbabae5a13b960e07ae5c2c27a9ddc6ecc9d5d7377bfd3540cff64651a99",
  "activity_history_digest_scope": [
    "orientation",
    "observation",
    "classification",
    "probe",
    "withdrawal",
    "naturalization",
    "integration"
  ],
  "actual_lgrc_step_processed_packet": false,
  "agency_claim_allowed": false,
  "allocation_policy_origin": "experiment_local_design_probe",
  "artifact_replay_chain_digest": "ce4dcb296fff85fc084314e7701637d81d31922b3f84ca0aa113fc0d91e8f88b",
  "artifact_replay_gate": "pass",
  "becoming_class_status": "reusable_class",
  "boundary_rung": "recurrence_or_continuation",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "source_backed_reflexively_self_maintaining_identity_candidate",
  "claim_flags": {
    "agency_claim_allowed": false,
    "agentic_like_claim_allowed": false,
    "ant_colony_claim_allowed": false,
    "biological_claim_allowed": false,
    "goal_proxy_regulation_claim_allowed": false,
    "identity_acceptance_claim_allowed": false,
    "intention_claim_allowed": false,
    "locomotion_like_claim_allowed": false,
    "memory_or_trail_claim_allowed": false,
    "movement_claim_allowed": false,
    "personhood_claim_allowed": false,
    "rc_identity_collapse_claim_allowed": false,
    "semantic_choice_claim_allowed": false,
    "unrestricted_identity_claim_allowed": false,
    "unrestricted_movement_claim_allowed": false
  },
  "closeout_row_digest": "6a074e6680fb3f7e80f63cdc8ecfc92066d811a3a8cb32284bd9e7334ed8e1d7",
  "closeout_row_digest_input": {
    "activity_history": {
      "classification": "ID5_reflexively_self_maintaining_identity_candidate",
      "integration": {
        "artifact_replay": "pass",
        "compatibility": "deferred_to_iteration_9",
        "derived_id_ceiling": "ID5",
        "next": "9_c3_t7_competing_basin_compatibility_fixture_design"
      },
      "naturalization": "Nat0_probe_dependent_expression",
      "observation": "source_backed_C1_T6_single_basin_chain_replayed",
      "orientation": "N07 Iteration 8 C1/T6 artifact-only replay closeout",
      "probe": "artifact_only_replay_validator",
      "withdrawal": "not_tested"
    },
    "activity_history_digest": "6ad8cbabae5a13b960e07ae5c2c27a9ddc6ecc9d5d7377bfd3540cff64651a99",
    "activity_history_digest_scope": [
      "orientation",
      "observation",
      "classification",
      "probe",
      "withdrawal",
      "naturalization",
      "integration"
    ],
    "actual_lgrc_step_processed_packet": false,
    "agency_claim_allowed": false,
    "allocation_policy_origin": "experiment_local_design_probe",
    "artifact_replay_chain_digest": "ce4dcb296fff85fc084314e7701637d81d31922b3f84ca0aa113fc0d91e8f88b",
    "artifact_replay_gate": "pass",
    "becoming_class_status": "reusable_class",
    "boundary_rung": "recurrence_or_continuation",
    "candidate_identity_carrier_type": "coherence_basin",
    "claim_ceiling": "source_backed_reflexively_self_maintaining_identity_candidate",
    "claim_flags": {
      "agency_claim_allowed": false,
      "agentic_like_claim_allowed": false,
      "ant_colony_claim_allowed": false,
      "biological_claim_allowed": false,
      "goal_proxy_regulation_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "locomotion_like_claim_allowed": false,
      "memory_or_trail_claim_allowed": false,
      "movement_claim_allowed": false,
      "personhood_claim_allowed": false,
      "rc_identity_collapse_claim_allowed": false,
      "semantic_choice_claim_allowed": false,
      "unrestricted_identity_claim_allowed": false,
      "unrestricted_movement_claim_allowed": false
    },
    "compatibility_gate": "blocked",
    "compatibility_primary_blocker": "compatibility_deferred_to_iteration_9",
    "compatibility_status": "deferred_to_iteration_9_c3_t7",
    "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
    "core_membership_source_backed": false,
    "derived_id_ceiling": "ID5",
    "experiment_local_observables_used": [
      "artifact_derived_processed_packet_rows",
      "artifact_derived_state_rows",
      "later_cycle_producer_record_consumes_updated_digest",
      "n07_i7b_proper_time_identity_persistence_evaluator_v1",
      "n07_i7b_source_backed_t6_reflexive_closure_event_0001",
      "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
      "n07_i8_artifact_only_replay_chain_v1",
      "n07_i8_c1_t6_closeout_row_v1",
      "n07_i8_source_control_replay_rows_v1"
    ],
    "experiment_local_packet_application": true,
    "gate_vector": {
      "artifact_replay": "pass",
      "attractivity": "pass",
      "compatibility": "blocked",
      "invariance": "pass",
      "lineage_current": "pass",
      "reflexive_closure": "pass",
      "stability": "pass",
      "support": "pass"
    },
    "id6_blocker": "c3_t7_compatibility_not_yet_tested",
    "id6_not_claimed": true,
    "id_level": "ID5",
    "identity_acceptance_claim_allowed": false,
    "identity_acceptance_event_emitted": false,
    "identity_carrier_surface": "runtime_coherence_basin",
    "implementation_surface": "artifact_only_validator",
    "native_observables_used": [
      "node_plus_packet_budget_accounting",
      "source_row_digests",
      "surface_lineage_transport_context",
      "topology_state_reabsorption_context"
    ],
    "native_policy_blockers": [
      "c3_t7_compatibility_not_yet_tested",
      "native_attractor_neighborhood_policy_missing",
      "native_basin_potential_policy_missing",
      "native_identity_invariance_policy_missing",
      "native_rc_identity_support_area_policy_not_available",
      "native_reflexive_closure_policy_missing"
    ],
    "native_runtime_reflexive_closure_observed": false,
    "native_support_status": "mixed_native_experiment_local",
    "naturalization_rung": "Nat0_probe_dependent_expression",
    "personhood_claim_allowed": false,
    "primary_blocker": null,
    "probe_role": "diagnostic_probe",
    "rc_identity_collapse_claim_allowed": false,
    "row_id": "n07_i8_c1_t6_artifact_replay_closeout_row_v1",
    "runtime_family": "hybrid_lgrc9v3_experiment_local",
    "source_artifact_sha256": {
      "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json": "56e27d9b0783ac33f97ab06e42e64cf153e9289a00b07e77e02ff17e0ad6b0c2",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json": "9fe490f364545dd9efe90f25be5a7196747df812b469e2c1e7282576da277035",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json": "bd5eb02a7ba419d6837340b46c537e5201353aa27e9619abbe7aaa1886bce97c",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json": "7da0bfbc044eb8589d0d4749d59fe21b72dc095299546807b1d46058c07c2ebc",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json": "418334600c32cc2bda5ff4343ae08fcf6b49ee3cf248fca9249846d15f7da6f0",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json": "7134db432a859e9e94e191c525ba92f5f84e94e787246bc11b668f9343f92fcc",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json": "59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json": "617bb86c85ccc4a653280237f51b8749ecda50670b3df2efa9afc01b39464b33",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_3_id1_support_area_candidate.md": "172854c3736d860f9e5ef4ea3a43d2843dc8fc5ae47c750da97b6551ff965ac2",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_4_id2_stability_candidate.md": "e5e07fe53c9028247d376ee1947788ca20db3328893202752b95ce1c0708ce4f",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_5b_id3_attractivity_stress_candidate.md": "df11920ef76e1aa7a71811378131123eb95e9f351b1e498e7045dbe187804fb7",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md": "5ef2dda323b44c4e6c2cd026773a90e0dbe2d41e8b7c28671e8dc372a8a1a8c8",
      "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_7b_source_backed_t6_reflexive_closure.md": "5da517fd853adfadc69b753c0cdb55c28867593a825a6100c64fc36661f228c0"
    },
    "source_artifacts": [
      {
        "name": "n07_fixture_manifest_v1",
        "object_digest": "89d46bf941cb40f359b99381f0c7d1b391f67ae3eb07955ec850a8c03a242e5e",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json",
        "sha256": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603"
      },
      {
        "name": "iteration_1",
        "object_digest": "b38d2b7945724fad281d0c9db493ce887d2867059f4f6258830780cc4e1eee0b",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json",
        "schema": "n07_iteration_1_baseline_theory_schema_inventory_v1",
        "sha256": "56e27d9b0783ac33f97ab06e42e64cf153e9289a00b07e77e02ff17e0ad6b0c2",
        "status": "passed"
      },
      {
        "name": "iteration_2",
        "object_digest": "df89737f45e8f2eaaa4916bd6c1f2d6a8878758532846e3aac24fb217576cfdf",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json",
        "schema": "n07_iteration_2_fixture_manifest_validation_v1",
        "sha256": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
        "status": "passed"
      },
      {
        "name": "iteration_3",
        "object_digest": "f664b0eac297f7a96216ede1524b62ff3913aafaab7ec6e841e7ca48cf44bc39",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json",
        "schema": "n07_iteration_3_id1_support_area_candidate_v1",
        "sha256": "9fe490f364545dd9efe90f25be5a7196747df812b469e2c1e7282576da277035",
        "status": "passed"
      },
      {
        "name": "iteration_4",
        "object_digest": "7877a10caa45ade0ad864bc948d1769c9cf6f4126e5ac4d3126827a8c0dc02c8",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json",
        "schema": "n07_iteration_4_id2_stability_candidate_v1",
        "sha256": "bd5eb02a7ba419d6837340b46c537e5201353aa27e9619abbe7aaa1886bce97c",
        "status": "passed"
      },
      {
        "name": "iteration_5",
        "object_digest": "d97b407b5476c5f87b44ac2bdf684875c492645d3109a525dca6e454288b2539",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json",
        "schema": "n07_iteration_5_id3_attractivity_candidate_v1",
        "sha256": "7da0bfbc044eb8589d0d4749d59fe21b72dc095299546807b1d46058c07c2ebc",
        "status": "passed"
      },
      {
        "name": "iteration_5b",
        "object_digest": "3fa1077854a8a41b862e2af97cf4f468a6304383a5c2e083efabf1d72b006475",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json",
        "schema": "n07_iteration_5b_id3_attractivity_stress_candidate_v1",
        "sha256": "418334600c32cc2bda5ff4343ae08fcf6b49ee3cf248fca9249846d15f7da6f0",
        "status": "passed"
      },
      {
        "name": "iteration_6",
        "object_digest": "881d6c6f7844ce8ab47e448f79a4575d2efdbd324b64bdd29be65e8207a993aa",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json",
        "schema": "n07_iteration_6_id4_invariance_candidate_v1",
        "sha256": "7134db432a859e9e94e191c525ba92f5f84e94e787246bc11b668f9343f92fcc",
        "status": "passed"
      },
      {
        "name": "iteration_6b",
        "object_digest": "778723022c1f69bd00961a0a52c64f22059a80dbf506dbdc8e6422261cbfb8b4",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
        "schema": "n07_iteration_6b_id4_topology_split_birth_invariance_stress_v1",
        "sha256": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
        "status": "passed"
      },
      {
        "name": "iteration_7",
        "object_digest": "d520a7db44b48dc106723e65b6018d41e2bb9008506cc4e20f66f5738060ebc2",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json",
        "schema": "n07_iteration_7_id5_reflexive_closure_persistence_v1",
        "sha256": "59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e",
        "status": "passed"
      },
      {
        "name": "iteration_7b",
        "object_digest": "c4a3bda9d46639b1cc832f43be9bee26ec25220e09785be5714c7b99c2dec4f2",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json",
        "schema": "n07_iteration_7b_source_backed_t6_reflexive_closure_v1",
        "sha256": "617bb86c85ccc4a653280237f51b8749ecda50670b3df2efa9afc01b39464b33",
        "status": "passed"
      }
    ],
    "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
    "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
    "source_id5_candidate_row_digest": "88f284dd115bcabc77db0e5cea038f1c7c043abfbd720afcf94145839e2c0e56",
    "source_id5_candidate_row_id": "n07_i7b_id5_source_backed_t6_candidate_row_v1",
    "source_reports": [
      {
        "name": "iteration_3",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_3_id1_support_area_candidate.md",
        "sha256": "172854c3736d860f9e5ef4ea3a43d2843dc8fc5ae47c750da97b6551ff965ac2"
      },
      {
        "name": "iteration_4",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_4_id2_stability_candidate.md",
        "sha256": "e5e07fe53c9028247d376ee1947788ca20db3328893202752b95ce1c0708ce4f"
      },
      {
        "name": "iteration_5b",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_5b_id3_attractivity_stress_candidate.md",
        "sha256": "df11920ef76e1aa7a71811378131123eb95e9f351b1e498e7045dbe187804fb7"
      },
      {
        "name": "iteration_6b",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md",
        "sha256": "5ef2dda323b44c4e6c2cd026773a90e0dbe2d41e8b7c28671e8dc372a8a1a8c8"
      },
      {
        "name": "iteration_7b",
        "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_7b_source_backed_t6_reflexive_closure.md",
        "sha256": "5da517fd853adfadc69b753c0cdb55c28867593a825a6100c64fc36661f228c0"
      }
    ],
    "source_t6_record_digest": "f8852c2e90beae00489abd6ec2d93c2b5bba6a268826c6baeb61d8fad809f0f0",
    "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "support_area_id": "n07_support_area_A_v1",
    "support_dependency_status": "probe_dependent",
    "t4_no_mutation_baseline_deferred": true,
    "topology_family_id": "n07_T6_reflexive_closure",
    "unrestricted_identity_claim_allowed": false,
    "visual_is_evidence_source": false,
    "visual_reference": null,
    "withdrawal_test_status": "not_tested"
  },
  "compatibility_gate": "blocked",
  "compatibility_primary_blocker": "compatibility_deferred_to_iteration_9",
  "compatibility_status": "deferred_to_iteration_9_c3_t7",
  "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
  "core_membership_source_backed": false,
  "derived_id_ceiling": "ID5",
  "experiment_local_observables_used": [
    "artifact_derived_processed_packet_rows",
    "artifact_derived_state_rows",
    "later_cycle_producer_record_consumes_updated_digest",
    "n07_i7b_proper_time_identity_persistence_evaluator_v1",
    "n07_i7b_source_backed_t6_reflexive_closure_event_0001",
    "n07_i7b_source_backed_t6_reflexive_closure_record_v1",
    "n07_i8_artifact_only_replay_chain_v1",
    "n07_i8_c1_t6_closeout_row_v1",
    "n07_i8_source_control_replay_rows_v1"
  ],
  "experiment_local_packet_application": true,
  "gate_vector": {
    "artifact_replay": "pass",
    "attractivity": "pass",
    "compatibility": "blocked",
    "invariance": "pass",
    "lineage_current": "pass",
    "reflexive_closure": "pass",
    "stability": "pass",
    "support": "pass"
  },
  "id6_blocker": "c3_t7_compatibility_not_yet_tested",
  "id6_not_claimed": true,
  "id_level": "ID5",
  "identity_acceptance_claim_allowed": false,
  "identity_acceptance_event_emitted": false,
  "identity_carrier_surface": "runtime_coherence_basin",
  "implementation_surface": "artifact_only_validator",
  "native_observables_used": [
    "node_plus_packet_budget_accounting",
    "source_row_digests",
    "surface_lineage_transport_context",
    "topology_state_reabsorption_context"
  ],
  "native_policy_blockers": [
    "c3_t7_compatibility_not_yet_tested",
    "native_attractor_neighborhood_policy_missing",
    "native_basin_potential_policy_missing",
    "native_identity_invariance_policy_missing",
    "native_rc_identity_support_area_policy_not_available",
    "native_reflexive_closure_policy_missing"
  ],
  "native_runtime_reflexive_closure_observed": false,
  "native_support_status": "mixed_native_experiment_local",
  "naturalization_rung": "Nat0_probe_dependent_expression",
  "personhood_claim_allowed": false,
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "rc_identity_collapse_claim_allowed": false,
  "row_id": "n07_i8_c1_t6_artifact_replay_closeout_row_v1",
  "runtime_family": "hybrid_lgrc9v3_experiment_local",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json": "56e27d9b0783ac33f97ab06e42e64cf153e9289a00b07e77e02ff17e0ad6b0c2",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json": "9fe490f364545dd9efe90f25be5a7196747df812b469e2c1e7282576da277035",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json": "bd5eb02a7ba419d6837340b46c537e5201353aa27e9619abbe7aaa1886bce97c",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json": "7da0bfbc044eb8589d0d4749d59fe21b72dc095299546807b1d46058c07c2ebc",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json": "418334600c32cc2bda5ff4343ae08fcf6b49ee3cf248fca9249846d15f7da6f0",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json": "7134db432a859e9e94e191c525ba92f5f84e94e787246bc11b668f9343f92fcc",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json": "59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json": "617bb86c85ccc4a653280237f51b8749ecda50670b3df2efa9afc01b39464b33",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_3_id1_support_area_candidate.md": "172854c3736d860f9e5ef4ea3a43d2843dc8fc5ae47c750da97b6551ff965ac2",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_4_id2_stability_candidate.md": "e5e07fe53c9028247d376ee1947788ca20db3328893202752b95ce1c0708ce4f",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_5b_id3_attractivity_stress_candidate.md": "df11920ef76e1aa7a71811378131123eb95e9f351b1e498e7045dbe187804fb7",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md": "5ef2dda323b44c4e6c2cd026773a90e0dbe2d41e8b7c28671e8dc372a8a1a8c8",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_7b_source_backed_t6_reflexive_closure.md": "5da517fd853adfadc69b753c0cdb55c28867593a825a6100c64fc36661f228c0"
  },
  "source_artifacts": [
    {
      "name": "n07_fixture_manifest_v1",
      "object_digest": "89d46bf941cb40f359b99381f0c7d1b391f67ae3eb07955ec850a8c03a242e5e",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json",
      "sha256": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603"
    },
    {
      "name": "iteration_1",
      "object_digest": "b38d2b7945724fad281d0c9db493ce887d2867059f4f6258830780cc4e1eee0b",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_1_baseline_theory_schema_inventory.json",
      "schema": "n07_iteration_1_baseline_theory_schema_inventory_v1",
      "sha256": "56e27d9b0783ac33f97ab06e42e64cf153e9289a00b07e77e02ff17e0ad6b0c2",
      "status": "passed"
    },
    {
      "name": "iteration_2",
      "object_digest": "df89737f45e8f2eaaa4916bd6c1f2d6a8878758532846e3aac24fb217576cfdf",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json",
      "schema": "n07_iteration_2_fixture_manifest_validation_v1",
      "sha256": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
      "status": "passed"
    },
    {
      "name": "iteration_3",
      "object_digest": "f664b0eac297f7a96216ede1524b62ff3913aafaab7ec6e841e7ca48cf44bc39",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json",
      "schema": "n07_iteration_3_id1_support_area_candidate_v1",
      "sha256": "9fe490f364545dd9efe90f25be5a7196747df812b469e2c1e7282576da277035",
      "status": "passed"
    },
    {
      "name": "iteration_4",
      "object_digest": "7877a10caa45ade0ad864bc948d1769c9cf6f4126e5ac4d3126827a8c0dc02c8",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json",
      "schema": "n07_iteration_4_id2_stability_candidate_v1",
      "sha256": "bd5eb02a7ba419d6837340b46c537e5201353aa27e9619abbe7aaa1886bce97c",
      "status": "passed"
    },
    {
      "name": "iteration_5",
      "object_digest": "d97b407b5476c5f87b44ac2bdf684875c492645d3109a525dca6e454288b2539",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5_id3_attractivity_candidate.json",
      "schema": "n07_iteration_5_id3_attractivity_candidate_v1",
      "sha256": "7da0bfbc044eb8589d0d4749d59fe21b72dc095299546807b1d46058c07c2ebc",
      "status": "passed"
    },
    {
      "name": "iteration_5b",
      "object_digest": "3fa1077854a8a41b862e2af97cf4f468a6304383a5c2e083efabf1d72b006475",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_5b_id3_attractivity_stress_candidate.json",
      "schema": "n07_iteration_5b_id3_attractivity_stress_candidate_v1",
      "sha256": "418334600c32cc2bda5ff4343ae08fcf6b49ee3cf248fca9249846d15f7da6f0",
      "status": "passed"
    },
    {
      "name": "iteration_6",
      "object_digest": "881d6c6f7844ce8ab47e448f79a4575d2efdbd324b64bdd29be65e8207a993aa",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6_id4_invariance_candidate.json",
      "schema": "n07_iteration_6_id4_invariance_candidate_v1",
      "sha256": "7134db432a859e9e94e191c525ba92f5f84e94e787246bc11b668f9343f92fcc",
      "status": "passed"
    },
    {
      "name": "iteration_6b",
      "object_digest": "778723022c1f69bd00961a0a52c64f22059a80dbf506dbdc8e6422261cbfb8b4",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_6b_id4_topology_split_birth_invariance_stress.json",
      "schema": "n07_iteration_6b_id4_topology_split_birth_invariance_stress_v1",
      "sha256": "50fec7cad7be08cb94e0b467e1700ac4350c77aca1f13017ca6ad68912a16f77",
      "status": "passed"
    },
    {
      "name": "iteration_7",
      "object_digest": "d520a7db44b48dc106723e65b6018d41e2bb9008506cc4e20f66f5738060ebc2",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7_id5_reflexive_closure_persistence.json",
      "schema": "n07_iteration_7_id5_reflexive_closure_persistence_v1",
      "sha256": "59b6a2dd5f0b88abe453997e74263ef4cf01ce629f975b0fb6f1712e98dde15e",
      "status": "passed"
    },
    {
      "name": "iteration_7b",
      "object_digest": "c4a3bda9d46639b1cc832f43be9bee26ec25220e09785be5714c7b99c2dec4f2",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_7b_source_backed_t6_reflexive_closure.json",
      "schema": "n07_iteration_7b_source_backed_t6_reflexive_closure_v1",
      "sha256": "617bb86c85ccc4a653280237f51b8749ecda50670b3df2efa9afc01b39464b33",
      "status": "passed"
    }
  ],
  "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
  "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
  "source_id5_candidate_row_digest": "88f284dd115bcabc77db0e5cea038f1c7c043abfbd720afcf94145839e2c0e56",
  "source_id5_candidate_row_id": "n07_i7b_id5_source_backed_t6_candidate_row_v1",
  "source_reports": [
    {
      "name": "iteration_3",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_3_id1_support_area_candidate.md",
      "sha256": "172854c3736d860f9e5ef4ea3a43d2843dc8fc5ae47c750da97b6551ff965ac2"
    },
    {
      "name": "iteration_4",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_4_id2_stability_candidate.md",
      "sha256": "e5e07fe53c9028247d376ee1947788ca20db3328893202752b95ce1c0708ce4f"
    },
    {
      "name": "iteration_5b",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_5b_id3_attractivity_stress_candidate.md",
      "sha256": "df11920ef76e1aa7a71811378131123eb95e9f351b1e498e7045dbe187804fb7"
    },
    {
      "name": "iteration_6b",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_6b_id4_topology_split_birth_invariance_stress.md",
      "sha256": "5ef2dda323b44c4e6c2cd026773a90e0dbe2d41e8b7c28671e8dc372a8a1a8c8"
    },
    {
      "name": "iteration_7b",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_7b_source_backed_t6_reflexive_closure.md",
      "sha256": "5da517fd853adfadc69b753c0cdb55c28867593a825a6100c64fc36661f228c0"
    }
  ],
  "source_t6_record_digest": "f8852c2e90beae00489abd6ec2d93c2b5bba6a268826c6baeb61d8fad809f0f0",
  "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "t4_no_mutation_baseline_deferred": true,
  "topology_family_id": "n07_T6_reflexive_closure",
  "unrestricted_identity_claim_allowed": false,
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Artifact Replay Chain

```json
{
  "artifact_only": true,
  "artifact_replay_gate": "pass",
  "budget_error_max": 0.0,
  "claim_flags_all_false": true,
  "compatibility_gate": "deferred_to_iteration_9",
  "private_runtime_state_used": false,
  "runtime_state_used": false,
  "scheduler_order": [
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26
  ],
  "scheduler_order_monotonic": true,
  "semantic_consistency": {
    "boundary_rungs_allowed": true,
    "carrier_kind_consistent": true,
    "claim_flags_remain_false": true,
    "id_progression": [
      "ID1",
      "ID2",
      "ID3",
      "ID4",
      "ID5"
    ],
    "id_progression_matches_expected": true,
    "identity_surface_consistent": true,
    "pre_transport_support_digest_consistent": true,
    "semantic_consistency_passed": true,
    "support_area_id_consistent": true,
    "t6_support_digest_is_lineage_transport_successor": true,
    "t6_support_digest_matches_6b_birth_support": true
  },
  "source_link_checks": {
    "iteration_4_links_iteration_3_summary": true,
    "iteration_5_links_iteration_4_summary": true,
    "iteration_5b_links_iteration_5_summary": true,
    "iteration_6_links_iteration_5b_summary": true,
    "iteration_6b_links_iteration_6_summary": true,
    "iteration_7b_embeds_iteration_6b": true,
    "iteration_7b_embeds_iteration_7": true
  },
  "source_links_passed": true,
  "source_row_digest_matches": true,
  "source_rows": [
    {
      "boundary_rung": "eligible_state",
      "candidate_identity_carrier_type": "coherence_basin",
      "claim_flags_all_false": true,
      "composite_topology_id": null,
      "digest_key": "id1_candidate_row_digest",
      "digest_match": true,
      "expected_digest": "f3f9c176531c9d782ebc0b9b22eafb2e83e6a03879cadceae4ef27520b7d97e9",
      "gate": "support",
      "identity_carrier_surface": "runtime_coherence_basin",
      "native_support_status": "experiment_local",
      "recomputed_digest": "f3f9c176531c9d782ebc0b9b22eafb2e83e6a03879cadceae4ef27520b7d97e9",
      "row_derived_id_ceiling": "ID1",
      "row_id": "n07_i3_id1_support_area_candidate_row_v1",
      "row_key": "id1_candidate_row",
      "rung": "ID1",
      "source_artifact_schema": "n07_iteration_3_id1_support_area_candidate_v1",
      "source_context_composite_topology_id": null,
      "source_context_topology_family_id": null,
      "source_iteration": "iteration_3",
      "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
      "support_area_id": "n07_support_area_A_v1",
      "topology_family_id": "n07_T1_support_area_minimal"
    },
    {
      "boundary_rung": "substrate_consequence",
      "candidate_identity_carrier_type": "coherence_basin",
      "claim_flags_all_false": true,
      "composite_topology_id": null,
      "digest_key": "id2_candidate_row_digest",
      "digest_match": true,
      "expected_digest": "5370ea86856620fa283c12a1a1f2ae2dda7cb031511b6c3e7bd7918c44fa8226",
      "gate": "stability",
      "identity_carrier_surface": "runtime_coherence_basin",
      "native_support_status": "experiment_local",
      "recomputed_digest": "5370ea86856620fa283c12a1a1f2ae2dda7cb031511b6c3e7bd7918c44fa8226",
      "row_derived_id_ceiling": "ID2",
      "row_id": "n07_i4_id2_stability_candidate_row_v1",
      "row_key": "id2_candidate_row",
      "rung": "ID2",
      "source_artifact_schema": "n07_iteration_4_id2_stability_candidate_v1",
      "source_context_composite_topology_id": null,
      "source_context_topology_family_id": null,
      "source_iteration": "iteration_4",
      "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
      "support_area_id": "n07_support_area_A_v1",
      "topology_family_id": "n07_T2_stable_well_basin"
    },
    {
      "boundary_rung": "structured_consequence",
      "candidate_identity_carrier_type": "coherence_basin",
      "claim_flags_all_false": true,
      "composite_topology_id": null,
      "digest_key": "id3_stress_candidate_row_digest",
      "digest_match": true,
      "expected_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
      "gate": "attractivity",
      "identity_carrier_surface": "runtime_coherence_basin",
      "native_support_status": "experiment_local",
      "recomputed_digest": "7b299541e9450501c6748398fff9b0a306fb287c397a97aa3d9f041aa2f62431",
      "row_derived_id_ceiling": "ID3",
      "row_id": "n07_i5b_id3_attractivity_stress_candidate_row_v1",
      "row_key": "id3_attractivity_stress_candidate_row",
      "rung": "ID3",
      "source_artifact_schema": "n07_iteration_5b_id3_attractivity_stress_candidate_v1",
      "source_context_composite_topology_id": null,
      "source_context_topology_family_id": null,
      "source_iteration": "iteration_5b",
      "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
      "support_area_id": "n07_support_area_A_v1",
      "topology_family_id": "n07_T3_attractor_neighborhood"
    },
    {
      "boundary_rung": "recurrence_or_continuation",
      "candidate_identity_carrier_type": "coherence_basin",
      "claim_flags_all_false": true,
      "composite_topology_id": null,
      "digest_key": "id4_stress_candidate_row_digest",
      "digest_match": true,
      "expected_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
      "gate": "invariance_and_lineage_current",
      "identity_carrier_surface": "runtime_coherence_basin",
      "native_support_status": "mixed_native_experiment_local",
      "recomputed_digest": "e3042131c1b2beffb797ffb371f2afa7380ffdf2e91f8977dda0eeaf2788eeba",
      "row_derived_id_ceiling": "ID4",
      "row_id": "n07_i6b_id4_split_birth_invariance_stress_candidate_row_v1",
      "row_key": "id4_topology_stress_candidate_row",
      "rung": "ID4",
      "source_artifact_schema": "n07_iteration_6b_id4_topology_split_birth_invariance_stress_v1",
      "source_context_composite_topology_id": null,
      "source_context_topology_family_id": null,
      "source_iteration": "iteration_6b",
      "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
      "support_area_id": "n07_support_area_A_v1",
      "topology_family_id": "n07_T5_lineage_current_invariance"
    },
    {
      "boundary_rung": "recurrence_or_continuation",
      "candidate_identity_carrier_type": "coherence_basin",
      "claim_flags_all_false": true,
      "composite_topology_id": "n07_C1_recurrent_single_basin_identity_candidate",
      "digest_key": "id5_candidate_row_digest",
      "digest_match": true,
      "expected_digest": "88f284dd115bcabc77db0e5cea038f1c7c043abfbd720afcf94145839e2c0e56",
      "gate": "reflexive_closure",
      "identity_carrier_surface": "runtime_coherence_basin",
      "native_support_status": "mixed_native_experiment_local",
      "recomputed_digest": "88f284dd115bcabc77db0e5cea038f1c7c043abfbd720afcf94145839e2c0e56",
      "row_derived_id_ceiling": "ID5",
      "row_id": "n07_i7b_id5_source_backed_t6_candidate_row_v1",
      "row_key": "id5_source_backed_t6_candidate_row",
      "rung": "ID5",
      "source_artifact_schema": "n07_iteration_7b_source_backed_t6_reflexive_closure_v1",
      "source_context_composite_topology_id": "n07_C2_lineage_current_topology_mutating_identity_candidate",
      "source_context_topology_family_id": "n07_T5_lineage_current_invariance",
      "source_iteration": "iteration_7b",
      "support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
      "support_area_id": "n07_support_area_A_v1",
      "topology_family_id": "n07_T6_reflexive_closure"
    }
  ],
  "support_area_digest_replay": {
    "digest_method": "sha256_canonical_json_sorted_keys",
    "id1_recomputed_support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "id1_source_support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "id1_support_area_digest_matches": true,
    "id1_support_area_row_digest_matches": true,
    "manifest_declared_support_area_digest": "0942731278e985c654cb39323ee9ac78550e293d6183c927b386de93ac02c887",
    "manifest_recomputed_support_area_digest": "0942731278e985c654cb39323ee9ac78550e293d6183c927b386de93ac02c887",
    "manifest_support_area_digest_matches": true,
    "required_input_fields": [
      "support_area_id",
      "candidate_identity_carrier_type",
      "support_node_ids",
      "support_edge_ids",
      "support_port_ids",
      "lineage_status",
      "lineage_map_digest",
      "support_surface_digest",
      "event_time_key",
      "scheduler_event_index",
      "budget_surface",
      "budget_before",
      "budget_after",
      "budget_error"
    ],
    "transported_t6_support_area_digest": "565a3f024ebb217cb62b0cd9aaa2c816ff1613d74cee6b65b9a6d94edb8a3075",
    "transported_t6_support_area_digest_linked": true,
    "transported_t6_support_area_digest_matches_6b_birth_digest": true,
    "transported_t6_support_area_digest_source": "iteration_7b.source_backed_t6_chain.birth_lineage_context.transported_support_digest"
  },
  "t6_digest_checks": {
    "proper_time_evaluation_digest_match": true,
    "source_backed_t6_chain_digest_match": true,
    "source_backed_t6_record_digest_match": true,
    "t6_record_digest_input_match": true
  },
  "t6_digest_checks_passed": true
}
```

## Controls

| Control | Status | Primary blocker | Scope |
|---|---|---|---|
| `missing_support_area` | `blocked` | `missing_support_area` | `iteration_8_artifact_replay_closeout` |
| `unstable_basin_no_local_well` | `blocked` | `unstable_basin_no_local_well` | `iteration_8_artifact_replay_closeout` |
| `non_attractive_flux` | `blocked` | `non_attractive_flux` | `iteration_8_artifact_replay_closeout` |
| `lineage_map_scrambled` | `blocked` | `lineage_map_scrambled` | `iteration_8_artifact_replay_closeout` |
| `no_reentry` | `blocked` | `no_reentry` | `iteration_8_artifact_replay_closeout` |
| `closure_not_consumed_by_later_cycle` | `blocked` | `closure_not_consumed_by_later_cycle` | `iteration_8_artifact_replay_closeout` |
| `hidden_support_field` | `blocked` | `hidden_support_field` | `iteration_8_artifact_replay_closeout` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `iteration_8_artifact_replay_closeout` |
| `unauthorized_identity_acceptance_event` | `blocked` | `unauthorized_identity_acceptance_event` | `iteration_8_artifact_replay_closeout` |
| `identity_claim_promotion` | `blocked` | `identity_claim_promotion` | `iteration_8_artifact_replay_closeout` |
| `agency_claim_promotion` | `blocked` | `agency_claim_promotion` | `iteration_8_artifact_replay_closeout` |
| `destructive_interference` | `deferred` | `destructive_interference` | `deferred_to_iteration_9_c3_t7_compatibility` |
| `ambiguous_overlap` | `deferred` | `ambiguous_overlap` | `deferred_to_iteration_9_c3_t7_compatibility` |
| `wrong_basin` | `deferred` | `wrong_basin` | `deferred_to_iteration_9_c3_t7_compatibility` |
| `identity_threshold_missing` | `schema_guard_declared` | `identity_threshold_missing` | `manifest_threshold_schema_guard_validated_in_iteration_2` |

## Checks

| Check | Passed |
|---|---:|
| `activity_history_digest_recomputed` | `True` |
| `activity_history_scope_complete` | `True` |
| `actual_lgrc_step_not_claimed` | `True` |
| `artifact_only` | `True` |
| `artifact_replay_passed` | `True` |
| `becoming_fields_preserved` | `True` |
| `budget_exact` | `True` |
| `claim_flags_false` | `True` |
| `closeout_boundary_rung_allowed` | `True` |
| `closeout_implementation_surface_allowed` | `True` |
| `closeout_row_digest_recomputed` | `True` |
| `closeout_row_required_fields_present` | `True` |
| `closeout_runtime_family_allowed` | `True` |
| `compatibility_controls_deferred` | `True` |
| `compatibility_deferred` | `True` |
| `control_blockers_distinct` | `True` |
| `control_blockers_match_source_and_manifest` | `True` |
| `control_derived_ceilings_source_specific` | `True` |
| `id5_ceiling_frozen` | `True` |
| `identity_claims_blocked` | `True` |
| `identity_threshold_missing_guard_recorded` | `True` |
| `in_scope_controls_blocked` | `True` |
| `in_scope_controls_replayed_from_source_artifacts` | `True` |
| `next_iteration_is_c3` | `True` |
| `no_src_changes_required` | `True` |
| `scheduler_order_monotonic` | `True` |
| `semantic_consistency_passed` | `True` |
| `source_links_passed` | `True` |
| `source_outputs_passed` | `True` |
| `source_row_digest_matches` | `True` |
| `status_passed` | `True` |
| `support_area_digest_replay_passed` | `True` |
| `t4_deferral_preserved` | `True` |
| `t6_digest_checks_passed` | `True` |

## Artifact Digests

```json
{
  "artifact_replay_chain_digest": "ce4dcb296fff85fc084314e7701637d81d31922b3f84ca0aa113fc0d91e8f88b",
  "checks_digest": "fbb57232652c7f852e1b25953d5c7343a4a19e08bb86bb50350d5cf743ef00cd",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "closeout_row_artifact_digest": "127b268a9df06b80286829e6face9ec747f0071973f16ac6e97f3d16a93b9804",
  "closeout_row_digest": "6a074e6680fb3f7e80f63cdc8ecfc92066d811a3a8cb32284bd9e7334ed8e1d7",
  "control_rows_digest": "fa34172aff876c394e71d3eea68e7db52a5dbb51b1adea876190d9951f1decbe"
}
```

## Acceptance

Iteration 8 passes because the C1/T6 support, stability, attractivity,
invariance/lineage, reflexive-closure, and proper-time evidence chain replays
from artifacts only with exact budget accounting and clean claim boundaries.
The current ceiling remains ID5 because C3/T7 compatibility is deferred to
Iteration 9. No identity acceptance, RC identity collapse, agency, semantic
choice, biological identity, personhood, or unrestricted identity claim is
emitted.
