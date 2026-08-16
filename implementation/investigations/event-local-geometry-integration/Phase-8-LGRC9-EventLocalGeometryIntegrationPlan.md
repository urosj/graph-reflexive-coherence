# Phase 8 LGRC9 Event-Local Geometry Integration Plan

**Date:** 2026-08-16
**Status:** Evidence tranche closed at Iteration 96; no source changes authorized
**Specification:** [`specs/lgrc-9-v3-event-local-geometry-integration.md`](../../../specs/lgrc-9-v3-event-local-geometry-integration.md)
**Companion checklist:** [`Phase-8-LGRC9-EventLocalGeometryIntegrationChecklist.md`](./Phase-8-LGRC9-EventLocalGeometryIntegrationChecklist.md)

## Purpose

This plan defines the repository-local path for deciding whether the post-N31
Gate A/Gate B bridge should become a native LGRC9V3 event-local geometry
integration surface.

The plan does not assume that C2 should be implemented. It first requires local
admission or reproduction of the external evidence and prospective C0/C1
execution. Only a bounded C1 order/timing result beyond the C0 full-drain null
opens the source-change gate.

The target, if authorized, is:

```text
committed LGRC packet arrival/local update
  -> causally available dependency-closed GRC proposal
  -> trigger-owned current realization
  -> directly funded geometry-derived packet work
  -> ordinary LGRC event-queue recurrence
```

The implementation remains a Phase 8 substrate continuation. It does not
constitute N32 scientific evidence.

## Inputs

### Current repository authority

- `implementation/Phase-8-LGRC9-ImplementationPlan.md`
- `implementation/Phase-8-LGRC9-ImplementationChecklist.md`
- `implementation/Phase-8-LGRC9-Handoff.md`
- `specs/lgrc-9-v3-spec.md`
- current `src/pygrc/models/lgrc_9_v3_*` runtime and contract surfaces
- current tests, telemetry, examples, and restoration identity

### Evidence and requirements inputs

The preparation package includes:

- Gate A complete evidence package;
- Gate B complete evidence package;
- C0/C1 requirements bridge;
- event-local geometry requirements contract;
- post-N31 source evidence archives;
- Phase 8 precedent documents from N25.1, multi-basin implementation, and
  N25.2 validation.

These remain external inputs until locally admitted or reproduced.

## Current Boundary

Supported before this tranche:

- native GRC9V3 state-conditioned transport and continuity write-back;
- native LGRC9V3 packet execution, event history, timing, conservation, and
  recurrence;
- bounded external Gate A state-to-current bridge;
- bounded external Gate B current-to-packet bridge;
- C0/C1 prospective requirements.

Missing before this tranche:

- ordinary LGRC event-to-geometry trigger;
- causal-availability and dependency-closed proposal semantics;
- proposal-current artifact and lifecycle;
- event/proper-time integration ownership;
- exactly-once current realization;
- native geometry-derived packet work without fixture routes/scores;
- event-queue-owned geometry recurrence;
- source-current evidence for event-local closure.

## Authority and Claim Boundary

The following transitions remain separate:

```text
external probe evidence
  -> local evidence admission/reproduction
  -> C0/C1 scientific gate
  -> Phase 8 implementation
  -> source-current validation bridge
  -> possible N32 experiment
  -> possible RCAE re-admission
```

A later native implementation does not retroactively upgrade external Gate A,
Gate B, C0, or C1 evidence.

## Scope

### Phase 8 preparation scope

- import and verify the evidence package;
- rebind all source references to current local HEAD;
- freeze current runtime behavior and absence of the candidate mode;
- prospectively register and execute C0/C1 outside source-changing iterations;
- classify the C2 implementation gate;
- freeze unresolved semantic decisions before code.

### Conditional source-changing scope

Only if the gate passes:

- add default-off policy and artifact contracts;
- add causal-availability/read-scope records;
- add pure geometry/current proposal generation;
- add current realization, temporal ownership, and staleness logic;
- add generic directly funded flux-to-packet transduction;
- integrate the trigger into ordinary event processing;
- add snapshot, telemetry, replay, and validation surfaces;
- preserve all prior behavior by default.

### Out of scope

- C3 confirmation semantics;
- topology-changing event-local geometry;
- credit, borrowing, or future-arrival funding;
- semantic role, learning, agency, ecology, or N32 claims;
- changes to RCAE;
- replacing the current synchronous GRC equations with a new theory;
- hidden global reconstruction described as native local geometry.

## Protected Invariants

The tranche must preserve:

- deterministic event queue ordering;
- scheduler time, event time, checkpoint order, and proper time as distinct;
- packet departure/arrival ownership;
- node-plus-packet conservation;
- current snapshot/load and restoration identity;
- existing causal route, pulse, topology, arbitration, multi-basin, and
  restoration behavior when the new mode is disabled;
- existing GRC9V3 semantics and tests;
- producer/executor boundary unless explicitly revised by the accepted spec;
- no runtime claim promotion.

## Source-Change Gate

No source files may change until Iterations 95 and 96 close positively.

The gate requires:

```text
C0 = stable full-drain null or understood domain result
C1 = bounded non-tied order/timing effect beyond C0
geometry dependence = passed
packet-transduction dependence = passed
independent later-effect readout = passed
replay/provenance = passed
label/score/route explanations = rejected
external orchestrator = identified remaining hidden mechanism
```

If the gate fails, close the tranche without runtime changes or reopen only the
specific evidence question.

## Candidate Source-Change Envelope

The exact envelope is frozen locally after the evidence gate. The expected
initial envelope is:

```text
src/pygrc/models/lgrc_9_v3_contract.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_timing.py
src/pygrc/models/lgrc_9_v3_packets.py
src/pygrc/models/lgrc_9_v3_geometry.py            # new if selected
src/pygrc/models/lgrc_9_v3_restoration.py
src/pygrc/models/__init__.py
specs/lgrc-9-v3-spec.md
specs/lgrc-9-v3-event-local-geometry-integration.md
tests/models/test_lgrc_9_v3_contract.py
tests/models/test_lgrc_9_v3_runtime.py
tests/models/test_lgrc_9_v3_event_local_geometry.py # new if selected
```

Later optional envelope:

```text
src/pygrc/telemetry/lgrc9v3_contract.py
tests/telemetry/test_lgrc9v3_contract.py
docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
examples/lgrc9v3/
implementation/Phase-8-LGRC9-Handoff.md
implementation/Phase-8-LGRC9-ImplementationChecklist.md
```

Any out-of-envelope change requires a recorded dependency reason before the
change.

## Iteration Map

The next unused Phase 8 iteration number in the frozen evidence baseline is 95.
The local repository must recheck this before promotion.

### Iteration 95. Evidence Import and Baseline Freeze

No source changes.

- verify all package checksums;
- record local branch, HEAD, and worktree status;
- compare local source with `47a8a096e86a33b36466bee92738c52bf966ec50`;
- classify every source difference relevant to the bridge;
- reproduce or locally admit Gate A and Gate B;
- confirm candidate policy, records, and runtime behavior are absent;
- freeze source hashes, focused tests, full regression baseline, and change
  envelope;
- activate the baseline freeze only on a clean source state.

### Iteration 96. C0/C1 Registration and Evidence Gate

No source changes.

- instantiate the prospective C0/C1 registration against current source;
- freeze histories, frontier policy, integration amount, funding domain,
  controls, readouts, and outcome classes;
- execute C0 and C1 once under their evidence rules;
- reconstruct independently;
- close the C2 source-change gate.

Permitted outcomes:

```text
gate_passed
close_without_runtime_change
repair_and_reregister_evidence
invalid_no_disposition
```

Source-current result:

```text
C0 = C0-EQUIV
C1 = C1-SCOPE (observed numerical result C1-NULL)
source-change disposition = close_without_runtime_change
Iteration 97 opened = false
```

Native reconstructed current was incoming at the registered trigger node, so
the trigger-node-owned outward action scope emitted no geometry-derived packet
work and no independent order effect. The wrong-direction control produced an
effect but cannot support the registered relation. Iterations 97-104 below are
retained as a conditional design reference only.

A completed post-C1 interpretation now distinguishes event locus, native
current source, and causal-work owner. The registered fixture had node 0 as the
event locus and sink while nodes 1 and 2 sourced the native current. This may
motivate a future receptive or source-owned question, but no such question is
registered here. It requires a new identity and cannot be treated as a repaired
C1 or as authority to open Iteration 97.

### Iteration 97. Specification and Contract-Schema Freeze

Source changes open only if Iteration 96 passes.

- resolve same-frontier policy;
- resolve causal-availability policy;
- resolve integration-interval policy;
- resolve in-flight-state policy;
- freeze default flags, record types, lifecycle, reason codes, digests,
  idempotency, and claim flags;
- update the dedicated specification before runtime behavior changes.

Contract/schema changes only. No proposal emission or packet scheduling yet.

### Iteration 98. Causal Availability and Proposal Surface

- implement read/action scope records;
- implement pure proposal construction;
- preserve source-state, policy, dependency, and timing digests;
- reject hidden/future inputs;
- emit no packet work;
- prove default-off and proposal purity.

### Iteration 99. Current Realization and Temporal Ownership

- implement proposal eligibility;
- implement current realization IDs and lifecycle;
- implement non-overlapping interval ownership;
- implement staleness/supersession;
- implement direct-funding preflight;
- still schedule no packet work unless the commitment gate is explicitly
  enabled for tests.

### Iteration 100. Native Geometry-Derived Packet Work

- implement generic sign-and-integration-amount packetization;
- limit action to trigger-node-owned outward current;
- cite current realization in every packet record;
- fail closed on underfunding, stale proposal, scope leak, duplicate interval,
  or malformed mapping;
- prohibit synchronous continuity in the packet branch.

### Iteration 101. Event Trigger and Queue-Owned Recurrence

- open proposal evaluation only after committed trigger events/frontiers;
- integrate selected same-frontier semantics;
- let ordinary packet execution create later trigger boundaries;
- verify no external checkpoint call is needed in the positive path;
- keep fixed topology.

### Iteration 102. Snapshot, Restoration, Telemetry, and Replay

- serialize policies, proposals, realizations, interval ownership, idempotency,
  packet references, and causal-availability evidence;
- extend restoration identity as required;
- add artifact validators;
- reproduce IDs, transitions, packets, budgets, and final state after restore.

### Iteration 103. Controls, Synchronous Limit, and Stress

- run default-off regressions;
- run Gate A/Gate B and C0/C1 controls;
- run same-frontier, order, delay, wrong-direction, wrong-scale, stale-current,
  duplicate-current, funding, scope-leak, label, basin-ID, restoration, and
  anti-proxy controls;
- run transfer to at least one second declared fixture/topology if the claim is
  intended to travel;
- run focused and full repository tests.

### Iteration 104. Examples, Documentation, and Closeout

- add only examples needed to make the bounded capability inspectable;
- update the LGRC specification and reference guide;
- record enabled/validated/supported status separately;
- write Phase 8 closeout;
- hand exact implementation to a separate source-current validation experiment;
- leave N32 closed.

## Design Decisions That Must Precede Source Changes

The following are mandatory pre-code decisions:

1. same-frontier policy;
2. native trigger boundary;
3. causal-availability rule;
4. exact dependency-closed operator or declared approximation;
5. action scope;
6. integration-interval policy;
7. in-flight-state treatment;
8. current staleness and supersession;
9. direct-funding domain;
10. independent later-effect interface.

The checklist may not mark the source-change gate passed while any remains
`Unknown`.

## Post-C1 Distributed Admission Audit

After the C1 closeout and ownership pressure map, a source-only audit inspected
existing LGRC admission patterns before any new mechanism was proposed:

- [`Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.md`](./Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.md)

The audit finds a recurring descriptive chain across packet transport, route
surplus, topology integration, route arbitration, and boundary birth:

```text
proposal + funding + eligibility + scheduling + commit + reception
```

It does not find a generic native current-source admission block. Existing
eligibility predicates remain mechanism-specific and retain configured policy
content. Consequently, the prospective Iterations 97-104 remain closed. Their
design is retained as a requirements reference, not as the next authorized
implementation path.

A later source-change proposal must first show concrete demand from at least
two mechanisms for the same load-bearing admission contract. Similar workflow
shape alone is insufficient.

## Verification Strategy

Each source-changing iteration must run:

- focused contract/runtime tests;
- affected Phase 8 tranche regressions;
- snapshot/restoration tests when state changes;
- telemetry tests when evidence surfaces change;
- `git diff --check`;
- source-change-envelope audit.

Iteration 103 must run the full repository suite if feasible and preserve the
exact command/result in the closeout.

## Acceptance Statement

The tranche is implementation-positive only if it installs a default-off,
source-current, replayable event-local geometry-integration surface whose
trigger, causal reads, proposal, current lifecycle, packet work, budget, and
recurrence are owned by LGRC9V3 under the selected bounded policies.

The strongest possible Phase 8 claim is a bounded native substrate capability.
It does not establish N32, learning, agency, ecology, formative plurality, or
full RC Read-Back.
