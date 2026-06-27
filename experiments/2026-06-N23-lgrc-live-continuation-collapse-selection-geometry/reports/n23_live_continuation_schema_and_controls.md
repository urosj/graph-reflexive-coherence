# N23 Iteration 2 - Schema, Ladder, And Control Freeze

## Summary

Status: `passed`

Acceptance state: `accepted_live_continuation_schema_frozen_no_positive_evidence`

Output digest: `71de40c448a031ea352b94723cb538b9a333aa3e66d88080c2218338a23278e4`

Iteration 2 freezes N23 schema and control rules. It opens no positive
live-continuation evidence, assigns no LC rung, and does not support an
AP4 bridge.

## Frozen Ladders

| Ladder | Count | Boundary |
| --- | ---: | --- |
| LC | 7 | Rows below LC3 cannot support collapse; LC6 is N24 handoff only. |
| N23-C | 7 | Tranche-level closeout ladder; not semantic choice or agency. |

## Key Frozen Policies

- Live branches must be same-run, same-window, pre-collapse source-current records.
- Original LC2 branch evidence must come from the same source-current runtime trace; replay forks audit but do not create original branches.
- Required traces carry `trace_status`, `trace_origin`, and rung-blocking fields when missing.
- `branch_record_origin = source_current_same_run` is required for LC2+.
- Replay forks may audit counterfactuals but cannot create original live branches.
- Counterfactual retention means immutable pre-collapse audit evidence.
- Selected-branch reasons use a closed source-current enum.
- AP4-relevant selected reasons require route/branch conditioning and peer or counterfactual comparison.
- Producer labels, producer preference, random ties, post-hoc report selection, single-branch relabels, and semantic-choice labels are blocked.
- `susceptibility_delta_conditioned` cannot pass from inherited N22 evidence alone; row-local N23 susceptibility expression is required.
- Candidate AP dependency statuses use row-local enums only; inventory/meta AP values are invalid for candidate rows.
- Numeric support/coherence/boundary/flux/collapse thresholds must be frozen before positive probes.
- `not_applicable` support/coherence/boundary/flux result values block LC2+ candidate support.
- Artifact path and SHA lists must match artifact manifest paths and SHA values.
- `failed_closed` is the expected good result for required negative controls; `failed_open` invalidates and `not_run` blocks dependent rungs.
- Positive LC support cannot come from report, inherited-context, source-contract, or closeout-only artifacts.
- Required controls include random tie, missing counterfactual retention, N22-as-choice relabel, AP4/AP5 missing, AP-gap prose-only, and unsafe relabel controls.

## Required Candidate Field Count

`80` fields

## AP Dependency Enums

```text
ap4_dependency_status = ['required_recorded', 'not_applicable', 'missing_blocks_row']
ap5_dependency_status = ['conditional_required_recorded', 'not_applicable', 'missing_blocks_row']
invalid_candidate_values = ['not_supported_inventory_only', 'conditional_pending_future_rows', 'required_local_gap_dependency']
```

## Evidence Boundary

```text
candidate_rows_classified = false
positive_run_artifacts_consumed = false
live_continuation_collapse_evidence_opened = false
lc_ladder_rung_assigned = false
n23_closeout_ceiling = N23-C0_schema_freeze_only
ap4_bridge_status = not_supported
semantic_choice_supported = false
agency_supported = false
native_support_supported = false
phase8_opened = false
```

## Checks

| Check | Passed |
| --- | --- |
| `source_i1_inventory_passed` | `true` |
| `i1_boundary_kept_no_live_continuation_evidence` | `true` |
| `candidate_evidence_row_schema_complete` | `true` |
| `n19_boundary_only_schema_frozen` | `true` |
| `prefixed_source_status_fields_frozen` | `true` |
| `source_row_digests_split_frozen` | `true` |
| `live_branch_acceptance_frozen` | `true` |
| `trace_status_fields_frozen` | `true` |
| `branch_record_origin_enum_frozen` | `true` |
| `run_artifact_admissibility_fail_closed` | `true` |
| `artifact_manifest_crosschecks_frozen` | `true` |
| `artifact_role_enum_and_positive_restrictions_frozen` | `true` |
| `branch_collapse_temporal_ordering_frozen` | `true` |
| `counterfactual_retention_schema_frozen` | `true` |
| `selected_branch_reason_enum_frozen` | `true` |
| `ap4_relevant_reason_subset_frozen` | `true` |
| `n22_susceptibility_inheritance_blocker_frozen` | `true` |
| `n23_susceptibility_expression_trace_required` | `true` |
| `producer_preference_absence_schema_frozen` | `true` |
| `canonical_control_ids_frozen` | `true` |
| `threshold_policy_declared_before_use` | `true` |
| `support_coherence_boundary_flux_schema_frozen` | `true` |
| `replay_control_schema_frozen` | `true` |
| `failed_closed_negative_control_semantics_frozen` | `true` |
| `active_null_comparability_frozen` | `true` |
| `lc_ladder_complete` | `true` |
| `n23_closeout_ladder_complete` | `true` |
| `ap_dependency_enums_frozen` | `true` |
| `inventory_meta_ap_values_invalid_for_candidate_rows` | `true` |
| `ap4_bridge_status_enum_frozen` | `true` |
| `row_decision_policy_frozen` | `true` |
| `claim_boundary_schema_frozen` | `true` |
| `demotion_precedence_frozen` | `true` |
| `no_positive_evidence_opened` | `true` |

## Interpretation

I2 is a schema freeze only. It does not show live branch existence,
collapse, counterfactual retention, AP4 bridge evidence, semantic
choice, intention, agency, native support, sentience, Phase 8, or ant
ecology implementation.

The next step is Iteration 3 active nulls and failure baselines.
