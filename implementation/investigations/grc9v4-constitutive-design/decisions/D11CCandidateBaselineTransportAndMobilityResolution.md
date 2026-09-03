# D11-C Candidate C Baseline Transport and Mobility Resolution

**Gate:** D11-C
**Status:** Accepted bounded
**Record:** `GRC9V4-CD-D11-C-RESOLUTION-v1`
**Predecessor:** `GRC9V4-CD-D11-C-v1`
**Decision digest:** `82e8008e8edade39db7b5327a31a807031b712dcc86b3fe3e8c0977bda51e797`
**Selected candidate:** D11-C-T3a
**Selected profile:** `C-HM-STIFFNESS-BASELINE-v1`
**Human acceptance:** Accepted bounded on 2026-09-03

## Decision

D11-C accepts a revision-specific, graph-generic Candidate C baseline law
that keeps transport mobility separate from retained Hodge geometry:

1. a positive profile/reference edge field supplies a separately typed scalar
   transport mobility;
2. the accepted Candidate C sector changes
   $H_{1,\mathrm{form},M}$, not $M_{4,C}$;
3. the retained Hodge geometry supplies the direct baseline potential; and
4. the separate mobility converts its differential into physical flux.

The selected construction is the corrected D11-C-T3a refinement of the
preregistered T3 route. It closes the missing design-level $J_{0,C}$ contract
for CI, OS, RG2b, PC, and CI+PC. It does not authorize implementation or claim
runtime formation, endpoint effect, stability, physical nonabsorbability,
profile preference, or uniqueness.

## Why T3a Was Selected

Accepted D4-v2 requires the direct path

```text
T_C -> H_M -> J_0,C
```

to remain active when explicit Read-Back or its gain is disabled. T3a
implements that path literally through the retained Hodge stiffness. It does
not re-evaluate the sector statistic inside a second mobility law.

The accepted type correction permits $H_{1,\mathrm{form,ref}}$ and $M_{4,C}$
to share reference values while preserving distinct types and authorities.
T3a therefore uses sibling constructors from one declared reference field,
not an authority arrow from Hodge geometry to mobility.

## Typed Construction

Let $B$ be the oriented edge-flux-to-vertex divergence and
$d_0=B^\top$ the scalar differential. Candidate C retains the accepted
selector and positive Hodge deformation:

$$
T_C=P_M^\Delta(C,h,\Lambda_C)C,
\qquad
\rho_{C,v}=\tanh\!\left(\frac{T_{C,v}}{C_{\mathrm{ref}}}\right),
$$

$$
r_{C,e}=\frac{\rho_{C,u}+\rho_{C,v}}{2},
\qquad
\mathsf D_C
=\operatorname{Diag}\!\left[
\exp\!\left(\frac{\kappa_{M,C}}{2}r_C\right)
\right],
$$

$$
H_{1,\mathrm{form},M}(T_C,h)
=\mathsf D_C H_{1,\mathrm{form}}(h)\mathsf D_C.
$$

The complete profile binds an exact positive edge map

$$
W_{C,\mathrm{tr}}:E_{\mathrm{stable}}\longrightarrow\mathbb R_{>0}.
$$

Two separate typed constructors consume it at reference geometry:

$$
E_H(W_{C,\mathrm{tr}})
=H_{1,\mathrm{form,ref}}
=\operatorname{Diag}(W_{C,\mathrm{tr}}),
$$

$$
E_M(W_{C,\mathrm{tr}})
=M_{4,C}
=\eta_C\operatorname{Diag}(W_{C,\mathrm{tr}}),
\qquad \eta_C>0.
$$

The causal and authority boundary is

$$
D_{T_C}M_{4,C}=0,
\qquad
D_hM_{4,C}=0
$$

inside this same-profile law. There is no map

$$
H_{1,\mathrm{form},M}\longrightarrow M_{4,C}.
$$

## Baseline Potential and Current

Define the unnormalized retained vertex stiffness

$$
\mathcal L_{0,M}(T_C,h)
=B H_{1,\mathrm{form},M}(T_C,h)d_0.
$$

The direct Candidate C potential is

$$
\boxed{
\Phi_{0,C}(C,T_C,h,U)
=\kappa_{\Phi,C}\,
B H_{1,\mathrm{form},M}(T_C,h)d_0C
-V'_{C,U}(C).
}
$$

Equivalently,

$$
\Phi_{0,C}=\Phi_{G,C}+\Delta\Phi_{M,C},
$$

where

$$
\Phi_{G,C}
=\kappa_{\Phi,C}B H_{1,\mathrm{form}}(h)d_0C
-V'_{C,U}(C),
$$

$$
\Delta\Phi_{M,C}
=\kappa_{\Phi,C}
B\left(H_{1,\mathrm{form},M}-H_{1,\mathrm{form}}(h)\right)d_0C.
$$

The missing baseline current is now exactly

$$
\boxed{
J_{0,C}(C,T_C,h,U)
=-M_{4,C}d_0\Phi_{0,C}(C,T_C,h,U).
}
$$

It is a derived physical edge flux prepared before the fixed-geometry current
solve. Consequently,

$$
D_JJ_{0,C}=0
$$

inside that solve, and the accepted total-current closure remains

$$
J_{C,C}
=\left(I-\zeta_C\chi_C\widehat R_{C,\mathrm{flux}}\right)^{-1}
J_{0,C}.
$$

## Exact Unit Contract

The selected component binds symbolic physical units rather than leaving them
to an implementation default:

| Quantity | Unit |
|---|---|
| $C$, $C_{\mathrm{ref}}$ | $[C]$ |
| clock | $[t]$ |
| $J_{0,C}$, $J_{C,C}$ | $[J]=[C]/[t]$ |
| $H_{1,\mathrm{form}}$, $W_{C,\mathrm{tr}}$ | $[H_1]$ |
| $\Phi_{0,C}$, $V'_{C,U}$ | $[\Phi]$ |
| $\kappa_{\Phi,C}$ | $[\Phi]/([H_1][C])$ |
| $M_{4,C}$ | $[J]/[\Phi]$ |
| $\eta_C$ | $[J]/([\Phi][H_1])$ |
| $r_C$, $\mathsf D_C$, $\kappa_{M,C}$ | dimensionless |

Thus

$$
[\kappa_{\Phi,C}BH_{1,\mathrm{form},M}d_0C]=[\Phi],
\qquad
[M_{4,C}d_0\Phi_{0,C}]=[J],
$$

and the complete-step term $\Delta t\,BJ$ has unit $[C]$. Cross-profile
dimensionalization and magnitude comparison remain conditional under
`D10-CL-C-010`; they are not silently claimed by this internal type closure.

## Gauge, Domain, and Boundary

The accepted profile uses:

- a finite declared live graph and closed/no-flux boundary;
- a fixed-rank, strict-gap selector stratum;
- positive-definite bounded $H_0$ and $H_{1,\mathrm{form}}$;
- positive finite $W_{C,\mathrm{tr}}$ on every live edge;
- $C_{\mathrm{ref}}>0$, $\eta_C>0$, and finite $\kappa_{M,C}$ and
  $\kappa_{\Phi,C}$;
- a finite, sufficiently differentiable site-potential evaluator on the
  admitted $(C,U)$ domain; and
- the accepted D6-v2 invertible total-current block.

$\Phi_{0,C}$ is defined modulo one vertex constant per connected component,
because only $d_0\Phi_{0,C}$ enters current. The selected normalization is the
unnormalized stiffness $BH_{1,\mathrm{form},M}d_0$; substituting the normalized
$H_0^{-1}\Delta_0$ operator is a different profile.

Rank-gap loss, topology change, loss of positivity or finiteness, or total
current-block singularity exits this regular profile and fails closed.

## Canonical Reference-Field Lifecycle

The proposal's former “serialize or reconstruct” alternative is resolved as
one exact rule:

- the complete profile contains one exact stable-unoriented-edge-ID to
  $W_{C,\mathrm{tr}}$ map;
- the map is profile/reference context, not Candidate C state, and has no
  ordinary-beat writer;
- snapshots bind the complete profile digest and exact map;
- relabeling transports values by stable edge identity, while reversing an
  edge coordinate leaves its positive scalar value unchanged;
- migration or topology events must supply the entire target map as part of
  the target complete profile before readmission; and
- implicit copying, array resizing, interpolation, or treatment as retained
  history is forbidden.

A missing, duplicate, nonpositive, nonfinite, or unmatched target entry rejects
the event before atomic commit.

## Controls

- $\kappa_{M,C}=0$ makes $\mathsf D_C=I$, removes $T_C$ conditioning from the
  direct baseline, and returns $H_{1,\mathrm{form},M}$ to the supplied
  generated geometry.
- $\chi_C=0$ removes the explicit Read-Back current while the conditioned
  direct baseline remains active.
- $\zeta_C=0$ makes $J_{C,C}=J_{0,C}$; a read may remain diagnostic.
- $\tau_C=0$ removes only resolvent filtering from the explicit response. It
  does not remove the direct $H_M$-conditioned baseline.

Earlier statements that $\tau_C=0$ removes retained selectivity are henceforth
scoped to the explicit resolvent response channel.

## Disabled-Branch Compatibility

The selected T3a law applies only to the enabled GRCV4 Candidate C branch.
GRC9V4 owns the branch dispatch and must delegate the disabled branch exactly
to the unchanged GRC9V3 state, observable, and lifecycle contract. Substituting
or approximating that branch with T3a is forbidden. This freezes T3a's
nonapplication boundary without modifying GRC9V3 and without preempting the
D11-G9 port-allocation investigation.

## Realization Stages

| Realization | Accepted baseline stage |
|---|---|
| C-CI | Recompute the full selector/Hodge/potential/baseline chain for every trial $h$ before the joint residual. |
| C-OS | Build at predictor geometry, then rebuild from scratch at corrector geometry; predictor caches have no corrector authority. |
| C-RG2b | Build inside the fixed-$h$ current evaluator after target selector/Hodge readmission. |
| C-PC | Derive $h$ from old committed $Z_{4,C}$ and then build before current and continuity. |
| C-CI+PC | Recompute for every trial $h$ in the joint root reading old $Z_{4,C}$ and same-root $S_C$. |

The five realization-family labels remain unchanged. Their complete profile
payloads and digests must gain `C-HM-STIFFNESS-BASELINE-v1` during the later
ordered specification propagation.

## Derivative Surface

On the admitted smooth fixed-graph stratum,

$$
\begin{aligned}
\delta H_{1,\mathrm{form},M}
={}&(\delta\mathsf D_C)H_{1,\mathrm{form}}\mathsf D_C
+\mathsf D_C(\delta H_{1,\mathrm{form}})\mathsf D_C\\
&+\mathsf D_C H_{1,\mathrm{form}}(\delta\mathsf D_C),
\end{aligned}
$$

$$
\begin{aligned}
\delta\Phi_{0,C}
={}&\kappa_{\Phi,C}B(\delta H_{1,\mathrm{form},M})d_0C
+\kappa_{\Phi,C}BH_{1,\mathrm{form},M}d_0\delta C\\
&-D_CV'_{C,U}(C)[\delta C]
+D_U\Phi_{0,C}[\delta U],
\end{aligned}
$$

$$
\delta J_{0,C}
=-(\delta M_{4,C})d_0\Phi_{0,C}
-M_{4,C}(\delta d_0)\Phi_{0,C}
-M_{4,C}d_0\delta\Phi_{0,C}.
$$

For an ordinary same-profile fixed-graph variation,
$\delta M_{4,C}=\delta d_0=0$. These formulas close the design-level
$D_CJ_{0,C}$ and $D_hJ_{0,C}$ placeholders without claiming executable
implementation verification.

## Candidate Dispositions

| Candidate | Disposition | Reason |
|---|---|---|
| D11-C-T1 | Not selected; retained for comparison | It conditions mobility and duplicates sector modulation outside the accepted $H_M$-conditioned potential. It remains a possible D4/D4-v2 authority-expansion successor, without necessarily reopening D1. |
| D11-C-T2 | Not selected; admissible future family | General SPD or anisotropic mobility adds unnecessary transport ontology and separate support, unit, covariance, and event burdens. |
| D11-C-T3 | Refined into T3a | Its reference-mobility/conditioned-driving architecture is retained and made exact. |
| D11-C-T3a | Selected, accepted bounded | It realizes the required direct Hodge-conditioned path without added state or mobility-authority transfer. |
| D11-C-T0 | Not selected; fallback retained | A bounded complete design-level law was accepted. |

The provisional T1 text remains visible in the current spec until the ordered
paper-then-spec propagation phase. It is not accepted authority.

## Claim, Debt, and Provenance Effect

The accepted D10 topology remains immutable:

```text
D10 current claims rewritten = 0
D10 historical claims rewritten = 0
D10 claims reclassified = 0
D10 debt transformations changed = 0
```

The result adds the optional-profile successor claim `D11-C-CL-O-001` and
exact reciprocal edges to `D10-CL-O-002`, `D10-CL-N-003`,
`D10-CL-N-006`, `D10-CL-N-008`, and `D10-CL-C-011`. Those edges instantiate
or strengthen Candidate C through a successor; they do not edit the source
claims.

`D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY` is resolved boundedly. Its mobility,
potential, current, staging, internal units, lifecycle, derivative, and
provenance facets close. The 29 inherited D10 debt transformations retain their
accepted dispositions.

All ten forward runtime/numeric/implementation obligations remain pending.
D10.2's preclose provenance result remains satisfied only for its historical
population. The
[D11-C provenance supplement](D11CCandidateBaselineTransportProvenanceSupplement.json)
reopens and satisfies provenance for the three new objects and eleven new
contracts without modifying D10.2:

```text
D10.2 objects retained = 67
D11-C objects added = 3
current successor population = 70

D10.2 contracts retained = 152
D11-C contracts added = 11
current successor population = 163
```

## Witness

The tracked
[three-node algebra witness](../scripts/witness_d11_c_hm_stiffness_baseline.py)
passes with:

```text
closure residual L2 = 6.206335383118183e-17
charge residual absolute = 0
retained-geometry-off direct-path effect L2 = 0.4006081131911638
orientation covariance error L2 = 0
baseline dissipation = 1.952643684081568
```

This establishes finite algebra, typing, controls, a nonzero direct-path
witness, charge cancellation, and orientation covariance only. It is not
runtime or stability evidence.

## Authorization and Next Gate

```text
D11-C = accepted_bounded
D11-G9 = active
paper propagation = not yet authorized
specification propagation = not yet authorized
implementation = not authorized
src/tests changes = not authorized
GRC9/GRC9V3 changes = not authorized
```

The previously accepted sequence remains controlling:

```text
D11-C acceptance
  -> D11-G9 investigation and acceptance
  -> GRC-v4 paper propagation
  -> affected V4 specification extraction
  -> final specification audit
```
