# N27 Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification

Status: `passed`

Acceptance state: `accepted_ct5_controls_ap_claim_classification_pending_i8_closeout`

## Scope

Iteration 7 consumes I6 without creating new transfer geometry. It runs the
full frozen control matrix, records AP4/AP5 dependency statuses row-locally,
and classifies the strongest supported CT rung pending I8 closeout.

```text
classified_ct_ladder_rung = CT5
ct5_or_stronger_supported = true
ct6_or_stronger_supported = false
final_transfer_supported = false
failed_open_control_count = 0
```

## Classification Rows

| Row | Source | Scope | Decision | Classified CT Rung | CT5 Supported |
| --- | --- | --- | --- | --- | --- |
| `n27_i7_row_4_controls_ap_claim_classification` | `4` | `configuration` | `partial` | `CT4_control_clean_stress_limited` | `false` |
| `n27_i7_row_4a_controls_ap_claim_classification` | `4-A` | `topology` | `supported` | `CT5` | `true` |

## Interpretation

I7 keeps the I6 asymmetry. The I4 alpha/beta candidate is control-clean for its
supported scope, but remains stress-limited and contributes no CT5 evidence.
The I4-A gamma/delta topology/fixture candidate passes the full control matrix
with no failed-open controls, preserves AP4/AP5 row-local boundaries, and is
classified as the strongest CT5 candidate.

This is still not final transfer. CT6 requires I8 closeout and N28 handoff.
N26 remains bounded context, N25.2 is not directly consumed, native AP5 and the
AP5 NAT4 gap remain unresolved, and unsafe semantic/native/Phase-8/ant-ecology
claims remain blocked.

## Checks

| Check | Passed |
| --- | --- |
| `source_chain_digests_match` | `true` |
| `i6_ready_for_i7_controls` | `true` |
| `all_required_controls_accounted_per_row` | `true` |
| `failed_open_controls_zero` | `true` |
| `i4_remains_stress_limited_no_ct5_contribution` | `true` |
| `i4a_ct5_supported_after_controls` | `true` |
| `ap4_ap5_row_local_statuses_valid` | `true` |
| `n26_and_n25_2_boundaries_preserved` | `true` |
| `native_ap5_and_ap5_nat4_gap_remain_blocked` | `true` |
| `ct5_supported_but_ct6_and_final_transfer_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |


Output digest: `d25a2490345a25e41c76f76afecbd267d3dba77e3d2b0fdf6b3f8c256ccaa08c`
