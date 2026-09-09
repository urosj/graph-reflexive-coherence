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
| `P9-G2[C_OS]` | Pending | P9-4.8 draft HOLD; P9-4.9.1–P9-4.9.3 close its obligations, then P9-4.8B reassesses the full fixture/interface/authority product. |
| `P9-G2[A_OS]` | Pending | Tranche 5 plus A_OS lifecycle and P9-7.7 review. |
| `P9-G2[C_CI]` | Pending | P9-6.1a plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_CI]` | Pending | P9-6.1b plus profile lifecycle and P9-7.7 review. |
| `P9-G2[C_PC]` | Pending | P9-6.2a plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_PC]` | Pending | P9-6.2b plus profile lifecycle and P9-7.7 review. |
| `P9-G2[C_CI_PC]` | Pending | P9-6.3a plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_CI_PC]` | Pending | P9-6.3b plus profile lifecycle and P9-7.7 review. |
| `P9-G2[C_RG2b]` | Pending | P9-6.4a certification plus profile lifecycle and P9-7.7 review. |
| `P9-G2[A_RG2b]` | Pending | P9-6.4b certification plus profile lifecycle and P9-7.7 review. |

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
- [ ] P9-4.8: Draft **HOLD P9-G2[C_OS]**; fixture reconciliation and user
  review/acceptance remain open. Preserve this original review and its evidence;
  discharge its obligations through P9-4.9.1–P9-4.9.3 and the successor P9-4.8B
  result, not by relabeling the historical HOLD. A_OS and `P9-G3[C_OS]` remain
  behind G2.
- [ ] P9-4.9.1: Public C_OS facade implemented and 14 focused tests passed;
  interface closure is blocked on P9-4.9.1a and user review. See the
  [method/test mapping and ceilings](./phase-9-grcv4/tranche-4/P9-4.9.1-Review.md).
  `abundance` remains an explicit interim placeholder without accepted V4
  semantics; it does not close public-interface or G2 conformance.
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
- [ ] P9-4.9.1a: Resolve the narrow abundance-interface authority gap under
  `G2-COS-INTERFACE`, without reopening accepted constitutive/lifecycle results.
  Distinguish theoretical identity multiplicity from an instantaneous diagnostic.
  Propose family/capability ownership; do not accept it merely by adding this row.
  Decide exact V4 key/availability/type/unavailable semantics and any admitted
  detector/stage, read-only status and consumer compatibility. Current null/status
  is not an accepted resolution; no invented charge, topology or basin proxy.
  Record the bounded investigation decision, obtain acceptance, and propagate
  through claims/tooling and proposal/paper/V4 specs as applicable before changing
  runtime semantics. Keep legacy/common/V3 files unchanged; explain any V4
  inheritance exception explicitly in the V4 extension. Add only affected tests
  for availability, capability truth, stages, restoration and nonmutation.
  Keep final P9-4.9.1/P9-4.9.3 public-interface and G2 closure held until resolved.
  Planning only: no new runtime permission, accepted rule or extra governance gate.
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
- [ ] P9-4.9.3: Reconcile the 33-case catalog index and exact semantic vectors
  into the full fixture product for a nonempty nominated complete-profile set
  (`G2-COS-FIXTURES`).
  Initial bounded inventory is complete in the
  [gap list](./phase-9-grcv4/tranche-4/P9-4.9.3-EvidenceInventory.md); this row
  remains unchecked for final public/profile reconciliation. The inventory
  itself reran no numerical tests and added no runtime support. Subsequent
  P9-4.9.2 authority/implementation work is recorded above, not as G2 acceptance.
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
- [ ] P9-4.8B: Review the three work packages together once the integrated result
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

P9-4.8 has a draft **HOLD P9-G2[C_OS]**, pending fixture reconciliation and
user review. Start from the [current continuation handoff](./phase-9-grcv4/tranche-4/P9-4.8-Handoff.md).
The [gate review](./phase-9-grcv4/tranche-4/P9-4.8-Review.md) and
[33-case evidence index](./phase-9-grcv4/tranche-4/P9-4.8-GateReview.json)
record unfinished public-interface integration and deferred receipt-parent
authority. Fixture reconciliation is P9-4.8 work; its absent consolidated mapping
is not proof of missing behavior. Reassess the stale-cache case using the existing
second-beat reconstruction test before claiming a new gap. The corrected mandatory
mapped-event execution retains its scoped credit. A_OS and P9-G3[C_OS] stay
behind G2. Runtime support remains empty; permissions remain 26 leaves / 29
eligible paths. P9-4.8 has changed review artifacts only.

## Tranche 5. Candidate A and A_OS

- [ ] P9-5.1: Implement exact history-free initialization and positive
  retained-mobility authority.
- [ ] P9-5.2: Implement log-space writing, direct current, and Read-Back with
  no same-beat reading of newly written retained state.
- [ ] P9-5.3: Execute independent Candidate A numerical/stage/control vectors
  and the `A_OS` step cases.
- [ ] P9-5.4: Preserve separate initialization/formation/history claims and
  keep lifecycle-dependent conformance pending.

## Tranche 6. CI, PC, CI+PC, and RG2b

P9-6.1–P9-6.4 are parent registers. Their candidate children carry numerical
and failure oracles with each implementation; the `c` children audit shared
realization behavior once their reviewed inputs are available. Each profile
also needs applicable shared-contract evidence before its G2 review, but a
pending sibling implementation cannot substitute for or impose unrelated
coverage. Record bounded shared-audit results for the available profile set.

- [ ] P9-6.1a: Implement and verify C_CI's selected bounded root and exact
  failure/domain rules.
- [ ] P9-6.1b: Implement and verify A_CI's selected bounded root and exact
  failure/domain rules.
- [ ] P9-6.1c: Audit shared CI realization contracts and reconcile independent
  candidate evidence; record exactly which profiles the audit covers.
- [ ] P9-6.2a: Implement and verify C_PC old-history reads, one scalar-ZOH
  write, declared tau, and state/reset ownership.
- [ ] P9-6.2b: Implement and verify A_PC's candidate-specific PC contract.
- [ ] P9-6.2c: Audit shared PC behavior and independent history/state coverage.
- [ ] P9-6.3a: Implement and verify C_CI_PC same-source composition and gain two.
- [ ] P9-6.3b: Implement and verify A_CI_PC same-source composition and gain two.
- [ ] P9-6.3c: Audit shared CI+PC composition against the exact root/carrier
  source and candidate-specific evidence.
- [ ] P9-6.4a: Bind, certify, and verify the admitted C_RG2b evaluator and
  Lipschitz section; reject unsupported classical derivative claims.
- [ ] P9-6.4b: Bind, certify, and verify A_RG2b independently.
- [ ] P9-6.4c: Audit the RG2b evaluator/certification scope and regularity
  ceiling for the exact reviewed profiles.
- [ ] P9-6.5: Reconcile concrete realization results profile-by-profile,
  route each ready profile to lifecycle/G2 review, and retain pending or
  deferred siblings. Tranche-wide completion is not an entry condition.

## Tranche 7. Generic lifecycle generalization and P9-G2

The [P9-1.4 child register](./phase-9-grcv4/tranche-1/P9-1.4-SupportAndDependencies.json)
now declares exact C_OS and A_OS lifecycle children, source/target crossing
scopes, evidence aliases and dependencies. P9-7.1-C_OS and the early C_OS
P9-7.2a/b–P9-7.6 children have scoped evidence accepted with the P9-4.6/4.7 batch;
its full audit findings are closed. Generic parent-reference conformance remains
open across other profiles; the accepted P9-4.9.2 authority and bounded internal
C_OS implementation are recorded in its linked review. A_OS children remain
planned/unexecuted. P9-7.7-C_OS currently aliases the P9-4.8 draft HOLD review;
P9-4.8B will supply the successor disposition after closure, with no duplicate
execution credit.
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

- [ ] P9-7.1: Execute save/load/replay, reset, rebase, and independent
  duplication with canonical authority and receipt identities.
- [ ] P9-7.2a: Execute required profile migration classes over current and
  reset state, independently by source/target identities and failure surface.
  A decoded P9-2.3 declaration is not migration admission: test unresolved
  history/initializers, unsupported targets and missing mappings at the real
  consumer, including separate candidate/carrier channel decisions.
- [ ] P9-7.2b: Execute caller-mapped generic topology events over current and
  reset state, with their own map/identity/admission failure evidence.
- [ ] P9-7.3: Verify separate candidate/carrier history channels, explicit
  loss receipts, and target resource/charge policies.
- [ ] P9-7.4: Verify Candidate C target reference-map completeness and full
  target reconstruction/readmission before atomic commit.
- [ ] P9-7.5: Execute missing-lineage, invalid-map, and readmission failure
  cases, including reset after ordinary steps, migrations, and events.
- [ ] P9-7.6: Verify receipt lineage ownership and deep duplicate independence.
  Resolve P9-2.4's open parent-reference scope/order question from accepted
  authority before claiming lineage conformance: historical versus intra-commit
  parents, missing/forward/self/cyclic references and duplicate handling.
  Do not infer parent-DAG validity from receipt hashes, commit construction,
  ledger append equality or content-only comparison evidence. P9-4.9.2 owns the
  C_OS authority/conformance closure, now implemented under the accepted uniform
  predecessor rule; its review retains the bounded execution evidence. Broader
  profile completion and public-facade/G2 review remain scoped and pending.
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
