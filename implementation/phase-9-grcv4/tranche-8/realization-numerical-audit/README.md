# Retained independent numerical audit results

These are the supplied 2026-10-02 audit's historical JSON results, copied without
modification. Read the [retained review](../P9-8.0-RealizationNumericalIndependentReview.md)
for execution limits and the [local correction record](../P9-8.0-RealizationNumericalFeasibility.md#review-correction-and-portable-evidence)
for subsequent repository verification. The original isolated loader and its
duplicate dependencies are not needed to run the repository controls.

- [original_results.json](./original_results.json): original five test bodies,
  150 read stages, 124 effects, fixture transcript and audit environment.
- [input_mutation_results.json](./input_mutation_results.json): thirteen accepted
  altered-input counterexamples in the uncorrected consumer.
- [review_control_results.json](./review_control_results.json): six original
  cases and thirteen rejected mutations with the reviewer's isolation wrapper.
- [additional_pressure_results.json](./additional_pressure_results.json): exact
  equilibrium counterexample and six rejected C matrix-order substitutions.
- [carrier_transfer_pressure_results.json](./carrier_transfer_pressure_results.json):
  eight naive carrier-copy rejections, each with 27 unsupported edge pairs.
- [rg_independent_chain_results.json](./rg_independent_chain_results.json): eight
  physical and two exterior queries in an independent reconstruction; this is
  not execution or source review of the repository's RG numerical evaluator.

The reusable controls now run against current repository dependencies:

```bash
.venv/bin/python implementation/phase-9-grcv4/verification/test_p980_realization_numerical.py
```

Run that command from the repository root. The original JSON files intentionally
retain the old consumer's accepted counterexamples; they are evidence of RN-F1,
not expectations for the corrected implementation. No complete-profile,
carrier-policy, aggregate or production acceptance is recorded here.
