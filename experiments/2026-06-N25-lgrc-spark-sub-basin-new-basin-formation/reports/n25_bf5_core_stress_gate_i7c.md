# N25 Iteration 7-C - BF5 Core Stress Gate

Status: `passed`
Acceptance state: `accepted_scoped_native_bf5_high_margin_core_sub_basin_stress_candidate`
Output digest: `2af0f3eb0cb463df1565ce73458353f96259bc103e9d9c6198aeef9695595858`

## Result

```text
native_bf5_supported = true
native_bf6_supported = false
bf_ceiling = BF5_native_high_margin_core_sub_basin_stress_candidate
n25_closeout_ceiling = N25-C5_native_high_margin_core_sub_basin_stress_candidate
independent_new_basin_supported = false
ready_for_iteration_8_closeout_and_n26_handoff = true
```

## Geometric Interpretation

I7-C upgrades N25 to a scoped BF5: stress/threshold-backed native high-margin core sub-basin formation inside the inherited 1e-9 flux envelope. It does not support independent new-basin formation or BF6.

This is BF5 only in the scoped high-margin core/sub-basin sense. It is
not independent new-basin formation and not BF6.

## Remaining Limitations

- `independent_new_basin_not_supported`
- `native_flux_routing_above_1e-9_not_naturalized`
- `full_module_zero_margin_preserved`

## Controls

- `bf5_scope_control`: `passed`; BF5 remains scoped; independent new-basin claim blocked
- `support_coherence_stress_control`: `passed`; support/coherence stress gate supports scoped BF5
- `boundary_stress_control`: `passed`; boundary stress gate supports scoped BF5
- `merge_leakage_masquerading_as_new_basin_rejected`: `passed`; broad flux robustness remains blocked
- `producer_success_as_native_relabel_control`: `passed`; producer-to-native relabel blocked
- `native_flux_debt_remains_row_local`: `passed`; native flux debt preserved
- `semantic_learning_relabel_rejected`: `passed`; semantic learning relabel blocked
- `agency_relabel_rejected`: `passed`; agency relabel blocked
- `native_support_relabel_rejected`: `passed`; native support relabel blocked
- `phase8_relabel_rejected`: `passed`; Phase 8 relabel blocked

## Checks

- PASS: `i7a_high_margin_probe_passed`
- PASS: `i7b_core_replay_controls_passed`
- PASS: `support_coherence_stress_supported`
- PASS: `boundary_stress_supported`
- PASS: `merge_leakage_clean_at_native_bound`
- PASS: `native_flux_above_bound_fails_closed`
- PASS: `scoped_bf5_supported`
- PASS: `bf6_still_blocked`
- PASS: `controls_clean`
- PASS: `artifact_manifest_valid`
- PASS: `source_current_inputs_non_circular`
- PASS: `unsafe_claim_flags_false`
