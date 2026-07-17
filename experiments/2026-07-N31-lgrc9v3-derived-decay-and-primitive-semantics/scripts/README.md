# N31 Scripts

## Iteration 1

- `build_n31_source_inventory_i1.py` builds the pinned source-and-authority
  inventory, runtime capability dispositions, historical evidence boundaries,
  and claim-clean I1 report.

Run with:

```bash
.venv/bin/python experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/scripts/build_n31_source_inventory_i1.py
```

## Iteration 2

- `build_n31_schema_control_freeze_i2.py` freezes semantic/authority/outcome
  axes, DR and closeout ladders, normalized route contracts, producer and
  restoration policies, active-null comparability, controls, and the RCAE
  return manifest.

Run with:

```bash
.venv/bin/python experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/scripts/build_n31_schema_control_freeze_i2.py
```

## Iteration 3

- `build_n31_active_nulls_and_failure_baselines_i3.py` instantiates all 70
  frozen controls as claim-relative, semantically comparable derived fixtures.
  It machine-checks cross-field contradictions, dimensional controls, and
  trace-derived ownership without opening positive decay evidence.

Run with:

```bash
.venv/bin/python experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/scripts/build_n31_active_nulls_and_failure_baselines_i3.py
```

Scripts should be deterministic, use repository-relative paths, consume exact
source artifacts, and keep candidate-specific topology and invariants explicit.
Experiment scripts may construct fixtures and invoke public runtime operations;
they must not modify `src/` or implement hidden load-bearing D0 decay updates.
