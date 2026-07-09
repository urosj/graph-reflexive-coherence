# N30 Iteration 4 - Minimal Participant Admissibility Probe

Status: `passed`

Acceptance state:
`accepted_minimal_participant_admissibility_P2_candidate_no_medium_relation`

Output digest: `63f72c353b52f18eeeeece349fadde34d5f8a050d67c4f670d2397250b77774f`

## Scope

Iteration 4 is the first positive N30 content row, but its scope is only
participant admissibility. It does not declare a medium surface, does not assign
a medium-relation rung, and does not claim trace-mediated eligibility or minimal
shared-medium participation.

## Participant Candidate

```text
row_id = n30_i4_row_01_minimal_participant_carrier_admissibility
participant_ladder_rung = P2_candidate
participant_carrier_id = n30_i4_participant_carrier_basin_signature_A_mapped
recognizability_metric = signature_distance_under_declared_N27_mapping
recognizability_observed = 0.025
recognizability_threshold = 0.06
recognizability_margin = 0.035
replay_status = passed
label_drift_control_result = passed
```

The participant carrier is a mapped basin-signature carrier consumed from
underlying N27 source-current traces and replay records. The claim is not that
the carrier has selfhood, identity, agency, or semantic role. The claim is only
that the same carrier remains recognizable across the bounded pre/post/replay
window.

## Threshold Source

The recognizability threshold is inherited from the N27 post-transfer
basin-signature tolerance, not independently tuned by N30. N30 accepts that
transfer tolerance as the carrier-recognizability gate for this bounded P2
probe. This limits the claim to participant admissibility and does not support
general participant stability or medium-relation evidence.

## Geometric Interpretation

Geometrically, I4 treats the participant as a basin-signature carrier rather
than as a semantic actor. The alpha-frame basin signature is mapped into the
beta-frame basin signature while preserving support, coherence, boundary
mapping, and bounded flux. The recognizability metric is the mapped signature
distance: `0.025 <= 0.06`, with margin `0.035`. That is enough for a P2
participant-admissibility candidate, but it is not a medium perturbation or
shared-medium relation.

## Artifacts

| Role | Path |
|---|---|
| participant_recognizability_threshold_record | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4_artifacts/threshold_record.json` |
| participant_carrier_state_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4_artifacts/participant_carrier_state_trace.json` |
| participant_attribution_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4_artifacts/participant_attribution_trace.json` |
| participant_replay_recognizability_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4_artifacts/participant_replay_recognizability_trace.json` |
| participant_label_drift_control_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4_artifacts/participant_label_drift_control_trace.json` |
| i4_medium_leakage_guard_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4_artifacts/i4_medium_leakage_guard_trace.json` |

## Claim Boundary

```text
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
medium_relation_ladder_rung_assigned = false
medium_surface_trace_evidence_opened = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
```

## Checks

- i3_active_nulls_passed: true
- underlying_n27_artifacts_consumed_not_closeout_only: true
- required_i4_fields_present: true
- participant_carrier_digest_continuity_recorded: true
- recognizability_metric_declared_before_classification: true
- replay_status_passed: true
- label_drift_control_passed: true
- i4_ceiling_guard_preserved: true
- no_medium_evidence_opened: true
- artifact_manifest_sha256_matches: true
- derived_report_only_false_for_candidate: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true
