# Iteration 4 Null And Structured Lane Report

Command:

```bash
python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_null_structured_lanes.py
```

Status: `pass`

This report uses real `GRC9V3` fixed-topology continuity execution. It
does not call `step()`, spark expansion, growth, boundary behavior, birth,
or pruning.

## Lane Summary

| Lane | Budget | Source | Sink | Raw Cascades | Role-Gated Cascades | Claim Allowed | Topology Changed |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| U0 | True | False | False | 0 | 0 | False | False |
| U1 | True | True | False | 21 | 0 | False | False |
| U2 | True | False | False | 0 | 0 | False | False |
| S | True | False | False | 0 | 0 | False | False |

## Blocked Observations

- `U1`: `null_lane_shape_cascade_without_role_gate`. shape-only cascade evidence is insufficient; null lane remains blocked because measured source/sink role evidence fails
- `S`: `structured_lane_no_candidate_loop_claim`. the first fixed-topology structured initialization did not produce candidate loop evidence above null controls

## Interpretation

- U0/U1/U2 are null lanes and must not produce L4 positives.
- S is a structured lane; any positive result remains candidate-only
  while `same_parent_basin_mode = configured_parent_region_only`.
- Synthetic smoke results from Iteration 3 remain separate from these
  runtime traces.

## Errors

- none
