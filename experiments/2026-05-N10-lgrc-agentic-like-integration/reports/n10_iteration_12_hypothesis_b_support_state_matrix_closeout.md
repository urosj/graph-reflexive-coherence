# N10 Iteration 12 Hypothesis B Support-State Matrix Closeout

Status: `passed`.

## Result

Iteration 12 closes Hypothesis B for the bounded N10 scope. The
result is support-sensitive full composition: intact and mild
support states preserve the composition, disrupted support blocks it,
and explicit restoration resumes it without erasing the disruption
history.

```text
hypothesis_b_status = supported_bounded_support_sensitive_full_composition
hypothesis_b_supported = True
positive_scope = bounded_artifact_only_support_sensitive_full_composition
disrupted_support_blocker = support_disrupted_but_integration_allowed
restoration_preserves_disruption_history = True
artifact_only = true
runtime_state_used = false
```

## Support-State Matrix

```json
[
  {
    "accepted_integration_level": "A5",
    "accepted_n10_category_level": "ALI5",
    "artifact_only": true,
    "budget_error_zero": true,
    "claim_flags_false": true,
    "expected_outcome": "composition_preserved",
    "integration_allowed": true,
    "integration_outcome_tag": "bounded_artifact_only_agentic_like_integration_candidate",
    "matrix_row_digest": "b2a0a61cfa78c3a8d1ca7c7a42258605aa9756a2918afb6f1232ca881b291c2e",
    "matrix_state": "support_intact_survives",
    "outcome_matches_expectation": true,
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 8,
    "source_row_digest": "8ad9934bc4cef846dfbc510661dc70f1bef1fa34b354a8c7087a70d25722559e",
    "support_state_tag": "support_intact_survives"
  },
  {
    "accepted_integration_level": "A5",
    "accepted_n10_category_level": "ALI5",
    "artifact_only": true,
    "budget_error_zero": true,
    "claim_flags_false": true,
    "expected_outcome": "composition_preserved_under_bounded_companion_scope",
    "integration_allowed": true,
    "integration_outcome_tag": "route_memory_regulation_composition_candidate",
    "matrix_row_digest": "3d386c98bc1f66d4250b7af0c761d39ffe8e99a5df90f1c1deb598c97d31ca38",
    "matrix_state": "mild_withdrawal_survives",
    "outcome_matches_expectation": true,
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 8,
    "source_row_digest": "d56e47861c728bcd694e4601bb9fde17919373a7374306e1995acc33931f6bf3",
    "support_state_tag": "mild_withdrawal_survives"
  },
  {
    "accepted_integration_level": null,
    "accepted_n10_category_level": null,
    "artifact_only": true,
    "attempted_integration_level": "A6",
    "attempted_n10_category_level": "ALI6",
    "budget_error_zero": true,
    "claim_flags_false": true,
    "expected_outcome": "composition_blocked_or_downgraded",
    "integration_allowed": false,
    "matrix_row_digest": "56f4e1c524bc4bd6ea2712963e6476e15686c639861e56677feca3e7534ccafe",
    "matrix_state": "n09_matched_withdrawal_disrupts_support",
    "outcome_matches_expectation": true,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 10,
    "source_row_digest": "22b6166b43401ea2ceab6577f6ad6748771663995a8163ac803b55716836ebec",
    "support_state_tag": "n09_matched_withdrawal_disrupts_support"
  },
  {
    "accepted_integration_level": "A6",
    "accepted_n10_category_level": "ALI6",
    "artifact_only": true,
    "budget_error_zero": true,
    "claim_flags_false": true,
    "expected_outcome": "composition_restoration_gated_resume",
    "integration_allowed": true,
    "integration_outcome_tag": "restoration_gated_integration_candidate",
    "matrix_row_digest": "fa7dd2ba177e34efca3558a0504743c1ade39046aedfec80deee83eea202c56a",
    "matrix_state": "explicit_restoration_recovers_support",
    "outcome_matches_expectation": true,
    "prior_disruption_history_preserved": true,
    "row_digest_valid": true,
    "runtime_state_used": false,
    "source_iteration": 11,
    "source_row_digest": "34986a49e5be51dbd83fb90c8587de37000255ab1f74c91c23ccc41bff97c1cc",
    "support_state_tag": "explicit_restoration_recovers_support"
  }
]
```

## Interpretation

Hypothesis B is not a claim that all support states are acceptable.
It is the stronger boundary result: the full composition is accepted
only in support-valid states, blocked when support is disrupted, and
resumed only when explicit restoration evidence exists.

Hypothesis B was needed because the Hypothesis A positive row could
otherwise be overread as an unconditional route-memory-support-
regulation composition. The support-state matrix tests whether the
composition remains tied to the identity/support prerequisite instead
of becoming a free-standing regulation or agency claim.

What it proves in the bounded N10 scope:

```text
support_intact_survives:
    intact support preserves the bounded composition

mild_withdrawal_survives:
    mild withdrawal preserves the bounded companion scope

n09_matched_withdrawal_disrupts_support:
    disrupted support blocks attempted A6/ALI6 with
    support_disrupted_but_integration_allowed

explicit_restoration_recovers_support:
    explicit restoration resumes A6/ALI6 as
    restoration_gated_integration_candidate
```

The result proves support sensitivity, not agency. The composition
can proceed only when support remains valid, or when explicit
restoration revalidates it. The disrupted-support block is therefore
part of the positive evidence: it shows the validator refuses to
compose regulation over a failed support identity baseline.

## Controls

```json
{
  "artifact_only_replay": {
    "control_passed": true,
    "primary_blocker": "artifact_only_replay_missing_link",
    "reason": "support-state matrix is reconstructed from exported artifacts only"
  },
  "budget_surfaces": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "source-artifact budget compatibility remains exact in every matrix state"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "Hypothesis B closeout does not emit agency, identity acceptance, A7, or fully native claims"
  },
  "disrupted_support_blocks": {
    "control_passed": true,
    "primary_blocker": "support_disrupted_but_integration_allowed",
    "reason": "disrupted support blocks the attempted A6/ALI6 full composition"
  },
  "explicit_restoration_resumes": {
    "control_passed": true,
    "primary_blocker": "restoration_required_but_missing",
    "reason": "explicit restoration resumes the full composition and preserves disruption history"
  },
  "mild_withdrawal_positive": {
    "control_passed": true,
    "primary_blocker": "mild_withdrawal_full_composition_missing",
    "reason": "mild-withdrawal companion remains valid under bounded scope"
  },
  "support_intact_positive": {
    "control_passed": true,
    "primary_blocker": "support_intact_full_composition_missing",
    "reason": "support-intact full composition remains available from Iteration 8"
  }
}
```

## Checks

```json
{
  "all_matrix_row_digests_valid": true,
  "all_required_artifacts_passed": true,
  "all_required_artifacts_present": true,
  "artifact_only_replay": true,
  "claim_flags_all_false": true,
  "closeout_digest_valid": true,
  "controls_passed": true,
  "disrupted_support_blocks_full_composition": true,
  "explicit_restoration_resumes_full_composition": true,
  "hypothesis_b_supported": true,
  "mild_withdrawal_preserves_bounded_companion": true,
  "prior_output_digests_valid": true,
  "restoration_preserves_disruption_history": true,
  "src_clean_for_iteration_12": true,
  "support_intact_preserves_composition": true
}
```

## Acceptance

```json
{
  "acceptance_statement": "Iteration 12 passes if the bounded N10 full composition is validated as support-sensitive: intact and mild-withdrawal support may preserve the composition, disrupted support blocks or downgrades it, and explicit restoration can resume it without erasing disruption history. The closeout is artifact-only, source-backed, budget-clean, and claim-clean.",
  "achieved": true,
  "status": "passed"
}
```

## Claim Boundary

All claim flags remain false. Iteration 12 does not emit agency,
semantic goal ownership, identity acceptance, ACO, biological,
personhood, unrestricted agency, A7 generalization, or fully native
agentic-like integration claims.

## Reproduction

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_12_hypothesis_b_support_state_matrix_closeout.py
```

Output digest:

```text
9d85c7dc9d77a969680a2ed0b67283f4411cf3dca715aa27191529ceeb59aa18
```
