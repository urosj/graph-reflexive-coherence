# Iteration 5 One-Time Kick Lane Report

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_kick_lanes.py
```

Status: `pass`

This report uses real `GRC9V3` fixed-topology continuity execution with
one experiment-local zero-sum kick applied before the first transport
rebuild. It does not call `step()`, spark expansion, growth, boundary
behavior, birth, or pruning.

## Lane Summary

| Lane | Budget | Source | Sink | Raw Cascades | Role-Gated Cascades | Claim Allowed |
| --- | --- | --- | --- | ---: | ---: | --- |
| K | True | False | False | 0 | 0 | False |
| K_reversed | True | False | False | 0 | 0 | False |

## Reversal Outcome

- outcome: `failure`
- reason: neither kick direction produced paired role-gated loop evidence

## Blocked Controls

- shuffled conductance: blocked as non-informative for uniform conductance surface
- budget-projection-disabled dry run: blocked pending a separate approved diagnostic runner

## Errors

- none
