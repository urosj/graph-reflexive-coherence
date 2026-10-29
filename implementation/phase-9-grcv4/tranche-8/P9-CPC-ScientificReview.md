# C_PC Tranches 8–9: scientific scope and evidence

C_PC is the sixth realization in this bounded campaign, continuing on
`work/p9-aos-tranches-8-9`. The first five accepted realizations remain C_OS,
C_CI, A_CI, A_PC, and A_OS. This campaign covers P9-8.4d through P9-9.6;
P9-9.1a, C_PC basin migration, Tranche 10 work, and all-ten conformance remain
unselected. Execution records do not confer user acceptance.

## Deep layouts and exact represented charge

The inherited D94 split `(17,24,23)/64` sums to one mathematically. At the
actual evolved C_PC source, however, the three binary64 transfer products sum
to the source resource minus `2^-52`. The accepted small C_PC consumer requires
exact equality of represented charge. The replacement dyadic split is
`(1087,1537,1472)/4096`, with the same phase/chirality branch permutation. It
moves `1/4096` between the first two inherited shares, preserves the exact
represented resource sum in both histories, and passes the independent
20-step nominal feasibility preflight. No charge tolerance was changed.

The deep campaign retains 20 events, 40 history cells, 400 native target steps,
and 40 final reads. Signed flat and readback certificates accompany the current,
geometry, structural-source, continuity, and held-carrier checks. The ordering
campaign has 20 transformed history cells; the chart campaign has 24. Their
baseline cells, fresh source beats, two-step continuations, final reads, and
both complete carrier histories are retained explicitly.

## Original large target exclusion and separate companion

The original graph has 100 vertices and 400 edges; expansion produces 107
vertices and 407 edges. The original C_PC target has a strictly negative
first-step resource at `extra/1/1` in **both** current and reset histories
(about `-9.76e-15`). The original source passes. The original target therefore
receives no native-continuation credit. Its independent interval evidence is
retained in `P9-8.4g-CPCResults.json`.

A separately declared companion chooses `(1/4,3/8,3/8)` from exact affine
Candidate C leading-operator constraints, with leading margin `3/4`. It moves
`1/1024` resource from source vertex 0 to vertex 29, at graph distance 8, in
both histories. This is an exactly charge-preserving fixture change. The
profile, compact chart, solver tolerances, and ordinary step size remain fixed.
Allocation-only diagnostics and the adjusted fixture are retained separately.
Independent bounds establish source/target first-step nonnegativity for both
roles and the actual source postbeat trigger before native execution.

The native campaign requires four prerequisite steps, the actual event from
the evolved source, ten target steps per history, two final reads, and eight
signed/order/chart counterparts with one target step per history. The actual
event transfer is reconstructed from the evolved source; prepared-target
success cannot substitute for it. Every event retains complete current/reset
carrier archives and the four separate loss receipts. Replay must reproduce
the exact checkpoint bytes.

## Arithmetic, caching, and bounds

Workers use FLINT exact rationals, certified Arb at 256 bits for native large
calculations, one BLAS/OpenMP thread, operation-scoped exact-operand matrix
facts, and an eight-entry success-only schema memo bounded to 4 MiB per entry.
The preflight verifies the active policy before long work. The first 400-edge
source pilot took 411.531 seconds and observed 3 rounded-solve cache hits and
13 matrix-fact cache hits. Large event, step, and final-read caps are 1,800
seconds. Worker processes enforce these caps even inside a native call.

Profiling also identified repeated canonical JSON encoding of dense carrier
payloads. Subsequent large segments use a separate research-only JCS memo:
at most 16 entries and 64 MiB total key/value bytes, with an 8 MiB per-payload
limit. Every caller still passes the original I-JSON validation. Exact-content
keys retain only successful immutable RFC 8785 output bytes, never mutable
objects or failed inputs. Four mutation/eviction/rejection tests and native
checkpoint byte parity are retained in `P9-CPC-WirePreflight.json`. Earlier
executions keep their original records and policy; later segments bind the
additional runner/cache sources and record actual cache hits.
The first large event attempt, with matrix/schema reuse but without the added
JCS memo, reached the 1,800-second cap. `P9-CPC-EventCapAttempt.json` retains
that incomplete attempt with zero native success credit. The first memo-enabled
retry completed native expansion and checkpoint replay, then exposed an omitted
history-receipt schema tag in the retained-record checker. That failed attempt
has no retained success credit. A small native event reproduces the corrected
receipt check, including rejection of the missing-tag mutation. The full retry
uses the same event and unchanged 30-minute cap with the preflighted memo.
The successful baseline event and exact replay took 1,675.982 seconds and
recorded 662 canonical-byte hits. Larger covariance transports are prepared
separately under a 600-second mechanical budget. Construction reuses immutable
inputs and avoids rebuilding geometry that the transform immediately discards;
all sixteen small source/target transformations are checked against full
reconstruction. Spawned event workers reconstruct the prepared payload and
perform fresh native admission, event and replay under the 1,800-second cap.
The preparation time is retained separately from native execution time.
The initial parallel larger-covariance batch reached the 1,800-second worker
cap while continuation jobs were also active. It produced no passing
counterpart records. That development attempt receives no native-success
credit; capacity and scheduling are checked again before retrying under the
same numerical tolerances and per-worker cap.
`P9-CPC-CovarianceCapAttempt.json` retains the failed-batch log, frozen input
declaration, and exact original verifier source bytes.

Covariance retries use 64 JCS entries and 128 MiB total key/value capacity;
the 8 MiB per-payload limit and encoding/validation rules stay fixed. The
source-bound `P9-CPC-CovarianceComputePreflight.json` records four capacity
regressions and identical payload digests across two repeated constructions
under each policy. Hits increased from 63 to 85 and evictions fell from 29 to
zero. The measured times were 277.373 and 291.544 seconds under concurrent
work, so this pilot does not establish a wall-time speedup. It grants no native
execution credit. Initial retries avoid overlap with ordinary continuations.

The independent oracle uses Arb at 192 bits and a Woodbury reduction to a
vertex system. Connectedness and a strict whole-chart spectral gap establish
the selector sector. Whole-carrier radius, symmetry, resource norm, Hodge
positivity, source invariance, and conditioning are checked separately from
pointwise solves. The independent oracle does not call a native current,
selector, carrier certificate, or step producer.

Saved reads have signed componentwise error certificates for current, baseline,
readback, flat, Hodge, and structural source. Resource and carrier update bounds
also account for staged binary64 rounding. These are pointwise bounds at each
saved input, not a uniform enclosure of a ten-step exact trajectory. Ordinary
steps require exactly one continuity evaluation and one held-source ZOH write;
reset authority, clocks, receipts, and old-carrier geometry are consumed from
saved operands.

## Verification-source maintenance

`P9-CPC-VerifierSourceEpochs.json` retains original verifier bytes and exact
successor hashes for three verifier files: the independent transfer helper's
role constant, the inherited Candidate A initializer expectation for C_PC,
and the large-event consumer. The consumers use that finite source bridge;
the large-event checker also includes the history receipt's schema tag and
preserves a private failure capture if completed native execution fails a
subsequent consumer check. Such captures confer no retained success credit.
The first three large prerequisite records and the first two Tranche 9 records
keep their original bytes and digests. No numerical runtime producer changed,
old execution was not relabelled, and the broken target helper had not been
called by those three prerequisites. Other source changes are rejected.

`P9-CPC-SourceEpochs.json` separately preserves the accepted predecessor source
epochs through exact Git bytes. It does not certify new C_PC execution. The
compatibility successor contains 20 accepted, 4 passed-pending-acceptance, and
16 unselected cells. The four C_PC contract provenance traces retain
`indeterminate_requires_review`; no scientific or support authority is promoted.
