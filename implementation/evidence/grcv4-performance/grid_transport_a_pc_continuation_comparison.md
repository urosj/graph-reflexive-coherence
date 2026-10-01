# Bounded PC numerical continuation

Five strict public A_PC steps on the configurable **4×5, 20-node, 31-edge** grid:

| Measurement | Operation-local reuse only | Bounded continuation |
| --- | ---: | ---: |
| Total step time | 72.232 s | 45.785 s |
| Large inverse computations | 14 | 6 |
| Large conditioning proofs | 14 | 6 |
| Certified solves | 15 | 15 |
| Residual checks | 45 | 45 |
| Fresh conditioning certificates | 15 | 15 |
| Chart-membership checks | 15 | 15 |
| Facts retained after each step | 0 | 4 |

**1.58× faster, 36.6% less step time**, with 57.1% fewer large inverse and conditioning computations. These are single local samples in separate fresh processes with identical light observers. Setup and snapshotting are outside step totals; existing operation-local reuse is enabled in both runs.

Control steps 1–5: 7.749, 17.675, 17.338, 14.577, 14.894 seconds.
Continuation steps 1–5: 7.882, 11.475, 8.572, 9.001, 8.854 seconds.

Every complete initial declaration, backend, C/W/Z state, clock, receipt count and final snapshot digest matches the control and previous primitive-only run exactly. Final snapshot SHA256: `2f80ec318796d7730fbdd49dc57d109442401ad926f36fd1cdf4211e8708734a`.

## Containment

Only **grc_v4_linear.py** and **grc_v4_lifecycle.py** change in production. The store accepts a frozen continuation constrained to four facts for two matrices. One lifecycle adapter selects the reset and latest final Hodge facts already computed by PC. At the next operation entry, those facts seed a fresh private store; primitive lookups still require exact coefficients and conditioning limits.

The selected facts are part of the existing immutable publication. Its existing asset guard and locked single pointer swap publish state and continuation together. Failed operations never replace either. Missing or evicted facts fall back to normal computation. Reset, rebase, set_state, restore, migration and topology/representation publications use the empty continuation default.

PC recipes, candidate A current/writer algorithms, state admission, public result/snapshot formats, asset contexts and operation scopes are unchanged. Both A_PC and C_PC use the same PC adapter; the other realization lifetimes are unchanged. This adds no history cache, public solver mode, second state pointer or new ContextVar.

The retained **entry count** stays constant with trace length. Matrix data still scales with graph size; this is not a constant-byte promise.

## Validation and reproduction

**247 tests passed**, including nine new continuation tests, thirteen primitive tests, all ten realizations' canonical public results/snapshot equivalence, lifecycle, PC, migration and topology/representation suites. Tests cover strict changed limits/coefficients and RHS residuals, asset/numerical failure rollback, restoration and administrative invalidation, separate owners and concurrent steps. New files pass lint and the fact store passes type checks. The lifecycle file retains the same thirteen pre-existing lint diagnostics as HEAD, with none added.

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --disable-continuation --rows 4 --cols 5 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --rows 4 --cols 5 --steps 5
```

The control is benchmark-only and discards selected continuation facts, preserving reuse within each operation.

[Control](grid_transport_a_pc_4x5_5_continuation_disabled.json), [enabled run](grid_transport_a_pc_4x5_5_continuation_enabled.json), [machine-readable comparison and source hashes](grid_transport_a_pc_continuation_comparison.json).
