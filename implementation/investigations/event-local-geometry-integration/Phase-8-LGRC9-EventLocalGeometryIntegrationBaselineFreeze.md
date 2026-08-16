# Phase 8 LGRC9 Event-Local Geometry Integration Baseline Freeze

**Date:** 2026-08-16
**Status:** Active; `baseline_frozen_no_source_behavior_change`
**Source baseline:** `main@47a8a096e86a33b36466bee92738c52bf966ec50`
**Iteration:** 95 complete

## Boundary

This freeze records the source-current pre-extension state and the completed
Iteration 95 evidence admission. The real repository exactly equals the Graph
RC revision used by the external evidence package.

At activation:

```text
source/spec/test changes opened = false
C0/C1 locally executed = false
C2 implementation authorized = false
runtime evidence opened = false
N32 selected = false
```

## Expected Existing Source Context

At the archived baseline:

- synchronous GRC9V3 state/geometry/current closure exists;
- LGRC9V3 native packet/event execution exists;
- `LGRC9V3.step()` does not call synchronous `GRC9V3.step()`;
- `prepare_lgrc9v3_grc9v3_diagnostics(...)` provides an explicit diagnostic
  reconstruction but is not ordinary causal execution;
- causal routes and packet producers can schedule work, but route selection is
  configured or producer-mediated;
- native route arbitration consumes externally emitted candidate records and
  scores;
- no dedicated event-local geometry proposal/current-realization records exist;
- no native geometry-derived fixed-topology packet transduction is installed;
- no event-queue-owned event-to-geometry recurrence is supported.

These observations were rechecked at local HEAD. Existing
`causal_availability_buffers` vocabulary remains a packet-arrival eligibility
surface; it is not the proposed event-local geometry proposal/current
lifecycle.

## Evidence Inputs To Verify

- Gate A archive and checksum;
- Gate B archive and checksum;
- C0/C1 requirements bridge and checksum;
- event-local requirements contract and checksum;
- post-N31 evidence archives and internal manifests/checksums;
- N25.1/Phase 8/N25.2 precedent files.

Gate A and Gate B were accepted through bounded external admission. Their
claim-bearing runs were not locally reproduced. The C0/C1 bridge and other
archives remain external requirements/evidence inputs identified by digest.

## Candidate Source-Change Envelope

No source change is permitted during baseline activation.

If Iteration 96 later passes, the initial candidate envelope is:

```text
src/pygrc/models/lgrc_9_v3_contract.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_timing.py
src/pygrc/models/lgrc_9_v3_packets.py
src/pygrc/models/lgrc_9_v3_geometry.py (new, if selected)
src/pygrc/models/lgrc_9_v3_restoration.py
src/pygrc/models/__init__.py
specs/lgrc-9-v3-spec.md
specs/lgrc-9-v3-event-local-geometry-integration.md
tests/models/test_lgrc_9_v3_contract.py
tests/models/test_lgrc_9_v3_runtime.py
tests/models/test_lgrc_9_v3_event_local_geometry.py (new, if selected)
```

Optional later envelope:

```text
src/pygrc/telemetry/lgrc9v3_contract.py
tests/telemetry/test_lgrc9v3_contract.py
docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
examples/lgrc9v3/
implementation/Phase-8-LGRC9-Handoff.md
implementation/Phase-8-LGRC9-ImplementationChecklist.md
```

Any expansion requires a recorded dependency reason before modification.

## Protected Invariants

- current GRC9V3 equations and default behavior;
- current LGRC9V3 deterministic queue and packet semantics;
- scheduler/event/checkpoint/proper-time distinctions;
- node-plus-packet conservation;
- snapshot/load and restoration identity;
- default-off behavior of all existing Phase 8 tranches;
- route-aspect, pulse, topology, reabsorption, arbitration, multi-basin, and
  restoration contracts;
- no claim promotion from runtime code;
- no retroactive reclassification of Gate A/B or P2-I3 evidence.

## Activated Local Source Baseline

```text
branch = main
HEAD = 47a8a096e86a33b36466bee92738c52bf966ec50
HEAD matches external Graph RC evidence source = true
worktree before import-pressure record = clean
source drift = none
candidate source-envelope changes = none
candidate event-local mode = absent
next unused Phase 8 iteration = 95
```

The source hash manifest is
[`Phase-8-LGRC9-EventLocalGeometryIntegrationBaselineSourceHashes.json`](./Phase-8-LGRC9-EventLocalGeometryIntegrationBaselineSourceHashes.json),
SHA-256 `a30fbebd98ebc112e24e35c4d5a0b643c37e1b5f0c3b7b85060fdc0d9269a303`.

## Required Focused Verification

At minimum:

```text
tests/models/test_grc_9_v3_transport.py
tests/models/test_grc_9_v3_step.py
tests/models/test_grc_9_v3_choice_budget.py
tests/models/test_lgrc_9_v3_contract.py
tests/models/test_lgrc_9_v3_runtime.py
tests/models/test_lgrc_9_v3_restoration.py
tests/models/test_lgrc_9_v3_native_packet_loop_control_parity.py
tests/telemetry/test_lgrc9v3_contract.py
```

Results:

```text
focused baseline = 348 tests passed in 4.244s
full baseline = 1,211 tests passed in 248.123s
runtime/source behavior changes = none
```

## External Evidence Identities And Admission

```text
preparation package:
  sha256 = e71b5326fcafc19ff61f3d6975d25fa9a79d54ea367aee5d7196c82f3a43fead
  package checksums = passed

Gate A archive:
  sha256 = 9260f92787d4dcf48e8099a9ce391948c7dec24c2978cfcc305468ee5320c67e
  decision = bounded_external_admission
  locally reproduced = false

Gate B archive:
  sha256 = 9faf46e5c0b9d5b70b7a42a3b5a0a91cb045156fb33017c39702c526fddf33ad
  decision = bounded_external_admission
  locally reproduced = false

C0/C1 bridge archive:
  sha256 = 1a564bd39ec300033471cc65e50924d06b82311e8c20c2281afb8d6089decd62
  role = external requirements input
```

## Iteration 95 Disposition

```text
baseline disposition = baseline_frozen_no_source_behavior_change
Iteration 96 may open = true
C2 source-change gate = closed pending Iteration 96
```

## Claim Boundary

This baseline may claim only:

> The current Graph RC source state and relevant external evidence were frozen
> before any event-local geometry-integration source change.

It may not claim the mechanism is required, implemented, validated, supported,
or N32.
