# N28 Iteration 6-A - Regime Boundary / Transition Matrix

## Summary

- Status: `passed`
- Acceptance state: `accepted_regime_boundary_transition_matrix_same_policy_supported_no_new_ge_support`
- Output digest: `e6b0afbf81873e519db458e611cc01a1c11b2e9b5c2dead899946b270077700d`
- I6 GE5 result preserved: `true`
- I6-A new GE support opened: `false`
- GE6 supported: `false`
- Shared regime policy status: `supported`

I6-A varies the declared transition envelope around the I6 GE5 result.
It is a same-policy classifier-boundary probe: no source row is mutated,
thresholds are not retuned, and no new source-current N28 evidence row is
opened.

## Transition Summary

```text
transition_row_count = 34
label_match_count = 34
label_mismatch_count = 0
ge5_boundary_preservation_row_count = 16
new_source_current_evidence_opened = false
thresholds_retuned_for_transition = false
source_rows_mutated = false
shared_policy_ids = ['n28_shared_regime_policy_v1']
```

## Transition Roles

| Role | Rows | Passed | Failed |
|---|---:|---:|---:|
| `source_current_anchor` | 8 | 8 | 0 |
| `same_regime_boundary_edge` | 8 | 8 | 0 |
| `unclassified_gap_expected` | 8 | 8 | 0 |
| `opposite_regime_cross_check` | 6 | 6 | 0 |
| `aggregate_enrichment_cross_check` | 2 | 2 | 0 |
| `aggregate_depletion_cross_check` | 2 | 2 | 0 |

## Label Transitions

| Transition | Count |
|---|---:|
| `competitive->competitive` | 2 |
| `competitive->extractive` | 1 |
| `competitive->generative` | 1 |
| `competitive->unclassified` | 1 |
| `extractive->extractive` | 6 |
| `extractive->generative` | 3 |
| `extractive->unclassified` | 3 |
| `generative->extractive` | 3 |
| `generative->generative` | 6 |
| `generative->unclassified` | 3 |
| `neutral->extractive` | 1 |
| `neutral->generative` | 1 |
| `neutral->neutral` | 2 |
| `neutral->unclassified` | 1 |

## Interpretation

I6-A supports the same shared regime policy as a boundary classifier, not as
new source-current GE evidence. Source anchors and same-regime edge rows
are allowed to preserve the I6 GE5 support, while boundary-gap and
opposite-cross rows are controls that test whether the classifier changes
for the right geometric reason.

The key protection is that neutral/competitive classification is not allowed
from near-zero aggregate deltas alone. When mixed-lobe or circulation
evidence is removed, the row becomes unclassified rather than being
promoted by label. When aggregate enrichment or depletion crosses the
declared regime thresholds, the same policy classifies it as generative
or extractive.

This preserves the I6 GE5 result and supports
`shared_regime_policy_status = supported`, but it does not create GE6,
final N28, semantic cooperation, agency, native support, Phase 8
completion, or ant ecology evidence.

## Checks

| Check | Passed |
|---|---|
| `i6_stress_matrix_pinned_and_passed` | `true` |
| `all_source_rows_have_transition_paths` | `true` |
| `all_transition_labels_match_expected` | `true` |
| `unclassified_gaps_present` | `true` |
| `opposite_cross_checks_present` | `true` |
| `competitive_neutral_edges_present` | `true` |
| `single_shared_policy_family_preserved` | `true` |
| `thresholds_not_retuned_for_transition` | `true` |
| `source_rows_not_mutated` | `true` |
| `no_new_source_current_evidence_opened` | `true` |
| `i6_ge5_preserved_ge6_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
