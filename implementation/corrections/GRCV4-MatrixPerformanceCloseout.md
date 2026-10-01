# GRCV4 Matrix Performance Closeout

Record class: bounded implementation correction. The work removes redundant
matrix preparation and specializes one exact conditioning decision while keeping
scientific admission, strict public validation, and certificate contents.

The runnable grid declarations remain in [examples/grcv4](../../examples/grcv4/README.md).
Benchmark harnesses live under [scripts](../../scripts/), and raw measurements,
paired comparisons, and source hashes live in the [performance evidence](../evidence/grcv4-performance/README.md).
Historical timings below are single local samples from their recorded revisions;
the linked reports retain the exact workload, per-step results and validation.

## Original A_OS baseline

Measured locally using runtime commit `b2aff80`, without a profiler:

| Fresh run | Sum of public step times | Mean per step | Setup | Complete command |
| --- | ---: | ---: | ---: | ---: |
| 5 steps | 64.804 s | 12.961 s | 0.867 s | 68.28 s |
| 10 steps | 140.230 s | 14.023 s | 0.894 s | 143.79 s |

Step timers include public admission, numerical stages, strict validation and
result/history capture. They exclude setup, request construction, diagnostics,
progress output and the final snapshot. The complete-command column is measured
by `/usr/bin/time` and includes imports, setup, evolution, snapshot and report
writing. Reports also record simulation wall time and final snapshot time.
These are single sequential local samples, not statistical estimates.

Both runs committed every requested step. The first five numerical states match
exactly across the separate processes. Total resource stays within `1e-11` of
40; all resources remain nonnegative and all retained weights stay positive.
Maximum resource changes after 5 / 10 steps are approximately `0.0411 / 0.0735`;
maximum retained-history changes are `0.4285 / 0.6129`. Each committed step
produces four ordinary receipts. Physical endpoint times are `5/64` and `10/64`.

The reports retain complete initial declarations, the 2-D differential backend,
all per-step node resources and edge histories, individual timings, receipt
counts and final snapshot identities:

- [5-step report](../evidence/grcv4-performance/grid_transport_5.json)
- [10-step report](../evidence/grcv4-performance/grid_transport_10.json)

## Larger-grid scaling sample: 36 nodes

The same runner accepts grid dimensions. This fresh **6×6** A_OS run used
**36 nodes and 60 edges**, with the same timestep, coefficients, public commit
path and five-step schedule. The centered gradient preserves a closed initial
resource total of **72**, with the +0.25 / -0.25 perturbation at `r2c3` /
`r3c3`. The original 4×5 declaration remains byte-for-byte equivalent to the
earlier report.

```bash
PYTHONPATH=src:.:tests /usr/bin/time -f 'process_wall_seconds=%e' .venv/bin/python examples/grcv4/grid_transport.py --rows 6 --cols 6 --steps 5
```

| Grid | Nodes | Edges | Step 1 | Step 2 | Step 3 | Step 4 | Step 5 | Step sum | Complete command |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4×5 | 20 | 31 | 13.098 s | 15.281 s | 12.694 s | 13.004 s | 10.726 s | 64.804 s | 68.28 s |
| 6×6 | 36 | 60 | 127.720 s | 203.832 s | 242.801 s | 209.201 s | 244.130 s | 1,027.683 s | 1,033.57 s |

The larger run averaged **205.537 s per step** and took **15.86×** as much
public step time as the 4×5 run. All five commits succeeded, each produced
four receipts, and the resource total remained 72. The final maximum resource
and retained-history changes were 0.04297 and 0.42869, respectively. The step
times vary substantially on an unchanged graph, so this two-size sample does
not establish an asymptotic complexity law or isolate a single cause. It does
show that the exact numerical work becomes very costly before the history is
long. This run was not profiled.

The complete initial declaration, numerical states, timings and final snapshot
identity are in the [6×6 five-step report](../evidence/grcv4-performance/grid_transport_6x6_5.json).
The report's grid-size label was corrected after timing; no numerical result
or step timing was recomputed.

## Certified matrix preparation reuse

Reuse now belongs to the existing exact inverse and conditioning primitives.
Direct calls from analytic residuals, selectors and domain certificates use the
same operation-owned store as certified solves. The combined solve-preparation
layer has been removed; each primitive retains its single original numerical
algorithm behind its cached entry point.

Inverse facts name exact immutable coefficients. Conditioning facts additionally
name the exact conditioning limit. The store retains at most **64 facts total**
per operation, including small descriptor and interval blocks; it has no growth
with trace length. This replaces the older budget of eight combined solve
preparations, which did not account for direct callers. Successful facts alone
are stored. Every RHS, residual check, stage-labelled certificate and failed
conditioning attempt is evaluated under its current declaration. Unscoped calls
remain uncached, and publication guards are unchanged. PC, CI+PC and RG2b can seed a new scope
with the bounded numerical continuation described below; its operation store
and asset context still end at scope exit.

The primitive-only measurements below predate bounded continuation and use the same
strict public 4×5
examples, with 20 nodes and 31 edges. Each before/after pair has an identical
complete declaration. These gains are additional to the previous solve cache:

| Realization | Previous five-step total | Primitive reuse total | Additional speedup |
| --- | ---: | ---: | ---: |
| A_CI | 153.384 s | 117.100 s | 1.31× |
| A_PC | 72.237 s | 71.611 s | 1.01× |
| A_CI+PC | 161.750 s | 129.453 s | 1.25× |
| A_RG2b | 224.296 s | 202.090 s | 1.11× |

These are single sequential local samples. New runs include a light primitive
lookup counter; totals exclude setup and snapshotting. PC benefits mainly in
small descriptor inversions, without a material change in runtime. All saved
states, receipt counts and final snapshot digests match the previous runs
exactly. The [primitive comparison](../evidence/grcv4-performance/grid_transport_a_primitive_reuse_comparison.md)
records per-step times, numerical work counts, source hashes and validation.

The older OS measurements below describe the **previous shared-solve cache**
at revision `a857940`; its primitive bypasses were still uncached. They are
retained as historical measurements.

Earlier sequential unprofiled samples with the shared-solve cache:

| Grid and schedule | Saved baseline step sum | With reuse | Mean with reuse | Speedup |
| --- | ---: | ---: | ---: | ---: |
| 4×5, 5 steps | 64.804 s | 32.786 s | 6.557 s | 1.98× |
| 4×5, 10 steps | 140.230 s | 66.206 s | 6.621 s | 2.12× |
| 6×6, 5 steps | 1,027.683 s | 465.398 s | 93.080 s | 2.21× |

Complete command times with reuse were 36.01 s, 69.36 s and 470.88 s,
respectively. The larger run's individual step times were 63.148, 90.343,
111.602, 94.624 and 105.680 seconds. These are single local samples.

A separate five-step 4×5 control on the same modified runtime forced every
preparation lookup to miss using a test-only mock. It took **61.423 s**, versus
**32.786 s** with reuse: **1.87× speedup**, or **46.6% less step time**. This
checks the reuse benefit separately from the older baseline's timing variation;
there is no production mode switch.

Across a separate ten-step 4×5 profile, inverse and conditioning preparations
each dropped from **50 to 20** (**60% fewer**): two preparations in every
step. All **50 certified solve calls** still ran, together with **150 total
residual checks** across the flat solves and A current equations. Total
profiled function calls dropped from **114,078,930 to 70,797,732** (**37.9%
fewer**). The earlier profile additionally recorded solve inputs in a temporary
wrapper; those few wrapper calls are negligible relative to this volume.
Profiled timings are not used for the ordinary-runtime speedups above.

Every new run and the lookup-disabled control matches its baseline's full
initial declaration, all saved resources and histories, receipt counts and
final snapshot SHA256 exactly. Regression tests also compare exact public
result bytes and snapshots for OS, CI, PC, CI+PC and RG2b in both candidates,
with operation reuse disabled. Strict warm-cache failures, nested operations,
thread isolation, immutable preparation and bounded eviction have regression
coverage.

Reports record the runtime base commit and hashes of the modified source files:

- [4×5 five-step reuse](../evidence/grcv4-performance/grid_transport_matrix_reuse_5.json).
- [4×5 ten-step reuse](../evidence/grcv4-performance/grid_transport_matrix_reuse_10.json).
- [6×6 five-step reuse](../evidence/grcv4-performance/grid_transport_6x6_matrix_reuse_5.json).
- [Lookup-disabled control](../evidence/grcv4-performance/grid_transport_matrix_reuse_disabled_5.json).
- [Ten-step profile](../evidence/grcv4-performance/grid_transport_matrix_reuse_profile_10.json).
- [Complete comparison and validation details](../evidence/grcv4-performance/grid_transport_matrix_reuse_comparison.json).

## Shared matrix API and explicit fresh calculation

All five A realizations and all five C realizations use
[`grc_v4_numerics.py`](../../src/pygrc/models/grc_v4_numerics.py) for common exact
matrix conversion, multiplication, transpose, inverse, inertia, certified
conditioning, and physical solves. A's SPD normal-equation solve uses the same
inverse store, with fresh positivity and exact RHS checks. Candidate-specific
rounding and scientific admission remain with their owners. Interval/section
algorithms keep their separate certified contracts and call this shared API
for exact matrix work.

Ordinary strict public steps automatically reuse successful inverse and
conditioning facts. Callers do not prepare matrices or choose separate cached
and uncached functions. The private arithmetic implementation is
[`_grc_v4_matrix.py`](../../src/pygrc/models/_grc_v4_matrix.py); the old candidate C `_c_*` matrix entry points are removed.
Boundary tests reject implementation imports from realization modules. Public
failure messages and the historical `CandidateCStageError` exception spelling
are retained; that spelling aliases the neutral `MatrixError` type.

For diagnostics or independent verification, choose fresh matrix calculation
once at the operation boundary:

```python
from pygrc.models import grc_v4_numerics as matrices

# Normal use: automatic operation-owned reuse.
result = model.step_v4_input(request)

# Explicit verification mode: recompute matrix facts throughout this operation.
with matrices.matrix_operation(reuse=matrices.MatrixReuse.FRESH):
    result = model.step_v4_input(request)
```

Fresh mode bypasses lookup, seeding, and retention of numerical facts. It does
not weaken solver limits, residual checks, certificates, asset verification, or
publication admission. Nested scientific operations inherit the selected
policy while each receives its own private store. A nested matrix scope with
no explicit policy also inherits it; an explicit `AUTOMATIC` policy can override
it. The policy is not a new profile field or wire/snapshot mode.

Standalone matrix calls have no shared lifetime unless grouped in
`matrices.matrix_operation()`. There is no global cache. The existing bound of
64 inverse/conditioning facts per operation and four retained facts for two
matrices between eligible steps is unchanged. Every RHS and stage certificate
remains fresh in both modes.

[The shared API validation report](../evidence/grcv4-performance/shared_matrix_api_validation.md)
records exact public result and snapshot compatibility with the committed code
for all ten realizations, automatic/fresh equivalence, and regression checks.

## Bounded numerical continuation for PC, CI+PC and RG2b

The admitted reset and final Hodge matrices repeat across PC, CI+PC and RG2b
steps. CI+PC selects the actual trial Hodge from its admitted CI roots. The
lifecycle adapter now retains
only their available inverse and conditioning facts in the immutable committed
publication: **at most four facts for two matrices**. Each fresh operation seeds
its private store from those facts. The bound is independent of trace length;
matrix storage still scales with graph size.

Only the numerical fact store and lifecycle adapter change in production. PC,
CI+PC and RG2b recipes, candidate current/writer algorithms, state admission, asset contexts,
public formats and snapshot contents are unchanged. Exact coefficient and
conditioning-limit matches remain required, with fresh RHS, residual and
certificate work. Failed publications preserve the previous continuation.
Reset, rebase, assignment, restoration, migration and topology/representation
publications start cold by default. The other realization lifetimes are unchanged.

A sequential, separate-process five-step control on the 4×5 A_PC grid kept reuse
within each operation but disabled continuation at publication:

| Measurement | Operation reuse only | With continuation |
| --- | ---: | ---: |
| Total step time | 72.232 s | 45.785 s |
| Large inverses / conditioning proofs | 14 / 14 | 6 / 6 |
| Certified solves / residual checks | 15 / 45 | 15 / 45 |
| Fresh certificates / chart-membership checks | 15 / 15 | 15 / 15 |

This is **1.58× faster**, or **36.6% less step time**, in one local timing pair.
Every saved state and final snapshot digest matches both the control and the
previous primitive-only run exactly. All five publications retained four facts.
The [continuation comparison](../evidence/grcv4-performance/grid_transport_a_pc_continuation_comparison.md)
records per-step times, source hashes, counters and the 247-test regression run.

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --disable-continuation --rows 4 --cols 5 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --rows 4 --cols 5 --steps 5
```

The disabled control is a benchmark-only mock; production has no mode switch.

RG2b uses the same four-fact bound, selecting its already admitted reset and
restart native-point Hodge matrices. Graph sections, certified error enclosures,
whole-chart certificates and native arithmetic bridges still run freshly.
A fresh sequential five-step A_RG2b comparison on the same **4×5, 20-node,
31-edge** grid measured **202.882 s → 108.400 s**:
**1.87× faster**, or **46.6% less step time**.
Large inverse and conditioning computations each fell **19 → 11**. Both runs
still performed 65 certified solves, 185 residual checks, 65 fresh conditioning
certificates, 15 whole-chart certificates, 15 graph sections, and five native
arithmetic bridges. Every saved state and final snapshot digest matches the
control and prior primitive-only run exactly. All five publications retained
four facts. The [RG2b continuation comparison](../evidence/grcv4-performance/grid_transport_a_rg2b_continuation_comparison.md)
records timings, counts, source hashes, and the successful 145-test regression
run (one optional slow campaign skipped). This is one local timing pair.

The shared benchmark also accepts RG2b:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --realization RG2b --disable-continuation --rows 4 --cols 5 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --realization RG2b --rows 4 --cols 5 --steps 5
```

A repeat of the strict 4×5, five-step **A_CI+PC** workload after these updates
measured **131.471 s**, versus **129.453 s** in the earlier
primitive-reuse run. Every operation's inverse/conditioning lookup counts are
identical, as are all saved states and the final snapshot digest. At the time
of that repeat, CI+PC did not select continuation. The shared scalar PC carrier
write was unchanged, so its timing difference did not indicate a change in
numerical work. The [CI+PC repeat measurement](../evidence/grcv4-performance/grid_transport_a_ci_pc_after_pc_comparison.md)
retains those timings, counters, and source hashes as a historical measurement.

CI+PC now selects its already admitted reset/final roots' trial Hodge matrices
through the same bounded continuation adapter. Every root still starts from the
reference and performs fresh contraction/domain, PC envelope, and joint-residual
checks. The held same-root source still feeds exactly one PC carrier write.
Neither a whole root nor a certificate is cached.

The corrected paired **4×5, five-step A_CI+PC** measurement took
**131.121 s → 78.064 s**:
**1.68× faster**, or **40.5% less step time**.
Large inverses and conditioning proofs each fell **18 → 10**. Both runs retained
102 certified solves, 248 residual checks, 102 fresh conditioning certificates,
15 CI contraction certificates, 15 PC envelopes, 29 joint trial residuals, and
five carrier writes. Every saved state and final snapshot digest matches the
control and both preceding primitive-only runs. All publications retained four
facts. The [CI+PC continuation comparison](../evidence/grcv4-performance/grid_transport_a_ci_pc_continuation_comparison.md)
records the single local timing pair, source hashes, counters, and the 25 focused
plus 130 broader regression tests, all passing with no skips.

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --realization CI+PC --disable-continuation --rows 4 --cols 5 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --realization CI+PC --rows 4 --cols 5 --steps 5
```

## A-grid public comparison

Step timing excludes declaration construction, owner setup, progress output and
the final snapshot. Those costs are recorded separately. Reports retain full
identity-bound inputs, the A differential reference, C/W/Z after every step,
receipt counts and the final snapshot digest. Candidate C has a separate
[configurable-grid comparison](../evidence/grcv4-performance/grid_transport_c_realizations_comparison.md).

The benchmark-only [disabled control](../../scripts/benchmark_grcv4_grid_a.py) accepts the same
arguments. It disables inverse and conditioning fact reuse while retaining the
exact same declaration and strict public path. It records inverse and conditioning
requests, hits and misses separately. Add `--reuse` to observe enabled reuse.

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_a.py --realization CI --rows 4 --cols 5 --steps 5
```

[The 4×5 A comparison](../evidence/grcv4-performance/grid_transport_a_realizations_comparison.md)
contains five-step timings, per-step costs, preparation volume, exact state and
snapshot equivalence, and links to every enabled/disabled report.

## C-grid public comparison

The [Candidate C comparison](../evidence/grcv4-performance/grid_transport_c_realizations_comparison.md)
measures five public steps for OS, CI, PC, CI+PC, and RG2b on a **3×4 grid
(12 nodes, 17 edges)**. Automatic matrix reuse gives 1.26–2.10× speedups
against paired controls, with exact per-step result and snapshot equality.
Bounded continuation reduces a few more matrix calculations but shows no
material five-step timing gain in C on this grid. One admitted C_OS step
on **4×5 (20 nodes, 31 edges)** takes 226.33 seconds, excluding 140.41
seconds of declaration admission and 74.64 seconds of owner setup. The
report separates this one-step scaling observation from the complete
3×4 comparisons. Candidate A and C do not have identical physical laws,
so their times should not be interpreted as a controlled A/C speed ratio.

A subsequent [exact PSD certificate improvement](../evidence/grcv4-performance/grid_transport_c_exact_psd_comparison.md)
applies through the shared matrix API to all five C realizations. On 3×4
five-step runs it reduced OS from 81.49 to 57.82 seconds (1.41×), PC from
64.24 to 46.73 seconds (1.37×), and RG2b from 217.39 to 155.53 seconds
(1.40×). CI and CI+PC showed only small differences (1.04× and 1.03×) in
single runs. Every before/after pair has exact public output and fact-count
equality. The earlier C report and 4×5 one-step timing are
retained as pre-change baselines; the optimized C_OS 4×5 public step took
136.28 seconds with exact public output equality (1.66× faster).
