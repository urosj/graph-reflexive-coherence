# Phase 8 LGRC9 Causal Pulse-Substrate Closeout

Status: complete.

This closes the Phase 8 native causal pulse-substrate surface continuation.

## Result

```text
claim_ceiling = native_lgrc_pulse_substrate_surface_supported
native_causal_pulse_substrate_surface = supported
native_pulse_substrate_coupling_producer = supported
native_feedback_coupled_pulse_producer = supported
native_m6 = false
movement_claim_allowed = false
```

LGRC9V3 now exposes a default-off native causal pulse-substrate surface that
emits rows only from committed packet departure/arrival events. Coupling and
feedback producers read committed surface evidence and schedule work through
LGRC scheduling only. `step()` remains the mutation boundary for coherence and
packet budget.

## Evidence

Primary closeout artifacts:

- baseline freeze:
  [`Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.json`](./Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.json)
- N04 Lane F bridge:
  [`native_lgrc_lane_f_surface_bridge.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_lgrc_lane_f_surface_bridge.json)
- N04 Lane F closeout:
  [`n04_lane_f_native_surface_closeout.json`](../experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_f_native_surface_closeout.json)

Artifact hashes:

```text
Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.json
  sha256 = 0d0fadf5046f2b0927cb55a30eba12654e7193362cf7912682125e069bfa4b89

native_lgrc_lane_f_surface_bridge.json
  sha256 = 0c88c5e5696169bda153e2d5ed1735e0d7d1f3b3a06bbb54cff8d9e23b8f2655

n04_lane_f_native_surface_closeout.json
  sha256 = 1641543e8132af1a474c30bd6f90bd669cbb666a88df2fce55fc6982b0fa5169
```

The Lane F bridge records:

```text
native_lgrc_pulse_substrate_supported = true
native_causal_pulse_substrate_surface_validated = true
artifact_only_full_chain_reconstructed = true
control_count = 14
gate_map_readiness.ready_for_iteration_57_gate_map_update = true
```

Git head at closeout:

```text
fe47313792c9a173451bb4a9383703f85bafec1f
```

The worktree is dirty with the Phase 8 causal pulse-substrate implementation,
tests, plans, N04 Lane F artifacts, and generated closeout files. No unrelated
changes were reverted.

The reconstructed chain is:

```text
source_packet_event
-> surface_row
-> producer_record
-> scheduled_packet
-> processed_packet_event
```

## Controls

Iteration 56 and Lane F closeout covered:

- LGRC-0/LGRC-1 inertness;
- default-off and disabled-surface policy;
- coupling disabled and coupling subthreshold;
- feedback disabled, subthreshold, wrong polarity, and order mismatch;
- feedback budget violation;
- producer mutation-boundary violation;
- budget-surface ambiguity;
- snapshot continue-after-load with producers enabled;
- topology-lineage deferral for native surface v1.

All controls pass with explicit primary blockers. The topology-lineage control
fails closed with `topology_lineage_deferred`; LGRC-3 lineage transport is not
implemented in native surface v1.

## Telemetry

Formal `pygrc.telemetry` support is included:

- surface-row events classify as `event_domain = pulse_substrate_surface`;
- event extensions expose surface id, kind, digest, budget surface, pulse event,
  contact amount, and lineage status;
- step/run/checkpoint extensions expose `causal_pulse_substrate_surface` only
  when the surface is enabled or actual surface/producers evidence exists;
- default-off LGRC9V3 telemetry does not emit the pulse-substrate section.

## Blocked Claims

The native surface is scheduling/evidence infrastructure only. These remain
blocked:

```text
native_m6 = false
movement_claim_allowed = false
loop_driven_movement_claim_allowed = false
locomotion_like_claim_allowed = false
adaptive_topology_entry_allowed = false
biological_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
movement_claim_inherited_from_n03 = false
```

Runtime producers emit evidence and schedule work. They do not emit claim
labels or claim-promotion decisions.

## Verification

Latest targeted verification:

```bash
.venv/bin/python -m unittest tests.telemetry.test_lgrc9v3_contract -q
# 4 tests passed

.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_native_lgrc_lane_f_surface_bridge.py
# passed

.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/close_native_lgrc_lane_f.py
# passed

.venv/bin/ruff check \
    src/pygrc/telemetry/lgrc9v3_contract.py \
    src/pygrc/telemetry/__init__.py \
    tests/telemetry/test_lgrc9v3_contract.py \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_native_lgrc_lane_f_surface_bridge.py \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/close_native_lgrc_lane_f.py
# passed

git diff --check
# clean
```

Final Phase 8 full-suite verification:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
# Ran 1031 tests in 268.554s
# OK
```

Iteration 56 full regression reference:

```text
focused_lgrc_runtime_tests = 190
native_packet_loop_tests = 42
lgrc_sweep_tests = 236
full_unittest_discovery_tests = 1031
meets_or_exceeds_iteration_50_baseline = true
```

## Closeout Statement

LGRC9V3 exposes a default-off native causal pulse-substrate surface that emits
rows only from committed packet events, preserves producer/step mutation
boundaries, separates node-plus-packet conservation from derived accounting
surfaces, survives snapshot/telemetry replay, and supports policy-gated
coupling and feedback producers as scheduling evidence only. Existing packet,
route, packet-loop, snapshot, telemetry, topology, spark, and GRC9V3 behavior
remain compatible. Native movement, M6, locomotion-like, adaptive-topology,
biology, agency, and identity-acceptance claims remain blocked unless later
experiment validators independently open them.
