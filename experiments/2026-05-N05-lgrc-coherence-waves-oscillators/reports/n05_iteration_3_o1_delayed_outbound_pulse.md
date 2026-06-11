# N05 Iteration 3 O1 Delayed Outbound Pulse

Status: passed

Command:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_3_o1_delayed_outbound_pulse.py
```

## Result

| Field | Value |
|---|---|
| O-level | `O1` |
| claim ceiling | `delayed_pulse_candidate` |
| fixture | `N05_S0_source_target_reservoir_chain_v1` |
| route | `n05_o1_source_to_target_route_v1` |
| source node | `0` |
| target node | `2` |
| hop packets | `2` |
| canonical outbound packet | `lgrc9v3-packet-aee1863b655fbd5a` |
| causal epoch | `post_update` |
| causal delay | `2.0` |
| budget error | `0.0` |
| row schema compliance | `True` |
| target reservoir before/after | `0.5 -> 0.5` |
| return packet | `None` |
| cycle id | `None` |

## Packet Chain

| Event kind | Packet | Source | Target | T_e | Causal epoch |
|---|---|---|---|---|---|
| `lgrc9v3_packet_departure` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `0.0` | `post_update` |
| `lgrc9v3_packet_arrival` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `1.0` | `post_update` |
| `lgrc9v3_packet_departure` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `1.0` | `post_update` |
| `lgrc9v3_packet_arrival` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `2.0` | `post_update` |

## Artifact Replay

```json
{
  "artifact_only": true,
  "event_time_order_monotonic": true,
  "final_target_contact_node_matches": true,
  "packet_pairs_ok": true,
  "passed": true,
  "runtime_state_used": false,
  "scheduled_events_exist": true,
  "scheduler_order_monotonic": true,
  "source_to_outbound_packet_to_target_contact_reconstructed": true
}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
| `policy_disabled` | `n05_policy_disabled_noop` | `runtime_control` | True |
| `pulse_disabled` | `n05_pulse_disabled_no_packet` | `manifest_policy_gate_check` | True |
| `missing_source` | `n05_missing_source_node` | `runtime_control` | True |
| `missing_route` | `n05_missing_route` | `runtime_control` | True |
| `hidden_schedule` | `n05_hidden_schedule_rejected` | `runtime_control` | True |
| `budget_mismatch` | `n05_node_plus_packet_budget_mismatch` | `runtime_control` | True |
| `producer_mutation` | `n05_producer_mutation_boundary_violation` | `runtime_control` | True |
| `claim_promotion` | `n05_claim_promotion_rejected` | `runtime_control` | True |

The `pulse_disabled` control is a manifest/policy-gate check in O1, not an
independent runtime pulse-surface lane. O1 has no separate pulse surface:
packet emission is gated by the existing flux-route producer policy.

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O1 is a delayed-pulse evidence classification only.
