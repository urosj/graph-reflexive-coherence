# B2-GR Iteration 3 - Active Nulls And Failure Baselines

## Result

```text
status = passed
acceptance_state = awaiting_scientific_review
checks = 29/29 passed
failed_checks = []
active_null_rows = 52
failed_closed_rows = 52
failed_open_rows = 0
B2_positive_evidence_opened = false
GRR_rung_assigned = false
B2_closeout_ceiling = B2-C2-ready
```

## Admission Boundary

All 52 frozen I2 false-positive paths are instantiated exactly once. `failed_closed` means the blocker triggered and the dependent claim was rejected; it does not mean that a positive scientific control failed. These rows are deterministic admission fixtures, not runtime measurements, source-current candidate evidence, or replay evidence.

The null surface covers temporal/spectral relabels, branch relation and search coverage, formation provenance and full-path cleanliness, probe provenance and matched mediation, reset/swap/bypass semantics, carrier lineage/equivalence, and selection/threshold/claim governance.

## Threshold Calibration

The four I2 calibration recipes were instantiated from preregistered deterministic null fixtures. Their uncertainty bases are inherited replay tolerances, except for the dimensionless occupancy floor, which uses the frozen minimum floor divided by the safety multiplier. They are pre-positive admission floors, not empirical noise estimates. Every later candidate still must apply its row-local numerical uncertainty and the stronger frozen I2 margin rule. No runtime measurement or positive evidence was opened by calibration.

- `formation_contrast_floor_v1` = `0.000000001000` (usable)
- `formation_specific_occupancy_excess_floor_v1` = `0.000100000000` (usable)
- `oriented_interaction_component_floor_v1` = `0.000000001000` (usable)
- `control_target_residual_ceiling_v1` = `0.000000010000` (usable)

## Decision

I3 is mechanically ready for scientific review. Human acceptance may assign `B2-C2` and open I4 native preparation/reachability search. It cannot assign a GRR rung or support constructibility by itself.

Artifact payload SHA-256: `7260e5e2e1b23a97554107ad72f39f47f0e758a84797d5a9e3931ce1f5b97e0b`
