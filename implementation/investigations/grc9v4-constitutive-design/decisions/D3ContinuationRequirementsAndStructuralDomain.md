# D3 Continuation Requirements And Structural Domain

**Record:** `GRC9V4-CD-D3-v1`
**Status:** accepted bounded
**Decision digest:** `8e7db364cc4402b9794d825629962d1851fc15a2f0b71fa015cfaeb01f42643d`

## Purpose

D3 decides what may count as structural continuation for each D2 survivor. It
does not calculate a continuation spectrum, construct an empirical formed
branch, define the runtime transition, or select the current closure.

The controlling distinction is:

```text
runtime causal coordinate
  != structural continuation coordinate
```

A and B have independent runtime state authority. That does not create a joint
structural functional automatically. C has no independent sector coordinate;
its structural perturbation must remain derived from `C`.

All three candidates survive D3:

```text
V4-A-temporalized-W              = conditionally supported
V4-B-independent-derived-carrier = conditionally supported
V4-C-constitutive-C-sector       = supported bounded
```

No architecture is selected or ranked.

## Two Meanings Of Formed

D2 and D3 use different formation tests:

```text
retained_formed:
  attributable runtime activity moved the retained representation away from
  its neutral or instantaneous baseline

structurally_formed:
  the declared state is a constrained critical point of F_struct on a valid
  tangent or tangent-cone domain
```

Neither implies the other. A retained carrier can exist dynamically away from
a structural branch. A structurally formed state can exist without proving
native write, post-input retention, or Read-Back. A combined retained
structural claim needs both contracts.

To keep that distinction executable, D3 uses two state terms:

```text
structural reference state:
  constrained critical state of F_struct on the declared structural domain

retained structural state:
  structural reference state that also satisfies the D2 retained-formed or
  retaining contract
```

A structural reference state does not have to be produced by the D2 formation
protocol. D2 attribution becomes load-bearing only for the stronger combined
retained-structural claim.

## Structural Vocabulary

D3 freezes four different analytical objects:

```text
F_struct second variation -> structural stiffness alpha
runtime F or generator DF -> temporal rate gamma or multiplier mu
Read-Back derivative      -> response gain beta
spatial graph operator    -> spatial scale lambda
```

These may be related only through a declared representation, clock, mobility or
kinematic map, operator domain, inner product, and reference-space transport.
They are not spectra of one universal generator.

Raw alpha values also require a frozen normalization. Rescaling `F_struct`
rescales its Hessian. Cross-candidate magnitude or softness comparisons are
therefore blocked until the functional normalization, perturbation metric,
constraint normalization, domain, and boundary conditions are common or
explicitly mapped. No universal numerical softness cutoff is admitted by D3.

In particular:

```text
slow temporal mode        != low continuation stiffness
large Read-Back gain      != low continuation stiffness
low graph-Laplacian scale != low continuation stiffness
runtime DF                != structural Hessian
constitutive P_M          != analysis P_slow_analysis
```

## Formed State And Branch

A D3 structural reference state contains:

```text
C_star and conserved charge
candidate parameter, retained representation, or derived sector at star
geometry, measure, support, and boundary state
selected reference-current regime
lifecycle and topology stratum
complete constraint and accounting state
```

Nonneutral initialization, a single snapshot without constrained stationarity,
retrospective projector selection, or a future basin label does not establish
a structural reference state. A retained structural state additionally needs
D2 formation attribution and post-input retention or retaining status.

A formed branch, unqualified in D3, is a smooth family of constrained
structural reference states
`X_star(theta)`. Each point must remain a constrained critical point of the
declared `F_struct`, preserve candidate semantics and the identity basin, and
carry an explicit operator-domain and constraint transport. The branch
parameter `theta` is not runtime time by default.

A retained structural branch is the stronger intersection: the relevant
candidate state along the structural reference branch must also satisfy D2's
retained formation/retention contract.

The constitutive equations, constraints, and branch gauge must declare and
track the reference branch before comparison with a runtime trajectory.
Retrospective fitting of the branch or gauge to observed motion is blocked.

The actual runtime trajectory may approach or track such a branch, but it is
not automatically the branch. Likewise, finite displacement along the branch
is not automatically one continuation eigenmode.

## Reference Transport And Clock

Operators, modes, and projectors at different branch points generally live in
different weighted spaces. Before comparison, D3 requires an identification
map:

```text
U(theta -> theta_0)
```

It transports at least:

```text
volume or measure weight
fiber metric for tensors or cochains
conservation tangent space
boundary conditions and operator domain
candidate parameter or derived selector basis
later isolated spectral-cluster projectors
```

Bare mode comparison across moving spaces is blocked. A topology, rank, mode,
or branch event also blocks classical cross-event comparison until D4/D9
supply the required interspace map.

D3 keeps three clocks distinct:

```text
theta = structural branch parameter
k or t = runtime clock
D8 clock = temporal linearization clock for gamma or mu
```

An adiabatic identification between them requires a declared clock map and
branch-tracking error.

## Structural Cases

D3 admits three structural forms in principle:

### C-only

```text
F_struct(C)
H_C
structural coordinate = delta_C
```

### Conditional C structure

```text
F_struct(C; T_star)
H_C_given_T
structural coordinate = delta_C
frozen parameter = T_star
delta_T is not a structural coordinate
```

### Joint C/T structure

```text
source-backed F_struct(C,T)
H_(C,T)
structural coordinates = (delta_C, delta_T)
```

The joint case needs its own functional, constraints, inner product, and
operator domain. The derivative of the runtime transition `DF(C,T)` cannot be
used as a substitute.

An arbitrary positive `T` or `W` penalty cannot be added merely to manufacture
a stable joint direction. Conversely, omitting every `T`/`W` term and observing
a zero second derivative does not establish a soft mode; it establishes an
unspecified structural direction.

## Candidate A: Conditional C Structure Given W

Candidate A is structurally admitted only on the conditional lane:

```text
F_struct(C; W_star)
H_C_given_W
delta_W = 0 during the structural variation
```

`W` remains an independent runtime causal coordinate, but no current source
derives a joint `F_struct(C,W)`. D3 therefore does not admit `delta_W` as a
continuation coordinate.

The natural retained coordinate is coupled:

```text
R_W = W - W_hat(C, J, h, ...)

delta_R_W
  = delta_W
  - D W_hat[delta_C, delta_J, delta_h, ...]
```

On the conditional lane `delta_W = 0`, but `delta_R_W` generally still changes
with the admitted C/current/geometry tangent. `delta_R_W` and `delta_C` are not
independent structural coordinates.

This is not a rejection of temporalized `W`. It says that D4 must first decide
how `W_star` conditions geometry, mobility, or the structural functional. D7
may then define its temporal transition. If a later claim requires `delta_W`
inside the structural spectrum, a source-backed joint theory or named theory
successor is required.

Small `W` update rates, retained-state persistence, or a history-induced change
of the later `C` branch cannot substitute for low structural stiffness.

## Candidate B: Conditional C Structure Given T

Candidate B has the analogous bounded classification:

```text
F_struct(C; T_star)
H_C_given_T
delta_T = 0 during the structural variation
```

Independent `T` is legitimate runtime state under D1/D2. It may condition the
`C` landscape after D4 defines a constitutive map. But the current sources do
not supply a joint `F_struct(C,T)`, so independent `delta_T` is not yet a
structural continuation coordinate.

The joint case must add a source-backed reason that deformation of `T` itself
is structural. Temporal retained-state dynamics alone do not provide that
reason.

This distinction blocks the EMA trap. An independent Markov memory can be
temporally slow without being structurally soft. Candidate B remains viable on
the conditional lane; its joint structural interpretation remains theory-open.

## Candidate C: C-Only Structure With Derived Sector Tangent

Candidate C fits the source-backed C-only structural domain:

```text
F_struct(C)
H_C
T_C = S(C, ...) C
```

On a smooth fixed-rank stratum, its perturbation obeys:

```text
delta_T_C
  = S_star delta_C
  + D S_star[declared causal perturbations] C_star
```

`delta_T_C` cannot be varied independently. Doing so would manufacture an
extra structural direction and reclassify the candidate toward B.

The constitutive selector `P_M` is also not an analysis-only or retrospectively
selected temporal slow projector `P_slow_analysis`. Candidate C receives no
second alpha spectrum merely because its sector is addressable.

If a composite functional is later written as

```text
F_tilde(C) = F(C, S(C) C)
```

it remains C-only. Its Hessian needs every first- and second-order chain-rule
term through `S(C)`; it is not a joint Hessian evaluated with arbitrary
`delta_T_C`.

Neither a low-alpha result nor an analysis-only or retrospective temporal slow
subspace may define the constitutive selector and then serve as evidence for
that selected sector. This does not prohibit a future runtime-owned dynamic
slow projector. Such a projector is conditionally admissible only when an
executed temporal law, declared clock and branch, isolated sector or event
boundary, and causal runtime consumer exist, together with a self-consistent
projector fixed point whenever Read-Back depends on the dynamically selected
sector. A hard spectral selector still requires an isolated cluster with
projector-level transport, a smooth filter, or a declared event boundary.

Rank changes, mode crossings, sector exit/re-entry, branch transitions, and
topology events are not smooth tangent points. D4/D8 must provide a stratum or
event rule before modes can cross them.

## Reference-Current Support Matrix

D3 crosses every candidate with four current regimes. The matrix contains 12
rows:

| Candidate | No current | Frozen current | Smoothly slaved current | Independently active current |
| --- | --- | --- | --- | --- |
| A | conditional | conditional | conditional | theory-open |
| B | conditional | conditional | conditional | theory-open |
| C | supported | supported | conditional | theory-open |

The regimes mean:

```text
no current:
  J_star = 0 and delta_J = 0

frozen current:
  J_star may be nonzero, but delta_J = 0 and current-mediated geometry is fixed

smoothly slaved current:
  J_star = Phi(structural state) through a unique regular solve
  delta_J = D Phi applied to the admitted structural tangent

independently active current:
  delta_J is independent runtime variation
  no current source supplies the required joint structural operator
```

The active-current rows are `theory_open`, not negative candidate results. The
Continuation Spectrum paper explicitly leaves a joint Hessian or regular
Schur-complement construction open for active recurrent current. A formal
Schur complement without a solved current equation is blocked.

D3 does not choose among these rows. D6 selects the current closure; D8 may use
only the corresponding row after all row conditions are satisfied.

Each structured cell separately records its structural functional, constraint
manifold, admitted tangent, geometry derivative convention, retained-state
role, claim ceiling, and later-gate dependency. In particular, smoothly slaved
rows require all chain-rule effects from a unique regular D6 current solve;
they are not frozen-current rows with a different label.

D3 also leaves D4 ownership open. A cell may use a fixed-geometry partial
Hessian, or a total Hessian after D4 admits and eliminates `h(C,T,W)`. Those are
different operators. If `W` or nonresource `T` changes the metric and therefore
the measure in `Q`, the conservation tangent includes that induced measure
response without reclassifying `W` or `T` as physical resource.

## Admitted Tangent State

Every row begins with the conserved-coherence tangent:

```text
DQ[C_star] delta_C = 0
```

The induced measure response, boundary conditions, support, operator domain,
and nonnegativity tangent must be included. Candidate-specific additions are:

```text
A conditional lane: delta_W = 0
B conditional lane: delta_T = 0
C lane: delta_T_C follows the selector tangent
no/frozen current: delta_J = 0
slaved current: delta_J = D Phi delta_structural
active current: delta_J independent but structural status theory-open
```

The conservation scope must be declared from the actual graph: global,
componentwise, or multi-resource. Symmetry and gauge nulls from conservation,
translations, graph automorphisms, coordinate conventions, branch
parameterization, or unspecified variables must be removed or classified
before `alpha = 0` is called structural marginality.

At active nonnegativity, clipping, saturation, or inequality bounds, the
admissible object may be a tangent cone or variational inequality rather than a
linear tangent space. At a kink, hard cutoff, or rank crossing, “Hessian
undefined” is not “alpha equals zero.”

## Topology And Event Boundary

The local derivative envelope is:

```text
fixed topology
fixed rank
fixed operator domain
no unresolved mode or symmetry crossing
```

This is a verification envelope, not a fixed-topology GRC9V4 profile. The
normative target remains topology-capable. Event-local state may be recorded,
but lineage or event locality does not establish cross-event continuation.

Variable-rank sectors are stratified domains. Near degeneracy, an isolated
cluster or subspace is the transport object, not an individual eigenvector.

## Structural Interpretation Boundary

When D8 eventually computes an admitted operator, the labels are:

```text
alpha > 0  = restoring under the declared normalization and constraints
alpha = 0  = marginal after protected/gauge nulls are removed or classified
alpha < 0  = structurally unstable direction, not a stable identity branch
```

Structural marginality does not itself establish spark, collapse, topology
change, current deslavement, or a specific nonlinear destination. An
infinitesimal mode is not a finite basin. Alpha also does not determine memory
lifetime; temporal rates depend on mobility and closure. Finite-horizon
nonnormal survival subspaces remain norm-, path-, and horizon-relative analysis
objects rather than structural modes.

## Controls And Debt

D3 freezes 39 controls. They block:

```text
DF-as-Hessian and spectrum relabels
formed snapshot/trajectory/branch conflation
independent A/B structural coordinates without joint functionals
independent C-sector perturbations
rank/event derivatives without a stratum map
conditional structure relabeled as joint continuation
unregularized current elimination
active-current self-adjoint inheritance
D3 support rows promoted to D6 selection
cross-state mode comparison without reference transport
analysis projectors promoted to runtime carriers
retained formation promoted to structural formation or the reverse
conditioned C spectra promoted to carrier spectra
invented joint penalties or fake zero modes
unfrozen alpha normalization and gauge null overclaim
retrospective branch and selector construction
linear Hessians at tangent-cone or nonsmooth boundaries
alpha-zero event relabels and mode-to-basin relabels
nonnormal survival or temporal lifetime promoted to structural continuation
```

All 15 D2 debts are classified. D3 adds nine typed debts covering:

```text
formed branch construction
A joint C/W structural theory
B joint C/T structural theory
C exact derived tangent and moving-sector transport
independently active-current structural theory
operator representation and reference transport
functional normalization, metric, and protected nulls
geometry-dependent constraints and total derivatives
nonsmooth selector boundaries and tangent-cone domains
```

There are 24 open debts, 20 of which must close before D10. Four are currently
nonblocking: the closed Candidate D admission slot and three conditional theory
debts for A joint structure, B joint structure, and independently active-current
structure. Each conditional debt still blocks its named claim. It becomes a
named D10-blocking successor debt only if D6/D8 selects an architecture or
claim that requires that structural coordinate; it does not block a valid
conditional/reduced architecture that does not make the claim.

The structured artifact includes a 42-row pressure audit. Every supplied point
is bound to a frozen rule, control, candidate-local claim, matrix cell, or typed
later-gate debt; none is left as an unnamed implementation detail.

## Candidate Status

```text
candidate_set_after_D3 = [A, B, C]
rejected_on_D3_structural_domain = []
reclassified_or_revision_needed = []
joint_structural_candidate_supported = false
current_regime_selected = false
architecture_selected = false
```

`joint_structural_candidate_supported = false` is a claim boundary, not a
failed tranche. D3 establishes exactly which bounded structural interpretation
each candidate can currently support.

## Claim Ceiling

D3 supports only:

> Source-bounded structural-domain classifications, tangent and reference
> transport requirements, and current-regime support rows for A, B, and C.

It does not establish an empirical formed branch, compute a Hessian or spectrum,
admit joint A/B structural coordinates, solve independently active current,
select a current regime, define geometry/mobility ownership, or authorize a
specification or runtime implementation.

## Authorization

```text
D4_authorized = true
specification_authorized = false
runtime_implementation_authorized = false
src_change_authorized = false
```
