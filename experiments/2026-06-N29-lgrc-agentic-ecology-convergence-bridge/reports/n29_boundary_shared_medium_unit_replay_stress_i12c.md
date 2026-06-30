# Prototype B - Boundary / Shared-Medium Replay And Stress

Status: `passed`

Acceptance state: `accepted_boundary_shared_medium_bridge_candidate_controlled_replay_stress`

Output digest: `763752030ab58c6c73db61959b17426b63305c892bb875a6da150a4f3788df94`

## Replay / Stress

| Row | Status | Pass Condition |
|---|---|---|
| `artifact_only_replay` | `passed` | same unit row reconstructs from artifact manifest |
| `snapshot_load_replay` | `passed` | basin, medium, and counterpart assignments survive snapshot load |
| `duplicate_replay` | `passed` | duplicate run preserves classification within tolerance |
| `medium_coupling_stress` | `passed` | source coupling trace remains bounded and injected pressure fails closed |
| `merge_pressure_stress` | `passed` | merge pressure remains bounded or demotes claim |
| `counterpart_separability_stress` | `passed` | counterpart remains distinguishable from basin-side state or row is demoted |

Prototype B bridge exemplar candidate supported: `true`

## Claim Boundary

controlled and replay/stress-backed Prototype B bridge exemplar candidate

Unsafe claims remain false.

## Checks

| Check | Passed |
|---|---|
| `i12a_passed` | `true` |
| `i12b_passed` | `true` |
| `i12b_failed_open_count_zero` | `true` |
| `all_replay_stress_rows_pass_or_demote_cleanly` | `true` |
| `artifact_snapshot_duplicate_replay_pass` | `true` |
| `medium_coupling_and_merge_pressure_bounded` | `true` |
| `counterpart_separability_survives_or_demotes` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
