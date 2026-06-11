# Phase 5 GRCV3 Step Loop

## Purpose

This note fixes the exact Phase 5 reference `GRCV3` step loop in one place.

The representative runtime seed used in Iteration 11 is intentionally simple,
but the step loop itself is not a reduced or "minimal" loop. It is the
paper-facing reference baseline that later runtime lanes, telemetry, and
`GRC9V3` hybrid work should inherit unless a later phase explicitly revises it.

## Canonical Phase 5 Step Order

The current `GRCV3.step()` executes the following order:

1. `compute_differential_summary_pre_flux`
   Rebuild basin attributes from the current coherence field and current flux
   state so the step starts from a consistent local differential summary.

2. `compute_node_tensors`
   Materialize the node tensor from coherence, gradient, and net-flux summary.

3. `compute_metric`
   Update edge conductance using the Phase 5 constitutive metric law.

4. `compute_edge_labels_pre_flux`
   Compute pre-flux edge labels such as geometric length.

5. `compute_potential`
   Compute node potentials from conductance-weighted coherence differences and
   the selected site potential derivative.

6. `compute_flux`
   Compute antisymmetric edge flux from potential differences.

7. `compute_edge_labels_post_flux`
   Compute post-flux edge labels such as flux coupling and temporal delay.

8. `refresh_differential_summary_post_flux`
   Rebuild basin attributes again so `net_flux` and derived differential state
   reflect the flux field just computed in this same step.

9. `detect_identities`
   Rebuild sink/basin state and geometric-basin validation.

10. `detect_sparks`
    Detect spark candidates and apply immediate soft-split initialization plus
    attractor-count confirmation checks.

11. `advance_splits`
    Advance any active soft splits by one deterministic progress increment and
    re-evaluate attractor-gated spark completion.

12. `update_choice_state`
    Rebuild optional choice/collapse state under the selected choice backend.

13. `apply_continuity`
    Update coherence by flux divergence.

14. `enforce_budget`
    Clamp negative coherence, preserve the target budget, and record bounded
    remainder if exact closure cannot be completed.

15. `refresh_runtime_state`
    Rebuild differential, transport, identity, and hierarchy state so the
    stored post-step state is self-consistent rather than half-pre / half-post.

16. `compute_observables`
    Compute observables from the fully refreshed post-step state.

## Why The Loop Has Two Differential Passes

The double differential rebuild is intentional.

The first pass gives the metric and potential layers a coherent starting point.
The second pass is required because `net_flux` is a post-flux quantity in the
Phase 5 baseline, not a lagged previous-step cache. Without the second pass,
the stored node tensor and geometric identity diagnostics would mix old
differential state with new transport state.

## Why The Loop Has A Final Refresh

After continuity and budget enforcement, the node coherence field has changed.
That means:

- gradients may have changed
- Hessians may have changed
- net-flux summaries may need recomputation
- geometric basin validation may have changed
- hierarchy mass summaries may have changed

The final refresh ensures the stored state at `step_index + 1` is an actual
post-step state, not just a coherence update layered on top of stale
diagnostics.

## Budget Closure Heuristic

The Phase 5 baseline currently uses a deterministic budget-correction
heuristic.

After continuity:

- negative node coherence is clamped to `0.0`
- if mass must be added back to reach `budget_target`, the entire positive
  correction is assigned to the first live node in sorted node-id order
- if mass must be removed to reach `budget_target`, removal proceeds
  sequentially in sorted node-id order until the deficit is cleared
- any residual amount that cannot be closed exactly is recorded in
  `state.remainder`

This is a constitutive implementation choice for the current baseline. It is
deterministic and easy to replay, but it should not be mistaken for the only
possible budget-closure rule.

## Signed Hessian Stability Rule

The Phase 5 baseline treats `s_H` as run-fixed once established:

- if snapshot state already provides a valid `hessian_sign`, that value is
  reused
- otherwise the first valid basin-attribute rebuild calibrates `s_H`
- later basin-attribute rebuilds reuse the stored value rather than
  recalibrating silently
- if the calibration scores for `+1` and `-1` tie exactly, `+1` wins

That means the tie-break rule is operational at initialization or snapshot
restore time, but it is not a per-step sign-flip mechanism in the current
runtime loop.

## Phase 5 Boundary

This loop is the canonical Phase 5 baseline, but not the final possible `GRCV3`
loop forever.

Later phases may still add:

- additional choice-score backends
- alternative Hessian backends
- richer learning / persistent deformation updates
- more expressive boundary-event handling

Those are extensions. They should not silently replace the semantics fixed here.
