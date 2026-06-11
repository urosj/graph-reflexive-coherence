# N08 Iteration 4 MEM2 Trail Memory Surface

Status: `passed`.

Iteration 4 converts MEM1 route-use events into experiment-local serialized
trail memory surface rows. It does not yet run decay/reinforcement windows,
memory-shaped route arbitration, or candidate-score updates.

## Branch Question

What becomes available when committed route-use traces persist as serialized trail-surface rows?

## Branch Answer

Committed route-use events can persist as digest-pinned trail-surface rows.
The resulting surface is visible as serialized artifact state:

```json
{
  "route_a": 0.5,
  "route_b": 0.5
}
```

This is still not reinforcement learning or route-weight propagation. The
surface exists, but it has not been read by candidate scoring and has not yet
created future route bias.

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `trail_memory_surface_candidate`
- naturalization rung:
  `Nat1_persisted_artifact_surface`
- affordance status:
  `latent_not_yet_operational`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
| `use_history_becomes_surface` | `memory_surface_row_count` | `4` | The MEM1 trace is no longer only event history; each route use now has a digest-pinned trail surface row. |
| `route_specific_strength_accumulates` | `final_memory_strength_by_route` | `{'route_b': 0.5, 'route_a': 0.5}` | Route A and route B retain separate trail strengths under the canonical memory-surface key. This is surface persistence, not route choice bias yet. |
| `affordance_is_latent` | `affordance_surface_emitted` | `False` | The trail can become an affordance only when later candidate scoring reads it as runtime-visible evidence. |
| `memory_budget_separate_from_coherence` | `node_plus_packet_budget_error` | `0.0` | Trail strength accounting changes while physical node-plus-packet coherence remains unchanged. |

Cultivation next question:

Can the persisted trail surface undergo serialized decay and reinforcement updates while preserving memory-budget and node-plus-packet budget separation?

## Memory Surface Rows

| Source Cycle | Route | Before | Input | After | Surface Digest |
|---|---|---:|---:|---:|---|
| `cycle_0` | `route_a` | `0.0` | `0.25` | `0.25` | `7530f78c0ddd3dea6ae37c4b32bc4e82f6be9ea23410c412db3621f38d647a87` |
| `cycle_1` | `route_b` | `0.0` | `0.25` | `0.25` | `12098eba4caf7dd4972a650442400e1c31727bc6c14ea509812f6d39d940ec1a` |
| `cycle_2` | `route_a` | `0.25` | `0.25` | `0.5` | `f11487b6fbf0888a450543dd04859bb27ea04831573f3b26e281fc8c627f8074` |
| `cycle_3` | `route_b` | `0.25` | `0.25` | `0.5` | `82f3aba24f0e0093525dbe9c671dec8bbf88f8cd4b96f583e88de68a961a81d4` |

## Formation Versus MEM3 Window

Iteration 4 performs formation-phase seed accumulation: a committed route-use
event creates or strengthens a serialized trail surface row. The arithmetic is
saturating additive and matches the declared reinforcement policy, but this is
not the formal MEM3 decay/reinforcement policy window.

```json
{
  "formal_mem3_decay_reinforcement_window_applied": false,
  "formal_mem3_policy_window_applied": false,
  "formal_mem3_window_status": "deferred_to_iteration_5",
  "formation_arithmetic": "saturating_additive_seed_accumulation",
  "formation_arithmetic_policy_reference": "n08_saturating_additive_reinforcement_v1",
  "formation_update_kind": "route_use_seed_accumulation",
  "formation_window_applied": true
}
```

Iteration 5 starts from this formed surface state and applies the first formal
decay/reinforcement update window. It must not re-apply the Iteration 4
formation inputs as if they were unprocessed route-use events.

## MEM2 Event Contract

```json
{
  "allowed_supplementary_fields": [
    "artifact_kind",
    "schema_version",
    "mem_level",
    "mem_level_is_evidence_classification",
    "claim_ceiling",
    "memory_surface_id_rule",
    "memory_surface_kind_semantics",
    "route_use_event_id",
    "source_route_use_event_time_key",
    "source_route_use_scheduler_event_index",
    "source_cycle_id",
    "selected_route_id",
    "source_arbitration_record_digest",
    "source_candidate_set_digest",
    "selected_candidate_route_digest",
    "memory_policy_native_support_status",
    "memory_strength_before",
    "memory_strength_delta",
    "route_use_count_for_key",
    "event_time_key_derivation",
    "scheduler_event_index_derivation",
    "event_order_relation",
    "node_plus_packet_budget_semantics",
    "memory_budget_semantics",
    "formation_window_applied",
    "formation_update_kind",
    "formation_input",
    "formation_arithmetic",
    "formation_arithmetic_policy_reference",
    "formation_arithmetic_matches_reinforcement_policy",
    "formation_input_from_route_use",
    "formal_mem3_policy_window_applied",
    "formal_mem3_decay_reinforcement_window_applied",
    "formal_mem3_window_status",
    "decay_policy_applied",
    "reinforcement_policy_window_applied",
    "affordance_surface_emitted",
    "affordance_status",
    "learning_boundary",
    "visual_reference",
    "visual_is_evidence_source"
  ],
  "event_time_key_convention": {
    "offset_from_route_use_event": 0.2,
    "rationale": "MEM2 memory surface rows are placed after MEM1 route-use events while leaving an ordered event-time band for later MEM3 update windows."
  },
  "formation_window_semantics": {
    "formal_mem3_decay_reinforcement_window_applied": false,
    "formal_mem3_policy_window_applied": false,
    "formal_mem3_window_status": "deferred_to_iteration_5",
    "formation_arithmetic": "saturating_additive_seed_accumulation",
    "formation_arithmetic_policy_reference": "n08_saturating_additive_reinforcement_v1",
    "formation_update_kind": "route_use_seed_accumulation",
    "formation_window_applied": true
  },
  "memory_surface_id_rule": "n08-memory-surface:{memory_surface_key_digest[:16]}:{route_use_event_digest[:16]}",
  "required_fields": [
    "memory_surface_id",
    "memory_surface_kind",
    "route_use_event_digest",
    "memory_surface_key",
    "memory_surface_key_digest",
    "memory_policy_id",
    "memory_policy_digest",
    "memory_strength",
    "event_time_key",
    "scheduler_event_index",
    "node_plus_packet_budget_before",
    "node_plus_packet_budget_after",
    "node_plus_packet_budget_error",
    "memory_budget_surface",
    "memory_budget_before",
    "reinforcement_input",
    "decay_loss",
    "saturation_clamp_loss",
    "memory_budget_after",
    "memory_budget_error",
    "claim_flags",
    "memory_surface_digest"
  ],
  "scheduler_event_index_convention": {
    "offset_from_route_use_event": 10,
    "rationale": "MEM1 route-use evidence occupies the lower scheduler band; MEM2 memory surface formation rows use the 10-19 band so later MEM3 windows can be ordered after surface formation without reusing route-use indices.",
    "target_scheduler_band": "10-19"
  },
  "snapshot_scope": {
    "full_replay_requires": "memory_surface_rows",
    "snapshot_completeness": "latest_state_summary_not_full_replay_record"
  }
}
```

Memory policy digest validation:

```json
{
  "declared_digest": "bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb",
  "digest_rule": "sha256(canonical_json(memory_policy_without_memory_policy_digest))",
  "memory_policy_id": "n08_memory_policy_v1",
  "recomputed_digest": "bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb",
  "valid": true
}
```

## State Snapshot

```json
{
  "affordance_status": "latent_not_yet_read_by_candidate_scoring",
  "full_replay_requires": "memory_surface_rows",
  "memory_surface_state_snapshot_digest": "60448fc4c7d491c254fafd21a7745b34cf6cf1922f560a6a8b2f2c9df75a4d68",
  "memory_surface_storage": "experiment_local_serialized_json_artifact_rows",
  "omitted_replay_fields_reason": "Full per-event replay fields remain serialized on memory_surface_rows; the snapshot summarizes the latest state per canonical memory key.",
  "snapshot_completeness": "latest_state_summary_not_full_replay_record",
  "snapshot_id": "n08_mem2_trail_surface_state_snapshot_v1",
  "snapshot_kind": "memory_surface_state_snapshot",
  "snapshot_semantics": "final experiment-local trail surface state after MEM1 route-use events",
  "state_by_memory_surface_key_digest": {
    "3dca55df466ac3a101798884520a2ec1142994f03728aa4dd47aebcf4893de11": {
      "claim_flags_all_false": true,
      "latest_decay_loss": 0.0,
      "latest_event_time_key": 4.3,
      "latest_memory_budget_after": 0.5,
      "latest_memory_budget_before": 0.25,
      "latest_memory_budget_error": 0.0,
      "latest_memory_surface_digest": "82f3aba24f0e0093525dbe9c671dec8bbf88f8cd4b96f583e88de68a961a81d4",
      "latest_memory_surface_id": "n08-memory-surface:3dca55df466ac3a1:e44cdc336ccfc5ad",
      "latest_node_plus_packet_budget_after": 0.0,
      "latest_node_plus_packet_budget_before": 0.0,
      "latest_node_plus_packet_budget_error": 0.0,
      "latest_reinforcement_input": 0.25,
      "latest_route_use_event_digest": "e44cdc336ccfc5adebf42618cfa9fc739f695a5f88c1f787724afb85c8f428ab",
      "latest_saturation_clamp_loss": 0.0,
      "latest_scheduler_event_index": 15,
      "latest_selected_candidate_route_digest": "1732ca519398908214633ffb085a0c5d25b7c772891a025f5e7c1df0a5da7304",
      "latest_source_arbitration_record_digest": "274002a129793722412f4019ea2ff18f2b45710c0fa8d80e6bebb083cf085db0",
      "latest_source_candidate_set_digest": "cc8603974788f12118e143fb8f6c96ae3ef6eb1c021e3a6c6c14aba8469db765",
      "memory_policy_digest": "bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb",
      "memory_policy_id": "n08_memory_policy_v1",
      "memory_strength": 0.5,
      "memory_surface_key": {
        "memory_policy_id": "n08_memory_policy_v1",
        "route_aspect_digest": "4d10620cbdc9c7da9a1a1c5b510a5a03350f055d8139037876ce57524988e8d1",
        "route_id": "route_b",
        "source_support_area_digest": "c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb",
        "target_support_area_digest": "b2ff898e08259e4fca68a1ec59bf1add32c1612a0d4c75d85af63a0bfa795af1"
      },
      "memory_surface_key_digest": "3dca55df466ac3a101798884520a2ec1142994f03728aa4dd47aebcf4893de11",
      "memory_surface_kind": "trail",
      "route_use_count_for_key": 2,
      "selected_route_id": "route_b"
    },
    "c0a6fdca6c30cca1bbb900de543844c70ea23af922e6a4d8ddca16f7e5d4458d": {
      "claim_flags_all_false": true,
      "latest_decay_loss": 0.0,
      "latest_event_time_key": 3.3,
      "latest_memory_budget_after": 0.5,
      "latest_memory_budget_before": 0.25,
      "latest_memory_budget_error": 0.0,
      "latest_memory_surface_digest": "f11487b6fbf0888a450543dd04859bb27ea04831573f3b26e281fc8c627f8074",
      "latest_memory_surface_id": "n08-memory-surface:c0a6fdca6c30cca1:04706f438525fecc",
      "latest_node_plus_packet_budget_after": 0.0,
      "latest_node_plus_packet_budget_before": 0.0,
      "latest_node_plus_packet_budget_error": 0.0,
      "latest_reinforcement_input": 0.25,
      "latest_route_use_event_digest": "04706f438525fecc15574b77f01f06720d8bd063090cc38dbe574b69af4c3b92",
      "latest_saturation_clamp_loss": 0.0,
      "latest_scheduler_event_index": 14,
      "latest_selected_candidate_route_digest": "56df5ea777c43a139b3d26d314b41affc82cedafd8dc54e7f1af615cb43d52a1",
      "latest_source_arbitration_record_digest": "715bbac6df142956748a403236d214a949c7b36f3a87716a3cb2978e3f959e8f",
      "latest_source_candidate_set_digest": "30217e1dcc8c533d3175131d2b2be0a265829a41714fe338a1330982b6c8e510",
      "memory_policy_digest": "bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb",
      "memory_policy_id": "n08_memory_policy_v1",
      "memory_strength": 0.5,
      "memory_surface_key": {
        "memory_policy_id": "n08_memory_policy_v1",
        "route_aspect_digest": "4d10620cbdc9c7da9a1a1c5b510a5a03350f055d8139037876ce57524988e8d1",
        "route_id": "route_a",
        "source_support_area_digest": "c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb",
        "target_support_area_digest": "b2ff898e08259e4fca68a1ec59bf1add32c1612a0d4c75d85af63a0bfa795af1"
      },
      "memory_surface_key_digest": "c0a6fdca6c30cca1bbb900de543844c70ea23af922e6a4d8ddca16f7e5d4458d",
      "memory_surface_kind": "trail",
      "route_use_count_for_key": 2,
      "selected_route_id": "route_a"
    }
  }
}
```

The snapshot is a latest-state summary keyed by memory surface key digest. Full
artifact replay must use `memory_surface_rows`, which retain every ordered
formation event, source digest, budget field, and claim flag.

## Learning Boundary

```json
{
  "candidate_score_updated": false,
  "distinction": "Iteration 4 creates a serialized trail surface from route-use events. It still does not update native route weights or let memory bias future route arbitration.",
  "future_route_bias_created": false,
  "is_graph_weight_propagation": false,
  "is_neural_weight_update": false,
  "is_reinforcement_learning": false,
  "policy_updated": false,
  "route_weight_updated": false,
  "surface_strength_created": true
}
```

## Producer / Step Boundary

```json
{
  "primary_blocker": "producer_mutation_boundary_violation",
  "producer_may_mutate_memory_surface": false,
  "producer_may_mutate_node_coherence": false,
  "producer_may_mutate_packet_ledger": false,
  "producer_scheduling_allowed": true,
  "step_remains_packet_mutation_boundary": true
}
```

## Inherited Native Policy Blockers

```json
[
  "native_route_conductance_memory_policy_missing",
  "native_trail_memory_surface_missing",
  "native_memory_surface_serialization_policy_missing",
  "native_memory_surface_keying_policy_missing",
  "native_memory_budget_accounting_policy_missing",
  "native_memory_cross_cycle_persistence_policy_missing",
  "native_memory_decay_policy_missing",
  "native_memory_reinforcement_policy_missing",
  "native_memory_candidate_score_component_semantics_missing",
  "native_memory_artifact_replay_validator_missing"
]
```

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
| `missing_route_use_event` | `blocked` | `missing_route_use_event` | `True` | Reject a memory surface row without a source route-use event. |
| `memory_surface_digest_mismatch` | `blocked` | `memory_surface_digest_mismatch` | `True` | Reject a memory surface row whose digest does not recompute. |
| `memory_surface_key_digest_mismatch` | `blocked` | `memory_surface_key_digest_mismatch` | `True` | Reject a surface whose canonical key digest does not recompute. |
| `hidden_route_history` | `blocked` | `hidden_route_history` | `True` | Reject memory surfaces derived from hidden fixture history. |
| `memory_budget_discontinuity` | `blocked` | `memory_budget_discontinuity` | `True` | Reject trail-strength budget equation failure. |
| `node_plus_packet_budget_discontinuity` | `blocked` | `node_plus_packet_budget_discontinuity` | `True` | Reject node-plus-packet budget drift hidden by memory bookkeeping. |
| `claim_promotion` | `blocked` | `claim_promotion` | `True` | Reject MEM2 promotion to memory claim, ACO, agency, or movement. |

## Checks

| Check | Passed |
|---|---|
| `affordance_not_yet_operational` | `True` |
| `allowed_supplementary_fields_declared` | `True` |
| `arc_interpretation_present` | `True` |
| `arc_next_question_recorded` | `True` |
| `arc_not_endpoint_only` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_distinct` | `True` |
| `controls_passed` | `True` |
| `controls_present` | `True` |
| `event_time_offset_declared` | `True` |
| `formation_window_semantics_declared` | `True` |
| `memory_budget_equations_hold` | `True` |
| `memory_claim_still_closed` | `True` |
| `memory_policy_digest_recomputes` | `True` |
| `memory_strength_equals_memory_budget_after` | `True` |
| `memory_surface_digest_recomputes` | `True` |
| `memory_surface_id_rule_declared` | `True` |
| `memory_surface_key_digest_recomputes` | `True` |
| `memory_surface_kind_trail` | `True` |
| `memory_surface_persists_after_route_use` | `True` |
| `memory_surface_required_fields_present` | `True` |
| `memory_surface_rows_emitted` | `True` |
| `memory_surface_state_snapshot_digest_recomputes` | `True` |
| `memory_surface_state_snapshot_serialized` | `True` |
| `native_memory_surface_still_experiment_local` | `True` |
| `no_candidate_score_or_future_bias_update` | `True` |
| `node_plus_packet_budget_separate_and_exact` | `True` |
| `producer_step_boundary_preserved` | `True` |
| `route_use_digest_cited` | `True` |
| `scheduler_index_offset_declared` | `True` |
| `source_manifest_passed` | `True` |
| `source_mem1_passed` | `True` |
| `src_clean` | `True` |
| `state_snapshot_scope_declared` | `True` |

## Artifact Digests

```json
{
  "arc_interpretation_digest": "a94e51a2605e5a6c358d83a7c3d0239a94d4e9de57de480c1289e7d401b63d28",
  "checks_digest": "149c6b2a229a7a5cc744cd9f3f6f3d6bcd5b3a769f13a7929569a0fbee047550",
  "controls_digest": "270c19b88cdd71fe3670e22d9b9c7973d97ffa9d3592d549ad1bb5965764ed6b",
  "memory_surface_rows_digest": "0e9629e88ce615f261f0350552d62fdba1b1b02223b26cb38ee1eca54e7ad2d4",
  "memory_surface_state_snapshot_digest": "60448fc4c7d491c254fafd21a7745b34cf6cf1922f560a6a8b2f2c9df75a4d68"
}
```

## Acceptance

Iteration 4 passes if prior route use creates a persisted runtime-visible
memory/trail/affordance surface with source provenance and exact budgets.

Achieved: `True`.

Output digest: `acced36658c46bab5e6daa0f44a28f566c5848d1bc0578bd71da6b8720f27af8`.
