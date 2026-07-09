# N30 Iteration 6-B - Alternative Later Eligibility Probe

Status: `passed`

Acceptance state: `accepted_alternative_M2_later_eligibility_candidate_pending_I7_controls`

Output digest: `df9d1789199368ac62385e3e0052d2dcfaf4858bb44eecc338e66b07240f10f5`

## Interpretation

I6-B opens an alternative provisional M2 dependency over the I4-F circulatory route-conductance surface. Its neighbor-capacity stress margin is 0.010, compared with the original I6 edge margin of 0.002.

## Key Fields

```text
participant_ladder_rung_assigned = P2_candidate_alternative_source_fixture
medium_relation_ladder_rung_assigned = M2_candidate_alternative_source_pending_I7_controls
n30_closeout_ceiling = N30-C4_medium_perturbation_trace_candidate_with_alternative_C5_input_evidence
alternative_neighbor_capacity_threshold_margin = 0.01
alternative_lobe_exchange_margin = 0.02
minimal_shared_medium_participation_claim_allowed = false
final_n30_c5_claim_allowed = false
```

## Artifacts

| Role | Path |
|---|---|
| alternative_susceptibility_or_eligibility_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_later_eligibility_i6b_artifacts/alternative_susceptibility_or_eligibility_trace.json` |
| alternative_coupled_relation_lineage_trace | `experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/outputs/n30_alternative_later_eligibility_i6b_artifacts/alternative_coupled_relation_lineage_trace.json` |

## Checks

- source_i5d_passed: true
- alternative_margin_exceeds_i6_reference: true
- later_dependency_opened_but_final_c5_blocked: true
- artifact_manifest_sha256_matches: true
- no_absolute_paths_in_records: true
