# D2.2 State-Triggered Packet Departure

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_2_state_triggered_packets.py
```

Status: `pass`

Classification: `d2_2_state_triggered_packet_departure_positive_with_controls`

D2.2 launches packet departures from measured pole-surplus state
instead of a hand-authored packet seed schedule. It remains
experiment-local packetized prototype evidence, not native GRC9V3
evidence.

Budget invariant:

```text
B = sum(node coherence) + sum(in-flight packet coherence)
```

## Audit

- direction reversal symmetry: `True`
- max node-plus-packet budget error: `1.11022e-16`
- duplicate packet ids: `0`
- orphan parent ids: `0`
- unknown channel ids: `0`

## Lane Summary

| Lane | Mode | Direction | Delay | Initial Surplus | Triggers | Events | Cycles | Opposite | Budget | Packet Audit | Causality | Expected | Positive |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| D2.2-U0-no-surplus | closed_loop | cw | 3 | 0 | 0 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.2-P-cw-state-triggered | closed_loop | cw | 3 | 0.006 | 47 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.2-R-ccw-state-triggered | closed_loop | ccw | 3 | 0.006 | 47 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.2-P-cw-delay-1 | closed_loop | cw | 1 | 0.006 | 140 | 139 | 34 | 0 | pass | pass | pass | positive | yes |
| D2.2-P-cw-delay-6 | closed_loop | cw | 6 | 0.006 | 24 | 23 | 5 | 0 | pass | pass | pass | positive | yes |
| D2.2-C-subthreshold-surface | closed_loop | cw | 3 | 0.0015 | 0 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.2-C-wrong-direction-trigger | closed_loop | cw | 3 | 0.006 | 47 | 46 | 0 | 11 | pass | pass | fail | negative | no |
| D2.2-C-forward-only | forward_only | cw | 3 | 0.006 | 1 | 1 | 0 | 0 | pass | pass | pass | negative | no |
| D2.2-C-broken-return | broken_return | cw | 3 | 0.006 | 3 | 3 | 0 | 0 | pass | pass | pass | negative | no |
| D2.2-S-weak-trigger | closed_loop | cw | 3 | 0.0005 | 47 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.2-S-over-trigger | closed_loop | cw | 3 | 0.02 | 47 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.2-N-jittered-delay | closed_loop | cw | 3 | 0.006 | 47 | 46 | 11 | 0 | pass | pass | pass | positive | yes |
| D2.2-N-node-perturbation | closed_loop | cw | 3 | 0.006 | 47 | 46 | 11 | 0 | pass | pass | pass | positive | yes |

## Interpretation

D2.2 shows that the D2 packetized prototype can be launched by a measured state trigger: source-pole mass above a serialized threshold. Departure timing is derived from the evolving node state plus packet arrivals, not from a hand-authored packet seed schedule. Positive rows remain packetized prototype evidence only; native GRC9V3 and movement claims remain blocked.

## Errors

- none
