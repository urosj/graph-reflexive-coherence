# A_RG2b reuse analysis over five evolving steps

The strict public 4×5 example has **20 nodes and 31 edges**. Five instrumented steps took **198.726 seconds**. All saved C/W states, clocks, receipt counts and the final snapshot hash match the earlier primitive-reuse run exactly. This is an observational run, not an optimization result.

| Large numerical primitive | Computations | Distinct exact matrices | Time |
| --- | ---: | ---: | ---: |
| 31×31 inverse | 19 | 7 | 32.56 s |
| 31×31 conditioning proof | 19 | 7 | 120.75 s |

These disjoint algorithm timers total **153.31 seconds**, or **77.1%** of step time. Conditioning proof is the largest cost. Twelve repetitions per primitive occurred across steps; together they took **87.74 seconds**.

## Same bounded continuation policy

RG2b also computes reset, current and final sections. Its reset section repeats, and its final section becomes the next step's current section. Their Hodge matrices repeat exactly, despite fresh section reconstruction and numerical admission.

Retaining the reset and latest final inverse/conditioning facts would use the existing **four-fact, two-matrix** bound. It would avoid **eight inverse computations and eight conditioning proofs** over this trace, reducing each primitive from **19 to 11**. The other four repetitions belong to the fixed reference matrix: they cost only **0.593 seconds total**, so retaining a third matrix offers little benefit here.

The eight eligible inverse repetitions took **18.31 seconds**; the eight eligible conditioning repetitions took **68.83 seconds**. Subtracting that measured **87.14 seconds** from the run gives a first-order estimate of **111.58 seconds**, or roughly **1.78× faster**. This is a projection, not a measured speedup; implementation overhead and timing variation must be checked with an enabled/disabled comparison.

The contained implementation would extend the existing lifecycle continuation adapter to select RG2b's reset_point and restart_point Hodge matrices. The numerical fact store, exact primitive gateways, RG2b algorithms, graph-section calculation, native arithmetic bridge, domains and publication checks can stay unchanged. All section/enclosure evaluations and fresh RHS/residual work would still run. Restore/reset/migration and other publications would remain cold by default.

## Other repeated work

The graph-section calculation ran **15 times for six exact state queries**. Eight queries repeated from earlier steps and their recomputation consumed **16.63 seconds**. Repeated geometry, certified error enclosures, levels and evaluation counts were identical. All sections used level one with two evaluations. This warrants a separate numerical-result cache only if its keys bind the complete mathematical declaration/backend and query and its immutable value retains the error certificate as well as geometry. Returning an older state-bound section object would be unsafe because it also carries operation-specific inputs.

Point maps ran **35 times for 17 exact state/geometry queries**; 16 repetitions from prior steps took **15.54 seconds** and produced identical interval outputs. This work is largely inside graph-section time and must not be added to it.

All **15 whole-chart certificates** emitted identical bound payloads and exact graph algebra. Certificate construction took **3.57 seconds total**, including fresh native-current admission. A future cache may isolate declaration-only bounds and descriptor operators, while retaining those current checks. Descriptor operators alone took **0.19 seconds**. Repeated small descriptor inversions cost only milliseconds.

The priority is bounded matrix continuation: it has the largest measured opportunity and fits the existing adapter without changing RG2b numerical code. Section-result reuse is a separate, smaller follow-up requiring a distinct fact contract. Neither change is implemented by this analysis.

[Raw per-step timings, numerical call phases, repeated-query equality and source hashes](grid_transport_a_rg2b_reuse_analysis.json).
