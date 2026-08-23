# GRC9V4 Constitutive Design Basis

**Date:** 2026-08-23  
**Status:** Pre-D0 investigation basis; no architecture selected  
**Plan:** [`GRC9V4ConstitutiveDesignPlan.md`](./GRC9V4ConstitutiveDesignPlan.md)  
**Checklist:** [`GRC9V4ConstitutiveDesignChecklist.md`](./GRC9V4ConstitutiveDesignChecklist.md)  
**Decision ledger:** [`GRC9V4ConstitutiveDesignDecisionLedger.md`](./GRC9V4ConstitutiveDesignDecisionLedger.md)
**Initialization:** [`GRC9V4ConstitutiveDesignInitialization.json`](./GRC9V4ConstitutiveDesignInitialization.json)

## Purpose

This document defines the boundary of the pre-specification investigation. It
does not define GRC9V4 equations, fields, capabilities, or implementation.

The design basis inherits causal roles and acceptance constraints from the
Continuation/Read-Back theory contract, then uses accepted B1-GR and B2-GR
evidence to constrain what cannot be claimed of legacy GRC9V3. The inheritance
chain is:

```text
The Continuation Spectrum + Read-Back
  -> B1 Draft 3.4.1 theory-to-graph contract
  -> accepted B1/B2 evidence boundaries
  -> D0-D10 constitutive decisions
  -> possible later GRC9V4 normative specification
```

Draft 3.4.1 is a verification and decision surface. It is not copied into a
runtime specification and does not uniquely select a constitutive completion.

## Controlling Inputs

### Theory authority

- [The Continuation Spectrum](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2026-08-TheContinuationSpectrum.md)
- [Read-Back](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2026-08-ReadBack.md)

The current theory revisions and source identities must be frozen during D0.
The local B1 contract records the interpretation used by the accepted graph
experiments:

- [`GRC9V3ContinuationReadBackVerificationSpecification.md`](../../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/implementation/GRC9V3ContinuationReadBackVerificationSpecification.md)
- [`GRC9V3ContinuationReadBackVerificationSpecification_EvidenceGrounded_v1.md`](../../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/implementation/GRC9V3ContinuationReadBackVerificationSpecification_EvidenceGrounded_v1.md)

### Substrate and evidence authority

- [`grc-9-v3-spec.md`](../../../specs/grc-9-v3-spec.md)
- [`grc-9-v3-evidence-profile.md`](../../../specs/grc-9-v3-evidence-profile.md)
- [`Phase-7-StepLoop.md`](../../Phase-7-StepLoop.md)
- [`Phase-7-EquationMap.md`](../../Phase-7-EquationMap.md)
- [B1-GR experiment](../../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/README.md)
- [B1-GR implementation plan](../../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/implementation/GRC9V3ContinuationReadBackVerificationImplementationPlan.md)
- [B1-GR closeout](../../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/reports/b1_grc9v3_verification_report.md)
- [B2-GR experiment](../../../experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/README.md)
- [B2-GR implementation plan](../../../experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/implementation/GRC9V3RetentionMediationConstructibilityPlan.md)
- [B2-GR classification and handoff](../../../experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/reports/b2_i8_classification_and_handoff.md)

The theory sources govern theory claims. The GRC9V3 specification and Phase 7
records govern legacy runtime semantics. B1/B2 artifacts govern bounded runtime
evidence. None may silently inherit authority from another layer.

## Historical Lineage And Consumption Boundary

The local B1 specification and the B1/B2 experiments are historically
load-bearing. They explain how the GRC9V4 question was reached and preserve
failed mappings, bounded evidence, and verification distinctions that D0 must
not rediscover from memory:

```text
B1 theory-to-graph contract
  -> B1 unchanged-GRC9V3 verification
  -> B2 bounded unchanged-runtime constructibility search
  -> GRC9V3 normative/evidence reconciliation
  -> this GRC9V4 constitutive design investigation
```

The [B1 verification specification](../../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/implementation/GRC9V3ContinuationReadBackVerificationSpecification.md)
is the historical bridge that made continuation, retention, Read-Back,
write-back, causal-state closure, and analysis/runtime separation executable on
the graph substrate. Its evidence-grounded successor records the interpretation
after B1 execution. They are verification and decision history, not a literal
GRC9V4 field layout or equation set.

B1 established, within its declared fixed-topology envelope, exact synchronous
`C/W/J` recurrence, stage-local `J^2 -> W` write mechanics, bounded `GRR2`
neutral-coordinate persistence, and explicit non-realization or unresolved
status for stronger retention, directional Read-Back, write-back, and a closed
read/write loop. It also demonstrated why spatial, temporal, continuation, and
read-response operators cannot be treated as one spectrum.

B2 then tested whether unchanged GRC9V3 could construct stronger `GRR3-GRR5`
retention/mediation witnesses. Its accepted empty candidate set is a bounded
negative over the preregistered clean lane. It does not establish global
impossibility, require an independent `T`, select temporalized `W`, select a
current extension, or authorize any particular V4 architecture.

D0 must therefore classify B1/B2 material under two distinct uses:

```text
may consume as:
  historical decision lineage
  exact or bounded legacy-runtime evidence
  failed-mapping and false-positive controls
  claim ceilings and unresolved debts
  motivation for revision-distinct design

must not consume as:
  normative GRC9V4 semantics
  a preselected retained representation
  proof that retention requires independent state
  global non-constructibility of unchanged GRC9V3
  automatic extension trigger or architecture ranking
```

When a D0-D10 decision depends on a B1/B2 result, it must cite the source
experiment artifact directly and preserve that artifact's envelope. Historical
importance does not enlarge scientific authority.

D0 must also compare every B1-derived theory statement with the current core
papers and classify it as:

```text
unchanged
narrowed_by_current_core
broadened_by_current_core
superseded
historical_only
conflict_requires_rederivation
```

Current core sources control theory claims. B1 measurements remain valid within
their accepted historical envelope, but a changed interpretation cannot remain
a V4 design constraint merely because B1 once froze it.

## Target

The investigation asks whether one coherent, minimal constitutive architecture
can support all of the following without relabeling diagnostics as state:

```text
past activity
  -> formation of an admitted retained causal representation
  -> distinguishable post-input continuation
  -> present-current-conditioned directional Read-Back
  -> total-current/state consequence
  -> write-back into the future retained representation
```

Continuation comes before Read-Back in the design order. A carrier optimized
only to produce a convenient read operator is not sufficient.

The target does not assume that the retained representation is an independent
state coordinate. `T_M` is architecture-neutral notation until D1. It may name
a constitutively retained sector of `C`, temporalized geometry or mobility, a
separate derived structural carrier, or another source-admitted representation.

## D0 Scope Decisions

D0 must freeze four boundaries before candidate admission begins:

1. the exact theory, substrate, and evidence authorities and the claim ceiling;
2. the D1 candidate set and the deadline/rule for admitting any additional
   source-backed candidate;
3. the candidate-neutral GRC9V3 reduction contract and reference surfaces when
   retention and Read-Back coupling are disabled; and
4. both the design/verification envelope and the normative runtime capability
   scope for topology-changing mechanics.

The reduction contract must require every D1 candidate `a` to construct an
architecture-specific embedding and projection after its state space is known:

```text
i_a  : X_V3 -> X_V4_a_disabled
pi_a : X_V4_a_disabled -> X_V3

pi_a o F_V4_a_disabled o i_a = F_V3
```

D0 freezes the V3 reference transition, required comparison surfaces, allowed
exact/projected/tolerance semantics, added-state initialization requirements,
disabled-state serialization rules, and lifecycle comparison requirements. It
does not instantiate `i_a` or `pi_a` before D1 establishes `X_V4_a`.

Each D1 construction must state how its added state is initialized, whether
disabled state is serialized, which lifecycle coordinates are included, and
which structural blockers or unresolved obligations remain. D1 establishes
state-space and ownership compatibility; it cannot prove transition commutation
before the complete candidate transition exists.

D9 must verify the selected candidate's commuting condition separately for:

```text
transition equivalence
snapshot equivalence
observable equivalence
event/lifecycle equivalence
```

Each D9 classification must say whether it is exact, projected, or numerical
within a frozen tolerance. An equivalence label without candidate-indexed
`i_a`, `pi_a`, state initialization, compared surfaces, and an actual completed-
transition witness is inadmissible.

Topology scope has two independent decisions:

```text
design_verification_envelope
normative_runtime_capability_scope
```

The design envelope may initially be fixed-topology. That does not by itself
disable inherited spark or expansion mechanics in the normative runtime. The
runtime scope must select and justify one of: full retained-representation
transport/accounting across graph mutation; an explicit fixed-topology
subprofile with topology-changing capabilities disabled; or a declared event
boundary at which retained semantics terminate or reset. If the eventual V4
profile retains topology-changing capability while early work stays fixed-
topology, the explicit interspace transport/accounting map is a
`must_close_before_D10` debt. Lineage alone is not that map.

## Inherited Distinctions

The following distinctions are design invariants:

```text
core primitive state
  != runtime causal state
  != analytical perturbation state

retained causal representation T_M
  != independent runtime state by definition
  != analysis-only continuation projector P_slow
  != structural continuation spectrum {alpha_n}

retention
  != Read-Back
  != write-back

no_forming_or_write_input
  != zero_present_current

structural continuation stiffness alpha
  != temporal relaxation/growth gamma or map multiplier mu
  != Read-Back response beta
  != spatial scale lambda

frozen-carrier response
  != dynamic joint continuation
```

`no_forming_or_write_input` tests post-input retention or release after the
forming/write driver is absent. `zero_present_current` tests the Read-Back
passive null `R_G(T_M,h;0) = 0`. A representation may persist under the first
condition while producing no read current under the second.

An analysis-only projector or observer does not become constitutive merely
because it is useful. Conversely, a constitutively consumed representation may
be derived from `C` without becoming an additional independent state coordinate,
and a serialized field is not automatically an independent complete-step
coordinate.

## Inherited Read-Back Contract

The graph read relation must be typed as an oriented edge-current/cochain
operation, schematically:

```text
R_G : retained representation x graph structure x C^1(E) -> C^1(E)
```

It must preserve at least:

- the passive null: zero present current produces zero read current;
- edge-coordinate orientation covariance under relabeling of stored edge
  orientation;
- a separately declared physical response to present-current reversal while
  the coordinate convention stays fixed;
- an explicit statement of whether the retained representation carries
  orientation or chirality;
- separation of baseline current `J0`, read contribution `j`, and total current
  `J_C`;
- separation of direct read response from the full effective closed loop; and
- attribution controls showing that retained structure and present activity are
  both load-bearing.

A scalar carrier, route score, label, projector, or conductance diagnostic may
condition a read relation, but cannot itself be relabeled as oriented read
current.

If retained structure also conditions geometry or transport, the investigation
must separate two causal paths:

```text
direct_retained_to_J0_path:
  T_M -> h/W/mobility -> J0

readback_TJ_to_j_path:
  (T_M, J_C) -> j
```

D5/D6 must audit overlap and double counting. Where structurally possible, the
read-off control disables `j` while preserving the direct retained-to-`J0`
path. A retained-conditioned baseline-current change with `j = 0` is not
Read-Back.

Coordinate covariance and physical reversal are not interchangeable. A valid
cochain map must transform consistently when edge coordinates are relabeled.
Whether `j(T_M,-J) = -j(T_M,J)` holds is a separate constitutive symmetry
question and may depend on orientation content in `T_M`.

## Inherited Continuation Contract

The runtime must provide a complete transition on an admitted causal state.
Depending on D1, that state may remain `C` with a constitutively read retained
sector, expand to `(C,T)`, or take another source-admitted form. Current and read
current may remain intra-beat causal surfaces if their closure is regular.

Continuation analysis remains derived rather than serialized, but it is not one
undifferentiated spectrum. The investigation must preserve:

```text
structural functional/Hessian H_*       -> alpha_n
temporal generator or effective DF_*    -> gamma_n or multipliers mu_n
Read-Back derivative D_J R_*            -> beta_n
spatial graph operator -Delta_h         -> lambda_n
```

These objects may be compared only under declared mappings and assumptions.
They must not be reported as spectra of one universal generator.

The design must distinguish:

- formed state, formed branch, tracked reference branch, and actual trajectory;
- ordinary branch displacement from retained-sector displacement;
- temporal slowness from low structural continuation stiffness;
- a slow parameterized cache from a structurally admitted retained direction;
- simple isolated modes from clusters or invariant subspaces; and
- static/frozen retained-state response from native dynamic continuation.

Formation, retention, and release/reconfiguration must all be representable.
An arbitrarily small decay constant or small temporal rate is not by itself
evidence for low structural continuation stiffness.

For every admitted representation, D3 must distinguish three structural cases:

```text
C-only structural continuation:
  H_C is derived from F_struct(C)

conditional C structure:
  H_C_given_T is the C Hessian of F_struct(C; T_*)
  T_* parameterizes the structural landscape but delta_T is not a
  continuation coordinate

joint structural continuation:
  H_(C,T) is derived from a source-backed joint F_struct(C,T)
  and delta_T is an admitted structural coordinate
```

The runtime transition is denoted `F`; the structural functional is denoted
`F_struct`; `P_M` and `P_slow` are reserved for projectors, and `pi_a` is
reserved for candidate reduction projections. `DF(C,T)` is a temporal
transition derivative and cannot supply `H_(C,T)` by relabeling. The joint case may require theory
reopening and must fail closed when no source-backed structural functional is
available.

D3 must build a support matrix over structural reference-current regimes,
independently of the structural domain:

```text
no_current_reference
frozen_current_reference
smoothly_slaved_current_reference
independently_active_current_reference
```

For every row, each candidate must record `supported`,
`conditionally_supported`, `theory_open`, or `blocked`, plus the required
current elimination/freezing rule, whether current would be a structural
coordinate, and the active-joint-continuation theory status. D3 does not select
the runtime current regime. D6 selects the actual closure; D8 consumes the
corresponding D3 row. A self-adjoint structural Hessian is not inherited
automatically for an independently active `(C,T,J)` system; absent a
source-backed derivation, that row remains theory-open or blocks the affected
interpretation.

D8 analysis must declare the representation in which every operator and
projector lives:

```text
operator_domain
admissible_tangent_space
inner_product_or_weight
physical_representation
self_adjoint_or_reduced_representation
representation_map
projector_pullback_or_pushforward
moving_space_identification
cluster_conditioning
```

An analysis-coordinate projector is not a projector on physical runtime
coordinates without the declared conjugation and transport. If spaces move
along a formed branch, their identification map must be explicit before modes
or projectors are compared.

## Geometry And Mobility Vocabulary

D4 begins without assigning graph objects to theory roles:

```text
h = constitutive or induced geometry/metric
K = geometry-inducing or constitutive object under the frozen theory mapping
W = legacy graph conductance with potentially conflated structural/transport roles
M or A = declared transport-mobility operator, if separately realized
```

The investigation must decide which graph object, if any, realizes mobility.
It must not assume `K` is transport mobility or silently resolve inherited
geometry-mobility debt before D4.

## Architecture Candidates

D1 must compare, not assume, at least these candidate families:

| Candidate | Retained causal representation | Main advantage | Main risk |
| --- | --- | --- | --- |
| `V4-A-temporalized-W` | existing conductance/geometry surface receives independent cross-beat evolution | close to current mechanics; small state expansion | conflates retained structure, geometry, and transport mobility |
| `V4-B-independent-derived-carrier` | a separate retained carrier `T` whose update law is derived from permitted RC variables; `W` remains distinct | separates carrier, geometry, current, and read contribution | adds a new runtime causal coordinate and must not be algebraically reconstructable from present `C` |
| `V4-C-constitutive-C-sector` | a historically formed sector of `C` has later constitutive read/write authority without becoming an independent coordinate | stays closest to a coherence-primary ontology | ordinary `C` evolution can be tautologically relabeled as retained write-back |
| `V4-D-source-admitted-structural` | another representation admitted from frozen sources before D1 evaluation | prevents the initial list from forcing a false choice | may hide post-result invention unless D0 freezes its admission basis and deadline |

Names are investigation identifiers, not class or field names. D1 may admit an
additional source-backed architecture only under the admission rule frozen in
D0. D1 admits or rejects candidates on ontology; it does not select the final
architecture. If one candidate remains, it is a `sole_surviving_candidate`, not
an accepted design.

If no admitted candidate survives, D1 records
`current_candidate_set_exhausted`. That is a route outcome, not an architecture
and not rejection of GRC9V4. It must localize the missing constitutive,
theoretical, or discriminatory role and route to revised candidate admission or
named derivation.

Independent current temporalization is not a D1 candidate family. D6 evaluates
it as an orthogonal slaving/deslavement decision for every surviving retained-
representation architecture.

## Orthogonal Authority, Accounting, And Transport Types

D1 must classify every candidate independently on three axes:

```text
state_authority:
  independent_state
  derived_constitutive_representation
  reconstructed_view
  observer_only

resource_accounting:
  carries_independent_resource
  projects_existing_resource
  nonresource_structural_information
  no_resource_role

transport_roles: set[
  conditions_geometry
  conditions_mobility
  direct_transport_parameter
]
  empty set means no transport role
```

The axes are not mutually reducible. A constitutive `C` sector may be a derived
representation that projects existing resource. Temporalized `W` may carry
nonresource structural information while also acting as a transport parameter.
A separate serialized `T` may be independent state without carrying resource.
Transport roles are set-valued because one representation may condition
geometry and mobility or also act as the direct transport parameter.

D2 must define the conservation and budget consequence of each admitted
combination. Independent resource enters the declared budget. Projected
resource cannot be counted twice. Nonresource structural information cannot
become an unlimited hidden reservoir. A derived constitutive representation
must prove historical causal authority; a reconstructed view or observer alone
cannot satisfy retention. A transport role cannot silently confer resource,
current, or analysis-projector authority.

Every derived constitutive representation must also expose a runtime
addressability contract:

```text
representation_selector
selector_inputs
selector_is_constitutive
selector_statefulness
sector_identity_at_k
sector_identity_transport_rule
requires_hidden_history
requires_future_information
```

The selector must be available to the complete runtime transition from declared
causal state. A sector discovered retrospectively from a trajectory, future
persistence, or an analysis-only slow projector is not a runtime retained
representation. `observer_selected_retained_sector_as_runtime_representation`
is a D1 veto for every candidate, not only the constitutive `C` sector.

If selector evolution depends on prior selector state, that state is explicit,
serialized causal state. Otherwise the selector must be deterministic from the
current declared causal state. An unsaved stateful sector tracker is hidden
retained state and fails D1.

For `V4-C-constitutive-C-sector`, D2 and D7 must expose a retention-selective
factorization:

```text
ordinary C update
  != activity-induced occupation or change of the admitted retained sector
  != later retained-conditioned read effect
```

If those arrows cannot be separated causally, generic `C` continuity cannot be
claimed as retained write-back.

For a derived representation `T_M = S(C, ...)`, admissible perturbations must
obey its tangent constraint, schematically `delta_T_M = D_C S delta_C` plus any
other declared causal-coordinate terms. D3/D8 may not vary `delta_T_M`
independently unless D1 has admitted `T_M` as independent state. Doing so would
manufacture extra structural or temporal directions.

## Veto Requirements

Every architecture must satisfy the same hard requirements:

- theory provenance and claim ceiling;
- complete-step causal-state closure;
- native formation from permitted RC variables;
- post-input continuation distinguishable from reconstruction and branch
  relocation;
- release/reconfiguration rather than indefinite accumulation;
- conservation and budget compatibility;
- typed directional read relation and passive null;
- regular total-current closure or explicit deslavement reason;
- write/read loop attribution;
- separation of structural geometry from mobility where required;
- deterministic serialization, reset, migration, and replay;
- disabled-profile compatibility with GRC9V3 mechanics;
- absence of hidden producers or observers; and
- testability without defining success from the candidate's own output.

Failure of a veto requirement rejects the candidate for the affected scope.
Candidate convenience cannot compensate for it.

## Selection Preferences

Candidates that survive the veto requirements may be compared using:

- minimal additional causal state;
- closeness to accepted GRC9V3 mechanics and the frozen reduction relation;
- implementation and verification simplicity;
- computational cost; and
- clarity of telemetry and analysis ownership.

These are preferences, not evidence or ontology. Final selection belongs to
D10 after every load-bearing gate has been evaluated.

## Current Temporalization Policy

Current temporalization is not a default requirement. The regular candidate
keeps `J` and `j` causal within a beat but not independent temporal coordinates.
An explicit `(C,T,J)` state may be selected only if D6 shows that regular
slaving is unavailable or if a declared target requires persistent current
orientation/phase that cannot be represented by the admitted retained-state
architecture.

## Closed-Loop Requirement

The required causal dependency is architecture-neutral:

```text
T_M,k
  -> j_k
  -> J_C,k
  -> declared downstream state consequence
  -> T_M,k+1
```

D2 defines admissible write inputs and D7 closes the complete transition. The
contract does not assume that `C_(k+1)` is the sole write mediator. A valid
architecture may use `J_C,k`, `C_k`, `C_(k+1)`, or another declared downstream
state consequence, provided the dependency, accounting, and controls are
explicit.

## Bounded Debt Policy

An `accepted_bounded` decision may open later work only when every carried debt
records:

```text
debt_id
blocking_scope
candidate_scope
assumption_forbidden_downstream
resolution_gate
must_close_before_D10
```

Later gates may resolve or preserve that debt, but may not silently assume the
missing result. In particular, a missing source-backed joint structural
functional on `(C,T)` cannot be filled by treating `DF(C,T)` as a continuation
Hessian.

## Claim Ceiling Before D10

Before D10 acceptance, this investigation may support only:

```text
source-backed constitutive candidate
bounded architecture rejection
unresolved design debt
specification-writing recommendation
route_to_named_theory_or_constitutive_derivation
close_current_design_tranche_unresolved
```

It cannot support:

- a GRC9V4 runtime or capability;
- native retention or Read-Back in GRC9V3;
- a continuation spectrum implementation;
- memory, adaptive learning, agency, or ecology;
- automatic LGRC inheritance; or
- authorization to modify `src/`.

## Specification-Opening Rule

Normative spec writing may begin only after D10 records:

```text
selected architecture
accepted causal-state and step contract
accepted continuation and Read-Back contracts
accepted serialization/migration/capability boundary
all debts adjudicated and every must-close debt resolved
all remaining nonblocking debt and blocked relabels declared
human acceptance
specification_authorized = true
```

If no current architecture satisfies the frozen target, D10 localizes the
missing requirement and routes named theory, constitutive, candidate-admission,
or discriminator work. It may close this design tranche unresolved, but cannot
infer that GRC9V4 should not be built.
