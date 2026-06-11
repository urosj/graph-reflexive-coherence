# Phase 8 LGRC9 Causal Pulse-Substrate Surface Checklist

This checklist tracks implementation of:

- [`Phase-8-LGRC9-CausalPulseSubstratePlan.md`](./Phase-8-LGRC9-CausalPulseSubstratePlan.md)

The task is to move the N04 Lane E hybrid causal pulse-substrate surface from
an experiment-local proof of contract into native `LGRC9V3` runtime surfaces,
without changing the deterministic packet/event mutation boundary.

## Ground Rules

- Require LGRC-2 or higher; the surface depends on committed packet events.
- Preserve the producer/step boundary:
  producers observe, record, and schedule; `step()` mutates coherence.
- Keep all new behavior default-off and policy-gated.
- Separate:
  - native node-plus-packet conservation budget,
  - derived surface accounting,
  - claim/economy accounting.
- Emit surface rows only from committed source packet events.
- Preserve event-time/proper-time/checkpoint distinction.
- Treat "response" mechanically: declared surface-state update under a
  serialized `surface_update_policy`, not autonomous reaction.
- Producers must not write coherence, support masks, centroids, displacement,
  topology, or claim flags.
- Producers must not emit claim labels or claim promotion decisions.
- Producer evidence is mechanical scheduling eligibility, not choice or
  agency.
- Deformation tokens are not RC identity carriers.
- Native surface v1 is fixed-topology. LGRC-3 topology-lineage transport is
  deferred and topology-changing surface runs must fail closed.
- Movement, locomotion-like, adaptive-topology, biological, agency, native
  M6, and identity-acceptance claims remain blocked by default.
- Preserve existing scheduled packet, native packet-loop, static route,
  boundary birth, spark, topology, snapshot, telemetry, and example behavior.

## Iteration 50. Baseline Freeze

Status: complete.

### Goal

Freeze current LGRC9V3 behavior and N04 Lane E evidence before source changes.

### Checks

- [x] Record git commit and dirty working-tree state.
- [x] Record exact commands and environment for:
  - focused LGRC9V3 runtime tests;
  - native packet-loop tests;
  - LGRC test sweep;
  - GRC9V3 tests;
  - lint/ruff baseline;
  - `git diff --check`.
- [x] Confirm `git diff -- src` is empty before implementation.
- [x] Confirm `git status --short src` is empty before implementation.
- [x] Record N04 Lane E artifacts and SHA-256 digests:
  - `outputs/hybrid_lgrc_pulse_substrate_surface_probe.json`;
  - `outputs/hybrid_lgrc_lane_c_feedback_surface_compatibility.json`.
- [x] Confirm existing packet-loop closeout remains supported.
- [x] Confirm old static-route autonomy remains supported.
- [x] Confirm LGRC-2 packetized fixed-topology mode is available.
- [x] Record snapshot schema and LGRC9V3 telemetry format baseline.
- [x] Record deterministic seed/reproducibility baseline.
- [x] Record test-count baseline for focused and sweep suites.
- [x] Reference native packet-loop Iteration 49 closeout and gate-map position.
- [x] Confirm no native pulse-substrate surface rows or claims exist in the
  current baseline artifacts.
- [x] Confirm no native pulse-substrate support claim exists yet.

### Artifacts

- [`Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.md`](./Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.json`](./Phase-8-LGRC9-CausalPulseSubstrateBaselineFreeze.json)

### Expected Baseline Claim Flags

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

## Iteration 51. Native Surface Contract

Status: complete.

### Goal

Add the default-off serializable native causal pulse-substrate surface
contract.

### Checks

- [x] Add schema version, surface id, policy id, and digests.
- [x] Add `enabled` and `validated` flags separately.
- [x] Add serialized surface policy:
  - disabled means no rows and no producers;
  - enabled does not imply validated or supported.
- [x] Define surface policy as the serialized activation gate controlling
  surface row emission and producer eligibility evaluation.
- [x] Add runtime-visible input declarations for each `surface_kind`:
  - `local_support_mass`;
  - `boundary_polarity_score`;
  - `proper_time_phase`;
  - `surface_deformation`;
  - `route_local_pulse_contact`;
  - `feedback_eligibility`.
- [x] Surface schema validates that `surface_kind` determines required fields
  and runtime-visible inputs; for example, `boundary_polarity_score` requires
  declared front/rear masks, while `route_local_pulse_contact` requires pulse
  route/channel fields.
- [x] Record `min_lgrc_level = 2` in the contract artifact.
- [x] Reject causal pulse-substrate surface rows below LGRC-2.
- [x] Validate `surface_kind` against the fixed v1 enum.
- [x] Validate `surface_update_policy` structure:
  - `policy_id`;
  - `version`;
  - `activation_gate`;
  - `allowed_surface_kinds`.
- [x] Reject budget-surface ambiguity and merged node-plus-packet/surface
  accounting fields.
- [x] Reject producer writes to system-only fields.
- [x] Reject producer or row claim-promotion attempts.
- [x] Reject non-fixed lineage status in native surface v1.
- [x] Specify canonical digest algorithm and excluded fields.
- [x] Reject hidden fixture arrays and preauthored itineraries.
- [x] Add stable canonical digest for surface rows.
- [x] Add JSON round-trip tests.
- [x] Add digest stability and sensitivity tests.
- [x] Add invalid-schema tests.
- [x] Add synchronous-limit/default-off no-op tests.
- [x] Confirm old LGRC9V3 behavior unchanged with surface policy disabled.

### Implementation Notes

- Added passive contract-only surface schema in
  `src/pygrc/models/lgrc_9_v3_contract.py`.
- Added public exports from `pygrc.models`.
- Added tests in `tests/models/test_lgrc_9_v3_contract.py`.
- Added schema-level negative tests for LGRC-2 gating, budget split,
  producer/system boundary, fixed `surface_kind` enum, malformed
  `surface_update_policy`, fixed-topology v1 lineage, and claim promotion.
- Contract artifact now declares producer-writable fields, system-only fields,
  canonical digest specification, and synchronous-limit inertness.
- No runtime surface emission, packet scheduling, producer specialization, or
  snapshot persistence is implemented in Iteration 51.

### Verification

```bash
env PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract -q
# 99 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 157 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 201 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 996 tests passed

.venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_contract.py
# passed

git diff --check
# passed
```

### Required Contract Fields

```text
surface_id
schema_version
lgrc_runtime_level
surface_policy_id
surface_policy_enabled
route_aspect_id
route_aspect_digest
pulse_event_id
pulse_packet_id
pulse_event_kind
pulse_channel_id
pulse_route_step
event_time_key
scheduler_event_index
node_proper_time
source_node_id
target_node_id
contact_amount
surface_state_id
surface_state_digest
surface_kind
surface_nodes
surface_values_before
surface_values_after
surface_update_policy
surface_budget_surface
surface_budget_before
surface_budget_after
surface_budget_error
lineage_status
producer_records
claim_flags
surface_digest
```

### Field Write Boundary

```text
Producer-writable fields:
producer_records
scheduling_eligibility

System-only fields:
lgrc_runtime_level
surface_id
schema_version
surface_policy_id
surface_policy_enabled
route_aspect_digest
surface_state_digest
surface_budget_surface
surface_budget_before
surface_budget_after
surface_budget_error
lineage_status
claim_flags
surface_digest
```

## Iteration 52. Surface Emission From Committed Packet Events

Status: complete.

### Goal

Emit native route-local packet-contact surface rows only after committed
packet departure/arrival events. Local-update-derived surface kinds remain
deferred to later producer/surface specializations.

### Checks

- [x] Surface row source event exists.
- [x] Source event was processed by `step()`.
- [x] Surface emission is inert below LGRC-2: LGRC-0/LGRC-1 activation is
  rejected before rows can be emitted.
- [x] Disabled policy emits no rows and round-trips with an empty surface log.
- [x] Surface row scheduler index follows source event index.
- [x] Surface row event_time/proper_time evidence is present.
- [x] Surface row event_time/proper_time evidence is internally consistent at
  the contact node.
- [x] Surface row references route-aspect digest where route-bound.
- [x] Surface row uses runtime-visible inputs only.
- [x] Surface row records one LGRC packet budget and separate surface
  accounting.
- [x] Budget-surface ambiguity is rejected: a surface row that merges LGRC
  node-plus-packet budget with derived surface accounting is rejected or
  downgraded with a primary blocker.
- [x] Surface row does not mutate coherence.
- [x] Surface row does not write support, centroid, displacement, topology, or
  claims.
- [x] Pre-source surface rows are rejected.
- [x] Missing source event rows are rejected.
- [x] Missing digest rows are rejected.
- [x] Local-update events do not trigger surface row emission. Surface v1 filters
  source events to packet departure/arrival only.
- [x] Duplicate suppression: the same committed packet event does not generate
  multiple surface rows. The idempotency key is exactly
  `(source_event_id, surface_policy_id, surface_kind, route_aspect_digest)`.
- [x] Fixed-topology policy is recorded.
- [x] Topology-changing surface rows are rejected or downgraded with
  `primary_blocker = topology_lineage_deferred`.

### Ordering Gate

Required positive ordering:

```text
source packet event processed by step()
-> surface row emitted
-> producer evaluates committed surface row
-> optional scheduled packet has later scheduler index
```

### Implementation Notes

- Added default-off native surface emission controls to LGRC9V3 causal modes.
- Added route-local pulse-contact row emission after committed packet
  departure/arrival processing in `LGRC9V3.step()`.
- Added `causal_pulse_substrate_surface_log` to runtime state.
- Surface rows are passive evidence only. They do not mutate coherence,
  support masks, centroids, displacement, topology, or claim flags.
- Default-off execution emits no surface rows, no surface events, and no
  surface-count observable key.
- Surface row emission is idempotent per source event, policy, surface kind,
  and route-aspect digest.
- `step()` processes one queued packet event at a time in the current runtime;
  multi-event ordering is therefore checked as sequential event-queue ordering,
  not as multiple packet events inside one `step()` call.
- Native surface v1 rejects topology-changing runtime activation; LGRC-3
  lineage transport remains deferred.

### Verification

```bash
env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 175 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 219 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 1014 tests passed

.venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/lgrc_9_v3_runtime_state.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_runtime.py \
    tests/models/test_lgrc_9_v3_contract.py
# passed
```

## Iteration 53. Snapshot, Telemetry, And Replay

Status: complete.

### Goal

Make native surface evidence persistent and artifact-validatable.

### Checks

- [x] Snapshot saves and loads surface policy.
- [x] Snapshot saves and loads surface rows.
- [x] Snapshot saves and loads surface digests.
- [x] Snapshot saves and loads disabled policy state with an empty surface log.
- [x] Snapshot save/load does not duplicate rows.
- [x] Continue-after-load preserves surface ordering and producer suppression.
- [x] Telemetry/snapshot events export surface rows.
- [x] Snapshot surface rows and telemetry event rows carry the same digests in
  the same order.
- [x] Formal `pygrc.telemetry` LGRC9V3 event extensions classify surface rows
  with `event_domain = pulse_substrate_surface`.
- [x] Formal `pygrc.telemetry` LGRC9V3 step/run/checkpoint extensions export
  `causal_pulse_substrate_surface` summaries and checkpoint surface logs.
- [x] Surface rows persist `producer_records`; non-empty producer reason-code
  telemetry remains deferred to Iterations 54/55 where producers are added.
- [x] Telemetry/snapshot rows export budget-surface split.
- [x] Telemetry/snapshot rows export claim flags.
- [x] Artifact-only validator reconstructs:
  - source event;
  - surface row;
  - producer record;
  - scheduled packet, if any;
  - processed packet, if any.
- [x] Artifact-only validator rejects:
  - surface rows from LGRC-0/LGRC-1 artifacts;
  - surface row without committed source event;
  - surface row sourced from local-update events;
  - producer record before source event commitment;
  - producer record referencing a missing surface row;
  - missing `route_aspect_digest` on route-bound rows;
  - inconsistent event_time/proper_time at the contact node;
  - surface digest mismatch;
  - corrupted or incomplete chain.
- [x] Old snapshots/telemetry without surface rows still load.

### Implementation Notes

- Added artifact-only validator
  `validate_lgrc9v3_causal_pulse_substrate_surface_artifacts`.
- Runtime snapshots now round-trip native surface rows, digests, budget-surface
  split, claim flags, causal modes, and surface logs.
- Formal LGRC9V3 telemetry now exports pulse-substrate surface event fields,
  step/run summaries, and graph-checkpoint surface logs through
  `src/pygrc/telemetry/lgrc9v3_contract.py`.
- Snapshot load remains backward-compatible with old runtime artifacts that do
  not contain `causal_pulse_substrate_surface_log`. No core snapshot schema
  version bump is required for this additive optional runtime field; new
  snapshots include the field explicitly.
- Continue-after-load preserves surface ordering and idempotency: a saved
  post-departure row is not duplicated, and the later arrival emits one new row.
- Validator rejects missing committed source events, early producer records,
  orphaned producer records, sub-LGRC2 rows, local-update-sourced rows,
  inconsistent contact-node proper time, missing route-aspect digests, digest
  mismatches, and corrupted rows.

### Verification

```bash
env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 175 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 219 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 1014 tests passed

.venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/lgrc_9_v3_runtime_state.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_runtime.py \
    tests/models/test_lgrc_9_v3_contract.py
# passed
```

## Iteration 54. Pulse-Substrate Coupling Producer

Status: complete.

### Goal

Add a default-off producer specialization that reads surface rows and schedules
eligible coupling work without mutating coherence.

### Checks

- [x] Producer disabled by default.
- [x] Producer reads committed surface rows only.
- [x] Producer emits eligibility and non-trigger records.
- [x] Producer records:
  - policy id;
  - surface id;
  - surface digest;
  - source pulse event id;
  - observed value;
  - reference value;
  - threshold;
  - reason code;
  - scheduled packet id, if scheduled.
- [x] Producer schedules only through existing LGRC scheduling surface.
- [x] Producer does not mutate coherence.
- [x] Producer does not write support, centroid, displacement, topology, or
  claims.
- [x] Duplicate suppression works.
- [x] Controls remain negative for Iteration 54-owned surfaces:
  - disabled policy;
  - pulse disabled/no committed surface row;
  - coupling disabled/no coupling config;
  - subthreshold;
  - duplicate/idempotent replay.
- [x] Direct-write, claim-write, and budget-ambiguity controls remain enforced
  by the Iteration 51/52 surface schema and artifact validator.
- [x] Scrambled route/order control is not an Iteration 54 runtime condition:
  this producer reads one committed surface row and has no route-order
  semantics. Ordered/scrambled multi-row controls remain part of Iteration 56
  and N04 Lane F validation.

### Implementation Notes

- Added producer policy
  `packet_departure_from_pulse_substrate_coupling_policy`.
- Added coupling reason codes:
  - `pulse_substrate_coupling_disabled`;
  - `pulse_substrate_coupling_subthreshold`;
  - `pulse_substrate_coupling_packet_departure_scheduled`.
- Added `set_pulse_substrate_coupling_producer(...)` as a policy/configuration
  surface. It stores eligibility configuration only; it does not mutate
  coherence, support, centroid, displacement, topology, or claims.
- The coupling producer reads the latest committed
  `route_local_pulse_contact` surface row and compares `contact_amount` against
  a configured reference/threshold.
- Eligible coupling schedules packet work via the existing LGRC packet queue.
  Coherence remains unchanged until `step()` processes the scheduled packet
  departure.
- Producer evidence explicitly records mutation-boundary fields:
  `producer_mutated_coherence = false`, `producer_marked_packet_processed =
  false`, `producer_emitted_claim_label = false`, and `direct_claim_write =
  false`.
- Disabled surface policy suppresses the coupling producer completely:
  no producer records are emitted and no queued work is added.
- Producer-generated departures are scheduled no earlier than existing queued
  work, preserving pre-existing packet queue order.
- Producer evidence records threshold/reference/amount provenance as
  serialized producer policy fields, not hidden fixture state.
- Duplicate suppression is keyed by source surface digest, source pulse event,
  selected source/target/edge, observed value, reference, threshold, and packet
  amount. Identical keys suppress replay; distinct keys permit a new declared
  evaluation.
- The producer result uses the committed surface row digest as its causal
  surface digest so artifact-only validation can link producer evidence back to
  the source row.
- Producer policy configuration round-trips through snapshot/load before
  evaluation.
- Artifact-only digest linkage, orphaned producer rejection, early-producer
  rejection, and claim-promotion rejection remain covered by the Iteration 53
  validator.

### Verification

```bash
env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 189 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 233 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 1028 tests passed

.venv/bin/ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_runtime.py
# passed
```

## Iteration 55. Feedback-Coupled Pulse Producer

Status: complete.

### Goal

Add a default-off producer specialization for Lane C-style feedback
eligibility over the same native surface.

### Checks

- [x] Producer disabled by default.
- [x] Producer reads committed feedback surface rows only.
- [x] Feedback surface uses runtime-visible inputs:
  `committed_surface_rows`, `eligibility_thresholds`, and `producer_policy`.
- [x] Feedback row records:
  `boundary_polarity_score = (front_mass - rear_mass) - reference_delta`.
- [x] Producer waits for source packet event to be processed by `step()` and
  resulting surface row to be emitted.
- [x] Producer emits feedback eligibility evidence.
- [x] Producer may schedule next pulse only through LGRC scheduling.
- [x] Producer records polarity and expected next route/channel.
- [x] Controls remain negative:
  - pulse disabled;
  - feedback disabled;
  - subthreshold feedback;
  - wrong polarity;
  - source-surface/order mismatch;
  - claim-write attempt;
  - budget-violating synthetic blocker.
- [x] Native M6 remains false unless later N04 Lane F validators pass.

### Implementation Notes

- Added feedback producer policy
  `packet_departure_from_feedback_eligibility_policy`.
- Added feedback reason codes:
  - `feedback_coupled_pulse_disabled`;
  - `feedback_coupled_pulse_subthreshold`;
  - `feedback_coupled_pulse_wrong_polarity`;
  - `feedback_coupled_pulse_order_mismatch`;
  - `feedback_coupled_pulse_packet_departure_scheduled`.
- Added `emit_feedback_eligibility_surface_row(...)` to serialize a committed
  feedback surface row derived from the latest packet-contact surface row and
  declared front/rear masks.
- Added `set_feedback_coupled_pulse_producer(...)` as a policy/configuration
  surface. It records source/target/edge, expected polarity, threshold, packet
  amount, expected source surface digest, and expected next route/channel.
- The producer reads only committed `feedback_eligibility` rows, emits evidence
  records, and may enqueue packet work only through LGRC scheduling.
- Feedback producer evidence records
  `regenerated_pulse_source = feedback_eligibility` and
  `copied_from_original_schedule = false`.
- Producer evidence explicitly records mutation-boundary fields:
  `producer_mutated_coherence = false`, `producer_marked_packet_processed =
  false`, `producer_emitted_claim_label = false`, and `direct_claim_write =
  false`.
- Feedback surface rows are emitted after their source
  `route_local_pulse_contact` row and use
  `surface_kind = feedback_eligibility`.
- Feedback rows serialize declared front/rear masks in the update policy.
- Disabled surface policy suppresses the feedback producer completely:
  no producer records are emitted and no queued work is added.
- Feedback producer evidence records threshold/polarity/amount provenance as
  serialized producer policy fields.
- Feedback duplicate suppression prevents replay from identical committed
  feedback rows.
- Producer-generated departures are scheduled no earlier than existing queued
  work, preserving pre-existing packet queue order.
- Feedback producer policy configuration round-trips through snapshot/load
  before evaluation.
- Negative controls cover no committed row/config, subthreshold feedback, wrong
  polarity, source-surface/order mismatch, and budget violation.
- Claim flags remain blocked: `native_m6 = false`,
  `movement_claim_allowed = false`, and locomotion/adaptive/agency identity
  claims remain unavailable.
- Synchronous-limit producer inertness is retained for Iteration 56 controls:
  it is a whole-surface control because these producers intentionally require
  committed packet-event surface rows.

### Verification

```bash
env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 189 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 233 tests passed

env PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
# 1028 tests passed

.venv/bin/ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_runtime.py
# passed
```

## Iteration 56. Controls And N04 Lane F Bridge

Status: complete.

### Goal

Prove native surface behavior under controls and produce N04 Lane F evidence
without overclaiming movement.

### Checks

- [x] Run native surface positive fixture.
- [x] Run coupling producer controls.
- [x] Run feedback producer controls.
- [x] Run disabled/default-off controls.
- [x] Run synchronous-limit no-op control.
- [x] Run LGRC-0/LGRC-1 inertness control; verify no surface rows, no producer
  records, and no scheduled packets under sub-LGRC-2 runtime levels.
- [x] Run producer-coherence-mutation control; verify rejection with
  `primary_blocker = producer_mutation_boundary_violation`.
- [x] Run producer/step boundary runtime audit; verify producer evaluation
  schedules queued work without changing node or packet coherence, and `step()`
  performs the later coherence mutation.
- [x] Run budget-surface-merging control; verify rejection with
  `primary_blocker = budget_surface_ambiguity`.
- [x] Run disabled-surface/enabled-producer conflict control; verify no
  producer records and no queued work.
- [x] Run snapshot continue-after-load with coupling and feedback producers
  enabled; verify producer scheduling and queue ordering survive load.
- [x] Run fixed-topology audit; verify `topology_changed = false` and
  `topology_events_enabled = false` in positive/control lanes.
- [x] Run topology-changing negative/deferred control; verify
  `primary_blocker = topology_lineage_deferred` and no native support claim.
- [x] Record LGRC-3 lineage transport as out of scope for native surface v1.
- [x] In the N04 Lane F validator, verify regenerated native pulse work is not
  copied from the original E3 schedule.
- [x] Run artifact-only validator.
- [x] Run artifact-only validator on the N04 Lane F bridge artifact and record
  `artifact_validation_on_lane_f_artifacts = true`.
- [x] Record SHA-256 digests for positive fixture surface log, producer records,
  scheduled packets, and processed packet events.
- [x] Verify all declared coupling and feedback producer reason codes are
  exercised by the positive fixture and controls.
- [x] Run old scheduled packet route replay tests.
- [x] Run old static-route autonomy tests.
- [x] Run native packet-loop tests.
- [x] Run snapshot/telemetry compatibility tests.
- [x] Confirm Iteration 56 test counts meet or exceed Iteration 50 baseline
  counts for focused runtime, native packet-loop, sweep, and full suites.
- [x] Verify gate-map update prerequisites for Iteration 57:
  native support flags set, controls recorded, Lane F handoff artifacts exist,
  and claim boundaries are clean.
- [x] Verify native support flags:

```text
native_causal_pulse_substrate_surface_enabled = true for positive lane
native_causal_pulse_substrate_surface_validated = true only if controls pass
native_lgrc_pulse_substrate_supported = true only if artifact validators pass
```

- [x] Keep blocked unless separately validated:

```text
native_m6 = false
movement_claim_allowed = false
loop_driven_movement_claim_allowed = false
locomotion_like_claim_allowed = false
adaptive_topology_entry_allowed = false
biological_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
```

### Implementation Notes

- Added N04 Lane F bridge runner:
  `experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_native_lgrc_lane_f_surface_bridge.py`.
- Added N04 Lane F closeout runner:
  `experiments/2026-05-N04-grc9v3-movement-ladders/scripts/close_native_lgrc_lane_f.py`.
- Generated N04 Lane F artifacts:
  - `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/native_lgrc_lane_f_surface_bridge.json`;
  - `experiments/2026-05-N04-grc9v3-movement-ladders/reports/native_lgrc_lane_f_surface_bridge.md`;
  - `experiments/2026-05-N04-grc9v3-movement-ladders/outputs/n04_lane_f_native_surface_closeout.json`;
  - `experiments/2026-05-N04-grc9v3-movement-ladders/reports/n04_lane_f_native_surface_closeout.md`.
- The positive fixture runs native LGRC2 fixed-topology packet contact rows,
  coupling producer scheduling, feedback eligibility row emission, and feedback
  producer scheduling. Artifact-only validation passes with
  `native_lgrc_pulse_substrate_supported = true`.
- Artifact-only validation reconstructs the chain
  `source_packet_event -> surface_row -> producer_record -> scheduled_packet ->
  processed_packet_event`, and rejects producer records with missing reason
  codes, mutation-boundary violations, or claim-promotion evidence.
- The Lane F bridge artifact records `artifact_validation_on_lane_f_artifacts =
  true`; artifact-only validation is run against the Lane F event/producer
  artifacts, not just a generic fixture.
- Default-off/synchronous no-op and disabled-surface controls emit no producer
  records and enqueue no work.
- LGRC-0/LGRC-1 inertness control rejects construction below LGRC-2 with no
  rows, producer records, or scheduled packets.
- Producer mutation-boundary and budget-surface merging controls fail closed
  with `producer_mutation_boundary_violation` and `budget_surface_ambiguity`.
- Producer/step boundary runtime audit records no coherence mutation during
  producer evaluation, queued work after producer scheduling, and coherence
  mutation only after `step()` processes the scheduled packet.
- Snapshot continue-after-load with both producers enabled preserves producer
  scheduling and queue ordering.
- Coupling/feedback disabled, subthreshold, wrong-polarity, order-mismatch, and
  budget-violation controls fail with distinct primary blockers.
- Positive fixture artifact digests are recorded for the surface log, producer
  records, scheduled packets, and processed packet events.
- Reason-code coverage is complete for all declared coupling and feedback
  producer reason codes.
- `native_causal_pulse_substrate_surface_validated` promotion criteria are:
  positive fixture passes artifact-only validation; all controls pass; negative
  controls fail with distinct primary blockers; synchronous-limit control emits
  no rows/records; topology-changing control fails closed; and Lane F bridge
  artifacts pass validator.
- Iteration 56 records that focused runtime, native packet-loop, sweep, and
  full test counts meet or exceed the Iteration 50 baseline.
- Gate-map readiness for Iteration 57 is recorded with native support flags set,
  controls recorded, Lane F handoff artifacts present, and claim boundaries
  clean.
- The topology-changing control fails closed before construction with
  `primary_blocker = topology_lineage_deferred`; LGRC-3 surface lineage
  transport remains out of scope for v1.
- Lane F records
  `regenerated_native_pulse_work_not_copied_from_original_e3_schedule = true`
  with `regenerated_pulse_source = feedback_eligibility`.
- Lane F N04 closeout records
  `lane_f_status = native_surface_support_complete` and keeps
  `claim_ceiling = native_lgrc_pulse_substrate_surface_supported`.
- Native support is limited to the causal pulse-substrate surface contract.
  Movement, loop-driven movement, native M6, locomotion-like,
  adaptive-topology, biological, agency, and identity-acceptance claims remain
  blocked.

### Verification

```bash
.venv/bin/ruff check \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    tests/models/test_lgrc_9_v3_runtime.py \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_native_lgrc_lane_f_surface_bridge.py \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/close_native_lgrc_lane_f.py
# passed

.venv/bin/python \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_native_lgrc_lane_f_surface_bridge.py
# produced Lane F JSON/Markdown artifacts

.venv/bin/python \
    experiments/2026-05-N04-grc9v3-movement-ladders/scripts/close_native_lgrc_lane_f.py
# produced Lane F N04 closeout JSON/Markdown artifacts

.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime.LGRC9V3RuntimeTest -q
# 71 tests passed

.venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_runtime \
    tests.models.test_lgrc_9_v3_contract \
    tests.models.test_lgrc_9_v3_construction \
    tests.models.test_lgrc_9_v3_autonomy_contract -q
# 190 tests passed

.venv/bin/python -m unittest \
    tests.models.test_lgrc_9_v3_native_packet_loop_baseline \
    tests.models.test_lgrc_9_v3_native_packet_loop_route_aspect \
    tests.models.test_lgrc_9_v3_native_packet_loop_control_parity \
    tests.models.test_lgrc_9_v3_native_packet_loop_surplus_trigger -q
# 42 tests passed

.venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
# 236 tests passed

.venv/bin/python -m unittest discover tests -q
# 1031 tests passed

git diff --check
# clean
```

## Iteration 57. Closeout

Status: complete.

### Goal

Close the native pulse-substrate continuation only if native support is
artifact-validatable and old behavior remains compatible.

### Checks

- [x] Closeout report produced:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`.
- [x] Closeout JSON produced:
  `implementation/Phase-8-LGRC9-CausalPulseSubstrateCloseout.json`.
- [x] Commands and environment recorded.
- [x] Commit/worktree state recorded.
- [x] Surface schema and digest policy recorded.
- [x] Producer/step boundary audited.
- [x] Budget-surface separation audited.
- [x] Snapshot/telemetry round-trip audited.
- [x] Artifact-only validator passed.
- [x] Controls passed with primary blockers.
- [x] Claim flags recorded.
- [x] N04 Lane F handoff updated.
- [x] Phase 8 handoff updated.
- [x] No movement/identity/agency claims emitted by runtime producers.

### Artifacts

- [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.md`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.md)
- [`Phase-8-LGRC9-CausalPulseSubstrateCloseout.json`](./Phase-8-LGRC9-CausalPulseSubstrateCloseout.json)

### Minimal Closeout Statement

```text
LGRC9V3 exposes a default-off native causal pulse-substrate surface that emits
rows only from committed packet events, preserves producer/step mutation
boundaries, separates node-plus-packet conservation from derived accounting
surfaces, survives snapshot/telemetry replay, and supports policy-gated
coupling and feedback producers as scheduling evidence only. Existing packet,
route, packet-loop, snapshot, telemetry, topology, spark, and GRC9V3 behavior
remain compatible. Native movement, M6, locomotion-like, adaptive-topology,
biology, agency, and identity-acceptance claims remain blocked unless later
experiment validators independently open them.
```
