# N17 Iteration 8 - Shared-Medium Reciprocal Loop

Artifact: `n17_shared_medium_reciprocal_loop`
Status: `passed`
Acceptance state: `accepted_local_one_sided_shared_medium_g6_candidate_no_final_ap7`
Output digest: `18302290f9cf14eed2ae93a0db27ce5c88ccc5769c4c36e2989c753880b069db`

## Main Result

Iteration 8 tests whether the N16 B4/C5 shared-medium separability source can support a local one-sided N17 G6 shared-medium reciprocal candidate without basin merge. The result is artifact-level, narrow, and one-sided; it does not support general shared-medium G6, reverse-perspective shared-medium replay, symmetric native multi-basin selfhood, or final AP7.

```text
current_evidence_rung = G6_local_one_sided_shared_medium_reciprocal_candidate
shared_medium_extension_supported = true
local_one_sided_shared_medium_g6_candidate_supported = true
general_shared_medium_g6_supported = false
reverse_perspective_shared_medium_replay_supported = false
symmetric_shared_medium_replay_supported = false
full_comparative_ap7_classification_supported = false
final_ap7_supported = false
```

## Shared-Medium Envelope

```text
basin_separation_min_supported = 0.74
boundary_exclusivity_min_supported = 0.73
shared_medium_leakage_max_supported = 0.108
neighbor_leakage_max_supported = 0.07
merge_confusion_pressure_max_supported = 0.14
redirected_flux_through_coupling_channel_supported = 0.1
shared_medium_leakage_over_ceiling_status = rejected
merge_pressure_over_ceiling_status = rejected
neighbor_leakage_as_retention_status = rejected
symmetric_native_relabel_status = rejected
```

## Geometric And Flux Interpretation

Basin A remains the derived internal side, the shared medium and neighbor basin remain the derived external side, and reciprocal closure is admitted only while basin separation and boundary exclusivity stay above their B4/C5 floors.

The supported reciprocal path uses the B4/C5 shared-medium boundary exchange and coupling-channel attribution: shared-medium pressure is present, response-attributed redirected flux changes the medium, and later boundary state is conditioned by that changed medium without counting neighbor leakage as retention. This is not yet a reverse-perspective or general shared-medium robustness result.

```text
basin_a_to_shared_medium_edge_weight = 0.1
neighbor_to_shared_medium_edge_weight = 0.08
redirected_flux_through_coupling_channel = 0.1
basin_separation_margin = 0.04
boundary_exclusivity_margin = 0.03
shared_medium_leakage_margin_to_ceiling = 0.012
merge_confusion_margin_to_ceiling = 0.06
internal_support_margin = 0.004
coherence_margin_above_floor = 0.032
```

This is one-sided artifact-level shared-medium reciprocity. It is not symmetric native multi-basin replay, not basin merge, not general shared-medium G6 robustness, not agency, and not final AP7.

## Rows

| Row | Probe | Decision | Claim Allowed | Shared Leakage | Merge Pressure |
| --- | --- | --- | --- | --- | --- |
| `n17_i8_row_01_b4_c5_shared_medium_reciprocal_anchor` | `b4_c5_shared_medium_reciprocal_anchor` | `supported` | `true` | `0.108` | `0.14` |
| `n17_i8_row_02_shared_medium_neighbor_feedback_path` | `shared_medium_neighbor_feedback_path` | `supported` | `true` | `0.108` | `0.14` |
| `n17_i8_row_03_coupling_channel_attribution_path` | `coupling_channel_attribution_path` | `supported` | `true` | `0.108` | `0.14` |
| `n17_i8_row_04_b2_c5_shared_medium_pressure_control` | `b2_c5_shared_medium_pressure_control` | `rejected` | `false` | `0.18` | `0.28` |
| `n17_i8_row_05_b4_c2_flux_distribution_not_c5_control` | `b4_c2_flux_distribution_not_c5_control` | `partial` | `false` | `0.294` | `0.23` |
| `n17_i8_row_06_shared_medium_leakage_over_ceiling_control` | `shared_medium_leakage_over_ceiling_control` | `rejected` | `false` | `0.13` | `0.14` |
| `n17_i8_row_07_merge_pressure_over_ceiling_control` | `merge_pressure_over_ceiling_control` | `rejected` | `false` | `0.108` | `0.24` |
| `n17_i8_row_08_neighbor_leakage_as_retention_relabel_control` | `neighbor_leakage_as_retention_relabel_control` | `rejected` | `false` | `0.108` | `0.14` |
| `n17_i8_row_09_missing_changed_shared_medium_feedback_control` | `missing_changed_shared_medium_feedback_control` | `rejected` | `false` | `0.108` | `0.14` |
| `n17_i8_row_10_shared_medium_label_only_relabel_control` | `shared_medium_label_only_relabel_control` | `rejected` | `false` | `0.108` | `0.14` |
| `n17_i8_row_11_symmetric_native_multi_basin_relabel_control` | `symmetric_native_multi_basin_relabel_control` | `rejected` | `false` | `0.108` | `0.14` |

## Interpretation

I8 supports a local one-sided G6 candidate at artifact extension scope. The supported rows show B4/C5 shared-medium closure, neighbor/later feedback through the medium, and coupling-channel attribution while preserving basin separation and boundary exclusivity. This does not establish general G6 robustness: the margins remain narrow, the source anchor is B4/C5, and reverse-perspective shared-medium replay is still unsupported. The controls fail closed when B2/C5 is relabeled as enough, when B4/C2 flux is relabeled as C5 separability, when leakage or merge pressure exceeds policy, when neighbor leakage is counted as intended retention, when changed shared-medium feedback is missing, when a label-only loop is attempted, or when one-sided B4/C5 is promoted to symmetric/native multi-basin claims.

The clean I9 role is a local one-sided artifact-level G6 shared-medium reciprocal candidate. It does not support general shared-medium G6, reverse-perspective shared-medium replay, symmetric shared-medium replay, native multi-basin selfhood, semantic action/perception, agency, full comparative AP7, or final AP7.

## Checks

- `b4_c5_source_supported`: pass
- `supported_g6_rows_present`: pass
- `controls_fail_closed`: pass
- `supported_rows_keep_trace_contract`: pass
- `shared_medium_envelope_recorded`: pass
- `unsafe_claim_flags_false`: pass
- `final_ap7_still_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
