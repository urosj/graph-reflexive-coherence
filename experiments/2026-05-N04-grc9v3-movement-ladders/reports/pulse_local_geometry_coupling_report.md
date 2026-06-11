# N04 Lane D2 Local Geometry Coupling

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_local_geometry_coupling.py
```

Status: `passed`
Claim ceiling: `pulse_local_geometry_coupling`

## Positive Lane

- Geometry surface: `local_support_mass`
- Coupling count: `11`
- Response rows: `11`
- Max support delta: `0.10000000000000009`
- Max locality distance: `1`
- Max geometry budget error: `0.0`
- Minimum geometry state: `0.9`

## Controls

- `geometry_coupling_disabled`: `geometry_coupling_disabled`
- `pulse_disabled`: `pulse_absent`
- `static_pulse`: `local_response_without_transport`

## Interpretation

D2 proves local geometry/support response to pulse contact only.
The declared geometry surface is local support mass at the pulse
peak. The update is local, budget-conserving, nonnegative, and does
not directly write support masks, centroid, displacement, topology,
or claim flags. Traveling deformation and movement remain blocked.
