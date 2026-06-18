# N17 Scripts

Reconstruction scripts for N17 belong here.

Generated scripts:

- `build_n17_loop_source_inventory.py` - Builds the Iteration 1 source
  inventory, loop contract, source digests, phase gap map, and no-AP7 claim
  checks.
- `build_n17_loop_schema_v1.py` - Builds the Iteration 2 loop schema, AP7
  gate, and config files.
- `validate_n17_loop_row.py` - Validates future N17 loop rows against the
  Iteration 2 fail-closed AP7 gate.
- `build_n17_one_way_crossing_active_null.py` - Builds the Iteration 3
  one-way crossing active null and verifies it fails closed as AP7.
- `build_n17_perturbation_response_recovery_loop.py` - Builds the Iteration 4
  perturbation-response-recovery G3 candidate and keeps AP7 blocked pending
  Iteration 5 replay and controls.
- `build_n17_loop_replay_and_control_matrix.py` - Builds the Iteration 5
  replay and control matrix for the I4 candidate without adding new loop
  evidence.
- `build_n17_claim_boundary_record.py` - Builds the Iteration 6 MVP
  claim-boundary record, classifies the perturbation-response-recovery
  candidate as artifact-level AP7 at MVP scope, keeps the evidence rung at G4,
  and keeps G5, full comparative AP7, and final AP7 closeout blocked.
- `build_n17_mvp_challenge_stability_probe.py` - Builds the Iteration 6-A
  bounded MVP challenge-stability probe for G5 without opening resource/support
  or shared-medium extensions.
- `build_n17_alternative_g5_challenge_probe.py` - Builds the Iteration 6-B
  alternative target-band-gated G5 challenge probe without retuning the 6-A
  breach/flux envelope.

Planned scripts:

- `build_n17_resource_support_modulation_loop.py`
- `build_n17_shared_medium_reciprocal_loop.py`
- `build_n17_closed_loop_requirements_matrix.py`
- `build_n17_closeout_and_handoff.py`

Use `.venv/bin/python` for local runs.

Shared script requirements:

- Resolve source artifacts from portable relative paths or config entries.
- Verify expected SHA-256 values before using a source artifact.
- Emit deterministic JSON with sorted keys.
- Compute output digests with SHA-256 over canonical JSON that excludes
  wall-clock timestamps, local absolute paths, and git working-tree metadata.
- Fail closed with distinct blocker labels for missing sources, digest
  mismatch, stale state, budget invalidity, incomplete dependency traces,
  unexpected control pass, unsafe claim flags, one-way crossing relabel, hidden
  state carryover, post-hoc loop stitching, feedback removal, non-monotonic
  phase ordering, and absolute path emission.
- Write reports as summaries of generated JSON rather than independent sources
  of evidence.
