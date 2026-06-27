# N24 Iteration 6-A - Alternative Replay And Control Matrix

Status: `passed`

Acceptance state: `accepted_i5a_replay_control_backed_ab4_candidate_pending_i7a`

Output digest: `6a57579a029dd7a5c08bb995e3c455dc44db556f96201dd88db53c78d14169e3`

## Summary

Iteration 6-A replays and controls the I5-A high-margin optionality variant.
It does not replace the original I6 result.

```text
artifact_replay = passed
snapshot_load_replay = passed
duplicate_replay = passed
optional_set_survival_replay = passed
final_consumable_rung = AB4
ab4_candidate_supported = true
ready_for_iteration_7a_stress_threshold_matrix = true
```

## Interpretation

I6-A confirms the high-margin I5-A optional set survives artifact, snapshot/load, duplicate, and optional-set replay under the same control discipline as I6.

This is an alternative AB4 candidate only. It does not replace I6 and does not open AB5, reward, semantic choice, agency, native support, sentience, Phase 8, or ant ecology.

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_passed` | `true` |
| `i4_surplus_probe_passed` | `true` |
| `i5a_alternative_probe_ready` | `true` |
| `original_i6_i7_preserved` | `true` |
| `i5a_replay_modes_passed` | `true` |
| `i5a_controls_accept_candidate` | `true` |
| `i5a_ab4_candidate_supported` | `true` |
| `artifact_manifest_non_empty_and_sha_match` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `no_absolute_paths` | `true` |
