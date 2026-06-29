# N27 Iteration 2 - Transfer Schema And Controls

Status: `passed`

Acceptance state: `accepted_transfer_schema_and_controls_frozen_no_positive_evidence`

## Scope

Iteration 2 freezes N27 schema and controls only. It opens no positive transfer
evidence, assigns no CT rung, and does not classify a transfer candidate.

## Source Precedence

```text
normative_contract_row = n20_i5_row_08_configuration_substrate_transfer
descriptor_context_row = n20_i4_row_08_configuration_substrate_transfer
n20_i5_consumable_contract_is_normative = true
n20_i4_descriptor_is_context_only = true
```

Deferred I4 descriptor fields cannot weaken transfer gates.

## Digest Pins

```text
source_inventory_output_digest = 5ff3409dd63b9b52cf3e10e91797653c319af0564dbcc344dd9e9fc2c3cbb222
descriptor_contract_row_digest = c8be68905ad18176f6087210ad24cf2cc432d1b04e61e9db8edc54f86b46987f
consumable_contract_row_digest = 14d661d69af9aa62731834570a8db02e0050d8464c9a6b9608dcce2e472bb00c
n26_closeout_output_digest = bfb2f02a2c302da27215a87f5a42666ff11f5af5bbaed49ecc6204098afafe31
```

## Frozen Ladders

| Ladder | Rungs |
| --- | --- |
| `CT` | `CT0, CT1, CT2, CT3, CT4, CT5, CT6` |
| `N27-C` | `N27-C0, N27-C1, N27-C2, N27-C3, N27-C4, N27-C5, N27-C6` |

## Transfer Core

Every positive row must record:

```text
transfer_scope
transfer_mapping_id
transfer_mapping_digest
mapping_declared_before_use
mapping_source_backed
pre_signature_digest
post_signature_digest
boundary_mapping_digest
support_preservation_digest
coherence_preservation_digest
flux_balance_digest
```

Canonicalization:

```text
canonical_form = json_sort_keys_no_runtime_timestamp
digest_field = transfer_core_digest
positive_rows_reference_core_by_digest = true
```

The transfer core fails closed for same-label-only, movement-only,
visual-similarity-only, proxy-score-only, hidden support reconstruction, or
support reconstruction counted as transfer.

## Scope Rules

Allowed scopes:

```text
configuration
fixture
topology
substrate
```

Substrate transfer requires:

```text
declared_source_backed_substrate_mapping
mapping_source_artifact_digest
boundary_side_assignment_mapping
support_coherence_interpretation_mapping
```

## Rung-Specific Artifact Roles

| CT rung | Required roles |
| --- | --- |
| `CT1` | `transfer_mapping_trace, pre_transfer_basin_signature_trace, threshold_record` |
| `CT2` | `transfer_mapping_trace, pre_transfer_basin_signature_trace, threshold_record, post_transfer_basin_signature_trace, boundary_mapping_trace, support_preservation_trace, coherence_preservation_trace, flux_balance_trace` |
| `CT3` | `transfer_mapping_trace, pre_transfer_basin_signature_trace, threshold_record, post_transfer_basin_signature_trace, boundary_mapping_trace, support_preservation_trace, coherence_preservation_trace, flux_balance_trace, replay_trace` |
| `CT4` | `transfer_mapping_trace, pre_transfer_basin_signature_trace, threshold_record, post_transfer_basin_signature_trace, boundary_mapping_trace, support_preservation_trace, coherence_preservation_trace, flux_balance_trace, replay_trace, control_trace` |
| `CT5` | `transfer_mapping_trace, pre_transfer_basin_signature_trace, threshold_record, post_transfer_basin_signature_trace, boundary_mapping_trace, support_preservation_trace, coherence_preservation_trace, flux_balance_trace, replay_trace, control_trace, stress_variant_trace` |
| `CT6` | `transfer_mapping_trace, pre_transfer_basin_signature_trace, threshold_record, post_transfer_basin_signature_trace, boundary_mapping_trace, support_preservation_trace, coherence_preservation_trace, flux_balance_trace, replay_trace, control_trace, stress_variant_trace, closeout, N28_handoff_record` |


## Support Preservation Vs Reconstruction

```text
hidden_support_reconstruction_allowed = false
reconstructed_support_must_not_be_counted_as = support_preservation_trace
support_preservation_required_for_ct2_or_stronger = true
```

## Threshold And Formula Records

Required formula fields:

```text
signature_preservation_margin_formula
boundary_mapping_tolerance_formula
support_floor_margin_formula
coherence_floor_margin_formula
flux_balance_bound_formula
```

Required threshold fields:

```text
threshold_record_digest
row_specific_thresholds_declared_before_use
```

## Replay And AP Gates

Required CT3 replay modes:

```text
artifact_replay
snapshot_load_replay
duplicate_replay
mapping_order_replay
```

AP dependency statuses:

```text
ap4 = required_recorded | missing_blocks_row | not_applicable
ap5 = required_recorded | missing_blocks_row | not_applicable
not_applicable_requires_reason = true
```

## Controls

Required control count: `22`

```text
same_label_different_basin_control
fixture_equivalence_label_only_control
mapping_declared_after_outcome_control
proxy_score_relabel_as_transfer_control
hidden_support_reconstruction_control
support_reconstruction_as_transfer_control
boundary_mapping_missing_control
post_transfer_signature_missing_control
source_current_inputs_missing_control
cross_substrate_mapping_missing_control
artifact_manifest_failure_control
replay_failure_control
stress_variant_failure_control
AP4_dependency_omitted_control
AP5_dependency_omitted_control
n26_proxy_as_transfer_evidence_control
n26_scoped_ap5_as_native_ap5_control
n25_2_direct_transfer_consumption_control
semantic_identity_relabel_control
semantic_choice_goal_relabel_control
native_support_relabel_control
phase8_ant_ecology_relabel_control
```

Positive-row control audit fields include:

```text
control_satisfied_for_positive_row
control_applicability_reason
```

## Claim Boundary

```text
positive_transfer_evidence_opened = false
ct_ladder_rung_assigned = false
n27_closeout_ceiling = N27-C2_transfer_schema_and_controls_frozen
n26_consumed_as_transfer_evidence_allowed = false
n25_2_direct_transfer_consumption_used_required_value = false
```

Blocked claims:

```text
semantic identity
semantic choice
semantic goal ownership
semantic learning
agency
native support
selfhood
identity acceptance
sentience
organism/life
ant ecology implementation
Phase 8 completion
unscoped multi-basin substrate
native AP5
AP5 NAT4 gap resolution
```

## Checks

| Check | Passed |
| --- | --- |
| `i1_source_inventory_passed` | `true` |
| `source_inventory_digest_pinned` | `true` |
| `n20_i5_normative_i4_context_only` | `true` |
| `ct_ladder_frozen` | `true` |
| `n27_closeout_ladder_frozen` | `true` |
| `candidate_row_required_fields_present` | `true` |
| `transfer_core_schema_frozen` | `true` |
| `transfer_scope_schema_frozen` | `true` |
| `substrate_scope_requires_source_backed_mapping` | `true` |
| `rung_specific_artifact_roles_frozen` | `true` |
| `source_current_mapping_telemetry_required` | `true` |
| `transfer_core_canonicalization_frozen` | `true` |
| `threshold_formula_schema_frozen` | `true` |
| `support_preservation_reconstruction_split_frozen` | `true` |
| `replay_requirements_frozen` | `true` |
| `ap4_ap5_dependency_statuses_frozen` | `true` |
| `ap_not_applicable_requires_reason` | `true` |
| `control_families_frozen` | `true` |
| `orthogonal_control_roles_recorded` | `true` |
| `positive_row_control_audit_fields_frozen` | `true` |
| `no_direct_n25_2_consumption_invariant_frozen` | `true` |
| `n26_context_not_transfer_or_native_ap5` | `true` |
| `no_positive_transfer_evidence_opened` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |


## Interpretation

I2 makes N27 fail closed before positive probes. A later row cannot pass by
movement, same-label continuity, proxy preservation, N26 proxy/AP5 relabeling,
direct N25.2 backfill, hidden support reconstruction, support reconstruction
as preservation, or AP4/AP5 prose-only handling.

Output digest: `15515b88b7b6853f9cb47f9fd22f4291a78d7037da586d795110dea91c55ab22`
