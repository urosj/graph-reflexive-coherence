# N15 Runtime-Derived Target Candidate

Status: `passed`.

## Acceptance State

```text
accepted_runtime_derived_target_candidate_with_bridge_pending_controls
```

Iteration 3 generates a provisional runtime-derived target candidate
using the stronger old-best-claims path. It also adds a bridge probe
for the gap between `target condition exists` and `target condition
functions as an AP5-relevant proxy formation input`.

It does not run the external proxy contrast matrix, adversarial
controls, bounded drift replay, or final claim-boundary classification.
Final `AP5` remains unsupported.

## Iteration 3 Explanation

Iteration 3 composes a provisional AP5 candidate by taking the strongest closed claims from prior experiments and making them do one specific job: generate a target condition before use, then show that target can function as an input to bounded regulation.

The composition is not "N13 + N14 = AP5". It is more constrained than that.

**Inputs**

`N13 AP3` supplies the support/regulation axis.

The selected lane is the disrupted support case:

```text
support_margin = -0.120134817816
current_support_retention = 0.729865182184
support_threshold = 0.85
scheduled bounded response = 0.120134817816
```

This is the concrete pressure that makes target formation meaningful. There is support below threshold, and N13 has a bounded response candidate that can recover it. N13 contributes regulation, not selfhood, agency, or goal ownership.

`N14 AP4` supplies consequence-sensitive selection context.

N14's closed claim is that route/consequence evidence can guide selection at artifact level. In I3, this contributes:

```text
ap4_consequence_context_score = 1.0
selected_route_context = route_b
```

It gives the composition a consequence-sensitive axis, but not intention or semantic choice.

`N08` supplies memory context.

N08 contributes the route memory trend where route_b is reinforced:

```text
route_b memory delta = 0.12
memory_context_score = 0.12
```

This makes the generated target depend partly on prior route-memory context, not just instantaneous support error.

`N09` supplies bounded regulation context.

N09 contributes that perturbation recovery is in band:

```text
regulation_recovery_score = 1.0
```

This says the system has artifact-level bounded regulation context. It does not make the target native or goal-owned.

`N12` supplies readiness-only context.

N12 contributes:

```text
readiness_context_flag = 1.0
```

But I2 froze its weight at `0.0`, so it validates context without changing the target value. That is deliberate: N12 readiness must not become native support by relabeling.

**Composition Rule**

I3 uses the I2 frozen derivation policy:

```text
weighted_sum =
  0.40 * support_margin
+ 0.25 * regulation_recovery_score
+ 0.20 * memory_context_score
+ 0.15 * ap4_consequence_context_score
+ 0.00 * readiness_context_flag
```

With the I3 values:

```text
weighted_sum = 0.375946072874
```

Then:

```text
target_center =
  support_threshold + 0.10 * weighted_sum

target_center = 0.887594607287
target_tolerance = 0.07
target_band = [0.817594607287, 0.957594607287]
```

So the target is not externally declared. It is generated from serialized source-current state under a frozen policy.

**What The Composed Result Brings**

The composed result brings something stronger than historic target existence.

Direct historic evidence from N13 only showed:

```text
target condition exists at AP2 support-derived target scope
```

Iteration 3 adds:

```text
a target condition is generated before use from old-best runtime-visible inputs
```

Then the bridge probe tests whether the generated target functions as an input:

```text
no-response support = 0.729865182184
bounded-response support = 0.85
generated target band = [0.817594607287, 0.957594607287]
```

Result:

```text
no-response: outside band, rejected
bounded N13 response: inside band, selected
```

That is the important bridge. The generated target is not just written down; it changes the ranking of candidate regulation behavior.

**Claim Boundary**

The composed result supports only:

```text
provisional AP5 candidate pending contrast, controls, replay, and claim classification
```

It does not yet support final AP5 because I4-I7 still need to show:

```text
not externally injected
not hidden target derivation
not post-hoc proxy formation
negative controls fail closed
bounded drift and replay hold
claim boundary remains clean
```

So the end result is: a constructed, traceable, runtime-derived target candidate that can function as a bounded regulation input, but still not final AP5.

## I3 Top-Level Contract

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
  "direct_historic_gap_record",
  "iteration_3_explanation",
  "iteration_3_top_level_output_fields",
  "control_value_convention",
  "replay_digest_inputs_design_note",
  "runtime_state_vector",
  "target_condition",
  "bridge_probe",
  "dependency_trace",
  "budget_cost_surface",
  "budget_validity",
  "replay_digest_policy",
  "interpretation_record",
  "git",
  "output_digest"
]
```

## Control Value Convention

```json
{
  "reason": "Iteration 3 builds the bridge candidate only; Iterations 4 and 5 execute the contrast and adversarial control matrices.",
  "record_id": "n15_i3_control_value_convention_v1",
  "row_level_control_fields": "requirement status plus planned execution iteration where the Iteration 2 row schema has a corresponding control field",
  "top_level_controls": "requirement-only status for every control required before AP5"
}
```

## Replay Digest Design Note

```json
{
  "design_choice": "replay_digest_inputs intentionally embeds full runtime_state_vector and target_condition objects, while dependency_trace and bridge_probe are represented by canonical digests",
  "iteration_6_replay_requirement": "rederive full runtime_state_vector and target_condition objects from source-current rows and compare objects before accepting digest agreement",
  "not_gap": "full object copies are the replay surface, not hidden target derivation or post-hoc proxy formation",
  "record_id": "n15_i3_replay_digest_inputs_design_note_v1"
}
```

## Review Gap Closure

```text
closed: iteration_3_top_level_output_fields declares every I3 top-level key.
closed: idempotency_digest_plan scope matches replay_digest_inputs including claim_flags.
closed: n14_constructed_followout is included in candidate_path_used.
closed: dependency_trace covers context rows and bounded bridge response fields.
closed: I2 validator required check names are emitted in I3 checks.
closed: control value convention and replay digest design note are recorded.
not_gap: full runtime_state_vector and target_condition objects in replay_digest_inputs are intentional; Iteration 6 must rederive and compare the full objects.
```

## Direct Historic Gap

```json
{
  "candidate_path_used": [
    "n15_i1_row_02_n13_support_seeking_regulation_candidate",
    "n15_i1_row_03_n13_closeout_ap3",
    "n15_i1_row_04_n14_closeout_ap4",
    "n15_i1_row_05_n14_constructed_followout",
    "n15_i1_row_07_n08_memory_context",
    "n15_i1_row_08_n09_bounded_regulation_context",
    "n15_i1_row_09_n12_phase8_readiness"
  ],
  "direct_historic_source_row_id": "n15_i1_row_01_n13_support_derived_target_candidate",
  "direct_historic_support_status": "target_condition_exists_at_N13_AP2_scope_only",
  "gap": "target_condition_exists != AP5_relevant_proxy_formation_input",
  "reason_not_promoted": "N13 direct target evidence lacks N15 pre-use derivation from the old-best source vector plus bridge consumption by rank/regulation",
  "record_id": "n15_i3_direct_historic_gap_record_v1"
}
```

## Runtime State Vector

```json
{
  "ap4_consequence_context_score": 1.0,
  "constructed_followout_context": {
    "constructed_route_conditioned_regulation_followout_supported": true,
    "constructed_route_conditioned_support_followout_supported": true,
    "observed_upstream_route_conditioned_support_regulation_supported": false,
    "scope_caveat": "support/regulation positivity is constructed N14 followout evidence; it is not upstream N09/N13 observed route-conditioned evidence and it is not native support"
  },
  "current_support_retention": 0.729865182184,
  "memory_context_score": 0.12,
  "n13_ap3_closed_claim_ceiling": {
    "agency_claim_opened": false,
    "final_claim_ceiling": "artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation",
    "final_supported_ap_level": "AP3",
    "native_support_opened": false,
    "semantic_goal_ownership_opened": false
  },
  "n13_bounded_response": {
    "bounded_window_count": 4,
    "budget_debit_amount": 0.120134817816,
    "budget_debit_required": true,
    "scheduled_response_amounts": [
      0.07,
      0.050134817816
    ],
    "scheduled_response_total": 0.120134817816
  },
  "readiness_context_flag": 1.0,
  "regulation_recovery_score": 1.0,
  "selected_route_context": "route_b",
  "source_current": true,
  "source_window": "N13 disrupted-support lane + N14 AP4 closeout + N08 MEM6 + N09 GPR6 + N12 readiness",
  "support_error": 0.120134817816,
  "support_margin": -0.120134817816,
  "support_threshold": 0.85,
  "vector_id": "n15_i3_old_best_source_current_state_vector_v1"
}
```

## Generated Target

```json
{
  "claim_boundary": "runtime-derived target candidate only; not semantic goal ownership, intention, agency, identity acceptance, native support, or final AP5",
  "derivation_policy_id": "n15_endogenous_proxy_derivation_policy_v1",
  "derivation_policy_version": "1.0",
  "drift_clamped": false,
  "input_vector_digest": "3c05e2dc62c87c6ad0a91e7ad26fdb420f61be9c25e555198fc4dccb0af43c02",
  "target_band": [
    0.817594607287,
    0.957594607287
  ],
  "target_center": 0.887594607287,
  "target_center_unclamped": 0.887594607287,
  "target_condition_generated_at": "before_bridge_probe_regulation_candidate_ranking",
  "target_condition_id": "n15_i3_runtime_derived_support_recovery_target_v1",
  "target_condition_surface": "support_recovery_target_band_from_source_current_old_best_claims",
  "target_tolerance": 0.07,
  "weighted_sum": 0.375946072874
}
```

## Bridge Probe

Bridge result: `provisional_yes_bridge_probe_only_pending_external_proxy_contrast_controls_replay_and_claim_boundary`.

| Candidate | Post-response support | In generated band | Rank | Status |
| --- | ---: | --- | ---: | --- |
| `n13_bounded_support_response` | `0.85` | `True` | `1` | `selected_enters_generated_target_band` |
| `no_response_baseline` | `0.729865182184` | `False` | `2` | `rejected_outside_generated_target_band` |

## Candidate Row

```json
{
  "missing_gates": [
    "external_proxy_contrast_not_run_until_iteration_4",
    "adversarial_controls_not_run_until_iteration_5",
    "bounded_drift_and_replay_not_run_until_iteration_6",
    "claim_boundary_classification_not_run_until_iteration_7",
    "final_ap5_not_supported"
  ],
  "provisional_ap_level": "AP5_candidate_pending_contrast_controls_replay",
  "provisional_claim_ceiling": "runtime_derived_target_candidate_with_bridge_probe_pending_contrast_controls_replay_and_claim_boundary",
  "row_id": "n15_i3_row_01_constructed_runtime_derived_target_candidate",
  "target_band": [
    0.817594607287,
    0.957594607287
  ],
  "target_center": 0.887594607287,
  "target_condition_surface": "support_recovery_target_band_from_source_current_old_best_claims",
  "target_tolerance": 0.07
}
```

## Checks

```json
{
  "absolute_path_absence": true,
  "bridge_probe_consumes_target_condition": true,
  "bridge_response_surface_trace_present": true,
  "bridge_selects_bounded_response_over_no_response": true,
  "budget_limits_loaded": true,
  "budget_valid_before_target_use": true,
  "claim_flags_forced_false": true,
  "control_outcomes_present": true,
  "control_value_convention_recorded": true,
  "control_variants_loaded": true,
  "declared_external_proxy_absent": true,
  "dependency_trace_complete_for_target_fields": true,
  "dependency_trace_covers_selected_context_rows": true,
  "derivation_policy_loaded": true,
  "digest_reproducibility": true,
  "direct_historic_ap2_gap_recorded": true,
  "external_target_input_absent": true,
  "fully_native_integration_not_opened": true,
  "inventory_source_passed": true,
  "iteration_3_top_level_output_shape_declared": true,
  "iteration_3_top_level_output_shape_matches_output": true,
  "n14_constructed_followout_in_candidate_path": true,
  "native_support_not_opened": true,
  "no_absolute_paths_recorded": true,
  "no_final_ap5_supported": true,
  "old_best_claim_inputs_present": true,
  "phase8_opened_false": true,
  "replay_digest_inputs_design_note_recorded": true,
  "replay_policy_loaded": true,
  "required_fields_present": true,
  "schema_source_passed": true,
  "selected_source_digests_match_registry": true,
  "source_digest_presence": true,
  "source_registry_loaded": true,
  "src_diff_empty": true,
  "target_band_numeric_and_ordered": true,
  "target_center_within_drift_bound": true,
  "target_condition_functions_as_proxy_input_provisionally": true,
  "target_generated_before_bridge_use": true,
  "target_tolerance_within_policy": true
}
```

## Claim Boundary

```text
runtime-derived target candidate != final AP5 support
target-band bridge probe != semantic goal ownership
bounded regulation candidate != intention or agency
support/identity-condition descriptor != identity acceptance
N12 readiness-only context != native support
N15 Iteration 3 != fully native integration
```

## Output Digest

```text
7fcb73f4b70fdd4f4aadaa9e931040f8299669ca1598c9a1391c560637a26fbc
```
