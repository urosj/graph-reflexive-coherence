# N09 Iteration 4 GPR2 Error Signal

Status: passed.

Iteration 4 computes a proxy error from the serialized Iteration 3 proxy measurement row and target-band row. It does not read live runtime state, emit route/eligibility evidence, schedule packets, call step(), or perform regulation.

## Error Signal

- Error signal digest: `a82a3a9c72aacfe7935c8f332d333aef0eb44d26982ced4040539403cfc09e48`
- Proxy surface digest: `4c0ed3d7a3a70607a1d8b4f175025d895cb7d190160dc0f1fc7cb9136157636f`
- Target band digest: `72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b`
- Error metric: `signed_distance_to_declared_band`
- Formula: `measurement_value - upper_bound`
- Measurement value: `0.62`
- Bounds: `0.45` to `0.55`
- Error value: `0.07`
- Error direction: `decrease_proxy`
- In band: `false`

## Boundary

- GPR level: `GPR2`
- Claim ceiling: `proxy_error_signal_candidate`
- Artifact-only computation: `true`
- Runtime state used for error computation: `false`
- Regulation action enabled: `false`
- Eligibility or route evidence emitted: `false`
- Producer scheduling used: `false`
- `step()` called: `false`

## Controls

- `claim_promotion`: `claim_promotion_blocked` (passed: `true`)
- `error_policy_missing`: `error_policy_missing` (passed: `true`)
- `hidden_reward_input`: `hidden_reward_or_goal_label_rejected` (passed: `true`)
- `order_inversion`: `artifact_order_inversion` (passed: `true`)
- `posthoc_threshold_change`: `posthoc_target_change_rejected` (passed: `true`)
- `proxy_error_mismatch`: `error_signal_digest_mismatch` (passed: `true`)

## Validation Checks

- `claim_flags_all_false`: `true`
- `computed_from_serialized_proxy_and_target`: `true`
- `controls_all_passed`: `true`
- `eligibility_or_route_evidence_not_emitted`: `true`
- `error_direction_recomputes`: `true`
- `error_policy_digest_recomputes`: `true`
- `error_row_has_required_fields`: `true`
- `error_signal_digest_recomputes`: `true`
- `error_value_recomputes`: `true`
- `event_order_monotonic`: `true`
- `in_band_recomputes`: `true`
- `manifest_digest_recomputes`: `true`
- `producer_scheduling_not_used`: `true`
- `proxy_digest_recomputes`: `true`
- `regulation_action_disabled`: `true`
- `runtime_state_not_used_for_error_computation`: `true`
- `source_gpr1_artifact_digest_recomputes`: `true`
- `source_gpr1_status_passed`: `true`
- `source_gpr1_was_measurement_only`: `true`
- `step_not_called`: `true`
- `target_band_digest_recomputes`: `true`

## Acceptance State

Achieved. Proxy error is computed from serialized runtime-visible evidence under the declared error policy, and hidden reward/target controls fail closed.

## Replay

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_4_gpr2_error_signal.py
```
