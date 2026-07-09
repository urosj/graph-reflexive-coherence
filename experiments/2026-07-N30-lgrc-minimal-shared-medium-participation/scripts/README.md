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
- `build_n30_medium_surface_trace_i5.py`: consumes I4-B plus the N28 I4-A
  source-current focal/neighbor artifacts and replay trace to emit the I5
  medium-surface perturbation / trace JSON, supporting traces, and report.
- `build_n30_medium_surface_trace_i5a.py`: consumes I5 plus the N28 I4-A2
  source-current split-shell / delayed-boundary mechanism-diversity artifacts
  and replay trace to emit the I5-A mechanism-diverse M1 strengthening JSON,
  supporting traces, and report.
- `build_n30_medium_surface_scope_window_i5b.py`: consumes I5, I5-A, and N28
  neighbor-capacity stress rows to emit the I5-B persistence / scope-window
  audit JSON, supporting traces, and report.
- `build_n30_later_eligibility_i6.py`: consumes I5, I5-A, I5-B, and the N28
  same-policy transition traces to emit the I6 later eligibility /
  susceptibility JSON, supporting traces, and report.
- `build_n30_later_eligibility_margin_i6a.py`: consumes I6 and emits the I6-A
  later-eligibility contrast-margin JSON, supporting traces, and report.
- `build_n30_alternative_source_tranche_i4c_to_i6c.py`: consumes the N28 I4-F
  higher-margin neutral-circulation source and focused replay/stress records to
  emit I4-C, I5-C, I5-D, I6-B, and I6-C alternative-source JSON, supporting
  traces, and reports.

Run from the repository root:

```bash
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_source_inventory_i1.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_schema_control_freeze_i2.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_active_nulls_i3.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_participant_admissibility_i4.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_participant_admissibility_i4a.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_participant_boundary_support_i4b.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_medium_surface_trace_i5.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_medium_surface_trace_i5a.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_medium_surface_scope_window_i5b.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_later_eligibility_i6.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_later_eligibility_margin_i6a.py
.venv/bin/python experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/build_n30_alternative_source_tranche_i4c_to_i6c.py
```
