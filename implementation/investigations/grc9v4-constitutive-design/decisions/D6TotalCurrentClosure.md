# D6 Total-Current Closure

**Record:** `GRC9V4-CD-D6-v1`
**Status:** accepted bounded
**Decision digest:** `0c78ede1551ece13c4b4fc916f60531bdc30219791bf90be574e5b0f80aa3f16`

## Purpose

D6 decides the current-regime axis independently of the retained-state
ontology. For every D5-eligible candidate it must either provide a complete
regular algebraic current closure, admit a justified temporal current law, or
block and route the candidate. Merely listing algebraic and temporal current as
possibilities does not close this gate.

The D6 question is:

```text
Given the D5 operator R_a and its pre-read constitutive context,
can total current J_C be solved uniquely and regularly within one beat?
```

It is not yet the D7 question of whether present activity writes future retained
state, nor the D8 question of structural or temporal stability.

## Decision

The initial A and parameterized C profiles admit bounded same-beat algebraic
slaving. B remains a live architecture candidate but is routed because its
geometry and typed Read-Back operator have not been derived.

```text
candidate set after D6 = [A, B, C]
D7-eligible candidates = [A, C]
routed candidates = [B]

algebraically slaved candidates = 2
independently temporalized candidates = 0
rejected candidates = 0
architecture selected = false
```

No candidate is ranked. Algebraic closure for A or C does not make either one
the selected GRC9V4 architecture.

## Common Closure

For candidate `a`, D6 selects

```text
J_C = J0(X_a,k) + zeta_a chi_a R_a(T_a, h_a, X_read_a,k; J_C)

E_J,a = J_C - J0(X_a,k)
              - zeta_a chi_a R_a(T_a, h_a, X_read_a,k; J_C)
       = 0
```

The noncurrent package is frozen before the solve:

```text
X_a,k = C_k, retained state, geometry, mobility, topology,
        boundary data, and declared pre-read context X_read_a,k
```

The solve order is:

```text
1. freeze live-edge space, orientation, boundary data, and X_a,k
2. construct pre-read J0 and R_a
3. solve (I - zeta_a chi_a R_a) J_C = J0
4. verify domain, condition margin, support, boundary ledger, and residual
5. derive j_a = chi_a R_a J_C
6. expose authoritative J_C to D7; expose j_a only to the declared
   zeta_a (j_a tensor j_a) geometry path and telemetry/analysis
```

This ordering is load-bearing. D6 does not let `j`, `J_C`, or their downstream
geometry/write consequences re-enter `J0`, `R_a`, retained state, or
`X_read_a,k` inside the same solve. Under this reduced staging, the complete
within-solve current block is

```text
B_eff,D6,a = zeta_a chi_a R_a.
```

If D7 later moves a current-dependent geometry, mobility, retained-state, or
baseline path inside the current solve, this D6 result no longer supplies the
full effective block. D6 must then be reopened and every chain-rule path must be
included in `B_eff`.

This lagged-geometry order is a revision-distinct GRC9V4 discrete-beat
constitutive choice. It is not a claim that the core simultaneous active-current
loop generally reduces to `(I - zeta R)`. In the core relation, a same-beat
`J -> j -> K -> h -> J0` path belongs to the full instantaneous effective loop.
If D7 preserves the staged order above, the reduced D6 block remains complete;
if it moves geometry inside the current solve, D6 must reopen.

The selected active gain domain is

```text
0 < zeta_a <= zeta_bar,a < 1.
```

`zeta_a` is dimensionless and nonnegative in the initial normalized
current-to-current profile. Reusing it in the later `j tensor j` geometry term
remains conditional on the inherited D4 units, gauge, normalization, and tensor
compatibility audit. `chi_a` is a binary read gate, not a physical gain.
`chi_a = 0` is read-off; `zeta_a = 0` is gain-off. Both return `J_C = J0`, but
only read-off requires `j_a = 0`. Under gain-off, a nonzero `j_a` is diagnostic
only and has no causal downstream consumer in the initial profile.

The subunit gain is a uniform sufficient profile, not the exact or only
invertible domain. D6 diagnoses singularity by `+1` entering the spectrum of
the full effective current block and diagnoses robust slaving through the
smallest singular value or inverse norm in the declared current metric.
Spectral radius one is not a generic singularity test: an eigenvalue `-1`, or a
complex unit-modulus eigenvalue other than `+1`, does not make `I-B_eff`
singular.

The solve takes place on the declared admissible current cochain space, not on
an unrestricted edge vector followed by projection. Existing edges, closed
transport channels, boundary conditions, and external boundary drive are part
of that space or its affine translate. A constant-potential gauge is removed
upstream when constructing `J0`; a potential gauge null is not current
deslavement. Read-Back cannot create a nonexistent edge.

Both selected closures are linear and globally unique on each fixed D6 profile.
Their physical branch is therefore the exact inverse, independent of solver
seed, previous current, damping, line search, preconditioner, or iteration
count. Numerical iterations have no physical clock. A future nonlinear closure
would need an explicit global uniqueness or branch-selection law rather than
using solver convergence as constitutive semantics.

## Candidate A

D5 supplied

```text
q_A,e = (W_A,e - W_hat,e) / (W_A,e + W_hat,e)
R_A   = Diag(q_A).
```

D6 therefore selects the edgewise closure

```text
J_C,e = J0,A,e + zeta_A chi_A q_A,e J_C,e

J_C,e = J0,A,e / (1 - zeta_A chi_A q_A,e)

j_A,e = chi_A q_A,e J_C,e.
```

On the selected domain

```text
W_hat,e > 0
W_A,e >= 0
0 < zeta_A <= zeta_bar,A < 1
-1 <= q_A,e < 1,
```

the denominator is bounded away from zero and

```text
sigma_min(L_A) = min_e |1 - zeta_A chi_A q_A,e|
               >= 1 - zeta_bar,A

||L_A^-1|| <= 1 / (1 - zeta_bar,A).
```

The exact positive-gain classification is sharper:

```text
q_A > 0: singular only at zeta_A = 1/q_A > 1
q_A = 0: regular for every finite zeta_A
q_A < 0: regular for every nonnegative zeta_A
```

Thus the selected `zeta_bar,A < 1` profile is uniformly conditioned even as
`q_A -> 1`; D6 does not depend on a future `W_A <= W_max` bound. A future gain
profile reaching or exceeding one would require a new exact ratio/domain audit.

Positive retained contrast amplifies the baseline edge current; negative
contrast suppresses it; neutral contrast leaves it unchanged. The diagonal
operator cannot create support on an edge where `J0,A` has none.

The exact-zero-mobility boundary is also explicit. When `W_A,e = 0`,
`q_A,e = -1`, while D4 requires the mobility-conditioned baseline to have
`J0,A,e = 0`. The unique regular solution is therefore

```text
J_C,e = j_A,e = 0.
```

This closes A's initial support rule without creating a pseudoinverse, clipped
gain, or hidden current state. Strictly positive `W_A` is the smooth
fixed-transport-rank lane. Exact zero is a typed closed-channel lifecycle
boundary, not a smooth rank-preserving point.

A still has two declared paths:

```text
direct path:   W_A -> mobility -> pre-read J0,A
explicit path: W_A, W_hat -> q_A; q_A, J_C -> j_A
total current: J_C = J0,A + zeta_A j_A
```

Read-off disables only the explicit path and leaves the direct baseline path
unchanged. This makes the design factorization switchable and recoverable; it
does not yet prove that the explicit channel is physically non-absorbable.

D6 also performs the mathematical absorbability audit that can be done before
runtime evidence. Postsolve diagonal scaling is not automatically equivalent to
an admissible mobility replacement because the legacy-like baseline map uses
mobility both in potential construction and in the later flux. No universal
`W_tilde_A(W_A,W_hat,zeta_A)` has been established for the still-open complete
V4 baseline class. Conversely, nonredundancy is not yet proved: restricted
edge-local baseline classes could absorb the factor. D7 must freeze the complete
A baseline map, and D10 must demote A to retained-mobility recurrence without
explicit Read-Back if exact absorbability is then proved. This is a pre-D10
mathematical debt, separate from post-spec empirical identifiability.

Nonuniform `q_A` can mix global cut and cycle components even when `J0,A` is
potential-like. That is current-sector mixing, not retained historical cycle
orientation.

## Candidate B

B receives no D6 closure and is not rejected.

```text
disposition = routed_not_rejected_no_D6_closure

blocking routes:
  GRC9V4-D4-B-INDEPENDENT-CARRIER-GEOMETRY-CLOSURE
  GRC9V4-D5-B-TYPED-READBACK-DERIVATION
```

Without a typed `R_B` and a declared geometry or mobility map, neither an
algebraic inverse nor a temporal current law can be derived without invention.
D6 therefore forbids copying A or C into B and forbids temporalizing current to
hide B's missing operator. B remains in the architecture candidate set.

## Candidate C

D5 supplied the retained-geometry Hodge response

```text
Delta_1,M = B^T H0^-1 B H1
R_C       = (I + tau_C Delta_1,M)^-1.
```

On the regular `H1,M` one-form space, `Delta_1,M` is self-adjoint and
nonnegative in the `H1` inner product. Its modal response is

```text
r_C(nu) = 1 / (1 + tau_C nu),
0 < r_C(nu) <= 1.
```

Using the declared orientation-covariant isometric identification `I_4M`, D6
selects

```text
J_C^M = J0,C^M + zeta_C chi_C R_C J_C^M

J_C^M = (I - zeta_C chi_C R_C)^-1 J0,C^M

j_C^flat = I_4M^-1 chi_C R_C J_C^M.
```

Equivalently, the physical operator is

```text
R_C^physical = I_4M^-1 R_C I_4M.
```

Self-adjointness and norm bounds are taken in the `H1,M` metric or its transported
physical metric, not in an undeclared Euclidean metric. `h_M` and `I_4M` remain
frozen during the solve. If either depends on the unknown current, its derivative
belongs in `B_eff` and D6 must reopen.

For `tau_C > 0` and `0 < zeta_C <= zeta_bar,C < 1`,

```text
||(I - zeta_C chi_C R_C)^-1||_H1
  <= 1 / (1 - zeta_bar,C).
```

The positive profile amplifies low-Hodge and harmonic response most strongly.
That is a spatial/modal statement, not evidence of temporal slowness,
self-sustenance, or stability.

Topology makes the exact boundary visible:

```text
tree profile:
  no graph one-form harmonic kernel

cycle profile with zeta_C < 1:
  harmonic r_C = 1, but sigma_min(L_C) >= 1 - zeta_bar,C

cycle profile with zeta_C = 1:
  harmonic sector is singular
  increasing tau_C cannot regularize nu = 0
```

The selected subunit profile is therefore regular on both trees and cycle
graphs. A cycle-birth event can create a harmonic singular direction at unit
gain, but unit gain lies outside this profile and D9 must rebuild the current
space. D6 does not project harmonics away. Nor does regular C closure create
circulation: because the resolvent preserves Hodge eigenspaces, a solution has
no harmonic component when `J0,C` has none.

The initial C profile requires positive regular Hodge data, a valid `I_4M`, and
strictly positive transport mobility on every edge in the admitted current
component. Exact-zero transport mobility fails closed unless a future profile
derives an invariant transmissive subspace. Disconnected components remain
block diagonal. D6 adds no undeclared boundary source.

This is an explicit choice among the possible zero-mobility semantics: the
initial C profile rejects exact-zero mobility rather than inserting a support
projector or allowing Read-Back to reopen a closed channel. A later projected
profile would have to derive a metric-orthogonal invariant transmissive
subspace and re-audit the operator.

C remains parameterized by `h_M`. The closure does not derive
`T_C -> H_M -> h_M`, close retained mediation, or supply the exact Hodge-star
and metric-identification construction owned by D8.

The C absorbability audit is also bounded. A genuinely cross-edge Hodge
response is outside D4's direct scalar edge-mobility parameterization, but the
complete `h_M`-conditioned V4 baseline map is still open and scalar/diagonal
special reductions may be absorbable. Exact full-model redundancy or
nonredundancy remains a pre-D10 debt; parameterized operator notation alone
does not settle it.

## Current And Geometry Coupling

The mature RC form uses the same coefficient for the linear `j` contribution
to current and the quadratic `j tensor j` contribution to geometry. The initial
D6 profile retains that single-coefficient pattern:

```text
current stage:  J_C = J0 + zeta_a j
later D7 stage: K receives zeta_a (j tensor j)
```

This is an explicit V4 candidate choice grounded in the core pattern, not a
claim that theory uniquely forbids separate coefficients. `chi_a = 0` makes
`j = 0` and disables both uses. `zeta_a = 0` suppresses both causal couplings
even if enabled `j` is computed diagnostically. Negative gain is excluded, so
the quadratic geometry coefficient does not reverse sign. Introducing separate
`zeta_read` and `zeta_K` requires a named successor with fresh units,
regularity, and claim analysis.

After the solve, `J_C` is the authoritative current for continuity and declared
downstream causal consequences; direct current-derived geometry enters only
through the admitted `zeta (j tensor j)` path unless a successor explicitly
adds another map. Incoming current remains available only at declared pre-read
stages such as A's `W_hat` construction and later D7 write inputs; it cannot
bypass the solved total-current surface.

`j` is not a free D7 write input. D6 authorizes it only for the declared
`zeta (j tensor j)` geometry path and for telemetry or analysis. A direct
`j -> retained state` write would bypass the total-current closure and is not
authorized. If D7 proposes such a path, it must derive that path explicitly and
show that it remains a lawful downstream consequence of `J_C` rather than a
shortcut. In particular, when `zeta = 0`, diagnostic `j` may not change
geometry, retained state, or any other future causal state.

## Slaving And Deslavement

A and C are algebraically slaved within the beat. This means the current is a
unique constitutive function of the frozen pre-read package on the declared
regular domain. It does not mean that algebraic slaving has been derived as a
normally attracting fast temporal limit.

The deslavement trigger is loss of the declared lower singular-value margin of

```text
L_a = I - zeta_a chi_a R_a
```

or exit from the admitted current space. At that boundary D6 fails closed. It
does not infer a temporal current equation, delete a critical mode, use a
pseudoinverse, or identify the singularity with structural marginality, spark,
basin birth, or topology change.

If a future target requires passage through this boundary, it must open the
named `GRC9V4-D6-CURRENT-DESLAVEMENT-SUCCESSOR` and supply a justified temporal,
higher-order, or differential-algebraic completion.

That successor must first ask whether only a critical subspace needs an
independent coordinate. Loss of regular elimination in one direction does not
justify temporalizing all of `J`. Critical content must be represented as a
covariantly defined subspace, not a mode number; an analysis-only moving
projector cannot become runtime state without constitutive authority and event
transport.

No temporal profile is selected here. Consequently current relaxation rate and
`A-FAST-SLOW` are `not_applicable`, and disabled-profile temporal-state
migration is not activated. Singularity does not prove a nonzero current branch
or spontaneous circulation.

## Failure And Atomicity

The solve is invalid before execution when its state space, metric,
identification, gain, support, topology, or boundary inputs are invalid. It is
invalid during or after execution when the condition margin fails, the solve
fails, the scaled residual exceeds its declared tolerance, accounting fails,
or either current is nonfinite.

Solver failure and constitutive singularity are diagnosed separately. A solver
can fail on a regular equation or return a value near a singular one; condition
margin and scaled residual remain independent gates. A topology or edge-space
change invalidates the fixed-stratum problem and routes to D9 rather than being
called current singularity. Runtime loss of regularity rejects the step or exits
the admitted profile; it does not silently clip gain, reuse old current, add
`epsilon I`, or activate temporal current.

Failure is atomic:

```text
no partial J_C, j, geometry, retained-state, or observable update is committed
```

A future implementation must preregister a current-norm-scaled condition margin
and residual tolerance. D6 defines that obligation but does not invent runtime
thresholds or report runtime evidence.

## Controls And Pressure Audit

The structured record freezes 72 controls. They cover:

```text
pre-read staging and complete effective-block accounting
read-off, gain-off, and passive-null behavior
bounded inversion, residuals, and atomic failure
A denominator, support, zero-mobility, and double-path behavior
C metric, Hodge, component, mobility, and mediation boundaries
B routing and no borrowed closure
slaving/deslavement and threshold non-relabels
partial critical-subspace and runtime-projector boundaries
solver iteration, branch selection, regularization, and gauge traps
A/C exact mathematical absorbability boundaries
C harmonic topology and correct-metric semantics
shared current/geometry gain and authoritative downstream current staging
direct-j write bypass and gain-off causal-leakage prevention
revision-distinct lagged-geometry provenance and core-loop nonrelabeling
transitive predecessor-debt persistence and normalized-gain unit boundaries
D3 feedback and no cross-candidate gain ranking
boundary, topology, orientation, graph-isomorphism, and lifecycle scope
runtime, architecture-selection, and normative-specification overclaims
```

All 96 adversarial D6 pressure rows are individually classified in the
structured decision. Their main disposition groups are:

```text
1-13   closure ontology, staging, solver causality, and regularization
14-20  robust conditioning, exact singularity, current space, and gauge
21-34  zero mobility, A gain geometry, C harmonics, and partial deslavement
35-48  uniqueness, symmetry, mathematical absorbability, and read/gain controls
49-65  geometry coupling, physical representation, mediation, and support
66-78  temporal nonselection, failure semantics, topology, and boundaries
79-96  downstream authority, complete-loop staging, D3 feedback, debt, and claims
```

The audit is analytical and source-grounded. No prototype or runtime probe was
executed.

## Debt Lifecycle

D6 classifies every one of the 27 D5 debts. It also incorporates by reference
20 still-open older debt IDs carried through D5, of which 16 remain pre-D10
blockers and four remain nonblocking. The D10 blocker set is the union of the
current-generation open-debt ledger and this transitive inherited-debt ledger;
absence from the current-generation array is not resolution.

D6 resolves the total-current and
initial-gain obligations, resolves A's initial zero-mobility support rule, and
closes the `J0`/`j` split only at the constitutive factorization level. Exact
mathematical absorbability relative to the eventual complete baseline class is
separate from physical identification and remains explicit candidate debt.

Two predecessor obligations are transferred into narrower D6 debts, and the
hardening audit adds two candidate-specific mathematical debts:

```text
D6-DEBT-D7-STAGING-AND-FULL-LOOP
D6-DEBT-D9-SUPPORT-BOUNDARY-LIFECYCLE
D6-DEBT-A-MATHEMATICAL-ABSORBABILITY
D6-DEBT-C-MATHEMATICAL-ABSORBABILITY
```

The first requires D7 to preserve pre-read staging and close the cross-beat
write/read path. The second requires D9 to define zero-mobility, open-boundary,
and topology-event behavior in the complete lifecycle. The A/C absorbability
debts require the completed baseline maps to prove redundancy or nonredundancy
before D10; an exactly absorbable explicit channel must be demoted. A final
dormant debt records the singular-current successor, activated only if a future
target requires passage through loss of invertibility.

The resulting open ledger has 25 debts. It keeps pre-D10 design blockers
separate from post-spec runtime reachability, physical attribution, covariance,
and normative-encoding work.

## D7 Handoff

After human acceptance, D7 receives:

```text
A:
  exact regular algebraic current closure
  authoritative J_C,A at the post-solve stage
  j_A only for declared zeta_A (j_A tensor j_A) geometry and telemetry/analysis
  no D6-authorized direct j_A -> W_A write shortcut
  D2-admissible W_A write interface
  shared zeta_A current/geometry staging
  unresolved full-loop, absorbability, and physical-attribution debt

C:
  exact parameterized regular algebraic current closure
  authoritative J_C,C at the post-solve stage
  j_C only for declared zeta_C (j_C tensor j_C) geometry and telemetry/analysis
  no D6-authorized direct j_C -> T_C write shortcut
  shared zeta_C current/geometry staging
  unresolved H_M, T_C mediation, metric, Hodge, event-space, and absorbability debt

B:
  still in the architecture set
  routed to named geometry and typed-operator derivations
```

D7 must define the full cross-beat transition and prove

```text
retained state k -> j_k -> J_C,k
                   -> downstream consequence
                   -> retained state k+1.
```

It may not reinterpret this D6 same-beat solve as that closed loop.

## Claim Boundary

D6 supports only:

```text
two bounded candidate-specific regular algebraic current closures
one routed candidate with named missing derivations
explicit solve order, inverse domains, support rules, and atomic failure semantics
robust singular-value/inverse-norm conditioning on the admitted current spaces
an orthogonal no-current-temporalization decision for the initial A/C profiles
```

It does not support:

```text
runtime implementation or reachability
a demonstrated fast temporal limit
independent temporal current persistence
write-back, retention, or a closed reflexive loop
temporal or structural stability
singular branch passage
topology-event current transport
physical identification of j as a non-absorbable channel
final mathematical nonredundancy of either explicit j channel
T_C-specific retained mediation
candidate ranking or architecture selection
normative GRC9V4 specification
```

The experiment owner accepted D6 as `accepted_bounded` on 2026-08-24. D7 is
authorized. Normative specification, runtime implementation, and `src/` changes
remain unauthorized.
