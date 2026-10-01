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
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_transport.py --steps 5
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_transport.py --steps 10
```

`--output PATH` selects a different report destination. Ordinary successful
commit receipts and the complete public step results are produced; there is no
provisional-only shortcut. Declaration construction uses checkout test helpers,
as the other examples do. This example does not extend global conformance claims
or the supported profile registry.

The grid size is configurable; for example, `--rows 6 --cols 6` builds a
36-node closed grid. Measured scaling and optimization studies belong to the
[implementation correction](../../implementation/corrections/GRCV4-MatrixPerformanceCloseout.md)
and its [retained evidence](../../implementation/evidence/grcv4-performance/README.md).

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

## Candidate C configurable grids

[grid_realizations_c.py](grid_realizations_c.py) accepts `--rows`, `--cols`,
`--steps`, and all five realizations. It shares the grid topology, reference
weights, and initial resource pulse with the A examples, while using C-specific
declarations and no A edge history. Setup proposes a nonconstant selector
cutoff; production exact rank and realization certificates decide admission.
The admitted declaration stays fixed throughout the public run.

```bash
PYTHONPATH=src:.:tests .venv/bin/python examples/grcv4/grid_realizations_c.py --realization CI --rows 3 --cols 4 --steps 5
```

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
