# N08 Iteration 1 Baseline And Schema Inventory

Status: `passed`.

## Result

Iteration 1 built a source-backed baseline inventory from existing N05, N06,
and N07 closeout artifacts only. No N08 memory probe was run.

The current N08 starting boundary is:

```text
MEM evidence = not yet produced
native memory/trail surface = missing
route-score component carrier = available for non-forbidden serialized keys
memory/trail semantics = experiment-local until a later Phase 8 task exists
memory_or_trail_claim_allowed = false
```

## Inherited Evidence Inventory

N05:

- strongest O-level: `O5`
- claim ceiling: `self_sustained_oscillator_candidate`
- O6 supported: `False`
- O6 blocker: `missing_route_conductance_memory_policy`
- route-aspect digest: `4d10620cbdc9c7da9a1a1c5b510a5a03350f055d8139037876ce57524988e8d1`
- route conductance memory digest: `None`
- Phase 3 native policy blockers:
  `['missing_serialized_custom_node_potentials_policy', 'missing_serialized_potential_inversion_policy', 'missing_flux_facilitated_metric_map_policy', 'missing_serialized_delayed_passive_response_policy', 'missing_route_conductance_memory_policy']`

N06:

- strongest SC-level: `SC6`
- claim ceiling: `artifact_only_semantic_route_choice_candidate`
- cycle count: `4`
- candidate route records present: `True`
- candidate set records present: `True`
- native route-arbitration records present: `True`
- N06 selection counts as N08 route use: `False`

N07:

- frozen ceiling: `ID6`
- C3 class: `bounded_non_destructive_exchange`
- support area id: `n07_support_area_A_v1`
- support area digest: `c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb`
- runtime identity acceptance allowed: `False`

## Native Contract Inventory

Native route-arbitration forbidden input keys:

```json
[
  "experiment_if_else",
  "hidden_fixture_array",
  "hidden_fixture_state",
  "posthoc_threshold",
  "preselected_sink_id",
  "report_code"
]
```

Proposed N08 memory score components:

- `memory_trail_strength`: allowed as route-score key = `True`, native memory semantics = `False`
- `memory_surface_digest_match`: allowed as route-score key = `True`, native memory semantics = `False`
- `memory_recency_weight`: allowed as route-score key = `True`, native memory semantics = `False`
- `memory_decay_adjusted_strength`: allowed as route-score key = `True`, native memory semantics = `False`

This means the current native candidate-score contract can carry these names as
serialized score-component keys, but it does not supply memory/trail semantics
by itself. N08 must serialize route-use events, memory surfaces, memory policy,
and memory state snapshots as experiment-local artifacts unless a Phase 8 task
adds native memory support.

Missing native memory/trail policy surfaces:

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

## Frozen MEM Schema

The MEM0-MEM6 ladder is frozen as evidence classification only. Claim flags are
separate from MEM levels.

Frozen row fields:

- `row_id`
- `mem_level`
- `mem_level_is_evidence_classification`
- `claim_ceiling`
- `claim_flags`
- `source_artifacts`
- `source_reports`
- `route_use_event_id`
- `route_use_event_digest`
- `route_use_commit_status`
- `route_id`
- `selected_route_id`
- `route_aspect_digest`
- `source_arbitration_record_digest`
- `selected_candidate_route_digest`
- `rejected_candidate_route_digests`
- `memory_surface_id`
- `memory_surface_digest`
- `memory_surface_key`
- `memory_surface_key_digest`
- `source_support_area_digest`
- `target_support_area_digest`
- `support_area_id`
- `support_area_digest`
- `memory_policy_id`
- `memory_policy_digest`
- `decay_policy_id`
- `reinforcement_policy_id`
- `memory_surface_state_snapshot`
- `memory_surface_state_snapshot_digest`
- `candidate_route_digests`
- `candidate_set_digest`
- `native_route_arbitration_record_digest`
- `event_time_key`
- `scheduler_event_index`
- `node_plus_packet_budget_before`
- `node_plus_packet_budget_after`
- `node_plus_packet_budget_error`
- `memory_budget_surface`
- `memory_budget_before`
- `memory_budget_after`
- `memory_budget_error`
- `native_support_status`
- `native_policy_blockers`
- `visual_reference`
- `visual_is_evidence_source`

## Memory Surface Key Contract

`memory_surface_key` is frozen as a canonical JSON object, not a scalar string.
It must contain exactly the replay-relevant route/support/policy identity
fields needed by later memory rows:

- `route_id`
- `source_support_area_digest`
- `target_support_area_digest`
- `route_aspect_digest`
- `memory_policy_id`

Digest rule:

```text
memory_surface_key_digest = sha256(canonical_json(memory_surface_key))
```

The row schema therefore also includes `memory_surface_key_digest`.
Iteration 2 must instantiate this contract in the fixture manifest before
positive memory probes run.

## Claim Boundary

All claim flags remain false. The narrow
`memory_or_trail_claim_allowed` flag requires MEM6 artifact-only replay and
does not promote ACO, agency, intention, goal regulation, RC identity collapse,
identity acceptance, locomotion-like behavior, biological behavior, personhood,
unrestricted identity, or unrestricted movement.

Promotion criteria are required gates, not achieved Iteration 1 results:

- MEM6 required
- artifact-only replay passes
- route-use events replay
- memory surface state reconstructs
- decay/reinforcement policies replay
- memory-derived candidate scores recompute exactly
- controls fail with distinct blockers
- node-plus-packet budget passes
- memory budget passes
- does not promote ACO, agency, identity, or locomotion claims

## Checks

| Check | Passed |
|---|---|
| `baseline_json_schema_self_validates` | `True` |
| `claim_flags_all_false` | `True` |
| `forbidden_inputs_inventoried` | `True` |
| `frozen_row_schema_has_budget_split` | `True` |
| `frozen_row_schema_has_memory_snapshot` | `True` |
| `mem_ladder_complete` | `True` |
| `memory_or_trail_requires_mem6` | `True` |
| `memory_probe_not_run` | `True` |
| `memory_surface_key_contract_explicit` | `True` |
| `missing_native_memory_policy_surfaces_recorded` | `True` |
| `n05_o5_inventory_present` | `True` |
| `n05_o6_blocker_recorded` | `True` |
| `n05_route_memory_absent` | `True` |
| `n05_status_passed` | `True` |
| `n06_candidate_route_records_present` | `True` |
| `n06_candidate_score_components_present` | `True` |
| `n06_candidate_set_records_present` | `True` |
| `n06_cycle_structure_valid` | `True` |
| `n06_native_route_arbitration_records_present` | `True` |
| `n06_sc6_inventory_present` | `True` |
| `n06_selection_not_route_use` | `True` |
| `n06_status_passed` | `True` |
| `n07_11b_report_digest_recorded` | `True` |
| `n07_bounded_exchange_inventory_present` | `True` |
| `n07_status_passed` | `True` |
| `n07_support_fields_present` | `True` |
| `native_candidate_score_components_can_carry_memory_keys_by_name` | `True` |
| `native_memory_semantics_missing_recorded` | `True` |
| `promotion_criteria_encoded_as_required_gates` | `True` |
| `proposed_memory_score_components_not_forbidden` | `True` |
| `src_clean_for_iteration_1` | `True` |

## Artifact Digests

```json
{
  "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json": "38c9b37186d1139a3ce7d3cf324e8f9a2b649099aa8bddd79c11eb346a86f1c8",
  "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_8_sc6_closeout.json": "c020d954bdf5bfc53da9d550cd313f660af07f4b47e70b4c5102637500cc30bf",
  "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_11b_neutral_absorber_reservoir.json": "0a45dfa122bc2f727501208ed3731444907060f67c79a3ea56921e71f1b2a497",
  "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_12_long_horizon_compatibility_closeout.json": "af966c2f8063d88078d7a1c5fb9cfc0286b383ce7970221bdd8248e443c5c189"
}
```

## Source Report Digests

```json
{
  "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_8_o6_closeout.md": "fa9d3b7f7d44ddc03e5a14537f4d06fb6540019c0d3251dd503b0182d1a425c2",
  "experiments/2026-05-N06-lgrc-semantic-route-choice/reports/n06_iteration_8_sc6_closeout.md": "994a49ee0727a10b28f974bb08dbf6573ee0e3e104c861238b1c5f0594aece1f",
  "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_11b_neutral_absorber_reservoir.md": "866f767ca4b098b46aad4f5833f9644092eaa028bb9e4c742763fe612b238354",
  "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_12_long_horizon_compatibility_closeout.md": "33bfb5c32c7212cce496d1d0e2495dda95b9627ffe510fe79afe4981548d7bc8"
}
```

## Acceptance Result

Achieved: `True`.

Inventory digest scope:

```json
{
  "excluded": [
    "generated_at",
    "inventory_digest"
  ],
  "included": "all inventory fields except generated_at and inventory_digest",
  "stable_across_same_inputs": true
}
```

Inventory digest: `c27c011e1875c7e967aac398818c2a72b55adfb064752b594524e91530ed20de`.
