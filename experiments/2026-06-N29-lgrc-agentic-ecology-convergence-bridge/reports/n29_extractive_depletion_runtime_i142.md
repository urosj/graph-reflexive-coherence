# Prototype D I14.2 extractive_depletion_runtime_prototype

## Result

```text
status = passed
acceptance_state = accepted_extractive_depletion_motif_direct_runtime_candidate_pending_i14b_i14c
runtime_row_id = n29_i14_2_extractive_depletion_motif
motif_id = extractive_depletion_motif
row_decision = partial
row_decision_scope = direct_runtime_candidate_created_pending_i14b_controls_and_i14c_replay_stress
claim_ceiling = direct_extractive_depletion_runtime_candidate_with_leakage_exceedance_caveat_pending_i14b_i14c
canonical_i14a_output_digest = aeb89e95e03cf7f64e395375db8012b4b603491a7dfc1bc95c32ae55a46923cc
direct_runtime_support_claim_allowed = false
control_backed_runtime_supported = false
replay_stress_backed_runtime_supported = false
output_digest = 4e42198b18f34700956b53b5873a56639c80b774259ebfbfda5d18168a4e57d0
```

## Geometric Interpretation

focal basin stays above support/coherence/stability floors while the neighboring capacity shell loses support, distinguishability, boundary integrity, and basin-forming capacity.

The runtime candidate is source-current in the N28 sense: it carries the source runtime traces, threshold record, focal stability trace, capacity attribution trace, and merge/leakage trace into a new N29 runtime-candidate artifact. It is not accepted by relabelling the N28 row as N29 success.

Key capacity deltas:

```text
environment_capacity_delta = -0.069
neighbor_support_delta = -0.063
neighbor_distinguishability_delta = -0.077
neighbor_boundary_delta = -0.081
merge_or_leakage_value = 0.033
merge_or_leakage_ceiling = 0.025
```

Leakage caveat:

```text
leakage_record_status = extractive_mechanism_exceedance_caveat
merge_leakage_value = 0.033
merge_leakage_ceiling = 0.025
merge_leakage_below_ceiling = false
clean_bounded_leakage_claim_allowed = false
```

The over-ceiling leakage is interpreted only as extractive-mechanism evidence for this candidate. It is not clean bounded leakage and must be tested by I14-B/I14-C before stronger support can be claimed.

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
