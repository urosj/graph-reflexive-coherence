# N30 Iteration 6-C - Alternative Contrast / Margin Audit

Status: `passed`

Acceptance state: `accepted_alternative_source_margin_and_mechanism_contrast_audit_no_final_C5`

Output digest: `bb4930b3423156f4aac9b023cb14efb3c7bc8d707518395b2b95fe79fd39a403`

## Interpretation

I6-C compares the alternative I6-B source family with the original I6 edge case. It supports a fivefold threshold-margin improvement and a mechanism contrast, but still blocks final C5 pending I7.

## Margin Semantics

The `5.0` ratio compares raw gate headroom only:

```text
original I6 edge threshold margin = 0.002
alternative I6-B neighbor-capacity stress margin = 0.010
threshold_margin_ratio_vs_i6 = 5.0
```

This should not be read as five times the transmitted or exchanged capacity.
The stronger capacity-change evidence in I6-B is the lobe exchange:

```text
observed lobe deltas = 0.060 / 0.062
lobe threshold = 0.040
minimum lobe-exchange margin = 0.020
```

The fuller interpretation is that original I6 has narrow normalized
generative-edge eligibility headroom, roughly 2.7-2.8% over the mean declared
threshold with a weakest raw margin of `0.002`. I6-B adds a different
circulatory medium geometry with stronger lobe-exchange headroom and a 5x
larger raw stress gate margin. Both remain provisional pending I7 replay and
relation controls.

## Key Fields

```text
participant_ladder_rung_assigned = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung_assigned = M2_candidate_alternative_source_pending_I7_controls
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate_with_alternative_C5_input_evidence
alternative_lobe_exchange_margin = 0.02
threshold_margin_delta_vs_i6 = 0.008
threshold_margin_ratio_vs_i6 = 5.0
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
ready_for_iteration_7_replay_controls = true
```

## Artifacts

| Role | Path |
|---|---|
| i6c_alternative_mechanism_contrast_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_contrast_margin_i6c_artifacts/i6c_alternative_mechanism_contrast_trace.json` |
| i6c_claim_boundary_guard | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_contrast_margin_i6c_artifacts/i6c_claim_boundary_guard.json` |

## Checks

- source_i6b_passed: true
- threshold_margin_improves_over_i6_reference: true
- mechanism_contrast_supported: true
- final_c5_claim_blocked: true
- artifact_manifest_sha256_matches: true
- no_absolute_paths_in_records: true
