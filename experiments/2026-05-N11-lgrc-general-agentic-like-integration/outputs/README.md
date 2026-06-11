# N11 Outputs

This directory will hold machine-readable N11 output artifacts.

Generated artifacts:

- `n11_iteration_1_baseline_inventory.json`: source-backed N10 inventory and
  N11 starting boundary.
- `n11_iteration_2_fixture_manifest_validation.json`: validation result for
  the frozen N11 generalization fixture manifest.
- `n11_iteration_3_route_context_transfer_replay.json`: route-context transfer
  replay result for the N10 composition.
- `n11_iteration_4_proxy_condition_transfer_replay.json`: proxy-condition
  transfer replay result, blocked at GALI3 because no source-backed target-band
  variant exists.
- `n11_iteration_4b_proxy_target_band_variant_probe.json`: source-backed
  proxy target-band variant probe supporting scoped GALI3 proxy-condition
  transfer while preserving Iteration 4's negative source audit.
- `n11_iteration_5_support_state_transfer_replay.json`: support-state transfer
  replay matrix over intact, mild-withdrawal, disrupted, and explicitly
  restored support states, refreshed after 4-B with contiguous GALI4.
- `n11_iteration_6_multi_axis_transfer_matrix.json`: deterministic 24-row
  context/proxy/support matrix, with accepted bounded GALI5 rows and distinct
  source-derived blockers.
- `n11_iteration_7_longer_horizon_generalization_window.json`: 8-window
  artifact replay extension over accepted Iteration 6 rows, with trend fields
  and bounded GALI6 candidates.
- `n11_iteration_8_hidden_stale_claim_controls.json`: fail-closed negative
  control suite for hidden/stale/out-of-envelope/budget/native-relabeling/
  inheritance/claim-promotion boundaries.
- `n11_iteration_9_artifact_only_generalization_validator.json`: artifact-only
  replay validator over Iterations 1-8, with all seven manifest-declared
  validation passes green and no private runtime fallback.
- `n11_iteration_10_hypothesis_ab_closeout.json`: Hypothesis A/B closeout
  decision supporting local GALI7 as a broader/general artifact-only
  agentic-like integration candidate while preserving unsafe claim boundaries.
- `n11_iteration_11_hypothesis_c_native_generalization_gap.json`: native
  generalization gap inventory behind the GALI7 artifact-only result.
- `n11_iteration_12_final_closeout_and_handoff.json`: final N11 closeout and
  handoff, recording GALI7 artifact-only ceiling, native blockers, and roadmap
  update.
