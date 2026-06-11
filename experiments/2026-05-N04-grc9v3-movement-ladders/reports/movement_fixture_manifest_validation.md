# Movement Fixture Manifest Validation

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_fixture_manifest.py
```

Status: `passed`

## Top-Level Checks

| Check | Passed |
|---|---:|
| `schema_matches` | `True` |
| `topology_events_disabled` | `True` |
| `adaptive_topology_entry_blocked` | `True` |
| `topology_policy_present` | `True` |
| `topology_policy_blocks_changes` | `True` |
| `required_metrics_present` | `True` |
| `required_formulas_present` | `True` |
| `initializer_defaults_present` | `True` |
| `initializer_defaults_positive` | `True` |
| `default_edge_properties_present` | `True` |
| `default_edge_properties_positive` | `True` |
| `null_envelope_present` | `True` |
| `null_envelope_calibration_status_present` | `True` |
| `fixtures_present` | `True` |
| `active_fixtures_passed` | `True` |
| `lanes_passed` | `True` |

## Fixtures

| Fixture | Status | Passed |
|---|---|---:|
| `S0_chain_v1` | `active` | `True` |
| `S1_ring_v1` | `active` | `True` |
| `S3_grid_v1` | `deferred` | `True` |

## Lanes

| Lane | Passed |
|---|---:|
| `U0` | `True` |
| `B0` | `True` |
| `B1` | `True` |
| `B1_reversed` | `True` |
| `K1` | `True` |
| `K1_reversed` | `True` |

## Notes

- S0 and S1 are active first-tranche fixtures.
- S3 is declared but deferred until S0/S1 observables and classifier are validated.
- Ring centroid movement must use the declared unwrap policy.
- Topology events are disabled for the first movement tranche.

## Edge Defaults

```json
{
  "base_conductance": 1.0,
  "interpretation": "Unit coupling and unit edge delay for first fixed-substrate movement tranche unless an edge overrides these fields.",
  "proper_time_delay": 1.0,
  "temporal_delay": 1.0,
  "weight": 1.0
}
```

## Required Parameters

- Edge weights, conductance, temporal delay, and proper-time delay are validated.
- Ring coordinate mapping declares `theta_i = 2*pi*i/N` and clockwise direction.
- Even-N ring antipodal tie-break is explicitly declared.
- Initializer defaults are validated.
- B1/B1 reversed declare bump amplitude and tilt epsilon.
- K1/K1 reversed declare kick mask node count.
