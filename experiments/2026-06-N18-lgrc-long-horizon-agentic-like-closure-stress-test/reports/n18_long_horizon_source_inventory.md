# N18 Long-Horizon Source Inventory

Status: `passed`

Acceptance state: `accepted_long_horizon_source_inventory_only_no_ap8`

Output digest: `b9e45e7fb4e2c90fac206e1b2c666b425eec18b02bee6cd48685fc705000a2bf`

## Summary

Iteration 1 pins the old-best source artifacts and freezes the initial AP8
contract. It does not run a long-horizon stress test and it does not
support final AP8.

```text
source_rows = 12
direct_historic_ap8_evidence_exists = false
ap8_candidate_allowed = false
final_ap8_supported = false
phase8_opened = false
native_support_opened = false
```

## Contribution Summary

```json
{
  "boundary_separation": 4,
  "closed_loop_feedback": 4,
  "long_horizon": 2,
  "memory_context": 7,
  "proxy_target": 4,
  "regulation": 8,
  "selection_context": 5,
  "support_state": 7
}
```

## Source Rows

| Row | Source | Role | Claim Ceiling | AP8 Direct |
| --- | --- | --- | --- | --- |
| `n18_i1_row_01_n17_closeout_ap7` | `N17` | final AP7 closed boundary engagement loop handoff | `artifact_level_ap7_closed_boundary_engagement_loop_candidate` | `False` |
| `n18_i1_row_02_n17_requirements_matrix` | `N17` | closed-loop requirements and final AP7 classification basis | `artifact_level_ap7_closed_boundary_engagement_loop_candidate_pending_closeout` | `False` |
| `n18_i1_row_03_n17_replay_control_matrix` | `N17` | AP7 replay/order/hidden-state control source | `artifact_level_ap7_loop_candidate_pending_later_stress` | `False` |
| `n18_i1_row_04_n17_claim_boundary_record` | `N17` | AP7 unsafe promotion blocker | `artifact_level_ap7_claim_boundary_clean` | `False` |
| `n18_i1_row_05_n16_closeout_ap6` | `N16` | final AP6 boundary separability handoff | `artifact_level_ap6_self_environment_boundary_candidate_with_controlled_basin_boundary_requirements` | `False` |
| `n18_i1_row_06_n15_closeout_ap5` | `N15` | final AP5 proxy/target context | `artifact_level_ap5_endogenous_proxy_formation_candidate` | `False` |
| `n18_i1_row_07_n14_closeout_ap4` | `N14` | final AP4 consequence-sensitive route selection context | `artifact_level_ap4_consequence_sensitive_route_selection_candidate_with_constructed_route_conditioned_support_regulation_followout` | `False` |
| `n18_i1_row_08_n13_closeout_ap3` | `N13` | final AP3 support-seeking regulation context | `artifact_level_ap3_self_maintenance_candidate_support_seeking_regulation` | `False` |
| `n18_i1_row_09_n12_closeout_nat4` | `N12` | NAT4 readiness handoff | `NAT4 readiness-only native absorption context` | `False` |
| `n18_i1_row_10_n12_phase8_readiness` | `N12` | Phase 8 readiness contract context | `NAT4 readiness-only Phase 8 contract context` | `False` |
| `n18_i1_row_11_n08_memory_closeout` | `N08` | memory/trail context | `memory_context_only` | `False` |
| `n18_i1_row_12_n09_regulation_closeout` | `N09` | bounded regulation context | `bounded_regulation_context_only` | `False` |

## Interpretation

The strongest source is N17 AP7, but N17 explicitly hands off long-
horizon closure stress testing to N18. N18 therefore starts with a
source-backed AP7 loop substrate, AP6 boundary separation, AP5 proxy
context, AP4 selection context, AP3 support regulation, readiness-only
N12 context, and N08/N09 memory/regulation context. None of those rows
is direct AP8 evidence by itself.

## Checks

| Check | Passed | Detail |
| --- | --- | --- |
| `all_source_artifacts_exist` | `True` | `[]` |
| `all_source_reports_exist` | `True` | `[]` |
| `all_source_json_parseable` | `True` | `{}` |
| `all_source_digests_recorded` | `True` | `[]` |
| `expected_source_lanes_present` | `True` | `[]` |
| `contribution_axes_valid` | `True` | `[]` |
| `direct_historic_ap8_evidence_absent` | `True` | `[]` |
| `no_final_ap8_claim` | `True` | `"Iteration 1 is inventory and contract only."` |
| `unsafe_claim_flags_false` | `True` | `{"agency_claim_opened": false, "fully_native_integration_opened": false, "identity_acceptance_opened": false, "intention_claim_opened": false, "native_support_opened": false, "organism_life_opened": false, "phase8_opened": false, "selfhood_claim_opened": false, "semantic_action_opened": false, "semantic_goal_ownership_opened": false, "semantic_perception_opened": false, "unrestricted_agency_opened": false}` |
| `no_absolute_paths` | `True` | `"portable relative paths only"` |
