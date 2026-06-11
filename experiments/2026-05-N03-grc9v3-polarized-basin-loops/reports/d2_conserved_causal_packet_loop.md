# D2 Conserved Causal Packet Loop Prototype

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_conserved_causal_packet_loop.py
```

Status: `pass`

Classification: `d2_packetized_closed_flow_positive_with_controls`

D2 promotes D1f4 causal packet delay only. It is experiment-local
packetized prototype evidence, not native GRC9V3 evidence.

Budget invariant:

```text
B = sum(node coherence) + sum(in-flight packet coherence)
```

## Lane Summary

| Lane | Mode | Direction | Events | Cycles | Opposite Cycles | Max Norm Circ | Budget | Expected | Positive |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| D2-U0-no-seed | closed_loop | cw | 0 | 0 | 0 | 0 | pass | negative | no |
| D2-P-cw-packet-loop | closed_loop | cw | 46 | 11 | 0 | 1 | pass | positive | yes |
| D2-R-ccw-packet-loop | closed_loop | ccw | 46 | 11 | 0 | 1 | pass | positive | yes |
| D2-C-forward-only | forward_only | cw | 28 | 0 | 0 | 1 | pass | negative | no |
| D2-C-broken-return | broken_return | cw | 3 | 0 | 0 | 1 | pass | negative | no |
| D2-C-scrambled-order | scrambled_order | cw | 46 | 0 | 0 | 1 | pass | negative | no |

## Interpretation

D2 shows whether a packetized in-flight coherence layer can turn the D1e static role surface into closed-loop propagation under explicit budget accounting. Positive lanes are packetized prototype evidence only; native GRC9V3 and movement claims remain blocked.

## Errors

- none
