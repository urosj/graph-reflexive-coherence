# N04 Iteration 10 Failure Review

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iteration10_failure_review.py
```

Status: `passed`
Review subject: `Iteration 10 M6 failure`
Claim ceiling after failure: `m5_direction_parity_supported_boundary_response`

## Failure

- Iteration 10 status: `passed_fail_closed`
- M6 opened: `False`
- M6 gate passed: `False`
- Primary blocker: `no_feedback_path_from_boundary_response_to_pulse_generation`

## What Passed Before The Failure

- `lane_b_locked_baseline_available`: `True`
- `m5_direction_parity_supported_boundary_response`: `True`
- `repeated_boundary_response_measured`: `True`
- `bounded_boundary_fixture_cost_measured`: `True`
- `identity_continuity_passed`: `True`
- `shape_economy_passed`: `True`

## Failed Gates

- `feedback_path_present`: `False`
- `movement_restores_pulse_conditions`: `False`
- `polarity_regeneration_measured`: `False`
- `repeated_cycle_persistence_self_renewed`: `False`
- `full_m5_movement_support_available`: `False`
- `m6_gate_passed`: `False`

## Diagnosis

- `failure_is_expected_from_fixture_design`: `True`
- `failure_is_not_due_to_direction_parity`: `True`
- `failure_is_not_due_to_budget_identity_or_shape`: `True`
- `failure_is_due_to_absent_feedback_loop`: `True`
- `pulse_drive_is_external_to_s0_movement_substrate`: `True`
- `boundary_response_is_readout_not_rearm_source`: `True`

## Needed To Reopen M6

- `define_feedback_path`: Define a runtime-visible path by which S0 movement-substrate state changes alter native pulse-producing surplus/route conditions.
- `measure_post_response_pulse_condition_restoration`: Measure that a boundary response restores or raises the next pulse eligibility condition without external rescheduling.
- `measure_polarity_regeneration`: Show that post-response state regenerates the correct forward or reversed polarity rather than consuming imported telemetry.
- `distinguish_self_renewed_windows_from_pulse_schedule`: Count only response windows caused by regenerated pulse conditions, not windows inherited from the original E3 pulse schedule.

## Interpretation

Iteration 10 failed for the right reason: the current fixture has
direction-parity-supported repeated boundary response, but no feedback
from the S0 movement substrate back into native E3 pulse-generating
conditions. Budget, identity, shape/economy, and direction parity were
not the limiting failures. The limiting failure is causal closure of
the drive loop.

