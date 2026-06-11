# N09 Iteration 8 Perturbation, Withdrawal, And Support Checks

Status: passed.

Iteration 8 applies an explicit proxy perturbation and verifies that the memory-shaped GPR5 correction pattern returns the proxy to the declared band. It also serializes the support-withdrawal boundary: N07 withdrawal stability is not available, so support outcomes remain handoff tags rather than identity-acceptance claims.

## Perturbation Recovery

- GPR level: `GPR5`
- Claim ceiling: `repeated_bounded_proxy_regulation_candidate`
- Perturbation amount: `0.09`
- Before perturbation: `0.55`
- After perturbation: `0.64`
- After recovery: `0.55`
- Perturbation error: `0.09`
- Recovery error: `0.0`
- Recovery in band: `true`
- Recovery classification: `perturbation_recovered_to_band`
- Budget error: `0.0`

## Support Boundary

- Support withdrawal kind: `partial_support_weakening`
- Withdrawal depth: `0.25`
- Identity/support outcome tag: `identity_support_withdrawal_baseline_missing`
- Primary blocker: `n07_identity_withdrawal_baseline_not_available`

The support record is intentionally baseline-limited. It prevents the perturbation result from being overread as identity preservation, identity disruption, or identity acceptance.

## Controls

- `budget_discontinuity`: `budget_discontinuity` (passed: `true`)
- `claim_promotion`: `claim_promotion_blocked` (passed: `true`)
- `hidden_perturbation`: `hidden_perturbation_blocked` (passed: `true`)
- `hidden_reset`: `hidden_reset_blocked` (passed: `true`)
- `identity_acceptance_overclaim`: `identity_acceptance_overclaim` (passed: `true`)
- `support_label_only`: `support_label_only_blocked` (passed: `true`)
- `unsupported_recovery`: `unsupported_recovery` (passed: `true`)

## Validation Checks

- `claim_flags_all_false`: `true`
- `controls_all_passed`: `true`
- `identity_support_outcome_tag_valid`: `true`
- `manifest_digest_recomputes`: `true`
- `packet_response_digest_recomputes`: `true`
- `packet_response_has_required_fields`: `true`
- `perturbation_digest_recomputes`: `true`
- `perturbation_moved_proxy_out_of_band`: `true`
- `perturbation_record_has_required_fields`: `true`
- `perturbation_recovery_returned_to_band`: `true`
- `regulation_response_digest_recomputes`: `true`
- `regulation_response_has_required_fields`: `true`
- `source_gpr3_artifact_digest_recomputes`: `true`
- `source_gpr3_status_passed`: `true`
- `source_gpr5_artifact_digest_recomputes`: `true`
- `source_gpr5_status_passed`: `true`
- `support_withdrawal_baseline_gap_recorded`: `true`
- `support_withdrawal_digest_recomputes`: `true`
- `support_withdrawal_record_has_required_fields`: `true`

## Acceptance State

Achieved. The explicit perturbation is recovered through scheduled packet work with exact budget accounting. Support withdrawal is serialized but remains blocked by the missing N07 withdrawal baseline, and no agency or identity-acceptance claim is promoted.

## Replay

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_8_perturbation_withdrawal_support.py
```
