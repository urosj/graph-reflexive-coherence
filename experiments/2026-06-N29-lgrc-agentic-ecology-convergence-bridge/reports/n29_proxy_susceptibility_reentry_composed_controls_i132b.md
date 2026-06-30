# Prototype C I13.2-B Buffered Runtime Controls

Status: `passed`

Acceptance state: `accepted_i13_2b_buffered_runtime_controls_fail_closed`

Output digest: `1da84e47fa5e9130dceb5e074e8389a25384681bed63be37ac2eac38762a12d5`

Claim ceiling: `control-backed I13.2 buffered Prototype C runtime candidate; not final Prototype C success, semantic learning, choice, agency, native AP4/AP5, native support, or ecology success`

## Controls

Control-backed runtime candidate supported: `true`

Failed closed: `6`

Comparability controls passed: `1`

Failed open: `0`

| Control | Status | Interpretation |
|---|---|---|
| `buffer_lane_removed_control` | `failed_closed` | control blocks a buffered false-positive path while preserving the bounded alternative composed runtime candidate |
| `proxy_pressure_label_only_control` | `failed_closed` | control blocks a buffered false-positive path while preserving the bounded alternative composed runtime candidate |
| `same_budget_peer_buffer_copy_control` | `failed_closed` | control blocks a buffered false-positive path while preserving the bounded alternative composed runtime candidate |
| `reentry_order_inversion_control` | `failed_closed` | control blocks a buffered false-positive path while preserving the bounded alternative composed runtime candidate |
| `same_budget_peer_comparison_control` | `passed_as_comparability_control` | same-budget peer comparison supports buffered row-local distinguishability |
| `semantic_learning_choice_goal_relabel_control` | `failed_closed` | control blocks a buffered false-positive path while preserving the bounded alternative composed runtime candidate |
| `native_ap4_ap5_support_relabel_control` | `failed_closed` | control blocks a buffered false-positive path while preserving the bounded alternative composed runtime candidate |

## Checks

| Check | Passed |
|---|---|
| `i13_2_source_passed` | `true` |
| `runtime_candidate_digest_stable` | `true` |
| `all_controls_have_status` | `true` |
| `failed_open_control_count_zero` | `true` |
| `control_backed_candidate_supported` | `true` |
| `final_success_still_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
