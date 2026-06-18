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
- `build_n17_resource_support_modulation_loop.py` - Builds the Iteration 7
  resource/support modulation extension and blocks resource depletion as
  semantic goal pursuit.
- `build_n17_resource_support_challenge_stability_probe.py` - Builds the
  Iteration 7-A local G5 challenge-stability probe for the fixed Iteration 7
  route_b resource/support loop.
- `build_n17_alternative_resource_support_g5_probe.py` - Builds the Iteration
  7-B alternative low-margin resource/support G5 setup without treating it as a
  7-A refinement.
- `build_n17_shared_medium_reciprocal_loop.py` - Builds the Iteration 8 local
  one-sided shared-medium reciprocal loop extension, blocks general/reverse-
  perspective G6, merge/leakage relabels, and keeps symmetric native
  multi-basin claims and final AP7 blocked.
- `build_n17_shared_medium_reverse_perspective_probe.py` - Builds the
  Iteration 8-A shared-medium reverse-perspective/alternate-source probe,
  preserving the B4/C5 reverse-replay blocker while adding N07 alternate
  dual-basin bounded-exchange evidence.
- `build_n17_b4c5_reverse_perspective_replay_probe.py` - Builds the Iteration
  8-B B4/C5-specific reverse-perspective replay probe, recording that B4/C5 is
  multi-basin but not perspective-paired.
- `build_n17_paired_perspective_shared_medium_probe.py` - Builds the
  Iteration 8-C local paired-perspective shared-medium probe with explicit A/B
  perspective rows, a joint paired row, and fail-closed one-sided, label-swap,
  B4/C5-reuse, merge/leakage, asymmetric, and final-AP7 controls.
- `build_n17_b4c5_derived_paired_perspective_probe.py` - Builds the Iteration
  8-D B4/C5-derived two-cycle paired-perspective probe, preserving the
  original B4/C5 reverse-replay blocker while generating source-backed
  cycle-2 reverse-side state in the derived protocol.
- `build_n17_closed_loop_requirements_matrix.py` - Builds the Iteration 9
  comparative requirements and AP7 classification matrix with extensions
  included as the source classification for the Iteration 10 closeout.
- `build_n17_closeout_and_handoff.py` - Builds the Iteration 10 final closeout
  and N18 handoff, freezing final artifact-level AP7 while keeping unsafe,
  native, Phase 8, and agency claims blocked.

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
