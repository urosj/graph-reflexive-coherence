# D11 API, Notebook, And Browser UX

**Status:** ET-C11 candidate implemented and verified; human acceptance pending

This interface exposes the accepted D11-C and D11-G9 authority admitted by
ET-C10. It is a read-only presentation surface, not a new evidence source.

## Browser

From the repository root:

```bash
TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
.venv/bin/python "$TOOL/scripts/run.py" serve-iteration11-d11
```

Open the printed local URL and select **D11** in the header. The workspace
supports:

- D11-C, D11-G9, or combined scope;
- filtering by claims, debts, profiles, candidates, objects, contracts, or
  verification obligations;
- identifier and readable-label search;
- source-bound trace rows and machine-exact payloads;
- exact record, JSON pointer, and digest receipts; and
- support relationships with their recorded semantics.

The browser bundle contains 60 precomputed forensic API outputs and nine
source-bound profile/obligation projections. JavaScript verifies every digest
before rendering and contains no scientific inference or propagation logic.

## Notebook

Run the governed notebook:

```bash
.venv/bin/python "$TOOL/scripts/run.py" notebook-iteration11-d11
```

The source notebook is
[d11_successor_recipes.ipynb](../tool/notebooks/d11_successor_recipes.ipynb).
It writes six derived traces under `tool/generated/iteration11-notebook/`:

```text
d11-c-claim.json
d11-c-debt.json
d11-c-contract.json
d11-g9-claim.json
d11-g9-debt.json
d11-g9-contract.json
```

The runner proves each output is canonically byte-identical to both the direct
Python API result and the corresponding browser payload.

## Python API

Use the successor loader for D11 queries:

```python
from grcv4_explorer.forensic import contract_provenance, reconstruction_path
from grcv4_explorer.paths import SIDE_TOOL_ROOT, repository_root
from grcv4_explorer.successor import load_successor_forensic_context

context = load_successor_forensic_context(repository_root(), SIDE_TOOL_ROOT)
claim = reconstruction_path(context, "D11-C-CL-O-001")
contract = contract_provenance(context, "D11-G9-EC-EXACT-OLD-PORT-MAP")
```

Continue using `load_forensic_context` only when the historical D10/ET-C2
snapshot is specifically required. It intentionally rejects D11 identifiers.

## Verification

The normal verifier now covers the API, notebook, browser components, and
desktop/mobile interaction:

```bash
.venv/bin/python "$TOOL/scripts/run.py" verify-iteration9
```

Focused commands are also available:

```bash
.venv/bin/python "$TOOL/scripts/run.py" build-iteration11-d11-ux
.venv/bin/python "$TOOL/scripts/run.py" audit-iteration11-d11-ux
.venv/bin/python "$TOOL/scripts/run.py" test-iteration11-d11-ux
.venv/bin/python "$TOOL/scripts/run.py" browser-iteration11-d11
```

Neither surface marks paper propagation, specification propagation, or runtime
conformance complete. GRC9 and GRC9V3 remain outside the authorized change
scope.
