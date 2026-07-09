# N30 Scripts

N30 reconstruction and artifact-generation scripts will be stored here.

## Builders

- `build_n30_source_inventory_i1.py`: emits the Iteration 1 source inventory
  JSON and report.
- `build_n30_schema_control_freeze_i2.py`: consumes the Iteration 1 inventory
  and emits the Iteration 2 schema/control freeze JSON and report.
- `build_n30_active_nulls_i3.py`: consumes the Iteration 2 schema freeze and
  emits the Iteration 3 active-null/failure-baseline JSON and report.
- `build_n30_participant_admissibility_i4.py`: consumes I3 plus underlying N27
  source-current transfer/replay artifacts and emits the bounded I4 participant
  admissibility JSON, supporting traces, and report.
- `build_n30_participant_admissibility_i4a.py`: consumes I4 plus the underlying
  N27 topology/fixture variant transfer/replay artifacts and emits the bounded
  I4-A participant-admissibility strengthening JSON, supporting traces, and
  report.
- `build_n30_participant_boundary_support_i4b.py`: consumes I4, I4-A, and the
  N27 stress/mapping-variant matrix to emit the I4-B participant boundary /
  support-sensitivity JSON, supporting traces, and report.

Run from the repository root:

```bash
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_source_inventory_i1.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_schema_control_freeze_i2.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_active_nulls_i3.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_participant_admissibility_i4.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_participant_admissibility_i4a.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_participant_boundary_support_i4b.py
```
