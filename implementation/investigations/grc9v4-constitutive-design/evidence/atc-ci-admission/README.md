# Paired A_CI research admission

CI-0–CI-3 are scientifically complete and accepted within their reviewed
paired research scope. The user authorizes the [scoped adjudication](../../decisions/ATCCIClaimDebtAdjudication.md)
after the [final CI-3 PASS](CI3-FinalIndependentReview.md).

- [Four conditional claims and all 28 CI-local debt dispositions](ATCCIClaimDebtLedger.json)
- [Pinned source/graph admission](../../tools/exploratory-side-tool/records/ATCCIResearchAdmission.json)
- [Typed query implementation](../../tools/exploratory-side-tool/tool/src/grcv4_explorer/atc_ci.py)
- [Focused admission and authority tests](../../tools/exploratory-side-tool/tool/scripts/test_atc_ci_research.py)

From repository root:

```bash
TOOL=implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-ci-query discover
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-ci-query audit
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-ci-query claim ATC-CI-REFERENCE-03
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/run.py" atc-ci-query debt ATC7-DB-24
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$TOOL/scripts/test_atc_ci_research.py"
```

CI-local statuses: 14 closed, six partial, eight not activated. All global
debts remain open. DB-05 closes locally through the CI joint-root theorem;
DB-24 closes only for this exact source inventory and adapter. Scientific
references point to preserved certificate bytes. Their earlier pending
flags and working-note HOLDs are historical, superseded by this adjudication.
The review's optional prettier signature diagnostic is not a closure condition;
no scientific checker is rewritten for it and no numerical campaign is rerun.

The graph appends to accepted A_PC/A_OS without rewriting old nodes, edges,
debt meanings or admission pins. Old loaders retain their old scopes. CI
discovery observes its inventory; the audit also validates the full predecessor
context and transitive source bindings. New sources do not self-admit.
There is no native ATC, other-realization, browser/notebook or aggregate
ATC-2/ATC-3 support promotion here.
