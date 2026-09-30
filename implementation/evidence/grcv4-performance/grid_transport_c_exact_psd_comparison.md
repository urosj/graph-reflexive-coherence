# Exact conditioning certificate across Candidate C

A C_PC 3×4 public-step profile found that exact symmetric inertia checks inside Euclidean conditioning proofs took 4.28 of 8.73 step seconds. The existing algorithm needs only a positive-semidefinite **yes/no** decision for each proposed singular-value endpoint. General `inertia()` computes all three signed rank counts, including work unnecessary for that certificate. All five Candidate C realizations reach this shared conditioning path; their other numerical work determines how much whole-step time it saves.

The private arithmetic implementation now makes that certificate decision with exact symmetric Schur complements. A positive diagonal supplies a congruence pivot; if none remains, the residual matrix is PSD exactly when every entry is zero. Negative diagonals and nonzero off-diagonals at a zero-diagonal remainder fail. Equality at a bound is admitted. The public inertia function, singular-value proposal, conditioning limit, exact returned bound, failure path, and stage certificate format stay the same. This adds no new cache, caller branch, or realization-specific path.

## Five-step public measurements

Each before/after pair uses the same **3×4 grid, 12 nodes, 17 edges**, automatic operation-local matrix reuse, identical realization-specific declarations, and five evolving strict public steps. Each ran in a fresh process. Timers include the public step but exclude declaration and owner setup, digest capture, and report writing.

| Candidate C realization | Before | Exact PSD check | Speedup | Time saved |
| --- | ---: | ---: | ---: | ---: |
| OS | 81.49 s | 57.82 s | 1.41× | 29.0% |
| CI | 60.42 s | 57.98 s | 1.04× | 4.0% |
| PC | 64.24 s | 46.73 s | 1.37× | 27.2% |
| CI+PC | 61.98 s | 60.00 s | 1.03× | 3.2% |
| RG2b | 217.39 s | 155.53 s | 1.40× | 28.5% |

Relative to the original [reuse-disabled controls](grid_transport_c_realizations_comparison.md), the optimized automatic runs are **1.78× OS, 2.19× CI, 1.74× PC, 2.15× CI+PC, and 1.77× RG2b** faster. Those combined ratios include both matrix fact reuse and the exact PSD certificate change.

For every realization, all five complete public-result digests and all five snapshot digests match byte-for-byte in the before/after pair. Initial declarations, final snapshots, and matrix fact request/hit/miss counts also match. The only runtime change is the exact certificate decision. These are single local timing samples, not confidence intervals. CI and CI+PC show only small timing differences here; those samples alone do not establish a material speedup. The [machine-readable paired report](grid_transport_c_exact_psd_comparison.json) preserves per-step times, both source hashes, exact-equality checks, and links to all five full optimized runs.

## Strictness checks

The focused numerical regression passed 15 tests: deterministic exact PSD-versus-inertia decisions on zero pivots, exact equalities, near-boundary negatives, and 600 symmetric rational matrices; strict C conditioning and singularity rejection; and automatic/fresh public-result equivalence for all ten realizations. The private backend passes Ruff and strict mypy. The complete V4 suite passed **993 tests in 927.516 seconds**, with four existing opt-in tests skipped (three wheel/sdist campaigns and one slow 32-vertex RG2b campaign).

The earlier [Candidate C comparison](grid_transport_c_realizations_comparison.md) and its **226.33 s one-step 4×5 C_OS** observation are pre-change baselines. A separate one-step run on the identical **4×5, 20-node, 31-edge** declaration measured **136.28 s** with the exact PSD check: **1.66× faster**. Declaration admission fell from **140.41 to 82.73 s** and owner setup from **74.64 to 44.05 s**, about **1.7×** for each. The full declaration, complete public result, snapshot, and final digest match exactly. The optimized [4×5 one-step report](grid_transport_c_os_4x5_1_exact_psd.json) and both source hashes are linked by the machine-readable comparison. This is one step, not an extrapolated five-step total.

## Remaining C_PC cost

An instrumented optimized 3×4 C_PC public step took **6.23 s**. Exact inverse calls accounted for **2.33 s across 16 calls** and conditioning proofs for **1.96 s across 11 calls**; the three spectral-selector calls took **0.12 s**. The [scoped profile](grid_transport_c_remaining_cost_3x4_pc_1.json) matched the complete public-result digest from the optimized run. These timings may overlap where one observed call invokes another, so they should not be summed. Repeated exact inversion is the largest measured remaining numerical cost in this step; changing its algorithm or reuse policy needs a separate equivalence check and workload measurement.
