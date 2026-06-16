# N14 Observed Route-Specific Consequence Probe

Status: `passed`.

## Acceptance State

```text
accepted_observed_route_specific_memory_probe_support_regulation_generic
```

## Interpretation

```json
{
  "acceptance_state": "accepted_observed_route_specific_memory_probe_support_regulation_generic",
  "next_required_step": "Use Iteration 7 to classify AP4 with the narrowed memory-dominant claim ceiling unless new route-specific support/regulation sources are added.",
  "plain_language_interpretation": "The source-backed observed route-specific part of N14 is memory-dominant. Route_b has the stronger observed memory consequence under the same N08 window policy. Support and regulation remain generic source lanes, so they are blocked from route-specific closeout language unless future artifacts bind them to route IDs.",
  "record_id": "n14_i6a_interpretation_observed_route_specific_probe_v1",
  "supported_interpretation": "N14 Iteration 6-A finds observed route-specific memory consequences for both route_a and route_b under the same N08 MEM3 update-window policy. It does not find observed route-specific support or regulation consequences in the available N09/N13 sources.",
  "unsupported_interpretations": [
    "observed route-specific support consequence support",
    "observed route-specific regulation consequence support",
    "final AP4 support before Iteration 7 classification",
    "intention",
    "agency",
    "semantic choice",
    "semantic goal ownership",
    "identity acceptance",
    "selfhood",
    "personhood",
    "biological behavior",
    "native support",
    "fully native integration"
  ]
}
```

## Probe Summary

```json
{
  "route_specific_memory_supported": true,
  "route_specific_regulation_supported": false,
  "route_specific_support_supported": false,
  "stronger_support_or_regulation_closeout_available": false,
  "supported_closeout_scope": "artifact_level_ap4_memory_dominant_consequence_sensitive_route_selection_candidate"
}
```

## Observed Route Records

| Route | Memory delta | Memory rank | Support | Regulation |
| --- | ---: | ---: | --- | --- |
| `route_a` | 0.155 | 2 | `unsupported_generic_source_only` | `unsupported_generic_source_only` |
| `route_b` | 0.2 | 1 | `unsupported_generic_source_only` | `unsupported_generic_source_only` |

## Controls

| Control | Blocker | Passed |
| --- | --- | --- |
| `route_label_swap_control` | `route_label_swap_blocked` | `true` |
| `generic_support_regulation_reuse_control` | `generic_support_regulation_reuse_blocked` | `true` |
| `missing_route_observation_control` | `missing_route_observation_blocked` | `true` |
| `stale_route_specific_consequence_control` | `stale_route_specific_consequence_blocked` | `true` |
| `budget_invalid_observed_route_control` | `budget_invalid_observed_route_blocked` | `true` |
| `post_hoc_score_rank_control` | `post_hoc_score_rank_blocked` | `true` |

Iteration 6-A supports only observed route-specific memory
consequence evidence. Support and regulation remain generic source
lanes and are not promoted into route-specific AP4 evidence.

## Checks

```json
{
  "both_routes_observed_for_memory": true,
  "budget_invalid_observed_route_blocked": true,
  "claim_flags_forced_false": true,
  "controls_passed": true,
  "final_ap4_not_supported": true,
  "generic_support_regulation_reuse_blocked": true,
  "missing_route_observation_blocked": true,
  "n08_memory_source_passed": true,
  "n09_regulation_source_passed": true,
  "n13_support_source_passed": true,
  "native_support_opened_false": true,
  "observed_memory_rank_selects_route_b": true,
  "perturbation_source_passed": true,
  "phase8_opened_false": true,
  "post_hoc_score_rank_blocked": true,
  "route_label_swap_blocked": true,
  "route_specific_components_derived_from_observed_records": true,
  "route_specific_memory_supported": true,
  "route_specific_regulation_remains_unsupported_generic": true,
  "route_specific_support_remains_unsupported_generic": true,
  "same_budget_accounting": true,
  "same_selection_rule": true,
  "same_source_window_policy": true,
  "src_diff_empty": true,
  "stale_route_specific_consequence_blocked": true
}
```

## Claim Boundary

```text
observed route-specific memory consequence != intention
observed route-specific memory consequence != semantic choice
generic support/regulation lane != route-specific consequence
memory-dominant AP4 candidate != agency
artifact-level route-specific probe != native support
N14 Iteration 6-A != final AP4 closeout before Iteration 7
```

## Output Digest

```text
7f75ab3c2601a483938ba333676ef0435412ea7d5681910edcdc31c39c5a5a70
```
