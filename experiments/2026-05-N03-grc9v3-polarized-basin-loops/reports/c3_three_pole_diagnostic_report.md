# C3 Three-Pole Diagnostic Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_c3_three_pole_diagnostic.py
```

Status: `pass`

C3 is a three-pole diagnostic surface, not a positive loop-claim tranche.

## Synthetic Validator

| Lane | Raw Cascades | Role-Gated Cascades | Budget |
| --- | ---: | ---: | --- |
| ordered | 4 | 4 | True |
| scrambled | 0 | 0 | True |
| two_pole | 0 | 0 | True |
| budget_drift | 0 | 0 | False |

## Runtime Fixed-Topology

| Lane | Network Closure | Raw Cascades | Role-Gated Cascades | Candidate | Topology Changed |
| --- | ---: | ---: | ---: | --- | --- |
| U0 | 0 | 0 | 0 | False | False |
| U3 | 0 | 0 | 0 | False | False |
| P | 0 | 0 | 0 | False | False |
| P_reversed | 0 | 0 | 0 | False | False |

## Classification

`c3_fixed_topology_no_three_pole_candidate_rows`

## Errors

- none
