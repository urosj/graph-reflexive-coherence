# N29 Iteration 11-B - Trace / Pressure / Loop Runtime Controls

## Summary

- status: `passed`
- acceptance_state: `accepted_trace_pressure_loop_runtime_controls_fail_closed_producer_assisted_only`
- failed_open_count: `0`
- runtime_executed_control_count: `9`
- claim_ceiling: `perturbation_control_backed_runtime_bridge_candidate_no_ecology_success`
- ready_for_iteration_11C: `true`
- output_digest: `5c9aaaf087c783fd82d330ade313a589519a787532154aa613a98f4142cd582a`

I11-B consumes I11-A as the runtime surface and I11 as the lineage and
claim-boundary source. I11 alone is not treated as runtime evidence.

## Control Results

| Control | Status | Runtime | Rung Effect |
| --- | --- | --- | --- |
| `no_parent_arrival_trace_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `below_threshold_pressure_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `near_threshold_margin_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `wrong_expected_channel_control` | `failed_closed` | `false` | `preserves_i11a_only_if_failed_closed` |
| `route_aspect_digest_mismatch_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `channel_sequence_shuffle_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `same_causal_surface_replay_idempotency_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `direct_queue_injection_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `unprocessed_child_departure_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `producer_disabled_control` | `failed_closed` | `true` | `preserves_i11a_only_if_failed_closed` |
| `semantic_pheromone_hunger_relabel_control` | `failed_closed` | `false` | `preserves_claim_ceiling_only_if_failed_closed` |
| `producer_success_as_native_runtime_success_control` | `failed_closed` | `false` | `admits_only_producer_assisted_control_backed_candidate` |

## Runtime Interpretation

The runtime controls remove or corrupt each required leg of the I11-A
bridge. Without the returned parent-arrival trace, no route-surplus
pressure trigger is admitted. Below threshold, no child packet is
scheduled. With wrong route expectation, shuffled sequence, or route
digest mismatch, local packet activity cannot backfill the canonical
trace/pressure/loop row. Direct queue injection and unprocessed child
departure controls show that producer ownership and `step()` processing
are both required. The semantic controls reject pheromone, hunger, ant
behavior, native ecology, and agency relabels.

This backs I11-A as a perturbation-control-backed producer-assisted
runtime bridge candidate. It does not make native ecology, native
shared-medium coordination, semantic communication, or agency claims.

## Checks

| Check | Passed |
| --- | --- |
| `i11_source_passed` | `true` |
| `i11a_source_passed` | `true` |
| `i11a_runtime_artifact_present` | `true` |
| `all_required_controls_present` | `true` |
| `failed_open_count_zero` | `true` |
| `runtime_controls_executed_where_applicable` | `true` |
| `semantic_controls_are_claim_controls_only` | `true` |
| `producer_success_does_not_upgrade_native` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `ready_for_iteration_11C` | `true` |
| `no_absolute_paths_in_records` | `true` |
