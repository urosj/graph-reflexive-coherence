# E2.2 Runtime Ledger Extraction

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/extract_e2_2_runtime_ledgers.py
```

Status: `passed`

Extracted ledger count: `8`

## Lane Validation

| Lane | Records | Departures | Arrivals | Triggers | Rearms | Cycles | Positive | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| E2.3-U0-no-surplus | 1 | 0 | 0 | 0 | 0 | 0 | no | 0 |
| E2.3-P-adapter-triggered-cw | 219 | 80 | 80 | 40 | 9 | 10 | yes | 0 |
| E2.3-R-adapter-triggered-ccw | 219 | 80 | 80 | 40 | 9 | 10 | yes | 0 |
| E2.3-C-subthreshold | 1 | 0 | 0 | 0 | 0 | 0 | no | 0 |
| E2.3-C-wrong-direction | 201 | 80 | 80 | 40 | 0 | 0 | no | 0 |
| E2.3-C-forward-only | 6 | 2 | 2 | 1 | 0 | 0 | no | 0 |
| E2.3-C-broken-return | 16 | 6 | 6 | 3 | 0 | 0 | no | 0 |
| E2.3-C-scrambled-order | 6 | 2 | 2 | 1 | 0 | 0 | no | 0 |

## Interpretation

E2.2 extracts E2.3 native LGRC9V3 runtime packet events and adapter-derived trigger/self-rearm evidence into E1-compatible per-lane ledgers. Ledger-only validation reproduces the positive and negative classifications while preserving native event ids, event-time keys, scheduler indices, and proper-time updates where available. Route, trigger, self-rearm, cycle, and control semantics remain experiment-inferred evidence.
