# N30 Iteration 7 - Replay, Controls, And Medium Debt Matrix

Status: `passed`

Acceptance state: `accepted_replay_control_backed_C5_candidate_pending_I8_closeout`

Output digest: `46f7eba93fa206355f4dc3eb5b2ae8e70dd1126eba975030a2e2fc15f1603fec`

## Interpretation

I7 consumes the original I6/I6-A generative-edge M2 candidates and the
alternative I6-B/I6-C circulatory M2 candidate. It runs the required replay
modes and reinstantiates all I2/I3 fail-closed controls against each positive
row. All candidate rows pass artifact replay, duplicate replay, snapshot/load
replay, and later-response metric recomputation, and all false-positive control
paths fail closed.

This supports a replay/control-backed N30-C5 candidate, but not final N30
closeout. I8 still has to classify the final rung, record the candidate N31
interface status as part of the post-N30 spiral handoff, and preserve
medium/producer debt.

## Candidate Rows

- n30_i6_row_01_i5_single_shell_later_eligibility_candidate: family=original_generative, rung=M2_replay_control_backed_C5_candidate, controls=20, decision=supported_N30-C5_candidate_pending_I8_closeout
- n30_i6_row_02_i5a_split_shell_later_eligibility_candidate: family=original_generative, rung=M2_replay_control_backed_C5_candidate, controls=20, decision=supported_N30-C5_candidate_pending_I8_closeout
- n30_i6b_row_01_i4f_circulatory_route_eligibility_candidate: family=alternative_circulatory, rung=M2_replay_control_backed_C5_candidate, controls=20, decision=supported_N30-C5_candidate_pending_I8_closeout

## Key Fields

```text
candidate_row_count = 3
required_control_count = 20
total_control_result_count = 60
failed_open_control_count = 0
all_required_replay_modes_passed = true
all_required_controls_failed_closed = true
n30_c5_candidate_supported = true
final_n30_c5_claim_allowed = false
final_n30_c6_claim_allowed = false
post_n30_handoff_mode = cross_project_spiral_pending_I8
agentic_ecology_demand_pass_recommended = true
candidate_n31_interface_available_pending_i8 = true
candidate_n31_selected = false
next_lgrc_experiment_fixed = false
```

## Artifacts

| Role | Path |
|---|---|
| i7_replay_control_matrix | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_replay_controls_i7_artifacts/i7_replay_control_matrix.json` |
| i7_medium_debt_matrix | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_replay_controls_i7_artifacts/i7_medium_debt_matrix.json` |
| i7_claim_boundary_guard | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_replay_controls_i7_artifacts/i7_claim_boundary_guard.json` |

## Checks

- source_inputs_passed: true
- all_candidate_rows_covered: true
- all_required_replay_modes_passed: true
- all_required_controls_failed_closed: true
- c5_candidate_supported_but_final_closeout_blocked: true
- medium_debt_and_producer_residue_recorded: true
- artifact_manifest_sha256_matches: true
- no_absolute_paths_in_records: true
