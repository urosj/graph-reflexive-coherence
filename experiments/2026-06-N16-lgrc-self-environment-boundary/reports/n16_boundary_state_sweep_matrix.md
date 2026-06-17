# N16 Boundary-State Sweep Matrix

Status: `passed`.

## Acceptance State

```text
accepted_boundary_state_flux_sweep_no_ap6
```

Iteration 5 holds the hard Iteration 4 `C2` directional-flux challenge fixed and compares boundary-state maturity levels `B0-B4`.

The question is not whether a row can be retuned to pass. The question is which boundary-state level changes the `B2 x C2` partial result and why.

## Fixed C2 Policy

```json
{
  "challenge_class": "C2",
  "challenge_name": "directional flux",
  "challenge_profile": {
    "breach_pressure": 0.0,
    "directional_flux_pressure": 0.34,
    "noise_amplitude": 0.0,
    "shared_medium_pressure": 0.0,
    "structured_external_coherence_pressure": 0.0
  },
  "external_state_role": "coupling_channel",
  "perturbation_present_semantics": "C2 is directional flux through a coupling channel; it is not unstructured perturbation",
  "policy": "C2 pressure, threshold floors, leakage ceiling, external-state role, and admissibility rules are inherited from Iteration 4 without retuning per boundary state"
}
```

## Metric Construction Formulas

```json
{
  "boundary_stability_score": {
    "reason": "ordered maturity score for the fixed-C2 sweep: null < localized partition < B2 partial anchor < B4 coupled partial < B3 repair candidate that resolves the specific B2 C2 failures",
    "status": "explicit_construction_anchor"
  },
  "bounded_reabsorption_response": {
    "claim_boundary": "net retained flux under B3 repair pressure; not autonomous reabsorption or native repair",
    "formula": "inbound_flux - outbound_flux",
    "rounding": "six decimal places",
    "status": "formula_derived_for_B3"
  },
  "flux_tolerance_score": {
    "reason": "fixed-C2 comparison score for how much directional flux remains usable without violating the claim boundary",
    "status": "explicit_construction_anchor"
  },
  "leakage_ratio": {
    "reason": "leakage_ratio is a normalized failure-severity score, not direct outbound_flux / inbound_flux. B2 is inherited exactly from Iteration 4; B0/B1/B3/B4 are fixed construction anchors for B-state comparison under the same C2 profile.",
    "row_anchors": {
      "B0": "1.0 because externally organized flux has no supported internal boundary",
      "B1": "0.294 because localized partition leaks strongly under fixed C2",
      "B2": "0.186 exact Iteration 4 B2_C2 reproduction",
      "B3": "0.112 because bounded repair lowers leakage below the quiet ceiling",
      "B4": "0.132 because retained flux improves but neighbor leakage/merge pressure keep leakage above ceiling"
    },
    "status": "explicit_construction_anchor"
  },
  "metric_status": "Iteration 5 uses deterministic construction values for the fixed-C2 stress probe, not independent simulation outputs. Formula-derived values are marked here; construction anchors are listed explicitly.",
  "repair_score": {
    "reason": "B3-only artifact-level bounded repair/reabsorption score under C2",
    "status": "explicit_construction_anchor"
  },
  "retained_flux": {
    "reason": "retained_flux records intended-basin retained signal under fixed C2; B2 is inherited exactly from Iteration 4, while B3/B4 test repair and coupling effects without changing C2 pressure",
    "status": "explicit_construction_anchor"
  },
  "upstream_downstream_asymmetry_score": {
    "formula": "abs(inbound_flux - outbound_flux) / (inbound_flux + outbound_flux)",
    "rounding": "six decimal places",
    "status": "formula_derived",
    "zero_denominator_policy": "0.0"
  }
}
```

## Boundary-State Outcomes

| Cell | Decision | Classification | Leakage | Retained Flux | Stability | Failure Mode |
| --- | --- | --- | --- | --- | --- | --- |
| B0_C2 | rejected | active_null_flux_structure_rejected_as_boundary_support | 1.0 | 0.0 | 0.0 | externally_organized_flux_no_internal_boundary |
| B1_C2 | partial | localized_partition_flux_pressure_partial | 0.294 | 0.76 | 0.34 | localized_partition_leaks_under_directional_flux |
| B2_C2 | partial | b2_c2_reproduced_iteration_4_partial_anchor | 0.186 | 1.18 | 0.62 | directional_flux_leakage_exceeds_quiet_ceiling |
| B3_C2 | supported | b3_flux_repair_improves_b2_c2_failure_modes | 0.112 | 1.29 | 0.78 | c2_flux_repair_not_general_repair |
| B4_C2 | partial | b4_c2_flux_stress_partial_not_c5_separability | 0.132 | 1.31 | 0.64 | coupled_flux_distribution_does_not_prove_b4_separability |

## B2 Reproduction Audit

```json
{
  "anchor_reference": {
    "boundary_stability_score": 0.62,
    "challenge_profile": {
      "breach_pressure": 0.0,
      "directional_flux_pressure": 0.34,
      "noise_amplitude": 0.0,
      "shared_medium_pressure": 0.0,
      "structured_external_coherence_pressure": 0.0
    },
    "coherence_margin": 0.488,
    "external_coherence": 0.36,
    "failure_mode": "directional_flux_leakage_exceeds_quiet_ceiling",
    "flux_tolerance_score": 0.46,
    "inbound_flux": 0.34,
    "internal_coherence": 0.848,
    "leakage_ratio": 0.186,
    "minimum_internal_support": 0.84,
    "outbound_flux": 0.22,
    "requirements_failed": [
      "quiet_leakage_ceiling_exceeded_under_directional_flux",
      "minimum_internal_support_floor_not_preserved_under_flux",
      "minimum_coherence_margin_floor_not_preserved_under_flux"
    ],
    "retained_flux": 1.18,
    "row_decision": "partial",
    "upstream_downstream_asymmetry_score": 0.214286
  },
  "exact_reproduction": true,
  "iteration_4_anchor_cell": "B2_C2",
  "iteration_5_b2_metrics": {
    "boundary_stability_score": 0.62,
    "challenge_profile": {
      "breach_pressure": 0.0,
      "directional_flux_pressure": 0.34,
      "noise_amplitude": 0.0,
      "shared_medium_pressure": 0.0,
      "structured_external_coherence_pressure": 0.0
    },
    "coherence_margin": 0.488,
    "external_coherence": 0.36,
    "failure_mode": "directional_flux_leakage_exceeds_quiet_ceiling",
    "flux_tolerance_score": 0.46,
    "inbound_flux": 0.34,
    "internal_coherence": 0.848,
    "leakage_ratio": 0.186,
    "minimum_internal_support": 0.84,
    "outbound_flux": 0.22,
    "requirements_failed": [
      "quiet_leakage_ceiling_exceeded_under_directional_flux",
      "minimum_internal_support_floor_not_preserved_under_flux",
      "minimum_coherence_margin_floor_not_preserved_under_flux"
    ],
    "retained_flux": 1.18,
    "row_decision": "partial",
    "upstream_downstream_asymmetry_score": 0.214286
  },
  "tolerance_policy": "deterministic_exact_match_required_for_iteration_5"
}
```

## B3 Improvement Audit

```json
{
  "addresses_same_failure_modes": true,
  "b2_failed_requirements": [
    "quiet_leakage_ceiling_exceeded_under_directional_flux",
    "minimum_internal_support_floor_not_preserved_under_flux",
    "minimum_coherence_margin_floor_not_preserved_under_flux"
  ],
  "b3_satisfied_requirements": [
    "b2_c0_c1_c2_prerequisite_satisfied_before_B3",
    "quiet_leakage_ceiling_preserved_under_directional_flux",
    "minimum_internal_support_floor_preserved_under_flux",
    "minimum_internal_coherence_floor_preserved_under_flux",
    "minimum_coherence_margin_floor_preserved_under_flux",
    "retained_flux_improves_over_B2_C2",
    "boundary_stability_improves_over_B2_C2",
    "repair_score_recorded_under_flux",
    "C2_external_state_role_recorded_as_coupling_channel"
  ],
  "claim_boundary": "B3 support is artifact-level flux repair candidate evidence, not agency, intention, selfhood, native support, or final AP6",
  "coherence_margin_delta": 0.044,
  "compared_to": "B2_C2",
  "internal_coherence_delta": 0.01,
  "leakage_delta": -0.074,
  "minimum_internal_support_delta": 0.012,
  "outbound_flux_delta": -0.04,
  "retained_flux_delta": 0.11,
  "stability_delta": 0.16,
  "upstream_downstream_asymmetry_delta": 0.093406
}
```

## B4 C2 Provisional Audit

```json
{
  "basin_separation_score": 0.61,
  "claim_boundary": "B4 x C2 is a flux stress row only; B4 x C5 remains required for shared-medium separability",
  "flux_decomposition": {
    "leakage_into_neighbor_basin": 0.09,
    "merge_confusion_pressure": 0.27,
    "redirected_flux_through_coupling_channel": 0.12,
    "repair_or_reabsorption_present": false,
    "retained_flux_within_intended_basin": 1.31
  },
  "requirements_failed": [
    "B4_C2_is_not_B4_C5_shared_medium_separability",
    "quiet_leakage_ceiling_exceeded_under_directional_flux",
    "minimum_coherence_margin_floor_not_preserved_under_flux",
    "basin_separation_score_below_shared_medium_floor",
    "merge_confusion_pressure_not_resolved_under_C2"
  ],
  "row_decision": "partial"
}
```

## Maturity Gradient Summary

```json
{
  "claim_boundary": "Iteration 5 refines C2 flux-survival requirements only; final AP6 remains blocked",
  "final_ap6_closeout_allowed": false,
  "fixed_challenge": {
    "challenge_class": "C2",
    "challenge_name": "directional flux",
    "challenge_profile": {
      "breach_pressure": 0.0,
      "directional_flux_pressure": 0.34,
      "noise_amplitude": 0.0,
      "shared_medium_pressure": 0.0,
      "structured_external_coherence_pressure": 0.0
    },
    "external_state_role": "coupling_channel",
    "perturbation_present_semantics": "C2 is directional flux through a coupling channel; it is not unstructured perturbation",
    "policy": "C2 pressure, threshold floors, leakage ceiling, external-state role, and admissibility rules are inherited from Iteration 4 without retuning per boundary state"
  },
  "gradient": {
    "B0": {
      "basin_separation_score": "not_evaluated_by_b0_c2",
      "boundary_classification": "active_null_flux_structure_rejected_as_boundary_support",
      "boundary_stability_score": 0.0,
      "coherence_margin": -0.62,
      "flux_tolerance_score": 0.0,
      "internal_coherence": 0.0,
      "leakage_ratio": 1.0,
      "repair_score": "not_evaluated_by_b0",
      "requirements_failed": [
        "no_internal_support_relevant_side_under_flux",
        "no_boundary_edge_under_flux",
        "quiet_leakage_ceiling_exceeded_under_directional_flux",
        "minimum_internal_support_floor_not_preserved_under_flux",
        "minimum_internal_coherence_floor_not_preserved_under_flux",
        "minimum_coherence_margin_floor_not_preserved_under_flux"
      ],
      "retained_flux": 0.0,
      "row_decision": "rejected",
      "upstream_downstream_asymmetry_score": 0.0
    },
    "B1": {
      "basin_separation_score": "not_evaluated_by_b1_c2",
      "boundary_classification": "localized_partition_flux_pressure_partial",
      "boundary_stability_score": 0.34,
      "coherence_margin": 0.442,
      "flux_tolerance_score": 0.22,
      "internal_coherence": 0.812,
      "leakage_ratio": 0.294,
      "repair_score": "not_evaluated_by_b1",
      "requirements_failed": [
        "support_persistence_not_claimed_for_B1",
        "quiet_leakage_ceiling_exceeded_under_directional_flux",
        "minimum_internal_support_floor_not_preserved_under_flux",
        "minimum_internal_coherence_floor_not_preserved_under_flux",
        "minimum_coherence_margin_floor_not_preserved_under_flux"
      ],
      "retained_flux": 0.76,
      "row_decision": "partial",
      "upstream_downstream_asymmetry_score": 0.096774
    },
    "B2": {
      "basin_separation_score": "not_evaluated_by_b2_c2",
      "boundary_classification": "b2_c2_reproduced_iteration_4_partial_anchor",
      "boundary_stability_score": 0.62,
      "coherence_margin": 0.488,
      "flux_tolerance_score": 0.46,
      "internal_coherence": 0.848,
      "leakage_ratio": 0.186,
      "repair_score": "not_evaluated_by_b2_c2",
      "requirements_failed": [
        "quiet_leakage_ceiling_exceeded_under_directional_flux",
        "minimum_internal_support_floor_not_preserved_under_flux",
        "minimum_coherence_margin_floor_not_preserved_under_flux"
      ],
      "retained_flux": 1.18,
      "row_decision": "partial",
      "upstream_downstream_asymmetry_score": 0.214286
    },
    "B3": {
      "basin_separation_score": "not_evaluated_by_b3_c2",
      "boundary_classification": "b3_flux_repair_improves_b2_c2_failure_modes",
      "boundary_stability_score": 0.78,
      "coherence_margin": 0.532,
      "flux_tolerance_score": 0.72,
      "internal_coherence": 0.858,
      "leakage_ratio": 0.112,
      "repair_score": 0.74,
      "requirements_failed": [
        "B3_C2_is_not_B3_C4_breach_repair_closeout",
        "bounded_reabsorption_is_not_autonomous_repair",
        "final_ap6_not_allowed"
      ],
      "retained_flux": 1.29,
      "row_decision": "supported",
      "upstream_downstream_asymmetry_score": 0.307692
    },
    "B4": {
      "basin_separation_score": 0.61,
      "boundary_classification": "b4_c2_flux_stress_partial_not_c5_separability",
      "boundary_stability_score": 0.64,
      "coherence_margin": 0.514,
      "flux_tolerance_score": 0.58,
      "internal_coherence": 0.852,
      "leakage_ratio": 0.132,
      "repair_score": "not_evaluated_by_b4_c2",
      "requirements_failed": [
        "B4_C2_is_not_B4_C5_shared_medium_separability",
        "quiet_leakage_ceiling_exceeded_under_directional_flux",
        "minimum_coherence_margin_floor_not_preserved_under_flux",
        "basin_separation_score_below_shared_medium_floor",
        "merge_confusion_pressure_not_resolved_under_C2"
      ],
      "retained_flux": 1.31,
      "row_decision": "partial",
      "upstream_downstream_asymmetry_score": 0.259259
    }
  },
  "necessary_flux_survival_requirements": [
    "stable fixed C2 policy and failure vocabulary",
    "support floor preservation under directional flux",
    "coherence-margin preservation under directional flux",
    "leakage at or below quiet leakage ceiling",
    "retained flux must be separated from redirected coupling flux",
    "B4 separability still requires B4 x C5"
  ],
  "synthesis_mode": "partial_mvp",
  "what_changed_relative_to_iteration_4": {
    "B1_vs_B2": "B1 remains weaker than B2 under the same C2 pressure: lower retained flux, higher leakage, and no persistence claim",
    "B2_reproduced": true,
    "B3_supported_claim_blocked_note": "B3 row_decision=supported means the fixed C2 failure modes are resolved at artifact level; boundary_claim_allowed and final_ap6_supported remain false",
    "B3_vs_B2": {
      "coherence_margin_floor_preserved": true,
      "leakage_delta": -0.074,
      "retained_flux_delta": 0.11,
      "stability_delta": 0.16,
      "support_floor_preserved": true
    },
    "B3_vs_B4": "B4 retained flux is slightly higher than B3, but B3 is the supported C2 repair row because B4 still has neighbor leakage, merge confusion pressure, leakage above the quiet ceiling, and basin separation below the shared-medium floor",
    "B4_vs_B2": "B4 improves retained flux but introduces coupling/neighbor leakage and merge pressure, so it remains partial under C2"
  }
}
```

## Iteration 6 Guardrails

```json
{
  "b3_c2_scope_guard": "B3_C2 supports only C2 directional-flux repair improvement. It does not show general repair, breach reclosure, autonomous reabsorption, native support, agency, or final AP6.",
  "b3_c4_contrast_pair": {
    "b2_failed_requirements": [
      "quiet_leakage_ceiling_exceeded_under_directional_flux",
      "minimum_internal_support_floor_not_preserved_under_flux",
      "minimum_coherence_margin_floor_not_preserved_under_flux"
    ],
    "b3_satisfied_requirements": [
      "b2_c0_c1_c2_prerequisite_satisfied_before_B3",
      "quiet_leakage_ceiling_preserved_under_directional_flux",
      "minimum_internal_support_floor_preserved_under_flux",
      "minimum_internal_coherence_floor_preserved_under_flux",
      "minimum_coherence_margin_floor_preserved_under_flux",
      "retained_flux_improves_over_B2_C2",
      "boundary_stability_improves_over_B2_C2",
      "repair_score_recorded_under_flux",
      "C2_external_state_role_recorded_as_coupling_channel"
    ],
    "contrast_from": "B2_C2",
    "contrast_to": "B3_C2",
    "iteration_6_question": "Does the B3 mechanism that repaired C2 leakage also support breach/reclosure in B3_C4, or was it only flux-specific?"
  },
  "b4_c2_scope_guard": "B4_C2 remains partial, not nearly supported. Retained flux must not dominate interpretation while coupling, neighbor leakage, merge pressure, and basin separation remain unresolved.",
  "b4_c5_design_inputs": {
    "basin_separation_score": 0.61,
    "iteration_6_question": "Can B4_C5 resolve shared-medium separability rather than merely preserve or redistribute retained flux?",
    "leakage_into_neighbor_basin": 0.09,
    "merge_confusion_pressure": 0.27,
    "redirected_flux_through_coupling_channel": 0.12
  },
  "claim_boundary": "Iteration 6 may use Iteration 5 contrast pairs and risk signals, but final AP6 remains blocked until controls, replay, and claim classification close cleanly.",
  "selected_probe_expectations": {
    "B0_C3": "reject structured external coherence as boundary support; external coherence remains false-positive pressure, not self-region evidence",
    "B1_C2": "reproduce weak localized flux partial behavior; extraction remains below persistence or repair",
    "B2_C1": "reproduce bounded noise tolerance; C1 success must not substitute for C2/C4/C5 evidence",
    "B3_C4": "test whether the B3 mechanism that repaired C2 leakage also supports breach/reclosure, or whether the improvement was flux-specific",
    "B4_C5": "test whether B4 can resolve neighbor leakage, redirected coupling flux, merge pressure, and insufficient basin separation under shared medium pressure"
  }
}
```

## Interpretation

`B0` rejects externally organized flux as boundary support. `B1` extracts a weak localized partition but leaks under the same C2 pressure. `B2` reproduces the Iteration 4 partial result exactly. `B3` is the first row that resolves the specific B2 C2 leakage, support, and coherence-margin failures, but only as an artifact-level repair candidate. `B4` improves retained flux but introduces coupling and neighbor-leakage ambiguity, so it remains partial until the B4 x C5 shared-medium probe.

The important guard is that `B3_C2` is C2 flux repair only, not general repair. `B3_C4` must still test breach/reclosure. `B4_C2` is also not nearly supported: its retained flux is explicitly separated from redirected coupling flux, neighbor leakage, and merge pressure, which should drive `B4_C5`.

## Checks

```json
{
  "all_boundary_claims_false": true,
  "all_rows_under_c2": true,
  "all_rows_use_coupling_channel_role": true,
  "b0_rejects_flux_structure": true,
  "b1_limited_to_localized_partition": true,
  "b2_reproduces_iteration4_c2_partial_result": true,
  "b3_addresses_b2_specific_c2_failures": true,
  "b3_unlocked_by_b2_c0_c1_c2": true,
  "b4_c2_remains_provisional": true,
  "b4_distinguishes_retention_coupling_leakage_and_merge": true,
  "boundary_states_b0_to_b4_present": true,
  "failure_vocabulary_reused": true,
  "fixed_c2_profile_preserved": true,
  "i4_output_digest_matches_acceptance": true,
  "mvp_keeps_ap6_provisional": true,
  "row_count_is_five": true
}
```

## Output Digest

```text
a24c1db84cefbfcb3e99a26373ef5a12f21c795e0574c91fbb06ce72435e2620
```
