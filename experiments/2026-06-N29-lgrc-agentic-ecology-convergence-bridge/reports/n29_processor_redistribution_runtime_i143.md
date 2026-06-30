# Prototype D I14.3 processor_redistribution_runtime_prototype

## Result

```text
status = passed
acceptance_state = accepted_processor_redistribution_motif_direct_runtime_candidate_pending_i14b_i14c
runtime_row_id = n29_i14_3_processor_redistribution_motif
motif_id = processor_redistribution_motif
row_decision = partial
row_decision_scope = direct_runtime_candidate_created_pending_i14b_controls_and_i14c_replay_stress
claim_ceiling = direct_processor_redistribution_runtime_candidate_pending_i14b_i14c
canonical_i14a_output_digest = aeb89e95e03cf7f64e395375db8012b4b603491a7dfc1bc95c32ae55a46923cc
direct_runtime_support_claim_allowed = false
control_backed_runtime_supported = false
replay_stress_backed_runtime_supported = false
output_digest = 998950d34cce9ed539d5cc6ed49a89438b4d0d5c90146ab5b9c0950fada0944d
```

## Geometric Interpretation

focal basin stays bounded while one route lobe gains capacity and the opposed route lobe loses capacity under one source-current policy.

The runtime candidate is source-current in the N28 sense: it carries the source runtime traces, threshold record, focal stability trace, capacity attribution trace, and merge/leakage trace into a new N29 runtime-candidate artifact. It is not accepted by relabelling the N28 row as N29 success.

Key capacity deltas:

```text
environment_capacity_delta = 0.003
neighbor_support_delta = 0.008
neighbor_distinguishability_delta = 0.016
neighbor_boundary_delta = -0.01
merge_or_leakage_value = 0.017
merge_or_leakage_ceiling = 0.025
```

Route-lobe redistribution basis:

```text
route_lobe_a_capacity_delta = 0.07
route_lobe_b_capacity_delta = -0.068
aggregate_only_redistribution_allowed = false
```

## Claim Boundary

This row is a direct runtime candidate pending I14-B controls and I14-C replay/stress. It does not claim resource economy, cooperation, exploitation, closed environmental circulation, biological agency, native support, or agentic ecology runtime success.

## Checks

| Check | Passed |
| --- | --- |
| `i14_source_passed` | `true` |
| `i14a_schema_passed` | `true` |
| `canonical_i14a_digest_recorded` | `true` |
| `direct_target_matches_schema` | `true` |
| `direct_target_is_runtime_candidate_eligible` | `true` |
| `source_n28_row_id_matches_expected` | `true` |
| `source_n28_regime_matches_expected` | `true` |
| `source_n28_row_supported` | `true` |
| `source_n28_row_is_source_current` | `true` |
| `source_current_inputs_non_empty` | `true` |
| `source_manifest_paths_exist` | `true` |
| `source_manifest_sha256_matches` | `true` |
| `runtime_artifact_written` | `true` |
| `runtime_artifact_manifest_sha256_matches` | `true` |
| `runtime_artifact_digest_recorded` | `true` |
| `required_runtime_fields_present` | `true` |
| `thresholds_declared_before_use` | `true` |
| `producer_visibility_declared` | `true` |
| `hidden_producer_state_not_used` | `true` |
| `focal_support_floor_preserved` | `true` |
| `focal_coherence_floor_preserved` | `true` |
| `focal_stability_preserved` | `true` |
| `motif_geometry_matches_expected_shape` | `true` |
| `aggregate_only_redistribution_control_present` | `true` |
| `i14_2_leakage_caveat_recorded_when_needed` | `true` |
| `n28_not_relabelled_as_n29_runtime` | `true` |
| `controls_present_but_not_run` | `true` |
| `replay_present_but_not_run` | `true` |
| `stress_present_but_not_run_or_not_inferred` | `true` |
| `direct_runtime_support_claim_not_allowed_yet` | `true` |
| `unsafe_claim_flags_false` | `true` |
