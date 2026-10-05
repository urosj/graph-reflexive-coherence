# Tranche 8 evidence access

The side-tool now exposes the accepted shared 8.1 mechanics, pure 8.2 allocator,
all ten bounded 8.3 profile integrations, larger-configuration preparation,
and current 8.4 coverage. It reads existing records; it does not create claims,
accept results, authorize work or rerun models.

With the separate C_PC acceptance, C_OS, A_OS, C_CI, A_CI and C_PC supply
**162 of 322 accepted 8.4b history cells**. Five families own 160 pending cells.
C_PC contributes 34 accepted cells, including the separate literal reset
subject. Raw execution retains its original unaccepted flags; the separately
pinned review records user acceptance. The all-ten parent and `.c`–`.i` remain open.
All ten accepted 8.3 integrations are bounded small-graph results, not ten
arbitrary-graph implementations. Larger-configuration probes retain 16 passed,
16 incomplete and eight rejected outcomes; none is larger-runtime acceptance.
Forty disabled-profile surfaces remain Tranche 9 work. General ATC is not implied.

## Choose the check you need

From the repository root, using the existing `.venv`:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py tranche8-query check
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py tranche8-query status
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py notebook-phase9 --tranche8-only
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py serve-phase9
```

The first three check pinned sources and retained structure, including separate
execution and acceptance identities. They perform **no native trajectory rerun,
dense-oracle comparison or interval-equation recomputation**. The normal
`verify-phase9 --boundary-only` also checks this index alongside current
implementation bindings and release checks; it is not a full scientific rerun.

For an explicitly requested stronger retained check:

```bash
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py tranche8-query verify-retained --family A_OS
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run.py tranche8-query verify-retained --family C_OS
```

A_OS's retained checker checks stored operands, nominal comparisons and bound
certificates. Add `--recheck-numerics` to recompute its interval equations.
C_OS's retained checker already recomputes dense comparisons for both original
and successor results. Neither command runs native trajectories. A fresh
native run is a separate operation using the original review's `--run --output`
instructions and a new output name; never overwrite the accepted execution.

## API, notebook and browser

```python
from pathlib import Path
import sys

root = Path.cwd()  # repository root
tool = root / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool"
sys.path.insert(0, str(tool / "src"))
from grcv4_explorer.tranche8 import tranche8_status, tranche8_source

view = tranche8_status(root)
assert len(view["profiles"]) == 10
assert view["coverage"]["accepted_cells"] == 162
assert view["coverage"]["executed_pending_cells"] == 0
raw, identity = tranche8_source(root, view["coverage"]["record"]["path"])
```

`/api/tranche8` returns that same checked view. The browser's Tranche 8 section
shows mechanics, all-ten coverage, per-case outcomes, larger probes and owners.
Expand each profile to inspect exact source/target declarations, comparison
budgets, schedules and retained forensic traces. Source links retrieve exact
indexed bytes through `/api/tranche8/source?path=...`; arbitrary paths are rejected.
The notebook's executable `query-tranche8` cell uses the same API and clears
previous output before every call. Both surfaces reject stale projections.

This standalone view does not imply the slower full current-boundary status
passed. The full status includes the same `tranche8_evidence` field only when
its independent policy checks pass. Historical `specialization_admission_review`
still means the original 7.8 decision; current next-work text comes from the
Tranche 8 index, not that old entry permission.

## Evidence and authority boundaries

The two original C_OS phase-one cases committed events and then failed
continuation. They remain **incomplete cases**. Only their separately named,
successful successors receive positive coverage credit. Execution-time
`user_accepted=false` flags remain untouched; later scoped reviews record the
acceptance. The C_OS dense comparison is not an interval certificate, and the
A_OS pointwise interval checks are not a uniform parameter tube.

For scientific investigation use the typed forensic API described in
[AgenticQueryGuide](./AgenticQueryGuide.md). This implementation view preserves
retained trace classifications and references, but does not refresh those
queries or change `indeterminate_requires_review` into accepted authority.

The enclosing Phase 9 status digest uses RFC 8785 number serialization so
Python and browser hashes agree on the retained scientific floating-point
values. This changes no underlying execution or scientific identity.

Historical G2 executions also retain their original bytes. The finite
`P9-8-SideToolSourceBridge.json` reconstructs their pre-Tranche-8 source identities
from explicitly enumerated hashes and Git preimages, including later-added
helper files absent from historical rosters. This fixes stale discovery checks;
it does **not** prove that old executions certify the changed implementation.
Unknown paths and third identities still fail. The existing source-reuse tables
are composed once in order instead of repeatedly recursing through the chain.
Only immutable Git-object hashes are cached; live files are reread.

## Portability and maintenance

Use a clone containing the accepted Git history, not just exported source files
or a shallow snapshot. No machine-local paths, external bundles or generated
run directory are needed for this view. Immutable records must match the pinned
checkpoint on disk. Mutable handoff/plan references deliberately retrieve their
exact historical Git bytes; the interface labels that distinction.

For the next accepted family, extend the index's explicit checkpoint/run roster,
regenerate `tranche8-evidence.js` from `browser_source(build())`, and refresh
the ordinary maintenance bindings. Do not edit original runs or infer acceptance
from an unchecked directory scan. The projection is generated display data, not
a second acceptance ledger. Its update must preserve all pending families and
the original negative cases.

## Focused cross-surface scenarios

| Scenario | Required outcome |
| --- | --- |
| Load API, actual notebook cell and browser | Same checked ten-profile view; 162/322 accepted, 160 pending |
| Inspect original C_OS phase-one case | Event committed, case incomplete, first failure visible |
| Inspect its successor | Separate input/result identity and scoped acceptance |
| Inspect accepted C_CI execution | All case outcomes, exact sources and separate scoped acceptance; original timeout remains incomplete |
| Inspect accepted A_CI execution | All case outcomes, exact sources and joint-root/W-lifecycle scope; 32 cells credited through separate scoped acceptance |
| Inspect accepted C_PC execution | Seventeen cases, 34 cells and signed Read-Back/flat pressure; separate scoped acceptance |
| Inspect a larger CI/PC pass or RG rejection | Probe outcome retained; larger-runtime acceptance remains false |
| Alter counts, acceptance, source hash or runtime roster | Reject; no stale fallback or widened permission |
| Request an unindexed or traversal path | Reject without reading it |
| Fail a refresh after success, or resolve an old request late | Clear success; do not restore stale output |
| Read historical handoff after current handoff changes | Retrieve the pinned Git bytes and advertised original hash |

The focused tests are `verification/test_tranche8_evidence.py` under Phase 9
and `tool/phase9-web/tranche8.test.mjs`. Numerical campaign reruns are not part
of these presentation and provenance scenarios.

The catch-up was checked with ten focused Python tests, 44 JavaScript tests,
the actual notebook cell, local HTTP/source retrieval and desktop/mobile browser
access, and the live full-status payload through the shipped browser validator.
The phase-aware boundary/index check passed. No native numerical campaign or
full historical replay suite was rerun; the broad G1 surface fixture now uses
the current trusted support/permission rosters instead of old singleton counts.

## Accepted C_CI execution

The shared view binds C_CI execution to its separate 2026-10-05 user acceptance.
C_CI sources have finite content pins; altered bytes fail closed. They can be
retrieved through the same source links. That checkpoint raised the accepted
total to 96/322. Raw execution retains its original unaccepted flags.
The combined record contains eight unchanged retained passes and eight new
passes. The original D45 operational timeout remains linked and explicitly
incomplete; increasing its wall-clock budget did not change numerical criteria.

Use `run.py tranche8-query verify-retained --family C_CI` for the explicit
retained checker, adding `--recheck-numerics` only when independent interval
recomputation is needed. Neither option reruns native trajectories. The
[C_CI review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-CCIRuntimeReview.md)
states the numerical scope and commands for a separately named native run.

## Accepted A_CI execution

The shared view binds A_CI execution to its separate 2026-10-05 user acceptance and
[bounded review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-ACIRuntimeReview.md).
Source pins authenticate the exact execution and the separate decision; raw
execution flags remain unchanged. Its 32 accepted cells brought the total at
that checkpoint to 128/322, with 194 pending. Use `run.py tranche8-query verify-retained --family A_CI` for retained
identity, stage, schedule and bound checking, or add `--recheck-numerics` for
independent interval recomputation. Neither runs a native trajectory. Normal
API/browser/notebook status authenticates source bytes and retained structure,
not a new scientific execution or aggregate acceptance.

The A_CI result uses compact JSON to avoid storing indentation at numerical
record scale. Its schema, values and scientific record digest are unchanged;
the [storage note](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-ACIRuntimeReview.md#lossless-storage-compaction)
records exact reconstruction of the original accepted file. Retrieval returns
the compact bytes with their current advertised SHA-256. For future large
records, prefer compact serialization before freezing source-byte bindings;
do not silently reformat previously pinned files or drop numerical evidence.

## Accepted C_PC execution

The [bounded C_PC review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-CPCRuntimeReview.md)
defines seventeen native companions, including the separate literal reset
subject. Its source archive, target zero pair, carrier-loss receipts, old-Z
reads and one incoming-source write are visible through the same source
routes. Signed Read-Back/flat pressure supplements the current/source and
writer evidence, without changing the retained execution.

Use `run.py tranche8-query verify-retained --family C_PC` to check both records;
add `--recheck-numerics` for independent interval recomputation. The status
query remains read-only source/structure inspection. The user accepted all
34 cells on 2026-10-05 through the review's
[separate scoped decision](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-CPCRuntimeReview.md#scoped-user-acceptance).
Shared coverage is 162/322 accepted and 160 pending. Raw execution and
scientific restrictions remain unchanged; acceptance requires no native rerun.
