# N26 Iteration 3 - Active Nulls And Failure Baselines

Status: `passed`

Acceptance state: `accepted_active_nulls_fail_closed_no_positive_proxy_evidence`

## Scope

Iteration 3 instantiates the I2 controls as active nulls. It opens no positive proxy evidence.

## Ceiling

```text
i1_output_digest = b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a
source_schema_output_digest = bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070
source_contract_row_digest = 5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61
source_consumable_contract_row_digest = 99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec
candidate_pd_ladder_rung = not_assigned_active_null_control_only
n26_closeout_ceiling = N26-C3_active_nulls_fail_closed
positive_proxy_evidence_opened = false
proxy_derivation_opened = false
proxy_divergence_opened = false
proxy_collapse_opened = false
ap5_bridge_status = not_supported_active_null_only
```

## Active Null Rows

| Row | Control | Decision | Status | Rung Effect |
| --- | --- | --- | --- | --- |
| `n26_i3_null_01_source_digest_mismatch` | `source_digest_mismatch_control` | `rejected` | `failed_closed` | `blocks_all_positive_proxy_support` |
| `n26_i3_null_02_lower_stack_input_missing` | `lower_stack_input_missing_control` | `rejected` | `failed_closed` | `blocks_PD2_or_stronger` |
| `n26_i3_null_03_proxy_metric_trace_missing` | `proxy_metric_trace_missing_control` | `rejected` | `failed_closed` | `blocks_PD2_or_stronger` |
| `n26_i3_null_04_proxy_metric_not_replayable` | `proxy_metric_not_replayable_control` | `rejected` | `failed_closed` | `blocks_PD3_or_stronger` |
| `n26_i3_null_05_basin_persistence_capacity_trace_missing` | `basin_persistence_capacity_trace_missing_control` | `rejected` | `failed_closed` | `blocks_PD2_or_stronger` |
| `n26_i3_null_06_support_coherence_floor_missing` | `support_coherence_floor_missing_control` | `rejected` | `failed_closed` | `blocks_PD2_or_stronger` |
| `n26_i3_null_07_proxy_basin_measurement_not_independent` | `proxy_basin_measurement_not_independent_control` | `rejected` | `failed_closed` | `blocks_PD4_or_stronger` |
| `n26_i3_null_08_scoped_mb6_scope_id_missing` | `scoped_mb6_scope_id_missing_control` | `rejected` | `failed_closed` | `blocks_all_positive_proxy_support` |
| `n26_i3_null_09_derived_report_only_positive_row` | `derived_report_only_positive_row_control` | `rejected` | `failed_closed` | `blocks_PD2_or_stronger` |
| `n26_i3_null_10_artifact_manifest_failure` | `artifact_manifest_failure_control` | `rejected` | `failed_closed` | `blocks_all_positive_proxy_support` |
| `n26_i3_null_11_proxy_label_only` | `proxy_label_only_control` | `rejected` | `failed_closed` | `blocks_PD2_or_stronger` |
| `n26_i3_null_12_post_hoc_target_digest` | `post_hoc_target_digest_control` | `rejected` | `failed_closed` | `blocks_PD2_or_stronger` |
| `n26_i3_null_13_hidden_proxy_policy` | `hidden_proxy_policy_control` | `rejected` | `failed_closed` | `blocks_substrate_carried_proxy_claim` |
| `n26_i3_null_14_proxy_only_improvement` | `proxy_only_improvement_control` | `rejected` | `failed_closed` | `blocks_PD4_proxy_divergence` |
| `n26_i3_null_15_proxy_improves_basin_also_improves` | `proxy_improves_basin_also_improves_control` | `rejected` | `failed_closed` | `blocks_PD4_proxy_divergence` |
| `n26_i3_null_16_proxy_improves_basin_unmeasured` | `proxy_improves_basin_unmeasured_control` | `rejected` | `failed_closed` | `blocks_PD4_proxy_divergence` |
| `n26_i3_null_17_basin_degradation_hidden_by_proxy` | `basin_degradation_hidden_by_proxy_control` | `rejected` | `failed_closed` | `blocks_positive_proxy_success_claim` |
| `n26_i3_null_18_unscoped_mb6_consumption` | `unscoped_mb6_consumption_control` | `rejected` | `failed_closed` | `blocks_all_positive_proxy_support` |
| `n26_i3_null_19_front_capacity_backfill` | `front_capacity_backfill_control` | `rejected` | `failed_closed` | `blocks_unscoped_substrate_upgrade` |
| `n26_i3_null_20_peer_basin_missing` | `peer_basin_missing_control` | `rejected` | `failed_closed` | `blocks_PD4_or_stronger` |
| `n26_i3_null_21_perturbation_mismatch` | `perturbation_mismatch_control` | `rejected` | `failed_closed` | `blocks_PD5_proxy_collapse` |
| `n26_i3_null_22_perturbation_digest_missing` | `perturbation_digest_missing_control` | `rejected` | `failed_closed` | `blocks_PD5_proxy_collapse` |
| `n26_i3_null_23_basin_deepened_survivor_missing` | `basin_deepened_survivor_missing_control` | `rejected` | `failed_closed` | `blocks_PD5_proxy_collapse` |
| `n26_i3_null_24_proxy_collapse_result_trace_missing` | `proxy_collapse_result_trace_missing_control` | `rejected` | `failed_closed` | `blocks_PD5_proxy_collapse` |
| `n26_i3_null_25_ap5_gap_prose_only` | `AP5_gap_prose_only_control` | `rejected` | `failed_closed` | `blocks_AP5_bridge_and_PD2_or_stronger` |
| `n26_i3_null_26_missing_ap5_dependency_status` | `missing_ap5_dependency_status_control` | `rejected` | `failed_closed` | `blocks_AP5_bridge_and_PD2_or_stronger` |
| `n26_i3_null_27_n15_context_as_native_ap5` | `n15_context_as_native_ap5_control` | `rejected` | `failed_closed` | `blocks_AP5_bridge` |
| `n26_i3_null_28_n19_nat3_as_ap5_closeout` | `n19_nat3_as_ap5_closeout_control` | `rejected` | `failed_closed` | `blocks_AP5_bridge` |
| `n26_i3_null_29_semantic_goal_relabel` | `semantic_goal_relabel_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_30_semantic_choice_relabel` | `semantic_choice_relabel_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_31_agency_relabel` | `agency_relabel_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_32_native_support_relabel` | `native_support_relabel_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_33_n25_2_mb6_as_native_support` | `n25_2_mb6_as_native_support_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_34_n25_2_mb6_as_agency_sentience_ant_ecology` | `n25_2_mb6_as_agency_sentience_ant_ecology_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_35_sentience_relabel` | `sentience_relabel_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_36_phase8_completion_relabel` | `phase8_completion_relabel_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |
| `n26_i3_null_37_ant_ecology_relabel` | `ant_ecology_relabel_control` | `rejected` | `failed_closed` | `blocks_unsafe_claim` |

## Geometric Interpretation

- `source_digest_mismatch_control`: The row is attached to a different source state than the admitted proxy contract and scoped substrate chain, so its geometry cannot inherit the N26 schema boundary.
- `lower_stack_input_missing_control`: A proxy value is asserted without the lower LGRC substrate state that would make the proxy source-current.
- `proxy_metric_trace_missing_control`: The proxy cannot be evaluated as geometry if the metric itself has no source-current trace.
- `proxy_metric_not_replayable_control`: The metric is a transient annotation rather than a stable replayable quantity over the basin substrate.
- `basin_persistence_capacity_trace_missing_control`: The row cannot claim proxy divergence if the basin continuation capacity is not measured independently of the proxy.
- `support_coherence_floor_missing_control`: The proxy cannot be compared against basin persistence if the basin support and coherence floors are not visible.
- `proxy_basin_measurement_not_independent_control`: The row cannot show divergence if proxy and basin traces collapse into one measurement channel.
- `scoped_mb6_scope_id_missing_control`: The row points at multi-basin substrate but does not identify the scoped basin set it is allowed to consume.
- `derived_report_only_positive_row_control`: A narrative artifact can describe a proxy hypothesis, but cannot act as source-current proxy geometry.
- `artifact_manifest_failure_control`: The row cannot be replayed or audited if the trace artifacts are not role-labeled and digest-checked.
- `proxy_label_only_control`: A proxy name is attached to the basin, but no source-current metric, target digest, or lower-stack derivation exists.
- `post_hoc_target_digest_control`: The target surface is stitched around the observed result instead of being fixed before the trace is evaluated.
- `hidden_proxy_policy_control`: The apparent proxy is producer/policy mediated rather than visible as a declared source-current runtime or analysis policy.
- `proxy_only_improvement_control`: A proxy score rises, but no independent basin continuation surface shows whether the basin actually deepened or stalled.
- `proxy_improves_basin_also_improves_control`: Both surfaces move in the same favorable direction, so the row may describe proxy alignment but not proxy divergence.
- `proxy_improves_basin_unmeasured_control`: A rising proxy score cannot diverge from an unobserved basin surface; the basin side of the contrast is absent.
- `basin_degradation_hidden_by_proxy_control`: The proxy surface looks better while the basin floor worsens; this cannot be counted as success or divergence support without controls.
- `unscoped_mb6_consumption_control`: The multi-basin substrate is generalized beyond the scoped basin IDs that N25.2 allowed N26 to consume.
- `front_capacity_backfill_control`: A topology-birth companion cannot replace the scoped child-basin runtime/replay substrate required by N25.2.
- `peer_basin_missing_control`: The row cannot distinguish route-local proxy divergence from global drift if no peer/control basin is present.
- `perturbation_mismatch_control`: Collapse cannot be inferred if the two paths are not challenged by the same perturbation geometry.
- `perturbation_digest_missing_control`: The proxy and basin paths cannot be proven to share the same challenge geometry when the perturbation envelope is not digested.
- `basin_deepened_survivor_missing_control`: A proxy path failure is only failure; collapse requires a basin deepened path surviving the same envelope.
- `proxy_collapse_result_trace_missing_control`: The collapse claim has no auditable source-current result surface, so a proxy-optimized failure cannot be classified as collapse.
- `AP5_gap_prose_only_control`: Proxy/target participation cannot be smuggled through narrative; row-local AP5 status and reason are required.
- `missing_ap5_dependency_status_control`: A proxy/target-forming row cannot inherit AP5 context silently; the row-local dependency state must be explicit.
- `n15_context_as_native_ap5_control`: N15 can supply historical artifact-level proxy context, but it is not native AP5 evidence for N26.
- `n19_nat3_as_ap5_closeout_control`: N19 records the AP5 NAT4 gap; using that gap record as closeout would invert the classification boundary.
- `semantic_goal_relabel_control`: A digest-bounded target surface is not a semantic goal or ownership claim.
- `semantic_choice_relabel_control`: A contrast between proxy and basin traces does not establish choice or intention.
- `agency_relabel_control`: Even a future controlled proxy-collapse row would remain artifact-level evidence below agency.
- `native_support_relabel_control`: N25.2 substrate and N26 proxy traces are not native support channels.
- `n25_2_mb6_as_native_support_control`: Scoped multi-basin substrate is a permitted N26 geometry surface, not a native support channel.
- `n25_2_mb6_as_agency_sentience_ant_ecology_control`: A scoped substrate handoff does not implement agency, sentience, or the ant ecology bridge.
- `sentience_relabel_control`: Proxy failure/survival geometry does not become sentience or read-back identity.
- `phase8_completion_relabel_control`: N26 may consume Phase 8 multi-basin substrate, but cannot close Phase 8 implementation.
- `ant_ecology_relabel_control`: Proxy divergence on scoped substrate is still pre-ecology evidence and cannot specify or implement ant ecology.

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i2_schema_passed` | `true` | `{"acceptance_state": "accepted_proxy_divergence_collapse_schema_frozen_no_proxy_evidence", "status": "passed"}` |
| `schema_digest_matches_expected` | `true` | `{"output_digest": "bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070"}` |
| `source_chain_digests_match_expected` | `true` | `{"i1_output_digest": "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a", "source_consumable_contract_row_digest": "99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec", "source_contract_row_digest": "5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61"}` |
| `all_required_controls_instantiated` | `true` | `{"required_control_count": 37, "row_control_count": 37}` |
| `all_controls_failed_closed` | `true` | `{"row_count": 37}` |
| `failed_open_controls_zero` | `true` | `{"failed_open_rows": []}` |
| `source_current_derivation_blockers_present` | `true` | `{"required_source_current_blockers": ["artifact_manifest_failure_control", "derived_report_only_positive_row_control", "lower_stack_input_missing_control", "proxy_basin_measurement_not_independent_control", "proxy_metric_not_replayable_control", "scoped_mb6_scope_id_missing_control", "support_coherence_floor_missing_control"]}` |
| `no_positive_proxy_evidence_opened` | `true` | `"active nulls only"` |
| `no_positive_pd_rung_assigned` | `true` | `{"active_null_rung": "not_assigned_active_null_control_only"}` |
| `active_null_rows_are_not_positive_evidence` | `true` | `"null rows can block false positives but cannot support PD evidence"` |
| `ap5_not_applicable_limited_to_null_rows` | `true` | `"no positive proxy or target formation claim is made"` |
| `scoped_mb6_claims_fail_closed` | `true` | `"unscoped MB6 and front-capacity backfill remain blocked"` |
| `unsafe_claim_flags_false` | `true` | `"all unsafe claim flags are false for every null row"` |
| `no_absolute_paths_in_records` | `true` | `"all paths are repository-relative"` |

## Claim Boundary

active-null and failure-baseline matrix only; no proxy derivation, proxy divergence, proxy collapse, AP5 bridge, semantic goal, agency, native support, sentience, Phase 8, ant ecology, or unscoped multi-basin claim
