# N17 Iteration 5 - Replay And Control Matrix

Artifact: `n17_loop_replay_and_control_matrix`
Status: `passed`
Acceptance state: `accepted_loop_replay_and_control_matrix_g4_candidate_no_final_ap7`
Output digest: `919af53a36661c52439a7be65bbb0ea18770cdec28c118043e12c399bce5bb8a`

## Main Result

Iteration 5 tries to break the Iteration 4 G3 candidate. It reuses the exact I4 serialized candidate and does not add new loop evidence.

```text
source_loop_digest = 66bd43b80a31c08dd5b8106430cbf4623f0cebc9bbf505c986e2a617846b993f
candidate_trace_legs_unchanged = true
loop_ladder_rung = G4_replay_control_clean_candidate
loop_replay_control_clean = true
closed_loop_claim_allowed = false
final_ap7_supported = false
```

The candidate advances only to a G4 replay/control-clean candidate. I6 must still perform the claim-boundary record before AP7 classification is allowed.

## Replay Mode

I5 replay is artifact-level digest and variant-control verification. It verifies the serialized I4 candidate, row replay digest, trace digest, and declared break variants. It does not rebuild or improve the loop candidate and it is not a full pipeline rerun.

Duplicate replay is recorded as a run-level digest check: `schema_backed_like_row_controls = false` because it compares deterministic row replay digests rather than materializing a separate schema-backed row control case.

For `order_inversion_replay`, `stable` means the false-order variant is reproducibly blocked. It does not mean the inverted order supports closure.

## Replay Matrix

- `artifact_only_replay`: stable
- `snapshot_load_replay`: stable
- `duplicate_replay`: stable
- `order_inversion_replay`: stable

## Break Controls

- `artifact_only_replay_control`: stable
- `snapshot_load_replay_control`: stable
- `duplicate_replay_control`: stable
- `order_inversion_replay_control`: blocked
- `post_hoc_loop_stitching_control`: blocked
- `hidden_external_state_memory_control`: blocked
- `hidden_internal_state_carryover_control`: blocked
- `external_change_not_caused_by_response_control`: blocked
- `feedback_order_inversion_control`: blocked
- `feedback_removed_control`: blocked
- `outbound_response_relabel_control`: blocked
- `one_way_crossing_relabel_control`: blocked
- `semantic_agency_relabel_control`: blocked
- `semantic_intention_relabel_control`: blocked
- `semantic_action_perception_relabel_control`: blocked
- `native_support_relabel_control`: blocked
- `selfhood_identity_relabel_control`: blocked
- `organism_life_relabel_control`: blocked
- `resource_depletion_goal_pursuit_relabel_control`: not_applicable
- `shared_medium_merge_relabel_as_reciprocal_loop_control`: not_applicable

## Highest-Value Controls

```text
external_change_not_caused_by_response = blocked_as_expected
feedback_removed = blocked_as_expected
closed_loop_claim_allowed_when_feedback_removed = false
one_way_crossing_relabel = blocked_as_expected
```

The I4 candidate does not pass when response-caused external change is removed or when the changed external state no longer feeds back into later internal support.

## Claim Boundary

Semantic agency, intention, semantic action/perception, native support, selfhood/identity, organism/life, and unrestricted agency relabels are blocked. Resource/support and shared-medium controls are not applicable because those extensions are not opened in the MVP row.

## Checks

- `source_i4_status_passed`: pass
- `source_i4_candidate_unchanged`: pass
- `artifact_only_replay_stable`: pass
- `snapshot_load_replay_stable`: pass
- `duplicate_replay_stable`: pass
- `order_inversion_blocks_false_order`: pass
- `post_hoc_loop_stitching_blocked`: pass
- `hidden_state_controls_blocked_with_distinct_blockers`: pass
- `external_change_not_caused_by_response_blocked`: pass
- `feedback_removed_blocks_loop_claim`: pass
- `one_way_crossing_still_fails`: pass
- `resource_and_shared_medium_extensions_not_opened`: pass
- `unsafe_claim_flags_false`: pass
- `final_ap7_still_false`: pass
- `pre_i5_pending_controls_resolved`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
