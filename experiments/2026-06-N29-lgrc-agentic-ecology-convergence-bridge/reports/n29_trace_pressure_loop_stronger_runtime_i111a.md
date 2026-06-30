# N29 Iteration 11.1-A - Stronger Runtime Instantiation

## Summary

- status: `passed`
- acceptance_state: `accepted_stronger_three_pole_runtime_candidate_pending_controls_replay`
- output_digest: `e8e273643fa37e414153ff58ef34a56a6b0b1a7c334ea30949ae89492ebe0e0e`

- completed_leg_count: `6`
- min_surplus_after_arrival: `0.25`
- min_pressure_margin: `0.201`

I11.1-A runs the stronger three-pole route in LGRC9V3. It remains
producer-assisted and pending controls/replay.

## Checks

| Check | Passed |
| --- | --- |
| `i111_source_passed` | `true` |
| `runtime_artifact_present` | `true` |
| `self_rearm_validation_passed` | `true` |
| `six_completed_legs` | `true` |
| `pressure_margin_stronger_than_i11c` | `true` |
| `producer_success_does_not_upgrade_native` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
