# Phase 9 GRCV4 Implementation Checklist

Date: 2026-09-05. Status: P9-G1 accepted; bounded implementation authorized.

Companions: [plan](./Phase-9-GRCV4-ImplementationPlan.md),
[phase opening](./Phase-9-GRCV4-PhaseOpening.json), and
[phase registry](./ImplementationPhases.md#phase-9-grcv4-substrate-and-grc9v4-specialization).

## Recording rules

- Use the accepted V4 specs as the primary implementation source, together
  with the paper and accepted investigation claims. Link each work item to
  its specification section/machine contract, paper passage, and applicable
  claim authority; use the forensic API to verify status and provenance.
- Mark a task complete only with its concrete artifact, command/result, or
  accepted review. Documentation, design proof, vector construction, and
  runtime execution are separate kinds of evidence.
- Record the exact code/release/profile/fixture identities with runtime work.
- Preserve all D10/D10.2 and D11 claim classes, debt lineage, and nonclaims.
- Keep old family contracts and the accepted V4 release frozen; V4 owns its
  adaptations and new runtime evidence.
- Track all ten profile families independently. Unsupported profiles and
  unexecuted cases stay visible and unadvertised.
- Summarize relevant failures (cause, correction, remaining limit) and gate
  holds before advancing dependent work. Do not register every debugging attempt.
  Preserve retrievable evidence for accepted results; raw failures only when
  material to the result or its limits. The [handoff addendum](./phase-9-grcv4/tranche-1/P9-1.9-EvidenceHandoff.md)
  clarifies retention without adding a gate or rewriting historical records.

## Execution granularity

Top-level tranches organize related work. Each `P9-N.M` row is the default
independently executable and reviewable iteration. It receives its own entry
authority, exact scope, source-contract map, changed paths, tests/oracles,
commands/results, retained evidence, new debt/failure disposition, reviewer
decision, and next permitted step. Completing one row does not complete or
accept its tranche.

Split independent candidates, profiles, lifecycle surfaces, or compatibility
cells into stable child IDs before execution. Declare child dependencies and
the parent's reconciliation criterion. A parent with children is an aggregate
register; execute and review the children separately. Controlled batches
retain individual results. Further child splits may refine this checklist
without redesigning the phase or changing existing IDs.

A failed or bounded result stops only dependent work unless it invalidates a
shared predecessor contract. Tranche order is not a global completion barrier.
Early C_OS lifecycle children from Tranche 7 run during Tranche 4, and later
profile generalization links their evidence. Tranche 6 and RG2b may remain
pending while an accepted C_OS path advances to reviewed specialization work.

## Gate register

| Gate | State | Evidence or remaining requirement |
| --- | --- | --- |
| P9-G0 | Recorded | Branch and planning documents; accepted release audit and no-ff merge identity. |
| P9-G1 | Accepted | [P9-1.9 acceptance](./phase-9-grcv4/tranche-1/P9-1.9-G1Acceptance.json), exact implementation scope and successor dispatch. |
| `P9-G2[p]` | Pending per profile | Full applicable generic runtime/lifecycle fixture product for exact profile scope p. |
| `P9-G3[S]` | Pending per consumed set | Accepted G2 for every profile in S and reviewed GRC9V4 specialization scope. |
| P9-G4 | Pending | Runtime conformance, regression evidence, reviewed support set, and handoff. |

The accepted generic support set is initially empty. Each family-level gate
record must bind the actual complete-profile IDs, parameters/domains, fixture
coverage, and evidence; a family label alone does not certify all instances.

| Generic profile gate | State | Acceptance route |
| --- | --- | --- |
| `P9-G2[C_OS]` | Accepted, exact singleton | [explicit G2 acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json) closes Tranche 4 and aliases P9-7.7-C_OS. Other profiles and G3 remain closed. |
| `P9-G2[A_OS]` | Pending | Tranche 5 plus A_OS lifecycle and P9-7.7 review. |
| `P9-G2[C_CI]` | Pending | P9-6.1a plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_CI]` | Pending | P9-6.1b plus profile lifecycle and P9-7.7 review. |
| `P9-G2[C_PC]` | Pending | P9-6.2a plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_PC]` | Pending | P9-6.2b plus profile lifecycle and P9-7.7 review. |
| `P9-G2[C_CI_PC]` | Pending | P9-6.3a plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_CI_PC]` | Pending | P9-6.3b plus profile lifecycle and P9-7.7 review. |
| `P9-G2[C_RG2b]` | Pending | P9-6.4a foundation, P9-6.4c generalization and P9-6.4d audit for C, plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_RG2b]` | Pending | P9-6.4b foundation, P9-6.4c generalization and P9-6.4d audit for A, plus profile lifecycle and P9-7.7 review. |

`P9-G3[C_OS]` denotes singleton set `{C_OS}`. It may be reviewed through
P9-7.8 after P9-G2[C_OS], independently of other profiles. Adding profiles
requires a reviewed extension with their accepted generic identities. G3
admits specialization work; it does not establish full GRC9V4 conformance.

## Tranche 0. Planning bootstrap

- [x] P9-0.1: Create `impl/phase-9-grcv4` from merge
  `e00a8844c045ac4338fa52afb6ab096420fb6161`.
- [x] P9-0.2: Record specification acceptance commit
  `935cc532c9c8e53f4fc26bc43e9e40401cdb2410` and the two-parent merge.
- [x] P9-0.3: Create the Phase 9 plan, checklist, and successor opening record.
- [x] P9-0.4: Register Phase 9 and link the companion documents.
- [x] P9-0.5: Bind the accepted release and immutable predecessor governance records.
- [x] P9-0.6: Confirm dedicated release acceptance: twelve artifact members pass.
- [x] P9-0.7: Query both D11 claims and local debts through the successor forensic API;
  retain bounded resolution and forward-verification distinctions.
- [x] P9-0.8: Carry the full inherited populations and route all twelve vector holds.
- [x] P9-0.9: Record the existing normal-verification failure as `P9-TOOL-001`.
- [x] P9-0.10: Verify Markdown rendering, new links, opening bindings, and diff hygiene.

Opening evidence: `GRCV4_SPECIFICATION_RELEASE_ACCEPTANCE_AUDIT_PASS`;
successor graph discovery reports 41 current claims, 29 historical claims,
31 debt transformations, 80 objects, 183 equation contracts, and 18
verification-obligation nodes. These counts describe the source graph, not
completed runtime evidence or the executable profile population.

Initial planning checks passed: three Markdown documents rendered, 28 local links
validated, predecessor/release hashes and both merge parents verified, all
twelve coverage holds mapped, and the change scope limited to the four
declared planning files.

## Tranche 1. Implementation review and successor verification

- [x] P9-1.1: Read the V4 specifications, corresponding paper passages, and
  accepted investigation claims for the proposed support set; create the
  specification/paper/claim/contract-to-module-and-test crosswalk.
- [x] P9-1.2: Inventory all 29 inherited D10 debt transformations and both
  bounded D11 resolutions, with exact claim links and dispositions.
- [x] P9-1.3: Inventory all 18 source verification obligations. Link completed
  D11 propagation to downstream acceptance; route every remaining obligation
  to an implementation iteration or named deferred scientific gate.
- [x] P9-1.4: Review the early C_OS dynamics/lifecycle/G2 path and subsequent
  A_OS or C-only GRC9V4 route; specify exact dependencies and supported,
  planned, and deliberately deferred profile rows.
- [x] P9-1.5: Review module/API ownership, dependencies, independent oracles,
  artifact retention, and immutable old-family regression targets.
- [x] P9-1.6: Close `P9-TOOL-001` through successor verification of the current
  tree and routing from the normal tool entry point. Preserve release-bound
  historical auditor/boundary bytes and their historical checks.
- [x] P9-1.7: Verify rejection of unauthorized paths, modified frozen bytes,
  and stale/forged authority. Verify legitimate planning and later explicitly
  authorized V4 source/test additions are admitted in their respective states.
- [x] P9-1.8: Update tool plan/checklist and any API/notebook/browser surfaces
  affected by that verification change; retain consistent authority labels.
- [x] P9-1.9: Record accepted P9-G1 successor authority with exact mutation
  scope and release bindings before runtime work starts.

P9-1.9 current disposition: the user explicitly accepted P9-1.4–P9-1.8 and
the reviewed V4-only implementation scope. The [G1 review](./phase-9-grcv4/tranche-1/P9-1.9-G1Review.md)
and [execution record](./phase-9-grcv4/tranche-1/P9-1.9-ExecutionRecord.json)
record acceptance separately from the unchanged historical review evidence.
The historical pending statements below describe those earlier checkpoints;
they are superseded for P9-G1 only. G2/G3/G4, all runtime support, fifteen
source obligations and five implementation follow-ups remain pending. No
runtime code was added by this gate-recording step. Dependency-ready work:
P9-2.1 and P9-2.2 at that transition, with twelve eligible paths after P9-2.2's
narrow package-integration routing correction. Tranche 1 is
reconciled as the review/authorization tranche, not as Phase 9 completion.

P9-1.1–P9-1.3 evidence: [review package](./phase-9-grcv4/tranche-1/P9-1.1-1.3-Review.md)
and [separate execution results](./phase-9-grcv4/tranche-1/P9-1.1-1.3-ExecutionRecord.json).
The user accepted these three iterations on 2026-09-05. The later
[acceptance record](./phase-9-grcv4/tranche-1/P9-1.1-1.3-AcceptanceRecord.json)
binds their exact evidence; original preparation records remain unchanged.
This acceptance does not grant P9-G1 approval or accept P9-1.4/P9-1.5.
The crosswalk covers 41 current claims and 183 contracts;
the inventory retains all 31 debt records. Of 18 source obligations, one
bounded preclose and two downstream propagation steps were already satisfied;
fifteen still need runtime, numeric, or scientific evidence. No obligation
was discharged by this batch. `P9-REVIEW-001` preserves the API's indeterminate
support-edge semantics for the 152 D10.2 contracts, for P9-1.5 acknowledgement.
P9-1.4/P9-1.5 subsequently acknowledge that boundary without promoting it.

P9-1.4 evidence: [support/dependency review](./phase-9-grcv4/tranche-1/P9-1.4-SupportReview.md)
and its exact ten-profile/child/dependency register. P9-1.5 evidence:
[ownership/oracle/legacy review](./phase-9-grcv4/tranche-1/P9-1.5-OwnershipReview.md),
seventeen proposed module owners and 135 explicit baseline paths. Existing
regressions pass: 105 core tests and 763 model tests. These checkmarks record
completed engineering reviews; user acceptance and P9-G1 remain pending.
The [separate execution results](./phase-9-grcv4/tranche-1/P9-1.4-1.5-ExecutionRecord.json)
retain the scope, tests, observations and next step for each iteration.
P9-1.6 implementation/verification evidence is recorded separately below;
P9-1.7/P9-1.8 implementation/verification results follow below. Their user
acceptance, P9-1.9 and all runtime gates remain pending.

Independent-review planning corrections are applied: the composite families
retain their IDs but use the schema's `realization: "CI+PC"`; P9-9.1 is split
into optional completion and mandatory lifecycle children. The original
review/check attachments and post-correction validation are separately bound
in the execution record. These corrections do not accept P9-1.4/P9-1.5.

### Registered independent-review follow-through

The five `P9-REVIEW-FOLLOW-7.*` rows remain **pending**, not implemented or
executed. The six `P9-REVIEW-PRESSURE-8.*` assignments are now verified by
the [P9-1.7 pressure results](./phase-9-grcv4/tranche-1/P9-1.7-PressureResults.json)
and P9-1.8 access checks, without granting runtime authority. The
[ownership register](./phase-9-grcv4/tranche-1/P9-1.5-OwnershipAndLegacyBaseline.json)
retains detailed requirements, concrete test pressures and exact child owners.

| Registered item | Existing leaf owners | Required evidence |
| --- | --- | --- |
| `P9-REVIEW-FOLLOW-7.1` | P9-2.2, P9-2.6 | Release-bound packaged assets; clean wheel/sdist outside checkout; legacy without extra, V4 with extra, typed missing dependency and asset failures. |
| `P9-REVIEW-FOLLOW-7.2` | P9-2.1, P9-2.6, P9-3.1 | Explicit symbol/hash/contract/reason reuse ledger, including graph storage/lookup and utilities; no shared refactor by similarity. |
| `P9-REVIEW-FOLLOW-7.3` | P9-4.3 | Supplemental tau-C-zero on nontrivial retained Hodge with nonzero kappa-M: identity resolvent but direct baseline conditioning survives. |
| `P9-REVIEW-FOLLOW-7.4` | P9-2.5, P9-3.4, P9-4.5 | Exact-byte versus tolerance/environment scope; nonidentity SPD, near-admitted boundaries and repeated-eigenvalue cluster projectors; no silent numerical repairs. |
| `P9-REVIEW-FOLLOW-7.5` | C_OS/A_OS children of P9-7.2a/b–P9-7.6 | Different live/reset inputs, independent target transport/readmission, reset-after-operation, ledger/delta and full-payload rollback. |
| `P9-REVIEW-PRESSURE-8.1` | P9-1.6, P9-1.7 | Green planning review cannot unlock runtime/source/test/dependency writes. |
| `P9-REVIEW-PRESSURE-8.2` | P9-1.6, P9-1.7 | Legitimate successor planning passes with unchanged historical checks. |
| `P9-REVIEW-PRESSURE-8.3` | P9-1.7 | Deleted required child, forged alias, unresolved dependency reject even with matching counts. |
| `P9-REVIEW-PRESSURE-8.4` | P9-1.7, P9-1.8 | No unrelated profile barrier; no advertisement of unexecuted exact identities. |
| `P9-REVIEW-PRESSURE-8.5` | P9-1.7, P9-1.8 | Conditional completion and its own scoped evidence; no universal child prerequisite. |
| `P9-REVIEW-PRESSURE-8.6` | P9-1.6, P9-1.7 | Fail closed on forged/stale/hash/status/path-content violations, not filename or green marker. |

`P9-TOOL-001` was reproduced before Phase 9 file edits using
`verify-post-d10-specifications`. It rejected
`audit_grcv4_specification_release_acceptance.py`,
`GRCV4SpecificationReleaseAcceptanceGate.json`, and
`PostGRCV4SpecificationAcceptanceBoundary.json` as outside the historical
phase envelope. The dedicated acceptance audit passed. This opening-time
failure was carried to P9-1.6–P9-1.8; the later disposition follows below.

P9-1.6 successor update: the [verification candidate](./phase-9-grcv4/tranche-1/P9-1.6-SuccessorVerification.md)
and [execution record](./phase-9-grcv4/tranche-1/P9-1.6-ExecutionRecord.json)
record the normal-entry routing repair and unchanged historical checks on
their accepted Git revision. `P9-TOOL-001` is resolved for the present planning
tree; that result alone did not mark P9-1.7/P9-1.8 or the six registered successor pressure
assignments complete. The opening's original failure observation and all
earlier evidence remain unchanged. Candidate review and P9-G1 remain pending;
runtime authority/support remain false/empty.

P9-1.7/P9-1.8 successor update: the [verification review](./phase-9-grcv4/tranche-1/P9-1.7-1.8-VerificationReview.md)
and [separate leaf results](./phase-9-grcv4/tranche-1/P9-1.7-1.8-ExecutionRecord.json)
record 106 passing pressure cases, including replay of all 13 unchanged
P9-1.6 tests in the exact retained snapshot. Current byte checks protect 712
baseline files; runtime-positive controls use only synthetic, independently
pinned test approval. Actual API checks, ten cross-surface checks, two notebook code cells, eight new
Node tests and fourteen desktop/mobile browser tests pass. The normal verifier
also passes the unchanged historical/D11 checks and byte-exact rebuilds.
The [access guide](./investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/Phase9VerificationGuide.md)
provides runnable entry points; the scenario register links executable cases.
These checkmarks record engineering completion only. All five implementation
follow-ups, fifteen pending source obligations, user acceptance and
P9-1.9/P9-G1 remain pending. No scientific or runtime evidence is fabricated.

The [pressure-guide closure register](./phase-9-grcv4/tranche-1/P9-1.6-1.8-AuditClosure.json)
and [surface inventory](./phase-9-grcv4/tranche-1/P9-1.8-SurfaceInventory.json)
retain combined-fault, attributable-rejection, checker-sensitivity, semantic
projection, freshness, actual normal-command and cross-surface evidence.
Candidate decisions, harness assertions and project effect stay separate;
three bounded batches retain their own results and raw per-run manifests.

## Tranche 2. Interface, identity, and evidence foundation

- [x] P9-2.1: Implement V4-owned immutable state/result records with read-only
  common-interface projections and recursive mutation protection.
  Record symbol-level reuse/replacement decisions before consumption (§7.2).
  [Review](./phase-9-grcv4/tranche-2/P9-2.1-Review.md) and
  [execution](./phase-9-grcv4/tranche-2/P9-2.1-ExecutionRecord.json): R1/R2 stress
  corrections covered by 39 ownership tests and 511 required stress probes;
  105 unchanged core tests, Ruff and strict mypy pass. This marks
  engineering completion. The user's commit instruction accepts this work;
  see the [foundation decision](./phase-9-grcv4/tranche-2/P9-2.1-2.2-AcceptanceRecord.json).
  No model/profile is
  admitted and the broader P9-2.6 immutability/lifecycle obligations remain.
- [x] P9-2.2: Implement complete profile/parameter resolution and canonical
  identities against all applicable schema/preimage vectors.
  Package and hash-bind schema/identity assets for installed use (§7.1).
  Carry P9-2.1 stress H1/H2: typed/JCS identity rather than Python equality/hash,
  explicit codec projections rather than dataclass helpers, and wide-map
  refreezing/equality scale checks before profile/reference-map consumption.
  [Review](./phase-9-grcv4/tranche-2/P9-2.2-Review.md) and
  [execution](./phase-9-grcv4/tranche-2/P9-2.2-ExecutionRecord.json): all 25
  published preimages, typed ten-shape declarations, reference-content checks,
  and clean wheel/sdist installs. H1/H2 have focused regressions. Independent
  audit R1 (typed integer storage), R2 (explicit canonical reconstruction) and
  F1 (C/reference-Hodge value agreement) are corrected and regression-tested:
  79 focused tests and 357 stress probes pass. Original audit/subject bytes,
  the two-callsite probe adaptation and corrected execution remain separate.
  Frozen identities and native safe-integer rejection are unchanged. Engineering
  completion was followed by the user's commit acceptance in the same
  foundation decision. Executable support remains empty.
- [x] P9-2.3: Separate wire failures, semantic admission failures, and strict
  admitted requests; keep harness injection outside production identity.
  Enforce the P9-2.1 H1 boolean/number identity boundary and exclude unsupported
  pickle/reinitialization routes from admitted state decoding.
  Compose P9-2.2's distinct strict-configuration/canonical-reconstruction
  decoders with operation-specific admission; neither decoder admits a state.
  [Review](./phase-9-grcv4/tranche-2/P9-2.3-Review.md) and
  [execution](./phase-9-grcv4/tranche-2/P9-2.3-ExecutionRecord.json): 26 new tests
  cover duration admission, exact failure receipts, malformed/forged inputs,
  direct/factory consistency, numeric reconstruction, nonzero underflow,
  identity suffixes and nested mutation. The combined 105 foundation tests,
  357 previous audit probes and installed wheel/sdist request checks pass.
  Accepted by the user's commit instruction at `1647d3f`; the separate
  [acceptance record](./phase-9-grcv4/tranche-2/P9-2.3-AcceptanceRecord.json)
  preserves the original preparation/execution bytes.
  Migration execution, full prestate admission and complete stepping remain
  later work, not implicitly certified by typed request construction.
  Two-audit follow-up: content-identity-only receipt wording and explicit
  decoder guidance; isolated numeric-route, exact-underflow, receipt/request
  distinction, source/causal limits, enum parity and migration-declaration
  regressions: 112 focused tests, 875 checkout stress scenarios and clean
  wheel/sdist checks pass. The original 874/875 checkout result is retained;
  its only failure was the audit harness counting existing package legacy
  imports as V4 additions. The baseline-aware correction retains the rejection
  assertion, with eight sensitivity controls. See the review's per-item
  dispositions and distinct checkout run.
- [x] P9-2.4: Implement orthogonal operation/solver dispositions and receipt
  delta versus persistent ledger ownership.
  Negative duration: rejected operation, `solver_disposition=None`, no commit
  ID or persistent append. Bind imported receipt operation/stage/code and
  source/poststate to actual execution, not just a recomputed digest. With the
  later solver consumer, preserve `valid_root` on subsequent charge rejection.
  [Review](./phase-9-grcv4/tranche-2/P9-2.4-Review.md) and
  [execution](./phase-9-grcv4/tranche-2/P9-2.4-ExecutionRecord.json): strengthened
  existing immutable result records, content-checked typed failure/envelopes,
  acyclic receipt-to-commit-to-envelope construction, pure operation/state/
  ledger comparisons and a bound negative-duration result. Imported state or
  receipt labels alone cannot substitute for captured payloads and observed
  outcomes. Full numerical execution/rollback and live-state authentication
  remain later owner tests. The user's commit instruction accepted this leaf
  at `3845c41`; see the separate
  [acceptance](./phase-9-grcv4/tranche-2/P9-2.4-AcceptanceRecord.json).
  This is not acceptance of any runtime profile.
  Verified 134 foundation tests (22 new result/receipt cases), 875 predecessor
  stress scenarios, 105 legacy core tests, packaging and strict static checks.
  Two-audit correction: original-number validation, ordered event-container
  admission, typed/primitive commit composition, and exact-byte evidence
  storage now have 11 added regression/characterization tests. The exact
  checkout reproduces the submitted 11 exposures before correction. Separate
  pre/post records preserve that failure evidence and the corrected run.
  Parent-ID content validation is explicitly not lineage-DAG certification;
  the unresolved parent scope/order contract belongs to P9-7.6, not an invented
  intra-commit-only rule in this leaf. See the review's per-item dispositions.
- [x] P9-2.5: Create the runtime harness with independent oracles and exact
  source/profile/fixture/prestate/poststate/receipt evidence bindings.
  Specify environment and exact-byte versus tolerance comparison scope (§7.4).
  Retain exact request independently of receipt identity; test different
  negative requests with equal receipts, foreign/rehashed evidence and a
  grammar-valid wrong source. Compare complete scientific/lifecycle payloads
  on failure and distinguish emitted receipt delta from persistent history.
  Carry P9-2.4's four self-consistent but invalid transition characterizations
  into independent live-step oracles (also P9-4.7a): wrong elapsed time,
  unchanged index, backward clock and zero-duration state change. Capture
  observed stage/code/solver independently of the result under test. Account
  for binary64 clock rounding; matching records or a `StepResultEvidence`
  instance certify neither execution nor parent lineage.
  [Review](./phase-9-grcv4/tranche-2/P9-2.5-Review.md) and
  [execution](./phase-9-grcv4/tranche-2/P9-2.5-ExecutionRecord.json): engineering
  harness accepted by the user's commit instruction at `2075f47`; the
  [separate acceptance](./phase-9-grcv4/tranche-2/P9-2.5-AcceptanceRecord.json)
  preserves the original review/execution bytes. The actual adapter
  executes only the negative-duration prefix. Independent full-state/ledger/
  reset and receipt checks, exact-request retention, source/environment
  bindings, no-overwrite inspection and mutation controls are covered.
  The four positive/zero transition negatives currently exercise explicit
  fixture-clock rules, not a live numerical step; P9-4.7a retains that consumer
  obligation. Numerical conditioning/projectors remain P9-3.4/P9-4.5 work;
  parent lineage remains P9-7.6 work. No runtime support is promoted.
  Independent-audit correction: all two required and four advisory items have
  explicit dispositions in the review. Added regressions narrow the identity
  oracle (not science), reject mismatched default-CLI recipes, retain malformed
  capture diagnostics, validate failed reports, and bind checker origins.
  Inspection keeps evidence classification. Verified 177 foundation/harness
  tests and 3,337 independent numeric pressure cases; original run bytes and
  default content identities are preserved.
- [x] P9-2.6: Verify unsupported-profile rejection, deep immutability, and
  unchanged common-interface behavior for older families.
  Verify clean wheel/sdist and optional-extra boundaries (§7.1) and each
  consumed legacy symbol's exact reuse boundary (§7.2).
  Carry strict-request non-admission tests into each authorized facade/full-step
  consumer (P9-4.4/P9-4.5/P9-4.7a): zero, subnormal and extreme finite duration must not
  bypass graph/profile/context/domain checks. Current no-facade assertions are
  leaf-stage checks, not a permanent prohibition on authorized implementation.
  [Review](./phase-9-grcv4/tranche-2/P9-2.6-Review.md) and
  [execution](./phase-9-grcv4/tranche-2/P9-2.6-ExecutionRecord.json): bounded
  foundation integration implemented; user acceptance pending. Verify all ten
  declarations remain unsupported, detached recursive storage/common fields,
  unchanged explicit legacy baseline, clean installs with absent/partial/full
  extras and installed-asset corruption. No production, legacy or frozen source
  edits; no facade exported. Six leaves/nineteen paths are dependency-ready,
  not accepted conformance. P9-3.1 remains held until this leaf is accepted.
  Self-check hardening: nine integration methods, all implemented foundation
  layers through four fresh installed cells and two distinct import orders, partial
  extras, actual module/archive identities, cold/warm asset rejection and five
  older-family mixed-use comparisons. Reconcile prior corrections by accepted
  subject and preserve original evidence. A separate final combined suite and
  exact default-prefix CLI replay supply current-source evidence; neither
  accepts a profile nor starts Tranche 3.

## Tranche 3. Typed graph, geometry, transport, and charge

- [x] P9-3.1: Implement deterministic graph/differential identities, typed
  Hodge/one-form/physical-flux maps, and candidate-local mobility ownership.
  Resolve graph-backend storage/lookup and utility reuse before implementation (§7.2).
  [Review](./phase-9-grcv4/tranche-3/P9-3.1-Review.md) and
  [execution](./phase-9-grcv4/tranche-3/P9-3.1-ExecutionRecord.json): implemented
  primitive graph/pairing/mobility foundations, pending user review. Entry
  follows the separate [P9-2.6 acceptance](./phase-9-grcv4/tranche-2/P9-2.6-AcceptanceRecord.json).
  Completion does not accept P9-3.1, admit a profile, or enable P9-3.2.
  Audit 1 F1 is corrected with exact local positivity validation: native
  before/after evidence, 876/876 independent stress scenarios and 67 primitive
  tests including isolated wheel/source installations are bound in the review.
  Signed boundary cases, exact nonpositive families and positive extreme-scale
  controls are included; conditioning and stage admission remain separate.
- [x] P9-3.2: Implement exact stage/cache provenance and domain admission.
  [Review](./phase-9-grcv4/tranche-3/P9-3.2-Review.md) and
  [execution](./phase-9-grcv4/tranche-3/P9-3.2-ExecutionRecord.json): local reference,
  affine positive-geometry and stage/cache implementation. Accepted at `77286b2`;
  the separate [P9-3.2 acceptance record](./phase-9-grcv4/tranche-3/P9-3.2-AcceptanceRecord.json)
  preserves that decision without rewriting historical review evidence.
  Entry follows explicit P9-3.1 acceptance at `dccb1ca`, preserved in the
  separate [acceptance record](./phase-9-grcv4/tranche-3/P9-3.1-AcceptanceRecord.json).
  Historical preparation statements above do not override that later decision.
  Full candidate/root/PC invariant-domain and transaction execution remain with
  their assigned later leaves. No numerical profile is admitted.
- [x] P9-3.3: Implement the one-resource-write complete-step boundary and
  exact charge gate, without an extra remainder/repair coordinate.
  [Review](./phase-9-grcv4/tranche-3/P9-3.3-Review.md) and
  [execution](./phase-9-grcv4/tranche-3/P9-3.3-ExecutionRecord.json): one provisional
  continuity evaluation after a bound supplied current result, exact charge
  inequality after the prescribed binary64 tree, no resource repair, and local
  zero-duration identity. Explicitly accepted by the user for commit after
  audit follow-up and evidence cleanup. P9-3.4's committed-subject permission
  transition remains separate. Actual root
  selection, final reconstruction, writers and atomic commit remain with the
  full-step/lifecycle owners; no numerical runtime profile is advertised.
  First audit follow-up: native independent driver 701/701, eight mutation
  controls detected, and 96 transport/step methods including both clean
  resource package/reconstruction tests pass. Six added regressions preserve
  charge precision limits and charge-blind flow/authority controls. Executable
  numerical logic is unchanged; the review links reconstructible audit inputs
  and a complete packet exporter. The retained numerical limitations remain
  assigned to P9-3.4 and the later experimental/transaction owners.
- [x] P9-3.4: Execute nonidentity SPD, permutation, signed-edge covariance,
  nonfinite/domain, stale-cache, and charge-precision cases.
  Include near-admitted conditioning boundaries and repeated eigenvalues
  within a strictly separated cluster; compare invariant projectors (§7.4).
  Carry the [P9-3.2 audit numerical witness](./phase-9-grcv4/evidence/P9-3.2/audit-1-followup/run.json):
  adjacent-edge form `(5e-324, 1e150)` loses a representable off-diagonal
  coupling through intermediate underflow; reversing edge order retains it.
  Compare componentwise and normwise error, signed/permuted coordinates,
  true underflow, and overflow before declaring the numerical envelope or
  changing product evaluation. This follow-through is not discharged by the
  moderate-scale covariance tests and adds no P9-3.3 prerequisite.
  Carry the [P9-3.3 paired precision witnesses](./phase-9-grcv4/tranche-3/P9-3.3-Review.md#independent-audit-follow-up):
  `(2**53, 0)` with unit flux and duration `0.5` admits `(2**53, 0.5)`
  at zero rounded residual despite exact stored-sum growth `1/2`; the existing
  four-vertex exact-conservative transfer instead rejects with residual `2`.
  Include `(1e20, 0)` and 100 primitive continuity compositions, subnormal
  transfers, cancellation-heavy/high-degree divergence and safe-order controls.
  Declare the aggregation/environment envelope before broader covariance or
  experimental conservation claims. Zero rounded residual is not exact
  stored-sum conservation; diagnostic exact sums must not become hidden state,
  resource repair or an alternate admission rule. Primitive compositions are
  not executed full beats. The product correction and remaining precision
  boundaries are recorded in the review below.
  [Review](./phase-9-grcv4/tranche-3/P9-3.4-Review.md) and
  [execution](./phase-9-grcv4/tranche-3/P9-3.4-ExecutionRecord.json): implemented
  and verified; explicitly accepted by the user for commit after audit follow-up
  and evidence consolidation. P9-3.5's separate permission transition will bind
  the accepted commit. Corrected intermediate product underflow;
  retained true-underflow/rounded-PSD and charge/aggregation limits. The
  original full suite passes 1,653 tests, no skips; a separate added method passes
  288 dense near-gap projector actions. Audit follow-up: 1,662 current native
  tests, no failures/errors/skips, and 568 independent native scenarios pass.
  Verified 137 authority, 20 JavaScript and 18 browser checks, exact source reconstruction and unchanged earlier evidence.
  These primitive and analysis results do not execute the future C selector,
  current block, complete beat or lifecycle transaction. The
  [audit follow-up](./phase-9-grcv4/tranche-3/P9-3.4-Review.md#independent-audit-follow-up)
  closes capture coverage and provenance/diagnostic integrity gaps. Exact-SPD
  input can still evaluate negative/zero self-pairings: P9-4.2/P9-4.5 and later
  norm/energy consumers own demonstrated numerical validity at that boundary,
  with no clipping, floor or absolute-value repair. Actual selectors must cover
  both sides of the declared cutoff, the exact boundary and strict-gap loss;
  retained conditioning must not be relabeled as physical conditioning.
  Its committed acceptance at `12611fe` is now bound by the
  [successor entry record](./phase-9-grcv4/tranche-3/P9-3.4-AcceptanceRecord.json).
- [x] P9-3.5: Verify full prestate preservation after every rejected operation.
  [Review](./phase-9-grcv4/tranche-3/P9-3.5-Review.md) and
  [execution](./phase-9-grcv4/tranche-3/P9-3.5-ExecutionRecord.json): implementation
  and validation complete; explicitly accepted by the user for commit after
  the limited audit follow-up. The original full capture passed all 1,675
  regression methods with zero failures, errors or skips. Observe full reachable
  inputs at implemented local rejection boundaries, including both histories,
  ordered receipts, request/current selection, provisional results and caches.
  Constructor/wire failures and harness mutation controls remain separately
  identified. Real complete-beat and lifecycle rollback retain P9-4.5/P9-4.7a
  and P9-7.* ownership. Eleven leaves and 23 runtime paths are dependency-ready;
  runtime profile support remains empty.
  The limited independent audit's skip-reporting finding is corrected;
  all 20 focused follow-up methods passed. The original full run remains
  separately identified. The limited external audit did not complete the primary
  preservation review; user acceptance does not change that audit's scope.
  The bound review and execution record retain their pre-acceptance state.
  A later authorized entry will bind P9-3.5's accepted commit separately;
  no Tranche 4 work is started by this acceptance.

## Tranche 4. D11-C and the first C_OS runtime slice

- [x] P9-4.1: Bind `C-HM-STIFFNESS-BASELINE-v1`, the exact positive stable-edge
  reference map, and separate Hodge/mobility constructor identities.
  Implemented and verified on `impl/phase-9-grcv4-tranche-4`; accepted by the
  user's commit instruction after audit follow-up. The
  [review](./phase-9-grcv4/tranche-4/P9-4.1-Review.md) maps source contracts,
  typed constructor and complete-profile identities, strict reference-map
  admission, binary64/outlier pressure and reconstruction to executable tests.
  Entry binds P9-3.5 at `155c728`: twelve ready leaves, 25 eligible paths,
  empty runtime support. The corrected capture passed 51 focused methods and
  seven relocated checks; historical records retain their original dispositions
  and attribution limits. P9-4.2 entry now binds accepted `94a079d` in its separate
  [acceptance record](./phase-9-grcv4/tranche-4/P9-4.1-AcceptanceRecord.json).
- [x] P9-4.2: Implement the accepted potential and baseline flux, selector
  gap, Read-Back typing, and regular current solve at their declared stages.
  Implemented and verified; explicitly accepted by the user for commit after
  the user reported that both reviews found no defects. The
  [review](./phase-9-grcv4/tranche-4/P9-4.2-Review.md) and
  [execution record](./phase-9-grcv4/tranche-4/P9-4.2-ExecutionRecord.json) bind
  123 passing focused methods, including 27 current methods, source reconstruction
  and 17 relocated methods under each of two hash seeds. Exact singularity is
  checked before resolvent rounding; actual physical conditioning is certified
  separately from retained coordinates. Cutoff ties/unresolved gaps, nonreference
  SPD geometry, multigraph modes, previous pairing outliers, numerical extremes,
  strict declarations and input preservation are exercised. Thirteen leaves and
  25 paths are dependency-ready; full OS, lifecycle and runtime support remain held.
  Review/execution records retain their validation-time dispositions. P9-4.3 entry
  now binds accepted `ac3a7cf` in the separate
  [acceptance record](./phase-9-grcv4/tranche-4/P9-4.2-AcceptanceRecord.json).
- [x] P9-4.3: Verify independent kappa-M, chi, and zeta zero controls and
  complete smooth-stratum baseline derivative/covariance cases.
  Add the separate tau-C-zero control on nontrivial retained Hodge with
  nonzero kappa-M; no frozen-catalog edit or simultaneous-zero shortcut (§7.3).
  Implemented and verified; explicitly accepted by the user for commit. The
  [review](./phase-9-grcv4/tranche-4/P9-4.3-Review.md) maps the complete supported
  baseline chain, independent controls, covariance and edge cases to 20 new
  methods. The [execution record](./phase-9-grcv4/tranche-4/P9-4.3-ExecutionRecord.json)
  binds 143 passing focused methods and 27 passing reconstructed derivative/capture
  methods with a changed hash seed. Literal projector/scalar/reference witnesses,
  nonzero omitted terms, repeated/closing gaps, domain boundaries and saturation
  pressure the oracle and actual current independently. Production, frozen specs
  and paper are unchanged. Fourteen leaves and 25 paths are dependency-ready;
  P9-4.4 and runtime conformance remain held. Review, execution and run records
  retain their validation-time dispositions; this checklist and the commit record
  the later acceptance. A separately authorized P9-4.4 entry can bind this commit.
  Post-acceptance audit: `39cfe6a` had a test-only saturation false-zero/NaN gap.
  The [follow-up](./phase-9-grcv4/tranche-4/P9-4.3-AuditFollowup.md) corrects the
  derivative arithmetic, declares its numerical limits and adds five regressions.
  All 148 focused methods passed in a reconstructed checkout. The user has
  accepted the verified follow-up. Its index and run retain their validation-time
  dispositions; this checklist and the commit record the later acceptance.
  Original evidence is unchanged and P9-4.4 remains held.
- [x] P9-4.4: Implement one OS pass, explicit split residual, one resource
  write, and post-continuity rederivation.
  Implemented and verified; the user explicitly accepts the leaf and its audit
  follow-up for commit. The
  [review](./phase-9-grcv4/tranche-4/P9-4.4-Review.md) and
  [execution record](./phase-9-grcv4/tranche-4/P9-4.4-ExecutionRecord.json) bind
  the preserved 187-method initial run and 188 passing follow-up methods
  (22 OS), in a reconstructed checkout with a fresh interpreter and changed
  hash seed. The follow-up catches endpoint-only path checking at both pass/step
  entry points, rejects before residual/resource work, and admits safe mixed
  paths; both underchecking and blanket-rejection mutations are detected.
  Production source is unchanged by the audit follow-up. Exact split-norm
  boundaries, interior selector crossings, corrected-current singularity,
  dense signed covariance, strict zero/subnormal/extreme durations, single-write
  ordering and final-C failure receive explicit pressure. The pipeline is
  provisional; live lifecycle commit/receipts remain with P9-4.5/4.6/4.7.
  Review, execution and run records retain their validation-time dispositions;
  this checklist and the commit record later user acceptance. Fifteen leaves
  and 27 paths are ready; P9-4.5 entry and runtime conformance stay held.
- [x] P9-4.5: Execute positive and atomic-negative `C_OS` vectors; keep full
  profile conformance pending lifecycle completion.
  Exercise the declared numerical reproducibility scope without hidden
  damping, regularization, pseudoinverse, fallback or charge repair (§7.4).
  Resolve complete poststate reference/pre-read current/domain admission before
  a commit-ready positive vector; success at consumed corrector geometry does
  not prove reference-restart admission. Verify the required check or justify
  its exact source-backed operation-boundary placement (complete-step 8–11).
  Keep final-C current out of a second geometry/residual/continuity pass.
  P9-4.5/P9-4.6 must bind actual request/ledger identities; inherited
  `next_inputs.operation_id`, `dt` and `receipt_ids` have no lifecycle authority.
  Implemented and verified in the bounded lifecycle ordinary-operation owner;
  explicitly accepted by the user for commit, including all six audit corrections.
  All 256 scoped methods pass with zero failures/errors/skips
  in a reconstructed checkout; exact source and live declared-method bindings hold. The [review](./phase-9-grcv4/tranche-4/P9-4.5-Review.md) maps
  actual commits and native/injected negative vectors to independent oracles.
  The [execution record](./phase-9-grcv4/tranche-4/P9-4.5-ExecutionRecord.json)
  preserves source-query meanings and the scoped reconstruction recipe.
  Review, execution and run records retain their validation-time dispositions;
  this checklist and the commit record the later acceptance. Programmer errors
  propagate atomically, typed nonfinite causes survive both final-C boundaries,
  and general cluster/conditioning branches and reference atomicity are pressured.
  Parent-receipt scope stays provisional for the later lineage owner.
  Sixteen leaves and 29 paths are dependency-ready; support sets remain empty.
- [x] P9-4.6: Execute the C_OS snapshot/load/reset/rebase and deep-copy/
  immutability slice; record the corresponding P9-7.1-C_OS evidence.
  Implemented and verified; the user authorized commit without a full audit.
  The original commit carried a deferred full audit, since supplied and closed
  by the combined independent review below. This mark records implementation
  and verification; subsequent corrections are now accepted. All 76 original
  focused methods passed
  after exact source reconstruction with zero failures/errors/skips. The
  [review](./phase-9-grcv4/tranche-4/P9-4.6-Review.md) maps actual restoration,
  reset/rebase/assignment, deep independence and edge-case pressure to tests.
  The [execution record](./phase-9-grcv4/tranche-4/P9-4.6-ExecutionRecord.json)
  binds portable reconstruction and compact source queries. P9-7.1-C_OS is an
  evidence alias, not another execution or whole-parent acceptance. The original
  entry exposed seventeen leaves and 29 paths; the accepted batch status follows
  the P9-4.7a/b task rows below.
  The bound review and execution record retain their verification-time status;
  this checklist records the later commit authorization.
- [x] Complete the deferred full independent audit of P9-4.6 and record its
  findings and closure. The combined audit explicitly closes all three findings;
  the user has accepted the corrections.

- [x] P9-4.7a: Execute atomic failed-step, receipt identity/ownership, and
  state-to-step-to-snapshot-to-restore-to-replay pressure for C_OS.
- [x] P9-4.7b: Execute the remaining applicable C_OS lifecycle product through
  early Tranche 7 children: mapped events, migration admission/rejection,
  reset after events/migrations, reference maps, and atomic readmission.
  Unsupported targets must reject; mandatory fixtures cannot be waived.
- [x] P9-4.8: Historical **HOLD P9-G2[C_OS]**; its
  [P9-4.8B successor](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json) is now
  accepted for the exact nominated scope. Preserve the original review and its evidence;
  discharge its obligations through P9-4.9.1–P9-4.9.3 and the successor P9-4.8B
  result, not by relabeling the historical HOLD. A_OS and `P9-G3[C_OS]` remain
  subject to separate continuation/entry review.
- [x] P9-4.9.1: Bounded public C_OS facade implementation accepted in `7905e7e`;
  14 focused tests passed at that subject. P9-4.9.1a supplies the subsequent
  abundance authority/projection; final product review is P9-4.9.3/P9-4.8B. See the
  [method/test mapping and ceilings](./phase-9-grcv4/tranche-4/P9-4.9.1-Review.md).
  The former interim `abundance` placeholder is superseded, not retroactively
  treated as accepted semantics in the original run. G2 remains held.
  Close the public C_OS common/V4 interface integration deferred
  from P9-2.6 and its consumers (`G2-COS-INTERFACE`). Implement the specified
  `GRCV4(GRCModel)` facade using the existing sole atomic publication owner.
  Use the initial P9-4.9.3 inventory and accepted P9-4.9.2 parent contract;
  combine related implementation and targeted tests. Map constructors/admission,
  parameter access, stage-tagged observables, common projections, strict/input
  request boundaries, `step_v4`/`run_v4`, common `step`/`run`, immutable default
  requests and typed missing-request failures to actual public-receiver tests.
  Cover restored instances, invalid and zero/subnormal/negative/extreme finite
  duration inputs, atomic failure, exact profile/model discovery and capability
  truth. Update stage-local no-facade assertions only with real integration;
  registered test targets do not establish accepted public support.
- [x] P9-4.9.1a: Resolve the narrow abundance-interface authority gap under
  `G2-COS-INTERFACE`, without reopening accepted constitutive/lifecycle results.
  The [source-checked proposal](./investigations/grc9v4-constitutive-design/decisions/P9AbundanceInterfaceAuthorityProposal.md)
  incorporates all three proposal-audit refinements: `observed_state_digest`,
  detector totality/conformance failure and release-bound definition identity.
  The user explicitly accepted this refined rule on 2026-09-09. Source admission,
  proposal/paper §14.2.1, V4 specs/release and bounded C_OS projection are implemented;
  11 focused tests passed. The [abundance review](./phase-9-grcv4/tranche-4/P9-4.9.1a-Review.md)
  records the validation-time scope and pending review. The user's subsequent
  commit instruction accepts this bounded implementation, not G2; preserve the
  original execution/review records and continue next with final P9-4.9.3.
  Distinguish theoretical identity multiplicity from an instantaneous diagnostic.
  Apply accepted family/capability ownership; numeric abundance remains unadmitted.
  Decide exact V4 key/availability/type/unavailable semantics and any admitted
  detector/stage, read-only status and consumer compatibility. The accepted exact
  unavailable triplet supersedes the interim null/status; no invented proxy.
  Record the bounded investigation decision, obtain acceptance, and propagate
  through claims/tooling and proposal/paper/V4 specs as applicable before changing
  runtime semantics. Keep legacy/common/V3 files unchanged; explain any V4
  inheritance exception explicitly in the V4 extension. Add only affected tests
  for availability, capability truth, stages, restoration and nonmutation.
  Keep final P9-4.9.3/P9-4.8B product review separate. Only the existing
  lifecycle/codec/test/packaged-release paths gain P9-4.9.1a permission; no extra gate.
- [x] P9-4.9.2: Resolve P9-2.4/P9-7.6's receipt-parent authority obligation.
  The user accepted the [uniform predecessor decision](./investigations/grc9v4-constitutive-design/decisions/P9ReceiptParentAuthorityProposal.md)
  on 2026-09-09; the 9 valid and 16 invalid symbolic controls are design evidence
  only. Source/debt admission, actual API/notebook/browser access and ordered
  proposal/paper/spec propagation are implemented. The C_OS runtime applies the
  rule and explicit versioned snapshot admission. See the
  [bounded implementation review](./phase-9-grcv4/tranche-4/P9-4.9.2-Review.md)
  for validation (140 runtime tests; 242 boundary-pressure cases). Implementation
  was accepted by the user's commit instruction in `d8f26d9`; the original
  validation-time record remains unchanged. Public-facade, fixture and G2 review
  remain separate.
  Own `G2-COS-PARENTS`. Verify accepted provenance with the forensic API;
  ordered source/target profile identities and acyclic content hashing do not
  determine parent scope/order.
  Review the missing contract in the investigation/design, propagate accepted
  authority through proposal/paper and V4 specs, and use an admitted successor
  release if required before claiming runtime conformance. Define roots,
  historical/intra-commit scope, ordering and duplicates across ordinary,
  administrative and crossing operations. Accept this authority decision before
  changing the corresponding behavior, then align implementation and tests
  alongside the facade and demonstrated gap corrections,
  including valid controls, missing/foreign/forward/self/cyclic references,
  duplicates/reordering, coherent rehashes and snapshot/restoration. Preserve
  lawful unreceipted assignment and distinguish future replay from authenticated
  history. Discharge only the reviewed C_OS scope of the parent obligation.
- [x] P9-4.9.3: Reconcile the 33-case catalog index and exact semantic vectors
  into the full fixture product for a nonempty nominated complete-profile set
  (`G2-COS-FIXTURES`).
  Accepted by the user's commit instruction in `c01526c`; see the
  [final reconciliation](./phase-9-grcv4/tranche-4/P9-4.9.3-Review.md): one exact
  nominated complete-profile product, 33 catalog rows and two exact vectors,
  with distinct control/target identities and whole input/output records.
  The original inventory and accepted runs remain historical. This completion
  mark is not itself G2 acceptance; the separate accepted P9-4.8B decision
  is recorded below.
  Begin with a bounded gap list: requirement, existing usable evidence/limits,
  actual remaining change/test and owner. This is the first closure activity,
  not another audit framework or a reason to repeat suites. Final reconciliation
  follows the integrated P9-4.9.1/P9-4.9.2 implementation, accepted P9-4.9.1a
  interface semantics and targeted tests.
  Bind resolved parameters, graph/reference/context/domain, ordered crossing
  identities and required per-execution result fields. Reuse accepted evidence
  with its actual source/environment and limits; keep reruns distinct. Resolve
  `COMMON-STALE-CACHE` using the existing second-beat/no-cache/stage evidence
  before adding tests, and establish exact-input/layer credit for
  `SEMANTIC-REJECT-RESOURCE-TRANSFORM-DIMENSIONS`, not schema-only or synthetic
  shape-test credit. Retain the corrected exact mapped-event execution and all
  seven migration-class dispositions. Convert demonstrated gaps into tests;
  use independently justified expectations. Reconcile all seven schema/semantic
  negatives and algebra/identity/result vectors without promoting foundation
  credit to live transitions or copying historical holds as current failures.
  Retain separate history channels, live/reset and reset-only failure coverage,
  mixed crossings and charge/increment edge-case evidence. Verify affected
  shared/integration paths against the final facade and parent
  contract. Preserve explicit unsupported/deferred scopes without waiving a
  mandatory C_OS case or importing unrelated A/realization/GRC9 blockers.
- [x] P9-4.8B: Review the three work packages together once the integrated result
  and exact-profile evidence are ready; no three preceding full acceptance
  reviews. Issue the successor full `P9-G2[C_OS]` review using the single current
  verification path, bound to current authority, release, source and execution
  product. Reuse the final integrated run rather than automatically rerunning it
  for review. Preserve the original P9-4.8 draft/checker and runs for historical
  reconstruction. Recheck the implementation boundary, affected
  tool surfaces and misleading-acceptance rejection controls: missing/duplicate
  rows, family/empty-set
  substitution, unreviewed support, borrowed mapped identity and erased parent
  debt; include a valid complete-review control as well. Record PASS, HOLD
  or rejection; a checker pass is not user acceptance. Any unresolved blocker
  keeps G2 closed and returns to its owning closure child. Only an accepted
  positive review updates exact support/discovery and gate/checklist states;
  alias its result through P9-7.7-C_OS without duplicate credit. A_OS and G3
  require separate continuation/entry review; other gates do not open implicitly.
  - [x] Integrated review performed: [PASS proposal](./phase-9-grcv4/tranche-4/P9-4.8B-Review.md)
    and [exact bound record](./phase-9-grcv4/tranche-4/P9-4.8B-GateReview.json),
    using the retained 22-test run, 33-row product and current typed authority.
    Valid PASS/HOLD controls and 13 rejection controls, current boundary and
    scoped API/notebook/HTTP/browser-validator checks; no numerical rerun.
  - [x] User acceptance on 2026-09-09 and exact support/discovery propagation:
    [explicit G2 acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json). Tranche 4 is closed; only the nominated complete C_OS profile
    is accepted. G3, other profiles and specialization remain closed.
    Registry, API, notebook and browser project the same singleton; local
    migration targets are not global accepted support.
  - [x] Final corrected verification continuation completed on 2026-09-09:
    [portable completion record](./phase-9-grcv4/tranche-4/P9-4.8B-VerificationFollowup.json).
    Permission pressure **248/248**, surface checks with **32/32** browser-validator
    tests and exact API/notebook agreement, and the accepted G2 review checker
    passed. Clean and modified setup-commit alternatives both reach the intended
    committed frozen-file rejection; ancestry and export controls remain active.
    The record binds the execution Git subject plus exact correction and verifies
    reconstruction. Later publication metadata receives a separate boundary check.
    Previously passed historical/authority stages and original numerical captures
    are reused; the earlier interrupted invocation earns no completion credit.
    Historical P9-4.8 HOLD, accepted singleton scope and closed G3 are unchanged.

P9-4.9 is an aggregate of work packages, not new gates or separate full-review
cycles. Execution order is P9-4.9.3 inventory, P9-4.9.2 authority resolution,
combined implementation/targeted tests, final P9-4.9.3 reconciliation, then one
integrated P9-4.8B G2 review. Run necessary integrated checks when the result is
stable; repeat only checks affected by later corrections. These planning rows
grant no runtime authorization. Register authorized IDs/dependencies/path owners
through the existing boundary/work manifest, batching related work where useful;
update affected tool exposure/tests without adding an authorization framework.
Maintain one current verification path as corrections land, with G2 held until
accepted at P9-4.8B. Keep the original checker for historical reconstruction
only, not as a second evolving acceptance system or a ban on later source.
The [plan](./Phase-9-GRCV4-ImplementationPlan.md#p9-49-closure-of-the-p9-48-obligations)
defines the source mapping and exit criteria; the original P9-4.8 records remain
the starting evidence, not a claim that every apparent fixture gap is a defect.

`P9-4.7` is the parent of P9-4.7a and P9-4.7b. The early state/receipt/replay
cycle supplies evidence; P9-4.8 grants no reduced form of generic conformance.

P9-4.7 batch accepted: the user authorized acceptance of P9-4.6, P9-4.7a and
P9-4.7b after closing the combined audit findings. The
[batch record](./phase-9-grcv4/tranche-4/P9-4.7ab-AuthorizationRecord.json)
records that disposition. The [P9-4.6 follow-up](./phase-9-grcv4/tranche-4/P9-4.6-AuditFollowup.md)
closes the deferred audit without rewriting its original records.

The [P9-4.7b review](./phase-9-grcv4/tranche-4/P9-4.7b-Review.md) records the
accepted edge/K4 correction, explicit solver tolerances and orientation/reference
preimages. The successor specification release and packaged assets are active;
the exact published mandatory request/event identity passes in the retained
50-method replay. The earlier 135- and 35-method runs remain reproducible through
Git plus compact reverse patches. Mixed lifecycle pressure includes returning
to the original graph/profile and restoring its archive. P9-7.2a/b and 7.3–7.6
have scoped C_OS evidence reconciled; P9-7.1-C_OS retains only bounded snapshot/
continuation credit. Broader GRC9/reference-carrier correction and generic
parent-DAG conformance remain outside these accepted leaves.

Historical P9-4.8 snapshot: draft **HOLD P9-G2[C_OS]**, pending fixture
reconciliation and user review at that stage. Its
[continuation handoff](./phase-9-grcv4/tranche-4/P9-4.8-Handoff.md) is historical.
The successor [P9-4.8B review](./phase-9-grcv4/tranche-4/P9-4.8B-Review.md)
is now covered by [explicit G2 acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json) for its one exact C_OS nomination.
The [gate review](./phase-9-grcv4/tranche-4/P9-4.8-Review.md) and
[33-case evidence index](./phase-9-grcv4/tranche-4/P9-4.8-GateReview.json)
record unfinished public-interface integration and deferred receipt-parent
authority. Fixture reconciliation is P9-4.8 work; its absent consolidated mapping
is not proof of missing behavior. Reassess the stale-cache case using the existing
second-beat reconstruction test before claiming a new gap. The corrected mandatory
mapped-event execution retains its scoped credit. A_OS and P9-G3[C_OS] stay
behind G2. That snapshot had empty runtime support and 26 leaves / 29 eligible
paths. Current support is the user-accepted exact C_OS singleton; closure work
still has 30 leaves / 29 paths. P9-4.8 remains historical; P9-4.8B acceptance
updates discovery and status without authorizing new runtime leaves.

## Tranche 5. Candidate A and A_OS

**Tranche 5 accepted by the user on 2026-09-10.** P9-5.1–P9-5.4 and the four
repository-regression test and harness corrections are complete. The
[handoff](./Phase-9-GRCV4-Handoff.md) records the original full-suite result,
focused correction checks, and remaining validation limits. Live A lifecycle,
authenticated initializer-current provenance, formation, and A_OS G2 remain
with their owning leaves; this acceptance grants no new execution permission.

- [x] P9-5.1: Implement exact history-free initialization and positive
  retained-mobility authority. [Review and source/test map](./phase-9-grcv4/tranche-5/P9-5.1-Review.md)
  and [audit follow-up manifest](./phase-9-grcv4/tranche-5/P9-5.1-AuditFollowup.json).
  Implementation/verification and bounded independent audit corrections are
  complete; **accepted by the user on 2026-09-09**. Target differential/reference-current
  inputs and current/reset
  construction are explicit. Whole-target current/lifecycle admission, formation
  evidence and A_OS G2 remain with their owning leaves. Only P9-5.1 is newly
  execution-permitted; this scoped acceptance does not open P9-5.2 or accept A_OS G2.
- [x] P9-5.2: Implement log-space writing, direct current, and Read-Back with
  no same-beat reading of newly written retained state. Pressure
  `(W_A-W_hat_A)/(W_A+W_hat_A)` at large finite positive operands without
  denominator-overflow artifacts. [Review/source-test map](./phase-9-grcv4/tranche-5/P9-5.2-Review.md)
  and [audit follow-up](./phase-9-grcv4/tranche-5/P9-5.2-AuditFollowup.json):
  65 focused methods and three supplied audit regressions pass. Audit F1/F2
  are corrected: exact potential-decomposition diagnostics admit finite
  cancellation beyond component binary64 range, and the complete Decimal
  context is isolated from caller defaults. **Accepted by the user on
  2026-09-09**; P9-5.3 is authorized next.
  These are provisional
  current/writer primitives; complete A_OS integration remains in P9-5.3.
- [x] P9-5.3: Execute independent Candidate A numerical/stage/control vectors
  and the `A_OS` step cases. [Review/source-test map](./phase-9-grcv4/tranche-5/P9-5.3-Review.md)
  and [audit follow-up](./phase-9-grcv4/tranche-5/P9-5.3-AuditFollowup.json):
  68 focused methods and four supplied audit regressions pass, including one-pass/fresh-corrector staging, exact
  split boundaries, one continuity/writer, independent scalar and multigraph
  expectations, controls, clocks and zero duration. Numerical readmission
  rejects both consumed-geometry and reference-only post-writer singularities.
  Audit F1/F2 are corrected: an unavailable raw split display cannot veto
  exact admission; shared numeric failures retain the A_OS stage and cause.
  Both candidates and signs, display/tolerance boundaries and the existing C
  publication consumer are covered. The original execution remains unchanged.
  **Accepted by the user on 2026-09-09**. The later A_OS
  lifecycle child must prove live atomic rollback and receipt provenance for
  these retained witnesses; provisional input preservation does not discharge
  that obligation. P9-5.4 is authorized next.
- [x] P9-5.4: Preserve separate initialization/formation/history claims and
  keep lifecycle-dependent conformance pending. Before complete initializer
  conformance, the A lifecycle owner must establish the admitted reference-flux
  source, bind its actual target stage, exclude discarded-history dependence,
  and perform separate target-current and lifecycle readmission. P9-5.1's
  explicit operand and pair construction do not discharge these obligations.
  [Review and claim map](./phase-9-grcv4/tranche-5/P9-5.4-Review.md) and
  [execution manifest](./phase-9-grcv4/tranche-5/P9-5.4-ExecutionRecord.json):
  13 focused methods verify existing claim guards and three new counterexamples
  (reset-only current singularity after positive initialization, identical
  initializer/writer values, and reference neutrality without a W write).
  Twelve claim boundaries and seven source-contract queries retain formation,
  retention, release, branch, history-transport and lifecycle/G2 obligations.
  Numerical runtime remains unchanged. **Independent audit passed the substantive
  scope**; its squared-current formula correction and provenance/receipt
  clarifications are applied. The [audit follow-up](./phase-9-grcv4/tranche-5/P9-5.4-AuditFollowup.json)
  adds signed non-unit current pressure and a same-charge comparison while
  preserving the original execution record. **Accepted by the user on 2026-09-09**;
  P9-7.1-A_OS is not yet execution-permitted.

## Tranche 6. CI, PC, CI+PC, and RG2b

P9-6.1–P9-6.4 are parent registers. Their candidate children carry numerical
and failure oracles with each implementation; P9-6.1c, P9-6.2c and P9-6.3c audit
shared realization behavior once their reviewed inputs are available. RG2b
adds generalization at P9-6.4c before its shared audit at P9-6.4d. Each profile
also needs applicable shared-contract evidence before its G2 review, but a
pending sibling implementation cannot substitute for or impose unrelated
coverage. Record bounded shared-audit results for the available profile set.

The 2026-09-10 user-directed split moves the former unexecuted P9-6.4c audit
to P9-6.4d. Historical crosswalk/debt references and the a/b review/execution
record use the former numbering; their shared-audit c means d under this
amendment. No historical execution, scientific authority or acceptance changes.

- [x] P9-6.1a: Implement and verify C_CI's selected bounded root and exact
  failure/domain rules.
  Accepted by the user on 2026-09-10, with a separate C_CI PASS after F1/F2
  corrections: analytic residual enclosure and consumed-root failure staging. The
  [shared review/source map](./phase-9-grcv4/tranche-6/P9-6.1ab-Review.md)
  declares the concrete whole-ball single-stratum scope and its limitations.
- [x] P9-6.1b: Implement and verify A_CI's selected bounded root and exact
  failure/domain rules.
  Implemented in the same batch with independent A oracles and refreshed
  in-root conductance, one selected-current continuity/write, and separate
  reset/final-root admission. F1–F3 corrections include analytic residual
  enclosure, failure staging and zero-duration writer-policy admission. Accepted
  by the user on 2026-09-10, with a separate A_CI PASS. The
  [audit followup](./phase-9-grcv4/tranche-6/P9-6.1ab-AuditFollowup.json)
  keeps separate child results and reconstructs the original execution subject.
- [x] P9-6.1c: Audit shared CI realization contracts and reconcile independent
  candidate evidence; record exactly which profiles the audit covers.
  Accepted by the user for A_CI and C_CI on 2026-09-10; scientific verdict
  PASS. The [reconciliation review](./phase-9-grcv4/tranche-6/P9-6.1c-Review.md)
  reuses the combined audit and 48-method child run, reviews the corrected
  enclosure derivation and records four new focused pressure methods. No
  runtime correction or expanded CI support is claimed.
- [x] P9-6.2a: Implement and verify C_PC old-history reads, one scalar-ZOH
  write, declared tau, and state/reset ownership.
  Accepted by the user on 2026-09-10 after correction and P9-6.2c review;
  scientific verdict PASS. Computed zero is canonicalized in the shared writer and C source;
  exact selector-cutoff failure is attributed to domain admission before current.
  The [shared review](./phase-9-grcv4/tranche-6/P9-6.2ab-Review.md) preserves
  the bounded whole-chart and provisional ownership scope.
- [x] P9-6.2b: Implement and verify A_PC's candidate-specific PC contract.
  Accepted by the user on 2026-09-10 in the same corrected/reviewed batch;
  scientific verdict PASS. A's exponent certificate respects repeated loop endpoints;
  the G_W law and W writer remain unchanged. Old Z is preserved through the
  refreshed A writer until the single carrier update.
- [x] P9-6.2c: Audit shared PC behavior and independent history/state coverage.
  Completed at the user's request together with the a/b external audit, covering
  A_PC and C_PC; accepted by the user on 2026-09-10 with scientific verdict PASS. The
  [combined followup](./phase-9-grcv4/tranche-6/P9-6.2abc-AuditFollowup.json)
  records 48 fresh PC methods (32 original, eight audit regressions, eight
  additional pressure methods), reuses the unchanged 80 A/OS/CI regressions,
  and restores the original source hashes without a source archive.
  No PC lifecycle, formation provenance, matched-forcing contraction certificate,
  endpoint witness, G2 or G3 is inferred from this reconciliation.
- [x] P9-6.3a: Implement and verify C_CI_PC same-source composition and gain two.
  Accepted by the user on 2026-09-10; independent audit and bounded review PASS.
  The [shared review](./phase-9-grcv4/tranche-6/P9-6.3ab-Review.md) covers the
  entire B_2R image, uniform source/contraction bounds, one C selector stratum,
  complete trial-chain refresh and the exact same-root carrier source.
- [x] P9-6.3b: Implement and verify A_CI_PC same-source composition and gain two.
  Accepted by the user on 2026-09-10; independent audit and bounded review PASS.
  The existing CI/PC validators are shared. A's refreshed
  W writer preserves old Z until the single held-source carrier update.
  The [run record](./phase-9-grcv4/tranche-6/P9-6.3ab-ExecutionRecord.json)
  records 32 composition tests and 143 affected regressions. No composite
  lifecycle, formation, endpoint, G2 or G3 is inferred.
- [x] P9-6.3c: Audit shared CI+PC composition against the exact root/carrier
  source and candidate-specific evidence.
  Accepted by the user on 2026-09-10 with bounded numerical PASS. The
  [followup](./phase-9-grcv4/tranche-6/P9-6.3abc-AuditFollowup.json) closes the
  native-execution and record-integrity gaps: four audit proposals plus four
  additional methods pass. Numerical code and original test/oracle bytes are
  unchanged, so the 175 original passes are reused. The shared review records
  CI/PC ownership, cross-module coupling and the separate lifecycle ceiling.
- [x] P9-6.4a: Bind, certify, and verify the admitted C_RG2b evaluator and
  Lipschitz section; reject unsupported classical derivative claims.
  Implemented, verified and externally reviewed for a frozen two-vertex/one-edge
  completion; bounded scientific PASS, accepted by the user on 2026-09-10. The
  [shared review](./phase-9-grcv4/tranche-6/P9-6.4ab-Review.md) derives candidate-specific
  inverse, value/Lipschitz, contraction, containment and finite-error bounds.
  C retains its selector, retained Hodge and filtered response. This is the
  scalar reference foundation; generalization is owned by P9-6.4c and the
  combined audit by P9-6.4d. Lifecycle/G2 remain separate work.
- [x] P9-6.4b: Bind, certify, and verify A_RG2b independently.
  Implemented, verified and externally reviewed on the corresponding bounded A
  domain; bounded scientific PASS, accepted by the user on 2026-09-10. A geometry feedback and the refreshed W
  writer remain active; descriptor contrast vanishes structurally on this graph.
  The [single run record](./phase-9-grcv4/tranche-6/P9-6.4ab-ExecutionRecord.json)
  binds 29 RG2b methods and 52 affected A regressions, including independent
  section/preimage/writer oracles and nonzero-coupling separation from CI.
  The supplied a/b HOLD is corrected in the new c record: native reset/final
  section checks, preserved root disposition, and clock/index admission ordering.
  The original run is historical; generalization and shared audit are c/d.
- [x] P9-6.4c: Generalize the A_RG2b and C_RG2b evaluator and certification
  from the two-vertex/one-edge foundations to variable-size finite graphs.
  Implemented and reviewed with bounded scientific PASS; accepted by the user on 2026-09-10.
  The [graph review](./phase-9-grcv4/tranche-6/P9-6.4c-Review.md) and
  [current run](./phase-9-grcv4/tranche-6/P9-6.4c-ExecutionRecord.json) include the
  a/b audit corrections. The seven proposals pass natively after reproducing
  12 original failed assertions; three additional scalar methods pressure the
  neighboring boundaries. The following scope is required for completion.
  Reuse the scalar oracles and common owners,
  while reporting separate A and C outcomes. Bind a graph-general frozen
  completion, matrix error norms, finite deterministic evaluation and computed
  inverse, value/Lipschitz self-map, contraction and containment certificates.
  Arbitrary tiny-graph caps must disappear; scientific admission conditions
  remain explicit, and removing the existing guard alone is insufficient.
  Exercise nonzero A descriptor contrast, C retained-Hodge/filtering and
  noncommuting matrix behavior, paths/cycles/branching and high-degree graphs,
  parallel edges, loops, disconnected components and isolates where admitted
  by the source contracts. Include relabeling/reorientation, certificate
  boundaries, precision exhaustion, independent reset admission, replay and
  repeated ordinary beats. Demonstrate correct nonzero-coupling execution on
  larger graphs at several declared sizes, with independently justified
  expectations and exact reconstruction commands; tiny fixtures alone cannot
  complete this leaf. Failures to admit a case need a scientific or numerical
  reason, not a graph-size shortcut. Correctness and ability to execute larger
  graphs are required; speed and performance optimization are deferred.
  The 32-vertex campaign is opt-in on explicit request; default verification
  records its intentional skip separately and does not imply completion at that size.
  Preserve the Lipschitz-only, completion-relative claim and distinguish
  one-beat containment from indefinite invariance of the entry chart.
- [x] P9-6.4d: Audit the RG2b evaluator/certification scope and regularity
  ceiling for the exact reviewed profiles (formerly P9-6.4c).
  Reviewed and verified: **bounded scientific PASS for A_RG2b and C_RG2b**;
  accepted by the user on 2026-09-10. The [d followup](./phase-9-grcv4/tranche-6/P9-6.4d-AuditFollowup.json)
  closes the audit's earlier pending-record observation against the completed
  55-pass/one-optional-skip native campaign. Three new regressions pass for
  large-Hodge representation (both signs and zero gain), exact rational
  noncommuting current/source errors and dimensional Frobenius rounding.
  Runtime sources and the original methods are unchanged; the prior runs are
  reused without another full campaign. External isolated pressure remains
  attributed as such. No open numerical leaf blocker remains.
  Reconcile their evidence in one shared audit with separate A/C verdicts;
  challenge graph coverage, complete candidate behavior and finite error
  certificates. Preserve the one-beat containment and Lipschitz-only ceilings.
  Generalized numerical acceptance does not grant lifecycle, topology-event,
  C1-section or G2/G3 claims.
- [x] P9-6.5: Reconcile concrete realization results profile-by-profile,
  route each ready profile to lifecycle/G2 review, and retain pending or
  deferred siblings. Tranche-wide completion is not an entry condition.
  Accepted by the user on 2026-09-10; bounded review PASS. Tranche 6 is accepted
  and closed in its declared scope. The [review](./phase-9-grcv4/tranche-6/P9-6.5-Review.md) and
  [routing record](./phase-9-grcv4/tranche-6/P9-6.5-RealizationRouting.json)
  bind all eight accepted numerical candidate results and shared audits,
  reproducible exact seeds, independent lifecycle/conformance routes and both
  P9-6.5 forward obligations. The generalized RG2b result remains distinct from
  its scalar foundation. Lifecycle/G2, scientific debts and the optional
  32-vertex campaign retain their limits; public support remains exact C_OS.
  That handoff suggested P9-7.1-A_OS first. The user's later full-parent request
  supersedes that scheduling hint; see the ten-child batch below.

## Tranche 7. Generic lifecycle generalization and P9-G2

The [P9-1.4 child register](./phase-9-grcv4/tranche-1/P9-1.4-SupportAndDependencies.json)
now declares exact C_OS and A_OS lifecycle children, source/target crossing
scopes, evidence aliases and dependencies. P9-7.1-C_OS and the early C_OS
P9-7.2a/b–P9-7.6 children have scoped evidence accepted with the P9-4.6/4.7 batch;
its full audit findings are closed. Generic parent-reference conformance remains
open across other profiles; the accepted P9-4.9.2 authority and bounded internal
C_OS implementation are recorded in its linked review. P9-7.1 is accepted;
P9-7.2a is accepted and closed within the reviewed scope below. Generic event and wider
conformance children remain pending. P9-7.7-C_OS aliases the
[P9-4.8B exact-scope acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json),
with no duplicate execution credit. The original
P9-4.8 HOLD and historical child register remain unchanged.
Parent completion remains scoped to reviewed child evidence.

The registered C_OS/A_OS migration/event and P9-7.3–P9-7.6 children also own
§7.5: deliberately distinct live/reset prestates, independently calculated
transported/readmitted targets, reset after the operation, persistent ledger
versus emitted delta, and complete scientific/lifecycle rollback. Include a
reset-only target admission failure even when the live target would pass.

Instantiate profile-specific children (for example `P9-7.1-C_OS`) and exact
source/target migration or event children before execution. C_OS children
run during Tranche 4; later work generalizes their machinery and reuses their
evidence without claiming all-profile coverage. A_OS and each later profile
may reach G2 without waiting for all Tranche 6 realizations.

- [x] P9-7.1: Execute save/load/replay, reset, rebase, and independent
  duplication with canonical authority and receipt identities.
  Implemented and verified on `impl/phase-9-grcv4-tranche-7`: 26 focused tests
  passed, with scoped source/record and API/notebook/browser checks. These marks
  record completed execution, not user acceptance or wider G2. See the
  [concrete lifecycle record](./phase-9-grcv4/tranche-7/P9-7.1-Lifecycle.json).
  Later disposition: **accepted by the user on 2026-09-11**, including the
  audit corrections, through commit authorization. This accepts the bounded
  ten-child lifecycle batch, not new G2/G3 or migration/event scope. Original
  execution records retain their pre-acceptance flags and exact identities.
  - [x] P9-7.1-C_OS: reuse the accepted exact-scope lifecycle/G2 evidence;
    current shared-owner compatibility is checked without duplicate gate credit.
  - [x] P9-7.1-A_OS: explicit retained-W/backend lifecycle.
  - [x] P9-7.1-A_CI: retained-W, newly selected CI root on readmission.
  - [x] P9-7.1-C_CI: derived C sector, newly selected CI root on readmission.
  - [x] P9-7.1-A_RG2b: retained-W, fresh completion-relative graph section.
  - [x] P9-7.1-C_RG2b: derived C sector, fresh completion-relative graph section.
  - [x] P9-7.1-A_PC: independently retained W and Z, geometry rebuilt from Z.
  - [x] P9-7.1-C_PC: independently retained Z, geometry rebuilt from Z.
  - [x] P9-7.1-A_CI_PC: independent W/Z and newly selected coupled root.
  - [x] P9-7.1-C_CI_PC: retained Z and newly selected coupled root.
  Distinct live/reset authority, content-bound receipts, reset-only failure,
  canonical replay and atomic rollback are required per new concrete child.
  These checks do not close migration/events, formation, wider G2 or G3.
  - [x] Audit follow-up: verify RG2b K state readmission independently of
    K_minus step entry, current/reset rejection outside K, core-state lifecycle
    continuation and next-beat atomic rejection.
  - [x] Audit follow-up: reject incoherent zero-step and frozen-beat history;
    preserve lawful unreceipted assignment and rounded large-clock advancement.
  - [x] Audit follow-up: correct non-OS stage labels and verify the native
    A post-writer singularity against a populated immutable publication.
  - [x] Retain a separate source-bound 15-method correction capture and exact
    original source recovery; refresh the read-only successor without rerunning
    the full original campaign or granting acceptance/support.
    All 15 methods passed without failures/errors/skips; see the
    [follow-up](./phase-9-grcv4/tranche-7/P9-7.1-AuditFollowup.json).
- [x] P9-7.2a: Execute required profile migration classes over current and
  reset state, independently by source/target identities and failure surface.
  A decoded P9-2.3 declaration is not migration admission: test unresolved
  history/initializers, unsupported targets and missing mappings at the real
  consumer, including separate candidate/carrier channel decisions.
  The user accepted aggregate seven-class closure on 2026-09-11. The
  [historical review](./phase-9-grcv4/tranche-7/P9-7.2a-Review.md) binds the
  six-class fixtures accepted at `924fca9`; the
  [current acceptance](./phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntimeReview.md)
  additionally binds positive C→A through all five A targets and the final
  codec correction. No Cartesian family-wide or new G2 support is inferred.
  Historical capture-time flags remain unchanged.

  - [x] P9-7.2a-A_NH_NH: A_OS → A_CI.
  - [x] P9-7.2a-C_NH_NH: C_OS → C_CI.
  - [x] P9-7.2a-A_NH_PC: A_CI → A_PC, separate preserved W / zero Z.
  - [x] P9-7.2a-C_NH_PC: C_CI → C_PC, zero Z.
  - [x] P9-7.2a-A_PC_NH: A_PC → A_RG2b, archive/drop Z.
  - [x] P9-7.2a-C_PC_NH: C_PC → C_RG2b, archive/drop Z.
  - [x] P9-7.2a-A_PC_CIPC: A_PC → A_CI_PC, exact carrier preservation.
  - [x] P9-7.2a-C_PC_CIPC: C_PC → C_CI_PC, exact carrier preservation.
  - [x] P9-7.2a-A_CIPC_PC: A_CI_PC → A_PC, exact carrier preservation.
  - [x] P9-7.2a-C_CIPC_PC: C_CI_PC → C_PC, exact carrier preservation.
  - [x] P9-7.2a-A_C_NH: A_OS → C_OS, explicit candidate-history loss.
  - [x] P9-7.2a-A_C_PC: A_PC → C_PC, W loss and whole-carrier reset.
  - [x] P9-7.2a-A_C_DROP: A_CI_PC → C_CI, separate W/Z losses.
  - [x] P9-7.2a-C_TO_A_UNRESOLVED: native C_OS → A_OS and C_PC → A_PC
    rejection pressure; a negative result does not discharge positive migration.
  - [x] Verify exact current/reset maps, source/target readmission, reset and
    ordinary continuation, fresh load/replay, independent duplication, seeded
    receipt parent/delta, separate history channels and immutable publication.
  - [x] Pressure unlisted/stale requests, substituted history/initializer,
    exact carrier-contract mismatches, reset-only failure, missing A backend,
    injected early target-geometry failure,
    core-only RG2b readmission, archive tampering and late publication faults.
  - [x] Read-only successor and actual API/notebook/browser checks; retain
    accepted 7.1 sources/records in Git and exact C_OS-only G2 discovery.
    The source-bound capture passed 25/25; five evidence-mutation controls,
    35 browser-validator tests and actual API/notebook/browser checks passed.
  - [x] Audit F1: propagate unexpected mapper/source/target ValueError and
    V4IdentityError unchanged; retain typed declaration/backend/domain failures
    and whole-publication atomicity without message matching.
  - [x] Audit F2: bind known live/archived and repeated unknown scientific
    identities to consistent graph/model/authority/reset commitments and clocks
    in both restoration and prospective publication; preserve lawful assignment
    and the external-history trust ceiling.
  - [x] Audit additional pressure: switch to a distinct A backend, restore both
    archived recipes, reject an omitted old recipe and execute continuation.
  - [x] Preserve original evidence and exact source recovery; verify the separate
    correction capture: 17/17 passed. At that stage, aggregate 7.2 closure and
    positive C→A were deferred; their later completion is recorded below.
  - [x] Prepare the bounded [target-only reference-pass proposal](./investigations/grc9v4-constitutive-design/decisions/P9CandidateAInitializerReferencePassProposal.md)
    with source/choice separation, fixed target differential data, one bootstrap
    pass, full conductance channels, numerical/floor/range rules, versioned
    identity and independent current/reset lifecycle obligations. This initial
    drafting step did not itself create accepted authority.
  - [x] Incorporate the supplied design-review PASS: clarify unit-vertex pairing
    and boundary/normalization scope; retain auxiliary-singular/final-regular
    pressure, acyclic policy/profile/invocation identity, genuine reset-only
    failures, fixed target charts and archived-versus-evolved W restoration.
    One native primitive probe confirms the rounded fixture, not migration.
  - [x] User accepted the clarified initializer definition by requesting its
    commit and continuation on 2026-09-11. Producer choice is resolved; keep
    propagation/runtime verification distinct from this design acceptance.
  - [x] Admit the bounded successor/debt/claim through the existing side tool;
    preserve historical classifications and expose real API/notebook/browser
    traces with design-versus-implementation status. See the
    [admission review](./phase-9-grcv4/tranche-7/P9-7.2a-InitializerAuthority.md).
    Preserve the original 25/17-test subjects; no new migration execution.
  - [x] Update GRCV4-proposal §12.6 and the related lifecycle, optional-claim and
    appendix crosswalks from admitted typed authority. Separate the review draft
    from historical release inputs in current validators; keep paper/specs,
    runtime assets and original executions unchanged. See the
    [review candidate](./phase-9-grcv4/tranche-7/P9-7.2a-ProposalReview.md).
  - [x] User accepted that exact proposal revision through the commit-and-continue
    request on 2026-09-11, authorizing paper propagation next.
  - [x] Propagate the accepted revision to the paper, preserving paper-specific
    corrections and historical source/evidence identities. Check exact transfer
    of six sections, numerical/claim boundaries and the separate paper candidate.
    See the [paper review](./phase-9-grcv4/tranche-7/P9-7.2a-PaperReview.md).
  - [x] User accepted the paper revision through the commit-and-continue request
    on 2026-09-11, authorizing specification propagation next.
  - [x] Prepare the V4 specification supplement, closed policy/construction/pair
    schema, receipt/snapshot linkage and release applicability from accepted
    paper `7d45218`. Add wire vectors and focused negative checks; no old-family
    change or automatic GRC9V3 initializer binding. See the
    [spec review](./phase-9-grcv4/tranche-7/P9-7.2a-SpecificationReview.md).
  - [x] User accepted the specification through the commit-and-implement request.
  - [x] Bind its own successor release and explicit codec applicability before
    producer execution.
  - [x] Implement one graph-generic target-current producer and C→A map; use
    separate current/reset inputs, directional W/Z policies and existing target
    admission/publication owners. Preserve the old explicit-flux constructor's
    identity and evidence; new behavior requires the admitted policy/release.
  - [x] Execute focused nontrivial active-channel/signed-gamma, graph/order,
    floor/rounding/range and source-history-independence controls; positive C→A
    through all five A realization paths on declared admitted fixtures.
    Include the auxiliary-singularity regression at the actual producer, reject
    output-dependent target chart repair, and check identical current/reset
    operands give identical values despite different construction-record roles.
    The new bounded roster is 18 initializer methods plus seven compatibility
    guards, separate from the historical 25/17-test subjects. See the
    [runtime review](./phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntimeReview.md).
  - [x] Verify distinct current/reset outputs, reset-only failures, full rollback,
    F1/F2 consistency, restoration/reset/duplication and admitted continuation;
    bind new exact evidence in the existing scoped verifier and affected UX.
    The retained 25/25 capture, 17 document/release/spec checks and four read-only
    runtime-evidence/UX methods pass; browser validation includes four rehashed
    overclaim/permission controls. No full historical campaign was rerun.
  - [x] User accepted the initializer implementation through the explicit
    accept-and-commit request on 2026-09-11. The runtime review records that
    decision; execution-time review/support flags remain historical.
  - [x] Review all seven migration classes for aggregate P9-7.2a closure. Reuse
    unchanged 25/17-test evidence, but do not count negative C→A pressure as
    positive completion or grant unrelated G2/G3/event support.
    Review passed; the codec-reference finding is corrected with focused
    regression coverage. The user accepted and closed P9-7.2a through the
    explicit accept-and-commit request on 2026-09-11.
- [x] P9-7.2b: Execute caller-mapped generic topology events over current and
  reset state, with their own map/identity/admission failure evidence.
  - [x] Prepare the additive [event contract extension](./phase-9-grcv4/tranche-7/P9-7.2b-ContractExtension.md):
    separate candidate/carrier losses, mapped current/reset initializer inputs,
    event receipt v2 and new snapshot applicability; preserve accepted 7.2a.
  - [x] User accepted the corrected fallback binding and separate representation
    operation contract/scope on 2026-09-12 through “accept and commit”.
  - [x] Package/admit the joint contract release through its explicit wire
    decoder; predecessor loaders and model lifecycle dispatch remain unchanged.
    Package admission is not runtime execution or aggregate closure.
    Include mixed-version archive declarations and unknown-release dispatch;
    execute the mixed-operation restore/evolve/reset pressure with the runtime.
  - [x] Instantiate the finite event/representation runtime children and
    failure cases in the [runtime review](./phase-9-grcv4/tranche-7/P9-7.2b-RuntimeReview.md);
    preserve old C_OS evidence and distinguish the new run.
  - [x] Include the pure-representation coordinate law as a separate current
    operation contract, not the lossy fallback or a general topology map.
  - [x] Complete its closed request/receipt/archive/release binding, including
    declared correspondence and coordinate-sensitive identity handling.
  - [x] Resolve pre-acceptance R1/R2: exact coordinate-action zero delta with
    embedded numerical charge evidence; singleton successful primary group,
    commit/envelope binding and explicit previous-primary head semantics.
  - [x] User accepted the corrected wire/package and R1/R2 work on 2026-09-12
    through “commit changes”; runtime implementation and aggregate closure remain open.
  - [x] Implement representation transport independently: both
    current/reset, inverse/covariance, no initializer/loss, readmission,
    rollback and snapshot/restore/reset. Fallback tests do not close this work.
    Inverse scientific/reset/reference recovery must retain both ledger groups;
    distinguish identity transport from identity reconstruction with nontrivial
    histories. Exercise migration → representation → evolution → lossy event →
    restore/reset, charge-order and signed-zero controls, and incompatible
    reference/backend/context/chart targets despite valid correspondences.
  - [x] Independently review the retained P9-7.2b execution and accept aggregate
    closure. Implementation/test completion is not user acceptance or new G2/G3.
    Runtime audit F1/F2 corrections are implemented with eight native regression
    methods, including the additional changed-graph A-target pressure. The
    original capture is preserved separately from the correction run. The user
    accepted and closed P9-7.2b on 2026-09-12 through “accept and commit 7.2b”.
  Genuine topology-preserving maps remain deferred; isolated zero-resource
  vertex addition with declared old-edge lineage is the next bounded candidate.
- [x] P9-7.3: Verify separate candidate/carrier history channels, explicit
  loss receipts, and target resource/charge policies.
  - [x] Implement the [bounded verification](./phase-9-grcv4/tranche-7/P9-7.3-Review.md):
    32 policy cells, five native migration/event witnesses, separate lossless
    representation, channel/reset tampering and exact affine/charge pressure.
  - [x] Retain a separate source/claim-bound execution and expose it in the
    existing API/notebook/browser status without changing accepted 7.2 evidence.
  - [x] Review and accept P9-7.3; user accepted on 2026-09-12 following two
    passing audits, including the separately reported native six-test rerun.
    No additional G2/G3 or later leaf closure.
  - [x] Before commit, execute the user's requested three sharper regressions:
    subnormal round-once accumulation, admitted charge offset and changed
    coordinate hashes without loss. All three passed in a separate record.
- [x] P9-7.4: Verify Candidate C target reference-map completeness and full
  target reconstruction/readmission before atomic commit.
  - [x] Implement focused reference-map rejection, five-realization current/reset
    admission, changed-graph numerical reconstruction and whole-publication
    rollback checks; retain separate source/claim-bound execution.
  - [x] Expose [bounded verification](./phase-9-grcv4/tranche-7/P9-7.4-Review.md)
    through existing API/notebook/browser status without rewriting accepted
    runs or widening runtime permissions and G2/G3.
  - [x] Independently review and accept P9-7.4. User accepted on 2026-09-12
    following the passing audit and independently reported numerical rerun.
    P9-7.5 and P9-7.6 remain separate.
- [x] P9-7.5: Execute missing-lineage, invalid-map, and readmission failure
  cases, including reset after ordinary steps, migrations, and events.
  - [x] Add [bounded sequence pressure](./phase-9-grcv4/tranche-7/P9-7.5-Review.md):
    distinct live/reset states after positive steps and crossings, missing
    crossing/receipt evidence, invalid operation maps/history and mixed-prefix
    reset-only admission rejection. Check ledger versus delta and whole rollback.
  - [x] Retain separate source/claim-bound evidence and expose pending review
    through existing API/notebook/browser status; keep prior runs unchanged.
  - [x] Independently review and accept P9-7.5. User accepted on 2026-09-12
    after the passing audit and independently reported rerun. Parent-DAG conformance and
    deep duplicate ownership remain P9-7.6; no new G2/G3 support.
- [ ] P9-7.6: Verify receipt lineage ownership and deep duplicate independence.
  Resolve P9-2.4's open parent-reference scope/order question from accepted
  authority before claiming lineage conformance: historical versus intra-commit
  parents, missing/forward/self/cyclic references and duplicate handling.
  Do not infer parent-DAG validity from receipt hashes, commit construction,
  ledger append equality or content-only comparison evidence. P9-4.9.2 owns the
  C_OS authority/conformance closure, now implemented under the accepted uniform
  predecessor rule; its review retains the bounded execution evidence. Broader
  profile completion and public-facade/G2 acceptance remain scoped to the
  P9-4.8B singleton; other profiles remain pending.
- [ ] P9-7.7: Review the full applicable fixture product and record `P9-G2[p]`
  separately for each generic profile; link the original P9-4.8 C_OS review and
  its P9-4.8B successor without duplicate execution credit.
- [ ] P9-7.8: Review `P9-G3[S]` for the exact accepted generic support set
  before specialization code. Singleton `P9-G3[C_OS]` can run immediately
  after its G2; unrelated lifecycle/realization rows may remain pending.

## Tranche 8. D11-G9 mechanical specialization

Entry is the reviewed `P9-G3[S]` scope, potentially C_OS alone. P9-8.1 and
P9-8.3 are parent registers; their child scopes are independently reviewed.

- [ ] P9-8.1a: Implement and verify the fixed chart and port graph.
- [ ] P9-8.1b: Implement and verify row differential and V4 row-weight bridge.
- [ ] P9-8.1c: Implement and verify the mechanical candidate trigger.
- [ ] P9-8.1d: Implement and verify column coarse-graining and Split.
- [ ] P9-8.2: Implement exact D11-G9-P4a boundary reservation, primary spine,
  both chiralities, conditional phase, tree construction, and capacity rules.
- [ ] P9-8.3C-OS: Verify C_OS event/node/edge IDs, current/reset resource
  distribution, C reference transport, and carrier `not_applicable` semantics.
- [ ] P9-8.3C-PC: After C_PC's G2 and G3 entry, execute the separate C_PC
  nonnull carrier reset/loss vector and target readmission. Pending C_PC
  support does not hold the C_OS child.
- [ ] P9-8.3A: Held until a concrete Candidate A expansion target/history
  vector exists outside the frozen release and its A profile gates pass;
  then execute exact initialization/history and reconstruction cases.
  Template identity alone does not lift this hold or block C-family work.
- [ ] P9-8.4: Execute all applicable accepted D30, D31, D45, and D52 runtime
  counterparts, with exact chirality/phase cases. Add separately labeled
  D37/D44 capacity-shell boundary probes and deeper declared probes. Execute
  permutation, chart rotation, reflection/chirality conjugacy, signed-edge
  reorientation, and phase-boundary cases; probes never replace frozen vectors.
- [ ] P9-8.5: Verify unique target occupancy, whole-lifecycle target
  reconstruction/readmission, and atomic failures.
- [ ] P9-8.6: Keep arbitrary-size conformance held until actual deep/runtime
  covariance evidence passes.

## Tranche 9. Hybrid completion and disabled compatibility

- [ ] P9-9.1: Reconcile the two child dispositions below as an aggregate,
  not a universal execution/crossing prerequisite. Unselected optional scope
  remains planned/deferred, not marked executed.
- [ ] P9-9.1a: Execute optional child stabilization, completed-spark and
  hierarchy evidence when advertised or explicitly required by a stronger
  project handoff, after P9-8.6. Neither is selected by this planning review.
- [ ] P9-9.1b: Execute mandatory specialization lifecycle after P9-8.6,
  regardless of completion flags; preserve trigger/topology/charge/reset,
  receipt/readmission and legacy compatibility obligations.
- [ ] P9-9.2: Reconcile the forty-cell parent register below. Each child
  executes and reviews its exact unchanged GRC9V3 delegate/oracle separately;
  this parent is not a single execution iteration.
- [ ] P9-9.3: Track the complete ten-by-four matrix; mark each unsupported or
  unexecuted slot explicitly and claim only the supported tested subset.
- [ ] P9-9.4: Execute both enabled/disabled migration directions with exact
  authority, reset, history-loss, receipt, and readmission semantics.
  Depend on P9-9.1b and the applicable disabled lifecycle delegate, not the
  optional P9-9.1a child or aggregate P9-9.1.
- [ ] P9-9.5: Verify V4's `legacy_expansion_target_undefined` rejection for
  the saturated port-5 conflict, without changing the legacy implementation.
- [ ] P9-9.6: Review specialization support only after enabled and applicable
  disabled contracts pass; no enabled-only full-conformance label.
  Additionally require P9-9.1a evidence per exact profile/capability when
  completion/hierarchy is advertised or required for explicit project handoff.
  Completion-off waives no mandatory lifecycle/compatibility evidence.

### P9-9.2 compatibility execution register

Every child needs its own entry authority, complete-profile/delegate IDs,
exact fixture, commands/results, retained evidence, failure/debt disposition,
and review. Each cell binds the corresponding
`D10.2-EC-DISABLED-<profile>-<SURFACE>` contract in the
[frozen forty-contract matrix](../specs/grc-9-v4-spec.md#exact-disabled-grc9v3-compatibility).
Controlled batches retain independent child outcomes. Pending cells for an
unselected profile do not hold a different fully tested profile. All cells
are initially pending and unexecuted.

| Execution child | State |
| --- | --- |
| `P9-9.2-A_CI-transition` | Pending |
| `P9-9.2-A_CI-state` | Pending |
| `P9-9.2-A_CI-observable` | Pending |
| `P9-9.2-A_CI-lifecycle` | Pending |
| `P9-9.2-C_CI-transition` | Pending |
| `P9-9.2-C_CI-state` | Pending |
| `P9-9.2-C_CI-observable` | Pending |
| `P9-9.2-C_CI-lifecycle` | Pending |
| `P9-9.2-A_OS-transition` | Pending |
| `P9-9.2-A_OS-state` | Pending |
| `P9-9.2-A_OS-observable` | Pending |
| `P9-9.2-A_OS-lifecycle` | Pending |
| `P9-9.2-C_OS-transition` | Pending |
| `P9-9.2-C_OS-state` | Pending |
| `P9-9.2-C_OS-observable` | Pending |
| `P9-9.2-C_OS-lifecycle` | Pending |
| `P9-9.2-A_RG2b-transition` | Pending |
| `P9-9.2-A_RG2b-state` | Pending |
| `P9-9.2-A_RG2b-observable` | Pending |
| `P9-9.2-A_RG2b-lifecycle` | Pending |
| `P9-9.2-C_RG2b-transition` | Pending |
| `P9-9.2-C_RG2b-state` | Pending |
| `P9-9.2-C_RG2b-observable` | Pending |
| `P9-9.2-C_RG2b-lifecycle` | Pending |
| `P9-9.2-A_PC-transition` | Pending |
| `P9-9.2-A_PC-state` | Pending |
| `P9-9.2-A_PC-observable` | Pending |
| `P9-9.2-A_PC-lifecycle` | Pending |
| `P9-9.2-C_PC-transition` | Pending |
| `P9-9.2-C_PC-state` | Pending |
| `P9-9.2-C_PC-observable` | Pending |
| `P9-9.2-C_PC-lifecycle` | Pending |
| `P9-9.2-A_CI_PC-transition` | Pending |
| `P9-9.2-A_CI_PC-state` | Pending |
| `P9-9.2-A_CI_PC-observable` | Pending |
| `P9-9.2-A_CI_PC-lifecycle` | Pending |
| `P9-9.2-C_CI_PC-transition` | Pending |
| `P9-9.2-C_CI_PC-state` | Pending |
| `P9-9.2-C_CI_PC-observable` | Pending |
| `P9-9.2-C_CI_PC-lifecycle` | Pending |

## Tranche 10. Conformance and handoff

- [ ] P9-10.1: Reconcile every vector hold and acceptance-gate runtime debt
  with exact execution evidence or an explicit remaining support hold.
- [ ] P9-10.2: Verify deterministic replay, numerical comparison conventions,
  independent charge-edge results, and runtime-generated receipt evidence.
- [ ] P9-10.3: Run relevant old-family regressions and verify accepted release
  and source identity preservation.
- [ ] P9-10.4: Publish capability discovery, a minimal API/replay example,
  and new runtime evidence linked to the frozen fixture catalog.
- [ ] P9-10.5: Reconcile inherited scientific debts without upgrading source
  claims from test coverage alone.
- [ ] P9-10.6: Record reviewed support, pending profiles, residual debt,
  closeout, handoff, and P9-G4 acceptance.

## Planning review disposition

The attached execution-structure review is bound by SHA-256 in the phase
opening. Its recommendations change planning and scheduling; P9-G1 and all
runtime/profile acceptance gates remain pending.

| Review item | Planning disposition |
| --- | --- |
| 1. Atomic execution unit | Top-level tranches retained; each P9-N.M leaf owns an independent execution/review record. |
| 2. Split large rows | Candidate/realization children, separate migration/event rows, four mechanics children, and compatibility cells registered. |
| 3. Earlier lifecycle | P9-4.6–P9-4.8 pressure C_OS lifecycle and reconcile its full applicable fixture product before G2. |
| 4. Profile-indexed G2 | Ten pending profile gates and an initially empty accepted support set; G3 binds exact consumed sets. |
| 5. Earlier GRC9V4 option | P9-G2[C_OS] followed by reviewed P9-G3[C_OS] permits the C-only path. |
| 6. Separate A expansion hold | P9-8.3A retains the concrete-target-vector hold; C_OS and C_PC have independent children. |
| 7. Normative degrees | D30/D31/D45/D52 runtime counterparts required; D37/D44 are additional boundary probes. |
| 8. Independent realizations | Lifecycle/G2 review may proceed per profile while sibling realizations and RG2b remain pending. |
| 9. Keep groupings | Tranches 0–10 remain the conceptual organization with stable P9-N.M IDs. |
| 10. Recording/failure rule | Leaf template records authority, scope, evidence, debt, review, and next step; failures follow dependencies. |

Post-review validation passes: eleven tranche headings, ten pending profile
gates, forty distinct compatibility cells matching the frozen matrix, all
twelve coverage holds retained, and exact D30/D31/D45/D52 degree coverage
checked against the accepted vector bundle. Three Markdown documents render;
29 local links, predecessor/release/review hashes, merge parents, and the
four-file planning scope validate. The dedicated release-acceptance audit
still passes all twelve members. `P9-TOOL-001` remains pending under its own
execution rows; these planning corrections do not claim to repair it.

## Iteration record template

Append one record per executed leaf iteration, including each independently
reviewed child in a controlled batch. Its review covers only the named scope.

```text
Iteration ID / parent ID:
Entry authority and accepted dependencies:
Exact candidate/profile/lifecycle/compatibility scope:
Specification sections, machine contracts, paper passages, claim references:
Changed paths:
Tests and independent oracles:
Commands and results:
Retained evidence and code/release/profile/fixture identities:
New debt, failure, and affected dependent paths:
Review disposition (accepted / bounded / rejected / pending):
Parent reconciliation status:
Next permitted step:
```

The initial checklist records planning only. All runtime iterations and
profile gates remain pending.
