# Packet-Loop Geometry Coupling Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_packet_loop_geometry_coupling.py
```

Status: `passed`

## Summary

- Runtime family: `LGRC9V3`
- Execution surface: `surface_c_lgrc9v3_e3_pulse_geometry_audit`
- Claim ceiling: `packet_loop_geometry_coupling_audit`
- Boundary coupling enabled: `False`
- Source fixture changes detected: `True`
- Proper-time phase separation observed: `True`
- N04 fixture mapping defined: `False`
- Movement claim allowed: `False`

## Checks

| Check | Passed |
|---|---:|
| `e3_import_passed` | `True` |
| `source_fixture_pole_mass_oscillation_measured` | `True` |
| `budget_split_available_from_animation_telemetry` | `True` |
| `node_plus_packet_budget_conserved` | `True` |
| `edge_delay_audit_available` | `True` |
| `conductance_audit_available` | `True` |
| `boundary_coupling_disabled` | `True` |
| `pulse_activity_alone_does_not_claim_movement` | `True` |
| `no_direct_boundary_displacement_scripted` | `True` |
| `n04_fixture_mapping_not_yet_defined` | `True` |
| `movement_classifier_boundary_unchanged` | `True` |

## Pole Mass Oscillation

| Pole | Initial | Final | Min | Max | Amplitude | Proper-Time Span |
|---|---:|---:|---:|---:|---:|---:|
| `K1` | `1.000000` | `0.750000` | `0.750000` | `1.000000` | `0.250000` | `12.000000` |
| `K2` | `1.000000` | `1.000000` | `1.000000` | `1.100000` | `0.100000` | `10.000000` |
| `S1` | `2.000000` | `2.250000` | `2.000000` | `2.250000` | `0.250000` | `13.000000` |
| `S2` | `1.000000` | `1.000000` | `1.000000` | `1.100000` | `0.100000` | `11.000000` |

## Budget Split

- Node budget range: `4.75` to `5.0`
- In-flight packet budget range: `0.0` to `0.25`
- Total budget range: `5.0` to `5.0`
- Max checkpoint budget error: `0.0`
- Max event budget error: `0.0`

## Edge And Route Locality

- Edge delay uniform: `True`
- Edge delay asymmetry observed: `False`
- Conductance change observed: `False`
- Coupling change observed: `False`
- Near-route/off-route comparison available: `False`
- Near-route/off-route reason: `all_four_nodes_are_route_nodes`

## Iteration 8 Entry

- Route-to-substrate mapping required: `True`
- Mapping status: `not_defined`
- Boundary-coupled pulse fixture ready: `False`

## Coupling Interpretation

E3 telemetry shows packet-driven pole coherence/proper-time changes on the four-node source fixture, but N04 movement geometry coupling remains unopened because the E3 route is not mapped onto S0/S1 and boundary coupling is disabled.

## Notes

- Iteration 7-B audits geometry-coupling surfaces only.
- Boundary coupling remains disabled.
- No boundary, support-mask, centroid, or displacement state is directly scripted.
- E3 source telemetry contains exact node/in-flight packet budget split.
- Near-route versus off-route comparison is unavailable on the four-node E3 fixture because every node is on the route.
- N04 fixture mapping is still required before Iteration 8 can test boundary-coupled movement.
