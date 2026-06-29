# N28 Iteration 3 - Active Nulls And Failure Baselines

## Summary

- Status: `passed`
- Acceptance state: `accepted_active_nulls_fail_closed_no_positive_generative_evidence`
- Closeout ceiling: `N28-C3_active_nulls_fail_closed`
- Output digest: `ddd8234d8f3b5fb424c8160d65e90adbe755916c6e4e1b26bd8574a48dc6e8a4`
- Source schema digest: `e118496c025e1a36aac7e4337adcacd869715a5ce5ec6aaaf1558ef0d6576c18`
- Active null rows: `35`
- Failed-open controls: `0`
- Positive generative evidence opened: `false`
- Ready for Iteration 4: `true`

I3 instantiates every I2 control family as an active null. Each false-positive path fails closed and remains inadmissible as positive N28 evidence.

## Active Null Rows

| Row | Group | Control | Status | Violated Axis |
|---|---|---|---|---|
| `n28_i3_row_source_digest_mismatch` | `source_artifact_hygiene` | `source_digest_mismatch_control` | `failed_closed` | `source_admissibility` |
| `n28_i3_row_derived_report_only_positive_row` | `source_artifact_hygiene` | `derived_report_only_positive_row_control` | `failed_closed` | `source_current_inputs` |
| `n28_i3_row_artifact_manifest_failure` | `source_artifact_hygiene` | `artifact_manifest_failure_control` | `failed_closed` | `artifact_admissibility` |
| `n28_i3_row_threshold_declared_after_outcome` | `policy_threshold_attribution_false_positives` | `threshold_declared_after_outcome_control` | `failed_closed` | `classification_policy` |
| `n28_i3_row_missing_focal_stability_digest` | `core_digest_false_positives` | `missing_focal_stability_digest_control` | `failed_closed` | `focal_persistence_axis` |
| `n28_i3_row_missing_neighbor_capacity_digest` | `core_digest_false_positives` | `missing_neighbor_capacity_digest_control` | `failed_closed` | `neighborhood_capacity_axis` |
| `n28_i3_row_missing_extraction_cost_digest` | `core_digest_false_positives` | `missing_extraction_cost_digest_control` | `failed_closed` | `extraction_leakage_axis` |
| `n28_i3_row_missing_merge_leakage_digest` | `core_digest_false_positives` | `missing_merge_leakage_digest_control` | `failed_closed` | `extraction_leakage_axis` |
| `n28_i3_row_missing_capacity_attribution_digest` | `core_digest_false_positives` | `missing_capacity_attribution_digest_control` | `failed_closed` | `capacity_attribution_trace` |
| `n28_i3_row_malformed_generative_extractive_core_digest` | `core_digest_false_positives` | `malformed_generative_extractive_core_digest_control` | `failed_closed` | `generative_extractive_core_digest` |
| `n28_i3_row_policy_retuning_to_fit_label` | `policy_threshold_attribution_false_positives` | `policy_retuning_to_fit_label_control` | `failed_closed` | `shared_regime_policy` |
| `n28_i3_row_label_specific_threshold` | `policy_threshold_attribution_false_positives` | `label_specific_threshold_control` | `failed_closed` | `shared_regime_policy` |
| `n28_i3_row_post_hoc_regime_boundary_shift` | `policy_threshold_attribution_false_positives` | `post_hoc_regime_boundary_shift_control` | `failed_closed` | `regime_boundary_trace` |
| `n28_i3_row_focal_survival_only_as_generative` | `neighbor_capacity_false_positives` | `focal_survival_only_as_generative_control` | `failed_closed` | `neighborhood_capacity_axis` |
| `n28_i3_row_neighbor_label_only_as_capacity` | `neighbor_capacity_false_positives` | `neighbor_label_only_as_capacity_control` | `failed_closed` | `neighborhood_capacity_axis` |
| `n28_i3_row_neighbor_count_only_as_capacity` | `neighbor_capacity_false_positives` | `neighbor_count_only_as_capacity_control` | `failed_closed` | `neighborhood_capacity_axis` |
| `n28_i3_row_merge_leakage_as_support` | `extractive_merge_leakage_false_positives` | `merge_leakage_as_support_control` | `failed_closed` | `extraction_leakage_axis` |
| `n28_i3_row_extractive_flattening_masked` | `extractive_merge_leakage_false_positives` | `extractive_flattening_masked_control` | `failed_closed` | `extraction_leakage_axis` |
| `n28_i3_row_competitive_persistence_as_generative` | `general_false_positive_controls` | `competitive_persistence_as_generative_control` | `failed_closed` | `regime_classification` |
| `n28_i3_row_transfer_success_as_n28_success` | `n27_inheritance_false_positives` | `transfer_success_as_n28_success_control` | `failed_closed` | `source_precedence` |
| `n28_i3_row_hidden_capacity_attribution_policy` | `policy_threshold_attribution_false_positives` | `hidden_capacity_attribution_policy_control` | `failed_closed` | `capacity_attribution_trace` |
| `n28_i3_row_producer_generativity_label` | `general_false_positive_controls` | `producer_generativity_label_control` | `failed_closed` | `producer_residue` |
| `n28_i3_row_medium_segmentation_policy_hidden` | `policy_threshold_attribution_false_positives` | `medium_segmentation_policy_hidden_control` | `failed_closed` | `medium_debt` |
| `n28_i3_row_environment_capacity_budget_mismatch` | `policy_threshold_attribution_false_positives` | `environment_capacity_budget_mismatch_control` | `failed_closed` | `environment_capacity_budget_replay` |
| `n28_i3_row_neighbor_support_floor_missing` | `neighbor_capacity_false_positives` | `neighbor_support_floor_missing_control` | `failed_closed` | `neighborhood_capacity_axis` |
| `n28_i3_row_neighbor_boundary_integrity_missing` | `neighbor_capacity_false_positives` | `neighbor_boundary_integrity_missing_control` | `failed_closed` | `neighborhood_capacity_axis` |
| `n28_i3_row_replay_failure` | `general_false_positive_controls` | `replay_failure_control` | `failed_closed` | `replay_result` |
| `n28_i3_row_stress_variant_failure` | `general_false_positive_controls` | `stress_variant_failure_control` | `failed_closed` | `stress_result` |
| `n28_i3_row_semantic_cooperation_relabel` | `ap_claim_boundary_false_positives` | `semantic_cooperation_relabel_control` | `failed_closed` | `claim_boundary` |
| `n28_i3_row_semantic_choice_goal_relabel` | `ap_claim_boundary_false_positives` | `semantic_choice_goal_relabel_control` | `failed_closed` | `claim_boundary` |
| `n28_i3_row_native_support_relabel` | `ap_claim_boundary_false_positives` | `native_support_relabel_control` | `failed_closed` | `claim_boundary` |
| `n28_i3_row_ant_ecology_relabel` | `ap_claim_boundary_false_positives` | `ant_ecology_relabel_control` | `failed_closed` | `claim_boundary` |
| `n28_i3_row_phase8_completion_relabel` | `ap_claim_boundary_false_positives` | `phase8_completion_relabel_control` | `failed_closed` | `claim_boundary` |
| `n28_i3_row_native_ap5_relabel` | `ap_claim_boundary_false_positives` | `native_ap5_relabel_control` | `failed_closed` | `ap5_dependency_status` |
| `n28_i3_row_ap5_nat4_gap_resolution_relabel` | `ap_claim_boundary_false_positives` | `ap5_nat4_gap_resolution_relabel_control` | `failed_closed` | `ap5_dependency_status` |

## False-Positive Taxonomy

- `ap_claim_boundary_false_positives`: 7 rows
- `core_digest_false_positives`: 6 rows
- `extractive_merge_leakage_false_positives`: 2 rows
- `general_false_positive_controls`: 4 rows
- `n27_inheritance_false_positives`: 1 rows
- `neighbor_capacity_false_positives`: 5 rows
- `policy_threshold_attribution_false_positives`: 7 rows
- `source_artifact_hygiene`: 3 rows

## Geometric Interpretation

- `source_digest_mismatch`: The row is detached from the admitted source geometry. Even if it looks basin-like, it cannot inherit the N20/N27 contract surface.
- `derived_report_only_positive_row`: The geometry exists only as an interpretation layer. No focal, neighbor, extraction, or leakage trace is available for replay.
- `artifact_manifest_failure`: The basin and neighborhood traces cannot be audited or reconstructed, so apparent capacity cannot be source-backed.
- `threshold_declared_after_outcome`: The boundary between generative, extractive, and neutral regimes is drawn around the result instead of constraining the geometry.
- `missing_focal_stability_digest`: The focal basin is not source-current in the canonical core, so no persistence regime can be assigned.
- `missing_neighbor_capacity_digest`: The neighbor capacity axis cannot be audited, so generativity would be inferred without source-current capacity geometry.
- `missing_extraction_cost_digest`: The focal basin might persist by extraction, but the extraction axis is absent from the core.
- `missing_merge_leakage_digest`: Neighbor support could be merge or leakage, but the core cannot distinguish it from generated capacity.
- `missing_capacity_attribution_digest`: The capacity gain has no source-current attribution, so it could be a producer label or hidden medium policy.
- `malformed_generative_extractive_core_digest`: The canonical core has been altered or reconstructed, so replay/control rows cannot bind to the same geometry.
- `policy_retuning_to_fit_label`: The same geometric state changes regime only because the measuring surface moved, not because focal/neighbor/extraction axes changed.
- `label_specific_threshold`: Generative and extractive states are no longer compared in the same metric space, so regime separation is not source-current.
- `post_hoc_regime_boundary_shift`: The classification boundary follows the row rather than testing the row against a declared geometric boundary.
- `focal_survival_only_as_generative`: The focal basin persists, but the surrounding capacity axis is missing. This is persistence only, not generativity.
- `neighbor_label_only_as_capacity`: The neighbor has a new name, not a stronger basin-forming surface. Label change does not create capacity.
- `neighbor_count_only_as_capacity`: More counted parts do not imply stronger basin-forming geometry if support, coherence, and boundary traces are absent.
- `merge_leakage_as_support`: The neighbor appears supported because boundaries blur or flux leaks. That is not generated capacity; it is loss of separation.
- `extractive_flattening_masked`: The focal basin survives by reducing surrounding basin-forming structure. This is extractive persistence, not generative persistence.
- `competitive_persistence_as_generative`: The focal basin persists while the neighborhood is unchanged or redistributed. No net capacity improvement is shown.
- `transfer_success_as_n28_success`: A basin signature survives a frame transfer, but that says nothing by itself about whether the surrounding medium gained capacity.
- `hidden_capacity_attribution_policy`: The capacity gain is assigned from outside the graph. The geometry does not show where the neighbor improvement came from.
- `producer_generativity_label`: The word generative is attached by a producer surface while focal/neighbor/extraction axes remain unproven.
- `medium_segmentation_policy_hidden`: The neighborhood boundary is carved by hidden policy rather than emerging as an auditable source-current basin surface.
- `environment_capacity_budget_mismatch`: The neighborhood looks stronger because the budget changed, not because the same medium gained basin-forming capacity.
- `neighbor_support_floor_missing`: Without a support floor, the neighbor capacity claim cannot distinguish basin-forming support from noise or label changes.
- `neighbor_boundary_integrity_missing`: The neighbor cannot be separated from focal or medium geometry, so improved capacity could be merge or leakage.
- `replay_failure`: The regime appears once but does not replay as the same focal-neighbor-extraction geometry.
- `stress_variant_failure`: The regime survives only as a narrow fixture artifact; it does not remain a stable regime boundary under perturbation.
- `semantic_cooperation_relabel`: A social interpretation is substituted for focal, neighbor, and extraction/leakage traces.
- `semantic_choice_goal_relabel`: Goal language is substituted for geometric regime classification.
- `native_support_relabel`: A visible or producer-mediated support surface is overclaimed as native support generation.
- `ant_ecology_relabel`: A basin-regime primitive is overread as ecology behavior before N29.
- `phase8_completion_relabel`: A schema/control or primitive-row result is overread as completed implementation phase evidence.
- `native_ap5_relabel`: Proxy/target context is imported as native AP5 support, bypassing the inherited AP5 NAT4 gap.
- `ap5_nat4_gap_resolution_relabel`: A downstream regime classifier is used to backfill native target/proxy formation evidence it does not produce.

## Checks

| Check | Passed |
|---|---|
| `i2_schema_controls_passed` | `true` |
| `all_i2_controls_instantiated` | `true` |
| `headline_checklist_controls_present` | `true` |
| `all_active_nulls_fail_closed` | `true` |
| `control_row_required_fields_present` | `true` |
| `false_positive_taxonomy_recorded` | `true` |
| `failed_open_control_count_zero` | `true` |
| `no_positive_evidence_opened` | `true` |
| `no_positive_ge_rung_assigned` | `true` |
| `n28_closeout_ceiling_is_c3` | `true` |
| `source_digests_carried_from_i2` | `true` |
| `i1_source_inventory_digest_carried` | `true` |
| `medium_debt_and_producer_residue_not_success` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Claim Boundary

No active null row assigns a GE rung or opens positive generative/extractive evidence, native support, Phase 8 completion, or ant ecology.
