# Bounded A_OS ATC research queries

This append-only research context admits the reconciled ATC source inventory,
not native ATC implementation or aggregate ATC-2 closure. The old D10/D11/P9
loaders retain their exact historical meaning; they do not resolve ATC IDs.

From repository root, with the repository virtual environment:

```sh
TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
.venv/bin/python "$TOOL/scripts/run.py" atc-query discover
.venv/bin/python "$TOOL/scripts/run.py" atc-query audit
.venv/bin/python "$TOOL/scripts/run.py" atc-query claim ATC-LSF-G7-CL-06
.venv/bin/python "$TOOL/scripts/run.py" atc-query debt ATC7-DB-24
```

These commands print JSON and do not write evidence. Discovery covers the
research evidence directory, including retained review inputs; source identity
drift, missing files and newly unprocessed evidence hold current queries.
Navigation READMEs are not scientific source records. The older
`discover-sources` command is explicitly the pre-ATC inventory; its green state
alone is not ATC validation. Use `atc-query discover` and `audit` for this scope.

## Python API

```python
from pathlib import Path
import sys

root = Path.cwd()
side = root / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
sys.path.insert(0, str(side / "tool/src"))
from grcv4_explorer.atc import (
    load_current_forensic_context, reconstruction_path, debt_lifecycle,
)

context = load_current_forensic_context(root, side)
claim = reconstruction_path(context, "ATC-LSF-G7-CL-06")
debt = debt_lifecycle(context, "ATC7-DB-24")
proposal = reconstruction_path(context, "ATC7-CL-01")
```

ATC reconstruction traverses the complete accepted predecessor lineage rather
than the historical API's bounded-neighborhood projection. Every accepted row
carries its originating adjudication pointer and accepted-scope pointer.
Keep `classification`, `source_ref`, `edge_refs`, graph/bundle identities and
`trace_digest` when reporting results. A predecessor link records lineage;
it is not by itself proof that an older theorem covers a larger domain.

Proposal queries return `proposed_origin_not_accepted`. Proposed origins appear
separately from accepted backward support. Forward obligations are excluded
from claim reconstruction, and debt queries report them as forward work.
`A_OS_research_status` never replaces `origin_status`: all global origin debts
remain undischargeable by this bounded result alone. The local states are
13 closed, 6 partial and 9 not activated; DB-24 closes only for this exact
admitted inventory. No normative paper/specification or runtime status is
manufactured from these research classifications.

## Focused regression test

```sh
.venv/bin/python "$TOOL/scripts/test_atc_research.py"
```

This checks exact reconstruction, source/graph identity, inherited graph
preservation, reciprocal lineage, status boundaries and mutation rejection.
It is not a rerun of the numerical research campaigns. Browser and notebook
projections have not been added for this checkpoint; the actual exposed
surfaces are the typed Python API and read-only command above.
