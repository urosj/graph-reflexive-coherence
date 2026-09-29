# Bounded CI+PC numerical continuation

Five strict public **A_CI+PC** steps on the configurable **4×5, 20-node, 31-edge** grid:

| Measurement | Operation-local reuse only | Bounded continuation |
| --- | ---: | ---: |
| Total step time | 131.121 s | 78.064 s |
| Large inverse computations | 18 | 10 |
| Large conditioning proofs | 18 | 10 |
| ci contraction certificates | 15 | 15 |
| pc envelope certificates | 15 | 15 |
| chart membership checks | 15 | 15 |
| certified solves | 102 | 102 |
| fresh condition certificates | 102 | 102 |
| residual checks | 248 | 248 |
| ci trial residuals | 29 | 29 |
| pc carrier writes | 5 | 5 |
| Facts retained after each step | 0 | 4 |

**1.68× faster, 40.5% less step time**, with 44.4% fewer large inverse and conditioning computations. These are single local samples from sequential fresh processes with identical observers. Existing operation-local reuse remains enabled in both runs; declaration, owner setup, and final snapshot costs are excluded from step totals.

| Step | Operation-local only (s) | Continuation (s) |
| --- | ---: | ---: |
| 1 | 21.793 | 21.684 |
| 2 | 29.119 | 15.924 |
| 3 | 27.725 | 14.929 |
| 4 | 29.258 | 17.237 |
| 5 | 23.226 | 8.290 |

Every full initial declaration, differential backend, saved C/W/Z state, physical clock, receipt count, and final snapshot digest matches the control and both earlier primitive-only runs exactly. Final snapshot SHA256: `da0885c4415b58073f39607e7344073ddf794f760975f89285e0af706d27012e`.

## Containment and strictness

CI+PC now selects the already admitted reset and final CI roots' actual trial Hodge matrices in the existing lifecycle continuation adapter. This extends the same mechanism used by PC and RG2b; no CI+PC numerical implementation changes. Both A_CI+PC and C_CI+PC use the adapter. This grid measurement is for A; the focused tests also cover C.

The selected immutable inverse and conditioning facts are capped at four entries for two matrices. They are part of the existing guarded atomic publication and seed a fresh private operation store. Exact coefficient and conditioning-limit matches remain mandatory. Failed numerical/domain/asset operations cannot publish new facts. Restoration, assignment, reset, rebase, migration, and topology/representation publications start cold through the existing empty default. Fact count is independent of trace length; matrix data still scales with graph size.

CI roots still start from the reference and run their full iteration, contraction/domain admission, PC envelope checks, and fresh trial residuals. The selected same-root source still feeds one ordinary PC carrier write. This does not substitute a standalone PC read for a CI+PC root, cache a whole root, or bypass a certificate. All observed fresh-check counts match the disabled control exactly.

The earlier 131.471-second repeat did not enable CI+PC continuation. That report is retained as a historical measurement; this paired comparison measures the corrected connection.

## Validation and reproduction

The **25 focused continuation tests** and **130 broader regression tests** all passed, with no skips. Regression modules cover linear algebra, generic lifecycle across all ten realizations, CI, and CI+PC. The eight new CI+PC continuation tests cover canonical warm/cold result and snapshot equality, A/C zero/negative durations, fresh admission/residual/write counts, domain rejection, asset/numerical rollback, administrative invalidation, and separate/concurrent owners. New files pass lint; the lifecycle file has the same 13 pre-existing diagnostics as HEAD.

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_continuation.py --realization CI+PC --disable-continuation --rows 4 --cols 5 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_continuation.py --realization CI+PC --rows 4 --cols 5 --steps 5
```

The control uses a benchmark-only mock to discard selected continuation facts at publication. Production has no mode switch.

[Control](grid_transport_a_ci_pc_4x5_5_continuation_disabled.json), [enabled run](grid_transport_a_ci_pc_4x5_5_continuation_enabled.json), [comparison and measured source hashes](grid_transport_a_ci_pc_continuation_comparison.json).
