# B1-GR GRV6 Current Recurrence And Return Orbits

## Result

```text
mechanical_status = passed
current_control_branch_count = 48
cycle_control_branch_count = 16
cycle_seed_row_count = 32
cycle_seed_persistence_count = 0
maximum_post_step_cycle_component_l2 = 1.3498100806892346e-26
orbit_search_row_count = 1536
converged_search_candidate_count = 671
return_jacobian_ill_conditioned_count = 865
proper_divisor_rejected_count = 670
converged_but_not_return_count = 1
primitive_return_orbit_count = 0
ordinary_floquet_spectrum_count = 0
recurrence_evidence_opened = false
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

## Return-Orbit Search

The bounded search records all `1536` seeds
and roots: 256 candidates for each period 2, 3, 4, 5, 6, and 8, allocated
round-robin across all 48 accepted branches. It combines the already frozen
parameter envelope, GRV3 multiplier-continuation screening, and direct damped
return-residual minimization. Any period-p closure is rejected when period 1
or another proper divisor also closes. Physical-only and categorical/hybrid
returns have dedicated non-Floquet classifications.

Of the 1536 rows, 671 converge under the declared unregularized residual method. 670 are fixed points or lower-period closures and 1 fails the declared return tolerance. The remaining 865 rows are blocked by an ill-conditioned return Jacobian under the no-silent-regularization rule; they remain unresolved rather than counting as negative orbit evidence.

No primitive period-two-or-higher full causal-state return survives the proper-divisor and categorical gates in this bounded search. This is a search-envelope result, not a proof that recurrent orbits do not exist.

## Claim Boundary

Nonzero reconstructed current is not active circulation. Repeated transport
is not Read-Back, memory, or self-sustaining identity. GRV6 cannot assign
`GRV-C5` by itself; GRV7 threshold evidence remains required. No runtime,
`src/`, or existing-test change is part of this gate.

## Provenance

- Input execution revision: `69f1a11633a47bf7dc972f94bdd0c53aff6b15cb`
- GRV5 receipt: `a42ccda9772f5fa28e2e4681c2b5c6883a65499eaeab2badcc00ad31bb67ac35`
- GRV5 acceptance commit: `948db9b37069bc2a972f4bc2471287fa7140f677`
- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v6.json`
