# N15 External Proxy Contrast Matrix

Status: `passed`.

## Acceptance State

```text
accepted_external_proxy_contrast_matrix_pending_adversarial_controls_replay_and_claim_boundary
```

Iteration 4 contrasts the Iteration 3 runtime-derived target candidate
against declared, externally injected, hidden-derivation, and post-hoc
proxy explanations. It does not run the full Iteration 5 adversarial
control matrix or assign final AP5.

## Iteration 4 Explanation

Iteration 4 does not try to prove final AP5 by adding a new mechanism. It asks whether the Iteration 3 bridge can be distinguished from easier explanations: a declared target fixture, an externally injected target, hidden target derivation, or post-hoc proxy formation.

**Inputs**

`Iteration 3` supplies the positive reference:

```text
target_band = [0.817594607287, 0.957594607287]
bounded-response support = 0.85
no-response support = 0.729865182184
selected_bridge_candidate = n13_bounded_support_response
```

This is the candidate I4 protects. It is already generated before bridge ranking from the serialized runtime state vector, and it already carries a dependency trace and a before-use budget-validity record.

`I2 control variants` supply the blocker labels:

```text
fixture_label_proxy_blocked
externally_injected_target_blocked
hidden_target_derivation_blocked
post_hoc_proxy_formation_blocked
```

`I2 derivation policy` supplies the replay rule. I4 rederives the target from the I3 runtime state vector and requires the replayed target object to match the recorded target object.

`I2 budget limits` supply the before-use budget check. I4 confirms the I3 budget record remains valid before target consumption, but leaves the full budget-ambiguity adversarial matrix to Iteration 5.

**Contrast Rule**

The positive reference is accepted only under this provenance and timing surface:

```text
target_source = source_current_runtime_state_vector
external_target_input_present = false
dependency_trace_present = true
target_condition_consumed_before_rank = true
budget_checked_before_target_use = true
```

A contrast variant is blocked when it can imitate the response behavior but fails the provenance or timing requirements.

**What The Contrast Adds**

I4 adds a distinction that I3 did not yet establish. I3 showed that a generated target can rank a bounded regulation response. I4 shows that the same selected response is not enough.

The strongest contrast is the same-band declared fixture:

```text
same target band
same selected bounded response
same post-response support = 0.85
blocked because target_source != source_current_runtime_state_vector
```

So the candidate is not accepted merely because it chooses the bounded response. It is accepted only because the target was derived before use from source-current state, with trace and budget records intact.

I4 also blocks externally injected targets, hidden derivations, and post-hoc target formation after bridge ranking.

**End Result**

The composed I4 result is:

```text
I3 runtime-derived target candidate
+ same-band declared fixture contrast
+ external injection block
+ hidden derivation block
+ post-hoc formation block
+ source-current target replay
+ before-use budget check
= contrast-clean AP5 candidate pending I5-I7
```

**Claim Boundary**

The result supports only:

```text
AP5_candidate_contrast_clean_pending_adversarial_controls_replay_and_claim_boundary
```

It does not yet support final AP5 because Iteration 5 still needs the full adversarial control matrix, Iteration 6 still needs bounded drift and artifact replay, and Iteration 7 still needs claim-boundary classification.

## Result

```text
declared_target_fixture_distinguished = true
externally_injected_target_blocked = true
hidden_target_derivation_blocked = true
post_hoc_proxy_formation_blocked = true
source_current_runtime_derivation_replays = true
budget_validity_checked_before_target_use = true
candidate_distinguishable_from_declared_proxy_regulation = true
final_ap5_supported = false
```

## Contrast Records

| Contrast | Status | Blocker | Same Selected Response | Passed |
| --- | --- | --- | --- | --- |
| `runtime_derived_candidate_positive_reference` | `accepted` | `None` | `True` | `True` |
| `declared_target_fixture_same_band_contrast` | `blocked` | `fixture_label_proxy_blocked` | `True` | `True` |
| `externally_injected_target_variant` | `blocked` | `externally_injected_target_blocked` | `True` | `True` |
| `hidden_target_derivation_variant` | `blocked` | `hidden_target_derivation_blocked` | `True` | `True` |
| `post_hoc_proxy_formation_variant` | `blocked` | `post_hoc_proxy_formation_blocked` | `True` | `True` |

## Distinction Record

```json
{
  "behavioral_equivalence_not_sufficient": true,
  "candidate_distinguishable_from_declared_proxy_regulation": true,
  "declared_fixture_same_behavior_blocked": true,
  "declared_proxy_regulation_baseline": {
    "role_in_n15_i3": "bounded regulation context only; not target derivation and not declared AP5 proxy source",
    "source_artifact": "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_9_gpr6_closeout.json",
    "source_experiment": "N09",
    "source_sha256": "f2023e4b3aa456ac7aa301494b25e4a190226260fb90adc1c292182dccee3b68"
  },
  "distinction_basis": [
    "target condition generated from source-current runtime_state_vector",
    "dependency_trace records source rows and transforms",
    "target condition generated before bridge ranking",
    "external_target_input_absent is true for the I3 candidate",
    "declared or injected target variants are blocked even when ranking matches",
    "post-hoc target formation after candidate selection is blocked"
  ],
  "externally_injected_target_blocked": true,
  "hidden_target_derivation_blocked": true,
  "post_hoc_proxy_formation_blocked": true,
  "record_id": "n15_i4_distinguish_runtime_target_from_declared_proxy_v1"
}
```

## Source-Current Replay

```json
{
  "claim_boundary": "local source-current replay only; artifact-only filesystem replay, snapshot/load, and order-inversion replay remain Iteration 6 work",
  "full_object_match": true,
  "recorded_target_condition_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
  "replay_id": "n15_i4_source_current_runtime_derivation_replay_v1",
  "replayed_target_condition_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117"
}
```

## Control Execution Scope

```json
{
  "deferred_full_controls": [
    "semantic_goal_ownership_relabel_control",
    "unbounded_target_drift_control",
    "budget_surface_ambiguity_control",
    "identity_acceptance_relabel_control",
    "native_support_relabel_control",
    "stale_source_state_control",
    "missing_source_state_control",
    "dependency_trace_omission_control"
  ],
  "executed_in_iteration_4": [
    "externally_injected_target_control",
    "fixture_label_proxy_control",
    "hidden_target_derivation_control",
    "post_hoc_proxy_formation_control"
  ],
  "partial_checks_only": [
    "budget_surface_ambiguity_control",
    "dependency_trace_omission_control",
    "stale_source_state_control"
  ],
  "reason": "Iteration 4 contrasts the candidate against external or declared proxy explanations; Iteration 5 remains the full adversarial control matrix.",
  "record_id": "n15_i4_control_execution_scope_v1"
}
```

## Checks

```json
{
  "absolute_path_absence": true,
  "budget_limits_loaded": true,
  "budget_validity_checked_before_target_use": true,
  "candidate_distinguishable_from_declared_proxy_regulation": true,
  "claim_flags_forced_false": true,
  "control_outcomes_present": true,
  "control_variants_loaded": true,
  "declared_target_fixture_distinguished": true,
  "derivation_policy_loaded": true,
  "digest_reproducibility": true,
  "executed_i4_controls_blocked": true,
  "executed_i4_controls_present": true,
  "externally_injected_target_blocked": true,
  "final_ap5_not_supported": true,
  "fully_native_integration_not_opened": true,
  "hidden_target_derivation_blocked": true,
  "i3_declared_proxy_absent": true,
  "i3_external_target_absent": true,
  "i3_target_consumed_before_rank": true,
  "iteration_3_acceptance_state_valid": true,
  "iteration_3_source_passed": true,
  "iteration_4_explanation_recorded": true,
  "native_support_not_opened": true,
  "phase8_opened_false": true,
  "post_hoc_proxy_formation_blocked": true,
  "required_top_level_fields_present": true,
  "schema_source_passed": true,
  "source_current_runtime_derivation_replays": true,
  "source_digest_presence": true,
  "src_diff_empty": true
}
```

## Claim Boundary

```text
external proxy contrast passed != final AP5 support
same-band fixture blocked != semantic goal ownership
source-current replay != artifact-only replay completion
budget checked before use != full budget ambiguity control completion
N15 Iteration 4 != agency, intention, identity acceptance, native support, or fully native integration
```

## Output Digest

```text
bc97c3125ffdc83c0e97a02c7a6534fadfb95e0141f7082af3d1439c974fea59
```
