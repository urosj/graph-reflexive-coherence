# N04 Lane D4 Direction And Null Controls

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_pulse_substrate_direction_null_controls.py
```

Status: `passed`
Claim ceiling: `direction_controlled_traveling_deformation_supported`

## Controls

- `geometry_coupling_disabled`: `deformation_absent`
- `pulse_disabled`: `pulse_absent`
- `static_pulse`: `local_deformation_without_travel`
- `reversed_pulse`: `not_a_negative_control_direction_reversal_positive`
- `scrambled_timing_order`: `canonical_pulse_order_failed`
- `symmetric_coupling_null`: `balanced_symmetric_geometry_response`
- `budget_violating_synthetic`: `budget_gate_failed`
- `nonnegative_violating_synthetic`: `nonnegative_gate_failed`

## Interpretation

D4 hardens D3 with direction and null controls. Scrambled order
preserves pulse mass profile, event count, budget, and observation
window while failing canonical order. Symmetric coupling remains
balanced. Budget and nonnegative synthetic blockers fail for their
declared reasons. This supports direction-controlled traveling
deformation as mechanism evidence only; movement classification is
still deferred to D5.
