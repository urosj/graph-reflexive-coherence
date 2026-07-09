# N30 Iteration 6-A - Later Eligibility Contrast-Margin Probe

Status: `passed`

Acceptance state:
`accepted_M2_dependency_contrast_margin_strengthening_no_threshold_margin_upgrade`

Output digest: `145d5bf2acda7b049df43c5c9b5742fb33920e0dfc11d955cd795b5620cecad7`

## Scope

I6-A strengthens I6 by measuring counterfactual contrast margin. It does not
change N28 thresholds and does not reinterpret the narrow I6 threshold margin.

The question is narrower:

```text
Is the provisional M2 dependency clearly separated from neutral-gap and
opposite-regime counterfactuals?
```

## Result

```text
medium_relation_ladder_rung = M2_candidate_pending_I7_controls
source_i6_threshold_margin = 0.002
higher_threshold_margin_supported = false
dependency_contrast_margin_supported = true
minimum_dependency_contrast_margin_vs_neutral = 0.042
minimum_dependency_contrast_margin_vs_extractive = 0.044
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
```

## Candidate Rows

- n30_i6_row_01_i5_single_shell_later_eligibility_candidate: threshold_margin=0.002, contrast_vs_neutral=0.042, contrast_vs_extractive=0.044
- n30_i6_row_02_i5a_split_shell_later_eligibility_candidate: threshold_margin=0.002, contrast_vs_neutral=0.042, contrast_vs_extractive=0.044

## Interpretation

I6 was narrow at the N28 generative-threshold boundary: its minimum threshold
margin was 0.002. I6-A does not hide that. Instead, it asks whether the same
later-eligibility dependency is well separated from the active counterfactuals.

The answer is yes. Against the neutral-gap counterfactual, the minimum
axis-level dependency contrast margin is
0.042. Against the
extractive-cross counterfactual, it is
0.044. This strengthens
the M2 dependency separation while preserving the claim boundary: the threshold
margin remains narrow and final C5/C6 remain pending I7 controls.

## Artifacts

| Role | Path |
|---|---|
| i6a_contrast_threshold_policy | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_margin_i6a_artifacts/i6a_contrast_threshold_policy.json` |
| i6a_contrast_margin_matrix | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_margin_i6a_artifacts/i6a_contrast_margin_matrix.json` |
| i6a_claim_boundary_guard | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_later_eligibility_margin_i6a_artifacts/i6a_claim_boundary_guard.json` |

## Checks

- source_i6_passed_with_provisional_m2: true
- contrast_policy_declared_without_threshold_retune: true
- dependency_contrast_margins_supported: true
- higher_threshold_margin_not_overclaimed: true
- final_c5_c6_claims_blocked_pending_i7: true
- artifact_manifest_sha256_matches: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true
