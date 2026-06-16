# N14 Route-Conditioned Followout Probe

Status: `passed`.

## Acceptance State

```text
accepted_constructed_route_conditioned_support_regulation_followout
```

## Interpretation

```json
{
  "acceptance_state": "accepted_constructed_route_conditioned_support_regulation_followout",
  "boundary_interpretation": "This does not overturn Iteration 6-B. N09/N13 still do not contain upstream observed route-conditioned support/regulation rows. 6-C adds an experiment-local route-conditioned followout artifact calibrated from those sources.",
  "next_required_step": "Run Iteration 7 classification and distinguish constructed followout support/regulation evidence from upstream observed route-conditioned support/regulation evidence.",
  "plain_language_interpretation": "The attempt got a guarded positive: N14 can construct route-ID-bound support/regulation followout rows before scoring and pass the main relabeling controls. The positive is artifact-local and policy-mediated, so Iteration 7 must decide how much it broadens the final AP4 wording.",
  "record_id": "n14_i6c_interpretation_route_conditioned_followout_probe_v1",
  "supported_interpretation": "N14 Iteration 6-C obtains a positive artifact-level constructed followout result: route_a and route_b each receive serialized route IDs before support/regulation axis scoring, and the resulting support and regulation components differ by route under one frozen followout policy.",
  "unsupported_interpretations": [
    "native support",
    "upstream N09/N13 observed route-conditioned support evidence",
    "upstream N09/N13 observed route-conditioned regulation evidence",
    "final AP4 before Iteration 7",
    "intention",
    "agency",
    "semantic choice",
    "semantic goal ownership",
    "identity acceptance",
    "selfhood",
    "personhood",
    "biological behavior",
    "fully native integration"
  ]
}
```

## Followout Summary

```json
{
  "accepted_validation_status": {
    "blocker": null,
    "status": "accepted"
  },
  "constructed_route_conditioned_regulation_followout_supported": true,
  "constructed_route_conditioned_support_followout_supported": true,
  "observed_upstream_route_conditioned_support_regulation_from_6b": false,
  "regulation_components_by_route": {
    "route_a": -0.32,
    "route_b": 0.08
  },
  "scope_caveat": "support/regulation positivity is constructed N14 followout evidence; it is not upstream N09/N13 observed route-conditioned evidence and it is not native support",
  "support_components_by_route": {
    "route_a": -0.240269635632,
    "route_b": 0.0
  },
  "supported_closeout_scope": "artifact_level_ap4_support_memory_regulation_consequence_sensitive_route_selection_candidate",
  "top_followout_route": "route_b"
}
```

## Route Followout Records

| Route | Support component | Regulation component | Followout score | Rank |
| --- | ---: | ---: | ---: | ---: |
| `route_a` | -0.240269635632 | -0.32 | -0.720024135632 | 2 |
| `route_b` | 0.0 | 0.08 | 0.2 | 1 |

## Controls

| Control | Blocker | Passed |
| --- | --- | --- |
| `route_label_swap_control` | `route_label_swap_blocked` | `true` |
| `generic_source_reuse_control` | `generic_source_reuse_blocked` | `true` |
| `missing_route_followout_control` | `missing_route_followout_blocked` | `true` |
| `stale_source_window_control` | `stale_source_window_blocked` | `true` |
| `budget_invalid_followout_control` | `budget_invalid_followout_blocked` | `true` |
| `post_hoc_route_conditioning_control` | `post_hoc_route_conditioning_blocked` | `true` |
| `fixture_label_assignment_control` | `fixture_label_assignment_blocked` | `true` |
| `support_equal_effect_null_control` | `equal_effect_followout_blocked` | `true` |
| `regulation_equal_effect_null_control` | `equal_effect_followout_blocked` | `true` |
| `equal_effect_null_control` | `equal_effect_followout_blocked` | `true` |

## Result

Iteration 6-C obtains a guarded positive constructed followout:
support and regulation components are route-conditioned in the
N14 artifact because route IDs are serialized before axis scoring.
This is not upstream observed N09/N13 route-conditioned evidence,
native support, intention, semantic choice, or agency.

## Checks

```json
{
  "both_routes_have_followout_rows": true,
  "budget_invalid_followout_blocked": true,
  "claim_flags_forced_false": true,
  "controls_passed": true,
  "equal_effect_null_blocked": true,
  "final_ap4_not_supported": true,
  "fixture_label_assignment_blocked": true,
  "followout_policy_serialized": true,
  "followout_rank_derived_from_components": true,
  "generic_source_reuse_blocked": true,
  "iteration_6b_not_contradicted": true,
  "iteration_6b_source_passed": true,
  "missing_route_followout_blocked": true,
  "n09_regulation_source_passed": true,
  "n13_stress_source_passed": true,
  "native_support_opened_false": true,
  "no_generic_source_reuse": true,
  "no_post_hoc_rank_assignment": true,
  "no_producer_direct_mutation": true,
  "phase8_opened_false": true,
  "positive_followout_validation_accepted": true,
  "post_hoc_route_conditioning_blocked": true,
  "regulation_components_differ_by_route": true,
  "regulation_equal_effect_null_blocked": true,
  "regulation_followout_route_conditioned": true,
  "route_ids_serialized_before_axis_scoring": true,
  "route_label_swap_blocked": true,
  "runtime_state_used_false": true,
  "selection_source_passed": true,
  "src_diff_empty": true,
  "stale_source_window_blocked": true,
  "support_components_differ_by_route": true,
  "support_equal_effect_null_blocked": true,
  "support_followout_route_conditioned": true
}
```

## Claim Boundary

```text
constructed route-conditioned followout != upstream route-conditioned observation
constructed support/regulation followout != native support
route-conditioned consequence-sensitive selection != intention
artifact-level AP4 candidate != agency
N14 Iteration 6-C != final AP4 closeout before Iteration 7
```

## Output Digest

```text
387faa187068737884b67723e21c2c8068e38c337b486d8146cbd3261e73cb29
```
