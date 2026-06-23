# N22 Iteration 2 - Susceptibility Schema And Controls

## Summary

Status: `passed`

Acceptance state: `accepted_susceptibility_schema_frozen_no_positive_evidence`

Output digest: `a6d4e478b1e29f31007bb965c97a838764e196f18ca7ac8e1c78a7ccfc03680f`

Iteration 2 freezes the N22 schema and control contract. It opens no
positive susceptibility evidence and assigns no SU or N22-C rung.

## Frozen Ladders

| Ladder | Count | Boundary |
| --- | ---: | --- |
| SU | 7 | Rows below SU3 cannot support durable geometry modification; SU6 is N23 handoff only. |
| N22-C | 7 | Tranche-level closeout ladder; not semantic learning or agency. |

## Key Frozen Policies

- N19 is consumed as `ap_gap_boundary_only`, not susceptibility evidence.
- N20 inherited status is mirrored as `n20_source_downstream_consumption_status`.
- Candidate rows require source-current inputs and thresholds declared before use.
- Candidate rows require an `artifact_manifest` with repository-relative paths, roles, and SHA-256 digests.
- Support/coherence/boundary/flux acceptance is field-specific; changed values must preserve the declared floor or bound.
- Historical interaction provenance is separated from active reinforcement.
- Active reinforcement schedule, queue, and in-flight budget must be absent for durable-delta support.
- Active reinforcement can leave SU1/SU2 descriptive traces, but blocks SU4, SU5, SU6, N22-C4, N22-C5, N22-C6, and the ND6 bridge.
- Route/region-conditioned rows require peer same-budget comparison and global-drift rejection.
- Non-route SU2 rows may mark peer comparison `not_applicable` only with `non_route_conditioned_SU2_only` scope reason.
- `artifact_only_replay` is an alias for canonical `artifact_replay`.
- AP4/AP5 dependencies use closed enums and row-local condition reasons.
- I3 must include AP-gap active nulls for missing AP4, missing AP5, and prose-only AP gap handling.
- N21 ND6 bridge remains `not_supported` until source-backed SU5/SU6 evidence exists.

## Required Candidate Field Count

`61` fields

## Checks

| Check | Passed |
| --- | --- |
| `source_i1_inventory_passed` | `true` |
| `i1_boundary_kept_no_susceptibility_evidence` | `true` |
| `candidate_evidence_row_schema_complete` | `true` |
| `n19_boundary_only_schema_frozen` | `true` |
| `n20_prefixed_status_frozen` | `true` |
| `run_artifact_admissibility_fail_closed` | `true` |
| `threshold_policy_declared_before_use` | `true` |
| `susceptibility_delta_schema_blocks_labels` | `true` |
| `allowed_drift_and_same_basin_schema_frozen` | `true` |
| `historical_interaction_active_reinforcement_split_frozen` | `true` |
| `peer_same_budget_comparison_mandatory_when_conditioned` | `true` |
| `durability_metrics_frozen` | `true` |
| `support_coherence_boundary_flux_schema_frozen` | `true` |
| `replay_control_schema_frozen` | `true` |
| `active_null_comparability_frozen` | `true` |
| `su_ladder_complete` | `true` |
| `n22_closeout_ladder_complete` | `true` |
| `ap_dependency_enums_frozen` | `true` |
| `n21_nd6_bridge_status_enum_frozen` | `true` |
| `demotion_precedence_frozen` | `true` |
| `row_decision_policy_frozen` | `true` |
| `claim_boundary_schema_frozen` | `true` |
| `closeout_status_enums_frozen` | `true` |
| `primitive_schema_row_frozen_from_i1` | `true` |
| `no_positive_evidence_opened` | `true` |
| `no_local_absolute_paths` | `true` |

## Interpretation

I2 is a schema freeze. It does not show susceptibility update, durable
geometry modification, semantic learning, choice, agency, native
support, sentience, Phase 8, or ant-ecology implementation.

The next step is Iteration 3 active nulls and failure baselines.
