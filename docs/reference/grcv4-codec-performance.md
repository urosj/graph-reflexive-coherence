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
