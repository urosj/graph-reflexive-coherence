# Prototype D I14-B Direct Runtime Candidate Controls

## Result

```text
status = passed
acceptance_state = accepted_direct_runtime_candidate_controls_fail_closed_pending_i14c
canonical_i14a_output_digest = aeb89e95e03cf7f64e395375db8012b4b603491a7dfc1bc95c32ae55a46923cc
control_count = 30
failed_closed_count = 30
failed_open_count = 0
surviving_candidate_count = 3
control_backed_runtime_support_claim_allowed = false
ready_for_i14c_replay_stress = true
output_digest = 84ecb67648b879e82c123ca4f8f8f57dd38abf0deb602f03902f6a820a7a0c83
```

## Interpretation

I14-B is a control gate, not replay/stress support. It rejects the false-positive paths for all three direct candidates and keeps each surviving row as a candidate pending I14-C.

The N28 relabel control is scoped narrowly: copying an N28 label fails closed, but consuming N28 source-current traces remains allowed when the N29 row has its own artifact, manifest, threshold record, lineage audit, and claim boundary.

## Candidate Summary

| Candidate | Status | Notes |
| --- | --- | --- |
| `n29_i14_1_generative_enrichment_motif` | `admissible_for_i14c_replay_stress` | `reduce_neighbor_gain_below_threshold_reject_or_demote` |
| `n29_i14_2_extractive_depletion_motif` | `admissible_for_i14c_replay_stress_with_leakage_exceedance_caveat` | `distinguish_extractive_mechanism_exceedance_from_leakage_collapse` |
| `n29_i14_3_processor_redistribution_motif` | `admissible_for_i14c_replay_stress` | `remove_one_lobe_or_flatten_lobe_opposition_reject_or_demote` |

## Controls

| Candidate | Control | Status |
| --- | --- | --- |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_label_only_medium_reshaping_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_report_only_as_runtime_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_visual_only_as_runtime_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_focal_survival_only_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_aggregate_only_redistribution_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_hidden_producer_state_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_n28_relabel_as_n29_runtime_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_resource_economy_relabel_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_cooperation_exploitation_relabel_control` | `failed_closed` |
| `n29_i14_1_generative_enrichment_motif` | `prototype_d_total_coherence_visualization_overclaim_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_label_only_medium_reshaping_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_report_only_as_runtime_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_visual_only_as_runtime_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_focal_survival_only_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_aggregate_only_redistribution_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_hidden_producer_state_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_n28_relabel_as_n29_runtime_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_resource_economy_relabel_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_cooperation_exploitation_relabel_control` | `failed_closed` |
| `n29_i14_2_extractive_depletion_motif` | `prototype_d_total_coherence_visualization_overclaim_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_label_only_medium_reshaping_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_report_only_as_runtime_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_visual_only_as_runtime_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_focal_survival_only_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_aggregate_only_redistribution_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_hidden_producer_state_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_n28_relabel_as_n29_runtime_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_resource_economy_relabel_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_cooperation_exploitation_relabel_control` | `failed_closed` |
| `n29_i14_3_processor_redistribution_motif` | `prototype_d_total_coherence_visualization_overclaim_control` | `failed_closed` |

## Claim Boundary

Runtime support, Prototype D success, resource economy, cooperation, exploitation, biological agency, native support, and agentic ecology runtime success remain blocked.
