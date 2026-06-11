# D1f Minimal Handoff Mechanism Probes

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_d1f_minimal_handoff_mechanisms.py
```

Status: `pass`

Classification: `d1f_phase_and_closed_flow_positive_lanes_observed`

D1f is experiment-local mechanism isolation. It is not native GRC9V3
evidence and not a positive N03 loop claim.

## Lane Summary

| Lane | Mechanism | Events | Phase Cycles | Closed-Flow Steps | Max Norm Circ | Budget | Positive Surface |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| D1f1 | explicit phase handoff | 35 | 8 | 0 | 1 | pass | phase |
| D1f2 | edge/corridor storage | 280 | 0 | 0 | 1 | pass | none |
| D1f3 | momentum retention | 560 | 0 | 140 | 1 | pass | closed-flow |
| D1f4 | causal packet delay | 46 | 11 | 0 | 1 | pass | phase |
| D1f5 | adaptive role handoff | 47 | 11 | 0 | 1 | pass | phase |

## Interpretation

D1f isolates missing mechanisms after D1e. Positive lanes show that a specific added mechanism can generate ordered closed-loop event cycles under budget conservation, but because the mechanism is experiment-local the result is sufficiency evidence for a future prototype, not native GRC9V3 loop evidence.

## Errors

- none
