# N15 Proxy Formation Schema And AP5 Gate

Status: `passed`.

## Summary

```json
{
  "ap5_required_gate_count": 36,
  "control_requirement_count": 12,
  "fail_closed_error_label_count": 10,
  "final_ap5_rows": 0,
  "materialized_config_file_count": 5,
  "row_schema_field_count": 55
}
```

## Acceptance State

```text
accepted_schema_freeze_no_row_validation
```

Iteration 2 freezes the N15 row schema, AP5 gate, derivation policy,
old-best-claims composition operator, drift policy, budget units,
dependency trace format, replay digest scope, perturbation defaults,
control requirements, config-file contracts, output shape, and
fail-closed error labels. Post-review gap closure materializes
the planned config files, splits runtime output fields from I2
schema-freeze metadata fields, and links the local validator.
It does not validate rows beyond the Iteration 1 inventory,
generate a target, run controls, or assign final `AP5`.

## Top-Level Contracts

Runtime row outputs must include these fields:

```json
[
  "experiment",
  "iteration",
  "artifact_id",
  "purpose",
  "schema_version",
  "generated_at",
  "command",
  "status",
  "acceptance_state",
  "source_artifacts",
  "source_reports",
  "rows",
  "controls",
  "checks",
  "claim_flags",
  "errors",
  "output_digest"
]
```

The Iteration 2 schema-freeze artifact includes these fields:

```json
[
  "experiment",
  "iteration",
  "artifact_id",
  "purpose",
  "schema_version",
  "generated_at",
  "command",
  "status",
  "acceptance_state",
  "target_ap_ceiling",
  "iteration_result",
  "schema_summary",
  "ap_ladder",
  "row_schema_fields",
  "top_level_output_fields",
  "top_level_schema_freeze_fields",
  "ap5_required_gates",
  "endogenous_derivation_policy",
  "old_best_claims_composition",
  "bounded_drift_policy",
  "budget_limits",
  "dependency_trace_format",
  "replay_digest_policy",
  "perturbation_policy",
  "hypothesis_decision_rubric",
  "control_requirements",
  "config_file_contracts",
  "schema_validation_contract",
  "fail_closed_error_labels",
  "rows",
  "controls",
  "claim_flags",
  "checks",
  "source_artifacts",
  "source_reports",
  "errors",
  "git",
  "output_digest"
]
```

## AP5 Gate

| Gate |
| --- |
| `runtime_visible_source_state_inventory_present` |
| `source_artifact_report_digest_for_each_state_input` |
| `source_current_freshness_record_present` |
| `support_state_descriptor_present` |
| `memory_state_descriptor_or_explicit_absence_present` |
| `regulation_state_descriptor_or_explicit_absence_present` |
| `support_identity_condition_descriptor_or_explicit_absence_present` |
| `declared_external_proxy_absent` |
| `externally_injected_target_rejection_policy_present` |
| `hidden_target_derivation_rejection_policy_present` |
| `hidden_target_derivation_control_fails_closed` |
| `endogenous_derivation_policy_present` |
| `target_condition_generated_before_downstream_use` |
| `target_condition_surface_present` |
| `target_center_present` |
| `target_band_or_threshold_present` |
| `target_tolerance_present` |
| `bounded_drift_policy_present` |
| `drift_clamp_policy_present` |
| `budget_cost_surface_present` |
| `budget_units_present` |
| `budget_validity_policy_present` |
| `dependency_trace_from_source_state_to_target_condition_present` |
| `idempotency_digest_plan_present` |
| `generated_target_consumable_by_rank_or_regulation_without_goal_ownership_relabel` |
| `artifact_only_replay_requirement_present` |
| `snapshot_load_equivalence_requirement_present` |
| `order_inversion_replay_requirement_present` |
| `post_hoc_proxy_formation_rejection_policy_present` |
| `negative_controls_present` |
| `compatibility_checks_present` |
| `claim_flags_forced_false` |
| `src_diff_empty_true` |
| `native_supported_flags_false` |
| `phase8_opened_false` |
| `fully_native_integration_opened_false` |

## Frozen Derivation Policy

```json
{
  "budget_rule": "use budget_limits_v1 before any downstream target use",
  "clamp_rule": "clamp out-of-bound updates and mark drift_clamped = true",
  "composition_rule": "weighted sum over normalized support, regulation, memory, and AP4 consequence context; N12 readiness contributes only validation context and never changes the target value",
  "composition_weights": {
    "ap4_consequence_context_score": 0.15,
    "memory_context_score": 0.2,
    "readiness_context_flag": 0.0,
    "regulation_recovery_score": 0.25,
    "support_margin": 0.4
  },
  "digest_scope": "use replay_digest_policy_v1",
  "drift_bound_rule": "use bounded_drift_policy_v1",
  "input_fields": [
    "support_margin",
    "regulation_recovery_score",
    "memory_context_score",
    "ap4_consequence_context_score",
    "readiness_context_flag"
  ],
  "input_normalization": {
    "missing_input_policy": "fail_closed",
    "numeric_support_fields": "normalize to [-1.0, 1.0] around the frozen support threshold",
    "ordinal_fields": "map by the frozen ordinal codebook",
    "stale_input_policy": "fail_closed"
  },
  "ordinal_codebook": {
    "absent": 0.0,
    "blocked": -1.0,
    "present": 0.5,
    "supported": 1.0
  },
  "policy_id": "n15_endogenous_proxy_derivation_policy_v1",
  "policy_kind": "trace_preserving_old_best_claims_construction",
  "policy_version": "1.0",
  "target_band_rule": "numeric target_band = [target_center - target_tolerance, target_center + target_tolerance]; ordinal target_band uses the codebook category plus one adjacent category only when the drift policy allows it",
  "target_center_rule": "target_center = clamp(support_threshold + 0.10 * weighted_sum, support_threshold - 0.10, support_threshold + 0.10)",
  "target_tolerance_rule": "target_tolerance = clamp(0.05 + 0.02 * max(regulation_recovery_score, 0), 0.03, 0.08)"
}
```

## Budget And Drift

```json
{
  "bounded_drift_policy": {
    "clamp_status_field": "drift_clamped",
    "numeric_scale": "0_to_1_source_scale",
    "numeric_target_center_max_update": 0.1,
    "numeric_target_tolerance_max_update": 0.05,
    "ordinal_max_update": "one_adjacent_category_per_derivation_step",
    "policy_id": "n15_bounded_drift_policy_v1",
    "unconfigured_or_unbounded_drift": "fail_closed"
  },
  "budget_limits": {
    "limits": {
      "canonical_json_input_bytes": 262144,
      "canonical_json_output_bytes": 262144,
      "replay_count": 6,
      "source_row_count": 12,
      "transform_count": 24,
      "validation_count": 64,
      "wall_clock_seconds": 60
    },
    "policy_id": "n15_budget_limits_v1",
    "units": [
      "source_row_count",
      "transform_count",
      "canonical_json_input_bytes",
      "canonical_json_output_bytes",
      "replay_count",
      "validation_count",
      "wall_clock_seconds"
    ],
    "validity_rule": "budget is checked before target use; missing or exceeded limits fail closed"
  }
}
```

## Controls

| Control | Expected status | Blocker |
| --- | --- | --- |
| `externally_injected_target_control` | `blocked` | `externally_injected_target_blocked` |
| `hidden_target_derivation_control` | `blocked` | `hidden_target_derivation_blocked` |
| `semantic_goal_ownership_relabel_control` | `blocked` | `semantic_goal_ownership_relabel_blocked` |
| `post_hoc_proxy_formation_control` | `blocked` | `post_hoc_proxy_formation_blocked` |
| `unbounded_target_drift_control` | `blocked` | `unbounded_target_drift_blocked` |
| `budget_surface_ambiguity_control` | `blocked` | `budget_surface_ambiguity_blocked` |
| `identity_acceptance_relabel_control` | `blocked` | `identity_acceptance_relabel_blocked` |
| `native_support_relabel_control` | `blocked` | `native_support_relabel_blocked` |
| `fixture_label_proxy_control` | `blocked` | `fixture_label_proxy_blocked` |
| `stale_source_state_control` | `blocked` | `stale_source_state_blocked` |
| `missing_source_state_control` | `blocked` | `missing_source_state_blocked` |
| `dependency_trace_omission_control` | `blocked` | `dependency_trace_omission_blocked` |

## Materialized Config Files

| Config | SHA-256 |
| --- | --- |
| `configs/n15_source_registry.json` | `361457bb559a4e4255824ee72415ae9c77b661e1ec95f657ea3d65bff4a36e71` |
| `configs/n15_derivation_policy_v1.json` | `9de32ee9717fd813e2a20ded18cde3cc384307c92586212a07f7105d72041c7b` |
| `configs/n15_budget_limits_v1.json` | `8b1314a9d229d70cd48e12bfc5fa4aa978877f78a4880db9e8a3faa867fbe62e` |
| `configs/n15_control_variants_v1.json` | `bf4a17c7168c74a21e85c6893ce174b4d76fb159340710e261c16b5ef45984e9` |
| `configs/n15_replay_policy_v1.json` | `356589601130ec5a9edacf3c900b57758768cc6fa73b9e1e09880a2fbab7c7f3` |

## Schema Validator

```json
{
  "required_checks": [
    "required_fields_present",
    "claim_flags_forced_false",
    "control_outcomes_present",
    "source_digest_presence",
    "digest_reproducibility",
    "absolute_path_absence"
  ],
  "validator_kind": "project_local_python_validator",
  "validator_script": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/scripts/validate_n15_row.py"
}
```

## Checks

```json
{
  "ap5_gate_contains_fully_native_flag": true,
  "ap5_gate_contains_hidden_target_control": true,
  "ap5_gate_contains_target_consumability": true,
  "budget_units_and_limits_frozen": true,
  "claim_flags_forced_false": true,
  "config_file_contracts_materialized": true,
  "control_requirements_count": true,
  "dependency_trace_format_frozen": true,
  "derivation_policy_frozen": true,
  "drift_bounds_frozen": true,
  "fail_closed_error_labels_frozen": true,
  "fully_native_integration_not_opened": true,
  "hypothesis_decision_rubric_frozen": true,
  "inventory_acceptance_state_valid": true,
  "inventory_source_passed": true,
  "native_support_not_opened": true,
  "no_absolute_paths_recorded": true,
  "no_final_ap5_assigned": true,
  "old_best_composition_frozen": true,
  "perturbation_policy_frozen": true,
  "phase8_opened_false": true,
  "replay_digest_policy_frozen": true,
  "row_schema_covers_inventory_rows": true,
  "row_schema_has_budget_units": true,
  "row_schema_has_idempotency_digest_plan": true,
  "schema_validator_script_present": true,
  "src_diff_empty": true,
  "target_band_contract_frozen": true,
  "top_level_runtime_output_shape_frozen": true,
  "top_level_schema_freeze_shape_declared": true,
  "top_level_schema_freeze_shape_matches_output": true
}
```

## Claim Boundary

```text
schema freeze != AP5 support
derivation policy != generated target
old-best-claims composition contract != semantic goal ownership
N13 AP3 input != selfhood
N14 AP4 input != intention or goal ownership
N12 readiness-only context != native support
N15 Iteration 2 != fully native integration
```

## Output Digest

```text
3894554145fe84a7f594983ead562442cda686fd53d6b240164626b578f2ee67
```
