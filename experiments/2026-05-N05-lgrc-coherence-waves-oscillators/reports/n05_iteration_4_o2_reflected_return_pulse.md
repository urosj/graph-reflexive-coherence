# N05 Iteration 4 O2 Reflected Return Pulse

Status: passed

Command:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_4_o2_reflected_return_pulse.py
```

## Result

| Field | Value |
|---|---|
| O-level | `O2` |
| claim ceiling | `reflected_pulse_candidate` |
| fixture | `N05_S0_source_target_reservoir_chain_v1` |
| outbound route | `n05_o1_source_to_target_route_v1` |
| return route | `n05_o2_target_to_source_return_route_v1` |
| target contact event | `lgrc9v3-packet-event-39c554bb549d6020` |
| return source-contact event | `lgrc9v3-packet-event-daaf47b678a56237` |
| outbound packet | `lgrc9v3-packet-aee1863b655fbd5a` |
| return packet | `lgrc9v3-packet-3e430fa14f438186` |
| causal delay | `4.0` |
| return causal delay | `2.0` |
| budget error | `0.0` |
| row schema compliance | `True` |

## Packet Chain

| Phase | Event kind | Packet | Source | Target | T_e | Causal epoch |
|---|---|---|---|---|---|---|
| `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `0.0` | `post_update` |
| `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `1.0` | `post_update` |
| `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `1.0` | `post_update` |
| `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `2.0` | `post_update` |
| `return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-d7c6dd16ecba4d70` | `2` | `1` | `2.0` | `post_update` |
| `return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-d7c6dd16ecba4d70` | `2` | `1` | `3.0` | `post_update` |
| `return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-3e430fa14f438186` | `1` | `0` | `3.0` | `post_update` |
| `return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-3e430fa14f438186` | `1` | `0` | `4.0` | `post_update` |

## Return Eligibility

```json
{
  "committed_target_contact_required": true,
  "hidden_return_timing_used": false,
  "not_before_event_time_key": 2.0,
  "not_before_scheduler_event_index": 4,
  "record_id": "n05-o2-return-eligibility-19b5e94f09fd1f3fa5a380b2",
  "record_kind": "n05_return_eligibility_from_committed_target_contact",
  "return_route_id": "n05_o2_target_to_source_return_route_v1",
  "source_event_digest": "19b5e94f09fd1f3fa5a380b28b9b6827fb6c6fb8cccfc0f8e965c1da9ab69346",
  "source_event_id": "lgrc9v3-packet-event-39c554bb549d6020",
  "source_packet_id": "lgrc9v3-packet-aee1863b655fbd5a",
  "source_route_id": "n05_o1_source_to_target_route_v1"
}
```

## Artifact Replay

```json
{
  "artifact_only": true,
  "event_time_order_monotonic": true,
  "outbound_packet_pairs_ok": true,
  "outbound_to_contact_to_return_reconstructed": true,
  "passed": true,
  "return_linkage_ok": true,
  "return_packet_pairs_ok": true,
  "runtime_state_used": false,
  "scheduled_events_exist": true,
  "scheduler_order_monotonic": true,
  "target_contact_digest_matches": true
}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
| `policy_disabled` | `n05_policy_disabled_noop` | `runtime_control` | True |
| `missing_contact` | `n05_missing_target_contact` | `structural_validator_control` | True |
| `stale_outbound` | `n05_stale_outbound_contact` | `structural_linkage_control` | True |
| `hidden_schedule` | `n05_hidden_return_schedule_rejected` | `runtime_control` | True |
| `budget_mismatch` | `n05_node_plus_packet_budget_mismatch` | `runtime_control` | True |
| `producer_mutation` | `n05_producer_mutation_boundary_violation` | `runtime_control` | True |
| `claim_promotion` | `n05_claim_promotion_rejected` | `runtime_control` | True |

`missing_contact` and `stale_outbound` are structural validator/linkage
controls in O2. They prove the return eligibility record cannot validate
without the committed target-contact event digest, but they are not independent
runtime replay lanes.

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O2 is a reflected-return evidence classification only.
