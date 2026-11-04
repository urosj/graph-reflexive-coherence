# Current native spark claim/debt disposition — P9-10.5

The [decision](../../../decisions/SparkCompletionNativeDebtReconciliation.md)
and [successor ledger](../../../evidence/spark-completion/native/ClaimDebtLedger.json)
connect the accepted scientific contracts to exact accepted native subjects.
The user accepted P9-10.5 on 2026-11-04; the separate
[decision](../../../../../phase-9-grcv4/tranche-10/P9-10.5-NativeSpark-Acceptance.json)
binds the unchanged reconciliation ledger. Current views expose acceptance while
retaining its original review-time pending flags. All thirty native portions are discharged. Four original lifecycle rows are
split explicitly, retaining broader hierarchy work. Historical research contexts
still show their research-time pending obligations; they are not current native
status and are not rewritten.

From the repository root with the side-tool `tool/src` on `PYTHONPATH`:

```python
from pathlib import Path
from grcv4_explorer.spark_native_debts import native_spark_debts, query

view = native_spark_debts(Path.cwd())
query(view, "debt_lifecycle", "SC-DEBT-STABILITY")
query(view, "verification_obligation", "SC-VO-NATIVE-LIFECYCLE")
query(view, "scientific_claim", "SC1-CL-C-RETURN")
```

Typed results include source references, original claim/obligation fields,
bounded disposition, exact evidence and a trace digest. Unknown IDs fail closed.
Use the existing scientific forensic API for full normative provenance; these
native queries do not promote conditional claims or add backward proof edges.

`GET /api/native-spark/debts` exposes the same checked ledger.
`/api/native-spark/debts/source?name=ledger` and `?name=decision` expose its two
fixed sources. `?name=acceptance` exposes the separate user decision. No route executes numerical work. The browser's **Inspect current
claim/debt ledger** button and notebook `native-spark-debts` cell use this view;
failed refresh clears the previous result. P9-10.6, G4 and hierarchy remain separate.
