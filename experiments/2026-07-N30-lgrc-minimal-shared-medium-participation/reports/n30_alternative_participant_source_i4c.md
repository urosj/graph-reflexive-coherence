# N30 Iteration 4-C - Alternative Participant Source Fixture Admission

Status: `passed`

Acceptance state: `accepted_alternative_P2_participant_source_fixture_no_medium_claim`

Output digest: `80f5346ac422749246050bc5e4514c323ea63f7dc7d49394628ad2b6860d668d`

## Interpretation

I4-C admits the N28 I4-F focal basin as an alternative P2 participant source fixture. It does not open a medium relation claim.

## Key Fields

```text
participant_ladder_rung_assigned = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung_assigned = not_assigned
n30_closeout_ceiling = N30-C3_participant_admissibility_candidate
minimal_shared_medium_participation_claim_allowed = false
```

## Artifacts

| Role | Path |
|---|---|
| alternative_participant_carrier_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_participant_source_i4c_artifacts/alternative_participant_carrier_trace.json` |
| i4c_claim_boundary_guard | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_participant_source_i4c_artifacts/i4c_claim_boundary_guard.json` |

## Checks

- source_i4f_passed: true
- focal_basin_support_coherence_stability_preserved: true
- medium_relation_claims_closed: true
- artifact_manifest_sha256_matches: true
- no_absolute_paths_in_records: true
