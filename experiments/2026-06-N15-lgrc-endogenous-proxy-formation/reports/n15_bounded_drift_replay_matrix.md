# N15 Bounded Drift And Replay Matrix

Status: `passed`.

## Acceptance State

```text
accepted_bounded_drift_replay_matrix_pending_claim_boundary_classification
```

Iteration 6 tests bounded target formation under perturbation and
replay. It does not run final AP5 claim-boundary classification.

## Iteration 6 Explanation

Iteration 6 tests whether the Iteration 5 control-clean candidate is stable under replay and bounded under source-state perturbation.

**Inputs**

`Iteration 5` supplies the adversarial-control-clean AP5 candidate:

```text
all_controls_fail_closed = true
distinct_blockers_recorded = true
provisional_ap_level = AP5_candidate_control_clean_pending_bounded_drift_replay_and_claim_boundary
```

`Iteration 3` supplies the runtime state vector and generated target that I6 replays and perturbs.

`I2 replay policy` supplies the replay digest scope and perturbation defaults. I6 keeps the frozen policy and records concrete perturbation magnitudes.

**Replay Rule**

The target must reproduce exactly when serialized source-current state is unchanged:

```text
duplicate replay -> same target object
artifact-only filesystem replay -> same runtime vector and target object
snapshot/load replay -> same target object
order inversion replay -> same target object
```

**Bounded Drift Rule**

The target may change only when serialized source-current state changes, and each accepted change must remain inside the frozen drift policy:

```text
abs(perturbed_target_center - reference_target_center) <= 0.10
abs(perturbed_target_center - support_threshold) <= 0.10
```

Support, memory, regulation, and AP4 consequence-context perturbations are accepted bounded changes. Stale source state, budget-invalid input, and unbounded drift are rejected.

**What I6 Adds**

I5 showed that adversarial explanations fail closed. I6 adds a replay and drift discipline: the candidate is not just control-clean; it is deterministically reproducible from artifacts and changes only in bounded ways when source-current state is explicitly perturbed.

**End Result**

The composed I6 result is:

```text
I5 control-clean AP5 candidate
+ bounded support/memory/regulation/AP4-context perturbations
+ stale/budget/unbounded variants fail closed
+ duplicate/artifact/snapshot/order replay equality
= replay-clean AP5 candidate pending claim-boundary classification
```

**Claim Boundary**

The result supports only:

```text
AP5_candidate_replay_clean_pending_claim_boundary_classification
```

It does not support final AP5 because Iteration 7 still needs to resolve the AP5 gate, hypotheses, blocked inputs, and claim boundary.

## Result

```text
target_changes_only_for_serialized_source_current_changes = true
target_changes_match_state_change_direction = true
artifact_only_filesystem_replay_passed = true
snapshot_load_replay_passed = true
order_inversion_replay_passed = true
final_ap5_supported = false
```

## Matrix Summary

```json
{
  "accepted_record_count": 9,
  "all_records_passed": true,
  "blocked_record_count": 3,
  "blocked_record_ids": [
    "stale_state_perturbation",
    "budget_invalid_perturbation",
    "unbounded_drift_null"
  ],
  "bounded_perturbation_count": 5,
  "bounded_perturbations_change_target": true,
  "fail_closed_records_blocked": true,
  "record_count": 12,
  "unchanged_replay_count": 4,
  "unchanged_replays_preserve_target": true
}
```

## Records

| Record | Kind | Status | Target Changed | Blocker | Passed |
| --- | --- | --- | --- | --- | --- |
| `support_state_perturbation_lower` | `bounded_source_state_perturbation` | `accepted` | `True` | `None` | `True` |
| `support_state_perturbation_higher` | `bounded_source_state_perturbation` | `accepted` | `True` | `None` | `True` |
| `memory_state_perturbation` | `bounded_source_state_perturbation` | `accepted` | `True` | `None` | `True` |
| `regulation_state_perturbation` | `bounded_source_state_perturbation` | `accepted` | `True` | `None` | `True` |
| `ap4_consequence_context_perturbation` | `bounded_source_state_perturbation` | `accepted` | `True` | `None` | `True` |
| `stale_state_perturbation` | `fail_closed_perturbation` | `blocked` | `False` | `stale_source_state_blocked` | `True` |
| `budget_invalid_perturbation` | `fail_closed_perturbation` | `blocked` | `False` | `budget_exceeded` | `True` |
| `unbounded_drift_null` | `fail_closed_perturbation` | `blocked` | `False` | `unbounded_target_drift_blocked` | `True` |
| `duplicate_replay` | `unchanged_state_replay` | `accepted` | `False` | `None` | `True` |
| `artifact_only_filesystem_replay` | `unchanged_state_replay` | `accepted` | `False` | `None` | `True` |
| `snapshot_load_replay` | `unchanged_state_replay` | `accepted` | `False` | `None` | `True` |
| `order_inversion_replay` | `unchanged_state_replay` | `accepted` | `False` | `None` | `True` |

## Replay Context

```json
{
  "artifact_runtime_state_matches_i3": true,
  "order_inversion_policy": "reverse and shuffle source rows while preserving row ids and digests; canonical replay must reproduce the same target",
  "perturbed_nonzero_weight_fields": [
    "support_margin",
    "regulation_recovery_score",
    "memory_context_score",
    "ap4_consequence_context_score"
  ],
  "registry_row_digests_match": true,
  "reversed_selected_source_rows": [
    "n15_i1_row_09_n12_phase8_readiness",
    "n15_i1_row_08_n09_bounded_regulation_context",
    "n15_i1_row_07_n08_memory_context",
    "n15_i1_row_05_n14_constructed_followout",
    "n15_i1_row_04_n14_closeout_ap4",
    "n15_i1_row_03_n13_closeout_ap3",
    "n15_i1_row_02_n13_support_seeking_regulation_candidate",
    "n15_i1_row_01_n13_support_derived_target_candidate"
  ],
  "selected_source_rows": [
    "n15_i1_row_01_n13_support_derived_target_candidate",
    "n15_i1_row_02_n13_support_seeking_regulation_candidate",
    "n15_i1_row_03_n13_closeout_ap3",
    "n15_i1_row_04_n14_closeout_ap4",
    "n15_i1_row_05_n14_constructed_followout",
    "n15_i1_row_07_n08_memory_context",
    "n15_i1_row_08_n09_bounded_regulation_context",
    "n15_i1_row_09_n12_phase8_readiness"
  ],
  "unperturbed_zero_weight_fields": [
    "readiness_context_flag"
  ]
}
```

## Record Execution Scope

```json
{
  "record_id": "n15_i6_record_execution_scope_v1",
  "record_scope_records": [
    {
      "execution_scope": "target_recomputed_from_perturbed_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "support_state_perturbation_lower",
      "record_kind": "bounded_source_state_perturbation",
      "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
    },
    {
      "execution_scope": "target_recomputed_from_perturbed_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "support_state_perturbation_higher",
      "record_kind": "bounded_source_state_perturbation",
      "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
    },
    {
      "execution_scope": "target_recomputed_from_perturbed_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "memory_state_perturbation",
      "record_kind": "bounded_source_state_perturbation",
      "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
    },
    {
      "execution_scope": "target_recomputed_from_perturbed_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "regulation_state_perturbation",
      "record_kind": "bounded_source_state_perturbation",
      "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
    },
    {
      "execution_scope": "target_recomputed_from_perturbed_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "ap4_consequence_context_perturbation",
      "record_kind": "bounded_source_state_perturbation",
      "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
    },
    {
      "execution_scope": "policy_gate_blocked_before_target_derivation",
      "observed_blocker": "stale_source_state_blocked",
      "observed_status": "blocked",
      "record_id": "stale_state_perturbation",
      "record_kind": "fail_closed_perturbation",
      "scope_note": "The freshness, budget, or drift policy blocks the variant before a target can be accepted; no target rederivation is credited."
    },
    {
      "execution_scope": "policy_gate_blocked_before_target_derivation",
      "observed_blocker": "budget_exceeded",
      "observed_status": "blocked",
      "record_id": "budget_invalid_perturbation",
      "record_kind": "fail_closed_perturbation",
      "scope_note": "The freshness, budget, or drift policy blocks the variant before a target can be accepted; no target rederivation is credited."
    },
    {
      "execution_scope": "policy_gate_blocked_before_target_derivation",
      "observed_blocker": "unbounded_target_drift_blocked",
      "observed_status": "blocked",
      "record_id": "unbounded_drift_null",
      "record_kind": "fail_closed_perturbation",
      "scope_note": "The freshness, budget, or drift policy blocks the variant before a target can be accepted; no target rederivation is credited."
    },
    {
      "execution_scope": "target_recomputed_from_unchanged_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "duplicate_replay",
      "record_kind": "unchanged_state_replay",
      "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
    },
    {
      "execution_scope": "target_recomputed_from_unchanged_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "artifact_only_filesystem_replay",
      "record_kind": "unchanged_state_replay",
      "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
    },
    {
      "execution_scope": "target_recomputed_from_unchanged_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "snapshot_load_replay",
      "record_kind": "unchanged_state_replay",
      "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
    },
    {
      "execution_scope": "target_recomputed_from_unchanged_serialized_state",
      "observed_blocker": null,
      "observed_status": "accepted",
      "record_id": "order_inversion_replay",
      "record_kind": "unchanged_state_replay",
      "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
    }
  ],
  "scope_counts": {
    "policy_gate_blocked_before_target_derivation": 3,
    "target_recomputed_from_perturbed_serialized_state": 5,
    "target_recomputed_from_unchanged_serialized_state": 4
  },
  "scope_statement": "Iteration 6 recomputes accepted perturbation and replay targets. Fail-closed variants are policy-gated before target acceptance, so their evidence is a blocker record rather than a credited target rederivation."
}
```

## Idempotency Digest Plan

```json
{
  "algorithm": "sha256_canonical_json_sorted_keys",
  "digest": "95a4be05ae6751d49b87df8241b1ea92ae28610f43642e010ab60a80aad94182",
  "excluded_top_level_fields": [
    "generated_at",
    "git",
    "output_digest"
  ],
  "record_id": "n15_i6_idempotency_digest_plan_v1",
  "scope": {
    "budget_limits_config_id": "n15_budget_limits_v1",
    "claim_flags": {
      "agency_claim_allowed": false,
      "biological_behavior_claim_allowed": false,
      "fully_native_agentic_like_integration_claim_allowed": false,
      "identity_acceptance_claim_allowed": false,
      "intention_claim_allowed": false,
      "native_support_opened": false,
      "personhood_claim_allowed": false,
      "runtime_identity_acceptance_claim_allowed": false,
      "selfhood_claim_allowed": false,
      "semantic_choice_claim_allowed": false,
      "semantic_goal_ownership_claim_allowed": false,
      "semantic_goal_understanding_claim_allowed": false,
      "unrestricted_agency_claim_allowed": false
    },
    "controls": {
      "budget_surface_ambiguity_control": "passed_in_iteration_5",
      "dependency_trace_omission_control": "passed_in_iteration_5",
      "externally_injected_target_control": "passed_in_iteration_5",
      "fixture_label_proxy_control": "passed_in_iteration_5",
      "hidden_target_derivation_control": "passed_in_iteration_5",
      "identity_acceptance_relabel_control": "passed_in_iteration_5",
      "missing_source_state_control": "passed_in_iteration_5",
      "native_support_relabel_control": "passed_in_iteration_5",
      "post_hoc_proxy_formation_control": "passed_in_iteration_5",
      "semantic_goal_ownership_relabel_control": "passed_in_iteration_5",
      "stale_source_state_control": "passed_in_iteration_5",
      "unbounded_target_drift_control": "passed_in_iteration_5"
    },
    "derivation_policy_config_id": "n15_derivation_policy_v1",
    "iteration_3_output_digest": "7fcb73f4b70fdd4f4aadaa9e931040f8299669ca1598c9a1391c560637a26fbc",
    "iteration_4_output_digest": "bc97c3125ffdc83c0e97a02c7a6534fadfb95e0141f7082af3d1439c974fea59",
    "iteration_5_output_digest": "251116879e10182729ace752d2f684acf6878a2d2d3db74c7f39bef1a7a76a7f",
    "matrix_records": [
      {
        "expected_status": "accepted",
        "input_change": "support_margin - 0.05",
        "observed_blocker": null,
        "observed_runtime_state_digest": "710dc0840e19ea6abf804f09a8ad219b03c3c4c91ed10dc87044d0e4ba8a4e5e",
        "observed_status": "accepted",
        "observed_target_center": 0.885594607287,
        "observed_target_digest": "1b7bf62b620adab6e6a2e51232e9804199c2362a90da20586beba523ba47c5b9",
        "passed": true,
        "record_id": "support_state_perturbation_lower",
        "record_kind": "bounded_source_state_perturbation",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": true,
        "target_center_delta": 0.002,
        "target_changed": true,
        "within_bounded_drift_policy": true
      },
      {
        "expected_status": "accepted",
        "input_change": "support_margin + 0.05",
        "observed_blocker": null,
        "observed_runtime_state_digest": "7f4b2701b32497a27dde8d655919b264c05360e148d7ec830d7a93eba3d5db38",
        "observed_status": "accepted",
        "observed_target_center": 0.889594607287,
        "observed_target_digest": "9eb976eac185ce91d25d2e9c3c0cc6f3acdcbd75c41916631aebd9120a06679a",
        "passed": true,
        "record_id": "support_state_perturbation_higher",
        "record_kind": "bounded_source_state_perturbation",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": true,
        "target_center_delta": 0.002,
        "target_changed": true,
        "within_bounded_drift_policy": true
      },
      {
        "expected_status": "accepted",
        "input_change": "memory_context_score + 0.10",
        "observed_blocker": null,
        "observed_runtime_state_digest": "701854f30a4b52574a7f4166b1cc29311cee00c72a437f17acf21af9e84da273",
        "observed_status": "accepted",
        "observed_target_center": 0.889594607287,
        "observed_target_digest": "ebd7632bac9f39611b072c5f65c20af1d3b1cfa3c236d3d20ad88d6474bb1488",
        "passed": true,
        "record_id": "memory_state_perturbation",
        "record_kind": "bounded_source_state_perturbation",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": true,
        "target_center_delta": 0.002,
        "target_changed": true,
        "within_bounded_drift_policy": true
      },
      {
        "expected_status": "accepted",
        "input_change": "regulation_recovery_score -> 0.5",
        "observed_blocker": null,
        "observed_runtime_state_digest": "5fc6e16dc169aea21ac1f5f835369fd9f3b72ba93a093ba2a5a81d2f99d3b910",
        "observed_status": "accepted",
        "observed_target_center": 0.875094607287,
        "observed_target_digest": "1f9c68eccfa6713af4a84143c847dab72dec6dc2bfc794382e4370b84218f36c",
        "passed": true,
        "record_id": "regulation_state_perturbation",
        "record_kind": "bounded_source_state_perturbation",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": true,
        "target_center_delta": 0.0125,
        "target_changed": true,
        "within_bounded_drift_policy": true
      },
      {
        "expected_status": "accepted",
        "input_change": "ap4_consequence_context_score -> 0.0",
        "observed_blocker": null,
        "observed_runtime_state_digest": "c5ed4b336f67c2757811b05583b3e76070c09cdaf85fb2eceb27e240abe2ab25",
        "observed_status": "accepted",
        "observed_target_center": 0.872594607287,
        "observed_target_digest": "ac2aec5b5039687dc103c0796ed7d7f43b92e152416e095c30cfdccea267142a",
        "passed": true,
        "record_id": "ap4_consequence_context_perturbation",
        "record_kind": "bounded_source_state_perturbation",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": true,
        "target_center_delta": 0.015,
        "target_changed": true,
        "within_bounded_drift_policy": true
      },
      {
        "evidence": {
          "reference_source_current": true,
          "replay_policy": "source_current = false or outside freshness window",
          "variant_source_current": false
        },
        "expected_status": "blocked",
        "input_change": "source_current -> false",
        "observed_blocker": "stale_source_state_blocked",
        "observed_status": "blocked",
        "passed": true,
        "record_id": "stale_state_perturbation",
        "record_kind": "fail_closed_perturbation",
        "serialized_state_changed": true,
        "target_changed": false,
        "within_bounded_drift_policy": false
      },
      {
        "evidence": {
          "limit": 262144,
          "replay_policy": "exceed one frozen budget limit before target use",
          "variant_value": 262145
        },
        "expected_status": "blocked",
        "input_change": "canonical_json_input_bytes exceeds frozen limit",
        "observed_blocker": "budget_exceeded",
        "observed_status": "blocked",
        "passed": true,
        "record_id": "budget_invalid_perturbation",
        "record_kind": "fail_closed_perturbation",
        "serialized_state_changed": true,
        "target_changed": false,
        "within_bounded_drift_policy": false
      },
      {
        "evidence": {
          "allowed_max_update": 0.1,
          "support_threshold": 0.85,
          "variant_target_center": 1.0
        },
        "expected_status": "blocked",
        "input_change": "target_center exceeds support_threshold drift bound",
        "observed_blocker": "unbounded_target_drift_blocked",
        "observed_status": "blocked",
        "passed": true,
        "record_id": "unbounded_drift_null",
        "record_kind": "fail_closed_perturbation",
        "serialized_state_changed": true,
        "target_changed": false,
        "within_bounded_drift_policy": false
      },
      {
        "expected_status": "accepted",
        "input_change": "duplicate serialized runtime state vector",
        "observed_blocker": null,
        "observed_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "observed_status": "accepted",
        "observed_target_center": 0.887594607287,
        "observed_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "passed": true,
        "record_id": "duplicate_replay",
        "record_kind": "unchanged_state_replay",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": false,
        "target_center_delta": 0.0,
        "target_changed": false,
        "within_bounded_drift_policy": true
      },
      {
        "expected_status": "accepted",
        "input_change": "rebuild runtime vector from pinned source artifacts",
        "observed_blocker": null,
        "observed_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "observed_status": "accepted",
        "observed_target_center": 0.887594607287,
        "observed_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "passed": true,
        "record_id": "artifact_only_filesystem_replay",
        "record_kind": "unchanged_state_replay",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": false,
        "target_center_delta": 0.0,
        "target_changed": false,
        "within_bounded_drift_policy": true
      },
      {
        "expected_status": "accepted",
        "input_change": "canonical JSON snapshot/load round trip",
        "observed_blocker": null,
        "observed_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "observed_status": "accepted",
        "observed_target_center": 0.887594607287,
        "observed_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "passed": true,
        "record_id": "snapshot_load_replay",
        "record_kind": "unchanged_state_replay",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": false,
        "target_center_delta": 0.0,
        "target_changed": false,
        "within_bounded_drift_policy": true
      },
      {
        "expected_status": "accepted",
        "input_change": "reverse selected source row order while preserving row ids and digests",
        "observed_blocker": null,
        "observed_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "observed_status": "accepted",
        "observed_target_center": 0.887594607287,
        "observed_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "passed": true,
        "record_id": "order_inversion_replay",
        "record_kind": "unchanged_state_replay",
        "reference_runtime_state_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
        "reference_target_center": 0.887594607287,
        "reference_target_digest": "a624441448e30eb3e5867a152575f820c92438d3543625df079f8abb1e012117",
        "replay_policy_id": "n15_replay_digest_policy_v1",
        "serialized_state_changed": false,
        "target_center_delta": 0.0,
        "target_changed": false,
        "within_bounded_drift_policy": true
      }
    ],
    "matrix_summary": {
      "accepted_record_count": 9,
      "all_records_passed": true,
      "blocked_record_count": 3,
      "blocked_record_ids": [
        "stale_state_perturbation",
        "budget_invalid_perturbation",
        "unbounded_drift_null"
      ],
      "bounded_perturbation_count": 5,
      "bounded_perturbations_change_target": true,
      "fail_closed_records_blocked": true,
      "record_count": 12,
      "unchanged_replay_count": 4,
      "unchanged_replays_preserve_target": true
    },
    "record_execution_scope": {
      "record_id": "n15_i6_record_execution_scope_v1",
      "record_scope_records": [
        {
          "execution_scope": "target_recomputed_from_perturbed_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "support_state_perturbation_lower",
          "record_kind": "bounded_source_state_perturbation",
          "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
        },
        {
          "execution_scope": "target_recomputed_from_perturbed_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "support_state_perturbation_higher",
          "record_kind": "bounded_source_state_perturbation",
          "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
        },
        {
          "execution_scope": "target_recomputed_from_perturbed_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "memory_state_perturbation",
          "record_kind": "bounded_source_state_perturbation",
          "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
        },
        {
          "execution_scope": "target_recomputed_from_perturbed_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "regulation_state_perturbation",
          "record_kind": "bounded_source_state_perturbation",
          "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
        },
        {
          "execution_scope": "target_recomputed_from_perturbed_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "ap4_consequence_context_perturbation",
          "record_kind": "bounded_source_state_perturbation",
          "scope_note": "The runtime state vector is changed, the target condition is rederived, and the target delta must remain within bounded drift."
        },
        {
          "execution_scope": "policy_gate_blocked_before_target_derivation",
          "observed_blocker": "stale_source_state_blocked",
          "observed_status": "blocked",
          "record_id": "stale_state_perturbation",
          "record_kind": "fail_closed_perturbation",
          "scope_note": "The freshness, budget, or drift policy blocks the variant before a target can be accepted; no target rederivation is credited."
        },
        {
          "execution_scope": "policy_gate_blocked_before_target_derivation",
          "observed_blocker": "budget_exceeded",
          "observed_status": "blocked",
          "record_id": "budget_invalid_perturbation",
          "record_kind": "fail_closed_perturbation",
          "scope_note": "The freshness, budget, or drift policy blocks the variant before a target can be accepted; no target rederivation is credited."
        },
        {
          "execution_scope": "policy_gate_blocked_before_target_derivation",
          "observed_blocker": "unbounded_target_drift_blocked",
          "observed_status": "blocked",
          "record_id": "unbounded_drift_null",
          "record_kind": "fail_closed_perturbation",
          "scope_note": "The freshness, budget, or drift policy blocks the variant before a target can be accepted; no target rederivation is credited."
        },
        {
          "execution_scope": "target_recomputed_from_unchanged_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "duplicate_replay",
          "record_kind": "unchanged_state_replay",
          "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
        },
        {
          "execution_scope": "target_recomputed_from_unchanged_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "artifact_only_filesystem_replay",
          "record_kind": "unchanged_state_replay",
          "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
        },
        {
          "execution_scope": "target_recomputed_from_unchanged_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "snapshot_load_replay",
          "record_kind": "unchanged_state_replay",
          "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
        },
        {
          "execution_scope": "target_recomputed_from_unchanged_serialized_state",
          "observed_blocker": null,
          "observed_status": "accepted",
          "record_id": "order_inversion_replay",
          "record_kind": "unchanged_state_replay",
          "scope_note": "The runtime state vector is replayed without semantic changes, and the target condition must reproduce exactly."
        }
      ],
      "scope_counts": {
        "policy_gate_blocked_before_target_derivation": 3,
        "target_recomputed_from_perturbed_serialized_state": 5,
        "target_recomputed_from_unchanged_serialized_state": 4
      },
      "scope_statement": "Iteration 6 recomputes accepted perturbation and replay targets. Fail-closed variants are policy-gated before target acceptance, so their evidence is a blocker record rather than a credited target rederivation."
    },
    "replay_context": {
      "artifact_runtime_state_matches_i3": true,
      "order_inversion_policy": "reverse and shuffle source rows while preserving row ids and digests; canonical replay must reproduce the same target",
      "perturbed_nonzero_weight_fields": [
        "support_margin",
        "regulation_recovery_score",
        "memory_context_score",
        "ap4_consequence_context_score"
      ],
      "registry_row_digests_match": true,
      "reversed_selected_source_rows": [
        "n15_i1_row_09_n12_phase8_readiness",
        "n15_i1_row_08_n09_bounded_regulation_context",
        "n15_i1_row_07_n08_memory_context",
        "n15_i1_row_05_n14_constructed_followout",
        "n15_i1_row_04_n14_closeout_ap4",
        "n15_i1_row_03_n13_closeout_ap3",
        "n15_i1_row_02_n13_support_seeking_regulation_candidate",
        "n15_i1_row_01_n13_support_derived_target_candidate"
      ],
      "selected_source_rows": [
        "n15_i1_row_01_n13_support_derived_target_candidate",
        "n15_i1_row_02_n13_support_seeking_regulation_candidate",
        "n15_i1_row_03_n13_closeout_ap3",
        "n15_i1_row_04_n14_closeout_ap4",
        "n15_i1_row_05_n14_constructed_followout",
        "n15_i1_row_07_n08_memory_context",
        "n15_i1_row_08_n09_bounded_regulation_context",
        "n15_i1_row_09_n12_phase8_readiness"
      ],
      "unperturbed_zero_weight_fields": [
        "readiness_context_flag"
      ]
    },
    "replay_policy_config_id": "n15_replay_policy_v1",
    "schema_output_digest": "3894554145fe84a7f594983ead562442cda686fd53d6b240164626b578f2ee67",
    "source_artifacts": {
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_budget_limits_v1.json": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_budget_limits_v1.json",
        "sha256": "8b1314a9d229d70cd48e12bfc5fa4aa978877f78a4880db9e8a3faa867fbe62e"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_derivation_policy_v1.json": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_derivation_policy_v1.json",
        "sha256": "9de32ee9717fd813e2a20ded18cde3cc384307c92586212a07f7105d72041c7b"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_replay_policy_v1.json": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_replay_policy_v1.json",
        "sha256": "356589601130ec5a9edacf3c900b57758768cc6fa73b9e1e09880a2fbab7c7f3"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_source_registry.json": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/configs/n15_source_registry.json",
        "sha256": "361457bb559a4e4255824ee72415ae9c77b661e1ec95f657ea3d65bff4a36e71"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_external_proxy_contrast_matrix.json": {
        "acceptance_state": "accepted_external_proxy_contrast_matrix_pending_adversarial_controls_replay_and_claim_boundary",
        "output_digest": "bc97c3125ffdc83c0e97a02c7a6534fadfb95e0141f7082af3d1439c974fea59",
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_external_proxy_contrast_matrix.json",
        "sha256": "f7201b82f0071e26f05b62111d88396072d669d815153971f93f967e503c0ee8",
        "status": "passed"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_proxy_control_matrix.json": {
        "acceptance_state": "accepted_proxy_control_matrix_pending_bounded_drift_replay_and_claim_boundary",
        "output_digest": "251116879e10182729ace752d2f684acf6878a2d2d3db74c7f39bef1a7a76a7f",
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_proxy_control_matrix.json",
        "sha256": "35edc1ac9c475104d7c2b76e4278c108b2050dac65c06d0024141fc4b9ceadcf",
        "status": "passed"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_proxy_formation_schema_v1.json": {
        "acceptance_state": "accepted_schema_freeze_no_row_validation",
        "output_digest": "3894554145fe84a7f594983ead562442cda686fd53d6b240164626b578f2ee67",
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_proxy_formation_schema_v1.json",
        "sha256": "aa276922df3c39c30bcf09500b7eccfe96468fd681f3992a328a504f0d8c9d5b",
        "status": "passed"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_runtime_derived_target_candidate.json": {
        "acceptance_state": "accepted_runtime_derived_target_candidate_with_bridge_pending_controls",
        "output_digest": "7fcb73f4b70fdd4f4aadaa9e931040f8299669ca1598c9a1391c560637a26fbc",
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/outputs/n15_runtime_derived_target_candidate.json",
        "sha256": "30c834b47a7decf2bb32f3dabb8dcb436b2b7876be5b0e9c79fe76b7de010873",
        "status": "passed"
      }
    },
    "source_registry_config_id": "n15_source_registry",
    "source_reports": {
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_external_proxy_contrast_matrix.md": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_external_proxy_contrast_matrix.md",
        "sha256": "3c679397b75bd033df352995265c8cceee71612944729a6991805801509aad8c"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_proxy_control_matrix.md": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_proxy_control_matrix.md",
        "sha256": "e25c2b6b50bd6c50934963de8d2c93fc4045ac632f713f778f8c1733d006fa69"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_proxy_formation_schema_v1.md": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_proxy_formation_schema_v1.md",
        "sha256": "040582e46c1542a30c28aa4cda661fc5752e2529d93a0c14fc2f2c3b5e26eba6"
      },
      "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_runtime_derived_target_candidate.md": {
        "path": "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_runtime_derived_target_candidate.md",
        "sha256": "c54c784652e004a23f1283d8e716f370993636b72e4d9ade46f2d9d7c071277c"
      }
    }
  }
}
```

## Top-Level Output Fields

```json
[
  "experiment",
  "iteration",
  "artifact_id",
  "purpose",
  "schema_version",
  "generated_at",
  "command",
  "status",
  "acceptance_state",
  "source_artifacts",
  "source_reports",
  "rows",
  "controls",
  "checks",
  "claim_flags",
  "errors",
  "iteration_result",
  "matrix_records",
  "bounded_drift_replay_matrix",
  "matrix_summary",
  "replay_context",
  "record_execution_scope",
  "idempotency_digest_plan",
  "iteration_6_explanation",
  "iteration_6_top_level_output_fields",
  "interpretation_record",
  "git",
  "output_digest"
]
```

## Post-Review Gap Closure

```text
closed: iteration_6_top_level_output_fields declares every I6 top-level key.
closed: idempotency_digest_plan records the I6 replay/idempotency source scope.
closed: ap4_consequence_context_perturbation covers the remaining nonzero composition-weight axis.
closed: target_changes_match_state_change_direction splits the previous target-change implication into explicit bidirectional checks.
closed: record_execution_scope distinguishes recomputed perturbation/replay rows from policy-gated fail-closed rows.
closed: matrix_records, matrix_summary, and replay_context duplication is retained for access compatibility and guarded by identity checks.
not_gap: readiness_context_flag remains unperturbed because its frozen composition weight is 0.0.
not_gap: symmetric perturbation directions are not required by the frozen I6 replay policy; all nonzero composition-weight axes now have bounded source-current perturbation coverage.
not_gap: fail-closed records are policy-gated blockers before target acceptance, not credited target rederivations.
```

## Interpretation Record

```json
{
  "plain_language_interpretation": "Bounded support, memory, and regulation perturbations change the generated target within the frozen drift policy. Duplicate, artifact-only filesystem, snapshot/load, and order-inversion replays reproduce the target. Stale source, budget-invalid, and unbounded-drift variants fail closed.",
  "record_id": "n15_i6_interpretation_bounded_drift_replay_v1",
  "remaining_required_work": [
    "iteration_7_claim_boundary_and_ap5_classification",
    "iteration_8_closeout_and_handoff"
  ],
  "supported_interpretation": "The N15 AP5 candidate is replay-clean and bounded-drift clean at artifact level pending final claim-boundary classification.",
  "unsupported_interpretations": [
    "final AP5 support",
    "semantic goal ownership",
    "identity acceptance",
    "intention",
    "semantic choice",
    "agency",
    "native support",
    "fully native integration"
  ]
}
```

## Checks

```json
{
  "absolute_path_absence": true,
  "ap4_consequence_context_perturbation_run": true,
  "artifact_only_filesystem_replay_passed": true,
  "artifact_runtime_state_matches_i3": true,
  "bounded_perturbations_always_change_target": true,
  "bounded_perturbations_change_target_within_drift": true,
  "budget_invalid_perturbation_blocked": true,
  "budget_limits_loaded": true,
  "claim_flags_forced_false": true,
  "control_outcomes_present": true,
  "derivation_policy_loaded": true,
  "digest_reproducibility": true,
  "duplicate_replay_passed": true,
  "fail_closed_records_blocked": true,
  "final_ap5_not_supported": true,
  "fully_native_integration_not_opened": true,
  "idempotency_digest_plan_reproducible": true,
  "iteration_3_source_passed": true,
  "iteration_4_source_passed": true,
  "iteration_5_acceptance_state_valid": true,
  "iteration_5_source_passed": true,
  "iteration_6_explanation_recorded": true,
  "iteration_6_top_level_output_fields_match": true,
  "iteration_6_top_level_output_shape_declared": true,
  "matrix_records_match_bounded_drift_replay_matrix_records": true,
  "matrix_summary_match_bounded_drift_replay_matrix_summary": true,
  "memory_state_perturbation_run": true,
  "native_support_not_opened": true,
  "nonzero_composition_weight_fields_perturbed": true,
  "order_inversion_replay_passed": true,
  "phase8_opened_false": true,
  "policy_gate_blocks_documented": true,
  "readiness_zero_weight_unperturbed_by_design": true,
  "record_execution_scope_recorded": true,
  "registry_row_digests_match": true,
  "regulation_state_perturbation_run": true,
  "replay_context_match_bounded_drift_replay_matrix_context": true,
  "replay_policy_loaded": true,
  "required_fields_present": true,
  "schema_source_passed": true,
  "snapshot_load_replay_passed": true,
  "source_digest_presence": true,
  "source_registry_loaded": true,
  "src_diff_empty": true,
  "stale_state_perturbation_blocked": true,
  "support_state_perturbations_run": true,
  "target_changes_match_state_change_direction": true,
  "target_changes_only_for_serialized_source_current_changes": true,
  "unbounded_drift_null_blocked": true,
  "unchanged_replays_never_change_target": true,
  "unchanged_replays_preserve_target": true
}
```

## Claim Boundary

```text
replay-clean candidate != final AP5 support
bounded target drift != semantic goal ownership
artifact replay equality != native support
N15 Iteration 6 != agency, intention, identity acceptance, native support, or fully native integration
```

## Output Digest

```text
b73f05459697a18117ab5db0ef3f3bf5dff41c78a4dbacc40af11676a8b0532a
```
