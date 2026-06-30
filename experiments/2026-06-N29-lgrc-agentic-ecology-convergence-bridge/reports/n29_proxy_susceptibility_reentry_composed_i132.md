# Prototype C I13.2 Alternative Composed Runtime Candidate

Status: `passed`

Acceptance state: `accepted_i13_2_alternative_composed_runtime_candidate_pending_b_c`

Output digest: `f4a934506528d5fe0609ce50f1748b9d5bf308bf815a81c1ea0088a1789276c6`

## Read

I13.2 is an alternative composed Prototype C runtime candidate. It does not replace I13.1 and does not retune I13.1. It uses a buffered susceptibility lane to test repeatability and margin headroom in a different geometry.

Runtime artifact: `experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_proxy_susceptibility_reentry_composed_runtime_i132_artifact.json`

Prototype C runtime candidate supported: `true`

Final Prototype C success supported: `false`

Claim ceiling: `alternative bounded N29-composed Prototype C runtime candidate; not semantic learning, choice, agency, native AP4/AP5 closure, native support, or ecology success`

## Margins

Susceptibility delta margin: `0.0712`

Differential response margin: `0.19162`

Improved over I13.1 minimum susceptibility margin: `true`

Improved over I13.1 minimum differential margin: `true`

Susceptibility margin delta vs I13.1 minimum: `0.0666`

Differential margin delta vs I13.1 minimum: `0.15337`

## Next

I13.2-B and I13.2-C are required before this alternative can be called control-backed or replay/stress-backed.

## Checks

| Check | Passed |
|---|---|
| `i13_source_passed` | `true` |
| `i13_1c_source_passed` | `true` |
| `new_n29_runtime_artifact_created` | `true` |
| `runtime_artifact_sha256_matches` | `true` |
| `four_leg_trace_present` | `true` |
| `susceptibility_delta_margin_positive` | `true` |
| `differential_response_margin_positive` | `true` |
| `support_coherence_boundary_preserved` | `true` |
| `margin_improved_over_i13_1_min` | `true` |
| `i13_1_not_replaced` | `true` |
| `runtime_candidate_supported_but_final_success_blocked` | `true` |
| `ready_for_i13_2_b_c` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
