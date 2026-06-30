# Prototype B - Runtime Boundary / Shared-Medium Unit Extraction

Status: `passed`

Acceptance state: `accepted_exact_runtime_unit_extraction_pending_controls_replay_stress`

Output digest: `518d48d038ad7d27062b785820c91f69c35e5925e1feb864ff59a1204c4a93e5`

## Runtime Unit

Unit: `N29.I12A.BOUNDARY_SHARED_MEDIUM_UNIT.RUNTIME.001`

Basin side: `child_basin_core_0`

Shared/adjacent medium: `source_edge_1_route_candidate_medium_channel`

Counterpart region: `competing_sink_2`

This is an exact extracted runtime row, not wholesale MB6 inheritance.

## Claim Boundary

exact source-current boundary/shared-adjacent-medium unit extraction pending controls and replay/stress

Unsafe claims remain false.

## Checks

| Check | Passed |
|---|---|
| `i12_source_passed` | `true` |
| `runtime_source_passed` | `true` |
| `all_three_parts_present` | `true` |
| `all_three_parts_have_source_current_runtime_trace` | `true` |
| `medium_part_is_not_merely_label` | `true` |
| `counterpart_region_is_not_old_basin_thickening` | `true` |
| `n25_2_mb6_not_inherited_wholesale` | `true` |
| `artifact_manifest_sha256_present` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
