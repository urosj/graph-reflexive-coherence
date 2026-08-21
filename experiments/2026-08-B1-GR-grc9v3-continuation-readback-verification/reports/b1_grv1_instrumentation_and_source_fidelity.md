# B1-GR GRV1 Instrumentation And Source Fidelity

## Result

```text
mechanical_status = passed
scientific_acceptance = awaiting_human_review
candidate_closeout_ceiling = GRV-C2
runtime_change = false
positive_evidence_opened = false
```

GRV1 reproduces the canonical F0 transport anchor through current
runtime methods and independently observes the high-level call sequence
without changing the resulting physical projection. The emitted step
trace matches the frozen canonical order, topology remains fixed, and no
events occur.

## Source-Fidelity Findings

- The materialized hybrid tensor cache is diagnostic for transport:
  changing it does not alter transport, and the first differential stage
  overwrites it before a full step can consume the counterfactual value.
- Prior current magnitude has a direct sign-even `J^2` path into the next
  conductance. Under F0 its measured effect is below the declared `W`
  tolerance, so GRV1 records the source path without promoting a resolved
  magnitude-retention claim.
- Physical `J -> -J` leaves transport and complete-step projections equal.
  A pre-transport net-flux summary tracks sign, but transport reconstructs
  current and the later refresh overwrites that transient summary.
- Reversing the edge coordinate while mapping `J -> -J` preserves physical
  transport exactly. Coordinate covariance is therefore distinct from the
  negative old-current orientation result.

## Current Classification

```text
magnitude = direct_sign_even_input_to_next_conductance_but_F0_effect_below_declared_W_tolerance
axis = single_edge_sign_even_channel_only_not_distinct_from_magnitude
orientation = not_retained_across_transport_or_complete_step
current_reconstructed_anew = true
K_cache = diagnostic_only_not_transport_input
```

## State Closure Handoff

Every `GRC9V3State` dataclass field is classified. Causal and mixed
runtime fields remain explicit GRV3 closure candidates; exclusion from
the physical projection is not treated as proof of causal irrelevance.
The protected-path v1 manifest is an unchanged successor to v0. Any later
load-bearing-path discovery must route through
`source_or_specification_mismatch`; v1 cannot be amended silently.

## Claim Boundary

GRV1 supports exact bounded runtime dependency and coordinate/orientation
semantics only. It does not establish a formed branch, continuation,
retention, read-back, or write-back.
