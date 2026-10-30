# GRC9V4 connected C_RG2b completion specification

Selected for bounded implementation on 2026-10-30 under
`P9-EC-C-RG2B-CONNECTED-COMPLETION`. This optional numerical/domain binding
supplements the existing GRCV4 RG2b and GRC9V4 contracts. Native conformance
is a forward obligation; this document adds no accepted public population.

Use only simple connected port-owned graphs, unit vertex measures and edge
weights, zero base tensor, and the frozen C coefficients of the connected
completion contract. Check all graph-specific inequalities in the paper
addendum with exact FLINT rational arithmetic: selector, reference resolvent,
signed-chart containment, section self-map, Lipschitz class, contraction and
finite tail. A size cap alone is insufficient. Cache only exact immutable
graph algebra; state, selected sections and inverse histories must be fresh.

The signed auxiliary clamp is [-1,5], K_minus=[-1/4,17/4], K=[-1/2,9/2].
Only increment/source evaluation arguments are clamped. Physical inputs,
returned states and authoritative resources must never be clipped.
H is symmetric and star-supported; its induced-infinity distance from I is
at most 2^-12. The section Lipschitz bound is 2^-10; ordinary dt is 2^-12.

The profile's realization parameters are:

```json
{
  "schema_version": "grcv4-rg2b-params-v1",
  "extension_evaluator_id": "grc9v4_c_rg2b_connected_signed_argument_completion_v1",
  "containment_certificate_id": "grc9v4_c_rg2b_connected_resolvent_global_certificate_v1",
  "approximation_policy_id": "grc9v4_c_rg2b_chain6_sweeps18_vertex_binary64_arb192_v1",
  "error_norm_id": "grc9v4_rg2b_hodge_induced_infinity_v1",
  "error_tolerance": 3.552713678800501e-15,
  "iteration_limit": 222,
  "failure_policy_id": "fail_closed_on_uncertified_section_v1"
}
```

Reconstruct each current/reset section independently. Use terminal H_6=I,
six inverse levels and eighteen complete sweeps, followed by six independent
residual evaluations (222 charged evaluations total). Proposal work is
binary64, using the algebraically equivalent vertex system. Fixed 192-bit
Arb certifies the full signed-state and H-matrix residuals, coupled inverse
error and infinite-section tail. Validate exact query, terminal identity,
finite binary64 operands, symmetry, actual star support and matrix-ball
membership before certification. No warm start from a previous physical step.

The final section error must not exceed 2^-48. Existing native current,
conditioning, represented continuity, source/geometry and invariance checks
still apply; a research certificate cannot replace any native check.
Readmission runs at dt=0 on K; positive ordinary steps require both roles in
K_minus. Section/inverse work is neither authoritative history nor elapsed
physical time. Failure is explicit and atomic, with no solver/backend or
precision fallback. The unresolved C1 debt and all existing claim ceilings
remain unchanged. Old tree17 policy identifiers preserve their old domain.

Source: [paper addendum](../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4-Connected-RG2b-Addendum.md) and
[bound contract](../implementation/phase-9-grcv4/tranche-8/P9-CRG2b-ConnectedCompletionContract.json).
