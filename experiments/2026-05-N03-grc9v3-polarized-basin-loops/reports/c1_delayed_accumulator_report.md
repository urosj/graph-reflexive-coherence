# Branch C1 Delayed Accumulator Channel Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c1_delayed_accumulator.py
```

Status: `pass`

C1 uses a redesigned experiment-local execution surface. It computes
GRC9V3 flux proposals, then moves coherence through delayed forward and
return accumulator queues. Budget is audited as nodes plus in-flight
storage.

Rows: `15`
Candidate rows: `0`
Classification: `c1_no_candidate_loop_rows_observed`

## Row Summary

| Row | Lane | Delay | Source | Sink | Raw | Role-Gated | C1 Candidate | Max In-Flight | Max Budget Error |
| --- | --- | ---: | --- | --- | ---: | ---: | --- | ---: | ---: |
| c1_u0_delay_3 | U0 | 3 | False | False | 0 | 0 | False | 0 | 0 |
| c1_u2_delay_3 | U2 | 3 | False | False | 0 | 0 | False | 0 | 0 |
| c1_s_delay_3 | S | 3 | True | True | 0 | 0 | False | 0.00269384 | 2.22045e-16 |
| c1_k_delay_3 | K | 3 | True | True | 0 | 0 | False | 9.74993e-05 | 1.11022e-16 |
| c1_k_reversed_delay_3 | K_reversed | 3 | True | True | 0 | 0 | False | 9.74993e-05 | 1.11022e-16 |
| c1_u0_delay_6 | U0 | 6 | False | False | 0 | 0 | False | 0 | 0 |
| c1_u2_delay_6 | U2 | 6 | False | False | 0 | 0 | False | 0 | 0 |
| c1_s_delay_6 | S | 6 | True | True | 0 | 0 | False | 0.0053734 | 2.22045e-16 |
| c1_k_delay_6 | K | 6 | True | True | 0 | 0 | False | 0.00019474 | 1.11022e-16 |
| c1_k_reversed_delay_6 | K_reversed | 6 | True | True | 0 | 0 | False | 0.00019474 | 1.11022e-16 |
| c1_u0_delay_10 | U0 | 10 | False | False | 0 | 0 | False | 0 | 0 |
| c1_u2_delay_10 | U2 | 10 | False | False | 0 | 0 | False | 0 | 0 |
| c1_s_delay_10 | S | 10 | True | True | 0 | 0 | False | 0.00892262 | 2.22045e-16 |
| c1_k_delay_10 | K | 10 | True | True | 0 | 0 | False | 0.00032399 | 1.11022e-16 |
| c1_k_reversed_delay_10 | K_reversed | 10 | True | True | 0 | 0 | False | 0.00032399 | 1.11022e-16 |

## Reversal

```json
{
  "pairs": [
    {
      "delay_steps": 3,
      "k_candidate": false,
      "k_reversed_candidate": false,
      "k_reversed_role_gate": true,
      "k_reversed_role_gated_cycles": 0,
      "k_role_gate": true,
      "k_role_gated_cycles": 0
    },
    {
      "delay_steps": 6,
      "k_candidate": false,
      "k_reversed_candidate": false,
      "k_reversed_role_gate": true,
      "k_reversed_role_gated_cycles": 0,
      "k_role_gate": true,
      "k_role_gated_cycles": 0
    },
    {
      "delay_steps": 10,
      "k_candidate": false,
      "k_reversed_candidate": false,
      "k_reversed_role_gate": true,
      "k_reversed_role_gated_cycles": 0,
      "k_role_gate": true,
      "k_role_gated_cycles": 0
    }
  ]
}
```

## Errors

- none
