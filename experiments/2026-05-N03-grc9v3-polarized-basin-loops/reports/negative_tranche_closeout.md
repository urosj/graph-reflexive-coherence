# Iteration 6 Negative Tranche Closeout

Command:

```bash
.venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/close_negative_tranche.py
```

Status: `pass`
Classification: `negative_fixed_topology_first_tranche`

No polarized basin loop was observed on the first 12-node fixed-topology GRC9V3 ported-ring fixture under S/K lanes.

This is a valid negative result, not an implementation failure. No
classifier or threshold tuning was performed to rescue the first tranche.

## Lane Summary

| Group | Lane | Budget | Source | Sink | Raw Cascades | Role-Gated Cascades | Claim Allowed |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| null_structured | S | True | False | False | 0 | 0 | False |
| null_structured | U0 | True | False | False | 0 | 0 | False |
| null_structured | U1 | True | True | False | 21 | 0 | False |
| null_structured | U2 | True | False | False | 0 | 0 | False |
| kick | K | True | False | False | 0 | 0 | False |
| kick | K_reversed | True | False | False | 0 | 0 | False |

## Validated

- `fixed_topology_grc9v3_runtime_bridge`
- `observable_library_on_real_traces`
- `budget_topology_provenance_reporting`
- `null_rejection_behavior`
- `role_gated_blocking_of_shape_only_cascades`

## Not Validated

- `L4_conserved_internal_loop`
- `L5_self_regulating_pulse_generator`
- `L6_boundary_couplable_loop`
- `movement_or_locomotion_precursor_evidence`

## Future Branches

- Branch B diagnostic sweeps remain unopened and have claim ceiling
  `diagnostic_sensitivity_map_not_positive_loop_claim`.
- Branch C fixture/theory redesign remains unopened and requires a new
  fixture manifest plus a new claim ceiling.
- L5, L6, multi-pole Appendix A, and movement-ladders handoff remain
  blocked/deferred because L4 was not established.

## Errors

- none
