# D2.3 Self-Rearming Packet Pulse Probe

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d2_3_self_rearming_packets.py
```

Status: `pass`

Classification: `d2_3_self_rearming_packet_pulse_candidate_with_controls`

D2.3 tests whether a state-triggered packet loop can re-arm after
cycle completion when the returned packet recreates source surplus. It
remains experiment-local packetized prototype evidence, not native
GRC9V3 evidence.

Budget invariant:

```text
B = sum(node coherence) + sum(in-flight packet coherence)
```

## Audit

- direction reversal symmetry: `True`
- max node-plus-packet budget error: `0`
- duplicate packet ids: `0`
- orphan parent ids: `0`
- unknown channel ids: `0`

## Lane Summary

| Lane | Mode | Direction | Triggers | Rearms | Events | Cycles | Opposite | Drift | Budget | Packet Audit | Causality | Expected | Positive |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| D2.3-U0-no-surplus | closed_loop | cw | 0 | 0 | 0 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.3-P-self-rearming-cw | closed_loop | cw | 47 | 11 | 46 | 11 | 0 | 0 | pass | pass | pass | positive | yes |
| D2.3-R-self-rearming-ccw | closed_loop | ccw | 47 | 11 | 46 | 11 | 0 | 0 | pass | pass | pass | positive | yes |
| D2.3-C-single-pass-no-rearm | closed_loop | cw | 0 | 0 | 0 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.3-C-subthreshold | closed_loop | cw | 0 | 0 | 0 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.3-C-threshold-too-high | closed_loop | cw | 0 | 0 | 0 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.3-S-low-threshold | closed_loop | cw | 47 | 11 | 46 | 11 | 0 | 0 | pass | pass | pass | positive | yes |
| D2.3-C-wrong-direction | closed_loop | cw | 47 | 0 | 46 | 0 | 11 | 0 | pass | pass | fail | negative | no |
| D2.3-C-forward-only | forward_only | cw | 1 | 0 | 1 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.3-C-broken-return | broken_return | cw | 3 | 0 | 3 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.3-C-scrambled-order | scrambled_order | cw | 1 | 0 | 1 | 0 | 0 | 0 | pass | pass | pass | negative | no |
| D2.3-N-jittered-delay | closed_loop | cw | 47 | 11 | 46 | 11 | 0 | 0 | pass | pass | pass | positive | yes |

## Interpretation

D2.3 tests natural self-rearming of the state-triggered packet loop. Positive rows are self-rearming packetized pulse candidates: the final packet in a completed cycle returns coherence to the source pole, the measured source surplus crosses the serialized trigger threshold, and the next packet departs without a hand-authored schedule. This remains experiment-local packetized prototype evidence only; native GRC9V3, movement, and agency claims remain blocked.

## Errors

- none
