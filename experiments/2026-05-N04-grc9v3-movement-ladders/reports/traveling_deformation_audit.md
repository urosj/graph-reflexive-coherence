# N04 Lane D3 Traveling Deformation Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_traveling_deformation_audit.py
```

Status: `passed`
Claim ceiling: `traveling_deformation_candidate`

## Positive Lane

- Pulse peak sequence: `[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]`
- Deformation peak sequence: `[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]`
- Phase lag nodes: `[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]`
- Deformation displacement: `10`
- Width min/max: `2` / `2`
- Causal time lag steps: `1`
- Causal lag matches: `True`

## Instantaneous Reference

- Reference deformation displacement: `10`
- Reference phase lag nodes: `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]`

## Controls

- `static_pulse`: `local_deformation_without_travel`
- `geometry_coupling_disabled`: `deformation_absent`
- `pulse_disabled`: `pulse_absent`
- `reversed_pulse`: `not_a_negative_control_direction_reversal_positive`

## Interpretation

D3 supports a traveling deformation candidate: the local support
deformation at step t is linked to pulse contact at step t-1,
so the positive lane has an explicit causal time lag rather than
only an instantaneous same-step response. Reversed pulse direction
reverses the deformation direction on the same local coupling rule.
This is not yet a movement claim; movement-ladder reclassification
is deferred to D5.
