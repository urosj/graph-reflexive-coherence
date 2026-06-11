# N04 Iteration 17-B Circular Ring Motion Evidence

Status: **passed**

Claim ceiling: `s1_ring_circular_motion_evidence_candidate`

Iteration 17-B tests seam-crossing ring response with a declared circular phase metric.

## Summary

- achieved level: `M6`
- persistence level: `T6_candidate`
- persistence basis: `s1_ring_circular_wrap_route_recovers_0_15`
- recovery status: `recovers_0_15_on_circular_wrap_route`
- forward circular displacement nodes: `1.0`
- reversed circular displacement nodes: `-1.0`
- forward phase error to target: `0.0`
- reversed phase error to target: `0.0`

The ring supports a native seam-crossing circular-response candidate under a declared circular phase metric. This is a circular motion evidence candidate, not a locomotion-like, adaptive-topology, agency, identity-acceptance, or unrestricted movement claim.

## Controls

- `static`: passed=`True`, blocker=`no_committed_packet_contact`
- `wrong_direction`: passed=`True`, blocker=`feedback_wrong_polarity`
- `seam_artifact`: passed=`True`, blocker=`linear_unwrap_seam_intersects_active_route`
- `unwrap_only`: passed=`True`, blocker=`unwrap_robustness_has_no_circular_metric_or_seam_crossing_positive_lane`

## Checks

- `iteration_17a_available`: `True`
- `circular_metric_declared_before_run`: `True`
- `seam_crossing_routes_tested`: `True`
- `circular_distance_sign_reversal_passed`: `True`
- `circular_phase_target_passed`: `True`
- `m4_boundary_response_passed`: `True`
- `m5_direction_control_passed`: `True`
- `m6_circular_motion_candidate_passed`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `feedback_authorized_not_schedule_copied`: `True`
- `controls_fail_for_distinct_blockers`: `True`
- `native_surface_semantics_unchanged`: `True`
- `native_feedback_producer_semantics_unchanged`: `True`
- `no_direct_writes`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_18_allowed`: `True`
- `grid_transfer_ceiling_to_test`: `s1_ring_circular_motion_evidence_candidate`
- `guidance`: `Iteration 18 may test whether the circular/ring result survives route-defined front/rear masks on a grid. Circular claims do not automatically transfer to grid geometry.`

## Claim Boundary

This is circular motion evidence on one ring fixture. It is not locomotion-like, adaptive-topology, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement evidence.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter17b_circular_ring_motion.py
```
