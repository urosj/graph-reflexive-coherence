# D11-C Candidate C Baseline Transport and Mobility Closure

**Gate:** D11-C
**Status:** Open, preregistered
**Predecessor:** `GRC9V4-CD-D11-OPEN-v1`
**Preregistration digest:** `c1c22c88fa676705370d01256a34801a364e310c93e4ef85cc5a3208e6e06a78`
**Inherited authority:** [`GRC9V4-CD-D11-CLAIM-DEBT-ROUTING-v1`](D11ClaimDebtAndAuthorityRouting.md)
**Local debt:** `D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY`
**Result selected:** No

## Gate Question

What exact graph-generic Candidate C law produces the direct baseline current

$$
J_{0,C}(C,T_C,h,U)
$$

for all five Candidate C realizations while preserving the accepted separation
between transport mobility, retained-sector Hodge geometry, and structural
geometry?

This is a constitutive closure, not a notation repair. `C_CI`, `C_OS`,
`C_RG2b`, `C_PC`, and `C_CI_PC` all consume $J_{0,C}$, but the accepted source
population does not define the producing map.

The gate carries the complete D10.2 entry state: 39 current claims, 29
historical claim nodes, 29 transformed debts, and 11 verification obligations.
Its detailed claim bearings are consistency constraints, not claim
reclassifications. The D11-C debt is additive to that inherited topology.

## Accepted Boundary

The investigation inherits these constraints unchanged:

- $C$ is Candidate C's only authoritative candidate state. $T_C$, mobility,
  potential, Hodge surfaces, and $J_{0,C}$ remain derived or transient.
- $J_{C,C}=J_{0,C}+\zeta_Cj_{C,\mathrm{flux}}$ remains the total-current
  architecture.
- $\kappa_{M,C}=0$ removes selected-sector conditioning from the direct
  baseline path.
- $\chi_C=0$ removes the explicit Read-Back current but preserves the direct
  conditioned baseline.
- $\zeta_C=0$ leaves $J_{C,C}=J_{0,C}$ and makes any read diagnostic only.
- $M_{4,C}$ is a candidate-specific transport operator on physical current
  space. It is not $H_{1,\mathrm{form}}$, $G_J$, $G_J^{-1}$, or $h_4$ merely
  because dimensions or matrix representations coincide.

The gate reopens only the Candidate C direct transport chain and its bounded
downstream uses. It does not reopen Candidate A, the common charge/resource
contract, Read-Back typing, or the five realization identities except where
their C rows require the newly selected baseline law.

## Required Closure Surface

An accepted result must freeze all of the following as one profile-identity
package:

1. the type, domain, codomain, positivity, and authority of $M_{4,C}$;
2. the potential or other direct driving functional;
3. the exact $J_{0,C}$ equation;
4. dependence on $C$, $T_C$, $h$, $U$, and resolved parameters;
5. units, gauge, normalization, regular domain, and singular boundary;
6. the pre-read stage and freshness rule for CI, OS, RG2b, PC, and CI+PC;
7. graph-relabel and signed-edge-orientation covariance;
8. exact $\kappa_{M,C}=0$, $\chi_C=0$, and $\zeta_C=0$ controls;
9. topology-event, migration, and target-reconstruction behavior; and
10. the disabled GRC9V3 reduction relation as a GRC9V4 wrapper duty only.

## Preregistered Candidates

The candidates are alternatives. Their order is not a ranking.

### C-T1 — Log-sector scalar potential flow

This is the solution already written in the provisional V4 spec:

$$
W_{0,C,e}
=W_{\mathrm{ref},e}
\exp\!\left(\kappa_{J,C}\kappa_{M,C}r_{C,e}\right),
\qquad
M_{4,C}=\eta_C\operatorname{Diag}(W_{0,C}),
$$

$$
\Phi_{C,i}
=\kappa_C\sum_{e\sim i}W_{0,C,e}
\bigl(C_i-C_{\operatorname{nbr}(e,i)}\bigr)
-V_C'(C_i;U),
$$

$$
J_{0,C}=-M_{4,C}d_0\Phi_C.
$$

Its preregistered identity is
`candidate_c_log_sector_potential_flow_v1`. The investigation must establish,
rather than assume, that using the accepted sector statistic $r_C$ in this
separately typed mobility adapter is the intended direct $T_C\to H_M\to
J_{0,C}$ realization and that $\kappa_{J,C}$ is identifiable rather than a
redundant reparameterization.

### C-T2 — General derived SPD transport adapter

Derive a separately typed symmetric positive-definite physical-current
operator

$$
M_{4,C}=\mathcal M_C(C,T_C,h,U;\theta_C)
$$

from a declared finite-range, equivariant Candidate C feature map. The result
must remain derived same-beat data and must not acquire retained-state
authority. This candidate is admissible only if its covariance, locality,
positive domain, units, and neutral control are fixed exactly.

### C-T3 — Reference mobility with conditioned driving

Keep the reference scalar mobility fixed and place the accepted retained-sector
dependence in a separately declared driving potential:

$$
M_{4,C}=\eta_C\operatorname{Diag}(W_{\mathrm{ref}}),
\qquad
J_{0,C}=-M_{4,C}d_0\Phi_C(C,T_C,h,U;\theta_C).
$$

This candidate must show that the direct path remains $T_C$-conditioned when
$\chi_C=0$ and returns to its reference law when $\kappa_{M,C}=0$.

### C-T0 — Bounded unresolved disposition

If no candidate earns the complete contract, Candidate C remains admitted at
the design level but is non-implementation-ready. All five C profiles stay on
bounded hold; no arbitrary default baseline may be supplied by an
implementation.

## Forbidden Transfers

The following are excluded unless a new derivation separately earns the exact
typed map:

$$
M_{4,C}=H_{1,\mathrm{form}},
\qquad
M_{4,C}=G_J,
\qquad
M_{4,C}=G_J^{-1},
\qquad
M_{4,C}=h_4.
$$

No candidate may introduce a second resource, hidden $T_C$ state, an
unreceipted topology resize, a second continuity write, or a GRC9-only premise
into the graph-generic law.

## Pressure and Acceptance Tests

The investigation must produce:

- a type-and-unit derivation for every composition in $J_{0,C}$;
- a neutral-control table distinguishing $\kappa_{M,C}$, $\chi_C$, and
  $\zeta_C$;
- a relabeling/orientation covariance proof on the declared graph domain;
- a stage table for all five C realizations, including OS predictor and
  corrector freshness;
- a topology/migration reconstruction rule with no mobility history smuggling;
- a noncollision check against the accepted Hodge/geometry symbols and
  authorities;
- an exact relation to the 40 disabled compatibility rows without modifying
  the GRC9V3 target; and
- an explicit disposition for every preregistered candidate.

Acceptance is design-level only. It does not establish runtime conformance,
formed-branch reachability, numerical stability, physical-channel
attribution, nonabsorbability, or preference over Candidate A.

## Propagation Rule

Only an accepted D11-C successor may be propagated. The order is:

```text
accepted D11-C record
  -> GRC-v4 substrate paper
  -> affected GRCV4 and GRC9V4 clauses
  -> source manifest and conformance fixtures
  -> final specification audit
```

Until then, `candidate_c_log_sector_potential_flow_v1` remains visible in the
specification solely as candidate C-T1 and is not conformance authority.
