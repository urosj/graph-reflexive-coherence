# Phase 8 LGRC9 Time-Scoped Lineage Replay Closeout

Status: Closed.

Date: 2026-05-22.

## Summary

This continuation closes the artifact-replay boundary exposed by N04
Iteration 20:

```text
multi_topology_event_time_scoped_producer_lineage_replay_blocked
```

The runtime already handled the multi-topology chain with exact
node-plus-packet budget. The failing layer was artifact-only replay: producer
stale-read validation treated final topology lineage as globally invalidating
older producer records.

## Change

`validate_lgrc9v3_causal_pulse_substrate_surface_lineage_artifacts` now
evaluates producer stale reads by scheduler order:

```text
producer before later transport/supersession:
    historical read remains valid

producer at or after transport/supersession using stale source digest:
    stale-read failure remains valid

producer after transport using transported successor digest:
    valid if existing linkage, scheduled packet, and reabsorption checks pass
```

No runtime producer behavior, packet ledger behavior, topology-state
reabsorption behavior, or claim flags were changed.

## Verification

Focused validator regression:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q -k "time_scopes_producer_reads or rejects_source_read_after_transport or topology_state_reabsorption_artifact_validator_reconstructs_chain"
3 passed, 109 deselected
```

Runtime regression:

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
112 passed
```

N04 return probe:

```text
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter20_topology_mutating_repeatability_stress.py
passed
```

N04 Iteration 20 now records:

```text
stress_result = repeatability_stress_supported
multiple_committed_topology_events_artifact_replay_passed = true
primary_blocker = null
```

## Claim Boundary

This closeout supports artifact-only replay hardening only. It does not emit or
validate:

```text
native LGRC choice selection
RC identity collapse
semantic choice
agency
locomotion-like behavior
biological behavior
identity acceptance
inherited-N03 movement
unrestricted movement
```

N04 should resume at Iteration 21: native LGRC choice-selection boundary.
