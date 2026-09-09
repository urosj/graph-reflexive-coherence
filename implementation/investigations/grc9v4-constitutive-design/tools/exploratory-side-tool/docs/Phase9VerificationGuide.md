# Phase 9 verification access

This panel separates implementation verification from forensic authority.
P9-4.9.2 adds a separately admitted parent-contract overlay and propagates its
accepted rule through proposal, paper and a V4 successor release; historical
D10/D11 graph and acceptance records retain their authority and bytes. P9-G1 is accepted;
bounded implementation is authorized, but accepted runtime support sets remain
empty. GRC9V4 still requires its separate P9-G3 admission.

## CLI and browser

From the repository root, use the existing `.venv`:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py verify-phase9
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py verify-iteration9
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py serve-phase9
```

`verify-phase9` checks current accepted implementation authority, then replays
the unchanged accepted V2 verifier on commit `6e0a507`, including its four
historical audits, source/architecture, pressure and API/notebook/Node checks.
It then executes current G1/parent pressure and API/notebook/Node checks,
inspects retained parent evidence at accepted Git `d8f26d9` and focused facade
evidence against current runtime inputs, and writes
an ignored execution receipt. The normal `verify-iteration9` additionally runs
the unchanged D11 suites and old browser regression on their exact historical
Git subject, then the current Phase 9 browser regressions. Historical source
clones are disposable, under the repository's ignored generated directory.
Neither command creates approval; both validate the separately recorded user
acceptance. `--boundary-only` on `verify-phase9` or
`verify-post-d10-specifications` checks current authority/release only and is
never labeled a full verification pass.

`serve-phase9` opens a read-only local server at `http://127.0.0.1:4174`.
Visit that address to refresh current checks, inspect exact source hashes and
the accepted P9-1.4–P9-1.9 results, and download the same status JSON returned by
the API. Stop the server with Ctrl-C. No network dependency installation is
needed. The existing D11 explorer remains separately available through
`run.py serve-iteration11-d11`; its accepted records and candidate labels do
not change.

Refresh performs actual current-tree/policy checks. It does not rerun the
historical or browser suites. A matching **recorded** successor pass is a
previous `verify-phase9` execution for the current inputs, not a fresh pass
or a signed attestation. Missing, stale or mismatched receipts are not
current; invalid current authority is held. The panel clears old success on
refresh failure and rejects contradictory authority or digest drift. Hashes
detect inconsistency; they cannot substitute for user review or authenticate
an adversary who controls the verifier and all local evidence.

## API and notebook

```python
from pathlib import Path
import sys

root = Path.cwd()  # repository root
tool = root / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
sys.path.insert(0, str(tool / "src"))
from grcv4_explorer.phase9_verification import verification_status

status = verification_status(root)
assert status["P9_G1_accepted"] is True  # separately accepted implementation scope
assert status["runtime_authorized"] is True
assert status["accepted_generic_runtime_support"] == []  # not conformance
```

The separate `phase9_verification` module does not alter historical exports.
Its `output_class` is `implementation_verification_status_not_forensic_trace`.
For scientific questions, continue using `contract_provenance`,
`object_dependents`, and the other typed forensic functions, preserving their
claim class, source references and support disposition.

Open [the notebook](../tool/notebooks/phase9_verification.ipynb) with the
repository `.venv` kernel, or execute its actual code cells headlessly:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py notebook-phase9
```

The notebook discovers the checkout from its directory, calls the same API,
and leaves saved code-cell outputs empty. The runner checks exact API payload
identity and retains generated output under `tool/generated/phase9-verification/`.

## Scenarios and evidence

### P9-4.9.2 parent authority scenarios

- Load the parent claim, debt resolution, object and all three contracts using
  **Load parent authority** in the existing Phase 9 browser. Its
  `/api/receipt-parents` endpoint returns the same `parent_authority` typed
  traces as the executable notebook cell; use the selector to inspect full
  source/edge witnesses. It neither runs the model nor grants G2.
- Change or coherently rehash a source/admission candidate: the pinned current
  loader must hold. The historical D11 context remains historical, not a fallback
  that pretends the P9 contract is present.
- Fail a refresh after a successful load: old output clears in browser and
  notebook. The desktop/mobile browser regression exercises this behavior.
- Query the old ordered-profile contract in both contexts: its source payload
  and support disposition are unchanged; only the new successor trace identity
  adds the P9 source bundle. Parent selection is not retroactively attributed
  to D10.2.
- Run `tool/scripts/test_p9492_parents.py` with the repository `.venv` for the
  source/graph/notebook checks. The normal Phase 9 verification includes these
  checks and inspection of retained P9-4.9.2 runtime evidence at its original
  accepted Git subject. A new runtime capture is a separate rerun, not
  a replacement for the retained execution.

Current policies: `grcv4-previous-successful-primary-v1` and the separately
accepted `grcv4-family-abundance-diagnostic-v1`. P9-4.9.1a adds its bounded
availability permission on existing paths: 29 ready leaves, unchanged 29
eligible runtime paths, empty accepted support sets. No numeric detector is
admitted. The next work is final P9-4.9.3 reconciliation, then P9-4.8B.

For lean current checks:

```bash
.venv/bin/python implementation/phase-9-grcv4/verification/verify_p9491a_abundance.py --check
.venv/bin/python implementation/phase-9-grcv4/verification/audit_phase9_implementation.py --boundary-only
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run_phase9_notebook.py --status-only
```

The focused successor checks affected C_OS projections, synthetic numeric
protocol controls and real API/notebook/HTTP-handler/browser-validator identity.
The original parent/facade runs remain at `d8f26d9`/`7905e7e`; they are not new
execution of today's tree. Use a fresh generated destination for a deliberate
rerun; do not replace original evidence.

Use **Load abundance authority** in the browser or the notebook's
`abundance-authority` cell to inspect the accepted claim, debt, object or three
contracts. All views use the same typed forensic traces and clear stale output
on failure. Availability authority never implies numeric abundance or G2.
The registered scenarios are exact source/graph identity, rehashed/missing/new
source rejection, metadata/release/state distinction and typed failure versus
unavailability. The scoped handler/validator checks are not a desktop/mobile
browser campaign.

`PHASE9_STATUS_ONLY = True` or CLI `--status-only` queries current status without
pressure. It clears the isolated-pressure value to `None` and writes separate
`notebook-current-status.json`; it cannot refresh a stale full-pressure run.
Default/full mode still rejects stale evidence. Normal verification dispatches
to the abundance successor without applying older current-tree assertions to it.

The [scenario register](../../../../../phase-9-grcv4/tranche-1/P9-1.7-1.8-Scenarios.json)
links all six independent-review pressures and the live access scenarios to
executable checks. The [review](../../../../../phase-9-grcv4/tranche-1/P9-1.7-1.8-VerificationReview.md)
and [separate leaf results](../../../../../phase-9-grcv4/tranche-1/P9-1.7-1.8-ExecutionRecord.json)
record the precise claim ceiling and outstanding gates.

The predecessor P9-1.6 policy, auditor, evidence and full prepared artifact
snapshot are retained. The accepted V2 checker is replayed on its historical
commit; the G1 implementation successor is the current active route. Deleting
the acceptance or phase marker cannot restore the old verifier.
No old scientific scenario or accepted tool artifact is relabeled as a Phase 9
implementation result.

### Pressure-result subjects and audit evidence

The panel's separate **Isolated pressure evidence** section loads an exact
probe ID and downloads the same `pressure_projection(root, case_id)` API
payload. For `normal_entry_forbidden_source`, the actual normal CLI rejected
the temporary candidate; its negative-test assertion passed. Both facts stay
visible, alongside the explicit statement that no live permission was created.
`accepted_G1_exact_targets` shows an isolated generic addition admitted under
the actual accepted scope, without creating any new live permission or support.
The older `future_explicit_approval_exact_targets` case remains in the exact
historical V2 replay, where runtime authority was false.
Unknown full IDs reject; similar displayed prefixes never select another case.

The notebook's second cell clears old variables and binds the selected checkout
on each execution. The runner exports both current status and the separate
negative-probe result. Failed or out-of-order reruns cannot retain prior success.
The browser tests delay an older subject response until a newer one is visible,
and verify that the old response cannot overwrite it.

The [surface inventory](../../../../../phase-9-grcv4/tranche-1/P9-1.8-SurfaceInventory.json)
and [audit closure register](../../../../../phase-9-grcv4/tranche-1/P9-1.6-1.8-AuditClosure.json)
record applicability and named guide coverage. Per-run manifests, exact mutation
preimages, decisive traces and actual command output are retained in
`tool/generated/phase9-verification/runs/<run-id>/pressure-results.json`;
the latest run and three batch results also have convenient top-level files.
For the historical V2 subject, the tracked pressure file is a reproducible coverage index, not a substitute
for those current-input-bound raw results. API/notebook normalized projections
are retained in `surface-evidence.json`; browser output includes screenshots
and the tested JSON downloads.

The source-meaning panel keeps `accepted_frozen` specification authority and
`indeterminate_requires_review` forensic associations separate. Its 152/183
denominator is a source population, not executed V4 tests; fifteen obligations
remain pending under the already reviewed routing. This surface adds no claims.

The historical V2 future-runtime positive tests use disposable synthetic approval fixtures
with an externally supplied test trust anchor, release/predecessor bindings,
and exact before/after hashes. They test new V4 files and the two proposed
additive integration paths; they do not enact approval. P9-1.9 now supplies the
separately accepted real implementation policy and dispatch. Optional completion tests are
likewise scoped synthetic evidence, not executed GRC9V4 conformance.

## Accepted P9-G1 successor

The [G1 review](../../../../../phase-9-grcv4/tranche-1/P9-1.9-G1Review.md)
records the accepted scope and executable scenarios. Current V3 evidence is
`verification-v3.json`, `g1-pressure-results.json` and `g1-surface-evidence.json`;
raw G1 runs are archived under `runs/<run-id>/`. The exact V2 replay's receipt,
raw pressure, historical evidence and surface results are retained separately
under `accepted-predecessor/`. Do not compare their input identities as if they
were the same current tree.

These generated locations are local working outputs, not the handoff archive.
The [P9-G1 handoff addendum](../../../../../phase-9-grcv4/tranche-1/P9-1.9-EvidenceHandoff.md)
links the repository ZIP and compact manifest preserving normalized copies of selected V2
and V3 supporting runs, with the later predecessor replay labeled separately.
`verification/handoff_evidence.py` under the Phase 9 directory checks retrieval,
published member hashes and historical input identities without reexecuting those runs;
the full verifier reports archive integrity separately from current-work verification.
Retrieving this bundle requires no
ignored generated files. Original hashes remain citable separately from normalized
hashes; original raw ZIP retrieval is not claimed for a clone. A fresh rerun
cannot substitute for the recorded execution.

The API, notebook, browser, and downloaded status distinguish:

| Condition | Recorded `P9_G1_accepted` | Current `runtime_authorized` | `handoff_evidence.status` |
| --- | --- | --- | --- |
| Accepted scope and valid archive | `true` | `true` | `verified` |
| Accepted scope, archive missing or corrupt | `true` | `true` | `unavailable` or `invalid` |
| Current source or scope violation | `true` if the original decision authenticates | `false` | Independently checked |
| Acceptance record invalid or unavailable | `false` | `false` | Independently checked |

The ZIP and manifest are not authority inputs. Their standalone integrity check
still fails on missing/corrupt/replaced evidence; the normal implementation check
reports that result without silently withdrawing the user's decision. A missing
or malformed generated execution receipt remains `not_current`, not a new gate.

For current work, concise summaries of relevant development failures suffice;
raw failure outputs are retained only when material to a result or its limits.
There is no requirement to publish or review every local pressure archive.
Deliberately published supporting evidence remains immutable. Historical
blanket failure-retention wording is superseded by the addendum, not rewritten.

The runtime manifest binds exact current work paths, hashes and registered
owning-leaf IDs. The user's commit instructions accept the corrected P9-2.1
and P9-2.2 foundation; a separate committed-subject acceptance record preserves
the historical review/command evidence. The separately accepted P9-2.3 and
P9-2.4 commits enabled P9-2.5; its separately accepted commit now enables
P9-2.6. The accepted P9-2.6 commit enables P9-3.1; explicit P9-3.1
acceptance at `dccb1ca` enabled P9-3.2. P9-3.2 acceptance at `77286b2` now
enables P9-3.3, giving nine dependency-ready leaves and twenty-three eligible runtime paths; later generic and specialization leaves retain their
own gates. API/export includes `dependency_ready_leaves` and
`permitted_runtime_paths`, separately from the full conditional target roster.
`foundation_acceptance` identifies the exact acceptance record and accepted
foundation leaves. `request_acceptance` binds the user's P9-2.3 commit decision;
`result_acceptance` binds the user's P9-2.4 commit decision;
`harness_acceptance` binds the user's P9-2.5 commit decision;
`integration_acceptance` binds the P9-2.6 committed subject;
`geometry_acceptance` binds the separately accepted P9-3.1 committed subject;
`stage_acceptance` binds the separately accepted P9-3.2 committed subject.
Current P9-3.3 work cannot accept itself or unlock P9-3.4. The transport/step
modules and tests retain the checklist-assigned resource-boundary ownership; this entry adds no
runtime path. NumPy is an
explicit V4 extra under P9-3.1's scoped dependency ownership. The ownership adapter retains the
checklist-assigned result leaf on the existing state/step pairs; P9-2.5 uses
the two already-reviewed harness/oracle test paths.
G1 approval permits reviewed work under those conditions; the manifest is integrity
data, not an acceptance mechanism. No unexecuted profile may be advertised.
New scope, G2 conformance or G3 admission needs a separately reviewed successor.


P9-3.2 browser reconstruction includes installed DejaVu Sans, Serif and Sans Mono
families (the `fonts-dejavu-core` package on Debian/Ubuntu). The browser test
sets its generic font preferences explicitly through `Page.setFontFamilies`
and requires nonzero rendered title glyph width and line height. This catches
an observed host/headless-browser condition where DOM assertions passed but
generic-family text was invisible. It does not alter served CSS or page content.
The P9-3.2 font-environment record preserves the original blank screenshot,
protocol observations and font hashes. Browser pixels are scoped to that font
and browser environment, independently of numerical runtime conformance.

Use viewport screenshots in this pinned Chromium environment: full-page capture
was observed to discard generic-font overrides while rasterizing. The tests
check glyph dimensions before and after capture. Probe tests wait for their
exact network subject before checking the rendered decision; they do not rely
on a ten-second DOM wait to absorb full authority-report verification latency.
