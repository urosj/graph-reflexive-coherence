# N30 Iteration 3 - Active Nulls And Failure Baselines

Status: `passed`

Acceptance state:
`accepted_active_nulls_fail_closed_no_positive_evidence`

Output digest: `20de953306725e68bb866f5a71c65b1239cec4ecfc36abb3710d95ae9e4a5c49`

## Scope

Iteration 3 instantiates the false-positive boundary from the I2 schema. These
rows can block unsafe paths, but they cannot support participant admissibility,
medium trace evidence, later eligibility dependency, or N30-C5/C6.

`failed_closed` means the blocker triggered and the claim was rejected.
`failed_open` would mean the blocker triggered but the row still passed.

## Null Rows

| Null | Blocked Gate | Blocked Rung | Hypothesis | Failed Closed |
|---|---|---|---|---:|
| direct_message_only_relabel | medium_surface_non_private_trace_gate | N30-C5 | Hypothesis D | true |
| medium_surface_label_only | declared_medium_surface_trace_gate | N30-C4 | Hypothesis C | true |
| hidden_global_controller | later_response_depends_on_medium_trace | N30-C5 | Hypothesis E | true |
| hidden_producer_routing | producer_residue_and_trace_dependency_gate | N30-C5 | Hypothesis D | true |
| post_hoc_trace_construction | source_current_trace_gate | N30-C4 | Hypothesis C | true |
| no_perturbation_control | participant_to_medium_perturbation_gate | N30-C4 | Hypothesis C | true |
| trace_ablation_control | later_response_depends_on_medium_trace | N30-C5 | Hypothesis E | true |
| wrong_surface_control | declared_surface_specificity_gate | N30-C5 | Hypothesis C | true |
| time_reversed_trace_control | causal_order_gate | N30-C5 | Hypothesis E | true |
| medium_freeze_control | medium_surface_change_gate | N30-C4 | Hypothesis C | true |
| trace_shuffle_control | relation_chain_identity_gate | N30-C5 | Hypothesis E | true |
| false_trace_injection_control | trace_provenance_gate | N30-C4 | Hypothesis C | true |
| decay_manipulation_control | trace_persistence_or_decay_gate | N30-C5 | Hypothesis C | true |
| susceptibility_inversion_control | predeclared_later_response_metric_gate | N30-C5 | Hypothesis C | true |
| participant_label_drift_control | participant_carrier_continuity_gate | N30-C3 | Hypothesis B | true |
| generic_redistribution_relabel | N28_environment_effect_distinction_gate | N30-C5 | Hypothesis D | true |
| semantic_communication_relabel | claim_boundary_gate | N30-C6 | Hypothesis D | true |
| semantic_coordination_relabel | claim_boundary_gate | N30-C6 | Hypothesis D | true |
| cooperation_agency_relabel | claim_boundary_gate | N30-C6 | Hypothesis D | true |
| native_shared_medium_organization_relabel | native_shared_medium_claim_boundary_gate | N30-C6 | Hypothesis D | true |

## Interpretation

The nulls make the relation-chain boundary explicit. A later positive row
cannot pass by combining participant labels, trace labels, or later differences
after the fact. Direct messages, hidden producers, global controllers,
post-hoc traces, wrong surfaces, time reversal, trace shuffling, false trace
injection, decay manipulation, participant label drift, generic redistribution,
and semantic relabels all fail closed before any positive N30 probe runs.

## Fixture And Control Policy

```text
null_fixture_id = n30_i3_pre_positive_active_null_fixture
null_fixture_config_digest = aaf2736324b8284f7d7da6137309276e1f7ac706cd9579c3ed5a742b2e321beb
null_generation_policy_digest = df29a80fa0120267362c2680387f77c12fd6e58577a822c33b94282505d2aeb1
```

I3 nulls are pre-positive false-positive blockers. They do not substitute for
I7 runtime controls. I7 must rerun or reinstantiate equivalent controls against
the actual I4-I6 positive candidate fixture; `covered_by_i3` alone blocks
positive candidate validation.

The `observed_fail_reason` field is preserved because I2 requires it, but in
I3 its observation source is `pre_positive_synthetic_active_null_fixture`. These
values are declared fail-closed fixture conditions, not runtime measurements.

## I4 Ceiling Guard

I4 may test only participant admissibility. Its maximum ceiling is
`N30-C3_participant_admissibility_candidate`. I4 cannot assign a medium-relation
rung, medium perturbation claim, trace-mediated eligibility claim, or minimal
shared-medium participation claim. Any medium observation in I4 is exploratory
only and cannot support N30-C4 or N30-C5.

I4 must distinguish same label from same carrier by recording carrier digest or
trace continuity, recognizability metric, recognizability threshold, replay
status, and label-drift control result.

## Checks

- i2_schema_freeze_passed: true
- all_required_null_ids_present_once: true
- all_required_null_fields_present: true
- all_nulls_fail_closed: true
- no_failed_open_rows: true
- nulls_map_to_specific_gates_and_rungs: true
- nulls_reference_hypotheses: true
- no_positive_evidence_opened: true
- active_nulls_not_runtime_artifacts: true
- observed_fail_reasons_marked_synthetic: true
- null_fixture_reproducibility_digests_present: true
- i3_nulls_do_not_substitute_for_i7_runtime_controls: true
- i4_ceiling_guard_blocks_medium_evidence: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true

## Claim Boundary

`minimal_shared_medium_participation_claim_allowed = false`

`shared_medium_coordination_claim_allowed = false`

`native_shared_medium_organization_claim_allowed = false`
