# Native spark integration regressions

P9-10.3-NATIVE-SPARK has 28 passing tests in four parallel groups. All ten
accepted completion campaigns are reused. Inspect the retained result with:

```python
from grcv4_explorer.spark_native_regressions import native_spark_regressions
value = native_spark_regressions(repo_root)
```

The Phase 9 browser button **Inspect native integration results**, notebook cell
`native-spark-regressions`, and `/api/native-spark/regressions` use the same
read-only checker. `/api/native-spark/regressions/source` returns the bound record.
Inspection checks sources, test identities, scope and accepted evidence; it
does not rerun tests. A failed refresh clears old output.

From the repository root, the equivalent retained check is:

```bash
PYTHONPATH=.:src:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p9103_native_spark.py --check
```

`--run --workers 4` is an explicit fresh regression execution and refuses to
overwrite the retained record; it is not needed to inspect the completed run.

The all-ten persistence checks use fresh declarations and forbid numerical
steps. Full completion trajectories/cold replay are retained campaign evidence;
fresh short C_OS lifecycle tests cover the shared transaction mechanism.
Ordinary V4/V3 compatibility remains distinct from the unsupported implicit
native-exact-resource/V3 crossing. These checks grant no broader capability,
hierarchy or G4. User acceptance is separate from the execution result.

The user accepted the bounded supplement on 2026-11-03. The current view includes
the separate acceptance decision and retains `execution_status` and
`execution_user_accepted`; the source download remains the original run record.
