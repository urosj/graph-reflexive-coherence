# Prototype B - Active-Medium Separability Admission

Status: `passed`

Acceptance state: `accepted_active_medium_separability_admission_pending_i122abc`

Output digest: `999740bd86d0756e61f2d9c263dda209f3b26ab1d00ee49952023dc6f96a9f49`

## Tranche

I12.2 admits an active-medium separability tranche. I12.2-A extracts source-current medium activity, I12.2-B runs controls, and I12.2-C records replay/stress closeout.

## Checks

| Check | Passed |
|---|---|
| `i12_primary_reference_passed` | `true` |
| `i12_1_sibling_reference_passed` | `true` |
| `active_medium_probe_requires_i122abc` | `true` |
| `zero_leakage_ceiling_preserved_as_policy` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
