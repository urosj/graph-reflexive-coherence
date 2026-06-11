# N09 Iteration 6 GPR4 Single-Cycle Correction

Status: passed.

Iteration 6 schedules one selected memory-shaped correction packet and processes it through LGRC9V3 `step()`. The source-reservoir proxy returns to the declared band, while producer mutation and claim promotion remain blocked.

## Result

- GPR level: `GPR4`
- Claim ceiling: `single_cycle_proxy_correction_candidate`
- Selected candidate digest: `c6901dc48bc5862977cc9d9da4607e0a763ffd378f35459e9b5800265646a74d`
- Selected route: `route_b`
- Scheduled packet id: `lgrc9v3-packet-9c24c0be8ffcfd9f`
- Processed packet id: `lgrc9v3-packet-9c24c0be8ffcfd9f`
- Measurement before: `0.62`
- Measurement after: `0.55`
- Error before: `0.07`
- Error after: `0.0`
- In band after: `true`
- Outcome: `single_cycle_band_return`

## Budget

- Node-plus-packet before: `1.5`
- Node-plus-packet after: `1.5`
- Budget error: `0.0`
- Final in-flight packet total: `0.0`
- Final event queue count: `0`

## Controls

- `budget_discontinuity`: `node_plus_packet_budget_discontinuity` (passed: `true`)
- `claim_promotion`: `claim_promotion_blocked` (passed: `true`)
- `direct_rewrite`: `direct_rewrite_blocked` (passed: `true`)
- `no_response_to_error`: `no_response_to_error` (passed: `true`)
- `positive_response_reduces_error`: `single_cycle_error_not_reduced` (passed: `true`)
- `processed_packet_missing`: `processed_packet_missing` (passed: `true`)
- `scheduled_packet_missing`: `scheduled_packet_missing` (passed: `true`)
- `wrong_direction_response`: `wrong_direction_response` (passed: `true`)

## Validation Checks

- `claim_flags_all_false`: `true`
- `controls_all_passed`: `true`
- `final_in_flight_zero`: `true`
- `final_queue_empty`: `true`
- `manifest_digest_recomputes`: `true`
- `node_plus_packet_budget_within_tolerance`: `true`
- `packet_response_digest_recomputes`: `true`
- `packet_response_has_required_fields`: `true`
- `post_proxy_digest_recomputes`: `true`
- `pre_proxy_digest_recomputes`: `true`
- `pre_response_matches_gpr2_proxy`: `true`
- `producer_direct_mutation_not_used`: `true`
- `proxy_error_reduced`: `true`
- `regulation_response_digest_recomputes`: `true`
- `regulation_response_has_required_fields`: `true`
- `response_direction_correct`: `true`
- `schedule_request_digest_recomputes`: `true`
- `scheduled_packet_processed_by_step`: `true`
- `selected_candidate_effect_matches_error_direction`: `true`
- `selected_candidate_is_memory_lane_top_ranked`: `true`
- `single_cycle_band_return`: `true`
- `source_gpr3_artifact_digest_recomputes`: `true`
- `source_gpr3_status_passed`: `true`

## Acceptance State

Achieved. One proxy-conditioned packet correction is scheduled and processed by `step()`, the proxy moves in the expected direction back into the target band, budget remains within the fixed node-plus-packet tolerance, and claims remain blocked.

## Replay

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_6_gpr4_single_cycle_correction.py
```
