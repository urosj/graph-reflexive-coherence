# N13 Support Schema V1

## Status

Status: `passed`.

```text
target_ap_ceiling = AP3
phase8_opened = false
native_support_opened = false
identity_acceptance_opened = false
agency_claim_opened = false
```

Iteration 2 freezes the support-condition schema and N13 AP mapping.
It does not validate candidate rows against AP3 yet; that begins in
Iterations 3-7.

## AP Ladder

| AP | Label | N13 interpretation |
| --- | --- | --- |
| `AP0` | passive integrated replay | source envelope or boundary row with no support-seeking target |
| `AP1` | runtime-visible trigger produces bounded response | bounded response evidence exists, but target is still external or not support-derived |
| `AP2` | support-sensitive regulation preserves a declared support condition | composition or response is gated by support-state evidence, but the N13 support-derived target has not yet been isolated |
| `AP3` | self-maintenance candidate | regulation targets a source-current support-state-derived condition rather than only an externally declared proxy |
| `AP4` | consequence-sensitive selection | reserved for N14 |
| `AP5` | endogenous proxy candidate | reserved for N15 |
| `AP6` | self/environment boundary candidate | reserved for N16 |
| `AP7` | closed action-perception loop candidate | reserved for N17 |
| `AP8` | long-horizon agentic-like closure candidate | reserved for N18 |

## AP2 And AP3 Criteria

```json
{
  "AP2": {
    "forbidden": [
      "identity acceptance claim",
      "self-maintenance claim without target derivation"
    ],
    "required": [
      "source-backed support condition or support-state matrix",
      "support-present and support-disrupted distinction",
      "artifact replay or source-current reconstruction",
      "claim flags forced false"
    ]
  },
  "AP3": {
    "forbidden": [
      "identity acceptance claim",
      "semantic goal ownership claim",
      "intention claim",
      "agency claim",
      "native support claim without Phase 8 implementation"
    ],
    "required": [
      "support_state_fields source-current and serialized",
      "support_condition_name derived from support state",
      "target_derivation not external fixture label",
      "external_proxy_fields separated from support target",
      "support error signal recorded",
      "bounded response magnitude surface recorded",
      "node-plus-packet or explicit budget debit recorded",
      "support trend/stability fields recorded",
      "support-disrupted negative control passes",
      "explicit restoration control, if used, is source-backed",
      "hidden support target control passes",
      "post-hoc support label control passes",
      "identity acceptance relabel blocked",
      "semantic goal ownership relabel blocked",
      "agency relabel blocked"
    ]
  }
}
```

## Row Schema Fields

```json
[
  "row_id",
  "source_experiment",
  "source_iteration",
  "source_artifact",
  "source_report",
  "source_sha256",
  "source_report_sha256",
  "mechanism_name",
  "mechanism_role",
  "support_state_fields",
  "external_proxy_fields",
  "producer_decision_fields",
  "bookkeeping_fields",
  "runtime_visible_surfaces",
  "budget_surfaces",
  "response_surfaces",
  "support_condition_name",
  "target_derivation",
  "provisional_ap_level",
  "provisional_self_maintenance_candidate",
  "claim_ceiling",
  "blocked_claims",
  "missing_gates",
  "control_requirements"
]
```

## Controls

```json
{
  "agency_relabel_blocked": true,
  "budget_ambiguity_blocked": true,
  "external_proxy_relabel_blocked": true,
  "hidden_support_target_blocked": true,
  "identity_acceptance_relabel_blocked": true,
  "native_support_relabel_blocked": true,
  "post_hoc_support_label_blocked": true,
  "semantic_goal_ownership_relabel_blocked": true,
  "stale_source_replay_blocked": true,
  "support_disrupted_regulation_blocked": true
}
```

## Fail-Closed Blockers

```json
[
  "missing_source_artifact",
  "external_proxy_only",
  "hidden_support_target",
  "post_hoc_support_label",
  "support_disrupted_but_regulation_counted",
  "budget_surface_ambiguity",
  "stale_source_replay",
  "identity_acceptance_relabel",
  "semantic_goal_ownership_relabel",
  "agency_relabel",
  "native_support_without_phase8"
]
```

## Checks

```json
{
  "ap2_ap3_distinction_declared": true,
  "ap_ladder_complete": true,
  "claim_flags_all_false": true,
  "control_flags_declared": true,
  "inventory_sha256_present": true,
  "inventory_source_passed": true,
  "native_support_not_opened": true,
  "phase8_not_opened": true,
  "row_schema_fields_declared": true,
  "src_diff_empty": true,
  "validation_scope_declared": true
}
```

## Claim Boundary

```text
AP3 self-maintenance candidate != agency
support-derived target != semantic goal ownership
support survival != identity acceptance
bounded response != intention
artifact-level regulation != native support
```

## Output Digest

```text
7691834eb654dc15ee8aabf8ce732a10a72c375d95f3fa97290a8b6cf6984a4f
```
