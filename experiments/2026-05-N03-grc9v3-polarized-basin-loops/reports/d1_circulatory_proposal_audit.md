# D1 Circulatory Proposal Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1_circulatory_proposal_audit.py
```

Status: `pass`

D1 audits the existing GRC9V3 proposal surface. It does not add
circulatory terms, phase controllers, or topology changes.

Classification: `d1_weak_residual_loop_circulation_observed`
Max abs loop circulation: `0.0070727893817062425`
Max abs normalized circulation: `0.006041388204739038`

## Scenario Summary

| Scenario | Max Abs Circ | Max Norm Circ | Initial Circ | Final Circ | Initial Mean Abs Flux | Final Mean Abs Flux |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| d1_ring_u0 | 0 | 0 | 0 | 0 | 0 | 0 |
| d1_ring_u1 | 6.28837e-17 | 8.94669e-17 | -3.46945e-18 | 2.42861e-17 | 0.0358208 | 0.094793 |
| d1_ring_s | 0.00707279 | 0.00604139 | -1.85088e-05 | -0.000584429 | 0.0437189 | 0.138489 |
| d1_ring_kick | 0 | 0 | 0 | 0 | 0.00662334 | 0.137497 |
| d1_ring_profile_sinusoid | 6.07153e-18 | 4.49544e-17 | 0 | 4.33681e-19 | 0.0134434 | 0.00736182 |
| d1_ring_profile_traveling_phase_seed | 6.22857e-06 | 4.85713e-05 | 2.88371e-07 | -8.95756e-07 | 0.0107441 | 0.00549655 |
| d1_ring_profile_sawtooth | 0.00126998 | 0.000826531 | -5.46004e-07 | -3.38726e-06 | 0.00503965 | 0.191421 |
| d1_three_pole_u0 | 0 | 0 | 0 | 0 | 0 | 0 |
| d1_three_pole_u3 | 0 | 0 | 0 | 0 | 0.000694312 | 0.000460779 |
| d1_three_pole_p | 0.00522634 | 0.00305865 | 1.96047e-06 | -0.00510547 | 0.00496025 | 0.142295 |
| d1_three_pole_p_reversed | 0.00522634 | 0.00305865 | -1.96047e-06 | 0.00510547 | 0.00496025 | 0.142295 |

## Errors

- none
