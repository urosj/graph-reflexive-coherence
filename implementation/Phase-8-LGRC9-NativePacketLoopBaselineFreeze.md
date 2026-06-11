# Phase 8 LGRC9 Native Packet-Loop Baseline Freeze

Date: 2026-05-15

Status: passed.

This record freezes Iteration 43 before native route-aspect or surplus-trigger
behavior is added.

Machine-readable companion:

- [`Phase-8-LGRC9-NativePacketLoopBaselineFreeze.json`](./Phase-8-LGRC9-NativePacketLoopBaselineFreeze.json)

## Purpose

Iteration 43 does not prove the new packet-loop mechanism. It proves that
existing `LGRC9V3` behavior still holds before Iteration 44 starts.

The frozen boundary is:

```text
native_packet_execution = true
native_static_route_autonomy = true
native_surplus_trigger = false
native_self_rearm_evidence = false
native_d2_3_equivalent = false
adapter_required_for_d2_3_semantics = true
native_static_route_only = true
native_grc9v3_loop_evidence = false
movement_claim_allowed = false
```

## Working-Tree State

Baseline commit:

```text
7ab7044c9dc96600e8e4e7b0c342bfa3145e7c2d
```

Source diff:

```text
git diff -- src
    empty
```

Iteration 43 adds tests and implementation records only. It does not change
`src/*`.

## Fixture Identity

Imported E2 route manifest:

```text
experiments/2026-05-N03-grc9v3-polarized-basin-loops/configs/e2_lgrc9v3_route_manifest.json
sha256: df086174ce417b30dd3182d5bef43d67f798e1fea7e1e25b7dc8d506f047ea1a
```

Compact in-test fixture:

```text
tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py
sha256: e9f5fe5a644007b8246a548c687c51bd5b561d0364cd3a2ffc31c40f7c31b520
```

Route:

```text
S1_to_K2 -> K2_to_S2 -> S2_to_K1 -> K1_to_S1
```

Hop sequence:

```text
1 -> 2 via edge 1
2 -> 3 via edge 2
4 -> 5 via edge 4
5 -> 6 via edge 5
7 -> 8 via edge 7
8 -> 9 via edge 8
10 -> 11 via edge 10
11 -> 0 via edge 11
```

## Baseline Assertions

The new baseline tests assert:

- existing scheduled packet route replay works;
- existing static-route autonomy works;
- the existing static-route producer is not D2.3-equivalent;
- disabled producer policy is a no-op;
- disabled producer policy does not perturb static-route autonomy;
- no native surplus-trigger policy is accepted yet;
- no native self-rearm evidence is emitted by the existing static-route
  producer;
- packet events expose scheduler index, event-time key, checkpoint index, and
  packet records;
- arrival packet events expose proper-time update evidence;
- node-plus-packet budget remains conserved in the baseline fixture;
- topology remains unchanged in the baseline fixture.

## Command Record

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_native_packet_loop_baseline -q
# 6 tests passed

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline -q
# 64 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 149 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
# 123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 944 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py
# passed

git diff --check -- tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py implementation/Phase-8-LGRC9-NativePacketLoopChecklist.md
# passed

git diff -- src
# empty
```

## Minimal Pass Statement

Before adding native route-aspects or surplus triggers, existing `LGRC9V3`
packet execution and static-route autonomy still pass; no D2.3-equivalent
surplus trigger or self-rearm claim is emitted; claim flags are explicit;
budget, topology, timing, and `src/*` diff audits are clean; and the imported
E2 fixture is replayable.
