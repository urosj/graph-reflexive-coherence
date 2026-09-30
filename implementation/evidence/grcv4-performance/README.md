# GRCV4 performance evidence

This directory retains measured V4 grid runs, numerical-work counts, profiles,
source hashes, and paired strict-public comparisons. The [implementation
closeout](../../corrections/GRCV4-MatrixPerformanceCloseout.md) explains the
changes and their contract boundaries. The runnable public grid declarations
remain in [examples/grcv4](../../../examples/grcv4/README.md).

For the larger original grid, see the [6×6 A_OS FLINT comparison](grid_transport_6x6_flint_comparison.md),
which pairs the pre-optimization five-step run with the current exact CPU backend.

Start with the [A realization comparison](grid_transport_a_realizations_comparison.md),
[primitive reuse comparison](grid_transport_a_primitive_reuse_comparison.md), and
[shared matrix API validation](shared_matrix_api_validation.md). The
[Candidate C comparison](grid_transport_c_realizations_comparison.md) covers
all five C realizations, and the [exact PSD comparison](grid_transport_c_exact_psd_comparison.md)
shows the later shared conditioning improvement. Linked JSON files contain the
raw per-step measurements and complete declarations/results; timing samples
are local observations, not statistical estimates.

The `grid_transport_*` files were relocated from `examples/grcv4/results/`
after the measurements. Historical source-hash keys and runtime commit IDs
still name the files and revisions that were actually measured. Those hashes
were not recalculated to describe the new layout. Navigational links between
reports now point here; the relocation itself did not rerun or alter the
numerical experiments.

From the repository root, the benchmark-only harnesses now live under `scripts/`:

```bash
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_a.py --realization CI --rows 4 --cols 5 --steps 5 --reuse
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_c.py --realization CI --rows 3 --cols 4 --steps 5 --reuse
PYTHONPATH=src:.:tests .venv/bin/python scripts/benchmark_grcv4_grid_continuation.py --candidate C --realization PC --rows 3 --cols 4 --steps 5
```

The harnesses write new reports to the ignored `runs/` folder here by
default, so a repeat cannot overwrite curated evidence. `--output` selects
another location for an explicitly retained run. Ordinary grid runners in `examples/grcv4` remain usage examples and
keep their own optional output behavior. A benchmark control changes only the
observer's fact lookup/continuation return, not the production solver policy.
