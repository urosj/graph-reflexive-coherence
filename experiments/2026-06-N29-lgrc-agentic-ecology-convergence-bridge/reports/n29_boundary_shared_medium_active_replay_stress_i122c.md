# Prototype B - Active-Medium Replay And Stress Close

Status: `passed`

Acceptance state: `accepted_active_medium_separability_probe_no_leakage_policy_change`

Output digest: `d6077db416fa6c032bfc4d0d4edcf43802f8604f1468d45ba300f4ae4f9a9cf2`

## Active Medium Rows

| Variant | Packet records | Max contact | Observed flux | Ceiling | Injected pressure status |
|---|---:|---:|---:|---:|---|
| `I12_primary_reference` | `1.0` | `0.1` | `0.0` | `0.0` | `failed_closed` |
| `I12_1_sibling_variant` | `1.0` | `0.1` | `0.0` | `0.0` | `failed_closed` |

## Interpretation

I12.2 strengthens Prototype B by showing active source-current medium traces in both the primary and sibling units while preserving the zero-leakage boundary rule.

It does not improve leakage headroom. Nonzero injected pressure remains a fail-closed control, not a tolerated positive coupling.

Ready for I13: `true`

## Checks

| Check | Passed |
|---|---|
| `i122a_passed` | `true` |
| `i122b_passed` | `true` |
| `i122b_failed_open_count_zero` | `true` |
| `active_medium_present_in_both_rows` | `true` |
| `zero_leakage_policy_preserved_in_both_rows` | `true` |
| `nonzero_injected_pressure_fails_closed_in_both_rows` | `true` |
| `leakage_headroom_not_claimed_as_improved` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
