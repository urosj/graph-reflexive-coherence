# Exact CPU backend evaluation (2026-09-30)

This note separates the exploratory CPU measurements from the [integrated exact CPU backend](../../corrections/GRCV4-ExactCPUBackend.md) and its validation. V4 still defaults to `fractions.Fraction`; the integrated FLINT backend is optional and explicitly selected. The earlier experiment installed python-flint 0.9.0 only under `/tmp`, replaced exact scalar construction in an isolated process, and compared native `fmpq` values with an immutable wrapper around `fmpq`. Strict public publication remained enabled. The prototype measurements below predate all production changes.

FLINT's [rational matrix API](https://flintlib.org/doc/fmpq_mat.html) is exact; the [Python binding](https://python-flint.readthedocs.io/en/latest/fmpq_mat.html) exposes rational matrix multiplication, inverse, and solve. The conditioning SVD was still used only to propose endpoints; the same exact Schur PSD certificate decided their admissibility. The prototype changed the scalar implementation of that decision to `fmpq` without relaxing the algorithm.

The exact digest values and per-run timings are in [exact_cpu_backend_evaluation.json](exact_cpu_backend_evaluation.json).

## Public-run observations

Both FLINT prototypes matched each C realization's first public result and snapshot SHA-256 digest against the saved strict 3×4 report. C_PC and C_OS also matched every public result and snapshot over five steps. Both prototypes matched each A realization's first public result and snapshot digest against a fresh Python-backend 4×5 run. A_CI, A_PC, A_CI+PC, and A_RG2b also matched declaration digests. A_OS has no declaration digest in that example runner.

| Strict public workload | Python | Raw `fmpq` | Wrapped `fmpq` | Wrapper speedup |
| --- | ---: | ---: | ---: | ---: |
| C_PC 3×4, five steps | 47.14 s | 12.81 s | 13.42 s | 3.51× |
| C_OS 3×4, five steps | 61.39 s | 12.61 s | 14.81 s | 4.14× |
| A_OS 4×5, first step | 4.76 s | 1.43 s | 1.67 s | 2.85× |
| A_CI 4×5, first step | 14.62 s | 5.88 s | 6.86 s | 2.13× |
| A_PC 4×5, first step | 6.48 s | 2.34 s | 2.50 s | 2.59× |
| A_CI+PC 4×5, first step | 17.59 s | 6.79 s | 8.65 s | 2.03× |
| A_RG2b 4×5, first step | 21.76 s | 7.64 s | 10.05 s | 2.16× |

Times are wall-clock observations, not a statistical benchmark. A_PC runs overlapped briefly, and the C_OS Python control overlapped a short isolated multiplication probe; interpret their ratios as provisional. Parity refers to the complete public result and snapshot bytes hashed by the current example runner, not just final physical values. The one-step C_CI, C_CI+PC, and C_RG2b runs also matched saved public digests, but were not paired with fresh timing controls.

On 16 inversions captured from a strict C_PC step, native FLINT arithmetic including conversion back to `Fraction` took 0.263 s versus 2.401 s for Python elimination. On 11 captured 17×17 Gram products, native FLINT including input and output conversion took 0.022 s versus 0.210 s. Those measurements explain why the homogeneous prototype improves further: it does not convert at each matrix call.

## Prototype findings and integrated design

The prototype showed that converting between `Fraction` and `fmpq` at every matrix call discards much of the benefit. It also exposed conversion boundaries: FLINT does not directly accept Python floats, decimal strings, or `Fraction`; its `fmpq` values do not expose `as_integer_ratio()` and do not mix arithmetically with `Fraction`. CI had a `Fraction` type check, PC's Decimal calculation needed plain integer numerator and denominator values, and geometry's positivity check needed integer ratios. The wrapper matched the tested public digests but imposed workload-dependent cost: on the first C_RG2b step it increased observed FLINT time from 10.45 s to 15.48 s.

The integrated implementation uses native exact scalars with one backend selected for the owner. It does not use the prototype wrapper or the prototype's constructor/type-check façade. `grc_v4_exact.py` centralizes backend selection, exact construction, integer-ratio extraction, and the exact-value predicate. The owner captures the choice at construction and re-enters it for its numerical entry points; the default remains Python `Fraction`. The optional `v4-flint` dependency is imported only when explicitly selected. Native `fmpq_mat` multiplication and inverse, plus the same exact Schur PSD decision, are isolated in `_grc_v4_matrix_flint.py` behind the shared matrix API. The scientific declarations, public schemas, receipts, snapshots, and solver policies remain unchanged.

Private matrix-continuation facts carry a backend tag; seeding facts from a different backend is rejected. A duplicated owner retains its backend. Restoration from serialized state uses the backend active during restoration because the serialized scientific state contains no implementation choice. Exact input conversion happens when constructing numerical values, and binary64/JSON conversion stays at the existing public boundaries. This preserves the legacy path while keeping each operation on one native scalar representation. `ExactScalar` remains the type annotation and `exact_number(...)` the construction boundary. A source-level test now rejects direct `Fraction` references in V4 numerical modules outside `grc_v4_exact.py`; that catches a new default-only path even when FLINT is unavailable in the test environment.

## Integrated measurements and validation

The [integrated timing record](exact_cpu_backend_integrated.json) contains a paired strict public C_PC 3×4 five-step run: 48.08 s with Python `Fraction` and 11.49 s with FLINT, or 4.18× in that single local sample. FLINT C_OS took 12.10 s for five steps. These timings are for the integrated implementation; the table above remains historical prototype evidence. They do not establish a general speedup for every grid size or realization.

With the integrated implementation, all ten realizations matched strict first-step public result and snapshot digests; C_PC and C_OS also matched both digests at every step through five steps. Focused tests passed with the optional FLINT installation and covered native values, exact singular and conditioning failures, cross-backend continuation rejection, owner binding after scope exit, strict public result parity, duplication, state assignment, and reset. The default environment runs without FLINT. A broad legacy V4 run exercised 998 tests; eight initial errors were traced to an evidence-scope decorator regression and capture tests seeing untracked files. The decorator was corrected, the new source files were staged for capture reconstruction, and the affected tests passed on targeted reruns. The full broad suite was not rerun after those corrections.

Further validation should cover longer strict traces and failure-receipt parity across all realizations. The performance figures here are single-run measurements, not a scaling claim or a statistical benchmark.

The later [A_OS 6×6 five-step comparison](grid_transport_6x6_flint_comparison.md)
reproduces the original larger-grid declaration with all current optimizations
and FLINT. Its 53.37 s step sum is 19.26× faster than the 1,027.68 s
pre-matrix-optimization record; the final strict snapshot digest matches. That
cross-revision comparison does not isolate FLINT's contribution.
