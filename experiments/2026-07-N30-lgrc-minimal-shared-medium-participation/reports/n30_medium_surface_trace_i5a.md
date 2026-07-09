# N30 Iteration 5-A - Mechanism-Diverse Medium Surface Trace

Status: `passed`

Acceptance state:
`accepted_mechanism_diverse_medium_surface_trace_M1_strengthening_no_later_eligibility`

Output digest: `519cc4efb48963232d969a6ecbf9d67e1b8dda005d89faed5f17995c233590ef`

## Scope

Iteration 5-A strengthens I5 without replacing it. It consumes the N28 I4-A2
source-current generative mechanism-diversity row and its N28 replay trace to
declare a second non-private neighbor capacity shell as a medium surface.

This is inherited/source-current medium-surface admission, not fresh N30
runtime evidence. The N28 artifacts may support C4/M1 surface-trace admission;
they may not support C5/M2 later eligibility dependency unless I6/I7 add a new
N30 relation-chain dependency test.

This is still not minimal shared-medium participation. I5-A records medium
surface perturbation and replay-persistent surface change only. Later
eligibility or susceptibility dependency remains I6 scope.

## Result

```text
participant_carrier_id = n28_i4a2_focal_basin_epsilon
medium_surface_id = n28_i4a2_split_neighbor_capacity_shell_epsilon
medium_surface_scope = shared_local
participant_medium_distinct = true
medium_relation_ladder_rung = M1_candidate
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
runtime_origin = inherited_N28_source_current_artifact
n30_fresh_runtime = false
row_participant_ladder_rung = P2_candidate_with_I4B_P4_guardrail
strongest_N30_I5A_row_participant_rung = P2_candidate
source_i4b_strongest_participant_guardrail = P4_candidate
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
```

## Surface Change

```text
neighbor_distinguishability_delta = 0.141
neighbor_support_delta = 0.084
neighbor_boundary_delta = 0.132
environment_capacity_delta = 0.127
trace_persistence_status = replay_persistent_no_decay_curve
i5_replaced = false
i5a_strengthens_i5 = true
strengthening_kind = mechanism_diversity_repeatability_not_margin_upgrade
margin_upgrade_claimed = false
```

## Scope Classification

```text
i5a_positive_scope = inherited_source_current_medium_surface_trace_only
i5a_claim_type = inherited_medium_surface_trace_admission
supports_N30_C4 = true
supports_N30_C5 = false
supports_M1 = true
supports_M2 = false
n28_controls_classified_as = source_guardrail_controls_not_N30_relation_controls
trace_dependency_control_ids = pending_iteration_7
n30_relation_controls = pending_iteration_7
medium_surface_scope_status = shared_local_candidate_pending_later_encounter
```

## Geometric Interpretation

I5-A treats the N28 I4-A2 focal basin as the local participant side and the
I4-A2 split-shell neighbor capacity surface as the medium surface. The surface
is not the focal basin itself: it is a distinct shared-local shell with
distinguishability, support, boundary integrity, and environment-capacity
fields.

Geometrically, the focal basin remains viable while a split neighboring shell
becomes more distinguishable, better supported, better bounded, and more
basin-forming. This is a second M1 medium-surface perturbation / trace
candidate. It is not a stronger-margin upgrade over I5: the I4-A2 deltas are
slightly smaller than I5. Its value is mechanism diversity. I5 used a
single-shell strengthening source, while I5-A uses split-shell capacity growth
with delayed boundary thickening.

I4-B is consumed as participant-side discipline: N30 already has a bounded P4
participant guardrail. That P4 value is a source guardrail, not the I5-A row's
own participant rung. The I5-A row remains
`P2_candidate_with_I4B_P4_guardrail`. I5-A does not claim that the N27 carrier
itself perturbed the N28 surface; the load-bearing medium trace is the N28
I4-A2 source-current focal/neighbor relation.

I5 remains the primary minimal M1 row. I5-A is additional mechanism-diverse M1
evidence, not a replacement, not a widened envelope, and not M2/C5 evidence.
C4 and C5 remain separate: C4 means a changed medium surface exists; C5 means
a later response depends on that changed surface. I5-A supports C4 only.

## Artifacts

| Role | Path |
|---|---|
| medium_surface_declaration_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/medium_surface_declaration_trace.json` |
| participant_medium_separation_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/participant_medium_separation_trace.json` |
| medium_perturbation_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/medium_perturbation_trace.json` |
| trace_or_surface_change | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/trace_or_surface_change.json` |
| trace_persistence_or_decay | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/trace_persistence_or_decay.json` |
| medium_debt_record | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/medium_debt_record.json` |
| i5a_medium_leakage_guard_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/i5a_medium_leakage_guard_trace.json` |
| i5a_scope_classification | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/i5a_scope_classification.json` |
| i5a_vs_i5_medium_trace_comparison | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_medium_surface_trace_i5a_artifacts/i5a_vs_i5_medium_trace_comparison.json` |

## Claim Boundary

```text
medium_relation_ladder_rung_assigned = M1_candidate
medium_surface_trace_evidence_opened = true
later_eligibility_dependency_evidence_opened = false
source_guardrail_controls = N28_controls_only
n30_relation_controls = pending_iteration_7
minimal_shared_medium_participation_claim_allowed = false
shared_medium_coordination_claim_allowed = false
native_shared_medium_organization_claim_allowed = false
```

## Checks

- i4b_participant_guardrail_passed: true
- n28_i4a2_source_current_artifacts_consumed_not_closeout_only: true
- i5a_scope_classification_preserves_inherited_runtime_boundary: true
- n28_controls_are_guardrails_not_n30_relation_controls: true
- i4b_p4_guardrail_does_not_promote_i5a_row_participant_rung: true
- i5a_strengthens_i5_without_replacing_it: true
- medium_surface_declared_non_private: true
- participant_medium_distinct: true
- surface_change_deltas_pass_thresholds: true
- capacity_attribution_controls_clean: true
- replay_persistence_available_without_later_dependency_claim: true
- i5a_ceiling_guard_preserved: true
- artifact_manifest_sha256_matches: true
- derived_report_only_false_for_candidate: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true
