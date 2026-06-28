# N26 Iteration 7 - Replay, Controls, And AP5 Classification Gate

Status: `passed`

Acceptance state: `accepted_controlled_pd5_with_scoped_artifact_ap5_bridge_candidate_pending_i8`

## Summary

I7 consumes the positive N26 tranche and runs the replay/control/AP5 gate.
The I5-C score-dose rows pass as controlled PD4 proxy-divergence rows,
and the I6 perturbation rows pass as controlled PD5 proxy-collapse rows.

PD6 remains pending I8 closeout and N27 handoff. The AP5 result is a
scoped artifact bridge candidate only; native AP5 and native support
remain blocked because the decisive score/deepening surfaces are still
producer-mediated or declared fixture variants.

## Row Classifications

| Row | Source | Final Rung | Replay | Controls |
| --- | --- | --- | --- | --- |
| `n26_i4_i4_reference_child_basin_core_0` | `I4` | `PD2` | `True` | `True` |
| `n26_i4_i4a_route_variant_child_basin_core_2` | `I4` | `PD2` | `True` | `True` |
| `n26_i5c_same_route_score_dose_sink0_fixed_route` | `I5-C` | `PD4` | `True` | `True` |
| `n26_i5c_same_route_score_dose_sink2_fixed_route` | `I5-C` | `PD4` | `True` | `True` |
| `n26_i6_proxy_collapse_perturbation_sink0_proxy_collapse` | `I6` | `PD5` | `True` | `True` |
| `n26_i6_proxy_collapse_perturbation_sink2_proxy_collapse` | `I6` | `PD5` | `True` | `True` |

## AP5 Classification

```text
ap5_bridge_status = scoped_artifact_ap5_bridge_candidate_supported_native_ap5_blocked
scoped_artifact_ap5_bridge_candidate_supported = true
native_ap5_bridge_supported = false
ap5_nat4_gap_resolved = false
```

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_digests_match_expected` | `true` |
| `positive_row_manifests_match_file_contents` | `true` |
| `positive_row_replay_gate_passed` | `true` |
| `negative_controls_fail_closed_no_failed_open` | `true` |
| `post_hoc_target_derivation_blocked` | `true` |
| `hidden_proxy_policy_absent_or_failed_closed` | `true` |
| `scoped_ap5_bridge_candidate_classified_native_ap5_blocked` | `true` |
| `pd5_supported_pd6_pending_closeout` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |

## Artifacts

```text
outputs/n26_replay_controls_and_ap5_gate.json
reports/n26_replay_controls_and_ap5_gate.md
scripts/build_n26_replay_controls_and_ap5_gate.py
```
