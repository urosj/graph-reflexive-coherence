# N04 Evidence Ladder Audit

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_evidence_ladder_audit.py
```

Status: `passed`
Claim boundary: movement claims allowed = `False`

## Evidence Ladder

| Level | Classification | Source |
|---|---|---|
| `M0_M1_fixed_substrate` | `movement_negative_with_subthreshold_bias_diagnostics` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_classifier_m0_m3_validation.json` |
| `M2_M3_identity_shape` | `safety_gates_validated_no_displacement_promotion` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_classifier_m0_m3_validation.json` |
| `boundary_coupling_fixture` | `state_mediated_boundary_coupling_fixture_positive` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_report.json` |
| `M4_M5_candidate` | `m5_candidate_control_limited` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/loop_driven_movement_m4_m5_report.json` |

## Allowed Evidence Labels

- `fixed_substrate_negative`
- `subthreshold_directional_bias`
- `state_mediated_boundary_coupling_fixture_positive`
- `m5_candidate_control_limited`

## Blocked Claims

- `movement_response`
- `boundary_coupled_movement`
- `loop_driven_movement`
- `locomotion_like_basin_dynamics`
- `adaptive_topology_movement`
- `M6_self_renewing_movement`
- `biological_or_agency_claim`
- `movement_inherited_from_n03`

## Next Evidence Gap

- Primary: `native_true_reversed_e3_pulse_direction_parity`
- Alternative: `close_current_N04_tranche_as_m5_candidate_control_limited`

## Checks

| Check | Passed |
|---|---:|
| `all_source_artifacts_present` | `True` |
| `fixed_substrate_all_m0` | `True` |
| `iteration_8_fixture_positive_not_movement` | `True` |
| `iteration_9_candidate_control_limited` | `True` |
| `m6_remains_blocked` | `True` |
| `all_global_claims_blocked` | `True` |

## Interpretation

A1 clears the existing N04 evidence without promoting new claims. The fixed-substrate tranche remains movement-negative, Iteration 8 remains a fixture-level state-mediated boundary-coupling positive, and Iteration 9 remains an M5-style candidate/control-limited result. Iteration 10/M6 remains blocked.
