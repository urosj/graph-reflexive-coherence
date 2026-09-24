# Bounded Candidate-A ATC research queries — all five realizations

The new [CI+PC program](../../../decisions/ATCCIPCoupledProgram.md) is
now admitted by its separate successor described below. Its reviewed CIP-0
checker retains historical pending flags and uses the predecessor API for
lemma traces. Passing an older context's audit alone does not admit CIP.
CIP-0/CIP-1 now have independent scientific PASS; their reviews and additive
DB-04 route are in `evidence/atc-cip-successor`. CIP-2 reference/conformance
now has independent scientific PASS and local retained-record integrity PASS.
The reviewer's exact-record comparison remains unclaimed because they lacked
the certificate; see the [review disposition](../../../evidence/atc-cip-review/README.md).
All-28 scoped adjudication and exact source admission are now separately
completed through `atc-cip-query`, not by widening these predecessor APIs.

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

## Paired A_PC successor

The frozen A_OS command remains unchanged. Its passing audit does not cover
CI/PC observations. The new [A_PC adjudication](../../../decisions/ATCPCClaimDebtAdjudication.md)
admits five conditional PC claims and 28 PC-specific debt transformations
through a separate append-only context, loading the accepted A_OS baseline.
The reviewed shared CI/PC checkpoint is frozen; future CI work goes into
separate successor files. This historical PC loader does not admit CI handles;
the later CI successor below does, without changing the PC admission.

```sh
.venv/bin/python "$TOOL/scripts/run.py" atc-pc-query discover
.venv/bin/python "$TOOL/scripts/run.py" atc-pc-query audit
.venv/bin/python "$TOOL/scripts/run.py" atc-pc-query claim ATC-PC-DOMAIN-04
.venv/bin/python "$TOOL/scripts/run.py" atc-pc-query debt ATC7-DB-24
.venv/bin/python "$TOOL/scripts/test_atc_pc_research.py"
```

For Python, use the same `root` and `side` as above:

```python
from grcv4_explorer import atc_pc

pc_context = atc_pc.load_current_forensic_context(root, side)
claim = atc_pc.reconstruction_path(pc_context, "ATC-PC-DOMAIN-04")
debt = atc_pc.debt_lifecycle(pc_context, "ATC7-DB-24")
control = atc_pc.reconstruction_path(pc_context, "ATC-PC-CARRIER-02")
```

The debt result is explicitly PC-scoped: 13 locally closed, six partial,
nine not activated, all globally open. DB-24 closes for this exact admission
only. The superseded control is queryable but excluded from accepted backward
support. Source discovery checks transitive execution bindings as well as
retained outputs. Changed/missing sources and unprocessed additions fail
closed; a recomputed manifest cannot bypass its pinned identity.

The analytic whole-box result assumes a resolved admitted event; the executed
reference covers the quadratic subclass. Active-environment transport remains
a future extension, not an unmet PC-4 criterion. Native/aggregate status does
not change. Historical pending flags in certificates are superseded only by
this explicit ledger. Browser/notebook projections are not added here.

## Paired A_CI successor

Final independent review passes CI-0–CI-3; the user authorizes
[scoped adjudication](../../../decisions/ATCCIClaimDebtAdjudication.md).
Four conditional CI claims are now admitted on top of PC/A_OS. Twenty-eight
CI-local debt rows remain distinct: 14 closed, six partial, eight not activated,
all globally open. DB-05 closes through the bounded joint-root theorem; DB-24
closes for this pinned CI inventory only. No other realization is admitted.

```sh
.venv/bin/python "$TOOL/scripts/run.py" atc-ci-query discover
.venv/bin/python "$TOOL/scripts/run.py" atc-ci-query audit
.venv/bin/python "$TOOL/scripts/run.py" atc-ci-query claim ATC-CI-REFERENCE-03
.venv/bin/python "$TOOL/scripts/run.py" atc-ci-query debt ATC7-DB-24
.venv/bin/python "$TOOL/scripts/test_atc_ci_research.py"
```

```python
from grcv4_explorer import atc_ci

ci_context = atc_ci.load_current_forensic_context(root, side)
claim = atc_ci.reconstruction_path(ci_context, "ATC-CI-REFERENCE-03")
debt = atc_ci.debt_lifecycle(ci_context, "ATC7-DB-24")
pc_debt = atc_pc.debt_lifecycle(ci_context, "ATC7-DB-05")  # still PC-scoped
```

CI reconstruction delegates historical claims without promotion. The CI debt
function is explicitly CI-scoped; use the corresponding older function for
PC/A_OS debts. Old graphs/records and reviewed certificates are preserved.
Their historical pending flags are superseded only by the new ledger.
CI discovery observes both successor/admission evidence directories and
transitive scientific bindings; the audit also checks the accepted predecessor
context. Missing, changed or unprocessed evidence fails closed. No native,
browser/notebook or aggregate status is added. Do not rerun the scientific
campaign merely to change acceptance metadata or add CI files to the PC pin.

The ATC admission includes one exact navigation-only compatibility correction:
the ATC2 review README's command now uses its evidence location. Its historical
source hash is checked by reversing exactly that single path substitution;
the current bytes are independently pinned. Scientific evidence records and
their claims are unchanged; other source differences still fail closed.

## Paired A_CI+PC successor

The [CIP adjudication](../../../decisions/ATCCIPClaimDebtAdjudication.md) admits
ROOT-00, CHAIN-01 and REFERENCE-02. All 28 CIP-local debts are explicit:
14 closed, six partial, eight not activated; all globally open. DB-04 retains
its additive consumer route; DB-05 covers the combined root, DB-15 the signed
lossless history lift and DB-24 this exact pinned admission.

```sh
.venv/bin/python "$TOOL/scripts/run.py" atc-cip-query discover
.venv/bin/python "$TOOL/scripts/run.py" atc-cip-query audit
.venv/bin/python "$TOOL/scripts/run.py" atc-cip-query claim ATC-CIP-REFERENCE-02
.venv/bin/python "$TOOL/scripts/run.py" atc-cip-query debt ATC7-DB-04
.venv/bin/python "$TOOL/scripts/test_atc_cip_research.py"
```

```python
from grcv4_explorer import atc_ci, atc_cip

cip_context = atc_cip.load_current_forensic_context(root, side)
claim = atc_cip.reconstruction_path(cip_context, "ATC-CIP-REFERENCE-02")
debt = atc_cip.debt_lifecycle(cip_context, "ATC7-DB-15")
ci_debt = atc_ci.debt_lifecycle(cip_context, "ATC7-DB-15")  # still CI-scoped
```

Full ancestry includes accepted CI/PC lemmas with their original classifications
and scopes; it does not splice standalone dynamics or enlarge their domains.
Discovery covers `atc-cip`, `atc-cip-successor`, `atc-cip-review` and
`atc-cip-admission` evidence plus bound execution sources. Changes, missing
inputs or new unprocessed evidence fail closed. Navigation READMEs are not
automatically admitted; the specific CIP-2 review disposition README is pinned
explicitly as supporting evidence. Historical certificates/graphs are unchanged.
Native, aggregate and browser/notebook support are not added.

## A_RG2b successor and five-realization research closeout

The [RGATC adjudication](../../../decisions/ATCRGATCClaimDebtAdjudication.md)
admits seven conditional research claims after reported audit PASS and explicit
user authorization. All 28 RG-local debts are reconciled: 14 closed, six partial,
eight inactive. This successor extends CIP without changing earlier records.
The package's historical pending flags remain unchanged; the new ledger is
the current authority. Old-context audits do not admit these new claims.

```sh
.venv/bin/python "$TOOL/scripts/run.py" atc-rgatc-query discover
.venv/bin/python "$TOOL/scripts/run.py" atc-rgatc-query audit
.venv/bin/python "$TOOL/scripts/run.py" atc-rgatc-query claim RGATC-R-REFERENCE
.venv/bin/python "$TOOL/scripts/run.py" atc-rgatc-query debt ATC7-DB-05
.venv/bin/python "$TOOL/scripts/run.py" atc-rgatc-query summary
.venv/bin/python "$TOOL/scripts/test_atc_rgatc_research.py"
```

```python
from grcv4_explorer import atc_rgatc

context = atc_rgatc.load_current_forensic_context(root, side)
claim = atc_rgatc.reconstruction_path(context, "RGATC-R-REFERENCE")
debt = atc_rgatc.debt_lifecycle(context, "ATC7-DB-24")
five_programs = atc_rgatc.candidate_a_closure(context)
```

Discovery observes all package code/proofs/certificates/manifests, the reported
review and new admission ledger. Package-relative paths are not mistaken for
repository-relative inputs. The outer navigation README is excluded; package
READMEs remain bound by the exact inventory. The audit validates the entire
predecessor chain. Changed, missing or new unprocessed evidence holds queries.

RG2b contract provenance and fixed-H CI/A_OS lemmas retain their classifications;
they do not transfer realization dynamics, duration domains or native completion
authority. The new completion is admitted only at its own research scope.
The full E/R execution is supplied evidence, not a newly claimed local rerun.

The source-bound summary derives [five bounded program closures](../../../decisions/ATCCandidateAResearchClosure.md)
from the admitted ledgers: 54 conditional claims and one A_OS negative exclusion,
with 140 separate scoped dispositions over 28 globally open origin debts.
It does not claim universal Candidate-A support, Candidate C, native ATC,
or aggregate ATC-2/ATC-3 closure. No browser/notebook projection is added.
