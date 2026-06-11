# N10 Iteration 1 Baseline And Source Inventory

Status: `passed`.

## Result

Iteration 1 built a source-backed inventory from existing N05-N09
artifacts only. No N10 integration probe was run.

The starting boundary is:

```text
A6 evidence = not yet produced
integration rows = none
primary first-tranche path = Hypothesis A
required controls = Hypothesis B support sensitivity
native-policy gaps = Hypothesis C tracked, not solved
bounded agentic-like integration claim allowed = false
```

## Inherited Sources

N05:

- strongest O-level: `O5`
- claim ceiling: `self_sustained_oscillator_candidate`
- O6 supported: `False`
- O6 blocker: `missing_route_conductance_memory_policy`
- N10 role: `oscillator_and_route_aspect_background_only`

N06:

- strongest SC-level: `SC6`
- claim ceiling: `artifact_only_semantic_route_choice_candidate`
- selection scope: `not_applicable_pre_topology_selection_only_scope`
- N10 role: `route_choice_source_only_not_agency`

N07:

- ID level: `ID6`
- derived ceiling: `ID6`
- trajectory regime: `bounded_non_destructive_exchange`
- support area digest: `c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb`
- runtime identity acceptance: `False`

N07 Iteration 13 withdrawal baseline:

- baseline available: `True`
- N10 can consume baseline: `True`
- prior N09 blocker: `n07_identity_withdrawal_baseline_not_available`
- support lanes:
  - `support_intact_reference`: tag=`support_intact_bounded_exchange_reference`, survived=`True`, withdrawal=`0.0`, restoration=`0.0`, support=`0.9731535762447039`
  - `mild_support_weakening`: tag=`support_withdrawal_survival_baseline`, survived=`True`, withdrawal=`0.1`, restoration=`0.0`, support=`0.8758382186202335`
  - `n09_matched_partial_support_withdrawal`: tag=`support_disrupted_by_withdrawal_without_restoration`, survived=`False`, withdrawal=`0.25`, restoration=`0.0`, support=`0.7298651821835279`
  - `restored_after_n09_partial_withdrawal`: tag=`explicit_restoration_recovers_support_survival_baseline`, survived=`True`, withdrawal=`0.25`, restoration=`0.8`, support=`0.9244958974324687`

N08:

- Hypothesis A:
  - claim ceiling: `artifact_only_route_memory_or_trail_affordance_candidate`
  - claim scope: `artifact_only_serialized_producer_policy_route_memory_or_trail`
  - N10 role: `memory_trail_affordance_source_scoped_to_artifact_only_serialized_policy`
- Hypothesis B:
  - claim ceiling: `static_positive_geometry_route_response_persistence_candidate`
  - primary blocker: `native_route_conductance_memory_policy_missing`
  - N10 role: `native_geometry_trail_design_direction_and_policy_gap`

N09:

- Hypothesis A:
  - GPR level: `GPR6`
  - claim ceiling: `artifact_only_goal_proxy_regulation_candidate`
  - prior N10 blocker before N07 I13: `n07_identity_withdrawal_baseline_not_available`
- Hypothesis B:
  - claim ceiling: `native_substrate_mediated_goal_proxy_regulation_design_candidate`
  - strongest evidence: `finite_envelope_band_buffered_return_scaffold_candidate`
  - primary blocker: `native_response_magnitude_policy_missing_for_unbounded_perturbations`
  - general native regulation supported: `False`

## Hypothesis Orientation

```json
{
  "hypothesis_b_role": "required_support_sensitivity_controls",
  "hypothesis_c_role": "tracked_native_policy_gap_not_solved_in_first_tranche",
  "iterations_1_to_9_primary_path": "hypothesis_a_bounded_artifact_only_integration"
}
```

## Native Policy Gaps

```json
[
  "native_agentic_like_integration_policy_missing",
  "native_identity_acceptance_validator_missing",
  "native_response_magnitude_policy_missing_for_unbounded_perturbations",
  "native_route_conductance_memory_policy_missing"
]
```

## Claim Boundary

All N10 claim flags are false at baseline:

```json
{
  "aco_like_claim_allowed": false,
  "agency_claim_allowed": false,
  "agentic_like_claim_allowed": false,
  "ant_colony_claim_allowed": false,
  "biological_claim_allowed": false,
  "goal_ownership_claim_allowed": false,
  "identity_acceptance_claim_allowed": false,
  "intention_claim_allowed": false,
  "locomotion_like_claim_allowed": false,
  "personhood_claim_allowed": false,
  "rc_identity_collapse_claim_allowed": false,
  "runtime_identity_acceptance_claim_allowed": false,
  "semantic_choice_claim_allowed": false,
  "semantic_goal_understanding_claim_allowed": false,
  "unrestricted_agency_claim_allowed": false,
  "unrestricted_identity_claim_allowed": false,
  "unrestricted_movement_claim_allowed": false
}
```

## Checks

```json
{
  "a6_not_supported_at_start": true,
  "claim_flags_all_false": true,
  "n05_source_present": true,
  "n06_source_present": true,
  "n07_i13_baseline_consumable": true,
  "n07_i13_has_disrupted_support_control": true,
  "n07_i13_has_explicit_restoration_lane": true,
  "n07_i13_has_four_support_lanes": true,
  "n07_i13_source_present": true,
  "n07_source_present": true,
  "n08_hypothesis_a_scope_artifact_only": true,
  "n08_hypothesis_a_source_present": true,
  "n08_hypothesis_b_source_present": true,
  "n09_hypothesis_a_goal_proxy_available": true,
  "n09_hypothesis_a_source_present": true,
  "n09_hypothesis_b_native_general_regulation_blocked": true,
  "n09_hypothesis_b_source_present": true,
  "native_policy_gaps_recorded": true,
  "no_integration_probe_run": true,
  "no_integration_rows_at_start": true,
  "src_clean_for_iteration_1": true
}
```

## Acceptance

Iteration 1 passes if N10 has a source-backed inventory of all prerequisite N05-N09 artifacts and records the exact evidence ceilings and blocked claims without promoting them into integration evidence.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/build_n10_iteration_1_baseline_inventory.py
```

Inventory digest:

```text
eda16e097598d336f5ea8897ea6390d4cbaef308315f70b24e17df81f11982e7
```
