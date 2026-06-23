# N22 Iteration 3 - Active Nulls And Failure Baselines

## Summary

Status: `passed`

Acceptance state: `accepted_active_nulls_fail_closed_no_positive_evidence`

Output digest: `4843f5661908cc612d71df1957bc16929ed199b7c2c72134c4f0d67bea750138`

Iteration 3 instantiates the frozen I2 schema as active nulls. It does
not expand the schema, open positive susceptibility evidence, or assign
SU/N22-C rungs above control scope.

## Active Null Matrix

| Row | Null | Result | Rung Effect |
| --- | --- | --- | --- |
| `n22_i3_row_01_route_label_only_delta` | `label_only_delta` | `failed_closed` | `blocks SU2 and stronger` |
| `n22_i3_row_02_reinforcement_schedule_only_delta` | `producer_schedule_only_delta` | `failed_closed` | `blocks SU2 and stronger` |
| `n22_i3_row_03_one_window_flux_transient` | `one_window_flux_transient` | `failed_closed` | `blocks SU4 and stronger` |
| `n22_i3_row_04_missing_later_reentry` | `missing_reentry_trace` | `failed_closed` | `blocks SU5 and stronger` |
| `n22_i3_row_05_post_hoc_delta_construction` | `post_hoc_delta_construction` | `failed_closed` | `blocks SU2 and stronger` |
| `n22_i3_row_06_hidden_reinforcement` | `hidden_reinforcement` | `failed_closed` | `blocks SU4, SU5, SU6, N22-C4, N22-C5, N22-C6, and ND6 bridge` |
| `n22_i3_row_07_route_conditioned_row_missing_AP4` | `ap4_gap_omission` | `failed_closed` | `blocks route-conditioned SU rows` |
| `n22_i3_row_08_proxy_or_target_conditioned_row_missing_AP5` | `ap5_gap_omission` | `failed_closed` | `blocks proxy-conditioned SU rows` |
| `n22_i3_row_09_AP_gap_prose_only` | `ap_gap_prose_only` | `failed_closed` | `blocks dependent SU rows` |
| `n22_i3_row_10_peer_same_budget_missing` | `missing_peer_same_budget_comparison` | `failed_closed` | `blocks SU5, SU6, N22-C5, and N22-C6` |
| `n22_i3_row_11_global_drift_not_rejected` | `global_drift_not_rejected` | `failed_closed` | `blocks route/region-conditioned SU5 and SU6` |
| `n22_i3_row_12_semantic_learning_relabel` | `semantic_learning_relabel` | `failed_closed` | `blocks all SU support and unsafe claims` |
| `n22_i3_row_13_native_support_relabel` | `native_support_relabel` | `failed_closed` | `blocks all SU support and unsafe claims` |
| `n22_i3_row_14_phase8_relabel` | `phase8_relabel` | `failed_closed` | `blocks all SU support and unsafe claims` |

## Summary Counts

- Rows: `14`
- Failed closed rows: `14`
- Failed open rows: `0`
- Positive susceptibility evidence opened: `false`

## Status Semantics

`failed_closed` means the false-positive blocker triggered and the
susceptibility claim was rejected. `failed_open` means the blocker
triggered but the claim still passed.

## Geometric Interpretation

- `route_label_only_delta`: A name moves, but no basin geometry moves. There is no measured pre/post shape delta and no later re-entry expression.
- `reinforcement_schedule_only_delta`: The producer surface changes, but the substrate basin does not show a source-current susceptibility delta.
- `one_window_flux_transient`: A local flow pulse appears in one window, but it does not leave a durable basin deformation.
- `missing_later_reentry`: The basin may show an immediate difference, but there is no later return through the route or region where susceptibility should be expressed.
- `post_hoc_delta_construction`: The geometry is narrated after the fact instead of emitted as a source-current pre/post trace.
- `hidden_reinforcement`: The basin is held by an active producer channel, so persistence is not yet a substrate-carried geometric modification.
- `route_conditioned_row_missing_AP4`: The row depends on route-conditioned selection, but the selection axis is not made auditable.
- `proxy_or_target_conditioned_row_missing_AP5`: The row depends on target/proxy formation, but that target/proxy axis is not made auditable.
- `AP_gap_prose_only`: The dependency is outside the row's geometry record, so the row cannot be replayed as a controlled susceptibility claim.
- `peer_same_budget_missing`: A route-local change cannot be separated from scheduler/global drift without an equal-budget peer lane.
- `global_drift_not_rejected`: The whole substrate drifts, so no route-specific susceptibility update has been isolated.
- `semantic_learning_relabel`: A semantic label is substituted for a measured geometric susceptibility change.
- `native_support_relabel`: Producer support is treated as substrate-native support, which is outside the N22 claim ceiling.
- `phase8_relabel`: A classification artifact is promoted into native implementation, which N22 explicitly does not open.

## Checks

| Check | Passed |
| --- | --- |
| `source_i1_inventory_passed` | `true` |
| `source_i2_schema_passed` | `true` |
| `required_active_null_matrix_complete` | `true` |
| `candidate_evidence_fields_present_in_all_rows` | `true` |
| `schema_instantiated_without_expansion` | `true` |
| `label_only_null_visibly_violates_delta_gate` | `true` |
| `all_active_nulls_fail_closed` | `true` |
| `all_controls_reject_claims` | `true` |
| `ap_gap_active_nulls_present` | `true` |
| `artifact_manifest_present_but_not_positive` | `true` |
| `no_source_current_inputs_opened` | `true` |
| `no_su_or_n22c_rungs_above_control_scope` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `geometric_interpretations_present` | `true` |
| `no_local_absolute_paths` | `true` |

## Interpretation

I3 supports only fail-closed false-positive rejection discipline. It does
not support susceptibility update, durable geometry modification,
semantic learning, choice, agency, native support, sentience, Phase 8,
or ant-ecology implementation.
