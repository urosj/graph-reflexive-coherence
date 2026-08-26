# D4 Geometry, Mobility, And Topology Ownership

**Record:** `GRC9V4-CD-D4-v1`
**Status:** accepted bounded
**Decision digest:** `c3c4507d4623ee526e636c4434bc13b4af23bdd3f6051cf1db99a2ce5736215c`

## Purpose

D4 is the first gate that assigns candidate-specific constitutive ownership.
It does not merely repeat that unchanged GRC9V3 lacks independent retention.
It asks which object owns geometry, which object owns mobility, and which maps
would make each D1 survivor causal rather than nominal.

The central result is:

```text
K_4 -> h_4                         geometry induction
W or another A_4/M_4 surface       transport mobility
J_C                               oriented current
P_M or spectral projectors         selectors, not automatic runtime owners

geometry != mobility != current != analysis projector
```

This separation is not a claim that the objects can never be related. It says
that any relation must be an explicit constitutive map. A symbol, cache, edge
label, or persistent value cannot acquire all four roles by relabel.

Nor does role separation imply field-count separation. One stored object may
parameterize both geometry and mobility when the architecture supplies
separate typed maps and intervention consequences. Conversely, two field names
do not establish two causal degrees of freedom when one is reconstructed from
the other. D4 tests causal factorization, ownership, and transition authority,
not the number of arrays.

## Source Boundary

The controlling RC papers keep the core primitive coherence-only state at
`(C, J_C)`. The complete candidate runtime causal state is not thereby closed:
Candidate A adds retained mobility `W_A`, Candidate B proposes independent
nonresource `T_B`, and Candidate C adds no independent sector state. They
locate induced geometry through `K -> h[K]`, distinguish
mobility from structural stiffness, and reconstruct Read-Back as a relation
conditioned by retained geometry. They also state two important open points:

```text
the exact nonlinear metric closure h[K] is underdetermined
the schematic retained geometry h_M is not an exact constitutive map
```

GRC9V3 supplies a different, implementation-specific fact. Its
`base_conductance` is a scalar load-bearing transport surface. On each edge,
the present flux uses `eta * W_e` as its scalar mobility factor. The runtime
reconstructs `W` before present flux from current coherence, differential
summaries, and incoming-current magnitude. `geometric_length`,
`temporal_delay`, and `flux_coupling` are analytic labels; they are not metric
or transport authority. The cached hybrid node tensor is likewise not a
positive-definite metric merely because it is tensor-valued.

These are frozen V3 facts. They constrain the V4 reduction profile but do not
dictate V4 ontology.

## Shared Ownership Map

D4 freezes the following typed roles:

```text
K_4 = geometry-inducing constitutive object
h_4 = H_4(K_4) = induced spatial geometry
A_4 or M_4 = transport mobility
W_hat = legacy reconstructed scalar conductance
W_authoritative = scalar edge mobility surface selected by the active profile
J_C = oriented current cochain
```

For the legacy scalar realization:

```text
m_e = eta * W_authoritative,e
J_e = -m_e * (Phi_u - Phi_v)
```

The potential also consumes authoritative `W`, so the total transport response
is not reduced here to one linear graph Laplacian. The equation above records
the edge mobility factor and current sign convention, not a complete V4
transition.

The geometry map remains:

```text
h_4 = H_4(K_4)
```

with positive-definite spatial geometry, measure response, covariance, and
boundary behavior required on each admitted smooth stratum. D4 does not invent
the missing numerical `H_4` merely to close the gate.

The runtime mobility in this map is not automatically the analytical
`script_A_star` used by the continuation relaxation construction. D8 must
derive the linearized push-forward through the selected runtime clock, measure,
constraint representation, and mobility law. Shared dimensions or notation are
not enough.

Metric and mobility positivity are also distinct. `h_4` needs a valid
nondegenerate spatial metric on its declared stratum. A dissipative mobility
needs a positive-semidefinite symmetric part when that branch is claimed, and
may later include nonreciprocal or antisymmetric components. Such components
cannot be relabelled as metric geometry.

Finally, separate identification of geometry and mobility requires a gauge.
For some realizations, a joint rescaling such as `h -> a h` and
`M -> a^-1 M` may leave the observed transition unchanged. Units, metric or
volume normalization, mobility and clock scale, normalization locality, and
load-bearing regularization must therefore be frozen before numerical
cross-candidate comparison.

The derivative consequence is candidate-specific:

```text
A:
  fixed-h C-only Hessian remains available
  no direct W_A-conditioned structural derivative
  indirect W_A -> present J_C -> D5 j -> K -> h derivative waits for D5/D6/D8

B:
  fixed-h C-only Hessian is not evidence for T_B
  total T_B-conditioned derivative waits for G_B and measure response

C:
  C-only derivative with exact fixed-rank selector tangent remains available
  total sector-conditioned derivative waits for H_M and the selector/geometry
  fixed point
```

Whenever retained state changes `h`, conservation remains a single coherence
budget but the constraint manifold moves through the induced measure. A
nonresource `T` does not create `C`; it can still change the tangent condition
for `Q[C;h] = Q0`. All first- and second-order geometry, measure, constraint,
and selector chain-rule terms are required before a total structural derivative
is reported.

## Candidate A: Retained Scalar Mobility

Candidate A receives **coherent bounded ownership**.

Its retained object is a positive live-edge scalar state `W_A`. In the enabled
A profile, `W_A` is the only transport authority:

```text
enabled A:
  W_authoritative = W_A
  W_hat            = instantaneous write reference or target

disabled A / V3 reduction:
  W_authoritative = W_hat reconstructed under exact V3 semantics
```

Here `W_A` names the authoritative positive state called `W[k]` in D2. It is
not D2's relation coordinate:

```text
R_W = W_A - W_hat, or the other relation explicitly selected under D2
m_e = eta W_A,e
R_W is not itself positive mobility or transport authority
```

This is replacement of transport authority, not addition of `W_hat + W_A`.
It closes the D4 double-authority ambiguity without choosing the D7 temporal
update law.

Candidate A does **not** make `W_A` the induced metric. Its D1 roles are
narrowed to:

```text
owns scalar transport mobility
acts as a direct transport parameter
does not condition h_4 directly under the admitted D4 map
```

`K_4` remains geometry-inducing. `W_A` may affect later geometry indirectly by
changing present current, which a later D5 Read-Back map may convert to `j`
before `j` enters `K_4`; this is a theory-open dynamical path, not a direct
`W_A -> h_4` or `J0 -> K_4` identity.

That result narrows D3. Candidate A remains a viable retained runtime
architecture, but retained `W_A` currently changes kinetics, not the declared
structural functional:

```text
no-current / frozen-current:
  inherited C-only structure remains
  W_A-conditioned structural continuation is unsupported

smoothly slaved current:
  indirect W_A -> mobility -> present J_C -> D5 j -> K -> h remains
  theory-open pending D5/D6/D8

independently active current:
  theory-open as before
```

Thus A may change relaxation rates or map multipliers after D8 derives the
runtime-to-analytical mobility relation. It does not currently provide an
`alpha` spectrum of `W_A` or a `W_A`-conditioned structural stiffness.
It enters D5 only as a retained-mobility-conditioned operator candidate; it
cannot inherit the core paper's retained-geometry Read-Back claim unless a
later source-backed direct or indirect structural map is admitted.

The staging is also explicit. `W_hat` is reconstructed from pretransport
inputs. Existing `W_A` drives current transport. The D7 write may use
`W_hat`, previous `W_A`, and declared write inputs, but newly written `W_A`
cannot be consumed in the same beat unless a later explicit solve replaces the
one-beat-delayed contract. This prevents the incoming `J^2` contribution from
appearing twice through simultaneous conductance authorities.

D7 still owns the exact `W_A` update, normalization, bounds, release, and solve
order. D9 owns edge birth, deletion, split, merge, relabel, and disabled-profile
commutation.

## Candidate B: Independent Geometry Carrier

Candidate B is **routed to a named missing derivation**:

```text
GRC9V4-D4-B-INDEPENDENT-CARRIER-GEOMETRY-CLOSURE
```

B remains a revision-level candidate, but current sources do not select:

```text
the graph/tensor domain of T
the map G_B(C, T, declared baseline K inputs, topology) -> K_4 or h_4
the orientation, rank, units, or topology transport of T
```

Writing “T conditions geometry” would therefore repeat D1 rather than add a
D4 constitutive fact. B also cannot inherit core status: the controlling
coherence-only paper does not introduce or authorize a new independent memory
or Read-Back field as an inherited primitive. A future B derivation must state
whether B is an explicit RC
extension or an exact reparameterization, prove that `T` remains nonresource,
and keep mobility and current authority separate.

Until that derivation exists, B has no admitted direct geometry or mobility
role. D5 may record requirements for a B-parameterized operator, but it cannot
claim a complete B closure.

If B later uses geometry as an input to `T` formation, its default admissible
timing is previous-beat geometry. A same-beat
`T -> K -> h -> T-write` cycle is an implicit solve and requires a unique,
regular closure; it cannot be settled by arbitrary stage order. A many-to-one
`T -> h` map would not itself reject B, because native write or Read-Back could
still distinguish the preimages. If geometry becomes B's only native consumer,
that possible redundancy becomes a D7 elimination/equivalence question.

## Candidate C: Derived Retained Geometry

Candidate C is also **routed to a named missing derivation**:

```text
GRC9V4-D4-C-RETAINED-GEOMETRY-CLOSURE
```

Its exact retained object remains a derived current-state sector:

```text
T_C = P_M^(Delta)[current C, current induced geometry, cutoff] C
```

It is not an independent field, resource, or mobility. This preserves the
coherence-only ontology and the D1 resource accounting.

The Read-Back paper supports a retained-geometry role schematically:

```text
h_M = h[retained spatial sector, optional dynamic slow sector; C]
```

but explicitly says that the exact map is open. It also says the spatial and
dynamically slow sectors need not coincide. D4 therefore admits the role
“source-backed retained geometry conditioner” while refusing to report an
exact closure that the source does not provide.

Candidate C has no direct mobility authority. Its source-backed dynamical
geometry path is instead:

```text
retained sector + present J_C
  -> D5 Read-Back j
  -> j tensor j contribution to K_4
  -> later h_4
```

The direct retained metric map needed by the Read-Back operator remains open.
D5 may derive an operator family parameterized by a declared `h_M`, but C
cannot become a final architecture until `H_M` or an equivalent `K`-conditioning
map, selector regularity, and topology/rank transport are resolved.

An optional dynamic projector does not acquire runtime authority through
analysis alone. If its sector is deterministically reconstructable from the
declared current causal state, it may remain a derived constitutive
representation under the D3 dynamic-projector contract. If it requires its own
persistent history or state, it requires D1 reclassification or successor
admission. If it remains analysis-only, `H_M` cannot consume it at runtime.

Candidate C also contains a pure geometry fixed-point risk:

```text
P_M = P_M(C, h)
T_C = P_M(C, h) C
h_M = H_M(T_C, C, ...)
```

This is not a simple cache refresh. The named C derivation must either use a
declared lagged/reference geometry to stage the selector, or prove that the
joint selector/geometry fixed point exists, is unique, and remains regular on
the admitted fixed-rank stratum. Current D4 does neither and therefore leaves
the exact closure open.

Ordinary `h(C)` is also not evidence that the selected sector is load-bearing.
The admitted closure must respond specifically to an intervention on the
selected factorization while counting `C` exactly once. This preserves
coherence-only resource accounting without turning a tautological decomposition
into a geometry result.

## Candidate Causal Ownership Graphs

The structured record freezes 12 object records and 15 typed causal arrows.
Every arrow records map status, temporal side, locality, invertibility,
resource or measure effect, smooth-stratum domain, and topology obligation.
The compact graphs are:

```text
A:
  C, incoming J -> W_hat
  previous W_A + declared writes -> next W_A       [D7 open]
  C, grad C, source-typed terms -> K_4 -> h_4       [H_4 open]
  current W_A + h_4 -> edge mobility -> baseline J0
  present J_C -> D5 j -> later K_4 -> later h_4

B:
  previous T_B + declared writes -> next T_B       [D7 open]
  T_B -> K_4 or h_4                                [G_B missing]
  h_4 + separate mobility -> baseline J0

C:
  C, geometry, cutoff -> P_M -> T_C
  T_C, C, optional admitted/reconstructable dynamic sector -> h_M
                                                    [H_M missing]
  h_M + separate mobility -> baseline J0
  T_C, h_M, present J_C -> j                        [D5]
j -> K_4 -> later h_4
```

The source ordering is therefore `J_C -> j -> K_4 -> h_4 -> J0` when the
Read-Back branch is active. Present `J_C` is not a direct baseline input to
`K_4`, and it is not an input to Candidate C's `H_M`. It enters C only at the
D5 Read-Back map after `h_M` has been prepared.

The baseline route and Read-Back route are separate for all candidates:

```text
retained state -> geometry/mobility -> J0
retained state + present J_C -> j
```

A retained-conditioned change in direct `J0` is not Read-Back. D5 must audit
path overlap and double counting when it introduces `j`.

The object registry also freezes cache ownership. Derived `h`, `K`, selected
sectors, decompositions, inverse matrices, factorizations, preconditioners, and
solver caches may be serialized as representation, but stale values must not
change the future. If they do, they have acquired causal state and require D1
reclassification. A solver metric that changes convergence but not the solved
state is computational machinery, not physical geometry.

## Topology And Basin Boundary

Fixed topology is the local smooth analysis lane, not the normative V4 scope.
GRC9V4 remains topology-capable.

At a topology, selector-rank, mode, or basin-identity event, D4 requires a
later typed interspace map for:

```text
C and conserved measure
J_C and edge orientation
K_4 and h_4
authoritative mobility state
retained selector basis and rank
lifecycle and release accounting
```

Node lineage or an event record does not provide this transport by itself.
Likewise, a geometry or mobility change does not establish basin birth. Basin
identity and topology-event claims remain governed by their own runtime and
accounting contracts.

Persistent topology mutation can nevertheless carry historical causal
information even when topology is not the claimed retained representation.
In that case topology is a rival historical carrier: no result may be credited
to A, B, or C unless the topology write/read effect is isolated and included in
event accounting.

D4 further distinguishes:

```text
near-zero mobility       = weak transport, edge remains present
exact zero mobility      = closed transport channel, edge remains present
inactive retained edge   = explicit lifecycle state
metric degeneracy        = invalid/boundary geometry state
adjacency deletion       = topology event
thresholded zero         = constitutive event rule, not floating tolerance
```

Effective transport disconnection does not automatically alter adjacency or
the formal global conservation law. Componentwise invariants, if any, must be
derived from the selected D7 transition and consumed by D8. Metric degeneracy,
zero mobility, and edge deletion are never interchangeable.

For each candidate, D4 records the class of event transport that D9 must
choose. New elements require explicit neutral, parent-projected,
neighbor-distributed, or event-derived initialization. Splits cannot copy a
full retained value onto every child without declaring information/capacity
semantics; merges cannot silently average or sum. C instead transports
authoritative `C`, then recomputes its sector with a rank/basis receipt.

The current map scope is the occupied port-pair graph with scalar A mobility.
Parallel-edge, self-loop, anisotropic, and broader nonreciprocal profiles need
explicit admission. Node relabels and stored edge-orientation reversals must
preserve scalar geometry/mobility invariants, while cochains and tensors must
transform covariantly. Topology-driven symmetry changes do not preserve mode,
projector, or gauge-null identity automatically; D8 owns that analytical
transport.

Topology may carry historical causal information whenever past activity leaves
persistent mutation. It counts as the claimed retained representation only
when explicitly assigned that role; otherwise it remains a rival historical
carrier that must be controlled when attributing effects to A, B, or C.

## B1/B2 Consumption

D4 consumes B1/B2 in four distinct ways:

```text
legacy_fact:
  V3 reconstructs W and uses scalar conductance for transport

verification_control:
  stored W/J, labels, caches, and lineage cannot be relabelled as the missing
  V4 causal roles

design_pressure:
  unchanged V3 did not construct retained mediation or Read-Back

open_hypothesis:
  retained W, independent T, or a derived C-sector may support a V4 closure
```

Only the first category is a hard premise, and only for frozen V3. The three
candidate dispositions come from the current theory and candidate maps, not
from rerunning unchanged-runtime absence.

## Result

```text
V4-A-temporalized-W:
  coherent bounded ownership
  retained scalar mobility, not geometry

V4-B-independent-derived-carrier:
  routed to named independent-carrier geometry derivation

V4-C-constitutive-C-sector:
  source-backed retained-geometry role
  routed to named exact retained-metric derivation
```

No candidate is rejected and no architecture is selected. This asymmetry is a
scientific result: A has an already typed discrete mobility surface, while B
and C need geometry closures that the current sources do not uniquely supply.
It is not a ranking of eventual adequacy. In particular, C remains closest to
the coherence-only ontology even though its exact retained metric map is open.

The D4 pressure audit contains 50 rows, all bound to explicit object, arrow,
topology, control, D3-feedback, or debt records. It adds localized failure codes
such as:

```text
no_source_backed_geometry_map
mobility_only_no_structural_effect
geometry_mobility_nonidentifiable_without_gauge
selector_geometry_fixed_point_not_regular
topology_event_transport_undefined
retained_sector_not_load_bearing_in_geometry
```

These codes reject a role claim, not an entire candidate by default.

## Claim Ceiling

D4 supports bounded ownership and missing-derivation routing. It does not
support:

```text
an exact nonlinear metric closure
a B or C complete geometry implementation
a Directional Read-Back operator
a total-current closure
a complete transition or topology-event transport
a formed branch or runtime result
architecture selection
a normative GRC9V4 specification
src changes
```

D5 is authorized only after human acceptance of this record.
