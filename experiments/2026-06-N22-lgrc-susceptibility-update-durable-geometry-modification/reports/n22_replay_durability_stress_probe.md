# N22 Iteration 5-A - Replay Durability Stress Probe

Status: `passed`

Acceptance state: `accepted_replay_stress_limited_su3_candidates_pending_i7_controls`

Output digest: `2602c7b3fb99b19521b5a72f0615f0ff401aa2cb532674df7eeae2875c48ff27`

## Summary

Iteration 5-A stress-tests the I5 replay-backed SU3 candidates without
changing thresholds or opening SU4. Stress modes are baseline post-
snapshot re-entry, delayed idle windows before re-entry, repeated re-entry,
and mild unrelated peer flux before re-entry.

I5 tested clean replay. I5-A keeps the same thresholds and starts from the saved post-interaction state, then delays re-entry, repeats re-entry, or injects a mild unrelated peer flux before route_b re-entry. The second repeated re-entry depletes the route-specific delta below the SU3 preservation ratio, so I5-A records limited replay-stress support rather than SU4 evidence.

## Stress Rows

| Row | Source | Passed Modes | Role | Narrow |
| --- | --- | ---: | --- | --- |
| `i4_minimal_route_b` | `I4` | 3/4 | `replay_stress_limited_SU3_candidate_pending_I7_controls` | `false` |
| `dose_08_i4_reference` | `I4-A` | 3/4 | `replay_stress_limited_SU3_candidate_pending_I7_controls` | `false` |
| `dose_14_stronger_bounded` | `I4-A` | 3/4 | `replay_stress_limited_SU3_candidate_pending_I7_controls` | `false` |
| `single_route_b_reference` | `I4-B` | 3/4 | `replay_stress_limited_SU3_candidate_pending_I7_controls` | `false` |
| `complementary_split_route_b_adjacent` | `I4-B` | 3/4 | `replay_stress_limited_SU3_candidate_pending_I7_controls` | `true` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i5_passed` | `true` | accepted_replay_backed_su3_candidates_pending_i7_controls |
| `i5_su3_candidate_count` | `true` | ["n22_i5_row_i4_minimal_route_b", "n22_i5_row_dose_08_i4_reference", "n22_i5_row_dose_14_stronger_bounded", "n22_i5_row_single_route_b_re... |
| `stress_modes_declared_before_use` | `true` | ["baseline_post_snapshot_reentry", "delayed_idle_two_windows_reentry", "repeated_reentry_two_step", "mild_peer_flux_before_reentry"] |
| `artifact_manifest_non_empty` | `true` | 121 |
| `artifact_hashes_match` | `true` | 121 |
| `all_rows_have_four_stress_modes` | `true` | [{"i5a_consumable_role": "replay_stress_limited_SU3_candidate_pending_I7_controls", "narrow_margin_candidate": false, "passed_stress_mode... |
| `all_rows_pass_su3_preservation_stress_modes` | `true` | [{"i5a_consumable_role": "replay_stress_limited_SU3_candidate_pending_I7_controls", "narrow_margin_candidate": false, "passed_stress_mode... |
| `repeated_reentry_depletion_boundary_recorded` | `true` | [{"i5a_consumable_role": "replay_stress_limited_SU3_candidate_pending_I7_controls", "narrow_margin_candidate": false, "passed_stress_mode... |
| `narrow_complementary_stress_tracked` | `true` | [{"i5a_consumable_role": "replay_stress_limited_SU3_candidate_pending_I7_controls", "narrow_margin_candidate": false, "passed_stress_mode... |
| `no_rows_promote_to_su4` | `true` | [{"i5a_consumable_role": "replay_stress_limited_SU3_candidate_pending_I7_controls", "narrow_margin_candidate": false, "passed_stress_mode... |
| `all_claims_still_blocked` | `true` | [{"i5a_consumable_role": "replay_stress_limited_SU3_candidate_pending_I7_controls", "narrow_margin_candidate": false, "passed_stress_mode... |
| `unsafe_flags_all_false` | `true` | all stress rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |

## Claim Boundary

I5-A strengthens replay-backed SU3 evidence only for delayed and mild-peer-flux preservation. Repeated re-entry is a fail-closed depletion boundary. I5-A does not support durable SU4, transfer SU5, SU6, final N22, the N21 ND6 bridge, semantic learning, choice, agency, native support, sentience, Phase 8, or ant-ecology implementation.

I5-A does not run the full I7 control matrix and cannot assign SU4.
