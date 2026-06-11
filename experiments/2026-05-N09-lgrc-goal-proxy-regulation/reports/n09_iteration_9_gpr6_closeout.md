# N09 Iteration 9 GPR6 Artifact-Only Replay And Closeout

Status: passed.

Iteration 9 reconstructs the N09 Hypothesis A regulation chain from exported artifacts only. It closes the serialized producer/policy path and records Hypothesis B as staged behind native-policy blockers.

## Closeout

- GPR level: `GPR6`
- Claim ceiling: `artifact_only_goal_proxy_regulation_candidate`
- Hypothesis A status: `closed`
- Hypothesis B status: `staged_native_policy_gap`
- Hypothesis B blocker: `native_goal_proxy_regulation_policy_missing`
- N10 identity/support blocker: `n07_identity_withdrawal_baseline_not_available`

## N10 Handoff

- Regulation policy digest: `896133e8af4cdbb6cabb1436d9cb6f41a2ad1ad300f0ceca79f460d392358d40`
- Latest proxy surface digest: `e16abbd31147af9312ff37e4de308c6199ed385a3bbe9d8e441ed275fa82f7af`
- Error policy digest: `61c34d66e9416772b40a8db54dff3cf7a34f5a6ece4a18428a590f8d9594b706`
- Regulation response digest: `7f33759d102c3eee102f4b32bb515b9d0cf8eecb40cd22057de7c475dcde9d34`
- Memory surface digest: `b21c093d70245fab02088b8ebed42ac931629c41f6e45d618f5b5a67d9bea627`
- Identity support digest: `c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb`
- Regulation outcome tag: `bounded_repeated_regulation`
- Identity/support outcome tag: `identity_support_withdrawal_baseline_missing`
- Identity support lane consumption allowed: `false`

## Controls

- `artifact_runtime_fallback`: `runtime_state_fallback_blocked` (passed: `true`)
- `budget_violation`: `budget_violation` (passed: `true`)
- `claim_promotion`: `claim_promotion_blocked` (passed: `true`)
- `error_mismatch`: `proxy_error_mismatch` (passed: `true`)
- `native_policy_gap`: `native_goal_proxy_regulation_policy_missing` (passed: `true`)
- `processed_packet_missing`: `processed_packet_missing` (passed: `true`)
- `proxy_digest_mismatch`: `proxy_surface_digest_mismatch` (passed: `true`)
- `route_or_producer_missing`: `route_or_producer_evidence_missing` (passed: `true`)
- `scheduled_packet_missing`: `scheduled_packet_missing` (passed: `true`)
- `support_withdrawal_baseline_missing`: `n07_identity_withdrawal_baseline_not_available` (passed: `true`)

## Validation Checks

- `all_digests_recompute`: `true`
- `all_source_artifacts_passed`: `true`
- `artifact_only_validator_used`: `true`
- `claim_flags_all_false`: `true`
- `controls_all_passed`: `true`
- `gpr5_backbone_bounded`: `true`
- `gpr8_perturbation_recovered`: `true`
- `identity_support_blocker_preserved`: `true`
- `n10_handoff_fields_complete`: `true`
- `ordered_chain_reconstructed`: `true`
- `runtime_state_used`: `false`

## Acceptance State

Achieved. The proxy measurement, target/error policy, route/producer evidence, scheduled/processed packet work, repeated bounded regulation, perturbation recovery, support boundary, controls, and N10 handoff fields replay from artifacts only. All stronger agency, identity, ACO, locomotion, biological, personhood, and unrestricted claims remain blocked.

## Replay

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_9_gpr6_closeout.py
```
