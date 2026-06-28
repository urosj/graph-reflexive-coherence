# N25 Iteration 7-B - High-Margin Core Replay And Controls

Status: `passed`
Acceptance state: `accepted_high_margin_core_replay_control_backed_bf5_stress_ready`
Output digest: `dc33c7d5ee0d59152027753c8f287fab381b283bf4ee6910039074155c1cf5ce`

## Result

```text
native_high_margin_core_replay_control_supported = true
core_replay_stable = true
artifact_reconstruction_stable = true
native_bf5_supported = false
ready_for_iteration_7c_bf5_stress_gate = true
```

## Geometric Interpretation

I7-B replays and reconstructs the I7-A positive-core partition. The same three coherence-positive core nodes, two zero-coherence shell nodes, and core/shell boundary relation are recovered. This removes the core replay/control blocker, but BF5 still waits for a stress gate.

## Controls

- `positive_core_post_hoc_relabel_control`: `passed`; core remains stress-eligible but scope-limited
- `core_partition_replay_control`: `passed`; positive_core_replay_control_pending removed
- `boundary_shell_as_support_relabel_control`: `passed`; support/coherence margin remains core-scoped
- `new_basin_independence_relabel_control`: `passed`; independent new-basin claim remains blocked
- `non_replayable_transient_rejected`: `passed`; transient interpretation blocked
- `producer_success_as_native_relabel_control`: `passed`; producer-to-native relabel blocked
- `native_flux_debt_remains_row_local`: `passed`; native flux debt preserved
- `semantic_learning_relabel_rejected`: `passed`; semantic learning relabel blocked
- `agency_relabel_rejected`: `passed`; agency relabel blocked
- `native_support_relabel_rejected`: `passed`; native support relabel blocked
- `phase8_relabel_rejected`: `passed`; Phase 8 relabel blocked

## Checks

- PASS: `i5_native_matrix_passed`
- PASS: `i7a_high_margin_probe_passed`
- PASS: `core_replay_stable`
- PASS: `artifact_reconstruction_stable`
- PASS: `controls_clean`
- PASS: `bf5_still_pending_stress`
- PASS: `artifact_manifest_valid`
- PASS: `source_current_inputs_non_circular`
- PASS: `unsafe_claim_flags_false`
