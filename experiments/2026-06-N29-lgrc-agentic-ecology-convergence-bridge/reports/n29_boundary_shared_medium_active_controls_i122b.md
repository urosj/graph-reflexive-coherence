# Prototype B - Active-Medium Controls

Status: `passed`

Acceptance state: `accepted_active_medium_controls_fail_closed`

Output digest: `e6f189f79572713f5097f05d7cedc77c1a465c4ba7c463899a138698e9912139`

## Controls

| Control | Status |
|---|---|
| `I12_primary_reference_nonzero_pressure_control` | `failed_closed` |
| `I12_1_sibling_variant_nonzero_pressure_control` | `failed_closed` |
| `active_medium_as_coordination_relabel_control` | `failed_closed` |
| `semantic_trail_or_pheromone_relabel_control` | `failed_closed` |
| `active_medium_as_ecology_success_relabel_control` | `failed_closed` |

## Checks

| Check | Passed |
|---|---|
| `i122a_passed` | `true` |
| `all_required_controls_present` | `true` |
| `all_controls_failed_closed` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
