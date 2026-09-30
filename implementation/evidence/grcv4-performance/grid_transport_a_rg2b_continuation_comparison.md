# Bounded RG2b numerical continuation

Five strict public A_RG2b steps on the configurable **4×5, 20-node, 31-edge** grid:

| Measurement | Operation-local reuse only | Bounded continuation |
| --- | ---: | ---: |
| Total step time | 202.882 s | 108.400 s |
| Large inverse computations | 19 | 11 |
| Large conditioning proofs | 19 | 11 |
| Certified solves | 65 | 65 |
| Residual checks | 185 | 185 |
| Fresh conditioning certificates | 65 | 65 |
| Whole-chart certificates | 15 | 15 |
| Graph section evaluations | 15 | 15 |
| Native arithmetic bridges | 5 | 5 |
| Facts retained after each step | 0 | 4 |

**1.87× faster, 46.6% less step time**, with 42.1% fewer large inverse and conditioning computations. These are single local samples in separate fresh processes with identical light observers. Setup and snapshotting are outside step totals; existing operation-local reuse is enabled in both runs.

Control steps 1–5: 31.795, 43.621, 44.166, 42.845, 40.455 seconds.
Continuation steps 1–5: 29.103, 19.382, 20.083, 19.718, 20.115 seconds.

Every complete initial declaration, backend, C/W/Z state, clock, receipt count and final snapshot digest matches the control and previous primitive-only run exactly. Final snapshot SHA256: `33a0b518e752c1b30090767046a40a24b1d7ec7c7938d8de632ece57bccc04ff`.

## Containment

RG2b adds one case to the existing lifecycle adapter: select the admitted reset and final native points' Hodge matrices. The prior PC implementation already provides the bounded immutable fact store, seeding, and publication ownership. No RG2b numerical algorithm or graph recipe changes. There is no section-result cache, public solver mode, extra state pointer, or new ContextVar.

The selected facts are part of the existing immutable publication. Its existing asset guard and locked single pointer swap publish state and facts together. Failed operations never replace either. Exact coefficient and conditioning-limit keys still govern reuse; fresh RHS residual checks and conditioning certificates remain mandatory. Reset, rebase, set_state, restore, migration, and topology/representation publications use the empty continuation default.

Both A_RG2b and C_RG2b use the shared adapter. This measured workload is A_RG2b. A/C small-graph continuation tests also cover zero and negative durations. Whole-chart certificates, graph section evaluations, section error enclosures, and native arithmetic bridges remain fresh.

The retained entry count is at most **four facts for two matrices**, independent of trace length. Matrix data still scales with graph size; this is not a constant-byte promise. Missing or evicted facts use the normal computation path. The cheap fixed reference Hodge is deliberately recomputed rather than retaining a third matrix.

## Validation and reproduction

**145 regression tests completed successfully; one optional 32-vertex slow campaign was skipped.** Coverage includes all 17 continuation tests (eight for RG2b), strict primitive algebra, operation evidence, generic lifecycle, and scalar/graph RG2b. Tests cover canonical public result/snapshot equivalence, strict changed limits/coefficients and RHS residuals, frozen beat rejection, fresh section/certificate/bridge counts, asset/numerical rollback, restoration and administrative invalidation, separate owners, and concurrent steps.

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --realization RG2b --disable-continuation --rows 4 --cols 5 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --realization RG2b --rows 4 --cols 5 --steps 5
```

The control is benchmark-only and discards selected continuation facts, preserving reuse within each operation.

[Control](grid_transport_a_rg2b_4x5_5_continuation_disabled.json), [enabled run](grid_transport_a_rg2b_4x5_5_continuation_enabled.json), [machine-readable comparison and source hashes](grid_transport_a_rg2b_continuation_comparison.json).
