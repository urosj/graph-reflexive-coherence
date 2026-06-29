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

Later scripts will build probe artifacts, replay/control matrices, stress
matrices, classification records, and closeout records.
