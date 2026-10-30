# GRC9V4 connected A_RG2b completion specification

This optional numerical/domain binding implements
`P9-EC-A-RG2B-CONNECTED-COMPLETION`; native acceptance is separate.
See the [paper addendum](../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4-Connected-A-RG2b-Addendum.md)
and [bound contract](../implementation/phase-9-grcv4/tranche-8/P9-ARG2b-ConnectedCompletionContract.json).

Require a simple connected port-owned graph, unit reference measures/weights,
zero base tensor, the fixed-port Candidate-A backend, and the frozen A
coefficients: eta=kappa_c=tau_A=1, W_floor=kappa_Ah=1/2,
alpha=beta=gamma=2^-24, chi_A=1/16, zeta_A=1/2, kappa_H=1/2.
Check exact graph norms <=9/18/9 and every rational completion inequality.
No size, topology or current-only surrogate replaces these checks.

The auxiliary coordinates are (C,512 log W), with signed argument clamps
[-1,5] and [-1,1]. Readmission K is [-1/2,9/2] times [-3/4,3/4]; ordinary
K_minus is [-1/4,17/4] times [-5/8,5/8]. H is symmetric, star-supported and
within 2^-12 of I in induced infinity norm. Physical resources/history are
never clipped. Ordinary dt is exactly 2^-12; dt=0 only reconstructs/admit.

```json
{
  "schema_version": "grcv4-rg2b-params-v1",
  "extension_evaluator_id": "grc9v4_a_rg2b_connected_signed_argument_completion_v1",
  "containment_certificate_id": "grc9v4_a_rg2b_connected_degree_global_certificate_v1",
  "approximation_policy_id": "grc9v4_a_rg2b_chain4_sweeps18_factored_binary64_arb192_v1",
  "error_norm_id": "grc9v4_rg2b_hodge_induced_infinity_v1",
  "error_tolerance": 3.552713678800501e-15,
  "iteration_limit": 148,
  "failure_policy_id": "fail_closed_on_uncertified_section_v1"
}
```

Use four inverse levels, terminal H_4=I, eighteen complete sweeps and four
residual evaluations (148 charged evaluations). Proposals are binary64;
certificates use FLINT rational bounds and fixed 192-bit Arb. Validate exact
query, finite operands, terminal identity, symmetry, actual support and H
ball membership. Certify complete C/Y/H residuals, coupled error, represented
log-input error and infinite-section tail within the unchanged 2^-48 budget.
Use the direct log drive/expm1 writer proposal as declared by the policy.
Factoring B^TB as B-transpose times B is permitted; approximating its action
without a certificate is not. Squaring a zero-containing interval uses outward
multiplication. An inconclusive result fails explicitly with no fallback.

At every physical read/step, retain existing native current, conditioning,
continuity, writer and invariance checks. Both histories require independent
readmission; only current receives the ordinary write. Cache immutable graph
algebra only. Old tree17 identifiers retain their old domain and arithmetic.
The declared large companion preserves source resources and event allocation,
transports old W=1025/1024 and seeds new bonds at one. Its original reset
exclusion must remain visible; it is not repaired by clipping or a tolerance
change. No C1 debt closure, generic ATC or uniform trajectory tube is asserted.
