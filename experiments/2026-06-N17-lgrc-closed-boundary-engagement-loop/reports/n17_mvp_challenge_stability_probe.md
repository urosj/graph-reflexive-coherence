# N17 Iteration 6-A - MVP Challenge-Stability Probe

Artifact: `n17_mvp_challenge_stability_probe`
Status: `passed`
Acceptance state: `accepted_bounded_g5_mvp_challenge_stability_no_final_ap7`
Output digest: `4c795ca09ec6d7b557f5d1f8d1f7d0624f4eb7cfea99a43f383f40d68068ebc4`

## Main Result

Iteration 6-A tests G5 challenge stability for the same MVP perturbation-response-recovery loop classified in I6. It does not open resource/support or shared-medium extensions.

```text
current_evidence_rung = G5_bounded_challenge_stable_candidate
g5_challenge_stability_supported = true
g5_support_scope = bounded_source_backed_breach_flux_envelope
full_comparative_ap7_classification_supported = false
final_ap7_supported = false
```

The supported envelope is bounded by the source-backed C4 breach profile and C2 directional-flux profile. Feedback attenuation, extra feedback delay, and pressure outside that envelope fail closed.

## Rows

| Row | Challenge | Decision | Claim Allowed |
| --- | --- | --- | --- |
| `n17_i6a_row_01_canonical_c4_breach_reclosure` | `canonical_c4_breach_reclosure` | `supported` | `true` |
| `n17_i6a_row_02_c2_directional_flux_repair_anchor` | `c2_directional_flux_repair_anchor` | `supported` | `true` |
| `n17_i6a_row_03_bounded_breach_flux_composite_envelope` | `bounded_breach_flux_composite_envelope` | `supported` | `true` |
| `n17_i6a_row_04_feedback_attenuation_control` | `feedback_attenuation_control` | `partial` | `false` |
| `n17_i6a_row_05_feedback_delay_control` | `feedback_delay_control` | `partial` | `false` |
| `n17_i6a_row_06_overpressure_control` | `overpressure_control` | `rejected` | `false` |

## Claim Boundary

This is still artifact-level AP7 MVP evidence only. It does not support final AP7, full comparative AP7, resource/support AP7, shared-medium reciprocal AP7, agency, intention, semantic action or perception, selfhood, native support, organism/life, or fully native integration.

## Handoff

Iteration 7 can now open the resource/support modulation extension. Iteration 8 remains the shared-medium reciprocal extension. Iteration 9 must synthesize comparative requirements and extension mode, and Iteration 10 must freeze final closeout if warranted.

## Checks

- `source_i6_ap7_mvp_claim_clean`: pass
- `mvp_family_only`: pass
- `bounded_g5_supported_rows_present`: pass
- `challenge_controls_fail_closed`: pass
- `supported_rows_keep_all_trace_legs`: pass
- `unsafe_claim_flags_false`: pass
- `final_ap7_still_false`: pass
- `src_diff_empty`: pass
- `no_absolute_paths`: pass
