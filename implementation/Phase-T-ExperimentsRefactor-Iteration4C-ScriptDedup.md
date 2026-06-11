# Phase T Experiments Refactor: Iteration 4C Script Deduplication

## Purpose

Record the script-test deduplication that replaced the repeated bespoke script
validation/emission methods with shared helpers and a table-driven generated
test surface, while preserving the Iteration 4A discovery baseline.

## Structural Change

Inside `tests/telemetry/test_experiments.py`, the `TelemetryScriptTest`
surface now uses:

- `_assert_script_rejects_non_positive_steps(...)`
- `_assert_script_emits_output(...)`
- `_ScriptRejectSpec`
- `_ScriptEmitSpec`
- `_SCRIPT_REJECT_SPECS`
- `_SCRIPT_EMIT_SPECS`
- generated methods attached with `setattr(...)`

This replaces the repeated copy-paste script test scaffolding with a shared
spec-table pattern.

## Preserved Boundary

- discovered test id count remains `64`
- all `TelemetryScriptTest.test_*` ids from Iteration 4A are preserved
- no script coverage was dropped
- the semantic assertions for each script output remain script-specific
- no non-script test classes were structurally changed in this step

## Migration Note

Iteration 4C changes internal structure materially, but it does not change the
discovered ids. So there is no many-to-one or one-to-many replacement map to
record against Iteration 4A.

The same script-test ids are now generated from the shared spec tables rather
than defined as 30 bespoke methods.

## Verification

- syntax/import verification:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m py_compile tests/telemetry/test_experiments.py`
- post-dedup discovery:
  - `64` discovered ids
  - unchanged from Iteration 4A / 4B
- targeted regression rerun after fixing the temporary-directory assertion bug:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest tests.telemetry.test_experiments.TelemetryScriptTest.test_grcv3_landscape_script_can_emit_checkpoint_artifacts`
  - `Ran 1 test in 0.636s`
  - `OK`
- full run:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
  - `Ran 64 tests in 595.451s`
  - `OK`

## Boundary Notes

- The first full 4C run surfaced one real helper bug: the landscape checkpoint
  artifact assertion ran after the temporary directory context had already
  closed.
- That helper bug was fixed by moving output assertion execution inside the
  temporary-directory context.
- No test semantics were broadened beyond that fix.
