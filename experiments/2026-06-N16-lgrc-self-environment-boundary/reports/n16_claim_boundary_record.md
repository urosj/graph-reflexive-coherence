# N16 Claim Boundary And AP6 Classification

Status: `passed`.

```text
acceptance_state = accepted_ap6_classification_claim_boundary_clean_pending_closeout
classified_ap_level = AP6
ap6_classification_supported = true
artifact_level_ap6_supported = true
final_ap6_supported = false
final_artifact_level_ap6_frozen = false
final_ap_freeze_pending_iteration9 = true
phase8_opened = false
native_support_opened = false
```

Iteration 8 classifies the N16 candidate as artifact-level AP6 with claim boundaries intact. Final AP6 freeze remains pending until Iteration 9 closeout.

## AP6 Gate Summary

```json
{
  "all_ap6_gates_validated": true,
  "blocked_gate_count": 0,
  "blocked_gates": [],
  "gate_count": 39,
  "validated_gate_count": 39
}
```

## Hypotheses

| Hypothesis | Decision | Scope |
| --- | --- | --- |
| `hypothesis_a_boundary_source_inventory` | `supported` | source-backed internal, external, structured, B-axis, and C-axis records are pinned and claim-clean |
| `hypothesis_b_artifact_basin_boundary_stability` | `supported` | artifact-level AP6 basin-boundary stability candidate pending final closeout |
| `hypothesis_c_selfhood_identity_agency_boundary` | `supported` | unsafe promotions remain blocked while AP6 candidate classification is preserved |

## Boundary Summary

```json
{
  "all_boundary_claims_blocked": true,
  "all_unsafe_boundary_promotions_blocked": true,
  "artifact_ap6_boundary_candidate_supported": true,
  "blocked_claims": [
    "selfhood",
    "identity_acceptance",
    "semantic_goal_ownership",
    "closed_action_perception_loop",
    "native_support",
    "fully_native_agentic_like_integration",
    "agency_environment_model",
    "autonomous_repair",
    "native_multi_basin_selfhood",
    "selective_uptake_resource_assimilation_life",
    "schema_control_overclaim"
  ],
  "boundary_row_count": 11,
  "closed_action_perception_loop_blocked": true,
  "duplicate_replay_schema_backing_acknowledged": true,
  "identity_acceptance_blocked": true,
  "native_support_blocked": true,
  "selfhood_blocked": true,
  "semantic_goal_ownership_blocked": true
}
```

## Boundary Rows

| Row | Blocked Claim | Claim Allowed |
| --- | --- | --- |
| `n16_i8_boundary_01_artifact_boundary_not_selfhood` | `selfhood` | `false` |
| `n16_i8_boundary_02_boundary_side_assignment_not_identity_acceptance` | `identity_acceptance` | `false` |
| `n16_i8_boundary_03_internal_support_not_semantic_goal_ownership` | `semantic_goal_ownership` | `false` |
| `n16_i8_boundary_04_boundary_crossing_not_action_perception_loop` | `closed_action_perception_loop` | `false` |
| `n16_i8_boundary_05_artifact_ap6_not_native_support` | `native_support` | `false` |
| `n16_i8_boundary_06_artifact_ap6_not_fully_native_integration` | `fully_native_agentic_like_integration` | `false` |
| `n16_i8_boundary_07_external_state_not_agency_environment_model` | `agency_environment_model` | `false` |
| `n16_i8_boundary_08_b3_reclosure_not_autonomous_repair` | `autonomous_repair` | `false` |
| `n16_i8_boundary_09_b4_shared_medium_not_native_multi_basin_selfhood` | `native_multi_basin_selfhood` | `false` |
| `n16_i8_boundary_10_no_selective_uptake_resource_assimilation_or_life` | `selective_uptake_resource_assimilation_life` | `false` |
| `n16_i8_boundary_11_duplicate_replay_not_i2_schema_control` | `schema_control_overclaim` | `false` |

## Blocked Input Audit

```json
{
  "audit_complete": true,
  "blocked_boundary_claims": [
    {
      "blocked_claim": "selfhood",
      "row_id": "n16_i8_boundary_01_artifact_boundary_not_selfhood",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "identity_acceptance",
      "row_id": "n16_i8_boundary_02_boundary_side_assignment_not_identity_acceptance",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "semantic_goal_ownership",
      "row_id": "n16_i8_boundary_03_internal_support_not_semantic_goal_ownership",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "closed_action_perception_loop",
      "row_id": "n16_i8_boundary_04_boundary_crossing_not_action_perception_loop",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "native_support",
      "row_id": "n16_i8_boundary_05_artifact_ap6_not_native_support",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "fully_native_agentic_like_integration",
      "row_id": "n16_i8_boundary_06_artifact_ap6_not_fully_native_integration",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "agency_environment_model",
      "row_id": "n16_i8_boundary_07_external_state_not_agency_environment_model",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "autonomous_repair",
      "row_id": "n16_i8_boundary_08_b3_reclosure_not_autonomous_repair",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "native_multi_basin_selfhood",
      "row_id": "n16_i8_boundary_09_b4_shared_medium_not_native_multi_basin_selfhood",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "selective_uptake_resource_assimilation_life",
      "row_id": "n16_i8_boundary_10_no_selective_uptake_resource_assimilation_or_life",
      "source": "n16_i8_claim_boundary_record"
    },
    {
      "blocked_claim": "schema_control_overclaim",
      "row_id": "n16_i8_boundary_11_duplicate_replay_not_i2_schema_control",
      "source": "n16_i8_claim_boundary_record"
    }
  ],
  "blocked_control_inputs": [
    {
      "control_id": "artifact_only_replay_control",
      "observed_blocker": "artifact_replay_instability_blocks_ap6",
      "observed_status": "stable",
      "schema_backed": true
    },
    {
      "control_id": "boundary_drift_outside_policy_control",
      "observed_blocker": "boundary_drift_outside_policy_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "duplicate_replay_control",
      "observed_blocker": "duplicate_replay_instability_blocks_ap6",
      "observed_status": "stable",
      "schema_backed": false
    },
    {
      "control_id": "externally_supplied_boundary_control",
      "observed_blocker": "externally_supplied_boundary_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "hidden_external_state_injection_control",
      "observed_blocker": "hidden_external_state_injection_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "identity_acceptance_relabel_control",
      "observed_blocker": "identity_acceptance_relabel_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "missing_boundary_side_state_control",
      "observed_blocker": "missing_boundary_side_state_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "multi_basin_merge_control",
      "observed_blocker": "multi_basin_merge_or_leakage_recorded",
      "observed_status": "blocked_or_recorded_failure",
      "schema_backed": true
    },
    {
      "control_id": "native_support_relabel_control",
      "observed_blocker": "native_support_relabel_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "order_inversion_replay_control",
      "observed_blocker": "order_inversion_instability_blocks_ap6",
      "observed_status": "stable",
      "schema_backed": true
    },
    {
      "control_id": "post_hoc_boundary_label_control",
      "observed_blocker": "post_hoc_boundary_label_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "resource_relabel_as_self_control",
      "observed_blocker": "resource_relabel_as_self_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "self_support_relabel_as_external_control",
      "observed_blocker": "self_support_relabel_as_external_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "selfhood_personhood_relabel_control",
      "observed_blocker": "selfhood_personhood_relabel_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "semantic_goal_ownership_relabel_control",
      "observed_blocker": "semantic_goal_ownership_relabel_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "snapshot_load_replay_control",
      "observed_blocker": "snapshot_load_instability_blocks_ap6",
      "observed_status": "stable",
      "schema_backed": true
    },
    {
      "control_id": "stale_external_state_control",
      "observed_blocker": "stale_external_state_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "stale_internal_state_control",
      "observed_blocker": "stale_internal_state_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    },
    {
      "control_id": "structured_external_coherence_rejection_control",
      "observed_blocker": "structured_external_coherence_false_boundary_blocked",
      "observed_status": "blocked_or_rejected",
      "schema_backed": true
    },
    {
      "control_id": "untracked_boundary_crossing_control",
      "observed_blocker": "untracked_boundary_crossing_blocked",
      "observed_status": "blocked",
      "schema_backed": true
    }
  ],
  "duplicate_replay_extension_audited": true,
  "n14_caveat_evidence": [
    {
      "ap6_required_evidence_still_missing": [
        "route_selection_is_not_boundary_separability",
        "shared_medium_boundary_rows_not_generated"
      ],
      "boundary_claim_allowed": false,
      "claim_promotion_allowed": false,
      "direct_historic_ap6_support_status": "not_direct_ap6_support",
      "evidence_strategy_class": "old_best_claims_construction",
      "final_ap6_supported": false,
      "mechanism_name": "artifact_level_ap4_consequence_sensitive_route_selection",
      "mechanism_role": "old_best_ap4_consequence_selection_axis",
      "provisional_claim_ceiling": "artifact_level_ap4_consequence_sensitive_route_selection_candidate",
      "row_id": "n16_i1_row_05_n14_closeout_ap4",
      "source_artifact": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/n14_closeout_and_handoff.json",
      "source_experiment": "N14",
      "source_iteration": "closeout_and_n15_handoff",
      "source_report": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_closeout_and_handoff.md",
      "source_report_sha256": "5f058dd6802065954e2c4e0f8d663d93fb8d55b2520a43edafbf79b3a14e1c7a",
      "source_sha256": "47d794a5fd53e96e9017d5cbdcf8959d5372d6dfa52467661a0dc14661eadbc1"
    },
    {
      "ap6_required_evidence_still_missing": [
        "upstream_observed_route_conditioned_support_missing",
        "upstream_observed_route_conditioned_regulation_missing",
        "not_multi_basin_separability_evidence"
      ],
      "boundary_claim_allowed": false,
      "claim_promotion_allowed": false,
      "direct_historic_ap6_support_status": "not_direct_ap6_support",
      "evidence_strategy_class": "old_best_claims_construction",
      "final_ap6_supported": false,
      "mechanism_name": "constructed_route_conditioned_support_regulation_followout",
      "mechanism_role": "constructed_external_route_context",
      "provisional_claim_ceiling": "constructed_route_conditioned_followout_context_only",
      "row_id": "n16_i1_row_06_n14_constructed_followout",
      "source_artifact": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/outputs/n14_route_conditioned_followout_probe.json",
      "source_experiment": "N14",
      "source_iteration": "route_conditioned_followout_probe",
      "source_report": "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_route_conditioned_followout_probe.md",
      "source_report_sha256": "6b25d12a8f8cf9412d317ebb398972be68b19f9ae8cc8f683b59fbf69316533f",
      "source_sha256": "450dd43f4f35a7ba375fa0b197c34c11a0ddac324b2d26660d75c98b201ccaa4"
    }
  ],
  "n14_constructed_followout_caveat_preserved": true,
  "n15_ap5_target_proxy_boundary_caveat_preserved": true,
  "n15_caveat_evidence": [
    {
      "ap6_required_evidence_still_missing": [
        "ap6_internal_external_boundary_schema_not_frozen",
        "ap6_boundary_rows_not_generated",
        "ap6_controls_not_run"
      ],
      "boundary_claim_allowed": false,
      "claim_promotion_allowed": false,
      "direct_historic_ap6_support_status": "not_direct_ap6_support",
      "evidence_strategy_class": "old_best_claims_construction",
      "final_ap6_supported": false,
      "mechanism_name": "artifact_level_ap5_endogenous_proxy_formation_candidate",
      "mechanism_role": "old_best_ap5_proxy_target_axis",
      "provisional_claim_ceiling": "artifact_level_ap5_endogenous_proxy_formation_candidate",
      "row_id": "n16_i1_row_01_n15_closeout_ap5",
      "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_closeout_and_handoff.json",
      "source_experiment": "N15",
      "source_iteration": "closeout_and_n16_handoff",
      "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_closeout_and_handoff.md",
      "source_report_sha256": "7fd4773de2bb4cce79799caf287f22b13e056b567a44da562d22665d07fda4ee",
      "source_sha256": "9a86c0e3f5fcc96dd055a8c05baf8b0cd22edc91693a67dc6a8ee209db862fa5"
    },
    {
      "ap6_required_evidence_still_missing": [
        "target_condition_is_not_boundary_side_assignment",
        "internal_external_state_separation_not_built",
        "ap6_claim_boundary_not_classified"
      ],
      "boundary_claim_allowed": false,
      "claim_promotion_allowed": false,
      "direct_historic_ap6_support_status": "not_direct_ap6_support",
      "evidence_strategy_class": "old_best_claims_construction",
      "final_ap6_supported": false,
      "mechanism_name": "runtime_derived_target_candidate_from_old_best_inputs",
      "mechanism_role": "source_current_target_generation_context",
      "provisional_claim_ceiling": "provisional_runtime_derived_target_candidate_pending_controls",
      "row_id": "n16_i1_row_02_n15_runtime_derived_target_candidate",
      "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_runtime_derived_target_candidate.json",
      "source_experiment": "N15",
      "source_iteration": "iteration_3_runtime_derived_target_candidate",
      "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_runtime_derived_target_candidate.md",
      "source_report_sha256": "c54c784652e004a23f1283d8e716f370993636b72e4d9ade46f2d9d7c071277c",
      "source_sha256": "30c834b47a7decf2bb32f3dabb8dcb436b2b7876be5b0e9c79fe76b7de010873"
    },
    {
      "ap6_required_evidence_still_missing": [
        "boundary_side_replay_digest_not_frozen",
        "challenge_class_rows_not_generated"
      ],
      "boundary_claim_allowed": false,
      "claim_promotion_allowed": false,
      "direct_historic_ap6_support_status": "not_direct_ap6_support",
      "evidence_strategy_class": "control_context",
      "final_ap6_supported": false,
      "mechanism_name": "bounded_drift_replay_matrix",
      "mechanism_role": "replay_and_drift_control_context",
      "provisional_claim_ceiling": "bounded_drift_replay_context_only",
      "row_id": "n16_i1_row_03_n15_bounded_drift_replay",
      "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_bounded_drift_replay_matrix.json",
      "source_experiment": "N15",
      "source_iteration": "iteration_6_bounded_drift_and_replay_matrix",
      "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_bounded_drift_replay_matrix.md",
      "source_report_sha256": "8766f392358f7aa675a591c076e3cec5a97f91af5ed5f382bc306a9809a13728",
      "source_sha256": "c9c5307c408836d7a54e88507ceb85cf6dae4755444b20ab072409cddbc7b3d0"
    },
    {
      "ap6_required_evidence_still_missing": [
        "positive_ap6_boundary_evidence_absent"
      ],
      "boundary_claim_allowed": false,
      "claim_promotion_allowed": false,
      "direct_historic_ap6_support_status": "not_ap6_positive_evidence",
      "evidence_strategy_class": "rejected",
      "final_ap6_supported": false,
      "mechanism_name": "n15_claim_boundary_record",
      "mechanism_role": "unsafe_claim_relabel_blocker_source",
      "provisional_claim_ceiling": "claim_boundary_context_only",
      "row_id": "n16_i1_row_04_n15_claim_boundary",
      "source_artifact": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_claim_boundary_record.json",
      "source_experiment": "N15",
      "source_iteration": "iteration_7_claim_boundary_record",
      "source_report": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_claim_boundary_record.md",
      "source_report_sha256": "9a7f9558adeda1449f5b728cf330bea1a4906a99094d9a8fa5c8a310284845fe",
      "source_sha256": "99781fbd38ea972c07c1f1313cbcce95bbbc99eeec05cdafb2678a445810bb87"
    }
  ],
  "prior_claim_promotion_blockers": [
    "N15 AP5 proxy formation is not AP6 boundary separability by relabel",
    "N14 AP4 consequence-sensitive selection is not intention or semantic choice",
    "N13 AP3 support regulation is not selfhood or native support",
    "N12 NAT4 readiness remains readiness-only context"
  ]
}
```

## Review-Hardening Audits

```json
{
  "claim_flag_merge_audit": {
    "control_unsafe_false_preserved": true,
    "intentional_overrides": {
      "artifact_level_ap6_supported": {
        "control_variant_value": false,
        "iteration_8_value": true,
        "reason": "I8 classifies artifact-level AP6 as supported while final AP6 freeze and unsafe promotions remain false"
      }
    },
    "shared_unsafe_flags_consistent": true,
    "shared_unsafe_keys": [
      "agency_claim_allowed",
      "biological_behavior_claim_allowed",
      "final_ap6_supported",
      "fully_native_agentic_like_integration_claim_allowed",
      "identity_acceptance_claim_allowed",
      "intention_claim_allowed",
      "native_support_opened",
      "personhood_claim_allowed",
      "phase8_opened",
      "resource_assimilation_claim_allowed",
      "runtime_identity_acceptance_claim_allowed",
      "selective_uptake_claim_allowed",
      "selfhood_claim_allowed",
      "semantic_choice_claim_allowed",
      "semantic_goal_ownership_claim_allowed",
      "semantic_goal_understanding_claim_allowed",
      "unrestricted_agency_claim_allowed"
    ],
    "status": "passed",
    "unsafe_flags_false": true
  },
  "cross_iteration_cell_consistency": {
    "cells": [
      {
        "cell_id": "B2_C0",
        "key_metrics_consistent": true,
        "metric_consistency": {
          "boundary_stability_score": {
            "compared": true,
            "consistent": true,
            "values": [
              1.0,
              1.0
            ]
          },
          "coherence_margin": {
            "compared": true,
            "consistent": true,
            "values": [
              0.53,
              0.53
            ]
          },
          "external_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.35,
              0.35
            ]
          },
          "inbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.0,
              0.0
            ]
          },
          "internal_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.88,
              0.88
            ]
          },
          "leakage_ratio": {
            "compared": true,
            "consistent": true,
            "values": [
              0.061644,
              0.061644
            ]
          },
          "minimum_internal_support": {
            "compared": false,
            "consistent": true,
            "values": [
              0.86
            ]
          },
          "outbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.0,
              0.0
            ]
          },
          "retained_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              1.46,
              1.46
            ]
          }
        },
        "row_count": 2,
        "row_decision_consistent": true,
        "row_decisions": [
          "supported",
          "supported"
        ],
        "source_rows": [
          {
            "boundary_claim_allowed": false,
            "row_decision": "supported",
            "row_id": "n16_i3_row_b2_c0",
            "source_artifact_id": "n16_quiet_boundary_calibration"
          },
          {
            "boundary_claim_allowed": false,
            "row_decision": "supported",
            "row_id": "n16_i4_row_b2_c0",
            "source_artifact_id": "n16_challenge_sweep_matrix"
          }
        ],
        "status": "consistent"
      },
      {
        "cell_id": "B2_C1",
        "key_metrics_consistent": true,
        "metric_consistency": {
          "boundary_stability_score": {
            "compared": true,
            "consistent": true,
            "values": [
              0.9,
              0.9
            ]
          },
          "coherence_margin": {
            "compared": true,
            "consistent": true,
            "values": [
              0.532,
              0.532
            ]
          },
          "external_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.34,
              0.34
            ]
          },
          "inbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.03,
              0.03
            ]
          },
          "internal_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.872,
              0.872
            ]
          },
          "leakage_ratio": {
            "compared": true,
            "consistent": true,
            "values": [
              0.078,
              0.078
            ]
          },
          "minimum_internal_support": {
            "compared": true,
            "consistent": true,
            "values": [
              0.85,
              0.85
            ]
          },
          "outbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.02,
              0.02
            ]
          },
          "retained_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              1.41,
              1.41
            ]
          }
        },
        "row_count": 2,
        "row_decision_consistent": true,
        "row_decisions": [
          "supported",
          "supported"
        ],
        "source_rows": [
          {
            "boundary_claim_allowed": false,
            "row_decision": "supported",
            "row_id": "n16_i4_row_b2_c1",
            "source_artifact_id": "n16_challenge_sweep_matrix"
          },
          {
            "boundary_claim_allowed": false,
            "row_decision": "supported",
            "row_id": "n16_i6_row_b2_c1",
            "source_artifact_id": "n16_selected_interaction_probe_matrix"
          }
        ],
        "status": "consistent"
      },
      {
        "cell_id": "B2_C2",
        "key_metrics_consistent": true,
        "metric_consistency": {
          "boundary_stability_score": {
            "compared": true,
            "consistent": true,
            "values": [
              0.62,
              0.62
            ]
          },
          "coherence_margin": {
            "compared": true,
            "consistent": true,
            "values": [
              0.488,
              0.488
            ]
          },
          "external_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.36,
              0.36
            ]
          },
          "inbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.34,
              0.34
            ]
          },
          "internal_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.848,
              0.848
            ]
          },
          "leakage_ratio": {
            "compared": true,
            "consistent": true,
            "values": [
              0.186,
              0.186
            ]
          },
          "minimum_internal_support": {
            "compared": true,
            "consistent": true,
            "values": [
              0.84,
              0.84
            ]
          },
          "outbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.22,
              0.22
            ]
          },
          "retained_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              1.18,
              1.18
            ]
          }
        },
        "row_count": 2,
        "row_decision_consistent": true,
        "row_decisions": [
          "partial",
          "partial"
        ],
        "source_rows": [
          {
            "boundary_claim_allowed": false,
            "row_decision": "partial",
            "row_id": "n16_i4_row_b2_c2",
            "source_artifact_id": "n16_challenge_sweep_matrix"
          },
          {
            "boundary_claim_allowed": false,
            "row_decision": "partial",
            "row_id": "n16_i5_row_b2_c2",
            "source_artifact_id": "n16_boundary_state_sweep_matrix"
          }
        ],
        "status": "consistent"
      },
      {
        "cell_id": "B1_C2",
        "key_metrics_consistent": true,
        "metric_consistency": {
          "boundary_stability_score": {
            "compared": true,
            "consistent": true,
            "values": [
              0.34,
              0.34
            ]
          },
          "coherence_margin": {
            "compared": true,
            "consistent": true,
            "values": [
              0.442,
              0.442
            ]
          },
          "external_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.37,
              0.37
            ]
          },
          "inbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.34,
              0.34
            ]
          },
          "internal_coherence": {
            "compared": true,
            "consistent": true,
            "values": [
              0.812,
              0.812
            ]
          },
          "leakage_ratio": {
            "compared": true,
            "consistent": true,
            "values": [
              0.294,
              0.294
            ]
          },
          "minimum_internal_support": {
            "compared": true,
            "consistent": true,
            "values": [
              0.76,
              0.76
            ]
          },
          "outbound_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.28,
              0.28
            ]
          },
          "retained_flux": {
            "compared": true,
            "consistent": true,
            "values": [
              0.76,
              0.76
            ]
          }
        },
        "row_count": 2,
        "row_decision_consistent": true,
        "row_decisions": [
          "partial",
          "partial"
        ],
        "source_rows": [
          {
            "boundary_claim_allowed": false,
            "row_decision": "partial",
            "row_id": "n16_i5_row_b1_c2",
            "source_artifact_id": "n16_boundary_state_sweep_matrix"
          },
          {
            "boundary_claim_allowed": false,
            "row_decision": "partial",
            "row_id": "n16_i6_row_b1_c2",
            "source_artifact_id": "n16_selected_interaction_probe_matrix"
          }
        ],
        "status": "consistent"
      }
    ],
    "cells_checked": [
      "B2_C0",
      "B2_C1",
      "B2_C2",
      "B1_C2"
    ],
    "status": "passed",
    "tolerance": 1e-09
  },
  "duplicate_replay_backing_audit": {
    "acknowledged": true,
    "control_present": true,
    "expected_backing": "i7_run_level_replay_extension_not_i2_schema_control",
    "handoff_note_contains_control_id": true,
    "schema_backed": false,
    "schema_backed_field_present": true
  },
  "global_stress_envelope_scope_note": "Global aggregate metrics are computed across every reused I3-I6 row, including null, rejected, and partial control rows. Supported boundary-candidate metrics exclude B0 active-null rows and unsupported rows.",
  "row_decision_enum_revalidation": {
    "allowed_values": [
      "blocked",
      "not_applicable",
      "partial",
      "rejected",
      "supported"
    ],
    "control_evidence_cell_count_checked": 47,
    "invalid_control_evidence": [],
    "invalid_rows": [],
    "row_count_checked": 19,
    "status": "passed"
  }
}
```

## Interpretation

N16 now has a claim-clean artifact-level AP6 classification: internal support-relevant state and external resource, perturbation, structured-state, and shared-medium pressures are separable in the generated artifacts and controls. The result remains a basin-boundary candidate pending Iteration 9 closeout; it does not support selfhood, identity acceptance, semantic goal ownership, agency, native support, Phase 8, fully native integration, selective uptake, resource assimilation, organism claims, life claims, or a closed action-perception loop.

## Checks

```json
{
  "all_ap6_gates_validated": true,
  "ap6_classification_supported": true,
  "artifact_level_ap6_supported_separate_from_final_freeze": true,
  "b4_c5_one_sided_limitation_recorded": true,
  "boundary_rows_block_claims": true,
  "claim_flag_merge_consistent": true,
  "control_gate_rationales_specific": true,
  "cross_iteration_cell_consistency_passed": true,
  "duplicate_replay_backing_acknowledged": true,
  "final_ap6_not_frozen_until_iteration9": true,
  "global_stress_envelope_scope_explained": true,
  "hypothesis_a_supported": true,
  "hypothesis_b_supported": true,
  "hypothesis_c_supported": true,
  "i7_requirements_matrix_passed": true,
  "n14_n15_caveats_traceable": true,
  "native_phase8_fully_native_false": true,
  "no_new_b_c_cells_created": true,
  "post_write_output_digest_self_verification_enabled": true,
  "row_decision_enum_revalidated": true,
  "source_digests_match_acceptance": true,
  "src_diff_empty": true,
  "unsafe_claim_flags_false": true
}
```

## Output Digest

```text
c9e319f6f5a2fce79a13748bc38f2272d9b69775032136c5e47f33abe61bf6c6
```
