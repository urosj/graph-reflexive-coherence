# GRC-v4 numerical examples

These checkout-only examples construct matched declarations using test fixtures
and execute production numerical steps. They do not register new supported
profiles, modify the runtime, or create lifecycle acceptance receipts.

## Larger public simulation: 20-node transport grid

[grid_transport.py](grid_transport.py) runs **A_OS through the strict public
GRCV4 lifecycle** on a **4×5 grid: 20 nodes, 31 edges**. Horizontal edges point
right and vertical edges point down; every nearest neighbour is connected.
The graph has loops and node degrees from two to four. Candidate A uses actual
2-D grid positions for its regularized differential descriptors.

The closed system starts with total resource **40**, a smooth gradient across
both axes, and a localized `+0.25` / `−0.25` perturbation at `r1c2` / `r2c2`.
These are initial conditions; there is no external injection or boundary input.
Resource values initially span `1.65625–2.34375`. Reference weights vary spatially
from `1–1.375`, and retained `W_A` starts at `1.5–1.75`. The initial state is also
the reset baseline.

- Timestep: `1/64`; A history relaxation time: `1/8`.
- Candidate coefficients: `eta=0.125`, `kappa_c=0.25`, `kappa_Ah=0.125`;
  `alpha=0.02`, `beta=0.1`, `gamma=0.05`.
- Feedback: `chi_A=zeta_A=0.25`; geometry gain: `0.09375`.
- OS split tolerance: `1e-8`; absolute charge tolerance: `1e-11`.
- Differential descriptor regularization: `1`, in two dimensions.

Run separate fresh processes from the repository root:

```bash
PYTHONPATH=src:.:tests /usr/bin/time -f 'process_wall_seconds=%e' .venv/bin/python examples/grcv4/grid_transport.py --steps 5
PYTHONPATH=src:.:tests /usr/bin/time -f 'process_wall_seconds=%e' .venv/bin/python examples/grcv4/grid_transport.py --steps 10
```

`--output PATH` selects a different report destination. Ordinary successful
commit receipts and the complete public step results are produced; there is no
provisional-only shortcut. Declaration construction uses checkout test helpers,
as the other examples do. This example does not extend global conformance claims
or the supported profile registry.

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

- [5-step report](results/grid_transport_5.json)
- [10-step report](results/grid_transport_10.json)

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
identity are in the [6×6 five-step report](results/grid_transport_6x6_5.json).
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
remain uncached, and publication guards are unchanged.

The current primitive reuse measurements use the same strict public 4×5
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
exactly. The [primitive comparison](results/grid_transport_a_primitive_reuse_comparison.md)
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

- [4×5 five-step reuse](results/grid_transport_matrix_reuse_5.json).
- [4×5 ten-step reuse](results/grid_transport_matrix_reuse_10.json).
- [6×6 five-step reuse](results/grid_transport_6x6_matrix_reuse_5.json).
- [Lookup-disabled control](results/grid_transport_matrix_reuse_disabled_5.json).
- [Ten-step profile](results/grid_transport_matrix_reuse_profile_10.json).
- [Complete comparison and validation details](results/grid_transport_matrix_reuse_comparison.json).

## Configurable public grids for the other A realizations

[grid_realizations_a.py](grid_realizations_a.py) accepts the same grid dimensions
as the OS transport example. It builds CI, PC, CI+PC or RG2b declarations, then
runs strict public `GRCV4.step_v4_input` operations with receipts and snapshots.

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_realizations_a.py --realization CI --rows 4 --cols 5 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_realizations_a.py --realization PC --rows 6 --cols 6 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_realizations_a.py --realization "CI+PC" --rows 3 --cols 4 --steps 5
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_realizations_a.py --realization RG2b --rows 4 --cols 5 --steps 5
```

These are examples of the same graph size, not identical physical experiments.
At 4×5 they preserve the OS reference geometry, initial resources and retained
edge history. CI keeps the original physical coefficients, geometry gain and
time step. PC and CI+PC reduce geometry gain to fit their uniform carrier
certificates. RG2b also reduces transport eta and the physical time step to
certify its compact graph domain.

For other dimensions, initialization scales the resource gradient and pulse to
keep each resource within 0.34375 of its center 2. The declarations scale with
node/edge count; the whole-chart PC resource bound also scales with node count.
Setup checks the production certificate and can select a more conservative
declaration before creating the public owner. It records every attempted
declaration admission and the final exact certificate bounds in the JSON.
Declarations remain fixed throughout evolution. A rejected certificate or
public step is never treated as a successful run; setup stops after twelve
unsuccessful attempts. Arbitrary grid sizes or run lengths are not guaranteed
admissible.

Step timing excludes declaration construction, owner setup, progress output and
the final snapshot. Those costs are recorded separately. Reports retain full
identity-bound inputs, the A differential reference, C/W/Z after every step,
receipt counts and the final snapshot digest. Candidate C grids are deferred to
the next comparison.

The benchmark-only [disabled control](benchmark_grid_a.py) accepts the same
arguments. It disables inverse and conditioning fact reuse while retaining the
exact same declaration and strict public path. It records inverse and conditioning
requests, hits and misses separately. Add `--reuse` to observe enabled reuse.

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/benchmark_grid_a.py --realization CI --rows 4 --cols 5 --steps 5
```

[The 4×5 A comparison](results/grid_transport_a_realizations_comparison.md)
contains five-step timings, per-step costs, preparation volume, exact state and
snapshot equivalence, and links to every enabled/disabled report.

## Five realizations, two candidates

From the repository root, using the existing virtual environment:

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/compare_candidate_a.py --output-dir examples/grcv4/results
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/compare_candidate_c.py --output-dir examples/grcv4/results
```

Each command runs **OS, CI, RG2b, PC, and CI+PC for ten physical steps**. These
are small graphs, but certified root/section construction and final readmission
make the complete runs substantially slower than an ordinary arithmetic loop.
Progress prints after each realization's step.

Both candidates use the same branching topology:

```text
v000 ──e000──> v001 ──e001──> v002
                │
               e002
                ↓
              v003
```

- Reference edge weights: `(1, 1.125, 1.25)`.
- Initial resource: `(2.12, 1.88, 2.10, 1.90)`; total resource `8`.
- Candidate A's initial retained `W_A`: `(1.96875, 2, 2.03125)`.
- Candidate C has **no independent W history**; its exact reference transport
  weights are fixed configuration, recorded in the JSON declarations.
- PC and CI+PC start with the same zero `3×3` carrier; the other realizations
  have no carrier slot.
- Common step duration: `2^-10`; geometry gain `0.075`.
- Carrier relaxation time: `2^-9`, so each write covers half a relaxation time.

Within each candidate, **all five share candidate coefficients, reference
geometry, topology, initial resources/history, and step duration**. Solver and
realization declarations differ as required. The RG2b compact domain constrains
the common experiment: this is not a large-signal parameter sweep. Small or
numerically unresolved differences must not be presented as proof that every
realization has a distinct trajectory.

## Retained reports

- [Candidate A: complete evolution and end-state comparison](results/candidate_a_five.md)
  ([full numerical data](results/candidate_a_five.json)).
- [Candidate C: complete evolution and end-state comparison](results/candidate_c_five.md)
  ([full numerical data](results/candidate_c_five.json)).

Every report presents all node resources and edge histories, complete symmetric
carrier/geometry/source matrices, baseline and total current, potential,
read-back flux, causal flat read, and the candidate-specific derived quantities.
JSON retains full arrays, declarations, solver diagnostics, and the A backend.

Read-back effects are explicitly decomposed as
`J = J0 + ζ·read` and `ΔC = -dt·B·J0 - dt·B·(ζ·read)`.
Continuation includes each step's `ΔW`, `ΔZ`, reconstructed next-read current,
geometry and source, and their differences from the current read. The next
actual read is checked against that reconstruction. This reconstruction does
not advance the clock or write history. In particular, step ten's continuation
is **not an eleventh physical step**.

Continuation differences combine resource and history changes; they do not
isolate a W-only or carrier-only causal intervention. A's read target `W_hat_A`
is distinguished from the post-continuity writer target `W_drv_A`. C's selected
sector and retained Hodge are recomputed quantities, not independently stored
history. OS predictor/corrector details and RG2b section errors are retained
without treating either method as an exact CI root.

The final comparisons cover all ten realization pairs, including next-read
current and geometry. An absent carrier is not silently identified with a
stored zero matrix. Pairwise distances are observed floating-point differences,
not automatically certified separation beyond each method's numerical error.

Reports can be reformatted without another numerical run:

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/compare_candidate_a.py --render-from examples/grcv4/results/candidate_a_five.json --output-dir examples/grcv4/results
```

## Smaller three-realization example

The original [single-edge A comparison](compare_ci_pc.py) uses a stronger
CI/PC/CI+PC comparison regime, without RG2b's additional common-domain constraint:

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/compare_ci_pc.py
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/compare_ci_pc.py --zero-gain --steps 2
```
