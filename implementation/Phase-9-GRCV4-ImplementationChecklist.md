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
| `P9-G2[C_OS]` | Pending | Early lifecycle and full fixture review at P9-4.8. |
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
  remain later owner tests. Engineering completion, not acceptance of P9-2.4
  or any runtime profile; P9-2.5 is not started.
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
- [ ] P9-2.5: Create the runtime harness with independent oracles and exact
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
- [ ] P9-2.6: Verify unsupported-profile rejection, deep immutability, and
  unchanged common-interface behavior for older families.
  Verify clean wheel/sdist and optional-extra boundaries (§7.1) and each
  consumed legacy symbol's exact reuse boundary (§7.2).
  Carry strict-request non-admission tests into each authorized facade/full-step
  consumer (P9-4.4/P9-4.5/P9-4.7a): zero, subnormal and extreme finite duration must not
  bypass graph/profile/context/domain checks. Current no-facade assertions are
  leaf-stage checks, not a permanent prohibition on authorized implementation.

## Tranche 3. Typed graph, geometry, transport, and charge

- [ ] P9-3.1: Implement deterministic graph/differential identities, typed
  Hodge/one-form/physical-flux maps, and candidate-local mobility ownership.
  Resolve graph-backend storage/lookup and utility reuse before implementation (§7.2).
- [ ] P9-3.2: Implement exact stage/cache provenance and domain admission.
- [ ] P9-3.3: Implement the one-resource-write complete-step boundary and
  exact charge gate, without an extra remainder/repair coordinate.
- [ ] P9-3.4: Execute nonidentity SPD, permutation, signed-edge covariance,
  nonfinite/domain, stale-cache, and charge-precision cases.
  Include near-admitted conditioning boundaries and repeated eigenvalues
  within a strictly separated cluster; compare invariant projectors (§7.4).
- [ ] P9-3.5: Verify full prestate preservation after every rejected operation.

## Tranche 4. D11-C and the first C_OS runtime slice

- [ ] P9-4.1: Bind `C-HM-STIFFNESS-BASELINE-v1`, the exact positive stable-edge
  reference map, and separate Hodge/mobility constructor identities.
- [ ] P9-4.2: Implement the accepted potential and baseline flux, selector
  gap, Read-Back typing, and regular current solve at their declared stages.
- [ ] P9-4.3: Verify independent kappa-M, chi, and zeta zero controls and
  complete smooth-stratum baseline derivative/covariance cases.
  Add the separate tau-C-zero control on nontrivial retained Hodge with
  nonzero kappa-M; no frozen-catalog edit or simultaneous-zero shortcut (§7.3).
- [ ] P9-4.4: Implement one OS pass, explicit split residual, one resource
  write, and post-continuity rederivation.
- [ ] P9-4.5: Execute positive and atomic-negative `C_OS` vectors; keep full
  profile conformance pending lifecycle completion.
  Exercise the declared numerical reproducibility scope without hidden
  damping, regularization, pseudoinverse, fallback or charge repair (§7.4).
- [ ] P9-4.6: Execute the C_OS snapshot/load/reset/rebase and deep-copy/
  immutability slice; record the corresponding P9-7.1-C_OS evidence.
- [ ] P9-4.7a: Execute atomic failed-step, receipt identity/ownership, and
  state-to-step-to-snapshot-to-restore-to-replay pressure for C_OS.
- [ ] P9-4.7b: Execute the remaining applicable C_OS lifecycle product through
  early Tranche 7 children: mapped events, migration admission/rejection,
  reset after events/migrations, reference maps, and atomic readmission.
  Unsupported targets must reject; mandatory fixtures cannot be waived.
- [ ] P9-4.8: Review all applicable C_OS fixtures and accept, reject, or hold
  `P9-G2[C_OS]`. Missing mandatory cases keep this gate pending. Record the
  next permitted A_OS or `P9-G3[C_OS]` review path.

`P9-4.7` is the parent of P9-4.7a and P9-4.7b. The early state/receipt/replay
cycle supplies evidence; P9-4.8 grants no reduced form of generic conformance.

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
scopes, evidence aliases and dependencies. All are planned/unexecuted;
P9-7.1-C_OS aliases P9-4.6 and P9-7.7-C_OS aliases P9-4.8, with no duplicate
execution credit. Parent completion remains scoped to reviewed child evidence.

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
  ledger append equality or content-only comparison evidence.
- [ ] P9-7.7: Review the full applicable fixture product and record `P9-G2[p]`
  separately for each generic profile; link P9-4.8 for the early C_OS result.
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
