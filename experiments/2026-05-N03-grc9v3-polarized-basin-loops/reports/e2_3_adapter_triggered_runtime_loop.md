# E2.3 Adapter-Triggered Runtime Loop

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e2_3_adapter_triggered_runtime_loop.py
```

Status: `passed`

Classification: `adapter_triggered_runtime_loop_with_controls`

Boundary:

```text
native_grc9v3_evidence = false
native_lgrc9v3_execution = true
adapter_only = false
movement_claim_allowed = false
adapter_driven_runtime_execution = true
native_autonomous_runtime_execution = false
```

## Audit

- direction reversal symmetry: `True`
- max budget error: `0`
- max event budget error: `2.22045e-16`
- expectation failures: `[]`

## Lane Summary

| Lane | Mode | Direction | Behavior | Triggers | Continuations | Rearms | Runtime Events | Cycles | Opposite | Budget | Topology | Expected | Positive |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| E2.3-U0-no-surplus | closed_loop | cw | cw | 0 | 0 | 0 | 0 | 0 | 0 | pass | pass | negative | no |
| E2.3-P-adapter-triggered-cw | closed_loop | cw | cw | 41 | 40 | 9 | 160 | 10 | 0 | pass | pass | positive | yes |
| E2.3-R-adapter-triggered-ccw | closed_loop | ccw | ccw | 41 | 40 | 9 | 160 | 10 | 0 | pass | pass | positive | yes |
| E2.3-C-subthreshold | closed_loop | cw | cw | 0 | 0 | 0 | 0 | 0 | 0 | pass | pass | negative | no |
| E2.3-C-wrong-direction | closed_loop | cw | ccw | 41 | 40 | 0 | 160 | 0 | 10 | pass | pass | negative | no |
| E2.3-C-forward-only | forward_only | cw | cw | 1 | 1 | 0 | 4 | 0 | 0 | pass | pass | negative | no |
| E2.3-C-broken-return | broken_return | cw | cw | 3 | 3 | 0 | 12 | 0 | 0 | pass | pass | negative | no |
| E2.3-C-scrambled-order | scrambled_order | cw | cw | 1 | 1 | 0 | 4 | 0 | 0 | pass | pass | negative | no |

## Interpretation

E2.3 shows that an experiment-local surplus trigger adapter can drive existing LGRC9V3 packet execution into repeated route cycles with returned-packet self-rearm evidence. Packet departure/arrival processing, budget accounting, event-time, and proper-time mutation are native LGRC9V3 runtime behavior. Trigger authorization, route semantics, and self-rearm labels remain adapter-derived, so this is adapter-driven runtime execution, not native autonomous LGRC9V3 loop production. Counted self-rearm evidence requires the child departure to have been processed by the native runtime inside the bounded event window.
