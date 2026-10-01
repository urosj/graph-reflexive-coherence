# A_PC reuse analysis over five evolving public steps

The configurable 4×5 example has 20 nodes and 31 edges. Five strict public steps took **67.84 seconds** under light stage instrumentation. Every saved state, clock, receipt count and final snapshot hash matches the previous primitive-reuse run. This new timing sample is not an optimization result.

PC separately reads the reset state, current state and written final state: three current reads per positive step. Within a step, the three large Hodge matrices generally differ. Their overlap becomes apparent across steps: the final state's matrix becomes the next step's current matrix, while the reset matrix repeats.

| Work over five steps | Observed computation | Reuse opportunity |
| --- | ---: | --- |
| Exact 31×31 inverses | 14 computations; 18.18 s | Only six exact coefficient matrices occurred |
| 31×31 conditioning proofs | 14 computations; 37.26 s | The same six matrices, with identical limits |
| Whole-chart envelopes | 15 constructions; 0.72 s | All fifteen emitted the same bound payload |
| Descriptor reconstruction | 20 calls; 0.058 s | Fixed geometric coefficients; fresh resource RHS |
| Exact 2×2 inverses | 100 computations; 0.0035 s | Twenty matrices recur in every step |
| Scalar ZOH writer | 5 calls; 0.28 s | Constant dt/tau enclosure; fresh source and outputs |

Timings are inclusive: descriptor inverse/norm work is inside envelope timing, and descriptor reconstruction is inside current/writer work. The inverse and conditioning algorithm totals are disjoint and together account for **81.7%** of measured step time. They exclude fresh RHS multiplication and residual validation.

The existing operation cache already removes 200 of 300 small inverse requests, but saves only one of fifteen large inverse/conditioning requests. Its lifetime ends before the previous final matrix can be reused by the next step.

The substantial candidate is a bounded numerical continuation owned by the simulator: retain only inverse/conditioning facts for the reset and latest committed final matrices. Start each operation with those immutable facts and admit reuse only on exact coefficients and conditioning limit. Keep operation/asset contexts separate; do not retain intermediate matrices or the entire trace. Each changed state still gets current admission, a fresh RHS, residual checks, certificates, interval checks where applicable, and publication verification. Rebase, migration, reset, restore and failed operations need explicit ownership/lifetime coverage before such a change is implemented. Restored owners may start cold.

For this trace that could reduce each large primitive from **14 computations to 6**, or eight avoided computations. Repeated matrices have unequal costs, so this count does not establish a runtime speedup. Reset work is also repeated, but eliminating whole reset admissions is a separate and stronger change than retaining pure numerical facts.

Caching declaration-only envelope bounds while checking every state's chart membership is also valid in principle, but saves less than one second in this workload. Descriptor preparation and a shared scalar ZOH enclosure are smaller opportunities. None is implemented by this analysis.

[Raw stage counts, per-step timings, coefficient overlap, source hashes and validation](grid_transport_a_pc_reuse_analysis.json).
