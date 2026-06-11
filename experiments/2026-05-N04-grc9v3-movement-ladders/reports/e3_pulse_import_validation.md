# E3 Pulse Import Validation

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/validate_e3_pulse_import.py
```

Status: `passed`

## Summary

- Runtime family: `LGRC9V3`
- Execution surface: `surface_c_lgrc9v3_e3_pulse_import`
- Source result: `E3_native_LGRC9V3_D2_3_equivalent_packet_loop`
- Loop ladder level: `L5`
- Movement claim inherited: `False`
- Claim ceiling: `e3_pulse_import_validation_only`
- Movement state mutated by import: `False`
- Fixed-substrate tranche A result: `no_movement_response_candidates`

## Checks

| Check | Passed |
|---|---:|
| `schema_is_movement_ladder_report_v1` | `True` |
| `source_e3_closeout_passed` | `True` |
| `native_lgrc9v3_execution_true` | `True` |
| `native_d2_3_equivalent_true` | `True` |
| `movement_claim_not_inherited` | `True` |
| `budget_surface_recorded` | `True` |
| `positive_pulse_rows_imported` | `True` |
| `pulse_disabled_control_available` | `True` |
| `pulse_active_boundary_disabled_does_not_mutate_movement_state` | `True` |
| `direction_reversal_control_available` | `True` |
| `scrambled_control_available` | `True` |
| `required_controls_available` | `True` |
| `snapshot_telemetry_replayable` | `True` |
| `direct_movement_state_writes_absent` | `True` |
| `fixed_substrate_classification_unchanged` | `True` |
| `route_structural_reversal_verified` | `True` |

## Positive Pulse Rows

| Direction | Cycles | Self-Rearms | Route Digest | Max Budget Error |
|---|---:|---:|---|---:|
| `clockwise` | `3` | `12` | `25ce1cc1550c0a717d4c1bcaa7f4179789024b67c2c22893df1f0fa21d41cb57` | `0.0` |
| `counter_clockwise` | `3` | `12` | `a621e96cd477308e0365b1d06f2a80f4a1285c7c7f4680d24cd3715a878ef3c8` | `0.0` |

## Controls

- Pulse disabled: metadata loaded = `True`, pulse active = `False`, movement state mutated = `False`
- Pulse active, boundary coupling disabled: packet loop observed = `True`, movement state mutated = `False`
- Direction reversal passed: `True`
- Structural route reversal passed: `True`
- Scrambled/non-self-rearming control passed: `True`
- Direct boundary/support/centroid writes: `False`

## Compatibility Notes

- E3 source fixture: `n03_e3_native_four_pole_packet_loop` with `4` nodes
- N04 active fixtures: `['S0_chain_v1', 'S1_ring_v1']`
- Mapping strategy defined: `False`
- Pulse taxonomy status: `local_import_taxonomy_for_n04_iteration_7`

## Import No-Op

- State hash equal: `True`
- Movement metrics equal: `True`
- Topology equal: `True`
- Budget equal: `True`

## Budget

- Budget surface: `node_plus_packet`
- Packet amount: `0.1`
- Max positive event budget error: `0.0`
- Max control event budget error: `8.881784197001252e-16`
- Note: E3 source artifacts expose node-plus-packet budget surface and max event budget errors; exact node/in-flight totals are not serialized in the closeout rows imported by Iteration 7.

## Notes

- Iteration 7 imports E3 pulse metadata as a drive candidate only.
- No N04 movement state is mutated by the import.
- The import mutation audit is true by construction because the adapter is read-only.
- E3 heartbeat remains pulse-substrate evidence, not movement evidence.
- Boundary coupling remains disabled until later iterations.
- E3 source artifacts are pinned by SHA-256; the source seed is not serialized in the imported E3 closeout.
- Iteration 8 must define the four-pole E3 route to N04 movement-fixture mapping before boundary coupling is tested.
- Iteration 7-B may require additional E3 telemetry or reconstruction if exact node/in-flight budget split is needed.
