# Prototype C I13.1-C Composed Runtime Replay / Stress

Status: `passed`

Acceptance state: `accepted_i13_1c_composed_runtime_replay_stress_backed_candidate`

Output digest: `1939e892718f1a63e1246ce580b402ff72da4a1102136b0945f2faaa3129d284`

Claim ceiling: `replay/stress-backed I13.1 composed Prototype C runtime candidate under a narrow local envelope; not final ecology success or semantic agency`

## Replay / Stress

Replay/stress-backed runtime candidate supported: `true`

Stable replays: `3 / 3`

Supported stress rows: `2`

Rejected stress rows: `2`

Minimum supported susceptibility margin: `0.0046`

Minimum supported differential response margin: `0.03825`

baseline plus near-floor proxy-pressure support; below susceptibility floor and high-challenge response-floor cases reject

| Stress Row | Decision | Susc. Margin | Diff. Margin |
|---|---|---:|---:|
| `baseline_replay_stress` | `supported` | `0.0256` | `0.0645` |
| `near_floor_proxy_pressure_supported` | `supported` | `0.0046` | `0.03825` |
| `below_susceptibility_floor_rejected` | `rejected` | `-0.008` | `0.0225` |
| `high_challenge_response_floor_rejected` | `rejected` | `0.0256` | `0.0645` |

## Checks

| Check | Passed |
|---|---|
| `i13_1b_source_passed` | `true` |
| `all_replays_stable` | `true` |
| `supported_stress_rows_present` | `true` |
| `rejected_stress_rows_present` | `true` |
| `control_stress_failed_closed` | `true` |
| `supported_margins_positive` | `true` |
| `replay_stress_backed_candidate_supported` | `true` |
| `final_success_still_blocked` | `true` |
| `ready_for_iteration_14` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
