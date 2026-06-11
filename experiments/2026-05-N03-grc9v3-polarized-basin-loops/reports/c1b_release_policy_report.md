# C1-B Release Policy Diagnostic Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c1b_release_policy_diagnostics.py
```

Status: `pass`

C1-B is a diagnostic release-policy sensitivity map, not a positive
loop-claim tranche.

Rows: `51`
Promising rows: `0`
Classification: `release_policy_no_role_gated_cycles_observed`

## Compact Summary

| Row | Lane | Policy | Source | Sink | Raw | Role-Gated | Would Claim | Max In-Flight | Max Budget Error |
| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| c1b_s_no_delay | S | no_delay | True | True | 0 | 0 | False | 0 | 4.44089e-16 |
| c1b_k_no_delay | K | no_delay | True | True | 0 | 0 | False | 0 | 0 |
| c1b_s_passive_leak_0p05 | S | passive_leak_0p05 | True | True | 0 | 0 | False | 0.0151029 | 1.11022e-16 |
| c1b_k_passive_leak_0p05 | K | passive_leak_0p05 | True | True | 0 | 0 | False | 0.000575707 | 3.33067e-16 |
| c1b_s_passive_leak_0p1 | S | passive_leak_0p1 | True | True | 0 | 0 | False | 0.00753631 | 2.22045e-16 |
| c1b_k_passive_leak_0p1 | K | passive_leak_0p1 | True | True | 0 | 0 | False | 0.000281231 | 2.22045e-16 |
| c1b_s_passive_leak_0p2 | S | passive_leak_0p2 | True | True | 0 | 0 | False | 0.00345971 | 2.22045e-16 |
| c1b_k_passive_leak_0p2 | K | passive_leak_0p2 | True | True | 0 | 0 | False | 0.000127328 | 3.33067e-16 |
| c1b_s_passive_leak_0p4 | S | passive_leak_0p4 | True | True | 0 | 0 | False | 0.00132354 | 2.22045e-16 |
| c1b_k_passive_leak_0p4 | K | passive_leak_0p4 | True | True | 0 | 0 | False | 4.82763e-05 | 2.22045e-16 |
| c1b_s_threshold_t0p0005_r0p5 | S | threshold_t0p0005_r0p5 | True | True | 0 | 0 | False | 0.000886378 | 2.22045e-16 |
| c1b_k_threshold_t0p0005_r0p5 | K | threshold_t0p0005_r0p5 | True | True | 0 | 0 | False | 0.000499909 | 2.22045e-16 |
| c1b_s_threshold_t0p0005_r1 | S | threshold_t0p0005_r1 | True | True | 0 | 0 | False | 0 | 4.44089e-16 |
| c1b_k_threshold_t0p0005_r1 | K | threshold_t0p0005_r1 | True | True | 0 | 0 | False | 0.000495595 | 2.22045e-16 |
| c1b_s_threshold_t0p001_r0p5 | S | threshold_t0p001_r0p5 | True | True | 0 | 0 | False | 0.000899011 | 2.22045e-16 |
| c1b_k_threshold_t0p001_r0p5 | K | threshold_t0p001_r0p5 | True | True | 0 | 0 | False | 0.000995061 | 2.22045e-16 |
| c1b_s_threshold_t0p001_r1 | S | threshold_t0p001_r1 | True | True | 0 | 0 | False | 0.000899011 | 2.22045e-16 |
| c1b_k_threshold_t0p001_r1 | K | threshold_t0p001_r1 | True | True | 0 | 0 | False | 0.000999128 | 2.22045e-16 |
| c1b_s_threshold_t0p002_r0p5 | S | threshold_t0p002_r0p5 | True | True | 0 | 0 | False | 0.00199858 | 2.22045e-16 |
| c1b_k_threshold_t0p002_r0p5 | K | threshold_t0p002_r0p5 | True | True | 0 | 0 | False | 0.0019939 | 2.22045e-16 |
| c1b_s_threshold_t0p002_r1 | S | threshold_t0p002_r1 | True | True | 0 | 0 | False | 0.00179728 | 1.11022e-16 |
| c1b_k_threshold_t0p002_r1 | K | threshold_t0p002_r1 | True | True | 0 | 0 | False | 0.0019939 | 2.22045e-16 |
| c1b_s_hysteretic_h0p001_r0p5 | S | hysteretic_h0p001_r0p5 | True | True | 0 | 0 | False | 0.000899011 | 2.22045e-16 |
| c1b_k_hysteretic_h0p001_r0p5 | K | hysteretic_h0p001_r0p5 | True | True | 0 | 0 | False | 0.000999042 | 2.22045e-16 |
| c1b_s_hysteretic_h0p001_r1 | S | hysteretic_h0p001_r1 | True | True | 0 | 0 | False | 0.000899011 | 4.44089e-16 |
| c1b_k_hysteretic_h0p001_r1 | K | hysteretic_h0p001_r1 | True | True | 0 | 0 | False | 0.000999128 | 2.22045e-16 |
| c1b_s_hysteretic_h0p002_r0p5 | S | hysteretic_h0p002_r0p5 | True | True | 0 | 0 | False | 0.00179728 | 1.11022e-16 |
| c1b_k_hysteretic_h0p002_r0p5 | K | hysteretic_h0p002_r0p5 | True | True | 0 | 0 | False | 0.00199474 | 2.22045e-16 |
| c1b_s_hysteretic_h0p002_r1 | S | hysteretic_h0p002_r1 | True | True | 0 | 0 | False | 0.00179728 | 1.11022e-16 |
| c1b_k_hysteretic_h0p002_r1 | K | hysteretic_h0p002_r1 | True | True | 0 | 0 | False | 0.0019939 | 2.22045e-16 |
| c1b_s_hysteretic_ref_h0p001_rf5 | S | hysteretic_ref_h0p001_rf5 | True | True | 0 | 0 | False | 0.00605235 | 2.22045e-16 |
| c1b_k_hysteretic_ref_h0p001_rf5 | K | hysteretic_ref_h0p001_rf5 | True | True | 0 | 0 | False | 0.000995061 | 2.22045e-16 |
| c1b_s_hysteretic_ref_h0p001_rf10 | S | hysteretic_ref_h0p001_rf10 | True | True | 0 | 0 | False | 0.0115619 | 2.22045e-16 |
| c1b_k_hysteretic_ref_h0p001_rf10 | K | hysteretic_ref_h0p001_rf10 | True | True | 0 | 0 | False | 0.000995061 | 2.22045e-16 |
| c1b_s_hysteretic_ref_h0p001_rf20 | S | hysteretic_ref_h0p001_rf20 | True | True | 0 | 0 | False | 0.0219151 | 2.22045e-16 |
| c1b_k_hysteretic_ref_h0p001_rf20 | K | hysteretic_ref_h0p001_rf20 | True | True | 0 | 0 | False | 0.000995061 | 2.22045e-16 |
| c1b_s_hysteretic_ref_h0p002_rf5 | S | hysteretic_ref_h0p002_rf5 | True | True | 0 | 0 | False | 0.00605506 | 2.22045e-16 |
| c1b_k_hysteretic_ref_h0p002_rf5 | K | hysteretic_ref_h0p002_rf5 | True | True | 0 | 0 | False | 0.0019939 | 2.22045e-16 |
| c1b_s_hysteretic_ref_h0p002_rf10 | S | hysteretic_ref_h0p002_rf10 | True | True | 0 | 0 | False | 0.0115544 | 1.11022e-16 |
| c1b_k_hysteretic_ref_h0p002_rf10 | K | hysteretic_ref_h0p002_rf10 | True | True | 0 | 0 | False | 0.0019939 | 2.22045e-16 |
| c1b_s_hysteretic_ref_h0p002_rf20 | S | hysteretic_ref_h0p002_rf20 | True | True | 0 | 0 | False | 0.0218888 | 2.22045e-16 |
| c1b_k_hysteretic_ref_h0p002_rf20 | K | hysteretic_ref_h0p002_rf20 | True | True | 0 | 0 | False | 0.0019939 | 2.22045e-16 |
| c1b_s_coupled_hysteretic_ref_h0p001_rf10 | S | coupled_hysteretic_ref_h0p001_rf10 | True | False | 0 | 0 | False | 0.109769 | 2.22045e-16 |
| c1b_k_coupled_hysteretic_ref_h0p001_rf10 | K | coupled_hysteretic_ref_h0p001_rf10 | True | True | 0 | 0 | False | 0.00351489 | 2.22045e-16 |
| c1b_s_forward_only_hysteretic_ref_h0p001_rf10 | S | forward_only_hysteretic_ref_h0p001_rf10 | True | True | 0 | 0 | False | 0.0115619 | 2.22045e-16 |
| c1b_k_forward_only_hysteretic_ref_h0p001_rf10 | K | forward_only_hysteretic_ref_h0p001_rf10 | True | True | 0 | 0 | False | 0.000995061 | 2.22045e-16 |
| c1b_s_return_only_hysteretic_ref_h0p001_rf10 | S | return_only_hysteretic_ref_h0p001_rf10 | True | False | 0 | 0 | False | 0.111117 | 1.11022e-16 |
| c1b_k_return_only_hysteretic_ref_h0p001_rf10 | K | return_only_hysteretic_ref_h0p001_rf10 | True | False | 0 | 0 | False | 0.00428492 | 2.22045e-16 |
| c1b_u0_coupled_hysteretic_ref_h0p001_rf10 | U0 | coupled_hysteretic_ref_h0p001_rf10 | False | False | 0 | 0 | False | 0 | 0 |
| c1b_u2_coupled_hysteretic_ref_h0p001_rf10 | U2 | coupled_hysteretic_ref_h0p001_rf10 | False | False | 0 | 0 | False | 0 | 0 |
| c1b_k_reversed_coupled_hysteretic_ref_h0p001_rf10 | K_reversed | coupled_hysteretic_ref_h0p001_rf10 | True | True | 0 | 0 | False | 0.00351489 | 2.22045e-16 |

## Errors

- none
