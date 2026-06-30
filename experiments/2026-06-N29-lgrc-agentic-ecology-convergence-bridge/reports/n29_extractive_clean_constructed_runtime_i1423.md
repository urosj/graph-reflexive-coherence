# N29 I14.2-3 Leakage-Gated Extractor Construction Attempt

## Result

```text
status = passed
acceptance_state = accepted_producer_mediated_leakage_gated_extractor_construction_candidate_pending_controls_replay_stress
runtime_row_id = n29_i14_2_3_leakage_gated_extractive_construction_motif
capacity_delta_factor = 1.0
leakage_gate_factor = 0.5
merge_leakage_value = 0.0165
merge_leakage_ceiling = 0.025
merge_leakage_margin = 0.0085
minimum_meaningful_margin_floor = 0.005
meaningful_leakage_margin = true
rounding_level_margin_blocker = false
minimum_degradation_margin = 0.019
narrow_margin_caveat = false
clean_bounded_leakage_candidate_created = true
clean_bounded_leakage_support_claim_allowed = false
ready_for_i14_2_3_b_controls = true
output_digest = 8247fa5d5efcbb694051783a77a1b9d19c4f2785690bf75f820e1efa973d57d6
failed_checks = []
```

## Interpretation

I14.2-3 is a producer-mediated construction attempt, not an existing N28
source row. It keeps the primary I14.2 extractive capacity deltas at
source strength and adds an explicit declared leakage gate. The result
remains extractive because all neighbor/medium capacity deltas stay
negative and above degradation floors, while merge/leakage falls below
the original ceiling with a margin above the declared meaningful-margin
floor.

This replaces the earlier uniform-attenuation path because that path only
cleared the leakage ceiling by a rounding-scale margin. The replacement
does not claim native LGRC support: the leakage gate is visible producer
residue and must pass focused controls and replay/stress before it can be
used as clean bounded-leakage extractor evidence.

## Constructed Deltas

```text
environment_capacity_delta = -0.069
neighbor_support_delta = -0.063
neighbor_distinguishability_delta = -0.077
neighbor_boundary_delta = -0.081
```
