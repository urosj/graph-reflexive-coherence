# Iteration 11-B M2 Runtime Shape-Blocked Fixture

Status: `passed`

This fixture provides a runtime timeseries for the M2 rung. It is not a
movement claim and it is not native LGRC telemetry. The lane intentionally
passes displacement, identity, budget, topology, and directed boundary
reassignment, then fails the profile similarity gate so M3 remains blocked.

## Classification

- movement_level: `M2_identity_preserving_displacement`
- diagnostic_subtype: `M2_boundary_reassignment_shape_blocked`
- primary_blocked_reason: `shape_gate_failed`
- movement_claim_allowed: `False`

## Metrics

- centroid displacement: `0.17167957557684588`
- effective displacement threshold: `0.05`
- front entered mass: `3.3150981035444347`
- rear left mass: `1.034370396895702`
- identity mass ratio min: `1.0`
- width relative change max: `0.008893340751886612`
- profile similarity aligned: `0.7614634487196019`

## Checks

- `budget_gate_passed`: `True`
- `displacement_gate_passed`: `True`
- `identity_gate_passed`: `True`
- `boundary_reassignment_gate_passed`: `True`
- `shape_gate_failed`: `True`
- `profile_gate_is_shape_blocker`: `True`
- `classified_as_m2`: `True`
- `primary_blocker_shape`: `True`
- `movement_claims_blocked`: `True`
- `timeseries_emitted`: `True`

## Artifacts

- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m2_runtime_shape_blocked_timeseries/M2_shape_degraded_boundary_handoff.jsonl`
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m2_runtime_shape_blocked_fixture.json`

