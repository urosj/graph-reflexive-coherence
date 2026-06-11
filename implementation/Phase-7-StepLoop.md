# Phase 7 GRC9V3 Step Loop

## Purpose

This document fixes the initial reference step loop for core `GRC9V3`.

It reconciles:

- the Phase 6 GRC9 mechanical loop,
- the Phase 5 GRCV3 semantic loop,
- and the hybrid requirements in `specs/grc-9-v3-spec.md`.

The loop is not a telemetry or visualization contract. It is the runtime order
that Phase T-GRC9V3 and Phase V-GRC9V3 observe from downstream artifact layers.

Current status: the core loop is implemented, and the later telemetry,
visualization, phenomenology discovery, and GRCL-9V3 source/lowering layers
have been completed without redefining this runtime order. See
[GRCL-9V3-Handoff.md](./GRCL-9V3-Handoff.md) for the final source-layer
handoff.

## Canonical Phase 7 Step Order

The baseline `GRC9V3.step()` should execute in this order:

1. `compute_row_basis_gradient_pre_flux`
   Rebuild gradient summaries in the fixed 3x3 port chart from the current
   coherence field and current occupied-port topology.

2. `compute_signed_hessian_row_basis_pre_flux`
   Rebuild signed Hessian summaries using the configured `hessian_backend` and
   apply the run-fixed Hessian sign convention. The default backend is the
   Eq. G3 row-basis diagonal form; the weighted least-squares backend is a
   comparison mode.

3. `compute_net_flux_summary_pre_flux`
   Build the lagged or current available row-basis net-flux summary used by the
   first tensor and metric pass.

4. `compute_node_tensors`
   Materialize hybrid node tensors from coherence, row-basis gradient,
   signed-Hessian summary, and net-flux summary.

5. `compute_base_conductance`
   Update scalar base conductance on occupied port-pairs.

6. `compute_edge_labels_pre_flux`
   Compute selected pre-flux analytic labels where applicable, especially
   geometric length and any label whose definition does not depend on the new
   flux field.

7. `compute_potential`
   Compute node potentials from current base conductance and coherence.

8. `compute_flux`
   Compute occupied-port-pair flux with deterministic orientation.

9. `compute_edge_labels_post_flux`
   Compute selected post-flux analytic labels, especially flux coupling and any
   temporal-delay proxy that requires current transport information.

10. `refresh_row_basis_differential_post_flux`
    Refresh net-flux summaries and any differential summary that must reflect
    the flux computed in this step.

11. `detect_flux_topology_identities`
    Rebuild successor map, sink set, and attraction basins from the transport
    state.

12. `validate_geometric_basin_seeds`
    Validate or seed basin identities from gradient and signed-Hessian
    conditions. The seed rule must implement both clauses of Eq. G7.

13. `compute_effective_basin_masses`
    Compute Appendix G effective basin mass `M_i` from current basin
    membership. In the baseline unit-measure mode this is the member coherence
    sum for each flux-topology/geometric basin. This step updates identity
    caches and representative basin-chart node state; it must not be treated
    as telemetry-only metadata.

14. `detect_hybrid_spark_candidates`
    Evaluate hybrid spark candidates:
    - GRC9 saturation gate,
    - basin-interior gate,
    - signed-Hessian degeneracy gate,
    - optional signed-crossing gate when the `spark_signed_crossing`
      capability is enabled.

15. `apply_mechanical_expansion`
    Apply GRC9 mechanical expansion for deterministic eligible candidates:
    - module construction,
    - column-preserving boundary reassignment,
    - coherence transfer under `expansion_distribution_mode`.

16. `refresh_after_expansion`
    Refresh identity and row-basis differential summaries on the changed
    topology.

17. `evaluate_child_basin_stabilization`
    Determine whether expansion produced at least one stable child basin or
    attractor.

18. `register_completed_hybrid_sparks`
    Register completed hybrid sparks only when stabilization passes. Candidate
    and mechanical expansion evidence must remain distinguishable.

19. `update_hierarchy`
    Update parent/child hierarchy, node depth, and basin identifiers for
    stabilized refinements.

20. `update_choice_collapse_learning`
    Update optional but required-by-spec event logic:
    - sink compatibility scores,
    - choice regimes,
    - collapse events,
    - persistent learning state change.

21. `apply_growth`
    Apply configured inactive-port growth if enabled for the hybrid runtime.

22. `apply_boundary_behavior`
    Apply `boundary_mode`.
    Baseline Phase 7 may execute `prune`. `barrier` and `ghost` require
    explicit `boundary_barrier` capability support.

23. `apply_continuity`
    Update coherence by flux divergence on the settled post-topology graph.

24. `enforce_quadrature_budget`
    Preserve `B = sum_i mu_i * C_i`, with unit measure as the baseline.

25. `refresh_runtime_state_final`
    Rebuild row-basis differential summaries, identity layers, hierarchy mass
    summaries, and registries that depend on post-continuity coherence.

26. `refresh_or_invalidate_coarse_cache`
    Refresh or invalidate column/coarse caches affected by topology or value
    updates.
    This step is cache hygiene only. It does not by itself implement the
    Section 9 column coarse-graining operator. The required operator surface is
    `coarse_grain_columns(...)` plus `split_columns(...)`; Phase 7 Iteration
    9.2 added that public GRC9V3 surface.

27. `compute_observables`
    Compute observables from the fully settled post-step state.

## Why This Loop Has Both Pre-Flux And Post-Flux Differential Passes

GRC9V3 inherits a key lesson from GRCV3: net flux is not a purely pre-step
quantity if it is stored as part of node semantics.

The pre-flux pass gives metric and potential computation a coherent starting
summary. The post-flux refresh updates row-basis net-flux summaries so identity
and spark semantics do not mix old differential state with new transport.

The final refresh is still required after continuity and budget enforcement,
because coherence changes can alter gradients, Hessians, basin seed validity,
and hierarchy mass summaries.

## Why Edge Labels Split Around Flux

GRC9 uses one edge-label step before flux. GRCV3 uses pre-flux and post-flux
label passes.

GRC9V3 should use the GRCV3-style split because:

- the family explicitly distinguishes `base_conductance` from analytic labels,
- `flux_coupling` is transport-dependent,
- temporal-delay labels may depend on selected transport quantities,
- and the hybrid runtime must keep label computation modes inspectable.

This does not make `temporal_delay` a Lorentzian proper-time field.

## Why Mechanical Expansion Is Not Completed Spark

In pure GRC9, a spark event and mechanical expansion are closely coupled.

In GRC9V3, this is not enough.

The hybrid rule requires:

- candidate detection from saturation plus basin/Hessian evidence,
- mechanical expansion,
- then post-event child-basin or attractor gain.

Therefore the loop separates:

- `detect_hybrid_spark_candidates`,
- `apply_mechanical_expansion`,
- `evaluate_child_basin_stabilization`,
- `register_completed_hybrid_sparks`.

This separation is the main guard against accidentally treating GRC9V3 as
GRC9 plus metadata.

## Why Hierarchy Updates Follow Stabilization

Mechanical expansion creates structure. It does not automatically create a
semantic parent/child hierarchy.

Hierarchy updates should happen only after stabilized child identity evidence
exists. This keeps the GRCV3 semantic layer tied to runtime-observed basin
structure rather than topology mutation alone.

## Why Choice / Collapse Happens Before Continuity

Choice/collapse state should be evaluated on the settled post-expansion
identity landscape before continuity changes the coherence field again.

The event layer therefore sees:

- current transport,
- current identity structure,
- newly stabilized hierarchy,
- and current compatibility scores.

Learning can then register persistent state change before the next coherence
update is applied.

If later evidence shows that collapse should be evaluated after continuity for
a specific backend, that backend must document the order and expose it in
telemetry. It should not silently replace the baseline loop.

## Boundary And Growth Placement

Growth remains after the hybrid semantic event stages because growth changes
topology and should not retroactively affect whether the just-expanded module
stabilized a child basin.

Boundary behavior precedes continuity so continuity is evaluated on the graph
that survives regularization for this step.

## Budget Placement

Quadrature budget enforcement remains after continuity and topology changes.

The invariant is:

```text
B = sum_i mu_i * C_i
```

with `mu_i = 1` in baseline unit-measure mode.

If non-unit measures are introduced, the budget stage must correct weighted
mass. Expansion transfer must also preserve weighted mass.

## Basin Mass Correctness

The identity stage must maintain the full Appendix G basin-attribute bundle.
In particular, `basin_mass` / `M_i` is not an authored seed constant and not a
checkpoint-only convenience field. It is a runtime quantity derived from the
current basin membership:

```text
M_b = sum_{i in basin(b)} mu_i C_i
```

The Phase 7 baseline uses `quadrature_mode = "unit_measure"`, so `mu_i = 1`
unless a future non-unit measure mode is explicitly implemented. The identity
refresh must therefore cache basin masses and update representative basin-chart
nodes after flux-topology and geometric basin assignment. Downstream telemetry
and visualization may mirror this value, but they must not be the source of
truth for it.

## Baseline Non-Claims

This step loop does not claim:

- host embedding frame,
- Lorentzian causal layer,
- anisotropic edge transport,
- multiscale sigma dynamics,
- barrier/ghost boundary behavior,
- or GRCL/source-language lowering for GRC9V3 as part of the runtime loop.

GRCL-9V3 source-language lowering is now implemented downstream of the runtime
loop. Barrier/ghost boundary behavior and the other capability-gated items
still require explicit later runtime support.
