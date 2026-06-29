# N28 Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

## Summary

- Status: `passed`
- Acceptance state: `accepted_ge5_controls_ap_claim_classification_pending_i8_closeout`
- Output digest: `13271b6c1e5e67f89fdabf77722aba648654094250cd1bf8c60d361c95560e35`
- Provisional GE rung: `GE5`
- GE6 supported: `false`
- Final N28 supported: `false`

I7 consumes existing evidence only. It classifies the broad I6 GE5 matrix,
the I6-A same-policy transition surface, the I6-B margin diagnostic, and
the I6-C focused current-multiplier margin tranche without opening new
source-current regime rows.

## Evidence Roles

| Evidence | Source | Status | Scope |
|---|---|---|---|
| `primary_paired_regime_ge5_matrix` | `6` | `supported` | `broad_paired_regime_GE5_matrix` |
| `boundary_transition_policy_evidence` | `6-A` | `supported` | `same_policy_transition_surface` |
| `margin_envelope_diagnostic_evidence` | `6-B` | `diagnostic_supported` | `margin_envelope_characterization` |
| `focused_current_multiplier_margin_evidence` | `6-C` | `focused_GE5_supported` | `focused_current_multiplier_competitive_neutral_margin_support` |

## Classification Rows

| Row | Source | Regime | Role | Decision | Rung |
|---|---|---|---|---|---|
| `n28_i7_n28_i4_row_primary_generative_candidate_classification` | `4` | `generative` | `positive_generative_candidate` | `supported` | `GE5` |
| `n28_i7_n28_i4a_row_generative_strengthening_candidate_classification` | `4-A` | `generative` | `positive_generative_candidate` | `supported` | `GE5` |
| `n28_i7_n28_i4a2_row_generative_mechanism_diversity_candidate_classification` | `4-A2` | `generative` | `positive_generative_candidate` | `supported` | `GE5` |
| `n28_i7_n28_i4b_row_primary_extractive_contrast_classification` | `4-B` | `extractive` | `extractive_measured_contrast` | `supported` | `GE5` |
| `n28_i7_n28_i4c_row_extractive_strengthening_contrast_classification` | `4-C` | `extractive` | `extractive_measured_contrast` | `supported` | `GE5` |
| `n28_i7_n28_i4c2_row_extractive_mechanism_diversity_contrast_classification` | `4-C2` | `extractive` | `extractive_measured_contrast` | `supported` | `GE5` |
| `n28_i7_n28_i4d_row_primary_competitive_neutral_contrast_classification` | `4-D` | `competitive` | `competitive_neutral_measured_contrast` | `supported` | `GE5` |
| `n28_i7_n28_i4e_row_competitive_neutral_mechanism_diversity_contrast_classification` | `4-E` | `neutral` | `competitive_neutral_measured_contrast` | `supported` | `GE5` |
| `n28_i7_n28_i4f_row_higher_margin_neutral_circulation_contrast_classification` | `4-F` | `neutral` | `competitive_neutral_measured_contrast` | `supported` | `GE5` |
| `n28_i7_n28_i4g_row_higher_margin_competitive_redistribution_contrast_classification` | `4-G` | `competitive` | `competitive_neutral_measured_contrast` | `supported` | `GE5` |

## Interpretation

I7 supports a GE5 bounded artifact-level regime-separation candidate,
not final N28. The strongest evidence remains the broad paired-regime
I6 matrix: three generative rows, three extractive contrasts, and two
competitive/neutral contrasts survive replay/control/stress under one
shared policy family.

I6-A supports the same-policy transition surface. I6-B is diagnostic
only and does not add new GE support. I6-C adds focused
current-multiplier margin support for competitive/neutral transition
rows, but it is not broad robustness and not GE6.

AP4/AP5 NAT4 gaps remain unresolved, N27 transfer context is not
promoted to N28 evidence, and semantic cooperation, agency, native
support, Phase 8 completion, and ant ecology remain blocked.

## Checks

| Check | Passed |
|---|---|
| `all_source_digests_match_expected` | `true` |
| `all_positive_and_contrast_rows_classified` | `true` |
| `all_probe_source_digests_match_expected` | `true` |
| `primary_and_strengthening_generative_candidates_represented` | `true` |
| `primary_and_strengthening_extractive_contrasts_represented` | `true` |
| `competitive_neutral_contrasts_and_focused_rows_represented` | `true` |
| `shared_regime_policy_supported` | `true` |
| `label_specific_thresholds_absent_or_blocked` | `true` |
| `competitive_neutral_not_promoted_to_generative` | `true` |
| `extractive_not_promoted_to_generative` | `true` |
| `ap4_ap5_dependencies_row_local_and_unresolved` | `true` |
| `n27_context_not_promoted_to_n28_evidence` | `true` |
| `control_families_fail_closed_without_positive_evidence` | `true` |
| `focused_margin_support_is_not_broad_robustness` | `true` |
| `ge5_supported_ge6_final_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
