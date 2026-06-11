# E2.3-A Adapter-Triggered Runtime Loop Hardening

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_e2_3_adapter_triggered_runtime_loop.py
```

Status: `passed`

## Audit

- adapter state visibility: `True`
- self-rearm causality: `True`
- ledger-only validation: `True`
- direction symmetry details: `True`
- per-event budget preserved: `True`

## Ledger-Only Lane Summary

| Lane | Cycles | Opposite | Rearms | Paired Packets | Budget Error | Topology Mutations | Positive | Matches Runner |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| E2.3-U0-no-surplus | 0 | 0 | 0 | 0 | 0 | 0 | no | yes |
| E2.3-P-adapter-triggered-cw | 10 | 0 | 9 | 80 | 2.22045e-16 | 0 | yes | yes |
| E2.3-R-adapter-triggered-ccw | 10 | 0 | 9 | 80 | 2.22045e-16 | 0 | yes | yes |
| E2.3-C-subthreshold | 0 | 0 | 0 | 0 | 0 | 0 | no | yes |
| E2.3-C-wrong-direction | 0 | 10 | 0 | 80 | 2.22045e-16 | 0 | no | yes |
| E2.3-C-forward-only | 0 | 0 | 0 | 2 | 2.22045e-16 | 0 | no | yes |
| E2.3-C-broken-return | 0 | 0 | 0 | 6 | 2.22045e-16 | 0 | no | yes |
| E2.3-C-scrambled-order | 0 | 0 | 0 | 2 | 2.22045e-16 | 0 | no | yes |

## Interpretation

E2.3-A hardens the adapter-triggered runtime result using only the E2.3 artifact. It confirms that adapter triggers expose measured runtime-state fields, self-rearm labels follow returned-packet arrival and threshold crossing, ledger-only event records reproduce positive/control classifications, direction reversal symmetry holds across event counts and timing, and per-event budget errors remain within tolerance.
