# N24 Iteration 7-B - Flux Envelope Probe

Status: `passed`

Acceptance state: `accepted_flux_envelope_not_widened_n24c6_flux_blocker_recorded`

Output digest: `09387f3989903bdb95b58679e9d45c2f93e1ead1788f29dd68977b75224cfe6a`

## Summary

Iteration 7-B tests whether the existing N24 AB5 candidates have flux room
above the frozen `1e-9` leakage bound. They do not.

```text
flux_or_leakage_bound = 0.000000001000
all_candidates_pass_at_bound = true
all_candidates_fail_above_bound = true
any_candidate_widens_flux_envelope = false
n24_c6_flux_readiness_supported = false
n24_c6_blocker = flux_envelope_not_widened_above_1e-9
```

## Interpretation

I7-B confirms the current N24 AB5 candidates pass at the frozen 1e-9 flux bound but do not widen the flux envelope above it.

This supports closing N24 as AB5/N24-C5 with explicit flux debt, not N24-C6. A future primitive must naturalize or widen the flux/leakage envelope before N24-style optionality can become N25-ready without that constraint.

## Candidate Flux Rows

| Candidate | Best preserved flux | First above-bound failure | Widens envelope |
| --- | --- | --- | --- |
| `I7` | `0.000000001000` | `0.000000001010` | `false` |
| `I7-A` | `0.000000001000` | `0.000000001010` | `false` |

## Checks

| Check | Passed |
| --- | --- |
| `i1_inventory_passed` | `true` |
| `i2_schema_passed` | `true` |
| `i3_active_nulls_passed` | `true` |
| `i7_and_i7a_ready` | `true` |
| `at_bound_flux_passes_for_both_candidates` | `true` |
| `above_bound_flux_fails_closed_for_both_candidates` | `true` |
| `flux_envelope_not_widened` | `true` |
| `controls_fail_closed` | `true` |
| `artifact_manifest_non_empty_and_sha_match` | `true` |
| `unsafe_claim_flags_all_false` | `true` |
| `no_absolute_paths` | `true` |
