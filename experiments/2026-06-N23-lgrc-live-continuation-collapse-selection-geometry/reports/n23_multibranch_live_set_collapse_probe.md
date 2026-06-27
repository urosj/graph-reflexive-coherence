# N23 Iteration 4-A - Multi-Branch Live-Set Collapse Probe

Status: `passed`

Acceptance state: `accepted_multibranch_source_current_lc3_candidate_pending_i5a`

Output digest: `1c52af46ebbedadf8cd0bee091ad14785c58b21e412f8c01a06c315261ce5339`

## Summary

Iteration 4-A adds breadth to I4 by producing a source-current four-branch live set inside the same LGRC9V3 basin. It remains provisional LC3 pending I5-A replay/control validation.

## Branch Geometry

| Branch | Score | Source Coherence | Edge |
| --- | ---: | ---: | ---: |
| `branch_edge_0_node_1` | 1.500000000000 | 13.000000000000 | 0 |
| `branch_edge_4_node_5` | 2.000000000000 | 11.000000000000 | 4 |
| `branch_edge_6_node_7` | 1.000000000000 | 10.250000000000 | 6 |
| `branch_edge_8_node_9` | 0.500000000000 | 12.000000000000 | 8 |

## Result

```text
branch_count = 4
retained_non_selected_branch_count = 3
selected_branch_id = branch_edge_4_node_5
selection_reason = support_gradient_dominance
score_margin = 0.500000000000
provisional_lc_ladder_rung = LC3
live_continuation_collapse_claim_allowed = false
```

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_passed` | `true` | "accepted_source_handoff_inventory_no_live_continuation_evidence" |
| `i2_schema_passed` | `true` | "accepted_live_continuation_schema_frozen_no_positive_evidence" |
| `i3_active_nulls_ready` | `true` | "accepted_active_nulls_fail_closed_no_positive_evidence" |
| `i4_minimal_probe_preserved` | `true` | "accepted_minimal_source_current_lc3_candidate_pending_replay_controls" |
| `candidate_row_field_set_matches_i2_required_fields` | `true` | {"candidate_count": 80, "extra": [], "missing": [], "required_count": 80} |
| `source_current_inputs_present` | `true` | ["LGRC9V3 pre-collapse runtime snapshot", "LGRC9V3 four-branch live-set trace emitted from the same runtime state", "LGRC9V3 selected-branch packet... |
| `artifact_manifest_non_empty_and_allowed_roles` | `true` | [{"artifact_role": "collapse_trace", "path": "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_multibranch_li... |
| `artifact_hashes_match` | `true` | [{"artifact_role": "collapse_trace", "path": "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_multibranch_li... |
| `artifact_paths_repository_relative` | `true` | ["experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/outputs/n23_multibranch_live_set_collapse_probe_artifacts/n23_i4a_coll... |
| `four_branch_live_set_present` | `true` | {"artifact_role": "branch_set_trace", "branch_count": 4, "path": "experiments/2026-06-N23-lgrc-live-continuation-collapse-selection-geometry/output... |
| `three_counterfactual_branches_retained` | `true` | {"artifact_role": "counterfactual_retention_trace", "immutable_pre_collapse_audit_record": true, "path": "experiments/2026-06-N23-lgrc-live-continu... |
| `collapse_trace_present` | `true` | {"artifact_role": "collapse_trace", "event_counts_by_kind": {"lgrc9v3_causal_spark_candidate": 1, "lgrc9v3_local_update": 1, "lgrc9v3_packet_arriva... |
| `selected_reason_geometry_conditioned` | `true` | {"counterfactual_retention_trace_present": true, "min_score_margin": 0.25, "retained_non_selected_branch_count": 3, "runner_up_score": 1.5, "score_... |
| `support_and_coherence_gates_accepted` | `true` | {"coherence": {"coherence_floor": 9.85, "coherence_margin": 1.1500000000000004, "selected_branch_source_node_coherence_after": 10.94, "status": "ch... |
| `boundary_and_flux_gates_accepted` | `true` | {"boundary": {"branch_count": 4, "distinct_branch_edges": [0, 4, 6, 8], "status": "preserved", "topology_signature_same": true}, "flux": {"in_fligh... |
| `claim_allowed_false_pending_replay_controls` | `true` | "provisional source-current LC3 multi-branch live-continuation collapse candidate pending I5-A replay and I7 controls; no AP4 bridge support, seman... |
| `unsafe_flags_all_false` | `true` | {"agency": false, "consciousness": false, "free_will": false, "fully_native_integration": false, "identity_acceptance": false, "native_ant_agency":... |
| `lc3_only_pending_i5a_replay` | `true` | {"affected_rungs": ["LC4", "LC5", "LC6", "N23-C4", "N23-C5", "N23-C6"], "artifact_replay": "not_run", "duplicate_replay": "not_run", "not_run_reaso... |

## Claim Boundary

I4-A supports only additive provisional LC3 breadth evidence. It does not replace I4 and does not support LC4, LC5, LC6, AP4 bridge closeout, semantic choice, agency, native support, sentience, Phase 8, or ant-ecology implementation.
