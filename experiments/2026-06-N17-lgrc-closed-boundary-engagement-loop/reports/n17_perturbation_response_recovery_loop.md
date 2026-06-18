# N17 Iteration 4 - Perturbation-Response-Recovery Loop

Artifact: `n17_perturbation_response_recovery_loop`
Status: `passed`
Acceptance state: `accepted_perturbation_response_recovery_g3_candidate_pending_controls_no_ap7`
Output digest: `66bd43b80a31c08dd5b8106430cbf4623f0cebc9bbf505c986e2a617846b993f`

## Main Result

Iteration 4 records the first positive minimal G3 candidate, but keeps AP7 blocked until Iteration 5 replay and controls.

```text
row_decision = supported
row_type = loop_candidate
loop_family = perturbation_response_recovery_loop
loop_ladder_rung = G3_candidate
closed_loop_candidate = true
closed_loop_claim_allowed = false
final_ap7_supported = false
```

## Trace Read

- `external_to_internal_trace`: present and source-backed.
- `internal_response_trace`: present and source-backed.
- `response_to_external_change_trace`: present, source-backed, and recorded as response-caused candidate evidence pending I5.
- `external_feedback_to_internal_trace`: present and source-backed as candidate later internal dependence pending I5 hidden-state and feedback-removal controls.

## Contrast With Iteration 3

```text
i3_missing_feedback_leg = true
i4_feedback_leg_present = true
i3_closed_loop_claim_allowed = false
i4_closed_loop_claim_allowed = false
```

Iteration 3 stopped at G2. Iteration 4 adds candidate response-caused external change and candidate later internal support dependence on that changed external state. Those are the G3 hinge, but their AP7 gates remain false until I5 controls pass.

## One-Step Recovery Distinction

```text
one_step_recovery_only = false
closed_boundary_engagement_loop_candidate = true
reason = candidate_changed_external_state_feeds_later_internal_support
```

This does not make the row final AP7 evidence. It is a candidate until I5 replay, hidden-state, post-hoc stitching, order-inversion, external-change-not-caused-by-response, and feedback-removal controls pass.

## AP7 Gate Boundary

```text
response_caused_external_change = false
external_change_counterfactual_blocks_spontaneous_change = false
later_internal_depends_on_changed_external_state = false
feedback_removed_control_passed = false
replay_digest_valid = false
controls_passed = false
```

These gates are false because Iteration 4 records candidate traces only. Iteration 5 must validate causality, counterfactuals, hidden state exclusion, replay, and feedback removal before any AP7 classification can be allowed.

## Requirements Satisfied

- `minimal_perturbation_response_recovery_loop_built`
- `all_four_ordered_trace_legs_recorded`
- `contrast_with_i3_one_way_null_recorded`
- `response_caused_external_change_candidate_recorded`
- `later_internal_dependence_candidate_recorded`
- `loop_closure_distinguished_from_one_step_recovery`
- `resource_support_and_shared_medium_extensions_not_opened`
- `unsafe_claim_flags_forced_false`

## Pending Before AP7

- `artifact_only_replay_control_pending_i5`
- `snapshot_load_replay_control_pending_i5`
- `duplicate_replay_control_pending_i5`
- `order_inversion_control_pending_i5`
- `post_hoc_loop_stitching_control_pending_i5`
- `hidden_state_controls_pending_i5`
- `external_change_not_caused_by_response_control_pending_i5`
- `feedback_removed_control_pending_i5`

## Claim Boundary

The row remains artifact-level only. It does not support agency, intention, semantic action, semantic perception, semantic goal ownership, selfhood, identity acceptance, native support, organism or life claims, fully native integration, or unrestricted agency.

## Checks

- `schema_status_passed`: pass
- `source_inventory_status_passed`: pass
- `i3_active_null_available_for_contrast`: pass
- `mvp_family_only`: pass
- `g3_candidate_trace_present`: pass
- `monotonic_phase_order_valid`: pass
- `response_caused_external_change_marked_candidate_pending_i5`: pass
- `later_internal_feedback_dependence_marked_candidate_pending_i5`: pass
- `distinguished_from_one_step_recovery`: pass
- `ap7_causality_and_feedback_gates_false_until_i5`: pass
- `i4_keeps_final_ap7_blocked`: pass
- `unsafe_claim_flags_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
