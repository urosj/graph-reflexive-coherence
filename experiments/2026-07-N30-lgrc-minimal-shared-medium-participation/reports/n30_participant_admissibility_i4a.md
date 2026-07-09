# N30 Iteration 4-A - P2 Participant Strengthening Variant

Status: `passed`

Acceptance state:
`accepted_topology_fixture_variant_P2_participant_strengthening_no_medium_relation`

Output digest: `353b4417d6b278ee428de5e1adc88fdb7dd456f3aaa7e01c7d92a68d06296421`

## Scope

Iteration 4-A strengthens I4 by adding a second P2 participant-admissibility
candidate under a different N27 topology/fixture shape. It does not replace
I4, does not assign a medium-relation rung, and does not claim medium
perturbation, trace-mediated eligibility, or minimal shared-medium
participation.

## Participant Candidate

```text
row_id = n30_i4a_row_01_topology_fixture_variant_P2_participant_admissibility
participant_ladder_rung = P2_candidate
participant_carrier_id = n30_i4a_participant_carrier_branched_topology_signature
recognizability_metric = signature_distance_under_declared_N27_topology_fixture_mapping
recognizability_observed = 0.03
recognizability_threshold = 0.07
recognizability_margin = 0.04
replay_status = passed
label_drift_control_result = passed
i4_replaced = false
```

## Threshold Source

The recognizability threshold is inherited from the N27 topology-fixture
post-transfer basin-signature tolerance, not independently tuned by N30. N30
accepts that transfer tolerance as the carrier-recognizability gate for this
bounded P2 strengthening probe. This limits the claim to participant
admissibility under topology/fixture variation and does not support general
participant stability or medium-relation evidence.

## Geometric Difference From I4

I4 used a three-node alpha/beta chain with one support lane. I4-A uses a
four-node gamma/delta branched/folded carrier with two support lanes and four
boundary edges. The support-branch count and boundary-edge count remain
preserved across the declared topology/fixture mapping, while the mapped
signature distance remains within threshold: `0.03 <= 0.07`, margin `0.04`.

This makes I4-A a repeatability strengthening probe for P2 participant
admissibility under topology/fixture shape variation. It is still not medium
evidence.

## Artifacts

| Role | Path |
|---|---|
| participant_recognizability_threshold_record | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4a_artifacts/threshold_record.json` |
| participant_carrier_state_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4a_artifacts/participant_carrier_state_trace.json` |
| participant_attribution_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4a_artifacts/participant_attribution_trace.json` |
| participant_replay_recognizability_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4a_artifacts/participant_replay_recognizability_trace.json` |
| participant_label_drift_control_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4a_artifacts/participant_label_drift_control_trace.json` |
| topology_fixture_variant_strengthening_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4a_artifacts/topology_fixture_variant_strengthening_trace.json` |
| i4a_medium_leakage_guard_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_participant_admissibility_i4a_artifacts/i4a_medium_leakage_guard_trace.json` |

## Claim Boundary

```text
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
medium_relation_ladder_rung_assigned = false
medium_surface_trace_evidence_opened = false
later_eligibility_dependency_evidence_opened = false
minimal_shared_medium_participation_claim_allowed = false
```

## Checks

- i4_primary_participant_candidate_passed: true
- underlying_n27_topology_artifacts_consumed_not_closeout_only: true
- i4a_strengthens_without_replacing_i4: true
- participant_carrier_digest_continuity_recorded: true
- recognizability_metric_declared_before_classification: true
- topology_fixture_shape_variant_recorded: true
- replay_status_passed: true
- label_drift_control_passed: true
- i4a_ceiling_guard_preserved: true
- no_medium_evidence_opened: true
- artifact_manifest_sha256_matches: true
- derived_report_only_false_for_candidate: true
- unsafe_claim_flags_false: true
- no_absolute_paths_in_records: true
