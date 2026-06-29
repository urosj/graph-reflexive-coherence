# N28 Scripts

- `build_n28_source_inventory_and_contract_admission.py` - Builds the
  deterministic Iteration 1 source inventory and contract admission artifacts.
- `build_n28_generative_extractive_schema_and_controls.py` - Builds the
  deterministic Iteration 2 schema and control freeze artifacts.
- `build_n28_active_nulls_and_failure_baselines.py` - Builds the deterministic
  Iteration 3 active-null and failure-baseline artifacts.
- `build_n28_primary_generative_candidate_probe.py` - Builds the deterministic
  Iteration 4 primary source-current GE3 generative candidate probe and trace
  artifact bundle.
- `build_n28_generative_strengthening_candidate_probe.py` - Builds the
  deterministic Iteration 4-A GE3 generative strengthening probe, including the
  direct margin comparison against I4.
- `build_n28_generative_mechanism_diversity_probe.py` - Builds the
  deterministic Iteration 4-A2 GE3 generative mechanism-diversity probe, using
  split-shell capacity growth with delayed boundary thickening.
- `build_n28_primary_extractive_contrast_probe.py` - Builds the deterministic
  Iteration 4-B GE3 primary extractive measured contrast probe and trace
  artifact bundle.
- `build_n28_extractive_strengthening_contrast_probe.py` - Builds the
  deterministic Iteration 4-C GE3 extractive strengthening contrast probe,
  including direct margin comparison against I4-B.
- `build_n28_extractive_mechanism_diversity_probe.py` - Builds the
  deterministic Iteration 4-C2 GE3 extractive mechanism-diversity probe, using
  merge/leakage-dominant boundary flattening.
- `build_n28_primary_competitive_neutral_contrast_probe.py` - Builds the
  deterministic Iteration 4-D GE3 competitive/neutral measured contrast probe,
  using mixed neighbor capacity redistribution without generative or
  extractive promotion.
- `build_n28_competitive_neutral_mechanism_diversity_probe.py` - Builds the
  deterministic Iteration 4-E GE3 competitive/neutral mechanism-diversity
  probe, using three-lobe neutral capacity circulation without generative or
  extractive promotion.
- `build_n28_replay_capacity_attribution_matrix.py` - Builds the
  deterministic Iteration 5 replay and capacity-attribution matrix over I4
  through I4-E.
- `build_n28_artifact_only_reconstruction_replay_probe.py` - Builds the
  deterministic Iteration 5-A artifact-only reconstruction replay controls.
- `build_n28_stress_regime_separation_matrix.py` - Builds the deterministic
  Iteration 6 stress and regime-separation matrix over the I4-family rows
  admitted by I5.
- `build_n28_regime_boundary_transition_matrix.py` - Builds the deterministic
  Iteration 6-A regime boundary / transition matrix around the I6 GE5 result.
- `build_n28_margin_envelope_sweep.py` - Builds the deterministic Iteration
  6-B margin envelope sweep around the I6 stress matrix.
- `build_n28_higher_margin_neutral_circulation_probe.py` - Builds the
  deterministic Iteration 4-F focused higher-margin neutral circulation
  variant recommended by I6-B.
- `build_n28_higher_margin_competitive_redistribution_probe.py` - Builds the
  deterministic Iteration 4-G focused higher-margin competitive
  redistribution variant recommended by I6-B.
- `build_n28_focused_margin_variant_replay_matrix.py` - Builds the
  deterministic Iteration 5-B replay/control matrix for I4-F and I4-G.
- `build_n28_focused_margin_variant_stress_envelope.py` - Builds the
  deterministic Iteration 6-C focused stress/envelope matrix for I4-F and
  I4-G.

Later scripts will build probe artifacts, replay/control matrices, stress
matrices, classification records, and closeout records.
