# N06 Iteration 1: Baseline And Schema Inventory

Status: passed.

## Purpose

Iteration 1 is inventory-only. It runs no route-choice probes and does not
change `src/*`.

## N05 Inheritance

```json
{
  "claim_flags": {
    "agency_claim_allowed": false,
    "agentic_like_claim_allowed": false,
    "ant_colony_claim_allowed": false,
    "biological_claim_allowed": false,
    "goal_proxy_regulation_claim_allowed": false,
    "identity_acceptance_claim_allowed": false,
    "locomotion_like_claim_allowed": false,
    "memory_or_trail_claim_allowed": false,
    "movement_claim_allowed": false,
    "rc_identity_collapse_claim_allowed": false,
    "semantic_choice_claim_allowed": false,
    "unrestricted_movement_claim_allowed": false
  },
  "inherited_background": "oscillator_circuit_background_only",
  "n06_inheritance_claims": {
    "agency_inherited": false,
    "identity_acceptance_inherited": false,
    "locomotion_inherited": false,
    "memory_or_trail_inherited": false,
    "semantic_choice_inherited": false
  },
  "n06_ready": true,
  "o6_primary_blocker": "missing_route_conductance_memory_policy",
  "o6_route_coupled_oscillator_supported": false,
  "source_artifact": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json",
  "source_status": "passed",
  "strongest_claim_ceiling": "self_sustained_oscillator_candidate",
  "strongest_supported_o_level": "O5"
}
```

N06 inherits only oscillator/circuit background from N05. It does not inherit
semantic choice, memory/trail, agency, identity, ACO, locomotion, or unrestricted
movement claims.

## Native Route-Arbitration Contract

Native route arbitration is LGRC-3/topology-changing-causal-history gated:

```json
{
  "causal_layer_mode": "topology_changing_causal_history",
  "causal_pulse_substrate_surface_lineage_transport_supported": true,
  "causal_topology_integration_allowed": true,
  "causal_topology_state_reabsorption_supported": true,
  "disabled_policy_requires_enabled_false": true,
  "lgrc2_native_route_arbitration_allowed": false,
  "lgrc_runtime_level": "lgrc3",
  "n06_default_native_lgrc_route_arbitration_policy": "score_ordered_topology_route_candidates",
  "native_lgrc_route_arbitration_enabled": true,
  "native_lgrc_route_arbitration_policy_gate": "policy != disabled"
}
```

Validator:

```json
{
  "optional": [
    "surface_rows",
    "surface_lineage_records",
    "topology_events",
    "topology_state_reabsorption_records",
    "production_results",
    "budget_tolerance"
  ],
  "required": [
    "events",
    "candidate_route_records",
    "candidate_set_records",
    "route_arbitration_records"
  ]
}
```

Validator failure modes:

```json
{
  "budget_invalid": "native_route_arbitration_budget_invalid",
  "budget_mismatch": "native_route_candidate_budget_mismatch",
  "candidate_digest_mismatch": "candidate_route_digest_mismatch",
  "candidate_order_inversion": "native_route_arbitration_order_invalid:candidate_set_before_candidate",
  "candidate_set_digest_mismatch": "candidate_set_digest_mismatch",
  "candidate_set_missing_candidate": "candidate_set_missing_candidate",
  "candidate_source_surface_missing": "native_route_candidate_unknown_source_surface",
  "claim_promotion": "native_route_arbitration_claim_promotion_blocked",
  "disabled_policy": "native_route_arbitration_policy_disabled",
  "duplicate_arbitration": "duplicate_native_route_arbitration",
  "duplicate_candidate": "duplicate_native_route_candidate",
  "duplicate_candidate_set": "duplicate_native_route_candidate_set",
  "hidden_input": "native_route_arbitration_hidden_input_rejected",
  "no_candidates": "native_route_arbitration_no_candidates",
  "order_invalid": "native_route_arbitration_order_invalid",
  "selected_candidate_outside_set": "native_route_arbitration_selected_candidate_outside_set",
  "unresolved_tie": "native_route_arbitration_unresolved_tie"
}
```

Reason codes:

```json
[
  "native_route_arbitration_selected_highest_score",
  "native_route_arbitration_selected_declared_local_preference",
  "native_route_arbitration_no_candidates",
  "native_route_arbitration_unresolved_tie",
  "native_route_arbitration_policy_disabled",
  "native_route_arbitration_budget_invalid",
  "native_route_arbitration_order_invalid",
  "native_route_arbitration_hidden_input_rejected"
]
```

Score invariant:

```json
{
  "enforced_by": "LGRC9V3NativeRouteCandidateRecord.__post_init__",
  "owner": "native_lgrc9v3_candidate_record_contract",
  "rule": "candidate_route_score == sum(candidate_score_components)",
  "tolerance": "1e-12"
}
```

Candidate-set ordering and ties:

```json
{
  "candidate_set_ordering": {
    "default_for_n06": "score_desc_then_candidate_id",
    "digest_ascending_order": [
      "candidate_route_digest ascending"
    ],
    "iteration_2_requirement": "fixture manifest must declare the order key before candidate emission; list order alone is not native evidence",
    "policy_configurable_values": [
      "score_desc_then_candidate_id",
      "digest_ascending"
    ],
    "score_desc_then_candidate_id_order": [
      "candidate_route_score descending",
      "candidate_order_key ascending",
      "candidate_route_id ascending"
    ]
  },
  "declared_tiebreaker_serialization": {
    "blocked_sources": [
      "fixture hidden order",
      "experiment if/else",
      "Python/list order unless declared by candidate_set_order_key",
      "report-side selected route"
    ],
    "policy": "declared_runtime_visible_tiebreaker",
    "serialized_fields": [
      "candidate_set.unresolved_tie_policy",
      "candidate_set.candidate_set_order_key",
      "candidate.candidate_order_key",
      "candidate.candidate_route_digest",
      "arbitration_record.arbitration_runtime_visible_inputs"
    ]
  }
}
```

## Context/Affordance Mapping

```json
{
  "allowed_native_field_mappings": [
    {
      "field": "candidate_score_components",
      "native": true,
      "use": "numeric context/affordance contribution; route score must equal the component sum"
    },
    {
      "field": "candidate_runtime_visible_inputs",
      "native": true,
      "use": "serialized names of context inputs consumed by a candidate"
    },
    {
      "field": "arbitration_runtime_visible_inputs",
      "native": true,
      "use": "serialized names of inputs consumed by arbitration"
    },
    {
      "field": "causal_pulse_substrate_surface_rows",
      "native": true,
      "use": "context from local_support_mass, boundary_polarity_score, proper_time_phase, surface_deformation, route_local_pulse_contact, or feedback_eligibility"
    },
    {
      "field": "route_aspect_mass_polarity_channel_fields",
      "native": true,
      "use": "route aspect context from serialized route semantics"
    },
    {
      "field": "experiment_local_compatibility_gate_record",
      "native": false,
      "use": "exploratory scaffold only; not native route-arbitration context"
    }
  ],
  "blocked_context_sources": [
    "hidden_fixture_array",
    "hidden_fixture_state",
    "experiment_if_else",
    "preselected_sink_id",
    "posthoc_threshold",
    "report_code"
  ],
  "compatibility_gate_options": [
    "native_score_components_with_threshold_interpretation",
    "experiment_local_gate_records"
  ],
  "dedicated_native_context_surface_exists": false,
  "mapping_elimination_criteria": [
    "reject if context state is not serialized in runtime-visible fields",
    "reject if compatibility is decided by fixture/report code",
    "reject if the mapping requires hidden context arrays",
    "reject if the mapping cannot reconstruct A/B selection from artifacts",
    "label as experiment-local if it cannot be expressed by native fields"
  ],
  "preferred_default_native_mapping_for_iteration_2": {
    "arbitration_context_sources": "arbitration_runtime_visible_inputs",
    "candidate_context_sources": "candidate_runtime_visible_inputs",
    "default_compatibility_gate": "native_score_components_with_threshold_interpretation",
    "fallback_only": "experiment_local_compatibility_gate_record",
    "score_surface": "candidate_score_components",
    "surface_row_inputs": "optional source evidence when context is derived from native causal pulse-substrate rows"
  },
  "required_iteration_2_decision": "map context states A/B to native score/runtime-visible input fields or explicitly label an experiment-local gate"
}
```

N06 has no dedicated native `context_surface` record type at baseline. Iteration
2 must choose the concrete mapping before fixture probes run.

## SC Row Schema

Required fields:

- `run_id`
- `sc_level`
- `sc_level_is_evidence_classification`
- `claim_ceiling`
- `claim_flags`
- `runtime_family`
- `lgrc_runtime_level`
- `source_native_surfaces`
- `fixture_id`
- `source_node_id`
- `candidate_route_records`
- `candidate_route_digests`
- `candidate_set_record`
- `candidate_set_digest`
- `native_route_arbitration_record`
- `native_route_arbitration_digest`
- `selected_candidate_route_digest`
- `rejected_candidate_route_digests`
- `context_surface`
- `context_surface_digest`
- `context_relation`
- `context_runtime_visible`
- `selection_rule`
- `selection_reason_code`
- `score_components`
- `compatibility_gate_components`
- `arbitration_window_id`
- `candidate_source_surface_digest`
- `candidate_source_producer_record_id`
- `candidate_source_topology_state_reabsorption_digest`
- `route_intent`
- `selected_topology_event_id`
- `event_time_key`
- `scheduler_event_index`
- `causal_epoch`
- `node_proper_time`
- `scheduled_packet_id`
- `processed_packet_id`
- `node_plus_packet_budget_before`
- `node_plus_packet_budget_after`
- `node_plus_packet_budget_error`
- `producer_records`
- `producer_boundary`
- `artifact_only_replay`
- `controls`
- `blocked_claims`

## Claim Boundary

- `agency_claim_allowed` = `False`
- `agentic_like_claim_allowed` = `False`
- `ant_colony_claim_allowed` = `False`
- `biological_claim_allowed` = `False`
- `goal_proxy_regulation_claim_allowed` = `False`
- `identity_acceptance_claim_allowed` = `False`
- `locomotion_like_claim_allowed` = `False`
- `memory_or_trail_claim_allowed` = `False`
- `movement_claim_allowed` = `False`
- `rc_identity_collapse_claim_allowed` = `False`
- `semantic_choice_claim_allowed` = `False`
- `unrestricted_movement_claim_allowed` = `False`

## Source Artifacts

| Name | Exists | SHA-256 | Path |
|---|---:|---|---|
| `n06_readme` | `True` | `831417f96820f0eefc1679d68c3745936c117d0425960e1efd107dd6d572b556` | `experiments/2026-05-N06-lgrc-semantic-route-choice/README.md` |
| `n06_plan` | `True` | `e988d66c3170d7acefec4ef655fba27940ac0ed3fb2d2de0df3d26342ebb5838` | `experiments/2026-05-N06-lgrc-semantic-route-choice/implementation/SemanticRouteChoiceImplementationPlan.md` |
| `n06_checklist` | `True` | `b99c9d15e5aa3db067300d3160c2cb07fa6738064bd6df2c47088bb27a8b159b` | `experiments/2026-05-N06-lgrc-semantic-route-choice/implementation/SemanticRouteChoiceImplementationChecklist.md` |
| `n06_implementation_readme` | `True` | `285990f5d6e44f143d2bdaaf7f04220da52de8efbb7d2382af74317a1f64640d` | `experiments/2026-05-N06-lgrc-semantic-route-choice/implementation/README.md` |
| `n05_n11_roadmap` | `True` | `fcc30afaeecf6410ccd94ca453f45a6a3d4f51286b22731e47caa3312cf7b0a0` | `experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md` |
| `n05_closeout` | `True` | `38c9b37186d1139a3ce7d3cf324e8f9a2b649099aa8bddd79c11eb346a86f1c8` | `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json` |
| `n05_closeout_report` | `True` | `fa9d3b7f7d44ddc03e5a14537f4d06fb6540019c0d3251dd503b0182d1a425c2` | `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_8_o6_closeout.md` |
| `n04_native_route_arbitration_rerun` | `True` | `4d28f1fa0d2822de374d09ae20927eac6c682c112b7434254010890c059694c1` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter21b_native_lgrc_route_arbitration_rerun.json` |
| `n04_native_route_arbitration_rerun_report` | `True` | `95a22fdfeddf38bc55456c648907f03c9a2acea452c038ebb670f23fa90be4ca` | `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter21b_native_lgrc_route_arbitration_rerun.md` |
| `n04_identity_native_route_arbitrated_topology` | `True` | `65477fda0529097244fa7191df540721f8f148526619193007e639e7d4dc6714` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json` |
| `phase8_native_route_arbitration_closeout` | `True` | `1d3166a3ca4b08cf88aa50b6054782442e7739b11eb2d2e7157c0581d830292c` | `implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.md` |
| `phase8_native_route_arbitration_closeout_json` | `True` | `cabc1f5b81fdb19154d778b04463f74f32e82653db6291daa62b1e5128d01b65` | `implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json` |
| `lgrc9v3_contract_source` | `True` | `0c50cffe638ff18ada4375f8e3acd897e054eb48d75137da735d6d5a4cdafe8a` | `src/pygrc/models/lgrc_9_v3_contract.py` |
| `lgrc9v3_runtime_source` | `True` | `70c065b003ebdd4351fad7b5089abc27557dee9a04b6e1c7834e1d01bd5fa6ee` | `src/pygrc/models/lgrc_9_v3_runtime.py` |
| `lgrc9v3_telemetry_source` | `True` | `4af287dad2ec42bec6a619d294238e8f9fb915821374207a694afc553e57d026` | `src/pygrc/telemetry/lgrc9v3_contract.py` |

## Artifact Digests

```json
{
  "claim_boundary_digest": "ffcf9f3262407e22fdad4c175e46b4759fe8ef86a17e7349c3442493bbe53607",
  "context_affordance_inventory_digest": "843d173ca5132180492f36dd40c087eb1142a3462737a218052e77f4592cc294",
  "native_route_arbitration_surfaces_digest": "53ef97f95efd039d518fedcfa50108f052ef6beaf2c2250a58ef695e7573cb95",
  "sc_ladder_schema_digest": "4ac6a7742fd5dcd167506e3a0f4fbc3ec063274fe1943961b5f574e32c7c9396",
  "source_artifacts_digest": "d6125fd11ca305ee7235b9e60ae8509cdba8839c3e174234fb1b4e4125ca5934"
}
```

## Acceptance Result

Achieved. N06 has a source-backed baseline inventory, frozen SC-ladder row
schema, explicit blocked claim flags, native LGRC-3 route-arbitration gate
record, context/affordance mapping inventory, and no route-choice probe
evidence or claim promotion.
