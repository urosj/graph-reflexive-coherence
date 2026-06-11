# N11 Scripts

This directory will hold N11 artifact builders, probes, and validators.

Generated scripts:

- `build_n11_iteration_1_baseline_inventory.py`: builds the N10 source
  inventory and N11 baseline boundary.
- `build_n11_iteration_2_fixture_manifest.py`: builds and validates the N11
  generalization fixture manifest.
- `run_n11_iteration_3_route_context_transfer_replay.py`: runs the
  route-context transfer replay.
- `run_n11_iteration_4_proxy_condition_transfer_replay.py`: runs the
  proxy-condition transfer replay.
- `run_n11_iteration_4b_proxy_target_band_variant_probe.py`: runs the
  proxy target-band variant probe.
- `run_n11_iteration_5_support_state_transfer_replay.py`: runs the
  support-state transfer replay and consumes 4-B when computing the contiguous
  GALI ceiling.
- `run_n11_iteration_6_multi_axis_transfer_matrix.py`: builds the
  context/proxy/support transfer matrix from Iterations 3, 4, 4-B, and 5.
- `run_n11_iteration_7_longer_horizon_generalization_window.py`: extends
  accepted Iteration 6 rows over the manifest's 8-window trend horizon.
- `run_n11_iteration_8_hidden_stale_claim_controls.py`: runs the fail-closed
  hidden/stale/out-of-envelope/budget/native-relabeling/inheritance/claim
  control suite.
- `run_n11_iteration_9_artifact_only_generalization_validator.py`: validates
  the accepted N11 generalization chain from exported artifacts only.
- `build_n11_iteration_10_hypothesis_ab_closeout.py`: closes Hypotheses A/B
  and decides the strongest supported GALI ceiling.
- `build_n11_iteration_11_hypothesis_c_native_generalization_gap.py`: records
  native generalization gaps and Phase 8 readiness behind the GALI7 result.
- `build_n11_iteration_12_final_closeout_and_handoff.py`: closes N11 and
  records final handoff state.
