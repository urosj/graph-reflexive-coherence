# N22 Iteration 7 - Replay And Control Matrix

Status: `passed`

Acceptance state: `accepted_controlled_producer_mediated_su5_candidate_no_final_closeout`

Output digest: `243d068ba53715b30a40312d8f5c6a2e512f41a23c1773e0e7abb620dce963ef`

## Summary

I7 separates the consumptive packet-readout branch from the producer-mediated carrier branch. Packet evidence remains SU3-limited; carrier evidence becomes I7-consumable producer-mediated SU5 candidate evidence pending I8 closeout.

I7 does not close final SU5, SU6, N22, or the N21 ND6 bridge. It does not support native route-conductance memory, semantic learning, choice, agency, native support, sentience, Phase 8, or ant ecology.

```text
packet_branch_i7_consumable_su3_count = 4
packet_branch_blocked_before_su5_count = 1
carrier_branch_i7_consumable_su5_count = 3
i7_consumable_highest_su_rung = SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate
recommended_iteration8_closeout_candidate = N22-C5_producer_mediated_bounded_candidate
n22_closeout_ladder_rung_assigned = false
final_n22_supported = false
n21_nd6_bridge_status = not_supported
```

## Packet Branch

| Row | Decision | I7 Rung | Limited SU3 | SU5 |
| --- | --- | --- | --- | --- |
| `i4_minimal_route_b` | `partial` | `SU3_consumptive_transfer_readout_expression` | `true` | `false` |
| `dose_08_i4_reference` | `partial` | `SU3_consumptive_transfer_readout_expression` | `true` | `false` |
| `dose_14_stronger_bounded` | `partial` | `SU3_consumptive_transfer_readout_expression` | `true` | `false` |
| `single_route_b_reference` | `partial` | `SU3_consumptive_transfer_readout_expression` | `true` | `false` |
| `complementary_split_route_b_adjacent` | `blocked` | `blocked_before_SU5_route_specific_margin_failure` | `false` | `false` |

## Carrier Branch

| Row | Decision | I7 Rung | Min I6-B Ratio | Min I6-B Margin | Final SU5 |
| --- | --- | --- | ---: | ---: | --- |
| `band_buffered_return_carrier` | `supported` | `SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate` | 1.000000 | 0.070000 | `false` |
| `neutral_reservoir_buffered_carrier` | `supported` | `SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate` | 1.000000 | 0.120000 | `false` |
| `route_conductance_geometry_carrier` | `supported` | `SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate` | 1.000000 | 0.180000 | `false` |

## Replay Matrix

| Replay | Status | Detail |
| --- | --- | --- |
| `artifact_only_reconstruction` | `passed` | source output digests recompute from artifact JSON |
| `artifact_manifest_hash_replay` | `passed` | source artifact manifests point to relative paths with matching SHA-256 |
| `duplicate_source_status_replay` | `passed` | all source artifact statuses remain passed |
| `branch_order_replay` | `passed` | packet branch and carrier branch are consumed separately; carrier evidence does not backfill packet branch |

## Control Matrix

| Control | Status | Claim Allowed | Detail |
| --- | --- | --- | --- |
| `i3_active_nulls` | `failed_closed` | `false` | 14/14 active null rows reject false-positive paths |
| `packet_consumptive_readout_boundary` | `failed_closed` | `false` | I5-B repeated readout spends route-b packet residue |
| `packet_transfer_as_su5_relabel` | `failed_closed` | `false` | I6 transfer expression remains SU3 because I5-B blocks non-consumptive durability |
| `carrier_native_conductance_memory_relabel` | `failed_closed` | `false` | carrier delta remains producer-mediated naturalization debt |
| `carrier_peer_label_swap_controls` | `failed_closed` | `false` | peer-label and peer-stress controls fail closed |
| `carrier_final_su5_before_closeout_relabel` | `failed_closed` | `false` | I7 may assign consumable evidence but cannot close final SU5 or N22 |
| `semantic_learning_choice_agency_native_support_phase8_relabels` | `failed_closed` | `false` | unsafe claim flags remain false in all I7 output rows |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `source_artifacts_valid` | `true` | [{"acceptance_state": "accepted_source_handoff_inventory_no_susceptibility_evidence", "artifact_manifest_count": 0, "artifact_manifest_va... |
| `active_nulls_fail_closed` | `true` | 14 |
| `packet_branch_consumptive_boundary_preserved` | `true` | {"active_null_rows_consumed": 14, "carrier_branch_i7_consumable_su5_count": 3, "carrier_branch_native_route_conductance_memory_supported"... |
| `carrier_branch_controlled_su5_candidates` | `true` | {"active_null_rows_consumed": 14, "carrier_branch_i7_consumable_su5_count": 3, "carrier_branch_native_route_conductance_memory_supported"... |
| `controls_failed_closed` | `true` | [{"claim_allowed": false, "control_id": "i3_active_nulls", "detail": "14/14 active null rows reject false-positive paths", "scope": "pre-... |
| `replays_passed` | `true` | [{"detail": "source output digests recompute from artifact JSON", "replay_id": "artifact_only_reconstruction", "status": "passed"}, {"det... |
| `unsafe_flags_all_false` | `true` | all I7 rows |
| `final_claims_blocked` | `true` | {"active_null_rows_consumed": 14, "carrier_branch_i7_consumable_su5_count": 3, "carrier_branch_native_route_conductance_memory_supported"... |
| `artifact_paths_repository_relative` | `true` | relative paths only |
