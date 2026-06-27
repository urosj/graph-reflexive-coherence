# N23 Iteration 6-A - AP4 Selection Geometry Robustness Probe

Status: `passed`
Acceptance state: `accepted_ap4_selection_geometry_robustness_stress_evidence_pending_i7`
Output digest: `69541623939689724ca04c248125995f4c2ab5a5a51faf2e8e9153b62a18e0f5`

## Summary

I6-A stress-tests the I6 AP4 bridge candidate by varying source-current branch geometry. It preserves I6 as the primary AP4 bridge record and classifies this as robustness evidence only.

| Case | Decision | Selected | Margin | Role |
| --- | --- | --- | ---: | --- |
| `reference_four_branch_geometry` | `supported` | `branch_edge_4_node_5` | `0.500000000000` | `reference_pass` |
| `eroded_margin_still_supported` | `supported` | `branch_edge_4_node_5` | `0.300000000000` | `narrow_margin_pass` |
| `alternate_branch_wins_supported` | `supported` | `branch_edge_0_node_1` | `0.500000000000` | `alternate_winner_pass` |
| `below_margin_rejected` | `rejected` | `branch_edge_4_node_5` | `0.100000000000` | `margin_gate_fail` |
| `equalized_tie_rejected` | `rejected` | `branch_edge_4_node_5` | `0.000000000000` | `tie_gate_fail` |

## Interpretation

I6-A shows that the I6 AP4 candidate is stronger than a single fixed selected-label result: selection follows branch geometry when the winning branch changes, but fails closed when the score margin is too narrow or tied.

```text
reference: branch_edge_4_node_5 wins by margin 0.5
eroded margin: branch_edge_4_node_5 still wins by margin 0.3
alternate winner: branch_edge_0_node_1 wins when its source-current support-gradient rises to 2.5
below margin: rejected at margin 0.1
equalized tie: rejected at margin 0.0
```

## Claim Boundary

```text
I6 remains the primary AP4 bridge candidate.
I6-A adds robustness/stress evidence.
general AP4 robustness = not claimed
semantic choice = false
agency = false
native support = false
final N23 = false pending I7/I8
```

## Checks

| Check | Passed |
| --- | --- |
| `i6_source_passed` | `true` |
| `three_supported_stress_rows` | `true` |
| `two_fail_closed_stress_rows` | `true` |
| `alternate_winner_changes_with_geometry` | `true` |
| `eroded_margin_remains_above_threshold` | `true` |
| `below_margin_and_tie_fail_closed` | `true` |
| `duplicate_replay_stable_for_supported_rows` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `robustness_controls_fail_closed` | `true` |
| `artifact_hashes_match` | `true` |
| `artifact_roles_match_i2_frozen_enum` | `true` |
| `artifact_paths_are_portable` | `true` |
