# Movement Initializer Validation

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_initializers.py
```

Status: `passed`

## Top-Level Checks

| Check | Passed |
|---|---:|
| `all_lanes_passed` | `True` |
| `reversed_controls_deterministic` | `True` |
| `formulas_serialized` | `True` |
| `projection_declared` | `True` |

## Lane Summary

| Fixture/Lane | Passed | Budget Error | Min C | Max C | Centroid |
|---|---:|---:|---:|---:|---:|
| `S0_chain_v1:U0` | `True` | `0.000e+00` | `1.000000` | `1.000000` | `10.000000` |
| `S0_chain_v1:B0` | `True` | `0.000e+00` | `0.904511` | `1.304509` | `10.000000` |
| `S0_chain_v1:B1` | `True` | `0.000e+00` | `0.892713` | `1.304509` | `10.064051` |
| `S0_chain_v1:B1_reversed` | `True` | `0.000e+00` | `0.892713` | `1.304509` | `9.935949` |
| `S0_chain_v1:K1` | `True` | `0.000e+00` | `0.904511` | `1.304509` | `10.001905` |
| `S0_chain_v1:K1_reversed` | `True` | `0.000e+00` | `0.904511` | `1.304509` | `9.998095` |
| `S1_ring_v1:U0` | `True` | `0.000e+00` | `1.000000` | `1.000000` | `-0.500000` |
| `S1_ring_v1:B0` | `True` | `0.000e+00` | `0.895561` | `1.295557` | `-0.447781` |
| `S1_ring_v1:B1` | `True` | `0.000e+00` | `0.884575` | `1.295585` | `-0.359021` |
| `S1_ring_v1:B1_reversed` | `True` | `0.000e+00` | `0.884519` | `1.295529` | `-0.536540` |
| `S1_ring_v1:K1` | `True` | `0.000e+00` | `0.895561` | `1.295557` | `-0.446114` |
| `S1_ring_v1:K1_reversed` | `True` | `0.000e+00` | `0.895561` | `1.295557` | `-0.449447` |

## Projection Diagnostics

| Fixture/Lane | Raw Sum | Projection Delta Norm |
|---|---:|---:|
| `S0_chain_v1:U0` | `21.000000` | `0.000000` |
| `S0_chain_v1:B0` | `23.005302` | `0.437593` |
| `S0_chain_v1:B1` | `23.005302` | `0.437593` |
| `S0_chain_v1:B1_reversed` | `23.005302` | `0.437593` |
| `S0_chain_v1:K1` | `23.005302` | `0.437593` |
| `S0_chain_v1:K1_reversed` | `23.005302` | `0.437593` |
| `S1_ring_v1:U0` | `24.000000` | `0.000000` |
| `S1_ring_v1:B0` | `26.506623` | `0.511662` |
| `S1_ring_v1:B1` | `26.505951` | `0.511525` |
| `S1_ring_v1:B1_reversed` | `26.507295` | `0.511800` |
| `S1_ring_v1:K1` | `26.506623` | `0.511662` |
| `S1_ring_v1:K1_reversed` | `26.506623` | `0.511662` |

## Reversal Checks

| Fixture | Checks |
|---|---|
| `S0_chain_v1` | `{'b1_centroid_offsets_opposite': True, 'k1_centroid_offsets_opposite': True, 'b1_equal_budget': True, 'k1_equal_budget': True, 'baseline_centroid': 10.0}` |
| `S1_ring_v1` | `{'b1_centroid_offsets_opposite': True, 'k1_centroid_offsets_opposite': True, 'b1_equal_budget': True, 'k1_equal_budget': True, 'baseline_centroid': -0.4477806715150818}` |

## Notes

- Projection uses conserved nonnegative simplex projection.
- Projection delta norm is reported per lane.
- Ring signed distances use shortest unwrapped distance around the tracked basin representative.
- For even-N rings, the antipodal node uses negative signed distance; uniform S1_ring_v1 therefore has centroid -0.5 by convention.
- B1/B1_reversed centroid offsets must have opposite signs.
- K1/K1_reversed centroid offsets must have opposite signs.
