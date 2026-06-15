# N12 Iteration 4 Response Magnitude Candidate

## Status

Status: `passed`.

```text
primary_disposition = native_absorption_candidate
nat_level = NAT4
phase8_ready = true
phase8_opened = false
native_support_opened = false
row.native_support_opened = false
row.phase8_opened = false
```

Iteration 4 classifies response magnitude as a bounded/envelope-gated
`NAT4` Phase 8-ready response magnitude policy candidate. This is a
readiness classification only. It opens no native support claim for
regulation, no semantic goal ownership, no intention, no agency, and no
Phase 8 implementation.

The JSON artifact is the source of truth for the full candidate record,
source artifacts, digests, policy schema sketch, controls, and gate audit.

## Source Decision

N09 Hypothesis A remains artifact-only goal-proxy regulation. The native
bounded/envelope-gated candidate is limited to serialized proxy error,
response magnitude, bounded window, packet scheduling, and
budget-accounted correction policy. N09 B-branch native substrate claims
remain blocked.

```text
N09 Hypothesis A scope = artifact_only_serialized_producer_policy_goal_proxy_regulation
N09 GPR6 claim ceiling = artifact_only_goal_proxy_regulation_candidate
N09 B blocker = native_goal_proxy_regulation_policy_missing
native_substrate_mediated_goal_proxy_regulation_claim_allowed = false
```

## Producer Vs Native Split

| Layer | Status | Boundary |
| --- | --- | --- |
| Producer-side goal-proxy regulation pattern | experiment_local_scaffold_only | Serialized proxy, target band, and producer response remain artifact-only. |
| Bounded/envelope-gated response magnitude policy candidate | phase8_ready_candidate_not_implemented | Only step/packet events may mutate proxy-affecting state. |
| Native goal semantics | blocked_not_part_of_candidate | Goal ownership, intention, and semantic understanding remain blocked. |

## NAT4 Gate Audit

| Gate | Present | Validated | Source |
| --- | --- | --- | --- |
| `native_policy_name` | `true` | `true` | N09 closeout, N10 contract, N11 gap, N12 candidate row |
| `record_schema_sketch` | `true` | `true` | N12 Iteration 4 record schema sketch |
| `default_off_flags` | `true` | `true` | N12 Iteration 4 default-off policy flags |
| `enabled_validated_supported_separation` | `true` | `true` | N12 Iteration 4 claim boundary fields |
| `idempotency_digest_plan` | `true` | `true` | N12 Iteration 4 digest plan |
| `runtime_visible_inputs` | `true` | `true` | N10 contract plus N12 trend/budget extensions |
| `budget_surfaces` | `true` | `true` | N10 contract plus N12 typed budget semantics |
| `telemetry_requirements` | `true` | `true` | N12 telemetry namespace and export behavior |
| `snapshot_replay_requirements` | `true` | `true` | N10 replay requirements plus N12 replay extensions |
| `negative_controls` | `true` | `true` | N09 controls, N10 contract controls, N12 claim controls |
| `compatibility_tests` | `true` | `true` | N12 Iteration 4 compatibility test list |
| `claim_flags_forced_false` | `true` | `true` | N12 Iteration 2 claim flags |
| `non_rc_quantity_audit` | `true` | `true` | N12 Iteration 4 non-RC audit |
| `mutation_boundary` | `true` | `true` | N12 Iteration 4 mutation boundary |
| `producer_or_policy_may_schedule_only` | `true` | `true` | N12 Iteration 4 mutation boundary |
| `step_or_topology_event_owns_state_mutation` | `true` | `true` | N12 Iteration 4 mutation boundary |
| `src_diff_empty` | `true` | `true` | git status --short src |
| `native_supported_flags_false` | `true` | `true` | N12 Iteration 4 no-native-support flags |
| `phase8_opened_false` | `true` | `true` | N12 Iteration 4 no-implementation flags |

## Trend And Stability

```json
{
  "bounded_window": {
    "perturbation_amplitude": 0.09,
    "perturbation_expected_recovery_window_count": 1,
    "same_regulation_policy_all_windows": true,
    "same_target_band_all_windows": true,
    "window_count": 4,
    "window_input_amount": 0.07
  },
  "error_trend": {
    "memory_lane_outcome": "bounded_repeated_regulation",
    "memory_lane_post_correction_errors": [
      0.0,
      0.0,
      0.0,
      0.0
    ],
    "no_memory_lane_errors_after_inputs": [
      0.07,
      0.14,
      0.21,
      0.28
    ],
    "no_memory_lane_outcome": "policy_saturation",
    "perturbation_recovery_in_band": true,
    "single_cycle_error_after": 0.0,
    "single_cycle_error_before": 0.07,
    "source": "N09 GPR4/GPR5/GPR8",
    "status": "bounded_improving_or_blocked_by_envelope"
  },
  "out_of_envelope_blocker": {
    "blocker": "unbounded_perturbation_envelope_blocked",
    "related_controls": [
      "unbounded_perturbation_without_policy_rejected",
      "general_native_regulation_overclaim_blocked",
      "adaptive_response_amount_hidden_policy_blocked"
    ],
    "status": "required_for_phase8_entry"
  },
  "overcorrection_status": {
    "fixed_return_amount_family_control_passed": true,
    "single_cycle_post_response_in_band": true,
    "status": "blocked_by_target_band_and_wrong_direction_controls",
    "wrong_direction_control_passed": true
  },
  "saturation_status": {
    "bounded_candidate_status": "not_saturated_within_declared_memory_lane_window",
    "no_memory_comparator_status": "policy_saturation",
    "out_of_envelope_status": "blocked_without_perturbation_envelope_policy"
  }
}
```

## Record Schema Sketch

```json
{
  "forbidden_fields": [
    "hidden_goal_state",
    "semantic_goal_ownership",
    "agent_intention",
    "hidden_optimizer_state",
    "unbounded_response_gain",
    "report_side_response_override"
  ],
  "record_type": "native_response_magnitude_policy_record",
  "required_fields": [
    "policy_id",
    "enabled",
    "validated",
    "supported",
    "proxy_surface_digest",
    "target_band_policy_id",
    "target_band_digest",
    "proxy_error_digest",
    "eligibility_record_digest",
    "perturbation_envelope_digest",
    "response_gain_policy_id",
    "max_correction_per_window",
    "bounded_window_id",
    "response_packet_schedule_digest",
    "node_plus_packet_budget_before_digest",
    "node_plus_packet_budget_after_digest",
    "proxy_budget_before_digest",
    "proxy_budget_after_digest",
    "error_trend_digest",
    "saturation_status",
    "overcorrection_status",
    "policy_record_digest"
  ],
  "state_carrier": "proxy_error_and_packet_scheduling_policy",
  "version": "v1"
}
```

## Budget Semantics

```json
{
  "goal_proxy_budget_surface": {
    "phase8_rule": "proxy measurement remains derived observable, not new hidden state",
    "role": "tracks proxy measurement and target-band error from runtime-visible state",
    "surface_type": "derived_proxy_observable_surface"
  },
  "node_plus_packet_budget_surface_separate": {
    "phase8_rule": "response correction must conserve node-plus-packet budget",
    "role": "ensures correction is expressed as scheduled packet work and step-owned mutation",
    "surface_type": "existing_conservation_surface"
  },
  "response_magnitude_budget_surface": {
    "phase8_rule": "response size must be replayable from policy, error, envelope, and budget digests",
    "role": "accounts response gain, max correction per window, and envelope limits",
    "surface_type": "serialized_policy_sizing_surface",
    "unit_boundary": "response packet amount and error reduction, not semantic goal value"
  }
}
```

## Telemetry Requirements

```json
{
  "telemetry_export_behavior": {
    "backward_compatible_when_disabled": true,
    "default_off": true,
    "legacy_exports_unchanged_until_enabled": true,
    "native_support_flags_exported_false": true,
    "new_records_require_explicit_flag": true
  },
  "telemetry_namespaces": {
    "backward_compatibility_rule": "existing telemetry exports remain byte-compatible when the native response magnitude policy is disabled",
    "candidate_records": [
      "ResponseMagnitudePolicyRecord",
      "ResponseMagnitudeBudgetRecord",
      "ResponseMagnitudeControlRecord"
    ],
    "default_off_namespace_rule": "new native telemetry is disabled unless the Phase 8 policy flag is explicitly enabled",
    "primary_native_namespace": "src/pygrc/telemetry"
  },
  "telemetry_requirements": [
    "response_magnitude_policy_record_emitted_default_off",
    "proxy_surface_digest_and_target_band_digest",
    "proxy_error_digest_and_error_trend_digest",
    "eligibility_record_digest",
    "response_gain_policy_id_and_max_correction_per_window",
    "perturbation_envelope_digest",
    "response_packet_schedule_digest",
    "node_plus_packet_budget_before_after_digests",
    "proxy_budget_before_after_digests",
    "negative_control_blocker_id",
    "claim_flags_forced_false_snapshot"
  ]
}
```

## Compatibility Tests

```json
[
  "policy_disabled_records_no_response_mutation",
  "proxy_measurement_is_derived_observable",
  "target_band_digest_precedes_error_digest",
  "response_gain_serialized_and_replayable",
  "max_correction_per_window_enforced",
  "wrong_direction_response_rejected",
  "hidden_optimizer_state_rejected",
  "out_of_envelope_perturbation_blocked",
  "node_plus_packet_budget_conserved",
  "artifact_replay_recomputes_policy_record_digest",
  "telemetry_default_off_exports_no_new_records",
  "existing_telemetry_exports_backward_compatible_when_disabled",
  "claim_flags_remain_false"
]
```

## Non-RC Quantity Audit

```json
{
  "audit_status": "passed_for_nat4_readiness",
  "blocked_if_extra_quantity_required": "unaccounted_non_rc_quantity_required",
  "does_correction_debit_node_plus_packet_budget": true,
  "does_response_sizing_require_hidden_optimization_or_external_controller_state": false,
  "extra_unaccounted_quantity_allowed": false,
  "forbidden_non_rc_quantities": [
    "hidden_goal_state",
    "semantic_goal_ownership",
    "agent_intention",
    "hidden_optimizer_state",
    "unbounded_response_gain"
  ],
  "is_expressible_as_rc_causality_coherence_scheduling_lineage_budget": true,
  "is_proxy_measurement_derived_observable_or_new_state": "derived_observable_from_runtime_visible_active_node_state",
  "is_response_gain_serialized_and_replayable": true,
  "is_target_band_exogenous_or_runtime_visible_policy": "runtime_visible_serialized_policy_record_not_semantic_goal"
}
```

## Schema Alignment And Candidate Extensions

```json
{
  "all_extra_fields_documented": true,
  "candidate_row_fields_count": 68,
  "candidate_specific_extension_fields": {
    "budget_semantics": "Iteration 4 typed budget semantics for proxy and response sizing.",
    "native_support_opened": "Row-level no-native-support flag.",
    "phase8_opened": "Row-level no-Phase-8-implementation flag.",
    "proxy_measurement_surface": "Iteration 4 proxy measurement surface details.",
    "response_magnitude_policy": "Iteration 4 response gain and correction window details.",
    "response_packet_scheduling_boundary": "Iteration 4 scheduling/mutation boundary.",
    "response_policy_split": "Iteration 4 producer-vs-native response policy split.",
    "source_evidence_summary": "Iteration 4 compact source-backed evidence summary.",
    "target_band_policy": "Iteration 4 target band policy details.",
    "telemetry_export_behavior": "Iteration 4 default-off/backward-compatible telemetry export behavior.",
    "telemetry_namespaces": "Iteration 4 telemetry namespace declaration, including src/pygrc/telemetry.",
    "trend_stability_fields": "Iteration 4 error trend, saturation, overcorrection, bounded window, and envelope blocker."
  },
  "extension_policy": "Iteration 4 may add candidate-specific extension fields when they are explicitly documented and do not promote native support or Phase 8 implementation.",
  "extra_row_fields": [
    "budget_semantics",
    "native_support_opened",
    "phase8_opened",
    "proxy_measurement_surface",
    "response_magnitude_policy",
    "response_packet_scheduling_boundary",
    "response_policy_split",
    "source_evidence_summary",
    "target_band_policy",
    "telemetry_export_behavior",
    "telemetry_namespaces",
    "trend_stability_fields"
  ],
  "iteration_2_final_row_fields_count": 56,
  "missing_final_row_fields": []
}
```

## Source Digest Policy

```json
{
  "all_source_file_sha256_present": true,
  "controlling_provenance_pin": "source_artifacts[*].sha256",
  "file_sha256_is_required_for_every_source": true,
  "null_digest_reason": "Upstream N09/N10/N11 artifacts use mixed output_digest and artifact_digest conventions. N12 pins every source by file SHA-256 and records upstream digest fields opportunistically.",
  "upstream_output_digest_or_artifact_digest_may_be_null": true
}
```

## Artifact Reproducibility

```json
{
  "file_sha_reproducible_for_fixed_sources_and_git_head": true,
  "generated_at": "2026-06-15T00:00:00+00:00",
  "generated_at_policy": "fixed experiment timestamp for reproducible file SHA across reruns with unchanged source files and git HEAD",
  "output_digest_excludes": [
    "generated_at",
    "output_digest",
    "git"
  ],
  "wall_clock_timestamp_in_file": false
}
```

## Checks

```json
{
  "all_nat4_gates_present": true,
  "all_nat4_gates_validated": true,
  "budget_semantics_typed": true,
  "claim_flags_forced_false": true,
  "generated_at_reproducible": true,
  "iteration_1_response_row_present": true,
  "iteration_2_nat4_gates_loaded": true,
  "mutation_boundary_recorded": true,
  "n09_bounded_native_overclaim_blocked": true,
  "n09_gpr4_single_cycle_band_return": true,
  "n09_gpr5_bounded_repeated_regulation": true,
  "n09_gpr6_artifact_only_scope": true,
  "n09_gpr8_perturbation_recovered": true,
  "n09_native_substrate_claim_blocked": true,
  "n09_proxy_measurement_runtime_visible": true,
  "n10_contract_present": true,
  "n11_gap_present": true,
  "no_hidden_optimizer_state": true,
  "no_native_support_claim": true,
  "non_rc_quantity_audit_passed": true,
  "phase8_ready_derived_from_nat4": true,
  "row_level_native_support_opened_false": true,
  "row_level_phase8_opened_false": true,
  "schema_extension_fields_documented": true,
  "source_file_sha256_all_present": true,
  "src_clean": true,
  "telemetry_default_off_backward_compatible": true,
  "telemetry_namespace_explicit": true,
  "trend_stability_fields_recorded": true
}
```

## Claim Boundary

```text
native absorption candidate != native support
native support != agency
response magnitude policy != goal ownership
response magnitude policy != intention
goal-proxy regulation != semantic goal understanding
bounded response != unbounded native regulation
phase8_ready != Phase 8 implementation
```

## Output Digest

```text
347a66e30fb532899664a475f6240239de70229573dc09f5947a2033e45614b4
```
