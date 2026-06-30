# Prototype B - Active-Medium Runtime Extraction

Status: `passed`

Acceptance state: `accepted_active_medium_runtime_extraction_pending_controls`

Output digest: `55eb734a533aea01d605c9fd77b9a827099998d56892e81699608db60f95956a`

## Active Medium Rows

| Variant | Packet records | Max contact | Observed flux | Ceiling | Injected pressure status |
|---|---:|---:|---:|---:|---|
| `I12_primary_reference` | `1.0` | `0.1` | `0.0` | `0.0` | `failed_closed` |
| `I12_1_sibling_variant` | `1.0` | `0.1` | `0.0` | `0.0` | `failed_closed` |

## Checks

| Check | Passed |
|---|---|
| `i122_admission_passed` | `true` |
| `source_current_medium_activity_present_in_both_rows` | `true` |
| `zero_leakage_policy_preserved_in_both_rows` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
