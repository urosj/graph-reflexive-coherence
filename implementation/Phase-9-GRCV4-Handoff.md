# Phase 9 GRCV4 handoff — P9-5.2 implementation

Current restart point, 2026-09-09: branch `impl/phase-9-grcv4-tranche-5`,
based on accepted P9-5.1 commit `c920376`.
[P9-5.2](./phase-9-grcv4/tranche-5/P9-5.2-Review.md) implements fixed-geometry
A current/Read-Back, structural source and the provisional final-C log writer.
The independent audit's two findings are corrected: potential decomposition
diagnostics now remain exact rational values, and the writer pins its complete
Decimal context without modifying caller state. 65 focused methods and all
three supplied integrated audit regressions pass. **P9-5.2 was accepted by the
user on 2026-09-09**, with P9-5.3 authorized next.
The [audit follow-up](./phase-9-grcv4/tranche-5/P9-5.2-AuditFollowup.json)
records reconstruction and scoped checks; the original 61-method/33-browser
execution remains intact. Current permission is 32 leaves /
31 runtime paths. Use:

```sh
.venv/bin/python implementation/phase-9-grcv4/verification/verify_p952_current_writer.py --check
```

P9-5.3 is the authorized continuation after this acceptance commit. It must
integrate and verify
the complete A_OS pass, split residual, one corrector/continuity/writer, clocks
and zero-duration path. The current writer validates its supplied corrector
and resource result; the OS owner must prove the corrector geometry came from
the admitted predictor pass. Full lifecycle admission/commit and A_OS G2 remain
with their owners. No accepted C_OS scientific implementation changed.

Concrete post-writer pressure for P9-5.3/full lifecycle: `C=(0,0)`, `W_old=4`,
zero potential, `alpha=beta=gamma=0`, `chi=1`, `zeta=3`, `tau=1`, and binary64
`dt=log(2)` give an admitted zero current with denominator `-4/5`. The local
writer lawfully returns `W_next=2`; reconstructing the poststate current is
singular (denominator zero). The integrated owner must reject atomically at
post-writer readmission, preserving the whole prestate. That read-only check
must not change the already selected same-beat current or misreport its
earlier solve as failed. The portable regression is retained in the leaf's
test suite and audit reproducer; it currently characterizes the local boundary,
not a completed lifecycle rollback implementation.

Accepted predecessor: [P9-5.1](./phase-9-grcv4/tranche-5/P9-5.1-Review.md)
implements explicit history-free Candidate A current/reset construction and
positive retained mobility authority, with a portable
[audit follow-up manifest](./phase-9-grcv4/tranche-5/P9-5.1-AuditFollowup.json).
Independent audit passed its bounded scope; the rounding descriptions and
underflow/exponent/multigraph regressions are corrected. **P9-5.1 was accepted
by the user on 2026-09-09** after 41 focused tests, the 269-kernel local rerun,
and entry/status verification passed. Its retained-source checker belongs to
the historical `c920376` checkout; use the successor command above for current
status. No A state was added to the accepted C_OS facade or support set.

For continuation, the explicit reference flux remains a declared operand:
later integration must establish its admitted source, bind the actual target
stage, exclude discarded-history dependence, and perform current/lifecycle
readmission before claiming the complete initializer. P9-5.2 must also pressure
finite large `W_A`/`W_hat_A` contrasts without overflowing their denominator;
the P9-5.2 tests now cover this, including exact regular denominators whose
displayed binary64 contrast rounds to an endpoint.
The review distinguishes value-constructor failure from lifecycle rollback.

The [P9-4.8B integrated review](./phase-9-grcv4/tranche-4/P9-4.8B-Review.md)
remains the accepted Tranche 4 basis.
The user accepted the receipt-parent design and requested full implementation:
the admitted claim/debt overlay, actual tool UX, proposal/paper/spec successor
and internal C_OS parent rule are implemented. Consult that review and the
current checklist for validation/acceptance state. P9-4.9.2 was accepted in
`d8f26d9`. The bounded public C_OS facade implementation and focused evidence
were accepted in `7905e7e`. The user then explicitly accepted the audit-refined
**P9-4.9.1a abundance availability authority** on 2026-09-09 and authorized
implementation. It is admitted through the forensic API and propagated through
proposal/paper §14.2.1, the V4 specs and the C_OS projection. Consult the
[abundance review](./phase-9-grcv4/tranche-4/P9-4.9.1a-Review.md) for focused
verification and limits. P9-4.9.3 was accepted by the user's commit instruction
in `c01526c`. It supplies the exact 33-case product for one
nominated complete profile, plus exact dimension and mapped-event vectors.
Control/target identities are not broader support. **The user explicitly accepted
P9-4.8B on 2026-09-09; Tranche 4 is closed.** The
[explicit G2 acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json) links the original proposed review and execution.
All three phase closure obligations are discharged for exactly:

`grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d`

Global runtime discovery reconstructs this exact declaration. Instance-local
migration targets do not expand the accepted set. API/notebook/browser status
projects the same acceptance, with `P9-7.7-C_OS` as an alias, not extra credit.
G3, other profiles and specialization remain closed. The user chose the bounded
P9-5.1 continuation above; further A work and a G3 entry review require their
own continuation. The exact accepted C_OS population is unchanged.

The [P9-4.9.1a proposal](./investigations/grc9v4-constitutive-design/decisions/P9AbundanceInterfaceAuthorityProposal.md)
is accepted. All three refinements
(observed-state naming, detector totality/conformance failure, and release-bound
definition identity) are incorporated; the user's explicit acceptance followed
the conditional audit. The rule is a required common key,
explicit unavailable triplet for C_OS, and numeric capability only with a separately
admitted family definition/detector/stage. No numeric functional is admitted.
The new release preserves scientific/model/reset identity and the v3 snapshot
layout, but old-release snapshots remain explicitly rejected. The old parent
and facade runs are retained at their Git subjects, not relabeled as current.
The user's subsequent instruction to commit accepts the bounded P9-4.9.1a
implementation and its focused evidence. The review/execution records retain
their validation-time pending disposition; this handoff and the commit record
the later acceptance in `1f5f5e9`. Those earlier decisions did not grant G2; the separate
P9-4.8B acceptance above now grants the exact reviewed scope.

Lean checks: use `verification/verify_p948b_review.py --check` and
`verification/audit_phase9_implementation.py --boundary-only` under
`implementation/phase-9-grcv4/`, with `.venv/bin/python` from the repository
root. The accepted parent/facade/abundance runs are checked at their original Git
subjects; the retained 22-test fixture record binds unchanged scientific
source. Acceptance-only discovery, registry assertions and status projections
have separate exact bindings; the original source hashes and run are unchanged. The successor also checks PASS/HOLD and misleading-record controls,
plus existing status/authority API, notebook and HTTP/browser-validator paths.
Neither command reruns numerical tests or claims fresh full historical/browser
verification. Tranche 4 closed with 30 ready leaves / 29 eligible paths;
the separate P9-5.1 entry above adds one leaf and its two candidate module/test
paths. Review maintenance itself opens no runtime leaf.

**Verification provenance follow-up closed on 2026-09-09.** The
[compact completion record](./phase-9-grcv4/tranche-4/P9-4.8B-VerificationFollowup.json)
retains all three resumed stages: permission pressure **248/248**, surface checks
including **32/32** browser-validator tests and exact API/notebook agreement,
and the accepted G2 review checker. Resumption exposed an empty setup-commit
failure on a clean checkout; the corrected harness explicitly exercises both
clean and modified candidates before requiring the committed forbidden edit to
reach frozen-byte rejection. The record preserves the Git subject, exact small
correction, reconstruction check, outputs and digests. Historical/authority
stages are reused; no numerical or desktop/mobile browser campaign was rerun.
The [earlier interrupted runs](./phase-9-grcv4/tranche-4/P9-4.8B-Review.md#full-path-follow-up-and-harness-correction)
remain incomplete at their original subjects. Completion belongs to the recorded
source plus correction; subsequent publication metadata is checked separately
at the current boundary. Use the lean checks above for current status.

## Historical P9-4.8 snapshot

Historical P9-4.8 restart point: **read the
[P9-4.8 continuation handoff](./phase-9-grcv4/tranche-4/P9-4.8-Handoff.md)**.
It contains the then-current checkout/acceptance state, source links, remaining work,
environment commands, verification limits and files intended for the next commit.

The branch is `impl/phase-9-grcv4-tranche-4`; accepted runtime base is
`12411282422ba3cd9e91ce93051fe3470b9bf084`. P9-4.6/4.7 audit corrections are
accepted. P9-4.8 has a draft G2 HOLD; fixture reconciliation and user review
remain open. The user intends to commit the review files after this handoff.
Use that later handoff-bearing branch tip on the destination machine.

The latest correction is essential: the user followed the checklist. Facade
integration and receipt-parent authority were left deferred under narrower
accepted scopes. Missing fixture mapping is not proof of missing behavior;
existing second-beat reconstruction tests must be considered before asserting
a stale-cache gap. The linked handoff and revised draft review preserve this
distinction. No new scientific requirements or runtime defects are inferred
from missing paperwork.

Everything below is historical navigation accumulated from earlier handoffs.
Its old “held”, “next” and “not started” statements describe those earlier
snapshots; they must not override the current restart point above.

## Historical Tranche 2 snapshot and subsequent continuation notes

Snapshot: 2026-09-06, branch `impl/phase-9-grcv4-tranche-2`, accepted implementation
commit `5307343e34d33ab4a95a5712fbafe0ebd1df1a62`.
This is a navigation and continuation note, not a new acceptance gate, scientific
claim, execution record, or authorization to start another iteration.

Later working guidance, recorded 2026-09-07: read the
[prospective evidence workflow](./phase-9-grcv4/tranche-1/P9-1.9-EvidenceHandoff.md#prospective-evidence-workflow)
before collecting evidence for the next leaf. It records the user's direction
to preserve published evidence and simplify future capture and reconstruction.
The Tranche 2 status below remains the historical snapshot named above; use
the current plan/checklist and acceptance records for continuation status.

Current continuation (2026-09-08): branch `impl/phase-9-grcv4-tranche-4`
starts from the Tranche 3 merge `2e90398`. P9-3.5's accepted `155c728` subject
is now authenticated in its [acceptance record](./phase-9-grcv4/tranche-3/P9-3.5-AcceptanceRecord.json),
without expanding the limited audit's scope. That P9-4.1 entry exposed
twelve dependency-ready leaves and 25 eligible paths. P9-4.1 implements the
Candidate C complete-profile/reference-map binding and separate typed
constructor identities; see the [P9-4.1 review](./phase-9-grcv4/tranche-4/P9-4.1-Review.md)
and [execution record](./phase-9-grcv4/tranche-4/P9-4.1-ExecutionRecord.json).
The user's commit instruction accepts P9-4.1 after its audit follow-up. The
review, execution record and run manifests retain their validation-time pending
dispositions; this handoff and the commit record the later acceptance separately.
The follow-up passed 51 focused methods and seven relocated capture checks,
and reconstructed both source revisions. The older broad-run observations retain
their live-code attribution limit. P9-4.2 entry now binds accepted commit `94a079d`
in [its acceptance record](./phase-9-grcv4/tranche-4/P9-4.1-AcceptanceRecord.json):
thirteen dependency-ready leaves and 25 eligible paths. P9-4.2 implements the
fresh stage selector, retained-Hodge potential/baseline, typed Read-Back and regular
physical current solve. All 123 focused methods passed, with exact source
reconstruction and 17 relocated methods passing under each of two hash seeds.
The [P9-4.2 review](./phase-9-grcv4/tranche-4/P9-4.2-Review.md) maps equations and
outlier pressure to the tests; its [execution record](./phase-9-grcv4/tranche-4/P9-4.2-ExecutionRecord.json)
records numerical policy, source queries, reconstruction and validation limits.
P9-4.2 is implemented, verified and explicitly accepted by the user for commit.
The user reports that both reviews found no defects. The review, execution record
and run manifest retain their validation-time dispositions; this handoff and the
commit record the later acceptance. P9-4.3 entry now binds accepted `ac3a7cf` in
[the P9-4.2 acceptance record](./phase-9-grcv4/tranche-4/P9-4.2-AcceptanceRecord.json),
opening fourteen leaves with the same 25 eligible paths. P9-4.3 is implemented,
verified and explicitly accepted by the user for commit: see its
[review](./phase-9-grcv4/tranche-4/P9-4.3-Review.md) and
[execution record](./phase-9-grcv4/tranche-4/P9-4.3-ExecutionRecord.json).
All 143 focused methods passed, including 20 new derivative/control methods;
27 derivative/capture methods also passed after exact source reconstruction in a
checkout with spaces and a changed hash seed. Coverage includes the moving
selector, all retained-Hodge product terms, covariance, separate zero controls,
repeated/near-gap spectra, resource-domain boundaries and saturation. The checks
identified no production defect; runtime source is unchanged. Evidence is one
review index, one execution record and one run manifest. Those records retain
their validation-time dispositions; this handoff and the commit record the later
user acceptance. A separately authorized P9-4.4 entry can bind the accepted commit.
P9-4.4 remains held; generic runtime and specialization support remain empty.

Post-acceptance P9-4.3 audit follow-up: the audit identified a test-only extreme
saturation defect in accepted `39cfe6a`. The correction and numerical limits are
recorded in the [follow-up index](./phase-9-grcv4/tranche-4/P9-4.3-AuditFollowup.md).
The new capture passed 148 focused methods in a reconstructed checkout with a
fresh interpreter and changed hash seed. The user has accepted the verified
follow-up. Original evidence and acceptance history remain intact; the follow-up
index and run retain their validation-time dispositions. This handoff and the
commit record the later user acceptance. P9-4.4 remains held.

P9-4.4 continuation: the user authorized the next leaf. The
[P9-4.3 acceptance record](./phase-9-grcv4/tranche-4/P9-4.3-AcceptanceRecord.json)
binds accepted follow-up `4a3a7ee`, opening fifteen leaves and 27 eligible paths.
P9-4.4 is implemented, verified and explicitly accepted by the user for commit,
including its closed audit gap: see its
[review](./phase-9-grcv4/tranche-4/P9-4.4-Review.md) and
[execution record](./phase-9-grcv4/tranche-4/P9-4.4-ExecutionRecord.json).
The initial 187-method run is preserved. The audit follow-up passes 188 focused
methods, including 22 OS methods, in a reconstructed checkout. It adds actual
pass/step crossing rejection and safe-path controls; endpoint-only and blanket
rejection mutations are detected. Runtime source is unchanged by the follow-up.
The bounded provisional pipeline performs one reference predictor,
one geometry update, one fresh corrector, an explicit reference-relative split
check, one resource write and final-C reconstruction. Live lifecycle commit and
receipt authentication remain with their later owners; runtime support stays
empty. The review, execution and run records retain their validation-time
dispositions; this handoff and the commit record the later user acceptance.
A separately authorized P9-4.5 entry can bind the accepted commit. P9-4.5 remains
held. Its complete-operation work must resolve next-reference
current/domain admission before claiming a commit-ready positive vector. Current
`next_inputs` constructs reference geometry without evaluating that current; its
operation ID, duration and receipt IDs are numerical continuation metadata, not
an authenticated next request/ledger. Preserve final-C current quarantine from
a second geometry, residual or continuity pass.

P9-4.5 continuation: the user authorized the next leaf. The accepted P9-4.4
`1752426` subject is bound in [its acceptance record](./phase-9-grcv4/tranche-4/P9-4.4-AcceptanceRecord.json).
The bounded ordinary-operation owner is implemented, verified and explicitly
accepted by the user for commit, including all six audit corrections.
All 256 scoped methods pass after exact source reconstruction. Its
[review](./phase-9-grcv4/tranche-4/P9-4.5-Review.md) explains the
minimal lifecycle ownership refinement, actual committed vectors, typed failures,
full-tuple atomicity and explicit local receipt conventions. The
[execution record](./phase-9-grcv4/tranche-4/P9-4.5-ExecutionRecord.json) carries
source queries and reproduction metadata. Final C is admitted at both consumed
and next-reference geometry before publication, without another OS pass. Actual
next requests and receipt ledgers replace provisional continuation metadata.
The verified scope also passed 199 permission checks, API/notebook checks,
26 JavaScript tests and 18 desktop/mobile browser tests. Review, execution and
run records retain their validation-time dispositions; this handoff and the
commit record the later user acceptance. Receipt parenting remains a provisional
local convention that the later lineage owner may revise. A separately authorized
P9-4.6 entry can bind the accepted commit; P9-4.6 and profile conformance remain held.

P9-4.6 continuation: the user authorized this leaf after accepting P9-4.5.
The [P9-4.5 acceptance record](./phase-9-grcv4/tranche-4/P9-4.5-AcceptanceRecord.json)
binds `ec9f8662d08eafc5346837ddbbb74c9a4359a9b4`. Seventeen leaves and 29 paths
are dependency-ready. P9-4.6 implements actual C_OS snapshot/load/reset/rebase,
compatible current assignment and independent duplication. All 76 focused
methods passed in the reconstructed checkout with no failures/errors/skips.
The user authorized the original commit with the full independent audit
pending; the later combined audit and its findings are recorded below. See the
[review](./phase-9-grcv4/tranche-4/P9-4.6-Review.md) and
[execution record](./phase-9-grcv4/tranche-4/P9-4.6-ExecutionRecord.json).
The `P9-7.1-C_OS` child aliases this evidence without duplicate credit. Snapshots
embed resolved reference/profile content, scientific/reset payloads, ordered
receipts and historical commit preimages. Target current and reset are freshly
readmitted; state and commit preimages publish together. Reset preserves live
clock and lineage; assignment changes only C. The review states the explicit
implementation snapshot layout and local receipt-parent conventions. Full
receipt ownership/replay, events/migrations and profile conformance remain with
their later leaves. The bound review and execution record retain their
verification-time pending-review status; this handoff records the later commit
authorization. The later supplied audits, correction and closure are recorded
separately below; the original pending-audit records remain unchanged.

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



Validation scope for continuation: select the leaf's scientific/edge-case tests,
relevant shared V4 regression tests, and checks for changed verification surfaces.
The full repository run for P9-4.1 is not a requirement to repeat it after every
leaf. Use full regression at integration/tranche milestones or when changes to
shared infrastructure, dependencies, public exports, or observed failures justify
wider coverage. Record what ran and its limits; test counts are not a substitute
for coverage of the scientific obligations.

Subsequent portability maintenance presents older machine-specific paths relative
to the project. Read the [path presentation and exact-replay guide](./phase-9-grcv4/tranche-1/P9-1.9-EvidenceHandoff.md#repository-path-presentations)
before comparing historical hashes or extracting embedded source. Original
bytes remain in Git; current presentations do not represent new scientific runs.
Direct historical-SHA checks against normalized files still need reconciliation;
the linked guide names the confirmed cases. The user authorized committing this
maintenance and merging `impl/phase-9-grcv4-tranche-3` into `main` with that
limitation known. That merge is the base of the Tranche 4 branch named above.
The old direct historical-SHA consumers remain a separate maintenance limitation;
P9-4.1 reconstruction uses its own source bindings and does not depend on them.

## Historical Tranche 2 stopping point

P9-G1 and P9-2.1 through P9-2.6 are accepted. The user's instruction to commit
is acceptance; the P9-2.6 commit message explicitly records that decision.
P9-3.1 has **not** started. The user subsequently authorized committing this
note and closing Tranche 2 into `main` with `--no-ff`. After that merge, resume
from `main`; the named Tranche 2 branch is the source branch, not the required
continuation branch. The merge's second parent identifies the handoff-bearing
Tranche 2 tip. No new implementation branch or P9-3.1 work is authorized here.

Some plan/review/execution text still says acceptance is pending. Those are
pre-acceptance descriptions, not a request to obtain the same acceptance again.
In particular, preserve the bound P9-2.6 review and execution evidence instead
of editing them to make the earlier run appear accepted at execution time.

The live permission adapter currently authenticates acceptance through P9-2.5
and exposes six ready leaves through P9-2.6 and nineteen eligible paths. It
still holds P9-3.1: **P9-2.6's committed acceptance has not yet been wired into
the next entry transition.** When the user authorizes continuation, add the
committed-subject P9-2.6 acceptance link and scoped successor routing, following
the existing predecessor pattern. Update affected API/notebook/browser checks
and current bindings together. Do not bypass the check, reopen P9-G1, promote
all later leaves, or rewrite historical run identities.

Accepted generic runtime support and admitted specialization support are both
empty. Valid profiles, canonical records, installed modules, successful-content
reconstruction, and a tested negative-duration prefix are not an executable
numerical profile or GRC9V4 conformance. No concrete V4 model facade is exported.

## Sources and code to read

Read the [implementation plan](./Phase-9-GRCV4-ImplementationPlan.md) and
[checklist](./Phase-9-GRCV4-ImplementationChecklist.md), then the
[P9-2.6 review](./phase-9-grcv4/tranche-2/P9-2.6-Review.md). Their detailed source
and remaining-obligation links are more authoritative than this summary.

- Primary implementation contracts: [generic V4](../specs/grc-v4-spec.md),
  [V4 common-interface extension](../specs/grc-common-interface-v4-ext.md), and
  [GRC9V4 specialization](../specs/grc-9-v4-spec.md). The accepted
  [release](../specs/grc-v4-specification-release.json),
  [schema](../specs/grc-v4-contract-schema.json), and
  [vectors](../specs/grc-v4-conformance-vectors.json) remain frozen.
- Mathematical meaning: [paper](./investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md).
  Use the [proposal](./investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md)
  for claim links/provenance. Implement from the specs **with** the paper and
  accepted D10/D10.2/D11 claims, not from a claim list or legacy code alone.
- Scientific investigation: follow the
  [Agentic Query Guide](./investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/AgenticQueryGuide.md).
  Use typed forensic queries as the main route; preserve claim class, support
  disposition, source/edge references and trace identities. Raw JSON is a
  fallback for literal registry/provenance strings outside the accepted graph;
  a referenced identifier is not automatically a resolved claim.
- Scope and inherited obligations: [source crosswalk](./phase-9-grcv4/tranche-1/P9-1.1-SourceCrosswalk.json),
  [debt inventory](./phase-9-grcv4/tranche-1/P9-1.2-DebtInventory.json),
  [support/dependencies](./phase-9-grcv4/tranche-1/P9-1.4-SupportAndDependencies.json),
  and [ownership review](./phase-9-grcv4/tranche-1/P9-1.5-OwnershipReview.md),
  especially §7.2.

Current foundation code is under `src/pygrc/models/`: `grc_v4.py`,
`grc_v4_state.py`, `grc_v4_profile.py`, `grc_v4_codec.py`, `grc_v4_step.py`, and
`grc_v4_assets/`. Corresponding `tests/models/test_grc_v4*.py` tests cover value,
identity, request, result, packaging and ownership boundaries.
`tests/models/grcv4_conformance_harness.py` and `grcv4_reference_oracles.py`
provide the bounded prefix harness and independent oracles. An imported
callback/control remains a control even when its bytes match real execution.

## Next bounded implementation step, when requested

P9-3.1 implements deterministic graph/differential identities, typed
Hodge/one-form/physical-flux maps, and candidate-local mobility ownership.
Carry forward the P9-2.6 storage decision: V4-local immutable stable-ID lookup
for pure graph maps, not a shallow wrapper around mutable legacy backends,
integer allocation tables, or mutation journals. Map the exact applicable
spec, paper and accepted contracts before implementing it.
In particular, do not identify Hodge pairing, physical-flux conversion and
candidate mobility merely because their matrices have compatible shapes.

Keep the later obligations with their owners: stage/cache admission P9-3.2;
one-resource-write/charge boundary P9-3.3; conditioning, signed covariance and
invariant-projector pressure P9-3.4; rejection-state preservation P9-3.5.
Actual facade/full-step admission, zero/subnormal/extreme-duration checks and
rollback belong to the Tranche 4 consumers. Parent-reference scope/order remains
P9-7.6; specialization and exact legacy delegation remain Tranches 8–9.
The first intended numerical slice is C_OS, not all ten profiles at once.

## Moving to another machine

Publish the handoff-bearing `main`, including the Tranche 2 merge, through the
usual Git remote before switching machines. Unpushed local commits are not
available to another clone. This note does not assert that a push has occurred.
Keep full Git history: acceptance checks inspect historical committed subjects.

After obtaining the updated `main`, run from the repository root:

```bash
git switch main
git status --short
git merge-base --is-ancestor 5307343e34d33ab4a95a5712fbafe0ebd1df1a62 HEAD
git show --no-patch --format=full 5307343
git log --first-parent --merges -1 --format='%H %P %s'
```

Use the checkout's `.venv`; do not copy another machine's virtual environment
or point tools at a foreign checkout. The following are Linux/macOS shell
commands, not a claim that the whole test suite has been validated on every OS:

```bash
GRCV4_TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
python3 "$GRCV4_TOOL/scripts/bootstrap.py" --python-only
.venv/bin/python -m pip install -e '.[v4,dev]' build setuptools wheel
```

Host Python is used only for bootstrap, which creates/re-enters `.venv`.
Python 3.11+ is declared; the accepted P9-2.6 run used CPython 3.12.3 on Linux
x86_64. Bootstrap's side-tool Python lock currently has no package requirements:
bootstrap alone does **not** install the V4 extra or repository package.
The install command above provisions a working environment, not an exact replay
of all recorded package versions. Consult the retained environments below for
exact comparisons; record any changed resolution/platform as a new run.

For Node/browser checks, run the full bootstrap once:

```bash
.venv/bin/python "$GRCV4_TOOL/scripts/bootstrap.py"
```

It provisions managed Node, locked frontend dependencies and Chromium under
the ignored tool-local directories. Network access and browser OS libraries
may be needed. Use its managed tools, not global Node/npm. The
[tool README](./investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/README.md)
and [verification guide](./investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/Phase9VerificationGuide.md)
describe the CLI, API, notebook and browser surfaces.

## Evidence and proportionate verification

The accepted P9-2.6 results are **1,055 tests, no failures/errors/skips**:
105 core, 918 model and 32 harness/oracle tests, including four fresh package
environments and sixteen consumer processes. Separate checks passed 90 authority
cases, API/notebook identity, 16 Node tests and 18 desktop/mobile browser tests,
plus Ruff, strict mypy and the current-boundary check. These are foundation
results, not numerical support. The full historical-predecessor replay was not
repeated as part of P9-2.6's boundary-only check.

Inspect without rerunning:

- [Execution record](./phase-9-grcv4/tranche-2/P9-2.6-ExecutionRecord.json) and
  [final self-check run](./phase-9-grcv4/evidence/P9-2.6/self-check/run.json)
  bind the review, exact source identities and results.
- [Self-check inputs](./phase-9-grcv4/evidence/P9-2.6/self-check/inputs.json)
  retain the guide and `final_combined_command`.
  [Actual results](./phase-9-grcv4/evidence/P9-2.6/self-check/actual.json) retain
  the executed test roster, loaded origins, package/archive hashes, dependencies
  and outcomes. Its `retention_note` explains structured-output deduplication
  and reconstructed deterministic inputs; this is not a raw terminal transcript.
- [Original integration inputs](./phase-9-grcv4/evidence/P9-2.6/integration/inputs.json)
  identify the offline wheelhouse by filenames/hashes. That earlier run remains
  separately qualified; do not substitute its counts for the final suite.
- [Fresh prefix replay](./phase-9-grcv4/evidence/P9-2.5/p926-self-check-replay/run.json)
  has a new run identity but the same four deterministic content files as the
  accepted P9-2.5 prefix. Neither replaces the other.
- [G1 evidence handoff](./phase-9-grcv4/tranche-1/P9-1.9-EvidenceHandoff.md)
  explains the existing tracked historical bundle. No new ZIP is required here.

Tracked records travel with Git. `.venv`, installed wheels, built distribution
archives, Node/browser installations and ignored generated surface outputs do
not. The offline wheelhouse must be replenished before the package test;
its recorded CPython/Linux wheels are not universal cross-platform artifacts.
Matching original inputs requires checking the recorded hashes. Compatible
replacement wheels on another platform yield a new validation, not the original
execution or a promise of byte-identical wheel/sdist builds.

Start with the inexpensive current boundary:

```bash
.venv/bin/python "$GRCV4_TOOL/scripts/run.py" verify-phase9 --boundary-only
```

If inspecting pressure projections or checking affected surfaces, generate the
current pressure report **before** its consumers; do not run these two commands
concurrently or change their bound inputs between them:

```bash
.venv/bin/python implementation/phase-9-grcv4/verification/test_phase9_g1.py
.venv/bin/python "$GRCV4_TOOL/scripts/test_phase9_g1_surfaces.py"
.venv/bin/python "$GRCV4_TOOL/scripts/test_phase9_g1_surfaces.py" --browser
```

Missing/stale generated reports on a fresh clone are not revoked acceptance.
Regenerate them when needed. `verify-phase9` without `--boundary-only` is the
larger historical/current verification workflow; it is not required merely to
read the evidence. Choose checks for the next actual change and finish editing
their inputs before a final run; avoid repeating broad suites without a reason.

Ordinary model discovery skips the opt-in package test unless
`GRCV4_PACKAGE_TESTS=1` and `GRCV4_WHEELHOUSE` identifies a populated repository-local
wheelhouse. Do not report that skipped run as the recorded 1,055-test result.
Use the retained `final_combined_command` for the assembled suite once its
dependency inputs are ready. Retain any rerun under a fresh output name;
never overwrite published execution evidence.

## Working agreements for the next conversation

- The goal is coherence across claims, paper, specs and code, with exact
  validation and explicitly scoped reproducibility. Tooling serves that goal;
  it is not a reason to invent more gates, archives or administrative work.
- Fix only V4. Preserve older model/spec behavior and frozen accepted authority.
  A scientific contradiction needs investigation resolution, then paper/proposal
  and spec propagation; do not repair it editorially in runtime code.
- Turn substantive audit gaps into regression tests. A short explanation of
  routine development failures suffices; do not archive every failed attempt.
- Retain only useful review/evidence material, using repository-relative paths.
  Imported review files need no machine-local provenance or separate original
  hash merely because they were copied into the repository.
- A commit request is user acceptance. Preserve historical evidence and record
  successor acceptance separately when wiring the next authorized entry.
  Do not commit, push, merge, or start later work just because this note lists it.

Suggested first message in the new conversation:

> Read `implementation/Phase-9-GRCV4-Handoff.md` and inspect the current checkout.
> P9-2.6 is accepted at `5307343`; do not repeat that acceptance or infer runtime
> support. Check local setup and identify the next bounded P9-3.1 entry action.
> Do not implement or change branches until I authorize continuation.
