# N09 Iteration 7 GPR5 Repeated Bounded Regulation

Status: passed.

Iteration 7 repeats the GPR4 packet-correction pattern across four serialized regulation windows. The memory-shaped lane schedules and processes one correction packet per window. The no-memory comparator receives the same window inputs, but its candidates remain tied, so it does not schedule without an experiment-side tie-breaker.

## Result

- GPR level: `GPR5`
- Claim ceiling: `repeated_bounded_proxy_regulation_candidate`
- Window count: `4`
- Window input amount: `0.07`
- Memory lane outcome: `bounded_repeated_regulation`
- No-memory lane outcome: `policy_saturation`
- Memory lane post-correction measurements: `[0.55, 0.55, 0.55, 0.55]`
- No-memory comparator measurements: `[0.62, 0.69, 0.76, 0.83]`
- Max memory-lane post-correction error: `0.0`
- Max memory-lane budget error: `0.0`

## Interpretation

The positive evidence is repeated bounded regulation under a serialized producer-mediated scaffold: repeated window inputs push the proxy above band, memory-shaped route evidence authorizes the same correction route, and LGRC `step()` processes the packet work back to band each time. The no-memory comparator is useful because it shows that the repeated result depends on the scoped N08 memory surface; without it, the candidate set stays tied and the proxy drifts out of band.

This is not semantic goal understanding, agency, or constitutive native regulation. It remains a GPR5 candidate with a native-policy gap.

## Controls

- `budget_drift`: `budget_drift` (passed: `true`)
- `claim_promotion`: `claim_promotion_blocked` (passed: `true`)
- `cross_cycle_leakage`: `cross_cycle_leakage` (passed: `true`)
- `duplicate_proxy_update`: `duplicate_proxy_update` (passed: `true`)
- `hidden_target_drift`: `hidden_target_drift` (passed: `true`)
- `no_regulation_control`: `no_response_to_error` (passed: `true`)
- `stale_proxy_read`: `stale_proxy_read_blocked` (passed: `true`)
- `wrong_policy_control`: `wrong_direction_response` (passed: `true`)

## Validation Checks

- `claim_flags_all_false`: `true`
- `controls_all_passed`: `true`
- `manifest_digest_recomputes`: `true`
- `memory_cycle_digests_recompute`: `true`
- `memory_cycles_all_return_to_band`: `true`
- `memory_cycles_all_schedule_and_process`: `true`
- `memory_cycles_have_required_packet_response_fields`: `true`
- `memory_cycles_have_required_regulation_response_fields`: `true`
- `memory_error_rows_reference_current_proxy_rows`: `true`
- `memory_lane_classified_bounded`: `true`
- `memory_packet_response_digests_recompute`: `true`
- `memory_regulation_response_digests_recompute`: `true`
- `memory_selected_candidate_is_unique_top_ranked`: `true`
- `no_memory_comparator_drifted_out_of_band`: `true`
- `no_memory_comparator_records_unresolved_tie`: `true`
- `no_memory_cycle_digests_recompute`: `true`
- `same_policy_all_windows`: `true`
- `same_target_band_all_windows`: `true`
- `source_gpr3_artifact_digest_recomputes`: `true`
- `source_gpr3_status_passed`: `true`
- `source_gpr4_artifact_digest_recomputes`: `true`
- `source_gpr4_status_passed`: `true`

## Acceptance State

Achieved. Repeated proxy-conditioned cycles return the memory-shaped lane to the declared band with exact node-plus-packet accounting. The no-memory comparator records a tied/no-schedule failure mode, and all stronger claim flags remain blocked.

## Replay

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_7_gpr5_repeated_bounded_regulation.py
```
