# Phase T Experiments Refactor: Iteration 4B Helper Layout

## Purpose

Record the shared helper boundary introduced in Iteration 4B without changing
the `64`-test discovery baseline established in Iteration 4A.

## Helper Boundary

Shared test support now lives in:

- `tests/telemetry/_experiments_test_support.py`

That private helper module now owns:

- the shared script path constants
- the shared landscape seed constants
- the generic `_load_script_module(...)` helper
- the named `_load_grcv3_*_script_module()` wrappers used by the current tests

`tests/telemetry/test_experiments.py` remains the discovered test module, but
its top-of-file support block is now imported from the helper module instead
of being defined inline.

## Preserved Boundaries

- test method names are unchanged
- test bodies and assertions are unchanged
- the six concern-shaped test classes introduced in Iteration 4A remain the
  owning test surface
- no script validation or emission tests were deduplicated in this step
- no public telemetry entry-point coverage was intentionally changed

## Verification

- syntax/import verification:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m py_compile tests/telemetry/test_experiments.py tests/telemetry/_experiments_test_support.py`
- post-helper discovery:
  - `64` discovered ids
  - unchanged from Iteration 4A
- full run:
  - `MPLCONFIGDIR=/tmp/mpl ./.venv/bin/python -m unittest discover -s tests/telemetry -p 'test_experiments.py'`
  - `Ran 64 tests in 597.778s`
  - `OK`

## Why This Stops Here

Iteration 4B centralizes the shared support block only. It does not yet:

- replace the repeated trace-script test pairs
- change test names or discovery shape
- collapse multiple bespoke script tests into a table-driven form

Those are reserved for Iteration 4C so the helper move can stand on its own
as a no-drift structural step.
