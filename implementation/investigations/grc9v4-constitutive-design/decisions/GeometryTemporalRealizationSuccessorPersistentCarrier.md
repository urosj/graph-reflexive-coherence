# Geometry-Temporal Realization Successor: Persistent Structural Carrier

**Record:** `GRC9V4-GTRS-PC-v1`  
**Status:** `accepted_bounded`  
**Disposition:** `accepted_bounded_persistent_K4_carrier_family_complete_A_C`  
**Decision digest:** `d1e38d6aa36b03154715c1e26c0b4a1b181dab19ed4bbfbd1575c94c9962e49a`  
**Runtime or `src/` changed:** `false`

## Purpose

GTRS-PC is the last minimum realization-family pressure before comparative
synthesis. It asks whether Candidate A and Candidate C can close a complete
step when geometry, or a sufficient structural coordinate for geometry,
becomes explicit causal state.

The positive burden is stronger than merely serializing a value. The carrier
must:

```text
add capability beyond the accepted local invariant-section RG result
have one declared authority and writer
form, persist, reconfigure, and release without hidden refresh
remain bounded without append-only history
participate in exact snapshot, restoration, reset, and migration semantics
distinguish same-carrier-space context changes from carrier-space events
feed a later causal substage before atomic commit
```

The gate applies the same burden to A and C. It does not select either
candidate or rank PC against coupled, operator-split, or reconstructed
geometry.

## Theory Boundary

The mature Read-Back paper keeps the coherence-only state at

```text
S_coh = (C,J_C)
```

and explicitly does not restore an independent memory field as a core
primitive. It also says that failed Markov sufficiency could require explicit
history, delay, or additional state. GTRS-PC therefore has a precise status:

```text
persistent carrier = revision-specific constitutive completion candidate
persistent carrier != inherited coherence-only RC primitive
PC success != proof that coherence-only Markov closure fails
```

PC is also not ontology-neutral relative to the other realization families. It
adds the independently serialized, nonresource structural authority anticipated
by D1's independent-carrier family to A's mobility semantics or C's sector
semantics:

```text
A_PC = A + independent B-like K_4 structural state
C_PC = C + independent B-like K_4 structural state
```

This is a realization-local ontology effect, not merely a different ordering of
the CI, OS, or RG equations.

The historical slow-field form

```text
tau_M dM/dt = -M + F
```

motivates a minimal formation/forgetting writer. It does not uniquely derive or
normatively authorize the writer used here.

## Primary Carrier

For candidate `a` in `{A,C}`, add one authoritative coordinate

```text
Z_4,a,k in B_R,a subset K_4,a.
```

`Z_4` has the same candidate-specific structural type as the accepted
`Delta K_4` source. It is not full geometry, coherence resource, `W_A`, `T_C`,
current, solver state, or cache.

The read path is

```text
K_4,a,k = K_4,base + Z_4,a,k
h_a,k   = H_profile(K_4,a,k).
```

At fixed `h_a,k`, execute the accepted candidate-local current construction and
derive

```text
S_a,k = Delta K_4,a(J_C,a,k,h_a,k).
```

The frozen PC writer is

```text
a_PC,k = exp(-Delta_t,k / tau_PC,a),       tau_PC,a > 0

Z_4,a,k+1 = a_PC,k Z_4,a,k + (1-a_PC,k) S_a,k.
```

This is the exact zero-order-hold step of

```text
tau_PC,a dZ_4,a/dt = -Z_4,a + S_a
```

when `S_a` is held over one beat. It is a frozen family-local completion, not a
claim that this is the unique RC temporalization.

## Boundedness And Capacity

Boundedness cannot be established by assuming that a frozen carrier set already
contains every source generated from that set. Declare a candidate-specific
`K_4` norm and compact base-state chart `K_X,a`, then define

```text
B_R,a = {Z_4,a : ||Z_4,a||_K <= R_a}

m_a(R_a)
  = sup_{X in K_X,a, Z in B_R,a} ||S_a(X,Z)||_K.
```

The exact carrier-domain admission criterion is

```text
m_a(R_a) <= R_a

H_profile(K_4,base + B_R,a) subset H_adm.
```

The source must also remain defined throughout that ball. Require

```text
(X, H_profile(K_4,base+Z)) in D_reg,a
  for every X in K_X,a and Z in B_R,a

inf_{X,Z} sigma_min(D_J F_J,a) >= m_J,a > 0
```

in the declared current metric. For A, `D_reg,A` includes the floor-inactive,
positive-domain fixed-geometry conditions. For C, it includes fixed selector
rank, strict gap, positive domain, and the accepted fixed-geometry current
conditions. Compact reference charts strictly inside those regular domains and
continuity supply a positive regularity radius `R_reg,a`.

A constructive sufficient condition is

```text
||S_a(X,Z)||_K <= M_0,a + L_Z,a ||Z||_K
0 <= L_Z,a < 1

M_0,a / (1-L_Z,a)
  <= R_a
  <= min(R_profile_adm,a, R_reg,a).
```

On a smooth source family whose `M_0,a` and `L_Z,a` scale continuously to zero
with the declared source coupling, any positive reference-geometry
neighborhood admits a nonzero sufficiently small coupling profile. Thus the
result freezes a constructive parametric local invariance theorem. It does not
instantiate numerical `M_0`, `L_Z`, `R`, profile-radius, `R_reg`, or `m_J`
values and does not claim an unconditional carrier domain.

For nonnegative step duration,

```text
0 <= a_PC <= 1.
```

Once the exact or sufficient criterion holds, both `Z_4` and `S_a` belong to
`B_R,a`. The writer is therefore a convex combination of two points in
`B_R,a` and stays there without clipping, projection, or post-hoc
normalization. The carrier has fixed dimension on the declared topology and
cannot become an append-only history log.

The primary positive-duration profile requires

```text
0 < a_PC < 1.
```

The case `a_PC=1` at positive duration would provide retention without native
release and is excluded. At `Delta_t=0`, `a_PC=1` is only the smooth identity
reference.

## Formation, Persistence, And Release

From neutral state, a nonzero source forms the carrier:

```text
Z_4=0, S_a!=0
  -> Z_4+ = (1-a_PC) S_a != 0.
```

When the qualifying source is absent,

```text
S_a=0
  -> Z_4+ = a_PC Z_4.
```

Thus a nonzero carrier survives at every finite positive time while contracting
toward zero. This is finite-time retention with asymptotic native release, not
a finite release event. No threshold label, administrative reset, or hidden
producer refresh is needed.

For variable positive step durations, let

```text
T_n = sum_{k<n} Delta_t,k.
```

The exact zero-source and constant-source laws are

```text
Z_n     = exp(-T_n/tau_PC) Z_0
Z_n - S = exp(-T_n/tau_PC) (Z_0-S).
```

Consequently, convergence to zero or constant `S` requires `T_n -> infinity`.
An exotic shrinking-step sequence with finite accumulated time is not claimed
to complete asymptotic release.

For a constant source, `Z_4` converges to that source. A changed or opposing
source reconfigures the carrier through the same writer. Source composition is
completed by the accepted candidate structural map before the one PC writer;
external producer order is not stored.

The same sufficient-domain hypothesis gives a strict matched-forcing
contraction. For fixed base-state and context sequences,

```text
||U_X(Z)-U_X(Ztilde)||_K
  <= [a_PC + (1-a_PC)L_Z] ||Z-Ztilde||_K,

a_PC + (1-a_PC)L_Z < 1.
```

Thus the primary writer contractively forgets carrier-state differences under
matched future forcing. This strengthens finite information capacity without
turning the carrier into an append-only history.

## D2 Intervention Semantics

The D2 interventions remain causally distinct even when two rows produce the
same scalar update:

```text
initialization:
  Z_4 = declared construction baseline; primary neutral baseline is zero

no forming or write input:
  S_a = 0
  Z_4+ = a_PC Z_4

write off:
  suppress formation coupling even if a qualifying source exists
  Z_4+ = a_PC Z_4
  record a write-off receipt distinct from natural source absence

retained state frozen:
  Z_4+ = Z_4
  current geometry still reads committed Z_4
  no formation or release is claimed

administrative reset:
  Z_4 -> declared reset baseline
  does not count as native release

PC disabled:
  Z_4 = 0
  Z_4+ = 0
  h = h_ref
```

When PC remains enabled, `chi_a=0` or `zeta_a=0` stops new inscription by
setting `S_a=0`; it does not erase historical state. Existing `Z_4` continues
to condition the current through `h(Z_4)` and relaxes as `Z_4+=a_PC Z_4`.
This intentionally differs from instantaneous CI/OS gain-off semantics.

## Complete Step

The common stage order is:

```text
1. validate topology, K_4 representation, context, profile, and Z_4 in B_R
2. derive h_k from committed Z_4,k
3. derive candidate-local fixed-h operator surfaces
4. solve the accepted D6-v2 total current J_C,k
5. derive j_k and S_k = Delta K_4(J_C,k,h_k)
6. apply authoritative continuity once to obtain C_k+1
7. execute A's unchanged W writer or rederive C's poststate sector
8. compute Z_4,k+1 = a_PC Z_4,k + (1-a_PC) S_k
9. validate and atomically commit all candidate and carrier state
```

New `Z_4,k+1` is not read during the same beat. There is no simultaneous root,
same-beat geometry corrector, serialized current, or serialized full geometry.
Any substage failure aborts before any commit.

## Candidate A

Candidate A has complete PC state

```text
X_PC,A = (C,W_A,Z_4,A).
```

`W_A` remains the sole mobility authority and its accepted post-continuity
log-geometric writer is unchanged. `Z_4,A` owns only the persistent global
profile perturbation. It cannot write `W_A` directly or duplicate its history.

At `h_A(Z_4,A)`, the accepted fixed-geometry A current solve produces the
authoritative current and accepted `S_A`. The PC writer then updates `Z_4,A`
for the next beat.

```text
A_PC disposition = bounded_complete_realization
```

## Candidate C

Candidate C has complete PC state

```text
X_PC,C = (C,Z_4,C).
```

`T_C` remains the derived projected coherence sector. It is neither serialized
nor independently written. At `h_C(Z_4,C)`, the fixed-rank, strict-gap C chain
derives `P_M`, `T_C`, `H_M`, `I_4M`, and `R_C`, solves the accepted current
closure, and produces accepted `S_C`. Continuity commits `C`; the PC writer
commits `Z_4,C`.

```text
C_PC disposition = bounded_complete_realization
```

## Capability Beyond RG

The accepted RG realization is locally single-valued:

```text
h = Gamma_a(X_a)
```

for one fixed context and frozen extension completion. PC instead declares

```text
(X_a,Z_4,a^(1))
(X_a,Z_4,a^(2))
```

as distinct complete states even when their base candidate state `X_a` is the
same. Distinct carrier histories can therefore remain distinct in the complete
PC state and can produce distinct geometry.

At vanishing geometry sensitivity,

```text
D_Z U_PC,a = a_PC I,
```

which is nonsingular for `0<a_PC<1`. By openness of invertibility,
`D_Z U_PC,a=a_PC I+O(epsilon_H)` remains nonsingular on a sufficiently small
declared geometry-coupling chart. PC therefore supports persistent independent
historical-state capacity now.

Choose the carrier difference along an accepted D8-A direct-field visibility
direction. Then

```text
D_Z h[delta Z] != 0
```

and the geometry difference enters a named A or C current-equation term. This
supports equation-level path dependence unavailable to a single-valued
`Gamma(X)`.

PC also does not require inversion of the base commit map, graph-transform
contraction, or invariant-section uniqueness. It therefore remains a defined
realization where RG reconstruction is nonunique or unavailable, provided the
fixed-geometry candidate substeps and carrier domain remain admissible.

This is a capability distinction, not a proof of a larger numerical domain.
Base-state hysteresis or a nonzero future `C`/`W` endpoint difference remains
behind the A/C complete-chain witnesses.

## State Lifecycle

The snapshot contract includes:

```text
current Z_4 value and type
graph identity
PC enabled/profile identity
tau_PC
reset-baseline Z_4
```

Save/load restores current state and reset baseline before continuation.
`reset()` returns to the construction baseline, not the checkpoint value.
`set_state()` does not silently rebase. Duplication copies carrier state and
baseline without shared mutable storage.

Migration from an existing non-PC A or C state initializes `Z_4=0` and records
that no prior PC history was reconstructed. Downgrading from PC may archive and
drop `Z_4` only through explicit migration; it is not native release. Profile
mismatch fails closed.

Changing `H_profile`, `K_4,base`, the `K_4` representation, carrier norm/domain,
or writer/profile semantics is not an ordinary context change, even when array
dimensions match. It requires an explicit profile transition or migration and
target-domain/current-regularity re-admission. Identical serialized bytes may
not silently acquire new physical meaning.

In the disabled PC profile:

```text
Z_4 = 0
Z_4+ = 0
h = h_ref.
```

This exactly removes PC, but it reduces only to the candidate A or C reference-
geometry transition. Full V3 transition/lifecycle reduction remains D9 debt.

## Context, Topology, And Events

The positive result is fixed-topology and fixed `K_4` representation. Candidate
C's smooth analysis chart also requires fixed selector rank and strict gap.
Changes are partitioned by what they do to carrier authority:

```text
representation-preserving context or boundary change:
  retain Z_4
  recompute all candidate surfaces under the new declared data
  require profile, K_4 base/representation, carrier domain, and writer semantics unchanged
  continue when the deterministic runtime change stays in admitted domains

same-space but nonsmooth candidate change:
  continue only through an explicit deterministic runtime map
  block classical derivative and smooth-chart claims at the change

carrier-space-changing topology/reindex/split/merge/birth/death event:
  require L_event^K4 or abort atomically before mutation
```

A Candidate C rank change is outside the positive smooth chart and requires an
explicit candidate transition or fails closed. It does not automatically imply
that global `K_4` changed. Event termination is not carrier transport.

A future `L_event^K4` must freeze source and target spaces, covariance,
boundedness, profile admissibility, split/merge/birth/death conflict handling,
resource nonduplication, event receipts, and replay identity. Until then, PC is
not a topology-capable V4 result.

## Analysis Surface

For committed state `(X_a,Z_4,a)`, the transition has block Jacobian

```text
M_PC,a = [ D_X Phi_a    D_Z Phi_a ]
         [ D_X U_PC,a   D_Z U_PC,a ]
```

with

```text
D_Z U_PC,a
  = a_PC I
    + (1-a_PC)(D_J S_a D_Z J_a + D_h S_a D_Z h_a),

D_Z h_a = D_K H_profile,

D_Z J_a
  = -(D_J F_J,a)^-1 D_h F_J,a D_Z h_a.
```

This is an architecture-local derivative contract on A's floor-inactive and
C's fixed-rank, strict-gap smooth charts. It is not a numerical multiplier,
stability, or complete-chain witness.

## Comparison-Time Alternatives

The primary architecture stores full `K_4`, but that need not be the minimal
causal carrier. For affine `H_profile`, let

```text
N = kernel(D_K H_profile).
```

If all accepted runtime maps depend on `Z_4` only through its profile
equivalence class and the projected writer is well defined, the exact carrier
may be reduced to `K_4/N`. If the profile is injective on the admitted source
space, full `K_4` is already minimal. GTRS-COMP must perform this
minimal-sufficient-carrier audit before assigning PC state and lifecycle cost.

The present writer is the **scalar-ZOH `K_4` PC representative**. It is not the
universal persistent-carrier law. A future nonprimary profile may use a typed
contractive operator semigroup with multiple retention timescales, provided it
independently proves source-domain invariance, covariance, and release. No new
PC gate is opened for that alternative now.

COMP must also determine whether the architecture space is really four
exclusive columns or whether history authority is orthogonal to current/
geometry timing:

```text
{CI, OS, lagged/RG timing}
  x
{reconstructed/no persistent state, persistent carrier}.
```

No hybrid campaign is authorized now. If a lawful hybrid could materially
dominate the primary rows, COMP must name the exact missing row before
architecture selection.

## Debt And Claim Boundary

All 39 predecessor live debts are dispositioned. Two RG-specific debts remain
live, one remaining-family debt is superseded, and all 36 inherited rows are
carried. Five PC debts remain:

```text
comparative synthesis
numeric carrier-domain/current-regularity/writer/parameter instantiation
carrier-space-changing topology-event interspace semantics
A base-state complete-chain witness
C base-state complete-chain witness
```

The resulting union is:

```text
2 carried RG debts
+ 36 carried inherited debts
+ 5 current PC debts
= 43 live debts
```

The result supports bounded design-level PC realizations for A and C on
constructively admitted parametric carrier balls, bounded formation and
finite-time retention with asymptotic release, explicit lifecycle contracts,
and genuine independent path-dependent state capacity beyond local RG.

It does not support native-core status, coherence-only failure, runtime
evidence, base-state hysteresis, full-chain nonannihilation, an instantiated
numeric invariant domain, carrier-space event transport, global validity,
family ranking, specification, or implementation.

## Disposition

```text
record = GRC9V4-GTRS-PC-v1
status = accepted_bounded

A_PC = bounded_complete_realization
C_PC = bounded_complete_realization
top_level = accepted_bounded_persistent_K4_carrier_family_complete_A_C

predecessor_live_debts = 39
predecessor_debts_dispositioned = 39
current_debts = 5
live_debt_union = 43
controls = 82

human_acceptance_recorded = true
GTRS-COMP_authorized_after_acceptance = true
GTRS-COMP_authorized = true
D9_authorized = false
runtime_or_src_changed = false
```

No source/runtime implementation change is authorized by this result.
