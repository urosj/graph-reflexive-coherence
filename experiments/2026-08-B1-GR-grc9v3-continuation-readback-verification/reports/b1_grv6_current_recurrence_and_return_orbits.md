# B1-GR GRV6 Current Recurrence And Return Orbits

## Result

```text
mechanical_status = passed
current_control_branch_count = 48
cycle_control_branch_count = 16
cycle_seed_row_count = 32
cycle_seed_persistence_count = 0
maximum_post_step_cycle_component_l2 = 1.3498100806892346e-26
symmetric_exact_zero_control_count = 16
finite_activity_amplitude_ladder_row_count = 192
cycle_activity_amplitude_ladder_row_count = 64
cycle_seed_stage_trace_pair_count = 16
orbit_search_row_count = 1536
converged_search_candidate_count = 671
return_jacobian_ill_conditioned_count = 865
proper_divisor_rejected_count = 670
converged_but_not_return_count = 1
boundary_state_candidate_count = 1
boundary_state_classifications = ['budget_projection_supported_current_state']
primitive_return_orbit_count = 0
ordinary_floquet_spectrum_count = 0
recurrence_evidence_opened = false
review_points_accounted_for = 36
current_result_requirements_executed_or_satisfied = 22
positive_candidate_requirements_conditionally_deferred = 14
scientific_acceptance = awaiting_human_review
```

## Edge-Space And Current Controls

The primary cycle decomposition uses the native inverse-conductance metric
on the sorted live-edge order with each edge oriented from its stored
`node_u` endpoint to `node_v`. Every branch passes projector algebra, native
potential-flow annihilation, and coordinate-reorientation covariance.
All 16 triangle branches admit a one-dimensional cycle space. Their positive
and negative divergence-free cycle seeds are certified before execution and
are overwritten by the native potential-flow reconstruction after one complete
step. The sign-even conductance response is recorded separately from the
reconstructed current. This excludes stationary cycle-current persistence in
the tested envelope; it does not prove global absence on every GRC topology.

Exact-zero rows are interpreted relative to present coherence. Zero remains
zero on symmetric homogeneous branches; a nonuniform coherence profile may
reconstruct a nonzero potential current without constituting spontaneous
symmetry breaking. Positive and negative old-current seeds test orientation
retention, while their matched squared write tests sign-even preparation.
The hardening matrix separately certifies 16 genuinely symmetric F1
exact-zero states and classifies nonsymmetric zero-input rows without
calling their bounded reconstructed potential-flow residual spontaneous
orientation selection.

Four preregistered activity levels are run in both signs for every branch
and for every cycle-capable branch. The stage-local conductance response
matches the native quadratic old-current law, no ladder row requires budget
projection, a conductance floor, an event, or topology change, and all 16
cycle branches have public-method traces through every current-reading or
current-overwriting stage. Those traces match the complete native step and
locate orientation erasure at the first transport reconstruction.

## Return-Orbit Search

The bounded search records all `1536` seeds
and roots: 256 candidates for each period 2, 3, 4, 5, 6, and 8, allocated
round-robin across all 48 accepted branches. The frozen allocation restarts
at branch zero for each period: each F1 branch therefore receives 36 rows
and each F2/F3 branch receives 30. This modest bias toward the simplest
fixture is disclosed rather than changed after outcomes were observed.
The search combines the already frozen
parameter envelope, GRV3 multiplier-continuation screening, and direct damped
return-residual minimization. Any period-p closure is rejected when period 1
or another proper divisor also closes. Physical-only and categorical/hybrid
returns have dedicated non-Floquet classifications.

Of the 1536 rows, 671 converge under the declared unregularized residual method. 670 are fixed points or lower-period closures and 1 fails the declared return tolerance. The remaining 865 rows are blocked by an ill-conditioned return Jacobian under the no-silent-regularization rule; they remain unresolved rather than counting as negative orbit evidence.

Fixture-stratified resolution is:

| Fixture | Search rows | Resolved | Ill-conditioned | Blocked fraction |
| --- | ---: | ---: | ---: | ---: |
| `F1` | 576 | 459 | 117 | 20.3% |
| `F2` | 480 | 116 | 364 | 75.8% |
| `F3` | 480 | 96 | 384 | 80.0% |

The unresolved set is concentrated on F2/F3. The result therefore says
more about the F1 fixed-point neighborhood than recurrent dynamics on the
richer fixtures. Every ill-conditioned row carries its finite-difference
step, singular values, condition result and threshold, residual, Jacobian
digest, and explicit `regularization_applied = false` record.

No primitive period-two-or-higher full causal-state return is admitted among the 671 resolved candidates in the preregistered branch-relative `(C,W)` chart with native current reconstruction and full-state admission. This is a search-envelope result, not a proof that recurrent orbits, including relative periodic or old-`J`-dependent orbits not searched here, do not exist.

## Boundary-State Diagnostic

The sole reduced-coordinate convergence with a full-state failure was replayed from its beat-one complete state locally, after snapshot/load, and in a fresh process. It is retained as a boundary-state diagnostic, not a return orbit.

- Source row: `p08-s243` on `grv2-f1-004`
- Classification: `budget_projection_supported_current_state`
- Budget projection active: `true`
- Positivity boundary active: `true`
- All replay modes equal: `true`
- Old-current reset changes the next physical future: `false`
- `T-A05` contradiction candidate: `false`

The row is a one-beat entry into a reproducible nonzero potential-current
state supported by the admissible coherence-simplex projection. Its old
current is overwritten by native reconstruction and is not admitted as an
independent causal coordinate. It does not satisfy the unconstrained
stationary-current envelope of `T-A05`, open recurrence evidence, or
retroactively expand the frozen search chart.

## Review Accounting

All 36 review points are accounted for. 22 current-result requirements were executed or satisfied; 14 positive-candidate requirements remain conditionally deferred because no orbit was admitted. Deferred controls were not executed and remain mandatory for any future positive candidate.

## Claim Boundary

Nonzero reconstructed current is not active circulation. Repeated transport
is not Read-Back, memory, or self-sustaining identity. GRV6 cannot assign
`GRV-C5` by itself; GRV7 threshold evidence remains required. No runtime,
`src/`, or existing-test change is part of this gate.

## Provenance

- Input execution revision: `1def2aeab3f2ec50bff411a5d89c2d391c586466`
- GRV5 receipt: `a42ccda9772f5fa28e2e4681c2b5c6883a65499eaeab2badcc00ad31bb67ac35`
- GRV5 acceptance commit: `948db9b37069bc2a972f4bc2471287fa7140f677`
- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v6.json`
