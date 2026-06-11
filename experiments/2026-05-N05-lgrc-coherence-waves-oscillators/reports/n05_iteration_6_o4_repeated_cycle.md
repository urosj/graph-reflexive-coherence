# N05 Iteration 6 O4 Repeated Cycle

Status: passed

Command:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_6_o4_repeated_cycle.py
```

## Result

| Field | Value |
|---|---|
| O-level | `O4` |
| claim ceiling | `repeated_oscillator_cycle_candidate` |
| cycle policy | `n05_o4_declared_repeated_cycle_policy_v1` |
| distinct cycles | `2` |
| run_autonomous used | `True` |
| native self-rearm validator used | `False` |
| causal delay semantics | `total_elapsed_event_time_across_recorded_o4_cycle_set` |
| per-cycle causal delays | `[5.0, 5.0]` |
| reservoir exhausted after recorded cycles | `True` |
| budget error | `0.0` |
| row schema compliance | `True` |

## Cycle Records

| Index | Cycle id | Target contact | Source contact | Reservoir before | Reservoir after | Budget error |
|---|---|---|---|---|---|---|
| `0` | `n05_o4_repeated_cycle_000` | `lgrc9v3-packet-event-39c554bb549d6020` | `lgrc9v3-packet-event-f49a67bce785cf50` | `0.5` | `0.25` | `0.0` |
| `1` | `n05_o4_repeated_cycle_001` | `lgrc9v3-packet-event-656577ce8913ff56` | `lgrc9v3-packet-event-7ac233d4bd0ef92d` | `0.25` | `0.0` | `0.0` |

## Packet Chain

| Cycle | Phase | Event kind | Packet | Source | Target | Amount | T_e | Causal epoch |
|---|---|---|---|---|---|---|---|---|
| `n05_o4_repeated_cycle_000` | `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `0.25` | `0.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-d5cdf187c9ea07b3` | `0` | `1` | `0.25` | `1.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `0.25` | `1.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-aee1863b655fbd5a` | `1` | `2` | `0.25` | `2.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `reservoir_release` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-baaacfda7cf1b600` | `3` | `2` | `0.25` | `2.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `reservoir_release` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-baaacfda7cf1b600` | `3` | `2` | `0.25` | `3.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `amplified_return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-ed4719d1115035b9` | `2` | `1` | `0.5` | `3.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `amplified_return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-ed4719d1115035b9` | `2` | `1` | `0.5` | `4.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `amplified_return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-927bd854ad4c07a5` | `1` | `0` | `0.5` | `4.0` | `post_update` |
| `n05_o4_repeated_cycle_000` | `amplified_return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-927bd854ad4c07a5` | `1` | `0` | `0.5` | `5.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-737ec4edaddfc54d` | `0` | `1` | `0.25` | `5.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-737ec4edaddfc54d` | `0` | `1` | `0.25` | `6.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `outbound` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-6055b501103a53af` | `1` | `2` | `0.25` | `6.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `outbound` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-6055b501103a53af` | `1` | `2` | `0.25` | `7.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `reservoir_release` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-914ab1cb9defda25` | `3` | `2` | `0.25` | `7.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `reservoir_release` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-914ab1cb9defda25` | `3` | `2` | `0.25` | `8.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `amplified_return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-708573af1b206177` | `2` | `1` | `0.5` | `8.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `amplified_return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-708573af1b206177` | `2` | `1` | `0.5` | `9.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `amplified_return` | `lgrc9v3_packet_departure` | `lgrc9v3-packet-a4987a4c62ca0328` | `1` | `0` | `0.5` | `9.0` | `post_update` |
| `n05_o4_repeated_cycle_001` | `amplified_return` | `lgrc9v3_packet_arrival` | `lgrc9v3-packet-a4987a4c62ca0328` | `1` | `0` | `0.5` | `10.0` | `post_update` |

## Autonomous Scope

```json
{
  "native_self_rearm_claim_allowed": false,
  "scope_limitation": "O4 repeats explicit source-target-source cycle segments through flux-route producer evidence. Native self-rearm evidence is reserved for O5 renewal, where the next cycle must be authorized by committed circuit state rather than explicit cycle-route configuration.",
  "used": false,
  "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts(...)"
}
```

## Artifact Replay

```json
{
  "all_cycles_same_declared_policy": true,
  "artifact_only": true,
  "budget_ok": true,
  "cycle_count_reconstructed": 2,
  "cycles_reconstructed": [
    {
      "cycle_budget_ok": true,
      "cycle_id": "n05_o4_repeated_cycle_000",
      "cycle_order_ok": true,
      "passed": true,
      "reservoir_release_reconstructed": true,
      "source_authorization_ok": true,
      "source_contact_reconstructed": true,
      "target_contact_reconstructed": true
    },
    {
      "cycle_budget_ok": true,
      "cycle_id": "n05_o4_repeated_cycle_001",
      "cycle_order_ok": true,
      "passed": true,
      "reservoir_release_reconstructed": true,
      "source_authorization_ok": true,
      "source_contact_reconstructed": true,
      "target_contact_reconstructed": true
    }
  ],
  "distinct_cycle_count": 2,
  "global_event_time_order_monotonic": true,
  "global_scheduler_order_monotonic": true,
  "hidden_schedule_absent": true,
  "outbound_packet_pairs_ok": true,
  "passed": true,
  "plateau_samples_counted_as_cycles": false,
  "plateau_samples_counted_as_cycles_false": true,
  "runtime_state_used": false,
  "scheduled_events_exist": true
}
```

## Duplicate Suppression Semantics

```json
{
  "cycle_ids_unique": true,
  "distinct_packet_count": 10,
  "legitimate_repeated_cycles_use_serialized_cycle_ids": true,
  "packet_event_count": 20,
  "packet_event_ids_unique": true,
  "packet_id_repetition_semantics": "one packet id appears in its departure and arrival events; duplicates here are not duplicate scheduled packets",
  "packet_ids_repeat_across_departure_arrival_events": true,
  "producer_record_ids_unique": true
}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
| `policy_disabled` | `n05_policy_disabled_noop` | `runtime_control` | True |
| `hidden_schedule` | `n05_hidden_schedule_rejected` | `artifact_policy_control` | True |
| `duplicate_packet` | `n05_duplicate_cycle_packet_suppressed` | `runtime_idempotency_control` | True |
| `stale_cycle` | `n05_stale_cycle_authorization_rejected` | `artifact_cycle_lineage_control` | True |
| `budget_drift` | `n05_node_plus_packet_budget_mismatch` | `artifact_budget_control` | True |
| `producer_mutation` | `n05_producer_mutation_boundary_violation` | `runtime_artifact_control` | True |
| `claim_promotion` | `n05_claim_promotion_rejected` | `artifact_claim_boundary_control` | True |

## Claim Boundary

All N05 movement, semantic choice, agency, identity, memory/trail, regulation,
agentic-like, locomotion-like, biological, ACO, and unrestricted movement claim
flags remain false. O4 is repeated-cycle evidence only; self-sustained and
route-coupled oscillator claims remain blocked.
