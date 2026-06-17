# N16 Basin Boundary Requirements Matrix

Status: `passed`.

## Acceptance State

```text
accepted_full_control_matrix_no_ap6_closeout
```

Iteration 7 is a full control matrix synthesis over existing I3-I6 evidence. It does not create new B/C evidence cells and it does not close AP6.

## Requirement Summary

| Requirement | Supported By | Failed Or Limited By | Scope Limitations |
| --- | --- | --- | --- |
| minimum_coherence_margin_requirement | B2_C0, B2_C1, B3_C4, B4_C5 | B1_C0, B1_C2, B2_C2, B2_C4, B2_C5 | coherence_margin_is_artifact_metric_only, does_not_imply_identity_acceptance |
| minimum_internal_support_requirement | B2_C0, B2_C1, B3_C2, B3_C4, B4_C5 | B1_C2, B2_C2, B2_C4, B2_C5 | internal_support_is_not_native_support, phase8_remains_unopened |
| maximum_leakage_requirement | B2_C1, B3_C2, B3_C4, B4_C5 | B1_C2, B2_C2, B2_C4, B2_C5, B4_C2 | retained_flux_index_is_not_normalized_fraction, leakage_control_does_not_close_final_ap6 |
| flux_balance_requirement | B3_C2 | B1_C2, B2_C2, B4_C2 | B3_C2_is_C2_flux_repair_only, B3_C2_is_not_B3_C4_breach_repair_closeout |
| repair_reabsorption_requirement | B3_C4 | B2_C4 | B3_C4_is_not_autonomous_repair_or_native_reabsorption, B3_C4_does_not_close_final_AP6 |
| structured_external_coherence_rejection_requirement | B0_C3, B2_C3 | - | supported_null_row_supports_rejection_not_boundary, structured_external_coherence_is_not_self_region, no_C3_failure_cell_exists_all_C3_cells_correctly_reject |
| inter_basin_separation_requirement | B4_C5 | B2_C5, B4_C2 | B4_C5_is_artifact_level_separability_candidate_only, native_multi_basin_separability_not_supported, reverse_basin_perspective_replay_deferred_before_final_AP6 |

## Negative Controls

| Control | Status | Blocker | Stress | Schema Backed |
| --- | --- | --- | --- | --- |
| externally_supplied_boundary_control | blocked | externally_supplied_boundary_blocked | standard | true |
| post_hoc_boundary_label_control | blocked | post_hoc_boundary_label_blocked | standard | true |
| hidden_external_state_injection_control | blocked | hidden_external_state_injection_blocked | standard | true |
| resource_relabel_as_self_control | blocked | resource_relabel_as_self_blocked | standard | true |
| self_support_relabel_as_external_control | blocked | self_support_relabel_as_external_blocked | standard | true |
| untracked_boundary_crossing_control | blocked | untracked_boundary_crossing_blocked | standard | true |
| structured_external_coherence_rejection_control | blocked_or_rejected | structured_external_coherence_false_boundary_blocked | high | true |
| multi_basin_merge_control | blocked_or_recorded_failure | multi_basin_merge_or_leakage_recorded | high | true |
| identity_acceptance_relabel_control | blocked | identity_acceptance_relabel_blocked | standard | true |
| selfhood_personhood_relabel_control | blocked | selfhood_personhood_relabel_blocked | standard | true |
| semantic_goal_ownership_relabel_control | blocked | semantic_goal_ownership_relabel_blocked | standard | true |
| native_support_relabel_control | blocked | native_support_relabel_blocked | standard | true |
| stale_internal_state_control | blocked | stale_internal_state_blocked | standard | true |
| stale_external_state_control | blocked | stale_external_state_blocked | standard | true |
| missing_boundary_side_state_control | blocked | missing_boundary_side_state_blocked | standard | true |
| boundary_drift_outside_policy_control | blocked | boundary_drift_outside_policy_blocked | standard | true |
| artifact_only_replay_control | stable | artifact_replay_instability_blocks_ap6 | standard | true |
| snapshot_load_replay_control | stable | snapshot_load_instability_blocks_ap6 | standard | true |
| order_inversion_replay_control | stable | order_inversion_instability_blocks_ap6 | standard | true |
| duplicate_replay_control | stable | duplicate_replay_instability_blocks_ap6 | standard | false |

Duplicate replay is intentionally marked `schema_backed = false`: it is an I7 run-level replay extension, while the I2 schema backs the frozen row/control requirements. I8 must not collapse that distinction when classifying AP6.

## Aggregate Metric Scope

Global aggregate metrics are computed across every reused I3-I6 row, including null, rejected, and partial control rows. Supported boundary-candidate metrics exclude B0 active-null rows and unsupported rows.

```json
{
  "global_all_rows": {
    "maximum_leakage_ratio": 1.0,
    "minimum_coherence_margin": -0.92,
    "minimum_internal_support": 0.0,
    "row_scope": "all_reused_i3_to_i6_rows_including_controls"
  },
  "scope_note": "Global aggregate metrics are computed across every reused I3-I6 row, including null, rejected, and partial control rows. Supported boundary-candidate metrics exclude B0 active-null rows and unsupported rows.",
  "supported_boundary_candidate_rows": {
    "cell_sources": [
      {
        "cell_id": "B2_C0",
        "source_artifact_id": "n16_quiet_boundary_calibration"
      },
      {
        "cell_id": "B2_C0",
        "source_artifact_id": "n16_challenge_sweep_matrix"
      },
      {
        "cell_id": "B2_C1",
        "source_artifact_id": "n16_challenge_sweep_matrix"
      },
      {
        "cell_id": "B3_C2",
        "source_artifact_id": "n16_boundary_state_sweep_matrix"
      },
      {
        "cell_id": "B2_C1",
        "source_artifact_id": "n16_selected_interaction_probe_matrix"
      },
      {
        "cell_id": "B3_C4",
        "source_artifact_id": "n16_selected_interaction_probe_matrix"
      },
      {
        "cell_id": "B4_C5",
        "source_artifact_id": "n16_selected_interaction_probe_matrix"
      }
    ],
    "maximum_leakage_ratio": 0.118,
    "minimum_coherence_margin": 0.524,
    "minimum_internal_support": 0.85,
    "row_scope": "supported_B2_B3_B4_rows_only"
  }
}
```

## Cross-Iteration Metric Summary

| Cell | Source Artifact | Decision | Coherence Margin | Minimum Internal Support | Leakage | Stability | Repair | Reclosure | Basin Separation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2_C0 | n16_quiet_boundary_calibration | supported | 0.53 | - | 0.061644 | 1.0 | not_evaluated_in_quiet_calibration | - | not_evaluated_until_shared_medium_rows |
| B2_C0 | n16_challenge_sweep_matrix | supported | 0.53 | 0.86 | 0.061644 | 1.0 | 0.0 | - | 1.0 |
| B2_C1 | n16_challenge_sweep_matrix | supported | 0.532 | 0.85 | 0.078 | 0.9 | not_evaluated_by_c1 | - | not_evaluated_by_c1 |
| B2_C2 | n16_challenge_sweep_matrix | partial | 0.488 | 0.84 | 0.186 | 0.62 | not_evaluated_by_c2 | - | not_evaluated_by_c2 |
| B2_C2 | n16_boundary_state_sweep_matrix | partial | 0.488 | 0.84 | 0.186 | 0.62 | not_evaluated_by_b2_c2 | - | not_evaluated_by_b2_c2 |
| B3_C2 | n16_boundary_state_sweep_matrix | supported | 0.532 | 0.852 | 0.112 | 0.78 | 0.74 | - | not_evaluated_by_b3_c2 |
| B2_C1 | n16_selected_interaction_probe_matrix | supported | 0.532 | 0.85 | 0.078 | 0.9 | not_evaluated_by_c1 | - | not_evaluated_by_c1 |
| B3_C4 | n16_selected_interaction_probe_matrix | supported | 0.524 | 0.851 | 0.118 | 0.74 | 0.76 | 0.76 | not_evaluated_by_b3_c4 |
| B4_C5 | n16_selected_interaction_probe_matrix | supported | 0.552 | 0.854 | 0.108 | 0.76 | not_evaluated_by_b4_c5 | - | 0.74 |

## Replay Matrix

```json
{
  "artifact_only_replay": {
    "digest": "bd1bcbe9003eb256fcd9a6d0435fdcba44df35e57c24232c55848852c014e239",
    "hidden_runtime_dependency_detected": false,
    "meaning": "I7 uses serialized I3-I6 artifacts and configs only",
    "status": "stable"
  },
  "duplicate_replay": {
    "first_digest": "bd1bcbe9003eb256fcd9a6d0435fdcba44df35e57c24232c55848852c014e239",
    "meaning": "same accepted rows and requirement synthesis from same artifact inputs",
    "same_digest": true,
    "second_digest": "bd1bcbe9003eb256fcd9a6d0435fdcba44df35e57c24232c55848852c014e239",
    "status": "stable"
  },
  "order_inversion_replay": {
    "canonical_inverted_digest": "0b6aa3859869a70533ace7179a83be00ce962f6ddd10f50dc0877a205b467a11",
    "canonical_original_digest": "0b6aa3859869a70533ace7179a83be00ce962f6ddd10f50dc0877a205b467a11",
    "meaning": "row order does not create boundary evidence",
    "same_digest_after_canonical_ordering": true,
    "status": "stable"
  },
  "snapshot_load_replay": {
    "digest": "0b6aa3859869a70533ace7179a83be00ce962f6ddd10f50dc0877a205b467a11",
    "meaning": "serialized row state can be loaded and re-evaluated without runtime mutation",
    "state_restore_required": false,
    "status": "stable"
  }
}
```

## I8 Handoff

```json
{
  "claim_flags_forced_false": true,
  "control_backing_note": "Schema-backed controls are the frozen I2 control requirements. duplicate_replay_control is intentionally an I7 run-level replay extension with schema_backed=false; it must be treated as replay admissibility evidence, not as an I2 schema control.",
  "final_ap6_closeout_allowed": false,
  "i8_required_decision": "classify AP6 support boundary from controlled requirements; do not inherit final AP6 from I7 synthesis",
  "negative_controls_status": "passed_fail_closed",
  "ready_for_iteration_8_classification": true,
  "replay_status": "passed",
  "requirements_blocked": [
    "final_ap6_closeout",
    "claim_boundary_classification",
    "native_support",
    "selfhood_personhood_identity_acceptance",
    "semantic_goal_ownership",
    "closed_action_perception_loop"
  ],
  "requirements_observed": [
    "flux_balance_requirement",
    "inter_basin_separation_requirement",
    "maximum_leakage_requirement",
    "minimum_coherence_margin_requirement",
    "minimum_internal_support_requirement",
    "repair_reabsorption_requirement",
    "structured_external_coherence_rejection_requirement"
  ]
}
```

## Interpretation

I7 converts the evidence matrix into controlled requirements. Supported null/control rows remain null/control rows; supported B3/B4 rows remain artifact-level candidates; partial and rejected rows remain requirement blockers. The matrix is ready for I8 classification, but final AP6 remains false and closeout remains blocked.

## Checks

```json
{
  "all_boundary_claims_false": true,
  "all_required_controls_present": true,
  "artifact_only_replay_stable": true,
  "contract_provenance_included": true,
  "dangerous_relabels_stressed": true,
  "duplicate_replay_control_in_full_matrix": true,
  "duplicate_replay_stable": true,
  "i8_handoff_ready_without_final_ap6": true,
  "included_iterations_1_to_7": true,
  "negative_controls_distinct_fail_closed": true,
  "no_new_scientific_cells": true,
  "order_inversion_replay_stable": true,
  "requirements_have_support_and_failure_or_limit": true,
  "snapshot_load_replay_stable": true,
  "source_digests_match_acceptance": true,
  "synthesis_mode_full": true
}
```

## Output Digest

```text
383df2eb297e4a82cb71e0ce4a80aa3c506cc21ee2841b5ec010f33680229bdf
```
