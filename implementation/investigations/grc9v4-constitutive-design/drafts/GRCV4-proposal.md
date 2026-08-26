# GRC-v4 Substrate Paper — Extraction Skeleton

**Working paper title:**
*Graph Reflexive Coherence V4 (GRC-v4): Profile-Explicit Retention, Read-Back, and Structural Geometry*

**Intended repository destination:**
`geometric-reflexive-coherence/substrates/2026-??-GRC-V4.md`

**Paper relation:**

$$
\text{accepted D0--D10.2 investigation}
\;\xrightarrow{\text{controlled exposition}}\;
\text{GRC-v4 substrate paper}
$$

The main paper defines graph-generic GRC-v4. **Appendix A** defines GRC9V4 as its substantive nine-port specialization. Exact disabled-profile compatibility with GRC9V3 belongs to that specialization.

**Status:** This is an extraction skeleton. It is not a paper draft, a specification, or a new mathematical source.

---

## Editorial Control Header

### Immediate mathematical authority

The immediate source for the paper is the accepted D0–D10.2 investigation. Earlier core papers, GRC-v3, GRC-9, specifications, and runtime records enter the paper only through the lineage already accepted by that investigation.

The paper may:

* reorganize accepted results into a coherent scientific sequence;
* explain accepted equations and definitions;
* introduce an accessible narrative around accepted distinctions;
* assign paper-local equation numbers;
* move detailed contracts into appendices;
* state accepted limitations and negative results.

The paper may not:

* derive replacement equations;
* repair or complete an accepted equation from intuition;
* choose among A, C, CI, OS, RG2b, PC, or CI+PC;
* promote a conditional or open claim;
* silently normalize notation in a way that changes typing, stage, authority, or profile identity;
* turn a runtime, stability, endpoint, attribution, or ranking obligation into a substrate result.

The existing substrate papers provide the expository precedent: GRC-v3 presents a constructive graph substrate and its full loop, while GRC-9 adds a substantive mechanical specialization rather than merely a configuration profile.

### Equation-control rule

Every displayed paper equation must have a one-to-one source entry:

```text
paper equation
    -> D10.2 equation/contract row
    -> D10.2 parent normative object
    -> accepted D10 claim
    -> accepted predecessor lineage
```

The draft should maintain a private crosswalk such as:

```text
paper_eq_id
source_equation_contract_id
source_parent_object_ids
source_claim_ids
notation_changes
stage_preserved
authority_preserved
claim_ceiling
```

The paper may simplify notation only where the crosswalk records exact equivalence.

D10.2 currently supplies the control population of 39 accepted claims, 67 parent normative objects, and 152 normative equation/contract rows, including 85 expanded rows and the 40-row disabled-reduction matrix. The paper need not print all of them, but it must not contain load-bearing mathematics outside them.

### Boundary-control rule

When coherent exposition appears to require an unsupported proposition, the draft stops at that point and records:

```text
PAPER-BOUNDARY-ID:
paper section:
exact sentence or proposition that cannot yet be written:
accepted source currently available:
accepted claim or boundary that prevents it:
why the missing content is scientific rather than expository:
earliest investigation contract that would have to reopen:
```

No successor investigation is predeclared. D11 exists only if this process exposes a specific scientific boundary that the intended paper must cross.

---

# Paper Skeleton

## Abstract

### Paper function

Give the shortest complete statement of what GRC-v4 is, why it exists, what it adds to GRC-v3, how its profile architecture is organized, and what remains outside its claim.

### Content to extract

The abstract should make five moves.

1. **Inherited substrate.**
   Begin from graph Reflexive Coherence with scalar resource $C$, graph-generated transport, oriented current, continuity, identities, and topology-aware lifecycle.

2. **V4 distinction.**
   State that GRC-v4 separates:

   $$
   \text{retention}
   \neq
   \text{Read-Back}
   \neq
   \text{write-back},
   $$

   and places them inside a complete, profile-explicit causal step.

3. **Common architecture.**
   State that $C$ remains the only resource coordinate; every enabled profile declares any authoritative nonresource state; one current is authoritative for the resource write; structural geometry, mobility, current, lifecycle, charge, and event semantics are explicitly typed.

4. **Admitted profiles.**
   State that the current bounded population contains two admitted constitutive families, A and C, crossed with five admitted geometry-temporal realizations:

   $$
   \mathrm{CI},\quad
   \mathrm{OS},\quad
   \mathrm{RG2b},\quad
   \mathrm{PC},\quad
   \mathrm{CI+PC}.
   $$

   These are admitted profiles, not ranked alternatives or an exhaustive theorem.

5. **Substrate factorization and claim ceiling.**
   State the earned bounded relation:

   $$
   \mathrm{GRCV4}
   \xrightarrow{\text{nine-port specialization}}
   \mathrm{GRC9V4}
   \xrightarrow{\text{disabled V4 profile}}
   \mathrm{GRC9V3}.
   $$

   End by saying that the paper defines a design-level substrate architecture. It does not establish runtime implementation, formed-branch reachability, committed endpoint hysteresis, structural or temporal stability, physical nonabsorbability, or profile preference.

### Controlling sources

* `D10DesignSynthesisAndSpecWritingDecision`
* `D10NormativeClaimTopology`
* `D10_2FullSubstrateProvenanceAndPromotionAudit`

D10 selects a profile-explicit common architecture rather than a unique candidate or realization, and D10.2 promotes the accepted common population from the GRC9 lineage to graph-generic GRC-v4.

### Boundary

The abstract must not use:

* “implemented”;
* “observed”;
* “stable”;
* “demonstrated memory”;
* “causally nonredundant”;
* “preferred realization”;
* “complete taxonomy”;
* “lossless across arbitrary topology change.”

---

## 1. Introduction

### 1.1 GRC-v3 as the inherited graph substrate

#### Paper function

Establish what GRC-v4 inherits rather than reconstructing GRC from first principles.

#### Content to extract

Explain that GRC-v3 already supplies:

* a finite graph substrate;
* scalar coherence/resource at vertices;
* graph-local differential summaries;
* positive edge conductance;
* potential and oriented flux;
* continuity and budget preservation;
* basin and spark semantics;
* hierarchy and topology change;
* a distinction between dynamical conductance and analytical labels.

Retain the GRC-v3 closed-loop lineage as historical context, but do not copy its immediate conductance update as the definition of V4:

$$
C
\rightarrow
K[C]
\rightarrow
w
\rightarrow
\Phi
\rightarrow
J
\rightarrow
C.
$$

The V4 paper must say that this loop remains part of the inheritance, but its causal roles are now refined.

#### Controlling sources

* `2026-02-GRC-V3.md`
* `GRCV3-NORMATIVE-SPEC`
* `D10.2-DER-TRANSPORT`
* `D10.2-DER-DIFFERENTIAL`

GRC-v3 explicitly presents itself as an enriched state on which the inherited loop closes, not as a replacement of that loop.

#### Boundary

Do not say that GRC-v3 was mathematically wrong. The V4 claim is that the accepted continuation and Read-Back distinctions require a more explicit causal architecture than the inherited loop alone provides.

---

### 1.2 The continuation and Read-Back gap

#### Paper function

State the exact scientific pressure that led to V4.

#### Content to extract

Present the investigation target:

```text
past activity
    -> formation of an admitted retained causal representation
    -> distinguishable post-input continuation
    -> present-current-conditioned directional Read-Back
    -> total-current/state consequence
    -> write-back into the future retained representation
```

Explain the inherited distinctions:

```text
core primitive state
    != runtime causal state
    != analytical perturbation state

retained causal representation
    != independent runtime state by definition
    != analysis-only slow projector
    != continuation spectrum

retention
    != Read-Back
    != write-back
```

Also state that coordinate covariance, physical current reversal, causal retention, and analytical continuation are separate questions.

#### Controlling sources

* `GRC9V4ConstitutiveDesignBasis`
* D0–D3
* accepted B1/B2 boundaries as consumed by D0–D3

The design basis records both the target chain and these non-equivalences as controlling distinctions.

#### Boundary

This section may explain why V4 was investigated. It must not import failed B1/B2 mappings as V4 equations or treat bounded unchanged-GRC9V3 evidence as a V4 implementation result.

---

### 1.3 Result of the constitutive investigation

#### Paper function

Give the reader the final architecture before entering the details.

#### Content to extract

State that the investigation did not choose one universal retained object or one timing law. It established:

$$
\boxed{
\text{common GRC-v4 contract}
+
\text{constitutive family}
+
\text{geometry-temporal realization}
}
$$

The common contract owns:

* resource authority;
* current authority;
* structural geometry typing;
* mobility/geometry separation;
* charge and tangent;
* complete-step ordering;
* lifecycle identity;
* events and migrations;
* profile identity;
* disabled-reduction surfaces.

The complete profile supplies the candidate-specific current, retained representation, geometry source, writer, and realization-specific timing/history law.

#### Controlling sources

* D10
* D10.2

#### Boundary

Do not flatten A and C into a generic formula. Do not flatten the five realization families into one timing parameter.

---

### 1.4 Contributions of the paper

The introduction should identify the paper’s contributions as exposition of accepted results:

1. a graph-generic V4 state and authority contract;
2. a typed retention–Read-Back–write-back loop;
3. a separation of $K_4$, Hodge geometry, structural current, and transport mobility;
4. two admitted constitutive families;
5. five admitted geometry-temporal realizations;
6. a complete-step and lifecycle contract;
7. a substantive GRC9V4 specialization;
8. an explicit claim ceiling and successor rule.

No contribution should be described as newly proved by the paper.

---

## 2. Roadmap: What Changes and What Does Not

This section should parallel the role of the roadmap in the GRC-v3 paper.

### 2.1 What remains fixed

* $C$ is the authoritative scalar resource.
* Current is an oriented graph quantity.
* Continuity is the sole ordinary resource write.
* Charge accounting follows the actual resource path.
* Graph geometry is generated rather than externally prescribed.
* Identity, topology, event, and conservation semantics remain part of the substrate lineage.
* No producer, observer, scheduler, or analytical object receives hidden causal authority.

### 2.2 What changes in V4

* retention, Read-Back, and write-back become distinct contracts;
* every executable state binds one constitutive family and one realization;
* authoritative, derived, transient, and analysis-only surfaces are separated;
* $K_4$, $H_{1,\mathrm{form}}$, $G_J$, $h_4$, and $M_4$ are separately typed;
* one complete-step order governs current, continuity, post-continuity refresh, writers, validation, and atomic commit;
* lifecycle identity includes current state, reset state, charge target, graph, context, and profile identity;
* topology events and migrations transform the entire lifecycle tuple.

### 2.3 What remains profile-dependent

* the authoritative nonresource state;
* the retained causal representation;
* the Read-Back operator;
* the constitutive current closure;
* the write-back law;
* the structural source;
* the geometry-temporal realization;
* normalization, units, gauge, domain, solver, and composition law.

### 2.4 What remains specialization-dependent

The following are not part of graph-generic GRC-v4:

* nine ordered ports;
* the fixed $3\times3$ row/column chart;
* the fixed row-basis differential backend;
* saturation at nine occupied ports;
* GRC9 mechanical expansion;
* GRC9 hybrid spark completion;
* GRC9 child-basin stabilization;
* GRC9 column coarse-graining;
* the exact GRC9V3 initializer binding;
* exact disabled-profile compatibility with GRC9V3.

### Controlling sources

* D10 normative claims N-001 through N-009
* D10.2 provenance classification

### Boundary

The current A/C-by-realization population is the complete **initial admitted population**, not the complete set of all possible GRC-v4 profiles.

---

## 3. Mathematical Setting and Authority

### 3.1 Finite oriented graph and cochain spaces

#### Content to extract

Define the accepted graph setting:

* finite graph $\mathcal G=(V,E)$;
* one fixed coordinate orientation per edge;
* vertex resource $C$;
* antisymmetric/oriented edge current $J_C$;
* incidence operator $B$;
* declared graph measure $\mu$;
* declared charge covector $\varpi$;
* vertex and one-form spaces;
* positive Hodge objects on their admitted domains.

Use the exact orientation, incidence, flat/sharp, and one-form typing from the accepted Hodge correction.

#### Required source objects

* `CORE-C-AUTHORITY`
* `CORE-INCIDENCE-CONTINUITY`
* `C-HODGE-MAPS`
* `GEOM-H1-FORM`
* `GEOM-GJ`
* `GEOM-COVARIANCE`

#### Boundary

Do not infer physical reversal from coordinate reorientation. Do not identify equal matrix dimensions with equal mathematical types.

---

### 3.2 Complete profile identity

#### Content to extract

Define a complete executable profile as the binding of:

```text
constitutive_family
realization_family
parameter set
units
gauge
normalization
admission domain
solver contract
composition law
differential backend
geometry profile
lifecycle and reduction contracts
```

Use a profile symbol such as $p$, provided the notation crosswalk records its equivalence to the D9/D10 profile identity.

State:

$$
p=(a,r,\Theta_p),
$$

only as a shorthand for the accepted profile tuple, not as a newly reduced ontology.

#### Required source objects

* `L-PROFILE-GRAMMAR`
* `SPEC-PROFILE-GRAMMAR`
* `SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER`
* `SPEC-COMPOSITION-PROFILE-IDENTITY`

#### Boundary

Changing a load-bearing parameterization, writer, realization, geometry profile, solver, gain, normalization, or composition law may require a new complete-profile identity.

---

### 3.3 State authority classes

#### Content to extract

For each profile distinguish:

1. **authoritative resource state**;
2. **authoritative nonresource state**;
3. **derived causal surfaces**;
4. **same-beat transient solver surfaces**;
5. **serialized lifecycle metadata**;
6. **analysis-only perturbation and spectral objects**.

State that:

* $C$ is the only resource coordinate;
* Candidate A adds positive edge state $W_A$;
* Candidate C writes only $C$;
* PC adds its declared persistent $K_4$-history state;
* $J_C$, selectors, Hodge surfaces, geometry, and solver roots are not automatically independent state;
* analytical projectors and spectra are never runtime authority merely because they are mathematically derived.

#### Required source objects

* `CORE-C-AUTHORITY`
* `A-STATE-REDUCTION`
* `C-AUTHORITY`
* `REAL-PC`
* `L-SNAPSHOT-RESET`

#### Boundary

Do not present one universal state tuple that falsely serializes all optional profile surfaces.

---

### 3.4 Differential backend contract

#### Content to extract

Define the graph-generic requirement:

* explicit;
* deterministic;
* serialized or reproducibly reconstructible;
* declared frame and orientation;
* declared regularization;
* declared freshness;
* declared covariance semantics.

Use the GRC-v3 induced-frame/weighted-least-squares construction as the current reference backend.

#### Required source objects

* `BASE-GRC-DIFFERENTIAL`

#### Boundary

The GRC-v3 backend is a canonical current reference, not a theorem that every future GRC-v4 profile must use that exact construction. The GRC9 fixed row-basis backend belongs in Appendix A.

---

## 4. Resource Dynamics, Charge, and Structural Tangent

### 4.1 Authoritative continuity

Include the accepted general continuity equation:

$$
C_{\mathrm{next}} =
C-\Delta t\,B J_C+B_{\mathrm{ext}}+S_{\mathrm{ext}}.
$$

Explain:

* $J_C$ is the one authoritative current;
* ordinary candidate and history writers do not write $C$ again;
* external terms must be typed;
* continuity executes exactly once per accepted complete step.

#### Required source objects

* `CORE-INCIDENCE-CONTINUITY`
* `L-AUTHORITATIVE-CURRENT`
* `L-CONTINUITY-WRITE`

---

### 4.2 General charge

Include:

$$
Q_\varpi(C)=\varpi^\top C.
$$

Present the unit-measure profile as:

$$
\varpi=\mathbf 1,
\qquad
Q(C)=\sum_i C_i,
$$

without making it the only lawful charge profile.

#### Required source objects

* `CORE-GENERAL-CHARGE`
* `CORE-UNIT-MEASURE`

---

### 4.3 Complete-state charge tangent

Include:

$$
DQ_\varpi[\delta X] =
\varpi^\top\delta C,
$$

and:

$$
V_{Q,\varpi} =
\ker DQ_\varpi =
\left\{
\delta X:\varpi^\top\delta C=0
\right\}.
$$

Explain that nonresource variations remain unrestricted by the charge tangent unless another profile contract constrains them.

#### Required source objects

* `CORE-CHARGE-TANGENT`

---

### 4.4 Structural $C$-sector projector and full-tangent retraction

Include the accepted $H_0$-orthogonal structural projector:

$$
\Pi_{Q,C,H_0}(\delta C) =
\delta C
-
H_0^{-1}\varpi
\frac{\varpi^\top\delta C}
{\varpi^\top H_0^{-1}\varpi}.
$$

Then distinguish its identity extension to nonresource variations as a canonical complete-tangent retraction.

#### Required source objects

* `CORE-STRUCTURAL-CHARGE-PROJECTOR`

#### Boundary

The identity extension is not a full-state orthogonal projector until a complete-state product metric is frozen.

---

### 4.5 Ordinary-step charge budget

State the accepted stage rule:

```text
one authoritative continuity write
    -> final resource state
    -> compare with Q_target_next
    -> only then permit final atomic commit
```

Do not add an event delta to a charge target that has already been updated by the event contract.

---

### 4.6 Topology-event resource accounting

Include the accepted decomposition:

$$
C^+
=
T_{C,\mathrm{evt}}C^-  +
\Delta C_{\mathrm{event}},
$$

with conservative transport condition:

$$
\varpi_+^\top T_{C,\mathrm{evt}} =
\varpi_-^\top,
$$

event receipt:

$$
\Delta Q_{\mathrm{event}} =
\varpi_+^\top C^+  -
\varpi_-^\top C^-,
$$

and lifecycle-target update:

$$
Q_{\mathrm{target}}^+ =
Q_{\mathrm{target}}^-  +
\Delta Q_{\mathrm{event}} =
\varpi_+^\top C^+.
$$

#### Required source objects

* `CORE-EXTERNAL-EVENT-CHARGE`
* `L-TOPOLOGY-EVENT`
* `L-ORDERED-RECEIPTS`

#### Boundary

A scalar charge receipt does not replace the resource-coordinate increment $\Delta C_{\mathrm{event}}$.

---

## 5. The GRC-v4 Causal Loop

### 5.1 Role-level loop

Present the architecture-neutral causal relation:

$$
T_{M,k}
\longrightarrow
j_k
\longrightarrow
J_{C,k}
\longrightarrow
\text{declared state consequence}
\longrightarrow
T_{M,k+1}.
$$

Explain that $T_M$ names the retained causal **role**. It does not assert that every profile serializes an independent coordinate named $T_M$.

Candidate A realizes this role through retained $W_A$. Candidate C realizes it through an admitted sector and response derived from authoritative $C$. PC introduces its own declared persistent structural history.

### Controlling sources

* D2
* D5/D5-v2
* D6/D6-v2
* D7/D7-v2
* D10

The D7 investigation explicitly required closure of the retained-object to read-current to total-current to downstream consequence to future-retention chain.

---

### 5.2 Retention

Define retention by the accepted profile’s authoritative state and writer:

* what persists across beats;
* which input forms it;
* how it is retained;
* how it is released, reset, archived, or reconfigured;
* what capacity/domain restrictions apply.

Do not define retention merely by a slow coefficient.

---

### 5.3 Read-Back

Define Read-Back as the profile-declared map by which retained causal structure conditions present activity into an oriented current contribution.

Read-Back must be distinguished from:

* observing retained state;
* reconstructing retained state from current $C$;
* multiplying current by a diagnostic;
* an analysis-only projector;
* ordinary immediate current generation.

---

### 5.4 Authoritative total current

Use the generic role equation:

$$
J_C =
J_0+\zeta\,j,
$$

only as the common current-composition interface.

Candidate-specific equations, domains, and root conditions belong to their profile sections.

Explain that explicit notation $J_0+\zeta j$ does not by itself prove that the Read-Back contribution is physically nonredundant.

---

### 5.5 Write-back

Define write-back as the accepted profile-specific state transition by which the consequences of the current beat alter the retained causal representation available to later beats.

The paper should distinguish:

* direct retained-state writer;
* resource-mediated future sector change;
* realization-history writer;
* lifecycle reset or loss;
* topology-event transport or reinitialization.

---

### 5.6 Passive and null surfaces

Extract the accepted distinctions among:

* no formation/write input;
* zero present current;
* read disabled;
* writer disabled;
* frozen retained state;
* passive baseline;
* failed solve;
* disabled V4 compatibility profile.

#### Boundary

A passive null must be defined per profile. One null condition must not be used as a substitute for another.

---

## 6. Structural Geometry, Hodge Typing, and Mobility

### 6.1 Core structural role and graph realization

Explain:

$$
K\longrightarrow g[K]
$$

as the substrate-independent core-theory role.

Then define graph $K_4$ as the accepted GRC realization:

* graph-local;
* symmetric bilinear form;
* acting on the oriented one-form space;
* assembled from overlapping graph restrictions;
* not identical to core $K$;
* not the legacy GRC9 cached row tensor.

#### Required source objects

* `CORE-K-STRUCTURAL-ROLE`
* `GEOM-K4`
* `GEOM-ASSEMBLY`

---

### 6.2 Reference Hodge embedding

Include the accepted reference construction:

$$
H_{0,\mathrm{ref}} =
\operatorname{diag}(\mu),
$$

$$
H_{1,\mathrm{form,ref}} =
\operatorname{diag}(W_{\mathrm{ref}}),
$$

$$
G_{J,\mathrm{ref}} =
\operatorname{diag}(W_{\mathrm{ref}}^{-1}).
$$

Explain that this is a V4 reference embedding built from GRC surfaces. It is not a claim that GRC-v3 already possessed the full V4 physical geometry.

#### Required source objects

* `GEOM-H1-FORM`
* `GEOM-GJ`

---

### 6.3 Structural crossing

Include the accepted crossing:

$$
H_{1,\mathrm{form}}^+  =
H_{1,\mathrm{form,ref}}  +
\kappa_H\,\Delta K_4,
$$

on the declared positive admitted domain, followed by:

$$
G_J(h)
=
H_{1,\mathrm{form}}(h)^{-1},
$$

and:

$$
j_{\mathrm{struct}}^\flat =
G_J\,j_{\mathrm{flux}}.
$$

State that the declared geometry profile constructs $h_4$ from the accepted Hodge/structural package.

#### Required source objects

* `GEOM-K4-TO-H4-TO-h4`
* `GEOM-H1-FORM`
* `GEOM-GJ`

---

### 6.4 Transport mobility

Define $M_4$ as the candidate-specific transport mobility operator on physical current space.

State explicitly:

$$
M_4
\neq
H_{1,\mathrm{form}}
\neq
G_J
\neq
h_4
\neq
\text{overlap-normalized }K_4\text{ assembly}.
$$

For Candidate A, include the accepted factorization:

$$
M_{4,A}
=
\eta\,\operatorname{diag}(W_A).
$$

Candidate C’s transport factorization must be copied exactly from its accepted source rather than inferred from a matrix resemblance.

#### Required source objects

* `GEOM-M4`

---

### 6.5 Covariance

State the accepted graph-relabeling and signed-edge-coordinate covariance contract for:

* $K_4$ assembly;
* Hodge maps;
* flat/sharp maps;
* structural current;
* current consumers;
* topology transport.

#### Boundary

The paper defines the covariance contract. It does not claim that all general SPD conditioning, inverse solvers, component/cycle boundaries, or runtime adapters have been executably verified.

---

### 6.6 Geometry claim ceiling

This section must preserve:

* the reference normalization is admitted, not proved unique;
* alternative star-pair and richer DEC edge-volume profiles remain possible successors;
* physical units and cross-profile magnitude comparison remain open;
* structural geometry does not acquire mobility authority by numerical coincidence.

---

## 7. Complete Profile Grammar

### 7.1 Two independent profile axes

Define the current profile population as:

$$
\{\mathrm A,\mathrm C\}
\times
\{\mathrm{CI},\mathrm{OS},\mathrm{RG2b},\mathrm{PC},\mathrm{CI+PC}\}.
$$

Explain:

* A/C choose the constitutive family;
* CI/OS/RG2b/PC/CI+PC choose the geometry-temporal realization;
* one executable state binds exactly one member of each axis;
* the product gives ten current complete profile identities.

### Required source objects

* `L-PROFILE-GRAMMAR`
* `SPEC-PROFILE-GRAMMAR`
* `SPEC-COMPOSITION-PROFILE-IDENTITY`

---

### 7.2 Profile-local contracts

Every profile must declare:

* authoritative state;
* derived and transient surfaces;
* parameters;
* units;
* gauge;
* normalization;
* domain;
* solver;
* root-selection rule;
* structural source;
* geometry profile;
* history law;
* composition gains;
* failure disposition;
* lifecycle maps;
* disabled reduction.

### Required source objects

* `SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER`
* `SPEC-CLAIM-CEILINGS`

---

### 7.3 Successor admission

State that a materially distinct:

* constitutive law;
* retained writer;
* current closure;
* persistent-carrier law;
* geometry map;
* temporal realization;
* composition gain;
* normalization;
* lifecycle or event law

requires a new complete-profile identity and reopens the earliest accepted contract it changes.

### Required source objects

* `SPEC-FUTURE-ADMISSION`

---

### 7.4 Candidate B

Candidate B appears only as a reserved, nonexecutable successor slot.

State:

* B is not rejected;
* B currently lacks a source-backed formation, retention, release, capacity, and lifecycle writer;
* PC is not B and cannot be relabeled as B.

### Required source objects

* `SPEC-B-SLOT`

### Boundary

The paper must not provide a speculative B equation or fill the missing writer.

---

## 8. Constitutive Family A: Retained Edge Mobility

### 8.1 Scientific role

Present Candidate A as the admitted normalized, nondimensional, revision-specific temporalized-mobility and Read-Back family.

It is not inherited core and is not the unique V4 completion.

---

### 8.2 Authoritative state

Define the profile-authoritative state as:

$$
X_A=(C,W_A,\ldots),
$$

where $C$ is the resource coordinate and $W_A>0$ is the authoritative retained edge-mobility state. Any realization-specific history is added only by the chosen complete profile.

### Required source objects

* `A-STATE-REDUCTION`

---

### 8.3 Accepted conductance functional

Include the accepted curvature-disabled D7 functional exactly:

$$
G_{W,e}(C,J)
=
\max\!\left(
W_{\mathrm{floor}},
\exp\!\left[
-\alpha\frac{C_u+C_v}{2}
-\beta\frac{\lVert D_u-D_v\rVert^2}{2}
-\gamma\frac{J_e^2}{2}
\right]
\right).
$$

Explain:

* $D_i(C)$ is supplied by the admitted graph differential backend;
* curvature is disabled in the accepted current profile;
* the functional is graph-generic;
* the GRC9 row-basis backend is only one specialization.

### Required source objects

* `A-GW-FUNCTIONAL`

### Boundary

Any curvature-conditioned successor requires a new profile identity and reopened provenance.

---

### 8.4 Pre-read reference

Include:

$$
\widehat W_A =
G_W(C,J_{0,A})
$$

at the accepted fresh pre-read stage.

### Required source objects

* `A-WHAT`

---

### 8.5 Directional contrast

Include:

$$
q_A =
\frac{W_A-\widehat W_A}
{W_A+\widehat W_A}.
$$

Explain why positivity supplies a regular denominator on the admitted domain.

### Required source objects

* `A-DIRECTIONAL-CONTRAST`

---

### 8.6 Read-Back and current closure

Include the accepted equations:

$$
j_A =
\chi_A q_A J_{C,A},
$$

$$
J_{C,A}
=
J_{0,A}+\zeta_A j_A.
$$

On the regular algebraic domain, include:

$$
J_{C,A} =
\frac{J_{0,A}}
{1-\zeta_A\chi_A q_A}.
$$

Preserve the exact candidate- and realization-specific root/domain conditions from D6, D7, CI, and CI+PC.

### Required source objects

* `A-READ-CLOSURE`

### Boundary

Do not infer physical nonabsorbability or committed endpoint effect from the existence of this algebraic closure.

---

### 8.7 Post-continuity writer target

After accepted continuity and fresh post-state differential reconstruction, include:

$$
W_{\mathrm{drv},A} =
G_W(C_{\mathrm{next}},J_{C,A}).
$$

Pre-continuity differential caches are inadmissible writer inputs.

### Required source objects

* `A-WRITER-TARGET`
* `L-POSTCONTINUITY-REFRESH`

---

### 8.8 Retained writer

Include:

$$
\log W_A^{\mathrm{next}} =
a_A\log W_A +
(1-a_A)\log W_{\mathrm{drv},A}.
$$

Explain:

* one authoritative writer;
* positivity preservation through log coordinates;
* one-beat causal retention;
* profile-declared release/reconfiguration;
* atomic commit with the complete state.

### Required source objects

* `A-RETAINED-WRITER`

---

### 8.9 Candidate A initialization and migration

Explain the graph-generic history-free initializer:

```text
target graph and context
    -> rebuild admitted target differential surfaces
    -> evaluate accepted curvature-disabled G_W reference stage
    -> target-profile readmission
    -> emit direction-specific history-loss receipt
```

The exact GRC9V3 base-conductance reconstruction belongs to Appendix A.

### Required source objects

* `L-A-INITIALIZER-GRC`
* `L-PROFILE-MIGRATION`

---

### 8.10 Candidate A boundary

State explicitly:

* A is admitted, not preferred;
* the current law is normalized and nondimensional;
* physical dimensionalization remains open;
* A’s physical nonabsorbability remains open;
* formed runtime formation/retention/release remains unexecuted;
* no committed endpoint witness is claimed;
* A is not inherited core;
* A is not unique.

---

## 9. Constitutive Family C: Derived $C$-Sector Hodge Response

### 9.1 Scientific role

Present Candidate C as the admitted revision-specific family in which an historically formed sector derived from authoritative $C$ receives constitutive Read-Back authority without becoming an independent resource or hidden state coordinate.

---

### 9.2 Authoritative state

State:

* $C$ remains the only independently written candidate coordinate;
* $T_C$, selectors, Hodge surfaces, resolvents, and read surfaces are derived;
* any independent realization-history state belongs to the chosen realization, not to Candidate C by default.

### Required source objects

* `C-AUTHORITY`

---

### 9.3 Derived sector

Present $T_C$ as the accepted sector derived from authoritative $C$ through the declared selector.

The paper must copy exactly:

* selector input;
* selected operator;
* rank rule;
* strict-gap or boundary semantics;
* stratum identity;
* post-state rederivation rule.

### Required source objects

* `C-SECTOR`
* `C-SELECTOR`

### Boundary

Do not turn the analysis projector into runtime authority. Do not claim smooth passage through selector-rank boundaries.

---

### 9.4 Hodge package

Insert the exact accepted Candidate C equations for:

* $H_0$;
* $H_1$;
* flat/sharp identifications;
* selected and physical one-form spaces;
* $\Delta_1$;
* pre/post identification maps.

Do not reconstruct these formulas from matrix shape or from earlier uncorrected records.

### Required source objects

* `C-HODGE-MAPS`

---

### 9.5 Resolvent Read-Back

Insert the exact accepted chain from D5-v2/D6-v2/D7-v2 and the D10.2 equation registry:

```text
selected sector
    -> typed Hodge Laplacian
    -> regular resolvent
    -> lawful selected/physical identification
    -> one external chi gate
    -> physical read-current contribution
```

State the accepted resolvent role:

$$
R_C
=
(I+\tau_C\Delta_1)^{-1},
$$

with the precise selected/physical mappings and gain placement copied from the controlling record.

### Required source objects

* `C-READ-BACK`

### Boundary

The $\chi_C$ gate must appear exactly once. Positivity or contraction in retained coordinates must not be promoted into a physical norm claim unless the accepted identification supports it.

---

### 9.6 Candidate C write-back

Explain the accepted C-only authority:

```text
authoritative current
    -> single continuity update of C
    -> accepted post-state
    -> sector and Hodge surfaces rederived from that C
    -> future Read-Back changes accordingly
```

This is the Candidate C write/read closure. It is not an independent writer to a hidden $T_C$ coordinate.

---

### 9.7 Candidate C boundary

State explicitly:

* Candidate C is admitted, not preferred;
* constitutive operator-level mediation is accepted on the declared regular selector strata;
* physical nonabsorbability remains open;
* general nonidentity complete-chain endpoint effect remains open;
* runtime mediation remains unexecuted;
* singular or rank-changing passage requires a named successor profile.

---

## 10. Geometry-Temporal Realization Families

### 10.1 Why realization is a separate axis

Explain that a constitutive family answers:

> What is retained, how is it read, and what writes it?

A realization answers:

> At what stage is generated geometry consumed, and what geometry/history state persists across beats?

The realization changes timing and history semantics without silently changing A into C or C into A.

---

### 10.2 Coupled Implicit — CI

#### Content to extract

Present CI as the simultaneous current/geometry root.

For Candidate A include:

* the exact accepted self-map;
* bounded invariant domain;
* contraction condition;
* unique root.

For Candidate C include:

* stratum-local root problem;
* strict regularity conditions;
* exactly one required self-consistent regular root across admissible strata;
* fail-closed disposition for zero, multiple, singular, or nonfinite roots.

### Required source objects

* `REAL-CI`

### Controlling sources

* `GeometryTemporalRealizationSuccessorCoupledImplicit`
* `D8BCoupledArchitectureLocalContinuationAnalysis`

### Boundary

Local bounded root uniqueness is not global stability, formed-branch reachability, or continuation-spectrum evidence.

---

### 10.3 Operator Split — OS

#### Content to extract

Present the frozen one-pass order:

```text
predict current
    -> construct generated geometry
    -> correct current
    -> evaluate declared split residual
```

Include the exact A and C predictor, geometry, corrector, and residual equations from the accepted OS record.

### Required source objects

* `REAL-OS`

### Boundary

The split residual is not automatically a $\Delta t$-truncation theorem. A same-beat geometry consumer does not by itself prove nonzero committed endpoint effect.

---

### 10.4 Reconstructed Geometry — RG2b

#### Content to extract

Present RG2b as:

* a bounded reconstructed-geometry realization;
* defined relative to a frozen, family-local equivariant extension;
* possessing the accepted unique bounded Lipschitz invariant section.

Insert the exact reconstruction map and domain contract from the accepted RG record.

### Required source objects

* `REAL-RG2B`

### Boundary

Do not claim:

* a unique reconstruction beyond the frozen completion;
* $C^1$ differentiability;
* a classical derivative graph;
* structural spectrum;
* stability.

---

### 10.5 Persistent Carrier — PC

#### Content to extract

Present PC as the specific admitted:

* scalar-ZOH;
* one-$\tau_{\mathrm{PC}}$;
* independently authoritative;
* persistent $K_4$-history realization.

Insert the exact accepted:

* history state;
* retention law;
* release law;
* source consumption;
* reset and lifecycle behavior.

### Required source objects

* `REAL-PC`

### Boundary

PC is not a universal history law and is not Candidate B.

---

### 10.6 Coupled Implicit plus Persistent Carrier — CI+PC

#### Content to extract

Present the exact accepted composition:

```text
unit immediate CI contribution
+
unit retained PC contribution
```

with steady structural-source gain two.

For A include the accepted bounded-domain composite contraction and root uniqueness.

For C include the accepted stratum-local composite contraction and exactly one self-consistent regular root.

### Required source objects

* `REAL-CI-PC`
* `SPEC-COMPOSITION-PROFILE-IDENTITY`

### Boundary

The gain-two profile is one revision-specific composition, not a unique or generally optimal composition law.

---

### 10.7 Comparative disposition

End the section with a compact table:

| Realization | Accepted role                       | What is not claimed                      |
| ----------- | ----------------------------------- | ---------------------------------------- |
| CI          | simultaneous current/geometry root  | global stability                         |
| OS          | one-pass staged geometry feedback   | equivalence to CI beyond accepted bounds |
| RG2b        | bounded reconstructed geometry      | unique universal reconstruction          |
| PC          | persistent $K_4$ history          | universal memory law                     |
| CI+PC       | immediate plus retained composition | preferred or unique hybrid               |

No ranking language belongs in this section.

---

## 11. Full Closed GRC-v4 Step

This section should play the role that the algorithmic loop plays in the GRC-v3 paper, but it must preserve profile-dependent substages.

### 11.1 Inputs

List:

```text
current complete profile identity
current authoritative state X_current
reset baseline X_reset
graph and orientation
context and differential-backend identity
Q_target
external inputs
event/migration status
solver and domain contract
```

---

### 11.2 Common outer order

Use the following as a structural skeleton. Replace each line with the exact accepted D9/D10.2 stage language during drafting.

```text
1. Validate complete profile, graph, context, state, Q_target,
   parameter identity, solver, and domain.

2. Reconstruct all required pre-read derived surfaces from
   authoritative current state.

3. Execute the selected realization's candidate-specific
   current/geometry/history substages.

4. Produce exactly one authoritative J_C.

5. Execute continuity exactly once.

6. Validate resource domain and ordinary-step charge budget.

7. Rebuild every post-continuity surface required by the
   candidate or history writer.

8. Execute the candidate-specific retained/write-back law.

9. Execute the realization-specific history writer or release.

10. Rebuild declared final derived surfaces.

11. Validate complete-state domain, profile invariants,
    lifecycle tuple, receipts, and serializer contract.

12. Commit all authoritative coordinates atomically.
```

### Required source objects

* `L-AUTHORITATIVE-CURRENT`
* `L-CONTINUITY-WRITE`
* `L-POSTCONTINUITY-REFRESH`
* `L-ATOMICITY`

---

### 11.3 Realization-specific internal order

The paper must not imply that CI, OS, RG2b, PC, and CI+PC share one internal solver order.

The full-loop algorithm should call a named profile-local subroutine:

```text
(J_C, geometry_state, history_candidate, solver_receipt)
    = realize_profile_p(prestate, context)
```

That notation is expositional only. Its implementation must be expanded through the exact accepted realization equations.

---

### 11.4 Failure atomicity

State that any:

* singular root;
* missing root;
* multiple inadmissible roots;
* nonfinite result;
* invalid domain;
* charge failure;
* positivity failure;
* failed target readmission;
* untyped event;
* serializer mismatch

commits nothing.

### Required source objects

* `L-SINGULAR-FAIL-CLOSED`
* `L-ATOMICITY`

---

### 11.5 No hidden same-beat authority

State that:

* diagnostics do not become writers;
* analysis projectors do not become state;
* stale pre-continuity caches do not feed post-continuity writers;
* candidate writers do not perform a second resource update;
* telemetry current is not automatically the structural current;
* scheduler or RNG state has no unregistered scientific authority.

---

## 12. Lifecycle, Reset, Migration, and Events

### 12.1 Lifecycle identity

Define lifecycle identity as containing, at minimum:

```text
X_current
X_reset
Q_target
graph identity
context identity
complete profile identity
declared serialized scientific state
```

### Required source objects

* `L-SNAPSHOT-RESET`

---

### 12.2 Snapshot and restoration

Explain that a scientific snapshot binds the complete lifecycle identity, not merely current arrays.

Representation caches may be rebuilt and need not be scientific identity unless the profile explicitly declares otherwise.

---

### 12.3 Reset

Reset returns to the transformed current reset baseline associated with the current graph and profile.

A topology event or profile migration must transform the reset baseline together with current state and $Q_{\mathrm{target}}$. Reset may not resurrect an obsolete graph or obsolete profile semantics.

---

### 12.4 Profile migration

Present migration as an ordered map:

$$
p_{\mathrm{source}}
\longrightarrow
p_{\mathrm{target}}.
$$

Require:

* typed source state;
* typed target state;
* target initializer where needed;
* history transport, archive, reset, or loss;
* target readmission;
* direction-specific receipt;
* atomic commit.

### Required source objects

* `L-PROFILE-MIGRATION`
* `L-ORDERED-RECEIPTS`

### Boundary

Endpoint profile coverage is not evidence that the crossing itself is lawful.

---

### 12.5 Topology events

Present topology change as a typed source-graph to target-graph continuation.

Separately map:

* resource state;
* current/reset baseline;
* charge target;
* Candidate A history;
* Candidate C derived-sector reconstruction;
* realization-history state;
* profile/context identity;
* receipts.

### Required source objects

* `L-TOPOLOGY-EVENT`
* `CORE-EXTERNAL-EVENT-CHARGE`

---

### 12.6 History transport and loss

State the accepted negative boundary:

> Generic lossless history preservation across topology change is not canonically definable without sufficient typed lineage.

Therefore each profile/event pair must provide one of:

* lawful history transport;
* partial transport with explicit information-loss receipt;
* archive;
* reset;
* target reconstruction;
* rejection.

---

### 12.7 Candidate A history-free initializer

Describe the graph-generic initializer in the main text.

Move the exact GRC9V3 initializer binding to Appendix A.

---

### 12.8 Lifecycle claim ceiling

This section defines lifecycle contracts. It does not claim that runtime snapshot, replay, event, migration, and failure atomicity have already passed implementation-level conformance.

---

## 13. Continuation and Analysis Interfaces

### 13.1 Purpose

Explain how GRC-v4 exposes the correctly separated objects needed for later continuation analysis without serializing the analysis as runtime state.

### 13.2 Four distinct operator families

Preserve the accepted distinction:

```text
structural functional/Hessian
    -> alpha_n

temporal generator or complete-step derivative
    -> gamma_n or multipliers mu_n

Read-Back derivative
    -> beta_n

spatial graph operator -Delta_h
    -> lambda_n
```

Explain that these may be compared only under declared mappings, branch assumptions, metrics, domains, and regularity.

### Controlling sources

* D3
* D8-A
* D8-B
* D10 conditional claims C-001 and C-005

The design basis explicitly rejects treating these as one universal spectrum.

---

### 13.3 Structural target

Describe the accepted branch-sensitive distinction:

```text
smoothly slaved branch
    -> reduced self-adjoint structural object may be admissible

active or joint branch
    -> joint, nonselfadjoint, or DAE object may be required
```

Do not present a universal self-adjoint continuation Hessian for all realizations.

---

### 13.4 Current analysis status

State only:

* the required operator surfaces and derivative contracts have been identified for the admitted profiles;
* bounded regularity and constructibility results exist for the declared local domains;
* no formed branch, numerical operator, analysis metric, or stability spectrum is instantiated by the paper.

### Boundary

Any claim about:

* $\alpha_n$;
* $\gamma_n$;
* $\mu_n$;
* stability;
* slow modes;
* nonnormal growth;
* continuation-spectrum identity

must stop at `PAPER-BOUNDARY` unless supported by a later accepted investigation.

---

## 14. Inheritance, Specialization, and Reduction

### 14.1 Graph-generic inheritance from GRC-v3

State that GRC-v4 inherits or reuses:

* scalar vertex resource;
* finite oriented graph;
* graph differential contract;
* positive scalar transport reference;
* potential and potential-flow equations;
* incidence continuity;
* graph measure and charge;
* identity/topology lineage.

State that V4 adds a new causal and structural contract around those inherited elements.

---

### 14.2 GRC-v4 to GRC9V4

State:

$$
\mathrm{GRCV4}
\longrightarrow
\mathrm{GRC9V4}
$$

by addition of the exact objects classified as GRC9-intrinsic or GRC9-specialization-specific.

GRC9V4 is not merely a compatibility shim. It retains substantive nine-port mechanics.

---

### 14.3 GRC9V4 to GRC9V3

State:

$$
\mathrm{GRC9V4}
\longrightarrow
\mathrm{GRC9V3}
$$

through the profile-scoped disabled reduction.

The reduction must be independently stated for:

1. transition;
2. authoritative state;
3. observable surface;
4. lifecycle.

Passing one does not imply the others.

### Required source objects

* `BASE-DISABLED-TRANSITION`
* `BASE-DISABLED-STATE`
* `BASE-DISABLED-OBSERVABLE`
* `BASE-DISABLED-LIFECYCLE`

### Boundary

The exact reduction is GRC9 specialization content. It is not a graph-generic GRC-v4 theorem.

---

## 15. Claims Established by the Substrate Definition

### 15.1 Positive bounded claims

The paper may state that the accepted investigation establishes, for the current initial population:

* a graph-generic profile-explicit V4 architecture;
* $C$-only resource authority;
* declared nonresource authority per profile;
* one authoritative current and one continuity write;
* general charge, tangent, and structural projection contracts;
* typed $K_4$, Hodge, geometry, and mobility separation;
* two admitted constitutive families;
* five admitted realization families;
* ten complete current profile identities;
* complete-step ordering and atomic failure;
* typed lifecycle, reset, event, and migration grammar;
* exact profile-scoped disabled compatibility after GRC9 specialization;
* the bounded factorization:

  $$
  \mathrm{GRCV4}
  \rightarrow
  \mathrm{GRC9V4}
  \rightarrow
  \mathrm{GRC9V3}.
  $$

### Controlling sources

* D10
* D10.2

---

### 15.2 Negative and limiting claims

The paper must state that it does **not** establish:

* implementation completion;
* runtime formation, retention, release, or replay;
* formed-branch reachability;
* nonzero committed endpoint effect;
* endpoint hysteresis;
* structural stability;
* temporal stability;
* continuation-spectrum identity;
* physical nonabsorbability of A or C;
* physical-channel attribution;
* physical dimensionalization of A;
* cross-profile capacity or magnitude comparison;
* candidate or realization ranking;
* unique composition;
* unique Hodge normalization;
* lossless generic topology-history transport;
* singular continuation;
* future-exhaustive V4 taxonomy.

D10 records these as conditional, open, or negative claims rather than as a mandatory successor checklist.

---

## 16. Conclusion

### Paper function

Close the substrate definition without turning limitations into a promise of future results.

### Content to extract

The conclusion should state:

1. GRC-v4 retains the graph RC resource-and-current lineage.
2. Its revision-distinct contribution is the explicit causal separation and closure of retention, Read-Back, total current, write-back, structural geometry, and lifecycle.
3. The common architecture is profile-explicit rather than built around one universal constitutive law.
4. A and C are both admitted.
5. Five realization families are admitted without ranking.
6. GRC9V4 is a substantive specialization.
7. GRC9V3 remains the exact disabled target.
8. Strong runtime, stability, attribution, and preference claims remain outside the paper.

### Boundary

Do not end with “future work will prove” any open claim. State only the accepted boundary and the rule that materially distinct successors reopen the earliest affected contract.

---

# Appendices

## Appendix A. GRC9V4: Nine-Port Specialization of GRC-v4

This appendix is the substantive GRC9V4 extension. It must import the common V4 equations rather than duplicate a second core dynamics.

### A.1 Specialization statement

State:

```text
GRC9V4
    = GRCV4 common contract
    + nine-port graph mechanics
    + GRC9 differential specialization
    + GRC9 topology/refinement mechanics
    + exact GRC9V3 disabled compatibility
```

### A.2 Port-labeled graph

Extract from the existing GRC-9 lineage:

* nine ordered ports;
* endpoint port pairs;
* active/inactive ports;
* active degree;
* edge orientation and antisymmetric flux;
* per-edge versus per-port storage interpretation.

### Required source objects

* `GRC9-ORDERED-PORTS`

---

### A.3 Fixed $3\times3$ chart

Define:

* three mode rows;
* three polarity columns;
* fixed port-to-$(a,b)$ map;
* row role in the local directional backend;
* column role in interface routing, refinement, and coarse-graining.

### Required source objects

* `GRC9-ROW-COLUMN-CHART`

The existing GRC-9 paper treats rows as local directional structure and columns as stable boundary/interface families.

### Boundary

Do not claim that continuum RC contains nine primitive directions. The chart is a discrete specialization.

---

### A.4 GRC9 row-basis differential backend

Present the exact fixed row-basis gradient, Hessian, and flux-summary backend used by the GRC9 specialization.

### Required source objects

* `BASE-GRC9-ROW-BASIS-DIFFERENTIAL`

### Boundary

Do not promote this backend into the graph-generic main text.

---

### A.5 Saturation and mechanical expansion

Extract:

* nine-port saturation;
* mechanical refinement trigger;
* column-preserving boundary reassignment;
* resource transfer;
* internal module construction;
* typed topology-event lifecycle.

### Required source objects

* `GRC9-SATURATION`
* `GRC9-MECHANICAL-EXPANSION`

### Boundary

Generic graph topology change is not identical to GRC9 mechanical expansion.

---

### A.6 Hybrid spark completion and child basins

Present the accepted GRC9 hybrid sequence:

```text
nine-port saturation
    + basin-interior degeneracy
    -> mechanical expansion
    -> post-event reflexive evolution
    -> completed spark only if child-basin/attractor gain is established
```

### Required source objects

* `GRC9-HYBRID-SPARK`
* `GRC9-CHILD-BASIN-STABILIZATION`

The existing GRC-9 paper already separates the refinement event from the later emergence of child identities.

---

### A.7 Column coarse-graining

Present the exact GRC9 column coarse-graining and split/reconstruction contract.

### Required source objects

* `GRC9-COLUMN-COARSE-GRAINING`

Do not generalize ordinary graph coarsening into this chart-specific operation.

---

### A.8 Exact GRC9V3 Candidate A initializer binding

Present the exact GRC9V3 base-conductance reconstruction as the specialization binding of the graph-generic Candidate A initializer role.

### Required source objects

* `L-A-INITIALIZER-GRC9V3`

---

### A.9 Disabled-profile matrix

Include the full:

$$
10\ \text{profiles}
\times
4\ \text{reduction surfaces} =
40\ \text{contracts}.
$$

For every current profile list:

* transition reduction;
* state reduction;
* observable reduction;
* lifecycle reduction.

Do not summarize this as one generic “backward compatible” claim.

---

### A.10 GRC9V4 claim boundary

State:

* GRC9V4 is substantive;
* nine ports are not promoted into generic GRC-v4;
* the paper does not prove that nine is uniquely necessary;
* exact GRC9V3 compatibility is deliberate specialization content;
* future GRC9 profiles reopen both generic and specialization provenance where affected.

---

## Appendix B. Normative Notation and Type Table

Include one table covering:

* graph spaces;
* resource coordinates;
* current coordinates;
* retained coordinates;
* selected/physical one-form spaces;
* $K_4$;
* $H_0$;
* $H_{1,\mathrm{form}}$;
* $G_J$;
* $h_4$;
* $M_4$;
* profile history state;
* lifecycle tuple;
* analysis-only operators.

Every row should include:

```text
symbol
space/type
authority class
writer
reader
serialization status
profile scope
source object
```

---

## Appendix C. Complete Profile Registry

Provide one row for each of:

* A-CI
* C-CI
* A-OS
* C-OS
* A-RG2b
* C-RG2b
* A-PC
* C-PC
* A-CI+PC
* C-CI+PC

Each row should record:

```text
authoritative state
constitutive Read-Back
current closure
geometry source
realization order
history state
writer
release
domain
solver/root rule
failure rule
disabled surfaces
claim ceiling
```

This appendix should be generated by extraction from the D9 registry and accepted realization records, not manually reconstructed.

---

## Appendix D. Exact Candidate and Realization Equations

Move long root, contraction, selector, Hodge, OS residual, RG section, PC writer, and CI+PC composition equations here if including all of them in the main text would obscure the substrate architecture.

The main text must still state every causal role and authority relation.

---

## Appendix E. Lifecycle and Event Contract Tables

Include:

* snapshot identity;
* reset identity;
* profile migration maps;
* topology-event maps;
* resource transport;
* event resource increments;
* charge receipts;
* history transport/reset/archive;
* target initializer;
* target readmission;
* failure atomicity;
* ordered source/target receipt schema.

---

## Appendix F. Analysis Interfaces and Nonclaims

Collect:

* structural operator surfaces;
* temporal derivative/Jacobian surfaces;
* Read-Back derivative surfaces;
* spatial graph operator surfaces;
* required metrics;
* required regularity;
* branch assumptions;
* current uninstantiated evidence obligations.

This appendix must not print numerical spectra that the investigation has not instantiated.

---

## Appendix G. Paper-to-Investigation Provenance Crosswalk

For every main-text proposition and equation record:

```text
paper section
paper statement/equation
D10 claim IDs
D10.2 parent object IDs
D10.2 equation/contract IDs
accepted predecessor decisions
paper claim ceiling
```

This appendix may remain a repository-side companion rather than part of the published prose, but it should be generated and preserved before the paper is frozen.

---

# Initial Paper-Pressure Boundary Register

This table identifies known places where ordinary scholarly phrasing could accidentally cross the accepted investigation boundary.

| Tempting paper claim                                                       | Boundary crossed                          | Current paper treatment                                                             |
| -------------------------------------------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------------------- |
| “V4 retention produces a nonzero committed downstream effect.”             | `D10-CL-C-004`, `D10-CL-U-002`            | Do not claim; state complete-chain endpoint evidence is unexecuted.                 |
| “The retained branch is structurally or temporally stable.”                | `D10-CL-C-001`, `C-005`, `U-004`, `X-003` | Do not claim; describe only operator and analysis interfaces.                       |
| “A and C are physically distinct, nonabsorbable mechanisms.”               | `D10-CL-C-007`, `U-003`                   | State that both are admitted profiles; physical nonabsorbability remains open.      |
| “One candidate or realization is preferable.”                              | `D10-CL-C-008`, `X-002`                   | No ranking; list profiles symmetrically.                                            |
| “Candidate A has a physical dimensional interpretation comparable with C.” | `D10-CL-C-010`, `U-004`                   | State normalized nondimensional profile only.                                       |
| “History is preserved losslessly across arbitrary topology change.”        | `D10-CL-C-002`, `X-001`                   | Require typed lineage or explicit loss/reset/archive.                               |
| “The regular A/C equations continue through singular current states.”      | `D10-CL-C-003`                            | State fail-closed regular domain; singular continuation needs a successor.          |
| “The ten profiles exhaust GRC-v4.”                                         | `D10-CL-C-012`                            | Call them the current initial admitted population.                                  |
| “PC supplies Candidate B.”                                                 | `D10-CL-U-001`, `X-005`                   | Keep B reserved and nonexecutable.                                                  |
| “The reference Hodge normalization is uniquely determined.”                | `D10-CL-U-005`, `C-010`                   | Present it as the accepted reference profile.                                       |
| “General covariance and SPD solvers are implemented.”                      | `D10-CL-C-006`                            | Define the contract; state implementation verification is pending.                  |
| “GRC9V4 proves nine ports are necessary.”                                  | GRC9 specialization claim ceiling         | State nine-port mechanics as a substantive specialization, not a necessity theorem. |

### Initial disposition

None of these boundaries automatically blocks a design-level substrate paper. They become a successor-investigation trigger only where the intended paper cannot describe the accepted substrate coherently without asserting the stronger proposition.

---

# Drafting Order

The paper should be drafted in dependency order:

```text
1. Sections 2–4:
   inheritance, typed setting, resource and charge contract

2. Sections 5–7:
   causal loop, structural geometry, profile grammar

3. Sections 8–10:
   A, C, and realization families

4. Sections 11–12:
   complete step and lifecycle

5. Sections 13–15:
   analysis interfaces, factorization, claim ceiling

6. Appendix A:
   GRC9V4 specialization

7. Technical appendices and provenance crosswalk

8. Introduction and abstract last
```

Writing the abstract last prevents it from making claims that the extracted body does not support.

---

# Completion Condition for the Skeleton

The paper extraction is complete when:

```text
every load-bearing paper equation has a source row
every authority statement has a source object
every profile statement preserves complete-profile identity
every limitation maps to an accepted conditional, open, or negative claim
no GRC9-intrinsic object appears in the graph-generic main contract
no paper-side equation or assumption has been introduced
every exposed unsupported proposition is recorded as a paper boundary
```

At that point there are only two lawful outcomes:

```text
no blocking paper boundary
    -> proceed from skeleton to substrate-paper prose

specific blocking paper boundary
    -> open the next investigation exactly at that boundary
       and return to the paper only after acceptance
```
