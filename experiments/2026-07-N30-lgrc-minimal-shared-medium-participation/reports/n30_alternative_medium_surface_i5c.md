# N30 Iteration 5-C - Alternative Medium-Surface Trace

Status: `passed`

Acceptance state: `accepted_alternative_M1_circulatory_medium_surface_trace`

Output digest: `754c8cabeeb35d4274b2841ecc7458eeebb9c1eee8c1c5d26782c38a4bf2b335`

## Interpretation

I5-C declares the N28 I4-F wide circulatory neighbor field as an alternative shared-local medium surface. The surface is circulatory rather than generative: one lobe gains, one lobe loses, and a buffer lobe remains near stable.

## Key Fields

```text
participant_ladder_rung_assigned = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung_assigned = M1_candidate_alternative_circulatory_surface
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate
minimum_lobe_exchange_margin = 0.02
minimal_shared_medium_participation_claim_allowed = false
```

## Artifacts

| Role | Path |
|---|---|
| alternative_medium_surface_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_medium_surface_i5c_artifacts/alternative_medium_surface_trace.json` |
| i5c_participant_medium_separation_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_medium_surface_i5c_artifacts/i5c_participant_medium_separation_trace.json` |

## Checks

- source_i4c_passed: true
- circulatory_surface_margin_positive: true
- participant_medium_distinct: true
- later_eligibility_claims_closed: true
- artifact_manifest_sha256_matches: true
- no_absolute_paths_in_records: true
