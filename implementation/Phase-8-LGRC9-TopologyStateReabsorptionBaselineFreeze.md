# Phase 8 LGRC9 Topology-State Reabsorption Baseline Freeze

Iteration 66 records the boundary before native topology-state reabsorption
source changes.

## Status

Passed.

## Baseline Boundary

N04 remains capped at:

```text
adaptive_topology_entry_candidate
```

The current topology-mutating movement probe fails closed with:

```text
primary_blocker =
packet_ledger_state_reabsorption_mismatch_after_topology_event
```

The concrete mismatch from N04 Iteration 19-D is:

```text
ledger node total = 6.0
active state node total = 5.9
delta = 0.1
post-topology packet scheduled = false
post-topology packet processed = false
```

This confirms the surface-lineage layer is available, but live active state and
packet-ledger reabsorption are still missing.

## Inputs

- N04 19-D artifact:
  `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19d_topology_mutating_movement_probe.json`
- N04 19-D SHA-256:
  `28df03d76ced295508d535848b4efee9bbcf782840d8688e442b4e7257b2b653`
- Surface-lineage closeout:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json`
- Surface-lineage closeout SHA-256:
  `97ad2e56ba6f2b2b303070dcbc4eb16ee54a5267c4911269abb664f35571709f`
- N04 taxonomy closeout SHA-256:
  `2b37e9ff1999b3aa75c97d44b93d4e6c82c3f624afa0c744475178f541105a0d`

## Baseline Flags

```text
causal_topology_state_reabsorption_enabled = false
causal_topology_state_reabsorption_policy = disabled
causal_topology_state_reabsorption_validated = false
causal_topology_state_reabsorption_supported = false
```

Movement, adaptive-topology movement, topology-mutating movement, choice,
identity-collapse, agency, locomotion-like, biological, and
identity-acceptance claims remain blocked.

## Verification

```text
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py tests/models/test_lgrc_9_v3_runtime.py -q
200 passed, 24 subtests passed in 3.14s

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py -q
42 passed in 2.76s

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_module_split.py tests/telemetry/test_lgrc9v3_contract.py -q
7 passed in 1.79s

git diff -- src tests/models tests/telemetry
empty

.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter19d_topology_mutating_movement_probe.py
passed fail-closed with primary_blocker=packet_ledger_state_reabsorption_mismatch_after_topology_event
ledger_node_total=6.0, active_state_node_total=5.9, delta=0.09999999999999964
```

Head commit:

```text
2736641f9738312897b52f428907a46fcd4fef04
```

Next iteration:

```text
67_contract_and_policy_schema
```
