# Phase 8 LGRC9 Causal Pulse-Substrate Baseline Freeze

Date: 2026-05-16

Status: passed.

This record freezes Iteration 50 before native causal pulse-substrate surface
behavior is added.

Machine-readable companion:

- [`Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.json`](./Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.json)

## Purpose

Iteration 50 does not prove the native surface. It proves that existing
`LGRC9V3` behavior and the N04 Lane E hybrid evidence are cleanly recorded
before native implementation starts.

The frozen boundary is:

```text
native_causal_pulse_substrate_surface_enabled = false
native_causal_pulse_substrate_surface_validated = false
native_pulse_substrate_coupling_producer_enabled = false
native_feedback_coupled_pulse_producer_enabled = false
native_lgrc_pulse_substrate_supported = false
native_m6 = false
movement_claim_allowed = false
loop_driven_movement_claim_allowed = false
locomotion_like_claim_allowed = false
adaptive_topology_entry_allowed = false
biological_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
```

Native surface v1 is fixed-topology. LGRC-3 topology-lineage transport is
deferred; topology-changing surface runs must fail closed with
`topology_lineage_deferred`.

## Working-Tree State

Baseline commit:

```text
fe47313792c9a173451bb4a9383703f85bafec1f
```

Source diff:

```text
git diff -- src
    empty
git status --short src
    empty
```

Iteration 50 adds implementation records only. It does not change `src/*`.

## Runtime And Format Baseline

The native surface requires LGRC-2 or higher. Iteration 50 records LGRC-2 as
available through the existing packetized fixed-topology contract tests.

```text
required_for_native_surface: lgrc2_or_higher
validated_mode: packetized_fixed_topology
snapshot_schema: pygrc.snapshot
snapshot_version: 1
telemetry_family: lgrc9v3
telemetry_contract_version: phase8_lgrc9v3_iter29_v1
graph_checkpoint_schema_version: lgrc9v3_graph_checkpoint_v1
native_surface_fields_present: false
```

Determinism baseline:

```text
surface_contract_randomness: none
default_rng_seed_policy: use evolution.rng_seed when present, otherwise seed 0
fixture_policy: unit fixtures deterministic; generated fixtures serialize seed parameters
```

Continuation reference:

```text
previous continuation: native packet-loop Iterations 43-49
closeout: implementation/Phase-8-LGRC9-NativePacketLoopChecklist.md#iteration-49-native-packet-loop-closeout
baseline: implementation/Phase-8-LGRC9-NativePacketLoopBaselineFreeze.json
```

## N04 Lane E Evidence

Hybrid surface probe:

```text
experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_pulse_substrate_surface_probe.json
sha256: 809ba5c96a598b60d8cea567a694de0121c261a3413303cadb813eed49f312ff
status: passed
claim_ceiling: hybrid_lgrc_causal_pulse_substrate_surface_contract_supported
native_lgrc_pulse_substrate_supported: false
movement_claim_allowed: false
```

Lane C feedback compatibility:

```text
experiments/2026-05-N04-grc9v3-movement-ladders/outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json
sha256: cc6cede94ae3839f9fdeb64b0b529baa394a91e0d92b7642b7149a073821588e
status: passed
claim_ceiling: lane_c_feedback_policy_compatible_with_causal_pulse_substrate_surface
native_lgrc_pulse_substrate_supported: false
movement_claim_allowed: false
```

## Packet-Loop Evidence

E3 closeout:

```text
experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_closeout.json
sha256: 75e02858f32484a8c4e9a24d9751c0ce98e4ef603fd6e550d8a47f7466e2288e
status: passed
native_d2_3_equivalent: true
```

E3 animation:

```text
experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation.json
sha256: 3c7094198ad273369af49beb10e6916b4d2bf9a705ecaef6c421e4be39033b2f
status: passed
```

## Baseline Assertions

The baseline asserts:

- `src/*` is unchanged before implementation;
- no native causal pulse-substrate symbols exist in `src`;
- no native pulse-substrate surface rows or support claims exist yet;
- N04 Lane E hybrid evidence exists and remains non-native;
- N04 Lane C feedback compatibility exists and remains non-native;
- existing E3 native packet-loop closeout remains supported;
- old static-route autonomy remains supported by the focused LGRC tests;
- native surface v1 is fixed-topology and LGRC-3 lineage transport is
  deferred.

## Command Record

```bash
env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 141 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 185 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
# 123 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 980 tests passed

.venv/bin/python -m ruff check src tests \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts \
    experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts
# failed baseline: 1146 pre-existing errors

git diff --check
# passed

git diff -- src
# empty

git status --short src
# empty
```

## Baseline Notes

The broad Ruff command is intentionally recorded as baseline state. It fails on
pre-existing lint debt unrelated to this continuation. The implementation gate
for Iteration 50 is that no `src/*` changes exist and all unittest baselines
pass before native surface work starts.
