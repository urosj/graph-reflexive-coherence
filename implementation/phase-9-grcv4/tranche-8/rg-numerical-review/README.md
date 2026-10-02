# P9-8.0 actual RG numerical implementation review package

2026-10-02. **Includes the user-requested own implementation review and four
locally verified corrections; not an externally independent audit.** See the
[findings and pressure results](./SelfReview.md). The baseline is the actual
represented evaluator at repository commit
`42976ed60da397a95de95b0361454e39ffbf9643`, including its exact current dependencies
and the event companion that consumes it. Corrected working-tree source and the
pressure owner are explicitly marked in the manifest; the baseline numerical
owner is also exported under `rg-numerical-review/baseline/`. The prior [event audit](../P9-8.0-RGEventIndependentReview.md)
passed against a reconstructed numerical dependency because the original was
missing. This package removes that missing-source obstacle without extending
the earlier verdict. Mathematical feasibility, local execution, independent
implementation review and aggregate user acceptance remain distinct.

The selected-case compatibility reconciliation is accepted at that commit.
The own review has executed the actual implementation and fixed its findings.
The user explicitly accepts this own review, its corrections and the bounded
actual-implementation review disposition through the 2026-10-02 acceptance/commit
instruction. Aggregate all-ten review and acceptance remain open. No production, native registration or new
scientific authority is supplied by exporting these files.

## Contents and provenance

[export.py](./export.py) exports the pinned commit's research verification
sources, tranche-8 records/notes, exact combinatorial fixture, profile registry,
relevant specifications and the tracked `src/pygrc` package. The complete package
is included because the exact helper import chain reaches the package facades;
replacing those imports with reconstructed stubs would recreate the review gap.
The baseline snapshot replay used unchanged source. The later own-review runs
use the explicit numerical-owner correction; no missing dependency is replaced
by a reconstruction.

The export overlays the corrected numerical owner, new pressure owner, review
briefs, correction patch, exporter, environment/requirements and local results. [manifest.json](./manifest.json) records every payload
file's SHA256, size and whether it comes from the source commit, a local code
correction or local review evidence. The manifest excludes its own checksum. Its presence proves neither
external authenticity nor acceptance; compare source entries with the stated
commit in a trusted checkout. The deterministic archive can be regenerated;
the generated ZIP stays under ignored `build/`, while its sources, manifest and
evidence live in this repository directory. Review-document links outside the
included subset require the full repository at the stated commit.

| Actual file | Review role |
| --- | --- |
| [test_p980_rg2b_numerical.py](../../verification/test_p980_rg2b_numerical.py) | Represented increment, finite-chain producer, complete residual certificate, section and physical ordinary consumer; four original test methods |
| [test_p980_rg2b_completion.py](../../verification/test_p980_rg2b_completion.py) | Global constants, exact rational slope/section bounds, frozen auxiliary completion and literal signed increment |
| [test_p980_os_effect_witness.py](../../verification/test_p980_os_effect_witness.py) | Interval A/C equations, full-coordinate errors, whole-writer references and effect criterion |
| [test_p980_os_numerical_feasibility.py](../../verification/test_p980_os_numerical_feasibility.py) | Represented row/current/writer stages and declared scalar product arithmetic |
| [test_p980_fixed_row_bounds.py](../../verification/test_p980_fixed_row_bounds.py) | Fixed-row parameters, graph models and rational bounds |
| [test_p980_revised_realization_bounds.py](../../verification/test_p980_revised_realization_bounds.py) | Physical-domain envelopes reused by the RG completion |
| [test_p980_boundary_continuation.py](../../verification/test_p980_boundary_continuation.py) and [test_p980_feasibility.py](../../verification/test_p980_feasibility.py) | Frozen layout selection, exact reference preimage and Laplacian; original native-domain imports remain present |
| [test_p980_rg_event_companion.py](../../verification/test_p980_rg_event_companion.py) | Independent event-consumer entry ownership, recertification of returned chains and read/write outputs, seven original test methods |
| [test_p980_event_companion.py](../../verification/test_p980_event_companion.py) and [test_p980_a_event_companion.py](../../verification/test_p980_a_event_companion.py) | Shared consumed-model/transfer guards and the corrected A counterfactual writer boundary |

The [RG numerical construction](../P9-8.0-RG2bNumericalFeasibility.md),
[completion](../P9-8.0-RG2bCompletion.md), [event construction](../P9-8.0-RGEventConstruction.md)
and [selected-case reconciliation](../P9-8.0-SelectedCaseCompatibility.md)
state the mathematical claims and their scope. The common/A/RG JSON records
remain in their original relative locations; fixture selection stays
`G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-3`.

## Reproduce and inspect

From the full repository, regenerate the review ZIP:

```bash
python3 implementation/phase-9-grcv4/tranche-8/rg-numerical-review/export.py
```

Extract `build/P9-8.0-RG-NumericalReview.zip` into an empty directory and use that
extracted directory as the working directory. Preserve the tree: helpers locate
fixtures and inputs relative to `__file__`. The local replay used Python 3.12.3
and the versions in [requirements.txt](./requirements.txt). For a fresh review
environment, install those requirements in an isolated virtual environment:

```bash
python3 -m venv .review-venv
.review-venv/bin/python -m pip install -r implementation/phase-9-grcv4/tranche-8/rg-numerical-review/requirements.txt
```

No editable install of another repository checkout is needed. The entry script
resolves sibling research modules; its original feasibility helper adds the
extracted `src` directory. Verify the archive payload hashes before executing:

```bash
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path.cwd()
record = root / 'implementation/phase-9-grcv4/tranche-8/rg-numerical-review/manifest.json'
manifest = json.loads(record.read_text())
for name, expected in manifest['files'].items():
    data = (root / name).read_bytes()
    assert len(data) == expected['bytes'], name
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
print('All payload hashes match the supplied manifest.')
PY
```

Run the actual original owners unchanged, with separate output files so supplied
historical results are not overwritten:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .review-venv/bin/python implementation/phase-9-grcv4/verification/test_p980_rg2b_numerical.py --report > numerical-local.json 2> numerical-local.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .review-venv/bin/python implementation/phase-9-grcv4/verification/test_p980_rg_event_companion.py --report > event-local.json 2> event-local.txt
```

Report both process exits and unittest summaries. Decimal report fields are
presentation values; the actual checks use interval endpoints and rational
bounds. Library/platform differences can change display maxima without failing
a gate; the prior reconstructed C-current final-read discrepancy is retained
in the event construction note. Do not replace a missing dependency with an
independent reconstruction and call the result a replay of this implementation.

## Specific implementation questions to resolve

These are the existing independent-review obligation's concrete subjects, not
new acceptance gates. A local source map is supplied to make review finite:

1. `RepresentedAuxiliary.increment` applies the frozen resource `[-1,5]` and
   scaled-history `[-1,1]` clamps to arguments at every backward depth. Check
   A's final-C/incoming-W/selected-J writer and C's noncommuting response order
   against the literal interval equations, including exterior queries.
2. `solve_chain` uses A depth 4 / C depth 6, 18 sweeps and terminal identity.
   `certify_chain` validates full state and H dimensions, finiteness, symmetry,
   star support, geometry radius, terminal identity and graph hypotheses. It
   independently clips and recomputes **every** residual coordinate. Determine
   whether any accepted return can evade the stated certificate, without
   assuming sweep convergence.
3. `chain_error_bounds` must preserve the finite-chain amplification and positive
   coupling denominator. Inspect the output tail `q^N V`, first-inverse tail
   `q^(N-1) V`, and the refined first-image enclosure. Publication error in H
   remains separately bounded. An interval defect containing zero is numerical
   consistency, not proof of the invariant-section equation.
4. The actual field definition is `input_error = SECTION_LIP * query_error`,
   where `query_error = full_error(chain.x[0], exact_query)`. Verify both its
   section contribution and division by `SECTION_LIP` before inverse sensitivity.
   It is not a raw state-input error despite the short field name.
5. The own review corrected point/intended admission and producer ownership.
   Distinguish intended-exact C/W enclosures from represented operands and their
   evaluation errors, including A log conversion and next-history consumers.
   The corrected `section`/`ordinary` boundary now owns producer work arrays
   and certifies complete point read/write outputs; inspect its explicit patch.
6. The event consumer constructs its saved point query before calling `ordinary`
   with private arrays, independently recertifies the chain, enforces the declared
   depth and published H/chain relation, and reconstructs read/write references.
   Its checks do not make the original producer's self-reported `exact_*` fields
   independent authority or automatically harden every caller of that producer.
7. Execute the original four methods: both-role continuation, defining effects
   and history consumers, completion/certificate mutations, and actual-consumer
   substitutions/equilibria. Execute the companion's seven methods on actual
   dependencies. Check the named-stage effect restrictions, source/reset schedule,
   graph binding and legal zero-current equilibria; do not impose a universal
   nonzero-effect requirement.

The original certificate API accepts depths 1–8 and derives the corresponding
bound; nominal section calls select A4/C6, and the event consumer additionally
requires those declared depths. These different interfaces should be reviewed
as written, rather than treating a configurable auxiliary certificate as a
native profile or receipt. The actual numerical owner also does not claim a
uniform floating-point theorem or a trajectory-error enclosure.

## Local execution evidence and disposition

[environment.json](./environment.json) records the local package versions,
thread settings and relative import origins. Both test classes were set up
from a source-snapshot extraction, and every loaded `test_p980_*` and `pygrc`
module was verified to lie within that extraction: 156 repository modules.
The environment reused installed external dependencies; no fresh dependency
installation or external reviewer authentication is claimed.

The actual owner reports are [numerical-report.json](./numerical-report.json)
and [event-report.json](./event-report.json), with unchanged unittest summaries
in [numerical-run.txt](./numerical-run.txt) and [event-run.txt](./event-run.txt).
The numerical owner passes four methods (50 read stages, 44 named effects);
the event companion passes seven methods (four candidate/role paths, forty
target beats and 26 named effects). These baseline runs test the portability of the
exported source/dependency tree. They
are local evidence, not independent audit results. The subsequent [own review](./SelfReview.md) supplies actual-source findings,
corrections and ten pressure methods; corrected numerical and event runs pass
four and seven methods respectively, with all nominal report fields unchanged.
Those corrected results have separate filenames. Any further review must state
its authorship, source version and scope. The user has accepted the local review
and corrections; the all-ten aggregate decision remains separate.

Run the added pressure campaign on the corrected export:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .review-venv/bin/python implementation/phase-9-grcv4/verification/test_p980_rg_implementation_review.py --report > pressure-local.json 2> pressure-local.txt
```

To reproduce the original findings, work in a separate copy of the export and
replace only the numerical owner with its exported `baseline/` copy. Run the
five named methods corresponding to RG-NR1–4 in `SelfReview.md`; the expanded
owner adds further cases and expects the corrected interface. Do not overwrite
the retained baseline or corrected result files when rerunning either version.
