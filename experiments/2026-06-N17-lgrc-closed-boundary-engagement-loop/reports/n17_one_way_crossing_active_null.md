# N17 Iteration 3 - One-Way Crossing Active Null

Artifact: `n17_one_way_crossing_active_null`
Status: `passed`
Acceptance state: `accepted_one_way_crossing_active_null_no_ap7`
Output digest: `3f70a70db68edf537d20f4b1478e0b53a7012510c7357539b3af8385fef30635`

## Main Result

Iteration 3 builds a strong near-miss and rejects it as AP7.

```text
row_decision = supported
row_type = active_null
active_null_decision = supported_as_active_null_rejection
loop_ladder_rung = G2
closed_loop_claim_allowed = false
final_ap7_supported = false
failure_mode = one_way_crossing_is_not_closed_loop
```

## Trace Read

- `external_to_internal_trace`: present and source-backed.
- `internal_response_trace`: present and source-backed.
- `response_to_external_change_trace`: present as a tempting marker, but not validated as response-caused external change.
- `external_feedback_to_internal_trace`: explicitly absent.

## Requirements Satisfied

- `external_to_internal_trace_recorded`
- `internal_support_update_recorded`
- `bounded_response_marker_recorded_as_tempting_near_miss`
- `one_way_crossing_relabel_control_blocks_ap7`
- `unsafe_claim_flags_forced_false`
- `artifact_replay_stable_for_active_null`

## Requirements Failed

- `external_feedback_to_internal_trace_absent`
- `loop_closure_evidence_absent`
- `G3_not_reached`
- `response_caused_external_change_not_validated`
- `later_internal_dependence_on_changed_external_state_absent`

## Interpretation

This row demonstrates boundary crossing and internal update fragments, but it does not demonstrate closed boundary engagement because no response-caused external change feeds back into later internal support.

## Checks

- `schema_status_passed`: pass
- `source_inventory_status_passed`: pass
- `strong_near_miss_contains_crossing_internal_update_and_response_marker`: pass
- `assigned_below_g3`: pass
- `missing_feedback_leg_explicit`: pass
- `replay_digest_binds_schema_and_loop_policy`: pass
- `one_way_relabel_control_blocks_ap7`: pass
- `iteration_4_evidence_not_introduced`: pass
- `closed_loop_claim_allowed_false`: pass
- `final_ap7_supported_false`: pass
- `unsafe_claim_flags_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
