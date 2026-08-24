# D5 Directional Read-Back

**Record:** `GRC9V4-CD-D5-v1`
**Status:** accepted bounded
**Decision digest:** `453416f42beefa1c9e725b675a0af7d4fd49c3e83691ee16e3e3bcfb6d37f213`

## Purpose

D5 asks a narrower question than total-current closure:

```text
Given an admitted retained representation and the D4 ownership map,
what typed directional operator returns retained formation into present current?
```

The gate must produce a candidate-specific operator family or a named missing
derivation. A list of desired properties is not enough. D5 does not yet choose
the total-current solve, write-back law, complete step, architecture, or runtime
implementation.

The result is intentionally asymmetric:

```text
A = bounded explicit V4 edge-contrast operator family
B = routed to a typed carrier/geometry/Read-Back derivation
C = bounded retained-geometry Hodge-resolvent family parameterized by h_M
```

A and C can proceed to D6 after D5 acceptance. B is not rejected, but it cannot
enter D6 until its D4 geometry and D5 operator routes are actually derived.

## Source Boundary

The core Read-Back class is

```text
j^flat = R_M(T_M, h; J_C^flat)
R_M(T, h; 0) = 0
```

and `j` is a derived current-like contribution, not another independently
conserved coherence stream. The core also supplies a candidate class on
retained-geometry one-forms through a Hodge spectral response. It does not
select one universal nonlinear operator.

D4 provides the candidate-specific ownership constraints:

```text
A owns retained scalar mobility W_A, not retained geometry
B proposes independent nonresource T_B but lacks its type and G_B map
C owns a derived retained C-sector role but still lacks exact H_M
```

The B1 graph contract contributes typed edge-cochain, orientation, passive-null,
and `J0`/`j`/effective-loop controls. It is a starting derivation and verification
surface, not immutable V4 semantics or positive unchanged-GRC9V3 Read-Back
evidence.

## Common Operator Contract

Every admitted D5 operator has the widened form

```text
R_a(T_a, h_a, X_read_a,k; .) : Omega^1(E_k) -> Omega^1(E_k)
j_a = R_a(T_a, h_a, X_read_a,k; J_trial)
```

where `X_read_a,k` is declared nonretained current-step constitutive context. It
cannot hide prior history, and it must be held fixed or transformed as declared
in retained-state counterfactuals. This admits A's instantaneous `W_hat`
reference without pretending that `W_hat` is retained state. On one fixed
live-edge space and regular metric stratum, a typed family must satisfy:

```text
zero_present_current:
  J_trial = 0 -> j_a = 0 for every admissible retained state

coordinate reorientation:
  B' = B R
  J_trial' = R J_trial
  j_a' = R j_a

physical current reversal:
  candidate-specific parity class at fixed retained state and coordinates
  A and C are odd on their declared linear strata; B remains unresolved

typed_operator_family:
  domain, codomain, current stage, retained inputs, geometry or metric inputs,
  X_read, and fail-closed operator controls are all declared

retained_mediation_closed:
  the claimed retained representation has an admitted causal path to the
  operator conditioning surface, and a lawful retained-state intervention
  changes j_a on at least one admissible nonzero current probe
```

These are separate admission levels. A has a typed family and an operator-level
retained intervention, while physical separation from its direct mobility path
remains unresolved. C has a typed family conditional on regular `h_M`, but its
retained mediation is not closed until `T_C -> H_M -> h_M` exists. B has neither
a typed family nor closed retained mediation. A typed family alone is not
physical channel identification, runtime reachability, or total-current closure.

`J_trial` is an unsolved pre-write argument in the same physical cochain space
as the later total current. D5 does not assume it already satisfies the D6
recurrence. D6 alone may substitute `J_C` and solve

```text
J_C = J0 + zeta_a R_a(T_a, h_a, X_read_a,k; J_C).
```

`X_read_a,k` is frozen at its D5-declared pre-read stage throughout that D6
solve. In particular, A's `W_hat_k` is not recomputed from the unknown `J_C`
inside the recurrence unless a later gate explicitly admits and analyzes a
different closure.

The graph cochain is already the declared current representation; continuum
flat notation does not lower it a second time. If `h_4` and `h_M` use different
edge inner products, a typed identification must carry the cochain between
them. The retained state is preexisting state at `k`; a D7 write for `k+1`
cannot be read early.

Pure edge-coordinate reorientation and physical current reversal are different
operations. The former changes representation while preserving physical state;
the latter changes the physical current under fixed coordinates. Reversed
forming history and simultaneous retained-package/current reversal are two
additional tests. Node permutations and graph isomorphisms must also transform
the operator covariantly; storage order is never physical.

The passive null is operator-level only. It is not a zero-`J0` test, a
full-loop equilibrium statement, energetic passivity, or loop stability. The
explicit `J0`/`j` decomposition is fixed here as a constitutive gauge: `J0` is
the D4 baseline path and `chi_a` switches only `j`. A and C use unit-normalized
dimensionless operator families; the separate physical gain `zeta_a` belongs
to D6. This makes the channels well-defined for design without yet proving
that they are physically identifiable rather than absorbable into `J0`.

## Candidate A: Edge-Contrast Read-Back

Candidate A does not inherit the core retained-geometry Read-Back claim. D5
instead defines an explicit V4 extension family from A's admitted retained
mobility state.

For each live edge, define the dimensionless retained contrast

```text
q_A,e = (W_A,e - W_hat,e) / (W_A,e + W_hat,e)
```

where `W_A >= 0` is authoritative retained mobility and `W_hat > 0` is the
pre-read instantaneous reference. This does not redefine D2's `R_W`; it is a
separate D5 read coordinate. The operator is

```text
R_A = chi_A Diag(q_A)
j_A,e = chi_A q_A,e J_trial,e
```

with `chi_A = 1` in the enabled read profile and `chi_A = 0` for read-off.

The construction has several useful exact properties:

```text
-1 <= q_A,e < 1
W_A = W_hat -> q_A = 0
J_trial = 0 -> j_A = 0
J_trial -> -J_trial -> j_A -> -j_A
edge-coordinate reversal -> q_A unchanged and j_A covariant
graph isomorphism -> q_A permutes and j_A transforms as an edge cochain
```

`q_A` is dimensionless and the operator norm is at most one under a diagonal,
orientation-invariant edge metric. Positive contrast supports the present edge
direction; negative contrast opposes it. Because `W_A` and `q_A` are scalar
edge quantities, they retain magnitude or an unoriented route axis, not past
flow chirality. The direction of `j_A` comes from present `J_trial`. This is an
edge-local, edge-dependent gain. A nonuniform `q_A` can mix global cut and cycle
components, but it does not establish cycle memory or rich historical
directionality.

This is an actual operator family, but it creates a D6 attribution obligation.
`W_A` already conditions direct baseline transport:

```text
direct path:    W_A -> mobility -> J0
explicit read:  W_A, W_hat -> q_A; q_A, J_trial -> j_A
```

Read-off sets only `chi_A = 0`; it leaves `W_A`, mobility, and direct `J0`
unchanged. D6 must include both paths in the effective current closure and
reject double counting. It must also resolve current support on exact-zero
mobility edges.

That last qualification is load-bearing. Defining `chi_A` makes the direct and
explicit paths separately switchable, but does not prove that the added path is
physically non-arbitrary rather than a reparameterization of mobility. An
operator-level `W_A` swap holds `W_hat` and `J_trial` fixed; runtime attribution
must additionally account for the simultaneous change in baseline `J0`.
Candidate A may therefore be demoted later to retained-mobility recurrence
without explicit Read-Back while remaining a valid retained-mobility
architecture.

## Candidate B: Named Missing Derivation

Candidate B cannot yet receive a lawful operator. D4 does not select the type,
rank, orientation, or units of `T_B`, and it does not supply `G_B(T_B,C) -> h_B`
or an equivalent geometry map. Therefore an expression such as

```text
j_B = T_B J_trial
```

would be untyped and could silently turn a scalar, tensor, score, or unrelated
state into a current operator.

D5 routes B to:

```text
GRC9V4-D5-B-TYPED-READBACK-DERIVATION
```

That route must first consume the D4 B geometry route, then provide

```text
R_B(T_B, h_B; .) : declared Omega^1 input -> identified Omega^1 output
```

with passive-null, retained-state, orientation, physical reversal, nonresource,
and hidden-history controls. Physical oddness is not preimposed: a future
oriented or chiral carrier must declare its own reversal class while preserving
coordinate covariance. B remains a revision-level candidate; it is not a D6
candidate in the current gate state and receives no native consumer by stealth.

## Candidate C: Hodge-Resolvent Read-Back

Candidate C receives an explicit isotropic resolvent specialization of the core
Hodge-response candidate class. This particular resolvent is a D5 constitutive
choice, not a unique law selected by the core paper. It remains parameterized by
a regular positive `h_M`; D5 does not close the missing `H_M` map.

On the current graph treated as a one-dimensional cell complex, freeze a
node-by-edge incidence `B`, positive node Hodge star `H0`, and positive edge
Hodge star `H1`, all induced by or explicitly identified with `h_M`:

```text
d0       = B^T
delta1   = H0^-1 B H1
Delta1_M = d0 delta1 = B^T H0^-1 B H1
<u,v>_1  = u^T H1 v
```

`Delta1_M` is self-adjoint and nonnegative in the declared edge one-form inner
product. For `tau_C > 0`, define

```text
R_C = chi_C (I + tau_C Delta1_M)^-1
J_trial^M = I_h4_to_hM J_trial^flat
j_C^M = R_C J_trial^M
j_C^flat = I_h4_to_hM^-1 j_C^M
```

on the regular domain where the metric identification is valid. The modal gain
is

```text
r_C(nu_a) = 1 / (1 + tau_C nu_a)
```

so this family is a positive self-adjoint contraction. Low Hodge-eigenvalue
and graph-harmonic current modes receive larger read gain. That is a Read-Back
response statement, not a claim that those modes are dynamically slow or
self-sustaining. In particular, unit gain on a graph harmonic mode does not
establish temporal circulation persistence.

The operator is graph-native and orientation covariant. Under a diagonal edge
reorientation `R`:

```text
B' = B R
H1' = R H1 R
Delta1_M' = R Delta1_M R
j_C' = R j_C
```

The same construction is covariant under graph isomorphism. It is graph-global
inside each connected component but block diagonal across disconnected
components when the Hodge data respect graph support. It acts only on existing
live edges. Its metric Hodge decomposition can preserve gradient and
cycle/harmonic eigenspaces; a tree cannot verify the latter, so later analysis
must include a graph with nontrivial first cycle space. A selected cycle basis
is analysis gauge, not physical state.

Candidate C has the same direct/read separation obligation as A:

```text
direct path:    T_C-conditioned h_M + separate mobility -> J0
explicit read:  h_M, J_trial -> R_C -> j_C
provenance:     T_C -> H_M -> h_M                     [H_M still missing]
```

Read-off sets `chi_C = 0` while preserving `T_C`, `h_M`, and direct `J0`.
D6 must include the full `J_C -> j -> K -> h -> J0` feedback where active.

The current operator is directly conditioned by `h_M`, not by a free-standing
`T_C` input. A `T_C` counterfactual counts as retained-sector mediation only
after an admitted `H_M` or equivalent map propagates that intervention into
`h_M`. At fixed `h_M`, a matched `T_C` swap is a negative control and must leave
`j_C` unchanged. Until that derivation exists, D5 supports a parameterized
retained-geometry response, not demonstrated `T_C`-specific mediation.

An algebraic `h_M` package swap is admissible for operator typing and
sensitivity, but it is off-manifold unless an admitted `H_M` can produce it.
Runtime evidence instead needs matched admissible `C` states or a lawful
selector intervention propagated through `H_M`. The initial C profile consumes
the spatial retained sector only. An optional dynamic slow sector remains
excluded until it is reconstructable from declared current causal state under
D3, or receives D1-level successor authority with its clock and transport.

`j_C` enters continuity through incidence divergence and may be divergence-free.
Consequently, no scalar `C` change is not a negative Read-Back control: a cycle
or harmonic current may still affect geometry through `j tensor j`. Net open
boundary transport requires a boundary ledger, and exact-zero mobility support
remains a D6 question.

An analysis-only dynamic projector cannot enter `H_M` or `R_C`. A dynamic
sector may be used only when deterministically reconstructable from admitted
current causal state or separately admitted under D1-level state authority.

## Controls And 68-Point Pressure Audit

D5 freezes 57 fail-closed controls and one structured pressure row for every
item in the adversarial review. The load-bearing families cover:

```text
trial current versus solved total current
typing, passive null, and energetic-passivity separation
edge-subset reorientation, graph isomorphism, and four reversal cases
directionality class and historical-orientation carrier
read-off versus carrier-neutral versus frozen-carrier controls
J0 / j decomposition gauge and zeta / j scale gauge
lawful, off-manifold, and runtime-reachable counterfactuals
live-edge support, zero mobility, locality, divergence, and boundary accounting
cut, cycle, harmonic, disconnected-support, and cycle-basis boundaries
candidate-specific topology, boundary, event, RNG, selector, and hidden-history rivals
scalar, label, score, projector, and sign-even proxy relabels
A's W_A/R_W and double-path boundaries
B's untyped-carrier shortcuts
C's H_M, Hodge metric, selector, and event-space boundaries
runtime, closure, write-back, and architecture overclaims
```

All 68 pressure rows are classified in the structured decision. The audit does
not change the asymmetric candidate outcome, but it narrows what “admitted”
means:

```text
A = explicit bounded operator channel definition;
    physical separation from mobility remains open

B = no typed Read-Back operator;
    D4/D5 derivation routes remain open

C = explicit bounded h_M-conditioned operator family;
    T_C-specific mediation and runtime H_M remain open

physically identified Read-Back channels = 0
candidate ranking = not performed

candidate_set_after_D5 = [A, B, C]
D6_eligible_candidate_set = [A, C]
routed_candidate_set = [B]
```

For navigation, the exact one-row-per-check ledger is grouped as follows:

| Audit items | Surface | Disposition |
|---|---|---|
| 1-14 | operator commitment, trial current, typing, graph covariance, reversal, directionality | closed at D5 |
| 15-24 | A identifiability, decomposition/scale gauges, three control modes, lawful counterfactuals | contracts frozen; physical attribution remains open |
| 25-36 | B/C derivation boundaries, linearity, direct versus effective feedback, signature factorization | B routed; A/C bounded only |
| 37-49 | mobility support, live edges, conservation, cut/cycle space, topology, rivals, C dynamic sector | support and later verification debts assigned |
| 50-61 | sign-even geometry, historical direction, parity, reachability, locality, units, derivatives, mediation | claim boundaries closed; runtime evidence absent |
| 62-68 | present activity, write/read separation, candidate demotion routes, no ranking | closed at D5 |

The deliberately deferred items have named owners: exact-zero mobility,
decomposition attribution, physical gain, and full effective loops go to D6;
write-back and lawful retained-state evolution go to D7; derivative, cycle,
graph-covariance, and operator comparisons go to D8 or later verification; and
event-space transport and boundary lifecycle go to D9.

The debt lifecycle separates design closure from empirical verification. Before
D10, the `J0`/`j` factorization must be constitutively defined, recoverable, and
non-double-counted, and rival carrier paths plus their controls must be
structurally available. Whether the factorization is physically non-absorbable
and whether rival carriers are empirically excluded remain post-spec causal
verification debts. The optional C dynamic sector is not in the initial profile;
its dormant debt reopens only if that sector is later admitted.

For C, D8 must freeze the `H0`/`H1` construction, boundary convention, and enough
discretization semantics to define `R_C` before D10. Encoding that accepted
construction in a normative specification is separate post-D10 work and is not
a design-closeout blocker. The D4 selector/geometry fixed-point debt also remains
open: a lawful counterfactual does not establish staging or existence and
uniqueness of the `P_M <-> T_C <-> h_M` feedback relation.

D5 also accounts explicitly for all 23 open D4 debts. Each is resolved,
narrowed, carried, carried as nonblocking, or superseded by a named D5 debt.
Supersession transfers the obligation; it does not erase it. Accepted predecessor
debts remain globally persistent until one of those explicit lifecycle actions
occurs.

## D6 Handoff

After human acceptance, D6 receives:

```text
A:
  R_A = Diag(q_A)
  direct W_A-conditioned J0 path
  explicit decomposition-identifiability, double-path, and zero-mobility debts

C:
  R_C = (I + tau_C Delta1_M)^-1
  parameterized h_M and metric identification requirements
  direct h_M-conditioned J0 path
  open H_M and T_C-specific mediation dependencies

B:
  not D6-eligible
  retained as named D4/D5 derivation debt, not rejected
```

D6 must choose an algebraic or explicitly temporal total-current closure for A
and C, substitute its unknown `J_C` for the D5 `J_trial` argument, include every
active chain-rule path in the effective loop, and define gain, regularity,
support, singular-boundary, and failure semantics. D5 does not pre-authorize
either closure class.

## Claim Boundary

D5 supports only:

```text
two bounded candidate-specific directional Read-Back operator families
one named missing typed Read-Back derivation
an exact graph-cochain, passive, covariance, reversal, support, and read-off contract
```

It does not support:

```text
runtime implementation or runtime reachability
physical identification of either explicit operator as non-absorbable Read-Back
regular total-current closure
write-back or a closed reflexive loop
temporal current persistence
topology-event Read-Back
architecture selection
normative GRC9V4 specification
```

The experiment owner accepted D5 as `accepted_bounded` on 2026-08-24. D6 is
authorized; normative specification, runtime implementation, and `src/` changes
remain unauthorized.
