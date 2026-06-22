# N20 Iteration 4 - Continuation Function / Proxy / Scaffold Contract

Status:

```text
status = passed
acceptance_state = accepted_native_function_proxy_scaffold_contract_no_primitive_evidence
row_count = 9
primitive_evidence_opened = false
native_function_descriptors_defined = true
proxy_metric_definitions_defined = true
support_scaffold_declarations_defined = true
rows_marked_complete = false
```

Interpretation:

Iteration 4 defines bounded continuation-function, proxy, and support/scaffold contracts. It does not test any primitive and does not mark any primitive complete; I5 still owns same-basin criteria and the full control contract.

Primitive contracts:

| Primitive | Contract Status | Proxy Metric | Support/Scaffold | AP Gaps |
| --- | --- | --- | --- | --- |
| withdrawal_resistance | incomplete_missing_same_basin_rule | support_coherence_survival_margin | 2 declared supports | none |
| naturalization_depth | incomplete_missing_same_basin_rule | post_probe_persistence_margin | 2 declared supports | none |
| susceptibility_update | incomplete_missing_same_basin_rule | susceptibility_delta_replay_margin | 2 declared supports | AP4, AP5 conditional |
| live_continuation_collapse | incomplete_missing_same_basin_rule | branch_collapse_geometry_margin | 2 declared supports | AP4, AP5 conditional |
| surplus_supported_optionality | incomplete_missing_same_basin_rule | surplus_optional_branch_capacity | 2 declared supports | none |
| spark_sub_basin_new_basin_formation | incomplete_missing_same_basin_rule | basin_distinguishability_persistence_margin | 2 declared supports | none |
| proxy_divergence_proxy_collapse | incomplete_missing_same_basin_rule | proxy_basin_coupling_gap | 2 declared supports | AP5 |
| configuration_substrate_transfer | incomplete_missing_same_basin_rule | transfer_signature_preservation_margin | 2 declared supports | AP4 conditional |
| generative_extractive_persistence | incomplete_missing_same_basin_rule | generative_capacity_delta_margin | 2 declared supports | none |

N21 handoff inputs:

```json
[
  {
    "coherence_floor": "coherence remains above declared withdrawal floor",
    "declared_supports": [
      "support_coherence_floor_trace",
      "boundary_integrity_trace"
    ],
    "hidden_support_blocker": "fail closed if support or scaffold is preserved by an undeclared producer surface",
    "primitive_id": "withdrawal_resistance",
    "probe_absent_condition": "declared support/scaffold weakened or absent after withdrawal",
    "probe_present_condition": "declared support/scaffold present before withdrawal",
    "proxy_only_success_blocker": "proxy improves while basin continuation fails -> primitive not supported",
    "support_floor": "support remains above declared withdrawal floor",
    "withdrawal_condition": "declared support is weakened or removed in a bounded window"
  },
  {
    "coherence_floor": "post-probe coherence remains above declared residual floor",
    "declared_supports": [
      "post_probe_support_floor_trace",
      "post_probe_coherence_floor_trace"
    ],
    "hidden_support_blocker": "fail closed if support or scaffold is preserved by an undeclared producer surface",
    "primitive_id": "naturalization_depth",
    "probe_absent_condition": "original probe/scaffold absent with residual replay",
    "probe_present_condition": "original probe/scaffold present",
    "proxy_only_success_blocker": "proxy improves while basin continuation fails -> primitive not supported",
    "support_floor": "post-probe support remains above declared residual floor",
    "withdrawal_condition": "original probe/scaffold is removed or disabled"
  }
]
```

Proxy-only fail-closed rule:

```text
A proxy metric can be an indicator only. If the proxy improves while the continuation function, declared basin signature, support floor, coherence floor, boundary condition, or flux condition fails, the primitive is not supported.
```

Checks:

| Check | Passed |
| --- | --- |
| source_ledger_passed_and_not_primitive_evidence | true |
| all_expected_primitives_have_contract_rows | true |
| continuation_descriptors_defined_geometric | true |
| proxy_metrics_defined_as_signs_not_replacements | true |
| proxy_only_success_blockers_defined | true |
| blocked_relabels_not_used_as_proxy_metrics | true |
| support_scaffold_declarations_defined | true |
| ap4_ap5_dependencies_carried_forward_locally | true |
| rows_remain_incomplete_until_iteration5 | true |
| primitive_specific_descriptors_distinct | true |
| n21_handoff_inputs_present | true |
| unsafe_claim_flags_false_per_row | true |
| artifact_invariants_preserved | true |
| no_primitive_evidence_opened | true |
| no_absolute_paths | true |

Claim boundary:

```text
N20 Iteration 4 defines contract objects only. It does not test or support withdrawal resistance, naturalization depth, susceptibility update, live-continuation collapse, optionality, spark/new-basin formation, proxy collapse, transfer, generative persistence, agency, Phase 8, native support, sentience, or semantic function.
```
