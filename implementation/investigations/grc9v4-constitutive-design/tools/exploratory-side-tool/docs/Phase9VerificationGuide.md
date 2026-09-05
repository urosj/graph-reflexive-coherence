# Phase 9 verification access

This is implementation-governance tooling, not a new scientific graph or a
forensic claim API. The frozen specifications, paper, accepted D10/D11 claims,
and existing explorer retain their authority and bytes. P9-G1 is pending;
runtime authorization is false and accepted support sets are empty.

## CLI and browser

From the repository root, use the existing `.venv`:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py verify-phase9
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py verify-iteration9
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py serve-phase9
```

`verify-phase9` executes the accepted-release audit, four unchanged historical
audits in their exact historical checkout, source/architecture verification,
the successor pressure matrix, and API/notebook/Node checks. It writes an
ignored execution receipt. The normal `verify-iteration9` additionally runs
the unchanged D11 suites and both old and Phase 9 browser regressions.
Neither command accepts P9-G1 or installs runtime permission.

`serve-phase9` opens a read-only local server at `http://127.0.0.1:4174`.
Visit that address to refresh current checks, inspect exact source hashes and
separate P9-1.7/P9-1.8 results, and download the same status JSON returned by
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
assert status["runtime_authorized"] is False
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

The [scenario register](../../../../../phase-9-grcv4/tranche-1/P9-1.7-1.8-Scenarios.json)
links all six independent-review pressures and the live access scenarios to
executable checks. The [review](../../../../../phase-9-grcv4/tranche-1/P9-1.7-1.8-VerificationReview.md)
and [separate leaf results](../../../../../phase-9-grcv4/tranche-1/P9-1.7-1.8-ExecutionRecord.json)
record the precise claim ceiling and outstanding gates.

The predecessor P9-1.6 policy, auditor, evidence and full prepared artifact
snapshot are retained. V2's exact-path/content-bound successor is the normal
active route; deleting the phase marker cannot restore the old verifier.
No old scientific scenario or accepted tool artifact is relabeled as a Phase 9
implementation result.

### Pressure-result subjects and audit evidence

The panel's separate **Isolated pressure evidence** section loads an exact
probe ID and downloads the same `pressure_projection(root, case_id)` API
payload. For `normal_entry_forbidden_source`, the actual normal CLI rejected
the temporary candidate; its negative-test assertion passed. Both facts stay
visible, alongside the explicit statement that no live permission was created.
`future_explicit_approval_exact_targets` shows the converse simulated admission,
without erasing the old historical false flag or granting current authority.
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
The tracked pressure file is a reproducible coverage index, not a substitute
for those current-input-bound raw results. API/notebook normalized projections
are retained in `surface-evidence.json`; browser output includes screenshots
and the tested JSON downloads.

The source-meaning panel keeps `accepted_frozen` specification authority and
`indeterminate_requires_review` forensic associations separate. Its 152/183
denominator is a source population, not executed V4 tests; fifteen obligations
remain pending under the already reviewed routing. This surface adds no claims.

The future-runtime positive tests use disposable synthetic approval fixtures
with an externally supplied test trust anchor, release/predecessor bindings,
and exact before/after hashes. They test new V4 files and the two proposed
additive integration paths; they do not enact approval. A real runtime policy
and its reviewed dispatch remain P9-1.9 work. Optional completion tests are
likewise scoped synthetic evidence, not executed GRC9V4 conformance.
