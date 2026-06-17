# N16 B2 Challenge-Class Sweep Matrix

Status: `passed`.

## Acceptance State

```text
accepted_b2_challenge_sweep_partial_mvp_no_ap6
```

Iteration 4 is the first N16 MVP scientific result. It holds the Iteration 3 `B2` support-persistent basin fixed and sweeps C0-C5 challenge classes without retuning the basin definition.

It does not close final AP6, does not claim B3 repair/reabsorption, and does not claim B4 multi-basin separability.

## Challenge Outcomes

| Cell | Decision | Classification | Leakage | Stability | Failure Mode |
| --- | --- | --- | --- | --- | --- |
| B2_C0 | supported | within_sweep_quiet_b2_anchor | 0.061644 | 1.0 | not_applicable |
| B2_C1 | supported | b2_noise_tolerance_supported | 0.078 | 0.9 | not_applicable |
| B2_C2 | partial | b2_flux_pressure_partial | 0.186 | 0.62 | directional_flux_leakage_exceeds_quiet_ceiling |
| B2_C3 | supported | structured_external_false_positive_rejected | 0.066 | 0.91 | not_applicable |
| B2_C4 | partial | b2_breach_reclosure_partial_not_b3 | 0.148 | 0.55 | breach_pressure_exposes_need_for_b3_repair_probe |
| B2_C5 | rejected | b2_shared_medium_pressure_rejected | 0.31 | 0.32 | shared_medium_leakage_and_merge_pressure_exceed_B2_policy |

## MVP Requirement Summary

```json
{
  "challenge_status": {
    "C0": {
      "boundary_classification": "within_sweep_quiet_b2_anchor",
      "failure_mode": "not_applicable",
      "requirements_failed": [
        "challenge_classes_not_tested_by_c0_anchor"
      ],
      "row_decision": "supported"
    },
    "C1": {
      "boundary_classification": "b2_noise_tolerance_supported",
      "failure_mode": "not_applicable",
      "requirements_failed": [
        "noise_tolerance_does_not_substitute_for_flux_tolerance",
        "noise_tolerance_does_not_substitute_for_repair_or_shared_medium"
      ],
      "row_decision": "supported"
    },
    "C2": {
      "boundary_classification": "b2_flux_pressure_partial",
      "failure_mode": "directional_flux_leakage_exceeds_quiet_ceiling",
      "requirements_failed": [
        "quiet_leakage_ceiling_exceeded_under_directional_flux",
        "minimum_internal_support_floor_not_preserved_under_flux",
        "minimum_coherence_margin_floor_not_preserved_under_flux"
      ],
      "row_decision": "partial"
    },
    "C3": {
      "boundary_classification": "structured_external_false_positive_rejected",
      "failure_mode": "not_applicable",
      "requirements_failed": [
        "C3_success_is_not_flux_tolerance",
        "C3_success_is_not_resource_assimilation"
      ],
      "row_decision": "supported"
    },
    "C4": {
      "boundary_classification": "b2_breach_reclosure_partial_not_b3",
      "failure_mode": "breach_pressure_exposes_need_for_b3_repair_probe",
      "requirements_failed": [
        "regulated_repair_not_supported_for_B2",
        "reclosure_score_below_breach_reclosure_floor",
        "B3_repair_reabsorption_probe_required",
        "quiet_leakage_ceiling_exceeded_under_breach_pressure",
        "minimum_internal_support_floor_not_preserved_under_breach_pressure",
        "minimum_coherence_margin_floor_not_preserved_under_breach_pressure"
      ],
      "row_decision": "partial"
    },
    "C5": {
      "boundary_classification": "b2_shared_medium_pressure_rejected",
      "failure_mode": "shared_medium_leakage_and_merge_pressure_exceed_B2_policy",
      "requirements_failed": [
        "basin_separation_score_below_shared_medium_floor",
        "shared_medium_leakage_exceeds_B2_policy",
        "B2_insufficient_for_multi_basin_shared_medium",
        "quiet_leakage_ceiling_exceeded_under_shared_medium",
        "minimum_internal_support_floor_not_preserved_under_shared_medium",
        "minimum_internal_coherence_floor_not_preserved_under_shared_medium",
        "minimum_coherence_margin_floor_not_preserved_under_shared_medium"
      ],
      "row_decision": "rejected"
    }
  },
  "claim_boundary": "Iteration 4 is the first N16 MVP challenge result but not final AP6 closeout; Iterations 5-6 and final controls remain deferred",
  "extension_recommendations": [
    "B3 x C4 needed for regulated repair/reabsorption evidence",
    "B4 x C5 needed for shared-medium multi-basin separability"
  ],
  "final_ap6_closeout_allowed": false,
  "noise_amplitude_scope": "C1 tests a single MVP noise point at amplitude 0.08; it does not map the full noise tolerance boundary",
  "requirements_failed": [
    "B2_insufficient_for_multi_basin_shared_medium",
    "B3_repair_reabsorption_probe_required",
    "C3_success_is_not_flux_tolerance",
    "C3_success_is_not_resource_assimilation",
    "basin_separation_score_below_shared_medium_floor",
    "challenge_classes_not_tested_by_c0_anchor",
    "minimum_coherence_margin_floor_not_preserved_under_breach_pressure",
    "minimum_coherence_margin_floor_not_preserved_under_flux",
    "minimum_coherence_margin_floor_not_preserved_under_shared_medium",
    "minimum_internal_coherence_floor_not_preserved_under_shared_medium",
    "minimum_internal_support_floor_not_preserved_under_breach_pressure",
    "minimum_internal_support_floor_not_preserved_under_flux",
    "minimum_internal_support_floor_not_preserved_under_shared_medium",
    "noise_tolerance_does_not_substitute_for_flux_tolerance",
    "noise_tolerance_does_not_substitute_for_repair_or_shared_medium",
    "quiet_leakage_ceiling_exceeded_under_breach_pressure",
    "quiet_leakage_ceiling_exceeded_under_directional_flux",
    "quiet_leakage_ceiling_exceeded_under_shared_medium",
    "reclosure_score_below_breach_reclosure_floor",
    "regulated_repair_not_supported_for_B2",
    "shared_medium_leakage_exceeds_B2_policy"
  ],
  "requirements_failed_by_challenge": {
    "C0": [
      "challenge_classes_not_tested_by_c0_anchor"
    ],
    "C1": [
      "noise_tolerance_does_not_substitute_for_flux_tolerance",
      "noise_tolerance_does_not_substitute_for_repair_or_shared_medium"
    ],
    "C2": [
      "quiet_leakage_ceiling_exceeded_under_directional_flux",
      "minimum_internal_support_floor_not_preserved_under_flux",
      "minimum_coherence_margin_floor_not_preserved_under_flux"
    ],
    "C3": [
      "C3_success_is_not_flux_tolerance",
      "C3_success_is_not_resource_assimilation"
    ],
    "C4": [
      "regulated_repair_not_supported_for_B2",
      "reclosure_score_below_breach_reclosure_floor",
      "B3_repair_reabsorption_probe_required",
      "quiet_leakage_ceiling_exceeded_under_breach_pressure",
      "minimum_internal_support_floor_not_preserved_under_breach_pressure",
      "minimum_coherence_margin_floor_not_preserved_under_breach_pressure"
    ],
    "C5": [
      "basin_separation_score_below_shared_medium_floor",
      "shared_medium_leakage_exceeds_B2_policy",
      "B2_insufficient_for_multi_basin_shared_medium",
      "quiet_leakage_ceiling_exceeded_under_shared_medium",
      "minimum_internal_support_floor_not_preserved_under_shared_medium",
      "minimum_internal_coherence_floor_not_preserved_under_shared_medium",
      "minimum_coherence_margin_floor_not_preserved_under_shared_medium"
    ]
  },
  "requirements_observed": [
    "B2 can record breach pressure but does not yet support B3 repair/reabsorption",
    "B2 is insufficient for C5 shared-medium pressure without B4-style separability evidence",
    "B2 needs stronger retention or lower leakage to survive C2 cleanly",
    "B2 tolerates bounded unstructured perturbation at noise_amplitude_0.08",
    "C0 baseline supports comparison but does not prove robustness",
    "directional flux is the first hard boundary-pressure requirement",
    "structured external coherence must remain external unless crossing or disruption is recorded"
  ],
  "requirements_observed_by_challenge": {
    "C0": [
      "C0 baseline supports comparison but does not prove robustness"
    ],
    "C1": [
      "B2 tolerates bounded unstructured perturbation at noise_amplitude_0.08"
    ],
    "C2": [
      "B2 needs stronger retention or lower leakage to survive C2 cleanly",
      "directional flux is the first hard boundary-pressure requirement"
    ],
    "C3": [
      "structured external coherence must remain external unless crossing or disruption is recorded"
    ],
    "C4": [
      "B2 can record breach pressure but does not yet support B3 repair/reabsorption"
    ],
    "C5": [
      "B2 is insufficient for C5 shared-medium pressure without B4-style separability evidence"
    ]
  },
  "synthesis_mode": "partial_mvp",
  "where_b2_is_partial": [
    "C2",
    "C4"
  ],
  "where_b2_is_rejected": [
    "C5"
  ],
  "where_b2_remains_bounded": [
    "C0",
    "C1",
    "C3"
  ]
}
```

## Fixed B2 Audit

```json
{
  "B2_fixed_across_challenges": true,
  "canonical_b2_definition_digest": "e60b71228ee2411e95a77f1724f2c37f6738a8192d2eeab974a385b4dbb2fda0",
  "canonical_b2_reference_metrics": {
    "boundary_stability_score": 1.0,
    "coherence_margin": 0.53,
    "external_coherence": 0.35,
    "internal_coherence": 0.88,
    "leakage_ratio": 0.061644,
    "minimum_internal_support": 0.86,
    "retained_flux": 1.46
  },
  "canonical_b2_source_artifact": "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/n16_quiet_boundary_calibration.json",
  "canonical_b2_source_row_id": "n16_i3_row_b2_c0",
  "only_challenge_class_changes": true,
  "post_challenge_drift_surface_deferred_to": [
    "5",
    "6"
  ],
  "same_admissibility_rules": true,
  "same_boundary_policy": true,
  "same_boundary_side_assignments": true,
  "same_boundary_side_assignments_intent": "Iteration 4 tests challenge response against the initial fixed B2 boundary-side assignment; post-challenge drift, leakage, and merge pressure are measured as effects rather than by silently changing the canonical assignment"
}
```

## Quiet Calibration Source Provenance

```json
{
  "accepted_output_digest": "863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1",
  "current_file_sha256": "625cd005da6fe7f31ae704ea63d9af3833818a19a2c6de5c3282d0b9dbe70297",
  "current_output_digest": "863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1",
  "file_sha_policy": "file SHA-256 is recorded for the current artifact bytes; semantic provenance uses output_digest because generated_at and git metadata are excluded from the stable digest",
  "output_digest_matches_acceptance": true
}
```

## Metric Construction Rationale

```json
{
  "baseline_anchor": "B2_C0 metrics reproduce the Iteration 3 B2 quiet row",
  "basin_separation_score": "C5-only shared-medium separation score; below the B4-style separation floor and therefore a reference failure",
  "boundary_stability_score": "ordered MVP stability score: quiet anchor highest, bounded noise and C3 false-positive rejection high, directional flux/breach partial, shared medium rejected",
  "construction_type": "deterministic MVP stress probe constructed from the fixed Iteration 3 B2 baseline; metric values are explicit challenge-case construction values, not independent physics simulation outputs",
  "flux_tolerance_score": "C2-only score reflecting retained measurable boundary under one-sided flow despite leakage and floor failures",
  "leakage_ratio": "records challenge-specific cross-boundary leakage pressure; C2/C4/C5 intentionally exceed the quiet leakage ceiling to expose requirements",
  "noise_resilience_score": "C1-only score at the single MVP noise amplitude; it is not a general robustness envelope",
  "repair_score": "C4-only reclosure-pressure score; below the breach reclosure floor and therefore not B3 repair/reabsorption support",
  "retained_flux": "starts from the B2_C0 retained flux baseline and decreases as the challenge profile adds leakage, breach, or shared-medium pressure"
}
```

## Challenge Pressure Rationale

```json
{
  "C0": "zero pressure anchor used for within-sweep comparison",
  "C1": "noise_amplitude 0.08 is a bounded MVP perturbation point that should not substitute for flux, breach, or shared-medium evidence",
  "C2": "directional_flux_pressure 0.34 is the fixed hard C2 stressor for Iteration 4 and Iteration 5 comparison; it is high enough to expose leakage while leaving the boundary measurable",
  "C3": "structured_external_coherence_pressure 0.92 creates strong coherent outside false-positive pressure without crossing or disruption",
  "C4": "breach_pressure 0.38 creates partial reclosure pressure below the B3 repair/reabsorption claim boundary",
  "C5": "shared_medium_pressure 0.44 creates a reference shared-medium failure for B2 and motivates the later B4 x C5 probe"
}
```

## C2 External Role Rationale

```json
{
  "external_state_role": "coupling_channel",
  "perturbation_present_semantics": "the field marks unstructured or localized perturbation pressure; C2 records directional_flux_pressure separately",
  "reason": "C2 is directed flow across/against the boundary, so the external state role is a coupling channel rather than unstructured perturbation"
}
```

## Challenge Thresholds

```json
{
  "breach_reclosure_floor": 0.7,
  "flux_leakage_warning": 0.12,
  "internal_coherence_floor": 0.84,
  "internal_support_floor": 0.85,
  "minimum_coherence_margin_floor": 0.52,
  "quiet_leakage_ceiling": 0.12,
  "shared_medium_basin_separation_floor": 0.7
}
```

## Challenge Boundary Notes

- `C1` records noise tolerance only; it does not substitute for flux, repair, or shared-medium evidence.
- `C2` is the first hard flux-pressure result and is partial because leakage and support/coherence floors fail under one-sided flow.
- `C3` is supported as false-positive rejection, not structured environment assimilation.
- `C4` records breach/reclosure pressure but does not promote B2 into B3 repair capability.
- `C5` rejects B2 sufficiency under shared-medium pressure and points to the later B4 x C5 probe.
- `neighbor_basin_q0` is a synthetic C5 stressor only; it is not source-backed B4 evidence.

## Checks

```json
{
  "all_boundary_claims_false": true,
  "all_rows_hold_b2_fixed": true,
  "c0_metrics_match_i3_b2_reference": true,
  "c0_within_sweep_anchor_present": true,
  "c1_limited_to_noise_tolerance": true,
  "c2_external_state_role_is_coupling_channel": true,
  "c2_flux_pressure_measured": true,
  "c3_structured_false_positive_rejected": true,
  "c4_breach_not_promoted_to_b3": true,
  "c4_general_threshold_failures_recorded": true,
  "c5_general_threshold_failures_recorded": true,
  "c5_shared_medium_not_promoted_to_b4": true,
  "challenge_classes_c0_to_c5_present": true,
  "i3_output_digest_matches_acceptance": true,
  "mvp_keeps_ap6_provisional": true,
  "requirements_failed_recorded_for_every_row": true,
  "row_count_is_six": true
}
```

## Output Digest

```text
b91d7bb77fd0053d9995a05a11571471a9338c0ce6b63909ca5021d429ce9d77
```
