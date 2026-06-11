# Experiment B Column-Interface Cancellation

Status: complete.

## Scope

This report tests whether a derived column-local cancellation/pressure
proxy is observable under the Lane A baseline
`current_hybrid_signed_hessian`.

It does not claim direct column-H spark gating. Column-H remains an
analysis-derived proxy unless a future canonical-column-H lane exists.

## Outputs

- `../outputs/experiment_b_column_interface_cancellation_rows.csv`
- `../outputs/experiment_b_column_interface_cancellation_sign_crossings.csv`
- `../outputs/experiment_b_column_interface_cancellation_summary.json`
- `../outputs/experiment_b_column_interface_cancellation_manifest.json`
- `../reports/experiment_b_column_interface_cancellation_blocked_observations.csv`

## Fixture Matching

- energy totals matched: `true`
- each column fixture uses the same row-wise plus/minus coherence pattern
  moved to a different target column.

## Identity Column Proxy Responses

| Fixture | Expected Column | Pressure Column | Cancellation Column |
| --- | ---: | ---: | ---: |
| b_column_1_near_cancellation_near_zero_seed_0 | 1 | 1 | 1 |
| b_column_2_near_cancellation_near_zero_seed_0 | 2 | 2 | 2 |
| b_column_3_near_cancellation_near_zero_seed_0 | 3 | 3 | 3 |

## Column Permutation Controls

- column proxy moves under column permutation: `true`

| Fixture | Expected Column After Permutation | Pressure Column | Cancellation Column |
| --- | ---: | ---: | ---: |
| b_column_1_near_cancellation_near_zero_seed_0 | 3 | 3 | 3 |
| b_column_2_near_cancellation_near_zero_seed_0 | 1 | 1 | 1 |
| b_column_3_near_cancellation_near_zero_seed_0 | 2 | 2 | 2 |

## Sign-Crossing Proxy Pairs

| Column | Before Signed Sum | After Signed Sum | Crosses Zero |
| ---: | ---: | ---: | --- |
| 1 | 0.006764348 | -0.010854531 | `true` |
| 2 | 0.006764348 | -0.010854531 | `true` |
| 3 | 0.006764348 | -0.010854531 | `true` |

## Event Terminology

- spark candidate events: `0`
- refinement events: `0`
- completed identity-level events: `0`
- direct column-H gate claim: `blocked_under_lane_a`

## Controls Summary

- identity column proxy matches expected column: `true`
- row permutation preserves proxy column: `true`
- transpose control rows present: `true`
- transpose removes predefined clean column claim: `true`
- random relabel removes predefined clean column claim: `true`
- minimum true-minus-random cancellation interpretability margin: `0.003354`

## Interpretation

Experiment B supports observability of a derived column-local
cancellation/pressure proxy in a clean saturated central-node fixture
under Lane A.

Column-local plus/minus patterns produce the expected target-column
proxy signature, column permutation moves that signature, and row
permutation does not explain it away. Random relabeling removes the
predefined clean column claim.

This is not evidence that column-H directly triggered a spark. Under
Lane A, spark candidates remain signed-Hessian hybrid candidates.
This run produced no refinement or completed identity-level events,
so routing/refinement/identity consequences are recorded as blocked
or inconclusive in the companion blocked-observations CSV.
