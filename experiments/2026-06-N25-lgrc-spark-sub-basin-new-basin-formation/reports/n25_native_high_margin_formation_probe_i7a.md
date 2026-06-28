# N25 Iteration 7-A - Native High-Margin Formation Probe

Status: `passed`
Acceptance state: `accepted_native_high_margin_core_candidate_bf5_pending_replay_stress`
Output digest: `f3137900d167f264fa30001be5e4f5d3f8991c6af30dc49e4b0aafa3b886bec3`

## Result

```text
native_high_margin_core_candidate_supported = true
support_floor_margin_new_region = 10.000000001
coherence_floor_margin_new_region = 3.3333333336666664
full_module_zero_margin_preserved = true
native_bf5_supported = false
ready_for_iteration_7b_high_margin_replay_controls = true
```

## Geometric Interpretation

I7-A does not change the LGRC9V3 run. It re-examines the native source-current module emitted by the I4/I5 spark-to-expansion path and partitions it into a positive-coherence core plus zero-coherence boundary shell. The core has positive support/coherence margin, so the zero-margin blocker is removed for this core axis. The full module zero-margin record remains, and the core is still attached to the shell/old-basin refinement relation, so this is not BF5 or new-basin formation yet.

## Remaining Blockers

- `full_module_zero_margin_preserved`
- `positive_core_replay_control_pending`
- `new_basin_candidate_not_established`
- `native_flux_routing_or_rate_limiting_surface_not_naturalized`

## Controls

- `positive_core_post_hoc_relabel_control`: `passed`; I7-A may support core-axis margin only
- `boundary_shell_as_support_relabel_control`: `passed`; support/coherence margin remains core-scoped
- `new_basin_independence_relabel_control`: `passed`; new-basin claim remains blocked
- `producer_success_as_native_relabel_control`: `passed`; producer-to-native relabel blocked
- `native_flux_debt_remains_row_local`: `passed`; native flux debt preserved
- `semantic_learning_relabel_rejected`: `passed`; semantic learning relabel blocked
- `agency_relabel_rejected`: `passed`; agency relabel blocked
- `native_support_relabel_rejected`: `passed`; native support relabel blocked
- `phase8_relabel_rejected`: `passed`; Phase 8 relabel blocked

## Checks

- PASS: `i4_native_probe_passed`
- PASS: `i5_native_matrix_passed`
- PASS: `i7_comparative_matrix_passed`
- PASS: `positive_core_margin_supported`
- PASS: `full_module_zero_margin_preserved`
- PASS: `native_lane_only`
- PASS: `bf5_still_blocked`
- PASS: `controls_clean`
- PASS: `artifact_manifest_valid`
- PASS: `source_current_inputs_non_circular`
- PASS: `unsafe_claim_flags_false`
