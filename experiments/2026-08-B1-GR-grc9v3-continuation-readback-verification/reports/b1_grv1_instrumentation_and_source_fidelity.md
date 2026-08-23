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

## Observation And Replay Integrity

The instrumented and ordinary steps produce exactly equal complete
runtime snapshots. Every high-level call records its ordinal, input
digest, output digest, and changed top-level fields. An experiment-local
replay of the current public stage sequence matches every captured stage
boundary and the final state. Snapshot capture, diagnostic reads, hashing,
save, and load do not mutate the observed source model. Same-input runs
also agree across reset-to-input reuse, a fresh instance, snapshot/load,
and a fresh Python process.

## Source-Fidelity Findings

- Structurally valid small, moderate, and large diagonal K interventions
  produce exact non-K transport equality, and the first differential
  stage overwrites them before full-step use. This is a fixed-topology,
  no-event F0 result; it is not a global K-causality claim.
- Prior current magnitude has a direct sign-even `J^2` path into the next
  conductance. Under F0 its measured effect is below the declared `W`
  tolerance, so GRV1 records the source path without promoting a resolved
  magnitude-retention claim.
- The stagewise `J -> -J` trace shows sign in the pre-transport net-flux
  summary, exact sign-even conductance and potential, equal reconstructed
  current, and final equality after the later differential refresh.
- Reversing the edge coordinate while mapping `J -> -J` preserves physical
  transport exactly; the coordinate transform is explicitly involutive.
  Coordinate covariance is distinct from physical current reversal.

## Surface Authority

Mismatch controls identify `state.base_conductance` as authoritative for
potential/flux when present, and `state.port_edges[*].flux_uv` as the
authoritative old-current input. Edge conductance, oriented-flux cache,
net-flux summaries, and flux coupling are duplicate, fallback, or derived
surfaces with separately recorded rebuild and overwrite stages. K has no
identified consumer on the tested path. The full map is emitted as
`outputs/surface_authority_map.json`.

## Current Classification

```text
magnitude = direct_sign_even_input_to_next_conductance_but_F0_effect_below_declared_W_tolerance
axis = single_edge_sign_even_channel_only_not_distinct_from_magnitude
orientation = not_retained_across_transport_or_complete_step
current_reconstructed_anew = true
K_cache = not_consumed_on_tested_F0_fixed_topology_no_event_path
```

## State Closure Handoff

Every `GRC9V3State` dataclass field is classified. Causal and mixed
runtime fields remain explicit GRV3 closure candidates; exclusion from
the physical projection is not treated as proof of causal irrelevance.
The transition environment is recorded separately from dynamic state,
and RNG remains classified as causal even though it does not advance in
the lambda-birth-zero F0 envelope.
The protected-path v1 manifest is an unchanged successor to v0. Any later
load-bearing-path discovery must route through
`source_or_specification_mismatch`; v1 cannot be amended silently.

## Claim Boundary

GRV1 supports exact bounded runtime dependency and coordinate/orientation
semantics only. It does not establish a formed branch, continuation,
retention, read-back, or write-back.
