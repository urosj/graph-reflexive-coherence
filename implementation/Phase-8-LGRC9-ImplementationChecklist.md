# Phase 8 LGRC-9 Implementation Checklist

This document tracks execution of **Phase 8: `LGRC-9` Causal-History
Substrate**.

It is intentionally separate from
[`Phase-8-LGRC9-ImplementationPlan.md`](./Phase-8-LGRC9-ImplementationPlan.md):

- the plan defines scope, design constraints, workstreams, and acceptance
  criteria;
- this checklist records how the work is executed iteration by iteration.

## Usage Rules

- Treat Phase 8 as an `LGRC-9` family track, not a general LGRC family program.
- Treat `LGRC9V3` annotation/timing evidence as the first executable target,
  because `GRC9V3` is the current complete nine-port runtime.
- Treat hyphenated names such as `LGRC-9` and `LGRC-V3` as paper/family phase
  labels.
- Treat executable/runtime names as non-hyphenated: `LGRC9`, `LGRCV3`, and
  `LGRC9V3`.
- Treat pure `LGRC9` as the substrate interpretation, not the first standalone
  runtime target.
- Do not change default `GRC9` or `GRC9V3` runtime behavior.
- Implement LGRC-0 annotation before behavior-changing LGRC-1 work.
- Label LGRC-1 as semi-causal unless causal availability buffers exist.
- Treat LGRC-2 packetized causal flux as a Phase 8 continuation scope beyond
  the completed LGRC-0/LGRC-1 slice.
- Treat LGRC-3 topology-changing causal history as a later Phase 8
  continuation scope after LGRC-2 packet accounting is stable.
- Keep scheduler index, checkpoint index, event-time key, node proper time, and
  edge delay distinct.
- Preserve the three distance notions: geometric, causal/proper-time, and
  functional/coupling.
- Do not claim packetized conservation without explicit in-flight coherence
  accounting.
- Do not start LGRC-2 or LGRC-3 code without explicit decision records,
  contracts, tests, and handoffs.
- Do not rename or restructure GRCL/LGRC terminology in this phase.
- Update the plan before making a code change that changes LGRC semantics.

## Iteration Template

Copy this section for each new iteration.

```markdown
## Iteration N. <Short Name>

### Goal

<What this iteration is intended to complete>

### Checks

- [ ] <Concrete task 1>
- [ ] <Concrete task 2>
- [ ] <Concrete task 3>

### Implementation Notes

- <Important implementation detail, decision, or constraint>

### Verification

- [ ] <Import / test / review check>
- [ ] <Boundary / acceptance check>

### Summary

<Short outcome summary once iteration is complete>
```

## Current Record After Iterations 1-4

Iterations 1-4 complete the **LGRC-0 compatibility and derived annotation
slice**.

What this proves:

- stable LGRC9V3 timing vocabulary exists for `kappa`, `k`, `T_e`, `tau_i`,
  and `tau_ij`;
- causal-history modes and policy names can be validated without changing
  `GRC9V3`;
- derived lapse, edge-delay, and geometric/causal/functional distance helpers
  can run over a synchronous `GRC9V3State`;
- an LGRC-0 annotation artifact can record derived proper-time, edge-delay,
  event-time, cone, and causal basin-core evidence;
- LGRC-0 evidence round-trips through JSON and can be attached under the
  optional `causal_history` block;
- missing `causal_history` restores as non-LGRC evidence;
- old `GRC9`/`GRC9V3` snapshots and readers remain valid;
- default synchronous event counts, topology, budgets, observables, and spark
  lanes are not changed.

What this does **not** prove:

- LGRC causal propagation is implemented;
- `dt` has been replaced as the operational update driver;
- packetized event-queue flux or in-flight budget accounting exists;
- LGRC sparks are causally scheduled;
- proper-time identity persistence is implemented;
- topology-changing causal history, packet redirection, collapse, or
  reabsorption exists;
- LGRC-0 annotations are physical Lorentzian dynamics.

Safe claim:

```text
LGRC-0 timing and causal-history vocabulary can be attached to synchronous
GRC9V3 artifacts as derived annotation evidence without corrupting the
synchronous runtime.
```

Unsafe claim:

```text
LGRC is operationally validated.
```

## Iteration 0. Planning Bootstrap

### Goal

Create the Phase 8 planning documents and lock the LGRC-9-family /
LGRC9V3-first-target boundary before code changes begin.

### Checks

- [x] Create `Phase-8-LGRC9-ImplementationPlan.md`
- [x] Create `Phase-8-LGRC9-ImplementationChecklist.md`
- [x] Create `specs/lgrc-9-v3-spec.md`
- [x] Link the Phase 8 plan and checklist from `ImplementationPhases.md`
- [x] Record that Phase 8 is the `LGRC-9` family phase
- [x] Record that `LGRC9V3` annotation/timing evidence is the first executable
      target
- [x] Record that pure `LGRC9` remains the substrate interpretation, not the
      first standalone runtime target
- [x] Record that general LGRC and LGRC-V3 / executable LGRCV3 are future
      derivable families, not Phase 8 deliverables
- [x] Record that LGRC-0 annotation is the first target
- [x] Record that LGRC-1 is semi-causal unless causal availability buffers
      exist
- [x] Record that LGRC-2 packet queues and LGRC-3 topology-changing causal
      history are outside the first slice and retained as later Phase 8
      continuation scopes
- [x] Record that no GRCL/LGRC naming cleanup is part of this phase

### Implementation Notes

- Iteration 0 is documentation-only.
- No runtime code is changed in Iteration 0.
- The semantic source is `papers/2026-05-LGRC-9.md`.
- The executable target contract is `specs/lgrc-9-v3-spec.md`.

### Verification

- [x] Phase 8 docs exist under `implementation/`
- [x] Phase 8 is listed as a core phase in `ImplementationPhases.md`
- [x] Applications/IDE work is listed separately from core Phase 8

### Summary

Planning bootstrap is complete when the plan/checklist exist and the global
phase document points to them.

## Iteration 1. Timing Schema And Config Contract

### Goal

Define the core timing vocabulary and config surface before adding derived or
runtime behavior.

### Checks

- [x] Define serialized names for scheduler event index `kappa`
- [x] Define serialized names for checkpoint/snapshot index `k`
- [x] Define serialized names for event-time key `T_e`
- [x] Define serialized names for node-local proper time `tau_i`
- [x] Define serialized names for edge causal delay `tau_ij`
- [x] Define `lapse_policy`
- [x] Define `edge_delay_policy`
- [x] Define whether policies live in model params, artifact config, or both
- [x] Reject ambiguous timing configs
- [x] Document that `step_index` from synchronous GRC is not automatically
      equal to `kappa`, `k`, `T_e`, or `tau_i`

### Implementation Notes

- Added `src/pygrc/models/lgrc_9_v3.py` as a contract-only module.
- The module defines stable serialized timing names, paper/runtime naming
  constants, default causal-history modes, and
  `validate_lgrc9v3_causal_modes(...)`.
- Causal-history policy values live in
  `constitutive_semantic_modes["causal_history"]` for model params.
  Artifacts/checkpoints should copy the resolved values into a same-named
  `causal_history` evidence block.
- Iteration 1 does not add a concrete `LGRC9V3` model class and does not change
  `GRC9V3` defaults or runtime behavior.

### Verification

- [x] Timing schema review passes against `papers/2026-05-LGRC-9.md`
- [x] Serialization names are stable and deterministic
- [x] Existing `GRC9`/`GRC9V3` snapshots remain backward-compatible

### Summary

Iteration 1 complete.

Added the LGRC9V3 timing/config contract without changing synchronous runtime
behavior. Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_state`

## Iteration 2. Lapse, Edge Delay, And Distance Helpers

### Goal

Implement or stage pure helper functions for LGRC-0 annotation.

### Checks

- [x] Add bounded density/tension lapse helper or record why it remains
      documentation-only
- [x] Add geometry-only edge-delay helper
- [x] Add GRC-V3-style flux-dependent edge-delay helper or record it as a
      comparison policy
- [x] Keep symmetric delay as the default
- [x] Reject or defer directed delay unless explicitly configured
- [x] Add geometric distance helper if a reusable one is needed
- [x] Add causal/proper-time distance helper
- [x] Add functional/coupling distance helper or adapter
- [x] Ensure helpers are deterministic and side-effect-free

### Implementation Notes

- Extended `src/pygrc/models/lgrc_9_v3.py` with pure helpers for:
  - unit and bounded density/tension lapse;
  - constant, geometry-baseline, and GRCV3 temporal-label edge causal delay;
  - geometric edge costs and shortest-path distances;
  - causal/proper-time edge costs and shortest-path distances;
  - functional/coupling edge costs and shortest-path distances.
- Directed delay is not implemented as a policy. Passing `directed_delay`
  fails clearly.
- Helpers return derived maps and do not mutate `GRC9V3State`.
- Post-review coverage includes empty-state and single-node behavior.
- LGRC-0 shortest-path helpers are documented as undirected/symmetric
  annotation helpers; directed future/past cones remain future causal-runtime
  work.

### Verification

- [x] Unit tests cover bounded lapse behavior
- [x] Unit tests cover constant-delay specialization
- [x] Unit tests cover nonnegative causal distances
- [x] Unit tests prove the three distance helpers are not conflated

### Summary

Iteration 2 complete.

Added deterministic, side-effect-free LGRC9V3 helper functions for lapse,
edge-delay, and three-distance surfaces. Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_state`

## Iteration 3. LGRC-0 Causal Annotation Surface

### Goal

Expose annotation-only causal-history surfaces over existing synchronous
runtime evidence.

### Checks

- [x] Add LGRC-0 annotation entry point
- [x] Compute `tau_i` annotations without mutating model state
- [x] Compute `tau_ij` annotations without mutating model state
- [x] Compute event-time keys for annotated events
- [x] Add causal/proper-time path summaries
- [x] Add causal cone overlays where enough state exists
- [x] Mark causal basin-core evidence as derived/annotation-only
- [x] Ensure annotation does not alter event counts, topology, budget, or
      observables

### Verification

- [x] LGRC-0 annotation round-trips through JSON artifacts
- [x] Existing synchronous run outputs are unchanged before/after annotation
- [x] Annotation-only fields are labelled as derived evidence

### Summary

Iteration 3 complete.

Added `LGRC9V3CausalAnnotation` and
`annotate_lgrc9v3_causal_history(...)` as an LGRC-0 derived overlay over an
existing synchronous `GRC9V3State`. The annotation computes node proper-time
labels, edge causal delays, event-time records, geometric/causal/functional
path summaries, causal cone overlays, and derived causal basin-core evidence.

The entry point is annotation-only: it does not mutate topology, event logs,
observables, edge labels, budget state, or synchronous runtime behavior.
Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_v3_state`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.core.test_module_imports`

## Iteration 4. Evidence And Replay Surfaces

### Goal

Make LGRC-0 timing annotations auditable in core artifacts without opening a
full downstream telemetry or visualization phase.

### Checks

- [x] Add event timing fields only where LGRC-0 annotation is enabled
- [x] Add node timing fields only where LGRC-0 annotation is enabled
- [x] Add edge delay fields only where LGRC-0 annotation is enabled
- [x] Preserve old artifact readers for non-LGRC runs
- [x] Record `lapse_policy` and `edge_delay_policy`
- [x] Record annotation mode/version
- [x] Ensure replay can distinguish synchronous `step_index` from LGRC timing
      fields

### Verification

- [x] Old GRC9/GRC9V3 artifacts still load
- [x] LGRC-0 artifacts JSON round-trip
- [x] Missing LGRC fields do not break existing consumers

### Summary

Iteration 4 complete.

Added core artifact/replay helpers for LGRC-0 causal-history evidence:

- `build_lgrc9v3_causal_history_artifact(...)`;
- `attach_lgrc9v3_causal_history_artifact(...)`;
- `extract_lgrc9v3_causal_history_artifact(...)`;
- `restore_lgrc9v3_causal_annotation_artifact(...)`.

LGRC-0 event timing fields, node proper-time fields, and edge delay fields are
serialized only inside the optional `causal_history` block. The block records
artifact kind/schema version, annotation mode version, runtime family, derived
evidence class, and the resolved lapse/edge-delay policies.

Missing `causal_history` is treated as non-LGRC evidence and restores as
`None`; existing snapshot readers continue to accept old GRC/GRC9V3 artifacts.
Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract`

## Iteration 5. LGRC-1 Fixed-Topology Eligibility

### Goal

If promoted, implement an opt-in fixed-topology semi-causal eligibility mode.

### Checks

- [x] Add explicit mode/config for LGRC-1 eligibility
- [x] Keep mode disabled by default
- [x] Require fixed topology
- [x] Reject mechanical expansion, collapse, and topology-changing identity
      claims in LGRC-1
- [x] Define virtual advancement for nodes with no currently processed event
- [x] Define elapsed proper time since last local update:
      `delta_tau_i = tau_i - tau_i_last_update`
- [x] Preserve budget checks under the selected update order
- [x] Serialize that the mode is semi-causal unless causal availability buffers
      exist

### Verification

- [x] Default synchronous behavior unchanged
- [x] LGRC-1 mode is opt-in
- [x] Fixed-topology eligibility tests pass
- [x] Budget preservation tests pass
- [x] Artifacts label the run as semi-causal where appropriate

### Summary

Iteration 5 complete.

Added `LGRC9V3FixedTopologyEligibility` and
`compute_lgrc9v3_fixed_topology_eligibility(...)` as the first opt-in LGRC-1
surface. It computes fixed-topology, semi-causal eligibility evidence:

- node proper time at an event-time frontier;
- `delta_tau_i = tau_i - tau_i_last_update`;
- eligible/ineligible node ids under `min_delta_tau`;
- virtual proper-time advancement for all live nodes;
- next last-update proper-time values for explicitly processed nodes;
- fixed topology signature;
- budget before/after/error evidence.
- explicit rejection of mechanical expansion, collapse, identity acceptance,
  and packetized-flux claims in LGRC-1 v1.

This is not full LGRC propagation. It does not move coherence, schedule
packets, apply mechanical expansion, emit identity acceptance, or change the
underlying `GRC9V3State`. Artifacts are labelled
`fixed_topology_semicausal`, `semi_causal=true`,
`causal_availability_buffers=false`, and `packetized_flux=false`.

Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract`

## Iteration 6. Synchronous Limit And No-Regression

### Goal

Prove that the Phase 8 surfaces do not corrupt the existing synchronous
families and that the documented synchronous limit is testable.

### Checks

- [x] Uniform lapse test
- [x] Constant-delay test
- [x] Synchronous eligibility test
- [x] No in-flight retention test
- [x] Existing `GRC9` default behavior unchanged
- [x] Existing `GRC9V3` default behavior unchanged
- [x] Lane A/Lane B `GRC9V3` spark evidence remains unchanged when LGRC modes
      are disabled
- [x] LGRC-0 annotation produces no topology mutation
- [x] LGRC-0 annotation produces no event-count mutation

### Verification

- [x] Relevant GRC9 tests pass
- [x] Relevant GRC9V3 tests pass
- [x] LGRC synchronous-limit fixture passes

### Summary

Iteration 6 complete.

Added explicit synchronous-limit/no-regression contract tests. The fixture uses:

- `lapse_policy = "unit"`;
- `edge_delay_policy = "constant_delay"`;
- `event_time_policy = "synchronous_limit"`;
- explicit `event_time_scale` mapping from synchronous `step_index` to
  compatibility event-time evidence.

The tests prove that LGRC-0 annotation and LGRC-1 fixed-topology eligibility
can reduce to the documented synchronous-limit surface without mutating event
counts, topology, or `GRC9V3` spark evidence. The LGRC-1 fixture also confirms
that no in-flight packet or pending-flux ledger is retained or claimed.

Post-review tightening:

- constant-delay reduction is covered by a standalone named test separate from
  the uniform-lapse test;
- Lane A signed-Hessian candidate evidence and Lane B direct column-H candidate
  evidence are checked in separate fixtures while LGRC helpers remain external
  and LGRC modes are disabled.

This remains a compatibility/no-regression proof, not proof of full
event-driven LGRC dynamics.

Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract`

Regression verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract tests.models.test_grc_9_state tests.models.test_grc_9_step tests.models.test_grc_9_runtime tests.models.test_grc_9_sparks tests.models.test_grc_9_v3_state tests.models.test_grc_9_v3_step tests.models.test_grc_9_v3_sparks tests.models.test_grc_9_v3_column_h_assisted tests.models.test_grc_9_v3_hessian_readiness tests.core.test_module_imports tests.core.test_serialization_contract`

## Iteration 7. Docs, Examples, And Handoff

### Goal

Close the first Phase 8 implementation slice with user-facing guidance and a
clear handoff.

### Checks

- [x] Update `docs/reference/` with LGRC-9 timing terminology if runtime
      surfaces exist
- [x] Add or update examples only after the API shape is stable
- [x] Record what is annotation-only
- [x] Record what is semi-causal behavior
- [x] Record what remains outside the completed LGRC-0/LGRC-1 slice and
      continues in LGRC-2/LGRC-3 iterations
- [x] Add Phase 8 handoff or closeout artifact

### Verification

- [x] Docs do not imply general LGRC, LGRC-V3, or executable LGRCV3
      implementation
- [x] Docs do not imply packetized causal conservation unless LGRC-2 exists
- [x] Docs do not imply topology-changing causal identity unless LGRC-3 exists

### Summary

Iteration 7 complete.

Added the `LGRC9V3` causal-history reference guide, runnable LGRC9V3 examples,
and a Phase 8 handoff. The docs record the current scope as LGRC-0 derived
annotation plus LGRC-1 fixed-topology semi-causal eligibility over `GRC9V3`
state. They also record that packetized causal flux, in-flight coherence
conservation, causally scheduled sparks, topology-changing causal history,
proper-time identity acceptance, general LGRC, executable `LGRC9`, and
executable `LGRCV3` remain outside the completed LGRC-0/LGRC-1 slice and are
tracked through explicit continuation scopes.

## Continuation From Completed LGRC-0/LGRC-1 Slice

These are explicitly not part of the completed first Phase 8 slice:

- LGRC-2 event queue and packetized in-flight coherence accounting;
- compact pending-flux ledgers;
- packet transport through refinement;
- topology-changing causal history;
- causal collapse/reabsorption;
- proper-time identity acceptance;
- directed delay as a default policy;
- general LGRC, LGRC-V3, or executable LGRCV3 family implementation.

LGRC-2 and LGRC-3 are continuation scopes within Phase 8. LGRC-2 is
implemented progressively in the later iterations below, with pending-flux
ledger compaction closed in Iteration 12. LGRC-3 remains the planned
topology-changing continuation. Iteration 15 defines default-disabled
collapse/reabsorption and proper-time identity policy contracts; active
execution for those surfaces remains optional unless explicitly promoted later.
General-family work, directed-delay defaults, algebraic Lorentzian metric work,
and landscape-general validation remain longer-range items at the end of this
checklist.

The Phase 8 continuation opened by N04 Iteration 19-D is now closed:

- [`Phase-8-LGRC9-TopologyStateReabsorptionPlan.md`](./Phase-8-LGRC9-TopologyStateReabsorptionPlan.md)
- [`Phase-8-LGRC9-TopologyStateReabsorptionChecklist.md`](./Phase-8-LGRC9-TopologyStateReabsorptionChecklist.md)
- [`Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md`](./Phase-8-LGRC9-TopologyStateReabsorptionCloseout.md)

That continuation ran Iterations 66-72 and added native topology-state
reabsorption: committed topology events can rebase active node/edge state and
packet-ledger accounting together before post-topology packet work is
scheduled from lineage-current state. It is runtime support only; movement,
topology-mutating movement, choice, agency, and identity-acceptance claims
remain blocked until N04 reruns the movement ladder.

The Phase 8 continuation opened by N04 Iteration 20 is now closed:

- [`Phase-8-LGRC9-TimeScopedLineageReplayPlan.md`](./Phase-8-LGRC9-TimeScopedLineageReplayPlan.md)
- [`Phase-8-LGRC9-TimeScopedLineageReplayChecklist.md`](./Phase-8-LGRC9-TimeScopedLineageReplayChecklist.md)
- [`Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md`](./Phase-8-LGRC9-TimeScopedLineageReplayCloseout.md)

That continuation ran Iterations 73-75 and hardened artifact-only surface
lineage replay: producer stale-read validation is now scoped to the producer's
scheduler time. Later topology transports no longer invalidate historically
valid earlier producer reads, while stale reads at or after transport remain
blocked.

The Phase 8 continuation opened by N04 Iteration 21 is closed:

- [`Phase-8-LGRC9-NativeRouteArbitrationPlan.md`](./Phase-8-LGRC9-NativeRouteArbitrationPlan.md)
- [`Phase-8-LGRC9-NativeRouteArbitrationChecklist.md`](./Phase-8-LGRC9-NativeRouteArbitrationChecklist.md)
- [`Phase-8-LGRC9-NativeRouteArbitrationCloseout.md`](./Phase-8-LGRC9-NativeRouteArbitrationCloseout.md)

That continuation ran Iterations 76-82. LGRC9V3 now supports default-off
native route arbitration: runtime-visible evidence emits candidate route sets,
serialized policy selects one route, the selected topology event references
the arbitration record, and artifact-only replay reconstructs the selected
route chain through surface lineage, topology-state reabsorption, producer
scheduling, and step processing. It is runtime route arbitration only; native
choice, semantic choice, agency, RC identity collapse, identity acceptance,
locomotion-like behavior, biological behavior, and unrestricted movement
claims remain blocked until N04 validators separately rerun and pass.

## Planned Phase 8 Continuation

The completed Iterations 1-7 remain the LGRC-0/LGRC-1 slice. The following
iterations are the planned continuation path for LGRC-2 and LGRC-3. They are
not complete until each section is explicitly executed and verified.

## Iteration 8. LGRC-2 Decision Record And Packet Contract

### Goal

Open LGRC-2 as fixed-topology packetized causal flux without introducing
topology-changing behavior.

### Checks

- [x] Record LGRC-2 as packetized causal flux on fixed topology
- [x] Define event queue key and deterministic tie-breaking
- [x] Define packet schema
- [x] Define packet lifecycle states
- [x] Define departure event payload
- [x] Define arrival event payload
- [x] Define in-flight packet budget invariant:
      `B = sum_i C_i + sum_p C_p`
- [x] Define packet ledger / pending-flux representation
- [x] Define replay and JSON round-trip schema
- [x] Define how packet arrival can expose local update or spark-diagnostic
      eligibility
- [x] Record that LGRC-2 does not transport packets through topology changes
- [x] Record that LGRC-2 does not implement proper-time identity acceptance

### Verification

- [x] Spec and plan agree on LGRC-2 field names
- [x] Checklist distinguishes LGRC-2 from LGRC-1 semi-causal eligibility
- [x] Checklist distinguishes LGRC-2 from LGRC-3 topology-changing history

### Summary

Iteration 8 complete.

Added the LGRC-2 packetized fixed-topology contract without implementing packet
processing. The contract defines `causal_layer_mode =
"packetized_fixed_topology"`, `lgrc_runtime_level = "lgrc2"`, packet
departure/arrival event kinds, packet lifecycle states, packet and ledger field
names, deterministic event-queue tie-breaking, the in-flight packet budget
invariant, and a JSON-round-trippable packet contract artifact.

The contract remains fixed-topology. It records that topology-changing packet
transport, collapse/reabsorption, and proper-time identity acceptance are not
LGRC-2 behavior.

## Iteration 9. LGRC-2 Packet State And Ledger Surface

### Goal

Implement the fixed-topology packet state and ledger surface.

### Checks

- [x] Add packet value object or record type
- [x] Add packet ledger value object or record type
- [x] Add queue event value object or record type
- [x] Add deterministic packet ids
- [x] Add deterministic event ids
- [x] Serialize packet source/target, amount, departure key, arrival key, and
      edge id
- [x] Keep packet ledger separate from synchronous `GRC9V3State` mutation
      unless an explicit LGRC-2 state object is introduced
- [x] JSON round-trip packet and ledger artifacts

### Verification

- [x] Empty ledger round-trips
- [x] Single packet round-trips
- [x] Multiple packets on one edge preserve deterministic order
- [x] Packet ids are stable under deterministic fixture construction

### Summary

Iteration 9 complete.

Added passive LGRC-2 packet surfaces:

- `LGRC9V3PacketRecord`;
- `LGRC9V3PacketQueueEventRecord`;
- `LGRC9V3PacketLedger`;
- deterministic packet and packet-event id builders;
- packet/queue-event creation helpers;
- packet/queue-event/ledger restore helpers;
- JSON-round-trippable `lgrc9v3_packet_ledger` artifact.

The ledger remains a passive fixed-topology evidence surface. It can account
for node coherence plus in-flight packet totals, but it does not process
departure/arrival transitions and does not mutate `GRC9V3State`.

## Iteration 10. LGRC-2 Departure And Arrival Processing

### Goal

Implement packet departure and arrival processing on fixed topology.

### Checks

- [x] Departure subtracts coherence from source or records an equivalent
      pending debit
- [x] Departure adds in-flight packet amount
- [x] Arrival removes in-flight packet amount
- [x] Arrival adds coherence to target or records an equivalent arrived credit
- [x] Queue processing is deterministic
- [x] Arrival does not mutate topology
- [x] Arrival does not imply spark, expansion, or identity acceptance by itself
- [x] Packet events record `kappa`, `T_e`, source/target node ids, edge id,
      amount, and budget evidence
- [x] Normal packet arrival `T_e` is derived from captured edge delay:
      `departure_event_time_key + edge_causal_delay[edge_id]`
- [x] Explicit arrival keys remain allowed for replay/fixture construction
- [x] Record that arrival `T_e` is not source or target node proper time

### Verification

- [x] Departure budget audit passes
- [x] Arrival budget audit passes
- [x] Multi-packet ordering is deterministic
- [x] Fixed-topology assertion rejects topology drift

### Summary

Iteration 10 complete.

Added active fixed-topology LGRC-2 packet processing:

- `process_lgrc9v3_packet_departure(...)`;
- `process_lgrc9v3_packet_arrival(...)`;
- `process_lgrc9v3_next_packet_event(...)`;
- `derive_lgrc9v3_packet_arrival_event_time_key(...)`;
- `LGRC9V3PacketProcessingResult`.

Departure debits source coherence and adds the same amount to in-flight packet
evidence. Arrival removes the in-flight amount and credits the target node.
Both transitions record `scheduler_event_index`, `event_time_key`,
source/target node ids, edge id, packet amount, and budget before/after/error
evidence under `B = sum_i C_i + sum_p C_p`.

Arrival `event_time_key` is a `T_e` queue-ordering key. The normal LGRC-2 path
derives it from the edge-delay surface captured for packet scheduling or
departure:

```text
arrival_event_time_key = departure_event_time_key + edge_causal_delay[edge_id]
```

It is not node-local proper time. Explicit arrival keys are still permitted
for replay and fixture construction.

The processing surface remains fixed-topology. It mutates node coherence and
packet lifecycle evidence only; it does not mutate topology, schedule sparks,
apply mechanical expansion, emit identity acceptance, collapse basins, or
transport packets through topology changes.

Focused verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract`

## Iteration 11. LGRC-2 Acceptance And Handoff

### Goal

Close LGRC-2 with conservation, replay, and no-regression evidence.

### Checks

- [x] Prove `B = sum_i C_i + sum_p C_p` across departure/arrival cycles
- [x] Prove synchronous `GRC9V3` defaults are unchanged
- [x] Prove Lane A/Lane B spark evidence is unchanged unless LGRC-2 explicitly
      feeds a diagnostic eligibility path
- [x] Prove packet ledger JSON round-trip
- [x] Add LGRC-2 docs/reference update
- [x] Add LGRC-2 example or smoke script
- [x] Add LGRC-2 handoff

### Verification

- [x] Focused LGRC-2 tests pass
- [x] GRC9/GRC9V3 no-regression tests pass
- [x] Docs do not imply LGRC-3 topology-changing causal history

### Summary

Iteration 11 complete.

Closed the LGRC-2 acceptance pass for fixed-topology packetized causal flux.
The current accepted shape is:

```text
GRC9V3State + LGRC9V3PacketLedger + processing helpers
```

not a concrete `LGRC9V3` model class.

Added acceptance coverage showing that a departure/arrival cycle preserves:

```text
B = sum_i C_i + sum_p C_p
```

and that packet ledgers JSON round-trip after both departure and arrival.
Existing synchronous `GRC9V3` defaults remain unchanged, and Lane A/Lane B
spark evidence remains isolated unless LGRC surfaces explicitly feed diagnostic
eligibility.

Post-gap tightening:

- `scheduled` packet state is operationalized by
  `schedule_lgrc9v3_packet_departure(...)`;
- queued departure processing transitions `scheduled -> in_flight`;
- packet arrival can emit explicit local-update / spark-diagnostic eligibility
  evidence through `derive_lgrc9v3_packet_arrival_eligibility(...)`;
- arrival eligibility evidence does not run a spark predicate and does not emit
  expansion or identity acceptance.

Added the runnable smoke script:

```text
examples/lgrc9v3/packetized_causal_flux.py
```

and updated the spec, reference guide, examples README, and handoff to record
that LGRC-2 packet processing mutates node coherence through helpers while the
packet ledger/event queue remain external evidence objects. LGRC-3 topology
history, packet transport through refinement, causally scheduled spark
evaluation, and proper-time identity remain out of scope.

## Iteration 12. LGRC-2 Pending-Flux Ledger Compaction

### Goal

Close the packet-ledger representation before topology-changing LGRC-3 work
starts.

### Checks

- [x] Decide whether fixed-topology LGRC-2 packets remain per-packet or compact
      into pending-flux entries
- [x] Define compaction aggregation keys
- [x] Preserve edge id or directed channel id
- [x] Preserve arrival key or arrival window
- [x] Preserve source/target lineage where topology changes may occur later
- [x] Preserve packet amount totals
- [x] Define compact ledger JSON schema
- [x] Define expanded-packet to compact-ledger budget equivalence
- [x] Define how compact entries can be transported through LGRC-3 refinement
      maps
- [x] Record that compaction cannot discard lineage needed for LGRC-3 audit

### Verification

- [x] Expanded packet ledger and compact ledger have equal budget totals
- [x] Compact ledger round-trips through JSON
- [x] Compact ledger keeps enough lineage for refinement transport tests
- [x] LGRC-3 decision record is blocked until this gate is complete

### Summary

Iteration 12 complete.

Closed the pending-flux ledger compaction gate. The decision is:

```text
canonical LGRC-2 packet ledger:
    remains per-packet

compact pending-flux ledger:
    derived budget-equivalent artifact over in-flight packets
```

Added:

- `LGRC9V3PendingFluxEntry`;
- `LGRC9V3PendingFluxLedger`;
- `build_lgrc9v3_pending_flux_entry_id(...)`;
- `compact_lgrc9v3_packet_ledger(...)`;
- `restore_lgrc9v3_pending_flux_ledger_artifact(...)`.

Compaction groups packets only by exact directed channel, arrival key, and
source/target lineage:

```text
source_node_id
target_node_id
edge_id
arrival_event_time_key
source_lineage_id
target_lineage_id
```

Each entry preserves packet ids, departure keys, total amount, and lineage
fields. The compact ledger proves:

```text
pending_flux_total == in_flight_packet_total
conserved_budget_total == node_coherence_total + pending_flux_total
```

The compact ledger is marked `transport_ready_for_refinement = true`, but it
does not transport packets through topology changes. LGRC-3 remains blocked
from topology-changing packet transport until it defines refinement lineage map
semantics over these preserved fields.

## Iteration 13. LGRC-3 Decision Record And Topology Contract

### Goal

Open LGRC-3 as topology-changing causal history after LGRC-2 packet accounting
and pending-flux ledger compaction are stable.

### Checks

- [x] Record that LGRC-3 builds on LGRC-2 packet accounting
- [x] Record that LGRC-3 builds on the completed pending-flux ledger
      compaction gate
- [x] Define topology-changing event kinds in scope
- [x] Define refinement lineage map contract
- [x] Define packet transport through refinement lineage
- [x] Define proper-time inheritance policy for new nodes and internal edges
- [x] Define whether collapse/reabsorption is in scope for this LGRC-3 slice
- [x] Define whether proper-time identity persistence is in scope for this
      LGRC-3 slice
- [x] Preserve distinction:
      candidate event != mechanical expansion != identity acceptance
- [x] Preserve distinction:
      packet transport != semantic identity transfer

### Verification

- [x] Spec and plan agree on LGRC-3 topology fields
- [x] LGRC-3 checklist depends on completed LGRC-2 budget evidence
- [x] Docs do not reinterpret LGRC-0/LGRC-1/LGRC-2 results

### Summary

Iteration 13 complete.

Opened LGRC-3 with a contract artifact only:

```text
artifact_kind = "lgrc9v3_topology_contract"
artifact_schema_version = "lgrc9v3_topology_contract_v1"
mode_version = "lgrc3_topology_contract_v1"
evidence_class = "topology_contract"
contract_only = true
topology_change_processing_implemented = false
packet_transport_through_topology_change_implemented = false
```

The contract records that LGRC-3 builds on:

```text
LGRC-2 packet accounting
LGRC-2 pending-flux compaction
```

In-scope event kinds for the first LGRC-3 slice:

```text
lgrc9v3_refinement_topology_event
lgrc9v3_refinement_packet_transport
lgrc9v3_proper_time_inheritance
lgrc9v3_causal_boundary_birth
```

Out of scope for this slice:

```text
lgrc9v3_causal_collapse
lgrc9v3_causal_reabsorption
lgrc9v3_proper_time_identity_acceptance
```

Proper-time inheritance policy is `uniform_parent_proper_time`; internal edge
delay policy is `explicit_or_default_tau0`.

This iteration does not mutate topology or transport packets. It defines the
field contract that Iteration 14 must satisfy.

## Iteration 14. LGRC-3 Refinement Packet Transport

### Goal

Transport in-flight packets through mechanical expansion without losing budget
or lineage evidence.

### Checks

- [x] Capture pre-expansion packet ledger
- [x] Capture GRC9V3 reassignment map
- [x] Map packets involving expanded node through refinement lineage
- [x] Record source/target lineage before and after refinement
- [x] Preserve packet amounts
- [x] Preserve budget before/after/error
- [x] Preserve old parent port / new endpoint column evidence where applicable
- [x] Do not emit identity acceptance from packet transport alone

### Verification

- [x] Packet transport through one refinement preserves budget
- [x] Packet transport through multiple packets preserves deterministic order
- [x] Candidate/expansion/packet events are linkable without conflation

### Summary

Iteration 14 complete.

Added `transport_lgrc9v3_packets_through_refinement(...)` as the first narrow
LGRC-3 processing helper.

The helper consumes:

```text
pre-expansion LGRC-2 packet ledger
GRC9V3 hybrid_mechanical_expansion event
post-expansion topology signature
optional compact pending-flux ledger
```

It emits:

```text
artifact_kind = "lgrc9v3_refinement_packet_transport_result"
artifact_schema_version = "lgrc9v3_refinement_packet_transport_result_v1"
evidence_class = "refinement_packet_transport"
```

For every in-flight packet, the helper records a transport row. Packets whose
source or target was the expanded node are mapped through the GRC9V3 expansion
`reassignment_map`; unaffected packets remain unchanged but still participate
in deterministic transport evidence.

Transport preserves packet ids, packet amounts, pending-flux entry ids where a
compact ledger is provided, and the budget invariant:

```text
B = sum_i C_i + sum_p C_p
```

For transported boundary packets, records include:

```text
old_parent_port
new_endpoint_port
old_parent_column
new_endpoint_column
```

The helper updates future queued arrival records to point at the transported
endpoint. Past packet event records remain historical evidence.

Packet transport is not semantic identity transfer:

```text
identity_acceptance_emitted = false
packet_transport_identity_transfer = false
```

## Iteration 15. LGRC-3 Collapse, Reabsorption, And Identity Policy

### Goal

If promoted, add causal collapse/reabsorption and proper-time identity policy.

### Checks

- [x] Define collapse/reabsorption event payloads
- [x] Define budget transfer fields
- [x] Define lineage transfer fields
- [x] Define proper-time transfer policy
- [x] Choose identity clock policy:
      sink-local, lineage, basin aggregate, or causal frontier
- [x] Define proper-time persistence threshold calibration
- [x] Keep mechanical expansion separate from identity acceptance

### Verification

- [x] Collapse/reabsorption disabled by default
- [x] Proper-time identity disabled by default unless explicitly scoped
- [x] Budget and lineage fields round-trip

### Summary

Iteration 15 complete.

Added `build_lgrc9v3_lgrc3_policy_contract_artifact(...)` and
`restore_lgrc9v3_lgrc3_policy_contract_artifact(...)` as the default-disabled
LGRC-3 collapse/identity policy contract.

The artifact is:

```text
artifact_kind = "lgrc9v3_collapse_identity_policy_contract"
artifact_schema_version = "lgrc9v3_collapse_identity_policy_contract_v1"
evidence_class = "collapse_identity_policy_contract"
contract_only = true
```

It defines collapse/reabsorption payload fields later consumed by active
processors for:

```text
causal timing
competing / selected / losing sinks
lineage_transfer_map
transferred nodes / packets / pending-flux entries
coherence_transfer_amount
budget_before / budget_after / budget_error
budget_transfer_policy
lineage_transfer_policy
proper_time_transfer_policy
identity_acceptance_emitted
```

The first-round transfer policies are:

```text
budget_transfer_policy = "budget_conserving_transfer"
lineage_transfer_policy = "explicit_lineage_transfer_map"
proper_time_transfer_policy = "selected_sink_clock_continuity"
```

It defines proper-time identity payload fields later consumed by active
processors for:

```text
source_topology_event_ids
sink_node_id
lineage_id
basin_node_ids
identity_clock_policy
threshold_calibration_policy
proper_time_persistence_threshold
threshold_multiplier
window_start_event_time_key
window_end_event_time_key
observed_persistence_duration
budget_before / budget_after / budget_error
identity_acceptance_allowed
identity_acceptance_emitted
```

The first-round identity policy is:

```text
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
threshold_multiplier = 4.0
```

The default contract keeps:

```text
collapse_reabsorption_allowed = false
identity_acceptance_allowed = false
collapse_reabsorption_processing_implemented = false
proper_time_identity_processing_implemented = false
mechanical_expansion_is_identity_acceptance = false
refinement_packet_transport_is_identity_transfer = false
```

## Iteration 16. LGRC-3 Current-Slice Acceptance And Handoff

### Goal

Close the currently implemented LGRC-3 slice with topology-contract evidence,
refinement packet transport, default-disabled collapse/identity policy
contracts, and clear boundaries.

### Checks

- [x] Prove packet budget is preserved through topology changes
- [x] Prove lineage evidence is auditable after refinement
- [x] Prove no identity acceptance is emitted unless identity policy is enabled
- [x] Prove synchronous `GRC9V3` defaults remain unchanged
- [x] Add LGRC-3 docs/reference update
- [x] Add LGRC-3 example or smoke script if API is stable
- [x] Add LGRC-3 handoff

### Verification

- [x] Focused LGRC-3 tests pass
- [x] LGRC-2 no-regression tests pass
- [x] GRC9/GRC9V3 no-regression tests pass
- [x] Docs distinguish LGRC-2 packet transport from LGRC-3 topology history

### Summary

Iteration 16 complete.

Closed the current LGRC-3 slice with acceptance evidence and handoff updates.
This closeout covers:

```text
LGRC-3 topology contract
refinement packet transport through one GRC9V3 mechanical expansion
default-disabled collapse/identity policy contract
active LGRC-3 helper/evidence iterations
planned executable LGRC9V3 parity iterations
```

Added `examples/lgrc9v3/refinement_packet_transport.py` as the current LGRC-3
smoke path. It creates one in-flight LGRC-2 packet, triggers a GRC9V3 Lane B
mechanical expansion, transports packet endpoint/lineage evidence through the
refinement, and prints budget/lineage evidence.

The current closeout does not claim:

```text
full LGRC9V3 model loop
causally scheduled Lane A/Lane B spark predicates
active proper-time inheritance processing
active collapse/reabsorption processing
proper-time identity acceptance
telemetry/visual parity for active LGRC events
```

## Active LGRC-3 Helper/Evidence Iterations

These iterations are the direct helper/evidence continuation of the LGRC-3
contracts. They are not long-range general-family work, and they do not create
a concrete `LGRC9V3` model class.

## Iteration 17. Proper-Time Inheritance Processor

### Goal

Implement active proper-time inheritance evidence for refinement events.

### Checks

- [x] Consume a GRC9V3 `hybrid_mechanical_expansion` event
- [x] Consume parent proper-time surface captured at the refinement event
- [x] Consume replacement-node ids and internal edge ids
- [x] Emit `lgrc9v3_proper_time_inheritance` evidence
- [x] Apply `uniform_parent_proper_time`
- [x] Record internal edge delays using `explicit_or_default_tau0`
- [x] Preserve scheduler/event-time/checkpoint distinction
- [x] Do not emit identity acceptance

### Verification

- [x] Child nodes inherit parent proper time at the event key
- [x] Internal edge delays are explicit or equal to configured `tau_0`
- [x] Artifact round-trips through JSON
- [x] Refinement lineage remains separate from identity persistence

### Summary

Iteration 17 complete.

Added `process_lgrc9v3_proper_time_inheritance(...)` plus typed
`LGRC9V3ProperTimeInheritanceResult` / record surfaces. The helper consumes a
GRC9V3 `hybrid_mechanical_expansion` event and an event-captured parent
proper-time surface, assigns `uniform_parent_proper_time` to replacement nodes,
records explicit-or-`tau_0` internal edge delays, and serializes separate
`scheduler_event_index`, `checkpoint_index`, and `event_time_key` fields.

The processor emits `lgrc9v3_proper_time_inheritance` topology evidence but
does not mutate `GRC9V3State`, emit identity acceptance, or convert refinement
lineage into identity persistence.

## Iteration 18. Collapse/Reabsorption Processor

### Goal

Implement active collapse/reabsorption event evidence with budget and lineage
transfer.

### Checks

- [x] Consume explicit sink-selection/collapse evidence parameters
- [x] Consume packet and pending-flux ledgers where available
- [x] Emit `lgrc9v3_causal_collapse` or `lgrc9v3_causal_reabsorption`
- [x] Record competing, selected, and losing sink ids
- [x] Apply `budget_conserving_transfer`
- [x] Apply `explicit_lineage_transfer_map`
- [x] Apply `selected_sink_clock_continuity`
- [x] Keep identity acceptance separate

### Verification

- [x] Budget before/after/error is audited
- [x] Lineage transfer map is complete for transferred nodes
- [x] Proper-time transfer policy is serialized
- [x] Collapse/reabsorption can be disabled by policy

### Summary

Iteration 18 complete.

Added `process_lgrc9v3_collapse_reabsorption(...)` plus typed
`LGRC9V3CollapseReabsorptionResult` evidence. The helper consumes explicit
sink-selection/collapse evidence, node proper-time surfaces, explicit lineage
transfer maps, and packet/pending-flux ledgers when supplied. It emits either
`lgrc9v3_causal_collapse` or `lgrc9v3_causal_reabsorption` topology evidence
with `budget_conserving_transfer`, `explicit_lineage_transfer_map`, and
`selected_sink_clock_continuity` policy fields.

The processor requires explicit `collapse_reabsorption_allowed=True`, audits
zero budget error, records impacted packet/pending-flux ids without
transporting them, and keeps `identity_acceptance_emitted=false`.

Review note:
    Iteration 18 does not yet consume a single basin/collapse artifact object.
    In the current helper-only architecture, the causal basin/collapse evidence
    is supplied as explicit parameters: competing/selected/losing sinks,
    transferred nodes, lineage maps, node proper time, and budget evidence. A
    future replay/runtime adapter may gather those fields from a richer
    basin-collapse artifact without changing this processor contract.

## Iteration 19. Collapse/Reabsorption Packet Transport

### Goal

Transport packet and compact pending-flux evidence through collapse or
reabsorption lineage maps.

### Checks

- [x] Consume pre-collapse packet ledger
- [x] Consume compact pending-flux ledger
- [x] Consume collapse/reabsorption lineage transfer map
- [x] Redirect or settle in-flight packets according to policy
- [x] Preserve packet ids where packets remain in flight
- [x] Preserve source pending-flux entry links
- [x] Preserve `sum_i C_i + sum_p C_p`

### Verification

- [x] In-flight packet total is conserved or settled into node coherence
- [x] Queue records target the post-collapse endpoint
- [x] Historical packet events remain historical
- [x] JSON replay validates budget and lineage

### Summary

Iteration 19 complete.

Added `transport_lgrc9v3_packets_through_collapse_reabsorption(...)` plus typed
`LGRC9V3CollapsePacketTransportResult` evidence. The helper consumes the
pre-collapse packet ledger, an active collapse/reabsorption result, and an
optional compact pending-flux ledger. It redirects affected in-flight packet
endpoints through the explicit lineage map to the selected sink, preserves
packet ids for packets that remain in flight, settles selected-sink self-loop
packets into the returned ledger's node-coherence total, rewrites queued future
arrival endpoints, and preserves historical packet event records.

The helper keeps budget invariant evidence closed and keeps
`identity_acceptance_emitted=false`.

## Iteration 20. Proper-Time Identity Persistence Evaluator

### Goal

Evaluate identity persistence over sink-local proper time.

### Checks

- [x] Consume topology/lineage event evidence
- [x] Consume basin membership or basin-core evidence
- [x] Consume proper-time surfaces
- [x] Use `sink_local_proper_time`
- [x] Use `local_median_delay_multiplier`
- [x] Compute `proper_time_persistence_threshold`
- [x] Compute observed persistence duration
- [x] Do not emit identity acceptance

### Verification

- [x] Short-lived refinements fail persistence
- [x] Persistent basin evidence passes evaluation
- [x] Threshold calibration is serialized
- [x] Evaluator output round-trips without becoming an event emitter

### Summary

Iteration 20 complete.

Added `evaluate_lgrc9v3_proper_time_identity_persistence(...)` plus typed
`LGRC9V3ProperTimeIdentityPersistenceEvaluation` evidence. The evaluator
consumes topology/lineage ids, basin membership or basin-core ids, and a
proper-time surface. It evaluates sink-local persistence under:

```text
identity_clock_policy = "sink_local_proper_time"
threshold_calibration_policy = "local_median_delay_multiplier"
```

The threshold is:

```text
proper_time_persistence_threshold =
    threshold_multiplier * local_median_edge_delay
```

and the observed duration is the sink-local proper-time window:

```text
window_end_sink_proper_time - window_start_sink_proper_time
```

The evaluator serializes pass/fail evidence, threshold calibration, local
median edge delay, source topology ids, basin evidence id, and budget audit
fields. It remains an evaluator only:

```text
identity_acceptance_allowed = false
identity_acceptance_emitted = false
state_mutated = false
topology_mutated = false
```

Identity acceptance remains Iteration 21.

## Iteration 21. Identity Acceptance Event Emitter

### Goal

Emit identity acceptance only after persistence evaluation passes and policy
explicitly enables identity acceptance.

### Checks

- [x] Require passing persistence evaluator output
- [x] Require `identity_acceptance_allowed = true`
- [x] Emit `lgrc9v3_proper_time_identity_acceptance`
- [x] Link source topology/lineage event ids
- [x] Record budget before/after/error
- [x] Keep mechanical expansion and packet transport separate

### Verification

- [x] Disabled policy prevents emission
- [x] Failed persistence prevents emission
- [x] Passing persistence plus enabled policy emits exactly one event
- [x] Event payload distinguishes identity from refinement and transport

### Summary

Iteration 21 complete.

Added `emit_lgrc9v3_proper_time_identity_acceptance(...)` as the explicit
proper-time identity acceptance event emitter. The emitter consumes a passing
`LGRC9V3ProperTimeIdentityPersistenceEvaluation` and requires:

```text
identity_acceptance_allowed = true
```

It emits exactly one `GRCEvent` with:

```text
kind = "lgrc9v3_proper_time_identity_acceptance"
event_schema_version = "lgrc9v3_proper_time_identity_acceptance_event_v1"
evidence_class = "proper_time_identity_acceptance"
```

The payload links back to:

```text
source_identity_evaluation_id
source_topology_event_ids
source_basin_evidence_id
lineage_id
```

and records budget evidence without changing budget. The payload keeps the
identity boundary explicit:

```text
identity_acceptance_allowed = true
identity_acceptance_emitted = true
mechanical_expansion_emitted = false
packet_transport_emitted = false
mechanical_expansion_is_identity_acceptance = false
refinement_packet_transport_is_identity_transfer = false
state_mutated = false
topology_mutated = false
```

Failed persistence or disabled identity policy prevents emission.

## Iteration 22. LGRC-3 Topology Event Replay Validator

### Goal

Validate LGRC-3 topology-event artifact replay for ordering, budget, and
lineage.

### Checks

- [x] Replay refinement transport artifacts
- [x] Replay proper-time inheritance artifacts
- [x] Replay collapse/reabsorption artifacts
- [x] Replay identity acceptance artifacts
- [x] Validate event-time ordering
- [x] Validate lineage continuity
- [x] Validate budget conservation across event sequence

### Verification

- [x] Replay accepts valid deterministic fixture
- [x] Replay rejects missing lineage
- [x] Replay rejects budget mismatch
- [x] Replay rejects impossible event-time ordering

### Summary

Iteration 22 complete.

Added `validate_lgrc9v3_topology_event_replay(...)` plus typed
`LGRC9V3TopologyReplayRecord` and
`LGRC9V3TopologyReplayValidationResult` evidence. The validator consumes an
ordered replay sequence containing:

```text
lgrc9v3_refinement_packet_transport_result
lgrc9v3_proper_time_inheritance_result
lgrc9v3_collapse_reabsorption_result
lgrc9v3_collapse_reabsorption_packet_transport_result
lgrc9v3_proper_time_identity_persistence_evaluation
lgrc9v3_proper_time_identity_acceptance
```

It validates:

```text
event_time_key is nondecreasing in replay order
source topology ids point to prior topology evidence
identity acceptance points to a prior identity evaluation
lineage ids are present where semantic lineage is required
budget_before matches the previous budget_after across budget-bearing records
end_budget - start_budget == 0
```

The result artifact is:

```text
artifact_kind = "lgrc9v3_topology_event_replay_validation"
artifact_schema_version = "lgrc9v3_topology_event_replay_validation_v1"
evidence_class = "topology_event_replay_validation"
```

The validator is still a replay/audit surface. It does not schedule events,
run an event queue, mutate state, or provide a standalone LGRC9V3 step loop.

## Iteration 23. Active LGRC-3 Examples And Handoff

### Goal

Document active LGRC-3 processing once at least one active runtime processor is
stable.

### Checks

- [x] Add example for proper-time inheritance or collapse processing
- [x] Add example README section distinguishing LGRC-2 and active LGRC-3
- [x] Update handoff with active runtime surface status
- [x] Update reference guide with stable imports

### Verification

- [x] Example runs from repo root
- [x] Example output does not imply full LGRC model loop unless implemented
- [x] Focused active LGRC-3 tests pass

### Summary

Iteration 23 complete.

Added `examples/lgrc9v3/active_lgrc3_causal_history.py`, which composes the
current active LGRC-3 helper/evidence chain:

```text
GRC9V3 Lane B mechanical expansion
+ LGRC-2 packet ledger
+ refinement packet transport
+ proper-time inheritance
+ collapse/reabsorption evidence
+ collapse packet transport
+ proper-time identity evaluation
+ explicit identity acceptance
+ replay validation
```

The examples README now distinguishes LGRC-2 fixed-topology packetized causal
flux from active LGRC-3 topology-changing causal-history helper processors.
The handoff records the active LGRC-3 status and the reference guide lists the
stable active-LGRC-3 imports.

The example and docs preserve the current boundary:

```text
LGRC9V3 Iterations 1-23 are helper/evidence surfaces over GRC9V3State.
Iteration 25 introduces a concrete LGRC9V3 event-queue shell.
That shell owns packet departure/arrival queue processing only.
Lane A/Lane B spark diagnostics are not causally scheduled until Iteration 27.
```

## Planned Executable LGRC9V3 Runtime Parity Iterations

These iterations are the path from causal-history evidence layer to a
standalone executable LGRC9V3 runtime. Iteration 24 accepted the model-class
boundary; Iteration 25 begins the runtime shell without claiming full parity
with synchronous `GRC9V3`.

## Iteration 24. LGRC9V3 Runtime Class Decision

### Goal

Decide whether to introduce a concrete `LGRC9V3` model class or keep LGRC9V3
as helper/evidence surfaces over `GRC9V3State`.

### Checks

- [x] Record whether `LGRC9V3` should subclass/share `GRCModel`
- [x] Record state ownership boundary:
      wrapped `GRC9V3State`, new `LGRC9V3State`, or composed state bundle
- [x] Record how LGRC packet ledger and topology-event ledger are owned
- [x] Record migration path from current helpers
- [x] Record compatibility expectations for existing `GRC9V3` snapshots

### Verification

- [x] Decision record names files to create or confirms no model class yet
- [x] No existing helper API is silently reinterpreted

### Summary

Iteration 24 complete.

Decision:

```text
Introduce a concrete executable `LGRC9V3` model class for Iterations 25+.
```

The class should implement/share the `GRCModel` interface and use composition
over `GRC9V3State`. It should not subclass `GRC9V3`, because synchronous
`GRC9V3.step()` semantics must not be inherited or blurred with event-driven
LGRC scheduling.

Planned files:

```text
src/pygrc/models/lgrc_9_v3_runtime.py
src/pygrc/models/lgrc_9_v3_runtime_state.py
tests/models/test_lgrc_9_v3_runtime.py
```

Runtime state ownership:

```text
base GRC9V3State
+ causal timing fields
+ packet ledger
+ event queue
+ topology-event/replay ledger
+ causal-history modes/policies
+ diagnostic history for later causal spark evaluation
```

Migration path:

```text
GRC9V3State -> explicit LGRC9V3.from_state(...) adapter
```

Existing helper/evidence APIs remain stable. They are not silently
reinterpreted as model-owned state.

Compatibility expectation:

```text
Old GRC9V3 snapshots remain GRC9V3 snapshots.
LGRC9V3 loading requires an explicit causal-state block or an explicit
synchronous-limit adapter policy.
```

## Iteration 25. Event Queue Orchestration Loop

### Goal

Implement the top-level event queue runner if a model class is accepted.

### Checks

- [x] Define scheduler event record ordering
- [x] Process packet departures and arrivals through one queue loop
- [x] Route local update eligibility events
- [x] Route topology events as explicit no-op bookkeeping for this iteration
- [x] Keep `kappa`, `k`, `T_e`, and `tau_i` distinct
- [x] Define stop conditions and checkpoint surfaces

### Verification

- [x] Deterministic event ordering
- [x] No starvation in bounded interleaved packet fixtures
- [x] JSON replay of event queue

### Summary

Iteration 25 complete.

Added `LGRC9V3` as an executable `GRCModel`-compatible runtime shell in
`src/pygrc/models/lgrc_9_v3_runtime.py`, backed by composed
`LGRC9V3RuntimeState` in `src/pygrc/models/lgrc_9_v3_runtime_state.py`.

The runtime owns a deterministic packet event queue and processes exactly one
queued packet departure or arrival per `step()`. Departures and arrivals use
the existing LGRC-2 packet-processing helpers and mutate the composed
`GRC9V3State` node coherence through packet budget accounting, not through
synchronous `GRC9V3.step()`.

Iteration 25 guarantees:

```text
scheduler_event_index / kappa:
    processed packet event order

checkpoint_index / k:
    runtime checkpoint count

event_time_key / T_e:
    event-queue ordering key

node_proper_time / tau_i:
    serialized local proper-time surface, not equal to T_e by default
```

Arrival events emit local-update / spark-diagnostic eligibility evidence, but
they do not run the local update loop, Lane A/Lane B spark predicates,
mechanical expansion, boundary birth, topology integration, or identity
acceptance. Topology routing is present only as explicit no-op bookkeeping
until Iteration 28+.

## Iteration 26. Causal Flux And Local Update Loop

### Goal

Make causal availability and packetized flux the active continuity driver.

### Checks

- [x] Consume arrival eligibility as local update input
- [x] Update node coherence by causal events rather than synchronous slice
- [x] Preserve packet budget invariant
- [x] Preserve lapse/proper-time accumulation policy
- [x] Keep delayed-evaluation and packetized paths separate

### Verification

- [x] Fixed-topology causal flux conserves budget across many events
- [x] Unit-lapse / constant-delay packet fixture exercises the documented
      synchronous-limit timing surface
- [x] Large-delay fixture differs from synchronous update in expected direction

### Summary

Iteration 26 complete.

Arrival events now feed an active packetized local-update surface. On packet
arrival, `LGRC9V3.step()`:

```text
1. credits the target through packet arrival processing;
2. emits arrival eligibility evidence;
3. advances the target's local proper-time surface under the serialized
   proper-time/lapse policy;
4. emits `lgrc9v3_local_update` evidence;
5. schedules any explicit outbound causal-flux packet routes for later
   departure/arrival events.
```

Node coherence continues to change only through packet departure and packet
arrival processing. The delayed-evaluation continuity formula is not applied:

```text
packetized_flux_applied = true
delayed_evaluation_applied = false
local_continuity_formula_applied = false
```

This keeps LGRC-2 packet accounting separate from delayed-evaluation
optimizations and prevents double-counting flux. The local-update route table
is explicit and fixed-topology only; it does not infer or run GRC9V3's
synchronous flux loop.

Additional closure checks:

```text
bounded interleaved queue:
    every initially queued event is processed exactly once;
    derived route events drain within the bounded fixture;
    event_time_key ordering is nondecreasing;
    the queue is empty at completion.

many-event budget audit:
    budget_before == budget_after for each processed packet event;
    budget_error == 0 for each processed packet event;
    sum_i C_i + sum_p C_p remains equal to the initial budget after every step.

synchronous-limit timing surface:
    unit lapse and constant edge delay produce the expected event-time and
    node-proper-time surface for packetized causal flux.
```

This is not a full equivalence test against synchronous `GRC9V3.step()`.
Iteration 31 later adds controlled comparison fixtures after causally scheduled
sparks, topology events, and the broader executable runtime surfaces exist.
Those fixtures remain bounded fixture comparisons, not landscape-general
equivalence proofs.

## Iteration 27. Causally Scheduled Lane A/Lane B Spark Diagnostics

### Goal

Re-derive GRC9V3 Lane A and Lane B spark candidate evaluation under LGRC
causal scheduling. This is the first iteration where LGRC9V3 may claim that
Lane A signed-Hessian or Lane B direct column-H proxy-branch candidates are
produced by causal events rather than by synchronous global slice steps.

### Checks

- [x] Define causal spark diagnostic eligibility triggers:
      packet arrival, local update completion, causal frontier event, or
      explicitly scheduled diagnostic event
- [x] Define the causal snapshot used by spark evaluation:
      event-time key `T_e`, node proper time, pre-expansion topology,
      packet/arrival/local-update state, and captured diagnostic surfaces
- [x] Preserve Lane A `current_hybrid_signed_hessian` predicate semantics under
      causal scheduling
- [x] Preserve Lane B `grc9v3_column_h_assisted` predicate semantics under
      causal scheduling
- [x] Define how signed-Hessian diagnostics are captured at event time
- [x] Define how Column-H diagnostics are single-captured at event time
- [x] Resolve previous Column-H values through causal evaluation history,
      not through raw synchronous `step_index`
- [x] Invalidate previous diagnostics across refinement/collapse lineage
      changes unless lineage transport explicitly preserves them
- [x] Emit lane-tagged causal spark candidate events with branch attribution:
      `signed_hessian_hit`, `column_h_threshold_hit`,
      `column_h_sign_crossing_hit`, `column_h_branch_hit`
- [x] Keep candidate production separate from mechanical expansion,
      packet transport, proper-time inheritance, collapse, and identity
- [x] Record that LGRC9V3 before this iteration may claim only
      spark-diagnostic eligibility, not causally scheduled Lane A/Lane B spark
      predicates

### Verification

- [x] Arrival/local-update event can schedule diagnostic
- [x] First causal evaluation has no invalid previous-H crossing
- [x] Lane A/Lane B branch attribution remains exact
- [x] Lane A default behavior remains signed-Hessian-only unless Lane B is
      explicitly selected
- [x] Lane B column-H-only candidate can fire inside the causal saturation /
      gradient envelope
- [x] Large-gradient column-H hit remains blocked under Lane B v1 envelope
- [x] Predicate evidence, candidate payload, and later expansion routing use
      the same captured diagnostic object
- [x] Causal diagnostic event does not mutate topology by itself
- [x] Synchronous GRC9V3 default remains unchanged

### Summary

Iteration 27 complete.

Added causally scheduled Lane A/Lane B spark diagnostics to executable
`LGRC9V3`. Packet arrivals still emit arrival eligibility and
`lgrc9v3_local_update`; after that local-update boundary, the runtime evaluates
the existing GRC9V3 spark predicate against the causal event snapshot and wraps
any resulting candidate as:

```text
event kind:
    lgrc9v3_causal_spark_candidate

schema:
    lgrc9v3_causal_spark_candidate_event_v1
```

The causal candidate payload preserves the captured GRC9V3 predicate evidence
and adds:

```text
causal_spark_evaluation_index
causal_spark_trigger_kind
causal_spark_trigger_event_id
causal_spark_trigger_source
scheduler_event_index
checkpoint_index
event_time_key
candidate_node_proper_time
node_proper_time_surface
pre_expansion_topology_signature
```

Lane A remains the default `current_hybrid_signed_hessian` predicate. Lane B
remains opt-in as `grc9v3_column_h_assisted`; its direct column-H proxy branch
can now produce a causal candidate inside the active-degree-9 and
small-gradient envelope. Large-gradient column-H hits remain blocked under the
Lane B v1 envelope.

Previous Column-H history is keyed by `causal_spark_evaluation_index` during
LGRC evaluation, not by synchronous `GRC9V3.step_index`. The runtime also
exposes `invalidate_causal_spark_diagnostics(...)` so topology/lineage changes
can clear previous diagnostic history unless an explicit lineage transport
policy preserves it.

Candidate production remains separate from mechanical expansion, packet
transport, collapse/reabsorption, and identity acceptance:

```text
topology_mutated = false
mechanical_expansion_emitted = false
identity_acceptance_emitted = false
packet_transport_emitted = false
```

## Iteration 28-A. Causal Frontier Boundary Birth

### Goal

Implement LGRC9V3's active analogue of GRC9V3 boundary birth as an explicit
causal frontier topology event. This feature must be default-off/overridable,
and when enabled its active birth probability policy must be on par with the
corresponding GRC9V3 boundary-birth probability semantics.

### Checks

- [x] Define event kind:
      `lgrc9v3_causal_boundary_birth` or `lgrc9v3_frontier_birth`
- [x] Define default-off policy:
      `causal_boundary_birth_allowed = false`
- [x] Define override path to enable active causal boundary birth
- [x] Map GRC9V3 boundary-birth probability parameters into the LGRC policy
- [x] Define causal eligibility event:
      frontier event, boundary pressure event, or scheduled birth trial
- [x] Define event-time owner `T_e`
- [x] Define parent/frontier proper-time inheritance for the new node
- [x] Define coherence source:
      zero-coherence birth, parent debit, or frontier reservoir
- [x] Define edge-delay assignment:
      explicit edge delay or configured `tau_0`
- [x] Define packet visibility:
      packets see the new node only after the birth event is processed
- [x] Emit budget, lineage, and topology signature evidence
- [x] Keep boundary birth separate from refinement, collapse, and identity

### Verification

- [x] Default-off policy emits no boundary birth
- [x] Enabled policy matches GRC9V3 boundary-birth probability behavior under
      synchronous-limit conditions
- [x] Birth event preserves budget under the selected coherence-source policy
- [x] New node proper time is inherited from parent/frontier at event time
- [x] New edge delay is serialized
- [x] Event payload round-trips through JSON
- [x] Boundary birth does not emit identity acceptance

### Summary

Iteration 28-A complete.

Added explicit causal frontier boundary birth to the executable `LGRC9V3`
runtime as an opt-in LGRC-3 topology event:

```text
event kind = lgrc9v3_causal_boundary_birth
causal_boundary_birth_allowed = false by default
active policy = grc9v3_outward_flux_probability
coherence source = parent_debit
edge delay policy = explicit_or_tau0
```

The active policy uses the same GRC9V3 boundary-birth probability law:

```text
birth_probability = 1 - exp(-lambda_birth * outward_flux_pressure)
```

When accepted, the event creates a new boundary child at an inactive parent
port, debits parent coherence by `alpha_seed * parent_coherence`, assigns a
new edge delay from explicit `edge_delay` or `tau_0`, and inherits the
parent's proper-time surface at the birth event time. Payloads record budget
before/after/error, parent/child lineage, pre/post topology signatures,
probability evidence, RNG sample, event-time owner `T_e`, and packet visibility
semantics.

Boundary birth remains separate from spark/refinement/collapse/identity:

```text
spark_event_emitted = false
mechanical_expansion_emitted = false
identity_acceptance_emitted = false
```

The current implementation rejects causal boundary birth while packets are
queued or in flight. Iteration 28 may relax this by integrating topology events
directly into the event loop with packet routing across topology changes.

Focused verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract tests.models.test_lgrc_9_v3_runtime
PYTHONPATH=src ./.venv/bin/python -m unittest discover tests
```

## Iteration 28. Active Topology Integration

### Goal

Integrate refinement, packet transport, proper-time inheritance,
causal frontier boundary birth, collapse/reabsorption, and identity events into
the executable event loop.

### Checks

- [x] Route spark candidate to mechanical expansion when policy allows
- [x] Route expansion to packet transport and proper-time inheritance
- [x] Route causal boundary birth when policy allows
- [x] Route collapse/reabsorption when policy allows
- [x] Route identity acceptance only after persistence acceptance
- [x] Preserve event linkage across candidate, expansion, transport,
      inheritance, collapse, and identity events

### Verification

- [x] Candidate-only path does not mutate topology
- [x] Expansion path preserves budget and lineage
- [x] Boundary birth path preserves budget and lineage
- [x] Collapse path preserves budget and lineage
- [x] Identity event appears only when enabled and justified

### Summary

Iteration 28 complete.

Added active topology integration gates to executable `LGRC9V3`.

Default runtime behavior remains candidate-only:

```text
causal_topology_integration_allowed = false
causal_spark_expansion_allowed = false
causal_refinement_packet_transport_allowed = false
causal_proper_time_inheritance_allowed = false
causal_collapse_reabsorption_allowed = false
causal_identity_acceptance_allowed = false
```

When LGRC-3 topology integration is explicitly enabled, arrival/local-update
spark candidates can route to the existing GRC9V3 mechanical expansion helper.
The expansion event is then linked to LGRC-3 refinement packet transport and
proper-time inheritance evidence:

```text
lgrc9v3_causal_spark_candidate
-> hybrid_mechanical_expansion
-> lgrc9v3_refinement_packet_transport
-> lgrc9v3_proper_time_inheritance
```

The runtime now also supports scheduled causal boundary-birth trials in
`LGRC9V3.step()`. Boundary birth remains explicit, opt-in, and probability
compatible with GRC9V3 outward-flux boundary birth.

Collapse/reabsorption and proper-time identity acceptance are exposed through
runtime wrapper APIs that append auditable LGRC topology/identity events only
when their policies are explicitly enabled. Identity acceptance still requires
a passing proper-time persistence evaluation.

Focused verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract tests.models.test_lgrc_9_v3_runtime
PYTHONPATH=src ./.venv/bin/python -m unittest discover tests
```

## Iteration 29. LGRC9V3 Telemetry And Checkpoint Parity

### Goal

Expose active LGRC9V3 runtime events in telemetry and checkpoint artifacts.

### Checks

- [x] Add event rows for LGRC packet, topology, collapse, and identity events
- [x] Add checkpoint overlays for causal clocks, packet ledger, and topology
      history
- [x] Preserve old GRC9V3 telemetry compatibility
- [x] Add schema/version fields

### Verification

- [x] Telemetry JSON round-trips
- [x] Old GRC9V3 runs still load
- [x] LGRC9V3 event rows can distinguish packet, topology, spark, and identity

### Summary

Iteration 29 complete.

Added `src/pygrc/telemetry/lgrc9v3_contract.py` as the LGRC9V3 telemetry
extension surface. The contract classifies active runtime events by causal
domain instead of event kind alone:

```text
packet
local_update
spark
topology
collapse
identity
other
```

It also adds `build_lgrc9v3_graph_checkpoint(...)`, which emits a port-graph
checkpoint with LGRC9V3 overlays for causal clocks, node proper-time surfaces,
edge causal delays, packet ledger state, event queues, local-update logs,
causal spark diagnostics, topology history, and runtime-state snapshot data.

Old GRC9V3 telemetry artifacts remain compatible because LGRC9V3 evidence is
stored only under `family_extensions["lgrc9v3"]`; existing GRC9V3 rows and graph
checkpoints can still serialize and load without that family extension.

Focused verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_lgrc9v3_contract
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_contract tests.models.test_lgrc_9_v3_runtime tests.telemetry.test_lgrc9v3_contract
```

## Iteration 30. LGRC9V3 Visualization Parity

### Goal

Visualize active LGRC9V3 causal-history events without implying synchronous
slice semantics.

### Checks

- [x] Render event-time/proper-time surfaces
- [x] Render packet in-flight/arrival state
- [x] Render topology event lineage
- [x] Render identity persistence windows
- [x] Distinguish LGRC events from GRC9V3 synchronous events

### Verification

- [x] Visual bundle renders from LGRC telemetry
- [x] Lane A/Lane B spark branch labels remain visible where relevant
- [x] No visual surface collapses graph, causal, and functional distance

### Summary

Iteration 30 complete.

Added LGRC9V3 visualization parity over the Iteration 29 telemetry and graph
checkpoint surfaces. Behavior visual bundles now expose causal event-time,
proper-time, packet-ledger, local-update, causal-spark, and topology-event
series through `DEFAULT_LGRC9V3_RUN_OBSERVABLES`. Event timelines classify
LGRC9V3 rows by causal domain:

```text
packet
local_update
spark
topology
collapse
identity
```

Spark rows keep Lane A/Lane B attribution visible, including the distinction
between Lane B signed-Hessian-only candidates and Lane B direct column-H proxy
branch candidates.

LGRC9V3 behavior plots use checkpoint/event-row axis labels instead of plain
`step` labels so the visual surface does not imply synchronous `GRC9V3.step()`
slice semantics.

Graph visual bundles now read LGRC9V3 checkpoint overlays for causal clocks,
node proper-time/lapse fields, edge causal delays, in-flight packet records,
topology lineage edges, and proper-time identity windows. The graph surface
keeps geometric length, temporal/causal delay, and packet/functional evidence
as separate tooltip fields rather than collapsing them into one generic
distance.

Focused verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_visualization
```

## Iteration 31. GRC9V3 vs LGRC9V3 Comparison Fixtures

### Goal

Compare synchronous `GRC9V3` and executable `LGRC9V3` under controlled
fixtures.

### Checks

- [x] Add synchronous-limit comparison fixture
- [x] Add delay-sensitive fixture
- [x] Add packet-transport/refinement fixture
- [x] Add identity-persistence fixture if identity is active
- [x] Compare by proper-time surfaces and event classes, not raw step only

### Verification

- [x] Synchronous-limit comparison matches expected baseline
- [x] Delay-sensitive fixture shows causal-history delta
- [x] Reports state which claims are supported and which remain open

### Summary

Iteration 31 complete.

Added controlled GRC9V3/LGRC9V3 comparison fixtures in
`tests.models.test_lgrc_9_v3_runtime`. The comparison fixtures intentionally
align by:

```text
proper_time_surfaces_and_event_classes
```

not by raw synchronous step count.

The fixtures cover:

- synchronous-limit timing surface:
  unit lapse + constant delay aligns LGRC9V3 event-time/proper-time evidence
  with the GRC9V3 one-step time surface while recording that packetized flux is
  extra LGRC9V3 event evidence;
- delay-sensitive packet routing:
  larger `edge_causal_delay` defers downstream arrival and leaves visible queued
  packet evidence, proving a causal-history delta in a controlled fixture;
- Lane B refinement/topology integration:
  synchronous GRC9V3 Lane B and active LGRC9V3 reach the same refined node
  count while LGRC9V3 adds event-time, packet-transport, and proper-time
  inheritance evidence;
- proper-time identity persistence:
  LGRC9V3 can emit explicit, policy-gated proper-time identity acceptance while
  synchronous GRC9V3 mechanical expansion remains non-identity evidence.

Each fixture builds a small JSON-round-trippable comparison report with:

```text
supported_claims
open_claims
grc9v3_event_counts
lgrc9v3_event_counts
lgrc9v3_node_proper_time
raw_step_count_alignment_used = false
```

The comparison fixtures support controlled runtime-parity claims only. They do
not claim full `GRC9V3.step()` equivalence, landscape-general behavior, general
LGRC, executable LGRC9, or executable LGRCV3.

Focused verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime
```

## Iteration 31-A. Runtime Stress And Determinism Sweep

### Goal

Add bounded stress coverage for the executable `LGRC9V3` runtime before the
examples/handoff closeout. This iteration does not add runtime semantics.

### Checks

- [x] Add deterministic packet queue tie-order stress
- [x] Add multi-event packet budget stress
- [x] Add mixed packet, boundary-birth, and Lane B expansion stress
- [x] Add causal-clock monotonicity checks after mixed events
- [x] Add runtime snapshot JSON round-trip stress
- [x] Add default `GRC9V3` isolation check after an LGRC9V3 run

### Verification

- [x] Queue ordering remains deterministic under tied event-time keys
- [x] Packet departure/arrival ids are processed once
- [x] Conserved budget remains stable across many queued events
- [x] Mixed packet/birth/expansion run drains queues and preserves runtime
      references for non-arrived packets
- [x] Runtime snapshot preserves LGRC9V3 topology and queue surfaces through
      JSON round-trip
- [x] Synchronous `GRC9V3` snapshots remain causal-layer-free

### Summary

Iteration 31-A complete.

Added bounded stress tests in `tests.models.test_lgrc_9_v3_runtime`.

The stress sweep covers:

- deterministic packet queue ordering with tied `event_time_key` values;
- repeated packet departure/arrival processing with stable budget;
- mixed packet departure, causal boundary birth, causal spark candidate,
  mechanical expansion, refinement packet transport, and proper-time
  inheritance in one bounded run;
- causal clock monotonicity after mixed runtime events;
- JSON round-trip of the active runtime snapshot after topology events;
- default `GRC9V3` isolation after an LGRC9V3 run.

The stress sweep is confidence coverage, not a new semantic claim. It does not
prove landscape-general parity or full equivalence with synchronous
`GRC9V3.step()`.

Focused verification:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime
```

## Iteration 32. Executable LGRC9V3 Examples And Handoff

### Goal

Close the executable LGRC9V3 runtime-parity arc with runnable examples,
reference-guide imports, and a handoff that states exactly what Iterations
24-31-A implemented and what remains outside the runtime.

### Checks

- [x] Add executable LGRC9V3 example README section
- [x] Add example for constructing/running executable `LGRC9V3`
- [x] Add example for event-queue / packetized causal-flux run
- [x] Add example for causally scheduled Lane A/Lane B spark diagnostics
- [x] Add example for telemetry and visualization if Iterations 29-30 are
      complete
- [x] Add comparison example or link to Iteration 31 artifacts
- [x] Mention Iteration 31-A stress coverage in the handoff
- [x] Update reference guide with stable executable-runtime imports
- [x] Update handoff with executable runtime surface status
- [x] State whether `LGRC9V3.step()` exists and what it guarantees
- [x] State which parity surfaces remain incomplete

### Verification

- [x] Examples run from repo root
- [x] Example output distinguishes LGRC event-time/proper-time evidence from
      synchronous `GRC9V3.step_index`
- [x] Example output does not imply general LGRC, executable LGRC9, or
      executable LGRCV3 support
- [x] Focused executable LGRC9V3 tests pass
- [x] GRC9V3 no-regression tests pass
- [x] Handoff records supported and unsupported claims

### Summary

Iteration 32 complete.

Added executable LGRC9V3 examples:

- `examples/lgrc9v3/executable_runtime.py`;
- `examples/lgrc9v3/executable_packet_queue.py`;
- `examples/lgrc9v3/causal_spark_diagnostics.py`;
- `examples/lgrc9v3/telemetry_visual_bundle.py`.

Updated the LGRC9V3 README, root examples README, reference guide, plan, and
handoff to state the current executable runtime boundary:

```text
LGRC9V3.step() processes one queued packet event or scheduled causal
boundary-birth trial.

Packet arrivals can advance local proper time, emit local-update evidence, and
evaluate causally scheduled Lane A/Lane B spark diagnostics.

Active topology integration remains opt-in.
LGRC9V3 does not run synchronous GRC9V3.step().
General LGRC, executable LGRC9, and executable LGRCV3 remain out of scope.
```

Iteration 31 comparison fixtures and Iteration 31-A stress fixtures are linked
from the example README as test evidence rather than user-facing scripts.

Focused verification:

```text
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/executable_runtime.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/executable_packet_queue.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/causal_spark_diagnostics.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/telemetry_visual_bundle.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/causal_history_surfaces.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/packetized_causal_flux.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/refinement_packet_transport.py
PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/active_lgrc3_causal_history.py
```

## Post-32 Code Design Correctness Track

Iterations 33-37 are a baseline-preserving design catch-up track. They are not
new LGRC semantics.

Rule:

```text
Freeze behavior first.
Then improve code ownership and usage entry points.
```

The current implementation is the baseline until an iteration explicitly
updates it:

```text
LGRC9V3.step() event ordering and payloads;
LGRC9V3 stress fixtures;
GRC9/GRC9V3 no-regression behavior;
LGRC9V3 telemetry/checkpoint family extensions;
LGRC9V3 visualization interpretation;
corrected cascade comparison reproduction;
legacy pygrc.models.lgrc_9_v3 imports.
```

## Iteration 33. LGRC9V3 Baseline Freeze And Assumption Audit

### Goal

Freeze the accepted post-32 LGRC9V3 implementation as a behavioral baseline
before design cleanup begins.

### Checks

- [x] Record the current `LGRC9V3.step()` contract:
      packet departure,
      packet arrival,
      scheduled causal boundary-birth trial.
- [x] Record the Iteration 33 `LGRC9V3.run_event_queue(max_events=...)`
      contract and known birth-only queue gap.
- [x] Record current event kinds and payload surfaces for packet, local-update,
      causal spark, topology, boundary birth, collapse, and identity events.
- [x] Record the current GRC9V3 substrate dependency:
      reuse `GRC9V3State`, do not call synchronous `GRC9V3.step()` in LGRC
      queue execution.
- [x] Record current stable import surfaces, including legacy
      `pygrc.models.lgrc_9_v3` imports.
- [x] Record current landscape-backed path:
      `LandscapeSeed -> GRCL9V3 source -> GRC9V3State -> LGRC9V3.from_state`.
- [x] Record current native snapshot state:
      `LGRC9V3.snapshot()` exists and `LGRC9V3.load(...)` is deferred.
- [x] Record corrected cascade reproduction command and expected high-level
      output:
      final topology `29 nodes / 28 edges`,
      max packet budget error approximately `2.84e-14`.

### Verification

- [x] Run focused LGRC9V3 runtime tests.
- [x] Run focused LGRC9V3 telemetry tests.
- [x] Run focused visualization tests if visualization contracts are touched.
- [x] Run default GRC9/GRC9V3 no-regression tests used by Phase 8.
- [x] Run executable LGRC9V3 examples from repo root.
- [x] Run or dry-run the corrected cascade reproduction script and record
      whether generated outputs are refreshed.
- [x] Add a short baseline-freeze summary to the Phase 8 handoff.

### Summary

Iteration 33 complete.

Froze the accepted post-32 LGRC9V3 implementation as the baseline for future
code-design cleanup. The Phase 8 handoff now records:

```text
LGRC9V3.step() contract;
LGRC9V3.run_event_queue(...) contract and post-33 birth-only queue gap;
current packet/local-update/spark/topology/identity event surfaces;
GRC9V3State substrate dependency;
stable import paths;
landscape-backed construction path;
native snapshot/load boundary;
corrected cascade reproduction result.
```

Verification completed:

```text
tests.models.test_lgrc_9_v3_runtime
    31 tests passed

tests.telemetry.test_lgrc9v3_contract
    3 tests passed

tests.visualization.test_visualization
    68 tests passed

GRC9/GRC9V3 no-regression subset
    69 tests passed

LGRC9V3 executable examples
    all listed examples passed

examples/lgrc9v3/corrected_cascade_comparison.py
    regenerated ignored outputs
    GRC9V3 final topology = 29 nodes / 28 edges
    LGRC9V3 final topology = 29 nodes / 28 edges
    max packet budget error = 2.842170943040401e-14
```

Known baseline gap closed in Iteration 34:

```text
run_event_queue(max_events=...) now drains both packet event_queue_records and
boundary_birth_trial_queue.
```

## Iteration 34. Deterministic Queue Ownership Patch

### Goal

Fix model-owned queue draining so `LGRC9V3.run_event_queue(max_events=...)`
matches the event surfaces that `LGRC9V3.step()` can process.

### Checks

- [x] Update `run_event_queue(...)` to continue while either queue has work:
      packet event queue or boundary-birth trial queue.
- [x] Preserve `step()` event ordering and tie-break behavior.
- [x] Add a birth-only queue test:
      scheduled boundary-birth trial is processed even when packet queue is
      empty.
- [x] Add a mixed packet/birth queue test:
      `run_event_queue(...)` drains both queues in deterministic order.
- [x] Assert `run_event_queue(max_events=0)` remains a no-op.
- [x] Assert empty queues still stop cleanly.

### Verification

- [x] Focused runtime tests pass.
- [x] Iteration 31-A stress tests still pass.
- [x] Corrected cascade comparison behavior is unchanged.
- [x] No default `GRC9V3` behavior changes.

### Summary

Iteration 34 complete.

Updated `LGRC9V3.run_event_queue(max_events=...)` so model-owned queue draining
matches `LGRC9V3.step()`: it continues while either the packet event queue or
the boundary-birth trial queue has work.

Added regression coverage for:

```text
birth-only boundary trial queue;
mixed packet departure / birth trial / packet arrival queue ordering;
max_events=0 no-op behavior;
empty queue clean stop behavior.
```

Verification completed:

```text
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime
    33 tests passed

PYTHONPATH=src ./.venv/bin/python -m unittest \
    tests.models.test_grc_9_step \
    tests.models.test_grc_9_runtime \
    tests.models.test_grc_9_v3_step \
    tests.models.test_grc_9_v3_sparks \
    tests.models.test_grc_9_v3_column_h_assisted
    69 tests passed

PYTHONPATH=src ./.venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
    GRC9V3 final topology = 29 nodes / 28 edges
    LGRC9V3 final topology = 29 nodes / 28 edges
    max packet budget error = 2.842170943040401e-14
```

## Iteration 35. Behavior-Preserving Module Ownership Split

### Goal

Split `lgrc_9_v3.py` by ownership without changing behavior, public semantics,
or legacy import compatibility.

### Checks

- [x] Freeze baseline from Iteration 33 before moving code.
- [x] Create split modules with explicit `__all__`:
      `lgrc_9_v3_contract.py`,
      `lgrc_9_v3_timing.py`,
      `lgrc_9_v3_packets.py`,
      `lgrc_9_v3_topology.py`,
      `lgrc_9_v3_identity.py`.
- [x] Keep `lgrc_9_v3.py` as a thin compatibility re-export facade.
- [x] Preserve `pygrc.models` exports.
- [x] Keep the dependency graph acyclic:
      contract imports no split modules;
      runtime may import split modules;
      split modules do not import runtime.
- [x] Move tests gradually toward specific split modules while keeping old
      import-path smoke tests.
- [x] Do not make semantic edits in the same iteration.

### Verification

- [x] Compile all model modules.
- [x] Smoke-test old `pygrc.models.lgrc_9_v3` imports.
- [x] Smoke-test direct split-module imports.
- [x] Focused LGRC9V3 contract/runtime tests pass.
- [x] Full Phase 8 LGRC9V3 relevant test set passes.
- [x] Corrected cascade reproduction still produces the same accepted
      high-level result.

### Summary

Iteration 35 complete.

`lgrc_9_v3.py` is now a compatibility facade over ownership-specific modules:
contract, timing, packets, topology, and identity. `LGRC9V3` runtime imports the
split modules directly, preserving the acyclic dependency rule and the legacy
`pygrc.models.lgrc_9_v3` import path.

Verification:
- `PYTHONPATH=src ./.venv/bin/python -m py_compile ...` over the split modules,
  facade, and runtime;
- `PYTHONPATH=src ./.venv/bin/python -m unittest
  tests.models.test_lgrc_9_v3_module_split
  tests.models.test_lgrc_9_v3_contract
  tests.models.test_lgrc_9_v3_runtime`;
- `PYTHONPATH=src ./.venv/bin/python -m unittest discover tests -p
  'test_lgrc*.py'`;
- `PYTHONPATH=src ./.venv/bin/python -m unittest
  tests.telemetry.test_lgrc9v3_contract
  tests.visualization.test_visualization`;
- `PYTHONPATH=src ./.venv/bin/python
  examples/lgrc9v3/corrected_cascade_comparison.py`.

The corrected cascade comparison remains at the accepted high-level result:
GRC9V3 and LGRC9V3 both finish with 29 nodes and 28 edges; the LGRC9V3 max
packet budget error remains `2.842170943040401e-14`.

## Iteration 36. Runtime Construction And Landscape Facades

### Goal

Move source-to-runtime wiring and common queue priming out of examples and into
tested library-owned helpers or model facades.

### Checks

- [x] Add a first-class landscape-backed construction path, such as:
      `build_lgrc9v3_from_landscape_seed(...)`,
      `run_lgrc9v3_landscape_seed(...)`, or
      `LGRC9V3.from_landscape_seed(...)`.
- [x] Preserve the current valid lowering sequence:
      `LandscapeSeed -> GRCL9V3 source -> GRC9V3State -> LGRC9V3RuntimeState`.
- [x] Add tested queue-priming helper(s) for initial packets, broad seed
      packets, and route generation from current topology.
- [x] Add an explicit scenario policy for corrected-cascade-style runs instead
      of keeping that policy only inside an example.
- [x] Keep examples thin: examples should demonstrate library-owned behavior,
      not own core scheduling policy.
- [x] Preserve corrected cascade comparison outcome.

### Verification

- [x] New landscape-backed LGRC9V3 example runs from repo root.
- [x] Existing landscape GRC9V3 examples still run.
- [x] Existing LGRC9V3 examples still run.
- [x] Corrected cascade comparison uses the new helper/facade or documents why
      it remains custom.
- [x] No default GRC9/GRC9V3 behavior changes.

### Summary

Iteration 36 complete.

Added `lgrc_9_v3_construction.py` as the library-owned construction and
queue-priming facade. It provides:

- `prepare_lgrc9v3_landscape_runtime(...)`;
- `build_lgrc9v3_from_landscape_seed(...)`;
- `LGRC9V3.from_landscape_seed(...)`;
- topology route generation through `lgrc9v3_graph_routes_for_current_topology(...)`;
- explicit packet queue priming through `prime_lgrc9v3_packet_departures(...)`
  and `prime_lgrc9v3_broad_seed_packets(...)`;
- corrected-cascade policy data through
  `LGRC9V3CorrectedCascadeScenarioPolicy`;
- corrected-cascade queue helpers through
  `build_lgrc9v3_corrected_cascade_runtime(...)`,
  `prime_lgrc9v3_corrected_cascade_queues(...)`, and
  `prime_lgrc9v3_corrected_cascade_broad_seed(...)`.

The preserved lowering sequence is explicit:

```text
LandscapeSeed -> GRCL9V3 source -> GRC9V3State -> LGRC9V3RuntimeState
```

`examples/lgrc9v3/landscape_seed_runtime.py` is the new landscape-backed
LGRC9V3 example. `examples/lgrc9v3/corrected_cascade_comparison.py` now uses
the library-owned corrected-cascade construction and queue-priming helpers.

Verification:
- `PYTHONPATH=src ./.venv/bin/python -m py_compile ...` over the new
  construction module, runtime/facade exports, updated examples, and tests;
- `PYTHONPATH=src ./.venv/bin/python -m unittest
  tests.models.test_lgrc_9_v3_construction
  tests.models.test_lgrc_9_v3_module_split
  tests.models.test_lgrc_9_v3_contract
  tests.models.test_lgrc_9_v3_runtime`;
- `PYTHONPATH=src ./.venv/bin/python -m unittest discover tests -p
  'test_lgrc*.py'`;
- `PYTHONPATH=src ./.venv/bin/python -m unittest
  tests.telemetry.test_lgrc9v3_contract
  tests.visualization.test_visualization`;
- `PYTHONPATH=src ./.venv/bin/python -m unittest
  tests.models.test_grc_9_step
  tests.models.test_grc_9_runtime
  tests.models.test_grc_9_v3_step
  tests.models.test_grc_9_v3_sparks
  tests.models.test_grc_9_v3_column_h_assisted`;
- `PYTHONPATH=src ./.venv/bin/python examples/landscapes/run_seed_grc9v3.py`;
- all existing `examples/lgrc9v3/*.py` smoke-run, including
  `corrected_cascade_comparison.py`.

The corrected cascade comparison remains at the accepted high-level result:
GRC9V3 and LGRC9V3 both finish with 29 nodes and 28 edges; the LGRC9V3 max
packet budget error remains `2.842170943040401e-14`.

## Iteration 37. Native Runtime Snapshot Restore Parity

### Goal

Implement native `LGRC9V3.load(...)` for snapshots emitted by
`LGRC9V3.snapshot()`.

### Checks

- [x] Restore base `GRC9V3State`.
- [x] Restore causal modes.
- [x] Restore packet ledger and event queue.
- [x] Restore boundary-birth trial queue.
- [x] Restore node proper-time surfaces and last-update event-time keys.
- [x] Restore local-update, packet-processing, causal-spark, and topology logs.
- [x] Restore observables consistently with `compute_observables()`.
- [x] Reject malformed or partial runtime snapshots clearly.
- [x] Keep old `GRC9V3` snapshots as `GRC9V3` snapshots; do not silently load
      them as native LGRC9V3 without an explicit adapter path.

### Verification

- [x] `LGRC9V3.save(...)` / `LGRC9V3.load(...)` round-trip preserves runtime
      state.
- [x] Loaded runtime can continue stepping deterministically.
- [x] Queue order after restore is stable.
- [x] Packet budget after restore remains audited.
- [x] Corrected cascade or a smaller mixed-event fixture can checkpoint,
      restore, and continue without changing accepted high-level behavior.

### Summary

Iteration 37 complete.

Native `LGRC9V3.load(...)` now restores snapshots emitted by
`LGRC9V3.snapshot()`.

The restore path:

- requires `metadata.model_family == "LGRC9V3"`;
- restores the cached base `GRC9V3` snapshot into a `GRC9V3State`;
- restores the native LGRC9V3 runtime artifact from
  `dynamics.lgrc9v3_runtime`;
- restores packet ledger, ordered event queue, boundary-birth trial queue,
  causal flux routes, proper-time maps, last-update event-time maps, arrival
  eligibility logs, packet-processing logs, local-update logs, causal-spark
  diagnostic logs, and topology logs;
- checks snapshot observables against `compute_observables()`;
- rejects partial native runtime snapshots clearly;
- rejects plain `GRC9V3` snapshots rather than treating them as native LGRC9V3.

Verification added:

```text
native runtime save/load round-trip
deterministic continuation after restore
queue-order preservation after restore
packet-budget audit after restore
plain GRC9V3 snapshot rejection
partial LGRC9V3 runtime snapshot rejection
```

Validation:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    125 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    920 tests passed

.venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_runtime_state.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/grc_9_v3.py \
    tests/models/test_lgrc_9_v3_runtime.py
    passed
```

## Post-37 Autonomous Event Production Track

Iterations 38-42 are autonomy work, not executor rewrites.

Rule:

```text
LGRC9V3.step()
    remains the deterministic queue executor

Autonomous producers
    schedule work with auditable reasons
```

Do not hide event production inside `step()` without an explicit policy and
payload contract.

## Iteration 38. Autonomous Event Production Contract

### Goal

Define the producer/scheduler contract before adding autonomous event
production.

### Checks

- [x] Add explicit producer policy ids.
- [x] Add producer schema/version constants.
- [x] Define producer reason-code fields:
      producer policy,
      producer version,
      trigger node/edge,
      thresholds,
      observed evidence,
      scheduled event kind,
      scheduled event-time key.
- [x] Define idempotency rules so repeated production in the same causal
      surface does not duplicate work.
- [x] Define queue ownership:
      producers may enqueue work;
      only `step()` consumes queued work.
- [x] Define disabled/no-op behavior.
- [x] Keep collapse/reabsorption and identity acceptance outside autonomous v1
      unless explicitly gated.

### Verification

- [x] Producer contract artifacts JSON round-trip.
- [x] Disabled producer policy schedules no work.
- [x] Repeated producer call on unchanged state is idempotent.
- [x] No topology mutation occurs during production.
- [x] `step()` behavior remains unchanged when no producer is called.

### Summary

Iteration 38 complete.

Added the autonomous event-production contract without adding active event
production yet.

New contract surfaces:

```text
LGRC9V3_AUTONOMOUS_PRODUCER_* constants
LGRC9V3AutonomousProducerFieldNames
LGRC9V3AutonomousProductionRecord
LGRC9V3AutonomousProductionResult
build_lgrc9v3_autonomous_surface_digest(...)
build_lgrc9v3_disabled_autonomous_production_result(...)
restore_lgrc9v3_autonomous_production_result_artifact(...)
LGRC9V3.produce_events(policy="disabled")
```

The v1 queue-ownership rule is now explicit:

```text
producers may enqueue work;
only LGRC9V3.step() consumes queued work.
```

The only implemented producer policy in this iteration is:

```text
disabled
```

It returns an auditable no-op result with reason code
`producer_policy_disabled`, schedules no work, does not mutate topology, does
not consume queues, and is idempotent on an unchanged causal surface.

Active producers remain planned:

```text
packet_departure_from_flux_route_policy
boundary_birth_trial_policy
```

Validation:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    129 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    924 tests passed

.venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_autonomy_contract.py
    passed
```

## Iteration 39. Packet Departure Producer From Flux/Route Policy

### Goal

Add the first autonomous producer for packet departures using explicit causal
flux/route policy.

### Checks

- [x] Inspect configured `causal_flux_routes` and/or accepted route policy.
- [x] Schedule packet departures only when route, source node, target node, and
      edge are valid.
- [x] Compute amount from explicit policy:
      fixed amount,
      amount fraction,
      or flux/pressure threshold policy.
- [x] Use existing edge causal delay and event-time policy.
- [x] Emit/serialize producer evidence for each scheduled packet.
- [x] Enforce idempotency for repeated production on the same causal surface.
- [x] Do not process packets inside the producer.

### Verification

- [x] Producer schedules expected packet departures from a simple route fixture.
- [x] Producer schedules no packets when no route is eligible.
- [x] Producer rejects malformed routes clearly.
- [x] Producer is idempotent on repeated calls.
- [x] Produced queue drains through existing `step()` with unchanged packet
      budget behavior.

### Summary

Iteration 39 complete.

Added the first active autonomous producer:

```text
policy = "packet_departure_from_flux_route_policy"
```

The producer inspects explicit `causal_flux_routes`, validates source/target
nodes and edge topology, resolves fixed `amount` or source-coherence
`amount_fraction`, rejects overdraw before scheduling, and enqueues packet
departure events through the existing LGRC9V3 packet queue. It records
auditable producer evidence with reason
`packet_departure_scheduled`, idempotency keys, thresholds, observed amount
evidence, and linked queued event ids.

Repeated calls on the same causal route surface do not duplicate work; they
emit `idempotent_causal_surface_already_produced`. Producers still do not
consume queued work. Packet debit, arrival, local-update evidence, and budget
accounting remain owned by `step()`.

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    9 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    929 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_autonomy_contract.py
    passed
```

## Iteration 40. Boundary-Birth Trial Producer

### Goal

Add autonomous scheduling of causal boundary-birth trials when the existing
boundary-birth policy is enabled.

### Checks

- [x] Inspect boundary/open ports without mutating topology.
- [x] Compute outward flux pressure from the existing accepted policy surface.
- [x] Schedule causal boundary-birth trial records only when policy-enabled.
- [x] Preserve existing birth acceptance/rejection semantics in `step()`.
- [x] Record producer reason codes and observed pressure evidence.
- [x] Keep random acceptance sampling explicit and reproducible.
- [x] Enforce idempotency for repeated production on the same causal surface.

### Verification

- [x] Disabled boundary-birth producer schedules no work.
- [x] Enabled producer schedules expected trial records.
- [x] Repeated producer call does not duplicate trials.
- [x] Scheduled trials route through existing `step()` birth processing.
- [x] GRC9V3 birth probability compatibility remains unchanged.

### Summary

Iteration 40 complete.

Added the second active autonomous producer:

```text
policy = "boundary_birth_trial_policy"
```

The producer inspects open boundary ports, computes outward flux pressure using
the existing GRC9V3-compatible surface, records the birth probability

```text
1 - exp(-lambda_birth * outward_flux_pressure)
```

and schedules explicit causal boundary-birth trial records with reproducible
`rng_sample` values. Acceptance/rejection and topology mutation remain owned by
`step()` through the existing scheduled-trial path.

The producer emits `boundary_birth_trial_scheduled` for scheduled trials,
records pressure/probability/sample evidence, and enforces idempotency for
repeated calls on the same causal surface. Disabled boundary-birth policy,
zero `lambda_birth`, missing open ports, or zero outward pressure produce
`no_eligible_work` instead of topology mutation.

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    13 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    138 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    933 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_autonomy_contract.py
    passed
```

## Iteration 41. Bounded Autonomous Run Loop

### Goal

Add `run_autonomous(max_events=..., policy=...)` as a bounded producer plus
executor loop.

### Checks

- [x] Add explicit autonomous run policy object or mode mapping.
- [x] Run producers only when queues need work or when policy says to refresh.
- [x] Consume work only through `step()`.
- [x] Stop clearly when no producer can schedule work and queues are empty.
- [x] Respect `max_events`.
- [x] Record producer counts, consumed event counts, stop condition, and
      idempotency status in bookkeeping.
- [x] Keep manual `step()` and `run_event_queue(...)` behavior unchanged.

### Verification

- [x] Autonomous loop reproduces a manually seeded packet fixture.
- [x] Autonomous loop schedules and consumes boundary-birth trials when enabled.
- [x] `max_events=0` is a no-op.
- [x] Empty/no-producer fixture stops cleanly.
- [x] Packet budget and queue ordering remain audited.
- [x] Native save/load works before and after autonomous execution.

### Summary

Iteration 41 complete.

Added bounded autonomous execution:

```text
LGRC9V3.run_autonomous(
    max_events=...,
    policy="bounded_lgrc9v3_v1",
    producer_policies=(...)
)
```

The loop runs producers only when both model-owned queues are empty, then
consumes scheduled work exclusively through `step()`. It respects
`max_events`, stops with a clear condition when no producer can schedule work,
and records producer/consumer counts in:

```text
StepResult.bookkeeping["autonomous_run"]
state.cached_quantities["last_lgrc9v3_autonomous_run"]
```

The summary includes producer invocation count, scheduled-event count,
state-mutating producer count, idempotent-skip count, no-eligible-work count,
consumed step/event counts, final queue status, and stop condition.

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    18 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    143 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests/models -p 'test_grc_9_v3*.py' -q
    123 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    938 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check \
    src/pygrc/models/lgrc_9_v3_contract.py \
    src/pygrc/models/lgrc_9_v3_runtime.py \
    src/pygrc/models/__init__.py \
    tests/models/test_lgrc_9_v3_autonomy_contract.py
    passed
```

## Iteration 42. Autonomy Examples And Handoff

### Goal

Document and demonstrate the difference between manual queue execution and
autonomous producer-driven execution.

### Checks

- [x] Add a concise example showing `produce_events(...)` then `step()`.
- [x] Add a concise example showing `run_autonomous(...)`.
- [x] Update LGRC9V3 examples README.
- [x] Update reference/status docs with the executor/producer boundary.
- [x] Update Phase 8 handoff with accepted autonomy v1 claims.
- [x] Keep corrected cascade reproducibility intact.

### Verification

- [x] New autonomy examples run from repo root.
- [x] Existing LGRC9V3 examples still run.
- [x] Existing landscape examples still run.
- [x] Focused LGRC runtime tests pass.
- [x] Full LGRC test sweep passes.
- [x] Full repository test suite passes.

### Summary

Iteration 42 complete.

Added two focused autonomy examples:

```text
examples/lgrc9v3/autonomous_produce_then_step.py
examples/lgrc9v3/autonomous_run.py
```

The first example shows the producer/executor boundary directly:

```text
produce_events(...)
    schedules one packet departure from causal_flux_routes

step()
    consumes the queued departure and performs the packet budget mutation
```

The second example compares manual queue seeding with autonomous production
over the same route. The traces consume the same packet lifecycle and reach
the same selected node coherence values, while the autonomous run records
producer/consumer summary evidence in `last_lgrc9v3_autonomous_run`.

Updated the LGRC9V3 examples README, Phase 8 handoff, and status record to
state the accepted autonomy v1 boundary:

```text
producers enqueue;
step consumes;
run_autonomous is a bounded producer + step loop.
```

Verification on 2026-05-07:

```text
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/autonomous_produce_then_step.py
    passed

PYTHONPATH=src .venv/bin/python examples/lgrc9v3/autonomous_run.py
    passed
```

Existing LGRC9V3 examples:

```text
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/executable_runtime.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/executable_packet_queue.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/causal_spark_diagnostics.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/landscape_seed_runtime.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/causal_history_surfaces.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/packetized_causal_flux.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/refinement_packet_transport.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/active_lgrc3_causal_history.py
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/telemetry_visual_bundle.py
    passed
```

Corrected cascade reproducibility:

```text
PYTHONPATH=src .venv/bin/python examples/lgrc9v3/corrected_cascade_comparison.py
    passed
    GRC final nodes/edges: 29 / 28
    LGRC final nodes/edges: 29 / 28
    max_abs_packet_budget_error: 2.842170943040401e-14
```

Landscape example:

```text
PYTHONPATH=src .venv/bin/python examples/landscapes/run_seed_grc9v3.py
    passed
```

Focused tests and static checks:

```text
PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_autonomy_contract -q
    18 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_runtime -q
    36 tests passed

PYTHONPATH=src .venv/bin/python -m unittest tests.models.test_lgrc_9_v3_construction -q
    4 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -p 'test_lgrc*.py' -q
    143 tests passed

PYTHONPATH=src .venv/bin/python -m unittest discover tests -q
    938 tests passed

PYTHONPATH=src .venv/bin/python -m ruff check ...
    passed

git diff --check
    passed
```

## Longer-Range Continuation Checklist

Use this list for surfaces that remain outside the planned LGRC-2/LGRC-3 and
executable LGRC9V3 runtime iteration paths. Do not mark these as complete
unless the corresponding surface is explicitly promoted into scope.

The N03-driven native packet-loop continuation has now been promoted into a
dedicated Phase 8 plan/checklist:

```text
Phase-8-LGRC9-NativePacketLoopPlan.md
Phase-8-LGRC9-NativePacketLoopChecklist.md
```

That continuation owns route-aspect semantics, source-pole surplus trigger
production, and native self-rearm causality evidence. It should not be tracked
as a loose long-range item here.

The N25.1-driven multi-basin formation continuation has now been promoted into
a dedicated Phase 8 plan/checklist:

```text
Phase-8-LGRC9-MultiBasinFormationPlan.md
Phase-8-LGRC9-MultiBasinFormationChecklist.md
```

That continuation owns the missing LGRC9V3 runtime surfaces between existing
causal refinement / child-stabilization source context and replayable
multi-basin formation evidence. It should not be treated as a loose
long-range item or as already-supported BF6 evidence.

- [ ] Standalone executable `LGRC9` runtime:
      decide whether pure nine-port causal history needs behavior beyond
      `GRC9V3`-backed annotation.
- [ ] Executable `LGRCV3` runtime:
      decide whether non-nine-port V3 needs its own causal-history substrate.
- [ ] General LGRC abstraction:
      wait until at least two executable Lorentzian families show repeated
      structure worth sharing.
- [ ] Directed delay as a default policy:
      define flux orientation, normalization, clipping, and default-off policy.
- [ ] Algebraic Lorentzian metric:
      decide whether a signed interval/tensor is justified by observed runtime
      tension.
- [ ] Landscape-general validation:
      define held-out landscape suites only after LGRC-2/LGRC-3 fixtures are
      stable.
