# Movement Observables Validation

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_movement_observables.py
```

Status: `passed`

## Checks

| Check | Passed |
|---|---:|
| `all_cases_passed` | `True` |
| `synthetic_positive_present` | `True` |
| `synthetic_negatives_present` | `True` |
| `identity_replacement_negative_present` | `True` |
| `topology_changed_negative_present` | `True` |
| `ring_wrap_cases_present` | `True` |
| `reversal_cross_check_passed` | `True` |
| `timeseries_evidence_emitted` | `True` |
| `claim_flags_remain_false` | `True` |

## Cases

| Run | Passed | Budget | Move | Identity | Shape | Topology | dX | Width d | Profile | Boundary Flips |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `S0_chain_v1_null_static` | `True` | `True` | `False` | `True` | `True` | `True` | `0.000000` | `0.000000` | `1.000000` | `0` |
| `S0_chain_v1_uniform_jitter` | `True` | `True` | `False` | `False` | `False` | `True` | `-0.000001` | `0.000000` | `0.000000` | `19` |
| `S0_chain_v1_shape_preserving_shift` | `True` | `True` | `True` | `True` | `True` | `True` | `0.095489` | `0.001286` | `1.000000` | `2` |
| `S0_chain_v1_reversed_shape_preserving_shift` | `True` | `True` | `True` | `True` | `True` | `True` | `-0.095489` | `0.001286` | `1.000000` | `2` |
| `S0_chain_v1_boundary_reassignment_front_gain_rear_loss` | `True` | `True` | `True` | `True` | `True` | `True` | `0.095489` | `0.001286` | `1.000000` | `2` |
| `S0_chain_v1_smeared_shift` | `True` | `True` | `False` | `True` | `False` | `True` | `0.000000` | `0.045459` | `0.000000` | `14` |
| `S0_chain_v1_basin_replacement` | `True` | `True` | `True` | `False` | `True` | `True` | `0.626592` | `0.057138` | `0.911910` | `14` |
| `S0_chain_v1_budget_drift` | `True` | `False` | `False` | `False` | `True` | `True` | `-0.023281` | `0.012966` | `1.000000` | `3` |
| `S0_chain_v1_topology_changed_apparent_displacement` | `True` | `True` | `True` | `True` | `True` | `False` | `0.095489` | `0.001286` | `1.000000` | `2` |
| `S1_ring_v1_null_static` | `True` | `True` | `False` | `True` | `True` | `True` | `0.000000` | `0.000000` | `1.000000` | `0` |
| `S1_ring_v1_uniform_jitter` | `True` | `True` | `False` | `False` | `False` | `True` | `-0.000001` | `0.000000` | `0.000000` | `22` |
| `S1_ring_v1_shape_preserving_shift` | `True` | `True` | `True` | `True` | `True` | `True` | `0.104418` | `0.002143` | `1.000000` | `2` |
| `S1_ring_v1_reversed_shape_preserving_shift` | `True` | `True` | `True` | `True` | `True` | `True` | `-0.104439` | `0.000000` | `1.000000` | `2` |
| `S1_ring_v1_boundary_reassignment_front_gain_rear_loss` | `True` | `True` | `True` | `True` | `True` | `True` | `0.104418` | `0.002143` | `1.000000` | `2` |
| `S1_ring_v1_smeared_shift` | `True` | `True` | `True` | `True` | `False` | `True` | `-0.052219` | `0.048476` | `0.000000` | `17` |
| `S1_ring_v1_basin_replacement` | `True` | `True` | `True` | `False` | `False` | `True` | `-0.199998` | `0.107632` | `-0.209801` | `14` |
| `S1_ring_v1_budget_drift` | `True` | `False` | `True` | `True` | `True` | `True` | `0.107957` | `0.003022` | `0.960032` | `2` |
| `S1_ring_v1_topology_changed_apparent_displacement` | `True` | `True` | `True` | `True` | `True` | `False` | `0.104418` | `0.002143` | `1.000000` | `2` |
| `S1_ring_v1_ring_wrap_forward` | `True` | `True` | `True` | `True` | `True` | `True` | `0.313274` | `0.002139` | `1.000000` | `6` |
| `S1_ring_v1_ring_wrap_reverse` | `True` | `True` | `True` | `True` | `True` | `True` | `-0.313274` | `0.002139` | `1.000000` | `6` |

## Notes

- Synthetic traces validate observables only; they are not movement evidence.
- Centroid drift is emitted as a time series and only supports early displacement evidence.
- Centroid drift is separated from identity, boundary/support, shape, budget, and topology gates.
- Budget drift blocks movement promotion even when displacement is present.
- Identity replacement blocks movement promotion even when a new basin appears elsewhere.
- Identity continuity levels distinguish candidate continuity from gate-passed identity.
- Movement-cost per displacement is null when displacement is effectively zero.
- Shape-preserving forward/reverse synthetic cases are cross-checked for opposite displacement signs.
- Ring wrap cases validate the tracked-basin unwrapped centroid convention.
- All movement claim flags remain false in Iteration 4.
