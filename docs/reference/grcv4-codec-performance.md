# V4 codec performance investigation

The supplied two-step Candidate A CI profile spent 85.3 of 95.8 seconds in
`load_contract_schema`. Each of 736 payload validations reread the pinned
assets, parsed the contract schema, walked every JSON field, and created a
validator class. The schema processing dominated the numerical step.

## Change

`grc_v4_codec.py` now caches parsed base and initializer schemas by their
verified bytes and caches validators by schema bytes and local definition.
The caches have fixed size limits. Internal validation reads private schemas;
public schema loaders return deep copies. Selecting a definition copies only
the schema root, keeping the shared definitions unchanged.

Every lookup still reads and checks the packaged assets. Changed or missing
assets reject even after a successful lookup. This deliberately retains the
existing integrity contract rather than treating file metadata as authority.
Caller payloads are copied and checked for the I-JSON domain every time.
The first optimization did not memoize validation results, scientific states,
or numerical solver outputs; the follow-up below adds bounded reuse of
successful closed-schema validation by content.

## Reproduction and initial measurements

Install the declared V4 extra, then run from the repository root:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_ci.py
```

The script uses the supplied fixture (`A`, `dt=0.5`, geometry gain and radius
`0.25`, candidate `eta=0.025`). It times the first step normally and profiles
the second. Fixture construction and output hashing are outside step timing.
Both steps print the SHA-256 of the canonical next-input payload.

One paired run of original and optimized source copies using Python 3.12 and
the declared V4 dependency versions produced:

| Measurement | Original | Cached |
| --- | ---: | ---: |
| First step, no profiler | 7.155 s | 1.425 s |
| Second step, with cProfile | 18.504 s | 2.537 s |
| Second-step function calls | 21,754,149 | 2,070,556 |
| Schema loading, cumulative | 14.981 s | 0.663 s |

The profiled second step was about 7.3 times faster. These are single-run
measurements, not statistical benchmarks; machine load and profiling overhead
influence the absolute times. Compare matching rows across revisions, rather
than comparing a profiled step with an ordinary step.

The canonical next-input hashes matched exactly for both steps:

- Step 1: `a4bd4195921329ddd7937b5588bcc8a8bfbee6946457ecf9d36e919e7f2f9f84`
- Step 2: `e7cdc5e08732dd9b5ba83b34ebf6f1d01b949a1bfa9a6a205f447d3cd051ca90`

## Follow-up: remaining opportunities addressed

The next optimization shares reset, scientific-state, and lifecycle preimages
within each geometry-stage projection and reconstruction. CI trials reuse their
already computed read-back for structural assembly, avoiding a second matrix
solve and stage serialization. The source helper used by RG2b retains its
existing interface and zero-gain behavior. No numerical root or scientific-state
record is memoized.

Closed-schema validation now reuses successful checks by the verified schema
bytes, definition name, and canonical payload bytes. Input dictionaries are
copied on every call; cached success never returns a previous caller's values.
Equivalent integer/float JSON numbers retain their original Python types in the
returned copy. Changed fields, booleans, unknown definitions, and invalid wire
numbers still reject. Errors are not cached. The memo is protected by a lock,
holds at most 128 entries, and bypasses records larger than 8 KiB.

Asset digests and the pinned asset index are reused by exact byte content.
Files are still read on every lookup: changing contents, even without changing
size or timestamp, cannot reuse an old digest. Additive event schemas, their
offline registry, and definition validators are now cached too; public schema
loaders remain detached, and warm lookups still check all nine joint-package
assets and the required optional dependencies.

A fresh comparison against the first optimization measured:

| Measurement | First optimization | Follow-up |
| --- | ---: | ---: |
| First CI step, no profiler | 1.283 s | 0.554 s |
| Second CI step, with cProfile | 2.334 s | 1.128 s |
| Second-step function calls | 2,055,827 | 1,068,774 |
| 200 warm event-schema validations | 2.209 s | 0.219 s |

Both CI next-input hashes and the event-validation output hash matched.
These remain single-run measurements, with the same limitations as above.
The event measurement covers closed wire validation, not graph-map admission
or a complete topology operation. Reproduce it with:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_ci.py --event-validation 200
```

Asset I/O and serialization of new payload contents remain. Removing fresh
file reads would weaken the existing per-lookup integrity contract. Larger
records deliberately bypass validation memoization to limit retained memory.

## Initial validation

The initial focused codec, CI, profile, and request asset-failure run passed
all 91 tests. This includes the new cache regression tests and the final
integrity adjustments. The profiling script reproduced both original next-input hashes.
Ruff passes for the changed runtime module and the new script; the existing
lint findings in the test files and existing codec mypy findings remain.

An expanded 889-test V4 run was interrupted after more than 300 tests. It found
a capability-list assertion that also fails against the original source
(`PublicFacadeTests.test_construction_protocols_and_exact_discovery`). It also
exercised a test that mocked the old public schema-copy boundary; that test now
faults the asset-resource read instead and passes independently. This is not a
claim of a fully passing V4 suite.

The original codec asset-fault test selected every packaged JSON file, including
additive-release assets outside the base loader's pinned index. Its ten failures
were reproduced on the original source. It now faults only the base index and
its members; the new warm-cache tests separately exercise initializer assets.

## Follow-up validation

All 187 affected tests passed, covering codec and event caches, CI, geometry-stage
reconstruction, profile resolution, initializer crossings, event runtime/audits,
and RG2b. New controls check bounded eviction, oversized-record bypass,
integer/float type preservation, boolean rejection, concurrent callers, detached
outputs, registry reuse, warm optional-dependency failures, and all nine joint
package assets under same-size corruption and deletion.

```bash
PYTHONPATH=src:.:tests .venv/bin/python -m unittest \
  tests.models.test_grc_v4_codec.CodecTests \
  tests.models.test_grc_v4_event_codec \
  tests.models.test_grc_v4_ci \
  tests.models.test_grc_v4_geometry.StageCacheTests \
  tests.models.test_grc_v4_profile \
  tests.models.test_grc_v4_initializer \
  tests.models.test_grc_v4_events \
  tests.models.test_grc_v4_event_audit \
  tests.models.test_grc_v4_rg2b
```

Ruff passes for both codec modules, the new event-cache tests, and the profiling
script. Existing lint findings in CI/geometry/older tests and existing mypy
findings remain; comparison with the saved first-optimization source found no
new type diagnostics. The complete repository test suite was not rerun.

## Further optimization without relaxing validation

Identity construction now retains the canonical bytes produced by the same
invocation's closed-schema validation. Base and initializer identities hash
those bytes directly, avoiding a second RFC 8785 serialization. Every call
still detaches and checks the caller's value, verifies installed assets,
selects the pinned definition, and compares any supplied identity. This also
works for records too large for the validation memo; no cached caller object
or previous identity is returned. Additive event identity paths retain their
existing serialization route.

The exact exponential enclosure helper shared by CI, PC, and CI+PC now has a
128-entry LRU cache keyed by its immutable scalar argument and type. Its
Taylor expansion, outward rounding, reciprocal endpoints, and finite argument
budget are unchanged. Only exact rational interval endpoints are reused;
root selection, contraction certificates, residual evaluation, writer
admission, and publication still run for each state. Failed computations are
not cached. These arithmetic results do not depend on mutable decimal context,
profile identity, geometry, or packaged schema contents.

The profiling script also supports full public steps and snapshot restoration
for all ten accepted candidate/realization families:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_ci.py --families
```

Fixture creation and snapshot projection/hashing are outside timing. Each
restored snapshot must have identical canonical bytes. This broader benchmark
uses the accepted generic lifecycle fixtures, rather than claiming the original
Candidate A CI fixture represents every family.

A final paired run without concurrent tests measured:

| Measurement | Before this change | After |
| --- | ---: | ---: |
| Original fixture first CI step, no profiler | 0.537 s | 0.421 s |
| Original fixture second CI step, with cProfile | 1.052 s | 0.860 s |
| Second-step function calls | 1,058,284 | 975,145 |
| Second-step RFC 8785 encodings | 1,313 | 1,037 |
| Sum of ten family public steps | 8.631 s | 7.338 s |
| Sum of ten family restorations | 4.259 s | 3.196 s |

The profiled original CI fixture improved by about 18%. The all-family totals
are sums of one execution per family, not a representative workload average.
Some small family timings varied upward; these single-run measurements do not
establish a speedup for every family. The larger Candidate A RG2b improvement
also benefits from the shared exact enclosure helper.

| Family | Public step before / after | Restore before / after |
| --- | ---: | ---: |
| A_OS | 0.593 / 0.554 s | 0.160 / 0.145 s |
| C_OS | 0.447 / 0.431 s | 0.170 / 0.158 s |
| A_CI | 0.583 / 0.510 s | 0.269 / 0.185 s |
| C_CI | 0.500 / 0.547 s | 0.207 / 0.222 s |
| A_RG2b | 3.521 / 2.367 s | 2.168 / 1.393 s |
| C_RG2b | 0.998 / 1.000 s | 0.468 / 0.362 s |
| A_PC | 0.431 / 0.427 s | 0.143 / 0.148 s |
| C_PC | 0.420 / 0.415 s | 0.150 / 0.150 s |
| A_CI_PC | 0.604 / 0.567 s | 0.282 / 0.202 s |
| C_CI_PC | 0.534 / 0.519 s | 0.241 / 0.231 s |

Both original CI hashes and all ten full snapshot hashes matched exactly,
including receipt and commit content. All 235 selected tests passed in
322.079 seconds:

```bash
PYTHONPATH=src:.:tests .venv/bin/python -m unittest \
  tests.models.test_grc_v4_codec.CodecTests \
  tests.models.test_grc_v4_event_codec \
  tests.models.test_grc_v4_ci \
  tests.models.test_grc_v4_pc \
  tests.models.test_grc_v4_cipc \
  tests.models.test_grc_v4_profile \
  tests.models.test_grc_v4_initializer \
  tests.models.test_grc_v4_generic_lifecycle
```

New regressions check one encoding per identity invocation for cold/warm and
oversized payloads, unchanged published identities, invalid input and supplied
identity rejection, context-independent exact enclosures, adjacent scalar
arguments, cache eviction, and repeated rejection outside the finite budget.
Existing independent Decimal tests continue to check the enclosure endpoints.
Ruff passes for the codec and benchmark; comparison with the saved baseline
found no new mypy diagnostics. Existing lint/type findings in other affected
files remain. The full repository suite was not run.

The remaining measured work includes fresh asset reads, detached JSON copies,
profile and geometry reconstruction, and numerical source calculations. Sharing
an immutable validated representation across more internal boundaries may help
further, but it requires preserving canonical numeric normalization and every
ownership/admission check at those boundaries. The current changes keep those
checks in place.

## Reusing unchanged declarations during a run

The next investigation focused on work that repeats after simulation starts.
Stage capture reconstructs the same complete profile from canonical bytes
several times per step. Each reconstruction previously repeated decoding,
parameter record construction, schema checks, parameter-content hashes, and
profile consistency checks even when every profile byte was unchanged.

`GRCV4Profile.from_canonical_bytes` now reuses a private fully checked profile
template by exact canonical UTF-8 bytes. It retains at most 16 declarations
and bypasses inputs larger than 64 KiB. Every caller receives an independent
deep copy, including nested records and frozen maps. Private templates are
never returned to a stage or caller. Changed bytes undergo the full original
reconstruction; failed inputs are not memoized. Canonical number restoration,
closed schemas, nested content hashes, and supplied profile IDs retain their
original checks and semantics.

Each lookup still reads and verifies installed base assets and checks required
optional dependencies before returning. Reuse cannot hide deleted or corrupted
assets. This is reuse of a checked declaration, not a scientific-state admission
or a solver certificate: graph/reference binding, evolving geometry, current
and reset admission, numerical roots, charge, history, and publication continue
through their existing owners.

The benchmark now accepts a longer CI sequence and profiles the final step,
so unchanged setup work can be measured after multiple scientific updates:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_ci.py --steps 5
```

All steps print exact output hashes; only the last step uses cProfile. The
original two-step command and the all-family benchmark remain available.

A paired run without concurrent tests measured:

| Measurement | Before profile reuse | After |
| --- | ---: | ---: |
| Two-step fixture, first step without profiler | 0.451 s | 0.349 s |
| Two-step fixture, profiled second step | 0.863 s | 0.659 s |
| Profiled second-step calls | 964,645 | 766,050 |
| Second-step closed-schema validation invocations | 525 | 315 |
| Five-step fixture, third step without profiler | 0.352 s | 0.261 s |
| Five-step fixture, fourth step without profiler | 0.344 s | 0.264 s |
| Five-step fixture, profiled fifth step | 0.953 s | 0.684 s |
| Profiled fifth-step calls | 875,264 | 675,949 |

The profiled fifth step used about 23% fewer calls and 28% less wall time.
These are single-run measurements, not statistical results. Counts include
recursive encoding, defensive copying, Python standard-library and dependency
calls, not just explicit validation calls. Baseline and changed code run from
separate source copies, so path-dependent library call counts can differ too.
All two-step and five-step output hashes matched exactly.

| Family | Public step before / after | Restore before / after |
| --- | ---: | ---: |
| A_OS | 0.595 / 0.422 s | 0.168 / 0.094 s |
| C_OS | 0.485 / 0.303 s | 0.206 / 0.088 s |
| A_CI | 0.591 / 0.408 s | 0.224 / 0.131 s |
| C_CI | 0.546 / 0.380 s | 0.221 / 0.140 s |
| A_RG2b | 2.418 / 2.253 s | 1.429 / 1.377 s |
| C_RG2b | 0.864 / 0.757 s | 0.398 / 0.340 s |
| A_PC | 0.433 / 0.324 s | 0.141 / 0.088 s |
| C_PC | 0.420 / 0.333 s | 0.147 / 0.080 s |
| A_CI_PC | 0.559 / 0.451 s | 0.212 / 0.146 s |
| C_CI_PC | 0.553 / 0.417 s | 0.225 / 0.164 s |

All ten full snapshot hashes matched, covering both candidates and all five
realizations. New controls cover independent nested copies (including deliberate
unsupported reinitialization), changed/forged inputs, exact canonical encoding,
cache bounds and oversized bypass, warm asset corruption/deletion, and missing
optional dependencies. Existing canonical numeric round-trip controls remain.

The selected run covered 279 tests. All functional solver, lifecycle,
stage/cache, resource boundary, and reconstruction checks passed, with one
opt-in packaging test skipped. It initially reported seven evidence-capture
errors because the capture runner requires new sources to be represented in
its Git reconstruction preimage; those errors reproduced before this change.
All seven capture tests then passed using a temporary Git index containing an
intent-to-add entry for the existing new event-codec test. This supplies a valid
Git diff reconstruction without changing the workspace's index or modifying
the capture tests. Thus 278 selected tests passed and one was skipped across
the completed verification. The complete repository suite was not run.

```bash
PYTHONPATH=src:.:tests .venv/bin/python -m unittest \
  tests.models.test_grc_v4_codec.CodecTests \
  tests.models.test_grc_v4_event_codec \
  tests.models.test_grc_v4_profile \
  tests.models.test_grc_v4_ci \
  tests.models.test_grc_v4_pc \
  tests.models.test_grc_v4_cipc \
  tests.models.test_grc_v4_initializer \
  tests.models.test_grc_v4_generic_lifecycle \
  tests.models.test_grc_v4_geometry.StageCacheTests \
  tests.models.test_grc_v4_geometry.CaptureIntegrityTests \
  tests.models.test_grc_v4_step.ResourceBoundaryTests \
  tests.models.test_grc_v4_step.ResourceReconstructionTests
```

Ruff passes for the benchmark. Existing profile module/test lint findings and
profile type diagnostics remain; no new diagnostics were found in the cache
implementation or new regression bodies. Patch whitespace checks passed.

Further reductions would target repeated stage-to-payload-to-stage ownership
copies and descriptor serialization inside candidate iterations. These still
require checked ownership boundaries and preservation of canonical numeric
semantics; simply trusting a caller's frozen dataclass or skipping evolving
state admission would not preserve strictness.

## Full V4 verification after the optimization commit

The optimization changes were committed as `a7a7d0a`. A complete V4 unit-test
selection then ran 903 tests in 1137.998 seconds:

```bash
PYTHONPATH=src:.:tests .venv/bin/python -m unittest discover -v \
  -s tests/models -t . -p 'test_grc_v4*.py'
```

It passed 893 tests and skipped four opt-in packaging tests. Six test cases
produced three assertion failures and seven error reports. The failures were
outdated test assumptions and fault hooks:

- The capability assertion omitted explicit history reconstruction and pure
  representation transport already provided by the public API.
- The import inspector classified `from . import grc_v4_codec` by its parent
  package rather than the qualified imported module. It now recognizes owned
  imports and still detects legacy imports hidden behind misleading aliases.
- Three administrative/readmission controls patched the removed lifecycle
  `_os_inputs` symbol. They now inject errors through `_readmit_state` and corrupt
  the target returned by `_fresh_geometry`, preserving the source observation
  and the existing atomicity/identity rejection assertions.
- The registry control assumed the generalized lifecycle owner still accepted
  only C_OS targets. It now checks the bounded helper's original C_OS rejection
  separately, and verifies explicit A/C declarations in the generalized owner.
  Duplicate references, invalid weights, and unauthorized graph migration still
  reject in the existing controls.

All six failing cases passed on rerun, together with one new import-spelling
and alias regression (seven tests). All seven evidence-capture integrity tests
also passed with the corrected sources and normal Git index. No runtime or
scientific validation checks were weakened or changed in this correction.
Patch whitespace checks passed; lint comparison found no new diagnostics
(98 existing findings before, 97 after in the affected test files).
The 903-test selection was not repeated after these test-only corrections.


## Remaining call volume and ordinary runtime costs

A fresh measurement of the same Candidate A CI fixture's fifth step recorded
668,014 calls. Seven ordinary executions of that identical step had a median
of 0.215 seconds; cProfile took 0.555 seconds, about 2.6 times longer. Fixture
construction, the four preceding steps, and output hashing were excluded.
These are repeated executions of the same input, not successive evolving steps.
The fifth-step output hash still matched:

```text
4198a000a4b6461db99ab9e3e477c4b4b75bb9b204f9774afb49c2d710f03d35
```

Call count alone is a poor optimization target. `isinstance`, byte-buffer
`write`, and string `encode` accounted for 271,895 calls (41% of all calls),
but only about 14% of the profiler's exclusive time. Conversely, 289 contract
asset lookups performed 1,156 file opens/reads and consumed substantial time.

A separate timing harness wrapped selected outer functions rather than every
Python call. Nested measured time was subtracted from the enclosing category,
so the following costs do not overlap. Five ordinary repetitions had a median
of 0.221 seconds; five instrumented repetitions had a median of 0.227 seconds.
Shares use the mean instrumented elapsed time, approximately 0.228 seconds;
they are approximate attribution, not predicted speedups.

| Work | Mean exclusive milliseconds | Share |
| --- | ---: | ---: |
| Fresh asset/schema loading and verification | 83.0 | 36% |
| Canonical JSON encoding | 55.6 | 24% |
| JSON domain checks/copying and independent deep copies | 24.9 | 11% |
| Certified solves, residual arithmetic, and other read-back work | 26.1 | 11% |
| Schema validation/memo lookup, excluding encoding | 4.9 | 2% |
| Remaining work and instrumentation overhead | 33.6 | 15% |

The harness counted 723 canonical encodings, 4,326 JSON domain-copy calls,
279 schema validation/memo calls, and 27 certified read-back solves. Thus more
schema-validator caching alone is unlikely to deliver a large improvement.

An additional lightweight property timer found 19 newly constructed Candidate A
points and 27 stage-identity constructions: eight constructions repeated on the
same point during CI trial read-back. Across five repetitions, first identity
construction cost about 51 ms in total and repeated construction about 20 ms.
These inclusive identity costs overlap the categories above and must not be
added to them. The repeated work is roughly 9% of ordinary step time; this is
an upper bound on a potential saving, not an implemented speedup.

The next opportunities, in order of concreteness, are:

1. Reuse the stage identity produced during fresh point construction within
   the internal trial read-back path. The trial current can differ from the
   point's admitted current, so flux calculation, the certified solve, and
   residual checks must still run. Public read-back must retain fresh checks;
   a persistent cache keyed only by a caller's frozen dataclass is insufficient.
2. Reduce repeated complete stage projections and identity-preimage construction
   within checked ownership boundaries. Five stage reconstructions and 36 stage
   projections remain in this fixture. An internal checked capture could reuse
   static verified material while still admitting changed coordinates and
   returning independently owned records. Preserve the exact existing hash
   preimages and canonical numeric route.
3. Reduce resource/path setup overhead inside asset verification and duplicate
   verification requests generated by those repeated projections. Any such
   change must retain fresh file reads at every existing lookup boundary and
   rejection of missing or modified assets. A run-wide successful-verification
   cache would change the current integrity guarantee and is not a free
   optimization.

This attribution covers one A CI fixture. Shared codec and ownership paths are
used by the other realizations, but their cost proportions need separate
measurements. No runtime code or validation guarantees were changed in this
analysis. Temporary raw measurements were saved under
`/tmp/grcv4-cost-analysis/` during the investigation.


## Comparison across all five realizations and both candidates
The follow-up analysis measured all ten accepted generic lifecycle fixtures at
both the provisional numerical dispatch boundary and the public `step_v4_input`
boundary. Five ordinary repetitions and five instrumented repetitions used the
same initial input, with model construction, restoration and snapshot hashing
excluded. A separate cProfile execution recorded call counts. Every repetition,
including instrumented and profiled operations, matched its baseline output
hash. All public operations committed.

OS, CI, PC and CI+PC fixtures have two vertices and one edge. RG2b uses its
accepted graph fixture with four vertices and three edges. Durations, parameters
and convergence criteria also differ across realizations: this is attribution
within each fixture, not a claim about their relative algorithmic efficiency.
Raw timings, graph sizes, counts and output hashes are retained in
[`grcv4-realization-costs.json`](grcv4-realization-costs.json).

| Family | Numerical median, ms | Public median, ms | Numerical calls | Public calls |
| --- | ---: | ---: | ---: | ---: |
| A_OS | 127 | 263 | 405,791 | 836,976 |
| C_OS | 108 | 256 | 338,570 | 786,280 |
| A_CI | 180 | 353 | 578,894 | 1,000,679 |
| C_CI | 206 | 369 | 595,045 | 1,014,704 |
| A_PC | 133 | 292 | 338,400 | 767,032 |
| C_PC | 125 | 299 | 309,370 | 735,669 |
| A_CI+PC | 233 | 399 | 621,038 | 1,048,958 |
| C_CI+PC | 242 | 393 | 633,304 | 1,059,141 |
| A_RG2b | 2094 | 2292 | 2,438,969 | 2,897,203 |
| C_RG2b | 530 | 681 | 1,875,327 | 2,329,214 |

For OS, CI, PC and CI+PC, fresh contract asset/schema loading accounts for
roughly 32–40% of instrumented numerical time and canonical encoding for 21–27%.
Together they account for 48–55% at the public boundary. JSON domain copying
and independent deep copies contribute another 8–13%. These costs are shared
across A and C. Percentages are approximate: timing noise and wrapper overhead
produce differences between instrumented means and ordinary medians of up to
23% in this sample. Nested measured work is subtracted from outer exclusive
categories; inclusive identity observations must not be added to those totals.

### A shared public result-validation bottleneck

Schema validation/memo lookup excluding encoding contributes only about 2% to
these numerical steps, but 17–25% to their public steps. A schema-cache probe
found the reason in every family: the `step_result` record is validated three
times and its roughly 16.4–16.6 KB canonical content exceeds the existing 8 KB
memo limit. All other schema lookups in the warmed probe hit the content cache.
The three full `step_result` checks cost approximately 57–67 ms, excluding
encoding.

A temporary process-local experiment raised only the maximum cacheable payload
size to 32 KiB. Fresh result records then incurred one full schema check and
two exact-content hits in every family, at a total validation cost of about
20–24 ms. JSON domain checking, independent copying, fresh asset reads, schema
selection and downstream semantic/evidence checks remained in place. The
entry-count bound remained 128; the payload-byte ceiling would rise from
1 MiB to 4 MiB, excluding retained schema bytes and Python overhead.

Three matching evolving public steps per family also produced identical
snapshot hashes under both size limits. Their overall timings were noisy and
subject to shared-cache/order effects, so they do not establish a reliable
whole-step speedup. The repeat-check reduction is established by the cache
probe. Larger result records would still fall through to full validation.
This is a contained codec adjustment to investigate before redesigning result
construction or ownership boundaries.

### Repeated candidate stage identities

Both CI and CI+PC constructed 15 fresh points and evaluated their stage identity
21 times: six repeated evaluations, for both A and C. The repeats cost roughly
17–22 ms at the numerical boundary and 17–19 ms at the public boundary. OS and
PC showed no repeated point identity on the same object; graph RG2b showed only
one, costing approximately 3–4 ms. Therefore internal trial identity reuse is
an opportunity shared by A/C CI and CI+PC, rather than a broad remedy for every
realization. Trial-current solves and residual checks must remain fresh.

Stage reconstruction counts are also distinct: A/C OS performed seven/six,
whereas the other realizations performed five/four. Complete stage projections
ranged from 10–16 in OS/PC to 29–30 in CI/CI+PC and 34/21 in A/C graph RG2b.
These counts identify repeated work, but do not by themselves justify a new
ownership abstraction.

### RG2b has a separate arithmetic bottleneck

Graph A RG2b spent only about 8% of its numerical time in asset loading and
canonical encoding combined; graph C RG2b spent about 20%. Certified section
and interval arithmetic dominate the remaining work. The A cProfile trace
spent 1.41 of 3.21 profiler seconds inside `math.gcd`; graph-section logarithm
and exponential enclosures were substantial contributors. These profiler
figures are hotspot evidence, not ordinary wall-time estimates.

A targeted A RG2b probe observed 126 `_log_point` calls on only 29 distinct
exact rational operands, with approximately 0.46 seconds spent on repeated
logarithms. A temporary bounded 128-entry cache stored immutable `(lo, hi)`
endpoint pairs and constructed a fresh interval for each caller. With scalar
caches cleared before every step, three ordinary repetitions had a median of
1.645 seconds versus 2.103 seconds for the existing code, about a 22% reduction.
All next-input hashes matched. The cache had 29 misses and 97 hits within each
step, so the gain did not depend on replaying an old simulation input.

Increasing the exponential cache from 128 to 1,024 entries alone gave no
improvement in this experiment: both sizes had 295 misses and 142 hits within
one step. Combining it with logarithm caching did not improve on the latter.
The logarithm opportunity is specific to A's retained-history equations in
RG2b; C's profile calls for a separate assessment of its matrix/projector and
interval work. No enclosure precision or error-admission threshold was altered
in these experiments.

The measurements support evaluating three contained changes first: bounded
memoization of larger result records, exact logarithm endpoint memoization for
A RG2b, and scoped trial-identity reuse for A/C CI and CI+PC. A broad stage
ownership redesign remains a separate option, without evidence here that it
is necessary. These fixture measurements are not graph-size scaling tests or
full correctness validation of the temporary prototypes. No production runtime
code was changed by this analysis.

The numerical/public attribution can be repeated with the standalone harness:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_families.py \
  --repetitions 5 --output /tmp/grcv4-family-costs
```

It saves per-family JSON and cProfile artifacts and restores every temporary
instrumentation patch after the measured operation. Raw experimental helpers
and profiles from this session also reside under `/tmp/grcv4-cost-analysis/`.

The saved harness completed a one-repetition check of all twenty boundaries;
every output hash matched the five-repetition investigation. Ruff and patch
whitespace checks passed. No scientific unit-test rerun was required for these
benchmark/report additions; the experimental runtime alternatives remain
unimplemented and require their own regression verification before adoption.


## Initial contained changes and comparisons
This section records the initial implementation. The 64 KiB cache policy was
superseded after longer-history measurements; see the correction below.

The three optimizations were implemented in their existing owners, without new
candidate/realization switches or a stage-ownership framework:

- The codec retains successful records up to 64 KiB, still capped at 128
  entries. This bounds retained payload bytes at 8 MiB, excluding existing
  schema/key overhead. Exact verified schema content, definition name and
  canonical payload bytes remain the cache key; returned data is detached and
  asset/dependency guards still run. Errors and oversized records are not cached.
- RG2b memoizes 128 exact logarithm operands with immutable endpoint pairs.
  The cached values precede the original final interval rounding; every caller
  receives a fresh interval and performs that rounding once. This preserves
  the original enclosure expression exactly rather than relying on repeated
  interval normalization being idempotent.
- A/C read-back expose a common private helper accepting an established stage
  identity. Public `read_back()` still computes a fresh identity. CI constructs
  a fresh point and immediately consumes its construction identity through the
  helper, retaining the trial flux, certified solve and residual checks. CI+PC
  uses that same path. No evolving state admission is cached.

The initial 32 KiB experiment was insufficient for even a short evolving run:
result records grew from roughly 16 KiB to 57 KiB across six accepted steps.
The initial 64 KiB bound covered that measured trace. A fresh six-step A_OS probe
observed one schema miss and two hits per result at every step. Longer or larger
records eventually exceed the bound and receive full validation; receipt-history
processing itself remains in place.

### Fresh evolving public runs

The baseline was recorded before editing production code. Each family then ran
the same five ordinary evolving steps followed by one fresh profiled step.
The table compares total unprofiled time for the five-step trace and call volume
for the sixth step. Model creation, intermediate snapshot hashing and profiler
time are excluded from the ordinary trace timings. All 60 paired snapshot hashes
matched. These are local measurements, not confidence intervals or guarantees
for other graphs and histories.

| Family | Five-step time, before → after, s | Speedup | Sixth-step calls, before → after | Fewer calls |
| --- | ---: | ---: | ---: | ---: |
| A_OS | 2.085 → 1.984 | 1.05× | 1,499,999 → 1,372,575 | 8.5% |
| C_OS | 1.969 → 1.820 | 1.08× | 1,444,267 → 1,316,766 | 8.8% |
| A_CI | 2.505 → 2.238 | 1.12× | 1,670,995 → 1,489,228 | 10.9% |
| C_CI | 2.409 → 2.152 | 1.12× | 1,679,201 → 1,500,498 | 10.6% |
| A_PC | 2.052 → 1.628 | 1.26× | 1,424,084 → 1,296,724 | 8.9% |
| C_PC | 2.008 → 1.601 | 1.25× | 1,390,374 → 1,262,941 | 9.2% |
| A_CI+PC | 2.814 → 2.123 | 1.33× | 1,721,343 → 1,537,704 | 10.7% |
| C_CI+PC | 2.582 → 1.990 | 1.30× | 1,726,766 → 1,546,191 | 10.5% |
| A_RG2b | 13.176 → 9.409 | 1.40× | 3,592,980 → 3,175,755 | 11.6% |
| C_RG2b | 4.226 → 4.194 | 1.01× | 3,007,080 → 2,877,787 | 4.3% |

C RG2b's total trace time is effectively unchanged within timing variation,
despite its reduced public call volume. Its numerical matrix/projector work
was not optimized. The smaller OS improvements should also be interpreted
with local timing variation in mind.

### Numerical work and the original CI example

The separate identical-input benchmark matched all twenty numerical/public
output hashes. CI/CI+PC's six duplicate candidate identities disappeared for
both A and C. Their numerical call reductions were approximately 8–9%; A RG2b
removed about 13% of numerical calls. Numerical call volume stayed essentially
unchanged for OS, PC and C RG2b, as expected; timing differences there cannot
be attributed to an altered numerical algorithm. Replaying identical public
results gives larger gains than fresh evolving runs because all three result
schema checks can hit an already populated cache, so those timings are retained
in the raw artifact but are not the primary speedup claim.

For the original fifth-step A CI fixture, using the same four preceding steps
and seven ordinary repetitions of the fifth input:

- Calls: 668,014 → 599,538, 10.3% fewer.
- Ordinary median: 215.4 → 196.3 ms, 1.10× speedup.
- Next-input hash: unchanged. Profiler wall time is not used as ordinary runtime.

Fresh public traces can be repeated with:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/profile_grc_v4_families.py \
  --evolving --repetitions 5 --output /tmp/grcv4-evolving-costs
```

Use repeated `--family` options to select individual A/C families. The default
mode retains the separate numerical/public identical-input comparison.

### Verification of the implementation

The affected selection exercised 402 tests in 569.552 seconds: 399 passed,
two optional cases skipped, and one source-capture control failed because test
spacing was edited after the process loaded those files. A fresh integrity/new
control selection passed all ten tests. After the final 64 KiB bound and its
growing-record regression, all 25 codec tests passed.

After making the original logarithm rounding explicit, the RG2b selection ran
61 tests in 345.858 seconds with one optional slow case skipped. Its only failure
was a new memo assertion still comparing raw pre-rounding bounds with rounded
output. That assertion was corrected. A fresh final selection passed all eleven
integrity, large-record, logarithm, exact-rounding and A/C trial controls. All
22 additive event/initializer tests also passed, covering consumers of the
shared validation memo. The complete affected selection was not rerun as one
process after these targeted checks. There are no unresolved test failures.

Benchmark lint passes. Comparison against the committed versions of the changed
production/test files found no new lint diagnostics; existing findings remain.
Patch whitespace checks pass. Raw before/after traces, hashes and verification
counts are retained in `grcv4-realization-costs.json`.


## Longer-history correction: carry ownership instead of increasing the cache

The user's scaling concern was correct. The 64 KiB result cache postponed the
repeat work; it did not remove it. In a fresh evolving A_OS run, using the
fixture's admitted duration and `growth-check-{step}` operation IDs:

| Accepted step | Canonical result bytes | Result schema calls | Cache hits |
| --- | ---: | ---: | ---: |
| 1 | 16,580 | 3 | 2 |
| 6 | 56,605 | 3 | 2 |
| 7 | 64,502 | 3 | 2 |
| 8 | 72,397 | 3 | 0 |
| 10 | 88,215 | 3 | 0 |
| 20 | 167,354 | 3 | 0 |
| 50 | 403,171 | 3 | 0 |

At step 8, all three checks bypass the cache. The growth probe was stopped
after the 50-step sample; a completed 100-step run was not measured. Observed
size growth suggests roughly 0.8 MB at 100 steps, but that is an estimate, not
a measured size or runtime prediction. Bytes vary with operation IDs and values.

### Size-independent removal of redundant reconstruction

The public `bind_step_result()` still detaches and reconstructs caller-supplied
records before binding them. An externally obtained frozen object is not proof
of validity: forced field mutation must still be detected.

The private `_bind_owned_step_result()` contains the same binding comparisons.
The lifecycle owner invokes it immediately after constructing its own result,
before returning it or exposing it to caller code. The constructor has already
performed full result schema validation and local semantic checks. Reconstructing
that exact owned result in the next function added two schema calls, another
receipt reconstruction and another freeze/copy of the growing observations.
Those repetitions are now absent at every payload size. State, ledger, receipt,
commit, outcome and publication checks remain in place. There is no fast mode,
trust flag, cross-run validation scope or candidate/realization condition.

The global successful-payload memo is restored to its original 8 KiB/128-entry
bound, at most 1 MiB of retained payload bytes plus schema/key overhead. Large
result records are fully validated and are not retained in that memo. The
logarithm and fresh CI identity optimizations from the initial implementation
remain unchanged.

### Incremental benefit over the initial 64 KiB workaround

An isolated paired benchmark compared the initial public reconstruction path
with the owned-result path, retaining the other optimizations on both sides.
Each family executed five ordinary steps and a fresh profiled sixth step. The
table uses sixth-step call counts and total ordinary five-step runtime ratios.
All 60 snapshot hashes matched. Local timing gains are modest and several are
within variation; CI timings do not demonstrate an additional speedup. This is
an incremental comparison, not a new measurement against the original code.

| Family | Sixth-step calls, before → after | Fewer calls | Five-step speed ratio |
| --- | ---: | ---: | ---: |
| A_OS | 1,372,576 → 1,303,720 | 5.0% | 1.07× |
| C_OS | 1,316,797 → 1,248,024 | 5.2% | 1.01× |
| A_CI | 1,489,317 → 1,421,284 | 4.6% | 1.00× |
| C_CI | 1,500,710 → 1,432,717 | 4.5% | 0.99× |
| A_RG2b | 3,174,800 → 3,083,641 | 2.9% | 1.03× |
| C_RG2b | 2,878,888 → 2,810,597 | 2.4% | 1.03× |
| A_PC | 1,296,728 → 1,228,735 | 5.2% | 1.06× |
| C_PC | 1,262,972 → 1,194,979 | 5.4% | 1.05× |
| A_CI+PC | 1,537,903 → 1,469,870 | 4.4% | 1.03× |
| C_CI+PC | 1,546,511 → 1,478,291 | 4.4% | 1.01× |

For A_OS after crossing the old cache limit, a separate paired run used nine
ordinary steps followed by a fresh profiled tenth step. All ten snapshot hashes
matched. Ordinary trace time was 6.668 → 6.025 s (1.11×); tenth-step calls were
1,914,560 → 1,688,809 (11.8% fewer). This is not a 100-step scaling result.

### What still grows

`_public_observables()` includes the entire receipt ledger in every successful
result. Producing that detached representation requires work proportional to
history size. Retaining every full result can likewise consume quadratic total
space across a run; a larger memo would merely retain additional copies.

`_validate_publication()` also reconstructs the previous receipt ledger,
serializes all accumulated commit preimages and calls `_restore_commits()` on
the full archive. It scans historical scientific commitments again as well.
These repeated history traversals can make total run work grow quadratically,
even though the actual scientific computation has a small fixed graph. The
owned-result correction removes duplicate work; it does not remove those
archive traversals or change the public wire contract.

The architectural next step at that stage was a privately owned, append-only checked archive:
carry the established prefix and its lineage/component/clock facts forward,
validate the new delta against those facts, then publish the extended archive.
Full imports and explicit whole-history checks must still validate every record.
Ownership, mutation isolation, crossing compatibility and actual verified schema
content must be part of that design; public frozen dataclasses alone cannot
supply the fact. This archive change was not yet implemented by that patch; the later
contained implementation is described below.
A full-ledger public result still has linear materialization cost even with
incremental archive validation.


### Verification of the longer-history correction

The 135-test selection covered codec behavior, result composition/admission,
all generic lifecycle families and prepublication binding fault controls. It
completed with 132 passing, one opt-in packaging skip and two errors. One was
a subprocess timeout while the parent regression process was paused for timing
isolation. The other was a new negative-zero assertion expecting `V4WireError`
instead of the existing constructor's `ValueError`; the guard had correctly
rejected the invalid result.

After correcting only that expectation, a fresh three-test selection passed:
resource reconstruction outside the checkout across three hash seeds; the
all-ten-family one-validation/public-forgery control; and the over-1-MiB result
plus malformed-observation rollback control. All seven source-integrity tests
also passed. The entire 135-test selection was not repeated as one process.
There are no unresolved failures from that selection. Comparison against HEAD
found no new lint diagnostics in the five source/test files changed by this
correction; existing findings remain. Patch whitespace checks pass.


## Contained checked archive implementation

The subsequent archive implementation is contained in `_CheckedArchive` inside
`grc_v4_lifecycle.py`. Its `from_history()` entry point performs complete
historical checks on import. `read_ledger()` compares the actual exposed receipt
content with detached, type-aware immutable projections before returning private
admitted receipt objects. `append()` validates the new commit against the prior
lineage, component and clock facts and returns a prospective archive. A changed
prefix, registry/reference binding or structural transition runs the complete
historical checker and establishes a new checkpoint. All package asset and
optional validation dependency guards remain active on warm reads and appends.

The semantic commit and scientific-claim loops are shared by full import and
incremental append, rather than maintained as parallel implementations. The
lineage state carries prior receipt IDs, primary parent, reset identity and clock.
The scientific index preserves consistency of all historical component/clock
claims and checks newly available actual preimages against them. New index
containers are built before publication; a failed append cannot mutate the prior
archive's facts. The archive is not serialized and cannot be supplied through
the public snapshot contract.

Integration consists of the private publication's `ledger` property, archive
initialization/load, carrying the prospective archive in the final publication,
and passing the fact through compatible current-state assignment. The existing
private result binder now consumes owned captured receipt tuples; the public
binder still fully reconstructs caller-supplied ledgers. All source/target,
request, result, receipt, commit, outcome and publication comparisons remain.
There are no validation modes or new candidate/realization branches. Candidate,
CI, PC, CI+PC and RG2b numerical owners were not modified by this archive change.

An initial whole-prefix byte encoding experiment was insufficient: serializing
the complete archive twice consumed the semantic-check savings. The implemented
comparison projects only the exposed current history and extends the stored
immutable projections with the new delta. It distinguishes booleans from
numbers, rejects unsafe integer/float equivalence and prevents negative-zero or
nonfinite mutations from matching admitted values. Private captured receipts
never escape through state or result projections; changed exposed contents use
ordinary schema and identity reconstruction before any prefix reuse.

This is not constant-time stepping. Exact inspection of publicly exposed frozen
DTOs, tuple/index container copies and full-ledger result/evidence materialization
still grow with history size. Private fact storage is linear in the current
archive, rather than a global collection of growing historical result records.
The implementation removes repeated schema admission and semantic replay of the
prefix while preserving the current public observation and serialization format.

### Additional benefit over the owned-result implementation

A fresh ten-step A_OS baseline was recorded before these archive edits. Nine
ordinary step timings exclude creation, snapshot hashing and profiler time;
the tenth fresh step supplies call volume. All ten snapshot hashes match.

- Nine-step time: 5.587 → 4.925 s, 1.13× measured speedup.
- Tenth-step calls: 1,688,809 → 1,072,287, 36.5% fewer.
- These are local samples, not confidence intervals or a measured 100-step claim.

All-family fresh runs matched all 60 sixth-step-trace snapshot hashes against
the previous owned-result implementation. Call counts below are incremental
savings over that implementation. Runtime ratios across those separately
recorded family baselines are not claimed.

| Family | Sixth-step calls, before → after | Fewer calls |
| --- | ---: | ---: |
| A_OS | 1,303,720 → 963,486 | 26.1% |
| C_OS | 1,248,024 → 908,830 | 27.2% |
| A_CI | 1,421,284 → 1,081,704 | 23.9% |
| C_CI | 1,432,717 → 1,093,474 | 23.7% |
| A_RG2b | 3,083,641 → 2,766,638 | 10.3% |
| C_RG2b | 2,810,597 → 2,469,350 | 12.1% |
| A_PC | 1,228,735 → 889,264 | 27.6% |
| C_PC | 1,194,979 → 855,981 | 28.4% |
| A_CI+PC | 1,469,870 → 1,130,976 | 23.1% |
| C_CI+PC | 1,478,291 → 1,138,874 | 23.0% |


### Verification of the contained archive

The broad selection ran 254 cases in 745.376 seconds, covering the archive,
all generic families, lifecycle, migration, events, event audits, initializer,
public result composition/audit, codec and source-integrity controls. No behavior
assertion failed. Seven errors arose in two integrity methods (one with six
subtest controls): the capture runner rejects untracked source because it must
reconstruct all code from Git HEAD plus a scoped patch. The new archive test
file was marked intent-to-add to provide that reconstruction preimage; no
commit or staged file contents were created.

Independent review also found a public capture-order regression introduced by
moving ledger capture to the public binder. A hostile caller ledger could
alter the original request during capture before it was detached. The request
is now detached before reading those ledgers, preserving the original order;
a new adversarial regression requires the original foreign request to reject.
Native private ownership and the measured ordinary-step path are unchanged.

A fresh 50-case selection passed all archive, public composition/audit and
source-integrity controls after these corrections. The full 254-case selection
was not repeated as one process. New archive test lint passes, both production
files add no lint findings relative to HEAD, and patch whitespace checks pass.

## Operation-local evidence and incremental legacy lifecycle hashing

Implemented on `perf/v4-operation-evidence`, based on `8e4e048`. A fresh profile
of the 100th A_OS public step on the two-node, one-edge fixture exposed 5,101,971
calls. Geometry requested lifecycle identity through `source_lifecycle_id` 23
times and `_identity_chain` 23 times; the binder added two requests. These paths
repeated full receipt-array schema traversal and canonical hashing during one
numerical operation.

The compatibility-preserving implementation lives in
`src/pygrc/models/_grc_v4_evidence.py`. Geometry and the binder share its identity
resolver; ordinary lifecycle execution creates one private operation scope.
There are no candidate/realization branches or public validation switches.

### Exact legacy hashes can be incremental

The earlier architectural suggestion that incremental lifecycle hashing requires
a different identity format was too strong. Canonical key sorting places the
receipt array **before** the scientific-state digest. SHA-256's internal state
can therefore be retained immediately before closing that array. This is not
reuse of a finalized digest as though it were the original preimage.

The checked archive owns that state and its receipt count. An append copies the
state and adds only canonical bytes of the newly checked receipt IDs, including
any required comma. A lifecycle identity copies it again, closes the array, and
adds the fixed version and newly checked scientific-state digest. Existing
canonical bytes and lifecycle IDs remain exact. The private hash state is never
serialized, supplied by an imported snapshot, or used as proof of numerical
execution. Full import reconstructs it from the fully admitted history.

Operation memoization reuses IDs for the same checked prefix/state digest.
Immutable tuple aliases retain strong references, avoiding object-ID reuse;
new captures must match an admitted ordered prefix or follow full validation.
Asset pins and numerical dependency guards remain fresh on cache hits. Prefix
builders use the detached admission result, never a second read of a caller
iterable. New hash states never mutate prior published states, preserving
rollback.

The memo has bounded retained prefixes, aliases and identities and is discarded
at operation exit, including failures. Nested operations and separate threads
have independent scopes. Numerical solves, flux/read-back, selector, residual,
charge, history, receipt and publication checks remain with their existing owners.

### Binding checks do not require discarded evidence bytes

The native binder now returns only its checked request and source/target payloads.
Native callers still execute every comparison. The public `bind_step_result`
retains full detached capture and materializes the same `StepResultEvidence`
bytes. Ordinary native steps no longer serialize the result and both full ledgers
into evidence that their callers discard. Request capture still precedes caller
ledger reads, preserving the adversarial capture-order guard.

### Measured benefit and limits

The saved baseline and final branch each ran 100 evolving A_OS public steps using
the same operation IDs and fixed graph. Setup, request construction and the
50/100-step snapshot projections were excluded. No profiler was used for these
timings; separate 100th-step profiles supplied call counts.

| Measurement | Before (`8e4e048`) | Final branch |
| --- | ---: | ---: |
| 100 ordinary steps | 78.704 s | 57.956 s |
| 100th ordinary step | 1.341 s | 0.844 s |
| 100th-step profiled calls | 5,101,971 | 2,123,656 |

The final ordinary trace is 1.36x faster; call volume falls 58.4%. Both checkpoint
snapshot hashes match exactly, and the final profiled snapshot matches too.
The private binder's cumulative **profiled** time fell from 0.645 to 0.022 s;
profiled times are not ordinary runtime measurements or additive cost categories.

An intermediate cache-only implementation ran the same 100 steps in 51.946 s.
That separate-session sample is retained in the raw report. Its lower time does
not establish that removing unused serialization increases runtime, nor do these
single ordinary runs establish an isolated timing benefit for that second change.
The final profile confirms removal of its work. No all-family runtime speedup or
confidence interval is claimed.

**The narrow constant-time claim:** extending the retained hash evidence and
hashing a new state-digest suffix are independent of prior history length for a
bounded receipt delta. Newly captured tuple matching, public DTO inspection,
stage descriptor serialization, ledger/index copies and full result projections
still grow with history. The complete public step is not constant time, and total
run overhead can still be quadratic. This change does not alter those public
contracts or eliminate every historical scan.

All 86 focused checks passed: exact legacy hashes across growing/reordered
prefixes, failure and rollback, changing caller iterables, bounds, nested/thread
isolation, fresh asset/dependency rejection, archive import, public binder/audit,
codec, and source-integrity controls. All ten candidate/realization combinations
also produced identical result bytes and snapshots with operation identity reuse
enabled and replaced by the original full identity computation, over two positive
steps and a zero-duration step. New module, tests and benchmark lint pass; patch
whitespace checks pass.

Raw traces and profile summaries are retained in
`grcv4-operation-evidence-costs.json`. Reproduce a normal trace with:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grc_v4_history.py \
  --family A_OS --steps 100 --output /tmp/grcv4-history.json
```

Add `--profile-last` to profile the 100th step. Its time is then reported separately
and excluded from ordinary totals; that profiled run must not be compared as a
100-step ordinary runtime sample.

### Publication wiring follow-up: compare the target instead of rebuilding it

The user's concern about remaining call volume led to another concrete duplicate.
The public step constructed its complete target lifecycle state, then publication
constructed the same state again solely for equality comparison. Each projection
created frozen receipt records and the public lifecycle constructor captured them
again. The preceding 100th-step profile showed two `_lifecycle_state` calls, seven
stage serialize/parse round trips, and 345 `_load_contract_schema` calls.

`_CheckedArchive.check_target_state` now checks all 14 target fields directly.
Endpoint stage inputs are still freshly reconstructed with `replace`, retaining
the original geometry, coordinate, context, stage and identity admission checks.
The target DTO's public constructor still runs once. Its graph/profile/current,
reset baseline, context, clocks, charge target and identities are compared with
actual endpoint values. Every target receipt is inspected against the admitted
prefix plus the new delta, using the same detached type-aware token semantics.
The token walker reads frozen storage directly instead of thawing another ledger;
reordered keys remain equivalent, while boolean/number changes and changed arrays
fail. No validation or public result construction is disabled.

The all-family generic binder regression was updated for its private helper's
bounded return value. It now explicitly compares all six public evidence byte
fields rather than comparing a public evidence object with the obsolete private
return type. The same one-native-validation and full-public-revalidation assertions
remain. New controls force changes to each already constructed target field,
verify receipt token behavior, and require exactly one native target projection.
All 90 focused tests passed after correcting test setup; no production behavior
failure was observed. New test/module/benchmark lint and whitespace checks pass.

A fresh ordinary 100-step trace and separate final-step profile on the same A_OS
fixture produced the following local samples:

| Measurement | Preceding branch | Publication comparison change |
| --- | ---: | ---: |
| 100 ordinary steps | 57.956 s | 43.013 s |
| 100th ordinary step | 0.844 s | 0.513 s |
| 100th-step calls | 2,123,656 | 1,899,530 |

Call volume falls another 10.6%; the ordinary trace is 1.35x faster in these local
samples. Both checkpoint snapshots and the profiled final snapshot match exactly.
The whole branch now measures 78.704 → 43.013 seconds relative to `8e4e048`, while
preserving the public result. These are sequential single-run samples with timing
variation, not isolated attribution or confidence intervals. Raw follow-up traces
are in `grcv4-operation-evidence-costs.json` under `publication_wiring_followup`.

Remaining architectural opportunities include internal stage serialize/parse
handoffs and repeated asset verification. A numerical stage still receives the
receipt-ID history in its public descriptor; its wire projection is larger than
its numerical operands. The full public history and two exposed-state integrity
inspections also remain linear in history. This follow-up removes a demonstrably
redundant reconstruction; it does not make complete public steps constant time.


### Internal stage capture and operation asset verification

The next two targets are now implemented on `perf/v4-operation-evidence`.
The lifecycle owner performs one full stage serialize/parse admission in the
candidate-solve failure boundary and registers its detached reference privately
for that operation. `_capture_stage_inputs` rebuilds the Hodge and geometry and
runs the complete stage constructor on internal handoffs. It retains current and
reset reconstruction, carrier positivity, coordinates, context, clocks, trial
selection, receipt grammar and identity checks. The reference alone is reused.
External or unrecognized references still use full wire admission. Resource
selection capture also runs its constructor directly, retaining disposition and
current checks. Public payload parsers and scientific result binding remain.

Contract verification is scoped in the codec. It checks all pinned base assets
at entry, uses those verified bytes internally, then freshly verifies installed
assets before the publication pointer changes. Rejected results receive a fresh
exit check too. Nested operations and threads have separate scopes, and failure
clears them. Public request admission remains outside this scope; public schema
lookup always reads freshly, even inside a scope. Dependencies remain checked on
uses. Additive initializer/event asset verification is unchanged. No persistent
asset-trust cache or per-realization validation mode is introduced.

All ten candidate/realization combinations produced identical result bytes and
snapshots over two positive steps and a zero-duration step when operation
identity reuse and private stage capture were disabled and fresh asset reads
restored. The broader realization/resource/cache run passed 82 tests with one
existing skip. A separate evidence/codec/public-audit/capture run passed 62 tests
(overlapping the evidence tests). Controls require one full stage admission,
reject malformed private stage fields and a non-positive Hodge, reject changed
assets before publication without changing owned state, and require external
stage and public schema lookup admission. New-file lint passes, production lint
findings are unchanged from HEAD, and whitespace checks pass.

The same evolving public A_OS fixture (two nodes, one edge) gives:

| Measurement | Before this follow-up | After |
| --- | ---: | ---: |
| 100 ordinary public steps | 43.013 s | 27.997 s |
| 100th ordinary step | 0.513 s | 0.458 s |
| Calls in the 100th-step profile | 1,899,530 | 1,552,491 |
| Full stage wire captures in that step | 7 | 1 |
| Fresh base-contract asset verifications | 345 | 4 |

The operation itself performs two asset verifications; the other two are public
request admission checks. Internal `_load_contract_schema` calls still occur
(253 in the final profile), but use the operation's admitted snapshot instead of
rereading every installed file. The 100-step ordinary trace is 1.54x faster and
final-step call volume falls 18.3%. Step-50 and step-100 checkpoint snapshots and
the profiled final snapshot match the preceding version exactly. These are local
sequential samples with timing variation, not confidence intervals. Profiling
time is separate from ordinary runtime. Raw traces and counters are retained
under `stage_asset_followup` in `grcv4-operation-evidence-costs.json`.

Full public result construction and its history validation now dominate the
profile. Exposed-state integrity checks and public ledger projection still grow
with history. This change bounds repeated reference admission and asset disk
verification; it does not make the complete public step constant time or remove
all quadratic aggregate history work.


### Consolidate the audit boundary and reduce ownership assumptions

The preceding performance changes introduced an audit burden: four publication
paths had to remember an explicit fresh asset check, while assets and evidence
used two independent ContextVar lifetimes. This follow-up consolidates those
invariants rather than adding another optimization mode.

`GRCV4Operation._owned` is now a property over a private backing slot. Its one
setter requires an exact `_OwnedCOS`, freshly verifies pinned contract assets,
and only then changes the pointer. Ordinary assignment and even
`object.__setattr__(operation, "_owned", ...)` pass through that guard. A future
path using the ordinary owned-state assignment automatically receives the same
check. Initial construction and restoration also use it. Only that setter writes
the backing slot and records verified publication.

The codec owns one `_OperationContext`, holding pinned asset bytes, operation
facts and publication status. The evidence module reads that same context;
there is no second ContextVar to synchronize. Normal returns without publication
receive a fresh exit check, independent of a result's claimed committed flag.
Failures and nested scopes restore the entire context together. The private
publication status is set only after the setter's verified pointer write.

Reference ownership is now one retained reference compared with `is`. Tuple
aliases use a bounded scan of retained objects, and identity-cache keys retain
the actual frozen prefix object. All three `id()`-keyed caches are removed;
cache limits remain independent of history size and trial count. Receipt evidence
is a frozen dataclass. Incremental hashing encodes receipt elements through the
codec, derives its fixed-size framing from the codec's empty envelope, and
rejects an unexpected canonical layout. It no longer slices serialized array
bytes or duplicates the hard-coded scientific-state suffix. Exact legacy hash
comparisons, delta-extension and failure-preservation controls remain.

Archive comparison uses the existing efficient `FrozenJSONMap.items()` interface
rather than `_items`. `_lifecycle_fields` is the single bounded metadata projection
used for state construction and target comparison. An executable coverage check
requires its keys to cover every lifecycle dataclass field except the separately
checked ledger. A future field omitted from this projection fails closed. Every
target field and receipt is still compared; public constructors and scientific
result binding remain in place.

The review also found that assignment and administrative reset/rebase wrote
the state pointer after releasing their existing lock. Those writes now stay
inside the lock, keeping admission, asset verification and publication in the
same critical section. New controls check that ordering, exercise asset failure
through step/reset/rebase/assignment/direct pointer writes, and require unchanged
owned state on failure. Distinct getter/setter names preserve the existing
loaded-source integrity checker. The final main run passed 75 tests; subsequent
ownership controls passed three tests, and lock-order/publication/source checks
passed nine tests after the administrative correction. These runs overlap.
All ten realizations retain exact result bytes on full-admission comparison paths.
New-file lint passes, production lint findings are unchanged, and whitespace
checks pass.

| Measurement | Before consolidation | After |
| --- | ---: | ---: |
| 100 ordinary public steps | 27.997 s | 28.272 s |
| Calls in the 100th-step profile | 1,552,491 | 1,565,350 |
| Operation ContextVars | 2 | 1 |
| `id()`-keyed ownership/identity caches | 3 | 0 |
| Publication asset-verification sites | 4 | 1 |
| Lifecycle metadata projection implementations | 2 | 1 |

Call volume increases 0.83% and runtime increases 0.98% in these sequential local
samples. This is a small measured cost for fewer distributed safety assumptions;
no precise timing attribution or statistical confidence is claimed. Against the
preceding 43.013-second / 1,899,530-call publication version, the overall change
still measures about 1.52x faster with 17.6% fewer final-step calls. Checkpoints
at 50 and 100 and the profiled final snapshot match exactly. Raw data is under
`audit_boundary_followup` in `grcv4-operation-evidence-costs.json`.

Incremental hashing remains an algorithm tied to the pinned canonical wire
contract, with executable layout checks and byte-equivalence regressions. Python
privacy is not protection against deliberate backing-slot or module tampering.
The supported publication path enforces its guard automatically; fresh external
admission, exposed-state checks, numerical claim checks and source integrity
continue to define the surrounding audit boundaries. Full public-history cost
is unchanged by this consolidation and remains the dominant scaling limit.
