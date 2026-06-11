# Loop-Driven Movement M4-M5 Classifier

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/classify_loop_driven_movement_m4_m5.py
```

Status: `passed`

## Summary

- Claim ceiling: `m5_candidate_control_limited`
- Budget surface: `node_only`
- Primary result: `m5_candidate_blocked_by_incomplete_direction_parity_controls`
- M5 candidate supported: `True`
- Full claim controls passed: `False`
- Loop-driven movement claim allowed: `False`
- True reversed E3 pulse control: `not_available_in_native_e3_animation_telemetry`
- Boundary report SHA-256 consumed: `75600c24540653f3bebccbbadce7087bf7d2985310a8f4d8d2624af83d6418c8`

## Lanes

| Lane | Level | M4 | M5 | dX | Response Count | Window | Primary Blocker |
|---|---|---:|---:|---:|---:|---:|---|
| `P0_pulse_disabled_control` | `M0_no_threshold_displacement` | `False` | `False` | `0.000000000` | `0` | `0.000` | `displacement_below_threshold` |
| `P1_symmetric_boundary_coupling_null` | `M0_no_threshold_displacement` | `False` | `False` | `-0.000000000` | `0` | `0.000` | `displacement_below_threshold` |
| `P2_asymmetric_boundary_coupling_forward` | `M5_repeated_loop_driven_boundary_response_candidate` | `True` | `True` | `0.083333333` | `4` | `12.000` | `claim_parity_controls_not_complete` |
| `P2_asymmetric_boundary_coupling_reversed` | `M5_repeated_loop_driven_boundary_response_candidate` | `True` | `True` | `-0.083333333` | `4` | `12.000` | `claim_parity_controls_not_complete` |

## Controls

| Control | Passed |
|---|---:|
| `pulse_disabled_negative` | `True` |
| `symmetric_null_negative` | `True` |
| `coupling_reversal_symmetry` | `True` |
| `scrambled_order_blocks_loop_driven_movement` | `True` |
| `true_reversed_e3_pulse_control_available` | `False` |

## Interpretation

Iteration 9 finds M5-style repeated boundary-response candidates in the asymmetric coupling lanes, but full loop-driven movement claims remain blocked because native true reversed-E3-pulse telemetry is not available in the current artifact set.

Response counts use `distinct_pulse_locked_windows`; repeated samples on the same plateau are counted as one window.

`pulse_locked_window_min_coupling` is derived per lane as `0.9 * max_observed_coupling`; it is not a fixed absolute coupling threshold.

The scrambled-order control is a synthetic classifier sanity check, not an empirical scrambled telemetry fixture lane. An empirical scrambled-pulse fixture remains deferred.

M4/M5 gates classify boundary-response structure. They do not replace the M0-M3 identity/shape ladder; a full movement claim would require both identity/shape support and completed M4/M5 direction-parity controls.

The distinct pulse-locked window count is coupled to the E3 pulse-cycle structure. It validates repeated pulse-locked responses, not substrate response between pulses or post-pulse persistence.

The classifier preserves the positive boundary-response signal, but it keeps movement, loop-driven movement, locomotion-like, adaptive-topology, biological, and agency claims blocked until the missing native true reversed-E3-pulse control is available.
