# N07 Iteration 3: ID1 Support-Area Candidate

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_3_id1_support_area_candidate.py
```

Iteration 3 emits a source-backed support-area candidate. It does not claim
identity acceptance, agency, native identity support, stability, attractivity,
invariance, reflexive closure, or compatibility.

## Execution Boundary

Iteration 3 runs zero LGRC `step()` cycles. The `scheduler_event_index = 0`
value in the source support event is a support-commit marker, not a runtime
simulation step. The support area is derived from the Iteration 2 fixture
manifest's declared support core, not discovered from dynamic stability.

```json
{
  "dynamic_coherence_observation_window": "not_run_iteration_3",
  "lgrc_step_invocations": 0,
  "scheduler_event_index_semantics": "support_commit_marker_not_runtime_step",
  "stability_deferred_to_iteration_4": true,
  "stability_probe_run": false,
  "step_cycles_run": 0,
  "support_area_derivation": "manifest_declared_support_core",
  "support_area_discovered_by_dynamics": false,
  "support_area_source": "iteration_2_fixture_manifest"
}
```

## Candidate Row

```json
{
  "activity_history_digest": "d466f715ab90f773499189d325d83a9006717d4e614206f3a6459280f74cabb8",
  "agency_claim_allowed": false,
  "becoming_class_status": "observation_tag",
  "boundary_rung": "eligible_state",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "support_area_candidate",
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
  "derived_id_ceiling": "ID1",
  "experiment_local_observables_used": [
    "n07_i3_support_surface_event_0001",
    "n07_i3_support_area_row_v1"
  ],
  "gate_vector": {
    "artifact_replay": "not_measured",
    "attractivity": "not_measured",
    "compatibility": "not_measured",
    "invariance": "not_measured",
    "lineage_current": "not_applicable",
    "reflexive_closure": "not_measured",
    "stability": "not_measured",
    "support": "pass"
  },
  "id_level": "ID1",
  "identity_acceptance_claim_allowed": false,
  "identity_carrier_surface": "runtime_coherence_basin",
  "implementation_surface": "experiment_local_identity_gate_record",
  "native_observables_used": [
    "manifest_declared_lgrc_node_ids",
    "manifest_declared_lgrc_edge_ids",
    "node_plus_packet_budget_accounting"
  ],
  "native_policy_blockers": [
    "native_rc_identity_support_area_policy_not_available"
  ],
  "native_support_status": "experiment_local",
  "naturalization_rung": "Nat0_probe_dependent_expression",
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "row_id": "n07_i3_id1_support_area_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26"
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
    }
  ],
  "source_reports": [
    {
      "name": "n07_iteration_2_fixture_manifest_validation_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_2_fixture_manifest_validation.md",
      "sha256": "e7796b9cf4467d48f5778fcdbadd75c6ce4d1742cdbfa9401b7036e834085a82"
    }
  ],
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_area_is_identity_claim": false,
  "support_dependency_status": "probe_dependent",
  "topology_family_id": "n07_T1_support_area_minimal",
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Support Area Row

```json
{
  "authored_central_node_is_identity_evidence": false,
  "budget_after": 6.0,
  "budget_before": 6.0,
  "budget_error": 0.0,
  "budget_surface": "node_plus_packet",
  "candidate_identity_carrier_type": "coherence_basin",
  "event_time_key": "n07_i3_t0_support_commit",
  "hidden_support_source_used": false,
  "identity_label_is_evidence": false,
  "lineage_map_digest": null,
  "lineage_status": "fixed_topology",
  "report_side_only": false,
  "runtime_visible": true,
  "scheduler_event_index": 0,
  "source_backed": true,
  "source_event_digest": "3944f51fcd6dad9b1b751ecd8899c501084d2a66d50e90c7bf6ff50950ef7baf",
  "source_event_id": "n07_i3_support_surface_event_0001",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_area_idempotency_key": {
    "event_time_key": "n07_i3_t0_support_commit",
    "lineage_status": "fixed_topology",
    "scheduler_event_index": 0,
    "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "support_area_id": "n07_support_area_A_v1"
  },
  "support_area_idempotency_key_digest": "1fe71a42bf1479b523d55e5f45754efa2d96141811238f6da1475b792d836460",
  "support_edge_ids": [
    1,
    2,
    3,
    5
  ],
  "support_gate": "pass",
  "support_node_ids": [
    2
  ],
  "support_port_ids": [
    "support_front",
    "support_rear",
    "support_reentry"
  ],
  "support_surface_digest": "3944f51fcd6dad9b1b751ecd8899c501084d2a66d50e90c7bf6ff50950ef7baf"
}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
| `label_only_null_topology` | `blocked` | `label_only_null_topology` | `ID0` |
| `missing_support_area` | `blocked` | `missing_support_area` | `ID0` |
| `external_label_only` | `blocked` | `external_label_only` | `ID0` |
| `hidden_support_field` | `blocked` | `hidden_support_field` | `ID0` |
| `duplicate_support_row` | `blocked` | `duplicate_support_row` | `ID0` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID0` |

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
| `controls_blocked` | `True` |
| `derived_ceiling_id1` | `True` |
| `evidence_only_surfaces_not_promoted` | `True` |
| `gate_vector_schema_matches_manifest` | `True` |
| `identity_acceptance_blocked` | `True` |
| `lineage_status_matches_manifest` | `True` |
| `native_support_not_overstated` | `True` |
| `native_support_status_value_allowed` | `True` |
| `no_src_changes_required` | `True` |
| `paired_negative_control_present` | `True` |
| `required_controls_present` | `True` |
| `source_event_runtime_visible` | `True` |
| `stability_deferred_to_iteration_4` | `True` |
| `status_passed` | `True` |
| `support_area_digest_matches` | `True` |
| `support_area_manifest_derived` | `True` |
| `support_area_not_identity_claim` | `True` |
| `support_area_source_backed` | `True` |
| `support_gate_passed` | `True` |
| `support_idempotency_key_declared` | `True` |
| `zero_step_cycles_recorded` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "2f9af72dbcf16a74f2aff435877cbf889eedd994371b39ae38418d26d72fdf4b",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "ea97659931681a32a80b00efcb10f85bf440d4fe346a3c65903bca7bc3cf7e0a",
  "execution_boundary_digest": "ea45152d1633d0f9cc314543b3d52a3accebbff059381f70003373e5bf3b50a1",
  "id1_candidate_row_digest": "f3f9c176531c9d782ebc0b9b22eafb2e83e6a03879cadceae4ef27520b7d97e9",
  "source_support_event_digest": "3944f51fcd6dad9b1b751ecd8899c501084d2a66d50e90c7bf6ff50950ef7baf",
  "support_area_row_digest": "9fdc6d7862752cfbca82baccb96d1c6b5814c53b7acbaf399c3adb4fca2fda4b"
}
```

## Acceptance

Iteration 3 passes because a support-area candidate is emitted from
runtime-visible, source-backed evidence with exact node-plus-packet budget
accounting, manifest-contract checks, and controls for label-only null topology,
missing support, external labels, hidden support, duplicate rows, and budget
discontinuity. The result is capped at ID1 and all
identity, identity-acceptance, agency, movement, biological, and unrestricted
claim flags remain false.
