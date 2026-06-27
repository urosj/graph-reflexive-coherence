# N23 Iteration 6 - AP4-Relevant Selection Geometry Probe

Status: `passed`
Acceptance state: `accepted_ap4_selection_geometry_lc5_candidate_pending_i7`
Output digest: `ff20018f3546c0567a03d840c14d2e924b9aca162ff25e74b912579c33a24422`

## Summary

I6 consumes the replay-backed I5/I5-A collapse rows and asks whether their selected branch is source-current, branch-conditioned geometry rather than producer preference, random tie, N22 inherited context, or semantic choice.

## Rows

| Row | Source | Branches | Retained | Selected | Margin | LC | AP4 bridge |
| --- | --- | ---: | ---: | --- | ---: | --- | --- |
| `n23_i6_row_01_minimal_ap4_selection_geometry_bridge` | `minimal_two_branch_replay_backed_collapse` | `2` | `1` | `branch_edge_4_node_5` | `0.500000000000` | `LC5` | `bridge_candidate_supported` |
| `n23_i6_row_02_multibranch_ap4_selection_geometry_bridge` | `four_branch_replay_backed_collapse` | `4` | `3` | `branch_edge_4_node_5` | `0.500000000000` | `LC5` | `bridge_candidate_supported` |

## Geometric Interpretation

I6 does not claim semantic choice. It shows that the selected continuation in both the minimal and four-branch cases is conditioned by source-current branch geometry: branch-specific coherence, conductance, support-gradient score, margin over the runner-up, and retained counterfactual branch records.

```text
minimal: 2 branches, selected branch_edge_4_node_5 over branch_edge_0_node_1 by support-gradient margin 0.5
multibranch: 4 branches, selected branch_edge_4_node_5 over three retained counterfactual branches by the same source-current support-gradient rule
AP4 bridge: candidate-supported because route/branch-conditioned selection is source-current, replay-backed, control-backed, row-local AP4 dependency is recorded, and producer/semantic relabels fail closed
```

## Negative Controls

The AP4 bridge controls fail closed for producer preference, random tie, branch-label-only selection, missing AP4 dependency, N22-context reuse, semantic choice relabel, missing replay backing, and missing counterfactual retention.

## Claim Boundary

```text
LC5 = provisional AP4-relevant selection-geometry bridge candidate
LC6 = false pending I7/I8
AP4 bridge final claim = false pending I7/I8
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
| `two_ap4_bridge_rows_supported` | `true` |
| `minimal_and_multibranch_lc5_candidates` | `true` |
| `row_local_ap4_dependency_recorded` | `true` |
| `ap5_not_applicable_without_proxy_or_target` | `true` |
| `selection_geometry_is_source_current_and_branch_conditioned` | `true` |
| `counterfactual_branches_auditable` | `true` |
| `replay_and_controls_backing_present` | `true` |
| `ap4_negative_controls_fail_closed` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `semantic_choice_and_agency_blocked` | `true` |
| `artifact_manifest_hashes_match` | `true` |
| `artifact_roles_match_i2_frozen_enum` | `true` |
| `artifact_paths_are_portable` | `true` |
