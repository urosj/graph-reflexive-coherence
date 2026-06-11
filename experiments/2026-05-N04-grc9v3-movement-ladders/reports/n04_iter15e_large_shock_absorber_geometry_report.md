# N04 Iteration 15-E Large-Shock Absorber Geometry

Status: **passed**

Claim ceiling: `large_shock_absorber_same_family_recovery_candidate`

Iteration 15-E tests a same-family absorber geometry against the 0.15 shock.

## Absorber Summary

- challenge perturbation: `0.15`
- full recovery window scheduled: `True`
- source-budget exhaustion avoided: `True`
- R6 polarity restoration passed: `True`
- T6 centroid restoration passed: `True`
- directions recovered: `['forward', 'reversed']`
- cost metric: `total_redistribution_load_per_cycle`
- cost per feedback cycle: `0.1`

The large-shock absorber geometry restores the 0.15 shock in both directions by combining central source capacity with fixed recovery channels to boundary absorber nodes. Recovery still occurs through native packet events, surface rows, feedback eligibility, scheduled packet work, and step() mutation.

Topology note: the absorber recovery channels are declared in the fixture before the run. Runtime topology remains fixed; no topology mutation occurs during execution.

Centroid note: raw centroid deltas use increasing S0 chain index. Signed centroid deltas are direction-normalized, so positive means recovery in the lane's declared direction for both forward and reversed lanes.

Cost note: recovery cost uses the Iteration 15 native feedback packet cost metric and packet amount; 15-E does not introduce a new cost schedule.

## Checks

- `iteration_15c_available`: `True`
- `iteration_15d_available`: `True`
- `candidate_absorber_geometry_declared_before_run`: `True`
- `challenge_perturbation_is_0_15`: `True`
- `native_surface_semantics_unchanged`: `True`
- `native_feedback_producer_semantics_unchanged`: `True`
- `absorber_initialization_budget_neutral`: `True`
- `topology_fixed_during_run`: `True`
- `fixture_topology_changed_before_run`: `True`
- `no_runtime_topology_mutation_observed`: `True`
- `no_forbidden_direct_writes`: `True`
- `artifact_validators_passed`: `True`
- `budget_and_nonnegative_gates_passed`: `True`
- `identity_shape_gates_passed`: `True`
- `source_budget_exhaustion_avoided`: `True`
- `r6_polarity_restoration_passed`: `True`
- `t6_centroid_restoration_passed`: `True`
- `cost_scaling_inherited_from_iteration_15`: `True`
- `broader_claims_blocked`: `True`

## Go/No-Go

- `iteration_16_allowed`: `True`
- `entry_ceiling_for_geometry_transfer`: `large_shock_absorber_same_family_recovery_candidate`
- `iteration_16_fixture_guidance`: `test absorber-informed corridor/widened-chain geometry`

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter15e_large_shock_absorber_geometry.py
```
