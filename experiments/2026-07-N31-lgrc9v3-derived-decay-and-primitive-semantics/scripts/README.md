# N31 Scripts

## Iteration 1

- `build_n31_source_inventory_i1.py` builds the pinned source-and-authority
  inventory, runtime capability dispositions, historical evidence boundaries,
  and claim-clean I1 report.

Run with:

```bash
.venv/bin/python experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/scripts/build_n31_source_inventory_i1.py
```

Scripts should be deterministic, use repository-relative paths, consume exact
source artifacts, and keep candidate-specific topology and invariants explicit.
Experiment scripts may construct fixtures and invoke public runtime operations;
they must not modify `src/` or implement hidden load-bearing D0 decay updates.
