# N17 Iteration 6-B - Alternative G5 Challenge Probe

Artifact: `n17_alternative_g5_challenge_probe`
Status: `passed`
Acceptance state: `accepted_alternative_target_band_g5_mvp_challenge_stability_no_final_ap7`
Output digest: `cecfc28625e871c4d7d12ba0a1904a9ef7866c2230206c1b033b316b9b2564ab`

## Main Result

Iteration 6-B tests an alternative G5 configuration. It is not a refinement of the 6-A breach/flux envelope and does not retune 6-A rows after failure. The alternative configuration gates challenge stability through the N15 generated target band, the N13 bounded response budget, N09 recovery-in-band context, and N15 replay cleanliness.

```text
current_evidence_rung = G5_alternative_target_band_challenge_stable_candidate
alternative_g5_configuration_supported = true
g5_support_scope = target_band_gated_mvp_perturbation_loop
full_comparative_ap7_classification_supported = false
final_ap7_supported = false
```

## Source Values

```text
target_center = 0.887594607287
target_band = [0.817594607287, 0.957594607287]
support_floor = 0.85
n13_bounded_response_amount = 0.120134817816
n09_recovery_in_band = true
n15_bounded_drift_replay_passed = true
```

## Rows

| Row | Challenge | Decision | Claim Allowed | Projected Later Support |
| --- | --- | --- | --- | --- |
| `n17_i6b_row_01_target_band_anchor_replay` | `target_band_anchor_replay` | `supported` | `true` | `0.887594607287` |
| `n17_i6b_row_02_mild_feedback_attenuation_target_band` | `mild_feedback_attenuation_target_band` | `supported` | `true` | `0.875581125505` |
| `n17_i6b_row_03_source_window_feedback_delay_target_band` | `source_window_feedback_delay_target_band` | `supported` | `true` | `0.870094607287` |
| `n17_i6b_row_04_compound_mild_attenuation_delay_target_band` | `compound_mild_attenuation_delay_target_band` | `supported` | `true` | `0.858081125505` |
| `n17_i6b_row_05_target_band_lower_bound_crossing_control` | `target_band_lower_bound_crossing_control` | `rejected` | `false` | `0.805594607287` |
| `n17_i6b_row_06_response_budget_exceeds_n13_control` | `response_budget_exceeds_n13_control` | `rejected` | `false` | `0.861594607287` |

## Interpretation

6-B is stronger than 6-A only in this bounded sense: mild feedback attenuation, a source-backed one-window feedback delay, and their compound case remain inside the generated target band and above the support floor. It still fails closed when projected support crosses below the target band or when the response demand exceeds the N13 bounded response budget.

This supports an alternative bounded G5 MVP configuration, not a general challenge-stable loop. It does not support final AP7, resource/support modulation, shared-medium reciprocal closure, agency, intention, semantic action/perception, selfhood, native support, organism/life, or fully native integration.

## Checks

- `source_i6_ap7_mvp_claim_clean`: pass
- `old_best_values_source_backed`: pass
- `alternative_not_i6a_retune`: pass
- `stronger_alternative_supported_rows_present`: pass
- `fail_closed_bounds_present`: pass
- `supported_rows_keep_trace_contract`: pass
- `mvp_family_only`: pass
- `unsafe_claim_flags_false`: pass
- `final_ap7_still_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
