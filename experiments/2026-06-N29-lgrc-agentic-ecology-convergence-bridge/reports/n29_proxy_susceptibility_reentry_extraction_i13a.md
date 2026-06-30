# Prototype C I13-A Exact Row Extraction Attempt

Status: `passed`

Acceptance state: `accepted_i13a_exact_row_absent_mapping_inventory_consumable`

Output digest: `8eda4085ebacf26f80ab4a19a326be42d9d90edb98a656cb1fe57d625ad1e732`

Claim ceiling: `exact-row extraction attempt over source-backed Prototype C parts; runtime Prototype C remains blocked`

## Extraction

Exact source-current runtime row found: `false`

Mapping record consumable: `true`

Missing exact-row evidence:

- I13 part sources are distributed across N22, N23, N26, and N27 artifacts
- no artifact_id appears as the primary source for all four bridge parts
- N29 I5-I8 are coverage indexes only and cannot replace original source rows

## Checks

| Check | Passed |
|---|---|
| `i13_source_passed` | `true` |
| `all_four_parts_still_source_backed` | `true` |
| `exact_runtime_row_not_found` | `true` |
| `runtime_claim_blocked` | `true` |
| `mapping_record_consumable` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
