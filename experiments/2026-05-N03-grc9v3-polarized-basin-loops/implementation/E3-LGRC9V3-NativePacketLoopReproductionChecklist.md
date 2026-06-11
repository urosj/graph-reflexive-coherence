# E3 LGRC9V3 Native Packet-Loop Reproduction Checklist

Related plan:

- [`E3-LGRC9V3-NativePacketLoopReproductionPlan.md`](./E3-LGRC9V3-NativePacketLoopReproductionPlan.md)

## E3.0. Dependency And Fixture Baseline

Status: complete.

### Checks

- [x] Confirm native route-aspect contract imports.
- [x] Confirm native surplus-trigger producer surface imports.
- [x] Confirm native self-rearm validator imports.
- [x] Build E3 route manifest from N03 D2.3 route/control semantics.
- [x] Record route-aspect digest.
- [x] Record pole-region digest.
- [x] Record channel-sequence digest.
- [x] Record trigger thresholds and reference masses.
- [x] Confirm old D2/D2.3 prototype runner is not used as execution engine.
- [x] Confirm no new `src/*` changes are made by E3.

### Outputs

- [x] `configs/e3_native_lgrc9v3_packet_loop_route_manifest.json`
- [x] `outputs/e3_0_dependency_and_fixture_baseline.json`
- [x] `reports/e3_0_dependency_and_fixture_baseline.md`

### Result

E3.0 passed. The E3 route manifest records native clockwise and
counter-clockwise four-pole route-aspects, digests, trigger policy, packet
amount, and claim boundary. E3 uses native LGRC9V3 route-aspects and native
surplus-trigger producers as the execution surface; the old D2/D2.3 packet
prototype and E2 adapter trigger are not execution engines.

## E3.1. Native Positive Reproduction

Status: complete.

### Checks

- [x] Run clockwise native route-aspect surplus-triggered loop.
- [x] Run counter-clockwise native route-aspect surplus-triggered loop.
- [x] Require completed native self-rearm chains.
- [x] Require cycle count at or above the D2.3 threshold.
- [x] Verify node-plus-packet budget at every event.
- [x] Verify fixed topology.
- [x] Verify event-time key ordering.
- [x] Verify node proper-time evidence is serialized.
- [x] Verify direction symmetry for cycle count, event count, budget, route order,
      and trigger-to-departure timing.

### Outputs

- [x] `outputs/e3_1_native_positive_reproduction.json`
- [x] `reports/e3_1_native_positive_reproduction.md`

### Result

E3.1 passed.

```text
clockwise cycles: 3
clockwise completed self-rearms: 12
clockwise trigger count: 12
counter-clockwise cycles: 3
counter-clockwise completed self-rearms: 12
counter-clockwise trigger count: 12
direction symmetry: passed
max event budget error: 0.0
topology changed: false
```

The first run exposed a fixture issue: counter-clockwise initially reused the
clockwise reference mass for the pre-seeded return pole and stopped early. The
E3 manifest now uses route-relative reference masses: `S1` uses `2.15`, the
route's final source pole uses `0.75` after the seed debit, and the other poles
use `1.0`.

## E3.2. Native Control Parity

Status: complete.

### Controls

- [x] No-surplus control remains negative.
- [x] Subthreshold control remains negative.
- [x] Threshold-too-high control remains negative.
- [x] Wrong-direction control remains negative.
- [x] Forward-only control remains negative for closed-loop claims.
- [x] Broken-return control remains negative for self-rearm claims.
- [x] Scrambled-order control remains negative for canonical route-order claims.

### Checks

- [x] Every negative control records a primary blocker.
- [x] Packet activity alone does not promote loop evidence.
- [x] Self-rearm evidence requires the native causal chain:
      parent arrival -> post-arrival trigger -> child scheduled -> child
      departure processed.
- [x] Ledger-only validator reproduces positive and negative classifications from
      native artifacts.
- [x] Claim flags preserve N03 boundaries.

### Outputs

- [x] `outputs/e3_2_native_control_parity.json`
- [x] `reports/e3_2_native_control_parity.md`

### Result

E3.2 passed. Required controls remained negative:

```text
no_surplus: surplus_gate_failed
subthreshold: threshold_gate_failed
threshold_too_high: threshold_gate_failed
wrong_direction: route_direction_gate_failed
forward_only: return_chain_missing
broken_return: route_aspect_closed_loop_validation_failed
scrambled_order: route_aspect_pole_contiguity_validation_failed
```

Forward-only and wrong-direction controls can still produce native packet
activity, but they do not produce completed native self-rearm cycles or
D2.3-equivalent claims.

## E3.3. Snapshot And Telemetry Reproduction

Status: complete.

### Checks

- [x] Snapshot round-trip preserves route-aspect config and digests.
- [x] Snapshot round-trip preserves autonomous producer records.
- [x] Snapshot round-trip preserves self-rearm evidence records.
- [x] Save/load does not duplicate packet, producer, or self-rearm records.
- [x] Continue-after-load preserves route order.
- [x] Continue-after-load preserves duplicate-trigger suppression.
- [x] Telemetry exports route-aspect digest, producer evidence, packet events,
      self-rearm evidence, budget audit, and claim flags.
- [x] Artifact-only validation passes from telemetry-exported data.
- [x] Disabled-policy save/load remains default-off in the native Phase 8
      regression surface; E3 does not alter that default.

### Outputs

- [x] `outputs/e3_3_snapshot_telemetry_reproduction.json`
- [x] `reports/e3_3_snapshot_telemetry_reproduction.md`

### Result

E3.3 passed.

```text
producer records before/after save-load: 13 / 13
self-rearm records before/after save-load: 12 / 12
packet events before/after save-load: 26 / 26
snapshot artifact-only validation: passed
telemetry artifact-only validation: passed
continue-after-load scheduled events: 1
continue-after-load duplicate scheduled events: 0
continue-after-load duplicate reason: idempotent_skip
```

Telemetry exposes the native packet-loop surface with producer policy,
route-aspect digest, completed self-rearm count, native surplus trigger, native
self-rearm evidence, and the explicit claim boundary.

## E3.4. N03 Native LGRC Closeout

Status: complete.

### Checks

- [x] Closeout states whether native LGRC9V3 reproduces D2.3.
- [x] Closeout states whether adapter/prototype execution is still required.
- [x] Closeout states whether D2.3 controls all pass.
- [x] Closeout states whether snapshot/telemetry evidence is replayable.
- [x] Closeout records exact commands.
- [x] Closeout records generated artifacts.
- [x] Closeout preserves claim boundaries:
      no native GRC9V3 proposal-flux loop claim, no movement claim, no agency
      claim, no biological claim.
- [x] Closeout records whether any core follow-up remains.

### Outputs

- [x] `outputs/e3_native_lgrc9v3_packet_loop_closeout.json`
- [x] `reports/e3_native_lgrc9v3_packet_loop_closeout.md`

### Run Record

Command:

```bash
PYTHONPATH=src .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py
```

Result:

```json
{"adapter_required_for_d2_3_semantics": false, "adapter_trigger_used_as_execution_engine": false, "classification": "n03_native_lgrc9v3_packet_loop_reproduced", "controls_passed": true, "core_follow_up_required": false, "entire_n03_experiment_closed": false, "native_d2_3_equivalent": true, "native_lgrc9v3_execution": true, "native_packet_execution": true, "native_self_rearm_evidence": true, "native_static_route_only": false, "native_surplus_trigger": true, "prototype_runner_used_as_execution_engine": false, "scope_closed": "d2_3_native_lgrc_packet_loop_branch", "snapshot_telemetry_replayable": true, "status": "passed"}
```

Additional verification:

```bash
PYTHONPATH=src .venv/bin/python -m ruff check \
    experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py
```

Result:

```text
All checks passed.
```

### Closeout

E3 is complete. The N03 D2.3/native-LGRC packet-loop branch is now reproduced
using native LGRC9V3 packet-loop surfaces only:

```text
native_lgrc9v3_execution = true
native_packet_execution = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true
adapter_required_for_d2_3_semantics = false
prototype_runner_used_as_execution_engine = false
adapter_trigger_used_as_execution_engine = false
```

Claims still blocked:

```text
native GRC9V3 proposal-flux loop evidence
movement or locomotion
agency, intention, or biological behavior
identity acceptance
multi-pole generalization
```

This does not close the entire N03 experiment family. Remaining N03 follow-up
work, such as movement-ladder handoff, boundary-coupled pulses, multi-pole
basin loops, larger fixtures, output cleanup, and paper polish, should remain
separate branches with their own controls and claim boundaries.
