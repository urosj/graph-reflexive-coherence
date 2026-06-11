# N04 Iterations 1-3 Lock Summary

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_iteration_1_3_lock_summary.py
```

Status: `passed`

## Lock Flags

| Flag | Passed |
|---|---:|
| `handoff_frozen` | `True` |
| `fixtures_frozen` | `True` |
| `lanes_frozen` | `True` |
| `metric_defaults_frozen` | `True` |
| `topology_policy_frozen` | `True` |
| `initializer_formulas_frozen` | `True` |
| `projection_policy_frozen` | `True` |
| `coordinate_policy_frozen` | `True` |
| `claim_flags_frozen` | `True` |
| `src_unchanged` | `True` |
| `topology_disabled` | `True` |

## Frozen Surfaces

- Active fixtures: `['S0_chain_v1', 'S1_ring_v1']`
- Deferred fixtures: `['S3_grid_v1']`
- Lanes: `['B0', 'B1', 'B1_reversed', 'K1', 'K1_reversed', 'U0']`
- Projection policy: `conserved_nonnegative_simplex`
- Null displacement calibrated: `False`
- Strong movement claims remain blocked until null calibration and movement gates pass.

## Source Status

```text
(no src/* status entries)
```
