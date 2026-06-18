# N17 Reports

Human-readable reports for N17 generated artifacts belong here.

Generated reports:

- `n17_loop_source_inventory.md` - Iteration 1 interpretation of the source
  inventory and loop-contract artifact. It records no direct historic AP7
  support and hands off the missing ordered-closure gap to Iteration 2.
- `n17_loop_schema_v1.md` - Iteration 2 schema interpretation. It records G3
  as the first admissible closed-loop rung and keeps AP7 unsupported.
- `n17_one_way_crossing_active_null.md` - Iteration 3 active-null
  interpretation. It records a G2 near-miss and rejects it as AP7 because the
  feedback leg is absent.
- `n17_perturbation_response_recovery_loop.md` - Iteration 4 interpretation.
  It records the first G3 perturbation-response-recovery candidate while
  keeping final AP7 blocked pending Iteration 5 replay and controls.
- `n17_loop_replay_and_control_matrix.md` - Iteration 5 interpretation. It
  records replay stability and break-control results for the I4 candidate,
  upgrading it only to a G4 replay/control-clean candidate with final AP7
  still blocked.
- `n17_claim_boundary_record.md` - Iteration 6 interpretation. It classifies
  the MVP perturbation-response-recovery candidate as artifact-level AP7 at
  MVP scope while keeping current evidence at G4 and blocking G5, unsafe
  promotions, full comparative AP7, and final AP7 closeout.
- `n17_mvp_challenge_stability_probe.md` - Iteration 6-A interpretation. It
  records bounded G5 support for the MVP loop under the source-backed
  breach/flux envelope while keeping final AP7 blocked.
- `n17_alternative_g5_challenge_probe.md` - Iteration 6-B interpretation. It
  records an independent target-band-gated G5 alternative with mild
  attenuation and source-window delay support while keeping final AP7 blocked.

Planned reports:

- `n17_resource_support_modulation_loop.md`
- `n17_shared_medium_reciprocal_loop.md`
- `n17_closed_loop_requirements_matrix.md`
- `n17_closeout_and_handoff.md`

Reports should summarize generated JSON artifacts without weakening source
traceability or claim boundaries.
