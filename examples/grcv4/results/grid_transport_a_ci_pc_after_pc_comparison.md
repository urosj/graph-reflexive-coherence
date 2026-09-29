# A_CI+PC measurement after the PC continuation update

Five strict public steps on the configurable **4×5, 20-node, 31-edge** grid, with the same scientific declaration and operation-local matrix reuse as the previous run:

| Step | Earlier run (s) | Current run (s) |
| --- | ---: | ---: |
| 1 | 21.547 | 21.808 |
| 2 | 28.472 | 29.190 |
| 3 | 27.376 | 28.165 |
| 4 | 29.054 | 29.043 |
| 5 | 23.003 | 23.264 |
| **Total** | **129.453** | **131.471** |

Current mean step time: **26.294 s**. Owner setup: 53.651 s; declaration admission: 1.249 s; final snapshot: 0.173 s. Complete example wall time: **186.558 s**. These costs are outside the step total.

## What the PC update changed at the time of this repeat

At the time of this measurement, bounded continuation selected only PC and RG2b. CI+PC uses the CI root solver for reset, current, and final readmission, and calls the shared PC scalar carrier write afterward. That carrier write is unchanged. This repeat therefore had operation-local numerical reuse and did not retain matrix facts across steps. A subsequent change connects CI+PC to the same bounded continuation; its paired benchmark is documented separately.

Every operation's inverse and conditioning request/hit/miss counts match the earlier run exactly. Across the five steps:

| Primitive lookup | Requests | Hits | Misses / computations |
| --- | ---: | ---: | ---: |
| Inverse | 1311 | 1193 | 118 |
| Conditioning | 102 | 84 | 18 |

Inverse counts include small descriptor and CI interval blocks. They should not be interpreted as large Hodge inverse counts alone.

The observed earlier/current timing ratio is 0.985×. This is one fresh sample compared with an earlier local sample. Since numerical work counts are identical and CI+PC does not enter the continuation adapter, this difference is not evidence of a speedup from the PC update.

Every complete initial declaration, differential backend, saved C/W/Z state, clock, receipt count, and final snapshot digest matches exactly. Final snapshot SHA256: `da0885c4415b58073f39607e7344073ddf794f760975f89285e0af706d27012e`.

No production code or solver policy changed for this measurement. The machine-readable reports include source hashes for the current uncommitted checkout.

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_a.py --realization CI+PC --rows 4 --cols 5 --steps 5 --reuse --output examples/grcv4/results/grid_transport_a_ci_pc_4x5_5_after_pc_update.json
```

[Earlier run](grid_transport_a_ci_pc_4x5_5_primitive_reuse.json), [current run](grid_transport_a_ci_pc_4x5_5_after_pc_update.json), [comparison and source hashes](grid_transport_a_ci_pc_after_pc_comparison.json).
