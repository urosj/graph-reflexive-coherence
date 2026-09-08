# Phase 9 GRCV4 handoff — accepted through P9-2.6

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
without expanding the limited audit's scope. The permission adapter exposes
twelve dependency-ready leaves and 25 eligible paths. P9-4.1 implements the
Candidate C complete-profile/reference-map binding and separate typed
constructor identities; see the [P9-4.1 review](./phase-9-grcv4/tranche-4/P9-4.1-Review.md)
and [execution record](./phase-9-grcv4/tranche-4/P9-4.1-ExecutionRecord.json).
The user's commit instruction accepts P9-4.1 after its audit follow-up. The
review, execution record and run manifests retain their validation-time pending
dispositions; this handoff and the commit record the later acceptance separately.
The follow-up passed 51 focused methods and seven relocated capture checks,
and reconstructed both source revisions. The older broad-run observations retain
their live-code attribution limit. P9-4.2 entry still needs a separate transition
binding the accepted commit. Generic runtime and specialization support remain empty.

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

## Where we stopped

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
