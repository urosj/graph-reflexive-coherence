# N09 Iteration 3 GPR1 Proxy Measurement

Status: passed.

Iteration 3 emits one runtime-visible proxy measurement row from a live LGRC9V3 active-node state and one declared target-band row. It does not compute an error signal, schedule packets, call step(), mutate state, or emit regulation/claim evidence.

## Measurement

- Proxy surface digest: `4c0ed3d7a3a70607a1d8b4f175025d895cb7d190160dc0f1fc7cb9136157636f`
- Target band digest: `72ef4d4d3cc71289716af1cc8c1ad6ec176df92c37210dd58ea283d0589e8d8b`
- Regulated variable digest: `ba0c07db8285c471cbf5cc44b791f0ac01f42f562d5490409b446ba6160da9d9`
- Measurement value: `0.62` coherence
- Target band: `0.45` to `0.55` coherence
- Relation to band: `above_target_band`
- Runtime state digest: `9995d3daaca6b3bb84f7fdaa187ddba96f2e1d39c97b86781b7907b7d081406d`
- Packet ledger digest: `905a83adfb01428f82e6fff5bb6212d574a162c1b716ee772adf213f0f3d3362`

## Boundary

- GPR level: `GPR1`
- Claim ceiling: `goal_proxy_measurement_candidate`
- Regulation action enabled: `false`
- Error signal emitted: `false`
- Producer scheduling used: `false`
- `step()` called: `false`

## Controls

- `claim_promotion`: `claim_promotion_blocked` (passed: `true`)
- `hidden_proxy_source`: `hidden_proxy_source_rejected` (passed: `true`)
- `hidden_proxy_target`: `hidden_proxy_target_rejected` (passed: `true`)
- `missing_proxy_surface`: `proxy_surface_missing` (passed: `true`)
- `posthoc_target_change`: `posthoc_target_change_rejected` (passed: `true`)
- `proxy_surface_digest_mismatch`: `proxy_surface_digest_mismatch` (passed: `true`)

## Validation Checks

- `claim_flags_all_false`: `true`
- `controls_all_passed`: `true`
- `error_signal_not_emitted`: `true`
- `manifest_digest_matches`: `true`
- `measurement_is_not_hidden_fixture_state`: `true`
- `measurement_is_runtime_visible`: `true`
- `node_plus_packet_budget_error_zero`: `true`
- `producer_scheduling_not_used`: `true`
- `proxy_digest_recomputes`: `true`
- `proxy_row_has_required_fields`: `true`
- `regulated_variable_digest_recomputes`: `true`
- `regulation_action_disabled`: `true`
- `runtime_state_digest_referenced`: `true`
- `step_not_called`: `true`
- `target_band_digest_recomputes`: `true`
- `target_band_has_required_fields`: `true`
- `target_digest_referenced_by_proxy`: `true`

## Acceptance State

Achieved. Runtime-visible proxy condition and declared target band are serialized with digest and order evidence, without regulation action or claim promotion.

## Replay

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_3_gpr1_proxy_measurement.py
```
