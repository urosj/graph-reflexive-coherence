# N30 Iteration 4-B - Participant Boundary / Support Sensitivity

Status: `passed`

Acceptance state:
`accepted_participant_boundary_support_sensitive_P4_candidate_no_medium_relation`

Output digest: `b248e35e131071c606c2c5cc7c7ca1c2638f79ed2ea9fe2fda0959a88bd612d0`

## Scope

Iteration 4-B stress-tests the participant side before any medium-surface
claim is opened. It consumes the N27 stress/mapping-variant matrix over the
I4 and I4-A carriers. It records I4 as boundary-limited and I4-A as the
stronger boundary/support-sensitive participant candidate.

It does not assign a medium-relation rung and does not claim minimal
shared-medium participation.

## Result

```text
strongest_participant_ladder_rung = P4_candidate
strongest_participant_carrier_id = n30_i4a_participant_carrier_branched_topology_signature
i4_boundary_limited = true
i4a_boundary_support_sensitive_candidate_supported = true
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
medium_relation_ladder_rung_assigned = false
minimal_shared_medium_participation_claim_allowed = false
```

## Rows

```text
n30_i4b_row_01_i4_boundary_limited_participant:
  participant_ladder_rung = P2_stress_limited
  decision = partial_boundary_limited_participant_admissibility
  failed_stress_ids = boundary_tightening_0_05, combined_moderate_mapping_stress

n30_i4b_row_02_i4a_boundary_support_sensitive_participant:
  participant_ladder_rung = P4_candidate
  decision = supported_participant_boundary_support_sensitive_candidate_only
  failed_stress_ids = none
  minimum_residual_margin_across_stress = 0.007
```

## Geometric Interpretation

I4-B separates two participant facts. The I4 alpha/beta carrier remains a
valid P2 participant-admissibility candidate, but its boundary margin is at
floor; boundary tightening therefore fails closed and blocks a stronger
participant classification.

The I4-A gamma/delta branched/folded carrier has positive boundary, support,
coherence, and flux margins. It survives boundary tightening, support
drawdown, coherence drawdown, flux pressure, and combined bounded stress. That
supports a bounded P4 participant candidate: the participant is not just
recognizable under replay, but also remains admissible under declared
boundary/support stress.

This is still only participant-side evidence. It says nothing yet about a
non-private medium surface, medium trace, or later eligibility dependency.

## Artifacts

| Role | Path |
|---|---|
| participant_boundary_support_stress_policy_record | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_boundary_support_i4b_artifacts/stress_policy_record.json` |
| participant_boundary_support_sensitivity_matrix | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_boundary_support_i4b_artifacts/participant_boundary_support_sensitivity_matrix.json` |
| participant_p4_candidate_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_boundary_support_i4b_artifacts/participant_p4_candidate_trace.json` |
| participant_stress_limited_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_boundary_support_i4b_artifacts/participant_stress_limited_trace.json` |
| i4b_medium_leakage_guard_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_boundary_support_i4b_artifacts/i4b_medium_leakage_guard_trace.json` |

## Checks

- i4_and_i4a_inputs_passed: true
- n27_stress_matrix_consumed: true
- source_guardrails_match_i4_i4a_and_n27_stress: true
- candidate_rows_have_source_and_artifact_metadata: true
- i4_boundary_limited_not_upgraded: true
- i4a_survives_boundary_support_coherence_flux_stress: true
- stress_policy_declared_before_classification: true
- participant_only_ceiling_preserved: true
- no_medium_or_later_eligibility_evidence_opened: true
- artifact_manifest_sha256_matches: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true
