# N18 Long-Horizon Schema V1

Status: `passed`

Acceptance state: `accepted_long_horizon_schema_v1_no_ap8_evidence`

Output digest: `53918702f07a4ccb613149f839855a855db912646ef7c53e45679d3383bcf760`

## Summary

Iteration 2 freezes the AP8 stress-row schema, horizon policy, replay
policy, budget policy, controls, and claim gate. It does not generate
positive long-horizon evidence and it does not support final AP8.

```text
rows = 0
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
```

## Stress Ladder

| Rung | Meaning |
| --- | --- |
| `L0` | source inventory and AP8 contract only |
| `L1` | short-horizon AP7 replay remains source-current |
| `L2` | longer horizon replay remains source-current without added perturbation |
| `L3` | support withdrawal/restoration and proxy perturbation remain bounded |
| `L4` | route/context reversal and memory relaxation remain bounded |
| `L5` | environment/resource and shared-medium perturbation remain separable |
| `L6` | artifact-only reconstruction and replay controls pass |
| `L7` | claim-clean AP8 candidate, unsafe promotions blocked |

## AP8 Required Gates

```json
[
  "source_rows_pinned",
  "source_claim_ceilings_preserved",
  "evidence_branch_artifact_only",
  "horizon_envelope_declared",
  "horizon_policy_satisfied",
  "all_required_trace_axes_present",
  "linked_trace_continuity_present",
  "cross_axis_continuity_evidence_present",
  "long_horizon_continuity_present",
  "budget_valid",
  "artifact_only_reconstruction_passed",
  "duplicate_replay_passed",
  "snapshot_load_replay_passed",
  "stale_state_control_passed",
  "single_axis_stale_controls_passed",
  "post_hoc_stitching_control_passed",
  "drift_as_autonomy_control_passed",
  "b4c5_relabel_controls_passed",
  "stress_controls_passed",
  "unsafe_claim_flags_false",
  "phase8_not_opened",
  "native_support_not_opened"
]
```

## Config Files

| Config | Path | SHA-256 |
| --- | --- | --- |
| `source_registry` | `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/configs/n18_source_registry.json` | `712af2edfaded3c04bb0582e3dad26fc213ecccf5dc896b6f1eddc67b92be031` |
| `horizon_policy` | `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/configs/n18_horizon_policy_v1.json` | `2aae1cbb8786486d91c6e5dd59cd00a5e1aaaba768e6efa9394874497d89d998` |
| `stress_policy` | `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/configs/n18_stress_policy_v1.json` | `9016fb30087b7dc40b11d6ba2014e72093875ee1e4d563918184e6c0e6d626c9` |
| `budget_limits` | `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/configs/n18_budget_limits_v1.json` | `8e5e87445c70f45b52407da34af32d46980d09b98fe7eebf889d10a5010e4cfa` |
| `control_variants` | `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/configs/n18_control_variants_v1.json` | `1099bb463fdb3147cf6011ee3e41fea22dc1330b3662ea88691edee0747b8de1` |
| `replay_policy` | `experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/configs/n18_replay_policy_v1.json` | `e9f0ab3e4131e9d6c34003cf1e8136776c666455ef71d8df73f77ec97048c436` |

## Interpretation

The schema makes AP8 fail closed: a row cannot allow AP8 unless source
rows are pinned, claim ceilings are preserved, the artifact-only branch
is declared, the horizon envelope is explicit, horizon policy passes,
all trace axes are present, linked and cross-axis continuity are shown,
budget is valid, replay/reconstruction, order-inversion, stale-axis,
drift/autonomy, and B4/C5 relabel controls pass, unsafe claim flags
remain false, and Phase 8/native support remain unopened.

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_inventory_ready` | `true` | `{"output_digest": "b9e45e7fb4e2c90fac206e1b2c666b425eec18b02bee6cd48685fc705000a2bf", "path": "experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/outputs/n18_long_horizon_source_inventory.json", "ready_for_iteration_2_schema": true, "sha256": "743a7d91cc63c9fbd49fa33c1f01404727eecb4225bc39f361817fce7d0c3546"}` |
| `required_config_files_written` | `true` | `["budget_limits", "control_variants", "horizon_policy", "replay_policy", "source_registry", "stress_policy"]` |
| `stress_ladder_frozen` | `true` | `{"L0": "source inventory and AP8 contract only", "L1": "short-horizon AP7 replay remains source-current", "L2": "longer horizon replay remains source-current without added perturbation", "L3": "support withdrawal/restoration and proxy perturbation remain bounded", "L4": "route/context reversal and memory relaxation remain bounded", "L5": "environment/resource and shared-medium perturbation remain separable", "L6": "artifact-only reconstruction and replay controls pass", "L7": "claim-clean AP8 candidate, unsafe promotions blocked"}` |
| `ap8_gates_fail_closed` | `true` | `["source_rows_pinned", "source_claim_ceilings_preserved", "evidence_branch_artifact_only", "horizon_envelope_declared", "horizon_policy_satisfied", "all_required_trace_axes_present", "linked_trace_continuity_present", "cross_axis_continuity_evidence_present", "long_horizon_continuity_present", "budget_valid", "artifact_only_reconstruction_passed", "duplicate_replay_passed", "snapshot_load_replay_passed", "stale_state_control_passed", "single_axis_stale_controls_passed", "post_hoc_stitching_control_passed", "drift_as_autonomy_control_passed", "b4c5_relabel_controls_passed", "stress_controls_passed", "unsafe_claim_flags_false", "phase8_not_opened", "native_support_not_opened"]` |
| `artifact_only_branch_visible` | `true` | `{"evidence_branch": "artifact_only", "native_branch_opened": false, "phase8_branch_opened": false}` |
| `horizon_envelope_policy_frozen` | `true` | `{"horizon_extrapolation_allowed": false, "max_supported_horizon": "not_established_until_iteration_4"}` |
| `linked_trace_continuity_policy_frozen` | `true` | `["support_to_regulation", "regulation_to_selection", "selection_to_proxy", "proxy_to_boundary", "boundary_to_loop_feedback", "memory_context_to_selection"]` |
| `cross_axis_continuity_policy_frozen` | `true` | `{"field": "cross_axis_continuity_evidence", "must_bind_linked_trace_continuity": true, "required_for_ap8": true, "trace_presence_alone_is_insufficient": true}` |
| `single_axis_stale_controls_frozen` | `true` | `["stale_support_state_control", "stale_memory_context_control", "stale_selection_context_control", "stale_proxy_target_control", "stale_boundary_state_control", "stale_loop_feedback_control"]` |
| `order_inversion_control_frozen` | `true` | `"order_inversion_control blocks inverted or shuffled horizon traces"` |
| `b4c5_relabel_controls_frozen` | `true` | `["b4c5_original_reverse_replay_relabel_control", "general_symmetric_native_multibasin_relabel_control"]` |
| `claim_boundary_names_aligned` | `true` | `[]` |
| `ap8_outcome_taxonomy_frozen` | `true` | `{"AP8_blocked": "core continuity, budget, replay, or claim controls fail", "AP8_supported_full": "all required stress families pass under the declared horizon and stress envelope", "AP8_supported_limited": "long-horizon replay plus some stress families pass while other families are deferred or blocked"}` |
| `config_embedded_policy_consistency` | `true` | `"embedded policy sections match generated config payloads"` |
| `baseline_replay_cannot_support_ap8` | `true` | `"Iteration 3 baseline replay can be L1 only."` |
| `phase8_native_flags_false` | `true` | `{"native_support_opened": false, "phase8_opened": false}` |
| `no_final_ap8_claim` | `true` | `"Iteration 2 freezes rules only."` |
| `no_absolute_paths` | `true` | `"portable relative paths only"` |
