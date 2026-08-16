# Phase 8 LGRC9 Event-Local Geometry Integration Checklist

**Date:** 2026-08-16
**Status:** Iterations 95-96 complete; closed without runtime change
**Plan:** [`Phase-8-LGRC9-EventLocalGeometryIntegrationPlan.md`](./Phase-8-LGRC9-EventLocalGeometryIntegrationPlan.md)
**Specification:** [`specs/lgrc-9-v3-event-local-geometry-integration.md`](../../../specs/lgrc-9-v3-event-local-geometry-integration.md)

## Usage Rules

- This checklist is locally admitted through Iteration 96.
- Do not mark external Gate A/B evidence as local verification without local
  admission or reproduction.
- No runtime, specification, test, example, or telemetry source changes are
  allowed before Iteration 96 closes `gate_passed`.
- Preserve the exact source state used by every claim-bearing run.
- Keep C0/C1 evidence, Phase 8 implementation evidence, and later N32 evidence
  separate.
- Preserve prior candidate failures additively; do not rewrite historical
  evidence to match the final implementation.
- Any change outside the activated source envelope requires a dependency reason
  recorded before the change.
- Producers may schedule eligible work only where the specification permits;
  packet execution remains owned by `step()`.
- Disabled mode must preserve all existing behavior.
- One valid mapped counterexample blocks an iteration; an unmapped preference
  does not silently expand the contract.
- Every iteration ends with verification, summary, open debt, and exact next
  gate.

## Current Status

```text
preparation package created = true
local repository admission = true
baseline freeze activated = true
Gate A = bounded_external_admission; not locally reproduced
Gate B = bounded_external_admission; not locally reproduced
C0/C1 registered = true
C0/C1 executed = true under valid re-registration
C0 = C0-EQUIV
C1 = C1-SCOPE; observed numerical result C1-NULL
C2 source-change gate = closed_without_runtime_change
post-C1 scope/ownership interpretation = complete_no_new_execution
Phase 8 runtime implementation opened = false
post-implementation validation opened = false
N32 selected = false
```

## Iteration 95. Evidence Import and Baseline Freeze

Status: complete; `baseline_frozen_no_source_behavior_change`.

### Goal

Establish the local source/evidence authority before any source-changing work.

### Checks

- [x] Read this specification, plan, checklist, handoff, and schema together.
- [x] Verify the preparation-package archive checksum.
- [x] Verify every bundled evidence archive checksum.
- [x] Record current branch, HEAD, and `git status --short`.
- [x] Confirm current HEAD equals `47a8a096e86a33b36466bee92738c52bf966ec50`.
- [x] Record that no source-delta audit is required because HEAD is exact.
- [x] Confirm no unreviewed local changes existed in the candidate source envelope.
- [x] Admit Gate A as bounded external evidence under exact current source.
- [x] Admit Gate B as bounded external evidence under exact current source.
- [x] Record that both external claim boundaries remain unchanged.
- [x] Confirm no existing event-local geometry-integration policy is already
      installed under another name.
- [x] Confirm no current runtime path already closes the proposed trigger,
      proposal, current lifecycle, and packet transduction relation.
- [x] Record current hashes for source, specs, tests, and existing Phase 8 docs.
- [x] Run focused GRC9V3/LGRC9V3 transport, runtime, restoration, contract,
      telemetry, and packet-loop tests.
- [x] Run the full test baseline.
- [x] Run `git diff --check`.
- [x] Freeze candidate and optional source-change envelopes.
- [x] Write the activated baseline freeze JSON/Markdown.

### Verification

```text
expected disposition:
  baseline_frozen_no_source_behavior_change
```

### Gate

- [x] Iteration 96 opened only after the baseline was clean and evidence inputs
      are readable.

## Iteration 96. C0/C1 Registration and Evidence Gate

Status: complete; `close_without_runtime_change`.

### Goal

Determine whether event-order/timing pressure beyond full-drain recurrence is
real enough to justify native substrate work.

### Checks

- [x] Instantiate C0 registration from the bundled requirements bridge.
- [x] Instantiate C1 registration from the bundled requirements bridge.
- [x] Freeze exact initial state, exogenous events, histories, frontier policy,
      timing, funding, controls, outputs, tolerances, attempt limits, and
      outcome classes.
- [x] Register C0 full-drain null.
- [x] Register C1 event-triggered global interleaving.
- [x] Include same-frontier scheduler/batching control.
- [x] Include geometry-off control.
- [x] Include packetization-off control.
- [x] Include stale-proposal control.
- [x] Include scope-leak control.
- [x] Include label, direction, scale, funding, restoration, and replay controls.
- [x] Use an independent later-effect surface rather than proposal current as
      self-proof.
- [x] Preserve the invalid first execution and execute the unchanged valid
      re-registration once.
- [x] Reconstruct independently without importing PyGRC.
- [x] Classify C0 as `C0-EQUIV`.
- [x] Classify C1 as `C1-SCOPE`, with observed numerical `C1-NULL`.
- [x] Record the external global orchestrator as the remaining hidden
      mechanism.

### Source-change decision

- [ ] `gate_passed`: all seven specification requirements pass.
- [x] `close_without_runtime_change`: C1 is null at the registered action scope
      because native current is incoming at the trigger node and no eligible
      trigger-owned geometry-derived packet work is emitted.
- [ ] `repair_and_reregister_evidence`: a bounded evidence defect is repairable.
- [ ] `invalid_no_disposition`: source/evidence integrity failed.

### Hard stop

- [x] No source-changing iteration opened because `gate_passed` was not selected.

## Post-C1 Scope And Ownership Interpretation

Status: complete; no scientific execution and no source behavior change.

### Checks

- [x] Preserve `C1-SCOPE` as the scientific result and `C1-NULL` only as the
      observed numerical result.
- [x] Record that event locus, current source, and causal-work owner are not
      interchangeable.
- [x] Record node 0 as event locus and native current sink.
- [x] Record nodes 1 and 2 as native current sources at both trigger frontiers.
- [x] Trace the direction through coherence, differential reconstruction,
      conductance, potential, and signed flux.
- [x] Record that the producer-owned global reconstruction remains a hidden
      mechanism.
- [x] Keep receptive susceptibility as an interpretation candidate only.
- [x] Block support, demand, attraction, need, recruitment, and maintenance
      semantics.
- [x] Keep source-owned distributed action and field-/edge-owned transport
      unregistered and unexecuted.
- [x] Require a new identity and prospective registration for any future
      ownership question.
- [x] Keep Iteration 97, runtime implementation, and N32 closed.
- [x] Complete a source-backed causal-work ownership pressure map without
      selecting an ownership model or opening scientific execution.

### Record

- [`Phase-8-LGRC9-EventLocalGeometryIntegrationPostC1ScopeInterpretation.md`](./Phase-8-LGRC9-EventLocalGeometryIntegrationPostC1ScopeInterpretation.md)
- [`Phase-8-LGRC9-EventLocalGeometryIntegrationPostC1ScopeInterpretation.json`](./Phase-8-LGRC9-EventLocalGeometryIntegrationPostC1ScopeInterpretation.json)
- [`Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkOwnershipPressureMap.md`](./Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkOwnershipPressureMap.md)
- [`Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkOwnershipPressureMap.json`](./Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkOwnershipPressureMap.json)

## Iteration 97. Specification and Contract-Schema Freeze

Status: closed; Iteration 96 did not select `gate_passed`.

### Goal

Close all load-bearing semantic decisions before runtime behavior changes.

### Checks

- [ ] Select same-frontier policy.
- [ ] Select native trigger boundary.
- [ ] Select causal-availability policy.
- [ ] Select dependency-closed operator or explicit approximation boundary.
- [ ] Select read scope and action scope.
- [ ] Select integration-interval policy.
- [ ] Select in-flight-state treatment.
- [ ] Select current staleness/supersession rules.
- [ ] Select direct-funding policy.
- [ ] Freeze default enabled/validated/supported flags.
- [ ] Freeze policy IDs.
- [ ] Freeze proposal record fields and digest.
- [ ] Freeze current-realization record fields and digest.
- [ ] Freeze lifecycle statuses and reason codes.
- [ ] Freeze idempotency keys.
- [ ] Freeze claim flags.
- [ ] Add contract-schema tests only.
- [ ] Confirm no proposal emission, current commitment, packet scheduling, or
      runtime mutation has been added.
- [ ] Update the dedicated specification before proceeding.

### Verification

- [ ] Contract schema round-trips.
- [ ] Malformed records fail closed.
- [ ] Hidden/future inputs fail closed.
- [ ] Disabled mode remains inert.
- [ ] `git diff --check` passes.

## Iteration 98. Causal Availability and Proposal Surface

Status: blocked on Iteration 97.

### Goal

Implement a pure, replayable event-local geometry/current proposal.

### Checks

- [ ] Add causal-availability record or digest surface.
- [ ] Record trigger event, packet, node, event time, scheduler index,
      checkpoint, and proper time.
- [ ] Record source-state digest.
- [ ] Record read scope and action scope separately.
- [ ] Verify dependency closure.
- [ ] Reject future queue outcomes and unjustified remote reads.
- [ ] Build proposal on an isolated state copy.
- [ ] Record reconstruction policy and invocation count.
- [ ] Record proposed gradient, conductance, potential, and flux.
- [ ] Keep proposal choice state annotation-only.
- [ ] Mutate no coherence, conductance, prior flux, basin state, topology,
      queue, packets, or claim flags.
- [ ] Add duplicate-trigger suppression.
- [ ] Add default-off parity tests.

### Verification

- [ ] Proposal purity tests pass.
- [ ] Scope-leak tests pass.
- [ ] Causal-availability tests pass.
- [ ] Replay/digest tests pass.
- [ ] Existing runtime tests pass.

## Iteration 99. Current Realization and Temporal Ownership

Status: blocked on Iteration 98.

### Goal

Create an explicit exactly-once lifecycle for proposed current.

### Checks

- [ ] Add current-realization record.
- [ ] Add statuses: proposed, rejected, eligible, committed, packetized,
      consumed, superseded, invalidated.
- [ ] Add reason codes.
- [ ] Add integration policy and interval identity.
- [ ] Prevent overlapping current ownership for one node/policy.
- [ ] Prevent duplicate packetization of one proposal/interval.
- [ ] Detect source-state staleness before commitment.
- [ ] Add supersession/invalidity records.
- [ ] Implement direct-funding preflight.
- [ ] Fail closed without partial scheduling.
- [ ] Schedule no claim-bearing packet work until Iteration 100.

### Verification

- [ ] Lifecycle transition matrix passes.
- [ ] Duplicate/stale/overlap controls pass.
- [ ] Funding pass/fail controls pass.
- [ ] Snapshot round-trip of records passes if state is persisted here.

## Iteration 100. Native Geometry-Derived Packet Work

Status: blocked on Iteration 99.

### Goal

Convert one committed trigger-owned current realization into generic LGRC
packet work.

### Checks

- [ ] Use the accepted integration amount and flux-sign mapping.
- [ ] Limit packet work to trigger-node action scope.
- [ ] Derive target/edge from proposal flux, not fixture routes or scores.
- [ ] Cite current realization in packet records.
- [ ] Preserve stored-edge orientation invariance.
- [ ] Fail on wrong direction, wrong scale, stale proposal, duplicate interval,
      scope leak, or underfunding.
- [ ] Apply no synchronous continuity in the packet branch.
- [ ] Preserve node-plus-packet budget at every event.
- [ ] Keep topology fixed.

### Verification

- [ ] Gate B equivalence controls pass in the admitted domain.
- [ ] Wrong-scale and wrong-direction controls fail as expected.
- [ ] Split-packet/order/delay controls preserve fully drained endpoint where
      the specification predicts equality.
- [ ] Existing packet-loop and route controls remain unchanged when disabled.

## Iteration 101. Event Trigger and Queue-Owned Recurrence

Status: blocked on Iteration 100.

### Goal

Move recurrence ownership from an external checkpoint loop into ordinary event
processing.

### Checks

- [ ] Trigger only after committed arrival/local-update boundary.
- [ ] Apply selected same-frontier semantics.
- [ ] Open at most one proposal per trigger/frontier/policy.
- [ ] Commit at most one current realization per accepted interval.
- [ ] Let ordinary packet events own debit, in-flight state, arrival, credit,
      and later trigger.
- [ ] Require no external call to begin the next positive-path cycle.
- [ ] Invalidate or supersede stale current after load-bearing state change.
- [ ] Preserve fixed topology.
- [ ] Preserve proper-time/event-time distinction.

### Verification

- [ ] Two-cycle bounded recurrence passes.
- [ ] No double-continuity control passes.
- [ ] Geometry-off and packetization-off controls remove the claimed closure.
- [ ] Same-frontier control matches the selected policy.
- [ ] Event order does not gain unclaimed physical meaning.

## Iteration 102. Snapshot, Restoration, Telemetry, and Replay

Status: blocked on Iteration 101.

### Goal

Make the new mode inspectable and restorable without changing old snapshot
semantics when disabled.

### Checks

- [ ] Persist policy state.
- [ ] Persist proposal/current lifecycle records or their owned runtime state.
- [ ] Persist interval ownership and idempotency keys.
- [ ] Persist source-state/proposal/current digests.
- [ ] Persist packet-work references.
- [ ] Extend restoration identity if required.
- [ ] Add artifact validators.
- [ ] Add telemetry rows for trigger, proposal, funding, commitment,
      packetization, consumption, supersession, rejection, and scope/funding
      failures.
- [ ] Ensure telemetry does not mutate runtime or promote claims.

### Verification

- [ ] Save/load reproduces IDs and state.
- [ ] Replay reproduces event order and budgets where promised.
- [ ] Duplicate work is not emitted after restore.
- [ ] Legacy/current snapshots remain compatible per repository policy.

## Iteration 103. Controls, Synchronous Limit, Transfer, and Stress

Status: blocked on Iteration 102.

### Goal

Pressure the completed implementation against the evidence and source
boundaries that motivated it.

### Checks

- [ ] Default-off no-regression matrix.
- [ ] Gate A state-to-current reconstruction comparison.
- [ ] Gate B flux-to-packet comparison.
- [ ] C0 full-drain null.
- [ ] C1 interleaving comparison.
- [ ] Same-frontier control.
- [ ] Geometry-off control.
- [ ] Packetization-off control.
- [ ] Stale-proposal control.
- [ ] Duplicate current/interval control.
- [ ] Scope-leak control.
- [ ] Future-leak control.
- [ ] Label-only and basin-ID-only controls.
- [ ] Prior-flux and retained-conductance controls.
- [ ] Funding and overdraw controls.
- [ ] Wrong-direction and wrong-scale controls.
- [ ] Restoration/replay control.
- [ ] Independent later-effect/anti-proxy control.
- [ ] Second fixture/topology or explicit non-transfer boundary.
- [ ] Bounded stress and determinism sweep.
- [ ] Focused tests.
- [ ] Full test suite if feasible.
- [ ] `git diff --check`.

### Verification

- [ ] Every positive claim maps to an exact test/artifact.
- [ ] Every blocked stronger claim remains false.
- [ ] No runtime path depends on fixture-authored target selection.

## Iteration 104. Documentation, Closeout, and Validation Handoff

Status: blocked on Iteration 103.

### Goal

Close the implementation tranche without turning implementation into N32
scientific evidence.

### Checks

- [ ] Update `specs/lgrc-9-v3-spec.md`.
- [ ] Finalize the dedicated specification.
- [ ] Update reference documentation.
- [ ] Add bounded examples if they materially aid inspection.
- [ ] Record enabled/validated/supported flags separately.
- [ ] Record exact source commit and changed files.
- [ ] Record focused and full regression commands/results.
- [ ] Record remaining debt and open semantic questions.
- [ ] Write Phase 8 closeout and machine-readable closeout.
- [ ] Update parent Phase 8 plan/checklist/handoff.
- [ ] Open a separate source-current validation bridge.
- [ ] Keep N32 closed pending that validation.

### Maximum closeout claim

- [ ] Only the bounded native substrate capability supported by implementation
      evidence is claimed.
- [ ] No learning, agency, ecology, formative plurality, or full Read-Back claim
      is emitted.

## Post-C1 Native Causal-Work Admission Pattern Audit

Status: complete; source audit only; no source-change gate opened.

- [x] Preserve the ownership map as an authority decomposition rather than
      selecting one owner.
- [x] Inspect packet departure eligibility and source debit.
- [x] Inspect packet arrival eligibility and target credit.
- [x] Inspect configured flux-route and route-surplus packet producers.
- [x] Inspect spark diagnostics and topology-event integration.
- [x] Inspect sink-compatibility choice/collapse.
- [x] Inspect native route arbitration and stale-candidate commitment guards.
- [x] Inspect boundary-birth proposal, funding, scheduling, and commitment.
- [x] Inspect event-time, proper-time, idempotency, lineage, replay, and stale
      protections as cross-cutting guards.
- [x] Record for each mechanism the direction proposer, funding source,
      eligibility predicate, scheduler, committer, configured residue, and
      generalization boundary.
- [x] Distinguish a recurring descriptive grammar from a shared runtime
      contract.
- [x] Record that the generic native current-source eligibility crossing is
      absent.
- [x] Keep a generic admission extension unselected pending concrete
      multi-mechanism demand.
- [x] Keep Phase 8 implementation, Iteration 97, RCAE L04 return, and N32
      closed.

Result:

```text
distributed native authority = source-supported
distributed admission grammar = observed descriptively
generic causal-work admission block = absent
current-source local eligibility crossing = absent
new generic extension justified = false pending concrete demand
runtime source modified = false
Iteration 97 opened = false
N32 selected = false
```

Evidence:

- [`Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.md`](./Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.md)
- [`Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.json`](./Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.json)
