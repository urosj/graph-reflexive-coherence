# N22 Iteration 4-A - Susceptibility Dose / Boundary Probe

Status: `passed`

Acceptance state: `accepted_dose_boundary_su2_extension_pending_replay_controls`

Output digest: `bfc7856e5685fab47383f3e03e0311f6f140841667a5f36a75b7e6f2b5cd5d6d`

## Summary

Iteration 4-A keeps the I4 fixture and thresholds fixed, then sweeps a
declared route_b prior-interaction dose ladder. It does not retune I4,
replace I4, or open durable geometry modification.

No prior interaction and 0.03 packet dose fail closed; 0.08 and 0.14 packet doses produce route-local SU2 deltas; 0.20 produces a larger delta but crosses the center coherence floor.

I4 showed one source-current route-local delta. I4-A shows the delta has a bounded dose region and a fail-closed high-dose boundary, so success is not a label-only or one-value artifact.

## Dose Rows

| Dose | Decision | Classification | Target Delta | Peer Delta | Re-entry Ratio | Coherence Gate |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `0.0` | `rejected` | `no_prior_interaction_control_failed_closed` | 0.000000000000 | 0.000000000000 | 0.000000000000 | `changed_within_allowed_delta_above_floor` |
| `0.03` | `rejected` | `below_delta_floor_failed_closed` | 0.030000000000 | 0.000000000000 | 0.333333333333 | `changed_within_allowed_delta_above_floor` |
| `0.08` | `partial` | `bounded_source_current_SU2_candidate` | 0.080000000000 | 0.000000000000 | 0.500000000000 | `changed_within_allowed_delta_above_floor` |
| `0.14` | `partial` | `bounded_source_current_SU2_candidate` | 0.140000000000 | 0.000000000000 | 0.714285714286 | `changed_within_allowed_delta_above_floor` |
| `0.2` | `blocked` | `out_of_scope_drift_failed_closed` | 0.200000000000 | 0.000000000000 | 0.800000000000 | `crossed_floor` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_passed` | `true` | accepted_source_handoff_inventory_no_susceptibility_evidence |
| `i2_schema_passed` | `true` | accepted_susceptibility_schema_frozen_no_positive_evidence |
| `i3_active_nulls_passed` | `true` | accepted_active_nulls_fail_closed_no_positive_evidence |
| `i4_minimal_probe_passed` | `true` | accepted_minimal_source_current_su2_candidate_pending_replay_controls |
| `threshold_policy_matches_i4` | `true` | {"boundary_active_degree_floor": 9, "coherence_floor": 9.85, "declared_before_use": true, "dose_rows_declared_before_use": [{"dose_id": "... |
| `dose_ladder_declared_before_use` | `true` | [{"dose_id": "dose_00_no_prior_interaction_control", "expected_role": "no_prior_interaction_control", "prior_interaction_packet_amount": ... |
| `artifact_manifest_non_empty` | `true` | 87 |
| `artifact_hashes_match` | `true` | 87 |
| `two_positive_su2_rows` | `true` | ["n22_i4a_dose_08_i4_reference", "n22_i4a_dose_14_stronger_bounded"] |
| `below_threshold_and_no_prior_fail_closed` | `true` | [{"classification": "no_prior_interaction_control_failed_closed", "coherence_status": "changed_within_allowed_delta_above_floor", "dose_i... |
| `out_of_scope_high_dose_blocks` | `true` | [{"classification": "no_prior_interaction_control_failed_closed", "coherence_status": "changed_within_allowed_delta_above_floor", "dose_i... |
| `positive_rows_reject_global_drift` | `true` | [{"global_drift_rejected": true, "peer_prior_route": "route_peer_edge_1", "peer_route_delta": 0.0, "same_prior_interaction_budget": true,... |
| `all_rows_claim_allowed_false` | `true` | ["rejected", "rejected", "partial", "partial", "blocked"] |
| `durable_geometry_not_supported` | `true` | I4-A is dose boundary only |
| `unsafe_flags_all_false` | `true` | all dose rows |
| `artifact_paths_repository_relative` | `true` | relative paths only |

## Claim Boundary

The result strengthens provisional SU2 input evidence only. Replay-backed SU3, durable SU4, transfer SU5, SU6, final N22, and the N21 ND6 bridge remain blocked.

Semantic learning, choice, agency, native support, sentience, Phase 8,
and ant-ecology implementation remain blocked.
