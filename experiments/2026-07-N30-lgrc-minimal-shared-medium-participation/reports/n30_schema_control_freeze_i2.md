# N30 Iteration 2 - Participant / Medium Schema Freeze

Status: `passed`

Acceptance state:
`accepted_participant_medium_schema_controls_frozen_no_positive_evidence`

Output digest: `1286b3242c3a466c34289be0d4d1589be428c10782ac64eadff7611483b1462c`

## Scope

Iteration 2 freezes the contract that later positive rows must obey. It assigns
no participant rung, no medium-relation rung, and no final closeout rung.

## Participant Ladder

| Rung | Label | N30 Positive Support |
|---|---|---|
| P0 | medium_only_perturbation_no_attributable_participant | false |
| P1 | attributable_contributor_or_respondent_within_one_event_chain | minimal_input_only |
| P2 | same_carrier_recognizable_across_bounded_replay_window | true |
| P3 | boundary_or_interface_participant | secondary_observation_only |
| P4 | support_sensitive_participant | secondary_observation_only |
| P5 | withdrawal_resistant_participant_out_of_N30_primary_scope | false |
| P6 | generative_participant_out_of_N30_primary_scope | false |
| P7 | agentic_participant_blocked | false |

## Shared-Medium Relation Ladder

| Rung | Label | N30 Positive Support |
|---|---|---|
| M0 | direct_message_passing | false |
| M1 | boundary_perturbation | true |
| M2 | trace_mediated_eligibility_or_influence | true |
| M3 | shared_field_co_response_optional_secondary_candidate | secondary_candidate_only |
| M4 | parent_basin_modulation_blocked_future | false |
| M5 | resonant_alignment_blocked_future | false |
| M6 | native_shared_medium_organization_blocked_future | false |

## Coupled Relation Chain

A later row cannot close at N30-C5 or N30-C6 unless one causal lineage links:

```text
participant continuity
medium surface perturbation
trace or surface change
later eligibility / susceptibility / cost / routing / support / capacity change
```

Separate components without ordered dependency are partial or rejected.

## Minimum Rung Policy

```text
N30-C3 may close with P1.
N30-C4 may close with P1 + M1.
N30-C5 and N30-C6 require P2 + M2.
```

This keeps boundary perturbation from being promoted into trace-mediated
shared-medium participation. M1 is necessary for N30-C4, but it is not
sufficient for C5/C6 without later eligibility or susceptibility dependence.

## Separation And Telemetry Policies

```text
same participant_carrier_id == medium_surface_id blocks N30-C5/C6
```

Same-identifier rows may be recorded as internal aftereffect,
medium-mediated self-aftereffect, or partial rows, but not as minimal
shared-medium participation closeout evidence.

Telemetry-only surfaces are also blocked. A packet/event history surface must
condition runtime later response; if it exists only as a report or log artifact,
it is classified as post-hoc trace construction or label-only surface.

## Controls Frozen

- `direct_message_only_relabel`
- `medium_surface_label_only`
- `hidden_global_controller`
- `hidden_producer_routing`
- `post_hoc_trace_construction`
- `no_perturbation_control`
- `trace_ablation_control`
- `wrong_surface_control`
- `time_reversed_trace_control`
- `medium_freeze_control`
- `trace_shuffle_control`
- `false_trace_injection_control`
- `decay_manipulation_control`
- `susceptibility_inversion_control`
- `participant_label_drift_control`
- `generic_redistribution_relabel`
- `semantic_communication_relabel`
- `semantic_coordination_relabel`
- `cooperation_agency_relabel`
- `native_shared_medium_organization_relabel`

## Hypothesis Linkage

I3 active nulls and later positive rows should reference these hypothesis IDs
through `dependent_hypothesis`:

- Hypothesis A: `source_basis_and_method_admission`
- Hypothesis B: `participant_continuity_gate`
- Hypothesis C: `medium_trace_and_later_eligibility_gate`
- Hypothesis D: `debt_controls_and_claim_boundary_gate`
- Hypothesis E: `coupled_relation_chain_gate`

## Checks

- i1_source_inventory_passed: true
- participant_ladder_frozen: true
- medium_relation_ladder_frozen: true
- n30_closeout_ladder_frozen: true
- candidate_required_fields_present: true
- coupled_relation_chain_requirement_frozen: true
- sharedness_gate_blocks_private_internal: true
- participant_medium_separation_audit_frozen: true
- C5_C6_minimum_rung_policy_frozen: true
- telemetry_only_medium_surfaces_blocked: true
- later_response_metrics_predeclared: true
- controls_cover_plan_required_ids: true
- active_null_gate_mapping_fields_required: true
- replay_requirements_block_C5_until_replay_controls: true
- unsafe_claim_flags_false: true
- no_positive_evidence_opened: true
- no_absolute_paths_in_records: true

## Claim Boundary

`minimal_shared_medium_participation_claim_allowed = false`

`shared_medium_coordination_claim_allowed = false`

`native_shared_medium_organization_claim_allowed = false`
