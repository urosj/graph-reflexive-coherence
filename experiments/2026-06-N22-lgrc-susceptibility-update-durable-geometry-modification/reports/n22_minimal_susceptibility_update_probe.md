# N22 Iteration 4 - Minimal Susceptibility Update Probe

Status: `passed`

Acceptance state: `accepted_minimal_source_current_su2_candidate_pending_replay_controls`

Output digest: `9bee91dba55414c1be3b63dd299b9d3c2629743adf2796cbf4da911a3db769ae`

## Summary

Iteration 4 runs the first source-backed N22 susceptibility probe using
the LGRC9V3 column-H fixture. It records pre-interaction geometry, a
prior route-local interaction, post-interaction geometry, a later route
re-entry trace, and a same-budget peer comparison.

The row is accepted only as a provisional `SU2` candidate. Replay-backed
`SU3`, durable `SU4`, transfer/re-entry `SU5`, N23-ready `SU6`, final
N22 closeout, and the N21 ND6 bridge remain unsupported.

## Geometric Interpretation

The prior interaction moves 0.08 coherence from the center into route_b node 1. The same-budget peer run moves the same budget into node 2 instead, leaving route_b node 1 unchanged.

Because the peer run spends the same budget but does not create the route_b node delta, the I4 delta is route-local rather than a global scheduler or budget drift.

Later route_b re-entry preserves a measurable route_b delta relative to the peer run, but replay and control matrices have not yet established durable geometry modification.

In numeric terms:

```text
target route_b delta = 0.080000000000
peer route_b delta under same peer budget = 0.000000000000
reentry delta persistence ratio = 0.500000000000
```

## Candidate Row

| Field | Value |
| --- | --- |
| Row | `n22_i4_row_01_minimal_route_b_susceptibility_update_probe` |
| Decision | `partial` |
| Provisional SU rung | `SU2` |
| Claim allowed | `false` |
| Derived report only | `false` |
| AP4 status | `required_recorded` |
| AP5 status | `not_applicable` |
| Artifact manifest entries | `19` |

## Gates

| Gate | Status |
| --- | --- |
| Support | `preserved` |
| Coherence | `changed_within_allowed_delta_above_floor` |
| Boundary | `preserved` |
| Flux/leakage | `preserved` |
| Global drift rejected | `true` |
| One-window transient rejected | `false` |

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `i1_inventory_passed` | `true` | accepted_source_handoff_inventory_no_susceptibility_evidence |
| `i2_schema_passed` | `true` | accepted_susceptibility_schema_frozen_no_positive_evidence |
| `i3_active_nulls_ready` | `true` | accepted_active_nulls_fail_closed_no_positive_evidence |
| `candidate_row_has_required_fields` | `true` | [] |
| `derived_report_only_false` | `true` | False |
| `source_current_inputs_present` | `true` | ["LGRC9V3 target route pre-interaction snapshot", "LGRC9V3 target route post-interaction snapshot", "LGRC9V3 target route later re-entry ... |
| `thresholds_declared_before_use` | `true` | experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/outputs/n22_minimal_susceptibility_update_probe_artifact... |
| `artifact_manifest_non_empty` | `true` | 19 |
| `artifact_hashes_match` | `true` | [{"artifact_role": "minimal_susceptibility_trace", "path": "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modificat... |
| `pre_post_delta_observed` | `true` | {"delta_observed": true, "delta_source": "LGRC9V3 packet arrival modified route_b node coherence", "min_route_local_delta": 0.05, "min_ta... |
| `peer_comparison_rejects_global_drift` | `true` | {"global_drift_rejected": true, "peer_prior_route": "route_peer_edge_1", "peer_route_delta": 0.0, "same_prior_interaction_budget": true, ... |
| `later_reentry_trace_present` | `true` | {"delta_persistence_ratio": 0.5000000000000111, "min_reentry_delta_persistence_ratio": 0.45, "peer_reentry_route_delta_from_pre": -0.0399... |
| `same_basin_preserved` | `true` | {"active_degree_same": true, "basin_member_count_same": true, "center_basin_id_same": true, "center_node_id_same": true, "topology_signat... |
| `support_gate_accepted` | `true` | {"center_basin_mass": 10.0, "status": "preserved", "support_floor": 9.85, "support_margin": 0.15000000000000036} |
| `coherence_gate_accepted` | `true` | {"center_node_coherence": 9.959999999999999, "coherence_floor": 9.85, "coherence_margin": 0.10999999999999943, "status": "changed_within_... |
| `boundary_gate_accepted` | `true` | {"active_degree": 9, "active_degree_floor": 9, "boundary_margin": 0, "status": "preserved", "topology_signature_same": true} |
| `flux_gate_accepted` | `true` | {"budget_error": 1.4210854715202004e-14, "in_flight_packet_total": 0.0, "max_budget_error": 1e-09, "status": "preserved"} |
| `active_reinforcement_absent_before_reentry` | `true` | {"active_reinforcement_queue_empty": true, "active_reinforcement_schedule_disabled": true, "reinforcement_budget_in_flight": 0.0} |
| `ap4_recorded_ap5_not_applicable` | `true` | {"ap4": "required_recorded", "ap5": "not_applicable"} |
| `unsafe_flags_all_false` | `true` | {"agency": false, "consciousness": false, "free_will": false, "fully_native_integration": false, "identity_acceptance": false, "native_an... |
| `claim_allowed_false_pending_replay_controls` | `true` | provisional source-current SU2 susceptibility-delta candidate pending I5 replay and I7 control matrix; no durable geometry modification, ... |
| `su2_only_pending_replay` | `true` | {"row_decision": "partial", "rung": "SU2"} |
| `durable_geometry_not_supported_yet` | `true` | {"durable_geometry_modification_supported": false, "one_window_transient_rejected": false} |
| `artifact_paths_repository_relative` | `true` | ["experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/outputs/n22_minimal_susceptibility_update_probe_artifa... |

## Claim Boundary

The result is provisional SU2 pending I5 replay and I7 controls; it is not semantic learning, choice, agency, native support, or Phase 8.

Semantic learning, choice, agency, native support, sentience, Phase 8,
and ant-ecology implementation remain blocked.
