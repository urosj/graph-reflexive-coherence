# N07 Iteration 4: ID2 Stability / Local Well Candidate

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_4_id2_stability_candidate.py
```

Iteration 4 applies the manifest-declared experiment-local stability proxy to
the Iteration 3 support-area candidate. It records source-backed proxy inputs,
a fixed threshold, and a recomputable stability score. It does not claim native
basin-potential support, identity acceptance, agency, attractivity, invariance,
reflexive closure, or compatibility.

## Stability Proxy Record

```json
{
  "budget_after": 6.0,
  "budget_before": 6.0,
  "budget_error": 0.0,
  "budget_surface": "node_plus_packet",
  "digest_scope": [
    "proxy_formula",
    "threshold",
    "input_fields",
    "support_area_digest"
  ],
  "hidden_potential_or_report_side_well_score_used": false,
  "hidden_report_side_score_allowed": false,
  "incoming_flux_to_support": 0.24,
  "input_fields": [
    "support_area_mass_before",
    "support_area_mass_after",
    "incoming_flux_to_support",
    "outgoing_flux_from_support"
  ],
  "local_inflow_dominance_score": 0.8571428571428572,
  "native_policy_available": false,
  "native_policy_blocker": "native_basin_potential_policy_missing",
  "outgoing_flux_from_support": 0.04,
  "posthoc_threshold_change_used": false,
  "proper_time_sample_count": 3,
  "proper_time_samples_digest": "d9a23d350752c561481e916be45ccb76eb482d06fca7a7b0ac314e714bea9fc5",
  "proper_time_window_id": "n07_i4_ptw_support_A_0_2",
  "proxy_formula": "0.5 * support_area_mass_retention + 0.5 * local_inflow_dominance_score",
  "record_id": "n07_i4_stability_proxy_record_v1",
  "record_kind": "experiment_local_stability_well_proxy_record",
  "report_side_only": false,
  "runtime_visible": true,
  "selected_proxy": "experiment_local_declared_second_difference_retention_proxy",
  "source_backed": true,
  "source_observation_event_digest": "7d5a85dd31170f2735e51b170710b0b452f35f6a1ba000a1ff8149c1334aa37e",
  "source_observation_event_id": "n07_i4_stability_observation_event_0001",
  "stability_gate": "pass",
  "stability_idempotency_key": {
    "event_time_key": "n07_i4_t1_stability_window",
    "proper_time_window_id": "n07_i4_ptw_support_A_0_2",
    "scheduler_event_index": 1,
    "stability_proxy_policy_id": "n07_stability_well_proxy_v1",
    "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb"
  },
  "stability_idempotency_key_digest": "c4e81140747495dcd230d0b5b214bff16d29fce24572f9d377ae5f07956b3122",
  "stability_proxy_policy_id": "n07_stability_well_proxy_v1",
  "stability_record_digest": "069482b59919fe556e2d7c266f8cdc145f365c872bd0c205676877aeff1ce83d",
  "stability_record_digest_input": {
    "incoming_flux_to_support": 0.24,
    "input_fields": [
      "support_area_mass_before",
      "support_area_mass_after",
      "incoming_flux_to_support",
      "outgoing_flux_from_support"
    ],
    "outgoing_flux_from_support": 0.04,
    "proper_time_window_id": "n07_i4_ptw_support_A_0_2",
    "proxy_formula": "0.5 * support_area_mass_retention + 0.5 * local_inflow_dominance_score",
    "source_id1_candidate_row_digest": "f3f9c176531c9d782ebc0b9b22eafb2e83e6a03879cadceae4ef27520b7d97e9",
    "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "support_area_mass_after": 0.96,
    "support_area_mass_before": 1.0,
    "threshold": 0.75
  },
  "stability_score": 0.9085714285714286,
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_mass_after": 0.96,
  "support_area_mass_before": 1.0,
  "support_area_mass_retention": 0.96,
  "threshold": 0.75,
  "thresholds_fixed_before_run": true
}
```

## Candidate Row

```json
{
  "activity_history_digest": "02ee3dbf82d6a8a18f69afe4d2c61c5cdc1b03a4b8473af08cd2f9024257e9b5",
  "agency_claim_allowed": false,
  "becoming_class_status": "observation_tag",
  "boundary_rung": "substrate_consequence",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "stable_basin_candidate",
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
  "composite_topology_id": null,
  "derived_id_ceiling": "ID2",
  "experiment_local_observables_used": [
    "n07_i4_stability_observation_event_0001",
    "n07_i4_stability_proxy_record_v1"
  ],
  "gate_vector": {
    "artifact_replay": "not_measured",
    "attractivity": "not_measured",
    "compatibility": "not_measured",
    "invariance": "not_measured",
    "lineage_current": "not_applicable",
    "reflexive_closure": "not_measured",
    "stability": "pass",
    "support": "pass"
  },
  "id_level": "ID2",
  "identity_acceptance_claim_allowed": false,
  "identity_carrier_surface": "runtime_coherence_basin",
  "implementation_surface": "experiment_local_identity_gate_record",
  "native_observables_used": [
    "manifest_declared_lgrc_node_ids",
    "manifest_declared_lgrc_edge_ids",
    "node_plus_packet_budget_accounting"
  ],
  "native_policy_blockers": [
    "native_basin_potential_policy_missing"
  ],
  "native_support_status": "experiment_local",
  "naturalization_rung": "Nat0_probe_dependent_expression",
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "row_id": "n07_i4_id2_stability_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json": "9fe490f364545dd9efe90f25be5a7196747df812b469e2c1e7282576da277035"
  },
  "source_artifacts": [
    {
      "name": "n07_fixture_manifest_v1",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json",
      "sha256": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603"
    },
    {
      "name": "n07_iteration_2_fixture_manifest_validation",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json",
      "sha256": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26"
    },
    {
      "id1_candidate_row_digest": "f3f9c176531c9d782ebc0b9b22eafb2e83e6a03879cadceae4ef27520b7d97e9",
      "name": "n07_iteration_3_id1_support_area_candidate",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_3_id1_support_area_candidate.json",
      "sha256": "9fe490f364545dd9efe90f25be5a7196747df812b469e2c1e7282576da277035",
      "status": "passed",
      "support_area_row_digest": "9fdc6d7862752cfbca82baccb96d1c6b5814c53b7acbaf399c3adb4fca2fda4b"
    }
  ],
  "source_reports": [
    {
      "name": "n07_iteration_3_id1_support_area_candidate_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_3_id1_support_area_candidate.md",
      "sha256": "172854c3736d860f9e5ef4ea3a43d2843dc8fc5ae47c750da97b6551ff965ac2"
    }
  ],
  "stability_is_identity_acceptance_claim": false,
  "stability_record_digest": "069482b59919fe556e2d7c266f8cdc145f365c872bd0c205676877aeff1ce83d",
  "stability_record_id": "n07_i4_stability_proxy_record_v1",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "topology_family_id": "n07_T2_stable_well_basin",
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
| `unstable_basin_no_local_well` | `blocked` | `unstable_basin_no_local_well` | `ID1` |
| `posthoc_threshold_change` | `blocked` | `posthoc_threshold_change` | `ID1` |
| `hidden_potential_or_report_side_well_score` | `blocked` | `hidden_potential_or_report_side_well_score` | `ID1` |
| `wrong_support_area` | `blocked` | `wrong_support_area` | `ID1` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID1` |

## Checks

| Check | Passed |
|---|---:|
| `becoming_method_values_allowed` | `True` |
| `budget_exact` | `True` |
| `candidate_carrier_is_coherence_basin` | `True` |
| `candidate_gate_matches_manifest` | `True` |
| `candidate_primary_metric_matches_manifest` | `True` |
| `candidate_target_id_matches_manifest` | `True` |
| `candidate_topology_family_matches_manifest` | `True` |
| `claim_flag_keys_match_manifest` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_distinct` | `True` |
| `control_ceilings_id1` | `True` |
| `controls_blocked` | `True` |
| `derived_ceiling_id2` | `True` |
| `evidence_only_surfaces_not_promoted` | `True` |
| `gate_vector_schema_matches_manifest` | `True` |
| `identity_acceptance_blocked` | `True` |
| `native_support_not_overstated` | `True` |
| `no_hidden_potential_or_report_side_score` | `True` |
| `no_src_changes_required` | `True` |
| `proper_time_flux_aggregates_match_samples` | `True` |
| `proper_time_sample_ordering_valid` | `True` |
| `proper_time_samples_source_backed` | `True` |
| `required_controls_present` | `True` |
| `source_id1_status_passed` | `True` |
| `source_id1_support_gate_passed` | `True` |
| `stability_inputs_source_backed` | `True` |
| `stability_not_identity_acceptance_claim` | `True` |
| `stability_proxy_formula_matches_manifest` | `True` |
| `stability_proxy_inputs_match_manifest` | `True` |
| `stability_score_above_threshold` | `True` |
| `stability_score_recomputed` | `True` |
| `stability_threshold_fixed` | `True` |
| `status_passed` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "a55708f5f3af0ca23becaf3e84b9cacf7e322c75fcd6b72a70a315a45df347f0",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "bc956df2a40021d1624e5ca09832e26d4ba9dc38039868b3b139af807a120403",
  "id2_candidate_row_digest": "5370ea86856620fa283c12a1a1f2ae2dda7cb031511b6c3e7bd7918c44fa8226",
  "source_id1_output_digest": "2fe9cbda285382c3e438cfd30a0b7ca3c3f1b8f836c9bcc046bba17f4667abee",
  "stability_observation_event_digest": "7d5a85dd31170f2735e51b170710b0b452f35f6a1ba000a1ff8149c1334aa37e",
  "stability_proxy_record_digest": "3dc60c7f6e60f429bbd0cbb86cf677337ec9386f3ca4a22e1b9556b9308835c0"
}
```

## Acceptance

Iteration 4 passes because the support area also satisfies the declared
stability proxy with source-backed inputs, a fixed threshold, exact
node-plus-packet budget accounting, and controls for unstable basin,
post-hoc threshold changes, hidden/report-side well scores, wrong support
area, and budget discontinuity. The result is capped at ID2/stable basin
candidate, remains experiment-local because native basin-potential support is
not available, and all identity-acceptance, agency, movement, biological, and
unrestricted claim flags remain false.
