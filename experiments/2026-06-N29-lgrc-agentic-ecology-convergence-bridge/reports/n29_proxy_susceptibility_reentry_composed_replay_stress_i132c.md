# Prototype C I13.2-C Buffered Runtime Replay / Stress

Status: `passed`

Acceptance state: `accepted_i13_2c_buffered_runtime_replay_stress_backed_candidate`

Output digest: `3672b90ef3f361f26bcd654708f10962dd4c4c2b833258b82e9997d15a7393fc`

Claim ceiling: `replay/stress-backed I13.2 buffered Prototype C runtime candidate under a local alternative envelope; not final ecology success or semantic agency`

## Replay / Stress

Replay/stress-backed runtime candidate supported: `true`

Stable replays: `3 / 3`

Supported stress rows: `2`

Rejected stress rows: `2`

Minimum supported susceptibility margin: `0.0436`

Minimum supported differential response margin: `0.14336`

baseline buffered and moderate proxy-pressure rows pass; buffer-removed and high-challenge rows reject

I13.2's buffered geometry remains supported under weaker high-challenge loads. The high-challenge rejection row therefore uses a floor-crossing challenge load rather than assuming any elevated challenge should reject.

| Stress Row | Decision | Susc. Margin | Diff. Margin |
|---|---|---:|---:|
| `baseline_buffered_replay_stress` | `supported` | `0.0712` | `0.19162` |
| `moderate_proxy_pressure_supported` | `supported` | `0.0436` | `0.14336` |
| `buffer_removed_rejected` | `rejected` | `-0.0092` | `0.03008` |
| `high_challenge_buffered_response_floor_rejected` | `rejected` | `0.0712` | `0.19162` |

## Checks

| Check | Passed |
|---|---|
| `i13_2b_source_passed` | `true` |
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
