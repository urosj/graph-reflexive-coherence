# N28 Iteration 2 - Generative / Extractive Schema And Controls

## Summary

- Status: `passed`
- Acceptance state: `accepted_generative_extractive_schema_and_controls_frozen_no_positive_evidence`
- Closeout ceiling: `N28-C2_schema_controls_and_classification_policy_frozen`
- Output digest: `e118496c025e1a36aac7e4337adcacd869715a5ce5ec6aaaf1558ef0d6576c18`
- I1 digest: `f30af50b1e1209039b82454b510f4765de7ee8befe214d96218dec3207db5985`
- Positive generative evidence opened: `false`
- GE rung assigned: `false`
- Ready for Iteration 3: `true`

I2 freezes the schema and control surface only. It defines how later rows must distinguish generative, extractive, competitive, and neutral persistence without treating N27 transfer success, medium debt, labels, or focal survival alone as N28 evidence.

## Three-Axis Classifier

| Axis | Allowed States |
|---|---|
| `extraction_leakage_axis` | `low_preserved_medium, high_extraction_flattening_leakage_or_merge, missing` |
| `focal_persistence_axis` | `stable, unstable, missing` |
| `neighborhood_capacity_axis` | `improves, degrades, neutral_or_mixed, label_only, missing` |

## Source Digest Pins

| Field | Digest |
|---|---|
| `n20_i3_row_digest` | `2108f86e21cbf795a2ab0ef089a1f25f641c60865d97c0fb983119a4f34d50a0` |
| `n20_i4_row_digest` | `c08025d24b89807fc5ad245302f33ae4286ed8ad89bf7db450a94eb08c27d99b` |
| `n20_i5_row_digest` | `240de0c58bf066a6fb1ff610f13dbecb4f76a3f187ac08012927005de91563b7` |
| `n27_closeout_output_digest` | `818a57c3c3fd778809f6e2b37525d69f1010976adb953e91eceeb633dde5b716` |
| `n27_side_effect_claim_classification_output_digest` | `10a4ca23ea7c111a6de53fd2c5b27d30cd75063ef7c7304cad46010776362fbb` |
| `n27_side_effect_precursor_output_digest` | `2dbe7d94d14ffd6753952dfb5360ac779b2c433c0a24e3a8a7444b40964fd1af` |
| `source_inventory_output_digest` | `f30af50b1e1209039b82454b510f4765de7ee8befe214d96218dec3207db5985` |

## Ladders

| GE Rung | Definition |
|---|---|
| `GE0` | no source-current generative/extractive persistence evidence |
| `GE1` | focal persistence trace present; environment-side effect not measured |
| `GE2` | focal persistence plus source-current neighborhood capacity metrics observed |
| `GE3` | provisional source-current regime classification candidate |
| `GE4` | replay/control-backed regime-separation candidate |
| `GE5` | stress/variant-backed paired-regime separation candidate |
| `GE6` | N29-ready bounded generative/extractive persistence evidence with claim-clean handoff |

| N28 Closeout Rung | Definition |
|---|---|
| `N28-C0` | initialized contract only |
| `N28-C1` | source inventory and generative/extractive contract admission passed |
| `N28-C2` | schema, controls, and classification policy frozen |
| `N28-C3` | active nulls fail closed |
| `N28-C4` | source-current generative/extractive candidate supported |
| `N28-C5` | replay/control/stress-backed generative/extractive candidate supported |
| `N28-C6` | N29-ready bounded generative/extractive closeout |

## Required Control Families

`source_digest_mismatch_control`, `derived_report_only_positive_row_control`, `artifact_manifest_failure_control`, `threshold_declared_after_outcome_control`, `missing_focal_stability_digest_control`, `missing_neighbor_capacity_digest_control`, `missing_extraction_cost_digest_control`, `missing_merge_leakage_digest_control`, `missing_capacity_attribution_digest_control`, `malformed_generative_extractive_core_digest_control`, `policy_retuning_to_fit_label_control`, `label_specific_threshold_control`, `post_hoc_regime_boundary_shift_control`, `focal_survival_only_as_generative_control`, `neighbor_label_only_as_capacity_control`, `neighbor_count_only_as_capacity_control`, `merge_leakage_as_support_control`, `extractive_flattening_masked_control`, `competitive_persistence_as_generative_control`, `transfer_success_as_n28_success_control`, `hidden_capacity_attribution_policy_control`, `producer_generativity_label_control`, `medium_segmentation_policy_hidden_control`, `environment_capacity_budget_mismatch_control`, `neighbor_support_floor_missing_control`, `neighbor_boundary_integrity_missing_control`, `replay_failure_control`, `stress_variant_failure_control`, `semantic_cooperation_relabel_control`, `semantic_choice_goal_relabel_control`, `native_support_relabel_control`, `ant_ecology_relabel_control`, `phase8_completion_relabel_control`, `native_ap5_relabel_control`, `ap5_nat4_gap_resolution_relabel_control`


## Checks

| Check | Passed |
|---|---|
| `i1_source_inventory_passed` | `true` |
| `source_precedence_frozen` | `true` |
| `source_digest_pins_present` | `true` |
| `ge_ladder_frozen` | `true` |
| `n28_closeout_ladder_frozen` | `true` |
| `paired_regime_evidence_requirement_frozen` | `true` |
| `three_axis_classifier_frozen` | `true` |
| `required_evidence_fields_present` | `true` |
| `core_schema_and_digest_policy_frozen` | `true` |
| `formulas_frozen` | `true` |
| `regime_policy_enums_frozen` | `true` |
| `medium_debt_and_producer_residue_frozen` | `true` |
| `artifact_roles_replay_ap_frozen` | `true` |
| `control_families_frozen` | `true` |
| `no_positive_evidence_opened` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

All unsafe claim flags remain false. I2 assigns no GE rung and opens no positive generative/extractive evidence.
