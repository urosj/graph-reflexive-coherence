# N04 Initial Tranche Closeout

Status: `passed`
Result: `closed_with_taxonomy_handoff`
Next iteration: `13_taxonomy_inventory`

## Claim Ceiling

- strongest current ceiling: `native_m6_same_fixture_self_renewal_candidate`
- native_m6: `True`
- native_m6_candidate_gate_passed: `True`
- movement_claim_allowed: `False`

This closes the initial fixed-substrate/M0-M6 tranche. It does not close N04.

## Source Of Truth By Rung

### M0
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/fixed_substrate_tranche_a_report.json`
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_classifier_m0_m3_validation.json`

### M1
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_observables_timeseries/S0_chain_v1_basin_replacement.jsonl`
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_classifier_m0_m3_validation.json`

### M2
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m2_runtime_shape_blocked_fixture.json`
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/m2_runtime_shape_blocked_timeseries/M2_shape_degraded_boundary_handoff.jsonl`

### M3
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_observables_timeseries/S0_chain_v1_shape_preserving_shift.jsonl`
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/movement_classifier_m0_m3_validation.json`

### M4
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/boundary_coupled_pulse_report.json`
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/loop_driven_movement_m4_m5_report.json`

### M5
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_b_direction_parity_closeout.json`

### M6
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_m6_same_fixture_validator.json`
- `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_m6_validation_checklist_audit.json`

## Summaries

- M2: `M2_identity_preserving_displacement` with `shape_gate_failed`.
- M5: `m5_direction_parity_supported_boundary_response`.
- M6: `native_m6_same_fixture_self_renewal_candidate` on `S0_chain_v1`.

## Blocked Claims

- `movement_claim_allowed`
- `loop_driven_movement_claim_allowed`
- `locomotion_like_claim_allowed`
- `adaptive_topology_entry_allowed`
- `biological_claim_allowed`
- `agency_claim_allowed`
- `identity_acceptance_claim_allowed`
- `movement_claim_inherited_from_n03`
- `unrestricted_movement_claim_allowed`

## Taxonomy Continuation Handoff

Inventory and separate movement taxonomy classes across centroid, boundary, shape, deformation, basin identity, self-renewal, geometry, and topology axes.

First artifacts:

- `outputs/n04_taxonomy_inventory_v1.json`
- `reports/n04_taxonomy_inventory_v1.md`

Adaptive topology status: `blocked_until_explicit_topology_controls`

## Checks

| Check | Passed |
|---|---:|
| `all_source_artifacts_present` | `True` |
| `fixed_substrate_claims_remain_blocked` | `True` |
| `m2_runtime_fixture_passed` | `True` |
| `m5_direction_parity_supported` | `True` |
| `native_m6_same_fixture_candidate_passed` | `True` |
| `broader_claims_blocked` | `True` |
| `taxonomy_continuation_opened` | `True` |
| `visual_reference_current` | `True` |

## Acceptance

Iteration 12 closes the initial N04 fixed-substrate/M0-M6 tranche and opens Iterations 13-19 as a movement-taxonomy/topology search sequence. The closeout preserves the bounded native M6 same-fixture candidate and the M0-M6 evidence ladder, but it does not permit adaptive-topology, locomotion-like, biological, agency, identity-acceptance, inherited-N03, or unrestricted movement claims.
