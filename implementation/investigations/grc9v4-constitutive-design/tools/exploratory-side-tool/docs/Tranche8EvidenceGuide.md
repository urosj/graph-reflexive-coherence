# Tranche 8 evidence access

The side-tool now exposes the accepted shared 8.1 mechanics, pure 8.2 allocator,
all ten bounded 8.3 profile integrations, larger-configuration preparation,
and current 8.4 coverage. It reads existing records; it does not create claims,
accept results, authorize work or rerun models.

With the separate A_RG2b acceptance, all ten families supply **322 of 322
accepted 8.4b history cells**. No cells remain pending acceptance.
C_PC contributes 34 accepted cells, including the separate literal reset
subject. Raw execution retains its original unaccepted flags; the separately
pinned reviews record user acceptance. The A_PC successor contributes 32
accepted cells through its own separate scoped decision. C_CI_PC adds 32
accepted cells through its own separate scoped decision.
The bounded all-ten P9-8.4b item is closed; P9-8.4c–i remain open.
`coverage.boundary_contract` now exposes the first `.c` task: 32 layouts,
640 both-role obligations (600 new, 40 exact-reuse candidates), budgets,
prerequisites and exact contract/review links. The user accepted the matrix and
budgets, with zero native executions or accepted `.c` cells. Its structural
checks do not certify new numerical targets or reopen `.b` acceptance.
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
assert view["coverage"]["accepted_cells"] == 322
assert view["coverage"]["executed_pending_cells"] == 0
assert view["coverage"]["boundary_contract"]["counts"]["history_cells"] == 640
assert view["coverage"]["boundary_contract"]["counts"]["executed_cells"] == 0
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
| Load API, actual notebook cell and browser | Same checked ten-profile view; 258/322 accepted, 64 pending |
| Inspect original C_OS phase-one case | Event committed, case incomplete, first failure visible |
| Inspect its successor | Separate input/result identity and scoped acceptance |
| Inspect accepted C_CI execution | All case outcomes, exact sources and separate scoped acceptance; original timeout remains incomplete |
| Inspect accepted A_CI execution | All case outcomes, exact sources and joint-root/W-lifecycle scope; 32 cells credited through separate scoped acceptance |
| Inspect accepted C_PC execution | Seventeen cases, 34 cells and signed Read-Back/flat pressure; separate scoped acceptance |
| Inspect accepted A_PC execution | Sixteen cases, both W/Z histories, signed-read certificates and consumer effects; 32 cells credited through separate scoped acceptance |
| Inspect accepted C_CI_PC execution | Sixteen cases, composite chart/root certificates, signed vectors and carrier effects; 32 cells credited through separate scoped acceptance |
| Inspect accepted A_CI_PC execution | Sixteen cases, full composite roots, exact W lineage and separate W/Z consumer controls; 32 cells credited through separate scoped acceptance |
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
Shared coverage at that checkpoint was 162/322 accepted and 160 pending. Raw execution and
scientific restrictions remain unchanged; acceptance requires no native rerun.


## Accepted A_PC execution

The [bounded A_PC review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-APCRuntimeReview.md)
records sixteen layout companions, both history roles, exact W transport and
complete Z archive/reset. Unlike C_PC's separate signed-stage supplement,
A_PC retains its signed Read-Back and lowered-vector certificates in each
native read record. W/Z consumer controls and final read-path effects stay
bounded by full formula error plus ULP margins. These are distinct from
endpoint hysteresis or arbitrary-graph support.

Use `run.py tranche8-query verify-retained --family A_PC` to check staged
operands and saved certificates; add `--recheck-numerics` to recompute interval
equations and effects without native trajectory reruns. All surfaces bind the
[separate 2026-10-05 acceptance](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-APCRuntimeReview.md#scoped-user-acceptance)
of all 32 A_PC cells: 194/322 accepted, with 128 pending across four families.
Raw execution flags stay unchanged. Exact source links retrieve the manifest,
result and review; no generated projection grants acceptance on its own.


The A_PC update passes thirteen source/API tests, eight browser logic tests,
both notebook cells and the real HTTP desktop/mobile browser scenario. The
explicit retained CLI command and full independent interval recomputation
also pass without native trajectory reruns. The current-boundary audit checks
these source and projection bindings without supplying acceptance on its own.


## C_CI_PC accepted bounded execution

The [bounded composite review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-CCIPCRuntimeReview.md)
defines sixteen native companions and 32 history cells. The same CLI/API/notebook/
browser surfaces expose composite contraction and strict source slack, signed
Read-Back/flat checks, fixed old-Z root inputs, the same-root-source writer and
next-root history effects. Source links retain complete input, result, review
and independent numerical-recheck identities. The user's separate scoped acceptance on 2026-10-06 supplies credit for these
32 cells: coverage is 226/322 accepted, with 96 pending across three families. Parent 8.4b and later work remain open.

Use `run.py tranche8-query verify-retained --family C_CI_PC` to check saved
operands, outputs and certificates, or add `--recheck-numerics` for independent
interval/effect recomputation. Neither reruns native trajectories. Normal
status authenticates pinned sources and retained structure. The gain-two profile
and effect summaries do not establish amplitude equivalence, endpoint hysteresis,
stability or arbitrary-graph support; the D10 claim restrictions remain visible.


This successor passes fourteen source/API tests, nine browser logic tests, both
notebook cells and the real HTTP desktop/mobile scenario. The explicit retained
CLI command, complete independent numerical recomputation and current-boundary
audit also pass. These checks preserve the separate user-acceptance decision.


## Accepted A_CI_PC execution

The [bounded A composite review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-ACIPCRuntimeReview.md)
binds sixteen layouts and 32 history cells. Shared surfaces expose independent
whole-chart admission, joint residual/full-root certificates, signed Read-Back,
both-role exact W lineage, complete Z archive/reset and separate W/Z writer
effects at their next-root consumers. Exact source routes include the numerical
recheck. The separate scoped user decision of 2026-10-06 credits these 32
cells: 258/322 are accepted, with 64 pending across C_RG2b and A_RG2b. Raw
execution flags remain unchanged; parent 8.4b and later work remain open.

Use `run.py tranche8-query verify-retained --family A_CI_PC` for retained
structure, or add `--recheck-numerics` to recompute interval equations and
counterfactual effect margins. Neither repeats native trajectories. The source
review retains the gain-two, bounded-root, event-versus-continuation and
no-endpoint/no-stability claim limits.


This successor passes fifteen source/API tests, ten browser logic tests, both
notebook cells and the real HTTP desktop/mobile scenario. The retained CLI
command, complete independent numerical recomputation and current-boundary
audit also pass, preserving the separate user-acceptance decision.


## C_RG2b scoped acceptance

The [bounded C_RG2b review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-CRG2bRuntimeReview.md)
binds all sixteen layouts and both histories. Shared surfaces expose actual
six-level signed chains, full section and signed-read certificates, Euclidean
current and row-sum geometry bridges, lagged invariance and held-section
mechanism controls. Exact source retrieval includes numerical recomputation.
The separate [2026-10-06 scoped user decision](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-CRG2bRuntimeReview.md#scoped-user-acceptance)
credits all 32 cells: 290/322 are accepted, with 32 A_RG2b cells pending. Raw
execution and recheck flags stay unchanged; parent 8.4b remains open.

Use `run.py tranche8-query verify-retained --family C_RG2b` for retained
structure, or add `--recheck-numerics` for complete independent interval and
effect recomputation without native trajectories. The signed argument completion
is separately accepted; it does not inherit the paper's exterior compact-support
property. Completion-relative Lipschitz uniqueness does not close the C1 debt,
prove arbitrary-graph support or promise indefinite positive continuation.


The C_RG2b view binds completed cases and their independent numerical checks.
Suspended/incomplete runs, working journals and progress checkpoints are not
published or required by the retained checker. The final case bodies and
independent case-check digests are unchanged by this retention decision.

This successor passes sixteen source/API tests, eleven browser logic tests, both
notebook cells and the real HTTP desktop/mobile scenario. The retained CLI
command, complete independent numerical recomputation and current-boundary
audit also pass, preserving the separate user-acceptance decision.


Large retained JSON is now a byte-exact, ignored local copy of an adjacent XZ
archive. The current evidence index restores missing copies automatically;
standalone historical readers first run `python scripts/evidence_storage.py restore`
from the repository root. This is storage reconstruction, not a numerical rerun
or a new acceptance. See the [storage and value guide](../../../../../../docs/reference/EvidenceStorage.md)
for archive links, the 10 MB Git-file rule and limits of the evidence claims.


## A_RG2b bounded execution and scoped acceptance

The [A_RG2b review](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-ARG2bRuntimeReview.md)
binds sixteen layouts and both histories. Shared surfaces expose four-level
C/scaled-log-W chains, complete query/tail errors, signed Read-Back/flat,
current-L2 and C/Y-state bridges, exact W lineage and composed temporal-writer
controls. The next read propagates intended C/W errors. No geometry history or
carrier coordinate is added. The signed completion and C1 claim limits remain.

Use `run.py tranche8-query verify-retained --family A_RG2b` for source,
operand, schedule and bound checks; add `--recheck-numerics` for independent
interval recomputation. Neither reruns native trajectories. The separately
linked numerical report disables native numerical producers throughout its
checks. The user accepted this bounded result on 2026-10-06; the separate
[decision](../../../../../phase-9-grcv4/tranche-8/P9-8.4b-ARG2bRuntimeReview.md#scoped-user-acceptance)
supplies acceptance while raw execution/recheck flags stay unchanged. It
credits the final 32 cells and closes bounded P9-8.4b, without closing later
8.4 work. Completed evidence uses compact poststates and
lossless XZ storage; interrupted runs are not repository artifacts.
