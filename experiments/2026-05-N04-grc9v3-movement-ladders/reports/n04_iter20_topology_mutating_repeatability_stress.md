# N04 Iteration 20 Topology-Mutating Repeatability And Stress

Status: **passed**

Claim ceiling: `topology_mutating_movement_candidate`

Stress result: `repeatability_stress_supported`

Iteration 20 stresses the 19-E topology-mutating movement candidate without promoting choice, identity, agency, locomotion-like, biological, inherited-N03, or unrestricted movement claims.

## Lanes

- repeated native attempts passed: `3/3`
- reversed matched lane: `passed`
- perturbation lane: `passed`
- multiple topology events in one run: `passed`
- multiple topology runtime passed: `True`
- multiple topology artifact replay passed: `True`

## Multiple Topology Events

- topology events: `4`
- reabsorption records: `2`
- surface lineage records: `5`
- scheduled events: `['lgrc9v3-packet-event-404fa41884262268', 'lgrc9v3-packet-event-bb5398431f9105fd']`
- duplicate reabsorption digests: `False`
- artifact replay boundary: `None`
- artifact replay failures: `[]`

## Checks

- `iteration_19e_baseline_passed`: `True`
- `repeated_topology_mutating_runs_passed`: `True`
- `reversed_matched_lane_passed`: `True`
- `lineage_accounted_perturbation_lane_passed`: `True`
- `multiple_committed_topology_events_runtime_passed`: `True`
- `multiple_committed_topology_events_artifact_replay_passed`: `True`
- `multiple_committed_topology_events_boundary_recorded`: `False`
- `multiple_committed_topology_events_replay_closed_or_boundary_recorded`: `True`
- `artifact_only_replay_preserved`: `True`
- `exact_budget_preserved`: `True`
- `claim_boundary_preserved`: `True`

## Boundary

Iteration 20 shows that the 19-E topology-mutating movement candidate repeats across matched native runs, survives a matched reversed lane, survives a lineage-accounted transfer perturbation, and handles two committed topology events in one run with artifact-only replay and exact budget. This is stress support for the existing candidate, not native choice, RC identity collapse, agency, locomotion-like behavior, or unrestricted movement.

## Command

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_n04_iter20_topology_mutating_repeatability_stress.py
```
