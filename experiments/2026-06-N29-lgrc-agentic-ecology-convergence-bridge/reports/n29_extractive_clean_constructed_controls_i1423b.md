# N29 I14.2-3-B Leakage-Gated Extractor Controls

## Result

```text
status = passed
acceptance_state = accepted_leakage_gated_extractor_controls_fail_closed_pending_replay_stress
control_count = 10
failed_closed_count = 10
failed_open_count = 0
candidate_survives_controls = true
leakage_gate_factor = 0.5
capacity_delta_factor = 1.0
merge_leakage_margin = 0.0085
ready_for_i14_2_3_c_replay_stress = true
output_digest = 4897dd938ae282ea3cf062d83dd3250434d42bb92a61e37cbf6722d870e397f9
failed_checks = []
```

## Interpretation

I14.2-3-B validates the leakage-gated extractor by rejecting hidden gate,
gate-as-native, threshold-retune, uniform-attenuation, neutral-gap
backfill, label-only, source-caveat erasure, rounding-margin, report-only,
and ecology/resource relabel paths. The candidate survives only as an
explicit producer-mediated bridge candidate pending replay/stress.
