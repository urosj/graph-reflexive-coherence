# N25 Iteration 7 - Comparative Stress And Formation Boundary Matrix

Status: `passed`
Acceptance state: `accepted_comparative_bf4_boundary_matrix_bf5_blocked_n26_ready`
Output digest: `0cf5c7d42e775a2e34a9cbb6bc6e31a89b2aae09e1e0785b590efd24b18e8c79`

## Result

```text
native_bf4_candidate_supported = true
native_bf5_supported = false
producer_assisted_bf4_candidate_supported = true
producer_assisted_bf5_supported = false
bf5_or_stronger_supported = false
n25_closeout_ceiling = N25-C4_comparative_bf4_with_producer_scaffold_debt
ready_for_iteration_8_closeout_and_n26_handoff = true
```

## Geometric Interpretation

I7 separates the geometric axes. Boundary distinguishability has margin, and merge/leakage controls stay clean. The producer-assisted lane improves flux scheduling by windowing larger attempted flux into native-bound packets. But the formed region itself remains exactly at the support/coherence floor, and the producer does not create a new substrate-carried basin. Therefore I7 strengthens the diagnosis of what is missing rather than upgrading N25 to BF5/BF6.

## Stress Axes

- Boundary distinguishability: supported as an axis, but not enough for BF5.
- Support/coherence: zero-margin in both native and producer-assisted lanes; blocks BF5/BF6.
- Flux/merge/leakage: producer windowing helps attempted flux up to `1e-8`, but native bound remains `1e-9`.

## Naturalization Targets

- `native_flux_routing_or_rate_limiting_surface`: `not_naturalized` (producer_scaffold_supported)
- `positive_support_coherence_margin_for_formed_region`: `not_supported_zero_margin` (required_for_BF5_BF6)
- `new_basin_independence_beyond_sub_basin_differentiation`: `not_supported_sub_basin_candidate_only` (required_for_new_basin_candidate)

## Controls

- `producer_assisted_success_does_not_overwrite_native_failure`: `passed`; native BF5/BF6 remain blocked
- `native_flux_debt_remains_row_local`: `passed`; producer flux help stays producer-mediated
- `producer_success_as_native_relabel_control`: `passed`; producer-to-native relabel blocked
- `merge_leakage_masquerading_as_new_basin_rejected`: `passed`; new-basin overclaim blocked
- `non_replayable_transient_rejected`: `passed`; transient overclaim blocked
- `producer_threshold_relaxation_control`: `passed`; threshold relaxation blocked
- `semantic_learning_relabel_rejected`: `passed`; semantic learning relabel blocked
- `semantic_choice_relabel_rejected`: `passed`; semantic choice relabel blocked
- `agency_relabel_rejected`: `passed`; agency relabel blocked
- `native_support_relabel_rejected`: `passed`; native support relabel blocked
- `phase8_relabel_rejected`: `passed`; Phase 8 relabel blocked
- `ant_ecology_relabel_rejected`: `passed`; ant ecology relabel blocked

## Checks

- PASS: `i1_inventory_passed`
- PASS: `i2_schema_passed`
- PASS: `i3_active_nulls_passed`
- PASS: `i4_native_probe_passed`
- PASS: `i5_native_matrix_passed`
- PASS: `i6_producer_probe_passed`
- PASS: `native_and_producer_lane_ceiling_preserved`
- PASS: `boundary_stress_axis_recorded`
- PASS: `support_coherence_zero_margin_blocks_bf5`
- PASS: `producer_flux_help_not_native`
- PASS: `naturalization_targets_recorded`
- PASS: `controls_clean`
- PASS: `artifact_manifest_valid`
- PASS: `source_current_inputs_non_circular`
- PASS: `unsafe_claim_flags_false`
