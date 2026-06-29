# N27 Iteration 3 - Active Nulls And Failure Baselines

Status: `passed`

Acceptance state: `accepted_active_nulls_fail_closed_no_positive_transfer_evidence`

## Scope

Iteration 3 instantiates the frozen I2 transfer controls as active nulls and
failure baselines. It opens no positive transfer evidence and assigns no CT
rung.

```text
n27_closeout_ceiling = N27-C3_active_nulls_fail_closed
positive_transfer_evidence_opened = false
ct_ladder_rung_assigned = false
failed_closed_control_count = 22
failed_open_control_count = 0
```

## Source And Implementation Boundary

```text
normative_contract_row = n20_i5_row_08_configuration_substrate_transfer
descriptor_context_row = n20_i4_row_08_configuration_substrate_transfer
n20_i5_consumable_contract_is_normative = true
n20_i4_descriptor_is_context_only = true
n26_context_is_bounded_not_transfer_evidence = true
n25_2_consumed_only_through_n26_not_direct_transfer_evidence = true
src_diff_empty = true
spec_diff_empty = true
test_diff_empty = true
implementation_patch_opened = false
```

## Active Null Rows

| Control | Blocker Triggered | Expected | Actual | Rung Effect | Claim Allowed |
| --- | --- | --- | --- | --- | --- |
| `same_label_different_basin_control` | `true` | `failed_closed` | `failed_closed` | `CT1_or_stronger_blocked` | `false` |
| `fixture_equivalence_label_only_control` | `true` | `failed_closed` | `failed_closed` | `CT1_or_stronger_blocked` | `false` |
| `mapping_declared_after_outcome_control` | `true` | `failed_closed` | `failed_closed` | `CT1_or_stronger_blocked` | `false` |
| `proxy_score_relabel_as_transfer_control` | `true` | `failed_closed` | `failed_closed` | `CT2_or_stronger_blocked` | `false` |
| `hidden_support_reconstruction_control` | `true` | `failed_closed` | `failed_closed` | `CT2_or_stronger_blocked` | `false` |
| `support_reconstruction_as_transfer_control` | `true` | `failed_closed` | `failed_closed` | `CT2_or_stronger_blocked` | `false` |
| `boundary_mapping_missing_control` | `true` | `failed_closed` | `failed_closed` | `CT2_or_stronger_blocked` | `false` |
| `post_transfer_signature_missing_control` | `true` | `failed_closed` | `failed_closed` | `CT2_or_stronger_blocked` | `false` |
| `source_current_inputs_missing_control` | `true` | `failed_closed` | `failed_closed` | `CT1_or_stronger_blocked` | `false` |
| `cross_substrate_mapping_missing_control` | `true` | `failed_closed` | `failed_closed` | `substrate_transfer_claim_blocked` | `false` |
| `artifact_manifest_failure_control` | `true` | `failed_closed` | `failed_closed` | `positive_transfer_support_blocked` | `false` |
| `replay_failure_control` | `true` | `failed_closed` | `failed_closed` | `CT3_or_stronger_blocked` | `false` |
| `stress_variant_failure_control` | `true` | `failed_closed` | `failed_closed` | `CT5_or_stronger_blocked` | `false` |
| `AP4_dependency_omitted_control` | `true` | `failed_closed` | `failed_closed` | `row_blocks_at_AP4_gate` | `false` |
| `AP5_dependency_omitted_control` | `true` | `failed_closed` | `failed_closed` | `row_blocks_at_AP5_gate` | `false` |
| `n26_proxy_as_transfer_evidence_control` | `true` | `failed_closed` | `failed_closed` | `positive_transfer_support_blocked` | `false` |
| `n26_scoped_ap5_as_native_ap5_control` | `true` | `failed_closed` | `failed_closed` | `AP5_NAT4_gap_resolution_blocked` | `false` |
| `n25_2_direct_transfer_consumption_control` | `true` | `failed_closed` | `failed_closed` | `positive_transfer_support_blocked` | `false` |
| `semantic_identity_relabel_control` | `true` | `failed_closed` | `failed_closed` | `unsafe_claim_blocked` | `false` |
| `semantic_choice_goal_relabel_control` | `true` | `failed_closed` | `failed_closed` | `unsafe_claim_blocked` | `false` |
| `native_support_relabel_control` | `true` | `failed_closed` | `failed_closed` | `unsafe_claim_blocked` | `false` |
| `phase8_ant_ecology_relabel_control` | `true` | `failed_closed` | `failed_closed` | `unsafe_claim_blocked` | `false` |


## Geometric Interpretation

Each row records a false transfer path in geometric terms: label survival,
within-frame movement, visual/topological similarity, proxy preservation,
hidden support reconstruction, missing boundary mapping, missing post-transfer
signature, missing source-current inputs, unmapped substrate claims, replay or
stress failure, AP dependency omission, imported N26/N25.2 context, or unsafe
semantic/native/Phase-8 relabeling. In every case the blocker triggers and the
claim fails closed.

The negative set is intentionally orthogonal: every row records exactly one
`primary_blocker_control_id`, and all non-target positive gates remain
`not_evaluated_active_null`. This prevents an active null from passing only
because unrelated gates were also forced to fail.

## Checks

| Check | Passed |
| --- | --- |
| `i2_schema_passed` | `true` |
| `i2_digest_recorded` | `true` |
| `all_frozen_controls_instantiated` | `true` |
| `all_active_nulls_fail_closed` | `true` |
| `failed_open_control_count_zero` | `true` |
| `controls_remain_orthogonal` | `true` |
| `control_result_audit_fields_present` | `true` |
| `active_null_boundary_markers_present` | `true` |
| `primary_blockers_isolated` | `true` |
| `non_target_positive_gates_not_evaluated` | `true` |
| `artifact_manifest_failure_cases_explicit` | `true` |
| `no_positive_transfer_evidence_opened` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `active_null_rows_not_source_current_positive_evidence` | `true` |
| `source_precedence_preserved` | `true` |
| `no_implementation_patch_opened` | `true` |
| `ready_for_iteration_4` | `true` |
| `no_absolute_paths_in_records` | `true` |


## Interpretation

I3 supports only the fail-closed-control portion of N27. It proves that the
frozen false-transfer paths are rejected before positive probes. It does not
support CT1, CT2, CT3, transfer, identity, native support, native AP5, AP5
NAT4-gap resolution, Phase 8, or ant ecology.

Output digest: `2ef877fbbd8a66ca858a28d9deaf8ec84dbaf4529471920a90623499a2d4ebe3`
