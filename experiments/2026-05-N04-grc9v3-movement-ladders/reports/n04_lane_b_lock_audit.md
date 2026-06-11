# N04 Lane B Lock Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/audit_lane_b_direction_parity_lock.py
```

Status: `passed`

## Checks

| Check | Passed |
|---|---:|
| `native_reversed_telemetry_validation` | `True` |
| `same_fixture_and_mapping` | `True` |
| `only_pulse_direction_changes` | `True` |
| `matched_metrics_recomputed_from_timeseries` | `True` |
| `controls_still_negative` | `True` |
| `claim_flag_consistency` | `True` |

## Acceptance Statement

Lane B resolves the Iteration 9 direction-parity blocker. True native counter-clockwise E3 telemetry is available and validated. When run through the same fixed S0 boundary-coupled fixture and frozen M4/M5 classifier, the native forward E3 lane produces dX=+0.083333333 and the native reversed E3 lane produces dX=-0.083333333, with matched boundary_coupling_score=0.25 and matched distinct pulse-locked response windows=4. The M5 candidate gate and full direction-parity gate pass. The upgraded claim ceiling is m5_direction_parity_supported_boundary_response. This supports a native direction-parity-controlled repeated loop-driven boundary-response candidate, while movement, locomotion-like, adaptive-topology, M6, biological, agency, and inherited-N03 claims remain blocked.
