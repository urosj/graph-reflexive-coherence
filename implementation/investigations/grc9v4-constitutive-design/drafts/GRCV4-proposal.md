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

D10.2 currently supplies the control population of 39 accepted claims, 67 parent normative objects, and 152 normative equation/contract rows: 67 parent-atomic contracts plus 85 explicit equation/contract rows. The 40 profile-scoped disabled-reduction rows form one scope category within that 152-row population. The paper need not print all of them, but it must not contain load-bearing mathematics outside them.

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

### Sections 2–4 tranche status

**Status:** Working synthesis from the accepted GRC-v4/GRC9V4 constitutive-design investigation.

**Scientific authority:** None independent of the accepted investigation.

**Current controlling closure:** Accepted D10.2, decision digest `28343064e85065b7f18227cf429e8cd8f33b414d7a19d5f3e9090a318adcb32c`.

The tranche reorganizes accepted results for exposition; it does not derive a second GRC-v4, modify an accepted equation, promote an unresolved claim, or authorize implementation. Claim associations in the crosswalk preserve the explorer disposition `indeterminate_requires_review`; they are provenance references rather than reconstructed support proof.

### Coverage and status corrections applied in this tranche

A literal parent-object coverage pass over the extraction skeleton found four D10.2 parent identifiers without an extraction slot. This tranche closes those drafting gaps as follows:

| Previously absent parent object | New extraction location | Treatment |
|---|---|---|
| `BASE-SCALAR-MOBILITY` | §4.1 | Positive scalar edge-mobility input of the inherited baseline transport channel |
| `BASE-POTENTIAL` | §4.1 | Graph-generic potential equation |
| `BASE-POTENTIAL-FLOW` | §4.1 | Oriented potential-flow equation and its separation from retained/total current |
| `SPEC-VERIFICATION-REGISTRY` | §2.5 | Separation of scientific claim topology from runtime, numerical, and implementation verification |

When these insertions are merged into the controlling skeleton, all 67 D10.2 parent normative objects are present by identifier.

One claim-status correction is also made explicit. The D10 preclosure condition `D10-CL-C-011` is not carried forward as an unresolved generic-substrate question. Accepted D10.2 records that it is succeeded by `D10_2_CL_N_001`, which earns, for the current D10 initial population, the bounded factorization

$$
\mathrm{GRCV4}
\longrightarrow
\mathrm{GRC9V4}
\longrightarrow
\mathrm{GRC9V3}.
$$

The bounded-completeness claim `D10-CL-C-012` remains unchanged: the current ten profiles are complete for the initial admitted population, not exhaustive over every lawful future GRC-v4 profile.

### Sections 2–4 provenance crosswalk

The table below is a drafting-control surface. It does not replace the D10.2 registry.

| Proposal location | Parent object(s) | Equation/contract row(s) | Current claim relation |
|---|---|---|---|
| §2.1.1, §3.1, §3.3 | `CORE-C-AUTHORITY` | `D10.2-EC-PARENT-CORE-C-AUTHORITY` | `D10-CL-N-001`, `D10-CL-N-002`; bounded generic promotion by `D10_2_CL_N_001` |
| §2.1.2, §3.4 | `BASE-GRC-DIFFERENTIAL` | `D10.2-EC-PARENT-BASE-GRC-DIFFERENTIAL` | `D10-CL-N-001`; graph-generic promotion accepted |
| §4.1.1 | `BASE-SCALAR-MOBILITY` | `D10.2-EC-PARENT-BASE-SCALAR-MOBILITY` | `D10-CL-N-001`; predecessor `D10-CL-C-011` succeeded by `D10_2_CL_N_001` |
| §4.1.2 | `BASE-POTENTIAL` | `D10.2-EC-PARENT-BASE-POTENTIAL` | same |
| §4.1.3 | `BASE-POTENTIAL-FLOW` | `D10.2-EC-PARENT-BASE-POTENTIAL-FLOW` | same |
| §3.1 (graph-generic geometry typing) | `CORE-K-STRUCTURAL-ROLE`, `GEOM-K4`, `GEOM-H1-FORM`, `GEOM-GJ`, `GEOM-M4`, `GEOM-COVARIANCE` | corresponding parent rows; detailed equations deferred to the structural-geometry section | `D10-CL-N-006`; reference-Hodge uniqueness remains bounded by `D10-CL-U-005` |
| §3.1 (Candidate C typing example), §9.4 | `C-HODGE-MAPS` | `D10.2-EC-PARENT-C-HODGE-MAPS` | Candidate C only: `D10-CL-N-002`, `D10-CL-O-002`, `D10-CL-C-006`; predecessor `D10-CL-C-011`; negative boundary `D10-CL-X-006` |
| §3.2 | `L-PROFILE-GRAMMAR`, `SPEC-PROFILE-GRAMMAR`, `SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER`, `SPEC-COMPOSITION-PROFILE-IDENTITY` | corresponding parent rows | `D10-CL-N-008`, `D10-CL-N-009`, `D10-CL-C-012` |
| §3.3 | `A-STATE-REDUCTION`, `C-AUTHORITY`, `REAL-PC`, `L-SNAPSHOT-RESET` | corresponding parent rows and D9 registry | `D10-CL-N-002`, optional A/C/PC claims, lifecycle claim `D10-CL-N-005` |
| §2.5 | `SPEC-VERIFICATION-REGISTRY` | `D10.2-EC-PARENT-SPEC-VERIFICATION-REGISTRY` | keeps conditional/open/negative claims and named verification obligations distinct from accepted substrate mathematics |
| §4.2 | `CORE-INCIDENCE-CONTINUITY`, `L-AUTHORITATIVE-CURRENT`, `L-CONTINUITY-WRITE` | corresponding parent rows | `D10-CL-N-003`, `D10-CL-N-004` |
| §4.3 | `CORE-GENERAL-CHARGE`, `CORE-UNIT-MEASURE` | corresponding parent rows | `D10-CL-N-004` |
| §4.4 | `CORE-CHARGE-TANGENT` | `D10.2-EC-CHARGE-DQ`, `D10.2-EC-CHARGE-TANGENT` | `D10-CL-N-004` |
| §4.5 | `CORE-STRUCTURAL-CHARGE-PROJECTOR` | `D10.2-EC-CHARGE-C-SECTOR-PROJECTOR`, `D10.2-EC-CHARGE-FULL-TANGENT-RETRACTION` | `D10-CL-N-004`; full product metric remains bounded |
| §4.6 | `CORE-GENERAL-CHARGE`, `L-CONTINUITY-WRITE`, `L-TOPOLOGY-EVENT` | `D10.2-EC-CHARGE-BUDGET-STAGE` | `D10-CL-N-004` |
| §4.7 | `L-TOPOLOGY-EVENT` | `D10.2-EC-EVENT-RESOURCE` | `D10-CL-N-004`, `D10-CL-N-005`, `D10-CL-X-001` |
| §2.4, §3.4 | `BASE-GRC9-ROW-BASIS-DIFFERENTIAL` and GRC9-intrinsic objects | specialization parent rows | specialization only; not graph-generic GRC-v4 |

`CORE-EXTERNAL-EVENT-CHARGE` and `L-ORDERED-RECEIPTS` are related objects discussed in §4.7; they are not direct parents of `D10.2-EC-EVENT-RESOURCE`.

### Paper-pressure register after Sections 2–4

| Boundary | Current disposition | Does it block this tranche? | Successor trigger condition |
|---|---|---|---|
| Mapping the inherited potential-flow output into the candidate-stage name $J_0$ | Notational/staging crosswalk; the equation itself is unchanged | No | Only if a later section needs one universal $J_0$ authority rule not supplied by complete profiles |
| Full tensor anisotropic mobility | Explicitly outside `BASE-SCALAR-MOBILITY` | No | Only if the intended V4 account claims tensor transport as common current-population content |
| Full-state orthogonal charge projector | Product analysis metric not frozen | No | Only if later structural/spectral claims require orthogonality on the complete state rather than the accepted tangent retraction |
| General nonidentity Hodge conditioning and executable covariance | Routed to implementation-level verification under `D10-CL-C-006` | No | Only if proposal prose attempts an executed numerical/runtime claim |
| Nontrivial ordinary-step budget projection | Not part of current bounded profiles | No | Only if a new profile requires such a projection as part of its accepted transition |
| Generic lossless event-history preservation | Negatively bounded without sufficient lineage | No | Only if a later lifecycle section requires lossless continuation for an event lacking the required typed lineage |
| Generic-substrate promotion | Closed bounded by accepted D10.2 successor `D10_2_CL_N_001` | No | Reopen only for a materially distinct future profile outside the audited population |
| Future-exhaustive profile taxonomy | Not established; `D10-CL-C-012` remains the ceiling | No | Only if the proposal attempts to claim that the ten current profiles exhaust all lawful GRC-v4 constructions |

**Current disposition:** Sections 2–4 are fillable from the accepted investigation. They expose no new scientific contradiction and require no successor investigation.

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

GRC-v4 does not discard the graph substrate inherited from GRC-v3. It retains the finite graph, scalar resource, graph-local differential construction, positive edge transport, potential and oriented flow, continuity, charge accounting, identity semantics, and topology-aware lifecycle. Its revision-specific work is to make causal roles that were previously compressed into one graph update explicit and separately typed.

The central change is therefore not a replacement of graph dynamics by a new state space. It is a reorganization of the graph dynamics into a complete profile-explicit loop in which retained causal structure, Read-Back, generated structural geometry, authoritative current, continuity, and write-back have declared owners and stages.

The accepted architecture has the form

$$
\boxed{
\text{common GRC-v4 contract}
+
\text{constitutive family}
+
\text{geometry-temporal realization}
}.
$$

The common contract fixes the resource ledger, type boundaries, lifecycle grammar, and conditions under which a profile is admissible. A complete profile supplies the constitutive and realization-specific maps. The common layer is therefore neither an empty interface nor a universal candidate equation.

> **Control lineage:** `D10-CL-N-001` through `D10-CL-N-009`; accepted successor `D10_2_CL_N_001`; D10.2 parent and equation/contract registry.
>
> **Provenance note:** Claim and parent-object associations below retain the explorer disposition `indeterminate_requires_review`. They are crosswalk references, not reconstructed proof or an independent change in claim status.

### 2.1 What remains fixed

#### 2.1.1 Finite graph and resource authority

The substrate remains a finite graph with a declared orientation convention. Its unique resource coordinate is the scalar vertex field $C$. Other state may be authoritative for a particular profile, but it is nonresource state and cannot silently alter the resource ledger.

This preserves the accepted distinction between:

- resource authority;
- nonresource causal authority;
- derived causal surfaces;
- same-beat solver work;
- analysis-only objects.

The common resource statement is represented by `CORE-C-AUTHORITY`. Candidate A, Candidate C, and the persistent-carrier realizations differ in their admitted nonresource authority, but none introduces a second resource coordinate.

#### 2.1.2 Graph-local differential and baseline transport inheritance

GRC-v4 retains a graph-generic differential backend contract and the inherited scalar-mobility potential-flow channel. The backend must be explicit, deterministic, reproducible from serialized identity, and clear about frame, orientation, regularization, freshness, and covariance. The current canonical reference is the admitted GRC-v3 induced-frame and weighted-least-squares backend, represented by `BASE-GRC-DIFFERENTIAL`.

The inherited baseline transport consists of:

- a positive scalar edge-mobility field, `BASE-SCALAR-MOBILITY`;
- the graph potential equation, `BASE-POTENTIAL`;
- the oriented potential-flow equation, `BASE-POTENTIAL-FLOW`.

These equations are written explicitly in §4.1. Their promotion to GRC-v4 is graph-generic: no ordered-port or fixed $3\times3$ chart premise enters them. Their presence does not imply that scalar mobility already represents full tensor anisotropy, that a baseline potential flow contains retained Read-Back, or that GRC9 storage conventions have been promoted with the equations.

#### 2.1.3 One current ledger and one ordinary resource write

Every complete profile produces one authoritative current $J_C$ for the ordinary resource transition. Continuity is applied once. Candidate writers, geometry writers, carrier writers, diagnostics, and analysis operations cannot perform a second hidden update of $C$.

The baseline potential-flow result may be one input to the profile’s current closure. It is not automatically identical to the final authoritative current once a constitutive Read-Back or geometry-temporal realization is enabled.

#### 2.1.4 Charge from the actual resource path

Charge remains a functional of the authoritative resource coordinate. It is checked after the actual continuity write, not inherited by model name and not repaired after a downstream writer has already consumed a different resource state. External exchange and topology events must be typed and receipted.

The current initial population uses the closed-internal unit-measure profile for ordinary beats. The common GRC-v4 contract nevertheless preserves the accepted general charge covector form, so the unit profile is a reference specialization rather than the only lawful future measure.

#### 2.1.5 Identity, topology, and conservation remain substrate concerns

Snapshot, reset, profile migration, topology events, target readmission, information-loss receipts, and charge-target transformation remain part of the substrate contract. They are not deferred to an untyped driver layer.

A representation change that only relabels nodes or reverses coordinate orientations must transform typed objects covariantly without changing scientific identity. A physical reversal, resource event, profile change, or history loss is a different operation and requires its own contract.

#### 2.1.6 No hidden causal authority

A producer, observer, scheduler, prior root, retry trace, cache, random-number generator, analysis projector, or continuation token cannot become scientific state unless a complete profile explicitly declares and serializes that authority. Reproducible computation is required, but reproducibility machinery does not thereby become physics.

### 2.2 What changes in V4

#### 2.2.1 Retention, Read-Back, and write-back become distinct

GRC-v4 no longer permits the words *retention*, *Read-Back*, and *write-back* to name the same undifferentiated historical effect.

- **Retention** identifies what persists and under which writer, release, reset, and capacity/domain contract.
- **Read-Back** identifies how retained causal structure conditions present activity into a current contribution.
- **Write-back** identifies how the consequences of the present beat alter the retained structure available to later beats.

A slow parameter does not by itself prove retention. A diagnostic dependence does not by itself prove Read-Back. A post-step recomputation does not by itself prove that an independent history coordinate was written.

#### 2.2.2 Complete-profile identity becomes mandatory

Every executable state, reset baseline, and snapshot binds exactly one admitted constitutive family and one admitted realization. The current initial population is

$$
\{\mathrm A,\mathrm C\}
\times
\{\mathrm{CI},\mathrm{OS},\mathrm{RG2b},\mathrm{PC},\mathrm{CI+PC}\}.
$$

This product names ten complete profile identities. It does not assert that the two axes are exhaustive beyond the current initial population, nor does it rank their members.

#### 2.2.3 Authority classes are explicit

Each profile must distinguish authoritative state from derived and transient surfaces. In particular:

- Candidate A makes $W_A$ authoritative nonresource state;
- Candidate C writes only $C$ and rederives its selected sector and Hodge response;
- PC and CI+PC add their declared persistent $K_4$ carrier state;
- current, geometry, selectors, solver roots, and analytical objects remain derived or transient unless an accepted profile says otherwise.

#### 2.2.4 Structural and transport objects are separately typed

The accepted Hodge correction separates:

- $H_{1,\mathrm{form}}$, the structural one-form Hodge/Gram operator;
- $G_J$, the physical-flux resistance and flat/sharp map;
- $M_4$, candidate-specific transport mobility;
- $K_4$, the graph structural bilinear object;
- $h_4$, the generated geometry state/profile output.

Equal coordinate dimensions or equal numerical diagonal entries do not merge these objects or transfer authority among them.

#### 2.2.5 One complete-step order governs the transaction

A profile must declare its candidate- and realization-specific internal substages, but every admitted complete step respects the common outer obligations:

```text
validate complete identity and domain
-> derive/solve without commit
-> produce one authoritative current
-> write C once through continuity
-> validate charge and resource domain
-> refresh final-C-derived surfaces
-> execute candidate/history writers
-> verify postconditions
-> commit all authoritative coordinates atomically, or commit nothing
```

#### 2.2.6 Lifecycle identity expands beyond current arrays

Scientific lifecycle identity contains current authoritative state, reset baseline, $Q_{\mathrm{target}}$, graph identity, context-contract identity, complete-profile identity, and every declared serialized scientific coordinate. An event or migration must transform the whole lifecycle tuple rather than only the currently visible arrays.

### 2.3 What remains profile-dependent

The common architecture does not supply one universal formula for every causal role. A complete profile must declare:

- authoritative nonresource state;
- retained causal representation;
- Read-Back map;
- constitutive current closure;
- structural source;
- geometry-temporal realization;
- write-back and release laws;
- parameters and units;
- gauge and normalization;
- admissible domain;
- solver and root-selection rule;
- stage order;
- composition law and gains;
- failure disposition;
- lifecycle and event maps;
- disabled transition, state, observable, and lifecycle reductions.

This profile dependence is intentional. It preserves the distinct accepted ontologies of A and C and the distinct timing/history semantics of CI, OS, RG2b, PC, and CI+PC. Candidate neutrality means symmetric evidentiary burden, not identical equations.

The shorthand profile symbol introduced below bundles all of these identity-bearing choices; it is not merely a pair of labels plus a freely editable parameter dictionary.

### 2.4 What remains GRC9 specialization-dependent

The following objects are not part of graph-generic GRC-v4:

- `GRC9-ORDERED-PORTS`;
- `GRC9-ROW-COLUMN-CHART`;
- `BASE-GRC9-ROW-BASIS-DIFFERENTIAL`;
- `GRC9-SATURATION`;
- `GRC9-MECHANICAL-EXPANSION`;
- `GRC9-HYBRID-SPARK`;
- `GRC9-CHILD-BASIN-STABILIZATION`;
- `GRC9-COLUMN-COARSE-GRAINING`;
- `L-A-INITIALIZER-GRC9V3`;
- the exact profile-scoped GRC9V3 reduction surfaces.

GRC9V4 is therefore a substantive specialization, not an alias and not only a compatibility wrapper. Conversely, the successful promotion of the common V4 contract does not establish that nine ports are unnecessary or that every future V4 profile will be graph-generic under the same derivation.

The accepted bounded relation is

$$
\mathrm{GRCV4}
\xrightarrow{\text{nine-port specialization}}
\mathrm{GRC9V4}
\xrightarrow{\text{disabled V4 profile}}
\mathrm{GRC9V3}.
$$

This is the current status after D10.2. The earlier conditional substrate-provenance question in `D10-CL-C-011` has been succeeded by accepted `D10_2_CL_N_001` and must not be presented as still unresolved.

### 2.5 Scientific claims and verification obligations

The proposal must preserve the evidence boundary represented by `SPEC-VERIFICATION-REGISTRY`:

> Runtime, numerical, and implementation verification obligations remain separate from the scientific claim topology.

This separation works in both directions.

First, an accepted design-level equation or contract is not invalid merely because its runtime implementation, numerical conditioning, formed-branch reachability, or matched discrimination has not yet been executed. Those obligations are routed to named verification surfaces rather than misclassified as missing constitutive mathematics.

Second, design-level acceptance cannot be used as evidence that the routed runtime or numerical claim has passed. In particular, the present proposal does not establish:

- formed runtime formation, retention, release, or replay;
- a nonzero committed endpoint effect;
- general nonidentity SPD conditioning or executable covariance;
- structural or temporal stability;
- a continuation spectrum on a formed branch;
- physical nonabsorbability of A or C;
- matched profile ranking;
- physical dimensionalization and cross-profile comparison.

D10 organizes current propositions into normative, optional, conditional, open, and negative claims. Conditional and open claims are not an automatic sequence of future gates. A successor investigation is justified only when the content needed for the intended GRC-v4 account reaches one of those boundaries and cannot continue without asserting the stronger proposition.

The accepted D10.2 promotion result is a specific exception to the older conditional status of the substrate-identity question: `D10-CL-C-011` has a named accepted successor. The current-population ceiling in `D10-CL-C-012` is not similarly removed and must remain visible.

The exploratory side tool may verify that these status relations and lineage edges have been preserved. It may not decide that an unexecuted verification obligation has passed, fabricate a rerun result, or generate a new claim.

#### Section 2 boundary disposition

No successor investigation is required by this roadmap. The section can be completed from accepted material provided that it preserves:

- the graph-generic/GRC9 specialization boundary;
- the current-population ceiling;
- the separation between scientific closure and routed verification;
- the nonranking of candidates and realizations.

---

## 3. Mathematical Setting and Authority

### 3.1 Finite oriented graph and typed edge spaces

Let

$$
\mathcal G=(V,E)
$$

be a finite graph. Choose one coordinate orientation for each live edge. This choice provides an oriented incidence operator

$$
B:\mathbb R^{E}\longrightarrow\mathbb R^{V},
$$

with transpose

$$
B^\top:\mathbb R^{V}\longrightarrow\mathbb R^{E}.
$$

The transpose acts as the graph scalar-to-edge differential in the inherited potential-flow construction, while $B$ returns the signed edge flux to the vertex divergence used by continuity. Reversing the coordinate orientation of an edge changes the corresponding edge coordinates and operator columns by the declared signed cochain transformation. It does not by itself reverse the physical history of the system.

The authoritative resource is

$$
C\in\mathbb R^{V}.
$$

A physical current or flux is represented in an oriented edge-flux space,

$$
J_{\mathrm{flux}}\in\mathbb R^{E}_{\mathrm{flux}}.
$$

A structural one-form is represented in a separately typed edge-form space,

$$
j_{\mathrm{struct}}^{\flat}
\in
\mathbb R^{E}_{\mathrm{form}}.
$$

The two edge spaces have the same coordinate dimension on a fixed graph, but they are not the same typed object. The accepted Hodge correction assigns the following roles:

$$
H_{1,\mathrm{form}}:
\mathbb R^{E}_{\mathrm{form}}
\longrightarrow
\left(\mathbb R^{E}_{\mathrm{form}}\right)^*,
$$

as the positive structural one-form Hodge/Gram operator, and

$$
G_J:
\mathbb R^{E}_{\mathrm{flux}}
\longrightarrow
\mathbb R^{E}_{\mathrm{form}},
$$

as the physical-flux resistance/flat map. Its inverse, when admitted, sharpens a structural one-form back to physical-flux coordinates. The transport mobility $M_4$ is a third object with candidate-specific authority; it is not identified with either $H_{1,\mathrm{form}}$ or $G_J$.

At vertex level, a positive $H_0$ provides the admitted vertex Hodge/Gram structure. The current reference embedding later used by the structural geometry construction has

$$
H_{0,\mathrm{ref}}=\operatorname{diag}(\mu),
$$

for a declared positive graph measure $\mu$, but the full $K_4\rightarrow H_4\rightarrow h_4$ construction belongs to the later structural-geometry section.

A declared charge covector

$$
\varpi\in(\mathbb R^{V})^*
$$

specifies the resource functional. The current initial population uses the unit-measure specialization $\varpi=\mathbf 1$ for ordinary beats. The general covector notation is retained because topology events may change graph dimension and because GRC-v4 does not declare the unit profile to be the only lawful future charge convention.

Graph identity also includes the declared boundary class, orientation convention, stable node/edge identity, and the context contract under which differential and constitutive surfaces are interpreted. A change of coordinate representation is handled covariantly. A change of graph, boundary semantics, context schema, or profile semantics requires a typed event or migration.

#### Type-control summary

| Object | Accepted role | Not the same as |
|---|---|---|
| $C$ | authoritative scalar resource on vertices | derived sector, current, geometry, or analysis state |
| $J_{\mathrm{flux}}$ | physical oriented current consumed by continuity | structural one-form merely because coordinates have the same length |
| $j_{\mathrm{struct}}^{\flat}$ | lowered one-form consumed by structural rank-one maps | physical flux before an admitted sharp map |
| $H_0$ | positive vertex Hodge/Gram object | charge projector or complete-state product metric |
| $H_{1,\mathrm{form}}$ | positive structural one-form Hodge/Gram object | transport mobility $M_4$ or flux resistance $G_J$ |
| $G_J$ | flux-to-form resistance/flat map | candidate transport mobility |
| $M_4$ | candidate-specific transport mobility | overlap-normalized $K_4$ assembly or Hodge geometry |

> **Core source objects:** `CORE-C-AUTHORITY`, `CORE-INCIDENCE-CONTINUITY`.
>
> **Graph-generic geometry source objects:** `CORE-K-STRUCTURAL-ROLE`, `GEOM-K4`, `GEOM-H1-FORM`, `GEOM-GJ`, `GEOM-M4`, `GEOM-COVARIANCE`; associated accepted claim `D10-CL-N-006`.
>
> **Candidate C typing example:** `C-HODGE-MAPS`; associated claims `D10-CL-N-002`, `D10-CL-O-002`, and `D10-CL-C-006`. This profile-scoped object illustrates the shared flux/form distinction but does not supply graph-generic geometry authority.

#### Boundary

This section fixes types and covariance obligations. It does not claim that general nonidentity Hodge conditioning, inverse solvers, or executable covariance have already been verified. Those remain under `D10-CL-C-006` and the corresponding verification registry.

### 3.2 Complete profile identity

A complete executable profile is not only a constitutive-family label. It binds the complete set of choices that determine authority, equations, stage order, and lifecycle semantics.

For exposition, write

$$
p=(a,r,\Theta_p),
$$

where:

- $a\in\{\mathrm A,\mathrm C\}$ is the currently admitted constitutive family;
- $r\in\{\mathrm{CI},\mathrm{OS},\mathrm{RG2b},\mathrm{PC},\mathrm{CI+PC}\}$ is the currently admitted realization;
- $\Theta_p$ denotes the rest of the accepted complete-profile identity, not merely freely editable numerical parameters.

The bundle $\Theta_p$ includes, where applicable:

```text
graph and orientation identity
boundary and context-contract identity
quadrature/charge profile
constitutive current-law identity
Read-Back identity
K4 base and structural-source identity
H_profile identity
mobility factorization
candidate writer and release identity
realization stage order
history/carrier identity
normalization, units, and gauge
admission domain
solver and root-selection rule
composition law and gains
capability set
Q_target lifecycle rule
disabled transition/state/observable/lifecycle surfaces
```

Candidate- and realization-specific additions are also part of profile identity. Examples include Candidate A’s $W_A$ type, floor, units, writer, and reset semantics; Candidate C’s selector rank/gap rule and Hodge identification; OS’s predictor/geometry/corrector order and residual; RG2b’s frozen equivariant extension; PC’s carrier domain and $\tau_{\mathrm{PC}}$; and CI+PC’s composition gain and composite domain.

The current initial population contains ten profile identities. An implementation may support a nonempty subset, but every executable state it does support must bind exactly one admitted constitutive family and one admitted realization. There is no ambiguous “auto” profile that selects an equation from hidden runtime context.

A change in a load-bearing profile field is a semantic change, not an in-place parameter edit. It requires a typed migration, target readmission, and the appropriate history or information-loss receipt. A mere change in the current value of an already-declared per-beat input does not change profile identity; a change in the input schema, units, representation semantics, or admissibility rule does.

The profile grammar is substrate-independent specification metadata. It governs which physical equations are selected but is not itself physical evidence for any candidate or realization.

> **Source objects:** `L-PROFILE-GRAMMAR`, `SPEC-PROFILE-GRAMMAR`, `SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER`, `SPEC-COMPOSITION-PROFILE-IDENTITY`.

> **Claim status:** `D10-CL-N-008`, `D10-CL-N-009`, and bounded-current-population condition `D10-CL-C-012`.

### 3.3 State authority classes

GRC-v4 uses profile-scoped state rather than one universal tuple containing every optional surface. For any complete profile, the scientific record distinguishes at least six classes.

#### 3.3.1 Authoritative resource state

The sole resource coordinate is $C$. Its ordinary update is the one continuity write. No candidate, geometry, carrier, or analysis operation receives an independent resource ledger.

#### 3.3.2 Authoritative nonresource state

Authoritative nonresource state is profile-dependent. For the current population:

| Complete-profile class | Authoritative state |
|---|---|
| A-CI, A-OS, A-RG2b | $(C,W_A)$ |
| C-CI, C-OS, C-RG2b | $(C)$ |
| A-PC, A-CI+PC | $(C,W_A,Z_{4,A})$ |
| C-PC, C-CI+PC | $(C,Z_{4,C})$ |

Here $W_A>0$ is Candidate A’s retained edge-mobility state. $Z_{4,A}$ and $Z_{4,C}$ are the separately declared persistent $K_4$ carrier states of PC and CI+PC. Candidate C does not add an independently written $T_C$, selector, or Hodge state.

The table records the current admitted profile identities only. It is not a universal theorem that all future persistent realizations must use one scalar-ZOH $Z_4$ carrier.

#### 3.3.3 Derived causal surfaces

Derived causal surfaces are reconstructed from authoritative state, profile identity, graph, and current context. They may be load-bearing in the transition without becoming independently serialized state.

Examples include:

- Candidate A’s $\widehat W_A$, $q_A$, writer target, differential summaries, current, $K_4$, and geometry;
- Candidate C’s $T_C$, selector, selected Hodge package, resolvent, identification maps, current, $K_4$, and geometry;
- the geometry and current surfaces reconstructed from the old PC carrier;
- post-continuity surfaces rebuilt for a writer or target readmission.

Derived does not mean observationally irrelevant. It means that the surface has no independent writer and must be rederived from its declared authorities.

#### 3.3.4 Same-beat transient solver surfaces

Same-beat solver work may affect whether the transaction succeeds without surviving as scientific state. This class includes previous iterates, trial roots, factorization caches, OS predictor/corrector caches, split-residual work arrays, continuation tokens, retry traces, and hidden numerical history.

A solver receipt may be serialized as lifecycle evidence without turning the internal work state into a causal coordinate. CI and CI+PC root selection must follow from the authoritative state, profile, input, and admitted domain, not from a previously cached root.

#### 3.3.5 Serialized lifecycle metadata

Scientific lifecycle identity contains more than dynamic coordinates. It binds:

```text
X_current
X_reset
Q_target
graph identity
orientation and boundary identity
context-contract identity
complete-profile identity
declared serialized scientific state and receipts
```

The lifecycle tuple and its event/migration morphisms are developed later. At this stage the important authority point is that reset state and $Q_{\mathrm{target}}$ are not disposable implementation metadata: they determine lawful restoration and future admission.

#### 3.3.6 Analysis-only objects

Perturbations, analytical projectors, continuation Hessians, Jacobian workspaces, spectra, and mode labels remain analysis-only unless a future accepted profile explicitly changes their status. Mathematical derivability does not confer runtime authority.

In particular, the structural charge projector introduced in §4.5 is an analysis/tangent operation. It does not write the resource state, and its identity extension does not supply a missing full-state analysis metric.

> **Source objects:** `CORE-C-AUTHORITY`, `A-STATE-REDUCTION`, `C-AUTHORITY`, `REAL-PC`, `L-SNAPSHOT-RESET`.

> **Primary registry source:** `D9ProfileStateLifecycleRegistry.json`.

#### Boundary

No universal state tuple should be introduced for convenience. Doing so would either fabricate history for profiles that do not possess it or convert derived surfaces into hidden state.

### 3.4 Differential backend contract

GRC-v4 requires a graph differential backend wherever an admitted profile consumes graph-local gradient, Hessian, or frame information. The common contract is represented by `BASE-GRC-DIFFERENTIAL`.

An admitted backend must declare:

1. the graph, boundary, and neighborhood on which it operates;
2. the local frame or displacement convention;
3. orientation semantics;
4. positive regression or graph weights;
5. regularization and singular-case handling;
6. deterministic ordering and sign choices;
7. the stage at which its inputs are sampled;
8. freshness and cache invalidation rules;
9. covariance under the declared relabeling/reorientation action;
10. the identity needed to reconstruct or serialize the same scientific surface.

The present canonical reference is inherited from GRC-v3. For a node $i$, it constructs a weighted ego graph, obtains a deterministic graph-intrinsic local frame from the ordered nontrivial eigenvectors of its normalized weighted Laplacian, fixes eigenvector signs by a stable rule, and uses the resulting pseudo-displacements in regularized weighted least-squares gradient and Hessian fits.

This reference backend matters for provenance because it demonstrates that the GRC-v4 differential contract does not require the GRC9 fixed row basis. A future complete profile may admit another documented deterministic backend, but it must serialize the backend identity and satisfy the same declared frame, stage, regularity, and covariance obligations.

Differential output remains a derived surface. The backend does not receive authority to alter $C$, choose a profile, preserve hidden history, or carry stale pre-continuity data into a post-continuity writer.

The GRC9 specialization may select `BASE-GRC9-ROW-BASIS-DIFFERENTIAL`; that backend is not promoted into graph-generic GRC-v4.

> **Source objects:** `BASE-GRC-DIFFERENTIAL`; specialization boundary `BASE-GRC9-ROW-BASIS-DIFFERENTIAL`.

#### Section 3 boundary disposition

Sections 3.1–3.4 are supportable from accepted records. They expose two nonblocking boundaries:

- general executable nonidentity Hodge conditioning/covariance remains a verification obligation under `D10-CL-C-006`;
- a complete-state orthogonal analysis projector remains unavailable until a product metric is frozen.

Neither boundary prevents the substrate types, profile identity, or authority classes from being stated. No successor investigation is required here unless a later section attempts the stronger executable or spectral claim.

---

## 4. Resource Dynamics, Inherited Baseline Transport, Charge, and Structural Tangent

### 4.1 Inherited scalar-mobility potential-flow channel

The graph-generic V4 common layer preserves the inherited scalar-mobility potential-flow construction. This construction was present in both GRC-v3 and GRC9V3, but its equations contain no ordered-port premise. D10.2 therefore promotes the equations while leaving GRC9 storage and row/column mechanics in the specialization.

#### 4.1.1 Positive scalar edge mobility

Let $W$ be a positive scalar field on live graph edges:

$$
W_e>0
\qquad
\text{for every live }e\in E.
$$

This is the parent object `BASE-SCALAR-MOBILITY`. It is the scalar mobility input of the inherited baseline transport channel. Its exact authority and source are fixed by the selected complete profile and stage. In one profile it may coincide with authoritative retained mobility; in another it may be a reference or derived transport surface. The common statement does not silently make one $W$ field universal state for every profile.

Scalar positivity also does not make $W$ a full tensorial or channel-anisotropic mobility. A profile that introduces richer transport must declare that additional structure and its authority explicitly.

#### 4.1.2 Graph potential

The accepted graph potential is

$$
\Phi_i
=
\kappa\sum_j W_{ij}(C_i-C_j)
-
V'(C_i).
$$

This is `BASE-POTENTIAL`. The sum is over the graph neighbors represented by the live scalar edge field. The equation depends on the finite graph, scalar mobility, and declared site potential. It does not depend on a nine-port chart.

#### 4.1.3 Oriented potential flow

For the selected coordinate orientation of an edge $e$, the inherited flow equation is

$$
J_e
=
-\eta W_e(B^\top\Phi)_e,
$$

with the opposite orientation carrying $-J_e$. This is `BASE-POTENTIAL-FLOW`.

When a complete profile consumes this output as its immediate pre-Read-Back current, later candidate sections use the accepted stage notation $J_0$. The stage name does not create a second equation: it identifies the baseline output inside the profile’s larger current closure.

The potential-flow equation alone does not establish retained current, Read-Back, generated-geometry feedback, or final current authority. Those enter only through the selected candidate and realization. In particular,

$$
J_{\mathrm{potential\ flow}}
\not\equiv
J_C
$$

as a universal V4 identity. Equality holds only in a profile/stage whose accepted closure makes it so.

#### 4.1.4 Provenance and blocked overreads

The three promoted baseline objects have the following exact boundaries:

| Parent object | Promoted content | Blocked overread |
|---|---|---|
| `BASE-SCALAR-MOBILITY` | positive scalar edge mobility | scalar mobility is not full tensor anisotropy |
| `BASE-POTENTIAL` | graph potential equation | the shared equation does not promote port storage |
| `BASE-POTENTIAL-FLOW` | antisymmetric oriented flow equation | potential flow does not imply retained current |

> **Equation/contract rows:** `D10.2-EC-PARENT-BASE-SCALAR-MOBILITY`, `D10.2-EC-PARENT-BASE-POTENTIAL`, `D10.2-EC-PARENT-BASE-POTENTIAL-FLOW`.

> **Associated accepted claims:** `D10-CL-N-001`; substrate-promotion predecessor `D10-CL-C-011`, succeeded by `D10_2_CL_N_001`.

### 4.2 Authoritative current and continuity

Every complete profile produces exactly one authoritative current $J_C$ for the ordinary resource transition. The profile may obtain it through a direct algebraic closure, a coupled current/geometry root, an operator-split corrector, reconstructed geometry, a persistent carrier, or a hybrid realization. Whatever the internal construction, only the accepted final $J_C$ enters the resource write.

The common continuity equation is

$$
C_{\mathrm{next}}
=
C
-
\Delta t\,B J_C
+
B_{\mathrm{ext}}
+
S_{\mathrm{ext}}.
$$

Here $BJ_C$ is the signed graph divergence under the declared orientation. The external terms are admitted only when typed by the active profile/event contract. The current initial population uses closed-internal ordinary beats,

$$
B_{\mathrm{ext}}=0,
\qquad
S_{\mathrm{ext}}=0,
$$

but D10.2 preserves the general typed form rather than hard-coding the closed-internal specialization as the only future GRC-v4 possibility.

Continuity executes exactly once. After it has produced final $C$:

- resource and charge conditions are checked;
- every writer that consumes final $C$ receives freshly reconstructed post-continuity surfaces;
- Candidate A may update $W_A$;
- PC or CI+PC may update its carrier;
- Candidate C rederives its selected sector and Hodge response;
- the transaction commits all authoritative coordinates together or commits nothing.

No later candidate or carrier writer may alter $C$ again. A read-current contribution affects resource only through its participation in the one authoritative $J_C$; it is not an additional resource transfer.

> **Source objects:** `CORE-INCIDENCE-CONTINUITY`, `L-AUTHORITATIVE-CURRENT`, `L-CONTINUITY-WRITE`.

> **Associated accepted claims:** `D10-CL-N-003`, `D10-CL-N-004`.

### 4.3 General charge and the current unit-measure profile

For a declared charge covector $\varpi$, define

$$
Q_\varpi(C)
=
\varpi^\top C.
$$

This is `CORE-GENERAL-CHARGE`. Because $C$ is the only resource coordinate, nonresource state does not contribute an independent term to $Q_\varpi$.

The current initial profiles use the unit-measure reference

$$
\varpi=\mathbf 1,
$$

so that

$$
Q(C)
=
\sum_i C_i.
$$

This is `CORE-UNIT-MEASURE`. It is the current bounded population’s reference profile, not a theorem that every lawful GRC-v4 graph, topology event, or future quadrature convention must use unit weights.

For a closed-internal ordinary beat on a fixed graph, signed-incidence cancellation of antisymmetric internal edge contributions gives

$$
\sum_i (BJ_C)_i=0,
$$

and therefore the current unit-measure profile preserves $Q$ under the one continuity write. This statement is the accepted current-population specialization. The general charge contract instead requires the declared transport/event map to preserve or explicitly receipt the selected $\varpi$-charge.

> **Source objects:** `CORE-GENERAL-CHARGE`, `CORE-UNIT-MEASURE`, `CORE-C-AUTHORITY`.

### 4.4 Complete-state charge tangent

Let the complete profile state be decomposed only for tangent bookkeeping as

$$
X=(C,X_{\mathrm{nr}}),
$$

where $X_{\mathrm{nr}}$ denotes whatever authoritative nonresource state the selected profile actually possesses. A variation is

$$
\delta X=(\delta C,\delta X_{\mathrm{nr}}).
$$

Because charge depends only on the authoritative resource coordinate,

$$
DQ_\varpi[\delta X]
=
\varpi^\top\delta C.
$$

The complete-state charge tangent is

$$
V_{Q,\varpi}
=
\ker DQ_\varpi
=
\left\{
\delta X:
\varpi^\top\delta C=0
\right\}.
$$

This is `CORE-CHARGE-TANGENT`. Nonresource variations are unrestricted by the charge constraint itself. Candidate, realization, positivity, domain, or analysis-metric contracts may impose additional conditions, but those conditions are not part of $DQ_\varpi$.

The unit-measure profile specializes this to

$$
DQ[\delta X]
=
\mathbf 1^\top\delta C,
\qquad
V_Q
=
\left\{
\delta X:
\sum_i\delta C_i=0
\right\}.
$$

> **Equation/contract rows:** `D10.2-EC-CHARGE-DQ`, `D10.2-EC-CHARGE-TANGENT`.

> **Associated accepted claim:** `D10-CL-N-004`.

### 4.5 Structural $C$-sector projector and complete-tangent retraction

Let $H_0$ be positive on the vertex sector. The accepted $H_0$-orthogonal projector of a resource variation onto the charge-preserving structural $C$ sector is

$$
\Pi_{Q,C,H_0}(\delta C)
=
\delta C
-
H_0^{-1}\varpi
\frac{\varpi^\top\delta C}
{\varpi^\top H_0^{-1}\varpi}.
$$

This is the load-bearing equation of `CORE-STRUCTURAL-CHARGE-PROJECTOR`. It satisfies the resource-sector charge condition

$$
\varpi^\top
\Pi_{Q,C,H_0}(\delta C)
=0.
$$

Its canonical extension to the complete tangent leaves nonresource variations unchanged:

$$
R_Q(\delta X)
=
\left(
\Pi_{Q,C,H_0}(\delta C),
\delta X_{\mathrm{nr}}
\right).
$$

This extension is a retraction onto $V_{Q,\varpi}$. It is not yet a full-state orthogonal projector, because the accepted investigation has not frozen a product metric that assigns the relative weight and geometry of every profile’s nonresource coordinates. In particular, Candidate A’s complete-state analysis metric remains a routed analysis obligation.

Neither $\Pi_{Q,C,H_0}$ nor $R_Q$ is runtime state or resource authority. They are structural/analysis operations used under a declared tangent and metric contract.

> **Equation/contract rows:** `D10.2-EC-CHARGE-C-SECTOR-PROJECTOR`, `D10.2-EC-CHARGE-FULL-TANGENT-RETRACTION`.

> **Associated accepted claim:** `D10-CL-N-004`.

> **Boundary:** full-state orthogonality remains conditioned by `D10-CL-C-005` and open numerical/metric work in `D10-CL-U-004`.

### 4.6 Ordinary-step charge budget and stage order

The charge test is tied to the actual resource write. For an ordinary complete step,

$$
Q_\varpi(C_{\mathrm{next}})
=
Q_{\mathrm{target,next}}
$$

is checked after the single authoritative continuity update and before final commit.

If a future admitted ordinary-step external exchange exists, its target update is staged explicitly:

$$
Q_{\mathrm{target,next}}
=
Q_{\mathrm{target,current}}
+
\Delta Q_{\mathrm{step}}.
$$

For the current bounded population,

$$
\Delta Q_{\mathrm{step}}=0.
$$

The post-continuity resource state must be finite, nonnegative, and on its serialized charge-target surface before any final-$C$ writer is allowed to consume it. In the current unit-measure profiles, the budget projection is required to be an identity/no-op. A nontrivial correction fails the beat; it may not repair $C$ after a candidate or carrier writer has already consumed another value.

A future profile may admit a nontrivial projection only by making the projection a declared, receipted part of the complete transition before all final-$C$ consumers and by including it in the complete derivative. That future possibility is not part of the present current-population step.

The notation $Q_{\mathrm{target,next}}$ is intentionally stage-specific. A bare $Q_{\mathrm{target}}$ must not conflate pre-update and post-update targets or double-count an event receipt.

> **Equation/contract row:** `D10.2-EC-CHARGE-BUDGET-STAGE`.

> **Source objects:** `CORE-GENERAL-CHARGE`, `L-CONTINUITY-WRITE`, `L-TOPOLOGY-EVENT`.

### 4.7 Topology-event resource accounting

A topology event is a typed jump between source and target graph/profile spaces. It is not represented by weakening the ordinary continuity law or by treating array resizing as a physical map.

To avoid collision with Candidate C’s derived sector $T_C$, write the event resource transport as $T_{C,\mathrm{evt}}$. The accepted resource equation is

$$
C^+
=
T_{C,\mathrm{evt}}C^-
+
\Delta C_{\mathrm{event}}.
$$

The conservative part obeys

$$
\varpi_+^\top T_{C,\mathrm{evt}}
=
\varpi_-^\top.
$$

The event charge receipt is computed from the actual resource state map:

$$
\Delta Q_{\mathrm{event}}
=
\varpi_+^\top C^+
-
\varpi_-^\top C^-.
$$

The target lifecycle charge is then

$$
Q_{\mathrm{target}}^+
=
Q_{\mathrm{target}}^-
+
\Delta Q_{\mathrm{event}}
=
\varpi_+^\top C^+.
$$

For a positivity-preserving unit-measure event, the accepted specialization requires

$$
T_{C,\mathrm{evt}}\ge 0,
\qquad
\mathbf 1_+^\top T_{C,\mathrm{evt}}
=
\mathbf 1_-^\top.
$$

Split weights, merge aggregation, node lineage, birth, death, and external exchange are event data. Birth, death, and exchange enter through $\Delta C_{\mathrm{event}}$ and the resulting explicit charge receipt.

The scalar $\Delta Q_{\mathrm{event}}$ cannot replace $\Delta C_{\mathrm{event}}$. The former records the charge consequence of the actual resource-coordinate map; it does not specify how resource is distributed across target vertices.

The event must later apply compatible typed maps to current state, reset baseline, and any admitted nonresource history, then perform target reconstruction/readmission and atomic commit. Those lifecycle details belong to the later event section; the equations here fix the resource and charge part that every such event must preserve.

> **Equation/contract row:** `D10.2-EC-EVENT-RESOURCE`.

> **Direct parent object:** `L-TOPOLOGY-EVENT`.
>
> **Related section objects:** `CORE-EXTERNAL-EVENT-CHARGE`, `L-ORDERED-RECEIPTS`.

> **Associated accepted claims:** `D10-CL-N-004`, `D10-CL-N-005`; negative boundary `D10-CL-X-001`.

### 4.8 Resource and transport claim ceiling

Sections 4.1–4.7 establish the accepted common mathematical body needed before the candidate-specific causal loop is introduced:

- positive scalar baseline edge mobility;
- graph potential and oriented potential flow;
- separation of baseline flow from authoritative total current;
- one continuity write to the sole resource coordinate;
- general charge and unit-measure reference profile;
- complete-state charge tangent;
- structural resource-sector projector and complete-tangent retraction;
- stage-correct ordinary charge validation;
- typed event resource transport, event increment, and charge receipt.

They do not establish:

- full tensor anisotropic baseline transport;
- that every profile’s scalar mobility is an independently retained state;
- that potential flow already includes Read-Back;
- a full-state orthogonal projector;
- executable general-SPD conditioning or covariance;
- runtime conformance of continuity, event, serializer, or failure atomicity;
- a formed branch, endpoint effect, or stability result.

These are existing claim boundaries, not newly discovered contradictions. No successor investigation is required to state Sections 2–4. A successor would become necessary only if later proposal content requires one of these stronger propositions rather than merely recording it as outside the current claim.

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

## Initial disposition

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
