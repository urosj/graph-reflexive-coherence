# N07 Iteration 11-B Neutral Absorber Reservoir

Status: `passed`

## Intro: C3 Question Redirection

11-B changes the interpretation target for the 11-* series:

```text
For connected basins, no-leakage is not the natural C3 target. The better
question is whether leakage becomes bounded, non-destructive exchange that
does not erase either basin.
```

The 11-A result is therefore reinterpreted as incomplete not because leakage
existed, but because support, leakage, and destructive-interference trends
still degraded. 11-B asks:

```text
Can neutral_absorber_reservoir_v1 turn connected-basin leakage into bounded
non-destructive exchange while both basins remain separable attractors?
```

The proposed success regime is:

```text
bounded_non_destructive_exchange
bounded_flat_leakage_after_transient
dual_basin_survival_with_exchange
```

## Arc-of-Becoming Interpretation

- expressed property:
  `Connected dual basins can express bounded non-destructive exchange when shared-U flux is absorbed through a neutral reservoir rather than immediately credited as competitor support.`
- classification:
  `reusable_dual_basin_exchange_class`
- trajectory regime:
  `bounded_non_destructive_exchange`
- endpoint status:
  `passed_12_window_horizon`
- zero leakage required:
  `False`
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
| `leakage_allowed_not_zero` | `wrong_basin_leakage_level` | `nonzero_bounded_exchange` | The successful condition is not zero leakage; it is bounded exchange below the destructive threshold. |
| `post_transient_flattening` | `wrong_basin_leakage_level` | `positive_slope_to_near_flat_post_transient` | Leakage approaches a plateau after the transient instead of accumulating linearly. |
| `dual_basin_survival` | `A_and_B_support_retention_level` | `both_basin_supports_preserved` | Both support areas remain above the survival threshold despite shared-U exchange. |
| `separability_preserved` | `basin_separability_level` | `distinct_attractors_remain_distinguishable` | The basins do not collapse into a single smeared support area under the reservoir policy. |
| `budget_exactness_preserved` | `budget_error_level` | `zero_slope` | The exchange class is not created by hidden mass normalization or budget drift. |

Cultivation next question:

Can Iteration 12 replay the 11-* branch inventory from artifacts only and freeze bounded non-destructive exchange as the current long-horizon C3 class?

Naturalization note:

The reservoir is a serialized experiment-local geometry policy. It demonstrates a reusable stability regime, but not yet endogenous native formation of the absorber.

## Reservoir Policy

- policy: `neutral_absorber_reservoir_v1`
- zero leakage required: `False`
- allowed exchange mode: `bounded_non_destructive_exchange`
- exchange cap: `0.075`
- reservoir settling factor: `0.65`
- neutral absorption fraction: `0.85`
- hidden routing allowed:
  `False`
- native support status:
  `not_native_lgrc_policy`

## Result

- branch: `11-B`
- endpoint status: `passed_12_window_horizon`
- first failure window: `None`
- primary blocker: `artifact_replay_pending_iteration_12`
- trajectory regime: `bounded_non_destructive_exchange`
- non-destructive exchange passed:
  `True`
- derived ceiling: `ID5`
- ID6 claimed: `False`
- series ready for Iteration 12: `True`
- next branch: `12_long_horizon_artifact_replay_and_compatibility_closeout`

## Baseline Comparison

- 11-0 trajectory: `unbounded_degrading_without_recovery`
- 11-A trajectory: `bounded_degrading`
- 11-A wrong-basin slope:
  `0.007999999999999998`
- 11-B wrong-basin slope:
  `0.00439303630184246`
- 11-B wrong-basin post-transient slope:
  `0.0008716360195236764`
- wrong-basin slope reduction vs 11-A:
  `0.003606963698157538`
- 11-A final wrong-basin leakage:
  `0.09599999999999997`
- 11-B final wrong-basin leakage:
  `0.07457339932026706`
- 11-A final A support retention:
  `0.8914436088034363`
- 11-B final A support retention:
  `0.9731535762447039`
- 11-A final destructive interference:
  `0.10855639119656368`
- 11-B final destructive interference:
  `0.02684642375529611`

## Trend Slopes

- wrong-basin leakage slope/window:
  `0.00439303630184246`
- wrong-basin leakage post-transient slope/window:
  `0.0008716360195236764`
- A support-retention slope/window:
  `-0.0015814930686632866`
- B support-retention slope/window:
  `-0.001449701979608011`
- destructive-interference slope/window:
  `0.0015814930686632866`
- destructive-interference post-transient slope/window:
  `0.00031378896702851283`
- basin-separability slope/window:
  `-0.0015814930686632866`
- budget-error slope/window:
  `0.0`

## Windows

| Window | A Retention | B Retention | Wrong-Basin Exchange | Destructive Interference | Separability | Passed | Blockers |
|---:|---:|---:|---:|---:|---:|---|---|
| 1 | 0.990550 | 0.991337 | 0.026250 | 0.009450 | 0.990550 | `True` | `` |
| 2 | 0.984407 | 0.985707 | 0.043312 | 0.015593 | 0.984407 | `True` | `` |
| 3 | 0.980415 | 0.982047 | 0.054403 | 0.019585 | 0.980415 | `True` | `` |
| 4 | 0.977820 | 0.979668 | 0.061612 | 0.022180 | 0.977820 | `True` | `` |
| 5 | 0.976133 | 0.978122 | 0.066298 | 0.023867 | 0.976133 | `True` | `` |
| 6 | 0.975036 | 0.977117 | 0.069344 | 0.024964 | 0.975036 | `True` | `` |
| 7 | 0.974324 | 0.976463 | 0.071323 | 0.025676 | 0.974324 | `True` | `` |
| 8 | 0.973860 | 0.976039 | 0.072610 | 0.026140 | 0.973860 | `True` | `` |
| 9 | 0.973559 | 0.975763 | 0.073447 | 0.026441 | 0.973559 | `True` | `` |
| 10 | 0.973363 | 0.975583 | 0.073990 | 0.026637 | 0.973363 | `True` | `` |
| 11 | 0.973236 | 0.975467 | 0.074344 | 0.026764 | 0.973236 | `True` | `` |
| 12 | 0.973154 | 0.975391 | 0.074573 | 0.026846 | 0.973154 | `True` | `` |

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
| `baseline_no_recovery_would_degrade` | `blocked` | `wrong_basin` | `True` | Keep the 11-0 source failure visible as the baseline. |
| `zero_leakage_requirement_misframed` | `blocked` | `misframed_zero_leakage_requirement` | `True` | Reject interpreting C3 as sealed connected basins. |
| `reservoir_absorption_missing` | `blocked` | `reservoir_absorption_missing` | `True` | Reject shared-U exchange without neutral absorption. |
| `hidden_reservoir_routing` | `blocked` | `hidden_support_field` | `True` | Reject fixture-side or report-side basin preference. |
| `asymmetric_absorber_preference` | `blocked` | `asymmetric_exchange_preference` | `True` | Reject unrecorded A/B preference in the absorber. |
| `over_isolated_fixture` | `blocked` | `disconnected_basin_trivialization` | `True` | Reject proving compatibility by disconnecting the basins. |
| `budget_discontinuity_after_absorption` | `blocked` | `budget_discontinuity` | `True` | Reject reservoir success by mass creation or normalization. |
| `support_destroyed_by_allowed_exchange` | `blocked` | `support_drift_beyond_threshold` | `True` | Reject leakage that stays bounded by destroying support. |
| `identity_claim_promotion` | `blocked` | `identity_claim_promotion` | `True` | Reject ID6 or identity-acceptance wording before replay. |

## Checks

| Check | Passed |
|---|---|
| `all_window_records_have_required_reservoir_chain` | `True` |
| `arc_dual_basin_exchange_classified` | `True` |
| `arc_interpretation_present` | `True` |
| `arc_zero_leakage_reframed` | `True` |
| `branch_id_is_11b` | `True` |
| `budget_error_zero_all_windows` | `True` |
| `candidate_ceiling_id5` | `True` |
| `candidate_claim_flags_false` | `True` |
| `candidate_no_id6` | `True` |
| `claim_flags_false` | `True` |
| `control_blockers_distinct` | `True` |
| `controls_passed` | `True` |
| `controls_present` | `True` |
| `dual_basin_support_survives` | `True` |
| `endpoint_passes_12_window_horizon` | `True` |
| `hidden_routing_disallowed` | `True` |
| `intro_reinterpretation_recorded` | `True` |
| `leakage_bounded_below_threshold` | `True` |
| `next_branch_is_iteration_12` | `True` |
| `no_src_changes_required` | `True` |
| `nonzero_leakage_observed` | `True` |
| `post_transient_destructive_flattened` | `True` |
| `post_transient_wrong_basin_flattened` | `True` |
| `separability_preserved` | `True` |
| `series_ready_for_iteration_12` | `True` |
| `source_10_passed` | `True` |
| `source_11_0_passed` | `True` |
| `source_11a_passed` | `True` |
| `source_7b_passed` | `True` |
| `source_9b_passed` | `True` |
| `source_artifact_hashes_present` | `True` |
| `status_passed` | `True` |
| `trajectory_regime_bounded_non_destructive_exchange` | `True` |
| `wrong_basin_slope_reduced_vs_11a` | `True` |
| `zero_leakage_not_required` | `True` |

## Artifact Digests

```json
{
  "arc_interpretation_digest": "f63a51fcc275931cf32f2782eee0da2fbd175d0e073178a51c47ed3ae583d2bc",
  "branch_record_digest": "9ed01471f34bb5b30d35feb5e1c4aedcfffd41e15147ec3b4fda72fcb3df28d7",
  "candidate_row_digest": "44bd5935324e40451d45dabaf447b66d98d39c0f8ce4bfcf0b6a4ae28fb5073c",
  "checks_digest": "c383e421e080e3c4e37797d8ab915e3fb38bcc979340a1e0799b38a439e03b77",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "61b176d272f5df54e89d629f55d2f904493d3143a3c48d903908167ead5672b8",
  "reservoir_policy_digest": "96cccc73ae57591eb4688e0b54656eeddd23afa7ab2445f6844e2aa527555516",
  "reservoir_window_records_digest": "db073ea88df88f44657f0f42c24eb95ba19a8f0f5735a85eba400d9da8c649e1",
  "series_decision_digest": "6b697eca48d059859558f802d677de52bf3ea16dfad5b6d41814f802921299c1",
  "trajectory_digest": "48f6bf4a8f15332f4212023715dfdf801c02107e48984a76ff642c02414a0aa9"
}
```

## Acceptance

Iteration 11-B passes if it records the C3 question redirection, tests neutral_absorber_reservoir_v1 as a bounded non-destructive exchange mechanism, preserves both basin supports and separability under nonzero leakage, keeps budget exact, records controls, and preserves claim boundaries.

Achieved: `True`
