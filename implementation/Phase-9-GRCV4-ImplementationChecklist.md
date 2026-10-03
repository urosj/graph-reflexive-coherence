# Phase 9 GRCV4 Implementation Checklist

Date: 2026-09-05. Status: P9-G1 accepted; bounded implementation authorized.

2026-10-02: P9-8.0 is complete after explicit acceptance of R1–R10 and the
aggregate bounded feasibility scope. All ten rows are provisionally closed;
the all-ten production hold is released. P9-8.1a's four checkpoints are complete
and committed at `75a6629`. P9-8.1b's four recorded checkpoints are delivered
together under the user's request: row equations, stage-specific weight bridge
and integrated own review, accepted and committed at `7f33a42`. P9-8.1c's four
recorded checkpoints are implemented, own-reviewed and user-accepted together: baseline
candidate detection, admitted post-commit fixture and boundary pressure,
committed at `e9dfad7`. P9-8.1d's three content-specific checkpoints are
implemented and own-reviewed together: nonnegative inverse algebra, canonical
signed channels and graph-bound field dispatch. The user accepts `.d` with the
identified exact-backend integration correction assigned to new P9-8.1e;
that checkpoint is committed at `a2d3d36`. P9-8.1e is implemented, own-reviewed
and user-accepted with real Python/FLINT parity and P9-8.0 arithmetic classification,
committed at `c27583c`. The user explicitly accepts the complete P9-8.1 parent
on 2026-10-02 and requests merging its branch into `main`.
P9-8.2 is implemented and own-reviewed on 2026-10-03 in three substeps delivered
together on `work/p9-8-2-expansion-allocator`, from merge `184919b`.
The user explicitly accepts P9-8.2 on 2026-10-03 after specification/paper
review and requests commit and merge, then P9-8.3C-OS on a new branch.
The end-of-Tranche-8 cache review remains open.
General 7T and later native acceptance gates remain separate.

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
| `P9-G2[p]` | Ten exact declarations accepted | Full applicable generic runtime/lifecycle fixture product for exact profile scope p; aggregate P9-7.7 accepted, no broader domains inferred. |
| `P9-G3[S]` | Accepted; Tranche 7 closed | Ten exact generic declarations consumed; P9-8.0 explicitly accepted and its hold released. P9-8.1a retains its scoped permission. No specialization conformance. |
| P9-G4 | Pending | Runtime conformance, regression evidence, reviewed support set, and handoff. |

The initially empty generic support set now contains exact C_OS, A_OS,
A_CI, C_CI, A_PC, C_PC, A_CI+PC, C_CI+PC, A_RG2b and C_RG2b declarations. Each family-level gate
record must bind the actual complete-profile IDs, parameters/domains, fixture
coverage, and evidence; a family label alone does not certify all instances.

| Generic profile gate | State | Acceptance route |
| --- | --- | --- |
| `P9-G2[C_OS]` | Accepted, exact singleton | [explicit G2 acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json) closes Tranche 4 and aliases P9-7.7-C_OS. This historical decision implies no other profile or G3 acceptance. |
| `P9-G2[A_OS]` | Accepted, exact nomination | [Explicit G2 acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-G2Acceptance.json) accepts the reviewed 28-case scope; no all-pairs or G3 support. |
| `P9-G2[C_CI]` | Accepted, exact nomination | [Explicit G2 acceptance](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2Acceptance.json) accepts the reviewed 33-cell scope at `8ec744e`; distinct initializer/event targets and dense controls are not added support. |
| `P9-G2[A_CI]` | Accepted, exact nomination | [Explicit G2 acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-G2Acceptance.json) accepts the reviewed 28-case scope. Discovery at acceptance was exactly C_OS/A_OS/A_CI; no all-pairs or G3 support. |
| `P9-G2[C_PC]` | Accepted by user, 2026-09-14 | Exact 33-cell product and bounded ordered endpoints; [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-C_PC-G2Acceptance.json) pins review checkpoint `06475b2`. No all-pairs or G3. |
| `P9-G2[A_PC]` | Accepted by user, 2026-09-14 | Exact 28-cell product and bounded ordered endpoints; [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-G2Acceptance.json). No all-pairs or G3. |
| `P9-G2[C_CI_PC]` | Accepted by user, 2026-09-14 | [Explicit acceptance](./phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-G2Acceptance.json) binds the exact 33-cell review at checkpoint `2b7e974`. Separate targets, all-pairs and G3 are not promoted. |
| `P9-G2[A_CI_PC]` | Accepted by user, 2026-09-14 | Exact 28-cell product and bounded ordered endpoints; [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-G2Acceptance.json) pins checkpoint `07859cc`. Separate targets, all-pairs and G3 are not promoted. |
| `P9-G2[C_RG2b]` | Accepted, exact declaration | User accepted the 33-cell graph nomination on 2026-09-15; frozen Lipschitz/K/K-minus limits and separate initializer/event endpoints remain explicit. |
| `P9-G2[A_RG2b]` | Accepted, 2026-09-15 | Exact reviewed 28-cell graph nomination at `504859f`; frozen-completion/Lipschitz and ordered-target limits retained. Nine exact declarations published. |

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
its full audit findings are closed. P9-7.1–P9-7.6 are now accepted in their
bounded numerical/lifecycle scopes, including generic events and the accepted
P9-4.9.2 parent rule's later verification. This does not establish the full
exact-profile product required by P9-7.7. Its original review held nine new
nominations for evidence/endpoint reconciliation. P9-7.7-C_OS aliases the
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
- [x] P9-7.6: Verify receipt lineage ownership and deep duplicate independence.
  Resolve P9-2.4's open parent-reference scope/order question from accepted
  authority before claiming lineage conformance: historical versus intra-commit
  parents, missing/forward/self/cyclic references and duplicate handling.
  Do not infer parent-DAG validity from receipt hashes, commit construction,
  ledger append equality or content-only comparison evidence. P9-4.9.2 owns the
  C_OS authority/conformance closure, now implemented under the accepted uniform
  predecessor rule; its review retains the bounded execution evidence. Broader
  profile completion and public-facade/G2 acceptance remain scoped to the
  P9-4.8B singleton; other profiles remain pending.
  - [x] Apply accepted P9-4.9.2 parent authority to a mixed generic sequence,
    including singleton representation groups and lawful unreceipted assignment.
  - [x] Add [bounded lineage/ownership pressure](./phase-9-grcv4/tranche-7/P9-7.6-Review.md):
    coherently rehashed bad parents, partition rejection, crossing-publication
    rollback, representation-root history and independent mutable duplicate forks.
    Keep symbolic self/cycle projections distinct from content-hashed execution.
  - [x] Retain the execution and verify existing API/notebook/browser exposure
    with pending-review flags and no change to runtime permissions or G2/G3.
  - [x] Independently review and accept P9-7.6. User accepted on 2026-09-12
    following the passing audit and reported independent native rerun.
    P9-7.7/G2 and P9-7.8/G3 remain separate; original execution flags are unchanged.
- [x] P9-7.7: Review the full applicable fixture product and record `P9-G2[p]`
  separately for each generic profile; link the original P9-4.8 C_OS review and
  its P9-4.8B successor without duplicate execution credit.
  - [x] Add the [305-cell exact-profile review](./phase-9-grcv4/tranche-7/P9-7.7-Review.md),
    with lossless nominations, source pointers and all seven ordered migration
    classes. Retain the 33-cell C_OS alias; do not substitute its 7.1 seed.
  - [x] Record HOLD for A_CI, C_CI, A_OS, A_RG2b, C_RG2b, A_PC, C_PC,
    A_CI+PC and C_CI+PC. The 272 uncredited product cells are not failed tests
    or a mandate to rerun all cases. Matching execution evidence remains valid.
  - [x] Close G2-EXACT-PRODUCT, G2-ORDERED-ENDPOINTS and G2-INTEGRATED-REVIEW
    for each nominated child: reuse exact retained assertions, capture only
    missing evidence, then independently review and obtain scoped acceptance.
  - [x] Verify review/status integrity: three focused tests, fourteen review
    mutations and API/notebook/HTTP/browser agreement with forty browser controls.
    No numerical campaign was rerun.
  - [x] Reconcile all ten accepted child declarations against the original
    305-cell product at checkpoint `ffbcabf`: 33 historical C_OS aliases and
    272 accepted child cells, with unchanged nominations and endpoint ceilings.
    [Aggregate reconciliation](./phase-9-grcv4/tranche-7/P9-7.7-AggregateReconciliation.md).
  - [x] Correct the shared browser fixture's stale singleton and permission
    assumptions. Preserve all original rejection tests; add detached-fixture,
    current registry/aggregate and held-state regressions (38/38 shared tests
    and 2/2 aggregate browser tests pass, no production validator relaxation).
  - [x] Review and accept the aggregate reconciliation. The user accepted
    P9-7.7 on 2026-09-15 against checkpoint `1863ab8`; all ten child G2 decisions
    and the aggregate are closed. P9-7.8/G3 remains separate and pending.
    [Aggregate acceptance](./phase-9-grcv4/tranche-7/P9-7.7-AggregateAcceptance.md).
  - [x] P9-7.7-A_OS-local: add the [exact local product](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-LocalReview.md)
    with 21 catalog rows from three focused methods. Retain scalar/log oracles,
    actual stage values, source/control identities, result fields and complete
    publication evidence. Labeled fault controls are not natural-failure claims;
    shared executions and provisional stages are not extra committed runs.
  - [x] Reconcile the seven A_OS crossing cells through the
    [bounded crossing record](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-CrossingReview.md).
    Reuse exact retained witnesses; add persistent crossings, mapped-event reset,
    reset-only rejection and incoming-initializer negative pressure. Keep the
    seven-class matrix's separate endpoints and negative boundaries explicit.
  - [x] User accepted the bounded A_OS local/crossing reconciliation on
    2026-09-13 through “accept and commit.” Preserve original execution flags;
    this does not assert an independent audit or close G2/P9-7.7.
  - [x] Perform the [integrated A_OS G2 assessment](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-G2Review.md):
    PASS proposal with 28 exact case links, explicit crossing applicability,
    one focused facade supplement and unchanged scientific/legacy sources.
    This is not a second independent audit or G2 acceptance.
  - [x] User accepted exact A_OS G2 on 2026-09-13 through “accept and commit”:
    [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-G2Acceptance.json).
    Discovery contains only exact C_OS and A_OS declarations. Eight profile
    gates, all-pairs, aggregate P9-7.7 and G3 remain open. A_CI is next.
    Acceptance checks cover exact registry identity, source-reuse integrity,
    original evidence preservation, rehashed overclaims and required browser
    acceptance. API/notebook/HTTP/browser agreement passed with 58 existing
    mutation controls; no numerical campaign was rerun.
  - [x] P9-7.7-A_CI-local: capture the exact nomination's 21 local catalog
    cells through three focused methods, including independent implicit-root
    equations, local contraction/residual, trial-current-dependent W-hat,
    one post-continuity writer and distinct live/reset lifecycle pressure.
    [Review and evidence](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-LocalReview.md).
    Original A_OS/C_OS acceptance and all retained runs remain unchanged.
  - [x] Reconcile the seven A_CI crossing rows through five retained aliases
    and six new cases in three focused methods. Reuse exact incoming A_OS and
    outgoing PC witnesses; add returning PC, outgoing C, mapped event/reset,
    reset-only readmission contrast and unselected incoming-initializer rejection.
    [Scoped crossing review](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-CrossingReview.md).
  - [x] User accepted the bounded A_CI local/crossing reconciliation on
    2026-09-14, explicitly reserving A_CI G2 review for later. Preserve the
    original execution flags and exact C_OS/A_OS public support.
  - [x] Perform the [integrated A_CI G2 review](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-G2Review.md):
    PASS proposal for 28 exact catalog obligations, bounded crossing
    applicability and one zero-duration facade supplement. Its initializer/event
    target differs from the nomination; no all-pairs or global CI-root shortcut.
  - [x] Add shared exact-profile G2 acceptance/discovery plumbing alongside
    the A_CI proposal, using pinned C_OS/A_OS historical adapters and a common
    new-profile schema. Preserve original acceptance/run evidence and runtime
    permissions; expose accepted versus proposed scope in API/notebook/browser.
  - [x] User accepted exact A_CI G2 on 2026-09-14 after the integrated review:
    [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-G2Acceptance.json),
    binding reviewed checkpoint `fa94cd2`. Discovery contains exactly C_OS,
    A_OS and A_CI; original evidence remains unchanged. Seven other profile
    decisions, all-pairs, aggregate P9-7.7 and G3 remain open.
  - [x] P9-7.7-C_CI-local: capture 26 local cells through four focused methods:
    independent C baseline/derivatives, bounded CI root and per-trial/restart
    rederivation, exact controls, native common and fixed-profile lifecycle
    operations. Dense nonzero-deformation controls are separately identified,
    not additional nominated runtime support.
    [Review and evidence](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-LocalReview.md).
  - [x] Reconcile seven C_CI crossing obligations using five retained aliases
    and five new cases in three methods. Verify returning carrier loss,
    outgoing reference-pass initialization, renamed target reference map with
    both-role numerical readmission, mapped reset/charge and reset-only failure.
    [Scoped crossing review](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-CrossingReview.md).
  - [x] User accepted the combined bounded C_CI local/crossing product on
    2026-09-14; preserve original capture flags. Integrated G2 review and
    explicit G2 acceptance remain separate.
  - [x] Share local/crossing evidence presentation through pinned expected
    views in the existing registry; keep profile-specific scientific checkers
    and original accepted evidence. No new gate or runtime permission.
  - [x] Perform the [integrated C_CI G2 review](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2Review.md):
    PASS proposal for 33 exact catalog obligations, explicit initializer/event
    target boundaries and one zero-duration facade supplement. Reuse the
    four local and three crossing methods without a numerical campaign rerun.
  - [x] At the fourth G2 profile, replace Python per-profile status dispatch,
    view/review seeding and cleanup with pinned ordered registry materializers.
    Check dependencies, source bindings/origins and complete projection;
    preserve distinct scientific checkers, accepted records and permissions.
  - [x] User accepted exact C_CI G2 on 2026-09-14: [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2Acceptance.json)
    binds reviewed checkpoint `8ec744e`. Publish exactly C_OS/A_OS/A_CI/C_CI;
    preserve original evidence and record finite discovery-source comparisons.
    Six other profile decisions, all-pairs, aggregate P9-7.7 and G3 remain open.
  - [x] P9-7.7-A_PC-local: reconcile 21 exact local cells (old Z geometry,
    refreshed A writer, one held-source ZOH write, both-role admission, common
    failures and fixed-profile C/W/Z lifecycle ownership).
    [Bounded review](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-LocalReview.md).
    Four native methods passed; no acceptance or new G2 support.
  - [x] Reconcile the seven A_PC crossing obligations through seven retained
    aliases and five new cases in three passing methods. Preserve exact PC pair
    identities, independent current/reset event targets, separate W/Z loss,
    reset-only rejection and changed-carrier/unselected-initializer boundaries.
    [Scoped review](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-CrossingReview.md).
  - [x] User accepted the combined A_PC local/crossing result on 2026-09-14.
    Preserve original execution records and project bounded acceptance separately.
  - [x] Perform the [integrated A_PC G2 review](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-G2Review.md):
    28 cells, exact PC pair contracts, separate W/Z losses and native release,
    typed contract/debt ceilings and one zero-duration public-facade supplement.
    Reuse four local and three crossing methods without a numerical campaign rerun.
  - [x] User accepted exact A_PC G2 on 2026-09-14: [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-G2Acceptance.json)
    binds reviewed checkpoint `b4909a3`. Publish exactly C_OS/A_OS/A_CI/C_CI/A_PC;
    preserve original evidence via finite source comparisons. Five other profile
    G2 decisions, all-pairs, aggregate P9-7.7 and G3 remain open.
  - [x] Continue persistent profiles in order A_PC, C_PC, A_CI+PC, C_CI+PC;
    leave A_RG2b/C_RG2b last. This is scheduling, not weaker acceptance criteria.
  - [x] P9-7.7-C_PC-local: capture 26 local cells in five passing methods.
    Independently reconstruct the complete C chain at old-carrier, reset and
    post-write geometry; zero A writers, one held-source ZOH write, native release,
    fixed-stage derivative controls and complete C/Z lifecycle rollback.
    [Bounded review](./phase-9-grcv4/tranche-7/P9-7.7-C_PC-LocalReview.md).
  - [x] Reconcile seven C_PC crossing obligations using seven retained aliases
    and four new cases in three passing methods. Preserve exact PC↔CI+PC
    contracts, independent C→A initialization, two-channel losses, target
    reference rederivation, reset, replay and whole-publication rollback.
    [Crossing review](./phase-9-grcv4/tranche-7/P9-7.7-C_PC-CrossingReview.md).
  - [x] User accepted combined C_PC local/crossing reconciliation on 2026-09-14
    and requested its commit before G2. Preserve original execution flags and
    project bounded acceptance separately. No new public support.
  - [x] Complete integrated C_PC G2 review: 33 exact cells, ordered carrier
    contracts/loss channels, complete C reference/baseline authority and one
    zero-duration facade supplement. Reuse five local and three crossing
    methods; preserve typed claim/debt ceilings and five accepted declarations.
    [G2 proposal](./phase-9-grcv4/tranche-7/P9-7.7-C_PC-G2Review.md).
  - [x] User accepted exact C_PC G2 on 2026-09-14. Bind checkpoint `06475b2`,
    preserve original review/execution bytes and publish six exact declarations
    through the shared adapter. Four other G2 decisions, all-pairs, aggregate
    P9-7.7 and G3 remain open.
  - [x] P9-7.7-A_CI_PC-local: verify 21 exact local cells, coupled same-root
    geometry/ZOH, separate W refresh, signed-carrier release, independent
    reset/restart, lifecycle ownership and rehashed evidence pressure. Five
    native methods, 33 evidence mutations and shared surfaces pass; acceptance
    remains separate.
    [Local review](./phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-LocalReview.md).
  - [x] P9-7.7-A_CI_PC-crossings: reconcile seven crossing cells with five
    retained aliases and seven native cases in four methods; verify two-role
    implicit admission, carrier/W loss distinctions, reset and rejection.
    Four native methods, 39 rehashed mutations and shared surfaces passed.
    [Crossing review](./phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-CrossingReview.md).
  - [x] User accepted combined A_CI+PC local/crossing reconciliation on
    2026-09-14: all 28 cells at their exact declared scope. Preserve execution
    records and six existing G2 declarations; no all-pairs or G3 promotion.
  - [x] Complete integrated A_CI+PC G2 review: 28 exact cells, same-source
    coupled geometry/ZOH, separate W refresh, exact carrier transport/loss,
    typed authority ceilings and one zero-duration facade supplement. Reuse
    five local and four crossing methods; distinguish both separate targets.
    Facade supplement, 13 focused methods and one shared status/UX check pass.
    [G2 proposal](./phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-G2Review.md).
  - [x] User accepted exact A_CI+PC G2 on 2026-09-14. Bind checkpoint
    `07859cc`, preserve original review/execution bytes and publish seven exact
    declarations through the shared adapter. Three other profile G2 decisions,
    all-pairs, aggregate P9-7.7 and G3 remain separate.
  - [x] P9-7.7-C_CI_PC-local: verify 26 exact local cells with complete C
    reconstruction at coupled trials and current/reset/restart roots, one
    selected geometry/ZOH source, no W writer, signed history/release and exact
    lifecycle ownership. Five native methods, 47 evidence mutations and shared
    surfaces pass. Keep seven accepted G2 declarations; crossing evidence is below.
    [Local review](./phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-LocalReview.md).
  - [x] P9-7.7-C_CI_PC-crossings: reconcile all seven remaining cells with
    eight native cases in four methods and three retained aliases. Verify
    exact ordered endpoints, separate initializer scope, coupled target roots,
    two-channel history loss, reset/replay and atomic failure. All 55 rehashed
    mutations, 12 registry/materializer tests and shared surfaces pass.
    [Crossing review](./phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-CrossingReview.md).
  - [x] User accepted the combined 26+7-cell C_CI+PC reconciliation on
    2026-09-14. Preserve original execution records; this is not G2 acceptance.
  - [x] Complete the exact C_CI+PC integrated G2 proposal/review: all three
    obligations pass for the 33-cell product and bounded ordered endpoints.
    Bind checkpoint `6ab241f`, 22 contract/four debt traces and one facade
    supplement; reuse the five local/four crossing methods without reruns.
    All 38 rehashed mutations, 14 focused tests and shared surfaces pass.
    [G2 review](./phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-G2Review.md).
  - [x] User accepted exact C_CI+PC G2 on 2026-09-14. Bind checkpoint
    `2b7e974`, preserve original review/execution bytes and publish eight exact
    declarations through the shared adapter. Both RG2b decisions, separate
    controls/targets, all-pairs, aggregate P9-7.7 and G3 remain outside scope.
  - [x] Reconcile exact A_RG2b local product: 21 cells with completion-relative
    section/error, independent inverse/current/writer equations, separate
    current/reset/restart, fixed-beat and admission failures, replay/ownership.
    [Local review](./phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-LocalReview.md).
  - [x] Reconcile A_RG2b's remaining seven crossing cells: nine native cases,
    exact graph endpoints, independent per-role section/current/initializer,
    explicit history dispositions, reset/replay and target K versus K-minus.
    Four retained scalar/persistent witnesses remain separately scoped.
    [Crossing review](./phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-CrossingReview.md).
  - [x] User accepted bounded A_RG2b reconciliation on 2026-09-15. Preserve
    execution records and project acceptance through the shared materializer.
  - [x] Prepare and verify the separate A_RG2b integrated G2 proposal: 28 cells,
    one native facade method, 15 focused review/surface methods and 39 rehashed
    mutation controls. Preserve frozen completion, K/K-minus and Lipschitz-only
    boundaries, plus distinct scalar/initializer/event targets.
    [G2 review](./phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-G2Review.md).
  - [x] User accepted exact A_RG2b G2 on 2026-09-15. Bind checkpoint `504859f`,
    preserve original evidence and publish nine exact declarations through the
    shared adapter. C_RG2b, separate controls/targets, all-pairs, aggregate
    P9-7.7 and G3 remain separate.
    [Acceptance](./phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-G2Acceptance.json).
  - [x] P9-7.7-C_RG2b-local: implement 26 exact local cells, complete C
    reconstruction at current/reset/restart RG sections, independent inverse,
    baseline/continuity equations, fixed-stratum controls and whole-publication
    rollback. Five native methods, 51 semantic mutations, 13 focused shared
    checks and the phase boundary pass. Register through the shared materializer.
    [Local review](./phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-LocalReview.md).
  - [x] P9-7.7-C_RG2b-crossings: implement all seven crossing obligations with
    nine native cases and two separately scoped retained PC↔CI+PC witnesses.
    Verify complete two-role C reconstruction, independent C→A initialization,
    explicit history losses, mapped event/reset/replay, and K/K-minus admission.
    Three native methods, 56 rehashed mutations, 14 focused shared methods and
    the phase boundary passed; all 33 cells are reconciled at bounded scope.
    [Crossing review](./phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-CrossingReview.md).
  - [x] User accepted bounded C_RG2b local/crossing reconciliation on 2026-09-15
    and requested its commit before G2. Preserve execution records and nine
    accepted G2 declarations; the integrated G2 decision remains separate.
  - [x] Prepare the integrated C_RG2b G2 proposal from checkpoint `a168b7d`:
    33 exact cells, one zero-duration facade supplement, complete C authority,
    separate initializer/event endpoints and frozen Lipschitz/K/K-minus limits.
    The facade method, 15 focused methods, 42 rehashed mutations and the phase
    boundary pass. Nine accepted G2 declarations are unchanged.
    [G2 review](./phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-G2Review.md).
  - [x] User accepted exact C_RG2b G2 on 2026-09-15. Bind checkpoint `796229e`,
    preserve original evidence and publish the tenth exact declaration through
    the shared adapter. Aggregate P9-7.7, G3 and specialization remain separate.
    [Acceptance](./phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-G2Acceptance.md).
- [x] P9-7.8: Review `P9-G3[S]` for the exact accepted generic support set
  before specialization code. Singleton `P9-G3[C_OS]` can run immediately
  after its G2; unrelated lifecycle/realization rows may remain pending.
  - [x] Review the ten exact accepted declarations and accepted aggregate 7.7;
    bind V4 spec/paper, 73 typed provenance queries and unchanged legacy bytes.
  - [x] Register forward mechanics, 17 expansion/3 metamorphic oracles, G9
    failures and 40 independent disabled surfaces without runtime credit.
    Assign A oracle production to P9-8.3A.1 and runtime to P9-8.3A.2;
    preserve mandatory lifecycle and optional scope.
    [Review](./phase-9-grcv4/tranche-7/P9-7.8-SpecializationReview.md).
  - [x] Expose the checked pending review through API/notebook/browser with
    scope/gate/drift rejection pressure; no new runtime authorization.
  - [x] User accepted the exact G3 consumed set and Tranche 7 closure against
    `c6925b5`; the scoped successor opens only P9-8.1a's V4 topology source/test
    entry. No runtime file is created. [Acceptance](./phase-9-grcv4/tranche-7/P9-7.8-G3Acceptance.md).

## Tranche 7T. Reserved autonomous-topology extension

Research is owned by the
[ATC investigation](./investigations/grc9v4-constitutive-design/decisions/ATCSuccessorInvestigationOpening.md),
not by an implementation leaf. Accepted Tranche 7 and existing machine
permissions are unchanged. Detailed implementation leaves await scientific
closure; this is a dependency reservation, not runtime authorization.

- [x] Reserve investigation → reviewed topology proposal → extension paper →
  normative specification/release → 7T → specialization that actually consumes
  those new autonomous contracts. The blanket Tranche 8 dependency is superseded
  by the 2026-10-01 scoped mechanical continuation.
- [ ] Accept the relevant ATC claim/debt results and ordered propagation.
- [ ] Derive scoped 7T implementation leaves from the accepted contracts.
- [ ] Demonstrate a policy-generated event reached through ordinary evolution,
  complete target admission and continued evolution, with negative controls.
- [ ] Reconcile generic/GRC9V4 ownership and Tranches 8–10 dependencies;
  bind exact prerequisites before any later execution-policy opening.
- [ ] ATC investigation maintenance: reconcile the pre-existing 23 A_OS
  support-file hash changes before relying on fresh full ATC typed ancestry
  for ATC successor acceptance. The RGATC inventory is exact; no blind repin.
  This is not a P9-8.0 or P9-8.1a prerequisite: the new nine-port completion
  proof is self-contained and does not consume that ancestry.

P9-8.1a retains its existing scoped permission. Specified nine-port candidate
detection, request-driven expansion and column field coarse/Split do not await
general ATC. The all-ten feasibility review and explicit user acceptance below
now close P9-8.0 and release its production hold. Later runtime leaves require their exact existing generic and
specialization contracts and scoped execution permission. A missing new
autonomous contract holds only its consumers. No optional spark/hierarchy,
automatic complete request generation or specialization conformance is inferred.

## Tranche 8. D11-G9 mechanical specialization

Entry is the accepted G3 set of ten exact generic declarations, not ten
conformant nine-port models. All-ten bounded feasibility is now reviewed and
user-accepted. P9-8.1 shared mechanics is complete and user-accepted; P9-8.2
is implemented and own-reviewed, then C_OS first while retaining the population. P9-8.1 and P9-8.3
are parent registers with independently reviewed children.
General 7T is not a prerequisite for the defined mechanical scope. Accepted
Tranche 7 and current execution permissions remain unchanged.

- [x] P9-8.0: Close and review all-ten mathematical/construction feasibility
  before any new specialization production work, including P9-8.1a.
  The [readiness inventory](./phase-9-grcv4/tranche-8/P9-8.0-ReadinessReview.md)
  and [initial feasibility record](./phase-9-grcv4/tranche-8/P9-8.0-AllProfileFeasibility.md)
  retain the initial research checkpoints. The subsequent
  [aggregate review and restriction pressure check](./phase-9-grcv4/tranche-8/P9-8.0-AggregateReview.md)
  pass; the user explicitly accepts R1–R10 and the aggregate scope on
  2026-10-02 (“i accept both”). All ten rows are provisionally closed;
  P9-8.0 is complete and its production hold is released. No specialization
  runtime is accepted by this closure.
  Closure means independently justified, numerically feasible constructions
  for all ten declared scopes, not ten native implementations. P9-8.1a's chart
  authority and scoped permission are available; P9-8.1a is the next leaf.
  Completed evidence below is retained; later native work remains separate.

  - [x] Map chart/ports, row backend/weights, candidate detection, D11-G9
    expansion, field coarse/Split and lifecycle to spec/paper/typed authority
    and actual runtime prerequisites. Do not equate field Split with fission.
  - [x] Account for source selection, capacity, chirality, conditional phase,
    resource shares, target template/reference, bond seed and W/Z policies;
    distinguish resolved/source-derived operands from supplied request data.
  - [x] Nominate exact combined identities and source/target domains; check
    numerical admission, zero-resource targets, distinct current/reset roles,
    complete C maps, A initialization and whole-carrier dispositions.
    Construction identities nominated, not admitted as native runtime;
    unconstructed identities remain held by their per-profile oracle owners.
    Confirmed exact reference-cutoff failures on frozen C_OS source/D30 target
    route to P9-8.3C-OS's preproduction oracle work, not to an alteration of the
    resource map or selector. This inventory check does not close admission.
  - [x] Inventory independent vectors/oracles and missing profile-specific
    evidence; retain P9-8.3A.1 and prohibit production-as-oracle expectations.
  - [x] Bind mandatory lifecycle, deep/covariance and four disabled surfaces
    per advertised profile; retain all 40 planned compatibility cells.
  - [x] Explicitly exclude general ATC, automatic complete request generation,
    completed sparks and hierarchy. Route genuinely missing authority through
    claims/paper/spec; allow independent research under the aggregate production hold.
  - [x] Identify later scoped policy openings without granting them in this
    review. No blanket Tranche 8/9 authorization or numerical rerun credit.
  - [x] Apply the user-directed all-ten production hold; preserve historical
    permissions without treating them as current authorization to proceed.
    This hold is now released by the explicit aggregate acceptance below.
  - [x] Retain initial obstruction/control calculations: existing RG2b chart
    excludes zero core for both candidates; reference-baseline continuation
    can fail despite charge conservation; a distinct positive control is bounded.
  - [x] Construct the [bounded reference continuation](./phase-9-grcv4/tranche-8/P9-8.0-BoundaryContinuation.md):
    positive source preimage and fresh row candidate, sixteen role layouts,
    distinct current/reset resources, ten exact target steps, selector gap,
    resource perturbation budget and covariance. Five focused tests pass;
    enabled realizations are not certified by this control.
  - [x] Identify the general auxiliary inverse/graph-transform argument and
    demonstrate the signed inverse needed by an inward zero-core target.
    The small ATC fission certificate is not nine-port evidence. The successor
    below is self-contained and imports no ATC package, fixture or constants.
  - [x] Derive [nine-port fixed-row candidate bounds](./phase-9-grcv4/tranche-8/P9-8.0-FixedRowCandidateBounds.md)
    and retain their independent oracle: proposed A stage binding and history
    interval, strict-gap C current, nonzero-read rate/source bounds, PC envelope,
    local CI/CI+PC contraction and finite continuation. Independent bounded
    mathematical PASS includes the proposed A stage binding. The user's
    2026-10-01 commit instruction accepts this bounded checkpoint; complete
    preimages, numerical admission and aggregate closure remain separate.
  - [x] Close review F1 locally: integrate the supplied A geometry, C modulation
    and actual writer-output assertions; reject all four in-memory mutations
    on the real D52 vector. Nine focused tests pass, including the original
    enabled OS witnesses and the source publication-rounding limitation.
    Retain the inverse-metric derivation and symmetric/star-supported carrier
    domain without changing parameters or the prescribed resource map.
  - [x] Bind OS raw H-space mismatch to the actual normalized split contract
    and proposed research tolerance: Href=I, spectral <= Frobenius, both exact
    ceilings < 2^-40/128. The [numerical successor](./phase-9-grcv4/tranche-8/P9-8.0-OSNumericalFeasibility.md)
    independently checks the exact normalized PSD admission inequality,
    equality and nonidentity-reference rejection. This is not complete native
    profile admission or a uniform chart-wide arithmetic-error certificate.
  - [x] Test the unchanged source and both-role D52 ten-step witness with
    staged binary64 arithmetic, independent high-precision/supplied-H controls
    and separate exact current-block error enclosures. Five focused tests:
    split admission passes, but geometry-to-current effects disappear in all
    42 evaluations; off-diagonal H, Read-Back, C modulation and A history remain.
  - [x] Apply the OS numerical review: retain its bounded PASS/independent
    execution limits, five extra matrix controls and exact A writer ceiling
    <1.695e-21 (resource-only search in the old chart cannot give robust
    one-ULP history discrimination). Correct the stale final work-order paragraph.
  - [x] Construct a separate [OS effect witness](./phase-9-grcv4/tranche-8/P9-8.0-OSEffectWitness.md):
    same topology/arithmetic, explicit revised sensitivities/history, both-role
    interval neighborhoods and ten-step continuation. Source/target geometry,
    actual A writer outputs and their next current consumers clear combined
    full-evaluation errors plus a declared ULP margin. Seven predecessor and
    three successor methods pass locally. Preserve the old loss regression.
  - [x] Retain the [bounded D52 review](./phase-9-grcv4/tranche-8/P9-8.0-OSEffectIndependentReview.md)
    and its isolated execution boundary. Close F1/F2 in the existing owner:
    bind predictor/regenerated geometry to distinct source stages; reject
    incomplete/nonfinite effect vectors and enclosures. Seven successor plus
    seven predecessor tests pass against actual updated repository dependencies;
    substituted regeneration fails both verification paths. Keep parameters,
    precision, tolerances and legitimate zero residuals unchanged.
  - [x] Record user acceptance of the reviewed bounded OS checkpoint and its
    checker corrections through the 2026-10-01 commit instruction. This is not
    native profile binding or all-ten closure. Named-stage effect margins are
    not uniform all-state/all-realization claims.
  - [x] Recheck affected CI/PC/CI+PC estimates before RG2b reuse in the
    [revised realization bounds](./phase-9-grcv4/tranche-8/P9-8.0-RevisedRealizationBounds.md).
    The original five methods establish 50 source/target state-box bounds for both
    candidates: regular currents, local joint roots, symmetric/star-supported
    carrier-ball invariance and both-role ten-step continuation. These are
    exact-real research results, not six native runs
    or automatic replacement of old all-realization/profile identities.
  - [x] Retain the [independent revised-bounds audit](./phase-9-grcv4/tranche-8/P9-8.0-RevisedRealizationIndependentReview.md)
    and its isolated execution limit. Close RR-F1/RR-F2 locally: verify the full
    geometry coordinate hull from endpoint support and bind the source norm
    scalar to the complete matrix sum. Three new methods reject the three
    narrowed enclosures and max-entry scalar, including actual tube-path
    mutations. All eight methods and unchanged 50 boxes pass against current
    repository dependencies. The user's 2026-10-01 acceptance and commit
    instruction accepts the bounded checkpoint (`238978f`). No parameter search, source
    admission or production authorization is inferred.
  - [x] Derive the [new nine-port RG2b completion](./phase-9-grcv4/tranche-8/P9-8.0-RG2bCompletion.md)
    directly for A/C source and D52: signed-resource/scaled-log-history
    retraction of increment arguments, global state/history/geometry slopes,
    selector/floor margins, auxiliary inverse, compact containment and a
    completion-relative bounded Lipschitz section. The original five methods pass;
    50 state boxes establish both-role ten-step physical continuation. This is
    bounded research, not C1 or native admission; review corrections follow.
  - [x] Retain the [bounded RG2b review](./phase-9-grcv4/tranche-8/P9-8.0-RG2bIndependentReview.md)
    and its isolated dependency boundary. Close RG-F1/RG-F2 locally: twelve
    signed/near-face/exterior controls reject fourteen narrowed-clamp cases;
    all four inverse queries independently bind every returned coordinate to
    residual/error and reject stale/zeroed/corrupted certificates. Mutations
    reach the actual evidence consumer. Three new methods bring the current
    repository run to eight passing methods, including unchanged 50-box
    continuation. No parameters, completion domains or tolerances changed.
  - [x] User accepts the bounded reviewed RG2b completion and checker corrections
    through the explicit 2026-10-01 acceptance and commit instruction. Retain
    the old native zero-core incompatibility without altering the resource map.
    Complete profile admission and all-ten production authorization remain open.
  - [x] Establish bounded both-role boundary viability and enabled continuation
    in the accepted source/D52 work: OS witnesses, CI joint-root and PC/CI+PC
    envelope bounds, and RG sections. These are the declared finite-horizon
    results, not an arbitrary-graph or all-parameter theorem. Persistent
    continuation remains conditional on a lawful carrier event policy.
    Reconcile their exact scopes below; do not repeat the accepted derivations.
  - [x] Resolve the zero-resource obstruction mathematically with the accepted
    new A/C RG2b completion (`d6d3647`) on its source/D52 domain. Preserve the
    old native completion's incompatibility and the prescribed resource map.
    Represented evaluation and complete research-profile binding remain below;
    no native replacement, C1 or completion-independent claim follows.

  - [x] Pin the [all-ten research scope](./phase-9-grcv4/tranche-8/P9-8.0-AllProfileFeasibility.md#pinned-all-ten-research-scope--2026-10-02)
    and map accepted evidence to it (2026-10-02): exact parameters,
    source/target graphs and capacities, candidate/backend stages, geometry/
    history/carrier domains, both roles, duration and continuation horizon.
    Record restrictions explicitly. A finite union is not its surrounding
    rectangle; revised D52 evidence does not cover all allocator layouts.
    Pin the previously selected D52 positive-chirality phase-3 fixture by name;
    distinguish its local runs from isolated reviews describing negative chirality.
    Three focused scope tests cover exact ports/capacity, bad or reordered
    fixtures and the actual research consumers. This is performed reconciliation,
    not user acceptance of restrictions, a new review or complete row closure.

  - [x] Construct and locally verify the [A/C RG numerical successor](./phase-9-grcv4/tranche-8/P9-8.0-RG2bNumericalFeasibility.md)
    (2026-10-02): finite inverse-chain residuals, section truncation and complete
    evaluation errors with frozen argument completion at every depth. Fifty
    nominal read stages and both-role ten-step continuation pass; 44 named
    effect checks include RG/OS discrimination, CI defects and A history's next
    RG current. Four methods reject altered clamps, corrupt chains and wrong
    realization outputs through the actual consumer. This separate binary64
    NumPy research arithmetic inherits no OS margins. No uniform all-box
    floating-point or accumulated trajectory-error claim. The 2026-10-02 commit
    instruction accepts this bounded checkpoint. The supplied numerical audit
    supports the RG mathematics; actual evaluator review and complete RG
    profile/event/oracle bindings remain open.

  - [x] Construct and locally verify the [six-profile CI/PC/CI+PC numerical successor](./phase-9-grcv4/tranche-8/P9-8.0-RealizationNumericalFeasibility.md)
    (2026-10-02): nine methods pass after review corrections, covering 150 nominal
    read stages, both-role ten-step targets and 124 defining-effect comparisons through next W/Z
    consumers. Represented root/error certificates bind old-carrier reads and
    same-source writers. Nonzero target carriers are separately supplied, not
    an accepted event transfer. Retain the C_PC reset margin failure and its
    algebraically equivalent compensated C correction with unchanged precision
    and effect threshold. Bounded independent review passes with RN-F1 corrected
    locally. The user accepts this bounded checkpoint through the 2026-10-02
    commit instruction. No OS margins, uniform all-box
    arithmetic claim or native solver acceptance is imported.

  - [x] Retain the [numerical independent review and portable evidence](./phase-9-grcv4/tranche-8/P9-8.0-RealizationNumericalIndependentReview.md)
    and correct RN-F1: verifier entry snapshots, separate producer work arrays,
    thirteen altered-target rejections and the exact equilibrium counterexample.
    Preserve intended-exact enclosures, lawful scratch writes and caller inputs.
    Six wrong C response orders and eight naive carrier-copy cases also reject.
    This is local correction/validation, not a second independent audit. The
    user accepts the bounded successor and correction through the 2026-10-02
    commit instruction. The actual RG evaluator still needs review; aggregate
    P9-8.0 acceptance and production remain held.

  Remaining P9-8.0 work follows the
  [bounded deliverables and stopping criteria](./phase-9-grcv4/tranche-8/P9-8.0-AllProfileFeasibility.md#bounded-construction-deliverables-before-production).
  These are research inputs for later owners; completing P9-8.1–8.3 or newly
  admitting the research profiles natively is not a prerequisite. All items
  retain their stated status below, including the OS, persistent, CI and RG
  construction increments. The scope clarification itself supplied no
  construction result; local increments do not close aggregate acceptance.

  - [x] Review the actual RG numerical evaluator with independent numerical
    equations and adversarial controls, and resolve its
    findings on the pinned scope. The supplied mathematical review did not
    include that implementation. The [actual-source review package](./phase-9-grcv4/tranche-8/rg-numerical-review/README.md)
    now supplies pinned source/dependencies, local snapshot replays and a portable
    export. The user's subsequently requested [own implementation review](./phase-9-grcv4/tranche-8/rg-numerical-review/SelfReview.md)
    executes that source and uses independent equations, but is not an external
    independent verdict. Four findings are corrected locally. The user explicitly
    accepts the own review, RG-NR1–4 corrections and this bounded review
    disposition through the 2026-10-02 acceptance/commit instruction; external
    audit authorship and aggregate acceptance are not inferred.
  - [x] Perform the requested own RG implementation review and pressure the
    actual consumer: ten methods pass after RG-NR1–4 corrections, including
    malformed chains at every depth, complete read fields, private input
    ownership, point/intended admission, clamp faces, equilibria and outliers.
    Separate 90-digit equations enclose 7,188 entries. Four original numerical
    and seven event methods pass with every nominal report field unchanged.
    Retain before/after evidence and corrected-source provenance. The user
    explicitly accepts this bounded review/correction checkpoint through the
    2026-10-02 acceptance/commit instruction; aggregate acceptance stays open.
  - [x] Bind complete mathematical source/request/target operands for all ten
    rows on the pinned source/positive-D52 case, both roles and ten-step horizon.
    Start with a shared operand record and independently checked C_OS companion;
    include complete C reference maps, then A fixed-row/initializer/reference-
    current and W recipes. Supply or derive every operand; retain intended
    identity preimages. Native descriptor registration/serialization is later.
    The [selected-case reconciliation](./phase-9-grcv4/tranche-8/P9-8.0-SelectedCaseCompatibility.md)
    now maps complete research records, inherited fields, numerical owners and
    target oracles for all ten rows. Remaining review and aggregate acceptance
    stay open; native identity completion is later.
  - [x] Construct and locally verify the first
    [shared-input/C_OS companion](./phase-9-grcv4/tranche-8/P9-8.0-EventConstruction.md)
    (2026-10-02): explicit rational inputs and complete C references, independent
    charge-preserving transfer, actual current/reset targets, fresh current
    trigger, absent W/Z, both-role ten-step continuation and final reads.
    Seven methods pass after the [bounded audit](./phase-9-grcv4/tranche-8/P9-8.0-EventIndependentReview.md):
    retain six effects, ten input mutations and thirteen transfer-consumer
    rejections; add thirteen consumed-model rejections, entry ownership at
    final/effect reads and a final-only fault through actual continuation.
    EC-F1/EC-F2 are corrected locally. The user accepts this bounded checkpoint
    through the 2026-10-02 commit instruction; the
    all-ten bindings/oracles and C_OS row are not closed.
  - [x] Construct and locally verify the [A_OS lineage/initialization companion](./phase-9-grcv4/tranche-8/P9-8.0-AEventConstruction.md)
    (2026-10-02): preserve old W by exact edge lineage, seed new W with bond 1,
    derive and certify fresh role-entry reference currents and independently
    check the actual event outputs. Six methods pass, including both-role
    ten-step continuation, eight effects through the next W consumer and
    binding/producer mutations. The [independent review](./phase-9-grcv4/tranche-8/P9-8.0-AEventIndependentReview.md)
    passes the bounded construction. AEC-F1 now isolates writer-control C/W/J,
    certifies entry-point W error and retains a separate intended-exact branch;
    twelve mutation controls and the actual effect-consumer regression reject,
    four scratch controls pass, and nominal report fields are unchanged.
    Historical audit results are retained portably. This selects the allowed
    lineage/new-edge initialization branch. The user accepts this bounded
    checkpoint through the 2026-10-02 commit instruction; P9-8.3A.1 and the
    A_OS feasibility row stay open.
  - [x] Select and locally validate the [whole-source archive/whole-target zero-reset policy](./phase-9-grcv4/tranche-8/P9-8.0-CarrierEventConstruction.md)
    for A_PC, C_PC, A_CI_PC and C_CI_PC (2026-10-02), separately from A W
    history. Check each role's complete actual source archive, exact target
    zero, support/symmetry/norm and explicit carrier-only loss; recheck actual
    target reads, ten-step continuation and affected defining effects under
    unchanged thresholds. Five methods and 68 effect comparisons pass; the
    minimum margin exceeds 1.421. PC geometry/carrier effects begin after the first
    nonzero write; CI+PC additionally has its instantaneous source at entry.
    Reuse the accepted whole-carrier-ball envelope. Direct old-edge copying
    remains forbidden. The [bounded review](./phase-9-grcv4/tranche-8/P9-8.0-CarrierEventIndependentReview.md)
    passes; CEC-F1 now anchors the complete archive and resource/W transfer to
    an independent initial-record and physical-stage oracle. Eight probe-write
    and four dropped-source-writer substitutions reject through the event path.
    Audit evidence is retained portably. The user accepts this bounded checkpoint
    through the 2026-10-02 commit instruction; no native policy/receipt or
    all-ten oracle item closes.
  - [x] Construct and locally verify the [A_CI/C_CI event companion](./phase-9-grcv4/tranche-8/P9-8.0-CIEventConstruction.md)
    (2026-10-02): exact role source-stage binding, resource/W or C-reference
    transfer, fresh CI-root reference currents, absent Z/archive/loss channels,
    both-role ten-step continuation and final reads. Six methods and 22 named
    target effects pass with minimum margin above 1.995. Eight wrong source
    stages, three constructed-model substitutions, sixteen forged outputs,
    three producer-input shifts, two wrong references and four changed recipes
    reject; lawful scratch writes pass. Reuse accepted root certificates and
    the AEC-F1 writer guard. The [bounded review](./phase-9-grcv4/tranche-8/P9-8.0-CIEventIndependentReview.md)
    passes without a new blocking finding; no corrective iteration is needed.
    Only the supplied report was available for retention. The user accepts this
    bounded checkpoint through the 2026-10-02 commit instruction; actual RG
    numerical review and selected-case compatibility are separate
    obligations below.
  - [x] Construct and locally verify the [A_RG2b/C_RG2b event companion](./phase-9-grcv4/tranche-8/P9-8.0-RGEventConstruction.md)
    (2026-10-02): bind actual role source stages, C/W or C references, absent
    carrier channels and each target's own completion-relative section. Seven
    methods and 26 target comparisons pass, with minimum margin above 1.371;
    both roles admit ten target steps and final reads. First inverse core
    coordinates remain negative after full error/tail allowances. Entry-owned
    chain/read/write certification rejects source-chain substitutions, shifted
    producer inputs and corrupted outputs. The [bounded construction review](./phase-9-grcv4/tranche-8/P9-8.0-RGEventIndependentReview.md)
    passes without corrections under reconstructed dependencies; only its report
    was available. The user accepts this checkpoint through the 2026-10-02 commit
    instruction. The subsequent actual RG own-review/correction checkpoint
    above is now explicitly accepted.
  - [x] Derive independent bounded event/target expectations for all ten rows:
    event preconditions/trigger, topology/role IDs, resources, W or C references,
    Z disposition, target-zero admission, positive continuation and defining
    effects at declared stages.
    Retain distinct current/reset inputs and focused construction failures.
    Research oracles feed P9-8.3A.1 and corresponding C owners; full native
    fixture encodings, runtime receipts and comprehensive failure suites stay
    with their later acceptance/execution work. The five accepted companions
    supply these local expectations for all ten rows; the actual RG numerical
    owner's user-requested own-review/correction checkpoint is now accepted;
    aggregate technical review and explicit restriction/user acceptance are
    complete below.
  - [x] Check selected-case transfer compatibility: charge, W/Z disposition,
    target/reset domain inclusion and failure/no-publication expectations.
    Map lifecycle and disabled projection to accepted contracts and identify
    conflicts. Reuse generic arguments; actual rollback/replay, crossings and
    forty disabled-runtime cells remain later. Route genuinely absent authority
    through claims → paper/spec before implementing its consumers. The
    [local argument](./phase-9-grcv4/tranche-8/P9-8.0-SelectedCaseCompatibility.md)
    establishes shared exact transfer/history identities, maps actual target
    domains and existing lifecycle rules, and retains the selected legacy
    undefined-domain rejection. Native charge-policy arithmetic and runtime
    transaction checks remain later. The user accepts this bounded reconciliation
    through the 2026-10-02 commit instruction. The subsequent explicit
    aggregate acceptance below closes the rows under R1–R10.
  - [x] Review all ten disposition rows against the concrete deliverables. The
    [aggregate own review](./phase-9-grcv4/tranche-8/P9-8.0-AggregateReview.md)
    passes all twenty profile/role paths and 103 event-output rejection controls;
    all ten rows are now provisionally closed after explicit acceptance.
    Historical-box versus actual-query coverage and stale RG review status
    are reconciled; no new numerical blocker.
  - [x] Accept the aggregate review's R1–R10 restrictions explicitly. No
    unresolved row or silently dropped profile at production entry without a
    user-approved scope change. The user explicitly accepts R1–R10 on
    2026-10-02 (“i accept both”); no acceptance is inferred from test passes.
  - [x] User accepts the aggregate bounded feasibility scope before production
    resumes. Explicitly accepted on 2026-10-02 in the same “i accept both”
    instruction. Later native gates and specialization leaves remain independent.

P9-8.0 does not execute later runtime acceptance: chart/row/backend and allocator
implementation belong to P9-8.1–8.2; native profile integration and oracle
comparisons to P9-8.3; deep/covariance/atomicity execution to P9-8.4–8.6; mandatory
specialization lifecycle and all forty disabled executions to Tranche 9.
ATC ancestry maintenance remains with the investigation/7T reservation above.
These obligations are retained, not waived or relabeled as feasibility passes.

After aggregate feasibility review, implementation order: C_OS first;
then independent A_OS and C_PC branches; remaining
CI/PC/CI+PC products; both RG2b products last. Shared mechanics are reused;
target/history/readmission/lifecycle acceptance remains profile-specific.

- [x] P9-8.1: Complete and accept shared mechanics across `.a`–`.e` below.
  The user explicitly accepts the complete parent on 2026-10-02 and requests
  merging `work/p9-8-1-shared-mechanics` into `main`. The final implementation
  subject is `c27583cc476b0c4cbdd63d3428d611b423389f04`; see the
  [parent acceptance and child checkpoints](./Phase-9-GRCV4-Handoff.md#p9-81-shared-mechanics-parent-acceptance).
  Allocator, native profile integration and later conformance duties retain
  their existing owners; the end-of-Tranche-8 cache review remains open.
- [x] P9-8.1a: Implement and verify the fixed chart and port graph.
  The subitems below are checkpoints within the existing `P9-8.1a` leaf,
  not new machine gates or independent permission requests. Each implementation
  increment carries focused tests and its exact work-manifest binding under
  `P9-8.1a`; the parent closes after all four are verified and reviewed.
  The [current boundary reconciliation](./phase-9-grcv4/tranche-8/P9-8.1-BindingReconciliation.md)
  passes the entry audit before `.2`; `.4` also requires a passing boundary on
  its exact subject. Historical scientific-source failures in that review
  retain their separate scopes.
  [Scope and exit criteria](./Phase-9-GRCV4-ImplementationPlan.md#p9-81a-work-breakdown).
  All four checkpoints now pass the implementation/own-review criteria;
  [parent review](./Phase-9-GRCV4-Handoff.md#p9-81a4-integrated-review-and-parent-completion).
  This closes chart/graph work only, without opening later native scopes.

  - [x] P9-8.1a.1: Fixed chart and endpoint primitives. Implement the exact
    port ↔ row/column bijection, immutable row/column partitions and validated
    endpoints. Verify all nine ports and inverse pairs; reject malformed types
    and out-of-range coordinates without confusing rows with columns.
    Implemented in [V4 topology](../src/pygrc/models/grc_9_v4_topology.py), with
    seven focused methods plus sixteen generic graph regressions passing;
    Ruff/mypy pass and both new source/test hashes are registered under
    `P9-8.1a`. This checks off the primitive implementation only. The global
    phase-boundary check initially failed on pre-existing bindings, now
    reconciled by the linked boundary review; see the
    [execution note](./Phase-9-GRCV4-Handoff.md#p9-81a1-chart-and-endpoint-implementation).
  - [x] P9-8.1a.2: Immutable port-graph admission. Bind stable node/edge IDs,
    edge kinds, live endpoints and tail/head orientation. Reject duplicate IDs,
    dangling endpoints and repeated `(node_id, port)` occupancy, including
    collisions hidden by distinct parallel-edge IDs. Preserve legal parallel
    edges; prove caller mutation cannot alter admitted graph contents.
    Preserve the schema's empty-string node IDs and nonempty edge IDs; exercise
    present/absent `""` membership, normalized `1`/`1.0` duplicates and distinct
    `1`/`"1"` occupancy. Reassess equality/hash if endpoint field types change.
    Implemented with frozen, slotted `GRC9V4PortEdge`/`GRC9V4PortGraph`, copying
    and revalidating nested input records. Loops require two distinct ports;
    event-specific loop eligibility remains with D11-G9. All 39 focused methods
    pass (16 new, 7 prior chart/endpoint, 16 generic graph), including 1,296
    incidence patterns; Ruff, mypy and the current phase-boundary audit pass.
    Exact source/test bindings remain under `P9-8.1a`; see the
    [execution note](./Phase-9-GRCV4-Handoff.md#p9-81a2-immutable-port-graph-admission).
    The user explicitly accepts this structural checkpoint and its recorded
    interpretations on 2026-10-02 (“Great, accept and commit”); `.3`/`.4` were
    still open at that checkpoint.
  - [x] P9-8.1a.3: Graph payload, digest and generic projection. Reuse the
    accepted canonicalization and identity contracts; round-trip the port-graph
    envelope and independently recompute its payload-only digest. Provide the
    deterministic read-only generic graph projection with stable edge identity
    and orientation; establish that no second authoritative graph is created.
    Decode through graph admission and project only admitted graphs. Use
    typed/JCS payload identity; Python hashes confer no graph identity.
    Implemented on the same graph owner, with an alias for the normative
    `GRC9V4SerializedPortGraph` name and computed schema/digest properties.
    The immutable generic topology view retains only the admitted port owner;
    its identities delegate to that owner and it exposes no separate codec.
    All 80 focused methods pass (39 topology, 16 generic graph, 25 codec),
    including the frozen vector and seven rehashed structural defects through
    four admission routes. Ruff, mypy and the current phase-boundary audit pass;
    see the [execution note](./Phase-9-GRCV4-Handoff.md#p9-81a3-graph-envelope-identity-and-projection).
    Generic numerical/row-weight integration remains with later leaves; `.4`
    still owns the integrated parent review.
  - [x] P9-8.1a.4: Integrated boundary checks and parent review. Exercise the
    frozen graph-envelope vector, malformed/rehashed payloads, port-capacity
    edges, orientation reversal and input ownership across the actual consumers.
    Record focused results, exact source/test identities and the existing
    execution-boundary check; review the complete chart/port graph before
    marking the parent complete. Lifecycle, allocator and profile conformance
    remain with their later owners. The initial thirteen maintenance and
    twenty-five work-entry mismatches, omitted committed files and optional
    dependency integration are reconciled in the linked review. Repeat the
    current boundary audit after `.2`–`.4` edits; the passing `.1` maintenance
    subject cannot be reused as evidence for later implementation bytes.
    Own review found and closed the common interface's missing explicit
    port-to-edge lookup with validated `edge_at(node_id, port)`. The frozen
    source and 17 target graphs pass structural/identity checks, all 512
    saturated-star orientations pass, and the 1,296 incidence patterns pass
    canonical admission (360 admitted, 936 rejected). All 72 rehashed tenth-
    incidence attempts reject across two wire routes and star/loop layouts.
    Input/export ownership, warm malformed inputs and three process hash seeds
    also pass. All 88 focused methods, Ruff, mypy and the current phase-boundary
    audit pass; exact source/test identities and bounded review disposition
    are in the linked parent review. Performance/cache review stays scheduled
    at the end of Tranche 8; no cache optimization or expansion execution is
    claimed here.
- [x] P9-8.1b: Implement and verify row differential and V4 row-weight bridge.
  Deliver the following checkpoints together, as requested on 2026-10-02;
  they are recorded subitems, not separate acceptance gates or turn boundaries.
  Formal runtime ownership remains `P9-8.1b` in the existing topology source/test
  paths. Preserve the accepted `.a` subject and historical G3 decision.
  - [x] P9-8.1b.1: Bind the closed row-weight policy and immutable, graph-bound
    input contract, with explicit post-beat stage and Hessian sign.
  - [x] P9-8.1b.2: Implement fixed-row gradient, diagonal/signed Hessian,
    outward row flux and the separately named legacy node tensor. Check zero
    rows, parallel edges, loops, both signs and numerical extremes.
  - [x] P9-8.1b.3: Select A weights from committed W_A, C weights by complete
    stable-edge W_C_tr coverage, and disabled weights from the exact delegate's
    native base conductance. Preserve sole graph ownership and reject stage,
    candidate, shape and identity mismatches without fallback.
  - [x] P9-8.1b.4: Review the integrated bridge against independent equations,
    covariance, mutation and stale-input cases; record exact subjects and pass
    the affected regressions and current phase-boundary audit.
  All four checkpoints are implemented and own-reviewed together; see the
  [review and exact subjects](./Phase-9-GRCV4-Handoff.md#p9-81b-row-differential-and-weight-bridge).
  Evidence covers 512 orientations, 120 independent Decimal cases, numerical
  extremes, all ten declaration shapes, actual generic A/C commit handoffs and
  exact delegate-native conductance inspection. This is shared mechanical
  completion, not native specialization lifecycle or disabled conformance.
  The user explicitly accepts the complete reviewed P9-8.1b result on
  2026-10-02 (“review passes fully. commit changes”), within the recorded scope.
- [x] P9-8.1c: Implement and verify the mechanical candidate trigger.
  Deliver these checkpoints together under the 2026-10-02 user request, with
  formal ownership `P9-8.1c` in the reviewed V4 lifecycle source/test paths.
  They are recorded subitems, not separate gates or turn boundaries.
  - [x] P9-8.1c.1: Bind the closed spark policy, explicit baseline-lane support
    and fresh postbeat input contract. Keep basin seeds, candidates, expansion
    and completed sparks distinct.
  - [x] P9-8.1c.2: Implement exact occupied-port saturation and the strict
    gradient/signed-Hessian conjunction, with stable node order and no cache
    or caller-supplied verdict. Preserve basin classification as a separate test.
  - [x] P9-8.1c.3: Exercise an admitted saturated source through a real ordinary
    commit and fresh detection, retaining independent candidate expectations.
    Optional column-H assistance must reject explicitly when unsupported;
    no legacy thresholds or history controls are inferred into V4 policy.
  - [x] P9-8.1c.4: Pressure threshold equality and adjacent floats, numerical
    outliers, occupancy, orientation, stale inputs and stage/identity/type
    failures; record exact subjects and pass current boundary checks.
  All four checkpoints pass together; see the
  [review and exact subjects](./Phase-9-GRCV4-Handoff.md#p9-81c-mechanical-candidate-trigger).
  Evidence includes all 512 occupancy masks, 180 independent Decimal cases,
  strict boundary/outlier decisions and an admitted saturated C_OS commit.
  Optional column-H execution rejects explicitly; expansion, completion and
  native specialization lifecycle retain their later owners. The user explicitly
  accepts this complete reviewed result on 2026-10-02 ("accpeted and commit
  changes"), within the recorded baseline scope and integration limits.
- [x] P9-8.1d: Implement and verify column coarse-graining and Split.
  Content-specific checkpoints, delivered together under the user's request;
  formal source/test ownership remains `P9-8.1d` in the topology module.
  - [x] P9-8.1d.1: Implement nonnegative column totals, exact simplex profiles
    and inverse Split, including canonical uniform zero columns and explicit
    binary64 reconstruction admission. Verify both inverse identities.
  - [x] P9-8.1d.2: Implement signed flux as independent positive/negative
    channels; enforce disjoint support and field-family dispatch. Pressure
    cancellation, mixed signs and invalid alternate encodings.
  - [x] P9-8.1d.3: Bind fine/coarse snapshots to the sole port graph and closed
    policy; gather edge fields with correct local signs and port placement.
    Check topology/value replacement, typed node order, immutable ownership
    and exact numerical outliers without introducing a cache or graph fission.
    Record the integrated evidence and current phase-boundary check.
  All three checkpoints pass together; see the
  [review and exact subjects](./Phase-9-GRCV4-Handoff.md#p9-81d-column-coarse-graining-and-split).
  Both inverse identities hold exactly on the recorded binary64 reconstruction
  domain. Evidence covers 512 support masks, 27 column-sign patterns, 200
  wide-scale Decimal cases, both loop ports, parallel edges and 16 orientations.
  No model cache or native facade/capability wiring is introduced. The user
  explicitly accepts current `.d` on 2026-10-02 and requests committing it
  before `.e`. This accepts the recorded mechanical/default-backend result;
  the identified backend abstraction gap is assigned to `.e` below.
- [x] P9-8.1e: Align shared mechanics with the accepted V4 exact-backend contract.
  - [x] P9-8.1e.1: Replace direct runtime `Fraction` use throughout `.b`–`.d`
    with `ExactScalar`/`exact_number` and backend-neutral ratio extraction.
    Bind retained exact values to their backend, preserving binary64 boundaries,
    exact coarse reconstruction domain, identities and failure behavior.
  - [x] P9-8.1e.2: Extend the source guard to GRC9V4 and verify real Python/FLINT
    parity, native scalar use, scope restoration and cross-backend handling,
    including threshold, subnormal, overflow and malformed-input cases.
  - [x] P9-8.1e.3: Audit P9-8.0's use of exact arithmetic, distinguishing
    independent proof/test oracles from runtime consumers. Record the supported
    conclusion without rewriting accepted proof artifacts or implying new
    scientific/backend acceptance. Reconcile bindings and phase-boundary checks.
  All three correction obligations pass; see the
  [review and P9-8.0 finding](./Phase-9-GRCV4-Handoff.md#p9-81e-exact-backend-correction-and-p9-80-audit).
  Validation includes 173 regression/backend methods, 14 unchanged P9-8.0
  probe executions nested across both backends and pinned `.d` identities.
  Independent proof `Fraction` use is retained; no P9-8.0 proof defect was
  identified by this audit. The user's 2026-10-02 request to commit the completed
  changes accepts `.e` and its bounded audit finding, without broader native/FLINT
  conformance acceptance.
- [x] P9-8.2: Implement exact D11-G9-P4a boundary reservation, primary spine,
  both chiralities, conditional phase, tree construction, and capacity rules.
  Requested on 2026-10-03 after P9-8.1 acceptance and merge at `184919b`.
  Deliver these content-specific substeps together on
  `work/p9-8-2-expansion-allocator`; they are not separate acceptance gates.
  - [x] P9-8.2.1: Admit the closed request/policy and source bindings, compute
    exact capacity, conditional phase and noncircular event identity; check
    digest assertions and reject source loops before constructing the target.
  - [x] P9-8.2.2: Reserve inherited boundary ports first, build both primary
    spines and the arbitrary-size creation-order BFS/rotor tree, preserving
    old identities/orientations and allocating collision-free role IDs with
    uniform internal reference seeds. Return an immutable admitted graph plan.
  - [x] P9-8.2.3: Execute frozen allocation and covariance vectors, independent
    capacity/tree oracles, deep recursion and malformed/outlier pressure;
    review exact subjects and pass the current phase-boundary audit.
  Resource/history transfer, target numerical admission and atomic publication
  remain with P9-8.3 and the later lifecycle owners.
  All three implementation/own-review substeps pass; see the
  [review and exact subjects](./Phase-9-GRCV4-Handoff.md#p9-82-pure-expansion-allocator).
  Evidence covers 17 frozen allocation vectors, three metamorphic vectors,
  four preallocation failure vectors, 224 independent tree layouts through
  1,004 nodes, 512 orientations and real Python/FLINT parity. The exact-simplex
  wire restriction and its P9-8.0 research distinction are recorded for P9-8.3.
  The user explicitly accepts the reviewed implementation on 2026-10-03
  ("implementation mathches specs and papers, accepted"), with commit and
  merge requested before continuing with P9-8.3C-OS.
- [x] P9-8.3C-OS: Verify C_OS event/node/edge IDs, current/reset resource
  distribution, C reference transport, and carrier `not_applicable` semantics.
  Execute on `work/p9-8-3-profile-integration` after accepted P9-8.2 merge
  `79e0e8f`, as requested on 2026-10-03. Record projection/identity integration,
  pure resource/reference reconstruction, and event admission/publication plus
  independent continuation/failure/replay checks together.
  - [x] P9-8.3C-OS.1: Connect numerical coordinates to the sole immutable port
    owner; preserve generic graph bytes; bind specialization, combined model,
    native reset and scientific identities.
  - [x] P9-8.3C-OS.2: Rebuild the complete stable-edge C reference/Hodge map
    and target profile; apply the exact satellite resource transform to current
    and reset independently; require rederived C and absent carrier channels.
  - [x] P9-8.3C-OS.3: Complete integrated own review of source/target numerical
    admission, independent continuation, native receipts, rollback and replay.
  The implementation is an internal C_OS event owner with unit measures and
  zero structural K4 base; the separately identified native fixture uses dyadic
  shares `(1/2,1/4,1/4)` and one shared charge target. Full public model lifecycle,
  later profiles and broader numerical claims remain separate.
  The user explicitly accepts this bounded checkpoint and its pressure-review
  correction on 2026-10-03 ("this is much better, great. accept and commit").
  All three checkpoints pass own review: 267 passing regression methods plus
  one opt-in package skip, seven scope checks, three original cutoff probes,
  twelve side-tool provenance checks, Ruff and targeted strict mypy.
  The additional paper/side-tool pressure review corrected missing full OS
  current/reset readmission; actual split, conditioning, nonfinite and charge
  failures now have atomic rollback regressions. Weighted/oriented equation
  checks pass; simplex-vertex events do not guarantee nonnegative subsequent
  continuity. See the [pressure findings](./Phase-9-GRCV4-Handoff.md#p9-83c-os-pressure-review) and
  [bounded review and exact subjects](./Phase-9-GRCV4-Handoff.md#p9-83c-os-native-event-integration).
  During P9-8.0 feasibility, construct an independently checked, separately identified numerical
  source/target companion to the frozen allocation vectors; preserve the
  P9-8.0 exact-cutoff regression. Include distinct current/reset roles, zero
  resources, source/target admission and continuation. Execute natively only
  after aggregate feasibility review. Do not reinterpret
  construction-vector `committed: true` as native numerical success.
- [x] P9-8.3C-PC: After C_PC's G2 and G3 entry, execute the separate C_PC
  nonnull carrier reset/loss vector and target readmission. The bounded native
  implementation and pressure review are user-accepted on 2026-10-03
  ("great, then commit changes"), after confirmation of the paper, side-tool
  and adversarial numerical checks and their recorded limits.
  Requested on 2026-10-03 after accepted C_OS commit `eeb82e9`; execute these
  content-specific checkpoints together on `work/p9-8-3-profile-integration`:
  - [x] P9-8.3C-PC.1: Bind whole current/reset carrier content to the frozen
    reset/loss policy; archive source order/content and zero every target
    carrier coordinate while rebuilding the complete C reference profile.
  - [x] P9-8.3C-PC.2: Integrate native PC state, old-carrier numerical
    readmission, atomic event/archive/receipt publication and checkpoint replay.
  - [x] P9-8.3C-PC.3: Independently check source carrier writing, both-role
    target continuation, delayed carrier effects and adversarial domain/history
    failures against the paper, frozen vector and accepted carrier companion.
  The regression batch passes (329 methods, one opt-in packaging skip), including
  independent source writing and ten target steps for each role; 13 focused
  authorization/cutoff checks and 12 side-tool checks pass. The real target
  whole-chart failure probe rejects atomically despite regular point currents.
  See the [C_PC review and exact subjects](./Phase-9-GRCV4-Handoff.md#p9-83c-pc-whole-carrier-event-integration).
- [x] P9-8.3C-CI: Native C_CI event integration after exact C_CI G2/G3,
  requested on 2026-10-03 after accepted A_OS commit `ba5cf5c`. The bounded
  implementation and pressure review are explicitly user-accepted on 2026-10-03
  ("found it. accept and commit"), including their documented scientific and
  side-tool scope limits. All content-specific checkpoints are complete:
  - [x] P9-8.3C-CI.1: Bind the nonpersistent C template/authority and complete
    target references; use the unchanged certified joint-root solver for both
    roles, with separately identified native and research domain norms.
  - [x] P9-8.3C-CI.2: Integrate exact two-role resource transfer, fresh selected
    source reference currents, full target root/domain and row readmission,
    atomic receipts/reference evidence, and deterministic checkpoint replay.
  - [x] P9-8.3C-CI.3: Complete independent paper/interval/side-tool pressure,
    actual source and both-role ten-step continuations, genuine domain and
    iteration failures, outliers, rollback/replay, and portable boundary review.
  All three checkpoints pass own review: 16 native pressure tests, 208 shared
  regressions, six unchanged research tests, 12 side-tool checks, targeted
  Ruff/mypy and the phase boundary audit. Explicit domain limits remain in
  scope and are included in this explicit acceptance.
  See the [C_CI runtime review](./phase-9-grcv4/tranche-8/P9-8.3C-CI-RuntimeReview.md)
  and [validation](./phase-9-grcv4/tranche-8/P9-8.3C-CI-Validation.json).
- [x] P9-8.3A: Reconcile acceptance of both children for the same exact A scope;
  template identity alone is not expansion evidence. C-family work is independent.
  Reconciled for the bounded A_OS scope on 2026-10-03: both children are
  explicitly user-accepted. Other A profiles remain open in the register below.
  - [x] P9-8.3A.1: Own the independent oracle for each selected exact A profile,
    starting with A_OS. Prepare and review its bounded mathematical inputs and
    expectations during P9-8.0 using accepted port/chart, fixed-row initializer
    and D11-G9 contracts; this research preparation has no production-runtime
    or new native G2/G3 prerequisite. Formal oracle acceptance for an exact
    native scope still requires that scope's A G2 and consumed-set G3 and an
    explicit match to the research binding; do not infer it from family labels.
    Bind source/target IDs, distinct current/reset inputs, old/new-edge W,
    reference-current recipe, W/Z loss channels, expected resource/receipt/
    readmission outcomes and rollback cases. Reuse the P9-8.0 expectations,
    completing native identity/fixture details for that scope outside the frozen
    release. Review and accept before runtime comparison; P9-8.0 closure alone
    does not mark this leaf or the runtime coverage hold complete.
    A_OS oracle preparation and own review are complete on 2026-10-03 after
    accepted C_PC commit `4f82313`; explicitly user-accepted on 2026-10-03
    ("ok, accept and commit, then do A.2"). Three
    preparation checkpoints cover exact native/history/reference bindings,
    independent point/interval expectations, and adversarial consumer review.
    The pinned oracle covers 25 positive comparisons and a target OS split
    failure despite a regular current and positive updates. A.1 was separated
    because the then-current generic A evaluator required WLS; A.2 now supplies
    the explicit fixed-port-row incoming-W bridge. See the
    [A_OS oracle review](./phase-9-grcv4/tranche-8/P9-8.3A.1-AOS-OracleReview.md).
    A_CI preparation and bounded own review are complete on 2026-10-03 after
    accepted C_CI commit `2a1d6c0`; A_CI oracle explicitly user-accepted on
    2026-10-03 ("i accept, coninue with A_CI runtime and closure"), distinct
    from the accepted A_OS scope. Its preparation checkpoints are:

    - [x] Bind exact A_CI profile/domain and fixed-row descriptor, independent
      current/reset inputs, W lineage, native identity and reference recipes.
    - [x] Construct and independently certify 25 simultaneous-root/continuation
      expectations, full Frobenius domains and a genuine target self-map exit.
    - [x] Complete 15 oracle pressure methods, 18 full-error/ULP effect controls,
      paper/spec and side-tool review; record the exact CI proof/replay bridge.
    - [x] Accept this exact A_CI oracle before A_CI `.2` runtime comparison.
      The [acceptance record](./phase-9-grcv4/tranche-8/P9-8.3A.1-ACI-Acceptance.json)
      pins the reviewed working-tree bytes; all four oracle subjects are unchanged.

    See the [A_CI oracle review](./phase-9-grcv4/tranche-8/P9-8.3A.1-ACI-OracleReview.md)
    and [portable validation](./phase-9-grcv4/tranche-8/P9-8.3A.1-ACI-Validation.json).
    A_PC preparation and bounded own review are complete on 2026-10-03 after
    accepted A_CI commit `d431e2e`; explicitly user-accepted on 2026-10-03
    ("accept and commit, then continue with A_PC"), including its separately
    declared native fixture. Its preparation checkpoints are:

    - [x] Separate the local research domain from the native full compact chart;
      prove the uniform source/carrier bound and retain the small-radius
      counterexample. Proposed R=2048, kappa_H=2^-14, M=16 and W in [1/2,513/512].
    - [x] Bind independent physical source stages, old W near 15/16 with exact
      lineage/unit new seeds, whole Z archives/zero resets, shares (1/4,3/8,3/8),
      native identity preimages and distinct W/Z receipt channels.
    - [x] Independently certify 25 PC read/writer/continuation expectations and
      24 full-error/ULP effects at their named W/Z consumers; no geometry effect
      claimed at zero-carrier target entry.
    - [x] Complete 21 pressure methods, paper/spec/side-tool claim checks and
      unchanged carrier regressions; retain source-stage, domain, covariance,
      tampering and admitted-event/negative-next-step controls for A.2.
    - [x] Explicitly accept this separately declared A_PC oracle scope before
      A_PC `.2`; the [acceptance record](./phase-9-grcv4/tranche-8/P9-8.3A.1-APC-Acceptance.json)
      pins all four unchanged oracle/review/producer/test subjects.

    See the [A_PC oracle review](./phase-9-grcv4/tranche-8/P9-8.3A.1-APC-OracleReview.md)
    and [portable validation](./phase-9-grcv4/tranche-8/P9-8.3A.1-APC-Validation.json).
  - [x] P9-8.3A.2: For that same exact A profile, after accepted `.1`,
    exact A G2/G3 and applicable P9-8.1a–c
    and P9-8.2 implementation, implement/test against the pinned oracle:
    independent current/reset targets, reconstruction/readmission, receipts,
    whole-lifecycle rollback and replay. Do not replace expected values with
    production output. Accept separately from oracle construction.
    A_OS implementation and bounded own review are complete on 2026-10-03
    against the unchanged accepted A.1 checkpoint `0c995f9`; explicitly
    user-accepted on 2026-10-03 ("awesome. accept, commit"). Three
    implementation checkpoints are complete:
    - [x] Closed fixed-row A_OS descriptor/current/OS/writer bridge, with
      incoming-W stage operands and unchanged WLS behavior/identity.
    - [x] Actual two-role W lineage, complete target references, fresh source
      reference currents, full target OS/writer-surface readmission and atomic
      state/receipt/checkpoint replay publication.
    - [x] Native oracle comparison and both-role continuation; certified target
      split rejection, invalid policy/charge/receipt/replay controls, numerical
      outliers/covariance, regression and exact boundary binding review.
    See the [A.2 review](./phase-9-grcv4/tranche-8/P9-8.3A.2-AOS-RuntimeReview.md).
    A_CI runtime and bounded closure review are complete on 2026-10-03,
    following explicit acceptance of its separate A.1 oracle. Three checkpoints:

    - [x] Exact incoming-C/W fixed-row CI residual/domain bridge, explicit
      descriptor replay and a bound confirming-root numerical recipe. The latter
      closes the source-reset early-stop precision gap without changing the
      oracle, profile, tolerance, domain or iteration budget.
    - [x] Closed A_CI event/state/template, independent two-role W lineage and
      full root/writer-surface readmission, atomic receipts and checkpoint replay.
    - [x] Native source/twenty target beats, 18 effect controls, 23 pressure
      methods, certified domain and resource-boundary outliers, paper/spec and
      side-tool claim review, regressions, static checks and phase bindings.
    - [x] Separately accept the bounded A_CI runtime review; explicitly
      user-accepted on 2026-10-03 ("accept and commit"), distinct from the
      earlier oracle acceptance.

    See the [A_CI runtime review](./phase-9-grcv4/tranche-8/P9-8.3A.2-ACI-RuntimeReview.md)
    and [portable validation](./phase-9-grcv4/tranche-8/P9-8.3A.2-ACI-Validation.json).
  - Escalation: genuinely absent generic authority found in `.1` holds the
    affected child and returns to a bounded Tranche 7 contract correction;
    follow the established authority propagation process, not a specialization
    workaround. Do not reopen unrelated G2 or block independent C research;
    the P9-8.0 all-ten hold is now released by explicit aggregate acceptance;
    affected native leaves retain their own prerequisites.

P9-8.3 per-profile completion register (all include independent targets,
history channels, readmission, failure/rollback and replay; A rows require
their own `.1` oracle and `.2` execution acceptance):

- [x] C_OS — first mechanical checkpoint; complete C references, absent Z.
  Bounded implementation and pressure correction accepted at `eeb82e9`.
- [x] A_OS — first A oracle/implementation; explicit W history policy.
  A.1 oracle and pressure review explicitly user-accepted on 2026-10-03;
  A.2 runtime integration and pressure review separately user-accepted on
  2026-10-03 ("awesome. accept, commit"); bounded A_OS reconciliation is complete.
- [x] C_PC — nonnull whole-carrier policy and target continuation.
  Bounded implementation and pressure review user-accepted on 2026-10-03.
- [x] C_CI — joint target-root/domain evidence, no carrier.
  Native integration and bounded pressure review explicitly user-accepted on
  2026-10-03 ("found it. accept and commit").
  See P9-8.3C-CI above for the exact separate scope.
- [x] A_CI — A history plus joint target-root/domain evidence.
  A.1 explicitly user-accepted on 2026-10-03. A.2 implementation and bounded
  closure review are complete against the unchanged oracle; exact proof/replay,
  the source-reset precision correction, event/rollback and continuation pass.
  A.2 runtime and bounded closure review separately user-accepted on
  2026-10-03 ("accept and commit"); no public support promotion.
- [ ] A_PC — A history plus persistent carrier evidence.
  A.1 independent oracle and bounded own review complete on 2026-10-03;
  separately declared chart/history/resource scope explicitly user-accepted.
  A.2 fixed-row PC proof/replay and two-channel event/archive integration are
  authorized next; native rollback and public support are not claimed by the oracle.
- [ ] C_CI_PC — coupled root/carrier target evidence.
- [ ] A_CI_PC — combined W, coupled root and carrier evidence.
- [ ] C_RG2b — target completion/section reconstruction and domain evidence.
- [ ] A_RG2b — A history and target completion/section evidence.

These rows nominate no new production profile or ATC completion. Unselected
or held profiles remain pending and unadvertised. Only after the all-ten
feasibility prerequisite is reviewed may a partial runtime-accepted subset
proceed to its applicable P9-8.4–8.6 and Tranche 9 obligations without closing
the full ten-profile plan.

- [ ] P9-8.4: Execute all applicable accepted D30, D31, D45, and D52 runtime
  counterparts, with exact chirality/phase cases. Add separately labeled
  D37/D44 capacity-shell boundary probes and deeper declared probes. Execute
  permutation, chart rotation, reflection/chirality conjugacy, signed-edge
  reorientation, and phase-boundary cases; probes never replace frozen vectors.
- [ ] P9-8.5: Verify unique target occupancy, whole-lifecycle target
  reconstruction/readmission, and atomic failures.
- [ ] P9-8.6: Keep arbitrary-size conformance held until actual deep/runtime
  covariance evidence passes.
- [ ] End-of-Tranche-8 performance/cache review (after P9-8.6, before Tranche 9).
  User-requested on 2026-10-02. Profile the integrated paths and review graph
  envelope/identity repetition plus other reusable derived work. Require an
  explicit validity argument for each cache's owner, complete key, lifetime,
  invalidation and memory bound; prove cached/uncached results and rejections
  agree. Preserve asset checks, typed identity and numerical evidence domains.
  [Scope and proof obligations](./Phase-9-GRCV4-ImplementationPlan.md#end-of-tranche-8-performance-and-cache-review).
  This schedules review; implementation stays with the applicable existing
  work owners and introduces no new machine gate or conformance claim.

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
| 6. Separate A expansion work | P9-8.3A.1 produces/reviews the oracle; P9-8.3A.2 implements/tests against it. Generic authority gaps route back to Tranche 7; C_OS/C_PC remain independent. |
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
