# N07 Iteration 9-C Short-Window Artifact Replay Closeout

Status: `passed`

9-C replays the short-window N07 evidence chain from artifacts only. It keeps
Iteration 9-B as one-window C3/T7 compatibility evidence and carries Iteration
9-B2 forward as a prolonged-stress blocker. This is not persistent C3
compatibility and not ID6.

## Closeout

- derived ceiling: `ID5`
- artifact replay gate: `pass`
- compatibility gate: `blocked`
- one-window compatibility: `pass`
- prolonged compatibility: `blocked`
- primary blocker: `wrong_basin`
- ID6 claimed: `False`
- next iteration: `10_long_horizon_compatibility_design`

## Prolonged Stress Boundary

- stress model: `n07_c3_repeated_window_no_recovery_accumulation_v1`
- stress windows: `12`
- dynamic LGRC steps: `0`
- first failure: `{'A_cumulative_support_retention': 0.8637481156814181, 'B_cumulative_support_retention': 0.8801359953694519, 'cumulative_destructive_interference_score': 0.13625188431858193, 'cumulative_wrong_basin_leakage_score': 0.12, 'primary_blockers': ['wrong_basin'], 'stress_window': 3}`

## Replayed Controls

| Control | Status | Primary Blocker | Ceiling | Source |
|---|---|---|---|---|
| `destructive_interference` | `blocked` | `destructive_interference` | `ID5` | `iteration_9b` |
| `ambiguous_overlap` | `blocked` | `ambiguous_overlap` | `ID5` | `iteration_9b` |
| `wrong_basin` | `blocked` | `wrong_basin` | `ID5` | `iteration_9b` |
| `hidden_support_field` | `blocked` | `hidden_support_field` | `ID5` | `iteration_9b` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID5` | `iteration_9b` |
| `support_drift_beyond_threshold` | `blocked` | `support_drift_beyond_threshold` | `ID5` | `iteration_9b` |
| `prolonged_compatibility_stress` | `blocked` | `wrong_basin` | `ID5` | `iteration_9b2` |

## Checks

| Check | Passed |
|---|---|
| `A_support_digest_replayed` | `True` |
| `B_support_digest_replayed` | `True` |
| `acceptance_matches_closeout` | `True` |
| `all_source_artifacts_passed` | `True` |
| `artifact_only` | `True` |
| `artifact_replay_gate_pass` | `True` |
| `claim_flags_false` | `True` |
| `closeout_boundary_rung_allowed` | `True` |
| `closeout_ceiling_id5` | `True` |
| `closeout_claim_flags_false` | `True` |
| `closeout_digest_recomputed` | `True` |
| `closeout_does_not_claim_id6` | `True` |
| `closeout_implementation_surface_allowed` | `True` |
| `closeout_records_wrong_basin_blocker` | `True` |
| `closeout_required_fields_present` | `True` |
| `closeout_runtime_family_allowed` | `True` |
| `compatibility_gate_blocked` | `True` |
| `compatibility_record_digest_replayed` | `True` |
| `control_ceilings_source_specific` | `True` |
| `control_digests_replayed` | `True` |
| `metric_digests_replayed` | `True` |
| `next_iteration_is_10` | `True` |
| `no_src_changes_required` | `True` |
| `one_window_compatibility_passed` | `True` |
| `private_runtime_state_not_used` | `True` |
| `prolonged_stress_blocked` | `True` |
| `prolonged_stress_digest_replayed` | `True` |
| `prolonged_stress_primary_blocker_wrong_basin` | `True` |
| `runtime_state_not_used` | `True` |
| `semantic_consistency_passed` | `True` |
| `single_basin_ceiling_id5` | `True` |
| `source_artifact_hashes_present` | `True` |
| `status_passed` | `True` |
| `visuals_not_evidence` | `True` |

## Artifact Digests

```json
{
  "artifact_replay_chain_digest": "244cee3b4fab86d9b2db6b9ee86cc6f7ab9266c4e47991cc158fd40274b1ba2b",
  "checks_digest": "bedf8431fbfafb7be1eca0fa31df5aa960134e4b66ce71282f18a3ade080c914",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "closeout_row_artifact_digest": "a055750c8f5c9d074474c459b17fdba554d435c5b07eb9a4675e631bc57605f0",
  "closeout_row_digest": "94e9b7919dd0c3bee91898b0812a40ae5e7712d2a82b97a88caeaf6bdfe18707",
  "source_artifacts_digest": "7f6c068829b1e286f062e6ea698403d311fdca091a4175a782f54329b78ab133"
}
```

## Acceptance

Iteration 9-C replays the N07 short-window evidence chain through 9-B2 from artifacts only. It records 9-B as one-window compatibility evidence, records 9-B2 as prolonged-stress failure, freezes the ceiling at ID5, and does not claim ID6 or identity acceptance.
