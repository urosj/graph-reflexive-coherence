# N09 Iteration 5 GPR3 Proxy-Conditioned Eligibility

Status: passed.

Iteration 5 emits proxy-conditioned eligibility and route-candidate score evidence from the serialized GPR2 error signal. It compares the same proxy, target, and regulation policy with and without N08 memory surface evidence. It does not select a route, schedule packets, call step(), or mutate state.

## Result

- GPR level: `GPR3`
- Claim ceiling: `proxy_conditioned_route_selection_candidate`
- Error direction: `decrease_proxy`
- Route arbitration emitted: `false`
- Packet scheduling used: `false`
- `step()` called: `false`

## Lane Comparison

- Same proxy/target/policy: `true`
- No-memory scores: `[1.07, 1.07]`
- Memory-shaped scores: `[1.825, 1.87]`
- Memory changes candidate ranking: `true`
- No-memory classification: `no_memory_proxy_conditioned_eligibility_tied_candidates`
- Memory-shaped classification: `memory_shaped_proxy_conditioned_eligibility_ranked_candidates`
- Memory surface digest: `b21c093d70245fab02088b8ebed42ac931629c41f6e45d618f5b5a67d9bea627`
- Memory policy digest: `bd003905a6c189a1c44babbeb80d931b2dd4d3ce27eb3b1788aefbaefb8198eb`
- Memory strength: `0.7`

## Candidate Sets

- Memory-shaped candidate set digest: `134e35907533c2da88e567dfcfa83db5e68b885f55c25f6c09e478395f328ffa`
- No-memory candidate set digest: `a0b0828fcadc58fbc69af2dfc2ca74973870abb8fd04e6ed999d7b32749ccfb1`

## Controls

- `claim_promotion`: `claim_promotion_blocked` (passed: `true`)
- `experiment_side_if_else`: `experiment_side_if_else_rejected` (passed: `true`)
- `hidden_proxy`: `hidden_proxy_source_rejected` (passed: `true`)
- `memory_surface_missing`: `memory_surface_missing_for_memory_lane` (passed: `true`)
- `memory_surface_not_used`: `memory_surface_not_used` (passed: `true`)
- `memory_surface_read_in_no_memory_lane`: `memory_surface_read_in_no_memory_lane` (passed: `true`)
- `no_error_control`: `no_error_non_trigger` (passed: `true`)
- `producer_mutation`: `producer_direct_mutation_blocked` (passed: `true`)
- `stale_proxy_read`: `stale_proxy_read_blocked` (passed: `true`)
- `wrong_error_control`: `wrong_direction_response` (passed: `true`)

## Validation Checks

- `candidate_budget_predictions_present`: `true`
- `candidate_ranking_not_committed_route_selection`: `true`
- `candidate_route_digests_recompute`: `true`
- `candidate_scores_equal_component_sums`: `true`
- `candidate_set_digests_recompute`: `true`
- `claim_flags_all_false`: `true`
- `controls_all_passed`: `true`
- `eligibility_depends_on_error_direction`: `true`
- `error_signal_digest_recomputes`: `true`
- `manifest_digest_recomputes`: `true`
- `memory_budget_separate_from_node_plus_packet`: `true`
- `memory_changes_candidate_ranking`: `true`
- `memory_lane_uses_n08_memory_surface`: `true`
- `n08_memory_source_status_passed`: `true`
- `no_memory_lane_has_no_memory_surface`: `true`
- `no_scheduling_or_step`: `true`
- `producer_does_not_mutate_state`: `true`
- `producer_record_linkage_complete`: `true`
- `producer_records_digest_recompute`: `true`
- `proxy_conditioned_eligibility_emitted`: `true`
- `regulation_policy_digest_recomputes`: `true`
- `same_proxy_target_policy_for_both_lanes`: `true`
- `source_gpr2_artifact_digest_recomputes`: `true`
- `source_gpr2_status_passed`: `true`

## Acceptance State

Achieved. Proxy error changes route/producer eligibility evidence through serialized runtime-visible inputs, the memory-shaped lane is explicitly compared with a no-memory comparator, and the producer/step and claim boundaries remain intact.

## Replay

```bash
.venv/bin/python experiments/2026-05-N09-lgrc-goal-proxy-regulation/scripts/run_n09_iteration_5_gpr3_proxy_conditioned_eligibility.py
```
