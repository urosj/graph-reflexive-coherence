# D7G-v2 Geometry-Parametric Closure And Finalization

**Record:** `GRC9V4-CD-D7G-v2`  
**Status:** accepted bounded  
**Predecessor:** accepted `GRC9V4-CD-D7G-v1`  
**Decision digest:** `c52912d83797ee294799709b3e770574043df37f80073b51eebfaf8b2fd27efb`  
**Runtime or `src/` changed:** no

## Disposition

D7G-v2 closes the current D7G profile/staging audit and authorizes A and C for
bounded D8-A structural-target extraction. It does not admit either candidate
to full continuation comparison. The negative result belongs specifically to the selected D6/D7
lagged explicit realization; it is not a general GRC9V4 handoff requirement,
impossibility result, or candidate-local A/C failure.

The gate establishes five different facts:

1. A source-constrained, revision-specific reference embedding can be admitted.
2. The affine graph-Hodge profile and bounded A/C parametric domains are
   mathematically coherent.
3. Under the selected lagged explicit transitions, neither candidate defines a
   `Gamma_a` carrying generated geometry into later evolution.
4. The generated-geometry derivative through that missing realization is
   undefined, not zero, and is distinct from supplied pre-read geometry
   sensitivity.
5. The branch-appropriate structural continuation object remains a D8-A
   derivation; one common self-adjoint Hessian is not assumed.

The exact result is:

```text
E_ref = admitted revision-specific V4 embedding
affine H_profile = instantiated bounded profile
A supplied-geometry regularness = bounded
C supplied-geometry regularness = bounded on strict-gap SPD domain
A D_h_pre F_A = not established load-bearing
C internal operator dependence on h_pre = load-bearing and conditionally nonzero
C D_h_pre J_C = nonzero sensitivity not established
C D_h_pre F_C = not identically excluded, but nonzero full-transition sensitivity unproved
A/C D_h_generated F_later = undefined absent Gamma_a or equivalent realization
D8-A authorized structural-target candidates = [A, C]
D8 full-continuation-comparable candidates = []
```

Both candidate lanes retain the same bounded disposition:

```text
candidate-local transition valid
geometry-parametric regularness valid
selected lagged explicit geometry feedback unresolved
```

The next order is:

```text
D8-A branch-appropriate structural-target extraction
  -> GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR
  -> earliest affected gate reopening, if a realization changes authority/stage
  -> D8-B full analysis of completed realization(s)
```

The successor may begin by freezing a typed `S_H` interface, but it cannot
close there. It must instantiate and pressure at least one bounded complete
realization. The four named families are a non-exhaustive minimum pressure set:
their failure is not a V4 impossibility unless a separate result proves the
classification complete. Otherwise the search broadens or closes bounded
unresolved. Core theory need not uniquely select one, and implementation
convenience cannot select one either.

## What Closed

### Exact reference embedding

D7G-v1 correctly found that baseline GRC9V3 does not itself declare a physical
`h_4` owner. D7G-v2 does not reverse that finding. It admits an explicit V4
embedding from existing source conventions:

```text
E_ref(W_V3, mu_V3, G, boundary) -> h_4,ref

H_0,ref = diag(mu_i)
H_1,ref = diag(W_V3,e^-1)
B_ref   = oriented incidence on the live graph
boundary_ref = declared fixed V3 boundary class
```

The edge convention is grounded in B1-GR's primary native constitutive metric
`M_E,* = W_*^-1`. The node measure uses the positive V3 quadrature weights,
with the existing unit default. This is an explicit GRC9V4 embedding, not a
claim that GRC9V3 already possessed the V4 induced-geometry object.
The frozen sources constrain this choice but do not make it the unique possible
V4 embedding.

The runtime `geometric_length` label is supporting context only. Its
implementation uses a small additive regularizer, so it is not silently used
as the exact `W^-1` map.

### Geometry and profile classes

D7G-v2 keeps two classes separate:

```text
H_adm = admissible geometry states
P_adm = admissible profile maps whose outputs lie in H_adm
```

On the initial fixed stratum, an `H_adm` member has fixed `H_0,ref`, incidence,
boundary, and coordinate order, with a variable one-form metric satisfying:

```text
0 < h_min I <= H_1 <= h_max I < infinity.
```

The instantiated profile is:

```text
H_1,+ = H_1,ref + kappa_H Delta K_4
H_0,+ = H_0,ref
```

with `I + Theta_4` positive definite. For the admitted nonnegative-gain,
positive-semidefinite A/C tensor subprofile:

```text
lambda_min(H_1,+) >= h_ref,min
lambda_max(H_1,+) <= h_ref,max + kappa_H k_max.
```

The derivative is exact:

```text
D_K H_profile[delta K_4]
  = (0, kappa_H delta K_4, 0, 0).
```

This closes profile sensitivity for this named affine family. It does not make
the family the unique core `g[K]`, a canonical GRC9V4 metric, or a continuum
metric theorem.

### Reference neutrality

The affine map has exact reference neutrality:

```text
Delta K_4 = 0 or kappa_H = 0
  -> h_4,+ = h_4,ref.
```

This is not complete disabled-transition reduction. Candidate A has
revision-specific retained `W_A` state and staging; Candidate C has its sector,
retained geometry, and identification factorization. Turning off this profile
does not remove those objects or restore the exact V3 step/lifecycle contract.

## Candidate A

Candidate A retains one positive mobility authority:

```text
M_4,A = eta diag(W_A).
```

`H_1` is not relabeled as mobility. On the declared bounded geometry domain,
the accepted A algebra remains regular:

```text
W_A > 0 and W_hat_A > 0
  -> |q_A| < 1

0 <= zeta_A <= zeta_bar_A < 1
  -> D6 margin >= rho_A = 1 - zeta_bar_A > 0.
```

The positive `G_W` target and log-geometric writer also remain well typed. This
is a bounded invariance/type-regularness receipt over supplied geometry. It does
not demonstrate meaningful `h_4`-parametric transition sensitivity for A.

This does not yet close structural cultivation. The accepted A transition
commits:

```text
C[k+1]
W_A[k+1] = writer(W_A[k], C[k+1], J_C[k])
```

and its writer does not consume `h_4,+[k]`. Adding the new geometry to
`W_drv,A`, potential, or current would change an accepted operator or stage.
No current constitutive result admits one, and core theory may intentionally
leave the discrete realization open. D7G-v2 therefore does not invent one and
does not reopen D7 procedurally.

Under the selected lagged explicit staging, Candidate A's generated-geometry
chain stops at:

```text
delta W_A
  -> delta K_4,A
  -> delta h_4
  -?-> delta F_A,later because Gamma_A or an equivalent realization is undefined.
```

This is not the statement `D_h F_A = 0`. The accepted A transition has not made
supplied pre-read geometry load-bearing, while the derivative from generated
`h_4+` through a complete temporal realization is undefined. D8-A must derive
A's branch-appropriate structural continuation object and the non-erased
directions a complete realization would need to transmit.

## Candidate C

Candidate C has a stronger supplied-geometry result. On the fixed-topology,
fixed-boundary, fixed-rank, strict-selector-gap SPD subdomain, D7G-v2 types:

```text
L_0,sym(h)
P_M(h)
T_C = P_M(h) C
H_1,M = D_C H_1(h) D_C
I_4M(h) = H_1,M H_1(h)^-1
R_C = (I + tau_C Delta_1,M)^-1
Rbar_C = I_4M^-1 R_C I_4M.
```

The bounded domain requires:

```text
selector gap >= gamma_selector > 0
d_min <= diag(D_C) <= d_max
cond(I_4M) <= kappa_I < infinity
rho_C = (1 - zeta_bar_C) / kappa_I > 0.
```

Consequently:

```text
lambda_min(H_1,M) >= d_min^2 h_min
lambda_max(H_1,M) <= d_max^2 h_max
||R_C||_(H_1,M) <= 1 for tau_C >= 0.
```

This is a bounded theorem-shaped parametric domain, not a claim across selector
rank change, gap closure, topology events, or all SPD matrices.

Unlike A, C's supplied pre-read geometry is a declared load-bearing input to the
selector, `H_M`, `I_4M`, response, baseline current, and transition. On an
admitted strict-gap direction, at least one named internal map may have a
nonzero derivative. That does not yet prove nonzero `D_(h_pre) J_C` or
`D_(h_pre) F_C`: downstream maps may annihilate or cancel the variation, and a
nonzero current variation may be divergence-free. No complete chain
derivation or executed geometry-sensitivity witness currently excludes those
possibilities. The generated `h_4,+[k]` still has no `Gamma_C` or equivalent
complete temporal realization. The accepted C transition commits only
`C[k+1]`; `T_C`, `H_M`, and `h_4` are derived. Prior postsolve geometry cannot
in general be reconstructed from `C[k+1]` alone.

Under the selected lagged explicit staging, Candidate C's generated-geometry
chain therefore also stops at:

```text
delta T_C
  -> delta K_4,C
  -> delta h_4
  -?-> delta F_C,later because Gamma_C or an equivalent realization is undefined.
```

The distinction is exact:

```text
D_(h_pre) internal C operators
  = conditionally nonzero on named strict-gap directions

D_(h_pre) J_C
  = nonzero sensitivity not established

D_(h_pre) F_C
  = load-bearing and not identically excluded,
    but nonzero full-transition sensitivity remains unproved

D_(h_generated) F_C,later
  = undefined while Gamma_C or an equivalent realization is absent
```

Sensitivity to supplied pre-read geometry is not evidence that generated
geometry participates temporally. Undefined generated-geometry sensitivity is
not zero and does not preclude a structural continuation consequence.

## Structural Target Versus Temporal Realization

D7G-v2 originally treated these as one admission test. They are related but
not equivalent:

```text
structural target:
  delta K_4 -> delta h_4 -> delta C_struct,a -> non-erased target directions

complete temporal realization:
  coupled implicit | operator split | persistent carrier | reconstruction
```

The first belongs to D8-A. It must derive the branch-appropriate continuation
object under each accepted D6 closure. A reduced self-adjoint Hessian is
admissible only after a smooth slaving reduction supports it; a joint,
non-selfadjoint, or differential-algebraic object may instead be required.
Every resulting direction must be classified as:

```text
realization-invariant structural target
accepted-lagged-branch structural target
target not finalizable before temporal realization
```

Only the first class constrains every successor realization. If a successor
changes the current/geometry slaving relation, lagged-branch targets must be
rederived in D8-B rather than promoted into universal requirements.

The second belongs to the realization successor. For the current lagged
factorization, `D_(h_generated) F_later` is undefined because `Gamma_a` is
absent. D8-A must not manufacture a zero derivative by deleting that arrow or
count a repeated absence diagnosis as evidence. Instead, it must identify and
scope directions `v` for which the branch-appropriate structural object
responds. A complete temporal realization may be rejected for erasing a target
only when that target is proven realization-invariant or has been rederived for
that realization.

D8-A is an analytical consumer of the `h_4+` surface, not a runtime causal
consumer. The symbol registry therefore records no runtime causal consumer for
`h_4+`; analysis access does not close the missing generated-geometry feedback
arrow.

## Design Freedom And Concrete Realization Families

The selected lagged explicit realization is one V4 construction:

```text
J_C[k] -> j[k] -> K_4[k] -> h_4+[k] -> future use
```

It is not the core temporal grammar. Core also permits all algebraic
current-dependent geometry inside one complete effective current block:

```text
J = Psi(X, h(K(j(J))))
```

provided the full chain-rule block is included and boundedly regular. Such a
coupled realization has no cross-beat `Gamma_a` problem; it has a fixed-point
existence, uniqueness, and regularity problem instead. The Read-Back structural
bookkeeping also does not prescribe one universal discrete graph integrator.

The non-exhaustive minimum pressure surface is therefore:

| Family | Complete-step question | Main obligations |
| --- | --- | --- |
| Coupled/implicit | Solve `J`, `j`, `K`, and `h` in one reflexive closure | existence, uniqueness, complete `B_eff`, fixed-point regularity |
| Operator-split same beat | Let current produce geometry and consume it in a load-bearing substage before atomic commit | ordering, conservation, splitting error, atomicity |
| Persistent structural carrier | Make geometry or a sufficient structural coordinate causal state | D1 authority, writer, lifecycle, reset, serialization |
| Reconstructed geometry | Derive later geometry from already-authoritative retained state | exact reconstruction, no lost current-dependent information, Markov closure |

The coupled/implicit family deserves full pressure because it follows the core
effective-loop grammar directly. It reopens D6 as a new constitutive solution,
not because accepted D6 was erroneous.

`S_H` is only the typed comparative interface:

```text
S_H : (X, J, K, h, Delta t, context)
      -> admitted geometry participation in the complete step
```

The successor cannot close by naming it. It must instantiate and pressure at
least one bounded complete realization. Failure of all four minimum families
does not establish V4 impossibility unless a separate result proves this
classification complete. Without that proof, the search must broaden or close
bounded unresolved.

Before D8-B admission, a realization must close its equations, state authority,
stage order, fixed-stratum Markov closure, conservation/accounting, design
covariance, failure semantics, bounded local well-posedness/regularity, and
linearization surface. It must declare disabled behavior, lifecycle
requirements, and stability-analysis surfaces. Exact disabled V4-to-V3
reduction and full topology/event lifecycle remain D9 debt; stability
classification remains D8-B work. Those downstream results are not circular
prerequisites for admission.

The physical `H_profile` remains common, but A and C need not use an identical
temporal realization equation. Their retained ontologies differ. Candidate
neutrality means the same burden of proof and acceptance criteria, not the same
equation. Only a concrete realization determines which earlier authority or
stage must reopen. Later D8-B comparison must either match the realization
family where meaningful or treat each `(candidate, realization)` pair as an
architecture and separate realization effects from candidate effects.

## Scientific Meaning

D7G-v2 strengthens the design in one important respect and blocks it in
another.

The stronger result is that global geometry is no longer just a symbol. There
is now an exact source-grounded reference embedding, an instantiated bounded
profile, explicit geometry/profile classes, quantitative domains, and bounded
A/C parametric receipts.

The blocker is equally substantive but narrower than a V4 failure. A nonzero
geometric object is not enough to prove a runtime continuation effect. The
selected lagged explicit realization currently ends before generated geometry
feeds back because it has no `Gamma_a`. A coupled or operator-split realization
could close the same core loop without any cross-beat handoff.

This result therefore says:

> GRC9V4 now has coherent candidate-local transitions and a coherent candidate
> geometry construction. The selected lagged explicit realization does not yet
> complete generated-geometry feedback; V4 must now choose and justify a
> complete temporal geometry realization.

It does not say that GRC9V4 is impossible, that A or C is rejected, that the
branch-appropriate continuation object is geometry-insensitive, or that
persistent geometry state is required. It localizes a design decision created
by the investigation's selected lagged staging. Candidate B remains different:
its unresolved `U_B` is a candidate-local formative-law gap, not this A/C
complete-realization question.

Machine-readable completion is deliberately split:

```text
D7G_profile_stage_audit_complete = true
D7G_global_structural_cultivation_complete = false
```

The accepted D7G-v1 predecessor was also reverified directly from the working
tree before this revision: its canonical decision digest recomputes to
`b173c03f...`, and its file SHA-256 recomputes to `2824f7db...`, exactly as the
D7G-v2 source identity declares.

## Claim Ceiling

D7G-v2 supports:

```text
revision-specific inverse-conductance/quadrature E_ref
instantiated bounded affine graph-Hodge profile
exact affine sensitivity and reference neutrality
bounded A regularness under supplied admitted geometry
bounded C strict-gap SPD parametric closure under supplied geometry
C load-bearing internal geometry dependence without proven nonzero full-transition sensitivity
fail-closed localization of the selected lagged explicit geometry-feedback gap
separation of supplied pre-read sensitivity from undefined generated-geometry sensitivity
bounded D8-A scope-classified structural-target readiness for A and C after acceptance
non-exhaustive four-family minimum temporal-realization pressure surface
```

It does not support:

```text
complete structural cultivation
one universal structural Hessian
an admitted complete temporal geometry realization
full D8-B continuation comparison or stability classification
complete disabled V4-to-V3 reduction
runtime evidence
topology/event lifecycle
architecture selection
normative GRC9V4 specification
implementation or src changes
```

## Authorization

Human acceptance on 2026-08-24 authorizes D8-A only:

```text
D8_authorized = true
D8_authorized_scope = D8-A branch-appropriate scope-classified structural-target extraction only
D8-B_authorized = false
```

D8-A may derive each candidate's branch-appropriate
structural continuation object and scope-classified structural directions. It
must distinguish `D_(h_pre) F` from the undefined generated-geometry derivative,
must not promote C internal-map dependence into nonzero full-transition
sensitivity, and cannot count a repeated missing `Gamma_a` diagnosis as
evidence. Only realization-invariant targets constrain every successor family;
lagged-branch targets require D8-B rederivation after changed slaving.

The named `GRC9V4-GEOMETRY-TEMPORAL-REALIZATION-SUCCESSOR` is ready only after
D8-A. It must instantiate and pressure concrete realization(s), not close with
an interface. The four named families are a minimum, not a proven exhaustive
taxonomy. This record does not authorize that successor yet, D8-B, D9, D10, a
normative specification, implementation, or source changes.
