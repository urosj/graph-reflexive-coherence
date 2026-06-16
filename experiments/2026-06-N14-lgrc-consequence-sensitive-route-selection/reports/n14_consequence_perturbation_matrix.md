# N14 Consequence Perturbation And Replay Matrix

Status: `passed`.

## Acceptance State

```text
accepted_perturbation_replay_matrix_pending_claim_classification
```

## Interpretation

```json
{
  "acceptance_state": "accepted_perturbation_replay_matrix_pending_claim_classification",
  "next_required_step": "Run Iteration 7 claim boundary and AP4 classification.",
  "plain_language_interpretation": "Iteration 6 handles the Iteration 5 control-clean candidate by testing whether route choice changes only when serialized source-backed consequence inputs change, and whether replay is stable for unchanged inputs. The positive variants select the route favored by the active support, memory, or regulation component; stale and budget-invalid cases fail closed. Final AP4 remains pending until Iteration 7 freezes the claim boundary.",
  "record_id": "n14_i6_interpretation_perturbation_replay_v1",
  "supported_interpretation": "N14 Iteration 6 shows that the provisional AP4 candidate is source-sensitive and replay-stable at artifact level: support, memory, and regulation perturbation variants alter the selected route only through serialized source-backed consequence inputs, while duplicate, artifact-only, snapshot/load, and order-inverted replays remain stable.",
  "unsupported_interpretations": [
    "final AP4 support before claim classification",
    "native support",
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

## Perturbation Records

| Variant | Changed components | Observed | Blocker | Passed |
| --- | --- | --- | --- | --- |
| `baseline_memory_dominant_replay` | `none` | `selected:route_b` | `none` | `true` |
| `support_risk_active_variant` | `route_specific_support_component` | `selected:route_a` | `none` | `true` |
| `memory_effect_variant` | `memory_delta_component` | `selected:route_a` | `none` | `true` |
| `regulation_deficit_variant` | `route_specific_regulation_component` | `selected:route_a` | `none` | `true` |
| `budget_invalid_high_consequence_variant` | `budget_validity` | `blocked` | `budget_invalid_route_blocked` | `true` |
| `stale_record_replay_variant` | `source_window` | `blocked` | `stale_consequence_record_blocked` | `true` |

## Replay Records

| Replay | First route | Second route | Stable |
| --- | --- | --- | --- |
| `duplicate_replay_stability` | `route_b` | `route_b` | `true` |
| `artifact_only_replay_stability` | `route_b` | `route_b` | `true` |
| `snapshot_load_replay_stability` | `route_b` | `route_b` | `true` |
| `order_inversion_replay_stability` | `route_b` | `route_b` | `true` |

Iteration 6 tests source-sensitive perturbation and replay stability
for the Iteration 5 control-clean candidate. It does not close final
`AP4`, does not open Phase 8, and does not claim agency or native
support.

## Checks

```json
{
  "all_perturbation_records_passed": true,
  "artifact_only_replay_stable": true,
  "artifact_only_replay_uses_filesystem_roundtrip": true,
  "budget_invalid_high_consequence_route_rejected": true,
  "budget_validity_checked_before_ranking": true,
  "claim_flags_forced_false": true,
  "consequence_rank_source_validated_before_ranking": true,
  "control_matrix_source_passed": true,
  "duplicate_replay_stable": true,
  "final_ap4_not_supported": true,
  "memory_effect_variant_changes_route_ranking_only_through_source_backed_memory_input": true,
  "native_support_opened_false": true,
  "no_producer_direct_mutation_recorded": true,
  "order_inversion_replay_stable": true,
  "phase8_opened_false": true,
  "regulation_deficit_variant_changes_route_ranking_only_through_source_backed_regulation_input": true,
  "runtime_state_used_false": true,
  "selection_source_passed": true,
  "snapshot_load_replay_stable": true,
  "snapshot_load_replay_uses_filesystem_roundtrip": true,
  "src_diff_empty": true,
  "stale_consequence_record_rejected": true,
  "support_risk_variant_changes_route_ranking_only_through_source_backed_support_input": true
}
```

## Claim Boundary

```text
perturbation replay pass != final AP4 support before claim classification
source-sensitive route ranking != intention
artifact-level replay stability != native support
support perturbation variant != semantic goal ownership
memory/regulation perturbation variant != agency
N14 Iteration 6 != fully native integration
```

## Output Digest

```text
3d207f963e6d3ed049c01bfcf75235c2cb8780d79e0cbe14d8ab349d7b6674e9
```
