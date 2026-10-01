# A_OS 6×6 five-step comparison with FLINT (2026-09-30)

The [original strict public run](grid_transport_6x6_5.json) was measured before
the matrix optimizations. The [new run](grid_transport_6x6_flint_5.json) uses
runtime commit `1a18791`, including the shared matrix API, bounded reuse, and
the optional FLINT 0.9.0 exact CPU backend. Both execute five evolving A_OS
steps on the same **36-node, 60-edge** closed grid at `dt = 1/64` through the
public `GRCV4` lifecycle.

| Local run | Step 1 | Step 2 | Step 3 | Step 4 | Step 5 | Sum of public steps | Whole process |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original, before matrix optimization | 127.720 s | 203.832 s | 242.801 s | 209.201 s | 244.130 s | 1,027.683 s | 1,033.57 s |
| Earlier shared-solve reuse | 63.148 s | 90.343 s | 111.602 s | 94.624 s | 105.680 s | 465.398 s | 470.88 s |
| Current code with FLINT | 7.961 s | 10.497 s | 12.238 s | 10.612 s | 12.060 s | **53.368 s** | **57.18 s** |

The current run is **19.26× faster by summed step time** than the original
(94.8% less time), and 8.72× faster than the older shared-solve-reuse sample.
Whole-process time improved by 18.08× against the original. These are single
local runs from different revisions, so the comparison measures their combined
change; it does not isolate FLINT's marginal effect on the current code.

Before stepping, the new run compared its complete initial geometry input and
differential reference with the original report. Every new step committed. At
each step, resource values, retained edge histories, physical time, total
resource, and receipt count matched the original record exactly. Final
snapshot SHA-256 and length matched as well:
`76a972facd790a7ee81943a9e9a93de097f30277afb6201aa64fc9790f42992d`
and 87,235 bytes. The new report also records per-step public result and
snapshot digests. The original report did not retain those per-step digests;
its final snapshot digest includes the complete committed history.

The new run used `examples.grcv4.grid_transport.make_inputs(6, 6)` and
`run_inputs(..., 5, 6, 6)` inside
`exact_backend(ExactBackend.FLINT)`, with the same declaration and request
schedule as the original example. Step timers cover public admission, numerical
stages, and strict validation, while result/snapshot hashing is outside those
timers. The whole-process timing from `/usr/bin/time` also includes imports,
setup, report writing, and interpreter startup. The complete new declaration,
per-step states and timings, digests, parity checks, and runtime commit are in
the [new machine-readable report](grid_transport_6x6_flint_5.json).
