# N10 Iteration 8 Bounded Repeated Integration

Status: `passed`.

## Result

Iteration 8 replayed a bounded four-cycle integration window. The main
support-intact row and the mild-withdrawal companion both remain
source-current, budget-safe, artifact-only, and claim-clean.

This is `ALI5`, not final `ALI6`. Iteration 9 still has to run the
artifact-only closeout validator before N10 can decide its final A6
ceiling.

```text
main.integration_level = A5
main.n10_category_level = ALI5
main.accepted_integration_level = A5
companion.support_state_tag = mild_withdrawal_survives
window_count = 4
node_plus_packet_budget_error = 0.0
artifact_only = true
runtime_state_used = false
```

## Main Row Summary

```json
{
  "a6_relevance": "bounded_repeated_integration_component_not_a6_closeout",
  "accepted_integration_level": "A5",
  "attempted_integration_level": "A6",
  "bounded_window": {
    "all_cycle_budgets_exact": true,
    "all_cycle_claim_flags_false": true,
    "all_cycle_rows_source_current": true,
    "cycle_row_digests": [
      "fa8fcc6b5e26b22bb90be245b33379dc6c07bca2b4b9950c6844bf8eac139280",
      "1890024f767604c20414e535a1d374f466198dd59c7ff77f1598cf46880896df",
      "d7add93b5cb9d621338458e3a8d2ce0a43f0a2880ef6262337282cdaced85651",
      "ce4c8d461731db9796c26226e5936be3465dd15d254e56b250e28acc1273f2c5"
    ],
    "duplicate_cycle_rows_suppressed": true,
    "window_count": 4,
    "window_digest": "7a67f3a8c2d5a0c102b8185b91792ae8371acbb21c86ea07c3fc2a7265a3a1ca"
  },
  "budget_mode": "bounded_replay_uses_n09_same_run_node_plus_packet_budget; route, memory, support, and proxy surfaces remain separately audited source-artifact evidence",
  "integration_level": "A5",
  "integration_outcome_tag": "bounded_artifact_only_agentic_like_integration_candidate",
  "integration_row_id": "n10_i8_bounded_repeated_integration_row_v1",
  "memory_scope_tag": "artifact_only_serialized_producer_policy_route_memory_or_trail",
  "n10_category_level": "ALI5",
  "regulation_scope_tag": "artifact_only_goal_proxy_regulation_candidate",
  "route_context_tag": "route_context_selection_only",
  "support_state_tag": "support_intact_survives"
}
```

## Mild-Withdrawal Companion

```json
{
  "accepted_integration_level": "A5",
  "bounded_window": {
    "all_cycle_budgets_exact": true,
    "all_cycle_claim_flags_false": true,
    "all_cycle_rows_source_current": true,
    "cycle_row_digests": [
      "b63f13fbbf8e0863bbdc5ab1dc0497e8acdcf96abf695a27a877c78a34f279da",
      "f383f63eef1ed5bf93708f7fe13a6270281cd05d7d9d720bfc0edda442f2ca2f",
      "a712578ace121bf3a1221ff028f377fc98ff11e81e6af7b15ad5a2332bb11878",
      "a5fb1edf250b10ef46539693a972add3e975d5e061b9a3b29c4e91e2d213d9b8"
    ],
    "duplicate_cycle_rows_suppressed": true,
    "window_count": 4,
    "window_digest": "276ac737252043bad0bc92f9a5a32f6bb7103320357420b249f8995f805d3658"
  },
  "companion_scope": "mild_withdrawal_same_artifact_window_only",
  "integration_level": "A5",
  "integration_row_id": "n10_i8_bounded_repeated_integration_mild_withdrawal_companion_row_v1",
  "n10_category_level": "ALI5",
  "support_evidence": {
    "final_A_support_retention": 0.8758382186202335,
    "final_basin_separability": 0.8758382186202335,
    "final_budget_error": 0.0,
    "identity_support_outcome_tag": "support_withdrawal_survival_baseline",
    "lane_digest": "d5fae1cee95b0650287173c3e0456f1df42464771336b4e6e02cfb4e095bff69",
    "manifest_lane_digest": "d5fae1cee95b0650287173c3e0456f1df42464771336b4e6e02cfb4e095bff69",
    "reference_A_support_retention": 0.9731535762447039,
    "restoration_fraction": 0.0,
    "source_lane_id": "mild_support_weakening",
    "support_loss_from_reference": 0.09731535762447041,
    "support_state_tag": "mild_withdrawal_survives",
    "support_survival_passed": true,
    "support_survival_threshold": 0.85,
    "withdrawal_depth": 0.1,
    "withdrawal_kind": "partial_support_weakening"
  },
  "support_state_tag": "mild_withdrawal_survives"
}
```

## Cycle Rows

```json
[
  {
    "bounded_cycle_row_digest": "fa8fcc6b5e26b22bb90be245b33379dc6c07bca2b4b9950c6844bf8eac139280",
    "claim_flags_false": true,
    "cycle_index": 1,
    "memory_budget_error": 0.0,
    "memory_budget_surface": "trail_strength",
    "memory_route_a_strength_after_cycle": 0.5895,
    "memory_route_b_strength_after_cycle": 0.88,
    "memory_selected_route": "route_b",
    "memory_source_current": true,
    "memory_strength_used_as_physical_flux": false,
    "memory_surface_scope": "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "node_plus_packet_budget_after": 1.5,
    "node_plus_packet_budget_before": 1.5,
    "node_plus_packet_budget_error": 0.0,
    "proxy_budget_error": 0.0,
    "proxy_budget_surface": "active_node_coherence_band",
    "regulation_cycle_index": 1,
    "regulation_error_signal_digest": "9b0dd641a39bf5a23ca01301ed6cef497915340b75573641b1e7677a7121bfac",
    "regulation_outcome_tag": "single_cycle_band_return",
    "regulation_post_response_proxy_surface_digest": "c683d33c5779e50c404d0d3df74dba8366531d2652adadc8de7d2708355daa13",
    "regulation_pre_response_proxy_surface_digest": "6c9fad8c06896aef60fe78f2f198b47d22158d0565a2d4e880d12856758f89f4",
    "regulation_processed_packet_id": "lgrc9v3-packet-a73dadd6e5eb7584",
    "regulation_proxy_surface_digest": "6c9fad8c06896aef60fe78f2f198b47d22158d0565a2d4e880d12856758f89f4",
    "regulation_response_digest": "e764425f585c2d7a63b0b03ae7517d22acf070e205378f8377930a61d2238d81",
    "regulation_scheduled_packet_id": "lgrc9v3-packet-a73dadd6e5eb7584",
    "regulation_selected_candidate_route_digest": "c6901dc48bc5862977cc9d9da4607e0a763ffd378f35459e9b5800265646a74d",
    "regulation_selected_route": "route_b",
    "regulation_source_current": true,
    "regulation_top_ranked_is_unique": true,
    "route_candidate_set_digest": "cc28d581e856d3782a840c63157f7b1d4d565387e8c00ed28b8365cba7b5f4a9",
    "route_context_tag": "route_context_selection_only",
    "route_cycle_id": "cycle_0",
    "route_replay_ok": true,
    "route_scheduled_processed_packet_applicability": "not_applicable_pre_topology_selection_only_scope",
    "route_selected_candidate_route_digest": "7e94c09f12ba57b1a057b462d3e3f8931a65e399511ad5fd8255fdc97d5cdcd8",
    "route_selected_candidate_route_score": 1.0,
    "route_selected_route": "route_a",
    "route_selection_contract_valid_under_pre_topology_scope": true,
    "route_source_current": true,
    "support_budget_error": 0.0,
    "support_lane_digest": "359d248493fc4ce8ee57f5f682d043cc745762671ab1a67fb8c779e38ed67bdb",
    "support_lane_id": "support_intact_reference",
    "support_retention": 0.9731535762447039,
    "support_source_current": true,
    "support_state_tag": "support_intact_survives",
    "support_survival_passed": true
  },
  {
    "bounded_cycle_row_digest": "1890024f767604c20414e535a1d374f466198dd59c7ff77f1598cf46880896df",
    "claim_flags_false": true,
    "cycle_index": 2,
    "memory_budget_error": 0.0,
    "memory_budget_surface": "trail_strength",
    "memory_route_a_strength_after_cycle": 0.53055,
    "memory_route_b_strength_after_cycle": 1.0,
    "memory_selected_route": "route_b",
    "memory_source_current": true,
    "memory_strength_used_as_physical_flux": false,
    "memory_surface_scope": "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "node_plus_packet_budget_after": 1.5,
    "node_plus_packet_budget_before": 1.5,
    "node_plus_packet_budget_error": 0.0,
    "proxy_budget_error": 0.0,
    "proxy_budget_surface": "active_node_coherence_band",
    "regulation_cycle_index": 2,
    "regulation_error_signal_digest": "ffa84e448e3b4ae54776baabf2c4f4a2df0d01c700732a80f97ff1a1292df487",
    "regulation_outcome_tag": "single_cycle_band_return",
    "regulation_post_response_proxy_surface_digest": "66a1b8300825047fcd8753808b52229083fa78ee09c15dcd1dd0f6ad934d7ce1",
    "regulation_pre_response_proxy_surface_digest": "7b8c9a910c07f29dacc1505af8064dc468aa65e5fb1e1d536bc6f36dc901e88f",
    "regulation_processed_packet_id": "lgrc9v3-packet-a02eb5d11f60ccf8",
    "regulation_proxy_surface_digest": "7b8c9a910c07f29dacc1505af8064dc468aa65e5fb1e1d536bc6f36dc901e88f",
    "regulation_response_digest": "0ebef74ae51ad8a22f7fad82533850b12855eaedc830090aa20753b6a6791cbb",
    "regulation_scheduled_packet_id": "lgrc9v3-packet-a02eb5d11f60ccf8",
    "regulation_selected_candidate_route_digest": "c6901dc48bc5862977cc9d9da4607e0a763ffd378f35459e9b5800265646a74d",
    "regulation_selected_route": "route_b",
    "regulation_source_current": true,
    "regulation_top_ranked_is_unique": true,
    "route_candidate_set_digest": "5c8918b0cdf07c3c5b303bf2c71d4c5c184370f5b875dc01af6b3aaff2506648",
    "route_context_tag": "route_context_selection_only",
    "route_cycle_id": "cycle_1",
    "route_replay_ok": true,
    "route_scheduled_processed_packet_applicability": "not_applicable_pre_topology_selection_only_scope",
    "route_selected_candidate_route_digest": "21ff5096388e202c1c708be518b6966013049873a36fb34e9eedf245e9d79c63",
    "route_selected_candidate_route_score": 1.0,
    "route_selected_route": "route_b",
    "route_selection_contract_valid_under_pre_topology_scope": true,
    "route_source_current": true,
    "support_budget_error": 0.0,
    "support_lane_digest": "359d248493fc4ce8ee57f5f682d043cc745762671ab1a67fb8c779e38ed67bdb",
    "support_lane_id": "support_intact_reference",
    "support_retention": 0.9731535762447039,
    "support_source_current": true,
    "support_state_tag": "support_intact_survives",
    "support_survival_passed": true
  },
  {
    "bounded_cycle_row_digest": "d7add93b5cb9d621338458e3a8d2ce0a43f0a2880ef6262337282cdaced85651",
    "claim_flags_false": true,
    "cycle_index": 3,
    "memory_budget_error": 0.0,
    "memory_budget_surface": "trail_strength",
    "memory_route_a_strength_after_cycle": 0.477495,
    "memory_route_b_strength_after_cycle": 1.0,
    "memory_selected_route": "route_b",
    "memory_source_current": true,
    "memory_strength_used_as_physical_flux": false,
    "memory_surface_scope": "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "node_plus_packet_budget_after": 1.5,
    "node_plus_packet_budget_before": 1.5,
    "node_plus_packet_budget_error": 0.0,
    "proxy_budget_error": 0.0,
    "proxy_budget_surface": "active_node_coherence_band",
    "regulation_cycle_index": 3,
    "regulation_error_signal_digest": "d6937ea53d83fa7fdc7c3b6c218221885084d23a3b45a89731362318f11ffe0a",
    "regulation_outcome_tag": "single_cycle_band_return",
    "regulation_post_response_proxy_surface_digest": "86ec3a9da1865149822985f0ad55746a1a34f82f7459b7b954fe5283307ad099",
    "regulation_pre_response_proxy_surface_digest": "fdfb78fe402dd54438f4429524cd06284cef535bd0f418b3d5a898b6fd93ccba",
    "regulation_processed_packet_id": "lgrc9v3-packet-50d44a93bc735943",
    "regulation_proxy_surface_digest": "fdfb78fe402dd54438f4429524cd06284cef535bd0f418b3d5a898b6fd93ccba",
    "regulation_response_digest": "b92f6c3d54d118e9780ffa5c4961745512707eb11b1e1b014a76232d149e16e8",
    "regulation_scheduled_packet_id": "lgrc9v3-packet-50d44a93bc735943",
    "regulation_selected_candidate_route_digest": "c6901dc48bc5862977cc9d9da4607e0a763ffd378f35459e9b5800265646a74d",
    "regulation_selected_route": "route_b",
    "regulation_source_current": true,
    "regulation_top_ranked_is_unique": true,
    "route_candidate_set_digest": "30217e1dcc8c533d3175131d2b2be0a265829a41714fe338a1330982b6c8e510",
    "route_context_tag": "route_context_selection_only",
    "route_cycle_id": "cycle_2",
    "route_replay_ok": true,
    "route_scheduled_processed_packet_applicability": "not_applicable_pre_topology_selection_only_scope",
    "route_selected_candidate_route_digest": "56df5ea777c43a139b3d26d314b41affc82cedafd8dc54e7f1af615cb43d52a1",
    "route_selected_candidate_route_score": 1.0,
    "route_selected_route": "route_a",
    "route_selection_contract_valid_under_pre_topology_scope": true,
    "route_source_current": true,
    "support_budget_error": 0.0,
    "support_lane_digest": "359d248493fc4ce8ee57f5f682d043cc745762671ab1a67fb8c779e38ed67bdb",
    "support_lane_id": "support_intact_reference",
    "support_retention": 0.9731535762447039,
    "support_source_current": true,
    "support_state_tag": "support_intact_survives",
    "support_survival_passed": true
  },
  {
    "bounded_cycle_row_digest": "ce4c8d461731db9796c26226e5936be3465dd15d254e56b250e28acc1273f2c5",
    "claim_flags_false": true,
    "cycle_index": 4,
    "memory_budget_error": 0.0,
    "memory_budget_surface": "trail_strength",
    "memory_route_a_strength_after_cycle": 0.4297455,
    "memory_route_b_strength_after_cycle": 1.0,
    "memory_selected_route": "route_b",
    "memory_source_current": true,
    "memory_strength_used_as_physical_flux": false,
    "memory_surface_scope": "artifact_only_serialized_producer_policy_route_memory_or_trail",
    "node_plus_packet_budget_after": 1.5,
    "node_plus_packet_budget_before": 1.5,
    "node_plus_packet_budget_error": 0.0,
    "proxy_budget_error": 0.0,
    "proxy_budget_surface": "active_node_coherence_band",
    "regulation_cycle_index": 4,
    "regulation_error_signal_digest": "542472163274a5fcef6ffd557f8ec751b2cc0dfd815668d730a6686e69735b95",
    "regulation_outcome_tag": "single_cycle_band_return",
    "regulation_post_response_proxy_surface_digest": "2368386da12d613bf88c82c9240856fa29fbeeafae15a33a59a5074dc16da9c3",
    "regulation_pre_response_proxy_surface_digest": "739a70708fb55a057fbacd43c4a7857eeb679ba5c2027468072fb0728c354852",
    "regulation_processed_packet_id": "lgrc9v3-packet-766156e3c0c8d434",
    "regulation_proxy_surface_digest": "739a70708fb55a057fbacd43c4a7857eeb679ba5c2027468072fb0728c354852",
    "regulation_response_digest": "b09829ce116bf67a47976c5bf1965ea85bdfd382f9d5a34194795d8eb5eeeeba",
    "regulation_scheduled_packet_id": "lgrc9v3-packet-766156e3c0c8d434",
    "regulation_selected_candidate_route_digest": "c6901dc48bc5862977cc9d9da4607e0a763ffd378f35459e9b5800265646a74d",
    "regulation_selected_route": "route_b",
    "regulation_source_current": true,
    "regulation_top_ranked_is_unique": true,
    "route_candidate_set_digest": "cc8603974788f12118e143fb8f6c96ae3ef6eb1c021e3a6c6c14aba8469db765",
    "route_context_tag": "route_context_selection_only",
    "route_cycle_id": "cycle_3",
    "route_replay_ok": true,
    "route_scheduled_processed_packet_applicability": "not_applicable_pre_topology_selection_only_scope",
    "route_selected_candidate_route_digest": "1732ca519398908214633ffb085a0c5d25b7c772891a025f5e7c1df0a5da7304",
    "route_selected_candidate_route_score": 1.0,
    "route_selected_route": "route_b",
    "route_selection_contract_valid_under_pre_topology_scope": true,
    "route_source_current": true,
    "support_budget_error": 0.0,
    "support_lane_digest": "359d248493fc4ce8ee57f5f682d043cc745762671ab1a67fb8c779e38ed67bdb",
    "support_lane_id": "support_intact_reference",
    "support_retention": 0.9731535762447039,
    "support_source_current": true,
    "support_state_tag": "support_intact_survives",
    "support_survival_passed": true
  }
]
```

## Controls

```json
{
  "artifact_only_replay_missing_link": {
    "control_passed": true,
    "primary_blocker": "artifact_only_replay_missing_link",
    "reason": "bounded integration rows preserve all source links without private runtime fallback"
  },
  "bounded_window_length": {
    "control_passed": true,
    "primary_blocker": "bounded_window_incomplete",
    "reason": "Iteration 8 requires four source-backed repeated cycles in the main and companion lanes"
  },
  "budget_surface_ambiguity": {
    "control_passed": true,
    "primary_blocker": "budget_surface_ambiguity",
    "reason": "node-plus-packet, memory, support, and proxy budget surfaces are audited separately and remain exact"
  },
  "claim_promotion": {
    "control_passed": true,
    "primary_blocker": "claim_promotion_blocked",
    "reason": "ALI5 bounded repetition does not emit ACO, agency, A6, identity acceptance, or goal-ownership claims"
  },
  "duplicate_row_suppression": {
    "control_passed": true,
    "primary_blocker": "duplicate_integration_row",
    "reason": "cycle row digests are unique and main/companion rows have distinct digests"
  },
  "hidden_experiment_side_steering": {
    "control_passed": true,
    "primary_blocker": "hidden_experiment_side_steering",
    "reason": "route and memory-shaped regulation selections are serialized source evidence, not N10 if/else steering"
  },
  "mild_withdrawal_companion_survives": {
    "control_passed": true,
    "primary_blocker": "mild_withdrawal_companion_failed",
    "reason": "the companion lane remains above the support-survival threshold"
  },
  "source_artifact_digest_mismatch": {
    "control_passed": true,
    "primary_blocker": "source_artifact_digest_mismatch",
    "reason": "N06/N07/N08/N09 source artifact digests are rechecked against Iteration 1"
  },
  "stale_identity_support_baseline": {
    "control_passed": true,
    "primary_blocker": "stale_identity_support_baseline",
    "reason": "main and companion support lanes match current N07/manifest digests"
  },
  "stale_memory_surface": {
    "control_passed": true,
    "primary_blocker": "stale_memory_surface",
    "reason": "each cycle consumes N08 serialized memory/trail evidence and the stale-memory control remains passed"
  },
  "stale_regulation_window": {
    "control_passed": true,
    "primary_blocker": "stale_proxy_read_blocked",
    "reason": "each regulation cycle reads its current proxy/error digest"
  },
  "stale_route_context": {
    "control_passed": true,
    "primary_blocker": "stale_route_context",
    "reason": "each cycle consumes N06 under selection-only pre-topology scope"
  }
}
```

## Checks

```json
{
  "a6_not_supported_by_iteration_8": true,
  "attempted_a6_not_accepted": true,
  "bounded_window_count_is_four": true,
  "companion_all_budgets_exact": true,
  "companion_all_claim_flags_false": true,
  "companion_all_cycles_source_current": true,
  "companion_integration_level_is_a5": true,
  "companion_is_ali5": true,
  "companion_row_digest_valid": true,
  "companion_row_required_fields_present": true,
  "controls_passed": true,
  "main_all_budgets_exact": true,
  "main_all_claim_flags_false": true,
  "main_all_cycles_source_current": true,
  "main_integration_level_is_a5": true,
  "main_is_ali5": true,
  "main_row_digest_valid": true,
  "main_row_required_fields_present": true,
  "memory_scope_artifact_only_preserved": true,
  "mild_withdrawal_companion_lane": true,
  "route_context_selection_only_preserved": true,
  "source_artifact_digests_match_baseline": true,
  "src_clean_for_iteration_8": true,
  "support_intact_main_lane": true
}
```

## Acceptance

Iteration 8 passes if the bounded integration chain remains source-current, budget-safe, replayable, and claim-clean across repeated cycles, while the mild-withdrawal companion remains support-aware and A6/ALI6 closeout stays deferred to Iteration 9.

Acceptance state: `passed`.

## Run Record

```text
.venv/bin/python experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/run_n10_iteration_8_bounded_repeated_integration.py
```

Output digest:

```text
043ca2e2038bc6b402083b87758c57922b293761474b1215b719b932c6e42a58
```
