# Phase 7 Mid-Gate Review

## Purpose

This review checks whether the current `GRC9V3` implementation remains a
truthful hybrid before representative runtime evidence is built.

The gate is intentionally about boundaries, not about producing new evidence
lanes. Iteration 8 should start only after the implementation can still be read
as:

- GRC9 mechanics on a nine-slot port graph,
- GRCV3 semantic state lifted onto that substrate,
- and explicit GRC9V3-only behavior where the two interact.

## Reviewed Scope

Reviewed implementation surfaces:

- `src/pygrc/models/grc_9_v3.py`
- `src/pygrc/models/grc_9_v3_state.py`
- `src/pygrc/models/grc_9_v3_runtime.py`
- `src/pygrc/models/grc_9_v3_sparks.py`
- `src/pygrc/models/grc_9_v3_choice.py`

Reviewed planning surfaces:

- `implementation/Phase-7-ImplementationPlan.md`
- `implementation/Phase-7-EquationMap.md`
- `implementation/Phase-7-StepLoop.md`
- `implementation/Phase-7-ImplementationChecklist.md`

## GRC9 Mechanics Remain Separately Inspectable

The GRC9 substrate remains explicit in the `GRC9V3State` shape:

- `topology` is a `PortGraphBackend`.
- `port_edges` are keyed by occupied port-pair edges.
- mechanical expansion uses the GRC9 expansion helpers:
  `compute_expansion_node_count`, `normalize_expansion_weights`,
  `boundary_reassignment_order`, `aggregate_bond_conductance`, and the
  canonical core/satellite column layout.
- expansion records preserve parent sink id, module node ids, distribution
  weights, expansion step, and optional schedule.
- growth uses inactive port slots, outward flux pressure, `lambda_birth`,
  `alpha_seed`, and `w_bond`.

This means the nine-slot mechanics are not hidden inside GRCV3 semantic
metadata.

## GRCV3 Semantic Fields Remain Separately Inspectable

The semantic layer remains explicit on each `GRC9V3NodeState`:

- `gradient_row_basis`
- `signed_hessian_row_basis`
- `net_flux_summary`
- `basin_mass`
- `basin_id`
- `parent_id`
- `depth`

Runtime caches also preserve the semantic diagnostics separately:

- row neighborhoods,
- unsigned row-basis Hessian,
- weighted least-squares comparison Hessian,
- row mismatch sums,
- current and previous minimum signed-Hessian summaries,
- geometric identity seed diagnostics,
- choice/collapse registries,
- hierarchy state,
- and quadrature budget summaries.

The weighted least-squares Hessian remains available as a named comparison
backend, while `row_basis_diagonal` remains the baseline GRC9V3 equation path.

## Hybrid-Only Behavior Is Explicit

The implementation names the behaviors that exist only in the hybrid family:

- `hybrid_spark_candidate`
- `hybrid_mechanical_expansion`
- `hybrid_spark_completed`
- post-expansion child-basin stabilization
- hierarchy updates from completed hybrid sparks
- choice/collapse over GRC9 port-flux successor structure
- GRC9 inactive-port growth using GRCV3-style runtime state and budget closure

The step loop records the difference between:

1. candidate detection,
2. mechanical expansion,
3. post-expansion refresh,
4. child-basin stabilization,
5. completed hybrid spark registration.

That distinction is the main protection against treating pure GRC9 expansion as
if it had already proven GRCV3-style child identity semantics.

## Optional Capabilities Are Not Over-Claimed

`GRC9V3_CAPABILITY_PROFILE` lists the following optional capabilities:

- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

The runtime does not claim them from `list_capabilities()`. It currently claims
only required baseline capabilities from the profile.

The parameter resolver rejects `boundary_mode = "barrier"` and
`boundary_mode = "ghost"` for this phase. This is the correct current behavior:
those modes require explicit `boundary_barrier` runtime support and should not
be made available by configuration alone.

`temporal_delay` is computed as an analytic edge label, not as a Lorentzian
causal layer. Scalar base conductance remains the transport path; no anisotropic
edge transport is claimed.

## Deferred Runtime Surface

The following surfaces remain deferred after Iteration 7:

- barrier and ghost boundary modes,
- Lorentzian causal semantics,
- anisotropic edge transport,
- multiscale sigma fields,
- non-unit quadrature measures,
- richer curvature backends beyond the current `none` path,
- adiabatic expansion scheduling beyond preserved schedule storage,
- Phase T-GRC9V3 telemetry contract and replay lanes,
- Phase V-GRC9V3 visualization,
- GRC9V3 phenomenology discovery catalogs,
- GRCL/source-seed lowering for GRC9V3.

These are downstream surfaces and should not be silently folded into core
closeout.

## Follow-Up Before Closeout

No blocker prevents Iteration 8 from starting.

Recommended Iteration 8 focus:

- build one representative hybrid fixture that exercises the full step loop,
- build the Appendix E-style cell-division fixture as an evidence target,
- record deterministic replay commands and final snapshot digests,
- keep Phase T/V-grade telemetry and visualization out of core Phase 7.

## Gate Decision

Iteration 7 passes the mid-gate review.

The current implementation is a truthful executable `GRC9V3` hybrid: GRC9
mechanics, GRCV3 semantic state, and hybrid-only events remain separately
inspectable, and optional capabilities are not over-claimed.
