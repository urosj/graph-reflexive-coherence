# N16 Selected Interaction Probe Matrix

Status: `passed`.

## Acceptance State

```text
accepted_selected_interaction_probes_no_ap6
```

Iteration 6 is selective, not a new full matrix. It runs only the five planned cells exposed by Iterations 4-5.

## Selected Outcomes

| Cell | Decision | Classification | Leakage | Stability | Failure Mode |
| --- | --- | --- | --- | --- | --- |
| B0_C3 | supported | b0_c3_structured_external_false_positive_rejected | 0.0 | 0.0 | structured_external_coherence_no_internal_boundary |
| B1_C2 | partial | b1_c2_weak_boundary_replay_partial | 0.294 | 0.34 | localized_partition_leaks_under_directional_flux |
| B2_C1 | supported | b2_c1_persistent_noise_replay_supported | 0.078 | 0.9 | not_applicable |
| B3_C4 | supported | b3_c4_breach_reclosure_candidate_supported | 0.118 | 0.74 | breach_reclosure_candidate_not_autonomous_repair |
| B4_C5 | supported | b4_c5_shared_medium_separability_candidate_supported | 0.108 | 0.76 | shared_medium_separability_candidate_requires_final_controls |

## Probe Summary

```json
{
  "cell_status": {
    "B0_C3": {
      "boundary_classification": "b0_c3_structured_external_false_positive_rejected",
      "failure_mode": "structured_external_coherence_no_internal_boundary",
      "requirements_failed": [
        "no_internal_support_relevant_side_under_structured_external_coherence",
        "no_boundary_edge_under_structured_external_coherence",
        "structured_external_coherence_is_not_self_region",
        "final_ap6_not_allowed"
      ],
      "requirements_satisfied": [
        "structured_external_coherence_rejected_as_boundary_support",
        "active_null_boundary_claim_remains_false",
        "C3_external_state_role_preserved_as_structured_external_state",
        "supported_decision_confirms_active_null_rejection_not_boundary_support"
      ],
      "row_decision": "supported"
    },
    "B1_C2": {
      "boundary_classification": "b1_c2_weak_boundary_replay_partial",
      "failure_mode": "localized_partition_leaks_under_directional_flux",
      "requirements_failed": [
        "support_persistence_not_claimed_for_B1",
        "quiet_leakage_ceiling_exceeded_under_directional_flux",
        "minimum_internal_support_floor_not_preserved_under_flux",
        "minimum_internal_coherence_floor_not_preserved_under_flux",
        "minimum_coherence_margin_floor_not_preserved_under_flux"
      ],
      "requirements_satisfied": [
        "localized_partition_visible_under_flux",
        "boundary_edge_extraction_under_flux_recorded",
        "C2_external_state_role_recorded_as_coupling_channel"
      ],
      "row_decision": "partial"
    },
    "B2_C1": {
      "boundary_classification": "b2_c1_persistent_noise_replay_supported",
      "failure_mode": "not_applicable",
      "requirements_failed": [
        "noise_tolerance_does_not_substitute_for_flux_tolerance",
        "noise_tolerance_does_not_substitute_for_repair_or_shared_medium"
      ],
      "requirements_satisfied": [
        "noise_resilience_score_recorded",
        "derived_boundary_edges_remain_incident_to_both_sides",
        "leakage_ratio_remains_below_c0_ceiling_under_noise"
      ],
      "row_decision": "supported"
    },
    "B3_C4": {
      "boundary_classification": "b3_c4_breach_reclosure_candidate_supported",
      "failure_mode": "breach_reclosure_candidate_not_autonomous_repair",
      "requirements_failed": [
        "B3_C4_is_not_autonomous_repair_or_native_reabsorption",
        "B3_C4_does_not_close_final_AP6",
        "full_control_matrix_still_required",
        "duplicate_and_order_inversion_replay_still_required"
      ],
      "requirements_satisfied": [
        "b3_unlock_allowed_by_b2_c0_c1_c2",
        "breach_pressure_recorded",
        "reclosure_score_above_breach_reclosure_floor",
        "quiet_leakage_ceiling_preserved_under_breach_pressure",
        "minimum_internal_support_floor_preserved_under_breach_pressure",
        "minimum_coherence_margin_floor_preserved_under_breach_pressure",
        "B3_C4_breach_reclosure_candidate_supported",
        "B3_C4_compared_inline_against_B2_C4_baseline",
        "B3_C2_anchor_metrics_inlined_for_generalization_audit"
      ],
      "row_decision": "supported"
    },
    "B4_C5": {
      "boundary_classification": "b4_c5_shared_medium_separability_candidate_supported",
      "failure_mode": "shared_medium_separability_candidate_requires_final_controls",
      "requirements_failed": [
        "B4_C5_is_artifact_level_separability_candidate_only",
        "B4_C5_does_not_close_final_AP6",
        "native_multi_basin_separability_not_supported",
        "full_control_matrix_still_required",
        "duplicate_and_order_inversion_replay_still_required",
        "reverse_basin_perspective_replay_deferred_before_final_AP6"
      ],
      "requirements_satisfied": [
        "B4_C5_separability_measured_not_inherited_from_label",
        "basin_separation_score_above_shared_medium_floor",
        "shared_medium_leakage_below_quiet_ceiling",
        "merge_confusion_pressure_below_ceiling",
        "boundary_exclusivity_score_above_floor",
        "neighbor_leakage_distinguished_from_retained_flux",
        "B4_C5_asymmetric_one_sided_separability_probe_recorded",
        "B4_C5_leakage_ratio_documented_as_shared_medium_leakage"
      ],
      "row_decision": "supported"
    }
  },
  "claim_boundary": "Iteration 6 supplies selected extension evidence only; final AP6 remains blocked until Iteration 7-8 controls and classification",
  "final_ap6_closeout_allowed": false,
  "remaining_iteration_7_blockers": [
    "full_negative_control_matrix",
    "duplicate_and_order_inversion_replay",
    "claim_boundary_classification",
    "final_AP6_closeout_decision"
  ],
  "selected_cells": [
    "B0_C3",
    "B1_C2",
    "B2_C1",
    "B3_C4",
    "B4_C5"
  ],
  "synthesis_mode": "partial_mvp",
  "unresolved_questions_answered": {
    "did_b3_generalize_from_c2_flux_to_c4_breach_reclosure": true,
    "did_b4_resolve_c5_shared_medium_separability": true
  }
}
```

## B3 C4 Repair Audit

```json
{
  "b2_c4_baseline_reference": {
    "basin_separation_score": "not_evaluated_by_c4",
    "boundary_stability_score": 0.55,
    "coherence_margin": 0.472,
    "failure_mode": "breach_pressure_exposes_need_for_b3_repair_probe",
    "inbound_flux": 0.18,
    "internal_coherence": 0.842,
    "leakage_ratio": 0.148,
    "minimum_internal_support": 0.83,
    "outbound_flux": 0.16,
    "repair_score": 0.52,
    "retained_flux": 1.05,
    "row_decision": "partial"
  },
  "b3_c2_anchor_metrics": {
    "basin_separation_score": "not_evaluated_by_b3_c2",
    "boundary_stability_score": 0.78,
    "coherence_margin": 0.532,
    "failure_mode": "c2_flux_repair_not_general_repair",
    "inbound_flux": 0.34,
    "internal_coherence": 0.858,
    "leakage_ratio": 0.112,
    "minimum_internal_support": 0.852,
    "outbound_flux": 0.18,
    "repair_score": 0.74,
    "retained_flux": 1.29,
    "row_decision": "supported"
  },
  "b3_c4_delta_vs_b2_c4": {
    "boundary_stability_delta": 0.19,
    "coherence_margin_delta": 0.052,
    "leakage_ratio_delta": -0.03,
    "reclosure_score_delta": 0.24
  },
  "breach_reclosure_floor": 0.7,
  "claim_boundary": "B3_C4 is artifact-level breach/reclosure candidate evidence, not autonomous repair, agency, native support, or final AP6",
  "probe_decomposition": {
    "b2_c4_baseline_reference": {
      "basin_separation_score": "not_evaluated_by_c4",
      "boundary_stability_score": 0.55,
      "coherence_margin": 0.472,
      "failure_mode": "breach_pressure_exposes_need_for_b3_repair_probe",
      "inbound_flux": 0.18,
      "internal_coherence": 0.842,
      "leakage_ratio": 0.148,
      "minimum_internal_support": 0.83,
      "outbound_flux": 0.16,
      "repair_score": 0.52,
      "retained_flux": 1.05,
      "row_decision": "partial"
    },
    "b3_c2_anchor_metrics": {
      "basin_separation_score": "not_evaluated_by_b3_c2",
      "boundary_stability_score": 0.78,
      "coherence_margin": 0.532,
      "failure_mode": "c2_flux_repair_not_general_repair",
      "inbound_flux": 0.34,
      "internal_coherence": 0.858,
      "leakage_ratio": 0.112,
      "minimum_internal_support": 0.852,
      "outbound_flux": 0.18,
      "repair_score": 0.74,
      "retained_flux": 1.29,
      "row_decision": "supported"
    },
    "b3_c4_delta_vs_b2_c4": {
      "boundary_stability_delta": 0.19,
      "coherence_margin_delta": 0.052,
      "leakage_ratio_delta": -0.03,
      "reclosure_score_delta": 0.24
    },
    "bounded_single_window_definition": "reclosure observed within one step of the three-snapshot selected-probe window",
    "breach_pressure": 0.38,
    "breach_reclosure_floor": 0.7,
    "generalizes_from_c2_flux_repair": true,
    "reclosure_latency_bucket": "bounded_single_window",
    "reclosure_latency_steps": 1,
    "reclosure_score": 0.76,
    "repair_score_relationship": "row repair_score intentionally carries C4 reclosure_score for this B3_C4 breach/reclosure probe",
    "selected_probe_window_snapshot_count": 3
  },
  "reclosure_score": 0.76,
  "repair_score": 0.76,
  "row_decision": "supported",
  "source_question": "Does the B3 mechanism that repaired C2 leakage also support breach/reclosure, or was it only flux-specific?"
}
```

## B4 C5 Separability Audit

```json
{
  "asymmetry_note": "B4_C5 tests whether basin A remains separable in the presence of basin B inside a shared medium; reverse basin perspective replay is deferred before final AP6",
  "basin_separation_score": 0.74,
  "boundary_exclusivity_score": 0.73,
  "claim_boundary": "B4_C5 is artifact-level shared-medium separability candidate evidence, not native multi-basin selfhood or final AP6",
  "leakage_into_neighbor_basin": 0.07,
  "merge_confusion_pressure": 0.14,
  "probe_decomposition": {
    "asymmetry_note": "B4_C5 tests whether basin A remains separable in the presence of basin B inside a shared medium; reverse basin perspective replay is deferred before final AP6",
    "basin_a_as_internal_side": true,
    "basin_separation_score": 0.74,
    "boundary_exclusivity_score": 0.73,
    "coupling_channel_attribution": "separated_from_intended_basin_retention",
    "leakage_into_neighbor_basin": 0.07,
    "leakage_ratio_relationship": "top-level leakage_ratio intentionally equals shared_medium_leakage for the C5 selected probe",
    "merge_confusion_pressure": 0.14,
    "neighbor_basin_treated_as_external_side": true,
    "redirected_flux_through_coupling_channel": 0.1,
    "shared_medium_leakage": 0.108
  },
  "row_decision": "supported",
  "shared_medium_leakage": 0.108,
  "source_question": "Can separate basins remain distinct inside a shared medium, or does coupling cause leakage, merge pressure, or boundary confusion?"
}
```

## Interpretation

`B0_C3` supports active-null false-positive rejection only. `B1_C2` preserves the weak-boundary flux replay. `B2_C1` preserves bounded noise tolerance only. `B3_C4` supports artifact-level breach/reclosure candidate evidence, answering that B3 generalizes beyond C2 flux repair under this constructed probe. `B4_C5` supports artifact-level shared-medium separability candidate evidence by measuring basin separation, neighbor leakage, merge pressure, shared-medium leakage, coupling attribution, and boundary exclusivity.

All rows keep `boundary_claim_allowed = false` and `final_ap6_supported = false`; Iteration 7 controls and claim classification remain required.

## Result Interpretation

This is a very strong Iteration 6 result. It does exactly what the selected interaction probe was supposed to do: it does not expand into a new full matrix, it runs only the five planned cells, and it answers the two open questions from Iterations 4-5 while keeping AP6 provisional.

### Main Read

The result now gives a clean post-I6 state:

```text id="i6-state"
B0_C3: supported as active-null false-positive rejection
B1_C2: partial weak-boundary replay under flux
B2_C1: supported persistent-noise replay
B3_C4: supported artifact-level breach/reclosure candidate
B4_C5: supported artifact-level shared-medium separability candidate
```

That is the right pattern. It preserves the earlier weak/partial controls while adding the two important positive extension rows: `B3_C4` and `B4_C5`.

### What Changed After Iteration 6

Before I6, the main open questions were:

```text id="i6-open-before"
Did B3 generalize from C2 flux repair to C4 breach/reclosure?
Did B4 resolve the C5 shared-medium separability problem?
```

The report answers both as `true`, but keeps them bounded as artifact-level candidate evidence, not final AP6, native repair, native support, selfhood, or agency.

That is exactly the right claim ceiling.

### B3_C4 Interpretation

`B3_C4` looks good. The breach/reclosure floor is `0.7`, the reclosure score is `0.76`, and the probe records that the mechanism generalizes from C2 flux repair under this constructed probe.

The important phrasing is:

```text id="b3-bound"
artifact-level breach/reclosure candidate evidence
not autonomous repair
not native reabsorption
not final AP6
```

So the supported claim is:

```text id="b3-claim"
B3 supplies bounded breach/reclosure candidate evidence under C4.
```

Not:

```text id="b3-blocked"
B3 proves autonomous repair.
B3 proves native repair.
B3 closes AP6.
```

That is clean.

### B4_C5 Interpretation

`B4_C5` is probably the biggest milestone in I6. It no longer relies on the B4 label; it measures separability directly through basin separation, boundary exclusivity, neighbor leakage, merge pressure, shared-medium leakage, redirected coupling flux, and coupling-channel attribution.

That resolves the concern from Iteration 5, where B4 improved retained flux but still had coupling/neighbor ambiguity. Here, B4 is supported specifically as:

```text id="b4-claim"
artifact-level shared-medium separability candidate evidence
```

Still blocked:

```text id="b4-blocked"
native multi-basin separability
multi-basin selfhood
final AP6
```

Again, this is the correct ceiling.

### Why This Is Strong

The strength is not that several rows are `supported`. The strength is that the supported rows are role-specific:

```text id="role-specific"
B0_C3 supports rejection, not boundary.
B2_C1 supports noise tolerance, not flux/repair/shared-medium.
B3_C4 supports breach/reclosure candidate, not autonomous repair.
B4_C5 supports artifact separability candidate, not native multi-basin selfhood.
```

That means Iteration 6 did not blur the ladder. It sharpened it.

### What Remains Before Closeout

The report is right to keep final AP6 blocked. The remaining blockers are now mostly control and classification blockers, not evidence-discovery blockers:

```text id="remaining"
full negative control matrix
duplicate and order-inversion replay
claim boundary classification
final AP6 closeout decision
```

The report explicitly keeps `boundary_claim_allowed = false`, `final_ap6_supported = false`, and says Iteration 7 controls and classification remain required.

### Recommended Next Step

Proceed to Iteration 7 full comparative requirements and control matrix.

The stance going into I7 should be:

```text id="i7-stance"
The evidence matrix has enough positive and negative structure to synthesize
requirements, but AP6 is still blocked until controls, replay, and claim
classification pass.
```

The most important I7 double-check will be:

```text id="i7-key"
Can the full control matrix break any of the supported I6 rows by relabeling,
hiding external state, injecting boundary labels, reversing order, or replaying
artifact-only?
```

If not, then I7 can legitimately convert the I3-I6 evidence into a controlled requirements matrix.

## Metric Construction Formulas

```json
{
  "basin_separation_score": {
    "policy": "B4_C5 explicit construction anchor measuring separation of the candidate basin from a neighbor basin inside a shared medium."
  },
  "boundary_exclusivity_score": {
    "policy": "B4_C5 explicit construction anchor for whether intended-basin membership remains distinct from neighbor and medium nodes."
  },
  "leakage_into_neighbor_basin": {
    "policy": "B4_C5 explicit construction anchor separating neighbor leakage from retained flux and shared-medium leakage."
  },
  "leakage_ratio": {
    "policy": "Leakage ratio is a challenge-specific normalized leakage score. For B4_C5 it intentionally aliases shared_medium_leakage because the selected C5 question is shared-medium leakage."
  },
  "merge_confusion_pressure": {
    "policy": "B4_C5 explicit construction anchor for pressure toward treating candidate and neighbor basins as one merged basin."
  },
  "metric_status": "Iteration 6 selected probes combine source-exact replay rows and explicit construction anchors. Retained flux is a composite retained signal index, not a probability and not globally bounded by 1.0.",
  "reclosure_score": {
    "formula": "For B3_C4, reclosure_score is the row-schema repair_score carrier applied to C4 breach/reclosure context.",
    "latency_bucket_definition": "bounded_single_window means reclosure is observed within the three-snapshot selected-probe window; reclosure_latency_steps records the numeric step count.",
    "relationship_to_repair_score": "intentional_alias_for_C4_reclosure"
  },
  "retained_flux": {
    "authoritative_value_policy": "The row retained_flux value is authoritative when marked as source_replay_preserved or explicit_construction_anchor; the projection is a cross-check, not a replacement.",
    "formula_projection_recorded": "For audit, each row records the diagnostic projection inbound_flux - outbound_flux + internal_coherence.",
    "source_replay_policy": "B1_C2 and B2_C1 preserve their source artifact retained_flux values exactly instead of recomputing them under a later formula."
  },
  "upstream_downstream_asymmetry_score": {
    "formula": "abs(inbound_flux - outbound_flux) / (inbound_flux + outbound_flux)",
    "rounding": "six decimal places",
    "zero_denominator_policy": "0.0"
  }
}
```

## Retained Flux Projection Audit

The projection audit records the diagnostic formula `inbound_flux - outbound_flux + internal_coherence` for every row. It is a transparency check; source replays and explicit construction anchors remain the authoritative row values.

```json
{
  "B0_C3": {
    "authoritative_value_policy": "explicit_construction_anchor",
    "diagnostic_formula": "inbound_flux - outbound_flux + internal_coherence",
    "diagnostic_projection": 0.0,
    "difference_recorded_minus_projection": 0.0,
    "formula_projection_is_authoritative": false,
    "recorded_retained_flux": 0.0
  },
  "B1_C2": {
    "authoritative_value_policy": "source_replay_preserved",
    "diagnostic_formula": "inbound_flux - outbound_flux + internal_coherence",
    "diagnostic_projection": 0.872,
    "difference_recorded_minus_projection": -0.112,
    "formula_projection_is_authoritative": false,
    "recorded_retained_flux": 0.76
  },
  "B2_C1": {
    "authoritative_value_policy": "source_replay_preserved",
    "diagnostic_formula": "inbound_flux - outbound_flux + internal_coherence",
    "diagnostic_projection": 0.882,
    "difference_recorded_minus_projection": 0.528,
    "formula_projection_is_authoritative": false,
    "recorded_retained_flux": 1.41
  },
  "B3_C4": {
    "authoritative_value_policy": "explicit_construction_anchor",
    "diagnostic_formula": "inbound_flux - outbound_flux + internal_coherence",
    "diagnostic_projection": 0.926,
    "difference_recorded_minus_projection": 0.294,
    "formula_projection_is_authoritative": false,
    "recorded_retained_flux": 1.22
  },
  "B4_C5": {
    "authoritative_value_policy": "explicit_construction_anchor",
    "diagnostic_formula": "inbound_flux - outbound_flux + internal_coherence",
    "diagnostic_projection": 1.012,
    "difference_recorded_minus_projection": 0.328,
    "formula_projection_is_authoritative": false,
    "recorded_retained_flux": 1.34
  }
}
```

## Replay Consistency Audit

```json
{
  "B1_C2": {
    "all_key_metrics_match": true,
    "metric_comparison": {
      "boundary_stability_score": {
        "matches": true,
        "replay": 0.34,
        "source": 0.34
      },
      "coherence_margin": {
        "matches": true,
        "replay": 0.442,
        "source": 0.442
      },
      "inbound_flux": {
        "matches": true,
        "replay": 0.34,
        "source": 0.34
      },
      "internal_coherence": {
        "matches": true,
        "replay": 0.812,
        "source": 0.812
      },
      "leakage_ratio": {
        "matches": true,
        "replay": 0.294,
        "source": 0.294
      },
      "outbound_flux": {
        "matches": true,
        "replay": 0.28,
        "source": 0.28
      },
      "retained_flux": {
        "matches": true,
        "replay": 0.76,
        "source": 0.76
      }
    },
    "replay_row_id": "n16_i6_row_b1_c2",
    "source_artifact": "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/n16_boundary_state_sweep_matrix.json",
    "source_row_id": "n16_i5_row_b1_c2"
  },
  "B2_C1": {
    "all_key_metrics_match": true,
    "metric_comparison": {
      "boundary_stability_score": {
        "matches": true,
        "replay": 0.9,
        "source": 0.9
      },
      "coherence_margin": {
        "matches": true,
        "replay": 0.532,
        "source": 0.532
      },
      "inbound_flux": {
        "matches": true,
        "replay": 0.03,
        "source": 0.03
      },
      "internal_coherence": {
        "matches": true,
        "replay": 0.872,
        "source": 0.872
      },
      "leakage_ratio": {
        "matches": true,
        "replay": 0.078,
        "source": 0.078
      },
      "outbound_flux": {
        "matches": true,
        "replay": 0.02,
        "source": 0.02
      },
      "retained_flux": {
        "matches": true,
        "replay": 1.41,
        "source": 1.41
      }
    },
    "replay_row_id": "n16_i6_row_b2_c1",
    "source_artifact": "experiments/2026-06-N16-lgrc-self-environment-boundary/outputs/n16_challenge_sweep_matrix.json",
    "source_row_id": "n16_i4_row_b2_c1"
  },
  "all_replay_rows_match_sources": true
}
```

## Cross-Iteration Metric Comparison

| Comparison | Source | Target | Result |
| --- | --- | --- | --- |
| B1_C2 replay identity | Iteration 5 B1_C2 | Iteration 6 B1_C2 | identical_replay |
| B2_C1 replay identity | Iteration 4 B2_C1 | Iteration 6 B2_C1 | identical_replay |
| B3_C2 repair to B3_C4 reclosure | Iteration 5 B3_C2 | Iteration 6 B3_C4 | B3_C4 records C4 breach/reclosure as an artifact-level candidate while preserving the B3_C2 repair claim ceiling |
| B2_C4 baseline to B3_C4 reclosure | Iteration 4 B2_C4 | Iteration 6 B3_C4 | B3_C4 improves the B2_C4 breach/reclosure baseline |

## Checks

```json
{
  "all_boundary_claims_false": true,
  "b0_c3_strict_false_positive_rejection": true,
  "b1_c2_replays_weak_boundary_partial": true,
  "b2_c1_noise_probe_decomposition_recorded": true,
  "b2_c1_replays_noise_tolerance_only": true,
  "b3_c4_answers_breach_reclosure": true,
  "b3_c4_inline_source_comparisons_recorded": true,
  "b3_c4_latency_numeric_grounding_recorded": true,
  "b3_c4_reclosure_alias_documented": true,
  "b3_c4_unlock_allowed": true,
  "b4_c5_answers_shared_medium_separability": true,
  "b4_c5_asymmetry_and_leakage_alias_documented": true,
  "b4_c5_decomposition_metrics_promoted": true,
  "b4_c5_does_not_inherit_separability_from_label": true,
  "boundary_trace_event_types_explicit": true,
  "i4_output_digest_matches_acceptance": true,
  "i5_output_digest_matches_acceptance": true,
  "metric_construction_formulas_recorded": true,
  "mvp_keeps_ap6_provisional": true,
  "replay_rows_match_source_metrics": true,
  "requirements_satisfied_and_failed_recorded": true,
  "retained_flux_projection_audit_recorded": true,
  "row_count_is_five": true,
  "selected_cells_only": true
}
```

## Output Digest

```text
20c90ead4f3c5c3621d940cf02d315a6ff398e85f053a928ad5f7ecd3f85106d
```
