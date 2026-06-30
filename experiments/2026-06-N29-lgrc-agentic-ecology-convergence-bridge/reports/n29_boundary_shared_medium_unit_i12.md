# N29 Iteration 12 - Boundary / Shared-Medium Unit

Status: `passed`

Acceptance state: `accepted_boundary_shared_medium_unit_runtime_tranche_admission_pending_i12abc`

Output digest: `069c034eee8430a307da163ae9f9459978687cd0ad5d150de0f36c97bb4c4137`

## Main Read

I12 admits Prototype B as a boundary/shared-medium unit design. It does not claim prototype success yet. The source hierarchy is now explicit: N25.2 is the primary scoped MB6 runtime source, N16 supplies AP6 boundary discipline, N25/N25.1 explain the gap-to-implementation chain, and N24/N28 are context-only sources for medium capacity or reshaping.

The bridge unit has three required geometric parts:

- `basin_side_state`: N25.2 scoped MB6 multi-basin substrate evidence plus N16 AP6 internal-side discipline
- `shared_or_adjacent_medium`: N16 shared-medium separability controls, N25.2 child-basin / multi-basin interface, N24/N28 context only if capacity or reshaping is needed
- `counterpart_region`: N25.2 multi-basin counterpart-side records; N16 negative controls prevent label-only neighbor claims

Geometric interpretation:

Prototype B treats the ecology bridge unit as a three-part geometric surface: one basin-side region, one shared or adjacent medium channel, and one counterpart region. The important dynamic is not motion, choice, or colony behavior. It is whether the sides remain distinguishable while coupling/leakage through the medium is measurable and fail-closed controls reject merge, label-only, and visual-only success.

## Source Hierarchy

| Source | Consumed As | Status | Output Digest |
|---|---|---|---|
| `n16_closeout_ap6_boundary` | `boundary_discipline_source` | `passed` | `fb073257cde92b544ff5dbfb169d8177720cfba7622de09d913b670ce3fcebdf` |
| `n16_boundary_requirements` | `boundary_requirement_and_control_source` | `passed` | `383df2eb297e4a82cb71e0ce4a80aa3c506cc21ee2841b5ec010f33680229bdf` |
| `n25_closeout_bf_scope` | `sub_basin_and_gap_history_context` | `passed` | `2a1f19a2ce760275a223989b886c6a006ab1ccea33961b7bcf834c6cb22a565f` |
| `n25_1_phase8_bridge` | `phase8_multi_basin_extension_bridge` | `passed` | `396692475de004ddc8a586a501e1518b8316eebbf8f651304a76abeae25ae09e` |
| `n25_2_closeout_mb6` | `primary_scoped_multi_basin_runtime_source` | `passed` | `b92401da545899c7721ab42692827beb5b357bbd246d8991d7ad56649a6bbf03` |
| `n25_2_runtime_positive` | `runtime_candidate_source` | `passed` | `1a38c59b8e3149a4cdde1861237e45a0e9f2da8ecca6f548bf462313149527f1` |
| `n25_2_multi_window_replay` | `multi_window_child_basin_replay_source` | `passed` | `c297e0ef20296c37d54717df4d4d0adc3c44944e5fc2f828fd22ff789e67ec0a` |
| `n25_2_control_matrix` | `multi_basin_control_source` | `passed` | `62d1213a2a31b2704a064cb53a23cf1838e08850b92508a5cf6b592cfeee4011` |
| `n24_closeout_medium_capacity` | `medium_capacity_context_only` | `passed` | `2301cdb702c935419f4eaeaf9b102cb4a975571beb9fd375baed5ec235edcbb0` |
| `n28_closeout_medium_reshaping` | `medium_reshaping_context_only` | `passed` | `80ca5f1fcd75372fbd0f05065e67e077d140f4e9ff5931574f4d1beefee2ec4f` |
| `n29_i10_prototype_admission_schema` | `prototype_admission_schema_source` | `passed` | `fed49575d0ae9bc598d54cfbb6d01a87d69a3f8229fe466f580182b7e2c49f4d` |
| `n29_i111c_prototype_a_context` | `prior_prototype_context_only` | `passed` | `1f5eb9d6cb5b3a5b418d882814972e6ad93d1f605f6f630a335fe11c06a62fac` |

## Debt Records

| Debt ID | Meaning |
|---|---|
| `DEBT.I12.MULTI_BASIN_EXACT_ROW_EXTRACTION_REQUIRED` | Runtime source is available from N25.2, but I12-A must extract one exact bridge-unit row rather than inherit MB6 wholesale. |
| `DEBT.I12.CHILD_BASIN_REPLAY_CONTROL_LINEAGE_REQUIRED` | Child-basin records may be consumed only with replay/control lineage intact. |
| `DEBT.I12.MOBILE_BODY_READING_BLOCKED` | Mobile/body-like readings remain blocked; no mobile boundary or agent-body claim is opened. |
| `DEBT.I12.N16_N25_2_JOIN_REQUIRED` | N16 artifact-level shared-medium discipline and N25.2 runtime substrate must be joined before claiming a bridge exemplar. |
| `DEBT.I12.SEMANTIC_MEDIUM_LABELS_BLOCKED` | Trail, pheromone, resource, and colony-local medium language remain blocked labels. |

## I12-A/B/C Handoff

I12-A must extract or instantiate the source-current unit row. I12-B must run the fail-closed control matrix. I12-C must replay and stress the basin-side, shared/adjacent-medium, and counterpart-region separability.

Required controls:

- `label_only_boundary_control`
- `visual_only_boundary_control`
- `merge_leakage_as_success_control`
- `old_basin_thickening_as_counterpart_control`
- `producer_as_native_control`
- `n16_artifact_boundary_as_native_runtime_relabel_control`
- `n25_2_mb6_as_ant_ecology_relabel_control`
- `native_shared_medium_coordination_relabel_control`
- `semantic_trail_or_pheromone_relabel_control`
- `agent_body_relabel_control`

I12-A required candidate fields include:

- `runtime_family`
- `source_runtime_artifact_id`
- `source_runtime_artifact_digest`
- `unit_extraction_rule`
- `unit_id`
- `basin_side_region_id`
- `basin_side_support_or_coherence_trace`
- `basin_side_boundary_assignment`
- `medium_region_or_channel_id`
- `medium_coupling_or_leakage_trace`
- `medium_merge_pressure_metric`
- `counterpart_region_id`
- `counterpart_support_or_coherence_trace`
- `counterpart_separability_from_basin_side`
- `coupling_or_leakage_measure`
- `separability_measure`
- `merge_pressure_measure`
- `producer_residue`
- `claim_ceiling`
- `why_admitted`
- `why_not_stronger`

Hard gates before I13:

- `i12a_runtime_artifact_present` = `True`
- `i12a_basin_side_trace_present` = `True`
- `i12a_medium_trace_present` = `True`
- `i12a_counterpart_trace_present` = `True`
- `i12a_manifest_sha256_present` = `True`
- `i12b_all_controls_run` = `True`
- `i12b_failed_open_count` = `0`
- `i12b_merge_leakage_as_success_rejected` = `True`
- `i12b_old_basin_thickening_as_counterpart_rejected` = `True`
- `i12b_native_shared_medium_relabel_rejected` = `True`
- `i12b_agent_body_relabel_rejected` = `True`
- `i12c_replay_stress_complete` = `True`
- `i12c_counterpart_separability_survives_or_demotes` = `True`
- `i12c_merge_pressure_survives_or_demotes` = `True`
- `prototype_success_claimed` = `False`
- `native_shared_medium_coordination_opened` = `False`
- `agent_body_claim_opened` = `False`
- `multi_agent_interaction_opened` = `False`
- `semantic_trail_or_pheromone_substrate_opened` = `False`

## Claim Boundary

Allowed: admitted bounded boundary/shared-medium bridge unit pending I12-A/B/C runtime, controls, and replay/stress.

Blocked: agent body, organism/environment boundary, native colony boundary, native shared-medium coordination, semantic trail or pheromone substrate, resource ownership, multi-agent interaction, agency, life, sentience, native support, and Phase 8 completion.

## Checks

| Check | Passed |
|---|---|
| `all_required_sources_exist_and_parse` | `true` |
| `n16_consumed_as_boundary_discipline_not_native_shared_medium` | `true` |
| `n25_2_consumed_as_scoped_mb6_runtime_source` | `true` |
| `n25_and_n25_1_not_promoted_to_runtime_mb6` | `true` |
| `n24_n28_consumed_as_context_only` | `true` |
| `prototype_b_route_present_in_i10` | `true` |
| `unit_has_basin_medium_counterpart_parts` | `true` |
| `i12abc_handoff_defined` | `true` |
| `i12a_exact_row_extraction_required` | `true` |
| `i12b_expected_control_results_defined` | `true` |
| `i13_hard_gates_keep_next_family_closed` | `true` |
| `mobile_body_subclass_boundary_recorded` | `true` |
| `stable_debt_ids_present` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
