# N16 Scripts

Reconstruction scripts for N16 belong here.

Generated scripts:

- `build_n16_boundary_source_inventory.py`
- `build_n16_boundary_schema_v1.py`
- `build_n16_quiet_boundary_calibration.py`
- `build_n16_challenge_sweep_matrix.py`
- `build_n16_boundary_state_sweep_matrix.py`
- `build_n16_selected_interaction_probe_matrix.py`
- `build_n16_basin_boundary_requirements_matrix.py`
- `build_n16_claim_boundary_record.py`
- `validate_n16_row.py`
- `build_n16_closeout_and_handoff.py`

Use `.venv/bin/python` for local runs.

Shared script requirements:

- Resolve source artifacts from portable relative paths or config entries.
- Verify expected SHA-256 values before using a source artifact.
- Emit deterministic JSON with sorted keys.
- Compute output digests with SHA-256 over canonical JSON that excludes
  wall-clock timestamps, local absolute paths, and git working-tree metadata.
- Fail closed with distinct blocker labels for missing sources, digest
  mismatch, stale state, budget invalidity, incomplete dependency traces,
  unexpected control pass, unsafe claim flags, and absolute path emission.
- Write reports as summaries of generated JSON rather than independent sources
  of evidence.
