# D1b Circulation Persistence Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1b_circulation_persistence.py
```

Status: `pass`

Classification: `d1b_stable_weak_residual_circulation`

D1b consumes D1 circulation time-series artifacts. It does not rerun or
modify core dynamics.

## Scenario Summary

| Scenario | Mean Signed | Max Abs | Mean Abs Norm | Max Abs Norm | Sign Persist | Lag1 | Decay Late/Early | Corr AbsCirc/Flux |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| d1_ring_u0 | 0 | 0 | 0 | 0 | 0 | 0 | n/a | 0 |
| d1_ring_u1 | 1.0662e-18 | 6.28837e-17 | 1.62449e-17 | 8.94669e-17 | 0 | 0.024397 | n/a | 0.466024 |
| d1_ring_s | -0.0024265 | 0.00707279 | 0.00218722 | 0.00604139 | 1 | 0.998441 | 2.92455 | 0.426777 |
| d1_ring_kick | 0 | 0 | 0 | 0 | 0 | 0 | n/a | 0 |
| d1_ring_profile_sinusoid | 6.50521e-20 | 6.07153e-18 | 1.41035e-17 | 4.49544e-17 | 0 | 0.0671596 | n/a | 0.156043 |
| d1_ring_profile_traveling_phase_seed | 2.12807e-06 | 6.22857e-06 | 2.12643e-05 | 4.85713e-05 | 0.935714 | 0.956152 | 0.251319 | 0.946173 |
| d1_ring_profile_sawtooth | -0.000223362 | 0.00126998 | 0.000234861 | 0.000826531 | 0.992857 | 0.990932 | 0.630387 | 0.000383114 |
| d1_three_pole_u0 | 0 | 0 | 0 | 0 | 0 | 0 | n/a | 0 |
| d1_three_pole_u3 | 0 | 0 | 0 | 0 | 0 | 0 | n/a | 0 |
| d1_three_pole_p | -0.00133262 | 0.00522634 | 0.000956959 | 0.00305865 | 0.55 | 0.999738 | 26.612 | 0.772157 |
| d1_three_pole_p_reversed | 0.00133262 | 0.00522634 | 0.000956959 | 0.00305865 | 0.55 | 0.999738 | 26.612 | 0.772157 |

## Interpretation

Residual circulation remains below the material normalized threshold. Stable weak rows, if present, should be treated as weak residual targets for any future D2 prototype, not as native loop evidence.

## Errors

- none
