# N08 Iteration 2 Fixture Manifest And Route-Use Trace Contract

Status: `passed`.

## Result

Iteration 2 defines the route-use and memory/trail fixture contract before any
positive memory probe. It does not emit route-use events or memory surfaces.

Key boundary:

```text
N06 route selection artifact != N08 route-use event
N08 route-use event = ordered, serialized, budget-audited consumption record
memory surface = experiment-local JSON artifact rows until native Phase 8 support
memory_or_trail_claim_allowed = false
```

## Route-Use Event Schema

Required fields:

- `route_use_event_id`
- `route_use_commit_status`
- `source_arbitration_record_digest`
- `source_candidate_set_digest`
- `selected_candidate_route_digest`
- `selected_route_id`
- `route_aspect_digest`
- `source_support_area_digest`
- `target_support_area_digest`
- `topology_commit_required`
- `event_time_key`
- `scheduler_event_index`
- `node_plus_packet_budget_before`
- `node_plus_packet_budget_after`
- `node_plus_packet_budget_error`
- `claim_flags`
- `route_use_event_digest`

Default topology commit requirement:
`False`.

The early N08 fixture explicitly does not require topology commit. Its route-use
event is a memory-lane consumption record, not topology mutation evidence.

Template provenance note: route-use events require
`source_arbitration_record_digest`, but the N06 SC6 closeout per-cycle rows
serialize native arbitration replay status and record IDs rather than the
positive arbitration digest directly. Iteration 3 must resolve and pin the
actual source arbitration digest when it emits MEM1 route-use events.

Template coverage note: Iteration 2 templates are deduplicated by selected
route and cover route A and route B shapes. Iteration 3 must emit route-use
events for all `4` N06 SC6
source cycles:

```json
[
  "cycle_0",
  "cycle_1",
  "cycle_2",
  "cycle_3"
]
```

## Memory Surface Schema

Storage format:
`experiment_local_serialized_json_artifact_rows`.

Required fields:

- `memory_surface_id`
- `memory_surface_kind`
- `route_use_event_digest`
- `memory_surface_key`
- `memory_surface_key_digest`
- `memory_policy_id`
- `memory_policy_digest`
- `memory_strength`
- `event_time_key`
- `scheduler_event_index`
- `node_plus_packet_budget_before`
- `node_plus_packet_budget_after`
- `node_plus_packet_budget_error`
- `memory_budget_surface`
- `memory_budget_before`
- `reinforcement_input`
- `decay_loss`
- `saturation_clamp_loss`
- `memory_budget_after`
- `memory_budget_error`
- `claim_flags`
- `memory_surface_digest`

Memory surface kind definitions:

- `trail`: serialized persistence of prior committed route use on a route/support/aspect key
- `affordance`: serialized prospective route capability signal derived from trail/support/aspect evidence, not a hidden preference

`memory_surface_key` is a canonical JSON object with fields:

```json
[
  "route_id",
  "source_support_area_digest",
  "target_support_area_digest",
  "route_aspect_digest",
  "memory_policy_id"
]
```

Digest rules:

```text
route_use_event_digest =
  sha256(canonical_json(route_use_event_without_route_use_event_digest))

memory_surface_key_digest =
  sha256(canonical_json(memory_surface_key))

memory_surface_digest =
  sha256(canonical_json(memory_surface_record_without_memory_surface_digest))
```

MEM2+ requires one of:
`['memory_surface_state_snapshot', 'memory_surface_rows']`.

MEM2+ evidence-row mapping:

```json
{
  "memory_strength_source": "MEM2+ evidence rows read memory_strength from serialized memory_surface_state_snapshot or memory_surface_rows",
  "memory_surface_digest_source": "memory_surface_digest",
  "memory_surface_policy_source": "memory_policy_id"
}
```

## Policies And Budgets

Default decay policy:
`exponential_per_memory_window`
with factor `0.9`.
Decay can only reduce memory strength:
`True`.

Default reinforcement policy:
`saturating_additive`
with amount
`0.25`.

Same-window order:
`['decay', 'reinforcement']`.

Memory budget equation:

```text
memory_budget_before + reinforcement_input - decay_loss - saturation_clamp_loss == memory_budget_after
```

Memory-budget row fields:

- `memory_budget_surface`
- `memory_budget_before`
- `reinforcement_input`
- `decay_loss`
- `saturation_clamp_loss`
- `memory_budget_after`
- `memory_budget_error`

Node-plus-packet budget remains a separate exact coherence accounting surface.

## Score Components

Memory-derived candidate score components:

```json
[
  "memory_trail_strength",
  "memory_surface_digest_match",
  "memory_recency_weight",
  "memory_decay_adjusted_strength"
]
```

Required `candidate_runtime_visible_inputs`:

```json
[
  "memory_surface_id",
  "memory_surface_digest",
  "memory_surface_state_snapshot_digest",
  "memory_policy_id",
  "route_use_event_digest",
  "memory_event_time_key"
]
```

## Event Ordering

```json
[
  "route_arbitration",
  "selected_route_use",
  "memory_update",
  "later_candidate_scoring",
  "native_route_arbitration"
]
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

Producers may schedule and record evidence only. They may not mutate memory
surfaces, node coherence, or packet ledgers; `step()` remains the packet
mutation boundary.

## Inherited Native Policy Blockers

The Iteration 1 native memory/trail policy blockers are carried forward:

- `native_route_conductance_memory_policy_missing`
- `native_trail_memory_surface_missing`
- `native_memory_surface_serialization_policy_missing`
- `native_memory_surface_keying_policy_missing`
- `native_memory_budget_accounting_policy_missing`
- `native_memory_cross_cycle_persistence_policy_missing`
- `native_memory_decay_policy_missing`
- `native_memory_reinforcement_policy_missing`
- `native_memory_candidate_score_component_semantics_missing`
- `native_memory_artifact_replay_validator_missing`

## Controls

| Control | Primary Blocker |
|---|---|
| `hidden_route_history` | `hidden_route_history` |
| `missing_route_use_event` | `missing_route_use_event` |
| `memory_surface_missing` | `memory_surface_missing` |
| `memory_surface_digest_mismatch` | `memory_surface_digest_mismatch` |
| `memory_surface_poisoned` | `memory_surface_poisoned` |
| `memory_policy_missing` | `memory_policy_missing` |
| `memory_policy_hidden_preference` | `memory_policy_hidden_preference` |
| `decay_policy_missing` | `decay_policy_missing` |
| `reinforcement_policy_missing` | `reinforcement_policy_missing` |
| `candidate_score_memory_digest_missing` | `candidate_score_memory_digest_missing` |
| `candidate_score_hidden_memory_input` | `candidate_score_hidden_memory_input` |
| `arbitration_memory_order_invalid` | `arbitration_memory_order_invalid` |
| `memory_budget_discontinuity` | `memory_budget_discontinuity` |
| `node_plus_packet_budget_discontinuity` | `node_plus_packet_budget_discontinuity` |
| `stale_memory_surface_read` | `stale_memory_surface_read` |
| `cross_cycle_memory_leak` | `cross_cycle_memory_leak` |
| `duplicate_memory_update` | `duplicate_memory_update` |
| `policy_disabled` | `policy_disabled` |
| `producer_mutation_boundary_violation` | `producer_mutation_boundary_violation` |
| `no_memory_surface_read_by_arbitration` | `no_memory_surface_read_by_arbitration` |
| `posthoc_memory_threshold_change` | `posthoc_memory_threshold_change` |
| `claim_promotion` | `claim_promotion` |

`hidden_route_history` and `memory_policy_hidden_preference` are distinct
failure modes.

## Checks

| Check | Passed |
|---|---|
| `claim_flags_all_false` | `True` |
| `committed_route_use_semantics_complete` | `True` |
| `control_blockers_distinct` | `True` |
| `controls_include_required_blockers` | `True` |
| `decay_policy_can_only_reduce_strength` | `True` |
| `decay_policy_schema_complete` | `True` |
| `event_ordering_contract_declared` | `True` |
| `hidden_route_history_and_hidden_preference_distinct` | `True` |
| `iteration_3_requires_all_n06_cycles` | `True` |
| `manifest_digest_stable_scope_declared` | `True` |
| `mem2_plus_requires_snapshot_or_rows` | `True` |
| `memory_budget_equation_declared` | `True` |
| `memory_probe_not_run` | `True` |
| `memory_strength_mapping_declared` | `True` |
| `memory_surface_budget_equation_terms_serialized` | `True` |
| `memory_surface_claim_flags_reference_frozen_set` | `True` |
| `memory_surface_digest_algorithm_declared` | `True` |
| `memory_surface_key_contract_complete` | `True` |
| `memory_surface_kind_definitions_declared` | `True` |
| `memory_surface_schema_required_fields_present` | `True` |
| `memory_surface_storage_experiment_local` | `True` |
| `native_policy_blockers_inherited` | `True` |
| `node_plus_packet_budget_separate` | `True` |
| `producer_step_boundary_declared` | `True` |
| `reinforcement_policy_schema_complete` | `True` |
| `route_use_claim_flags_reference_frozen_set` | `True` |
| `route_use_event_schema_required_fields_present` | `True` |
| `route_use_event_schema_requires_arbitration_digest` | `True` |
| `route_use_template_arbitration_digest_resolution_explicit` | `True` |
| `route_use_templates_cover_two_routes` | `True` |
| `route_use_templates_source_backed` | `True` |
| `runtime_visible_inputs_declared` | `True` |
| `same_window_update_order_serialized` | `True` |
| `score_component_names_match_baseline` | `True` |
| `source_baseline_digest_matches` | `True` |
| `source_baseline_passed` | `True` |
| `special_controls_present` | `True` |
| `support_anchors_present_in_templates` | `True` |
| `topology_commit_requirement_explicit` | `True` |

## Artifact Digests

```json
{
  "experiments/2026-05-N08-lgrc-memory-trail-affordance/configs/n08_fixture_manifest_v1.json": "be8556f209b0dd31ed0b9896c04e5a91fcdeca0efb7702ba53e48ea4202818c6",
  "experiments/2026-05-N08-lgrc-memory-trail-affordance/outputs/n08_iteration_1_baseline_inventory.json": "32f46adb7f07e78d391fd1160c4fc2e4513235371c29da115ab2762b112bf4c9"
}
```

## Acceptance Result

Achieved: `True`.

Manifest digest: `7dbcdf1ada38683a33abb1230a5354972fe9365bbe24ee54c448c9ca4110a85a`.
Validation digest: `1ad3ec9766390e621c5338671466f65654929d80643d3003efb1cac294f7779a`.
