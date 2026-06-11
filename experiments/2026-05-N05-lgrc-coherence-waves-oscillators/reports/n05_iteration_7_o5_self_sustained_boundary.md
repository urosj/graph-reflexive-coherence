# N05 Iteration 7 O5 Self-Sustained Oscillator Boundary

Status: passed

Command:

```bash
.venv/bin/python experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/run_n05_iteration_7_o5_self_sustained_boundary.py
```

## Result

| Field | Value |
|---|---|
| O-level | `O5` |
| claim ceiling | `self_sustained_oscillator_candidate` |
| O5 mode | `producer_mediated` |
| execution stage | `native_self_rearm_boundary` |
| fixture id | `N05_O5_two_pole_native_self_rearm_loop_v1` |
| native self-rearm evidence | `True` |
| self-rearm completed count | `6` |
| reconstructed cycles | `3` |
| native constitutive oscillator supported | `False` |
| native policy blocker | `missing_serialized_delayed_passive_response_policy` |
| budget error | `0.0` |
| row schema compliance | `True` |

## Cycle Records

| Index | Cycle id | S-to-K packet | K-to-S packet | Renewal state-authorized |
|---|---|---|---|---|
| `0` | `n05_o5_self_rearm_cycle_000` | `lgrc9v3-packet-020c7a5efb259bfb` | `lgrc9v3-packet-8ac4ff414b6b248f` | True |
| `1` | `n05_o5_self_rearm_cycle_001` | `lgrc9v3-packet-cae8662be91f5054` | `lgrc9v3-packet-7eee594ca142440d` | True |
| `2` | `n05_o5_self_rearm_cycle_002` | `lgrc9v3-packet-0785d50792c123b5` | `lgrc9v3-packet-74e0788a48032487` | True |

## Fixture And Seed Boundary

O5 uses a two-pole closed-loop route-aspect fixture because native self-rearm
evidence is defined over `LGRC9V3RouteAspect` channels. This is intentionally
different from the source-target-reservoir fixture used by O3/O4.

```json
{
  "fixture_kind": "two_pole_native_route_aspect_loop",
  "reason": "native self-rearm evidence is defined over LGRC9V3 route-aspect closed-loop channels",
  "source_manifest": "n05_fixture_manifest_v1"
}
```

The first parent return is a declared bootstrap seed. The counted O5 cycles
come from subsequent native self-rearm evidence.

```json
{
  "budget_error": 0.0,
  "parent_arrival_event_digest": "6ced1df26cbd8d9443ad983152ab96ad4a136da19ca8639223a10fce8a5b9fb8",
  "parent_arrival_event_id": "lgrc9v3-packet-event-6e0befbe79a1c3c1",
  "parent_packet_id": "lgrc9v3-packet-612a6d8723dbea14",
  "preauthored_event_list_used": false,
  "seed_kind": "single_declared_parent_return_arrival",
  "seeded_first_contact_only": true
}
```

## Artifact Replay

```json
{
  "artifact_only": true,
  "budget_ok": true,
  "completed_self_rearm_count": 6,
  "cycle_count_reconstructed": 3,
  "hidden_event_list_absent": true,
  "passed": true,
  "renewal_depends_on_committed_state": true,
  "runtime_state_used": false,
  "self_rearm_linkage_ok": true,
  "validation_failure_reasons": [],
  "validation_valid": true,
  "validator": "validate_lgrc9v3_self_rearm_evidence_artifacts",
  "validator_replay_note": "validator reran from exported snapshot events and production results"
}
```

## Phase 3 Native Policy Audit

```json
{
  "constitutive_native_claim_allowed": false,
  "current_native_supports": [
    "route_aspect_surplus_trigger",
    "native_self_rearm_evidence",
    "bounded_autonomous_run_loop"
  ],
  "custom_node_potentials_support": false,
  "delayed_passive_response_support": false,
  "flux_facilitated_metric_map_support": false,
  "native_constitutive_oscillator_supported": false,
  "native_policy_blocker": "missing_serialized_delayed_passive_response_policy",
  "native_policy_blockers": [
    "missing_serialized_custom_node_potentials_policy",
    "missing_serialized_potential_inversion_policy",
    "missing_flux_facilitated_metric_map_policy",
    "missing_serialized_delayed_passive_response_policy",
    "missing_route_conductance_memory_policy"
  ],
  "passed": true,
  "potential_inversion_support": false,
  "route_conductance_memory_support": false
}
```

## Controls

| Control | Primary blocker | Mode | Passed |
|---|---|---|---|
| `disabled_trigger` | `n05_o5_trigger_policy_disabled` | `runtime_control` | True |
| `subthreshold` | `n05_o5_threshold_gate_failed` | `runtime_control` | True |
| `wrong_state` | `n05_o5_committed_parent_arrival_missing` | `runtime_control` | True |
| `hidden_event_list` | `n05_o5_hidden_event_list_rejected` | `artifact_policy_control` | True |
| `duplicate_trigger` | `n05_o5_duplicate_trigger_suppressed` | `runtime_idempotency_control` | True |
| `budget_drift` | `n05_o5_node_plus_packet_budget_mismatch` | `artifact_budget_control` | True |
| `producer_mutation` | `n05_o5_producer_mutation_boundary_violation` | `runtime_artifact_control` | True |
| `claim_promotion` | `n05_o5_claim_promotion_rejected` | `artifact_claim_boundary_control` | True |

## Claim Boundary

O5 is a producer-mediated, threshold-authorized self-rearm oscillator boundary.
It does not prove a pure constitutive native oscillator. Movement, semantic
choice, agency, identity, memory/trail, route-coupled oscillator, agentic-like,
locomotion-like, biological, ACO, and unrestricted movement claim flags remain
false.
