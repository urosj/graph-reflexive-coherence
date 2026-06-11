# N04 Native M6 Same-Fixture Validator

Status: `passed`
Claim ceiling: `native_m6_same_fixture_self_renewal_candidate`

## Result

Native LGRC9V3 now supports a same-fixture M6 self-renewal candidate on S0: after one seeded packet contact, native feedback eligibility rows authorize regenerated packet work through the native feedback producer for both forward and reversed boundary polarity. This remains a bounded M6 candidate, not locomotion, agency, biology, adaptive topology, or unrestricted movement.

## Gates

- native_same_fixture_validator_available: `True`
- forward_self_renewed_cycles_passed: `True`
- reversed_self_renewed_cycles_passed: `True`
- native_repeated_self_renewed_cycles_measured: `True`
- movement_restores_pulse_conditions: `True`
- polarity_regeneration_measured: `True`
- artifact_only_validation_passed: `True`
- budget_gate_passed: `True`
- nonnegative_gate_passed: `True`
- identity_shape_gates_integrated: `True`
- controls_negative: `True`
- topology_fixed: `True`

## Direction Parity

- forward dX: `0.026190476190476986`
- reversed dX: `-0.026190476190476986`
- passed: `True`

## Self-Renewed Cycles

- forward: `3`
- reversed: `3`

## Controls

- pulse_disabled: passed=`True`, reason=`feedback_surface_requires_committed_pulse_contact`
- feedback_disabled: passed=`True`, reason=`feedback_coupled_pulse_disabled`
- subthreshold: passed=`True`, reason=`feedback_coupled_pulse_subthreshold`
- wrong_polarity: passed=`True`, reason=`feedback_coupled_pulse_wrong_polarity`
- budget_violation: passed=`True`, reason=`budget_surface_gate_failed`

## Claim Flags

```json
{
  "adaptive_topology_entry_allowed": false,
  "agency_claim_allowed": false,
  "biological_claim_allowed": false,
  "identity_acceptance_claim_allowed": false,
  "locomotion_like_claim_allowed": false,
  "loop_driven_movement_claim_allowed": false,
  "movement_claim_allowed": false,
  "movement_claim_inherited_from_n03": false,
  "native_m6": true,
  "native_m6_candidate_gate_passed": true
}
```

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_native_m6_same_fixture_validator.py
```
