# D7 Closed Write/Read Loop

**Record:** `GRC9V4-CD-D7-v1`  
**Status:** accepted bounded  
**Decision digest:** `7ffaf92b1672aa4fb116539ca5da36aef8bc7f3caf088827fd71f3ec7b483fea`

## Purpose

D7 asks whether any surviving retained-representation candidate can be written
as a complete cross-beat transition rather than as a collection of one-way
relations. The required architecture-neutral loop is:

```text
retained representation at k
  -> present directional read
  -> authoritative total current J_C[k]
  -> declared downstream state consequence
  -> retained representation at k+1
```

The gate produces one positive but bounded result:

```text
Candidate A:
  complete fixed-topology, fixed-geometry kinetic reduced transition
  closed cross-beat retained-mobility recurrence
  explicit Read-Back subloop is constitutively load-bearing on a declared
  nondegenerate domain
  physical nonabsorbability remains open
  normative structural geometry path still open

Candidate B:
  routed, not rejected

Candidate C:
  source-backed write relation preserved
  routed, not rejected, because retained mediation is not closed
```

D7 does not select A, claim a complete normative GRC9V4 architecture, execute a
runtime probe, or establish structural or temporal stability.

## Why A Can Advance Only On A Reduced Profile

Candidate A has enough accepted pieces to close a graph-native kinetic loop:

- D4 makes positive `W_A` the sole enabled scalar mobility authority;
- D5 supplies the edge-contrast read operator;
- D6 supplies a regular algebraic total-current closure;
- the GRC9V3 implementation supplies exact graph potential, flux,
  conductance-target, and incidence-continuity formulas; and
- D2 permits a one-beat delayed update from postsolve `J_C` and the downstream
  `C` state.

The exact `K_4 -> H_4 -> h_4` map remains underdetermined in the controlling
core theory and was deliberately left open at D4. D7 therefore does not invent
one. It closes A's kinetic recurrence while routing structural cultivation to:

```text
GRC9V4-D7-GLOBAL-METRIC-AND-STRUCTURAL-CULTIVATION-CLOSURE
```

This fixed-geometry qualifier is a verification/design subprofile. It is not a
claim that the intended GRC9V4 runtime has fixed geometry or fixed topology.

## Candidate A Causal State

On the admitted D7 stratum, the independent cross-beat coordinates are:

```text
X_A[k] = (
  C[k],
  W_A[k],
  fixed topology and boundary profile,
  declared lifecycle parameters
)
```

`W_A` is positive retained mobility. `J_C` is authoritative within the beat and
as the declared write input, but it is not independently temporalized. The
following are derived stage surfaces:

```text
differential summaries
potential Phi_A
baseline current J0_A
instantaneous reference W_hat_A
retained contrast q_A
total current J_C_A
read current j_A
write target W_drv_A
```

Serializing one of these surfaces for exact restoration or telemetry does not
give it independent authority. A stale or independently modified cache must not
change the transition.

The enabled profile consumes no incoming or prior-current cache. Every current
surface is reconstructed from `C[k]`, `W_A[k]`, fixed topology and geometry,
and declared parameters. A successor that consumes unreconstructable lagged
current must add it to the Markov state rather than hide that history in a
cache.

## Exact A Reduced Transition

### 1. Baseline transport

The enabled A profile uses the GRC9V3 graph potential and flux forms with
authoritative `W_A` replacing reconstructed conductance:

```text
Phi_A,i =
  kappa_c sum_(e incident to i) W_A,e (C_i - C_neighbor(e,i))
  - V_site'(C_i)

J0_A,e = -eta W_A,e (Phi_A,u - Phi_A,v)
```

This is the complete reduced A baseline map. It is graph coupled because
changing one edge mobility changes incident node potentials and therefore may
change several edge currents.

### 2. Instantaneous reference

Define the existing positive conductance functional:

```text
G_W,e(C,J) = max(
  w_min,
  exp(
    -alpha (C_u + C_v) / 2
    -beta ||gradient C_u - gradient C_v||^2 / 2
    -gamma J_e^2 / 2
  )
)
```

The enabled A profile freezes:

```text
W_hat_A,e[k] = G_W,e(C[k], J0_A[k])
```

after constructing `J0_A` and before constructing `q_A` or solving total
current. This is a revision-distinct enabled-profile staging choice. It avoids
making an independently carried incoming current into hidden cross-beat state,
and it keeps the accepted D6 current equation linear. It is not the disabled
GRC9V3 stage order; D9 must prove exact disabled-profile reduction separately.
`W_hat_A[k]` is therefore the pre-read reference. It is not the
postcontinuity write target and is not a future `W_hat_A[k+1]` surface.

### 3. Directional read and total current

The accepted D5/D6 equations remain unchanged:

```text
q_A,e = (W_A,e - W_hat_A,e) / (W_A,e + W_hat_A,e)

j_A,e = chi_A q_A,e J_C_A,e

J_C_A,e = J0_A,e + zeta_A j_A,e

J_C_A,e = J0_A,e / (1 - zeta_A chi_A q_A,e)
```

The selected profile requires positive `W_A`, positive `W_hat_A`, and

```text
0 <= zeta_A <= zeta_bar_A < 1.
```

`J_C_A` is the only current consumed by continuity and the future retained
write. `j_A` is not a direct write input.

The explicit Read-Back arrow is constitutively load-bearing only on admissible
states where `J0_A`, `q_A`, `chi_A = 1`, `zeta_A`, and downstream writer
sensitivity are nonzero. Because `chi_A` is a binary gate, the correct proof
object is the exact on/off difference:

```text
J_C_A(chi_A=1) - J_C_A(chi_A=0) =
  J0_A zeta_A q_A / (1 - zeta_A q_A)
```

is nonzero. At `q_A = 0`, `J0_A = 0`, `chi_A = 0`, or `zeta_A = 0`, the
explicit subloop is open even though the direct retained-mobility recurrence
may remain.

The domain is nonempty. A fixed two-node, one-edge graph with positive unequal
node coherence, positive `W_A`, a linear site potential with the same constant
derivative at both nodes, `W_A != G_W(C,J0_A)`, `chi_A = 1`, `0 < zeta_A < 1`,
`gamma > 0`, and sufficiently small `Delta_t` gives nonzero `J0_A`, `q_A`, the
binary-gate current difference, and generically the current-sensitive writer,
while preserving nonnegative coherence.

### 4. Continuity

On the closed internal graph profile:

```text
C_i[k+1] =
  C_i[k]
  - Delta_t div_E J_C_A[k]_i.
```

Declared boundary or source terms may be added only with their existing
ledger. Antisymmetric internal edge current conserves total node coherence.
Failure of non-negativity or the declared measure budget rejects the whole
step before the retained write is committed.

### 5. Retained write

After continuity, construct:

```text
W_drv_A,e[k] = G_W,e(C[k+1], J_C_A[k]).
```

The exact downstream mediator is:

```text
D_A[k] = (C[k+1], J_C_A[k]).
```

It excludes diagnostic `j_A`, stale current, postsolve geometry, and any
future next-beat current.

Let:

```text
a_A = exp(-Delta_t / tau_A),
0 < a_A < 1.
```

The exact retained update family is:

```text
log W_A,e[k+1] =
  a_A log W_A,e[k]
  + (1 - a_A) log W_drv_A,e[k]
```

or equivalently:

```text
W_A,e[k+1] =
  W_A,e[k]^a_A
  W_drv_A,e[k]^(1-a_A).
```

This is a minimal V4 constitutive completion built from the existing positive
conductance surface. It is not uniquely derived from the core RC papers. It is
one deterministic, edge-local, one-writer, one-beat-delayed candidate law. Its
constitutive reason is narrower than "an EMA gives memory": log interpolation
preserves the positive multiplicative mobility domain, relaxes toward one
native conductance target, and provides bounded retention and release without
another cache or clipping history.

No post-update clipping or global normalization is introduced. If both inputs
lie in `[w_min, 1]`, their weighted geometric mean remains in that interval.
The initial profile uses no RNG and no hidden optimizer, queue, accumulator, or
previous target.

The inherited `w_min` in `G_W` is a load-bearing constitutive floor, not
numerical hygiene. D8 may use classical derivatives only on the interior where
the unfloored exponential is strictly above `w_min`. Floor activation is a
nonsmooth boundary and requires one-sided or tangent-cone treatment rather than
silent differentiation through `max`.

## Formation, Retention, And Release

The write law gives the three lifecycle distinctions concrete meanings.

There are not three independent writers. The single logarithmic increment is:

```text
Delta log W_A = (1-a_A) (log W_drv_A - log W_A).
```

Formation is the matched current-dependent difference in `log W_drv_A`; carry
is the `a_A` fraction of the prior residual; release is relaxation of that
residual toward the stationary no-forming target. These are causal
attributions of one multiplicative writer, not additive update terms whose
ordering could change the result.

**Formation** is an attributable difference from a matched zero-forming-current
row. The `J_C^2` term changes `W_drv_A` and therefore changes `W_A[k+1]`.
Initialization of nonneutral `W_A` is not formation.

**Retention** is the future causal availability of the nonneutral `W_A` state.
For a stationary target and no forming current, the logarithmic residual
decays by `a_A` per beat. While nonzero, it still changes future mobility,
baseline current, read contrast, and the next write.

**Release** is the constitutive convergence toward the zero-current
instantaneous target under repeated no-forming-current steps. It does not use
reset, silent overwrite, clipping, or an external cleanup producer.

`a_A` near one is not evidence by itself. Runtime formation, persistence,
release, and causal attribution remain post-spec verification obligations.

### Moving neutral attribution

`R_W` or `q_A` can move because authoritative `W_A` was written or because the
derived pre-read reference `W_hat_A` moved. These are not equivalent:

```text
carrier write or release:
  W_A[k+1] differs from W_A[k] under the authoritative writer

reference-surface motion:
  W_hat_A changes while W_A is held fixed

relation neutralization:
  R_W or q_A moves toward zero by either route
```

Only the first route can support an A write/release claim. Pre-read `W_hat_A`
and postcontinuity `W_drv_A` are distinct stages of one beat, not two
independent formation events. Traversal with no attributable `W_A` change is
enactment, not formation.

## What The Closed A Loop Is

The always-present direct retained-mobility recurrence is:

```text
W_A[k]
  -> Phi_A[k]
  -> J0_A[k]
  -> J_C_A[k]
  -> C[k+1] and W_drv_A[k]
  -> W_A[k+1].
```

The explicit Read-Back-participating subloop is:

```text
W_A[k], W_hat_A[k]
  -> q_A[k]
  -> j_A[k]
  -> J_C_A[k]
  -> W_drv_A[k]
  -> W_A[k+1].
```

This is a source-legible cross-beat recurrence, not merely a one-way
retained-to-current or current-to-state path. The two classifications remain
separate: setting `chi_A = 0` opens the explicit subloop but can leave the
direct retained-mobility recurrence closed. D7 establishes constitutive
sensitivity of the explicit subloop on its nondegenerate domain; it does not
establish empirical physical nonabsorbability.

The structural route remains:

```text
j_A[k]
  -> zeta_A j_A[k] tensor j_A[k]
  -> K_4[k+]
  -> H_4
  -> h_4
  -> future geometry-conditioned dynamics.
```

The first tensor arrow is admitted and staged after the current solve. The
`H_4` arrow is not closed. Recording `K_4` or `j tensor j` therefore does not
establish structural cultivation.

The temporal geometry surfaces are therefore explicit:

```text
K_pre[k]      = fixed admitted structural surface underlying h_pre[k]
h_pre[k]      = fixed admitted geometry used by Phi_A, J0_A, and D6
K_plus_j[k]   = postsolve structural input record
h_read_plus   = undefined without H_4
K[k+1]        = undefined without the structural update/H_4 contract
h[k+1]        = undefined without H_4
```

Neither postsolve surface can re-enter the current D7 beat.

## Arrow-Specific Loop Tests

The design-level closure is established by four mathematical interventions,
not by endpoint correlation:

```text
W_A intervention
  -> changes q_A and j_A on a nondegenerate admissible state

chi_A intervention with the baseline frozen
  -> changes J_C and D_A when zeta_A q_A J0_A is nonzero

postsolve J_C writer intervention
  -> changes W_drv_A and W_A[k+1] when the declared writer sensitivity is nonzero

write-off after the same valid current/continuity stages
  -> changes the next-beat q_A, j_A, or J_C on a nondegenerate state
```

These are constitutive proofs. They are not runtime interventions, empirical
channel attribution, or proof that no admissible effective-mobility
reparameterization exists.

The A rival-carrier graph keeps `C`, derived `W_hat_A`, fixed geometry,
topology, boundary/source ledgers, and any normalization/global state distinct
from authoritative `W_A`. Incoming current is absent rather than silently
matched. Persistent topology mutation invalidates this fixed-stratum
attribution even though topology is not the claimed retained representation.

## Staging And Atomicity

The complete reduced A stage order is:

```text
1. validate C[k], W_A[k], topology, boundary, and parameters
2. rebuild differential summaries from C[k]
3. construct Phi_A[k] and J0_A[k]
4. construct and freeze W_hat_A[k]
5. construct q_A and the D5 read operator
6. solve the regular D6 total-current equation
7. derive j_A and validate support, condition margin, and residual
8. form the staged j tensor j K contribution without geometry re-entry
9. apply continuity with authoritative J_C_A[k]
10. validate C non-negativity, measure, and boundary accounting
11. rebuild every differential and gradient summary used by G_W from C[k+1]
12. construct W_drv_A[k] without reusing pre-continuity C[k] caches
13. write W_A[k+1] once
14. validate W bounds and lifecycle receipt
15. commit the reduced post-state atomically
```

New `W_A[k+1]` cannot affect `J_C[k]`. Postsolve geometry cannot re-enter the
same current solve. Either change would reopen D6 and require a new complete
effective derivative and branch rule.

This stage order is Jacobian-ready on the interior where `G_W` is above its
floor, the D6 inverse is regular, and the coherence budget is valid. D8 must
differentiate and compose every declared stage. Floor activation, current
singularity, coherence-budget failure, and topology or boundary events are
named nonsmooth/event boundaries rather than ordinary smooth recurrence.

## A Read/Write Controls

The load-bearing controls include:

```text
passive zero-current
no forming or write input
write-off
retained-state frozen
read-off
gain-off
carrier-neutral
loop-open before current
loop-open after current
rival C path
rival topology path
rival boundary path
rival cache path
current-authority swap
same-beat new-W read
same-beat geometry re-entry
direct-j write
physical current reversal
edge-coordinate reversal
graph isomorphism
multiwrite order
hidden helper state
administrative reset as release
initialization as formation
silent clipping or normalization
formation attribution
driver exhaustion
large tau or a close to one as retention proof
scalar field as signed-chirality memory
direct path as Read-Back relabel
explicit-read load-bearing domain
moving-neutral attribution
same-beat reference/target double counting
lagged-current hidden state
traversal as formation
floor saturation as stability
explicit-channel absorbability
K tensor as executed geometry
```

Because `W_hat_A` depends on the baseline generated by `W_A`, carrier-neutral
and loop-open-before-current controls require a preregistered admissible fixed
point or matched prepared row satisfying
`W_A = G_W(C, J0_A(W_A,C))`. They cannot impose `W_A = W_hat_A` post hoc. If no
such row exists on the tested stratum, that control is unavailable and the
corresponding attribution fails closed.

Three parity questions remain distinct. Arbitrary stored-edge coordinate
reorientation transforms cochain currents covariantly while leaving scalar
`W_A`, `W_hat_A`, `W_drv_A`, and `q_A` invariant. The explicit `J_C^2` factor
inside `G_W` is also sign-even. A physical current-history reversal, however,
generally changes `C[k+1]` and its differential summaries, so the complete
`W_drv_A = G_W(C[k+1],J_C)` and `W_A[k+1]` need not be invariant. Candidate A
stores no intrinsically signed cochain or chirality coordinate, but its scalar
spatial pattern may still distinguish reversed physical histories through the
continuity-mediated `C` path.

## A Absorbability Boundary

D7 can now narrow the A mathematical-absorbability debt because the complete
reduced baseline map is explicit. The read factor acts after the graph-coupled
potential map:

```text
J_C = Diag(1 / (1 - zeta q_A)) J0(W_A, C).
```

Changing an edge `W_A` changes both its direct mobility factor and incident
node potentials, potentially changing several edge currents. A general
nonuniform post-current diagonal scaling is therefore not universally the same
as an edge-local mobility replacement.

This does not prove nonabsorbability on every restricted fixture or symmetry
class, nor does it rule out a state-dependent global reparameterization. After
D8, a named pre-D10 A absorbability classification must resolve the selected
model class. D10 consumes that answer; it does not perform the unresolved
technical derivation. Exact absorption demotes the explicit A Read-Back label
to retained-mobility recurrence.

## Candidate B

B remains routed, not rejected. It still lacks:

```text
typed T_B domain, rank, orientation, and units
exact bounded nonresource U_B update and release
G_B from T_B to geometry or another native consumer
typed R_B one-cochain operator
regular total-current closure
```

Copying A's low-pass update or C's Hodge operator would not solve those missing
roles. An EMA by itself would be a slow cache substitute, not a B architecture.

## Candidate C

C retains the strongest source-backed write relation:

```text
D_t^vol C_M =
  -P_M div J_C
  + (D_t^write P_M) C
```

with the projected boundary source added when present. Its discrete
bookkeeping identity remains:

```text
T_C[k+1] - T_C[k] =
  S[k](C[k+1] - C[k])
  + (S[k+1] - S[k])C[k+1].
```

This is a real write equation, but not yet a closed C loop. The missing map is:

```text
T_C, C, declared selector context
  -> H_M
  -> h_M
  -> parameterized R_C and baseline geometry.
```

At fixed `h_M`, changing `T_C` must leave the current parameterized operator
unchanged. Without an admitted `H_M`, a package-level `h_M` swap is off-manifold
and cannot prove retained-sector mediation. Generic `C` continuity, projector
motion, and rank changes also cannot be renamed as retained write-back,
formation, or release.

Both a direct retained-geometry recurrence and explicit Hodge Read-Back
participation are therefore blocked, not merely untested. The selected sector
is not yet load-bearing because no lawful selected-content versus matched-
complement intervention can propagate through `H_M`. Physical flow reversal
may change authoritative `C` and selected-sector content, but that fact alone
does not establish retained cochain orientation memory.

C is routed to the existing retained-geometry closure, not rejected.

The two terms in the discrete identity remain separately reported as selected
content change and selector/basis motion. D7 admits no independent `T_C`
writer. A future C transition must factor through authoritative `C[k+1]` and a
constitutive `S[k+1]`; it must also select lagged, staged, or uniquely regular
fixed-point selector/geometry timing.

No lawful C runtime `write_off` or frozen-carrier switch is currently admitted.
Holding `T_C` fixed while `C` and `S` evolve is generally off-manifold. A
successor must use an admissible matched `C`-state counterfactual or retain the
missing-discriminator debt. `T_C = 0` is not presumed to be neutral.

## Candidate Partition After D7

```text
candidate_set_after_D7 = [A, B, C]

D8_eligible_candidate_set = [A]
routed_candidate_set = [B, C]

complete_reduced_transition_count = 1
complete_normative_transition_count = 0
closed_write_read_loop_count = 1
closed_retained_mobility_recurrence_count = 1
constitutively_load_bearing_explicit_Read_Back_subloop_count = 1
empirically_attributed_explicit_Read_Back_loop_count = 0
closed_structural_cultivation_loop_count = 0
candidate_rejected_count = 0
architecture_selected = false
```

D8 is authorized only to analyze A's concrete reduced transition and the
explicit consequences of its missing structural map. It may not convert the
fixed-geometry audit profile into normative V4 scope or analyze B/C as though
their transitions were complete.

## Debt And Audit

D7 carries 16 current open debts and dispositions all 25 immediate
D6-generation debts and all 20 transitively
inherited debt rows. Twenty-three immediate rows are explicitly resolved or
superseded into named D7 debts; two nonblocking rows remain independently
carried. Sixteen transitive rows remain pre-D10 blockers. D10 consumes a
three-way union:

```text
current D7 open_debt
+ unresolved immediate predecessor dispositions not explicitly superseded
+ unresolved transitive predecessor dispositions not explicitly superseded
```

The blocker set is every row in that union marked `must_close_before_D10`.
Missing or malformed supersession keeps the predecessor row live.

Pre-D10 technical debts cannot resolve at D10. A's core-status,
absorbability, and units/gauge results must be produced by D8 or named pre-D10
audits and then consumed by D10. Reduced temporal-transition stability and
floor nonsmoothness belong to D8; normative structural continuation/stability
through `H_4` remains under the separate global structural-cultivation debt and
requires later reanalysis after that map exists.

The original 72-row pressure audit covers:

```text
current and writer authority
pre-read and cross-beat staging
exact A equations and bounds
formation, retention, release, and capacity
passive, read-off, gain-off, and loop-open controls
rival carriers and hidden state
orientation, covariance, multiwrite, and RNG
failure atomicity
reduced versus normative geometry scope
A absorbability
B/C routing discipline
debt persistence and authorization boundaries
```

A second 96-row adversarial matrix responds item by item to the closure audit.
It records the direct-versus-explicit-loop correction, exact downstream
mediator, moving-neutral attribution, lagged-current exclusion, rival-carrier
graphs, C's unavailable on-manifold controls, Jacobian-ready factorization,
and all D8/D9/D10 deferrals. No audit item is silently treated as evidence.

## Claim Ceiling

D7 supports only:

> One bounded complete Candidate A fixed-stratum kinetic transition with a
> closed direct retained-mobility recurrence and a constitutively load-bearing
> explicit Read-Back subloop on a declared nondegenerate domain. Physical
> nonabsorbability remains open. Candidate B, Candidate C, and the normative
> structural geometry path remain routed to named missing derivations.

It does not support:

```text
complete normative GRC9V4 architecture
structural cultivation
structural or temporal stability
runtime reachability or replay
physical identification of a nonabsorbable Read-Back channel
topology-event retention or transport
candidate ranking or architecture selection
normative specification or implementation authority
learning, semantic memory, choice, or agency
```

## Acceptance And Authorization

Current state:

```text
status = accepted_bounded
D8_authorized = false
D8_authorization_status = deferred_pending_separate_human_direction
D8_authorization_requires_separate_human_direction = true
D8_scope = A fixed-stratum kinetic reduced transition only
B_or_C_D8_analysis_authorized = false
specification_authorized = false
runtime_implementation_authorized = false
src_change_authorized = false
```

D7 acceptance does not authorize D8. A separate human direction is required.
The later normative specification and implementation must also make the
post-continuity refresh explicit: every differential or gradient summary used
by `G_W(C[k+1], J_C[k])` is rebuilt from `C[k+1]`; pre-continuity `C[k]`
summaries cannot be reused.
