# GRC-v4 realization comparisons

These checkout-only examples construct matched declarations using test fixtures
and execute production numerical steps. They do not register new supported
profiles, modify the runtime, or create lifecycle acceptance receipts.

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
