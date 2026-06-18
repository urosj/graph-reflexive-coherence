# N17 Iteration 8-B - B4/C5 Reverse-Perspective Replay Probe

Artifact: `n17_b4c5_reverse_perspective_replay_probe`
Status: `passed`
Acceptance state: `accepted_b4c5_reverse_perspective_blocked_multi_source_context_preserved_no_final_ap7`
Output digest: `2434af23c68d0a6e3856e8e131a9ff60ce4eee8252ad2c30235e347774ea22f7`

## Main Result

Iteration 8-B tests the original N16 B4_C5 row specifically. B4_C5 is multi-basin, but it is not perspective-paired: the source records basin A as internal and the neighbor basin as external. Reverse-perspective replay remains blocked because reverse internal support, reverse coherence, reverse boundary-side assignment, reverse boundary edge, and reverse later-internal feedback trace are not source-backed.

```text
b4c5_multi_basin_source_present = true
b4c5_perspective_paired_supported = false
b4c5_reverse_perspective_replay_supported = false
alternate_source_shared_medium_g6_candidate_supported = true
general_shared_medium_g6_supported = false
final_ap7_supported = false
```

## Source Audit

```text
basin_count = 2
forward_internal_nodes = ['b4_c5_a0', 'b4_c5_a1', 'b4_c5_a2']
reverse_internal_nodes = []
neighbor_basin_treated_as_external_side = true
has_neighbor_internal_descriptor = false
has_reverse_support_metric = false
has_reverse_coherence_metric = false
reverse_boundary_edge_source_backed = false
reverse_trace_source_backed = false
shared_medium_leakage = 0.108
leakage_into_neighbor_basin = 0.07
merge_confusion_pressure = 0.14
```

## Rows

| Row | Probe | Decision | Blocker |
| --- | --- | --- | --- |
| `n17_i8b_row_01_b4c5_reverse_source_inventory` | `b4c5_reverse_source_inventory` | `blocked` | `reverse_internal_side_not_source_backed` |
| `n17_i8b_row_02_b4c5_neighbor_internal_support_control` | `b4c5_neighbor_internal_support_control` | `blocked` | `neighbor_internal_support_metric_missing` |
| `n17_i8b_row_03_b4c5_neighbor_coherence_control` | `b4c5_neighbor_coherence_control` | `blocked` | `neighbor_coherence_metric_missing` |
| `n17_i8b_row_04_b4c5_reverse_boundary_assignment_control` | `b4c5_reverse_boundary_assignment_control` | `blocked` | `reverse_boundary_side_assignment_missing` |
| `n17_i8b_row_05_b4c5_reverse_boundary_edge_control` | `b4c5_reverse_boundary_edge_control` | `blocked` | `reverse_boundary_edge_missing` |
| `n17_i8b_row_06_b4c5_reverse_feedback_trace_control` | `b4c5_reverse_feedback_trace_control` | `blocked` | `reverse_later_internal_feedback_trace_missing` |
| `n17_i8b_row_07_b4c5_label_swap_relabel_control` | `b4c5_label_swap_relabel_control` | `rejected` | `label_swap_is_not_reverse_replay` |
| `n17_i8b_row_08_b4c5_reverse_leakage_merge_metrics_partial` | `b4c5_reverse_leakage_merge_metrics_partial` | `partial` | `leakage_and_merge_metrics_exist_but_do_not_supply_reverse_internal_state` |
| `n17_i8b_row_09_b4c5_perspective_paired_candidate` | `b4c5_perspective_paired_candidate` | `blocked` | `perspective_paired_b4c5_not_supported` |

## Interpretation

8-B confirms that the overall shared-medium state remains multi-source because of 8-A, but the original B4_C5 row itself remains one-sided. It is multi-basin, not perspective-paired. I9 should preserve both facts: shared-medium G6 candidate evidence is multi-source, while B4_C5 reverse-perspective replay and general/symmetric G6 remain blocked.

## Checks

- `b4c5_multi_basin_source_present`: pass
- `b4c5_reverse_internal_side_not_source_backed`: pass
- `b4c5_reverse_support_and_coherence_missing`: pass
- `b4c5_reverse_trace_legs_missing`: pass
- `all_reverse_probe_rows_fail_closed`: pass
- `i8a_multi_source_context_preserved`: pass
- `unsafe_claim_flags_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
