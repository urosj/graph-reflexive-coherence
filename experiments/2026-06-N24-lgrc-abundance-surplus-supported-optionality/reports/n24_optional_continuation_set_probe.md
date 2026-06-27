# N24 Iteration 5 - Optional Continuation Set Probe

Status: `passed`

Acceptance state: `accepted_source_current_ab3_optional_continuation_candidate_pending_replay_controls_no_ab4`

Output digest: `77a9c3027bb8913a6443379cde883d29157026a8fba21aee8aac1795741e75cb`

## Summary

Iteration 5 opens the first source-current optional continuation set.
The result is capped at provisional AB3 pending I6 replay/control
validation and later stress/threshold work.

## Geometric Interpretation

The optionality is geometric rather than semantic: the branch records are LGRC center-to-neighbor edge continuations in the same runtime snapshot, with branch-specific support/coherence and boundary/flux traces.

I5 supports availability, not stress-backed joint admissibility. jointly_admissible_optional_continuation_count remains 0 until stress/threshold validation.

surplus_persistence_ratio and optional_branch_persistence_ratio are single-window descriptive placeholders, not replay-backed persistence evidence.

surplus_without_optional_continuation_rejected_or_demoted=true means the surplus-without-optionality control is satisfied because the bad condition is absent in I5; the field name is inherited from the frozen row schema.

The source snapshot intentionally matches the N23 I4 pre-collapse fixture hash,
because both probes start from the same LGRC fixture state. N24 re-emits
that state as its own runtime artifact and does not consume the N23 snapshot
as optionality evidence.

```text
maintenance_basin_id = n24_i4_core_support_maintenance_basin
maintenance_node_ids = [0, 1, 5, 6, 7, 8, 9]
optional_branch_target_node_ids = [1, 5, 9]
support_floor = 9.850000000000
coherence_floor = 9.850000000000
observed_min_support = 10.000000000000
observed_min_coherence = 10.000000000000
support_surplus_margin = 0.150000000000
coherence_surplus_margin = 0.150000000000
optional_continuation_availability_count = 3
jointly_admissible_optional_continuation_count = 0
residual_support_margin_under_optionality = 0.150000000000
residual_coherence_margin_under_optionality = 0.150000000000
```

## Candidate Row

| Field | Value |
| --- | --- |
| Row | `n24_i5_row_01_source_current_optional_continuation_set_probe` |
| Decision | `partial` |
| Provisional AB rung | `AB3` |
| Claim allowed | `false` |
| Derived report only | `false` |
| AP4 status | `required_recorded` |
| AP5 status | `not_applicable` |
| Artifact manifest entries | `10` |

## Branches

| Branch | Target | Support After | Coherence After | Status |
| --- | ---: | ---: | ---: | --- |
| `n24_i5_branch_01_to_node_1` | 1 | 13.000000000000 | 13.000000000000 | `admissible` |
| `n24_i5_branch_02_to_node_5` | 5 | 11.000000000000 | 11.000000000000 | `admissible` |
| `n24_i5_branch_03_to_node_9` | 9 | 12.000000000000 | 12.000000000000 | `admissible` |

## Gates

| Gate | Status |
| --- | --- |
| Support | `preserved` |
| Coherence | `preserved` |
| Boundary | `preserved` |
| Flux/leakage | `preserved` |
| Optionality | `present` |
| Replay | `not_run` |

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_ready` | `true` |
| `i4_ab2_surplus_ready` | `true` |
| `candidate_row_field_set_matches_i2_required_fields` | `true` |
| `derived_report_only_false` | `true` |
| `source_current_inputs_present` | `true` |
| `artifact_manifest_non_empty` | `true` |
| `artifact_manifest_roles_allowed_by_i2` | `true` |
| `source_current_optional_set_present` | `true` |
| `ab3_availability_count_met` | `true` |
| `maintenance_floors_preserved_under_optionality` | `true` |
| `boundary_flux_and_optional_drain_preserved` | `true` |
| `branch_records_are_source_current_not_labels` | `true` |
| `ab3_only_pending_i6` | `true` |
| `ap4_required_ap5_not_applicable` | `true` |
| `unsafe_claim_flags_all_false` | `true` |

## Claim Boundary

This supports only provisional AB3 source-current optional continuation evidence. AB4+ requires I6 replay/control validation; AB5+ requires later stress/threshold evidence.
