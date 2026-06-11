# Experiment G Mixed Row/Column Motion

Status: complete.

## Scope

This report tests whether an experiment-local checkpoint-overlay
observer can classify dominant central-port motion as row-preserving
and column-changing, column-preserving and row-changing, both-changing,
or neither-changing.

The evidence surface is `GRC9V3State.port_edges` plus topology endpoint
metadata. Full reusable motion-loader port histories remain partial.

## Observer Rule

- dominant flux edge: central-node incident edge with maximum
  `abs(PortEdge.flux_uv)`
- dominant boundary edge: same selected central-node incident edge
- successor: opposite endpoint of the selected dominant edge
- port coordinates: canonical `port_to_rc(central_port)`
- ties: break by edge id and report tie count

## Canonical Controls

| Condition | Transform | Ports | Rows | Columns | Classes | Match |
| --- | --- | --- | --- | --- | --- | --- |
| g_row_preserving_column_changing | identity | 4 5 6 | 2 2 2 | 1 2 3 | row_preserving_column_changing | row_preserving_column_changing | `true` |
| g_row_preserving_column_changing | row_permutation_231 | 7 8 9 | 3 3 3 | 1 2 3 | row_preserving_column_changing | row_preserving_column_changing | `true` |
| g_row_preserving_column_changing | column_permutation_312 | 6 4 5 | 2 2 2 | 3 1 2 | row_preserving_column_changing | row_preserving_column_changing | `true` |
| g_column_preserving_row_changing | identity | 3 6 9 | 1 2 3 | 3 3 3 | column_preserving_row_changing | column_preserving_row_changing | `true` |
| g_column_preserving_row_changing | row_permutation_231 | 6 9 3 | 2 3 1 | 3 3 3 | column_preserving_row_changing | column_preserving_row_changing | `true` |
| g_column_preserving_row_changing | column_permutation_312 | 2 5 8 | 1 2 3 | 2 2 2 | column_preserving_row_changing | column_preserving_row_changing | `true` |
| g_static_no_motion_baseline | identity | 5 5 5 | 2 2 2 | 2 2 2 | neither_changing | neither_changing | `true` |
| g_static_no_motion_baseline | row_permutation_231 | 8 8 8 | 3 3 3 | 2 2 2 | neither_changing | neither_changing | `true` |
| g_static_no_motion_baseline | column_permutation_312 | 4 4 4 | 2 2 2 | 1 1 1 | neither_changing | neither_changing | `true` |

## Random Relabel Controls

| Condition | Ports | Rows | Columns | Observed Classes | Interpretation |
| --- | --- | --- | --- | --- | --- |
| g_row_preserving_column_changing | 9 1 3 | 3 1 1 | 3 1 3 | both_changing | row_preserving_column_changing | semantic_interpretability_weakened_by_random_relabel |
| g_column_preserving_row_changing | 5 3 7 | 2 1 3 | 2 3 1 | both_changing | both_changing | semantic_interpretability_weakened_by_random_relabel |
| g_static_no_motion_baseline | 1 1 1 | 1 1 1 | 1 1 1 | neither_changing | neither_changing | semantic_interpretability_weakened_by_random_relabel |

## Summary

- canonical controls match expected classes: `true`
- row-preserving/column-changing supported: `true`
- column-preserving/row-changing supported: `true`
- static no-motion baseline supported: `true`
- random relabel weakens semantic interpretability: `true`

## Interpretation

Experiment G supports observer-local mixed row/column motion
classification in clean checkpoint-overlay fixtures. Dominant
edge/port histories are sufficient to classify row-preserving
column-changing and column-preserving row-changing transitions under
identity, row-permutation, and column-permutation controls.

The random degree-preserving port relabel is non-factorized, so the
canonical row/column interpretation is intentionally weakened rather
than treated as a failed canonical class.

This result does not establish landscape-general motion behavior or
full reusable motion-loader support for normalized port histories.
