# N08 Iteration 5 MEM3 Decay / Reinforcement Update

Status: `passed`.

Iteration 5 starts from the MEM2 trail surface state and applies a serialized
formal MEM3 update window. It does not re-create the Iteration 4 formation
inputs, run candidate scoring, run route arbitration, mutate node coherence, or
promote claims.

## Branch Question

What changes when a persisted trail surface passes through a serialized decay/reinforcement window?

## Branch Answer

The persisted trail surface can be updated by serialized decay and
reinforcement policy rows. Both routes qualify for repeated-use reinforcement,
but the older route surface decays across more elapsed memory windows before
reinforcement:

```json
{
  "route_a": 0.655,
  "route_b": 0.7
}
```

This is still not reinforcement learning or native route-weight propagation.
The result is an artifact-visible memory update, not candidate-score bias yet.
`decay_loss` is also not physical RC flux; it is serialized memory-signal
attenuation with no coherence-pocket destination in this iteration.

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `decay_reinforcement_memory_candidate`
- naturalization rung:
  `Nat2_policy_updated_artifact_surface`
- affordance status:
  `latent_not_yet_operational`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
| `memory_surface_updates_without_reformation` | `mem3_update_row_count` | `2` | The MEM2 surfaces are not re-created from route history; new MEM3 rows cite the prior surface digests and apply a formal update window. |
| `recency_changes_decay_amount` | `elapsed_memory_window_count_by_route` | `{'route_a': 2, 'route_b': 1}` | Both routes qualify for repeated-use reinforcement, but the older surface has more elapsed decay windows before reinforcement. |
| `updated_strengths_remain_serialized` | `final_memory_strength_by_route` | `{'route_b': 0.7, 'route_a': 0.655}` | MEM3 creates a replayable strength difference from serialized timing and policy fields, not from hidden route preference. |
| `memory_budget_separate_from_coherence` | `decay_loss_by_route` | `{'route_a': 0.095, 'route_b': 0.05}` | Decay loss changes memory signal strength only. It is not physical flux and has no coherence-pocket destination. |

Cultivation next question:

Can candidate-route score components cite these MEM3 memory surface digests and alter route arbitration without hidden memory inputs?

## MEM3 Update Policy

```json
{
  "claim_promotion_allowed": false,
  "coherence_pocket_transfer_guard": "If memory decay is later used to transfer into coherence pockets, the transfer must declare a conserved destination surface and preserve the main node-plus-packet RC budget. Without that destination this quantity is a divergent artifact-signal path, not physical RC flux.",
  "coherence_pocket_transfer_performed": false,
  "conserved_destination_required_for_physical_decay": true,
  "decay_destination_surface": null,
  "decay_is_physical_flux": false,
  "decay_policy": {
    "decay_can_only_reduce_strength": true,
    "decay_factor": 0.9,
    "decay_function": "exponential_per_memory_window",
    "decay_policy_id": "n08_exponential_decay_v1",
    "floor": 0.0,
    "hidden_decay_allowed": false,
    "records_decay_loss": true
  },
  "decay_policy_digest": "e696301dbb4653e75b74a2549458fa04682760150e14a75927bc4ed4e9ae548f",
  "decay_quantity_kind": "serialized_memory_signal_attenuation",
  "decay_quantity_semantics": "decay_loss attenuates artifact-level memory strength only; it is not node coherence, packet mass, physical flux, or RC substrate budget.",
  "elapsed_memory_window_rule": "max(1, floor(update_window_event_time_key - source_memory_surface_event_time_key))",
  "hidden_route_history_allowed": false,
  "mem3_update_window_policy_digest": "3adaccba822f131195901dc3938687a600cae7b6e1016a172477bcad138750ee",
  "node_plus_packet_budget_mutation_allowed": false,
  "physical_decay_support_status": "not_supported_without_explicit_conserved_destination_surface",
  "policy_id": "n08_mem3_decay_then_reinforce_repeated_use_v1",
  "policy_surface": "experiment_local_serialized_json_rows",
  "posthoc_threshold_change_allowed": false,
  "reinforcement_eligibility_rule": "route_use_count_for_key >= 2",
  "reinforcement_policy": {
    "ceiling": 1.0,
    "floor": 0.0,
    "hidden_reinforcement_allowed": false,
    "records_reinforcement_input": true,
    "records_saturation_clamp_loss": true,
    "reinforcement_amount": 0.25,
    "reinforcement_function": "saturating_additive",
    "reinforcement_policy_id": "n08_saturating_additive_reinforcement_v1"
  },
  "reinforcement_policy_digest": "0c1e4b8e9549d3f0cba7cf94661799903218710734a1945cb8676bc185d82073",
  "route_specific_preference_allowed": false,
  "same_window_order_serialized": true,
  "same_window_update_order": [
    "decay",
    "reinforcement"
  ],
  "update_scheduler_band": "20-29",
  "update_scheduler_event_index_base": 25,
  "update_window_event_time_key": 5.5,
  "update_window_id": "n08_mem3_decay_reinforcement_window_0"
}
```

## Decay Quantity Boundary

```json
{
  "coherence_pocket_transfer_guard": "If memory decay is later used to transfer into coherence pockets, the transfer must declare a conserved destination surface and preserve the main node-plus-packet RC budget. Without that destination this quantity is a divergent artifact-signal path, not physical RC flux.",
  "coherence_pocket_transfer_performed": false,
  "conserved_destination_required_for_physical_decay": true,
  "decay_destination_surface": null,
  "decay_is_physical_flux": false,
  "decay_quantity_kind": "serialized_memory_signal_attenuation",
  "decay_quantity_semantics": "decay_loss attenuates artifact-level memory strength only; it is not node coherence, packet mass, physical flux, or RC substrate budget.",
  "physical_decay_support_status": "not_supported_without_explicit_conserved_destination_surface",
  "rc_budget_implication": "node-plus-packet budget remains the only physical coherence budget in this iteration"
}
```

If a later iteration uses memory decay to transfer into coherence pockets, it
must declare a conserved destination surface and prove node-plus-packet budget
conservation. Without that destination, `decay_loss` must remain an
artifact-level signal quantity and must not be read as RC mass or flux.

## MEM3 Update Rows

| Route | Before | Windows | Decay Loss | After Decay | Reinforcement | After | Surface Digest |
|---|---:|---:|---:|---:|---:|---:|---|
| `route_a` | `0.5` | `2` | `0.095` | `0.405` | `0.25` | `0.655` | `a0ba9befc3a8ad113271636fe3a799f63deb5e10baaafebfb674629fd8757447` |
| `route_b` | `0.5` | `1` | `0.05` | `0.45` | `0.25` | `0.7` | `b21c093d70245fab02088b8ebed42ac931629c41f6e45d618f5b5a67d9bea627` |

## State Snapshot

```json
{
  "affordance_status": "latent_not_yet_read_by_candidate_scoring",
  "full_replay_requires": "memory_surface_rows",
  "memory_surface_state_snapshot_digest": "284cf90a485db74c28e0d5e8c90cc3aceb4aac1f6073f4d9c1a0fade35623209",
  "memory_surface_storage": "experiment_local_serialized_json_artifact_rows",
  "snapshot_completeness": "latest_state_summary_not_full_replay_record",
  "snapshot_id": "n08_mem3_decay_reinforcement_state_snapshot_v1",
  "snapshot_kind": "memory_surface_state_snapshot",
  "snapshot_semantics": "final experiment-local trail surface state after the MEM3 decay/reinforcement update window",
  "state_by_memory_surface_key_digest": {
    "3dca55df466ac3a101798884520a2ec1142994f03728aa4dd47aebcf4893de11": {
      "claim_flags_all_false": true,
      "coherence_pocket_transfer_performed": false,
      "decay_destination_surface": null,
      "decay_is_physical_flux": false,
      "decay_loss": 0.05,
      "decay_policy_digest": "e696301dbb4653e75b74a2549458fa04682760150e14a75927bc4ed4e9ae548f",
      "decay_policy_id": "n08_exponential_decay_v1",
      "decay_quantity_kind": "serialized_memory_signal_attenuation",
      "elapsed_memory_window_count": 1,
      "latest_event_time_key": 5.51,
      "latest_memory_surface_digest": "b21c093d70245fab02088b8ebed42ac931629c41f6e45d618f5b5a67d9bea627",
      "latest_memory_surface_id": "n08-memory-surface:3dca55df466ac3a1:mem3:3adaccba822f",
      "latest_route_use_event_digest": "e44cdc336ccfc5adebf42618cfa9fc739f695a5f88c1f787724afb85c8f428ab",
      "latest_scheduler_event_index": 26,
      "mem3_update_window_id": "n08_mem3_decay_reinforcement_window_0",
      "mem3_update_window_policy_digest": "3adaccba822f131195901dc3938687a600cae7b6e1016a172477bcad138750ee",
      "memory_policy_digest": "bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb",
      "memory_policy_id": "n08_memory_policy_v1",
      "memory_strength": 0.7,
      "memory_strength_before": 0.5,
      "memory_surface_key": {
        "memory_policy_id": "n08_memory_policy_v1",
        "route_aspect_digest": "4d10620cbdc9c7da9a1a1c5b510a5a03350f055d8139037876ce57524988e8d1",
        "route_id": "route_b",
        "source_support_area_digest": "c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb",
        "target_support_area_digest": "b2ff898e08259e4fca68a1ec59bf1add32c1612a0d4c75d85af63a0bfa795af1"
      },
      "memory_surface_key_digest": "3dca55df466ac3a101798884520a2ec1142994f03728aa4dd47aebcf4893de11",
      "memory_surface_kind": "trail",
      "physical_decay_support_status": "not_supported_without_explicit_conserved_destination_surface",
      "reinforcement_input": 0.25,
      "reinforcement_policy_digest": "0c1e4b8e9549d3f0cba7cf94661799903218710734a1945cb8676bc185d82073",
      "reinforcement_policy_id": "n08_saturating_additive_reinforcement_v1",
      "route_use_count_for_key": 2,
      "saturation_clamp_loss": 0.0,
      "selected_route_id": "route_b",
      "source_memory_surface_digest": "82f3aba24f0e0093525dbe9c671dec8bbf88f8cd4b96f583e88de68a961a81d4",
      "strength_after_decay": 0.45
    },
    "c0a6fdca6c30cca1bbb900de543844c70ea23af922e6a4d8ddca16f7e5d4458d": {
      "claim_flags_all_false": true,
      "coherence_pocket_transfer_performed": false,
      "decay_destination_surface": null,
      "decay_is_physical_flux": false,
      "decay_loss": 0.095,
      "decay_policy_digest": "e696301dbb4653e75b74a2549458fa04682760150e14a75927bc4ed4e9ae548f",
      "decay_policy_id": "n08_exponential_decay_v1",
      "decay_quantity_kind": "serialized_memory_signal_attenuation",
      "elapsed_memory_window_count": 2,
      "latest_event_time_key": 5.5,
      "latest_memory_surface_digest": "a0ba9befc3a8ad113271636fe3a799f63deb5e10baaafebfb674629fd8757447",
      "latest_memory_surface_id": "n08-memory-surface:c0a6fdca6c30cca1:mem3:3adaccba822f",
      "latest_route_use_event_digest": "04706f438525fecc15574b77f01f06720d8bd063090cc38dbe574b69af4c3b92",
      "latest_scheduler_event_index": 25,
      "mem3_update_window_id": "n08_mem3_decay_reinforcement_window_0",
      "mem3_update_window_policy_digest": "3adaccba822f131195901dc3938687a600cae7b6e1016a172477bcad138750ee",
      "memory_policy_digest": "bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb",
      "memory_policy_id": "n08_memory_policy_v1",
      "memory_strength": 0.655,
      "memory_strength_before": 0.5,
      "memory_surface_key": {
        "memory_policy_id": "n08_memory_policy_v1",
        "route_aspect_digest": "4d10620cbdc9c7da9a1a1c5b510a5a03350f055d8139037876ce57524988e8d1",
        "route_id": "route_a",
        "source_support_area_digest": "c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb",
        "target_support_area_digest": "b2ff898e08259e4fca68a1ec59bf1add32c1612a0d4c75d85af63a0bfa795af1"
      },
      "memory_surface_key_digest": "c0a6fdca6c30cca1bbb900de543844c70ea23af922e6a4d8ddca16f7e5d4458d",
      "memory_surface_kind": "trail",
      "physical_decay_support_status": "not_supported_without_explicit_conserved_destination_surface",
      "reinforcement_input": 0.25,
      "reinforcement_policy_digest": "0c1e4b8e9549d3f0cba7cf94661799903218710734a1945cb8676bc185d82073",
      "reinforcement_policy_id": "n08_saturating_additive_reinforcement_v1",
      "route_use_count_for_key": 2,
      "saturation_clamp_loss": 0.0,
      "selected_route_id": "route_a",
      "source_memory_surface_digest": "f11487b6fbf0888a450543dd04859bb27ea04831573f3b26e281fc8c627f8074",
      "strength_after_decay": 0.405
    }
  }
}
```

The snapshot is a latest-state summary keyed by memory surface key digest. Full
artifact replay must use `memory_surface_rows`, which retain every ordered
update event, source digest, policy digest, budget field, and claim flag.

## Learning Boundary

```json
{
  "candidate_score_updated": false,
  "distinction": "Iteration 5 updates serialized trail surface strength through declared policies. It still does not update native route weights or let memory bias candidate scoring.",
  "future_route_bias_created": false,
  "is_graph_weight_propagation": false,
  "is_neural_weight_update": false,
  "is_reinforcement_learning": false,
  "policy_updated": false,
  "route_weight_updated": false,
  "surface_strength_updated": true
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
| `decay_policy_missing` | `blocked` | `decay_policy_missing` | `True` | Reject MEM3 update rows without serialized decay policy. |
| `reinforcement_policy_missing` | `blocked` | `reinforcement_policy_missing` | `True` | Reject MEM3 reinforcement rows without serialized reinforcement policy. |
| `memory_policy_hidden_preference` | `blocked` | `memory_policy_hidden_preference` | `True` | Reject route-specific memory preference not derived from serialized route-use evidence. |
| `posthoc_memory_threshold_change` | `blocked` | `posthoc_memory_threshold_change` | `True` | Reject changing reinforcement eligibility after rows are built. |
| `duplicate_memory_update` | `blocked` | `duplicate_memory_update` | `True` | Reject duplicate MEM3 update ids for the same key/window/policy. |
| `arbitration_memory_order_invalid` | `blocked` | `arbitration_memory_order_invalid` | `True` | Reject MEM3 rows ordered before their source memory surface. |
| `memory_budget_discontinuity` | `blocked` | `memory_budget_discontinuity` | `True` | Reject decay/reinforcement rows whose memory budget fails. |
| `node_plus_packet_budget_discontinuity` | `blocked` | `node_plus_packet_budget_discontinuity` | `True` | Reject MEM3 rows that hide physical budget drift. |
| `claim_promotion` | `blocked` | `claim_promotion` | `True` | Reject MEM3 promotion to memory claim, ACO, agency, or movement. |

## Checks

| Check | Passed |
|---|---|
| `allowed_supplementary_fields_declared` | `True` |
| `arc_interpretation_present` | `True` |
| `arc_next_question_recorded` | `True` |
| `arc_not_endpoint_only` | `True` |
| `claim_flags_all_false` | `True` |
| `coherence_pocket_transfer_guard_recorded` | `True` |
| `control_blockers_distinct` | `True` |
| `controls_passed` | `True` |
| `controls_present` | `True` |
| `decay_not_physical_flux` | `True` |
| `decay_policy_applied` | `True` |
| `decay_quantity_scope_declared` | `True` |
| `decay_then_reinforcement_order_declared` | `True` |
| `duplicate_update_suppressed` | `True` |
| `elapsed_window_rule_applied` | `True` |
| `formal_mem3_window_applied` | `True` |
| `mem3_changes_strength` | `True` |
| `mem3_update_rows_emitted` | `True` |
| `memory_budget_equations_hold` | `True` |
| `memory_claim_still_closed` | `True` |
| `memory_strength_equals_memory_budget_after` | `True` |
| `memory_surface_digest_recomputes` | `True` |
| `memory_surface_key_digest_recomputes` | `True` |
| `memory_surface_required_fields_present` | `True` |
| `memory_update_persists_after_source_surface` | `True` |
| `native_memory_update_still_experiment_local` | `True` |
| `no_candidate_score_or_future_bias_update` | `True` |
| `node_plus_packet_budget_separate_and_exact` | `True` |
| `policy_digests_recompute` | `True` |
| `producer_step_boundary_preserved` | `True` |
| `recency_visible_in_strengths` | `True` |
| `reinforcement_policy_window_applied` | `True` |
| `route_neutral_reinforcement_rule` | `True` |
| `source_manifest_passed` | `True` |
| `source_mem2_passed` | `True` |
| `source_mem2_snapshot_requires_rows_for_full_replay` | `True` |
| `source_memory_surface_digests_cited` | `True` |
| `src_clean` | `True` |
| `state_snapshot_digest_recomputes` | `True` |
| `state_snapshot_scope_declared` | `True` |
| `state_snapshot_serialized` | `True` |

## Artifact Digests

```json
{
  "arc_interpretation_digest": "6c648a35a8e1373fbbaf8c5f6a45d9f4fc6b295673ac36c8d57fc6d3ea3a489b",
  "checks_digest": "89d8cda57f5a6dc8b23fbc94489e3193f41e217f2c02d8b091705a5d13ad784e",
  "controls_digest": "6ab0504f0e492a68c34c85b5fe012f614ae48b1b5c0a920f6f6066cfb27cad7c",
  "mem3_update_window_policy_digest": "3adaccba822f131195901dc3938687a600cae7b6e1016a172477bcad138750ee",
  "memory_surface_rows_digest": "1475855ec85f128d9c35b8667d30be13044f29b017eb33f38456ffcd0433cb8d",
  "memory_surface_state_snapshot_digest": "284cf90a485db74c28e0d5e8c90cc3aceb4aac1f6073f4d9c1a0fade35623209"
}
```

## Acceptance

Iteration 5 passes if memory surface strength changes through serialized decay
or reinforcement policy and the update is replayable without hidden state.

Achieved: `True`.

Output digest: `e9b752b1bf5df9e4d58aa5da15c0a741df53b0e1237c9d5124390986ca8b89be`.
