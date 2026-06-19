# N18 Iteration 9 - Long-Horizon Control And Classification Matrix

## Summary

```text
status = passed
acceptance_state = accepted_limited_ap8_classification_pending_i10_closeout
classified_ap_level = AP8_limited_artifact_candidate
ap8_classification_supported = true
ap8_candidate_allowed = true
final_ap8_supported = false
max_supported_horizon = h4
highest_positive_stress_ladder_rung = L5
replay_control_ladder_rung = L6
ready_for_iteration10_closeout = true
output_digest = c7b400660c5203a3b975b1921ee808ad447329ebdda199af47ba27e26d1fc734
```

## Classification

| Field | Value |
| --- | --- |
| Claim classification | `artifact_level_ap8_long_horizon_agentic_like_closure_candidate_pending_i10_closeout` |
| Claim ceiling | `artifact_level_ap8_long_horizon_agentic_like_closure_candidate` |
| Classification row | `n18_i9_row_01_ap8_limited_classification` |
| Final closeout pending | `true` |

## Requirement Matrix

| Requirement | Decision | Supported By | Role |
| --- | --- | --- | --- |
| source_inventory_and_schema | supported | I1, I2 | AP8 gate and source contract |
| h4_horizon_envelope | supported_limited | I3, I4 | narrow long-horizon envelope |
| support_proxy_and_route_memory_stress | supported_limited | I5, I6 | L3/L4 prerequisite stress |
| environment_resource_stress | supported_limited | I7 | L5 environment/resource stress |
| shared_medium_stress | supported_limited | I8, I8-A | L5 shared-medium stress |
| replay_and_controls | supported | I9 | L6 replay/control cleanliness |
| claim_boundary | supported | I9 | L7 artifact-level AP8 classification |

## Replay Matrix

| Replay | Status | Role |
| --- | --- | --- |
| `artifact_only_reconstruction` | `stable` | positive L6 replay control |
| `duplicate_replay` | `stable` | duplicate replay did not alter classification digest |
| `snapshot_load_replay` | `stable` | snapshot/load replay preserved source-current row |
| `order_inversion_control` | `failed_expected` | negative order control |
| `post_hoc_stitching_control` | `failed_expected` | negative construction control |

## Interpretation

Iteration 9 classifies the existing N18 h4/L5 stress stack as a
limited artifact-level AP8 candidate. It does not widen the horizon,
recover h8, change the budget policy, retune thresholds, or promote
shared-medium evidence into general robustness.

The classification preserves the I8/I8-A distinction. I8 remains the
minimal equality-at-floor shared-medium edge case, while I8-A is
additional higher-margin support. The conservative classification
row still carries the I8 bottleneck: `boundary_to_loop_feedback` at
0.800 and budget headroom 0.01.

Replay and controls now pass the L6 gate: artifact-only
reconstruction, duplicate replay, and snapshot/load replay are
stable; stale-state, single-axis stale, order inversion, post-hoc
stitching, hidden native support, semantic agency/action/perception,
identity, Phase 8, B4/C5 relabel, general symmetric multi-basin,
and budget-overrun controls fail closed as required.

The result supports AP8 classification only at artifact level and
only for the narrow h4/L5 envelope. Final AP8 freeze, final claim
ceiling, and handoff remain pending Iteration 10.

## Checks

| Check | Passed |
| --- | --- |
| all_source_artifacts_passed | true |
| i8_and_i8a_roles_preserved | true |
| all_ap8_gates_true_for_classification_row | true |
| replay_statuses_match_schema | true |
| negative_controls_match_ap8_expectations | true |
| single_axis_stale_controls_fail_closed | true |
| narrow_h4_l5_stack_preserved | true |
| unsafe_claim_flags_false | true |
| final_ap8_pending_i10 | true |
| no_absolute_paths | true |
