# N04 Lane D5 Movement Reclassification

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_pulse_substrate_movement_reclassification.py
```

Status: `passed`
Claim ceiling: `substrate_carried_deformation_movement_candidate`

## D-Level

- D label: `D5_direction_controlled_traveling_deformation_supported`

## Movement-Candidate Probe

- Deformation displacement: `10.0`
- Response windows: `11`
- M projection: `M3_shape_preserving_identity_displacement_candidate_on_deformation_surface`
- M5-style deformation candidate: `True`

## Claim Boundary

- Runtime coherence basin moved: `False`
- Full movement claim allowed: `False`
- Primary blocker: `deformation_surface_is_not_runtime_coherence_basin`

## Interpretation

D5 finds a substrate-carried deformation movement candidate on the
deformation surface: the direction-controlled traveling deformation
projects through the frozen movement-style gates as an M3/M5-style
surface candidate. This is not a full movement claim because the moved
identity is a causal geometry-deformation token, not a runtime coherence
basin. Lane E should decide whether a native LGRC causal pulse-substrate
surface is broad enough to promote this mechanism.
