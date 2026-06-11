# D2.1 Packet Loop Robustness And Conservation Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_1_packet_loop_robustness.py
```

Status: `pass`

Classification: `d2_1_packet_loop_robustness_passed`

D2.1 hardens the D2 packetized closed-flow prototype. It is
experiment-local packetized prototype evidence, not native GRC9V3
evidence, and it does not open movement claims.

Budget invariant:

```text
B = sum(node coherence) + sum(in-flight packet coherence)
```

## Robustness Checks

- direction reversal symmetry: `True`
- max packet budget error: `1.11022e-16`
- duplicate packet ids: `0`
- orphan parent ids: `0`
- unknown channel ids: `0`

## Lane Summary

| Lane | Mode | Direction | Delay | Amount | Events | Cycles | Opposite | Budget | Packet Audit | Causality | Expected | Positive |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| D2.1-U0-no-seed | closed_loop | cw | 3 | 0.006 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.1-P-cw-delay-1 | closed_loop | cw | 1 | 0.006 | 139 | 34 | 0 | pass | pass | pass | positive | yes |
| D2.1-P-cw-delay-3 | closed_loop | cw | 3 | 0.006 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.1-P-cw-delay-6 | closed_loop | cw | 6 | 0.006 | 23 | 5 | 0 | pass | pass | pass | positive | yes |
| D2.1-R-ccw-delay-3 | closed_loop | ccw | 3 | 0.006 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.1-C-wrong-direction-seed | closed_loop | cw | 3 | 0.006 | 46 | 0 | 11 | pass | pass | fail | negative | no |
| D2.1-C-forward-only | forward_only | cw | 3 | 0.006 | 28 | 0 | 0 | pass | pass | fail | negative | no |
| D2.1-C-broken-return | broken_return | cw | 3 | 0.006 | 3 | 0 | 0 | pass | pass | pass | negative | no |
| D2.1-C-scrambled-order | scrambled_order | cw | 3 | 0.006 | 46 | 0 | 0 | pass | pass | fail | negative | no |
| D2.1-S-weak-seed | closed_loop | cw | 3 | 0.0005 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.1-S-over-seed | closed_loop | cw | 3 | 0.02 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.1-N-jittered-delay | closed_loop | cw | 3 | 0.006 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.1-N-node-perturbation | closed_loop | cw | 3 | 0.006 | 46 | 11 | 0 | pass | pass | pass | positive | yes |

## Interpretation

D2.1 confirms whether the D2 packetized prototype survives robustness checks: exact node-plus-packet budget accounting, packet-id loss/duplication audit, declared channel causality, direction reversal symmetry, seed dependence controls, delay sweep, and deterministic small perturbations. Positive rows remain packetized prototype evidence only; native GRC9V3 and movement claims remain blocked.

## Errors

- none
