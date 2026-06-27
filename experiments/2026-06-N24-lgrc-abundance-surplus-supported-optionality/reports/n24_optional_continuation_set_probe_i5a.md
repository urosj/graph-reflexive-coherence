# N24 Iteration 5-A - Alternative Optional Continuation Set Probe

Status: `passed`

Acceptance state: `accepted_alternative_high_margin_ab3_optional_continuation_candidate_pending_i6a`

Output digest: `694994ac8393f7e8a8cd148706d6d8e7caf71da4b9c46fd6e9abc53eb60b6c44`

## Summary

Iteration 5-A adds an alternative high-margin optionality variant. It does
not replace I5; it creates a second source-current AB3 candidate for I6-A
and I7-A to replay and stress-test.

## Geometry

I5-A reuses the LGRC fixture but declares a different source-current maintenance basin over high-support optional target nodes [1, 5, 9].

The original I5 maintenance basin had min support/coherence 10.0, margin 0.15 above the 9.85 floor. I5-A has min support/coherence 11.0, margin 1.15 above the same floor.

```text
maintenance_basin_id = n24_i5a_high_margin_target_supported_basin
maintenance_node_ids = [1, 5, 9]
optional_branch_target_node_ids = [1, 5, 9]
support_floor = 9.850000000000
coherence_floor = 9.850000000000
observed_min_support = 11.000000000000
observed_min_coherence = 11.000000000000
support_surplus_margin = 1.150000000000
coherence_surplus_margin = 1.150000000000
```

## Boundary

This is an alternative AB3 candidate only. It does not replace I5, does not change the frozen thresholds, and does not open reward, semantic choice, agency, native support, sentience, Phase 8, or ant ecology.

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_passed` | `true` |
| `i4_surplus_probe_passed` | `true` |
| `original_i5_i6_i7_preserved_as_context` | `true` |
| `candidate_row_field_set_matches_i2_required_fields` | `true` |
| `derived_report_only_false` | `true` |
| `artifact_manifest_roles_allowed_by_i2` | `true` |
| `high_margin_variant_observed` | `true` |
| `source_current_optional_set_present` | `true` |
| `boundary_flux_and_claim_boundary_preserved` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
