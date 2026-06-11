# N04 Lane D1 Pulse Transport Baseline

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_pulse_transport_baseline.py
```

Status: `passed`
Claim ceiling: `pulse_transport_only`

## Positive Lane

- Peak sequence: `[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]`
- Peak source: `argmax_post_transfer_pulse_field`
- Final peak: `14`
- Max hop distance: `1`
- Nonlocal jump detected: `False`
- Max budget error: `0.0`
- Minimum pulse state: `0.0`
- Pulse width max: `1`
- Pulse peak mass min: `1.0`

## Controls

- `pulse_disabled`: `pulse_absent`
- `static_pulse`: `no_propagation`
- `blocked_edge`: `local_transport_blocked`
- `wrong_direction`: `wrong_direction_for_positive_path`
- `budget_violating_synthetic`: `budget_gate_failed`

## Interpretation

D1 proves only local pulse transport. The pulse peak advances by
local one-hop transfers on the S0 chain with exact pulse-budget
conservation and nonnegative state. Geometry coupling, traveling
deformation, movement, loop-driven movement, and native LGRC pulse
substrate claims remain blocked.
