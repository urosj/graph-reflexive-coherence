# N04 Iteration 17-A Ring Unwrap Robustness

Status: **passed**

Claim ceiling: `s1_ring_unwrap_robust_transfer_candidate`

Iteration 17-A tests whether the S1 ring result is robust across declared unwrap origins.

## Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- persistence basis: `s1_ring_multiple_unwraps_recover_0_15`
- recovery status: `recovers_0_15_across_equivalent_unwraps`
- accepted unwrap origins: `[0, 1, 2, 3, 4, 5, 6, 15, 16, 17, 18, 19, 20]`
- seam-control origins: `[7, 8, 9, 10, 11, 12, 13, 14]`
- forward signed centroid range: `0.15000000000000036` to `0.15000000000000036`
- reversed signed centroid range: `0.14999999999999858` to `0.15000000000000036`

The Iteration 17 ring M6 candidate is robust across all declared unwrap origins whose seam does not intersect the active route. Seam-intersecting unwraps are recorded as controls and do not promote circular or wrap-crossing claims.

## Checks

- `iteration_17_available`: `True`
- `multiple_unwrap_origins_declared`: `True`
- `accepted_unwraps_keep_route_off_seam`: `True`
- `seam_intersecting_controls_recorded`: `True`
- `candidate_gates_recomputed_per_origin`: `True`
- `all_accepted_origins_reach_m6`: `True`
- `direction_parity_passed_all_accepted_origins`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `feedback_authorized_not_schedule_copied`: `True`
- `signed_centroid_magnitude_stable`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_17b_allowed`: `True`
- `circular_motion_ceiling_to_test`: `s1_ring_unwrap_robust_transfer_candidate`
- `guidance`: `17-B may test circular metrics and seam-crossing routes; it must not inherit circular claims from unwrap robustness alone.`

## Claim Boundary

This is unwrap-robust ring-transfer evidence, not circular locomotion or wrap-crossing movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter17a_ring_unwrap_robustness.py
```
