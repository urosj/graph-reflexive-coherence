# Accepted paired A_CI+PC research admission

- [Scoped decision](../../decisions/ATCCIPClaimDebtAdjudication.md)
- [Three conditional claims and all 28 CIP-local debts](ATCCIPClaimDebtLedger.json)
- [Pinned source admission](../../tools/exploratory-side-tool/records/ATCCIPResearchAdmission.json)
- [Independent review / local integrity distinction](../atc-cip-review/README.md)

Fourteen CIP-local debts close, six remain partial, eight are not activated.
All origin debts stay globally open. Accepted CI/PC/A_OS records and graphs
are unchanged; reviewed CIP certificates retain their original pending flags.
This explicit successor, not an edited certificate, supplies acceptance.

Graph digest: `541bf8c23afcca2f5f3b3a61e9c986e9720b270610759b2e0f4c8105673cb89c`.
Admission digest: `f98cb10a902dd11b6df76a36fae60aa23c55b648b8ddeee8df64b2b411c610cc`.

From repository root:

```sh
TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-cip-query audit
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-cip-query discover
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-cip-query claim ATC-CIP-REFERENCE-02
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-cip-query debt ATC7-DB-04
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/test_atc_cip_research.py"
```

These read-only checks rebuild the admitted graph and test authority boundaries;
they do not rerun scientific campaigns. Native runtime, browser/notebook support,
whole-box formation and aggregate ATC-2/ATC-3 acceptance are not added.

The initial admission-test run exposed a raw KeyError for an invalid pointer
and two test mocks still aimed at the predecessor module. The new CIP adapter
now reports SourceAdmissionError for invalid pointers; the mocks target CIP.
No scientific data or criteria were changed.
