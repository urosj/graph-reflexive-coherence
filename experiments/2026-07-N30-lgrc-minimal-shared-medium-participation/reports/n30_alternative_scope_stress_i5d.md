# N30 Iteration 5-D - Alternative Scope / Stress Audit

Status: `passed`

Acceptance state: `accepted_alternative_M1_circulatory_surface_replay_stress_audit`

Output digest: `5052dc86851af8f12bc26949a640b6df4eb766183255b83a8b90416eeff13b92`

## Interpretation

I5-D verifies that the alternative I5-C circulatory surface survives focused N28 replay and stress. It still does not open later eligibility.

## Key Fields

```text
participant_ladder_rung_assigned = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung_assigned = M1_candidate_alternative_circulatory_surface
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
minimum_current_margin = 0.006
neighbor_capacity_current_margin = 0.01
minimal_shared_medium_participation_claim_allowed = false
```

## Artifacts

| Role | Path |
|---|---|
| i5d_alternative_scope_stress_matrix | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_scope_stress_i5d_artifacts/i5d_alternative_scope_stress_matrix.json` |
| i5d_claim_boundary_guard | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_scope_stress_i5d_artifacts/i5d_claim_boundary_guard.json` |

## Checks

- source_i5c_passed: true
- replay_and_stress_supported: true
- minimum_margin_materially_above_i6_edge: true
- later_eligibility_claims_closed: true
- artifact_manifest_sha256_matches: true
- no_absolute_paths_in_records: true
