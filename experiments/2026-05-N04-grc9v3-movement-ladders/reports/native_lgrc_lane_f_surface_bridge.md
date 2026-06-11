# N04 Lane F Native LGRC Surface Bridge

- claim_ceiling: `native_lgrc_pulse_substrate_surface_supported`
- native_lgrc_pulse_substrate_supported: `true`
- movement_claim_allowed: `false`
- native_m6: `false`

## Result

Lane F validates native LGRC causal pulse-substrate surface support as an artifact-validatable scheduling/evidence surface. Coupling and feedback producers schedule through LGRC queues only, feedback regeneration is sourced from feedback eligibility rather than copied from the original E3 schedule, controls pass, and movement/M6/agency/identity claims remain blocked.

## Controls

- `F_lgrc0_lgrc1_inertness_control`: passed=`true`, primary_blocker=`lgrc_runtime_level_below_2`
- `F_default_off_synchronous_noop_control`: passed=`true`, primary_blocker=`surface_policy_disabled`
- `F_producer_coherence_mutation_control`: passed=`true`, primary_blocker=`producer_mutation_boundary_violation`
- `F_budget_surface_merging_control`: passed=`true`, primary_blocker=`budget_surface_ambiguity`
- `F_snapshot_continue_after_load_with_producers_control`: passed=`true`, primary_blocker=`None`
- `F_coupling_disabled_control`: passed=`true`, primary_blocker=`coupling_disabled`
- `F_coupling_subthreshold_control`: passed=`true`, primary_blocker=`subthreshold`
- `F_feedback_disabled_control`: passed=`true`, primary_blocker=`feedback_disabled`
- `F_feedback_subthreshold_control`: passed=`true`, primary_blocker=`subthreshold`
- `F_feedback_wrong_polarity_control`: passed=`true`, primary_blocker=`wrong_polarity`
- `F_feedback_order_mismatch_control`: passed=`true`, primary_blocker=`canonical_causal_order_failed`
- `F_feedback_budget_violation_control`: passed=`true`, primary_blocker=`budget_surface_gate_failed`
- `F_disabled_surface_policy_producer_control`: passed=`true`, primary_blocker=`surface_policy_disabled`
- `F_topology_lineage_deferred_control`: passed=`true`, primary_blocker=`topology_lineage_deferred`
