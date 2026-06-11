# N07 Iteration 5: ID3 Attractivity / Flux Convergence

Status: passed.

Command:

```bash
.venv/bin/python experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/run_n07_iteration_5_id3_attractivity_candidate.py
```

Iteration 5 applies the manifest-declared flux-convergence metric to the
Iteration 4 stable-basin candidate. It records runtime-visible packet-work
events from the declared neighborhood U into the support area, verifies exact
budget/nonnegative state, and rejects hidden route-context steering. It does
not claim native attractor-neighborhood support, agency, identity acceptance,
invariance, reflexive closure, or compatibility.

This is a first-pass ID3 attractivity candidate. Iteration 5-B is reserved for
multi-source, multi-window attractivity stress before the experiment advances
to invariance.

## Flux Convergence Record

```json
{
  "attractivity_gate": "pass",
  "budget_after": 6.0,
  "budget_before": 6.0,
  "budget_error": 0.0,
  "budget_surface": "node_plus_packet",
  "flux_convergence_idempotency_key": {
    "event_time_key": "n07_i5_t2_flux_convergence_window",
    "flux_metric_id": "n07_flux_convergence_to_support_v1",
    "neighborhood_U_digest": "c9a63c87b120554882f09fb3f3f8c010425735395909b3a65e336ee5e9578a05",
    "scheduler_event_index": 2,
    "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb"
  },
  "flux_convergence_idempotency_key_digest": "ca5cfbeee0d748f66228d44986810ed141156b164b0d816bdf583120ccff4aed",
  "flux_convergence_record_digest": "e82c31e97d2441214168554a6c49ad562090733010316481b7cda2e4ad5efa3f",
  "flux_convergence_record_digest_input": {
    "event_time_key": "n07_i5_t2_flux_convergence_window",
    "formula": "net_flux_into_support_from_U > net_flux_out_of_support",
    "metric_id": "n07_flux_convergence_to_support_v1",
    "neighborhood_U_digest": "c9a63c87b120554882f09fb3f3f8c010425735395909b3a65e336ee5e9578a05",
    "net_flux_convergence_margin": 0.24,
    "net_flux_into_support_from_U": 0.3,
    "net_flux_out_of_support": 0.06,
    "packet_work_events_digest": "c8ca479ba4d4e68a12c54b729f9b68de773f699aff7ee82214531de24499c079",
    "positive_threshold": 0.0,
    "runtime_visible_inputs": [
      "neighborhood_U",
      "packet_work_events",
      "surface_rows",
      "budget_surface"
    ],
    "scheduler_event_index": 2,
    "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
    "surface_rows_consumed": [
      {
        "source_iteration": 3,
        "surface_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
        "surface_kind": "support_area"
      },
      {
        "source_iteration": 4,
        "surface_digest": "3dc60c7f6e60f429bbd0cbb86cf677337ec9386f3ca4a22e1b9556b9308835c0",
        "surface_kind": "stability_proxy"
      }
    ]
  },
  "flux_metric_id": "n07_flux_convergence_to_support_v1",
  "formula": "net_flux_into_support_from_U > net_flux_out_of_support",
  "hidden_route_context_steering_used": false,
  "metric_controls": [
    "non_attractive_flux",
    "wrong_polarity",
    "subthreshold_flux",
    "wrong_basin"
  ],
  "min_active_node_coherence": 0.0,
  "min_packet_amount": 0.06,
  "native_policy_available": false,
  "native_policy_blocker": "native_attractor_neighborhood_policy_missing",
  "neighborhood_U_digest": "c9a63c87b120554882f09fb3f3f8c010425735395909b3a65e336ee5e9578a05",
  "net_flux_convergence_margin": 0.24,
  "net_flux_into_support_from_U": 0.3,
  "net_flux_out_of_support": 0.06,
  "nonnegative_state_passed": true,
  "packet_work_events_digest": "c8ca479ba4d4e68a12c54b729f9b68de773f699aff7ee82214531de24499c079",
  "polarity": "toward_support",
  "positive_threshold": 0.0,
  "preselected_by_fixture_label": false,
  "record_id": "n07_i5_flux_convergence_record_v1",
  "record_kind": "experiment_local_flux_convergence_record",
  "report_side_only": false,
  "runtime_visible": true,
  "runtime_visible_inputs": [
    "neighborhood_U",
    "packet_work_events",
    "surface_rows",
    "budget_surface"
  ],
  "source_backed": true,
  "source_observation_event_digest": "ec0baa495c66ba5112b426f04c0b33cef56ce9082ba0ee62ccde5292a5176eab",
  "source_observation_event_id": "n07_i5_flux_observation_event_0001",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "wrong_basin_node_ids_observed": []
}
```

## Candidate Row

```json
{
  "activity_history_digest": "ab925ec070dbe47e2e65c816d96bc576513bbe5840678cf7d0098a48ed314c9c",
  "agency_claim_allowed": false,
  "attractivity_is_agency_claim": false,
  "becoming_class_status": "observation_tag",
  "boundary_rung": "structured_consequence",
  "candidate_identity_carrier_type": "coherence_basin",
  "claim_ceiling": "attractor_candidate",
  "claim_flags": {
    "agency_claim_allowed": false,
    "agentic_like_claim_allowed": false,
    "ant_colony_claim_allowed": false,
    "biological_claim_allowed": false,
    "goal_proxy_regulation_claim_allowed": false,
    "identity_acceptance_claim_allowed": false,
    "intention_claim_allowed": false,
    "locomotion_like_claim_allowed": false,
    "memory_or_trail_claim_allowed": false,
    "movement_claim_allowed": false,
    "personhood_claim_allowed": false,
    "rc_identity_collapse_claim_allowed": false,
    "semantic_choice_claim_allowed": false,
    "unrestricted_identity_claim_allowed": false,
    "unrestricted_movement_claim_allowed": false
  },
  "composite_topology_id": null,
  "derived_id_ceiling": "ID3",
  "experiment_local_observables_used": [
    "n07_i5_flux_observation_event_0001",
    "n07_i5_flux_convergence_record_v1"
  ],
  "flux_convergence_record_digest": "e82c31e97d2441214168554a6c49ad562090733010316481b7cda2e4ad5efa3f",
  "flux_convergence_record_id": "n07_i5_flux_convergence_record_v1",
  "gate_vector": {
    "artifact_replay": "not_measured",
    "attractivity": "pass",
    "compatibility": "not_measured",
    "invariance": "not_measured",
    "lineage_current": "not_applicable",
    "reflexive_closure": "not_measured",
    "stability": "pass",
    "support": "pass"
  },
  "id_level": "ID3",
  "identity_acceptance_claim_allowed": false,
  "identity_carrier_surface": "runtime_coherence_basin",
  "implementation_surface": "experiment_local_identity_gate_record",
  "native_observables_used": [
    "manifest_declared_lgrc_node_ids",
    "manifest_declared_lgrc_edge_ids",
    "node_plus_packet_budget_accounting"
  ],
  "native_policy_blockers": [
    "native_attractor_neighborhood_policy_missing"
  ],
  "native_support_status": "experiment_local",
  "naturalization_rung": "Nat0_probe_dependent_expression",
  "primary_blocker": null,
  "probe_role": "diagnostic_probe",
  "row_id": "n07_i5_id3_attractivity_candidate_row_v1",
  "runtime_family": "LGRC9V3",
  "source_artifact_sha256": {
    "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26",
    "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json": "bd5eb02a7ba419d6837340b46c537e5201353aa27e9619abbe7aaa1886bce97c"
  },
  "source_artifacts": [
    {
      "name": "n07_fixture_manifest_v1",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/configs/n07_fixture_manifest_v1.json",
      "sha256": "e40f383520c95e3587be70d588e6f126d82f35e093ecb53e0d4e3ed5a0715603"
    },
    {
      "name": "n07_iteration_2_fixture_manifest_validation",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_2_fixture_manifest_validation.json",
      "sha256": "b27cd665aec68f992632f3198e83794852ff645e1996e2edd1f1497f15f9fd26"
    },
    {
      "id2_candidate_row_digest": "5370ea86856620fa283c12a1a1f2ae2dda7cb031511b6c3e7bd7918c44fa8226",
      "name": "n07_iteration_4_id2_stability_candidate",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/outputs/n07_iteration_4_id2_stability_candidate.json",
      "sha256": "bd5eb02a7ba419d6837340b46c537e5201353aa27e9619abbe7aaa1886bce97c",
      "stability_proxy_record_digest": "3dc60c7f6e60f429bbd0cbb86cf677337ec9386f3ca4a22e1b9556b9308835c0",
      "status": "passed"
    }
  ],
  "source_reports": [
    {
      "name": "n07_iteration_4_id2_stability_candidate_report",
      "path": "experiments/2026-05-N07-rc-identity-attractor-invariance/reports/n07_iteration_4_id2_stability_candidate.md",
      "sha256": "e5e07fe53c9028247d376ee1947788ca20db3328893202752b95ce1c0708ce4f"
    }
  ],
  "stability_record_digest": "069482b59919fe556e2d7c266f8cdc145f365c872bd0c205676877aeff1ce83d",
  "stability_record_id": "n07_i4_stability_proxy_record_v1",
  "support_area_digest": "ec0ec6111ecc42a4cde4c91a96d24c87792a5a149f9ea9e8ac99529824e26deb",
  "support_area_id": "n07_support_area_A_v1",
  "support_dependency_status": "probe_dependent",
  "topology_family_id": "n07_T3_attractor_neighborhood",
  "visual_is_evidence_source": false,
  "visual_reference": null,
  "withdrawal_test_status": "not_tested"
}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
| `non_attractive_flux` | `blocked` | `non_attractive_flux` | `ID2` |
| `wrong_basin` | `blocked` | `wrong_basin` | `ID2` |
| `wrong_polarity` | `blocked` | `wrong_polarity` | `ID2` |
| `subthreshold_flux` | `blocked` | `subthreshold_flux` | `ID2` |
| `hidden_route_context_steering` | `blocked` | `hidden_route_context_steering` | `ID2` |
| `budget_discontinuity` | `blocked` | `budget_discontinuity` | `ID2` |

## Checks

| Check | Passed |
|---|---:|
| `attractivity_not_agency_claim` | `True` |
| `becoming_method_values_allowed` | `True` |
| `budget_exact` | `True` |
| `candidate_carrier_is_coherence_basin` | `True` |
| `candidate_gate_matches_manifest` | `True` |
| `candidate_primary_metric_matches_manifest` | `True` |
| `candidate_target_id_matches_manifest` | `True` |
| `candidate_topology_family_matches_manifest` | `True` |
| `claim_flag_keys_match_manifest` | `True` |
| `claim_flags_all_false` | `True` |
| `control_blockers_distinct` | `True` |
| `control_ceilings_id2` | `True` |
| `controls_blocked` | `True` |
| `derived_ceiling_id3` | `True` |
| `evidence_only_surfaces_not_promoted` | `True` |
| `flux_convergence_passed` | `True` |
| `flux_events_runtime_visible` | `True` |
| `flux_margin_recomputed` | `True` |
| `flux_metric_formula_matches_manifest` | `True` |
| `flux_metric_inputs_match_manifest` | `True` |
| `flux_native_policy_fields_match_manifest` | `True` |
| `flux_nodes_are_members_of_neighborhood_u` | `True` |
| `gate_vector_schema_matches_manifest` | `True` |
| `identity_acceptance_blocked` | `True` |
| `manifest_flux_controls_exercised` | `True` |
| `native_support_not_overstated` | `True` |
| `neighborhood_u_matches_manifest` | `True` |
| `no_hidden_route_context_steering` | `True` |
| `no_src_changes_required` | `True` |
| `nonnegative_state_passed` | `True` |
| `not_preselected_by_fixture_labels` | `True` |
| `packet_event_ids_unique` | `True` |
| `packet_routes_follow_manifest_edges` | `True` |
| `required_controls_present` | `True` |
| `source_id2_status_passed` | `True` |
| `source_id2_support_and_stability_passed` | `True` |
| `status_passed` | `True` |

## Artifact Digests

```json
{
  "checks_digest": "20d7aa05c27236aa7076dd45b92eb87c967af10bc15c85ae76cd28847e6750d7",
  "claim_boundary_digest": "e4b3ea6782a52982d160df9757cbebf399c7385f93ab8bba634022acb9462388",
  "control_rows_digest": "ebc029486a0c77ab24f81512c6885e1ff036f0fc0374cfa7de1a0df9c1c96205",
  "flux_convergence_record_digest": "3c65623498c011abe71ce795308152a258f5944229944750a335b5c02497f526",
  "flux_observation_event_digest": "ec0baa495c66ba5112b426f04c0b33cef56ce9082ba0ee62ccde5292a5176eab",
  "id3_candidate_row_digest": "ccc285afc59abcad2c07fb1f75009a42400f5ce2357a4adb7d796536fd677177",
  "source_id2_output_digest": "7a1c97c34f495bffd93db211b04842e8f910e154a5ef4a67e296194808b2ba1b"
}
```

## Acceptance

Iteration 5 passes because flux from the declared runtime-visible neighborhood
converges into the stable support area under exact node-plus-packet budget
accounting and nonnegative state. The result is capped at ID3/attractor
candidate, remains experiment-local because native attractor-neighborhood
policy support is not available, and all identity-acceptance, agency, movement,
biological, and unrestricted claim flags remain false.
