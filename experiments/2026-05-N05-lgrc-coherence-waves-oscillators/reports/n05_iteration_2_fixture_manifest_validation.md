# N05 Iteration 2 Fixture Manifest Validation

Status: passed

Command:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/validate_n05_fixture_manifest.py
```

Manifest: `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/configs/n05_fixture_manifest_v1.json`

Manifest SHA-256: `f3ade569aa97e92bbad8b4a59463dbe98953341789d2520cb5d0301c639e702f`

Canonical manifest digest: `3f6a2f09668651b62290b52b167b87a765470918cea65666e65087ad3fbadac7`

No oscillator probes were run in this iteration.

## Fixture

| Field | Value |
|---|---|
| fixture_id | `N05_S0_source_target_reservoir_chain_v1` |
| source_node_id | `0` |
| target_node_id | `2` |
| target_reservoir_node_id | `3` |
| outbound_route_id | `n05_o1_source_to_target_route_v1` |
| return_route_id | `n05_o2_target_to_source_return_route_v1` |
| node_plus_packet_conserved_total | `3.5` |

## Checks

| Check | Passed |
|---|---|
| `all_required_controls_declared` | True |
| `budget_nodes_cover_fixture_nodes` | True |
| `budget_surfaces_separated` | True |
| `budget_total_matches_node_sum` | True |
| `claim_flags_all_false` | True |
| `control_blockers_are_unique` | True |
| `cycle_definition_frozen` | True |
| `default_off_noop_declared` | True |
| `edge_count_matches` | True |
| `edge_endpoints_exist` | True |
| `edge_ids_unique` | True |
| `fixed_topology_declared` | True |
| `fixture_roles_are_nonsemantic` | True |
| `hidden_reservoir_arrays_disallowed` | True |
| `hidden_schedule_disallowed_on_routes` | True |
| `idempotency_key_declared` | True |
| `initial_node_coherence_nonnegative` | True |
| `lgrc2_minimum_declared` | True |
| `native_surface_cross_references_declared` | True |
| `new_n05_fixture_strategy_declared` | True |
| `no_oscillator_probe_run` | True |
| `no_positive_o_level_evidence_generated` | True |
| `node_count_matches` | True |
| `node_ids_unique` | True |
| `node_plus_packet_conserved_total_matches` | True |
| `o_ladder_claim_ceiling_progression_declared` | True |
| `o_ladder_contract_complete` | True |
| `o_ladder_runtime_levels_declared` | True |
| `outbound_and_return_routes_present` | True |
| `packet_ledger_declared` | True |
| `packetized_flux_declared` | True |
| `phase_1_hidden_schedule_blocked` | True |
| `phase_1_policy_fields_declared` | True |
| `phase_2_runtime_threshold_fields_declared` | True |
| `phase_3_audit_fields_declared` | True |
| `plateau_samples_not_cycles` | True |
| `producer_writes_only_evidence` | True |
| `required_lgrc_defaults_present` | True |
| `reservoir_native_surplus_mapping_declared` | True |
| `route_aspect_contract_declared` | True |
| `route_delays_match_edge_delays` | True |
| `routes_resolve_to_existing_edges` | True |
| `run_autonomous_stop_conditions_declared` | True |
| `schema_matches` | True |
| `self_rearm_reference_declared` | True |
| `snapshot_contract_declared` | True |
| `source_node_exists` | True |
| `source_target_distinct` | True |
| `surplus_trigger_reference_declared` | True |
| `symmetric_delay_declared` | True |
| `target_node_exists` | True |
| `target_reservoir_distinct` | True |
| `target_reservoir_initial_coherence_nonnegative` | True |
| `target_reservoir_node_exists` | True |
| `timing_vocabulary_declared` | True |
| `timing_vocabulary_symbols_declared` | True |

## Controls

| Control | Primary Blocker | Passed |
|---|---|---|
| `budget_ambiguity` | `n05_budget_surface_ambiguity` | True |
| `claim_promotion_attempt` | `n05_claim_promotion_rejected` | True |
| `hidden_reservoir` | `n05_hidden_reservoir_rejected` | True |
| `hidden_schedule` | `n05_hidden_schedule_rejected` | True |
| `idempotent_duplicate_production` | `n05_duplicate_production_suppressed` | True |
| `missing_route` | `n05_missing_route` | True |
| `missing_source` | `n05_missing_source_node` | True |
| `missing_target` | `n05_missing_target_node` | True |
| `policy_disabled` | `n05_policy_disabled_noop` | True |
| `producer_mutation_attempt` | `n05_producer_mutation_boundary_violation` | True |
| `pulse_disabled` | `n05_pulse_disabled_no_packet` | True |
| `snapshot_continue_after_load` | `n05_snapshot_continue_after_load_idempotent` | True |
| `stale_producer_read` | `n05_stale_producer_read_blocked` | True |

## Claim Flags

| Flag | Value |
|---|---|
| `agency_claim_allowed` | False |
| `agentic_like_claim_allowed` | False |
| `ant_colony_claim_allowed` | False |
| `biological_claim_allowed` | False |
| `goal_proxy_regulation_claim_allowed` | False |
| `identity_acceptance_claim_allowed` | False |
| `locomotion_like_claim_allowed` | False |
| `memory_or_trail_claim_allowed` | False |
| `movement_claim_allowed` | False |
| `rc_identity_collapse_claim_allowed` | False |
| `semantic_choice_claim_allowed` | False |
| `unrestricted_movement_claim_allowed` | False |

## Acceptance

Iteration 2 declares the N05 source-target-reservoir fixture, route policy,
delay policy, budget surfaces, default-off behavior, producer policy fields,
Phase 3 native-policy audit fields, cycle semantics, duplicate suppression,
snapshot continue-after-load contract, and fail-closed controls before any
oscillator probe runs.
