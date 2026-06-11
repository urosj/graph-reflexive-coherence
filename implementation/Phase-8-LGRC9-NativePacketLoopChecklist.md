# Phase 8 LGRC9 Native Packet-Loop Continuation Checklist

This checklist tracks implementation of:

- [`Phase-8-LGRC9-NativePacketLoopPlan.md`](./Phase-8-LGRC9-NativePacketLoopPlan.md)

The task is to move the N03 D2.3 packet-loop mechanism from an
experiment-local adapter into native `LGRC9V3` runtime surfaces.

## Ground Rules

- Preserve the existing Phase 8 producer/executor boundary:
  producers enqueue, `step()` consumes.
- Keep `LGRC9V3.step()` deterministic and auditable.
- Add new behavior behind explicit policies; keep defaults unchanged.
- Preserve existing scheduled packet, static route, boundary birth, spark,
  topology, snapshot, telemetry, and example behavior.
- Treat N03 as evidence for packet-loop mechanism design, not as a movement
  claim.
- Do not emit native GRC9V3 loop claims.
- Do not emit movement, locomotion, agency, intention, or biological claims.
- Preserve node-plus-packet budget at every transition.
- Preserve event-time/proper-time distinction.
- Keep route-aspect, surplus-trigger, and self-rearm evidence serializable.
- Treat producer evidence as eligibility/scheduling evidence only. Packet
  budget mutation starts only when `step()` processes packet departure.
- Require self-rearm trigger evaluation to observe post-arrival state.
- Require native D2.3-equivalence claims to pass ledger-only validation from
  native artifacts.

## Iteration 43. Baseline Freeze And E2 Fixture Import

Status: complete.

### Goal

Freeze the current LGRC9V3 baseline and import the E2 expectations as
replayable tests before adding native trigger behavior.

### Checks

- [x] Record current LGRC9V3 test baseline.
- [x] Record current full test baseline if feasible.
- [x] Record current `ruff` baseline for affected files.
- [x] Add or identify a compact E2 route fixture under tests.
- [x] Add a baseline test proving existing native static-route autonomy still
      works.
- [x] Add a baseline test proving native D2.3-equivalent surplus trigger is
      not yet claimed.
- [x] Add default-off compatibility test:
      with surplus-trigger policy disabled, old scheduled packet route
      behavior is unchanged.
- [x] Add default-off compatibility test:
      with surplus-trigger policy disabled, old static route autonomy is
      unchanged.
- [x] Add default-off compatibility test:
      with surplus-trigger policy disabled, no self-rearm evidence is emitted.
- [x] Add a baseline test preserving scheduled packet route replay.
- [x] Add a baseline test preserving adapter-free `run_autonomous(...)`
      behavior.
- [x] Confirm no claim flags changed.

### Verification

- [x] Focused LGRC9V3 runtime tests pass.
- [x] LGRC test sweep passes.
- [x] GRC9V3 tests pass.
- [x] Full repository test suite passes.
- [x] `ruff` passes for the new baseline test file.
- [x] `git diff --check` passes.

### Summary

Iteration 43 complete.

Added the baseline-freeze test module:

```text
tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py
```

Added the durable baseline-freeze record:

```text
implementation/Phase-8-LGRC9-NativePacketLoopBaselineFreeze.md
implementation/Phase-8-LGRC9-NativePacketLoopBaselineFreeze.json
```

The new tests import a compact E2-style 12-node clockwise route fixture into
the test suite and pin the current runtime boundary:

```text
existing scheduled packet route replay: supported
existing static-route autonomy: supported
native D2.3-equivalent surplus trigger: not yet claimed
self-rearm evidence: not emitted by the existing static-route producer
disabled producer policy: no-op and does not perturb static-route autonomy
packet timing/proper-time evidence: present on packet runtime events
```

Run record:

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_native_packet_loop_baseline -q
    6 tests passed

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline -q
    64 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    149 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    944 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check \
    tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py
    passed

git diff --check -- tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py
    passed

python -m json.tool implementation/Phase-8-LGRC9-NativePacketLoopBaselineFreeze.json
    passed
```

Claim boundary after Iteration 43:

```text
native_packet_execution = true
native_static_route_autonomy = true
native_d2_3_equivalent = false
adapter_required_for_d2_3_semantics = true
native_static_route_only = true for the existing producer
movement_claim_allowed = false
native_grc9v3_loop_evidence = false
```

## Iteration 44. Native Route-Aspect Contract

Status: complete.

### Goal

Add a native serializable contract for pole/channel route semantics while
compiling to existing node/edge route execution where possible.

### Checks

- [x] Define route-aspect data structure.
- [x] Define pole-region data structure.
- [x] Define channel sequence data structure.
- [x] Define direction field and allowed values.
- [x] Define `expected_next_channel` semantics.
- [x] Define serialization artifact version.
- [x] Define stable `route_aspect_id`.
- [x] Define canonical `route_aspect_digest`.
- [x] Define canonical `pole_region_digest`.
- [x] Define canonical `channel_sequence_digest`.
- [x] Add JSON round-trip tests.
- [x] Add digest stability tests.
- [x] Add digest-change tests for changed pole mask.
- [x] Add digest-change tests for changed channel order.
- [x] Add digest-change tests for changed direction convention.
- [x] Add conversion to existing node/edge causal route table.
- [x] Add validation for missing nodes/edges/poles/channels.
- [x] Add validation for broken return route.
- [x] Add validation for scrambled route ordering.
- [x] Keep static node/edge route behavior unchanged.

### Verification

- [x] Route-aspect round-trip passes.
- [x] Existing causal flux route tests pass.
- [x] No circular imports introduced.

### Summary

Iteration 44 complete.

Added native route-aspect contract surfaces in:

```text
src/pygrc/models/lgrc_9_v3_contract.py
src/pygrc/models/__init__.py
```

The new contract introduces:

```text
LGRC9V3RouteAspectHop
LGRC9V3RouteAspectChannel
LGRC9V3RouteAspect
```

and stable artifact helpers:

```text
restore_lgrc9v3_route_aspect_artifact(...)
validate_lgrc9v3_route_aspect(...)
compile_lgrc9v3_route_aspect_to_causal_flux_routes(...)
```

Route-aspects serialize pole regions, channel sequence, direction,
`expected_next_channel`, stable route IDs, and canonical digests:

```text
route_aspect_digest
pole_region_digest
channel_sequence_digest
```

The compiler maps the pole/channel route-aspect intent to the existing
node/edge causal route table without adding a surplus trigger, self-rearm
producer, or new runtime mutation path.

Added route-aspect contract tests in:

```text
tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py
```

The tests cover JSON round-trip, digest stability, digest changes for pole
mask/channel order/direction changes, state validation, conversion to existing
node/edge causal routes, broken-return rejection, scrambled-order rejection,
overlapping-pole rejection, missing-node rejection, directed-edge validation,
and static-route baseline preservation.

Run record:

```bash
PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect -q
    7 tests passed
    11 tests passed after adding overlap, missing-node, and directed-edge
    validation

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect -q
    13 tests passed before adding the explicit channel-order digest test
    14 tests passed after adding the explicit channel-order digest test
    17 tests passed after adding overlap, missing-node, and directed-edge
    validation

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect -q
    71 tests passed
    75 tests passed after adding overlap, missing-node, and directed-edge
    validation

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    156 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    951 tests passed

.venv/bin/ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py
    passed

git diff --check
    passed
```

Claim boundary after Iteration 44:

```text
native_route_aspect_contract = true
route_aspect_to_existing_route_compiler = true
native_surplus_trigger = false
native_self_rearm_evidence = false
native_d2_3_equivalent = false
adapter_required_for_d2_3_semantics = true
movement_claim_allowed = false
native_grc9v3_loop_evidence = false
```

## Iteration 45. Surplus Trigger Producer

Status: complete.

### Goal

Add a policy-gated producer that schedules packet departure from measured
source-pole surplus.

### Checks

- [x] Add producer policy constant/name.
- [x] Keep producer disabled by default.
- [x] Compute pole mass from runtime-exposed node coherence only.
- [x] Compute reference mass from serialized route-aspect config or runtime
      baseline.
- [x] Compute surplus:
      `observed_mass - reference_mass`.
- [x] Compare surplus to serialized threshold.
- [x] Restrict eligible channel by route-aspect order.
- [x] Schedule packet departure through existing runtime scheduling surface.
- [x] Add deterministic duplicate-trigger suppression:
      producer epoch,
      consumed trigger marker,
      last triggered route step,
      or refractory event count.
- [x] Record producer evidence:
      policy,
      route id,
      route-aspect digest,
      pole id,
      observed mass,
      reference mass,
      surplus,
      threshold,
      eligible channel,
      packet id,
      reason code.
- [x] Do not debit source coherence in the producer.
- [x] Preserve mutation ownership in `step()`.
- [x] Confirm producer evidence is diagnostic/eligibility evidence only.

### Controls

- [x] No-surplus fixture schedules no packet.
- [x] Subthreshold fixture schedules no packet.
- [x] Repeated producer call in the same eligibility window does not
      double-fire.
- [x] Wrong-direction fixture does not satisfy declared direction.
- [x] Forward-only route does not claim closure.
- [x] Broken-return route does not claim closure.

### Verification

- [x] Producer tests pass.
- [x] Existing autonomy producer tests pass.
- [x] Packet budget tests pass.

### Summary

Iteration 45 complete.

Added the native route-aspect surplus trigger producer policy:

```text
LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS
```

and reason codes:

```text
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SCHEDULED
LGRC9V3_AUTONOMOUS_PRODUCER_REASON_SURPLUS_TRIGGER_SUBTHRESHOLD
```

Added runtime configuration surface:

```text
LGRC9V3.set_route_aspect_surplus_trigger(...)
```

The producer:

- reads pole mass from runtime node coherence;
- computes `surplus = observed_mass - reference_mass`;
- compares surplus against a serialized trigger threshold;
- restricts the eligible channel to route-aspect order;
- schedules packet departure through the existing packet scheduling surface;
- records route-aspect digest, pole digest, channel sequence digest, pole id,
  observed mass, reference mass, surplus, threshold, eligible channel,
  expected next channel, packet amount, scheduled packet ID, producer event-time
  key, source node proper-time-at-evaluation, and reason code;
- uses autonomous producer idempotency keys to suppress duplicate scheduling in
  the same eligibility window;
- does not debit source coherence before `step()` processes the queued
  departure.

Forward-only and broken-return closure claims remain unavailable in Iteration
45 because no closure/self-rearm classifier has been added. Broken or
non-closed route shapes continue to be rejected by the Iteration 44
route-aspect validator rather than promoted as runtime closure evidence.

Added producer tests in:

```text
tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py
```

Run record:

```bash
PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
    8 tests passed
    8 tests passed after adding explicit scheduled packet ID,
    producer event-time, and source proper-time evidence

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
    25 tests passed
    25 tests passed after adding explicit scheduled packet ID,
    producer event-time, and source proper-time evidence

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
    83 tests passed
    83 tests passed after adding explicit scheduled packet ID,
    producer event-time, and source proper-time evidence

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    167 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    963 tests passed

.venv/bin/ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py
    passed

git diff --check
    passed
```

Claim boundary after Iteration 45:

```text
native_route_aspect_contract = true
native_surplus_trigger = true
native_self_rearm_evidence = false
native_d2_3_equivalent = false
native_static_route_only = false only for the explicit surplus-trigger producer
adapter_required_for_d2_3_semantics = true
movement_claim_allowed = false
native_grc9v3_loop_evidence = false
```

## Iteration 46. Native Self-Rearm Causality Evidence

Status: complete.

### Goal

Emit native self-rearm evidence only when the runtime can reconstruct the
arrival -> surplus trigger -> child departure chain.

### Checks

- [x] Record parent packet arrival id.
- [x] Record target pole/source pole affected by the arrival.
- [x] Record measured surplus after arrival.
- [x] Record trigger threshold crossing.
- [x] Record child packet scheduled by producer.
- [x] Record child departure event after `step()` processes it.
- [x] Link:
      parent packet,
      arrival event,
      producer record,
      child packet,
      departure event.
- [x] Record event-time ordering.
- [x] Record node proper-time updates.
- [x] Enforce that producer evaluation occurs after parent arrival mutation is
      committed by `step()`.
- [x] Reject evidence produced from pre-arrival state.
- [x] Reject self-rearm evidence if any link is missing.
- [x] Keep self-rearm as causal-loop evidence, not identity, movement, or
      agency evidence.

### Verification

- [x] Positive self-rearm chain validates from artifacts alone.
- [x] Missing parent packet blocks self-rearm.
- [x] Missing threshold crossing blocks self-rearm.
- [x] Scheduled but unprocessed child departure blocks completed self-rearm.
- [x] Pre-arrival trigger observation blocks completed self-rearm.
- [x] Missing producer record blocks artifact-only validation.
- [x] Route digest mismatch blocks artifact-only validation.
- [x] Wrong parent/trigger channel order blocks artifact-only validation.
- [x] Per-transition budget fields are present for parent arrival, producer
      scheduling, and child departure.

### Summary

Iteration 46 complete.

Added native self-rearm evidence events:

```text
lgrc9v3_self_rearm_evidence
```

Self-rearm evidence is emitted only when the runtime can reconstruct this
post-arrival chain:

```text
parent packet arrival processed by step()
-> arrival target node belongs to the configured source pole
-> producer observes post-arrival pole surplus above threshold
-> producer schedules a child packet departure
-> step() later processes the child departure
```

The producer emits candidate evidence with status:

```text
scheduled_child_pending_departure
```

and `step()` emits completion evidence with status:

```text
child_departure_processed
```

The evidence links:

```text
parent_packet_id
parent_arrival_event_id
producer_record_id
child_packet_id
child_departure_event_id
child_departure_processed_event_id
```

and records event-time ordering, scheduler ordering, node proper-time surface,
source node proper-time at trigger, and source node proper-time at departure.

The evidence remains causal-loop evidence only. It does not emit identity,
movement, agency, biological, or native GRC9V3 loop claims.

The public artifact-only validator:

```text
validate_lgrc9v3_self_rearm_evidence_artifacts(...)
```

reconstructs completed self-rearm chains from serialized runtime events plus
serialized producer results. It validates parent arrival, producer record,
child departure, route-aspect digest, previous/trigger/next channel ordering,
event-time/scheduler ordering, threshold crossing, proper-time evidence, and
per-transition budget errors. Corrupt or incomplete artifacts do not support
native self-rearm.

Run record:

```bash
PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
    12 tests passed
    16 tests passed after adding artifact-only validator corruption checks

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
    29 tests passed

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
    87 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    172 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    967 tests passed

.venv/bin/ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_route_aspect.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py
    passed

git diff --check
    passed
```

Claim boundary after Iteration 46:

```text
native_route_aspect_contract = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = false
adapter_required_for_d2_3_semantics = true
movement_claim_allowed = false
native_grc9v3_loop_evidence = false
```

## Iteration 47. D2.3 Native Control Parity

Status: complete.

### Goal

Run native surfaces against the D2.3/E2 control expectations.

### Checks

- [x] Clockwise positive fixture.
- [x] Counter-clockwise positive fixture.
- [x] No-surplus negative fixture.
- [x] Subthreshold negative fixture.
- [x] Threshold-too-high negative fixture.
- [x] Wrong-direction negative fixture for declared direction.
- [x] Forward-only negative fixture.
- [x] Broken-return negative fixture.
- [x] Scrambled-order negative fixture.
- [x] Jittered-delay robustness fixture, if deterministic.
- [x] Direction symmetry comparison:
      cycle count,
      trigger count,
      event count,
      budget error,
      route order,
      trigger-to-departure timing.
- [x] Native report includes:
      `native_d2_3_equivalent`,
      `adapter_required_for_d2_3_semantics`,
      and `native_static_route_only`.

### Verification

- [x] Ledger-only validator reproduces classifications from native artifacts.
- [x] Native D2.3-equivalent support is not claimed without ledger-only
      validation.
- [x] Per-event budget audits pass.
- [x] Topology remains fixed unless a test explicitly declares otherwise.
- [x] Movement and native GRC9V3 loop claim flags remain false.

### Summary

Iteration 47 complete.

Added D2.3 native control-parity tests in:

```text
tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py
```

The tests run the native `LGRC9V3` route-aspect surplus producer and `step()`
chain, then classify each row from serialized runtime events plus serialized
producer results using:

```text
validate_lgrc9v3_self_rearm_evidence_artifacts(...)
```

The positive fixtures now require repeated cycles, not merely one completed
self-rearm chain:

```text
n_cycles_min = 3
cycle_count >= n_cycles_min
self_rearm_count >= 2 * n_cycles_min for the two-channel loop
trigger_count == scheduled_packet_count == accepted_trigger_count
```

Positive rows:

```text
clockwise native self-rearm cycles: pass
counter-clockwise native self-rearm cycles: pass
jittered parent-arrival delay cycles: pass
```

Negative/control rows:

```text
no-surplus: negative
subthreshold: negative
threshold-too-high: negative
wrong-direction parent arrival: negative
forward-only/no-parent-return: negative
broken-return route aspect: rejected
scrambled next-channel order: rejected
```

Direction symmetry is checked across completed count, candidate count,
cycle count, trigger count, self-rearm count, event count, route order,
duplicate suppression count, and trigger-to-departure lag. Positive reports
expose:

```text
native_lgrc9v3_execution = true
native_packet_execution = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true
adapter_required_for_d2_3_semantics = false
native_static_route_only = false
native_grc9v3_loop_evidence = false
movement_claim_allowed = false
```

Negative rows keep `native_d2_3_equivalent = false`; no movement or native
GRC9V3 loop claim is emitted.

The stricter repeated-cycle parity test found and fixed a native runtime
matching bug: self-rearm channel matching previously used truthiness fallback
for optional parent source node and edge IDs, which treated valid ID `0` as
missing. The matcher now distinguishes `None` from `0`, so direction parity
works for routes touching node/edge zero.

Run record:

```bash
PYTHONPATH=src .venv/bin/python \
    tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py
    5 tests passed
    5 tests passed after replacing single-chain positives with repeated-cycle
    parity

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity -q
    38 tests passed
    38 tests passed after repeated-cycle parity

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity -q
    96 tests passed
    96 tests passed after repeated-cycle parity

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    181 tests passed
    181 tests passed after repeated-cycle parity

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed
    123 tests passed after repeated-cycle parity

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    976 tests passed
    976 tests passed after repeated-cycle parity

PYTHONPATH=src .venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py
    passed
    passed after repeated-cycle parity

git diff --check
    passed
```

Claim boundary after Iteration 47:

```text
native_route_aspect_contract = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true for artifact-validated native control rows
adapter_required_for_d2_3_semantics = false for artifact-validated native rows
native_static_route_only = false for surplus-triggered self-rearm rows
movement_claim_allowed = false
native_grc9v3_loop_evidence = false
```

## Iteration 48. Snapshot, Telemetry, And Reference Surfaces

Status: complete.

### Goal

Make the new route-aspect, surplus-trigger, and self-rearm evidence visible in
runtime snapshots, telemetry, examples, and reference docs.

### Checks

- [x] Snapshot includes route-aspect config.
- [x] Snapshot includes route-aspect digest fields.
- [x] Snapshot includes producer policy and trigger evidence.
- [x] Snapshot includes self-rearm evidence log.
- [x] Save/load restores route-aspect config.
- [x] Save/load restores trigger/self-rearm logs.
- [x] Telemetry records producer policy and reason code.
- [x] Telemetry records self-rearm link ids.
- [x] Example demonstrates native surplus-triggered packet loop.
- [x] Reference guide documents the claim boundary.

### Verification

- [x] Native snapshot round-trip passes after packet-loop execution.
- [x] Telemetry artifact remains backward-compatible.
- [x] Example runs from repo root.

### Summary

Iteration 48 complete.

Runtime snapshots now serialize `cached_quantities` in:

```text
dynamics.lgrc9v3_runtime.cached_quantities
```

This preserves the native packet-loop surfaces:

```text
lgrc9v3_route_aspect_surplus_trigger_config
lgrc9v3_self_rearm_evidence_log
lgrc9v3_autonomous_producer_idempotency_keys
lgrc9v3_autonomous_production_log
```

`LGRC9V3.load(...)` restores those fields through the runtime-state artifact,
so route-aspect trigger config and completed self-rearm evidence survive
save/load.

The autonomous production log makes producer records replayable from snapshots
without requiring the caller to retain the return value from `produce_events`.
Artifact-only validation can now use:

```text
snapshot.events
dynamics.lgrc9v3_runtime.cached_quantities.lgrc9v3_autonomous_production_log
```

The snapshot tests also verify that save/load does not create duplicate
producer, self-rearm, or packet-event records, and that a loaded runtime can
continue the loop while preserving duplicate-trigger suppression and event
ordering.

Telemetry now exposes packet-loop evidence in:

```text
event extension:
    event_domain = "self_rearm"
    self_rearm_status
    route_aspect_id
    route_aspect_digest
    producer_record_id
    parent_packet_id
    child_packet_id
    parent_arrival_event_id
    child_departure_event_id
    native_self_rearm_evidence
    native_d2_3_equivalent
    movement_claim_allowed

step/checkpoint extension:
    packet_loop.route_aspect_surplus_trigger_configured
    packet_loop.route_aspect_digest
    packet_loop.producer_policy
    packet_loop.latest_reason_code
    packet_loop.autonomous_production_result_count
    packet_loop.self_rearm_evidence_count
    packet_loop.completed_self_rearm_count
    packet_loop.native_lgrc9v3_execution
    packet_loop.native_packet_execution
    packet_loop.native_surplus_trigger
    packet_loop.native_self_rearm_evidence
    packet_loop.native_d2_3_equivalent_requires_control_parity
    packet_loop.native_grc9v3_loop_evidence
    packet_loop.movement_claim_allowed
```

Added the runnable example:

```text
examples/lgrc9v3/native_packet_loop.py
```

and linked it from:

```text
examples/lgrc9v3/README.md
```

The reference guide now documents the native packet-loop route-aspect surface,
snapshot/telemetry evidence, and claim boundary:

```text
docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
```

Strict follow-up from review:

```text
snapshot round-trip preserves route-aspect config/digests and self-rearm logs
snapshot round-trip preserves autonomous producer records
save/load does not duplicate packet, producer, or self-rearm records
continue-after-load preserves route order and duplicate suppression
disabled-policy save/load remains default-off and emits no self-rearm evidence
telemetry checkpoint cached producer log validates with the artifact-only validator
```

The continue-after-load test found and fixed a persistence-sensitive route
validation issue: restored GRC9V3 `PortEdge` records can normalize endpoint
orientation, while topology edge endpoint order preserves the actual route
direction. Route-aspect state validation now checks route direction against the
topology edge endpoints, so route-aspect replay identity remains stable after
snapshot restore.

Run record:

```bash
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/native_packet_loop.py
    completed_self_rearm_count = 6
    cycle_count = 3
    native_d2_3_equivalent = true
    movement_claim_allowed = false
    native_grc9v3_loop_evidence = false

PYTHONPATH=src .venv/bin/python \
    tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py
    7 tests passed
    9 tests passed after adding producer-log persistence,
    continue-after-load, and default-off save/load checks

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity -q
    40 tests passed
    42 tests passed after strict persistence follow-up

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity -q
    98 tests passed
    100 tests passed after strict persistence follow-up

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    183 tests passed
    185 tests passed after strict persistence follow-up

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    978 tests passed
    980 tests passed after strict persistence follow-up

PYTHONPATH=src .venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/lgrc_9_v3_runtime_state.py \
    src/pygrc/telemetry/lgrc9v3_contract.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py \
    examples/lgrc9v3/native_packet_loop.py
    passed

git diff --check
    passed
```

Claim boundary after Iteration 48:

```text
native_route_aspect_contract = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true for artifact-validated native control rows
snapshot_save_load_packet_loop_surfaces = true
telemetry_packet_loop_surfaces = true
continue_after_load_packet_loop_surfaces = true
snapshot_exported_producer_log_validation = true
adapter_required_for_d2_3_semantics = false for validated native rows
movement_claim_allowed = false
native_grc9v3_loop_evidence = false
```

## Iteration 49. Native Packet-Loop Closeout

Status: complete.

### Goal

Close the continuation with an explicit native-support classification.

### Possible Classifications

- [x] `native_d2_3_equivalent_packet_loop_supported`
- [ ] `native_packet_loop_partially_supported`
- [ ] `native_surplus_trigger_supported_self_rearm_missing`
- [ ] `native_route_aspect_supported_trigger_missing`
- [ ] `not_supported_without_adapter`

### Checks

- [x] Record all commands.
- [x] Record all artifacts.
- [x] Record supported and blocked claims.
- [x] Compare against E2 closeout.
- [x] State whether the experiment-local adapter is still needed.
- [x] State whether `native_d2_3_equivalent` is true or false.
- [x] State whether `adapter_required_for_d2_3_semantics` is true or false.
- [x] State whether `native_static_route_only` is true or false.
- [x] State whether any further core task is requested.
- [x] State whether movement-ladder handoff is still blocked.

### Verification

- [x] Focused tests pass.
- [x] Full LGRC test sweep passes.
- [x] `git diff --check` passes.
- [x] Closeout report is written.

### Summary

Iteration 49 complete.

Native packet-loop support is now closed as:

```text
classification = native_d2_3_equivalent_packet_loop_supported
native_lgrc9v3_execution = true
native_packet_execution = true
native_surplus_trigger = true
native_self_rearm_evidence = true
native_d2_3_equivalent = true for artifact-validated native control rows
adapter_required_for_d2_3_semantics = false for validated native rows
native_static_route_only = false for D2.3-equivalent packet-loop rows
```

Comparison with E2:

```text
E2 closeout:
    native_packet_execution_compatible
    adapter_triggered_runtime_compatible
    native_static_route_autonomy_available
    missing_native_surplus_trigger_primitive

Iteration 49 closeout:
    native route-aspect contract implemented
    native surplus-trigger producer implemented
    native self-rearm evidence implemented
    native D2.3-equivalent control parity implemented
    snapshot/telemetry persistence implemented
    N03 E3 native reproduction passed
```

The experiment-local E3 branch verifies that N03 D2.3 is reproducible using
native LGRC9V3 only. The old D2/D2.3 prototype runner and E2 adapter trigger
are not execution engines for the E3 reproduction.

E3 closeout:

```json
{"adapter_required_for_d2_3_semantics": false, "adapter_trigger_used_as_execution_engine": false, "classification": "n03_native_lgrc9v3_packet_loop_reproduced", "controls_passed": true, "core_follow_up_required": false, "native_d2_3_equivalent": true, "native_lgrc9v3_execution": true, "native_packet_execution": true, "native_self_rearm_evidence": true, "native_surplus_trigger": true, "prototype_runner_used_as_execution_engine": false, "snapshot_telemetry_replayable": true, "status": "passed"}
```

E3 positive rows:

```text
clockwise route: S1 -> K2 -> S2 -> K1 -> S1
counter-clockwise route: S1 -> K1 -> S2 -> K2 -> S1
clockwise cycles: 3
counter-clockwise cycles: 3
clockwise completed self-rearms: 12
counter-clockwise completed self-rearms: 12
max event budget error: 0.0
topology changed: false
direction symmetry: passed
```

E3 controls remain negative:

```text
no_surplus: surplus_gate_failed
subthreshold: threshold_gate_failed
threshold_too_high: threshold_gate_failed
wrong_direction: route_direction_gate_failed
forward_only: return_chain_missing
broken_return: route_aspect_closed_loop_validation_failed
scrambled_order: route_aspect_pole_contiguity_validation_failed
```

Phase 8 native packet-loop artifacts:

```text
implementation/Phase-8-LGRC9-NativePacketLoopBaselineFreeze.json
implementation/Phase-8-LGRC9-NativePacketLoopBaselineFreeze.md
examples/lgrc9v3/native_packet_loop.py
docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
experiments/2026-05-N03-grc9v3-polarized-basin-loops/configs/e3_native_lgrc9v3_packet_loop_route_manifest.json
experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_closeout.json
experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_closeout.md
```

Run record:

```bash
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/native_packet_loop.py
    completed_self_rearm_count = 6
    cycle_count = 3
    native_d2_3_equivalent = true
    movement_claim_allowed = false
    native_grc9v3_loop_evidence = false

PYTHONPATH=src .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py
    n03_native_lgrc9v3_packet_loop_reproduced

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity -q
    42 tests passed

PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_autonomy_contract \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity -q
    100 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    185 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    980 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/lgrc_9_v3_runtime_state.py \
    src/pygrc/telemetry/lgrc9v3_contract.py \
    tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py \
    examples/lgrc9v3/native_packet_loop.py \
    experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py
    passed

git diff --check
    passed
```

Blocked claims remain blocked:

```text
native GRC9V3 proposal-flux loop evidence
movement or locomotion
agency, intention, or biological behavior
identity acceptance
multi-pole generalization
```

No further core task is requested by this closeout. Movement-ladder handoff
remains blocked until a separate movement experiment explicitly opens it with
its own controls and claim boundary.
