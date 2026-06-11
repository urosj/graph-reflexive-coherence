# E3 LGRC9V3 Native Packet-Loop Reproduction Plan

## Purpose

E3 is an experiment-local reproduction branch for N03 after the separate Phase
8 native packet-loop implementation.

The dependency direction is intentional:

```text
Phase 8 implements native LGRC9V3 packet-loop runtime surfaces.
N03 E3 tests whether the experiment can reproduce its D2.3 result with them.
```

E3 must not define new core semantics. If E3 needs new `src/*` behavior, stop
and return to the global implementation plan instead of adding hidden
experiment-specific assumptions.

## Question

```text
Can the N03 D2.3 packet-loop result be reproduced using only native LGRC9V3
runtime surfaces?
```

Native surfaces mean:

- `LGRC9V3`;
- native route-aspect configuration;
- native route-aspect surplus-trigger producer;
- native `step()` / event-queue packet processing;
- native packet departure and arrival event records;
- native self-rearm evidence records;
- native snapshots and telemetry;
- artifact-only validation from exported runtime evidence.

The old experiment-local D2/D2.3 packet prototype and E2 adapter trigger may be
used only as comparison references, not as the E3 execution engine.

The first E3 fixture should use the N03 four-pole source/sink route expressed
as native one-hop route-aspect channels:

```text
clockwise:         S1 -> K2 -> S2 -> K1 -> S1
counter-clockwise: S1 -> K1 -> S2 -> K2 -> S1
```

This is intentionally a compact 4-node / 4-edge native packet-loop fixture:
one runtime node per route pole and one native route-aspect channel per route
hop. It is not the earlier 12-node N03/E2 ported-ring fixture. E2 used the
12-node bridge fixture to test native packet execution against the original
ring substrate; E3 uses the minimal four-pole route because the native
surplus-trigger and self-rearm semantics are pole/channel keyed, and the
reproduction target is D2.3-equivalent packet-loop causality rather than the
negative 12-node synchronous ring mechanism.

This keeps the N03 pole semantics visible while matching the current native
route-aspect surplus-trigger primitive, whose producer schedules the first hop
of an eligible route-aspect channel.

## Claim Boundary

Supported if successful:

- N03 D2.3 is reproducible with native LGRC9V3 packet-loop surfaces.
- Native LGRC9V3 can produce surplus-triggered, self-rearming packet-loop
  evidence under the N03 route/control matrix.
- Artifact-only validation can reproduce positive and negative classifications
  from native runtime outputs.

Still not supported:

- native GRC9V3 proposal-flux loop formation;
- movement or locomotion;
- agency, intention, or biological behavior;
- identity acceptance;
- multi-pole generalization;
- changing N03's original negative result for native fixed-topology GRC9V3
  proposal flux.

## Stop Rule

E3 may add experiment-local manifests, scripts, reports, validators, and
documentation.

E3 must stop before any `src/*` change. A required core change must be recorded
as a new global implementation task, not hidden inside this experiment branch.

## Iteration E3.0. Dependency And Fixture Baseline

Goal:

```text
Confirm the native LGRC9V3 packet-loop surfaces required by N03 exist and map
the N03 route/control fixture onto them.
```

Checks:

- confirm native route-aspect contract is importable;
- confirm native surplus-trigger producer is importable;
- confirm native self-rearm validator is importable;
- map N03 D2.3 route aspects to native route-aspect config;
- record route-aspect digests;
- record trigger thresholds and reference masses;
- confirm no D2/D2.3 prototype runner is used as the execution engine;
- confirm no `src/*` change is made by E3.

Outputs:

- `configs/e3_native_lgrc9v3_packet_loop_route_manifest.json`
- `outputs/e3_0_dependency_and_fixture_baseline.json`
- `reports/e3_0_dependency_and_fixture_baseline.md`

## Iteration E3.1. Native Positive Reproduction

Goal:

```text
Run clockwise and counter-clockwise N03 packet-loop positives through native
LGRC9V3 route-aspect surplus triggers and self-rearm evidence.
```

Checks:

- construct LGRC9V3 runtime from the E3 route manifest;
- enable native surplus-trigger policy explicitly;
- run bounded native event processing;
- require completed native self-rearm chains;
- require at least the D2.3 cycle threshold;
- verify node-plus-packet budget at every event;
- verify fixed topology;
- verify event-time and proper-time evidence;
- compare clockwise/counter-clockwise direction symmetry.

Outputs:

- `outputs/e3_1_native_positive_reproduction.json`
- `reports/e3_1_native_positive_reproduction.md`

## Iteration E3.2. Native Control Parity

Goal:

```text
Verify D2.3 negative controls remain negative under native LGRC9V3 execution.
```

Required controls:

- no-surplus;
- subthreshold;
- threshold-too-high;
- wrong-direction;
- forward-only;
- broken-return;
- scrambled-order.

Checks:

- native packet execution may occur where expected;
- incomplete or wrong-route activity does not promote a loop claim;
- each control has a primary blocker;
- budgets remain conserved unless a control explicitly targets budget;
- topology remains fixed;
- ledger-only validation reproduces each positive/negative classification.

Outputs:

- `outputs/e3_2_native_control_parity.json`
- `reports/e3_2_native_control_parity.md`

## Iteration E3.3. Snapshot And Telemetry Reproduction

Goal:

```text
Prove the native N03 reproduction survives save/load and telemetry export.
```

Checks:

- save/load preserves route-aspect config and digests;
- save/load preserves autonomous producer records;
- save/load preserves self-rearm evidence;
- save/load does not duplicate evidence;
- continue-after-load preserves route order and duplicate suppression;
- telemetry exports enough evidence for artifact-only validation;
- claim flags remain stable after export/import.

Outputs:

- `outputs/e3_3_snapshot_telemetry_reproduction.json`
- `reports/e3_3_snapshot_telemetry_reproduction.md`

## Iteration E3.4. N03 Native LGRC Closeout

Goal:

```text
Close N03's post-core LGRC reproduction branch with a precise claim boundary.
```

Required conclusions:

- whether native LGRC9V3 reproduces the D2.3 packet-loop result;
- whether adapter/prototype execution is no longer required for N03 D2.3
  semantics;
- whether all D2.3 controls remain negative;
- whether snapshot/telemetry replay is sufficient;
- whether any core follow-up remains.

Outputs:

- `outputs/e3_native_lgrc9v3_packet_loop_closeout.json`
- `reports/e3_native_lgrc9v3_packet_loop_closeout.md`

Closeout must preserve:

```text
native GRC9V3 proposal-flux loop evidence = false
movement_claim_allowed = false
agency_claim_allowed = false
biology_claim_allowed = false
```
