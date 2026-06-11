# Iteration 3 Loop Observable Smoke Report

Command:

```bash
python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_loop_observables.py
```

Status: `pass`

This smoke run uses synthetic traces only. It validates the experiment-local
observable library and does not import or modify `src/pygrc`.

## Trace Summary

| Trace | Budget | Source | Sink | Cascades | L4 Cycle Gate | Claim Allowed | Runner |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| U0_synthetic | True | False | False | 0 | False | False | synthetic_trace_validator |
| S_synthetic | True | True | True | 3 | True | False | synthetic_trace_validator |
| K_synthetic | True | True | True | 3 | True | False | synthetic_trace_validator |
| partial_cascade_synthetic | True | True | True | 0 | False | False | synthetic_trace_validator |
| phase_scrambled_synthetic | True | True | True | 0 | False | False | synthetic_trace_validator |
| budget_drift_synthetic | False | False | False | 0 | False | False | synthetic_trace_validator |
| budget_drift_with_cascade_synthetic | False | True | True | 3 | True | False | synthetic_trace_validator |

## Artifacts

- JSON report: `outputs/loop_observables_smoke_report.json`
- Time-series artifacts: `outputs/loop_observables_timeseries/*.jsonl`

## Errors

- none
