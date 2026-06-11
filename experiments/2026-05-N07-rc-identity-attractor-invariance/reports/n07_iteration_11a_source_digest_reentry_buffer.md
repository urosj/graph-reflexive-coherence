# N07 Iteration 11-A Source-Digest Reentry Buffer

Status: `passed`

11-A uses the lesson from 11-0 as its introduction:

```text
Can source_digest_reentry_buffer_v1 convert the 11-0 trajectory from
unbounded_degrading_without_recovery into bounded-flat, bounded-improving,
or oscillatory-recovering compatibility?
```

The answer is partial. The buffer changes the expressed regime from
`unbounded_degrading_without_recovery` to `bounded_degrading`.
The 12-window endpoint passes, but the trend still degrades, so this does not
close long-term C3 compatibility.

## Arc-of-Becoming Interpretation

- expressed property:
  `Serialized source-digest reentry expresses partial recovery: it bounds the 12-window endpoint while preserving a degrading trend.`
- classification:
  `reusable_partial_recovery_class`
- trajectory regime:
  `bounded_degrading`
- endpoint status:
  `passed_12_window_horizon`
- not merely passed endpoint:
  `True`
- naturalization rung:
  `Nat2_regime_assisted_expression`
- recovery mechanism observed:
  `True`
- self-regenerated support observed:
  `False`

Observations:

| Observation | Metric | Change | Interpretation |
|---|---|---|---|
| `unresolved_leakage_slope_reduced` | `wrong_basin_leakage_level` | `positive_slope_reduced` | The buffer reduces unresolved leakage from the 11-0 baseline, but does not flatten it. |
| `endpoint_survives_horizon` | `endpoint_pass_status` | `blocked_to_passed_12_window_horizon` | The fixed 12-window endpoint passes under this policy. |
| `support_retention_still_degrades` | `A_and_B_support_retention_level` | `negative_slope_reduced` | Support decay is reduced enough to remain inside the horizon threshold, but it still trends downward. |
| `budget_exactness_preserved` | `budget_error_level` | `zero_slope` | The improvement is not caused by mass creation or budget discontinuity. |

Cultivation next question:

Can neutral_absorber_reservoir_v1 convert bounded-degrading source-digest reentry into bounded-flat or recovering long-horizon compatibility?

Naturalization note:

The branch uses a serialized experiment-local reentry policy. It is regime-assisted recovery, not endogenous native formation of the recovery precondition.

## Reentry Policy

- policy: `source_digest_reentry_buffer_v1`
- capture fraction: `0.8`
- minimum capture fraction from contract:
  `0.7916666666666667`
- hidden routing allowed:
  `False`
- native support status:
  `not_native_lgrc_policy`

## Result

- branch: `11-A`
- endpoint status: `passed_12_window_horizon`
- first failure window: `None`
- primary blocker: `bounded_degrading_trend`
- trajectory regime: `bounded_degrading`
- derived ceiling: `ID5`
- ID6 claimed: `False`
- series ready for Iteration 12: `False`
- next branch: `11-B_neutral_absorber_reservoir`

## Baseline Comparison

- 11-0 trajectory: `unbounded_degrading_without_recovery`
- 11-0 wrong-basin slope:
  `0.04`
- 11-A wrong-basin slope:
  `0.007999999999999998`
- wrong-basin slope reduction:
  `0.032`
- 11-0 A support slope:
  `-0.03597648527676473`
- 11-A A support slope:
  `-0.009002364041475657`
- 11-0 destructive-interference slope:
  `0.03597648527676473`
- 11-A destructive-interference slope:
  `0.009002364041475657`

## Trend Slopes

- wrong-basin leakage slope/window:
  `0.007999999999999998`
- A support-retention slope/window:
  `-0.009002364041475657`
- B support-retention slope/window:
  `-0.007928026592438813`
- destructive-interference slope/window:
  `0.009002364041475657`
- budget-error slope/window:
  `0.0`

## Windows

| Window | A Retention | B Retention | Wrong-Basin Leakage | Destructive Interference | Passed | Blockers |
|---:|---:|---:|---:|---:|---|---|
| 1 | 0.990470 | 0.991667 | 0.008000 | 0.009530 | `True` | `` |
| 2 | 0.981030 | 0.983403 | 0.016000 | 0.018970 | `True` | `` |
| 3 | 0.971680 | 0.975208 | 0.024000 | 0.028320 | `True` | `` |
| 4 | 0.962420 | 0.967081 | 0.032000 | 0.037580 | `True` | `` |
| 5 | 0.953248 | 0.959022 | 0.040000 | 0.046752 | `True` | `` |
| 6 | 0.944163 | 0.951030 | 0.048000 | 0.055837 | `True` | `` |
| 7 | 0.935165 | 0.943105 | 0.056000 | 0.064835 | `True` | `` |
| 8 | 0.926252 | 0.935246 | 0.064000 | 0.073748 | `True` | `` |
| 9 | 0.917425 | 0.927452 | 0.072000 | 0.082575 | `True` | `` |
| 10 | 0.908681 | 0.919723 | 0.080000 | 0.091319 | `True` | `` |
| 11 | 0.900021 | 0.912059 | 0.088000 | 0.099979 | `True` | `` |
| 12 | 0.891444 | 0.904458 | 0.096000 | 0.108556 | `True` | `` |

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
| `baseline_no_recovery_would_degrade` | `blocked` | `wrong_basin` | `True` | Keep the 11-0 source failure visible as the baseline. |
| `capture_fraction_below_contract` | `blocked` | `wrong_basin_slope_unbounded` | `True` | Reject a reentry buffer that cannot meet the frozen leakage budget. |
| `source_digest_scrambled` | `blocked` | `wrong_support_area` | `True` | Reject reentry credited to the wrong basin digest. |
| `hidden_reentry_preference` | `blocked` | `hidden_support_field` | `True` | Reject fixture-side or report-side route preference. |
| `budget_discontinuity_after_reentry` | `blocked` | `budget_discontinuity` | `True` | Reject recovery by mass creation or silent normalization. |
| `endpoint_only_promotion` | `blocked` | `bounded_degrading_trend` | `True` | Reject ID6 promotion from endpoint pass alone. |
| `identity_claim_promotion` | `blocked` | `identity_claim_promotion` | `True` | Reject identity-acceptance or RC-collapse claims. |

## Checks

| Check | Passed |
|---|---|
| `all_window_records_have_required_reentry_chain` | `True` |
| `arc_endpoint_not_enough` | `True` |
| `arc_interpretation_present` | `True` |
| `arc_naturalization_regime_assisted` | `True` |
| `arc_partial_recovery_classified` | `True` |
| `branch_id_is_11a` | `True` |
| `budget_error_zero_all_windows` | `True` |
| `candidate_ceiling_id5` | `True` |
| `candidate_claim_flags_false` | `True` |
| `candidate_no_id6` | `True` |
| `capture_fraction_meets_contract` | `True` |
| `claim_flags_false` | `True` |
| `control_blockers_distinct` | `True` |
| `controls_passed` | `True` |
| `controls_present` | `True` |
| `destructive_slope_reduced_but_positive` | `True` |
| `endpoint_passes_12_window_horizon` | `True` |
| `hidden_routing_disallowed` | `True` |
| `intro_question_recorded` | `True` |
| `next_branch_is_11b` | `True` |
| `no_src_changes_required` | `True` |
| `series_not_ready_for_iteration_12` | `True` |
| `source_10_passed` | `True` |
| `source_11_0_passed` | `True` |
| `source_7b_passed` | `True` |
| `source_9b_passed` | `True` |
| `source_artifact_hashes_present` | `True` |
| `status_passed` | `True` |
| `support_slopes_improved_but_negative` | `True` |
| `trajectory_regime_bounded_degrading` | `True` |
| `wrong_basin_slope_reduced` | `True` |
| `wrong_basin_slope_within_contract` | `True` |

## Artifact Digests

```json
{
  "arc_interpretation_digest": "dbc5e47f329a03559cb09ee3c0dfa6879e919ca8d2afa8f2fb5bec423a64c1d8",
  "branch_record_digest": "7e42262b015200b7fb0c49bc029f5e910dd15752046b1adccc1ea33be5acdf95",
  "candidate_row_digest": "b3a50d87d55bdac6cf778e283874116c7938e74cbb55bcab52911f9124626988",
  "checks_digest": "300d217f18d4b78f5ce08ff4f3803947e41a7345e132fa2dfcd395ca893de791",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "4c72ef02e3c19a492a13cc676e6710803d927b32823f6b59f0989590d0b50be0",
  "reentry_policy_digest": "276db7febae6ba4880ba8db37ea99abcd99eae58de378c35fb803be58622bdaa",
  "reentry_window_records_digest": "4133812cd6a5dec3b3e68d4d9c8e9388a93cc68e77893aadda39265f780871e5",
  "series_decision_digest": "d706153f561b1844d82c0e5de7642cfdb2c52fcbbd65efe27873c155f0d9a2db",
  "trajectory_digest": "9e8265bc4ed9c506e3e5adebecf553bfc0248f2042feb63a1c37680390c9be66"
}
```

## Acceptance

Iteration 11-A passes if it records whether source_digest_reentry_buffer_v1 changes the 11-0 trajectory class, emits the reentry chain records, preserves budget exactness and claim boundaries, and records the next 11-* question.

Achieved: `True`
