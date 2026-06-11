# Phase 8 LGRC9 Causal Pulse-Substrate Surface Lineage Baseline Freeze

Date: 2026-05-17

Status: passed.

This record freezes Iteration 58 before native causal pulse-substrate surface
lineage transport or supersession source changes are added.

Machine-readable companion:

- [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageBaselineFreeze.json`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageBaselineFreeze.json)

## Purpose

Iteration 58 does not prove adaptive topology or topology-mutating movement. It
records the exact boundary that Phase 8 must address:

```text
LGRC-3 topology lineage replay exists.
Native causal pulse-substrate surface v1 is fixed-topology only.
Surface lineage transport/supersession support does not exist yet.
N04 remains capped at s7_fixed_port_composed_gate_candidate.
```

The frozen claim boundary is:

```text
native_causal_pulse_substrate_surface_lineage_transport_enabled = false
native_causal_pulse_substrate_surface_lineage_transport_validated = false
native_causal_pulse_substrate_surface_lineage_transport_supported = false
adaptive_topology_entry_allowed = false
topology_mutating_movement_claim_allowed = false
movement_claim_allowed = false
locomotion_like_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
```

## Working-Tree State

Baseline commit:

```text
eb840a740fa972f78307611945a1960fbac2b39f
```

Source diff:

```text
git diff -- src
    empty
git status --short src
    empty
```

The working tree contains N04 taxonomy artifacts and the new Phase 8
surface-lineage plan/checklist. Iteration 58 does not change `src/*`.

## Runtime And Format Baseline

```text
lineage_transport_required_lgrc_level: lgrc3
existing_native_surface_required_lgrc_level: lgrc2_or_higher
snapshot_schema: pygrc.snapshot
snapshot_version: 1
telemetry_family: lgrc9v3
telemetry_contract_version: phase8_lgrc9v3_iter29_v1
surface_log: causal_pulse_substrate_surface_log
surface_row_lineage_status: fixed_topology
topology_lineage_replay_schema: lgrc9v3_topology_event_replay_validation_v1
lineage_transport_fields_present: false
```

The baseline preserves the Phase 8 producer/step boundary: producers emit
evidence and schedule through LGRC, while `step()` remains the mutation
boundary.

## Source Artifacts

N04 Iteration 19-B:

```text
experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_iter19b_topology_lineage_adaptive_gate_report.json
sha256: cba7628158f88613148ccb99a4d221b6e001ebe221900f215ad8238d6847433f
status: passed
claim_ceiling: s7_fixed_port_composed_gate_candidate
primary_blocker: causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status
```

N04 taxonomy continuation closeout:

```text
experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_taxonomy_continuation_closeout.json
sha256: bf92931093905fc354c5a74d2b1e37e208c4395db7d1c22ddfec23d11501742d
next_work: phase8_causal_pulse_substrate_surface_lineage_transport
return_to_n04_after_phase8: N04 Iteration 19-C
```

Previous Phase 8 causal pulse-substrate closeout:

```text
implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.json
sha256: 2c2b1171c31cc8ad4bcc4373d6a8a04f94865714707d7f9924066ce7e3feb2e2
claim_ceiling: native_lgrc_pulse_substrate_surface_supported
topology_lineage_decision: deferred_for_native_surface_v1
```

## Baseline Assertions

- current causal pulse-substrate surface rows require `fixed_topology`;
- lineage-transport surface rows are rejected with
  `causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status`;
- native LGRC-3 topology lineage replay passes independently;
- the fixed-topology S7 candidate remains recorded as
  `s7_fixed_port_composed_gate_candidate`;
- no native surface-lineage transport support claim exists yet;
- snapshot and telemetry baselines are additive targets for later iterations;
- movement, adaptive topology, topology-mutating movement, choice, agency, and
  identity-acceptance claims remain blocked.

## Command Record

```bash
env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 192 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_module_split -q
# 2 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.telemetry.test_lgrc9v3_contract -q
# 4 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 236 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 1031 tests passed

env PYTHONPATH=src .venv/bin/python \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter19b_topology_lineage_adaptive_gate.py
# passed

env PYTHONPATH=src .venv/bin/python \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_taxonomy_continuation_closeout.py
# passed

git diff --check
# passed

git diff -- src
# empty

git status --short src
# empty
```

## Minimal Pass Statement

Iteration 58 passes as a baseline freeze. Before Iteration 59 source changes,
LGRC-3 topology lineage replay is available, native causal pulse-substrate
surface rows remain fixed-topology-only, surface lineage transport is absent,
N04 remains capped at `s7_fixed_port_composed_gate_candidate`, and all movement
or adaptive-topology claim flags remain blocked.
