# N14 Claim Boundary And AP4 Classification

## Status

Status: `passed`.

```text
acceptance_state = accepted_ap4_classification_claim_boundary_clean_pending_closeout
classified_ap_level = AP4
ap4_classification_supported = true
provisional_ap_level = AP4_candidate_boundary_clean_pending_closeout
final_ap4_supported = false
final_ap_freeze_pending_iteration8 = true
phase8_opened = false
native_support_opened = false
```

Iteration 7 classifies the N14 candidate as artifact-level `AP4`
with claim boundaries intact. Final AP4 freeze remains pending until
Iteration 8 closeout.

## AP4 Scope

```text
Observed route-specific memory evidence plus constructed route-conditioned support/regulation followout evidence; upstream observed N09/N13 route-conditioned support/regulation remains unsupported.
```

## Hypotheses

| Hypothesis | Acceptance state | Scope |
| --- | --- | --- |
| `hypothesis_a_pre_selection_consequence_records` | `supported` | source-backed pre-selection route consequence records with explicit support, memory, and regulation descriptors |
| `hypothesis_b_rank_sensitive_route_selection` | `supported` | artifact-level AP4 consequence-sensitive route selection with observed route-specific memory evidence and constructed route-conditioned support/regulation followout evidence |
| `hypothesis_c_intention_and_agency_boundary` | `supported` | all unsafe claim promotions remain blocked despite AP4 classification |

## Boundary Summary

```json
{
  "agency_blocked": true,
  "all_boundary_claims_blocked": true,
  "boundary_row_count": 10,
  "fully_native_integration_blocked": true,
  "identity_acceptance_blocked": true,
  "intention_blocked": true,
  "native_support_without_phase8_blocked": true,
  "selfhood_personhood_biological_behavior_blocked": true,
  "semantic_choice_blocked": true,
  "semantic_goal_ownership_blocked": true,
  "unrestricted_agency_blocked": true,
  "upstream_observed_support_regulation_blocker_recorded": true
}
```

## Boundary Rows

| Row | Blocked claim | Claim allowed |
| --- | --- | --- |
| `n14_i7_boundary_01_consequence_selection_not_intention` | `intention` | `false` |
| `n14_i7_boundary_02_expected_effect_not_goal_ownership` | `semantic_goal_ownership` | `false` |
| `n14_i7_boundary_03_route_preference_not_semantic_choice` | `semantic_choice` | `false` |
| `n14_i7_boundary_04_memory_effect_not_identity_acceptance` | `identity_acceptance` | `false` |
| `n14_i7_boundary_05_constructed_followout_not_upstream_observation` | `upstream_observed_route_conditioned_support_regulation` | `false` |
| `n14_i7_boundary_06_artifact_ap4_not_native_support` | `native_support_without_phase8` | `false` |
| `n14_i7_boundary_07_ap4_not_agency` | `agency` | `false` |
| `n14_i7_boundary_08_ap4_not_selfhood_personhood_biology` | `selfhood_personhood_biological_behavior` | `false` |
| `n14_i7_boundary_09_not_fully_native_integration` | `fully_native_agentic_like_integration` | `false` |
| `n14_i7_boundary_10_not_unrestricted_agency` | `unrestricted_agency` | `false` |

## Interpretation Record

```json
{
  "ap4_scope": "Observed route-specific memory evidence plus constructed route-conditioned support/regulation followout evidence; upstream observed N09/N13 route-conditioned support/regulation remains unsupported.",
  "ap_state_after_claim_boundary": {
    "ap4_classification_supported": true,
    "classified_ap_level": "AP4",
    "final_ap4_supported": false,
    "final_ap_freeze_pending_iteration8": true,
    "native_support_opened": false,
    "phase8_opened": false,
    "provisional_ap_level": "AP4_candidate_boundary_clean_pending_closeout"
  },
  "hypothesis_acceptance_states": {
    "hypothesis_a_pre_selection_consequence_records": "supported",
    "hypothesis_b_rank_sensitive_route_selection": "supported",
    "hypothesis_c_intention_and_agency_boundary": "supported"
  },
  "plain_language_meaning": "Iteration 7 classifies the N14 candidate as AP4 at artifact level with claim boundaries intact. The supported result is consequence-sensitive route selection over source-pinned records, not intention, semantic choice, agency, native support, or fully native integration.",
  "record_id": "n14_i7_interpretation_claim_boundary_ap4_classification_v1",
  "record_type": "n14_iteration_7_claim_boundary_and_ap4_classification",
  "remaining_required_work": [
    "n14_closeout_handoff_iteration_8"
  ],
  "supported_interpretation": "Artifact-level AP4 consequence-sensitive route selection candidate, boundary-clean pending Iteration 8 closeout.",
  "unsupported_interpretations": [
    "intention",
    "semantic_goal_ownership",
    "semantic_choice",
    "identity_acceptance",
    "upstream_observed_route_conditioned_support_regulation",
    "native_support_without_phase8",
    "agency",
    "selfhood_personhood_biological_behavior",
    "fully_native_agentic_like_integration",
    "unrestricted_agency"
  ]
}
```

## Claim Ceiling Candidate

```text
artifact_level_ap4_consequence_sensitive_route_selection_candidate_with_constructed_route_conditioned_support_regulation_followout
```

## Remaining Blockers

```json
[
  "final_ap4_freeze_pending_iteration8",
  "upstream_observed_route_conditioned_support_rows_missing",
  "upstream_observed_route_conditioned_regulation_rows_missing",
  "intention_semantics_missing",
  "semantic_choice_semantics_missing",
  "semantic_goal_ownership_semantics_missing",
  "identity_acceptance_validator_missing",
  "phase8_native_support_not_opened",
  "fully_native_agentic_like_integration_meta_policy_missing"
]
```

## Required False Flags

```json
{
  "agency_claim_opened": false,
  "fully_native_integration_opened": false,
  "identity_acceptance_opened": false,
  "intention_claim_opened": false,
  "native_support_opened": false,
  "personhood_or_biological_behavior_opened": false,
  "phase8_opened": false,
  "selfhood_opened": false,
  "semantic_choice_opened": false,
  "semantic_goal_ownership_opened": false,
  "unrestricted_agency_opened": false
}
```

## Checks

```json
{
  "affordance_conflict_resolved_by_consequence": true,
  "all_boundary_claims_blocked": true,
  "all_claim_flags_forced_false": true,
  "all_negative_controls_blocked": true,
  "all_required_false_flags_false": true,
  "ap4_classification_supported": true,
  "artifact_replay_filesystem_roundtrip": true,
  "boundary_control_references_canonical": true,
  "boundary_evidence_references_typed": true,
  "conditioned_probe_source_passed": true,
  "consequence_source_passed": true,
  "constructed_support_regulation_followout_supported": true,
  "control_source_passed": true,
  "final_ap4_not_frozen_until_iteration8": true,
  "followout_source_passed": true,
  "hypothesis_a_supported": true,
  "hypothesis_b_supported": true,
  "hypothesis_c_supported": true,
  "inventory_source_passed": true,
  "legacy_source_controls_absent": true,
  "native_support_opened_false": true,
  "observed_probe_source_passed": true,
  "observed_route_specific_memory_supported": true,
  "perturbation_and_replay_passed": true,
  "perturbation_source_passed": true,
  "phase8_opened_false": true,
  "schema_source_passed": true,
  "selection_source_passed": true,
  "split_equal_effect_null_controls_passed": true,
  "src_diff_empty": true,
  "upstream_observed_support_regulation_not_supported": true
}
```

## Claim Boundary

```text
consequence-sensitive route selection != intention
expected downstream support effect != semantic goal ownership
support-preserving route choice != agency
memory-sensitive route choice != identity acceptance
regulation-sensitive route choice != goal ownership
route preference != selfhood
artifact-level AP4 != native support
N14 AP4 != fully native agentic-like integration
constructed support/regulation followout != upstream observed route-conditioned support/regulation
```

## Output Digest

```text
828a553f428245c7fff758c519014fe22c4a1fe924b441f0c066dcf09747b2ea
```
