# Phase 8 LGRC9 Causal Pulse-Substrate Surface Lineage Closeout

Status: complete.

This closes the Phase 8 continuation for native causal pulse-substrate surface
lineage transport.

## Result

```text
claim_ceiling = native_causal_pulse_substrate_surface_lineage_transport_supported
native_causal_pulse_substrate_surface_lineage_transport = supported
surface_rows_superseded_after_committed_topology_events = true
surface_rows_transported_through_explicit_lineage_maps = true
artifact_only_lineage_replay_validator = true
producer_stale_read_prevention = true
movement_claim_allowed = false
adaptive_topology_entry_allowed = false
```

LGRC9V3 now supports default-off native causal pulse-substrate surface lineage
transport. A committed topology event can either supersede stale surface
evidence or transport it through an explicit complete lineage map. Producers
read only lineage-current surface rows: fixed-topology rows when unaffected,
transported successor rows after topology transport, and never stale
pre-topology source rows.

This is runtime evidence transport. It is not movement, adaptive topology,
choice, agency, locomotion, biology, or identity acceptance.

## Implemented Capability

The continuation added:

- default-off LGRC-3-only surface lineage transport policy;
- lineage statuses for `transported_topology_lineage` and
  `superseded_by_topology_event`;
- serializable lineage transport/supersession records;
- canonical topology-event and lineage-record digests;
- duplicate suppression via lineage idempotency keys;
- transported successor surface rows;
- fail-closed supersession when transport cannot be proven;
- artifact-only lineage replay validation;
- coupling/feedback producer stale-read prevention;
- snapshot, reload, and telemetry support.

The producer rule is:

```text
No valid lineage map:
    supersede the old row and block producer eligibility.

Complete valid lineage map:
    emit a transported successor row and allow producer eligibility to read
    the successor digest only.
```

## Evidence

Primary closeout artifacts:

- baseline freeze:
  [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageBaselineFreeze.json`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageBaselineFreeze.json)
- plan:
  [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md)
- checklist:
  [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageChecklist.md)
- closeout JSON:
  [`Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json`](./Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageCloseout.json)

Source hashes:

```text
Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineageBaselineFreeze.json
  sha256 = 1cd675071246a43368f76072497d1e0da730fd1ba8eebcf7f3c0e5d3ceb28933

Phase-8-LGRC9-CausalPulseSubstrateSurfaceLineagePlan.md
  sha256 = e1bf41fbaf2a5cfa4bcd8a44d32ee492b0e42fad9114153a55e2153bdfa83e42
```

Input N04 blocker:

```text
N04 Iteration 19-B primary_blocker =
causal_pulse_substrate_surface_v1_requires_fixed_topology_lineage_status
```

This closeout addresses that runtime capability blocker. It does not rerun the
N04 adaptive-topology probe; that belongs to N04 Iteration 19-C.

## Controls

The continuation passes controls for:

- missing topology event;
- missing lineage map;
- partial lineage map;
- budget mismatch;
- stale producer read;
- direct surface rewrite;
- duplicate transport record;
- topology-only claim promotion;
- disabled/default-off behavior;
- LGRC-0/LGRC-1 inertness.

Controls fail closed with distinct blockers. Producer stale reads are blocked
with `producer_stale_surface_read_blocked` or the supersession-specific stale
surface reason.

## Snapshot And Telemetry

Snapshot save/load preserves:

- source surface rows;
- topology event logs;
- lineage transport/supersession records;
- transported surface rows;
- producer records;
- lineage idempotency keys.

Continue-after-load does not duplicate transported or superseded rows. After
reload, producers read transported successor digests and continue to block
superseded source rows.

Formal telemetry support is included in `src/pygrc/telemetry`:

- lineage summaries are emitted only when lineage transport policy is enabled;
- checkpoint extensions include the lineage log only when enabled;
- default-off telemetry remains backward-compatible and does not emit lineage
  sections.

## Claim Boundary

These remain blocked:

```text
movement_claim_allowed = false
native_m6 = false
adaptive_topology_entry_allowed = false
topology_mutating_movement_claim_allowed = false
locomotion_like_claim_allowed = false
biological_claim_allowed = false
agency_claim_allowed = false
identity_acceptance_claim_allowed = false
choice_or_agency_claim_allowed = false
unrestricted_movement_claim_allowed = false
```

Runtime producers emit evidence and schedule work. They do not emit claim
labels or claim-promotion decisions.

## Validation Scope

Producer records still do not serialize a canonical `producer_record_digest`.
Artifact validators therefore validate producer linkage by:

```text
causal_surface_digest
reason_code
scheduler_event_index / scheduler order
scheduled_event_id
source or transported surface status
```

This is sufficient for the current contract, but weaker than full producer
record digest validation. Future hardening can add `producer_record_digest`.

## Verification

Latest focused verification:

```bash
.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_runtime.py -q
# 94 passed

.venv/bin/python -m pytest tests/telemetry/test_lgrc9v3_contract.py -q
# 5 passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_contract.py -q
# 106 passed, 24 subtests passed

.venv/bin/python -m pytest tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py -q
# 9 passed

uv run ruff check \
    src/pygrc/telemetry/lgrc9v3_contract.py \
    tests/telemetry/test_lgrc9v3_contract.py \
    tests/models/test_lgrc_9_v3_runtime.py
# passed

git diff --check
# passed
```

Full test sweep is deferred; the user will run it later. Focused Phase 8
lineage, telemetry, runtime, contract, and packet-loop compatibility suites
passed.

## N04 Return Point

Resume N04 at:

```text
N04 Iteration 19-C
```

Probe goal:

```text
Rerun the S7 topology-lineage/adaptive gate with native pulse-surface lineage
transport enabled.
```

Entry ceiling:

```text
s7_fixed_port_composed_gate_candidate
```

Success ceiling to test:

```text
adaptive_topology_entry_candidate
```

Still blocked until N04 revalidates them:

```text
topology_mutating_movement
native_lgrc_choice_selection
rc_identity_collapse
semantic_choice
agency
locomotion_like_basin_dynamics
biological_behavior
identity_acceptance
unrestricted_movement
```

## Closeout Statement

LGRC9V3 supports default-off native causal pulse-substrate surface lineage
transport. Committed topology events can supersede or transport causal
pulse-substrate surface evidence through explicit lineage maps; artifact-only
validators replay the packet/surface/topology/transported-surface/producer
chain; producers are blocked from stale pre-topology surface reads. Existing
fixed-topology pulse-substrate, packet-loop, topology, snapshot, telemetry,
and GRC9V3 behavior remains compatible. Movement, adaptive topology,
topology-mutating movement, native LGRC choice selection, RC identity
collapse, agency, locomotion-like behavior, biological behavior, and identity
acceptance remain blocked unless N04 Iteration 19-C or later validators
independently open them.
