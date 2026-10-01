# Primitive-owned inverse and conditioning reuse

The comparison uses the same **4×5, 20-node, 31-edge, five-step strict public** examples before and after centralizing numerical reuse. Each pair's complete declaration is identical. Realization-specific physical settings differ across rows, as documented in the earlier comparison.

| Realization | Earlier solve cache: 5 steps | Primitive cache: 5 steps | Additional speedup | Step time saved |
|---|---:|---:|---:|---:|
| A_CI | 153.38 s | 117.10 s | 1.31× | 23.7% |
| A_PC | 72.24 s | 71.61 s | 1.01× | 0.9% |
| A_CI_PC | 161.75 s | 129.45 s | 1.25× | 20.0% |
| A_RG2b | 224.30 s | 202.09 s | 1.11× | 9.9% |

These are single sequential local samples, with a light lookup counter in the new runs. Totals exclude setup and snapshotting. Setup remains unscoped and is not accelerated by this change.

## Numerical work

Counts include all direct primitive callers, including analytic residual, descriptor and interval blocks. Only exact inverse and conditioning results are reused; right-hand sides, residuals, interval widths and certificates remain fresh. The earlier preparation counts covered only shared solve calls and cannot be compared directly with these broader counts.

| Realization | Inverse requests → computations | Conditioning requests → proofs |
|---|---:|---:|
| A_CI | 1035 → 119 | 105 → 19 |
| A_PC | 315 → 114 | 15 → 14 |
| A_CI_PC | 1311 → 118 | 102 → 18 |
| A_RG2b | 1100 → 119 | 65 → 19 |

## Containment and strictness

Three production files changed: grc_v4_candidate_c.py holds the existing primitive entry points and the single original algorithm for each; grc_v4_linear.py owns immutable inverse/conditioning fact types and one bounded LRU store; grc_v4_codec.py gives that store the existing operation lifetime. No realization call sites were rewritten. The combined preparation object and _c_prepare_matrix controller were removed.

The store has a fixed budget of 64 total facts, covering small direct proof blocks as well as solver matrices. It starts empty in each operation, never stores failures, and does not grow with trace length. Calls outside an operation run the original algorithms uncached.

All five C/W/Z states, physical clocks, receipt counts, declarations/backend and final snapshot byte counts/digests match the previous implementation exactly for every row. Fresh zero/subnormal residual rejection, changed coefficients/limits, non-SPD inverses, retry labels, nested/failed scopes, thread isolation and shared eviction have regression coverage.

A real CI point regression verifies that repeated fresh analytic residual evaluations reuse its exact Hodge inverse. An interval regression verifies that a reused midpoint inverse still produces fresh enclosure widths and rejects an unresolved Neumann bound.

V4 regression run: **954 tests, OK, four optional skips**. The final **13 primitive tests** also pass; that run includes two integration regressions added after full-suite collection. Exact public result bytes and snapshots match cache-disabled execution across all ten realizations.

## Per-step costs

| Realization | Previous steps 1–5 (s) | Primitive steps 1–5 (s) | Constructor previous / current (s) |
|---|---|---|---|
| A_CI | 26.78, 32.24, 30.67, 33.79, 29.90 | 19.37, 25.73, 25.38, 23.31, 23.31 | 42.98 / 42.37 |
| A_PC | 7.72, 18.33, 16.93, 14.24, 15.02 | 7.71, 17.55, 17.15, 14.49, 14.72 | 1.05 / 0.93 |
| A_CI_PC | 28.41, 36.28, 34.69, 35.73, 26.64 | 21.55, 28.47, 27.38, 29.05, 23.00 | 53.69 / 52.36 |
| A_RG2b | 33.84, 48.31, 46.55, 47.30, 48.28 | 30.05, 41.58, 43.35, 44.36, 42.75 | 26.54 / 29.68 |

## Reports

- A_CI: [previous solve cache](grid_transport_a_ci_4x5_5.json), [primitive cache](grid_transport_a_ci_4x5_5_primitive_reuse.json).
- A_PC: [previous solve cache](grid_transport_a_pc_4x5_5.json), [primitive cache](grid_transport_a_pc_4x5_5_primitive_reuse.json).
- A_CI_PC: [previous solve cache](grid_transport_a_ci_pc_4x5_5.json), [primitive cache](grid_transport_a_ci_pc_4x5_5_primitive_reuse.json).
- A_RG2b: [previous solve cache](grid_transport_a_rg2b_4x5_5.json), [primitive cache](grid_transport_a_rg2b_4x5_5_primitive_reuse.json).

[Machine-readable comparison, source hashes and validation](grid_transport_a_primitive_reuse_comparison.json).

Reproduce with scripts/benchmark_grcv4_grid_a.py --reuse --realization CI --rows 4 --cols 5 --steps 5. Omitting --reuse disables primitive fact lookup as a benchmark-only control. Candidate C grid timings were measured subsequently in [their separate comparison](grid_transport_c_realizations_comparison.md).
