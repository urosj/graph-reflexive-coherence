# Prototype C I13-B Mapping Relabel Controls

Status: `passed`

Acceptance state: `accepted_i13b_mapping_controls_fail_closed_no_runtime_claim`

Output digest: `9c2adba1a6d56c541ef21fd3d0967acb3af7046d01667c1089237179dadf20d9`

Claim ceiling: `fail-closed mapping/relabel controls over Prototype C source-backed parts; no runtime control-backed Prototype C`

## Controls

All controls failed closed: `true`

Runtime control matrix run: `false`

I13-A did not admit an exact source-current runtime row; I13-B can only test relabel/stitching controls over the mapping/extraction record.

| Control | Status | Rung Effect |
|---|---|---|
| `coverage_map_as_source_row_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `cross_experiment_stitching_without_source_digest_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `semantic_goal_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `semantic_choice_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `preference_ownership_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `intentional_return_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `identity_transfer_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `learning_as_semantic_knowledge_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `native_ap4_ap5_closure_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `native_support_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `ant_role_behavior_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |
| `ecology_success_relabel_control` | `failed_closed` | blocks runtime Prototype C; preserves mapping/debt record |

## Checks

| Check | Passed |
|---|---|
| `i13a_source_passed` | `true` |
| `required_controls_present` | `true` |
| `all_controls_failed_closed` | `true` |
| `failed_open_control_count_zero` | `true` |
| `runtime_claim_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
