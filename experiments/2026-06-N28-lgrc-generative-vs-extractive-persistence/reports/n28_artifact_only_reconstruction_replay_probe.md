# N28 Iteration 5-A - Artifact-Only Reconstruction Replay Probe

## Summary

- Status: `passed`
- Acceptance state: `accepted_artifact_only_reconstruction_controls_fail_closed_no_new_ge_support`
- Output digest: `c88d2605b60f272ab4fd50bc062c09ab5059f26bf236e7339309196f47863646`
- I5 GE4 result preserved: `true`
- I5-A new GE support opened: `false`
- GE5 or stronger supported: `false`

I5-A tries to reconstruct N28 support from insufficient surfaces: report text, regime labels, N27 transfer context, digests/hashes, and the I5 matrix summary alone. Every path fails closed. This protects I5 from being overread as report-only or label-only evidence.

## Control Summary

```text
control_row_count = 5
failed_closed_row_count = 5
failed_open_row_count = 0
positive_support_allowed_rows = []
source_current_n28_trace_missing_blocks_support = true
```

## Control Rows

| Row | Mode | Decision | Reason |
|---|---|---|---|
| `n28_i5a_report_only_reconstruction_control` | `report_only_summary` | `rejected` | report text summarizes the result but cannot satisfy source-current N28 trace requirements |
| `n28_i5a_label_only_regime_reconstruction_control` | `regime_labels_and_counts_only` | `rejected` | regime labels and counts cannot replace source-current geometric deltas |
| `n28_i5a_n27_transfer_only_reconstruction_control` | `n27_transfer_context_only` | `rejected` | N27 transfer success is prerequisite context and cannot recreate N28 generative/extractive regime evidence |
| `n28_i5a_digest_only_reconstruction_control` | `digest_and_hashes_only` | `rejected` | digests prove provenance but do not by themselves replay the regime classifier |
| `n28_i5a_matrix_summary_only_reconstruction_control` | `i5_matrix_summary_only` | `rejected` | I5 matrix summary confirms replay outcome but cannot replace per-row source-current evidence for a new positive claim |

## Interpretation

I5-A does not add new positive GE support. It confirms that the I5 GE4 result depends on source-current N28 traces and per-row replay controls. Reports, labels, N27 transfer context, digests, and matrix summaries can document or verify provenance, but cannot replace the regime metrics and capacity-attribution traces.

The GE4 candidate remains sourced to I5. GE5/GE6, final N28, semantic cooperation, agency, native support, Phase 8 completion, and ant ecology remain blocked pending stress, claim classification, and closeout.

## Checks

| Check | Passed |
|---|---|
| `i5_replay_matrix_passed` | `true` |
| `all_controls_failed_closed` | `true` |
| `no_controls_failed_open` | `true` |
| `no_artifact_only_positive_support` | `true` |
| `report_only_reconstruction_rejected` | `true` |
| `label_only_reconstruction_rejected` | `true` |
| `n27_transfer_only_reconstruction_rejected` | `true` |
| `digest_only_reconstruction_rejected` | `true` |
| `matrix_summary_only_reconstruction_rejected` | `true` |
| `ge5_and_ge6_still_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
