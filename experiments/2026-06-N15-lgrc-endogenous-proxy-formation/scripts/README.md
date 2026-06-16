# N15 Scripts

Reconstruction scripts for N15 belong here.

Generated scripts:

- `build_n15_proxy_source_inventory.py`
- `build_n15_proxy_formation_schema_v1.py`
- `validate_n15_row.py`

Planned scripts:

- `build_n15_runtime_derived_target_candidate.py`
- `build_n15_external_proxy_contrast_matrix.py`
- `build_n15_proxy_control_matrix.py`
- `build_n15_bounded_drift_replay_matrix.py`
- `build_n15_claim_boundary_record.py`
- `build_n15_closeout_and_handoff.py`

Use `.venv/bin/python` for local runs.

Shared script requirements:

- Resolve source artifacts from portable relative paths or config entries.
- Verify expected SHA-256 values before using a source artifact.
- Emit deterministic JSON with sorted keys.
- Compute output digests with SHA-256 over canonical JSON that excludes
  wall-clock timestamps, local absolute paths, and git working-tree metadata.
- Fail closed with distinct blocker labels for missing sources, digest
  mismatch, stale state, budget invalidity, incomplete dependency traces,
  nondeterministic derivation, unexpected control pass, unsafe claim flags, and
  absolute path emission.
- Write reports as summaries of generated JSON rather than independent sources
  of evidence.
