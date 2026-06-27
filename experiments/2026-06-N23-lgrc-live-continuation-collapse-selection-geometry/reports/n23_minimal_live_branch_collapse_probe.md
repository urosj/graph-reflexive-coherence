# N23 Iteration 4 - Minimal Live-Branch Collapse Probe

Status: `passed`

Acceptance state: `accepted_minimal_source_current_lc3_candidate_pending_replay_controls`

Output digest: `720890f8a556409625b83bdade1f3d21fa92368a2ffc5a7ce87dd35148220626`

## Summary

Iteration 4 runs the first positive N23 probe. It produces a source-
current live branch set from the LGRC9V3 column-H fixture, collapses to
one continuation via support-gradient dominance, and records the
non-selected branch as immutable pre-collapse counterfactual retention.

The row remains provisional. I4 does not run replay controls and does
not support LC4, LC5, LC6, AP4 bridge closeout, semantic choice, agency,
native support, sentience, Phase 8, or ant-ecology implementation.

## Geometric Interpretation

Two branch records are emitted from the same pre-collapse LGRC9V3 runtime state. They are distinct by edge, source node, coherence, conductance, and support-gradient score.

The selected branch has the higher support-gradient score by the declared margin, so the producer schedules one packet along that branch and records the resulting departure, arrival, and local-update events.

The non-selected branch remains as an immutable pre-collapse audit record. It need not remain dynamically active after collapse.

```text
selected_branch_id = branch_edge_4_node_5
selection_reason = support_gradient_dominance
score_margin = 0.500000000000
selected_packet_amount = 0.060000000000
```

## Candidate Row

| Field | Value |
| --- | --- |
| Row | `n23_i4_row_01_minimal_live_branch_collapse_probe` |
| Decision | `partial` |
| Provisional LC rung | `LC3` |
| Claim allowed | `false` |
| Derived report only | `false` |
| AP4 status | `required_recorded` |
| AP5 status | `not_applicable` |
| Artifact manifest entries | `9` |

## Gates

| Gate | Status |
| --- | --- |
| Support | `changed_within_allowed_delta_above_floor` |
| Coherence | `changed_within_allowed_delta_above_floor` |
| Boundary | `preserved` |
| Flux/leakage | `preserved` |
| Replay | `not_run` |

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_ready` | `true` |
| `candidate_row_field_set_matches_i2_required_fields` | `true` |
| `derived_report_only_false` | `true` |
| `source_current_inputs_present` | `true` |
| `artifact_manifest_non_empty_and_allowed_roles` | `true` |
| `artifact_hashes_match` | `true` |
| `artifact_paths_repository_relative` | `true` |
| `live_branch_set_present` | `true` |
| `collapse_trace_present` | `true` |
| `counterfactual_retention_present` | `true` |
| `selected_reason_geometry_conditioned` | `true` |
| `support_gate_accepted` | `true` |
| `coherence_gate_accepted` | `true` |
| `boundary_gate_accepted` | `true` |
| `flux_gate_accepted` | `true` |
| `ap4_recorded_ap5_not_applicable` | `true` |
| `n22_inherited_delta_not_used` | `true` |
| `unsafe_flags_all_false` | `true` |
| `claim_allowed_false_pending_replay_controls` | `true` |
| `lc3_only_pending_replay` | `true` |

## Claim Boundary

This is a provisional LC3 candidate pending I5 replay and I7 controls. It is not semantic choice, intention, agency, native support, sentience, Phase 8, or ant-ecology implementation.
