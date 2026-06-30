# Prototype C I13.1-B Composed Runtime Controls

Status: `passed`

Acceptance state: `accepted_i13_1b_composed_runtime_controls_fail_closed`

Output digest: `feca975ed081a275e90f01b81b23cb6fd9e7d5e821db32bd9f24c997ebab2138`

Claim ceiling: `control-backed I13.1 composed Prototype C runtime candidate; not final Prototype C success, semantic learning, choice, agency, native AP4/AP5, native support, or ecology success`

## Controls

Control-backed runtime candidate supported: `true`

Failed closed: `6`

Comparability controls passed: `1`

Failed open: `0`

| Control | Status | Interpretation |
|---|---|---|
| `no_prior_proxy_pressure_control` | `failed_closed` | control blocks the false-positive path while preserving the bounded composed runtime candidate |
| `label_only_susceptibility_delta_control` | `failed_closed` | control blocks the false-positive path while preserving the bounded composed runtime candidate |
| `reentry_removed_control` | `failed_closed` | control blocks the false-positive path while preserving the bounded composed runtime candidate |
| `hidden_direct_response_producer_control` | `failed_closed` | control blocks the false-positive path while preserving the bounded composed runtime candidate |
| `peer_same_budget_comparison_control` | `passed_as_comparability_control` | same-budget peer comparison supports row-local distinguishability |
| `semantic_learning_choice_goal_relabel_control` | `failed_closed` | control blocks the false-positive path while preserving the bounded composed runtime candidate |
| `native_ap4_ap5_support_relabel_control` | `failed_closed` | control blocks the false-positive path while preserving the bounded composed runtime candidate |

## Checks

| Check | Passed |
|---|---|
| `i13_1_source_passed` | `true` |
| `runtime_candidate_digest_stable` | `true` |
| `all_controls_have_status` | `true` |
| `failed_open_control_count_zero` | `true` |
| `control_backed_candidate_supported` | `true` |
| `final_success_still_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
