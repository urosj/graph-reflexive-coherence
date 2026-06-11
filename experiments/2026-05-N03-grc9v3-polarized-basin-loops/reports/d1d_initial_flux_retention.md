# D1d Initial Circulating-Flux Retention Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1d_initial_flux_retention.py
```

Status: `pass`

Classification: `d1d_initial_flux_erased_by_transport_rebuild`

D1d initializes a closed ring with nonzero clockwise/counter-clockwise
`flux_uv` on every edge, then runs the native fixed-topology GRC9V3
transport rebuild. It tests whether initialized flux behaves like
persistent corridor flow.

## Scenario Summary

| Scenario | Init Flux | Init Circ | First Rebuild Circ | Final Circ | First Signed Retention | Final Signed Retention | First Abs-Flux Retention | Max Norm After Rebuild |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| d1d_uniform_clockwise_flux_0p01 | 0.01 | 0.12 | 0 | 0 | 0 | 0 | 0 | 0 |
| d1d_uniform_clockwise_flux_0p05 | 0.05 | 0.6 | 0 | 0 | 0 | 0 | 0 | 0 |
| d1d_uniform_clockwise_flux_0p1 | 0.1 | 1.2 | 0 | 0 | 0 | 0 | 0 | 0 |
| d1d_single_bump_clockwise_flux_0p05 | 0.05 | 0.6 | 8.67362e-18 | -1.04083e-16 | 1.4456e-17 | 1.73472e-16 | 0.400787 | 1.30991e-16 |
| d1d_source_sink_clockwise_flux_0p05 | 0.05 | 0.6 | 0 | 0 | 0 | 0 | 0.0993362 | 0 |
| d1d_traveling_phase_seed_clockwise_flux_0p05 | 0.05 | 0.6 | 6.95443e-07 | -1.09057e-05 | 1.15907e-06 | 1.81762e-05 | 0.293387 | 9.58263e-05 |
| d1d_source_sink_counterclockwise_flux_0p05 | 0.05 | -0.6 | 0 | 0 | 0 | 0 | 0.0993362 | 0 |

## Interpretation

D1d tests initialized flux as a native GRC9V3 state surface. If transport rebuild erases the initialized signed circulation, then `flux_uv` is behaving as a recomputed proposal rather than a persistent corridor-flow or momentum state. Any blood/vein-like closed-flow model would need explicit edge/corridor coherence, packet, accumulator, or momentum state outside plain native GRC9V3 fixed-topology continuity.

## Errors

- none
