# N18 Iteration 4 - Horizon Window Sweep

## Summary

```text
status = passed
acceptance_state = accepted_horizon_window_sweep_l2_max_h4_no_ap8
highest_positive_stress_ladder_rung = L2
max_supported_horizon = h4
supported_windows = ['h2', 'h4']
partial_windows = ['h8']
blocked_windows = ['h16']
primary_i5_stress_anchor = h4
fallback_i5_control = h2
ap8_candidate_allowed = false
final_ap8_supported = false
output_digest = 0b65b390dabc30ee34b3003796cfb85cb1ca8f2c1bfe44f91bac160aa9c7c21e
```

## Window Results

| Window | Relative Count | Decision | Limiting Axis | Min Axis | Limiting Link | Cross-Axis | Drift | Budget Headroom |
| --- | ---: | --- | --- | ---: | --- | ---: | ---: | ---: |
| h2 | 2 | supported | loop_feedback | 0.880 | boundary_to_loop_feedback | 0.890 | 0.045 | 0.780 |
| h4 | 4 | supported | loop_feedback | 0.830 | boundary_to_loop_feedback | 0.840 | 0.086 | 0.590 |
| h8 | 8 | partial | loop_feedback | 0.720 | boundary_to_loop_feedback | 0.730 | 0.142 | 0.240 |
| h16 | 16 | rejected | loop_feedback | 0.490 | boundary_to_loop_feedback | 0.520 | 0.315 | -0.210 |

## Interpretation

Iteration 4 extends the I3 AP7 baseline into longer no-perturbation
artifact windows. `h2` and `h4` remain source-current across support,
memory, regulation, selection, proxy, boundary, loop feedback, and
linked trace continuity. This establishes a bounded L2 replay
envelope with `max_supported_horizon = h4`.

`h8` is partial because linked trace continuity drops below the
floor and drift exceeds the quiet ceiling. `h16` is rejected because
it is outside the source-backed envelope and exceeds the declared
budget surface. These rows prevent horizon extrapolation.

For Iteration 5, `h4` is the primary stress anchor and `h2` is the
fallback/control row. `h8` remains horizon-limit evidence and `h16`
remains rejected out-of-envelope evidence. I5 must not retune the
horizon or try to recover `h8`; it should stress the supported `h4`
envelope.

At `h4`, the limiting axis is loop feedback and the limiting linked
edge is boundary-to-loop-feedback. Support and proxy are still above
floor, so I5 support/proxy stress should record whether those axes
remain linked without breaking the already-limiting loop edge.

N12 is intentionally not consumed in I4 trace rows. It remains
readiness-only context and is not AP7/L2 horizon replay evidence.

The numeric floors and ceilings used for I4 decisions are recorded in
`threshold_policy`. Iteration 2 froze the required fields and
fail-closed gates; Iteration 4 freezes the L2 numeric floors before
row evaluation.

The result is stronger than the I3 active null because it tests
longer windows, but it is still not final AP8. Stress families,
artifact-only reconstruction, duplicate replay, snapshot/load replay,
order inversion, stale-state controls, and final classification
remain pending.

## Claim Boundary

I4 supports only a bounded artifact-level L2 horizon replay envelope.
It does not support agency, semantic action/perception, semantic goal
ownership, identity acceptance, native support, Phase 8, organism or
life claims, unrestricted autonomy, or final AP8.

## Checks

| Check | Passed |
| --- | --- |
| iteration3_baseline_ready | true |
| all_horizon_policy_windows_present | true |
| supported_envelope_is_h2_h4 | true |
| out_of_envelope_windows_fail_closed | true |
| all_rows_l2_no_added_perturbation | true |
| all_rows_keep_ap8_false | true |
| unsafe_claim_flags_false | true |
| i5_anchor_policy_recorded | true |
| n12_not_consumed_in_i4_traces | true |
| source_digest_matches_n18_i3_baseline | true |
| source_digest_matches_n18_i1_row_01_n17_closeout_ap7 | true |
| source_digest_matches_n18_i1_row_02_n17_requirements_matrix | true |
| source_digest_matches_n18_i1_row_03_n17_replay_control_matrix | true |
| source_digest_matches_n18_i1_row_04_n17_claim_boundary_record | true |
| source_digest_matches_n18_i1_row_05_n16_closeout_ap6 | true |
| source_digest_matches_n18_i1_row_06_n15_closeout_ap5 | true |
| source_digest_matches_n18_i1_row_07_n14_closeout_ap4 | true |
| source_digest_matches_n18_i1_row_08_n13_closeout_ap3 | true |
| source_digest_matches_n18_i1_row_11_n08_memory_closeout | true |
| source_digest_matches_n18_i1_row_12_n09_regulation_closeout | true |
| no_absolute_paths | true |
