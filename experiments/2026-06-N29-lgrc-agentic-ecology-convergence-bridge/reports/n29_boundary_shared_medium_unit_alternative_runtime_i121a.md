# Prototype B - Alternative Runtime Unit Extraction

Status: `passed`

Acceptance state: `accepted_alternative_exact_runtime_unit_extraction_pending_controls_replay_stress`

Output digest: `0c3cb123e7245747705de79d2e732e962de014882fdf5fae7d668b152b189dd4`

## Alternative Runtime Unit

Unit: `N29.I12.1A.BOUNDARY_SHARED_MEDIUM_UNIT.RUNTIME.001`

Basin side: `child_basin_core_2`

Shared/adjacent medium: `source_edge_1_route_variant_medium_channel`

Counterpart region: `competing_sink_0`

## Checks

| Check | Passed |
|---|---|
| `i121_admission_passed` | `true` |
| `variant_runtime_source_passed` | `true` |
| `all_three_parts_present` | `true` |
| `variant_is_distinct_from_i12_reference` | `true` |
| `medium_part_is_not_merely_label` | `true` |
| `counterpart_region_is_not_old_basin_thickening` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
