# N23 Iteration 7 - Replay And Control Matrix

Status: `passed`
Acceptance state: `accepted_full_replay_control_matrix_lc5_candidate_pending_i8`
Output digest: `817aa46c8c55e341b329e8c2bfe7c3775043a166e920880f790f37346a066485`

## Summary

I7 consumes the provisional N23 rows from I3 through I6-A and validates them as a full replay/control matrix. It assigns I7-consumable LC rungs, but keeps final closeout and N24 handoff pending I8.

## Primary Matrix Rows

| Row | Variant | Branches | Selected | Margin | I7 LC | Decision |
| --- | --- | ---: | --- | ---: | --- | --- |
| `n23_i7_row_01_minimal_lc5_full_matrix` | `minimal_two_branch_lc5_path` | `2` | `branch_edge_4_node_5` | `0.500000000000` | `LC5` | `supported` |
| `n23_i7_row_02_multibranch_lc5_full_matrix` | `four_branch_lc5_path` | `4` | `branch_edge_4_node_5` | `0.500000000000` | `LC5` | `supported` |

## Stress Matrix Rows

| Case | Decision | Selected | Margin | Role |
| --- | --- | --- | ---: | --- |
| `reference_four_branch_geometry` | `supported` | `branch_edge_4_node_5` | `0.500000000000` | `bounded_ap4_stress_support` |
| `eroded_margin_still_supported` | `supported` | `branch_edge_4_node_5` | `0.300000000000` | `bounded_ap4_stress_support` |
| `alternate_branch_wins_supported` | `supported` | `branch_edge_0_node_1` | `0.500000000000` | `bounded_ap4_stress_support` |
| `below_margin_rejected` | `rejected` | `branch_edge_4_node_5` | `0.100000000000` | `negative_stress_control` |
| `equalized_tie_rejected` | `rejected` | `branch_edge_4_node_5` | `0.000000000000` | `negative_stress_control` |

## Control Matrix

```text
active nulls: 14/14 failed closed
minimal replay path: artifact, snapshot/load, and duplicate replay passed; seven LC4 controls failed closed
multibranch replay path: artifact, snapshot/load, and duplicate replay passed; seven LC4 controls failed closed
AP4 bridge: eight AP4-specific controls failed closed
AP4 stress: three bounded stress rows supported; below-margin and equalized-tie rows failed closed
closeout: LC5/N23-C5 candidate only; LC6/N23-C6 pending I8
```

## Claim Boundary

```text
I7-supported LC rung = LC5
I7-supported N23 closeout candidate = N23-C5
LC6 = pending I8 closeout
final AP4 supported = false
final N23 supported = false
semantic choice = false
semantic intention = false
agency = false
native support = false
sentience = false
Phase 8 = false
ant ecology implementation = false
```

## Checks

| Check | Passed |
| --- | --- |
| `source_inputs_passed` | `true` |
| `all_active_nulls_consumed_and_failed_closed` | `true` |
| `primary_lc5_rows_supported` | `true` |
| `bounded_stress_rows_classified` | `true` |
| `required_control_status_values_valid` | `true` |
| `no_required_failed_open_or_not_run_controls` | `true` |
| `artifact_manifest_hashes_match` | `true` |
| `artifact_roles_match_i2_frozen_enum` | `true` |
| `artifact_paths_are_portable` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `claim_boundaries_preserved` | `true` |
| `no_absolute_paths_in_matrix_payload` | `true` |
