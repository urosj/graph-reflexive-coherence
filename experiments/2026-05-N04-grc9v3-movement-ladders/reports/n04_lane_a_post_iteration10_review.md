# N04 Lane A2 Post-Iteration-10 Review

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_lane_a_post_iteration10_review.py
```

Status: `passed`
Claim ceiling: `m5_direction_parity_supported_boundary_response__m6_blocked`

## Updated Evidence Ladder

| Level | Classification | Source |
|---|---|---|
| `M0_M3_fixed_substrate` | `unchanged_from_A1_movement_negative` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_evidence_ladder_audit.json` |
| `M4_M5_direction_parity` | `m5_direction_parity_supported_boundary_response` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_b_direction_parity_closeout.json` |
| `M6_self_renewal` | `m6_not_opened_feedback_path_absent` | `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/self_renewing_movement_candidate_report.json` |

## Allowed Evidence Labels

- `fixed_substrate_negative`
- `subthreshold_directional_bias`
- `state_mediated_boundary_coupling_fixture_positive`
- `m5_direction_parity_supported_boundary_response`
- `m6_not_opened_feedback_path_absent`

## Blocked Claims

- `movement_response`
- `boundary_coupled_movement`
- `loop_driven_movement`
- `self_renewing_movement`
- `locomotion_like_basin_dynamics`
- `adaptive_topology_movement`
- `biological_or_agency_claim`
- `movement_inherited_from_n03`

## Checks

| Check | Passed |
|---|---:|
| `a1_remains_valid` | `True` |
| `lane_b_locked` | `True` |
| `lane_b_promoted_to_direction_parity_boundary_response` | `True` |
| `iteration_10_failed_closed` | `True` |
| `m6_not_opened` | `True` |
| `all_claim_flags_blocked` | `True` |

## Interpretation

A2 updates Lane A after Lane B and Iteration 10. Lane B is promoted
from control-limited M5 candidate to direction-parity-supported
boundary response. Iteration 10 then fails closed for M6 because the
S0 boundary response does not feed back into native E3 pulse-generating
conditions. The strongest current N04 ceiling is therefore
`m5_direction_parity_supported_boundary_response` with M6 blocked.

