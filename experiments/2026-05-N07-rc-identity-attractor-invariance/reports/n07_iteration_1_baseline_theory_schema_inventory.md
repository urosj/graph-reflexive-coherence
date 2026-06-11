# N07 Iteration 1: Baseline And Theory/Schema Inventory

Status: passed.

Generated: `2026-06-06T07:59:32.588428+00:00`

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/build_n07_iteration_1_baseline_theory_schema_inventory.py
```

## Purpose

Iteration 1 is inventory-only. It runs no identity probes, emits no support
rows, and does not change `src/*`.

## Boundaries

- N06 is route-choice context only, not identity evidence.
- N05 is oscillator context only, not identity, memory, or agency evidence.
- N04 Iteration 22/22-B artifacts are boundary/negative evidence: they show
  topology-aware continuity but still block RC identity through topology.
- ID levels are evidence classifications, not claim flags.
- Arc of Becoming sources are recorded by title only, not by filesystem path.

## Source Status

```text
(no src/* status entries)
```

## Theory Gates

```json
[
  "grc_v2_directed_flux_identity_basin",
  "grc_v3_basin_attribute_bundle",
  "grc9_nine_port_basin_chart",
  "lgrc_proper_time_identity_window",
  "lgrc_lineage_current_identity",
  "pulse_substrate_identity_carrier_taxonomy",
  "coherence_state",
  "continuity_equation",
  "coherence_functional",
  "global_coherence_invariance",
  "identity_basin_stability",
  "attractivity",
  "invariance",
  "reflexive_closure",
  "coherence_compatibility",
  "local_irreducibility_agency_boundary"
]
```

## Available Native Surfaces

| Surface | Minimum level | N07 use | Claim boundary |
|---|---:|---|---|
| `native_causal_pulse_substrate_surface` | `lgrc2` | surface/support evidence only | surface row is not identity carrier by itself |
| `surface_lineage_transport` | `lgrc3` | lineage-current support across topology changes | lineage evidence is not RC identity acceptance |
| `topology_state_reabsorption` | `lgrc3` | state/ledger consistency after topology mutation | reabsorption is runtime hygiene, not identity |
| `native_route_arbitration` | `lgrc3` | route-fed context for C4 only | route choice is not identity |
| `packet_ledger_and_budget_accounting` | `lgrc2` | node-plus-packet conservation for every candidate | budget conservation is necessary but insufficient |
| `proper_time_identity_evaluation` | `lgrc2_or_experiment_local` | proper-time persistence window if available | persistence window is evidence, not unrestricted identity |
| `identity_acceptance_event_contract` | `unknown_or_experiment_local` | only as explicit native contract if present; otherwise blocked | no runtime identity-acceptance event in Iteration 1 |
| `telemetry_export_surfaces` | `lgrc2_lgrc3_by_surface` | artifact-only replay inputs | telemetry is evidence transport only |

## ID-Ladder Schema

| ID level | Name | Claim ceiling |
|---|---|---|
| `ID0` | no_identity_evidence | `no_identity_evidence` |
| `ID1` | runtime_visible_support_area_candidate | `support_area_candidate` |
| `ID2` | stable_basin_candidate | `stable_basin_candidate` |
| `ID3` | attractor_candidate | `attractor_candidate` |
| `ID4` | invariant_basin_candidate | `invariant_basin_candidate` |
| `ID5` | reflexively_self_maintaining_identity_candidate | `reflexively_self_maintaining_identity_candidate` |
| `ID6` | artifact_only_rc_identity_acceptance_candidate | `experiment_local_rc_identity_acceptance_candidate` |

Required row fields:

```text
row_id
id_level
topology_family_id
composite_topology_id
candidate_identity_carrier_type
identity_carrier_surface
support_area_id
support_area_digest
source_artifacts
source_artifact_sha256
source_reports
runtime_family
implementation_surface
gate_vector
derived_id_ceiling
primary_blocker
native_support_status
native_observables_used
experiment_local_observables_used
native_policy_blockers
becoming_class_status
probe_role
boundary_rung
support_dependency_status
withdrawal_test_status
naturalization_rung
activity_history_digest
claim_flags
visual_reference
visual_is_evidence_source
```

Gate-vector values:

```text
pass
fail
blocked
not_measured
not_applicable
```

Schema field definitions:

```json
{
  "activity_history_digest_method": "sha256 of canonical JSON over orient/observe/classify/probe/withdraw/naturalize/integrate events; null if no activity history exists",
  "experiment_local_observables_used_format": "list of declared experiment-local observable ids consumed by the row",
  "gate_vector_allowed_values": [
    "pass",
    "fail",
    "blocked",
    "not_measured",
    "not_applicable"
  ],
  "implementation_surface_allowed_values": [
    "experiment_local",
    "native_lgrc_telemetry",
    "native_causal_pulse_substrate_surface",
    "surface_lineage_transport",
    "topology_state_reabsorption",
    "native_route_arbitration",
    "proper_time_identity_evaluation",
    "artifact_only_validator",
    "not_applicable"
  ],
  "native_observables_used_format": "list of runtime-visible LGRC/native observable ids consumed by the row",
  "native_support_status_allowed_values": [
    "pure_native",
    "mixed_native_experiment_local",
    "experiment_local",
    "blocked"
  ],
  "runtime_family_allowed_values": [
    "LGRC9V3",
    "experiment_local",
    "hybrid_lgrc9v3_experiment_local",
    "not_applicable"
  ],
  "source_artifacts_format": "list of objects with name, path, exists, sha256, status, claim_ceiling, primary_blocker when available",
  "source_reports_format": "list of objects with name, path, exists, sha256",
  "visual_is_evidence_source_format": "boolean; must be false for Iteration 1 and for any visual-only reference without source artifact backing",
  "visual_reference_format": "optional relative path or null; visual references are illustrative unless visual_is_evidence_source is explicitly true"
}
```

## Becoming-Method Schema

```json
{
  "becoming_class_status": [
    "observation_tag",
    "reusable_class",
    "generative_class",
    "coherence_preserving_class"
  ],
  "boundary_rung": [
    "eligible_state",
    "event",
    "substrate_consequence",
    "structured_consequence",
    "source_specific_expression",
    "recurrence_or_continuation",
    "natural_regime_expression"
  ],
  "naturalization_rung": [
    "Nat0_probe_dependent_expression",
    "Nat1_probe_weakened_expression",
    "Nat2_regime_assisted_expression",
    "Nat3_endogenous_precondition_formation",
    "Nat4_native_expression",
    "Nat5_recurrent_native_expression",
    "Nat6_self_interrogating_regime",
    "not_applicable"
  ],
  "probe_role": [
    "none",
    "diagnostic_probe",
    "constructive_probe",
    "boundary_probe",
    "withdrawal_probe",
    "naturalization_probe"
  ],
  "support_dependency_status": [
    "not_tested",
    "probe_dependent",
    "weakened_support_survives",
    "regime_assisted",
    "endogenous_precondition_candidate",
    "native_expression_candidate",
    "recurrent_native_expression_candidate"
  ],
  "withdrawal_test_status": [
    "not_tested",
    "support_weakened_passed",
    "support_removed_passed",
    "support_removed_failed",
    "not_applicable"
  ]
}
```

## Topology Schema

First manifest families:

```text
n07_T1_support_area_minimal
n07_T2_stable_well_basin
n07_T3_attractor_neighborhood
n07_T5_lineage_current_invariance
```

Composite suite:

```text
n07_C1_recurrent_single_basin_identity_candidate
n07_C2_lineage_current_topology_mutating_identity_candidate
n07_C3_competing_basin_compatibility_candidate
n07_C4_route_fed_route_independent_identity_candidate
n07_C5_movement_carried_movement_independent_identity_candidate
n07_C6_parent_child_refinement_identity_boundary_candidate
```

## Identity Carrier Taxonomy

```json
{
  "eligible_identity_carrier": "coherence_basin",
  "rule": "non-coherence-basin carriers cannot derive an ID ceiling above ID0",
  "supporting_evidence_only": [
    "surface_row",
    "deformation_token",
    "boundary_signal",
    "route_selection",
    "movement_trace",
    "topology_event",
    "lineage_record",
    "topology_state_reabsorption_record"
  ]
}
```

## Claim Flags

```json
{
  "agency_claim_allowed": false,
  "agentic_like_claim_allowed": false,
  "ant_colony_claim_allowed": false,
  "biological_claim_allowed": false,
  "goal_proxy_regulation_claim_allowed": false,
  "identity_acceptance_claim_allowed": false,
  "intention_claim_allowed": false,
  "locomotion_like_claim_allowed": false,
  "memory_or_trail_claim_allowed": false,
  "movement_claim_allowed": false,
  "personhood_claim_allowed": false,
  "rc_identity_collapse_claim_allowed": false,
  "semantic_choice_claim_allowed": false,
  "unrestricted_identity_claim_allowed": false,
  "unrestricted_movement_claim_allowed": false
}
```

## Canonical Controls

```text
label_only_null_topology
missing_support_area
external_label_only
duplicate_support_row
budget_discontinuity
stale_node_id_replay
missing_topology_state_reabsorption
lineage_map_scrambled
support_drift_beyond_threshold
unstable_basin_no_local_well
hidden_potential_or_report_side_well_score
posthoc_threshold_change
identity_threshold_missing
wrong_support_area
no_reentry
closure_not_consumed_by_later_cycle
improper_proper_time_threshold
failed_persistence
non_attractive_flux
wrong_basin
wrong_polarity
subthreshold_flux
hidden_route_context_steering
destructive_interference
ambiguous_overlap
hidden_support_field
producer_mutation_boundary_violation
direct_state_or_topology_rewrite
unauthorized_identity_acceptance_event
identity_claim_promotion
agency_claim_promotion
```

## Inherited Boundaries

```json
{
  "n04_22": {
    "attempted_promotion": "rc_identity_through_topology_mutation_candidate",
    "boundary_use": "negative_boundary_evidence_not_n07_identity_support",
    "identity_acceptance_supported": false,
    "primary_blocker": "rc_identity_basin_invariance_not_validated_across_topology_mutation",
    "rc_identity_supported": false,
    "source_artifact": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22_identity_through_topology_mutation_boundary.json",
    "source_status": "passed"
  },
  "n04_22b": {
    "attempted_promotion": "rc_identity_through_native_route_arbitrated_topology_candidate",
    "boundary_use": "negative_boundary_evidence_not_n07_identity_support",
    "identity_acceptance_supported": false,
    "primary_blocker": "rc_identity_basin_invariance_not_validated_across_topology_mutation",
    "rc_identity_supported": false,
    "source_artifact": "experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json",
    "source_status": "passed"
  },
  "n05": {
    "agency_inherited": false,
    "identity_inherited": false,
    "inherited_background": "oscillator_circuit_background_only",
    "memory_or_trail_inherited": false,
    "source_artifact": "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json",
    "source_status": "passed",
    "strongest_claim_ceiling": "self_sustained_oscillator_candidate",
    "strongest_supported_o_level": "O5"
  },
  "n06": {
    "agency_inherited": false,
    "identity_inherited": false,
    "inherited_background": "route_choice_context_only",
    "semantic_choice_claim_allowed": false,
    "source_artifact": "experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_8_sc6_closeout.json",
    "source_status": "passed",
    "strongest_claim_ceiling": "artifact_only_semantic_route_choice_candidate",
    "strongest_supported_sc_level": "SC6"
  }
}
```

## Artifact Digests

```json
{
  "becoming_schema_digest": "6ad45d6586678d977ab98f8a09c434031e2276e54d6d6c6e9bec55b58284d551",
  "claim_flags_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_taxonomy_digest": "cb5dc4c3cbfcfc0fc16a4f342da65c2d76998b5160d78678bfbec7372b0ff873",
  "id_ladder_schema_digest": "afc1c4ae4e0a114c1b0af8f1f13804b6893420ba9e8ac6d76a02c9d0b3ecf8d3",
  "native_surfaces_digest": "8db53ef65e8ef3e67c87ae00eee75c569155dd6608adda499f0c64cf2c8f96a0",
  "source_artifacts_digest": "d33b076cd089bcf16609831b85baf028b2c402766c6f9eddcf5689d2986e8e50",
  "theory_gates_digest": "7101f45f81f6d23fce7eeeafde217e5a28f135446012e73a8e6d0241fa6bfc00",
  "topology_schema_digest": "fe480f0a797cf73b47a185aa0b50cfcdf4a0963ea4e7161694cd8031570d7d75"
}
```

## Artifact Inventory

| Name | Exists | SHA-256 | Path |
|---|---:|---|---|
| `n07_readme` | `True` | `5e61f44ceca04afbc4fa3385b17b938375ccd35adb39b120432a5884dc6b22bb` | `experiments/2026-05-N07-rc-identity-attractor-invariance/README.md` |
| `n07_plan` | `True` | `cfc4b762ebf0d206a184e436d3f20d324faac22e8278b15ebc00452cb1fb3ecc` | `experiments/2026-05-N07-rc-identity-attractor-invariance/implementation/RCIdentityAttractorInvarianceImplementationPlan.md` |
| `n07_checklist` | `True` | `461660f93f711ca9fe80d7baff961230cb70002e95aa4ba7a3d4acc01e3645d8` | `experiments/2026-05-N07-rc-identity-attractor-invariance/implementation/RCIdentityAttractorInvarianceImplementationChecklist.md` |
| `n07_implementation_readme` | `True` | `92e7c1162560fd7bba00f1bf97777c5417541985af274acc29d0811dc58bb26b` | `experiments/2026-05-N07-rc-identity-attractor-invariance/implementation/README.md` |
| `n05_n11_roadmap` | `True` | `fbb55c00c42877ee3c0f0ab7116534d8d33536cb3430a33998990c43e95a0f75` | `experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md` |
| `rc_identity_choice_abundance` | `True` | `a9d49332b25d01511c8731a2478de6321792137f645cef32e3be01cc94f0fbe5` | `papers/2025-11-RC-IdentityChoiceAbundance.md` |
| `grc_v2` | `True` | `ddcd55f7a322593572da029e1defaf142acd4dd5d509bd864cfcacca378604cf` | `papers/2025-12-GRC-V2.md` |
| `grc_v3` | `True` | `d26c29c70f8df2e4166451ccd9be6ee603cba6c1a023d251bf16de17e8bd3400` | `papers/2026-02-GRC-V3.md` |
| `grc_9` | `True` | `cefc33e91e496c236660dad5c1e009a720ca908488db460d47322118dd7c3e08` | `papers/2026-04-GRC-9.md` |
| `lgrc_9` | `True` | `4340a8b7b4be0d6b04127f4205630db59912e2a4a18ca326025517ece6a996cb` | `papers/2026-05-LGRC-9.md` |
| `lgrc9v3_causal_pulse_substrate_surfaces` | `True` | `82506f5b1fbf2aa7e60a2e67559be82bca4781e2becede75fb2f17c5a0a5c45e` | `papers/2026-05-LGRC9V3-Causal-Pulse-Substrate-Surfaces.md` |
| `n04_taxonomy_inventory` | `True` | `40dcf56c001f25909c92e3b39e570889e6f52f8b44b425533ba6e31eb942c72a` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_inventory_v1.json` |
| `n04_taxonomy_inventory_report` | `True` | `827336ad46f1d6319dd4a2ec538b9d6e23a19b2d0aa969e5b5a964e85eb5998b` | `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_taxonomy_inventory_v1.md` |
| `n04_taxonomy_closeout` | `True` | `36a96f188b2d0d32ee7d8840305bec34554b54de68f46c433f96271c2c53d780` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json` |
| `n04_iter19e_topology_mutating_movement` | `True` | `a293e7efa74e92369d6fd59f0c73f25669ee385b224e0f3fb32d06a5204e8910` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19e_topology_mutating_movement_after_state_reabsorption.json` |
| `n04_iter22_identity_boundary` | `True` | `3f30dfff12ab855ad0086b0f995de34a3dcb326445329fe0d45863ba9317648e` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22_identity_through_topology_mutation_boundary.json` |
| `n04_iter22_identity_boundary_report` | `True` | `f65c86783ed9fd741233c26689e79c89b3697dc0d116b39f71b5ec225cda6833` | `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter22_identity_through_topology_mutation_boundary.md` |
| `n04_iter22b_native_route_arbitrated_identity_boundary` | `True` | `65477fda0529097244fa7191df540721f8f148526619193007e639e7d4dc6714` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter22b_identity_through_native_route_arbitrated_topology.json` |
| `n04_iter22b_native_route_arbitrated_identity_boundary_report` | `True` | `43a405c11ea9fa9984b11748bff76489fad206ff5ae1d8899a2c409e62e66ef9` | `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_iter22b_identity_through_native_route_arbitrated_topology.md` |
| `n05_closeout` | `True` | `38c9b37186d1139a3ce7d3cf324e8f9a2b649099aa8bddd79c11eb346a86f1c8` | `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/outputs/n05_iteration_8_o6_closeout.json` |
| `n05_closeout_report` | `True` | `fa9d3b7f7d44ddc03e5a14537f4d06fb6540019c0d3251dd503b0182d1a425c2` | `experiments/2026-05-N05-lgrc-coherence-waves-oscillators/reports/n05_iteration_8_o6_closeout.md` |
| `n06_closeout` | `True` | `c020d954bdf5bfc53da9d550cd313f660af07f4b47e70b4c5102637500cc30bf` | `experiments/2026-05-N06-lgrc-semantic-route-choice/outputs/n06_iteration_8_sc6_closeout.json` |
| `n06_closeout_report` | `True` | `994a49ee0727a10b28f974bb08dbf6573ee0e3e104c861238b1c5f0594aece1f` | `experiments/2026-05-N06-lgrc-semantic-route-choice/reports/n06_iteration_8_sc6_closeout.md` |
| `phase8_causal_pulse_substrate_closeout` | `True` | `2c2b1171c31cc8ad4bcc4373d6a8a04f94865714707d7f9924066ce7e3feb2e2` | `implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.json` |
| `phase8_surface_lineage_closeout` | `True` | `97ad2e56ba6f2b2b303070dcbc4eb16ee54a5267c4911269abb664f35571709f` | `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json` |
| `phase8_topology_state_reabsorption_closeout` | `True` | `7db33f5c04b34e3046ebbfda523a245c1b8dd80457e6fdf3a158dae1a6ecac31` | `implementation/Phase-8-LGRC9-TopologyStateReabsorptionCloseout.json` |
| `phase8_time_scoped_lineage_replay_closeout` | `True` | `26a291a3fe17432b55e5da1fea22db950508c71ad4effe83346c09e6ee050201` | `implementation/Phase-8-LGRC9-TimeScopedLineageReplayCloseout.json` |
| `phase8_native_route_arbitration_closeout` | `True` | `cabc1f5b81fdb19154d778b04463f74f32e82653db6291daa62b1e5128d01b65` | `implementation/Phase-8-LGRC9-NativeRouteArbitrationCloseout.json` |
| `lgrc9v3_contract_source` | `True` | `0c50cffe638ff18ada4375f8e3acd897e054eb48d75137da735d6d5a4cdafe8a` | `src/pygrc/models/lgrc_9_v3_contract.py` |
| `lgrc9v3_runtime_source` | `True` | `70c065b003ebdd4351fad7b5089abc27557dee9a04b6e1c7834e1d01bd5fa6ee` | `src/pygrc/models/lgrc_9_v3_runtime.py` |
| `lgrc9v3_runtime_state_source` | `True` | `e939fc363898dfa8b7c64ced1ba6159dbd7320ad7c69fa0f695c90a2aac2312b` | `src/pygrc/models/lgrc_9_v3_runtime_state.py` |
| `lgrc9v3_topology_source` | `True` | `f3cf7e2281c4073531a5951a19f9ae9141a336f9f9b6398f76eda7e1493abde4` | `src/pygrc/models/lgrc_9_v3_topology.py` |
| `lgrc9v3_telemetry_source` | `True` | `4af287dad2ec42bec6a619d294238e8f9fb915821374207a694afc553e57d026` | `src/pygrc/telemetry/lgrc9v3_contract.py` |

## Acceptance

Iteration 1 passes because N07 has a source-backed theory/schema inventory, a
frozen ID-ladder row schema, frozen becoming/topology/carrier/control schemas,
explicit blocked claim flags, no identity probes, and no `src/*` changes
required.
