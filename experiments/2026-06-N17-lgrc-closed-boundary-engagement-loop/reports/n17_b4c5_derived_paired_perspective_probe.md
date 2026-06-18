# N17 Iteration 8-D - B4/C5-Derived Paired-Perspective Loop Probe

Artifact: `n17_b4c5_derived_paired_perspective_probe`
Status: `passed`
Acceptance state: `accepted_b4c5_derived_two_cycle_paired_perspective_g6_candidate_no_original_relabel_no_final_ap7`
Output digest: `874495c7778ad263ebf8045e95392ba64797a7513db4a0d189057792fe6ae46a`

## Main Result

Iteration 8-D tests a new two-cycle protocol derived from the original B4/C5 shared-medium row. It does not relabel the original B4/C5 row as reverse-perspective replay. Cycle 1 keeps B4/C5's forward basin A-to-medium source. Cycle 2 uses the changed shared medium as input to generate a reverse neighbor-side internal state with source-backed support, coherence, boundary edge, and later-feedback trace.

```text
b4c5_original_state_remains_one_sided = true
b4c5_original_reverse_perspective_replay_supported = false
b4c5_derived_two_cycle_paired_perspective_supported = true
i8c_evidence_imported_as_b4c5_reverse = false
general_shared_medium_g6_supported = false
final_ap7_supported = false
```

## Low-Margin Envelope

```text
reverse_minimum_internal_support = 0.8526
support_floor = 0.85
reverse_support_margin = 0.0026
reverse_support_without_feedback = 0.8494
shared_medium_leakage = 0.108
quiet_leakage_ceiling = 0.12
merge_confusion_pressure = 0.14
merge_confusion_ceiling = 0.2
```

## Row Decisions

| Probe | Decision | Claim Allowed |
| --- | --- | --- |
| `b4c5_derived_cycle2_reverse_side` | `supported` | `True` |
| `b4c5_derived_joint_paired_perspective` | `supported` | `True` |
| `label_swap_as_reverse_perspective_control` | `rejected` | `False` |
| `cycle2_reverse_state_missing_control` | `blocked` | `False` |
| `reverse_support_coherence_missing_control` | `blocked` | `False` |
| `neighbor_leakage_as_retention_control` | `rejected` | `False` |
| `merge_leakage_as_reciprocity_control` | `rejected` | `False` |
| `hidden_shared_medium_routing_control` | `rejected` | `False` |
| `original_b4c5_replay_relabel_control` | `rejected` | `False` |
| `i8c_import_backfill_control` | `rejected` | `False` |
| `final_ap7_relabel_control` | `rejected` | `False` |

## Interpretation

8-D sits between 8-B and 8-C. 8-B still blocks original B4/C5 reverse replay. 8-C remains an independent local paired-perspective protocol. 8-D adds a B4/C5-derived two-cycle candidate: the original B4/C5 state remains one-sided, but the derived second cycle generates new reverse-side state and passes only within a narrow support/leakage envelope. It does not support general shared-medium G6 or final AP7.

## Checks

- `original_b4c5_remains_one_sided`: pass
- `cycle2_reverse_state_generated`: pass
- `low_margin_limits_preserved`: pass
- `feedback_removed_control_changes_result`: pass
- `i8c_not_used_as_b4c5_backfill`: pass
- `controls_fail_closed`: pass
- `supported_rows_keep_trace_contract`: pass
- `unsafe_claim_flags_false`: pass
- `final_ap7_still_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
