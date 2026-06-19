# N19 Iteration 3 - Lower-Stack Candidate Classification

Status:

```text
status = passed
row_count = 6
phase8_ready_row_count = 1
phase8_opened = false
native_support_opened = false
```

Classification rows:

| Row | Source | Disposition | NAT | Decision | Phase 8 Ready | Surface |
| --- | --- | --- | --- | --- | --- | --- |
| n19_i3_row_01_n13_support_margin_response_policy_nat4 | N13 | phase8_ready_native_policy_candidate | NAT4 | supported | true | native_support_margin_and_response_magnitude_policy |
| n19_i3_row_02_n13_support_goal_selfhood_relabels_rejected | N13 | unsafe_relabel_rejected | NAT0 | rejected | false | not_applicable_relabel_rejected |
| n19_i3_row_03_n14_route_consequence_selection_contract_nat3 | N14 | native_contract_candidate | NAT3 | supported | false | native_route_consequence_selection_telemetry |
| n19_i3_row_04_n14_constructed_followout_native_support_blocker | N14 | implementation_gap_blocker | NAT2 | blocked | false | native_route_conditioned_support_regulation_observation_required |
| n19_i3_row_05_n15_proxy_derivation_contract_nat3 | N15 | native_contract_candidate | NAT3 | supported | false | native_proxy_derivation_policy |
| n19_i3_row_06_n15_proxy_goal_choice_relabels_rejected | N15 | unsafe_relabel_rejected | NAT0 | rejected | false | not_applicable_relabel_rejected |

Main interpretation:

```text
Iteration 3 finds one lower-stack Phase 8-ready native policy candidate: N13 support-margin/response-magnitude telemetry. N14 and N15 are stronger than scaffolds because their native contracts are clear and source-backed, but they remain NAT3: N14 is limited by the constructed-followout versus observed route-conditioned support/regulation gap, and N15 depends on artifact lower-stack inputs that are not yet native surfaces.
```

Lower-stack result:

```json
{
  "blocked_rows": [
    "n19_i3_row_04_n14_constructed_followout_native_support_blocker"
  ],
  "classified_sources": [
    "N13",
    "N14",
    "N15"
  ],
  "lower_stack_phase8_ready_surfaces": [
    "native_support_margin_and_response_magnitude_policy"
  ],
  "n13_classification": "NAT4 phase8-ready native policy candidate",
  "n14_classification": "NAT3 native contract candidate plus route-conditioned support/regulation blocker",
  "n15_classification": "NAT3 native contract candidate plus unsafe proxy/goal relabel rejection",
  "nat3_rows": [
    "n19_i3_row_03_n14_route_consequence_selection_contract_nat3",
    "n19_i3_row_05_n15_proxy_derivation_contract_nat3"
  ],
  "nat4_rows": [
    "n19_i3_row_01_n13_support_margin_response_policy_nat4"
  ],
  "native_contract_surfaces": [
    "native_route_consequence_selection_telemetry",
    "native_proxy_derivation_policy"
  ],
  "phase8_ready_row_count": 1,
  "rejected_rows": [
    "n19_i3_row_02_n13_support_goal_selfhood_relabels_rejected",
    "n19_i3_row_06_n15_proxy_goal_choice_relabels_rejected"
  ]
}
```

Checks:

| Check | Passed |
| --- | --- |
| source_inventory_passed | true |
| schema_freeze_passed | true |
| required_lower_stack_rows_present | true |
| all_required_schema_fields_present | true |
| primary_dispositions_valid_and_singular | true |
| nat_levels_valid | true |
| row_decisions_valid | true |
| phase8_ready_derivation_enforced | true |
| nat4_rows_have_all_gates_passed | true |
| nat3_rows_keep_phase8_ready_false | true |
| nat3_rows_have_explicit_nat4_gate_blocker | true |
| claim_flags_forced_false_all_rows | true |
| phase8_and_native_support_not_opened | true |
| source_digests_present | true |
| constructed_followout_not_promoted_to_observed_native_support | true |
| n12_readiness_only_context_not_relabelled_as_native_support | true |
| unsafe_goal_choice_selfhood_agency_promotions_rejected | true |
| no_absolute_paths | true |
| src_diff_empty_recorded_true | true |
