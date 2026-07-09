# N30 Scripts

N30 reconstruction and artifact-generation scripts will be stored here.

## Builders

- `build_n30_source_inventory_i1.py`: emits the Iteration 1 source inventory
  JSON and report.
- `build_n30_schema_control_freeze_i2.py`: consumes the Iteration 1 inventory
  and emits the Iteration 2 schema/control freeze JSON and report.

Run from the repository root:

```bash
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_source_inventory_i1.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_schema_control_freeze_i2.py
```
