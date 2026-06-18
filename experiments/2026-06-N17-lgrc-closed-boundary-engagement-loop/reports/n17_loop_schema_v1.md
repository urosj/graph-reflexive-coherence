# N17 Iteration 2 - Loop Schema And AP7 Gate

Artifact: `n17_loop_schema_v1`
Status: `passed`
Acceptance state: `accepted_loop_schema_v1_no_ap7_evidence`
Output digest: `911f2910da5cb5899f9bc4b87e52e71177a013725b48b0356a6087a2e237ad72`

## Scope

Iteration 2 freezes the enforceable loop contract. It does not produce loop evidence and does not support AP7.

Allowed language:

```text
AP7 gates frozen
loop schema frozen
one-way null rules frozen
replay and controls frozen
```

Blocked language:

```text
AP7 supported
closed loop demonstrated
action-perception loop proven
agency-like loop established
```

## Core Contract

- `G3` is the first admissible closed-loop rung.
- `G0`, `G1`, and `G2` are fragments and cannot support AP7.
- Closure requires `external -> internal -> external -> later internal`.
- The fourth leg, `external_feedback_to_internal_trace`, is the AP7 hinge.
- External change after a response is insufficient unless the response caused it.
- Feedback removal must force `closed_loop_claim_allowed = false`.

## AP7 Gates

- `g3_or_higher`
- `four_trace_legs_present`
- `four_trace_legs_source_backed`
- `monotonic_phase_order_valid`
- `response_caused_external_change`
- `external_change_counterfactual_blocks_spontaneous_change`
- `later_internal_depends_on_changed_external_state`
- `feedback_removed_control_passed`
- `one_way_crossing_null_blocked`
- `dependency_trace_complete`
- `replay_digest_valid`
- `budget_validity_passed`
- `controls_passed`
- `claim_boundary_clean`
- `source_registry_backed`
- `no_absolute_paths`

## Controls

- `artifact_only_replay_control`: requires replay from artifact state rather than hidden runtime state
- `snapshot_load_replay_control`: requires snapshot/load replay stability
- `duplicate_replay_control`: requires duplicate replay stability
- `order_inversion_replay_control`: requires order-inversion replay to block post-hoc ordering
- `post_hoc_loop_stitching_control`: blocks unordered compatible events from being narrated as closure
- `hidden_external_state_memory_control`: blocks hidden external-state carryover as later feedback
- `hidden_internal_state_carryover_control`: blocks hidden internal-state carryover as loop dependence
- `outbound_response_relabel_control`: blocks naming an outbound change action without causal closure
- `external_change_not_caused_by_response_control`: blocks external change that follows response but is not caused by it
- `feedback_order_inversion_control`: blocks t3 feedback appearing before t2 response-caused external change
- `feedback_removed_control`: removing changed-external feedback must force closed_loop_claim_allowed false
- `one_way_crossing_relabel_control`: blocks N16-style crossing from being relabeled as AP7
- `semantic_agency_relabel_control`: blocks agency-language promotion
- `semantic_intention_relabel_control`: blocks intention-language promotion
- `semantic_action_perception_relabel_control`: blocks semantic action/perception promotion
- `native_support_relabel_control`: blocks native support promotion
- `selfhood_identity_relabel_control`: blocks selfhood and identity-acceptance promotion
- `organism_life_relabel_control`: blocks organism, life, and biological-behavior promotion; split from the plan's claim-boundary text so the validator has an explicit flag
- `resource_depletion_goal_pursuit_relabel_control`: blocks resource depletion from being relabeled as semantic goal pursuit in resource/support extensions
- `shared_medium_merge_relabel_as_reciprocal_loop_control`: blocks basin merge or leakage from being relabeled as shared-medium reciprocal closure

Replay controls are status-backed: the replay controls must pass and their backing replay status fields must be `stable`.

Extension controls for resource/support and shared-medium rows are frozen now. MVP rows may mark those extension controls `not_applicable`.

## Policy Canonical Sources

Config files are the canonical policy artifacts. The schema records their paths and digests, and the generated checks verify consistency between schema summaries and config payloads.

## Config Files

- `source_registry`: `experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/configs/n17_source_registry.json`
- `loop_policy`: `experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/configs/n17_loop_policy_v1.json`
- `budget_limits`: `experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/configs/n17_budget_limits_v1.json`
- `control_variants`: `experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/configs/n17_control_variants_v1.json`
- `replay_policy`: `experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/configs/n17_replay_policy_v1.json`

## Plan To Schema Mapping

- `loop_ladder_rung` -> `loop_rung`: same value family G0-G7; implementation keeps numeric loop_rung_index separately
- `monotonic_phase_ordering` -> `monotonic_phase_order`: boolean row field plus phase_timing map
- `external_to_internal_trace` -> `external_to_internal_trace`: mandatory trace leg
- `internal_response_trace` -> `internal_response_trace`: mandatory trace leg
- `response_to_external_change_trace` -> `response_to_external_change_trace`: mandatory trace leg; must be response-caused
- `external_feedback_to_internal_trace` -> `external_feedback_to_internal_trace`: mandatory AP7 hinge leg
- `feedback_removed_control` -> `controls.feedback_removed_control`: control row field, plus feedback_removed_control_changes_result
- `artifact-only replay` -> `artifact_only_replay_status and controls.artifact_only_replay_control`: replay is represented both as a stable status and a status-backed control

## Iteration 3 Handoff

Iteration 3 should run the one-way crossing active null and confirm that N16-style boundary crossing cannot pass this schema as AP7.

## Checks

- `source_inventory_passed`: pass
- `g3_first_admissible_rung_frozen`: pass
- `g0_g1_g2_closed_loop_claim_forbidden`: pass
- `one_way_crossing_promotion_blocked`: pass
- `four_trace_legs_mandatory`: pass
- `phase_ordering_frozen`: pass
- `response_caused_external_change_required`: pass
- `feedback_removed_control_frozen`: pass
- `ap7_gates_fail_closed`: pass
- `mvp_family_perturbation_response_recovery_only`: pass
- `one_way_null_family_classified_as_null_not_evidence_family`: pass
- `loop_specific_controls_frozen`: pass
- `extension_controls_frozen`: pass
- `replay_controls_status_backed`: pass
- `replay_digest_admissibility_critical`: pass
- `config_schema_policy_consistency`: pass
- `unsafe_claim_flags_forced_false`: pass
- `config_files_materialized`: pass
- `validator_script_present`: pass
- `no_loop_evidence_rows_generated`: pass
- `no_final_ap7_claim`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
