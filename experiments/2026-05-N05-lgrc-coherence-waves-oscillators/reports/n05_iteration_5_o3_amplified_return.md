# N05 Iteration 5 O3 Amplified Return

Status: passed

Command:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_5_o3_amplified_return.py
```

## Result

| Field | Value |
|---|---|
| O-level | `O3` |
| claim ceiling | `amplified_return_candidate` |
| outbound amount | `0.25` |
| return amount | `0.5` |
| return excess | `0.25` |
| reservoir before/release-after/final | `0.5 -> 0.25 -> 0.25` |
| return packet | `lgrc9v3-packet-927bd854ad4c07a5` |
| budget error | `0.0` |
| row schema compliance | `True` |

## Packet Chain

| Phase | Event kind | Packet | Source | Target | Amount | T_e | Causal epoch |
|---|---|---|---|---|---|---|---|
| `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `0.25` | `0.0` | `post_update` |
| `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `0.25` | `1.0` | `post_update` |
| `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `0.25` | `1.0` | `post_update` |
| `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `0.25` | `2.0` | `post_update` |
| `reservoir_release` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-baaacfda7cf1b600` | `3` | `2` | `0.25` | `2.0` | `post_update` |
| `reservoir_release` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-baaacfda7cf1b600` | `3` | `2` | `0.25` | `3.0` | `post_update` |
| `amplified_return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-ed4719d1115035b9` | `2` | `1` | `0.5` | `3.0` | `post_update` |
| `amplified_return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-ed4719d1115035b9` | `2` | `1` | `0.5` | `4.0` | `post_update` |
| `amplified_return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-927bd854ad4c07a5` | `1` | `0` | `0.5` | `4.0` | `post_update` |
| `amplified_return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-927bd854ad4c07a5` | `1` | `0` | `0.5` | `5.0` | `post_update` |

## Reservoir Policy

```json
{
  "hidden_reservoir_array_used": false,
  "not_before_event_time_key": 2.0,
  "not_before_scheduler_event_index": 4,
  "observed_value_before_release": 0.5,
  "observed_value_field": "node_coherence",
  "policy_id": "n05_o3_declared_target_reservoir_release_policy_v1",
  "reference_value": 0.5,
  "release_amount": 0.25,
  "reservoir_node_id": 3,
  "reservoir_runtime_visible": true,
  "return_amount": 0.5,
  "return_excess": 0.25,
  "route_id": "n05_o3_declared_target_reservoir_release_route_v1",
  "source_event_digest": "19b5e94f09fd1f3fa5a380b28b9b6827fb6c6fb8cccfc0f8e965c1da9ab69346",
  "source_event_id": "lgrc9v3-packet-event-39c554bb549d6020",
  "source_event_kind": "lgrc9v3_packet_arrival",
  "threshold_sources_serialized": true
}
```

## Amplification Accounting

```json
{
  "amplification_source_detail": "declared_target_reservoir_node",
  "amplification_source_kind": "target_reservoir",
  "observed_value_source": "runtime_node_coherence",
  "outbound_amount": 0.25,
  "reservoir_budget_after": 0.25,
  "reservoir_budget_before": 0.5,
  "reservoir_delta": 0.25,
  "reservoir_hidden_array_used": false,
  "reservoir_runtime_visible": true,
  "reservoir_source_serialized": true,
  "return_amount": 0.5,
  "return_amount_exceeds_outbound": true,
  "return_excess": 0.25,
  "return_excess_debited": 0.25,
  "return_excess_matches_reservoir_debit": true,
  "silent_amplification_used": false,
  "status": "passed",
  "target_reservoir_after": 0.25,
  "target_reservoir_after_release": 0.25,
  "target_reservoir_before": 0.5,
  "target_reservoir_node_id": 3
}
```

## Artifact Replay

```json
{
  "amplification_accounting_ok": true,
  "artifact_only": true,
  "event_time_order_monotonic": true,
  "outbound_contact_release_return_reconstructed": true,
  "outbound_packet_pairs_ok": true,
  "passed": true,
  "reservoir_release_after_target_contact": true,
  "reservoir_release_packet_pairs_ok": true,
  "return_after_reservoir_release": true,
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
| `hidden_reservoir` | `n05_hidden_reservoir_rejected` | `manifest_policy_gate_check` | True |
| `undeclared_source` | `n05_undeclared_reservoir_source` | `runtime_control` | True |
| `budget_mismatch` | `n05_node_plus_packet_budget_mismatch` | `artifact_accounting_control` | True |
| `negative_reservoir` | `n05_negative_reservoir_rejected` | `runtime_control` | True |
| `silent_amplification` | `n05_silent_amplification_rejected` | `artifact_accounting_control` | True |
| `producer_mutation` | `n05_producer_mutation_boundary_violation` | `runtime_artifact_control` | True |
| `claim_promotion` | `n05_claim_promotion_rejected` | `artifact_claim_boundary_control` | True |

## Deferred Shared Controls

| Control | Status | Reason |
|---|---|---|
| `missing_target` | `not_rerun_in_o3` | covered by Iteration 2 fixture manifest controls; O3 ran O3-specific reservoir controls |
| `missing_route` | `not_rerun_in_o3` | covered by Iteration 3 route control; O3 route ids are serialized in the artifact |
| `stale_producer_read` | `not_rerun_in_o3` | reserved for later producer-state or repeated-cycle lanes |
| `idempotent_duplicate_production` | `not_rerun_in_o3` | reserved for repeated-cycle lanes where duplicate cycle production is meaningful |
| `snapshot_continue_after_load` | `not_rerun_in_o3` | reserved for later repeated-cycle or closeout lanes |

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O3 is an amplified-return evidence classification only.
