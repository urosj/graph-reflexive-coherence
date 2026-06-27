# N23 Iteration 3 - Active Nulls And Failure Baselines

## Summary

Status: `passed`

Acceptance state: `accepted_active_nulls_fail_closed_no_positive_evidence`

Output digest: `05b65af917c90a8b16286c9c8b78386199188a23fa4dffa1ea3d503c165777dd`

Iteration 3 instantiates the frozen I2 schema as active nulls. It does
not expand the schema, open positive live-continuation evidence, or
assign LC/N23-C rungs above control scope.

## Active Null Matrix

| Row | Null | Result | Rung Effect |
| --- | --- | --- | --- |
| `n23_i3_row_01_fake_alternative_control` | `fake_alternative` | `failed_closed` | `blocks LC2 and stronger` |
| `n23_i3_row_02_single_branch_relabel_control` | `single_branch_relabel` | `failed_closed` | `blocks LC2 and stronger` |
| `n23_i3_row_03_post_hoc_selected_branch_control` | `post_hoc_selected_branch` | `failed_closed` | `blocks LC3 and stronger` |
| `n23_i3_row_04_producer_preference_injection_control` | `producer_preference_injection` | `failed_closed` | `blocks LC3, LC4, LC5, LC6, and unsafe selection claims` |
| `n23_i3_row_05_random_tie_as_collapse_control` | `random_tie_as_collapse` | `failed_closed` | `blocks LC3 and stronger` |
| `n23_i3_row_06_missing_counterfactual_retention_control` | `missing_counterfactual_retention` | `failed_closed` | `blocks LC3 and stronger` |
| `n23_i3_row_07_N22_susceptibility_as_choice_relabel_control` | `inherited_susceptibility_as_choice` | `failed_closed` | `blocks susceptibility-conditioned LC5 and stronger` |
| `n23_i3_row_08_route_conditioned_row_missing_AP4` | `missing_ap4_dependency` | `failed_closed` | `blocks AP4-relevant LC5 and stronger` |
| `n23_i3_row_09_proxy_conditioned_row_missing_AP5` | `missing_ap5_dependency` | `failed_closed` | `blocks proxy-conditioned LC rows` |
| `n23_i3_row_10_AP_gap_prose_only` | `ap_gap_prose_only` | `failed_closed` | `blocks AP-dependent LC rows` |
| `n23_i3_row_11_semantic_choice_relabel` | `semantic_choice_relabel` | `failed_closed` | `blocks all LC support and unsafe choice claims` |
| `n23_i3_row_12_agency_relabel` | `agency_relabel` | `failed_closed` | `blocks all LC support and unsafe agency claims` |
| `n23_i3_row_13_native_support_relabel` | `native_support_relabel` | `failed_closed` | `blocks all LC support and unsafe native-support claims` |
| `n23_i3_row_14_phase8_relabel` | `phase8_relabel` | `failed_closed` | `blocks all LC support and unsafe Phase 8 claims` |

## Summary Counts

- Rows: `14`
- Failed closed rows: `14`
- Failed open rows: `0`
- Positive live-continuation evidence opened: `false`

## Status Semantics

`failed_closed` means the false-positive blocker triggered and the
unsafe/null claim was rejected. It satisfies the negative-control
gate; it does not automatically demote future positive rows.

These rows are source-current-shaped null fixtures only:
`trace_admissibility = active_null_fixture_only_not_positive_evidence`,
`positive_evidence_admissible = false`, and
`control_execution_kind = schema_instantiation_only`.

The N23-C ceiling after I3 is
`N23-C1_active_null_control_discipline_established`; no final
closeout rung is assigned.

## Row Field Policy

I3 rows use all `80` I2 candidate fields plus a declared active-null
metadata extension set. A validation check requires each row's field
set to equal `I2 required fields U active_null_extension_fields`.

## Geometric Interpretation

- `fake_alternative_control`: The graph has alternative labels but not alternative source-current branch geometry. No pre-collapse branch basin separates from the substrate, so there is nothing geometric to collapse.
- `single_branch_relabel_control`: A single continuation lane remains a lane, not a live branch set. There is no simultaneous geometric plurality for a collapse event to resolve.
- `post_hoc_selected_branch_control`: The branch that wins is named after the geometry already ended. That gives a narrative selection, not an in-collapse geometric reason carried by the run.
- `producer_preference_injection_control`: The continuation is injected through a producer preference surface. The selected lane is not selected by support, coherence, boundary, flux, or route geometry.
- `random_tie_as_collapse_control`: Both branches remain geometrically tied. A random schedule chooses an index, but no branch-specific support, coherence, or flux advantage explains the collapse.
- `missing_counterfactual_retention_control`: A selected continuation can be seen, but the unselected branch has no immutable pre-collapse trace. Without that retained audit edge, the run cannot distinguish collapse from a single-path history.
- `N22_susceptibility_as_choice_relabel_control`: The old susceptibility delta is used as an explanation, but no N23 source-current branch expresses it during collapse. The cause is inherited context, not live selection geometry.
- `route_conditioned_row_missing_AP4`: The row depends on route-shaped selection, but the AP4 gap is not recorded in the row. The route geometry may exist, yet its claim dependency is not auditable.
- `proxy_conditioned_row_missing_AP5`: A support/proxy target is used to value the branch, but the AP5 gap is not row-local. The target-like pressure is therefore not admissible collapse evidence.
- `AP_gap_prose_only`: The caveat sits outside the replayable row. A future reader cannot tell whether the selection geometry depends on AP4/AP5 gaps by inspecting the artifact itself.
- `semantic_choice_relabel`: A semantic label replaces the branch geometry. No live branch set, collapse trace, or counterfactual retention is present.
- `agency_relabel`: A high-level agency word is placed on the artifact, but no branch selection geometry is added. The graph remains claim metadata, not agency evidence.
- `native_support_relabel`: Producer scaffolding is mistaken for substrate-carried support. The substrate has not generated the branch enumeration or support surface natively.
- `phase8_relabel`: A schema artifact is promoted into native implementation. No new LGRC producer surface, source-current branch geometry, or runtime mutation has been added.

## Checks

| Check | Passed |
| --- | --- |
| `source_i1_inventory_passed` | `true` |
| `source_i2_schema_passed` | `true` |
| `source_digest_chain_aligned` | `true` |
| `required_active_null_matrix_complete` | `true` |
| `canonical_controls_covered` | `true` |
| `candidate_evidence_fields_present_in_all_rows` | `true` |
| `row_field_set_equals_i2_required_plus_active_null_extensions` | `true` |
| `schema_instantiated_without_expansion` | `true` |
| `active_null_fixtures_not_positive_evidence` | `true` |
| `all_active_nulls_fail_closed` | `true` |
| `failed_closed_semantics_are_not_positive_demotions` | `true` |
| `required_trace_status_fields_present` | `true` |
| `susceptibility_trace_applicability_scoped` | `true` |
| `trace_row_condition_blockers_are_targeted` | `true` |
| `ap_gap_active_nulls_present` | `true` |
| `n22_inheritance_blocker_executed` | `true` |
| `artifact_manifest_fields_present_but_not_positive` | `true` |
| `no_source_current_inputs_opened` | `true` |
| `no_lc_or_n23c_rungs_above_control_scope` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `geometric_interpretations_present` | `true` |
| `no_local_absolute_paths` | `true` |

## Boundary

I3 can block false-positive paths, but it cannot support live branch
existence, collapse, counterfactual retention, replay-backed LC
rungs, AP4 bridge evidence, semantic choice, agency, native support,
sentience, Phase 8, or ant-ecology implementation.
