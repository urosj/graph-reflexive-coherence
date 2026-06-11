# Branch B1 Diagnostic Sweep Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_b1_diagnostic_sweeps.py
```

Status: `pass`

Branch B1 is diagnostic-only. It uses real `GRC9V3` fixed-topology
continuity execution, but it cannot promote a positive loop claim.

Rows: `26`
Promising diagnostic rows: `0`
Interpretation: `no_role_gated_cascades_detected_fixture_mechanism_mismatch_likely`

## Row Summary

| Row | Axis | Lane | Param | Source | Sink | Raw | Role-Gated | Would Claim | Claim Allowed | Max Correction |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | ---: |
| b1_1_s_epsilon_0p005 | B1.1_amplitude_s_modulation | S | eps=0.005 | True | False | 0 | 0 | False | False | 3.33067e-16 |
| b1_1_s_epsilon_0p01 | B1.1_amplitude_s_modulation | S | eps=0.01 | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_1_s_epsilon_0p02 | B1.1_amplitude_s_modulation | S | eps=0.02 | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_1_s_epsilon_0p04 | B1.1_amplitude_s_modulation | S | eps=0.04 | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_1_k_delta_0p005 | B1.1_amplitude_k_kick | K | kick=0.005 | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_1_k_delta_0p01 | B1.1_amplitude_k_kick | K | kick=0.01 | False | False | 0 | 0 | False | False | 5.55112e-16 |
| b1_1_k_delta_0p02 | B1.1_amplitude_k_kick | K | kick=0.02 | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_1_k_delta_0p04 | B1.1_amplitude_k_kick | K | kick=0.04 | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_2_s_width_1 | B1.2_mask_width | S | N=12,w=1,spacing=half | False | False | 0 | 0 | False | False | 5.55112e-16 |
| b1_2_k_width_1 | B1.2_mask_width | K | N=12,w=1,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_2_s_width_2 | B1.2_mask_width | S | N=12,w=2,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_2_k_width_2 | B1.2_mask_width | K | N=12,w=2,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_2_s_width_3 | B1.2_mask_width | S | N=12,w=3,spacing=half | True | False | 0 | 0 | False | False | 3.33067e-16 |
| b1_2_k_width_3 | B1.2_mask_width | K | N=12,w=3,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_3_s_n_12 | B1.3_ring_size | S | N=12,w=2,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_3_k_n_12 | B1.3_ring_size | K | N=12,w=2,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_3_s_n_24 | B1.3_ring_size | S | N=24,w=2,spacing=half | False | False | 0 | 0 | False | False | 5.55112e-16 |
| b1_3_k_n_24 | B1.3_ring_size | K | N=24,w=2,spacing=half | False | False | 0 | 0 | False | False | 7.77156e-16 |
| b1_3_s_n_48 | B1.3_ring_size | S | N=48,w=2,spacing=half | False | False | 0 | 0 | False | False | 5.55112e-16 |
| b1_3_k_n_48 | B1.3_ring_size | K | N=48,w=2,spacing=half | False | False | 0 | 0 | False | False | 1.22125e-15 |
| b1_4_s_spacing_half | B1.4_spacing | S | N=12,w=2,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_4_k_spacing_half | B1.4_spacing | K | N=12,w=2,spacing=half | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_4_s_spacing_third | B1.4_spacing | S | N=12,w=2,spacing=third | False | False | 0 | 0 | False | False | 4.44089e-16 |
| b1_4_k_spacing_third | B1.4_spacing | K | N=12,w=2,spacing=third | False | False | 0 | 0 | False | False | 5.55112e-16 |
| b1_4_s_spacing_quarter | B1.4_spacing | S | N=12,w=2,spacing=quarter | True | True | 0 | 0 | False | False | 4.44089e-16 |
| b1_4_k_spacing_quarter | B1.4_spacing | K | N=12,w=2,spacing=quarter | False | False | 13 | 0 | False | False | 5.55112e-16 |

## Errors

- none
