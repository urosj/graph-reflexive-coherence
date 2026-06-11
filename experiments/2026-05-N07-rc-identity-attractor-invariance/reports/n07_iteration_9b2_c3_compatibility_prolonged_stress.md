# N07 Iteration 9-B2 C3 Compatibility Prolonged Stress

Status: `passed`

Iteration 9-B2 is a negative prolonged-stress result. The 9-B one-window compatibility pass does not justify multi-window C3 stability when the observed wrong-basin leakage and support loss are allowed to recur without a recovery mechanism.

This is not a native LGRC dynamic simulation. It is an experiment-local
repeated-window stress model over the source-backed 9-B metrics.

## Result

- stress windows: `12`
- native LGRC dynamic steps: `0`
- stress passed all windows: `False`
- first failure window: `3`
- first failure blockers: `['wrong_basin']`
- derived ceiling: `ID5`
- ID6 claimed: `False`

## Interpretation

What it shows:

- The 4% one-window wrong-basin leakage is not negligible under a repeated-window no-recovery stress model.
- The first compatibility failure occurs before the 12-window stress horizon completes.
- 9-B should be treated as one-window compatibility evidence, not as persistent A/B compatibility.

Needed next:

Either record 9-C as a closeout of one-window compatibility plus a prolonged-stress blocker, or design a recovery/re-separation probe that can keep wrong-basin leakage and support drift bounded across repeated windows.

Claim boundary:

This stress result does not emit identity acceptance, RC identity collapse, semantic choice, agency, biological identity, personhood, movement, or unrestricted identity claims.

## Stress Windows

| Window | A Retention | B Retention | Cumulative Wrong-Basin Leakage | Cumulative Destructive Score | Passed | Blockers |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.952348 | 0.958333 | 0.040000 | 0.047652 | `True` | `` |
| 2 | 0.906967 | 0.918403 | 0.080000 | 0.093033 | `True` | `` |
| 3 | 0.863748 | 0.880136 | 0.120000 | 0.136252 | `False` | `wrong_basin` |
| 4 | 0.822589 | 0.843464 | 0.160000 | 0.177411 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 5 | 0.783391 | 0.808319 | 0.200000 | 0.216609 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 6 | 0.746061 | 0.774639 | 0.240000 | 0.253939 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 7 | 0.710510 | 0.742363 | 0.280000 | 0.289490 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 8 | 0.676652 | 0.711431 | 0.320000 | 0.323348 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 9 | 0.644409 | 0.681788 | 0.360000 | 0.355591 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 10 | 0.613701 | 0.653380 | 0.400000 | 0.386299 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 11 | 0.584457 | 0.626156 | 0.440000 | 0.415543 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |
| 12 | 0.556607 | 0.600066 | 0.480000 | 0.443393 | `False` | `destructive_interference,support_drift_beyond_threshold,wrong_basin` |

## Checks

| Check | Passed |
|---|---|
| `budget_error_zero_all_windows` | `True` |
| `claim_flags_false` | `True` |
| `compatibility_stress_blocked` | `True` |
| `cumulative_wrong_basin_exceeds_threshold_at_failure` | `True` |
| `first_failure_is_wrong_basin` | `True` |
| `first_failure_recorded` | `True` |
| `next_iteration_is_9c` | `True` |
| `no_src_changes_required` | `True` |
| `source_9b_dynamic_lgrc_steps_zero` | `True` |
| `source_9b_passed` | `True` |
| `source_9b_was_one_window` | `True` |
| `source_artifact_hashes_present` | `True` |
| `status_passed` | `True` |
| `stress_candidate_ceiling_id5` | `True` |
| `stress_does_not_claim_id6` | `True` |
| `stress_model_not_native_lgrc_dynamics` | `True` |
| `stress_window_count_gt_one` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "ad4276fe245becb091f78146c0c1f154838724654e582f2dcb96f57a1fa08bf9",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "interpretation_digest": "312b3210fdd8c82b8823dc10c3c796af1bb5a978c71f801d5b3a484f880095ee",
  "stress_candidate_row_digest": "7a94a8c02013af380445a45ee28f49673caf45e91aa6daef21073784dab2c2ac",
  "stress_model_digest": "874e983bb9bb1054ea523fb7938cd4b1c6a68932e258561fdb345199bb3837c3"
}
```

## Acceptance

Iteration 9-B2 passes if it explicitly tests prolonged compatibility under a serialized stress model, records whether the 9-B leakage/support-loss boundary remains stable, and does not promote ID6 or identity claims.

Achieved: `True`
